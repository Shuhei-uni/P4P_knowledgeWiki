#!/usr/bin/env python3
"""Plot the outlet-based apparent liquid separation measure for Stage 2."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "phase72a_stage2_e27_roughness"
PARENT = ROOT / "output" / "phase72a_ewf_server1_e27_cont5000_20260923T102912Z" / "report-histories.json"
FIGURES = ROOT.parent / "Project" / "experiments" / "phase-07-2a-wall-liquid-routing" / "stage-02-combined-ewf-roughness" / "figures"
RUNS = {"R3": "20260926T223230Z", "R4": "20260926T223500Z", "R5": "20260926T223501Z"}
COLORS = {"R3": "#3f74b8", "R4": "#d38528", "R5": "#40906b"}


def series(history, name):
    record = history[name]
    return np.asarray(record["iterations"], dtype=int), np.asarray(record["values"], dtype=float)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    p_iter, p_liquid_in = series(parent, "v2-flux-phase2-liquidinlet")
    _, p_steam_in = series(parent, "v2-flux-phase1-steaminlet")
    _, p_out = series(parent, "v2-flux-phase2-steamoutlet")
    p_total_in = p_liquid_in + p_steam_in
    assert p_iter[-1] == 13586 and p_total_in[-1] > 0 and p_out[-1] < 0
    parent_carry = -p_out[-1] / p_total_in[-1]
    parent_eff = 100.0 * (1.0 - parent_carry)

    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    ax.axhline(parent_eff, color="#666666", linestyle="--", linewidth=1.2,
               label=f"E2.7 parent at N13586: {parent_eff:.2f}%")
    summary = {
        "measure": "apparent outlet-based liquid separation efficiency with total-feed denominator",
        "formula": "100 * (1 + signed_phase2_steamoutlet_mass_flux / (phase1_steaminlet_mass_flux + phase2_liquidinlet_mass_flux))",
        "equivalent_carryover_fraction": "-signed_phase2_steamoutlet_mass_flux / (phase1_steaminlet_mass_flux + phase2_liquidinlet_mass_flux)",
        "sign_convention": "Both inlet fluxes are positive; phase-2 steamoutlet outflow is negative.",
        "claim_limit": "Outlet-based ratio only. Film accumulation, transfer, storage, source-inclusive closure, and physical validity are not resolved; all children reached the exploratory film-thickness cap.",
        "parent_at_native_13586": {"steam_inlet_kg_s": float(p_steam_in[-1]), "liquid_inlet_kg_s": float(p_liquid_in[-1]), "total_inlet_kg_s": float(p_total_in[-1]), "phase2_steamoutlet_kg_s": float(p_out[-1]), "carryover_percent": float(100 * parent_carry), "apparent_efficiency_percent": float(parent_eff)},
        "cases": {},
    }
    for case, stamp in RUNS.items():
        path = OUTPUT / f"{case}-{stamp}" / "report-histories.json"
        history = json.loads(path.read_text(encoding="utf-8"))
        x, liquid_in = series(history, "v2-flux-phase2-liquidinlet")
        _, steam_in = series(history, "v2-flux-phase1-steaminlet")
        _, outlet = series(history, "v2-flux-phase2-steamoutlet")
        inlet = liquid_in + steam_in
        assert len(x) == 3001 and x[0] == 13586 and x[-1] == 16586
        assert np.all(inlet > 0) and np.all(outlet <= 0)
        carry = -outlet / inlet
        efficiency = 100.0 * (1.0 - carry)
        ax.plot(x, efficiency, color=COLORS[case], linewidth=1.25, label=f"E2.7+{case}")
        tail = x >= 16087
        summary["cases"][case] = {
            "points": len(x), "first_iteration": int(x[0]), "last_iteration": int(x[-1]),
            "steam_inlet_last_kg_s": float(steam_in[-1]),
            "liquid_inlet_last_kg_s": float(liquid_in[-1]),
            "total_inlet_last_kg_s": float(inlet[-1]),
            "phase2_steamoutlet_last_kg_s": float(outlet[-1]),
            "apparent_efficiency_last_percent": float(efficiency[-1]),
            "apparent_efficiency_tail500_mean_percent": float(efficiency[tail].mean()),
            "apparent_efficiency_min_percent": float(efficiency.min()),
            "carryover_last_percent": float(100 * carry[-1]),
            "carryover_tail500_mean_percent": float(100 * carry[tail].mean()),
        }
    ax.set_title("Phase 7.2A Stage 2: apparent liquid separation relative to total feed")
    ax.set_xlabel("Native Fluent iteration")
    ax.set_ylabel("Outlet-based apparent separation (%)")
    ax.set_xlim(13586, 16586)
    ax.grid(alpha=0.23)
    ax.legend(loc="lower right")
    fig.tight_layout()
    png = FIGURES / "E2.7-R3-R4-R5-outlet-based-efficiency.png"
    fig.savefig(png, dpi=180)
    plt.close(fig)
    (FIGURES / "E2.7-R3-R4-R5-outlet-based-efficiency-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(png)


if __name__ == "__main__":
    main()
