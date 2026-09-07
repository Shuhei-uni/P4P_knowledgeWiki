#!/usr/bin/env python3
"""Prepare setup 07j from the clean resolved-brine mesh as transient VOF.

This is a source-free carrier-field diagnostic.  It never loads a prior
solution, runs DPM/EWF, hooks the historical sink UDF, or advances physical
time.  The script changes only the formulation needed for the new branch:
transient pressure-based VOF with explicit volume fraction, Geo-Reconstruct,
first-order time for guarded startup, and WFGC on the polyhedral mesh.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
import time
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import (  # noqa: E402
    remote_chdir,
    require_live_compute_node_count,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402

import prepare_setup07g_brine_outlet as base  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = "brine620k_07j_transient_vof_equal_psep_v1"
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_MESH = base.REMOTE_MESH
SETTINGS_FILE = base.SETTINGS_FILE
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
PREFLIGHT = base.PREFLIGHT
EXPECTED_MESH_SHA256 = base.EXPECTED_MESH_SHA256
EXPECTED_COMPUTE_NODES = 16

POOL_LEVEL_Y_M = 0.0
POOL_REGISTER = "setup07j_initial_liquid_pool"
POOL_REGION_MIN_M = (-2.1, -1.5, -1.5)
POOL_REGION_MAX_M = (1.1, POOL_LEVEL_Y_M, 1.1)

VOF_FORMULATION = "explicit"
INTERFACE_MODELING_TYPE = "sharp"
# Fluent 2024 R2's interface-modeling-options TUI uses integer selectors:
# 0 = Sharp, 1 = Sharp/Dispersed, 2 = Dispersed.  The value is accepted only
# when the resulting volume-fraction allowed-values readback contains
# Geo-Reconstruct, so this cannot silently select the wrong regime.
INTERFACE_MODELING_SELECTOR = 0
GENERAL_TIME_VALUE = "unsteady-1st-order"
VOLUME_FRACTION_SCHEME_CANDIDATES = (
    "geo-reconstruct",
    "geometric-reconstruction",
    "Geo-Reconstruct",
)
TRANSIENT_FORMULATION_CANDIDATES = (
    "unsteady-1st-order",
    "first-order-implicit",
    "first-order implicit",
    "First Order Implicit",
)
TIME_STEP_SIZE_S = 1.0e-4
MAX_ITERATIONS_PER_TIME_STEP = 20


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--server-id",
        choices=("1", "2", "3"),
        default="1",
        help=(
            "Configured Fluent server from .env. Server 1 uses FLUENT_IP/PORT/"
            "PASSWORD; server 2 uses the FLUENT_IP2/PORT2/PASSWORD2 keys."
        ),
    )
    return result


def run_label_for_server(server_id: str | int) -> str:
    normalized = str(server_id).strip()
    if normalized not in {"1", "2", "3"}:
        raise ValueError(f"unsupported Fluent server id: {server_id!r}")
    return RUN_LABEL if normalized == "1" else f"{RUN_LABEL}_server{normalized}"


def local_root_for_server(server_id: str | int) -> Path:
    return PROJECT_ROOT / "output" / STUDY_ID / run_label_for_server(server_id)


def remote_join(directory: str, name: str) -> str:
    return str(PureWindowsPath(directory) / name)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def preserve_failed_preparation(manifest_path: Path, local_root: Path = LOCAL_ROOT) -> None:
    if not manifest_path.exists():
        return
    try:
        prior = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if prior.get("status") != "unresolved":
        return
    error = str(prior.get("error", ""))
    if "time' has no attribute 'transient" in error:
        suffix = "attempt1_general_time_value"
    else:
        suffix = f"attempt_{int(time.time())}"
    archived = local_root / f"preparation_manifest_{suffix}.json"
    if not archived.exists():
        shutil.copy2(manifest_path, archived)
    transcript = local_root / "preparation_transcript.trn"
    archived_transcript = local_root / f"preparation_transcript_{suffix}.trn"
    if transcript.exists() and not archived_transcript.exists():
        shutil.copy2(transcript, archived_transcript)


def nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def choose_allowed(setting: Any, candidates: tuple[str, ...], label: str) -> str:
    allowed = [str(value) for value in setting.allowed_values()]
    normalized = {value.lower().replace("_", "-").replace(" ", "-"): value for value in allowed}
    for candidate in candidates:
        key = candidate.lower().replace("_", "-").replace(" ", "-")
        if key in normalized:
            return normalized[key]
    raise RuntimeError(
        f"path/version issue: no supported {label} value matched {candidates}; "
        f"actual allowed values={allowed}"
    )


def configure_transient_vof(solver: Any) -> dict[str, Any]:
    """Change the imported Mixture setup to guarded transient explicit VOF."""

    from ansys.fluent.core.solver import General, Models

    general = General(solver)
    models = Models(solver)
    before = {
        "general": safe_get_state(general, "general-before-vof"),
        "multiphase": safe_get_state(models.multiphase, "multiphase-before-vof"),
    }

    allowed_time_values = [str(value) for value in general.solver.time.allowed_values()]
    if GENERAL_TIME_VALUE not in allowed_time_values:
        raise RuntimeError(
            "path/version issue: Fluent 2024 R2 first-order transient value is "
            f"unavailable; actual={allowed_time_values}"
        )
    general.solver.time = GENERAL_TIME_VALUE
    allowed_models = [str(value) for value in models.multiphase.models.allowed_values()]
    if "vof" not in allowed_models:
        raise RuntimeError(
            f"path/version issue: VOF is unavailable; actual models={allowed_models}"
        )
    models.multiphase.models = "vof"
    formulation_transcript = mesh_study.capture_fluent(
        "setup07j_vof_parameters",
        lambda: mesh_study.call_and_drain(
            lambda: (
                solver.tui.define.models.multiphase.volume_fraction_parameters.formulation(
                    VOF_FORMULATION
                ),
                solver.tui.define.models.multiphase.volume_fraction_parameters.courant_number(
                    0.25
                ),
                solver.tui.define.models.multiphase.volume_fraction_parameters.volume_fraction_cutoff(
                    1.0e-6
                ),
            )
        ),
    )
    body_force_transcript = mesh_study.capture_fluent(
        "setup07j_implicit_body_force",
        lambda: mesh_study.call_and_drain(
            lambda: solver.tui.define.models.multiphase.body_force_formulation("yes")
        ),
    )
    interface_modeling_transcript = mesh_study.capture_fluent(
        "setup07j_sharp_interface_modeling",
        lambda: mesh_study.call_and_drain(
            lambda: solver.tui.define.models.multiphase.interface_modeling_options(
                INTERFACE_MODELING_SELECTOR
            )
        ),
    )

    after = {
        "general": safe_get_state(general, "general-after-vof"),
        "multiphase": safe_get_state(models.multiphase, "multiphase-after-vof"),
    }
    if nested(after, "general", "solver", "time") != GENERAL_TIME_VALUE:
        raise RuntimeError(f"transient solver readback failed: {after['general']}")
    model_value = nested(after, "multiphase", "models")
    if str(model_value).lower() != "vof":
        raise RuntimeError(f"VOF model readback failed: {after['multiphase']}")
    return {
        "before": before,
        "after": after,
        "vof_parameter_command_transcript": formulation_transcript,
        "implicit_body_force_command_transcript": body_force_transcript,
        "interface_modeling_type": INTERFACE_MODELING_TYPE,
        "interface_modeling_selector": INTERFACE_MODELING_SELECTOR,
        "interface_modeling_command_transcript": interface_modeling_transcript,
        "formulation_readback_method": (
            "Geo-Reconstruct availability and persisted mp discretization are "
            "required independently after the explicit-only TUI command"
        ),
    }


def configure_transient_methods(solver: Any) -> dict[str, Any]:
    methods = solver.settings.solution.methods
    before = safe_get_state(methods, "methods-before-07j")

    transient_value = choose_allowed(
        methods.transient_formulation,
        TRANSIENT_FORMULATION_CANDIDATES,
        "transient formulation",
    )
    methods.transient_formulation.set_state(transient_value)

    # discretization_scheme is a non-creatable named object in Fluent 2024 R2.
    # Its active equation names are runtime keys ("mp" for volume fraction),
    # not generated Python attributes.
    mp = methods.discretization_scheme["mp"]
    volume_fraction_value = choose_allowed(
        mp,
        VOLUME_FRACTION_SCHEME_CANDIDATES,
        "VOF spatial-discretization",
    )
    mp.set_state(volume_fraction_value)

    piso = choose_allowed(
        methods.p_v_coupling.flow_scheme,
        ("PISO",),
        "pressure-velocity coupling",
    )
    methods.p_v_coupling.flow_scheme.set_state(piso)

    solver.tui.solve.set.warped_face_gradient_correction.enable("yes", "yes")

    parameters = solver.settings.solution.run_calculation.transient_controls
    parameters.time_step_size.set_state(TIME_STEP_SIZE_S)
    parameters.max_iter_per_time_step.set_state(MAX_ITERATIONS_PER_TIME_STEP)

    after = safe_get_state(methods, "methods-after-07j")
    parameter_after = safe_get_state(parameters, "transient-parameters-after-07j")
    wfgc = methods.warped_face_gradient_correction.get_state()
    if not bool(wfgc.get("enable")):
        raise RuntimeError(f"WFGC did not read back enabled: {wfgc}")
    if nested(after, "transient_formulation") != transient_value:
        raise RuntimeError(
            f"transient formulation setter did not persist: expected={transient_value}, actual={after}"
        )
    if nested(after, "discretization_scheme", "mp") != volume_fraction_value:
        raise RuntimeError(
            f"VOF scheme setter did not persist: expected={volume_fraction_value}, actual={after}"
        )
    if nested(after, "p_v_coupling", "flow_scheme") != piso:
        raise RuntimeError(
            f"PISO setter did not persist: expected={piso}, actual={after}"
        )
    time_step = nested(parameter_after, "time_step_size")
    max_iterations = nested(parameter_after, "max_iter_per_time_step")
    if time_step is None or not math.isclose(
        float(time_step), TIME_STEP_SIZE_S, rel_tol=0.0, abs_tol=1.0e-12
    ):
        raise RuntimeError(f"time-step readback mismatch: {parameter_after}")
    if int(max_iterations or -1) != MAX_ITERATIONS_PER_TIME_STEP:
        raise RuntimeError(f"max-iterations/time-step readback mismatch: {parameter_after}")
    return {
        "before": before,
        "after": after,
        "transient_parameters": parameter_after,
        "transient_formulation": transient_value,
        "volume_fraction_scheme": volume_fraction_value,
        "pressure_velocity_coupling": piso,
        "warped_face_gradient_correction": wfgc,
    }


def create_pool_register(solver: Any) -> dict[str, Any]:
    registers = solver.settings.solution.cell_registers
    existing = registers.get_object_names()
    if POOL_REGISTER in existing:
        registers.delete(name_list=[POOL_REGISTER])
    xmin, ymin, zmin = POOL_REGION_MIN_M
    xmax, ymax, zmax = POOL_REGION_MAX_M
    solver.tui.mesh.adapt.cell_registers.add(
        POOL_REGISTER,
        "type",
        "hexahedron",
        "inside?",
        "yes",
        "max-point",
        xmax,
        ymax,
        zmax,
        "min-point",
        xmin,
        ymin,
        zmin,
    )
    if POOL_REGISTER not in registers.get_object_names():
        raise RuntimeError("setup-07j pool register did not read back")
    return {
        "name": POOL_REGISTER,
        "minimum_m": list(POOL_REGION_MIN_M),
        "maximum_m": list(POOL_REGION_MAX_M),
        "settings_readback": registers[POOL_REGISTER].get_state(),
    }


def patch_pool(solver: Any) -> dict[str, Any]:
    before = mesh_study.volume_scalar(
        solver, REMOTE_ROOT, "07j_pool_vf_before", "phase-2-vof"
    )
    patch = solver.settings.solution.initialization.patch.calculate_patch
    patch(
        domain="phase-2",
        cell_zones=[],
        registers=[POOL_REGISTER],
        variable="mp",
        reference_frame="Relative to Cell Zone",
        use_custom_field_function=False,
        value=1.0,
    )
    after = mesh_study.volume_scalar(
        solver, REMOTE_ROOT, "07j_pool_vf_after", "phase-2-vof"
    )
    if not (math.isfinite(after) and after > before + 1.0e-4 and 0.0 < after < 1.0):
        raise RuntimeError(
            f"setup-07j pool patch failed: before={before}, after={after}"
        )
    return {
        "domain_volume_average_liquid_vf_before": before,
        "domain_volume_average_liquid_vf_after": after,
        "patch_variable": "mp",
        "patch_value": 1.0,
    }


def validate_snapshot(snapshot: Mapping[str, Any], mesh_metrics: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    def expect(path: tuple[str, ...], expected: Any, tolerance: float = 0.0) -> None:
        actual = nested(snapshot, *path)
        if tolerance and actual is not None:
            passed = math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tolerance)
        else:
            passed = actual == expected
        if not passed:
            errors.append(f"{'.'.join(path)} expected={expected!r} actual={actual!r}")

    expect(("general", "solver", "type"), "pressure-based")
    expect(("general", "solver", "time"), GENERAL_TIME_VALUE)
    expect(("general", "operating_conditions", "gravity", "enable"), True)
    expect(("general", "operating_conditions", "gravity", "components"), [0, -9.81, 0])
    expect(("energy", "enabled"), False)
    expect(("multiphase", "models"), "vof")
    expect(("multiphase", "number_of_phases"), 2)
    expect(("viscous", "model"), "k-epsilon")
    expect(("viscous", "k_epsilon_model"), "rng")
    expect(("dpm_interaction", "enabled"), False)
    expect(("phase_materials", "phase-1"), "water-vapor-at-psep")
    expect(("phase_materials", "phase-2"), "water-liquid-at-psep")
    expect(("phase_densities_kg_m3", "phase-1"), 5.797433853149414, 1.0e-5)
    expect(("phase_densities_kg_m3", "phase-2"), 881.2108764648438, 1.0e-5)
    expect(
        (
            "boundary_conditions",
            "mass_flow_inlet",
            "liquidinlet",
            "phase",
            "phase-2",
            "momentum",
            "mass_flow_rate",
            "value",
        ),
        116.92,
        1.0e-8,
    )
    expect(
        (
            "boundary_conditions",
            "mass_flow_inlet",
            "steaminlet",
            "phase",
            "phase-1",
            "momentum",
            "mass_flow_rate",
            "value",
        ),
        80.69,
        1.0e-8,
    )
    for outlet, liquid_backflow in (("steamoutlet", 0.0), ("brineoutlet", 1.0)):
        expect(
            (
                "boundary_conditions",
                "pressure_outlet",
                outlet,
                "phase",
                "mixture",
                "momentum",
                "gauge_pressure",
                "value",
            ),
            1120000.0,
            1.0e-6,
        )
        expect(
            (
                "boundary_conditions",
                "pressure_outlet",
                outlet,
                "phase",
                "phase-2",
                "multiphase",
                "backflow_volume_fraction",
                "value",
            ),
            liquid_backflow,
            1.0e-12,
        )
    if int(mesh_metrics.get("cells", -1)) != 620431:
        errors.append(f"mesh cell count mismatch: {mesh_metrics.get('cells')}")
    return errors


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    run_label = run_label_for_server(args.server_id)
    local_root = local_root_for_server(args.server_id)
    local_root.mkdir(parents=True, exist_ok=True)
    manifest_path = local_root / "preparation_manifest.json"
    preserve_failed_preparation(manifest_path, local_root)
    payload: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": run_label,
        "server_id": args.server_id,
        "connection_environment": (
            "FLUENT_IP/FLUENT_PORT/FLUENT_PASSWORD"
            if args.server_id == "1"
            else (
                f"FLUENT_IP{args.server_id}/FLUENT_PORT{args.server_id}/"
                f"FLUENT_PASSWORD{args.server_id}"
            )
        ),
        "status": "running",
        "classification": "diagnostic preparation",
        "mesh_file": REMOTE_MESH,
        "settings_file": SETTINGS_FILE,
        "saved_solution_data_loaded": False,
        "production_time_steps_run": 0,
        "formulation": {
            "solver": "pressure-based transient",
            "multiphase": "VOF",
            "volume_fraction_formulation": VOF_FORMULATION,
            "interface_modeling_type": INTERFACE_MODELING_TYPE,
            "volume_fraction_scheme": "Geo-Reconstruct (required by readback)",
            "time_step_size_s": TIME_STEP_SIZE_S,
            "max_iterations_per_time_step": MAX_ITERATIONS_PER_TIME_STEP,
            "startup_transient_formulation": "first-order implicit",
            "pressure_velocity_coupling": "PISO",
        },
        "boundary_bracket": {
            "steamoutlet": "pressure outlet, 1.12 MPa, vapor backflow",
            "brineoutlet": "pressure outlet, 1.12 MPa, liquid backflow",
            "qualification": "diagnostic only; downstream brine pressure is not measured",
        },
        "dpm": "off; no injections updated or tracked",
        "ewf": "off/not introduced",
        "sink_udf": "not loaded, compiled, or hooked",
        "started_epoch": time.time(),
    }
    write_json(manifest_path, payload)
    # Fluent's parallel-connectivity report is delivered through PyFluent's
    # transcript stream. Keep it only for the mandatory 16-rank gate, then
    # stop it before the longer preparation RPCs.
    # The project connection helper always authenticates PyFluent with
    # cleanup_on_exit=False; keeping that policy centralized also avoids
    # exposing unsupported wrapper keywords here.
    solver = connect(server_id=args.server_id, start_transcript=True)
    transcript = remote_join(REMOTE_ROOT, f"{run_label}_preparation.trn")
    transcript_started = False
    try:
        payload["required_compute_nodes"] = EXPECTED_COMPUTE_NODES
        payload["live_parallel_runtime"] = require_live_compute_node_count(
            solver, EXPECTED_COMPUTE_NODES
        )
        # Keep this process-scoped stream through the settings import. Fluent
        # 2024 R2 delivers both the import dialogue and its completion through
        # that stream; stopping it here can leave read_settings waiting.
        payload["client_transcript_stream"] = (
            "kept through preparation for settings-import completion/readback"
        )
        preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
        mesh_metrics = preflight["mesh_metrics"]
        payload["mesh_metrics"] = mesh_metrics
        if preflight.get("mesh_sha256") != EXPECTED_MESH_SHA256:
            raise RuntimeError("preflight mesh hash mismatch")
        if not sweep.ensure_remote_directory_best_effort(solver, REMOTE_ROOT):
            raise RuntimeError(f"could not create remote output directory {REMOTE_ROOT}")
        for path, label in (
            (REMOTE_MESH, "resolved brine-outlet mesh"),
            (SETTINGS_FILE, "authoritative setup-07 settings"),
        ):
            mesh_study.require_remote_input(solver, path, label)

        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        transcript_started = True
        remote_chdir(solver, str(PureWindowsPath(REMOTE_MESH).parent))
        payload["mesh_load_transcript"] = mesh_study.read_mesh(solver, REMOTE_MESH)
        payload["zone_inventory_before"] = base.zone_inventory(solver)
        for old, new in base.ZONE_RENAMES:
            base.rename_zone(solver, old, new)
        payload["zone_inventory_after_rename"] = base.zone_inventory(solver)
        payload["settings_import_transcript"] = mesh_study.apply_settings(
            solver, SETTINGS_FILE
        )

        payload["vof_model_change_readback"] = configure_transient_vof(solver)
        payload["boundary_readback"] = base.configure_brine_outlet(solver)
        payload["transient_method_readback"] = configure_transient_methods(solver)

        preinit = mesh_study.capture_settings(solver, REMOTE_ROOT)
        payload["preinitialization_settings_readback"] = preinit
        preinit_errors = validate_snapshot(preinit, mesh_metrics)
        # Phase identity can be hidden until initialization in Fluent 2024 R2.
        preinit_errors = [
            error
            for error in preinit_errors
            if not error.startswith("phase_materials.")
            and not error.startswith("phase_densities_kg_m3.")
        ]
        payload["preinitialization_validation_errors"] = preinit_errors
        if preinit_errors:
            raise RuntimeError(
                "pre-initialization readback failed: " + "; ".join(preinit_errors)
            )

        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.maybe_initialize(solver, "hybrid")
        payload["pool_cell_register_readback"] = create_pool_register(solver)
        payload["pool_patch_readback"] = patch_pool(solver)
        sweep.set_verified_iteration_label(solver, 0)

        initialized = mesh_study.capture_settings(solver, REMOTE_ROOT)
        initialized.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT))
        errors = validate_snapshot(initialized, mesh_metrics)
        payload["initialized_settings_readback"] = initialized
        payload["initialized_validation_errors"] = errors
        payload["full_settings_fingerprint_sha256"] = mesh_study.fingerprint_sha256(
            mesh_study.critical_fingerprint(initialized)
        )
        if errors:
            raise RuntimeError("initialized readback failed: " + "; ".join(errors))

        checkpoint = {
            "case": remote_join(REMOTE_ROOT, f"{run_label}_initialized_t0.cas.h5"),
            "data": remote_join(REMOTE_ROOT, f"{run_label}_initialized_t0.dat.h5"),
        }
        sweep.write_case_data_pair(
            solver, checkpoint["case"], checkpoint["data"], "07j_initialized_t0"
        )
        payload.update(
            {
                "status": "accepted",
                "prepared_checkpoint": checkpoint,
                "completed_epoch": time.time(),
            }
        )
        write_json(manifest_path, payload)
        sweep.remote_text_write_best_effort(
            solver,
            remote_join(REMOTE_ROOT, f"{run_label}_preparation_manifest.json"),
            json.dumps(payload, indent=2, default=str),
        )
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
            transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
            if transcript_text:
                (local_root / "preparation_transcript.trn").write_text(
                    transcript_text, encoding="utf-8"
                )


if __name__ == "__main__":
    raise SystemExit(main())
