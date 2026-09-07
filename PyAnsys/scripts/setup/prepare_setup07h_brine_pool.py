#!/usr/bin/env python3
"""Prepare setup 07h from the clean brine-outlet mesh with a lower liquid pool."""

from __future__ import annotations

import json
import math
import shutil
import sys
import time
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
RUN_LABEL = "brine620k_07h_pool_y0_equal_psep_v1"
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_MESH = base.REMOTE_MESH
SETTINGS_FILE = base.SETTINGS_FILE
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
PREFLIGHT = base.PREFLIGHT
EXPECTED_MESH_SHA256 = base.EXPECTED_MESH_SHA256
POOL_LEVEL_Y_M = 0.0
POOL_REGISTER = "setup07h_initial_liquid_pool"
POOL_REGION_MIN_M = (-2.1, -1.5, -1.5)
POOL_REGION_MAX_M = (1.1, POOL_LEVEL_Y_M, 1.1)
ENABLE_WFGC = False
EXPECTED_COMPUTE_NODES = 16


def remote_join(directory: str, name: str) -> str:
    return str(PureWindowsPath(directory) / name)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def preserve_failed_preparation_attempt(manifest_path: Path) -> None:
    """Keep each known failed patch attempt before a clean retry."""

    if not manifest_path.exists():
        return
    try:
        prior = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if prior.get("status") != "unresolved":
        return
    error = str(prior.get("error", ""))
    if "pool patch did not create a bounded lower liquid inventory" in error:
        suffix = "attempt1_inactive_expression_patch"
    elif "phase-2 patch variable 'mp' is unavailable; actual=[]" in error:
        suffix = "attempt2_empty_dynamic_allowed_values"
    else:
        return
    archived_manifest = LOCAL_ROOT / f"preparation_manifest_{suffix}.json"
    if not archived_manifest.exists():
        shutil.copy2(manifest_path, archived_manifest)
    transcript = LOCAL_ROOT / "preparation_transcript.trn"
    archived_transcript = LOCAL_ROOT / f"preparation_transcript_{suffix}.trn"
    if transcript.exists() and not archived_transcript.exists():
        shutil.copy2(transcript, archived_transcript)


def create_pool_register(solver: Any) -> dict[str, Any]:
    """Create a hexahedral cell register spanning the mesh below y=0 m."""

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
    updated = registers.get_object_names()
    if POOL_REGISTER not in updated:
        raise RuntimeError(
            f"requires TUI fallback: region register creation did not read back; actual={updated}"
        )
    return {
        "name": POOL_REGISTER,
        "type": "hexahedron",
        "inside": True,
        "minimum_m": list(POOL_REGION_MIN_M),
        "maximum_m": list(POOL_REGION_MAX_M),
        "settings_readback": registers[POOL_REGISTER].get_state(),
    }


def patch_pool(solver: Any) -> dict[str, Any]:
    before = mesh_study.volume_scalar(
        solver, REMOTE_ROOT, "07h_pool_vf_before", "phase-2-vof"
    )
    patch = solver.settings.solution.initialization.patch.calculate_patch
    allowed_variables = list(patch.variable.allowed_values())
    allowed_registers = list(patch.registers.allowed_values())
    # Fluent 2024 R2 can return an empty dynamic allowed-values list for this
    # command even though ``mp`` and the existing register are valid command
    # arguments.  The authoritative gates are therefore the register settings
    # readback above and the bounded post-patch phase-volume-fraction readback
    # below, not the optional dynamic metadata.
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
        solver, REMOTE_ROOT, "07h_pool_vf_after", "phase-2-vof"
    )
    if not (math.isfinite(after) and after > before + 1.0e-4 and 0.0 < after < 1.0):
        raise RuntimeError(
            f"pool patch did not create a bounded lower liquid inventory: before={before}, after={after}"
        )
    return {
        "cell_register": POOL_REGISTER,
        "selected_patch_variable": "mp",
        "patch_value": 1.0,
        "allowed_patch_variables": allowed_variables,
        "allowed_patch_registers": allowed_registers,
        "domain_volume_average_liquid_vf_before": before,
        "domain_volume_average_liquid_vf_after": after,
    }


def configure_warped_face_gradient_correction(solver: Any) -> dict[str, Any]:
    """Apply the optional one-factor polyhedral-mesh numerical sensitivity."""

    methods = solver.settings.solution.methods
    before = methods.warped_face_gradient_correction.get_state()
    if ENABLE_WFGC:
        solver.tui.solve.set.warped_face_gradient_correction.enable("yes", "yes")
    after = methods.warped_face_gradient_correction.get_state()
    expected = bool(ENABLE_WFGC)
    if bool(after.get("enable")) is not expected:
        raise RuntimeError(
            "warped-face gradient correction readback mismatch: "
            f"expected={expected}, actual={after}"
        )
    return {
        "requested_enable": expected,
        "requested_mode": "fast" if expected else "unchanged/disabled",
        "before": before,
        "after": after,
    }


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = LOCAL_ROOT / "preparation_manifest.json"
    preserve_failed_preparation_attempt(manifest_path)
    print(f"setup-{RUN_LABEL}: connecting to Fluent", flush=True)
    solver = connect(server_id="1")
    print(f"setup-{RUN_LABEL}: connected", flush=True)
    transcript = remote_join(REMOTE_ROOT, f"{RUN_LABEL}_preparation.trn")
    transcript_started = False
    payload: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "classification": "diagnostic preparation",
        "status": "running",
        "mesh_file": REMOTE_MESH,
        "settings_file": SETTINGS_FILE,
        "saved_solution_data_loaded": False,
        "production_iterations_run": 0,
        "initial_liquid_pool": {
            "level_y_m": POOL_LEVEL_Y_M,
            "rationale": (
                "brine face centroid y=-0.25417245 m and equivalent circular "
                "radius about 0.252 m place the pipe crown near y=0 m"
            ),
            "evidence_class": "geometry-derived inference",
        },
        "outlets": {
            "steamoutlet_pressure_pa": 1120000.0,
            "brineoutlet_pressure_pa": 1120000.0,
            "pressure_note": (
                "Fluent gravity-modified pressure inputs exclude manually added "
                "hydrostatic head"
            ),
        },
        "dpm": "off; no injections updated or tracked",
        "ewf": "off/not introduced",
        "sink_udf": "not loaded, compiled, or hooked",
        "started_epoch": time.time(),
    }
    try:
        print(f"setup-{RUN_LABEL}: verifying live compute-node count", flush=True)
        payload["required_compute_nodes"] = EXPECTED_COMPUTE_NODES
        payload["live_parallel_runtime"] = require_live_compute_node_count(
            solver, EXPECTED_COMPUTE_NODES
        )
        payload["live_compute_nodes"] = payload["live_parallel_runtime"][
            "compute_node_count"
        ]
        print(f"setup-{RUN_LABEL}: checking remote output directory", flush=True)
        if not sweep.ensure_remote_directory_best_effort(solver, REMOTE_ROOT):
            raise RuntimeError(f"could not create remote output directory {REMOTE_ROOT}")
        print(f"setup-{RUN_LABEL}: validating local preflight and remote inputs", flush=True)
        preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
        mesh_metrics = preflight["mesh_metrics"]
        payload["mesh_metrics"] = mesh_metrics
        if preflight.get("mesh_sha256") != EXPECTED_MESH_SHA256:
            raise RuntimeError("preflight mesh hash mismatch")
        for path, label in (
            (REMOTE_MESH, "resolved brine-outlet mesh"),
            (SETTINGS_FILE, "authoritative setup-07 settings"),
        ):
            mesh_study.require_remote_input(solver, path, label)

        # The useful 07g state is already preserved at verified iteration 500.
        # Do not duplicate the later overflow-scale live field: its attempted
        # write blocked Fluent and carries no additional physical evidence.
        payload["prior_live_state_handling"] = {
            "saved_again": False,
            "reason": "overflow-scale divergent field; verified 07g iter500 pair already exists",
        }

        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        print(f"setup-{RUN_LABEL}: starting transcript and loading clean mesh", flush=True)
        solver.settings.file.start_transcript(file_name=transcript)
        transcript_started = True
        remote_chdir(solver, str(PureWindowsPath(REMOTE_MESH).parent))
        payload["mesh_load_transcript"] = mesh_study.read_mesh(solver, REMOTE_MESH)
        payload["zone_inventory_before"] = base.zone_inventory(solver)
        for old, new in base.ZONE_RENAMES:
            base.rename_zone(solver, old, new)
        payload["zone_inventory_after_rename"] = base.zone_inventory(solver)

        print(f"setup-{RUN_LABEL}: clean mesh loaded; importing authoritative settings", flush=True)
        payload["settings_import_transcript"] = mesh_study.apply_settings(
            solver, SETTINGS_FILE
        )
        print(f"setup-{RUN_LABEL}: settings imported; configuring WFGC and brine outlet", flush=True)
        payload["warped_face_gradient_correction"] = (
            configure_warped_face_gradient_correction(solver)
        )
        payload["boundary_readback_after_customization"] = base.configure_brine_outlet(
            solver
        )
        before_init = mesh_study.capture_settings(solver, REMOTE_ROOT)
        errors = base.validate_prepared(before_init, mesh_metrics)
        payload["preinitialization_settings_readback"] = before_init
        payload["preinitialization_validation_errors"] = errors
        operating_density = (
            before_init.get("general", {})
            .get("operating_conditions", {})
            .get("operating_density", {})
            .get("method")
        )
        if operating_density != "minimum-phase-averaged":
            errors.append(
                f"operating density must be minimum-phase-averaged; actual={operating_density}"
            )
        if errors:
            raise RuntimeError("pre-initialization readback failed: " + "; ".join(errors))

        print(f"setup-{RUN_LABEL}: pre-initialization readback accepted; initializing", flush=True)
        sweep.configure_residual_history(solver, 5000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.maybe_initialize(solver, "hybrid")
        payload["pool_cell_register_readback"] = create_pool_register(solver)
        payload["pool_patch_readback"] = patch_pool(solver)
        sweep.set_verified_iteration_label(solver, 0)

        initialized = mesh_study.capture_settings(solver, REMOTE_ROOT)
        initialized.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT))
        errors = base.validate_prepared(initialized, mesh_metrics)
        errors.extend(
            error
            for error in mesh_study.validate_settings(
                initialized, mesh_metrics, require_phase_identity=True
            )
            if error not in errors and not error.startswith("boundary role 'bottom'")
        )
        payload["initialized_settings_readback"] = initialized
        payload["initialized_validation_errors"] = errors
        payload["full_settings_fingerprint_sha256"] = mesh_study.fingerprint_sha256(
            mesh_study.critical_fingerprint(initialized)
        )
        if errors:
            raise RuntimeError("initialized readback failed: " + "; ".join(errors))

        print(f"setup-{RUN_LABEL}: pool patch accepted; writing initialized checkpoint", flush=True)
        checkpoint = {
            "case": remote_join(REMOTE_ROOT, f"{RUN_LABEL}_initialized_pool.cas.h5"),
            "data": remote_join(REMOTE_ROOT, f"{RUN_LABEL}_initialized_pool.dat.h5"),
        }
        sweep.write_case_data_pair(
            solver, checkpoint["case"], checkpoint["data"], f"{RUN_LABEL}_initialized_pool"
        )
        payload.update(
            {"status": "accepted", "prepared_checkpoint": checkpoint, "completed_epoch": time.time()}
        )
        write_json(manifest_path, payload)
        sweep.remote_text_write_best_effort(
            solver,
            remote_join(REMOTE_ROOT, f"{RUN_LABEL}_preparation_manifest.json"),
            json.dumps(payload, indent=2, default=str),
        )
        print(f"setup-{RUN_LABEL}: preparation accepted", flush=True)
        return 0
    except Exception as exc:
        payload.update(
            {"status": "unresolved", "error": f"{type(exc).__name__}: {exc}", "completed_epoch": time.time()}
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
                (LOCAL_ROOT / "preparation_transcript.trn").write_text(
                    text, encoding="utf-8"
                )


if __name__ == "__main__":
    raise SystemExit(main())
