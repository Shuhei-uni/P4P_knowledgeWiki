#!/usr/bin/env python3
"""Hold the finite setup-07m 0.1% inlet state for ten more time steps.

The 100-inner-iteration sensitivity reduced the final continuity residual to
about 0.027 but did not meet the strict 0.01 promotion threshold.  This branch
does not increase the flow.  It tests whether the residual and physical
closure settle or worsen across physical time at the same 0.1% input.
"""

from __future__ import annotations

import argparse
import json
import math
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

import prepare_setup07l_hydrostatic_rest as prepare07l  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07j_transient_vof_qualification as transient07j  # noqa: E402
import run_setup07l_hydrostatic_rest as rest07l  # noqa: E402
import run_setup07m_pressure_opening_campaign as campaign07m  # noqa: E402


LOCAL_ROOT = campaign07m.LOCAL_ROOT / "micro_inlet_hold_0p1pct_inner100"
SOURCE_ROOT = campaign07m.LOCAL_ROOT / "micro_inlet_ramp_dt1e-7_inner100"
DT_S = 1.0e-7
MAX_INNER = 100
TARGET_STEPS = 10
FRACTION = 0.001


def diagnostic_hold_gate(row: dict[str, Any], continuity: float) -> list[str]:
    failures = campaign07m.finite_failures(row)
    if not math.isfinite(continuity) or continuity > 0.1:
        failures.append(f"continuity residual is non-finite or above 0.1: {continuity}")
    if float(row["latest_global_courant"]) > campaign07m.MAX_VOF_COURANT:
        failures.append(f"Global Courant exceeds {campaign07m.MAX_VOF_COURANT}")
    if not -1.0e-6 <= float(row["domain_volume_avg_liquid_volume_fraction"]) <= 1.0 + 1.0e-6:
        failures.append("volume-averaged liquid fraction is unbounded")
    if abs(float(row["liquid_brineoutlet_kgs"])) > 0.25 * campaign07m.LIQUID_FEED_KG_S:
        failures.append(f"brine liquid flow exceeds 25% feed: {row['liquid_brineoutlet_kgs']}")
    if abs(float(row["vapor_brineoutlet_kgs"])) > 0.01 * campaign07m.VAPOR_FEED_KG_S:
        failures.append(f"brine vapor flow exceeds 1% feed: {row['vapor_brineoutlet_kgs']}")
    if float(row["domain_volume_avg_velocity_ms"]) > 1.0:
        failures.append(f"domain velocity exceeds 1 m/s: {row['domain_volume_avg_velocity_ms']}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)

    source = json.loads((SOURCE_ROOT / "ramp_manifest.json").read_text(encoding="utf-8"))
    checkpoint = source.get("checkpoints", {}).get("0.001")
    if not checkpoint:
        raise RuntimeError("finite 0.1%/inner100 checkpoint is unavailable")
    source_block = source.get("blocks", [])[-1]
    source_metrics = source_block.get("metrics", {})
    if source_metrics.get("latest_global_courant", 1.0) > campaign07m.MAX_VOF_COURANT:
        raise RuntimeError("source checkpoint failed the Courant gate")
    preparation = json.loads(
        (prepare07l.local_root_for_server(args.server_id) / "preparation_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    domain_volume = float(preparation["mesh_metrics"]["domain_volume_m3"])
    manifest_path = LOCAL_ROOT / "hold_manifest.json"
    result: dict[str, Any] = {
        "status": "running",
        "classification": "diagnostic / fixed 0.1% inlet hold",
        "controller_pid": os.getpid(),
        "source_checkpoint": checkpoint,
        "source_gate_failure": source.get("error"),
        "time_step_size_s": DT_S,
        "max_inner_iterations": MAX_INNER,
        "fixed_inlet_fraction": FRACTION,
        "target_steps": TARGET_STEPS,
        "blocks": [],
        "checkpoints": {},
        "started_epoch": time.time(),
    }
    campaign07m.write_json(manifest_path, result)

    solver = connect(server_id=args.server_id, start_transcript=True)
    transcript = ""
    try:
        result["live_parallel_runtime"] = require_live_compute_node_count(
            solver, prepare07l.EXPECTED_COMPUTE_NODES
        )
        solver.transcript.stop()
        solver.settings.file.read_case(file_name=checkpoint["case"])
        solver.settings.file.read_data(file_name=checkpoint["data"])
        transcript = campaign07m.start_case_transcript(
            solver, f"{campaign07m.RUN_LABEL}_micro_hold_0p1pct_inner100.trn"
        )
        campaign07m.open_brine_pressure_outlet(
            solver, campaign07m.BRINE_FACE_REST_PRESSURE_PA
        )
        campaign07m.MAX_ITERATIONS_PER_TIME_STEP = MAX_INNER
        campaign07m.set_time_step(solver, DT_S)
        result["inlet_readback"] = campaign07m.set_inlet_fraction(solver, FRACTION)
        result["dpm_readback"] = campaign07m.dpm_readback(solver)
        initial_clock = transient07j.runtime_clock(solver)
        result["initial_clock"] = initial_clock
        rows: list[dict[str, Any]] = []
        for step in range(1, TARGET_STEPS + 1):
            solver.settings.solution.run_calculation.dual_time_iterate(
                time_step_count=1, max_iter_per_step=MAX_INNER
            )
            clock = transient07j.runtime_clock(solver)
            if int(clock["time_step"]) != int(initial_clock["time_step"]) + step:
                raise RuntimeError(f"time-step proof failed: {clock}")
            expected_time = float(initial_clock["flow_time_s"]) + step * DT_S
            if not math.isclose(
                float(clock["flow_time_s"]), expected_time, rel_tol=0.0, abs_tol=1.0e-12
            ):
                raise RuntimeError(f"flow-time proof failed: {clock}")
            metrics = rest07l.physical_metrics(solver, step)
            metrics.update(rest07l.inventory(metrics, domain_volume))
            metrics.update(clock)
            transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
            courants = rest07l.parse_global_courant(transcript_text)
            residuals = campaign07m.residual_tail(solver)
            continuity = float(residuals[-1].get("continuity", math.nan)) if residuals else math.nan
            row = {
                **metrics,
                "hold_step": step,
                "latest_global_courant": courants[-1] if courants else math.nan,
                "max_global_courant": max(courants) if courants else math.nan,
                "final_continuity_residual": continuity,
            }
            failures = diagnostic_hold_gate(row, continuity)
            rows.append(row)
            if step in (1, 5, 10):
                result["checkpoints"][str(step)] = campaign07m.save_pair(
                    solver,
                    f"{campaign07m.RUN_LABEL}_micro_hold_0p1pct_inner100_step{step}",
                    f"07m_micro_hold_step{step}",
                )
            result["blocks"].append(
                {"step": step, "metrics": row, "gate_failures": failures}
            )
            result["steps_completed"] = step
            result["last_heartbeat_epoch"] = time.time()
            campaign07m.write_csv(LOCAL_ROOT / "physical_history.csv", rows)
            campaign07m.write_json(manifest_path, result)
            print(
                f"07m micro hold: step={step}/{TARGET_STEPS}; "
                f"continuity={continuity:.6g}; Co={row['latest_global_courant']:.6g}; "
                f"m_brine_l={row['liquid_brineoutlet_kgs']:.6g} kg/s",
                flush=True,
            )
            if failures:
                raise RuntimeError("micro-hold diagnostic gate failed: " + "; ".join(failures))
        transcript_text = campaign07m.stop_and_copy_transcript(
            solver, transcript, LOCAL_ROOT / "transcript.trn"
        )
        trend = [float(row["final_continuity_residual"]) for row in rows]
        result.update(
            {
                "status": "completed",
                "classification": "diagnostic / fixed 0.1% inlet hold completed",
                "continuity_history": trend,
                "continuity_improved_over_hold": trend[-1] < trend[0],
                "strict_0p01_gate_passed": trend[-1] <= 0.01,
                "dpm_tracking_evidence": rest07l.dpm_tracking_evidence(transcript_text),
                "completed_epoch": time.time(),
            }
        )
        campaign07m.write_json(manifest_path, result)
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
        campaign07m.write_json(manifest_path, result)
        raise
    finally:
        if transcript:
            try:
                campaign07m.stop_and_copy_transcript(
                    solver, transcript, LOCAL_ROOT / "transcript.trn"
                )
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
