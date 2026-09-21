#!/usr/bin/env python3
"""Run the 2,000-iteration inlet-loading discovery on baseline v2.

The prepared v2 pair is preserved as the parent.  Both mass-flow inlets are
set to 25 percent of the previous inlet-loading experiment at active 0 and
are increased linearly, with their ratio held fixed, to the recorded base
targets over 2,000 steady iterations.  The v2 virtual liquid outlet remains
expression-driven; this runner does not replace or retune its source law.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path, PureWindowsPath
import re
import sys
import traceback
from collections.abc import Mapping
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "inspection"), str(ROOT / "scripts" / "setup")]

from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    configure_residual_history,
    data_path,
    ensure_remote_directory,
    remote_file_sha256,
)
from run_p7_e0_ref_discovery import parse_residuals  # noqa: E402


PARENT_ZONE = "separator-purnanto"
LOWER_ZONE = "p71a-v2-virtual-outlet"
LIQUID_BASE_KG_S = 116.92
VAPOR_BASE_KG_S = 80.69
START_MULTIPLIER = 0.25
RAMP_ITERATIONS = 2000
HORIZON = 2000
UPDATE_INTERVAL = 10
CHECKPOINTS = (500, 1000, 1500, 2000)
SETUP_ID = "P71A-V2-INLET-LOADING-RAMP"
COUPLED_PSEUDO_SETUP_ID = "P71A-V2-COUPLED-GLOBAL-PSEUDO-TIME-INLET-RAMP"


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def nested(value: Any, *keys: str | int) -> Any:
    for key in keys:
        if isinstance(value, (list, tuple)) and isinstance(key, int):
            value = value[key] if -len(value) <= key < len(value) else None
        elif isinstance(value, Mapping):
            value = value.get(key)
        else:
            return None
    return value


def as_float(value: Any) -> float:
    if isinstance(value, Mapping):
        if "Net" in value:
            value = value["Net"]
        elif "value" in value:
            value = value["value"]
        elif len(value) == 1:
            value = next(iter(value.values()))
    if isinstance(value, (list, tuple)):
        if len(value) == 1:
            return as_float(value[0])
        if len(value) == 2 and isinstance(value[0], (int, float)):
            return float(value[0])
    return float(value)


def multiplier(active: int) -> float:
    return START_MULTIPLIER + (1.0 - START_MULTIPLIER) * min(max(active, 0) / RAMP_ITERATIONS, 1.0)


def schedule_inlets(solver: Any, active: int) -> dict[str, Any]:
    f = multiplier(active)
    inlet = solver.settings.setup.boundary_conditions.mass_flow_inlet
    liquid = LIQUID_BASE_KG_S * f
    vapor = VAPOR_BASE_KG_S * f
    inlet["liquidinlet"].phase["phase-2"].momentum.mass_flow_rate = liquid
    inlet["steaminlet"].phase["phase-1"].momentum.mass_flow_rate = vapor
    state = safe_get_state(solver.settings.setup.boundary_conditions, "v2 inlet schedule")
    liquid_read = nested(state, "mass_flow_inlet", "liquidinlet", "phase", "phase-2", "momentum", "mass_flow_rate", "value")
    vapor_read = nested(state, "mass_flow_inlet", "steaminlet", "phase", "phase-1", "momentum", "mass_flow_rate", "value")
    require(liquid_read is not None and abs(float(liquid_read) - liquid) < 1e-8, f"liquid inlet readback mismatch: {liquid_read} != {liquid}")
    require(vapor_read is not None and abs(float(vapor_read) - vapor) < 1e-8, f"steam inlet readback mismatch: {vapor_read} != {vapor}")
    return {
        "active_iteration": active,
        "multiplier": f,
        "liquid_inlet_command_kg_s": float(liquid_read),
        "steam_inlet_command_kg_s": float(vapor_read),
    }


def expression_value(solver: Any, name: str) -> float:
    value = solver.settings.setup.named_expressions[name].get_value()
    return as_float(value)


def compute_report(solver: Any, name: str) -> float:
    value = solver.settings.solution.report_definitions.compute(report_defs=[name])
    if isinstance(value, (list, tuple)):
        require(len(value) == 1, f"unexpected report result for {name}: {value}")
        value = value[0]
    return as_float(value)


def applied_absorber(solver: Any) -> float:
    value = solver.settings.results.report.volume_integrals.get_sum(
        cell_zones=[LOWER_ZONE],
        locations={"geometry": [LOWER_ZONE]},
        cell_function="phase-2-user-mass-source",
        current_domain="mixture",
    )
    return as_float(value)


def source_audit(solver: Any) -> dict[str, Any]:
    cells = solver.settings.setup.cell_zone_conditions.fluid
    lower = safe_get_state(cells[LOWER_ZONE], "v2 lower zone")
    parent = safe_get_state(cells[PARENT_ZONE], "v2 parent zone")
    lower_p2 = nested(lower, "phase", "phase-2", "sources")
    lower_mix = nested(lower, "phase", "mixture", "sources") if isinstance(lower, Mapping) else None
    p1_lower = nested(lower, "phase", "phase-1", "sources")
    p1_parent = nested(parent, "phase", "phase-1", "sources")
    require(nested(lower, "phase", "phase-2", "sources", "enable") is True, f"v2 phase-2 source not enabled: {lower_p2}")
    require(nested(lower, "phase", "phase-2", "sources", "terms", "mass", 0, "value") == "P71V2Sink", f"v2 mass source mismatch: {lower_p2}")
    require(nested(lower, "phase", "phase-1", "sources", "enable") is False, f"v2 lower phase-1 source not disabled: {p1_lower}")
    require(nested(parent, "phase", "phase-1", "sources", "enable") is False, f"v2 parent phase-1 source not disabled: {p1_parent}")
    return {
        "lower_zone": LOWER_ZONE,
        "phase2_mass_source": lower_p2,
        "lower_phase1_source": p1_lower,
        "parent_phase1_source": p1_parent,
        "lower_mixture_source": lower_mix,
    }


def audit(solver: Any, active: int | None = None) -> dict[str, Any]:
    zones = safe_get_state(solver.settings.setup.cell_zone_conditions, "v2 cell zones")
    require(set((zones.get("fluid") or {}).keys()) == {PARENT_ZONE, LOWER_ZONE}, f"unexpected v2 fluid zones: {zones}")
    boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "v2 boundaries")
    require("steamoutlet" in (boundaries.get("pressure_outlet") or {}), f"steamoutlet missing: {boundaries}")
    sources = source_audit(solver)
    defs = {}
    for name in ("P71V2Sink", "P71V2Command", "P71V2Removal", "P71V2AvailableVolume"):
        defs[name] = solver.settings.setup.named_expressions[name].definition()
    return {
        "active_iteration": active,
        "fluid_zones": sorted((zones.get("fluid") or {}).keys()),
        "boundaries": {"pressure_outlet": sorted((boundaries.get("pressure_outlet") or {}).keys()), "wall": sorted((boundaries.get("wall") or {}).keys())},
        "named_expression_definitions": defs,
        "named_expression_values": {name: expression_value(solver, name) for name in ("P71V2Command", "P71V2Removal", "P71V2AvailableVolume", "P71V2CommandError")},
        "source_audit": sources,
    }


def configure_coupled_global_pseudo_time(solver: Any) -> dict[str, Any]:
    """Apply only the requested Coupled + global pseudo-time delta."""
    solver.settings.setup.general.solver.time.set_state("steady")
    solver.settings.solution.methods.p_v_coupling.flow_scheme.set_state("Coupled")
    pseudo_method = solver.settings.solution.methods.pseudo_time_method
    pseudo_method.formulation.coupled_solver.set_state("global-time-step")
    pseudo_settings = solver.settings.solution.run_calculation.pseudo_time_settings
    pseudo_settings.time_step_method.time_step_method.set_state("automatic")

    solver_state = safe_get_state(solver.settings.setup.general.solver, "coupled pseudo solver")
    methods_state = safe_get_state(solver.settings.solution.methods, "coupled pseudo methods")
    pseudo_method_state = safe_get_state(pseudo_method, "pseudo-time method")
    pseudo_settings_state = safe_get_state(pseudo_settings, "pseudo-time settings")
    require(solver_state.get("time") == "steady", f"solver formulation changed unexpectedly: {solver_state}")
    require(methods_state.get("p_v_coupling", {}).get("flow_scheme") == "Coupled", f"Coupled readback mismatch: {methods_state}")
    require(pseudo_method_state.get("formulation", {}).get("coupled_solver") == "global-time-step", f"global pseudo-time readback mismatch: {pseudo_method_state}")
    require(pseudo_settings_state.get("time_step_method", {}).get("time_step_method") == "automatic", f"automatic pseudo-time readback mismatch: {pseudo_settings_state}")
    return {
        "solver": solver_state,
        "methods": methods_state,
        "pseudo_time_method": pseudo_method_state,
        "pseudo_time_settings": pseudo_settings_state,
        "controlled_delta": "SIMPLE -> Coupled; pseudo-time off -> Global Time Step with Automatic timestep",
    }


def replace_named(branch: Any, name: str) -> Any:
    if name in set(str(item) for item in branch.get_object_names()):
        branch.delete(name_list=[name])
    branch.create(name=name)
    return branch[name]


def set_optional(obj: Any, name: str, value: Any) -> None:
    try:
        setattr(obj, name, value)
    except Exception:
        pass


def configure_definitions(solver: Any) -> list[str]:
    names: list[str] = []
    flux = solver.settings.solution.report_definitions.flux
    volume = solver.settings.solution.report_definitions.volume
    expressions = solver.settings.solution.report_definitions.single_valued_expression

    def add_flux(name: str, phase: str, surface: str) -> None:
        report = replace_named(flux, name)
        report.report_type = "flux-massflow"
        report = flux[name]
        report.boundaries = [surface]
        report.phase = phase
        for key, value in (("per_selection", False), ("average_over", 1), ("retain_instantaneous_values", True), ("create_report_file", False), ("create_report_plot", False)):
            set_optional(report, key, value)
        state = safe_get_state(report, f"flux report {name}")
        require(state.get("report_type") == "flux-massflow" and state.get("boundaries") == [surface] and state.get("phase") == phase, f"flux report mismatch: {name}: {state}")
        names.append(name)

    add_flux("v2-flux-mixture-steamoutlet", "mixture", "steamoutlet")
    add_flux("v2-flux-phase1-steamoutlet", "phase-1", "steamoutlet")
    add_flux("v2-flux-phase2-steamoutlet", "phase-2", "steamoutlet")
    add_flux("v2-flux-phase2-liquidinlet", "phase-2", "liquidinlet")
    add_flux("v2-flux-phase1-steaminlet", "phase-1", "steaminlet")

    def add_volume(name: str, report_type: str, field: str | None, zones: list[str], phase: str | None = None) -> None:
        report = replace_named(volume, name)
        report.report_type = report_type
        report = volume[name]
        report.cell_zones = zones
        if field is not None:
            report.field = field
        if phase is not None and report_type != "volume-integral":
            report.phase = phase
        for key, value in (("per_selection", False), ("average_over", 1), ("retain_instantaneous_values", True), ("create_report_file", False), ("create_report_plot", False)):
            set_optional(report, key, value)
        state = safe_get_state(report, f"volume report {name}")
        require(state.get("report_type") == report_type and state.get("cell_zones") == zones, f"volume report mismatch: {name}: {state}")
        names.append(name)

    all_zones = [PARENT_ZONE, LOWER_ZONE]
    add_volume("v2-total-liquid-mass", "volume-mass", None, all_zones, "phase-2")
    add_volume("v2-total-liquid-volume", "volume-integral", "phase-2-vof", all_zones)
    add_volume("v2-lower-liquid-mass", "volume-mass", None, [LOWER_ZONE], "phase-2")
    add_volume("v2-lower-liquid-volume", "volume-integral", "phase-2-vof", [LOWER_ZONE])
    add_volume("v2-applied-absorber", "volume-sum", "phase-2-user-mass-source", [LOWER_ZONE])

    expression_map = {
        "v2-command": "P71V2Command",
        "v2-absorber-removal": "P71V2Removal",
        "v2-lower-available-volume": "P71V2AvailableVolume",
        "v2-command-error": "P71V2CommandError",
        "v2-solver-iteration": "P71V2Iteration",
    }
    for name, definition in expression_map.items():
        report = expressions[name] if name in set(str(item) for item in expressions.get_object_names()) else None
        if report is None:
            expressions.create(name=name)
            report = expressions[name]
        report.definition = definition
        require(report.definition() == definition, f"expression report mismatch: {name}")
        names.append(name)
    return names


def configure_report_files(solver: Any, monitor_root: str, case: str, definitions: list[str]) -> dict[str, str]:
    ensure_remote_directory(solver, monitor_root)
    files = solver.settings.solution.monitor.report_files
    existing = list(files.get_object_names())
    if existing:
        files.delete(name_list=existing)
    paths: dict[str, str] = {}
    for definition in definitions:
        file_name = f"{definition}-rfile"
        files.create(name=file_name)
        path = str(PureWindowsPath(monitor_root) / f"{case}-{definition}.out")
        require(not remote_file_exists(solver, path), f"refusing to overwrite report file: {path}")
        files[file_name].set_state({"file_name": path, "report_defs": [definition], "frequency": 1, "active": True})
        state = safe_get_state(files[file_name], f"report file {file_name}")
        require(PureWindowsPath(str(state.get("file_name"))).name == PureWindowsPath(path).name, f"report file path mismatch: {state}")
        paths[definition] = path
    return paths


def save_pair(solver: Any, case: str) -> None:
    dat = data_path(case)
    require(not remote_file_exists(solver, case) and not remote_file_exists(solver, dat), f"refusing to overwrite checkpoint: {case}")
    solver.settings.file.write_case(file_name=case)
    solver.settings.file.write_data(file_name=dat)
    require(remote_file_exists(solver, case) and remote_file_exists(solver, dat), f"checkpoint pair missing: {case}")


def paths(checkpoint_root: str, final_root: str, case: str, stamp: str) -> dict[str, str]:
    local = PureWindowsPath(checkpoint_root) / case / stamp
    final = PureWindowsPath(final_root) / case / stamp
    result = {
        "prepared": str(local / f"{case}-prepared.cas.h5"),
        "active000": str(local / f"{case}-active000.cas.h5"),
        "monitor_root": str(local / "monitors"),
        "scratch": str(local / "scratch"),
        "final_root": str(final),
    }
    for active in CHECKPOINTS[:-1]:
        result[f"active{active}"] = str(local / f"{case}-active{active}.cas.h5")
    result["active2000"] = str(final / f"{case}-active2000.cas.h5")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-case", required=True)
    parser.add_argument("--parent-data", required=True)
    parser.add_argument("--checkpoint-root", required=True)
    parser.add_argument("--final-root", required=True)
    parser.add_argument("--local-dir", type=Path, required=True)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--case", default="P71A-V2-INLET-LOADING-RAMP")
    parser.add_argument("--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--coupled-pseudo-time", action="store_true", help="Use Coupled pressure-velocity with steady Global Time Step pseudo-time.")
    args = parser.parse_args()
    local = args.local_dir.resolve()
    local.mkdir(parents=True, exist_ok=False)
    manifest_path = local / "run-manifest.json"
    run_paths = paths(args.checkpoint_root, args.final_root, args.case, args.stamp)
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": COUPLED_PSEUDO_SETUP_ID if args.coupled_pseudo_time else SETUP_ID,
        "case_id": args.case,
        "server_id": args.server_id,
        "parent_case": args.parent_case,
        "parent_data": args.parent_data,
        "requested_active_iterations": HORIZON,
        "inlet_start_multiplier": START_MULTIPLIER,
        "ramp_active_iterations": RAMP_ITERATIONS,
        "liquid_base_target_kg_s": LIQUID_BASE_KG_S,
        "steam_base_target_kg_s": VAPOR_BASE_KG_S,
        "absorber_law": "P71V2Sink follows P71V2Command from instantaneous liquid-inlet throughput; no source retuning",
        "controlled_delta": "SIMPLE -> Coupled; steady Global Time Step pseudo-time enabled with Automatic timestep" if args.coupled_pseudo_time else "v2 baseline settings",
        "artifacts": run_paths,
        "events": [],
    }
    dump(manifest_path, manifest)
    capture = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True, tcp_timeout_seconds=120)
        require("2025 R2" in str(solver.get_fluent_version()), f"unexpected Fluent version: {solver.get_fluent_version()}")
        for directory in (str(PureWindowsPath(args.checkpoint_root) / args.case / args.stamp), run_paths["monitor_root"], run_paths["scratch"], run_paths["final_root"]):
            ensure_remote_directory(solver, directory)
        require(remote_file_exists(solver, args.parent_case) and remote_file_exists(solver, args.parent_data), "v2 prepared parent pair is not visible on student")
        solver.settings.file.read_case(file_name=args.parent_case)
        solver.settings.file.read_data(file_name=args.parent_data)
        if args.coupled_pseudo_time:
            manifest["solver_variant_readback"] = configure_coupled_global_pseudo_time(solver)
        manifest["parent_readback"] = audit(solver, 0)
        definitions = configure_definitions(solver)
        manifest["report_definitions"] = definitions
        report_paths = configure_report_files(solver, run_paths["monitor_root"], args.case, definitions)
        manifest["report_paths"] = report_paths
        manifest["residual_configuration"] = configure_residual_history(solver, HORIZON + 100)
        solver.settings.solution.run_calculation.profile_update_interval = 1
        manifest["initial_inlet_schedule"] = schedule_inlets(solver, 0)
        manifest["initial_readback"] = audit(solver, 0)
        save_pair(solver, run_paths["prepared"])
        solver.settings.file.read_case(file_name=run_paths["prepared"])
        solver.settings.file.read_data(file_name=data_path(run_paths["prepared"]))
        if args.coupled_pseudo_time:
            manifest["prepared_reopen_solver_variant_readback"] = configure_coupled_global_pseudo_time(solver)
        manifest["prepared_reopen_parent_state"] = audit(solver, 0)
        # Fluent case/data reopen restores the parent boundary values. Reapply
        # the declared child schedule after reopen, then audit it before the
        # active-000 pair is saved; otherwise the first control block would
        # silently run at the parent's base inlet loading.
        manifest["prepared_reopen_schedule"] = schedule_inlets(solver, 0)
        manifest["prepared_reopen"] = audit(solver, 0)
        save_pair(solver, run_paths["active000"])
        capture = SessionTranscriptCapture(solver, stream_path=local / "transcript.txt", echo=False)
        capture.start()
        marker = capture.mark()
        active = 0
        while active < HORIZON:
            block = min(UPDATE_INTERVAL, HORIZON - active)
            before = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=block)
            active += block
            console = capture.text_since(before)
            if re.search(r"floating point exception|divergence detected in AMG solver|fatal error|segmentation violation", console, re.I):
                manifest.update({"status": "BLOCKED", "last_valid_active_iteration": active - block, "failure_console_tail": console[-16000:]})
                dump(manifest_path, manifest)
                raise RuntimeError(f"solver failure during block ending at {active}")
            schedule = schedule_inlets(solver, active)
            event = {
                "event": "inlet_loading_update",
                **schedule,
                "command_kg_s": expression_value(solver, "P71V2Command"),
                "absorber_named_removal_kg_s": expression_value(solver, "P71V2Removal"),
                "applied_absorber_source_kg_s": applied_absorber(solver),
                "lower_liquid_volume_m3": expression_value(solver, "P71V2AvailableVolume"),
                "total_liquid_mass_kg": compute_report(solver, "v2-total-liquid-mass"),
                "total_liquid_volume_m3": compute_report(solver, "v2-total-liquid-volume"),
                "lower_liquid_mass_kg": compute_report(solver, "v2-lower-liquid-mass"),
                "warnings": {"console_tail": console[-3000:]},
            }
            manifest["events"].append(event)
            if active in CHECKPOINTS:
                key = "active2000" if active == 2000 else f"active{active}"
                save_pair(solver, run_paths[key])
                event["checkpoint_case"] = run_paths[key]
            if active % 100 == 0:
                dump(manifest_path, manifest)

        residuals = parse_residuals(capture.text_since(marker))
        require(residuals["point_count"] >= HORIZON, f"residual history too short: {residuals['point_count']}")
        dump(local / "residuals.json", residuals)
        histories: dict[str, Any] = {}
        for definition, path in report_paths.items():
            require(remote_file_exists(solver, path), f"missing report file: {path}")
            history = parse_report_forms(read_remote_forms(solver, path))
            require(history["points"] >= HORIZON, f"report history too short for {definition}: {history['points']}")
            history["definition_name"] = definition
            history["remote_file"] = path
            histories[definition] = history
        dump(local / "report-histories.json", histories)
        solver.settings.file.read_case(file_name=run_paths["active2000"])
        solver.settings.file.read_data(file_name=data_path(run_paths["active2000"]))
        manifest["terminal_readback"] = audit(solver, HORIZON)
        manifest["final_sha256"] = {
            "case": remote_file_sha256(solver, run_paths["active2000"], str(PureWindowsPath(run_paths["scratch"]) / "active2000-case.sha256.txt")),
            "data": remote_file_sha256(solver, data_path(run_paths["active2000"]), str(PureWindowsPath(run_paths["scratch"]) / "active2000-data.sha256.txt")),
        }
        manifest.update({"achieved_active_iterations": active, "residuals": residuals, "report_histories": str(local / "report-histories.json"), "status": "COMPLETE"})
        dump(manifest_path, manifest)
        return 0
    except Exception as exc:
        manifest.update({"status": "BLOCKED", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
        dump(manifest_path, manifest)
        return 1
    finally:
        if capture is not None:
            capture.close()


if __name__ == "__main__":
    raise SystemExit(main())
