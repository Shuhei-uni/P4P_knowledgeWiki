#!/usr/bin/env python3
"""Plot the 900k checkpoint liquid-inventory and pressure diagnostic."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mesh_convergence_20260801"
    / "mesh_900k"
    / "checkpoint_liquid_inventory"
)
INPUT = DATA_DIR / "liquid_inventory_checkpoints.csv"
OUTPUT = DATA_DIR / "liquid_inventory_pressure_checkpoint_diagnostic.png"


def style_axis(axis: plt.Axes) -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#626B73")
    axis.grid(axis="y", color="#D9DEE3", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(colors="#374047")


def main() -> int:
    frame = pd.read_csv(INPUT).sort_values("iteration")
    x = frame["iteration"]
    blue = "#1769AA"
    orange = "#D97706"

    figure, axes = plt.subplots(1, 2, figsize=(10.5, 5.4))
    figure.patch.set_facecolor("white")
    figure.suptitle(
        "900k checkpoint liquid inventory and pressure drop",
        fontsize=15,
        fontweight="semibold",
        color="#1F2933",
        y=0.97,
    )
    figure.text(
        0.5,
        0.91,
        "Four saved steady-solver states; bottom remains a wall and DPM is off",
        ha="center",
        fontsize=9.5,
        color="#5B6570",
    )

    panels = (
        (axes[0], frame["liquid_inventory_kg"], "Liquid inventory", "kg", blue, "{:.1f}"),
        (axes[1], frame["pressure_drop_pa"] / 1000.0, "Pressure drop", "kPa", orange, "{:.2f}"),
    )
    for axis, values, title, unit, color, label_format in panels:
        axis.plot(x, values, color=color, linewidth=2.2, marker="o", markersize=6)
        for iteration, value in zip(x, values, strict=True):
            axis.annotate(
                label_format.format(value),
                (iteration, value),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                color="#263238",
            )
        axis.set_title(title, fontsize=12, color="#1F2933", pad=9)
        axis.set_xlabel("Solver iteration checkpoint")
        axis.set_ylabel(unit)
        axis.set_xticks(x)
        axis.margins(x=0.08, y=0.2)
        style_axis(axis)

    figure.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.80, wspace=0.30)
    figure.text(
        0.01,
        0.035,
        "Source: Fluent volume integral of phase-2-vof and checkpoint pressure reports.",
        fontsize=8,
        color="#6B7280",
    )
    figure.savefig(OUTPUT, dpi=200, facecolor="white")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
