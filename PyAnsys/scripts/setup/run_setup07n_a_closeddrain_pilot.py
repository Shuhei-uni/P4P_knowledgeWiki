#!/usr/bin/env python3
"""Run the bounded setup-07n-a lower-face-proxy closed-drain pilot.

The run cold-loads the accepted setup-07l step-10 case *without data*, freshly
Hybrid Initializes, patches the lower Stage-0 pool candidate, saves and cold
reloads a unique time-zero pair, then advances ten guarded 1e-6 s physical
steps.  It is a non-promotable face-proxy smoke test, not a plant-valid water
level or a physically relaxed separator state.
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
from measure_setup07n_candidate_pool_volumes import (  # noqa: E402
    DOMAIN_VOLUME_M3,
    LIQUID_DENSITY_KG_M3,
    POOL_MAXIMUM_XZ_M,
    POOL_MINIMUM_M,
    dpm_gate,
    source_gate,
)
from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402

import prepare_setup07l_hydrostatic_rest as prepare07l  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07l_hydrostatic_rest as rest07l  # noqa: E402
import run_setup07j_transient_vof_qualification as transient07j  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = "brine620k_07n_a_closeddrain_lower_faceproxy_pilot_attempt4_20260822"
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_CARRIER_CASE = (
    REMOTE_ROOT + r"\brine620k_07l_hydrostatic_rest_v1_checkpoint_step10.cas.h5"
)
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
GLOBAL_WRITER_LOCK = PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server1_writer.lock"
STAGE0_MANIFEST = (
    PROJECT_ROOT
    / "output"
    / STUDY_ID
    / "brine620k_07n_stage0_geometry_v1"
    / "brine620k_07n_stage0_candidate_pool_volumes_faceproxy_attempt1_20260822.json"
)
EXPECTED_STAGE0_SHA256 = "d0a39744b49c43838f15d2ee18b279d276804c2ca20a7cc07a0e5301fc0a71f4"
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16
TARGET_LEVEL_Y_M = 0.016416369820944965
EXPECTED_MARKED_CELLS = 98473
EXPECTED_LIQUID_VOLUME_M3 = 4.400159116224599
EXPECTED_LIQUID_INVENTORY_KG = 3877.4680713930516
TIME_STEP_SIZE_S = 1.0e-6
INNER_ITERATIONS = 20
TARGET_STEPS = 10
CHECKPOINT_STEPS = {1, 5, 10}
MAX_VOF_COURANT = 0.25
REGISTER_NAME = "setup07n_a_lower_faceproxy_pilot_attempt4_pool"
CANDIDATE_MODE = "faceproxy"
CANDIDATE_BASIS = "resolved crown plus two crown-touching boundary-face heights"
CANDIDATE_LIMITATION = "boundary-face proxy; adjacent volume-cell height unresolved"
RUN_CLASSIFICATION = "diagnostic / unresolved lower faceproxy pilot"
FINAL_CLASSIFICATION = "diagnostic / unresolved lower faceproxy bounded startup"
GRAVITY_TIME_SCALE_NOTE = (
    "10 us is only a smoke test; local gravity scale is about 0.0428 s"
)
ACCEPTANCE_LIMITATION = (
    "Ten microseconds proves only guarded implementation/startup behavior. "
    "The level uses a boundary-face proxy and is not a promoted 07n-a pool."
)
ELIGIBILITY_SCOPE = "same faceproxy diagnostic lineage, conservative dt extension only"
ZONES = ["liquidinlet", "steaminlet", "steamoutlet", "brineoutlet"]
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"


class HardGateError(RuntimeError):
    """A numerical or physical failure that makes the field terminal."""


def remote_join(name: str) -> str:
    return str(PureWindowsPath(REMOTE_ROOT) / name)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("1",), default="1")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


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


def local_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def remote_hash(solver: Any, path: str, label: str) -> dict[str, str]:
    scratch = remote_join(f"_{RUN_LABEL}_{label}_sha256.txt")
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"refusing to overwrite remote hash evidence: {scratch}")
    return {
        "path": path,
        "sha256": mesh_study.remote_file_sha256(solver, path, scratch),
        "scratch": scratch,
    }


def ewf_gate(solver: Any) -> dict[str, Any]:
    enabled = solver.scheme.eval("(rpgetvar 'sg-wallfilm?)")
    parameters = solver.scheme.eval("(rpgetvar 'wall-film/model-parameters)")
    equations = list(solver.settings.solution.monitor.residual.equations.get_object_names())
    film_equations = [name for name in equations if "film" in str(name).lower()]
    result = {
        "sg_wallfilm_rpvar": enabled,
        "model_parameters": parameters,
        "film_residual_equations": film_equations,
    }
    result["passed"] = enabled is False and not parameters and not film_equations
    return result


def boundary_gate(solver: Any) -> dict[str, Any]:
    boundaries = solver.settings.setup.boundary_conditions
    membership = {
        "wall": list(boundaries.wall.get_object_names()),
        "mass_flow_inlet": list(boundaries.mass_flow_inlet.get_object_names()),
        "pressure_outlet": list(boundaries.pressure_outlet.get_object_names()),
        "mass_flow_outlet": list(boundaries.mass_flow_outlet.get_object_names()),
    }
    zero_flows: dict[str, Any] = {}
    passed = (
        "brineoutlet" in membership["wall"]
        and set(membership["mass_flow_inlet"]) >= {"liquidinlet", "steaminlet"}
        and membership["pressure_outlet"] == ["steamoutlet"]
        and not membership["mass_flow_outlet"]
    )
    for zone in ("liquidinlet", "steaminlet"):
        state = boundaries.mass_flow_inlet[zone].get_state()
        zero_flows[zone] = state
        for phase in ("phase-1", "phase-2"):
            value = prepare07l.nested(
                state, "phase", phase, "momentum", "mass_flow_rate", "value"
            )
            passed = passed and value is not None and math.isclose(
                float(value), 0.0, rel_tol=0.0, abs_tol=1.0e-12
            )
    return {"membership": membership, "inlet_states": zero_flows, "passed": passed}


def methods_gate(solver: Any) -> dict[str, Any]:
    methods = solver.settings.solution.methods
    readback = {
        "pressure_velocity_coupling": methods.p_v_coupling.flow_scheme.get_state(),
        "pressure_scheme": methods.discretization_scheme["pressure"].get_state(),
        "volume_fraction_scheme": methods.discretization_scheme["mp"].get_state(),
        "transient_formulation": methods.transient_formulation.get_state(),
        "warped_face_gradient_correction": methods.warped_face_gradient_correction.get_state(),
        "full_state": safe_get_state(methods, "07n-a methods"),
    }
    readback["passed"] = (
        readback["pressure_velocity_coupling"] == "PISO"
        and readback["pressure_scheme"] == "presto!"
        and readback["volume_fraction_scheme"] == "geo-reconstruct"
        and readback["transient_formulation"] == "unsteady-1st-order"
        and bool(readback["warped_face_gradient_correction"].get("enable"))
    )
    return readback


def complete_gate(solver: Any) -> dict[str, Any]:
    setup = solver.settings.setup
    result = {
        "boundary": boundary_gate(solver),
        "methods": methods_gate(solver),
        "dpm": dpm_gate(setup.models.discrete_phase),
        "sources": source_gate(setup),
        "ewf": ewf_gate(solver),
        "models": safe_get_state(setup.models, "07n-a models"),
        "operating_conditions": safe_get_state(
            setup.general.operating_conditions, "07n-a operating conditions"
        ),
    }
    result["passed"] = all(
        bool(result[key].get("passed"))
        for key in ("boundary", "methods", "dpm", "sources", "ewf")
    )
    return result


def report_volume_extreme(solver: Any, field: str, mode: str, label: str) -> float:
    reports = solver.settings.results.report.volume_integrals
    command = reports.minimum if mode == "minimum" else reports.maximum
    text = mesh_study.report_file_text(
        solver,
        REMOTE_ROOT,
        label,
        lambda path: command(
            cell_zones=["fluid"],
            cell_function=field,
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    from pyansys_fluent.mesh_convergence import parse_named_report_rows

    rows = parse_named_report_rows(text, ["fluid"])
    if "fluid" not in rows:
        raise RuntimeError(f"could not parse {mode} {field}: {text}")
    return float(rows["fluid"])


def brine_face_field_range(solver: Any, field: str) -> dict[str, Any]:
    """Read every brine-face scalar value through the field-data service."""

    data = solver.fields.field_data.get_scalar_field_data(
        field_name=field,
        surfaces=["brineoutlet"],
        node_value=False,
        boundary_value=True,
    )
    values = [float(value) for value in data["brineoutlet"]]
    if not values or not all(math.isfinite(value) for value in values):
        raise RuntimeError(f"invalid brine-face {field} field data")
    return {"minimum": min(values), "maximum": max(values), "count": len(values)}


def extrema(solver: Any, label: str) -> dict[str, Any]:
    brine_vf = brine_face_field_range(solver, "phase-2-vof")
    result: dict[str, Any] = {
        "liquid_vf_min": report_volume_extreme(
            solver, "phase-2-vof", "minimum", f"{label}_vf_min"
        ),
        "liquid_vf_max": report_volume_extreme(
            solver, "phase-2-vof", "maximum", f"{label}_vf_max"
        ),
        "pressure_min_pa": report_volume_extreme(
            solver, "pressure", "minimum", f"{label}_pressure_min"
        ),
        "pressure_max_pa": report_volume_extreme(
            solver, "pressure", "maximum", f"{label}_pressure_max"
        ),
        "velocity_max_ms": report_volume_extreme(
            solver, "velocity-magnitude", "maximum", f"{label}_velocity_max"
        ),
        "brine_face_liquid_vf_min": brine_vf["minimum"],
        "brine_face_liquid_vf_max": brine_vf["maximum"],
        "brine_face_liquid_vf_value_count": brine_vf["count"],
    }
    result["brine_face_liquid_vf_area_avg"] = mesh_study.surface_scalar(
        solver,
        REMOTE_ROOT,
        f"{label}_brine_vf_avg",
        ["brineoutlet"],
        "phase-2-vof",
    )["Net"]
    return result


def clock_gate(clock: Mapping[str, Any], step: int) -> list[str]:
    failures: list[str] = []
    if int(clock["time_step"]) != step:
        failures.append(f"time step expected={step} actual={clock['time_step']}")
    expected = step * TIME_STEP_SIZE_S
    if not math.isclose(
        float(clock["flow_time_s"]),
        expected,
        rel_tol=0.0,
        abs_tol=max(1.0e-12, TIME_STEP_SIZE_S * 1.0e-6),
    ):
        failures.append(f"flow time expected={expected} actual={clock['flow_time_s']}")
    return failures


def latest_residual_row(solver: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows = sweep.monitor_history_rows(solver)
    if not rows:
        raise RuntimeError("residual history is empty")
    return dict(rows[-1]), rows


def continuity_value(row: Mapping[str, Any]) -> float:
    matches = [value for key, value in row.items() if "continuity" in str(key).lower()]
    if len(matches) != 1:
        raise RuntimeError(f"could not identify one continuity residual: {row}")
    return float(matches[0])


def closed_rest_storage_closure(
    previous: Mapping[str, Any], current: Mapping[str, Any]
) -> dict[str, Any]:
    """Close phase storage against setup-07l's ``*_net_kgs`` reports.

    The older setup-07j helper expects renamed ``*_net_boundary_flux_kg_s``
    keys.  This pilot deliberately consumes the setup-07l physical-monitor
    schema directly so a post-solve bookkeeping mismatch cannot invalidate a
    physically completed Fluent step.
    """

    elapsed = float(current["flow_time_s"]) - float(previous["flow_time_s"])
    if elapsed <= 0.0:
        raise RuntimeError(
            f"physical time did not advance: previous={previous}, current={current}"
        )
    result: dict[str, Any] = {"elapsed_physical_time_s": elapsed}
    reference_rates = {
        "liquid": transient07j.LIQUID_FEED_KG_S,
        "vapor": transient07j.VAPOR_FEED_KG_S,
    }
    for phase in ("liquid", "vapor"):
        storage_rate = (
            float(current[f"{phase}_inventory_kg"])
            - float(previous[f"{phase}_inventory_kg"])
        ) / elapsed
        average_boundary_flux = 0.5 * (
            float(previous[f"{phase}_net_kgs"])
            + float(current[f"{phase}_net_kgs"])
        )
        residual = storage_rate - average_boundary_flux
        result.update(
            {
                f"{phase}_storage_rate_kg_s": storage_rate,
                f"{phase}_trapezoidal_boundary_flux_kg_s": average_boundary_flux,
                f"{phase}_storage_closure_residual_kg_s": residual,
                f"{phase}_storage_closure_percent_of_full_feed_reference": (
                    abs(residual) / reference_rates[phase] * 100.0
                ),
            }
        )
    result["storage_closure_method"] = (
        "inventory finite difference minus trapezoidal endpoint boundary flux; "
        "setup-07l *_net_kgs schema; diagnostic approximation"
    )
    return result


def transcript_failures(text: str) -> list[str]:
    patterns = {
        "floating point exception": r"floating point exception|\bFPE\b",
        "segmentation fault": r"SIGSEGV|segmentation fault",
        "AMG divergence": r"AMG.*diverg",
        "node/server shutdown": r"Node-\d+.*shutdown|server.*shutdown",
    }
    return [label for label, pattern in patterns.items() if re.search(pattern, text, re.I)]


def row_gate(
    row: Mapping[str, Any], previous: Mapping[str, Any], transcript_text: str
) -> list[str]:
    failures = rest07l.rest_gate(row, previous)
    for key, value in row.items():
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            failures.append(f"non-finite {key}={value}")
    courant = float(row["latest_global_courant"])
    if not math.isfinite(courant) or courant > MAX_VOF_COURANT:
        failures.append(f"Global Courant {courant} exceeds {MAX_VOF_COURANT}")
    if float(row["liquid_vf_min"]) < -1.0e-8 or float(row["liquid_vf_max"]) > 1.0 + 1.0e-8:
        failures.append(
            f"VOF bounds [{row['liquid_vf_min']}, {row['liquid_vf_max']}]"
        )
    if max(abs(float(row["pressure_min_pa"])), abs(float(row["pressure_max_pa"]))) > 1.0e7:
        failures.append("domain pressure magnitude exceeds 1e7 Pa")
    if abs(float(row["velocity_max_ms"])) > 100.0:
        failures.append(f"domain maximum velocity {row['velocity_max_ms']} exceeds 100 m/s")
    if float(row["brine_face_liquid_vf_min"]) < 0.99:
        failures.append(
            "brine face lost full liquid coverage: "
            f"minimum VF={row['brine_face_liquid_vf_min']}"
        )
    for phase in ("liquid", "vapor"):
        closure = abs(float(row[f"{phase}_storage_closure_residual_kg_s"]))
        if closure > 100.0:
            failures.append(f"{phase} storage closure residual {closure} exceeds 100 kg/s")
    failures.extend(transcript_failures(transcript_text))
    return sorted(set(failures))


def save_pair(solver: Any, label: str) -> dict[str, Any]:
    case = remote_join(f"{RUN_LABEL}_{label}.cas.h5")
    data = remote_join(f"{RUN_LABEL}_{label}.dat.h5")
    if remote_file_exists(solver, case) or remote_file_exists(solver, data):
        raise FileExistsError(f"refusing to overwrite remote checkpoint {label}")
    sweep.write_case_data_pair(solver, case, data, f"07n_a_{label}")
    return {
        "case": remote_hash(solver, case, f"{label}_case"),
        "data": remote_hash(solver, data, f"{label}_data"),
        "eligible_parent": False,
    }


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    manifest_path = LOCAL_ROOT / "pilot_manifest.json"
    physical_path = LOCAL_ROOT / "physical_history.csv"
    residual_path = LOCAL_ROOT / "residual_history.csv"
    transcript_path = LOCAL_ROOT / "pilot_transcript.trn"
    lock_path = LOCAL_ROOT / "pilot_writer.lock"
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite pilot attempt: {manifest_path}")
    stage0_sha = local_sha256(STAGE0_MANIFEST)
    if stage0_sha != EXPECTED_STAGE0_SHA256:
        raise RuntimeError(
            f"Stage-0 manifest checksum mismatch: expected={EXPECTED_STAGE0_SHA256} actual={stage0_sha}"
        )
    stage0 = json.loads(STAGE0_MANIFEST.read_text(encoding="utf-8"))
    if CANDIDATE_MODE == "faceproxy":
        candidate = stage0["candidates"][0]
        candidate_level = float(candidate["target_level_y_m"])
        candidate_cells = EXPECTED_MARKED_CELLS
    elif CANDIDATE_MODE == "mesh-selection-plateau":
        plateau = stage0["selection_plateau"]
        candidate = plateau
        candidate_level = float(plateau["recommended_centered_threshold_y_m"])
        candidate_cells = int(plateau["recommended_centered_threshold_marked_cells"])
        if stage0.get("status") != "accepted":
            raise RuntimeError(f"Stage-0 selection diagnostic is not accepted: {stage0}")
    else:
        raise RuntimeError(f"unsupported CANDIDATE_MODE={CANDIDATE_MODE}")
    if not math.isclose(
        candidate_level, TARGET_LEVEL_Y_M, rel_tol=0.0, abs_tol=1e-14
    ) or candidate_cells != EXPECTED_MARKED_CELLS:
        raise RuntimeError(f"Stage-0 candidate mismatch: {candidate}")

    payload: dict[str, Any] = {
        "schema_version": 1,
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "server_id": args.server_id,
        "status": "running",
        "classification": RUN_CLASSIFICATION,
        "eligible_parent": False,
        "adaptive_extension_eligible": False,
        "settings_carrier_case": REMOTE_CARRIER_CASE,
        "data_files_read_before_fresh_t0": [],
        "stage0_manifest": str(STAGE0_MANIFEST),
        "stage0_manifest_sha256": stage0_sha,
        "candidate_mode": CANDIDATE_MODE,
        "candidate_basis": CANDIDATE_BASIS,
        "candidate_limitation": CANDIDATE_LIMITATION,
        "target_level_y_m": TARGET_LEVEL_Y_M,
        "expected_marked_cells": EXPECTED_MARKED_CELLS,
        "expected_liquid_volume_m3": EXPECTED_LIQUID_VOLUME_M3,
        "expected_liquid_inventory_kg": EXPECTED_LIQUID_INVENTORY_KG,
        "time_step_size_s": TIME_STEP_SIZE_S,
        "inner_iterations_per_step": INNER_ITERATIONS,
        "target_physical_steps": TARGET_STEPS,
        "target_flow_time_s": TARGET_STEPS * TIME_STEP_SIZE_S,
        "gravity_time_scale_note": GRAVITY_TIME_SCALE_NOTE,
        "unchanged_contract": (
            "case-only 07l settings carrier; zero feed; brine wall; steam pressure outlet; "
            "transient explicit VOF; PISO/PRESTO/Geo-Reconstruct/WFGC; RNG k-epsilon; "
            "Energy off; DPM zero/off; EWF off; no sources/sinks"
        ),
        "physical_steps_completed": 0,
        "physical_steps_observed": 0,
        "checkpoints": {},
        "steps": [],
        "started_epoch": time.time(),
        "controller_pid": os.getpid(),
    }
    write_manifest(manifest_path, payload, create=True)
    rows: list[dict[str, Any]] = []
    solver: Any | None = None
    transcript_started = False
    transcript_remote = remote_join(f"{RUN_LABEL}_pilot.trn")
    register_created = False
    try:
        with exclusive_writer_lock(GLOBAL_WRITER_LOCK), exclusive_writer_lock(lock_path):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                start_transcript=True,
            )
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_case_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError(f"exclusive ownership unresolved: {clients!r}")
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            if payload["fluent_version"] != EXPECTED_VERSION:
                raise RuntimeError(f"unexpected Fluent version: {payload['fluent_version']}")
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            if not remote_file_exists(solver, REMOTE_CARRIER_CASE):
                raise FileNotFoundError(f"carrier case missing: {REMOTE_CARRIER_CASE}")
            if remote_file_exists(solver, transcript_remote):
                raise FileExistsError(f"refusing to overwrite remote transcript: {transcript_remote}")
            payload["carrier_case_hash"] = remote_hash(
                solver, REMOTE_CARRIER_CASE, "carrier_case"
            )
            solver.settings.file.read_case(file_name=REMOTE_CARRIER_CASE)
            time.sleep(2.0)
            payload["live_parallel_runtime_after_case_load"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            payload["case_only_preinitialization_gate"] = complete_gate(solver)
            if not payload["case_only_preinitialization_gate"]["passed"]:
                raise RuntimeError("case-only preinitialization gate failed")

            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass
            solver.settings.file.start_transcript(file_name=transcript_remote)
            transcript_started = True
            controls = solver.settings.solution.run_calculation.transient_controls
            payload["transient_controls_before"] = controls.get_state()
            controls.time_step_size.set_state(TIME_STEP_SIZE_S)
            controls.max_iter_per_time_step.set_state(INNER_ITERATIONS)
            solver.tui.define.models.multiphase.volume_fraction_parameters.courant_number(
                MAX_VOF_COURANT
            )
            payload["transient_controls_after"] = controls.get_state()
            if not math.isclose(
                float(prepare07l.nested(payload["transient_controls_after"], "time_step_size")),
                TIME_STEP_SIZE_S,
                rel_tol=0.0,
                abs_tol=1e-14,
            ) or int(
                prepare07l.nested(
                    payload["transient_controls_after"], "max_iter_per_time_step"
                )
            ) != INNER_ITERATIONS:
                raise RuntimeError("transient-control readback mismatch")

            sweep.configure_residual_history(solver, 10000)
            sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
            sweep.maybe_initialize(solver, "hybrid")
            if not complete_gate(solver)["passed"]:
                raise RuntimeError("post-initialization model/boundary gate failed")
            registers = solver.settings.solution.cell_registers
            if REGISTER_NAME in registers.get_object_names():
                raise FileExistsError(f"register already exists: {REGISTER_NAME}")
            solver.tui.mesh.adapt.cell_registers.add(
                REGISTER_NAME,
                "type",
                "hexahedron",
                "inside?",
                "yes",
                "max-point",
                POOL_MAXIMUM_XZ_M[0],
                TARGET_LEVEL_Y_M,
                POOL_MAXIMUM_XZ_M[1],
                "min-point",
                *POOL_MINIMUM_M,
            )
            register_created = True
            payload["register_readback"] = registers[REGISTER_NAME].get_state()
            solver.settings.solution.initialization.patch.calculate_patch(
                domain="phase-2",
                cell_zones=[],
                registers=[REGISTER_NAME],
                variable="mp",
                reference_frame="Relative to Cell Zone",
                use_custom_field_function=False,
                value=1.0,
            )
            sweep.set_verified_iteration_label(solver, 0)
            clock0 = transient07j.runtime_clock(solver)
            if int(clock0["time_step"]) != 0 or not math.isclose(
                float(clock0["flow_time_s"]), 0.0, abs_tol=1e-15
            ):
                raise RuntimeError(f"fresh time-zero clock is not zero: {clock0}")
            t0_metrics = rest07l.physical_metrics(solver, 0)
            t0 = {
                **t0_metrics,
                **clock0,
                **rest07l.inventory(t0_metrics, DOMAIN_VOLUME_M3),
                **extrema(solver, "07n_a_t0"),
            }
            transcript_text = sweep.remote_text_read_best_effort(solver, transcript_remote)
            marked = [int(v.replace(",", "")) for v in re.findall(r"([\d,]+)\s+cells marked", transcript_text, re.I)]
            payload["marked_cell_counts_seen"] = marked
            if not marked or marked[-1] != EXPECTED_MARKED_CELLS:
                raise RuntimeError(
                    f"marked-cell count mismatch expected={EXPECTED_MARKED_CELLS} actual={marked}"
                )
            actual_volume = (
                float(t0["domain_volume_avg_liquid_volume_fraction"]) * DOMAIN_VOLUME_M3
            )
            t0["liquid_volume_m3"] = actual_volume
            if not math.isclose(
                actual_volume, EXPECTED_LIQUID_VOLUME_M3, rel_tol=2.0e-6, abs_tol=1.0e-7
            ):
                raise RuntimeError(
                    f"time-zero liquid-volume mismatch expected={EXPECTED_LIQUID_VOLUME_M3} actual={actual_volume}"
                )
            if float(t0["brine_face_liquid_vf_min"]) < 0.99:
                raise RuntimeError(f"time-zero brine face not liquid-filled: {t0}")
            payload["time_zero_metrics_before_save"] = t0
            payload["post_patch_gate"] = complete_gate(solver)
            if not payload["post_patch_gate"]["passed"]:
                raise RuntimeError("post-patch model/boundary gate failed")
            payload["checkpoints"]["time_zero"] = save_pair(solver, "time_zero")

            t0_pair = payload["checkpoints"]["time_zero"]
            solver.settings.file.read_case(file_name=t0_pair["case"]["path"])
            solver.settings.file.read_data(file_name=t0_pair["data"]["path"])
            time.sleep(2.0)
            payload["cold_reload_gate"] = complete_gate(solver)
            payload["cold_reload_clock"] = transient07j.runtime_clock(solver)
            if not payload["cold_reload_gate"]["passed"]:
                raise RuntimeError("cold-reload settings gate failed")
            if int(payload["cold_reload_clock"]["time_step"]) != 0:
                raise RuntimeError(f"cold-reload clock mismatch: {payload['cold_reload_clock']}")
            previous = {
                **rest07l.physical_metrics(solver, 0),
                **payload["cold_reload_clock"],
            }
            previous.update(rest07l.inventory(previous, DOMAIN_VOLUME_M3))
            payload["time_zero_metrics_after_cold_reload"] = {
                **previous,
                **extrema(solver, "07n_a_t0_reload"),
            }
            write_manifest(manifest_path, payload)

            for step in range(1, TARGET_STEPS + 1):
                step_started = time.time()
                solver.settings.solution.run_calculation.dual_time_iterate(
                    time_step_count=1, max_iter_per_step=INNER_ITERATIONS
                )
                clock = transient07j.runtime_clock(solver)
                clock_failures = clock_gate(clock, step)
                if clock_failures:
                    raise HardGateError("; ".join(clock_failures))
                payload["physical_steps_observed"] = step
                payload["last_observed_clock"] = dict(clock)
                payload["last_heartbeat_epoch"] = time.time()
                write_manifest(manifest_path, payload)
                metrics = rest07l.physical_metrics(solver, step)
                row: dict[str, Any] = {
                    **metrics,
                    **clock,
                    **rest07l.inventory(metrics, DOMAIN_VOLUME_M3),
                    **extrema(solver, f"07n_a_step{step}"),
                }
                row.update(closed_rest_storage_closure(previous, row))
                transcript_text = sweep.remote_text_read_best_effort(
                    solver, transcript_remote
                )
                courant_values = rest07l.parse_global_courant(transcript_text)
                row["latest_global_courant"] = (
                    courant_values[-1] if courant_values else math.nan
                )
                residual_last, residual_rows = latest_residual_row(solver)
                row["end_step_continuity_residual"] = continuity_value(residual_last)
                row["residual_iteration"] = residual_last["iteration"]
                row["wall_seconds"] = time.time() - step_started
                failures: list[str] = []
                failures.extend(row_gate(row, previous, transcript_text))
                gate = complete_gate(solver)
                if not gate["passed"]:
                    failures.append(f"DPM/source/EWF/boundary/method gate failed: {gate}")
                rows.append(row)
                payload["physical_steps_completed"] = step
                payload["last_heartbeat_epoch"] = time.time()
                payload["steps"].append(
                    {
                        "step": step,
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
                if step in CHECKPOINT_STEPS:
                    checkpoint = save_pair(solver, f"checkpoint_step{step}")
                    payload["checkpoints"][str(step)] = checkpoint
                    payload["steps"][-1]["checkpoint"] = checkpoint
                write_manifest(manifest_path, payload)
                print(
                    f"07n-a pilot: step {step}/{TARGET_STEPS}; "
                    f"t={clock['flow_time_s']:.6g}s; "
                    f"continuity={row['end_step_continuity_residual']:.6g}; "
                    f"Co={row['latest_global_courant']:.6g}; "
                    f"M_l={row['liquid_inventory_kg']:.9g}kg",
                    flush=True,
                )
                previous = row

            continuity_tail = [
                float(row["end_step_continuity_residual"]) for row in rows[-2:]
            ]
            residual_gate_passed = len(continuity_tail) == 2 and all(
                value <= 0.01 for value in continuity_tail
            )
            payload.update(
                {
                    "status": "completed",
                    "classification": FINAL_CLASSIFICATION,
                    "eligible_parent": False,
                    "adaptive_extension_eligible": residual_gate_passed,
                    "residual_promotion_gate": {
                        "required": "two consecutive end-step continuity residuals <= 0.01",
                        "tail": continuity_tail,
                        "passed": residual_gate_passed,
                    },
                    "acceptance_limitation": ACCEPTANCE_LIMITATION,
                    "completed_epoch": time.time(),
                }
            )
            if residual_gate_passed:
                endpoint = payload["checkpoints"][str(TARGET_STEPS)]
                endpoint["eligible_parent"] = True
                endpoint["eligibility_scope"] = ELIGIBILITY_SCOPE
            write_manifest(manifest_path, payload)
            return 0
    except HardGateError as exc:
        payload.update(
            {
                "status": "terminal",
                "classification": "terminal diagnostic",
                "eligible_parent": False,
                "adaptive_extension_eligible": False,
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
                "adaptive_extension_eligible": False,
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
        if solver is not None and register_created:
            # The register is part of saved case evidence; do not mutate the
            # final field merely to remove it.  Record its existence instead.
            payload["final_register_disposition"] = (
                "retained in saved attempt case as the explicit pool-definition register"
            )
            try:
                write_manifest(manifest_path, payload)
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
