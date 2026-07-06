#!/usr/bin/env python3
"""Shared helpers for read-mostly Fluent extraction workflows."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from pathlib import PureWindowsPath
from typing import Any

from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.dependency_workflow import (
    safe_allowed_values,
    safe_child_names,
    safe_command_names,
)


def safe_json(value: Any) -> Any:
    """Convert PyFluent states and Python objects into JSON-safe values."""
    if isinstance(value, Mapping):
        return {str(key): safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [safe_json(item) for item in value]
    if isinstance(value, Path | PureWindowsPath):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    try:
        return value.item()
    except Exception:
        return str(value)


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(safe_json(payload), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def note_failure(notes: list[str], label: str, exc: Exception) -> None:
    notes.append(f"{label}: unavailable ({type(exc).__name__}: {exc})")


def try_call(
    label: str,
    func: Callable[[], Any],
    notes: list[str],
    *,
    default: Any = None,
) -> Any:
    try:
        return safe_json(func())
    except Exception as exc:
        note_failure(notes, label, exc)
        return default


def probe_meta(obj: Any, label: str, notes: list[str]) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "label": label,
        "type": type(obj).__name__,
        "module": type(obj).__module__,
        "child_names": safe_child_names(obj),
        "command_names": safe_command_names(obj),
        "allowed_values": safe_allowed_values(obj),
    }

    for attr_name, key in (
        ("is_active", "is_active"),
        ("min", "min"),
        ("max", "max"),
        ("python_name", "python_name"),
    ):
        try:
            value = getattr(obj, attr_name)
            meta[key] = safe_json(value() if callable(value) else value)
        except Exception:
            continue

    return meta


def summarize_state(state: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {"state_type": type(state).__name__}
    if isinstance(state, Mapping):
        summary["mapping_keys"] = sorted(str(key) for key in state.keys())
        summary["mapping_size"] = len(state)
    elif isinstance(state, list):
        summary["list_size"] = len(state)
    elif isinstance(state, str):
        summary["string_length"] = len(state)
    return summary


def capture_object_tree(
    obj: Any,
    label: str,
    notes: list[str],
    *,
    max_depth: int,
    include_state: bool = True,
    depth: int = 0,
    seen: set[int] | None = None,
) -> dict[str, Any]:
    """Recursively capture reachable PyFluent settings objects."""
    if seen is None:
        seen = set()

    object_id = id(obj)
    if object_id in seen:
        return {"_meta": {"label": label, "cycle_detected": True}}
    seen.add(object_id)

    snapshot: dict[str, Any] = {"_meta": probe_meta(obj, label, notes)}

    if not hasattr(obj, "get_state") or not hasattr(obj, "child_names"):
        snapshot["_non_settings_object"] = True
        snapshot["_truncated"] = True
        return snapshot

    if include_state:
        state = try_call(f"{label}.get_state", obj.get_state, notes, default=None)
        snapshot["_state"] = state
        snapshot["_state_summary"] = summarize_state(state)

    if depth >= max_depth:
        snapshot["_truncated"] = True
        return snapshot

    child_names = snapshot["_meta"].get("child_names", [])
    for child_name in child_names:
        if not child_name or str(child_name).startswith("_"):
            continue
        child_label = f"{label}.{child_name}"
        try:
            child_obj = getattr(obj, str(child_name))
        except Exception as exc:
            note_failure(notes, child_label, exc)
            continue
        snapshot[str(child_name)] = capture_object_tree(
            child_obj,
            child_label,
            notes,
            max_depth=max_depth,
            include_state=include_state,
            depth=depth + 1,
            seen=seen,
        )

    return snapshot


def resolve_path(root: Any, path_parts: Iterable[str]) -> Any:
    obj = root
    for part in path_parts:
        obj = getattr(obj, part)
    return obj


def capture_candidate_paths(
    root: Any,
    notes: list[str],
    path_specs: list[dict[str, Any]],
) -> dict[str, Any]:
    captures: dict[str, Any] = {}
    for spec in path_specs:
        label = spec["label"]
        path_options: list[list[str]] = spec["paths"]
        max_depth = spec.get("max_depth", 3)
        include_state = spec.get("include_state", True)

        resolved_obj = None
        resolved_path: list[str] | None = None
        errors: list[str] = []
        for path_parts in path_options:
            try:
                resolved_obj = resolve_path(root, path_parts)
                resolved_path = path_parts
                break
            except Exception as exc:
                errors.append(f"{'.'.join(path_parts)} -> {type(exc).__name__}: {exc}")

        if resolved_obj is None:
            notes.append(
                f"{label}: unresolved candidate paths ({'; '.join(errors)})"
            )
            captures[label] = {
                "_meta": {
                    "label": label,
                    "resolved": False,
                    "candidate_paths": [".".join(parts) for parts in path_options],
                }
            }
            continue

        branch_label = ".".join(resolved_path)
        branch_snapshot = capture_object_tree(
            resolved_obj,
            branch_label,
            notes,
            max_depth=max_depth,
            include_state=include_state,
        )
        branch_snapshot["_meta"]["resolved"] = True
        branch_snapshot["_meta"]["resolved_path"] = branch_label
        captures[label] = branch_snapshot

    return captures


def remote_file_exists(solver: Any, path_text: str) -> bool:
    quoted = quote_scheme_string(path_text)
    return bool(solver.scheme.eval(f'(file-exists? "{quoted}")'))


def load_remote_case_data(
    solver: Any,
    case_path: str,
    data_path: str | None,
    notes: list[str],
) -> None:
    if not remote_file_exists(solver, case_path):
        raise FileNotFoundError(f"Fluent cannot see case file: {case_path}")
    if data_path and not remote_file_exists(solver, data_path):
        raise FileNotFoundError(f"Fluent cannot see data file: {data_path}")

    case_name = PureWindowsPath(case_path).name
    case_dir = str(PureWindowsPath(case_path).parent)
    solver.scheme.eval(f'(chdir "{quote_scheme_string(case_dir)}")')

    if data_path:
        expected_data_name = case_name.removesuffix(".cas.h5") + ".dat.h5"
        actual_data_name = PureWindowsPath(data_path).name
        if actual_data_name == expected_data_name:
            solver.settings.file.read_case_data(file_name=case_path)
        else:
            notes.append(
                "Data filename does not match Fluent default pairing; loading case then explicit data."
            )
            solver.settings.file.read_case(file_name=case_path)
            solver.settings.file.read_data(file_name=data_path)
    else:
        solver.settings.file.read_case(file_name=case_path)


def collect_scheme_snapshot(
    solver: Any,
    notes: list[str],
    expressions: Mapping[str, str],
) -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    for key, expression in expressions.items():
        snapshot[key] = try_call(
            f"scheme {expression}",
            lambda expr=expression: solver.scheme.eval(expr),
            notes,
            default=None,
        )
    return snapshot
