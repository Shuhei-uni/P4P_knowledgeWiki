#!/usr/bin/env python3
"""Plot saved Stage-3 scaled residual histories for F08, F10, and F12.

The overnight queue saved a residual export for F08 only.  This script reads
that export through Fluent's Scheme reader without changing the loaded case,
and makes missing F10/F12 histories explicit in the figure instead of
inventing zero-valued curves.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


BRANCHES = ("F08", "F10", "F12")
RESIDUAL_ORDER = (
    "continuity",
    "x-velocity",
    "y-velocity",
    "z-velocity",
    "k",
    "epsilon",
    "vf-phase-2",
)


def read_residual_export(solver: Any, path: str) -> dict[str, dict[str, list[float]]]:
    """Read Fluent's Lisp-style residual export without using read-line."""
    escaped = quote_scheme_string(path)
    expression = (
        f'(with-input-from-file "{escaped}" '
        "(lambda () "
        "(let loop ((x (read)) (out (quote ()))) "
        "(if (eof-object? x) (reverse out) "
        "(loop (read) (cons x out))))))"
    )
    payload = solver.scheme.eval(expression)
    result: dict[str, dict[str, list[float]]] = {}
    for series in payload:
        if not isinstance(series, (list, tuple)) or len(series) < 3:
            continue
        label_pair = series[0]
        label = str(label_pair[1]) if isinstance(label_pair, (list, tuple)) else str(label_pair)
        values = list(series[1:])
        iterations = [int(values[index]) for index in range(0, len(values), 2)]
        residuals = [float(values[index]) for index in range(1, len(values), 2)]
        result[label] = {"iterations": iterations, "values": residuals}
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "output" / "03a_stage3" / "residual-plots"),
    )
    parser.add_argument(
        "--f08-residuals",
        default=(
            r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F08"
            r"\F08-full-mixture-20pct-resume-iter004900-20260818T103253Z-residuals.out"
        ),
    )
    return parser


def plot_histories(
    output_path: Path,
    histories: dict[str, dict[str, dict[str, list[float]]]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {
        "continuity": "#2563eb",
        "x-velocity": "#0f766e",
        "y-velocity": "#15803d",
        "z-velocity": "#a16207",
        "k": "#c2410c",
        "epsilon": "#be123c",
        "vf-phase-2": "#7c3aed",
    }
    fig, axes = plt.subplots(
        len(BRANCHES),
        len(RESIDUAL_ORDER),
        figsize=(22, 9.5),
        sharex=False,
        constrained_layout=True,
    )
    fig.suptitle(
        "03A Stage-3 Queue: Scaled Residual Histories\n"
        "F08 saved data; F10/F12 residual exports unavailable",
        fontsize=16,
        fontweight="bold",
    )

    for row, branch in enumerate(BRANCHES):
        branch_data = histories.get(branch, {})
        for col, residual_name in enumerate(RESIDUAL_ORDER):
            ax = axes[row, col]
            data = branch_data.get(residual_name)
            ax.set_yscale("log")
            ax.grid(True, which="major", linestyle="-", alpha=0.25)
            ax.grid(True, which="minor", linestyle=":", alpha=0.15)
            ax.set_title(residual_name, fontsize=9)
            if data:
                ax.plot(
                    data["iterations"],
                    data["values"],
                    color=colors[residual_name],
                    linewidth=1.1,
                )
                ax.set_xlim(min(data["iterations"]), max(data["iterations"]))
                ax.tick_params(axis="both", labelsize=7)
            else:
                ax.set_facecolor("#f8fafc")
                ax.text(
                    0.5,
                    0.5,
                    "NO SAVED\nHISTORY",
                    ha="center",
                    va="center",
                    color="#b91c1c",
                    fontsize=8,
                    fontweight="bold",
                    transform=ax.transAxes,
                )
                ax.set_xticks([])
                ax.set_yticks([])
            if col == 0:
                ax.set_ylabel(f"{branch}\nscaled residual", fontsize=9)
            if row == len(BRANCHES) - 1:
                ax.set_xlabel("Iteration", fontsize=8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_combined_history(
    output_path: Path,
    histories: dict[str, dict[str, dict[str, list[float]]]],
) -> None:
    """Write one Fluent-style log-scaled chart with all available curves."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {
        "continuity": "#2563eb",
        "x-velocity": "#0f766e",
        "y-velocity": "#15803d",
        "z-velocity": "#a16207",
        "k": "#c2410c",
        "epsilon": "#be123c",
        "vf-phase-2": "#7c3aed",
    }
    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)
    branch_data = histories.get("F08", {})
    for residual_name in RESIDUAL_ORDER:
        data = branch_data.get(residual_name)
        if data:
            ax.plot(
                data["iterations"],
                data["values"],
                color=colors[residual_name],
                linewidth=1.25,
                label=residual_name,
            )

    ax.set_yscale("log")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Scaled residual")
    ax.set_title(
        "03A Stage-3 F08: Scaled Residual History\n"
        "F10/F12 have no saved residual histories",
    )
    ax.grid(True, which="major", linestyle="-", alpha=0.28)
    ax.grid(True, which="minor", linestyle=":", alpha=0.16)
    if branch_data:
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            ncol=3,
            frameon=False,
            fontsize=9,
        )
    ax.text(
        0.99,
        0.02,
        "F08 saved data only; F10/F12 stage journals failed before residual export",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#991b1b",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "03A-stage3-F08-F10-F12-scaled-residuals.png"
    combined_output_path = output_dir / "03A-stage3-F08-F10-F12-scaled-residuals-combined.png"
    json_path = output_path.with_suffix(".json")

    solver = connect(server_id=args.server_id, start_transcript=False)
    histories: dict[str, dict[str, dict[str, list[float]]]] = {branch: {} for branch in BRANCHES}
    f08_exists = bool(remote_file_exists(solver, args.f08_residuals))
    if f08_exists:
        histories["F08"] = read_residual_export(solver, args.f08_residuals)

    availability = {
        "F08": {
            "status": "available" if f08_exists else "missing",
            "source": args.f08_residuals,
            "series": sorted(histories["F08"]),
        },
        "F10": {
            "status": "not_saved",
            "reason": "carrier-stage journal failed before residual export/checkpoint",
        },
        "F12": {
            "status": "not_saved",
            "reason": "carrier-stage journal failed before residual export/checkpoint",
        },
    }
    payload = {"availability": availability, "histories": histories}
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    plot_histories(output_path, histories)
    plot_combined_history(combined_output_path, histories)
    print(f"Saved plot: {output_path}")
    print(f"Saved combined plot: {combined_output_path}")
    print(f"Saved data: {json_path}")
    print(json.dumps(availability, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
