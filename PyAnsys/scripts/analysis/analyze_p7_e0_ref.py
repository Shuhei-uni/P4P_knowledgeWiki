#!/usr/bin/env python3
"""Produce the predeclared P7-E0-REF numerical evidence package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def stats(x: np.ndarray, y: np.ndarray, lo: int, hi: int) -> dict:
    mask = (x >= lo) & (x <= hi)
    xx, yy = x[mask], y[mask]
    slope, intercept = np.polyfit(xx, yy, 1)
    return {
        "window": [lo, hi], "points": int(len(xx)), "mean": float(np.mean(yy)),
        "minimum": float(np.min(yy)), "maximum": float(np.max(yy)),
        "range": float(np.ptp(yy)), "slope_per_iteration": float(slope),
        "intercept": float(intercept), "start": float(yy[0]), "end": float(yy[-1]),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--reports", required=True, type=Path)
    p.add_argument("--residuals", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--summary", required=True, type=Path)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    reports_payload = json.loads(a.reports.read_text())
    if isinstance(reports_payload, dict) and "reports" in reports_payload:
        report_records = reports_payload["reports"]
    elif isinstance(reports_payload, dict):
        # The E0 runner writes a keyed mapping; the generic report-history
        # extractor writes {"reports": [...]}. Accept both durable forms
        # without changing the scientific identity of any report.
        report_records = list(reports_payload.values())
    else:
        raise ValueError("report history JSON must be a mapping or {reports: [...]}")
    residuals = json.loads(a.residuals.read_text())
    rec = {
        (r.get("monitor_name") or r.get("report_file_label", "")).removesuffix("-rfile"): r
        for r in report_records
    }
    x = np.asarray(rec["e0-liquid-mass-total"]["iterations"], dtype=float)
    series = {k: np.asarray(v["values"], dtype=float) for k, v in rec.items()}

    mass = series["e0-liquid-mass-total"]
    volume = series["e0-liquid-volume-total"]
    windows = [(1000, 1500), (1500, 2000)]
    inventory_stats = {
        "liquid_mass_kg": [stats(x, mass, *w) for w in windows],
        "liquid_volume_m3": [stats(x, volume, *w) for w in windows],
    }

    fig, ax = plt.subplots(figsize=(10, 5.8), constrained_layout=True)
    ax.plot(x, mass, color="#1d4ed8", lw=1.05, label="raw continuous-liquid mass")
    colors = ["#d97706", "#dc2626"]
    for (lo, hi), color in zip(windows, colors):
        s = stats(x, mass, lo, hi)
        mask = (x >= lo) & (x <= hi)
        fit = s["slope_per_iteration"] * x[mask] + s["intercept"]
        ax.plot(x[mask], fit, color=color, lw=2.0,
                label=f"fit {lo}–{hi}: {s['slope_per_iteration']:.4g} kg/iter")
    ax.set(xlabel="Native solver iteration", ylabel="Continuous-liquid mass [kg]",
           title="P7-E0-REF F1 — liquid-inventory reference")
    ax.grid(alpha=.25); ax.legend()
    f1 = a.output_dir / "F1-liquid-inventory-reference.png"
    fig.savefig(f1, dpi=200); plt.close(fig)

    def raw(name: str) -> np.ndarray: return series[f"e0-flux-{name}"]
    liq_in = raw("phase2-liquidinlet") + raw("phase2-steaminlet")
    liq_out = -(raw("phase2-steamoutlet") + raw("phase2-bottom"))
    vap_in = raw("phase1-liquidinlet") + raw("phase1-steaminlet")
    vap_out = -(raw("phase1-steamoutlet") + raw("phase1-bottom"))
    mix_in = raw("mixture-liquidinlet") + raw("mixture-steaminlet")
    mix_out = -(raw("mixture-steamoutlet") + raw("mixture-bottom"))
    liq_net, vap_net, mix_net = liq_in-liq_out, vap_in-vap_out, mix_in-mix_out
    imbalance = np.abs(mix_net) / 197.61
    routing_stats = {name: [stats(x, y, 1500, 2000)][0] for name, y in {
        "liquid_inflow_kg_s": liq_in, "liquid_outflow_kg_s": liq_out,
        "liquid_net_kg_s": liq_net, "vapor_inflow_kg_s": vap_in,
        "vapor_outflow_kg_s": vap_out, "vapor_net_kg_s": vap_net,
        "mixture_inflow_kg_s": mix_in, "mixture_outflow_kg_s": mix_out,
        "mixture_net_kg_s": mix_net, "mixture_imbalance_ratio": imbalance,
    }.items()}
    routing_stats["bottom_raw_fluxes_kg_s"] = {
        phase: {"min": float(np.min(raw(f"{phase}-bottom"))), "max": float(np.max(raw(f"{phase}-bottom")))}
        for phase in ("mixture", "phase1", "phase2")
    }

    fig, axes = plt.subplots(4, 1, figsize=(11, 11), sharex=True, constrained_layout=True)
    for ax, title, vals in [
        (axes[0], "Liquid routing", [(liq_in,"in"),(liq_out,"steam+bottom out"),(liq_net,"net")]),
        (axes[1], "Vapor routing", [(vap_in,"in"),(vap_out,"steam+bottom out"),(vap_net,"net")]),
        (axes[2], "Mixture routing", [(mix_in,"in"),(mix_out,"steam+bottom out"),(mix_net,"net")]),
    ]:
        for y, label in vals: ax.plot(x, y, lw=.9, label=label)
        ax.set_ylabel("Mass rate [kg/s]"); ax.set_title(title, loc="left"); ax.grid(alpha=.2); ax.legend(ncol=3)
    axes[3].plot(x, imbalance, color="#7c3aed", lw=.95)
    axes[3].set(ylabel="|mixture net| / 197.61 [-]", xlabel="Native solver iteration")
    axes[3].grid(alpha=.2)
    fig.suptitle("P7-E0-REF F2 — phase routing and closure")
    f2 = a.output_dir / "F2-phase-routing-and-closure.png"
    fig.savefig(f2, dpi=200); plt.close(fig)

    rx = np.asarray(residuals["iterations"], dtype=float)
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True, constrained_layout=True)
    residual_stats = {}
    for name, values in residuals["series"].items():
        y = np.asarray(values, dtype=float)
        axes[0].semilogy(rx, y, lw=.8, label=name)
        residual_stats[name] = stats(rx, y, 1500, 2000)
    axes[0].set(ylabel="Scaled residual [-]", title="All active solved equations")
    axes[0].grid(alpha=.2, which="both"); axes[0].legend(ncol=4, fontsize=8)
    axes[1].plot(x, imbalance, color="#7c3aed", lw=.95)
    axes[1].set(xlabel="Native solver iteration", ylabel="Mixture imbalance ratio [-]",
                title="Mixture imbalance")
    axes[1].grid(alpha=.2)
    fig.suptitle("P7-E0-REF F3 — numerical adequacy")
    f3 = a.output_dir / "F3-numerical-adequacy.png"
    fig.savefig(f3, dpi=200); plt.close(fig)

    slopes = inventory_stats["liquid_mass_kg"]
    ratio = abs(slopes[1]["slope_per_iteration"] / slopes[0]["slope_per_iteration"]) if slopes[0]["slope_per_iteration"] else None
    out = {
        "setup_id": "P7-E0-REF", "status": "complete_numerical_analysis",
        "sources": {"reports": str(a.reports), "residuals": str(a.residuals)},
        "native_coordinate_extent": [int(x[0]), int(x[-1])],
        "report_count": len(rec), "report_points_each": sorted(set(r["points"] for r in report_records)),
        "residual_points": residuals["point_count"], "inventory": inventory_stats,
        "adjacent_liquid_mass_slope_ratio_abs": ratio,
        "routing_final_500": routing_stats, "residuals_final_500": residual_stats,
        "figures": {"F1": str(f1), "F2": str(f2), "F3": str(f3)},
        "sign_convention": "Raw Fluent flux positive into domain and negative out; plotted outflow is the negated sum of steamoutlet and bottom raw fluxes.",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
