#!/usr/bin/env python3
"""Run a verified prepared Phase 7.2A Family E child on student."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "inspection"), str(ROOT / "scripts" / "setup")]

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.common import safe_get_state  # noqa: E402
import run_phase72a_family_r_native as native  # noqa: E402


FILM_MATERIAL = "water-liquid-at-psep"


def alist_value(value: Any, target: str) -> Any:
    if isinstance(value, (list, tuple)):
        for item in value:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                if str(item[0]) == target:
                    return item[1]
            found = alist_value(item, target)
            if found is not None:
                return found
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) == target:
                return item
            found = alist_value(item, target)
            if found is not None:
                return found
    return None


def ewf_validator(
    expected_mode: int,
    expected_initial_dt: float,
    expected_subiterations: int,
    expected_max_thickness: float,
    expected_controls: dict[str, Any],
    expected_flow_momentum_coupling: bool,
):
    def validate(solver: Any, _audit: Any) -> None:
        parameters = solver.rp_vars().get("wall-film/model-parameters")
        material = alist_value(parameters, "film-material")
        mode = alist_value(parameters, "secondary-phase-mode")
        initial_dt = alist_value(parameters, "adapt-init-dt")
        subiterations = alist_value(parameters, "sub-iter-nums")
        max_thickness = alist_value(parameters, "thickness-limit")
        native.require(str(material).strip('"') == FILM_MATERIAL, f"film material mismatch: {material!r}")
        native.require(int(mode) == expected_mode, f"secondary phase mode mismatch: {mode!r}")
        native.require(abs(float(initial_dt) - expected_initial_dt) <= max(1e-12, expected_initial_dt * 1e-9), f"initial film time step mismatch: {initial_dt!r}")
        native.require(int(subiterations) == expected_subiterations, f"film sub-iterations mismatch: {subiterations!r}")
        native.require(
            abs(float(max_thickness) - expected_max_thickness)
            <= max(1e-12, expected_max_thickness * 1e-9),
            f"film thickness limit mismatch: {max_thickness!r}",
        )
        for key, expected in expected_controls.items():
            actual = alist_value(parameters, key)
            if isinstance(expected, float):
                native.require(
                    actual is not None
                    and abs(float(actual) - expected) <= max(1e-12, abs(expected) * 1e-9),
                    f"EWF control {key} mismatch: expected {expected!r}, got {actual!r}",
                )
            else:
                native.require(actual == expected, f"EWF control {key} mismatch: {actual!r}")
        walls = solver.settings.setup.boundary_conditions.wall
        wall_state = walls["wall"].phase["mixture"].wall_film.get_state()
        native.require(wall_state.get("eulerian_film_wall") is True, "wall film is not active on wall")
        native.require(
            wall_state.get("enable_flow_momentum_coupling") is expected_flow_momentum_coupling,
            f"wall flow momentum coupling mismatch: {wall_state.get('enable_flow_momentum_coupling')!r}",
        )
        bottom_state = walls["bottom"].phase["mixture"].wall_film.get_state()
        native.require(bottom_state.get("eulerian_film_wall") is not True, "bottom unexpectedly became a film wall")
        dpm = solver.settings.setup.models.discrete_phase.get_state()
        enabled = dpm.get("physical_models", {}).get("erosion_accretion_enabled")
        native.require(enabled is False, "DPM erosion/accretion must remain off")

    return validate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-receipt", type=Path, required=True)
    parser.add_argument("--local-root", type=Path, required=True)
    parser.add_argument("--case", choices=("E1", "E2", "E2.1", "E2.2", "E2.3", "E2.4", "E2.5", "E2.6", "E2.7", "E3"), required=True)
    parser.add_argument("--secondary-phase-mode", type=int, required=True)
    parser.add_argument("--max-film-thickness", type=float, required=True)
    parser.add_argument("--report-frequency", type=int, required=True)
    parser.add_argument(
        "--run-stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    args = parser.parse_args()
    receipt = json.loads(args.build_receipt.read_text(encoding="utf-8"))
    native.require(receipt.get("status") == "COMPLETE_NO_SOLVE", "prepared build receipt is not complete")
    native.require(receipt.get("solve_issued") is False, "prepared build unexpectedly issued a solve")
    expected_build_case = "E1" if args.case == "E3" else args.case
    native.require(receipt.get("case_id", "E1") == expected_build_case, "wrong EWF build recipe")
    expected_mode = 1 if args.case in {"E2", "E2.1", "E2.2", "E2.3", "E2.4", "E2.5", "E2.6", "E2.7"} else 0
    native.require(args.secondary_phase_mode == expected_mode, "wrong EWF phase-coupling mode")
    native.require(args.report_frequency >= 1, "report frequency must be at least one iteration")
    saved = receipt["saved_pair"]
    receipt_thickness = float(
        receipt.get("screenshot_model_values", {}).get("thickness-limit", float("nan"))
    )
    native.require(
        abs(receipt_thickness - args.max_film_thickness)
        <= max(1e-12, args.max_film_thickness * 1e-9),
        f"build receipt thickness limit {receipt_thickness!r} does not match requested {args.max_film_thickness!r}",
    )
    report_names = [str(name) for name in receipt["ewf_report_names"]]

    native.SERVER_ID = "student"
    native.FAMILY_ID = "P72A-Family-E"
    native.FAMILY_LABEL = f"{args.case}-Eulerian-wall-film"
    native.SETUP_ID_PREFIX = "P72A-FAMILY-E"
    native.PARENT_CASE = saved["case"]
    native.PARENT_DATA = saved["data"]
    native.PARENT_HASHES = {"case": saved["case_sha256"], "data": saved["data_sha256"]}
    native.REMOTE_LOCAL_ROOT = PureWindowsPath(
        r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE"
    )
    native.REMOTE_FINAL_ROOT = PureWindowsPath(
        r"C:\Users\Shuhei Yokkaichi\Documents\OneDrive - The University of Auckland"
        r"\P4P-Fluent-Artifacts\Phase72A\FamilyE"
    )
    expected_initial_dt = float(receipt.get("screenshot_model_values", {}).get("adapt-init-dt", 0.0001))
    expected_subiterations = int(receipt.get("screenshot_model_values", {}).get("sub-iter-nums", 5))
    expected_controls = {
        "E2.4": {"courant-number": 0.05, "film-message?": True, "sub-iter-interval": 1},
        "E2.5": {"ewf-adaptive?": False, "timestep-max": 1e-6, "film-message?": True, "sub-iter-interval": 1},
        "E2.6": {
            "film-coupled-solution?": True,
            "ewf-adaptive?": False,
            "timestep-max": 1e-5,
            "courant-number": 0.05,
            "sub-iter-nums": 10,
            "film-message?": True,
            "sub-iter-interval": 1,
        },
        "E2.7": {
            "film-coupled-solution?": True,
            "ewf-adaptive?": False,
            "timestep-max": 1e-5,
            "courant-number": 0.05,
            "sub-iter-nums": 10,
            "film-message?": True,
            "sub-iter-interval": 1,
        },
    }.get(args.case, {})
    native.validate_model_state = ewf_validator(
        args.secondary_phase_mode,
        expected_initial_dt,
        expected_subiterations,
        args.max_film_thickness,
        expected_controls,
        expected_flow_momentum_coupling=args.case != "E2.7",
    )
    native.controlled_delta_record = lambda case_id, ks, cs: {
        "EWF": "phase-accretion" if case_id in {"E2", "E2.1", "E2.2", "E2.3", "E2.4", "E2.5", "E2.6", "E2.7"} else "basic",
        "roughness_height_m": ks,
        "roughness_constant_Cs": cs,
        "film_material": FILM_MATERIAL,
        "film_wall": "wall",
        "secondary_phase_mode": args.secondary_phase_mode,
        "film_initial_time_step_s": receipt.get("screenshot_model_values", {}).get("adapt-init-dt"),
        "film_subiterations": receipt.get("screenshot_model_values", {}).get("sub-iter-nums"),
        "film_maximum_thickness_m": receipt.get("screenshot_model_values", {}).get("thickness-limit"),
        "film_adaptive_time_stepping": receipt.get("screenshot_model_values", {}).get("ewf-adaptive?"),
        "film_courant_number": receipt.get("screenshot_model_values", {}).get("courant-number"),
        "film_fixed_time_step_s": receipt.get("screenshot_model_values", {}).get("timestep-max") if case_id in {"E2.5", "E2.6", "E2.7"} else None,
        "film_coupled_solution": receipt.get("screenshot_model_values", {}).get("film-coupled-solution?"),
        "film_flow_momentum_coupling": case_id != "E2.7",
        "interaction_basis": "E1-basic-EWF-plus-R3-roughness" if case_id == "E3" else None,
        "authoritative_baseline_case": receipt["parent_case"],
        "authoritative_baseline_data": receipt["parent_data"],
    }

    original_definitions = native.configure_definitions
    original_report_files = native.configure_report_files

    def configure_outer_wall_velocity_report(solver: Any) -> tuple[str, dict[str, Any]]:
        surface = solver.settings.solution.report_definitions.surface
        name = "family-e-outer-wall-liquid-y-velocity"
        existing = {str(item) for item in surface.get_object_names()}
        if name in existing:
            surface.delete(name_list=[name])
        surface.create(name=name)
        report = surface[name]
        report.report_type = "surface-areaavg"
        report = surface[name]
        report.field = "phase-2-y-velocity"
        report.surface_names = list(native.OUTER_WALL_ZONES)
        report.per_surface = False
        report.average_over = 1
        report.create_report_file = False
        report.create_report_plot = False
        state = safe_get_state(report, name)
        native.require(state.get("report_type") == "surface-areaavg", f"outer-wall report mismatch: {state}")
        native.require(state.get("field") == "phase-2-y-velocity", f"outer-wall field mismatch: {state}")
        return name, state

    def configure_definitions_with_ewf(solver: Any) -> list[str]:
        bulk = original_definitions(solver)
        available = {
            str(name)
            for name in solver.settings.solution.report_definitions.surface.get_object_names()
        }
        native.require(set(report_names).issubset(available), "prepared EWF reports are missing")
        return [*bulk, *report_names]

    def configure_report_files_at_frequency(
        solver: Any, monitor_root: str, case: str, definitions: list[str]
    ) -> dict[str, str]:
        paths = original_report_files(
            solver, monitor_root, case, definitions, frequency=args.report_frequency
        )
        files = solver.settings.solution.monitor.report_files
        for name in files.get_object_names():
            state = files[str(name)].get_state()
            if state.get("active") and state.get("report_defs"):
                native.require(
                    int(state.get("frequency", -1)) == args.report_frequency,
                    f"report-file frequency mismatch in {name}: {state}",
                )
        return paths

    native.configure_definitions = configure_definitions_with_ewf
    native.configure_report_files = configure_report_files_at_frequency
    native.configure_outer_wall_velocity_report = configure_outer_wall_velocity_report

    local_root = args.local_root.expanduser().resolve()
    local_root.mkdir(parents=True, exist_ok=False)
    queue_path = local_root / "queue-manifest.json"
    queue: dict[str, Any] = {
        "status": "RUNNING",
        "family": native.FAMILY_ID,
        "server_id": "student",
        "case_id": args.case,
        "run_stamp": args.run_stamp,
        "build_receipt": str(args.build_receipt.resolve()),
        "prepared_parent": native.PARENT_CASE,
        "prepared_parent_sha256": native.PARENT_HASHES,
        "authoritative_baseline": {
            "case": receipt["parent_case"],
            "data": receipt["parent_data"],
            "native_iteration": native.PARENT_START,
        },
        "ewf_report_names": report_names,
    }
    native.dump(queue_path, queue)
    try:
        solver = connect("student", start_transcript=True, tcp_timeout_seconds=10)
        roughness_height = 5e-4 if args.case == "E3" else 0.0
        result = native.one_case(
            solver, args.case, roughness_height, 0.5, args.run_stamp, local_root
        )
        queue["status"] = result["status"]
        queue["case_manifest"] = str(local_root / args.case / "run-manifest.json")
        native.dump(queue_path, queue)
        print(json.dumps(queue, indent=2))
        return 0
    except Exception as exc:
        queue["status"] = "BLOCKED"
        queue["error"] = f"{type(exc).__name__}: {exc}"
        queue["traceback"] = traceback.format_exc()
        native.dump(queue_path, queue)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
