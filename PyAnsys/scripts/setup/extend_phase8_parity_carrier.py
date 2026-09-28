#!/usr/bin/env python3
"""Extend a completed Phase 8 carrier from one verified 1,000-block endpoint."""
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
from build_phase8_numerical_recovery_f1 import inspect as audit_recovery_f1
from build_phase8_numerical_recovery_f2 import inspect as audit_recovery_f2
from run_phase8_parity_carrier import (
    FAILURE_MARKER, FINAL_ROOT, ITERATION_ROW, RUN_ROOT, audit_parity,
    check_reports, dump, load_pair, require, save_pair, sha256,
)


def extend(source_manifest: Path, target: int) -> dict:
    source = json.loads(source_manifest.read_text(encoding="utf-8"))
    start = source.get("achieved_active_iterations")
    require(source["status"] == "COMPLETE" and isinstance(start, int) and start >= 2000,
            "Source is not a verified completed carrier")
    require(target > start and target % 1000 == 0, "Target must extend the source by whole 1,000-iteration blocks")
    family = source["family"]
    speed = source["speed_m_s"]
    variant = source.get("variant")
    if variant == "coupled-global-time-step-recovery":
        audit = (lambda solver: audit_recovery_f1(solver, speed=speed)) if family == "F1" else (
            lambda solver: audit_recovery_f2(solver, speed=speed))
    else:
        audit = lambda solver: audit_parity(solver, exact_flows=False)
    variant_label = "coupled-gts-" if variant else ""
    label = f"{family}-{str(speed).replace('.', 'p')}-{variant_label}extension-to{target}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    local = RUN_ROOT / label
    final = FINAL_ROOT / label
    manifest = ROOT / "output" / "phase8-carrier" / label / "manifest.json"
    require(not local.exists() and not final.exists() and not manifest.exists(), f"Run exists: {label}")
    local.mkdir(parents=True)
    final.mkdir(parents=True)
    source_pair = Path(source["checkpoints"][-1]["case"])
    source_base = Path(str(source_pair).removesuffix(".cas.h5"))
    receipt = {"status": "RUNNING", "family": family, "variant": variant, "speed_m_s": speed, "source_manifest": str(source_manifest),
               "source_case": str(source_pair), "source_data": str(source["checkpoints"][-1]["data"]),
               "source_case_sha256": sha256(source_pair), "source_data_sha256": sha256(Path(source["checkpoints"][-1]["data"])),
               "start_active_iteration": start, "target_active_iteration": target, "report_cadence": 10,
               "paths": {"local": str(local), "final": str(final), "monitors": str(local / "monitors"),
                         "transcript": str(local / "transcript.txt")},
               "checkpoints": [], "claim_limit": "steady inventory drift per iteration is not physical storage rate"}
    dump(manifest, receipt)
    solver = None
    capture = None
    try:
        solver = launch_fluent(product_version="25.2", dimension=3, precision="double", processor_count=4,
                               ui_mode="gui", start_timeout=240, cleanup_on_exit=True, start_transcript=True)
        load_pair(solver, source_base)
        receipt["start_readback"] = audit(solver)
        receipt["autosave_configuration"] = configure_autosave(solver, str(local), data_frequency=1000)
        receipt["residual_configuration"] = configure_residual_history(solver, target + 500)
        monitor_root = local / "monitors"
        monitor_root.mkdir(parents=True)
        paths = {}
        for definition in source["report_definitions"]:
            report = solver.settings.solution.monitor.report_files[f"{definition}-rfile"]
            report.active = False
            path = monitor_root / f"{definition}.out"
            require(not path.exists(), f"Report path exists: {path}")
            report.file_name = str(path)
            report.active = True
            paths[definition] = str(path)
        receipt["report_definitions"] = source["report_definitions"]
        receipt["report_paths"] = paths
        check_reports(solver, source["report_definitions"], paths)
        receipt["initial_report_compute"] = solver.settings.solution.report_definitions.compute(report_defs=list(paths))
        require(len(receipt["initial_report_compute"]) == len(paths), "Initial report computation incomplete")
        solver.settings.mesh.check()
        capture = SessionTranscriptCapture(solver, stream_path=local / "transcript.txt").start()
        receipt["start_pair"] = save_pair(solver, local / f"active{start}")
        load_pair(solver, local / f"active{start}")
        receipt["start_reopen_readback"] = audit(solver)
        check_reports(solver, source["report_definitions"], paths)
        dump(manifest, receipt)
        for endpoint in range(start + 1000, target + 1, 1000):
            marker = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=1000)
            capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10)
            block = capture.text_since(marker)
            rows = [int(value) for value in ITERATION_ROW.findall(block)]
            require(rows and rows[-1] == endpoint and set(range(endpoint - 999, endpoint + 1)).issubset(set(rows)),
                    f"Incomplete iteration block: N{endpoint}, last={rows[-1] if rows else None}")
            require(not FAILURE_MARKER.search(block), f"Fatal event in N{endpoint} block")
            pair = save_pair(solver, final / "final" if endpoint == target else local / f"active{endpoint}")
            receipt["checkpoints"].append({"active_iteration": endpoint, "transcript_unique_rows": len(set(rows)), **pair})
            receipt["last_valid_active_iteration"] = endpoint
            dump(manifest, receipt)
            if endpoint == start + 1000:
                require(all(Path(path).stat().st_size > 0 for path in paths.values()), "Native reports not recording")
        load_pair(solver, final / "final")
        receipt["final_reopen_readback"] = audit(solver)
        check_reports(solver, source["report_definitions"], paths)
        receipt["report_file_bytes"] = {name: Path(path).stat().st_size for name, path in paths.items()}
        receipt["achieved_active_iterations"] = target
        receipt["status"] = "COMPLETE"
        dump(manifest, receipt)
        return {"status": "COMPLETE", "manifest": str(manifest), "final_pair": receipt["checkpoints"][-1]}
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        dump(manifest, receipt)
        raise
    finally:
        if capture is not None:
            capture.close()
        if solver is not None and receipt["status"] == "COMPLETE":
            solver.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_manifest", type=Path)
    parser.add_argument("--target", type=int, default=5000)
    args = parser.parse_args()
    print(json.dumps(extend(args.source_manifest, args.target), indent=2), flush=True)
