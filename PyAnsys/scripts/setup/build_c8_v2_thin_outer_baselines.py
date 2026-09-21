#!/usr/bin/env python3
"""Build corrected Server-3 C8 baselines with the Phase 7.1A v2 absorber.

The immutable C8-D0 all-wall parent is read, the existing lower absorber zone
is renamed and converted to the v2 throughput-controlled phase-2 source, and
two paired artifacts are written:

* an all-wall v2 parent for the corrected C8 development/pressure family;
* a thin-outer-ring pressure-outlet baseline at the P0 pressure.

No solver iterations are performed.  The pressure baseline is left loaded so
the selected Server-3 endpoint visibly contains the requested corrected thin
ring pressure-outlet case.
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping
from datetime import datetime, timezone
import json
import math
from pathlib import Path, PureWindowsPath
import sys
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.stage4_native import data_path, ensure_remote_directory, remote_file_sha256
from build_p71a_baseline_v2_virtual_outlet import (
    LIQUID_INLET,
    LIQUID_PHASE,
    OUTLET_ZONE,
    SOURCE_HOOKS,
    configure_virtual_outlet,
    define_expression,
    expression_definitions,
    source_state,
)

OLD_LOWER_ZONE = "p7-e5-lower-y010"
PARENT_ZONE = "separator-purnanto"
OUTER_RING = "bottom-bottom-band1-thin-outer-separator-purnanto"
P0_PRESSURE_PA = 1_120_000.0
RINGS = (
    "bottom",
    "bottom-thin-inner-separator-purnanto",
    "bottom-thick-inner-separator-purnanto",
    "bottom-thick-outer-separator-purnanto",
    OUTER_RING,
)


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def save_pair(solver: Any, case: str, scratch: str) -> dict[str, Any]:
    data = data_path(case)
    require(not remote_file_exists(solver, case), f"refusing to overwrite case: {case}")
    require(not remote_file_exists(solver, data), f"refusing to overwrite data: {data}")
    remote_chdir(solver, str(PureWindowsPath(case).parent))
    solver.settings.file.write_case(file_name=case)
    solver.settings.file.write_data(file_name=data)
    require(remote_file_exists(solver, case) and remote_file_exists(solver, data), f"pair missing: {case}")
    return {
        "case": case,
        "data": data,
        "case_sha256": remote_file_sha256(solver, case, str(PureWindowsPath(scratch) / (PureWindowsPath(case).name + ".sha256.txt"))),
        "data_sha256": remote_file_sha256(solver, data, str(PureWindowsPath(scratch) / (PureWindowsPath(data).name + ".sha256.txt"))),
    }


def rename_lower_zone(solver: Any) -> dict[str, Any]:
    cells = solver.settings.setup.cell_zone_conditions.fluid
    names = list(cells.get_object_names())
    require(OLD_LOWER_ZONE in names, f"expected old absorber zone {OLD_LOWER_ZONE!r}; got {names}")
    require(OUTLET_ZONE not in names, f"v2 zone already exists unexpectedly: {names}")
    solver.settings.mesh.modify_zones.zone_name(zone_name=OLD_LOWER_ZONE, new_name=OUTLET_ZONE)
    after = list(solver.settings.setup.cell_zone_conditions.fluid.get_object_names())
    require(OUTLET_ZONE in after and PARENT_ZONE in after, f"zone rename failed: {after}")
    solver.settings.mesh.check()
    return {"before": names, "after": after, "renamed": {"from": OLD_LOWER_ZONE, "to": OUTLET_ZONE}}


def set_outer_wall(solver: Any) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions
    state = safe_get_state(bc, "C8 v2 baseline boundary state before wall audit")
    pressure = state.get("pressure_outlet", {}) if isinstance(state, Mapping) else {}
    if OUTER_RING in pressure:
        bc.set_zone_type(zone_list=[OUTER_RING], new_type="wall")
    after = safe_get_state(bc, "C8 v2 all-wall boundary readback")
    walls = after.get("wall", {}) if isinstance(after, Mapping) else {}
    require(all(name in walls for name in RINGS), f"all-wall baseline is missing bottom band(s): {RINGS}")
    return {"boundary_type": "wall", "retained_walls": list(RINGS)}


def set_outer_pressure(solver: Any, pressure_pa: float) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions
    state = safe_get_state(bc, "C8 v2 pressure baseline boundary state before switch")
    if OUTER_RING in (state.get("wall", {}) if isinstance(state, Mapping) else {}):
        bc.set_zone_type(zone_list=[OUTER_RING], new_type="pressure-outlet")
    outlet = bc.pressure_outlet[OUTER_RING]
    outlet.phase["mixture"].momentum.gauge_pressure = pressure_pa
    outlet.phase["mixture"].momentum.backflow_dir_spec_method = "Normal to Boundary"
    outlet.phase["mixture"].momentum.backflow_pressure_spec = "Total Pressure"
    outlet.phase["phase-2"].multiphase.backflow_volume_fraction = 0.0
    after = safe_get_state(outlet, "C8 v2 thin-ring pressure baseline readback")
    actual = after["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"]
    vf = after["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"]["value"]
    require(abs(float(actual) - pressure_pa) < 1e-9, f"pressure readback mismatch: {actual}")
    require(abs(float(vf)) < 1e-12, f"phase-2 backflow readback mismatch: {vf}")
    boundaries = safe_get_state(bc, "C8 v2 pressure baseline boundary audit")
    require(all(name in boundaries.get("wall", {}) for name in RINGS[:-1]), "pressure baseline changed an inner bottom band")
    return {"boundary_type": "pressure-outlet", "pressure_pa": float(actual), "phase2_backflow_volume_fraction": float(vf), "boundary": after}


def configure_c8_v2_virtual_outlet(solver: Any) -> dict[str, Any]:
    """Apply v2 sources while holding each live Settings handle stable."""
    definitions = expression_definitions()
    for name, definition in definitions.items():
        define_expression(solver, name, definition)
    cells = solver.settings.setup.cell_zone_conditions.fluid
    for zone_name in list(cells.get_object_names()):
        for phase_name in ("mixture", "phase-1", "phase-2"):
            cells[zone_name].phase[phase_name].sources.enable = False
    # Reacquire after the enable sweep; Fluent 2025 R2 can invalidate a
    # nested source proxy when the previous proxy is reused across writes.
    cells = solver.settings.setup.cell_zone_conditions.fluid
    outlet = cells[OUTLET_ZONE]
    outlet.phase["phase-1"].sources.enable = False
    source_hooks: dict[str, Any] = {}
    for phase_name, terms in SOURCE_HOOKS.items():
        source = outlet.phase[phase_name].sources
        source.enable = True
        source_hooks[phase_name] = {}
        for equation, expression in terms.items():
            term = source.terms[equation]
            term.resize(size=1)
            term[0].set_state({"option": "value", "value": expression})
            require(term[0].value() == expression, f"source hook mismatch: {phase_name}.{equation}")
            source_hooks[phase_name][equation] = expression
    solver.settings.solution.run_calculation.profile_update_interval = 1
    return {"definitions": definitions, "source_hooks": source_hooks, "source_state": source_state(solver), "profile_update_interval": solver.settings.solution.run_calculation.profile_update_interval()}


def mesh_counts(solver: Any) -> dict[str, Any]:
    zones = solver.fields.solution_variable_info.get_zones_info()
    names = solver.settings.setup.cell_zone_conditions.fluid.get_object_names()
    # ``zones`` is a remote Settings collection; membership checks issue a
    # separate RPC for each name and can hang on the 237k mesh.  The fluid
    # names have already been read from the same live tree, so index directly.
    counts = {name: int(zones[name].count) for name in names}
    return {"fluid_cell_counts": counts, "total_fluid_cells": sum(counts.values())}


def audit(solver: Any, expected_sources: Mapping[str, Any], expected_absorber: Mapping[str, Any], boundary_mode: str) -> dict[str, Any]:
    models = safe_get_state(solver.settings.setup.models, "C8 v2 models")
    boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "C8 v2 boundaries")
    require(models["multiphase"]["model"] == "mixture", "C8 v2 parent is not Mixture")
    require(models["viscous"]["k_epsilon_model"] == "rng", "C8 v2 parent is not RNG k-epsilon")
    definitions = {name: solver.settings.setup.named_expressions[name].definition() for name in expected_absorber["definitions"]}
    require(definitions == expected_absorber["definitions"], "v2 named-expression persistence mismatch")
    sources = source_state(solver)
    require(sources == expected_sources, "v2 source state mismatch")
    require(sources[OUTLET_ZONE][LIQUID_PHASE]["enable"] is True, "v2 phase-2 source is disabled")
    require(sources[OUTLET_ZONE]["phase-1"]["enable"] is False, "v2 vapor source is enabled")
    if boundary_mode == "all-wall":
        require(all(name in boundaries.get("wall", {}) for name in RINGS), "all-wall audit failed")
    elif boundary_mode == "pressure-outlet":
        require(OUTER_RING in boundaries.get("pressure_outlet", {}), "thin ring pressure outlet missing")
        require(all(name in boundaries.get("wall", {}) for name in RINGS[:-1]), "inner bottom wall missing")
    else:
        raise ValueError(boundary_mode)
    values = {}
    for name in ("P71V2LiquidInlet", "P71V2Command", "P71V2AvailableVolume", "P71V2NormalizationVolume", "P71V2Removal", "P71V2CommandError"):
        values[name] = solver.settings.setup.named_expressions[name].get_value()
    require(math.isfinite(float(values["P71V2Command"])) and float(values["P71V2Command"]) > 0, f"invalid v2 command: {values}")
    return {"models": models, "boundaries": boundaries, "sources": sources, "definitions": definitions, "expression_values": values, "mesh": mesh_counts(solver), "boundary_mode": boundary_mode}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server-id", default="3")
    ap.add_argument("--parent-case", required=True)
    ap.add_argument("--run-root", required=True, help="Server-local working/recovery directory")
    ap.add_argument("--baseline-root", required=True, help="Final baseline directory, normally OneDrive")
    ap.add_argument("--manifest", required=True, type=Path)
    args = ap.parse_args()

    work = PureWindowsPath(args.run_root)
    base = PureWindowsPath(args.baseline_root)
    live_recovery = str(work / "C8-old-incorrect-absorber-live-recovery.cas.h5")
    all_wall = str(base / "C8-V2-thin-outer-all-wall-prepared.cas.h5")
    pressure = str(base / "C8-V2-thin-ring-pressure-baseline-P1120.cas.h5")
    manifest: dict[str, Any] = {"status": "RUNNING", "setup_id": "C8-V2-THIN-RING-BASELINES", "server_id": args.server_id, "parent_case": args.parent_case, "parent_data": data_path(args.parent_case), "run_root": args.run_root, "baseline_root": args.baseline_root, "paths": {"live_recovery": live_recovery, "all_wall": all_wall, "pressure_baseline": pressure}, "pressure_pa": P0_PRESSURE_PA, "scientific_screen": False, "iterations": 0, "created_at": datetime.now(timezone.utc).isoformat()}
    dump(args.manifest, manifest)
    try:
        solver = connect(server_id=args.server_id, start_transcript=False, tcp_timeout_seconds=120)
        require("2025 R2" in str(solver.get_fluent_version()), "unexpected Fluent version")
        require(not bool(solver.settings.solution.run_calculation.iterating()), "Server 3 is iterating")
        ensure_remote_directory(solver, str(work)); ensure_remote_directory(solver, str(base))
        # The currently loaded old pressure state is preserved before loading the parent.
        if not remote_file_exists(solver, live_recovery):
            manifest["live_recovery_pair"] = save_pair(solver, live_recovery, str(work))
        require(remote_file_exists(solver, args.parent_case), f"parent case missing: {args.parent_case}")
        require(remote_file_exists(solver, data_path(args.parent_case)), f"parent data missing: {data_path(args.parent_case)}")
        solver.settings.file.read_case(file_name=args.parent_case); solver.settings.file.read_data(file_name=data_path(args.parent_case))
        manifest["parent_loaded"] = {"case": args.parent_case, "data": data_path(args.parent_case), "boundary": safe_get_state(solver.settings.setup.boundary_conditions, "parent boundary")}
        manifest["zone_rename"] = rename_lower_zone(solver)
        set_outer_wall(solver)
        manifest["v2_absorber"] = configure_c8_v2_virtual_outlet(solver)
        expected_sources = source_state(solver)
        expected_absorber = {"definitions": expression_definitions(), "source_hooks": SOURCE_HOOKS}
        manifest["all_wall_audit"] = audit(solver, expected_sources, expected_absorber, "all-wall")
        manifest["all_wall_pair"] = save_pair(solver, all_wall, str(work))
        solver.settings.file.read_case(file_name=all_wall); solver.settings.file.read_data(file_name=data_path(all_wall))
        manifest["all_wall_reopen_audit"] = audit(solver, expected_sources, expected_absorber, "all-wall")
        set_outer_pressure(solver, P0_PRESSURE_PA)
        manifest["pressure_pre_save_audit"] = audit(solver, expected_sources, expected_absorber, "pressure-outlet")
        manifest["pressure_baseline_pair"] = save_pair(solver, pressure, str(work))
        solver.settings.file.read_case(file_name=pressure); solver.settings.file.read_data(file_name=data_path(pressure))
        manifest["pressure_reopen_audit"] = audit(solver, expected_sources, expected_absorber, "pressure-outlet")
        manifest["status"] = "COMPLETE"
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        dump(args.manifest, manifest)
        print(json.dumps({"status": manifest["status"], "all_wall_pair": manifest["all_wall_pair"], "pressure_baseline_pair": manifest["pressure_baseline_pair"], "pressure_expression_values": manifest["pressure_reopen_audit"]["expression_values"], "mesh": manifest["pressure_reopen_audit"]["mesh"]}, indent=2, default=str))
        return 0
    except Exception as exc:
        manifest.update({"status": "BLOCKED", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
        dump(args.manifest, manifest)
        print(json.dumps({"status": manifest["status"], "error": manifest["error"]}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
