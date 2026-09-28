#!/usr/bin/env python3
"""Run the true single-face F1 SIMPLE carrier as a separate parity pilot."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]

from ansys.fluent.core import launch_fluent
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history
from build_phase8_f1_single_face_parity import inspect as inspect_single
from run_phase8_parity_carrier import (
    FAILURE_MARKER, ITERATION_ROW, RUN_ROOT, FINAL_ROOT,
    check_reports, configure_reports, dump, load_pair, require, save_pair, sha256,
)

BOUNDARIES = ("liquidinlet", "steamoutlet")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("child_receipt", type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    args = parser.parse_args()
    require(args.iterations >= 1000 and args.iterations % 1000 == 0,
            "Run in 1000-iteration blocks")
    child = json.loads(args.child_receipt.read_text(encoding="utf-8"))
    require(child["status"] == "CASE_DATA_VERIFIED", "Source child is not verified")
    source = Path(child["child_base"])
    for kind in ("case", "data"):
        path = Path(child["child_pair"][kind])
        require(path.is_file() and sha256(path) == child["child_pair"][f"{kind}_sha256"],
                f"Single-face source {kind} identity changed")
    label = f"F1-single-face-SIMPLE-26p81-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    local, final = RUN_ROOT / label, FINAL_ROOT / label
    manifest = ROOT / "output" / "phase8-single-face" / label / "manifest.json"
    require(not local.exists() and not final.exists() and not manifest.exists(),
            "Single-face pilot collision")
    local.mkdir(parents=True)
    final.mkdir(parents=True)
    run = {"status": "RUNNING", "family": "F1-single-face", "speed_m_s": 26.81,
           "source_receipt": str(args.child_receipt),
           "source_case_sha256": child["child_pair"]["case_sha256"],
           "source_data_sha256": child["child_pair"]["data_sha256"],
           "requested_iterations": args.iterations,
           "paths": {"local": str(local), "final": str(final),
                     "transcript": str(local / "transcript.txt")},
           "checkpoints": [],
           "claim_limit": "True one-face SIMPLE carrier pilot; F1/F2 matched DPM release footprint does not apply."}
    dump(manifest, run)
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double",
                           processor_count=4, ui_mode="gui", start_timeout=240,
                           cleanup_on_exit=True, start_transcript=True)
    capture = None
    try:
        load_pair(solver, source)
        run["source_readback"] = inspect_single(solver)
        run["autosave_configuration"] = configure_autosave(
            solver, str(local), data_frequency=1000)
        definitions, paths = configure_reports(
            solver, local / "monitors", boundaries=BOUNDARIES)
        run["report_definitions"] = definitions
        run["report_paths"] = paths
        run["residual_configuration"] = configure_residual_history(
            solver, args.iterations + 200)
        solver.settings.mesh.check()
        capture = SessionTranscriptCapture(solver, stream_path=local / "transcript.txt").start()
        run["start_pair"] = save_pair(solver, local / "active000")
        load_pair(solver, local / "active000")
        run["start_reopen_readback"] = inspect_single(solver)
        check_reports(solver, definitions, paths)
        run["initial_report_compute"] = solver.settings.solution.report_definitions.compute(
            report_defs=list(definitions))
        require(len(run["initial_report_compute"]) == len(definitions),
                "Single-face initial reports incomplete")
        dump(manifest, run)
        for block in range(1, args.iterations // 1000 + 1):
            marker = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=1000)
            capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10)
            output = capture.text_since(marker)
            rows = [int(value) for value in ITERATION_ROW.findall(output)]
            require(rows and set(range(rows[-1] - 999, rows[-1] + 1)).issubset(set(rows)),
                    f"Single-face block {block} missing iteration rows")
            require(not FAILURE_MARKER.search(output), f"Fatal event in block {block}")
            destination = (final / "final" if block * 1000 == args.iterations else
                           local / f"active{block*1000:04d}")
            run["checkpoints"].append({"additional_iterations": block * 1000,
                                       "native_iteration": rows[-1],
                                       **save_pair(solver, destination)})
            run["last_valid_native_iteration"] = rows[-1]
            dump(manifest, run)
        load_pair(solver, final / "final")
        run["final_reopen_readback"] = inspect_single(solver)
        check_reports(solver, definitions, paths)
        run["status"] = "COMPLETE"
    except Exception as exc:
        run["status"] = "BLOCKED"
        run["error"] = repr(exc)
        raise
    finally:
        dump(manifest, run)
        if capture is not None:
            capture.close()
        if run["status"] == "COMPLETE":
            solver.exit()
    print(json.dumps({"status": run["status"], "manifest": str(manifest)}, indent=2))


if __name__ == "__main__":
    main()
