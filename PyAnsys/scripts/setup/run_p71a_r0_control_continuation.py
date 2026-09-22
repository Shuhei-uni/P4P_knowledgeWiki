#!/usr/bin/env python3
"""Run the Phase 7.1A R0 smooth-control Coupled/Global-Time-Step continuation.

This runner is intentionally specific to the user-supplied developed Family R
full-loading pair.  It verifies the parent on Server 1, preserves a paired
pre-mutation copy, changes only pressure-velocity coupling and pseudo-time
method, configures child-owned native histories, and advances exactly 1,000
additional native steady iterations from the verified starting iteration.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path, PureWindowsPath
import re
import sys
import time
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
from run_p71a_v2_inlet_loading import (  # noqa: E402
    applied_absorber,
    audit as v2_audit,
    compute_report,
    configure_definitions,
    configure_report_files,
    expression_value,
)
from run_p7_e0_ref_discovery import parse_residuals  # noqa: E402


PARENT_CASE = r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL\20260922T025211Z\P71A-R0-SMOOTH-CONTROL-full-loading-final.cas.h5"
PARENT_DATA = r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL\20260922T025211Z\P71A-R0-SMOOTH-CONTROL-full-loading-final.dat.h5"
EXPECTED_PARENT_HASHES = {
    "case": "331bc57550fa0eff67bdc89a0925aa52c8c6f79a4632188e234abdd8ece28c3c",
    "data": "1a8c31aac6a3a347629a94cc9814edb76b84b49ca1fdfcb1566004bef4517083",
}
SERVER_ID = "1"
HORIZON = 1000
BLOCK = 10
CHECKPOINTS = (250, 500, 750, 1000)
CASE_ID = "P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME"


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def as_float(value: Any) -> float:
    if isinstance(value, Mapping):
        if "Net" in value:
            value = value["Net"]
        elif "value" in value:
            value = value["value"]
        elif len(value) == 1:
            value = next(iter(value.values()))
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return as_float(value[0])
    return float(value)


def native_iteration(solver: Any) -> int:
    value = solver.scheme.eval("(%rpgetvar 'current-iteration)")
    return int(round(as_float(value)))


def native_clock(solver: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in ("current-iteration", "number-of-iterations", "flow-time", "time-step", "physical-time-step"):
        try:
            result[name] = solver.scheme.eval(f"(%rpgetvar '{name})")
        except Exception as exc:
            result[name] = f"{type(exc).__name__}: {exc}"
    return result


def pair_save(solver: Any, case_path: str, *, overwrite: bool = False) -> dict[str, Any]:
    data = data_path(case_path)
    if not overwrite:
        require(not remote_file_exists(solver, case_path), f"refusing to overwrite case: {case_path}")
        require(not remote_file_exists(solver, data), f"refusing to overwrite data: {data}")
    solver.settings.file.write_case(file_name=case_path)
    solver.settings.file.write_data(file_name=data)
    require(remote_file_exists(solver, case_path) and remote_file_exists(solver, data), f"paired save missing: {case_path}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    scratch = str(PureWindowsPath(case_path).parent / f"hash-{stamp}")
    ensure_remote_directory(solver, scratch)
    return {
        "case": case_path,
        "data": data,
        "case_sha256": remote_file_sha256(solver, case_path, str(PureWindowsPath(scratch) / "case.sha256.txt")),
        "data_sha256": remote_file_sha256(solver, data, str(PureWindowsPath(scratch) / "data.sha256.txt")),
        "native_iteration": native_iteration(solver),
    }


def readback(solver: Any) -> dict[str, Any]:
    methods = safe_get_state(solver.settings.solution.methods, "solution methods")
    return {
        "native_clock": native_clock(solver),
        "general": safe_get_state(solver.settings.setup.general, "general settings"),
        "models": safe_get_state(solver.settings.setup.models, "models"),
        "materials": safe_get_state(solver.settings.setup.materials, "materials"),
        "boundaries": safe_get_state(solver.settings.setup.boundary_conditions, "boundaries"),
        "cell_zones": safe_get_state(solver.settings.setup.cell_zone_conditions, "cell zones"),
        "methods": methods,
        "controls": safe_get_state(solver.settings.solution.controls, "solution controls"),
        "named_expressions": safe_get_state(solver.settings.setup.named_expressions, "named expressions"),
        "report_definitions": safe_get_state(solver.settings.solution.report_definitions, "report definitions"),
        "report_files": safe_get_state(solver.settings.solution.monitor.report_files, "report files"),
        "residual": safe_get_state(solver.settings.solution.monitor.residual, "residual monitor"),
        "fluid_zones": list(solver.settings.setup.cell_zone_conditions.fluid.get_object_names()),
        "solver_method_summary": {
            "flow_scheme": methods.get("p_v_coupling", {}).get("flow_scheme") if isinstance(methods, Mapping) else None,
            "pseudo_time_method": methods.get("pseudo_time_method") if isinstance(methods, Mapping) else None,
        },
    }


def set_control_delta(solver: Any) -> dict[str, Any]:
    before = readback(solver)
    require(before["general"].get("solver", {}).get("time") == "steady", "parent is not steady")
    solver.settings.solution.methods.p_v_coupling.flow_scheme.set_state("Coupled")
    solver.settings.solution.methods.pseudo_time_method.formulation.coupled_solver.set_state("global-time-step")
    after = readback(solver)
    require(after["general"].get("solver", {}).get("time") == "steady", "control delta changed physical solver time")
    require(after["solver_method_summary"]["flow_scheme"] == "Coupled", f"Coupled readback mismatch: {after['solver_method_summary']}")
    require(after["solver_method_summary"]["pseudo_time_method"].get("formulation", {}).get("coupled_solver") == "global-time-step", f"Global Time Step readback mismatch: {after['solver_method_summary']}")
    return {"before": before, "after": after}


def report_snapshot(solver: Any, report_paths: Mapping[str, str]) -> dict[str, Any]:
    histories: dict[str, Any] = {}
    for definition, path in report_paths.items():
        if remote_file_exists(solver, path):
            try:
                histories[definition] = parse_report_forms(read_remote_forms(solver, path))
            except Exception as exc:
                histories[definition] = {"parse_error": f"{type(exc).__name__}: {exc}", "remote_file": path}
        else:
            histories[definition] = {"missing": True, "remote_file": path}
    return histories


def event_flags(text: str) -> dict[str, Any]:
    patterns = {
        "amg": r"AMG|divergence detected in AMG",
        "fpe": r"floating point exception|FPE",
        "nonfinite": r"non.?finite|NaN|Inf",
        "fatal": r"fatal error|segmentation violation|node failure",
        "reverse_flow": r"reverse flow|reversed flow",
        "turbulent_viscosity": r"turbulent viscosity|viscosity limited|limiting",
    }
    return {name: bool(re.search(pattern, text, re.I)) for name, pattern in patterns.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-dir", type=Path, required=True)
    parser.add_argument("--run-stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    args = parser.parse_args()
    local = args.local_dir.resolve()
    local.mkdir(parents=True, exist_ok=False)
    manifest_path = local / "run-manifest.json"
    manifest: dict[str, Any] = {
        "status": "PREFLIGHT",
        "setup_id": "P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME",
        "server_id": SERVER_ID,
        "server_ref": "server-1@10.104.145.170",
        "fluent_version_expected": "Ansys Fluent 2025 R2",
        "parent_case": PARENT_CASE,
        "parent_data": PARENT_DATA,
        "expected_parent_sha256": EXPECTED_PARENT_HASHES,
        "requested_additional_iterations": HORIZON,
        "checkpoint_offsets": [0, *CHECKPOINTS],
        "controlled_delta": {
            "pressure_velocity_coupling": "verified parent -> Coupled",
            "pseudo_time_method": "verified parent -> Global Time Step",
        },
        "frozen_policy": "all physical/model/mesh/material/boundary/inlet/absorber/discretization/URF/report-independent settings unchanged",
        "remote_run_root": None,
        "events": [],
    }
    dump(manifest_path, manifest)
    solver: Any | None = None
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=SERVER_ID, start_transcript=True, tcp_timeout_seconds=10)
        version = str(solver.get_fluent_version())
        require("2025 R2" in version, f"unexpected Fluent version: {version}")
        stamp = args.run_stamp
        local_root = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase71A\FamilyR") / CASE_ID / stamp
        final_root = PureWindowsPath(r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals") / CASE_ID / stamp
        checkpoint_root = str(local_root)
        monitor_root = str(local_root / "monitors")
        scratch_root = str(local_root / "scratch")
        manifest["remote_run_root"] = str(local_root)
        manifest["remote_final_root"] = str(final_root)
        for directory in (checkpoint_root, monitor_root, scratch_root, str(final_root)):
            ensure_remote_directory(solver, directory)

        require(remote_file_exists(solver, PARENT_CASE), f"parent case not found: {PARENT_CASE}")
        require(remote_file_exists(solver, PARENT_DATA), f"parent data not found: {PARENT_DATA}")
        parent_hashes = {
            "case": remote_file_sha256(solver, PARENT_CASE, str(PureWindowsPath(scratch_root) / "parent-case.sha256.txt")),
            "data": remote_file_sha256(solver, PARENT_DATA, str(PureWindowsPath(scratch_root) / "parent-data.sha256.txt")),
        }
        manifest["parent_sha256"] = parent_hashes
        require(parent_hashes == EXPECTED_PARENT_HASHES, f"parent hash mismatch: {parent_hashes}")
        solver.settings.file.read_case(file_name=PARENT_CASE)
        solver.settings.file.read_data(file_name=PARENT_DATA)
        parent = readback(solver)
        start = native_iteration(solver)
        manifest["fluent_version"] = version
        manifest["verified_starting_iteration"] = start
        manifest["parent_readback"] = parent
        manifest["parent_v2_audit"] = v2_audit(solver, start)
        pre_case = str(local_root / f"{CASE_ID}-pre-mutation.cas.h5")
        manifest["pre_mutation_pair"] = pair_save(solver, pre_case)
        require(manifest["pre_mutation_pair"]["native_iteration"] == start, "pre-mutation copy iteration mismatch")
        dump(manifest_path, manifest)

        delta = set_control_delta(solver)
        manifest["control_delta_readback"] = delta
        # Child-owned report definitions/files.  The parent artifact is never
        # written; all report files resolve under the task-owned child root.
        definitions = configure_definitions(solver)
        report_paths = configure_report_files(solver, monitor_root, CASE_ID, definitions)
        manifest["report_definitions"] = definitions
        manifest["report_paths"] = report_paths
        manifest["residual_configuration"] = configure_residual_history(solver, HORIZON + 200)
        manifest["instrumentation_readback_before_save"] = {
            "reports": safe_get_state(solver.settings.solution.report_definitions, "reports"),
            "report_files": safe_get_state(solver.settings.solution.monitor.report_files, "report files"),
            "residual": safe_get_state(solver.settings.solution.monitor.residual, "residual"),
        }
        prepared_case = str(local_root / f"{CASE_ID}-prepared.cas.h5")
        manifest["prepared_pair"] = pair_save(solver, prepared_case)
        solver.settings.file.read_case(file_name=prepared_case)
        solver.settings.file.read_data(file_name=data_path(prepared_case))
        reopened = readback(solver)
        manifest["reopen_readback"] = reopened
        require(reopened["solver_method_summary"]["flow_scheme"] == "Coupled", "Coupled did not persist after reopen")
        require(reopened["solver_method_summary"]["pseudo_time_method"].get("formulation", {}).get("coupled_solver") == "global-time-step", "Global Time Step did not persist after reopen")
        require(reopened["general"].get("solver", {}).get("time") == "steady", "physical steady mode did not persist")
        require(reopened["fluid_zones"] == parent["fluid_zones"], "fluid topology changed across child save/reopen")
        manifest["smoke_gate"] = {"status": "READY", "native_iteration": native_iteration(solver), "report_snapshot": report_snapshot(solver, report_paths)}
        dump(manifest_path, manifest)

        # A one-block smoke proves native advancement and live file-backed
        # instrumentation before the long continuation.  It is included in
        # the requested +1,000 horizon and is not a separate extra solve.
        capture = SessionTranscriptCapture(solver, stream_path=local / "transcript.txt", echo=False)
        capture.start()
        marker = capture.mark()
        active = 0
        checkpoint_paths: dict[int, dict[str, Any]] = {0: manifest["prepared_pair"]}
        while active < HORIZON:
            block = min(BLOCK, HORIZON - active)
            before = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=block)
            active += block
            current_native = native_iteration(solver)
            console = capture.text_since(before)
            flags = event_flags(console)
            event = {
                "offset": active,
                "native_iteration": current_native,
                "console_event_flags": flags,
                "command_kg_s": expression_value(solver, "P71V2Command"),
                "named_removal_kg_s": expression_value(solver, "P71V2Removal"),
                "command_error_kg_s": expression_value(solver, "P71V2CommandError"),
                "applied_phase2_source_kg_s_signed": applied_absorber(solver),
                "available_liquid_volume_m3": expression_value(solver, "P71V2AvailableVolume"),
                "total_liquid_mass_kg": compute_report(solver, "v2-total-liquid-mass"),
                "total_liquid_volume_m3": compute_report(solver, "v2-total-liquid-volume"),
                "lower_liquid_mass_kg": compute_report(solver, "v2-lower-liquid-mass"),
                "lower_liquid_volume_m3": compute_report(solver, "v2-lower-liquid-volume"),
                "console_tail": console[-4000:],
            }
            manifest["events"].append(event)
            if flags["amg"] or flags["fpe"] or flags["nonfinite"] or flags["fatal"]:
                manifest["first_event"] = event
                manifest["last_valid_offset"] = active - block
                dump(manifest_path, manifest)
                raise RuntimeError(f"fatal/nonfinite solver event in block ending at {active}")
            if active in CHECKPOINTS:
                checkpoint_case = str(local_root / f"{CASE_ID}-plus{active:04d}.cas.h5")
                checkpoint_paths[active] = pair_save(solver, checkpoint_case)
                event["checkpoint_pair"] = checkpoint_paths[active]
                event["report_snapshot"] = report_snapshot(solver, report_paths)
                dump(local / f"checkpoint-plus{active:04d}-readback.json", {"event": event, "readback": readback(solver)})
                # Terminal artifacts are placed in the durable final root only
                # after their local checkpoint has been proved paired.
                if active == HORIZON:
                    final_case = str(final_root / f"{CASE_ID}-full-loading-plus{HORIZON:04d}.cas.h5")
                    final_pair = pair_save(solver, final_case)
                    event["final_pair"] = final_pair
            if active % 50 == 0:
                dump(manifest_path, manifest)

        transcript = capture.text_since(marker)
        residuals = parse_residuals(transcript)
        dump(local / "residuals.json", residuals)
        histories = report_snapshot(solver, report_paths)
        dump(local / "report-histories.json", histories)
        manifest["checkpoint_pairs"] = checkpoint_paths
        manifest["achieved_additional_iterations"] = active
        manifest["verified_terminal_iteration"] = native_iteration(solver)
        manifest["residual_history"] = {"points": residuals.get("point_count"), "path": str(local / "residuals.json")}
        manifest["report_history_path"] = str(local / "report-histories.json")
        manifest["terminal_readback_before_reopen"] = readback(solver)
        final_pair = manifest["events"][-1].get("final_pair")
        require(final_pair is not None, "terminal final pair not saved")
        solver.settings.file.read_case(file_name=final_pair["case"])
        solver.settings.file.read_data(file_name=final_pair["data"])
        manifest["terminal_readback_after_reopen"] = readback(solver)
        require(manifest["terminal_readback_after_reopen"]["solver_method_summary"]["flow_scheme"] == "Coupled", "terminal Coupled readback failed")
        require(manifest["terminal_readback_after_reopen"]["solver_method_summary"]["pseudo_time_method"].get("formulation", {}).get("coupled_solver") == "global-time-step", "terminal Global Time Step readback failed")
        manifest["status"] = "COMPLETE"
        manifest["claim_status"] = "finite_horizon_control_continuation_only"
        dump(manifest_path, manifest)
        print(json.dumps(manifest, indent=2, default=str, allow_nan=True))
        return 0
    except Exception as exc:
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        if solver is not None:
            try:
                manifest["last_live_clock"] = native_clock(solver)
            except Exception:
                pass
        dump(manifest_path, manifest)
        print(json.dumps(manifest, indent=2, default=str, allow_nan=True), file=sys.stderr)
        return 1
    finally:
        if capture is not None:
            capture.close()


if __name__ == "__main__":
    raise SystemExit(main())
