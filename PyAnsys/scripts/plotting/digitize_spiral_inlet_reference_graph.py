#!/usr/bin/env python3
"""Digitize the spiral-inlet steam-quality reference graph."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from digitize_bangma_reference_graph import (
    DigitizedPoint,
    PlotBox,
    connected_components,
    group_indices,
    pixel_to_data,
    write_overlay,
    write_points_csv,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "graph_digitization"
DEFAULT_IMAGE = DEFAULT_OUTPUT_DIR / "spiral_inlet_reference_source.jpg"
DEFAULT_POINTS_CSV = DEFAULT_OUTPUT_DIR / "spiral_inlet_reference_digitized_points.csv"
DEFAULT_FILTERED_CSV = (
    DEFAULT_OUTPUT_DIR / "spiral_inlet_reference_digitized_points_y99p7_to_100.csv"
)
DEFAULT_OVERLAY = DEFAULT_OUTPUT_DIR / "spiral_inlet_reference_digitized_overlay.png"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default=str(DEFAULT_IMAGE))
    parser.add_argument("--output-csv", default=str(DEFAULT_POINTS_CSV))
    parser.add_argument("--filtered-output-csv", default=str(DEFAULT_FILTERED_CSV))
    parser.add_argument("--overlay", default=str(DEFAULT_OVERLAY))
    parser.add_argument("--x-min", type=float, default=0.0)
    parser.add_argument("--x-max", type=float, default=80.0)
    parser.add_argument("--y-top", type=float, default=99.4)
    parser.add_argument("--y-bottom", type=float, default=100.0)
    parser.add_argument("--filter-y-min", type=float, default=99.7)
    parser.add_argument("--filter-y-max", type=float, default=100.0)
    return parser


def detect_strong_plot_box(rgb: np.ndarray) -> PlotBox:
    """Detect the regularly spaced grid while rejecting text near the y-axis."""
    height, width, _channels = rgb.shape
    x_start = max(0, int(width * 0.08))
    x_stop = min(width, int(width * 0.99))
    y_start = max(0, int(height * 0.28))
    y_stop = min(height, int(height * 0.90))

    roi = rgb[y_start:y_stop, x_start:x_stop].astype(int)
    mean = roi.mean(axis=2)
    spread = roi.max(axis=2) - roi.min(axis=2)
    gray_grid = (spread < 18) & (mean > 70) & (mean < 210)

    column_counts = gray_grid.sum(axis=0)
    row_counts = gray_grid.sum(axis=1)
    minimum_column_strength = max(120, int(roi.shape[0] * 0.35))
    minimum_row_strength = max(500, int(roi.shape[1] * 0.30))
    vertical_groups = group_indices(np.where(column_counts >= minimum_column_strength)[0])
    horizontal_groups = group_indices(np.where(row_counts >= minimum_row_strength)[0])

    if len(vertical_groups) < 2 or len(horizontal_groups) < 2:
        raise RuntimeError(
            f"Could not detect strong plot grid: {len(vertical_groups)} vertical, "
            f"{len(horizontal_groups)} horizontal lines"
        )

    return PlotBox(
        x_left_px=x_start + sum(vertical_groups[0]) / 2.0,
        x_right_px=x_start + sum(vertical_groups[-1]) / 2.0,
        y_top_px=y_start + sum(horizontal_groups[0]) / 2.0,
        y_bottom_px=y_start + sum(horizontal_groups[-1]) / 2.0,
    )


def component_dimensions(component: np.ndarray) -> tuple[float, float]:
    return float(np.ptp(component[:, 1]) + 1), float(np.ptp(component[:, 0]) + 1)


def inside_plot(component: np.ndarray, box: PlotBox) -> bool:
    x = float(component[:, 1].mean())
    y = float(component[:, 0].mean())
    return (
        box.x_left_px - 30 <= x <= box.x_right_px + 30
        and box.y_top_px - 30 <= y <= box.y_bottom_px + 30
    )


def split_touching_markers(components: list[np.ndarray]) -> list[np.ndarray]:
    """Split a horizontally merged pair using the normal marker width."""
    widths = [component_dimensions(component)[0] for component in components]
    normal_width = float(np.median(widths))
    split_components: list[np.ndarray] = []

    for component, width in zip(components, widths):
        if width <= normal_width * 1.45:
            split_components.append(component)
            continue

        split_x = (float(component[:, 1].min()) + float(component[:, 1].max())) / 2.0
        left = component[component[:, 1] <= split_x]
        right = component[component[:, 1] > split_x]
        if len(left) < 300 or len(right) < 300:
            raise RuntimeError("Could not reliably split touching graph markers")
        split_components.extend((left, right))

    return split_components


def colored_marker_components(rgb: np.ndarray, box: PlotBox) -> dict[str, list[np.ndarray]]:
    red = rgb[:, :, 0].astype(int)
    green = rgb[:, :, 1].astype(int)
    blue = rgb[:, :, 2].astype(int)

    blue_mask = (
        (blue > 100)
        & (blue > red + 35)
        & (blue > green + 10)
        & (red < 140)
        & (green < 170)
    )
    red_mask = (
        (red > 120)
        & (red > green + 35)
        & (red > blue + 35)
        & (green < 150)
        & (blue < 150)
    )
    purple_outline_mask = (
        (blue > red + 15)
        & (blue > green + 15)
        & (red > 70)
        & (green > 60)
        & (blue > 105)
        & (red < 190)
        & (green < 190)
    )

    calculation = [
        component
        for component in connected_components(blue_mask, min_area=500)
        if inside_plot(component, box)
        and component_dimensions(component)[0] <= 125
        and component_dimensions(component)[1] <= 85
    ]
    simulation = [
        component
        for component in connected_components(red_mask, min_area=500)
        if inside_plot(component, box)
        and component_dimensions(component)[0] <= 110
        and component_dimensions(component)[1] <= 75
    ]
    correlation = [
        component
        for component in connected_components(purple_outline_mask, min_area=250)
        if inside_plot(component, box)
        and 250 <= len(component) <= 800
        and 35 <= component_dimensions(component)[0] <= 70
        and 28 <= component_dimensions(component)[1] <= 65
    ]

    return {
        "Calculation": split_touching_markers(calculation),
        "Simulation": split_touching_markers(simulation),
        "Lazalde-Crabtree Correlation": correlation,
    }


def component_center(component: np.ndarray, *, use_bbox_center: bool) -> tuple[float, float]:
    if use_bbox_center:
        return (
            (float(component[:, 1].min()) + float(component[:, 1].max())) / 2.0,
            (float(component[:, 0].min()) + float(component[:, 0].max())) / 2.0,
        )
    return float(component[:, 1].mean()), float(component[:, 0].mean())


def extract_points(rgb: np.ndarray, box: PlotBox, args: argparse.Namespace) -> list[DigitizedPoint]:
    colors = {
        "Calculation": "blue",
        "Simulation": "red",
        "Lazalde-Crabtree Correlation": "green",
    }
    components_by_series = colored_marker_components(rgb, box)
    counts = {series: len(components) for series, components in components_by_series.items()}
    if any(count != 6 for count in counts.values()):
        raise RuntimeError(f"Expected six points per series, got {counts}")

    points: list[DigitizedPoint] = []
    for series, components in components_by_series.items():
        for component in components:
            pixel_x, pixel_y = component_center(
                component,
                use_bbox_center=series == "Lazalde-Crabtree Correlation",
            )
            x_value, y_value = pixel_to_data(
                pixel_x,
                pixel_y,
                box,
                x_min=args.x_min,
                x_max=args.x_max,
                y_top=args.y_top,
                y_bottom=args.y_bottom,
            )
            y_value = min(args.y_bottom, max(args.y_top, y_value))
            points.append(
                DigitizedPoint(
                    series=series,
                    color=colors[series],
                    x_mps=x_value,
                    steam_quality_pct=y_value,
                    pixel_x=pixel_x,
                    pixel_y=pixel_y,
                    component_area_px=int(len(component)),
                )
            )

    return sorted(points, key=lambda point: (point.series, point.x_mps))


def main() -> int:
    args = build_parser().parse_args()
    image_path = Path(args.image).expanduser().resolve()
    image = Image.open(image_path).convert("RGB")
    rgb = np.array(image)
    box = detect_strong_plot_box(rgb)
    points = extract_points(rgb, box, args)

    output_csv = Path(args.output_csv).expanduser().resolve()
    write_points_csv(output_csv, points)
    filtered = [
        point
        for point in points
        if args.filter_y_min <= point.steam_quality_pct <= args.filter_y_max
    ]
    filtered_output = Path(args.filtered_output_csv).expanduser().resolve()
    write_points_csv(filtered_output, filtered)

    overlay_path = Path(args.overlay).expanduser().resolve()
    write_overlay(image, box, points, overlay_path)

    counts = {
        series: sum(point.series == series for point in points)
        for series in ("Calculation", "Simulation", "Lazalde-Crabtree Correlation")
    }
    print(
        "plot_box: "
        f"x={box.x_left_px:.1f}-{box.x_right_px:.1f}, "
        f"y={box.y_top_px:.1f}-{box.y_bottom_px:.1f}"
    )
    print(f"series_counts: {counts}")
    print(f"points_total: {len(points)}")
    print(f"points_filtered_{args.filter_y_min:g}_to_{args.filter_y_max:g}: {len(filtered)}")
    print(f"wrote_csv: {output_csv}")
    print(f"wrote_filtered_csv: {filtered_output}")
    print(f"wrote_overlay: {overlay_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
