#!/usr/bin/env python3
"""Digitise Bangma-style steam-quality graph markers from a screenshot.

This is intentionally narrow and repeatable: it detects the plot grid, extracts
the blue diamonds, red squares, and green correlation markers, then converts
marker centres from pixels to graph coordinates.
"""

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = Path("/Users/andy/Desktop/Screenshot 2026-06-13 at 12.17.40\u202fPM.jpg")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "graph_digitization"
DEFAULT_POINTS_CSV = DEFAULT_OUTPUT_DIR / "bangma_reference_digitized_points.csv"
DEFAULT_FILTERED_CSV = DEFAULT_OUTPUT_DIR / "bangma_reference_digitized_points_y99p7_to_100.csv"
DEFAULT_OVERLAY = DEFAULT_OUTPUT_DIR / "bangma_reference_digitized_overlay.png"


@dataclass(frozen=True)
class PlotBox:
    x_left_px: float
    x_right_px: float
    y_top_px: float
    y_bottom_px: float


@dataclass(frozen=True)
class DigitizedPoint:
    series: str
    color: str
    x_mps: float
    steam_quality_pct: float
    pixel_x: float
    pixel_y: float
    component_area_px: int


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Digitise a Bangma-style graph screenshot.")
    parser.add_argument("--image", default=str(DEFAULT_IMAGE), help="Input graph screenshot.")
    parser.add_argument("--output-csv", default=str(DEFAULT_POINTS_CSV), help="All extracted points CSV.")
    parser.add_argument(
        "--filtered-output-csv",
        default=str(DEFAULT_FILTERED_CSV),
        help="CSV filtered to --filter-y-min/--filter-y-max. Use empty string to skip.",
    )
    parser.add_argument("--overlay", default=str(DEFAULT_OVERLAY), help="QA overlay image path.")
    parser.add_argument("--x-min", type=float, default=0.0)
    parser.add_argument("--x-max", type=float, default=80.0)
    parser.add_argument(
        "--y-top",
        type=float,
        default=99.4,
        help="Steam-quality value at the top visible horizontal gridline.",
    )
    parser.add_argument(
        "--y-bottom",
        type=float,
        default=100.0,
        help="Steam-quality value at the bottom visible horizontal gridline.",
    )
    parser.add_argument("--filter-y-min", type=float, default=99.7)
    parser.add_argument("--filter-y-max", type=float, default=100.0)
    return parser


def group_indices(indices: np.ndarray, *, max_gap: int = 2) -> list[tuple[int, int]]:
    if len(indices) == 0:
        return []
    groups: list[tuple[int, int]] = []
    start = previous = int(indices[0])
    for value in indices[1:]:
        value = int(value)
        if value - previous > max_gap:
            groups.append((start, previous))
            start = value
        previous = value
    groups.append((start, previous))
    return groups


def detect_plot_box(rgb: np.ndarray) -> PlotBox:
    height, width, _channels = rgb.shape
    x_start = max(0, int(width * 0.08))
    x_stop = min(width, int(width * 0.99))
    y_start = max(0, int(height * 0.28))
    y_stop = min(height, int(height * 0.90))

    roi = rgb[y_start:y_stop, x_start:x_stop].astype(int)
    mean = roi.mean(axis=2)
    spread = roi.max(axis=2) - roi.min(axis=2)
    gray_grid = (spread < 18) & (mean > 70) & (mean < 210)

    col_counts = gray_grid.sum(axis=0)
    row_counts = gray_grid.sum(axis=1)
    vertical_groups = group_indices(np.where(col_counts >= 120)[0])
    horizontal_groups = group_indices(np.where(row_counts >= 700)[0])

    if len(vertical_groups) < 2 or len(horizontal_groups) < 2:
        raise RuntimeError(
            f"Could not detect plot grid: {len(vertical_groups)} vertical, "
            f"{len(horizontal_groups)} horizontal lines"
        )

    x_left = x_start + sum(vertical_groups[0]) / 2.0
    x_right = x_start + sum(vertical_groups[-1]) / 2.0
    y_top = y_start + sum(horizontal_groups[0]) / 2.0
    y_bottom = y_start + sum(horizontal_groups[-1]) / 2.0
    return PlotBox(x_left_px=x_left, x_right_px=x_right, y_top_px=y_top, y_bottom_px=y_bottom)


def connected_components(mask: np.ndarray, min_area: int) -> list[np.ndarray]:
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    components: list[np.ndarray] = []

    for start_y, start_x in zip(*np.where(mask)):
        if seen[start_y, start_x]:
            continue

        stack = [(int(start_y), int(start_x))]
        seen[start_y, start_x] = True
        points: list[tuple[int, int]] = []
        while stack:
            y, x = stack.pop()
            points.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny = y + dy
                    nx = x + dx
                    if (
                        0 <= ny < height
                        and 0 <= nx < width
                        and mask[ny, nx]
                        and not seen[ny, nx]
                    ):
                        seen[ny, nx] = True
                        stack.append((ny, nx))

        if len(points) >= min_area:
            components.append(np.array(points, dtype=float))

    return components


def split_blue_component(component: np.ndarray) -> list[np.ndarray]:
    x_min = int(component[:, 1].min())
    x_max = int(component[:, 1].max())
    width = x_max - x_min + 1
    if width <= 45:
        return [component]

    y_min = int(component[:, 0].min())
    y_max = int(component[:, 0].max())
    submask = np.zeros((y_max - y_min + 1, width), dtype=bool)
    submask[(component[:, 0] - y_min).astype(int), (component[:, 1] - x_min).astype(int)] = True
    projection = submask.sum(axis=0)
    low_columns = np.where((projection > 0) & (projection <= max(5, projection.max() * 0.2)))[0]
    low_groups = [group for group in group_indices(low_columns, max_gap=1) if group[1] - group[0] >= 2]
    if not low_groups:
        return [component]

    split_group = max(low_groups, key=lambda group: group[1] - group[0])
    split_x = x_min + sum(split_group) / 2.0
    left = component[component[:, 1] < split_x]
    right = component[component[:, 1] >= split_x]
    if len(left) < 100 or len(right) < 100:
        return [component]
    return [left, right]


def component_center(component: np.ndarray, crop_x: int, crop_y: int) -> tuple[float, float, int]:
    return (
        float(component[:, 1].mean() + crop_x),
        float(component[:, 0].mean() + crop_y),
        int(len(component)),
    )


def pixel_to_data(
    pixel_x: float,
    pixel_y: float,
    box: PlotBox,
    *,
    x_min: float,
    x_max: float,
    y_top: float,
    y_bottom: float,
) -> tuple[float, float]:
    x_value = x_min + (pixel_x - box.x_left_px) / (box.x_right_px - box.x_left_px) * (x_max - x_min)
    y_value = y_top + (pixel_y - box.y_top_px) / (box.y_bottom_px - box.y_top_px) * (y_bottom - y_top)
    return x_value, y_value


def extract_points(rgb: np.ndarray, box: PlotBox, args: argparse.Namespace) -> list[DigitizedPoint]:
    crop_x = int(round(box.x_left_px))
    crop_y = int(round(box.y_top_px))
    crop = rgb[crop_y : int(round(box.y_bottom_px)) + 1, crop_x : int(round(box.x_right_px)) + 1]
    red = crop[:, :, 0].astype(int)
    green = crop[:, :, 1].astype(int)
    blue = crop[:, :, 2].astype(int)

    masks = {
        "Calculation": (
            "blue",
            (blue > 100) & (blue > red + 35) & (blue > green + 10) & (red < 140) & (green < 170),
            100,
        ),
        "Simulation": (
            "red",
            (red > 120) & (red > green + 35) & (red > blue + 35) & (green < 150) & (blue < 150),
            180,
        ),
        "Lazalde-Crabtree Correlation": (
            "green",
            (green > 110) & (green > red + 25) & (green > blue + 15) & (red < 100) & (blue < 180),
            200,
        ),
    }

    extracted: list[DigitizedPoint] = []
    for series, (color, mask, min_area) in masks.items():
        components = connected_components(mask, min_area=min_area)
        if series == "Calculation":
            split_components: list[np.ndarray] = []
            for component in components:
                split_components.extend(split_blue_component(component))
            components = split_components

        for component in components:
            width = component[:, 1].max() - component[:, 1].min() + 1
            height = component[:, 0].max() - component[:, 0].min() + 1
            if series in ("Simulation", "Lazalde-Crabtree Correlation") and (width > 38 or height > 38):
                continue
            if series == "Calculation" and (width > 42 or height > 45):
                continue

            pixel_x, pixel_y, area = component_center(component, crop_x, crop_y)
            x_value, y_value = pixel_to_data(
                pixel_x,
                pixel_y,
                box,
                x_min=args.x_min,
                x_max=args.x_max,
                y_top=args.y_top,
                y_bottom=args.y_bottom,
            )
            extracted.append(
                DigitizedPoint(
                    series=series,
                    color=color,
                    x_mps=x_value,
                    steam_quality_pct=y_value,
                    pixel_x=pixel_x,
                    pixel_y=pixel_y,
                    component_area_px=area,
                )
            )

    return sorted(extracted, key=lambda point: (point.series, point.x_mps))


def write_points_csv(path: Path, points: list[DigitizedPoint]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "series",
                "color",
                "x_mps",
                "steam_quality_pct",
                "pixel_x",
                "pixel_y",
                "component_area_px",
            ),
        )
        writer.writeheader()
        for point in points:
            writer.writerow(
                {
                    "series": point.series,
                    "color": point.color,
                    "x_mps": f"{point.x_mps:.4f}",
                    "steam_quality_pct": f"{point.steam_quality_pct:.4f}",
                    "pixel_x": f"{point.pixel_x:.2f}",
                    "pixel_y": f"{point.pixel_y:.2f}",
                    "component_area_px": point.component_area_px,
                }
            )


def write_overlay(image: Image.Image, box: PlotBox, points: list[DigitizedPoint], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    overlay = image.convert("RGB").copy()
    draw = ImageDraw.Draw(overlay)
    draw.rectangle(
        [(box.x_left_px, box.y_top_px), (box.x_right_px, box.y_bottom_px)],
        outline=(255, 165, 0),
        width=3,
    )
    colors = {
        "blue": (30, 90, 220),
        "red": (220, 30, 30),
        "green": (0, 170, 70),
    }
    for point in points:
        radius = 8
        fill = colors[point.color]
        draw.ellipse(
            [
                (point.pixel_x - radius, point.pixel_y - radius),
                (point.pixel_x + radius, point.pixel_y + radius),
            ],
            outline=fill,
            width=4,
        )
        draw.line(
            [(point.pixel_x - 11, point.pixel_y), (point.pixel_x + 11, point.pixel_y)],
            fill=fill,
            width=2,
        )
        draw.line(
            [(point.pixel_x, point.pixel_y - 11), (point.pixel_x, point.pixel_y + 11)],
            fill=fill,
            width=2,
        )
    overlay.save(path)


def main() -> int:
    args = build_parser().parse_args()
    image_path = Path(args.image).expanduser().resolve()
    image = Image.open(image_path).convert("RGB")
    rgb = np.array(image)
    box = detect_plot_box(rgb)
    points = extract_points(rgb, box, args)

    output_csv = Path(args.output_csv).expanduser().resolve()
    write_points_csv(output_csv, points)

    if args.filtered_output_csv:
        filtered = [
            point
            for point in points
            if args.filter_y_min <= point.steam_quality_pct <= args.filter_y_max
        ]
        write_points_csv(Path(args.filtered_output_csv).expanduser().resolve(), filtered)
    else:
        filtered = []

    overlay_path = Path(args.overlay).expanduser().resolve()
    write_overlay(image, box, points, overlay_path)

    print(
        "plot_box: "
        f"x={box.x_left_px:.1f}-{box.x_right_px:.1f}, "
        f"y={box.y_top_px:.1f}-{box.y_bottom_px:.1f}"
    )
    print(f"points_total: {len(points)}")
    print(f"points_filtered_{args.filter_y_min:g}_to_{args.filter_y_max:g}: {len(filtered)}")
    print(f"wrote_csv: {output_csv}")
    if args.filtered_output_csv:
        print(f"wrote_filtered_csv: {Path(args.filtered_output_csv).expanduser().resolve()}")
    print(f"wrote_overlay: {overlay_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
