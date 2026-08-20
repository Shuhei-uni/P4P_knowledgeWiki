#!/usr/bin/env python3
"""Build stitched Stage-3 scaled-residual plots from segmented evidence.

This is an offline report builder.  It never connects to Fluent and never
fills missing residual intervals.  F09 is reconstructed from its five native
stream transcripts.  F03 and F07 prefer the recovered server-side native
transcript streams saved under ``residual-plots/recovered-remote`` and fall
back to local supervision/event records when those streams are unavailable.
Unrecorded intervals remain visible as gaps in the branch panels.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "03a_stage3" / "residual-plots"
DEFAULT_REPORT_DIR = (
    PROJECT_ROOT
    / ".."
    / "Setups"
    / "reports"
    / "full-geometry"
    / "mixture"
    / "steady-liquid-outlet"
    / "plots"
    / "03a-stage3"
).resolve()
RECOVERED_REMOTE_DIR = DEFAULT_OUTPUT_DIR / "recovered-remote"

RESIDUAL_ORDER = (
    "continuity",
    "x-velocity",
    "y-velocity",
    "z-velocity",
    "k",
    "epsilon",
    "vf-phase-2",
)

COLORS = {
    "continuity": "#2563eb",
    "x-velocity": "#0f766e",
    "y-velocity": "#15803d",
    "z-velocity": "#a16207",
    "k": "#c2410c",
    "epsilon": "#be123c",
    "vf-phase-2": "#7c3aed",
}

NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
RESIDUAL_LINE = re.compile(
    rf"^\s*(\d+)\s+({NUMBER})\s+({NUMBER})\s+({NUMBER})\s+"
    rf"({NUMBER})\s+({NUMBER})\s+({NUMBER})\s+({NUMBER})(?:\s|$)"
)


def finite_positive(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result) or result <= 0.0:
        return None
    return result


def empty_series() -> dict[str, list[list[float]]]:
    return {name: [] for name in RESIDUAL_ORDER}


def add_point(series: dict[str, list[list[float]]], iteration: Any, values: dict[str, Any]) -> None:
    try:
        x_value = int(iteration)
    except (TypeError, ValueError):
        return
    for name in RESIDUAL_ORDER:
        y_value = finite_positive(values.get(name))
        if y_value is not None:
            series[name].append([x_value, y_value])


def deduplicate(series: dict[str, list[list[float]]]) -> dict[str, list[list[float]]]:
    result: dict[str, list[list[float]]] = {}
    for name, points in series.items():
        by_iteration = {int(point[0]): float(point[1]) for point in points}
        result[name] = [[x_value, by_iteration[x_value]] for x_value in sorted(by_iteration)]
    return result


def parse_native_stream(path: Path) -> dict[str, list[list[float]]]:
    """Parse Fluent printed residual rows from one native stream transcript."""

    series = empty_series()
    if not path.exists():
        return series
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = RESIDUAL_LINE.match(line)
        if not match:
            continue
        values = [finite_positive(value) for value in match.groups()[1:]]
        if any(value is None for value in values):
            continue
        add_point(series, match.group(1), dict(zip(RESIDUAL_ORDER, values)))
    return deduplicate(series)


def merge_series(chunks: list[dict[str, list[list[float]]]]) -> dict[str, list[list[float]]]:
    merged = empty_series()
    for chunk in chunks:
        for name, points in chunk.items():
            merged[name].extend(points)
    return deduplicate(merged)


def parse_event_snapshots(path: Path, branch: str) -> dict[str, list[list[float]]]:
    series = empty_series()
    if not path.exists():
        return series
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("branch") != branch:
            continue
        snapshot = event.get("snapshot") or {}
        residuals = snapshot.get("residuals")
        iteration = snapshot.get("monitor_iteration", snapshot.get("iteration"))
        if isinstance(residuals, dict) and iteration is not None:
            add_point(series, iteration, residuals)
    return deduplicate(series)


def parse_event_snapshot_segments(path: Path, branch: str) -> list[dict[str, list[list[float]]]]:
    """Return one segment per preserved event snapshot, without bridging gaps."""

    segments: list[dict[str, list[list[float]]]] = []
    if not path.exists():
        return segments
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("branch") != branch:
            continue
        snapshot = event.get("snapshot") or {}
        residuals = snapshot.get("residuals")
        iteration = snapshot.get("monitor_iteration", snapshot.get("iteration"))
        if not isinstance(residuals, dict) or iteration is None:
            continue
        segment = empty_series()
        add_point(segment, iteration, residuals)
        segments.append(deduplicate(segment))
    return segments


def parse_f07_history(path: Path) -> dict[str, list[list[float]]]:
    series = empty_series()
    if not path.exists():
        return series
    payload = json.loads(path.read_text(encoding="utf-8"))
    iterations = payload.get("residual_iterations", [])
    residuals = payload.get("residuals", {})
    for iteration_index, iteration in enumerate(iterations):
        values = {
            name: values[iteration_index]
            for name, values in residuals.items()
            if iteration_index < len(values)
        }
        add_point(series, iteration, values)
    return deduplicate(series)


def stage_streams(f09_dir: Path) -> list[tuple[str, Path, int, int]]:
    stages = (
        ("10%", 3000),
        ("20%", 6000),
        ("40%", 9000),
        ("80%", 12000),
        ("100%", 15000),
    )
    result = []
    for label, end_iteration in stages:
        path = next(
            f09_dir.glob(f"F09-{label[:-1]}pct-end-iter{end_iteration:06d}-*.stream.trn"),
            f09_dir / f"F09-{label[:-1]}pct-end-iter{end_iteration:06d}-missing.stream.trn",
        )
        result.append((label, path, end_iteration - 2999, end_iteration))
    return result


def recovered_stream(path: Path) -> dict[str, list[list[float]]]:
    """Parse an optionally recovered server-side native stream."""

    return parse_native_stream(path) if path.exists() else empty_series()


def build_data() -> dict[str, Any]:
    f03_events = PROJECT_ROOT / "output" / "03a_stage3" / "supervised" / "20260820T054645Z" / "supervised-events.jsonl"
    f07_events = PROJECT_ROOT / "output" / "03a_stage3" / "overnight" / "20260820T002135Z" / "overnight-events.jsonl"
    f07_history = PROJECT_ROOT / "output" / "03a_stage3" / "F07" / "F07-monitor-histories-10pct.json"
    f09_dir = PROJECT_ROOT / "output" / "03a_stage3" / "supervised" / "20260820T082047Z"

    f03_event_series = parse_event_snapshots(f03_events, "F03")
    f03_event_segments = parse_event_snapshot_segments(f03_events, "F03")
    f03_remote_paths = (
        RECOVERED_REMOTE_DIR / "F03-initial-1000.stream.trn",
        RECOVERED_REMOTE_DIR / "F03-continuation-1000-5000.stream.trn",
    )
    f03_remote_segments = [
        recovered_stream(path) for path in f03_remote_paths if path.exists()
    ]
    if f03_remote_segments:
        f03_segments = f03_remote_segments
        f03_series = merge_series([*f03_remote_segments, f03_event_series])
        f03_sources = [str(path) for path in f03_remote_paths if path.exists()]
        f03_sources.append(str(f03_events))
        f03_coverage = (
            "server-side native transcripts recovered: iterations 1–981 and "
            "1000–5000; 982–999 are absent from the preserved transcript streams"
        )
    else:
        f03_segments = f03_event_segments
        f03_series = f03_event_series
        f03_sources = [str(f03_events)]
        f03_coverage = (
            "local supervision snapshots only; server-side transcript recovery "
            "not available"
        )

    f07_history_series = parse_f07_history(f07_history)
    f07_endpoint_segments = parse_event_snapshot_segments(f07_events, "F07")
    f07_remote_paths = (
        RECOVERED_REMOTE_DIR / "F07-native-1-1000.stream.trn",
        RECOVERED_REMOTE_DIR / "F07-10pct-1000-3150.stream.trn",
        RECOVERED_REMOTE_DIR / "F07-20pct-3150-6150.stream.trn",
        RECOVERED_REMOTE_DIR / "F07-40pct-6150-9150.stream.trn",
        RECOVERED_REMOTE_DIR / "F07-80pct-9150-9400-fpe.stream.trn",
    )
    f07_remote_segments = [
        recovered_stream(path) for path in f07_remote_paths if path.exists()
    ]
    if f07_remote_segments:
        f07_segments = f07_remote_segments
        f07_series = merge_series(
            [*f07_remote_segments, f07_history_series, *f07_endpoint_segments]
        )
        f07_sources = [str(path) for path in f07_remote_paths if path.exists()]
        f07_sources.extend([str(f07_history), str(f07_events)])
        f07_coverage = (
            "server-side native transcripts recovered continuously through 9150, "
            "with the 80% failure transcript continuing to iteration 9174; no "
            "80% terminal pair was written"
        )
        f07_boundaries = [
            [3150, "10% endpoint"],
            [6150, "20% endpoint"],
            [9150, "40% endpoint / 80% transition"],
            [9174, "80% FPE observed"],
        ]
    else:
        f07_segments = [f07_history_series, *f07_endpoint_segments]
        f07_series = merge_series([f07_history_series, *f07_endpoint_segments])
        f07_sources = [str(f07_history), str(f07_events)]
        f07_coverage = (
            "local 10% history through 750 plus preserved stage-boundary snapshots; "
            "gaps are not interpolated"
        )
        f07_boundaries = [
            [3150, "10% endpoint"],
            [6150, "20% endpoint"],
            [9150, "40% endpoint"],
            [9400, "80% FPE attempt"],
        ]
    f09_chunks: list[dict[str, list[list[float]]]] = []
    f09_segments: list[dict[str, list[list[float]]]] = []
    f09_sources: list[str] = []
    for _, path, _, _ in stage_streams(f09_dir):
        f09_sources.append(str(path))
        chunk = parse_native_stream(path)
        f09_chunks.append(chunk)
        f09_segments.append(chunk)
    f09_series = merge_series(f09_chunks)

    return {
        "residual_order": list(RESIDUAL_ORDER),
        "branches": {
            "F03": {
                "series": f03_series,
                "segments": f03_segments,
                "x_limit": 5000,
                "coverage": f03_coverage,
                "sources": f03_sources,
                "stage_boundaries": [[1000, "transport boundary"], [5000, "terminal pair"]],
            },
            "F07": {
                "series": f07_series,
                "segments": f07_segments,
                "x_limit": 9400,
                "coverage": f07_coverage,
                "sources": f07_sources,
                "stage_boundaries": f07_boundaries,
            },
            "F09": {
                "series": f09_series,
                "segments": f09_segments,
                "x_limit": 15000,
                "coverage": "complete native residual streams stitched across five stage transcripts",
                "sources": f09_sources,
                "stage_boundaries": [[3000, "10%"], [6000, "20%"], [9000, "40%"], [12000, "80%"], [15000, "100%"]],
            },
        },
    }


def plot(data: dict[str, Any], output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    branches = data["branches"]
    fig, axes = plt.subplots(3, 1, figsize=(15, 14), constrained_layout=True)
    for axis, branch in zip(axes, ("F03", "F07", "F09")):
        record = branches[branch]
        series = record["series"]
        segments = record.get("segments") or [series]
        for name in RESIDUAL_ORDER:
            first_segment = True
            for segment in segments:
                points = segment.get(name, [])
                if not points:
                    continue
                x_values = [point[0] for point in points]
                y_values = [point[1] for point in points]
                axis.plot(
                    x_values,
                    y_values,
                    color=COLORS[name],
                    linewidth=1.0,
                    label=name if first_segment else "_nolegend_",
                )
                if branch != "F09":
                    axis.scatter(x_values, y_values, color=COLORS[name], s=8, zorder=3)
                first_segment = False

        for boundary, label in record["stage_boundaries"]:
            axis.axvline(boundary, color="#6b7280", linestyle="--", linewidth=0.7, alpha=0.7)
            axis.text(
                boundary,
                0.985,
                label,
                transform=axis.get_xaxis_transform(),
                rotation=90,
                va="top",
                ha="right",
                fontsize=8,
                color="#4b5563",
            )
        axis.set_xlim(0, record["x_limit"])
        axis.set_yscale("log")
        if branch == "F07":
            # The preserved 80% failure transcript contains rapidly diverging
            # residuals up to ~1e74. Keep the completed-branch history legible
            # while retaining the failure location and explicit clipping note.
            axis.set_ylim(1e-6, 1e4)
            axis.text(
                0.99,
                0.03,
                "80% FPE tail clipped above 1e4",
                transform=axis.transAxes,
                fontsize=8,
                color="#991b1b",
                ha="right",
            )
        axis.set_ylabel("Scaled residual")
        axis.set_title(f"{branch} — stitched scaled residuals", loc="left", fontweight="bold")
        axis.text(0.01, 0.03, record["coverage"], transform=axis.transAxes, fontsize=8, color="#4b5563")
        axis.grid(True, which="major", linestyle="-", alpha=0.24)
        axis.grid(True, which="minor", linestyle=":", alpha=0.14)
        axis.legend(loc="upper right", fontsize=8, ncol=4, frameon=False)
    axes[-1].set_xlabel("Cumulative Fluent native iteration")
    fig.suptitle("03A Stage-3 — stitched scaled residual histories", fontsize=16, fontweight="bold")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = build_data()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    output_name = "03A-stage3-F03-F07-F09-scaled-residuals-stitched"
    json_path = args.output_dir / f"{output_name}.json"
    plot_path = args.output_dir / f"{output_name}.png"
    report_plot_path = args.report_dir / f"{output_name}.png"
    json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    plot(data, plot_path)
    plot(data, report_plot_path)
    print(f"Saved data: {json_path}")
    print(f"Saved plot: {plot_path}")
    print(f"Saved report plot: {report_plot_path}")
    for branch, record in data["branches"].items():
        counts = {name: len(points) for name, points in record["series"].items()}
        print(f"{branch}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
