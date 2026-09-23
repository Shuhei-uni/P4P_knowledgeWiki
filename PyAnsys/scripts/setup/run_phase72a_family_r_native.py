#!/usr/bin/env python3
"""Execute the Phase 7.2A Family R queue with Fluent-owned native solves.

The setup/readback work is PyFluent, but each case solve is handed to Fluent
with exactly one literal ``/solve/iterate 3000`` TUI command.  No Python loop
controls solver progress.  Reports are file-backed at native frequency 1 and
Fluent-native autosave retains local paired checkpoints every 250 iterations.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
import math
from pathlib import Path, PureWindowsPath
import re
import statistics
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
from pyansys_fluent.ewf_audit import audit_ewf_dpm_settings  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    configure_autosave,
    configure_residual_history,
    data_path,
    ensure_remote_directory,
    remote_file_sha256,
)
from run_03a_q01_s4_01_50 import list_remote_directory, pair_autosave_names  # noqa: E402
from run_p71a_r0_control_continuation import (  # noqa: E402
    PARENT_CASE,
    PARENT_DATA,
    event_flags,
    native_clock,
    native_iteration,
    pair_save,
    readback,
    report_snapshot,
)
from run_p71a_v2_inlet_loading import (  # noqa: E402
    applied_absorber,
    audit as v2_audit,
    compute_report,
    configure_definitions,
    configure_report_files,
    expression_value,
)

# The historical continuation module imports the earlier prepared-control
# parent.  Family R must use the final 5586 handoff pair instead.
PARENT_CASE = r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000\20260922T162500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-full-loading-plus1000.cas.h5"
PARENT_DATA = r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000\20260922T162500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-full-loading-plus1000.dat.h5"


SERVER_ID = "1"
FAMILY_ID = "P72A-Family-R"
FAMILY_LABEL = "R-roughness-EWF-off"
SETUP_ID_PREFIX = "P72A-FAMILY-R"
HORIZON = 3000
CHECKPOINTS = (250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000)
PARENT_START = 5586
PARENT_HASHES = {
    "case": "4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc",
    "data": "b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72",
}
REMOTE_LOCAL_ROOT = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\FamilyR")
REMOTE_FINAL_ROOT = PureWindowsPath(r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\FamilyR")
OUTER_WALL_ZONES = (
    "separator-purnanto:1",
    "separator-purnanto:1:001",
    "wall",
    "wall:004",
)
CASES: tuple[tuple[str, float, float], ...] = (
    ("R0", 0.0, 0.5),
    ("R1", 5e-5, 0.5),
    ("R2", 2e-4, 0.5),
    ("R3", 5e-4, 0.5),
    ("R4", 1e-3, 0.5),
    ("R5", 2e-3, 0.5),
    ("R6", 4e-3, 0.5),
    ("R7", 8e-3, 0.5),
)


def controlled_delta_record(case_id: str, ks: float, cs: float) -> dict[str, Any]:
    return {"roughness_height_m": ks, "roughness_constant_Cs": cs, "EWF": "off"}


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")
    temp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def authoritative_native_iteration(solver: Any) -> int:
    """Read Fluent's persisted native Iteration expression, not stale RP state."""
    value = solver.settings.setup.named_expressions["P71V2Iteration"].get_value()
    value = float(value)
    require(math.isfinite(value), f"nonfinite native Iteration expression: {value!r}")
    return int(round(value))


def roughness_from_state(state: Mapping[str, Any], name: str) -> dict[str, Any]:
    turbulence = nested(state, "phase", "mixture", "turbulence") or {}
    return {
        "roughness_height": nested(turbulence, "roughness_height"),
        "roughness_const": nested(turbulence, "roughness_const"),
    }


def wall_state(solver: Any) -> dict[str, Any]:
    branch = solver.settings.setup.boundary_conditions.wall
    names = sorted(str(item) for item in branch.get_object_names())
    return {
        name: safe_get_state(branch[name], f"wall.{name}")
        for name in names
    }


def wall_readback(solver: Any) -> dict[str, Any]:
    state = wall_state(solver)
    return {
        "all_wall_names": sorted(state),
        "intended_outer_wall_zones": list(OUTER_WALL_ZONES),
        "settings": {
            name: roughness_from_state(state[name], name)
            for name in sorted(set(OUTER_WALL_ZONES) & set(state))
        },
        "full_wall_states": state,
    }


def configure_outer_wall_velocity_report(solver: Any) -> tuple[str, dict[str, Any]]:
    root = solver.settings.solution.report_definitions
    surface = root.surface
    name = "family-r-outer-wall-liquid-y-velocity"
    existing = {str(item) for item in surface.get_object_names()}
    if name in existing:
        surface.delete(name_list=[name])
    surface.create(name=name)
    report = surface[name]
    report.report_type = "surface-areaavg"
    report = surface[name]
    report.field = "phase-2-y-velocity"
    report.surface_names = list(OUTER_WALL_ZONES)
    report.per_surface = False
    report.average_over = 1
    report.phase = "mixture"
    report.create_report_file = False
    report.create_report_plot = False
    state = safe_get_state(report, name)
    require(state.get("report_type") == "surface-areaavg", f"outer-wall report type mismatch: {state}")
    require(state.get("field") == "phase-2-y-velocity", f"outer-wall report field mismatch: {state}")
    require(state.get("surface_names") == list(OUTER_WALL_ZONES), f"outer-wall scope mismatch: {state}")
    return name, state


def assert_ewf_off(audit: Mapping[str, Any]) -> None:
    mechanisms = audit.get("mechanisms", {})
    if mechanisms.get("ewf_enabled") is True:
        raise RuntimeError(f"EWF is enabled in Family R parent: {mechanisms}")
    active = audit.get("active_film_walls", [])
    require(not active, f"active Eulerian film walls found in Family R parent: {active}")


def validate_model_state(solver: Any, audit: Mapping[str, Any]) -> None:
    """Family-specific model gate; Family E wrappers replace this hook."""
    del solver
    assert_ewf_off(audit)


def strip_instrumentation(value: Any) -> Any:
    result = copy.deepcopy(value)
    if isinstance(result, dict):
        for key in ("native_clock", "report_definitions", "report_files", "residual"):
            result.pop(key, None)
        for key, child in list(result.items()):
            result[key] = strip_instrumentation(child)
    elif isinstance(result, list):
        result = [strip_instrumentation(child) for child in result]
    return result


def strip_intended_roughness(value: Any) -> Any:
    result = copy.deepcopy(value)
    boundaries = result.get("boundaries") if isinstance(result, dict) else None
    if isinstance(boundaries, dict):
        walls = boundaries.get("wall")
        if isinstance(walls, dict):
            for name in OUTER_WALL_ZONES:
                if name in walls:
                    turbulence = nested(walls[name], "phase", "mixture", "turbulence")
                    if isinstance(turbulence, dict):
                        turbulence.pop("roughness_height", None)
                        turbulence.pop("roughness_const", None)
    return result


def assert_only_roughness_changed(parent: Mapping[str, Any], changed: Mapping[str, Any]) -> None:
    before = strip_intended_roughness(strip_instrumentation(parent))
    after = strip_intended_roughness(strip_instrumentation(changed))
    require(before == after, "a setting outside the declared Family R roughness delta changed")


def apply_roughness(solver: Any, case_id: str, ks: float, cs: float) -> dict[str, Any]:
    before = wall_readback(solver)
    require(set(OUTER_WALL_ZONES).issubset(set(before["all_wall_names"])), f"intended wall scope not present: {before['all_wall_names']}")
    branch = solver.settings.setup.boundary_conditions.wall
    payload = {
        "phase": {
            "mixture": {
                "turbulence": {
                    "roughness_height": {"option": "value", "value": ks},
                    "roughness_const": {"option": "value", "value": cs},
                }
            }
        }
    }
    already_requested = all(
        abs(float(before["settings"][name]["roughness_height"].get("value")) - ks)
        <= max(1e-15, abs(ks) * 1e-9)
        and abs(float(before["settings"][name]["roughness_const"].get("value")) - cs)
        <= 1e-12
        for name in OUTER_WALL_ZONES
    )
    # Avoid writing an already-satisfied smooth-wall state.  Some Fluent wall
    # schemas expose roughness for readback but reject a redundant set_state.
    if not already_requested:
        for name in OUTER_WALL_ZONES:
            branch[name].set_state(payload)
    after = wall_readback(solver)
    for name in OUTER_WALL_ZONES:
        current = after["settings"][name]
        height = current["roughness_height"].get("value")
        const = current["roughness_const"].get("value")
        require(abs(float(height) - ks) <= max(1e-15, abs(ks) * 1e-9), f"{case_id} roughness height readback mismatch on {name}: {height}")
        require(abs(float(const) - cs) <= 1e-12, f"{case_id} roughness constant readback mismatch on {name}: {const}")
    return {"before": before, "after": after, "case": case_id, "k_s_m": ks, "C_s": cs}


def report_histories(solver: Any, paths: Mapping[str, str], local_path: Path) -> dict[str, Any]:
    histories: dict[str, Any] = {}
    for name, path in paths.items():
        require(remote_file_exists(solver, path), f"required report file missing: {path}")
        record = parse_report_forms(read_remote_forms(solver, path))
        record.update({"definition_name": name, "remote_file": path})
        histories[name] = record
    dump(local_path, histories)
    return histories


def finite_stats(values: Any) -> dict[str, Any]:
    try:
        finite = [float(v) for v in values if math.isfinite(float(v))]
    except Exception:
        finite = []
    if not finite:
        return {"count": 0, "final": None, "mean_last_100": None, "slope_last_100": None}
    tail = finite[-100:]
    slope = None
    if len(tail) >= 2:
        slope = (tail[-1] - tail[0]) / (len(tail) - 1)
    return {"count": len(finite), "final": finite[-1], "mean_last_100": statistics.fmean(tail), "slope_last_100_per_native_iteration": slope}


def closure_summary(histories: Mapping[str, Any]) -> dict[str, Any]:
    def vals(name: str) -> list[float]:
        return [float(v) for v in (histories.get(name, {}).get("values") or []) if math.isfinite(float(v))]

    p2_in = vals("v2-flux-phase2-liquidinlet")
    p2_out = vals("v2-flux-phase2-steamoutlet")
    p1_in = vals("v2-flux-phase1-steaminlet")
    p1_out = vals("v2-flux-phase1-steamoutlet")
    mixture = vals("v2-flux-mixture-steamoutlet")
    sink = vals("v2-applied-absorber")
    count = min(len(p2_in), len(p2_out), len(sink))
    p2 = [p2_in[i] + p2_out[i] + sink[i] for i in range(count)]
    count1 = min(len(p1_in), len(p1_out))
    p1 = [p1_in[i] + p1_out[i] for i in range(count1)]
    cm = min(len(mixture), len(p1), len(p2))
    mix = [mixture[i] + p1[i] + p2[i] for i in range(cm)]
    storage = vals("v2-total-liquid-mass")
    storage_delta = [(storage[i] - storage[i - 1]) for i in range(1, len(storage))]
    return {
        "sign_convention": "Fluent report values retained as written; inlet and outlet signs are not flipped.",
        "phase2_source_inclusive_closure_kg_s": finite_stats(p2),
        "phase1_source_inclusive_closure_kg_s": finite_stats(p1),
        "mixture_source_inclusive_closure_kg_s": finite_stats(mix),
        "liquid_storage_delta_kg_per_native_iteration": finite_stats(storage_delta),
        "phase2_primary_carryover": finite_stats(p2_out),
        "phase1_steam_outlet": finite_stats(p1_out),
        "mixture_steam_outlet": finite_stats(mixture),
    }


def parse_required_residuals(text: str) -> dict[str, Any]:
    rows: list[str] = []
    for line in text.splitlines():
        if re.search(r"\b(?:continuity|x-velocity|y-velocity|z-velocity|k|epsilon|vf-phase-2)\b", line, re.I):
            rows.append(line)
    return {"line_count": len(rows), "first_rows": rows[:10], "last_rows": rows[-20:]}


def checkpoint_pairs_from_transcript(text: str) -> list[dict[str, str]]:
    paths = re.findall(r'Writing to [^:]+:"([^"]+checkpoint-[^"]+\.(?:cas|dat)\.h5)"', text, re.I)
    cases = {path[:-7]: path for path in paths if path.casefold().endswith(".cas.h5")}
    data = {path[:-7]: path for path in paths if path.casefold().endswith(".dat.h5")}
    return [
        {"stem": stem, "case": cases[stem], "data": data[stem]}
        for stem in sorted(set(cases) & set(data))
    ]


def one_case(solver: Any, case_id: str, ks: float, cs: float, stamp: str, local_root: Path) -> dict[str, Any]:
    case_local = local_root / case_id
    case_local.mkdir(parents=True, exist_ok=False)
    manifest_path = case_local / "run-manifest.json"
    remote_work = REMOTE_LOCAL_ROOT / case_id / stamp
    remote_final = REMOTE_FINAL_ROOT / case_id / stamp
    monitor_root = remote_work / "monitors"
    scratch_root = remote_work / "scratch"
    prepared_case = remote_work / f"P72A-{case_id}-prepared.cas.h5"
    parent_copy_case = remote_work / f"P72A-{case_id}-parent-copy.cas.h5"
    local_final_case = remote_work / f"P72A-{case_id}-full-loading-plus{HORIZON:04d}.cas.h5"
    durable_final_case = remote_final / f"P72A-{case_id}-full-loading-plus{HORIZON:04d}.cas.h5"
    manifest: dict[str, Any] = {
        "status": "PREFLIGHT",
        "setup_id": f"{SETUP_ID_PREFIX}-{case_id}",
        "family": FAMILY_LABEL,
        "case_id": case_id,
        "server_id": SERVER_ID,
        "fluent_version_expected": "Ansys Fluent 2025 R2",
        "parent_case": PARENT_CASE,
        "parent_data": PARENT_DATA,
        "expected_parent_sha256": PARENT_HASHES,
        "controlled_delta": controlled_delta_record(case_id, ks, cs),
        "frozen_invariants": "mesh, zones, materials, inlets, absorber, bottom walls, pressure outlet, steady Coupled/Global-Time-Step scaffold",
        "requested_additional_iterations": HORIZON,
        "parent_native_coordinate_expected": PARENT_START,
        "checkpoint_offsets": [0, *CHECKPOINTS],
        "remote_paths": {
            "work_root": str(remote_work),
            "monitor_root": str(monitor_root),
            "scratch_root": str(scratch_root),
            "parent_copy_case": str(parent_copy_case),
            "prepared_case": str(prepared_case),
            "prepared_data": str(data_path(str(prepared_case))),
            "local_final_case": str(local_final_case),
            "local_final_data": str(data_path(str(local_final_case))),
            "durable_final_case": str(durable_final_case),
            "durable_final_data": str(data_path(str(durable_final_case))),
        },
        "sign_convention": {"vertical_velocity_y": "+y is upward; -y is downward", "flux": "Fluent report signs retained as written"},
        "events": [],
    }
    dump(manifest_path, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        for directory in (remote_work, monitor_root, scratch_root, remote_final):
            ensure_remote_directory(solver, str(directory))
        for path in (parent_copy_case, prepared_case, local_final_case, durable_final_case):
            require(not remote_file_exists(solver, str(path)), f"refusing to overwrite child artifact: {path}")
            require(not remote_file_exists(solver, data_path(str(path))), f"refusing to overwrite child data: {data_path(str(path))}")
        require(remote_file_exists(solver, PARENT_CASE) and remote_file_exists(solver, PARENT_DATA), "authoritative parent pair not visible on Server 1")
        manifest["parent_sha256"] = {
            "case": remote_file_sha256(solver, PARENT_CASE, str(scratch_root / "parent-case.sha256.txt")),
            "data": remote_file_sha256(solver, PARENT_DATA, str(scratch_root / "parent-data.sha256.txt")),
        }
        require(manifest["parent_sha256"] == PARENT_HASHES, f"authoritative parent hash mismatch: {manifest['parent_sha256']}")
        solver.settings.file.read_case(file_name=PARENT_CASE)
        solver.settings.file.read_data(file_name=PARENT_DATA)
        parent = readback(solver)
        start = authoritative_native_iteration(solver)
        manifest["verified_parent_native_clock"] = native_clock(solver)
        manifest["verified_starting_iteration"] = start
        require(start == PARENT_START, f"loaded native starting coordinate is {start}, expected {PARENT_START}")
        manifest["parent_readback"] = parent
        manifest["parent_v2_audit"] = v2_audit(solver, start)
        manifest["parent_ewf_audit"] = audit_ewf_dpm_settings(solver)
        validate_model_state(solver, manifest["parent_ewf_audit"])
        manifest["parent_wall_readback"] = wall_readback(solver)
        require(set(OUTER_WALL_ZONES).issubset(set(manifest["parent_wall_readback"]["all_wall_names"])), "verified outer-wall scope is not present in loaded parent")
        manifest["parent_copy"] = pair_save(solver, str(parent_copy_case))
        manifest["parent_copy"]["native_iteration_authoritative"] = authoritative_native_iteration(solver)
        require(manifest["parent_copy"]["native_iteration_authoritative"] == start, "independent parent copy coordinate mismatch")

        delta = apply_roughness(solver, case_id, ks, cs)
        changed = readback(solver)
        assert_only_roughness_changed(parent, changed)
        manifest["roughness_delta_readback"] = delta
        manifest["child_readback_before_instrumentation"] = changed
        manifest["child_v2_audit"] = v2_audit(solver, start)
        manifest["child_ewf_audit"] = audit_ewf_dpm_settings(solver)
        validate_model_state(solver, manifest["child_ewf_audit"])
        manifest["reports"] = configure_definitions(solver)
        wall_report_name, wall_report_state = configure_outer_wall_velocity_report(solver)
        definitions = list(manifest["reports"]) + [wall_report_name]
        report_paths = configure_report_files(solver, str(monitor_root), f"P72A-{case_id}", definitions)
        manifest["reports"].append({"name": wall_report_name, "state": wall_report_state})
        manifest["report_paths"] = report_paths
        manifest["residual_configuration"] = configure_residual_history(solver, HORIZON + 200)
        manifest["autosave_configuration"] = configure_autosave(solver, str(remote_work), data_frequency=250)
        autosave_state = dict(manifest["autosave_configuration"])
        autosave_state["max_files"] = 20
        solver.settings.file.auto_save.set_state(autosave_state)
        manifest["autosave_configuration"] = safe_get_state(solver.settings.file.auto_save, "autosave after retention update")
        require(manifest["autosave_configuration"].get("max_files") == 20, "native autosave retention readback mismatch")
        manifest["instrumentation_readback_before_save"] = {
            "report_definitions": safe_get_state(solver.settings.solution.report_definitions, "reports"),
            "report_files": safe_get_state(solver.settings.solution.monitor.report_files, "report files"),
            "residual": safe_get_state(solver.settings.solution.monitor.residual, "residual"),
            "autosave": safe_get_state(solver.settings.file.auto_save, "autosave"),
        }
        dump(manifest_path, manifest)

        manifest["prepared_pair"] = pair_save(solver, str(prepared_case))
        manifest["prepared_pair"]["native_iteration_authoritative"] = authoritative_native_iteration(solver)
        solver.settings.file.read_case(file_name=str(prepared_case))
        solver.settings.file.read_data(file_name=data_path(str(prepared_case)))
        reopened = readback(solver)
        require(authoritative_native_iteration(solver) == start, "prepared reopen changed native starting coordinate")
        assert_only_roughness_changed(parent, reopened)
        manifest["prepared_reopen_readback"] = reopened
        manifest["prepared_reopen_wall_readback"] = wall_readback(solver)
        manifest["prepared_reopen_report_files"] = safe_get_state(solver.settings.solution.monitor.report_files, "report files")
        manifest["prepared_reopen_ewf_audit"] = audit_ewf_dpm_settings(solver)
        validate_model_state(solver, manifest["prepared_reopen_ewf_audit"])
        manifest["prepared_reopen_gate"] = "PASS"
        dump(manifest_path, manifest)

        capture = SessionTranscriptCapture(solver, stream_path=case_local / "transcript.txt", echo=False)
        capture.start()
        marker = capture.mark()
        manifest["status"] = "RUNNING_FLUENT_NATIVE_SOLVE"
        manifest["solve_command"] = "/solve/iterate 3000"
        dump(manifest_path, manifest)
        # This is the sole solve-control call for the case. Fluent owns the
        # entire horizon; Python does not issue blocks or per-iteration polls.
        solver.execute_tui(f"/solve/iterate {HORIZON}\n")
        capture.wait_until_quiet(quiet_seconds=2.0, timeout_seconds=30.0)
        transcript = capture.text_since(marker)
        (case_local / "transcript-native-solve.txt").write_text(transcript, encoding="utf-8")
        flags = event_flags(transcript)
        manifest["native_solve_returned"] = True
        manifest["native_solve_event_flags"] = flags
        manifest["terminal_native_clock_before_save"] = native_clock(solver)
        manifest["terminal_native_iteration_before_save"] = authoritative_native_iteration(solver)
        manifest["residual_transcript_summary"] = parse_required_residuals(transcript)
        require(authoritative_native_iteration(solver) == start + HORIZON, f"native solve ended at {authoritative_native_iteration(solver)}, expected {start + HORIZON}")
        if flags["amg"] or flags["fpe"] or flags["nonfinite"] or flags["fatal"]:
            manifest["first_event_preserved"] = transcript[:20000]
            manifest["status"] = "BLOCKED"
            dump(manifest_path, manifest)
            raise RuntimeError(f"fatal/nonfinite solver event during {case_id}: {flags}")

        directory_listing = list_remote_directory(
            solver,
            str(remote_work),
            str(scratch_root / "postsolve-directory-listing.txt"),
        )
        listed_pairs = pair_autosave_names(directory_listing["names"])
        transcript_pairs = checkpoint_pairs_from_transcript(transcript)
        manifest["checkpoint_autosave_inventory"] = listed_pairs or transcript_pairs
        manifest["checkpoint_autosave_inventory_source"] = "remote-directory-listing" if listed_pairs else "native-solve-transcript"
        require(len(manifest["checkpoint_autosave_inventory"]) >= 11, f"incomplete native autosave-pair evidence: {manifest['checkpoint_autosave_inventory']}")
        manifest["checkpoint_directory_listing"] = directory_listing
        manifest["local_final_pair"] = pair_save(solver, str(local_final_case))
        manifest["durable_final_pair"] = pair_save(solver, str(durable_final_case))
        manifest["local_final_pair"]["native_iteration_authoritative"] = authoritative_native_iteration(solver)
        manifest["durable_final_pair"]["native_iteration_authoritative"] = authoritative_native_iteration(solver)
        histories = report_histories(solver, report_paths, case_local / "report-histories.json")
        manifest["report_history_points"] = {name: record.get("points") for name, record in histories.items()}
        manifest["closure_summary"] = closure_summary(histories)
        manifest["terminal_monitor_snapshot"] = report_snapshot(solver, report_paths)
        manifest["terminal_readback_before_reopen"] = readback(solver)
        manifest["terminal_wall_readback_before_reopen"] = wall_readback(solver)
        manifest["terminal_ewf_audit_before_reopen"] = audit_ewf_dpm_settings(solver)
        validate_model_state(solver, manifest["terminal_ewf_audit_before_reopen"])
        solver.settings.file.read_case(file_name=str(durable_final_case))
        solver.settings.file.read_data(file_name=data_path(str(durable_final_case)))
        terminal_reopen = readback(solver)
        require(authoritative_native_iteration(solver) == start + HORIZON, "durable final reopen native coordinate mismatch")
        assert_only_roughness_changed(parent, terminal_reopen)
        manifest["terminal_readback_after_reopen"] = terminal_reopen
        manifest["terminal_wall_readback_after_reopen"] = wall_readback(solver)
        manifest["terminal_ewf_audit_after_reopen"] = audit_ewf_dpm_settings(solver)
        validate_model_state(solver, manifest["terminal_ewf_audit_after_reopen"])
        manifest["final_hashes"] = {
            "case": remote_file_sha256(solver, str(durable_final_case), str(scratch_root / "durable-final-case.sha256.txt")),
            "data": remote_file_sha256(solver, data_path(str(durable_final_case)), str(scratch_root / "durable-final-data.sha256.txt")),
        }
        manifest["achieved_additional_iterations"] = HORIZON
        manifest["status"] = "COMPLETE"
        dump(manifest_path, manifest)
        return manifest
    except Exception as exc:
        if capture is not None:
            try:
                capture.wait_until_quiet(quiet_seconds=1.0, timeout_seconds=5.0)
                (case_local / "transcript-failure-tail.txt").write_text(capture.text_since(0)[-50000:], encoding="utf-8")
            except Exception:
                pass
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        try:
            manifest["last_live_clock"] = native_clock(solver)
            manifest["last_live_iteration"] = native_iteration(solver)
            manifest["last_live_iteration_authoritative"] = authoritative_native_iteration(solver)
        except Exception:
            pass
        dump(manifest_path, manifest)
        raise
    finally:
        if capture is not None:
            capture.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-root", type=Path, required=True)
    parser.add_argument("--run-stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--case", choices=[item[0] for item in CASES], action="append", help="Repeat to run a subset in queue order.")
    args = parser.parse_args()
    local_root = args.local_root.expanduser().resolve()
    local_root.mkdir(parents=True, exist_ok=False)
    queue_manifest = local_root / "queue-manifest.json"
    selected = [item for item in CASES if not args.case or item[0] in set(args.case)]
    queue: dict[str, Any] = {
        "status": "RUNNING",
        "family": FAMILY_ID,
        "server_id": SERVER_ID,
        "run_stamp": args.run_stamp,
        "queue_order": [item[0] for item in selected],
        "requested_horizon_per_case": HORIZON,
        "parent_case": PARENT_CASE,
        "parent_data": PARENT_DATA,
        "parent_sha256": PARENT_HASHES,
        "cases": [],
    }
    dump(queue_manifest, queue)
    solver: Any | None = None
    try:
        solver = connect(server_id=SERVER_ID, start_transcript=True, tcp_timeout_seconds=10)
        version = str(solver.get_fluent_version())
        require("2025 R2" in version, f"unexpected Fluent version: {version}")
        queue["fluent_version"] = version
        dump(queue_manifest, queue)
        for case_id, ks, cs in selected:
            try:
                result = one_case(solver, case_id, ks, cs, args.run_stamp, local_root)
                queue["cases"].append({"case_id": case_id, "status": result.get("status"), "manifest": str(local_root / case_id / "run-manifest.json")})
                dump(queue_manifest, queue)
            except Exception as exc:
                queue["status"] = "BLOCKED"
                queue["blocked_case"] = case_id
                queue["error"] = f"{type(exc).__name__}: {exc}"
                dump(queue_manifest, queue)
                raise
        queue["status"] = "COMPLETE"
        dump(queue_manifest, queue)
        print(json.dumps(queue, indent=2, default=str))
        return 0
    except Exception:
        if queue.get("status") != "BLOCKED":
            queue["status"] = "BLOCKED"
            dump(queue_manifest, queue)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
