#!/usr/bin/env python3
"""Print setup 07c's local thick-sink status; optionally probe live Fluent."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


LOCAL_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_thickened_water_level_sink_20260808"
    / "mesh-900k_band0p140165_tau0p100_v1"
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--live", action="store_true")
    return result


def last_row(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return rows[-1] if rows else None


def main() -> int:
    args = parser().parse_args()
    manifest_path = LOCAL_DIR / "qualification_manifest.json"
    if not manifest_path.exists():
        print(f"Setup 07c manifest not found: {manifest_path}")
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(f"Setup 07c thick sink: {manifest.get('status')}")
    print(f"Classification: {manifest.get('classification')}")
    print(
        "Band: {:.6g} m ({} nominal layers) | tau: {} s".format(
            float(manifest.get("layer_thickness_m", 0.0)),
            manifest.get("nominal_equivalent_layers"),
            manifest.get("tau_s"),
        )
    )
    print(f"DPM: {manifest.get('dpm')}")
    mask = manifest.get("mask_readback")
    if mask:
        print(
            "Mask: {count:.0f} cells, {volume:.6g} m3, y=[{y_min:.6g}, {y_max:.6g}] m".format(
                **mask
            )
        )
    print(
        "Iterations: cumulative={} | R=1={}".format(
            manifest.get("cumulative_iterations_completed", 0),
            manifest.get("r1_iterations_completed", 0),
        )
    )
    latest = last_row(LOCAL_DIR / "physical_monitor_history.csv")
    if latest:
        print(
            "Latest: stage={} sink={} kg/s balance={}% pressure-drop={} Pa inventory={} kg".format(
                latest.get("stage"),
                latest.get("sink_magnitude_kgs"),
                latest.get("liquid_source_augmented_imbalance_percent"),
                latest.get("pressure_drop_pa"),
                latest.get("domain_liquid_inventory_kg"),
            )
        )
    print(f"Stop reason: {manifest.get('stop_reason', '')}")
    print(f"Checkpoints: {', '.join(manifest.get('checkpoints', {}))}")
    if args.live:
        load_dotenv(PROJECT_ROOT / ".env")
        solver = connect(server_id=args.server_id)
        print(f"Fluent health: {solver.health_check.status()}")
        print(f"Fluent version: {solver.get_fluent_version()}")
        try:
            print(
                "Live controls: ramp={} tau={} thickness={} m".format(
                    solver.scheme.eval("(rpgetvar 'user/cwl07c/ramp)"),
                    solver.scheme.eval("(rpgetvar 'user/cwl07c/tau-s)"),
                    solver.scheme.eval("(rpgetvar 'user/cwl07c/layer-thickness-m)"),
                )
            )
        except Exception as exc:
            print(f"Live setup-07c controls unavailable: {type(exc).__name__}: {exc}")
    print("Read-only status check: no Fluent settings or calculations were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
