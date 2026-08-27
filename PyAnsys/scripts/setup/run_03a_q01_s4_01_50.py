#!/usr/bin/env python3
"""Run the selected 03A-Q01 continuation from the verified S4-01 endpoint.

This is deliberately a single-branch, hard-bounded native-run owner.  It
prepares a new case-only child, verifies the unchanged scientific state, and
asks Fluent to execute exactly 50 iterations from the S4-01 endpoint.  Fluent
owns the iteration, autosave, transcript, and endpoint writes; this script
does not poll or replay the solve.
"""

from __future__ import annotations

import contextlib
from datetime import datetime, timezone
import argparse
import io
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sys
import time
import traceback
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import (  # noqa: E402
    parse_parallel_connectivity_roster,
    quote_scheme_string,
    remote_file_exists,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    EventLog,
    Tee,
    assert_controlled_scientific_delta,
    configure_autosave,
    configure_residual_history,
    data_path,
    ensure_remote_directory,
    exclusive_writer_lock,
    redirect_report_files,
    remote_file_sha256,
    remote_text_read,
    render_native_queue,
    scientific_readback,
    verify_parent_state,
    verify_report_file_location,
    win,
    write_new_json,
    write_remote_text_new,
    write_status,
)


EXPECTED_VERSION = "2025 R2"
EXPECTED_RANKS = 18
ITERATIONS = 50
EXPERIMENT_ID = "03A-Q01"
REMOTE_BRANCH_ROOT = r"C:\Users\syok443\Documents\FluentRuns\03A-stage4\S4-01"
REMOTE_PARENT_CASE = (
    REMOTE_BRANCH_ROOT
    + r"\run-20260822T123011Z\03A-stage4-S4-01-plus030000-end-20260822T123011Z.cas.h5"
)
REMOTE_PARENT_DATA = (
    REMOTE_BRANCH_ROOT
    + r"\run-20260822T123011Z\03A-stage4-S4-01-plus030000-end-20260822T123011Z.dat.h5"
)
PARENT_CUMULATIVE_ITERATION = 33_000
EXPECTED_PARENT_CASE_SHA256 = "dfbc0109e910f11f71d9c15956f49a3ab81a015e2d5d7a43f7d366e75aec1126"
EXPECTED_PARENT_DATA_SHA256 = "f52a7f91cbadaa276eab851bde16a0f1c2a92dfa39c7c005517d28f2f8706249"


def build_parser() -> argparse.ArgumentParser:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="2")
    parser.add_argument(
        "--run-stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    )
    return parser


def rp_value(solver: Any, variable: str) -> Any:
    last_error: Exception | None = None
    for expression in (f"(%rpgetvar '{variable})", f"(rpgetvar '{variable})"):
        try:
            return solver.scheme.eval(expression)
        except Exception as exc:
            last_error = exc
    if last_error is None:
        raise RuntimeError(f"Could not read Fluent RP variable {variable}")
    raise last_error


def rp_clock(solver: Any) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for variable in ("current-iteration", "number-of-iterations", "flow-time", "time-step"):
        try:
            values[variable] = rp_value(solver, variable)
        except Exception as exc:
            values[variable] = f"{type(exc).__name__}: {exc}"
    return values


def prove_quiescent(solver: Any, *, samples: int = 3, delay_seconds: float = 2.0) -> dict[str, Any]:
    clocks: list[dict[str, Any]] = []
    for index in range(samples):
        clocks.append({"current-iteration": rp_value(solver, "current-iteration")})
        if index + 1 < samples:
            time.sleep(delay_seconds)
    current = [sample["current-iteration"] for sample in clocks]
    if any(isinstance(value, Mapping) for value in current) or len(set(current)) != 1:
        raise RuntimeError(f"Could not prove Fluent quiescence: {clocks!r}")
    try:
        solver.settings.solution.controls.equations.get_state()
    except Exception as exc:
        raise RuntimeError(f"Fluent equation-control readback failed during quiescence check: {exc}") from exc
    return {"samples": clocks, "quiescent": True}


def capture_exclusive_clients(solver: Any) -> dict[str, Any]:
    """Capture the server report through the transcript stream.

    Fluent 2025 R2 emits this TUI report to the transcript rather than as the
    return value of the PyFluent TUI wrapper.  The report is required to say
    that no other client is connected before this owner mutates the session.
    """

    transcript = getattr(solver, "transcript", None)
    if transcript is None:
        raise RuntimeError("Fluent transcript service is unavailable for ownership preflight")
    command = "/server/print-connected-grpc-clients"
    buffer = io.StringIO()
    result: Any = None
    try:
        if bool(getattr(transcript, "is_streaming", False)):
            transcript.stop()
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            transcript.start(write_to_stdout=True)
            try:
                result = solver.tui.server.print_connected_grpc_clients()
            except AttributeError:
                command = "/server/print-connected-clients"
                result = solver.tui.server.print_connected_clients()
            time.sleep(1.0)
    finally:
        try:
            transcript.stop()
        except Exception:
            pass
    raw_report = buffer.getvalue()
    normalized = " ".join(raw_report.casefold().split())
    print(f"Connected-client command: {command}", flush=True)
    print(f"Connected-client report: {raw_report!r}", flush=True)
    if "no client is connected to server" not in normalized:
        raise RuntimeError(
            "Remote Fluent ownership is not proven exclusive; report was "
            f"{raw_report!r}"
        )
    return {
        "command": command,
        "raw_report": raw_report,
        "result": str(result),
        "exclusive": True,
    }


def capture_parallel_roster(solver: Any) -> dict[str, Any]:
    """Capture the parallel roster through the same native transcript route."""

    transcript = getattr(solver, "transcript", None)
    if transcript is None:
        raise RuntimeError("Fluent transcript service is unavailable for rank preflight")
    buffer = io.StringIO()
    try:
        if bool(getattr(transcript, "is_streaming", False)):
            transcript.stop()
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            transcript.start(write_to_stdout=True)
            try:
                solver.settings.parallel.show_connectivity(compute_node=0)
            finally:
                time.sleep(3.0)
    finally:
        try:
            transcript.stop()
        except Exception:
            pass
    raw_report = buffer.getvalue()
    parsed = parse_parallel_connectivity_roster(raw_report)
    parsed["raw_report"] = raw_report
    print(
        f"Parallel preflight: {parsed['compute_node_count']} compute nodes, "
        f"hardware cores={parsed['hardware_core_counts']}",
        flush=True,
    )
    return parsed


def capture_preflight_reports(solver: Any) -> dict[str, Any]:
    """Capture rank and ownership reports in one transcript stream session."""

    transcript = getattr(solver, "transcript", None)
    if transcript is None:
        raise RuntimeError("Fluent transcript service is unavailable for preflight reports")
    buffer = io.StringIO()
    try:
        if bool(getattr(transcript, "is_streaming", False)):
            transcript.stop()
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            transcript.start(write_to_stdout=True)
            try:
                solver.settings.parallel.show_connectivity(compute_node=0)
                time.sleep(3.0)
                solver.tui.server.print_connected_grpc_clients()
                time.sleep(1.0)
            finally:
                transcript.stop()
    finally:
        try:
            transcript.stop()
        except Exception:
            pass
    raw_report = buffer.getvalue()
    parsed = parse_parallel_connectivity_roster(raw_report)
    normalized = " ".join(raw_report.casefold().split())
    if "no client is connected to server" not in normalized:
        raise RuntimeError(
            "Remote Fluent ownership is not proven exclusive; combined preflight "
            f"report was {raw_report!r}"
        )
    parsed["raw_report"] = raw_report
    print(
        f"Preflight reports: {parsed['compute_node_count']} compute nodes; "
        "ownership report says no other client is connected",
        flush=True,
    )
    return {
        "parallel": parsed,
        "connected_clients": {
            "command": "/server/print-connected-grpc-clients",
            "raw_report": raw_report,
            "exclusive": True,
        },
    }


def list_remote_directory(solver: Any, directory: str, scratch: str) -> dict[str, Any]:
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"Refusing to overwrite remote directory-listing evidence: {scratch}")
    command = f'cmd /c dir /b "{directory}" > "{scratch}" 2>&1'
    solver.scheme.eval(f'(system "{quote_scheme_string(command)}")')
    listing = remote_text_read(solver, scratch)
    names = [line.strip() for line in listing.splitlines() if line.strip()]
    return {"directory": directory, "scratch": scratch, "names": names}


def parse_transcript_residual_rows(text: str) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 8 or not parts[0].isdigit():
            continue
        try:
            values = [float(value) for value in parts[1:8]]
        except ValueError:
            continue
        rows.append({"iteration": int(parts[0]), "values": values})
    return {
        "row_count": len(rows),
        "first": rows[0] if rows else None,
        "last": rows[-1] if rows else None,
    }


def pair_autosave_names(names: list[str]) -> list[dict[str, str]]:
    cases = {name.removesuffix(".cas.h5"): name for name in names if name.endswith(".cas.h5")}
    data = {name.removesuffix(".dat.h5"): name for name in names if name.endswith(".dat.h5")}
    return [
        {"stem": stem, "case": cases[stem], "data": data[stem]}
        for stem in sorted(set(cases) & set(data))
        if stem.startswith("checkpoint-")
    ]


def target_exists(solver: Any, paths: list[str]) -> None:
    existing = [path for path in paths if remote_file_exists(solver, path)]
    if existing:
        raise FileExistsError(f"Refusing to overwrite Q01 artifact(s): {existing}")


def main() -> int:
    args = build_parser().parse_args()
    stamp = args.run_stamp
    local_root = PROJECT_ROOT / "output" / "03a_q01" / f"s4-01-50iter-{stamp}"
    local_root.mkdir(parents=True, exist_ok=False)
    tee = Tee(sys.stdout, local_root / "owner-console.log")
    original_stdout, original_stderr = sys.stdout, sys.stderr
    sys.stdout = tee
    sys.stderr = tee
    events = EventLog(local_root / "events.jsonl")
    status_path = local_root / "status.json"
    lock_path = PROJECT_ROOT / "output" / "03a_q01" / ".writer.lock"
    run_root = win(REMOTE_BRANCH_ROOT, f"run-q01-50iter-{stamp}")
    monitor_root = win(run_root, "monitors")
    prepared_case = win(run_root, f"03A-Q01-S4-01-50iter-prepared-{stamp}.cas.h5")
    endpoint_case = win(run_root, f"03A-Q01-S4-01-50iter-end-{stamp}.cas.h5")
    endpoint_data = data_path(endpoint_case)
    transcript = win(run_root, f"03A-Q01-S4-01-50iter-{stamp}.trn")
    residual_file = win(run_root, f"03A-Q01-S4-01-50iter-{stamp}-residuals.out")
    remote_journal = win(run_root, f"03A-Q01-S4-01-50iter-{stamp}.jou")
    manifest: dict[str, Any] = {
        "kind": "03a_q01_s4_01_50_iteration_manifest",
        "schema_version": 1,
        "run_stamp": stamp,
        "experiment_id": EXPERIMENT_ID,
        "stage_parent": "S4-01",
        "status": "preflight",
        "pid": os.getpid(),
        "requested_iterations": ITERATIONS,
        "remote_run_root": run_root,
        "parent_case": REMOTE_PARENT_CASE,
        "parent_data": REMOTE_PARENT_DATA,
        "parent_cumulative_iteration_from_native_history": PARENT_CUMULATIVE_ITERATION,
        "intentional_scientific_delta": "none",
        "fluent_native_run_owner": True,
        "experiments": [],
    }
    write_status(status_path, manifest)
    try:
        with exclusive_writer_lock(lock_path):
            solver = connect(server_id=args.server_id, start_transcript=False)
            version = str(solver.get_fluent_version())
            if EXPECTED_VERSION not in version:
                raise RuntimeError(f"Expected Fluent {EXPECTED_VERSION}, got {version!r}")
            preflight_reports = capture_preflight_reports(solver)
            clients = preflight_reports["connected_clients"]
            roster = preflight_reports["parallel"]
            if int(roster["compute_node_count"]) != EXPECTED_RANKS:
                raise RuntimeError(
                    f"Q01 requires {EXPECTED_RANKS} compute ranks; got {roster['compute_node_count']}"
                )
            idle_before = prove_quiescent(solver)
            ensure_remote_directory(solver, run_root)
            ensure_remote_directory(solver, monitor_root)
            target_exists(
                solver,
                [prepared_case, endpoint_case, endpoint_data, transcript, residual_file, remote_journal],
            )
            if not remote_file_exists(solver, REMOTE_PARENT_CASE):
                raise FileNotFoundError(f"Missing Q01 parent case: {REMOTE_PARENT_CASE}")
            if not remote_file_exists(solver, REMOTE_PARENT_DATA):
                raise FileNotFoundError(f"Missing Q01 parent data: {REMOTE_PARENT_DATA}")
            parent_case_sha = remote_file_sha256(
                solver,
                REMOTE_PARENT_CASE,
                win(run_root, f"q01-parent-case-sha256-{stamp}.txt"),
            )
            parent_data_sha = remote_file_sha256(
                solver,
                REMOTE_PARENT_DATA,
                win(run_root, f"q01-parent-data-sha256-{stamp}.txt"),
            )
            if parent_case_sha != EXPECTED_PARENT_CASE_SHA256:
                raise RuntimeError(
                    f"Q01 parent case SHA-256 mismatch: {parent_case_sha} != {EXPECTED_PARENT_CASE_SHA256}"
                )
            if parent_data_sha != EXPECTED_PARENT_DATA_SHA256:
                raise RuntimeError(
                    f"Q01 parent data SHA-256 mismatch: {parent_data_sha} != {EXPECTED_PARENT_DATA_SHA256}"
                )
            manifest.update(
                {
                    "fluent_version": version,
                    "compute_node_count": roster["compute_node_count"],
                    "compute_node_ids": roster["compute_node_ids"],
                    "hardware_core_counts": roster["hardware_core_counts"],
                    "connected_clients": clients,
                    "quiescence_before_parent_load": idle_before,
                    "parent_case_sha256": parent_case_sha,
                    "parent_data_sha256": parent_data_sha,
                    "status": "parent_verified",
                }
            )
            events.emit(
                "preflight_passed",
                fluent_version=version,
                compute_node_count=roster["compute_node_count"],
                requested_iterations=ITERATIONS,
            )

            print("Loading the exact S4-01 case/data parent", flush=True)
            solver.settings.file.read_case(file_name=REMOTE_PARENT_CASE)
            solver.settings.file.read_data(file_name=REMOTE_PARENT_DATA)
            parent_clock = rp_clock(solver)
            parent_readback = scientific_readback(solver)
            parent_summary = verify_parent_state(parent_readback, expected_turbulence="rng")
            manifest.update(
                {
                    "parent_clock_after_explicit_load": parent_clock,
                    "parent_summary": parent_summary,
                    "parent_readback": parent_readback,
                }
            )
            events.emit("parent_loaded_and_read_back", parent_clock=parent_clock)

            monitor_files = redirect_report_files(solver, monitor_root)
            residual_state = configure_residual_history(solver, ITERATIONS + 1000)
            autosave_state = configure_autosave(
                solver,
                run_root,
                data_frequency=ITERATIONS,
            )
            solver.settings.file.write_case(file_name=prepared_case)
            if not remote_file_exists(solver, prepared_case):
                raise RuntimeError(f"Prepared case was not written: {prepared_case}")
            prepared_case_sha = remote_file_sha256(
                solver,
                prepared_case,
                win(run_root, f"q01-prepared-case-sha256-{stamp}.txt"),
            )

            solver.settings.file.read_case(file_name=prepared_case)
            solver.settings.file.read_data(file_name=REMOTE_PARENT_DATA)
            reload_readback = scientific_readback(solver)
            reload_summary = verify_parent_state(reload_readback, expected_turbulence="rng")
            assert_controlled_scientific_delta(
                parent_readback,
                reload_readback,
                turbulence_variant="rng",
            )
            reload_reports = solver.settings.solution.monitor.report_files
            reload_monitor_files: dict[str, str] = {}
            for name in monitor_files:
                state = reload_reports[name].get_state()
                actual_path = state.get("file_name") if isinstance(state, Mapping) else None
                if not isinstance(actual_path, str):
                    raise RuntimeError(f"Prepared-case report path missing after reload: {name}")
                verify_report_file_location(
                    actual_path,
                    monitor_root=monitor_root,
                    report_name=name,
                    allow_relative=True,
                )
                reload_monitor_files[name] = actual_path
            reload_autosave = solver.settings.file.auto_save.get_state()
            if reload_autosave.get("root_name") != autosave_state.get("root_name"):
                raise RuntimeError(
                    f"Prepared-case autosave root mismatch: {reload_autosave!r}"
                )
            idle_before_run = prove_quiescent(solver)
            item = {
                "experiment_id": EXPERIMENT_ID,
                "parent_branch": "S4-01",
                "parent_case": REMOTE_PARENT_CASE,
                "parent_data": REMOTE_PARENT_DATA,
                "parent_case_sha256": parent_case_sha,
                "parent_data_sha256": parent_data_sha,
                "parent_iteration": PARENT_CUMULATIVE_ITERATION,
                "objective": (
                    "Qualify the exact S4-01 endpoint with a bounded 50-iteration "
                    "unchanged continuation; no scientific setup delta."
                ),
                "intentional_delta": "none",
                "prepared_case": prepared_case,
                "prepared_case_sha256": prepared_case_sha,
                "endpoint_case": endpoint_case,
                "endpoint_data": endpoint_data,
                "transcript": transcript,
                "residual_file": residual_file,
                "monitor_root": monitor_root,
                "monitor_files": monitor_files,
                "monitor_files_case_reload": reload_monitor_files,
                "autosave": autosave_state,
                "residual_monitor": residual_state,
                "parent_clock_after_load": parent_clock,
                "parent_summary": parent_summary,
                "prepared_case_reload_summary": reload_summary,
                "prepared_case_reload_readback": reload_readback,
                "quiescence_before_native_run": idle_before_run,
            }
            manifest["experiments"] = [item]
            manifest["status"] = "prepared"
            journal = render_native_queue([item], ITERATIONS)
            local_journal = local_root / f"03A-Q01-S4-01-50iter-{stamp}.jou"
            local_journal.write_text(journal, encoding="utf-8", newline="\n")
            write_remote_text_new(solver, remote_journal, journal)
            manifest["native_journal"] = {
                "local": str(local_journal),
                "remote": remote_journal,
            }
            write_new_json(local_root / "prepared-manifest.json", manifest)
            write_status(status_path, manifest)
            events.emit("native_journal_prepared", remote_journal=remote_journal)

            submitted = {
                **manifest,
                "status": "submitted",
                "submitted_epoch": time.time(),
            }
            write_new_json(local_root / "submitted-manifest.json", submitted)
            write_status(status_path, submitted)
            events.emit(
                "native_run_submitted",
                experiment_id=EXPERIMENT_ID,
                iterations=ITERATIONS,
                remote_journal=remote_journal,
            )

            journal_error: str | None = None
            try:
                solver.settings.file.read_journal(file_name_list=[remote_journal])
            except Exception as exc:
                journal_error = f"{type(exc).__name__}: {exc}"
                events.emit(
                    "native_run_client_error",
                    error=journal_error,
                    no_replay=True,
                    note=(
                        "Endpoint-pair reconciliation is authoritative; this owner will not "
                        "replay the journal after an uncertain return."
                    ),
                )

            completion = {
                "endpoint_case_exists": remote_file_exists(solver, endpoint_case),
                "endpoint_data_exists": remote_file_exists(solver, endpoint_data),
                "transcript_exists": remote_file_exists(solver, transcript),
                "residual_file_exists": remote_file_exists(solver, residual_file),
            }
            completion["endpoint_pair_complete"] = bool(
                completion["endpoint_case_exists"] and completion["endpoint_data_exists"]
            )
            directory_listing = list_remote_directory(
                solver,
                run_root,
                win(run_root, f"q01-directory-listing-{stamp}.txt"),
            )
            autosave_pairs = pair_autosave_names(directory_listing["names"])
            completion["native_autosave_pairs"] = autosave_pairs

            endpoint_verification: dict[str, Any] | None = None
            endpoint_hashes: dict[str, str] | None = None
            transcript_residuals: dict[str, Any] | None = None
            if completion["endpoint_pair_complete"]:
                endpoint_hashes = {
                    "case": remote_file_sha256(
                        solver,
                        endpoint_case,
                        win(run_root, f"q01-endpoint-case-sha256-{stamp}.txt"),
                    ),
                    "data": remote_file_sha256(
                        solver,
                        endpoint_data,
                        win(run_root, f"q01-endpoint-data-sha256-{stamp}.txt"),
                    ),
                }
                transcript_text = remote_text_read(solver, transcript)
                transcript_residuals = parse_transcript_residual_rows(transcript_text)
                solver.settings.file.read_case(file_name=endpoint_case)
                solver.settings.file.read_data(file_name=endpoint_data)
                endpoint_clock = rp_clock(solver)
                endpoint_readback = scientific_readback(solver)
                endpoint_summary = verify_parent_state(
                    endpoint_readback,
                    expected_turbulence="rng",
                )
                assert_controlled_scientific_delta(
                    parent_readback,
                    endpoint_readback,
                    turbulence_variant="rng",
                )
                endpoint_quiescence = prove_quiescent(solver)
                endpoint_verification = {
                    "clock_after_endpoint_reload": endpoint_clock,
                    "summary": endpoint_summary,
                    "readback": endpoint_readback,
                    "quiescence_after_endpoint_reload": endpoint_quiescence,
                }

            if completion["endpoint_pair_complete"]:
                final_status = (
                    "completed_50_iteration_native_run_with_client_error"
                    if journal_error
                    else "completed_50_iteration_native_run"
                )
            else:
                final_status = "incomplete_endpoint_pair_no_replay"
            final = {
                **submitted,
                "status": final_status,
                "journal_error": journal_error,
                "completion": completion,
                "endpoint_hashes": endpoint_hashes,
                "endpoint_verification": endpoint_verification,
                "transcript_residuals": transcript_residuals,
                "reconciled_epoch": time.time(),
            }
            write_new_json(local_root / f"{final_status}.json", final)
            write_status(status_path, final)
            events.emit(
                "native_run_reconciled",
                status=final_status,
                completion=completion,
                journal_error=journal_error,
            )
            return 0 if completion["endpoint_pair_complete"] else 3
    except Exception as exc:
        failed = {
            **manifest,
            "status": "failed_before_or_during_native_run",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "no_replay": True,
        }
        write_new_json(local_root / "failure-manifest.json", failed)
        write_status(status_path, failed)
        events.emit("owner_failure", error=failed["error"], no_replay=True)
        return 2
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        tee.close()


if __name__ == "__main__":
    raise SystemExit(main())
