#!/usr/bin/env python3
"""Preserve the interrupted S4-02 field and run independent S4-03/S4-04 recovery branches.

This is a bounded recovery/submit owner, not an iteration runner.  It saves the
currently loaded S4-02 field under a forensic non-overwriting label, prepares
fresh S4-03/S4-04 cases from the exact F11 parent, and submits one Fluent-native
30,000-iteration journal per branch.  Fluent owns iteration and paired autosave.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
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
    capture_parallel_connectivity_roster,
    remote_file_exists,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    EventLog,
    Tee,
    assert_controlled_scientific_delta,
    capture_connected_clients,
    configure_autosave,
    configure_residual_history,
    data_path,
    ensure_remote_directory,
    exclusive_writer_lock,
    redirect_report_files,
    remote_file_sha256,
    scientific_readback,
    set_turbulence_variant,
    verify_parent_state,
    verify_report_file_location,
    write_new_json,
    write_remote_text_new,
    write_status,
)


EXPECTED_VERSION = "2025 R2"
EXPECTED_RANKS = 18
ITERATIONS = 30_000
REMOTE_ROOT = r"C:\Users\syok443\Documents\FluentRuns\03A-stage4"
SOURCE_RUN = "20260822T123011Z"
SOURCE_MANIFEST = (
    PROJECT_ROOT
    / "output"
    / "03a_stage4"
    / "native_queue"
    / SOURCE_RUN
    / "prepared-manifest.json"
)
SOURCE_OBSERVER_LOG = (
    PROJECT_ROOT
    / "output"
    / "03a_stage4"
    / "native_queue"
    / SOURCE_RUN
    / "observer-20260823T012500Z-attempt2"
    / "observer-console.log"
)
def wjoin(*parts: str) -> str:
    """Join absolute Windows path components without host-OS reinterpretation."""

    return str(PureWindowsPath(parts[0]).joinpath(*parts[1:]))


EXPECTED_S4_02_AUTOSAVE_ROOT = wjoin(
    REMOTE_ROOT,
    "S4-02",
    f"run-{SOURCE_RUN}",
    "checkpoint-%i",
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="2")
    result.add_argument(
        "--prior-s4-02-forensic-manifest",
        type=Path,
        help=(
            "Reference a previously completed S4-02 forensic preservation so a "
            "non-overwriting preparation retry does not misidentify the newly loaded field."
        ),
    )
    result.add_argument(
        "--run-stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    )
    return result


def source_experiments() -> dict[str, dict[str, Any]]:
    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    return {
        str(item["experiment_id"]): dict(item)
        for item in payload["experiments"]
    }


def rp_clock(solver: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in ("current-iteration", "number-of-iterations"):
        try:
            result[name] = solver.scheme.eval(f"(%rpgetvar '{name})")
        except Exception as exc:
            result[name] = {"error": f"{type(exc).__name__}: {exc}"}
    return result


def prove_idle(solver: Any) -> dict[str, Any]:
    samples = []
    for index in range(3):
        samples.append(rp_clock(solver))
        if index < 2:
            time.sleep(2.0)
    current = [sample.get("current-iteration") for sample in samples]
    if any(isinstance(value, Mapping) for value in current) or len(set(current)) != 1:
        raise RuntimeError(f"Could not prove steady solver quiescence: {samples!r}")
    solver.settings.solution.controls.equations.get_state()
    return {"samples": samples, "quiescent": True}


def stop_active_transcript(solver: Any) -> dict[str, Any]:
    try:
        solver.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
        return {"attempted": True, "result": "returned"}
    except Exception as exc:
        return {
            "attempted": True,
            "result": "no-active-transcript-or-command-error",
            "detail": f"{type(exc).__name__}: {exc}",
        }


def write_pair_new(solver: Any, case_path: str) -> None:
    dat_path = data_path(case_path)
    for path in (case_path, dat_path):
        if remote_file_exists(solver, path):
            raise FileExistsError(f"Refusing to overwrite recovery pair member: {path}")
    solver.settings.file.write_case(file_name=case_path)
    solver.settings.file.write_data(file_name=dat_path)
    if not remote_file_exists(solver, case_path) or not remote_file_exists(solver, dat_path):
        raise RuntimeError(f"Fluent did not expose a complete recovery pair: {case_path}")


def hash_pair(solver: Any, case_path: str, scratch_root: str, tag: str) -> dict[str, str]:
    dat_path = data_path(case_path)
    return {
        "case": remote_file_sha256(
            solver,
            case_path,
            wjoin(scratch_root, f"sha256-{tag}-case.txt"),
        ),
        "data": remote_file_sha256(
            solver,
            dat_path,
            wjoin(scratch_root, f"sha256-{tag}-data.txt"),
        ),
    }


def source_console_evidence() -> dict[str, Any]:
    text = SOURCE_OBSERVER_LOG.read_text(encoding="utf-8", errors="replace")
    rows = re.findall(r"^\s*(\d+)\s+([0-9.eE+-]+)(?:\s+[0-9.eE+-]+){6}", text, re.MULTILINE)
    return {
        "source": str(SOURCE_OBSERVER_LOG),
        "last_residual_iteration": int(rows[-1][0]) if rows else None,
        "last_continuity": float(rows[-1][1]) if rows else None,
        "journal_interrupt_warning": (
            "Warning: An error or interrupt occurred while reading the journal file." in text
        ),
        "named_endpoint_write_observed": bool(
            re.search(r"^Writing to .*S4-02-plus030000-end", text, re.MULTILINE)
        ),
    }


def verify_live_s4_02_identity(solver: Any) -> dict[str, Any]:
    autosave = solver.settings.file.auto_save.get_state()
    if autosave.get("root_name") != EXPECTED_S4_02_AUTOSAVE_ROOT:
        raise RuntimeError(f"Loaded field is not bound to the S4-02 autosave root: {autosave!r}")
    reports = solver.settings.solution.monitor.report_files.get_state()
    report_paths = [
        str(value.get("file_name", ""))
        for value in reports.values()
        if isinstance(value, Mapping)
    ]
    expected_fragment = rf"03A-stage4\S4-02\run-{SOURCE_RUN}\monitors".lower()
    normalized = [path.replace("\\\\", "\\").lower() for path in report_paths]
    if len(normalized) != 30 or any(expected_fragment not in path for path in normalized):
        raise RuntimeError("Live report-file roots do not prove the original S4-02 setup identity")
    readback = scientific_readback(solver)
    summary = verify_parent_state(readback, expected_turbulence="rng")
    return {
        "autosave": autosave,
        "report_file_count": len(normalized),
        "summary": summary,
        "scientific_readback": readback,
    }


def preserve_live_s4_02(
    solver: Any,
    *,
    recovery_root: str,
    stamp: str,
) -> dict[str, Any]:
    evidence = source_console_evidence()
    identity = verify_live_s4_02_identity(solver)
    clock_before = rp_clock(solver)
    transcript_close = stop_active_transcript(solver)
    branch_root = wjoin(REMOTE_ROOT, "S4-02", f"recovery-{stamp}")
    ensure_remote_directory(solver, branch_root)
    stem = f"03A-stage4-S4-02-ambiguous-live-field-forensic-{stamp}"
    case_path = wjoin(branch_root, stem + ".cas.h5")
    write_pair_new(solver, case_path)
    hashes = hash_pair(solver, case_path, recovery_root, "s4-02-forensic")
    solver.settings.file.read_case(file_name=case_path)
    solver.settings.file.read_data(file_name=data_path(case_path))
    reload_readback = scientific_readback(solver)
    reload_summary = verify_parent_state(reload_readback, expected_turbulence="rng")
    return {
        "classification": "forensic live-field preservation / diagnostic-unresolved",
        "eligible_parent": False,
        "reason": (
            "Native console proves cumulative 36000 before journal interruption, but the "
            "post-interruption RP current-iteration value is not reconciled; the saved field "
            "is intentionally not called an accepted endpoint."
        ),
        "source_console_evidence": evidence,
        "identity_before_save": identity,
        "clock_before_save": clock_before,
        "transcript_close": transcript_close,
        "case": case_path,
        "data": data_path(case_path),
        "sha256": hashes,
        "clock_after_reload": rp_clock(solver),
        "reload_summary": reload_summary,
        "reload_readback": reload_readback,
    }


def verify_source_hash(
    solver: Any,
    *,
    path: str,
    expected: str,
    scratch_root: str,
    tag: str,
) -> str:
    if not remote_file_exists(solver, path):
        raise FileNotFoundError(f"Missing authoritative source file: {path}")
    actual = remote_file_sha256(solver, path, wjoin(scratch_root, f"sha256-{tag}.txt"))
    if actual != expected:
        raise RuntimeError(f"Source SHA256 mismatch for {path}: {actual} != {expected}")
    return actual


def prepare_branch(
    solver: Any,
    *,
    source: Mapping[str, Any],
    experiment_id: str,
    turbulence: str,
    stamp: str,
    recovery_root: str,
    parent_hashes: Mapping[str, str],
) -> dict[str, Any]:
    run_root = wjoin(REMOTE_ROOT, experiment_id, f"run-recovery-{stamp}")
    monitor_root = wjoin(run_root, "monitors")
    ensure_remote_directory(solver, run_root)
    ensure_remote_directory(solver, monitor_root)
    stem = f"03A-stage4-{experiment_id}-recovery-{stamp}"
    prepared_case = wjoin(run_root, stem + "-prepared.cas.h5")
    endpoint_case = wjoin(run_root, stem + "-plus030000-end.cas.h5")
    transcript = wjoin(run_root, stem + ".trn")
    residual_file = wjoin(run_root, stem + "-residuals.out")
    final_autosave_case = wjoin(run_root, "checkpoint-45000-1-45000.cas.h5")
    targets = (
        prepared_case,
        endpoint_case,
        data_path(endpoint_case),
        transcript,
        residual_file,
        final_autosave_case,
        data_path(final_autosave_case),
    )
    for path in targets:
        if remote_file_exists(solver, path):
            raise FileExistsError(f"Refusing to overwrite branch recovery artifact: {path}")

    parent_case = str(source["parent_case"])
    parent_data = str(source["parent_data"])
    solver.settings.file.read_case(file_name=parent_case)
    solver.settings.file.read_data(file_name=parent_data)
    before = scientific_readback(solver)
    before_summary = verify_parent_state(before, expected_turbulence="rng")
    if turbulence != "rng":
        set_turbulence_variant(solver, turbulence)
    after = scientific_readback(solver)
    after_summary = verify_parent_state(after, expected_turbulence=turbulence)
    assert_controlled_scientific_delta(before, after, turbulence_variant=turbulence)
    monitor_files = redirect_report_files(solver, monitor_root)
    residual = configure_residual_history(solver, ITERATIONS + 1000)
    autosave = configure_autosave(solver, run_root)
    solver.settings.file.write_case(file_name=prepared_case)
    prepared_sha = remote_file_sha256(
        solver,
        prepared_case,
        wjoin(recovery_root, f"sha256-{experiment_id.lower()}-prepared-case.txt"),
    )

    solver.settings.file.read_case(file_name=prepared_case)
    solver.settings.file.read_data(file_name=parent_data)
    reload = scientific_readback(solver)
    reload_summary = verify_parent_state(reload, expected_turbulence=turbulence)
    reload_reports = solver.settings.solution.monitor.report_files.get_state()
    if len(reload_reports) != 30:
        raise RuntimeError(f"{experiment_id} reload exposed {len(reload_reports)} report files")
    for name, state in reload_reports.items():
        actual = str(state.get("file_name", ""))
        verify_report_file_location(
            actual,
            monitor_root=monitor_root,
            report_name=str(name),
            allow_relative=True,
        )
    reload_autosave = solver.settings.file.auto_save.get_state()
    if reload_autosave.get("root_name") != autosave.get("root_name"):
        raise RuntimeError(f"{experiment_id} autosave changed after case/data reload")
    return {
        "experiment_id": experiment_id,
        "classification": "prepared independent diagnostic continuation",
        "eligible_parent": False,
        "parent_case": parent_case,
        "parent_data": parent_data,
        "parent_case_sha256": parent_hashes["case"],
        "parent_data_sha256": parent_hashes["data"],
        "parent_iteration": int(source["parent_iteration"]),
        "turbulence_variant": turbulence,
        "prepared_case": prepared_case,
        "prepared_case_sha256": prepared_sha,
        "endpoint_case": endpoint_case,
        "endpoint_data": data_path(endpoint_case),
        "final_autosave_case": final_autosave_case,
        "final_autosave_data": data_path(final_autosave_case),
        "transcript": transcript,
        "residual_file": residual_file,
        "monitor_root": monitor_root,
        "monitor_files": monitor_files,
        "autosave": autosave,
        "residual_monitor": residual,
        "before_summary": before_summary,
        "after_summary": after_summary,
        "reload_summary": reload_summary,
        "reload_readback": reload,
    }


def render_branch_journal(item: Mapping[str, Any]) -> str:
    def posix(path: str) -> str:
        return path.replace("\\", "/")

    return "\n".join(
        (
            "/file/set-tui-version \"25.2\"",
            "/file/confirm-overwrite? no",
            f'; BEGIN {item["experiment_id"]}',
            f'(chdir "{posix(str(item["monitor_root"]))}")',
            f'/file/read-case "{posix(str(item["prepared_case"]))}"',
            f'/file/read-data "{posix(str(item["parent_data"]))}"',
            f'/file/start-transcript "{posix(str(item["transcript"]))}"',
            "/solve/monitors/residual/print? yes",
            "/solve/monitors/residual/plot? no",
            f"/solve/monitors/residual/n-save {ITERATIONS + 1000}",
            f"/solve/iterate {ITERATIONS}",
            f'/file/write-case-data "{posix(str(item["endpoint_case"]))}"',
            f'/plot/residuals-set/plot-to-file "{posix(str(item["residual_file"]))}"',
            "/plot/residuals",
            "/plot/residuals-set/end-plot-to-file",
            "/file/stop-transcript",
            f'; END {item["experiment_id"]}',
            "; Branch journal finished; Fluent remains open.",
            "",
        )
    )


def reconnect(server_id: str, *, attempts: int = 4) -> Any:
    delay = 5.0
    last: Exception | None = None
    for _ in range(attempts):
        try:
            return connect(server_id=server_id, start_transcript=True)
        except Exception as exc:
            last = exc
            time.sleep(delay)
            delay = min(delay * 2.0, 30.0)
    raise RuntimeError(f"Could not reconnect to Fluent after native journal return: {last}")


def reconcile_branch(solver: Any, item: Mapping[str, Any], recovery_root: str) -> dict[str, Any]:
    endpoint_complete = remote_file_exists(solver, str(item["endpoint_case"])) and remote_file_exists(
        solver, str(item["endpoint_data"])
    )
    autosave_complete = remote_file_exists(solver, str(item["final_autosave_case"])) and remote_file_exists(
        solver, str(item["final_autosave_data"])
    )
    if endpoint_complete:
        candidate_case = str(item["endpoint_case"])
        source = "named endpoint"
    elif autosave_complete:
        candidate_case = str(item["final_autosave_case"])
        source = "target-iteration native autosave"
    else:
        raise RuntimeError(
            f"{item['experiment_id']} has neither a complete endpoint nor its target autosave"
        )
    hashes = hash_pair(
        solver,
        candidate_case,
        recovery_root,
        f"{str(item['experiment_id']).lower()}-candidate",
    )
    solver.settings.file.read_case(file_name=candidate_case)
    solver.settings.file.read_data(file_name=data_path(candidate_case))
    readback = scientific_readback(solver)
    summary = verify_parent_state(
        readback,
        expected_turbulence=str(item["turbulence_variant"]),
    )
    return {
        "classification": "completed diagnostic / unresolved pending physical-history analysis",
        "eligible_parent": False,
        "candidate_source": source,
        "case": candidate_case,
        "data": data_path(candidate_case),
        "sha256": hashes,
        "clock_after_reload": rp_clock(solver),
        "summary": summary,
        "readback": readback,
        "named_endpoint_complete": endpoint_complete,
        "target_autosave_complete": autosave_complete,
    }


def main() -> int:
    args = parser().parse_args()
    stamp = args.run_stamp
    local_root = PROJECT_ROOT / "output" / "03a_stage4" / "native_queue_recovery" / stamp
    local_root.mkdir(parents=True, exist_ok=False)
    tee = Tee(sys.stdout, local_root / "owner-console.log")
    original_stdout, original_stderr = sys.stdout, sys.stderr
    sys.stdout = tee
    sys.stderr = tee
    events = EventLog(local_root / "events.jsonl")
    status_path = local_root / "status.json"
    lock_path = PROJECT_ROOT / "output" / "03a_stage4" / ".writer.lock"
    manifest: dict[str, Any] = {
        "kind": "03a_stage4_native_recovery_manifest",
        "schema_version": 1,
        "run_stamp": stamp,
        "queue_label": f"03A-stage4-S4-02-forensic-S4-03-S4-04-recovery-{stamp}",
        "status": "preflight",
        "pid": os.getpid(),
        "credentials_persisted": False,
        "source_manifest": str(SOURCE_MANIFEST),
        "branches": [],
    }
    write_status(status_path, manifest)
    try:
        with exclusive_writer_lock(lock_path):
            solver = connect(server_id=args.server_id, start_transcript=True)
            version = str(solver.get_fluent_version())
            if EXPECTED_VERSION not in version:
                raise RuntimeError(f"Expected Fluent {EXPECTED_VERSION}, got {version!r}")
            clients = capture_connected_clients(solver)
            if not clients["exclusive"]:
                raise RuntimeError(f"Another Fluent client is connected: {clients['raw_report']!r}")
            roster = capture_parallel_connectivity_roster(solver)
            if roster["compute_node_count"] != EXPECTED_RANKS:
                raise RuntimeError(f"Expected {EXPECTED_RANKS} ranks, got {roster['compute_node_count']}")
            idle = prove_idle(solver)
            recovery_root = wjoin(REMOTE_ROOT, f"recovery-{stamp}")
            ensure_remote_directory(solver, recovery_root)
            manifest.update(
                {
                    "status": "preserving_s4_02",
                    "fluent_version": version,
                    "compute_node_count": roster["compute_node_count"],
                    "compute_node_ids": roster["compute_node_ids"],
                    "connected_clients": clients,
                    "quiescence": idle,
                    "remote_recovery_root": recovery_root,
                }
            )
            write_status(status_path, manifest)
            events.emit("preflight_passed", version=version, ranks=EXPECTED_RANKS)

            if args.prior_s4_02_forensic_manifest:
                prior_path = args.prior_s4_02_forensic_manifest.expanduser().resolve()
                s4_02 = json.loads(prior_path.read_text(encoding="utf-8"))
                if not s4_02.get("case") or not s4_02.get("data") or not s4_02.get("sha256"):
                    raise RuntimeError(f"Prior S4-02 forensic manifest is incomplete: {prior_path}")
                prior_hashes = hash_pair(
                    solver,
                    str(s4_02["case"]),
                    recovery_root,
                    "prior-s4-02-forensic",
                )
                if prior_hashes != s4_02["sha256"]:
                    raise RuntimeError(
                        f"Prior S4-02 forensic hashes changed: {prior_hashes!r} != {s4_02['sha256']!r}"
                    )
                s4_02 = {
                    **s4_02,
                    "referenced_from_prior_attempt": str(prior_path),
                    "reverified_sha256": prior_hashes,
                }
            else:
                s4_02 = preserve_live_s4_02(
                    solver,
                    recovery_root=recovery_root,
                    stamp=stamp,
                )
            manifest["s4_02_forensic"] = s4_02
            write_new_json(local_root / "s4-02-forensic-manifest.json", s4_02)
            write_status(status_path, {**manifest, "status": "preparing_remaining"})
            events.emit(
                "s4_02_forensic_preserved",
                case=s4_02["case"],
                data=s4_02["data"],
                classification=s4_02["classification"],
            )

            sources = source_experiments()
            s4_03_source = sources["S4-03"]
            s4_04_source = sources["S4-04"]
            if s4_03_source["parent_case"] != s4_04_source["parent_case"] or s4_03_source[
                "parent_data"
            ] != s4_04_source["parent_data"]:
                raise RuntimeError("S4-03 and S4-04 no longer share the exact F11 parent")
            parent_hashes = {
                "case": verify_source_hash(
                    solver,
                    path=str(s4_03_source["parent_case"]),
                    expected=str(s4_03_source["parent_case_sha256"]),
                    scratch_root=recovery_root,
                    tag="f11-parent-case",
                ),
                "data": verify_source_hash(
                    solver,
                    path=str(s4_03_source["parent_data"]),
                    expected=str(s4_03_source["parent_data_sha256"]),
                    scratch_root=recovery_root,
                    tag="f11-parent-data",
                ),
            }
            branches = [
                prepare_branch(
                    solver,
                    source=s4_03_source,
                    experiment_id="S4-03",
                    turbulence="rng",
                    stamp=stamp,
                    recovery_root=recovery_root,
                    parent_hashes=parent_hashes,
                ),
                prepare_branch(
                    solver,
                    source=s4_04_source,
                    experiment_id="S4-04",
                    turbulence="standard",
                    stamp=stamp,
                    recovery_root=recovery_root,
                    parent_hashes=parent_hashes,
                ),
            ]
            manifest["branches"] = branches
            manifest["status"] = "prepared"
            write_new_json(local_root / "prepared-manifest.json", manifest)
            write_status(status_path, manifest)
            events.emit("remaining_branches_prepared", branches=["S4-03", "S4-04"])

            for item in branches:
                branch_id = str(item["experiment_id"])
                journal = render_branch_journal(item)
                local_journal = local_root / f"{branch_id.lower()}-{stamp}.jou"
                local_journal.write_text(journal, encoding="utf-8", newline="\n")
                remote_journal = wjoin(recovery_root, f"{branch_id.lower()}-{stamp}.jou")
                write_remote_text_new(solver, remote_journal, journal)
                item["local_journal"] = str(local_journal)
                item["remote_journal"] = remote_journal
                submission = {
                    "experiment_id": branch_id,
                    "submitted_epoch": time.time(),
                    "remote_journal": remote_journal,
                    "iterations": ITERATIONS,
                    "endpoint_case": item["endpoint_case"],
                    "endpoint_data": item["endpoint_data"],
                    "target_autosave_case": item["final_autosave_case"],
                    "target_autosave_data": item["final_autosave_data"],
                    "no_automatic_replay": True,
                }
                write_new_json(local_root / f"{branch_id.lower()}-submitted.json", submission)
                write_status(
                    status_path,
                    {**manifest, "status": f"{branch_id.lower()}_submitted", "active": submission},
                )
                events.emit("native_branch_submitted", **submission)
                stop_active_transcript(solver)
                native_error: str | None = None
                try:
                    solver.settings.file.read_journal(file_name_list=[remote_journal])
                except Exception as exc:
                    native_error = f"{type(exc).__name__}: {exc}"
                    events.emit(
                        "native_branch_client_or_journal_error",
                        experiment_id=branch_id,
                        error=native_error,
                        no_replay=True,
                    )
                    solver = reconnect(str(args.server_id))
                    if not prove_idle(solver)["quiescent"]:
                        raise RuntimeError(f"{branch_id} did not become quiescent after journal return")
                reconciliation = reconcile_branch(solver, item, recovery_root)
                reconciliation["native_error"] = native_error
                item["reconciliation"] = reconciliation
                write_new_json(local_root / f"{branch_id.lower()}-reconciled.json", reconciliation)
                write_status(
                    status_path,
                    {**manifest, "status": f"{branch_id.lower()}_reconciled", "active": None},
                )
                events.emit(
                    "native_branch_reconciled",
                    experiment_id=branch_id,
                    source=reconciliation["candidate_source"],
                    case=reconciliation["case"],
                    classification=reconciliation["classification"],
                )

            manifest["status"] = "complete_diagnostic_unresolved"
            write_new_json(local_root / "complete-manifest.json", manifest)
            write_status(status_path, manifest)
            events.emit("recovery_queue_complete", branches=["S4-03", "S4-04"])
            return 0
    except Exception as exc:
        failed = {
            **manifest,
            "status": "stopped_or_failed_unresolved",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }
        write_new_json(local_root / "failure-manifest.json", failed)
        write_status(status_path, failed)
        events.emit("recovery_owner_failure", error=failed["error"])
        return 2
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        tee.close()


if __name__ == "__main__":
    raise SystemExit(main())
