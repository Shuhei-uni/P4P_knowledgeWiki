#!/usr/bin/env python3
"""Build meeting figures comparing the qualified fixed-strength sink trials.

Setup 07c and setup 07d start from the same prepared 900k carrier case, use
the same 0.1401652536 m bottom-local band, and differ only in the fixed sink
timescale (0.1 s versus 0.02 s).  The figures deliberately describe the
remaining liquid rate as an unclosed steady-solver balance, not a physical
transient accumulation rate.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"
SETUP07C_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_thickened_water_level_sink_20260808"
    / "mesh-900k_band0p140165_tau0p100_v1"
)
SETUP07D_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_strong_sink_sensitivity_20260810"
    / "mesh-900k_band0p140165_tau0p020_v1"
)

BLUE = "#1769AA"
ORANGE = "#D97706"
GOLD = "#C49A00"
INK = "#1F2933"
MID = "#5B6570"
GRID = "#D9DEE3"
GREY = "#D5DADF"
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


def add_footer(figure: plt.Figure, text: str) -> None:
    figure.text(0.01, 0.012, text, fontsize=8, color="#6B7280", ha="left")


def save_figure(figure: plt.Figure, stem: str) -> dict[str, str]:
    png = OUTPUT_DIR / f"{stem}.png"
    svg = OUTPUT_DIR / f"{stem}.svg"
    figure.savefig(png, dpi=240)
    figure.savefig(svg)
    plt.close(figure)
    return {"png": str(png), "svg": str(svg)}


def load_full_strength(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path / "physical_monitor_history.csv")
    return (
        frame[frame["r1_iteration"] > 0]
        .drop_duplicates("r1_iteration", keep="last")
        .sort_values("r1_iteration")
        .copy()
    )


def load_residuals(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path / "residual_history.csv")
    frame = frame[frame["iteration"] > 1000].copy()
    frame["r1_iteration"] = frame["iteration"] - 1000
    return frame


def matched_frame(c: pd.DataFrame, d: pd.DataFrame) -> pd.DataFrame:
    iterations = sorted(set(c["r1_iteration"]) & set(d["r1_iteration"]))
    rows: list[pd.DataFrame] = []
    for label, tau, frame in (("07c", 0.1, c), ("07d", 0.02, d)):
        selected = frame[frame["r1_iteration"].isin(iterations)].copy()
        selected["setup"] = label
        selected["tau_s"] = tau
        selected["sink_coefficient_relative"] = 0.1 / tau
        selected["removed_liquid_fraction_percent"] = (
            100.0 * selected["sink_magnitude_kgs"] / 116.92
        )
        # Fluent's phase-2 Net already includes the cell-zone liquid source.
        # Subtracting sink_magnitude_kgs here would count the UDF source twice.
        selected["unclosed_liquid_rate_kgs"] = selected[
            "liquid_net_kgs"
        ].clip(lower=0.0)
        rows.append(selected)
    return pd.concat(rows, ignore_index=True)


def history_figure(c: pd.DataFrame, d: pd.DataFrame) -> dict[str, str]:
    figure, axes = plt.subplots(2, 2, figsize=(12.2, 8.0))
    figure.suptitle(
        "A five-times stronger local sink improves closure but does not stabilize the carrier field",
        fontsize=16,
        fontweight="semibold",
        y=0.982,
    )
    figure.text(
        0.5,
        0.943,
        "Same clean 900k case, same 0.140165 m band and 2000 full-strength iterations; DPM off",
        ha="center",
        fontsize=10,
        color=MID,
    )

    panels = (
        ("sink_magnitude_kgs", "Liquid sink", "kg/s", 1.0),
        ("unclosed_liquid_rate_kgs", "Unclosed liquid rate", "kg/s", 1.0),
        ("domain_liquid_inventory_kg", "Domain liquid inventory", "kg", 1.0),
        ("pressure_drop_pa", "Pressure drop", "kPa", 1.0 / 1000.0),
    )
    for axis, (field, title, unit, scale) in zip(axes.flat, panels, strict=True):
        for frame, label, color, style in (
            (c, "07c: tau = 0.10 s", BLUE, "-"),
            (d, "07d: tau = 0.02 s", ORANGE, "--"),
        ):
            values = (
                frame["liquid_net_kgs"]
                if field == "unclosed_liquid_rate_kgs"
                else frame[field]
            )
            axis.plot(
                frame["r1_iteration"],
                values * scale,
                color=color,
                linestyle=style,
                linewidth=2.2,
                marker="o" if color == BLUE else "s",
                markersize=5,
                label=label,
            )
        axis.set_title(title, fontweight="semibold")
        axis.set_xlabel("Full-strength iteration")
        axis.set_ylabel(unit)
        axis.set_xticks([250, 750, 1250, 1750, 2000])
        axis.margins(x=0.04, y=0.15)
        style_axis(axis)
    axes[0, 0].axhline(116.92, color=INK, linestyle=":", linewidth=1.3, label="liquid inlet")
    axes[0, 0].legend(frameon=False, fontsize=8.5, loc="upper left")
    axes[0, 1].legend(frameon=False, fontsize=8.5, loc="upper right")

    figure.subplots_adjust(left=0.075, right=0.985, bottom=0.105, top=0.88, hspace=0.38, wspace=0.27)
    add_footer(
        figure,
        "Diagnostic steady-solver histories. The unclosed liquid rate is source-inclusive balance error, not a physical transient accumulation rate.",
    )
    return save_figure(figure, "10_fixed_sink_strength_history")


def endpoint_figure(c: pd.DataFrame, d: pd.DataFrame) -> dict[str, str]:
    endpoints = pd.DataFrame(
        {
            "case": ["07c\ntau = 0.10 s", "07d\ntau = 0.02 s"],
            "relative_coefficient": [1.0, 5.0],
            "sink_kgs": [c.iloc[-1]["sink_magnitude_kgs"], d.iloc[-1]["sink_magnitude_kgs"]],
            "removed_percent": [
                100.0 * c.iloc[-1]["sink_magnitude_kgs"] / 116.92,
                100.0 * d.iloc[-1]["sink_magnitude_kgs"] / 116.92,
            ],
            "band_inventory_kg": [
                c.iloc[-1]["bottom_layer_liquid_inventory_kg"],
                d.iloc[-1]["bottom_layer_liquid_inventory_kg"],
            ],
        }
    )
    endpoints.to_csv(OUTPUT_DIR / "fixed_sink_strength_endpoints.csv", index=False)

    figure, axes = plt.subplots(1, 3, figsize=(12.2, 5.7))
    figure.suptitle("Fixed-strength sensitivity shows diminishing return from the same local sink band", fontsize=16, fontweight="semibold", y=0.975)
    figure.text(0.5, 0.922, "Endpoint at 2000 full-strength iterations; diagnostic and unresolved", ha="center", fontsize=10, color=MID)

    x = np.arange(2)
    colors = [BLUE, ORANGE]
    series = (
        ("relative_coefficient", "Imposed source coefficient", "relative to 07c", "×"),
        ("sink_kgs", "Resulting liquid sink", "kg/s", ""),
        ("band_inventory_kg", "Liquid available in sink band", "kg", ""),
    )
    for axis, (field, title, unit, suffix) in zip(axes, series, strict=True):
        values = endpoints[field].to_numpy()
        axis.bar(x, values, width=0.58, color=colors, edgecolor=WHITE)
        axis.set_xticks(x, endpoints["case"])
        axis.set_title(title, fontweight="semibold")
        axis.set_ylabel(unit)
        axis.margins(y=0.22)
        style_axis(axis)
        for index, value in enumerate(values):
            label = f"{value:.2f}{suffix}" if field != "relative_coefficient" else f"{value:.0f}{suffix}"
            axis.text(index, value, label, ha="center", va="bottom", fontsize=11, color=colors[index], fontweight="bold")
    axes[1].axhline(116.92, color=INK, linestyle=":", linewidth=1.2)
    axes[1].text(1.45, 113.0, "liquid inlet", ha="right", va="top", fontsize=8.5, color=INK)
    axes[1].set_ylim(0, 132)
    axes[1].text(0, endpoints.loc[0, "sink_kgs"] + 11, f"{endpoints.loc[0, 'removed_percent']:.1f}% of inlet", ha="center", fontsize=8.8, color=BLUE)
    axes[1].text(1, endpoints.loc[1, "sink_kgs"] + 11, f"{endpoints.loc[1, 'removed_percent']:.1f}% of inlet", ha="center", fontsize=8.8, color=ORANGE)

    figure.subplots_adjust(left=0.07, right=0.985, bottom=0.17, top=0.80, wspace=0.32)
    add_footer(
        figure,
        "A 5× coefficient produced only a 2.09× endpoint sink because the marked band contained less liquid. This does not reproduce outlet hydraulics.",
    )
    return save_figure(figure, "11_fixed_sink_diminishing_return")


def inventory_limited_mechanism_figure(c: pd.DataFrame, d: pd.DataFrame) -> dict[str, str]:
    """Show why the stronger source does not provide outlet-like flow control."""
    figure, axes = plt.subplots(1, 2, figsize=(12.2, 5.8))
    figure.suptitle(
        "The local sink is limited by liquid reaching its band—not by the inlet flow",
        fontsize=16,
        fontweight="semibold",
        y=0.975,
    )
    figure.text(
        0.5,
        0.920,
        "Same 900k carrier case and marked volume; full-strength samples only",
        ha="center",
        fontsize=10,
        color=MID,
    )

    for frame, label, color, style, marker in (
        (c, "07c: tau = 0.10 s", BLUE, "-", "o"),
        (d, "07d: tau = 0.02 s", ORANGE, "--", "s"),
    ):
        axes[0].plot(
            frame["r1_iteration"],
            frame["bottom_layer_liquid_inventory_kg"],
            color=color,
            linestyle=style,
            linewidth=2.2,
            marker=marker,
            markersize=5,
            label=label,
        )
        axes[1].scatter(
            frame["bottom_layer_liquid_inventory_kg"],
            frame["sink_magnitude_kgs"],
            color=color,
            marker=marker,
            s=46,
            label=label,
            zorder=3,
        )

    axes[0].set_title("Liquid available inside the active band", fontweight="semibold")
    axes[0].set_xlabel("Full-strength iteration")
    axes[0].set_ylabel("Band liquid inventory (kg)")
    axes[0].set_xticks([250, 750, 1250, 1750, 2000])
    axes[0].legend(frameon=False, fontsize=8.5, loc="upper left")
    axes[0].margins(x=0.04, y=0.18)
    style_axis(axes[0])

    maximum_inventory = max(
        c["bottom_layer_liquid_inventory_kg"].max(),
        d["bottom_layer_liquid_inventory_kg"].max(),
    )
    inventory_axis = np.linspace(0.0, maximum_inventory * 1.08, 100)
    axes[1].plot(inventory_axis, inventory_axis / 0.1, color=BLUE, linewidth=1.4, alpha=0.8)
    axes[1].plot(inventory_axis, inventory_axis / 0.02, color=ORANGE, linewidth=1.4, alpha=0.8)
    axes[1].set_title("The UDF removes only local inventory: sink = Mband / tau", fontweight="semibold")
    axes[1].set_xlabel("Band liquid inventory (kg)")
    axes[1].set_ylabel("Liquid sink (kg/s)")
    axes[1].legend(frameon=False, fontsize=8.5, loc="upper left")
    axes[1].margins(x=0.05, y=0.14)
    style_axis(axes[1])

    c_end = c.iloc[-1]
    d_end = d.iloc[-1]
    axes[0].annotate(
        f"{c_end['bottom_layer_liquid_inventory_kg']:.2f} kg",
        (c_end["r1_iteration"], c_end["bottom_layer_liquid_inventory_kg"]),
        xytext=(-48, 12),
        textcoords="offset points",
        color=BLUE,
        fontsize=9,
        fontweight="bold",
    )
    axes[0].annotate(
        f"{d_end['bottom_layer_liquid_inventory_kg']:.2f} kg",
        (d_end["r1_iteration"], d_end["bottom_layer_liquid_inventory_kg"]),
        xytext=(-47, -18),
        textcoords="offset points",
        color=ORANGE,
        fontsize=9,
        fontweight="bold",
    )
    axes[1].annotate(
        f"07d endpoint\n{d_end['sink_magnitude_kgs']:.1f} kg/s",
        (d_end["bottom_layer_liquid_inventory_kg"], d_end["sink_magnitude_kgs"]),
        xytext=(12, -2),
        textcoords="offset points",
        color=ORANGE,
        fontsize=9,
        fontweight="bold",
    )

    figure.subplots_adjust(left=0.078, right=0.985, bottom=0.16, top=0.80, wspace=0.27)
    add_footer(
        figure,
        "The 5x coefficient depletes the marked band, so endpoint removal rises only 2.09x. A real brine outlet would impose resolved discharge hydraulics.",
    )
    return save_figure(figure, "16_inventory_limited_sink_mechanism")


def residual_figure(c: pd.DataFrame, d: pd.DataFrame) -> dict[str, str]:
    rc = load_residuals(SETUP07C_DIR)
    rd = load_residuals(SETUP07D_DIR)
    figure, axes = plt.subplots(1, 2, figsize=(11.6, 5.8))
    figure.suptitle("The stronger fixed sink does not resolve the residual problem", fontsize=16, fontweight="semibold", y=0.975)
    figure.text(0.5, 0.920, "Full-strength portions only; same mesh and solver setup", ha="center", fontsize=10, color=MID)

    for axis, field, title in (
        (axes[0], "continuity", "Continuity residual"),
        (axes[1], "vf-phase-2", "Liquid volume-fraction residual"),
    ):
        axis.plot(rc["r1_iteration"], rc[field], color=BLUE, linewidth=1.3, label="07c: tau = 0.10 s")
        axis.plot(rd["r1_iteration"], rd[field], color=ORANGE, linewidth=1.3, label="07d: tau = 0.02 s")
        axis.axhline(1e-3, color=INK, linestyle=":", linewidth=1.2, label="1e-3 gate")
        axis.set_yscale("log")
        axis.set_title(title, fontweight="semibold")
        axis.set_xlabel("Full-strength iteration")
        axis.set_ylabel("Scaled residual")
        axis.set_xlim(0, 2000)
        style_axis(axis)
    axes[0].legend(frameon=False, fontsize=8.5, loc="best")
    axes[1].legend(frameon=False, fontsize=8.5, loc="best")

    figure.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.80, wspace=0.28)
    add_footer(
        figure,
        f"Endpoints: continuity 07c={rc.iloc[-1]['continuity']:.3f}, 07d={rd.iloc[-1]['continuity']:.3f}; "
        f"liquid VF 07c={rc.iloc[-1]['vf-phase-2']:.2e}, 07d={rd.iloc[-1]['vf-phase-2']:.2e}.",
    )
    return save_figure(figure, "12_fixed_sink_residual_comparison")


def updated_decision_summary() -> dict[str, str]:
    sources = (
        ("01_closed_bottom_inventory_pressure.png", "1. Closed bottom: inventory and pressure keep changing"),
        ("06_closed_bottom_liquid_field_comparison.png", "2. Spatial evidence: the liquid-rich region expands"),
        ("11_fixed_sink_diminishing_return.png", "3. Five-times stronger source removes only 40% of liquid feed"),
        ("12_fixed_sink_residual_comparison.png", "4. Continuity and physical-monitor gates still fail"),
    )
    figure, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    figure.suptitle(
        "Tuesday decision: add a resolved brine outlet before restarting mesh convergence",
        fontsize=23,
        color="#14324A",
        fontweight="bold",
    )
    for axis, (name, heading) in zip(axes.flat, sources, strict=True):
        axis.imshow(Image.open(OUTPUT_DIR / name).convert("RGB"))
        axis.set_title(heading, fontsize=13.5, color="#14324A", fontweight="bold", pad=8)
        axis.axis("off")
    figure.text(
        0.5,
        0.008,
        "Diagnostic / unresolved: fixed local sinks improve removal but do not supply outlet hydraulics or an iteration-independent carrier solution. DPM off.",
        ha="center",
        va="bottom",
        fontsize=11.5,
        color="#B42318",
        fontweight="bold",
    )
    return save_figure(figure, "13_tuesday_updated_decision_summary")


def update_manifest(artifacts: dict[str, dict[str, str]], comparison_csv: Path) -> None:
    path = OUTPUT_DIR / "visual_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    manifest.setdefault("source_files", [])
    manifest.setdefault("artifacts", {})
    manifest.setdefault("data_exports", [])
    for source in (
        SETUP07D_DIR / "physical_monitor_history.csv",
        SETUP07D_DIR / "residual_history.csv",
        SETUP07D_DIR / "qualification_manifest.json",
    ):
        if str(source) not in manifest["source_files"]:
            manifest["source_files"].append(str(source))
    manifest["artifacts"].update(artifacts)
    for export in (comparison_csv, OUTPUT_DIR / "fixed_sink_strength_endpoints.csv"):
        if str(export) not in manifest["data_exports"]:
            manifest["data_exports"].append(str(export))
    manifest["setup07d_takeaway"] = (
        "Reducing tau from 0.1 s to 0.02 s increased the endpoint sink from "
        "22.49 to 46.99 kg/s, but pressure, inventory and sink histories remained "
        "iteration-dependent and only 40.2% of the liquid inlet was removed."
    )
    chart_map = OUTPUT_DIR / "CHART_MAP.md"
    if chart_map.exists():
        manifest["chart_map"] = str(chart_map)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    set_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    c = load_full_strength(SETUP07C_DIR)
    d = load_full_strength(SETUP07D_DIR)
    comparison = matched_frame(c, d)
    comparison_csv = OUTPUT_DIR / "fixed_sink_strength_comparison.csv"
    comparison.to_csv(comparison_csv, index=False)
    artifacts = {
        "fixed_sink_strength_history": history_figure(c, d),
        "fixed_sink_diminishing_return": endpoint_figure(c, d),
        "inventory_limited_sink_mechanism": inventory_limited_mechanism_figure(c, d),
        "fixed_sink_residual_comparison": residual_figure(c, d),
        "tuesday_updated_decision_summary": updated_decision_summary(),
    }
    update_manifest(artifacts, comparison_csv)
    print(OUTPUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
