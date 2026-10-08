"""Plot the selected Stage 4 boundary-only phase-2 steamoutlet history."""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/phase72a-stage4-core-development/20261008"
FIG = ROOT.parent / "Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/core-development/figures"
SEGMENTS = [
    ("phase72a-commercial-steel/20261006/raw/N29815-20261007", 25815, 29815),
    ("phase72a-stage4-realism/20261007/feedback-off/raw/N37149", 29815, 37149),
    ("phase72a-stage4-sensitivity/20261007/stripping-on/raw/final-N40483", 37149, 40483),
    ("phase72a-stage4-ewf-drain/20261007/on/raw/drain-screen-N40503-N41483", 40483, 41483),
    ("phase72a-stage4-analytical/20261008/momentum10/run-N41483-N41503/raw", 41483, 41503),
    ("phase72a-stage4-analytical/20261008/momentum10/run-N41503-N43483/raw", 41503, 42924),
    ("phase72a-stage4-analytical/20261008/momentum10/run-N42924-N43483/raw", 42924, 43483),
]


def main():
    values, sources, overlaps = {}, [], []
    for directory, start, end in SEGMENTS:
        path = ROOT / "output" / directory / "v2-flux-phase2-steamoutlet.out"
        rows = []
        for line in path.read_text().splitlines():
            parts = line.split()
            if len(parts) != 2:
                continue
            try:
                coordinate, value = map(float, parts)
            except ValueError:
                continue
            assert coordinate.is_integer() and np.isfinite(value)
            iteration = int(coordinate)
            if start <= iteration <= end:
                rows.append((iteration, value))
        assert [i for i, _ in rows] == list(range(start, end + 1)), path
        for iteration, value in rows:
            if iteration in values:
                assert np.isclose(values[iteration], value, rtol=0, atol=1e-11)
                overlaps.append(iteration)
            else:
                values[iteration] = value
        sources.append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "start": start, "end": end, "rows": len(rows)})
    x = np.array(sorted(values))
    assert np.array_equal(x, np.arange(25815, 43484))
    signed = np.array([values[int(i)] for i in x])
    outward = -signed
    assert (outward >= 0).all()
    capture_path = OUT / "core17/run-N43483-N48483/capture-readback.json"
    capture = json.loads(capture_path.read_text())
    assert capture["final"]["native_iteration"] == 48483
    bulk = capture["final"]["bulk"]
    latest, unit = bulk["v2-flux-phase2-steamoutlet(without-sources)"]
    assert unit == "kg/s" and np.isclose(latest, signed[-1], rtol=0, atol=1e-11)
    assert np.isclose(bulk["v2-flux-phase2-steamoutlet"][0], latest +
                      bulk["v2-flux-phase2-steamoutlet(User Mass Source)"][0])
    assert np.allclose(signed[x >= 33815], latest, rtol=0, atol=1e-11)
    peak_index = int(np.argmax(outward))
    FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.6), sharex=True)
    for ax in axes:
        ax.axvspan(33815, 48483, color="#eeeeee", zorder=0)
        ax.plot(x, outward, color="#2464a0", linewidth=1.0, label="Native report samples")
        ax.plot([43483, 48483], [-latest, -latest], linestyle="--", color="#c06c20",
                linewidth=1.7, label="Held-field reference; endpoint checks")
        ax.scatter([43483, 48483], [-latest, -latest], s=25, color="#c06c20", zorder=5)
        ax.axvline(29815, color="#8c6bb1", linestyle=":", linewidth=1)
        ax.axvline(33815, color="#666666", linestyle="--", linewidth=1)
        ax.set_ylabel("Outward liquid mass flow (kg/s)")
        ax.grid(alpha=.2)
        ax.set_xlim(25815, 48600)
        ax.tick_params(labelsize=9)
    axes[0].set_ylim(0, 2750)
    axes[0].set_title("Phase-2 boundary flow through steamoutlet — complete recorded range", loc="left", fontsize=12)
    axes[0].annotate(f"Transient peak: {outward[peak_index]:,.1f} kg/s at N{x[peak_index]}",
                     xy=(x[peak_index], outward[peak_index]), xytext=(32200, 2230),
                     arrowprops={"arrowstyle": "->", "color": "#333333"}, fontsize=10)
    axes[0].text(40000, 1900, "Bulk equations frozen\nafter N33815", ha="center", fontsize=10)
    axes[0].text(31650, 1100, "Selected mechanisms\nbulk + EWF", ha="center", fontsize=9)
    axes[0].legend(loc="upper right", fontsize=9)
    axes[1].set_ylim(0, 30)
    axes[1].set_title("Detail: 0–30 kg/s (larger values remain visible in the panel above)", loc="left", fontsize=11)
    axes[1].annotate(f"Current held value: {-latest:.3f} kg/s", xy=(48483, -latest),
                     xytext=(40700, 17), arrowprops={"arrowstyle": "->", "color": "#333333"}, fontsize=10)
    axes[1].text(27900, 26, "Commercial-steel\nbulk + EWF", ha="center", fontsize=9)
    axes[1].set_xlabel("Native global iteration (bulk solves stop at N33815)")
    axes[1].xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    fig.text(.07, .015,
             "Outward flow = − native signed boundary flux. No smoothing. N43483–N48483: no per-iteration bulk history; dashed line is a held-field reference.",
             fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(FIG / "phase2-steamoutlet-vs-iteration.png", dpi=170)
    fig.savefig(FIG / "phase2-steamoutlet-vs-iteration.pdf")
    plt.close(fig)
    with (OUT / "phase2-steamoutlet-vs-iteration.csv").open("w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["native_iteration", "signed_boundary_flux_kg_s", "outward_boundary_flow_kg_s", "evidence"])
        writer.writerows((int(i), float(v), float(-v), "NATIVE_REPORT_SAMPLE") for i, v in zip(x, signed))
        writer.writerow([48483, latest, -latest, "PAIRED_ENDPOINT_READBACK_NOT_PER_ITERATION_HISTORY"])
    provenance = {"status": "STITCHED_RAW_HISTORY_WITH_HELD_FIELD_REFERENCE", "report_name": "v2-flux-phase2-steamoutlet",
                  "phase": "phase-2", "boundary": "steamoutlet", "units": "kg/s",
                  "quantity": "Boundary-only mass flow; user mass source excluded", "display_transform": "outward = - native signed flux",
                  "raw_history_start": 25815, "raw_history_end": 43483, "raw_history_rows": len(x),
                  "verified_overlap_iterations": overlaps, "source_files": sources,
                  "bulk_freeze_iteration": 33815, "latest_native_iteration": 48483,
                  "latest_signed_boundary_flux_kg_s": latest, "latest_outward_boundary_flow_kg_s": -latest,
                  "source_inclusive_alias_kg_s": bulk["v2-flux-phase2-steamoutlet"][0],
                  "user_source_alias_kg_s": bulk["v2-flux-phase2-steamoutlet(User Mass Source)"][0],
                  "peak_outward_flow_kg_s": float(outward[peak_index]), "peak_native_iteration": int(x[peak_index]),
                  "endpoint_readback": str(capture_path), "endpoint_readback_sha256": hashlib.sha256(capture_path.read_bytes()).hexdigest(),
                  "history_gap": {"start_exclusive": 43483, "end_inclusive": 48483,
                                  "reason": "17-report production plan omitted continuous frozen-bulk reports",
                                  "display": "Dashed held-field reference plus saved endpoint marker; no invented native samples"},
                  "claim_limit": "Frozen-flow outlet plateau does not establish a steady film or predict outlet response to later film evolution",
                  "solve_issued": False, "visual_qa": "PENDING"}
    (OUT / "phase2-steamoutlet-history.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({k: provenance[k] for k in ["raw_history_rows", "latest_outward_boundary_flow_kg_s", "peak_outward_flow_kg_s", "peak_native_iteration"]}, indent=2))


if __name__ == "__main__":
    main()
