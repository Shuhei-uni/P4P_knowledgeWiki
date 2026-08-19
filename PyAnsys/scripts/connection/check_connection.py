#!/usr/bin/env python3
"""Quickly report reachability and activity for an existing Fluent session.

The default command answers three separate questions without mutating Fluent:

1. Can the configured TCP endpoint be reached?
2. Can PyFluent complete the gRPC handoff?
3. Does observable solver progress change during a short activity window?

Use ``--print-console [SECONDS]`` to also stream new Fluent console output for
a fixed duration after the activity check. Console streaming is intentionally
opt-in; omitting SECONDS uses a 10-second sample.
"""

from __future__ import annotations

import os
from queue import Empty, Queue
import socket
import sys
from threading import Thread
import time
import warnings
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
from pyansys_fluent.native_run_monitor import collect_snapshot  # noqa: E402


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
        print(f"Endpoint : REACHABLE ({target}; {elapsed:.2f} s)")
    elif status == "not_probed":
        print(f"Endpoint : NOT PROBED ({detail})")
    elif status == "unavailable":
        print(f"Endpoint : UNKNOWN ({detail})")
    elif status == "invalid_configuration":
        print(f"Endpoint : INVALID ({detail})")
    else:
        suffix = f"; {detail}" if detail else ""
        print(f"Endpoint : {status.upper()} ({target}{suffix})")


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


def _collect_snapshot_with_timeout(
    solver: object,
    timeout_seconds: float,
    *,
    previous_state: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, Exception | None]:
    value, error = _call_with_timeout(
        lambda: collect_snapshot(
            solver,
            previous_state=previous_state,
            monitor_sets=("residual",),
        ),
        timeout_seconds,
    )
    if error is not None:
        return None, error
    if not isinstance(value, dict):
        return None, RuntimeError("Fluent returned an invalid status snapshot")
    return value, None


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def classify_activity(
    first: dict[str, Any] | None,
    second: dict[str, Any] | None,
) -> tuple[str, str]:
    """Classify observable activity without falsely claiming that Fluent is idle."""
    if first is None or second is None:
        return "UNKNOWN", "one or both status snapshots were unavailable"

    first_iteration = _numeric(first.get("progress", {}).get("iteration"))
    second_iteration = _numeric(second.get("progress", {}).get("iteration"))
    first_flow_time = _numeric(first.get("runtime", {}).get("flow_time"))
    second_flow_time = _numeric(second.get("runtime", {}).get("flow_time"))

    if (
        first_iteration is not None
        and second_iteration is not None
        and second_iteration > first_iteration
    ):
        return "RUNNING", "iteration advanced"

    if (
        first_flow_time is not None
        and second_flow_time is not None
        and second_flow_time > first_flow_time
    ):
        return "RUNNING", "flow time advanced"

    if first_iteration is not None and second_iteration is not None:
        if second_iteration < first_iteration:
            return "UNKNOWN", "iteration went backwards or the case was reloaded"
        return "QUIESCENT", "no progress detected during the activity window"

    if first_flow_time is not None and second_flow_time is not None:
        if second_flow_time < first_flow_time:
            return "UNKNOWN", "flow time went backwards or the case was reloaded"
        return "QUIESCENT", "no progress detected during the activity window"

    return "UNKNOWN", "Fluent did not expose a comparable iteration or flow time"


def _latest_snapshot(
    first: dict[str, Any] | None,
    second: dict[str, Any] | None,
) -> dict[str, Any] | None:
    return second if second is not None else first


def print_activity_summary(
    first: dict[str, Any] | None,
    second: dict[str, Any] | None,
    *,
    activity_window_seconds: float,
    first_error: Exception | None = None,
    second_error: Exception | None = None,
) -> str:
    """Print a compact status summary and return the activity classification."""
    activity, reason = classify_activity(first, second)
    if activity == "QUIESCENT":
        print(f"Activity : QUIESCENT ({reason}; not proof of idle)")
    elif activity == "UNKNOWN" and (first_error or second_error):
        detail = second_error or first_error
        print(f"Activity : UNKNOWN ({type(detail).__name__}: {detail})")
    else:
        print(f"Activity : {activity} ({reason})")

    if first is not None and second is not None:
        first_iteration = _numeric(first.get("progress", {}).get("iteration"))
        second_iteration = _numeric(second.get("progress", {}).get("iteration"))
        if first_iteration is not None and second_iteration is not None:
            delta = second_iteration - first_iteration
            if delta > 0:
                print(
                    "Iteration: "
                    f"{_format_value(first_iteration)} -> {_format_value(second_iteration)} "
                    f"(+{_format_value(delta)} in {_format_value(activity_window_seconds)} s)"
                )
            else:
                print(
                    "Iteration: "
                    f"{_format_value(second_iteration)} "
                    f"(unchanged over {_format_value(activity_window_seconds)} s)"
                )

        first_flow = _numeric(first.get("runtime", {}).get("flow_time"))
        second_flow = _numeric(second.get("runtime", {}).get("flow_time"))
        if first_flow is not None and second_flow is not None:
            delta_flow = second_flow - first_flow
            if delta_flow > 0:
                print(
                    "Flow time: "
                    f"{_format_value(first_flow)} -> {_format_value(second_flow)} "
                    f"(+{_format_value(delta_flow)} s)"
                )
            else:
                print(f"Flow time: {_format_value(second_flow)}")

    latest = _latest_snapshot(first, second)
    if latest is None:
        return activity

    version = latest.get("fluent_version")
    if version:
        print(f"Fluent   : {version}")

    residual = latest.get("monitors", {}).get("residual", {})
    last_values = residual.get("last_values", {})
    if last_values:
        print("Residuals:")
        for name, value in last_values.items():
            print(f"  {name:<14} {_format_value(value)}")

    return activity


def start_console_stream(solver: Any) -> Any | None:
    """Opt in to new Fluent transcript output on stdout for this client only."""
    transcript = getattr(solver, "transcript", None)
    if transcript is None:
        print("Console  : UNAVAILABLE (PyFluent transcript service is not exposed)")
        return None

    try:
        if bool(getattr(transcript, "is_streaming", False)):
            transcript.stop()
        transcript.start(write_to_stdout=True)
    except Exception as exc:
        print(f"Console  : UNAVAILABLE ({type(exc).__name__}: {exc})")
        return None

    return transcript


def stop_console_stream(transcript: Any | None) -> None:
    if transcript is None:
        return
    try:
        transcript.stop()
    except Exception:
        pass


def stream_console_for(
    solver: Any,
    duration_seconds: float,
    *,
    sleep_fn: Any = time.sleep,
) -> bool:
    """Stream new Fluent transcript output for exactly one operator-selected window."""
    transcript = start_console_stream(solver)
    if transcript is None:
        return False

    print(f"Console  : STREAMING for {_format_value(duration_seconds)} s")
    print("--- Fluent console sample ---")
    try:
        sleep_fn(duration_seconds)
    finally:
        stop_console_stream(transcript)
    print("--- end Fluent console sample ---")
    return True


def main() -> int:
    parser = build_parser()
    parser.description = "Quickly check whether Fluent is reachable, connected, and observably progressing."
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
        "--snapshot-timeout-seconds",
        type=float,
        default=3.0,
        help="Maximum time for each read-only Fluent status snapshot. Default: 3.",
    )
    parser.add_argument(
        "--activity-window-seconds",
        type=float,
        default=2.0,
        help="Delay between two status snapshots used to detect progress. Default: 2.",
    )
    parser.add_argument(
        "--print-console",
        nargs="?",
        type=float,
        const=10.0,
        default=None,
        metavar="SECONDS",
        help=(
            "After the status check, stream new Fluent console output for SECONDS. "
            "Use the flag without a value for 10 seconds. Off by default."
        ),
    )
    args = parser.parse_args()

    for name in (
        "connect_timeout_seconds",
        "endpoint_probe_timeout_seconds",
        "snapshot_timeout_seconds",
        "activity_window_seconds",
    ):
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be greater than zero")
    if args.print_console is not None and args.print_console <= 0:
        parser.error("--print-console SECONDS must be greater than zero")

    server_id = _normalize_server_id(str(args.server_id))
    suppress_repeated_insecure_transport_warnings()
    print(f"Fluent server: {server_id}\n")

    endpoint = probe_endpoint(
        server_id,
        timeout_seconds=args.endpoint_probe_timeout_seconds,
    )
    print_endpoint_probe(endpoint)
    if endpoint.get("status") in {"unreachable", "timed_out", "invalid_configuration"}:
        print("gRPC     : NOT ATTEMPTED")
        print("Activity : UNKNOWN")
        return 2

    solver, connection_error = _call_with_timeout(
        lambda: connect(server_id=server_id, start_transcript=False),
        args.connect_timeout_seconds,
    )
    if connection_error is not None:
        print(f"gRPC     : FAILED ({type(connection_error).__name__}: {connection_error})")
        print("Activity : UNKNOWN")
        return 2

    print("gRPC     : CONNECTED")

    first, first_error = _collect_snapshot_with_timeout(
        solver,
        args.snapshot_timeout_seconds,
    )
    time.sleep(args.activity_window_seconds)
    second, second_error = _collect_snapshot_with_timeout(
        solver,
        args.snapshot_timeout_seconds,
        previous_state=first,
    )

    print()
    print_activity_summary(
        first,
        second,
        activity_window_seconds=args.activity_window_seconds,
        first_error=first_error,
        second_error=second_error,
    )

    if args.print_console is not None:
        print()
        stream_console_for(solver, args.print_console)

    print("\nRead-only check complete; no solver command was issued and Fluent was not closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
