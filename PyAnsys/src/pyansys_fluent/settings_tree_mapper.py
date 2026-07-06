#!/usr/bin/env python3
"""Tree-mapping helpers for live Fluent settings discovery.

The mapper is intentionally probe-first:
enable or load the relevant parent state, inspect live child/object names,
then recurse only into branches that exist in the current Fluent session.

An optional seed tree can be supplied from an archived JSON snapshot to help
label expected-but-missing branches and to compare a live tree against a prior
case without hard-coding the path list.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pyansys_fluent.common import safe_get_state
from pyansys_fluent.dependency_workflow import (
    safe_allowed_values,
    safe_child_names,
    safe_command_names,
    safe_object_names,
)


META_KEYS = {
    "_meta",
    "_state",
    "_state_summary",
    "_missing_in_live",
    "_missing_reason",
    "_seed_available",
    "_seed_path",
}

ATTRIBUTE_ALIASES: dict[str, tuple[str, ...]] = {
    "model": ("models",),
    "models": ("model",),
}

ACTIVATION_RULES: list[dict[str, Any]] = [
    {
        "path_suffix": ("energy",),
        "assignments": (("enabled", True),),
    },
    {
        "path_suffix": ("energy", "two_temperature"),
        "assignments": (("enabled", True),),
    },
    {
        "path_suffix": ("viscous",),
        "assignments": (("model", "k-epsilon"),),
    },
    {
        "path_suffix": ("multiphase",),
        "assignments": (("model", "mixture"), ("models", "mixture")),
    },
    {
        "path_suffix": ("discrete_phase",),
        "assignments": (("enabled", True), ("model", True)),
    },
]


def _coerce_seed_children(seed_tree: Any) -> dict[str, Any]:
    if not isinstance(seed_tree, Mapping):
        return {}

    children = seed_tree.get("children")
    if isinstance(children, Mapping):
        return {str(name): child for name, child in children.items()}

    objects = seed_tree.get("objects")
    if isinstance(objects, Mapping):
        return {str(name): child for name, child in objects.items()}

    return {
        str(name): value
        for name, value in seed_tree.items()
        if str(name) not in META_KEYS and not str(name).startswith("_")
    }


def _seed_child_names(seed_tree: Any, live_child_names: Sequence[str] | None = None, live_object_names: Sequence[str] | None = None) -> list[str]:
    if live_object_names:
        return list(_coerce_seed_children(seed_tree).keys()) if isinstance(seed_tree, Mapping) and isinstance(seed_tree.get("children"), Mapping) else []
    return list(_coerce_seed_children(seed_tree).keys())


def _seed_object_names(seed_tree: Any, live_child_names: Sequence[str] | None = None, live_object_names: Sequence[str] | None = None) -> list[str]:
    if not isinstance(seed_tree, Mapping):
        return []
    object_names = seed_tree.get("object_names")
    if isinstance(object_names, Sequence) and not isinstance(object_names, (str, bytes)):
        return [str(name) for name in object_names]
    objects = seed_tree.get("objects")
    if isinstance(objects, Mapping):
        return [str(name) for name in objects.keys()]
    if seed_tree.get("children") is None and (live_object_names or not live_child_names):
        return [
            str(name)
            for name in seed_tree.keys()
            if str(name) not in META_KEYS and not str(name).startswith("_")
        ]
    return []


def _merge_ordered(*groups: Sequence[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            item_text = str(item)
            if item_text in seen:
                continue
            seen.add(item_text)
            merged.append(item_text)
    return merged


def _summarize_state(state: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {"state_type": type(state).__name__}
    if isinstance(state, Mapping):
        summary["mapping_keys"] = sorted(str(key) for key in state.keys())
        summary["mapping_size"] = len(state)
    elif isinstance(state, list):
        summary["list_size"] = len(state)
    elif isinstance(state, str):
        summary["string_length"] = len(state)
    return summary


def _probe_meta(obj: Any, label: str) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "label": label,
        "type": type(obj).__name__,
        "module": type(obj).__module__,
        "child_names": safe_child_names(obj),
        "object_names": safe_object_names(obj),
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
            meta[key] = value() if callable(value) else value
        except Exception:
            continue
    return meta


def _get_live_child(obj: Any, name: str) -> Any:
    try:
        return getattr(obj, name)
    except Exception:
        for alias in ATTRIBUTE_ALIASES.get(name, ()):
            try:
                return getattr(obj, alias)
            except Exception:
                continue
        raise


def _get_live_object(obj: Any, name: str) -> Any:
    try:
        return obj[name]
    except Exception:
        return _get_live_child(obj, name)


def _path_suffix_matches(label: str, suffix: tuple[str, ...]) -> bool:
    parts = [part for part in label.replace("[", ".").replace("]", "").split(".") if part]
    if len(parts) < len(suffix):
        return False
    return tuple(parts[-len(suffix):]) == suffix


def _attempt_known_activation(obj: Any, label: str) -> list[str]:
    notes: list[str] = []
    for rule in ACTIVATION_RULES:
        if not _path_suffix_matches(label, tuple(rule["path_suffix"])):
            continue
        for child_name, value in rule["assignments"]:
            try:
                if hasattr(obj, child_name):
                    setattr(obj, child_name, value)
                    notes.append(f"{child_name}={value!r}")
                    break
            except Exception as exc:
                notes.append(f"{child_name} failed: {type(exc).__name__}: {exc}")
                continue
    return notes


def _seed_child_has_name(seed_tree: Any, name: str) -> bool:
    if not isinstance(seed_tree, Mapping):
        return False
    children = seed_tree.get("children")
    if isinstance(children, Mapping) and name in children:
        return True
    objects = seed_tree.get("objects")
    if isinstance(objects, Mapping) and name in objects:
        return True
    return False


def _attempt_direct_child_activation(obj: Any, child_name: str, child_seed: Any = None) -> list[str]:
    notes: list[str] = []
    nested_payloads: list[dict[str, Any]] = []
    if _seed_child_has_name(child_seed, "enable"):
        nested_payloads.append({"enable": True})
    if _seed_child_has_name(child_seed, "enabled"):
        nested_payloads.append({"enabled": True})
    nested_payloads.extend([{"enable": True}, {"enabled": True}])
    strategies: list[tuple[str, Any]] = [
        ("set_state_true", True),
        ("set_state_on", "on"),
        ("setattr_true", True),
        ("setattr_on", "on"),
    ]
    strategies.extend(
        (f"set_state_{'_'.join(sorted(payload.keys()))}", payload)
        for payload in nested_payloads
    )
    for strategy_name, payload in strategies:
        try:
            if strategy_name.startswith("setattr_"):
                setattr(obj, child_name, payload)
            else:
                obj.set_state({child_name: payload})
            notes.append(f"{child_name}:{strategy_name}")
            return notes
        except Exception as exc:
            notes.append(f"{child_name}:{strategy_name} failed: {type(exc).__name__}: {exc}")
    return notes


def capture_settings_tree(
    obj: Any,
    label: str,
    *,
    max_depth: int = 5,
    include_state: bool = True,
    seed_tree: Any = None,
    activate_parents: bool = False,
    depth: int = 0,
    seen: set[int] | None = None,
) -> dict[str, Any]:
    """Capture a live Fluent settings subtree plus optional seed comparison data."""
    if seen is None:
        seen = set()

    object_id = id(obj)
    if object_id in seen:
        return {
            "_meta": {
                "label": label,
                "cycle_detected": True,
            }
        }
    seen.add(object_id)

    snapshot: dict[str, Any] = {
        "_meta": _probe_meta(obj, label),
    }
    if seed_tree is not None:
        snapshot["_meta"]["_seed_available"] = True
        seed_label = None
        if isinstance(seed_tree, Mapping):
            seed_label = seed_tree.get("label") or seed_tree.get("path")
        if seed_label is not None:
            snapshot["_meta"]["_seed_path"] = str(seed_label)

    if include_state and hasattr(obj, "get_state"):
        state = safe_get_state(obj, label)
        snapshot["_state"] = state
        snapshot["_state_summary"] = _summarize_state(state)

    if activate_parents:
        activation_notes = _attempt_known_activation(obj, label)
        if activation_notes:
            snapshot["_activation_attempts"] = activation_notes
            if include_state and hasattr(obj, "get_state"):
                refreshed_state = safe_get_state(obj, label)
                snapshot["_activation_state"] = refreshed_state
                snapshot["_activation_state_summary"] = _summarize_state(refreshed_state)

    if depth >= max_depth:
        snapshot["_truncated"] = True
        return snapshot

    live_child_names = _merge_ordered(
        snapshot["_meta"]["child_names"],
        _seed_child_names(seed_tree, snapshot["_meta"]["child_names"], snapshot["_meta"]["object_names"]),
    )
    live_object_names = _merge_ordered(
        snapshot["_meta"]["object_names"],
        _seed_object_names(seed_tree, snapshot["_meta"]["child_names"], snapshot["_meta"]["object_names"]),
    )

    seed_children = _coerce_seed_children(seed_tree)

    if live_child_names:
        children: dict[str, Any] = {}
        for child_name in live_child_names:
            child_seed = seed_children.get(child_name)
            activation_notes: list[str] = []
            try:
                child_obj = _get_live_child(obj, child_name)
            except Exception as exc:
                if activate_parents:
                    activation_notes = _attempt_direct_child_activation(obj, child_name, child_seed)
                    try:
                        child_obj = _get_live_child(obj, child_name)
                    except Exception as exc2:
                        children[child_name] = {
                            "_meta": {
                                "label": f"{label}.{child_name}",
                                "missing_in_live": True,
                            },
                            "_missing_reason": f"{type(exc2).__name__}: {exc2}",
                            "_activation_attempts": activation_notes,
                        }
                        continue
                else:
                    children[child_name] = {
                        "_meta": {
                            "label": f"{label}.{child_name}",
                            "missing_in_live": True,
                        },
                        "_missing_reason": f"{type(exc).__name__}: {exc}",
                    }
                    continue
            if activation_notes:
                snapshot.setdefault("_activation_attempts", []).extend(activation_notes)
            children[child_name] = capture_settings_tree(
                child_obj,
                f"{label}.{child_name}",
                max_depth=max_depth,
                include_state=include_state,
                seed_tree=child_seed,
                activate_parents=activate_parents,
                depth=depth + 1,
                seen=seen,
            )
        snapshot["children"] = children

    if live_object_names:
        objects: dict[str, Any] = {}
        for object_name in live_object_names:
            object_seed = None
            if isinstance(seed_tree, Mapping):
                if isinstance(seed_tree.get("objects"), Mapping):
                    object_seed = seed_tree["objects"].get(object_name)
                elif object_name in seed_tree:
                    object_seed = seed_tree[object_name]
            try:
                object_obj = _get_live_object(obj, object_name)
            except Exception as exc:
                objects[object_name] = {
                    "_meta": {
                        "label": f"{label}[{object_name}]",
                        "missing_in_live": True,
                    },
                    "_missing_reason": f"{type(exc).__name__}: {exc}",
                }
                continue
            objects[object_name] = capture_settings_tree(
                object_obj,
                f"{label}[{object_name}]",
                max_depth=max_depth,
                include_state=include_state,
                seed_tree=object_seed,
                activate_parents=activate_parents,
                depth=depth + 1,
                seen=seen,
            )
        snapshot["objects"] = objects

    return snapshot


def compare_tree_shapes(live_tree: Mapping[str, Any], seed_tree: Any, prefix: str = "") -> dict[str, list[str]]:
    """Compare a live capture against a seed tree and list missing/extra paths."""
    summary = {
        "missing_children": [],
        "extra_children": [],
        "missing_objects": [],
        "extra_objects": [],
    }

    live_children = {}
    if isinstance(live_tree.get("children"), Mapping):
        live_children = {str(name): value for name, value in live_tree["children"].items()}
    live_objects = {}
    if isinstance(live_tree.get("objects"), Mapping):
        live_objects = {str(name): value for name, value in live_tree["objects"].items()}

    seed_children = _coerce_seed_children(seed_tree)
    live_child_name_list = list(live_children)
    live_object_name_list = list(live_objects)
    seed_child_names = set(_seed_child_names(seed_tree, live_child_name_list, live_object_name_list))
    seed_object_names = set(_seed_object_names(seed_tree, live_child_name_list, live_object_name_list))

    live_child_names = set(live_child_name_list)
    live_object_names = set(live_object_name_list)

    for name in sorted(seed_child_names - live_child_names):
        summary["missing_children"].append(f"{prefix}.{name}" if prefix else name)
    for name in sorted(live_child_names - seed_child_names):
        summary["extra_children"].append(f"{prefix}.{name}" if prefix else name)
    for name in sorted(seed_object_names - live_object_names):
        summary["missing_objects"].append(f"{prefix}[{name}]" if prefix else name)
    for name in sorted(live_object_names - seed_object_names):
        summary["extra_objects"].append(f"{prefix}[{name}]" if prefix else name)

    for name in sorted(seed_child_names & live_child_names):
        child_summary = compare_tree_shapes(
            live_children[name],
            seed_children.get(name),
            f"{prefix}.{name}" if prefix else name,
        )
        for key, values in child_summary.items():
            summary[key].extend(values)

    for name in sorted(seed_object_names & live_object_names):
        object_seed = None
        if isinstance(seed_tree, Mapping):
            if isinstance(seed_tree.get("objects"), Mapping):
                object_seed = seed_tree["objects"].get(name)
            elif name in seed_tree:
                object_seed = seed_tree[name]
        child_summary = compare_tree_shapes(
            live_objects[name],
            object_seed,
            f"{prefix}[{name}]" if prefix else name,
        )
        for key, values in child_summary.items():
            summary[key].extend(values)

    return summary
