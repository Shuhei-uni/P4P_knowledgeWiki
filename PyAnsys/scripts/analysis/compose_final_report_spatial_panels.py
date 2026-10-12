"""Compose report panels from saved native Fluent graphics.

Only blank margins, native annotations and colour-bar surroundings are cropped.
The scientific field pixels are not recoloured or reconstructed. The shared
legend uses pixels from the original Fluent legend, rather than an assumed
Matplotlib colour map. Project records establish the common 0–1 contour range.
Run with PyAnsys/.venv/bin/python from any working directory.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "Project/meetings/Poster/poster-sections/poster mesh assets"
REPORT = ROOT / "Project/Final research report/figures"
INLET_CROP = (210, 100, 2190, 1700)
CENTRE_CROP = (540, 75, 1260, 2320)
LEGEND_SOURCE = ASSETS / "F1-26.81-N10000-inlet-liquid-volume-fraction-range-0-1.png"
LEGEND_CROP = (60, 602, 61, 1239)


@dataclass(frozen=True)
class Panel:
    path: Path
    crop: tuple[int, int, int, int]
    label: str
    case: str
    cells: int
    section: str
    iteration: int | None = None

    def pixels(self) -> np.ndarray:
        with Image.open(self.path) as source:
            return np.asarray(source.convert("RGB").crop(self.crop))

    def provenance(self) -> dict:
        return {
            "path": str(self.path.relative_to(ROOT)),
            "sha256": sha256(self.path),
            "crop_pixels_left_top_right_bottom": self.crop,
            "label": self.label,
            "case": self.case,
            "mesh_cells": self.cells,
            "section": self.section,
            "saved_iteration": self.iteration,
        }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_native_palettes(panels: list[Panel]) -> dict:
    """Check native colour bars, excluding antialiased borders and labels."""
    reference = None
    checks = []
    for panel in panels:
        if panel.iteration is None:
            continue
        # The F2 vertical export has no visible legend; its 0–1 range is
        # established by the linked owning Project result record.
        if panel.path.name == "F2-26.81-n10000-liquid.png":
            continue
        with Image.open(panel.path) as image:
            margin = np.asarray(image.convert("RGB"))[:, :150]
        coloured = np.ptp(margin.astype(int), axis=2) > 100
        y, x = np.where(coloured)
        centre_x = (x.min() + x.max()) // 2
        rows = np.where(coloured[:, centre_x])[0]
        profile = margin[rows.min() + 1 : rows.max(), centre_x]
        indices = np.linspace(0.05 * (len(profile) - 1), 0.95 * (len(profile) - 1), 19).round().astype(int)
        samples = profile[indices].astype(int)
        if reference is None:
            reference = samples
        maximum_difference = int(np.abs(samples - reference).max())
        if maximum_difference > 3:
            raise ValueError(f"Native colour bar differs: {panel.path.name}")
        checks.append({"source": str(panel.path.relative_to(ROOT)),
                       "maximum_sampled_RGB_channel_difference": maximum_difference})
    return {"method": "19 equally spaced samples from 5–95% of native colour-bar height, excluding border pixels",
            "allowed_RGB_channel_difference": 3, "checks": checks}


def add_panel(ax: plt.Axes, panel: Panel) -> None:
    # Antialias mesh line graphics when reducing them to report width. Scalar
    # field graphics retain nearest-neighbour display of their native pixels.
    interpolation = "hanning" if panel.iteration is None else "nearest"
    ax.imshow(panel.pixels(), interpolation=interpolation)
    ax.set_axis_off()
    ax.set_title(panel.label, fontsize=10, pad=8, linespacing=1.25)


def add_native_legend(fig: plt.Figure, bounds: tuple[float, ...]) -> None:
    with Image.open(LEGEND_SOURCE) as source:
        # Reverse top-to-bottom native pixels to place zero at the left.
        native = np.asarray(source.convert("RGB").crop(LEGEND_CROP))
    horizontal = native[::-1].transpose(1, 0, 2)
    ax = fig.add_axes(bounds)
    ax.imshow(horizontal, extent=(0, 1, 0, 1), aspect="auto", interpolation="nearest")
    ax.set_yticks([])
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.tick_params(axis="x", labelsize=10, length=3)
    ax.set_title("Bulk-liquid volume fraction (shared 0–1 scale)", fontsize=10, pad=7)
    for spine in ax.spines.values():
        spine.set_linewidth(0.6)


def save(fig: plt.Figure, stem: str, panels: list[Panel], caption_basis: list[Path]) -> None:
    output = REPORT / f"{stem}.png"
    fig.savefig(output, dpi=300, facecolor="white")
    plt.close(fig)
    source_records = []
    for path in caption_basis:
        source_records.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path)})
    manifest = {
        "output": str(output.relative_to(ROOT)),
        "output_sha256": sha256(output),
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "panels": [panel.provenance() for panel in panels],
        "contour_range": [0.0, 1.0],
        "native_palette_verification": verify_native_palettes(panels),
        "legend": {
            "source": str(LEGEND_SOURCE.relative_to(ROOT)),
            "source_sha256": sha256(LEGEND_SOURCE),
            "crop_pixels_left_top_right_bottom": LEGEND_CROP,
            "method": "Native colour-bar centre-column pixels, reversed into a horizontal bar; no assumed colour map",
        },
        "range_and_case_evidence": source_records,
        "operations": [
            "Crop export margins and native annotations outside the scientific fields",
            "Display scalar-field crops with native RGB values and nearest-neighbour graphic interpolation",
            "Antialias mesh-line graphics when reducing the saved raster to report width; no mesh geometry changes",
            "Use the same crop and panel size within each matched view pair",
            "Add report-size case labels and a shared legend from native export pixels",
        ],
        "limits": [
            "No scientific fields were calculated, recoloured, interpolated in space or replaced",
            "The historical mesh/inlet/numerical package differs from the reconstruction; this is not an isolated mesh effect",
            "The 342,609-cell illustration is excluded: no solved liquid field is supplied for it in the poster comparison",
            "Source images and Project records are present; some linked original machine export manifests are absent from this checkout",
            "Horizontal and vertical views in the inlet figure use different display magnification; each mixed/split pair has equal magnification",
        ],
        "figure_size_inches": list(fig.get_size_inches()),
        "dpi": 300,
    }
    output.with_suffix(".provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    comparison = ROOT / "Project/meetings/Poster/poster-sections/mesh-and-volume-fraction-comparison.md"
    inlet_results = ROOT / "Project/experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline"
    mesh_panels = [
        Panel(ASSETS / "08b-tetrahedral-mesh-inlet-section.png", INLET_CROP,
              "(a) Historical tetrahedral mesh\n7,601,261 cells", "08b historical split feed", 7_601_261, "Own inlet midpoint"),
        Panel(ASSETS / "mesh60k-inlet-section.png", INLET_CROP,
              "(b) Polyhedral–hexahedral mesh\n60,964 cells", "F0 mesh", 60_964, "Inlet midpoint"),
        Panel(ASSETS / "08b-N10000-inlet-liquid-volume-fraction.png", INLET_CROP,
              "(c) Historical split feed\nSaved iteration 10,000", "08b historical split feed", 7_601_261, "Own inlet midpoint", 10_000),
        Panel(ASSETS / "F0-26.81-N10000-inlet-liquid-volume-fraction-range-0-1.png", INLET_CROP,
              "(d) Mixed feed; SIMPLE\nSaved iteration 10,000", "F0 mixed feed SIMPLE, nominal 26.81 m/s", 60_964, "Inlet midpoint", 10_000),
    ]
    fig, axs = plt.subplots(2, 2, figsize=(7.5, 6.8))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.94, bottom=0.14, wspace=0.06, hspace=0.25)
    for ax, panel in zip(axs.flat, mesh_panels, strict=True):
        add_panel(ax, panel)
    add_native_legend(fig, (0.27, 0.07, 0.46, 0.023))
    save(fig, "results-mesh-spatial-comparison", mesh_panels, [comparison])

    inlet_panels = [
        Panel(ASSETS / "F1-26.81-N10000-inlet-liquid-volume-fraction-range-0-1.png", INLET_CROP,
              "(a) Mixed feed\nInlet-height section", "F1 mixed feed Coupled, nominal 26.81 m/s", 60_964, "y = 2.065999985 m", 10_000),
        Panel(ASSETS / "F2-26.81-N10000-inlet-liquid-volume-fraction-range-0-1.png", INLET_CROP,
              "(b) Split feed\nInlet-height section", "F2 split feed Coupled, nominal 26.81 m/s", 60_964, "y = 2.065999985 m", 10_000),
        Panel(ASSETS / "F1-26.81-N10000-side-liquid-volume-fraction.png", CENTRE_CROP,
              "(c) Mixed feed\nCentre section", "F1 mixed feed Coupled, nominal 26.81 m/s", 60_964, "z = 0 m", 10_000),
        Panel(inlet_results / "f2-split-inlet/figures/F2-26.81-n10000-liquid.png", CENTRE_CROP,
              "(d) Split feed\nCentre section", "F2 split feed Coupled, nominal 26.81 m/s", 60_964, "z = 0 m", 10_000),
    ]
    fig = plt.figure(figsize=(8.0, 4.0))
    grid = fig.add_gridspec(1, 4, width_ratios=(2.65, 2.65, 1.15, 1.15),
                            left=0.015, right=0.985, bottom=0.22, top=0.81, wspace=0.12)
    for index, panel in enumerate(inlet_panels):
        add_panel(fig.add_subplot(grid[0, index]), panel)
    fig.suptitle("Same 60,964-cell mesh; nominal 26.81 m/s; iteration 10,000", fontsize=11, y=0.97)
    add_native_legend(fig, (0.26, 0.10, 0.48, 0.030))
    save(fig, "results-inlet-spatial-comparison", inlet_panels,
         [comparison, inlet_results / "f1-one-inlet/results.md", inlet_results / "f2-split-inlet/results.md"])


if __name__ == "__main__":
    main()
