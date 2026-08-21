#!/usr/bin/env python3
"""Build the evidence-first Stage-3 analysis for the Schedule-D subset.

This is an offline report builder.  It never connects to Fluent and never
changes a case or a report definition.  The raw native report-history JSON,
the checkpoint CSV, and the previously preserved residual exports are inputs;
missing branch histories remain missing.

The subset is F08/F10/F12, the three Schedule-D branches assigned to the
user-supervised queue.  The script deliberately does not import or compare
the other Stage-3 branches.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import statistics
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = (
    PROJECT_ROOT
    / ".."
    / "Setups"
    / "reports"
    / "full-geometry"
    / "mixture"
    / "steady-liquid-outlet"
    / "03a"
).resolve()
CHECKPOINT_PATH = REPORT_ROOT / "03a-stage3-results-20260821-checkpoints.csv"
DEFAULT_RAW_DIR = PROJECT_ROOT / "output" / "03A-stage3" / "server1-final-analysis" / "raw-report-history"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "03A-stage3" / "session1-final-analysis"
DEFAULT_PLOT_DIR = REPORT_ROOT / "plots" / "03a-stage3" / "session1"
ARTIFACT_PROVENANCE_PATH = DEFAULT_OUTPUT_DIR / "server1-artifact-provenance.json"
RESIDUAL_ORDER = (
    "continuity",
    "x-velocity",
    "y-velocity",
    "z-velocity",
    "k",
    "epsilon",
    "vf-phase-2",
)
BRANCHES = ("F08", "F10", "F12")
STAGE_BOUNDARIES = (
    (3000, "carrier-only end"),
    (6000, "10%"),
    (9000, "20%"),
    (12000, "40%"),
    (15000, "80%"),
    (18000, "100%"),
)
PRESSURE_REFERENCE_PA = 1_120_000.0

RAW_NAMES = {
    "total_inlet": "03a_stage3_total_mixture_inlet-rfile",
    "total_outlet_signed": "03a_stage3_total_outlet-rfile",
    "steam_outlet_signed": "03a_stage3_steam_outlet_total-rfile",
    "brine_outlet_signed": "03a_stage3_brine_outlet_total-rfile",
    "mass_imbalance_net": "03a_stage3_full_domain_mass_imbalance-rfile",
    "relative_mass_imbalance_abs": "03a_stage3_relative_mass_imbalance-rfile",
    "liquid_inlet": "03a_stage3_liquid_inlet_mass_flux-rfile",
    "vapor_inlet": "03a_stage3_vapor_inlet_mass_flux-rfile",
    "liquid_to_brine_signed": "03a_stage3_routing_liquid_to_brine-rfile",
    "liquid_to_steam_signed": "03a_stage3_routing_liquid_to_steam-rfile",
    "vapor_to_brine_signed": "03a_stage3_routing_vapor_to_brine-rfile",
    "vapor_to_steam_signed": "03a_stage3_routing_vapor_to_steam-rfile",
    "total_liquid_mass": "03a_stage3_inventory_total_liquid_mass-rfile",
    "total_liquid_volume": "03a_stage3_inventory_total_liquid_volume-rfile",
    "y010_liquid_mass": "03a_stage3_inventory_y010_liquid_mass-rfile",
    "y030_liquid_mass": "03a_stage3_inventory_y030_liquid_mass-rfile",
    "brine_entry_static_pressure": "03a_stage3_brine_entry_static_pressure-rfile",
    "brine_entry_total_pressure": "03a_stage3_brine_entry_total_pressure-rfile",
}

CHECKPOINT_FIELDS = {
    "total_inlet": "total_inlet_kg_s",
    "total_outlet_abs_path_sum": "total_outlet_kg_s",
    "relative_mass_imbalance_abs_path_pct": "mass_imbalance_abs_pct",
    "liquid_inlet": "liquid_inlet_kg_s",
    "vapor_inlet": "vapour_inlet_kg_s",
    "liquid_to_brine": "liquid_to_brine_kg_s",
    "liquid_to_steam": "liquid_to_steam_kg_s",
    "vapor_to_brine": "vapour_to_brine_kg_s",
    "vapor_to_steam": "vapour_to_steam_kg_s",
    "total_liquid_mass": "liquid_inventory_total_kg",
    "y030_liquid_mass": "liquid_inventory_y030_kg",
    "y010_liquid_mass": "liquid_inventory_y010_kg",
    "brine_entry_static_pressure": "brine_entry_static_pressure_pa",
    "brine_entry_total_pressure": "brine_entry_total_pressure_pa",
}
CHECKPOINT_ROUTE_MAGNITUDE_METRICS = {
    "liquid_to_brine",
    "liquid_to_steam",
    "vapor_to_brine",
    "vapor_to_steam",
}


def parse_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def newest_matching(directory: Path, pattern: str) -> Path | None:
    candidates = sorted(directory.glob(pattern))
    return candidates[-1] if candidates else None


def load_report_histories(path: Path) -> dict[str, Any]:
    payload = load_json(path)
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
    return payload


def record_points(record: dict[str, Any]) -> tuple[list[int], list[float]]:
    iterations = [int(value) for value in record.get("iterations", [])]
    values = [float(value) for value in record.get("values", [])]
    if len(iterations) != len(values):
        raise ValueError("Report history has mismatched iteration/value lengths")
    return iterations, values


def make_series(record: dict[str, Any], transform: str = "identity") -> dict[str, Any]:
    iterations, values = record_points(record)
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


def absolute_series(record: dict[str, Any]) -> dict[str, Any]:
    iterations, values = record_points(record)
    return {"iterations": iterations, "values": [abs(value) for value in values]}


def value_at(series: dict[str, Any], iteration: int) -> float | None:
    try:
        index = series["iterations"].index(iteration)
    except ValueError:
        return None
    return series["values"][index]


def percentile(values: Iterable[float], fraction: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return float("nan")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def log_slope_per_1000(iterations: list[int], values: list[float]) -> float | None:
    pairs = [
        (float(iteration), math.log10(value))
        for iteration, value in zip(iterations, values)
        if value > 0.0 and math.isfinite(value)
    ]
    if len(pairs) < 2:
        return None
    x_mean = statistics.fmean(x for x, _ in pairs)
    y_mean = statistics.fmean(y for _, y in pairs)
    denominator = sum((x - x_mean) ** 2 for x, _ in pairs)
    if denominator == 0.0:
        return None
    slope = sum((x - x_mean) * (y - y_mean) for x, y in pairs) / denominator
    return slope * 1000.0


def describe_trend(values: list[float]) -> str:
    if len(values) < 10:
        return "insufficient window"
    block = max(1, len(values) // 5)
    first = statistics.median(values[:block])
    last = statistics.median(values[-block:])
    if first == 0.0:
        return "increasing" if last > 0.0 else "flat at zero"
    ratio = last / first
    if ratio > 1.10:
        return "increasing"
    if ratio < 0.90:
        return "decreasing"
    return "bounded/flat by endpoint-window comparison"


def residual_stats(
    branch: str,
    stage: str,
    source: Path | str,
    histories: dict[str, dict[str, list[float]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in RESIDUAL_ORDER:
        record = histories.get(name, {})
        iterations = [int(value) for value in record.get("iterations", [])]
        values = [float(value) for value in record.get("values", [])]
        rows.append(
            {
                "branch": branch,
                "stage": stage,
                "equation": name,
                "source": str(source),
                "status": "complete" if values else "unavailable",
                "points": len(values),
                "first_iteration": iterations[0] if iterations else None,
                "last_iteration": iterations[-1] if iterations else None,
                "median": statistics.median(values) if values else None,
                "p05": percentile(values, 0.05) if values else None,
                "p95": percentile(values, 0.95) if values else None,
                "log10_slope_per_1000_iterations": log_slope_per_1000(iterations, values)
                if values
                else None,
                "trend": describe_trend(values) if values else "unavailable",
            }
        )
    return rows


def read_checkpoints(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            if raw.get("branch") not in BRANCHES:
                continue
            row: dict[str, Any] = dict(raw)
            row["iteration"] = int(raw["iteration"])
            row["load_percent"] = int(raw["load_percent"])
            row["momentum_urf"] = parse_float(raw["momentum_urf"])
            for key, value in raw.items():
                if key in {"branch", "run_stamp", "solver_state", "checkpoint_case", "checkpoint_data", "evidence_status"}:
                    continue
                if key not in {"iteration", "load_percent", "momentum_urf"}:
                    row[key] = parse_float(value)
            rows.append(row)
    return rows


def history_duplicate_groups(reports: dict[str, Any]) -> list[list[str]]:
    names = sorted(reports)
    parent = {name: name for name in names}

    def find(name: str) -> str:
        while parent[name] != name:
            parent[name] = parent[parent[name]]
            name = parent[name]
        return name

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for index, left in enumerate(names):
        left_i, left_v = record_points(reports[left])
        for right in names[index + 1 :]:
            right_i, right_v = record_points(reports[right])
            if left_i != right_i or len(left_v) != len(right_v):
                continue
            if all(math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-11) for a, b in zip(left_v, right_v)):
                union(left, right)

    groups: dict[str, list[str]] = {}
    for name in names:
        groups.setdefault(find(name), []).append(name)
    return [group for group in groups.values() if len(group) > 1]


def canonical_series(reports: dict[str, Any]) -> dict[str, dict[str, Any]]:
    transforms = {
        "total_inlet": "identity",
        "total_outlet": "negate",
        "steam_outlet_total": "negate",
        "brine_outlet_total": "negate",
        "mass_imbalance_net": "identity",
        "relative_mass_imbalance_abs": "percent",
        "liquid_inlet": "identity",
        "vapor_inlet": "identity",
        "liquid_to_brine": "negate",
        "liquid_to_steam": "negate",
        "vapor_to_brine": "negate",
        "vapor_to_steam": "negate",
        "total_liquid_mass": "identity",
        "total_liquid_volume": "identity",
        "y010_liquid_mass": "identity",
        "y030_liquid_mass": "identity",
        "brine_entry_static_pressure": "identity",
        "brine_entry_total_pressure": "identity",
        "brine_entry_static_pressure_margin": "static-margin",
    }
    result: dict[str, dict[str, Any]] = {}
    for canonical, raw_name in RAW_NAMES.items():
        if raw_name not in reports:
            continue
        result[canonical] = make_series(reports[raw_name], transforms.get(canonical, "identity"))
    result["total_outlet"] = make_series(reports[RAW_NAMES["total_outlet_signed"]], "negate")
    result["total_outlet_net_magnitude"] = absolute_series(reports[RAW_NAMES["total_outlet_signed"]])
    result["steam_outlet_total"] = make_series(reports[RAW_NAMES["steam_outlet_signed"]], "negate")
    result["brine_outlet_total"] = make_series(reports[RAW_NAMES["brine_outlet_signed"]], "negate")
    result["liquid_to_brine"] = make_series(reports[RAW_NAMES["liquid_to_brine_signed"]], "negate")
    result["liquid_to_steam"] = make_series(reports[RAW_NAMES["liquid_to_steam_signed"]], "negate")
    result["vapor_to_brine"] = make_series(reports[RAW_NAMES["vapor_to_brine_signed"]], "negate")
    result["vapor_to_steam"] = make_series(reports[RAW_NAMES["vapor_to_steam_signed"]], "negate")
    result["brine_entry_static_pressure_margin"] = make_series(
        reports[RAW_NAMES["brine_entry_static_pressure"]], "static-margin"
    )
    route_raw_names = (
        RAW_NAMES["liquid_to_brine_signed"],
        RAW_NAMES["liquid_to_steam_signed"],
        RAW_NAMES["vapor_to_brine_signed"],
        RAW_NAMES["vapor_to_steam_signed"],
    )
    route_records = [reports[name] for name in route_raw_names]
    route_points = [record_points(record) for record in route_records]
    route_iterations = route_points[0][0]
    route_value_arrays = [values for _, values in route_points]
    if all(iterations == route_iterations for iterations, _ in route_points):
        combined_values = [
            sum(abs(values[index]) for values in route_value_arrays)
            for index in range(len(route_iterations))
        ]
        result["total_outlet_abs_path_sum"] = {
            "iterations": route_iterations,
            "values": combined_values,
        }
        inlet_values = result["total_inlet"]["values"]
        result["relative_mass_imbalance_abs_path_pct"] = {
            "iterations": route_iterations,
            "values": [
                100.0 * abs(outlet - inlet) / abs(inlet) if inlet else float("nan")
                for inlet, outlet in zip(inlet_values, combined_values)
            ],
        }
    return result


def checkpoint_expected(row: dict[str, Any], metric: str) -> float | None:
    field = CHECKPOINT_FIELDS.get(metric)
    return row.get(field) if field else None


def validate_checkpoints(
    checkpoints: list[dict[str, Any]],
    histories: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for checkpoint in checkpoints:
        branch = checkpoint["branch"]
        iteration = checkpoint["iteration"]
        if branch == "F12":
            metrics = list(CHECKPOINT_FIELDS)
            for metric in metrics:
                series = histories.get(metric)
                extracted = value_at(series, iteration) if series else None
                expected = checkpoint_expected(checkpoint, metric)
                if extracted is None or expected is None:
                    status = "unavailable"
                    difference = None
                    tolerance = None
                else:
                    extracted_for_checkpoint = (
                        abs(extracted) if metric in CHECKPOINT_ROUTE_MAGNITUDE_METRICS else extracted
                    )
                    difference = extracted_for_checkpoint - expected
                    tolerance = max(1e-3, abs(expected) * 1e-5)
                    status = "match" if abs(difference) <= tolerance else "mismatch"
                rows.append(
                    {
                        "branch": branch,
                        "iteration": iteration,
                        "load_percent": checkpoint["load_percent"],
                        "metric": metric,
                        "expected_checkpoint": expected,
                        "extracted_history": extracted,
                        "extracted_for_checkpoint": extracted_for_checkpoint if extracted is not None else None,
                        "difference": difference,
                        "tolerance": tolerance,
                        "status": status,
                    }
                )
        else:
            rows.append(
                {
                    "branch": branch,
                    "iteration": iteration,
                    "load_percent": checkpoint["load_percent"],
                    "metric": "all physical histories",
                    "expected_checkpoint": None,
                    "extracted_history": None,
                    "difference": None,
                    "tolerance": None,
                    "status": "unavailable — no branch-specific continuous history",
                }
            )
    return rows


def endpoint_summary(checkpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for branch in BRANCHES:
        branch_rows = [row for row in checkpoints if row["branch"] == branch]
        if not branch_rows:
            continue
        for row in branch_rows:
            selected.append(
                {
                    "branch": branch,
                    "load_percent": row["load_percent"],
                    "iteration": row["iteration"],
                    "total_inlet_kg_s": row.get("total_inlet_kg_s"),
                    "total_outlet_kg_s": row.get("total_outlet_kg_s"),
                    "mass_imbalance_signed_pct": row.get("mass_imbalance_signed_pct"),
                    "mass_imbalance_abs_pct": row.get("mass_imbalance_abs_pct"),
                    "liquid_inventory_total_kg": row.get("liquid_inventory_total_kg"),
                    "liquid_inventory_y030_kg": row.get("liquid_inventory_y030_kg"),
                    "liquid_inventory_y010_kg": row.get("liquid_inventory_y010_kg"),
                    "brine_entry_static_pressure_margin_pa": row.get("brine_entry_pressure_margin_pa"),
                    "evidence_status": row.get("evidence_status"),
                }
            )
    return selected


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def add_stage_lines(axis: Any, *, labels: bool = True) -> None:
    for iteration, label in STAGE_BOUNDARIES:
        axis.axvline(iteration, color="#64748b", linestyle="--", linewidth=0.7, alpha=0.55)
        if labels:
            axis.text(
                iteration,
                0.98,
                label,
                transform=axis.get_xaxis_transform(),
                rotation=90,
                va="top",
                ha="right",
                fontsize=7,
                color="#475569",
            )


def plot_residuals(
    output_path: Path,
    f08_residuals: dict[str, dict[str, list[float]]],
    f12_residuals: dict[str, dict[str, list[float]]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {
        "continuity": "#2563eb",
        "x-velocity": "#0f766e",
        "y-velocity": "#15803d",
        "z-velocity": "#a16207",
        "k": "#c2410c",
        "epsilon": "#be123c",
        "vf-phase-2": "#7c3aed",
    }
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), constrained_layout=True)
    branch_data = {
        "F08": f08_residuals,
        "F10": {},
        "F12": f12_residuals,
    }
    notes = {
        "F08": "partial saved export; source filename identifies a 20% resume stream, not the 40% endpoint",
        "F10": "no saved native residual history after carrier-stage failure",
        "F12": "final 250-point native residual window only (iterations 17,003–18,000)",
    }
    for axis, branch in zip(axes, BRANCHES):
        data = branch_data[branch]
        plotted = False
        for name in RESIDUAL_ORDER:
            record = data.get(name, {})
            if not record:
                continue
            axis.plot(
                record["iterations"],
                record["values"],
                color=colors[name],
                linewidth=1.0,
                label=name,
            )
            plotted = True
        axis.set_yscale("log")
        axis.grid(True, which="major", alpha=0.25)
        axis.grid(True, which="minor", linestyle=":", alpha=0.14)
        axis.set_ylabel(f"{branch}\nscaled residual")
        axis.set_title(f"{branch} — available residual evidence", loc="left", fontweight="bold")
        axis.text(0.01, 0.03, notes[branch], transform=axis.transAxes, fontsize=8, color="#475569")
        if plotted:
            axis.legend(loc="upper right", ncol=4, fontsize=8, frameon=False)
        else:
            axis.set_facecolor("#f8fafc")
            axis.text(0.5, 0.5, "NO SAVED HISTORY", transform=axis.transAxes, ha="center", va="center", color="#b91c1c", fontweight="bold")
        if branch == "F12":
            axis.axvline(18000, color="#0f172a", linewidth=0.9, linestyle="--")
            axis.text(18000, 0.98, "100% endpoint", transform=axis.get_xaxis_transform(), rotation=90, va="top", ha="right", fontsize=8)
    axes[-1].set_xlabel("Fluent native iteration (preserved where available)")
    fig.suptitle("03A Stage-3 — Schedule-D residual evidence", fontsize=16, fontweight="bold")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_physical_convergence(output_path: Path, histories: dict[str, dict[str, Any]], checkpoints: list[dict[str, Any]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    f12 = histories
    f08_rows = [row for row in checkpoints if row["branch"] == "F08"]
    fig, axes = plt.subplots(3, 1, figsize=(13, 11), sharex=True, constrained_layout=True)

    axes[0].plot(f12["total_inlet"]["iterations"], f12["total_inlet"]["values"], color="#2563eb", linewidth=1.0, label="F12 total inlet")
    axes[0].plot(
        f12["total_outlet_abs_path_sum"]["iterations"],
        f12["total_outlet_abs_path_sum"]["values"],
        color="#dc2626",
        linewidth=1.0,
        label="F12 outlet path-magnitude sum (checkpoint-compatible)",
    )
    axes[0].plot(
        f12["total_outlet_net_magnitude"]["iterations"],
        f12["total_outlet_net_magnitude"]["values"],
        color="#64748b",
        linewidth=0.9,
        linestyle="--",
        label="F12 native net-outlet magnitude",
    )
    if f08_rows:
        row = f08_rows[-1]
        axes[0].plot(row["iteration"], row["total_inlet_kg_s"], marker="o", color="#f59e0b", label="F08 checkpoint inlet")
        axes[0].plot(row["iteration"], row["total_outlet_kg_s"], marker="o", color="#7c2d12", label="F08 checkpoint outlet")
    axes[0].set_ylabel("Mass flow (kg/s)")
    axes[0].set_title("A — total inlet and outlet", loc="left", fontweight="bold")

    axes[1].plot(
        f12["relative_mass_imbalance_abs_path_pct"]["iterations"],
        f12["relative_mass_imbalance_abs_path_pct"]["values"],
        color="#7c3aed",
        linewidth=1.0,
        label="F12 path-magnitude imbalance (checkpoint-compatible)",
    )
    axes[1].plot(
        f12["relative_mass_imbalance_abs"]["iterations"],
        f12["relative_mass_imbalance_abs"]["values"],
        color="#64748b",
        linewidth=0.9,
        linestyle=":",
        label="F12 native net-report imbalance",
    )
    if f08_rows:
        row = f08_rows[-1]
        axes[1].plot(row["iteration"], row["mass_imbalance_abs_pct"], marker="o", color="#f59e0b", label="F08 checkpoint")
    axes[1].set_ylabel("|mass imbalance| (%)")
    axes[1].set_title("B — mass-balance magnitude", loc="left", fontweight="bold")

    axes[2].plot(f12["total_liquid_mass"]["iterations"], f12["total_liquid_mass"]["values"], color="#059669", linewidth=1.0, label="F12 total liquid inventory")
    if f08_rows:
        row = f08_rows[-1]
        axes[2].plot(row["iteration"], row["liquid_inventory_total_kg"], marker="o", color="#f59e0b", label="F08 checkpoint")
    axes[2].set_ylabel("Liquid mass (kg)")
    axes[2].set_title("C — total liquid inventory", loc="left", fontweight="bold")
    axes[2].set_xlabel("Cumulative Fluent iteration")

    for axis in axes:
        add_stage_lines(axis)
        axis.grid(True, alpha=0.25)
        axis.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
        axis.text(0.01, 0.03, "F10 has no full-Mixture physical checkpoint; F08 is checkpoint-only in this subset.", transform=axis.transAxes, fontsize=8, color="#475569")
    fig.suptitle("03A Stage-3 — primary physical convergence evidence", fontsize=16, fontweight="bold")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_phase_routing(output_path: Path, histories: dict[str, dict[str, Any]], checkpoints: list[dict[str, Any]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    f08 = [row for row in checkpoints if row["branch"] == "F08"][-1:]
    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True, constrained_layout=True)
    route_colors = {"liquid": "#2563eb", "vapor": "#dc2626"}
    for axis, outlet, title in zip(axes, ("brine", "steam"), ("Brine outlet routing", "Steam outlet routing")):
        for phase in ("liquid", "vapor"):
            key = f"{phase}_to_{outlet}"
            axis.plot(histories[key]["iterations"], histories[key]["values"], color=route_colors[phase], linewidth=1.0, label=f"F12 {phase} → {outlet}")
        if f08:
            row = f08[0]
            values = {
                "liquid": row[f"liquid_to_{outlet}_kg_s"],
                "vapor": row[f"vapour_to_{outlet}_kg_s"],
            }
            for phase, value in values.items():
                axis.plot(row["iteration"], value, marker="o", color=route_colors[phase], label=f"F08 {phase} → {outlet}")
        axis.set_ylabel("Mass flow (kg/s)\n(outward-positive sign; negative = backflow)")
        axis.set_title(title, loc="left", fontweight="bold")
        axis.grid(True, alpha=0.25)
        axis.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
        add_stage_lines(axis, labels=False)
    axes[-1].set_xlabel("Cumulative Fluent iteration")
    fig.suptitle("03A Stage-3 — phase routing diagnostic evidence", fontsize=16, fontweight="bold")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_liquid_distribution(output_path: Path, histories: dict[str, dict[str, Any]], checkpoints: list[dict[str, Any]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axis = plt.subplots(figsize=(13, 6), constrained_layout=True)
    styles = {
        "total_liquid_mass": ("#059669", "F12 total liquid mass"),
        "y030_liquid_mass": ("#2563eb", "F12 Y030 liquid mass"),
        "y010_liquid_mass": ("#dc2626", "F12 Y010 liquid mass"),
    }
    for key, (color, label) in styles.items():
        axis.plot(histories[key]["iterations"], histories[key]["values"], color=color, linewidth=1.0, label=label)
    f08 = [row for row in checkpoints if row["branch"] == "F08"][-1:]
    if f08:
        row = f08[0]
        axis.plot(row["iteration"], row["liquid_inventory_total_kg"], marker="o", color="#f59e0b", label="F08 total liquid checkpoint")
        axis.plot(row["iteration"], row["liquid_inventory_y030_kg"], marker="o", mfc="white", color="#f59e0b", label="F08 Y030 checkpoint")
        axis.plot(row["iteration"], row["liquid_inventory_y010_kg"], marker="o", mfc="white", color="#7c2d12", label="F08 Y010 checkpoint")
    add_stage_lines(axis)
    axis.set_xlabel("Cumulative Fluent iteration")
    axis.set_ylabel("Liquid mass (kg)")
    axis.set_title("03A Stage-3 — liquid distribution evidence", loc="left", fontweight="bold")
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
    axis.text(0.01, 0.03, "Register geometric volumes are constants and are not plotted as histories.", transform=axis.transAxes, fontsize=8, color="#475569")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_brine_hydraulics(output_path: Path, histories: dict[str, dict[str, Any]], checkpoints: list[dict[str, Any]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True, constrained_layout=True)
    axes[0].plot(histories["brine_entry_static_pressure_margin"]["iterations"], histories["brine_entry_static_pressure_margin"]["values"], color="#2563eb", linewidth=1.0, label="F12 static-pressure margin")
    total_margin = [value - PRESSURE_REFERENCE_PA for value in histories["brine_entry_total_pressure"]["values"]]
    axes[0].plot(histories["brine_entry_total_pressure"]["iterations"], total_margin, color="#dc2626", linewidth=1.0, label="F12 total-pressure margin")
    axes[0].set_ylabel("Pressure margin (Pa)\nrelative to 1.120 MPa")
    axes[0].set_title("A — brine-entry pressure margins", loc="left", fontweight="bold")

    axes[1].plot(histories["brine_outlet_total"]["iterations"], histories["brine_outlet_total"]["values"], color="#059669", linewidth=1.0, label="F12 total brine outlet")
    axes[1].plot(histories["liquid_to_brine"]["iterations"], histories["liquid_to_brine"]["values"], color="#7c3aed", linewidth=1.0, label="F12 liquid → brine")
    axes[1].set_ylabel("Mass flow (kg/s)\n(outward-positive sign; negative = backflow)")
    axes[1].set_title("B — brine flow response", loc="left", fontweight="bold")
    f08 = [row for row in checkpoints if row["branch"] == "F08"][-1:]
    if f08:
        row = f08[0]
        axes[0].plot(row["iteration"], row["brine_entry_pressure_margin_pa"], marker="o", color="#f59e0b", label="F08 static margin checkpoint")
        axes[1].plot(row["iteration"], row["liquid_to_brine_kg_s"] + row["vapour_to_brine_kg_s"], marker="o", color="#f59e0b", label="F08 total brine checkpoint")
        axes[1].plot(row["iteration"], row["liquid_to_brine_kg_s"], marker="o", mfc="white", color="#7c2d12", label="F08 liquid → brine checkpoint")
    for axis in axes:
        add_stage_lines(axis, labels=False)
        axis.grid(True, alpha=0.25)
        axis.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
    axes[-1].set_xlabel("Cumulative Fluent iteration")
    fig.suptitle("03A Stage-3 — brine-entry hydraulic response", fontsize=16, fontweight="bold")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_ramp_response(output_path: Path, checkpoints: list[dict[str, Any]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    metrics = (
        ("mass_imbalance_abs_pct", "Absolute mass imbalance (%)"),
        ("liquid_inventory_total_kg", "Total liquid inventory (kg)"),
        ("brine_entry_pressure_margin_pa", "Brine-entry static margin (Pa)"),
        ("total_outlet_kg_s", "Total outlet magnitude (kg/s)"),
    )
    for axis, (metric, ylabel) in zip(axes.flat, metrics):
        for branch, color, marker in (("F08", "#f59e0b", "o"), ("F12", "#2563eb", "s")):
            rows = sorted((row for row in checkpoints if row["branch"] == branch), key=lambda row: row["load_percent"])
            if not rows:
                continue
            axis.plot([row["load_percent"] for row in rows], [row[metric] for row in rows], color=color, marker=marker, linewidth=1.1, label=branch)
        axis.set_xlabel("Inlet loading (%)")
        axis.set_ylabel(ylabel)
        axis.grid(True, alpha=0.25)
        axis.set_xticks([10, 20, 40, 80, 100])
        axis.set_title(ylabel, loc="left", fontweight="bold")
        axis.legend(frameon=False, fontsize=8)
    fig.suptitle("03A Stage-3 — progressive-loading endpoint response", fontsize=16, fontweight="bold")
    fig.text(0.01, 0.01, "F10 has no completed physical endpoint. F08 contributes only the verified 40% checkpoint.", fontsize=8, color="#475569")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_matched_100_not_applicable(output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axis = plt.subplots(figsize=(12, 5), constrained_layout=True)
    axis.axis("off")
    axis.text(
        0.5,
        0.62,
        "FIGURE 6 — MATCHED 100% CROSS-BRANCH COMPARISON",
        ha="center",
        va="center",
        fontsize=17,
        fontweight="bold",
        color="#0f172a",
    )
    axis.text(
        0.5,
        0.42,
        "Not applicable within the requested Schedule-D subset",
        ha="center",
        va="center",
        fontsize=15,
        color="#b91c1c",
    )
    axis.text(
        0.5,
        0.25,
        "F08: no 100% endpoint   |   F10: no native endpoint   |   F12: one 100% endpoint",
        ha="center",
        va="center",
        fontsize=11,
        color="#475569",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def no_data_figure(output_path: Path, title: str, message: str, detail: str = "") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axis = plt.subplots(figsize=(12, 5), constrained_layout=True)
    axis.set_facecolor("#f8fafc")
    axis.set_xticks([])
    axis.set_yticks([])
    for spine in axis.spines.values():
        spine.set_color("#cbd5e1")
    axis.text(0.5, 0.62, title, ha="center", va="center", fontsize=17, fontweight="bold", color="#0f172a")
    axis.text(0.5, 0.43, message, ha="center", va="center", fontsize=14, fontweight="bold", color="#b91c1c")
    if detail:
        axis.text(0.5, 0.27, detail, ha="center", va="center", fontsize=10.5, color="#475569", wrap=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def branch_checkpoint_rows(checkpoints: list[dict[str, Any]], branch: str) -> list[dict[str, Any]]:
    return sorted(
        (row for row in checkpoints if row["branch"] == branch),
        key=lambda row: (row["iteration"], row["load_percent"]),
    )


def plot_branch_residuals(
    output_path: Path,
    branch: str,
    residuals: dict[str, dict[str, list[float]]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not residuals or not any(residuals.get(name, {}).get("values") for name in RESIDUAL_ORDER):
        no_data_figure(
            output_path,
            f"03A Stage-3 — {branch} residual evidence",
            "NO SAVED RESIDUAL HISTORY",
            "The branch failed before a native residual export was preserved.",
        )
        return

    colors = {
        "continuity": "#2563eb",
        "x-velocity": "#0f766e",
        "y-velocity": "#15803d",
        "z-velocity": "#a16207",
        "k": "#c2410c",
        "epsilon": "#be123c",
        "vf-phase-2": "#7c3aed",
    }
    fig, axis = plt.subplots(figsize=(13, 7), constrained_layout=True)
    for name in RESIDUAL_ORDER:
        record = residuals.get(name, {})
        if not record or not record.get("values"):
            continue
        axis.plot(record["iterations"], record["values"], color=colors[name], linewidth=1.0, label=name)
    axis.set_yscale("log")
    axis.grid(True, which="major", alpha=0.25)
    axis.grid(True, which="minor", linestyle=":", alpha=0.14)
    axis.set_xlabel("Fluent native iteration (preserved where available)")
    axis.set_ylabel("scaled residual")
    axis.set_title(f"03A Stage-3 — {branch} residual evidence", loc="left", fontweight="bold")
    notes = {
        "F08": "partial saved export; source filename identifies a 20% resume stream, not the 40% endpoint",
        "F10": "no saved native residual history after carrier-stage failure",
        "F12": "final retained residual window only (iterations 17,003–18,000)",
    }
    axis.text(0.01, 0.03, notes[branch], transform=axis.transAxes, fontsize=9, color="#475569")
    if branch == "F12":
        axis.axvline(18000, color="#0f172a", linewidth=0.9, linestyle="--")
    axis.legend(loc="upper right", ncol=4, fontsize=8, frameon=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_branch_physical_convergence(
    output_path: Path,
    branch: str,
    histories: dict[str, dict[str, Any]],
    checkpoints: list[dict[str, Any]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = branch_checkpoint_rows(checkpoints, branch)
    has_history = all(
        key in histories
        for key in ("total_inlet", "total_outlet_abs_path_sum", "relative_mass_imbalance_abs_path_pct", "total_liquid_mass")
    )
    if not has_history and not rows:
        no_data_figure(
            output_path,
            f"03A Stage-3 — {branch} physical convergence",
            "NO PHYSICAL ENDPOINT OR NATIVE REPORT HISTORY",
            "No branch-specific inlet/outlet, imbalance, inventory, or checkpoint history is available.",
        )
        return

    fig, axes = plt.subplots(3, 1, figsize=(13, 11), sharex=True, constrained_layout=True)
    if has_history:
        axes[0].plot(histories["total_inlet"]["iterations"], histories["total_inlet"]["values"], color="#2563eb", linewidth=1.0, label="total inlet")
        axes[0].plot(histories["total_outlet_abs_path_sum"]["iterations"], histories["total_outlet_abs_path_sum"]["values"], color="#dc2626", linewidth=1.0, label="outlet path-magnitude sum")
        axes[0].plot(histories["total_outlet_net_magnitude"]["iterations"], histories["total_outlet_net_magnitude"]["values"], color="#64748b", linewidth=0.9, linestyle="--", label="native net-outlet magnitude")
        axes[1].plot(histories["relative_mass_imbalance_abs_path_pct"]["iterations"], histories["relative_mass_imbalance_abs_path_pct"]["values"], color="#7c3aed", linewidth=1.0, label="path-magnitude imbalance")
        axes[1].plot(histories["relative_mass_imbalance_abs"]["iterations"], histories["relative_mass_imbalance_abs"]["values"], color="#64748b", linewidth=0.9, linestyle=":", label="native net-report imbalance")
        axes[2].plot(histories["total_liquid_mass"]["iterations"], histories["total_liquid_mass"]["values"], color="#059669", linewidth=1.0, label="total liquid inventory")
    if rows and not has_history:
        row = rows[-1]
        axes[0].scatter(row["iteration"], row["total_inlet_kg_s"], color="#f59e0b", s=55, label="checkpoint inlet", zorder=4)
        axes[0].scatter(row["iteration"], row["total_outlet_kg_s"], color="#7c2d12", s=55, label="checkpoint outlet path sum", zorder=4)
        axes[1].scatter(row["iteration"], row["mass_imbalance_abs_pct"], color="#f59e0b", s=55, label="checkpoint imbalance", zorder=4)
        axes[2].scatter(row["iteration"], row["liquid_inventory_total_kg"], color="#f59e0b", s=55, label="checkpoint inventory", zorder=4)
    axes[0].set_ylabel("Mass flow (kg/s)")
    axes[1].set_ylabel("|mass imbalance| (%)")
    axes[2].set_ylabel("Liquid mass (kg)")
    axes[2].set_xlabel("Cumulative Fluent iteration")
    for axis in axes:
        if has_history:
            add_stage_lines(axis)
        axis.grid(True, alpha=0.25)
        axis.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
    if not has_history:
        axes[0].text(0.01, 0.03, "checkpoint-only evidence; no continuous branch-specific physical history", transform=axes[0].transAxes, fontsize=9, color="#475569")
    fig.suptitle(f"03A Stage-3 — {branch} primary physical convergence evidence", fontsize=16, fontweight="bold")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_branch_phase_routing(
    output_path: Path,
    branch: str,
    histories: dict[str, dict[str, Any]],
    checkpoints: list[dict[str, Any]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = branch_checkpoint_rows(checkpoints, branch)
    has_history = all(key in histories for key in ("liquid_to_brine", "vapor_to_brine", "liquid_to_steam", "vapor_to_steam"))
    if not has_history and not rows:
        no_data_figure(output_path, f"03A Stage-3 — {branch} phase routing", "NO PHASE-ROUTING HISTORY", "No native route history or checkpoint endpoint is available.")
        return

    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True, constrained_layout=True)
    for axis, outlet, title in zip(axes, ("brine", "steam"), ("Brine outlet routing", "Steam outlet routing")):
        for phase, color in (("liquid", "#2563eb"), ("vapor", "#dc2626")):
            key = f"{phase}_to_{outlet}"
            if has_history:
                axis.plot(histories[key]["iterations"], histories[key]["values"], color=color, linewidth=1.0, label=f"{phase} → {outlet} (signed)")
            if rows and not has_history:
                value_key = f"{phase}_to_{outlet}_kg_s" if phase == "liquid" else f"vapour_to_{outlet}_kg_s"
                axis.scatter([row["iteration"] for row in rows], [row[value_key] for row in rows], color=color, s=45, label=f"{phase} → {outlet} checkpoint magnitude", zorder=4)
        axis.set_ylabel("Mass flow (kg/s)\n(outward-positive; negative = backflow)")
        axis.set_title(title, loc="left", fontweight="bold")
        axis.grid(True, alpha=0.25)
        axis.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
        if has_history:
            add_stage_lines(axis, labels=False)
    axes[-1].set_xlabel("Cumulative Fluent iteration")
    note = "checkpoint path magnitudes only; no continuous route history" if not has_history else "signed canonical histories retained; checkpoint magnitudes are not silently substituted"
    axes[0].text(0.01, 0.03, note, transform=axes[0].transAxes, fontsize=9, color="#475569")
    fig.suptitle(f"03A Stage-3 — {branch} phase-routing evidence", fontsize=16, fontweight="bold")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_branch_liquid_distribution(
    output_path: Path,
    branch: str,
    histories: dict[str, dict[str, Any]],
    checkpoints: list[dict[str, Any]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = branch_checkpoint_rows(checkpoints, branch)
    keys = ("total_liquid_mass", "y030_liquid_mass", "y010_liquid_mass")
    has_history = all(key in histories for key in keys)
    if not has_history and not rows:
        no_data_figure(output_path, f"03A Stage-3 — {branch} liquid distribution", "NO LIQUID-INVENTORY HISTORY", "No native inventory history or checkpoint endpoint is available.")
        return

    fig, axis = plt.subplots(figsize=(13, 6), constrained_layout=True)
    styles = {
        "total_liquid_mass": ("#059669", "total liquid mass"),
        "y030_liquid_mass": ("#2563eb", "Y030 liquid mass"),
        "y010_liquid_mass": ("#dc2626", "Y010 liquid mass"),
    }
    for key, (color, label) in styles.items():
        if has_history:
            axis.plot(histories[key]["iterations"], histories[key]["values"], color=color, linewidth=1.0, label=label)
        if rows and not has_history:
            checkpoint_key = {
                "total_liquid_mass": "liquid_inventory_total_kg",
                "y030_liquid_mass": "liquid_inventory_y030_kg",
                "y010_liquid_mass": "liquid_inventory_y010_kg",
            }[key]
            axis.scatter([row["iteration"] for row in rows], [row[checkpoint_key] for row in rows], color=color, s=50, label=f"{label} checkpoint", zorder=4)
    if has_history:
        add_stage_lines(axis)
    axis.set_xlabel("Cumulative Fluent iteration")
    axis.set_ylabel("Liquid mass (kg)")
    axis.set_title(f"03A Stage-3 — {branch} liquid distribution evidence", loc="left", fontweight="bold")
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
    axis.text(0.01, 0.03, "Y010/Y030 are diagnostic regions; register geometric volumes are constants.", transform=axis.transAxes, fontsize=9, color="#475569")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_branch_brine_hydraulics(
    output_path: Path,
    branch: str,
    histories: dict[str, dict[str, Any]],
    checkpoints: list[dict[str, Any]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = branch_checkpoint_rows(checkpoints, branch)
    has_history = all(key in histories for key in ("brine_entry_static_pressure_margin", "brine_entry_total_pressure", "brine_outlet_total", "liquid_to_brine"))
    if not has_history and not rows:
        no_data_figure(output_path, f"03A Stage-3 — {branch} brine hydraulics", "NO BRINE HYDRAULIC HISTORY", "No native pressure/flow history or checkpoint endpoint is available.")
        return

    fig, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True, constrained_layout=True)
    if has_history:
        axes[0].plot(histories["brine_entry_static_pressure_margin"]["iterations"], histories["brine_entry_static_pressure_margin"]["values"], color="#2563eb", linewidth=1.0, label="static-pressure margin")
        total_margin = [value - PRESSURE_REFERENCE_PA for value in histories["brine_entry_total_pressure"]["values"]]
        axes[0].plot(histories["brine_entry_total_pressure"]["iterations"], total_margin, color="#dc2626", linewidth=1.0, label="total-pressure margin")
        axes[1].plot(histories["brine_outlet_total"]["iterations"], histories["brine_outlet_total"]["values"], color="#059669", linewidth=1.0, label="total brine outlet")
        axes[1].plot(histories["liquid_to_brine"]["iterations"], histories["liquid_to_brine"]["values"], color="#7c3aed", linewidth=1.0, label="liquid → brine (signed)")
    if rows and not has_history:
        axes[0].scatter([row["iteration"] for row in rows], [row["brine_entry_pressure_margin_pa"] for row in rows], color="#f59e0b", s=50, label="static margin checkpoint", zorder=4)
        axes[1].scatter([row["iteration"] for row in rows], [row["liquid_to_brine_kg_s"] + row["vapour_to_brine_kg_s"] for row in rows], color="#059669", s=50, label="total brine checkpoint", zorder=4)
        axes[1].scatter([row["iteration"] for row in rows], [row["liquid_to_brine_kg_s"] for row in rows], color="#7c3aed", s=50, label="liquid → brine checkpoint", zorder=4)
    axes[0].set_ylabel("Pressure margin (Pa)\nrelative to 1.120 MPa")
    axes[1].set_ylabel("Mass flow (kg/s)\n(outward-positive; negative = backflow)")
    axes[1].set_xlabel("Cumulative Fluent iteration")
    axes[0].set_title("Brine-entry pressure margins", loc="left", fontweight="bold")
    axes[1].set_title("Brine flow response", loc="left", fontweight="bold")
    for axis in axes:
        if has_history:
            add_stage_lines(axis, labels=False)
        axis.grid(True, alpha=0.25)
        axis.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
    fig.suptitle(f"03A Stage-3 — {branch} brine-entry hydraulic evidence", fontsize=16, fontweight="bold")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_branch_ramp_response(output_path: Path, branch: str, checkpoints: list[dict[str, Any]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = branch_checkpoint_rows(checkpoints, branch)
    if not rows:
        no_data_figure(output_path, f"03A Stage-3 — {branch} ramp response", "NO COMPLETED RAMP ENDPOINT", "The branch failed before a usable loading-stage checkpoint was preserved.")
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    metrics = (
        ("mass_imbalance_abs_pct", "Absolute mass imbalance (%)"),
        ("liquid_inventory_total_kg", "Total liquid inventory (kg)"),
        ("brine_entry_pressure_margin_pa", "Brine-entry static margin (Pa)"),
        ("total_outlet_kg_s", "Total outlet path magnitude (kg/s)"),
    )
    color = "#2563eb" if branch == "F12" else "#f59e0b"
    marker = "s" if branch == "F12" else "o"
    for axis, (metric, ylabel) in zip(axes.flat, metrics):
        axis.plot([row["load_percent"] for row in rows], [row[metric] for row in rows], color=color, marker=marker, linewidth=1.1, label=branch)
        axis.set_xlabel("Inlet loading (%)")
        axis.set_ylabel(ylabel)
        axis.grid(True, alpha=0.25)
        axis.set_xticks([10, 20, 40, 80, 100])
        axis.set_title(ylabel, loc="left", fontweight="bold")
        axis.legend(frameon=False, fontsize=8)
        if branch == "F08":
            axis.axvline(80, color="#b91c1c", linestyle="--", linewidth=0.9)
            axis.text(80, 0.96, "80% failure", transform=axis.get_xaxis_transform(), rotation=90, va="top", ha="right", fontsize=8, color="#b91c1c")
    fig.suptitle(f"03A Stage-3 — {branch} progressive-loading response", fontsize=16, fontweight="bold")
    fig.text(0.01, 0.01, "Steady-solver iteration sequence; not physical time.", fontsize=8, color="#475569")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_branch_cross_diagnostics(
    output_path: Path,
    branch: str,
    histories: dict[str, dict[str, Any]],
    residuals: dict[str, dict[str, list[float]]],
    checkpoints: list[dict[str, Any]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = branch_checkpoint_rows(checkpoints, branch)
    has_history = branch == "F12" and all(
        key in histories
        for key in (
            "relative_mass_imbalance_abs_path_pct",
            "total_liquid_mass",
            "brine_entry_static_pressure_margin",
            "brine_outlet_total",
            "liquid_to_brine",
        )
    )
    if branch == "F10" and not rows:
        no_data_figure(output_path, f"03A Stage-3 — {branch} branch-specific cross-diagnostics", "NO CROSS-PLOT DATA", "No completed checkpoint or native history is available for this branch.")
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    if has_history:
        axes[0, 0].plot(histories["total_liquid_mass"]["values"], histories["relative_mass_imbalance_abs_path_pct"]["values"], color="#7c3aed", linewidth=0.9)
        axes[0, 0].set_xlabel("Total liquid inventory (kg)")
        axes[0, 0].set_ylabel("Path-magnitude imbalance (%)")
        axes[0, 1].plot(histories["brine_entry_static_pressure_margin"]["values"], histories["brine_outlet_total"]["values"], color="#059669", linewidth=0.9)
        axes[0, 1].set_xlabel("Static pressure margin (Pa)")
        axes[0, 1].set_ylabel("Total brine outlet (kg/s)")
        axes[1, 0].plot(histories["total_liquid_mass"]["values"], histories["liquid_to_brine"]["values"], color="#2563eb", linewidth=0.9)
        axes[1, 0].set_xlabel("Total liquid inventory (kg)")
        axes[1, 0].set_ylabel("Liquid → brine (signed kg/s)")
        epsilon = residuals.get("epsilon", {})
        if epsilon:
            imbalance_by_iteration = dict(zip(histories["relative_mass_imbalance_abs_path_pct"]["iterations"], histories["relative_mass_imbalance_abs_path_pct"]["values"]))
            paired = [(value, imbalance_by_iteration[iteration]) for iteration, value in zip(epsilon["iterations"], epsilon["values"]) if iteration in imbalance_by_iteration]
            if paired:
                axes[1, 1].plot([x for x, _ in paired], [y for _, y in paired], color="#be123c", linewidth=0.9)
        axes[1, 1].set_xlabel("epsilon residual")
        axes[1, 1].set_ylabel("Path-magnitude imbalance (%)")
        title_note = "continuous F12 histories; associations only"
    else:
        row = rows[-1]
        x_values = [row["liquid_inventory_total_kg"]]
        y_values = [row["mass_imbalance_abs_pct"]]
        axes[0, 0].scatter(x_values, y_values, color="#f59e0b", s=60)
        axes[0, 0].set_xlabel("Total liquid inventory (kg)")
        axes[0, 0].set_ylabel("Checkpoint imbalance (%)")
        axes[0, 1].scatter([row["brine_entry_pressure_margin_pa"]], [row["total_outlet_kg_s"]], color="#059669", s=60)
        axes[0, 1].set_xlabel("Static pressure margin (Pa)")
        axes[0, 1].set_ylabel("Checkpoint outlet magnitude (kg/s)")
        axes[1, 0].scatter([row["liquid_inventory_total_kg"]], [row["liquid_to_brine_kg_s"]], color="#2563eb", s=60)
        axes[1, 0].set_xlabel("Total liquid inventory (kg)")
        axes[1, 0].set_ylabel("Liquid → brine checkpoint (kg/s)")
        axes[1, 1].axis("off")
        axes[1, 1].text(0.5, 0.5, "One checkpoint only:\nno trend inference", ha="center", va="center", fontsize=13, color="#b91c1c", fontweight="bold")
        title_note = "checkpoint-only association; no continuous trend inference"
    for axis in axes.flat:
        if axis.axison:
            axis.grid(True, alpha=0.25)
    fig.suptitle(f"03A Stage-3 — {branch} branch-specific cross-diagnostics", fontsize=16, fontweight="bold")
    fig.text(0.01, 0.01, title_note, fontsize=8, color="#475569")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def last_window_stats(series: dict[str, Any] | None, points: int = 500) -> dict[str, Any]:
    if not series:
        return {"points": 0, "first_iteration": None, "last_iteration": None, "median": None, "p95": None, "trend": "unavailable"}
    iterations = list(series.get("iterations", []))
    values = [float(value) for value in series.get("values", []) if math.isfinite(float(value))]
    if not values:
        return {"points": 0, "first_iteration": None, "last_iteration": None, "median": None, "p95": None, "trend": "unavailable"}
    selected_values = values[-points:]
    selected_iterations = iterations[-len(selected_values):]
    return {
        "points": len(selected_values),
        "first_iteration": selected_iterations[0],
        "last_iteration": selected_iterations[-1],
        "median": statistics.median(selected_values),
        "p95": percentile(selected_values, 0.95),
        "trend": describe_trend(selected_values),
    }


def derive_late_window_summary(
    branches: tuple[str, ...],
    branch_histories: dict[str, dict[str, dict[str, Any]]],
    residual_rows: list[dict[str, Any]],
    checkpoints: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for branch in branches:
        branch_residuals = [row for row in residual_rows if row["branch"] == branch]
        by_equation = {row["equation"]: row for row in branch_residuals}
        physical = branch_histories.get(branch, {})
        imbalance_stats = last_window_stats(physical.get("relative_mass_imbalance_abs_path_pct"))
        inventory_stats = last_window_stats(physical.get("total_liquid_mass"))
        pressure_stats = last_window_stats(physical.get("brine_entry_static_pressure_margin"))
        rows = branch_checkpoint_rows(checkpoints, branch)
        final = rows[-1] if rows else {}
        result.append(
            {
                "branch": branch,
                "residual_window_points": by_equation.get("continuity", {}).get("points"),
                "residual_first_iteration": by_equation.get("continuity", {}).get("first_iteration"),
                "residual_last_iteration": by_equation.get("continuity", {}).get("last_iteration"),
                "continuity_median": by_equation.get("continuity", {}).get("median"),
                "continuity_p95": by_equation.get("continuity", {}).get("p95"),
                "k_median": by_equation.get("k", {}).get("median"),
                "epsilon_median": by_equation.get("epsilon", {}).get("median"),
                "physical_late_window_points": imbalance_stats["points"],
                "physical_first_iteration": imbalance_stats["first_iteration"],
                "physical_last_iteration": imbalance_stats["last_iteration"],
                "physical_imbalance_median_pct": imbalance_stats["median"],
                "physical_imbalance_p95_pct": imbalance_stats["p95"],
                "physical_imbalance_trend": imbalance_stats["trend"],
                "liquid_inventory_median_kg": inventory_stats["median"],
                "liquid_inventory_p95_kg": inventory_stats["p95"],
                "liquid_inventory_trend": inventory_stats["trend"],
                "static_margin_median_pa": pressure_stats["median"],
                "final_checkpoint_load_percent": final.get("load_percent"),
                "final_checkpoint_iteration": final.get("iteration"),
                "final_checkpoint_abs_imbalance_pct": final.get("mass_imbalance_abs_pct"),
                "final_checkpoint_liquid_inventory_kg": final.get("liquid_inventory_total_kg"),
            }
        )
    return result


def build_branch_package(
    branch: str,
    branch_output_dir: Path,
    branch_plot_dir: Path,
    histories: dict[str, dict[str, Any]],
    residuals: dict[str, dict[str, list[float]]],
    checkpoints: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
    validation: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = branch_checkpoint_rows(checkpoints, branch)
    branch_residual_rows = [row for row in residual_rows if row["branch"] == branch]
    branch_validation = [row for row in validation if row["branch"] == branch]
    branch_output_dir.mkdir(parents=True, exist_ok=True)
    branch_plot_dir.mkdir(parents=True, exist_ok=True)
    plot_branch_residuals(branch_plot_dir / "residuals.png", branch, residuals)
    plot_branch_physical_convergence(branch_plot_dir / "mass-imbalance-inventory.png", branch, histories, checkpoints)
    plot_branch_phase_routing(branch_plot_dir / "phase-routing.png", branch, histories, checkpoints)
    plot_branch_liquid_distribution(branch_plot_dir / "liquid-distribution.png", branch, histories, checkpoints)
    plot_branch_brine_hydraulics(branch_plot_dir / "brine-pressure-flow.png", branch, histories, checkpoints)
    plot_branch_ramp_response(branch_plot_dir / "ramp-response.png", branch, checkpoints)
    plot_branch_cross_diagnostics(branch_plot_dir / "cross-diagnostics.png", branch, histories, residuals, checkpoints)
    package = {
        "branch": branch,
        "analysis_scope": "branch-by-branch numerical convergence/stabilisation package",
        "checkpoint_count": len(rows),
        "residual_stats": branch_residual_rows,
        "checkpoint_validation": {
            "rows": len(branch_validation),
            "matches": sum(row["status"] == "match" for row in branch_validation),
            "mismatches": sum(row["status"] == "mismatch" for row in branch_validation),
            "unavailable": sum(row["status"].startswith("unavailable") for row in branch_validation),
        },
        "endpoint_summary": endpoint_summary(rows),
        "figures": {
            "residuals": str(branch_plot_dir / "residuals.png"),
            "mass_imbalance_inventory": str(branch_plot_dir / "mass-imbalance-inventory.png"),
            "phase_routing": str(branch_plot_dir / "phase-routing.png"),
            "liquid_distribution": str(branch_plot_dir / "liquid-distribution.png"),
            "brine_pressure_flow": str(branch_plot_dir / "brine-pressure-flow.png"),
            "ramp_response": str(branch_plot_dir / "ramp-response.png"),
            "cross_diagnostics": str(branch_plot_dir / "cross-diagnostics.png"),
        },
    }
    (branch_output_dir / "analysis.json").write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    write_csv(branch_output_dir / "residual-window-statistics.csv", branch_residual_rows)
    write_csv(branch_output_dir / "endpoint-summary.csv", endpoint_summary(rows))
    write_csv(branch_output_dir / "checkpoint-validation.csv", branch_validation)
    return package


def build(args: argparse.Namespace) -> dict[str, Any]:
    report_path = args.report_history
    f08_path = args.f08_residuals
    f12_path = args.f12_residuals
    report_payload = load_report_histories(report_path)
    reports = report_payload["reports"]
    checkpoints = read_checkpoints(args.checkpoints)

    histories = canonical_series(reports)
    validation = validate_checkpoints(checkpoints, histories)
    duplicate_groups = history_duplicate_groups(reports)

    f08_payload = load_json(f08_path)
    f08_histories = f08_payload.get("histories", {}).get("F08", {})
    f12_payload = load_json(f12_path)
    f12_histories = {
        name: {
            "iterations": [int(value) for value in f12_payload.get("iterations", [])],
            "values": [float(value) for value in values],
        }
        for name, values in f12_payload.get("series", {}).items()
    }
    residual_rows = residual_stats(
        "F08",
        "saved stream (source filename identifies 20% resume; endpoint stage not independently re-established)",
        f08_payload.get("availability", {}).get("F08", {}).get("source", f08_path),
        f08_histories,
    )
    residual_rows.extend(residual_stats("F10", "carrier-stage failure", "not saved", {}))
    residual_rows.extend(residual_stats("F12", "100% final retained window", f12_path, f12_histories))

    branch_histories = {
        "F08": {},
        "F10": {},
        "F12": histories,
    }
    branch_residual_histories = {
        "F08": f08_histories,
        "F10": {},
        "F12": f12_histories,
    }
    stats_by_branch: dict[str, list[dict[str, Any]]] = {}
    for row in residual_rows:
        stats_by_branch.setdefault(row["branch"], []).append(row)

    late_window_summary = derive_late_window_summary(BRANCHES, branch_histories, residual_rows, checkpoints)

    artifact_provenance = None
    if ARTIFACT_PROVENANCE_PATH.exists():
        artifact_provenance = load_json(ARTIFACT_PROVENANCE_PATH)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.plot_dir.mkdir(parents=True, exist_ok=True)
    branch_packages: dict[str, dict[str, Any]] = {}
    for branch in BRANCHES:
        branch_packages[branch] = build_branch_package(
            branch,
            args.output_dir / "branches" / branch,
            args.plot_dir / "branches" / branch,
            branch_histories[branch],
            branch_residual_histories[branch],
            checkpoints,
            residual_rows,
            validation,
        )

    summary = {
        "scope": {
            "branches": list(BRANCHES),
            "setup": "03A Stage-3 Fluent-Recommended Convergence Sweep",
            "analysis_mode": "diagnostic numerical convergence/stabilisation",
            "plot_structure": "branch-by-branch packages first; compact late-window cross-branch summary second",
            "interpretation_status": "pending user direction",
        },
        "inputs": {
            "report_history_json": str(report_path),
            "checkpoint_csv": str(args.checkpoints),
            "f08_residual_json": str(f08_path),
            "f12_residual_json": str(f12_path),
            "artifact_provenance_json": str(ARTIFACT_PROVENANCE_PATH),
            "report_history_count": len(reports),
            "report_history_read_errors": report_payload.get("errors", {}),
        },
        "report_history_coverage": {
            name: {
                "points": len(record.get("iterations", [])),
                "first_iteration": record.get("iterations", [None])[0] if record.get("iterations") else None,
                "last_iteration": record.get("iterations", [None])[-1] if record.get("iterations") else None,
            }
            for name, record in reports.items()
        },
        "canonical_sources": RAW_NAMES,
        "canonical_transform_notes": {
            "outlet_and_routing_flows": "negated from Fluent outward-positive report-file sign so checkpoint magnitudes are comparable",
            "routing_checkpoint_comparison": "signed canonical routing histories are retained for backflow diagnosis; checkpoint routing fields are compared using their absolute path magnitudes",
            "total_outlet_abs_path_sum": "sum of absolute values of the four signed phase-routing report histories; this is the checkpoint total-outlet definition",
            "relative_mass_imbalance_abs_path_pct": "100 times the absolute difference between the checkpoint-compatible phase-path magnitude sum and total inlet, divided by total inlet",
            "native_net_report_definition": "native total outlet and native relative imbalance are retained separately; backflow at the 10% F12 checkpoint makes them differ from the checkpoint path-magnitude definition",
            "brine_entry_static_pressure_margin": "static pressure minus 1,120,000 Pa",
        },
        "duplicate_history_groups": duplicate_groups,
        "checkpoint_validation": {
            "rows": len(validation),
            "matches": sum(row["status"] == "match" for row in validation),
            "mismatches": sum(row["status"] == "mismatch" for row in validation),
            "unavailable": sum(row["status"].startswith("unavailable") for row in validation),
        },
        "residual_stats": stats_by_branch,
        "endpoint_summary": endpoint_summary(checkpoints),
        "late_window_summary": late_window_summary,
        "branch_packages": branch_packages,
        "artifact_provenance": artifact_provenance,
        "evidence_quality": {
            "F08": "partial — verified 40% checkpoint and failed 80% attempts; no continuous F08 report-history bundle in this analysis",
            "F10": "unavailable — hybrid initialization and failure evidence exist, but no native solve checkpoint/residual/report history",
            "F12": "complete for 30 native report histories through 18,000; residual evidence is only the retained final 250-point window",
        },
    }

    (args.output_dir / "03A-stage3-session1-analysis.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_csv(args.output_dir / "03A-stage3-session1-checkpoint-validation.csv", validation)
    write_csv(args.output_dir / "03A-stage3-session1-residual-window-statistics.csv", residual_rows)
    write_csv(args.output_dir / "03A-stage3-session1-endpoint-summary.csv", endpoint_summary(checkpoints))
    write_csv(args.output_dir / "03A-stage3-session1-cross-branch-late-window-summary.csv", late_window_summary)

    manifest = {
        "report_history_file": str(report_path),
        "artifact_provenance_file": str(ARTIFACT_PROVENANCE_PATH),
        "reports_read": len(reports),
        "duplicate_history_groups": duplicate_groups,
        "canonical_sources": RAW_NAMES,
        "plot_structure": {
            "branch_packages": {branch: str(args.plot_dir / "branches" / branch) for branch in BRANCHES},
            "cross_branch_summary": str(args.output_dir / "03A-stage3-session1-cross-branch-late-window-summary.csv"),
        },
        "series_available": sorted(histories),
        "branches": {
            "F08": {"status": "checkpoint plus partial saved residual stream", "checkpoint_count": sum(row["branch"] == "F08" for row in checkpoints)},
            "F10": {"status": "no physical endpoint or residual history", "checkpoint_count": 0},
            "F12": {"status": "full native report-history bundle plus endpoint checkpoints", "checkpoint_count": sum(row["branch"] == "F12" for row in checkpoints)},
        },
    }
    (args.output_dir / "03A-stage3-session1-canonical-history-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-history", type=Path, default=None)
    parser.add_argument("--f08-residuals", type=Path, default=PROJECT_ROOT / "output" / "03a_stage3" / "residual-plots" / "03A-stage3-F08-F10-F12-scaled-residuals.json")
    parser.add_argument("--f12-residuals", type=Path, default=None)
    parser.add_argument("--checkpoints", type=Path, default=CHECKPOINT_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--plot-dir", type=Path, default=DEFAULT_PLOT_DIR)
    args = parser.parse_args()
    if args.report_history is None:
        args.report_history = newest_matching(DEFAULT_RAW_DIR, "server1-schedule-d-report-histories_*.json")
    if args.f12_residuals is None:
        args.f12_residuals = newest_matching(PROJECT_ROOT / "output" / "server1-live-plots", "server1_residuals_*.json")
    if args.report_history is None or args.f12_residuals is None:
        parser.error("Could not discover the native report-history JSON or the retained F12 residual JSON")
    return args


def main() -> int:
    args = parse_args()
    summary = build(args)
    print(json.dumps(summary["checkpoint_validation"], indent=2))
    for branch, rows in summary["residual_stats"].items():
        complete = sum(row["status"] == "complete" for row in rows)
        print(f"{branch}: {complete}/{len(rows)} residual equations have saved values")
    print(f"Saved analysis outputs under {args.output_dir}")
    print(f"Saved figures under {args.plot_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
