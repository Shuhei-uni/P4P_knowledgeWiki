#!/usr/bin/env python3
"""Print the current setup-07b sink qualification status without mutating Fluent."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


RUN_LABEL = "mesh-900k_tau0p100_qualification_v1"
LOCAL_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_constant_water_level_sink_20260807"
    / RUN_LABEL
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--live", action="store_true")
    return result


def last_csv_row(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return rows[-1] if rows else None


def main() -> int:
    args = parser().parse_args()
    manifest_path = LOCAL_DIR / "qualification_manifest.json"
    if not manifest_path.exists():
        print(f"Qualification manifest not found: {manifest_path}")
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    latest = last_csv_row(LOCAL_DIR / "physical_monitor_history.csv")
    print(f"Setup 07b qualification: {manifest.get('status')}")
    print(f"Classification: {manifest.get('classification')}")
    print(f"Source: {manifest.get('source_origin')}")
    print(f"tau: {manifest.get('tau_s')} s | DPM: {manifest.get('dpm')}")
    print(
        "Iterations: cumulative={} | R=1={}".format(
            manifest.get("cumulative_iterations_completed", 0),
            manifest.get("r1_iterations_completed", 0),
        )
    )
    if latest:
        print(
            "Latest: stage={stage} ramp={ramp} sink={sink} kg/s "
            "liquid-balance={balance}% pressure-drop={pressure} Pa "
            "liquid-inventory={inventory} kg".format(
                stage=latest.get("stage"),
                ramp=latest.get("ramp"),
                sink=latest.get("integrated_liquid_sink_kgs"),
                balance=latest.get("liquid_source_augmented_imbalance_percent"),
                pressure=latest.get("pressure_drop_pa"),
                inventory=latest.get("domain_liquid_inventory_kg"),
            )
        )
    window = manifest.get("latest_500_iteration_assessment")
    if window:
        print(
            "Latest 500-window: pass={} physical={} balance={} residual-level={}".format(
                window.get("acceptance_window_pass"),
                window.get("physical_stable"),
                window.get("balance_pass"),
                window.get("residual_level_pass"),
            )
        )
    print(f"Checkpoints: {', '.join(manifest.get('checkpoints', {}))}")

    if args.live:
        load_dotenv(PROJECT_ROOT / ".env")
        solver = connect(server_id=args.server_id)
        print(f"Fluent health: {solver.health_check.status()}")
        print(f"Fluent version: {solver.get_fluent_version()}")
        try:
            ramp = solver.scheme.eval("(rpgetvar 'user/cwl07b/ramp)")
            tau = solver.scheme.eval("(rpgetvar 'user/cwl07b/tau-s)")
            print(f"Live sink controls: ramp={ramp}, tau={tau} s")
        except Exception as exc:
            print(f"Live sink controls unavailable: {type(exc).__name__}: {exc}")
        try:
            if not solver.monitors.is_streaming:
                solver.monitors.start()
                time.sleep(1.0)
            monitor_names = list(solver.monitors.get_monitor_set_names())
            latest_iterations = []
            for name in monitor_names:
                x_values, _ = solver.monitors.get_monitor_set_data(name)
                latest_iterations.extend(float(value) for value in x_values)
            latest_iteration = max(latest_iterations) if latest_iterations else None
            print(f"Live latest monitored iteration: {latest_iteration}")
        except Exception as exc:
            print(f"Live monitor iteration unavailable: {type(exc).__name__}: {exc}")
    print("Read-only status check: no Fluent settings or calculations were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
