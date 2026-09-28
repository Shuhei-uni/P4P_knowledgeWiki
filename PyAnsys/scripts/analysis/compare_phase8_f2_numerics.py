#!/usr/bin/env python3
"""Compare F2 SIMPLE parity and Coupled recovery over N1–5000."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np

ROW = re.compile(r"^\s*(\d+)\s+([-+\d.eE]+)\s*$", re.M)
RESIDUAL = re.compile(r"^\s*(\d+)\s+(\d+\.\d+e[+-]\d+)", re.I | re.M)


def read_history(path: str) -> dict[int, float]:
    return {int(i): float(value) for i, value in ROW.findall(Path(path).read_text(encoding="utf-8"))}


def load_chain(pilot_path: Path, extension_path: Path) -> dict:
    pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
    extension = json.loads(extension_path.read_text(encoding="utf-8"))
    if pilot["status"] != "COMPLETE" or extension["status"] != "COMPLETE":
        raise RuntimeError("Both chained runs must be complete")
    if pilot["achieved_active_iterations"] != 2000 or extension["achieved_active_iterations"] != 5000:
        raise RuntimeError("Chain horizons do not match N2000 -> N5000")
    if extension["source_case_sha256"] != pilot["checkpoints"][-1]["case_sha256"]:
        raise RuntimeError("Extension is not based on pilot final pair")
    reports = {}
    for name in pilot["report_paths"]:
        reports[name] = read_history(pilot["report_paths"][name]) | read_history(extension["report_paths"][name])
        if not set(range(10, 5001, 10)).issubset(reports[name]):
            raise RuntimeError(f"Report trajectory incomplete: {name}")
    trans = Path(pilot["paths"]["transcript"]).read_text(encoding="utf-8")
    recovered = Path(pilot["paths"]["local"]) / "continuation1000-2000.txt"
    if recovered.exists():
        trans += recovered.read_text(encoding="utf-8")
    trans += Path(extension["paths"]["transcript"]).read_text(encoding="utf-8")
    residuals = {int(i): float(v) for i, v in RESIDUAL.findall(trans)}
    if not set(range(1, 5001)).issubset(residuals):
        raise RuntimeError("Residual trajectory incomplete")
    return {"pilot": pilot, "extension": extension, "reports": reports, "residuals": residuals,
            "events": {"reversed_flow_messages": trans.count("Reversed flow on"),
                       "viscosity_limit_messages": trans.count("turbulent viscosity limited")}}


def summarize(run: dict) -> dict:
    r = run["reports"]
    x = np.arange(4500, 5001, 10)
    inlet = np.array([r["p8-flux-mixture-liquidinlet"][i] + r["p8-flux-mixture-steaminlet"][i] for i in x])
    outlet = np.array([r["p8-flux-mixture-steamoutlet"][i] for i in x])
    liquid = np.array([r["p8-mass-phase2-total"][i] for i in x])
    liquid_out = -r["p8-flux-phase2-steamoutlet"][5000]
    return {
        "pilot_manifest": run["pilot"]["paths"], "extension_manifest": run["extension"]["paths"],
        "terminal_n5000": {
            "inlet_mixture_kg_s": float(inlet[-1]), "outlet_mixture_kg_s": float(-outlet[-1]),
            "boundary_imbalance_kg_s": float(inlet[-1]+outlet[-1]),
            "boundary_imbalance_fraction_of_inlet": float((inlet[-1]+outlet[-1])/inlet[-1]),
            "outlet_liquid_kg_s": float(liquid_out),
            "outlet_liquid_fraction_of_feed": float(liquid_out / (r["p8-flux-phase2-liquidinlet"][5000]+r["p8-flux-phase2-steaminlet"][5000])),
            "phase2_inventory_kg": float(liquid[-1]),
            "continuity_residual": run["residuals"][5000],
        },
        "n4500_to_5000": {
            "phase2_inventory_start_end_kg": [float(liquid[0]), float(liquid[-1])],
            "phase2_inventory_slope_kg_per_steady_iteration": float(np.polyfit(x, liquid, 1)[0]),
            "mixture_boundary_imbalance_mean_kg_s": float(np.mean(inlet+outlet)),
            "mixture_boundary_imbalance_range_kg_s": [float(np.min(inlet+outlet)), float(np.max(inlet+outlet))],
            "continuity_residual_range": [float(min(run["residuals"][i] for i in x)), float(max(run["residuals"][i] for i in x))],
        }, "events": run["events"],
        "claim_limit": "Steady-iteration inventory slope is not a physical storage rate."
    }


def plot(runs: dict[str, dict], path: Path) -> None:
    x = np.arange(10, 5001, 10)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    for label, run in runs.items():
        r = run["reports"]
        inlet = np.array([r["p8-flux-mixture-liquidinlet"][i]+r["p8-flux-mixture-steaminlet"][i] for i in x])
        outlet = np.array([r["p8-flux-mixture-steamoutlet"][i] for i in x])
        liquid_in = np.array([r["p8-flux-phase2-liquidinlet"][i]+r["p8-flux-phase2-steaminlet"][i] for i in x])
        liquid_out = np.array([r["p8-flux-phase2-steamoutlet"][i] for i in x])
        axes[0, 0].plot(x, -liquid_out/liquid_in, label=label)
        axes[0, 1].plot(x, [r["p8-mass-phase2-total"][i] for i in x], label=label)
        axes[1, 0].plot(x, (inlet+outlet)/inlet, label=label)
        axes[1, 1].semilogy(x, [run["residuals"][i] for i in x], label=label)
    axes[0, 0].set_ylabel("Outlet liquid / liquid feed")
    axes[0, 1].set_ylabel("Phase-2 inventory (kg)")
    axes[1, 0].set_ylabel("Mixture boundary imbalance / feed")
    axes[1, 1].set_ylabel("Continuity residual")
    for ax in axes.flat:
        ax.grid(alpha=0.3)
        ax.axvspan(4500, 5000, color="0.9", zorder=-1)
        ax.set_xlabel("Active steady iteration")
    axes[0, 0].legend()
    fig.suptitle("Phase 8 F2 numerical recovery at nominal 26.81 m/s")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("simple_pilot", type=Path)
    parser.add_argument("simple_extension", type=Path)
    parser.add_argument("coupled_pilot", type=Path)
    parser.add_argument("coupled_extension", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    runs = {"SIMPLE parity": load_chain(args.simple_pilot, args.simple_extension),
            "Coupled recovery": load_chain(args.coupled_pilot, args.coupled_extension)}
    fig = args.output / "f2-simple-vs-coupled-26p81.png"
    plot(runs, fig)
    summary = {"runs": {label: summarize(run) for label, run in runs.items()},
               "figure": str(fig), "figure_sha256": hashlib.sha256(fig.read_bytes()).hexdigest()}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
