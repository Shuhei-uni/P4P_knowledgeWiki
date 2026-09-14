#!/usr/bin/env python3
"""Plot-led evidence analysis for the cold-start Phase-07 absorber probe.

This analyzer deliberately keeps the three planned discovery questions
separate: inventory response, source realization, and numerical/phase
credibility.  A completed iteration horizon is not promoted to convergence,
and missing pre-run instrumentation is reported rather than reconstructed from
an unrelated quantity.
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
    return records


def values(records: dict[str, dict[str, Any]], name: str, field: str = "values") -> np.ndarray:
    if name not in records:
        raise KeyError(f"missing report history: {name}")
    return np.asarray(records[name][field], dtype=float)


def late_mask(x: np.ndarray, start: int) -> np.ndarray:
    mask = x >= float(start)
    return mask if np.any(mask) else np.ones(len(x), dtype=bool)


def stats(x: np.ndarray, y: np.ndarray, start: int = 700) -> dict[str, Any]:
    mask = late_mask(x, start)
    xx = np.asarray(x[mask], dtype=float)
    yy = np.asarray(y[mask], dtype=float)
    slope = float("nan")
    if len(xx) >= 2 and np.ptp(xx) > 0:
        slope = float(np.polyfit(xx, yy, 1)[0])
    return {
        "points": int(len(yy)),
        "window": [int(xx[0]), int(xx[-1])] if len(xx) else [],
        "start": float(yy[0]) if len(yy) else None,
        "end": float(yy[-1]) if len(yy) else None,
        "minimum": float(np.min(yy)) if len(yy) else None,
        "maximum": float(np.max(yy)) if len(yy) else None,
        "mean": float(np.mean(yy)) if len(yy) else None,
        "range": float(np.ptp(yy)) if len(yy) else None,
        "slope_per_native_iteration": slope,
    }


def residual_stats(residuals: dict[str, Any], start: int = 700) -> dict[str, Any]:
    x = np.asarray(residuals["iterations"], dtype=float)
    return {
        name: stats(x, np.asarray(series, dtype=float), start)
        for name, series in residuals.get("series", {}).items()
    }


def routing(records: dict[str, dict[str, Any]]) -> dict[str, np.ndarray]:
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
        "phase2_net_without_absorber": phase2_in - phase2_out,
        "phase1_in": phase1_in,
        "phase1_out": phase1_out,
        "phase1_net": phase1_in - phase1_out,
        "mixture_in": mixture_in,
        "mixture_out": mixture_out,
        "mixture_net": mixture_in - mixture_out,
        "bottom_phase1_raw": raw("phase1", "bottom"),
        "bottom_phase2_raw": raw("phase2", "bottom"),
    }


def event_series(manifest: dict[str, Any]) -> dict[str, np.ndarray]:
    events = [e for e in manifest.get("events", []) if e.get("event") == "ramp_update"]
    events = sorted(events, key=lambda e: int(e.get("active_iteration", 0)))
    x = np.asarray([float(e.get("active_iteration", 0)) for e in events], dtype=float)
    command = np.asarray([float(e.get("command_kg_s", 0.0)) for e in events], dtype=float)
    measured = np.asarray(
        [-float(e.get("source_audit", {}).get("measured_kg_s", np.nan)) for e in events],
        dtype=float,
    )
    expected = np.asarray(
        [-float(e.get("source_audit", {}).get("expected_kg_s", np.nan)) for e in events],
        dtype=float,
    )
    error = np.asarray(
        [float(e.get("source_audit", {}).get("absolute_error_kg_s", np.nan)) for e in events],
        dtype=float,
    )
    lower = np.asarray(
        [float(e.get("lower_inventory", {}).get("phase2_mass_kg", np.nan)) for e in events],
        dtype=float,
    )
    return {
        "x": x,
        "command": command,
        "measured": measured,
        "expected": expected,
        "audit_error": error,
        "lower_mass": lower,
    }


def warning_counts(manifest: dict[str, Any]) -> dict[str, int]:
    tails = "\n".join(
        str(e.get("warnings", {}).get("console_tail", ""))
        for e in manifest.get("events", [])
        if isinstance(e.get("warnings"), dict)
    )
    return {
        "reversed_flow_messages": len(re.findall(r"Reversed flow on", tails, re.I)),
        "turbulent_viscosity_limit_messages": len(
            re.findall(r"turbulent viscosity limited", tails, re.I)
        ),
        "amg_divergence_messages": len(re.findall(r"Divergence detected in AMG solver", tails, re.I)),
        "floating_point_or_fatal_messages": len(
            re.findall(r"floating point exception|fatal error", tails, re.I)
        ),
    }


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
    x = values(records, "e0-liquid-mass-total", "iterations")
    total_mass = values(records, "e0-liquid-mass-total")
    total_volume = values(records, "e0-liquid-volume-total")
    lower_mass = values(records, "absorb-lower-liquid-mass")
    lower_volume = values(records, "absorb-lower-liquid-volume")
    adjacent_mass = values(records, "absorb-adjacent-liquid-mass")
    broad_mass = values(records, "absorb-broad-liquid-mass")
    route = routing(records)
    events = event_series(manifest)
    final_command = float(manifest.get("final_absorber_rate_kg_s", np.nan))

    # F1 — the direct question: does a fresh start produce bounded inventory?
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True, constrained_layout=True)
    axes[0, 0].plot(x, total_mass, color="#1d4ed8", lw=1.1)
    axes[0, 0].set_title("Total liquid mass", loc="left")
    axes[0, 0].set_ylabel("kg")
    axes[0, 1].plot(x, total_volume, color="#0f766e", lw=1.1)
    axes[0, 1].set_title("Total liquid volume", loc="left")
    axes[0, 1].set_ylabel("m³")
    axes[1, 0].plot(x, lower_mass, color="#dc2626", lw=1.1, label="lower y≤0.10 m")
    axes[1, 0].plot(x, adjacent_mass, color="#d97706", lw=1.0, label="adjacent 0.10–0.30 m")
    axes[1, 0].plot(x, broad_mass, color="#7c3aed", lw=1.0, label="broad y≤0.50 m")
    axes[1, 0].set_title("Nested liquid inventories", loc="left")
    axes[1, 0].set_ylabel("kg")
    axes[1, 0].legend(fontsize=7)
    axes[1, 1].plot(x, lower_volume, color="#dc2626", lw=1.1)
    axes[1, 1].set_title("Lower-zone liquid volume", loc="left")
    axes[1, 1].set_ylabel("m³")
    for ax in axes.flat:
        ax.axvline(100, color="#64748b", ls="--", lw=0.8, label="ramp complete")
        ax.axvspan(700, 1000, color="#cbd5e1", alpha=0.2)
        ax.grid(alpha=0.22)
        ax.set_xlabel("Native solver iteration")
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(f"{manifest.get('setup_id')} F1 — cold-start liquid inventory response")
    f1 = args.output_dir / "F1-cold-start-inventory-response.png"
    fig.savefig(f1, dpi=190)
    plt.close(fig)

    # F2 — source realization and selectivity.  The source audit uses the
    # integrated Fluent get_sum value, not the nominal command alone.
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True, constrained_layout=True)
    ex = events["x"]
    axes[0].plot(ex, events["command"], "o-", ms=2.5, label="scheduled command")
    axes[0].plot(ex, events["measured"], "x", ms=3.0, label="− integrated phase-2 source")
    axes[0].axhline(final_command, color="#334155", ls="--", lw=0.9, label="final target 116.92 kg/s")
    axes[0].set_ylabel("Removal rate [kg/s]")
    axes[0].set_title("Inlet-matched lower-zone absorber realization", loc="left")
    axes[0].legend(fontsize=8)
    axes[1].semilogy(ex, np.maximum(events["audit_error"], 1e-18), "o-", ms=2.5, label="|get_sum − expected| [kg/s]")
    axes[1].plot(ex, events["lower_mass"], color="#dc2626", lw=1.0, label="lower-zone phase-2 mass [kg]")
    axes[1].set_ylabel("Audit error / mass")
    axes[1].set_xlabel("Active iteration at 10-iteration update")
    axes[1].set_title("Source audit and selected-zone inventory", loc="left")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.axvline(100, color="#64748b", ls="--", lw=0.8)
        ax.grid(alpha=0.22, which="both")
    fig.suptitle(f"{manifest.get('setup_id')} F2 — absorber source realization")
    f2 = args.output_dir / "F2-inlet-matched-source-realization.png"
    fig.savefig(f2, dpi=190)
    plt.close(fig)

    # F3 — phase routing and numerical adequacy.  The absence of a vapor
    # inventory report is kept explicit in the summary; vapor flux remains
    # plotted because it was actually recorded.
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True, constrained_layout=True)
    axes[0, 0].plot(x, route["phase2_in"], label="phase-2 in")
    axes[0, 0].plot(x, route["phase2_out"], label="phase-2 outlet/bottom out")
    axes[0, 0].plot(x, route["phase2_net_without_absorber"], label="phase-2 net, no absorber term")
    axes[0, 0].set_title("Liquid-phase boundary routing", loc="left")
    axes[0, 0].set_ylabel("kg/s")
    axes[0, 0].legend(fontsize=7)
    axes[0, 1].plot(x, route["phase1_in"], label="phase-1 in")
    axes[0, 1].plot(x, route["phase1_out"], label="phase-1 out")
    axes[0, 1].plot(x, route["phase1_net"], label="phase-1 net")
    axes[0, 1].set_title("Vapor-phase boundary routing", loc="left")
    axes[0, 1].set_ylabel("kg/s")
    axes[0, 1].legend(fontsize=7)
    axes[1, 0].plot(x, route["mixture_net"], color="#7c3aed", label="mixture net")
    axes[1, 0].plot(x, route["bottom_phase2_raw"], color="#dc2626", label="bottom phase-2 raw")
    axes[1, 0].plot(x, route["bottom_phase1_raw"], color="#d97706", label="bottom phase-1 raw")
    axes[1, 0].set_title("Mixture closure and bottom flux", loc="left")
    axes[1, 0].set_ylabel("kg/s")
    axes[1, 0].legend(fontsize=7)
    rx = np.asarray(residuals["iterations"], dtype=float)
    for name, series in residuals["series"].items():
        axes[1, 1].semilogy(rx, np.asarray(series, dtype=float), lw=0.75, label=name)
    axes[1, 1].set_title("Residual histories", loc="left")
    axes[1, 1].set_ylabel("Scaled residual")
    axes[1, 1].legend(fontsize=7, ncol=2)
    for ax in axes.flat:
        ax.axvline(100, color="#64748b", ls="--", lw=0.8)
        ax.axvspan(700, 1000, color="#cbd5e1", alpha=0.2)
        ax.grid(alpha=0.2, which="both")
        ax.set_xlabel("Native solver iteration")
    fig.suptitle(f"{manifest.get('setup_id')} F3 — numerical and vapor credibility")
    f3 = args.output_dir / "F3-numerical-and-vapor-credibility.png"
    fig.savefig(f3, dpi=190)
    plt.close(fig)

    source_errors = events["audit_error"]
    warning_summary = warning_counts(manifest)
    report_last = {name: int(record["iterations"][-1]) for name, record in records.items()}
    summary = {
        "setup_id": manifest.get("setup_id"),
        "run_id": manifest.get("run_id"),
        "manifest_status": manifest.get("status"),
        "requested_active_iterations": manifest.get("requested_active_iterations"),
        "achieved_active_iterations": manifest.get("achieved_active_iterations"),
        "report_count": len(records),
        "report_points_each": sorted({int(record["points"]) for record in records.values()}),
        "report_last_iteration_by_name": report_last,
        "residual_points": int(residuals.get("point_count", 0)),
        "late_analysis_window": [700, 1000],
        "inventory": {
            "total_liquid_mass_kg": stats(x, total_mass),
            "total_liquid_volume_m3": stats(x, total_volume),
            "lower_liquid_mass_kg": stats(x, lower_mass),
            "lower_liquid_volume_m3": stats(x, lower_volume),
            "adjacent_liquid_mass_kg": stats(x, adjacent_mass),
            "broad_liquid_mass_kg": stats(x, broad_mass),
        },
        "source_realization": {
            "updates": int(len(ex)),
            "command_min_kg_s": float(np.nanmin(events["command"])),
            "command_max_kg_s": float(np.nanmax(events["command"])),
            "integrated_measured_removal_min_kg_s": float(np.nanmin(events["measured"])),
            "integrated_measured_removal_max_kg_s": float(np.nanmax(events["measured"])),
            "max_absolute_get_sum_error_kg_s": float(np.nanmax(source_errors)),
            "direct_phase1_source_off_all_updates": bool(
                all(e.get("direct_phase1_source_off") is True for e in manifest.get("events", []) if e.get("event") == "ramp_update")
            ),
        },
        "routing_late": {name: stats(x, series) for name, series in route.items()},
        "residuals_late": residual_stats(residuals),
        "warnings": warning_summary,
        "evidence_completeness": {
            "F1": "complete",
            "F2": "complete",
            "F3": "partial",
            "missing": [
                "No vapor-inventory report history was configured in the executed child; F3 uses recorded phase-1 fluxes and residuals only."
            ],
        },
        "figures": {
            "F1": {"path": str(f1), "status": "core", "completeness": "complete"},
            "F2": {"path": str(f2), "status": "core", "completeness": "complete"},
            "F3": {"path": str(f3), "status": "core", "completeness": "partial"},
        },
        "claim_limits": [
            "This is a finite-horizon numerical discovery result, not a converged or physically qualified separator prediction.",
            "The absorber source was realized and audited in the selected lower cell zone, but the lower zone contained no phase-2 liquid in this cold-start history.",
            "Total liquid inventory increased across the horizon; this does not prove the mechanism can never remove liquid after liquid reaches the zone, but it does not support a bounded cold-start branch here.",
            "No vapor-inventory history was captured, so vapor compatibility is assessed only from phase-1 boundary fluxes and residuals.",
        ],
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
