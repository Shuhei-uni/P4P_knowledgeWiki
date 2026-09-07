#!/usr/bin/env python3
"""Run the bounded setup-07l closed-pool hydrostatic-rest isolation test.

The runner advances one 1e-6 s physical step per RPC from the accepted 07l
time-zero checkpoint.  Three steps are the default.  Each step is separately
checkpointed and checked for clock advancement, finite fields, VOF
boundedness, gross pressure/velocity growth, unintended boundary flow, and
any reappearance of DPM parcel tracking.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import require_live_compute_node_count  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import prepare_setup07l_hydrostatic_rest as prepare07l  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07g_brine_outlet_qualification as steady07g  # noqa: E402
import run_setup07j_transient_vof_qualification as transient07j  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = prepare07l.STUDY_ID
RUN_LABEL = prepare07l.RUN_LABEL
REMOTE_ROOT = prepare07l.REMOTE_ROOT
TIME_STEP_SIZE_S = prepare07l.TIME_STEP_SIZE_S
MAX_ITERATIONS_PER_TIME_STEP = prepare07l.MAX_ITERATIONS_PER_TIME_STEP
DEFAULT_TARGET_STEPS = 3
ZONES = ["liquidinlet", "steaminlet", "steamoutlet", "brineoutlet"]
LIQUID_DENSITY_KG_M3 = transient07j.LIQUID_DENSITY_KG_M3
VAPOR_DENSITY_KG_M3 = transient07j.VAPOR_DENSITY_KG_M3
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"


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


def read_csv(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as stream:
            raw_rows = list(csv.DictReader(stream))
    except OSError:
        return []
    rows: list[dict[str, Any]] = []
    for raw in raw_rows:
        row: dict[str, Any] = {}
        for key, value in raw.items():
            try:
                row[key] = float(value)
            except (TypeError, ValueError):
                row[key] = value
        rows.append(row)
    return rows


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
    from pyansys_fluent.mesh_convergence import parse_named_report_rows, parse_net_report_value

    values = parse_named_report_rows(text, ZONES)
    missing = [zone for zone in ZONES if zone not in values]
    if missing:
        raise RuntimeError(f"{domain} mass-flow report missing {missing}: {text}")
    values["Net"] = parse_net_report_value(text)
    return values


def physical_metrics(solver: Any, step: int) -> dict[str, Any]:
    mixture = mass_flows(solver, "mixture", f"07l_mixture_step{step}")
    vapor = mass_flows(solver, "phase-1", f"07l_vapor_step{step}")
    liquid = mass_flows(solver, "phase-2", f"07l_liquid_step{step}")
    inlet_pressure = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"07l_inlet_pressure_step{step}",
        ["liquidinlet", "steaminlet"],
        "pressure",
    )["Net"]
    steam_pressure = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"07l_steam_pressure_step{step}",
        ["steamoutlet"],
        "pressure",
    )["Net"]
    brine_pressure = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"07l_brine_wall_pressure_step{step}",
        ["brineoutlet"],
        "pressure",
    )["Net"]
    steam_velocity = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"07l_steam_velocity_step{step}",
        ["steamoutlet"],
        "velocity-magnitude",
    )["Net"]
    brine_velocity = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"07l_brine_wall_velocity_step{step}",
        ["brineoutlet"],
        "velocity-magnitude",
    )["Net"]
    result: dict[str, Any] = {
        "step": step,
        "inlet_area_weighted_pressure_pa": inlet_pressure,
        "steamoutlet_area_weighted_pressure_pa": steam_pressure,
        "brine_wall_area_weighted_pressure_pa": brine_pressure,
        "steamoutlet_area_weighted_velocity_ms": steam_velocity,
        "brine_wall_area_weighted_velocity_ms": brine_velocity,
        "domain_volume_avg_velocity_ms": steady07g.volume_average(
            solver, "velocity-magnitude", f"07l_velocity_step{step}"
        ),
        "domain_volume_avg_vorticity_s-1": steady07g.volume_average(
            solver, "vorticity-mag", f"07l_vorticity_step{step}"
        ),
        "domain_volume_avg_liquid_volume_fraction": steady07g.volume_average(
            solver, "phase-2-vof", f"07l_vf_step{step}"
        ),
    }
    for domain, values in (("mixture", mixture), ("vapor", vapor), ("liquid", liquid)):
        for zone in ZONES:
            result[f"{domain}_{zone}_kgs"] = values[zone]
        result[f"{domain}_net_kgs"] = values["Net"]
    return result


def inventory(metrics: Mapping[str, Any], domain_volume_m3: float) -> dict[str, float]:
    alpha = float(metrics["domain_volume_avg_liquid_volume_fraction"])
    return {
        "liquid_inventory_kg": alpha * domain_volume_m3 * LIQUID_DENSITY_KG_M3,
        "vapor_inventory_kg": (1.0 - alpha) * domain_volume_m3 * VAPOR_DENSITY_KG_M3,
    }


def rest_gate(row: Mapping[str, Any], previous: Mapping[str, Any] | None) -> list[str]:
    failures: list[str] = []
    for key, value in row.items():
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            failures.append(f"non-finite {key}={value}")
    alpha = float(row["domain_volume_avg_liquid_volume_fraction"])
    if not -1.0e-8 <= alpha <= 1.0 + 1.0e-8:
        failures.append(f"liquid volume fraction outside [0,1]: {alpha}")

    # Walls and zero-flow inlets must not carry appreciable mass.  Fluent's
    # surface report can contain round-off-scale values, hence the 1e-6 gate.
    for domain in ("mixture", "vapor", "liquid"):
        for zone in ("liquidinlet", "steaminlet", "brineoutlet"):
            key = f"{domain}_{zone}_kgs"
            if abs(float(row[key])) > 1.0e-6:
                failures.append(f"unintended closed-boundary flux {key}={row[key]}")

    # This is a startup isolation test, so these are gross-safety gates rather
    # than convergence criteria.  Values below the gates are still reported.
    for key in (
        "inlet_area_weighted_pressure_pa",
        "steamoutlet_area_weighted_pressure_pa",
        "brine_wall_area_weighted_pressure_pa",
    ):
        if abs(float(row[key])) > 1.0e7:
            failures.append(f"gross pressure response {key}={row[key]} exceeds 1e7 Pa")
    if abs(float(row["domain_volume_avg_velocity_ms"])) > 20.0:
        failures.append(
            "gross domain velocity "
            f"{row['domain_volume_avg_velocity_ms']} exceeds 20 m/s"
        )
    if abs(float(row["steamoutlet_area_weighted_velocity_ms"])) > 50.0:
        failures.append(
            "gross steam-outlet velocity "
            f"{row['steamoutlet_area_weighted_velocity_ms']} exceeds 50 m/s"
        )
    if abs(float(row["mixture_steamoutlet_kgs"])) > 100.0:
        failures.append(
            f"gross rest-state steam-outlet flux {row['mixture_steamoutlet_kgs']} exceeds 100 kg/s"
        )
    if previous is not None:
        change = abs(
            float(row["liquid_inventory_kg"])
            - float(previous["liquid_inventory_kg"])
        )
        if change > 0.01:
            failures.append(f"liquid inventory changed {change} kg in one 1e-6 s step")
    return failures


def parse_global_courant(text: str) -> list[float]:
    pattern = re.compile(
        rf"Global Courant Number(?:\s*\[[^\]]+\])?\s*[:=]\s*({NUMBER})",
        re.IGNORECASE,
    )
    return [float(value) for value in pattern.findall(text)]


def dpm_tracking_evidence(text: str) -> list[str]:
    evidence = []
    patterns = (
        r"Injecting\s+\d+\s+particle parcels",
        r"Advancing DPM injections",
        r"number tracked\s*=\s*\d+",
    )
    for pattern in patterns:
        evidence.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    return evidence


def save_pair(solver: Any, step: int, run_label: str) -> dict[str, str]:
    case = prepare07l.source07j.remote_join(
        REMOTE_ROOT, f"{run_label}_checkpoint_step{step}.cas.h5"
    )
    data = prepare07l.source07j.remote_join(
        REMOTE_ROOT, f"{run_label}_checkpoint_step{step}.dat.h5"
    )
    sweep.write_case_data_pair(solver, case, data, f"07l_checkpoint_step{step}")
    return {"case": case, "data": data}


def validate_cold_reload(solver: Any, preparation: Mapping[str, Any]) -> dict[str, Any]:
    snapshot = mesh_study.capture_settings(solver, REMOTE_ROOT)
    snapshot.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT))
    errors = prepare07l.validate_snapshot(snapshot, preparation["mesh_metrics"])
    dpm = solver.settings.setup.models.discrete_phase
    injection_names = list(dpm.injections.get_object_names())
    interaction = dpm.general_settings.interaction.get_state()
    unsteady = dpm.general_settings.unsteady_tracking.get_state()
    if injection_names:
        errors.append(f"DPM injection objects present: {injection_names}")
    if bool(interaction.get("enabled")):
        errors.append(f"DPM interaction enabled: {interaction}")
    if bool(unsteady.get("enabled")):
        errors.append(f"DPM unsteady tracking enabled: {unsteady}")
    controls = solver.settings.solution.run_calculation.transient_controls.get_state()
    actual_dt = prepare07l.nested(controls, "time_step_size")
    if actual_dt is None or not math.isclose(
        float(actual_dt), TIME_STEP_SIZE_S, rel_tol=0.0, abs_tol=1.0e-14
    ):
        errors.append(f"time-step readback mismatch: {controls}")
    if errors:
        raise RuntimeError("cold-reload validation failed: " + "; ".join(errors))
    return {
        "settings": snapshot,
        "dpm_injection_names": injection_names,
        "dpm_interaction": interaction,
        "dpm_unsteady_tracking": unsteady,
        "transient_controls": controls,
        "operating_conditions": solver.settings.setup.general.operating_conditions.get_state(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    parser.add_argument("--target-steps", type=int, default=DEFAULT_TARGET_STEPS)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume only from the latest separately saved numeric checkpoint.",
    )
    args = parser.parse_args()
    if args.target_steps < 1 or args.target_steps > 10:
        raise ValueError("--target-steps must be between 1 and 10")
    load_dotenv(PROJECT_ROOT / ".env", override=True)

    run_label = prepare07l.run_label_for_server(args.server_id)
    local_root = prepare07l.local_root_for_server(args.server_id)
    preparation_path = local_root / "preparation_manifest.json"
    preparation = json.loads(preparation_path.read_text(encoding="utf-8"))
    if preparation.get("status") != "accepted":
        raise RuntimeError("setup-07l preparation is not accepted")
    if str(preparation.get("server_id")) != args.server_id:
        raise RuntimeError("setup-07l preparation belongs to another server")

    manifest_path = local_root / "qualification_manifest.json"
    start_completed = 0
    rows: list[dict[str, Any]] = []
    if args.resume:
        result = json.loads(manifest_path.read_text(encoding="utf-8"))
        if str(result.get("server_id")) != args.server_id:
            raise RuntimeError("qualification manifest belongs to another server")
        numeric = sorted(
            int(key)
            for key, pair in result.get("checkpoints", {}).items()
            if str(key).isdigit()
            and isinstance(pair, Mapping)
            and pair.get("case")
            and pair.get("data")
        )
        if not numeric:
            raise RuntimeError("no numeric checkpoint is available to resume")
        start_completed = max(numeric)
        if start_completed >= args.target_steps:
            raise RuntimeError(
                f"latest checkpoint {start_completed} already meets target {args.target_steps}"
            )
        result.setdefault("attempt_history", []).append(
            {
                "status": result.get("status"),
                "classification": result.get("classification"),
                "time_steps_completed": result.get("time_steps_completed"),
                "completed_epoch": result.get("completed_epoch"),
            }
        )
        result.update(
            {
                "status": "running",
                "classification": "diagnostic / hydrostatic-rest isolation / resumed",
                "target_time_steps": args.target_steps,
                "target_flow_time_s": args.target_steps * TIME_STEP_SIZE_S,
                "resumed_from_step": start_completed,
                "resume_started_epoch": time.time(),
            }
        )
        result.pop("completed_epoch", None)
        result.pop("error", None)
        rows = [
            row
            for row in read_csv(local_root / "transient_physical_history.csv")
            if int(float(row.get("step", -1))) <= start_completed
        ]
        checkpoint = result["checkpoints"][str(start_completed)]
        transcript_name = f"{run_label}_qualification_resume_step{start_completed}.trn"
        local_transcript_name = f"qualification_transcript_resume_step{start_completed}.trn"
    else:
        result = {
            "study_id": STUDY_ID,
            "run_label": run_label,
            "server_id": args.server_id,
            "status": "running",
            "classification": "diagnostic / hydrostatic-rest isolation",
            "target_time_steps": args.target_steps,
            "time_step_size_s": TIME_STEP_SIZE_S,
            "target_flow_time_s": args.target_steps * TIME_STEP_SIZE_S,
            "time_steps_completed": 0,
            "checkpoints": {"time_zero": preparation["prepared_checkpoint"]},
            "blocks": [],
            "attempt_history": [],
            "dpm_contract": "zero injections, unsteady tracking off, interaction off",
            "started_epoch": time.time(),
        }
        checkpoint = preparation["prepared_checkpoint"]
        transcript_name = f"{run_label}_qualification.trn"
        local_transcript_name = "qualification_transcript.trn"
    write_json(manifest_path, result)
    solver = connect(server_id=args.server_id, start_transcript=True)
    transcript = prepare07l.source07j.remote_join(
        REMOTE_ROOT, transcript_name
    )
    transcript_started = False
    transcript_text = ""
    try:
        result["live_parallel_runtime"] = require_live_compute_node_count(
            solver, prepare07l.EXPECTED_COMPUTE_NODES
        )
        solver.transcript.stop()
        solver.settings.file.read_case(file_name=checkpoint["case"])
        solver.settings.file.read_data(file_name=checkpoint["data"])
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        transcript_started = True
        result["cold_reload_readback"] = validate_cold_reload(solver, preparation)
        controls = solver.settings.solution.run_calculation.transient_controls
        controls.time_step_size.set_state(TIME_STEP_SIZE_S)
        controls.max_iter_per_time_step.set_state(MAX_ITERATIONS_PER_TIME_STEP)
        domain_volume = float(preparation["mesh_metrics"]["domain_volume_m3"])
        initial_clock = transient07j.runtime_clock(solver)
        result["initial_clock"] = initial_clock
        previous: dict[str, Any] | None = rows[-1] if rows else None

        for completed in range(start_completed + 1, args.target_steps + 1):
            started = time.time()
            solver.settings.solution.run_calculation.dual_time_iterate(
                time_step_count=1,
                max_iter_per_step=MAX_ITERATIONS_PER_TIME_STEP,
            )
            clock = transient07j.runtime_clock(solver)
            session_steps = completed - start_completed
            expected_step = int(initial_clock["time_step"]) + session_steps
            expected_time = (
                float(initial_clock["flow_time_s"])
                + session_steps * TIME_STEP_SIZE_S
            )
            if int(clock["time_step"]) != expected_step:
                raise RuntimeError(
                    f"time-step proof failed: expected={expected_step}, actual={clock}"
                )
            if not math.isclose(
                float(clock["flow_time_s"]),
                expected_time,
                rel_tol=0.0,
                abs_tol=max(1.0e-12, TIME_STEP_SIZE_S * 1.0e-6),
            ):
                raise RuntimeError(
                    f"flow-time proof failed: expected={expected_time}, actual={clock}"
                )

            metrics = physical_metrics(solver, completed)
            row = {**metrics, **clock, **inventory(metrics, domain_volume)}
            failures = rest_gate(row, previous)
            transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
            parcel_evidence = dpm_tracking_evidence(transcript_text)
            if parcel_evidence:
                failures.append(f"DPM tracking reappeared: {parcel_evidence}")
            courant_values = parse_global_courant(transcript_text)
            row["latest_global_courant"] = (
                courant_values[-1] if courant_values else math.nan
            )
            rows.append(row)
            checkpoint = save_pair(solver, completed, run_label)
            result["checkpoints"][str(completed)] = checkpoint
            result["time_steps_completed"] = completed
            result["last_heartbeat_epoch"] = time.time()
            result["blocks"].append(
                {
                    "end_step": completed,
                    "end_flow_time_s": clock["flow_time_s"],
                    "wall_seconds": time.time() - started,
                    "metrics": row,
                    "gate_failures": failures,
                    "dpm_tracking_evidence": parcel_evidence,
                    "global_courant_values_seen": courant_values,
                }
            )
            write_csv(local_root / "transient_physical_history.csv", rows)
            write_json(manifest_path, result)
            if failures:
                raise RuntimeError("hydrostatic-rest gate failed: " + "; ".join(failures))
            print(
                f"07l: step {completed}/{args.target_steps}; "
                f"t={clock['flow_time_s']:.6g} s; "
                f"Udom={row['domain_volume_avg_velocity_ms']:.6g} m/s; "
                f"alpha_l={row['domain_volume_avg_liquid_volume_fraction']:.6g}; "
                f"Co={row['latest_global_courant']}",
                flush=True,
            )
            previous = row

        residual_rows = sweep.monitor_history_rows(solver)
        if residual_rows:
            sweep.write_monitor_history_csv(local_root / "residual_history.csv", residual_rows)
        result.update(
            {
                "status": "completed",
                "classification": "diagnostic / bounded hydrostatic-rest startup",
                "acceptance_limitation": (
                    "This proves only bounded closed-pool relaxation over the recorded "
                    "microseconds; it does not validate the brine-outlet production boundary."
                ),
                "global_courant_values": parse_global_courant(transcript_text),
                "dpm_tracking_evidence": dpm_tracking_evidence(transcript_text),
                "completed_epoch": time.time(),
            }
        )
        write_json(manifest_path, result)
        return 0
    except (Exception, KeyboardInterrupt) as exc:
        result.update(
            {
                "status": "failed",
                "classification": "diagnostic / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(manifest_path, result)
        raise
    finally:
        if transcript_started:
            try:
                solver.settings.file.stop_transcript()
                transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
                if transcript_text:
                    (local_root / local_transcript_name).write_text(
                        transcript_text, encoding="utf-8"
                    )
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
