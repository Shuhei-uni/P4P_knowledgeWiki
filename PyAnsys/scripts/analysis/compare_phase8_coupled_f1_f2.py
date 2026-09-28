#!/usr/bin/env python3
"""Compare matched F1/F2 Coupled carriers at one speed and horizon."""
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
    return {int(i): float(v) for i, v in ROW.findall(Path(path).read_text(encoding="utf-8"))}


def chain(paths: list[Path]) -> dict:
    runs = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    if not runs or any(run["status"] != "COMPLETE" for run in runs):
        raise RuntimeError("Carrier chain contains an incomplete run")
    horizons = [int(run["achieved_active_iterations"]) for run in runs]
    if horizons[0] != 2000 or any(after <= before for before, after in zip(horizons, horizons[1:])):
        raise RuntimeError(f"Carrier chain has an unexpected horizon: {horizons}")
    for before, after in zip(runs, runs[1:]):
        if after["source_case_sha256"] != before["checkpoints"][-1]["case_sha256"]:
            raise RuntimeError("Case lineage broke between carrier segments")
        if after["source_data_sha256"] != before["checkpoints"][-1]["data_sha256"]:
            raise RuntimeError("Data lineage broke between carrier segments")
    names = runs[0]["report_paths"].keys()
    if any(run["report_paths"].keys() != names for run in runs[1:]):
        raise RuntimeError("Report definition names changed across segments")
    reports = {name: {} for name in names}
    for run in runs:
        for name in names:
            reports[name].update(read_history(run["report_paths"][name]))
    end = horizons[-1]
    required = set(range(10, end + 1, 10))
    for name, data in reports.items():
        if not required.issubset(data):
            raise RuntimeError(f"Missing report coordinates for {name}")
    transcript = "".join(Path(run["paths"]["transcript"]).read_text(encoding="utf-8") for run in runs)
    residuals = {int(i): float(v) for i, v in RESIDUAL.findall(transcript)}
    if not set(range(1, end + 1)).issubset(residuals):
        raise RuntimeError("Missing continuity trajectory")
    return {"manifests": [str(p) for p in paths], "runs": runs, "reports": reports,
            "residuals": residuals, "end": end,
            "events": {"reversed_flow_messages": transcript.count("Reversed flow on"),
                       "viscosity_limit_messages": transcript.count("turbulent viscosity limited")}}


def series(run: dict, coordinates: np.ndarray) -> dict[str, np.ndarray]:
    r = run["reports"]
    inlet = np.array([r["p8-flux-mixture-liquidinlet"][i] + r["p8-flux-mixture-steaminlet"][i]
                      for i in coordinates])
    liquid_feed = np.array([r["p8-flux-phase2-liquidinlet"][i] + r["p8-flux-phase2-steaminlet"][i]
                            for i in coordinates])
    return {
        "liquid_out_fraction": np.array([-r["p8-flux-phase2-steamoutlet"][i] for i in coordinates]) / liquid_feed,
        "inventory_kg": np.array([r["p8-mass-phase2-total"][i] for i in coordinates]),
        "boundary_gap_fraction": np.array([inlet[j] + r["p8-flux-mixture-steamoutlet"][i]
                                           for j, i in enumerate(coordinates)]) / inlet,
        "continuity": np.array([run["residuals"][int(i)] for i in coordinates]),
        "pressure_drop_pa": np.array([r["p8-pressure-steaminlet"][i] - r["p8-pressure-steamoutlet"][i]
                                      for i in coordinates]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--f1", nargs="+", type=Path, required=True)
    parser.add_argument("--f2", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runs = {"F1 mixed faces": chain(args.f1), "F2 split faces": chain(args.f2)}
    end = runs["F1 mixed faces"]["end"]
    if runs["F2 split faces"]["end"] != end:
        raise RuntimeError("F1/F2 final horizons are not matched")
    speed = float(runs["F1 mixed faces"]["runs"][0]["speed_m_s"])
    if float(runs["F2 split faces"]["runs"][0]["speed_m_s"]) != speed:
        raise RuntimeError("F1/F2 speeds are not matched")
    if runs["F1 mixed faces"]["runs"][0]["source_readback"]["methods"] != runs["F2 split faces"]["runs"][0]["source_readback"]["methods"]:
        raise RuntimeError("F1/F2 numerical methods are not matched")
    coordinates = np.arange(10, end + 1, 10)
    data = {label: series(run, coordinates) for label, run in runs.items()}
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    specs = (("liquid_out_fraction", "Steam-outlet liquid / liquid feed"),
             ("inventory_kg", "Domain liquid inventory (kg)"),
             ("boundary_gap_fraction", "Mixture boundary gap / feed"),
             ("continuity", "Continuity residual"))
    for ax, (key, ylabel) in zip(axes.flat, specs):
        for label, s in data.items():
            ax.plot(coordinates, s[key], label=label)
        ax.axvspan(end - 500, end, color="0.90", zorder=-1)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Native steady iteration")
        ax.grid(alpha=0.25)
        if key == "continuity":
            ax.set_yscale("log")
    axes[0, 0].legend()
    fig.suptitle(f"Phase 8 matched Coupled carrier comparison, nominal {speed:.2f} m/s")
    fig.tight_layout()
    args.output.mkdir(parents=True, exist_ok=True)
    figure = args.output / f"f1-f2-coupled-{str(speed).replace('.', 'p')}-n{end}.png"
    fig.savefig(figure, dpi=170)
    plt.close(fig)
    window = coordinates[coordinates >= end - 500]
    summary = {"figure": str(figure), "figure_sha256": hashlib.sha256(figure.read_bytes()).hexdigest(),
               "speed_m_s": speed, "comparison_window": [end - 500, end], "families": {}}
    for label, run in runs.items():
        s = series(run, window)
        summary["families"][label] = {
            "manifests": run["manifests"], "events": run["events"],
            "terminal_liquid_out_fraction": float(s["liquid_out_fraction"][-1]),
            "last500_mean_liquid_out_fraction": float(np.mean(s["liquid_out_fraction"])),
            "terminal_liquid_inventory_kg": float(s["inventory_kg"][-1]),
            "terminal_mixture_boundary_gap_fraction": float(s["boundary_gap_fraction"][-1]),
            "last500_mean_steam_face_to_outlet_pressure_drop_pa": float(np.mean(s["pressure_drop_pa"])),
            "last500_mean_continuity_residual": float(np.mean(s["continuity"])),
        }
    summary["claim_limit"] = "Both numerical branches are Coupled recovery, not Purnanto SIMPLE; closed bottom and outlet liquid routing limit separator claims."
    out = args.output / "summary.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": str(out), "figure": str(figure),
                      "terminal_liquid_out_fractions": {k: v["terminal_liquid_out_fraction"] for k,v in summary["families"].items()}}, indent=2))


if __name__ == "__main__":
    main()
