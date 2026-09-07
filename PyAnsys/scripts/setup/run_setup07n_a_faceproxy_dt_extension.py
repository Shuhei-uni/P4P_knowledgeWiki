#!/usr/bin/env python3
"""Run the first conservative time-step extension of the 07n-a face-proxy pilot.

This script cold-loads the checksum-bound setup-07n-a attempt-4 step-10 pair
and changes one item only: physical dt from 1e-6 s to 2e-6 s.  It advances ten
additional guarded physical steps, one per RPC.  The result remains a
diagnostic/unresolved face-proxy startup and cannot promote the pool geometry.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

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

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07l_hydrostatic_rest as rest07l  # noqa: E402
import run_setup07j_transient_vof_qualification as transient07j  # noqa: E402
import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = (
    "brine620k_07n_a_closeddrain_lower_faceproxy_"
    "dt2em6_extension_attempt1_20260822"
)
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_SETTINGS_ROOT = r"C:\Users\qtra338\AppData\Local\Temp"
PARENT_LABEL = "brine620k_07n_a_closeddrain_lower_faceproxy_pilot_attempt4_20260822"
PARENT_CASE = REMOTE_ROOT + rf"\{PARENT_LABEL}_checkpoint_step10.cas.h5"
PARENT_DATA = REMOTE_ROOT + rf"\{PARENT_LABEL}_checkpoint_step10.dat.h5"
EXPECTED_PARENT_CASE_SHA256 = "5a17b9885682761ee60080695fc8b126f87b179aaac562e88d74ed173c4ef19b"
EXPECTED_PARENT_DATA_SHA256 = "29780b1604ad0c7c07d55592db1b599530ebc71265a70f9a01a27643463d0a8d"
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16
INITIAL_TIME_STEP = 10
INITIAL_FLOW_TIME_S = 1.0e-5
TIME_STEP_SIZE_S = 2.0e-6
INNER_ITERATIONS = 20
ADDITIONAL_STEPS = 10
CHECKPOINT_ADDITIONAL_STEPS = {1, 5, 10}
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
GLOBAL_WRITER_LOCK = PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server1_writer.lock"
RUN_CLASSIFICATION = "diagnostic / unresolved lower faceproxy dt extension"
FINAL_CLASSIFICATION = (
    "diagnostic / unresolved lower faceproxy dt2em6 bounded startup"
)
ONE_FACTOR_CHANGE = "physical dt 1e-6 s -> 2e-6 s"
UNCHANGED_CONTRACT = (
    "attempt-4 step-10 field; zero feed; brine wall; steam pressure outlet; "
    "transient explicit VOF; PISO/PRESTO/Geo-Reconstruct/WFGC; RNG k-epsilon; "
    "Energy off; DPM zero/off; EWF off; no sources/sinks"
)
PARENT_ELIGIBILITY_SCOPE = "same faceproxy diagnostic lineage only"
ACCEPTANCE_LIMITATION = (
    "30 us cumulative time is still startup-only and the level is "
    "a boundary-face proxy, not a promoted mesh-resolved pool"
)
NEXT_ELIGIBILITY_SCOPE = (
    "same faceproxy diagnostic lineage, next conservative 2x dt only"
)
SAVE_TAG = "07n_a_dt2em6"
PRINT_LABEL = "07n-a dt extension"
VOF_FORMULATION = "explicit"
EXPECTED_VOF_SCHEME = "geo-reconstruct"
EXPECTED_TRANSIENT_FORMULATION = "unsteady-1st-order"
COURANT_FIELD: str | None = None
ENDPOINT_ELIGIBILITY_ALLOWED = True


class HardGateError(RuntimeError):
    """A numerical or physical failure that makes the extension terminal."""


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("1",), default="1")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def remote_join(name: str) -> str:
    return str(PureWindowsPath(REMOTE_ROOT) / name)


def write_manifest(path: Path, payload: Mapping[str, Any], *, create: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, default=str) + "\n"
    if create:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        return
    fields = sorted({str(key) for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def remote_hash(solver: Any, path: str, label: str) -> dict[str, str]:
    scratch = remote_join(f"_{RUN_LABEL}_{label}_sha256.txt")
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"refusing to overwrite remote hash evidence: {scratch}")
    return {
        "path": path,
        "sha256": mesh_study.remote_file_sha256(solver, path, scratch),
        "scratch": scratch,
    }


def active_settings_gate(solver: Any) -> dict[str, Any]:
    """Validate the active explicit or implicit VOF numerical contract."""

    if VOF_FORMULATION == "explicit":
        return pilot.complete_gate(solver)
    if VOF_FORMULATION != "implicit":
        raise ValueError(f"unsupported VOF formulation: {VOF_FORMULATION}")
    setup = solver.settings.setup
    methods = solver.settings.solution.methods
    method_state = {
        "pressure_velocity_coupling": methods.p_v_coupling.flow_scheme.get_state(),
        "pressure_scheme": methods.discretization_scheme["pressure"].get_state(),
        "volume_fraction_scheme": methods.discretization_scheme["mp"].get_state(),
        "volume_fraction_scheme_allowed_values": list(
            methods.discretization_scheme["mp"].allowed_values()
        ),
        "transient_formulation": methods.transient_formulation.get_state(),
        "warped_face_gradient_correction": (
            methods.warped_face_gradient_correction.get_state()
        ),
        "residual_equations": list(
            solver.settings.solution.monitor.residual.equations.get_object_names()
        ),
        "full_state": methods.get_state(),
    }
    method_state["passed"] = (
        method_state["pressure_velocity_coupling"] == "PISO"
        and method_state["pressure_scheme"] == "presto!"
        and method_state["volume_fraction_scheme"] == EXPECTED_VOF_SCHEME
        and EXPECTED_VOF_SCHEME
        in method_state["volume_fraction_scheme_allowed_values"]
        and method_state["transient_formulation"]
        == EXPECTED_TRANSIENT_FORMULATION
        and bool(method_state["warped_face_gradient_correction"].get("enable"))
        and "vf-phase-2" in method_state["residual_equations"]
    )
    result = {
        "boundary": pilot.boundary_gate(solver),
        "methods": method_state,
        "dpm": pilot.dpm_gate(setup.models.discrete_phase),
        "sources": pilot.source_gate(setup),
        "ewf": pilot.ewf_gate(solver),
        "models": setup.models.get_state(),
        "operating_conditions": setup.general.operating_conditions.get_state(),
    }
    result["passed"] = all(
        bool(result[key].get("passed"))
        for key in ("boundary", "methods", "dpm", "sources", "ewf")
    )
    return result


def apply_formulation_change(solver: Any) -> dict[str, Any]:
    """Apply and prove the requested non-default formulation without solving."""

    if VOF_FORMULATION == "explicit":
        return {"requested": "explicit", "changed": False}
    command = (
        solver.tui.define.models.multiphase.volume_fraction_parameters.formulation
    )
    command_transcript = mesh_study.capture_fluent(
        f"{SAVE_TAG}_set_{VOF_FORMULATION}",
        lambda: mesh_study.call_and_drain(lambda: command(VOF_FORMULATION)),
    )
    transient_setting = solver.settings.solution.methods.transient_formulation
    transient_before = transient_setting.get_state()
    transient_allowed = [str(value) for value in transient_setting.allowed_values()]
    if EXPECTED_TRANSIENT_FORMULATION not in transient_allowed:
        raise RuntimeError(
            "required transient formulation unavailable: "
            f"requested={EXPECTED_TRANSIENT_FORMULATION!r} allowed={transient_allowed}"
        )
    if transient_before != EXPECTED_TRANSIENT_FORMULATION:
        transient_setting.set_state(EXPECTED_TRANSIENT_FORMULATION)
    transient_after = transient_setting.get_state()
    if transient_after != EXPECTED_TRANSIENT_FORMULATION:
        raise RuntimeError(
            "transient-formulation readback mismatch: "
            f"requested={EXPECTED_TRANSIENT_FORMULATION!r} actual={transient_after!r}"
        )
    volume_fraction_setting = (
        solver.settings.solution.methods.discretization_scheme["mp"]
    )
    volume_fraction_before = volume_fraction_setting.get_state()
    volume_fraction_allowed = [
        str(value) for value in volume_fraction_setting.allowed_values()
    ]
    if EXPECTED_VOF_SCHEME not in volume_fraction_allowed:
        raise RuntimeError(
            "required implicit VOF scheme unavailable: "
            f"requested={EXPECTED_VOF_SCHEME!r} allowed={volume_fraction_allowed}"
        )
    if volume_fraction_before != EXPECTED_VOF_SCHEME:
        volume_fraction_setting.set_state(EXPECTED_VOF_SCHEME)
    volume_fraction_after = volume_fraction_setting.get_state()
    if volume_fraction_after != EXPECTED_VOF_SCHEME:
        raise RuntimeError(
            "volume-fraction-scheme readback mismatch: "
            f"requested={EXPECTED_VOF_SCHEME!r} actual={volume_fraction_after!r}"
        )
    remote_path = str(
        PureWindowsPath(REMOTE_SETTINGS_ROOT)
        / f"{RUN_LABEL}_post_formulation_readback.set"
    )
    local_path = LOCAL_ROOT / "post_formulation_readback.set"
    if remote_file_exists(solver, remote_path) or local_path.exists():
        raise FileExistsError("refusing to overwrite formulation readback evidence")
    write_transcript = mesh_study.capture_fluent(
        f"{SAVE_TAG}_write_post_formulation_settings",
        lambda: mesh_study.call_and_drain(
            lambda: solver.tui.file.write_settings(remote_path)
        ),
    )
    text = sweep.remote_text_read_best_effort(solver, remote_path)
    if not text:
        raise RuntimeError("could not retrieve post-formulation settings evidence")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    with local_path.open("x", encoding="utf-8") as stream:
        stream.write(text)
    implicit_marker = bool(
        re.search(r"^\(mp/scheme-type\s+0\)$", text, re.MULTILINE)
    )
    if not implicit_marker:
        raise RuntimeError("post-change settings lack implicit VOF marker")
    scalar_fields = [
        str(value)
        for value in solver.fields.field_data.scalar_fields.allowed_values()
    ]
    courant_fields = [
        value for value in scalar_fields if "courant" in value.lower()
    ]
    if COURANT_FIELD is not None and COURANT_FIELD not in courant_fields:
        raise RuntimeError(
            f"required Courant field {COURANT_FIELD!r} unavailable: {courant_fields}"
        )
    return {
        "requested": VOF_FORMULATION,
        "changed": True,
        "command_transcript": command_transcript,
        "transient_formulation_before": transient_before,
        "transient_formulation_requested": EXPECTED_TRANSIENT_FORMULATION,
        "transient_formulation_after": transient_after,
        "transient_formulation_allowed_values": transient_allowed,
        "volume_fraction_scheme_before": volume_fraction_before,
        "volume_fraction_scheme_requested": EXPECTED_VOF_SCHEME,
        "volume_fraction_scheme_after": volume_fraction_after,
        "volume_fraction_scheme_allowed_values": volume_fraction_allowed,
        "settings_write_transcript": write_transcript,
        "settings_remote": remote_hash(
            solver, remote_path, "post_formulation_settings"
        ),
        "settings_local": str(local_path),
        "implicit_settings_marker": implicit_marker,
        "courant_scalar_fields": courant_fields,
    }


def save_pair(solver: Any, additional_step: int) -> dict[str, Any]:
    label = f"additional_step{additional_step}"
    case = remote_join(f"{RUN_LABEL}_{label}.cas.h5")
    data = remote_join(f"{RUN_LABEL}_{label}.dat.h5")
    if remote_file_exists(solver, case) or remote_file_exists(solver, data):
        raise FileExistsError(f"refusing to overwrite remote checkpoint {label}")
    sweep.write_case_data_pair(solver, case, data, f"{SAVE_TAG}_{label}")
    return {
        "case": remote_hash(solver, case, f"{label}_case"),
        "data": remote_hash(solver, data, f"{label}_data"),
        "eligible_parent": False,
    }


def clock_failures(clock: Mapping[str, Any], additional_step: int) -> list[str]:
    expected_step = INITIAL_TIME_STEP + additional_step
    expected_time = INITIAL_FLOW_TIME_S + additional_step * TIME_STEP_SIZE_S
    failures: list[str] = []
    if int(clock["time_step"]) != expected_step:
        failures.append(
            f"time step expected={expected_step} actual={clock['time_step']}"
        )
    if not math.isclose(
        float(clock["flow_time_s"]),
        expected_time,
        rel_tol=0.0,
        abs_tol=max(1.0e-12, TIME_STEP_SIZE_S * 1.0e-6),
    ):
        failures.append(
            f"flow time expected={expected_time} actual={clock['flow_time_s']}"
        )
    return failures


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    manifest_path = LOCAL_ROOT / "extension_manifest.json"
    physical_path = LOCAL_ROOT / "physical_history.csv"
    residual_path = LOCAL_ROOT / "residual_history.csv"
    transcript_path = LOCAL_ROOT / "extension_transcript.trn"
    local_lock_path = LOCAL_ROOT / "extension_writer.lock"
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite extension: {manifest_path}")

    payload: dict[str, Any] = {
        "schema_version": 1,
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "server_id": args.server_id,
        "status": "running",
        "classification": RUN_CLASSIFICATION,
        "eligible_parent": False,
        "next_dt_extension_eligible": False,
        "one_factor_change": ONE_FACTOR_CHANGE,
        "unchanged_contract": UNCHANGED_CONTRACT,
        "parent": {
            "case": PARENT_CASE,
            "case_expected_sha256": EXPECTED_PARENT_CASE_SHA256,
            "data": PARENT_DATA,
            "data_expected_sha256": EXPECTED_PARENT_DATA_SHA256,
            "eligibility_scope": PARENT_ELIGIBILITY_SCOPE,
        },
        "initial_time_step": INITIAL_TIME_STEP,
        "initial_flow_time_s": INITIAL_FLOW_TIME_S,
        "time_step_size_s": TIME_STEP_SIZE_S,
        "inner_iterations_per_step": INNER_ITERATIONS,
        "target_additional_steps": ADDITIONAL_STEPS,
        "target_final_time_step": INITIAL_TIME_STEP + ADDITIONAL_STEPS,
        "target_final_flow_time_s": (
            INITIAL_FLOW_TIME_S + ADDITIONAL_STEPS * TIME_STEP_SIZE_S
        ),
        "vof_formulation": VOF_FORMULATION,
        "expected_volume_fraction_scheme": EXPECTED_VOF_SCHEME,
        "expected_transient_formulation": EXPECTED_TRANSIENT_FORMULATION,
        "courant_monitor_field": COURANT_FIELD,
        "courant_hard_limit": pilot.MAX_VOF_COURANT,
        "physical_steps_observed": 0,
        "physical_steps_completed": 0,
        "steps": [],
        "checkpoints": {},
        "started_epoch": time.time(),
        "controller_pid": os.getpid(),
    }
    write_manifest(manifest_path, payload, create=True)

    rows: list[dict[str, Any]] = []
    solver: Any | None = None
    transcript_started = False
    transcript_remote = remote_join(f"{RUN_LABEL}_extension.trn")
    try:
        with exclusive_writer_lock(GLOBAL_WRITER_LOCK), exclusive_writer_lock(
            local_lock_path
        ):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                start_transcript=True,
            )
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_parent_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError(f"exclusive ownership unresolved: {clients!r}")
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            if payload["fluent_version"] != EXPECTED_VERSION:
                raise RuntimeError(f"unexpected Fluent version: {payload['fluent_version']}")
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            if not remote_file_exists(solver, PARENT_CASE) or not remote_file_exists(
                solver, PARENT_DATA
            ):
                raise FileNotFoundError("attempt-4 step-10 parent pair is incomplete")
            if remote_file_exists(solver, transcript_remote):
                raise FileExistsError(
                    f"refusing to overwrite remote transcript: {transcript_remote}"
                )
            parent_case_hash = remote_hash(solver, PARENT_CASE, "parent_case")
            parent_data_hash = remote_hash(solver, PARENT_DATA, "parent_data")
            payload["parent_readback"] = {
                "case": parent_case_hash,
                "data": parent_data_hash,
            }
            if parent_case_hash["sha256"] != EXPECTED_PARENT_CASE_SHA256:
                raise RuntimeError("parent case checksum mismatch")
            if parent_data_hash["sha256"] != EXPECTED_PARENT_DATA_SHA256:
                raise RuntimeError("parent data checksum mismatch")

            solver.settings.file.read_case(file_name=PARENT_CASE)
            solver.settings.file.read_data(file_name=PARENT_DATA)
            time.sleep(2.0)
            payload["live_parallel_runtime_after_parent_load"] = (
                require_live_compute_node_count(solver, EXPECTED_RANKS)
            )
            payload["parent_settings_gate"] = pilot.complete_gate(solver)
            if not payload["parent_settings_gate"]["passed"]:
                raise RuntimeError("parent settings gate failed")
            initial_clock = transient07j.runtime_clock(solver)
            payload["parent_clock"] = initial_clock
            if int(initial_clock["time_step"]) != INITIAL_TIME_STEP or not math.isclose(
                float(initial_clock["flow_time_s"]),
                INITIAL_FLOW_TIME_S,
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ):
                raise RuntimeError(f"parent clock mismatch: {initial_clock}")

            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass
            solver.settings.file.start_transcript(file_name=transcript_remote)
            transcript_started = True
            payload["formulation_change_readback"] = apply_formulation_change(solver)
            payload["post_formulation_settings_gate"] = active_settings_gate(solver)
            if not payload["post_formulation_settings_gate"]["passed"]:
                raise RuntimeError("post-formulation settings gate failed")
            controls = solver.settings.solution.run_calculation.transient_controls
            payload["transient_controls_before"] = controls.get_state()
            controls.time_step_size.set_state(TIME_STEP_SIZE_S)
            controls.max_iter_per_time_step.set_state(INNER_ITERATIONS)
            payload["transient_controls_after"] = controls.get_state()
            actual_dt = float(payload["transient_controls_after"]["time_step_size"])
            actual_inner = int(
                payload["transient_controls_after"]["max_iter_per_time_step"]
            )
            if not math.isclose(
                actual_dt, TIME_STEP_SIZE_S, rel_tol=0.0, abs_tol=1.0e-14
            ) or actual_inner != INNER_ITERATIONS:
                raise RuntimeError("transient-control readback mismatch")
            payload["post_change_settings_gate"] = active_settings_gate(solver)
            if not payload["post_change_settings_gate"]["passed"]:
                raise RuntimeError("post-change settings gate failed")

            sweep.configure_residual_history(solver, 10000)
            sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
            parent_metrics = rest07l.physical_metrics(solver, INITIAL_TIME_STEP)
            previous: dict[str, Any] = {
                **parent_metrics,
                **initial_clock,
                **rest07l.inventory(parent_metrics, pilot.DOMAIN_VOLUME_M3),
            }
            payload["parent_physical_metrics"] = {
                **previous,
                **pilot.extrema(solver, "07n_a_dt2em6_parent"),
            }
            if COURANT_FIELD is not None:
                payload["parent_physical_metrics"][
                    "cell_convective_courant_max"
                ] = pilot.report_volume_extreme(
                    solver,
                    COURANT_FIELD,
                    "maximum",
                    f"{SAVE_TAG}_parent_cell_courant_max",
                )
            write_manifest(manifest_path, payload)

            for additional_step in range(1, ADDITIONAL_STEPS + 1):
                total_step = INITIAL_TIME_STEP + additional_step
                started = time.time()
                solver.settings.solution.run_calculation.dual_time_iterate(
                    time_step_count=1,
                    max_iter_per_step=INNER_ITERATIONS,
                )
                clock = transient07j.runtime_clock(solver)
                failures = clock_failures(clock, additional_step)
                if failures:
                    raise HardGateError("; ".join(failures))
                payload["physical_steps_observed"] = additional_step
                payload["last_observed_clock"] = dict(clock)
                payload["last_heartbeat_epoch"] = time.time()
                write_manifest(manifest_path, payload)

                metrics = rest07l.physical_metrics(solver, total_step)
                row: dict[str, Any] = {
                    **metrics,
                    **clock,
                    **rest07l.inventory(metrics, pilot.DOMAIN_VOLUME_M3),
                    **pilot.extrema(
                        solver, f"{SAVE_TAG}_additional_step{additional_step}"
                    ),
                    "additional_step": additional_step,
                }
                row.update(pilot.closed_rest_storage_closure(previous, row))
                transcript_text = sweep.remote_text_read_best_effort(
                    solver, transcript_remote
                )
                if COURANT_FIELD is None:
                    courant_values = rest07l.parse_global_courant(transcript_text)
                    row["latest_global_courant"] = (
                        courant_values[-1] if courant_values else math.nan
                    )
                    row["courant_metric"] = (
                        "Global Courant Number [Explicit VOF Criteria]"
                    )
                else:
                    cell_courant = pilot.report_volume_extreme(
                        solver,
                        COURANT_FIELD,
                        "maximum",
                        f"{SAVE_TAG}_additional_step{additional_step}_cell_courant_max",
                    )
                    row["cell_convective_courant_max"] = cell_courant
                    # Keep the historical key so the proven row gate can apply
                    # the same conservative 0.25 ceiling.  The exact metric is
                    # recorded separately and printed below.
                    row["latest_global_courant"] = cell_courant
                    row["courant_metric"] = "maximum Cell Convective Courant Number"
                residual_last, residual_rows = pilot.latest_residual_row(solver)
                row["end_step_continuity_residual"] = pilot.continuity_value(
                    residual_last
                )
                row["residual_iteration"] = residual_last["iteration"]
                row["wall_seconds"] = time.time() - started
                failures = pilot.row_gate(row, previous, transcript_text)
                complete = active_settings_gate(solver)
                if not complete["passed"]:
                    failures.append(
                        f"DPM/source/EWF/boundary/method gate failed: {complete}"
                    )
                rows.append(row)
                payload["physical_steps_completed"] = additional_step
                payload["steps"].append(
                    {
                        "additional_step": additional_step,
                        "total_time_step": total_step,
                        "metrics": row,
                        "gate_failures": sorted(set(failures)),
                        "checkpoint": None,
                    }
                )
                write_csv(physical_path, rows)
                write_csv(residual_path, residual_rows)
                if failures:
                    write_manifest(manifest_path, payload)
                    raise HardGateError("; ".join(sorted(set(failures))))
                if additional_step in CHECKPOINT_ADDITIONAL_STEPS:
                    checkpoint = save_pair(solver, additional_step)
                    payload["checkpoints"][str(additional_step)] = checkpoint
                    payload["steps"][-1]["checkpoint"] = checkpoint
                write_manifest(manifest_path, payload)
                print(
                    f"{PRINT_LABEL}: "
                    f"additional step {additional_step}/{ADDITIONAL_STEPS}; "
                    f"total step={total_step}; t={clock['flow_time_s']:.6g}s; "
                    f"continuity={row['end_step_continuity_residual']:.6g}; "
                    f"Co={row['latest_global_courant']:.6g}; "
                    f"M_l={row['liquid_inventory_kg']:.9g}kg",
                    flush=True,
                )
                previous = row

            continuity_tail = [
                float(row["end_step_continuity_residual"]) for row in rows[-2:]
            ]
            residual_passed = len(continuity_tail) == 2 and all(
                value <= 0.01 for value in continuity_tail
            )
            payload.update(
                {
                    "status": "completed",
                    "classification": FINAL_CLASSIFICATION,
                    "eligible_parent": False,
                    "next_dt_extension_eligible": (
                        residual_passed and ENDPOINT_ELIGIBILITY_ALLOWED
                    ),
                    "residual_promotion_gate": {
                        "required": (
                            "two consecutive end-step continuity residuals <= 0.01"
                        ),
                        "tail": continuity_tail,
                        "passed": residual_passed,
                    },
                    "acceptance_limitation": ACCEPTANCE_LIMITATION,
                    "completed_epoch": time.time(),
                }
            )
            if residual_passed and ENDPOINT_ELIGIBILITY_ALLOWED:
                endpoint = payload["checkpoints"][str(ADDITIONAL_STEPS)]
                endpoint["eligible_parent"] = True
                endpoint["eligibility_scope"] = NEXT_ELIGIBILITY_SCOPE
            write_manifest(manifest_path, payload)
            return 0
    except HardGateError as exc:
        payload.update(
            {
                "status": "terminal",
                "classification": "terminal diagnostic",
                "eligible_parent": False,
                "next_dt_extension_eligible": False,
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_manifest(manifest_path, payload)
        raise
    except (Exception, KeyboardInterrupt) as exc:
        observed = int(payload.get("physical_steps_observed", 0))
        completed = int(payload.get("physical_steps_completed", 0))
        if observed == 0 and completed == 0:
            stop_status = "stopped_zero_step"
        elif observed > completed:
            stop_status = "stopped_postsolve_monitoring"
        else:
            stop_status = "stopped"
        payload.update(
            {
                "status": stop_status,
                "classification": "diagnostic / unresolved",
                "eligible_parent": False,
                "next_dt_extension_eligible": False,
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_manifest(manifest_path, payload)
        raise
    finally:
        if solver is not None and transcript_started:
            try:
                solver.settings.file.stop_transcript()
                text = sweep.remote_text_read_best_effort(solver, transcript_remote)
                if text and not transcript_path.exists():
                    transcript_path.write_text(text, encoding="utf-8")
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
