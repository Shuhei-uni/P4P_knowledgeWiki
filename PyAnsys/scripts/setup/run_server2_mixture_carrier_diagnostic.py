#!/usr/bin/env python3
"""Run a bounded carrier-only extension of the live server-2 Mixture case.

The live state is not treated as authoritative setup-07m lineage.  It is saved
first and labelled unverified, then inherited DPM injections are removed before
five proven 50-iteration carrier blocks are attempted.
"""

from __future__ import annotations

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

from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402

import prepare_setup07l_hydrostatic_rest as prepare07l  # noqa: E402
import prepare_setup07h_brine_pool as prepare07h  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07g_brine_outlet_qualification as qualify07g  # noqa: E402
import run_setup07m_pressure_opening_campaign as campaign07m  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = "server2_mixture_carrier_extension_20260821_v1"
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
MANIFEST = LOCAL_ROOT / "diagnostic_manifest.json"
REMOTE_PREFIX = rf"C:\Users\qtra338\Documents\{RUN_LABEL}"
BLOCK = 50
BLOCKS = 5


def write_json(payload: dict[str, Any]) -> None:
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def save_checkpoint(solver: Any, stem: str, *, allow_case_only: bool = False) -> dict[str, Any]:
    case = stem + ".cas.h5"
    data = stem + ".dat.h5"
    solver.settings.file.write_case(file_name=case)
    data_written = False
    try:
        solver.settings.file.write_data(file_name=data)
        data_written = True
    except Exception:
        if not allow_case_only:
            raise
    if not remote_file_exists(solver, case):
        raise RuntimeError(f"remote case verification failed for {stem}")
    if data_written and not remote_file_exists(solver, data):
        raise RuntimeError(f"remote data verification failed for {stem}")
    return {"case": case, "data": data if data_written else None, "case_only": not data_written}


def clean_dpm(solver: Any) -> dict[str, Any]:
    dpm = solver.settings.setup.models.discrete_phase
    before = list(dpm.injections.get_object_names())
    for name in before:
        branch = solver.settings.setup.models.discrete_phase.injections
        try:
            branch.__delitem__(name)
        except Exception:
            branch.delete(name_list=[name])
    dpm = solver.settings.setup.models.discrete_phase
    dpm.general_settings.interaction.enabled.set_state(False)
    unsteady_state: Any
    try:
        dpm.general_settings.unsteady_tracking.enabled.set_state(False)
        unsteady_state = dpm.general_settings.unsteady_tracking.get_state()
    except Exception as exc:
        unsteady_state = {"inactive_for_steady_case": f"{type(exc).__name__}: {exc}"}
    after = list(dpm.injections.get_object_names())
    if after:
        raise RuntimeError(f"DPM injections remain after deletion: {after}")
    return {
        "before_injection_names": before,
        "deleted_injection_names": before,
        "after_injection_names": after,
        "interaction_readback": dpm.general_settings.interaction.get_state(),
        "unsteady_tracking_readback": unsteady_state,
    }


def configure_brine_boundary(solver: Any) -> dict[str, Any]:
    outlet = solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"]
    state = outlet.get_state()
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {
        "option": "value",
        "value": campaign07m.BRINE_FACE_REST_PRESSURE_PA,
    }
    state["phase"]["phase-2"]["multiphase"]["volume_frac_spec_method"] = (
        "Backflow Volume Fraction"
    )
    state["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"] = {
        "option": "value",
        "value": 1.0,
    }
    outlet.set_state(state)
    readback = solver.settings.setup.boundary_conditions.pressure_outlet[
        "brineoutlet"
    ].get_state()
    actual_pressure = readback["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"]
    actual_liquid = readback["phase"]["phase-2"]["multiphase"][
        "backflow_volume_fraction"
    ]["value"]
    if not math.isclose(
        float(actual_pressure), campaign07m.BRINE_FACE_REST_PRESSURE_PA, abs_tol=1.0e-6
    ):
        raise RuntimeError(f"brine pressure readback mismatch: {actual_pressure}")
    if not math.isclose(float(actual_liquid), 1.0, abs_tol=1.0e-12):
        raise RuntimeError(f"brine liquid backflow readback mismatch: {actual_liquid}")
    return readback


def selected_setup_readback(solver: Any) -> dict[str, Any]:
    setup = solver.settings.setup
    boundaries = setup.boundary_conditions
    dpm = setup.models.discrete_phase
    return {
        "general": safe_get_state(setup.general, "general"),
        "energy": safe_get_state(setup.models.energy, "energy"),
        "multiphase": safe_get_state(setup.models.multiphase, "multiphase"),
        "viscous": safe_get_state(setup.models.viscous, "viscous"),
        "boundary_conditions": safe_get_state(boundaries, "boundary_conditions"),
        "methods": safe_get_state(solver.settings.solution.methods, "methods"),
        "controls": safe_get_state(solver.settings.solution.controls, "controls"),
        "dpm_interaction": safe_get_state(dpm.general_settings.interaction, "dpm.interaction"),
        "dpm_unsteady_tracking": safe_get_state(
            dpm.general_settings.unsteady_tracking, "dpm.unsteady_tracking"
        ),
        "dpm_injection_names": list(dpm.injections.get_object_names()),
        "zones": {
            "walls": list(boundaries.wall.get_object_names()),
            "pressure_outlets": list(boundaries.pressure_outlet.get_object_names()),
            "mass_flow_inlets": list(boundaries.mass_flow_inlet.get_object_names()),
        },
    }


def validate_live_case(state: dict[str, Any]) -> None:
    general = state["general"]
    if general.get("solver", {}).get("time") != "steady":
        raise RuntimeError(f"server-2 diagnostic requires a steady case: {general.get('solver')}")
    if state["energy"].get("enabled") is not False:
        raise RuntimeError(f"Energy must be off: {state['energy']}")
    multiphase = state["multiphase"]
    if multiphase.get("models") != "mixture" or multiphase.get("number_of_phases") != 2:
        raise RuntimeError(f"expected two-phase Mixture model: {multiphase}")
    zones = state["zones"]
    required = {"liquidinlet", "steaminlet"}
    if not required.issubset(set(zones["mass_flow_inlets"])):
        raise RuntimeError(f"missing split inlets: {zones}")
    if not {"steamoutlet", "brineoutlet"}.issubset(set(zones["pressure_outlets"])):
        raise RuntimeError(f"missing resolved outlets: {zones}")
    if state["dpm_interaction"].get("enabled"):
        raise RuntimeError("DPM interaction is enabled in the live server-2 case")


def finite_failures(row: dict[str, Any]) -> list[str]:
    failures = [
        f"non-finite {key}={value}"
        for key, value in row.items()
        if isinstance(value, (int, float)) and not math.isfinite(float(value))
    ]
    if abs(float(row.get("mixture_net_kgs", 0.0))) > 2.0 * qualify07g.TOTAL_INLET_KGS:
        failures.append(f"gross mixture imbalance: {row.get('mixture_net_kgs')}")
    if float(row.get("domain_volume_avg_velocity_ms", 0.0)) > 500.0:
        failures.append(f"gross domain velocity: {row.get('domain_volume_avg_velocity_ms')}")
    return failures


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    result: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "server_id": "2",
        "status": "running",
        "classification": "diagnostic / unverified live Mixture lineage",
        "controller_pid": os.getpid(),
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
        result["fluent_version"] = str(solver.get_fluent_version())
        result["health"] = str(solver.health_check.status())
        result["live_parallel_runtime"] = require_live_compute_node_count(solver, 16)
        before = selected_setup_readback(solver)
        validate_live_case(before)
        result["preflight_readback"] = before
        result["checkpoints"]["loaded_unverified_backup"] = save_checkpoint(
            solver, REMOTE_PREFIX + "_loaded_unverified_backup", allow_case_only=True
        )

        cleanup = clean_dpm(solver)
        result["brine_boundary_readback"] = configure_brine_boundary(solver)
        after = selected_setup_readback(solver)
        validate_live_case(after)
        if after["dpm_injection_names"]:
            raise RuntimeError(f"DPM injections remain: {after['dpm_injection_names']}")
        result["dpm_cleanup_readback"] = cleanup
        result["post_cleanup_readback"] = after
        result["checkpoints"]["carrier_only_case"] = save_checkpoint(
            solver, REMOTE_PREFIX + "_carrier_only_case", allow_case_only=True
        )

        sweep.maybe_initialize(solver, "hybrid")
        prepare07h.REMOTE_ROOT = "."
        result["pool_register_readback"] = prepare07h.create_pool_register(solver)
        result["pool_patch_readback"] = prepare07h.patch_pool(solver)
        result["checkpoints"]["initialized_pool"] = save_checkpoint(
            solver, REMOTE_PREFIX + "_initialized_pool"
        )

        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        qualify07g.REMOTE_ROOT = "."
        rows: list[dict[str, Any]] = []
        for block_index in range(1, BLOCKS + 1):
            before_monitor = mesh_study.monitor_snapshot(solver)
            before_points = mesh_study.monitor_point_count(before_monitor)
            solver.settings.solution.run_calculation.iterate(iter_count=BLOCK)
            after_monitor = mesh_study.monitor_snapshot(solver)
            advance = mesh_study.monitor_point_count(after_monitor) - before_points
            if advance < BLOCK:
                raise RuntimeError(
                    f"monitor history did not prove {BLOCK} iterations: advance={advance}"
                )
            credited = block_index * BLOCK
            row = qualify07g.physical_metrics(solver, credited)
            residuals = campaign07m.residual_tail(solver, count=5)
            row["credited_iterations"] = credited
            row["residual_tail"] = residuals
            failures = finite_failures(row)
            rows.append(row)
            result["blocks"].append({"metrics": row, "gate_failures": failures})
            result["credited_iterations"] = credited
            result["last_heartbeat_epoch"] = time.time()
            if credited in (50, 100, 250):
                result["checkpoints"][str(credited)] = save_checkpoint(
                    solver, f"{REMOTE_PREFIX}_iter{credited}"
                )
            write_json(result)
            print(
                f"server2 carrier diagnostic: {credited}/{BLOCK * BLOCKS}; "
                f"mix_net={row['mixture_net_kgs']:.6g} kg/s; "
                f"brine_l={row['liquid_brineoutlet_kgs']:.6g} kg/s",
                flush=True,
            )
            if failures:
                raise RuntimeError("server-2 physics gate failed: " + "; ".join(failures))

        solver.settings.file.stop_transcript()
        transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
        (LOCAL_ROOT / "transcript.trn").write_text(transcript_text, encoding="utf-8")
        result.update(
            {
                "status": "completed",
                "classification": "diagnostic / carrier-only Mixture extension completed",
                "dpm_tracking_text_detected": "Advancing DPM injections" in transcript_text,
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
