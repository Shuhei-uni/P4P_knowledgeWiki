"""Reconcile the two running cap tests, run R5, and verify their evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
STAMP = "20261002T122100Z"
RUNS = {name: f"{name}-{STAMP}" for name in ("R3", "R4", "R5")}
BASE = ROOT / "PyAnsys/output/phase72a-stage2-cap1m"


def read_manifest(case):
    return json.loads((BASE / RUNS[case] / "run-manifest.json").read_text(encoding="utf-8"))


def wait_for(case, deadline):
    previous = None
    while time.monotonic() < deadline:
        record = read_manifest(case)
        status = record["status"]
        progress = (status, len(record.get("completed_blocks", [])))
        if progress != previous:
            print(case, "status/blocks", progress, flush=True)
            previous = progress
        if status == "COMPLETE":
            verify(case)
            return
        if status in {"BLOCKED", "EXECUTION_UNCERTAIN"}:
            raise RuntimeError(f"{case}: {record.get('error', status)}; reconcile before any restart")
        time.sleep(30)
    raise TimeoutError(f"{case} exceeded supervision horizon; Fluent is preserved")


def verify(case):
    record = read_manifest(case)
    assert record["status"] == "COMPLETE", (case, record["status"])
    assert record["terminal_native_iteration"] == 16586
    assert record["parent_hashes_expected"] == record["parent_hashes_observed"]
    assert len(record["completed_blocks"]) == 3
    assert record["final_reopen_e27_readback"]["model_parameters"]["thickness-limit"] == 1.0
    for tag in ("final_pair_local", "final_pair_durable"):
        for key in ("case_sha256", "data_sha256"):
            assert re.fullmatch(r"[0-9a-f]{64}", record[tag][key])
    histories = json.loads((BASE / RUNS[case] / "report-histories.json").read_text())
    assert len(histories) == 27
    for name, history in histories.items():
        assert history["points"] >= 3000, (case, name)
        assert history["iterations"][-1] == 16586, (case, name)
        assert len(history["iterations"]) == len(history["values"])
    return record, histories


def analyse():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    figures = ROOT / "Project/experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/figures"
    old = json.loads((figures / "E2.7-R3-R4-R5-summary.json").read_text())
    metrics = [
        ("p72a-e2.7-ewf-thickness-max", "Maximum film thickness (m)"),
        ("p72a-e2.7-ewf-film-mass-total", "Film mass (kg)"),
        ("p72a-e2.7-ewf-velocity-mag-awavg", "Area-weighted film speed (m/s)"),
        ("v2-total-liquid-mass", "Bulk liquid mass (kg)"),
        ("v2-flux-phase2-steamoutlet", "Signed liquid outlet flux (kg/s)"),
        ("p72a-stage2-ewf-wetted-area", "Wetted area (m2)"),
    ]
    summary = {"cap_m": 1.0, "native_start": 13586, "native_end": 16586, "cases": {},
               "claim_limit": "Exploratory numerical limit; a reached cap censors thickness. No physical film or drainage qualification."}
    fig, axes = plt.subplots(3, 2, figsize=(13, 10), sharex=True)
    for case, color in zip(RUNS, ("#3f74b8", "#d38528", "#40906b")):
        manifest, histories = verify(case)
        stats = {"manifest": str(BASE / RUNS[case] / "run-manifest.json"), "metrics": {},
                 "final_pair": manifest["final_pair_local"],
                 "reopen_native_iteration": manifest["final_reopen_native_iteration"]}
        for ax, (name, label) in zip(axes.flat, metrics):
            x = np.asarray(histories[name]["iterations"], dtype=int)
            y = np.asarray(histories[name]["values"], dtype=float)
            assert np.isfinite(y).all(), (case, name, "nonfinite history")
            mask = x >= 16087
            baseline = old["cases"][case][name]
            if name.endswith("thickness-max"):
                # The old plotting summary used mm; keep comparison in metres.
                baseline = {key: value / 1000.0 for key, value in baseline.items()}
            stats["metrics"][name] = {"first": float(y[0]), "last": float(y[-1]),
                "min": float(y.min()), "max": float(y.max()),
                "tail500_mean": float(y[mask].mean()),
                "tail500_slope_per_iteration": float(np.polyfit(x[mask], y[mask], 1)[0]),
                "old_0p3m_cap_stats": baseline}
            if name.endswith("thickness-max"):
                stats["first_at_0p3m"] = int(x[y >= 0.3 - 1e-9][0]) if (y >= 0.3 - 1e-9).any() else None
                stats["first_at_1m"] = int(x[y >= 1.0 - 1e-9][0]) if (y >= 1.0 - 1e-9).any() else None
            ax.plot(x, y, color=color, linewidth=0.8, label=case + " / 1 m cap")
            ax.set_ylabel(label)
            ax.grid(alpha=0.2)
        summary["cases"][case] = stats
    axes[0, 0].axhline(0.3, color="grey", linestyle="--", label="Former 0.3 m cap")
    axes[0, 0].axhline(1.0, color="black", linestyle=":", label="New 1 m cap")
    axes[0, 0].legend(fontsize=8)
    for ax in axes[-1]:
        ax.set_xlabel("Native Fluent iteration")
    fig.suptitle("Phase 7.2A Stage 2 — matched 1 m film-limit sensitivity")
    fig.tight_layout()
    path = figures / ("E2.7-" + "-".join(RUNS) + "-cap1m-histories.png")
    fig.savefig(path, dpi=160)
    plt.close(fig)
    summary["figure"] = str(path)
    (BASE / "verified-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("Verified cap-sensitivity evidence:", BASE / "verified-summary.json", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--runs-json", type=Path, help="Reconciled replacement manifests; original run evidence stays immutable")
    args = parser.parse_args()
    if args.runs_json:
        RUNS.update(json.loads(args.runs_json.read_text()))
    cancellations = BASE / "cancelled-cases.json"
    if cancellations.exists():
        for case in json.loads(cancellations.read_text()):
            RUNS.pop(case, None)
    if args.verify_only:
        for case in RUNS:
            verify(case)
        assert (BASE / "verified-summary.json").is_file()
        return
    deadline = time.monotonic() + 4 * 3600
    wait_for("R3", deadline)
    if "R5" not in RUNS:
        wait_for("R4", deadline)
        analyse()
        return
    target = BASE / RUNS["R5"]
    if target.exists():
        print("R5 already exists; reconcile only, no duplicate launch", flush=True)
    else:
        command = [sys.executable, str(ROOT / "PyAnsys/scripts/setup/run_phase72a_stage2_e27_roughness.py"),
                   "--case", "R5", "--server-id", "1", "--max-film-thickness", "1",
                   "--stamp", STAMP, "--output-root", str(target)]
        print("Starting R5 on now-free server 1", flush=True)
        with (BASE / "R5-runner.log").open("x", encoding="utf-8") as log:
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            try:
                result = child.wait(timeout=max(1, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                raise TimeoutError("R5 remains live; preserve and reconcile its process before continuing")
        if result:
            raise RuntimeError(f"R5 runner returned {result}; inspect its manifest")
    wait_for("R4", deadline)
    wait_for("R5", deadline)
    analyse()


if __name__ == "__main__":
    main()
