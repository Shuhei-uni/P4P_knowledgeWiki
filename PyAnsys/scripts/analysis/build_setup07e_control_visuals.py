#!/usr/bin/env python3
"""Build diagnostic setup-07e control-history figures from saved CSV evidence.

The script is safe to run while the controller is active because it only reads
locally written histories.  It labels the adaptive sink as numerical feedback,
not a physical brine-outlet model.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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
SETUP07C_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_thickened_water_level_sink_20260808"
    / "mesh-900k_band0p140165_tau0p100_v1"
)
OUTPUT_DIR = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"

BLUE = "#1769AA"
ORANGE = "#D97706"
GOLD = "#C49A00"
INK = "#1F2933"
MID = "#5B6570"
GRID = "#D9DEE3"
LIGHT_GREY = "#D5DADF"
WHITE = "#FFFFFF"


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


def save(figure: plt.Figure, stem: str) -> dict[str, str]:
    paths = {}
    for suffix in ("png", "svg"):
        path = OUTPUT_DIR / f"{stem}.{suffix}"
        figure.savefig(path, dpi=240)
        paths[suffix] = str(path)
    plt.close(figure)
    return paths


def load_histories() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    physical = pd.read_csv(RUN_DIR / "physical_monitor_history.csv").drop_duplicates("iteration", keep="last").sort_values("iteration")
    residual = pd.read_csv(RUN_DIR / "residual_history.csv").drop_duplicates("iteration", keep="last").sort_values("iteration")
    manifest = json.loads((RUN_DIR / "qualification_manifest.json").read_text(encoding="utf-8"))
    return physical, residual, manifest


def control_history_figure(physical: pd.DataFrame, manifest: dict) -> dict[str, str]:
    frame = physical.copy()
    frame["commanded_sink_kgs"] = 116.92 * frame["ramp"]
    figure, axes = plt.subplots(2, 2, figsize=(12.2, 8.0))
    figure.suptitle("Setup 07e: adaptive numerical mass-balance control history", fontsize=16, fontweight="semibold", y=0.982)
    figure.text(
        0.5,
        0.943,
        f"{manifest.get('status', 'unknown').title()} diagnostic • clean 900k carrier • feedback every 100 iterations • DPM off",
        ha="center",
        fontsize=10,
        color=MID,
    )

    axis = axes[0, 0]
    axis.step(frame["iteration"], frame["commanded_sink_kgs"], where="post", color=INK, linestyle=":", linewidth=1.8, label="command R × 116.92")
    axis.plot(frame["iteration"], frame["sink_magnitude_kgs"], color=ORANGE, linewidth=2.2, marker="s", markersize=5, label="achieved sink")
    axis.set_title("Commanded versus achieved liquid sink", fontweight="semibold")
    axis.set_xlabel("Total solver iteration")
    axis.set_ylabel("kg/s")
    axis.legend(frameon=False, fontsize=8.5)
    style_axis(axis)

    axis = axes[0, 1]
    axis.step(frame["iteration"], frame["tau_s"], where="post", color=BLUE, linewidth=2.2, marker="o", markersize=4)
    axis.set_yscale("log")
    axis.axhline(0.002, color=MID, linestyle=":", linewidth=1.0)
    axis.axhline(0.2, color=MID, linestyle=":", linewidth=1.0)
    axis.set_title("Feedback time scale", fontweight="semibold")
    axis.set_xlabel("Total solver iteration")
    axis.set_ylabel("tau (s, log scale)")
    style_axis(axis)

    axis = axes[1, 0]
    axis.plot(frame["iteration"], frame["liquid_imbalance_percent"], color=ORANGE, linewidth=2.2, marker="s", markersize=5, label="liquid")
    axis.plot(frame["iteration"], frame["mixture_source_augmented_imbalance_percent"], color=BLUE, linewidth=2.2, marker="o", markersize=5, label="mixture, source-inclusive")
    axis.axhline(0.5, color=INK, linestyle=":", linewidth=1.2, label="0.5% gate")
    axis.set_title("Source-inclusive mass imbalance", fontweight="semibold")
    axis.set_xlabel("Total solver iteration")
    axis.set_ylabel("%")
    axis.legend(frameon=False, fontsize=8.2)
    style_axis(axis)

    axis = axes[1, 1]
    axis.plot(frame["iteration"], frame["pressure_drop_pa"] / 1000.0, color=ORANGE, linewidth=2.2, marker="s", markersize=5, label="pressure drop (kPa)")
    twin = axis.twinx()
    twin.plot(frame["iteration"], frame["domain_liquid_inventory_kg"], color=BLUE, linewidth=2.2, marker="o", markersize=5, label="liquid inventory (kg)")
    axis.set_title("Pressure and liquid inventory", fontweight="semibold")
    axis.set_xlabel("Total solver iteration")
    axis.set_ylabel("Pressure drop (kPa)", color=ORANGE)
    twin.set_ylabel("Liquid inventory (kg)", color=BLUE)
    axis.tick_params(axis="y", colors=ORANGE)
    twin.tick_params(axis="y", colors=BLUE)
    style_axis(axis)
    twin.spines["top"].set_visible(False)

    figure.subplots_adjust(left=0.075, right=0.925, bottom=0.115, top=0.88, hspace=0.38, wspace=0.30)
    figure.text(
        0.01,
        0.012,
        "Empirical global feedback through a local volumetric source. It tests numerical closure and field stability; it does not represent outlet hydraulics.",
        fontsize=8,
        color="#6B7280",
        ha="left",
    )
    return save(figure, "14_setup07e_adaptive_control_history")


def residual_figure(residual: pd.DataFrame, manifest: dict) -> dict[str, str]:
    figure, axes = plt.subplots(1, 2, figsize=(11.6, 5.8))
    figure.suptitle("Setup 07e residual response under adaptive liquid-mass control", fontsize=16, fontweight="semibold", y=0.975)
    figure.text(0.5, 0.920, f"Current controller status: {manifest.get('status', 'unknown')} • DPM off", ha="center", fontsize=10, color=MID)
    for axis, field, title in (
        (axes[0], "continuity", "Continuity residual"),
        (axes[1], "vf-phase-2", "Liquid volume-fraction residual"),
    ):
        axis.plot(residual["iteration"], residual[field], color=ORANGE if field == "continuity" else BLUE, linewidth=1.3)
        axis.axhline(1e-3, color=INK, linestyle=":", linewidth=1.2, label="1e-3 gate")
        axis.set_yscale("log")
        axis.set_title(title, fontweight="semibold")
        axis.set_xlabel("Total solver iteration")
        axis.set_ylabel("Scaled residual")
        axis.legend(frameon=False, fontsize=8.5)
        style_axis(axis)
    figure.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.80, wspace=0.28)
    figure.text(0.01, 0.012, "Residuals must be interpreted with physical-monitor and mass-balance stability; iteration count alone is not convergence.", fontsize=8, color="#6B7280")
    return save(figure, "15_setup07e_adaptive_residual_history")


def wetting_response_figure(physical: pd.DataFrame, manifest: dict) -> dict[str, str]:
    """Show transport delay and adaptive-source onset across log-scaled ranges."""
    frame = physical.copy().sort_values("iteration")
    band_floor = 1.0e-15
    sink_floor = 1.0e-12
    reporting_threshold = 1.0e-9
    frame["band_inventory_display_kg"] = np.maximum(
        frame["bottom_layer_liquid_inventory_kg"].abs(), band_floor
    )
    frame["sink_display_kgs"] = np.maximum(
        frame["sink_magnitude_kgs"].abs(), sink_floor
    )
    export_columns = [
        "iteration",
        "r1_iteration",
        "ramp",
        "tau_s",
        "bottom_layer_liquid_inventory_kg",
        "sink_magnitude_kgs",
        "liquid_imbalance_percent",
        "pressure_drop_pa",
        "domain_liquid_inventory_kg",
    ]
    frame[export_columns].to_csv(
        OUTPUT_DIR / "setup07e_band_wetting_response.csv", index=False
    )

    wet = frame[frame["bottom_layer_liquid_inventory_kg"].abs() > reporting_threshold]
    wet_iteration = int(wet.iloc[0]["iteration"]) if not wet.empty else None
    endpoint = int(frame.iloc[-1]["iteration"])

    figure, axes = plt.subplots(1, 3, figsize=(12.2, 5.2))
    figure.suptitle(
        "Setup 07e: local-band wetting controls when the adaptive sink can respond",
        fontsize=16,
        fontweight="semibold",
        y=0.975,
    )
    wet_text = (
        f"first saved band inventory above 1e-9 kg at iteration {wet_iteration}"
        if wet_iteration is not None
        else "active band remains below the 1e-9 kg reporting threshold"
    )
    figure.text(
        0.5,
        0.915,
        f"Saved evidence through iteration {endpoint} • {wet_text} • DPM off",
        ha="center",
        fontsize=9.5,
        color=MID,
    )

    axis = axes[0]
    axis.plot(
        frame["iteration"],
        frame["band_inventory_display_kg"],
        color=BLUE,
        linewidth=2.2,
        marker="o",
        markersize=4,
    )
    axis.axhline(
        reporting_threshold,
        color=INK,
        linestyle=":",
        linewidth=1.2,
        label="reporting threshold",
    )
    axis.axvline(1000, color=MID, linestyle="--", linewidth=1.0)
    axis.set_yscale("log")
    axis.set_title("Liquid available in sink band", fontweight="semibold")
    axis.set_xlabel("Total solver iteration")
    axis.set_ylabel("kg (log scale)")
    axis.legend(frameon=False, fontsize=8.0)
    style_axis(axis)

    axis = axes[1]
    axis.plot(
        frame["iteration"],
        frame["sink_display_kgs"],
        color=ORANGE,
        linewidth=2.2,
        marker="s",
        markersize=4,
    )
    axis.axhline(116.92, color=INK, linestyle=":", linewidth=1.2, label="116.92 kg/s command")
    axis.axvline(1000, color=MID, linestyle="--", linewidth=1.0)
    axis.set_yscale("log")
    axis.set_title("Achieved numerical liquid sink", fontweight="semibold")
    axis.set_xlabel("Total solver iteration")
    axis.set_ylabel("kg/s (log scale)")
    axis.legend(frameon=False, fontsize=8.0)
    style_axis(axis)

    axis = axes[2]
    axis.step(
        frame["iteration"],
        frame["tau_s"],
        where="post",
        color=GOLD,
        linewidth=2.2,
        marker="o",
        markersize=4,
    )
    axis.axhline(0.002, color=INK, linestyle=":", linewidth=1.0, label="bounded minimum")
    axis.axhline(0.2, color=MID, linestyle=":", linewidth=1.0, label="bounded maximum")
    axis.axvline(1000, color=MID, linestyle="--", linewidth=1.0, label="R=1 begins")
    axis.set_yscale("log")
    axis.set_title("Feedback time scale", fontweight="semibold")
    axis.set_xlabel("Total solver iteration")
    axis.set_ylabel("tau (s, log scale)")
    axis.legend(frameon=False, fontsize=8.0)
    style_axis(axis)

    figure.subplots_adjust(left=0.07, right=0.985, bottom=0.18, top=0.79, wspace=0.31)
    figure.text(
        0.01,
        0.012,
        "Values below 1e-15 kg and 1e-12 kg/s are displayed at plotting floors. Wetting and sink response are numerical diagnostics, not physical outlet flow.",
        fontsize=8,
        color="#6B7280",
    )
    return save(figure, "19_setup07e_band_wetting_and_sink_response")


def sink_strategy_comparison_figure(physical: pd.DataFrame) -> dict[str, str]:
    """Compare native saved R=1 histories for the three thick-band strategies."""
    current_r1 = int(physical["r1_iteration"].max())
    cases = (
        (
            "07c fixed tau=0.10 s",
            pd.read_csv(SETUP07C_DIR / "physical_monitor_history.csv"),
            BLUE,
            "o",
        ),
        (
            "07d fixed tau=0.02 s",
            pd.read_csv(SETUP07D_DIR / "physical_monitor_history.csv"),
            ORANGE,
            "s",
        ),
        ("07e adaptive tau", physical.copy(), GOLD, "^"),
    )
    prepared: list[tuple[str, pd.DataFrame, str, str]] = []
    exports: list[pd.DataFrame] = []
    for label, frame, color, marker in cases:
        frame = (
            frame[frame["r1_iteration"].astype(float) > 0]
            .drop_duplicates("r1_iteration", keep="last")
            .sort_values("r1_iteration")
        )
        frame = frame[frame["r1_iteration"].astype(float) <= current_r1]
        if frame.empty:
            continue
        prepared.append((label, frame, color, marker))
        export = frame[
            [
                "r1_iteration",
                "tau_s",
                "sink_magnitude_kgs",
                "liquid_imbalance_percent",
                "pressure_drop_pa",
                "domain_liquid_inventory_kg",
            ]
        ].copy()
        export.insert(0, "strategy", label)
        exports.append(export)
    if not prepared:
        raise RuntimeError("No setup-07c/07d/07e full-strength histories found")
    pd.concat(exports, ignore_index=True).to_csv(
        OUTPUT_DIR / "setup07_sink_strategy_comparison.csv", index=False
    )

    figure, axes = plt.subplots(2, 2, figsize=(12.2, 8.0))
    figure.suptitle(
        "Three local-sink strategies remain constrained by liquid reaching the same band",
        fontsize=16,
        fontweight="semibold",
        y=0.982,
    )
    figure.text(
        0.5,
        0.943,
        f"Same clean 900k carrier and 0.140165 m band • native saved R=1 blocks through iteration {current_r1} • DPM off",
        ha="center",
        fontsize=9.5,
        color=MID,
    )
    panels = (
        (axes[0, 0], "sink_magnitude_kgs", 1.0, "Liquid sink", "kg/s"),
        (axes[0, 1], "liquid_imbalance_percent", 1.0, "Corrected liquid imbalance", "%"),
        (axes[1, 0], "pressure_drop_pa", 1.0 / 1000.0, "Pressure drop", "kPa"),
        (axes[1, 1], "domain_liquid_inventory_kg", 1.0, "Domain liquid inventory", "kg"),
    )
    for axis, field, scale, title, unit in panels:
        for label, frame, color, marker in prepared:
            axis.plot(
                frame["r1_iteration"],
                frame[field] * scale,
                color=color,
                linewidth=2.0,
                marker=marker,
                markersize=4.5,
                label=label,
            )
        if field == "sink_magnitude_kgs":
            axis.axhline(116.92, color=INK, linestyle=":", linewidth=1.2, label="liquid feed")
        if field == "liquid_imbalance_percent":
            axis.axhline(0.5, color=INK, linestyle=":", linewidth=1.2, label="0.5% gate")
        axis.set_title(title, fontweight="semibold")
        axis.set_xlabel("Full-strength R=1 iteration")
        axis.set_ylabel(unit)
        style_axis(axis)
    axes[0, 0].legend(frameon=False, fontsize=8.0, loc="best")
    axes[0, 1].legend(frameon=False, fontsize=8.0, loc="best")
    figure.subplots_adjust(left=0.075, right=0.985, bottom=0.125, top=0.86, hspace=0.36, wspace=0.28)
    figure.text(
        0.01,
        0.012,
        "Histories use each controller's native saved block spacing. The comparison tests numerical source behavior only; none supplies physical outlet hydraulics.",
        fontsize=8,
        color="#6B7280",
    )
    return save(figure, "20_setup07_sink_strategy_comparison")


def liquid_pathway_accounting_figure(
    physical: pd.DataFrame, manifest: dict
) -> dict[str, str]:
    """Compare endpoint liquid routing for the closed and sink diagnostics."""
    baseline = pd.read_csv(OUTPUT_DIR / "endpoint_liquid_rate_closure.csv")[
        [
            "case",
            "liquid_inlet_kgs",
            "liquid_outlet_kgs",
            "udf_sink_kgs",
        ]
    ].copy()
    fixed = (
        pd.read_csv(SETUP07D_DIR / "physical_monitor_history.csv")
        .drop_duplicates("r1_iteration", keep="last")
        .sort_values("r1_iteration")
        .iloc[-1]
    )
    adaptive = physical.sort_values("iteration").iloc[-1]
    additions = pd.DataFrame(
        [
            {
                "case": f"07d strong fixed sink\nR1 = {int(fixed['r1_iteration'])}",
                "liquid_inlet_kgs": 116.92,
                "liquid_outlet_kgs": abs(float(fixed["liquid_steamoutlet_kgs"])),
                "udf_sink_kgs": float(fixed["sink_magnitude_kgs"]),
            },
            {
                "case": (
                    "07e adaptive sink\n"
                    f"R1 = {int(adaptive['r1_iteration'])} ({manifest.get('status', 'unknown')})"
                ),
                "liquid_inlet_kgs": 116.92,
                "liquid_outlet_kgs": abs(
                    float(adaptive["liquid_steamoutlet_kgs"])
                ),
                "udf_sink_kgs": float(adaptive["sink_magnitude_kgs"]),
            },
        ]
    )
    frame = pd.concat([baseline, additions], ignore_index=True)
    frame["unclosed_liquid_rate_kgs"] = (
        frame["liquid_inlet_kgs"]
        - frame["liquid_outlet_kgs"]
        - frame["udf_sink_kgs"]
    ).clip(lower=0.0)
    frame["accounted_fraction_percent"] = 100.0 * (
        frame["liquid_outlet_kgs"] + frame["udf_sink_kgs"]
    ) / frame["liquid_inlet_kgs"]
    export = OUTPUT_DIR / "setup07_liquid_pathway_accounting.csv"
    frame.to_csv(export, index=False)

    figure, axis = plt.subplots(figsize=(11.4, 7.1))
    figure.suptitle(
        "Setup 07 liquid-pathway accounting at diagnostic endpoints",
        fontsize=16,
        fontweight="semibold",
        y=0.978,
    )
    figure.text(
        0.5,
        0.928,
        "Common liquid feed = 116.92 kg/s • same 900k carrier lineage for sink cases • DPM off",
        ha="center",
        fontsize=9.5,
        color=MID,
    )
    y = np.arange(len(frame))
    left = np.zeros(len(frame))
    for field, label, color in (
        ("liquid_outlet_kgs", "Liquid through steam outlet", BLUE),
        ("udf_sink_kgs", "Numerical liquid sink", ORANGE),
        ("unclosed_liquid_rate_kgs", "Unclosed steady rate", LIGHT_GREY),
    ):
        values = frame[field].to_numpy(dtype=float)
        axis.barh(
            y,
            values,
            left=left,
            height=0.58,
            color=color,
            edgecolor=WHITE,
            linewidth=1.0,
            label=label,
        )
        for index, (start, value) in enumerate(zip(left, values, strict=True)):
            if value >= 5.0:
                axis.text(
                    start + value / 2.0,
                    index,
                    f"{value:.1f}",
                    ha="center",
                    va="center",
                    fontsize=8.8,
                    color=INK,
                    fontweight="semibold",
                )
        left += values
    for index, row in frame.iterrows():
        axis.text(
            119.0,
            index,
            f"{row['accounted_fraction_percent']:.1f}% routed",
            va="center",
            fontsize=8.8,
            color=ORANGE,
            fontweight="semibold",
        )
    axis.set_yticks(y, frame["case"])
    axis.invert_yaxis()
    axis.set_xlim(0.0, 137.0)
    axis.set_xlabel("Liquid rate (kg/s)")
    axis.axvline(116.92, color=INK, linewidth=1.2, linestyle=":")
    axis.legend(
        frameon=False,
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.24),
        fontsize=8.8,
    )
    style_axis(axis, grid_axis="x")
    axis.spines["left"].set_visible(False)
    axis.tick_params(axis="y", length=0)
    figure.subplots_adjust(left=0.245, right=0.985, bottom=0.22, top=0.84)
    figure.text(
        0.01,
        0.012,
        "Unclosed steady rate is source-inclusive mass-accounting evidence, not a physical transient accumulation rate. All states are diagnostic/unresolved.",
        fontsize=8,
        color="#6B7280",
    )
    return save(figure, "21_setup07_liquid_pathway_accounting")


def minimum_tau_capacity_figure(
    physical: pd.DataFrame, manifest: dict
) -> dict[str, str]:
    """Show the local liquid inventory required to meet the sink command."""
    target = float(manifest.get("adaptive_target_liquid_sink_kgs", 116.92))
    tau_min = float(manifest.get("adaptive_tau_bounds_s", [0.002, 0.2])[0])
    required_inventory = target * tau_min
    frame = (
        physical[physical["r1_iteration"].astype(float) > 0]
        .drop_duplicates("iteration", keep="last")
        .sort_values("iteration")
        .copy()
    )
    frame["required_band_inventory_at_tau_min_kg"] = required_inventory
    frame["band_inventory_fraction_of_required_percent"] = (
        100.0
        * frame["bottom_layer_liquid_inventory_kg"]
        / required_inventory
    )
    frame["achieved_sink_fraction_of_target_percent"] = (
        100.0 * frame["sink_magnitude_kgs"] / target
    )
    export_columns = [
        "iteration",
        "r1_iteration",
        "tau_s",
        "bottom_layer_liquid_inventory_kg",
        "required_band_inventory_at_tau_min_kg",
        "band_inventory_fraction_of_required_percent",
        "sink_magnitude_kgs",
        "achieved_sink_fraction_of_target_percent",
        "liquid_imbalance_percent",
    ]
    frame[export_columns].to_csv(
        OUTPUT_DIR / "setup07e_minimum_tau_capacity.csv", index=False
    )

    endpoint = frame.iloc[-1]
    figure, axes = plt.subplots(1, 2, figsize=(12.2, 5.7))
    figure.suptitle(
        "Setup 07e: minimum tau is saturated before liquid mass closure",
        fontsize=16,
        fontweight="semibold",
        y=0.975,
    )
    figure.text(
        0.5,
        0.918,
        f"At tau={tau_min:.3f} s, the active band needs {required_inventory:.5f} kg to remove {target:.2f} kg/s • DPM off",
        ha="center",
        fontsize=9.7,
        color=MID,
    )

    axis = axes[0]
    axis.plot(
        frame["r1_iteration"],
        frame["bottom_layer_liquid_inventory_kg"],
        color=BLUE,
        linewidth=2.2,
        marker="o",
        markersize=4.5,
        label="available band liquid",
    )
    axis.axhline(
        required_inventory,
        color=INK,
        linestyle=":",
        linewidth=1.5,
        label="required at minimum tau",
    )
    axis.annotate(
        f"{float(endpoint['bottom_layer_liquid_inventory_kg']):.5f} kg",
        (
            float(endpoint["r1_iteration"]),
            float(endpoint["bottom_layer_liquid_inventory_kg"]),
        ),
        xytext=(-82, 13),
        textcoords="offset points",
        fontsize=8.8,
        color=BLUE,
        arrowprops={"arrowstyle": "->", "color": BLUE, "lw": 1.0},
    )
    axis.set_title("Liquid inventory in the active sink band", fontweight="semibold")
    axis.set_xlabel("Full-strength R=1 iteration")
    axis.set_ylabel("kg")
    axis.set_ylim(bottom=0.0)
    axis.legend(frameon=False, fontsize=8.4)
    style_axis(axis)

    axis = axes[1]
    axis.plot(
        frame["r1_iteration"],
        frame["band_inventory_fraction_of_required_percent"],
        color=BLUE,
        linewidth=2.2,
        marker="o",
        markersize=4.5,
        label="inventory capacity",
    )
    axis.plot(
        frame["r1_iteration"],
        frame["achieved_sink_fraction_of_target_percent"],
        color=ORANGE,
        linewidth=2.0,
        linestyle="--",
        marker="s",
        markersize=4,
        label="achieved sink",
    )
    axis.axhline(100.0, color=INK, linestyle=":", linewidth=1.5, label="mass-closure command")
    axis.set_title("Fraction of the 116.92 kg/s command", fontweight="semibold")
    axis.set_xlabel("Full-strength R=1 iteration")
    axis.set_ylabel("%")
    axis.set_ylim(bottom=0.0)
    axis.legend(frameon=False, fontsize=8.4)
    style_axis(axis)

    figure.subplots_adjust(left=0.075, right=0.985, bottom=0.17, top=0.80, wspace=0.28)
    figure.text(
        0.01,
        0.012,
        "This tests the implemented source law S=-rho alpha/tau. It shows local numerical capacity, not a physical drain characteristic or outlet validation.",
        fontsize=8,
        color="#6B7280",
    )
    return save(figure, "26_setup07e_minimum_tau_capacity")


def dry_band_repeatability_figure(physical: pd.DataFrame) -> dict[str, str]:
    reference = (
        pd.read_csv(SETUP07D_DIR / "physical_monitor_history.csv")
        .drop_duplicates("iteration", keep="last")
        .sort_values("iteration")
    )
    dry = physical[physical["bottom_layer_liquid_inventory_kg"].abs() <= 1.0e-9]
    reference_dry = reference[
        reference["bottom_layer_liquid_inventory_kg"].abs() <= 1.0e-9
    ]
    matched = dry.merge(reference_dry, on="iteration", suffixes=("_07e", "_07d"))
    if matched.empty:
        raise RuntimeError("No exact saved dry-band iterations match setup 07d")
    matched.to_csv(OUTPUT_DIR / "setup07e_dry_band_lineage_comparison.csv", index=False)

    audited_fields = (
        "pressure_drop_pa",
        "domain_liquid_inventory_kg",
        "mixture_steamoutlet_kgs",
        "vapor_steamoutlet_kgs",
        "outlet_area_weighted_velocity_ms",
        "domain_volume_avg_velocity_ms",
        "domain_volume_avg_vorticity_s-1",
    )
    maximum_difference = 0.0
    for field in audited_fields:
        reference_values = matched[f"{field}_07d"].abs().clip(lower=1.0e-30)
        difference = (
            (matched[f"{field}_07e"] - matched[f"{field}_07d"]).abs()
            / reference_values
            * 100.0
        )
        maximum_difference = max(maximum_difference, float(difference.max()))

    figure, axes = plt.subplots(1, 3, figsize=(12.2, 5.5))
    figure.suptitle(
        "Clean-start carrier lineage is exactly repeatable before the sink band wets",
        fontsize=16,
        fontweight="semibold",
        y=0.975,
    )
    figure.text(
        0.5,
        0.918,
        f"Exact saved iterations {matched['iteration'].astype(int).tolist()} • maximum difference across seven audited fields {maximum_difference:.6f}%",
        ha="center",
        fontsize=10,
        color=MID,
    )
    panels = (
        ("pressure_drop_pa", "Pressure drop", "kPa", 1.0 / 1000.0),
        ("domain_liquid_inventory_kg", "Domain liquid inventory", "kg", 1.0),
        ("outlet_area_weighted_velocity_ms", "Outlet velocity", "m/s", 1.0),
    )
    for axis, (field, title, unit, scale) in zip(axes, panels, strict=True):
        axis.plot(
            matched["iteration"],
            matched[f"{field}_07d"] * scale,
            color=BLUE,
            linewidth=2.6,
            marker="o",
            markerfacecolor=WHITE,
            markeredgewidth=1.6,
            markersize=8,
            label="07d fixed tau",
        )
        axis.plot(
            matched["iteration"],
            matched[f"{field}_07e"] * scale,
            color=ORANGE,
            linestyle="--",
            linewidth=1.8,
            marker="s",
            markersize=4,
            label="07e adaptive tau",
        )
        axis.set_title(title, fontweight="semibold")
        axis.set_xlabel("Total solver iteration")
        axis.set_ylabel(unit)
        axis.set_xticks(matched["iteration"].astype(int).tolist())
        axis.margins(x=0.08, y=0.18)
        style_axis(axis)
    axes[0].legend(frameon=False, fontsize=8.5, loc="best")
    figure.subplots_adjust(left=0.07, right=0.985, bottom=0.17, top=0.79, wspace=0.30)
    figure.text(
        0.01,
        0.012,
        "Exact overlap verifies deterministic clean-start lineage only. It does not validate feedback, the volumetric sink or brine-outlet hydraulics.",
        fontsize=8,
        color="#6B7280",
    )
    return save(figure, "18_setup07e_dry_band_lineage_repeatability")


def update_manifest(artifacts: dict[str, dict[str, str]]) -> None:
    path = OUTPUT_DIR / "visual_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    manifest.setdefault("artifacts", {}).update(artifacts)
    manifest.setdefault("source_files", [])
    for source in (
        RUN_DIR / "physical_monitor_history.csv",
        RUN_DIR / "residual_history.csv",
        RUN_DIR / "qualification_manifest.json",
    ):
        if str(source) not in manifest["source_files"]:
            manifest["source_files"].append(str(source))
    reference = SETUP07D_DIR / "physical_monitor_history.csv"
    if str(reference) not in manifest["source_files"]:
        manifest["source_files"].append(str(reference))
    lineage_csv = OUTPUT_DIR / "setup07e_dry_band_lineage_comparison.csv"
    wetting_csv = OUTPUT_DIR / "setup07e_band_wetting_response.csv"
    strategy_csv = OUTPUT_DIR / "setup07_sink_strategy_comparison.csv"
    pathway_csv = OUTPUT_DIR / "setup07_liquid_pathway_accounting.csv"
    capacity_csv = OUTPUT_DIR / "setup07e_minimum_tau_capacity.csv"
    manifest.setdefault("data_exports", [])
    for export in (lineage_csv, wetting_csv, strategy_csv, pathway_csv, capacity_csv):
        if str(export) not in manifest["data_exports"]:
            manifest["data_exports"].append(str(export))
    manifest["completion_checklist"] = str(OUTPUT_DIR / "OVERNIGHT_COMPLETION_CHECKLIST.md")
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    set_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    physical, residual, manifest = load_histories()
    if physical.empty or residual.empty:
        raise RuntimeError("setup-07e histories do not yet contain plottable data")
    artifacts = {
        "setup07e_adaptive_control_history": control_history_figure(physical, manifest),
        "setup07e_adaptive_residual_history": residual_figure(residual, manifest),
        "setup07e_band_wetting_and_sink_response": wetting_response_figure(physical, manifest),
        "setup07_sink_strategy_comparison": sink_strategy_comparison_figure(physical),
        "setup07_liquid_pathway_accounting": liquid_pathway_accounting_figure(
            physical, manifest
        ),
        "setup07e_dry_band_lineage_repeatability": dry_band_repeatability_figure(physical),
        "setup07e_minimum_tau_capacity": minimum_tau_capacity_figure(
            physical, manifest
        ),
    }
    update_manifest(artifacts)
    print(OUTPUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
