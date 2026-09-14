#!/usr/bin/env python3
"""Check TCP reachability, gRPC connectivity, and Fluent run activity.

This command is deliberately narrow and read-only. It reports:

1. whether the configured TCP endpoint is reachable;
2. whether PyFluent can connect to the Fluent gRPC server; and
3. whether Fluent's direct ``solution.run_calculation.iterating()`` query
   returns the boolean ``True``.

The activity verdict is intentionally binary. Only an exact boolean ``True``
from the direct Fluent query produces ``RUNNING``. ``False``, an unavailable
query, an exception, a timeout, or any other return value produces
``NOT RUNNING``. This checker does not read or print residuals, monitor
history, iteration counters, flow time, case data, or solver configuration.
"""

from __future__ import annotations

import io
import os
from queue import Empty, Queue
import socket
import sys
from threading import Thread
import time
import warnings
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import (  # noqa: E402
    build_parser,
    connect,
    endpoint_env_namespace,
    load_dotenv,
)


def _normalize_server_id(value: str) -> str:
    normalized = value.strip().lower()
    if normalized.startswith("ip"):
        normalized = normalized[2:]
    return normalized or "1"


def _format_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def suppress_repeated_insecure_transport_warnings() -> None:
    """Keep this intentionally small status CLI quiet unless something matters."""
    warnings.simplefilter("ignore")


def probe_endpoint(server_id: str, *, timeout_seconds: float = 2.0) -> dict[str, Any]:
    """Probe only the configured TCP endpoint; do not authenticate or call Fluent."""
    load_dotenv(PROJECT_ROOT / ".env")
    _label, env_prefix, suffix = endpoint_env_namespace(server_id)
    ip_key = f"{env_prefix}_IP{suffix}"
    port_key = f"{env_prefix}_PORT{suffix}"
    server_info_key = f"{env_prefix}_SERVER_INFO_FILE{suffix}"
    host = os.getenv(ip_key, "").strip()
    port_text = os.getenv(port_key, "").strip()

    if not host or not port_text:
        if os.getenv(server_info_key, "").strip():
            return {
                "status": "not_probed",
                "detail": f"using {server_info_key}",
            }
        return {
            "status": "unavailable",
            "detail": f"configure {ip_key} and {port_key}",
        }

    try:
        port = int(port_text)
        if not 1 <= port <= 65535:
            raise ValueError("port must be between 1 and 65535")
    except ValueError as exc:
        return {
            "status": "invalid_configuration",
            "detail": f"invalid port {port_text!r}: {exc}",
        }

    target = f"{host}:{port}"
    started_at = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            elapsed = time.monotonic() - started_at
        return {
            "status": "reachable",
            "target": target,
            "elapsed_seconds": elapsed,
        }
    except socket.timeout:
        return {
            "status": "timed_out",
            "target": target,
            "detail": f"no TCP response within {timeout_seconds:g} s",
        }
    except OSError as exc:
        return {
            "status": "unreachable",
            "target": target,
            "detail": exc.strerror or str(exc),
        }


def print_endpoint_probe(probe: dict[str, Any]) -> None:
    status = str(probe.get("status", "unknown"))
    target = probe.get("target")
    detail = probe.get("detail")
    if status == "reachable":
        elapsed = float(probe.get("elapsed_seconds", 0.0))
        print(f"TCP      : CONNECTED ({target}; {elapsed:.2f} s)")
    else:
        suffix = f"; {detail}" if detail else ""
        explanation = f"{target}{suffix}" if target else str(detail or status)
        print(f"TCP      : NOT CONNECTED ({explanation})")


def _call_with_timeout(func: Any, timeout_seconds: float) -> tuple[Any | None, Exception | None]:
    """Run one potentially blocking Fluent call within a wall-clock budget."""
    result: Queue[tuple[Any | None, Exception | None]] = Queue(maxsize=1)

    def invoke() -> None:
        try:
            result.put((func(), None))
        except Exception as exc:
            result.put((None, exc))

    Thread(target=invoke, daemon=True).start()
    try:
        return result.get(timeout=timeout_seconds)
    except Empty:
        return None, TimeoutError("Fluent did not return before the deadline")


def read_iterating_state(solver: Any) -> tuple[bool, str]:
    """Return RUNNING only for an exact boolean True from Fluent's query."""
    try:
        run_calculation = solver.settings.solution.run_calculation
        query = getattr(run_calculation, "iterating")
        if not callable(query):
            return False, "solution.run_calculation.iterating is not callable"
        value = query()
    except Exception as exc:
        return False, (
            "solution.run_calculation.iterating did not return true "
            f"({type(exc).__name__}: {exc})"
        )

    if value is True:
        return True, "solution.run_calculation.iterating returned true"
    return False, f"solution.run_calculation.iterating returned {_format_value(value)!r}, not true"


def read_iterating_state_with_timeout(
    solver: Any,
    timeout_seconds: float,
) -> tuple[bool, str]:
    """Bound the direct Fluent query and collapse all non-True states."""
    value, error = _call_with_timeout(
        lambda: read_iterating_state(solver),
        timeout_seconds,
    )
    if error is not None:
        return False, (
            "solution.run_calculation.iterating did not return true "
            f"({type(error).__name__}: {error})"
        )
    if not isinstance(value, tuple) or len(value) != 2:
        return False, "solution.run_calculation.iterating did not return true (invalid query result)"
    is_running, reason = value
    if is_running is True:
        return True, str(reason)
    return False, str(reason)


def print_activity(is_running: bool, reason: str) -> None:
    """Print the required binary activity verdict."""
    state = "RUNNING" if is_running is True else "NOT RUNNING"
    print(f"Activity : {state} ({reason})")


def connect_quietly(server_id: str) -> Any:
    """Connect without leaking the connection helper's progress line into this summary."""
    with warnings.catch_warnings(), redirect_stdout(io.StringIO()):
        warnings.simplefilter("ignore")
        return connect(server_id=server_id, start_transcript=False)


def main() -> int:
    parser = build_parser()
    parser.description = "Check TCP reachability, gRPC connectivity, and Fluent running state."
    parser.add_argument(
        "--connect-timeout-seconds",
        type=float,
        default=5.0,
        help="Maximum time for the PyFluent/gRPC handoff. Default: 5.",
    )
    parser.add_argument(
        "--endpoint-probe-timeout-seconds",
        type=float,
        default=2.0,
        help="TCP reachability-probe timeout. Default: 2.",
    )
    parser.add_argument(
        "--activity-timeout-seconds",
        type=float,
        default=3.0,
        help="Maximum time for Fluent's direct iterating query. Default: 3.",
    )
    args = parser.parse_args()

    for name in (
        "connect_timeout_seconds",
        "endpoint_probe_timeout_seconds",
        "activity_timeout_seconds",
    ):
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be greater than zero")

    server_id = _normalize_server_id(str(args.server_id))
    suppress_repeated_insecure_transport_warnings()
    print(f"Fluent server: {server_id}\n")

    endpoint = probe_endpoint(
        server_id,
        timeout_seconds=args.endpoint_probe_timeout_seconds,
    )
    print_endpoint_probe(endpoint)
    if endpoint.get("status") in {"unreachable", "timed_out", "invalid_configuration"}:
        print("gRPC     : NOT CONNECTED")
        print_activity(False, "gRPC connection was not established")
        return 2

    solver, connection_error = _call_with_timeout(
        lambda: connect_quietly(server_id),
        args.connect_timeout_seconds,
    )
    if connection_error is not None:
        print(f"gRPC     : NOT CONNECTED ({type(connection_error).__name__}: {connection_error})")
        print_activity(False, "gRPC connection was not established")
        return 2

    print("gRPC     : CONNECTED")
    is_running, reason = read_iterating_state_with_timeout(
        solver,
        args.activity_timeout_seconds,
    )
    print_activity(is_running, reason)

    print("\nRead-only check complete; no solver command was issued and Fluent was not closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
