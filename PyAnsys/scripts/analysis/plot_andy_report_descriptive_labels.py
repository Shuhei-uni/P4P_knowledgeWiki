"""Replot Andy report Figures 6–8 from saved evidence with descriptive labels.

No Fluent connection or solver updates. Original experiment and partner assets
are read-only. Run with PyAnsys/.venv/bin/python from any working directory.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/andy-report-mpl")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from analyze_phase07b_screen import parse_history, parse_residuals

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "Project/Final research report/AndyReport"
FIGURES = REPORT / "figures"
PARTNER = REPORT.parent / "Shuhei Report/figures"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}


def save(fig, stem, provenance):
    path = FIGURES / f"{stem}.png"
    fig.savefig(path, dpi=240)
    texts = [t.get_text() for t in fig.findobj(matplotlib.text.Text) if t.get_text()]
    plt.close(fig)
    provenance.update(
        figure=stem, date="2026-10-17",
        script=source(Path(__file__).resolve()),
        output={"png": {"filename": path.name, "sha256": sha256(path)}},
        plot_text=texts,
        processing="Regenerated with Matplotlib from the exact saved numeric evidence. No image pixels edited, smoothing, resampling, or new solver updates.",
        software={"matplotlib": matplotlib.__version__, "numpy": np.__version__},
    )
    (FIGURES / f"{stem}.provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return provenance


def direct_drain():
    path = ROOT / "PyAnsys/output/phase72a-stage4-ewf-drain/20261007/analysis-summary.json"
    original = PARTNER / "results-direct-film-drain.provenance.json"
    prior = json.loads(original.read_text())
    # The analysis summary is not present in this checkout. Its full-precision
    # plotted values survive in the unchanged partner figure's provenance.
    # Use that numeric record explicitly; do not claim a fresh raw-data audit.
    assert prior["conditions_verified"]
    assert sha256(PARTNER / "results-direct-film-drain.png") == prior["output"]["png"]["sha256"]
    lower = prior["values"]["lower_final_kg_off_on"]
    edge = prior["values"]["native_outflow_kg_off_on"]
    drain = prior["values"]["direct_sink_kg_off_on"]
    external = [edge[i] + drain[i] for i in range(2)]
    for key, values in [("lower_final_kg_off_on", lower), ("native_outflow_kg_off_on", edge),
                        ("direct_sink_kg_off_on", drain), ("external_removal_kg_off_on", external)]:
        assert values == prior["values"][key], key
    reduction = 100 * (lower[0] - lower[1]) / lower[0]
    gain = external[1] - external[0]
    fig, axes = plt.subplots(1, 2, figsize=(8.3, 3.8))
    grey, blue = "#8E8E8E", "#0072B2"
    axes[0].bar([0, 1], lower, width=.55, color=[grey, blue])
    axes[0].set(title="(a) Lower-wall film after 15 ms", ylabel="Film mass (kg)", ylim=(0, .245))
    for i, value in enumerate(lower):
        axes[0].text(i, value + .007, f"{value:.5f}", ha="center", va="bottom")
    axes[0].text(.5, .232, f"{reduction:.2f}% less lower-wall film", ha="center", va="top", fontsize=10)
    axes[1].bar([0, 1], edge, width=.55, color=grey, label="Existing film-edge outflow")
    axes[1].bar([0, 1], drain, bottom=edge, width=.55, color=blue, label="Direct film drain")
    axes[1].set(title="(b) External removal over 15 ms", ylabel="Removed liquid (kg)", ylim=(0, .9))
    for i in range(2):
        axes[1].text(i, external[i] + .018, f"{external[i]:.4f}", ha="center", va="bottom")
        axes[1].text(i, edge[i] / 2, f"{edge[i]:.4f}", ha="center", va="center", color="white")
        if drain[i]:
            axes[1].text(i, edge[i] + drain[i] / 2, f"{drain[i]:.4f}", ha="center", va="center", color="white")
    axes[1].text(.5, .86, f"Net gain: +{gain:.4f} kg", ha="center", va="top", fontsize=10)
    axes[1].legend(loc="upper center", bbox_to_anchor=(.5, -.19), frameon=False, fontsize=9)
    for ax in axes:
        ax.set_xticks([0, 1], ["Drain disabled", "Drain enabled"])
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#DDDDDD", linewidth=.6)
        ax.spines[["top", "right"]].set_visible(False)
    fig.subplots_adjust(left=.09, right=.99, top=.87, bottom=.26, wspace=.43)
    return save(fig, "results-direct-film-drain", {
        "source": source(original), "original_figure": source(PARTNER / "results-direct-film-drain.png"),
        "original_provenance": source(original), "scope": prior["scope"], "values": prior["values"],
        "conditions_verified_in_original_provenance": True, "numeric_values_equal_to_original": True,
        "upstream_analysis_record": prior["source"],
        "upstream_record_available_in_checkout": path.exists(),
        "verification_scope": "Full-precision values reproduced from original figure provenance; original image hash checked. Upstream analysis summary is absent locally, so no fresh native-evidence verification is claimed.",
        "label_mapping": {"Native outflow": "Existing film-edge outflow", "Direct sink": "Direct film drain",
                          "Drain OFF": "Drain disabled", "Drain ON": "Drain enabled"},
        "credit": "Adapted from Yokkaichi (2026, Figure 17); figure supplied by Shuhei Yokkaichi. Labels clarified; numerical values unchanged.",
        "claim_limit": prior["claim_limit"],
    })


def pool_starts():
    path = ROOT / "PyAnsys/output/phase09/comparison/two-start-comparison.json"
    summary = json.loads(path.read_text())
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 8), layout="constrained")
    traces, inputs = {}, [source(path)]
    for key, colour, style in [("low", "#0072B2", "-"), ("high", "#D55E00", "--")]:
        record = summary[key]
        histories, residuals = [], []
        for block in record["sources"]:
            for field in ("history", "residuals"):
                artifact = Path(block[field]["path"])
                assert sha256(artifact) == block[field]["sha256"]
                inputs.append(source(artifact))
            h, ha = parse_history(Path(block["history"]["path"]))
            r, ra = parse_residuals(Path(block["residuals"]["path"]))
            assert not ha["conflicting_indices"] and not ra["conflicting_indices"]
            histories.append(h); residuals.append(r)
        def stitch(blocks):
            for k in blocks[0]:
                if k != "iteration":
                    assert np.allclose(blocks[0][k][blocks[0]["iteration"] == 50], blocks[1][k][blocks[1]["iteration"] == 50], rtol=1e-10, atol=1e-10)
            return {k: np.concatenate([blocks[0][k][blocks[0]["iteration"] <= 50], blocks[1][k][blocks[1]["iteration"] > 50]]) for k in blocks[0]}
        h, r = stitch(histories), stitch(residuals)
        assert np.array_equal(h["iteration"], np.arange(1, 1001))
        assert np.array_equal(r["iteration"], h["iteration"])
        imbalance = 100 * abs(h["p9lnet"]) / h["p9lli"]
        inventory = 100 * (h["p9liquidmass"] / record["initial_liquid_kg"] - 1)
        assert imbalance[-1] == record["closure"]["l"]["final_absolute_pct"]
        assert inventory[-1] == record["inventory_change_from_N0_pct"]
        assert r["continuity"][-1] == record["residuals"]["continuity"]["final"]
        name = f"Initial liquid level: {record['height_m']:.2f} m"
        axes[0].plot(h["iteration"], imbalance, color=colour, ls=style, label=name)
        axes[1].plot(h["iteration"], inventory, color=colour, ls=style, label=name)
        axes[2].semilogy(r["iteration"], r["continuity"], color=colour, ls=style, label=name)
        traces[key] = {"samples": 1000, "iteration": h["iteration"].tolist(), "liquid_imbalance_pct_feed": imbalance.tolist(),
                       "liquid_inventory_change_pct": inventory.tolist(), "continuity_residual": r["continuity"].tolist()}
    axes[0].set_ylabel("Absolute liquid imbalance\n(% of liquid feed)")
    axes[0].axhline(.5, color="grey", lw=.7)
    axes[1].set_ylabel("Liquid inventory change\nfrom initial state (%)")
    axes[2].set_ylabel("Scaled continuity residual")
    axes[2].axhline(1e-3, color="grey", lw=.7)
    axes[2].set_xlabel("Steady solver iteration (not physical time)")
    for ax in axes:
        ax.legend(fontsize=9)
    fig.suptitle("Steady VOF calculations from two initial liquid levels\nSame pseudo-time scale factor (0.1) and outlet pressure condition", fontsize=12)
    return save(fig, "two-start-comparison", {
        "sources": inputs, "original_figure": source(path.with_suffix(".png")),
        "original_generator": source(ROOT / "PyAnsys/scripts/analysis/compare_phase09_starts.py"),
        "label_mapping": {"Phase 9": "Steady VOF calculations", "same scale 0.1 and downstream head": "Same pseudo-time scale factor (0.1) and outlet pressure condition",
                          "Initial pool": "Initial liquid level", "from N0": "from initial state", "Native steady iteration": "Steady solver iteration"},
        "traces": traces, "numeric_verification": "Source hashes match original comparison; identical stitching and numeric formulas; all 1000 points per curve retained; endpoint values equal original audited summary.",
        "thresholds": {"liquid_imbalance_pct_feed": .5, "scaled_continuity_residual": .001},
        "claim_limit": summary["claim_limit"],
    })


def field_comparison():
    directory = ROOT / "PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity"
    summary = json.loads((directory / "summary.json").read_text())
    comparisons, scalars = summary["field_comparisons"], summary["scalar_rows"]
    with (directory / "field-comparison.csv").open() as stream:
        csv_rows = list(csv.DictReader(stream))
    assert len(csv_rows) == len(comparisons)
    for actual, expected in zip(csv_rows, comparisons):
        for key, value in expected.items():
            assert (actual[key] == value) if isinstance(value, str) else (float(actual[key]) == value)
    cells = {row["level"]: row["cells"] for row in scalars}
    reference = f"{cells['M06'] / 1e6:.2f}-million-cell mesh"
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    series = []
    for n, style in [(1000, "o-"), (2000, "s--")]:
        rows = [row for row in comparisons if row["iteration"] == n and row["comparison"] == "MESH_TO_M06"]
        x = [cells[row["level"]] / 1e6 for row in rows]
        y = [row["velocity_vector_difference_percent_of_reference_RMS"] for row in rows]
        label = f"Across meshes at iteration {n:,}"
        ax.plot(x, y, style, label=label)
        series.append({"label": label, "cells_millions": x, "difference_percent": y})
    rows = [row for row in comparisons if row["comparison"] == "ITERATION_N1000_TO_N2000"]
    x = [cells[row["level"]] / 1e6 for row in rows]
    y = [row["velocity_vector_difference_percent_of_reference_RMS"] for row in rows]
    label = "Same mesh: iterations 1,000 to 2,000"
    ax.plot(x, y, "d:", color="black", label=label)
    series.append({"label": label, "cells_millions": x, "difference_percent": y})
    ax.set(xlabel="Cells (millions)", ylabel="Velocity-vector RMS difference (%)")
    ax.grid(alpha=.25)
    ax.legend(fontsize=10, loc="upper right")
    ax.set_title(f"Spatially averaged velocity-field comparison\nAcross-mesh reference: {reference} at the same iteration", fontsize=12)
    fig.tight_layout()
    return save(fig, "field-refinement", {
        "sources": [source(directory / name) for name in ("summary.json", "field-comparison.csv", "scalar-comparison.csv")],
        "original_figure": source(directory / "field-refinement.png"),
        "original_generator": source(ROOT / "PyAnsys/scripts/analysis/analyze_phase10_predivergence_fields.py"),
        "label_mapping": {"M06": reference, "N1000": "iteration 1,000", "N2000": "iteration 2,000"},
        "series": series, "numeric_verification": "Every saved comparison field equals the source CSV; plotted x/y arrays use the same rows and formulas as the original generator, without recalculating or modifying field comparisons.",
        "common_projection": summary["common_projection"], "source_fields": summary["sources"],
        "claim_limit": "Unconverged saved fields; reference is not an exact solution; differences are diagnostic and not discretisation-error estimates.",
    })


def main():
    plt.rcParams.update({"font.size": 10, "axes.labelsize": 11, "axes.titlesize": 11})
    # These files must remain byte-identical after rebuilding the report copies.
    protected = [*PARTNER.glob("results-direct-film-drain.*"),
                 *FIGURES.glob("literature/*"),
                 FIGURES / "results-described-early-development.png"]
    before = {str(p): sha256(p) for p in protected if p.is_file()}
    outputs = [direct_drain(), pool_starts(), field_comparison()]
    assert before == {p: sha256(p) for p in before}
    register_path = REPORT / "review/reused-figure-register.json"
    register = json.loads(register_path.read_text())
    for row in register["figures"]:
        if row["asset"] == "figures/results-direct-film-drain.png":
            row.update(copied_without_modification=False,
                       sha256=outputs[0]["output"]["png"]["sha256"],
                       source_sha256=sha256(PARTNER / "results-direct-film-drain.png"),
                       modification="Regenerated from identical source values with clearer labels; numerical values unchanged.",
                       creator_credit=outputs[0]["credit"])
    register["date"] = "2026-10-17"
    register_path.write_text(json.dumps(register, indent=2) + "\n")
    print(json.dumps({"figures_updated": [p["figure"] for p in outputs], "originals_unchanged": True}, indent=2))


if __name__ == "__main__":
    main()
