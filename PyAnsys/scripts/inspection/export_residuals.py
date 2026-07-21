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
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.postprocess_live import (  # noqa: E402
    capture_residual_history,
    plot_residual_history,
    write_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export a scaled residual plot from the current Fluent session."
    )
    parser.add_argument(
        "--server-id",
        default="1",
        help="Configured Fluent server id. Default: 1.",
    )
    parser.add_argument(
        "--monitor-set",
        default="residual",
        help="Monitor set name to export. Defaults to residual.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "output"),
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


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{args.filename_prefix}_{timestamp}.png"

    solver = connect(server_id=args.server_id)
    print("\nConnected. Starting residual monitor stream...")
    payload = capture_residual_history(
        solver,
        monitor_set=args.monitor_set,
        timeout=args.timeout_seconds,
        interval=args.poll_interval_seconds,
        settle_seconds=args.settle_seconds,
    )
    print(
        f"Captured {payload['point_count']} points for '{args.monitor_set}' "
        f"across {payload['curve_count']} residual curves."
    )
    plot_residual_history(payload, output_path, title=args.title)
    write_json(output_path.with_suffix(".json"), payload)
    print(f"Saved scaled residual plot to: {output_path}")
    print(f"Saved residual data to: {output_path.with_suffix('.json')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
