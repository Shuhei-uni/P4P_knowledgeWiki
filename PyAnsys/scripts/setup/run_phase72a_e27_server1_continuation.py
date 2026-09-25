#!/usr/bin/env python3
"""Continue the verified E2.7 endpoint on Server 1 with Fluent-owned TUI solve."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path, PureWindowsPath
import re
import sys
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "inspection"), str(ROOT / "scripts" / "setup")]

from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    configure_autosave,
    configure_residual_history,
    data_path,
    ensure_remote_directory,
    remote_file_sha256,
)


SERVER_ID = "1"
START_ITERATION = 8586
HORIZON = 5000
EXPECTED_CASE_SHA256 = "3a92f610c25bdba6167b6b5cc268824e9a41e6d0e52f817f07cfe57687b7b65b"
EXPECTED_DATA_SHA256 = "c256d246b2e58280f0fbeab5af83126b25c5f3b5b12cbb3076b42420d68a85e1"
SOURCE_CASE = PureWindowsPath(
    r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\FamilyE\E0\20260922T054558Z\P72A-E2.7-full-loading-plus3000.cas.h5"
)
SOURCE_DATA = data_path(str(SOURCE_CASE))
REMOTE_WORK_BASE = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\FamilyE")
REMOTE_FINAL_BASE = PureWindowsPath(
    r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\FamilyE"
)


def dump(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")
    temp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def alist_value(value: Any, target: str) -> Any:
    if isinstance(value, dict):
        if target in value:
            return value[target]
        for item in value.values():
            found = alist_value(item, target)
            if found is not None:
                return found
    if isinstance(value, (list, tuple)):
        for item in value:
            if isinstance(item, (list, tuple)) and len(item) >= 2 and str(item[0]) == target:
                return item[1]
            found = alist_value(item, target)
            if found is not None:
                return found
    return None


def native_iteration(solver: Any) -> int:
    value = float(solver.settings.setup.named_expressions["P71V2Iteration"].get_value())
    require(math.isfinite(value), f"nonfinite native iteration expression: {value!r}")
    return int(round(value))


def validate_e27(solver: Any) -> dict[str, Any]:
    params = solver.rp_vars().get("wall-film/model-parameters")
    expected = {
        "secondary-phase-mode": 1,
        "thickness-limit": 0.3,
        "ewf-adaptive?": False,
        "courant-number": 0.05,
        "timestep-max": 1e-5,
        "sub-iter-nums": 10,
        "film-coupled-solution?": True,
        "film-message?": True,
    }
    observed: dict[str, Any] = {}
    for key, target in expected.items():
        actual = alist_value(params, key)
        observed[key] = actual
        if isinstance(target, float):
            require(actual is not None and abs(float(actual) - target) <= max(1e-12, target * 1e-9), f"E2.7 {key} mismatch: {actual!r}")
        else:
            require(actual == target, f"E2.7 {key} mismatch: {actual!r}")
    wall = solver.settings.setup.boundary_conditions.wall["wall"].phase["mixture"].wall_film.get_state()
    bottom = solver.settings.setup.boundary_conditions.wall["bottom"].phase["mixture"].wall_film.get_state()
    require(wall.get("eulerian_film_wall") is True, "E2.7 wall is not an Eulerian film wall")
    require(wall.get("enable_flow_momentum_coupling") is False, "E2.7 flow momentum coupling is not OFF")
    require(bottom.get("eulerian_film_wall") is not True, "bottom unexpectedly became a film wall")
    return {"model_parameters": observed, "wall": wall, "bottom": bottom}


def pair_save(
    solver: Any,
    case_path: PureWindowsPath,
    scratch_root: PureWindowsPath,
    *,
    scratch_tag: str,
) -> dict[str, Any]:
    data = data_path(str(case_path))
    require(not remote_file_exists(solver, str(case_path)), f"refusing to overwrite case: {case_path}")
    require(not remote_file_exists(solver, data), f"refusing to overwrite data: {data}")
    solver.settings.file.write_case(file_name=str(case_path))
    solver.settings.file.write_data(file_name=data)
    require(remote_file_exists(solver, str(case_path)), f"case save missing: {case_path}")
    require(remote_file_exists(solver, data), f"data save missing: {data}")
    return {
        "case": str(case_path),
        "data": data,
        "native_iteration": native_iteration(solver),
        "case_sha256": remote_file_sha256(solver, str(case_path), str(scratch_root / f"{scratch_tag}-{case_path.stem}.sha256.txt")),
        "data_sha256": remote_file_sha256(solver, data, str(scratch_root / f"{scratch_tag}-{PureWindowsPath(data).stem}.sha256.txt")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stamp", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    local_root = args.output_root.expanduser().resolve()
    local_root.mkdir(parents=True, exist_ok=False)
    manifest_path = local_root / "run-manifest.json"
    work = REMOTE_WORK_BASE / "E2.7-continuation-5000" / args.stamp
    durable = REMOTE_FINAL_BASE / "E2.7-continuation-5000" / args.stamp
    monitor_root = work / "monitors"
    scratch_root = work / "scratch"
    manifest: dict[str, Any] = {
        "status": "PREFLIGHT",
        "setup_id": "P72A-E2.7-CONTINUATION-5000-SERVER1",
        "server_id": SERVER_ID,
        "fluent_version_expected": "Ansys Fluent 2025 R2",
        "source_case": str(SOURCE_CASE),
        "source_data": SOURCE_DATA,
        "source_pair_observed_sha256": {"case": EXPECTED_CASE_SHA256, "data": EXPECTED_DATA_SHA256},
        "source_run_manifest_sha256": {
            "case": "e82b82dba2abcd2c4b0f1ca55cd0d926a50d9c5ad04ab69c7e666891b634165c",
            "data": "4b4221fd2cefcece9cf57a4d323425e69ffd4939f39329ad5971a5fafe287540",
        },
        "source_hash_note": "The local OneDrive pair and Server 1 bytes match each other but differ from the prior E2.7 run manifest hashes. The pair was loaded and validated at native 8586 with E2.7 EWF settings before this run.",
        "parent_native_iteration": START_ITERATION,
        "requested_additional_iterations": HORIZON,
        "expected_terminal_native_iteration": START_ITERATION + HORIZON,
        "controlled_delta": "No model change; 5,000-iteration continuation of the loaded E2.7 terminal pair.",
        "remote_paths": {
            "work_root": str(work),
            "monitor_root": str(monitor_root),
            "scratch_root": str(scratch_root),
            "durable_root": str(durable),
            "tui_command": f"/solve/iterate {HORIZON}",
        },
        "events": [],
    }
    dump(manifest_path, manifest)
    try:
        solver = connect(SERVER_ID, start_transcript=True, tcp_timeout_seconds=5)
        manifest["fluent_version"] = solver.get_fluent_version()
        require("2025 R2" in str(manifest["fluent_version"]), f"unexpected Fluent version: {manifest['fluent_version']}")
        for directory in (work, monitor_root, scratch_root, durable):
            ensure_remote_directory(solver, str(directory))
        for path in (SOURCE_CASE, PureWindowsPath(SOURCE_DATA)):
            require(remote_file_exists(solver, str(path)), f"source pair is not present on Server 1: {path}")
        source_hashes = {
            "case": remote_file_sha256(solver, str(SOURCE_CASE), str(scratch_root / "source-case.sha256.txt")),
            "data": remote_file_sha256(solver, SOURCE_DATA, str(scratch_root / "source-data.sha256.txt")),
        }
        require(source_hashes == {"case": EXPECTED_CASE_SHA256, "data": EXPECTED_DATA_SHA256}, f"source bytes changed after preflight: {source_hashes}")
        manifest["verified_source_hashes"] = source_hashes
        manifest["source_identity_gate"] = "PASS_BYTES_MATCH_PREFLIGHT; CASE-DATA DIFFER FROM PRIOR E2.7 RUN MANIFEST"

        # Re-read the exact shared pair after checking its bytes.  The existing
        # Server 1 R11 terminal pair has already been verified and preserved.
        solver.settings.file.read_case(file_name=str(SOURCE_CASE))
        solver.settings.file.read_data(file_name=SOURCE_DATA)

        start = native_iteration(solver)
        require(start == START_ITERATION, f"Server 1 is not loaded at E2.7 native 8586: {start}")
        manifest["verified_starting_iteration"] = start
        manifest["e27_readback"] = validate_e27(solver)
        report_files = solver.settings.solution.monitor.report_files
        names = sorted(str(item) for item in report_files.get_object_names())
        require(len(names) == 26, f"expected 26 E2.7 native report files, got {len(names)}")
        required_defs = {
            "p72a-e2.7-ewf-thickness-max",
            "p72a-e2.7-ewf-thickness-awavg",
            "p72a-e2.7-ewf-film-mass-total",
            "v2-flux-phase2-steamoutlet",
            "v2-flux-phase1-steamoutlet",
            "v2-flux-mixture-steamoutlet",
            "v2-applied-absorber",
            "v2-total-liquid-mass",
        }
        reports: dict[str, str] = {}
        report_states: dict[str, Any] = {}
        for name in names:
            obj = report_files[name]
            state = safe_get_state(obj, name)
            defs = state.get("report_defs") or []
            require(state.get("active") is True and int(state.get("frequency", 0)) == 1, f"inactive/non-iteration E2.7 report: {name}: {state}")
            require(len(defs) == 1, f"report file does not map to exactly one native definition: {name}")
            definition = str(defs[0])
            new_path = str(monitor_root / f"P72A-E2.7-CONT5000-{definition}.out")
            require(not remote_file_exists(solver, new_path), f"refusing to overwrite native report output: {new_path}")
            updated = {**state, "file_name": new_path, "frequency": 1, "active": True}
            obj.set_state(updated)
            readback = safe_get_state(obj, name)
            require(PureWindowsPath(str(readback.get("file_name"))) == PureWindowsPath(new_path), f"report path readback failed for {name}: {readback.get('file_name')!r}")
            require(int(readback.get("frequency", 0)) == 1 and readback.get("active") is True, f"report frequency readback failed for {name}")
            reports[definition] = new_path
            report_states[name] = readback
        require(required_defs.issubset(reports), f"required native monitoring definitions missing: {required_defs - set(reports)}")
        manifest["native_report_file_count"] = len(reports)
        manifest["native_report_frequency"] = 1
        manifest["native_reports"] = report_states
        manifest["residual_configuration"] = configure_residual_history(solver, HORIZON + 1)

        autosave = configure_autosave(solver, str(work), data_frequency=250)
        manifest["autosave_configuration"] = autosave
        manifest["instrumentation_gate"] = "PASS_READBACK_26_REPORT_FILES_FREQUENCY_1_EWF_FILM_RESIDUALS_ENABLED"
        dump(manifest_path, manifest)

        local_start = pair_save(solver, work / "P72A-E2.7-CONT5000-start-N8586.cas.h5", scratch_root, scratch_tag="local-start")
        durable_start = pair_save(solver, durable / "P72A-E2.7-CONT5000-start-N8586.cas.h5", scratch_root, scratch_tag="durable-start")
        manifest["local_start_pair"] = local_start
        manifest["durable_start_pair"] = durable_start
        # Reopen the saved, instrumented start pair before issuing Fluent's solve command.
        solver.settings.file.read_case(file_name=local_start["case"])
        solver.settings.file.read_data(file_name=local_start["data"])
        require(native_iteration(solver) == START_ITERATION, "instrumented start-pair reopen changed native iteration")
        manifest["reopen_e27_readback"] = validate_e27(solver)
        reopened_reports = solver.settings.solution.monitor.report_files
        for name in reopened_reports.get_object_names():
            state = safe_get_state(reopened_reports[str(name)], str(name))
            require(state.get("active") is True and int(state.get("frequency", 0)) == 1, f"report did not persist after reopen: {name}")
        manifest["prepared_reopen_gate"] = "PASS"
        dump(manifest_path, manifest)

        capture = SessionTranscriptCapture(solver, stream_path=local_root / "transcript-stream.txt", echo=False)
        capture.start()
        marker = capture.mark()
        manifest["status"] = "RUNNING_FLUENT_NATIVE_TUI"
        manifest["solve_command"] = f"/solve/iterate {HORIZON}"
        manifest["solve_started_utc"] = datetime.now(timezone.utc).isoformat()
        dump(manifest_path, manifest)
        # One native TUI command hands the complete solve horizon to Fluent.
        solver.execute_tui(f"/solve/iterate {HORIZON}\n")
        capture.wait_until_quiet(quiet_seconds=2.0, timeout_seconds=30.0)
        transcript = capture.text_since(marker)
        capture.close()
        transcript_path = local_root / "transcript-native-solve.txt"
        transcript_path.write_text(transcript, encoding="utf-8")
        manifest["native_solve_returned"] = True
        manifest["terminal_native_iteration"] = native_iteration(solver)
        manifest["transcript_lines"] = len(transcript.splitlines())
        manifest["ewf_residual_rows"] = len(re.findall(r"\bsub-iteration:\s*\d+\s+residual\s*-\s*h:", transcript, re.I))
        manifest["native_solve_event_flags"] = {
            "fpe": bool(re.search(r"floating point exception|floating-point exception|\bFPE\b", transcript, re.I)),
            "amg": bool(re.search(r"AMG solver.*(?:diverg|failed|failure)|divergence detected in AMG", transcript, re.I)),
            "nonfinite": bool(re.search(r"nan|infinity|nonfinite", transcript, re.I)),
            "fatal": bool(re.search(r"fatal error|aborted|unrecoverable", transcript, re.I)),
        }
        if manifest["terminal_native_iteration"] != START_ITERATION + HORIZON:
            failure_pair = pair_save(solver, work / f"P72A-E2.7-CONT5000-stop-N{manifest['terminal_native_iteration']}.cas.h5", scratch_root, scratch_tag="recovery")
            manifest["recovery_pair"] = failure_pair
            manifest["status"] = "BLOCKED"
            manifest["block_reason"] = "Fluent did not reach requested native iteration 13586."
            dump(manifest_path, manifest)
            return 1

        local_final = pair_save(solver, work / "P72A-E2.7-CONT5000-final-N13586.cas.h5", scratch_root, scratch_tag="local-final")
        durable_final = pair_save(solver, durable / "P72A-E2.7-CONT5000-final-N13586.cas.h5", scratch_root, scratch_tag="durable-final")
        manifest["local_final_pair"] = local_final
        manifest["durable_final_pair"] = durable_final
        histories: dict[str, Any] = {}
        for definition, report_path in reports.items():
            require(remote_file_exists(solver, report_path), f"native report output missing: {report_path}")
            history = parse_report_forms(read_remote_forms(solver, report_path))
            history.update({"definition_name": definition, "remote_file": report_path})
            histories[definition] = history
        history_path = local_root / "report-histories.json"
        dump(history_path, histories)
        point_counts = {name: int(record.get("points", 0)) for name, record in histories.items()}
        manifest["report_history_points"] = point_counts
        manifest["reports_complete_each_iteration"] = all(count >= HORIZON for count in point_counts.values())
        require(manifest["reports_complete_each_iteration"], f"one or more native reports have fewer than {HORIZON} points: {point_counts}")
        manifest["achieved_additional_iterations"] = HORIZON
        manifest["solve_finished_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["status"] = "COMPLETE"
        dump(manifest_path, manifest)
        # Do not call solver.exit(); Server 1's Fluent session remains available.
        return 0
    except Exception as exc:
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        dump(manifest_path, manifest)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
