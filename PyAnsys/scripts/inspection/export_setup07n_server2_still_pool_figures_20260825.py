#!/usr/bin/env python3
"""Export non-mutating contours for the independent server-2 still-pool test.

The accepted historical setup-07l step-10 pair is on server 1.  This script
therefore exports only the separately checksum-bound server-2 setup-07n
reconstruction at time zero, 10 microseconds and the last clean independent
step-90 endpoint.  It does not initialize, iterate, update DPM, or write
case/data files.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INSPECTION_DIR = PROJECT_ROOT / "scripts" / "inspection"
SETUP_DIR = PROJECT_ROOT / "scripts" / "setup"
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(INSPECTION_DIR))
sys.path.insert(0, str(SETUP_DIR))

import export_setup07_meeting_graphics as graphics_base  # noqa: E402
import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
from inspect_setup07n_mesh_geometry import (  # noqa: E402
    capture_connected_clients,
    exclusive_writer_lock,
)
from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
)
from pyansys_fluent.connection import connect  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = "brine620k_07n_a_server2_independent_stillpool_figures_attempt1_20260825"
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_OUTPUT = rf"C:\Users\qtra338\Documents\Mesh study\{RUN_LABEL}"
LOCAL_OUTPUT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
MANIFEST_PATH = LOCAL_OUTPUT / "graphics_manifest.json"
LOCK_PATH = PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server2_independent_writer.lock"
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16


def remote_path(stem: str, suffix: str) -> str:
    return str(PureWindowsPath(REMOTE_ROOT) / f"{stem}.{suffix}")


STATES: list[dict[str, Any]] = [
    {
        "key": "t0",
        "title": "Independent server-2 patched pool at t=0",
        "flow_time_s": 0.0,
        "stem": (
            "brine620k_07n_a_closeddrain_meshselected_"
            "server2_independent_startup_attempt2_20260824_time_zero"
        ),
        "case_sha256": "7fe9ca8243062b7f633b625886363dbc2fd4801b94015d06eaa82e0112ae824c",
        "data_sha256": "e8b589e1b3514bc063fffedb209eb3b72cc45eec11992d3c9d7603a299a908c4",
    },
    {
        "key": "startup_step10_10us",
        "title": "Independent server-2 micro-startup step 10 at t=10 us",
        "flow_time_s": 1.0e-5,
        "stem": (
            "brine620k_07n_a_closeddrain_meshselected_"
            "server2_independent_startup_attempt2_20260824_checkpoint_step10"
        ),
        "case_sha256": "ed6eefafbefe6296ece5a702c26a7f243d8cb046884bd70d56c02a50f6addbaf",
        "data_sha256": "844f0ca3ef6600150b7b0d2cb9e65484a11b0c5341c4b2b1b7e3ec0a2c2ba65b",
    },
    {
        "key": "lastclean_step90_5p11ms",
        "title": "Independent server-2 last-clean endpoint step 90 at t=5.11 ms",
        "flow_time_s": 0.00511,
        "stem": (
            "brine620k_07n_a_closeddrain_meshselected_"
            "server2_independent_dt256em6_attempt1_20260824_additional_step10"
        ),
        "case_sha256": "763fae763ce43c36505c7dc06986082f361e257c93afc778b5583a41dd15fd22",
        "data_sha256": "9513a957ae42e59db076466754a226c44b7bfdfa7f8a69b40e44139fa2bae6b7",
    },
]

PLANES = {
    "vessel_axis_xm1p5": -1.5,
    "brine_axis_x0p714343": 0.7143434057,
}

FIELD_RANGES = {
    "phase-2-vof": (0.0, 1.0),
    "pressure": (1_120_000.0, 1_133_000.0),
}


def local_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(payload: dict[str, Any], *, create: bool = False) -> None:
    text = json.dumps(payload, indent=2, default=str) + "\n"
    if create:
        LOCAL_OUTPUT.mkdir(parents=True, exist_ok=False)
        with MANIFEST_PATH.open("x", encoding="utf-8") as stream:
            stream.write(text)
        return
    temporary = MANIFEST_PATH.with_suffix(".json.tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, MANIFEST_PATH)


def remote_hash(solver: Any, path: str, label: str) -> dict[str, str]:
    scratch = str(PureWindowsPath(REMOTE_ROOT) / f"_{RUN_LABEL}_{label}_sha256.txt")
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"refusing to overwrite remote hash evidence: {scratch}")
    return {
        "path": path,
        "sha256": mesh_study.remote_file_sha256(solver, path, scratch),
        "scratch": scratch,
    }


def state_paths(state: dict[str, Any]) -> tuple[str, str]:
    return remote_path(str(state["stem"]), "cas.h5"), remote_path(
        str(state["stem"]), "dat.h5"
    )


def verify_state_files(solver: Any, state: dict[str, Any]) -> dict[str, Any]:
    case_path, data_path = state_paths(state)
    for path in (case_path, data_path):
        if not remote_file_exists(solver, path):
            raise FileNotFoundError(f"required remote checkpoint is missing: {path}")
    case_hash = remote_hash(solver, case_path, f"{state['key']}_case")
    data_hash = remote_hash(solver, data_path, f"{state['key']}_data")
    if case_hash["sha256"] != state["case_sha256"]:
        raise RuntimeError(f"case checksum mismatch for {state['key']}")
    if data_hash["sha256"] != state["data_sha256"]:
        raise RuntimeError(f"data checksum mismatch for {state['key']}")
    return {"case": case_hash, "data": data_hash}


def phase_identity(solver: Any) -> dict[str, Any]:
    species = solver.settings.setup.models.species.model.get_state()
    materials = species.get("phase_material", {}) if isinstance(species, dict) else {}
    result = {
        "phase_1": materials.get("phase-1"),
        "phase_2": materials.get("phase-2"),
    }
    result["passed"] = (
        result["phase_1"] == "water-vapor-at-psep"
        and result["phase_2"] == "water-liquid-at-psep"
    )
    return result


def clean_image_record(record: dict[str, Any]) -> dict[str, Any]:
    picture = record.get("picture", {})
    local_png_text = picture.get("local_png")
    if picture.get("ok") and local_png_text:
        local_png = Path(local_png_text)
        picture["local_sha256"] = local_sha256(local_png)
        picture["local_size_bytes"] = local_png.stat().st_size
    record["picture"] = picture
    return record


def export_contour(
    solver: Any,
    graphics: Any,
    *,
    state_key: str,
    plane_key: str,
    plane_x: float,
    field: str,
    minimum: float,
    maximum: float,
    range_label: str,
) -> dict[str, Any]:
    graphics_base.PLANE_NAME = f"{RUN_LABEL}_{plane_key}"
    graphics_base.PLANE_X_M = plane_x
    plane_state = graphics_base.create_longitudinal_plane(solver)
    graphics = solver.settings.results.graphics
    output_stem = f"{state_key}_{plane_key}_{field.replace('-', '_')}_{range_label}"
    record = graphics_base.make_contour(
        solver,
        graphics,
        state_key=f"{RUN_LABEL}_{state_key}_{plane_key}_{range_label}",
        field=field,
        minimum=minimum,
        maximum=maximum,
        output_stem=output_stem,
        local_dir=LOCAL_OUTPUT,
        remote_dir=REMOTE_OUTPUT,
    )
    record["plane"] = {"key": plane_key, "x_m": plane_x, "state": plane_state}
    return clean_image_record(record)


def export_state(solver: Any, state: dict[str, Any]) -> dict[str, Any]:
    case_path, data_path = state_paths(state)
    solver.settings.file.read_case(file_name=case_path)
    solver.settings.file.read_data(file_name=data_path)
    time.sleep(1.0)
    gate = pilot.complete_gate(solver)
    identity = phase_identity(solver)
    if not gate.get("passed") or not identity.get("passed"):
        raise RuntimeError(
            f"loaded-state readback failed for {state['key']}: "
            f"gate={gate.get('passed')} identity={identity}"
        )

    actions: list[dict[str, Any]] = []
    graphics = graphics_base.activate_window(solver, actions)
    result: dict[str, Any] = {
        "title": state["title"],
        "flow_time_s": state["flow_time_s"],
        "case": case_path,
        "data": data_path,
        "complete_gate": gate,
        "phase_identity": identity,
        "actions": actions,
        "graphics": {},
    }

    for plane_key, plane_x in PLANES.items():
        result["graphics"][f"{plane_key}_liquid_vf"] = export_contour(
            solver,
            graphics,
            state_key=str(state["key"]),
            plane_key=plane_key,
            plane_x=plane_x,
            field="phase-2-vof",
            minimum=0.0,
            maximum=1.0,
            range_label="range0to1",
        )

    result["graphics"]["brine_axis_pressure"] = export_contour(
        solver,
        graphics,
        state_key=str(state["key"]),
        plane_key="brine_axis_x0p714343",
        plane_x=PLANES["brine_axis_x0p714343"],
        field="pressure",
        minimum=FIELD_RANGES["pressure"][0],
        maximum=FIELD_RANGES["pressure"][1],
        range_label="range1120to1133kpa",
    )

    if state["key"] == "startup_step10_10us":
        velocity_max = 7.0e-5
        velocity_label = "range0to7em5ms"
    elif state["key"] == "lastclean_step90_5p11ms":
        velocity_max = 0.025
        velocity_label = "range0to0p025ms"
    else:
        velocity_max = 7.0e-5
        velocity_label = "range0to7em5ms"
    result["graphics"]["brine_axis_velocity"] = export_contour(
        solver,
        graphics,
        state_key=str(state["key"]),
        plane_key="brine_axis_x0p714343",
        plane_x=PLANES["brine_axis_x0p714343"],
        field="velocity-magnitude",
        minimum=0.0,
        maximum=velocity_max,
        range_label=velocity_label,
    )
    return result


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_label": RUN_LABEL,
        "status": "running",
        "classification": "diagnostic post-processing only",
        "authoritative_lineage": False,
        "server_id": "2",
        "started_epoch": time.time(),
        "postprocessing_only": True,
        "no_initialization": True,
        "no_iterations": True,
        "no_case_data_writes": True,
        "dpm_update_run": False,
        "scope_limitation": (
            "Independent server-2 setup-07n reconstruction; not accepted "
            "setup-07l step 10 and not authoritative server-1 step 940."
        ),
        "states": {},
    }
    write_manifest(payload, create=True)
    with exclusive_writer_lock(LOCK_PATH):
        solver = connect(server_id="2", tcp_timeout_seconds=5.0, start_transcript=True)
        clients = capture_connected_clients(solver)
        payload["connected_clients_before_load"] = clients
        if "No client is connected to server." not in clients:
            raise RuntimeError(f"exclusive ownership unresolved: {clients!r}")
        payload["health_status"] = str(solver.health_check.status())
        payload["fluent_version"] = str(solver.get_fluent_version())
        if payload["fluent_version"] != EXPECTED_VERSION:
            raise RuntimeError(
                f"expected {EXPECTED_VERSION}, got {payload['fluent_version']}"
            )
        payload["live_parallel_runtime"] = require_live_compute_node_count(
            solver, EXPECTED_RANKS
        )
        graphics_base.ensure_remote_directory(solver, REMOTE_OUTPUT)

        for state in STATES:
            key = str(state["key"])
            payload["states"][key] = {
                "source": dict(state),
                "remote_hashes": verify_state_files(solver, state),
            }
            write_manifest(payload)
            payload["states"][key]["export"] = export_state(solver, state)
            write_manifest(payload)

        # Deliberately leave the last clean independent step-90 pair resident.
        # The terminal 512-us field is not loaded or restored.
        payload["resident_state_after_export"] = STATES[-1]["key"]
        payload["status"] = "completed"
        payload["completed_epoch"] = time.time()
        write_manifest(payload)

    print(MANIFEST_PATH)
    print("Post-processing only: no initialization, iterations, DPM update, or case/data write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
