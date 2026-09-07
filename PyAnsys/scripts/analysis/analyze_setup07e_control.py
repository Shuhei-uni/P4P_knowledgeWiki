#!/usr/bin/env python3
"""Analyze setup-07e adaptive control without making physical-outlet claims."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mass_balance_sink_control_20260810"
    / "mesh-900k_band0p140165_target116p92_v1"
)
SETUP07D_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_strong_sink_sensitivity_20260810"
    / "mesh-900k_band0p140165_tau0p020_v1"
)
TARGET_KGS = 116.92


def span_percent(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    if abs(mean) <= 1.0e-30:
        return None
    return (max(values) - min(values)) / abs(mean) * 100.0


def endpoint_metrics(row: pd.Series) -> dict[str, float]:
    return {
        "cumulative_iteration": int(row["iteration"]),
        "r1_iteration": int(row["r1_iteration"]),
        "ramp": float(row["ramp"]),
        "tau_s": float(row["tau_s"]),
        "sink_magnitude_kgs": float(row["sink_magnitude_kgs"]),
        "commanded_sink_kgs": TARGET_KGS * float(row["ramp"]),
        "liquid_removed_fraction_percent": 100.0 * float(row["sink_magnitude_kgs"]) / TARGET_KGS,
        "corrected_liquid_imbalance_percent": float(row["liquid_imbalance_percent"]),
        "mixture_source_inclusive_imbalance_percent": float(row["mixture_source_augmented_imbalance_percent"]),
        "domain_liquid_inventory_kg": float(row["domain_liquid_inventory_kg"]),
        "band_liquid_inventory_kg": float(row["bottom_layer_liquid_inventory_kg"]),
        "pressure_drop_kpa": float(row["pressure_drop_pa"]) / 1000.0,
        "vapor_steamoutlet_kgs_out": abs(float(row["vapor_steamoutlet_kgs"])),
        "liquid_steamoutlet_kgs_out": abs(float(row["liquid_steamoutlet_kgs"])),
        "carrier_quality_percent_trend_only": float(row["carrier_outlet_quality_percent_trend_only"]),
        "outlet_velocity_ms": float(row["outlet_area_weighted_velocity_ms"]),
        "domain_velocity_ms": float(row["domain_volume_avg_velocity_ms"]),
        "domain_vorticity_s-1": float(row["domain_volume_avg_vorticity_s-1"]),
    }


def control_statistics(frame: pd.DataFrame, manifest: dict[str, Any]) -> dict[str, Any]:
    records = frame.copy()
    records["commanded_sink_kgs"] = TARGET_KGS * records["ramp"]
    records["tracking_error_percent_of_command"] = (
        (records["sink_magnitude_kgs"] - records["commanded_sink_kgs"]).abs()
        / records["commanded_sink_kgs"].where(records["commanded_sink_kgs"] > 0.0)
        * 100.0
    )
    active = records[
        (records["bottom_layer_liquid_inventory_kg"] > 1.0e-9)
        & (records["commanded_sink_kgs"] > 0.0)
    ]
    tau_history = manifest.get("adaptive_tau_history", [])
    minimum = float(manifest["adaptive_tau_bounds_s"][0])
    maximum = float(manifest["adaptive_tau_bounds_s"][1])
    return {
        "feedback_updates_recorded": len(tau_history),
        "rows_with_liquid_in_band": len(active),
        "tau_used_min_s": float(records["tau_s"].min()),
        "tau_used_max_s": float(records["tau_s"].max()),
        "tau_next_at_minimum_count": sum(abs(float(item["tau_next_s"]) - minimum) <= 1.0e-12 for item in tau_history),
        "tau_next_at_maximum_count": sum(abs(float(item["tau_next_s"]) - maximum) <= 1.0e-12 for item in tau_history),
        "active_band_tracking_error_percent": {
            "minimum": float(active["tracking_error_percent_of_command"].min()) if not active.empty else None,
            "median": float(median(active["tracking_error_percent_of_command"].tolist())) if not active.empty else None,
            "maximum": float(active["tracking_error_percent_of_command"].max()) if not active.empty else None,
            "endpoint": float(active.iloc[-1]["tracking_error_percent_of_command"]) if not active.empty else None,
        },
        "interpretation": "Tracking error measures numerical feedback response only; it is not brine-outlet validation.",
    }


def independent_final_window(frame: pd.DataFrame) -> dict[str, Any] | None:
    r1 = frame[frame["r1_iteration"] > 0].copy()
    if r1.empty or int(r1.iloc[-1]["r1_iteration"]) < 500:
        return None
    end = int(r1.iloc[-1]["r1_iteration"])
    start = end - 500
    window = r1[r1["r1_iteration"] >= start]
    fields = {
        "pressure_drop_pa": 0.5,
        "sink_magnitude_kgs": 0.5,
        "domain_liquid_inventory_kg": 0.5,
        "vapor_steamoutlet_kgs": 0.5,
        "outlet_area_weighted_velocity_ms": 1.0,
        "domain_volume_avg_velocity_ms": 1.0,
        "domain_volume_avg_vorticity_s-1": 1.0,
    }
    stability = {}
    for field, limit in fields.items():
        drift = span_percent([float(value) for value in window[field]])
        stability[field] = {
            "samples": len(window),
            "drift_percent": drift,
            "limit_percent": limit,
            "pass": drift is not None and drift <= limit,
        }
    return {
        "r1_window_start": start,
        "r1_window_end": end,
        "samples": len(window),
        "stability": stability,
        "all_physical_monitors_pass": all(item["pass"] for item in stability.values()),
    }


def residual_statistics(frame: pd.DataFrame, window_points: int = 100) -> dict[str, Any]:
    """Summarize residual endpoints and direction without inferring convergence."""
    window = frame.tail(min(window_points, len(frame))).copy()
    fields = [
        "continuity",
        "vf-phase-2",
        "k",
        "epsilon",
        "x-velocity",
        "y-velocity",
        "z-velocity",
    ]
    statistics: dict[str, Any] = {}
    for field in fields:
        first = float(window.iloc[0][field])
        endpoint = float(window.iloc[-1][field])
        change = None
        if abs(first) > 1.0e-30:
            change = (endpoint - first) / abs(first) * 100.0
        statistics[field] = {
            "endpoint": endpoint,
            "window_first": first,
            "window_minimum": float(window[field].min()),
            "window_maximum": float(window[field].max()),
            "endpoint_change_percent": change,
        }
    return {
        "samples": int(len(window)),
        "iteration_start": int(window.iloc[0]["iteration"]),
        "iteration_end": int(window.iloc[-1]["iteration"]),
        "statistics": statistics,
        "interpretation": (
            "Endpoint change describes direction over the recorded window; it "
            "does not by itself establish residual convergence."
        ),
    }


def dry_band_lineage_parity(frame: pd.DataFrame) -> dict[str, Any]:
    """Compare only exact saved iterations before setup-07e feedback is active."""
    reference_path = SETUP07D_DIR / "physical_monitor_history.csv"
    reference = (
        pd.read_csv(reference_path)
        .drop_duplicates("iteration", keep="last")
        .sort_values("iteration")
    )
    dry = frame[frame["bottom_layer_liquid_inventory_kg"].abs() <= 1.0e-9]
    reference_dry = reference[
        reference["bottom_layer_liquid_inventory_kg"].abs() <= 1.0e-9
    ]
    matched = dry.merge(reference_dry, on="iteration", suffixes=("_07e", "_07d"))
    fields = {
        "pressure_drop_pa": 0.5,
        "domain_liquid_inventory_kg": 0.5,
        "mixture_steamoutlet_kgs": 0.5,
        "vapor_steamoutlet_kgs": 0.5,
        "outlet_area_weighted_velocity_ms": 1.0,
        "domain_volume_avg_velocity_ms": 1.0,
        "domain_volume_avg_vorticity_s-1": 1.0,
    }
    comparisons: dict[str, Any] = {}
    for field, limit in fields.items():
        differences: list[float] = []
        for _, row in matched.iterrows():
            current = float(row[f"{field}_07e"])
            control = float(row[f"{field}_07d"])
            denominator = max(abs(control), 1.0e-30)
            differences.append(abs(current - control) / denominator * 100.0)
        maximum = max(differences) if differences else None
        comparisons[field] = {
            "maximum_absolute_percent_difference": maximum,
            "limit_percent": limit,
            "pass": maximum is not None and maximum <= limit,
        }
    return {
        "reference": str(reference_path),
        "matched_iterations": [int(value) for value in matched["iteration"].tolist()],
        "matched_rows": int(len(matched)),
        "comparisons": comparisons,
        "all_fields_pass": bool(comparisons)
        and all(item["pass"] for item in comparisons.values()),
        "interpretation": (
            "Exact-iteration dry-band parity tests clean-start lineage only; it "
            "does not validate adaptive feedback or the sink surrogate."
        ),
    }


def render_markdown(analysis: dict[str, Any]) -> str:
    endpoint = analysis["endpoint"]
    control = analysis["control_statistics"]
    title = "Setup 07e Adaptive Mass-Balance Control Result" if analysis["final"] else "Setup 07e Adaptive Mass-Balance Control Interim Analysis"
    lines = [
        f"# {title}",
        "",
        f"**Controller status:** `{analysis['controller_status']}`  ",
        f"**Evidence classification:** `{analysis['classification']}`",
        "",
        "This is an empirical numerical mass-balance control using the qualified local liquid sink. It is not a physical brine-outlet boundary and cannot validate separator efficiency, mesh independence, a free surface or physical-time accumulation.",
        "",
        "## Latest recorded state",
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| Total / full-strength iteration | `{endpoint['cumulative_iteration']} / {endpoint['r1_iteration']}` |",
        f"| Ramp / tau | `{endpoint['ramp']:.3g} / {endpoint['tau_s']:.6g} s` |",
        f"| Commanded / achieved sink | `{endpoint['commanded_sink_kgs']:.4f} / {endpoint['sink_magnitude_kgs']:.4f} kg/s` |",
        f"| Corrected liquid imbalance | `{endpoint['corrected_liquid_imbalance_percent']:.4f}%` |",
        f"| Source-inclusive mixture imbalance | `{endpoint['mixture_source_inclusive_imbalance_percent']:.4f}%` |",
        f"| Domain / band liquid inventory | `{endpoint['domain_liquid_inventory_kg']:.5f} / {endpoint['band_liquid_inventory_kg']:.6g} kg` |",
        f"| Pressure drop | `{endpoint['pressure_drop_kpa']:.4f} kPa` |",
        f"| Vapor / liquid through steam outlet | `{endpoint['vapor_steamoutlet_kgs_out']:.5f} / {endpoint['liquid_steamoutlet_kgs_out']:.6g} kg/s` |",
        f"| Outlet / domain velocity | `{endpoint['outlet_velocity_ms']:.5f} / {endpoint['domain_velocity_ms']:.5f} m/s` |",
        f"| Domain vorticity | `{endpoint['domain_vorticity_s-1']:.5f} s^-1` |",
        "",
        "## Feedback evidence",
        "",
        f"- Feedback updates recorded: `{control['feedback_updates_recorded']}`.",
        f"- Samples with liquid in the active band: `{control['rows_with_liquid_in_band']}`.",
        f"- Tau used range: `{control['tau_used_min_s']:.6g}-{control['tau_used_max_s']:.6g} s`.",
        f"- Next-tau lower/upper-bound selections: `{control['tau_next_at_minimum_count']}/{control['tau_next_at_maximum_count']}`.",
    ]
    tracking = control["active_band_tracking_error_percent"]
    if tracking["endpoint"] is None:
        lines.append("- The liquid front has not yet produced a reportable active-band feedback response; no tracking claim is made.")
    else:
        lines.append(f"- Active-band command-tracking error: median `{tracking['median']:.4f}%`, endpoint `{tracking['endpoint']:.4f}%`.")
    residual = analysis["residual_statistics"]
    lines.extend(
        [
            "",
            "## Residual evidence",
            "",
            f"Recorded iterations `{residual['iteration_start']}-{residual['iteration_end']}` "
            f"(`{residual['samples']}` samples). Endpoint change is directional only.",
            "",
            "| Residual | Endpoint | Window endpoint change |",
            "|---|---:|---:|",
        ]
    )
    for name, item in residual["statistics"].items():
        change = item["endpoint_change_percent"]
        change_text = "n/a" if change is None else f"{change:+.3f}%"
        lines.append(f"| `{name}` | `{item['endpoint']:.6g}` | `{change_text}` |")
    parity = analysis["dry_band_lineage_parity"]
    lines.extend(
        [
            "",
            "## Dry-band lineage parity",
            "",
            f"Exact matched saved iterations: `{parity['matched_iterations']}`. "
            f"All controlled fields pass: `{parity['all_fields_pass']}`.",
            "",
            "| Field | Maximum difference | Limit | Result |",
            "|---|---:|---:|---|",
        ]
    )
    for name, item in parity["comparisons"].items():
        difference = item["maximum_absolute_percent_difference"]
        difference_text = "n/a" if difference is None else f"{difference:.6f}%"
        lines.append(
            f"| `{name}` | `{difference_text}` | `{item['limit_percent']:.1f}%` | "
            f"`{'PASS' if item['pass'] else 'FAIL'}` |"
        )
    lines.append(
        "\nThis audit covers repeatable clean-start lineage only; it does not "
        "validate feedback tracking or physical outlet behavior."
    )
    lines.extend(["", "## Stability and acceptance", ""])
    window = analysis["independent_final_500"]
    if window is None:
        lines.append("A complete 500-iteration full-strength window is not yet available.")
    else:
        lines.extend(["| Monitor | Drift | Limit | Result |", "|---|---:|---:|---|"])
        for name, item in window["stability"].items():
            lines.append(f"| `{name}` | `{item['drift_percent']:.4f}%` | `{item['limit_percent']:.1f}%` | `{'PASS' if item['pass'] else 'FAIL'}` |")
    if analysis["authoritative_acceptance_window"]:
        authoritative = analysis["authoritative_acceptance_window"]
        lines.extend(
            [
                "",
                f"Controller acceptance-window pass: `{authoritative.get('acceptance_window_pass')}`; balance pass: `{authoritative.get('balance_pass')}`; residual-level pass: `{authoritative.get('residual_level_pass')}`; residual non-growing: `{authoritative.get('residual_non_growing')}`.",
            ]
        )
    lines.extend(
        [
            "",
            "## Decision rule",
            "",
            "Numerical closure is informative only if pressure, liquid inventory, velocity/swirl monitors and residual histories also stabilize over two consecutive accepted windows. Even then, the result remains a diagnostic control and a resolved brine outlet is required for physical claims.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    manifest = json.loads((RUN_DIR / "qualification_manifest.json").read_text(encoding="utf-8"))
    physical = pd.read_csv(RUN_DIR / "physical_monitor_history.csv").drop_duplicates("iteration", keep="last").sort_values("iteration")
    residual = pd.read_csv(RUN_DIR / "residual_history.csv").drop_duplicates("iteration", keep="last").sort_values("iteration")
    if physical.empty:
        raise RuntimeError("physical monitor history is empty")
    final = manifest.get("status") == "completed"
    classification = str(manifest.get("classification", "diagnostic/unresolved"))
    analysis: dict[str, Any] = {
        "study_id": manifest["study_id"],
        "run_label": manifest["run_label"],
        "controller_status": manifest.get("status"),
        "classification": classification,
        "final": final,
        "dpm": manifest.get("dpm"),
        "dpm_after_run": manifest.get("dpm_after_run"),
        "checkpoint_keys": sorted(manifest.get("checkpoints", {}).keys()),
        "endpoint": endpoint_metrics(physical.iloc[-1]),
        "control_statistics": control_statistics(physical, manifest),
        "independent_final_500": independent_final_window(physical),
        "authoritative_acceptance_window": manifest.get("latest_500_iteration_assessment"),
        "stable_windows_observed": int(manifest.get("stable_windows_observed", 0)),
        "stop_reason": manifest.get("stop_reason", ""),
        "residual_statistics": residual_statistics(residual),
        "dry_band_lineage_parity": dry_band_lineage_parity(physical),
        "residual_endpoint": {
            field: float(residual.iloc[-1][field])
            for field in residual.columns
            if field != "iteration"
        },
        "limitations": [
            "The adaptive source is numerical global feedback through a local volumetric sink, not outlet hydraulics.",
            "Steam-outlet quality remains trend-only without a resolved liquid outlet.",
            "Steady iterations are not physical time.",
            "No DPM, EWF, separator-efficiency or mesh-convergence claim is permitted.",
        ],
    }
    stem = "QUALIFICATION_RESULT" if final else "INTERIM_ANALYSIS"
    (RUN_DIR / f"{stem}.json").write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
    (RUN_DIR / f"{stem}.md").write_text(render_markdown(analysis), encoding="utf-8")
    print(RUN_DIR / f"{stem}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
