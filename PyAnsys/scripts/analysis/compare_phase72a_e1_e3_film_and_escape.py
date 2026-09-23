"""Plot E1/E3 wall-film thickness and phase-2 steamoutlet escape histories."""

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
    "E1": ROOT / "PyAnsys/output/phase72a_ewf_student_e1_run_20260923T024000Z/E1/report-histories.json",
    "E3": ROOT / "PyAnsys/output/phase72a_ewf_student_e3_run_20260923T032500Z/E3/report-histories.json",
}
OUT = ROOT / "PyAnsys/output/phase72a_family_e_e1_e3_film_escape_20260923"
KEYS = {
    "maximum_film_thickness_m": "p72a-e1-ewf-thickness-max",
    "area_weighted_film_thickness_m": "p72a-e1-ewf-thickness-awavg",
    "phase2_steamoutlet_flux_kg_s": "v2-flux-phase2-steamoutlet",
}
FINAL = (7590, 8580)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    histories = {case: json.loads(path.read_text()) for case, path in SOURCES.items()}
    data = {}
    provenance = {}
    for case, reports in histories.items():
        data[case] = {}
        provenance[case] = {}
        for label, key in KEYS.items():
            report = reports[key]
            assert len(report["iterations"]) == len(report["values"]) == 300
            data[case][label] = dict(zip(report["iterations"], report["values"], strict=True))
            provenance[case][label] = {"definition": key, "remote_file": report["remote_file"]}
    iterations = sorted(data["E1"]["maximum_film_thickness_m"])
    assert iterations == sorted(data["E3"]["maximum_film_thickness_m"])
    assert iterations[0] == 5590 and iterations[-1] == 8580
    assert all(set(iterations) == set(v) for case in data.values() for v in case.values())
    with (OUT / "aligned-film-escape.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["native_iteration"] + [f"{case}_{label}" for case in SOURCES for label in KEYS]
                        + [f"{case}_phase2_escape_magnitude_kg_s" for case in SOURCES])
        for i in iterations:
            writer.writerow([i] + [data[c][label][i] for c in SOURCES for label in KEYS]
                            + [-data[c]["phase2_steamoutlet_flux_kg_s"][i] for c in SOURCES])
    summary = {"sources": {c: str(p.relative_to(ROOT)) for c, p in SOURCES.items()},
               "reports": provenance,
               "coordinate": {"first": 5590, "last": 8580, "step": 10, "points": 300},
               "final_window": {"first": FINAL[0], "last": FINAL[1], "points": 100},
               "cases": {}}
    for case in SOURCES:
        max_t = list(data[case]["maximum_film_thickness_m"].values())
        avg_t = list(data[case]["area_weighted_film_thickness_m"].values())
        flux = data[case]["phase2_steamoutlet_flux_kg_s"]
        window = [-flux[i] for i in iterations if FINAL[0] <= i <= FINAL[1]]
        summary["cases"][case] = {
            "maximum_thickness_range_m": [min(max_t), max(max_t)],
            "area_weighted_thickness_range_m": [min(avg_t), max(avg_t)],
            "all_300_thickness_samples_zero": all(v == 0 for v in max_t + avg_t),
            "escape_final_window_mean_kg_s": mean(window),
            "escape_final_window_min_kg_s": min(window),
            "escape_final_window_max_kg_s": max(window),
            "escape_last_sample_kg_s": -flux[8580],
        }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    fig, (film_ax, flux_ax) = plt.subplots(2, 1, figsize=(10, 6.8), sharex=True, layout="constrained")
    colors = {"E1": "#147d74", "E3": "#c16a36"}
    for ax in (film_ax, flux_ax):
        ax.axvspan(*FINAL, color="#edf0f2", zorder=-1)
        ax.grid(alpha=0.2)
    for case in SOURCES:
        film_ax.plot(iterations, [1e3 * data[case]["maximum_film_thickness_m"][i] for i in iterations],
                     label=f"{case} maximum", color=colors[case], linewidth=1.6,
                     linestyle="-" if case == "E1" else "--")
        flux_ax.plot(iterations, [-data[case]["phase2_steamoutlet_flux_kg_s"][i] for i in iterations],
                     label=case, color=colors[case], linewidth=1.2)
    film_ax.set_ylim(-0.00005, 0.0005)
    film_ax.set_yticks([0, 0.00025, 0.0005])
    film_ax.set_ylabel("Maximum film thickness (mm)")
    film_ax.set_title("EWF film on wall: maximum thickness (both exactly zero)")
    film_ax.text(0.02, 0.87, "Area-weighted thickness also zero at every sample for E1 and E3",
                 transform=film_ax.transAxes, fontsize=9)
    film_ax.legend(loc="upper right", frameon=False)
    flux_ax.set_ylabel("Phase-2 escape magnitude (kg/s)")
    flux_ax.set_xlabel("Native Fluent iteration")
    flux_ax.set_title("Liquid-phase flux through steamoutlet (−Fluent signed flux)")
    flux_ax.legend(loc="upper right", frameon=False)
    fig.suptitle("Phase 7.2A: E1 basic EWF vs E3 basic EWF + R3 roughness")
    fig.savefig(OUT / "film-thickness-and-steamoutlet-escape.png", dpi=180)
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
