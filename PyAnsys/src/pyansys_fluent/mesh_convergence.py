#!/usr/bin/env python3
"""Reusable parsing and numerical helpers for carrier-field mesh studies."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any


NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"


def normalize_zone_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.strip().lower())


def named_zones(branch_state: Mapping[str, Any]) -> dict[str, str]:
    """Return ``zone name -> Fluent category`` from a settings state tree."""
    result: dict[str, str] = {}
    for category, zones in branch_state.items():
        if not isinstance(zones, Mapping):
            continue
        for name in zones:
            if str(name) != "settings":
                result[str(name)] = str(category)
    return result


def resolve_zone_roles(
    available: Mapping[str, str],
    aliases: Mapping[str, Sequence[str]],
) -> dict[str, dict[str, str]]:
    """Resolve every canonical role exactly once or raise a diagnostic error."""
    normalized: dict[str, list[str]] = {}
    for raw_name in available:
        normalized.setdefault(normalize_zone_name(raw_name), []).append(raw_name)

    resolved: dict[str, dict[str, str]] = {}
    for role, role_aliases in aliases.items():
        candidates: list[str] = []
        for alias in (role, *role_aliases):
            candidates.extend(normalized.get(normalize_zone_name(alias), []))
        unique = sorted(set(candidates))
        if not unique:
            raise RuntimeError(
                f"path/version issue: missing required zone role {role!r}; "
                f"available={sorted(available)}"
            )
        if len(unique) != 1:
            raise RuntimeError(
                f"invalid value/format issue: ambiguous zone role {role!r}; matches={unique}"
            )
        name = unique[0]
        resolved[role] = {"name": name, "category": available[name]}
    return resolved


def parse_mesh_size(text: str) -> dict[str, int]:
    match = re.search(
        rf"^\s*0\s+({NUMBER})\s+({NUMBER})\s+({NUMBER})\s+({NUMBER})\s*$",
        text,
        flags=re.MULTILINE,
    )
    if not match:
        raise ValueError("Could not parse Fluent mesh size report")
    return {
        "cells": int(float(match.group(1))),
        "faces": int(float(match.group(2))),
        "nodes": int(float(match.group(3))),
        "partitions": int(float(match.group(4))),
    }


def parse_mesh_check(text: str) -> dict[str, Any]:
    patterns = {
        "minimum_cell_volume_m3": rf"minimum volume \(m3\):\s*({NUMBER})",
        "maximum_cell_volume_m3": rf"maximum volume \(m3\):\s*({NUMBER})",
        "domain_volume_m3": rf"total volume \(m3\):\s*({NUMBER})",
        "minimum_face_area_m2": rf"minimum face area \(m2\):\s*({NUMBER})",
        "maximum_face_area_m2": rf"maximum face area \(m2\):\s*({NUMBER})",
    }
    result: dict[str, Any] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            result[key] = float(match.group(1))
    lowered = text.lower()
    result["negative_volume_reported"] = bool(
        re.search(r"negative\s+(?:cell\s+)?volume", lowered)
    ) and not bool(re.search(r"0\s+negative", lowered))
    result["raw_check_contains_error"] = "error:" in lowered
    if "domain_volume_m3" not in result:
        raise ValueError("Could not parse total domain volume from Fluent mesh check")
    return result


def parse_mesh_quality(text: str) -> dict[str, float]:
    oq = re.search(rf"Minimum Orthogonal Quality\s*=\s*({NUMBER})", text, re.IGNORECASE)
    ar = re.search(rf"Maximum Aspect Ratio\s*=\s*({NUMBER})", text, re.IGNORECASE)
    if not oq or not ar:
        raise ValueError("Could not parse Fluent mesh quality report")
    return {
        "minimum_orthogonal_quality": float(oq.group(1)),
        "maximum_aspect_ratio": float(ar.group(1)),
    }


def parse_named_report_rows(text: str, names: Sequence[str]) -> dict[str, float]:
    """Parse named rows from Fluent text reports without depending on headers."""
    result: dict[str, float] = {}
    for name in names:
        match = re.search(
            rf"^\s*{re.escape(name)}\s+({NUMBER})\s*$",
            text,
            flags=re.MULTILINE | re.IGNORECASE,
        )
        if match:
            result[name] = float(match.group(1))
    return result


def parse_net_report_value(text: str) -> float:
    matches = re.findall(rf"^\s*Net\s+({NUMBER})\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
    if not matches:
        raise ValueError("Could not parse Net value from Fluent report")
    return float(matches[-1])


def percent_drift(values: Sequence[float]) -> float:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    if len(finite) < 2:
        return math.nan
    reference = sum(abs(value) for value in finite) / len(finite)
    if reference == 0:
        return 0.0 if max(finite) == min(finite) else math.inf
    return 100.0 * (max(finite) - min(finite)) / reference


def monitor_stability(
    rows: Sequence[Mapping[str, Any]],
    fields: Sequence[str],
    *,
    first_iteration: int = 2500,
) -> dict[str, dict[str, float | int]]:
    window = [row for row in rows if int(float(row["iteration"])) >= first_iteration]
    result: dict[str, dict[str, float | int]] = {}
    for field in fields:
        values = [float(row[field]) for row in window if row.get(field) not in (None, "")]
        result[field] = {
            "samples": len(values),
            "minimum": min(values) if values else math.nan,
            "maximum": max(values) if values else math.nan,
            "mean": sum(values) / len(values) if values else math.nan,
            "drift_percent": percent_drift(values),
        }
    return result


def generalized_richardson(
    coarse: tuple[float, float],
    medium: tuple[float, float],
    fine: tuple[float, float],
    *,
    safety_factor: float = 1.25,
) -> dict[str, Any]:
    """Compute unequal-r Richardson/GCI for a monotonic three-grid sequence.

    Each tuple is ``(h, value)``. A percentage-only result is returned when the
    sequence is oscillatory, flat, or has no usable positive observed-order root.
    """
    h3, phi3 = coarse
    h2, phi2 = medium
    h1, phi1 = fine
    if not (h3 > h2 > h1 > 0):
        return {"status": "invalid_grid_order"}
    e32 = phi3 - phi2
    e21 = phi2 - phi1
    base: dict[str, Any] = {
        "status": "percentage_change_only",
        "coarse": phi3,
        "medium": phi2,
        "fine": phi1,
        "h_coarse": h3,
        "h_medium": h2,
        "h_fine": h1,
        "r_coarse_medium": h3 / h2,
        "r_medium_fine": h2 / h1,
        "pct_coarse_medium": abs(e32 / phi2) * 100.0 if phi2 else math.nan,
        "pct_medium_fine": abs(e21 / phi1) * 100.0 if phi1 else math.nan,
        "monotonic": e32 * e21 > 0,
    }
    if not base["monotonic"] or e32 == 0 or e21 == 0:
        return base
    target = e32 / e21

    def residual(order: float) -> float:
        numerator = h3**order - h2**order
        denominator = h2**order - h1**order
        return numerator / denominator - target

    scan = [10 ** (-5 + index * (math.log10(20.0) + 5) / 399) for index in range(400)]
    bracket: tuple[float, float] | None = None
    previous_p = scan[0]
    previous_f = residual(previous_p)
    for value in scan[1:]:
        current_f = residual(value)
        if math.isfinite(previous_f) and math.isfinite(current_f) and previous_f * current_f <= 0:
            bracket = (previous_p, value)
            break
        previous_p, previous_f = value, current_f
    if bracket is None:
        base["status"] = "unusable_observed_order"
        return base

    lo, hi = bracket
    for _ in range(100):
        mid = (lo + hi) / 2.0
        f_lo = residual(lo)
        f_mid = residual(mid)
        if abs(f_mid) < 1e-12:
            lo = hi = mid
            break
        if f_lo * f_mid <= 0:
            hi = mid
        else:
            lo = mid
    order = (lo + hi) / 2.0
    if not math.isfinite(order) or order <= 0:
        base["status"] = "unusable_observed_order"
        return base

    r21 = h2 / h1
    r32 = h3 / h2
    denom21 = r21**order - 1.0
    denom32 = r32**order - 1.0
    if denom21 <= 0 or denom32 <= 0:
        base["status"] = "unusable_observed_order"
        return base
    extrapolated = phi1 + (phi1 - phi2) / denom21
    gci21 = safety_factor * abs((phi1 - phi2) / phi1) / denom21 * 100.0 if phi1 else math.nan
    gci32 = safety_factor * abs((phi2 - phi3) / phi2) / denom32 * 100.0 if phi2 else math.nan
    asymptotic = gci32 / (gci21 * r21**order) if gci21 else math.nan
    base.update(
        {
            "status": "gci_computed",
            "observed_order": order,
            "richardson_extrapolated": extrapolated,
            "gci_fine_percent": gci21,
            "gci_medium_percent": gci32,
            "asymptotic_ratio": asymptotic,
        }
    )
    return base
