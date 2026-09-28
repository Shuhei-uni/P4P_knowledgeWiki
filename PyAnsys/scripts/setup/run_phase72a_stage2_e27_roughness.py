#!/usr/bin/env python3
"""Run one Phase 7.2A Stage 2 E2.7 plus roughness child on Server 3."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import re
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "inspection"), str(ROOT / "scripts" / "setup")]

from extract_report_plot_histories import parse_report_forms, read_remote_forms
from pyansys_fluent.common import remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history, ensure_remote_directory, remote_file_sha256
from run_phase72a_e27_server1_continuation import native_iteration, validate_e27, pair_save
from run_phase72a_family_r_native import apply_roughness


CASES = {"R3": 5e-4, "R4": 1e-3, "R5": 2e-3}
HORIZON = 3000
START = 13586
SOURCE = PureWindowsPath(r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\FamilyE\E2.7-continuation-5000\20260923T102912Z")
SOURCE_CASE = SOURCE / "P72A-E2.7-CONT5000-final-N13586.cas.h5"
SOURCE_DATA = SOURCE / "P72A-E2.7-CONT5000-final-N13586.dat.h5"
SOURCE_HASHES = {"case": "bc9eeac09adfeca77ebe467c03e6425f3f9bb7069aa5b1eaa9a839ee44f92990", "data": "57e8b1a97f9d9db8665eb0ab1a211c08065e1a0befc4570a90b89ab18fe61af5"}
WORK_BASE = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage2")
DURABLE_BASE = PureWindowsPath(r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\Stage2")
COVERAGE = "p72a-stage2-ewf-wetted-area"
REQUIRED = {"v2-flux-phase2-steamoutlet", "v2-total-liquid-mass", "p72a-e2.7-ewf-film-mass-total", "p72a-e2.7-ewf-thickness-max", "p72a-e2.7-ewf-velocity-mag-awavg"}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def configure_coverage(solver):
    surface = solver.settings.solution.report_definitions.surface
    if COVERAGE not in surface.get_object_names():
        surface.create(name=COVERAGE)
    report = surface[COVERAGE]
    report.report_type = "surface-integral"
    report.field = "film-coverage"
    report.surface_names = ["wall"]
    report.phase = "mixture"
    report.per_selection = False
    report.average_over = 1
    report.create_report_file = False
    report.create_report_plot = False
    state = report.get_state()
    require(state["report_type"] == "surface-integral" and state["field"] == "film-coverage" and state["surface_names"] == ["wall"], f"wetted area readback: {state}")
    value = solver.settings.solution.report_definitions.compute(report_defs=[COVERAGE])
    return {"state": state, "computed_parent": value}


def redirect_reports(solver, monitor_root, prefix):
    files = solver.settings.solution.monitor.report_files
    names = list(files.get_object_names())
    require(len(names) == 26, f"expected 26 parent report files, got {len(names)}")
    paths = {}
    for name in names:
        obj = files[name]
        state = safe_get_state(obj, name)
        defs = state.get("report_defs") or []
        require(len(defs) == 1, f"report mapping not one-to-one: {name}: {defs}")
        definition = str(defs[0])
        path = str(monitor_root / f"{prefix}-{definition}.out")
        require(not remote_file_exists(solver, path), f"report output already exists: {path}")
        obj.set_state({**state, "file_name": path, "frequency_of": "iteration", "frequency": 1, "active": True})
        new = safe_get_state(obj, name)
        require(PureWindowsPath(str(new["file_name"])) == PureWindowsPath(path) and new["active"] and int(new["frequency"]) == 1, f"report readback failed: {name}: {new}")
        paths[definition] = path
    require(REQUIRED.issubset(paths), f"missing native reports: {REQUIRED - set(paths)}")
    coverage_file = files
    coverage_name = COVERAGE + "-rfile"
    require(coverage_name not in coverage_file.get_object_names(), "unexpected existing coverage report file")
    coverage_file.create(name=coverage_name)
    coverage_path = str(monitor_root / f"{prefix}-{COVERAGE}.out")
    coverage_file[coverage_name].set_state({"file_name": coverage_path, "report_defs": [COVERAGE], "frequency_of": "iteration", "frequency": 1, "active": True})
    check = safe_get_state(coverage_file[coverage_name], coverage_name)
    require(check["report_defs"] == [COVERAGE] and check["active"] and int(check["frequency"]) == 1, f"coverage file readback failed: {check}")
    paths[COVERAGE] = coverage_path
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--stamp", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_root.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest_path = out / "run-manifest.json"
    case = args.case
    prefix = f"P72A-STAGE2-E27-{case}"
    work = WORK_BASE / case / args.stamp
    durable = DURABLE_BASE / case / args.stamp
    monitor = work / "monitors"
    scratch = work / "scratch"
    manifest = {"status": "PREFLIGHT", "case": case, "server_id": "3", "parent_case": str(SOURCE_CASE), "parent_data": str(SOURCE_DATA), "parent_hashes_expected": SOURCE_HASHES, "controlled_delta": {"roughness_height_m": CASES[case], "roughness_constant": 0.5}, "requested_iterations": HORIZON, "expected_terminal_iteration": START + HORIZON, "work_root": str(work), "durable_root": str(durable), "solve_command": f"/solve/iterate {HORIZON}"}
    dump(manifest_path, manifest)
    try:
        solver = connect("3", start_transcript=True, tcp_timeout_seconds=5)
        require("2025 R2" in str(solver.get_fluent_version()), "unexpected Fluent version")
        for path in (work, durable, monitor, scratch):
            ensure_remote_directory(solver, str(path))
        hashes = {"case": remote_file_sha256(solver, str(SOURCE_CASE), str(scratch / "parent-case.sha256.txt")), "data": remote_file_sha256(solver, str(SOURCE_DATA), str(scratch / "parent-data.sha256.txt"))}
        require(hashes == SOURCE_HASHES, f"parent hash mismatch: {hashes}")
        manifest["parent_hashes_observed"] = hashes
        solver.settings.file.read_case(file_name=str(SOURCE_CASE))
        solver.settings.file.read_data(file_name=str(SOURCE_DATA))
        require(native_iteration(solver) == START, "parent native iteration mismatch")
        manifest["parent_e27_readback"] = validate_e27(solver)
        manifest["parent_coverage"] = configure_coverage(solver)
        manifest["roughness_readback"] = apply_roughness(solver, case, CASES[case], 0.5)
        manifest["post_delta_e27_readback"] = validate_e27(solver)
        paths = redirect_reports(solver, monitor, prefix)
        manifest["report_paths"] = paths
        manifest["residual_configuration"] = configure_residual_history(solver, HORIZON + 1)
        manifest["autosave_configuration"] = configure_autosave(solver, str(work), data_frequency=250)
        manifest["start_pair_local"] = pair_save(solver, work / f"{prefix}-start-N{START}.cas.h5", scratch, scratch_tag="local-start")
        manifest["start_pair_durable"] = pair_save(solver, durable / f"{prefix}-start-N{START}.cas.h5", scratch, scratch_tag="durable-start")
        solver.settings.file.read_case(file_name=manifest["start_pair_local"]["case"])
        solver.settings.file.read_data(file_name=manifest["start_pair_local"]["data"])
        reopened_iteration = native_iteration(solver)
        manifest["prepared_pair_reopen_iteration"] = reopened_iteration
        if reopened_iteration == START - 1:
            # Fluent can expose the just-saved data one native coordinate below
            # the verified source data. Reapply that exact parent data to the
            # prepared roughness case, retaining the case-side wall delta.
            solver.settings.file.read_data(file_name=str(SOURCE_DATA))
            manifest["reopen_data_clock_recovery"] = "reloaded_hash_verified_parent_data_after_prepared_case_reopen"
        require(native_iteration(solver) == START, "prepared case plus verified parent data iteration mismatch")
        manifest["reopen_e27_readback"] = validate_e27(solver)
        manifest["reopen_roughness_readback"] = apply_roughness(solver, case, CASES[case], 0.5)
        coverage_state = solver.settings.solution.report_definitions.surface[COVERAGE].get_state()
        require(coverage_state["field"] == "film-coverage" and coverage_state["report_type"] == "surface-integral" and coverage_state["surface_names"] == ["wall"], "coverage report not preserved on reopen")
        for name in solver.settings.solution.monitor.report_files.get_object_names():
            state = safe_get_state(solver.settings.solution.monitor.report_files[name], name)
            require(state["active"] and int(state["frequency"]) == 1, f"report inactive after reopen: {name}")
        manifest["status"] = "PREPARED_REOPEN_VERIFIED"
        dump(manifest_path, manifest)

        capture = SessionTranscriptCapture(solver, stream_path=out / "transcript-stream.txt", echo=False)
        capture.start()
        marker = capture.mark()
        manifest["status"] = "RUNNING_FLUENT_NATIVE_TUI"
        manifest["solve_started_utc"] = datetime.now(timezone.utc).isoformat()
        dump(manifest_path, manifest)
        solver.execute_tui(f"/solve/iterate {HORIZON}\n")
        capture.wait_until_quiet(quiet_seconds=2.0, timeout_seconds=30.0)
        transcript = capture.text_since(marker)
        capture.close()
        (out / "transcript-native-solve.txt").write_text(transcript, encoding="utf-8")
        terminal = native_iteration(solver)
        manifest["terminal_native_iteration"] = terminal
        manifest["native_solve_event_flags"] = {"fpe": bool(re.search(r"floating.point exception|\\bFPE\\b", transcript, re.I)), "amg": bool(re.search(r"AMG solver.*(?:diverg|failed|failure)", transcript, re.I)), "nonfinite": bool(re.search(r"nan|infinity|nonfinite", transcript, re.I)), "fatal": bool(re.search(r"fatal error|aborted|unrecoverable", transcript, re.I))}
        if terminal != START + HORIZON:
            manifest["recovery_pair"] = pair_save(solver, work / f"{prefix}-stop-N{terminal}.cas.h5", scratch, scratch_tag="recovery")
            raise RuntimeError(f"solve stopped at native {terminal}, expected {START + HORIZON}")
        manifest["final_pair_local"] = pair_save(solver, work / f"{prefix}-final-N{terminal}.cas.h5", scratch, scratch_tag="local-final")
        manifest["final_pair_durable"] = pair_save(solver, durable / f"{prefix}-final-N{terminal}.cas.h5", scratch, scratch_tag="durable-final")
        histories = {}
        for name, path in paths.items():
            require(remote_file_exists(solver, path), f"missing native report file: {path}")
            record = parse_report_forms(read_remote_forms(solver, path))
            record.update({"definition_name": name, "remote_file": path})
            histories[name] = record
        dump(out / "report-histories.json", histories)
        manifest["report_history_points"] = {name: int(value.get("points", 0)) for name, value in histories.items()}
        require(all(n >= HORIZON for n in manifest["report_history_points"].values()), "incomplete per-iteration report history")
        manifest["status"] = "COMPLETE"
        manifest["solve_finished_utc"] = datetime.now(timezone.utc).isoformat()
        dump(manifest_path, manifest)
        return 0
    except Exception as exc:
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        dump(manifest_path, manifest)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
