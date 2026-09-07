#!/usr/bin/env python3
"""Run setup 07b's first controlled qualification from the clean 900k state.

The controller always reloads the accepted fresh-Hybrid, ramp-zero case/data
pair. It never reads setup-07a accumulated solution data, never initializes
again, never updates DPM, and never overwrites the protected source pair.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.constant_water_level_sink import (  # noqa: E402
    bottom_inventory_from_sink,
    source_augmented_imbalance_percent,
)
from pyansys_fluent.dependency_workflow import classify_failure  # noqa: E402
from pyansys_fluent.mesh_convergence import monitor_stability  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402
import verify_constant_water_level_sink as verify07b  # noqa: E402


STUDY_ID = "split_inlet_constant_water_level_sink_20260807"
RUN_LABEL = "mesh-900k_tau0p100_qualification_v1"
LOCAL_DIR = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
REMOTE_DIR = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}\{RUN_LABEL}"
CLEAN_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}\clean_900k_preparation"
CLEAN_CASE = CLEAN_ROOT + r"\mesh-900k_07b_clean_original_prepared_v3_fresh_hybrid_ramp0.cas.h5"
CLEAN_DATA = CLEAN_ROOT + r"\mesh-900k_07b_clean_original_prepared_v3_fresh_hybrid_ramp0.dat.h5"
EXPECTED_LIBRARY = "lib07b_cwl_bdfa31b0ec_r4_clean1"
EXPECTED_CELLS = 5_335_623
LIQUID_INLET_KGS = 116.92
TOTAL_INLET_KGS = 116.92 + 80.69
LIQUID_FIELD = "phase-2-vof"
RAMP_STAGES = ((0.05, 100), (0.10, 100), (0.25, 150), (0.50, 150))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--tau-s", type=float, default=0.1)
    result.add_argument("--block", type=int, default=250)
    result.add_argument("--minimum-r1-iterations", type=int, default=2500)
    result.add_argument("--maximum-r1-iterations", type=int, default=6000)
    result.add_argument("--checkpoint-interval", type=int, default=1000)
    result.add_argument("--stable-windows-required", type=int, default=2)
    result.add_argument("--minimum-free-gb", type=float, default=30.0)
    result.add_argument("--residual-limit", type=float, default=1.0e-3)
    return result


def set_rp_real(solver: Any, name: str, value: float) -> float:
    setup07b.define_or_set_rp_var(solver, name, float(value), "real")
    readback = float(solver.scheme.eval(f"(rpgetvar '{name})"))
    if not math.isclose(readback, float(value), rel_tol=0.0, abs_tol=1.0e-12):
        raise RuntimeError(f"RP readback mismatch for {name}: {readback} != {value}")
    return readback


def available_fields(solver: Any) -> list[str]:
    return verify07b.scalar_fields(solver)


def volume_report(
    solver: Any, label: str, command_name: str, field: str
) -> float:
    reports = solver.settings.results.report.volume_integrals
    command = getattr(reports, command_name)
    text = mesh_study.report_file_text(
        solver,
        REMOTE_DIR,
        label,
        lambda path: command(
            cell_zones=["fluid"],
            cell_function=field,
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    rows = mesh_study.parse_named_report_rows(text, ["fluid"])
    if "fluid" not in rows:
        raise RuntimeError(f"Could not parse {command_name} for {field}")
    return float(rows["fluid"])


def residual_window_summary(
    rows: Sequence[Mapping[str, Any]], first_iteration: int
) -> dict[str, Any]:
    window = [row for row in rows if float(row["iteration"]) >= first_iteration]
    names = sorted({str(key) for row in window for key in row if key != "iteration"})
    result: dict[str, Any] = {}
    for name in names:
        values = [float(row[name]) for row in window if row.get(name) not in (None, "")]
        if not values:
            continue
        split = max(1, len(values) // 2)
        early = statistics.median(values[:split])
        late = statistics.median(values[split:]) if values[split:] else values[-1]
        trend_ratio = late / early if early != 0.0 else math.inf
        result[name] = {
            "samples": len(values),
            "first": values[0],
            "last": values[-1],
            "minimum": min(values),
            "maximum": max(values),
            "early_median": early,
            "late_median": late,
            "late_to_early_ratio": trend_ratio,
            "non_growing": math.isfinite(trend_ratio) and trend_ratio <= 1.10,
        }
    return result


def collect_metrics(
    solver: Any,
    *,
    cumulative_iteration: int,
    r1_iteration: int,
    stage: str,
    ramp: float,
    tau_s: float,
    liquid_density: float,
    mask_field: str,
    mass_source_field: str,
) -> dict[str, Any]:
    row = mesh_study.collect_physical_metrics(
        solver, REMOTE_DIR, cumulative_iteration
    )
    sink_kgs = volume_report(
        solver,
        f"iter{cumulative_iteration}_sink",
        "volume_integral",
        mass_source_field,
    )
    mask_volume = volume_report(
        solver,
        f"iter{cumulative_iteration}_mask",
        "volume_integral",
        mask_field,
    )
    liquid_volume = volume_report(
        solver,
        f"iter{cumulative_iteration}_liquid_volume",
        "volume_integral",
        LIQUID_FIELD,
    )
    if sink_kgs > 1.0e-8:
        raise RuntimeError(f"liquid source has the wrong sign: {sink_kgs} kg/s")
    row.update(
        {
            "stage": stage,
            "ramp": ramp,
            "tau_s": tau_s,
            "r1_iteration": r1_iteration,
            "integrated_liquid_sink_kgs": sink_kgs,
            "sink_magnitude_kgs": abs(sink_kgs),
            "bottom_adjacent_mask_volume_m3": mask_volume,
            "bottom_layer_liquid_inventory_kg": bottom_inventory_from_sink(
                sink_kgs, tau_s, ramp
            ),
            "domain_liquid_volume_m3": liquid_volume,
            "domain_liquid_inventory_kg": liquid_volume * liquid_density,
            "liquid_source_augmented_net_kgs": row["liquid_net_kgs"] + sink_kgs,
            "liquid_source_augmented_imbalance_percent": (
                source_augmented_imbalance_percent(
                    row["liquid_net_kgs"], sink_kgs, LIQUID_INLET_KGS
                )
            ),
            "mixture_source_augmented_net_kgs": row["mixture_net_kgs"] + sink_kgs,
            "mixture_source_augmented_imbalance_percent": (
                source_augmented_imbalance_percent(
                    row["mixture_net_kgs"], sink_kgs, TOTAL_INLET_KGS
                )
            ),
            "recorded_epoch": time.time(),
        }
    )
    required = (
        "pressure_drop_pa",
        "outlet_area_weighted_velocity_ms",
        "domain_volume_avg_velocity_ms",
        "domain_volume_avg_vorticity_s-1",
        "domain_liquid_inventory_kg",
        "integrated_liquid_sink_kgs",
    )
    if not all(math.isfinite(float(row[name])) for name in required):
        raise RuntimeError(f"non-finite qualification monitor: {row}")
    return row


def qualification_window(
    physical_rows: Sequence[Mapping[str, Any]],
    residual_rows: Sequence[Mapping[str, Any]],
    residual_limit: float,
) -> dict[str, Any]:
    r1_rows = [row for row in physical_rows if int(row["r1_iteration"]) > 0]
    current = int(r1_rows[-1]["r1_iteration"])
    start = max(0, current - 500)
    window = [row for row in r1_rows if int(row["r1_iteration"]) >= start]
    fields = (
        "pressure_drop_pa",
        "integrated_liquid_sink_kgs",
        "domain_liquid_inventory_kg",
        "vapor_steamoutlet_kgs",
        "outlet_area_weighted_velocity_ms",
        "domain_volume_avg_velocity_ms",
        "domain_volume_avg_vorticity_s-1",
    )
    stability = monitor_stability(window, fields, first_iteration=0)
    last = window[-1]
    primary = (
        "pressure_drop_pa",
        "integrated_liquid_sink_kgs",
        "domain_liquid_inventory_kg",
        "vapor_steamoutlet_kgs",
    )
    secondary = (
        "outlet_area_weighted_velocity_ms",
        "domain_volume_avg_velocity_ms",
        "domain_volume_avg_vorticity_s-1",
    )
    enough_samples = len(window) >= 3 and current >= 500
    physical_stable = (
        enough_samples
        and all(stability[name]["drift_percent"] <= 0.5 for name in primary)
        and all(stability[name]["drift_percent"] <= 1.0 for name in secondary)
    )
    balance_pass = (
        float(last["liquid_source_augmented_imbalance_percent"]) <= 0.5
        and float(last["mixture_source_augmented_imbalance_percent"]) <= 0.5
    )
    cumulative_start = int(last["iteration"]) - 500
    residual_summary = residual_window_summary(residual_rows, cumulative_start)
    residual_non_growing = bool(residual_summary) and all(
        item["non_growing"] for item in residual_summary.values()
    )
    residual_level_pass = bool(residual_summary) and all(
        abs(float(item["last"])) <= residual_limit
        for item in residual_summary.values()
    )
    return {
        "r1_window_start": start,
        "r1_window_end": current,
        "samples": len(window),
        "stability": stability,
        "latest_balance": {
            "liquid_percent": last["liquid_source_augmented_imbalance_percent"],
            "mixture_percent": last["mixture_source_augmented_imbalance_percent"],
        },
        "residuals": residual_summary,
        "enough_samples": enough_samples,
        "physical_stable": physical_stable,
        "balance_pass": balance_pass,
        "residual_non_growing": residual_non_growing,
        "residual_limit": residual_limit,
        "residual_level_pass": residual_level_pass,
        "acceptance_window_pass": (
            physical_stable
            and balance_pass
            and residual_non_growing
            and residual_level_pass
        ),
    }


def persist(
    manifest: Mapping[str, Any],
    physical_rows: Sequence[Mapping[str, Any]],
    residual_rows: Sequence[Mapping[str, Any]],
) -> None:
    mesh_study.write_json(LOCAL_DIR / "qualification_manifest.json", manifest)
    if physical_rows:
        mesh_study.write_csv(LOCAL_DIR / "physical_monitor_history.csv", physical_rows)
        mesh_study.write_csv(LOCAL_DIR / "mass_balance_history.csv", physical_rows)
    if residual_rows:
        sweep.write_monitor_history_csv(
            LOCAL_DIR / "residual_history.csv", residual_rows
        )


def main() -> int:
    args = parser().parse_args()
    if args.tau_s <= 0.0:
        raise ValueError("--tau-s must be positive")
    if args.block <= 0 or args.minimum_r1_iterations < 500:
        raise ValueError("block must be positive and minimum R=1 iterations must be >=500")
    if args.maximum_r1_iterations < args.minimum_r1_iterations:
        raise ValueError("maximum R=1 iterations must be >= minimum")

    load_dotenv(PROJECT_ROOT / ".env")
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    solver = connect(server_id=args.server_id)
    mesh_study.ensure_remote_directory(solver, REMOTE_DIR)
    manifest: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "status": "preflight",
        "classification": "diagnostic qualification in progress",
        "source_case": CLEAN_CASE,
        "source_data": CLEAN_DATA,
        "source_origin": "clean original mesh-900k.msh plus fresh Hybrid Initialization",
        "setup07a_accumulated_data_loaded": False,
        "dpm": "off; no injection update or tracking",
        "tau_s": args.tau_s,
        "ramp_stages": list(RAMP_STAGES),
        "r1_block": args.block,
        "minimum_r1_iterations": args.minimum_r1_iterations,
        "maximum_r1_iterations": args.maximum_r1_iterations,
        "checkpoints": {},
        "iteration_evidence": [],
        "started_epoch": time.time(),
        "residual_limit": args.residual_limit,
    }
    physical_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    transcript = setup07b.remote_join(REMOTE_DIR, "qualification_transcript.trn")
    manifest["transcript"] = transcript
    stable_windows = 0
    try:
        free_bytes = mesh_study.remote_free_bytes(
            solver, setup07b.remote_join(REMOTE_DIR, "_disk_preflight.txt")
        )
        free_gb = free_bytes / 1_000_000_000.0
        manifest["remote_free_gb_at_start"] = free_gb
        if free_gb < args.minimum_free_gb:
            raise RuntimeError(
                f"remote C: free space {free_gb:.2f} GB is below "
                f"required {args.minimum_free_gb:.2f} GB"
            )

        solver.settings.file.start_transcript(file_name=transcript)
        solver.settings.file.read_case(file_name=CLEAN_CASE)
        solver.settings.file.read_data(file_name=CLEAN_DATA)
        mesh_metrics, quality_text = mesh_study.collect_mesh_reports(solver)
        if int(mesh_metrics.get("cells", -1)) != EXPECTED_CELLS:
            raise RuntimeError(f"expected {EXPECTED_CELLS} clean cells; got {mesh_metrics}")
        settings = mesh_study.capture_settings(solver, REMOTE_DIR)
        settings.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_DIR))
        errors = mesh_study.validate_settings(
            settings, mesh_metrics, require_phase_identity=True
        )
        sources = verify07b.source_readback(solver)
        errors.extend(
            verify07b.validate_source_readback(sources, library=EXPECTED_LIBRARY)
        )
        if bool(solver.scheme.eval("(sg-dpm?)")):
            errors.append("DPM model unexpectedly active")
        parameters = verify07b.rp_readback(solver)
        if not math.isclose(
            float(parameters["user/cwl07b/ramp"]), 0.0, abs_tol=1.0e-14
        ):
            errors.append(f"protected start ramp is not zero: {parameters}")
        if errors:
            raise RuntimeError("qualification preflight failed: " + "; ".join(errors))

        fields = available_fields(solver)
        mask_field = verify07b.find_field(
            fields, "cwl07b-bottom-adjacent-mask", "udm-0"
        )
        mass_source_field = verify07b.find_field(
            fields, "cwl07b-liquid-mass-source-kgm3s", "udm-1"
        )
        if LIQUID_FIELD not in fields:
            raise RuntimeError(f"required field {LIQUID_FIELD} is unavailable")
        liquid_density = float(settings["phase_densities_kg_m3"]["phase-2"])
        manifest.update(
            {
                "status": "running",
                "mesh_metrics": mesh_metrics,
                "settings_readback": settings,
                "source_readback": sources,
                "initial_rp_readback": parameters,
                "mask_field": mask_field,
                "mass_source_field": mass_source_field,
                "liquid_density_kg_m3": liquid_density,
                "mesh_quality_file": "mesh_quality.txt",
            }
        )
        (LOCAL_DIR / "mesh_quality.txt").write_text(quality_text, encoding="utf-8")
        set_rp_real(solver, "user/cwl07b/tau-s", args.tau_s)
        set_rp_real(solver, "user/cwl07b/ramp", 0.0)
        sweep.configure_residual_history(solver, 10000)
        manifest["residual_early_stop_flags"] = sweep.configure_full_iteration_run(
            solver, allow_early_convergence=False
        )
        sweep.set_verified_iteration_label(solver, 0)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()
        manifest["initial_monitor_snapshot"] = sweep.monitor_iteration_snapshot(solver)
        manifest["checkpoints"]["start_ramp0"] = setup07b.save_pair(
            solver, REMOTE_DIR, "start_clean_fresh_hybrid_ramp0"
        )
        persist(manifest, physical_rows, residual_rows)

        cumulative = 0
        for ramp, iterations in RAMP_STAGES:
            set_rp_real(solver, "user/cwl07b/ramp", ramp)
            before = sweep.monitor_iteration_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=iterations)
            after = sweep.require_monitor_advance(solver, before, iterations, 60.0)
            cumulative += iterations
            manifest["iteration_evidence"].append(
                {
                    "stage": f"ramp_{ramp:.2f}",
                    "ramp": ramp,
                    "requested": iterations,
                    "cumulative_iteration": cumulative,
                    "before": before,
                    "after": after,
                }
            )
            physical_rows.append(
                collect_metrics(
                    solver,
                    cumulative_iteration=cumulative,
                    r1_iteration=0,
                    stage=f"ramp_{ramp:.2f}",
                    ramp=ramp,
                    tau_s=args.tau_s,
                    liquid_density=liquid_density,
                    mask_field=mask_field,
                    mass_source_field=mass_source_field,
                )
            )
            residual_rows = sweep.monitor_history_rows(solver)
            manifest["cumulative_iterations_completed"] = cumulative
            persist(manifest, physical_rows, residual_rows)
            print(
                f"07b qualification: ramp={ramp:.2f}, "
                f"completed={cumulative}, sink={physical_rows[-1]['integrated_liquid_sink_kgs']:.6g} kg/s, "
                f"liquid-balance={physical_rows[-1]['liquid_source_augmented_imbalance_percent']:.4g}%",
                flush=True,
            )

        manifest["checkpoints"]["ramp_complete"] = setup07b.save_pair(
            solver, REMOTE_DIR, f"ramp_complete_iter{cumulative}_r0p50"
        )
        set_rp_real(solver, "user/cwl07b/ramp", 1.0)
        r1_completed = 0
        while r1_completed < args.maximum_r1_iterations:
            requested = min(args.block, args.maximum_r1_iterations - r1_completed)
            before = sweep.monitor_iteration_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=requested)
            after = sweep.require_monitor_advance(solver, before, requested, 60.0)
            cumulative += requested
            r1_completed += requested
            manifest["iteration_evidence"].append(
                {
                    "stage": "ramp_1.00",
                    "ramp": 1.0,
                    "requested": requested,
                    "cumulative_iteration": cumulative,
                    "r1_iteration": r1_completed,
                    "before": before,
                    "after": after,
                }
            )
            physical_rows.append(
                collect_metrics(
                    solver,
                    cumulative_iteration=cumulative,
                    r1_iteration=r1_completed,
                    stage="ramp_1.00",
                    ramp=1.0,
                    tau_s=args.tau_s,
                    liquid_density=liquid_density,
                    mask_field=mask_field,
                    mass_source_field=mass_source_field,
                )
            )
            residual_rows = sweep.monitor_history_rows(solver)
            window = qualification_window(
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
                    REMOTE_DIR,
                    f"r1_iter{r1_completed}_cumulative{cumulative}",
                )
            persist(manifest, physical_rows, residual_rows)
            print(
                f"07b qualification: R=1 {r1_completed}/{args.maximum_r1_iterations}, "
                f"sink={physical_rows[-1]['integrated_liquid_sink_kgs']:.6g} kg/s, "
                f"liquid-balance={physical_rows[-1]['liquid_source_augmented_imbalance_percent']:.4g}%, "
                f"window-pass={window['acceptance_window_pass']}",
                flush=True,
            )
            if r1_completed >= args.minimum_r1_iterations:
                stable_windows = (
                    stable_windows + 1 if window["acceptance_window_pass"] else 0
                )
                if stable_windows >= args.stable_windows_required:
                    break

        set_rp_real(solver, "user/cwl07b/ramp", 0.0)
        final_label = (
            f"accepted_stop_r1_{r1_completed}_ramp_reset0"
            if stable_windows >= args.stable_windows_required
            else f"max_r1_{r1_completed}_unresolved_ramp_reset0"
        )
        manifest["checkpoints"]["final"] = setup07b.save_pair(
            solver, REMOTE_DIR, final_label
        )
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
                "completed_epoch": time.time(),
            }
        )
        persist(manifest, physical_rows, residual_rows)
        return 0 if stable_windows >= args.stable_windows_required else 2
    except BaseException as exc:
        manifest.update(
            {
                "status": "failed",
                "classification": "unresolved qualification interruption",
                "failure_category": classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        try:
            set_rp_real(solver, "user/cwl07b/ramp", 0.0)
            manifest["checkpoints"]["failure_ramp_reset0"] = setup07b.save_pair(
                solver, REMOTE_DIR, f"failure_ramp_reset0_{int(time.time())}"
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
