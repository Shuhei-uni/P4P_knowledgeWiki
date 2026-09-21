#!/usr/bin/env python3
"""Rebuild the P7.1A absorber baseline on the supplied 237k thin-outer mesh.

This is a *prepared-case* builder only. It preserves the loaded Server-3 state
to a paired recovery artifact, reads the supplied mesh, reapplies either the
loaded or a supplied verified baseline snapshot, creates the y<=0.10 m
absorber cell zone, and configures its phase-2-only source at -116.92 kg/s.
The thin outer bottom band is either a 1.120 MPa-gauge pressure outlet or,
when requested, retained as a wall with the other bottom bands. It never
calls ``run_calculation.iterate``.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import traceback
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.stage4_native import data_path, ensure_remote_directory
from rebuild_setup_from_reference_case import (
    apply_boundary_states, apply_discrete_phase_state, apply_general_settings,
    apply_materials, apply_models, apply_phase_assignments, apply_solution_state,
    capture_reference_snapshot, convert_target_boundaries, read_target_mesh,
)
from run_p7_e5_cz import (
    LOWER_ZONE, PARENT_ZONE, create_lower_register, configure_sources,
    fluid_names, read_source_tree,
)

OUTER_RING = "bottom-bottom-band1-thin-outer-separator-purnanto"
OUTER_PRESSURE_PA = 1_120_000.0
SOURCE_RATE_KG_S = 116.92


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def lower_volume(solver: Any) -> float:
    value = solver.settings.results.report.volume_integrals.get_volume(
        cell_zones=[LOWER_ZONE], locations={"geometry": [LOWER_ZONE]},
        cell_function="cell-volume", current_domain="mixture",
    )
    if isinstance(value, Mapping):
        value = value.get("Net", value.get("value"))
    volume = float(value)
    require(math.isfinite(volume) and volume > 0, f"invalid lower-zone volume: {value!r}")
    return volume


def split_lower_zone(solver: Any) -> dict[str, Any]:
    before = fluid_names(solver)
    require(before == [PARENT_ZONE], f"target must begin with one fluid zone; got {before}")
    register, register_state = create_lower_register(solver)
    solver.settings.mesh.modify_zones.sep_cell_zone_mark(
        cell_zone_name=PARENT_ZONE, register=register, move_faces=True,
    )
    generated = [name for name in fluid_names(solver) if name not in before]
    require(len(generated) == 1, f"expected one lower-zone child; got {generated}")
    solver.settings.mesh.modify_zones.zone_name(zone_name=generated[0], new_name=LOWER_ZONE)
    after = fluid_names(solver)
    require(set(after) == {PARENT_ZONE, LOWER_ZONE}, f"lower-zone split mismatch: {after}")
    solver.settings.mesh.check()
    return {"register": register_state, "generated_name": generated[0], "fluid_zones": after}


def configure_outer_ring(solver: Any, *, all_bottom_walls: bool = False) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions
    if all_bottom_walls:
        state_before = safe_get_state(bc, "target boundaries before all-wall configuration")
        if OUTER_RING in (state_before.get("pressure_outlet", {}) if isinstance(state_before, Mapping) else {}):
            bc.set_zone_type(zone_list=[OUTER_RING], new_type="wall")
        state = safe_get_state(bc, "all-bottom-wall readback")
        walls = state.get("wall", {}) if isinstance(state, Mapping) else {}
        require(OUTER_RING in walls, f"thin outer all-wall conversion failed: {state}")
        return {"boundary_type": "wall", "state": walls[OUTER_RING]}
    state = safe_get_state(bc, "target boundaries before outer-ring configuration")
    pressure = state.get("pressure_outlet", {}) if isinstance(state, Mapping) else {}
    require(OUTER_RING in pressure, f"thin outer pressure outlet missing: {sorted(pressure)}")
    outer = bc.pressure_outlet[OUTER_RING]
    # Make the physically meaningful delta explicit.  Secondary-phase backflow
    # is retained at the baseline's zero-liquid fraction; this is a backflow
    # condition, not a claim of liquid-selective outward flow.
    outer.phase["mixture"].momentum.gauge_pressure = OUTER_PRESSURE_PA
    outer.phase["mixture"].momentum.backflow_dir_spec_method = "Normal to Boundary"
    outer.phase["mixture"].momentum.backflow_pressure_spec = "Total Pressure"
    outer.phase["phase-2"].multiphase.backflow_volume_fraction = 0.0
    result = safe_get_state(outer, "thin outer pressure-outlet readback")
    actual = result["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"]
    liquid_backflow = result["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"]["value"]
    require(abs(float(actual) - OUTER_PRESSURE_PA) < 1e-9, f"outer pressure mismatch: {actual}")
    require(abs(float(liquid_backflow)) < 1e-12, f"outer backflow mismatch: {liquid_backflow}")
    return result


def audit(solver: Any, expected_density: float, *, all_bottom_walls: bool = False) -> dict[str, Any]:
    models = safe_get_state(solver.settings.setup.models, "models")
    boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "boundaries")
    volume = lower_volume(solver)
    source = read_source_tree(solver)
    mass = source[LOWER_ZONE]["phase-2"]["terms"]["mass"][0]["value"]
    require(models["multiphase"]["model"] == "mixture", "Mixture model missing")
    require(models["viscous"]["k_epsilon_model"] == "rng", "RNG k-epsilon missing")
    require(abs(float(mass) - expected_density) < 1e-10, f"source density mismatch: {mass}")
    require(abs(float(mass) * volume + SOURCE_RATE_KG_S) < 1e-7, "integrated source mismatch")
    walls = set(boundaries.get("wall", {}))
    required_walls = ["bottom", "bottom-thin-inner-separator-purnanto", "bottom-thick-inner-separator-purnanto", "bottom-thick-outer-separator-purnanto"]
    if all_bottom_walls:
        required_walls.append(OUTER_RING)
    for name in required_walls:
        require(name in walls, f"required retained wall missing: {name}")
    if all_bottom_walls:
        require(OUTER_RING not in set(boundaries.get("pressure_outlet", {})), "C7 outer ring remained a pressure outlet")
    outer = boundaries.get("wall", {}).get(OUTER_RING) if all_bottom_walls else boundaries["pressure_outlet"][OUTER_RING]
    return {"fluid_zones": fluid_names(solver), "lower_volume_m3": volume, "source_density_kg_m3_s": mass,
            "integrated_source_kg_s": float(mass) * volume, "outer_ring": outer,
            "models": models, "source_tree": source}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--mesh", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--reference-manifest",
        type=Path,
        help=(
            "Optional local completed all-wall build manifest whose "
            "baseline_snapshot is the verified setup recipe. This lets a "
            "Server-3 rebuild avoid inheriting an unrelated live solver path."
        ),
    )
    parser.add_argument("--resume-after-split", action="store_true",
                        help="Resume only the verified, loaded thin-outer mesh after the lower-zone split.")
    parser.add_argument("--all-bottom-walls", action="store_true",
                        help="Create the C7 parent with every bottom band retained as a wall.")
    args = parser.parse_args()
    root = PureWindowsPath(args.run_root)
    recovery = str(root / "P71A-baseline-pre-thin-outer-recovery.cas.h5")
    prepared = str(root / "P71A-thin-outer-baseline-prepared.cas.h5")
    manifest: dict[str, Any] = {"status": "RUNNING", "server_id": args.server_id, "mesh": args.mesh,
                                "run_root": args.run_root, "recovery_case": recovery, "prepared_case": prepared,
                                "outer_ring": OUTER_RING, "outer_pressure_pa": None if args.all_bottom_walls else OUTER_PRESSURE_PA,
                                "all_bottom_walls": args.all_bottom_walls,
                                "reference_manifest": str(args.reference_manifest) if args.reference_manifest else None,
                                "absorber_rate_kg_s": SOURCE_RATE_KG_S, "initialized": False, "iterated": False}
    write_json(args.manifest, manifest)
    try:
        solver = connect(server_id=args.server_id, start_transcript=False)
        ensure_remote_directory(solver, args.run_root)
        if not args.resume_after_split:
            for path in (recovery, data_path(recovery), prepared):
                require(not remote_file_exists(solver, path), f"refusing to overwrite: {path}")
            manifest["server3_prebuild_snapshot"] = capture_reference_snapshot(solver)
            if args.reference_manifest:
                reference = json.loads(args.reference_manifest.read_text(encoding="utf-8"))
                baseline_snapshot = reference.get("baseline_snapshot")
                require(isinstance(baseline_snapshot, Mapping),
                        "reference manifest lacks a baseline_snapshot mapping")
                manifest["baseline_snapshot"] = deepcopy(dict(baseline_snapshot))
                manifest["baseline_snapshot_origin"] = str(args.reference_manifest)
            else:
                manifest["baseline_snapshot"] = manifest["server3_prebuild_snapshot"]
            remote_chdir(solver, args.run_root)
            solver.settings.file.write_case(file_name=recovery)
            solver.settings.file.write_data(file_name=data_path(recovery))
            require(remote_file_exists(solver, recovery) and remote_file_exists(solver, data_path(recovery)), "baseline recovery pair missing")
            read_target_mesh(solver, args.mesh)
            apply_general_settings(solver, manifest["baseline_snapshot"]["general"])
            apply_models(solver, manifest["baseline_snapshot"]["models"])
            apply_materials(solver, manifest["baseline_snapshot"]["materials"])
            apply_phase_assignments(solver, manifest["baseline_snapshot"]["phases"])
            apply_discrete_phase_state(solver, manifest["baseline_snapshot"]["models"])
            target = safe_get_state(solver.settings.setup.boundary_conditions, "target boundaries")
            convert_target_boundaries(solver, manifest["baseline_snapshot"]["boundary_conditions"], target)
            apply_boundary_states(solver, manifest["baseline_snapshot"]["boundary_conditions"])
            manifest["outer_ring_readback_pre_split"] = configure_outer_ring(solver, all_bottom_walls=args.all_bottom_walls)
            manifest["lower_zone_split"] = split_lower_zone(solver)
        else:
            require(set(fluid_names(solver)) == {PARENT_ZONE, LOWER_ZONE},
                    f"resume requires the verified two-zone topology; got {fluid_names(solver)}")
            manifest["resumed_after_split"] = True
            manifest["outer_ring_readback_pre_split"] = configure_outer_ring(solver, all_bottom_walls=args.all_bottom_walls)
        # Volume-integral evaluation is unavailable until Fluent owns an
        # initialized field. Hybrid initialization does not advance iterations.
        init = solver.settings.solution.initialization
        init.initialization_type = "hybrid"
        init.hybrid_init_options.general_settings.iter_count = 10
        init.hybrid_initialize()
        manifest["initialization"] = "hybrid; no run-calculation iterate call"
        volume = lower_volume(solver)
        density = -SOURCE_RATE_KG_S / volume
        manifest["source_readback"] = configure_sources(solver, density, {"x": 0.0, "y": 0.0, "z": 0.0})
        if not args.resume_after_split:
            apply_solution_state(solver, manifest["baseline_snapshot"]["solution"])
        manifest["pre_save_audit"] = audit(solver, density, all_bottom_walls=args.all_bottom_walls)
        remote_chdir(solver, args.run_root)
        solver.settings.file.write_case(file_name=prepared)
        solver.settings.file.write_data(file_name=data_path(prepared))
        require(remote_file_exists(solver, prepared) and remote_file_exists(solver, data_path(prepared)), "prepared case/data pair missing")
        solver.settings.file.read_case(file_name=prepared)
        solver.settings.file.read_data(file_name=data_path(prepared))
        manifest["post_reopen_audit"] = audit(solver, density, all_bottom_walls=args.all_bottom_walls)
        manifest["status"] = "COMPLETE"
        write_json(args.manifest, manifest)
        print(json.dumps({k: manifest.get(k) for k in ("status", "recovery_case", "prepared_case", "lower_zone_split", "pre_save_audit", "post_reopen_audit")}, indent=2, default=str))
        return 0
    except Exception as exc:
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        write_json(args.manifest, manifest)
        print(json.dumps({"status": manifest["status"], "error": manifest["error"]}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
