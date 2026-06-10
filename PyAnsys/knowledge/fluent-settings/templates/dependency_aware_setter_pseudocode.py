"""
Dependency-aware Fluent setting pattern.

This is pseudocode. Adapt to the actual PyFluent session object and version.
Goal: avoid blindly setting paths before parents exist.

For executable shared helpers, see:
- `../../../src/pyansys_fluent/common.py`
- `../../../src/pyansys_fluent/dependency_workflow.py`
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class SettingAttempt:
    path: str
    requested: Any
    parent_path: Optional[str] = None
    parent_active: Optional[bool] = None
    available_children: list[str] = field(default_factory=list)
    available_options: list[str] = field(default_factory=list)
    result: str = "not_attempted"
    readback: Any = None
    error: Optional[str] = None
    manual_fix_required: bool = False


def safe_child_names(obj: Any) -> list[str]:
    """Try common PyFluent inspection patterns."""
    for attr in ("child_names", "get_child_names"):
        try:
            value = getattr(obj, attr)
            return list(value() if callable(value) else value)
        except Exception:
            pass
    try:
        return [x for x in dir(obj) if not x.startswith("_")]
    except Exception:
        return []


def safe_allowed_values(obj: Any) -> list[str]:
    """Try common allowed-values patterns. Exact method varies by PyFluent version."""
    candidates = ["allowed_values", "allowed_values_list", "get_allowed_values"]
    out = []
    for attr in candidates:
        try:
            value = getattr(obj, attr)
            got = value() if callable(value) else value
            if got:
                out.extend(list(got))
        except Exception:
            pass
    return sorted(set(map(str, out)))


def dependency_aware_set(
    *,
    root: Any,
    path: str,
    value: Any,
    getter: Callable[[Any, str], Any],
    setter: Callable[[Any, Any], None],
    readback: Optional[Callable[[Any], Any]] = None,
    refresh: Optional[Callable[[], None]] = None,
) -> SettingAttempt:
    """
    Parameters:
        root: Fluent solver/settings root object.
        path: Logical setting path for logs.
        value: Desired value.
        getter: function that returns the live setting object from root.
        setter: function that applies value to the live setting object.
        readback: optional function to read current value.
        refresh: optional function to refresh/reacquire state.
    """
    attempt = SettingAttempt(path=path, requested=value)

    try:
        if refresh:
            refresh()
        obj = getter(root, path)
        attempt.available_children = safe_child_names(obj)
        attempt.available_options = safe_allowed_values(obj)

        setter(obj, value)

        if refresh:
            refresh()
            obj = getter(root, path)

        attempt.readback = readback(obj) if readback else None
        if readback is not None and str(attempt.readback) != str(value):
            attempt.result = "set_called_but_readback_mismatch"
            attempt.manual_fix_required = True
        else:
            attempt.result = "success"
        return attempt

    except Exception as exc:
        attempt.result = "failed"
        attempt.error = repr(exc)
        attempt.manual_fix_required = True
        return attempt


# DPM injection order pseudocode

def create_dpm_injection_dependency_order(session, injection_name: str, diameter_m: float):
    """
    Pseudocode only. Exact paths/commands must be discovered from the live session.
    """
    log = []

    # 1. Enable DPM if needed.
    # 2. Refresh/reacquire DPM tree.
    # 3. Create injection with minimum/default settings.
    # 4. Reacquire injection object.
    # 5. Set particle type = inert.
    # 6. Reacquire injection object.
    # 7. Assign material.
    # 8. Reacquire injection object.
    # 9. Set injection type = surface.
    # 10. Reacquire injection object.
    # 11. Inspect available surfaces and bind steaminlet.
    # 12. Set diameter, velocity, flow rate.
    # 13. Read back everything.

    return log
