"""Create descriptive report displays for three earlier liquid-removal studies.

The outlet screen uses verified endpoint/status records because its original
inventory histories are absent. The other two figures reproduce the existing
native curves from unchanged data. Original experiment assets are untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "Project/Final research report/Shuhei Report/figures"
SCREEN = "Project/experiments/phase-05-full-geometry-v2/full-geometry-02e-mixture-outlet-characterization/stage-01/results.md"
COLLECTOR = "PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G100-student-20260910T045745Z-reports.json"
REFERENCE = "PyAnsys/output/phase07_e0_ref/P7-E0-REF-server1-20260908T170000Z-report-histories.json"
POOL = "Project/experiments/phase-06-full-geometry-with-brine-pool/stage-06-long-horizon-surrogate-hypothesis/figures/P6-S6-H-server2-20260831T004750Z/raw/report_histories_20260831_145202.json"
RUNNER = "PyAnsys/output/phase06_stage06/P6-S6-H-server2-20260831T004750Z.runner.json"
EXPECTED = {
    COLLECTOR: "b16f0ddcfda8d4f3f9f434053ba13ea5b070ff67f2a21bbc238df5cbbb5b6773",
    REFERENCE: "e883ca73c0789a4bb45e28eae4540b2d25fcf17b5ff64d89248a99a20cd9c142",
    POOL: "a92e62c424a53d434570e512f1f4a9bfd33e7f4f56c5a5950af0d5f753ac25b6",
    RUNNER: "2b29734f98473baf26cd0c6bf087f929f3c0934eda657326ef355c4f088a7811",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(relative: str):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, ROOT / relative)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def save(fig, stem: str, out: Path, sources: list[str], checks: dict, arrays: dict) -> None:
    outputs = {}
    for suffix in ("png", "pdf"):
        path = out / f"{stem}.{suffix}"
        fig.savefig(path, dpi=300, facecolor="white")
        outputs[suffix] = {"filename": path.name, "sha256": sha256(path)}
    texts = [artist.get_text() for artist in fig.findobj(matplotlib.text.Text) if artist.get_text()]
    if any(re.search(r"Setup|Stage|P7-|\bE0\b|\bF1\b|phase-2", text) for text in texts):
        raise ValueError("An internal identifier remains in visible plot text")
    provenance = {
        "figure": stem,
        "script": {"path": str(Path(__file__).resolve().relative_to(ROOT)), "sha256": sha256(Path(__file__))},
        "sources": [{"path": relative, "sha256": sha256(ROOT / relative)} for relative in sources],
        "checks": checks,
        "array_sha256": {key: hashlib.sha256(np.asarray(array, dtype=np.float64).tobytes()).hexdigest() for key, array in arrays.items()},
        "plot_text": texts,
        "output": outputs,
        "size_inches": list(fig.get_size_inches()),
        "processing": "Presentation from recorded data only. All curve points retained without smoothing, interpolation or resampling. Original evidence is unchanged.",
        "software": {"matplotlib": matplotlib.__version__, "numpy": np.__version__},
    }
    (out / f"{stem}.provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    plt.close(fig)


def outlet_screen(out: Path) -> None:
    owner = (ROOT / SCREEN).read_text()
    pattern = r"\| `((?:PO|OV|MF|EF)-P[123])` \| `([^`]+)` \| `(COMPLETE_500|FAILED_FPE)` \| (\d+) \|"
    rows = re.findall(pattern, owner)
    original_source = "PyAnsys/scripts/inspection/analyze_02e_stage1_histories.py"
    original = module(original_source)
    if len(rows) != 12:
        raise ValueError("Expected 12 verified outlet-screen rows")
    for case, control, status, end in rows:
        meta = original.RUNS[case]
        if (meta["control"], meta["status"], meta["n"]) != (control, status, int(end)):
            raise ValueError(f"Endpoint record differs from original plotting source: {case}")
    completed = sum(status == "COMPLETE_500" for _, _, status, _ in rows)
    if completed != 4:
        raise ValueError("Completion count changed")
    titles = {"PO": "Pressure outlet (gauge pressure)", "OV": "Outlet vent (loss coefficient K)",
              "MF": "Mass-flow outlet (prescribed flow)", "EF": "Exhaust fan (pressure change)"}
    fig, axes = plt.subplots(2, 2, figsize=(16 / 2.54, 10 / 2.54), sharex=True)
    fig.subplots_adjust(left=0.20, right=0.98, bottom=0.16, top=0.80, hspace=0.65, wspace=0.65)
    blue, orange = "#0072B2", "#B86D20"
    for ax, family in zip(axes.flat, ("PO", "OV", "MF", "EF")):
        selected = [row for row in rows if row[0].startswith(family)]
        ends = [int(row[3]) for row in selected]
        ax.barh(range(3), ends, height=0.60,
                color=[blue if row[2] == "COMPLETE_500" else orange for row in selected])
        ax.set_yticks(range(3), [row[1] for row in selected])
        ax.invert_yaxis()
        ax.set(title=titles[family], xlim=(0, 580))
        ax.set_xticks([0, 250, 500])
        ax.tick_params(labelsize=8.5)
        for y, end in enumerate(ends):
            ax.text(end + 8, y, str(end), va="center", fontsize=8.5)
        ax.grid(axis="x", alpha=0.25)
        ax.set_axisbelow(True)
    fig.legend(handles=[Patch(color=blue, label="Completed 500 iterations (4)"),
                        Patch(color=orange, label="Numerical failure (8)")],
               loc="upper center", bbox_to_anchor=(0.55, 0.97), frameon=False, ncol=2, fontsize=8.5)
    fig.supxlabel("Iterations reached (unequal horizons)", y=0.035, fontsize=9.5)
    save(fig, "appendix-outlet-screen-endpoints", out, [SCREEN, original_source], {
        "completed": 4, "failed": 8,
        "endpoint_records": [{"archive_identifier": case, "physical_control": control, "status": status, "iterations_reached": int(end)}
                             for case, control, status, end in rows],
        "comparison": "Replacement endpoint/status display; unavailable regional-inventory curves are not reconstructed.",
        "claim_limit": "Completion describes the recorded horizon, not convergence or physical validity.",
    }, {"iterations_reached": [int(row[3]) for row in rows]})


def collector_history(out: Path) -> None:
    original_source = "PyAnsys/scripts/analysis/analyze_p7_treatment_screen.py"
    original = module(original_source)
    records, reference = original.load_records(ROOT / COLLECTOR), original.load_records(ROOT / REFERENCE)
    x = original.array(records, "e0-liquid-mass-total", "iterations")
    mass = original.array(records, "e0-liquid-mass-total")
    ref_x = original.array(reference, "e0-liquid-mass-total", "iterations")
    ref_mass = original.array(reference, "e0-liquid-mass-total")
    if (x[0], x[-1], len(x), ref_x[0], ref_x[-1], len(ref_x)) != (501, 1000, 500, 1, 2000, 2000):
        raise ValueError("Collector/reference horizons changed")
    if mass[-1] != 332.5241907618081:
        raise ValueError("Collector endpoint changed")
    late_lo, late_hi = float(max(x[0], x[-1] - 249)), float(x[-1])
    fig, ax = plt.subplots(figsize=(10, 5.8), constrained_layout=True)
    line_ref, = ax.plot(ref_x, ref_mass, color="#64748b", lw=1.0, ls="--", label="Closed-bottom reference")
    line_child, = ax.plot(x, mass, color="#1d4ed8", lw=1.15, label="Lower-zone collector (gain 1.0)")
    ax.axvspan(late_lo, late_hi, color="#f59e0b", alpha=0.10, label="Late window: 751–1000")
    ax.set(xlabel="Native solver iteration", ylabel="Continuous-liquid mass [kg]",
           title="Lower-zone collection and bulk liquid inventory")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    assert np.array_equal(line_ref.get_xydata(), np.column_stack((ref_x, ref_mass)))
    assert np.array_equal(line_child.get_xydata(), np.column_stack((x, mass)))
    save(fig, "appendix-collector-inventory-comparison", out, [COLLECTOR, REFERENCE, original_source], {
        "source_curve_array_equality": True, "child_points": len(x), "reference_points": len(ref_x),
        "child_window": [501, 1000], "late_statistical_window": [751, 1000],
        "shading_coordinates": [late_lo, late_hi], "child_final_mass_kg": float(mass[-1]),
        "claim_limit": "Different run horizons; collector mass still increases; no convergence or efficiency claim.",
    }, {"child_iteration": x, "child_mass_kg": mass, "reference_iteration": ref_x, "reference_mass_kg": ref_mass})


def pool_history(out: Path) -> None:
    original_source = "PyAnsys/scripts/analysis/analyze_p6_s6_long_hypothesis.py"
    original = module(original_source)
    payload, runner = (json.loads((ROOT / relative).read_text()) for relative in (POOL, RUNNER))
    if payload.get("errors"):
        raise ValueError("Native report recovery has errors")
    records = {str(record["report_definition"]): record for record in payload["reports"]}
    x, mass = original.history(records, "03a_stage3_inventory_y010_liquid_mass")
    chunks = runner["chunks"]
    if len(chunks) != runner["chunks_requested"] or len(chunks) != 100 or runner["target_proxy_kg"] != 200:
        raise ValueError("Incomplete pressure-control record")
    cx = np.array([float(chunk["report_iteration_after"]) for chunk in chunks])
    pressure = np.array([float(chunk["pressure_after_pa"]) for chunk in chunks]) / 1_000_000.0
    cx = np.insert(cx, 0, float(chunks[0]["report_iteration_before"]))
    pressure = np.insert(pressure, 0, float(chunks[0]["pressure_before_pa"]) / 1_000_000.0)
    if len(x) != 10051 or mass[-1] != 284.8335783200515:
        raise ValueError("Pool-control mass history changed")
    fig, axes = plt.subplots(2, 1, figsize=(9, 6.8), sharex=True, constrained_layout=True)
    mass_line, = axes[0].plot(x, mass, label="Liquid mass at y ≤ 0.10 m", color="#1d4ed8")
    axes[0].axhline(200, color="black", linestyle="--", linewidth=1, label="Assumed target (200 kg)")
    axes[0].set(ylabel="Lower-region liquid mass [kg]", title="Lower-region liquid inventory and bounded pressure control")
    axes[0].grid(alpha=0.25)
    axes[0].legend(fontsize=8)
    pressure_line, = axes[1].step(cx, pressure, where="post", color="#b45309", label="Reported brine pressure")
    axes[1].set(xlabel="Native Fluent iteration", ylabel="Brine pressure [MPa gauge]")
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=8)
    assert np.array_equal(mass_line.get_xydata(), np.column_stack((x, mass)))
    assert np.array_equal(pressure_line.get_xydata(), np.column_stack((cx, pressure)))
    save(fig, "appendix-pool-control-history", out, [POOL, RUNNER, original_source], {
        "source_curve_array_equality": True, "mass_points": len(x), "pressure_points": len(cx),
        "pressure_drawstyle": "steps-post", "assumed_target_kg": 200,
        "first_mass_kg": float(mass[0]), "final_mass_kg": float(mass[-1]),
        "claim_limit": "Numerical liquid-mass target; unequal physical and numerical meanings retained; no physical level-control or convergence claim.",
    }, {"mass_iteration": x, "lower_mass_kg": mass, "pressure_iteration": cx, "pressure_mpa_gauge": pressure})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    for relative, expected in EXPECTED.items():
        if sha256(ROOT / relative) != expected:
            raise ValueError(f"Immutable source changed: {relative}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"path.simplify": False, "agg.path.chunksize": 0, "axes.titlesize": 9.5})
    outlet_screen(args.output_dir)
    collector_history(args.output_dir)
    pool_history(args.output_dir)
    print("PASS: three report displays, exact source arrays for two native histories, verified outlet-screen endpoint/status table")


if __name__ == "__main__":
    main()
