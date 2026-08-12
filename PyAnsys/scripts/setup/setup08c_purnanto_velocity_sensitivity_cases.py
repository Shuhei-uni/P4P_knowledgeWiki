#!/usr/bin/env python3
"""Create setup 08c inlet-loading sensitivity case files from the 08b case.

This script intentionally writes case-only `.cas.h5` artifacts. It does not
initialize, iterate, or write data files.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state, try_action  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, write_case_only  # noqa: E402


DEFAULT_SERVER_ID = "2"
DEFAULT_SOURCE_CASE = (
    r"C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)"
    r"\TwoPhaseInletV2(Purnanto).cas.h5"
)
DEFAULT_SUMMARY_JSON = PROJECT_ROOT / "output" / "setup08c_velocity_sensitivity_cases_summary.json"


@dataclass(frozen=True)
class VelocityCase:
    label: str
    target_velocity_m_s: float
    liquid_mass_flow_kg_s: float
    vapor_mass_flow_kg_s: float
    output_name: str


VELOCITY_CASES = (
    VelocityCase(
        label="08c-v20p00",
        target_velocity_m_s=20.00,
        liquid_mass_flow_kg_s=86.18,
        vapor_mass_flow_kg_s=60.21,
        output_name="TwoPhaseInletV2(Purnanto)-08c-v20p00.cas.h5",
    ),
    VelocityCase(
        label="08c-v32p14",
        target_velocity_m_s=32.14,
        liquid_mass_flow_kg_s=138.48,
        vapor_mass_flow_kg_s=96.76,
        output_name="TwoPhaseInletV2(Purnanto)-08c-v32p14.cas.h5",
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Load the setup 08b Purnanto split-inlet case, update only the split "
            "mass-flow inlet loading for the 08c velocity endpoints, and write "
            "case-only .cas.h5 files."
        )
    )
    parser.add_argument("--server-id", default=DEFAULT_SERVER_ID, help="Configured Fluent server id. Default: 2.")
    parser.add_argument("--source-case", default=DEFAULT_SOURCE_CASE, help="Remote 08b .cas.h5 source case.")
    parser.add_argument(
        "--output-dir",
        default="",
        help="Remote output directory. Defaults to the source case directory.",
    )
    parser.add_argument(
        "--summary-json",
        default=str(DEFAULT_SUMMARY_JSON),
        help="Local JSON summary path for applied settings and readbacks.",
    )
    parser.add_argument(
        "--only",
        choices=[case.label for case in VELOCITY_CASES],
        default="",
        help="Build only one endpoint. Default: build both.",
    )
    return parser


def _phase_momentum(state: dict[str, Any], phase_name: str) -> dict[str, Any]:
    phase_state = state.setdefault("phase", {}).setdefault(phase_name, {})
    if not isinstance(phase_state, dict):
        raise TypeError(f"phase {phase_name} is not a mapping")
    momentum = phase_state.setdefault("momentum", {})
    if not isinstance(momentum, dict):
        raise TypeError(f"phase {phase_name} momentum is not a mapping")
    return momentum


def _set_mass_flow_if_present(state: dict[str, Any], phase_name: str, value: float, *, required: bool) -> bool:
    momentum = _phase_momentum(state, phase_name)
    mass_flow = momentum.get("mass_flow_rate")
    if mass_flow is None:
        if required:
            raise KeyError(f"{phase_name}.momentum.mass_flow_rate is missing")
        return False
    if not isinstance(mass_flow, dict):
        if required:
            raise TypeError(f"{phase_name}.momentum.mass_flow_rate is not a mapping")
        return False

    momentum["mass_flow_specification"] = "Mass Flow Rate"
    mass_flow["option"] = "value"
    mass_flow["value"] = value
    return True


def _extract_mass_flow_value(state: Any, phase_name: str) -> float | None:
    if not isinstance(state, dict):
        return None
    try:
        mass_flow = state["phase"][phase_name]["momentum"]["mass_flow_rate"]
    except (KeyError, TypeError):
        return None
    if isinstance(mass_flow, dict):
        value = mass_flow.get("value")
        return float(value) if value is not None else None
    return None


def _mass_flow_inlet_names(solver: Any) -> list[str]:
    branch = solver.settings.setup.boundary_conditions.mass_flow_inlet
    try:
        return sorted(str(name) for name in branch.get_object_names())
    except Exception:
        state = safe_get_state(branch, "mass_flow_inlet")
        if isinstance(state, dict):
            return sorted(name for name, value in state.items() if isinstance(value, dict) and name != "settings")
        return []


def _get_inlet_state(solver: Any, inlet_name: str) -> dict[str, Any]:
    state = safe_get_state(
        solver.settings.setup.boundary_conditions.mass_flow_inlet[inlet_name],
        f"mass_flow_inlet.{inlet_name}",
    )
    if not isinstance(state, dict):
        raise RuntimeError(f"Could not read mass-flow inlet state for {inlet_name}: {state}")
    return state


def _apply_inlet_state(solver: Any, inlet_name: str, inlet_state: dict[str, Any]) -> None:
    if not try_action(
        f"set_mass_flow_inlet_{inlet_name}",
        lambda: solver.settings.setup.boundary_conditions.mass_flow_inlet[inlet_name].set_state(inlet_state),
    ):
        raise RuntimeError(f"Could not set mass-flow inlet state for {inlet_name}")


def apply_velocity_case(solver: Any, case: VelocityCase) -> dict[str, Any]:
    print_header(f"Apply {case.label}")
    inlet_names = _mass_flow_inlet_names(solver)
    missing = sorted({"liquidinlet", "steaminlet"} - set(inlet_names))
    if missing:
        raise RuntimeError(f"Required split mass-flow inlet(s) missing: {missing}; available={inlet_names}")

    before = {
        "liquidinlet": _get_inlet_state(solver, "liquidinlet"),
        "steaminlet": _get_inlet_state(solver, "steaminlet"),
    }
    liquid_state = copy.deepcopy(before["liquidinlet"])
    steam_state = copy.deepcopy(before["steaminlet"])

    liquid_state["name"] = "liquidinlet"
    steam_state["name"] = "steaminlet"

    _set_mass_flow_if_present(liquid_state, "phase-2", case.liquid_mass_flow_kg_s, required=True)
    _set_mass_flow_if_present(liquid_state, "phase-1", 0.0, required=False)
    _set_mass_flow_if_present(steam_state, "phase-1", case.vapor_mass_flow_kg_s, required=True)
    _set_mass_flow_if_present(steam_state, "phase-2", 0.0, required=False)

    _apply_inlet_state(solver, "liquidinlet", liquid_state)
    _apply_inlet_state(solver, "steaminlet", steam_state)

    after = {
        "liquidinlet": _get_inlet_state(solver, "liquidinlet"),
        "steaminlet": _get_inlet_state(solver, "steaminlet"),
    }
    readback = {
        "liquidinlet_phase_2_mass_flow_kg_s": _extract_mass_flow_value(after["liquidinlet"], "phase-2"),
        "liquidinlet_phase_1_mass_flow_kg_s": _extract_mass_flow_value(after["liquidinlet"], "phase-1"),
        "steaminlet_phase_1_mass_flow_kg_s": _extract_mass_flow_value(after["steaminlet"], "phase-1"),
        "steaminlet_phase_2_mass_flow_kg_s": _extract_mass_flow_value(after["steaminlet"], "phase-2"),
    }
    expected = {
        "liquidinlet_phase_2_mass_flow_kg_s": case.liquid_mass_flow_kg_s,
        "steaminlet_phase_1_mass_flow_kg_s": case.vapor_mass_flow_kg_s,
    }
    for key, expected_value in expected.items():
        actual_value = readback[key]
        if actual_value is None or abs(actual_value - expected_value) > 1e-8:
            raise RuntimeError(f"Readback mismatch for {case.label} {key}: expected {expected_value}, got {actual_value}")

    return {
        "label": case.label,
        "target_velocity_m_s": case.target_velocity_m_s,
        "expected": {
            "liquid_mass_flow_kg_s": case.liquid_mass_flow_kg_s,
            "vapor_mass_flow_kg_s": case.vapor_mass_flow_kg_s,
        },
        "readback": readback,
    }


def output_path_for(source_case: str, output_dir: str, case: VelocityCase) -> str:
    source = PureWindowsPath(source_case)
    directory = PureWindowsPath(output_dir) if output_dir else source.parent
    return str(directory / case.output_name)


def write_summary(path_text: str, payload: dict[str, Any]) -> None:
    path = Path(path_text).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"summary_json: {path}", flush=True)


def main() -> int:
    args = build_parser().parse_args()
    selected_cases = [case for case in VELOCITY_CASES if not args.only or case.label == args.only]
    solver = connect(server_id=args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")

    summary: dict[str, Any] = {
        "source_case": args.source_case,
        "cases": [],
    }

    for velocity_case in selected_cases:
        output_case = output_path_for(args.source_case, args.output_dir, velocity_case)
        load_case_only(solver, args.source_case, label=f"Load Source Case For {velocity_case.label}")
        case_summary = apply_velocity_case(solver, velocity_case)
        write_case_only(solver, output_case, velocity_case.label)
        if not remote_file_exists(solver, output_case):
            raise RuntimeError(f"Fluent reported write success but output case is not visible: {output_case}")
        case_summary["output_case"] = output_case
        case_summary["output_exists"] = True
        summary["cases"].append(case_summary)

    write_summary(args.summary_json, summary)
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
