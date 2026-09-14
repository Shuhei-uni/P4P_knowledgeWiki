#!/usr/bin/env python3
"""Analyse the valid portion of the cold-start 1000-to-5000 continuation.

The solver diverged before the requested horizon in this run.  This analyser
therefore preserves the valid endpoint, stitches parent and continuation
histories on the active-iteration coordinate, and marks the missing horizon
and inherited vapor-inventory history explicitly.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze_p7_e5_cz_absorb_cold import routing  # noqa: E402
from run_p7_treatment_screen import parse_residuals  # noqa: E402


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


def merge_report_records(
    parent: dict[str, dict[str, Any]],
    continuation: dict[str, dict[str, Any]],
    last_valid: int,
) -> dict[str, dict[str, Any]]:
    if set(parent) != set(continuation):
        raise ValueError("parent and continuation report sets differ")
    merged: dict[str, dict[str, Any]] = {}
    for name in sorted(parent):
        p = parent[name]
        c = continuation[name]
        pi = [int(x) for x in p["iterations"]]
        pv = [float(x) for x in p["values"]]
        ci = [int(x) for x in c["iterations"]]
        cv = [float(x) for x in c["values"]]
        if not pi or pi[-1] != 1000:
            raise ValueError(f"parent history does not end at active 1000: {name}")
        pairs = [(x, y) for x, y in zip(ci, cv) if 1000 < x <= last_valid]
        iterations = pi + [x for x, _ in pairs]
        values = pv + [y for _, y in pairs]
        if not iterations or iterations[-1] != last_valid:
            raise ValueError(f"continuation history does not reach valid endpoint {last_valid}: {name}")
        merged[name] = {
            "report_file_label": c.get("report_file_label", name),
            "x_label": c.get("x_label", "iteration"),
            "report_definition": name,
            "points": len(iterations),
            "iterations": iterations,
            "values": values,
        }
    return merged


def merge_residuals(parent: dict[str, Any], continuation_text: str, last_valid: int) -> dict[str, Any]:
    continuation = parse_residuals(continuation_text)
    p_iter = [int(x) for x in parent["iterations"]]
    c_iter = [int(x) for x in continuation["iterations"]]
    if p_iter[-1] != 1000:
        raise ValueError("parent residual history does not end at 1000")
    keep = [i for i, x in enumerate(c_iter) if 1000 < x <= last_valid]
    names = list(parent["series"])
    if names != list(continuation["series"]):
        raise ValueError("parent and continuation residual columns differ")
    residuals = {
        "iterations": p_iter + [c_iter[i] for i in keep],
        "series": {
            name: [float(x) for x in parent["series"][name]]
            + [float(continuation["series"][name][i]) for i in keep]
            for name in names
        },
        "point_count": len(p_iter) + len(keep),
        "curve_count": len(names),
        "source": "parent JSON + continuation Fluent transcript, trimmed at last valid active iteration",
        "continuation_raw_point_count": int(continuation["point_count"]),
        "continuation_raw_last_iteration": int(c_iter[-1]),
        "last_valid_active_iteration": last_valid,
    }
    return residuals


def arr(records: dict[str, dict[str, Any]], name: str, field: str = "values") -> np.ndarray:
    if name not in records:
        raise KeyError(f"missing report history: {name}")
    return np.asarray(records[name][field], dtype=float)


def finite_stats(x: np.ndarray, y: np.ndarray, start: int, end: int | None = None) -> dict[str, Any]:
    mask = np.isfinite(x) & np.isfinite(y) & (x >= start)
    if end is not None:
        mask &= x <= end
    xx = x[mask]
    yy = y[mask]
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
        "slope_per_active_iteration": slope,
    }


def source_events(manifest: dict[str, Any], last_valid: int) -> list[dict[str, Any]]:
    selected: dict[int, dict[str, Any]] = {}
    for event in manifest.get("events", []):
        if event.get("event") != "continuation_source_update":
            continue
        total = int(event.get("total_active_iteration", -1))
        if 1000 <= total <= last_valid:
            selected[total] = event
    return [selected[x] for x in sorted(selected)]


def warning_counts(manifest: dict[str, Any]) -> dict[str, int]:
    text = "\n".join(
        [
            str(e.get("warnings", {}).get("console_tail", ""))
            for e in manifest.get("events", [])
            if isinstance(e.get("warnings"), dict)
        ]
        + [str(manifest.get("terminal_solver_diagnostics", {}).get("console_tail", ""))]
    )
    return {
        "reversed_flow_messages": len(re.findall(r"Reversed flow on", text, re.I)),
        "turbulent_viscosity_limit_messages": len(re.findall(r"turbulent viscosity limited", text, re.I)),
        "amg_divergence_messages": len(re.findall(r"Divergence detected in AMG solver", text, re.I)),
        "floating_point_or_fatal_messages": len(re.findall(r"floating point exception|fatal error", text, re.I)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--parent-reports", required=True, type=Path)
    parser.add_argument("--continuation-reports", required=True, type=Path)
    parser.add_argument("--parent-residuals", required=True, type=Path)
    parser.add_argument("--continuation-transcript", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--residuals-output", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_json(args.manifest)
    last_valid = int(manifest["last_valid_total_active_iteration"])
    parent_records = load_records(args.parent_reports)
    continuation_records = load_records(args.continuation_reports)
    records = merge_report_records(parent_records, continuation_records, last_valid)
    residuals = merge_residuals(
        load_json(args.parent_residuals),
        args.continuation_transcript.read_text(encoding="utf-8"),
        last_valid,
    )
    args.residuals_output.parent.mkdir(parents=True, exist_ok=True)
    args.residuals_output.write_text(json.dumps(residuals, indent=2) + "\n", encoding="utf-8")

    x = arr(records, "e0-liquid-mass-total", "iterations")
    total_mass = arr(records, "e0-liquid-mass-total")
    total_volume = arr(records, "e0-liquid-volume-total")
    lower_mass = arr(records, "absorb-lower-liquid-mass")
    lower_volume = arr(records, "absorb-lower-liquid-volume")
    adjacent_mass = arr(records, "absorb-adjacent-liquid-mass")
    broad_mass = arr(records, "absorb-broad-liquid-mass")
    route = routing(records)
    events = source_events(manifest, last_valid)
    ex = np.asarray([float(e["total_active_iteration"]) for e in events])
    command = np.asarray([float(e["command_kg_s"]) for e in events])
    measured = np.asarray([-float(e["source_audit"]["measured_kg_s"]) for e in events])
    audit_error = np.asarray([float(e["source_audit"]["absolute_error_kg_s"]) for e in events])
    event_lower = np.asarray([float(e["lower_inventory"]["phase2_mass_kg"]) for e in events])

    # F1: active-iteration inventory response, with the requested continuation boundary explicit.
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True, constrained_layout=True)
    axes[0, 0].plot(x, total_mass, color="#1d4ed8", lw=1.0)
    axes[0, 0].set_title("Total liquid mass", loc="left")
    axes[0, 0].set_ylabel("kg")
    axes[0, 1].plot(x, total_volume, color="#0f766e", lw=1.0)
    axes[0, 1].set_title("Total liquid volume", loc="left")
    axes[0, 1].set_ylabel("m³")
    axes[1, 0].plot(x, lower_mass, color="#dc2626", lw=1.0, label="lower y≤0.10 m")
    axes[1, 0].plot(x, adjacent_mass, color="#d97706", lw=0.9, label="adjacent 0.10–0.30 m")
    axes[1, 0].plot(x, broad_mass, color="#7c3aed", lw=0.9, label="broad y≤0.50 m")
    axes[1, 0].set_title("Nested liquid inventories", loc="left")
    axes[1, 0].set_ylabel("kg")
    axes[1, 0].legend(fontsize=7)
    axes[1, 1].plot(x, lower_volume, color="#dc2626", lw=1.0)
    axes[1, 1].set_title("Lower-zone liquid volume", loc="left")
    axes[1, 1].set_ylabel("m³")
    for ax in axes.flat:
        ax.axvline(1000, color="#64748b", ls="--", lw=0.8, label="continuation start")
        ax.axvline(last_valid, color="#b91c1c", ls=":", lw=0.9, label="last valid")
        ax.grid(alpha=0.22)
        ax.set_xlabel("Active iteration")
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(f"{manifest.get('setup_id')} F1 — stitched cold-start inventory response")
    f1 = args.output_dir / "F1-stitched-inventory-response.png"
    fig.savefig(f1, dpi=190)
    plt.close(fig)

    # F2: source realization and lower-zone inventory at the 10-iteration audits.
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True, constrained_layout=True)
    axes[0].plot(ex, command, "o-", ms=2.5, label="command")
    axes[0].plot(ex, measured, "x", ms=3.0, label="− integrated phase-2 source")
    axes[0].axhline(116.92, color="#334155", ls="--", lw=0.9, label="116.92 kg/s")
    axes[0].set_ylabel("Removal rate [kg/s]")
    axes[0].set_title("Fixed lower-zone absorber realization", loc="left")
    axes[0].legend(fontsize=8)
    axes[1].semilogy(ex, np.maximum(audit_error, 1e-18), "o-", ms=2.5, label="|get_sum − expected| [kg/s]")
    axes[1].plot(ex, np.maximum(event_lower, 1e-18), color="#dc2626", lw=1.0, label="lower phase-2 mass [kg]")
    axes[1].set_ylabel("Audit error / mass")
    axes[1].set_xlabel("Active iteration at source audit")
    axes[1].set_title("Source audit and selected-zone inventory", loc="left")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.axvline(1000, color="#64748b", ls="--", lw=0.8)
        ax.axvline(last_valid, color="#b91c1c", ls=":", lw=0.9)
        ax.grid(alpha=0.22, which="both")
    fig.suptitle(f"{manifest.get('setup_id')} F2 — absorber source realization")
    f2 = args.output_dir / "F2-source-realization-and-lower-inventory.png"
    fig.savefig(f2, dpi=190)
    plt.close(fig)

    # F3: phase routing and residuals through the valid endpoint.
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
        axes[1, 1].semilogy(rx, np.maximum(np.asarray(series, dtype=float), 1e-30), lw=0.7, label=name)
    axes[1, 1].set_title("Residual histories through last valid iteration", loc="left")
    axes[1, 1].set_ylabel("Scaled residual")
    axes[1, 1].legend(fontsize=7, ncol=2)
    for ax in axes.flat:
        ax.axvline(1000, color="#64748b", ls="--", lw=0.8)
        ax.axvline(last_valid, color="#b91c1c", ls=":", lw=0.9)
        ax.grid(alpha=0.2, which="both")
        ax.set_xlabel("Active iteration")
    fig.suptitle(f"{manifest.get('setup_id')} F3 — routing and numerical credibility")
    f3 = args.output_dir / "F3-routing-and-numerical-credibility.png"
    fig.savefig(f3, dpi=190)
    plt.close(fig)

    def late_stats(series: np.ndarray) -> dict[str, Any]:
        return {
            "parent_late_700_1000": finite_stats(x, series, 700, 1000),
            "continuation_1000_1960": finite_stats(x, series, 1001, last_valid),
            "last_1600_1960": finite_stats(x, series, 1600, last_valid),
        }

    source_audit_max = float(np.nanmax(audit_error)) if len(audit_error) else float("nan")
    direct_phase1_off = all(
        bool(e.get("direct_phase1_source_off"))
        for e in events
        if "direct_phase1_source_off" in e
    )
    summary = {
        "setup_id": manifest.get("setup_id"),
        "run_id": manifest.get("run_id"),
        "manifest_status": manifest.get("status"),
        "requested_total_active_iteration": manifest.get("requested_total_active_iteration"),
        "achieved_last_valid_active_iteration": last_valid,
        "solver_failure_iteration": manifest.get("terminal_solver_diagnostics", {}).get("total_active_iteration"),
        "additional_valid_iterations": last_valid - 1000,
        "report_count": len(records),
        "report_points_each": sorted({int(record["points"]) for record in records.values()}),
        "report_last_iteration": int(x[-1]),
        "residual_points": int(residuals["point_count"]),
        "residual_last_iteration": int(residuals["iterations"][-1]),
        "inventory": {
            "total_liquid_mass_kg": late_stats(total_mass),
            "total_liquid_volume_m3": late_stats(total_volume),
            "lower_liquid_mass_kg": late_stats(lower_mass),
            "lower_liquid_volume_m3": late_stats(lower_volume),
            "adjacent_liquid_mass_kg": late_stats(adjacent_mass),
            "broad_liquid_mass_kg": late_stats(broad_mass),
        },
        "source_realization": {
            "unique_audit_updates": int(len(events)),
            "command_min_kg_s": float(np.nanmin(command)),
            "command_max_kg_s": float(np.nanmax(command)),
            "integrated_measured_removal_min_kg_s": float(np.nanmin(measured)),
            "integrated_measured_removal_max_kg_s": float(np.nanmax(measured)),
            "max_absolute_get_sum_error_kg_s": source_audit_max,
            "direct_phase1_source_off_all_audits": direct_phase1_off,
        },
        "routing": {name: late_stats(series) for name, series in route.items()},
        "warnings": warning_counts(manifest),
        "evidence_completeness": {
            "F1": "complete through last valid active iteration",
            "F2": "complete through last valid active iteration",
            "F3": "partial",
            "missing": [
                "Requested total active 5000 was not reached; solver divergence/fatal diagnostic occurred in block ending at 1970.",
                "No vapor-inventory report history was configured in the parent/continuation package; vapor compatibility is assessed only from phase-1 fluxes and residuals.",
                "No final active-5000 save/reopen exists because the solver failed before that horizon.",
            ],
        },
        "figures": {
            "F1": {"path": str(f1), "status": "core", "completeness": "complete-to-1960"},
            "F2": {"path": str(f2), "status": "core", "completeness": "complete-to-1960"},
            "F3": {"path": str(f3), "status": "core", "completeness": "partial"},
        },
        "claim_limits": [
            "This is a finite-horizon continuation result, not a converged or physically qualified separator prediction.",
            "The fixed phase-2 source was realized and audited at approximately 116.92 kg/s, but lower-zone liquid remained negligible relative to total liquid inventory.",
            "Total liquid inventory continued to rise through the valid endpoint and the solver then diverged; the run does not support a bounded cold-start branch for this unchanged absorber setting.",
            "Because the requested 5000 horizon was not reached, no claim is made about behaviour beyond active 1960.",
            "No vapor-inventory history was captured, so vapor compatibility is not fully qualified.",
        ],
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
