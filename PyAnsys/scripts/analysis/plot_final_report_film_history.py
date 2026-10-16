"""Replot the selected 500 ms film history as two compact report panels.

Run with PyAnsys/.venv/bin/python. All selected native source points are
retained, with no smoothing, interpolation, resampling or Fluent connection.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SOURCE = "PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/selected-film-history-reference.csv"
SOURCE_SHA256 = "571d17968802be2520ea99f449c6598157c70432372d890c282fb9b330616e92"
SUMMARY = "PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/analysis-summary.json"
SUMMARY_SHA256 = "34344d2c78f1f9d8ad592f1d99032dd0168bde051b8363fca519f0234d9a1e71"
STEM = "results-film-development-reference500ms"
DEFAULT_OUT = ROOT / "Project/Final research report/Shuhei Report/figures"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    for relative, expected in ((SOURCE, SOURCE_SHA256), (SUMMARY, SUMMARY_SHA256)):
        if sha256(ROOT / relative) != expected:
            raise ValueError(f"Source hash changed: {relative}")
    with (ROOT / SOURCE).open(newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if 5080 <= int(row["native_iteration"]) <= 48205]
    arrays = {key: np.array([float(row[key]) for row in rows], dtype=np.float64)
              for key in ("native_iteration", "film_time_s", "film_kg", "accretion_kg_s", "drainage_kg_s", "bulk_liquid_kg")}
    ids, time = arrays["native_iteration"], arrays["film_time_s"]
    if len(rows) != 43126 or not np.array_equal(ids, np.arange(5080, 48206)):
        raise ValueError("Selected native range changed")
    if not np.all(np.diff(time) > 0):
        raise ValueError("Selected film clock is not strictly increasing")
    if not all(np.all(np.isfinite(array)) for array in arrays.values()):
        raise ValueError("Non-finite selected values")
    checks = {
        "all_clocks_strictly_increasing": True,
        "native_coordinates_contiguous": True,
        "bulk_inventory_constant_kg": 61.05488260946753,
        "endpoint_film_mass_kg": 9.544399018862931,
        "final_10ms_accretion_kg_s": 81.12137742644737,
        "final_10ms_drainage_kg_s": 69.59977698974535,
        "final_10ms_storage_kg_s_from_verified_summary": 11.527971400484478,
    }
    reference = json.loads((ROOT / SUMMARY).read_text())["summaries"]["reference"]
    if reference["final_10ms"]["storage_kg_s"] != checks["final_10ms_storage_kg_s_from_verified_summary"]:
        raise ValueError("Verified late-window film storage changed")
    if not np.all(arrays["bulk_liquid_kg"] == checks["bulk_inventory_constant_kg"]):
        raise ValueError("Frozen bulk inventory changed")
    if arrays["film_kg"][-1] != checks["endpoint_film_mass_kg"]:
        raise ValueError("Film endpoint changed")
    overlap = np.maximum(0, np.minimum(time[1:], 0.5) - np.maximum(time[:-1], 0.49))
    for key in ("accretion", "drainage"):
        mean = float(np.sum(arrays[f"{key}_kg_s"][1:] * overlap) / 0.01)
        if not np.isclose(mean, checks[f"final_10ms_{key}_kg_s"], rtol=0, atol=1e-10):
            raise ValueError(f"Final 10 ms {key} changed")
    markers = [5190, 13390, 25815, 48205]
    marker_indices = np.array(markers) - 5080
    milliseconds = time * 1000
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.labelsize": 9.5, "axes.titlesize": 9.5,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "path.simplify": False, "agg.path.chunksize": 0})
    fig, axes = plt.subplots(1, 2, figsize=(16 / 2.54, 6.5 / 2.54), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.27, top=0.85, wspace=0.35)
    blue, orange = "#0072B2", "#B86D20"
    axes[0].plot(milliseconds, arrays["film_kg"], color=blue, linewidth=1.2)
    axes[0].plot(milliseconds[marker_indices], arrays["film_kg"][marker_indices],
                 linestyle="none", marker="o", markersize=3.5, color=blue)
    axes[0].set(title="(a) Film mass", ylabel="Film mass (kg)", ylim=(0, 10.8))
    for i, xytext in zip(marker_indices[:3], ((25, 1.6), (65, 5.2), (260, 5.5))):
        axes[0].annotate(f"{milliseconds[i]:.2f} ms", (milliseconds[i], arrays["film_kg"][i]),
                         xytext=xytext, fontsize=8.5,
                         arrowprops={"arrowstyle": "-", "color": "#777777", "linewidth": 0.5})
    axes[0].text(235, 10.0, f"{arrays['film_kg'][-1]:.3f} kg at 500 ms", fontsize=8.5)
    axes[1].plot(milliseconds, arrays["accretion_kg_s"], color=blue, linewidth=1.1, label="Accretion")
    axes[1].plot(milliseconds, arrays["drainage_kg_s"], color=orange, linewidth=1.1, label="Drainage")
    axes[1].set(title="(b) Film input and drainage", ylabel="Film rate (kg/s)", ylim=(0, 100))
    axes[1].annotate("", xy=(455, checks["final_10ms_accretion_kg_s"]),
                     xytext=(455, checks["final_10ms_drainage_kg_s"]),
                     arrowprops={"arrowstyle": "<->", "color": "#555555", "linewidth": 0.8})
    axes[1].text(185, 89, "Input exceeds drainage", fontsize=8)
    axes[1].text(300, 42, "Final 10 ms: storage 11.53 kg/s\nBulk forcing held fixed", fontsize=7.5, ha="center",
                 bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9})
    axes[1].legend(loc="lower right", frameon=False, fontsize=8.5)
    for ax in axes:
        ax.axvspan(490, 500, color="#EFEFEF", zorder=0)
        ax.set_xlim(0, 500)
        ax.set_xticks([0, 100, 200, 300, 400, 500])
        ax.tick_params(labelsize=8.5)
        ax.grid(color="#DDDDDD", linewidth=0.6, alpha=0.7)
        ax.set_axisbelow(True)
    fig.supxlabel("Accepted film time since dry activation (ms)", y=0.045, fontsize=9.5)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for suffix in ("png", "pdf"):
        path = args.output_dir / f"{STEM}.{suffix}"
        fig.savefig(path, dpi=300, facecolor="white")
        outputs[suffix] = {"filename": path.name, "sha256": sha256(path)}
    plt.close(fig)
    provenance = {
        "figure": STEM, "source": SOURCE, "source_sha256": SOURCE_SHA256,
        "source_summary": SUMMARY, "source_summary_sha256": SUMMARY_SHA256,
        "scope": "Stage 3 nominal 26.81 m/s reference arm; selected frozen-bulk path from N5080 to N48205",
        "native_range": [5080, 48205], "selected_points": len(rows),
        "film_time_s": [float(time[0]), float(time[-1])],
        "units": {"film_time_ms": "1000 * film_time_s", "film_mass": "kg", "rates": "kg/s"},
        "processing": "All selected CSV points plotted without smoothing, subsampling or spatial interpolation. Film drainage uses the preverified CSV native cumulative-outflow rate. Grey shading marks 490-500 ms. Markers identify N5190, N13390, N25815 and the 500 ms endpoint. An arrow marks the late mean input/drainage gap; text reports the independently checked final-window storage rate under frozen bulk forcing.",
        "checks": checks,
        "claim_limit": "Prescribed-flow film development. Film inventory is still increasing; no new bulk convergence, full-model closure, timestep independence or physical validation claim.",
        "software": {"matplotlib": matplotlib.__version__, "numpy": np.__version__},
        "script": {"path": str(Path(__file__).resolve().relative_to(ROOT)), "sha256": sha256(Path(__file__))},
        "array_sha256": {key: hashlib.sha256(array.tobytes()).hexdigest() for key, array in arrays.items()},
        "markers": [{"native_iteration": n, "film_time_ms": float(milliseconds[i]), "film_mass_kg": float(arrays["film_kg"][i])}
                    for n, i in zip(markers, marker_indices)],
        "layout": {"panels": "two side by side", "size_cm": [16, 6.5]},
        "output": outputs,
    }
    (args.output_dir / f"{STEM}-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({"source_hashes": "PASS", "selected_points": len(rows), "final_10ms_checks": "PASS", "outputs": list(outputs)}))


if __name__ == "__main__":
    main()
