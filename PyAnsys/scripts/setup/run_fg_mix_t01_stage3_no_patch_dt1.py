#!/usr/bin/env python3
"""Prepare and submit FG-MIX-T01 Stage-3 NP-DT1.

NP-DT1 is an independently prepared no-patch transient control:

* source field: the verified unpatched steady C1375 parent;
* brine and steam pressure outlets: 1.120 MPa gauge;
* transient method: bounded second-order, current PISO settings, implicit
  Mixture volume fraction, and 20 maximum iterations per timestep;
* timestep: 2.5e-4 s;
* Fluent-native run: 200 transient timesteps, nominally 0.05 s.

This script prepares the start pair and submits one Fluent-native journal. It
does not initialize, patch, or loop over solver iterations from Python.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_resume_case_data  # noqa: E402
import build_02e_y010_campaign as y010  # noqa: E402
import build_fg_mix_t01_stage1_candidates as stage1  # noqa: E402
import build_fg_mix_t01_stage2_start_states as stage2  # noqa: E402


REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
SOURCE_CASE = (
    REMOTE_DIR
    + r"\FG-MIX-T01-S1-C1375-brine-p1137p5kpa-unpatched-preinit-"
    + r"20260816T102830Z-iter1000-20260816T104203Z.cas.h5"
)
SOURCE_DATA = SOURCE_CASE[:-7] + ".dat.h5"
EXACT_MESH_NAME = "Full-geomV2-231kcells.msh.h5"
STEAM_PRESSURE_PA = 1_120_000.0
BRINE_PRESSURE_PA = 1_120_000.0
TIME_STEP_S = 2.5e-4
TRANSIENT_STEPS = 200
MAX_ITER_PER_TIME_STEP = 20
TRANSIENT_FORMULATION = "unsteady-2nd-order-bounded"
RESIDUAL_HISTORY_SIZE = 1_200


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def set_optional(obj: Any, attribute: str, value: Any) -> None:
    try:
        setattr(obj, attribute, value)
    except Exception:
        pass


def ensure_absent(solver: Any, paths: list[str]) -> None:
    existing = [path for path in paths if remote_file_exists(solver, path)]
    if existing:
        raise FileExistsError("Refusing to overwrite NP-DT1 artifacts: " + ", ".join(existing))


def pressure_value(solver: Any, zone: str) -> float:
    state = safe_get_state(
        solver.settings.setup.boundary_conditions.pressure_outlet[zone],
        f"{zone} pressure",
    )
    value = nested(state, "phase", "mixture", "momentum", "gauge_pressure", "value")
    if value is None:
        raise RuntimeError(f"Could not read mixture gauge pressure for {zone}: {state}")
    return float(value)


def configure_flux_monitors(solver: Any, zones: Mapping[str, str]) -> list[dict[str, Any]]:
    """Create phase-separated outlet flux histories without creating a patch."""

    flux = solver.settings.solution.report_definitions.flux
    definitions: list[dict[str, Any]] = []
    for phase in ("phase-1", "phase-2"):
        for role in ("brine_outlet", "steam_outlet"):
            name = f"fg_mix_t01_s3_np_dt1_flux_{phase.replace('-', '')}_{role}"
            report = y010._replace_named_report(flux, name)
            report.report_type = "flux-massflow"
            report = flux[name]
            report.boundaries = [zones[role]]
            report.phase = phase
            set_optional(report, "per_selection", False)
            set_optional(report, "average_over", 1)
            set_optional(report, "retain_instantaneous_values", True)
            set_optional(report, "create_report_file", True)
            set_optional(report, "create_report_plot", True)
            state = report.get_state()
            if state.get("report_type") != "flux-massflow":
                raise RuntimeError(f"Flux report type readback failed for {name}: {state}")
            if state.get("boundaries") != [zones[role]]:
                raise RuntimeError(f"Flux report boundary readback failed for {name}: {state}")
            if state.get("phase") != phase:
                raise RuntimeError(f"Flux report phase readback failed for {name}: {state}")
            definitions.append({"name": name, "phase": phase, "surface": zones[role], "state": state})
    return definitions


def configure_transient(solver: Any) -> dict[str, Any]:
    controls = stage2.configure_transient_controls(solver)
    if controls["solver"].get("time") != TRANSIENT_FORMULATION:
        raise RuntimeError(f"Transient formulation readback failed: {controls}")
    if controls["transient_controls"].get("time_step_size") != TIME_STEP_S:
        raise RuntimeError(f"Timestep readback failed: {controls}")
    if controls["transient_controls"].get("max_iter_per_time_step") != MAX_ITER_PER_TIME_STEP:
        raise RuntimeError(f"Maximum-iteration readback failed: {controls}")
    return controls


def write_pair(solver: Any, case_file: str, data_file: str) -> None:
    solver.settings.file.write_case(file_name=case_file)
    solver.settings.file.write_data(file_name=data_file)
    if not all(remote_file_exists(solver, path) for path in (case_file, data_file)):
        raise RuntimeError(f"NP-DT1 start pair was not written: {case_file}, {data_file}")


def render_journal(artifacts: Mapping[str, str]) -> str:
    return "\n".join(
        [
            "; FG-MIX-T01 Stage-3 NP-DT1 no-patch control",
            "; Steady parent -> transient; both pressure outlets 1.120 MPa gauge.",
            "; No Hybrid Initialization and no Y010 patch are permitted.",
            "; Fluent owns 200 transient timesteps and paired endpoint write.",
            "/file/confirm-overwrite? no",
            f'/file/read-case "{posix(artifacts["start_case"])}"',
            f'/file/read-data "{posix(artifacts["start_data"])}"',
            f"/solve/set/transient-controls/time-step-size {TIME_STEP_S}",
            f"/solve/monitors/residual/n-save {RESIDUAL_HISTORY_SIZE}",
            "/solve/monitors/residual/print? yes",
            f'/file/start-transcript "{posix(artifacts["transcript"])}"',
            f"/solve/iterate {TRANSIENT_STEPS}",
            f'/file/write-case-data "{posix(artifacts["endpoint_case"])}"',
            f'/plot/residuals-set/plot-to-file "{posix(artifacts["residual_file"])}"',
            "/plot/residuals",
            "/plot/residuals-set/end-plot-to-file",
            "/file/stop-transcript",
            "; NP-DT1 native journal submitted; Fluent remains open.",
            "",
        ]
    )


def write_remote_journal(solver: Any, remote_journal: str, journal: str) -> None:
    body = " ".join(
        f'(display "{quote_scheme_string(line)}") (newline)' for line in journal.splitlines()
    )
    expression = (
        f'(with-output-to-file "{quote_scheme_string(posix(remote_journal))}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, remote_journal):
        raise RuntimeError(f"Remote NP-DT1 journal was not created: {remote_journal}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument(
        "--run-stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        help="UTC stamp used for NP-DT1 artifact names",
    )
    parser.add_argument("--local-journal", required=True, type=Path)
    parser.add_argument("--manifest-json", required=True, type=Path)
    args = parser.parse_args()

    solver = connect(server_id=args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    for path in (SOURCE_CASE, SOURCE_DATA):
        if not remote_file_exists(solver, path):
            raise FileNotFoundError(f"Verified steady parent input is not visible: {path}")

    stem = f"FG-MIX-T01-S3-NP-DT1-0p05s-{args.run_stamp}"
    remote_root = PureWindowsPath(REMOTE_DIR)
    artifacts = {
        "start_case": str(remote_root / f"{stem}-start.cas.h5"),
        "start_data": str(remote_root / f"{stem}-start.dat.h5"),
        "endpoint_case": str(remote_root / f"{stem}.cas.h5"),
        "endpoint_data": str(remote_root / f"{stem}.dat.h5"),
        "transcript": str(remote_root / f"{stem}.trn"),
        "residual_file": str(remote_root / f"{stem}-residuals.out"),
        "remote_journal": str(remote_root / f"{stem}.jou"),
    }
    ensure_absent(solver, list(artifacts.values()))

    load_resume_case_data(solver, SOURCE_CASE, SOURCE_DATA)
    zones = stage2.resolve_zones(solver)
    source_contract = stage1.read_contract(solver, zones)
    stage1.validate_common_contract(source_contract)
    if source_contract["pressures_pa"]["brine_outlet"] != 1_137_500.0:
        raise RuntimeError(f"Steady parent is not the accepted C1375 endpoint: {source_contract}")
    if source_contract["pressures_pa"]["steam_outlet"] != STEAM_PRESSURE_PA:
        raise RuntimeError(f"Steady parent steam pressure changed: {source_contract}")

    controls = configure_transient(solver)
    stage1.set_brine_pressure(solver, zones["brine_outlet"], BRINE_PRESSURE_PA)
    if pressure_value(solver, zones["brine_outlet"]) != BRINE_PRESSURE_PA:
        raise RuntimeError("NP-DT1 brine pressure readback failed")
    if pressure_value(solver, zones["steam_outlet"]) != STEAM_PRESSURE_PA:
        raise RuntimeError("NP-DT1 steam pressure readback failed")
    flux_monitors = configure_flux_monitors(solver, zones)

    # No initialization call and no patch call occur in this script.
    write_pair(solver, artifacts["start_case"], artifacts["start_data"])
    load_resume_case_data(solver, artifacts["start_case"], artifacts["start_data"])
    reload_controls = safe_get_state(
        solver.settings.solution.run_calculation.transient_controls,
        "NP-DT1 reload transient controls",
    )
    reload_solver = safe_get_state(solver.settings.setup.general.solver, "NP-DT1 reload solver")
    reload_brine = pressure_value(solver, zones["brine_outlet"])
    reload_steam = pressure_value(solver, zones["steam_outlet"])
    if reload_solver.get("time") != TRANSIENT_FORMULATION:
        raise RuntimeError(f"Reloaded solver is not bounded second-order transient: {reload_solver}")
    if reload_controls.get("flow_time") != 0 or reload_controls.get("time_step_count") != 0:
        raise RuntimeError(f"Reloaded NP-DT1 start is not at flow time zero: {reload_controls}")
    if reload_controls.get("time_step_size") != TIME_STEP_S:
        raise RuntimeError(f"Reloaded NP-DT1 timestep mismatch: {reload_controls}")
    if reload_controls.get("max_iter_per_time_step") != MAX_ITER_PER_TIME_STEP:
        raise RuntimeError(f"Reloaded NP-DT1 iteration cap mismatch: {reload_controls}")
    if reload_brine != BRINE_PRESSURE_PA or reload_steam != STEAM_PRESSURE_PA:
        raise RuntimeError(f"Reloaded NP-DT1 pressure mismatch: brine={reload_brine}, steam={reload_steam}")

    journal = render_journal(artifacts)
    local_journal = args.local_journal.expanduser().resolve()
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")
    write_remote_journal(solver, artifacts["remote_journal"], journal)

    payload = {
        "campaign": "FG-MIX-T01",
        "stage": "S3",
        "test": "NP-DT1",
        "purpose": "no-patch transient control from the developed steady parent",
        "source_case": SOURCE_CASE,
        "source_data": SOURCE_DATA,
        "start_case": artifacts["start_case"],
        "start_data": artifacts["start_data"],
        "endpoint_case": artifacts["endpoint_case"],
        "endpoint_data": artifacts["endpoint_data"],
        "mesh": source_contract["mesh"],
        "mesh_readback": {"cells": 231376, "nodes": 697078},
        "y010_patch": False,
        "hybrid_initialization": False,
        "brine_pressure_pa": BRINE_PRESSURE_PA,
        "steam_pressure_pa": STEAM_PRESSURE_PA,
        "solver_formulation": TRANSIENT_FORMULATION,
        "time_step_s": TIME_STEP_S,
        "native_transient_steps": TRANSIENT_STEPS,
        "physical_horizon_s": TRANSIENT_STEPS * TIME_STEP_S,
        "max_iter_per_time_step": MAX_ITER_PER_TIME_STEP,
        "source_contract": source_contract,
        "transient_controls": controls,
        "reload_readback": {
            "solver": reload_solver,
            "transient_controls": reload_controls,
            "brine_pressure_pa": reload_brine,
            "steam_pressure_pa": reload_steam,
        },
        "flux_monitors": flux_monitors,
        "transcript": artifacts["transcript"],
        "residual_file": artifacts["residual_file"],
        "remote_journal": artifacts["remote_journal"],
        "local_journal": str(local_journal),
        "status": "SUBMITTED_NATIVE_RUN",
        "fluent_version": str(solver.get_fluent_version()),
    }
    manifest_path = args.manifest_json.expanduser().resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str), flush=True)
    solver.settings.file.read_journal(file_name_list=[artifacts["remote_journal"]])
    print(f"native_journal_submitted: {artifacts['remote_journal']}", flush=True)
    print(f"manifest_json: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
