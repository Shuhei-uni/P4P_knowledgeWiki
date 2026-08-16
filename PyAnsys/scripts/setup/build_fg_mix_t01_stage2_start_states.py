#!/usr/bin/env python3
"""Build the two FG-MIX-T01 Stage-2 transient startup states.

The accepted Stage-1 C1375 case/data endpoint is the only source field.  The
builder creates two independent, paired case/data artifacts:

* INIT-S: load the developed C1375 field, switch to the common provisional
  transient method, set T-PO-1, then patch Y010 once;
* INIT-H: load the same C1375 case definition, switch to the same transient
  method, set T-PO-1, Hybrid Initialize, then patch the identical Y010 once.

Fluent owns the initialization and field writes.  This script never advances a
transient timestep and never runs a client-side iteration loop.
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

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_resume_case_data  # noqa: E402
import build_02e_y010_campaign as y010  # noqa: E402
import build_fg_mix_t01_stage1_candidates as stage1  # noqa: E402


EXACT_MESH_NAME = stage1.EXACT_MESH_NAME
DEFAULT_REMOTE_DIR = stage1.DEFAULT_REMOTE_DIR
DEFAULT_SOURCE_CASE = (
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
    r"\FG-MIX-T01-S1-C1375-brine-p1137p5kpa-unpatched-preinit-"
    r"20260816T102830Z-iter1000-20260816T104203Z.cas.h5"
)
DEFAULT_SOURCE_DATA = DEFAULT_SOURCE_CASE[:-7] + ".dat.h5"
TPO1_BRINE_PRESSURE_PA = 1_200_000.0
TIME_STEP_S = 2.5e-4
MAX_ITER_PER_TIME_STEP = 20
TRANSIENT_FORMULATION = "unsteady-2nd-order-bounded"
MONITOR_PREFIX = "fg_mix_t01_s2"
MESH_CELLS = 231_376
MESH_NODES = 697_078

BRANCHES = (
    ("FG-MIX-T01-S2-INIT-S", "INIT-S", False, "developed C1375 field"),
    ("FG-MIX-T01-S2-INIT-H", "INIT-H", True, "Fluent Hybrid Initialization"),
)


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def ensure_absent(solver: Any, paths: list[str]) -> None:
    existing = [path for path in paths if remote_file_exists(solver, path)]
    if existing:
        raise FileExistsError("Refusing to overwrite existing Stage-2 artifacts: " + ", ".join(existing))


def resolve_zones(solver: Any) -> dict[str, str]:
    return y010.resolve_zones(solver)


def set_optional(obj: Any, attribute: str, value: Any) -> None:
    try:
        setattr(obj, attribute, value)
    except Exception:
        pass


def configure_monitors(solver: Any, zones: Mapping[str, str], fluid_zone: str) -> dict[str, Any]:
    """Create the common Stage-2 monitor package after registers exist."""

    root = solver.settings.solution.report_definitions
    flux = root.flux
    volume = root.volume
    surfaces = {
        "liquid_inlet": zones["liquid_inlet"],
        "steam_inlet": zones["steam_inlet"],
        "brine_outlet": zones["brine_outlet"],
        "steam_outlet": zones["steam_outlet"],
    }
    definitions: list[dict[str, Any]] = []
    for phase in ("mixture", "phase-1", "phase-2"):
        for role, surface in surfaces.items():
            name = f"{MONITOR_PREFIX}_flux_{phase.replace('-', '')}_{role}"
            report = y010._replace_named_report(flux, name)
            report.report_type = "flux-massflow"
            report.boundaries = [surface]
            set_optional(report, "per_selection", False)
            set_optional(report, "average_over", 1)
            set_optional(report, "retain_instantaneous_values", True)
            report.phase = phase
            set_optional(report, "create_report_file", True)
            set_optional(report, "create_report_plot", True)
            definitions.append(
                {
                    "name": name,
                    "kind": "flux",
                    "phase": phase,
                    "surface": surface,
                    "state": report.get_state(),
                }
            )

    volumes = (
        ("y010_geometric_volume", y010.Y010_REGISTER, "volume-integral", "cell-volume", "mixture"),
        ("y010_liquid_volume", y010.Y010_REGISTER, "volume-integral", "phase-2-vof", "mixture"),
        ("y010_liquid_mass", y010.Y010_REGISTER, "volume-mass", None, "phase-2"),
        ("y030_geometric_volume", y010.Y030_REGISTER, "volume-integral", "cell-volume", "mixture"),
        ("y030_liquid_volume", y010.Y030_REGISTER, "volume-integral", "phase-2-vof", "mixture"),
        ("y030_liquid_mass", y010.Y030_REGISTER, "volume-mass", None, "phase-2"),
        ("total_liquid_volume", fluid_zone, "volume-integral", "phase-2-vof", "mixture"),
    )
    for suffix, register, report_type, field, phase in volumes:
        name = f"{MONITOR_PREFIX}_inventory_{suffix}"
        report = y010._replace_named_report(volume, name)
        report.report_type = report_type
        report = volume[name]
        report.cell_zones = [register]
        if field is not None:
            report.field = field
        set_optional(report, "per_selection", False)
        set_optional(report, "average_over", 1)
        set_optional(report, "retain_instantaneous_values", True)
        report.phase = phase
        set_optional(report, "create_report_file", True)
        set_optional(report, "create_report_plot", True)
        definitions.append(
            {
                "name": name,
                "kind": "volume",
                "register": register,
                "report_type": report_type,
                "field": field,
                "phase": phase,
                "state": report.get_state(),
            }
        )
    return {
        "prefix": MONITOR_PREFIX,
        "fluid_zone": fluid_zone,
        "count": len(definitions),
        "definitions": definitions,
    }


def configure_transient_controls(solver: Any) -> dict[str, Any]:
    """Apply and read back the common provisional Stage-3 method."""

    solver.settings.setup.general.solver.time = TRANSIENT_FORMULATION
    methods = solver.settings.solution.methods
    methods.p_v_coupling.flow_scheme = "PISO"
    methods.p_v_coupling.neighbor_correction_itr_count = 1
    methods.p_v_coupling.skewness_neighbor_coupling = True

    run = solver.settings.solution.run_calculation
    transient = run.transient_controls
    transient.time_step_size = TIME_STEP_S
    transient.max_iter_per_time_step = MAX_ITER_PER_TIME_STEP
    transient.time_step_count = 0
    transient.flow_time = 0.0

    residual = solver.settings.solution.monitor.residual
    residual.options.n_save = 600
    residual.options.n_display = 600
    equations = residual.equations.get_state()
    for name in equations:
        residual.equations[name].check_convergence = False

    solver_state = safe_get_state(solver.settings.setup.general.solver, "solver")
    method_state = safe_get_state(methods, "methods")
    transient_state = safe_get_state(transient, "transient_controls")
    residual_state = safe_get_state(residual, "residual")
    if solver_state.get("time") != TRANSIENT_FORMULATION:
        raise RuntimeError(f"Transient solver readback mismatch: {solver_state}")
    if method_state.get("p_v_coupling", {}).get("flow_scheme") != "PISO":
        raise RuntimeError(f"PISO readback mismatch: {method_state}")
    if transient_state.get("time_step_size") != TIME_STEP_S:
        raise RuntimeError(f"Timestep readback mismatch: {transient_state}")
    if transient_state.get("max_iter_per_time_step") != MAX_ITER_PER_TIME_STEP:
        raise RuntimeError(f"Inner-iteration readback mismatch: {transient_state}")
    if transient_state.get("time_step_count") != 0 or transient_state.get("flow_time") != 0:
        raise RuntimeError(f"Stage-2 start time readback mismatch: {transient_state}")
    return {
        "solver": solver_state,
        "methods": method_state,
        "transient_controls": transient_state,
        "residual": residual_state,
        "mixture_volume_fraction_note": "Mixture model retains its implicit volume-fraction treatment; no separate VOF formulation control is active.",
    }


def pressure_value(solver: Any, zone: str) -> float:
    state = safe_get_state(solver.settings.setup.boundary_conditions.pressure_outlet[zone], "brine pressure")
    return float(nested(state, "phase", "mixture", "momentum", "gauge_pressure", "value"))


def write_pair(solver: Any, case_file: str, data_file: str) -> None:
    solver.settings.file.write_case(file_name=case_file)
    solver.settings.file.write_data(file_name=data_file)
    ensure_present = [case_file, data_file]
    if not all(remote_file_exists(solver, path) for path in ensure_present):
        raise RuntimeError(f"Stage-2 paired endpoint was not visible after write: {ensure_present}")


def build_branch(
    solver: Any,
    source_case: str,
    source_data: str,
    remote_dir: str,
    stamp: str,
    branch: tuple[str, str, bool, str],
) -> dict[str, Any]:
    case_id, branch_name, hybrid, initialization_description = branch
    stem = f"{case_id}-TPO1-p1200kpa-y010-start-{stamp}"
    case_file = str(PureWindowsPath(remote_dir) / f"{stem}.cas.h5")
    data_file = str(PureWindowsPath(remote_dir) / f"{stem}.dat.h5")
    ensure_absent(solver, [case_file, data_file])

    load_resume_case_data(solver, source_case, source_data)
    zones = resolve_zones(solver)
    source_contract = stage1.read_contract(solver, zones)
    stage1.validate_common_contract(source_contract)
    if source_contract["pressures_pa"]["brine_outlet"] != 1_137_500.0:
        raise RuntimeError(f"Stage-2 source is not the accepted C1375 endpoint: {source_contract}")

    controls = configure_transient_controls(solver)
    pressure_change = stage1.set_brine_pressure(solver, zones["brine_outlet"], TPO1_BRINE_PRESSURE_PA)
    if pressure_value(solver, zones["brine_outlet"]) != TPO1_BRINE_PRESSURE_PA:
        raise RuntimeError("T-PO-1 brine pressure readback failed")

    if hybrid:
        solver.settings.solution.initialization.hybrid_initialize()

    y010_state = y010.create_register(solver, y010.Y010_REGISTER, y010.Y010_MAX)
    y030_state = y010.create_register(solver, y010.Y030_REGISTER, y010.Y030_MAX)
    solver.settings.solution.initialization.patch.calculate_patch(
        domain="phase-2", registers=[y010.Y010_REGISTER], variable="mp", value=1.0
    )
    inventory = y010.inventory_queries(solver, y010.Y010_REGISTER)
    fluid_names = [
        str(name)
        for name in safe_get_state(solver.settings.setup.cell_zone_conditions, "cell zones").get("fluid", {})
        if str(name) != "settings"
    ]
    if len(fluid_names) != 1:
        raise RuntimeError(f"Expected one fluid zone for total-liquid monitor, found {fluid_names}")
    monitors = configure_monitors(solver, zones, fluid_names[0])

    post_contract = stage1.read_contract(solver, zones)
    post_contract["pressures_pa"]["brine_outlet"] = pressure_value(solver, zones["brine_outlet"])
    if post_contract["pressures_pa"]["brine_outlet"] != TPO1_BRINE_PRESSURE_PA:
        raise RuntimeError(f"Post-patch boundary contract mismatch: {post_contract}")
    write_pair(solver, case_file, data_file)

    # Reload the written pair to make the case/data artifact, not the in-memory
    # object tree, the authoritative Stage-2 handoff record.
    load_resume_case_data(solver, case_file, data_file)
    reload_zones = resolve_zones(solver)
    reload_controls = configure_readback(solver)
    reload_pressure = pressure_value(solver, reload_zones["brine_outlet"])
    reload_registers = {
        y010.Y010_REGISTER: safe_get_state(solver.settings.solution.cell_registers[y010.Y010_REGISTER], "Y010 reload"),
        y010.Y030_REGISTER: safe_get_state(solver.settings.solution.cell_registers[y010.Y030_REGISTER], "Y030 reload"),
    }
    if reload_pressure != TPO1_BRINE_PRESSURE_PA:
        raise RuntimeError(f"Reloaded T-PO-1 pressure mismatch: {reload_pressure}")
    if set(reload_registers) != {y010.Y010_REGISTER, y010.Y030_REGISTER}:
        raise RuntimeError(f"Reloaded registers missing: {reload_registers}")

    return {
        "case_id": case_id,
        "branch": branch_name,
        "initialization": initialization_description,
        "hybrid_initialized": hybrid,
        "source_case": source_case,
        "source_data": source_data,
        "case_file": case_file,
        "data_file": data_file,
        "mesh": {
            "path": stage1.DEFAULT_MESH,
            "basename": EXACT_MESH_NAME,
            "cells": MESH_CELLS,
            "nodes": MESH_NODES,
            "handling": "unchanged; inherited from exact-mesh C1375 endpoint; no remeshing/adaptation/scaling",
        },
        "zones": reload_zones,
        "models": safe_get_state(solver.settings.setup.models, "models reload"),
        "source_contract": source_contract,
        "pressure_change": pressure_change,
        "stage2_brine_pressure_pa": TPO1_BRINE_PRESSURE_PA,
        "transient_controls": controls,
        "transient_controls_reload": reload_controls,
        "registers": {
            "created_y010": y010_state,
            "created_y030": y030_state,
            "reloaded": reload_registers,
        },
        "y010_inventory_after_patch": inventory,
        "monitor_package": monitors,
        "flow_time_s": 0.0,
        "timestep_run": False,
        "status": "CASE_DATA_VERIFIED",
        "fluent_version": solver.get_fluent_version(),
    }


def configure_readback(solver: Any) -> dict[str, Any]:
    methods = safe_get_state(solver.settings.solution.methods, "methods reload")
    transient = safe_get_state(solver.settings.solution.run_calculation.transient_controls, "transient reload")
    solver_state = safe_get_state(solver.settings.setup.general.solver, "solver reload")
    return {
        "solver": solver_state,
        "methods": methods,
        "transient_controls": transient,
        "flow_time_s": transient.get("flow_time"),
        "time_step_size_s": transient.get("time_step_size"),
        "max_iter_per_time_step": transient.get("max_iter_per_time_step"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--source-case", default=DEFAULT_SOURCE_CASE)
    parser.add_argument("--source-data", default=DEFAULT_SOURCE_DATA)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument(
        "--stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        help="UTC artifact stamp used to make both Stage-2 pairs unique",
    )
    parser.add_argument("--snapshot-json", required=True)
    args = parser.parse_args()

    if PureWindowsPath(stage1.DEFAULT_MESH).name != EXACT_MESH_NAME:
        raise RuntimeError("The Stage-1 exact mesh constant changed unexpectedly")
    if not args.source_case.lower().endswith("c1375-brine-p1137p5kpa-unpatched-preinit-20260816t102830z-iter1000-20260816t104203z.cas.h5"):
        raise ValueError("Stage-2 source must be the accepted FG-MIX-T01-S1-C1375 endpoint")

    solver = connect(server_id=args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    for path in (args.source_case, args.source_data):
        if not remote_file_exists(solver, path):
            raise FileNotFoundError(f"Stage-2 source is not visible: {path}")

    records = [
        build_branch(
            solver,
            args.source_case,
            args.source_data,
            args.remote_dir,
            args.stamp,
            branch,
        )
        for branch in BRANCHES
    ]
    inventories = {
        record["branch"]: float(
            record["y010_inventory_after_patch"]["values"]["liquid_volume_m3"]["Net"]
        )
        for record in records
    }
    reference_inventory = inventories["INIT-H"]
    inventory_difference = abs(inventories["INIT-S"] - reference_inventory)
    monitor_limited = sorted(
        definition["name"]
        for record in records
        for definition in record["monitor_package"]["definitions"]
        if definition["state"].get("create_report_file") is not True
    )
    equivalence_gate_open = inventory_difference > 1.0e-10 or bool(monitor_limited)
    payload = {
        "campaign": "FG-MIX-T01",
        "stage": "S2",
        "purpose": "matched transient startup states for INIT-S versus INIT-H comparison",
        "status": "CASE_DATA_VERIFIED_EQUIVALENCE_GATE_OPEN" if equivalence_gate_open else "CASE_DATA_VERIFIED",
        "source_candidate": "FG-MIX-T01-S1-C1375",
        "source_case": args.source_case,
        "source_data": args.source_data,
        "mesh": stage1.DEFAULT_MESH,
        "mesh_identity_rule": f"basename must equal {EXACT_MESH_NAME}",
        "mesh_readback": {"cells": MESH_CELLS, "nodes": MESH_NODES},
        "comparison_definition": {
            "brine_outlet_type": "pressure-outlet",
            "brine_outlet_gauge_pressure_pa": TPO1_BRINE_PRESSURE_PA,
            "y010_bounds": {"min": y010.Y010_MIN, "max": y010.Y010_MAX, "inside": True},
            "y010_patch": "phase-2 water-liquid volume fraction = 1.0, once at flow time 0 s",
        },
        "common_transient_method": {
            "solver_time": TRANSIENT_FORMULATION,
            "pressure_velocity_coupling": "PISO",
            "neighbor_correction": {"enabled": True, "iterations": 1},
            "mixture_volume_fraction": "implicit/default Mixture treatment; no separate VOF control active",
            "time_step_s": TIME_STEP_S,
            "max_iterations_per_time_step": MAX_ITER_PER_TIME_STEP,
            "initial_flow_time_s": 0.0,
        },
        "runs_submitted": False,
        "equivalence_gate": {
            "status": "OPEN" if equivalence_gate_open else "READY",
            "y010_liquid_volume_m3": inventories,
            "relative_difference_vs_INIT-H": inventory_difference / reference_inventory,
            "monitor_file_toggle_limited_definitions": monitor_limited,
        },
        "children": records,
        "fluent_version": solver.get_fluent_version(),
    }
    output = Path(args.snapshot_json).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print(f"snapshot_json: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
