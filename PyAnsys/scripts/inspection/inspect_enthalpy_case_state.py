#!/usr/bin/env python3
"""Inspect a saved Purnanto enthalpy case/data pair without running solves."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPTS = PROJECT_ROOT / "scripts" / "setup"
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SETUP_SCRIPTS))

from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
from run_purnanto_dpm_sensitivity import default_case_data_paths, single_case_plan  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect saved enthalpy case/data DPM setup state.")
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--case-filter", default="1600")
    parser.add_argument("--case-file", default="")
    parser.add_argument("--data-file", default="")
    parser.add_argument("--case-only", action="store_true", help="Read only the case file; do not require/read data.")
    parser.add_argument("--harwell-csv", default=str(sweep.DEFAULT_HARWELL_CSV))
    parser.add_argument("--remote-output-dir", default=sweep.DEFAULT_REMOTE_OUTPUT_DIR)
    parser.add_argument("--local-output-dir", default=str(sweep.DEFAULT_LOCAL_OUTPUT_DIR / "inspection"))
    parser.add_argument("--label", default="saved_case_state")
    return parser


def nested(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    value: Any = mapping
    for key in keys:
        if not isinstance(value, Mapping):
            return default
        value = value.get(key, default)
    return value


def object_names(branch: Any) -> list[str]:
    try:
        return sorted(str(name) for name in branch.get_object_names())
    except Exception as exc:
        return [f"<error: {type(exc).__name__}: {exc}>"]


def inspect_injections(solver: Any, bins: list[sweep.InjectionBin]) -> list[dict[str, Any]]:
    branch = solver.settings.setup.models.discrete_phase.injections
    rows: list[dict[str, Any]] = []
    for item in bins:
        try:
            state = branch[item.injection_name].get_state()
        except Exception as exc:
            rows.append(
                {
                    "injection_name": item.injection_name,
                    "error": f"{type(exc).__name__}: {exc}",
                    "state": {},
                }
            )
            continue

        row = {
            "injection_name": item.injection_name,
            "expected_diameter_m": item.diameter_m,
            "expected_mass_flow_kgs": item.mass_flow_kgs,
            "expected_z_velocity_ms": item.z_velocity_ms,
            "particle_type": state.get("particle_type"),
            "material": state.get("material"),
            "injection_type": nested(state, "injection_type", "option"),
            "surface": nested(state, "initial_values", "location", "injection_surfaces", default=[]),
            "mass_flow_kgs": nested(state, "initial_values", "mass_flow_rate", "total_flow_rate"),
            "velocity_use_face_normal": nested(state, "initial_values", "velocity", "use_face_normal_direction"),
            "velocity_magnitude": nested(state, "initial_values", "velocity", "magnitude"),
            "velocity_z": nested(state, "initial_values", "velocity", "z_velocity"),
            "diameter_m": nested(state, "initial_values", "particle_size", "diameter"),
            "particle_size_option": nested(state, "initial_values", "particle_size", "option"),
            "state": state,
        }
        rows.append(row)
    return rows


def inspect_all_injections(solver: Any) -> list[dict[str, Any]]:
    branch = solver.settings.setup.models.discrete_phase.injections
    rows: list[dict[str, Any]] = []
    for name in object_names(branch):
        try:
            state = branch[name].get_state()
        except Exception as exc:
            rows.append({"injection_name": name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        rows.append(
            {
                "injection_name": name,
                "particle_type": state.get("particle_type"),
                "material": state.get("material"),
                "injection_type": nested(state, "injection_type", "option"),
                "surface": nested(state, "initial_values", "location", "injection_surfaces", default=[]),
                "mass_flow_kgs": nested(state, "initial_values", "mass_flow_rate", "total_flow_rate"),
                "velocity_use_face_normal": nested(
                    state, "initial_values", "velocity", "use_face_normal_direction"
                ),
                "velocity_magnitude": nested(state, "initial_values", "velocity", "magnitude"),
                "velocity_z": nested(state, "initial_values", "velocity", "z_velocity"),
                "diameter_m": nested(state, "initial_values", "particle_size", "diameter"),
                "particle_size_option": nested(state, "initial_values", "particle_size", "option"),
                "state": state,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "injection_name",
        "particle_type",
        "material",
        "injection_type",
        "surface",
        "mass_flow_kgs",
        "expected_mass_flow_kgs",
        "velocity_use_face_normal",
        "velocity_magnitude",
        "expected_z_velocity_ms",
        "velocity_z",
        "diameter_m",
        "expected_diameter_m",
        "particle_size_option",
        "error",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()
    output_dir = Path(args.local_output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    case, bins = single_case_plan(args.case_filter, Path(args.harwell_csv).expanduser().resolve())
    case_file = args.case_file
    data_file = args.data_file
    if not case_file and not data_file:
        case_file, data_file = default_case_data_paths(case, args.remote_output_dir)
    if args.case_only:
        if not case_file:
            raise RuntimeError("--case-file is required with --case-only")
    elif not (case_file and data_file):
        raise RuntimeError("--case-file and --data-file must be supplied together")

    prefix = f"{sweep.case_prefix(case)}_{sweep.slugify(args.label)}"
    solver = connect(server_id=args.server_id)
    print(f"connected: {solver.get_fluent_version()}")
    sweep.require_remote_input(solver, case_file, "case")
    if not args.case_only:
        sweep.require_remote_input(solver, data_file, "data")
    sweep.remote_chdir(solver, str(PureWindowsPath(case_file).parent))

    print(f"reading_case: {case_file}")
    solver.settings.file.read_case(file_name=case_file)
    iteration_after_case = sweep.read_iteration_count(solver)
    injections_after_case = object_names(solver.settings.setup.models.discrete_phase.injections)

    iteration_after_data = None
    if args.case_only:
        print("reading_data: SKIPPED")
    else:
        print(f"reading_data: {data_file}")
        solver.settings.file.read_data(file_name=data_file)
        iteration_after_data = sweep.read_iteration_count(solver)
        sweep.start_iteration_monitor(solver)
    residual_monitor_history = sweep.monitor_iteration_snapshot(solver)
    injection_rows = inspect_injections(solver, list(bins))

    materials = solver.settings.setup.materials
    payload = {
        "case": case.csv_case,
        "condition": case.condition,
        "case_file": case_file,
        "data_file": data_file,
        "iteration_after_case_only": iteration_after_case,
        "iteration_after_data": iteration_after_data,
        "reported_number_of_iterations_is_completion_proof": False,
        "residual_monitor_history": residual_monitor_history,
        "injection_names_after_case_only": injections_after_case,
        "injection_names_after_data": object_names(solver.settings.setup.models.discrete_phase.injections),
        "materials": {
            "fluid": object_names(getattr(materials, "fluid", None)),
            "inert_particle": object_names(getattr(materials, "inert_particle", None)),
        },
        "dpm_general_settings": safe_get_state(solver.settings.setup.models.discrete_phase.general_settings, "dpm.general_settings"),
        "injections": injection_rows,
        "all_injections": inspect_all_injections(solver),
        "boundary_conditions": safe_get_state(
            solver.settings.setup.boundary_conditions, "boundary_conditions"
        ),
    }

    json_path = output_dir / f"{prefix}.json"
    csv_path = output_dir / f"{prefix}.csv"
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    write_csv(csv_path, injection_rows)

    print(f"iteration_after_case_only: {iteration_after_case}")
    print(f"iteration_after_data: {iteration_after_data}")
    print(f"injection_names_after_data: {payload['injection_names_after_data']}")
    print("all_injections:")
    for row in payload["all_injections"]:
        print(
            "  "
            f"{row['injection_name']}: material={row.get('material')} "
            f"diameter_m={row.get('diameter_m')} mass_flow_kgs={row.get('mass_flow_kgs')} "
            f"face_normal={row.get('velocity_use_face_normal')} "
            f"magnitude={row.get('velocity_magnitude')} z_velocity={row.get('velocity_z')}"
        )
    print(f"local_json: {json_path}")
    print(f"local_csv: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
