#!/usr/bin/env python3
"""Render the evidence-qualified F01 residual history versus iteration.

F01 has a complete retained residual history through its final valid checkpoint at
iteration 5,500, but no continuous physical-monitor history.  This builder
therefore emits only the residual figure and a source manifest; it intentionally
does not manufacture the other four Stage-3 figure families.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT_ROOT / "output" / "03a_stage3" / "F01" / "F01-monitor-histories.json"
OUTPUT_ROOT = PROJECT_ROOT / "output" / "03a_stage3" / "iteration-led" / "central" / "f01"
REPORT_ROOT = (
    PROJECT_ROOT.parent
    / "Setups"
    / "reports"
    / "full-geometry"
    / "mixture"
    / "steady-liquid-outlet"
    / "03a"
    / "plots"
    / "03a-stage3"
    / "iteration-led"
    / "central"
    / "f01"
)

RESIDUAL_ORDER = (
    "continuity",
    "x-velocity",
    "y-velocity",
    "z-velocity",
    "k",
    "epsilon",
    "vf-phase-2",
)
COLORS = {
    "continuity": "#2563eb",
    "x-velocity": "#0f766e",
    "y-velocity": "#15803d",
    "z-velocity": "#a16207",
    "k": "#c2410c",
    "epsilon": "#be123c",
    "vf-phase-2": "#7c3aed",
}


def load_verified_history() -> tuple[list[int], dict[str, list[float]]]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    iterations = [int(value) for value in payload["residual_iterations"]]
    if iterations != list(range(1, 5501)):
        raise ValueError("F01 residual iteration coverage is not exactly 1–5500")
    series: dict[str, list[float]] = {}
    for name in RESIDUAL_ORDER:
        values = [float(value) for value in payload["residuals"][name]]
        if len(values) != len(iterations) or not all(math.isfinite(value) and value > 0 for value in values):
            raise ValueError(f"F01 {name} is not a finite positive 5500-point residual series")
        series[name] = values
    return iterations, series


def render(iterations: list[int], series: dict[str, list[float]], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(14, 7), constrained_layout=True)
    for name in RESIDUAL_ORDER:
        axis.plot(iterations, series[name], color=COLORS[name], linewidth=0.9, label=name)
    axis.axvline(5500, color="#991b1b", linestyle="--", linewidth=1.0)
    axis.text(5500, 0.98, "last valid checkpoint: 5,500", transform=axis.get_xaxis_transform(),
              rotation=90, va="top", ha="right", fontsize=8, color="#991b1b")
    axis.set_xlim(0, 5704)
    axis.set_yscale("log")
    axis.set_xlabel("Cumulative Fluent native iteration")
    axis.set_ylabel("Scaled residual")
    axis.set_title("F01 — scaled residuals versus iteration", loc="left", fontweight="bold")
    axis.text(0.01, 0.03, "Full-Mixture 100%; valid residual history 1–5,500. Numerical failure followed at 5,704.",
              transform=axis.transAxes, fontsize=8, color="#4b5563")
    axis.grid(True, which="major", alpha=0.25)
    axis.grid(True, which="minor", linestyle=":", alpha=0.15)
    axis.legend(loc="upper right", ncol=4, frameon=False, fontsize=8)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(figure)


def main() -> int:
    iterations, series = load_verified_history()
    manifest = {
        "branch": "F01",
        "source": str(SOURCE),
        "source_remote_path": r"C:\\Temp\\03A-stage3-F01\\F01-residual-history-all.txt",
        "residual_iteration_range": [1, 5500],
        "last_valid_checkpoint": 5500,
        "failure_iteration": 5704,
        "stage": "full-Mixture 100%",
        "series": {name: len(values) for name, values in series.items()},
        "physical_plot_status": "not generated: only endpoint evidence is available",
        "plot": "figure-01-residuals-vs-iteration.png",
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "f01-iteration-led-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    render(iterations, series, OUTPUT_ROOT / manifest["plot"])
    render(iterations, series, REPORT_ROOT / manifest["plot"])
    print(OUTPUT_ROOT / "f01-iteration-led-manifest.json")
    print(REPORT_ROOT / manifest["plot"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
