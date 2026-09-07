#!/usr/bin/env python3
"""Prepare the clean setup-07g resolved-brine-outlet carrier case.

The script reads the original brine-outlet mesh, normalizes its zone names,
imports the authoritative setup-07 carrier settings, configures the new brine
pressure outlet, verifies every critical setting by readback, hybrid initializes,
and saves an iteration-zero case/data pair.  It never loads a saved solution,
hooks a sink UDF, or runs DPM.
"""

from __future__ import annotations

import copy
import json
import re
import sys
import time
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.mesh_convergence import named_zones  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = "brine620k_07g_pressure_equal_psep_v1"
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_MESH = (
    r"C:\Users\qtra338\Documents\Mesh study\Meshes"
    r"\brine-outlet-620kcells.msh.h5"
)
SETTINGS_FILE = r"C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set"
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
PREFLIGHT = (
    PROJECT_ROOT
    / "output"
    / STUDY_ID
    / "preflight"
    / "preflight_manifest.json"
)
EXPECTED_MESH_SHA256 = "0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394"

ZONE_RENAMES = (
    ("simple-spiral-separator--brine-outlet-", "fluid"),
    ("liquid-inlet", "liquidinlet"),
    ("steam-inlet", "steaminlet"),
    ("steam-outlet", "steamoutlet"),
    ("brine-outlet", "brineoutlet"),
    ("wall", "wall-fluid"),
    (
        "inlet-outer-wall-wall-simple-spiral-separator--brine-outlet-",
        "inlet-outer-wall",
    ),
)


def remote_join(directory: str, name: str) -> str:
    return str(PureWindowsPath(directory) / name)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def ensure_remote_root(solver: Any) -> None:
    if not sweep.ensure_remote_directory_best_effort(solver, REMOTE_ROOT):
        raise RuntimeError(f"could not create remote output directory {REMOTE_ROOT}")


def zone_inventory(solver: Any) -> dict[str, dict[str, str]]:
    boundary = safe_get_state(
        solver.settings.setup.boundary_conditions, "boundary_conditions"
    )
    cell = safe_get_state(
        solver.settings.setup.cell_zone_conditions, "cell_zone_conditions"
    )
    return {
        "faces": named_zones(boundary) if isinstance(boundary, Mapping) else {},
        "cells": named_zones(cell) if isinstance(cell, Mapping) else {},
    }


def rename_zone(solver: Any, old: str, new: str) -> None:
    before = zone_inventory(solver)
    available = set(before["faces"]) | set(before["cells"])
    if new in available and old not in available:
        return
    if old not in available:
        raise RuntimeError(f"zone rename source missing: {old!r}; available={sorted(available)}")
    solver.tui.mesh.modify_zones.zone_name(old, new)
    after = zone_inventory(solver)
    updated = set(after["faces"]) | set(after["cells"])
    if old in updated or new not in updated:
        raise RuntimeError(
            f"zone rename did not read back: {old!r} -> {new!r}; available={sorted(updated)}"
        )


def nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def configure_brine_outlet(solver: Any) -> dict[str, Any]:
    outlets = solver.settings.setup.boundary_conditions.pressure_outlet
    steam_state = outlets["steamoutlet"].get_state()
    brine_state = copy.deepcopy(steam_state)
    phase2 = nested(
        brine_state,
        "phase",
        "phase-2",
        "multiphase",
        "backflow_volume_fraction",
    )
    if not isinstance(phase2, dict):
        raise RuntimeError(
            "brine pressure-outlet state lacks phase-2 backflow-volume-fraction branch"
        )
    phase2["option"] = "value"
    phase2["value"] = 1.0
    outlets["brineoutlet"].set_state(brine_state)

    # Apply the established wall state to the additional inlet-pipe wall zone.
    walls = solver.settings.setup.boundary_conditions.wall
    walls["inlet-outer-wall"].set_state(copy.deepcopy(walls["wall-fluid"].get_state()))
    return {
        "steamoutlet": outlets["steamoutlet"].get_state(),
        "brineoutlet": outlets["brineoutlet"].get_state(),
        "wall-fluid": walls["wall-fluid"].get_state(),
        "inlet-outer-wall": walls["inlet-outer-wall"].get_state(),
    }


def validate_prepared(
    snapshot: Mapping[str, Any], mesh_metrics: Mapping[str, Any]
) -> list[str]:
    errors = mesh_study.validate_settings(
        snapshot, mesh_metrics, require_phase_identity=False
    )
    errors = [
        error
        for error in errors
        if not error.startswith("boundary role 'bottom'")
    ]
    boundary = snapshot.get("boundary_conditions", {})
    brine = nested(boundary, "pressure_outlet", "brineoutlet")
    if brine is None:
        errors.append("brineoutlet is not a pressure outlet")
    expected_pressure = 1120000.0
    pressure = nested(
        brine, "phase", "mixture", "momentum", "gauge_pressure", "value"
    )
    if pressure is None or abs(float(pressure) - expected_pressure) > 1.0e-6:
        errors.append(
            f"brineoutlet gauge pressure expected={expected_pressure} actual={pressure}"
        )
    backflow = nested(
        brine,
        "phase",
        "phase-2",
        "multiphase",
        "backflow_volume_fraction",
        "value",
    )
    if backflow is None or abs(float(backflow) - 1.0) > 1.0e-12:
        errors.append(
            f"brineoutlet liquid backflow volume fraction expected=1.0 actual={backflow}"
        )
    if nested(boundary, "wall", "bottom") is not None:
        errors.append("legacy bottom wall unexpectedly exists in resolved-outlet mesh")
    if nested(boundary, "wall", "wall-fluid") is None:
        errors.append("wall-fluid boundary is missing")
    if nested(boundary, "wall", "inlet-outer-wall") is None:
        errors.append("inlet-outer-wall boundary is missing")
    cells = snapshot.get("cell_zone_conditions", {})
    if nested(cells, "fluid", "fluid") is None:
        errors.append("canonical fluid cell zone is missing")
    sources = nested(cells, "fluid", "fluid", "phase") or {}
    enabled_sources = []
    if isinstance(sources, Mapping):
        for phase, state in sources.items():
            source_state = nested(state, "sources")
            if isinstance(source_state, Mapping) and source_state.get("enable"):
                enabled_sources.append(str(phase))
    if enabled_sources:
        errors.append(f"cell source terms unexpectedly enabled for {enabled_sources}")
    return errors


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = LOCAL_ROOT / "preparation_manifest.json"
    solver = connect(server_id="1")
    ensure_remote_root(solver)
    transcript = remote_join(REMOTE_ROOT, f"{RUN_LABEL}_preparation.trn")
    payload: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "classification": "diagnostic preparation",
        "status": "running",
        "mesh_file": REMOTE_MESH,
        "settings_file": SETTINGS_FILE,
        "saved_solution_data_loaded": False,
        "production_iterations_run": 0,
        "brine_outlet_boundary_condition": {
            "type": "pressure-outlet",
            "gauge_pressure_pa": 1120000.0,
            "phase_2_liquid_backflow_volume_fraction": 1.0,
            "rationale": (
                "same pressure reference as steam outlet for the first drainage "
                "qualification; downstream brine-system pressure is not yet supplied"
            ),
        },
        "dpm": "off; no injections updated or tracked",
        "ewf": "off/not introduced",
        "sink_udf": "not loaded, compiled, or hooked",
        "started_epoch": time.time(),
    }
    try:
        preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
        mesh_metrics = preflight["mesh_metrics"]
        payload["mesh_metrics"] = mesh_metrics
        if preflight.get("mesh_sha256") != EXPECTED_MESH_SHA256:
            raise RuntimeError(
                f"preflight mesh hash mismatch: {preflight.get('mesh_sha256')}"
            )
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
        remote_chdir(solver, str(PureWindowsPath(REMOTE_MESH).parent))
        payload["mesh_load_transcript"] = mesh_study.read_mesh(solver, REMOTE_MESH)
        payload["zone_inventory_before"] = zone_inventory(solver)
        for old, new in ZONE_RENAMES:
            rename_zone(solver, old, new)
        payload["zone_inventory_after_rename"] = zone_inventory(solver)

        payload["settings_import_transcript"] = mesh_study.apply_settings(
            solver, SETTINGS_FILE
        )
        payload["boundary_readback_after_customization"] = configure_brine_outlet(
            solver
        )
        snapshot = mesh_study.capture_settings(solver, REMOTE_ROOT)
        errors = validate_prepared(snapshot, mesh_metrics)
        payload["preinitialization_settings_readback"] = snapshot
        payload["preinitialization_validation_errors"] = errors
        if errors:
            raise RuntimeError("pre-initialization readback failed: " + "; ".join(errors))

        sweep.configure_residual_history(solver, 5000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.maybe_initialize(solver, "hybrid")
        sweep.set_verified_iteration_label(solver, 0)
        initialized = mesh_study.capture_settings(solver, REMOTE_ROOT)
        initialized.update(
            mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT)
        )
        errors = validate_prepared(initialized, mesh_metrics)
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

        checkpoint = {
            "case": remote_join(REMOTE_ROOT, f"{RUN_LABEL}_initialized.cas.h5"),
            "data": remote_join(REMOTE_ROOT, f"{RUN_LABEL}_initialized.dat.h5"),
        }
        sweep.write_case_data_pair(
            solver, checkpoint["case"], checkpoint["data"], "07g_initialized"
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
            remote_join(REMOTE_ROOT, f"{RUN_LABEL}_preparation_manifest.json"),
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
