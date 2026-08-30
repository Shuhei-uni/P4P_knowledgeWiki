#!/usr/bin/env python3
"""Make the three predeclared Stage-01 reference-screen figures."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    records = {item["report_definition"]: item for item in raw["reports"]}
    args.output_dir.mkdir(parents=True, exist_ok=True)

    def series(name: str) -> tuple[np.ndarray, np.ndarray]:
        item = records[name]
        return np.array(item["iterations"], dtype=float), np.array(item["values"], dtype=float)

    x, y010 = series("03a_stage3_inventory_y010_liquid_mass")
    _, y030 = series("03a_stage3_inventory_y030_liquid_mass")
    _, total = series("03a_stage3_inventory_total_liquid_mass")
    fig, ax = plt.subplots(figsize=(8, 4.4), constrained_layout=True)
    ax.plot(x, y010, label="phase-2 mass, y≤0.10 m")
    ax.plot(x, y030, label="phase-2 mass, y≤0.30 m")
    ax.plot(x, total, label="total phase-2 mass", alpha=.75)
    ax.set(xlabel="Native Fluent iteration", ylabel="Liquid mass [kg]", title="F1 — lower-region liquid inventory response")
    ax.grid(alpha=.25); ax.legend(fontsize=8)
    fig.savefig(args.output_dir / "f1_lower_region_inventory.png", dpi=180); plt.close(fig)

    x, liquid_in = series("03a_stage3_flux_phase2_liquid_inlet")
    _, liquid_brine = series("03a_stage3_flux_phase2_brine_outlet")
    _, liquid_steam = series("03a_stage3_flux_phase2_steam_outlet")
    net = liquid_in + liquid_brine + liquid_steam
    fig, ax = plt.subplots(figsize=(8, 4.4), constrained_layout=True)
    ax.plot(x, liquid_in, label="liquid inlet")
    ax.plot(x, liquid_brine, label="liquid → brine")
    ax.plot(x, liquid_steam, label="liquid → steam")
    ax.plot(x, net, label="derived net liquid rate", linewidth=2, color="black")
    ax.axhline(0, color="black", linewidth=.7)
    ax.set(xlabel="Native Fluent iteration", ylabel="Mass flow [kg/s]", title="F2 — phase-resolved liquid balance")
    ax.grid(alpha=.25); ax.legend(fontsize=8, ncol=2)
    fig.savefig(args.output_dir / "f2_phase_resolved_liquid_balance.png", dpi=180); plt.close(fig)

    x, rel = series("03a_stage3_relative_mass_imbalance")
    _, full = series("03a_stage3_full_domain_mass_imbalance")
    _, p = series("03a_stage3_brine_entry_static_pressure")
    fig, axes = plt.subplots(3, 1, figsize=(8, 7.2), sharex=True, constrained_layout=True)
    axes[0].plot(x, rel); axes[0].set_ylabel("Relative imbalance [-]")
    axes[1].plot(x, full); axes[1].set_ylabel("Full imbalance [kg/s]")
    axes[2].plot(x, p); axes[2].set_ylabel("Brine entry p [Pa]"); axes[2].set_xlabel("Native Fluent iteration")
    for ax in axes: ax.grid(alpha=.25)
    fig.suptitle("F3 — supporting mass-balance and outlet-state behavior")
    fig.savefig(args.output_dir / "f3_numerical_output_behavior.png", dpi=180); plt.close(fig)

    window = slice(-100, None)
    summary = {"native_window": [int(x[window][0]), int(x[window][-1])]}
    for name, values in {"y010_mass_kg": y010, "y030_mass_kg": y030, "total_liquid_mass_kg": total, "liquid_to_brine_kg_s": liquid_brine, "liquid_to_steam_kg_s": liquid_steam, "net_liquid_rate_kg_s": net, "relative_mass_imbalance": rel, "full_mass_imbalance_kg_s": full, "brine_entry_static_pressure_pa": p}.items():
        coeff = np.polyfit(x[window], values[window], 1)
        summary[name] = {"initial": float(values[0]), "final": float(values[-1]), "delta": float(values[-1]-values[0]), "late_mean": float(values[window].mean()), "late_min": float(values[window].min()), "late_max": float(values[window].max()), "late_slope_per_iteration": float(coeff[0])}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
