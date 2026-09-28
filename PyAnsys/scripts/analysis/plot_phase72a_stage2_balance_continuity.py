#!/usr/bin/env python3
"""Plot Stage 2 boundary/source imbalance and native continuity residuals."""
from __future__ import annotations

import json
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "phase72a_stage2_e27_roughness"
FIGURES = ROOT.parent / "Project" / "experiments" / "phase-07-2a-wall-liquid-routing" / "stage-02-combined-ewf-roughness" / "figures"
RUNS = {"R3": "20260926T223230Z", "R4": "20260926T223500Z", "R5": "20260926T223501Z"}
COLORS = {"R3": "#3f74b8", "R4": "#d38528", "R5": "#40906b"}
RESIDUAL_RE = re.compile(
    r"^\s*(\d+)\s+"
    + r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+" * 7
    + r"\d\d?:\d\d:\d\d",
    re.MULTILINE,
)


def series(history, name):
    item = history[name]
    return np.asarray(item["iterations"], dtype=int), np.asarray(item["values"], dtype=float)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    summary = {"formula": "phase1_in + phase1_out + phase2_in + phase2_out + native_applied_absorber", "units": "kg/s", "interpretation": "Signed boundary-plus-absorber algebraic imbalance. EWF transfer and storage are not included; this is not a complete physical closure rate.", "cases": {}}
    for case, stamp in RUNS.items():
        run = OUTPUT / f"{case}-{stamp}"
        history = json.loads((run / "report-histories.json").read_text(encoding="utf-8"))
        x, p1_in = series(history, "v2-flux-phase1-steaminlet")
        _, p1_out = series(history, "v2-flux-phase1-steamoutlet")
        _, p2_in = series(history, "v2-flux-phase2-liquidinlet")
        _, p2_out = series(history, "v2-flux-phase2-steamoutlet")
        _, applied = series(history, "v2-applied-absorber")
        assert len(x) == 3001 and x[0] == 13586 and x[-1] == 16586
        phase1 = p1_in + p1_out
        phase2 = p2_in + p2_out + applied
        mixture = phase1 + phase2
        padded = np.pad(mixture, (25, 25), mode="edge")
        median51 = np.median(np.lib.stride_tricks.sliding_window_view(padded, 51), axis=1)
        axes[0].plot(x, mixture, color=COLORS[case], linewidth=0.55, alpha=0.25, label=f"{case} raw")
        axes[0].plot(x, median51, color=COLORS[case], linewidth=1.5, label=f"{case} 51-iteration median")

        transcript = run / ("transcript-stream.txt" if case == "R4" else "transcript-native-solve.txt")
        rows = [(int(m.group(1)), float(m.group(2))) for m in RESIDUAL_RE.finditer(transcript.read_text(encoding="utf-8", errors="replace"))]
        # A transcript may repeat a native coordinate around a status line; keep
        # the last observed row and never interpolate over a missing tail.
        residual = dict(rows)
        rx = np.asarray(sorted(residual), dtype=int)
        ry = np.asarray([residual[i] for i in rx], dtype=float)
        assert len(rx) and rx[0] == 13586
        axes[1].plot(rx, ry, color=COLORS[case], linewidth=0.9, label=f"{case} ({len(rx)} rows)")
        tail = x >= 16087
        summary["cases"][case] = {
            "report_points": len(x),
            "mixture_imbalance_first_kg_s": float(mixture[0]),
            "mixture_imbalance_last_kg_s": float(mixture[-1]),
            "mixture_imbalance_tail500_mean_kg_s": float(mixture[tail].mean()),
            "mixture_imbalance_tail500_median_kg_s": float(np.median(mixture[tail])),
            "mixture_imbalance_tail500_mean_absolute_kg_s": float(np.abs(mixture[tail]).mean()),
            "mixture_imbalance_tail500_min_kg_s": float(mixture[tail].min()),
            "mixture_imbalance_tail500_max_kg_s": float(mixture[tail].max()),
            "phase2_imbalance_last_kg_s": float(phase2[-1]),
            "continuity_rows": len(rx),
            "continuity_first_iteration": int(rx[0]),
            "continuity_last_iteration": int(rx[-1]),
            "continuity_last_scaled_residual": float(ry[-1]),
            "continuity_source": str(transcript.relative_to(ROOT)),
        }
    axes[0].axhline(0, color="#555555", linewidth=0.8)
    axes[0].set_ylabel("Signed imbalance (kg/s)")
    axes[0].set_title("Boundary fluxes plus native applied absorber (raw and rolling median)")
    axes[0].legend(ncol=3, fontsize=8)
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Scaled continuity residual")
    axes[1].set_xlabel("Native Fluent iteration")
    axes[1].set_title("Fluent continuity residual (raw transcript rows)")
    axes[1].legend(ncol=3, fontsize=8)
    axes[1].axvspan(16060, 16586, color="#d38528", alpha=0.08)
    axes[1].text(16310, 0.98, "R4 transcript unavailable", transform=axes[1].get_xaxis_transform(), ha="center", va="top", fontsize=8, color="#885016")
    for ax in axes:
        ax.grid(alpha=0.22)
        ax.set_xlim(13586, 16586)
    fig.suptitle("Phase 7.2A Stage 2: balance diagnostic and continuity", fontsize=14)
    fig.tight_layout()
    png = FIGURES / "E2.7-R3-R4-R5-balance-continuity.png"
    fig.savefig(png, dpi=180)
    plt.close(fig)
    (FIGURES / "E2.7-R3-R4-R5-balance-continuity-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(png)


if __name__ == "__main__":
    main()
