#!/usr/bin/env python3
"""Build a dynamic one-page Tuesday action summary for setup 07."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mass_balance_sink_control_20260810"
    / "mesh-900k_band0p140165_target116p92_v1"
)
SETUP07D_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_strong_sink_sensitivity_20260810"
    / "mesh-900k_band0p140165_tau0p020_v1"
)
OUTPUT_DIR = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"
VISUAL_MANIFEST_PATH = OUTPUT_DIR / "visual_manifest.json"

BLUE = "#1769AA"
ORANGE = "#D97706"
GOLD = "#C49A00"
INK = "#1F2933"
MID = "#5B6570"
GRID = "#D9DEE3"
LIGHT_GREY = "#D5DADF"
PALE_BLUE = "#E8F1F8"
PALE_ORANGE = "#FFF1DF"
WHITE = "#FFFFFF"


def style_axis(axis: plt.Axes, *, grid_axis: str = "x") -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#626B73")
    axis.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)


def load_evidence() -> tuple[pd.Series, pd.Series, dict]:
    current = (
        pd.read_csv(RUN_DIR / "physical_monitor_history.csv")
        .drop_duplicates("iteration", keep="last")
        .sort_values("iteration")
        .iloc[-1]
    )
    fixed = (
        pd.read_csv(SETUP07D_DIR / "physical_monitor_history.csv")
        .drop_duplicates("iteration", keep="last")
        .sort_values("iteration")
        .iloc[-1]
    )
    manifest = json.loads((RUN_DIR / "qualification_manifest.json").read_text(encoding="utf-8"))
    return current, fixed, manifest


def main() -> int:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "axes.edgecolor": MID,
            "axes.labelcolor": INK,
            "xtick.color": "#374047",
            "ytick.color": "#374047",
            "text.color": INK,
            "figure.facecolor": WHITE,
            "axes.facecolor": WHITE,
            "savefig.facecolor": WHITE,
            "savefig.bbox": "tight",
        }
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    current, fixed, manifest = load_evidence()
    target = float(manifest.get("adaptive_target_liquid_sink_kgs", 116.92))
    tau_min = float(manifest.get("adaptive_tau_bounds_s", [0.002, 0.2])[0])
    required_band = target * tau_min
    band = float(current["bottom_layer_liquid_inventory_kg"])
    density = float(
        manifest["settings_readback"]["materials"]["fluid"]
        ["water-liquid-at-psep"]["density"]["value"]
    )
    status = str(manifest.get("status", "unknown"))
    current_r1 = int(current["r1_iteration"])

    figure, axes = plt.subplots(2, 2, figsize=(12.2, 8.2))
    figure.suptitle(
        "Tuesday action summary: resolve the brine outlet next",
        fontsize=17,
        fontweight="semibold",
        y=0.985,
    )
    figure.text(
        0.5,
        0.947,
        f"Setup 07e {status} through R=1 iteration {current_r1} • same clean 900k carrier • DPM/EWF off",
        ha="center",
        fontsize=9.7,
        color=MID,
    )

    axis = axes[0, 0]
    labels = ["Closed bottom\niter 6000", "07d fixed sink\nR1=2000", f"07e adaptive\nR1={current_r1}"]
    routed = np.array(
        [
            2.4,
            100.0 * float(fixed["sink_magnitude_kgs"]) / target,
            100.0 * float(current["sink_magnitude_kgs"]) / target,
        ]
    )
    unclosed = 100.0 - routed
    y = np.arange(len(labels))
    axis.barh(y, routed, color=ORANGE, edgecolor=WHITE, label="represented route")
    axis.barh(y, unclosed, left=routed, color=LIGHT_GREY, edgecolor=WHITE, label="unclosed steady rate")
    for index, value in enumerate(routed):
        axis.text(value + 1.2, index, f"{value:.1f}% routed", va="center", fontsize=8.6, color=INK, fontweight="semibold")
    axis.set_yticks(y, labels)
    axis.invert_yaxis()
    axis.set_xlim(0.0, 108.0)
    axis.set_xlabel("Liquid feed accounting (%)")
    axis.set_title("No tested surrogate provides a complete liquid route", fontweight="semibold")
    axis.legend(frameon=False, fontsize=7.8, loc="lower right")
    style_axis(axis)

    axis = axes[0, 1]
    values = [band, required_band]
    bars = axis.bar(
        ["available in band", "required at tau floor"],
        values,
        color=[BLUE, PALE_BLUE],
        edgecolor=[BLUE, BLUE],
        linewidth=1.2,
    )
    axis.bar_label(bars, labels=[f"{band:.5f} kg", f"{required_band:.5f} kg"], padding=4, fontsize=8.8)
    axis.set_ylim(0.0, required_band * 1.18)
    axis.set_ylabel("Liquid inventory (kg)")
    axis.set_title("Adaptive source is saturated at minimum tau", fontweight="semibold")
    axis.text(
        0.5,
        0.84,
        f"current capacity = {100.0 * band / required_band:.1f}%",
        transform=axis.transAxes,
        ha="center",
        fontsize=9,
        color=ORANGE,
        fontweight="semibold",
    )
    style_axis(axis, grid_axis="y")

    axis = axes[1, 0]
    velocities = np.array([1.0, 2.0, 3.0])
    volumetric_flow = target / density
    diameters = np.sqrt(4.0 * volumetric_flow / (math.pi * velocities))
    bars = axis.bar(
        ["1 m/s", "2 m/s", "3 m/s"],
        diameters,
        color=BLUE,
        edgecolor="#0E4774",
        linewidth=0.9,
    )
    axis.bar_label(bars, labels=[f"{value:.3f} m" for value in diameters], padding=4, fontsize=8.8)
    axis.set_ylim(0.0, max(diameters) * 1.22)
    axis.set_ylabel("Equivalent circular diameter (m)")
    axis.set_title("Continuity-only geometry starting envelope", fontweight="semibold")
    axis.text(
        0.5,
        0.86,
        f"116.92 kg/s at rho={density:.1f} kg/m³",
        transform=axis.transAxes,
        ha="center",
        fontsize=8.8,
        color=MID,
    )
    style_axis(axis, grid_axis="y")

    axis = axes[1, 1]
    axis.set_axis_off()
    cards = (
        (0.03, 0.70, "1  Add resolved brine pipe", "Place the numerical boundary away from vessel recirculation.", PALE_BLUE, BLUE),
        (0.03, 0.40, "2  Pressure-outlet first", "Use a defensible downstream static pressure; let Fluent solve the flow rate.", PALE_BLUE, BLUE),
        (0.03, 0.10, "3  Rate-forced diagnostic only", "Use 116.92 kg/s only if strictly outward; do not call it validated hydraulics.", PALE_ORANGE, ORANGE),
    )
    for x, y0, title, body, face, edge in cards:
        card = FancyBboxPatch(
            (x, y0),
            0.94,
            0.21,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            linewidth=1.2,
            edgecolor=edge,
            facecolor=face,
            transform=axis.transAxes,
        )
        axis.add_patch(card)
        axis.text(x + 0.025, y0 + 0.155, title, transform=axis.transAxes, fontsize=10.3, fontweight="semibold", va="top")
        axis.text(x + 0.025, y0 + 0.090, body, transform=axis.transAxes, fontsize=8.5, va="top", color=INK, wrap=True)
    axis.set_title("Controlled rebuild sequence", fontweight="semibold", pad=8)

    figure.subplots_adjust(left=0.095, right=0.985, bottom=0.12, top=0.87, hspace=0.38, wspace=0.28)
    figure.text(
        0.5,
        0.035,
        "Required acceptance: complete phase/mixture balance, stable liquid inventory and pressure, outward brine flux, stable velocity/swirl and acceptable residual level/trend.",
        ha="center",
        fontsize=8,
        color=MID,
    )
    figure.text(
        0.5,
        0.012,
        "All current states are diagnostic/unresolved. No mesh-independence, separator-efficiency, free-surface or physical-time claim.",
        ha="center",
        fontsize=8,
        color="#A33A2A",
        fontweight="semibold",
    )
    paths: dict[str, str] = {}
    for suffix in ("png", "svg"):
        path = OUTPUT_DIR / f"27_tuesday_brine_outlet_action_summary.{suffix}"
        figure.savefig(path, dpi=240)
        paths[suffix] = str(path)
    plt.close(figure)

    manifest_data = json.loads(VISUAL_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_data.setdefault("artifacts", {})["tuesday_brine_outlet_action_summary"] = paths
    VISUAL_MANIFEST_PATH.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")
    print(paths["png"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
