#!/usr/bin/env python3
"""Plot-led analysis for one Phase 7.1A turbulence-family discovery child.

The analyzer keeps the pre-run evidence contract visible: solver histories,
boundary routing/source balance, and selected lower-zone liquid inventories are
reported as finite-horizon observations.  It does not infer convergence or
promote a discovery child to a qualification case.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    raw = payload.get("reports", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw, dict):
        raise ValueError(f"unexpected report payload in {path}")
    records: dict[str, dict[str, Any]] = {}
    for key, record in raw.items():
        label = str(record.get("report_definition") or key).removesuffix("-rfile")
        records[label] = record
        records[str(key).removesuffix("-rfile")] = record
    return records


def record(records: dict[str, dict[str, Any]], name: str) -> dict[str, Any]:
    if name in records:
        return records[name]
    candidates = [value for key, value in records.items() if key.casefold() == name.casefold()]
    if candidates:
        return candidates[0]
    raise KeyError(f"missing report history: {name}")


def values(records: dict[str, dict[str, Any]], name: str, field: str = "values") -> np.ndarray:
    return np.asarray(record(records, name)[field], dtype=float)


def iterations(records: dict[str, dict[str, Any]], name: str) -> np.ndarray:
    return values(records, name, "iterations")


def align(records: dict[str, dict[str, Any]], names: list[str]) -> tuple[np.ndarray, list[np.ndarray]]:
    xs = [iterations(records, name) for name in names]
    ys = [values(records, name) for name in names]
    if not xs:
        raise ValueError("no report series requested")
    n = min(len(x) for x in xs + ys)
    if n == 0:
        raise ValueError(f"empty report series: {names}")
    return xs[0][-n:], [y[-n:] for y in ys]


def finite_stats(x: np.ndarray, y: np.ndarray, start_fraction: float = 0.5) -> dict[str, Any]:
    n = len(y)
    start = min(n - 1, max(0, int(n * start_fraction))) if n else 0
    xx = np.asarray(x[start:], dtype=float)
    yy = np.asarray(y[start:], dtype=float)
    slope = float("nan")
    if len(xx) >= 2 and np.ptp(xx) > 0:
        slope = float(np.polyfit(xx, yy, 1)[0])
    return {
        "points": int(len(yy)),
        "iteration_window": [int(xx[0]), int(xx[-1])] if len(xx) else [],
        "first": float(yy[0]) if len(yy) else None,
        "last": float(yy[-1]) if len(yy) else None,
        "minimum": float(np.min(yy)) if len(yy) else None,
        "maximum": float(np.max(yy)) if len(yy) else None,
        "mean": float(np.mean(yy)) if len(yy) else None,
        "range": float(np.ptp(yy)) if len(yy) else None,
        "slope_per_native_iteration": slope,
    }


def residual_summary(residuals: dict[str, Any]) -> dict[str, Any]:
    x = np.asarray(residuals.get("iterations", []), dtype=float)
    return {
        name: finite_stats(x, np.asarray(series, dtype=float))
        for name, series in (residuals.get("series") or {}).items()
    }


def route(records: dict[str, dict[str, Any]]) -> dict[str, np.ndarray]:
    def raw(phase: str, surface: str) -> np.ndarray:
        return values(records, f"e0-flux-{phase}-{surface}")

    phase2_in = raw("phase2", "liquidinlet") + raw("phase2", "steaminlet")
    phase2_out = -(raw("phase2", "steamoutlet") + raw("phase2", "bottom"))
    phase1_in = raw("phase1", "liquidinlet") + raw("phase1", "steaminlet")
    phase1_out = -(raw("phase1", "steamoutlet") + raw("phase1", "bottom"))
    mixture_in = raw("mixture", "liquidinlet") + raw("mixture", "steaminlet")
    mixture_out = -(raw("mixture", "steamoutlet") + raw("mixture", "bottom"))
    return {
        "phase2_in": phase2_in,
        "phase2_out": phase2_out,
        "phase2_net_no_absorber": phase2_in - phase2_out,
        "phase1_in": phase1_in,
        "phase1_out": phase1_out,
        "phase1_net": phase1_in - phase1_out,
        "mixture_in": mixture_in,
        "mixture_out": mixture_out,
        "mixture_net": mixture_in - mixture_out,
        "bottom_phase1_raw": raw("phase1", "bottom"),
        "bottom_phase2_raw": raw("phase2", "bottom"),
    }


def warning_counts(manifest: dict[str, Any]) -> dict[str, int]:
    text = str(manifest.get("terminal_diagnostics", ""))
    counts = manifest.get("terminal_diagnostics")
    if isinstance(counts, dict):
        return {str(key): int(value) for key, value in counts.items()}
    return {
        "reversed_flow_messages": len(re.findall(r"Reversed flow on", text, re.I)),
        "turbulent_viscosity_limit_messages": len(re.findall(r"turbulent viscosity limited", text, re.I)),
        "amg_divergence_messages": len(re.findall(r"Divergence detected in AMG solver", text, re.I)),
        "floating_point_or_fatal_messages": len(re.findall(r"floating point exception|fatal error", text, re.I)),
    }


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--reports", required=True, type=Path)
    parser.add_argument("--residuals", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_json(args.manifest)
    records = load_records(args.reports)
    residuals = load_json(args.residuals)
    residual_x = np.asarray(residuals["iterations"], dtype=float)
    residual_series = {name: np.asarray(series, dtype=float) for name, series in residuals["series"].items()}

    inventory_names = [
        "e0-liquid-mass-total",
        "e0-liquid-volume-total",
        "absorb-lower-liquid-mass",
        "absorb-adjacent-liquid-mass",
        "absorb-broad-liquid-mass",
    ]
    inventory_x, inventory_y = align(records, inventory_names)
    total_mass, total_volume, lower_mass, adjacent_mass, broad_mass = inventory_y
    routing = route(records)

    # F1 — planned numerical/turbulence evidence.  Raw histories are retained;
    # the shaded region is only a declared late half-window, not a convergence
    # filter or a discarded-tail operation.
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 8), sharex=True, constrained_layout=True)
    for name, series in residual_series.items():
        axes[0].semilogy(residual_x[-len(series):], np.maximum(series, 1e-30), lw=0.8, label=name)
    axes[0].set_ylabel("Scaled residual")
    axes[0].set_title("Turbulence-family discovery residual histories", loc="left")
    axes[0].legend(fontsize=8, ncol=3)
    axes[1].plot(residual_x, residual_series.get("k", np.full_like(residual_x, np.nan)), label="k")
    axes[1].plot(residual_x, residual_series.get("epsilon", np.full_like(residual_x, np.nan)), label="epsilon")
    axes[1].plot(residual_x, residual_series.get("vf-phase-2", np.full_like(residual_x, np.nan)), label="vf-phase-2")
    axes[1].set_xlabel("Native solver iteration")
    axes[1].set_ylabel("Scaled residual")
    axes[1].set_title("Turbulence and phase-fraction residuals", loc="left")
    axes[1].legend(fontsize=8)
    if len(residual_x):
        axes[0].axvspan(residual_x[len(residual_x) // 2], residual_x[-1], color="#cbd5e1", alpha=0.22)
        axes[1].axvspan(residual_x[len(residual_x) // 2], residual_x[-1], color="#cbd5e1", alpha=0.22)
    for ax in axes:
        ax.grid(alpha=0.22, which="both")
    f1 = args.output_dir / "F1-turbulence-stability-history.png"
    save(fig, f1)

    # F2 — coupled boundary routing and the absorber's balance consequence.
    x_route = iterations(records, "e0-flux-mixture-liquidinlet")
    n = min(len(x_route), *(len(series) for series in routing.values()))
    x_route = x_route[-n:]
    rr = {name: series[-n:] for name, series in routing.items()}
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 8), sharex=True, constrained_layout=True)
    axes[0].plot(x_route, rr["phase2_in"], label="phase-2 inlet")
    axes[0].plot(x_route, rr["phase2_out"], label="phase-2 boundary out")
    axes[0].plot(x_route, rr["phase2_net_no_absorber"], label="phase-2 net, no absorber term")
    axes[0].set_ylabel("kg/s")
    axes[0].set_title("Liquid-phase routing around bottom-only absorber", loc="left")
    axes[0].legend(fontsize=8)
    axes[1].plot(x_route, rr["mixture_net"], label="mixture net")
    axes[1].plot(x_route, rr["phase1_net"], label="phase-1 net")
    axes[1].plot(x_route, rr["bottom_phase2_raw"], label="bottom phase-2 raw flux")
    axes[1].axhline(-116.92, color="#dc2626", ls="--", lw=0.9, label="nominal absorber rate −116.92 kg/s")
    axes[1].set_xlabel("Native solver iteration")
    axes[1].set_ylabel("kg/s")
    axes[1].set_title("Mixture/vapor routing and bottom flux", loc="left")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.22)
    f2 = args.output_dir / "F2-coupled-phase-source-balance.png"
    save(fig, f2)

    # F3 — the planned spatial/phase-state evidence available from the
    # selected-cell report histories.  No contour field is fabricated here.
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 8), sharex=True, constrained_layout=True)
    axes[0].plot(inventory_x, total_mass, label="total liquid mass")
    axes[0].plot(inventory_x, lower_mass, label="absorber lower zone")
    axes[0].plot(inventory_x, adjacent_mass, label="adjacent band")
    axes[0].plot(inventory_x, broad_mass, label="broad lower band")
    axes[0].set_ylabel("Liquid mass [kg]")
    axes[0].set_title("Nested selected-cell liquid inventories", loc="left")
    axes[0].legend(fontsize=8)
    axes[1].plot(inventory_x, total_volume, color="#0f766e", label="total liquid volume")
    axes[1].plot(inventory_x, lower_mass / max(1e-30, np.nanmax(total_mass)), color="#dc2626", label="lower mass / max total mass")
    axes[1].set_xlabel("Native solver iteration")
    axes[1].set_ylabel("m³ or normalized mass")
    axes[1].set_title("Phase-state response in the absorber region", loc="left")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.22)
    f3 = args.output_dir / "F3-spatial-phase-state-derived.png"
    save(fig, f3)

    late_stats = {
        "total_liquid_mass_kg": finite_stats(inventory_x, total_mass),
        "total_liquid_volume_m3": finite_stats(inventory_x, total_volume),
        "lower_liquid_mass_kg": finite_stats(inventory_x, lower_mass),
        "adjacent_liquid_mass_kg": finite_stats(inventory_x, adjacent_mass),
        "broad_liquid_mass_kg": finite_stats(inventory_x, broad_mass),
        "phase2_net_without_absorber_kg_s": finite_stats(x_route, rr["phase2_net_no_absorber"]),
        "mixture_net_kg_s": finite_stats(x_route, rr["mixture_net"]),
    }
    summary = {
        "kind": "phase71a_turbulence_closure_analysis",
        "setup_id": manifest.get("setup_id"),
        "run_id": manifest.get("run_id"),
        "manifest_status": manifest.get("status"),
        "requested_active_iterations": manifest.get("requested_active_iterations"),
        "achieved_active_iterations": manifest.get("achieved_active_iterations"),
        "controlled_delta": manifest.get("controlled_delta"),
        "parent_setup_id": manifest.get("parent_setup_id"),
        "parent_sha256": manifest.get("parent_sha256"),
        "report_count": len(records),
        "report_points": sorted({int(rec.get("points", 0)) for rec in records.values()}),
        "residual_point_count": int(residuals.get("point_count", len(residual_x))),
        "late_window_definition": "last half of each complete finite history; raw histories retained",
        "late_window_statistics": late_stats,
        "diagnostics": warning_counts(manifest),
        "source_readback": manifest.get("integrated_source_readback"),
        "figures": {
            "F1": {"path": str(f1), "status": "core", "completeness": "complete", "message": "finite-horizon residual and turbulence/phase-fraction history"},
            "F2": {"path": str(f2), "status": "core", "completeness": "complete", "message": "phase routing and absorber-related balance"},
            "F3": {"path": str(f3), "status": "core", "completeness": "partial", "message": "selected-cell inventory histories; no spatial contours were captured"},
        },
        "observations": [
            "The plots describe the finite discovery horizon only; reaching the requested iteration count is not treated as convergence.",
            "The absorber command is a controlled setting and the integrated source readback remains the required realization evidence.",
            "F3 is derived selected-cell evidence, not a contour or field-based spatial claim.",
        ],
        "claim_limits": [
            "No qualification or hypothesis-route claim is made by this child.",
            "No physical conclusion is inferred from residual or reverse-flow behaviour alone.",
            "F3 contour evidence is unavailable because the queue captured report histories, not field contours.",
        ],
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
