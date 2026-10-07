"""Draw a conceptual separator process diagram for the research report.

This is an explanatory schematic, not a simulation result or a geometry drawing.
The physical routes follow Zarrouk and Purnanto (2015), Section 2, and Rizaldy,
Zarrouk and Morris (2016), Sections 2.2–2.3. No case-specific data are used.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    output = root / "Project" / "Final research report" / "figures"
    output.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
    fig, ax = plt.subplots(figsize=(12.6, 4.7))
    fig.patch.set_facecolor("white")
    ax.set_xlim(-0.05, 12.2)
    ax.set_ylim(-0.65, 4.65)
    ax.set_axis_off()

    neutral = "#334155"
    steam = "#2563eb"
    liquid = "#0f766e"
    entrainment = "#a16207"

    def box(x: float, y: float, width: float, height: float, text: str, color: str) -> None:
        patch = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.035,rounding_size=0.08",
            linewidth=1.4, edgecolor=color, facecolor="white",
        )
        ax.add_patch(patch)
        ax.text(x + width / 2, y + height / 2, text,
                ha="center", va="center", color=neutral, linespacing=1.45)

    def arrow(start: tuple[float, float], end: tuple[float, float], color: str,
              dashed: bool = False) -> None:
        ax.add_patch(FancyArrowPatch(
            start, end, arrowstyle="-|>", mutation_scale=15,
            linewidth=1.6, color=color,
            linestyle="--" if dashed else "-",
            shrinkA=2, shrinkB=4,
        ))

    box(0.10, 1.55, 2.20, 1.00, "Steam and brine\nTwo-phase feed", neutral)
    box(2.90, 1.55, 2.65, 1.00, "Spiral or tangential inlet\nRotating flow in vessel", neutral)
    box(6.20, 3.05, 2.65, 1.00, "Steam-rich core\nCentral collection pipe", steam)
    box(6.20, 0.05, 2.65, 1.00, "Liquid at wall\nFilm transport and drainage", liquid)
    box(9.45, 3.05, 2.55, 1.00, "Steam outlet\nAt bottom of BOC vessel", steam)
    box(9.45, 0.05, 2.55, 1.00, "Brine outlet\nCollected liquid discharge", liquid)

    arrow((2.30, 2.05), (2.90, 2.05), neutral)
    arrow((5.55, 2.35), (6.20, 3.55), steam)
    arrow((5.55, 1.75), (6.20, 0.55), liquid)
    arrow((8.85, 3.55), (9.45, 3.55), steam)
    arrow((8.85, 0.55), (9.45, 0.55), liquid)
    arrow((7.525, 1.05), (7.525, 3.05), entrainment, dashed=True)

    ax.text(7.75, 2.05, "Possible droplet\nentrainment from film",
            ha="left", va="center", color=entrainment, fontsize=11, linespacing=1.4)
    ax.text(6.10, 4.45, "Conceptual operation of a bottom-outlet cyclone separator",
            ha="center", va="center", color=neutral, fontsize=14)
    ax.text(6.10, -0.40, "Flow routes only; vessel geometry and computed flow rates are not shown.",
            ha="center", va="center", color=neutral, fontsize=10)

    fig.subplots_adjust(left=0.02, right=0.99, bottom=0.03, top=0.99)
    for extension in ("png", "svg"):
        fig.savefig(output / f"separator-operation.{extension}", dpi=220,
                    facecolor="white", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
