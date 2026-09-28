#!/usr/bin/env python3
"""Assess the declared last-500-iteration Phase 8 carrier gate from native files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import numpy as np

ROW = re.compile(r"^\s*(\d+)\s+([-+\d.eE]+)\s*$", re.M)
RESIDUAL = re.compile(r"^\s*(\d+)\s+(\d+\.\d+e[+-]\d+)", re.I | re.M)
FATAL = re.compile(r"floating point exception|error:.*(?:diverg|non-finite)|amg solver diverged", re.I)


def history(path: str) -> dict[int, float]:
    return {int(i): float(v) for i, v in ROW.findall(Path(path).read_text(encoding="utf-8"))}


def assess(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["status"] != "COMPLETE":
        raise RuntimeError(f"Run is not complete: {manifest['status']}")
    end = int(manifest["achieved_active_iterations"])
    points = np.arange(end - 500, end + 1, 10)
    reports = {name: history(path) for name, path in manifest["report_paths"].items()}
    for name in ("p8-flux-mixture-liquidinlet", "p8-flux-mixture-steaminlet",
                 "p8-flux-mixture-steamoutlet", "p8-flux-phase2-steamoutlet",
                 "p8-mass-phase2-total"):
        missing = set(points) - reports[name].keys()
        if missing:
            raise RuntimeError(f"{name} missing assessment rows: {sorted(missing)[:5]}")
    inlet = np.array([reports["p8-flux-mixture-liquidinlet"][i] +
                      reports["p8-flux-mixture-steaminlet"][i] for i in points])
    outlet = np.array([reports["p8-flux-mixture-steamoutlet"][i] for i in points])
    inventory = np.array([reports["p8-mass-phase2-total"][i] for i in points])
    gap = inlet + outlet  # Fluent's mass-flux report is positive into the domain.
    transcript = Path(manifest["paths"]["transcript"]).read_text(encoding="utf-8")
    residuals = {int(i): float(v) for i, v in RESIDUAL.findall(transcript)}
    missing = set(range(end - 499, end + 1)) - residuals.keys()
    if missing:
        raise RuntimeError(f"Transcript missing assessment iterations: {sorted(missing)[:5]}")
    residual_window = np.array([residuals[i] for i in range(end - 499, end + 1)])
    gap_mean_abs = float(np.mean(np.abs(gap)))
    gap_limit = float(np.mean(inlet)) * 0.01
    slope = float(np.polyfit(points, inventory, 1)[0])
    checks = {
        "mean_absolute_mixture_boundary_gap_le_1pct_feed": gap_mean_abs <= gap_limit,
        "absolute_inventory_slope_le_0p01_kg_per_iteration": abs(slope) <= 0.01,
        "continuity_residual_below_0p02": bool(np.max(residual_window) < 0.02),
        "no_fatal_solver_event": not bool(FATAL.search(transcript)),
    }
    return {
        "manifest": str(manifest_path), "assessment_window": [int(points[0]), end],
        "thresholds": {"mixture_gap_kg_s": gap_limit, "inventory_slope_kg_per_iteration": 0.01,
                       "continuity_residual": 0.02},
        "observed": {"mean_absolute_mixture_gap_kg_s": gap_mean_abs,
                     "mean_absolute_mixture_gap_fraction_of_feed": gap_mean_abs / float(np.mean(inlet)),
                     "terminal_mixture_gap_kg_s": float(gap[-1]),
                     "terminal_liquid_outlet_kg_s": -reports["p8-flux-phase2-steamoutlet"][end],
                     "liquid_inventory_start_end_kg": [float(inventory[0]), float(inventory[-1])],
                     "liquid_inventory_slope_kg_per_steady_iteration": slope,
                     "continuity_residual_range": [float(np.min(residual_window)), float(np.max(residual_window))],
                     "reverse_flow_warning_count": transcript.count("Reversed flow on"),
                     "viscosity_limit_warning_count": transcript.count("turbulent viscosity limited")},
        "checks": checks, "developed_for_diagnostic_dpm": all(checks.values()),
        "claim_limit": "Inventory change per steady iteration is not a physical storage rate; passing is an operational carrier gate, not validated separation.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = assess(args.manifest)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
