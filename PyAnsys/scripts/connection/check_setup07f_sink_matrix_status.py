#!/usr/bin/env python3
"""Print read-only status for the setup-07f sink thickness/rate matrix."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STUDY_DIR = (
    PROJECT_ROOT / "output" / "split_inlet_sink_thickness_rate_matrix_20260811"
)


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def last_csv_row(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return rows[-1] if rows else None


def show_case(run_label: str) -> None:
    run_dir = STUDY_DIR / run_label
    manifest_path = run_dir / "qualification_manifest.json"
    manifest = load_json(manifest_path)
    if manifest is None:
        print(f"[PENDING] {run_label}: no case manifest yet")
        return
    age = max(0.0, time.time() - manifest_path.stat().st_mtime)
    status = str(manifest.get("status", "unknown")).upper()
    print(f"[{status:9}] {run_label} | manifest age {age:.0f}s")
    print(
        "  thickness={} m | tau={} s | cumulative={} | R=1={}".format(
            manifest.get("layer_thickness_m"),
            manifest.get("tau_s"),
            manifest.get("cumulative_iterations_completed", 0),
            manifest.get("r1_iterations_completed", 0),
        )
    )
    mask = manifest.get("mask_readback") or {}
    if mask:
        print(
            "  mask: {:.0f} cells | {:.9g} m3 | y=[{:.6g},{:.6g}] m".format(
                float(mask.get("count", 0.0)),
                float(manifest.get("mask_volume_integral_m3", mask.get("volume", 0.0))),
                float(mask.get("y_min", 0.0)),
                float(mask.get("y_max", 0.0)),
            )
        )
    latest = last_csv_row(run_dir / "physical_monitor_history.csv")
    if latest:
        print(
            "  latest: stage={} sink={} kg/s liquid-imbalance={}% "
            "pressure={} Pa inventory={} kg".format(
                latest.get("stage"),
                latest.get("sink_magnitude_kgs"),
                latest.get("liquid_imbalance_percent"),
                latest.get("pressure_drop_pa"),
                latest.get("domain_liquid_inventory_kg"),
            )
        )
    print(
        "  classification={} | stable-windows={} | stop={}".format(
            manifest.get("classification"),
            manifest.get("stable_windows_observed", 0),
            manifest.get("stop_reason", ""),
        )
    )
    print(f"  checkpoints: {', '.join((manifest.get('checkpoints') or {}).keys())}")


def main() -> int:
    queue_path = STUDY_DIR / "queue_manifest.json"
    queue = load_json(queue_path)
    if queue is None:
        print(f"Setup 07f queue manifest not found: {queue_path}")
        return 2
    print(
        "Setup 07f sink thickness/rate matrix: {} | {}".format(
            queue.get("status"), queue.get("classification")
        )
    )
    print(f"Active case: {queue.get('active_run_label', 'none')}")
    for run_label in queue.get("case_order", []):
        show_case(str(run_label))
    print("Read-only status check: no Fluent settings or calculations were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
