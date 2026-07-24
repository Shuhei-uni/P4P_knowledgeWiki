#!/usr/bin/env python3
"""Launch the narrow self-healing Fluent watchdog on the Fluent computer."""

from __future__ import annotations

import argparse
import os
import signal
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import bool_env  # noqa: E402
from pyansys_fluent.fluent_watchdog import (  # noqa: E402
    ExclusiveWatchdogLock,
    FluentWatchdog,
    RestartLimitExceeded,
    WatchdogAlreadyRunning,
    WatchdogConfig,
)


def build_parser() -> argparse.ArgumentParser:
    bridge_default = os.getenv("FLUENT_BRIDGE_DIR", "")
    runtime_default = os.getenv(
        "FLUENT_WATCHDOG_WORK_DIR",
        str(PROJECT_ROOT / "output" / "fluent_watchdog"),
    )
    parser = argparse.ArgumentParser(
        description=(
            "Keep Fluent available, publish replacement gRPC credentials, and "
            "restart only after process death or repeated health failures."
        )
    )
    parser.add_argument(
        "--fluent-exe",
        default=os.getenv("FLUENT_LOCAL_EXE", ""),
        help="Absolute path to fluent.exe (or FLUENT_LOCAL_EXE).",
    )
    parser.add_argument(
        "--bridge-dir",
        default=bridge_default,
        help="Private shared directory (or FLUENT_BRIDGE_DIR).",
    )
    parser.add_argument(
        "--advertised-host",
        default=os.getenv("FLUENT_ADVERTISED_HOST", ""),
        help="Laptop-reachable Fluent host/IP (or FLUENT_ADVERTISED_HOST).",
    )
    parser.add_argument(
        "--runtime-dir",
        default=runtime_default,
        help=(
            "Host-local logs/server-info directory. Defaults to "
            "PyAnsys/output/fluent_watchdog."
        ),
    )
    parser.add_argument(
        "--dimension",
        type=int,
        choices=(2, 3),
        default=int(os.getenv("FLUENT_LOCAL_DIMENSION", "3")),
    )
    parser.add_argument(
        "--precision",
        choices=("single", "double"),
        default=os.getenv("FLUENT_LOCAL_PRECISION", "double"),
    )
    parser.add_argument(
        "--processor-count",
        type=int,
        default=int(os.getenv("FLUENT_LOCAL_PROCESSOR_COUNT", "2")),
    )
    parser.add_argument(
        "--gui",
        action=argparse.BooleanOptionalAction,
        default=bool_env("FLUENT_LOCAL_GUI", False),
    )
    parser.add_argument(
        "--insecure-mode",
        action=argparse.BooleanOptionalAction,
        default=bool_env("FLUENT_INSECURE_MODE", False),
    )
    parser.add_argument(
        "--startup-timeout",
        type=float,
        default=float(os.getenv("FLUENT_LOCAL_STARTUP_TIMEOUT", "180")),
    )
    parser.add_argument("--connect-timeout", type=float, default=60.0)
    parser.add_argument(
        "--health-timeout",
        type=float,
        default=float(
            os.getenv("FLUENT_WATCHDOG_HEALTH_TIMEOUT_SECONDS", "10")
        ),
    )
    parser.add_argument(
        "--health-interval",
        type=float,
        default=float(
            os.getenv("FLUENT_WATCHDOG_HEALTH_INTERVAL_SECONDS", "10")
        ),
    )
    parser.add_argument("--heartbeat-interval", type=float, default=5.0)
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument(
        "--restart-delay",
        type=float,
        default=float(
            os.getenv("FLUENT_WATCHDOG_RESTART_DELAY_SECONDS", "5")
        ),
    )
    parser.add_argument("--health-failures", type=int, default=3)
    parser.add_argument(
        "--max-restarts",
        type=int,
        default=int(os.getenv("FLUENT_WATCHDOG_MAX_RESTARTS", "3")),
    )
    parser.add_argument(
        "--restart-window",
        type=float,
        default=float(
            os.getenv("FLUENT_WATCHDOG_RESTART_WINDOW_SECONDS", "600")
        ),
    )
    parser.add_argument(
        "--max-runtime",
        type=float,
        default=0.0,
        help="Optional smoke-test runtime. Zero runs until stopped.",
    )
    parser.add_argument(
        "--extra-fluent-arg",
        action="append",
        default=[],
        help="Additional literal Fluent launch argument; repeat as needed.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    missing = []
    if not str(args.fluent_exe).strip():
        missing.append("--fluent-exe/FLUENT_LOCAL_EXE")
    if not str(args.bridge_dir).strip():
        missing.append("--bridge-dir/FLUENT_BRIDGE_DIR")
    if not str(args.advertised_host).strip():
        missing.append("--advertised-host/FLUENT_ADVERTISED_HOST")
    if missing:
        print("Missing required configuration: " + ", ".join(missing), file=sys.stderr)
        return 2
    runtime_dir = Path(args.runtime_dir).expanduser()
    config = WatchdogConfig(
        fluent_exe=Path(args.fluent_exe).expanduser().resolve(),
        bridge_dir=Path(args.bridge_dir).expanduser().resolve(),
        advertised_host=args.advertised_host,
        runtime_dir=runtime_dir.resolve(),
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
        poll_interval_seconds=args.poll_interval,
        restart_delay_seconds=args.restart_delay,
        consecutive_health_failures=args.health_failures,
        max_restarts=args.max_restarts,
        restart_window_seconds=args.restart_window,
        extra_fluent_args=tuple(args.extra_fluent_arg),
    )
    try:
        config.validate()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Invalid watchdog configuration: {exc}", file=sys.stderr)
        return 2

    watchdog = FluentWatchdog(config)

    def request_stop(_signum, _frame) -> None:
        watchdog.request_stop()

    signal.signal(signal.SIGINT, request_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, request_stop)
    print(
        f"Connection status: {config.bridge_dir / 'latest_connection.json'}",
        flush=True,
    )
    print(f"Watchdog runtime: {config.runtime_dir}", flush=True)
    try:
        with ExclusiveWatchdogLock(config.lock_path):
            watchdog.run(max_runtime_seconds=args.max_runtime)
    except WatchdogAlreadyRunning as exc:
        print(f"Watchdog did not start: {exc}", file=sys.stderr)
        return 3
    except RestartLimitExceeded as exc:
        print(f"Watchdog failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(
            f"Watchdog failed unexpectedly: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1
    print("Watchdog stopped cleanly.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
