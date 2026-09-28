#!/usr/bin/env python3
"""Compare Phase 8 F1/F2 carrier pilots from native report histories."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np

ROW = re.compile(r"^\s*(\d+)\s+([-+\d.eE]+)\s*$", re.M)
RESIDUAL = re.compile(r"^\s*(\d+)\s+(\d+\.\d+e[+-]\d+)\s+(\d+\.\d+e[+-]\d+)", re.I | re.M)


def history(path: str) -> dict[int, float]:
    values = {int(i): float(v) for i, v in ROW.findall(Path(path).read_text(encoding="utf-8"))}
    if not values:
        raise RuntimeError(f"No native report rows: {path}")
    return values


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_run(manifest: Path) -> dict:
    receipt = json.loads(manifest.read_text(encoding="utf-8"))
    if receipt["status"] != "COMPLETE" or receipt["achieved_active_iterations"] != 2000:
        raise RuntimeError(f"Incomplete carrier pilot: {manifest}")
    reports = {name: history(path) for name, path in receipt["report_paths"].items()}
    required = (
        "p8-flux-mixture-liquidinlet", "p8-flux-mixture-steaminlet", "p8-flux-mixture-steamoutlet",
        "p8-flux-phase1-liquidinlet", "p8-flux-phase1-steaminlet", "p8-flux-phase1-steamoutlet",
        "p8-flux-phase2-liquidinlet", "p8-flux-phase2-steaminlet", "p8-flux-phase2-steamoutlet",
        "p8-mass-phase2-total", "p8-mass-phase2-lower",
    )
    coordinates = set(range(10, 2001, 10))
    for name in required:
        if not coordinates.issubset(reports[name]):
            raise RuntimeError(f"Native report missing coordinates: {name}")
    transcript = Path(receipt["paths"]["transcript"]).read_text(encoding="utf-8")
    continuation = Path(receipt["paths"]["local"]) / "continuation1000-2000.txt"
    if continuation.exists():
        transcript += continuation.read_text(encoding="utf-8")
    residual_rows = {int(i): (float(continuity), float(x_velocity)) for i, continuity, x_velocity in RESIDUAL.findall(transcript)}
    if not set(range(1, 2001)).issubset(residual_rows):
        raise RuntimeError(f"Residual transcript incomplete: {manifest}")
    return {"receipt": receipt, "reports": reports, "residuals": residual_rows,
            "events": {"reversed_flow_messages": len(re.findall(r"Reversed flow on", transcript)),
                       "viscosity_limit_messages": len(re.findall(r"turbulent viscosity limited", transcript)),
                       "fatal_messages": len(re.findall(r"floating point exception|fatal error|nonfinite", transcript, re.I))}}


def series(run: dict, phase: str, boundary: str) -> np.ndarray:
    report = run["reports"][f"p8-flux-{phase}-{boundary}"]
    return np.array([report[i] for i in range(10, 2001, 10)])


def summarize(run: dict) -> dict:
    r = run["reports"]
    family = run["receipt"]["family"]
    inlet = series(run, "mixture", "liquidinlet") + series(run, "mixture", "steaminlet")
    outlet = series(run, "mixture", "steamoutlet")
    liquid_in = series(run, "phase2", "liquidinlet") + series(run, "phase2", "steaminlet")
    liquid_out = series(run, "phase2", "steamoutlet")
    inventory = np.array([r["p8-mass-phase2-total"][i] for i in range(10, 2001, 10)])
    lower = np.array([r["p8-mass-phase2-lower"][i] for i in range(10, 2001, 10)])
    x = np.arange(10, 2001, 10)
    mask = x >= 1500
    terminal = {
        "inlet_mixture_kg_s": float(inlet[-1]), "outlet_mixture_kg_s": float(-outlet[-1]),
        "boundary_imbalance_mixture_kg_s": float(inlet[-1] + outlet[-1]),
        "boundary_imbalance_fraction_of_inlet": float((inlet[-1] + outlet[-1]) / inlet[-1]),
        "inlet_liquid_kg_s": float(liquid_in[-1]), "outlet_liquid_kg_s": float(-liquid_out[-1]),
        "outlet_liquid_fraction_of_inlet": float(-liquid_out[-1] / liquid_in[-1]),
        "phase2_inventory_kg": float(inventory[-1]), "lower_phase2_inventory_kg": float(lower[-1]),
        "continuity_residual": run["residuals"][2000][0],
    }
    window = {
        "active_iterations": [1500, 2000],
        "phase2_inventory_start_end_kg": [float(inventory[mask][0]), float(inventory[-1])],
        "phase2_inventory_slope_kg_per_iteration": float(np.polyfit(x[mask], inventory[mask], 1)[0]),
        "lower_phase2_inventory_slope_kg_per_iteration": float(np.polyfit(x[mask], lower[mask], 1)[0]),
        "mixture_boundary_imbalance_mean_kg_s": float(np.mean((inlet + outlet)[mask])),
        "outlet_liquid_fraction_mean": float(np.mean((-liquid_out / liquid_in)[mask])),
    }
    return {"family": family, "manifest": run["receipt"].get("paths", {}), "terminal": terminal,
            "last_500_iteration_window": window, "events": run["events"],
            "interpretation": "Stationarity diagnostic only: kg per steady iteration is not physical storage in kg/s."}


def plot(runs: list[dict], path: Path) -> None:
    x = np.arange(10, 2001, 10)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    for run in runs:
        family = run["receipt"]["family"]
        reports = run["reports"]
        inlet = series(run, "mixture", "liquidinlet") + series(run, "mixture", "steaminlet")
        outlet = series(run, "mixture", "steamoutlet")
        liquid_in = series(run, "phase2", "liquidinlet") + series(run, "phase2", "steaminlet")
        liquid_out = series(run, "phase2", "steamoutlet")
        axes[0, 0].plot(x, -liquid_out / liquid_in, label=family)
        axes[0, 1].plot(x, [reports["p8-mass-phase2-total"][i] for i in x], label=family)
        axes[1, 0].plot(x, (inlet + outlet) / inlet, label=family)
        axes[1, 1].semilogy(x, [run["residuals"][i][0] for i in x], label=family)
    axes[0, 0].set_ylabel("Outlet liquid / liquid feed")
    axes[0, 1].set_ylabel("Phase-2 inventory (kg)")
    axes[1, 0].set_ylabel("Mixture boundary imbalance / feed")
    axes[1, 1].set_ylabel("Continuity residual")
    for ax in axes.flat:
        ax.grid(alpha=0.3)
        ax.axvspan(1500, 2000, color="0.9", zorder=-1)
        ax.set_xlabel("Active steady iteration")
    axes[0, 0].legend()
    fig.suptitle("Phase 8 Purnanto-parity carrier pilots at nominal 26.81 m/s")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    loaded = [load_run(path) for path in args.manifests]
    args.output.mkdir(parents=True, exist_ok=True)
    figure = args.output / "f1-f2-carrier-26p81.png"
    plot(loaded, figure)
    summary = {"runs": [summarize(run) for run in loaded], "figure": str(figure), "figure_sha256": sha256(figure)}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
