#!/usr/bin/env python3
"""Build the meeting-ready brine-outlet boundary-condition decision graphic."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"
VISUAL_MANIFEST_PATH = OUTPUT_DIR / "visual_manifest.json"

BLUE = "#1769AA"
ORANGE = "#D97706"
INK = "#1F2933"
MID = "#5B6570"
PALE_BLUE = "#E8F1F8"
PALE_ORANGE = "#FFF1DF"
PALE_GREY = "#F1F3F5"
WHITE = "#FFFFFF"


def add_card(axis: plt.Axes, x: float, y: float, width: float, height: float, *, title: str, body: str, face: str, edge: str) -> None:
    card = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.4,
        edgecolor=edge,
        facecolor=face,
        transform=axis.transAxes,
    )
    axis.add_patch(card)
    axis.text(x + 0.022, y + height - 0.055, title, transform=axis.transAxes, fontsize=10.7, fontweight="semibold", va="top", color=INK)
    wrapped_lines: list[str] = []
    for line in body.splitlines():
        if not line:
            wrapped_lines.append("")
        elif line.startswith("• "):
            wrapped_lines.append(
                textwrap.fill(line, width=43, subsequent_indent="  ")
            )
        else:
            wrapped_lines.append(textwrap.fill(line, width=38))
    axis.text(
        x + 0.022,
        y + height - 0.125,
        "\n".join(wrapped_lines),
        transform=axis.transAxes,
        fontsize=8.15,
        va="top",
        color=INK,
        linespacing=1.36,
    )


def main() -> int:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "figure.facecolor": WHITE,
            "savefig.facecolor": WHITE,
            "savefig.bbox": "tight",
        }
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(12.2, 6.7))
    axis.set_axis_off()
    figure.suptitle(
        "Brine-outlet boundary condition: staged Fluent plan",
        fontsize=17,
        fontweight="semibold",
        y=0.972,
        color=INK,
    )
    figure.text(
        0.5,
        0.915,
        "Mixture carrier model • intended liquid discharge • geometry and downstream condition still to be confirmed",
        ha="center",
        fontsize=10,
        color=MID,
    )

    add_card(
        axis,
        0.035,
        0.33,
        0.285,
        0.47,
        title="1  Preferred physical first case",
        body=(
            "PRESSURE OUTLET\n\n"
            "• Use when downstream static pressure is known or defensibly estimated.\n"
            "• Fluent solves the discharged mass flow from the field.\n"
            "• Specify secondary-phase backflow treatment and monitor any reversal.\n"
            "• Extend the outlet so the boundary is away from vessel recirculation."
        ),
        face=PALE_BLUE,
        edge=BLUE,
    )
    add_card(
        axis,
        0.357,
        0.33,
        0.285,
        0.47,
        title="2  Diagnostic rate bracket",
        body=(
            "MASS-FLOW OUTLET\n\n"
            "• Prescribe 116.92 kg/s only as a controlled diagnostic if the flow is strictly outward and liquid-dominant.\n"
            "• Useful when the required rate is known but downstream pressure is not.\n"
            "• It forces rate and lets pressure respond; it does not validate drain hydraulics."
        ),
        face=PALE_ORANGE,
        edge=ORANGE,
    )
    add_card(
        axis,
        0.679,
        0.33,
        0.285,
        0.47,
        title="3  Avoid for the first rebuild",
        body=(
            "OUTFLOW\n\n"
            "• Assumes an approximately fully developed exit with small streamwise gradients.\n"
            "• Recirculation or inflow makes the boundary less defensible and can hurt convergence.\n"
            "• Current separator evidence already shows outlet-reversal sensitivity."
        ),
        face=PALE_GREY,
        edge=MID,
    )

    axis.annotate("", xy=(0.345, 0.565), xytext=(0.326, 0.565), xycoords="axes fraction", arrowprops={"arrowstyle": "->", "color": MID, "lw": 1.5})
    axis.annotate("", xy=(0.667, 0.565), xytext=(0.648, 0.565), xycoords="axes fraction", arrowprops={"arrowstyle": "->", "color": MID, "lw": 1.5})

    footer = FancyBboxPatch(
        (0.035, 0.075),
        0.929,
        0.17,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.0,
        edgecolor="#AAB2BA",
        facecolor=WHITE,
        transform=axis.transAxes,
    )
    axis.add_patch(footer)
    axis.text(0.055, 0.215, "Acceptance evidence required for either first case", transform=axis.transAxes, fontsize=11.5, fontweight="semibold", color=INK, va="top")
    axis.text(
        0.055,
        0.160,
        "Complete phase/mixture mass balance  •  stable liquid inventory and pressure drop  •  outward brine flux  •  stable outlet phase split\n"
        "velocity/swirl monitor stability  •  residual level and trend  •  boundary-condition sensitivity if downstream pressure is uncertain",
        transform=axis.transAxes,
        fontsize=9.2,
        color=INK,
        va="top",
        linespacing=1.45,
    )
    figure.text(
        0.01,
        0.018,
        "Based on Ansys Fluent 2024 R2 boundary-condition and Mixture-model guidance. This is a setup plan, not a validated outlet model.",
        fontsize=8,
        color="#6B7280",
    )

    paths: dict[str, str] = {}
    for suffix in ("png", "svg"):
        path = OUTPUT_DIR / f"25_brine_outlet_boundary_condition_decision.{suffix}"
        figure.savefig(path, dpi=240)
        paths[suffix] = str(path)
    plt.close(figure)

    manifest = json.loads(VISUAL_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest.setdefault("artifacts", {})["brine_outlet_boundary_condition_decision"] = paths
    manifest["brine_outlet_boundary_condition_decision_note"] = str(
        OUTPUT_DIR / "BRINE_OUTLET_BOUNDARY_CONDITION_DECISION.md"
    )
    VISUAL_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(paths["png"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
