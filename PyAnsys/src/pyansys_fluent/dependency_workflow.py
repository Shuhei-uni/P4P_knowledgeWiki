#!/usr/bin/env python3
"""Dependency-aware execution helpers for PyFluent automation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal


FailureCategory = Literal[
    "order/dependency issue",
    "path/version issue",
    "invalid value/format issue",
    "PyFluent wrapper limitation",
    "requires TUI fallback",
    "requires manual GUI cleanup",
    "unknown",
]


@dataclass
class StepProbe:
    child_names: list[str] = field(default_factory=list)
    object_names: list[str] = field(default_factory=list)
    command_names: list[str] = field(default_factory=list)
    allowed_values: list[str] = field(default_factory=list)


@dataclass
class WorkflowStepResult:
    name: str
    path: str
    requested: Any = None
    probe: StepProbe = field(default_factory=StepProbe)
    result: Literal["pending", "success", "failed", "readback_mismatch"] = "pending"
    readback: Any = None
    category: FailureCategory = "unknown"
    error: str | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class WorkflowStep:
    name: str
    path: str
    getter: Callable[[Any], Any]
    setter: Callable[[Any], None]
    readback: Callable[[Any], Any] | None = None
    refresh: Callable[[], None] | None = None
    expected: Any = None


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    try:
        return [str(item) for item in list(value)]
    except Exception:
        return []


def safe_child_names(obj: Any) -> list[str]:
    for attr in ("child_names", "get_child_names"):
        try:
            value = getattr(obj, attr)
            return _coerce_list(value() if callable(value) else value)
        except Exception:
            pass
    try:
        return sorted(name for name in dir(obj) if not name.startswith("_"))
    except Exception:
        return []


def safe_command_names(obj: Any) -> list[str]:
    for attr in ("command_names", "get_command_names"):
        try:
            value = getattr(obj, attr)
            return _coerce_list(value() if callable(value) else value)
        except Exception:
            pass
    return []


def safe_object_names(obj: Any) -> list[str]:
    for attr in ("object_names", "get_object_names"):
        try:
            value = getattr(obj, attr)
            return _coerce_list(value() if callable(value) else value)
        except Exception:
            pass
    return []


def safe_allowed_values(obj: Any) -> list[str]:
    out: list[str] = []
    for attr in ("allowed_values", "allowed_values_list", "get_allowed_values"):
        try:
            value = getattr(obj, attr)
            out.extend(_coerce_list(value() if callable(value) else value))
        except Exception:
            pass
    return sorted(set(out))


def probe_object(obj: Any) -> StepProbe:
    return StepProbe(
        child_names=safe_child_names(obj),
        object_names=safe_object_names(obj),
        command_names=safe_command_names(obj),
        allowed_values=safe_allowed_values(obj),
    )


def classify_failure(error: Exception | str | None) -> FailureCategory:
    if error is None:
        return "unknown"

    text = str(error).lower()

    if any(token in text for token in ("inactive", "not active", "not enabled", "missing child", "does not exist yet")):
        return "order/dependency issue"
    if any(token in text for token in ("attributeerror", "unknown path", "unknown command", "no such", "not found")):
        return "path/version issue"
    if any(token in text for token in ("invalid", "expected", "typeerror", "valueerror", "allowed values", "out of range")):
        return "invalid value/format issue"
    if any(token in text for token in ("not implemented", "wrapper", "pyfluent", "api does not expose")):
        return "PyFluent wrapper limitation"
    if any(token in text for token in ("scheme", "tui", "text command", "menu")):
        return "requires TUI fallback"
    if any(token in text for token in ("gui", "manually", "dialog", "cleanup")):
        return "requires manual GUI cleanup"
    return "unknown"


def execute_step(root: Any, step: WorkflowStep) -> WorkflowStepResult:
    result = WorkflowStepResult(name=step.name, path=step.path, requested=step.expected)

    try:
        if step.refresh is not None:
            step.refresh()

        obj = step.getter(root)
        result.probe = probe_object(obj)
        step.setter(obj)

        if step.refresh is not None:
            step.refresh()
            obj = step.getter(root)

        if step.readback is not None:
            result.readback = step.readback(obj)
            if step.expected is not None and str(result.readback) != str(step.expected):
                result.result = "readback_mismatch"
                result.category = "requires manual GUI cleanup"
                result.notes.append("Setter ran but readback did not match the expected value.")
                return result

        result.result = "success"
        result.category = "unknown"
        return result

    except Exception as exc:
        result.result = "failed"
        result.error = repr(exc)
        result.category = classify_failure(exc)
        return result


def execute_workflow(root: Any, steps: list[WorkflowStep]) -> list[WorkflowStepResult]:
    return [execute_step(root, step) for step in steps]
