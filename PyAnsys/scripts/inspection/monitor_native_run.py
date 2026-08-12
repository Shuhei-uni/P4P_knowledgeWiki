#!/usr/bin/env python3
"""Monitor a Fluent-native run with automatic reconnects.

This client is intentionally read-only. It never initializes, iterates, saves,
reloads, interrupts, or shuts down the Fluent process.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.native_run_monitor import (  # noqa: E402
    CheckpointPair,
    MonitorConfig,
    run_monitor,
)
from pyansys_fluent.connection import connect  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only monitor for a Fluent-native run. Reconnects with bounded "
            "backoff and never controls the calculation."
        )
    )
    parser.add_argument(
        "--server-id",
        default="1",
        help="Connection alias only; it is not case identity. Default: 1.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=30.0,
        help="Seconds between successful snapshots. Default: 30.",
    )
    parser.add_argument(
        "--reconnect-initial-delay-seconds",
        type=float,
        default=2.0,
        help="Initial delay after a connection failure. Default: 2.",
    )
    parser.add_argument(
        "--reconnect-max-delay-seconds",
        type=float,
        default=60.0,
        help="Maximum exponential-backoff delay. Default: 60.",
    )
    parser.add_argument(
        "--max-reconnect-attempts",
        type=int,
        default=0,
        help="Maximum consecutive reconnect attempts; 0 means keep trying until Ctrl-C.",
    )
    parser.add_argument(
        "--duration-seconds",
        type=float,
        default=0.0,
        help="Stop after this many seconds; 0 means run until Ctrl-C.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Connect, collect one snapshot, persist it, and exit.",
    )
    parser.add_argument(
        "--monitor-set",
        action="append",
        dest="monitor_sets",
        help="Monitor set to read; repeat this option. Defaults to residual.",
    )
    parser.add_argument(
        "--no-monitors",
        action="store_true",
        help="Skip monitor streaming reads and report runtime/health only.",
    )
    parser.add_argument(
        "--checkpoint-pair",
        nargs=2,
        action="append",
        metavar=("CASE", "DATA"),
        default=[],
        help=(
            "Remote case/data pair to check without loading it. Repeat for retained "
            "native autosave pairs."
        ),
    )
    parser.add_argument(
        "--state-json",
        default=str(PROJECT_ROOT / "output" / "native_run_monitor_state.json"),
        help="Local atomic latest-snapshot path.",
    )
    parser.add_argument(
        "--events-jsonl",
        default=str(PROJECT_ROOT / "output" / "native_run_monitor_events.jsonl"),
        help="Local append-only event log path.",
    )
    parser.add_argument(
        "--run-label",
        default="",
        help="Optional operator-supplied label; never inferred as case identity.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    monitor_sets = () if args.no_monitors else tuple(args.monitor_sets or ["residual"])
    checkpoint_pairs = tuple(
        CheckpointPair(case_path=case_path, data_path=data_path)
        for case_path, data_path in args.checkpoint_pair
    )
    config = MonitorConfig(
        server_id=str(args.server_id),
        poll_interval_seconds=args.poll_interval_seconds,
        reconnect_initial_delay_seconds=args.reconnect_initial_delay_seconds,
        reconnect_max_delay_seconds=args.reconnect_max_delay_seconds,
        max_reconnect_attempts=args.max_reconnect_attempts,
        duration_seconds=args.duration_seconds,
        once=args.once,
        monitor_sets=monitor_sets,
        checkpoint_pairs=checkpoint_pairs,
        state_json=Path(args.state_json).expanduser(),
        events_jsonl=Path(args.events_jsonl).expanduser(),
        run_label=args.run_label,
    )

    def emit(event) -> None:
        print(json.dumps(event, default=str), flush=True)

    return run_monitor(config, connect_fn=connect, emit_fn=emit)


if __name__ == "__main__":
    raise SystemExit(main())

