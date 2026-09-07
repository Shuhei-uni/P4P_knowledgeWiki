#!/usr/bin/env python3
"""Report split-inlet mesh-convergence progress without changing Fluent.

By default this script reads the machine-readable manifests written after each
250-iteration block. Use ``--live`` to make a read-only connection to Fluent
and include the iteration currently being solved inside the active block.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


STUDY_ID = "split_inlet_mesh_convergence_20260801"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / STUDY_ID
MESH_NAMES = (
    "mesh-300k",
    "mesh-600k",
    "mesh-900k",
    "mesh-1600k",
    "mesh-1900k",
    "mesh-2000k",
    "mesh-2300k",
)
ITERATIONS_PER_MESH = 3000
EXTENSION_START = 3000
EXTENSION_TARGET = 6000
EXTENSION_MESH = "mesh-2300k"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--live", action="store_true", help="Read current Fluent monitor history.")
    parser.add_argument("--server-id", default="1", help="Fluent connection id from .env.")
    parser.add_argument("--watch", action="store_true", help="Refresh continuously until Ctrl-C.")
    parser.add_argument("--interval", type=float, default=10.0, help="Watch interval in seconds.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as stream:
            return list(csv.DictReader(stream))
    except OSError:
        return []


def final_window_drift_percent(
    rows: list[dict[str, str]], key: str, window_iterations: int = 500
) -> float | None:
    points = [
        (iteration, value)
        for row in rows
        if (iteration := finite_float(row.get("iteration"))) is not None
        and (value := finite_float(row.get(key))) is not None
    ]
    if len(points) < 2:
        return None
    final_iteration = max(point[0] for point in points)
    window = [value for iteration, value in points if iteration >= final_iteration - window_iterations]
    if len(window) < 2:
        return None
    scale = abs(sum(window) / len(window))
    if scale < 1.0e-12:
        return None
    return 100.0 * (max(window) - min(window)) / scale


def finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def age_seconds(path: Path) -> float | None:
    try:
        return max(0.0, time.time() - path.stat().st_mtime)
    except OSError:
        return None


def age_text(seconds: float | None) -> str:
    if seconds is None:
        return "unknown"
    total = int(seconds)
    minutes, seconds = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def read_local_status(output_dir: Path) -> dict[str, Any]:
    preflight = load_json(output_dir / "preflight_manifest.json") or {}
    study = load_json(output_dir / "study_manifest.json") or {}
    preflight_names = {
        str(row.get("mesh_name")) for row in preflight.get("meshes", []) if row.get("mesh_name")
    }
    preflight_by_name = {
        str(row.get("mesh_name")): row
        for row in preflight.get("meshes", [])
        if row.get("mesh_name")
    }
    preflight_status = preflight.get("status", "missing")
    if set(MESH_NAMES) - preflight_names:
        preflight_status = "partial" if preflight_names else "missing"
    meshes: list[dict[str, Any]] = []

    for mesh_name in MESH_NAMES:
        mesh_dir = output_dir / mesh_name.replace("-", "_")
        manifest_path = mesh_dir / f"{mesh_name}_run_manifest.json"
        manifest = load_json(manifest_path) or {}
        metrics_path = mesh_dir / f"{mesh_name}_physical_monitor_history.csv"
        monitor_rows = csv_rows(metrics_path)
        latest_metrics = monitor_rows[-1] if monitor_rows else None
        mesh_metrics = preflight_by_name.get(mesh_name, {}).get("mesh_metrics") or {}
        drift_keys = (
            "pressure_drop_pa",
            "vapor_steamoutlet_kgs",
            "liquid_steamoutlet_kgs",
            "outlet_area_weighted_velocity_ms",
            "domain_volume_avg_velocity_ms",
            "domain_volume_avg_vorticity_s-1",
        )
        iterations = int(manifest.get("iterations_completed") or 0)
        meshes.append(
            {
                "mesh_name": mesh_name,
                "status": manifest.get("status", "pending"),
                "classification": manifest.get("classification"),
                "iterations_completed_block": iterations,
                "iterations_requested": int(manifest.get("iterations_requested") or ITERATIONS_PER_MESH),
                "checkpoints": sorted(
                    str(key) for key in (manifest.get("checkpoints") or {}).keys()
                ),
                "error": manifest.get("error") if manifest.get("status") == "failed" else None,
                "manifest_age_seconds": age_seconds(manifest_path),
                "mesh_metrics": {
                    "cells": mesh_metrics.get("cells"),
                    "characteristic_size_m": mesh_metrics.get("characteristic_size_m"),
                    "minimum_orthogonal_quality": mesh_metrics.get(
                        "minimum_orthogonal_quality"
                    ),
                    "maximum_aspect_ratio": mesh_metrics.get("maximum_aspect_ratio"),
                },
                "latest_metrics": latest_metrics,
                "final_500_iteration_drift_percent": {
                    key: final_window_drift_percent(monitor_rows, key) for key in drift_keys
                },
            }
        )

    active = next((mesh for mesh in meshes if mesh["status"] == "running"), None)
    extension_manifest_candidates = list(
        output_dir.glob(
            "mesh_*/"
            "extension_*/"
            "mesh-*_extension_manifest.json"
        )
    )
    extension_manifest_path = max(
        extension_manifest_candidates,
        key=lambda path: path.stat().st_mtime,
        default=(
            output_dir
            / EXTENSION_MESH.replace("-", "_")
            / f"extension_{EXTENSION_START}_{EXTENSION_TARGET}"
            / f"{EXTENSION_MESH}_extension_manifest.json"
        ),
    )
    extension_dir = extension_manifest_path.parent
    extension_manifest = load_json(extension_manifest_path) or {}
    extension_mesh_name = str(extension_manifest.get("mesh_name") or EXTENSION_MESH)
    extension_rows = csv_rows(
        extension_dir / f"{extension_mesh_name}_extension_physical_monitor_history.csv"
    )
    extension = {
        "mesh_name": extension_mesh_name,
        "status": extension_manifest.get("status", "not_queued"),
        "classification": extension_manifest.get("classification"),
        "starting_iterations": int(
            extension_manifest.get("starting_iterations") or EXTENSION_START
        ),
        "target_iterations": int(
            extension_manifest.get("target_iterations") or EXTENSION_TARGET
        ),
        "iterations_completed": int(
            extension_manifest.get("iterations_completed")
            or extension_manifest.get("formal_iterations_observed")
            or 0
        ),
        "wait_for_pid": extension_manifest.get("wait_for_pid"),
        "run_label": extension_manifest.get("run_label"),
        "latest_metrics": extension_rows[-1] if extension_rows else None,
        "iteration_independence_status": extension_manifest.get(
            "iteration_independence_status"
        ),
        "error": extension_manifest.get("error"),
        "last_connection_error": extension_manifest.get("last_connection_error"),
        "manifest_age_seconds": age_seconds(extension_manifest_path),
    }
    return {
        "study_id": STUDY_ID,
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "preflight_status": preflight_status,
        "study_status": study.get("status", "unknown"),
        "active_mesh": active["mesh_name"] if active else None,
        "completed_block_iterations_total": sum(
            int(mesh["iterations_completed_block"]) for mesh in meshes
        ),
        "requested_iterations_total": ITERATIONS_PER_MESH * len(MESH_NAMES),
        "meshes": meshes,
        "extension": extension,
    }


def read_live_status(solver: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        result["health"] = str(solver.health_check.check_health())
    except Exception as exc:  # read-only diagnostic must degrade gracefully
        result["health_error"] = f"{type(exc).__name__}: {exc}"
    try:
        snapshot = sweep.monitor_iteration_snapshot(solver)
        result["monitor_snapshot"] = snapshot
        residual = snapshot.get("residual") or {}
        result["current_iteration"] = residual.get("last_iteration")
        result["monitor_points"] = residual.get("points")
        result["residual_series"] = residual.get("series") or []
    except Exception as exc:
        result["monitor_error"] = f"{type(exc).__name__}: {exc}"
    return result


def metric_text(metrics: dict[str, str] | None, key: str, suffix: str = "") -> str:
    if not metrics:
        return "n/a"
    value = finite_float(metrics.get(key))
    return "n/a" if value is None else f"{value:.6g}{suffix}"


def value_text(value: Any, suffix: str = "", scale: float = 1.0) -> str:
    number = finite_float(value)
    return "n/a" if number is None else f"{number * scale:.6g}{suffix}"


def render_text(status: dict[str, Any]) -> str:
    lines = [
        f"Mesh convergence status - {status['timestamp']}",
        f"Preflight: {status['preflight_status']} | Study: {status['study_status']}",
        "",
    ]
    live = status.get("live") or {}
    active_name = status.get("active_mesh")

    for mesh in status["meshes"]:
        marker = {
            "completed": "DONE",
            "running": "RUNNING",
            "failed": "FAILED",
        }.get(mesh["status"], "PENDING")
        completed = mesh["iterations_completed_block"]
        total = mesh["iterations_requested"]
        detail = f"{completed}/{total} recorded"
        if mesh["mesh_name"] == active_name and live.get("current_iteration") is not None:
            detail += f", {int(float(live['current_iteration']))}/{total} live"
        classification = mesh.get("classification")
        if classification:
            detail += f", {classification}"
        lines.append(f"[{marker:<7}] {mesh['mesh_name']}: {detail}")
        if mesh.get("error"):
            lines.append(f"          error: {mesh['error']}")
        metrics = mesh.get("latest_metrics")
        if metrics:
            quality = mesh.get("mesh_metrics") or {}
            lines.extend(
                [
                    f"          cells/h: {value_text(quality.get('cells'))} / "
                    f"{value_text(quality.get('characteristic_size_m'), ' m')}",
                    f"          pressure drop: {value_text(metrics.get('pressure_drop_pa'), ' kPa', 0.001)}",
                    f"          outlet vapor/liquid: "
                    f"{value_text(metrics.get('vapor_steamoutlet_kgs'), ' kg/s')} / "
                    f"{value_text(metrics.get('liquid_steamoutlet_kgs'), ' kg/s')}",
                    f"          carrier quality: "
                    f"{value_text(metrics.get('carrier_outlet_quality_percent_trend_only'), '%')} "
                    f"(trend only)",
                    f"          outlet/domain velocity: "
                    f"{value_text(metrics.get('outlet_area_weighted_velocity_ms'), ' m/s')} / "
                    f"{value_text(metrics.get('domain_volume_avg_velocity_ms'), ' m/s')}",
                    f"          domain vorticity: "
                    f"{value_text(metrics.get('domain_volume_avg_vorticity_s-1'), ' 1/s')}",
                    f"          imbalance mix/vapor/liquid: "
                    f"{value_text(metrics.get('mixture_imbalance_percent'), '%')} / "
                    f"{value_text(metrics.get('vapor_imbalance_percent'), '%')} / "
                    f"{value_text(metrics.get('liquid_imbalance_percent'), '%')}",
                ]
            )
            if completed >= total:
                drift = mesh.get("final_500_iteration_drift_percent") or {}
                lines.append(
                    "          final-500 drift Δp/vapor/liquid/outlet-U/domain-U/vorticity: "
                    f"{value_text(drift.get('pressure_drop_pa'), '%')} / "
                    f"{value_text(drift.get('vapor_steamoutlet_kgs'), '%')} / "
                    f"{value_text(drift.get('liquid_steamoutlet_kgs'), '%')} / "
                    f"{value_text(drift.get('outlet_area_weighted_velocity_ms'), '%')} / "
                    f"{value_text(drift.get('domain_volume_avg_velocity_ms'), '%')} / "
                    f"{value_text(drift.get('domain_volume_avg_vorticity_s-1'), '%')}"
                )

    completed_total = status["completed_block_iterations_total"]
    requested_total = status["requested_iterations_total"]
    lines.extend(
        [
            "",
            f"Recorded iteration total: {completed_total}/{requested_total}",
            f"Active mesh: {active_name or 'none'}",
        ]
    )
    extension = status.get("extension") or {}
    extension_status = str(extension.get("status", "not_queued"))
    extension_marker = {
        "queued": "QUEUED",
        "waiting_for_connection": "WAITING",
        "starting": "STARTING",
        "running": "RUNNING",
        "completed": "DONE",
        "failed": "FAILED",
    }.get(extension_status, "NOT QUEUED")
    lines.extend(
        [
            "",
            "Iteration-independence extension:",
            f"[{extension_marker}] {extension.get('mesh_name', EXTENSION_MESH)}: "
            f"{extension.get('starting_iterations', EXTENSION_START)} -> "
            f"{extension.get('target_iterations', EXTENSION_TARGET)} iterations",
        ]
    )
    if extension.get("run_label"):
        lines.append(f"          run label: {extension['run_label']}")
    if extension_status == "queued":
        lines.append(
            f"          waiting behind formal controller PID "
            f"{extension.get('wait_for_pid', 'unknown')}"
        )
    if extension_status == "waiting_for_connection":
        lines.append("          waiting for the Fluent endpoint to become available")
    if extension.get("iterations_completed"):
        lines.append(
            f"          latest recorded iteration: {extension['iterations_completed']}"
        )
    if extension.get("iteration_independence_status"):
        lines.append(
            "          iteration-independence status: "
            f"{extension['iteration_independence_status']}"
        )
    if extension.get("error"):
        lines.append(f"          error: {extension['error']}")
    if extension.get("last_connection_error"):
        lines.append(
            f"          last connection error: {extension['last_connection_error']}"
        )
    if extension_status != "not_queued":
        lines.append(
            f"          extension manifest updated: "
            f"{age_text(extension.get('manifest_age_seconds'))} ago"
        )
    if live:
        lines.append(f"Fluent health: {live.get('health', live.get('health_error', 'unknown'))}")
        if live.get("monitor_error"):
            lines.append(f"Live monitor error: {live['monitor_error']}")

    active = next((mesh for mesh in status["meshes"] if mesh["mesh_name"] == active_name), None)
    if active:
        metrics = active.get("latest_metrics")
        lines.extend(
            [
                "",
                f"Latest completed physical-monitor block: "
                f"{metric_text(metrics, 'iteration')}",
                f"  mixture imbalance: {metric_text(metrics, 'mixture_imbalance_percent', '%')}",
                f"  vapor imbalance:   {metric_text(metrics, 'vapor_imbalance_percent', '%')}",
                f"  liquid imbalance:  {metric_text(metrics, 'liquid_imbalance_percent', '%')}",
                f"  pressure drop:      {metric_text(metrics, 'pressure_drop_pa', ' Pa')}",
                f"Manifest updated: {age_text(active.get('manifest_age_seconds'))} ago",
            ]
        )
    lines.append("Read-only check: no Fluent settings or calculations were changed.")
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    if not output_dir.is_dir():
        print(f"Output directory not found: {output_dir}", file=sys.stderr)
        return 1

    solver = None
    if args.live:
        try:
            solver = connect(server_id=args.server_id)
        except Exception as exc:
            print(f"Live Fluent connection failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            if not args.watch:
                return 2

    try:
        while True:
            status = read_local_status(output_dir)
            if solver is not None:
                status["live"] = read_live_status(solver)
            if args.watch and not args.json:
                print("\033[2J\033[H", end="")
            if args.json:
                print(json.dumps(status, indent=2, default=str), flush=True)
            else:
                print(render_text(status), flush=True)
            if not args.watch:
                return 0
            time.sleep(max(1.0, args.interval))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
