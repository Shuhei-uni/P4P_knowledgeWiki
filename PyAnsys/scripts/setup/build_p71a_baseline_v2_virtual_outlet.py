#!/usr/bin/env python3
"""Build the Phase 7.1A v2 60k-mesh virtual-liquid-outlet baseline.

The current student session is used only as the v1 setup recipe.  The builder
preserves it to a recovery pair, loads the supplied 60k mesh, reapplies the v1
physics/numerics, partitions the existing y<=0.10 m lower region, and replaces
the uniform inventory-driven absorber with an inlet-throughput feed-forward
phase-2 sink weighted by local liquid volume fraction.

The canonical prepared pair is a freshly hybrid-initialized field. A separate
one-iteration pair is written as instrumentation smoke evidence, after which
the prepared pair is reloaded. Fluent's inherited global iteration counter is
recorded but is not used as initialization provenance. No scientific screen is
performed here.
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
from pathlib import Path, PureWindowsPath
import sys
import traceback
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.setup_common import deep_replace_names
from pyansys_fluent.stage4_native import data_path, ensure_remote_directory, remote_file_sha256
from rebuild_setup_from_reference_case import (
    apply_boundary_states,
    apply_discrete_phase_state,
    apply_general_settings,
    apply_materials,
    apply_models,
    apply_phase_assignments,
    apply_solution_state,
    build_name_replacements,
    capture_reference_snapshot,
    convert_target_boundaries,
    read_target_mesh,
)
from run_p7_e5_cz import create_lower_register, fluid_names


SETUP_ID = "P71A-BASELINE-V2-VIRTUAL-OUTLET"
PARENT_ZONE = "separator-purnanto"
OUTLET_ZONE = "p71a-v2-virtual-outlet"
LIQUID_INLET = "liquidinlet"
LIQUID_PHASE = "phase-2"
VAPOR_PHASE = "phase-1"
VOLUME_FLOOR_M3 = 1.0e-6


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def define_expression(solver: Any, name: str, definition: str) -> None:
    expressions = solver.settings.setup.named_expressions
    if name not in expressions.get_object_names():
        expressions.create(name=name)
    expressions[name].definition = definition
    require(expressions[name].definition() == definition, f"expression readback mismatch: {name}")


def expression_definitions() -> dict[str, str]:
    locations = f'["{OUTLET_ZONE}"]'
    return {
        "P71V2Iteration": "Iteration",
        "P71V2Alpha": f'Volumefraction(phase="{LIQUID_PHASE}")',
        "P71V2LiquidInlet": f'abs(MassFlow(["{LIQUID_INLET}"],phase="{LIQUID_PHASE}"))',
        "P71V2Command": "P71V2LiquidInlet",
        "P71V2AvailableVolume": f"VolumeInt(P71V2Alpha,{locations})",
        "P71V2NormalizationVolume": (
            f"max(P71V2AvailableVolume,{VOLUME_FLOOR_M3:.17g}[m^3])"
        ),
        "P71V2Sink": "-P71V2Command*P71V2Alpha/P71V2NormalizationVolume",
        "P71V2LiquidX": f'Velocity.x(phase="{LIQUID_PHASE}")',
        "P71V2LiquidY": f'Velocity.y(phase="{LIQUID_PHASE}")',
        "P71V2LiquidZ": f'Velocity.z(phase="{LIQUID_PHASE}")',
        "P71V2SinkX": "P71V2Sink*P71V2LiquidX",
        "P71V2SinkY": "P71V2Sink*P71V2LiquidY",
        "P71V2SinkZ": "P71V2Sink*P71V2LiquidZ",
        "P71V2K": "TurbulentKineticEnergyk",
        "P71V2Epsilon": "TurbulenceDissipationRate",
        "P71V2SinkK": "P71V2Sink*P71V2K",
        "P71V2SinkEpsilon": "P71V2Sink*P71V2Epsilon",
        "P71V2Removal": f"-VolumeInt(P71V2Sink,{locations})",
        "P71V2CommandError": "P71V2Removal-P71V2Command",
    }


SOURCE_HOOKS = {
    LIQUID_PHASE: {"mass": "P71V2Sink"},
    "mixture": {
        "x-momentum": "P71V2SinkX",
        "y-momentum": "P71V2SinkY",
        "z-momentum": "P71V2SinkZ",
        "k": "P71V2SinkK",
        "epsilon": "P71V2SinkEpsilon",
    },
}


def split_outlet_zone(solver: Any) -> dict[str, Any]:
    before = fluid_names(solver)
    require(before == [PARENT_ZONE], f"60k target must begin with one fluid zone: {before}")
    register_name, register_state = create_lower_register(solver)
    solver.settings.mesh.modify_zones.sep_cell_zone_mark(
        cell_zone_name=PARENT_ZONE, register=register_name, move_faces=True
    )
    generated = [name for name in fluid_names(solver) if name not in before]
    require(len(generated) == 1, f"expected one lower child zone; got {generated}")
    solver.settings.mesh.modify_zones.zone_name(zone_name=generated[0], new_name=OUTLET_ZONE)
    after = fluid_names(solver)
    require(set(after) == {PARENT_ZONE, OUTLET_ZONE}, f"outlet split mismatch: {after}")
    solver.settings.mesh.check()
    return {
        "register": register_state,
        "generated_zone": generated[0],
        "fluid_zones": after,
        "move_faces": True,
        "extent": "existing Phase-7 y<=0.10 m lower-region selection",
    }


def disable_all_sources(solver: Any) -> None:
    cells = solver.settings.setup.cell_zone_conditions.fluid
    for zone_name in fluid_names(solver):
        for phase_name in ("mixture", VAPOR_PHASE, LIQUID_PHASE):
            cells[zone_name].phase[phase_name].sources.enable = False


def apply_parent_zone_state(solver: Any, recipe: Mapping[str, Any]) -> None:
    source_fluids = recipe["cell_zone_conditions"].get("fluid", {})
    require(PARENT_ZONE in source_fluids, f"v1 recipe lacks {PARENT_ZONE}: {list(source_fluids)}")
    payload = deepcopy(source_fluids[PARENT_ZONE])
    payload["name"] = PARENT_ZONE
    for phase_state in payload.get("phase", {}).values():
        if isinstance(phase_state, dict) and isinstance(phase_state.get("sources"), dict):
            phase_state["sources"]["enable"] = False
    solver.settings.setup.cell_zone_conditions.fluid[PARENT_ZONE].set_state(payload)
    disable_all_sources(solver)


def configure_virtual_outlet(solver: Any) -> dict[str, Any]:
    definitions = expression_definitions()
    for name, definition in definitions.items():
        define_expression(solver, name, definition)

    disable_all_sources(solver)
    cells = solver.settings.setup.cell_zone_conditions.fluid
    outlet = cells[OUTLET_ZONE]
    outlet.phase[VAPOR_PHASE].sources.enable = False
    for phase_name, terms in SOURCE_HOOKS.items():
        source = outlet.phase[phase_name].sources
        source.enable = True
        for equation, expression in terms.items():
            source = outlet.phase[phase_name].sources
            source.terms[equation].resize(size=1)
            source.terms[equation][0].set_state({"option": "value", "value": expression})
            require(source.terms[equation][0].value() == expression, f"source hook mismatch: {equation}")
    solver.settings.solution.run_calculation.profile_update_interval = 1
    return {
        "definitions": definitions,
        "source_hooks": SOURCE_HOOKS,
        "source_state": source_state(solver),
        "profile_update_interval": solver.settings.solution.run_calculation.profile_update_interval(),
    }


def source_state(solver: Any) -> dict[str, Any]:
    cells = solver.settings.setup.cell_zone_conditions.fluid
    return {
        zone: {
            phase: safe_get_state(cells[zone].phase[phase].sources, f"{zone}.{phase}.sources")
            for phase in ("mixture", VAPOR_PHASE, LIQUID_PHASE)
        }
        for zone in fluid_names(solver)
    }


def expression_values(solver: Any) -> dict[str, Any]:
    expressions = solver.settings.setup.named_expressions
    names = (
        "P71V2Iteration",
        "P71V2LiquidInlet",
        "P71V2Command",
        "P71V2AvailableVolume",
        "P71V2NormalizationVolume",
        "P71V2Removal",
        "P71V2CommandError",
    )
    return {name: expressions[name].get_value() for name in names}


def mesh_fingerprint(solver: Any) -> dict[str, Any]:
    zones = solver.fields.solution_variable_info.get_zones_info()
    fluid_counts = {name: int(zones[name].count) for name in fluid_names(solver)}
    return {
        "fluid_cell_counts": fluid_counts,
        "total_fluid_cells": sum(fluid_counts.values()),
        "boundary_names": {
            kind: sorted(branch.get_object_names())
            for kind, branch in {
                "mass_flow_inlet": solver.settings.setup.boundary_conditions.mass_flow_inlet,
                "pressure_outlet": solver.settings.setup.boundary_conditions.pressure_outlet,
                "wall": solver.settings.setup.boundary_conditions.wall,
            }.items()
        },
    }


def audit(solver: Any, expected: Mapping[str, Any]) -> dict[str, Any]:
    models = safe_get_state(solver.settings.setup.models, "models")
    general = safe_get_state(solver.settings.setup.general, "general")
    sources = source_state(solver)
    definitions = {
        name: solver.settings.setup.named_expressions[name].definition()
        for name in expected["definitions"]
    }
    require(definitions == expected["definitions"], "named-expression persistence mismatch")
    require(models["multiphase"]["model"] == "mixture", "Mixture model missing")
    require(models["viscous"]["k_epsilon_model"] == "rng", "RNG k-epsilon missing")
    require(general["solver"]["time"] == "steady", "baseline is not steady")
    require(sources[PARENT_ZONE][VAPOR_PHASE].get("enable") is False, "parent vapor source enabled")
    require(sources[PARENT_ZONE][LIQUID_PHASE].get("enable") is False, "parent liquid source enabled")
    require(sources[OUTLET_ZONE][VAPOR_PHASE].get("enable") is False, "virtual outlet vapor source enabled")
    require(sources[OUTLET_ZONE][LIQUID_PHASE].get("enable") is True, "virtual outlet liquid source disabled")
    require(sources[OUTLET_ZONE]["mixture"].get("enable") is True, "momentum/turbulence sources disabled")
    require(sources == expected["source_state"], "source state changed across save/reopen")
    mesh = mesh_fingerprint(solver)
    require(55_000 <= mesh["total_fluid_cells"] <= 70_000, f"target is not the declared 60k mesh: {mesh}")
    values = expression_values(solver)
    require(math.isfinite(float(values["P71V2Command"])), f"invalid command value: {values}")
    require(float(values["P71V2Command"]) > 0, f"nonpositive inlet command: {values}")
    return {
        "models": models,
        "general": general,
        "mesh": mesh,
        "definitions": definitions,
        "sources": sources,
        "expression_values": values,
    }


def save_pair(solver: Any, path: str) -> dict[str, Any]:
    remote_chdir(solver, str(PureWindowsPath(path).parent))
    solver.settings.file.write_case(file_name=path)
    solver.settings.file.write_data(file_name=data_path(path))
    require(remote_file_exists(solver, path), f"case missing after save: {path}")
    require(remote_file_exists(solver, data_path(path)), f"data missing after save: {data_path(path)}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return {
        "case": path,
        "data": data_path(path),
        "case_sha256": remote_file_sha256(solver, path, f"{path}.{stamp}.sha256.txt"),
        "data_sha256": remote_file_sha256(
            solver, data_path(path), f"{data_path(path)}.{stamp}.sha256.txt"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--mesh", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--reference-case",
        help="Optional paired v1 recovery case to reload before recapturing the setup recipe.",
    )
    args = parser.parse_args()

    remote_root = PureWindowsPath(args.run_root)
    paths = {
        "recovery": str(remote_root / f"{SETUP_ID}-v1-live-recovery.cas.h5"),
        "prepared": str(remote_root / f"{SETUP_ID}-prepared.cas.h5"),
        "smoke": str(remote_root / f"{SETUP_ID}-smoke-plus001.cas.h5"),
    }
    manifest: dict[str, Any] = {
        "setup_id": SETUP_ID,
        "status": "BUILDING",
        "server_id": args.server_id,
        "mesh": args.mesh,
        "run_root": args.run_root,
        "paths": paths,
        "scientific_screen": False,
        "requested_smoke_iterations": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(args.manifest, manifest)
    try:
        solver = connect(server_id=args.server_id, start_transcript=False, tcp_timeout_seconds=5)
        require(not bool(solver.settings.solution.run_calculation.iterating()), "student is currently iterating")
        ensure_remote_directory(solver, args.run_root)
        require(remote_file_exists(solver, args.mesh), f"60k mesh missing: {args.mesh}")

        if args.reference_case:
            require(remote_file_exists(solver, args.reference_case), f"v1 reference case missing: {args.reference_case}")
            require(remote_file_exists(solver, data_path(args.reference_case)), "v1 reference data missing")
            solver.settings.file.read_case(file_name=args.reference_case)
            solver.settings.file.read_data(file_name=data_path(args.reference_case))
            manifest["v1_reference_reloaded"] = args.reference_case

        manifest["v1_live_snapshot"] = capture_reference_snapshot(solver)
        manifest["v1_live_fluid_zones"] = fluid_names(solver)
        if args.reference_case:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            manifest["recovery_pair"] = {
                "case": args.reference_case,
                "data": data_path(args.reference_case),
                "case_sha256": remote_file_sha256(
                    solver, args.reference_case, f"{args.reference_case}.{stamp}.sha256.txt"
                ),
                "data_sha256": remote_file_sha256(
                    solver,
                    data_path(args.reference_case),
                    f"{data_path(args.reference_case)}.{stamp}.sha256.txt",
                ),
            }
        else:
            manifest["recovery_pair"] = save_pair(solver, paths["recovery"])

        read_target_mesh(solver, args.mesh)
        target_boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "target boundaries")
        target_cells = safe_get_state(solver.settings.setup.cell_zone_conditions, "target cells")
        replacements = build_name_replacements(manifest["v1_live_snapshot"], target_boundaries, target_cells)
        recipe = deep_replace_names(deepcopy(manifest["v1_live_snapshot"]), replacements)
        manifest["name_replacements"] = replacements

        apply_general_settings(solver, recipe["general"])
        apply_models(solver, recipe["models"])
        apply_materials(solver, recipe["materials"])
        apply_phase_assignments(solver, recipe["phases"])
        apply_discrete_phase_state(solver, recipe["models"])
        apply_parent_zone_state(solver, recipe)
        current_boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "current boundaries")
        convert_target_boundaries(solver, recipe["boundary_conditions"], current_boundaries)
        apply_boundary_states(solver, recipe["boundary_conditions"])
        apply_solution_state(
            solver,
            {
                key: recipe["solution"][key]
                for key in ("methods", "controls", "initialization")
                if key in recipe["solution"]
            },
        )
        disable_all_sources(solver)
        manifest["lower_zone_split"] = split_outlet_zone(solver)

        initialization = solver.settings.solution.initialization
        initialization.initialization_type = "hybrid"
        initialization.hybrid_init_options.general_settings.iter_count = 10
        initialization.hybrid_initialize()
        manifest["initialization"] = "fresh hybrid, 10 passes, no patched pool"

        manifest["virtual_outlet"] = configure_virtual_outlet(solver)
        manifest["pre_save_audit"] = audit(solver, manifest["virtual_outlet"])
        manifest["pre_save_iteration_marker"] = int(
            manifest["pre_save_audit"]["expression_values"]["P71V2Iteration"]
        )
        manifest["prepared_pair"] = save_pair(solver, paths["prepared"])

        solver.settings.file.read_case(file_name=paths["prepared"])
        solver.settings.file.read_data(file_name=data_path(paths["prepared"]))
        manifest["post_reopen_audit"] = audit(solver, manifest["virtual_outlet"])
        prepared_iteration = int(
            manifest["post_reopen_audit"]["expression_values"]["P71V2Iteration"]
        )
        manifest["prepared_iteration_marker"] = prepared_iteration

        solver.settings.solution.run_calculation.iterate(iter_count=1)
        manifest["smoke_audit"] = audit(solver, manifest["virtual_outlet"])
        require(
            int(manifest["smoke_audit"]["expression_values"]["P71V2Iteration"])
            == prepared_iteration + 1,
            "smoke did not advance exactly one iteration",
        )
        manifest["smoke_pair"] = save_pair(solver, paths["smoke"])

        solver.settings.file.read_case(file_name=paths["prepared"])
        solver.settings.file.read_data(file_name=data_path(paths["prepared"]))
        manifest["terminal_loaded_audit"] = audit(solver, manifest["virtual_outlet"])
        require(
            int(manifest["terminal_loaded_audit"]["expression_values"]["P71V2Iteration"])
            == prepared_iteration,
            "terminal loaded state is not the canonical prepared pair",
        )

        manifest["status"] = "BASELINE_V2_READY"
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        write_json(args.manifest, manifest)
        print(json.dumps({
            "status": manifest["status"],
            "prepared_pair": manifest["prepared_pair"],
            "smoke_pair": manifest["smoke_pair"],
            "mesh": manifest["post_reopen_audit"]["mesh"],
            "expression_values": manifest["post_reopen_audit"]["expression_values"],
        }, indent=2, default=str))
        return 0
    except Exception as exc:
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        manifest["failed_at"] = datetime.now(timezone.utc).isoformat()
        write_json(args.manifest, manifest)
        print(json.dumps({"status": manifest["status"], "error": manifest["error"]}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
