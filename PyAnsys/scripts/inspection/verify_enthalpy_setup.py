#!/usr/bin/env python3
"""Verify saved Purnanto enthalpy setup against the paper table and Harwell CSV.

This is intended as a GUI-independent setup check.  It reads the inlet phase
mass flows and all nine DPM injection definitions from Fluent, compares them
with the expected paper/CSV values, and writes a compact PASS/FAIL CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPTS = PROJECT_ROOT / "scripts" / "setup"
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SETUP_SCRIPTS))

from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
from run_purnanto_dpm_sensitivity import default_case_data_paths  # noqa: E402


DEFAULT_VERIFY_OUTPUT_DIR = sweep.DEFAULT_LOCAL_OUTPUT_DIR / "verification"


@dataclass
class Check:
    case: str
    condition: str
    scope: str
    item: str
    field: str
    expected: Any
    actual: Any
    passed: bool
    notes: str = ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify Purnanto enthalpy inlet and DPM injection setup without using the Fluent GUI."
    )
    parser.add_argument("--server-id", default="1", help="Configured Fluent server id. Default: 1.")
    parser.add_argument(
        "--case-filter",
        action="append",
        default=[],
        help="Restrict cases by number or condition, e.g. --case-filter 1600. Defaults to all six.",
    )
    parser.add_argument(
        "--current-session",
        action="store_true",
        help="Verify the currently loaded Fluent session instead of loading saved case/data files.",
    )
    parser.add_argument(
        "--case-file",
        default="",
        help="Remote case file to verify. Use with exactly one --case-filter.",
    )
    parser.add_argument(
        "--data-file",
        default="",
        help="Remote data file to verify. Use with --case-file.",
    )
    parser.add_argument(
        "--case-only",
        action="store_true",
        help="Read/verify only the case file. Skips data-file loading.",
    )
    parser.add_argument(
        "--remote-output-dir",
        default=sweep.DEFAULT_REMOTE_OUTPUT_DIR,
        help="Remote folder containing final enthalpy sweep case/data files.",
    )
    parser.add_argument("--harwell-csv", default=str(sweep.DEFAULT_HARWELL_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_VERIFY_OUTPUT_DIR))
    parser.add_argument(
        "--velocity-mode",
        choices=("face-normal", "components", "any"),
        default=sweep.DEFAULT_DPM_VELOCITY_MODE,
        help="Expected injection velocity mode. Default: face-normal.",
    )
    parser.add_argument("--abs-tol", type=float, default=1.0e-7, help="Default absolute float tolerance.")
    parser.add_argument("--rel-tol", type=float, default=1.0e-6, help="Default relative float tolerance.")
    return parser


def nested(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    value: Any = mapping
    for key in keys:
        if not isinstance(value, Mapping):
            return default
        value = value.get(key, default)
    return value


def as_float(value: Any) -> float | None:
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def float_pass(actual: Any, expected: float, *, abs_tol: float, rel_tol: float) -> bool:
    actual_float = as_float(actual)
    if actual_float is None:
        return False
    return math.isclose(actual_float, expected, rel_tol=rel_tol, abs_tol=abs_tol)


def add_check(
    checks: list[Check],
    case: sweep.PaperCase,
    scope: str,
    item: str,
    field: str,
    expected: Any,
    actual: Any,
    passed: bool,
    notes: str = "",
) -> None:
    checks.append(
        Check(
            case=case.csv_case,
            condition=case.condition,
            scope=scope,
            item=item,
            field=field,
            expected=expected,
            actual=actual,
            passed=passed,
            notes=notes,
        )
    )


def check_equal(
    checks: list[Check],
    case: sweep.PaperCase,
    scope: str,
    item: str,
    field: str,
    expected: Any,
    actual: Any,
    notes: str = "",
) -> None:
    add_check(checks, case, scope, item, field, expected, actual, actual == expected, notes)


def check_float(
    checks: list[Check],
    case: sweep.PaperCase,
    scope: str,
    item: str,
    field: str,
    expected: float,
    actual: Any,
    *,
    abs_tol: float,
    rel_tol: float,
    notes: str = "",
) -> None:
    add_check(
        checks,
        case,
        scope,
        item,
        field,
        expected,
        actual,
        float_pass(actual, expected, abs_tol=abs_tol, rel_tol=rel_tol),
        notes,
    )


def object_names(branch: Any) -> list[str]:
    try:
        return sorted(str(name) for name in branch.get_object_names())
    except Exception:
        return []


def check_materials(solver: Any, case: sweep.PaperCase, checks: list[Check]) -> None:
    materials = solver.settings.setup.materials
    inert_names = object_names(materials.inert_particle)
    add_check(
        checks,
        case,
        "materials",
        "inert_particle",
        sweep.PARTICLE_MATERIAL,
        "present",
        "present" if sweep.PARTICLE_MATERIAL in inert_names else inert_names,
        sweep.PARTICLE_MATERIAL in inert_names,
    )


def check_inlet(
    solver: Any,
    case: sweep.PaperCase,
    checks: list[Check],
    *,
    abs_tol: float,
    rel_tol: float,
) -> None:
    inlet = solver.settings.setup.boundary_conditions.mass_flow_inlet[sweep.INLET_NAME]
    state = inlet.get_state()
    gas = nested(state, "phase", "phase-1", "momentum", "mass_flow_rate", "value")
    liquid = nested(state, "phase", "phase-2", "momentum", "mass_flow_rate", "value")
    check_float(
        checks,
        case,
        "boundary_conditions",
        sweep.INLET_NAME,
        "phase-1_gas_mass_flow_kgs",
        case.gas_mass_flow_kgs,
        gas,
        abs_tol=abs_tol,
        rel_tol=rel_tol,
    )
    check_float(
        checks,
        case,
        "boundary_conditions",
        sweep.INLET_NAME,
        "phase-2_liquid_mass_flow_kgs",
        case.liquid_mass_flow_kgs,
        liquid,
        abs_tol=abs_tol,
        rel_tol=rel_tol,
    )


def check_injection(
    state: Mapping[str, Any],
    case: sweep.PaperCase,
    item: sweep.InjectionBin,
    checks: list[Check],
    *,
    velocity_mode: str,
    abs_tol: float,
    rel_tol: float,
) -> None:
    name = item.injection_name
    check_equal(checks, case, "dpm_injection", name, "particle_type", "inert", state.get("particle_type"))
    check_equal(
        checks,
        case,
        "dpm_injection",
        name,
        "material",
        sweep.PARTICLE_MATERIAL,
        state.get("material"),
    )
    check_equal(
        checks,
        case,
        "dpm_injection",
        name,
        "injection_type",
        "surface",
        nested(state, "injection_type", "option"),
    )
    surface = nested(state, "initial_values", "location", "injection_surfaces", default=[])
    check_equal(checks, case, "dpm_injection", name, "surface", [sweep.INJECTION_SURFACE], surface)
    check_float(
        checks,
        case,
        "dpm_injection",
        name,
        "mass_flow_kgs",
        item.mass_flow_kgs,
        nested(state, "initial_values", "mass_flow_rate", "total_flow_rate"),
        abs_tol=abs_tol,
        rel_tol=rel_tol,
    )
    check_float(
        checks,
        case,
        "dpm_injection",
        name,
        "diameter_m",
        item.diameter_m,
        nested(state, "initial_values", "particle_size", "diameter"),
        abs_tol=abs_tol,
        rel_tol=rel_tol,
    )

    velocity = nested(state, "initial_values", "velocity", default={})
    use_face_normal = velocity.get("use_face_normal_direction") if isinstance(velocity, Mapping) else None
    if velocity_mode in ("face-normal", "any"):
        if use_face_normal is True:
            check_equal(checks, case, "dpm_injection", name, "velocity_mode", "face-normal", "face-normal")
            check_float(
                checks,
                case,
                "dpm_injection",
                name,
                "velocity_magnitude_ms",
                abs(item.z_velocity_ms),
                velocity.get("magnitude"),
                abs_tol=abs_tol,
                rel_tol=rel_tol,
            )
            return
        if velocity_mode == "face-normal":
            check_equal(checks, case, "dpm_injection", name, "velocity_mode", "face-normal", "components")

    if velocity_mode in ("components", "any"):
        actual_mode = "components" if use_face_normal is False else "face-normal"
        if velocity_mode == "components":
            check_equal(checks, case, "dpm_injection", name, "velocity_mode", "components", actual_mode)
        else:
            check_equal(checks, case, "dpm_injection", name, "velocity_mode", "any", actual_mode)
        check_float(
            checks,
            case,
            "dpm_injection",
            name,
            "x_velocity_ms",
            0.0,
            velocity.get("x_velocity") if isinstance(velocity, Mapping) else None,
            abs_tol=abs_tol,
            rel_tol=rel_tol,
        )
        check_float(
            checks,
            case,
            "dpm_injection",
            name,
            "y_velocity_ms",
            0.0,
            velocity.get("y_velocity") if isinstance(velocity, Mapping) else None,
            abs_tol=abs_tol,
            rel_tol=rel_tol,
        )
        check_float(
            checks,
            case,
            "dpm_injection",
            name,
            "z_velocity_ms",
            item.z_velocity_ms,
            velocity.get("z_velocity") if isinstance(velocity, Mapping) else None,
            abs_tol=abs_tol,
            rel_tol=rel_tol,
        )


def check_injections(
    solver: Any,
    case: sweep.PaperCase,
    bins: list[sweep.InjectionBin],
    checks: list[Check],
    *,
    velocity_mode: str,
    abs_tol: float,
    rel_tol: float,
) -> None:
    branch = solver.settings.setup.models.discrete_phase.injections
    names = set(object_names(branch))
    expected_names = {item.injection_name for item in bins}
    add_check(
        checks,
        case,
        "dpm_injection",
        "all",
        "expected_injection_count",
        len(expected_names),
        len(names & expected_names),
        expected_names <= names,
        f"available={sorted(names)}",
    )
    for item in bins:
        if item.injection_name not in names:
            add_check(
                checks,
                case,
                "dpm_injection",
                item.injection_name,
                "exists",
                True,
                False,
                False,
            )
            continue
        state = branch[item.injection_name].get_state()
        check_injection(
            state,
            case,
            item,
            checks,
            velocity_mode=velocity_mode,
            abs_tol=abs_tol,
            rel_tol=rel_tol,
        )


def rows_from_checks(checks: list[Check]) -> list[dict[str, Any]]:
    return [
        {
            "passed": "PASS" if check.passed else "FAIL",
            "case": check.case,
            "condition": check.condition,
            "scope": check.scope,
            "item": check.item,
            "field": check.field,
            "expected": json.dumps(check.expected, default=str) if isinstance(check.expected, (list, dict)) else check.expected,
            "actual": json.dumps(check.actual, default=str) if isinstance(check.actual, (list, dict)) else check.actual,
            "notes": check.notes,
        }
        for check in checks
    ]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["passed", "case", "condition", "scope", "item", "field", "expected", "actual", "notes"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def verify_loaded_case(
    solver: Any,
    case: sweep.PaperCase,
    bins: list[sweep.InjectionBin],
    *,
    velocity_mode: str,
    abs_tol: float,
    rel_tol: float,
) -> list[Check]:
    checks: list[Check] = []
    check_materials(solver, case, checks)
    check_inlet(solver, case, checks, abs_tol=abs_tol, rel_tol=rel_tol)
    check_injections(
        solver,
        case,
        bins,
        checks,
        velocity_mode=velocity_mode,
        abs_tol=abs_tol,
        rel_tol=rel_tol,
    )
    return checks


def load_case_data_if_requested(
    solver: Any,
    case_file: str,
    data_file: str,
    *,
    case_only: bool,
) -> None:
    sweep.require_remote_input(solver, case_file, "case")
    if not case_only:
        sweep.require_remote_input(solver, data_file, "data")
    sweep.remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    solver.settings.file.read_case(file_name=case_file)
    if not case_only:
        solver.settings.file.read_data(file_name=data_file)


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    groups = sweep.read_harwell_bins(Path(args.harwell_csv).expanduser().resolve())
    cases = sweep.selected_cases(args.case_filter)
    plan = sweep.build_sweep_plan(cases, groups)
    if args.current_session and len(plan) != 1:
        raise ValueError("--current-session requires exactly one selected case")
    if (args.case_file or args.data_file) and len(plan) != 1:
        raise ValueError("--case-file/--data-file require exactly one selected case")
    if bool(args.case_file) ^ bool(args.data_file) and not args.case_only:
        raise ValueError("--case-file and --data-file must be supplied together unless --case-only is used")

    solver = connect(server_id=args.server_id)
    print(f"connected: {solver.get_fluent_version()}")

    all_checks: list[Check] = []
    for plan_item in plan:
        case: sweep.PaperCase = plan_item["case"]
        bins: list[sweep.InjectionBin] = list(plan_item["bins"])
        case_file, data_file = args.case_file, args.data_file
        if not args.current_session:
            if not case_file and not data_file:
                case_file, data_file = default_case_data_paths(case, args.remote_output_dir)
            print(f"loading: {case.csv_case} {case.condition} -> {case_file}")
            load_case_data_if_requested(solver, case_file, data_file, case_only=args.case_only)
        else:
            print(f"verifying current session as: {case.csv_case} {case.condition}")
        all_checks.extend(
            verify_loaded_case(
                solver,
                case,
                bins,
                velocity_mode=args.velocity_mode,
                abs_tol=args.abs_tol,
                rel_tol=args.rel_tol,
            )
        )

    rows = rows_from_checks(all_checks)
    output_csv = output_dir / "enthalpy_setup_verification.csv"
    write_csv(output_csv, rows)
    failures = [check for check in all_checks if not check.passed]
    print(f"checks: {len(all_checks)}")
    print(f"failures: {len(failures)}")
    print(f"verification_csv: {output_csv}")
    if failures:
        print("first_failures:")
        for failure in failures[:20]:
            print(
                f"  FAIL {failure.case} {failure.condition} {failure.item} "
                f"{failure.field}: expected={failure.expected!r} actual={failure.actual!r}"
            )
        return 1
    print("setup_verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
