"""Compare saved Phase 7.2A E0/E1/E3 liquid-inventory report histories."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "E0": ROOT / "PyAnsys/output/phase72a_ewf_family_e_student_20260922T115500Z/E0/report-histories.json",
    "E1": ROOT / "PyAnsys/output/phase72a_ewf_student_e1_run_20260923T024000Z/E1/report-histories.json",
    "E3": ROOT / "PyAnsys/output/phase72a_ewf_student_e3_run_20260923T032500Z/E3/report-histories.json",
}
OUT = ROOT / "PyAnsys/output/phase72a_family_e_liquid_inventory_comparison_20260923"
REPORTS = {
    "total_mass_kg": "v2-total-liquid-mass",
    "lower_mass_kg": "v2-lower-liquid-mass",
    "total_volume_m3": "v2-total-liquid-volume",
    "lower_volume_m3": "v2-lower-liquid-volume",
}
FINAL_WINDOW = (7590, 8580)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw = {case: json.loads(path.read_text()) for case, path in SOURCES.items()}
    series = {}
    for case, reports in raw.items():
        series[case] = {}
        for label, key in REPORTS.items():
            report = reports[key]
            iterations = report["iterations"]
            values = report["values"]
            assert len(iterations) == len(values) == report["points"]
            assert len(set(iterations)) == len(iterations)
            series[case][label] = dict(zip(iterations, values, strict=True))
    shared = sorted(set.intersection(*(set(series[c]["total_mass_kg"]) for c in SOURCES)))
    assert shared[0] == 5590 and shared[-1] == 8580 and len(shared) == 300
    assert all(all(set(shared) <= set(series[c][label]) for label in REPORTS) for c in SOURCES)
    identical_e0_e1 = all(
        series["E0"][label][i] == series["E1"][label][i]
        for label in REPORTS for i in shared
    )

    with (OUT / "aligned-inventory.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["native_iteration"] + [f"{case}_{label}" for case in SOURCES for label in REPORTS])
        for iteration in shared:
            writer.writerow([iteration] + [series[c][label][iteration] for c in SOURCES for label in REPORTS])

    summary = {
        "sources": {case: str(path.relative_to(ROOT)) for case, path in SOURCES.items()},
        "alignment": {"start": shared[0], "end": shared[-1], "step": 10, "points": len(shared)},
        "final_window": {"start": FINAL_WINDOW[0], "end": FINAL_WINDOW[1], "points": sum(FINAL_WINDOW[0] <= i <= FINAL_WINDOW[1] for i in shared)},
        "e0_e1_exact_match_on_shared_coordinates": identical_e0_e1,
        "metrics": {},
    }
    for case in SOURCES:
        summary["metrics"][case] = {}
        for label in REPORTS:
            vals = series[case][label]
            window = [vals[i] for i in shared if FINAL_WINDOW[0] <= i <= FINAL_WINDOW[1]]
            summary["metrics"][case][label] = {
                "first_shared": vals[shared[0]], "last_shared": vals[shared[-1]],
                "change_shared": vals[shared[-1]] - vals[shared[0]],
                "final_window_mean": mean(window), "final_window_min": min(window),
                "final_window_max": max(window),
            }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, layout="constrained")
    colors = {"E0": "#536c83", "E1": "#147d74", "E3": "#c16a36"}
    for ax, label, title in zip(axes, ("total_mass_kg", "lower_mass_kg"),
                                ("Total continuous-liquid inventory", "Lower-zone continuous-liquid inventory"), strict=True):
        for case in ("E0", "E3") if identical_e0_e1 else SOURCES:
            name = "E0 = E1 (exact overlap)" if case == "E0" and identical_e0_e1 else case
            ax.plot(shared, [series[case][label][i] for i in shared], label=name,
                    color=colors[case], linewidth=1.3)
        ax.axvspan(*FINAL_WINDOW, color="#edf0f2", zorder=-1)
        ax.set_title(title)
        ax.set_ylabel("Liquid mass (kg)")
        ax.grid(alpha=0.22)
    axes[0].legend(ncol=3, frameon=False)
    axes[-1].set_xlabel("Native Fluent iteration")
    fig.suptitle("Phase 7.2A Family E: E0 vs E1 vs E3 (E2 excluded: FPE)")
    fig.savefig(OUT / "liquid-inventory-comparison.png", dpi=180)
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
