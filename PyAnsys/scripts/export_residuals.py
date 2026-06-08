#!/usr/bin/env python3
"""Export a scaled residual plot from the active Fluent session.

This script connects to the already-running remote Fluent session, starts the
monitor stream, waits for the residual history to populate, and saves a
log-scaled residual plot to disk.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# Allow importing check_connection.py from the same folder.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_connection import connect  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export a scaled residual plot from the current Fluent session."
    )
    parser.add_argument(
        "--monitor-set",
        default="residual",
        help="Monitor set name to export. Defaults to residual.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "output"),
        help="Directory where the PNG file will be written.",
    )
    parser.add_argument(
        "--filename-prefix",
        default="scaled_residuals",
        help="Prefix used for the output filename.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="Maximum time to wait for residual history to appear.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=0.5,
        help="How often to check for monitor data while waiting.",
    )
    parser.add_argument(
        "--settle-seconds",
        type=float,
        default=0.5,
        help="Initial pause after starting monitor streaming.",
    )
    parser.add_argument(
        "--title",
        default="Scaled Residual History",
        help="Title used on the plot.",
    )
    return parser


def wait_for_monitor_data(solver, monitor_set: str, timeout: float, interval: float):
    deadline = time.time() + timeout
    while time.time() < deadline:
        monitor_names = solver.monitors.get_monitor_set_names()
        if monitor_set in monitor_names:
            x_values, series = solver.monitors.get_monitor_set_data(monitor_set)
            if len(x_values):
                return x_values, series
        time.sleep(interval)
    raise TimeoutError(
        f"Timed out waiting for monitor set '{monitor_set}' to populate "
        f"after {timeout:.1f} seconds."
    )


def plot_residuals(x_values, series: dict[str, object], title: str, output_path: Path) -> None:
    df = pd.DataFrame(series, index=x_values)
    df.index.name = "iteration"

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)
    for column in df.columns:
        ax.plot(df.index, df[column], linewidth=1.5, label=column)

    ax.set_yscale("log")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Scaled residual")
    ax.set_title(title)
    ax.grid(True, which="major", linestyle="-", alpha=0.25)
    ax.grid(True, which="minor", linestyle=":", alpha=0.18)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=2,
        frameon=False,
        fontsize=9,
    )

    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{args.filename_prefix}_{timestamp}.png"

    solver = connect()
    print("\nConnected. Starting residual monitor stream...")
    solver.monitors.start()

    try:
        time.sleep(max(args.settle_seconds, 0.0))
        x_values, series = wait_for_monitor_data(
            solver,
            args.monitor_set,
            timeout=args.timeout_seconds,
            interval=args.poll_interval_seconds,
        )
        print(
            f"Captured {len(x_values)} points for '{args.monitor_set}' "
            f"across {len(series)} residual curves."
        )
        plot_residuals(x_values, series, args.title, output_path)
        print(f"Saved scaled residual plot to: {output_path}")
    finally:
        try:
            solver.monitors.stop()
        except Exception as exc:
            print(f"Monitor stream stop warning: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())