#!/usr/bin/env python3
"""Plain linear-scale comparison of successful Family E phase-2 outlet runs."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "Project/experiments/phase-07-2a-wall-liquid-routing/ewf-family/figures"
PNG = FIGURES / "e-family-phase2-steamoutlet-flux.png"
CSV_OUT = FIGURES / "e-family-phase2-steamoutlet-flux.csv"
REPORT_KEY = "v2-flux-phase2-steamoutlet"
SOURCES = {
    "E0": ("PyAnsys/output/phase72a_ewf_family_e_student_20260922T115500Z/E0/report-histories.json", "direct"),
    "E1": ("PyAnsys/output/phase72a_ewf_student_e1_run_20260923T024000Z/E1/report-histories.json", "direct"),
    "E3": ("PyAnsys/output/phase72a_ewf_student_e3_run_20260923T032500Z/E3/report-histories.json", "direct"),
    "E2.7": ("PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/report-histories.json", "direct"),
}


def main() -> None:
    # Match the 10-iteration cadence available for all four successful cases.
    target_iterations = list(range(5590, 8581, 10))
    series: dict[str, list[float]] = {}
    for case, (rel, _kind) in SOURCES.items():
        report = json.loads((ROOT / rel).read_text())[REPORT_KEY]
        points = dict(zip(report["iterations"], report["values"]))
        missing = [i for i in target_iterations if i not in points]
        if missing:
            raise ValueError(f"{case} missing common native report coordinates: {missing[:5]}")
        series[case] = [float(points[i]) for i in target_iterations]

    FIGURES.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["native_iteration", *[f"{case}_signed_phase2_flux_kg_s" for case in SOURCES]])
        writer.writerows([i, *(series[case][n] for case in SOURCES)] for n, i in enumerate(target_iterations))

    fig, ax = plt.subplots(figsize=(10, 5.6), constrained_layout=True)
    for case, values in series.items():
        ax.plot(target_iterations, values, label=case, linewidth=1.7)
    ax.set_xlabel("Native iteration")
    ax.set_ylabel("Phase-2 steamoutlet mass flux (kg/s)")
    ax.set_title("Successful E-family cases: phase-2 steamoutlet flux")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Case")
    fig.savefig(PNG, dpi=180)
    plt.close(fig)
    print(f"wrote {PNG}")
    print(f"wrote {CSV_OUT}")
    print(f"cases={','.join(SOURCES)}; native window=5590–8580; points/case={len(target_iterations)}")


if __name__ == "__main__":
    main()
