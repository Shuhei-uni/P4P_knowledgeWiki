#!/usr/bin/env python3
"""Build and persist a no-solve Phase 7.2A EWF E1/E2 capability probe."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import re
import sys
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.ewf_report_specs import REPORT_SPECS  # noqa: E402
from pyansys_fluent.ewf_reports import ensure_surface_report  # noqa: E402
from pyansys_fluent.stage4_native import data_path, ensure_remote_directory  # noqa: E402
from run_p71a_r0_control_continuation import pair_save  # noqa: E402


PARENT_CASE = (
    "C:/Users/Shuhei Yokkaichi/Documents/FluentRuns/Phase72A/FamilyE/"
    "parent-transfer-20260922T115133Z/"
    "P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-"
    "full-loading-plus1000.cas.h5"
)
PARENT_DATA = PARENT_CASE.replace(".cas.h5", ".dat.h5")
PARENT_NATIVE = 5586
FILM_MATERIAL = "water-liquid-at-psep"
E1_REPORT_KEYS = {
    "film_courant_max",
    "film_mass_total",
    "film_thickness_max",
    "film_thickness_area_average",
    "film_outflow_mass_total",
    "film_velocity_area_average",
    "film_velocity_max",
    "film_y_velocity_area_average",
}
E2_REPORT_KEYS = E1_REPORT_KEYS | {
    "film_secondary_phase_mass_total",
    "film_secondary_phase_collection_area_average",
}
SCREENSHOT_MODEL_VALUES = {
    "solve-momentum?": True,
    "mom-equation?": True,
    "mom-gravity?": True,
    "mom-aero-drive?": True,
    "mom-pressure?": False,
    "solve-energy?": False,
    "solve-scalar?": False,
    "dpm-collection?": False,
    "dpm-splashing?": False,
    "film-stripping?": False,
    "film-separation?": False,
    "treat-sharp-edge?": False,
    "secondary-phase-mode": 0,
    "film-vof-coupling?": False,
    "time-scheme": 2,
    "mass-scheme": 0,
    "mom-scheme": 0,
    "thickness-limit": 0.01,
    "film-coupled-solution?": False,
    "ewf-adaptive?": True,
    "courant-number": 0.25,
    "adapt-init-dt": 0.0001,
    "adapt-tstp-inc": 1.5,
    "adapt-tstp-dec": 2.0,
    "sub-iter-stop": 1e-5,
    "sub-iter-nums": 5,
    "sub-iter-interval": 1,
    "film-message?": True,
}


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def model_parameters(solver: Any) -> Any:
    values = solver.rp_vars()
    return values.get("wall-film/model-parameters")


def critical_readback(solver: Any) -> dict[str, Any]:
    wall = solver.settings.setup.boundary_conditions.wall
    dpm = solver.settings.setup.models.discrete_phase.get_state()
    return {
        "native_iteration": float(
            solver.settings.setup.named_expressions["P71V2Iteration"].get_value()
        ),
        "model_parameters": model_parameters(solver),
        "film_wall": safe_get_state(
            wall["wall"].phase["mixture"].wall_film, "wall.phase.mixture.wall_film"
        ),
        "bottom_wall": safe_get_state(wall["bottom"], "bottom"),
        "dpm_erosion_accretion_enabled": (
            dpm.get("physical_models", {}).get("erosion_accretion_enabled")
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("E1", "E2", "E2.1", "E2.2", "E2.3", "E2.4", "E2.5", "E2.6", "E2.7"), default="E1")
    parser.add_argument("--initial-film-dt", type=float, default=0.0001)
    parser.add_argument("--film-courant", type=float)
    parser.add_argument("--adaptive-film-timestep", choices=("on", "off"))
    parser.add_argument("--fixed-film-timestep", type=float)
    parser.add_argument("--film-subiterations", type=int, default=5)
    parser.add_argument("--max-film-thickness", type=float, default=0.01)
    parser.add_argument("--report-frequency", type=int, default=10)
    parser.add_argument("--local-root", type=Path, required=True)
    parser.add_argument(
        "--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    args = parser.parse_args()
    require(args.initial_film_dt > 0, "initial film time step must be positive")
    require(args.film_courant is None or args.film_courant > 0, "film Courant number must be positive")
    require(args.fixed_film_timestep is None or args.fixed_film_timestep > 0, "fixed film time step must be positive")
    require(args.film_subiterations >= 1, "film sub-iterations must be positive")
    require(args.max_film_thickness > 0, "maximum film thickness must be positive")
    require(args.report_frequency >= 1, "report frequency must be at least one iteration")
    local_root = args.local_root.expanduser().resolve()
    local_root.mkdir(parents=True, exist_ok=False)
    receipt_path = local_root / "probe-receipt.json"
    remote_root = PureWindowsPath(
        rf"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE"
        rf"\{args.case}\quoted-material-probe-{args.stamp}"
    )
    probe_case = remote_root / f"P72A-{args.case}-quoted-material-probe.cas.h5"
    receipt: dict[str, Any] = {
        "status": "PREFLIGHT",
        "server_id": "student",
        "case_id": args.case,
        "parent_case": PARENT_CASE,
        "parent_data": PARENT_DATA,
        "remote_root": str(remote_root),
        "probe_case": str(probe_case),
        "solve_issued": False,
    }
    dump(receipt_path, receipt)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect("student", start_transcript=True, tcp_timeout_seconds=10)
        require("2025 R2" in str(solver.get_fluent_version()), "wrong Fluent release")
        ensure_remote_directory(solver, str(remote_root))
        require(remote_file_exists(solver, PARENT_CASE), "student parent case is missing")
        require(remote_file_exists(solver, PARENT_DATA), "student parent data is missing")
        solver.settings.file.read_case(file_name=PARENT_CASE)
        solver.settings.file.read_data(file_name=PARENT_DATA)
        start = float(
            solver.settings.setup.named_expressions["P71V2Iteration"].get_value()
        )
        require(round(start) == PARENT_NATIVE, f"wrong parent coordinate: {start}")

        capture = SessionTranscriptCapture(
            solver, stream_path=local_root / "probe-transcript.txt", echo=False
        ).start()
        marker = capture.mark()
        ewf = solver.tui.define.models.eulerian_wallfilm
        ewf.enable_wallfilm_model("yes")
        # Use a raw command so Fluent receives the hyphenated material as a
        # quoted string rather than as an unbound Scheme symbol.
        solver.execute_tui(
            '/define/models/eulerian-wallfilm/film-material yes '
            f'"{FILM_MATERIAL}"\n'
        )
        ewf = solver.tui.define.models.eulerian_wallfilm
        previous_parameters = model_parameters(solver)
        require(isinstance(previous_parameters, list), "EWF parameters are unavailable")
        require(
            set(SCREENSHOT_MODEL_VALUES).issubset({str(k) for k, _ in previous_parameters}),
            "EWF screenshot controls are missing from this release",
        )
        target_values = dict(SCREENSHOT_MODEL_VALUES)
        target_values["secondary-phase-mode"] = 1 if args.case in {"E2", "E2.1", "E2.2", "E2.3", "E2.4", "E2.5", "E2.6", "E2.7"} else 0
        target_values["adapt-init-dt"] = args.initial_film_dt
        target_values["sub-iter-nums"] = args.film_subiterations
        target_values["thickness-limit"] = args.max_film_thickness
        if args.case == "E2.4":
            target_values["courant-number"] = 0.05
        elif args.case == "E2.5":
            target_values["ewf-adaptive?"] = False
            target_values["timestep-max"] = 1e-6
        elif args.case in {"E2.6", "E2.7"}:
            target_values["film-coupled-solution?"] = True
        if args.film_courant is not None:
            target_values["courant-number"] = args.film_courant
        if args.adaptive_film_timestep is not None:
            target_values["ewf-adaptive?"] = args.adaptive_film_timestep == "on"
        if args.fixed_film_timestep is not None:
            target_values["timestep-max"] = args.fixed_film_timestep
        changed_parameters = [
            (key, target_values.get(str(key), value))
            for key, value in previous_parameters
        ]
        solver.rp_vars("wall-film/model-parameters", changed_parameters)
        current_parameters = dict(model_parameters(solver))
        for key, expected in target_values.items():
            require(current_parameters.get(key) == expected, f"{key} mismatch")
        ewf.solve_wallfilm_equation("yes")

        film_wall = (
            solver.settings.setup.boundary_conditions.wall["wall"]
            .phase["mixture"]
            .wall_film
        )
        film_wall.eulerian_film_wall = True
        film_wall = (
            solver.settings.setup.boundary_conditions.wall["wall"]
            .phase["mixture"]
            .wall_film
        )
        film_wall.film_condition_type = "film-wall-boundary"
        flow_momentum_coupling = args.case != "E2.7"
        film_wall.enable_flow_momentum_coupling = flow_momentum_coupling
        ewf.initialize_wallfilm_model()
        capture.wait_until_quiet(quiet_seconds=1.0, timeout_seconds=10.0)
        transcript = capture.text_since(marker)
        receipt["configuration_transcript"] = transcript
        receipt["screenshot_model_values"] = target_values
        require(
            not re.search(
                r"(?:^|\n)\s*(?:Error:|Invalid |SIGSEGV|segmentation)",
                transcript,
                re.IGNORECASE,
            ),
            "Fluent reported an EWF configuration error",
        )
        before = critical_readback(solver)
        receipt["readback_before_save"] = before
        parameters_text = json.dumps(before["model_parameters"], default=str)
        require(FILM_MATERIAL in parameters_text, "film material readback mismatch")
        require(before["film_wall"].get("eulerian_film_wall") is True, "wall is not a film wall")
        require(
            before["film_wall"].get("enable_flow_momentum_coupling") is flow_momentum_coupling,
            "film-wall flow momentum coupling readback mismatch",
        )
        require(
            before["dpm_erosion_accretion_enabled"] is False,
            "DPM erosion/accretion was unexpectedly enabled",
        )
        require(round(before["native_iteration"]) == PARENT_NATIVE, "probe changed native coordinate")

        report_names: list[str] = []
        required_report_keys = E2_REPORT_KEYS if args.case in {"E2", "E2.1", "E2.2", "E2.3", "E2.4", "E2.5", "E2.6", "E2.7"} else E1_REPORT_KEYS
        if args.case in {"E2", "E2.1", "E2.2", "E2.3", "E2.4", "E2.5", "E2.6", "E2.7"}:
            # Fluent 2025 R2 exposes these fields only with Phase Accretion.
            receipt["phase_accretion_report_gate"] = {
                "mode": current_parameters.get("secondary-phase-mode"),
                "required_keys": sorted(E2_REPORT_KEYS - E1_REPORT_KEYS),
            }
        receipt["ewf_reports"] = []
        for spec in REPORT_SPECS:
            if spec.key not in required_report_keys:
                continue
            configured = ensure_surface_report(
                solver,
                spec,
                prefix=f"p72a-{args.case.lower()}-ewf",
                surfaces=["wall"],
                object_policy="replace",
                create_history_file=False,
                frequency=args.report_frequency,
            )
            report_names.append(configured["name"])
            receipt["ewf_reports"].append(configured)
        receipt["ewf_report_names"] = report_names
        require(len(report_names) == len(required_report_keys), "incomplete film instrumentation")

        receipt["saved_pair"] = pair_save(solver, str(probe_case))
        solver.settings.file.read_case(file_name=str(probe_case))
        solver.settings.file.read_data(file_name=data_path(str(probe_case)))
        after = critical_readback(solver)
        receipt["readback_after_reopen"] = after
        reopened_reports = {
            str(name)
            for name in solver.settings.solution.report_definitions.surface.get_object_names()
        }
        receipt["ewf_report_names_after_reopen"] = sorted(
            reopened_reports.intersection(report_names)
        )
        require(json.dumps(after["model_parameters"], default=str) == parameters_text, "model parameters did not persist")
        require(after["film_wall"].get("eulerian_film_wall") is True, "film wall did not persist")
        require(
            after["film_wall"].get("enable_flow_momentum_coupling") is flow_momentum_coupling,
            "reopened film-wall flow momentum coupling mismatch",
        )
        require(round(after["native_iteration"]) == PARENT_NATIVE, "reopen changed native coordinate")
        require(set(report_names).issubset(reopened_reports), "film reports did not persist")
        receipt["status"] = "COMPLETE_NO_SOLVE"
        dump(receipt_path, receipt)
        print(json.dumps(receipt, indent=2, default=str))
        return 0
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        receipt["traceback"] = traceback.format_exc()
        dump(receipt_path, receipt)
        traceback.print_exc()
        return 1
    finally:
        if capture is not None:
            capture.close()


if __name__ == "__main__":
    raise SystemExit(main())
