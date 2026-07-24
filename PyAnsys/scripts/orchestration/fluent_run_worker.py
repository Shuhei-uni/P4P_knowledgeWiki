#!/usr/bin/env python3
"""Poll the private bridge for narrow Fluent run requests."""

from __future__ import annotations

import argparse
import os
import signal
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.run_worker import FluentRunWorker  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Process only generation-pinned load/run/checkpoint/save requests. "
            "This worker never launches or restarts Fluent."
        )
    )
    parser.add_argument(
        "--bridge-dir",
        default=os.getenv("FLUENT_BRIDGE_DIR", ""),
        help="Private shared bridge directory. Defaults to FLUENT_BRIDGE_DIR.",
    )
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument(
        "--once", action="store_true", help="Process at most one request and exit."
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.bridge_dir:
        print("FLUENT_BRIDGE_DIR or --bridge-dir is required.", file=sys.stderr)
        return 2
    bridge_dir = Path(args.bridge_dir).expanduser()
    if not bridge_dir.is_absolute():
        print("Bridge directory must be absolute.", file=sys.stderr)
        return 2
    if args.poll_interval <= 0:
        print("--poll-interval must be positive.", file=sys.stderr)
        return 2

    worker = FluentRunWorker(bridge_dir)
    stopping = False

    def stop(_signum, _frame) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, stop)

    while not stopping:
        try:
            receipt = worker.process_next()
        except Exception as exc:
            print(
                f"Run request processing failed: {type(exc).__name__}: {exc}",
                file=sys.stderr,
                flush=True,
            )
            return 1
        if receipt is not None:
            print(f"Run receipt: {receipt}", flush=True)
        if args.once:
            break
        time.sleep(args.poll_interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
