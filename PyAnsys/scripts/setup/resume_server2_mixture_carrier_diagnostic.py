#!/usr/bin/env python3
"""Resume the server-2 carrier diagnostic from its clean initialized checkpoint."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import require_live_compute_node_count  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_server2_mixture_carrier_diagnostic as base  # noqa: E402
import run_setup07g_brine_outlet_qualification as qualify07g  # noqa: E402
import run_setup07m_pressure_opening_campaign as campaign07m  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


RUN_LABEL = "server2_mixture_carrier_extension_20260821_resume1"
LOCAL_ROOT = PROJECT_ROOT / "output" / base.STUDY_ID / RUN_LABEL
MANIFEST = LOCAL_ROOT / "diagnostic_manifest.json"
REMOTE_DIR = r"C:\Users\qtra338\Documents"
SOURCE_STEM = REMOTE_DIR + r"\server2_mixture_carrier_extension_20260821_v1_initialized_pool"
REMOTE_PREFIX = REMOTE_DIR + "\\" + RUN_LABEL
BLOCK = 50
BLOCKS = 5


def write_json(payload: dict[str, Any]) -> None:
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    result: dict[str, Any] = {
        "run_label": RUN_LABEL,
        "server_id": "2",
        "status": "running",
        "classification": "diagnostic / resumed from clean initialized checkpoint",
        "controller_pid": os.getpid(),
        "source_checkpoint": {
            "case": SOURCE_STEM + ".cas.h5",
            "data": SOURCE_STEM + ".dat.h5",
        },
        "target_iterations": BLOCK * BLOCKS,
        "credited_iterations": 0,
        "blocks": [],
        "checkpoints": {},
        "started_epoch": time.time(),
    }
    write_json(result)
    solver = connect(server_id="2", start_transcript=True)
    transcript = REMOTE_PREFIX + ".trn"
    try:
        result["live_parallel_runtime"] = require_live_compute_node_count(solver, 16)
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.read_case(file_name=result["source_checkpoint"]["case"])
        solver.settings.file.read_data(file_name=result["source_checkpoint"]["data"])
        state = base.selected_setup_readback(solver)
        base.validate_live_case(state)
        if state["dpm_injection_names"]:
            raise RuntimeError(f"source checkpoint contains DPM injections: {state['dpm_injection_names']}")
        pressure = state["boundary_conditions"]["pressure_outlet"]["brineoutlet"]["phase"][
            "mixture"
        ]["momentum"]["gauge_pressure"]["value"]
        if abs(float(pressure) - campaign07m.BRINE_FACE_REST_PRESSURE_PA) > 1.0e-6:
            raise RuntimeError(f"source brine-pressure mismatch: {pressure}")
        result["source_readback"] = state
        solver.settings.file.start_transcript(file_name=transcript)
        qualify07g.REMOTE_ROOT = REMOTE_DIR
        for block_index in range(1, BLOCKS + 1):
            before = mesh_study.monitor_snapshot(solver)
            before_points = mesh_study.monitor_point_count(before)
            solver.settings.solution.run_calculation.iterate(iter_count=BLOCK)
            after = mesh_study.monitor_snapshot(solver)
            advance = mesh_study.monitor_point_count(after) - before_points
            if advance < BLOCK:
                raise RuntimeError(f"iteration proof failed: requested={BLOCK}, advance={advance}")
            credited = block_index * BLOCK
            row = qualify07g.physical_metrics(solver, credited)
            row["credited_iterations"] = credited
            row["residual_tail"] = campaign07m.residual_tail(solver, count=5)
            failures = base.finite_failures(row)
            result["blocks"].append({"metrics": row, "gate_failures": failures})
            result["credited_iterations"] = credited
            result["last_heartbeat_epoch"] = time.time()
            if credited in (50, 100, 250):
                result["checkpoints"][str(credited)] = base.save_checkpoint(
                    solver, f"{REMOTE_PREFIX}_iter{credited}"
                )
            write_json(result)
            print(
                f"server2 carrier resume: {credited}/{BLOCK * BLOCKS}; "
                f"mix_net={row['mixture_net_kgs']:.6g} kg/s; "
                f"brine_l={row['liquid_brineoutlet_kgs']:.6g} kg/s",
                flush=True,
            )
            if failures:
                raise RuntimeError("server-2 physics gate failed: " + "; ".join(failures))
        solver.settings.file.stop_transcript()
        text = sweep.remote_text_read_best_effort(solver, transcript)
        LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
        (LOCAL_ROOT / "transcript.trn").write_text(text, encoding="utf-8")
        result.update(
            {
                "status": "completed",
                "classification": "diagnostic / carrier-only Mixture extension completed",
                "dpm_tracking_text_detected": "Advancing DPM injections" in text,
                "completed_epoch": time.time(),
            }
        )
        write_json(result)
        return 0
    except (Exception, KeyboardInterrupt) as exc:
        result.update(
            {
                "status": "failed",
                "classification": "diagnostic / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(result)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
