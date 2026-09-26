#!/usr/bin/env python3
"""Recover E2.8 from its preserved native-7000 stable checkpoint.

The aggressive adaptive segment is preserved as-run. This continuation uses
the proven E2.7 fixed-step controls only for the remaining native horizon,
keeps its reports/checkpoints in separate locations, and joins only the valid
trajectory rows when the run reaches native 8586.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path, PureWindowsPath
import re
import shutil
import sys
import time
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "PyAnsys" / "scripts" / "setup"))

import run_phase72a_e28_direct as e28  # noqa: E402


PARENT_NATIVE = 5586
FAST_STOP_NATIVE = 7000
FINAL_NATIVE = 8586
RECOVERY_BATCHES = (1000, 586)
TARGET_CONTROLS = {
    "ewf-adaptive?": False,
    "courant-number": 0.05,
    "timestep-max": 1.0e-5,
    "sub-iter-nums": 10,
    "sub-iter-stop": 1.0e-5,
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _near(actual: Any, expected: float, label: str) -> None:
    _require(
        actual is not None and abs(float(actual) - expected) <= max(1e-12, abs(expected) * 1e-9),
        f"{label} mismatch: expected {expected!r}, got {actual!r}",
    )


def _set_recovery_controls(solver: Any) -> dict[str, Any]:
    parameters = solver.rp_vars().get("wall-film/model-parameters")
    _require(isinstance(parameters, list), "EWF model parameters are unavailable")
    prior = dict(parameters)
    missing = set(TARGET_CONTROLS) - set(prior)
    _require(not missing, f"Fluent is missing EWF controls: {sorted(missing)}")
    solver.rp_vars(
        "wall-film/model-parameters",
        [(key, TARGET_CONTROLS.get(str(key), value)) for key, value in parameters],
    )
    actual = dict(solver.rp_vars().get("wall-film/model-parameters"))
    for key, expected in TARGET_CONTROLS.items():
        if isinstance(expected, float):
            _near(actual.get(key), expected, f"EWF control {key}")
        else:
            _require(actual.get(key) == expected, f"EWF control {key}: {actual.get(key)!r}")

    wall = solver.settings.setup.boundary_conditions.wall
    film_wall = wall["wall"].phase["mixture"].wall_film.get_state()
    bottom = wall["bottom"].phase["mixture"].wall_film.get_state()
    _require(film_wall.get("eulerian_film_wall") is True, "wall is not configured as an EWF wall")
    _require(film_wall.get("enable_flow_momentum_coupling") is False, "flow momentum coupling changed")
    _require(bottom.get("eulerian_film_wall") is not True, "bottom unexpectedly became an EWF wall")
    _require(int(actual.get("secondary-phase-mode", -1)) == 1, "Phase Accretion is not enabled")
    _require(actual.get("film-coupled-solution?") is True, "EWF Coupled Solution is not ON")
    return {"model_parameters": actual, "film_wall": film_wall, "bottom_wall": bottom}


def _pair_paths(case_path: Path) -> tuple[Path, Path]:
    return case_path, Path(str(case_path).replace(".cas.h5", ".dat.h5"))


def _save_checkpoint_pair(solver: Any, case_path: Path) -> dict[str, Any]:
    if case_path.exists() or Path(str(case_path).replace(".cas.h5", ".dat.h5")).exists():
        raise RuntimeError(f"Refusing to overwrite recovery checkpoint pair: {case_path}")
    return e28.save_pair(solver, case_path)


def _combine_report_histories(
    solver: Any,
    original_paths: dict[str, str],
    recovery_paths: dict[str, str],
) -> dict[str, dict[str, Any]]:
    expected_iterations = list(range(PARENT_NATIVE, FINAL_NATIVE + 1))
    combined: dict[str, dict[str, Any]] = {}
    for definition, recovery_path in recovery_paths.items():
        original_path = original_paths.get(definition)
        _require(original_path is not None, f"Missing original report path for {definition}")
        primary = e28.parse_report_forms(e28.read_remote_forms(solver, original_path))
        recovery = e28.parse_report_forms(e28.read_remote_forms(solver, recovery_path))
        selected: dict[int, float] = {
            int(iteration): float(value)
            for iteration, value in zip(primary["iterations"], primary["values"])
            if int(iteration) <= FAST_STOP_NATIVE
        }
        for iteration, value in zip(recovery["iterations"], recovery["values"]):
            native = int(iteration)
            if native > FAST_STOP_NATIVE:
                if native in selected:
                    raise RuntimeError(f"Duplicate selected report coordinate for {definition}: {native}")
                selected[native] = float(value)
        iterations = sorted(selected)
        if iterations != expected_iterations:
            missing = sorted(set(expected_iterations) - set(iterations))
            extra = sorted(set(iterations) - set(expected_iterations))
            raise RuntimeError(
                f"Selected report history is incomplete for {definition}: "
                f"points={len(iterations)}, missing={missing[:8]}, extra={extra[:8]}"
            )
        values = [selected[native] for native in iterations]
        record = dict(primary)
        record.update(
            {
                "definition_name": definition,
                "points": len(iterations),
                "iterations": iterations,
                "values": values,
                "summary": {
                    "first_iteration": iterations[0],
                    "last_iteration": iterations[-1],
                    "first_value": values[0],
                    "last_value": values[-1],
                    "minimum": min(values),
                    "maximum": max(values),
                },
                "selected_trajectory_sources": {
                    "fast_adaptive_through_native": FAST_STOP_NATIVE,
                    "fast_report_file": original_path,
                    "fixed_step_recovery_after_native": FAST_STOP_NATIVE,
                    "recovery_report_file": recovery_path,
                },
            }
        )
        combined[definition] = record
    return combined


def _selected_fast_transcript(source: Path, stop_native: int) -> str:
    def native_row(line: str) -> int | None:
        fields = line.split()
        if len(fields) < 10 or not fields[0].isdigit() or len(fields[0]) < 4:
            return None
        if not re.fullmatch(r"(?:\d+:)?\d{2}:\d{2}", fields[-2]) or not fields[-1].isdigit():
            return None
        try:
            for value in fields[1:-2]:
                float(value)
        except ValueError:
            return None
        return int(fields[0])

    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    retained: list[str] = []
    current_native: int | None = None
    for line in lines:
        native = native_row(line)
        if native is not None:
            current_native = native
            if current_native > stop_native:
                break
        if current_native is None or current_native <= stop_native:
            retained.append(line)
    native_rows = [native for line in retained if (native := native_row(line)) is not None]
    _require(native_rows and native_rows[-1] <= stop_native, "Fast transcript prefix has no selected native rows")
    return "\n".join(retained).rstrip() + "\n"


def _copy_selected_checkpoints(
    original_root: Path,
    recovery_root: Path,
    trajectory_root: Path,
) -> list[dict[str, Any]]:
    trajectory_root.mkdir(parents=True, exist_ok=True)
    selected: list[dict[str, Any]] = []
    candidates: list[tuple[Path, int]] = []
    for path in original_root.glob("checkpoint-*.cas.h5"):
        match = re.search(r"checkpoint-(\d+)-", path.name)
        native = int(match.group(1)) if match else None
        if native is not None and PARENT_NATIVE < native <= FAST_STOP_NATIVE:
            candidates.append((path, native))
    for path in recovery_root.glob("checkpoint-*.cas.h5"):
        match = re.search(r"checkpoint-(\d+)-", path.name)
        native = int(match.group(1)) if match else None
        if native is not None and FAST_STOP_NATIVE < native < FINAL_NATIVE:
            candidates.append((path, native))

    seen: set[int] = set()
    for source_case, native in sorted(candidates, key=lambda item: item[1]):
        if native in seen:
            continue
        source_data = Path(str(source_case).replace(".cas.h5", ".dat.h5"))
        _require(source_case.is_file() and source_data.is_file(), f"Incomplete checkpoint pair at native {native}")
        dest_case, dest_data = trajectory_root / source_case.name, trajectory_root / source_data.name
        if not dest_case.exists():
            shutil.copy2(source_case, dest_case)
        if not dest_data.exists():
            shutil.copy2(source_data, dest_data)
        _require(e28.sha256(source_case) == e28.sha256(dest_case), f"Checkpoint case copy hash mismatch at {native}")
        _require(e28.sha256(source_data) == e28.sha256(dest_data), f"Checkpoint data copy hash mismatch at {native}")
        selected.append({"native_iteration": native, "case": str(dest_case), "data": str(dest_data)})
        seen.add(native)
    return selected


def run_recovery(solver: Any, original_manifest_file: str | Path) -> dict[str, Any]:
    original_manifest_path = Path(original_manifest_file)
    original = json.loads(original_manifest_path.read_text(encoding="utf-8"))
    local_root = Path(original["local_run_root"])
    durable_root = Path(original["onedrive_root"])
    output_root = Path(original["local_output_root"])
    original_checkpoint_root = Path(original["local_checkpoint_root"])
    original_monitor_root = Path(original["local_monitor_root"])
    recovery_checkpoint_root = local_root / "recovery-checkpoints"
    recovery_monitor_root = local_root / "monitors-recovery"
    trajectory_checkpoint_root = local_root / "trajectory-checkpoints"
    recovery_manifest_path = output_root / "recovery-run-manifest.json"
    recovery_transcript_path = output_root / "transcript-recovery-native-7000-8586.txt"
    combined_transcript_path = output_root / "transcript-native-solve.txt"

    _require("2025 R2" in str(solver.get_fluent_version()), "E2.8 recovery requires Fluent 2025 R2")
    _require(not recovery_manifest_path.exists(), f"Recovery manifest already exists: {recovery_manifest_path}")
    _require(not recovery_checkpoint_root.exists(), f"Recovery checkpoint directory already exists: {recovery_checkpoint_root}")
    _require(not recovery_monitor_root.exists(), f"Recovery monitor directory already exists: {recovery_monitor_root}")
    _require(not trajectory_checkpoint_root.exists(), f"Trajectory checkpoint directory already exists: {trajectory_checkpoint_root}")

    recovery_base = original.get("recovery_base_pair") or {}
    base_case = Path(recovery_base.get("case", ""))
    base_data = Path(recovery_base.get("data", ""))
    _require(base_case.is_file() and base_data.is_file(), "Preserved native-7000 recovery pair is missing")
    _require(e28.sha256(base_case) == recovery_base.get("case_sha256"), "Native-7000 recovery case hash mismatch")
    _require(e28.sha256(base_data) == recovery_base.get("data_sha256"), "Native-7000 recovery data hash mismatch")
    _require(int(recovery_base.get("native_iteration", -1)) == FAST_STOP_NATIVE, "Recovery base is not native 7000")

    recovery_checkpoint_root.mkdir(parents=True, exist_ok=False)
    recovery_monitor_root.mkdir(parents=True, exist_ok=False)
    report_paths = dict(original["report_paths"])
    recovery_report_paths = {
        definition: str(recovery_monitor_root / PureWindowsPath(path).name)
        for definition, path in report_paths.items()
    }
    for path in recovery_report_paths.values():
        _require(not Path(path).exists(), f"Recovery report output already exists: {path}")

    autosave_state = dict(original["autosave_readback"])
    autosave_state["root_name"] = str(recovery_checkpoint_root / "checkpoint-%i")
    recovery_manifest: dict[str, Any] = {
        "status": "PREPARING",
        "experiment": "E2.8",
        "branch": "stable-control-recovery-from-native-7000",
        "fluent_version": str(solver.get_fluent_version()),
        "original_manifest": str(original_manifest_path),
        "original_fast_branch_status": original.get("status"),
        "selected_trajectory": {
            "start_native": PARENT_NATIVE,
            "fast_adaptive_stop_native": FAST_STOP_NATIVE,
            "final_native": FINAL_NATIVE,
            "requested_additional_iterations": FINAL_NATIVE - PARENT_NATIVE,
            "valid_fast_iterations": FAST_STOP_NATIVE - PARENT_NATIVE,
            "fixed_step_recovery_iterations": FINAL_NATIVE - FAST_STOP_NATIVE,
            "discarded_divergent_iterations_after_recovery_base": max(
                0, int(original.get("terminal_native_iteration", FAST_STOP_NATIVE)) - FAST_STOP_NATIVE
            ),
        },
        "recovery_base_pair": recovery_base,
        "local_run_root": str(local_root),
        "local_recovery_checkpoint_root": str(recovery_checkpoint_root),
        "local_recovery_monitor_root": str(recovery_monitor_root),
        "local_trajectory_checkpoint_root": str(trajectory_checkpoint_root),
        "local_output_root": str(output_root),
        "onedrive_root": str(durable_root),
        "requested_recovery_iterations": FINAL_NATIVE - FAST_STOP_NATIVE,
        "solve_batches": list(RECOVERY_BATCHES),
        "report_paths": recovery_report_paths,
        "original_fast_report_paths": report_paths,
        "autosave_readback_requested": autosave_state,
        "batches": [],
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    e28.dump(recovery_manifest_path, recovery_manifest)

    capture: Any = None
    recovery_started = time.perf_counter()
    try:
        print(f"E2.8 recovery: loading exact stable native-{FAST_STOP_NATIVE} pair", flush=True)
        solver.settings.file.read_case(file_name=str(base_case))
        solver.settings.file.read_data(file_name=str(base_data))
        _require(e28.native_iteration(solver) == FAST_STOP_NATIVE, "Loaded recovery pair is not native 7000")
        recovery_manifest["loaded_recovery_base_native_iteration"] = e28.native_iteration(solver)
        recovery_manifest["recovery_base_film_solution_state"] = e28.film_solution_state(solver)
        recovery_manifest["recovery_controls_before_save"] = _set_recovery_controls(solver)

        route_before_save = e28.route_report_file_outputs(solver, recovery_report_paths)
        solver.settings.file.auto_save.set_state(autosave_state)
        autosave_readback = solver.settings.file.auto_save.get_state()
        _require(int(autosave_readback.get("data_frequency", 0)) == 250, "Recovery checkpoint data frequency mismatch")
        _require(int(autosave_readback.get("max_files", 0)) == 20, "Recovery checkpoint retention mismatch")
        _require(
            PureWindowsPath(str(autosave_readback.get("root_name", "")))
            == PureWindowsPath(autosave_state["root_name"]),
            "Recovery checkpoint root did not persist",
        )
        recovery_manifest["report_path_routing_before_start_save"] = route_before_save
        recovery_manifest["autosave_readback_before_start_save"] = autosave_readback
        recovery_manifest["residual_history_before_start_save"] = e28.configure_residual_history(
            solver, FINAL_NATIVE - FAST_STOP_NATIVE + 1
        )

        start_case = local_root / f"P72A-E2.8-recovery-start-N{FAST_STOP_NATIVE}.cas.h5"
        durable_start_case = durable_root / f"P72A-E2.8-recovery-start-N{FAST_STOP_NATIVE}.cas.h5"
        local_start = e28.save_pair(solver, start_case)
        durable_start = e28.copy_saved_pair(solver, local_start, durable_start_case)
        recovery_manifest["local_recovery_start_pair"] = local_start
        recovery_manifest["durable_recovery_start_pair"] = durable_start

        print("E2.8 recovery: reopening saved N7000 recovery pair for setup readback", flush=True)
        solver.settings.file.read_case(file_name=local_start["case"])
        solver.settings.file.read_data(file_name=local_start["data"])
        _require(e28.native_iteration(solver) == FAST_STOP_NATIVE, "Reopened recovery start is not native 7000")
        recovery_manifest["recovery_controls_after_reopen"] = _set_recovery_controls(solver)
        recovery_manifest["report_path_routing_after_reopen"] = e28.route_report_file_outputs(
            solver, recovery_report_paths
        )
        solver.settings.file.auto_save.set_state(autosave_state)
        recovery_manifest["autosave_readback_after_reopen"] = solver.settings.file.auto_save.get_state()
        _require(
            PureWindowsPath(str(recovery_manifest["autosave_readback_after_reopen"].get("root_name", "")))
            == PureWindowsPath(autosave_state["root_name"]),
            "Reopened recovery checkpoint root did not persist",
        )
        recovery_manifest["residual_history_after_reopen"] = e28.configure_residual_history(
            solver, FINAL_NATIVE - FAST_STOP_NATIVE + 1
        )
        recovery_manifest["start_reopen_film_solution_state"] = e28.film_solution_state(solver)
        recovery_manifest["start_pair_reopen_gate"] = "PASS"
        recovery_manifest["status"] = "PREPARED"
        e28.dump(recovery_manifest_path, recovery_manifest)

        recovery_transcript_path.write_text("", encoding="utf-8")
        capture = e28.SessionTranscriptCapture(
            solver,
            stream_path=local_root / "transcript-recovery-stream.txt",
            echo=False,
        ).start()
        recovery_manifest["status"] = "RUNNING"
        recovery_manifest["solve_started_utc"] = datetime.now(timezone.utc).isoformat()
        e28.dump(recovery_manifest_path, recovery_manifest)

        for index, steps in enumerate(RECOVERY_BATCHES, start=1):
            expected_native = FAST_STOP_NATIVE + sum(RECOVERY_BATCHES[:index])
            marker = capture.mark()
            batch_started = time.perf_counter()
            print(
                f"E2.8 recovery: starting batch {index}/{len(RECOVERY_BATCHES)} "
                f"({steps} iterations) to native {expected_native}",
                flush=True,
            )
            solver.execute_tui(f"/solve/iterate {steps}\n")
            capture.wait_until_quiet(quiet_seconds=1.0, timeout_seconds=60.0)
            segment = capture.text_since(marker)
            with recovery_transcript_path.open("a", encoding="utf-8") as handle:
                handle.write(segment)
            actual_native = e28.native_iteration(solver)
            batch_record = {
                "batch": index,
                "requested_iterations": steps,
                "expected_native_iteration": expected_native,
                "actual_native_iteration": actual_native,
                "elapsed_wall_seconds": time.perf_counter() - batch_started,
                "ewf_solution_state": e28.film_solution_state(solver),
                "transcript_chars": len(segment),
            }
            recovery_manifest["batches"].append(batch_record)
            recovery_manifest["last_native_iteration"] = actual_native
            e28.dump(recovery_manifest_path, recovery_manifest)
            print(
                f"E2.8 recovery: batch {index} ended at native {actual_native}; "
                f"film state {batch_record['ewf_solution_state']}",
                flush=True,
            )
            if actual_native != expected_native:
                recovery_manifest["status"] = "INTERRUPTED_SHORT_OF_REQUESTED_HORIZON"
                emergency_case = local_root / f"P72A-E2.8-recovery-interrupted-N{actual_native}.cas.h5"
                if not emergency_case.exists():
                    recovery_manifest["interrupted_pair"] = _save_checkpoint_pair(solver, emergency_case)
                e28.dump(recovery_manifest_path, recovery_manifest)
                return recovery_manifest

        capture.wait_until_quiet(quiet_seconds=1.0, timeout_seconds=60.0)
        capture.close()
        capture = None
        transcript_text = recovery_transcript_path.read_text(encoding="utf-8", errors="replace")
        recovery_manifest["transcript_lines"] = len(transcript_text.splitlines())
        recovery_manifest["event_flags"] = {
            "fpe": bool(re.search(r"floating point exception|floating-point exception|\bFPE\b", transcript_text, re.I)),
            "amg_divergence": bool(re.search(r"AMG solver.*(?:diverg|failed|failure)|divergence detected in AMG", transcript_text, re.I)),
            "nonfinite": bool(re.search(r"\bnan\b|\binfinity\b|\bnonfinite\b", transcript_text, re.I)),
            "fatal": bool(re.search(r"fatal error|aborted|unrecoverable", transcript_text, re.I)),
        }
        final_native = e28.native_iteration(solver)
        _require(final_native == FINAL_NATIVE, f"Recovery ended at native {final_native}, expected {FINAL_NATIVE}")

        final_case = local_root / f"P72A-E2.8-final-N{final_native}.cas.h5"
        durable_final_case = durable_root / final_case.name
        local_final = e28.save_pair(solver, final_case)
        durable_final = e28.copy_saved_pair(solver, local_final, durable_final_case)
        recovery_manifest["local_final_pair"] = local_final
        recovery_manifest["durable_final_pair"] = durable_final
        recovery_manifest["final_film_solution_state"] = e28.film_solution_state(solver)

        histories = _combine_report_histories(solver, report_paths, recovery_report_paths)
        e28.dump(output_root / "report-histories.json", histories)
        recovery_manifest["report_history_points"] = {
            definition: int(history["points"]) for definition, history in histories.items()
        }
        recovery_manifest["reports_complete_each_iteration"] = all(
            int(history["points"]) == FINAL_NATIVE - PARENT_NATIVE + 1
            for history in histories.values()
        )
        recovery_manifest["report_definition_count"] = len(histories)

        original_transcript = output_root / "transcript-divergence-native-5586-7318.txt"
        _require(original_transcript.is_file(), f"Missing preserved primary transcript: {original_transcript}")
        fast_prefix = _selected_fast_transcript(original_transcript, FAST_STOP_NATIVE)
        (output_root / "transcript-fast-prefix-native-5586-7000.txt").write_text(
            fast_prefix, encoding="utf-8"
        )
        combined_transcript_path.write_text(
            fast_prefix.rstrip() + "\n\n" + transcript_text.lstrip(), encoding="utf-8"
        )

        selected_checkpoints = _copy_selected_checkpoints(
            original_checkpoint_root,
            recovery_checkpoint_root,
            trajectory_checkpoint_root,
        )
        recovery_manifest["selected_checkpoint_pairs"] = selected_checkpoints
        recovery_manifest["selected_checkpoint_pair_count"] = len(selected_checkpoints)
        analysis_manifest = dict(original)
        analysis_manifest.update(
            {
                "status": "SELECTED_TRAJECTORY_READY_FOR_ANALYSIS",
                "local_checkpoint_root": str(trajectory_checkpoint_root),
                "selected_trajectory_manifest": str(recovery_manifest_path),
                "selected_trajectory_native_range": [PARENT_NATIVE, FINAL_NATIVE],
            }
        )
        analysis_manifest_path = output_root / "analysis-manifest.json"
        e28.dump(analysis_manifest_path, analysis_manifest)

        recovery_manifest["elapsed_wall_seconds"] = time.perf_counter() - recovery_started
        recovery_manifest["solve_finished_utc"] = datetime.now(timezone.utc).isoformat()
        recovery_manifest["selected_trajectory"] = {
            **recovery_manifest["selected_trajectory"],
            "selected_report_points_each": FINAL_NATIVE - PARENT_NATIVE + 1,
            "total_film_time_s": float(recovery_manifest["final_film_solution_state"]["film_elapsed_time"])
            - float(recovery_manifest["start_reopen_film_solution_state"]["film_elapsed_time"]),
        }
        numerical_event = any(recovery_manifest["event_flags"].values())
        recovery_manifest["status"] = (
            "COMPLETE_WITH_REPORT_GAP"
            if not recovery_manifest["reports_complete_each_iteration"]
            else "COMPLETE_WITH_NUMERICAL_EVENTS"
            if numerical_event
            else "COMPLETE"
        )
        e28.dump(recovery_manifest_path, recovery_manifest)

        original["recovery_branch"] = {
            "manifest": str(recovery_manifest_path),
            "status": recovery_manifest["status"],
            "final_native_iteration": final_native,
            "local_final_pair": local_final,
            "durable_final_pair": durable_final,
            "selected_trajectory_native_range": [PARENT_NATIVE, FINAL_NATIVE],
            "analysis_manifest": str(analysis_manifest_path),
        }
        e28.dump(original_manifest_path, original)
        return recovery_manifest
    except Exception as exc:
        recovery_manifest["status"] = "RECOVERY_ERROR"
        recovery_manifest["error"] = f"{type(exc).__name__}: {exc}"
        recovery_manifest["traceback"] = traceback.format_exc()
        try:
            actual_native = e28.native_iteration(solver)
            recovery_manifest["last_native_iteration"] = actual_native
            emergency_case = local_root / f"P72A-E2.8-recovery-interrupted-N{actual_native}.cas.h5"
            if not emergency_case.exists():
                recovery_manifest["interrupted_pair"] = _save_checkpoint_pair(solver, emergency_case)
        except Exception as save_error:
            recovery_manifest["interrupted_pair_save_error"] = f"{type(save_error).__name__}: {save_error}"
        e28.dump(recovery_manifest_path, recovery_manifest)
        raise
    finally:
        if capture is not None:
            capture.close()


def finalize_recovery(solver: Any, original_manifest_file: str | Path) -> dict[str, Any]:
    """Finish evidence assembly after an already completed native-8586 solve."""
    original_manifest_path = Path(original_manifest_file)
    original = json.loads(original_manifest_path.read_text(encoding="utf-8"))
    output_root = Path(original["local_output_root"])
    local_root = Path(original["local_run_root"])
    recovery_manifest_path = output_root / "recovery-run-manifest.json"
    recovery_manifest = json.loads(recovery_manifest_path.read_text(encoding="utf-8"))
    _require(e28.native_iteration(solver) == FINAL_NATIVE, "Live Fluent session is not at native 8586")
    _require(int(recovery_manifest.get("last_native_iteration", -1)) == FINAL_NATIVE,
             "Recovery manifest does not record native 8586")

    local_final = recovery_manifest.get("local_final_pair")
    durable_final = recovery_manifest.get("durable_final_pair")
    _require(isinstance(local_final, dict) and isinstance(durable_final, dict),
             "Saved native-8586 local/shared final pairs are not recorded")
    for label, pair in (("local", local_final), ("OneDrive", durable_final)):
        case_path, data_path = Path(pair["case"]), Path(pair["data"])
        _require(case_path.is_file() and data_path.is_file(), f"{label} final pair is missing")
        _require(e28.sha256(case_path) == pair["case_sha256"], f"{label} final case hash mismatch")
        _require(e28.sha256(data_path) == pair["data_sha256"], f"{label} final data hash mismatch")
    _require(local_final["case_sha256"] == durable_final["case_sha256"], "Local/shared final cases differ")
    _require(local_final["data_sha256"] == durable_final["data_sha256"], "Local/shared final data differ")

    recovery_report_paths = dict(recovery_manifest["report_paths"])
    original_report_paths = dict(recovery_manifest["original_fast_report_paths"])
    histories = _combine_report_histories(solver, original_report_paths, recovery_report_paths)
    e28.dump(output_root / "report-histories.json", histories)
    expected_points = FINAL_NATIVE - PARENT_NATIVE + 1
    point_counts = {definition: int(record["points"]) for definition, record in histories.items()}
    recovery_manifest["report_history_points"] = point_counts
    recovery_manifest["reports_complete_each_iteration"] = all(
        count == expected_points for count in point_counts.values()
    )
    recovery_manifest["report_definition_count"] = len(histories)

    original_transcript = output_root / "transcript-divergence-native-5586-7318.txt"
    recovery_transcript_path = output_root / "transcript-recovery-native-7000-8586.txt"
    _require(original_transcript.is_file(), f"Missing preserved fast-branch transcript: {original_transcript}")
    _require(recovery_transcript_path.is_file(), f"Missing fixed-step recovery transcript: {recovery_transcript_path}")
    fast_prefix = _selected_fast_transcript(original_transcript, FAST_STOP_NATIVE)
    (output_root / "transcript-fast-prefix-native-5586-7000.txt").write_text(fast_prefix, encoding="utf-8")
    recovery_text = recovery_transcript_path.read_text(encoding="utf-8", errors="replace")
    (output_root / "transcript-native-solve.txt").write_text(
        fast_prefix.rstrip() + "\n\n" + recovery_text.lstrip(), encoding="utf-8"
    )

    trajectory_root = Path(recovery_manifest["local_trajectory_checkpoint_root"])
    selected_checkpoints = _copy_selected_checkpoints(
        Path(original["local_checkpoint_root"]),
        Path(recovery_manifest["local_recovery_checkpoint_root"]),
        trajectory_root,
    )
    recovery_manifest["selected_checkpoint_pairs"] = selected_checkpoints
    recovery_manifest["selected_checkpoint_pair_count"] = len(selected_checkpoints)
    analysis_manifest = dict(original)
    analysis_manifest.update(
        {
            "status": "SELECTED_TRAJECTORY_READY_FOR_ANALYSIS",
            "local_checkpoint_root": str(trajectory_root),
            "selected_trajectory_manifest": str(recovery_manifest_path),
            "selected_trajectory_native_range": [PARENT_NATIVE, FINAL_NATIVE],
        }
    )
    analysis_manifest_path = output_root / "analysis-manifest.json"
    e28.dump(analysis_manifest_path, analysis_manifest)

    recovery_state = e28.film_solution_state(solver)
    start_state = recovery_manifest["start_reopen_film_solution_state"]
    prior_error = recovery_manifest.get("error")
    recovery_manifest["pre_finalization_error"] = prior_error
    recovery_manifest["pre_finalization_traceback"] = recovery_manifest.get("traceback")
    recovery_manifest["post_solve_finalization_recovered"] = True
    recovery_manifest["final_film_solution_state"] = recovery_state
    recovery_manifest["selected_trajectory"]["recovery_film_time_increment_s"] = (
        float(recovery_state["film_elapsed_time"]) - float(start_state["film_elapsed_time"])
    )
    recovery_manifest["selected_trajectory"]["final_film_elapsed_time_s"] = float(
        recovery_state["film_elapsed_time"]
    )
    recovery_manifest["selected_trajectory"]["selected_report_points_each"] = expected_points
    recovery_manifest["actual_solver_iterations_including_discarded_branch"] = (
        int(original.get("achieved_additional_iterations_before_divergence", 0))
        + (FINAL_NATIVE - FAST_STOP_NATIVE)
    )
    recovery_manifest.pop("error", None)
    recovery_manifest.pop("traceback", None)
    recovery_manifest["solve_finished_utc"] = recovery_manifest.get("solve_finished_utc") or datetime.now(timezone.utc).isoformat()
    recovery_manifest["status"] = (
        "COMPLETE" if recovery_manifest["reports_complete_each_iteration"] else "COMPLETE_WITH_REPORT_GAP"
    )
    e28.dump(recovery_manifest_path, recovery_manifest)

    original["recovery_branch"] = {
        "manifest": str(recovery_manifest_path),
        "status": recovery_manifest["status"],
        "final_native_iteration": FINAL_NATIVE,
        "local_final_pair": local_final,
        "durable_final_pair": durable_final,
        "selected_trajectory_native_range": [PARENT_NATIVE, FINAL_NATIVE],
        "analysis_manifest": str(analysis_manifest_path),
    }
    e28.dump(original_manifest_path, original)
    return recovery_manifest
