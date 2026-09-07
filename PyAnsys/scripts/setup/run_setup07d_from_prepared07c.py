#!/usr/bin/env python3
"""Run setup 07d from setup 07c's verified clean prepared checkpoint."""

from __future__ import annotations

import argparse
import copy
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
from pyansys_fluent.constant_water_level_sink import (  # noqa: E402
    adaptive_tau_from_inventory,
)
from pyansys_fluent.dependency_workflow import classify_failure  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07b_sink_qualification as qualify07b  # noqa: E402
import run_setup07c_thick_sink_qualification as qualify07c  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402
import setup07c_thick_water_level_sink as setup07c  # noqa: E402


STUDY_ID = "split_inlet_strong_sink_sensitivity_20260810"
RUN_LABEL = "mesh-900k_band0p140165_tau0p020_v1"
LOCAL_DIR = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
REMOTE_DIR = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}\{RUN_LABEL}"
PARENT_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_thickened_water_level_sink_20260808"
    / "mesh-900k_band0p140165_tau0p100_v1"
)
TAU_S = 0.02
THICKNESS_M = 0.14016525361822468
PARENT_THICKNESS_M = 0.14016525361822468
MAXIMUM_R1 = 2000
MINIMUM_R1 = 1000
BLOCK = 250
RESIDUAL_LIMIT = 1.0e-3
STABLE_WINDOWS_REQUIRED = 2
SINK_GUARD_KGS = 175.0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--study-id", default=STUDY_ID)
    result.add_argument("--run-label", default=RUN_LABEL)
    result.add_argument(
        "--setup-branch",
        default="07d capacity-matched thick-sink strength diagnostic",
    )
    result.add_argument("--initial-tau-s", type=float, default=TAU_S)
    result.add_argument(
        "--layer-thickness-m",
        type=float,
        default=THICKNESS_M,
        help="Bottom-local sink-band height. Read back from Fluent before initialization.",
    )
    result.add_argument("--maximum-r1-iterations", type=int, default=MAXIMUM_R1)
    result.add_argument("--minimum-r1-iterations", type=int, default=MINIMUM_R1)
    result.add_argument("--block", type=int, default=BLOCK)
    result.add_argument("--adaptive-target-kgs", type=float, default=0.0)
    result.add_argument("--feedback-block", type=int, default=100)
    result.add_argument("--tau-min-s", type=float, default=0.002)
    result.add_argument("--tau-max-s", type=float, default=0.2)
    result.add_argument(
        "--static-mask-schedule",
        action="store_true",
        help=(
            "Build the fixed geometric mask on demand and clear the costly per-iteration "
            "Adjust hook. Rebuild/broadcast once whenever ramp or tau changes."
        ),
    )
    return result


def next_feedback_tau(
    row: Mapping[str, Any], *, target_kgs: float, minimum: float, maximum: float
) -> float:
    return adaptive_tau_from_inventory(
        float(row["bottom_layer_liquid_inventory_kg"]),
        target_kgs,
        minimum,
        maximum,
    )


def persist(
    manifest: Mapping[str, Any],
    physical_rows: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
) -> None:
    mesh_study.write_json(LOCAL_DIR / "qualification_manifest.json", manifest)
    if physical_rows:
        mesh_study.write_csv(LOCAL_DIR / "physical_monitor_history.csv", physical_rows)
        mesh_study.write_csv(LOCAL_DIR / "mass_balance_history.csv", physical_rows)
    if residual_rows:
        sweep.write_monitor_history_csv(LOCAL_DIR / "residual_history.csv", residual_rows)


def corrected_window(
    physical_rows: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Use Fluent's already-source-inclusive phase-2 Net for liquid closure."""
    result = qualify07b.qualification_window(
        physical_rows, residual_rows, RESIDUAL_LIMIT
    )
    r1_rows = [row for row in physical_rows if int(row["r1_iteration"]) > 0]
    last = r1_rows[-1]
    liquid = float(last["liquid_imbalance_percent"])
    mixture = float(last["mixture_source_augmented_imbalance_percent"])
    balance_pass = liquid <= 0.5 and mixture <= 0.5
    result["latest_balance"] = {
        "liquid_percent": liquid,
        "mixture_percent": mixture,
        "liquid_accounting": (
            "Fluent phase-2 Net already includes the cell-zone liquid source; "
            "do not add the sink a second time"
        ),
    }
    result["balance_pass"] = balance_pass
    result["acceptance_window_pass"] = bool(
        result["physical_stable"]
        and balance_pass
        and result["residual_non_growing"]
        and result["residual_level_pass"]
    )
    return result


def main() -> int:
    global STUDY_ID, RUN_LABEL, LOCAL_DIR, REMOTE_DIR
    global TAU_S, THICKNESS_M, MAXIMUM_R1, MINIMUM_R1, BLOCK
    args = parser().parse_args()
    if args.initial_tau_s <= 0.0:
        raise ValueError("initial tau must be positive")
    if args.layer_thickness_m <= 0.0:
        raise ValueError("layer thickness must be positive")
    if args.maximum_r1_iterations < args.minimum_r1_iterations:
        raise ValueError("maximum R=1 iterations must be at least the minimum")
    if args.block <= 0 or args.feedback_block <= 0:
        raise ValueError("iteration blocks must be positive")
    if args.tau_min_s <= 0.0 or args.tau_max_s < args.tau_min_s:
        raise ValueError("invalid adaptive tau bounds")

    STUDY_ID = args.study_id
    RUN_LABEL = args.run_label
    LOCAL_DIR = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
    REMOTE_DIR = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}\{RUN_LABEL}"
    TAU_S = args.initial_tau_s
    THICKNESS_M = args.layer_thickness_m
    MAXIMUM_R1 = args.maximum_r1_iterations
    MINIMUM_R1 = args.minimum_r1_iterations
    BLOCK = args.block
    adaptive = args.adaptive_target_kgs > 0.0

    load_dotenv(PROJECT_ROOT / ".env")
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    parent_manifest = json.loads(
        (PARENT_DIR / "qualification_manifest.json").read_text(encoding="utf-8")
    )
    parent_start = parent_manifest["checkpoints"]["start_ramp0"]
    parent_library = str(parent_manifest["udf_deployment"]["library_name"])
    carrier_fingerprint = str(parent_manifest["baseline_fingerprint"])
    expected_prepared_payload = copy.deepcopy(
        mesh_study.critical_fingerprint(parent_manifest["settings_readback"])
    )
    expected_prepared_payload.get("initialization", {}).pop("patch", None)
    expected_prepared_fingerprint = mesh_study.fingerprint_sha256(
        expected_prepared_payload
    )
    qualify07b.REMOTE_DIR = REMOTE_DIR
    qualify07b.LOCAL_DIR = LOCAL_DIR

    solver = connect(server_id="1")
    mesh_study.ensure_remote_directory(solver, REMOTE_DIR)
    physical_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    stable_windows = 0
    stop_reason = ""
    transcript = setup07b.remote_join(REMOTE_DIR, "qualification_recovery.trn")
    manifest: dict[str, Any] = {
        "study_id": STUDY_ID,
        "setup_branch": args.setup_branch,
        "run_label": RUN_LABEL,
        "status": "recovery_preflight",
        "classification": "diagnostic in progress",
        "recovery_mode": (
            "reuse setup-07c verified clean prepared checkpoint and loaded UDF "
            "to avoid duplicate UDM reservation in the persistent Fluent session"
        ),
        "superseded_attempt_manifest": str(
            LOCAL_DIR / "qualification_manifest_attempt1_udm_reservation_conflict.json"
        ),
        "source_origin": "setup-07c clean-original prepared ramp-zero checkpoint",
        "parent_start_pair": parent_start,
        "saved_accumulated_solution_loaded": False,
        "fresh_hybrid_initialization_after_tau_change": True,
        "carrier_fingerprint_before_udf_sources": carrier_fingerprint,
        "expected_prepared_fingerprint_with_udf_sources": (
            expected_prepared_fingerprint
        ),
        "tau_s": TAU_S,
        "parent_tau_s": 0.1,
        "sink_strength_relative_to_tau_0p100": 0.1 / TAU_S,
        "layer_thickness_m": THICKNESS_M,
        "parent_layer_thickness_m": PARENT_THICKNESS_M,
        "layer_thickness_relative_to_parent": THICKNESS_M / PARENT_THICKNESS_M,
        "adaptive_feedback": adaptive,
        "adaptive_target_liquid_sink_kgs": args.adaptive_target_kgs,
        "adaptive_feedback_block_iterations": args.feedback_block,
        "adaptive_tau_bounds_s": [args.tau_min_s, args.tau_max_s],
        "adaptive_control_law": (
            "after each feedback block, tau_next = clamp("
            "bottom_band_liquid_inventory / target_sink, tau_min, tau_max); "
            "with source S=-rho*alpha*ramp/tau this targets ramp*target_sink"
            if adaptive
            else "fixed tau"
        ),
        "mask_update_schedule": (
            "on-demand at initialization and every RP ramp/tau change; Adjust hook cleared"
            if args.static_mask_schedule
            else "legacy per-iteration Adjust hook"
        ),
        "ramp_stages": list(qualify07c.RAMP_STAGES),
        "minimum_r1_iterations": MINIMUM_R1,
        "maximum_r1_iterations": MAXIMUM_R1,
        "dpm": "off; no injection update or tracking",
        "liquid_balance_accounting": (
            "use liquid_imbalance_percent because Fluent phase-2 Net already "
            "includes the liquid cell-zone source"
        ),
        "transcript": transcript,
        "checkpoints": {},
        "iteration_evidence": [],
        "started_epoch": time.time(),
    }
    persist(manifest, physical_rows, residual_rows)

    try:
        free_bytes = mesh_study.remote_free_bytes(
            solver, setup07b.remote_join(REMOTE_DIR, "_disk_recovery_preflight.txt")
        )
        manifest["remote_free_gb_at_start"] = free_bytes / 1_000_000_000.0
        if manifest["remote_free_gb_at_start"] < 25.0:
            raise RuntimeError("remote free space is below the 25 GB safety floor")

        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        setup07b.restore_pair(solver, parent_start)

        mesh_metrics, quality_text = mesh_study.collect_mesh_reports(solver)
        (LOCAL_DIR / "mesh_quality.txt").write_text(quality_text, encoding="utf-8")
        if int(mesh_metrics.get("cells", -1)) != qualify07c.EXPECTED_CELLS:
            raise RuntimeError(f"prepared parent mesh mismatch: {mesh_metrics}")

        settings = mesh_study.capture_settings(solver, REMOTE_DIR)
        settings.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_DIR))
        errors = mesh_study.validate_settings(
            settings, mesh_metrics, require_phase_identity=True
        )
        fingerprint_payload = copy.deepcopy(mesh_study.critical_fingerprint(settings))
        fingerprint_payload.get("initialization", {}).pop("patch", None)
        fingerprint = mesh_study.fingerprint_sha256(fingerprint_payload)
        if fingerprint != expected_prepared_fingerprint:
            errors.append(
                "prepared fingerprint mismatch: "
                f"{fingerprint} != {expected_prepared_fingerprint}"
            )
        hooks = setup07c.source_readback(solver)
        errors.extend(
            setup07c.validate_source_readback(hooks, library=parent_library)
        )
        if bool(solver.scheme.eval("(sg-dpm?)")):
            errors.append("DPM model unexpectedly active")
        if errors:
            raise RuntimeError("prepared-parent recovery parity failed: " + "; ".join(errors))

        setup07c.set_rp_real(solver, "user/cwl07c/tau-s", TAU_S)
        setup07c.set_rp_real(
            solver, "user/cwl07c/layer-thickness-m", THICKNESS_M
        )
        setup07c.set_rp_real(solver, "user/cwl07c/ramp", 0.0)
        parameters = setup07c.rp_readback(solver)
        if not math.isclose(
            float(parameters["user/cwl07c/tau-s"]), TAU_S, abs_tol=1.0e-12
        ):
            raise RuntimeError(f"tau readback failed: {parameters}")
        if not math.isclose(
            float(parameters["user/cwl07c/layer-thickness-m"]),
            THICKNESS_M,
            rel_tol=1.0e-12,
        ):
            raise RuntimeError(f"thickness readback failed: {parameters}")

        sweep.maybe_initialize(solver, "hybrid")
        sweep.set_verified_iteration_label(solver, 0)
        mask_console = setup07c.execute_mask_builder(solver, parent_library)
        mask_readback = qualify07c.parse_mask_readback(mask_console)
        errors = qualify07c.validate_mask(
            mask_readback,
            bottom_y_m=float(parent_manifest["geometry_readback"]["bottom_y_m"]),
            thickness_m=THICKNESS_M,
        )
        mask_field, source_field, fields = qualify07c.latest_fields(solver)
        mask_volume = qualify07b.volume_report(
            solver, "07d_prepared_mask", "volume_integral", mask_field
        )
        if not math.isclose(mask_volume, mask_readback["volume"], rel_tol=2.0e-5):
            errors.append(
                f"mask volume mismatch: field={mask_volume}; UDF={mask_readback['volume']}"
            )
        if bool(solver.scheme.eval("(sg-dpm?)")):
            errors.append("DPM active after fresh initialization")
        if errors:
            raise RuntimeError("07d recovery preflight failed: " + "; ".join(errors))

        if args.static_mask_schedule:
            manifest["adjust_hook_clear"] = setup07c.clear_adjust_hook(solver)
            manifest["static_mask_equivalence_basis"] = (
                "mask membership depends only on fixed cell-centroid y and requested "
                "band height; source values still use live rho/alpha/velocity, while "
                "on-demand execution broadcasts ramp/tau before each control stage"
            )

        manifest.update(
            {
                "status": "prepared",
                "mesh_metrics": mesh_metrics,
                "baseline_fingerprint": fingerprint,
                "settings_readback": settings,
                "source_readback": hooks,
                "rp_parameter_readback": parameters,
                "mask_console_readback": mask_console,
                "mask_readback": mask_readback,
                "mask_field": mask_field,
                "source_field": source_field,
                "mask_volume_integral_m3": mask_volume,
                "udm_fields": [
                    name
                    for name in fields
                    if "cwl07c" in name.lower() or "udm" in name.lower()
                ],
            }
        )
        start_pair = setup07b.save_pair(
            solver,
            REMOTE_DIR,
            f"start_from_prepared07c_fresh_hybrid_{RUN_LABEL}_ramp0",
        )
        manifest["checkpoints"]["start_ramp0"] = start_pair
        persist(manifest, physical_rows, residual_rows)

        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.set_verified_iteration_label(solver, 0)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()
        manifest["status"] = "running"
        manifest["classification"] = "diagnostic capacity-matched sink in progress"
        persist(manifest, physical_rows, residual_rows)

        liquid_phase = str(parent_manifest["geometry_readback"]["liquid_phase"])
        liquid_density = float(settings["phase_densities_kg_m3"][liquid_phase])
        cumulative = 0
        r1_completed = 0

        for ramp, iterations in qualify07c.RAMP_STAGES:
            setup07c.set_rp_real(solver, "user/cwl07c/ramp", ramp)
            if args.static_mask_schedule:
                setup07c.execute_mask_builder(solver, parent_library)
            remaining = iterations
            while remaining > 0:
                requested = min(
                    args.feedback_block if adaptive else args.block,
                    remaining,
                )
                current_tau = float(
                    setup07c.rp_readback(solver)["user/cwl07c/tau-s"]
                )
                before = sweep.monitor_iteration_snapshot(solver)
                solver.settings.solution.run_calculation.iterate(iter_count=requested)
                after = sweep.require_monitor_advance(
                    solver, before, requested, 60.0
                )
                cumulative += requested
                remaining -= requested
                row = qualify07b.collect_metrics(
                    solver,
                    cumulative_iteration=cumulative,
                    r1_iteration=0,
                    stage=f"ramp_{ramp:.3f}",
                    ramp=ramp,
                    tau_s=current_tau,
                    liquid_density=liquid_density,
                    mask_field=mask_field,
                    mass_source_field=source_field,
                )
                physical_rows.append(row)
                residual_rows = sweep.monitor_history_rows(solver)
                evidence: dict[str, Any] = {
                    "stage": f"ramp_{ramp:.3f}",
                    "requested": requested,
                    "cumulative_iteration": cumulative,
                    "tau_s": current_tau,
                    "before": before,
                    "after": after,
                }
                if adaptive:
                    tau_next = next_feedback_tau(
                        row,
                        target_kgs=args.adaptive_target_kgs,
                        minimum=args.tau_min_s,
                        maximum=args.tau_max_s,
                    )
                    setup07c.set_rp_real(
                        solver, "user/cwl07c/tau-s", tau_next
                    )
                    if args.static_mask_schedule:
                        setup07c.execute_mask_builder(solver, parent_library)
                    evidence["tau_next_s"] = tau_next
                    manifest.setdefault("adaptive_tau_history", []).append(
                        {
                            "cumulative_iteration": cumulative,
                            "ramp": ramp,
                            "tau_used_s": current_tau,
                            "tau_next_s": tau_next,
                            "band_liquid_inventory_kg": row[
                                "bottom_layer_liquid_inventory_kg"
                            ],
                            "sink_magnitude_kgs": row["sink_magnitude_kgs"],
                        }
                    )
                manifest["iteration_evidence"].append(evidence)
                manifest["cumulative_iterations_completed"] = cumulative
                manifest["r1_iterations_completed"] = 0
                manifest["latest_metrics"] = row
                if bool(solver.scheme.eval("(sg-dpm?)")):
                    stop_reason = "DPM unexpectedly active during ramp"
                if float(row["sink_magnitude_kgs"]) > SINK_GUARD_KGS:
                    stop_reason = (
                        f"sink exceeded {SINK_GUARD_KGS} kg/s during ramp"
                    )
                persist(manifest, physical_rows, residual_rows)
                print(
                    f"07-control ramp={ramp:.3f} cumulative={cumulative} "
                    f"tau={current_tau:.6g} s "
                    f"sink={row['sink_magnitude_kgs']:.6g} kg/s "
                    f"liquid-imbalance={row['liquid_imbalance_percent']:.4g}%",
                    flush=True,
                )
                if stop_reason:
                    break
            if stop_reason:
                break

        if not stop_reason:
            manifest["checkpoints"]["ramp_complete"] = setup07b.save_pair(
                solver, REMOTE_DIR, f"ramp_complete_cumulative{cumulative}_r0p75"
            )
            setup07c.set_rp_real(solver, "user/cwl07c/ramp", 1.0)
            if args.static_mask_schedule:
                setup07c.execute_mask_builder(solver, parent_library)
            while r1_completed < args.maximum_r1_iterations:
                requested = min(
                    args.feedback_block if adaptive else args.block,
                    args.maximum_r1_iterations - r1_completed,
                )
                current_tau = float(
                    setup07c.rp_readback(solver)["user/cwl07c/tau-s"]
                )
                before = sweep.monitor_iteration_snapshot(solver)
                solver.settings.solution.run_calculation.iterate(iter_count=requested)
                after = sweep.require_monitor_advance(solver, before, requested, 60.0)
                cumulative += requested
                r1_completed += requested
                row = qualify07b.collect_metrics(
                    solver,
                    cumulative_iteration=cumulative,
                    r1_iteration=r1_completed,
                    stage="ramp_1.00",
                    ramp=1.0,
                    tau_s=current_tau,
                    liquid_density=liquid_density,
                    mask_field=mask_field,
                    mass_source_field=source_field,
                )
                physical_rows.append(row)
                residual_rows = sweep.monitor_history_rows(solver)
                window = corrected_window(physical_rows, residual_rows)
                evidence = {
                    "stage": "ramp_1.00",
                    "requested": requested,
                    "cumulative_iteration": cumulative,
                    "r1_iteration": r1_completed,
                    "tau_s": current_tau,
                    "before": before,
                    "after": after,
                }
                if adaptive:
                    tau_next = next_feedback_tau(
                        row,
                        target_kgs=args.adaptive_target_kgs,
                        minimum=args.tau_min_s,
                        maximum=args.tau_max_s,
                    )
                    setup07c.set_rp_real(
                        solver, "user/cwl07c/tau-s", tau_next
                    )
                    if args.static_mask_schedule:
                        setup07c.execute_mask_builder(solver, parent_library)
                    evidence["tau_next_s"] = tau_next
                    manifest.setdefault("adaptive_tau_history", []).append(
                        {
                            "cumulative_iteration": cumulative,
                            "r1_iteration": r1_completed,
                            "ramp": 1.0,
                            "tau_used_s": current_tau,
                            "tau_next_s": tau_next,
                            "band_liquid_inventory_kg": row[
                                "bottom_layer_liquid_inventory_kg"
                            ],
                            "sink_magnitude_kgs": row["sink_magnitude_kgs"],
                        }
                    )
                manifest["iteration_evidence"].append(evidence)
                manifest.update(
                    {
                        "cumulative_iterations_completed": cumulative,
                        "r1_iterations_completed": r1_completed,
                        "latest_metrics": row,
                        "latest_500_iteration_assessment": window,
                    }
                )
                if r1_completed % 1000 == 0:
                    manifest["checkpoints"][f"r1_{r1_completed}"] = setup07b.save_pair(
                        solver,
                        REMOTE_DIR,
                        f"r1_iter{r1_completed}_cumulative{cumulative}",
                    )

                r1_rows = [
                    item
                    for item in physical_rows
                    if int(item.get("r1_iteration", 0)) > 0
                ]
                if len(r1_rows) >= 2:
                    jumps = qualify07c.abrupt_change(r1_rows[-2], r1_rows[-1])
                    manifest["latest_block_change_percent"] = jumps
                    manifest.setdefault("block_change_history", []).append(
                        {"r1_iteration": r1_completed, **jumps}
                    )
                    if r1_completed >= 750 and jumps["pressure_drop_pa"] > 20.0:
                        stop_reason = f"abrupt >20% pressure-drop block change: {jumps}"
                if float(row["sink_magnitude_kgs"]) > SINK_GUARD_KGS:
                    stop_reason = f"sink exceeded guarded {SINK_GUARD_KGS} kg/s"
                if bool(solver.scheme.eval("(sg-dpm?)")):
                    stop_reason = "DPM unexpectedly active"

                if r1_completed >= args.minimum_r1_iterations:
                    stable_windows = (
                        stable_windows + 1
                        if window["acceptance_window_pass"]
                        else 0
                    )
                manifest["stable_windows_observed"] = stable_windows
                persist(manifest, physical_rows, residual_rows)
                print(
                    f"07-control R=1 {r1_completed}/{args.maximum_r1_iterations} "
                    f"tau={current_tau:.6g} s "
                    f"sink={row['sink_magnitude_kgs']:.6g} kg/s "
                    f"inventory={row['domain_liquid_inventory_kg']:.6g} kg "
                    f"liquid-imbalance={row['liquid_imbalance_percent']:.4g}% "
                    f"window-pass={window['acceptance_window_pass']}",
                    flush=True,
                )
                if stop_reason or stable_windows >= STABLE_WINDOWS_REQUIRED:
                    break

        setup07c.set_rp_real(solver, "user/cwl07c/ramp", 0.0)
        if args.static_mask_schedule:
            setup07c.execute_mask_builder(solver, parent_library)
        accepted = stable_windows >= STABLE_WINDOWS_REQUIRED
        final_label = (
            f"accepted_r1_{r1_completed}_ramp_reset0"
            if accepted
            else f"diagnostic_stop_r1_{r1_completed}_ramp_reset0"
        )
        manifest["checkpoints"]["final"] = setup07b.save_pair(
            solver, REMOTE_DIR, final_label
        )
        manifest.update(
            {
                "status": "completed",
                "classification": (
                    "accepted numerical capacity-matched sink diagnostic"
                    if accepted
                    else "diagnostic/unresolved capacity-matched sink result"
                ),
                "stable_windows_observed": stable_windows,
                "stop_reason": stop_reason or "maximum iteration budget reached",
                "ramp_after_run": 0.0,
                "dpm_after_run": bool(solver.scheme.eval("(sg-dpm?)")),
                "completed_epoch": time.time(),
            }
        )
        persist(manifest, physical_rows, residual_rows)
        return 0
    except BaseException as exc:
        manifest.update(
            {
                "status": "failed",
                "classification": "diagnostic/unresolved recovery or run failure",
                "failure_category": classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        try:
            setup07c.set_rp_real(solver, "user/cwl07c/ramp", 0.0)
            if args.static_mask_schedule:
                setup07c.execute_mask_builder(solver, parent_library)
            manifest["checkpoints"]["failure_ramp_reset0"] = setup07b.save_pair(
                solver, REMOTE_DIR, f"recovery_failure_ramp_reset0_{int(time.time())}"
            )
        except Exception as save_exc:
            manifest["failure_checkpoint_error"] = (
                f"{type(save_exc).__name__}: {save_exc}"
            )
        persist(manifest, physical_rows, residual_rows)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        persist(manifest, physical_rows, residual_rows)
        print(json.dumps(manifest, indent=2, default=str), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
