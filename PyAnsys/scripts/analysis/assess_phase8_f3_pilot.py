#!/usr/bin/env python3
"""Assess the first allocated F3 pilot using native steady reports and fates."""
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
    if run["status"] != "COMPLETE" or run["family"] != "F3":
        raise RuntimeError("F3 pilot has not completed")
    end = int(run["checkpoints"][-1]["native_iteration"])
    points = np.arange(end - 500, end + 1, 10)
    reports = {name: history(path) for name, path in run["report_paths"].items()}
    needed = ("p8-flux-mixture-liquidinlet", "p8-flux-mixture-steaminlet",
              "p8-flux-mixture-steamoutlet", "p8-flux-phase2-steamoutlet",
              "p8-mass-phase2-total")
    for name in needed:
        missing = set(points) - reports[name].keys()
        if missing:
            raise RuntimeError(f"{name} missing native rows: {sorted(missing)[:5]}")
    inlet = np.array([reports[needed[0]][i] + reports[needed[1]][i] for i in points])
    outlet = np.array([reports[needed[2]][i] for i in points])
    inventory = np.array([reports[needed[4]][i] for i in points])
    transcript = Path(run["paths"]["transcript"]).read_text(encoding="utf-8")
    residuals = {int(i): float(v) for i, v in RESIDUAL.findall(transcript)}
    missing = set(range(end - 499, end + 1)) - residuals.keys()
    if missing:
        raise RuntimeError(f"Missing residual coordinates: {sorted(missing)[:5]}")
    r = np.array([residuals[i] for i in range(end - 499, end + 1)])
    slope = float(np.polyfit(points, inventory, 1)[0])
    gap = inlet + outlet
    checks = {
        "eulerian_mean_abs_gap_le_1pct_feed": float(np.mean(np.abs(gap))) <=
        float(np.mean(inlet)) * 0.01,
        "liquid_inventory_slope_abs_le_0p01_kg_per_iteration": abs(slope) <= 0.01,
        "continuity_residual_below_0p02": bool(np.max(r) < 0.02),
        "no_fatal_solver_event": not bool(FATAL.search(transcript)),
    }
    source_def = run["report_definitions"].get("p8-dpm-mass-source-total")
    source_valid = source_def is not None and source_def["kind"] == "volume-sum"
    source_values = reports.get("p8-dpm-mass-source-total", {})
    source = ({"status": "DIMENSIONALLY_VALID", "field": source_def["field"],
               "last500_mean_kg_s": float(np.mean([source_values[i] for i in points]))}
              if source_valid and set(points).issubset(source_values) else
              {"status": "INVALID_VOLUME_INTEGRAL_OR_UNAVAILABLE",
               "reason": "Fluent's DPM Mass Source is a per-cell kg/s exchange rate; use Volume Sum."})
    result = {
        "manifest": str(args.manifest), "native_window": [int(points[0]), end],
        "observed": {
            "eulerian_feed_mean_kg_s": float(np.mean(inlet)),
            "eulerian_mean_abs_boundary_gap_kg_s": float(np.mean(np.abs(gap))),
            "eulerian_mean_abs_boundary_gap_fraction_of_feed":
                float(np.mean(np.abs(gap)) / np.mean(inlet)),
            "eulerian_terminal_boundary_gap_kg_s": float(gap[-1]),
            "terminal_phase2_steamoutlet_kg_s": -reports[needed[3]][end],
            "phase2_inventory_start_end_kg": [float(inventory[0]), float(inventory[-1])],
            "phase2_inventory_slope_kg_per_steady_iteration": slope,
            "continuity_residual_range": [float(np.min(r)), float(np.max(r))],
            "dpm_source": source,
        },
        "checks": checks,
        "eulerian_carrier_window_pass": all(checks.values()),
        "tracking_status": run.get("tracking_status", "NOT_RUN"),
        "claim_limit": "Steady-iteration inventory slope is not a physical storage rate. Eulerian balance alone omits incomplete particle fates and does not qualify whole-system carryover.",
    }
    if "particle_tracks" in run:
        tracks = run["particle_tracks"].get("results", [])
        result["tracked_particle_counts"] = {
            key: sum(int(item.get("counts", {}).get(key, 0) or 0) for item in tracks)
            for key in ("tracked", "escaped", "trapped", "incomplete")}
        parent = json.loads(Path(run["source_receipt"]).read_text(encoding="utf-8"))
        flows = parent["reopened"]["dpm_flows_kg_s"]
        if all(item.get("status") == "ok" and int(item["counts"]["tracked"]) > 0
               and item["name"] in flows for item in tracks):
            fate_flows = {
                fate: sum(float(flows[item["name"]]) * int(item["counts"][fate]) /
                          int(item["counts"]["tracked"]) for item in tracks)
                for fate in ("escaped", "trapped", "incomplete")}
            result["represented_particle_fate_kg_s"] = fate_flows
            result["represented_particle_fate_fraction"] = {
                fate: value / sum(float(v) for v in flows.values())
                for fate, value in fate_flows.items()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
