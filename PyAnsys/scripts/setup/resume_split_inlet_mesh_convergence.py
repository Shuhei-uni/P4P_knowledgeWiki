#!/usr/bin/env python3
"""Resume the split-inlet carrier mesh study after a controller disconnect.

This continuation is deliberately carrier-only. It loads an explicitly saved
case/data recovery pair, verifies the current mesh and scientific settings,
continues to the 3000-iteration endpoint, and then runs later meshes using the
normal fresh-initialization production workflow.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping, Sequence

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as study  # noqa: E402


DEFAULT_MESH = "mesh-1600k"
DEFAULT_START = 663
DEFAULT_RECOVERY_DIR = rf"{study.REMOTE_STUDY_ROOT}\mesh_1600k"
DEFAULT_CASE = rf"{DEFAULT_RECOVERY_DIR}\mesh-1600k_recovered_iter663.cas.h5"
DEFAULT_DATA = rf"{DEFAULT_RECOVERY_DIR}\mesh-1600k_recovered_iter663.dat.h5"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--mesh-name", default=DEFAULT_MESH, choices=study.MESH_NAMES)
    parser.add_argument("--starting-iterations", type=int, default=DEFAULT_START)
    parser.add_argument("--resume-case", default=DEFAULT_CASE)
    parser.add_argument("--resume-data", default=DEFAULT_DATA)
    parser.add_argument(
        "--continue-later-meshes",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Continue all canonical meshes after the recovered mesh (default: true).",
    )
    return parser


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
    except OSError:
        return []
    converted: list[dict[str, Any]] = []
    for row in rows:
        item: dict[str, Any] = {}
        for key, value in row.items():
            try:
                item[key] = float(value)
            except (TypeError, ValueError):
                item[key] = value
        converted.append(item)
    return converted


def merge_iteration_rows(
    existing: Sequence[Mapping[str, Any]],
    new: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    merged: dict[float, dict[str, Any]] = {}
    for row in [*existing, *new]:
        if "iteration" not in row:
            continue
        merged[float(row["iteration"])] = dict(row)
    return [merged[key] for key in sorted(merged)]


def science_fingerprint(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Exclude runtime monitor buffers while retaining all scientific setup."""
    fingerprint = study.critical_fingerprint(snapshot)
    fingerprint.pop("residual", None)
    fingerprint.pop("initialization", None)
    return fingerprint


def read_case_data(solver: Any, case_file: str, data_file: str) -> None:
    study.require_remote_input(solver, case_file, "resume case")
    study.require_remote_input(solver, data_file, "resume data")
    solver.settings.file.read_case(file_name=case_file)
    solver.settings.file.read_data(file_name=data_file)


def finalize_mesh(
    solver: Any,
    mesh_name: str,
    mesh_metrics: Mapping[str, Any],
    physical_rows: list[dict[str, Any]],
    quality_text: str,
    result: dict[str, Any],
    local_dir: Path,
    remote_dir: str,
) -> dict[str, Any]:
    final_metrics = physical_rows[-1]
    primary_fields = [
        "pressure_drop_pa",
        "vapor_steamoutlet_kgs",
        "liquid_steamoutlet_kgs",
        "carrier_outlet_quality_percent_trend_only",
    ]
    secondary_fields = [
        "outlet_area_weighted_velocity_ms",
        "domain_volume_avg_velocity_ms",
        "domain_volume_avg_vorticity_s-1",
    ]
    stability = study.monitor_stability(physical_rows, primary_fields + secondary_fields)
    balance_pass = all(
        final_metrics[field] <= 0.5
        for field in (
            "mixture_imbalance_percent",
            "vapor_imbalance_percent",
            "liquid_imbalance_percent",
        )
    )
    primary_stable = all(stability[field]["drift_percent"] <= 0.5 for field in primary_fields)
    secondary_stable = all(stability[field]["drift_percent"] <= 1.0 for field in secondary_fields)
    classification = "accepted" if balance_pass and primary_stable and secondary_stable else "unresolved"
    metrics_payload = {
        "study_id": study.STUDY_ID,
        "mesh_name": mesh_name,
        "classification": classification,
        "mesh_metrics": dict(mesh_metrics),
        "final_metrics": final_metrics,
        "monitor_stability_2500_3000": stability,
        "acceptance": {
            "phase_and_mixture_balance_pass": balance_pass,
            "primary_monitor_stability_pass": primary_stable,
            "secondary_monitor_stability_pass": secondary_stable,
        },
        "quality_metric_text_file": f"{mesh_name}_mesh_quality.txt",
        "carrier_quality_scope": (
            "trend-only; bottom is a wall and steamoutlet is the only carrier outlet"
        ),
        "continuation": {
            "resumed": True,
            "starting_iterations": result["resume"]["starting_iterations"],
            "recovery_case": result["resume"]["case"],
            "recovery_data": result["resume"]["data"],
        },
    }
    study.write_json(local_dir / f"{mesh_name}_metrics.json", metrics_payload)
    study.write_csv(local_dir / f"{mesh_name}_mass_balance_history.csv", physical_rows)
    study.write_csv(local_dir / f"{mesh_name}_surface_metrics.csv", [final_metrics])
    (local_dir / f"{mesh_name}_mesh_quality.txt").write_text(quality_text, encoding="utf-8")
    sweep.remote_text_write_best_effort(
        solver,
        study.remote_join(remote_dir, f"{mesh_name}_metrics.json"),
        json.dumps(metrics_payload, indent=2, default=str),
    )
    result.update(
        {
            "status": "completed",
            "classification": classification,
            "iterations_completed": study.ITERATIONS,
            "final_checkpoint_is_3000_checkpoint": True,
            "metrics": metrics_payload,
            "completed_epoch": time.time(),
        }
    )
    study.write_json(local_dir / f"{mesh_name}_run_manifest.json", result)
    return result


def resume_current_mesh(
    solver: Any,
    preflight: Mapping[str, Any],
    baseline_snapshot: Mapping[str, Any],
    starting_iterations: int,
    case_file: str,
    data_file: str,
) -> dict[str, Any]:
    mesh_name = str(preflight["mesh_name"])
    local_dir = study.LOCAL_ROOT / mesh_name.replace("-", "_")
    remote_dir = study.remote_join(study.REMOTE_STUDY_ROOT, mesh_name.replace("-", "_"))
    transcript = study.remote_join(
        remote_dir, f"{mesh_name}_resume_from_{starting_iterations}_transcript.trn"
    )
    old_manifest = study.load_json(local_dir / f"{mesh_name}_run_manifest.json") if hasattr(study, "load_json") else None
    if old_manifest is None:
        try:
            old_manifest = json.loads(
                (local_dir / f"{mesh_name}_run_manifest.json").read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            old_manifest = {}
    result: dict[str, Any] = dict(old_manifest)
    result.update(
        {
            "mesh_name": mesh_name,
            "status": "running",
            "classification": None,
            "iterations_requested": study.ITERATIONS,
            "iterations_completed": starting_iterations,
            "resumed_epoch": time.time(),
            "resume": {
                "starting_iterations": starting_iterations,
                "case": case_file,
                "data": data_file,
                "reason": "gRPC stream removed during the 500-750 block",
            },
        }
    )
    result.setdefault("checkpoints", {})[str(starting_iterations)] = {
        "case": case_file,
        "data": data_file,
        "classification": "recovery",
    }
    result.setdefault("iteration_evidence", [])
    study.write_json(local_dir / f"{mesh_name}_run_manifest.json", result)

    try:
        solver.settings.file.start_transcript(file_name=transcript)
    except Exception as exc:
        print(f"start_transcript: diagnostic failure -> {type(exc).__name__}: {exc}")
    try:
        read_case_data(solver, case_file, data_file)
        zones = study.current_zone_mapping(solver, allow_rename=False)
        mesh_metrics, quality_text = study.collect_mesh_reports(solver)
        expected_cells = int(preflight["mesh_metrics"]["cells"])
        if int(mesh_metrics["cells"]) != expected_cells:
            raise RuntimeError(
                f"resume mesh mismatch: expected {expected_cells} cells, got {mesh_metrics['cells']}"
            )
        snapshot = study.capture_settings(solver, remote_dir)
        snapshot.update(study.verify_initialized_phase_identity(solver, remote_dir))
        errors = study.validate_settings(snapshot, mesh_metrics, require_phase_identity=True)
        if science_fingerprint(snapshot) != science_fingerprint(baseline_snapshot):
            errors.append("resume scientific settings fingerprint differs from accepted baseline")
        if errors:
            raise RuntimeError("resume readback failed: " + "; ".join(errors))
        result["resume_validation"] = {
            "zones": zones,
            "mesh_metrics": mesh_metrics,
            "settings": "accepted",
            "dpm_interaction": snapshot["dpm_interaction"],
        }

        study.sweep.configure_residual_history(solver, 4000)
        study.sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.set_verified_iteration_label(solver, starting_iterations)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()

        physical_path = local_dir / f"{mesh_name}_physical_monitor_history.csv"
        residual_path = local_dir / f"{mesh_name}_residual_history.csv"
        physical_rows = read_csv_rows(physical_path)
        residual_rows = read_csv_rows(residual_path)
        completed = starting_iterations
        while completed < study.ITERATIONS:
            next_boundary = min(((completed // study.BLOCK) + 1) * study.BLOCK, study.ITERATIONS)
            requested = next_boundary - completed
            before = study.monitor_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=requested)
            after = study.require_point_advance(solver, before, requested)
            completed = next_boundary
            result["iteration_evidence"].append(
                {
                    "block_end": completed,
                    "requested": requested,
                    "before": before,
                    "after": after,
                    "continuation": True,
                }
            )
            metrics = study.collect_physical_metrics(solver, remote_dir, completed)
            physical_rows = merge_iteration_rows(physical_rows, [metrics])
            study.write_csv(physical_path, physical_rows)
            residual_rows = merge_iteration_rows(
                residual_rows,
                sweep.monitor_history_rows(solver),
            )
            sweep.write_monitor_history_csv(residual_path, residual_rows)
            if completed in study.CHECKPOINTS:
                label = (
                    f"iter{completed}_final"
                    if completed == study.ITERATIONS
                    else f"checkpoint_{completed}"
                )
                result["checkpoints"][str(completed)] = study.save_pair(
                    solver, remote_dir, mesh_name, label
                )
            result["iterations_completed"] = completed
            study.write_json(local_dir / f"{mesh_name}_run_manifest.json", result)
            print(f"{mesh_name}: resumed progress {completed}/{study.ITERATIONS}", flush=True)

        return finalize_mesh(
            solver,
            mesh_name,
            mesh_metrics,
            physical_rows,
            quality_text,
            result,
            local_dir,
            remote_dir,
        )
    except Exception as exc:
        result.update(
            {
                "status": "failed",
                "classification": "unresolved",
                "failure_category": study.classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        study.write_json(local_dir / f"{mesh_name}_run_manifest.json", result)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()
    if not 0 <= args.starting_iterations < study.ITERATIONS:
        raise ValueError("--starting-iterations must be between 0 and 2999")
    manifest = json.loads(
        (study.LOCAL_ROOT / "preflight_manifest.json").read_text(encoding="utf-8")
    )
    by_name = {row["mesh_name"]: row for row in manifest["meshes"]}
    preflight = by_name[args.mesh_name]
    baseline_snapshot = json.loads(
        (
            study.LOCAL_ROOT
            / "mesh_300k"
            / "mesh-300k_settings_readback.json"
        ).read_text(encoding="utf-8")
    )
    solver = connect(server_id=args.server_id)
    print(f"connected_fluent_version: {solver.get_fluent_version()}")
    resumed = resume_current_mesh(
        solver,
        preflight,
        baseline_snapshot,
        args.starting_iterations,
        args.resume_case,
        args.resume_data,
    )

    runs: list[dict[str, Any]] = []
    for name in study.MESH_NAMES:
        path = study.LOCAL_ROOT / name.replace("-", "_") / f"{name}_run_manifest.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("status") == "completed":
            runs.append(payload)
    if resumed not in runs:
        runs.append(resumed)

    if args.continue_later_meshes:
        baseline_hash = str(manifest["baseline_settings_fingerprint"])
        completed_names = {
            str(run.get("mesh_name"))
            for run in runs
            if run.get("status") == "completed"
            and int(run.get("iterations_completed", 0)) >= study.ITERATIONS
        }
        for mesh_name in study.MESH_NAMES:
            if mesh_name == args.mesh_name or mesh_name in completed_names:
                continue
            if mesh_name not in by_name:
                raise RuntimeError(f"Mesh lacks an accepted preflight record: {mesh_name}")
            print(f"\n=== PRODUCTION {mesh_name} ===", flush=True)
            run = study.formal_run_one(solver, by_name[mesh_name], baseline_hash)
            runs.append(run)
            study.write_json(
                study.LOCAL_ROOT / "study_manifest.json",
                {
                    "study_id": study.STUDY_ID,
                    "status": "running",
                    "baseline_settings_fingerprint": baseline_hash,
                    "runs": runs,
                    "resumed_from": args.mesh_name,
                    "updated_epoch": time.time(),
                },
            )

    study.write_json(
        study.LOCAL_ROOT / "study_manifest.json",
        {
            "study_id": study.STUDY_ID,
            "status": "completed",
            "baseline_settings_fingerprint": manifest["baseline_settings_fingerprint"],
            "runs": runs,
            "resumed_from": args.mesh_name,
            "completed_epoch": time.time(),
        },
    )
    print("mesh_convergence_continuation: COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
