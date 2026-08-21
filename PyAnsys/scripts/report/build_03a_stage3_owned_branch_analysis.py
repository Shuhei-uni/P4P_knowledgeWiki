#!/usr/bin/env python3
"""Build branch-by-branch Stage-3 evidence packages for F03, F07, and F09.

The script is offline and report-oriented.  It reads the preserved checkpoint
CSV and the already stitched native residual JSON, then writes one consistent
package per owned branch.  It does not connect to Fluent, load case/data
files, interpolate missing iterations, or edit the checkpoint packet.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Any, Callable, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = PROJECT_ROOT.parent
DEFAULT_CHECKPOINTS = (
    REPOSITORY_ROOT
    / "Setups"
    / "reports"
    / "full-geometry"
    / "mixture"
    / "steady-liquid-outlet"
    / "03a"
    / "03a-stage3-results-20260821-checkpoints.csv"
)
DEFAULT_RESIDUALS = (
    PROJECT_ROOT
    / "output"
    / "03a_stage3"
    / "residual-plots"
    / "03A-stage3-F03-F07-F09-scaled-residuals-stitched.json"
)
DEFAULT_REPORT_ROOT = (
    REPOSITORY_ROOT
    / "Setups"
    / "reports"
    / "full-geometry"
    / "mixture"
    / "steady-liquid-outlet"
    / "03a"
)
DEFAULT_REPORT_HISTORY_DIR = PROJECT_ROOT / "output" / "03a_stage3" / "owned-report-history"

OWNED_BRANCHES = ("F03", "F07", "F09")
BRANCH_COLORS = {"F03": "#2563eb", "F07": "#dc2626", "F09": "#059669"}
STAGE_ORDER = ("10%", "20%", "40%", "80%", "100%")
PRESSURE_REFERENCE_PA = 1_120_000.0
DISPLAY_RESIDUAL_CAP = 1.0e4

RAW_REPORT_NAMES = {
    "total_inlet": "03a_stage3_total_mixture_inlet-rfile",
    "total_outlet_signed": "03a_stage3_total_outlet-rfile",
    "brine_outlet_signed": "03a_stage3_brine_outlet_total-rfile",
    "relative_mass_imbalance": "03a_stage3_relative_mass_imbalance-rfile",
    "liquid_inlet": "03a_stage3_liquid_inlet_mass_flux-rfile",
    "vapour_inlet": "03a_stage3_vapor_inlet_mass_flux-rfile",
    "liquid_to_brine_signed": "03a_stage3_routing_liquid_to_brine-rfile",
    "liquid_to_steam_signed": "03a_stage3_routing_liquid_to_steam-rfile",
    "vapour_to_brine_signed": "03a_stage3_routing_vapor_to_brine-rfile",
    "vapour_to_steam_signed": "03a_stage3_routing_vapor_to_steam-rfile",
    "total_liquid_mass": "03a_stage3_inventory_total_liquid_mass-rfile",
    "total_liquid_volume": "03a_stage3_inventory_total_liquid_volume-rfile",
    "y010_liquid_mass": "03a_stage3_inventory_y010_liquid_mass-rfile",
    "y030_liquid_mass": "03a_stage3_inventory_y030_liquid_mass-rfile",
    "brine_entry_static_pressure": "03a_stage3_brine_entry_static_pressure-rfile",
    "brine_entry_total_pressure": "03a_stage3_brine_entry_total_pressure-rfile",
}

CHECKPOINT_HISTORY_COLUMNS = {
    "total_inlet_kg_s": "total_inlet_kg_s",
    "total_outlet_kg_s": "total_outlet_kg_s",
    "liquid_inlet_kg_s": "liquid_inlet_kg_s",
    "vapour_inlet_kg_s": "vapour_inlet_kg_s",
    "liquid_to_brine_kg_s": "liquid_to_brine_kg_s",
    "liquid_to_steam_kg_s": "liquid_to_steam_kg_s",
    "vapour_to_brine_kg_s": "vapour_to_brine_kg_s",
    "vapour_to_steam_kg_s": "vapour_to_steam_kg_s",
    "mass_imbalance_signed_pct": "mass_imbalance_signed_pct",
    "mass_imbalance_abs_pct": "mass_imbalance_abs_pct",
    "liquid_closure_pct": "liquid_closure_pct",
    "vapour_closure_pct": "vapour_closure_pct",
    "liquid_inventory_total_kg": "liquid_inventory_total_kg",
    "liquid_inventory_y030_kg": "liquid_inventory_y030_kg",
    "liquid_inventory_y010_kg": "liquid_inventory_y010_kg",
    "brine_entry_static_pressure_pa": "brine_entry_static_pressure_pa",
    "brine_entry_total_pressure_pa": "brine_entry_total_pressure_pa",
}

RESIDUAL_WINDOWS: dict[str, dict[str, tuple[int, int]]] = {
    "F03": {"100%": (4501, 5000)},
    "F07": {
        "10%": (2651, 3150),
        "20%": (5651, 6150),
        "40%": (8651, 9150),
        "80% failure tail": (9151, 9174),
    },
    "F09": {
        "10%": (2501, 3000),
        "20%": (5501, 6000),
        "40%": (8501, 9000),
        "80%": (11501, 12000),
        "100%": (14501, 15000),
    },
}

ORIGINAL_NUMERIC_COLUMNS = (
    "iteration",
    "load_percent",
    "momentum_urf",
    "total_inlet_kg_s",
    "total_outlet_kg_s",
    "liquid_inlet_kg_s",
    "vapour_inlet_kg_s",
    "liquid_to_brine_kg_s",
    "liquid_to_steam_kg_s",
    "vapour_to_brine_kg_s",
    "vapour_to_steam_kg_s",
    "mass_imbalance_signed_pct",
    "mass_imbalance_abs_pct",
    "liquid_closure_pct",
    "vapour_closure_pct",
    "liquid_inventory_total_kg",
    "liquid_inventory_y030_kg",
    "liquid_inventory_y010_kg",
    "brine_entry_static_pressure_pa",
    "brine_entry_total_pressure_pa",
    "brine_entry_pressure_margin_pa",
)
DERIVED_COLUMNS = (
    "load_label",
    "outlet_minus_inlet_kg_s",
    "liquid_to_brine_pct_of_liquid_inlet",
    "liquid_to_steam_pct_of_liquid_inlet",
    "vapour_to_brine_pct_of_vapour_inlet",
    "vapour_to_steam_pct_of_vapour_inlet",
    "liquid_inventory_y030_fraction_pct",
    "liquid_inventory_y010_fraction_pct",
    "brine_entry_static_margin_kpa",
    "brine_entry_total_margin_kpa",
)


def repo_relative(path: Path) -> str:
    """Return a portable repository-relative provenance path."""

    try:
        return path.resolve().relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def integer(value: Any) -> int | None:
    parsed = number(value)
    return int(parsed) if parsed is not None else None


def rounded(value: float | None, digits: int = 9) -> float | None:
    return round(value, digits) if value is not None else None


def ratio_percent(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0.0):
        return None
    return 100.0 * numerator / denominator


def add_derived_fields(row: dict[str, Any]) -> dict[str, Any]:
    load = integer(row.get("load_percent"))
    inlet = number(row.get("total_inlet_kg_s"))
    outlet = number(row.get("total_outlet_kg_s"))
    liquid_inlet = number(row.get("liquid_inlet_kg_s"))
    vapour_inlet = number(row.get("vapour_inlet_kg_s"))
    total_liquid = number(row.get("liquid_inventory_total_kg"))
    result = dict(row)
    result.update(
        {
            "iteration": integer(row.get("iteration")),
            "load_percent": load,
            "momentum_urf": number(row.get("momentum_urf")),
            "load_label": f"{load}%" if load is not None else None,
            "outlet_minus_inlet_kg_s": (
                rounded(outlet - inlet) if outlet is not None and inlet is not None else None
            ),
            "liquid_to_brine_pct_of_liquid_inlet": ratio_percent(
                number(row.get("liquid_to_brine_kg_s")), liquid_inlet
            ),
            "liquid_to_steam_pct_of_liquid_inlet": ratio_percent(
                number(row.get("liquid_to_steam_kg_s")), liquid_inlet
            ),
            "vapour_to_brine_pct_of_vapour_inlet": ratio_percent(
                number(row.get("vapour_to_brine_kg_s")), vapour_inlet
            ),
            "vapour_to_steam_pct_of_vapour_inlet": ratio_percent(
                number(row.get("vapour_to_steam_kg_s")), vapour_inlet
            ),
            "liquid_inventory_y030_fraction_pct": ratio_percent(
                number(row.get("liquid_inventory_y030_kg")), total_liquid
            ),
            "liquid_inventory_y010_fraction_pct": ratio_percent(
                number(row.get("liquid_inventory_y010_kg")), total_liquid
            ),
            "brine_entry_static_margin_kpa": (
                (number(row.get("brine_entry_static_pressure_pa")) - PRESSURE_REFERENCE_PA) / 1000.0
                if number(row.get("brine_entry_static_pressure_pa")) is not None
                else None
            ),
            "brine_entry_total_margin_kpa": (
                (number(row.get("brine_entry_total_pressure_pa")) - PRESSURE_REFERENCE_PA) / 1000.0
                if number(row.get("brine_entry_total_pressure_pa")) is not None
                else None
            ),
        }
    )
    for key in ORIGINAL_NUMERIC_COLUMNS:
        if key in result and key not in {"iteration", "load_percent"}:
            result[key] = number(result[key])
    return result


def load_checkpoints(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [
            add_derived_fields(row)
            for row in csv.DictReader(handle)
            if row.get("branch") in OWNED_BRANCHES
        ]
    return sorted(rows, key=lambda row: (row["branch"], row["iteration"] or 0))


def group_rows(rows: list[dict[str, Any]], branch: str) -> list[dict[str, Any]]:
    return sorted(
        [row for row in rows if row.get("branch") == branch],
        key=lambda row: row.get("iteration") or 0,
    )


def percentile(values: Iterable[float], fraction: float) -> float | None:
    ordered = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not ordered:
        return None
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] + weight * (ordered[upper] - ordered[lower])


def log_slope_per_1000(points: list[tuple[int, float]]) -> float | None:
    if len(points) < 2 or any(value <= 0.0 for _, value in points):
        return None
    xs = [float(point[0]) for point in points]
    ys = [math.log10(point[1]) for point in points]
    x_bar = statistics.mean(xs)
    y_bar = statistics.mean(ys)
    denominator = sum((x - x_bar) ** 2 for x in xs)
    if denominator == 0.0:
        return None
    slope = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denominator
    return slope * 1000.0


def trend_label(first_median: float | None, last_median: float | None) -> str:
    if first_median in (None, 0.0) or last_median is None:
        return "unavailable"
    ratio = last_median / first_median
    if ratio > 1.05:
        return "increasing"
    if ratio < 0.95:
        return "decreasing"
    return "approximately stationary"


def load_residuals(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_report_history(path: Path) -> dict[str, Any]:
    """Load one branch's recovered native Report File bundle."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    reports = payload.get("reports")
    if isinstance(reports, list):
        normalized: dict[str, Any] = {}
        for record in reports:
            if not isinstance(record, dict):
                continue
            name = str(
                record.get("monitor_name")
                or record.get("report_file_label")
                or record.get("report_definition")
                or "unknown-report"
            )
            normalized[name] = record
        payload["reports"] = normalized
        reports = normalized
    if not isinstance(reports, dict):
        raise ValueError(f"No report history mapping in {path}")
    if (
        payload.get("recovered_report_file_count") != payload.get("configured_report_file_count")
        or len(reports) < len(RAW_REPORT_NAMES)
    ):
        raise ValueError(
            f"Incomplete native report bundle {path}: "
            f"recovered={payload.get('recovered_report_file_count')}, reports={len(reports)}"
        )
    return payload


def newest_report_history(report_dir: Path, branch: str) -> Path:
    candidates = sorted(report_dir.glob(f"03a-stage3-{branch.lower()}-report-histories_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No recovered native report-history bundle for {branch} in {report_dir}")
    return candidates[-1]


def report_points(record: dict[str, Any]) -> tuple[list[int], list[float]]:
    iterations = [int(value) for value in record.get("iterations", [])]
    values = [float(value) for value in record.get("values", [])]
    if len(iterations) != len(values) or not iterations:
        raise ValueError("Report history has mismatched or empty iteration/value arrays")
    return iterations, values


def transformed_report_series(record: dict[str, Any], transform: str = "identity") -> dict[str, Any]:
    iterations, values = report_points(record)
    converted: list[float] = []
    for value in values:
        if transform == "negate":
            value = -value
        elif transform == "percent":
            value *= 100.0
        elif transform == "static-margin":
            value -= PRESSURE_REFERENCE_PA
        converted.append(value)
    return {"iterations": iterations, "values": converted}


def absolute_report_series(record: dict[str, Any]) -> dict[str, Any]:
    iterations, values = report_points(record)
    return {"iterations": iterations, "values": [abs(value) for value in values]}


def report_value_at(series: dict[str, Any], iteration: int) -> float | None:
    try:
        index = series["iterations"].index(iteration)
    except (KeyError, ValueError):
        return None
    return float(series["values"][index])


def canonical_report_history(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert signed Fluent report histories to checkpoint-compatible series."""

    reports = payload["reports"]

    def record(name: str) -> dict[str, Any]:
        return reports[RAW_REPORT_NAMES[name]]

    history: dict[str, Any] = {
        "total_inlet_kg_s": transformed_report_series(record("total_inlet")),
        "total_outlet_native_kg_s": transformed_report_series(record("total_outlet_signed"), "negate"),
        "total_outlet_net_magnitude_kg_s": absolute_report_series(record("total_outlet_signed")),
        "brine_outlet_total_kg_s": transformed_report_series(record("brine_outlet_signed"), "negate"),
        "native_relative_mass_imbalance_pct": transformed_report_series(
            record("relative_mass_imbalance"), "percent"
        ),
        "liquid_inlet_kg_s": transformed_report_series(record("liquid_inlet")),
        "vapour_inlet_kg_s": transformed_report_series(record("vapour_inlet")),
        "liquid_to_brine_kg_s": transformed_report_series(record("liquid_to_brine_signed"), "negate"),
        "liquid_to_steam_kg_s": transformed_report_series(record("liquid_to_steam_signed"), "negate"),
        "vapour_to_brine_kg_s": transformed_report_series(record("vapour_to_brine_signed"), "negate"),
        "vapour_to_steam_kg_s": transformed_report_series(record("vapour_to_steam_signed"), "negate"),
        "liquid_inventory_total_kg": transformed_report_series(record("total_liquid_mass")),
        "liquid_inventory_total_m3": transformed_report_series(record("total_liquid_volume")),
        "liquid_inventory_y010_kg": transformed_report_series(record("y010_liquid_mass")),
        "liquid_inventory_y030_kg": transformed_report_series(record("y030_liquid_mass")),
        "brine_entry_static_pressure_pa": transformed_report_series(record("brine_entry_static_pressure")),
        "brine_entry_total_pressure_pa": transformed_report_series(record("brine_entry_total_pressure")),
        "brine_entry_static_margin_kpa": transformed_report_series(
            record("brine_entry_static_pressure"), "static-margin"
        ),
        "brine_entry_total_margin_kpa": transformed_report_series(
            record("brine_entry_total_pressure"), "static-margin"
        ),
    }

    route_names = (
        "liquid_to_brine_kg_s",
        "liquid_to_steam_kg_s",
        "vapour_to_brine_kg_s",
        "vapour_to_steam_kg_s",
    )
    route_iterations = history[route_names[0]]["iterations"]
    if not all(history[name]["iterations"] == route_iterations for name in route_names):
        raise ValueError("Native routing report histories do not share a common iteration axis")
    route_magnitudes = [
        [abs(value) for value in history[name]["values"]]
        for name in route_names
    ]
    path_outlet = [
        sum(values[index] for values in route_magnitudes)
        for index in range(len(route_iterations))
    ]
    inlet = history["total_inlet_kg_s"]["values"]
    liquid_inlet = history["liquid_inlet_kg_s"]["values"]
    vapour_inlet = history["vapour_inlet_kg_s"]["values"]
    liquid_route = [
        route_magnitudes[0][index] + route_magnitudes[1][index]
        for index in range(len(route_iterations))
    ]
    vapour_route = [
        route_magnitudes[2][index] + route_magnitudes[3][index]
        for index in range(len(route_iterations))
    ]

    def percent_difference(numerator: float, denominator: float) -> float:
        return 100.0 * (numerator - denominator) / abs(denominator) if denominator else float("nan")

    history.update(
        {
            "total_outlet_kg_s": {"iterations": route_iterations, "values": path_outlet},
            "mass_imbalance_signed_pct": {
                "iterations": route_iterations,
                "values": [percent_difference(outlet, inlet_value) for outlet, inlet_value in zip(path_outlet, inlet)],
            },
            "mass_imbalance_abs_pct": {
                "iterations": route_iterations,
                "values": [abs(percent_difference(outlet, inlet_value)) for outlet, inlet_value in zip(path_outlet, inlet)],
            },
            "liquid_closure_pct": {
                "iterations": route_iterations,
                "values": [percent_difference(outlet, inlet_value) for outlet, inlet_value in zip(liquid_route, liquid_inlet)],
            },
            "vapour_closure_pct": {
                "iterations": route_iterations,
                "values": [percent_difference(outlet, inlet_value) for outlet, inlet_value in zip(vapour_route, vapour_inlet)],
            },
            "liquid_to_brine_pct_of_liquid_inlet": {
                "iterations": route_iterations,
                "values": [100.0 * value / inlet_value if inlet_value else float("nan") for value, inlet_value in zip(route_magnitudes[0], liquid_inlet)],
            },
            "liquid_to_steam_pct_of_liquid_inlet": {
                "iterations": route_iterations,
                "values": [100.0 * value / inlet_value if inlet_value else float("nan") for value, inlet_value in zip(route_magnitudes[1], liquid_inlet)],
            },
            "vapour_to_brine_pct_of_vapour_inlet": {
                "iterations": route_iterations,
                "values": [100.0 * value / inlet_value if inlet_value else float("nan") for value, inlet_value in zip(route_magnitudes[2], vapour_inlet)],
            },
            "vapour_to_steam_pct_of_vapour_inlet": {
                "iterations": route_iterations,
                "values": [100.0 * value / inlet_value if inlet_value else float("nan") for value, inlet_value in zip(route_magnitudes[3], vapour_inlet)],
            },
        }
    )
    total_liquid = history["liquid_inventory_total_kg"]["values"]
    history["liquid_inventory_y030_fraction_pct"] = {
        "iterations": route_iterations,
        "values": [100.0 * value / total if total else float("nan") for value, total in zip(history["liquid_inventory_y030_kg"]["values"], total_liquid)],
    }
    history["liquid_inventory_y010_fraction_pct"] = {
        "iterations": route_iterations,
        "values": [100.0 * value / total if total else float("nan") for value, total in zip(history["liquid_inventory_y010_kg"]["values"], total_liquid)],
    }
    return history


def residual_summary(residual_payload: dict[str, Any], branch: str) -> dict[str, Any]:
    branch_payload = residual_payload["branches"][branch]
    series = branch_payload["series"]
    summary: dict[str, Any] = {}
    for stage, (start, end) in RESIDUAL_WINDOWS[branch].items():
        failure_tail = "failure" in stage.lower()
        summary[stage] = {
            "iteration_window": [start, end],
            "failure_tail": failure_tail,
            "equations": {},
        }
        for equation in residual_payload["residual_order"]:
            points = [
                (int(iteration), float(value))
                for iteration, value in series.get(equation, [])
                if start <= int(iteration) <= end and float(value) > 0.0
            ]
            values = [value for _, value in points]
            midpoint = len(values) // 2
            first_half = values[:midpoint] if midpoint else values
            last_half = values[midpoint:] if midpoint else values
            first_median = statistics.median(first_half) if first_half else None
            last_median = statistics.median(last_half) if last_half else None
            descriptive_trend = (
                "failure escalation"
                if failure_tail and values and max(values) > max(values[0] * 10.0, 1.0)
                else trend_label(first_median, last_median)
            )
            summary[stage]["equations"][equation] = {
                "points": len(points),
                "first_iteration": points[0][0] if points else None,
                "last_iteration": points[-1][0] if points else None,
                "median": percentile(values, 0.50),
                "p05": percentile(values, 0.05),
                "p95": percentile(values, 0.95),
                "first_value": values[0] if values else None,
                "last_value": values[-1] if values else None,
                "log10_slope_per_1000_iterations": log_slope_per_1000(points),
                "late_to_early_median_ratio": (
                    last_median / first_median
                    if first_median not in (None, 0.0) and last_median is not None
                    else None
                ),
                "descriptive_trend": descriptive_trend,
            }
    return summary


def residual_metric(summary: dict[str, Any], stage: str, equation: str) -> float | None:
    return summary.get(stage, {}).get("equations", {}).get(equation, {}).get("median")


def history_window_values(
    history: dict[str, Any],
    column: str,
    start: int,
    end: int,
) -> list[float]:
    series = history.get(column, {})
    values = [
        float(value)
        for iteration, value in zip(series.get("iterations", []), series.get("values", []))
        if start <= int(iteration) <= end and math.isfinite(float(value))
    ]
    return values


def linear_slope(values: list[float], start: int, end: int) -> float | None:
    if len(values) < 2 or end <= start:
        return None
    step = (end - start) / max(len(values) - 1, 1)
    xs = [start + index * step for index in range(len(values))]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(values)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0.0:
        return None
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, values)) / denominator


def successful_terminal_window(branch: str) -> tuple[str, tuple[int, int]]:
    windows = [
        (label, window)
        for label, window in RESIDUAL_WINDOWS[branch].items()
        if "failure" not in label.lower()
    ]
    if not windows:
        raise ValueError(f"No successful residual window is defined for {branch}")
    return windows[-1]


def history_late_window_summary(
    branch: str,
    history: dict[str, Any],
    residual_payload: dict[str, Any],
) -> dict[str, Any]:
    stage, (start, end) = successful_terminal_window(branch)
    summary = residual_summary(residual_payload, branch)
    residual_stage = summary.get(stage, {})
    metrics: dict[str, Any] = {}
    for column in (
        "mass_imbalance_abs_pct",
        "total_outlet_kg_s",
        "brine_outlet_total_kg_s",
        "liquid_to_brine_kg_s",
        "liquid_inventory_total_kg",
        "liquid_inventory_y030_kg",
        "liquid_inventory_y010_kg",
        "brine_entry_static_margin_kpa",
        "brine_entry_total_margin_kpa",
    ):
        values = history_window_values(history, column, start, end)
        metrics[column] = {
            "points": len(values),
            "median": percentile(values, 0.50),
            "p05": percentile(values, 0.05),
            "p95": percentile(values, 0.95),
            "std": statistics.pstdev(values) if len(values) > 1 else (0.0 if values else None),
            "slope_per_iteration": linear_slope(values, start, end),
        }
    return {
        "status": "derived_late_window",
        "window_basis": "last 500 native Report File points of the last completed load stage",
        "stage": stage,
        "iteration_window": [start, end],
        "history_points": len(history_window_values(history, "total_inlet_kg_s", start, end)),
        "metrics": metrics,
        "residuals": {
            equation: {
                "median": values.get("median"),
                "p95": values.get("p95"),
                "log10_slope_per_1000_iterations": values.get("log10_slope_per_1000_iterations"),
            }
            for equation, values in residual_stage.get("equations", {}).items()
        },
        "failure_tail_retained_separately": any(
            "failure" in label.lower() for label in RESIDUAL_WINDOWS[branch]
        ),
    }


def checkpoint_history_validation(
    rows: list[dict[str, Any]],
    history: dict[str, Any],
) -> list[dict[str, Any]]:
    validation: list[dict[str, Any]] = []
    route_columns = {
        "liquid_to_brine_kg_s",
        "liquid_to_steam_kg_s",
        "vapour_to_brine_kg_s",
        "vapour_to_steam_kg_s",
    }
    for row in rows:
        iteration = int(row["iteration"])
        for column, history_key in CHECKPOINT_HISTORY_COLUMNS.items():
            expected = number(row.get(column))
            actual = report_value_at(history.get(history_key, {}), iteration)
            compared = abs(actual) if actual is not None and column in route_columns else actual
            if actual is None or expected is None:
                status = "unavailable"
                difference = None
                tolerance = None
            else:
                difference = compared - expected
                tolerance = max(1.0e-3, abs(expected) * 1.0e-5)
                status = "match" if abs(difference) <= tolerance else "mismatch"
            validation.append(
                {
                    "branch": row["branch"],
                    "iteration": iteration,
                    "load_percent": row.get("load_percent"),
                    "metric": column,
                    "expected_checkpoint": expected,
                    "extracted_history": actual,
                    "extracted_for_checkpoint": compared,
                    "difference": difference,
                    "tolerance": tolerance,
                    "status": status,
                }
            )
    return validation


def terminal_stage(rows: list[dict[str, Any]], branch: str) -> str | None:
    branch_rows = group_rows(rows, branch)
    return branch_rows[-1].get("load_label") if branch_rows else None


def late_window_summary(
    rows: list[dict[str, Any]],
    residual_payload: dict[str, Any],
    branch: str,
    history: dict[str, Any],
) -> dict[str, Any]:
    branch_rows = group_rows(rows, branch)
    endpoint = branch_rows[-1] if branch_rows else {}
    stage = terminal_stage(rows, branch)
    summary = residual_summary(residual_payload, branch)
    equations = summary.get(stage or "", {}).get("equations", {})
    late_window = history_late_window_summary(branch, history, residual_payload)
    late_metrics = late_window["metrics"]
    return {
        "branch": branch,
        "terminal_load": stage,
        "terminal_iteration": endpoint.get("iteration"),
        "late_window_stage": late_window["stage"],
        "late_window_iterations": late_window["iteration_window"],
        "late_window_points": late_window["history_points"],
        "late_abs_imbalance_median_pct": late_metrics["mass_imbalance_abs_pct"]["median"],
        "late_abs_imbalance_p95_pct": late_metrics["mass_imbalance_abs_pct"]["p95"],
        "late_liquid_inventory_median_kg": late_metrics["liquid_inventory_total_kg"]["median"],
        "late_liquid_inventory_std_kg": late_metrics["liquid_inventory_total_kg"]["std"],
        "late_liquid_inventory_slope_kg_per_iteration": late_metrics["liquid_inventory_total_kg"]["slope_per_iteration"],
        "late_static_margin_median_kpa": late_metrics["brine_entry_static_margin_kpa"]["median"],
        "late_brine_flow_median_kg_s": late_metrics["brine_outlet_total_kg_s"]["median"],
        "endpoint_abs_imbalance_pct": endpoint.get("mass_imbalance_abs_pct"),
        "endpoint_total_liquid_kg": endpoint.get("liquid_inventory_total_kg"),
        "endpoint_static_margin_kpa": endpoint.get("brine_entry_static_margin_kpa"),
        "continuity_median": equations.get("continuity", {}).get("median"),
        "continuity_p95": equations.get("continuity", {}).get("p95"),
        "k_median": equations.get("k", {}).get("median"),
        "epsilon_median": equations.get("epsilon", {}).get("median"),
        "vf_median": equations.get("vf-phase-2", {}).get("median"),
        "failure_at_terminal": bool(summary.get(stage or "", {}).get("failure_tail")),
        "history_metrics": late_window,
    }


def write_owned_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "branch",
        "run_stamp",
        *ORIGINAL_NUMERIC_COLUMNS,
        *DERIVED_COLUMNS,
        "solver_state",
        "checkpoint_case",
        "checkpoint_data",
        "evidence_status",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_rows_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def import_plotting():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def style_axis(axis: Any, *, xlabel: str | None = None, ylabel: str | None = None) -> None:
    axis.grid(True, which="major", alpha=0.25)
    axis.grid(True, which="minor", alpha=0.12, linestyle=":")
    if xlabel:
        axis.set_xlabel(xlabel)
    if ylabel:
        axis.set_ylabel(ylabel)


def branch_stage_boundaries(branch: str, residual_payload: dict[str, Any]) -> list[tuple[int, str]]:
    return [
        (int(iteration), str(label))
        for iteration, label in residual_payload["branches"][branch].get("stage_boundaries", [])
    ]


def add_boundary_lines(
    axis: Any,
    branch: str,
    residual_payload: dict[str, Any],
    *,
    show_labels: bool = True,
) -> None:
    for iteration, label in branch_stage_boundaries(branch, residual_payload):
        axis.axvline(iteration, color="#6b7280", linestyle="--", linewidth=0.7, alpha=0.65)
        if show_labels:
            axis.text(
                iteration,
                0.98,
                label,
                transform=axis.get_xaxis_transform(),
                rotation=90,
                va="top",
                ha="right",
                fontsize=7,
                color="#4b5563",
            )


def split_contiguous(points: list[tuple[int, float]]) -> list[list[tuple[int, float]]]:
    segments: list[list[tuple[int, float]]] = []
    current: list[tuple[int, float]] = []
    previous: int | None = None
    for point in points:
        if previous is not None and point[0] != previous + 1:
            if current:
                segments.append(current)
            current = []
        current.append(point)
        previous = point[0]
    if current:
        segments.append(current)
    return segments


def build_residuals(
    branch: str,
    residual_payload: dict[str, Any],
    output: Path,
) -> None:
    plt = import_plotting()
    equations = residual_payload["residual_order"]
    figure, axes = plt.subplots(4, 2, figsize=(14, 13), sharex=True, constrained_layout=True)
    axes_flat = list(axes.flat)
    for index, equation in enumerate(equations):
        axis = axes_flat[index]
        points = [
            (int(iteration), float(value))
            for iteration, value in residual_payload["branches"][branch]["series"].get(equation, [])
            if float(value) > 0.0 and math.isfinite(float(value))
        ]
        for segment in split_contiguous(points):
            axis.plot(
                [point[0] for point in segment],
                [min(point[1], DISPLAY_RESIDUAL_CAP) for point in segment],
                color=BRANCH_COLORS[branch],
                linewidth=0.65,
            )
        axis.set_yscale("log")
        axis.set_ylim(bottom=1.0e-12, top=DISPLAY_RESIDUAL_CAP * 1.25)
        axis.set_title(equation, loc="left", fontweight="bold")
        axis.set_ylabel("scaled residual")
        style_axis(axis)
        add_boundary_lines(axis, branch, residual_payload, show_labels=index == 0)
    axes_flat[-1].axis("off")
    axes_flat[-2].axis("off")
    axes_flat[-1].text(
        0.02,
        0.75,
        "Each panel is one native residual equation.\n"
        "Gaps are left as gaps; no interpolation was applied.\n"
        f"Display cap: {DISPLAY_RESIDUAL_CAP:.0e}; full values remain in the JSON.",
        transform=axes_flat[-1].transAxes,
        fontsize=9,
        va="top",
    )
    axes_flat[-2].text(
        0.02,
        0.75,
        residual_payload["branches"][branch].get("coverage", "coverage not stated"),
        transform=axes_flat[-2].transAxes,
        fontsize=9,
        va="top",
        wrap=True,
    )
    axes_flat[-3].set_xlabel("Cumulative Fluent native iteration")
    figure.suptitle(f"03A Stage 3 — {branch} residual histories", fontsize=16, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def plot_checkpoint_series(axis: Any, rows: list[dict[str, Any]], column: str, *, label: str) -> None:
    values = [(row["iteration"], row[column]) for row in rows if row.get(column) is not None]
    if values:
        axis.plot(
            [value[0] for value in values],
            [value[1] for value in values],
            marker="o",
            markersize=5,
            linewidth=1.0,
            color=BRANCH_COLORS[rows[0]["branch"]],
            label=label,
        )


def plot_history_series(
    axis: Any,
    history: dict[str, Any],
    column: str,
    *,
    label: str,
    linestyle: str = "-",
    linewidth: float = 0.9,
    alpha: float = 0.9,
) -> None:
    series = history.get(column, {})
    points = [
        (int(iteration), float(value))
        for iteration, value in zip(series.get("iterations", []), series.get("values", []))
        if math.isfinite(float(value))
    ]
    if points:
        axis.plot(
            [point[0] for point in points],
            [point[1] for point in points],
            color=BRANCH_COLORS.get(str(history.get("branch")), "#2563eb"),
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            label=label,
        )


def plot_history_series_colored(
    axis: Any,
    history: dict[str, Any],
    column: str,
    *,
    color: str,
    label: str,
    linestyle: str = "-",
    linewidth: float = 0.9,
    alpha: float = 0.9,
) -> None:
    series = history.get(column, {})
    points = [
        (int(iteration), float(value))
        for iteration, value in zip(series.get("iterations", []), series.get("values", []))
        if math.isfinite(float(value))
    ]
    if points:
        axis.plot(
            [point[0] for point in points],
            [point[1] for point in points],
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            label=label,
        )


def history_sample_points(
    history: dict[str, Any],
    x_column: str,
    y_column: str,
    *,
    maximum: int = 600,
    end_iteration: int | None = None,
) -> list[tuple[int, float, float]]:
    x_series = history.get(x_column, {})
    y_series = history.get(y_column, {})
    if x_series.get("iterations") != y_series.get("iterations"):
        return []
    points = [
        (int(iteration), float(x_value), float(y_value))
        for iteration, x_value, y_value in zip(
            x_series.get("iterations", []),
            x_series.get("values", []),
            y_series.get("values", []),
        )
        if end_iteration is None or int(iteration) <= end_iteration
        if math.isfinite(float(x_value)) and math.isfinite(float(y_value))
    ]
    if len(points) <= maximum:
        return points
    stride = math.ceil(len(points) / maximum)
    sampled = points[::stride]
    if points[-1] not in sampled:
        sampled.append(points[-1])
    return sampled


def build_physical(
    branch: str,
    rows: list[dict[str, Any]],
    residual_payload: dict[str, Any],
    history: dict[str, Any],
    output: Path,
) -> None:
    plt = import_plotting()
    figure, axes = plt.subplots(3, 1, figsize=(12, 11), sharex=True, constrained_layout=True)
    branch_rows = group_rows(rows, branch)
    color = BRANCH_COLORS[branch]
    plot_history_series_colored(axes[0], history, "total_inlet_kg_s", color=color, label="native inlet history")
    plot_history_series_colored(axes[0], history, "total_outlet_kg_s", color="#b91c1c", label="native outlet path-magnitude history")
    plot_checkpoint_series(axes[0], branch_rows, "total_inlet_kg_s", label="checkpoint inlet")
    plot_checkpoint_series(axes[0], branch_rows, "total_outlet_kg_s", label="checkpoint outlet")
    axes[0].set_title("Total mixture inlet and outlet mass flow", loc="left", fontweight="bold")
    axes[0].set_ylabel("Mass flow (kg/s)")
    axes[0].legend(frameon=False, fontsize=8, ncol=2)

    plot_history_series_colored(axes[1], history, "mass_imbalance_abs_pct", color="#7c3aed", label="path-magnitude imbalance")
    plot_history_series_colored(
        axes[1],
        history,
        "native_relative_mass_imbalance_pct",
        color="#64748b",
        label="native Report File imbalance",
        linestyle=":",
        alpha=0.75,
    )
    plot_checkpoint_series(axes[1], branch_rows, "mass_imbalance_abs_pct", label="checkpoint")
    axes[1].set_yscale("log")
    axes[1].set_title("Relative total mass imbalance", loc="left", fontweight="bold")
    axes[1].set_ylabel("Absolute imbalance (%)")
    axes[1].legend(frameon=False, fontsize=8, ncol=2)
    plot_history_series_colored(axes[2], history, "liquid_inventory_total_kg", color="#059669", label="native total liquid history")
    plot_checkpoint_series(axes[2], branch_rows, "liquid_inventory_total_kg", label="checkpoint")
    axes[2].set_yscale("log")
    axes[2].set_title("Total liquid inventory", loc="left", fontweight="bold")
    axes[2].set_ylabel("Liquid inventory (kg)")
    axes[2].legend(frameon=False, fontsize=8)
    axes[2].set_xlabel("Cumulative Fluent native iteration")
    for axis in axes:
        style_axis(axis)
        add_boundary_lines(axis, branch, residual_payload)
    figure.suptitle(f"03A Stage 3 — {branch} native physical histories", fontsize=16, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def build_phase(
    branch: str,
    rows: list[dict[str, Any]],
    residual_payload: dict[str, Any],
    history: dict[str, Any],
    output: Path,
) -> None:
    plt = import_plotting()
    branch_rows = group_rows(rows, branch)
    columns = (
        ("liquid_to_brine_pct_of_liquid_inlet", "Liquid → brine (% of liquid inlet)"),
        ("liquid_to_steam_pct_of_liquid_inlet", "Liquid → steam (% of liquid inlet)"),
        ("vapour_to_brine_pct_of_vapour_inlet", "Vapour → brine (% of vapour inlet)"),
        ("vapour_to_steam_pct_of_vapour_inlet", "Vapour → steam (% of vapour inlet)"),
    )
    figure, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, constrained_layout=True)
    for axis, (column, title) in zip(axes.flat, columns):
        plot_history_series_colored(
            axis,
            history,
            column,
            color=BRANCH_COLORS[branch],
            label="native routing history",
        )
        plot_checkpoint_series(axis, branch_rows, column, label="checkpoint")
        axis.axhline(100.0, color="#6b7280", linestyle=":", linewidth=0.8)
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_ylabel("Percent")
        axis.legend(frameon=False, fontsize=8)
        style_axis(axis)
        add_boundary_lines(axis, branch, residual_payload)
    axes[1, 0].set_xlabel("Cumulative Fluent native iteration")
    axes[1, 1].set_xlabel("Cumulative Fluent native iteration")
    figure.suptitle(f"03A Stage 3 — {branch} phase routing", fontsize=16, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def build_liquid_distribution(
    branch: str,
    rows: list[dict[str, Any]],
    residual_payload: dict[str, Any],
    history: dict[str, Any],
    output: Path,
) -> None:
    plt = import_plotting()
    branch_rows = group_rows(rows, branch)
    figure, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, constrained_layout=True)
    for column, label, marker in (
        ("liquid_inventory_total_kg", "Total liquid", "o"),
        ("liquid_inventory_y030_kg", "Y030 liquid", "s"),
        ("liquid_inventory_y010_kg", "Y010 liquid", "^"),
    ):
        plot_history_series_colored(
            axes[0], history, column, color=BRANCH_COLORS[branch], label=f"{label} history"
        )
        values = [(row["iteration"], row[column]) for row in branch_rows if row.get(column) is not None]
        if values:
            axes[0].plot(
                [value[0] for value in values],
                [value[1] for value in values],
                marker=marker,
                markersize=5,
                linewidth=0.0,
                label=f"{label} checkpoint",
                color=BRANCH_COLORS[branch],
            )
    axes[0].set_title("Total/Y030/Y010 liquid mass", loc="left", fontweight="bold")
    axes[0].set_ylabel("Liquid mass (kg)")
    axes[0].legend(frameon=False)
    for column, label, marker, linestyle in (
        ("liquid_inventory_y030_fraction_pct", "Y030 / total", "s", "-"),
        ("liquid_inventory_y010_fraction_pct", "Y010 / total", "^", "--"),
    ):
        plot_history_series_colored(
            axes[1],
            history,
            column,
            color=BRANCH_COLORS[branch],
            label=f"{label} history",
            linestyle=linestyle,
        )
        values = [(row["iteration"], row[column]) for row in branch_rows if row.get(column) is not None]
        if values:
            axes[1].plot(
                [value[0] for value in values],
                [value[1] for value in values],
                marker=marker,
                markersize=5,
                linewidth=0.0,
                label=f"{label} checkpoint",
                color=BRANCH_COLORS[branch],
            )
    axes[1].set_title("Y030/Y010 fraction of total liquid", loc="left", fontweight="bold")
    axes[1].set_ylabel("Fraction (%)")
    axes[1].set_xlabel("Cumulative Fluent native iteration")
    axes[1].legend(frameon=False)
    for axis in axes:
        style_axis(axis)
        add_boundary_lines(axis, branch, residual_payload)
    figure.suptitle(f"03A Stage 3 — {branch} liquid distribution", fontsize=16, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def build_brine(
    branch: str,
    rows: list[dict[str, Any]],
    residual_payload: dict[str, Any],
    history: dict[str, Any],
    output: Path,
) -> None:
    plt = import_plotting()
    branch_rows = group_rows(rows, branch)
    figure, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, constrained_layout=True)
    for column, label, linestyle in (
        ("brine_entry_static_margin_kpa", "static margin", "-"),
        ("brine_entry_total_margin_kpa", "total margin", "--"),
    ):
        plot_history_series_colored(
            axes[0],
            history,
            column,
            color=BRANCH_COLORS[branch],
            label=f"{label} history",
            linestyle=linestyle,
        )
        values = [(row["iteration"], row[column]) for row in branch_rows if row.get(column) is not None]
        if values:
            axes[0].plot(
                [value[0] for value in values],
                [value[1] for value in values],
                marker="o",
                markersize=5,
                linewidth=0.0,
                label=f"{label} checkpoint",
                color=BRANCH_COLORS[branch],
            )
    axes[0].axhline(0.0, color="#6b7280", linestyle=":", linewidth=0.8)
    axes[0].set_title("Brine-entry pressure margin", loc="left", fontweight="bold")
    axes[0].set_ylabel("Margin from 1.120 MPa (kPa)")
    axes[0].legend(frameon=False, fontsize=8, ncol=2)
    for column, label, marker, linestyle in (
        ("brine_outlet_total_kg_s", "total brine outlet", "s", "-"),
        ("liquid_to_brine_kg_s", "liquid → brine", "^", "--"),
    ):
        plot_history_series_colored(
            axes[1],
            history,
            column,
            color=BRANCH_COLORS[branch],
            label=f"{label} history",
            linestyle=linestyle,
        )
        checkpoint_column = "total_outlet_kg_s" if column == "brine_outlet_total_kg_s" else column
        values = [(row["iteration"], row[checkpoint_column]) for row in branch_rows if row.get(checkpoint_column) is not None]
        if values:
            axes[1].plot(
                [value[0] for value in values],
                [value[1] for value in values],
                marker=marker,
                markersize=5,
                linewidth=0.0,
                label=f"{label} checkpoint",
                color=BRANCH_COLORS[branch],
            )
    axes[1].set_title("Brine-flow response associated with the pressure readback", loc="left", fontweight="bold")
    axes[1].set_ylabel("Mass flow (kg/s)")
    axes[1].set_xlabel("Cumulative Fluent native iteration")
    axes[1].legend(frameon=False, fontsize=8, ncol=2)
    for axis in axes:
        style_axis(axis)
        add_boundary_lines(axis, branch, residual_payload)
    figure.suptitle(f"03A Stage 3 — {branch} brine-entry hydraulic evidence", fontsize=16, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def build_ramp(
    branch: str,
    rows: list[dict[str, Any]],
    residual_payload: dict[str, Any],
    history: dict[str, Any],
    output: Path,
) -> None:
    plt = import_plotting()
    summary = residual_summary(residual_payload, branch)
    figure, axes = plt.subplots(2, 3, figsize=(13, 8), constrained_layout=True)
    metrics = (
        ("mass_imbalance_abs_pct", "Absolute imbalance (%)"),
        ("liquid_inventory_total_kg", "Total liquid (kg)"),
        ("brine_entry_static_margin_kpa", "Static margin (kPa)"),
        ("total_outlet_kg_s", "Total outlet (kg/s)"),
    )
    for axis, (column, title) in zip(axes.flat, metrics):
        if column in {"mass_imbalance_abs_pct", "liquid_inventory_total_kg"}:
            axis.set_yscale("log")
        stage_points = []
        for stage, (start, end) in RESIDUAL_WINDOWS[branch].items():
            values = history_window_values(history, column, start, end)
            if values:
                stage_points.append((int(stage.split("%", 1)[0]), percentile(values, 0.50), stage))
        axis.plot(
            [point[0] for point in stage_points],
            [point[1] for point in stage_points],
            marker="o",
            linewidth=1.0,
            color=BRANCH_COLORS[branch],
            label="late-window native median",
        )
        checkpoint_column = column
        checkpoint_rows = [
            row for row in group_rows(rows, branch)
            if row.get("load_label") in STAGE_ORDER and row.get(checkpoint_column) is not None
        ]
        if checkpoint_rows:
            axis.plot(
                [row["load_percent"] for row in checkpoint_rows],
                [row[checkpoint_column] for row in checkpoint_rows],
                marker="x",
                linestyle="none",
                color="#111827",
                label="checkpoint",
            )
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_xticks([10, 20, 40, 80, 100])
        axis.tick_params(axis="x", labelrotation=45)
        axis.set_xlabel("Inlet loading (%)")
        axis.legend(frameon=False, fontsize=7)
        style_axis(axis)
    if any("failure" in stage.lower() for stage in RESIDUAL_WINDOWS[branch]):
        axes.flat[2].set_yscale("symlog", linthresh=100.0)
        axes.flat[2].text(
            0.02,
            0.03,
            "80% point = numerical-failure tail",
            transform=axes.flat[2].transAxes,
            fontsize=8,
            color="#7f1d1d",
        )
    for axis, equation, title in (
        (axes.flat[4], "continuity", "Late continuity median"),
        (axes.flat[5], "epsilon", "Late epsilon median"),
    ):
        stages = [stage for stage in STAGE_ORDER if stage in summary]
        values = [residual_metric(summary, stage, equation) for stage in stages]
        axis.plot(
            [int(stage[:-1]) for stage in stages],
            values,
            marker="o",
            linewidth=1.0,
            color=BRANCH_COLORS[branch],
        )
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_xticks([10, 20, 40, 80, 100])
        axis.tick_params(axis="x", labelrotation=45)
        axis.set_xlabel("Inlet loading (%)")
        style_axis(axis)
    for axis in axes.flat:
        if not axis.get_legend_handles_labels()[0]:
            continue
    figure.suptitle(f"03A Stage 3 — {branch} inlet-loading response", fontsize=16, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def stage_for_row(row: dict[str, Any]) -> str:
    return row.get("load_label") or "unknown"


def build_cross_plots(
    branch: str,
    rows: list[dict[str, Any]],
    residual_payload: dict[str, Any],
    history: dict[str, Any],
    output: Path,
) -> None:
    plt = import_plotting()
    branch_rows = group_rows(rows, branch)
    summary = residual_summary(residual_payload, branch)
    figure, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    color = BRANCH_COLORS[branch]
    successful_end = successful_terminal_window(branch)[1][1]
    failure_tail_excluded = any("failure" in label.lower() for label in RESIDUAL_WINDOWS[branch])
    history_label = (
        "successful native history samples"
        if failure_tail_excluded
        else "native history samples"
    )

    inventory_imbalance = history_sample_points(
        history,
        "liquid_inventory_total_kg",
        "mass_imbalance_abs_pct",
        end_iteration=successful_end,
    )
    axes[0, 0].scatter(
        [point[1] for point in inventory_imbalance if point[1] > 0.0],
        [max(point[2], 1.0e-9) for point in inventory_imbalance if point[1] > 0.0],
        color=color,
        s=10,
        alpha=0.45,
        label=history_label,
    )
    axes[0, 0].scatter(
        [row["liquid_inventory_total_kg"] for row in branch_rows],
        [max(row["mass_imbalance_abs_pct"], 1.0e-9) for row in branch_rows],
        color="#111827",
        marker="x",
        s=35,
        label="checkpoint",
    )
    axes[0, 0].set_xscale("log")
    axes[0, 0].set_yscale("log")
    axes[0, 0].set_xlabel("Total liquid inventory (kg)")
    axes[0, 0].set_ylabel("Absolute imbalance (%)")
    axes[0, 0].set_title("Inventory vs mass imbalance", loc="left", fontweight="bold")
    axes[0, 0].legend(frameon=False, fontsize=8)

    pressure_brine = history_sample_points(
        history,
        "brine_entry_static_margin_kpa",
        "liquid_to_brine_kg_s",
        end_iteration=successful_end,
    )
    axes[0, 1].scatter(
        [point[1] for point in pressure_brine],
        [point[2] for point in pressure_brine],
        color=color,
        s=10,
        alpha=0.45,
        label=history_label,
    )
    axes[0, 1].scatter(
        [row["brine_entry_static_margin_kpa"] for row in branch_rows],
        [row["liquid_to_brine_kg_s"] for row in branch_rows],
        color="#111827",
        marker="x",
        s=35,
        label="checkpoint liquid → brine",
    )
    axes[0, 1].axvline(0.0, color="#6b7280", linestyle=":", linewidth=0.8)
    axes[0, 1].set_xlabel("Static pressure margin (kPa)")
    axes[0, 1].set_ylabel("Liquid → brine (kg/s)")
    axes[0, 1].set_title("Pressure margin vs brine flow", loc="left", fontweight="bold")
    axes[0, 1].legend(frameon=False, fontsize=8)

    brine_inventory = history_sample_points(
        history,
        "liquid_to_brine_kg_s",
        "liquid_inventory_total_kg",
        end_iteration=successful_end,
    )
    axes[1, 0].scatter(
        [point[1] for point in brine_inventory if point[1] > 0.0],
        [point[2] for point in brine_inventory if point[1] > 0.0],
        color=color,
        s=10,
        alpha=0.45,
        label=history_label,
    )
    axes[1, 0].scatter(
        [row["liquid_to_brine_kg_s"] for row in branch_rows],
        [row["liquid_inventory_total_kg"] for row in branch_rows],
        color="#111827",
        marker="x",
        s=35,
        label="checkpoint",
    )
    axes[1, 0].set_xscale("log")
    axes[1, 0].set_yscale("log")
    axes[1, 0].set_xlabel("Liquid → brine (kg/s)")
    axes[1, 0].set_ylabel("Total liquid inventory (kg)")
    axes[1, 0].set_title("Brine flow vs liquid inventory", loc="left", fontweight="bold")
    axes[1, 0].legend(frameon=False, fontsize=8)

    endpoint_metrics: list[tuple[float, float]] = []
    for row in branch_rows:
        stage = stage_for_row(row)
        continuity = residual_metric(summary, stage, "continuity")
        if continuity is not None:
            endpoint_metrics.append((continuity, max(row["mass_imbalance_abs_pct"], 1.0e-9)))
    if endpoint_metrics:
        axes[1, 1].scatter(
            [point[0] for point in endpoint_metrics],
            [point[1] for point in endpoint_metrics],
            color=color,
            s=45,
        )
    axes[1, 1].set_xscale("log")
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_xlabel("Late continuity median")
    axes[1, 1].set_ylabel("Endpoint absolute imbalance (%)")
    axes[1, 1].set_title("Late residual vs endpoint imbalance", loc="left", fontweight="bold")

    for axis in axes.flat:
        style_axis(axis)
    label_offsets = {
        "10%": (5, 7),
        "20%": (5, -12),
        "40%": (5, 7),
        "80%": (5, -12),
        "100%": (5, 10),
    }
    for index, row in enumerate(branch_rows):
        label = stage_for_row(row)
        offset = label_offsets.get(label, (5, 5))
        axes[0, 0].annotate(
            label,
            (row["liquid_inventory_total_kg"], max(row["mass_imbalance_abs_pct"], 1.0e-9)),
            xytext=offset,
            textcoords="offset points",
            fontsize=8,
        )
        axes[0, 1].annotate(
            label,
            (row["brine_entry_static_margin_kpa"], row["liquid_to_brine_kg_s"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=8,
        )
        axes[1, 0].annotate(
            label,
            (row["liquid_to_brine_kg_s"], row["liquid_inventory_total_kg"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=8,
        )
        if index < len(endpoint_metrics):
            axes[1, 1].annotate(
                label,
                endpoint_metrics[index],
                xytext=offset,
                textcoords="offset points",
                fontsize=8,
            )
    if failure_tail_excluded:
        axes[0, 0].text(
            0.03,
            0.96,
            "80% numerical-failure tail omitted from continuous scale",
            transform=axes[0, 0].transAxes,
            ha="left",
            va="top",
            fontsize=8,
            color="#7f1d1d",
        )
    figure.suptitle(f"03A Stage 3 — {branch} branch-specific cross-plots", fontsize=16, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def branch_payload(
    branch: str,
    checkpoint_path: Path,
    residual_path: Path,
    report_history_path: Path,
    rows: list[dict[str, Any]],
    residual_payload: dict[str, Any],
    report_history_payload: dict[str, Any],
    history: dict[str, Any],
    validation: list[dict[str, Any]],
    figures: list[str],
) -> dict[str, Any]:
    validation_counts = {
        "rows": len(validation),
        "matches": sum(item["status"] == "match" for item in validation),
        "mismatches": sum(item["status"] == "mismatch" for item in validation),
        "unavailable": sum(item["status"] == "unavailable" for item in validation),
    }
    return {
        "kind": "03a_stage3_owned_branch_analysis",
        "branch": branch,
        "scope": "F03/F07/F09 only",
        "sources": {
            "checkpoint_csv": {"path": repo_relative(checkpoint_path), "sha256": sha256(checkpoint_path)},
            "stitched_residual_json": {"path": repo_relative(residual_path), "sha256": sha256(residual_path)},
            "native_report_history_json": {"path": repo_relative(report_history_path), "sha256": sha256(report_history_path)},
        },
        "native_report_history_status": {
            "status": "complete",
            "meaning": "All configured Stage-3 native Report File histories were recovered and parsed for this branch.",
            "remote_report_dir": report_history_payload.get("remote_report_dir"),
            "report_filename_suffix": report_history_payload.get("report_filename_suffix"),
            "configured_report_file_count": report_history_payload.get("configured_report_file_count"),
            "recovered_report_file_count": report_history_payload.get("recovered_report_file_count"),
            "points_by_report": {
                str(record.get("monitor_name") or record.get("report_definition")): record.get("points")
                for record in report_history_payload.get("reports", {}).values()
                if isinstance(record, dict)
            },
        },
        "definitions": {
            "mass_imbalance_signed_pct": "100 * (total_outlet - total_inlet) / total_inlet",
            "mass_imbalance_abs_pct": "absolute value of the signed imbalance",
            "pressure_margin": "entry pressure - 1,120,000 Pa",
            "phase_routing_percent": "phase outlet flow / corresponding phase inlet flow * 100",
            "residual_window": "last 500 native iterations of each evidenced stage; F07 failure tail kept separately",
            "native_history_note": "Physical histories use the recovered native .out Report Files; checkpoint markers are overlaid for validation.",
            "path_magnitude_note": "Outlet and routing histories are converted to outward-positive magnitudes for comparison with checkpoint readbacks; native signed outlet and native expression imbalance remain retained separately.",
            "descriptive_trend_note": "increasing/decreasing labels use a 5% late-to-early median change and are not convergence criteria",
        },
        "figures": figures,
        "checkpoints": rows,
        "residual_order": residual_payload["residual_order"],
        "residual_coverage": residual_payload["branches"][branch]["coverage"],
        "residual_stage_boundaries": residual_payload["branches"][branch].get("stage_boundaries", []),
        "residual_summary": residual_summary(residual_payload, branch),
        "native_history_validation": {
            "summary": validation_counts,
            "rows": validation,
        },
        "terminal_late_window": late_window_summary(rows, residual_payload, branch, history),
    }


def aggregate_payload(
    checkpoint_path: Path,
    residual_path: Path,
    rows: list[dict[str, Any]],
    residual_payload: dict[str, Any],
    branch_packages: dict[str, dict[str, Any]],
    late_windows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "kind": "03a_stage3_owned_branch_analysis_index",
        "scope": {
            "branches": list(OWNED_BRANCHES),
            "branch_selection": "fixed F03/F07/F09 evidence set",
            "plot_structure": "branch-by-branch packages; no multi-branch history overlays",
        },
        "sources": {
            "checkpoint_csv": {"path": repo_relative(checkpoint_path), "sha256": sha256(checkpoint_path)},
            "stitched_residual_json": {"path": repo_relative(residual_path), "sha256": sha256(residual_path)},
        },
        "native_report_history_status": "complete_for_all_owned_branches",
        "checkpoint_count": len(rows),
        "residual_order": residual_payload["residual_order"],
        "branch_packages": branch_packages,
        "compact_cross_branch_summary": [late_windows[branch] for branch in OWNED_BRANCHES],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint-csv", type=Path, default=DEFAULT_CHECKPOINTS)
    parser.add_argument("--residual-json", type=Path, default=DEFAULT_RESIDUALS)
    parser.add_argument("--report-history-dir", type=Path, default=DEFAULT_REPORT_HISTORY_DIR)
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    checkpoint_path = args.checkpoint_csv.resolve()
    residual_path = args.residual_json.resolve()
    report_history_dir = args.report_history_dir.resolve()
    report_root = args.report_root.resolve()
    evidence_root = report_root / "evidence" / "03a-stage3-owned"
    plot_root = report_root / "plots" / "03a-stage3" / "branches"
    rows = load_checkpoints(checkpoint_path)
    residual_payload = load_residuals(residual_path)
    if set(row["branch"] for row in rows) != set(OWNED_BRANCHES):
        raise ValueError(f"Expected exactly {OWNED_BRANCHES}, found {sorted(set(row['branch'] for row in rows))}")

    report_history_paths = {
        branch: newest_report_history(report_history_dir, branch)
        for branch in OWNED_BRANCHES
    }
    report_history_payloads = {
        branch: load_report_history(path)
        for branch, path in report_history_paths.items()
    }
    histories = {
        branch: canonical_report_history(report_history_payloads[branch])
        for branch in OWNED_BRANCHES
    }

    evidence_root.mkdir(parents=True, exist_ok=True)
    write_owned_csv(rows, evidence_root / "03a-stage3-owned-checkpoints.csv")
    branch_packages: dict[str, dict[str, Any]] = {}
    late_windows: dict[str, dict[str, Any]] = {}

    builders: tuple[tuple[str, Callable[..., None]], ...] = (
        ("figure-01-residuals.png", build_residuals),
        ("figure-02-physical-convergence.png", build_physical),
        ("figure-03-phase-routing.png", build_phase),
        ("figure-04-liquid-distribution.png", build_liquid_distribution),
        ("figure-05-brine-pressure-flow.png", build_brine),
        ("figure-07-cross-plots.png", build_cross_plots),
    )

    for branch in OWNED_BRANCHES:
        branch_rows = group_rows(rows, branch)
        branch_evidence = evidence_root / branch.lower()
        branch_plot = plot_root / branch.lower()
        branch_evidence.mkdir(parents=True, exist_ok=True)
        write_owned_csv(branch_rows, branch_evidence / "checkpoints.csv")
        validation = checkpoint_history_validation(branch_rows, histories[branch])
        write_rows_csv(validation, branch_evidence / "native-history-validation.csv")
        figure_paths: list[str] = []
        for filename, builder in builders:
            output = branch_plot / filename
            if builder is build_residuals:
                builder(branch, residual_payload, output)
            else:
                builder(branch, rows, residual_payload, histories[branch], output)
            figure_paths.append(repo_relative(output))
        ramp_output = branch_plot / "figure-06-ramp-response.png"
        if branch in {"F07", "F09"}:
            build_ramp(branch, rows, residual_payload, histories[branch], ramp_output)
            figure_paths.insert(5, repo_relative(ramp_output))
        branch_data = branch_payload(
            branch,
            checkpoint_path,
            residual_path,
            report_history_paths[branch],
            branch_rows,
            residual_payload,
            report_history_payloads[branch],
            histories[branch],
            validation,
            figure_paths,
        )
        branch_json = branch_evidence / "analysis.json"
        branch_json.write_text(json.dumps(branch_data, indent=2) + "\n", encoding="utf-8")
        branch_packages[branch] = {
            "analysis_json": repo_relative(branch_json),
            "checkpoints_csv": repo_relative(branch_evidence / "checkpoints.csv"),
            "native_history_validation_csv": repo_relative(branch_evidence / "native-history-validation.csv"),
            "native_report_history_json": repo_relative(report_history_paths[branch]),
            "figures": figure_paths,
            "terminal_late_window": branch_data["terminal_late_window"],
        }
        late_windows[branch] = branch_data["terminal_late_window"]

    aggregate = aggregate_payload(
        checkpoint_path,
        residual_path,
        rows,
        residual_payload,
        branch_packages,
        late_windows,
    )
    provenance_path = evidence_root / "remote-artifact-provenance.json"
    if provenance_path.exists():
        aggregate["sources"]["remote_artifact_provenance"] = {
            "path": repo_relative(provenance_path),
            "sha256": sha256(provenance_path),
        }
    (evidence_root / "03a-stage3-owned-analysis.json").write_text(
        json.dumps(aggregate, indent=2) + "\n",
        encoding="utf-8",
    )
    write_rows_csv(
        [
            {
                key: value
                for key, value in late_windows[branch].items()
                if key != "history_metrics"
            }
            for branch in OWNED_BRANCHES
        ],
        evidence_root / "03a-stage3-owned-cross-branch-late-window-summary.csv",
    )
    print(f"Filtered checkpoints: {len(rows)} rows from {', '.join(OWNED_BRANCHES)}")
    for branch in OWNED_BRANCHES:
        print(f"{branch}: {len(branch_packages[branch]['figures'])} branch-specific figures")
    print(evidence_root / "03a-stage3-owned-analysis.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
