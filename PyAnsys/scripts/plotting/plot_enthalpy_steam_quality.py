#!/usr/bin/env python3
"""Plot the enthalpy sweep outlet steam quality in Bangma-style formatting."""

from __future__ import annotations

import argparse
import csv
import math
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MPLCONFIGDIR = REPO_ROOT / "output" / ".matplotlib-cache"
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
XDG_CACHE_HOME = REPO_ROOT / "output" / ".cache"
XDG_CACHE_HOME.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))
os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_HOME))

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "enthalpy_sweep"
DEFAULT_INJECTION_RESULTS = DEFAULT_OUTPUT_DIR / "all_enthalpy_injection_results.csv"
DEFAULT_CASE_SUMMARY = DEFAULT_OUTPUT_DIR / "all_enthalpy_case_summary.csv"
DEFAULT_PLOT = DEFAULT_OUTPUT_DIR / "plots" / "enthalpy_output_steam_quality.png"
DEFAULT_PLOT_DATA = DEFAULT_OUTPUT_DIR / "plots" / "enthalpy_output_steam_quality_plot_data.csv"
DEFAULT_DIGITIZED_POINTS = (
    REPO_ROOT / "output" / "graph_digitization" / "bangma_reference_digitized_points.csv"
)


@dataclass(frozen=True)
class PlotPoint:
    case: str
    enthalpy: str
    inlet_velocity_ms: float
    gas_mass_flow_kgs: float
    escaped_kgs: float
    steam_quality_pct: float


@dataclass(frozen=True)
class DigitizedPoint:
    series: str
    color: str
    x_mps: float
    steam_quality_pct: float


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a Bangma-style scatter plot of output steam quality vs inlet velocity "
            "from the PyFluent enthalpy sweep results."
        )
    )
    parser.add_argument(
        "--injection-results",
        default=str(DEFAULT_INJECTION_RESULTS),
        help="Combined injection CSV from the enthalpy sweep.",
    )
    parser.add_argument(
        "--case-summary",
        default=str(DEFAULT_CASE_SUMMARY),
        help="Combined case summary CSV containing gas_mass_flow_kgs.",
    )
    parser.add_argument("--output", default=str(DEFAULT_PLOT), help="Output plot path.")
    parser.add_argument(
        "--layout",
        choices=("split", "single"),
        default="single",
        help="Plot layout. Split gives a full-range panel plus a 99.4-100%% zoom panel.",
    )
    parser.add_argument(
        "--digitized-points",
        default=str(DEFAULT_DIGITIZED_POINTS),
        help="Digitized Bangma reference graph CSV. Use an empty string to skip.",
    )
    parser.add_argument(
        "--connect-digitized-correlation",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Draw a line through the digitized correlation points.",
    )
    parser.add_argument(
        "--plot-data-output",
        default=str(DEFAULT_PLOT_DATA),
        help="CSV path for the aggregated plot data. Use an empty string to skip.",
    )
    parser.add_argument(
        "--title",
        default="Purnanto Replication: Outlet Steam Quality",
        help="Plot title.",
    )
    parser.add_argument(
        "--legend-label",
        default="Present CFD Replication",
        help="Legend label for the plotted points.",
    )
    parser.add_argument(
        "--reference-calculation-label",
        default="Bangma Calculation",
        help="Legend label for digitized calculation points.",
    )
    parser.add_argument(
        "--reference-simulation-label",
        default="Bangma Simulation",
        help="Legend label for digitized simulation points.",
    )
    parser.add_argument(
        "--reference-correlation-label",
        default="Lazalde-Crabtree Correlation",
        help="Legend label for the digitized correlation series.",
    )
    parser.add_argument(
        "--caption",
        default="",
        help="Optional italic caption placed below the plot.",
    )
    parser.add_argument("--x-min", type=float, default=0.0, help="X-axis minimum.")
    parser.add_argument("--x-max", type=float, default=80.0, help="X-axis maximum.")
    parser.add_argument("--x-step", type=float, default=10.0, help="X tick interval.")
    parser.add_argument(
        "--y-min",
        type=float,
        default=99.4,
        help=(
            "Preferred lowest steam-quality tick. By default the plot expands below this "
            "if needed so data points remain visible."
        ),
    )
    parser.add_argument(
        "--strict-y-range",
        action="store_true",
        help="Do not expand the y-axis if points fall outside --y-min/--y-max.",
    )
    parser.add_argument(
        "--y-max",
        type=float,
        default=100.0,
        help="Highest steam-quality tick to show. Use 100 to match the reference style.",
    )
    parser.add_argument(
        "--y-step",
        type=float,
        default=0.1,
        help="Y tick interval in steam-quality percentage points.",
    )
    parser.add_argument(
        "--zoom-y-min",
        type=float,
        default=99.4,
        help="Lower bound for the zoom panel when --layout split.",
    )
    parser.add_argument(
        "--zoom-y-max",
        type=float,
        default=100.0,
        help="Upper bound for the zoom panel when --layout split.",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Output image DPI.")
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show an interactive window after saving the plot.",
    )
    return parser


def required_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "").strip()
    if not value:
        raise ValueError(f"Missing required numeric field {key!r} in row: {row}")
    return float(value)


def load_case_gas_flows(path: Path) -> dict[tuple[str, str], float]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return {
            (row["case"], row["enthalpy_kJkg"]): required_float(row, "gas_mass_flow_kgs")
            for row in reader
        }


def load_plot_points(injection_results: Path, case_summary: Path) -> list[PlotPoint]:
    gas_flows = load_case_gas_flows(case_summary)
    grouped: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: {"escaped_kgs": 0.0, "velocity_sum": 0.0, "velocity_count": 0.0}
    )

    with injection_results.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            key = (row["case"], row["enthalpy_kJkg"])
            grouped[key]["escaped_kgs"] += required_float(row, "escaped_kgs")
            grouped[key]["velocity_sum"] += required_float(row, "normal_speed_ms")
            grouped[key]["velocity_count"] += 1.0

    points: list[PlotPoint] = []
    for key, values in grouped.items():
        gas_mass_flow = gas_flows[key]
        escaped = values["escaped_kgs"]
        denominator = gas_mass_flow + escaped
        if denominator <= 0:
            raise ValueError(f"Cannot compute steam quality for {key}: gas + escaped <= 0")
        points.append(
            PlotPoint(
                case=key[0],
                enthalpy=key[1],
                inlet_velocity_ms=values["velocity_sum"] / values["velocity_count"],
                gas_mass_flow_kgs=gas_mass_flow,
                escaped_kgs=escaped,
                steam_quality_pct=100.0 * gas_mass_flow / denominator,
            )
        )

    return sorted(points, key=lambda point: point.inlet_velocity_ms)


def load_digitized_points(path: Path) -> list[DigitizedPoint]:
    if not path.exists():
        print(f"warning: digitized points CSV not found, skipping: {path}")
        return []

    points: list[DigitizedPoint] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            points.append(
                DigitizedPoint(
                    series=row["series"],
                    color=row["color"],
                    x_mps=required_float(row, "x_mps"),
                    steam_quality_pct=required_float(row, "steam_quality_pct"),
                )
            )
    return sorted(points, key=lambda point: (point.series, point.x_mps))


def digitized_points_by_series(points: list[DigitizedPoint]) -> dict[str, list[DigitizedPoint]]:
    grouped: dict[str, list[DigitizedPoint]] = defaultdict(list)
    for point in points:
        grouped[point.series].append(point)
    return {series: sorted(values, key=lambda point: point.x_mps) for series, values in grouped.items()}


def format_tick(value: float, _position: int) -> str:
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value))}"
    return f"{value:.1f}"


def ticks(start: float, stop: float, step: float) -> list[float]:
    count = int(math.floor((stop - start) / step + 1e-9))
    return [start + index * step for index in range(count + 1)]


def aligned_ticks(start: float, stop: float, step: float) -> list[float]:
    first = math.ceil((start - 1e-9) / step) * step
    values: list[float] = []
    value = first
    while value <= stop + 1e-9:
        values.append(round(value, 10))
        value += step
    return values


def write_plot_data(path: Path, points: list[PlotPoint]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "case",
                "enthalpy_kJkg",
                "inlet_velocity_ms",
                "gas_mass_flow_kgs",
                "escaped_kgs",
                "steam_quality_pct",
            ),
        )
        writer.writeheader()
        for point in points:
            writer.writerow(
                {
                    "case": point.case,
                    "enthalpy_kJkg": point.enthalpy,
                    "inlet_velocity_ms": f"{point.inlet_velocity_ms:.6f}",
                    "gas_mass_flow_kgs": f"{point.gas_mass_flow_kgs:.6f}",
                    "escaped_kgs": f"{point.escaped_kgs:.6f}",
                    "steam_quality_pct": f"{point.steam_quality_pct:.6f}",
                }
            )


def draw_pyfluent_points(
    axis: plt.Axes,
    points: list[PlotPoint],
    args: argparse.Namespace,
    *,
    include_label: bool = True,
) -> None:
    axis.scatter(
        [point.inlet_velocity_ms for point in points],
        [point.steam_quality_pct for point in points],
        marker="o",
        s=78,
        color="#222222",
        edgecolors="#222222",
        linewidths=1.0,
        label=args.legend_label if include_label else "_nolegend_",
        zorder=5,
    )


def draw_digitized_points(
    axis: plt.Axes,
    points: list[DigitizedPoint],
    args: argparse.Namespace,
    *,
    include_labels: bool = True,
) -> None:
    if not points:
        return

    style_by_series = {
        "Calculation": {
            "label": args.reference_calculation_label,
            "color": "#4f81bd",
            "marker": "D",
            "size": 62,
            "zorder": 4,
        },
        "Simulation": {
            "label": args.reference_simulation_label,
            "color": "#c0504d",
            "marker": "s",
            "size": 68,
            "zorder": 4,
        },
        "Lazalde-Crabtree Correlation": {
            "label": args.reference_correlation_label,
            "color": "#00a65a",
            "marker": "o",
            "size": 64,
            "zorder": 3,
        },
    }

    for series, series_points in digitized_points_by_series(points).items():
        style = style_by_series.get(
            series,
            {
                "label": series,
                "color": "#666666",
                "marker": "o",
                "size": 58,
                "zorder": 3,
            },
        )
        x_values = [point.x_mps for point in series_points]
        y_values = [point.steam_quality_pct for point in series_points]
        label = style["label"] if include_labels else "_nolegend_"
        if series == "Lazalde-Crabtree Correlation" and args.connect_digitized_correlation:
            axis.plot(
                x_values,
                y_values,
                color=style["color"],
                marker=style["marker"],
                markersize=7.5,
                linewidth=2.4,
                label=label,
                zorder=style["zorder"],
            )
        else:
            axis.scatter(
                x_values,
                y_values,
                marker=style["marker"],
                s=style["size"],
                color=style["color"],
                edgecolors=style["color"],
                linewidths=1.0,
                label=label,
                zorder=style["zorder"],
            )


def apply_y_axis(axis: plt.Axes, y_min: float, y_max: float, y_step: float) -> None:
    y_minor_ticks = ticks(y_min, y_max, y_step)
    y_major_step = y_step
    if len(y_minor_ticks) > 14:
        y_major_step = max(0.5, y_step)

    axis.set_ylim(y_max, y_min)
    axis.set_yticks(aligned_ticks(y_min, y_max, y_major_step))
    if y_major_step != y_step:
        axis.set_yticks(y_minor_ticks, minor=True)
    axis.yaxis.set_major_formatter(FuncFormatter(format_tick))


def apply_grid_and_spines(axis: plt.Axes) -> None:
    axis.grid(True, which="major", linestyle="--", color="#9a9a9a", linewidth=0.6, alpha=0.65)
    axis.grid(True, which="minor", axis="y", linestyle="--", color="#b5b5b5", linewidth=0.45, alpha=0.55)
    for spine in axis.spines.values():
        spine.set_color("#a8a8a8")
        spine.set_linewidth(0.9)
    axis.tick_params(axis="both", labelsize=13, colors="#222222", pad=6)


def configure_x_axis(axis: plt.Axes, args: argparse.Namespace, *, show_top_labels: bool) -> None:
    axis.set_xlim(args.x_min, args.x_max)
    axis.set_xticks(ticks(args.x_min, args.x_max, args.x_step))
    if show_top_labels:
        axis.xaxis.set_label_position("top")
        axis.xaxis.tick_top()
        axis.set_xlabel("Steam Velocity at Separator Inlet (m/s)", fontsize=14, labelpad=15)
        axis.tick_params(axis="x", which="both", top=True, labeltop=True, bottom=False, labelbottom=False)
    else:
        axis.tick_params(axis="x", which="both", top=False, labeltop=False, bottom=False, labelbottom=False)


def y_lower_bound_for_values(values: list[float], args: argparse.Namespace) -> float:
    min_quality = min(values)
    y_min = args.y_min
    if not args.strict_y_range and min_quality < y_min:
        y_min = math.floor((min_quality - args.y_step) / args.y_step) * args.y_step
        print(f"expanded y-axis lower bound to {y_min:g}% so all points are visible")
    return y_min


def add_legend(figure: plt.Figure, axis: plt.Axes, *, y_anchor: float = 0.06) -> None:
    handles, labels = axis.get_legend_handles_labels()
    unique_handles = []
    unique_labels = []
    for handle, label in zip(handles, labels):
        if label == "_nolegend_" or label in unique_labels:
            continue
        unique_handles.append(handle)
        unique_labels.append(label)
    figure.legend(
        unique_handles,
        unique_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, y_anchor),
        frameon=False,
        fontsize=13,
        handlelength=2.4,
        scatterpoints=1,
        ncol=2,
        columnspacing=1.4,
    )


def draw_plot(
    points: list[PlotPoint],
    digitized_points: list[DigitizedPoint],
    args: argparse.Namespace,
) -> Path:
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.labelweight": "bold",
        }
    )

    if args.layout == "split":
        return draw_split_plot(output_path, points, digitized_points, args)
    return draw_single_axis_plot(output_path, points, digitized_points, args)


def draw_single_axis_plot(
    output_path: Path,
    points: list[PlotPoint],
    digitized_points: list[DigitizedPoint],
    args: argparse.Namespace,
) -> Path:
    all_quality_values = [point.steam_quality_pct for point in points] + [
        point.steam_quality_pct for point in digitized_points
    ]
    y_min = y_lower_bound_for_values(all_quality_values, args)
    y_max = args.y_max
    if y_min >= y_max:
        raise ValueError(f"Expected y-min < y-max, got {y_min} >= {y_max}")
    hidden_points = [
        value
        for value in all_quality_values
        if value < y_min or value > y_max
    ]
    if hidden_points:
        print(
            f"warning: {len(hidden_points)} point(s) outside y-axis range "
            f"{y_min:g}-{y_max:g}% and will not be visible"
        )

    figure_height = 5.7 if args.caption else 4.9
    figure, axis = plt.subplots(figsize=(10.2, figure_height), constrained_layout=False)

    draw_pyfluent_points(axis, points, args)
    draw_digitized_points(axis, digitized_points, args)

    axis.set_title(args.title, fontsize=24, pad=28)
    axis.set_ylabel("Output Steam Quality (%)", fontsize=14, labelpad=10)
    configure_x_axis(axis, args, show_top_labels=True)
    apply_y_axis(axis, y_min, y_max, args.y_step)
    apply_grid_and_spines(axis)
    add_legend(figure, axis, y_anchor=0.04)

    bottom_margin = 0.38 if args.caption else 0.28
    figure.subplots_adjust(left=0.11, right=0.98, top=0.78, bottom=bottom_margin)
    if args.caption:
        figure.text(
            0.02,
            0.045,
            args.caption,
            ha="left",
            va="bottom",
            fontsize=22,
            fontstyle="italic",
            color="#5a5a5a",
        )

    figure.savefig(output_path, dpi=args.dpi, bbox_inches="tight")
    if args.show:
        plt.show()
    plt.close(figure)
    return output_path


def draw_split_plot(
    output_path: Path,
    points: list[PlotPoint],
    digitized_points: list[DigitizedPoint],
    args: argparse.Namespace,
) -> Path:
    all_quality_values = [point.steam_quality_pct for point in points] + [
        point.steam_quality_pct for point in digitized_points
    ]
    full_y_min = y_lower_bound_for_values(all_quality_values, args)
    if full_y_min >= args.y_max:
        raise ValueError(f"Expected y-min < y-max, got {full_y_min} >= {args.y_max}")
    if args.zoom_y_min >= args.zoom_y_max:
        raise ValueError(
            f"Expected zoom-y-min < zoom-y-max, got {args.zoom_y_min} >= {args.zoom_y_max}"
        )

    figure_height = 7.7 if args.caption else 7.1
    figure, (full_axis, zoom_axis) = plt.subplots(
        2,
        1,
        figsize=(10.4, figure_height),
        sharex=True,
        gridspec_kw={"height_ratios": [1.05, 1.0], "hspace": 0.18},
        constrained_layout=False,
    )

    for axis, include_labels in ((full_axis, True), (zoom_axis, False)):
        draw_pyfluent_points(axis, points, args, include_label=include_labels)
        draw_digitized_points(axis, digitized_points, args, include_labels=include_labels)
        apply_grid_and_spines(axis)

    figure.suptitle(args.title, fontsize=24, fontweight="bold", y=0.965)
    configure_x_axis(full_axis, args, show_top_labels=True)
    configure_x_axis(zoom_axis, args, show_top_labels=False)
    apply_y_axis(full_axis, full_y_min, args.y_max, args.y_step)
    apply_y_axis(zoom_axis, args.zoom_y_min, args.zoom_y_max, args.y_step)

    full_axis.text(
        0.012,
        0.08,
        "Full range",
        transform=full_axis.transAxes,
        fontsize=11,
        fontweight="bold",
        color="#4a4a4a",
    )
    zoom_axis.text(
        0.012,
        0.08,
        "99.4-100% zoom",
        transform=zoom_axis.transAxes,
        fontsize=11,
        fontweight="bold",
        color="#4a4a4a",
    )
    figure.text(
        0.025,
        0.50,
        "Output Steam Quality (%)",
        rotation="vertical",
        va="center",
        ha="center",
        fontsize=14,
        fontweight="bold",
    )

    bottom_margin = 0.27 if args.caption else 0.20
    figure.subplots_adjust(left=0.11, right=0.98, top=0.82, bottom=bottom_margin)
    add_legend(figure, full_axis, y_anchor=0.045)

    if args.caption:
        figure.text(
            0.02,
            0.035,
            args.caption,
            ha="left",
            va="bottom",
            fontsize=22,
            fontstyle="italic",
            color="#5a5a5a",
        )

    figure.savefig(output_path, dpi=args.dpi, bbox_inches="tight")
    if args.show:
        plt.show()
    plt.close(figure)
    return output_path


def main() -> int:
    args = build_parser().parse_args()
    injection_results = Path(args.injection_results).expanduser().resolve()
    case_summary = Path(args.case_summary).expanduser().resolve()
    points = load_plot_points(injection_results, case_summary)
    digitized_points = (
        load_digitized_points(Path(args.digitized_points).expanduser().resolve())
        if args.digitized_points
        else []
    )

    if args.plot_data_output:
        write_plot_data(Path(args.plot_data_output).expanduser().resolve(), points)

    output_path = draw_plot(points, digitized_points, args)
    print(f"wrote_plot: {output_path}")
    print(f"digitized_points_plotted: {len(digitized_points)}")
    if args.plot_data_output:
        print(f"wrote_plot_data: {Path(args.plot_data_output).expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
