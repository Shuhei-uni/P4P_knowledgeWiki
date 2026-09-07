#!/usr/bin/env python3
"""Shared helpers for Fluent setup reconstruction scripts."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pyansys_fluent.common import remote_file_exists


def print_header(title: str) -> None:
    print(f"\n=== {title} ===")


def normalize_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.strip().lower())


def require_remote_input(solver, path_text: str, label: str) -> None:
    if not remote_file_exists(solver, path_text):
        raise FileNotFoundError(f"Fluent cannot see {label}: {path_text}")


def names_from_boundary_state(boundary_state: Mapping[str, Any], boundary_type: str) -> list[str]:
    section = boundary_state.get(boundary_type, {})
    if not isinstance(section, Mapping):
        return []
    return sorted(str(name) for name in section.keys() if str(name) != "settings")


def summarize_boundary_state(boundary_state: Mapping[str, Any]) -> None:
    for boundary_type, zones in boundary_state.items():
        if not isinstance(zones, Mapping):
            continue
        names = [str(name) for name in zones.keys() if str(name) != "settings"]
        if names:
            print(f"{boundary_type}: {', '.join(sorted(names))}")


def detect_role_name(boundary_state: Mapping[str, Any], role_aliases: Mapping[str, Sequence[str]], role: str) -> tuple[str, str] | None:
    aliases = {normalize_name(alias) for alias in role_aliases[role]}
    for boundary_type, zones in boundary_state.items():
        if not isinstance(zones, Mapping):
            continue
        for raw_name in zones.keys():
            if raw_name == "settings":
                continue
            if normalize_name(str(raw_name)) in aliases:
                return boundary_type, str(raw_name)
    return None


def detect_cell_zone_name(cell_zone_state: Mapping[str, Any], preferred: Sequence[str]) -> tuple[str, str] | None:
    aliases = {normalize_name(alias) for alias in preferred}
    for zone_type, zones in cell_zone_state.items():
        if not isinstance(zones, Mapping):
            continue
        for raw_name in zones.keys():
            if raw_name == "settings":
                continue
            if normalize_name(str(raw_name)) in aliases:
                return zone_type, str(raw_name)
    return None


def pick_first_named_object(branch_state: Mapping[str, Any]) -> tuple[str, str] | None:
    for zone_type, zones in branch_state.items():
        if not isinstance(zones, Mapping):
            continue
        for raw_name in zones.keys():
            if raw_name == "settings":
                continue
            return zone_type, str(raw_name)
    return None


def deep_replace_names(value: Any, replacements: Mapping[str, str]) -> Any:
    if isinstance(value, str):
        return replacements.get(value, value)
    if isinstance(value, Mapping):
        remapped: dict[str, Any] = {}
        for key, item in value.items():
            new_key = replacements.get(key, key) if isinstance(key, str) else key
            remapped[new_key] = deep_replace_names(item, replacements)
        return remapped
    if isinstance(value, list):
        return [deep_replace_names(item, replacements) for item in value]
    return value


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

