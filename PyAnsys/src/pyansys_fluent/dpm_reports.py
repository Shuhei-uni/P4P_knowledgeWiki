#!/usr/bin/env python3
"""Reusable Fluent DPM summary-report helpers.

The functions in this module are deliberately read-mostly.  They discover the
currently loaded DPM injections and invoke Fluent's legacy Particle Tracks
Summary workflow through literal TUI commands.  They do not change injection
physics, wall fates, or solver controls.
"""

from __future__ import annotations

import contextlib
import io
import math
import re
import time
from collections.abc import Mapping, Sequence
from typing import Any

from pyansys_fluent.common import quote_scheme_string

_COUNT_RE = re.compile(
    r"(?P<key>tracked|escaped|aborted|trapped|incomplete|evaporated|injected|inserted)"
    r"\s*=\s*(?P<value>[+-]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_EWF_EVENT_RE = re.compile(
    r"(?P<key>absorbed|splashed|stripped|separated|escaped|trapped)"
    r"\s*=\s*(?P<value>[+-]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
_MASS_ROW_RE = re.compile(
    rf"^\s*(?P<fate>[A-Za-z][A-Za-z -]*?)\s+"
    rf"(?:(?P<zone>[A-Za-z0-9_.-]+)\s+(?P<zone_id>\d+)\s+)?"
    rf"(?P<initial>{_NUMBER})\s+(?P<final>{_NUMBER})\s+(?P<change>{_NUMBER})\s*$"
)
_FATE_ROW_WITH_ZONE_RE = re.compile(
    rf"^\s*(?P<fate>[A-Za-z][A-Za-z -]*?)\s+"
    rf"(?P<zone>[A-Za-z0-9_.-]+)\s+(?P<zone_id>\d+)\s+"
    rf"(?P<count>\d+)\s+(?P<minimum>{_NUMBER})\s+(?P<maximum>{_NUMBER})\s+"
    rf"(?P<average>{_NUMBER})\s+(?P<std_dev>{_NUMBER})\s+.*$"
)
_FATE_ROW_NO_ZONE_RE = re.compile(
    rf"^\s*(?P<fate>[A-Za-z][A-Za-z -]*?)\s+"
    rf"(?P<count>\d+)\s+(?P<minimum>{_NUMBER})\s+(?P<maximum>{_NUMBER})\s+"
    rf"(?P<average>{_NUMBER})\s+(?P<std_dev>{_NUMBER})\s+.*$"
)
_KNOWN_FATES = {
    "aborted",
    "absorbed",
    "escaped",
    "evaporated",
    "incomplete",
    "injected",
    "inserted",
    "removed",
    "separated",
    "splashed",
    "stripped",
    "trapped",
}


def execute_tui(solver: Any, command: str) -> Any:
    """Execute a literal Fluent TUI command with a Scheme fallback."""
    framed = command if command.endswith("\n") else command + "\n"
    method = getattr(solver, "execute_tui", None)
    if method is not None:
        return method(framed)
    return solver.scheme.eval(
        f'(ti-menu-load-string "{quote_scheme_string(framed)}")'
    )


def _recursive_find_numeric(payload: Any, keys: set[str]) -> float | None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            normalized = str(key).lower().replace("_", "-")
            if normalized in keys:
                try:
                    result = float(value)
                    if math.isfinite(result):
                        return result
                except (TypeError, ValueError):
                    pass
        for value in payload.values():
            found = _recursive_find_numeric(value, keys)
            if found is not None:
                return found
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        for value in payload:
            found = _recursive_find_numeric(value, keys)
            if found is not None:
                return found
    return None


def _compact_state(obj: Any, label: str) -> Any:
    try:
        state = obj.get_state()
        return dict(state) if isinstance(state, Mapping) else state
    except Exception as exc:
        return {"_capture_error": f"{label}: {type(exc).__name__}: {exc}"}


def _diameter_um(injection: Any) -> float | None:
    try:
        state = injection.initial_values.particle_size.get_state()
    except Exception:
        state = None
    diameter = _recursive_find_numeric(
        state,
        {"diameter", "particle-diameter", "particle-size"},
    )
    if diameter is None:
        diameter = _recursive_find_numeric(
            _compact_state(injection, "injection"),
            {"diameter", "particle-diameter", "particle-size"},
        )
    if diameter is None:
        return None
    return diameter * 1.0e6 if abs(diameter) < 1.0 else diameter


def discover_live_injections(solver: Any) -> list[dict[str, Any]]:
    """Return the live DPM injection list with stable names and metadata."""
    try:
        branch = solver.settings.setup.models.discrete_phase.injections
    except Exception as exc:
        raise RuntimeError(
            "order/dependency issue: no active DPM injection branch is available"
        ) from exc

    try:
        names = [str(name) for name in branch.get_object_names()]
    except Exception as exc:
        raise RuntimeError(
            "path/version issue: Fluent did not expose DPM injection names"
        ) from exc

    discovered: list[dict[str, Any]] = []
    for index, name in enumerate(names):
        injection = branch[name]
        state = _compact_state(injection, f"injections.{name}")
        initial_values = state.get("initial_values", {}) if isinstance(state, Mapping) else {}
        location = initial_values.get("location", {}) if isinstance(initial_values, Mapping) else {}
        discovered.append(
            {
                "index": index,
                "name": name,
                "diameter_um": _diameter_um(injection),
                "particle_type": state.get("particle_type") if isinstance(state, Mapping) else None,
                "material": state.get("material") if isinstance(state, Mapping) else None,
                "injection_type": state.get("injection_type") if isinstance(state, Mapping) else None,
                "injection_surfaces": (
                    location.get("injection_surfaces") if isinstance(location, Mapping) else None
                ),
                "state": state,
            }
        )
    return discovered


def select_injections(
    discovered: Sequence[Mapping[str, Any]],
    *,
    requested_names: Sequence[str] | None = None,
    requested_indices: Sequence[int] | None = None,
    order: str = "diameter-ascending",
) -> list[dict[str, Any]]:
    by_name = {str(item["name"]): item for item in discovered}
    by_index = {int(item["index"]): item for item in discovered}

    if requested_names or requested_indices:
        selected: list[Mapping[str, Any]] = []
        seen: set[str] = set()
        for name in requested_names or []:
            if name not in by_name:
                raise RuntimeError(
                    f"requested injection {name!r} is not in the live list {list(by_name)}"
                )
            if name not in seen:
                selected.append(by_name[name])
                seen.add(name)
        for index in requested_indices or []:
            if index not in by_index:
                raise RuntimeError(
                    f"requested injection index {index} is outside 0..{len(discovered) - 1}"
                )
            name = str(by_index[index]["name"])
            if name not in seen:
                selected.append(by_index[index])
                seen.add(name)
    else:
        selected = list(discovered)

    def diameter_key(item: Mapping[str, Any]) -> tuple[bool, float, int]:
        diameter = item.get("diameter_um")
        return (diameter is None, float(diameter or 0.0), int(item["index"]))

    if order == "live":
        selected.sort(key=lambda item: int(item["index"]))
    elif order == "diameter-descending":
        selected.sort(key=diameter_key, reverse=True)
    else:
        selected.sort(key=diameter_key)
    return [dict(item) for item in selected]


def configure_particle_track_summary(solver: Any, *, tui_version: str = "24.2") -> list[str]:
    """Configure Summary-to-console tracking without displaying trajectories."""
    commands = [
        f'/file/set-tui-version "{tui_version}"',
        "/preferences/graphics/enable-non-object-based-workflow yes",
        "/display/set/particle-tracks/report-type summary",
        "/display/set/particle-tracks/report-to screen",
        "/display/set/particle-tracks/display? no",
        "/report/dpm-zone-summaries-per-injection? yes",
    ]
    for command in commands:
        execute_tui(solver, command)
    return commands


def build_track_command(injection_name: str) -> str:
    safe_name = injection_name.replace("\\", "\\\\").replace('"', '\\"')
    return (
        "/display/particle-tracks particle-tracks mixture particle-resid-time "
        f'"{safe_name}" () 0 0'
    )


def parse_summary_counts(raw_output: str) -> dict[str, int | None]:
    counts: dict[str, int | None] = {
        "tracked": None,
        "escaped": 0,
        "aborted": 0,
        "trapped": 0,
        "incomplete": 0,
        "evaporated": 0,
        "injected": 0,
        "inserted": 0,
    }
    iteration_match = re.search(r"DPM Iteration\s*\.{1,}\s*(.*?)(?:\n|$)", raw_output, re.IGNORECASE)
    source = iteration_match.group(1) if iteration_match else raw_output
    for match in _COUNT_RE.finditer(source):
        counts[match.group("key").lower()] = int(float(match.group("value")))
    return counts


def parse_ewf_event_counts(raw_output: str) -> dict[str, int]:
    match = re.search(
        r"Eulerian wall film particles:\s*(?P<body>[^\n]*(?:\n(?!\s*One of)[^\n]*)?)",
        raw_output,
        re.IGNORECASE,
    )
    if not match:
        return {}
    return {
        item.group("key").lower(): int(float(item.group("value")))
        for item in _EWF_EVENT_RE.finditer(match.group("body"))
    }


def parse_fate_rows(raw_output: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    before_mass = raw_output.split("Mass Transfer Summary", 1)[0]
    for raw_line in before_mass.splitlines():
        line = raw_line.rstrip()
        match = _FATE_ROW_WITH_ZONE_RE.match(line) or _FATE_ROW_NO_ZONE_RE.match(line)
        if not match:
            continue
        fate = match.group("fate").strip().lower()
        if fate not in _KNOWN_FATES:
            continue
        payload = match.groupdict()
        rows.append(
            {
                "fate": fate,
                "zone": payload.get("zone"),
                "zone_id": int(payload["zone_id"]) if payload.get("zone_id") else None,
                "count": int(payload["count"]),
                "elapsed_time_s": {
                    "min": float(payload["minimum"]),
                    "max": float(payload["maximum"]),
                    "avg": float(payload["average"]),
                    "std_dev": float(payload["std_dev"]),
                },
            }
        )
    return rows


def parse_mass_transfer_rows(raw_output: str) -> list[dict[str, Any]]:
    marker = "Mass Transfer Summary"
    if marker not in raw_output:
        return []
    section = raw_output.split(marker, 1)[1]
    rows: list[dict[str, Any]] = []
    for raw_line in section.splitlines():
        match = _MASS_ROW_RE.match(raw_line.rstrip())
        if not match:
            continue
        data = match.groupdict()
        fate = data["fate"].strip().lower()
        if fate not in _KNOWN_FATES | {"net"}:
            continue
        rows.append(
            {
                "fate": fate,
                "zone": data.get("zone"),
                "zone_id": int(data["zone_id"]) if data.get("zone_id") else None,
                "initial_kg_s": float(data["initial"]),
                "final_kg_s": float(data["final"]),
                "change_kg_s": float(data["change"]),
            }
        )
    return rows


def parse_particle_track_summary(raw_output: str) -> dict[str, Any]:
    return {
        "counts": parse_summary_counts(raw_output),
        "ewf_events": parse_ewf_event_counts(raw_output),
        "fate_rows": parse_fate_rows(raw_output),
        "mass_transfer_rows": parse_mass_transfer_rows(raw_output),
    }


def dpm_flow_closure(parsed: Mapping[str, Any]) -> dict[str, Any]:
    rows = list(parsed.get("mass_transfer_rows", []))
    net_rows = [row for row in rows if row.get("fate") == "net"]
    terminal = [row for row in rows if row.get("fate") != "net"]
    injected = float(net_rows[-1]["initial_kg_s"]) if net_rows else None
    terminal_sum = sum(float(row.get("initial_kg_s", 0.0)) for row in terminal)
    residual = injected - terminal_sum if injected is not None else None
    relative = residual / injected if injected not in (None, 0.0) else None
    return {
        "injected_kg_s": injected,
        "terminal_sum_kg_s": terminal_sum if terminal else None,
        "residual_kg_s": residual,
        "relative_residual": relative,
        "terms": terminal,
        "status": "computed" if injected is not None and terminal else "unavailable",
    }


def track_one_injection(
    solver: Any,
    item: Mapping[str, Any],
    *,
    settle_seconds: float = 0.5,
) -> dict[str, Any]:
    name = str(item["name"])
    command = build_track_command(name)
    buffer = io.StringIO()
    returned: Any = None
    error: str | None = None
    try:
        with contextlib.redirect_stdout(buffer):
            returned = execute_tui(solver, command)
            time.sleep(settle_seconds)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    raw_output = buffer.getvalue()
    parsed = parse_particle_track_summary(raw_output)
    status = "ok" if parsed["counts"].get("tracked") is not None and error is None else "failed"
    return {
        "index": int(item["index"]),
        "name": name,
        "diameter_um": item.get("diameter_um"),
        "status": status,
        "error": error,
        "command": command,
        "returned": repr(returned),
        "raw_output": raw_output,
        "parsed": parsed,
        "closure": dpm_flow_closure(parsed),
    }
