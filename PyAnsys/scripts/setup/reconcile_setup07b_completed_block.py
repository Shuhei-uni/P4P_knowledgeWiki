#!/usr/bin/env python3
"""Reconcile one Fluent-completed setup-07b block after a controller disconnect.

This script is intentionally narrow.  It is for the 2026-08-07 qualification
recovery where Fluent completed the requested 250-iteration block, but the
Python controller lost its response before recording metrics or writing the
R1=3000 checkpoint.  It does not iterate and it does not change model settings.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))

from pyansys_fluent.connection import connect  # noqa: E402

import resume_setup07b_sink_qualification as resume07b  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import run_setup07b_sink_qualification as qualify  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402
import verify_constant_water_level_sink as verify07b  # noqa: E402


EXPECTED_CUMULATIVE_BEFORE = 3250
EXPECTED_R1_BEFORE = 2750
RECOVERED_BLOCK = 250
EXPECTED_CUMULATIVE_AFTER = 3500
EXPECTED_R1_AFTER = 3000


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    manifest_path = qualify.LOCAL_DIR / "qualification_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cumulative_before = int(manifest["cumulative_iterations_completed"])
    r1_before = int(manifest["r1_iterations_completed"])

    if (cumulative_before, r1_before) == (
        EXPECTED_CUMULATIVE_AFTER,
        EXPECTED_R1_AFTER,
    ):
        print("The disconnected block is already reconciled; no changes made.")
        return 0
    if (cumulative_before, r1_before) != (
        EXPECTED_CUMULATIVE_BEFORE,
        EXPECTED_R1_BEFORE,
    ):
        raise RuntimeError(
            "unexpected manifest position: "
            f"cumulative={cumulative_before}, R1={r1_before}"
        )
    recovery_key = f"live_recovery_{EXPECTED_CUMULATIVE_BEFORE}"
    if recovery_key not in manifest.get("checkpoints", {}):
        raise RuntimeError(f"required separate recovery checkpoint is missing: {recovery_key}")

    solver = connect(server_id="1")
    mesh_metrics, _ = mesh_study.collect_mesh_reports(solver)
    errors: list[str] = []
    if int(mesh_metrics.get("cells", -1)) != qualify.EXPECTED_CELLS:
        errors.append(f"mesh mismatch: {mesh_metrics}")

    settings = mesh_study.capture_settings(solver, qualify.REMOTE_DIR)
    settings.update(
        mesh_study.verify_initialized_phase_identity(solver, qualify.REMOTE_DIR)
    )
    errors.extend(
        mesh_study.validate_settings(settings, mesh_metrics, require_phase_identity=True)
    )
    sources = verify07b.source_readback(solver)
    errors.extend(
        verify07b.validate_source_readback(sources, library=qualify.EXPECTED_LIBRARY)
    )
    parameters = verify07b.rp_readback(solver)
    if not math.isclose(
        float(parameters["user/cwl07b/tau-s"]),
        float(manifest["tau_s"]),
        abs_tol=1.0e-12,
    ):
        errors.append(f"tau mismatch: {parameters}")
    if not math.isclose(
        float(parameters["user/cwl07b/ramp"]), 1.0, abs_tol=1.0e-12
    ):
        errors.append(f"ramp mismatch: {parameters}")
    if bool(solver.scheme.eval("(sg-dpm?)")):
        errors.append("DPM model unexpectedly active")
    if errors:
        raise RuntimeError("reconciliation preflight failed: " + "; ".join(errors))

    fields = qualify.available_fields(solver)
    mask_field = verify07b.find_field(
        fields, "cwl07b-bottom-adjacent-mask", "udm-0"
    )
    mass_source_field = verify07b.find_field(
        fields, "cwl07b-liquid-mass-source-kgm3s", "udm-1"
    )
    liquid_density = float(settings["phase_densities_kg_m3"]["phase-2"])
    metrics = qualify.collect_metrics(
        solver,
        cumulative_iteration=EXPECTED_CUMULATIVE_AFTER,
        r1_iteration=EXPECTED_R1_AFTER,
        stage="ramp_1.00_reconciled_disconnect",
        ramp=1.0,
        tau_s=float(manifest["tau_s"]),
        liquid_density=liquid_density,
        mask_field=mask_field,
        mass_source_field=mass_source_field,
    )

    physical_rows = resume07b.read_csv(
        qualify.LOCAL_DIR / "physical_monitor_history.csv"
    )
    if any(int(float(row["r1_iteration"])) == EXPECTED_R1_AFTER for row in physical_rows):
        raise RuntimeError("an R1=3000 physical-monitor row already exists")
    physical_rows.append(metrics)
    residual_rows = resume07b.read_csv(qualify.LOCAL_DIR / "residual_history.csv")
    window = qualify.qualification_window(
        physical_rows, residual_rows, float(manifest.get("residual_limit", 1.0e-3))
    )
    window.update(
        {
            "acceptance_window_pass": False,
            "recovery_residual_gap": True,
            "recovery_note": (
                "The disconnected block completed in Fluent, but residual samples "
                "after the last locally received console line were unavailable. "
                "This window is diagnostic and cannot count toward acceptance."
            ),
        }
    )

    checkpoint_key = f"r1_{EXPECTED_R1_AFTER}"
    if checkpoint_key in manifest.get("checkpoints", {}):
        raise RuntimeError(f"refusing to overwrite existing checkpoint: {checkpoint_key}")
    checkpoint = setup07b.save_pair(
        solver,
        qualify.REMOTE_DIR,
        f"r1_iter{EXPECTED_R1_AFTER}_cumulative{EXPECTED_CUMULATIVE_AFTER}",
    )
    manifest.setdefault("checkpoints", {})[checkpoint_key] = checkpoint
    manifest.setdefault("iteration_evidence", []).append(
        {
            "stage": "ramp_1.00_reconciled_disconnect",
            "ramp": 1.0,
            "requested": RECOVERED_BLOCK,
            "cumulative_iteration": EXPECTED_CUMULATIVE_AFTER,
            "r1_iteration": EXPECTED_R1_AFTER,
            "evidence": {
                "last_console_iteration_received": 3719,
                "remaining_iterations_at_last_console_line": 31,
                "live_bottom_layer_liquid_inventory_kg": metrics[
                    "bottom_layer_liquid_inventory_kg"
                ],
                "separate_recovery_checkpoint": manifest["checkpoints"][recovery_key],
                "interpretation": (
                    "Fluent completed the outstanding command after the controller "
                    "connection stalled; the completed field was recovered separately."
                ),
            },
        }
    )
    manifest.setdefault("resume_events", []).append(
        {
            "started_epoch": time.time(),
            "completed_epoch": time.time(),
            "mode": "completed-block reconciliation",
            "recorded_cumulative_before": EXPECTED_CUMULATIVE_BEFORE,
            "recorded_r1_before": EXPECTED_R1_BEFORE,
            "recorded_cumulative_after": EXPECTED_CUMULATIVE_AFTER,
            "recorded_r1_after": EXPECTED_R1_AFTER,
            "residual_history_complete": False,
        }
    )
    manifest.update(
        {
            "status": "paused",
            "classification": "diagnostic qualification reconciled; ready to resume",
            "controller_state": "paused after completed-block reconciliation",
            "cumulative_iterations_completed": EXPECTED_CUMULATIVE_AFTER,
            "r1_iterations_completed": EXPECTED_R1_AFTER,
            "latest_metrics": metrics,
            "latest_500_iteration_assessment": window,
            "pause_reason": (
                "Controller connection failed during the R1=2750 to R1=3000 block. "
                "The completed live field was saved separately and reconciled."
            ),
            "last_update_epoch": time.time(),
        }
    )
    qualify.persist(manifest, physical_rows, residual_rows)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "cumulative_iterations_completed": EXPECTED_CUMULATIVE_AFTER,
                "r1_iterations_completed": EXPECTED_R1_AFTER,
                "checkpoint": checkpoint,
                "latest_metrics": metrics,
                "acceptance_window_pass": False,
                "residual_history_complete": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
