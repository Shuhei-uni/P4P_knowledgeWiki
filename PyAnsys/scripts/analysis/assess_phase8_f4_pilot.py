#!/usr/bin/env python3
"""Assess a provisional F4 pilot without treating steady iterations as time."""
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
    if run["status"] != "COMPLETE" or run["family"] != "F4":
        raise RuntimeError("F4 pilot has not completed")
    end = int(run["checkpoints"][-1]["native_iteration"])
    points = np.arange(end - 500, end + 1, 10)
    reports = {name: history(path) for name, path in run["report_paths"].items()}
    names = ("p8-flux-mixture-liquidinlet", "p8-flux-mixture-steaminlet",
             "p8-flux-mixture-steamoutlet", "p8-flux-phase2-steamoutlet",
             "p8-mass-phase2-total", "p8-ewf-film-mass-total",
             "p8-ewf-thickness-max", "p8-ewf-stripped-mass-total")
    for name in names:
        missing = set(points) - reports[name].keys()
        if missing:
            raise RuntimeError(f"{name} missing coordinates {sorted(missing)[:5]}")
    inlet = np.array([reports[names[0]][i] + reports[names[1]][i] for i in points])
    outlet = np.array([reports[names[2]][i] for i in points])
    gap = inlet + outlet
    liquid = np.array([reports[names[4]][i] for i in points])
    film = np.array([reports[names[5]][i] for i in points])
    thickness = np.array([reports[names[6]][i] for i in points])
    stripped = np.array([reports[names[7]][i] for i in points])
    transcript = Path(run["paths"]["transcript"]).read_text(encoding="utf-8")
    residuals = {int(i): float(v) for i, v in RESIDUAL.findall(transcript)}
    missing = set(range(end - 499, end + 1)) - residuals.keys()
    if missing:
        raise RuntimeError(f"Missing residual coordinates {sorted(missing)[:5]}")
    continuity = np.array([residuals[i] for i in range(end - 499, end + 1)])
    slope = float(np.polyfit(points, liquid, 1)[0])
    checks = {
        "eulerian_mean_abs_gap_le_1pct_feed": float(np.mean(np.abs(gap))) <=
        float(np.mean(inlet)) * 0.01,
        "liquid_inventory_slope_abs_le_0p01_kg_per_iteration": abs(slope) <= 0.01,
        "continuity_residual_below_0p02": bool(np.max(continuity) < 0.02),
        "no_fatal_solver_event": not bool(FATAL.search(transcript)),
    }
    result = {
        "manifest": str(args.manifest), "native_window": [int(points[0]), end],
        "checks": checks, "operational_carrier_window_pass": all(checks.values()),
        "observed": {
            "eulerian_feed_mean_kg_s": float(np.mean(inlet)),
            "eulerian_mean_abs_boundary_gap_kg_s": float(np.mean(np.abs(gap))),
            "eulerian_mean_abs_boundary_gap_fraction_of_feed":
                float(np.mean(np.abs(gap)) / np.mean(inlet)),
            "eulerian_terminal_boundary_gap_kg_s": float(gap[-1]),
            "terminal_phase2_steamoutlet_kg_s": -float(reports[names[3]][end]),
            "phase2_inventory_start_end_kg": [float(liquid[0]), float(liquid[-1])],
            "phase2_inventory_slope_kg_per_steady_iteration": slope,
            "continuity_residual_range": [float(np.min(continuity)),
                                          float(np.max(continuity))],
            "ewf_film_mass_start_end_kg": [float(film[0]), float(film[-1])],
            "ewf_max_thickness_range_m": [float(np.min(thickness)),
                                          float(np.max(thickness))],
            "ewf_stripped_mass_start_end_kg": [float(stripped[0]),
                                                float(stripped[-1])],
        },
        "claim_limit": "Provisional E2.7 film setup on a carrier whose matched F3 pilot failed its gate. Film mass and transfer reports must not be converted from steady carrier iterations into a physical whole-system storage rate; unresolved DPM and unavailable film DPM mass-source report limit closure.",
    }
    for key, field in (("p8-ewf-outflow-mass-total", "ewf_outflow_mass_start_end_kg"),
                       ("p8-ewf-secondary-phase-mass-total", "ewf_phase2_mass_start_end_kg")):
        if key in reports and set(points).issubset(reports[key]):
            result["observed"][field] = [float(reports[key][points[0]]),
                                         float(reports[key][points[-1]])]
    source_name = "p8-dpm-mass-source-total"
    if source_name in reports and set(points).issubset(reports[source_name]):
        definition = run["report_definitions"][source_name]
        result["observed"]["dpm_mass_source"] = {
            "status": "DIMENSIONALLY_VALID" if definition["kind"] == "volume-sum"
            else "INVALID_REPORT_TYPE",
            "last500_mean_kg_s": float(np.mean([reports[source_name][i] for i in points])),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
