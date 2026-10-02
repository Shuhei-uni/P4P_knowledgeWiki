#!/usr/bin/env python3
"""Summarize matched F1 SIMPLE and Coupled carrier evidence at N10,000."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "output" / "phase8-carrier"
OUT = ROOT / "output" / "phase8-analysis" / "f1-simple-vs-coupled-n10000"
COUPLED_SUMMARY = ROOT / "output" / "phase8-storyline-20260930" / "summary.json"
SPEEDS = [20.11, 23.46, 26.81, 29.48, 32.14]
SOURCE_CASE = Path(r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\PurnantoParity\F1\F1-purnanto-parity-26p81.cas.h5")
ROW = re.compile(r"^\s*(\d+)\s+([-+\d.eE]+)\s*$", re.M)
RESIDUAL = re.compile(r"^\s*(\d+)\s+(\d+\.\d+e[+-]\d+)", re.I | re.M)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def history(path: str) -> dict[int, float]:
    values = {int(i): float(v) for i, v in ROW.findall(Path(path).read_text(encoding="utf-8"))}
    if not values:
        raise RuntimeError(f"No report history rows: {path}")
    return values


def selected_manifests() -> dict[float, tuple[Path, dict]]:
    candidates: dict[float, list[tuple[Path, dict]]] = {speed: [] for speed in SPEEDS}
    for path in RUN_ROOT.glob("*/manifest.json"):
        run = json.loads(path.read_text(encoding="utf-8"))
        if (run.get("family") == "F1" and run.get("status") == "COMPLETE"
                and run.get("achieved_active_iterations") == 10000
                and Path(run.get("source_case", "")).resolve() == SOURCE_CASE.resolve()):
            candidates[float(run["speed_m_s"])].append((path, run))
    selected = {}
    for speed in SPEEDS:
        matches = candidates[speed]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one completed parity-source F1 SIMPLE N10000 run at {speed:g}; found {len(matches)}")
        selected[speed] = matches[0]
    return selected


def summarize(path: Path, run: dict) -> dict:
    if run.get("requested_active_iterations") != 10000 or run.get("comparison_window_active_iterations") != [9500, 10000]:
        raise RuntimeError(f"Unexpected bounded horizon/window: {path}")
    checkpoint = run["checkpoints"][-1]
    for kind in ("case", "data"):
        artifact = Path(checkpoint[kind])
        actual = digest(artifact)
        if actual != checkpoint[f"{kind}_sha256"]:
            raise RuntimeError(f"Final {kind} hash mismatch: {artifact}")
    r = {name: history(value) for name, value in run["report_paths"].items()}
    x = np.arange(10, 10001, 10)
    window = x >= 9500
    def values(name: str) -> np.ndarray:
        series = r[name]
        missing = [int(i) for i in x if int(i) not in series]
        if missing:
            raise RuntimeError(f"{name} missing coordinates {missing[:5]} in {path}")
        return np.array([series[int(i)] for i in x])
    vapor_in = values("p8-flux-phase1-liquidinlet") + values("p8-flux-phase1-steaminlet")
    liquid_in = values("p8-flux-phase2-liquidinlet") + values("p8-flux-phase2-steaminlet")
    mixture_in = values("p8-flux-mixture-liquidinlet") + values("p8-flux-mixture-steaminlet")
    liquid_out = values("p8-flux-phase2-steamoutlet")
    mixture_out = values("p8-flux-mixture-steamoutlet")
    inventory = values("p8-mass-phase2-total")
    pressure = values("p8-pressure-steaminlet") - values("p8-pressure-steamoutlet")
    transcript = Path(run["paths"]["transcript"]).read_text(encoding="utf-8")
    residual = {int(i): float(v) for i, v in RESIDUAL.findall(transcript)}
    missing_residuals = set(range(9501, 10001)) - residual.keys()
    if missing_residuals:
        raise RuntimeError(f"Continuity history incomplete in {path}: {sorted(missing_residuals)[:5]}")
    residual_values = np.array([residual[int(i)] for i in x if i >= 9500])
    return {
        "speed_m_s": float(run["speed_m_s"]), "family": "F1", "method_package": "SIMPLE / segregated pseudo-time off / second-order k",
        "manifest": str(path.relative_to(ROOT)).replace("\\", "/"),
        "source_case_sha256": run["source_case_sha256"], "source_data_sha256": run["source_data_sha256"],
        "horizon": 10000, "comparison_window": [9500, 10000],
        "final_pair": {key: checkpoint[key] for key in ("case", "data", "case_sha256", "data_sha256")},
        "feed_kg_s_last_window_mean": {"vapor": float(np.mean(vapor_in[window])), "liquid": float(np.mean(liquid_in[window])),
                                       "mixture": float(np.mean(mixture_in[window]))},
        "last_window_mean": {
            "steam_outlet_liquid_feed_percent": float(np.mean(-liquid_out[window] / liquid_in[window]) * 100),
            "liquid_outlet_kg_s": float(np.mean(-liquid_out[window])),
            "liquid_inventory_kg": float(inventory[-1]),
            "inventory_slope_kg_per_steady_iteration": float(np.polyfit(x[window], inventory[window], 1)[0]),
            "mixture_boundary_gap_kg_s": float(np.mean(mixture_in[window] + mixture_out[window])),
            "absolute_mixture_boundary_gap_feed_percent": float(np.mean(np.abs(mixture_in[window] + mixture_out[window]) / mixture_in[window]) * 100),
            "steam_face_to_outlet_pressure_drop_kpa": float(np.mean(pressure[window]) / 1000),
            "continuity_residual_min_mean_max": [float(np.min(residual_values)), float(np.mean(residual_values)), float(np.max(residual_values))],
        },
        "events": {"reverse_flow_messages": transcript.count("Reversed flow on"),
                   "viscosity_limit_messages": transcript.count("turbulent viscosity limited"),
                   "fatal_solver_markers": len(re.findall(r"floating point exception|Divergence detected in AMG solver|fatal error|nonfinite", transcript, re.I))},
        "reopened_flow_scheme": run["final_reopen_audit"]["flow_scheme"],
        "report_file_bytes": run["report_file_bytes"],
    }


def main() -> None:
    coupled = json.loads(COUPLED_SUMMARY.read_text(encoding="utf-8"))
    coupled_by_speed = {float(row["speed"]): row for row in coupled["families"]["F1"]}
    selected = selected_manifests()
    rows = []
    for speed in SPEEDS:
        path, run = selected[speed]
        simple = summarize(path, run)
        c = coupled_by_speed[speed]
        s = simple["last_window_mean"]
        simple["coupled_match"] = {"method_package": "Coupled / Global Time Step / first-order k",
                                   "manifest_summary": str((ROOT / "output" / "phase8-analysis" / f"{str(speed).replace('.', 'p')}-f1-coupled-n10000" / "summary.json").relative_to(ROOT)).replace("\\", "/"),
                                   "horizon": 10000, "comparison_window": [9500, 10000],
                                   "steam_outlet_liquid_feed_percent": c["out_pct"], "liquid_inventory_kg": c["inventory"],
                                   "steam_face_to_outlet_pressure_drop_kpa": c["pressure_kpa"],
                                   "absolute_mixture_boundary_gap_feed_percent": c["gap_pct"]}
        simple["simple_minus_coupled"] = {
            "steam_outlet_liquid_feed_percentage_points": s["steam_outlet_liquid_feed_percent"] - c["out_pct"],
            "liquid_inventory_kg": s["liquid_inventory_kg"] - c["inventory"],
            "steam_face_to_outlet_pressure_drop_kpa": s["steam_face_to_outlet_pressure_drop_kpa"] - c["pressure_kpa"],
            "absolute_mixture_boundary_gap_feed_percentage_points": s["absolute_mixture_boundary_gap_feed_percent"] - c["gap_pct"],
        }
        rows.append(simple)
    OUT.mkdir(parents=True, exist_ok=True)
    colors = ["#31688e", "#35b779", "#d99b24", "#9253a1", "#c54843"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fields = [
        ("steam_outlet_liquid_feed_percent", "Steam-outlet liquid / liquid feed (%)"),
        ("liquid_inventory_kg", "Final Eulerian liquid inventory (kg)"),
        ("steam_face_to_outlet_pressure_drop_kpa", "Steam-face to outlet pressure difference (kPa)"),
        ("absolute_mixture_boundary_gap_feed_percent", "Absolute mixture boundary gap / feed (%)"),
    ]
    for ax, (field, label) in zip(axes.flat, fields):
        simple_y = [r["last_window_mean"][field] for r in rows]
        coupled_y = [r["coupled_match"][field] for r in rows]
        ax.plot(SPEEDS, coupled_y, "o-", color="#7b8794", label="Coupled recovery")
        ax.plot(SPEEDS, simple_y, "o-", color="#c54843", label="SIMPLE reconstruction")
        ax.set(xlabel="Nominal inlet speed (m/s)", ylabel=label)
        ax.grid(alpha=.25)
    axes[0, 0].legend()
    fig.suptitle("F1 numerical-package comparison, matched speed and N9,500–10,000 windows")
    fig.tight_layout()
    figure = OUT / "f1-simple-vs-coupled-n10000.png"
    fig.savefig(figure, dpi=180, bbox_inches="tight")
    plt.close(fig)
    receipt = {"status": "COMPLETE", "family": "F1", "speeds_m_s": SPEEDS,
               "horizon": 10000, "comparison_window": [9500, 10000], "solve_issued": False,
               "runs": rows, "figure": str(figure.relative_to(ROOT)).replace("\\", "/"),
               "figure_sha256": digest(figure),
               "claim_limit": "Matched F1 feed/topology/mesh and horizon, but different solver packages; historical 08b also has a different split-inlet topology and 7,601,261-cell mesh. Numerical-package comparison is not an algorithm-only causal attribution."}
    (OUT / "summary.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": str(OUT / "summary.json"), "figure": str(figure),
                      "rows": [{"speed": r["speed_m_s"], **r["simple_minus_coupled"]} for r in rows]}, indent=2))


if __name__ == "__main__":
    main()
