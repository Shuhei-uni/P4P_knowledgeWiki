#!/usr/bin/env python3
"""Fail-closed P4P verification for reviewed deterministic workers.

The safe_* accessors are compatibility helpers for domain workers, not a second
agent discovery API. New live discovery uses pyfluent-mcp's describe_path tools.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import math
from numbers import Real
from typing import Any, Callable, Literal

FailureCategory = Literal[
    "order/dependency issue", "path/version issue", "invalid value/format issue",
    "PyFluent wrapper limitation", "requires TUI fallback", "requires manual GUI cleanup",
    "readback mismatch", "verification missing", "prerequisite blocked", "unknown",
]
_UNSET = object()


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
    result: Literal["pending", "success", "failed", "readback_mismatch", "blocked"] = "pending"
    readback: Any = None
    category: FailureCategory = "unknown"
    error: str | None = None
    notes: list[str] = field(default_factory=list)
    verified: bool = False


@dataclass
class WorkflowStep:
    name: str
    path: str
    getter: Callable[[Any], Any]
    setter: Callable[[Any], None]
    readback: Callable[[Any], Any] | None = None
    refresh: Callable[[], None] | None = None
    expected: Any = _UNSET
    rel_tol: float = 0.0
    abs_tol: float = 0.0


def _coerce_list(value: Any) -> list[str]:
    if value is None or isinstance(value, (str, bytes)):
        return []
    try:
        return [str(item) for item in value]
    except (TypeError, ValueError):
        return []


def _names(obj: Any, accessors: tuple[str, ...]) -> list[str]:
    for name in accessors:
        try:
            value = getattr(obj, name)
            return _coerce_list(value() if callable(value) else value)
        except Exception:
            continue
    return []  # Compatibility only: an empty result is not evidence of absence.


def safe_child_names(obj: Any) -> list[str]:
    return _names(obj, ("get_active_child_names", "child_names", "get_child_names"))


def safe_command_names(obj: Any) -> list[str]:
    return _names(obj, ("get_active_command_names", "command_names", "get_command_names"))


def safe_object_names(obj: Any) -> list[str]:
    return _names(obj, ("get_object_names", "object_names"))


def safe_allowed_values(obj: Any) -> list[str]:
    return sorted(set(_names(obj, ("allowed_values", "get_allowed_values", "allowed_values_list"))))


def probe_object(obj: Any) -> StepProbe:
    return StepProbe(safe_child_names(obj), safe_object_names(obj), safe_command_names(obj), safe_allowed_values(obj))


def classify_failure(error: Exception | str | None) -> FailureCategory:
    text = str(error or "").lower()
    groups = [
        ("order/dependency issue", ("inactive", "not active", "not enabled", "missing child", "does not exist yet")),
        ("path/version issue", ("attributeerror", "unknown path", "unknown command", "no such", "not found")),
        ("invalid value/format issue", ("invalid", "expected", "typeerror", "valueerror", "allowed values", "out of range")),
        ("PyFluent wrapper limitation", ("not implemented", "wrapper", "pyfluent", "api does not expose")),
        ("requires TUI fallback", ("scheme", "tui", "text command", "menu")),
        ("requires manual GUI cleanup", ("gui", "manually", "dialog", "cleanup")),
    ]
    for category, tokens in groups:
        if any(token in text for token in tokens):
            return category
    return "unknown"


def values_equal(observed: Any, expected: Any, *, rel_tol: float = 0.0, abs_tol: float = 0.0) -> bool:
    """Typed structural equality with explicit numerical tolerances; NaN never passes."""
    if isinstance(observed, bool) or isinstance(expected, bool):
        return type(observed) is type(expected) and observed == expected
    if isinstance(observed, Real) and isinstance(expected, Real):
        return math.isfinite(observed) and math.isfinite(expected) and math.isclose(observed, expected, rel_tol=rel_tol, abs_tol=abs_tol)
    if isinstance(observed, Mapping) and isinstance(expected, Mapping):
        return observed.keys() == expected.keys() and all(values_equal(observed[k], expected[k], rel_tol=rel_tol, abs_tol=abs_tol) for k in observed)
    if isinstance(observed, (list, tuple)) and isinstance(expected, (list, tuple)):
        return len(observed) == len(expected) and all(values_equal(a, b, rel_tol=rel_tol, abs_tol=abs_tol) for a, b in zip(observed, expected))
    return type(observed) is type(expected) and observed == expected


def execute_step(root: Any, step: WorkflowStep) -> WorkflowStepResult:
    result = WorkflowStepResult(name=step.name, path=step.path, requested=None if step.expected is _UNSET else step.expected)
    if step.readback is None or step.expected is _UNSET:
        result.result, result.category = "blocked", "verification missing"
        result.notes.append("Define expected state and readback before mutation.")
        return result
    try:
        if step.rel_tol < 0 or step.abs_tol < 0 or not math.isfinite(step.rel_tol) or not math.isfinite(step.abs_tol):
            raise ValueError("Readback tolerances must be finite and non-negative.")
        if step.refresh is not None:
            step.refresh()
        obj = step.getter(root)
        result.probe = probe_object(obj)
        step.setter(obj)
        if step.refresh is not None:
            step.refresh()
        obj = step.getter(root)  # Always reacquire after the mutation.
        result.readback = step.readback(obj)
        if not values_equal(result.readback, step.expected, rel_tol=step.rel_tol, abs_tol=step.abs_tol):
            result.result, result.category = "readback_mismatch", "readback mismatch"
            result.notes.append("Mutation returned, but its postcondition did not match; reconcile before retry.")
            return result
        result.result, result.verified = "success", True
        return result
    except Exception as exc:
        result.result, result.error = "failed", repr(exc)
        result.category = classify_failure(exc)
        return result


def execute_workflow(root: Any, steps: list[WorkflowStep]) -> list[WorkflowStepResult]:
    """Never execute dependent steps after a missing or failed verification."""
    results = []
    blocked = False
    for step in steps:
        if blocked:
            result = WorkflowStepResult(name=step.name, path=step.path, result="blocked", category="prerequisite blocked", notes=["A preceding step was not verified; this step was not attempted."])
        else:
            result = execute_step(root, step)
            blocked = not result.verified
        results.append(result)
    return results
