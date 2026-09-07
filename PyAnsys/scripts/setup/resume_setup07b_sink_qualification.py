#!/usr/bin/env python3
"""Resume the active setup-07b qualification from Fluent's live recorded state."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Mapping

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import classify_failure  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import run_setup07b_sink_qualification as qualify  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402
import verify_constant_water_level_sink as verify07b  # noqa: E402


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--block", type=int, default=250)
    result.add_argument("--minimum-r1-iterations", type=int, default=2500)
    result.add_argument("--maximum-r1-iterations", type=int, default=6000)
    result.add_argument("--checkpoint-interval", type=int, default=1000)
    result.add_argument("--stable-windows-required", type=int, default=2)
    result.add_argument("--residual-limit", type=float, default=1.0e-3)
    return result


def convert(value: str) -> Any:
    if value == "":
        return ""
    try:
        return float(value)
    except ValueError:
        return value


def read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as stream:
        return [
            {str(key): convert(str(value)) for key, value in row.items()}
            for row in csv.DictReader(stream)
        ]


def merge_residual_rows(
    old: list[dict[str, Any]], new: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    merged = {float(row["iteration"]): row for row in old}
    merged.update({float(row["iteration"]): row for row in new})
    return [merged[key] for key in sorted(merged)]


def persist(
    manifest: Mapping[str, Any],
    physical_rows: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
) -> None:
    qualify.persist(manifest, physical_rows, residual_rows)


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    manifest_path = qualify.LOCAL_DIR / "qualification_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cumulative = int(manifest.get("cumulative_iterations_completed", 0))
    r1_completed = int(manifest.get("r1_iterations_completed", 0))
    if cumulative <= 0 or r1_completed <= 0:
        raise RuntimeError(
            f"live resume requires a recorded full-strength block: {manifest}"
        )
    if manifest.get("status") == "completed":
        print("Qualification is already completed; no resume performed.")
        return 0

    physical_rows = read_csv(qualify.LOCAL_DIR / "physical_monitor_history.csv")
    residual_rows = read_csv(qualify.LOCAL_DIR / "residual_history.csv")
    solver = connect(server_id=args.server_id)
    stable_windows = 0
    resume_event: dict[str, Any] = {
        "started_epoch": time.time(),
        "recorded_cumulative_iteration": cumulative,
        "recorded_r1_iteration": r1_completed,
        "mode": "live-state recovery",
    }
    manifest.setdefault("resume_events", []).append(resume_event)
    try:
        mesh_metrics, _ = mesh_study.collect_mesh_reports(solver)
        if int(mesh_metrics.get("cells", -1)) != qualify.EXPECTED_CELLS:
            raise RuntimeError(f"live recovery mesh mismatch: {mesh_metrics}")
        settings = mesh_study.capture_settings(solver, qualify.REMOTE_DIR)
        settings.update(
            mesh_study.verify_initialized_phase_identity(solver, qualify.REMOTE_DIR)
        )
        errors = mesh_study.validate_settings(
            settings, mesh_metrics, require_phase_identity=True
        )
        sources = verify07b.source_readback(solver)
        errors.extend(
            verify07b.validate_source_readback(
                sources, library=qualify.EXPECTED_LIBRARY
            )
        )
        parameters = verify07b.rp_readback(solver)
        if not math.isclose(
            float(parameters["user/cwl07b/tau-s"]),
            float(manifest["tau_s"]),
            abs_tol=1.0e-12,
        ):
            errors.append(f"live tau mismatch: {parameters}")
        if not math.isclose(
            float(parameters["user/cwl07b/ramp"]), 1.0, abs_tol=1.0e-12
        ):
            errors.append(f"live ramp is not full strength: {parameters}")
        if bool(solver.scheme.eval("(sg-dpm?)")):
            errors.append("DPM model unexpectedly active")
        if errors:
            raise RuntimeError("live recovery preflight failed: " + "; ".join(errors))

        fields = qualify.available_fields(solver)
        mask_field = verify07b.find_field(
            fields, "cwl07b-bottom-adjacent-mask", "udm-0"
        )
        mass_source_field = verify07b.find_field(
            fields, "cwl07b-liquid-mass-source-kgm3s", "udm-1"
        )
        liquid_density = float(settings["phase_densities_kg_m3"]["phase-2"])

        recovery_key = f"live_recovery_{cumulative}"
        if recovery_key not in manifest["checkpoints"]:
            recovery_label = (
                f"recovery_live_cumulative{cumulative}_r1_{r1_completed}_r1p0"
            )
            manifest["checkpoints"][recovery_key] = setup07b.save_pair(
                solver, qualify.REMOTE_DIR, recovery_label
            )
        resume_event["recovery_checkpoint"] = manifest["checkpoints"][recovery_key]
        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.set_verified_iteration_label(solver, cumulative)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()
        manifest.update(
            {
                "status": "running",
                "classification": "diagnostic qualification resumed",
                "controller_state": "supervised recovery controller active",
            }
        )
        persist(manifest, physical_rows, residual_rows)

        while r1_completed < args.maximum_r1_iterations:
            requested = min(args.block, args.maximum_r1_iterations - r1_completed)
            before = sweep.monitor_iteration_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=requested)
            after = sweep.require_monitor_advance(solver, before, requested, 60.0)
            cumulative += requested
            r1_completed += requested
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
            physical_rows.append(
                qualify.collect_metrics(
                    solver,
                    cumulative_iteration=cumulative,
                    r1_iteration=r1_completed,
                    stage="ramp_1.00_resume",
                    ramp=1.0,
                    tau_s=float(manifest["tau_s"]),
                    liquid_density=liquid_density,
                    mask_field=mask_field,
                    mass_source_field=mass_source_field,
                )
            )
            residual_rows = merge_residual_rows(
                residual_rows, sweep.monitor_history_rows(solver)
            )
            window = qualify.qualification_window(
                physical_rows, residual_rows, args.residual_limit
            )
            manifest.update(
                {
                    "cumulative_iterations_completed": cumulative,
                    "r1_iterations_completed": r1_completed,
                    "latest_metrics": physical_rows[-1],
                    "latest_500_iteration_assessment": window,
                }
            )
            if r1_completed % args.checkpoint_interval == 0:
                manifest["checkpoints"][f"r1_{r1_completed}"] = setup07b.save_pair(
                    solver,
                    qualify.REMOTE_DIR,
                    f"r1_iter{r1_completed}_cumulative{cumulative}",
                )
            persist(manifest, physical_rows, residual_rows)
            print(
                f"07b resumed: R=1 {r1_completed}/{args.maximum_r1_iterations}, "
                f"sink={physical_rows[-1]['integrated_liquid_sink_kgs']:.6g} kg/s, "
                f"continuity={residual_rows[-1].get('continuity')}, "
                f"balance={physical_rows[-1]['liquid_source_augmented_imbalance_percent']:.4g}%, "
                f"window-pass={window['acceptance_window_pass']}",
                flush=True,
            )
            if r1_completed >= args.minimum_r1_iterations:
                stable_windows = (
                    stable_windows + 1 if window["acceptance_window_pass"] else 0
                )
                if stable_windows >= args.stable_windows_required:
                    break

        qualify.set_rp_real(solver, "user/cwl07b/ramp", 0.0)
        final_label = (
            f"accepted_stop_r1_{r1_completed}_ramp_reset0"
            if stable_windows >= args.stable_windows_required
            else f"max_r1_{r1_completed}_unresolved_ramp_reset0"
        )
        manifest["checkpoints"]["final"] = setup07b.save_pair(
            solver, qualify.REMOTE_DIR, final_label
        )
        resume_event["completed_epoch"] = time.time()
        manifest.update(
            {
                "status": "completed",
                "classification": (
                    "accepted tau=0.1 qualification"
                    if stable_windows >= args.stable_windows_required
                    else "unresolved at maximum R=1 iteration budget"
                ),
                "stable_windows_observed": stable_windows,
                "ramp_after_run": 0.0,
                "controller_state": "completed",
                "completed_epoch": time.time(),
            }
        )
        persist(manifest, physical_rows, residual_rows)
        return 0 if stable_windows >= args.stable_windows_required else 2
    except BaseException as exc:
        resume_event.update(
            {
                "completed_epoch": time.time(),
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        manifest.update(
            {
                "status": "failed",
                "classification": "unresolved qualification interruption",
                "failure_category": classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "controller_state": "failed",
                "completed_epoch": time.time(),
            }
        )
        try:
            qualify.set_rp_real(solver, "user/cwl07b/ramp", 0.0)
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
        persist(manifest, physical_rows, residual_rows)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
