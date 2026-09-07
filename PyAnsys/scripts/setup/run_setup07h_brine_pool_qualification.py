#!/usr/bin/env python3
"""Run guarded setup-07h carrier qualification from the patched clean checkpoint."""

from __future__ import annotations

import csv
import json
import math
import sys
import time
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping, Sequence

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.mesh_convergence import monitor_stability  # noqa: E402

import prepare_setup07h_brine_pool as prepare  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07g_brine_outlet_qualification as base_run  # noqa: E402


STUDY_ID = prepare.STUDY_ID
RUN_LABEL = prepare.RUN_LABEL
REMOTE_ROOT = prepare.REMOTE_ROOT
LOCAL_ROOT = prepare.LOCAL_ROOT
PREPARATION_MANIFEST = LOCAL_ROOT / "preparation_manifest.json"
TARGET_ITERATIONS = 3000
MANDATORY_DIAGNOSTIC_ITERATIONS = 1000
CHECKPOINTS = {25, 250, 500, 1000, 2000, 3000}
REQUIRE_WFGC = False
ENABLE_GROSS_PHYSICAL_GATE = False


def remote_join(directory: str, name: str) -> str:
    return str(PureWindowsPath(directory) / name)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        return
    fields = sorted({str(key) for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def save_pair(solver: Any, label: str) -> dict[str, str]:
    case = remote_join(REMOTE_ROOT, f"{RUN_LABEL}_{label}.cas.h5")
    data = remote_join(REMOTE_ROOT, f"{RUN_LABEL}_{label}.dat.h5")
    sweep.write_case_data_pair(solver, case, data, f"07h_{label}")
    return {"case": case, "data": data}


def finite_state(metrics: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            failures.append(f"{key}=non-finite")
    for key, limit in (
        ("inlet_mass_weighted_pressure_pa", 1.0e8),
        ("pressure_drop_to_steamoutlet_pa", 1.0e8),
        ("pressure_drop_to_brineoutlet_pa", 1.0e8),
        ("domain_volume_avg_velocity_ms", 1.0e5),
        ("domain_volume_avg_vorticity_s-1", 1.0e8),
    ):
        value = abs(float(metrics.get(key, 0.0)))
        if value > limit:
            failures.append(f"{key}={value} exceeds {limit}")
    for phase in ("mixture", "vapor", "liquid"):
        for outlet in ("steamoutlet", "brineoutlet"):
            key = f"{phase}_{outlet}_kgs"
            value = abs(float(metrics.get(key, 0.0)))
            if value > 1.0e5:
                failures.append(f"{key}={value} exceeds 1e5")
    return not failures, failures


def routing_state(metrics: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "steam_mixture_outward": float(metrics["mixture_steamoutlet_kgs"]) < 0.0,
        "brine_mixture_outward": float(metrics["mixture_brineoutlet_kgs"]) < 0.0,
        "steam_vapor_outward": float(metrics["vapor_steamoutlet_kgs"]) < 0.0,
        "brine_liquid_outward": float(metrics["liquid_brineoutlet_kgs"]) < 0.0,
    }


def checkpoint_schedule(completed: int) -> int:
    if completed == 0:
        return 25
    if completed == 25:
        return 225
    return min(250, TARGET_ITERATIONS - completed)


def gross_physical_gate(metrics: Mapping[str, Any]) -> tuple[bool, list[str]]:
    """Reject a finite but clearly nonphysical drainage state."""

    failures: list[str] = []
    liquid_feed = abs(float(metrics["liquid_liquidinlet_kgs"]))
    brine_liquid = abs(float(metrics["liquid_brineoutlet_kgs"]))
    if brine_liquid > 3.0 * liquid_feed:
        failures.append(
            f"brine liquid outflow {brine_liquid} exceeds 3x feed {liquid_feed}"
        )
    if float(metrics["mixture_imbalance_percent"]) > 100.0:
        failures.append(
            f"mixture imbalance {metrics['mixture_imbalance_percent']}% exceeds 100%"
        )
    if float(metrics["liquid_imbalance_percent"]) > 200.0:
        failures.append(
            f"liquid imbalance {metrics['liquid_imbalance_percent']}% exceeds 200%"
        )
    return not failures, failures


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    preparation = json.loads(PREPARATION_MANIFEST.read_text(encoding="utf-8"))
    if preparation.get("status") != "accepted":
        raise RuntimeError("setup-07h preparation is not accepted")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = LOCAL_ROOT / "qualification_manifest.json"
    transcript = remote_join(REMOTE_ROOT, f"{RUN_LABEL}_qualification.trn")

    # Reuse the tested report/readback functions, but point their scratch files
    # at this branch before any call is made.
    base_run.REMOTE_ROOT = REMOTE_ROOT
    base_run.RUN_LABEL = RUN_LABEL
    base_run.LOCAL_ROOT = LOCAL_ROOT

    solver = connect(server_id="1")
    result: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "status": "running",
        "classification": "diagnostic",
        "prepared_checkpoint": preparation["prepared_checkpoint"],
        "target_iterations_if_qualified": TARGET_ITERATIONS,
        "mandatory_diagnostic_iterations": MANDATORY_DIAGNOSTIC_ITERATIONS,
        "iterations_completed": 0,
        "checkpoints": {"initialized_pool": preparation["prepared_checkpoint"]},
        "iteration_blocks": [],
        "dpm": "off; no injections updated or tracked",
        "ewf": "off/not introduced",
        "sink_udf": "absent",
        "started_epoch": time.time(),
    }
    physical_rows: list[dict[str, Any]] = []
    write_json(manifest_path, result)
    try:
        checkpoint = preparation["prepared_checkpoint"]
        solver.settings.file.read_case(file_name=checkpoint["case"])
        solver.settings.file.read_data(file_name=checkpoint["data"])
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        errors, snapshot = base_run.validation_errors(solver, preparation)
        result["cold_reload_settings_readback"] = snapshot
        result["cold_reload_validation_errors"] = errors
        wfgc = solver.settings.solution.methods.warped_face_gradient_correction.get_state()
        result["cold_reload_warped_face_gradient_correction"] = wfgc
        if REQUIRE_WFGC and not bool(wfgc.get("enable")):
            errors.append(
                f"warped-face gradient correction must be enabled; actual={wfgc}"
            )
        if errors:
            raise RuntimeError("cold-reload validation failed: " + "; ".join(errors))
        sweep.set_verified_iteration_label(solver, 0)
        sweep.configure_residual_history(solver, 5000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()

        completed = 0
        while completed < TARGET_ITERATIONS:
            requested = checkpoint_schedule(completed)
            started = time.time()
            proof, after = base_run.proven_iteration_block(solver, transcript, requested)
            completed += requested
            result["iterations_completed"] = completed
            metrics = base_run.physical_metrics(solver, completed)
            finite, finite_failures = finite_state(metrics)
            routing = routing_state(metrics)
            physical_rows.append(metrics)
            block = {
                "end_iteration": completed,
                "requested": requested,
                "wall_seconds": time.time() - started,
                "iteration_proof": proof,
                "after_monitor": after,
                "physical_metrics": metrics,
                "finite_state": finite,
                "finite_state_failures": finite_failures,
                "routing": routing,
            }
            result["iteration_blocks"].append(block)
            if completed in CHECKPOINTS:
                result["checkpoints"][str(completed)] = save_pair(
                    solver, f"checkpoint_iter{completed}"
                )
            residual_rows = base_run.transcript_residual_rows(solver, transcript)
            sweep.write_monitor_history_csv(
                LOCAL_ROOT / "residual_history.csv", residual_rows
            )
            write_csv(LOCAL_ROOT / "physical_monitor_history.csv", physical_rows)
            write_json(manifest_path, result)
            print(
                f"07h {completed}/{TARGET_ITERATIONS}: "
                f"steam mix={metrics['mixture_steamoutlet_kgs']:.6g}, "
                f"brine mix={metrics['mixture_brineoutlet_kgs']:.6g}, "
                f"brine liquid={metrics['liquid_brineoutlet_kgs']:.6g}, "
                f"brine vapor={metrics['vapor_brineoutlet_kgs']:.6g}, "
                f"mix imbalance={metrics['mixture_imbalance_percent']:.4g}%",
                flush=True,
            )
            if not finite:
                raise RuntimeError("numerical divergence gate failed: " + "; ".join(finite_failures))

            if ENABLE_GROSS_PHYSICAL_GATE and completed >= 250:
                physical_pass, physical_failures = gross_physical_gate(metrics)
                block["gross_physical_gate"] = {
                    "passed": physical_pass,
                    "failures": physical_failures,
                    "criteria": "brine liquid <=3x feed; mixture imbalance <=100%; liquid imbalance <=200%",
                }
                write_json(manifest_path, result)
                if not physical_pass:
                    result["status"] = "completed"
                    result["classification"] = "unresolved"
                    result["stop_reason"] = (
                        "gross physical gate rejected finite but nonphysical drainage state"
                    )
                    result["completed_epoch"] = time.time()
                    write_json(manifest_path, result)
                    return 2

            if completed == MANDATORY_DIAGNOSTIC_ITERATIONS:
                route_pass = all(routing.values())
                contamination_pass = (
                    float(metrics["vapor_carryunder_at_brineoutlet_percent_of_feed"]) <= 25.0
                    and float(metrics["liquid_carryover_at_steamoutlet_percent_of_feed"]) <= 10.0
                )
                result["iteration_1000_extension_gate"] = {
                    "routing_pass": route_pass,
                    "contamination_pass": contamination_pass,
                    "criteria": "all intended directions; brine vapor <=25% feed; steam liquid <=10% feed",
                }
                if not (route_pass and contamination_pass):
                    result["status"] = "completed"
                    result["classification"] = "unresolved"
                    result["stop_reason"] = "pool-initialized steady branch failed phase-routing extension gate"
                    result["completed_epoch"] = time.time()
                    write_json(manifest_path, result)
                    return 2

        primary = [
            "pressure_drop_to_steamoutlet_pa",
            "pressure_drop_to_brineoutlet_pa",
            "vapor_steamoutlet_kgs",
            "liquid_brineoutlet_kgs",
        ]
        secondary = [
            "steamoutlet_area_weighted_velocity_ms",
            "brineoutlet_area_weighted_velocity_ms",
            "domain_volume_avg_velocity_ms",
            "domain_volume_avg_vorticity_s-1",
            "domain_volume_avg_liquid_volume_fraction",
        ]
        stability = monitor_stability(
            physical_rows, primary + secondary, first_iteration=2500
        )
        final = physical_rows[-1]
        balance_pass = all(
            float(final[key]) <= 0.5
            for key in (
                "mixture_imbalance_percent",
                "vapor_imbalance_percent",
                "liquid_imbalance_percent",
            )
        )
        primary_stable = all(stability[key]["drift_percent"] <= 0.5 for key in primary)
        secondary_stable = all(stability[key]["drift_percent"] <= 1.0 for key in secondary)
        directions_pass = all(routing_state(final).values())
        classification = (
            "accepted"
            if balance_pass and primary_stable and secondary_stable and directions_pass
            else "unresolved"
        )
        metrics_payload = {
            "study_id": STUDY_ID,
            "run_label": RUN_LABEL,
            "classification": classification,
            "scope": "single-mesh brine-boundary qualification; not mesh independence or separator validation",
            "mesh_metrics": preparation["mesh_metrics"],
            "final_metrics": final,
            "monitor_stability_2500_3000": stability,
            "acceptance": {
                "phase_and_mixture_balance_pass": balance_pass,
                "primary_monitor_stability_pass": primary_stable,
                "secondary_monitor_stability_pass": secondary_stable,
                "outlet_flow_directions_pass": directions_pass,
            },
        }
        write_json(LOCAL_ROOT / "qualification_metrics.json", metrics_payload)
        result.update(
            {"status": "completed", "classification": classification, "metrics": metrics_payload, "completed_epoch": time.time()}
        )
        write_json(manifest_path, result)
        return 0 if classification == "accepted" else 2
    except Exception as exc:
        result.update(
            {"status": "unresolved", "classification": "diagnostic", "error": f"{type(exc).__name__}: {exc}", "failed_epoch": time.time()}
        )
        if result.get("iterations_completed", 0):
            try:
                result["interrupt_checkpoint"] = save_pair(
                    solver, f"interrupt_iter{result['iterations_completed']}"
                )
            except Exception as save_exc:
                result["interrupt_checkpoint_error"] = f"{type(save_exc).__name__}: {save_exc}"
        write_json(manifest_path, result)
        raise
    finally:
        try:
            if solver.monitors.is_streaming:
                solver.monitors.stop()
        except Exception:
            pass
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
        if transcript_text:
            (LOCAL_ROOT / "qualification_transcript.trn").write_text(
                transcript_text, encoding="utf-8"
            )


if __name__ == "__main__":
    raise SystemExit(main())
