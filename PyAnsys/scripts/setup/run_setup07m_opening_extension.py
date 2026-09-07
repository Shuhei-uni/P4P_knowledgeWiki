#!/usr/bin/env python3
"""Extend each safe setup-07m zero-feed opening case to ten 1e-5 s steps.

The one-step matrix remained bounded but did not yet resolve a directional
brine mass flux.  This controller independently reloads the low, centre, and
high opened-time-zero checkpoints and advances each for ten steps.  It does
not ramp the inlets unless a later campaign explicitly promotes a pressure.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections.abc import Mapping
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


RUN_LABEL = campaign07m.RUN_LABEL + "_extension10"
LOCAL_ROOT = campaign07m.LOCAL_ROOT / "opening_extension_10steps"
DT_S = 1.0e-5
TARGET_STEPS = 10


def write_manifest(path: Path, payload: Any) -> None:
    campaign07m.write_json(path, payload)


def source_opened_checkpoint(pressure_label: str) -> dict[str, str]:
    slug = campaign07m.case_slug(pressure_label, DT_S)
    path = campaign07m.LOCAL_ROOT / "matrix" / slug / "case_manifest.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("status") != "accepted":
        raise RuntimeError(f"one-step source was not accepted: {path}")
    checkpoint = result.get("pre_step_checkpoint")
    if not isinstance(checkpoint, Mapping) or not checkpoint.get("case"):
        raise RuntimeError(f"opened-time-zero checkpoint is missing: {path}")
    return dict(checkpoint)


def run_branch(
    solver: Any,
    pressure_label: str,
    pressure_pa: float,
    checkpoint: Mapping[str, str],
    domain_volume_m3: float,
) -> dict[str, Any]:
    branch_root = LOCAL_ROOT / pressure_label
    branch_root.mkdir(parents=True, exist_ok=True)
    solver.settings.file.read_case(file_name=checkpoint["case"])
    solver.settings.file.read_data(file_name=checkpoint["data"])
    transcript = campaign07m.start_case_transcript(
        solver, f"{RUN_LABEL}_{pressure_label}.trn"
    )
    manifest_path = branch_root / "extension_manifest.json"
    result: dict[str, Any] = {
        "status": "running",
        "classification": "diagnostic / zero-feed pressure-opening extension",
        "pressure_label": pressure_label,
        "pressure_pa": pressure_pa,
        "source_checkpoint": checkpoint,
        "time_step_size_s": DT_S,
        "target_steps": TARGET_STEPS,
        "controller_pid": os.getpid(),
        "checkpoints": {},
        "blocks": [],
        "started_epoch": time.time(),
    }
    write_manifest(manifest_path, result)
    rows: list[dict[str, Any]] = []
    try:
        campaign07m.open_brine_pressure_outlet(solver, pressure_pa)
        campaign07m.set_time_step(solver, DT_S)
        result["dpm_readback"] = campaign07m.dpm_readback(solver)
        initial_clock = transient07j.runtime_clock(solver)
        result["initial_clock"] = initial_clock
        for step in range(1, TARGET_STEPS + 1):
            solver.settings.solution.run_calculation.dual_time_iterate(
                time_step_count=1,
                max_iter_per_step=campaign07m.MAX_ITERATIONS_PER_TIME_STEP,
            )
            clock = transient07j.runtime_clock(solver)
            expected_step = int(initial_clock["time_step"]) + step
            expected_time = float(initial_clock["flow_time_s"]) + step * DT_S
            if int(clock["time_step"]) != expected_step or not math.isclose(
                float(clock["flow_time_s"]),
                expected_time,
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ):
                raise RuntimeError(f"clock proof failed at extension step {step}: {clock}")
            metrics = rest07l.physical_metrics(solver, step)
            metrics.update(rest07l.inventory(metrics, domain_volume_m3))
            metrics.update(clock)
            transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
            courant = rest07l.parse_global_courant(transcript_text)
            row = {
                **metrics,
                "extension_step": step,
                "pressure_label": pressure_label,
                "requested_brine_pressure_pa": pressure_pa,
                "latest_global_courant": courant[-1] if courant else math.nan,
                "max_global_courant": max(courant) if courant else math.nan,
                "max_reversed_flow_faces": max(
                    campaign07m.reversed_flow_counts(transcript_text), default=0
                ),
            }
            residuals = campaign07m.residual_tail(solver)
            failures = campaign07m.opening_gate(row, transcript_text, residuals)
            rows.append(row)
            if step in (1, 3, 10):
                saved = campaign07m.save_pair(
                    solver,
                    f"{RUN_LABEL}_{pressure_label}_step{step}",
                    f"07m_extension_{pressure_label}_step{step}",
                )
                result["checkpoints"][str(step)] = saved
            result["blocks"].append(
                {"step": step, "metrics": row, "gate_failures": failures}
            )
            result["steps_completed"] = step
            result["last_heartbeat_epoch"] = time.time()
            campaign07m.write_csv(branch_root / "physical_history.csv", rows)
            write_manifest(manifest_path, result)
            print(
                f"07m extension {pressure_label}: step={step}/{TARGET_STEPS}; "
                f"m_brine_l={row['liquid_brineoutlet_kgs']:.9g} kg/s; "
                f"Ubrine={row['brine_wall_area_weighted_velocity_ms']:.6g} m/s; "
                f"Co={row['latest_global_courant']:.6g}",
                flush=True,
            )
            if failures:
                raise RuntimeError("opening-extension gate failed: " + "; ".join(failures))
        text = campaign07m.stop_and_copy_transcript(
            solver, transcript, branch_root / "transcript.trn"
        )
        result.update(
            {
                "status": "completed",
                "classification": "diagnostic / bounded zero-feed opening extension",
                "completed_epoch": time.time(),
                "dpm_tracking_evidence": rest07l.dpm_tracking_evidence(text),
            }
        )
        write_manifest(manifest_path, result)
        return result
    except Exception as exc:
        result.update(
            {
                "status": "failed",
                "classification": "diagnostic / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_manifest(manifest_path, result)
        raise
    finally:
        try:
            campaign07m.stop_and_copy_transcript(
                solver, transcript, branch_root / "transcript.trn"
            )
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)

    preparation = json.loads(
        (prepare07l.local_root_for_server(args.server_id) / "preparation_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    domain_volume = float(preparation["mesh_metrics"]["domain_volume_m3"])
    manifest_path = LOCAL_ROOT / "extension_campaign_manifest.json"
    result: dict[str, Any] = {
        "status": "running",
        "classification": "diagnostic / independent opening extensions",
        "server_id": args.server_id,
        "controller_pid": os.getpid(),
        "time_step_size_s": DT_S,
        "target_steps_per_pressure": TARGET_STEPS,
        "branches": {},
        "started_epoch": time.time(),
    }
    write_manifest(manifest_path, result)
    solver = connect(server_id=args.server_id, start_transcript=True)
    try:
        result["live_parallel_runtime"] = require_live_compute_node_count(
            solver, prepare07l.EXPECTED_COMPUTE_NODES
        )
        solver.transcript.stop()
        for pressure_label, pressure_pa in campaign07m.PRESSURES:
            print(f"07m extension: starting {pressure_label}", flush=True)
            branch = run_branch(
                solver,
                pressure_label,
                pressure_pa,
                source_opened_checkpoint(pressure_label),
                domain_volume,
            )
            result["branches"][pressure_label] = branch
            result["last_heartbeat_epoch"] = time.time()
            write_manifest(manifest_path, result)

        finals = {
            label: float(branch["blocks"][-1]["metrics"]["liquid_brineoutlet_kgs"])
            for label, branch in result["branches"].items()
        }
        directional = finals["low"] < finals["center"] < finals["high"]
        sign_bracket = finals["low"] < 0.0 < finals["high"]
        centre_quiet = abs(finals["center"]) <= 0.01 * campaign07m.LIQUID_FEED_KG_S
        result.update(
            {
                "status": "completed",
                "classification": "diagnostic / opening-extension assessment",
                "final_liquid_brine_flows_kg_s": finals,
                "directional_monotonic_response": directional,
                "endpoint_sign_bracket": sign_bracket,
                "centre_quiet_within_1pct_feed": centre_quiet,
                "ramp_eligible": directional and sign_bracket and centre_quiet,
                "completed_epoch": time.time(),
            }
        )
        write_manifest(manifest_path, result)
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
        write_manifest(manifest_path, result)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
