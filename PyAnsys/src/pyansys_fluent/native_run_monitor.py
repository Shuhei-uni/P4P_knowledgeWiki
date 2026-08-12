#!/usr/bin/env python3
"""Read-only monitoring and reconnection support for a Fluent-native run.

The monitor deliberately does not initialize, iterate, save, reload, interrupt,
or shut down Fluent.  It may be stopped and restarted independently of the
solver; the local state file lets a fresh monitor process compare progress with
the last observation it recorded before a connection loss.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import time
from typing import Any

from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.connection import connect


class MonitorConnectionLost(RuntimeError):
    """Raised when a snapshot cannot perform any live Fluent probe."""


@dataclass(frozen=True)
class CheckpointPair:
    """A case/data pair that can be checked without loading it."""

    case_path: str
    data_path: str


@dataclass(frozen=True)
class MonitorConfig:
    """Runtime policy for a read-only reconnecting monitor."""

    server_id: str = "1"
    poll_interval_seconds: float = 30.0
    reconnect_initial_delay_seconds: float = 2.0
    reconnect_max_delay_seconds: float = 60.0
    max_reconnect_attempts: int = 0
    duration_seconds: float = 0.0
    once: bool = False
    monitor_sets: tuple[str, ...] = ("residual",)
    checkpoint_pairs: tuple[CheckpointPair, ...] = ()
    state_json: Path | None = None
    events_jsonl: Path | None = None
    run_label: str = ""

    def validate(self) -> None:
        if self.poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be greater than zero")
        if self.reconnect_initial_delay_seconds <= 0:
            raise ValueError("reconnect_initial_delay_seconds must be greater than zero")
        if self.reconnect_max_delay_seconds < self.reconnect_initial_delay_seconds:
            raise ValueError("reconnect_max_delay_seconds must not be below the initial delay")
        if self.max_reconnect_attempts < 0:
            raise ValueError("max_reconnect_attempts must be zero or greater")
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds must be zero or greater")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _json_safe(value: Any) -> Any:
    """Convert PyFluent/numpy-like values into bounded JSON-safe values."""
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else value
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        try:
            return _json_safe(tolist())
        except Exception:
            pass
    return str(value)


def _numeric(value: Any) -> int | float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    if number.is_integer():
        return int(number)
    return number


def _last_value(values: Any) -> Any:
    safe_values = _json_safe(values)
    if isinstance(safe_values, list) and safe_values:
        return safe_values[-1]
    return None


def _highest_monitor_point(values: Any) -> tuple[int | float | None, int | None]:
    """Return the greatest numeric monitor coordinate and its aligned index.

    A newly attached Fluent client can receive monitor-history points out of
    chronological order, so the final array element is not necessarily the
    newest completed iteration.
    """
    safe_values = _json_safe(values)
    if not isinstance(safe_values, list):
        return None, None
    candidates = [
        (numeric, index)
        for index, value in enumerate(safe_values)
        if (numeric := _numeric(value)) is not None
    ]
    if not candidates:
        return None, None
    return max(candidates, key=lambda item: (item[0], item[1]))


def _value_at_index(values: Any, index: int | None) -> Any:
    safe_values = _json_safe(values)
    if index is None or not isinstance(safe_values, list) or index >= len(safe_values):
        return None
    return safe_values[index]


def _call_or_value(value: Any) -> Any:
    return value() if callable(value) else value


def _read_health(solver: Any, errors: list[str]) -> tuple[dict[str, Any], bool]:
    health: dict[str, Any] = {}
    health_obj = getattr(solver, "health_check", None)
    if health_obj is None:
        errors.append("health_check is unavailable")
        return health, False

    probe_succeeded = False
    for name in ("status", "check_health"):
        try:
            health[name] = _json_safe(_call_or_value(getattr(health_obj, name)))
            probe_succeeded = True
        except Exception as exc:
            errors.append(f"health_check.{name}: {type(exc).__name__}: {exc}")
    return health, probe_succeeded


def _read_scheme_variable(solver: Any, variable: str) -> Any:
    """Read a Fluent RP variable, preferring the current (unbuffered) value."""
    last_error: Exception | None = None
    for expression in (f"(%rpgetvar '{variable})", f"(rpgetvar '{variable})"):
        try:
            return solver.scheme.eval(expression)
        except Exception as exc:
            last_error = exc
    if last_error is None:
        raise RuntimeError(f"Could not read Fluent RP variable {variable}")
    raise last_error


def _read_runtime(solver: Any, errors: list[str]) -> tuple[dict[str, Any], bool]:
    runtime: dict[str, Any] = {}
    probe_succeeded = False
    variables = (
        # Fluent exposes this RP variable as the configured maximum for the
        # run-calculation control, not as the number of iterations already
        # completed.  Keep it for context, but do not use it as live progress.
        ("configured_number_of_iterations", "number-of-iterations"),
        ("flow_time", "flow-time"),
        ("time_step", "time-step"),
        ("physical_time_step", "physical-time-step"),
    )
    for result_name, variable in variables:
        try:
            runtime[result_name] = _numeric(_read_scheme_variable(solver, variable))
            probe_succeeded = True
        except Exception as exc:
            errors.append(f"rpgetvar {variable}: {type(exc).__name__}: {exc}")
    return runtime, probe_succeeded


def _read_monitors(
    solver: Any,
    monitor_sets: Sequence[str],
    errors: list[str],
) -> tuple[dict[str, Any], bool]:
    monitors: dict[str, Any] = {}
    manager = getattr(solver, "monitors", None)
    if manager is None:
        errors.append("monitor streaming manager is unavailable")
        return monitors, False

    names: list[str] | None = None
    names_probe_succeeded = False
    try:
        names = [str(name) for name in manager.get_monitor_set_names()]
        names_probe_succeeded = True
    except Exception as exc:
        errors.append(f"monitors.get_monitor_set_names: {type(exc).__name__}: {exc}")

    probe_succeeded = names_probe_succeeded
    for monitor_set in monitor_sets:
        item: dict[str, Any] = {"name": monitor_set, "available": False}
        if names is not None and monitor_set not in names:
            item["error"] = "monitor set is not exposed by Fluent"
            monitors[monitor_set] = item
            continue
        try:
            x_values, series = manager.get_monitor_set_data(monitor_set_name=monitor_set)
            x_values_safe = _json_safe(x_values)
            series_safe = _json_safe(series)
            highest_iteration, highest_index = _highest_monitor_point(x_values_safe)
            item.update(
                {
                    "available": True,
                    "point_count": len(x_values_safe) if isinstance(x_values_safe, list) else 0,
                    # Retain this established field name for consumers, but
                    # calculate it from the greatest coordinate rather than
                    # the last response element. See _highest_monitor_point.
                    "latest_iteration": highest_iteration,
                    "highest_iteration": highest_iteration,
                    "last_values": {
                        str(name): _numeric(_value_at_index(values, highest_index))
                        for name, values in series_safe.items()
                    }
                    if isinstance(series_safe, Mapping)
                    else {},
                }
            )
            probe_succeeded = True
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
            errors.append(f"monitor {monitor_set}: {item['error']}")
        monitors[monitor_set] = item
    return monitors, probe_succeeded


def _read_checkpoint_pairs(
    solver: Any,
    pairs: Sequence[CheckpointPair],
    errors: list[str],
) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    for pair in pairs:
        item: dict[str, Any] = {
            "case_path": pair.case_path,
            "data_path": pair.data_path,
        }
        try:
            item["case_exists"] = bool(remote_file_exists(solver, pair.case_path))
            item["data_exists"] = bool(remote_file_exists(solver, pair.data_path))
            if item["case_exists"] and item["data_exists"]:
                item["status"] = "complete"
            elif item["case_exists"] or item["data_exists"]:
                item["status"] = "partial"
            else:
                item["status"] = "missing"
        except Exception as exc:
            item["status"] = "unknown"
            item["error"] = f"{type(exc).__name__}: {exc}"
            errors.append(f"checkpoint {pair.case_path}: {item['error']}")
        checkpoints.append(item)
    return checkpoints


def _previous_iteration(previous_state: Mapping[str, Any] | None) -> int | float | None:
    if not isinstance(previous_state, Mapping):
        return None
    progress = previous_state.get("progress", {})
    if not isinstance(progress, Mapping):
        return None
    return _numeric(progress.get("iteration"))


def _latest_monitor_iteration(monitors: Mapping[str, Any]) -> int | float | None:
    """Return the newest iteration coordinate exposed by any monitor set."""
    for item in monitors.values():
        if not isinstance(item, Mapping):
            continue
        latest = _numeric(item.get("latest_iteration"))
        if latest is not None:
            return latest
    return None


def collect_snapshot(
    solver: Any,
    *,
    previous_state: Mapping[str, Any] | None = None,
    monitor_sets: Sequence[str] = ("residual",),
    checkpoint_pairs: Sequence[CheckpointPair] = (),
    connection_generation: int = 1,
    run_label: str = "",
) -> dict[str, Any]:
    """Collect one read-only live snapshot from an existing Fluent session."""
    errors: list[str] = []
    health, health_ok = _read_health(solver, errors)

    version: str | None = None
    try:
        version = str(solver.get_fluent_version())
        version_ok = True
    except Exception as exc:
        version_ok = False
        errors.append(f"get_fluent_version: {type(exc).__name__}: {exc}")

    runtime, runtime_ok = _read_runtime(solver, errors)
    monitors, monitors_ok = _read_monitors(solver, monitor_sets, errors)
    checkpoints = _read_checkpoint_pairs(solver, checkpoint_pairs, errors)

    if not (health_ok or version_ok or runtime_ok or monitors_ok):
        detail = errors[0] if errors else "all live probes failed"
        raise MonitorConnectionLost(detail)

    # Prefer monitor history: the RP value above is the configured maximum,
    # while monitor x-values are the live flow-iteration coordinates.  If no
    # monitor set is available, report progress as unknown rather than turning
    # a maximum setting into a false completed-iteration count.
    iteration = _latest_monitor_iteration(monitors)

    previous_iteration = _previous_iteration(previous_state)
    if iteration is None or previous_iteration is None:
        progress_state = "first_observation" if iteration is not None else "unknown"
    elif iteration > previous_iteration:
        progress_state = "advancing"
    elif iteration == previous_iteration:
        progress_state = "not_advancing"
    else:
        progress_state = "went_backwards_or_reloaded"

    return {
        "timestamp_utc": utc_timestamp(),
        "run_label": run_label or None,
        "connection_generation": connection_generation,
        "fluent_version": version,
        "health": health,
        "runtime": runtime,
        "progress": {
            "iteration": iteration,
            "previous_iteration": previous_iteration,
            "delta": iteration - previous_iteration
            if iteration is not None and previous_iteration is not None
            else None,
            "state": progress_state,
            "source": "monitor_x_value" if iteration is not None else "unavailable",
        },
        "monitors": monitors,
        "checkpoints": checkpoints,
        "read_errors": errors,
        "read_only": True,
    }


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, default=str) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_previous_state(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return dict(value) if isinstance(value, Mapping) else None
    except Exception:
        return None


def _delay_for_failure(config: MonitorConfig, failure_number: int) -> float:
    exponent = max(0, failure_number - 1)
    return min(
        config.reconnect_max_delay_seconds,
        config.reconnect_initial_delay_seconds * (2**exponent),
    )


def run_monitor(
    config: MonitorConfig,
    *,
    connect_fn: Callable[[str], Any] = connect,
    sleep_fn: Callable[[float], None] = time.sleep,
    monotonic_fn: Callable[[], float] = time.monotonic,
    emit_fn: Callable[[Mapping[str, Any]], None] | None = None,
) -> int:
    """Run the reconnecting monitor until duration, ``once``, or Ctrl-C.

    Return codes are ``0`` for a normal stop, ``2`` when the configured retry
    limit is exhausted, and ``130`` for Ctrl-C.  A failed connection is never
    treated as evidence that Fluent stopped; the next attempt is explicitly
    reported so the operator can distinguish an unreachable client from a
    solver-side failure.
    """
    config.validate()
    emit = emit_fn or (lambda _event: None)
    previous_state = load_previous_state(config.state_json)
    started_at = monotonic_fn()
    deadline = started_at + config.duration_seconds if config.duration_seconds else None
    solver: Any | None = None
    connection_generation = 0
    failure_number = 0

    def within_deadline() -> bool:
        return deadline is None or monotonic_fn() < deadline

    def wait_for(seconds: float) -> bool:
        if not within_deadline():
            return False
        if deadline is not None:
            seconds = min(seconds, max(0.0, deadline - monotonic_fn()))
        if seconds > 0:
            sleep_fn(seconds)
        return within_deadline()

    def record(event: Mapping[str, Any]) -> None:
        payload = {"timestamp_utc": utc_timestamp(), **dict(event)}
        try:
            if config.events_jsonl is not None:
                _append_jsonl(config.events_jsonl, payload)
        except Exception as exc:
            payload = {
                **payload,
                "persistence_warning": f"events_jsonl: {type(exc).__name__}: {exc}",
            }
        emit(payload)

    try:
        while within_deadline():
            if solver is None:
                failure_number += 1
                try:
                    solver = connect_fn(config.server_id)
                    connection_generation += 1
                    failure_number = 0
                    record(
                        {
                            "event": "connected",
                            "connection_generation": connection_generation,
                            "server_id": config.server_id,
                            "case_identity": "not_inferred_from_server_id",
                        }
                    )
                except Exception as exc:
                    solver = None
                    record(
                        {
                            "event": "reconnect_failed",
                            "server_id": config.server_id,
                            "failure_number": failure_number,
                            "error": f"{type(exc).__name__}: {exc}",
                            "next_delay_seconds": _delay_for_failure(config, failure_number),
                        }
                    )
                    if (
                        config.max_reconnect_attempts
                        and failure_number >= config.max_reconnect_attempts
                    ):
                        record(
                            {
                                "event": "retry_limit_exhausted",
                                "max_reconnect_attempts": config.max_reconnect_attempts,
                            }
                        )
                        return 2
                    if not wait_for(_delay_for_failure(config, failure_number)):
                        break
                    continue

            try:
                snapshot = collect_snapshot(
                    solver,
                    previous_state=previous_state,
                    monitor_sets=config.monitor_sets,
                    checkpoint_pairs=config.checkpoint_pairs,
                    connection_generation=connection_generation,
                    run_label=config.run_label,
                )
                previous_state = snapshot
                if config.state_json is not None:
                    try:
                        _atomic_write_json(config.state_json, snapshot)
                    except Exception as exc:
                        snapshot = {
                            **snapshot,
                            "persistence_warning": f"state_json: {type(exc).__name__}: {exc}",
                        }
                record({"event": "snapshot", "snapshot": snapshot})
                if config.once:
                    return 0
                if not wait_for(config.poll_interval_seconds):
                    break
            except MonitorConnectionLost as exc:
                record(
                    {
                        "event": "connection_lost",
                        "connection_generation": connection_generation,
                        "error": str(exc),
                        "action": "drop_client_reference_and_reconnect_without_shutdown",
                    }
                )
                # Do not call solver.exit() or solver.force_exit(): they are
                # shutdown operations, not a safe way to detach a monitor.
                solver = None
                if not wait_for(_delay_for_failure(config, max(1, failure_number + 1))):
                    break
            except Exception as exc:
                record(
                    {
                        "event": "monitor_error",
                        "connection_generation": connection_generation,
                        "error": f"{type(exc).__name__}: {exc}",
                        "action": "drop_client_reference_and_reconnect",
                    }
                )
                solver = None
                if not wait_for(_delay_for_failure(config, max(1, failure_number + 1))):
                    break
    except KeyboardInterrupt:
        record({"event": "stopped_by_operator", "action": "client_stopped_without_solver_shutdown"})
        return 130

    record({"event": "monitor_finished", "reason": "duration_elapsed_or_deadline_reached"})
    return 0
