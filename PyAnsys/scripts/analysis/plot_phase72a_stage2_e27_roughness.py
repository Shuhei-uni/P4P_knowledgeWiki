#!/usr/bin/env python3
"""Plot matched Phase 7.2A Stage 2 R3/R4/R5 native report histories."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "phase72a_stage2_e27_roughness"
FIGURES = ROOT.parent / "Project" / "experiments" / "phase-07-2a-wall-liquid-routing" / "stage-02-combined-ewf-roughness" / "figures"
PARENT = ROOT / "output" / "phase72a_ewf_server1_e27_cont5000_20260923T102912Z" / "report-histories.json"
RUNS = {"R3": "20260926T223230Z", "R4": "20260926T223500Z", "R5": "20260926T223501Z"}
METRICS = [
    ("v2-flux-phase2-steamoutlet", "Phase-2 steamoutlet flux (kg/s)", 1.0),
    ("p72a-e2.7-ewf-film-mass-total", "EWF film mass (kg)", 1.0),
    ("p72a-e2.7-ewf-thickness-max", "Maximum film thickness (mm)", 1000.0),
    ("p72a-e2.7-ewf-velocity-mag-awavg", "Average film speed (m/s)", 1.0),
    ("p72a-stage2-ewf-wetted-area", "Native wetted area (m²)", 1.0),
    ("v2-total-liquid-mass", "Bulk liquid inventory (kg)", 1.0),
]
PARENT_COVERAGE_NATIVE_M2 = 50.33798212721793


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    children = {}
    for case, stamp in RUNS.items():
        path = OUTPUT / f"{case}-{stamp}"
        manifest = json.loads((path / "run-manifest.json").read_text(encoding="utf-8"))
        if not manifest["status"].startswith("COMPLETE") or manifest["terminal_native_iteration"] != 16586:
            raise RuntimeError(f"{case} is not verified complete: {manifest['status']}")
        children[case] = json.loads((path / "report-histories.json").read_text(encoding="utf-8"))

    fig, axes = plt.subplots(3, 2, figsize=(14, 11), sharex=True)
    colors = {"R3": "#3f74b8", "R4": "#d38528", "R5": "#40906b"}
    summary = {"parent_native_iteration": 13586, "terminal_native_iteration": 16586, "parent_native_wetted_area_m2": PARENT_COVERAGE_NATIVE_M2, "parent_offline_wetted_area_m2": 50.690, "cases": {}}
    rows = []
    for ax, (key, label, scale) in zip(axes.flat, METRICS):
        base = PARENT_COVERAGE_NATIVE_M2 if key == "p72a-stage2-ewf-wetted-area" else parent[key]["summary"]["last_value"] * scale
        ax.axhline(base, color="#666666", linestyle="--", linewidth=1.0, label="E2.7 parent at N13586")
        for case, hist in children.items():
            record = hist[key]
            x = np.asarray(record["iterations"], dtype=int)
            y = np.asarray(record["values"], dtype=float) * scale
            if len(x) < 3000 or x[-1] != 16586:
                raise RuntimeError(f"{case} {key} incomplete: {len(x)} points, last {x[-1] if len(x) else None}")
            ax.plot(x, y, color=colors[case], linewidth=1.05, label=f"E2.7+{case}")
            tail = y[x >= 16087]
            summary["cases"].setdefault(case, {})[key] = {"first": float(y[0]), "last": float(y[-1]), "min": float(y.min()), "max": float(y.max()), "tail500_mean": float(tail.mean()), "tail500_std": float(tail.std(ddof=0)), "tail500_slope_per_iteration": float(np.polyfit(x[x >= 16087], tail, 1)[0])}
            if key == METRICS[0][0]:
                rows.extend({"case": case, "iteration": int(i), "phase2_steamoutlet_kg_s": float(v)} for i, v in zip(x, y))
        ax.set_ylabel(label)
        ax.grid(alpha=0.22)
        ax.axvline(13586, color="#888888", linewidth=0.7)
    for ax in axes[-1]:
        ax.set_xlabel("Native Fluent iteration")
    axes[0, 0].legend(loc="best", fontsize=8)
    fig.suptitle("Phase 7.2A Stage 2: E2.7 continuation + R3/R4/R5 roughness", fontsize=14)
    fig.tight_layout()
    figure = FIGURES / "E2.7-R3-R4-R5-native-histories.png"
    fig.savefig(figure, dpi=180)
    plt.close(fig)
    (FIGURES / "E2.7-R3-R4-R5-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (FIGURES / "E2.7-R3-R4-R5-phase2-outlet.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case", "iteration", "phase2_steamoutlet_kg_s"])
        writer.writeheader()
        writer.writerows(rows)
    print(figure)


if __name__ == "__main__":
    main()
