#!/usr/bin/env python3
"""Deterministically evaluate one Phase 7.1A autoresearch experiment.

The evaluator reads the reset Fluent .out histories created by
prepare_p71a_evaluation_reports.py and emits one compact evaluation.json.
It deliberately keeps the objectives lexicographic rather than collapsing
scientifically different goals into one weighted scalar.

Current primary routing evidence is an inventory-based proxy using the already
validated Phase 7 lower/adjacent/broad reports.  A dedicated horizontal
phase-2 flux plane can replace that proxy later without changing the outer
contract.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from prepare_p71a_evaluation_reports import REQUIRED_REPORT_DEFINITIONS  # noqa: E402


DEFAULT_LIQUID_INLET_KG_S = 116.92
EPS = 1.0e-12


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def finite(values: Sequence[float]) -> list[float]:
    return [float(value) for value in values if math.isfinite(float(value))]


def linear_slope(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) < 2 or len(y) < 2:
        return float("nan")
    x_mean = statistics.fmean(x)
    y_mean = statistics.fmean(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    if denominator <= EPS:
        return float("nan")
    return sum((xx - x_mean) * (yy - y_mean) for xx, yy in zip(x, y)) / denominator


def late_stats(record: Mapping[str, Any], count: int) -> dict[str, Any]:
    raw_x = [float(value) for value in record.get("iterations", [])]
    raw_y = [float(value) for value in record.get("values", [])]
    n = min(count, len(raw_x), len(raw_y))
    if n <= 0:
        raise ValueError(f"empty report history: {record.get('report_definition')}")
    x = raw_x[-n:]
    y = raw_y[-n:]
    good = [(xx, yy) for xx, yy in zip(x, y) if math.isfinite(xx) and math.isfinite(yy)]
    if not good:
        raise ValueError(f"no finite late-window samples: {record.get('report_definition')}")
    x = [item[0] for item in good]
    y = [item[1] for item in good]
    slope = linear_slope(x, y)
    mean = statistics.fmean(y)
    return {
        "points": len(y),
        "iteration_start": x[0],
        "iteration_end": x[-1],
        "start": y[0],
        "end": y[-1],
        "mean": mean,
        "median": statistics.median(y),
        "minimum": min(y),
        "maximum": max(y),
        "range": max(y) - min(y),
        "slope_per_iteration": slope,
    }


def aligned_late_values(records: Mapping[str, Mapping[str, Any]], names: Sequence[str], count: int) -> list[list[float]]:
    arrays = [[float(value) for value in records[name]["values"]] for name in names]
    n = min([count] + [len(array) for array in arrays])
    if n <= 0:
        raise ValueError(f"no aligned values for reports: {names}")
    return [array[-n:] for array in arrays]


def late_mean_expression(
    records: Mapping[str, Mapping[str, Any]],
    names: Sequence[str],
    coefficients: Sequence[float],
    count: int,
) -> float:
    arrays = aligned_late_values(records, names, count)
    values = [sum(c * array[index] for c, array in zip(coefficients, arrays)) for index in range(len(arrays[0]))]
    values = finite(values)
    if not values:
        return float("nan")
    return statistics.fmean(values)


def clamp01(value: float) -> float:
    if not math.isfinite(value):
        return 0.0
    return max(0.0, min(1.0, value))


def read_reports(solver: Any, report_dir: Path) -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for name in REQUIRED_REPORT_DEFINITIONS:
        path = report_dir / f"{name}.out"
        if not remote_file_exists(solver, str(path)):
            missing.append(name)
            continue
        parsed = parse_report_forms(read_remote_forms(solver, str(path)))
        parsed["resolved_file_name"] = str(path)
        reports[name] = parsed
    if missing:
        raise FileNotFoundError("missing required evaluation reports: " + ", ".join(missing))
    return reports


def sink_from_manifest(manifest: Mapping[str, Any], fallback: float) -> dict[str, Any]:
    events = manifest.get("events", [])
    if isinstance(events, list):
        for event in reversed(events):
            if not isinstance(event, Mapping):
                continue
            audit = event.get("source_audit")
            if isinstance(audit, Mapping) and audit.get("measured_kg_s") is not None:
                measured = float(audit["measured_kg_s"])
                return {"removal_kg_s": abs(measured), "source": "manifest.latest_source_audit.measured_kg_s"}
            for key in ("clamped_command_kg_s", "requested_command_kg_s"):
                if event.get(key) is not None:
                    return {"removal_kg_s": abs(float(event[key])), "source": f"manifest.latest_event.{key}"}
    for key in ("absorber_command_kg_s_final", "source_cap_kg_s"):
        if manifest.get(key) is not None:
            return {"removal_kg_s": abs(float(manifest[key])), "source": f"manifest.{key}"}
    return {"removal_kg_s": abs(float(fallback)), "source": "command_line_or_default"}


def continuity_summary(residuals: Mapping[str, Any], count: int) -> dict[str, Any]:
    series = residuals.get("series", {})
    iterations = residuals.get("iterations", [])
    if not isinstance(series, Mapping) or not isinstance(iterations, list):
        return {"available": False}
    name = next((str(key) for key in series if "continuity" in str(key).casefold()), None)
    if name is None:
        return {"available": False}
    values = [float(value) for value in series[name]]
    n = min(count, len(values), len(iterations))
    if n <= 0:
        return {"available": False}
    record = {
        "report_definition": name,
        "iterations": iterations[-n:],
        "values": values[-n:],
    }
    stats = late_stats(record, n)
    median = max(abs(float(stats["median"])), EPS)
    stats.update(
        {
            "available": True,
            "series_name": name,
            "quality": -math.log10(median),
            "improving": bool(float(stats["end"]) <= float(stats["start"])),
        }
    )
    return stats


def evaluate(
    records: Mapping[str, Mapping[str, Any]],
    manifest: Mapping[str, Any],
    residuals: Mapping[str, Any],
    late_count: int,
    liquid_inlet_kg_s: float,
    fallback_sink_kg_s: float,
) -> dict[str, Any]:
    inventories = {
        name: late_stats(records[name], late_count)
        for name in (
            "e0-liquid-mass-total",
            "absorb-lower-liquid-mass",
            "absorb-adjacent-liquid-mass",
            "absorb-broad-liquid-mass",
        )
    }
    total = inventories["e0-liquid-mass-total"]
    lower = inventories["absorb-lower-liquid-mass"]
    adjacent = inventories["absorb-adjacent-liquid-mass"]
    broad = inventories["absorb-broad-liquid-mass"]

    total_mean = max(abs(float(total["mean"])), EPS)
    broad_mean = max(abs(float(broad["mean"])), EPS)
    broad_share_total = clamp01(float(broad["mean"]) / total_mean)
    lower_share_broad = clamp01(float(lower["mean"]) / broad_mean)

    # V0 routing proxy.  The broad y<=0.50 m inventory carries most weight;
    # lower-zone concentration is secondary because a strong absorber can
    # legitimately keep the immediate sink zone relatively lean.
    routing_index = clamp01(0.80 * broad_share_total + 0.20 * lower_share_broad)

    span = max(float(total["iteration_end"]) - float(total["iteration_start"]), 1.0)
    inventory_drift_fraction = abs(float(total["slope_per_iteration"])) * span / total_mean

    p2_in = late_mean_expression(
        records,
        ("e0-flux-phase2-liquidinlet", "e0-flux-phase2-steaminlet"),
        (1.0, 1.0),
        late_count,
    )
    p2_out = late_mean_expression(
        records,
        ("e0-flux-phase2-steamoutlet", "e0-flux-phase2-bottom"),
        (-1.0, -1.0),
        late_count,
    )
    mixture_in = late_mean_expression(
        records,
        ("e0-flux-mixture-liquidinlet", "e0-flux-mixture-steaminlet"),
        (1.0, 1.0),
        late_count,
    )
    mixture_out = late_mean_expression(
        records,
        ("e0-flux-mixture-steamoutlet", "e0-flux-mixture-bottom"),
        (-1.0, -1.0),
        late_count,
    )
    steamoutlet_liquid_net = late_mean_expression(
        records,
        ("e0-flux-phase2-steamoutlet",),
        (1.0,),
        late_count,
    )

    sink = sink_from_manifest(manifest, fallback_sink_kg_s)
    sink_rate = float(sink["removal_kg_s"])
    p2_balance_error = abs((p2_in - p2_out) - sink_rate) / max(abs(liquid_inlet_kg_s), EPS)
    mixture_balance_error = abs((mixture_in - mixture_out) - sink_rate) / max(abs(mixture_in), EPS)
    carryover_fraction = abs(steamoutlet_liquid_net) / max(abs(liquid_inlet_kg_s), EPS)
    continuity = continuity_summary(residuals, late_count)
    continuity_quality = float(continuity.get("quality", -99.0))

    selection_vector = [
        1,
        routing_index,
        -p2_balance_error,
        -mixture_balance_error,
        continuity_quality,
        -carryover_fraction,
        -inventory_drift_fraction,
    ]

    return {
        "status": "VALID",
        "objective_order": [
            "valid_run",
            "downward_liquid_routing_proxy",
            "phase2_mass_balance",
            "mixture_mass_balance",
            "continuity_quality",
            "low_steamoutlet_liquid",
            "bounded_total_liquid_inventory",
        ],
        "selection_vector_higher_is_better": selection_vector,
        "primary": {
            "downward_liquid_routing_proxy": routing_index,
            "broad_y_le_0p50_share_of_total": broad_share_total,
            "lower_y_le_0p10_share_of_broad": lower_share_broad,
            "basis": "inventory proxy; replace with dedicated horizontal phase-2 downward flux when that monitor is live-qualified",
        },
        "secondary": {
            "phase2_balance_error_fraction_of_liquid_inlet": p2_balance_error,
            "mixture_balance_error_fraction_of_mixture_inlet": mixture_balance_error,
            "continuity": continuity,
            "steamoutlet_liquid_net_kg_s": steamoutlet_liquid_net,
            "steamoutlet_liquid_net_fraction_of_liquid_inlet": carryover_fraction,
            "total_liquid_late_window_drift_fraction": inventory_drift_fraction,
        },
        "routing": {
            "phase2_in_kg_s": p2_in,
            "phase2_out_kg_s": p2_out,
            "mixture_in_kg_s": mixture_in,
            "mixture_out_kg_s": mixture_out,
            "absorber": sink,
        },
        "inventories": inventories,
        "diagnostic": {
            "adjacent_over_total": float(adjacent["mean"]) / total_mean,
            "late_window_points_requested": late_count,
            "liquid_inlet_reference_kg_s": liquid_inlet_kg_s,
            "warning": "steamoutlet metric is net phase-2 flux and can hide simultaneous reverse/outgoing flow",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--residuals", type=Path)
    parser.add_argument("--late-count", type=int, default=500)
    parser.add_argument("--liquid-inlet-kg-s", type=float, default=DEFAULT_LIQUID_INLET_KG_S)
    parser.add_argument("--absorber-sink-kg-s", type=float, default=DEFAULT_LIQUID_INLET_KG_S)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report_dir = args.report_dir.expanduser().resolve()
    output = (args.output or report_dir / "evaluation.json").expanduser().resolve()
    manifest = load_json(args.manifest)
    residuals = load_json(args.residuals)

    try:
        solver = connect(server_id=args.server_id, start_transcript=False)
        records = read_reports(solver, report_dir)
        result = evaluate(
            records=records,
            manifest=manifest,
            residuals=residuals,
            late_count=max(1, args.late_count),
            liquid_inlet_kg_s=args.liquid_inlet_kg_s,
            fallback_sink_kg_s=args.absorber_sink_kg_s,
        )
        result["report_dir"] = str(report_dir)
        result["report_count"] = len(records)
        result["manifest"] = str(args.manifest) if args.manifest else None
        result["residuals"] = str(args.residuals) if args.residuals else None
        write_json(output, result)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        failure = {
            "status": "TECHNICAL_FAILURE",
            "error": f"{type(exc).__name__}: {exc}",
            "selection_vector_higher_is_better": [0, 0.0, -1.0e99, -1.0e99, -99.0, -1.0e99, -1.0e99],
            "instruction": (
                "Do not reject the scientific idea from this result. Repair/retry the run or evidence pipeline first."
            ),
        }
        write_json(output, failure)
        print(json.dumps(failure, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
