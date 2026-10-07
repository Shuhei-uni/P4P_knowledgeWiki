#!/usr/bin/env python3
"""Run a verified F1/F2 Coupled/Global Time Step recovery carrier."""
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
from build_phase8_numerical_recovery_f1 import CHILD as F1_CHILD, inspect as inspect_f1
from build_phase8_numerical_recovery_f2 import CHILD as F2_CHILD, inspect as inspect_f2
from build_phase8_purnanto_parity_pilots import AREA, TARGET_LIQUID, TARGET_SPEED, TARGET_VAPOR
from run_phase8_parity_carrier import (
    FAILURE_MARKER, FINAL_ROOT, ITERATION_ROW, RUN_ROOT,
    check_reports, configure_reports, dump, load_pair, pair,
    require, save_pair, sha256,
)


SPEEDS = (20.11, 23.46, 26.81, 29.48, 32.14)


def apply_speed(solver, family: str, speed: float) -> None:
    if speed == TARGET_SPEED:
        return
    ratio = speed / TARGET_SPEED
    inlet = solver.settings.setup.boundary_conditions.mass_flow_inlet
    if family == "F1":
        total_area = sum(AREA.values())
        for zone, area in AREA.items():
            inlet[zone].phase["phase-1"].momentum.mass_flow_rate.value = TARGET_VAPOR * ratio * area / total_area
            inlet[zone].phase["phase-2"].momentum.mass_flow_rate.value = TARGET_LIQUID * ratio * area / total_area
    else:
        inlet["liquidinlet"].phase["phase-1"].momentum.mass_flow_rate.value = 0.0
        inlet["liquidinlet"].phase["phase-2"].momentum.mass_flow_rate.value = TARGET_LIQUID * ratio
        inlet["steaminlet"].phase["phase-1"].momentum.mass_flow_rate.value = TARGET_VAPOR * ratio
        inlet["steaminlet"].phase["phase-2"].momentum.mass_flow_rate.value = 0.0
    solver.settings.solution.initialization.hybrid_initialize()


def main(family: str, speed: float) -> dict:
    require(speed in SPEEDS, f"Unselected Phase 8 speed: {speed}")
    source = F1_CHILD if family == "F1" else F2_CHILD
    audit = inspect_f1 if family == "F1" else inspect_f2
    label = f"{family}-{str(speed).replace('.', 'p')}-coupled-gts-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    local, final = RUN_ROOT / label, FINAL_ROOT / label
    manifest = ROOT / "output" / "phase8-carrier" / label / "manifest.json"
    require(not local.exists() and not final.exists() and not manifest.exists(), "Recovery run name collision")
    local.mkdir(parents=True)
    final.mkdir(parents=True)
    source_case, source_data = pair(source)
    receipt = {"status": "RUNNING", "family": family, "variant": "coupled-global-time-step-recovery",
               "speed_m_s": speed, "source_case": str(source_case), "source_data": str(source_data),
               "source_case_sha256": sha256(source_case), "source_data_sha256": sha256(source_data),
               "requested_active_iterations": 2000, "report_cadence": 10,
               "paths": {"local": str(local), "final": str(final), "monitors": str(local / "monitors"),
                         "transcript": str(local / "transcript.txt")},
               "checkpoints": [], "claim_limit": "numerical-recovery child; not Purnanto SIMPLE parity"}
    dump(manifest, receipt)
    solver = None
    capture = None
    try:
        solver = launch_fluent(product_version="25.2", dimension=3, precision="double", processor_count=4,
                               ui_mode="gui", start_timeout=240, cleanup_on_exit=False, start_transcript=True)
        load_pair(solver, source)
        receipt["reference_source_readback"] = audit(solver)
        apply_speed(solver, family, speed)
        receipt["source_readback"] = audit(solver, speed=speed)
        require(receipt["source_readback"]["methods"]["p_v_coupling"]["flow_scheme"] == "Coupled", "Recovery scheme changed")
        receipt["autosave_configuration"] = configure_autosave(solver, str(local), data_frequency=1000)
        definitions, report_paths = configure_reports(solver, local / "monitors")
        receipt["report_definitions"] = definitions
        receipt["report_paths"] = report_paths
        receipt["residual_configuration"] = configure_residual_history(solver, 2200)
        solver.settings.mesh.check()
        capture = SessionTranscriptCapture(solver, stream_path=local / "transcript.txt").start()
        receipt["start_pair"] = save_pair(solver, local / "active000")
        load_pair(solver, local / "active000")
        receipt["start_reopen_readback"] = audit(solver, speed=speed)
        check_reports(solver, definitions, report_paths)
        receipt["initial_report_compute"] = solver.settings.solution.report_definitions.compute(report_defs=list(definitions))
        require(len(receipt["initial_report_compute"]) == len(definitions), "Initial report computation incomplete")
        dump(manifest, receipt)
        for count, endpoint in ((50, 50), (950, 1000), (1000, 2000)):
            marker = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=count)
            capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10)
            block = capture.text_since(marker)
            rows = [int(value) for value in ITERATION_ROW.findall(block)]
            require(rows and rows[-1] == endpoint and set(range(endpoint-count+1, endpoint+1)).issubset(set(rows)),
                    f"Missing iteration rows at N{endpoint}: last={rows[-1] if rows else None}")
            require(not FAILURE_MARKER.search(block), "Fatal Fluent solver event")
            checkpoint = save_pair(solver, final / "final" if endpoint == 2000 else local / f"active{endpoint:04d}")
            receipt["checkpoints"].append({"active_iteration": endpoint, "transcript_unique_rows": len(set(rows)), **checkpoint})
            receipt["last_valid_active_iteration"] = endpoint
            dump(manifest, receipt)
            if endpoint == 1000:
                require(all(Path(path).stat().st_size > 0 for path in report_paths.values()), "Native reports not recording")
        load_pair(solver, final / "final")
        receipt["final_reopen_readback"] = audit(solver, speed=speed)
        check_reports(solver, definitions, report_paths)
        receipt["achieved_active_iterations"] = 2000
        receipt["report_file_bytes"] = {name: Path(path).stat().st_size for name, path in report_paths.items()}
        require(all(size > 0 for size in receipt["report_file_bytes"].values()), "Incomplete report files")
        receipt["status"] = "COMPLETE"
        dump(manifest, receipt)
        return {"manifest": str(manifest), "status": "COMPLETE", "final_pair": receipt["checkpoints"][-1]}
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        dump(manifest, receipt)
        raise
    finally:
        if capture is not None:
            capture.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=("F1", "F2"), default="F2")
    parser.add_argument("--speed", type=float, default=26.81)
    args = parser.parse_args()
    print(json.dumps(main(args.family, args.speed), indent=2), flush=True)
