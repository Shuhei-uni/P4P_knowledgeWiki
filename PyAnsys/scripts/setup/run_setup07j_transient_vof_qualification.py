#!/usr/bin/env python3
"""Run a guarded transient-VOF startup qualification for setup 07j.

The driver cold-loads only the accepted time-zero checkpoint, proves physical
time advancement, samples complete phase/mixture boundary fluxes and liquid
inventory, and saves non-overwriting case/data checkpoints.  It aborts on a
gross drainage, non-finite, or boundedness failure.  DPM, EWF, and the
historical sink UDF remain absent throughout.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import require_live_compute_node_count  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import prepare_setup07j_transient_vof as prepare07j  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07g_brine_outlet_qualification as steady07g  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = prepare07j.STUDY_ID
RUN_LABEL = prepare07j.RUN_LABEL
REMOTE_ROOT = prepare07j.REMOTE_ROOT
LOCAL_ROOT = prepare07j.LOCAL_ROOT
PREPARATION_MANIFEST = LOCAL_ROOT / "preparation_manifest.json"
TIME_STEP_SIZE_S = prepare07j.TIME_STEP_SIZE_S
MAX_ITERATIONS_PER_TIME_STEP = prepare07j.MAX_ITERATIONS_PER_TIME_STEP
LIQUID_DENSITY_KG_M3 = 881.2108764648438
VAPOR_DENSITY_KG_M3 = 5.797433853149414
LIQUID_FEED_KG_S = 116.92
VAPOR_FEED_KG_S = 80.69
DEFAULT_TARGET_STEPS = 1000
CHECKPOINT_STEPS = {1, 10, 50, 100, 500, 1000}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--target-steps", type=int, default=DEFAULT_TARGET_STEPS)
    result.add_argument(
        "--server-id",
        choices=("1", "2", "3"),
        default="1",
        help="Configured Fluent server from .env; must match the preparation run.",
    )
    result.add_argument(
        "--resume",
        action="store_true",
        help=(
            "Resume from the latest saved checkpoint in this server's qualification "
            "manifest. Intended only after a connection-class failure."
        ),
    )
    return result


def remote_join(directory: str, name: str) -> str:
    return str(PureWindowsPath(directory) / name)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        return
    fields = sorted({str(key) for row in rows for key in row})
    path.parent.mkdir(parents=True, exist_ok=True)
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


def latest_checkpoint_step(result: Mapping[str, Any], target_steps: int) -> int:
    candidates: list[int] = []
    for label, pair in (result.get("checkpoints") or {}).items():
        try:
            step = int(label)
        except (TypeError, ValueError):
            continue
        if (
            0 < step <= target_steps
            and isinstance(pair, Mapping)
            and pair.get("case")
            and pair.get("data")
        ):
            candidates.append(step)
    if not candidates:
        raise RuntimeError("no saved qualification checkpoint is available to resume")
    return max(candidates)


def runtime_clock(solver: Any) -> dict[str, float | int]:
    flow_time = float(solver.scheme.eval("(rpgetvar 'flow-time)"))
    time_step = int(solver.scheme.eval("(rpgetvar 'time-step)"))
    physical_dt = float(solver.scheme.eval("(rpgetvar 'physical-time-step)"))
    return {
        "flow_time_s": flow_time,
        "time_step": time_step,
        "physical_time_step_s": physical_dt,
    }


def phase_inventory(
    liquid_volume_fraction: float, domain_volume_m3: float
) -> dict[str, float]:
    return {
        "liquid_inventory_kg": (
            liquid_volume_fraction * domain_volume_m3 * LIQUID_DENSITY_KG_M3
        ),
        "vapor_inventory_kg": (
            (1.0 - liquid_volume_fraction) * domain_volume_m3 * VAPOR_DENSITY_KG_M3
        ),
    }


def inventory_snapshot(solver: Any, domain_volume_m3: float, label: str) -> dict[str, Any]:
    liquid_vf = steady07g.volume_average(solver, "phase-2-vof", f"vf_{label}")
    liquid = steady07g.mass_flows(solver, "phase-2", f"liquid_{label}")
    vapor = steady07g.mass_flows(solver, "phase-1", f"vapor_{label}")
    mixture = steady07g.mass_flows(solver, "mixture", f"mixture_{label}")
    return {
        **runtime_clock(solver),
        "domain_volume_avg_liquid_volume_fraction": liquid_vf,
        **phase_inventory(liquid_vf, domain_volume_m3),
        "liquid_net_boundary_flux_kg_s": liquid["Net"],
        "vapor_net_boundary_flux_kg_s": vapor["Net"],
        "mixture_net_boundary_flux_kg_s": mixture["Net"],
    }


def storage_closure(previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, Any]:
    elapsed = float(current["flow_time_s"]) - float(previous["flow_time_s"])
    if elapsed <= 0.0:
        raise RuntimeError(f"physical time did not advance: previous={previous}, current={current}")
    result: dict[str, Any] = {"elapsed_physical_time_s": elapsed}
    for phase, feed in (("liquid", LIQUID_FEED_KG_S), ("vapor", VAPOR_FEED_KG_S)):
        storage_rate = (
            float(current[f"{phase}_inventory_kg"])
            - float(previous[f"{phase}_inventory_kg"])
        ) / elapsed
        average_boundary_flux = 0.5 * (
            float(previous[f"{phase}_net_boundary_flux_kg_s"])
            + float(current[f"{phase}_net_boundary_flux_kg_s"])
        )
        residual = storage_rate - average_boundary_flux
        result.update(
            {
                f"{phase}_storage_rate_kg_s": storage_rate,
                f"{phase}_trapezoidal_boundary_flux_kg_s": average_boundary_flux,
                f"{phase}_storage_closure_residual_kg_s": residual,
                f"{phase}_storage_closure_percent_of_feed": abs(residual) / feed * 100.0,
            }
        )
    result["method"] = (
        "inventory finite difference minus trapezoidal endpoint boundary flux; "
        "diagnostic approximation, not a per-time-step integrated flux"
    )
    return result


def gross_gate(metrics: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    zero_flow_ratios = {
        "steamoutlet_quality_percent": "mixture_steamoutlet_kgs",
        "brineoutlet_liquid_fraction_percent": "mixture_brineoutlet_kgs",
    }
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            denominator = zero_flow_ratios.get(key)
            if denominator is not None and math.isclose(
                float(metrics[denominator]), 0.0, rel_tol=0.0, abs_tol=1.0e-12
            ):
                # Composition is undefined at an outlet with exactly zero mass
                # flow. The underlying phase and mixture fluxes remain subject
                # to the finite and gross-flow gates below.
                continue
            failures.append(f"non-finite {key}={value}")
    vf = float(metrics["domain_volume_avg_liquid_volume_fraction"])
    if not -1.0e-8 <= vf <= 1.0 + 1.0e-8:
        failures.append(f"liquid volume fraction outside [0,1]: {vf}")
    limits = {
        "liquid_brineoutlet_kgs": 5.0 * LIQUID_FEED_KG_S,
        "liquid_steamoutlet_kgs": 5.0 * LIQUID_FEED_KG_S,
        "vapor_brineoutlet_kgs": 5.0 * VAPOR_FEED_KG_S,
        "vapor_steamoutlet_kgs": 5.0 * VAPOR_FEED_KG_S,
    }
    for key, limit in limits.items():
        if abs(float(metrics[key])) > limit:
            failures.append(f"gross boundary flux {key}={metrics[key]} exceeds {limit}")
    # Fail closed on unmistakable pressure/velocity blow-up even when imposed
    # mass-flow boundaries still report their commanded finite values.
    for key in (
        "inlet_mass_weighted_pressure_pa",
        "steamoutlet_mass_weighted_pressure_pa",
        "brineoutlet_mass_weighted_pressure_pa",
        "pressure_drop_to_steamoutlet_pa",
        "pressure_drop_to_brineoutlet_pa",
    ):
        if key in metrics and abs(float(metrics[key])) > 1.0e8:
            failures.append(f"gross pressure field {key}={metrics[key]} exceeds 1e8 Pa")
    for key in (
        "steamoutlet_area_weighted_velocity_ms",
        "brineoutlet_area_weighted_velocity_ms",
        "domain_volume_avg_velocity_ms",
    ):
        if key in metrics and abs(float(metrics[key])) > 1.0e4:
            failures.append(f"gross velocity field {key}={metrics[key]} exceeds 1e4 m/s")
    return failures


def next_block(completed: int, target: int) -> int:
    # Advance one physical time step per RPC.  Fluent 2024 R2 can return early
    # from a multi-step dual_time_iterate request when an internal stop
    # condition is met.  Single-step calls make the runtime clock proof exact,
    # provide a durable heartbeat after every step, and bound an interrupted
    # remote solve to one uncredited step.
    return min(1, target - completed)


def save_pair(
    solver: Any, step: int, *, run_label: str = RUN_LABEL, remote_root: str = REMOTE_ROOT
) -> dict[str, str]:
    label = f"checkpoint_step{step}_t{step * TIME_STEP_SIZE_S:.4f}s".replace(".", "p")
    case = remote_join(remote_root, f"{run_label}_{label}.cas.h5")
    data = remote_join(remote_root, f"{run_label}_{label}.dat.h5")
    sweep.write_case_data_pair(solver, case, data, f"07j_{label}")
    return {"case": case, "data": data}


def validate_cold_reload(
    solver: Any, preparation: Mapping[str, Any], *, remote_root: str = REMOTE_ROOT
) -> dict[str, Any]:
    snapshot = mesh_study.capture_settings(solver, remote_root)
    snapshot.update(mesh_study.verify_initialized_phase_identity(solver, remote_root))
    errors = prepare07j.validate_snapshot(snapshot, preparation["mesh_metrics"])
    methods = solver.settings.solution.methods
    controls = solver.settings.solution.run_calculation.transient_controls
    readback = {
        "settings": snapshot,
        "volume_fraction_scheme": methods.discretization_scheme["mp"].get_state(),
        "pressure_velocity_coupling": methods.p_v_coupling.flow_scheme.get_state(),
        "transient_formulation": methods.transient_formulation.get_state(),
        "warped_face_gradient_correction": methods.warped_face_gradient_correction.get_state(),
        "transient_controls": controls.get_state(),
    }
    expected = {
        "volume_fraction_scheme": "geo-reconstruct",
        "pressure_velocity_coupling": "PISO",
        "transient_formulation": preparation["transient_method_readback"][
            "transient_formulation"
        ],
    }
    for key, value in expected.items():
        if readback[key] != value:
            errors.append(f"{key} expected={value!r} actual={readback[key]!r}")
    wfgc = readback["warped_face_gradient_correction"]
    if not bool(wfgc.get("enable")):
        errors.append(f"WFGC expected enabled actual={wfgc}")
    if errors:
        raise RuntimeError("cold-reload validation failed: " + "; ".join(errors))
    return readback


def main() -> int:
    args = parser().parse_args()
    if args.target_steps < 1:
        raise ValueError("--target-steps must be positive")
    load_dotenv(PROJECT_ROOT / ".env")
    run_label = prepare07j.run_label_for_server(args.server_id)
    local_root = prepare07j.local_root_for_server(args.server_id)
    preparation_manifest = local_root / "preparation_manifest.json"
    preparation = json.loads(preparation_manifest.read_text(encoding="utf-8"))
    if preparation.get("status") != "accepted":
        raise RuntimeError("setup-07j preparation is not accepted")
    prepared_server_id = str(preparation.get("server_id", "1"))
    if prepared_server_id != args.server_id:
        raise RuntimeError(
            "setup-07j preparation server mismatch: "
            f"requested={args.server_id}, prepared={prepared_server_id}"
        )
    if preparation.get("run_label") != run_label:
        raise RuntimeError(
            "setup-07j preparation namespace mismatch: "
            f"expected={run_label!r}, actual={preparation.get('run_label')!r}"
        )

    manifest_path = local_root / "qualification_manifest.json"
    attempt_epoch = int(time.time())
    resume_step = 0
    rows: list[dict[str, Any]] = []
    if args.resume:
        result = json.loads(manifest_path.read_text(encoding="utf-8"))
        if str(result.get("server_id", "1")) != args.server_id:
            raise RuntimeError("qualification manifest belongs to a different server")
        if result.get("run_label") != run_label:
            raise RuntimeError("qualification manifest belongs to a different run namespace")
        resume_step = latest_checkpoint_step(result, args.target_steps)
        prior_attempt = {
            "status": result.get("status"),
            "classification": result.get("classification"),
            "time_steps_completed": result.get("time_steps_completed", 0),
            "error": result.get("error"),
            "failed_epoch": result.get("failed_epoch"),
        }
        result.setdefault("attempt_history", []).append(prior_attempt)
        result["blocks"] = [
            block
            for block in result.get("blocks", [])
            if int(block.get("end_step", -1)) <= resume_step
        ]
        rows = [
            row
            for row in read_csv(local_root / "transient_physical_history.csv")
            if int(float(row.get("time_step", -1))) <= resume_step
        ]
        result.update(
            {
                "status": "running",
                "classification": "diagnostic transient startup / resumed",
                "target_time_steps": args.target_steps,
                "target_flow_time_s": args.target_steps * TIME_STEP_SIZE_S,
                "time_steps_completed": resume_step,
                "resumed_from_step": resume_step,
                "resume_started_epoch": time.time(),
            }
        )
        result.pop("error", None)
        result.pop("failed_epoch", None)
        checkpoint = result["checkpoints"][str(resume_step)]
        transcript_name = f"{run_label}_qualification_resume_step{resume_step}_{attempt_epoch}.trn"
        local_transcript_name = f"qualification_transcript_resume_step{resume_step}_{attempt_epoch}.trn"
    else:
        result = {
            "study_id": STUDY_ID,
            "run_label": run_label,
            "server_id": args.server_id,
            "status": "running",
            "classification": "diagnostic transient startup",
            "target_time_steps": args.target_steps,
            "target_flow_time_s": args.target_steps * TIME_STEP_SIZE_S,
            "time_steps_completed": 0,
            "time_step_size_s": TIME_STEP_SIZE_S,
            "max_iterations_per_time_step": MAX_ITERATIONS_PER_TIME_STEP,
            "checkpoints": {"time_zero": preparation["prepared_checkpoint"]},
            "blocks": [],
            "attempt_history": [],
            "dpm": "off; no injections updated or tracked",
            "ewf": "off/not introduced",
            "sink_udf": "absent",
            "started_epoch": time.time(),
        }
        checkpoint = preparation["prepared_checkpoint"]
        transcript_name = f"{run_label}_qualification.trn"
        local_transcript_name = "qualification_transcript.trn"
    transcript = remote_join(REMOTE_ROOT, transcript_name)
    result["last_heartbeat_epoch"] = time.time()
    write_json(manifest_path, result)
    # Keep the client transcript stream active for the guarded solve. Besides
    # proving the required 16-rank roster, this provides inner-iteration
    # liveness to run_guarded and avoids relying on a silent long-lived RPC.
    solver = connect(server_id=args.server_id, start_transcript=True)
    transcript_started = False
    try:
        result["live_parallel_runtime"] = require_live_compute_node_count(
            solver, prepare07j.EXPECTED_COMPUTE_NODES
        )
        result["client_transcript_stream"] = (
            "active through qualification for residual/liveness evidence"
        )
        solver.settings.file.read_case(file_name=checkpoint["case"])
        solver.settings.file.read_data(file_name=checkpoint["data"])
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        transcript_started = True
        result["cold_reload_readback"] = validate_cold_reload(
            solver, preparation, remote_root=REMOTE_ROOT
        )
        controls = solver.settings.solution.run_calculation.transient_controls
        controls.time_step_size.set_state(TIME_STEP_SIZE_S)
        controls.max_iter_per_time_step.set_state(MAX_ITERATIONS_PER_TIME_STEP)
        domain_volume = float(preparation["mesh_metrics"]["domain_volume_m3"])
        previous = inventory_snapshot(solver, domain_volume, f"step{resume_step}")
        if resume_step:
            result["resume_inventory"] = previous
        else:
            result["time_zero_inventory"] = previous
        initial_step = int(previous["time_step"])
        initial_flow_time = float(previous["flow_time_s"])

        completed = resume_step
        session_steps_completed = 0
        while completed < args.target_steps:
            requested = next_block(completed, args.target_steps)
            started = time.time()
            solver.settings.solution.run_calculation.dual_time_iterate(
                time_step_count=requested,
                max_iter_per_step=MAX_ITERATIONS_PER_TIME_STEP,
            )
            completed += requested
            session_steps_completed += requested
            current_clock = runtime_clock(solver)
            expected_step = initial_step + session_steps_completed
            expected_time = initial_flow_time + session_steps_completed * TIME_STEP_SIZE_S
            if int(current_clock["time_step"]) != expected_step:
                raise RuntimeError(
                    f"time-step proof failed: expected={expected_step}, actual={current_clock}"
                )
            if not math.isclose(
                float(current_clock["flow_time_s"]),
                expected_time,
                rel_tol=0.0,
                abs_tol=max(1.0e-12, TIME_STEP_SIZE_S * 1.0e-6),
            ):
                raise RuntimeError(
                    f"flow-time proof failed: expected={expected_time}, actual={current_clock}"
                )

            metrics = steady07g.physical_metrics(solver, completed)
            inventory = phase_inventory(
                float(metrics["domain_volume_avg_liquid_volume_fraction"]), domain_volume
            )
            current = {
                **current_clock,
                "domain_volume_avg_liquid_volume_fraction": metrics[
                    "domain_volume_avg_liquid_volume_fraction"
                ],
                **inventory,
                "liquid_net_boundary_flux_kg_s": metrics["liquid_net_kgs"],
                "vapor_net_boundary_flux_kg_s": metrics["vapor_net_kgs"],
                "mixture_net_boundary_flux_kg_s": metrics["mixture_net_kgs"],
            }
            closure = storage_closure(previous, current)
            row = {**metrics, **current_clock, **inventory, **closure}
            failures = gross_gate(row)
            rows.append(row)
            result["time_steps_completed"] = completed
            result["last_heartbeat_epoch"] = time.time()
            result["blocks"].append(
                {
                    "end_step": completed,
                    "end_flow_time_s": current_clock["flow_time_s"],
                    "requested_steps": requested,
                    "wall_seconds": time.time() - started,
                    "metrics": row,
                    "gross_gate_failures": failures,
                }
            )
            if completed in CHECKPOINT_STEPS or completed == args.target_steps:
                result["checkpoints"][str(completed)] = save_pair(
                    solver, completed, run_label=run_label, remote_root=REMOTE_ROOT
                )
            write_csv(local_root / "transient_physical_history.csv", rows)
            write_json(manifest_path, result)
            if failures:
                raise RuntimeError("gross transient startup gate failed: " + "; ".join(failures))
            print(
                f"07j: step {completed}/{args.target_steps}; "
                f"t={current_clock['flow_time_s']:.6g} s; "
                f"brine={metrics['mixture_brineoutlet_kgs']:.6g} kg/s; "
                f"steam={metrics['mixture_steamoutlet_kgs']:.6g} kg/s; "
                f"alpha_l={metrics['domain_volume_avg_liquid_volume_fraction']:.6g}",
                flush=True,
            )
            previous = current

        residual_rows = sweep.monitor_history_rows(solver)
        if residual_rows:
            sweep.write_monitor_history_csv(local_root / "residual_history.csv", residual_rows)
        result.update(
            {
                "status": "completed",
                "classification": "diagnostic / bounded transient startup",
                "acceptance_limitation": (
                    "Equal 1.12 MPa outlet pressures are an initial bracket; downstream "
                    "brine pressure and physical level closure remain unresolved."
                ),
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
                text = sweep.remote_text_read_best_effort(solver, transcript)
                if text:
                    (local_root / local_transcript_name).write_text(
                        text, encoding="utf-8"
                    )
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
