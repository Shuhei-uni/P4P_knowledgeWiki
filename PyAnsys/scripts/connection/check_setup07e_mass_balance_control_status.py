#!/usr/bin/env python3
"""Print setup 07e's adaptive mass-balance control status."""

from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mass_balance_sink_control_20260810"
    / "mesh-900k_band0p140165_target116p92_v1"
)
ITERATION_RE = re.compile(r"^\s*(\d+)\s+[+\-.0-9Ee]+\s+[+\-.0-9Ee]+")
UDF_RE = re.compile(
    r"CWL07C:.*tau=([+\-.0-9Ee]+)\s+s\s+ramp=([+\-.0-9Ee]+).*"
    r"liquid-inventory=([+\-.0-9Ee]+)\s+kg"
)


def last_row(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return rows[-1] if rows else None


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def endpoint_change_percent(rows: list[dict[str, str]], field: str) -> float | None:
    if len(rows) < 2:
        return None
    first = float(rows[0][field])
    endpoint = float(rows[-1][field])
    if abs(first) <= 1.0e-30:
        return None
    return (endpoint - first) / abs(first) * 100.0


def live_log_status(
    path: Path,
) -> tuple[int | None, float | None, dict[str, float] | None]:
    if not path.exists():
        return None, None, None
    latest_iteration: int | None = None
    latest_udf: dict[str, float] | None = None
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            match = ITERATION_RE.match(line)
            if match:
                latest_iteration = int(match.group(1))
            udf_match = UDF_RE.search(line)
            if udf_match:
                latest_udf = {
                    "tau_s": float(udf_match.group(1)),
                    "ramp": float(udf_match.group(2)),
                    "band_liquid_inventory_kg": float(udf_match.group(3)),
                }
    return (
        latest_iteration,
        max(0.0, time.time() - path.stat().st_mtime),
        latest_udf,
    )


def main() -> int:
    manifest_path = LOCAL_DIR / "qualification_manifest.json"
    if not manifest_path.exists():
        print(f"Setup 07e manifest not found: {manifest_path}")
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(f"Setup 07e mass-balance control: {manifest.get('status')}")
    print(f"Classification: {manifest.get('classification')}")
    print(
        "Target: {} kg/s | tau bounds: {} s | feedback block: {} iterations".format(
            manifest.get("adaptive_target_liquid_sink_kgs"),
            manifest.get("adaptive_tau_bounds_s"),
            manifest.get("adaptive_feedback_block_iterations"),
        )
    )
    print(f"DPM: {manifest.get('dpm')}")
    print(
        "Iterations: cumulative={} | R=1={}".format(
            manifest.get("cumulative_iterations_completed", 0),
            manifest.get("r1_iterations_completed", 0),
        )
    )
    live_iteration, log_age_seconds, live_udf = live_log_status(
        LOCAL_DIR / "controller.log"
    )
    if live_iteration is not None and log_age_seconds is not None:
        activity = "active" if log_age_seconds <= 300.0 else "stale"
        print(
            "Live controller log: iteration={} | age={:.1f}s | {} "
            "(transcript observation, not a saved milestone)".format(
                live_iteration, log_age_seconds, activity
            )
        )
        if live_udf is not None:
            target = float(manifest.get("adaptive_target_liquid_sink_kgs", 116.92))
            implied_sink = (
                abs(live_udf["band_liquid_inventory_kg"])
                * live_udf["ramp"]
                / live_udf["tau_s"]
                if live_udf["tau_s"] > 0.0
                else float("nan")
            )
            implied_target_percent = implied_sink / target * 100.0
            wet_state = (
                "reportably wet"
                if live_udf["band_liquid_inventory_kg"] > 1.0e-9
                else "below reporting threshold"
            )
            print(
                "Live UDF: ramp={:.3g} tau={:.6g}s band-inventory={:.6g}kg "
                "implied-sink={:.6g}kg/s ({:.6g}% target; {}; "
                "transcript observation)".format(
                    live_udf["ramp"],
                    live_udf["tau_s"],
                    live_udf["band_liquid_inventory_kg"],
                    implied_sink,
                    implied_target_percent,
                    wet_state,
                )
            )
    latest = last_row(LOCAL_DIR / "physical_monitor_history.csv")
    if latest:
        print(
            "Latest: stage={} tau={} s sink={} kg/s liquid-imbalance={}% "
            "pressure-drop={} Pa inventory={} kg".format(
                latest.get("stage"),
                latest.get("tau_s"),
                latest.get("sink_magnitude_kgs"),
                latest.get("liquid_imbalance_percent"),
                latest.get("pressure_drop_pa"),
                latest.get("domain_liquid_inventory_kg"),
            )
        )
    residual_rows = read_rows(LOCAL_DIR / "residual_history.csv")
    if residual_rows:
        residual = residual_rows[-1]
        velocity_max = max(
            float(residual["x-velocity"]),
            float(residual["y-velocity"]),
            float(residual["z-velocity"]),
        )
        print(
            "Residuals at iteration {}: continuity={:.6g} vf={:.6g} "
            "k={:.6g} epsilon={:.6g} max-velocity={:.6g}".format(
                int(float(residual["iteration"])),
                float(residual["continuity"]),
                float(residual["vf-phase-2"]),
                float(residual["k"]),
                float(residual["epsilon"]),
                velocity_max,
            )
        )
        window = residual_rows[-min(100, len(residual_rows)) :]
        continuity_change = endpoint_change_percent(window, "continuity")
        vf_change = endpoint_change_percent(window, "vf-phase-2")
        if continuity_change is not None and vf_change is not None:
            print(
                "Residual endpoint change over iterations {}-{}: "
                "continuity={:+.3f}% vf={:+.3f}% (directional only)".format(
                    int(float(window[0]["iteration"])),
                    int(float(window[-1]["iteration"])),
                    continuity_change,
                    vf_change,
                )
            )
    history = manifest.get("adaptive_tau_history", [])
    if history:
        print(f"Next tau: {history[-1].get('tau_next_s')} s")
    print(f"Stable windows: {manifest.get('stable_windows_observed', 0)}")
    print(f"Stop reason: {manifest.get('stop_reason', '')}")
    print(f"Checkpoints: {', '.join(manifest.get('checkpoints', {}))}")
    print("Read-only status check: no Fluent settings or calculations were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
