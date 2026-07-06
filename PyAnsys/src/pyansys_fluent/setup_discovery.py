#!/usr/bin/env python3
"""Discovery and boundary-role helpers for Fluent setup scripts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pyansys_fluent.common import try_action
from pyansys_fluent.setup_common import detect_role_name, names_from_boundary_state, normalize_name


ROLE_ALIASES: dict[str, tuple[str, ...]] = {
    "liquid_inlet": (
        "inlet_liquid_outer",
        "liquidinlet",
        "liquid_inlet",
        "liquid inlet",
        "liquid",
    ),
    "steam_inlet": (
        "inlet_steam_inner",
        "steaminlet",
        "steam_inlet",
        "steam-inlet",
        "inletsteam",
        "inlet steam",
        "steam inlet",
        "steam",
    ),
    "outlet": (
        "steamoutlet",
        "steam_outlet",
        "steam outlet",
        "outlet",
    ),
    "wall": (
        "wall-fluid",
        "wallfluid",
        "wall",
    ),
    "bottom": ("bottom",),
}

BOUNDARY_TYPE_ORDER = (
    "velocity_inlet",
    "mass_flow_inlet",
    "pressure_outlet",
    "wall",
    "interior",
)


def _candidate_boundary_names(boundary_state: Mapping[str, Any], boundary_types: tuple[str, ...]) -> list[str]:
    names: list[str] = []
    for boundary_type in boundary_types:
        section = boundary_state.get(boundary_type, {})
        if not isinstance(section, Mapping):
            continue
        for raw_name in section.keys():
            if raw_name == "settings":
                continue
            names.append(str(raw_name))
    return names


def _resolve_steam_inlet_fallback(boundary_state: Mapping[str, Any], assigned_names: set[str]) -> str | None:
    candidate_names = [
        name
        for name in _candidate_boundary_names(boundary_state, ("velocity_inlet", "mass_flow_inlet"))
        if name not in assigned_names
    ]
    if not candidate_names:
        return None

    normalized = {normalize_name(name): name for name in candidate_names}
    for preferred in ("steaminlet", "inletsteam", "steam", "inlet"):
        if preferred in normalized:
            return normalized[preferred]

    steamish = [name for name in candidate_names if "steam" in normalize_name(name)]
    if len(steamish) == 1:
        return steamish[0]

    if len(candidate_names) == 1:
        return candidate_names[0]

    return None


def build_target_role_map(boundary_state: Mapping[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for role in ROLE_ALIASES:
        match = detect_role_name(boundary_state, ROLE_ALIASES, role)
        if not match:
            if role == "steam_inlet":
                fallback = _resolve_steam_inlet_fallback(boundary_state, set(mapping.values()))
                if fallback:
                    mapping[role] = fallback
                    print(f"role_map[{role}] = {fallback} (fallback heuristic)")
                    continue
            if role == "bottom" and "wall" in mapping:
                mapping["bottom"] = mapping["wall"]
                print(f"role_map[bottom] = {mapping['bottom']} (fallback to wall)")
                continue
            raise RuntimeError(f"Could not detect target boundary for role: {role}")
        mapping[role] = match[1]
        print(f"role_map[{role}] = {match[1]}")
    return mapping


def build_name_replacements_from_fallback(
    fallback_boundary_state: Mapping[str, Any],
    target_boundary_state: Mapping[str, Any],
) -> dict[str, str]:
    replacements: dict[str, str] = {"fluid": "fluid"}
    for role in ROLE_ALIASES:
        source_match = detect_role_name(fallback_boundary_state, ROLE_ALIASES, role)
        target_match = detect_role_name(target_boundary_state, ROLE_ALIASES, role)
        if source_match and target_match:
            replacements[source_match[1]] = target_match[1]
    return replacements


def convert_target_boundaries_to_intended(
    solver,
    target_boundary_state: Mapping[str, Any],
    role_map: Mapping[str, str],
) -> bool:
    bc = solver.settings.setup.boundary_conditions
    desired = {
        role_map["liquid_inlet"]: "velocity_inlet",
        role_map["steam_inlet"]: "velocity_inlet",
        role_map["outlet"]: "pressure_outlet",
        role_map["wall"]: "wall",
        role_map["bottom"]: "wall",
    }
    ok = True
    for zone_name, desired_type in desired.items():
        current_type = None
        for boundary_type, zones in target_boundary_state.items():
            if isinstance(zones, Mapping) and zone_name in zones:
                current_type = boundary_type
                break
        if current_type == desired_type:
            continue
        ok &= try_action(
            f"set_zone_type_{zone_name}",
            lambda name=zone_name, new_type=desired_type: bc.set_zone_type(
                zone_list=[name], new_type=new_type.replace("_", "-")
            ),
        )
    return ok


def build_compact_boundary_summary(boundary_state: Mapping[str, Any]) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {}
    for boundary_type in BOUNDARY_TYPE_ORDER:
        names = names_from_boundary_state(boundary_state, boundary_type)
        if names:
            summary[boundary_type] = names
    return summary
