#!/usr/bin/env python3
"""Launch and supervise Fluent on the Fluent Windows computer."""

from __future__ import annotations

import argparse
import os
import signal
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.host_worker import (  # noqa: E402
    ExclusiveHostLock,
    FluentHostWorker,
    HostWorkerConfig,
    HostWorkerAlreadyRunning,
    RestartLimitExceeded,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a persistent Fluent-host supervisor. It launches Fluent, waits "
            "for a fresh server-info file, verifies gRPC health, publishes a "
            "heartbeat, and relaunches Fluent after bounded failures."
        )
    )
    parser.add_argument(
        "--fluent-exe",
        default=os.getenv("FLUENT_LOCAL_EXE", ""),
        help="Absolute path to fluent.exe. Defaults to FLUENT_LOCAL_EXE.",
    )
    parser.add_argument(
        "--work-dir",
        default=os.getenv(
            "FLUENT_HOST_WORK_DIR",
            str(PROJECT_ROOT / "output" / "fluent_host_worker"),
        ),
        help="Host-local directory for status, server-info, and Fluent logs.",
    )
    parser.add_argument("--dimension", type=int, choices=(2, 3), default=3)
    parser.add_argument(
        "--precision",
        choices=("single", "double"),
        default="double",
    )
    parser.add_argument("--processor-count", type=int, default=2)
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch Fluent with its GUI. Headless mode is the default.",
    )
    parser.add_argument(
        "--insecure-mode",
        action="store_true",
        help="Pass insecure_mode=True when attaching through PyFluent.",
    )
    parser.add_argument("--startup-timeout", type=float, default=180.0)
    parser.add_argument("--connect-timeout", type=float, default=60.0)
    parser.add_argument("--health-timeout", type=float, default=10.0)
    parser.add_argument("--health-interval", type=float, default=10.0)
    parser.add_argument("--heartbeat-interval", type=float, default=5.0)
    parser.add_argument("--job-poll-interval", type=float, default=1.0)
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument("--restart-delay", type=float, default=5.0)
    parser.add_argument("--max-restarts", type=int, default=3)
    parser.add_argument("--restart-window", type=float, default=600.0)
    parser.add_argument(
        "--max-runtime",
        type=float,
        default=0.0,
        help="Optional smoke-test runtime in seconds. Zero runs until stopped.",
    )
    parser.add_argument(
        "--extra-fluent-arg",
        action="append",
        default=[],
        help="Additional literal Fluent launch argument. Repeat as needed.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not str(args.fluent_exe).strip():
        print(
            "Missing --fluent-exe and FLUENT_LOCAL_EXE is not set.",
            file=sys.stderr,
        )
        return 2

    config = HostWorkerConfig(
        fluent_exe=Path(args.fluent_exe).expanduser().resolve(),
        work_dir=Path(args.work_dir).expanduser().resolve(),
        dimension=args.dimension,
        precision=args.precision,
        processor_count=args.processor_count,
        gui=args.gui,
        insecure_mode=args.insecure_mode,
        startup_timeout_seconds=args.startup_timeout,
        connect_timeout_seconds=args.connect_timeout,
        health_timeout_seconds=args.health_timeout,
        health_interval_seconds=args.health_interval,
        heartbeat_interval_seconds=args.heartbeat_interval,
        job_poll_interval_seconds=args.job_poll_interval,
        poll_interval_seconds=args.poll_interval,
        restart_delay_seconds=args.restart_delay,
        max_restarts=args.max_restarts,
        restart_window_seconds=args.restart_window,
        extra_fluent_args=tuple(args.extra_fluent_arg),
    )

    try:
        config.validate(require_executable=True)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Invalid host-worker configuration: {exc}", file=sys.stderr)
        return 2

    worker = FluentHostWorker(config)

    def request_stop(_signum, _frame) -> None:
        worker.request_stop()

    signal.signal(signal.SIGINT, request_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, request_stop)

    print(f"Host worker status: {config.status_path}", flush=True)
    print(
        f"Fluent server-info generations: {config.work_dir / 'fluent-server-info-NNN.txt'}",
        flush=True,
    )
    print(
        f"Incoming job spool: {config.work_dir / 'jobs' / 'incoming'}",
        flush=True,
    )
    try:
        with ExclusiveHostLock(config.work_dir / "host-worker.lock"):
            worker.run(max_runtime_seconds=args.max_runtime)
    except HostWorkerAlreadyRunning as exc:
        print(f"Host worker did not start: {exc}", file=sys.stderr, flush=True)
        return 3
    except RestartLimitExceeded as exc:
        print(f"Host worker failed: {exc}", file=sys.stderr, flush=True)
        return 1
    except Exception as exc:
        print(
            f"Host worker failed unexpectedly: {type(exc).__name__}: {exc}",
            file=sys.stderr,
            flush=True,
        )
        return 1
    print("Host worker stopped cleanly.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
