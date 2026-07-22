#!/usr/bin/env python3
"""Shared live-tree helpers for Eulerian Wall Film diagnostics."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

from pyansys_fluent.dependency_workflow import safe_allowed_values, safe_child_names
from pyansys_fluent.extraction import safe_json


def normalize_token(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def safe_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def get_state(obj: Any, label: str, warnings: list[str]) -> Any:
    try:
        return safe_json(obj.get_state())
    except Exception as exc:
        warnings.append(f"{label}.get_state unavailable: {type(exc).__name__}: {exc}")
        return None


def find_values_by_key(payload: Any, candidate_keys: Sequence[str]) -> list[dict[str, Any]]:
    wanted = {normalize_token(key) for key in candidate_keys}
    found: list[dict[str, Any]] = []

    def walk(value: Any, path: list[str]) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                child_path = [*path, str(key)]
                if normalize_token(key) in wanted:
                    found.append({"path": ".".join(child_path), "value": safe_json(child)})
                walk(child, child_path)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for index, child in enumerate(value):
                walk(child, [*path, str(index)])

    walk(payload, [])
    return found


def first_scalar_match(payload: Any, candidate_keys: Sequence[str]) -> Any:
    for item in find_values_by_key(payload, candidate_keys):
        value = item["value"]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, Mapping):
            for key in ("value", "enabled", "option", "state"):
                if key in value and isinstance(value[key], (str, int, float, bool)):
                    return value[key]
    return None


def as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"yes", "on", "true", "enabled", "1"}:
            return True
        if normalized in {"no", "off", "false", "disabled", "0"}:
            return False
    return None


def child_by_alias(parent: Any, aliases: Sequence[str]) -> tuple[Any | None, str | None]:
    names = safe_child_names(parent)
    name_map = {normalize_token(name): str(name) for name in names}
    for alias in aliases:
        actual = name_map.get(normalize_token(alias))
        if actual:
            try:
                return getattr(parent, actual), actual
            except Exception:
                pass
    for alias in aliases:
        try:
            return getattr(parent, alias), alias
        except Exception:
            continue
    return None, None


def set_leaf(leaf: Any, value: Any) -> None:
    setter = getattr(leaf, "set_state", None)
    if callable(setter):
        setter(value)
        return
    raise AttributeError(f"{type(leaf).__name__} has no set_state method")


def set_child(
    parent: Any,
    aliases: Sequence[str],
    value: Any,
    *,
    required: bool,
    actions: list[dict[str, Any]],
) -> bool:
    child, resolved = child_by_alias(parent, aliases)
    if child is None:
        actions.append(
            {
                "aliases": list(aliases),
                "requested": safe_json(value),
                "status": "missing",
                "required": required,
            }
        )
        if required:
            raise AttributeError(f"Required child not found; aliases={list(aliases)}")
        return False
    try:
        set_leaf(child, value)
        readback = child.get_state() if hasattr(child, "get_state") else None
        actions.append(
            {
                "child": resolved,
                "requested": safe_json(value),
                "readback": safe_json(readback),
                "status": "set",
                "required": required,
            }
        )
        return True
    except Exception as exc:
        actions.append(
            {
                "child": resolved,
                "requested": safe_json(value),
                "status": "failed",
                "required": required,
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        if required:
            raise
        return False


def resolve_allowed_value(
    leaf: Any,
    candidates: Sequence[str],
    token_groups: Sequence[Sequence[str]],
) -> tuple[str, dict[str, Any]]:
    allowed = [str(value) for value in safe_allowed_values(leaf)]
    normalized = {normalize_token(value): value for value in allowed}
    for candidate in candidates:
        if normalize_token(candidate) in normalized:
            return normalized[normalize_token(candidate)], {
                "strategy": "exact-normalized",
                "allowed_values": allowed,
            }
    for tokens in token_groups:
        normalized_tokens = [normalize_token(token) for token in tokens]
        for value in allowed:
            compact = normalize_token(value)
            if all(token in compact for token in normalized_tokens):
                return value, {"strategy": "token-match", "allowed_values": allowed}
    return str(candidates[0]), {
        "strategy": "fallback-first-candidate",
        "allowed_values": allowed,
    }
