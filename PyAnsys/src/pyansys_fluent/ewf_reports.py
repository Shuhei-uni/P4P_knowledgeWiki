#!/usr/bin/env python3
"""Namespaced EWF surface report creation and final-state computation."""

from __future__ import annotations

import contextlib
import io
import re
import time
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from pyansys_fluent.dependency_workflow import safe_child_names, safe_object_names
from pyansys_fluent.ewf_core import (
    child_by_alias,
    normalize_token,
    resolve_allowed_value,
    safe_float,
    set_child,
    set_leaf,
)
from pyansys_fluent.ewf_report_specs import REPORT_SPECS, ReportSpec
from pyansys_fluent.extraction import safe_json

_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
_REPORT_VALUE_RE = re.compile(
    rf"^\s*(?P<name>[A-Za-z0-9_.-]+)\s+(?P<value>{_NUMBER})(?:\s+\[(?P<unit>[^\]]+)\])?\s*$"
)


def _surface_report_branch(solver: Any) -> tuple[Any, Any]:
    root = solver.settings.solution.report_definitions
    surface, _ = child_by_alias(root, ("surface",))
    if surface is None:
        raise AttributeError("solution.report_definitions.surface is unavailable")
    return root, surface


def _named_object_names(branch: Any) -> list[str]:
    names = safe_object_names(branch)
    if names:
        return [str(name) for name in names]
    list_method = getattr(branch, "list", None)
    if callable(list_method):
        try:
            return [str(name) for name in list_method()]
        except Exception:
            pass
    return []


def _delete_named_object(branch: Any, name: str) -> None:
    delete = getattr(branch, "delete", None)
    if callable(delete):
        for kwargs in ({"names": [name]}, {"name": name}, {}):
            try:
                if kwargs:
                    delete(**kwargs)
                else:
                    delete(name)
                return
            except Exception:
                continue
    try:
        del branch[name]
        return
    except Exception as exc:
        raise RuntimeError(f"Could not delete existing report definition {name}") from exc


def _create_named_object(branch: Any, name: str) -> Any:
    try:
        branch[name] = {}
        return branch[name]
    except Exception:
        pass
    create = getattr(branch, "create", None)
    if callable(create):
        created = create(name=name)
        return created if created is not None else branch[name]
    raise RuntimeError(f"Could not create report definition {name}")


def _configure_report_object(
    report: Any,
    spec: ReportSpec,
    surfaces: Sequence[str],
    *,
    create_history_file: bool,
    frequency: int,
    reacquire: Callable[[], Any],
) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []

    report_type_leaf, report_type_name = child_by_alias(report, ("report_type", "report-type"))
    if report_type_leaf is None:
        raise AttributeError("Report object has no report_type child")
    report_type, report_type_resolution = resolve_allowed_value(
        report_type_leaf,
        spec.report_type_candidates,
        spec.report_type_tokens,
    )
    set_leaf(report_type_leaf, report_type)
    actions.append(
        {
            "child": report_type_name,
            "requested": report_type,
            "resolution": report_type_resolution,
            "status": "set",
        }
    )

    # Report type changes can rebuild dependent children in Fluent.
    report = reacquire()

    field_leaf, field_name = child_by_alias(report, ("field", "report_of", "report-of"))
    if field_leaf is None:
        raise AttributeError("Report object has no field child")
    field_value, field_resolution = resolve_allowed_value(
        field_leaf,
        spec.field_candidates,
        spec.field_tokens,
    )
    set_leaf(field_leaf, field_value)
    actions.append(
        {
            "child": field_name,
            "requested": field_value,
            "resolution": field_resolution,
            "status": "set",
        }
    )

    set_child(report, ("surface_names", "surfaces_list", "surfaces"), list(surfaces), required=True, actions=actions)
    set_child(report, ("per_surface", "per_zone"), False, required=False, actions=actions)
    set_child(report, ("average_over",), 1, required=False, actions=actions)
    set_child(report, ("frequency",), int(frequency), required=False, actions=actions)
    set_child(report, ("print_to_console", "print"), True, required=False, actions=actions)
    set_child(report, ("create_report_file",), bool(create_history_file), required=False, actions=actions)
    set_child(report, ("create_report_plot",), False, required=False, actions=actions)
    set_child(report, ("current_domain", "domain", "phase"), "mixture", required=False, actions=actions)
    return {
        "report_type": report_type,
        "field": field_value,
        "actions": actions,
        "state": safe_json(report.get_state()) if hasattr(report, "get_state") else None,
    }


def ensure_surface_report(
    solver: Any,
    spec: ReportSpec,
    *,
    prefix: str,
    surfaces: Sequence[str],
    object_policy: str,
    create_history_file: bool,
    frequency: int,
) -> dict[str, Any]:
    if not prefix or normalize_token(prefix) == "":
        raise ValueError("A non-empty report prefix is required")
    name = f"{prefix}-{spec.suffix}"
    root, surface_branch = _surface_report_branch(solver)
    existing = _named_object_names(surface_branch)
    created = False

    if name in existing:
        if object_policy == "fail":
            raise RuntimeError(f"Diagnostic report already exists: {name}")
        if object_policy == "replace":
            _delete_named_object(surface_branch, name)
            _create_named_object(surface_branch, name)
            created = True
    else:
        _create_named_object(surface_branch, name)
        created = True

    report = surface_branch[name]
    configured = _configure_report_object(
        report,
        spec,
        surfaces,
        create_history_file=create_history_file,
        frequency=frequency,
        reacquire=lambda: surface_branch[name],
    )
    return {
        "key": spec.key,
        "name": name,
        "created": created,
        "object_policy": object_policy,
        "surfaces": list(surfaces),
        "expected_dimension": spec.expected_dimension,
        "optional_mechanism": spec.optional_mechanism,
        "configuration": configured,
        "report_root_children": safe_child_names(root),
    }


def parse_report_compute_output(raw_output: str, report_name: str) -> dict[str, Any]:
    target = normalize_token(report_name)
    candidates: list[dict[str, Any]] = []
    for raw_line in raw_output.splitlines():
        match = _REPORT_VALUE_RE.match(raw_line.rstrip())
        if not match:
            continue
        item = {
            "name": match.group("name"),
            "value": float(match.group("value")),
            "unit": match.group("unit"),
        }
        candidates.append(item)
        if normalize_token(item["name"]) == target:
            return item
    return candidates[-1] if candidates else {"name": report_name, "value": None, "unit": None}


def compute_report_definition(
    solver: Any,
    report_name: str,
    *,
    settle_seconds: float = 0.5,
) -> dict[str, Any]:
    report_root = solver.settings.solution.report_definitions
    buffer = io.StringIO()
    returned: Any = None
    attempts: list[dict[str, Any]] = []

    def try_compute(label: str, func: Callable[[], Any]) -> bool:
        nonlocal returned
        try:
            with contextlib.redirect_stdout(buffer):
                returned = func()
                time.sleep(settle_seconds)
            attempts.append({"method": label, "status": "ok"})
            return True
        except Exception as exc:
            attempts.append({"method": label, "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
            return False

    compute = getattr(report_root, "compute", None)
    ok = False
    if callable(compute):
        ok = try_compute("settings.compute(report_defs=...)", lambda: compute(report_defs=[report_name]))
        if not ok:
            ok = try_compute("settings.compute(report_definitions=...)", lambda: compute(report_definitions=[report_name]))
    if not ok:
        method = getattr(solver, "execute_tui", None)
        if method is not None:
            for command in (
                f'/solve/report-definitions/compute "{report_name}"',
                f'/solution/report-definitions/compute "{report_name}"',
            ):
                if try_compute(f"execute_tui:{command}", lambda cmd=command: method(cmd + "\n")):
                    ok = True
                    break

    raw_output = buffer.getvalue()
    parsed = parse_report_compute_output(raw_output, report_name)
    returned_value = None
    if isinstance(returned, Mapping):
        for key, value in returned.items():
            if normalize_token(key) == normalize_token(report_name):
                returned_value = safe_float(value)
                break
    elif isinstance(returned, (int, float)):
        returned_value = safe_float(returned)
    if parsed.get("value") is None and returned_value is not None:
        parsed["value"] = returned_value

    return {
        "status": "ok" if ok and parsed.get("value") is not None else "unparsed",
        "attempts": attempts,
        "returned": safe_json(returned),
        "raw_output": raw_output,
        "parsed": parsed,
    }


def create_and_compute_snapshot(
    solver: Any,
    *,
    surfaces: Sequence[str],
    prefix: str = "ewfdiag",
    object_policy: str = "reuse",
    create_history_files: bool = False,
    frequency: int = 1,
    mechanisms: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    mechanisms = mechanisms or {}
    reports: list[dict[str, Any]] = []
    warnings: list[str] = []

    for spec in REPORT_SPECS:
        if spec.optional_mechanism and mechanisms.get(spec.optional_mechanism) is not True:
            reports.append(
                {
                    "key": spec.key,
                    "name": f"{prefix}-{spec.suffix}",
                    "status": "inactive-mechanism",
                    "optional_mechanism": spec.optional_mechanism,
                    "mechanism_state": mechanisms.get(spec.optional_mechanism),
                }
            )
            continue
        try:
            definition = ensure_surface_report(
                solver,
                spec,
                prefix=prefix,
                surfaces=surfaces,
                object_policy=object_policy,
                create_history_file=create_history_files,
                frequency=frequency,
            )
            result = compute_report_definition(solver, definition["name"])
            reports.append({**definition, "status": result["status"], "compute": result})
        except Exception as exc:
            reports.append(
                {
                    "key": spec.key,
                    "name": f"{prefix}-{spec.suffix}",
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                    "surfaces": list(surfaces),
                }
            )
            warnings.append(f"{spec.key} failed: {type(exc).__name__}: {exc}")
    return {"reports": reports, "warnings": warnings}


def flatten_snapshot_reports(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for report in snapshot.get("reports", []):
        compute = report.get("compute", {}) if isinstance(report, Mapping) else {}
        parsed = compute.get("parsed", {}) if isinstance(compute, Mapping) else {}
        rows.append(
            {
                "key": report.get("key"),
                "name": report.get("name"),
                "status": report.get("status"),
                "value": parsed.get("value"),
                "unit": parsed.get("unit"),
                "expected_dimension": report.get("expected_dimension"),
                "surfaces": ";".join(report.get("surfaces", [])),
                "optional_mechanism": report.get("optional_mechanism"),
                "error": report.get("error"),
            }
        )
    return rows
