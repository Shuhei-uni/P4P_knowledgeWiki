#!/usr/bin/env python3
"""Run matched zero-feed and full-feed one-step setup-07n pulses on server 2.

Both members cold-load the accepted setup-07n-c centre step-10 checkpoint,
use explicit VOF/PISO at ``dt=1e-7 s`` and 100 inner iterations, and differ
only in inlet phase mass flow.  Every output is non-resumable and
non-promotable by design.
"""

from __future__ import annotations

import csv
import json
import math
import os
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
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
from pyansys_fluent.common import remote_file_exists, require_live_compute_node_count  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07l_hydrostatic_rest as rest07l  # noqa: E402
import run_setup07j_transient_vof_qualification as transient07j  # noqa: E402
import run_setup07m_pressure_opening_campaign as opening07m  # noqa: E402
import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402
import run_setup07n_c_pressure_response_sign_probe as pressure_probe  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = (
    "brine620k_07n_server2_centre_matched_zero_vs_fullfeed_"
    "dt1em7_inner100_one_step_attempt1_20260825"
)
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
PARENT_STEM = (
    "brine620k_07n_c_server2_independent_step90_zero_feed_pressure_bracket_"
    "dt256em6_steps10_attempt2_20260825_centre_additional_step10"
)
PARENT_CASE = REMOTE_ROOT + rf"\{PARENT_STEM}.cas.h5"
PARENT_DATA = REMOTE_ROOT + rf"\{PARENT_STEM}.dat.h5"
PARENT_CASE_SHA256 = "bacf0d22343c933b3d87ee806e6b233152f76aa17f0e76519b9723cb5f2ea198"
PARENT_DATA_SHA256 = "0c000fc3715210936fe1d6793102e173694d6dd694f9bb78bd64024be35290a7"
PARENT_STEP = 100
PARENT_FLOW_TIME_S = 0.007670000000000005
BRINE_PRESSURE_PA = 1_122_349.5
TIME_STEP_SIZE_S = 1.0e-7
INNER_ITERATIONS = 100
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16
MAX_VOF_COURANT = 0.25
MAX_PRESSURE_PA = 1.0e7
MAX_VELOCITY_M_S = 100.0
MAX_STORAGE_CLOSURE_KG_S = 5.0
DOMAIN_VOLUME_M3 = pilot.DOMAIN_VOLUME_M3
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
CAMPAIGN_MANIFEST = LOCAL_ROOT / "campaign_manifest.json"
GLOBAL_WRITER_LOCK = (
    PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server2_independent_writer.lock"
)
MEMBERS = (
    ("zero_feed", 0.0),
    ("full_feed", 1.0),
)


def write_json(path: Path, payload: Mapping[str, Any], *, create: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if create:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, default=str)
            stream.write("\n")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, default=str)
        stream.write("\n")
    temporary.replace(path)


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        return
    fields = sorted({str(key) for row in rows for key in row})
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def remote_join(name: str) -> str:
    return REMOTE_ROOT + "\\" + name


def remote_hash(solver: Any, path: str, label: str) -> dict[str, str]:
    scratch = remote_join(f"_{RUN_LABEL}_{label}_sha256.txt")
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"refusing to overwrite remote hash evidence: {scratch}")
    return {
        "path": path,
        "scratch": scratch,
        "sha256": pressure_probe.extension.mesh_study.remote_file_sha256(
            solver, path, scratch
        ),
    }


def save_pair(solver: Any, member: str, suffix: str) -> dict[str, Any]:
    stem = f"{RUN_LABEL}_{member}_{suffix}"
    case = remote_join(stem + ".cas.h5")
    data = remote_join(stem + ".dat.h5")
    if remote_file_exists(solver, case) or remote_file_exists(solver, data):
        raise FileExistsError(f"refusing to overwrite remote pulse checkpoint: {stem}")
    sweep.write_case_data_pair(solver, case, data, f"07n_pulse_{member}_{suffix}")
    return {
        "case": remote_hash(solver, case, f"{member}_{suffix}_case"),
        "data": remote_hash(solver, data, f"{member}_{suffix}_data"),
        "eligible_parent": False,
        "resume_allowed": False,
        "classification": "terminal diagnostic by design",
    }


def inlet_gate(solver: Any, fraction: float) -> dict[str, Any]:
    expected = {
        "liquidinlet": {"phase-1": 0.0, "phase-2": 116.92 * fraction},
        "steaminlet": {"phase-1": 80.69 * fraction, "phase-2": 0.0},
    }
    inlets = solver.settings.setup.boundary_conditions.mass_flow_inlet
    states: dict[str, Any] = {}
    readback: dict[str, Any] = {}
    passed = True
    for zone, phases in expected.items():
        state = inlets[zone].get_state()
        states[zone] = state
        readback[zone] = {}
        for phase, target in phases.items():
            value = nested(state, "phase", phase, "momentum", "mass_flow_rate", "value")
            readback[zone][phase] = value
            passed = passed and value is not None and math.isclose(
                float(value), target, rel_tol=0.0, abs_tol=1.0e-8
            )
    return {"fraction": fraction, "expected": expected, "readback": readback, "states": states, "passed": passed}


def set_controls(solver: Any) -> dict[str, Any]:
    controls = solver.settings.solution.run_calculation.transient_controls
    controls.time_step_size.set_state(TIME_STEP_SIZE_S)
    controls.max_iter_per_time_step.set_state(INNER_ITERATIONS)
    solver.tui.define.models.multiphase.volume_fraction_parameters.courant_number(
        MAX_VOF_COURANT
    )
    state = controls.get_state()
    passed = math.isclose(
        float(nested(state, "time_step_size")),
        TIME_STEP_SIZE_S,
        rel_tol=0.0,
        abs_tol=1.0e-14,
    ) and int(nested(state, "max_iter_per_time_step")) == INNER_ITERATIONS
    return {"state": state, "passed": passed}


def settings_gate(solver: Any, fraction: float) -> dict[str, Any]:
    base = pressure_probe.open_settings_gate(solver, BRINE_PRESSURE_PA)
    result = {
        "boundary": base["boundary"],
        "methods": base["methods"],
        "dpm": base["dpm"],
        "sources": base["sources"],
        "ewf": base["ewf"],
        "models": base["models"],
        "operating_conditions": base["operating_conditions"],
        "inlets": inlet_gate(solver, fraction),
    }
    result["passed"] = all(
        bool(result[key].get("passed"))
        for key in ("boundary", "methods", "dpm", "sources", "ewf", "inlets")
    )
    return result


def residual_rows(solver: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    return pilot.latest_residual_row(solver)


def pulse_gate(row: Mapping[str, Any], residuals: Sequence[Mapping[str, Any]], transcript: str) -> list[str]:
    failures: list[str] = []
    for key, value in row.items():
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            failures.append(f"non-finite {key}={value}")
    if float(row["latest_global_courant"]) > MAX_VOF_COURANT:
        failures.append(f"Global Courant exceeds {MAX_VOF_COURANT}")
    if float(row["liquid_vf_min"]) < -1.0e-8 or float(row["liquid_vf_max"]) > 1.0 + 1.0e-8:
        failures.append("liquid VOF is outside the bounded tolerance")
    if max(abs(float(row["pressure_min_pa"])), abs(float(row["pressure_max_pa"]))) > MAX_PRESSURE_PA:
        failures.append("pressure magnitude exceeds 10 MPa")
    if float(row["velocity_max_ms"]) > MAX_VELOCITY_M_S:
        failures.append("maximum velocity exceeds 100 m/s")
    if float(row["brine_face_liquid_vf_min"]) < 0.99:
        failures.append("brine-face liquid VF minimum fell below 0.99")
    if abs(float(row["vapor_brineoutlet_kgs"])) > 1.0e-3:
        failures.append("vapor through brine outlet exceeds 1e-3 kg/s")
    if abs(float(row["liquid_steamoutlet_kgs"])) > 1.0e-3:
        failures.append("liquid through steam outlet exceeds 1e-3 kg/s")
    for phase in ("liquid", "vapor"):
        if abs(float(row[f"{phase}_storage_closure_residual_kg_s"])) > MAX_STORAGE_CLOSURE_KG_S:
            failures.append(f"{phase} storage-closure residual exceeds 5 kg/s")
    if not residuals:
        failures.append("residual history unavailable")
    else:
        continuity_values = [
            pilot.continuity_value(item) for item in residuals
        ]
        if max(continuity_values) > 1.0:
            failures.append("within-step continuity exceeded 1")
        if continuity_values[-1] > 0.01:
            failures.append("end-step continuity exceeds 0.01")
    failures.extend(pressure_probe.transcript_failures(transcript))
    return sorted(set(failures))


def run_member(solver: Any, member: str, fraction: float) -> dict[str, Any]:
    member_root = LOCAL_ROOT / member
    member_root.mkdir(parents=True, exist_ok=False)
    manifest_path = member_root / "member_manifest.json"
    result: dict[str, Any] = {
        "member": member,
        "inlet_fraction": fraction,
        "status": "running",
        "classification": "terminal diagnostic by design",
        "eligible_parent": False,
        "resume_allowed": False,
        "physical_steps_completed": 0,
        "started_epoch": time.time(),
    }
    write_json(manifest_path, result, create=True)
    transcript_remote = remote_join(f"{RUN_LABEL}_{member}.trn")
    if remote_file_exists(solver, transcript_remote):
        raise FileExistsError(f"refusing to overwrite remote transcript: {transcript_remote}")
    try:
        solver.settings.file.read_case(file_name=PARENT_CASE)
        solver.settings.file.read_data(file_name=PARENT_DATA)
        time.sleep(2.0)
        initial_clock = transient07j.runtime_clock(solver)
        if int(initial_clock["time_step"]) != PARENT_STEP or not math.isclose(
            float(initial_clock["flow_time_s"]), PARENT_FLOW_TIME_S,
            rel_tol=0.0, abs_tol=1.0e-12,
        ):
            raise RuntimeError(f"parent clock mismatch: {initial_clock}")
        opening07m.set_inlet_fraction(solver, fraction)
        controls = set_controls(solver)
        settings = settings_gate(solver, fraction)
        if not controls["passed"] or not settings["passed"]:
            raise RuntimeError("pre-step controls/settings gate failed")
        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        baseline = rest07l.physical_metrics(solver, PARENT_STEP)
        baseline.update(rest07l.inventory(baseline, DOMAIN_VOLUME_M3))
        baseline.update(initial_clock)
        result.update({"initial_clock": initial_clock, "controls": controls, "pre_settings_gate": settings, "baseline_metrics": baseline})
        result["pre_step_checkpoint"] = save_pair(solver, member, "pre_step")
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript_remote)

        solver.settings.solution.run_calculation.dual_time_iterate(
            time_step_count=1, max_iter_per_step=INNER_ITERATIONS
        )
        clock = transient07j.runtime_clock(solver)
        expected_time = PARENT_FLOW_TIME_S + TIME_STEP_SIZE_S
        if int(clock["time_step"]) != PARENT_STEP + 1 or not math.isclose(
            float(clock["flow_time_s"]), expected_time,
            rel_tol=0.0, abs_tol=1.0e-12,
        ):
            raise RuntimeError(f"one-step clock proof failed: {clock}")
        metrics = rest07l.physical_metrics(solver, PARENT_STEP + 1)
        metrics.update(rest07l.inventory(metrics, DOMAIN_VOLUME_M3))
        metrics.update(pilot.extrema(solver, f"{RUN_LABEL}_{member}_step1"))
        metrics.update(clock)
        metrics.update(pilot.closed_rest_storage_closure(baseline, metrics))
        last, residual_history = residual_rows(solver)
        metrics["end_step_continuity_residual"] = pilot.continuity_value(last)
        metrics["residual_iteration"] = last["iteration"]
        solver.settings.file.stop_transcript()
        transcript = sweep.remote_text_read_best_effort(solver, transcript_remote)
        courant = rest07l.parse_global_courant(transcript)
        metrics["latest_global_courant"] = courant[-1] if courant else math.nan
        metrics["max_global_courant"] = max(courant) if courant else math.nan
        failures = pulse_gate(metrics, residual_history, transcript)
        post_settings = settings_gate(solver, fraction)
        if not post_settings["passed"]:
            failures.append("post-step settings gate failed")
        result["post_step_checkpoint"] = save_pair(solver, member, "step1")
        write_csv(member_root / "physical_history.csv", [metrics])
        write_csv(member_root / "residual_history.csv", residual_history)
        with (member_root / "transcript.trn").open("x", encoding="utf-8") as stream:
            stream.write(transcript)
        result.update(
            {
                "status": "completed",
                "classification": (
                    "accepted bounded diagnostic / one-step pulse"
                    if not failures
                    else "diagnostic / unresolved one-step pulse"
                ),
                "physical_steps_completed": 1,
                "endpoint": metrics,
                "gate_failures": sorted(set(failures)),
                "post_settings_gate": post_settings,
                "eligible_parent": False,
                "resume_allowed": False,
                "completed_epoch": time.time(),
            }
        )
        write_json(manifest_path, result)
        return result
    except (Exception, KeyboardInterrupt) as exc:
        result.update(
            {
                "status": "stopped",
                "classification": "terminal diagnostic",
                "eligible_parent": False,
                "resume_allowed": False,
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(manifest_path, result)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    if LOCAL_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite pulse evidence: {LOCAL_ROOT}")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=False)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "server_id": "2",
        "status": "running",
        "classification": "diagnostic / matched one-step pulse",
        "eligible_parent": False,
        "resume_allowed": False,
        "controller_pid": os.getpid(),
        "parent": {
            "case": PARENT_CASE, "case_expected_sha256": PARENT_CASE_SHA256,
            "data": PARENT_DATA, "data_expected_sha256": PARENT_DATA_SHA256,
            "clock": {"time_step": PARENT_STEP, "flow_time_s": PARENT_FLOW_TIME_S},
        },
        "matched_controls": {"time_step_size_s": TIME_STEP_SIZE_S, "inner_iterations": INNER_ITERATIONS, "brine_pressure_pa": BRINE_PRESSURE_PA},
        "members": {},
        "started_epoch": time.time(),
    }
    write_json(CAMPAIGN_MANIFEST, payload, create=True)
    solver: Any | None = None
    try:
        with exclusive_writer_lock(GLOBAL_WRITER_LOCK):
            solver = connect(server_id="2", tcp_timeout_seconds=5.0, start_transcript=True)
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_parent_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError(f"exclusive server-2 ownership unresolved: {clients!r}")
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            if payload["fluent_version"] != EXPECTED_VERSION:
                raise RuntimeError(f"unexpected Fluent version: {payload['fluent_version']}")
            payload["live_parallel_runtime"] = require_live_compute_node_count(solver, EXPECTED_RANKS)
            if not remote_file_exists(solver, PARENT_CASE) or not remote_file_exists(solver, PARENT_DATA):
                raise FileNotFoundError("accepted centre parent pair is incomplete")
            case = remote_hash(solver, PARENT_CASE, "parent_case")
            data = remote_hash(solver, PARENT_DATA, "parent_data")
            payload["parent_readback"] = {"case": case, "data": data}
            if case["sha256"] != PARENT_CASE_SHA256 or data["sha256"] != PARENT_DATA_SHA256:
                raise RuntimeError("accepted centre parent checksum mismatch")
            write_json(CAMPAIGN_MANIFEST, payload)

            # Retain unique remote report scratch files; deletion verification is
            # non-physical and previously stalled after successful reports.
            sweep.remote_delete_best_effort = lambda _solver, _path: True
            for member, fraction in MEMBERS:
                result = run_member(solver, member, fraction)
                payload["members"][member] = {
                    "status": result["status"],
                    "classification": result["classification"],
                    "physical_steps_completed": result["physical_steps_completed"],
                    "endpoint": result.get("endpoint"),
                    "gate_failures": result.get("gate_failures", []),
                    "manifest": str(LOCAL_ROOT / member / "member_manifest.json"),
                }
                write_json(CAMPAIGN_MANIFEST, payload)
            payload.update(
                {
                    "status": "completed",
                    "classification": "diagnostic / matched one-step zero-versus-full-feed pulse",
                    "eligible_parent": False,
                    "resume_allowed": False,
                    "acceptance_limitation": "One 1e-7 s pulse tests numerical and phase-routing survivability only; it cannot establish drainage capacity, level control, or full-flow operation.",
                    "completed_epoch": time.time(),
                }
            )
            write_json(CAMPAIGN_MANIFEST, payload)
            return 0
    except (Exception, KeyboardInterrupt) as exc:
        payload.update(
            {
                "status": "stopped",
                "classification": "terminal diagnostic",
                "eligible_parent": False,
                "resume_allowed": False,
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(CAMPAIGN_MANIFEST, payload)
        raise
    finally:
        if solver is not None:
            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
