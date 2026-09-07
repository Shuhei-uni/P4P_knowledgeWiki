#!/usr/bin/env python3
"""Queue and run a carrier-only iteration extension for one mesh-study case.

The formal mesh study remains capped at 3000 iterations.  This script waits for
that formal controller when requested, loads its final case/data checkpoint,
and continues the same solution without initialization.  Extension results are
stored separately and are diagnostic evidence for iteration independence; they
do not replace the formal mesh-convergence result.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Mapping

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as study  # noqa: E402
import resume_split_inlet_mesh_convergence as resume  # noqa: E402


DEFAULT_MESH = "mesh-2300k"
DEFAULT_START = 3000
DEFAULT_TARGET = 6000
DEFAULT_CHECKPOINT_INTERVAL = 1000
PRIMARY_FIELDS = (
    "pressure_drop_pa",
    "vapor_steamoutlet_kgs",
    "liquid_steamoutlet_kgs",
    "carrier_outlet_quality_percent_trend_only",
)
SECONDARY_FIELDS = (
    "outlet_area_weighted_velocity_ms",
    "domain_volume_avg_velocity_ms",
    "domain_volume_avg_vorticity_s-1",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--mesh-name", default=DEFAULT_MESH, choices=study.MESH_NAMES)
    parser.add_argument("--starting-iterations", type=int, default=DEFAULT_START)
    parser.add_argument("--target-iterations", type=int, default=DEFAULT_TARGET)
    parser.add_argument("--checkpoint-interval", type=int, default=DEFAULT_CHECKPOINT_INTERVAL)
    parser.add_argument(
        "--run-label",
        default="extension",
        help="Filename/directory label used to keep retries separate (letters, digits, '_' or '-').",
    )
    parser.add_argument(
        "--resume-case",
        default=None,
        help="Final formal case checkpoint; inferred from the mesh and start iteration.",
    )
    parser.add_argument(
        "--resume-data",
        default=None,
        help="Final formal data checkpoint; inferred from the mesh and start iteration.",
    )
    parser.add_argument(
        "--wait-for-pid",
        type=int,
        default=None,
        help="Wait for this formal controller PID before connecting to Fluent.",
    )
    parser.add_argument("--wait-timeout-hours", type=float, default=48.0)
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    parser.add_argument(
        "--connect-retry-hours",
        type=float,
        default=0.0,
        help="Keep the run queued for this long while the Fluent endpoint is unavailable.",
    )
    parser.add_argument("--connect-retry-seconds", type=float, default=60.0)
    return parser


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def formal_manifest(mesh_name: str) -> Path:
    local_dir = study.LOCAL_ROOT / mesh_name.replace("-", "_")
    return local_dir / f"{mesh_name}_run_manifest.json"


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def wait_for_formal_controller(
    pid: int,
    mesh_name: str,
    starting_iterations: int,
    timeout_hours: float,
    poll_seconds: float,
    queue_manifest_path: Path,
    queue_manifest: dict[str, Any],
) -> None:
    deadline = time.monotonic() + timeout_hours * 3600.0
    print(f"extension queued behind formal controller PID {pid}", flush=True)
    while process_exists(pid):
        if time.monotonic() >= deadline:
            raise TimeoutError(f"formal controller PID {pid} exceeded queue timeout")
        payload = read_json(formal_manifest(mesh_name))
        queue_manifest["formal_iterations_observed"] = int(
            payload.get("iterations_completed") or 0
        )
        queue_manifest["queue_heartbeat_epoch"] = time.time()
        study.write_json(queue_manifest_path, queue_manifest)
        time.sleep(max(5.0, poll_seconds))

    payload = read_json(formal_manifest(mesh_name))
    if payload.get("status") != "completed" or int(
        payload.get("iterations_completed") or 0
    ) < starting_iterations:
        raise RuntimeError(
            "formal controller exited without a completed starting checkpoint: "
            f"status={payload.get('status')}, "
            f"iterations={payload.get('iterations_completed')}"
        )


def inferred_pair(mesh_name: str, starting_iterations: int) -> tuple[str, str]:
    remote_dir = study.remote_join(
        study.REMOTE_STUDY_ROOT, mesh_name.replace("-", "_")
    )
    label = f"iter{starting_iterations}_final"
    return (
        study.remote_join(remote_dir, f"{mesh_name}_{label}.cas.h5"),
        study.remote_join(remote_dir, f"{mesh_name}_{label}.dat.h5"),
    )


def stable(stability: Mapping[str, Mapping[str, Any]], fields: tuple[str, ...], limit: float) -> bool:
    for field in fields:
        drift = float(stability[field]["drift_percent"])
        if not math.isfinite(drift) or drift > limit:
            return False
    return True


def start_separate_transcript(solver: Any, transcript: str) -> None:
    """Start this attempt's transcript, replacing a stale active transcript."""
    try:
        solver.settings.file.start_transcript(file_name=transcript)
        return
    except Exception as first_exc:
        print(
            f"start_transcript initial attempt -> {type(first_exc).__name__}: {first_exc}",
            flush=True,
        )
    try:
        solver.settings.file.stop_transcript()
    except Exception:
        pass
    solver.settings.file.start_transcript(file_name=transcript)


def connect_with_retry(
    args: argparse.Namespace,
    manifest_path: Path,
    result: dict[str, Any],
) -> Any:
    deadline = time.monotonic() + max(0.0, args.connect_retry_hours) * 3600.0
    while True:
        try:
            # Fluent generates a new password when its server is restarted.
            # Reload the local connection details while queued so a corrected
            # password/port can take effect without relaunching this controller.
            load_dotenv(override=True)
            solver = connect(server_id=args.server_id)
            result.pop("last_connection_error", None)
            return solver
        except Exception as exc:
            if args.connect_retry_hours <= 0 or time.monotonic() >= deadline:
                raise
            result.update(
                {
                    "status": "waiting_for_connection",
                    "last_connection_error": f"{type(exc).__name__}: {exc}",
                    "queue_heartbeat_epoch": time.time(),
                }
            )
            study.write_json(manifest_path, result)
            print(
                "Fluent unavailable; extension remains queued: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )
            time.sleep(max(5.0, args.connect_retry_seconds))


def run_extension(args: argparse.Namespace, manifest_path: Path, result: dict[str, Any]) -> None:
    mesh_name = args.mesh_name
    local_dir = manifest_path.parent
    remote_dir = study.remote_join(
        study.REMOTE_STUDY_ROOT, mesh_name.replace("-", "_")
    )
    default_case, default_data = inferred_pair(mesh_name, args.starting_iterations)
    case_file = args.resume_case or default_case
    data_file = args.resume_data or default_data
    transcript = study.remote_join(
        remote_dir,
        f"{mesh_name}_{args.run_label}_{args.starting_iterations}_{args.target_iterations}_transcript.trn",
    )

    preflight_payload = read_json(study.LOCAL_ROOT / "preflight_manifest.json")
    preflight_by_name = {
        str(row["mesh_name"]): row for row in preflight_payload.get("meshes", [])
    }
    preflight = preflight_by_name[mesh_name]
    baseline_snapshot = read_json(
        study.LOCAL_ROOT / "mesh_300k" / "mesh-300k_settings_readback.json"
    )

    solver = connect_with_retry(args, manifest_path, result)
    print(f"connected_fluent_version: {solver.get_fluent_version()}", flush=True)
    try:
        start_separate_transcript(solver, transcript)

        resume.read_case_data(solver, case_file, data_file)
        zones = study.current_zone_mapping(solver, allow_rename=False)
        mesh_metrics, quality_text = study.collect_mesh_reports(solver)
        expected_cells = int(preflight["mesh_metrics"]["cells"])
        if int(mesh_metrics["cells"]) != expected_cells:
            raise RuntimeError(
                f"extension mesh mismatch: expected {expected_cells}, got {mesh_metrics['cells']}"
            )

        snapshot = study.capture_settings(solver, remote_dir)
        snapshot.update(study.verify_initialized_phase_identity(solver, remote_dir))
        errors = study.validate_settings(snapshot, mesh_metrics, require_phase_identity=True)
        if resume.science_fingerprint(snapshot) != resume.science_fingerprint(baseline_snapshot):
            errors.append("extension scientific settings fingerprint differs from baseline")
        if errors:
            raise RuntimeError("extension readback failed: " + "; ".join(errors))

        result.update(
            {
                "status": "running",
                "started_epoch": time.time(),
                "resume_case": case_file,
                "resume_data": data_file,
                "zones": zones,
                "mesh_metrics": mesh_metrics,
                "settings_readback": "accepted",
                "dpm_interaction": snapshot["dpm_interaction"],
            }
        )
        study.write_json(manifest_path, result)

        sweep.configure_residual_history(solver, args.target_iterations + study.BLOCK)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.set_verified_iteration_label(solver, args.starting_iterations)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()

        physical_rows: list[dict[str, Any]] = []
        residual_rows: list[dict[str, Any]] = []
        completed = args.starting_iterations
        while completed < args.target_iterations:
            requested = min(study.BLOCK, args.target_iterations - completed)
            before = study.monitor_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=requested)
            after = study.require_point_advance(solver, before, requested)
            completed += requested
            result["iteration_evidence"].append(
                {
                    "block_end": completed,
                    "requested": requested,
                    "before": before,
                    "after": after,
                    "extension": True,
                }
            )
            physical_rows.append(
                study.collect_physical_metrics(solver, remote_dir, completed)
            )
            study.write_csv(
                local_dir / f"{mesh_name}_extension_physical_monitor_history.csv",
                physical_rows,
            )
            residual_rows = resume.merge_iteration_rows(
                residual_rows,
                [
                    row
                    for row in sweep.monitor_history_rows(solver)
                    if args.starting_iterations < float(row["iteration"]) <= completed
                ],
            )
            sweep.write_monitor_history_csv(
                local_dir / f"{mesh_name}_extension_residual_history.csv",
                residual_rows,
            )
            if (
                completed % args.checkpoint_interval == 0
                or completed == args.target_iterations
            ):
                result["checkpoints"][str(completed)] = study.save_pair(
                    solver, remote_dir, mesh_name, f"iter{completed}_{args.run_label}"
                )
            result["iterations_completed"] = completed
            result["queue_heartbeat_epoch"] = time.time()
            study.write_json(manifest_path, result)
            print(
                f"{mesh_name}: extension progress {completed}/{args.target_iterations}",
                flush=True,
            )

        first_stability_iteration = args.target_iterations - 500
        stability = study.monitor_stability(
            physical_rows,
            PRIMARY_FIELDS + SECONDARY_FIELDS,
            first_iteration=first_stability_iteration,
        )
        iteration_status = (
            "accepted"
            if stable(stability, PRIMARY_FIELDS, 0.5)
            and stable(stability, SECONDARY_FIELDS, 1.0)
            else "unresolved"
        )
        metrics_payload = {
            "study_id": study.STUDY_ID,
            "mesh_name": mesh_name,
            "classification": "diagnostic",
            "iteration_independence_status": iteration_status,
            "iteration_range": [args.starting_iterations, args.target_iterations],
            "final_metrics": physical_rows[-1],
            "monitor_stability_final_500": stability,
            "acceptance_limits_percent": {"primary": 0.5, "secondary": 1.0},
            "mass_balance_scope": (
                "reported but not used to accept this extension; bottom is intentionally a wall"
            ),
            "dpm": "off; no injections run",
        }
        study.write_json(local_dir / f"{mesh_name}_extension_metrics.json", metrics_payload)
        (local_dir / f"{mesh_name}_extension_mesh_quality.txt").write_text(
            quality_text, encoding="utf-8"
        )
        sweep.remote_text_write_best_effort(
            solver,
            study.remote_join(remote_dir, f"{mesh_name}_{args.run_label}_metrics.json"),
            json.dumps(metrics_payload, indent=2, default=str),
        )
        result.update(
            {
                "status": "completed",
                "classification": "diagnostic",
                "iteration_independence_status": iteration_status,
                "iterations_completed": args.target_iterations,
                "metrics": metrics_payload,
                "completed_epoch": time.time(),
            }
        )
        study.write_json(manifest_path, result)
        print("mesh_iteration_extension: COMPLETE", flush=True)
    except Exception as exc:
        result.update(
            {
                "status": "failed",
                "classification": "unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        study.write_json(manifest_path, result)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass


def main() -> int:
    args = build_parser().parse_args()
    if args.starting_iterations < study.ITERATIONS:
        raise ValueError("extension must start at or after the formal 3000-iteration endpoint")
    if args.target_iterations <= args.starting_iterations:
        raise ValueError("--target-iterations must exceed --starting-iterations")
    if args.checkpoint_interval <= 0:
        raise ValueError("--checkpoint-interval must be positive")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_label):
        raise ValueError("--run-label may contain only letters, digits, '_' and '-'")

    load_dotenv()
    local_dir = (
        study.LOCAL_ROOT
        / args.mesh_name.replace("-", "_")
        / f"extension_{args.starting_iterations}_{args.target_iterations}_{args.run_label}"
    )
    manifest_path = local_dir / f"{args.mesh_name}_extension_manifest.json"
    result: dict[str, Any] = {
        "study_id": study.STUDY_ID,
        "mesh_name": args.mesh_name,
        "status": "queued" if args.wait_for_pid else "starting",
        "classification": "diagnostic",
        "starting_iterations": args.starting_iterations,
        "target_iterations": args.target_iterations,
        "block_size": study.BLOCK,
        "checkpoint_interval": args.checkpoint_interval,
        "run_label": args.run_label,
        "checkpoints": {},
        "iteration_evidence": [],
        "queued_epoch": time.time(),
        "wait_for_pid": args.wait_for_pid,
        "no_reinitialization": True,
        "dpm": "off; no injections run",
    }
    study.write_json(manifest_path, result)

    try:
        if args.wait_for_pid is not None:
            wait_for_formal_controller(
                args.wait_for_pid,
                args.mesh_name,
                args.starting_iterations,
                args.wait_timeout_hours,
                args.poll_seconds,
                manifest_path,
                result,
            )
        run_extension(args, manifest_path, result)
        return 0
    except Exception as exc:
        result.update(
            {
                "status": "failed",
                "classification": "unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        study.write_json(manifest_path, result)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
