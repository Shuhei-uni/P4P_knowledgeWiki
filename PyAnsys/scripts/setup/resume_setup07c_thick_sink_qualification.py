#!/usr/bin/env python3
"""Resume setup-07c after a separately preserved diagnostic checkpoint."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import classify_failure  # noqa: E402

import resume_setup07b_sink_qualification as resume07b  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07c_thick_sink_qualification as qualify  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402
import setup07c_thick_water_level_sink as setup07c  # noqa: E402


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--block", type=int, default=250)
    result.add_argument("--minimum-r1-iterations", type=int, default=1000)
    result.add_argument("--maximum-r1-iterations", type=int, default=2000)
    result.add_argument("--checkpoint-interval", type=int, default=1000)
    result.add_argument("--stable-windows-required", type=int, default=2)
    result.add_argument("--residual-limit", type=float, default=1.0e-3)
    return result


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    manifest_path = qualify.LOCAL_DIR / "qualification_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cumulative = int(manifest.get("cumulative_iterations_completed", 0))
    r1_completed = int(manifest.get("r1_iterations_completed", 0))
    if cumulative <= 0 or r1_completed <= 0:
        raise RuntimeError("07c resume requires at least one recorded R=1 block")
    if r1_completed >= args.maximum_r1_iterations:
        print("07c already reached the full-strength iteration budget.", flush=True)
        return 0

    physical_rows = resume07b.read_csv(
        qualify.LOCAL_DIR / "physical_monitor_history.csv"
    )
    residual_rows = resume07b.read_csv(qualify.LOCAL_DIR / "residual_history.csv")
    solver = connect(server_id=args.server_id)
    stable_windows = int(manifest.get("stable_windows_observed", 0))
    event: dict[str, Any] = {
        "started_epoch": time.time(),
        "recorded_cumulative_iteration": cumulative,
        "recorded_r1_iteration": r1_completed,
        "mode": "07c saved-state recovery after startup-change guard correction",
    }
    manifest.setdefault("resume_events", []).append(event)
    transcript = setup07b.remote_join(
        qualify.REMOTE_DIR, f"qualification_resume_from_r1_{r1_completed}.trn"
    )

    try:
        # Preserve and explicitly restore the stopped state.  The original
        # clean-start, ramp, and first diagnostic files remain untouched.
        stopped_pair = manifest["checkpoints"]["final"]
        setup07b.restore_pair(solver, stopped_pair)
        mesh_metrics, _ = mesh_study.collect_mesh_reports(solver)
        if int(mesh_metrics.get("cells", -1)) != qualify.EXPECTED_CELLS:
            raise RuntimeError(f"07c recovery mesh mismatch: {mesh_metrics}")

        settings = mesh_study.capture_settings(solver, qualify.REMOTE_DIR)
        settings.update(
            mesh_study.verify_initialized_phase_identity(solver, qualify.REMOTE_DIR)
        )
        errors = mesh_study.validate_settings(
            settings, mesh_metrics, require_phase_identity=True
        )
        library = str(manifest["udf_deployment"]["library_name"])
        errors.extend(
            setup07c.validate_source_readback(
                setup07c.source_readback(solver), library=library
            )
        )
        parameters = setup07c.rp_readback(solver)
        if not math.isclose(
            float(parameters["user/cwl07c/tau-s"]),
            float(manifest["tau_s"]),
            abs_tol=1.0e-12,
        ):
            errors.append(f"live tau mismatch: {parameters}")
        if not math.isclose(
            float(parameters["user/cwl07c/layer-thickness-m"]),
            float(manifest["layer_thickness_m"]),
            rel_tol=1.0e-12,
        ):
            errors.append(f"live thickness mismatch: {parameters}")
        if not math.isclose(
            float(parameters["user/cwl07c/ramp"]), 0.0, abs_tol=1.0e-12
        ):
            errors.append(f"stopped recovery ramp is not zero: {parameters}")
        if bool(solver.scheme.eval("(sg-dpm?)")):
            errors.append("DPM model unexpectedly active")
        if errors:
            raise RuntimeError("07c recovery preflight failed: " + "; ".join(errors))

        mask_field, source_field, _ = qualify.latest_fields(solver)
        liquid_phase = str(manifest["geometry_readback"]["liquid_phase"])
        liquid_density = float(settings["phase_densities_kg_m3"][liquid_phase])
        recovery_key = f"resume_start_r1_{r1_completed}_ramp0"
        if recovery_key not in manifest["checkpoints"]:
            manifest["checkpoints"][recovery_key] = setup07b.save_pair(
                solver,
                qualify.REMOTE_DIR,
                f"resume_start_r1_{r1_completed}_cumulative{cumulative}_ramp0",
            )
        event["recovery_checkpoint"] = manifest["checkpoints"][recovery_key]

        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.set_verified_iteration_label(solver, cumulative)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()
        setup07c.set_rp_real(solver, "user/cwl07c/ramp", 1.0)
        if not math.isclose(
            float(setup07c.rp_readback(solver)["user/cwl07c/ramp"]),
            1.0,
            abs_tol=1.0e-12,
        ):
            raise RuntimeError("full-strength ramp readback failed")

        manifest.update(
            {
                "status": "running",
                "classification": "diagnostic 07c qualification resumed",
                "controller_state": "single recovery controller active",
                "resume_transcript": transcript,
                "stop_reason": "",
            }
        )
        qualify.persist(manifest, physical_rows, residual_rows)

        stop_reason = ""
        while r1_completed < args.maximum_r1_iterations:
            requested = min(args.block, args.maximum_r1_iterations - r1_completed)
            before = sweep.monitor_iteration_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=requested)
            after = sweep.require_monitor_advance(solver, before, requested, 60.0)
            cumulative += requested
            r1_completed += requested
            row = qualify.qualify07b.collect_metrics(
                solver,
                cumulative_iteration=cumulative,
                r1_iteration=r1_completed,
                stage="ramp_1.00_resume",
                ramp=1.0,
                tau_s=float(manifest["tau_s"]),
                liquid_density=liquid_density,
                mask_field=mask_field,
                mass_source_field=source_field,
            )
            physical_rows.append(row)
            residual_rows = resume07b.merge_residual_rows(
                residual_rows, sweep.monitor_history_rows(solver)
            )
            window = qualify.qualify07b.qualification_window(
                physical_rows, residual_rows, args.residual_limit
            )
            manifest["iteration_evidence"].append(
                {
                    "stage": "ramp_1.00_resume",
                    "ramp": 1.0,
                    "requested": requested,
                    "cumulative_iteration": cumulative,
                    "r1_iteration": r1_completed,
                    "before": before,
                    "after": after,
                }
            )
            manifest.update(
                {
                    "cumulative_iterations_completed": cumulative,
                    "r1_iterations_completed": r1_completed,
                    "latest_metrics": row,
                    "latest_500_iteration_assessment": window,
                }
            )

            r1_rows = [
                item
                for item in physical_rows
                if int(item.get("r1_iteration", 0)) > 0
            ]
            if len(r1_rows) >= 2:
                jumps = qualify.abrupt_change(r1_rows[-2], r1_rows[-1])
                manifest["latest_block_change_percent"] = jumps
                manifest.setdefault("block_change_history", []).append(
                    {"r1_iteration": r1_completed, **jumps}
                )
                if r1_completed >= 750 and jumps["pressure_drop_pa"] > 20.0:
                    stop_reason = f"abrupt >20% pressure-drop block change: {jumps}"
            values = (
                row["pressure_drop_pa"],
                row["domain_liquid_inventory_kg"],
                row["sink_magnitude_kgs"],
            )
            if not all(math.isfinite(float(value)) for value in values):
                stop_reason = "non-finite pressure, inventory, or sink metric"
            if row["sink_magnitude_kgs"] > 175.0:
                stop_reason = "sink exceeded the guarded 175 kg/s limit"

            if r1_completed % args.checkpoint_interval == 0:
                manifest["checkpoints"][f"r1_{r1_completed}"] = setup07b.save_pair(
                    solver,
                    qualify.REMOTE_DIR,
                    f"r1_iter{r1_completed}_cumulative{cumulative}_resume",
                )
            if r1_completed >= args.minimum_r1_iterations:
                stable_windows = (
                    stable_windows + 1 if window["acceptance_window_pass"] else 0
                )
            manifest["stable_windows_observed"] = stable_windows
            qualify.persist(manifest, physical_rows, residual_rows)
            print(
                f"07c resumed R=1 {r1_completed}/{args.maximum_r1_iterations} "
                f"sink={row['sink_magnitude_kgs']:.6g} kg/s "
                f"inventory={row['domain_liquid_inventory_kg']:.6g} kg "
                f"balance={row['liquid_source_augmented_imbalance_percent']:.4g}% "
                f"window-pass={window['acceptance_window_pass']}",
                flush=True,
            )
            if stop_reason or stable_windows >= args.stable_windows_required:
                break

        setup07c.set_rp_real(solver, "user/cwl07c/ramp", 0.0)
        accepted = stable_windows >= args.stable_windows_required
        label = (
            f"accepted_resume_r1_{r1_completed}_ramp_reset0"
            if accepted
            else f"diagnostic_resume_r1_{r1_completed}_ramp_reset0"
        )
        manifest["checkpoints"]["resume_final"] = setup07b.save_pair(
            solver, qualify.REMOTE_DIR, label
        )
        event["completed_epoch"] = time.time()
        manifest.update(
            {
                "status": "completed",
                "classification": (
                    "accepted 07c thick-sink diagnostic"
                    if accepted
                    else "diagnostic/unresolved thick-sink result"
                ),
                "stable_windows_observed": stable_windows,
                "stop_reason": stop_reason or "maximum iteration budget reached",
                "ramp_after_run": 0.0,
                "dpm_after_run": bool(solver.scheme.eval("(sg-dpm?)")),
                "controller_state": "completed",
                "completed_epoch": time.time(),
            }
        )
        qualify.persist(manifest, physical_rows, residual_rows)
        return 0
    except BaseException as exc:
        event.update(
            {"completed_epoch": time.time(), "error": f"{type(exc).__name__}: {exc}"}
        )
        manifest.update(
            {
                "status": "failed",
                "classification": "unresolved 07c recovery interruption",
                "failure_category": classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "controller_state": "failed",
                "completed_epoch": time.time(),
            }
        )
        try:
            setup07c.set_rp_real(solver, "user/cwl07c/ramp", 0.0)
            manifest["checkpoints"]["resume_failure_ramp_reset0"] = (
                setup07b.save_pair(
                    solver,
                    qualify.REMOTE_DIR,
                    f"resume_failure_ramp_reset0_{int(time.time())}",
                )
            )
        except Exception as save_exc:
            manifest["failure_checkpoint_error"] = (
                f"{type(save_exc).__name__}: {save_exc}"
            )
        qualify.persist(manifest, physical_rows, residual_rows)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
