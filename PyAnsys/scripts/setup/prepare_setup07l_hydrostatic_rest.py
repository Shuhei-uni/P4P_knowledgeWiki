#!/usr/bin/env python3
"""Prepare the setup-07l closed-pool hydrostatic-rest isolation test.

The branch cold-loads the accepted setup-07j time-zero carrier lineage and
removes two confounding effects found during the 07j/07k forensic review:
inherited DPM injections and immediate through-flow.  Both inlets are set to
zero mass flow and ``brineoutlet`` is temporarily converted to a wall.  The
steam pressure outlet remains the pressure anchor.  Fluent is then freshly
Hybrid-initialized and the same geometry-derived ``y <= 0 m`` liquid pool is
reapplied.  No physical time is advanced by this script.

This is an isolation diagnostic, not a proposed production boundary model.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import require_live_compute_node_count, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import prepare_setup07j_transient_vof as source07j  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = source07j.STUDY_ID
RUN_LABEL = "brine620k_07l_hydrostatic_rest_v1"
REMOTE_ROOT = source07j.REMOTE_ROOT
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
TIME_STEP_SIZE_S = 1.0e-6
MAX_ITERATIONS_PER_TIME_STEP = 20
MAX_VOF_COURANT = 0.25
EXPECTED_COMPUTE_NODES = source07j.EXPECTED_COMPUTE_NODES
VAPOR_DENSITY_KG_M3 = 5.797433853149414
REFERENCE_PRESSURE_LOCATION_M = [0.0, 1.0, 0.0]
INLET_ZONES = ("liquidinlet", "steaminlet")
PHASES = ("phase-1", "phase-2")


def run_label_for_server(server_id: str | int) -> str:
    normalized = str(server_id).strip()
    if normalized not in {"1", "2", "3"}:
        raise ValueError(f"unsupported Fluent server id: {server_id!r}")
    return RUN_LABEL if normalized == "1" else f"{RUN_LABEL}_server{normalized}"


def local_root_for_server(server_id: str | int) -> Path:
    return PROJECT_ROOT / "output" / STUDY_ID / run_label_for_server(server_id)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def configured_zero_inlet_state(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copied inlet state with both carrier-phase rates set to zero."""
    result = copy.deepcopy(dict(state))
    phases = result.get("phase")
    if not isinstance(phases, dict):
        raise RuntimeError(f"mass-flow inlet has no phase state: {state}")
    for phase in PHASES:
        phase_state = phases.get(phase)
        if not isinstance(phase_state, dict):
            raise RuntimeError(f"mass-flow inlet is missing {phase}: {state}")
        momentum = phase_state.setdefault("momentum", {})
        momentum["mass_flow_rate"] = {"option": "value", "value": 0.0}
    return result


def zero_inlet_flows(solver: Any) -> dict[str, Any]:
    inlets = solver.settings.setup.boundary_conditions.mass_flow_inlet
    result: dict[str, Any] = {}
    names = set(inlets.get_object_names())
    missing = sorted(set(INLET_ZONES) - names)
    if missing:
        raise RuntimeError(f"required mass-flow inlets are missing: {missing}")
    for zone in INLET_ZONES:
        before = inlets[zone].get_state()
        inlets[zone].set_state(configured_zero_inlet_state(before))
        after = inlets[zone].get_state()
        for phase in PHASES:
            actual = nested(after, "phase", phase, "momentum", "mass_flow_rate", "value")
            if actual is None or not math.isclose(
                float(actual), 0.0, rel_tol=0.0, abs_tol=1.0e-12
            ):
                raise RuntimeError(
                    f"zero-flow readback failed for {zone}/{phase}: {actual}"
                )
        result[zone] = {"before": before, "after": after}
    return result


def close_brine_outlet(solver: Any) -> dict[str, Any]:
    boundaries = solver.settings.setup.boundary_conditions
    before = {
        "pressure_outlets": list(boundaries.pressure_outlet.get_object_names()),
        "mass_flow_outlets": list(boundaries.mass_flow_outlet.get_object_names()),
        "walls": list(boundaries.wall.get_object_names()),
    }
    boundaries.set_zone_type(zone_list=["brineoutlet"], new_type="wall")
    after = {
        "pressure_outlets": list(boundaries.pressure_outlet.get_object_names()),
        "mass_flow_outlets": list(boundaries.mass_flow_outlet.get_object_names()),
        "walls": list(boundaries.wall.get_object_names()),
    }
    if "brineoutlet" not in after["walls"]:
        raise RuntimeError(f"brineoutlet did not read back as wall: {after}")
    if (
        "brineoutlet" in after["pressure_outlets"]
        or "brineoutlet" in after["mass_flow_outlets"]
    ):
        raise RuntimeError(f"brineoutlet remains in an outlet collection: {after}")
    return {"before": before, "after": after, "wall_state": boundaries.wall["brineoutlet"].get_state()}


def delete_all_dpm_injections(solver: Any) -> dict[str, Any]:
    dpm = solver.settings.setup.models.discrete_phase
    injections = dpm.injections
    before_names = list(injections.get_object_names())
    deleted: list[str] = []
    for name in before_names:
        branch = solver.settings.setup.models.discrete_phase.injections
        try:
            branch.__delitem__(name)
        except Exception:
            branch.delete(name_list=[name])
        deleted.append(name)

    # Interaction=False alone does not prevent one-way parcel tracking.  The
    # previous 07j/07k transcripts proved that unsteady injection updates still
    # occurred, so both tracking and all injection objects are gated here.
    dpm = solver.settings.setup.models.discrete_phase
    dpm.general_settings.interaction.enabled.set_state(False)
    dpm.general_settings.unsteady_tracking.enabled.set_state(False)
    after_names = list(dpm.injections.get_object_names())
    interaction = dpm.general_settings.interaction.get_state()
    unsteady = dpm.general_settings.unsteady_tracking.get_state()
    if after_names:
        raise RuntimeError(f"DPM injections remain after deletion: {after_names}")
    if bool(interaction.get("enabled")):
        raise RuntimeError(f"DPM interaction remains enabled: {interaction}")
    if bool(unsteady.get("enabled")):
        raise RuntimeError(f"DPM unsteady tracking remains enabled: {unsteady}")
    return {
        "before_injection_names": before_names,
        "deleted_injection_names": deleted,
        "after_injection_names": after_names,
        "interaction_readback": interaction,
        "unsteady_tracking_readback": unsteady,
        "classification": "DPM model dormant; zero injections; no parcel tracking",
    }


def _set_numeric_child(group: Any, child_name: str, value: float) -> bool:
    child = getattr(group, child_name)
    try:
        child.set_state(value)
        return True
    except Exception:
        state = child.get_state()
        if isinstance(state, Mapping) and "value" in state:
            updated = copy.deepcopy(dict(state))
            updated["value"] = value
            child.set_state(updated)
            return True
    return False


def _find_numeric_density(value: Any) -> float | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key == "method":
                continue
            found = _find_numeric_density(child)
            if found is not None:
                return found
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def configure_operating_reference(solver: Any) -> dict[str, Any]:
    operating = solver.settings.setup.general.operating_conditions
    density = operating.operating_density
    before = safe_get_state(operating, "07l-operating-before")
    density.method.set_state("user-input")
    density = solver.settings.setup.general.operating_conditions.operating_density
    active = list(density.get_active_child_names())
    candidate_children = [name for name in active if name != "method"]
    set_child = ""
    for name in candidate_children:
        try:
            if _set_numeric_child(density, name, VAPOR_DENSITY_KG_M3):
                set_child = name
                break
        except Exception:
            continue
    if not set_child:
        raise RuntimeError(
            "operating-density user-input exposed no writable numeric child; "
            f"active children={active}"
        )
    operating.reference_pressure_location.set_state(REFERENCE_PRESSURE_LOCATION_M)
    after = safe_get_state(operating, "07l-operating-after")
    method = nested(after, "operating_density", "method")
    value = _find_numeric_density(nested(after, "operating_density"))
    location = nested(after, "reference_pressure_location")
    if method != "user-input" or value is None or not math.isclose(
        value, VAPOR_DENSITY_KG_M3, rel_tol=0.0, abs_tol=1.0e-6
    ):
        raise RuntimeError(f"specified operating-density readback failed: {after}")
    if list(location or []) != REFERENCE_PRESSURE_LOCATION_M:
        raise RuntimeError(f"reference-pressure location readback failed: {after}")
    return {
        "before": before,
        "after": after,
        "numeric_child": set_child,
        "specified_density_kg_m3": value,
        "reference_pressure_location_m": location,
    }


def configure_bounded_transient_controls(solver: Any) -> dict[str, Any]:
    controls = solver.settings.solution.run_calculation.transient_controls
    controls.time_step_size.set_state(TIME_STEP_SIZE_S)
    controls.max_iter_per_time_step.set_state(MAX_ITERATIONS_PER_TIME_STEP)
    solver.tui.define.models.multiphase.volume_fraction_parameters.courant_number(
        MAX_VOF_COURANT
    )
    after = controls.get_state()
    actual_dt = nested(after, "time_step_size")
    actual_iterations = nested(after, "max_iter_per_time_step")
    if actual_dt is None or not math.isclose(
        float(actual_dt), TIME_STEP_SIZE_S, rel_tol=0.0, abs_tol=1.0e-14
    ):
        raise RuntimeError(f"time-step readback failed: {after}")
    if int(actual_iterations or -1) != MAX_ITERATIONS_PER_TIME_STEP:
        raise RuntimeError(f"inner-iteration readback failed: {after}")
    return {
        "transient_controls": after,
        "requested_max_vof_courant": MAX_VOF_COURANT,
        "limitation": "actual Global Courant must be captured from the solve transcript",
    }


def validate_snapshot(
    snapshot: Mapping[str, Any], mesh_metrics: Mapping[str, Any]
) -> list[str]:
    errors = []
    for error in source07j.validate_snapshot(snapshot, mesh_metrics):
        if "boundary_conditions.pressure_outlet.brineoutlet" in error:
            continue
        if "boundary_conditions.mass_flow_inlet.liquidinlet" in error:
            continue
        if "boundary_conditions.mass_flow_inlet.steaminlet" in error:
            continue
        errors.append(error)

    for zone in INLET_ZONES:
        for phase in PHASES:
            actual = nested(
                snapshot,
                "boundary_conditions",
                "mass_flow_inlet",
                zone,
                "phase",
                phase,
                "momentum",
                "mass_flow_rate",
                "value",
            )
            if actual is None or not math.isclose(
                float(actual), 0.0, rel_tol=0.0, abs_tol=1.0e-12
            ):
                errors.append(f"{zone}/{phase} zero-flow expected actual={actual}")
    if nested(snapshot, "boundary_conditions", "wall", "brineoutlet") is None:
        errors.append("brineoutlet is not present under wall")
    if nested(snapshot, "boundary_conditions", "pressure_outlet", "brineoutlet") is not None:
        errors.append("brineoutlet remains present under pressure_outlet")
    if nested(snapshot, "boundary_conditions", "mass_flow_outlet", "brineoutlet") is not None:
        errors.append("brineoutlet remains present under mass_flow_outlet")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)

    run_label = run_label_for_server(args.server_id)
    local_root = local_root_for_server(args.server_id)
    local_root.mkdir(parents=True, exist_ok=True)
    manifest_path = local_root / "preparation_manifest.json"
    source_path = source07j.local_root_for_server(args.server_id) / "preparation_manifest.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("status") != "accepted":
        raise RuntimeError("accepted setup-07j time-zero preparation is unavailable")

    payload: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": run_label,
        "server_id": args.server_id,
        "status": "running",
        "classification": "diagnostic preparation / hydrostatic-rest isolation",
        "source_preparation": str(source_path),
        "source_checkpoint": source["prepared_checkpoint"],
        "controlled_changes": [
            "delete all inherited DPM injections; disable unsteady tracking and interaction",
            "set both carrier phases at both inlets to 0 kg/s",
            "convert brineoutlet temporarily to wall",
            "specified operating density = vapor density and pressure reference in gas region",
            f"time step reduced to {TIME_STEP_SIZE_S:g} s",
        ],
        "unchanged_physics": (
            "transient explicit VOF, vapor primary/liquid secondary, RNG k-epsilon, "
            "gravity, Energy off, PISO, PRESTO, Geo-Reconstruct, WFGC, same 620431-cell mesh"
        ),
        "physical_time_steps_run": 0,
        "production_claim": False,
        "started_epoch": time.time(),
    }
    write_json(manifest_path, payload)

    # The project connection helper always authenticates PyFluent with
    # cleanup_on_exit=False.
    solver = connect(server_id=args.server_id, start_transcript=True)
    transcript_started = False
    transcript = source07j.remote_join(REMOTE_ROOT, f"{run_label}_preparation.trn")
    try:
        payload["live_parallel_runtime"] = require_live_compute_node_count(
            solver, EXPECTED_COMPUTE_NODES
        )
        solver.transcript.stop()
        solver.settings.file.read_case(file_name=source["prepared_checkpoint"]["case"])
        solver.settings.file.read_data(file_name=source["prepared_checkpoint"]["data"])
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        transcript_started = True

        payload["dpm_cleanup_readback"] = delete_all_dpm_injections(solver)
        payload["zero_inlet_readback"] = zero_inlet_flows(solver)
        payload["brine_wall_conversion_readback"] = close_brine_outlet(solver)
        payload["operating_reference_readback"] = configure_operating_reference(solver)
        payload["transient_control_readback"] = configure_bounded_transient_controls(solver)

        preinit = mesh_study.capture_settings(solver, REMOTE_ROOT)
        preinit_errors = validate_snapshot(preinit, source["mesh_metrics"])
        preinit_errors = [
            error
            for error in preinit_errors
            if not error.startswith("phase_materials.")
            and not error.startswith("phase_densities_kg_m3.")
        ]
        payload["preinitialization_settings_readback"] = preinit
        payload["preinitialization_validation_errors"] = preinit_errors
        if preinit_errors:
            raise RuntimeError(
                "pre-initialization readback failed: " + "; ".join(preinit_errors)
            )

        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.maybe_initialize(solver, "hybrid")
        payload["initialization_note"] = (
            "Hybrid initialization reports constant-pressure startup when boundary pressure "
            "information is unavailable; the subsequent rest run tests bounded relaxation, "
            "not an analytically patched hydrostatic pressure field."
        )
        payload["pool_cell_register_readback"] = source07j.create_pool_register(solver)
        payload["pool_patch_readback"] = source07j.patch_pool(solver)
        sweep.set_verified_iteration_label(solver, 0)

        initialized = mesh_study.capture_settings(solver, REMOTE_ROOT)
        initialized.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT))
        errors = validate_snapshot(initialized, source["mesh_metrics"])
        dpm_after = delete_all_dpm_injections(solver)
        if dpm_after["after_injection_names"]:
            errors.append(f"DPM injections reappeared after initialization: {dpm_after}")
        payload["postinitialization_dpm_readback"] = dpm_after
        payload["initialized_settings_readback"] = initialized
        payload["initialized_validation_errors"] = errors
        payload["mesh_metrics"] = source["mesh_metrics"]
        payload["transient_method_readback"] = source["transient_method_readback"]
        if errors:
            raise RuntimeError("initialized readback failed: " + "; ".join(errors))

        checkpoint = {
            "case": source07j.remote_join(REMOTE_ROOT, f"{run_label}_initialized_t0.cas.h5"),
            "data": source07j.remote_join(REMOTE_ROOT, f"{run_label}_initialized_t0.dat.h5"),
        }
        sweep.write_case_data_pair(
            solver, checkpoint["case"], checkpoint["data"], "07l_initialized_t0"
        )
        payload.update(
            {
                "status": "accepted",
                "prepared_checkpoint": checkpoint,
                "completed_epoch": time.time(),
            }
        )
        write_json(manifest_path, payload)
        return 0
    except Exception as exc:
        payload.update(
            {
                "status": "unresolved",
                "classification": "diagnostic preparation / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        write_json(manifest_path, payload)
        raise
    finally:
        if transcript_started:
            try:
                solver.settings.file.stop_transcript()
                text = sweep.remote_text_read_best_effort(solver, transcript)
                if text:
                    (local_root / "preparation_transcript.trn").write_text(
                        text, encoding="utf-8"
                    )
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
