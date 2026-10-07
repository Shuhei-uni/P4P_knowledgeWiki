"""Assess every recorded film thickness, including crossings before a batch ends."""
from __future__ import annotations

import math
from typing import Mapping


def assess_thickness(history: Mapping[int, float], limit_m: float) -> dict:
    """A later decrease cannot clear a run that reached its declared limit."""
    if not history or not math.isfinite(limit_m) or limit_m <= 0:
        raise ValueError("A positive limit and a nonempty native history are required")
    ordered = sorted((int(n), float(h)) for n, h in history.items())
    if any(not math.isfinite(h) or h < 0 for _, h in ordered):
        raise ValueError("Native film thickness contains an invalid value")
    crossings = [(n, h) for n, h in ordered if h >= limit_m]
    return {
        "classification": "UNREALISTIC" if crossings else "THICKNESS_LIMIT_NOT_REACHED",
        "reason": "FILM_THICKNESS_LIMIT_REACHED" if crossings else None,
        "limit_m": limit_m,
        "peak_thickness_m": max(h for _, h in ordered),
        "first_crossing_native_iteration": crossings[0][0] if crossings else None,
        "first_crossing_thickness_m": crossings[0][1] if crossings else None,
        "history_native_range": [ordered[0][0], ordered[-1][0]],
        "samples_checked": len(ordered),
        "physical_validation": False,
    }
