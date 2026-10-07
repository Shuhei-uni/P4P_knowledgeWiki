"""Reduce the retrieved native guard receipt without inventing missing histories.

This is a local, read-only solver analysis. It issues no Fluent calls and writes
only derived evidence and the Project figure. Full film accounting remains
unavailable until the solved native histories can be recovered.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "PyAnsys/output/phase72a-stage4-ewf-long-native/20261007"
FIGURES = ROOT / ("Project/experiments/phase-07-2a-wall-liquid-routing/"
                  "stage-04-ewf-wall-parameters/ewf-only-drain/long-development/figures")
PROBE = OUT / "inspection/check-20261008.json"
PREPARED = OUT / "prepared-readback.json"
RECORD = r"\((\d+) (\d+) (\d+) ([0-9.eE+-]+) (#t|#f)\)"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    probe = json.loads(PROBE.read_text())
    prepared = json.loads(PREPARED.read_text())
    manifest = json.loads((OUT / "run-manifest.json").read_text())
    header = re.match(r'^\("([A-Z_]+)" (\d+) ', probe["state"])
    if header is None:
        raise ValueError("Unrecognised native state receipt")
    status, completed_text = header.groups()
    completed = int(completed_text)
    records = re.findall(RECORD, probe["state"])
    if len(records) != 2 or records != re.findall(RECORD, probe["histories"]):
        raise ValueError("Native status and history receipts disagree")
    h, c = records
    start, end, samples = map(int, h[:3])
    if h[:3] != c[:3] or h[4] != "#t" or c[4] != "#t":
        raise ValueError("Guard histories are incomplete or nonconsecutive")
    if end - start != completed or samples != completed + 1:
        raise ValueError("Native counter and history coverage disagree")
    flags = re.search(r'\) (#t|#f) (#t|#f) (#t|#f) (#t|#f) (#t|#f)\)$', probe["histories"])
    if flags is None:
        raise ValueError("Missing native file-presence receipt")
    unrealistic, final_case, final_data, rejected_case, rejected_data = (
        item == "#t" for item in flags.groups())
    peak_h, peak_c = float(h[3]), float(c[3])
    if status != "NUMERICAL_REJECTED" or peak_c < 1 or peak_h >= .3:
        raise ValueError("Receipt does not describe the expected Courant guard stop")
    parent_h = prepared["fields"]["p72d-total-thickness"][0]
    parent_c = prepared["fields"]["p72d-total-courant"][0]
    dt = manifest["fixed_film_step_s"]
    inferred_added = completed * dt
    summary_path = OUT / "partial-analysis-summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    summary.update(
        status="STOPPED_NUMERICAL_GUARD_ANALYSED_AVAILABLE_EVIDENCE",
        native_start=start, native_end=end, completed_updates=completed,
        planned_updates=manifest["submitted_updates"],
        horizon_percent=100 * completed / manifest["submitted_updates"],
        fixed_declared_film_step_s=dt,
        added_film_time_inferred_s=inferred_added,
        total_film_time_inferred_s=prepared["film"]["film_elapsed_time"] + inferred_added,
        peak_thickness_m=peak_h, peak_courant=peak_c,
        parent_thickness_m=parent_h, parent_courant=parent_c,
        peak_thickness_over_parent=peak_h / parent_h,
        peak_thickness_percent_of_limit=100 * peak_h / .3,
        peak_courant_over_guard=peak_c, peak_courant_over_parent=peak_c / parent_c,
        thickness_limit_reached=False, native_stop_classification=status,
        native_samples=samples, native_histories_consecutive=True,
        unrealistic_marker_present=unrealistic,
        expected_final_pair_present=final_case and final_data,
        rejected_pair_presence_at_probe=rejected_case and rejected_data,
        first_guard_crossing_iteration_inferred_range=[end - manifest["native_block_updates"] + 1, end],
        first_guard_crossing_range_basis="Native loop stops at the first failing all-history block guard; exact crossing sample unavailable",
        full_horizon_reached=False, steady_film="NOT_ESTABLISHED",
        stationarity_required_windows_s=[.25, .25, .25],
        available_inferred_duration_s=inferred_added,
        report_complete_for_available_evidence=True, full_history_analysis_complete=False,
        evidence_recovery="UNAVAILABLE_CURRENT_CONNECTION_USER_REQUESTED_REPORT_FROM_AVAILABLE_EVIDENCE",
        no_new_solves_issued=True,
        source_sha256={str(p.relative_to(ROOT)): digest(p) for p in (PROBE, PREPARED)},
        native_probe=probe,
    )
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
    labels = [f"Parent N{start}", "Continuation maximum"]
    for ax, values, title, unit, precision in (
        (axes[0], [parent_h * 1000, peak_h * 1000], "Film thickness", "mm", 3),
        (axes[1], [parent_c, peak_c], "Film Courant", "Courant number", 3),
    ):
        bars = ax.bar(labels, values, color=["#808080", "#0072B2"], width=.6)
        ax.set_title(title)
        ax.set_ylabel(unit)
        ax.grid(axis="y", alpha=.25)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.bar_label(bars, fmt=f"%.{precision}f", padding=5)
        ax.set_ylim(0, max(values) * 1.25)
    axes[0].text(.03, .95, "Thickness limit: 300 mm\n(outside this plot range)",
                 transform=axes[0].transAxes, va="top")
    axes[1].axhline(1, color="#D55E00", linestyle="--", label="Declared stop value: 1")
    axes[1].legend(loc="upper left", frameon=True)
    fig.suptitle(f"Native guard stop at N{end} — {completed:,} additional updates")
    figure = FIGURES / "native-guard-summary.png"
    fig.savefig(figure, dpi=170)
    plt.close(fig)
    provenance = {
        "figure": figure.name,
        "source_parent": str(PREPARED.relative_to(ROOT)),
        "source_peaks": str(PROBE.relative_to(ROOT)),
        "source_sha256": summary["source_sha256"],
        "analysis_script": str(Path(__file__).resolve().relative_to(ROOT)),
        "interpretation": "Parent snapshot versus maximum over recorded continuation; maxima are not endpoint values; no interpolated time history",
        "visual_qa": "PENDING",
    }
    (FIGURES / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in (
        "status", "native_end", "completed_updates", "peak_thickness_m", "peak_courant",
        "full_history_analysis_complete", "steady_film")}, indent=2))


if __name__ == "__main__":
    main()
