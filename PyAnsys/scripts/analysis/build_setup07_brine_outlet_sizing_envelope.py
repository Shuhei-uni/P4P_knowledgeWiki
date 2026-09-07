#!/usr/bin/env python3
"""Build a kinematic brine-outlet sizing envelope for the setup-07 meeting.

This is deliberately not a CFD result or a final geometry recommendation.  It
uses the authoritative setup-07 liquid feed and liquid density read back from
Fluent to show the area/diameter required at selected mean liquid velocities.
Pressure loss, flashing, cavitation, free-surface behaviour, level control and
downstream back-pressure are outside the calculation.
"""

from __future__ import annotations

import json
import math
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
OUTPUT_DIR = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"
MANIFEST_PATH = RUN_DIR / "qualification_manifest.json"
VISUAL_MANIFEST_PATH = OUTPUT_DIR / "visual_manifest.json"

BLUE = "#1769AA"
ORANGE = "#D97706"
INK = "#1F2933"
MID = "#5B6570"
GRID = "#D9DEE3"
PALE_BLUE = "#E8F1F8"
WHITE = "#FFFFFF"


def setup_style() -> None:
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


def style_axis(axis: plt.Axes, *, grid_axis: str = "both") -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#626B73")
    axis.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)


def load_inputs() -> tuple[float, float]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    mass_flow = float(manifest["adaptive_target_liquid_sink_kgs"])
    density = float(
        manifest["settings_readback"]["materials"]["fluid"]
        ["water-liquid-at-psep"]["density"]["value"]
    )
    return mass_flow, density


def build_data(mass_flow: float, density: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    volumetric_flow = mass_flow / density
    velocities = np.linspace(0.5, 6.0, 111)
    areas = volumetric_flow / velocities
    diameters = np.sqrt(4.0 * areas / math.pi)
    envelope = pd.DataFrame(
        {
            "mean_liquid_velocity_ms": velocities,
            "required_flow_area_m2": areas,
            "equivalent_circular_diameter_m": diameters,
            "liquid_mass_flow_kgs": mass_flow,
            "liquid_density_kgm3": density,
            "liquid_volumetric_flow_m3s": volumetric_flow,
        }
    )

    reference_diameters = np.array([0.20, 0.25, 0.30, 0.35, 0.40])
    reference_areas = math.pi * reference_diameters**2 / 4.0
    reference_velocities = volumetric_flow / reference_areas
    references = pd.DataFrame(
        {
            "equivalent_circular_diameter_m": reference_diameters,
            "flow_area_m2": reference_areas,
            "mean_liquid_velocity_ms": reference_velocities,
            "liquid_mass_flow_kgs": mass_flow,
            "liquid_density_kgm3": density,
        }
    )
    return envelope, references


def save_figure(envelope: pd.DataFrame, references: pd.DataFrame, mass_flow: float, density: float) -> dict[str, str]:
    setup_style()
    figure, axes = plt.subplots(1, 2, figsize=(12.2, 5.8))
    figure.suptitle(
        "Preliminary brine-outlet flow-area envelope",
        fontsize=16,
        fontweight="semibold",
        y=0.975,
    )
    figure.text(
        0.5,
        0.922,
        f"Kinematic continuity only • liquid feed {mass_flow:.2f} kg/s • Fluent density {density:.3f} kg/m³",
        ha="center",
        fontsize=10,
        color=MID,
    )

    axis = axes[0]
    axis.axvspan(1.0, 3.0, color=PALE_BLUE, alpha=0.8, label="illustrative 1–3 m/s window")
    axis.plot(
        envelope["mean_liquid_velocity_ms"],
        envelope["equivalent_circular_diameter_m"],
        color=BLUE,
        linewidth=2.4,
    )
    for velocity in (1.0, 2.0, 3.0):
        diameter = math.sqrt(4.0 * (mass_flow / density / velocity) / math.pi)
        axis.scatter([velocity], [diameter], color=ORANGE, s=38, zorder=3)
        axis.annotate(
            f"{diameter:.3f} m",
            (velocity, diameter),
            xytext=(7, 5),
            textcoords="offset points",
            fontsize=8.5,
            color=INK,
        )
    axis.set_title("Equivalent diameter versus mean liquid velocity", fontweight="semibold")
    axis.set_xlabel("Mean liquid velocity (m/s)")
    axis.set_ylabel("Equivalent circular diameter (m)")
    axis.set_xlim(0.5, 6.0)
    axis.legend(frameon=False, fontsize=8.2)
    style_axis(axis)

    axis = axes[1]
    labels = [f"{value:.2f} m" for value in references["equivalent_circular_diameter_m"]]
    bars = axis.barh(
        labels,
        references["mean_liquid_velocity_ms"],
        color=ORANGE,
        edgecolor="#9A5203",
        linewidth=0.8,
    )
    axis.bar_label(bars, fmt="%.2f m/s", padding=5, fontsize=9)
    axis.set_title("Velocity implied by reference outlet diameters", fontweight="semibold")
    axis.set_xlabel("Mean liquid velocity (m/s)")
    axis.set_ylabel("Equivalent circular diameter")
    axis.invert_yaxis()
    axis.set_xlim(0.0, max(references["mean_liquid_velocity_ms"]) * 1.22)
    style_axis(axis, grid_axis="x")

    figure.subplots_adjust(left=0.08, right=0.98, bottom=0.20, top=0.82, wspace=0.30)
    figure.text(
        0.01,
        0.025,
        "Planning aid only: excludes pressure loss, flashing/cavitation, downstream back-pressure, level control and multiphase outlet behaviour.",
        fontsize=8,
        color="#6B7280",
        ha="left",
    )
    paths: dict[str, str] = {}
    for suffix in ("png", "svg"):
        path = OUTPUT_DIR / f"24_preliminary_brine_outlet_area_envelope.{suffix}"
        figure.savefig(path, dpi=240)
        paths[suffix] = str(path)
    plt.close(figure)
    return paths


def write_note(mass_flow: float, density: float, references: pd.DataFrame) -> Path:
    volumetric_flow = mass_flow / density
    rows = []
    for row in references.itertuples(index=False):
        rows.append(
            f"| {row.equivalent_circular_diameter_m:.2f} | {row.flow_area_m2:.5f} | {row.mean_liquid_velocity_ms:.3f} |"
        )
    note = "\n".join(
        [
            "# Preliminary Brine-Outlet Flow-Area Envelope",
            "",
            "## Purpose",
            "",
            "Provide a mass-continuity starting point for Tuesday's geometry discussion. This is a planning aid, not a final outlet design or a CFD result.",
            "",
            "## Authoritative inputs",
            "",
            f"- Liquid mass flow: `{mass_flow:.2f} kg/s`.",
            f"- Fluent liquid material: `water-liquid-at-psep`, constant density `{density:.6f} kg/m3`.",
            f"- Corresponding liquid volumetric flow: `{volumetric_flow:.6f} m3/s`.",
            f"- Source: `{MANIFEST_PATH}` settings readback and control contract.",
            "",
            "## Calculation",
            "",
            "For a single circular liquid outlet, `Q = m_dot/rho`, `A = Q/U`, and `D = sqrt(4A/pi)`.",
            "",
            "| Diameter (m) | Area (m2) | Mean velocity (m/s) |",
            "|---:|---:|---:|",
            *rows,
            "",
            "At illustrative mean liquid velocities of 1, 2 and 3 m/s, the equivalent circular diameters are approximately 0.411, 0.291 and 0.237 m, respectively.",
            "",
            "## Limits before geometry selection",
            "",
            "This envelope does not determine the correct outlet elevation, water level, pipe direction, pressure-outlet value, downstream loss coefficient, flashing margin, cavitation margin, free-surface treatment, or required control strategy. Those must be resolved before the geometry is treated as a physical brine discharge.",
            "",
        ]
    )
    path = OUTPUT_DIR / "PRELIMINARY_BRINE_OUTLET_SIZING.md"
    path.write_text(note, encoding="utf-8")
    return path


def update_manifest(paths: dict[str, str], envelope_path: Path, references_path: Path, note_path: Path) -> None:
    manifest = json.loads(VISUAL_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest.setdefault("artifacts", {})["preliminary_brine_outlet_area_envelope"] = paths
    for path in (envelope_path, references_path):
        value = str(path)
        if value not in manifest.setdefault("data_exports", []):
            manifest["data_exports"].append(value)
    manifest["preliminary_brine_outlet_sizing_note"] = str(note_path)
    VISUAL_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    mass_flow, density = load_inputs()
    envelope, references = build_data(mass_flow, density)
    envelope_path = OUTPUT_DIR / "preliminary_brine_outlet_velocity_envelope.csv"
    references_path = OUTPUT_DIR / "preliminary_brine_outlet_reference_diameters.csv"
    envelope.to_csv(envelope_path, index=False)
    references.to_csv(references_path, index=False)
    paths = save_figure(envelope, references, mass_flow, density)
    note_path = write_note(mass_flow, density, references)
    update_manifest(paths, envelope_path, references_path, note_path)
    print(paths["png"])
    print(note_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
