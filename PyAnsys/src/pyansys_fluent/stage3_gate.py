#!/usr/bin/env python3
"""Deterministic offline evaluator for the 03A Stage-3 gate.

This module contains no Fluent connection or solver-control code.  It accepts
already-collected monitor series and returns JSON-serializable evidence for the
frozen ``stage3-gate-v1`` decision.  The execution agent remains responsible
for issuing exactly one blocking solve command before each assessment.

The Stage-3 authority specifies the thresholds but leaves the shared
representative-magnitude and variability definitions to the evaluator.  This
implementation freezes them as follows for every branch:

* representative magnitude = max(abs(first median), abs(final median), 1e-30)
* variability envelope = P95 - P05

Residual log envelopes require finite, strictly positive values.  Phase-routing
and inventory histories are required only when full Mixture equations are
active; carrier-only M1 intervals record them as not-required.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median
from typing import Any, Mapping, Sequence


WINDOW = 750
BLOCK = 250
EPSILON = 1.0e-30

TURBULENCE_RESIDUALS = ("k", "epsilon")
CARRIER_RESIDUALS = ("continuity", "x-velocity", "y-velocity", "z-velocity")

CORE_SIGNALS = (
    "03a_stage3_total_mixture_inlet-rplot",
    "03a_stage3_total_outlet-rplot",
    "03a_stage3_steam_outlet_total-rplot",
    "03a_stage3_brine_outlet_total-rplot",
    "03a_stage3_relative_mass_imbalance-rplot",
    "03a_stage3_brine_entry_static_pressure-rplot",
    "03a_stage3_brine_entry_total_pressure-rplot",
)

PHASE_SIGNALS = (
    "03a_stage3_routing_liquid_to_brine-rplot",
    "03a_stage3_routing_liquid_to_steam-rplot",
    "03a_stage3_routing_vapor_to_brine-rplot",
    "03a_stage3_routing_vapor_to_steam-rplot",
    "03a_stage3_inventory_total_liquid_mass-rplot",
    "03a_stage3_inventory_total_liquid_volume-rplot",
    "03a_stage3_inventory_y010_liquid_mass-rplot",
    "03a_stage3_inventory_y030_liquid_mass-rplot",
)


@dataclass(frozen=True)
class WindowStats:
    count: int
    median: float
    p05: float
    p95: float
    maximum: float
    envelope: float
    log_envelope: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "median": self.median,
            "p05": self.p05,
            "p95": self.p95,
            "maximum": self.maximum,
            "envelope": self.envelope,
            "log_envelope": self.log_envelope,
        }


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return float(ordered[lower] + weight * (ordered[upper] - ordered[lower]))


def _finite_values(values: Sequence[Any], *, positive: bool = False) -> list[float]:
    result: list[float] = []
    for value in values:
        number = float(value)
        if not math.isfinite(number) or (positive and number <= 0.0):
            raise ValueError(f"non-finite or invalid monitor value: {value!r}")
        result.append(number)
    return result


def stats(values: Sequence[Any], *, log_envelope: bool = False) -> WindowStats:
    finite = _finite_values(values, positive=log_envelope)
    if not finite:
        raise ValueError("empty monitor window")
    p05 = _percentile(finite, 0.05)
    p95 = _percentile(finite, 0.95)
    log_width = math.log10(p95 / p05) if log_envelope else None
    return WindowStats(
        count=len(finite),
        median=float(median(finite)),
        p05=p05,
        p95=p95,
        maximum=max(finite),
        envelope=p95 - p05,
        log_envelope=log_width,
    )


def _three_blocks(values: Sequence[Any], *, log_envelope: bool = False) -> tuple[WindowStats, WindowStats, WindowStats]:
    if len(values) != WINDOW:
        raise ValueError(f"stage3-gate-v1 requires exactly {WINDOW} values, got {len(values)}")
    return (
        stats(values[:BLOCK], log_envelope=log_envelope),
        stats(values[BLOCK : 2 * BLOCK], log_envelope=log_envelope),
        stats(values[2 * BLOCK :], log_envelope=log_envelope),
    )


def _series(report_data: Mapping[str, Any], name: str) -> Sequence[Any]:
    value = report_data.get(name)
    if value is None:
        raise KeyError(f"required monitor series missing: {name}")
    return value


def _turbulence_result(values: Sequence[Any]) -> dict[str, Any]:
    first, middle, final = _three_blocks(values, log_envelope=True)
    improvement_median = final.median <= 0.90 * first.median
    improvement_log = bool(
        final.log_envelope is not None
        and first.log_envelope is not None
        and final.log_envelope <= 0.85 * first.log_envelope
    )
    veto_median = final.median > 1.20 * first.median
    veto_p95 = final.p95 > 1.20 * first.p95
    passed = (improvement_median or improvement_log) and not (veto_median or veto_p95)
    return {
        "first": first.as_dict(),
        "middle": middle.as_dict(),
        "final": final.as_dict(),
        "improvement_median": improvement_median,
        "improvement_log_envelope": improvement_log,
        "veto_median_expansion": veto_median,
        "veto_p95_expansion": veto_p95,
        "pass": passed,
    }


def _carrier_result(values: Sequence[Any]) -> dict[str, Any]:
    first, middle, final = _three_blocks(values)
    expansion = final.median > 1.20 * first.median and final.p95 > 1.20 * first.p95
    return {
        "first": first.as_dict(),
        "middle": middle.as_dict(),
        "final": final.as_dict(),
        "non_expansion": not expansion,
        "pass": not expansion,
    }


def _core_result(values: Sequence[Any], *, relative_mass_imbalance: bool = False) -> dict[str, Any]:
    first, middle, final = _three_blocks(values)
    if relative_mass_imbalance:
        passed = final.median <= 1.20 * first.median
        return {
            "first": first.as_dict(),
            "middle": middle.as_dict(),
            "final": final.as_dict(),
            "mass_imbalance_non_deterioration": passed,
            "pass": passed,
        }
    representative = max(abs(first.median), abs(final.median), EPSILON)
    stationarity_change = abs(final.median - first.median) / representative
    variability_reduction = final.envelope <= 0.85 * first.envelope
    passed = stationarity_change <= 0.05 or variability_reduction
    return {
        "first": first.as_dict(),
        "middle": middle.as_dict(),
        "final": final.as_dict(),
        "representative_magnitude": representative,
        "relative_median_change": stationarity_change,
        "variability_reduction": (first.envelope - final.envelope) / max(abs(first.envelope), EPSILON),
        "stationary_or_less_variable": passed,
        "pass": passed,
    }


def evaluate_gate(
    *,
    residuals: Mapping[str, Sequence[Any]],
    reports: Mapping[str, Sequence[Any]],
    full_mixture_active: bool,
    stage: str,
    iteration_start: float | int,
    iteration_end: float | int,
) -> dict[str, Any]:
    """Evaluate one rolling 750-iteration ``stage3-gate-v1`` window."""

    turbulence: dict[str, Any] = {}
    for name in TURBULENCE_RESIDUALS:
        turbulence[name] = _turbulence_result(_series(residuals, name))

    carrier: dict[str, Any] = {}
    for name in CARRIER_RESIDUALS:
        carrier[name] = _carrier_result(_series(residuals, name))

    core: dict[str, Any] = {}
    for name in CORE_SIGNALS:
        core[name] = _core_result(
            _series(reports, name),
            relative_mass_imbalance=name == "03a_stage3_relative_mass_imbalance-rplot",
        )

    phase: dict[str, Any] = {}
    if full_mixture_active:
        for name in PHASE_SIGNALS:
            phase[name] = {
                "stats": _three_blocks(_series(reports, name))[2].as_dict(),
                "finite": True,
                "required": True,
            }
    else:
        phase = {name: {"required": False, "status": "not-required-carrier-only"} for name in PHASE_SIGNALS}

    turbulence_pass = all(item["pass"] for item in turbulence.values())
    carrier_pass = all(item["pass"] for item in carrier.values())
    core_pass = all(item["pass"] for item in core.values())
    phase_pass = all(item.get("finite", False) for item in phase.values() if item.get("required"))
    preferred_pass = turbulence_pass and carrier_pass and core_pass and phase_pass
    return {
        "gate_version": "stage3-gate-v1",
        "stage": stage,
        "iteration_start": iteration_start,
        "iteration_end": iteration_end,
        "window_iterations": WINDOW,
        "full_mixture_active": full_mixture_active,
        "thresholds": {
            "turbulence_median_improvement_fraction": 0.10,
            "turbulence_log_envelope_reduction_fraction": 0.15,
            "deterioration_veto_fraction": 0.20,
            "flow_pressure_relative_median_stationarity_fraction": 0.05,
            "flow_pressure_variability_reduction_fraction": 0.15,
            "mass_balance_deterioration_veto_fraction": 0.20,
        },
        "shared_definitions": {
            "representative_magnitude": "max(abs(first_median), abs(final_median), 1e-30)",
            "variability_envelope": "P95 - P05",
            "percentiles": "linear interpolation over sorted samples",
        },
        "turbulence": turbulence,
        "carrier_residuals": carrier,
        "project_core": core,
        "phase_and_inventory": phase,
        "components": {
            "turbulence_pass": turbulence_pass,
            "carrier_residual_pass": carrier_pass,
            "project_core_pass": core_pass,
            "phase_inventory_pass": phase_pass,
        },
        "preferred_pass": preferred_pass,
        "decision": "PREFERRED_PASS_ADVANCE" if preferred_pass else "REMAIN_OR_FORCE_AT_3000",
    }


def material_improvement(current: Mapping[str, Any], previous: Mapping[str, Any] | None) -> bool:
    """Return whether a final-condition assessment materially improved.

    The final-condition authority calls for a rolling comparison every 250
    iterations but does not add new thresholds.  This uses the same frozen
    turbulence improvement tests against the preceding rolling window and
    counts a reduction in any project-core variability or relative mass
    imbalance as material improvement.
    """

    if previous is None:
        return True
    for name in TURBULENCE_RESIDUALS:
        before = previous["turbulence"][name]["final"]
        after = current["turbulence"][name]["final"]
        if after["median"] <= 0.90 * before["median"]:
            return True
        before_log = before.get("log_envelope")
        after_log = after.get("log_envelope")
        if before_log is not None and after_log is not None and after_log <= 0.85 * before_log:
            return True
    for name, item in current["project_core"].items():
        previous_item = previous["project_core"][name]
        if item["final"]["envelope"] <= 0.85 * previous_item["final"]["envelope"]:
            return True
    return (
        current["project_core"]["03a_stage3_relative_mass_imbalance-rplot"]["final"]["median"]
        <= 0.90 * previous["project_core"]["03a_stage3_relative_mass_imbalance-rplot"]["final"]["median"]
    )
