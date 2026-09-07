#!/usr/bin/env python3
"""Prepare the controlled setup-07k brine mass-flow-outlet diagnostic.

The branch cold-loads the accepted clean setup-07j time-zero checkpoint,
changes only ``brineoutlet`` from pressure-outlet to a phase-specific
mass-flow-outlet (116.92 kg/s liquid, zero vapor), then performs a fresh
Hybrid Initialization and reapplies the geometry-derived ``y <= 0 m`` pool.
It advances no physical time and keeps DPM, EWF, and sink sources absent.
"""

from __future__ import annotations

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

from pyansys_fluent.common import require_live_compute_node_count  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import prepare_setup07j_transient_vof as source07j  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = source07j.STUDY_ID
RUN_LABEL = "brine620k_07k_transient_vof_massflow_brine_v1"
REMOTE_ROOT = source07j.REMOTE_ROOT
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
TIME_STEP_SIZE_S = source07j.TIME_STEP_SIZE_S
MAX_ITERATIONS_PER_TIME_STEP = source07j.MAX_ITERATIONS_PER_TIME_STEP
EXPECTED_COMPUTE_NODES = source07j.EXPECTED_COMPUTE_NODES
LIQUID_OUTLET_KG_S = 116.92


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


def configured_mass_flow_outlet_state(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return a full state with zero vapor and prescribed liquid discharge."""
    result = copy.deepcopy(dict(state))
    phases = result.get("phase")
    if not isinstance(phases, dict):
        raise RuntimeError(f"mass-flow outlet has no phase state: {state}")
    for phase, rate in (("phase-1", 0.0), ("phase-2", LIQUID_OUTLET_KG_S)):
        phase_state = phases.get(phase)
        if not isinstance(phase_state, dict):
            raise RuntimeError(f"mass-flow outlet is missing {phase}: {state}")
        momentum = phase_state.setdefault("momentum", {})
        momentum["mass_flow_specification"] = "Mass Flow Rate"
        momentum["mass_flow_rate"] = {"option": "value", "value": rate}
    return result


def configure_brine_mass_flow_outlet(solver: Any) -> dict[str, Any]:
    boundaries = solver.settings.setup.boundary_conditions
    boundaries.set_zone_type(
        zone_list=["brineoutlet"], new_type="mass-flow-outlet"
    )
    outlets = boundaries.mass_flow_outlet
    if "brineoutlet" not in outlets.get_object_names():
        raise RuntimeError("brineoutlet did not convert to mass-flow-outlet")
    before = outlets["brineoutlet"].get_state()
    outlets["brineoutlet"].set_state(configured_mass_flow_outlet_state(before))
    after = outlets["brineoutlet"].get_state()
    for phase, expected in (("phase-1", 0.0), ("phase-2", LIQUID_OUTLET_KG_S)):
        actual = nested(
            after, "phase", phase, "momentum", "mass_flow_rate", "value"
        )
        if actual is None or not math.isclose(
            float(actual), expected, rel_tol=0.0, abs_tol=1.0e-8
        ):
            raise RuntimeError(
                f"brine mass-flow readback mismatch for {phase}: {actual}"
            )
    return {"before": before, "after": after}


def validate_snapshot(
    snapshot: Mapping[str, Any], mesh_metrics: Mapping[str, Any]
) -> list[str]:
    errors = [
        error
        for error in source07j.validate_snapshot(snapshot, mesh_metrics)
        if "boundary_conditions.pressure_outlet.brineoutlet" not in error
    ]
    for phase, expected in (("phase-1", 0.0), ("phase-2", LIQUID_OUTLET_KG_S)):
        actual = nested(
            snapshot,
            "boundary_conditions",
            "mass_flow_outlet",
            "brineoutlet",
            "phase",
            phase,
            "momentum",
            "mass_flow_rate",
            "value",
        )
        if actual is None or not math.isclose(
            float(actual), expected, rel_tol=0.0, abs_tol=1.0e-8
        ):
            errors.append(
                f"brineoutlet {phase} mass flow expected={expected} actual={actual}"
            )
    pressure_brine = nested(
        snapshot, "boundary_conditions", "pressure_outlet", "brineoutlet"
    )
    if pressure_brine is not None:
        errors.append("brineoutlet remains present under pressure_outlet")
    return errors


def main() -> int:
    import argparse

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
        "classification": "diagnostic preparation",
        "source_preparation": str(source_path),
        "source_checkpoint": source["prepared_checkpoint"],
        "controlled_change": (
            "brineoutlet pressure-outlet 1.12 MPa -> phase-specific "
            "mass-flow-outlet: liquid 116.92 kg/s, vapor 0 kg/s"
        ),
        "saved_solution_data_used_only_as_clean_t0_origin": True,
        "fresh_hybrid_initialization": True,
        "production_time_steps_run": 0,
        "dpm": "off; no injections updated or tracked",
        "ewf": "off/not introduced",
        "sink_udf": "absent",
        "started_epoch": time.time(),
    }
    write_json(manifest_path, payload)
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

        payload["brine_boundary_conversion_readback"] = configure_brine_mass_flow_outlet(
            solver
        )
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
        payload["pool_cell_register_readback"] = source07j.create_pool_register(solver)
        payload["pool_patch_readback"] = source07j.patch_pool(solver)
        sweep.set_verified_iteration_label(solver, 0)

        initialized = mesh_study.capture_settings(solver, REMOTE_ROOT)
        initialized.update(
            mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT)
        )
        errors = validate_snapshot(initialized, source["mesh_metrics"])
        payload["initialized_settings_readback"] = initialized
        payload["initialized_validation_errors"] = errors
        payload["mesh_metrics"] = source["mesh_metrics"]
        payload["transient_method_readback"] = source["transient_method_readback"]
        payload["full_settings_fingerprint_sha256"] = mesh_study.fingerprint_sha256(
            mesh_study.critical_fingerprint(initialized)
        )
        if errors:
            raise RuntimeError("initialized readback failed: " + "; ".join(errors))

        checkpoint = {
            "case": source07j.remote_join(
                REMOTE_ROOT, f"{run_label}_initialized_t0.cas.h5"
            ),
            "data": source07j.remote_join(
                REMOTE_ROOT, f"{run_label}_initialized_t0.dat.h5"
            ),
        }
        sweep.write_case_data_pair(
            solver, checkpoint["case"], checkpoint["data"], "07k_initialized_t0"
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
            except Exception:
                pass
            text = sweep.remote_text_read_best_effort(solver, transcript)
            if text:
                (local_root / "preparation_transcript.trn").write_text(
                    text, encoding="utf-8"
                )


if __name__ == "__main__":
    raise SystemExit(main())
