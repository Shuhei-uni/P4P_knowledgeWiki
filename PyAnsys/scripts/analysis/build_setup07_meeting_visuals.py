#!/usr/bin/env python3
"""Build the setup-07a/07b/07c meeting visual evidence pack.

The figures are static, reproducible exports for the 2026-08-11 supervisor
meeting.  They preserve the distinction between a steady-solver mass defect
and a physical accumulation rate: the former is labelled "unclosed liquid
rate" and is not presented as kg/s of physical transient accumulation.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"

CHECKPOINT_CSV = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mesh_convergence_20260801"
    / "mesh_900k"
    / "checkpoint_liquid_inventory"
    / "liquid_inventory_checkpoints.csv"
)
SETUP07B_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_constant_water_level_sink_20260807"
    / "mesh-900k_tau0p100_qualification_v1"
)
SETUP07C_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_thickened_water_level_sink_20260808"
    / "mesh-900k_band0p140165_tau0p100_v1"
)

BLUE = "#1769AA"
ORANGE = "#D97706"
GOLD = "#C49A00"
INK = "#1F2933"
MID = "#5B6570"
GRID = "#D9DEE3"
LIGHT_BLUE = "#A9CCE8"
LIGHT_ORANGE = "#F2C38B"
LIGHT_GREY = "#D5DADF"
WHITE = "#FFFFFF"
FAIL = "#B45309"


def set_style() -> None:
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


def style_axis(axis: plt.Axes, *, grid_axis: str = "y") -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#626B73")
    axis.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)


def add_footer(figure: plt.Figure, text: str) -> None:
    figure.text(0.01, 0.012, text, fontsize=8, color="#6B7280", ha="left")


def save_figure(figure: plt.Figure, stem: str) -> dict[str, str]:
    png = OUTPUT_DIR / f"{stem}.png"
    svg = OUTPUT_DIR / f"{stem}.svg"
    figure.savefig(png, dpi=240)
    figure.savefig(svg)
    plt.close(figure)
    return {"png": str(png), "svg": str(svg)}


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    checkpoints = pd.read_csv(CHECKPOINT_CSV).sort_values("iteration")
    setup07b = pd.read_csv(SETUP07B_DIR / "physical_monitor_history.csv")
    setup07c = pd.read_csv(SETUP07C_DIR / "physical_monitor_history.csv")
    residual07b = pd.read_csv(SETUP07B_DIR / "residual_history.csv")
    residual07c = pd.read_csv(SETUP07C_DIR / "residual_history.csv")
    return checkpoints, setup07b, setup07c, residual07b, residual07c


def closed_bottom_figure(checkpoints: pd.DataFrame) -> dict[str, str]:
    x = checkpoints["iteration"]
    inventory = checkpoints["liquid_inventory_kg"]
    pressure = checkpoints["pressure_drop_pa"] / 1000.0
    inventory_change = 100.0 * (inventory.iloc[-1] / inventory.iloc[0] - 1.0)
    pressure_change = 100.0 * (pressure.iloc[-1] / pressure.iloc[0] - 1.0)

    figure, axes = plt.subplots(1, 2, figsize=(11.2, 5.7))
    figure.suptitle("Closed-bottom 900k solution keeps changing with iteration", fontsize=16, fontweight="semibold", y=0.975)
    figure.text(
        0.5,
        0.918,
        "Saved Fluent states at iterations 4000–6000; no brine discharge and DPM off",
        ha="center",
        fontsize=10,
        color=MID,
    )

    panels = (
        (axes[0], inventory, "Liquid inventory", "kg", BLUE, inventory_change, "+{:.1f}%"),
        (axes[1], pressure, "Pressure drop", "kPa", ORANGE, pressure_change, "+{:.1f}%"),
    )
    for axis, values, title, unit, color, change, change_format in panels:
        axis.plot(x, values, color=color, linewidth=2.5, marker="o", markersize=7)
        axis.fill_between(x, values, values.min() * 0.96, color=color, alpha=0.08)
        for iteration, value in zip(x, values, strict=True):
            axis.annotate(f"{value:.1f}" if unit == "kg" else f"{value:.2f}", (iteration, value), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=9)
        axis.set_title(title, fontweight="semibold")
        axis.set_xlabel("Solver iteration")
        axis.set_ylabel(unit)
        axis.set_xticks(x)
        axis.margins(x=0.07, y=0.22)
        style_axis(axis)
        axis.text(
            0.96,
            0.08,
            change_format.format(change),
            transform=axis.transAxes,
            ha="right",
            va="bottom",
            fontsize=18,
            fontweight="bold",
            color=color,
        )
        axis.text(0.96, 0.02, "between 4000 and 6000", transform=axis.transAxes, ha="right", va="bottom", fontsize=8.5, color=MID)

    figure.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.80, wspace=0.28)
    add_footer(figure, "Source: saved 900k Fluent case/data checkpoints; phase-2 volume integral and pressure reports.")
    return save_figure(figure, "01_closed_bottom_inventory_pressure")


def matched_sink_figure(setup07b: pd.DataFrame, setup07c: pd.DataFrame) -> dict[str, str]:
    matched_iterations = [1000, 1250, 1500, 1750, 2000]
    b = setup07b[setup07b["r1_iteration"].isin(matched_iterations)].drop_duplicates("r1_iteration", keep="last").set_index("r1_iteration").loc[matched_iterations]
    c = setup07c[setup07c["r1_iteration"].isin(matched_iterations)].drop_duplicates("r1_iteration", keep="last").set_index("r1_iteration").loc[matched_iterations]

    figure, axes = plt.subplots(1, 2, figsize=(11.2, 5.8))
    figure.suptitle("A thicker sink removes more liquid, but the field still does not stabilize", fontsize=15.5, fontweight="semibold", y=0.975)
    figure.text(0.5, 0.918, "Matched full-strength iterations; same 900k mesh, tau = 0.1 s and carrier setup", ha="center", fontsize=10, color=MID)

    x = np.asarray(matched_iterations)
    series = (
        (axes[0], "sink_magnitude_kgs", "Liquid sink magnitude", "kg/s"),
        (axes[1], "domain_liquid_inventory_kg", "Domain liquid inventory", "kg"),
    )
    for axis, field, title, unit in series:
        axis.plot(x, b[field], color=BLUE, linewidth=2.3, marker="o", markersize=6, label="07b: one-cell layer")
        axis.plot(x, c[field], color=ORANGE, linewidth=2.3, marker="s", markersize=6, linestyle="--", label="07c: 16-layer band")
        axis.set_title(title, fontweight="semibold")
        axis.set_xlabel("Full-strength iteration (R = 1)")
        axis.set_ylabel(unit)
        axis.set_xticks(x)
        axis.margins(x=0.05, y=0.18)
        style_axis(axis)
    axes[0].axhline(116.92, color=INK, linestyle=":", linewidth=1.5, label="Liquid inlet: 116.92 kg/s")
    axes[0].text(1995, 113.0, "required inlet rate", ha="right", va="top", fontsize=8.5, color=INK)
    axes[0].set_ylim(0, 128)
    axes[0].legend(frameon=False, fontsize=8.8, loc="upper left", bbox_to_anchor=(0.01, 0.79))
    axes[1].legend(frameon=False, fontsize=8.8, loc="upper left")
    axes[0].annotate("22.49 kg/s\n(19.2% of inlet)", (2000, c.loc[2000, "sink_magnitude_kgs"]), xytext=(-62, 24), textcoords="offset points", arrowprops={"arrowstyle": "->", "color": ORANGE}, color=ORANGE, fontsize=9, ha="center")

    figure.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.80, wspace=0.28)
    add_footer(figure, "Source: setup-07b and setup-07c physical_monitor_history.csv; no DPM. Inventory is a phase-2 volume integral.")
    return save_figure(figure, "02_sink_thickness_matched_iteration")


def thick_sink_drift_figure(setup07c: pd.DataFrame) -> dict[str, str]:
    frame = setup07c[setup07c["r1_iteration"] > 0].drop_duplicates("r1_iteration", keep="last").sort_values("r1_iteration")
    x = frame["r1_iteration"]
    figure, axes = plt.subplots(1, 3, figsize=(14.0, 5.5))
    figure.suptitle("Setup 07c remains iteration-dependent at full sink strength", fontsize=16, fontweight="semibold", y=0.975)
    figure.text(0.5, 0.918, "Full-strength R = 1 samples; endpoint is diagnostic, not a converged operating point", ha="center", fontsize=10, color=MID)

    panels = (
        (axes[0], frame["pressure_drop_pa"] / 1000.0, "Pressure drop", "kPa", ORANGE),
        (axes[1], frame["domain_liquid_inventory_kg"], "Liquid inventory", "kg", BLUE),
        (axes[2], frame["sink_magnitude_kgs"], "Sink magnitude", "kg/s", GOLD),
    )
    for axis, values, title, unit, color in panels:
        axis.plot(x, values, color=color, linewidth=2.3, marker="o", markersize=5)
        axis.set_title(title, fontweight="semibold")
        axis.set_xlabel("Full-strength iteration")
        axis.set_ylabel(unit)
        axis.set_xticks([250, 750, 1250, 1750, 2000])
        axis.margins(x=0.05, y=0.18)
        style_axis(axis)
        axis.annotate(f"{values.iloc[-1]:.2f}", (x.iloc[-1], values.iloc[-1]), xytext=(-4, 9), textcoords="offset points", ha="right", fontsize=9, color=color, fontweight="semibold")

    figure.subplots_adjust(left=0.065, right=0.99, bottom=0.17, top=0.79, wspace=0.30)
    add_footer(figure, "Source: setup-07c physical monitor history. Final-500 drift: pressure 8.53%, inventory 16.93%, sink 29.99%.")
    return save_figure(figure, "03_setup07c_full_strength_drift")


def closure_frame(checkpoints: pd.DataFrame, setup07b: pd.DataFrame, setup07c: pd.DataFrame) -> pd.DataFrame:
    closed = checkpoints.iloc[-1]
    b = setup07b.iloc[-1]
    c = setup07c.iloc[-1]
    rows = [
        {
            "case": "Closed bottom\n900k, iter 6000",
            "liquid_inlet_kgs": 116.92,
            "liquid_outlet_kgs": abs(float(closed["liquid_steamoutlet_kgs"])),
            "udf_sink_kgs": 0.0,
        },
        {
            "case": "07b one-cell sink\nR1 = 6000",
            "liquid_inlet_kgs": 116.92,
            "liquid_outlet_kgs": abs(float(b["liquid_steamoutlet_kgs"])),
            "udf_sink_kgs": float(b["sink_magnitude_kgs"]),
        },
        {
            "case": "07c thick sink\nR1 = 2000",
            "liquid_inlet_kgs": 116.92,
            "liquid_outlet_kgs": abs(float(c["liquid_steamoutlet_kgs"])),
            "udf_sink_kgs": float(c["sink_magnitude_kgs"]),
        },
    ]
    frame = pd.DataFrame(rows)
    frame["unclosed_liquid_rate_kgs"] = (
        frame["liquid_inlet_kgs"] - frame["liquid_outlet_kgs"] - frame["udf_sink_kgs"]
    ).clip(lower=0.0)
    frame["accounted_fraction_percent"] = 100.0 * (
        frame["liquid_outlet_kgs"] + frame["udf_sink_kgs"]
    ) / frame["liquid_inlet_kgs"]
    return frame


def liquid_closure_figure(frame: pd.DataFrame) -> dict[str, str]:
    figure, axis = plt.subplots(figsize=(10.6, 6.2))
    figure.suptitle("Most of the liquid inlet has no steady discharge route", fontsize=16, fontweight="semibold", y=0.975)
    figure.text(0.5, 0.920, "Endpoint liquid-rate accounting relative to the fixed 116.92 kg/s inlet", ha="center", fontsize=10, color=MID)

    y = np.arange(len(frame))
    left = np.zeros(len(frame))
    components = (
        ("liquid_outlet_kgs", "Liquid through steam outlet", BLUE),
        ("udf_sink_kgs", "UDF liquid sink", ORANGE),
        ("unclosed_liquid_rate_kgs", "Unclosed liquid rate", LIGHT_GREY),
    )
    for field, label, color in components:
        values = frame[field].to_numpy()
        axis.barh(y, values, left=left, height=0.56, color=color, edgecolor=WHITE, linewidth=1.0, label=label)
        for index, (start, value) in enumerate(zip(left, values, strict=True)):
            if value >= 6.0:
                axis.text(start + value / 2.0, index, f"{value:.1f}", ha="center", va="center", fontsize=9, color=INK, fontweight="semibold")
        left += values

    for index, row in frame.iterrows():
        axis.text(119.5, index, f"{row['accounted_fraction_percent']:.1f}% removed", va="center", fontsize=9, color=FAIL, fontweight="semibold")
    axis.set_yticks(y, frame["case"])
    axis.invert_yaxis()
    axis.set_xlim(0, 137)
    axis.set_xlabel("Liquid rate (kg/s)")
    axis.axvline(116.92, color=INK, linewidth=1.2, linestyle=":")
    axis.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.28), fontsize=9)
    style_axis(axis, grid_axis="x")
    axis.spines["left"].set_visible(False)
    axis.tick_params(axis="y", length=0)
    figure.subplots_adjust(left=0.22, right=0.985, bottom=0.25, top=0.80)
    add_footer(figure, "Unclosed rate is a steady-solver source-inclusive mass defect, not a physical transient accumulation rate. DPM is off.")
    return save_figure(figure, "04_endpoint_liquid_rate_closure")


def residual_figure(residual07c: pd.DataFrame) -> dict[str, str]:
    figure, axes = plt.subplots(1, 2, figsize=(11.4, 5.9))
    figure.suptitle("Residuals do not support an accepted steady setup-07c solution", fontsize=15.5, fontweight="semibold", y=0.975)
    figure.text(0.5, 0.918, "Guarded ramp ends at total iteration 1000; full-strength sink continues to total iteration 3000", ha="center", fontsize=10, color=MID)

    axes[0].plot(residual07c["iteration"], residual07c["continuity"], color=ORANGE, linewidth=1.4)
    axes[0].axhline(1e-3, color=INK, linestyle=":", linewidth=1.2, label="Acceptance level: 1e-3")
    axes[0].axvline(1000, color=MID, linestyle="--", linewidth=1.0)
    axes[0].set_yscale("log")
    axes[0].set_title("Continuity residual", fontweight="semibold")
    axes[0].set_xlabel("Total solver iteration")
    axes[0].set_ylabel("Scaled residual")
    axes[0].legend(frameon=False, fontsize=8.8, loc="lower left")
    style_axis(axes[0])
    axes[0].annotate("final 0.192", (3000, residual07c.iloc[-1]["continuity"]), xytext=(-55, 20), textcoords="offset points", arrowprops={"arrowstyle": "->", "color": ORANGE}, color=ORANGE, fontsize=9)

    for field, label, color, style in (
        ("vf-phase-2", "Liquid volume fraction", BLUE, "-"),
        ("epsilon", "Epsilon", ORANGE, "--"),
        ("k", "Turbulent kinetic energy", GOLD, "-."),
        ("x-velocity", "Velocity residual (x)", INK, ":"),
    ):
        axes[1].plot(residual07c["iteration"], residual07c[field], label=label, color=color, linestyle=style, linewidth=1.2)
    axes[1].axhline(1e-3, color=MID, linestyle=":", linewidth=1.2)
    axes[1].axvline(1000, color=MID, linestyle="--", linewidth=1.0)
    axes[1].set_yscale("log")
    axes[1].set_title("Other monitored residuals", fontweight="semibold")
    axes[1].set_xlabel("Total solver iteration")
    axes[1].set_ylabel("Scaled residual")
    axes[1].legend(frameon=False, fontsize=8.2, loc="best")
    style_axis(axes[1])

    figure.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.79, wspace=0.28)
    add_footer(figure, "Source: setup-07c residual_history.csv. Residual stability alone is insufficient while pressure and liquid inventory drift.")
    return save_figure(figure, "05_setup07c_residual_history")


def storyboard_figure(checkpoints: pd.DataFrame, setup07b: pd.DataFrame, setup07c: pd.DataFrame, closure: pd.DataFrame) -> dict[str, str]:
    figure, axes = plt.subplots(2, 2, figsize=(13.2, 9.0))
    figure.suptitle("Why the current separator model cannot reach a steady mesh-independent state", fontsize=17, fontweight="semibold", y=0.985)
    figure.text(0.5, 0.945, "Meeting summary • split-inlet 900k carrier evidence • DPM off", ha="center", fontsize=10.5, color=MID)

    axis = axes[0, 0]
    axis.plot(checkpoints["iteration"], checkpoints["liquid_inventory_kg"], color=BLUE, linewidth=2.5, marker="o")
    axis.set_title("1. Closed bottom: liquid inventory rises", fontweight="semibold")
    axis.set_xlabel("Solver iteration")
    axis.set_ylabel("Liquid inventory (kg)")
    axis.set_xticks(checkpoints["iteration"])
    style_axis(axis)
    axis.annotate("+64.4%", (6000, checkpoints.iloc[-1]["liquid_inventory_kg"]), xytext=(-12, -24), textcoords="offset points", fontsize=11, color=BLUE, fontweight="bold", ha="right")

    axis = axes[0, 1]
    axis.plot(checkpoints["iteration"], checkpoints["pressure_drop_pa"] / 1000.0, color=ORANGE, linewidth=2.5, marker="o")
    axis.set_title("2. Pressure changes with the filling field", fontweight="semibold")
    axis.set_xlabel("Solver iteration")
    axis.set_ylabel("Pressure drop (kPa)")
    axis.set_xticks(checkpoints["iteration"])
    style_axis(axis)
    axis.annotate("+9.7%", (6000, checkpoints.iloc[-1]["pressure_drop_pa"] / 1000.0), xytext=(-12, -24), textcoords="offset points", fontsize=11, color=ORANGE, fontweight="bold", ha="right")

    axis = axes[1, 0]
    b = setup07b[setup07b["r1_iteration"].isin([1000, 1500, 2000])].drop_duplicates("r1_iteration", keep="last").set_index("r1_iteration")
    c = setup07c[setup07c["r1_iteration"].isin([1000, 1500, 2000])].drop_duplicates("r1_iteration", keep="last").set_index("r1_iteration")
    x = [1000, 1500, 2000]
    axis.plot(x, b.loc[x, "sink_magnitude_kgs"], color=BLUE, linewidth=2.3, marker="o", label="07b one cell")
    axis.plot(x, c.loc[x, "sink_magnitude_kgs"], color=ORANGE, linewidth=2.3, marker="s", linestyle="--", label="07c thick band")
    axis.axhline(116.92, color=INK, linestyle=":", linewidth=1.2, label="liquid inlet")
    axis.set_title("3. Thickening helps, but sink is still too small", fontweight="semibold")
    axis.set_xlabel("Full-strength iteration")
    axis.set_ylabel("Sink magnitude (kg/s)")
    axis.set_xticks(x)
    axis.legend(frameon=False, fontsize=8.3, loc="upper left")
    style_axis(axis)

    axis = axes[1, 1]
    rows = closure.iloc[[0, 2]]
    y = np.arange(len(rows))
    left = np.zeros(len(rows))
    for field, label, color in (
        ("liquid_outlet_kgs", "outlet", BLUE),
        ("udf_sink_kgs", "sink", ORANGE),
        ("unclosed_liquid_rate_kgs", "unclosed", LIGHT_GREY),
    ):
        values = rows[field].to_numpy()
        axis.barh(y, values, left=left, height=0.52, color=color, edgecolor=WHITE, label=label)
        left += values
    axis.set_yticks(y, ["Closed bottom", "07c thick sink"])
    axis.invert_yaxis()
    axis.set_title("4. Most liquid still lacks a discharge route", fontweight="semibold")
    axis.set_xlabel("Liquid rate (kg/s)")
    axis.legend(frameon=False, fontsize=8.3, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.32))
    style_axis(axis, grid_axis="x")
    axis.spines["left"].set_visible(False)
    axis.tick_params(axis="y", length=0)

    figure.text(
        0.5,
        0.035,
        "Decision: retain the current runs as diagnostic evidence and qualify a resolved brine outlet before repeating mesh convergence or adding DPM/EWF.",
        ha="center",
        fontsize=10.5,
        color=INK,
        fontweight="semibold",
    )
    figure.subplots_adjust(left=0.08, right=0.985, bottom=0.105, top=0.885, hspace=0.38, wspace=0.27)
    return save_figure(figure, "00_meeting_storyboard")


def main() -> int:
    set_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoints, setup07b, setup07c, residual07b, residual07c = load_inputs()
    closure = closure_frame(checkpoints, setup07b, setup07c)
    closure.to_csv(OUTPUT_DIR / "endpoint_liquid_rate_closure.csv", index=False)

    artifacts: dict[str, dict[str, str]] = {}
    artifacts["storyboard"] = storyboard_figure(checkpoints, setup07b, setup07c, closure)
    artifacts["closed_bottom"] = closed_bottom_figure(checkpoints)
    artifacts["matched_sink"] = matched_sink_figure(setup07b, setup07c)
    artifacts["thick_sink_drift"] = thick_sink_drift_figure(setup07c)
    artifacts["liquid_closure"] = liquid_closure_figure(closure)
    artifacts["residuals"] = residual_figure(residual07c)

    manifest = {
        "study": "setup07_meeting_visuals_20260811",
        "purpose": "meeting-ready diagnostic visual evidence before brine-outlet geometry changes",
        "takeaway": "The imposed vapor path is stable, but liquid inventory, pressure and sink capacity remain iteration-dependent because the current domain lacks a qualified liquid discharge route.",
        "source_files": [
            str(CHECKPOINT_CSV),
            str(SETUP07B_DIR / "physical_monitor_history.csv"),
            str(SETUP07B_DIR / "residual_history.csv"),
            str(SETUP07C_DIR / "physical_monitor_history.csv"),
            str(SETUP07C_DIR / "residual_history.csv"),
            str(SETUP07C_DIR / "analysis_correction.json"),
        ],
        "artifacts": artifacts,
        "data_exports": [str(OUTPUT_DIR / "endpoint_liquid_rate_closure.csv")],
        "limitations": [
            "All plotted Fluent endpoints are diagnostic and not iteration-independent steady solutions.",
            "Unclosed liquid rate is a steady-solver mass defect, not a physical transient accumulation rate.",
            "Steam-outlet quality is trend-only because no resolved brine outlet exists.",
            "DPM was off and no separator-efficiency claim is made.",
        ],
    }
    (OUTPUT_DIR / "visual_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(OUTPUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
