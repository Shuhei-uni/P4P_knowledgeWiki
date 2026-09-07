#!/usr/bin/env python3
"""Build captioned meeting composites from verified setup-07 Fluent images."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"
FLUENT = OUTPUT / "fluent"

NAVY = "#14324A"
BLUE = "#2D6CDF"
ORANGE = "#E9822B"
RED = "#C23B22"
GREEN = "#2E7D32"
GREY = "#5C6770"


def load_crop(name: str, crop: tuple[int, int, int, int] = (0, 245, 1210, 1110)) -> Image.Image:
    path = FLUENT / name
    if not path.exists():
        raise FileNotFoundError(path)
    return Image.open(path).convert("RGB").crop(crop)


def save(fig: plt.Figure, stem: str) -> None:
    for suffix in ("png", "svg"):
        fig.savefig(OUTPUT / f"{stem}.{suffix}", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def pair_figure(
    left: Image.Image,
    right: Image.Image,
    *,
    title: str,
    subtitle: str,
    left_title: str,
    right_title: str,
    footer: str,
    stem: str,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(15, 7.6), constrained_layout=True)
    fig.suptitle(title, fontsize=23, color=NAVY, fontweight="bold")
    fig.text(0.5, 0.925, subtitle, ha="center", va="top", fontsize=12.5, color=GREY)
    for ax, image, heading in zip(axes, (left, right), (left_title, right_title), strict=True):
        ax.imshow(image)
        ax.set_title(heading, fontsize=16, color=NAVY, fontweight="bold", pad=10)
        ax.axis("off")
    fig.text(0.5, 0.012, footer, ha="center", va="bottom", fontsize=11.5, color=GREY)
    save(fig, stem)


def build_liquid_comparison() -> None:
    pair_figure(
        load_crop("closed4000_phase2_liquid_volume_fraction_zoom0p05_xm1p5.png"),
        load_crop("closed6000_phase2_liquid_volume_fraction_zoom0p05_xm1p5.png"),
        title="Liquid-rich wall region expands as the steady solver continues",
        subtitle="Same 900k mesh, x = −1.5 m section, cell values, and fixed liquid volume-fraction range 0–0.05",
        left_title="Iteration 4000  |  liquid inventory 104.05 kg",
        right_title="Iteration 6000  |  liquid inventory 171.03 kg",
        footer=(
            "Diagnostic steady-solver iterates—not physical time. The clipped 0–0.05 scale is used only to reveal "
            "low-volume liquid structure; the full 0–1 exports are preserved separately."
        ),
        stem="06_closed_bottom_liquid_field_comparison",
    )


def build_pressure_comparison() -> None:
    pair_figure(
        load_crop("closed4000_static_pressure_xm1p5.png"),
        load_crop("closed6000_static_pressure_xm1p5.png"),
        title="Pressure field also shifts between iterations 4000 and 6000",
        subtitle="Same 900k mesh, x = −1.5 m section, cell values, and fixed absolute static-pressure range 1.10–1.20 MPa",
        left_title="Iteration 4000  |  pressure drop 31.03 kPa",
        right_title="Iteration 6000  |  pressure drop 34.05 kPa",
        footer=(
            "Pressure drop rose 9.7% while liquid inventory rose 64.4%; the closed-bottom solution was not "
            "iteration-independent over this diagnostic extension."
        ),
        stem="07_closed_bottom_pressure_field_comparison",
    )


def build_sink_and_swirl() -> None:
    mask = load_crop("sink07c_thick_sink_mask_xm1p5.png")
    paths = load_crop("sink07c_carrier_pathlines_from_liquidinlet.png", crop=(0, 245, 1280, 1110))
    fig, axes = plt.subplots(1, 2, figsize=(15, 7.8), constrained_layout=True)
    fig.suptitle("The diagnostic sink targets a bottom band, while the carrier field remains strongly swirling", fontsize=21, color=NAVY, fontweight="bold")
    fig.text(
        0.5,
        0.925,
        "Setup 07c: 0.140165 m bottom-local band, τ = 0.1 s, full-strength endpoint; DPM off",
        ha="center",
        va="top",
        fontsize=12.5,
        color=GREY,
    )
    axes[0].imshow(mask)
    axes[0].set_title("Sink mask (red = active band)", fontsize=16, color=NAVY, fontweight="bold")
    axes[1].imshow(paths)
    axes[1].set_title("Carrier pathlines from liquid inlet", fontsize=16, color=NAVY, fontweight="bold")
    for ax in axes:
        ax.axis("off")
    fig.text(
        0.5,
        0.012,
        "The sink removed 22.49 kg/s (19.2% of liquid inlet), leaving 94.43 kg/s unclosed. "
        "Pathlines are Mixture-model carrier trajectories colored by velocity—not droplets or DPM tracks.",
        ha="center",
        va="bottom",
        fontsize=11.5,
        color=GREY,
    )
    save(fig, "08_sink_band_and_carrier_swirl")


def build_decision_summary() -> None:
    inventory = Image.open(OUTPUT / "01_closed_bottom_inventory_pressure.png").convert("RGB")
    closure = Image.open(OUTPUT / "04_endpoint_liquid_rate_closure.png").convert("RGB")
    liquid = Image.open(OUTPUT / "06_closed_bottom_liquid_field_comparison.png").convert("RGB")
    sink = Image.open(OUTPUT / "08_sink_band_and_carrier_swirl.png").convert("RGB")
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    fig.suptitle("Tuesday decision summary: resolve the brine outlet before restarting mesh convergence", fontsize=24, color=NAVY, fontweight="bold")
    panels = (
        (inventory, "1. Closed bottom: inventory and pressure do not settle"),
        (liquid, "2. Spatial evidence: the liquid-rich wall region expands"),
        (closure, "3. Thick sink improves removal but does not close liquid rate"),
        (sink, "4. Next model change: replace the surrogate with a resolved brine outlet"),
    )
    for ax, (image, heading) in zip(axes.flat, panels, strict=True):
        ax.imshow(image)
        ax.set_title(heading, fontsize=14, color=NAVY, fontweight="bold", pad=8)
        ax.axis("off")
    fig.text(
        0.5,
        0.008,
        "Classification: diagnostic / unresolved. Do not claim mesh convergence, separator efficiency, a physical free surface, or physical-time accumulation from these results.",
        ha="center",
        va="bottom",
        fontsize=12,
        color=RED,
        fontweight="bold",
    )
    save(fig, "09_tuesday_decision_summary")


def update_manifest() -> None:
    manifest_path = OUTPUT / "visual_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("artifacts", {})
    for key, stem in {
        "closed_bottom_liquid_field": "06_closed_bottom_liquid_field_comparison",
        "closed_bottom_pressure_field": "07_closed_bottom_pressure_field_comparison",
        "sink_band_and_carrier_swirl": "08_sink_band_and_carrier_swirl",
        "tuesday_decision_summary": "09_tuesday_decision_summary",
    }.items():
        artifacts[key] = {
            "png": str(OUTPUT / f"{stem}.png"),
            "svg": str(OUTPUT / f"{stem}.svg"),
        }

    manifest["meeting_brief"] = str(OUTPUT / "MEETING_BRIEF.md")
    manifest["fluent_graphics_manifest"] = str(FLUENT / "fluent_graphics_manifest.json")
    manifest["graphics_provenance"] = {
        "fluent_version": "Ansys Fluent 2024 R2",
        "postprocessing_only": True,
        "solver_iterations_run": 0,
        "dpm_interaction": False,
        "plane": "yz-plane at x=-1.5 m",
        "contour_sampling": "cell values (node_values=False)",
        "fixed_ranges": {
            "liquid_volume_fraction_diagnostic": [0.0, 0.05],
            "liquid_volume_fraction_full": [0.0, 1.0],
            "absolute_static_pressure_pa": [1100000.0, 1200000.0],
        },
        "pathline_definition": "Mixture-model carrier trajectories released from liquidinlet and colored by velocity; not DPM particle tracks",
        "final_live_state": "setup-07c saved ramp-reset final restored; DPM read back off",
    }
    manifest["accepted_fluent_exports"] = [
        str(FLUENT / name)
        for name in (
            "closed4000_phase2_liquid_volume_fraction_xm1p5.png",
            "closed4000_phase2_liquid_volume_fraction_zoom0p05_xm1p5.png",
            "closed4000_static_pressure_xm1p5.png",
            "closed6000_phase2_liquid_volume_fraction_xm1p5.png",
            "closed6000_phase2_liquid_volume_fraction_zoom0p05_xm1p5.png",
            "closed6000_static_pressure_xm1p5.png",
            "closed6000_carrier_pathlines_from_liquidinlet.png",
            "sink07c_phase2_liquid_volume_fraction_xm1p5.png",
            "sink07c_phase2_liquid_volume_fraction_zoom0p05_xm1p5.png",
            "sink07c_static_pressure_xm1p5.png",
            "sink07c_thick_sink_mask_xm1p5.png",
            "sink07c_carrier_pathlines_from_liquidinlet.png",
        )
    ]
    manifest["excluded_fluent_exports"] = {
        str(FLUENT / "sink07c_boundary_map.png"): "Rejected because the boundary display/readback did not preserve every required named zone.",
        str(FLUENT / "sink07c_static_gauge_pressure_xm1p5.png"): "Superseded by the correctly scaled absolute-static-pressure export.",
        "steaminlet_pathlines": "Not exported because the pathline release-surface readback did not match steaminlet; no ambiguous image is used.",
        "closed3000_exports": "Preserved as diagnostic raw files but excluded from the meeting composites; the matched quantitative comparison is iteration 4000 versus 6000.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build_liquid_comparison()
    build_pressure_comparison()
    build_sink_and_swirl()
    build_decision_summary()
    update_manifest()
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
