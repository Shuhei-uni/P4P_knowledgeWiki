#!/usr/bin/env python3
"""Resume an owned Phase 8 carrier solver after a controller-side interruption."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]

from ansys.fluent.core import connect_to_fluent
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from run_phase8_parity_carrier import (
    FAILURE_MARKER, ITERATION_ROW, audit_parity, check_reports, dump,
    native_iteration, require, save_pair, load_pair,
)


def resume(manifest: Path, server_info: Path) -> dict:
    receipt = json.loads(manifest.read_text(encoding="utf-8"))
    require(receipt["status"] == "BLOCKED", "Only a stopped controller can be resumed")
    require(receipt["last_valid_active_iteration"] == 50, "Expected preserved F1 smoke point")
    require(receipt["family"] == "F1" and receipt["speed_m_s"] == 26.81, "Unexpected recovery target")
    local = Path(receipt["paths"]["local"])
    final = Path(receipt["paths"]["final"])
    transcript = Path(receipt["paths"]["transcript"])
    rows = [int(value) for value in ITERATION_ROW.findall(transcript.read_text(encoding="utf-8"))]
    require(set(range(1, 1001)).issubset(set(rows)), "Transcript does not prove complete N1–1000 history")
    report_paths = receipt["report_paths"]
    require(all(Path(path).stat().st_size > 0 for path in report_paths.values()), "Report files incomplete at N1000")

    solver = connect_to_fluent(server_info_file_name=str(server_info), cleanup_on_exit=False, start_transcript=True)
    capture = None
    try:
        receipt["recovery_live_audit_n1000"] = audit_parity(solver, exact_flows=False)
        check_reports(solver, receipt["report_definitions"], report_paths)
        checkpoint = save_pair(solver, local / "active1000")
        receipt["checkpoints"].append({"active_iteration": 1000, "transcript_first_iteration": 51,
                                       "transcript_last_iteration": 1000, "transcript_unique_rows": 950, **checkpoint})
        receipt["last_valid_active_iteration"] = 1000
        receipt["status"] = "RUNNING_RECOVERED"
        dump(manifest, receipt)
        capture = SessionTranscriptCapture(solver, stream_path=local / "continuation1000-2000.txt").start()
        marker = capture.mark()
        solver.settings.solution.run_calculation.iterate(iter_count=1000)
        capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10)
        block = capture.text_since(marker)
        block_rows = [int(value) for value in ITERATION_ROW.findall(block)]
        require(block_rows and block_rows[-1] == 2000 and set(range(1001, 2001)).issubset(set(block_rows)),
                f"Continuation did not reach N2000: last={block_rows[-1] if block_rows else None}")
        require(not FAILURE_MARKER.search(block), "Fatal solver event in continuation")
        checkpoint = save_pair(solver, final / "final")
        receipt["checkpoints"].append({"active_iteration": 2000, "transcript_first_iteration": block_rows[0],
                                       "transcript_last_iteration": 2000, "transcript_unique_rows": len(set(block_rows)), **checkpoint})
        receipt["last_valid_active_iteration"] = 2000
        dump(manifest, receipt)
        load_pair(solver, final / "final")
        receipt["final_reopen_audit"] = audit_parity(solver, exact_flows=False)
        check_reports(solver, receipt["report_definitions"], report_paths)
        receipt["final_rp_current_iteration"] = native_iteration(solver)
        receipt["achieved_active_iterations"] = 2000
        receipt["report_file_bytes"] = {name: Path(path).stat().st_size for name, path in report_paths.items()}
        receipt["status"] = "COMPLETE"
        dump(manifest, receipt)
        return {"status": receipt["status"], "manifest": str(manifest), "final_pair": checkpoint}
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        dump(manifest, receipt)
        raise
    finally:
        if capture is not None:
            capture.close()
        if receipt["status"] == "COMPLETE":
            # Reconnect with ownership only after the final pair is verified.
            owner = connect_to_fluent(server_info_file_name=str(server_info), cleanup_on_exit=True, start_transcript=False)
            owner.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--server-info", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(resume(args.manifest, args.server_info), indent=2), flush=True)
