#!/usr/bin/env python3
"""Plot the spiral-inlet replication against the digitized reference graph."""

from __future__ import annotations

import sys
from pathlib import Path

import plot_enthalpy_steam_quality as steam_quality_plot


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SWEEP_OUTPUT_DIR = PROJECT_ROOT / "output" / "spiral_enthalpy_sweep_20260725"
PLOT_OUTPUT_DIR = SWEEP_OUTPUT_DIR / "plots"
GRAPH_DIGITIZATION_DIR = PROJECT_ROOT / "output" / "graph_digitization"

DEFAULTS = {
    "--injection-results": str(SWEEP_OUTPUT_DIR / "all_enthalpy_injection_results.csv"),
    "--case-summary": str(SWEEP_OUTPUT_DIR / "all_enthalpy_case_summary.csv"),
    "--digitized-points": str(
        GRAPH_DIGITIZATION_DIR / "spiral_inlet_reference_digitized_points.csv"
    ),
    "--output": str(PLOT_OUTPUT_DIR / "spiral_inlet_output_steam_quality.png"),
    "--plot-data-output": str(
        PLOT_OUTPUT_DIR / "spiral_inlet_output_steam_quality_plot_data.csv"
    ),
    "--layout": "single",
    "--title": "Spiral-Inlet Replication: Outlet Steam Quality",
    "--legend-label": "Present Spiral-Inlet CFD Replication",
    "--reference-calculation-label": "Purnanto Spiral-Inlet Calculation",
    "--reference-simulation-label": "Purnanto Spiral-Inlet Simulation",
    "--reference-correlation-label": "Lazalde-Crabtree Correlation",
    "--x-min": "0",
    "--x-max": "80",
    "--x-step": "10",
    "--y-min": "99.4",
    "--y-max": "100",
    "--y-step": "0.1",
}


def apply_defaults(argv: list[str]) -> list[str]:
    result = list(argv)
    present = {argument.split("=", 1)[0] for argument in result if argument.startswith("--")}
    for option, value in DEFAULTS.items():
        if option not in present:
            result.extend((option, value))
    return result


if __name__ == "__main__":
    sys.argv = apply_defaults(sys.argv)
    raise SystemExit(steam_quality_plot.main())
