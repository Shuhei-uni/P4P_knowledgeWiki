#!/usr/bin/env python3
"""Connect to an already-running remote Fluent session.

This is the script to run when you are at/near the Fluent PC and have started
Fluent's gRPC server.

It uses either:
- FLUENT_SERVER_INFO_FILE{N}, or
- FLUENT_IP{N} + FLUENT_PORT{N} + FLUENT_PASSWORD{N}, or
- STUDENT_SERVER_INFO_FILE, or
- STUDENT_IP + STUDENT_PORT + STUDENT_PASSWORD when called with
  ``--server-id student``

from a .env file or shell environment.
"""

from __future__ import annotations

import json
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
from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.native_run_monitor import collect_snapshot  # noqa: E402


def _normalize_server_id(value: str) -> str:
    normalized = value.strip().lower()
    if normalized.startswith("ip"):
        normalized = normalized[2:]
    return normalized or "1"


def _format_value(value: object) -> str:
    """Format numerical monitor values compactly while preserving other values."""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def suppress_repeated_insecure_transport_warnings() -> None:
    """Suppress Python warning output for this intentionally quiet status CLI.

    Connection failures, reachability failures, and Fluent errors are exceptions
    or explicit status messages, so they remain visible.
    """
    warnings.simplefilter("ignore")


def json_print(label: str, value: Any) -> None:
    """Print a labelled, JSON-formatted read-only state capture."""
    print(f"{label}: {json.dumps(value, indent=2, default=str)}")


def try_value(label: str, func: Any) -> Any:
    """Read and report an optional Fluent branch without failing the check."""
    try:
        value = func()
    except Exception as exc:
        value = {"error": f"{type(exc).__name__}: {exc}"}
    json_print(label, value)
    return value


def print_endpoint_reachability(server_id: str, *, timeout_seconds: float = 3.0) -> str:
    """Report whether the configured direct TCP endpoint can be reached.

    This is a TCP connect probe only: it neither authenticates nor sends a
    Fluent/gRPC request.  It intentionally never prints the configured password.
    """
    load_dotenv(PROJECT_ROOT / ".env")
    _label, env_prefix, suffix = endpoint_env_namespace(server_id)
    ip_key = f"{env_prefix}_IP{suffix}"
    port_key = f"{env_prefix}_PORT{suffix}"
    server_info_key = f"{env_prefix}_SERVER_INFO_FILE{suffix}"
    host = os.getenv(ip_key, "").strip()
    port_text = os.getenv(port_key, "").strip()

    if not host or not port_text:
        if os.getenv(server_info_key, "").strip():
            print(
                "Target TCP reachability: not probed (this endpoint uses "
                f"{server_info_key}, not an explicit {ip_key}/{port_key} pair)"
            )
            return "not_probed"
        else:
            print(
                "Target TCP reachability: unavailable (configure "
                f"{ip_key} and {port_key} to enable the probe)"
            )
            return "unavailable"

    try:
        port = int(port_text)
        if not 1 <= port <= 65535:
            raise ValueError("port must be between 1 and 65535")
    except ValueError as exc:
        print(f"Target TCP reachability: invalid configured port {port_text!r}: {exc}")
        return "invalid_configuration"

    target = f"{host}:{port}"
    started_at = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            elapsed = time.monotonic() - started_at
        print(f"Target TCP reachability: reachable ({target}; connected in {elapsed:.2f} s)")
        return "reachable"
    except socket.timeout:
        print(f"Target TCP reachability: timed out ({target}; no TCP response within {timeout_seconds:g} s)")
        return "timed_out"
    except OSError as exc:
        reason = exc.strerror or str(exc)
        print(f"Target TCP reachability: unreachable ({target}; {reason})")
        return "unreachable"


def _has_live_progress(snapshot: dict[str, Any]) -> bool:
    """Return whether Fluent supplied both a completed iteration and residuals."""
    iteration = snapshot["progress"].get("iteration")
    residual = snapshot["monitors"].get("residual", {})
    return iteration is not None and bool(residual.get("last_values"))


def print_server_status(solver: object) -> bool:
    """Print a read-only, one-shot status summary for the current Fluent session.

    Fluent's residual monitor uses its x-axis for the actual completed flow
    iteration.  This deliberately does not read ``number-of-iterations`` as
    progress because that RP variable is the configured iteration limit.
    """
    try:
        snapshot = collect_snapshot(solver, monitor_sets=("residual",))
    except Exception as exc:
        print(f"Live server status unavailable: {type(exc).__name__}: {exc}")
        return False

    return print_server_status_snapshot(snapshot)


def print_server_status_snapshot(
    snapshot: dict[str, Any],
    *,
    iteration_label: str = "Current iteration",
) -> bool:
    """Print a collected snapshot and return whether it contains live progress."""

    progress = snapshot["progress"]
    iteration = progress["iteration"]
    if iteration is None:
        print(f"{iteration_label}: unavailable (no live monitor iteration returned)")
    else:
        print(f"{iteration_label}: {_format_value(iteration)}")

    residual = snapshot["monitors"].get("residual", {})
    last_values = residual.get("last_values", {})
    if last_values:
        print("Latest residuals:")
        for name, value in last_values.items():
            print(f"  {name}: {_format_value(value)}")
    else:
        detail = residual.get("error")
        if detail:
            print(f"Latest residuals: unavailable ({detail})")
        else:
            print("Latest residuals: unavailable")

    version = snapshot.get("fluent_version")
    if version:
        print(f"Fluent version: {version}")
    health = snapshot.get("health", {})
    if health:
        for name, value in health.items():
            print(f"Health {name}: {_format_value(value)}")

    runtime = snapshot["runtime"]
    configured_iterations = runtime.get("configured_number_of_iterations")
    if configured_iterations is not None:
        print(
            "Configured iteration limit: "
            f"{_format_value(configured_iterations)} "
            "(not a completed-iteration count)"
        )
    flow_time = runtime.get("flow_time")
    if flow_time is not None:
        print(f"Flow time: {_format_value(flow_time)}")

    read_errors = snapshot["read_errors"]
    if read_errors:
        print("Status notes:")
        for error in read_errors:
            print(f"  - {error}")
    return _has_live_progress(snapshot)


def _call_with_timeout(
    func: Any,
    timeout_seconds: float,
) -> tuple[Any | None, Exception | None]:
    """Run one potentially blocking Fluent call within a wall-clock budget."""
    result: Queue[tuple[dict[str, Any] | None, Exception | None]] = Queue(maxsize=1)

    def invoke() -> None:
        try:
            result.put((func(), None))
        except Exception as exc:
            result.put((None, exc))

    # Fluent can be busy inside an iteration or connection handshake. Keeping
    # this worker daemonized lets the CLI honour its deadline if that RPC has
    # not returned.
    Thread(target=invoke, daemon=True).start()
    try:
        return result.get(timeout=timeout_seconds)
    except Empty:
        return None, TimeoutError("Fluent did not return before the deadline")


def _collect_snapshot_with_timeout(
    solver: object,
    timeout_seconds: float,
) -> tuple[dict[str, Any] | None, Exception | None]:
    """Bound one potentially blocking Fluent monitor request by ``timeout_seconds``."""
    value, error = _call_with_timeout(
        lambda: collect_snapshot(solver, monitor_sets=("residual",)),
        timeout_seconds,
    )
    if error is not None:
        return None, error
    if not isinstance(value, dict):
        return None, RuntimeError("Fluent returned an invalid monitor snapshot")
    return value, None


def wait_for_live_server_status(
    solver: object,
    *,
    timeout_seconds: float = 60.0,
    poll_interval_seconds: float = 2.0,
    timeout_label_seconds: float | None = None,
    monotonic_fn: Any = time.monotonic,
    sleep_fn: Any = time.sleep,
) -> bool:
    """Poll for the full window and report the highest iteration observed.

    No solver command is issued. A read that happens while Fluent is busy may
    return the last completed iteration or wait until its current iteration
    reaches a solver-safe point. A newly attached client can receive monitor
    history out of order, so this retains the greatest valid iteration across
    every snapshot instead of returning after the first successful read.
    """
    display_timeout_seconds = timeout_label_seconds or timeout_seconds
    deadline = monotonic_fn() + timeout_seconds
    last_error = "no residual-monitor data was returned"
    highest_snapshot: dict[str, Any] | None = None
    successful_samples = 0

    def report_highest() -> bool:
        if highest_snapshot is None:
            return False
        print(
            f"Completed {_format_value(display_timeout_seconds)} seconds of polling "
            f"({successful_samples} successful monitor snapshots)."
        )
        print_server_status_snapshot(
            highest_snapshot,
            iteration_label="Highest iteration observed",
        )
        return True

    while True:
        remaining = deadline - monotonic_fn()
        if remaining <= 0:
            if report_highest():
                return True
            print(
                "Timed out after "
                f"{_format_value(display_timeout_seconds)} seconds waiting for a live iteration and residuals: "
                f"{last_error}"
            )
            return False

        snapshot, error = _collect_snapshot_with_timeout(solver, remaining)
        if error is not None:
            last_error = f"{type(error).__name__}: {error}"
        elif snapshot is None:
            last_error = "no monitor snapshot was returned"
        elif _has_live_progress(snapshot):
            successful_samples += 1
            iteration = snapshot["progress"]["iteration"]
            if highest_snapshot is None or iteration > highest_snapshot["progress"]["iteration"]:
                highest_snapshot = snapshot
        else:
            residual = snapshot["monitors"].get("residual", {})
            last_error = str(residual.get("error") or "iteration or residual values are unavailable")

        remaining = deadline - monotonic_fn()
        if remaining <= 0:
            if report_highest():
                return True
            print(
                "Timed out after "
                f"{_format_value(display_timeout_seconds)} seconds waiting for a live iteration and residuals: "
                f"{last_error}"
            )
            return False
        sleep_fn(min(poll_interval_seconds, remaining))


def print_configuration_state(solver: Any) -> None:
    """Print optional calculation and DPM settings without changing Fluent state."""
    print("\nCalculation and DPM configuration (read-only):")

    try:
        run_calculation = solver.settings.solution.run_calculation
    except Exception as exc:
        json_print("run_calculation", {"error": f"{type(exc).__name__}: {exc}"})
    else:
        try_value(
            "run_calculation_active_children",
            lambda: list(run_calculation.get_active_child_names()),
        )
        try_value(
            "run_calculation_state",
            lambda: safe_get_state(run_calculation, "run_calculation"),
        )

    try:
        dpm = solver.settings.setup.models.discrete_phase
    except Exception as exc:
        json_print("dpm", {"error": f"{type(exc).__name__}: {exc}"})
        return

    try_value("dpm_tracking_state", lambda: safe_get_state(dpm.tracking, "dpm.tracking"))
    try_value(
        "dpm_interaction_state",
        lambda: safe_get_state(dpm.general_settings.interaction, "dpm.interaction"),
    )
    try_value(
        "dpm_general_settings",
        lambda: safe_get_state(dpm.general_settings, "dpm.general_settings"),
    )


def main() -> int:
    parser = build_parser()
    parser.add_argument(
        "--status-timeout-seconds",
        type=float,
        default=60.0,
        help="Maximum time to wait for a live iteration and residuals. Default: 60.",
    )
    parser.add_argument(
        "--status-poll-interval-seconds",
        type=float,
        default=1.0,
        help="Seconds between status retries while waiting. Default: 1.",
    )
    parser.add_argument(
        "--endpoint-probe-timeout-seconds",
        type=float,
        default=3.0,
        help="TCP reachability-probe timeout before the Fluent connection. Default: 3.",
    )
    parser.add_argument(
        "--include-configuration-state",
        action="store_true",
        help=(
            "After live progress is found, also read detailed run-calculation and "
            "DPM settings. This can take longer on a busy Fluent session."
        ),
    )
    args = parser.parse_args()
    if args.status_timeout_seconds <= 0:
        parser.error("--status-timeout-seconds must be greater than zero")
    if args.status_poll_interval_seconds <= 0:
        parser.error("--status-poll-interval-seconds must be greater than zero")
    if args.endpoint_probe_timeout_seconds <= 0:
        parser.error("--endpoint-probe-timeout-seconds must be greater than zero")
    server_id = _normalize_server_id(str(args.server_id))
    suppress_repeated_insecure_transport_warnings()
    print(f"Using Fluent server id: {server_id}")
    endpoint_reachability = print_endpoint_reachability(
        server_id,
        timeout_seconds=args.endpoint_probe_timeout_seconds,
    )
    solver, connection_error = _call_with_timeout(
        lambda: connect(server_id=server_id),
        args.status_timeout_seconds,
    )
    if connection_error is not None:
        if endpoint_reachability == "reachable":
            print(
                "Server reachability verdict: REACHABLE — the configured TCP endpoint accepted "
                "a connection, but the PyFluent/gRPC handoff did not complete."
            )
        elif endpoint_reachability in {"unreachable", "timed_out"}:
            print(
                "Server reachability verdict: NOT REACHABLE — resolve the network, host, "
                "firewall, or configured port before diagnosing the Fluent handoff."
            )
        else:
            print(
                "Server reachability verdict: UNKNOWN — a direct IP/port probe was not available "
                "for this endpoint configuration."
            )
        print(
            "Timed out or failed after "
            f"{_format_value(args.status_timeout_seconds)} seconds while connecting to Fluent: "
            f"{type(connection_error).__name__}: {connection_error}"
        )
        return 2

    print("\nConnected to Fluent.")
    print("\nPolling for up to " f"{_format_value(args.status_timeout_seconds)} seconds for live server status (read-only)...")
    status_received = wait_for_live_server_status(
        solver,
        timeout_seconds=args.status_timeout_seconds,
        poll_interval_seconds=args.status_poll_interval_seconds,
    )
    if not status_received:
        print("\nDone. No solver or DPM commands were run, and Fluent was not closed.")
        return 2

    if args.include_configuration_state:
        print_configuration_state(solver)

    print("\nDone. This script did not run solver or DPM commands, and did not close Fluent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
