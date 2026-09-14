#!/usr/bin/env python3
"""Create the planned plot-led evidence package for one Phase-07 screen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load_records(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("reports") if isinstance(payload, dict) and "reports" in payload else payload
    if not isinstance(raw, dict):
        raw = {str(r.get("monitor_name") or r.get("report_file_label")): r for r in raw}
    records = {}
    for key, record in raw.items():
        name = str(record.get("monitor_name") or key).removesuffix("-rfile")
        records[name] = record
    return records


def array(records: dict[str, dict[str, Any]], name: str, field: str = "values") -> np.ndarray:
    if name not in records:
        raise KeyError(f"missing report {name}")
    return np.asarray(records[name][field], dtype=float)


def stats(x: np.ndarray, y: np.ndarray, lo: float, hi: float) -> dict[str, Any]:
    mask = (x >= lo) & (x <= hi)
    xx, yy = x[mask], y[mask]
    slope, intercept = np.polyfit(xx, yy, 1) if len(xx) >= 2 else (float("nan"), float("nan"))
    return {
        "window": [float(lo), float(hi)],
        "points": int(len(xx)),
        "mean": float(np.mean(yy)) if len(yy) else None,
        "minimum": float(np.min(yy)) if len(yy) else None,
        "maximum": float(np.max(yy)) if len(yy) else None,
        "range": float(np.ptp(yy)) if len(yy) else None,
        "slope_per_iteration": float(slope),
        "start": float(yy[0]) if len(yy) else None,
        "end": float(yy[-1]) if len(yy) else None,
    }


def routing(records: dict[str, dict[str, Any]]) -> dict[str, np.ndarray]:
    raw = lambda phase, zone: array(records, f"e0-flux-{phase}-{zone}")
    liq_in = raw("phase2", "liquidinlet") + raw("phase2", "steaminlet")
    liq_out = -(raw("phase2", "steamoutlet") + raw("phase2", "bottom"))
    vap_in = raw("phase1", "liquidinlet") + raw("phase1", "steaminlet")
    vap_out = -(raw("phase1", "steamoutlet") + raw("phase1", "bottom"))
    mix_in = raw("mixture", "liquidinlet") + raw("mixture", "steaminlet")
    mix_out = -(raw("mixture", "steamoutlet") + raw("mixture", "bottom"))
    return {
        "liquid_inflow": liq_in,
        "liquid_outflow": liq_out,
        "liquid_net": liq_in - liq_out,
        "vapor_inflow": vap_in,
        "vapor_outflow": vap_out,
        "vapor_net": vap_in - vap_out,
        "mixture_inflow": mix_in,
        "mixture_outflow": mix_out,
        "mixture_net": mix_in - mix_out,
        "mixture_imbalance_ratio": np.abs(mix_in - mix_out) / 197.61,
        "bottom_vapor_loss_ratio": np.maximum(-raw("phase1", "bottom"), 0.0) / 80.69,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--reports", required=True, type=Path)
    parser.add_argument("--residuals", required=True, type=Path)
    parser.add_argument("--reference-reports", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    records = load_records(args.reports)
    reference = load_records(args.reference_reports)
    residuals = json.loads(args.residuals.read_text(encoding="utf-8"))
    x = np.asarray(array(records, "e0-liquid-mass-total", "iterations"), dtype=float)
    mass = array(records, "e0-liquid-mass-total")
    volume = array(records, "e0-liquid-volume-total")
    route_x = np.asarray(array(records, "e0-flux-mixture-bottom", "iterations"), dtype=float)
    rx = np.asarray(residuals["iterations"], dtype=float)
    late_lo = float(max(x[0], x[-1] - 249))
    late_hi = float(x[-1])
    ref_x = np.asarray(array(reference, "e0-liquid-mass-total", "iterations"), dtype=float)
    ref_mass = array(reference, "e0-liquid-mass-total")

    route = routing(records)
    route_ref = routing(reference)
    setup_id = manifest.get("setup_id", args.manifest.stem)
    adaptive = setup_id.startswith(("P7-E4", "P7-E5-CZ"))

    # F1: direct inventory answer, with the matched E0 reference.
    fig, ax = plt.subplots(figsize=(10, 5.8), constrained_layout=True)
    ax.plot(ref_x, ref_mass, color="#64748b", lw=1.0, ls="--", label="E0 reference")
    ax.plot(x, mass, color="#1d4ed8", lw=1.15, label=setup_id)
    ax.axvspan(late_lo, late_hi, color="#f59e0b", alpha=0.10, label="declared late window")
    ax.set(xlabel="Native solver iteration", ylabel="Continuous-liquid mass [kg]",
           title=f"{setup_id} F1 — liquid inventory versus E0")
    ax.grid(alpha=.25); ax.legend(fontsize=8)
    f1 = args.output_dir / "F1-liquid-inventory-vs-E0.png"
    fig.savefig(f1, dpi=190); plt.close(fig)

    # F2: phase routing and closure, keeping bottom vapor loss explicit.
    fig, axes = plt.subplots(3, 1, figsize=(11, 9.2), sharex=True, constrained_layout=True)
    for ax, title, names in [
        (axes[0], "Liquid routing", ["liquid_inflow", "liquid_outflow", "liquid_net"]),
        (axes[1], "Vapor routing", ["vapor_inflow", "vapor_outflow", "vapor_net"]),
        (axes[2], "Mixture closure and bottom vapor loss", ["mixture_imbalance_ratio", "bottom_vapor_loss_ratio"]),
    ]:
        for name in names:
            ax.plot(route_x, route[name], lw=.9, label=name.replace("_", " "))
        ax.axvspan(late_lo, late_hi, color="#f59e0b", alpha=0.08)
        ax.set_title(title, loc="left", fontsize=10); ax.grid(alpha=.2); ax.legend(fontsize=8, ncol=3)
    axes[0].set_ylabel("kg/s"); axes[1].set_ylabel("kg/s")
    axes[2].set_ylabel("ratio [-]"); axes[2].set_xlabel("Native solver iteration")
    fig.suptitle(f"{setup_id} F2 — phase routing and closure")
    f2 = args.output_dir / "F2-phase-routing-and-closure.png"
    fig.savefig(f2, dpi=190); plt.close(fig)

    # F3: residual history aligned with the mixture imbalance.
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True, constrained_layout=True)
    residual_stats: dict[str, Any] = {}
    for name, values in residuals["series"].items():
        y = np.asarray(values, dtype=float)
        axes[0].semilogy(rx, y, lw=.8, label=name)
        residual_stats[name] = stats(rx, y, late_lo, late_hi)
    axes[0].set_ylabel("Scaled residual [-]"); axes[0].set_title("Native residual histories", loc="left")
    axes[0].grid(alpha=.2, which="both"); axes[0].legend(fontsize=8, ncol=4)
    axes[1].plot(route_x, route["mixture_imbalance_ratio"], color="#7c3aed", lw=.95)
    axes[1].axvspan(late_lo, late_hi, color="#f59e0b", alpha=0.08)
    axes[1].set(xlabel="Native solver iteration", ylabel="|mixture net| / 197.61 [-]", title="Mixture imbalance")
    axes[1].grid(alpha=.2)
    fig.suptitle(f"{setup_id} F3 — numerical adequacy")
    f3 = args.output_dir / "F3-numerical-adequacy.png"
    fig.savefig(f3, dpi=190); plt.close(fig)

    figures = {"F1": str(f1), "F2": str(f2), "F3": str(f3)}
    controller_summary = None
    if adaptive:
        events = [e for e in manifest.get("events", []) if e.get("event") == "controller_update"]
        cx = np.asarray([e["native_iteration"] for e in events], dtype=float)
        cm = np.asarray([e["Mcurrent_kg"] for e in events], dtype=float)
        ce = np.asarray([e["normalized_error"] for e in events], dtype=float)
        cc = np.asarray([e["clamped_command_kg_s"] for e in events], dtype=float)
        fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, constrained_layout=True)
        axes[0].plot(cx, cm, "o-", label="M current [kg]")
        axes[0].axhline(events[0]["Mstar_kg"], color="#64748b", ls="--", label="M* [kg]")
        axes[0].set_ylabel("Liquid mass [kg]"); axes[0].grid(alpha=.2); axes[0].legend(fontsize=8)
        axes[1].plot(cx, cc, "o-", color="#dc2626", label="command [kg/s]")
        axes[1].plot(cx, ce, "s-", color="#2563eb", label="normalized error [-]")
        axes[1].set(xlabel="Native solver iteration", ylabel="controller value", title="Adaptive controller readbacks")
        axes[1].grid(alpha=.2); axes[1].legend(fontsize=8)
        fig.suptitle(f"{setup_id} F4 — adaptive inventory controller")
        f4 = args.output_dir / "F4-adaptive-controller.png"
        fig.savefig(f4, dpi=190); plt.close(fig)
        figures["F4"] = str(f4)
        controller_summary = {
            "updates": len(events),
            "Mstar_kg": events[0]["Mstar_kg"] if events else None,
            "DeltaMref_kg": events[0]["DeltaMref_kg"] if events else None,
            "final_command_kg_s": float(cc[-1]) if len(cc) else None,
            "max_command_kg_s": float(np.max(cc)) if len(cc) else None,
            "saturated_updates": int(sum(bool(e.get("saturated")) for e in events)),
            "phase1_readback_max_kg_s": float(max((e.get("readback", {}).get("phase_1_kg_s", 0.0) for e in events), default=0.0)),
        }

    inventory = {
        "screen": [stats(x, mass, float(x[0]), late_hi), stats(x, mass, late_lo, late_hi)],
        "reference_matched": [stats(ref_x, ref_mass, float(ref_x[0]), min(float(ref_x[-1]), late_hi))],
        "volume_late": stats(x, volume, late_lo, late_hi),
    }
    routing_stats = {name: stats(route_x, values, late_lo, late_hi) for name, values in route.items()}
    out = {
        "setup_id": setup_id,
        "status": "complete_numerical_analysis",
        "requested_active_iterations": manifest.get("requested_active_iterations"),
        "native_coordinate_extent": [int(x[0]), int(x[-1])],
        "report_count": len(records),
        "report_points_each": sorted({int(r["points"]) for r in records.values()}),
        "residual_points": int(residuals["point_count"]),
        "analysis_window": [late_lo, late_hi],
        "inventory": inventory,
        "routing_late": routing_stats,
        "residuals_late": residual_stats,
        "controller": controller_summary,
        "figures": figures,
        "reference": "P7-E0-REF-server1-20260908T170000Z",
        "sign_convention": "Raw Fluent flux positive into domain and negative out; plotted outflow is the negated sum of steamoutlet and bottom raw fluxes.",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
