#!/usr/bin/env python3
"""Assess the true single-face F1 carrier against the common gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from assess_phase8_carrier_window import FATAL, RESIDUAL, history


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run = json.loads(args.manifest.read_text(encoding="utf-8"))
    if run["status"] != "COMPLETE" or run["family"] != "F1-single-face":
        raise RuntimeError("Single-face pilot has not completed")
    end = int(run["checkpoints"][-1]["native_iteration"])
    points = np.arange(end - 500, end + 1, 10)
    reports = {name: history(path) for name, path in run["report_paths"].items()}
    names = ("p8-flux-mixture-liquidinlet", "p8-flux-mixture-steamoutlet",
             "p8-flux-phase2-steamoutlet", "p8-mass-phase2-total")
    for name in names:
        missing = set(points) - reports[name].keys()
        if missing:
            raise RuntimeError(f"{name} missing coordinates: {sorted(missing)[:5]}")
    inlet = np.array([reports[names[0]][i] for i in points])
    outlet = np.array([reports[names[1]][i] for i in points])
    inventory = np.array([reports[names[3]][i] for i in points])
    gap = inlet + outlet
    transcript = Path(run["paths"]["transcript"]).read_text(encoding="utf-8")
    residuals = {int(i): float(v) for i, v in RESIDUAL.findall(transcript)}
    missing = set(range(end - 499, end + 1)) - residuals.keys()
    if missing:
        raise RuntimeError(f"Missing continuity rows: {sorted(missing)[:5]}")
    continuity = np.array([residuals[i] for i in range(end - 499, end + 1)])
    slope = float(np.polyfit(points, inventory, 1)[0])
    checks = {
        "mean_abs_boundary_gap_le_1pct_feed": float(np.mean(np.abs(gap))) <=
        float(np.mean(inlet)) * 0.01,
        "inventory_slope_abs_le_0p01_kg_per_iteration": abs(slope) <= 0.01,
        "continuity_below_0p02": bool(np.max(continuity) < 0.02),
        "no_fatal_event": not bool(FATAL.search(transcript)),
    }
    result = {"manifest": str(args.manifest), "native_window": [int(points[0]), end],
              "observed": {
                  "mean_abs_boundary_gap_kg_s": float(np.mean(np.abs(gap))),
                  "mean_abs_boundary_gap_fraction_of_feed":
                      float(np.mean(np.abs(gap)) / np.mean(inlet)),
                  "terminal_boundary_gap_kg_s": float(gap[-1]),
                  "terminal_phase2_steamoutlet_kg_s": -float(reports[names[2]][end]),
                  "phase2_inventory_start_end_kg": [float(inventory[0]),
                                                     float(inventory[-1])],
                  "phase2_inventory_slope_kg_per_steady_iteration": slope,
                  "continuity_residual_range": [float(np.min(continuity)),
                                                float(np.max(continuity))],
                  "reverse_flow_warning_count": transcript.count("Reversed flow on"),
                  "viscosity_limit_warning_count":
                      transcript.count("turbulent viscosity limited")},
              "checks": checks, "operational_carrier_gate_pass": all(checks.values()),
              "claim_limit": "Single-face SIMPLE setup comparison only. Steady-iteration inventory drift is not physical storage; no matched F1/F2 DPM footprint or physical separation efficiency is established."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
