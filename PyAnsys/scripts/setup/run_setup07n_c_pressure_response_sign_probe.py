#!/usr/bin/env python3
"""Run a bounded setup-07n zero-feed brine-pressure response-sign probe.

Each centre/low/high member cold-loads the same checksum-bound explicit-VOF
PISO step-940 closed-pool parent.  The only physical change is conversion of
``brineoutlet`` from wall to pressure outlet at the requested diagnostic
modified pressure.  No member inherits another member's field, no inlet flow
is introduced, and every checkpoint remains ineligible for promotion.

The pressure centre and half-width are CFD-derived numerical diagnostics, not
plant boundary data.  The experiment only establishes whether increasing
brine backpressure reduces outward drainage while the liquid seal is retained.
"""

from __future__ import annotations

import argparse
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
from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
)
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07l_hydrostatic_rest as rest07l  # noqa: E402
import run_setup07j_transient_vof_qualification as transient07j  # noqa: E402
import run_setup07m_pressure_opening_campaign as opening07m  # noqa: E402
import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402
import run_setup07n_a_faceproxy_dt_extension as extension  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = (
    "brine620k_07n_c_pressure_response_sign_zero_feed_"
    "dt256em6_steps10_attempt3_20260823"
)
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
PARENT_LABEL = (
    "brine620k_07n_a_closeddrain_meshselected_dt256em6_"
    "hold100_stage8_attempt1_20260823_additional_step100"
)
PARENT_CASE = REMOTE_ROOT + rf"\{PARENT_LABEL}.cas.h5"
PARENT_DATA = REMOTE_ROOT + rf"\{PARENT_LABEL}.dat.h5"
PARENT_CASE_SHA256 = (
    "03383ac0e1674b7a2acd47fc65ca84033c907f960bc3a4ace912e4902ce6c7c9"
)
PARENT_DATA_SHA256 = (
    "a5963dfada0754dd24685b699a65ac341d90b9ce0c3dda11879863eb9ff0772a"
)
INITIAL_TIME_STEP = 940
INITIAL_FLOW_TIME_S = 0.2227100000000037
TIME_STEP_SIZE_S = 2.56e-4
INNER_ITERATIONS = 100
PHYSICAL_STEPS = 10
CHECKPOINT_STEPS = {1, 5, 10}
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16
MAX_VOF_COURANT = 0.25
STEAM_OUTLET_PRESSURE_PA = 1_120_000.0
CENTRE_PRESSURE_PA = 1_122_423.2
PARENT_LIQUID_INVENTORY_KG = 3877.4680713930516
PARENT_VAPOR_INVENTORY_KG = 131.38684271718486
LIQUID_FEED_REFERENCE_KG_S = 116.92
VAPOR_FEED_REFERENCE_KG_S = 80.69
BRINE_FACE_AREA_M2 = 0.19936247
LIQUID_DENSITY_KG_M3 = transient07j.LIQUID_DENSITY_KG_M3
REFERENCE_LIQUID_VELOCITY_MS = (
    LIQUID_FEED_REFERENCE_KG_S / (LIQUID_DENSITY_KG_M3 * BRINE_FACE_AREA_M2)
)
PRESSURE_HALF_WIDTH_PA = (
    0.5 * LIQUID_DENSITY_KG_M3 * REFERENCE_LIQUID_VELOCITY_MS**2
)
PRESSURE_MEMBERS = (
    ("centre", CENTRE_PRESSURE_PA),
    ("low", CENTRE_PRESSURE_PA - PRESSURE_HALF_WIDTH_PA),
    ("high", CENTRE_PRESSURE_PA + PRESSURE_HALF_WIDTH_PA),
)
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
GLOBAL_WRITER_LOCK = (
    PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server1_writer.lock"
)


class HardGateError(RuntimeError):
    """A numerical or physical failure that terminates the probe."""


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("1",), default="1")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def write_json(path: Path, payload: Any, *, create: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if create else "w"
    with path.open(mode, encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, default=str)
        stream.write("\n")


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({str(key) for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def remote_join(name: str) -> str:
    return REMOTE_ROOT + "\\" + name


def remote_hash(solver: Any, path: str, label: str) -> dict[str, str]:
    scratch = remote_join(f"_{RUN_LABEL}_{label}_sha256.txt")
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"refusing to overwrite remote hash evidence: {scratch}")
    return {
        "path": path,
        "sha256": extension.mesh_study.remote_file_sha256(solver, path, scratch),
        "scratch": scratch,
    }


def save_pair(solver: Any, member: str, step: int) -> dict[str, Any]:
    suffix = "opened_t0" if step == 0 else f"additional_step{step}"
    stem = f"{RUN_LABEL}_{member}_{suffix}"
    case_path = remote_join(stem + ".cas.h5")
    data_path = remote_join(stem + ".dat.h5")
    if remote_file_exists(solver, case_path) or remote_file_exists(solver, data_path):
        raise FileExistsError(f"refusing to overwrite remote checkpoint: {stem}")
    sweep.write_case_data_pair(solver, case_path, data_path, f"07n_c_{member}_{suffix}")
    return {
        "case": remote_hash(solver, case_path, f"{member}_{suffix}_case"),
        "data": remote_hash(solver, data_path, f"{member}_{suffix}_data"),
        "eligible_parent": False,
    }


def zero_inlet_gate(solver: Any) -> dict[str, Any]:
    inlets = solver.settings.setup.boundary_conditions.mass_flow_inlet
    states: dict[str, Any] = {}
    passed = True
    for zone in ("liquidinlet", "steaminlet"):
        state = inlets[zone].get_state()
        states[zone] = state
        for phase in ("phase-1", "phase-2"):
            value = opening07m.nested(
                state, "phase", phase, "momentum", "mass_flow_rate", "value"
            )
            passed = passed and value is not None and math.isclose(
                float(value), 0.0, rel_tol=0.0, abs_tol=1.0e-12
            )
    return {"states": states, "passed": passed}


def open_settings_gate(solver: Any, pressure_pa: float) -> dict[str, Any]:
    setup = solver.settings.setup
    boundaries = setup.boundary_conditions
    membership = {
        "wall": list(boundaries.wall.get_object_names()),
        "mass_flow_inlet": list(boundaries.mass_flow_inlet.get_object_names()),
        "pressure_outlet": list(boundaries.pressure_outlet.get_object_names()),
        "mass_flow_outlet": list(boundaries.mass_flow_outlet.get_object_names()),
    }
    brine_state = boundaries.pressure_outlet["brineoutlet"].get_state()
    pressure = opening07m.nested(
        brine_state, "phase", "mixture", "momentum", "gauge_pressure", "value"
    )
    liquid_backflow = opening07m.nested(
        brine_state,
        "phase",
        "phase-2",
        "multiphase",
        "backflow_volume_fraction",
        "value",
    )
    boundary_passed = (
        "brineoutlet" not in membership["wall"]
        and set(membership["pressure_outlet"]) == {"steamoutlet", "brineoutlet"}
        and not membership["mass_flow_outlet"]
        and pressure is not None
        and math.isclose(float(pressure), pressure_pa, rel_tol=0.0, abs_tol=1.0e-5)
        and liquid_backflow is not None
        and math.isclose(
            float(liquid_backflow), 1.0, rel_tol=0.0, abs_tol=1.0e-12
        )
    )
    methods = pilot.methods_gate(solver)
    result = {
        "boundary": {
            "membership": membership,
            "brine_state": brine_state,
            "passed": boundary_passed,
        },
        "zero_inlets": zero_inlet_gate(solver),
        "methods": methods,
        "dpm": pilot.dpm_gate(setup.models.discrete_phase),
        "sources": pilot.source_gate(setup),
        "ewf": pilot.ewf_gate(solver),
        "models": pilot.safe_get_state(setup.models, "07n-c models"),
        "operating_conditions": pilot.safe_get_state(
            setup.general.operating_conditions, "07n-c operating conditions"
        ),
    }
    result["passed"] = all(
        bool(result[key].get("passed"))
        for key in ("boundary", "zero_inlets", "methods", "dpm", "sources", "ewf")
    )
    return result


def transcript_failures(text: str) -> list[str]:
    failures = pilot.transcript_failures(text)
    if rest07l.dpm_tracking_evidence(text):
        failures.append("DPM parcel tracking text reappeared")
    return failures


def row_gate(row: Mapping[str, Any], transcript_text: str) -> list[str]:
    failures: list[str] = []
    for key, value in row.items():
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            failures.append(f"non-finite {key}={value}")
    if float(row["latest_global_courant"]) > MAX_VOF_COURANT:
        failures.append(
            f"Global Explicit-VOF Courant {row['latest_global_courant']} exceeds "
            f"{MAX_VOF_COURANT}"
        )
    if float(row["liquid_vf_min"]) < -1.0e-8 or float(row["liquid_vf_max"]) > 1.0 + 1.0e-8:
        failures.append(
            f"VOF bounds [{row['liquid_vf_min']}, {row['liquid_vf_max']}]"
        )
    if max(abs(float(row["pressure_min_pa"])), abs(float(row["pressure_max_pa"]))) > 1.0e7:
        failures.append("domain pressure magnitude exceeds 1e7 Pa")
    if abs(float(row["velocity_max_ms"])) > 100.0:
        failures.append(f"maximum velocity exceeds 100 m/s: {row['velocity_max_ms']}")
    if float(row["brine_face_liquid_vf_min"]) < 0.99:
        failures.append(
            "brine face lost liquid seal: "
            f"minimum liquid VF={row['brine_face_liquid_vf_min']}"
        )
    if abs(float(row["vapor_brineoutlet_kgs"])) > 1.0e-3:
        failures.append(
            f"vapor flow through brine outlet exceeds 1e-3 kg/s: "
            f"{row['vapor_brineoutlet_kgs']}"
        )
    if abs(float(row["liquid_steamoutlet_kgs"])) > 1.0e-3:
        failures.append(
            f"liquid flow through steam outlet exceeds 1e-3 kg/s: "
            f"{row['liquid_steamoutlet_kgs']}"
        )
    if abs(float(row["liquid_brineoutlet_kgs"])) > 50.0:
        failures.append(
            f"gross zero-feed liquid brine response: {row['liquid_brineoutlet_kgs']} kg/s"
        )
    if abs(float(row["liquid_inventory_change_from_parent_kg"])) > 3.9:
        failures.append(
            "liquid inventory changed by more than about 0.1% during sign probe: "
            f"{row['liquid_inventory_change_from_parent_kg']} kg"
        )
    for phase in ("liquid", "vapor"):
        closure = abs(float(row[f"{phase}_storage_closure_residual_kg_s"]))
        if closure > 5.0:
            failures.append(f"{phase} storage closure residual exceeds 5 kg/s: {closure}")
    continuity = float(row["end_step_continuity_residual"])
    if continuity > 1.0:
        failures.append(f"gross continuity residual exceeds 1: {continuity}")
    failures.extend(transcript_failures(transcript_text))
    return sorted(set(failures))


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


def run_member(
    solver: Any,
    member: str,
    pressure_pa: float,
    parent_inventory_kg: float,
) -> dict[str, Any]:
    member_root = LOCAL_ROOT / member
    member_root.mkdir(parents=True, exist_ok=False)
    transcript_remote = remote_join(f"{RUN_LABEL}_{member}.trn")
    if remote_file_exists(solver, transcript_remote):
        raise FileExistsError(f"refusing to overwrite remote transcript: {transcript_remote}")

    solver.settings.file.read_case(file_name=PARENT_CASE)
    solver.settings.file.read_data(file_name=PARENT_DATA)
    time.sleep(2.0)
    if not pilot.complete_gate(solver)["passed"]:
        raise RuntimeError(f"{member}: cold-loaded closed parent failed settings gate")
    clock0 = transient07j.runtime_clock(solver)
    if int(clock0["time_step"]) != INITIAL_TIME_STEP or not math.isclose(
        float(clock0["flow_time_s"]),
        INITIAL_FLOW_TIME_S,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise RuntimeError(f"{member}: parent clock mismatch: {clock0}")

    try:
        solver.settings.file.stop_transcript()
    except Exception:
        pass
    solver.settings.file.start_transcript(file_name=transcript_remote)

    result: dict[str, Any] = {
        "member": member,
        "requested_brine_pressure_pa": pressure_pa,
        "status": "running",
        "classification": "diagnostic / unresolved zero-feed pressure-response member",
        "eligible_parent": False,
        "parent_clock": clock0,
        "physical_steps_observed": 0,
        "physical_steps_completed": 0,
        "steps": [],
        "checkpoints": {},
        "started_epoch": time.time(),
    }
    manifest_path = member_root / "member_manifest.json"
    write_json(manifest_path, result, create=True)
    rows: list[dict[str, Any]] = []
    try:
        result["boundary_change_readback"] = opening07m.open_brine_pressure_outlet(
            solver, pressure_pa
        )
        controls = solver.settings.solution.run_calculation.transient_controls
        controls.time_step_size.set_state(TIME_STEP_SIZE_S)
        controls.max_iter_per_time_step.set_state(INNER_ITERATIONS)
        solver.tui.define.models.multiphase.volume_fraction_parameters.courant_number(
            MAX_VOF_COURANT
        )
        result["transient_controls_readback"] = controls.get_state()
        if not math.isclose(
            float(result["transient_controls_readback"]["time_step_size"]),
            TIME_STEP_SIZE_S,
            rel_tol=0.0,
            abs_tol=1.0e-14,
        ) or int(
            result["transient_controls_readback"]["max_iter_per_time_step"]
        ) != INNER_ITERATIONS:
            raise RuntimeError(f"{member}: transient controls failed readback")
        result["opened_settings_gate"] = open_settings_gate(solver, pressure_pa)
        if not result["opened_settings_gate"]["passed"]:
            raise RuntimeError(f"{member}: opened settings gate failed")
        result["checkpoints"]["0"] = save_pair(solver, member, 0)

        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        previous: dict[str, Any] = {
            **clock0,
            "liquid_inventory_kg": parent_inventory_kg,
            "vapor_inventory_kg": PARENT_VAPOR_INVENTORY_KG,
            "liquid_net_kgs": 0.0,
            "vapor_net_kgs": 0.0,
        }

        for additional_step in range(1, PHYSICAL_STEPS + 1):
            started = time.time()
            solver.settings.solution.run_calculation.dual_time_iterate(
                time_step_count=1, max_iter_per_step=INNER_ITERATIONS
            )
            clock = transient07j.runtime_clock(solver)
            failures = clock_failures(clock, additional_step)
            if failures:
                raise HardGateError("; ".join(failures))
            result["physical_steps_observed"] = additional_step
            result["last_observed_clock"] = dict(clock)
            write_json(manifest_path, result)

            total_step = INITIAL_TIME_STEP + additional_step
            metrics = rest07l.physical_metrics(solver, total_step)
            row: dict[str, Any] = {
                **metrics,
                **clock,
                **rest07l.inventory(metrics, pilot.DOMAIN_VOLUME_M3),
                **pilot.extrema(solver, f"07n_c_{member}_step{additional_step}"),
                "member": member,
                "requested_brine_pressure_pa": pressure_pa,
                "additional_step": additional_step,
            }
            row.update(pilot.closed_rest_storage_closure(previous, row))
            row["liquid_inventory_change_from_parent_kg"] = (
                float(row["liquid_inventory_kg"]) - parent_inventory_kg
            )
            transcript_text = sweep.remote_text_read_best_effort(
                solver, transcript_remote
            )
            courant = rest07l.parse_global_courant(transcript_text)
            row["latest_global_courant"] = courant[-1] if courant else math.nan
            row["courant_metric"] = "Global Courant Number [Explicit VOF Criteria]"
            residual_last, residual_rows = pilot.latest_residual_row(solver)
            row["end_step_continuity_residual"] = pilot.continuity_value(
                residual_last
            )
            row["residual_iteration"] = residual_last["iteration"]
            row["wall_seconds"] = time.time() - started
            failures = row_gate(row, transcript_text)
            settings_gate = open_settings_gate(solver, pressure_pa)
            if not settings_gate["passed"]:
                failures.append("post-step settings gate failed")
            rows.append(row)
            result["physical_steps_completed"] = additional_step
            result["steps"].append(
                {
                    "additional_step": additional_step,
                    "metrics": row,
                    "gate_failures": sorted(set(failures)),
                    "checkpoint": None,
                }
            )
            write_csv(member_root / "physical_history.csv", rows)
            write_csv(member_root / "residual_history.csv", residual_rows)
            if failures:
                write_json(manifest_path, result)
                raise HardGateError("; ".join(sorted(set(failures))))
            if additional_step in CHECKPOINT_STEPS:
                checkpoint = save_pair(solver, member, additional_step)
                result["checkpoints"][str(additional_step)] = checkpoint
                result["steps"][-1]["checkpoint"] = checkpoint
            write_json(manifest_path, result)
            print(
                f"07n-c {member}: step {additional_step}/{PHYSICAL_STEPS}; "
                f"continuity={row['end_step_continuity_residual']:.6g}; "
                f"liquid brine={row['liquid_brineoutlet_kgs']:.6g} kg/s; "
                f"inventory change={row['liquid_inventory_change_from_parent_kg']:.6g} kg; "
                f"Co={row['latest_global_courant']:.6g}",
                flush=True,
            )
            previous = row

        continuity_tail = [
            float(item["end_step_continuity_residual"]) for item in rows[-2:]
        ]
        residual_passed = len(continuity_tail) == 2 and all(
            value <= 0.01 for value in continuity_tail
        )
        result.update(
            {
                "status": "completed" if residual_passed else "diagnostic_unresolved",
                "classification": (
                    "accepted diagnostic / bounded zero-feed pressure-response member"
                    if residual_passed
                    else "diagnostic / unresolved zero-feed pressure-response member"
                ),
                "eligible_parent": False,
                "residual_gate": {
                    "required": "two consecutive end-step continuity values <= 0.01",
                    "tail": continuity_tail,
                    "passed": residual_passed,
                },
                "endpoint": rows[-1],
                "post_settings_gate": open_settings_gate(solver, pressure_pa),
                "completed_epoch": time.time(),
            }
        )
        write_json(manifest_path, result)
        return result
    except HardGateError as exc:
        result.update(
            {
                "status": "terminal",
                "classification": "terminal diagnostic",
                "eligible_parent": False,
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(manifest_path, result)
        raise
    except (Exception, KeyboardInterrupt) as exc:
        observed = int(result.get("physical_steps_observed", 0))
        completed = int(result.get("physical_steps_completed", 0))
        status = (
            "stopped_zero_step"
            if observed == 0 and completed == 0
            else "stopped_postsolve_monitoring"
            if observed > completed
            else "stopped"
        )
        result.update(
            {
                "status": status,
                "classification": "diagnostic / unresolved",
                "eligible_parent": False,
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
        text = sweep.remote_text_read_best_effort(solver, transcript_remote)
        if text:
            with (member_root / "transcript.trn").open("x", encoding="utf-8") as stream:
                stream.write(text)


def comparison_gate(results: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    endpoints = {name: value["endpoint"] for name, value in results.items()}
    flows = {
        name: float(row["liquid_brineoutlet_kgs"])
        for name, row in endpoints.items()
    }
    monotonic = flows["low"] < flows["centre"] < flows["high"]
    sign_bracket = flows["low"] < 0.0 < flows["high"]
    centre_quiet = abs(flows["centre"]) <= 0.01 * LIQUID_FEED_REFERENCE_KG_S
    all_residual = all(bool(result["residual_gate"]["passed"]) for result in results.values())
    slope = (flows["high"] - flows["low"]) / (2.0 * PRESSURE_HALF_WIDTH_PA)
    passed = monotonic and sign_bracket and centre_quiet and all_residual
    return {
        "signed_liquid_brine_flow_convention": "negative is outward",
        "endpoint_liquid_brineoutlet_kgs": flows,
        "increasing_pressure_increases_signed_flow": monotonic,
        "endpoint_sign_bracket": sign_bracket,
        "centre_flow_within_1_percent_full_liquid_feed": centre_quiet,
        "all_member_residual_gates_passed": all_residual,
        "signed_flow_slope_kg_s_per_pa": slope,
        "controller_response_implication": (
            "For error=target-minus-measured, a low level must increase brine "
            "backpressure to reduce outward liquid flow."
            if monotonic
            else "Pressure-response direction is unresolved; no controller may run."
        ),
        "passed": passed,
    }


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    manifest_path = LOCAL_ROOT / "campaign_manifest.json"
    local_lock = LOCAL_ROOT / "campaign_writer.lock"
    if manifest_path.exists() or LOCAL_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite pressure probe: {LOCAL_ROOT}")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=False)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "server_id": args.server_id,
        "status": "running",
        "classification": "diagnostic / unresolved zero-feed pressure-response sign probe",
        "eligible_parent": False,
        "controller_use_authorized": False,
        "parent": {
            "label": PARENT_LABEL,
            "case": PARENT_CASE,
            "case_expected_sha256": PARENT_CASE_SHA256,
            "data": PARENT_DATA,
            "data_expected_sha256": PARENT_DATA_SHA256,
            "clock": {
                "time_step": INITIAL_TIME_STEP,
                "flow_time_s": INITIAL_FLOW_TIME_S,
            },
        },
        "pressure_definition": {
            "centre_pa": CENTRE_PRESSURE_PA,
            "centre_basis": "step-940 closed-brine-face area-weighted modified pressure",
            "half_width_pa": PRESSURE_HALF_WIDTH_PA,
            "half_width_basis": "one full-liquid-feed reference velocity head",
            "members": dict(PRESSURE_MEMBERS),
            "plant_boundary_validated": False,
        },
        "time_step_size_s": TIME_STEP_SIZE_S,
        "inner_iterations_per_step": INNER_ITERATIONS,
        "physical_steps_per_member": PHYSICAL_STEPS,
        "member_order": [name for name, _ in PRESSURE_MEMBERS],
        "one_factor_change": "closed brine wall -> diagnostic brine pressure outlet; pressure member only",
        "unchanged_contract": (
            "exact explicit/PISO step-940 field; zero feed; steam pressure outlet; "
            "explicit VOF/Geo-Reconstruct; PRESTO/WFGC; first-order transient; "
            "RNG k-epsilon; Energy off; DPM zero/off; EWF off; no sources/sinks; "
            "no initialization"
        ),
        "members": {},
        "started_epoch": time.time(),
        "controller_pid": os.getpid(),
    }
    write_json(manifest_path, payload, create=True)

    solver: Any | None = None
    try:
        with exclusive_writer_lock(GLOBAL_WRITER_LOCK), exclusive_writer_lock(local_lock):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                start_transcript=True,
            )
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_parent_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError(f"exclusive server-1 ownership unresolved: {clients!r}")
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
                raise FileNotFoundError("authoritative step-940 parent pair is incomplete")
            parent_case = remote_hash(solver, PARENT_CASE, "parent_case")
            parent_data = remote_hash(solver, PARENT_DATA, "parent_data")
            payload["parent_readback"] = {"case": parent_case, "data": parent_data}
            if parent_case["sha256"] != PARENT_CASE_SHA256:
                raise RuntimeError("parent case checksum mismatch")
            if parent_data["sha256"] != PARENT_DATA_SHA256:
                raise RuntimeError("parent data checksum mismatch")

            solver.settings.file.read_case(file_name=PARENT_CASE)
            solver.settings.file.read_data(file_name=PARENT_DATA)
            time.sleep(2.0)
            payload["live_parallel_runtime_after_parent_load"] = (
                require_live_compute_node_count(solver, EXPECTED_RANKS)
            )
            payload["parent_settings_gate"] = pilot.complete_gate(solver)
            if not payload["parent_settings_gate"]["passed"]:
                raise RuntimeError("authoritative parent settings gate failed")
            parent_clock = transient07j.runtime_clock(solver)
            if int(parent_clock["time_step"]) != INITIAL_TIME_STEP or not math.isclose(
                float(parent_clock["flow_time_s"]),
                INITIAL_FLOW_TIME_S,
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ):
                raise RuntimeError(f"authoritative parent clock mismatch: {parent_clock}")
            payload["parent_physical_metrics_reference"] = {
                "source": (
                    "checksum-bound accepted explicit/PISO step-940 manifest and "
                    "matched-window comparison; no redundant live phase-flux report"
                ),
                "liquid_inventory_kg": PARENT_LIQUID_INVENTORY_KG,
                "vapor_inventory_kg": PARENT_VAPOR_INVENTORY_KG,
                "brine_wall_area_weighted_pressure_pa": CENTRE_PRESSURE_PA,
                "brine_face_liquid_vf_min": 1.0,
                "liquid_steamoutlet_kgs": 0.0,
            }
            write_json(manifest_path, payload)

            results: dict[str, Any] = {}
            for member, pressure_pa in PRESSURE_MEMBERS:
                result = run_member(
                    solver,
                    member,
                    pressure_pa,
                    PARENT_LIQUID_INVENTORY_KG,
                )
                results[member] = result
                payload["members"][member] = {
                    "status": result["status"],
                    "classification": result["classification"],
                    "eligible_parent": False,
                    "manifest": str(LOCAL_ROOT / member / "member_manifest.json"),
                    "endpoint": result["endpoint"],
                    "residual_gate": result["residual_gate"],
                    "checkpoints": result["checkpoints"],
                }
                write_json(manifest_path, payload)

            comparison = comparison_gate(results)
            payload.update(
                {
                    "status": "completed",
                    "classification": (
                        "accepted diagnostic / bounded zero-feed pressure-response sign"
                        if comparison["passed"]
                        else "diagnostic / unresolved zero-feed pressure-response sign"
                    ),
                    "eligible_parent": False,
                    "controller_use_authorized": comparison["passed"],
                    "comparison_gate": comparison,
                    "acceptance_limitation": (
                        "This establishes only the numerical pressure-response direction "
                        "from a CFD-derived centre. It does not validate plant pressure, "
                        "operating level, drainage capacity or constant-level control."
                    ),
                    "completed_epoch": time.time(),
                }
            )
            write_json(manifest_path, payload)
            return 0
    except HardGateError as exc:
        payload.update(
            {
                "status": "terminal",
                "classification": "terminal diagnostic",
                "eligible_parent": False,
                "controller_use_authorized": False,
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(manifest_path, payload)
        raise
    except (Exception, KeyboardInterrupt) as exc:
        payload.update(
            {
                "status": "stopped",
                "classification": "diagnostic / unresolved",
                "eligible_parent": False,
                "controller_use_authorized": False,
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(manifest_path, payload)
        raise
    finally:
        if solver is not None:
            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
