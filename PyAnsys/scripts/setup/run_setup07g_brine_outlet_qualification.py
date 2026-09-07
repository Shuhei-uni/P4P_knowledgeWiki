#!/usr/bin/env python3
"""Run the setup-07g resolved-brine-outlet carrier qualification."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.mesh_convergence import (  # noqa: E402
    monitor_stability,
    parse_named_report_rows,
    parse_net_report_value,
)

import prepare_setup07g_brine_outlet as prepare07g  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = prepare07g.STUDY_ID
RUN_LABEL = prepare07g.RUN_LABEL
REMOTE_ROOT = prepare07g.REMOTE_ROOT
LOCAL_ROOT = prepare07g.LOCAL_ROOT
PREPARATION_MANIFEST = LOCAL_ROOT / "preparation_manifest.json"
TOTAL_INLET_KGS = 116.92 + 80.69
TARGET_ITERATIONS = 3000
CHECKPOINTS = {250, 500, 1000, 2000, 3000}
ZONES = ["liquidinlet", "steaminlet", "steamoutlet", "brineoutlet"]
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--resume-case", default="")
    result.add_argument("--resume-data", default="")
    result.add_argument("--resume-iterations", type=int, default=0)
    return result


def remote_join(directory: str, name: str) -> str:
    return str(PureWindowsPath(directory) / name)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({str(key) for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def mass_flows(solver: Any, domain: str, label: str) -> dict[str, float]:
    report = solver.settings.results.report.fluxes
    text = mesh_study.report_file_text(
        solver,
        REMOTE_ROOT,
        label,
        lambda path: report.mass_flow(
            domain=domain,
            zones=ZONES,
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    values = parse_named_report_rows(text, ZONES)
    missing = [zone for zone in ZONES if zone not in values]
    if missing:
        raise RuntimeError(f"mass-flow report {domain} missing zones {missing}: {text}")
    values["Net"] = parse_net_report_value(text)
    return values


def volume_average(solver: Any, field: str, label: str) -> float:
    report = solver.settings.results.report.volume_integrals
    text = mesh_study.report_file_text(
        solver,
        REMOTE_ROOT,
        label,
        lambda path: report.volume_average(
            cell_zones=["fluid"],
            cell_function=field,
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    values = parse_named_report_rows(text, ["fluid"])
    if "fluid" not in values:
        raise RuntimeError(f"volume-average report {field} could not be parsed: {text}")
    return values["fluid"]


def physical_metrics(solver: Any, iteration: int) -> dict[str, Any]:
    mixture = mass_flows(solver, "mixture", f"mixture_iter{iteration}")
    vapor = mass_flows(solver, "phase-1", f"vapor_iter{iteration}")
    liquid = mass_flows(solver, "phase-2", f"liquid_iter{iteration}")
    inlet_pressure = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"inlet_pressure_iter{iteration}",
        ["liquidinlet", "steaminlet"],
        "pressure",
        average="mass",
    )["Net"]
    steam_pressure = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"steam_pressure_iter{iteration}",
        ["steamoutlet"],
        "pressure",
        average="mass",
    )["Net"]
    brine_pressure = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"brine_pressure_iter{iteration}",
        ["brineoutlet"],
        "pressure",
        average="mass",
    )["Net"]
    steam_velocity = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"steam_velocity_iter{iteration}",
        ["steamoutlet"],
        "velocity-magnitude",
    )["Net"]
    brine_velocity = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"brine_velocity_iter{iteration}",
        ["brineoutlet"],
        "velocity-magnitude",
    )["Net"]
    vapor_steam = abs(vapor["steamoutlet"])
    liquid_steam = abs(liquid["steamoutlet"])
    vapor_brine = abs(vapor["brineoutlet"])
    liquid_brine = abs(liquid["brineoutlet"])
    steam_total = vapor_steam + liquid_steam
    brine_total = vapor_brine + liquid_brine
    return {
        "iteration": iteration,
        **{
            f"mixture_{zone}_kgs": mixture[zone]
            for zone in ZONES
        },
        "mixture_net_kgs": mixture["Net"],
        "mixture_imbalance_percent": abs(mixture["Net"]) / TOTAL_INLET_KGS * 100.0,
        **{f"vapor_{zone}_kgs": vapor[zone] for zone in ZONES},
        "vapor_net_kgs": vapor["Net"],
        "vapor_imbalance_percent": abs(vapor["Net"]) / 80.69 * 100.0,
        **{f"liquid_{zone}_kgs": liquid[zone] for zone in ZONES},
        "liquid_net_kgs": liquid["Net"],
        "liquid_imbalance_percent": abs(liquid["Net"]) / 116.92 * 100.0,
        "steamoutlet_quality_percent": (
            100.0 * vapor_steam / steam_total if steam_total else math.nan
        ),
        "brineoutlet_liquid_fraction_percent": (
            100.0 * liquid_brine / brine_total if brine_total else math.nan
        ),
        "vapor_recovery_at_steamoutlet_percent": 100.0 * vapor_steam / 80.69,
        "liquid_recovery_at_brineoutlet_percent": 100.0 * liquid_brine / 116.92,
        "liquid_carryover_at_steamoutlet_percent_of_feed": 100.0 * liquid_steam / 116.92,
        "vapor_carryunder_at_brineoutlet_percent_of_feed": 100.0 * vapor_brine / 80.69,
        "inlet_mass_weighted_pressure_pa": inlet_pressure,
        "steamoutlet_mass_weighted_pressure_pa": steam_pressure,
        "brineoutlet_mass_weighted_pressure_pa": brine_pressure,
        "pressure_drop_to_steamoutlet_pa": inlet_pressure - steam_pressure,
        "pressure_drop_to_brineoutlet_pa": inlet_pressure - brine_pressure,
        "steamoutlet_area_weighted_velocity_ms": steam_velocity,
        "brineoutlet_area_weighted_velocity_ms": brine_velocity,
        "domain_volume_avg_velocity_ms": volume_average(
            solver, "velocity-magnitude", f"domain_velocity_iter{iteration}"
        ),
        "domain_volume_avg_vorticity_s-1": volume_average(
            solver, "vorticity-mag", f"domain_vorticity_iter{iteration}"
        ),
        "domain_volume_avg_liquid_volume_fraction": volume_average(
            solver,
            "phase-2-vof",
            f"domain_liquid_vf_iter{iteration}",
        ),
    }


def save_pair(solver: Any, label: str) -> dict[str, str]:
    case = remote_join(REMOTE_ROOT, f"{RUN_LABEL}_{label}.cas.h5")
    data = remote_join(REMOTE_ROOT, f"{RUN_LABEL}_{label}.dat.h5")
    sweep.write_case_data_pair(solver, case, data, f"07g_{label}")
    return {"case": case, "data": data}


def validation_errors(
    solver: Any, preparation: Mapping[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    mesh_metrics = preparation["mesh_metrics"]
    snapshot = mesh_study.capture_settings(solver, REMOTE_ROOT)
    snapshot.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT))
    errors = prepare07g.validate_prepared(snapshot, mesh_metrics)
    errors.extend(
        error
        for error in mesh_study.validate_settings(
            snapshot, mesh_metrics, require_phase_identity=True
        )
        if error not in errors and not error.startswith("boundary role 'bottom'")
    )
    fingerprint = mesh_study.fingerprint_sha256(mesh_study.critical_fingerprint(snapshot))
    expected = preparation["full_settings_fingerprint_sha256"]
    if fingerprint != expected:
        errors.append(f"prepared settings fingerprint mismatch: {fingerprint} != {expected}")
    return errors, snapshot


def checkpoint_schedule(completed: int) -> int:
    if completed == 0:
        return 25
    if completed == 25:
        return 225
    return min(250, TARGET_ITERATIONS - completed)


def transcript_residual_rows(solver: Any, transcript: str) -> list[dict[str, Any]]:
    text = sweep.remote_text_read_best_effort(solver, transcript)
    pattern = re.compile(
        rf"^\s*(\d+)\s+({NUMBER})\s+({NUMBER})\s+({NUMBER})\s+"
        rf"({NUMBER})\s+({NUMBER})\s+({NUMBER})\s+({NUMBER})\s+",
        re.MULTILINE,
    )
    fields = (
        "iteration",
        "continuity",
        "x-velocity",
        "y-velocity",
        "z-velocity",
        "k",
        "epsilon",
        "vf-phase-2",
    )
    return [
        {
            field: int(value) if field == "iteration" else float(value)
            for field, value in zip(fields, match.groups())
        }
        for match in pattern.finditer(text)
    ]


def proven_iteration_block(
    solver: Any, transcript: str, requested: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    before_monitor = mesh_study.monitor_snapshot(solver)
    before_points = mesh_study.monitor_point_count(before_monitor)
    before_transcript_rows = len(transcript_residual_rows(solver, transcript))
    solver.settings.solution.run_calculation.iterate(iter_count=requested)
    after_monitor = mesh_study.monitor_snapshot(solver)
    after_points = mesh_study.monitor_point_count(after_monitor)
    after_transcript_rows = len(transcript_residual_rows(solver, transcript))
    monitor_advance = max(0, after_points - before_points)
    transcript_advance = max(0, after_transcript_rows - before_transcript_rows)
    proof = {
        "requested": requested,
        "monitor_points_before": before_points,
        "monitor_points_after": after_points,
        "monitor_advance": monitor_advance,
        "transcript_residual_rows_before": before_transcript_rows,
        "transcript_residual_rows_after": after_transcript_rows,
        "transcript_advance": transcript_advance,
        "accepted_proof": (
            "monitor-stream" if monitor_advance >= requested else "fluent-transcript"
        ),
    }
    if max(monitor_advance, transcript_advance) < requested:
        raise RuntimeError(
            "neither monitor stream nor Fluent transcript proved the full iteration "
            f"block: {proof}"
        )
    return proof, after_monitor


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    preparation = json.loads(PREPARATION_MANIFEST.read_text(encoding="utf-8"))
    if preparation.get("status") != "accepted":
        raise RuntimeError("setup-07g preparation is not accepted")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = LOCAL_ROOT / "qualification_manifest.json"
    resume_suffix = f"_resume_iter{args.resume_iterations}" if args.resume_iterations else ""
    transcript = remote_join(
        REMOTE_ROOT, f"{RUN_LABEL}_qualification{resume_suffix}.trn"
    )
    solver = connect(server_id="1")
    result: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "status": "running",
        "classification": "diagnostic",
        "prepared_checkpoint": preparation["prepared_checkpoint"],
        "resume_checkpoint": (
            {"case": args.resume_case, "data": args.resume_data}
            if args.resume_case and args.resume_data
            else None
        ),
        "target_iterations": TARGET_ITERATIONS,
        "iterations_completed": args.resume_iterations,
        "checkpoints": {"initialized": preparation["prepared_checkpoint"]},
        "iteration_blocks": [],
        "dpm": "off; no injections updated or tracked",
        "ewf": "off/not introduced",
        "sink_udf": "absent",
        "started_epoch": time.time(),
    }
    physical_rows: list[dict[str, Any]] = []
    write_json(manifest_path, result)
    try:
        if bool(args.resume_case) != bool(args.resume_data):
            raise ValueError("--resume-case and --resume-data must be supplied together")
        if not 0 <= args.resume_iterations < TARGET_ITERATIONS:
            raise ValueError("--resume-iterations must lie in [0, 3000)")
        checkpoint = (
            {"case": args.resume_case, "data": args.resume_data}
            if args.resume_case
            else preparation["prepared_checkpoint"]
        )
        if args.resume_iterations:
            result["checkpoints"][str(args.resume_iterations)] = checkpoint
        solver.settings.file.read_case(file_name=checkpoint["case"])
        solver.settings.file.read_data(file_name=checkpoint["data"])
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        errors, snapshot = validation_errors(solver, preparation)
        result["cold_reload_settings_readback"] = snapshot
        result["cold_reload_validation_errors"] = errors
        if errors:
            raise RuntimeError("cold-reload validation failed: " + "; ".join(errors))
        sweep.set_verified_iteration_label(solver, args.resume_iterations)

        sweep.configure_residual_history(solver, 5000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()
        completed = args.resume_iterations
        while completed < TARGET_ITERATIONS:
            requested = checkpoint_schedule(completed)
            started = time.time()
            proof, after = proven_iteration_block(solver, transcript, requested)
            completed += requested
            result["iterations_completed"] = completed
            result["iteration_blocks"].append(
                {
                    "end_iteration": completed,
                    "requested": requested,
                    "wall_seconds": time.time() - started,
                    "iteration_proof": proof,
                    "after_monitor": after,
                    "physical_metrics": None,
                }
            )
            write_json(manifest_path, result)
            metrics = physical_metrics(solver, completed)
            physical_rows.append(metrics)
            result["iteration_blocks"][-1]["physical_metrics"] = metrics
            if completed in CHECKPOINTS:
                result["checkpoints"][str(completed)] = save_pair(
                    solver, f"checkpoint_iter{completed}"
                )
            residual_rows = sweep.monitor_history_rows(solver)
            if not residual_rows:
                residual_rows = transcript_residual_rows(solver, transcript)
            sweep.write_monitor_history_csv(
                LOCAL_ROOT / "residual_history.csv", residual_rows
            )
            write_csv(LOCAL_ROOT / "physical_monitor_history.csv", physical_rows)
            write_json(manifest_path, result)

            if completed >= 250:
                if metrics["mixture_brineoutlet_kgs"] >= 0.0:
                    raise RuntimeError(
                        "brine outlet is not discharging after 250 iterations: "
                        f"{metrics['mixture_brineoutlet_kgs']} kg/s"
                    )
                if metrics["mixture_steamoutlet_kgs"] >= 0.0:
                    raise RuntimeError(
                        "steam outlet is not discharging after 250 iterations: "
                        f"{metrics['mixture_steamoutlet_kgs']} kg/s"
                    )
            print(
                f"07g: {completed}/{TARGET_ITERATIONS}; "
                f"brine={metrics['mixture_brineoutlet_kgs']:.6g} kg/s; "
                f"steam={metrics['mixture_steamoutlet_kgs']:.6g} kg/s; "
                f"mix imbalance={metrics['mixture_imbalance_percent']:.4g}%",
                flush=True,
            )

        primary_fields = [
            "pressure_drop_to_steamoutlet_pa",
            "pressure_drop_to_brineoutlet_pa",
            "vapor_steamoutlet_kgs",
            "liquid_brineoutlet_kgs",
        ]
        secondary_fields = [
            "steamoutlet_area_weighted_velocity_ms",
            "brineoutlet_area_weighted_velocity_ms",
            "domain_volume_avg_velocity_ms",
            "domain_volume_avg_vorticity_s-1",
            "domain_volume_avg_liquid_volume_fraction",
        ]
        stability = monitor_stability(
            physical_rows, primary_fields + secondary_fields, first_iteration=2500
        )
        final = physical_rows[-1]
        balance_pass = all(
            final[field] <= 0.5
            for field in (
                "mixture_imbalance_percent",
                "vapor_imbalance_percent",
                "liquid_imbalance_percent",
            )
        )
        primary_stable = all(
            stability[field]["drift_percent"] <= 0.5 for field in primary_fields
        )
        secondary_stable = all(
            stability[field]["drift_percent"] <= 1.0 for field in secondary_fields
        )
        directions_pass = (
            final["mixture_brineoutlet_kgs"] < 0.0
            and final["mixture_steamoutlet_kgs"] < 0.0
            and final["liquid_brineoutlet_kgs"] < 0.0
            and final["vapor_steamoutlet_kgs"] < 0.0
        )
        classification = (
            "accepted"
            if balance_pass and primary_stable and secondary_stable and directions_pass
            else "unresolved"
        )
        metrics_payload = {
            "study_id": STUDY_ID,
            "run_label": RUN_LABEL,
            "classification": classification,
            "scope": (
                "single-mesh carrier boundary qualification; not mesh convergence, "
                "DPM carryover validation, EWF validation, or separator validation"
            ),
            "mesh_metrics": preparation["mesh_metrics"],
            "final_metrics": final,
            "monitor_stability_2500_3000": stability,
            "acceptance": {
                "phase_and_mixture_balance_pass": balance_pass,
                "primary_monitor_stability_pass": primary_stable,
                "secondary_monitor_stability_pass": secondary_stable,
                "outlet_flow_directions_pass": directions_pass,
            },
        }
        write_json(LOCAL_ROOT / "qualification_metrics.json", metrics_payload)
        result.update(
            {
                "status": "completed",
                "classification": classification,
                "metrics": metrics_payload,
                "completed_epoch": time.time(),
            }
        )
        write_json(manifest_path, result)
        sweep.remote_text_write_best_effort(
            solver,
            remote_join(REMOTE_ROOT, f"{RUN_LABEL}_qualification_metrics.json"),
            json.dumps(metrics_payload, indent=2, default=str),
        )
        return 0
    except Exception as exc:
        result.update(
            {
                "status": "unresolved",
                "classification": "diagnostic",
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        if result.get("iterations_completed", 0):
            try:
                result["interrupt_checkpoint"] = save_pair(
                    solver, f"interrupt_iter{result['iterations_completed']}"
                )
            except Exception as save_exc:
                result["interrupt_checkpoint_error"] = (
                    f"{type(save_exc).__name__}: {save_exc}"
                )
        write_json(manifest_path, result)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
        if transcript_text:
            transcript_name = (
                f"qualification{resume_suffix}_transcript.trn"
                if resume_suffix
                else "qualification_transcript.trn"
            )
            (LOCAL_ROOT / transcript_name).write_text(
                transcript_text, encoding="utf-8"
            )


if __name__ == "__main__":
    raise SystemExit(main())
