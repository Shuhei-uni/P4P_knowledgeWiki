#!/usr/bin/env python3
"""Plot the requested E2.7 +5000 continuation report histories."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import statistics

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
RUN_ROOT = ROOT / "PyAnsys/output/phase72a_ewf_server1_e27_cont5000_20260923T102912Z"
HISTORY_PATH = RUN_ROOT / "report-histories.json"
FIGURES = ROOT / "Project/experiments/phase-07-2a-wall-liquid-routing/ewf-family/figures"
PNG_PATH = FIGURES / "E2.7-CONT5000-requested-histories.png"
CSV_PATH = FIGURES / "E2.7-CONT5000-requested-histories.csv"
MANIFEST_PATH = FIGURES / "E2.7-CONT5000-requested-histories-manifest.json"
ACTIVE_EWF_WALL_AREA_M2 = 53.4369522992766
WETTED_AREA_PATH = ROOT / "PyAnsys/output/phase72a_e27_cont5000_wetted_area/wetted-area.json"


def finite_stats(values: list[float]) -> dict[str, float | int]:
    tail = values[-500:]
    return {
        "count": len(values),
        "first": values[0],
        "last": values[-1],
        "minimum": min(values),
        "maximum": max(values),
        "mean_final_500": statistics.fmean(tail),
        "slope_final_500_per_iteration": (tail[-1] - tail[0]) / max(len(tail) - 1, 1),
    }


def main() -> None:
    data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    x = [int(round(float(v))) for v in data["v2-solver-iteration"]["values"]]
    specs = [
        ("v2-total-liquid-mass", "Total liquid mass inventory (kg)", "kg"),
        ("v2-flux-phase2-steamoutlet", "Phase-2 steamoutlet mass flux (kg/s; negative = outflow)", "kg/s"),
        ("p72a-e2.7-ewf-film-mass-total", "EWF liquid film mass (kg)", "kg"),
        ("__ewf_wall_area__", "EWF wall area (m²; wetted area measured at N=13586)", "m²"),
        ("p72a-e2.7-ewf-velocity-mag-awavg", "EWF area-weighted average speed (m/s)", "m/s"),
        ("p72a-e2.7-ewf-thickness-max", "Maximum EWF film thickness (mm)", "mm"),
    ]
    series: dict[str, list[float]] = {}
    for key, _, _ in specs:
        if key == "__ewf_wall_area__":
            series[key] = [ACTIVE_EWF_WALL_AREA_M2] * len(x)
            wetted = json.loads(WETTED_AREA_PATH.read_text(encoding="utf-8"))
            series["__ewf_wetted_area__"] = [None] * (len(x) - 1) + [float(wetted["wet_area_m2"])]
            continue
        record = data[key]
        iters = [int(round(float(v))) for v in record["iterations"]]
        values = [float(v) for v in record["values"]]
        if iters != x or len(values) != len(x):
            raise ValueError(f"History coordinates do not align for {key}")
        if key == "p72a-e2.7-ewf-thickness-max":
            values = [value * 1000.0 for value in values]
        series[key] = values

    FIGURES.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["native_iteration", "total_liquid_mass_kg", "phase2_steamoutlet_flux_kg_s", "ewf_film_mass_kg", "active_ewf_wall_geometric_area_m2_static", "ewf_wetted_area_m2_at_native_13586", "ewf_velocity_area_weighted_average_m_s", "ewf_maximum_film_thickness_mm"])
        for i, iteration in enumerate(x):
            writer.writerow([iteration, series["v2-total-liquid-mass"][i], series["v2-flux-phase2-steamoutlet"][i], series["p72a-e2.7-ewf-film-mass-total"][i], series["__ewf_wall_area__"][i], series["__ewf_wetted_area__"][i], series["p72a-e2.7-ewf-velocity-mag-awavg"][i], series["p72a-e2.7-ewf-thickness-max"][i]])

    fig, axes = plt.subplots(2, 3, figsize=(14, 8.5), sharex=True)
    for ax, (key, title, unit) in zip(axes.flat, specs):
        if key == "__ewf_wall_area__":
            ax.plot(x, series[key], color="#245b8f", linewidth=1.1, label="Total active EWF wall")
            wetted_area = float(series["__ewf_wetted_area__"][-1])
            ax.scatter([x[-1]], [wetted_area], color="#d1495b", s=38, zorder=3, label="Wetted area at N=13586")
            ax.annotate(f"{wetted_area:.2f} m² ({wetted_area / ACTIVE_EWF_WALL_AREA_M2:.1%})", (x[-1], wetted_area), xytext=(-8, -14), textcoords="offset points", ha="right", va="top", fontsize=8)
            ax.set_ylim(0, ACTIVE_EWF_WALL_AREA_M2 * 1.05)
            ax.legend(fontsize=8, loc="lower left")
        else:
            ax.plot(x, series[key], color="#245b8f", linewidth=0.9)
        ax.set_title(title, fontsize=10)
        ax.set_ylabel(unit)
        ax.grid(True, alpha=0.25)
        ax.ticklabel_format(axis="x", style="plain", useOffset=False)
    for ax in axes[-1, :]:
        ax.set_xlabel("Fluent native iteration")
    fig.suptitle("E2.7 continuation: 5,000 iterations on Server 1 (native 8586–13586)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(PNG_PATH, dpi=200)
    plt.close(fig)

    summary = {
        "status": "PLOTTED",
        "source_manifest": str((RUN_ROOT / "run-manifest.json").relative_to(ROOT)),
        "source_histories": str(HISTORY_PATH.relative_to(ROOT)),
        "native_iteration_start": x[0],
        "native_iteration_end": x[-1],
        "samples_per_native_report": len(x),
        "ewf_area": {
            "value_m2": ACTIVE_EWF_WALL_AREA_M2,
            "source": "temporary Fluent-native surface-area report computed on the active EWF wall at native iteration 13586",
            "interpretation": "total static geometric area of the active EWF wall; terminal wetted area is available at native 13586",
            "wetted_area_m2_terminal": float(wetted["wet_area_m2"]),
            "wetted_area_fraction_terminal": float(wetted["wet_area_fraction"]),
            "wetted_area_source": str(WETTED_AREA_PATH.relative_to(ROOT)),
            "wetted_area_measurement_method": wetted["measurement_method"],
        },
        "series": {
            key: finite_stats(values)
            for key, values in series.items()
            if key not in {"__ewf_wall_area__", "__ewf_wetted_area__"}
        },
        "figure": str(PNG_PATH.relative_to(ROOT)),
        "csv": str(CSV_PATH.relative_to(ROOT)),
    }
    MANIFEST_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
