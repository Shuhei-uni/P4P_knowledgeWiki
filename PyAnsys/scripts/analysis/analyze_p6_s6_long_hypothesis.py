#!/usr/bin/env python3
"""Make the four predeclared Phase-06 Stage-06 hypothesis-test figures.

This post-processor consumes portable, read-only report-history and residual
captures.  It does not connect to Fluent or modify any solver state.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument("--reports", type=Path, required=True)
    argument_parser.add_argument("--runner", type=Path, required=True)
    argument_parser.add_argument(
        "--residuals",
        type=Path,
        help="Optional PyFluent residual capture. Omit only when the capture failed and F4 must remain unavailable.",
    )
    argument_parser.add_argument("--output-dir", type=Path, required=True)
    argument_parser.add_argument("--target-kg", type=float, default=200.0)
    argument_parser.add_argument("--late-window", type=int, default=1000)
    return argument_parser


def history(records: dict[str, dict[str, Any]], report_definition: str) -> tuple[np.ndarray, np.ndarray]:
    if report_definition not in records:
        raise KeyError(f"Required report definition is absent: {report_definition}")
    record = records[report_definition]
    return (
        np.asarray(record["iterations"], dtype=float),
        np.asarray(record["values"], dtype=float),
    )


def summary(values: np.ndarray, x: np.ndarray, late_window: int) -> dict[str, float]:
    if len(values) < late_window:
        raise ValueError(f"Need at least {late_window} points, received {len(values)}")
    window_values = values[-late_window:]
    window_x = x[-late_window:]
    slope = np.polyfit(window_x, window_values, 1)[0]
    return {
        "initial": float(values[0]),
        "final": float(values[-1]),
        "delta": float(values[-1] - values[0]),
        "late_mean": float(np.mean(window_values)),
        "late_min": float(np.min(window_values)),
        "late_max": float(np.max(window_values)),
        "late_slope_per_iteration": float(slope),
    }


def main() -> int:
    args = parser().parse_args()
    if args.late_window <= 1:
        raise ValueError("late-window must be greater than one")
    reports_payload = json.loads(args.reports.read_text(encoding="utf-8"))
    runner = json.loads(args.runner.read_text(encoding="utf-8"))
    residuals = (
        json.loads(args.residuals.read_text(encoding="utf-8"))
        if args.residuals is not None
        else None
    )
    errors = reports_payload.get("errors", [])
    if errors:
        raise RuntimeError(f"Report recovery has errors: {errors}")
    records = {
        str(item["report_definition"]): item
        for item in reports_payload.get("reports", [])
    }
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    x, y010 = history(records, "03a_stage3_inventory_y010_liquid_mass")
    _, y030 = history(records, "03a_stage3_inventory_y030_liquid_mass")
    _, total = history(records, "03a_stage3_inventory_total_liquid_mass")
    chunk_rows = runner.get("chunks", [])
    if len(chunk_rows) != int(runner.get("chunks_requested", 0)):
        raise RuntimeError("Runner manifest does not prove all requested control chunks completed")
    controller_x = np.asarray(
        [float(chunk["report_iteration_after"]) for chunk in chunk_rows], dtype=float
    )
    controller_p = np.asarray(
        [float(chunk["pressure_after_pa"]) for chunk in chunk_rows], dtype=float
    ) / 1_000_000.0
    controller_x = np.insert(controller_x, 0, float(chunk_rows[0]["report_iteration_before"]))
    controller_p = np.insert(controller_p, 0, float(chunk_rows[0]["pressure_before_pa"]) / 1_000_000.0)

    figure, axes = plt.subplots(2, 1, figsize=(9, 6.8), sharex=True, constrained_layout=True)
    axes[0].plot(x, y010, label="phase-2 mass, y≤0.10 m", color="#1d4ed8")
    axes[0].axhline(args.target_kg, color="black", linestyle="--", linewidth=1, label=f"assumed target ({args.target_kg:g} kg)")
    axes[0].set(ylabel="Phase-2 liquid mass [kg]", title="F1 — numerical-pool proxy and bounded pressure action")
    axes[0].grid(alpha=0.25)
    axes[0].legend(fontsize=8)
    axes[1].step(controller_x, controller_p, where="post", color="#b45309", label="read-back brine pressure")
    axes[1].set(xlabel="Native Fluent iteration", ylabel="Brine pressure [MPa gauge]")
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=8)
    figure.savefig(output_dir / "f1_proxy_and_pressure.png", dpi=180)
    plt.close(figure)

    x, inlet_raw = history(records, "03a_stage3_flux_phase2_liquid_inlet")
    _, brine_raw = history(records, "03a_stage3_flux_phase2_brine_outlet")
    _, steam_raw = history(records, "03a_stage3_flux_phase2_steam_outlet")
    brine_out = -brine_raw
    steam_out = -steam_raw
    net = inlet_raw - brine_out - steam_out
    figure, axis = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    axis.plot(x, inlet_raw, label="liquid inlet (Fluent sign)")
    axis.plot(x, brine_out, label="liquid discharge to brine (− Fluent report)")
    axis.plot(x, steam_out, label="liquid discharge to steam (− Fluent report)")
    axis.plot(x, net, color="black", linewidth=1.6, label="derived inlet − brine − steam")
    axis.axhline(0, color="black", linewidth=0.7)
    axis.set(xlabel="Native Fluent iteration", ylabel="Liquid mass rate [kg/s]", title="F2 — phase-2 liquid balance (physical discharge sign)")
    axis.grid(alpha=0.25)
    axis.legend(fontsize=8, ncol=2)
    figure.savefig(output_dir / "f2_phase_liquid_balance.png", dpi=180)
    plt.close(figure)

    x, full_imbalance = history(records, "03a_stage3_full_domain_mass_imbalance")
    _, relative_imbalance = history(records, "03a_stage3_relative_mass_imbalance")
    figure, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True, constrained_layout=True)
    axes[0].plot(x, y010, label="y≤0.10 m")
    axes[0].plot(x, y030, label="y≤0.30 m")
    axes[0].plot(x, total, label="total phase-2 mass")
    axes[0].set_ylabel("Liquid mass [kg]")
    axes[0].legend(fontsize=8)
    axes[1].plot(x, full_imbalance, color="#991b1b")
    axes[1].axhline(0, color="black", linewidth=0.7)
    axes[1].set_ylabel("Full imbalance [kg/s]")
    axes[2].plot(x, relative_imbalance, color="#7c3aed")
    axes[2].set(xlabel="Native Fluent iteration", ylabel="Relative imbalance [−]")
    for axis in axes:
        axis.grid(alpha=0.25)
    figure.suptitle("F3 — storage and mass-closure histories")
    figure.savefig(output_dir / "f3_storage_and_closure.png", dpi=180)
    plt.close(figure)

    residual_summary: dict[str, Any]
    if residuals is None:
        residual_summary = {
            "status": "UNAVAILABLE",
            "reason": "The post-run PyFluent residual monitor did not populate before timeout; no replacement diagnostic was substituted.",
        }
    else:
        residual_x = np.asarray(residuals.get("iterations", []), dtype=float)
        residual_series = residuals.get("series", {})
        if len(residual_x) < int(runner.get("total_incremental_iterations", 0)):
            raise RuntimeError("Residual capture is shorter than the declared incremental horizon")
        if not residual_series:
            raise RuntimeError("Residual capture contains no equations")
        figure, axis = plt.subplots(figsize=(9, 5.2), constrained_layout=True)
        for name, raw_values in residual_series.items():
            values = np.asarray(raw_values, dtype=float)
            usable = min(len(residual_x), len(values))
            axis.plot(residual_x[-usable:], values[-usable:], linewidth=0.8, label=str(name))
        axis.set_yscale("log")
        axis.set(xlabel="Fluent residual iteration coordinate", ylabel="Scaled residual", title="F4 — residual history over the retained horizon")
        axis.grid(True, which="both", alpha=0.22)
        axis.legend(fontsize=7, ncol=2)
        figure.savefig(output_dir / "f4_residual_history.png", dpi=180)
        plt.close(figure)
        residual_summary = {
            "status": "COMPLETE",
            "point_count": int(len(residual_x)),
            "curve_count": int(len(residual_series)),
        }

    expected_incremental = int(runner["total_incremental_iterations"])
    if int(x[-1] - x[0] + 1) < expected_incremental:
        raise RuntimeError("Primary report history is shorter than the requested horizon")
    summary_payload = {
        "kind": "p6_s6_long_hypothesis_analysis",
        "target_proxy_kg": args.target_kg,
        "late_window_points": args.late_window,
        "native_late_window": [int(x[-args.late_window]), int(x[-1])],
        "report_history_points": int(len(x)),
        "residual_capture": residual_summary,
        "proxy_y010_mass_kg": summary(y010, x, args.late_window),
        "proxy_y030_mass_kg": summary(y030, x, args.late_window),
        "total_phase2_mass_kg": summary(total, x, args.late_window),
        "liquid_net_rate_kg_s": summary(net, x, args.late_window),
        "full_mass_imbalance_kg_s": summary(full_imbalance, x, args.late_window),
        "relative_mass_imbalance": summary(relative_imbalance, x, args.late_window),
        "controller": {
            "minimum_pressure_mpa_gauge": float(np.min(controller_p)),
            "maximum_pressure_mpa_gauge": float(np.max(controller_p)),
            "final_pressure_mpa_gauge": float(controller_p[-1]),
            "at_lower_bound_endpoints": int(np.count_nonzero(np.isclose(controller_p, 1.115))),
        },
        "sign_convention": {
            "raw_outlet_reports": "Fluent reports are negative for outward liquid flux in this F11 lineage.",
            "derived_net_liquid_rate": "liquid inlet − physical brine discharge − physical steam discharge; numerically equal to raw inlet + raw brine + raw steam.",
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary_payload, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
