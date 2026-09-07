#!/usr/bin/env python3
"""Spatially localize setup-07n matched-endpoint velocity maxima.

This is a post-processing-only server-1 inspection. It checksum-verifies and
cold-loads each matched case/data pair, bisects the fluid cell-centroid domain
with temporary hexahedral cell registers, and records the box containing the
maximum velocity. It never initializes, iterates, changes physics or saves a
case/data field.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path, PureWindowsPath
from typing import Any, Callable

import numpy as np
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from inspect_setup07n_mesh_geometry import (  # noqa: E402
    capture_connected_clients,
    exclusive_writer_lock,
)
from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.mesh_convergence import parse_named_report_rows  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = "brine620k_07n_a_closeddrain_velocity_max_localization_attempt4_20260823"
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
GLOBAL_WRITER_LOCK = PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server1_writer.lock"
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16

ENDPOINTS = [
    {
        "name": "base_dt256em6_inner20",
        "stem": "brine620k_07n_a_closeddrain_matchedwindow_base_dt256em6_steps20_attempt1_20260823_additional_step20",
        "case_sha256": "f2bc7428ce727cc90ed8e98077d5d868b6e3276d4a312bcc89118f281e5d29ec",
        "data_sha256": "bfa4065dbab456ef6aab0407dbae869af68fd01957563eefe6dbb65ee829439e",
    },
    {
        "name": "half_dt128em6_inner20",
        "stem": "brine620k_07n_a_closeddrain_matchedwindow_half_dt128em6_steps40_attempt1_20260823_additional_step40",
        "case_sha256": "a81e5b9582e5b8292dea5bbd5182465fff079f168417e807e1141396e21e9a51",
        "data_sha256": "a47ec7433c0a5ffd761ed3faec337fe0dc96a91a097ac16697316fae4f8b97e7",
    },
    {
        "name": "quarter_dt64em6_inner20",
        "stem": "brine620k_07n_a_closeddrain_matchedwindow_quarter_dt64em6_steps80_attempt1_20260823_additional_step80",
        "case_sha256": "32450dc83c9ed32a23494687d7cc032b576a15d31a5fc12a91ced479f733f064",
        "data_sha256": "8535e5abb3952776ebc7b74034a5109cd8906438ec9d963cb363101af4ae0526",
    },
]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("1",), default="1")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def remote_join(name: str) -> str:
    return str(PureWindowsPath(REMOTE_ROOT) / name)


def write_manifest(path: Path, payload: dict[str, Any], *, create: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, default=str) + "\n"
    if create:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def remote_hash(solver: Any, path: str, label: str) -> dict[str, str]:
    scratch = remote_join(f"_{RUN_LABEL}_{label}_sha256.txt")
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"refusing to overwrite remote hash evidence: {scratch}")
    return {
        "path": path,
        "sha256": mesh_study.remote_file_sha256(solver, path, scratch),
        "scratch": scratch,
    }


def report_value(
    solver: Any,
    mode: str,
    field: str | None,
    label: str,
    *,
    cell_zones: list[str] | None = None,
    volumes: list[str] | None = None,
) -> float:
    reports = solver.settings.results.report.volume_integrals
    command: Callable[..., Any] = getattr(reports, mode)
    names = list(cell_zones or volumes or [])

    def call(path: str) -> Any:
        arguments: dict[str, Any] = {
            "write_to_file": True,
            "file_name": path,
            "append_data": False,
        }
        if cell_zones is not None:
            arguments["cell_zones"] = list(cell_zones)
        if volumes is not None:
            arguments["volumes"] = list(volumes)
        if field is not None:
            arguments["cell_function"] = field
        return command(**arguments)

    text = mesh_study.report_file_text(solver, REMOTE_ROOT, label, call)
    rows = parse_named_report_rows(text, names)
    missing = [name for name in names if name not in rows]
    if missing:
        raise RuntimeError(
            f"could not parse {mode} {field} for {names}; missing={missing}; report={text}"
        )
    return float(rows[names[0]])


def domain_bounds(solver: Any, tag: str) -> tuple[list[float], list[float]]:
    lower = []
    upper = []
    for axis in "xyz":
        field = f"{axis}-coordinate"
        lower.append(
            report_value(
                solver,
                "minimum",
                field,
                f"{RUN_LABEL}_{tag}_{axis}_min",
                cell_zones=["fluid"],
            )
        )
        upper.append(
            report_value(
                solver,
                "maximum",
                field,
                f"{RUN_LABEL}_{tag}_{axis}_max",
                cell_zones=["fluid"],
            )
        )
    return lower, upper


def make_register(solver: Any, name: str, lower: list[float], upper: list[float]) -> None:
    registers = solver.settings.solution.cell_registers
    if name in registers.get_object_names():
        raise FileExistsError(f"temporary register already exists: {name}")
    solver.tui.mesh.adapt.cell_registers.add(
        name,
        "type",
        "hexahedron",
        "inside?",
        "yes",
        "max-point",
        *upper,
        "min-point",
        *lower,
    )
    registers = solver.settings.solution.cell_registers
    if name not in registers.get_object_names():
        raise RuntimeError(f"temporary register was not created: {name}")


def delete_register(solver: Any, name: str) -> None:
    registers = solver.settings.solution.cell_registers
    if name in registers.get_object_names():
        registers.delete(name_list=[name])


def localize(solver: Any, endpoint_index: int, endpoint_name: str) -> dict[str, Any]:
    """Fetch aligned solution-variable cell arrays and identify the maximum."""

    global_max = report_value(
        solver,
        "maximum",
        "velocity-magnitude",
        f"{RUN_LABEL}_{endpoint_name}_global_vmax",
        cell_zones=["fluid"],
    )
    variable_info = solver.fields.solution_variable_info.get_variables_info(
        zone_names=["fluid"], domain_name="mixture"
    )
    variables = variable_info.solution_variables
    result: dict[str, Any] = {
        "global_velocity_max_ms": global_max,
        "solution_variable_candidates": sorted(
            variable
            for variable in variables
            if any(
                token in variable.lower()
                for token in ("cent", "sv_u", "sv_v", "sv_w", "vof", "press", "turb", "visc")
            )
        ),
        "solution_variable_metadata": {},
    }
    required = ("SV_CENTROID", "SV_U", "SV_V", "SV_W")
    missing = [variable for variable in required if variable not in variables]
    if missing:
        raise RuntimeError(f"required solution variables are unavailable: {missing}")

    arrays: dict[str, np.ndarray] = {}
    for variable in required:
        metadata = variable_info[variable]
        raw = solver.fields.solution_variable_data.get_data(
            variable_name=variable,
            zone_names=["fluid"],
            domain_name="mixture",
        )["fluid"]
        values = np.asarray(raw, dtype=float)
        dimension = int(metadata.dimension)
        if dimension > 1:
            values = values.reshape((-1, dimension))
        else:
            values = values.reshape((-1,))
        if values.size == 0 or not np.all(np.isfinite(values)):
            raise RuntimeError(f"invalid solution-variable array: {variable}")
        arrays[variable] = values
        result["solution_variable_metadata"][variable] = {
            "dimension": dimension,
            "shape": list(values.shape),
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
        }

    centroids = arrays["SV_CENTROID"]
    if centroids.ndim != 2 or centroids.shape[1] != 3:
        raise RuntimeError(f"unexpected SV_CENTROID shape: {centroids.shape}")
    components = [arrays["SV_U"], arrays["SV_V"], arrays["SV_W"]]
    counts = {len(centroids), *(len(component) for component in components)}
    if len(counts) != 1:
        raise RuntimeError(f"solution-variable array lengths do not align: {counts}")
    velocity = np.sqrt(sum(component * component for component in components))
    maximum_index = int(np.argmax(velocity))
    fetched_max = float(velocity[maximum_index])
    if not math.isclose(fetched_max, global_max, rel_tol=1.0e-6, abs_tol=1.0e-10):
        raise RuntimeError(
            f"field-data maximum does not match report: fetched={fetched_max} report={global_max}"
        )
    top_indices = np.argsort(velocity)[-20:][::-1]
    result.update(
        {
            "cell_value_count": len(velocity),
            "maximum_array_index": maximum_index,
            "maximum_velocity_ms": fetched_max,
            "maximum_velocity_components_ms": [
                float(component[maximum_index]) for component in components
            ],
            "maximum_cell_centroid_m": [float(value) for value in centroids[maximum_index]],
            "top_20_cells": [
                {
                    "array_index": int(index),
                    "velocity_ms": float(velocity[index]),
                    "centroid_m": [float(value) for value in centroids[index]],
                }
                for index in top_indices
            ],
        }
    )

    optional_specs = (
        ("mixture", "SV_P", "pressure_pa"),
        ("mixture", "SV_MU_T", "turbulent_viscosity_pa_s"),
        ("phase-2", "SV_VOF", "liquid_vof"),
    )
    result["optional_cell_values"] = {}
    result["domain_solution_variable_candidates"] = {}
    for domain, variable, output_name in optional_specs:
        try:
            domain_info = solver.fields.solution_variable_info.get_variables_info(
                zone_names=["fluid"], domain_name=domain
            )
            domain_variables = domain_info.solution_variables
            result["domain_solution_variable_candidates"][domain] = sorted(
                value
                for value in domain_variables
                if any(token in value.lower() for token in ("vof", "sv_p", "vis", "mu_t"))
            )
            if variable not in domain_variables:
                raise RuntimeError(f"{variable} not available in {domain}")
            optional = np.asarray(
                solver.fields.solution_variable_data.get_data(
                    variable_name=variable,
                    zone_names=["fluid"],
                    domain_name=domain,
                )["fluid"],
                dtype=float,
            ).reshape((-1,))
            if len(optional) != len(velocity) or not np.all(np.isfinite(optional)):
                raise RuntimeError(
                    f"unaligned or non-finite {domain}/{variable}: {optional.shape}"
                )
            result["optional_cell_values"][output_name] = {
                "status": "available",
                "value_at_maximum_cell": float(optional[maximum_index]),
                "minimum": float(np.min(optional)),
                "maximum": float(np.max(optional)),
                "top_20_values": [float(optional[index]) for index in top_indices],
            }
        except Exception as exc:
            result["optional_cell_values"][output_name] = {
                "status": "unavailable",
                "error": f"{type(exc).__name__}: {exc}",
            }
    return result


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    manifest_path = LOCAL_ROOT / "localization_manifest.json"
    transcript_path = LOCAL_ROOT / "localization_transcript.trn"
    local_lock_path = LOCAL_ROOT / "localization_writer.lock"
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite localization evidence: {manifest_path}")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "status": "running",
        "classification": "diagnostic / unresolved post-processing localization",
        "localization_method": "aligned solution-variable SV_CENTROID/SV_U/SV_V/SV_W cell arrays",
        "postprocessing_only": True,
        "iterations": 0,
        "initializations": 0,
        "case_data_writes": 0,
        "endpoints": [],
        "controller_pid": os.getpid(),
        "started_epoch": time.time(),
    }
    write_manifest(manifest_path, payload, create=True)
    solver: Any | None = None
    transcript_remote = remote_join(f"{RUN_LABEL}.trn")
    transcript_started = False
    try:
        with exclusive_writer_lock(GLOBAL_WRITER_LOCK), exclusive_writer_lock(local_lock_path):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                start_transcript=True,
            )
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError(f"exclusive ownership unresolved: {clients!r}")
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            if payload["fluent_version"] != EXPECTED_VERSION:
                raise RuntimeError(f"unexpected Fluent version: {payload['fluent_version']}")
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            if remote_file_exists(solver, transcript_remote):
                raise FileExistsError(f"refusing to overwrite transcript: {transcript_remote}")
            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass
            solver.settings.file.start_transcript(file_name=transcript_remote)
            transcript_started = True
            write_manifest(manifest_path, payload)

            for endpoint_index, endpoint in enumerate(ENDPOINTS, start=1):
                case_path = remote_join(endpoint["stem"] + ".cas.h5")
                data_path = remote_join(endpoint["stem"] + ".dat.h5")
                if not remote_file_exists(solver, case_path) or not remote_file_exists(
                    solver, data_path
                ):
                    raise FileNotFoundError(f"endpoint pair is incomplete: {endpoint['name']}")
                case_hash = remote_hash(
                    solver, case_path, f"{endpoint['name']}_case"
                )
                data_hash = remote_hash(
                    solver, data_path, f"{endpoint['name']}_data"
                )
                if case_hash["sha256"] != endpoint["case_sha256"]:
                    raise RuntimeError(f"case checksum mismatch: {endpoint['name']}")
                if data_hash["sha256"] != endpoint["data_sha256"]:
                    raise RuntimeError(f"data checksum mismatch: {endpoint['name']}")
                solver.settings.file.read_case(file_name=case_path)
                solver.settings.file.read_data(file_name=data_path)
                time.sleep(2.0)
                gate = pilot.complete_gate(solver)
                if not gate["passed"]:
                    raise RuntimeError(f"settings gate failed: {endpoint['name']}: {gate}")
                result = {
                    **endpoint,
                    "case_readback": case_hash,
                    "data_readback": data_hash,
                    "settings_gate": gate,
                    "localization": localize(solver, endpoint_index, endpoint["name"]),
                }
                payload["endpoints"].append(result)
                payload["last_completed_endpoint"] = endpoint["name"]
                payload["last_heartbeat_epoch"] = time.time()
                write_manifest(manifest_path, payload)
                print(
                    f"localized {endpoint['name']}: "
                    f"vmax={result['localization']['global_velocity_max_ms']:.9g}; "
                    f"centroid={result['localization']['maximum_cell_centroid_m']}",
                    flush=True,
                )

            locations = [
                item["localization"]["maximum_cell_centroid_m"]
                for item in payload["endpoints"]
            ]
            indices = [
                item["localization"]["maximum_array_index"]
                for item in payload["endpoints"]
            ]
            payload["same_maximum_cell_index"] = len(set(indices)) == 1
            payload["same_maximum_cell_centroid"] = all(
                location == locations[0] for location in locations[1:]
            )
            payload.update(
                {
                    "status": "completed",
                    "classification": "accepted diagnostic / velocity-maximum localization",
                    "completed_epoch": time.time(),
                    "eligible_parent": False,
                }
            )
            write_manifest(manifest_path, payload)
            return 0
    except (Exception, KeyboardInterrupt) as exc:
        payload.update(
            {
                "status": "stopped",
                "classification": "diagnostic / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
                "eligible_parent": False,
            }
        )
        write_manifest(manifest_path, payload)
        raise
    finally:
        if solver is not None:
            if transcript_started:
                try:
                    solver.settings.file.stop_transcript()
                except Exception:
                    pass
            try:
                transcript_text = sweep.remote_text_read_best_effort(
                    solver, transcript_remote
                )
                if transcript_text and not transcript_path.exists():
                    transcript_path.parent.mkdir(parents=True, exist_ok=True)
                    with transcript_path.open("x", encoding="utf-8") as stream:
                        stream.write(transcript_text)
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
