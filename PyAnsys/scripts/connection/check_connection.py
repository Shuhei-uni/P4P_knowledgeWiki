#!/usr/bin/env python3
"""Connect to an already-running remote Fluent session.

This is the script to run when you are at/near the Fluent PC and have started
Fluent's gRPC server.

It uses either:
- FLUENT_SERVER_INFO_FILE{N}, or
- FLUENT_IP{N} + FLUENT_PORT{N} + FLUENT_PASSWORD{N}

from a .env file or shell environment.
"""

from __future__ import annotations

import contextlib
import signal
import sys
from pathlib import Path
from typing import Iterator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import build_parser, connect  # noqa: E402


class OperationTimeout(TimeoutError):
    pass


@contextlib.contextmanager
def timeout_after(seconds: float, label: str) -> Iterator[None]:
    if seconds <= 0:
        yield
        return

    def handle_timeout(_signum, _frame):
        raise OperationTimeout(f"{label} timed out after {seconds:.1f}s")

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, 0)
    signal.signal(signal.SIGALRM, handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        signal.signal(signal.SIGALRM, previous_handler)


def print_check(label: str, func, timeout_seconds: float) -> bool:
    try:
        with timeout_after(timeout_seconds, label):
            print(f"{label}:", func())
        return True
    except OperationTimeout as exc:
        print(f"{label}: TIMEOUT -> {exc}")
        return False
    except Exception as exc:
        print(f"{label} not available: {exc}")
        return True


def main() -> int:
    parser = build_parser()
    parser.add_argument(
        "--connect-timeout-seconds",
        type=float,
        default=60.0,
        help="Wall-clock timeout around the PyFluent connect call. Use 0 to disable.",
    )
    parser.add_argument(
        "--health-timeout-seconds",
        type=float,
        default=15.0,
        help="Wall-clock timeout around each health/version RPC. Use 0 to disable.",
    )
    args = parser.parse_args()

    try:
        with timeout_after(args.connect_timeout_seconds, "connect_to_fluent"):
            solver = connect(server_id=args.server_id, tcp_timeout_seconds=args.tcp_timeout_seconds)
    except OperationTimeout as exc:
        print(f"Connection timed out: {exc}")
        print(
            "TCP may still be open while Fluent gRPC is wedged. Restart the Fluent "
            "gRPC server/session on the Windows PC before retrying."
        )
        return 2

    print("\nConnected to Fluent.")

    # Different PyFluent versions expose health checks slightly differently,
    # so try a few non-mutating ways.
    ok = True
    ok &= print_check("Health status", lambda: solver.health_check.status(), args.health_timeout_seconds)
    ok &= print_check("Health check", lambda: solver.health_check.check_health(), args.health_timeout_seconds)
    ok &= print_check("Fluent version", solver.get_fluent_version, args.health_timeout_seconds)

    print("\nDone. This script did not close Fluent.")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
