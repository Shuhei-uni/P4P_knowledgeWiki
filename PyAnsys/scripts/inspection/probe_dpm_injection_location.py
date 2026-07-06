#!/usr/bin/env python3
"""Probe DPM injection location binding on a live Fluent session.

Workflow:
1. `scripted-failed`:
   - connect to Fluent
   - load a mesh
   - apply the shared carrier-field setup blocks
   - create one disposable scripted surface injection
   - dump the full injection/location state and child structure
2. Manually fix or create one surface injection in the Fluent GUI.
3. `capture-existing`:
   - reconnect
   - read back the successful GUI-managed injection state
   - dump the same structure
4. `compare`:
   - compare the failed and successful JSON dumps locally

This script is intentionally probe-first. It does not create the full production
09a injection set.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.dependency_workflow import safe_allowed_values, safe_child_names, safe_command_names  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402
from pyansys_fluent.setup_io import load_target_mesh  # noqa: E402
from pyansys_fluent.setup_discovery import build_target_role_map, build_compact_boundary_summary, convert_target_boundaries_to_intended  # noqa: E402
from pyansys_fluent.setup_carrier import (  # noqa: E402
    apply_boundary_states,
    apply_carrier_cell_zone_conditions,
    apply_carrier_general,
    apply_carrier_initialization_settings,
    apply_carrier_models,
    apply_carrier_phase_materials,
    apply_carrier_solution_controls,
    apply_carrier_solution_methods,
    apply_material_states,
    apply_surface_tension_best_effort,
    build_intended_boundary_state,
    build_intended_materials,
)
from pyansys_fluent.setup_dpm import (  # noqa: E402
    apply_dpm_injections,
    apply_dpm_model_settings,
    build_injection_state,
    delete_injection_if_present,
    ensure_inert_particle_material,
    ensure_seed_injection_for_inert_materials,
)

DEFAULT_SERVER_ID = "3"
DEFAULT_MESH = (
    r"C:\Users\syok443\Documents\TwoPhaseInletV2(PurnantoV2)\Major Files"
    r"\PureTwoPhaseV2(PurnantoV2).msh"
)
DEFAULT_INJECTION_NAME = "codex-dpm-location-probe"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "dpm_location_probe"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe one DPM injection location path against live Fluent.")
    parser.add_argument(
        "--mode",
        choices=("scripted-failed", "capture-existing", "compare"),
        required=True,
        help="Probe mode to run.",
    )
    parser.add_argument("--server-id", default=DEFAULT_SERVER_ID, help="Configured Fluent server id. Default: 3.")
    parser.add_argument("--target-mesh", default=DEFAULT_MESH, help="Remote mesh path visible to Fluent.")
    parser.add_argument("--injection-name", default=DEFAULT_INJECTION_NAME, help="Disposable or GUI-fixed injection name to inspect.")
    parser.add_argument(
        "--output-json",
        default="",
        help="Output JSON path. Defaults to output/dpm_location_probe/<mode>-<injection>.json",
    )
    parser.add_argument(
        "--failed-json",
        default="",
        help="Required for compare mode. Previously dumped scripted-failed JSON.",
    )
    parser.add_argument(
        "--success-json",
        default="",
        help="Required for compare mode. Previously dumped capture-existing JSON.",
    )
    parser.add_argument(
        "--cleanup-scripted-injection",
        action="store_true",
        help="Delete the scripted probe injection after dumping it. Default is to keep it for GUI inspection/fixup.",
    )
    return parser


def default_output_path(mode: str, injection_name: str) -> Path:
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUTPUT_DIR / f"{mode}-{injection_name}.json"


def dump_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"wrote_json= {path}")


def shallow_probe(obj: Any, label: str) -> dict[str, Any]:
    return {
        "label": label,
        "type": type(obj).__name__,
        "child_names": safe_child_names(obj),
        "command_names": safe_command_names(obj),
        "allowed_values": safe_allowed_values(obj),
        "state": safe_get_state(obj, label),
    }


def collect_injection_snapshot(solver, injection_name: str) -> dict[str, Any]:
    dpm = solver.settings.setup.models.discrete_phase
    injections = dpm.injections
    snapshot: dict[str, Any] = {
        "fluent_version": solver.get_fluent_version(),
        "boundary_summary": {},
        "dpm": shallow_probe(dpm, "discrete_phase"),
        "injections_branch": shallow_probe(injections, "discrete_phase.injections"),
        "injection_name": injection_name,
    }

    boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "boundary_conditions")
    if isinstance(boundary_state, Mapping):
        snapshot["boundary_summary"] = build_compact_boundary_summary(boundary_state)

    try:
        injection = injections[injection_name]
    except Exception as exc:
        snapshot["injection_lookup_error"] = str(exc)
        return snapshot

    snapshot["injection"] = shallow_probe(injection, f"injections.{injection_name}")
    try:
        snapshot["injection_type"] = shallow_probe(injection.injection_type, f"{injection_name}.injection_type")
    except Exception as exc:
        snapshot["injection_type_error"] = str(exc)
    try:
        snapshot["initial_values"] = shallow_probe(injection.initial_values, f"{injection_name}.initial_values")
    except Exception as exc:
        snapshot["initial_values_error"] = str(exc)
    try:
        snapshot["location"] = shallow_probe(injection.initial_values.location, f"{injection_name}.initial_values.location")
    except Exception as exc:
        snapshot["location_error"] = str(exc)
    try:
        snapshot["mass_flow_rate"] = shallow_probe(injection.initial_values.mass_flow_rate, f"{injection_name}.initial_values.mass_flow_rate")
    except Exception as exc:
        snapshot["mass_flow_rate_error"] = str(exc)
    try:
        snapshot["particle_size"] = shallow_probe(injection.initial_values.particle_size, f"{injection_name}.initial_values.particle_size")
    except Exception as exc:
        snapshot["particle_size_error"] = str(exc)
    try:
        snapshot["physical_models"] = shallow_probe(injection.physical_models, f"{injection_name}.physical_models")
    except Exception as exc:
        snapshot["physical_models_error"] = str(exc)
    return snapshot


def apply_live_carrier_setup(solver, mesh_path: str) -> dict[str, str]:
    load_target_mesh(solver, mesh_path)
    boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "target_boundary_conditions")
    if not isinstance(boundary_state, Mapping):
        raise RuntimeError("Could not inspect target boundary state after reading mesh.")
    role_map = build_target_role_map(boundary_state)
    if not convert_target_boundaries_to_intended(solver, boundary_state, role_map):
        raise RuntimeError("Could not convert target boundaries to intended types.")
    if not apply_carrier_general(solver):
        raise RuntimeError("apply_carrier_general failed")
    if not apply_carrier_models(solver):
        raise RuntimeError("apply_carrier_models failed")
    if not apply_material_states(solver, build_intended_materials()):
        raise RuntimeError("apply_material_states failed")
    if not apply_carrier_phase_materials(solver):
        raise RuntimeError("apply_carrier_phase_materials failed")
    if not apply_surface_tension_best_effort(solver):
        print("surface_tension_best_effort=FAILED", flush=True)
    if not apply_carrier_cell_zone_conditions(solver):
        raise RuntimeError("apply_carrier_cell_zone_conditions failed")
    if not apply_boundary_states(solver, build_intended_boundary_state(role_map)):
        raise RuntimeError("apply_boundary_states failed")
    if not apply_carrier_solution_methods(solver):
        raise RuntimeError("apply_carrier_solution_methods failed")
    if not apply_carrier_solution_controls(solver):
        raise RuntimeError("apply_carrier_solution_controls failed")
    if not apply_carrier_initialization_settings(solver):
        raise RuntimeError("apply_carrier_initialization_settings failed")
    return role_map


def create_scripted_probe_injection(solver, role_map: Mapping[str, str], injection_name: str) -> bool:
    delete_injection_if_present(solver, injection_name)
    ensure_seed_injection_for_inert_materials(solver)
    ensure_inert_particle_material(solver, "water-droplet", 881.77)
    apply_dpm_model_settings(solver, dpm_max_steps=5000, one_way_coupling=True)
    injections = build_injection_state(
        role_map,
        particle_material="water-droplet",
        injection_surface_role="steam_inlet",
        droplet_diameters_um=(10.0,),
        particle_mass_flow_rate=1e-6,
        enable_turbulent_dispersion=False,
        turbulent_dispersion_tries=2,
    )
    payload = {injection_name: injections["dpm-10um"] | {"name": injection_name}}
    return apply_dpm_injections(solver, payload)


def compare_values(failed: Any, success: Any) -> Any:
    if isinstance(failed, Mapping) and isinstance(success, Mapping):
        keys = sorted(set(failed.keys()) | set(success.keys()))
        return {
            key: compare_values(failed.get(key), success.get(key))
            for key in keys
            if failed.get(key) != success.get(key)
        }
    if isinstance(failed, list) and isinstance(success, list):
        if failed == success:
            return {}
        return {"failed": failed, "success": success}
    if failed != success:
        return {"failed": failed, "success": success}
    return {}


def run_compare(failed_json: Path, success_json: Path, output_json: Path) -> int:
    failed = json.loads(failed_json.read_text(encoding="utf-8"))
    success = json.loads(success_json.read_text(encoding="utf-8"))
    comparison = {
        "failed_json": str(failed_json),
        "success_json": str(success_json),
        "state_diff": compare_values(failed, success),
    }
    dump_json(output_json, comparison)
    print(json.dumps(comparison, indent=2))
    return 0


def main() -> int:
    args = build_parser().parse_args()
    output_json = Path(args.output_json) if args.output_json else default_output_path(args.mode, args.injection_name)

    if args.mode == "compare":
        if not args.failed_json or not args.success_json:
            raise RuntimeError("--failed-json and --success-json are required for compare mode.")
        return run_compare(Path(args.failed_json), Path(args.success_json), output_json)

    solver = connect(server_id=args.server_id)
    print(f"connected_version= {solver.get_fluent_version()}")

    if args.mode == "scripted-failed":
        print_header("Apply Carrier Setup For DPM Probe")
        role_map = apply_live_carrier_setup(solver, args.target_mesh)
        print_header("Create One Scripted Probe Injection")
        scripted_ok = create_scripted_probe_injection(solver, role_map, args.injection_name)
        snapshot = collect_injection_snapshot(solver, args.injection_name)
        snapshot["probe_mode"] = "scripted-failed"
        snapshot["scripted_injection_ok"] = scripted_ok
        snapshot["target_mesh"] = args.target_mesh
        snapshot["role_map"] = dict(role_map)
        dump_json(output_json, snapshot)
        if args.cleanup_scripted_injection:
            print(f"cleanup_scripted_injection= {delete_injection_if_present(solver, args.injection_name)}")
        else:
            print("scripted injection kept for manual Fluent GUI inspection/fixup")
        return 0

    if args.mode == "capture-existing":
        print_header("Capture Existing Injection")
        snapshot = collect_injection_snapshot(solver, args.injection_name)
        snapshot["probe_mode"] = "capture-existing"
        dump_json(output_json, snapshot)
        return 0

    raise RuntimeError(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    raise SystemExit(main())
