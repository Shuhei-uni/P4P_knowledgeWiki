#!/usr/bin/env python3
"""Prepare and submit the 03A Stage-4 S4-01 through S4-04 native queue.

Python owns only bounded preflight, cold-load/readback, monitor redirection,
case-only preparation, and one journal submission.  Fluent owns all four
30,000-iteration calculations and their checkpoints.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PureWindowsPath
import sys
import traceback
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import (  # noqa: E402
    capture_parallel_connectivity_roster,
    remote_file_exists,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.native_run_monitor import collect_snapshot  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    EventLog,
    Stage4Experiment,
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
    remote_free_bytes,
    render_native_queue,
    scientific_readback,
    set_turbulence_variant,
    verify_parent_state,
    verify_report_file_location,
    win,
    write_new_json,
    write_remote_text_new,
    write_status,
)


REMOTE_ROOT = r"C:\Users\syok443\Documents\FluentRuns\03A-stage4"
ITERATIONS = 30_000
EXPECTED_RANKS = 18
MIN_FREE_BYTES = 8_000_000_000
EXPERIMENTS = (
    Stage4Experiment(
        "S4-01",
        "F05",
        r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F05\run-20260820T013223Z\03A-stage3-F05-full-mixture-100pct-end-20260820T013223Z.cas.h5",
        r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F05\run-20260820T013223Z\03A-stage3-F05-full-mixture-100pct-end-20260820T013223Z.dat.h5",
        3000,
        "rng",
        "Test whether the F05 full-load state becomes stationary under unchanged continuation.",
    ),
    Stage4Experiment(
        "S4-02",
        "F06",
        r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F06\run-20260820T013223Z\03A-stage3-F06-full-mixture-100pct-end-20260820T013223Z.cas.h5",
        r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F06\run-20260820T013223Z\03A-stage3-F06-full-mixture-100pct-end-20260820T013223Z.dat.h5",
        6000,
        "rng",
        "Test whether carrier-first startup history matters after a long unchanged continuation.",
    ),
    Stage4Experiment(
        "S4-03",
        "F11",
        r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F11\run-20260820T013223Z\03A-stage3-F11-full-mixture-100pct-end-20260820T013223Z.cas.h5",
        r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F11\run-20260820T013223Z\03A-stage3-F11-full-mixture-100pct-end-20260820T013223Z.dat.h5",
        15000,
        "rng",
        "Test whether F11 preserves mass behaviour and bounds turbulence residuals unchanged.",
    ),
    Stage4Experiment(
        "S4-04",
        "F11",
        r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F11\run-20260820T013223Z\03A-stage3-F11-full-mixture-100pct-end-20260820T013223Z.cas.h5",
        r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F11\run-20260820T013223Z\03A-stage3-F11-full-mixture-100pct-end-20260820T013223Z.dat.h5",
        15000,
        "standard",
        "Test standard k-epsilon as the sole model-form delta from the F11 endpoint.",
    ),
)


def require_quiescent(solver: Any) -> dict[str, Any]:
    first = collect_snapshot(solver, monitor_sets=("residual",))
    import time

    time.sleep(4.0)
    second = collect_snapshot(solver, previous_state=first, monitor_sets=("residual",))
    first_iteration = first.get("progress", {}).get("iteration")
    second_iteration = second.get("progress", {}).get("iteration")
    first_flow = first.get("runtime", {}).get("flow_time")
    second_flow = second.get("runtime", {}).get("flow_time")
    comparable = False
    if first_iteration is not None and second_iteration is not None:
        comparable = True
        if second_iteration != first_iteration:
            raise RuntimeError(f"Fluent iteration advanced during ownership preflight: {first_iteration} -> {second_iteration}")
    if first_flow is not None and second_flow is not None:
        comparable = True
        if second_flow != first_flow:
            raise RuntimeError(f"Fluent flow time advanced during ownership preflight: {first_flow} -> {second_flow}")
    if not comparable:
        raise RuntimeError("Fluent ownership preflight exposed no comparable progress clock")
    return {"first": first, "second": second, "observed_quiescent": True}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", required=True)
    parser.add_argument(
        "--run-stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    )
    parser.add_argument("--prepare-only", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    local_root = PROJECT_ROOT / "output" / "03a_stage4" / "native_queue" / args.run_stamp
    local_root.mkdir(parents=True, exist_ok=False)
    tee = Tee(sys.stdout, local_root / "owner-console.log")
    original_stdout, original_stderr = sys.stdout, sys.stderr
    sys.stdout = tee
    sys.stderr = tee
    events = EventLog(local_root / "events.jsonl")
    status_path = local_root / "status.json"
    lock_path = PROJECT_ROOT / "output" / "03a_stage4" / ".writer.lock"
    manifest: dict[str, Any] = {
        "kind": "03a_stage4_native_queue_manifest",
        "schema_version": 1,
        "run_stamp": args.run_stamp,
        "queue_label": f"03A-stage4-S4-01-through-S4-04-native-{args.run_stamp}",
        "iterations_per_experiment": ITERATIONS,
        "status": "preflight",
        "pid": os.getpid(),
        "experiments": [],
        "credentials_persisted": False,
    }
    write_status(status_path, manifest)
    try:
        with exclusive_writer_lock(lock_path):
            solver = connect(server_id=args.server_id, start_transcript=True)
            version = str(solver.get_fluent_version())
            if "2025 R2" not in version:
                raise RuntimeError(f"Expected Fluent 2025 R2, got {version!r}")
            clients = capture_connected_clients(solver)
            if not clients["exclusive"]:
                raise RuntimeError(f"Remote Fluent ownership is not exclusive: {clients['raw_report']!r}")
            roster = capture_parallel_connectivity_roster(solver)
            if int(roster["compute_node_count"]) != EXPECTED_RANKS:
                raise RuntimeError(
                    f"Stage-4 comparison requires {EXPECTED_RANKS} ranks; got {roster['compute_node_count']}"
                )
            idle = require_quiescent(solver)
            ensure_remote_directory(solver, REMOTE_ROOT)
            disk_scratch = win(REMOTE_ROOT, f"disk-free-{args.run_stamp}.txt")
            free_bytes = remote_free_bytes(solver, disk_scratch)
            if free_bytes < MIN_FREE_BYTES:
                raise RuntimeError(f"Insufficient remote free disk: {free_bytes} bytes")
            manifest.update(
                {
                    "fluent_version": version,
                    "compute_node_count": roster["compute_node_count"],
                    "compute_node_ids": roster["compute_node_ids"],
                    "hardware_core_counts": roster["hardware_core_counts"],
                    "connected_client_report": clients,
                    "ownership_preflight": idle,
                    "remote_free_bytes": free_bytes,
                }
            )
            events.emit(
                "preflight_passed",
                fluent_version=version,
                compute_node_count=roster["compute_node_count"],
                remote_free_bytes=free_bytes,
            )

            parent_hashes: dict[str, str] = {}
            for experiment in EXPERIMENTS:
                for member, path in (("case", experiment.parent_case), ("data", experiment.parent_data)):
                    if not remote_file_exists(solver, path):
                        raise FileNotFoundError(f"Missing {experiment.experiment_id} parent {member}: {path}")
                    if path not in parent_hashes:
                        scratch = win(
                            REMOTE_ROOT,
                            f"hash-{experiment.parent_branch}-{member}-{args.run_stamp}.txt",
                        )
                        parent_hashes[path] = remote_file_sha256(solver, path, scratch)

            prepared: list[dict[str, Any]] = []
            for experiment in EXPERIMENTS:
                branch_root = win(REMOTE_ROOT, experiment.experiment_id)
                run_root = win(branch_root, f"run-{args.run_stamp}")
                monitor_root = win(run_root, "monitors")
                ensure_remote_directory(solver, branch_root)
                ensure_remote_directory(solver, run_root)
                prepared_case = win(
                    run_root,
                    f"03A-stage4-{experiment.experiment_id}-prepared-{args.run_stamp}.cas.h5",
                )
                endpoint_case = win(
                    run_root,
                    f"03A-stage4-{experiment.experiment_id}-plus030000-end-{args.run_stamp}.cas.h5",
                )
                transcript = win(run_root, f"03A-stage4-{experiment.experiment_id}-{args.run_stamp}.trn")
                residual_file = win(
                    run_root,
                    f"03A-stage4-{experiment.experiment_id}-{args.run_stamp}-residuals.out",
                )
                for path in (
                    prepared_case,
                    endpoint_case,
                    data_path(endpoint_case),
                    transcript,
                    residual_file,
                ):
                    if remote_file_exists(solver, path):
                        raise FileExistsError(f"Refusing to overwrite Stage-4 artifact: {path}")

                events.emit(
                    "parent_load_start",
                    experiment_id=experiment.experiment_id,
                    parent_branch=experiment.parent_branch,
                )
                solver.settings.file.read_case_data(file_name=experiment.parent_case)
                snapshot = collect_snapshot(solver, monitor_sets=("residual",))
                observed_iteration = snapshot.get("progress", {}).get("iteration")
                if observed_iteration is not None and int(observed_iteration) != experiment.parent_iteration:
                    raise RuntimeError(
                        f"{experiment.experiment_id} parent iteration mismatch: "
                        f"observed={observed_iteration!r} expected={experiment.parent_iteration}"
                    )
                clock_evidence = {
                    "expected_parent_iteration_from_stage3_endpoint_record": experiment.parent_iteration,
                    "live_monitor_iteration": observed_iteration,
                    "classification": (
                        "live-matched"
                        if observed_iteration is not None
                        else "live-monitor-unavailable; exact path and SHA-bound endpoint record used"
                    ),
                }
                before = scientific_readback(solver)
                before_summary = verify_parent_state(before, expected_turbulence="rng")
                if experiment.turbulence_variant != "rng":
                    set_turbulence_variant(solver, experiment.turbulence_variant)
                after = scientific_readback(solver)
                after_summary = verify_parent_state(
                    after,
                    expected_turbulence=experiment.turbulence_variant,
                )
                assert_controlled_scientific_delta(
                    before,
                    after,
                    turbulence_variant=experiment.turbulence_variant,
                )
                monitor_files = redirect_report_files(solver, monitor_root)
                residual_state = configure_residual_history(solver, ITERATIONS + 1000)
                autosave = configure_autosave(solver, run_root)
                solver.settings.file.write_case(file_name=prepared_case)
                if not remote_file_exists(solver, prepared_case):
                    raise RuntimeError(f"Prepared case is missing after write: {prepared_case}")
                prepared_hash_scratch = win(
                    run_root,
                    f"prepared-case-hash-{args.run_stamp}.txt",
                )
                prepared_hash = remote_file_sha256(
                    solver,
                    prepared_case,
                    prepared_hash_scratch,
                )
                solver.settings.file.read_case(file_name=prepared_case)
                reload_readback = scientific_readback(solver)
                reload_summary = verify_parent_state(
                    reload_readback,
                    expected_turbulence=experiment.turbulence_variant,
                )
                reload_reports = solver.settings.solution.monitor.report_files
                reload_monitor_files: dict[str, str] = {}
                for name in monitor_files:
                    report_state = reload_reports[name].get_state()
                    actual_path = report_state.get("file_name")
                    if not isinstance(actual_path, str):
                        raise RuntimeError(f"Prepared-case report path missing for {name}")
                    verify_report_file_location(
                        actual_path,
                        monitor_root=monitor_root,
                        report_name=name,
                        allow_relative=True,
                    )
                    reload_monitor_files[name] = actual_path
                reload_autosave = solver.settings.file.auto_save.get_state()
                if reload_autosave.get("root_name") != autosave.get("root_name"):
                    raise RuntimeError(
                        f"Prepared-case autosave root mismatch: {reload_autosave!r}"
                    )
                item = {
                    "experiment_id": experiment.experiment_id,
                    "parent_branch": experiment.parent_branch,
                    "parent_case": experiment.parent_case,
                    "parent_data": experiment.parent_data,
                    "parent_case_sha256": parent_hashes[experiment.parent_case],
                    "parent_data_sha256": parent_hashes[experiment.parent_data],
                    "parent_iteration": experiment.parent_iteration,
                    "objective": experiment.objective,
                    "intentional_delta": (
                        "none"
                        if experiment.turbulence_variant == "rng"
                        else "RNG to standard k-epsilon only"
                    ),
                    "prepared_case": prepared_case,
                    "prepared_case_sha256": prepared_hash,
                    "parent_data_reused_by_native_journal": True,
                    "endpoint_case": endpoint_case,
                    "endpoint_data": data_path(endpoint_case),
                    "transcript": transcript,
                    "residual_file": residual_file,
                    "monitor_files": monitor_files,
                    "monitor_files_case_reload": reload_monitor_files,
                    "monitor_root": monitor_root,
                    "autosave": autosave,
                    "residual_monitor": residual_state,
                    "parent_snapshot": snapshot,
                    "parent_clock_evidence": clock_evidence,
                    "readback_before_summary": before_summary,
                    "readback_after_summary": after_summary,
                    "scientific_readback_before": before,
                    "scientific_readback_after": after,
                    "prepared_case_reload_summary": reload_summary,
                    "prepared_case_reload_readback": reload_readback,
                }
                prepared.append(item)
                manifest["experiments"] = prepared
                write_status(status_path, {**manifest, "status": "preparing"})
                events.emit(
                    "experiment_prepared",
                    experiment_id=experiment.experiment_id,
                    prepared_case=prepared_case,
                    prepared_case_sha256=prepared_hash,
                    monitor_file_count=len(monitor_files),
                    intentional_delta=item["intentional_delta"],
                )

            journal = render_native_queue(prepared, ITERATIONS)
            local_journal = local_root / f"03A-stage4-S4-01-through-S4-04-{args.run_stamp}.jou"
            local_journal.write_text(journal, encoding="utf-8", newline="\n")
            remote_journal = win(
                REMOTE_ROOT,
                f"03A-stage4-S4-01-through-S4-04-{args.run_stamp}.jou",
            )
            write_remote_text_new(solver, remote_journal, journal)
            manifest["native_journal"] = {
                "local": str(local_journal),
                "remote": remote_journal,
            }
            manifest["status"] = "prepared"
            write_new_json(local_root / "prepared-manifest.json", manifest)
            write_status(status_path, manifest)
            events.emit("queue_prepared", remote_journal=remote_journal)
            if args.prepare_only:
                events.emit("prepare_only_complete")
                return 0

            submitted = {**manifest, "status": "submitted", "submitted_epoch": __import__("time").time()}
            write_new_json(local_root / "submitted-manifest.json", submitted)
            write_status(status_path, submitted)
            events.emit(
                "native_queue_submitted",
                queue=[experiment.experiment_id for experiment in EXPERIMENTS],
                iterations_per_experiment=ITERATIONS,
                remote_journal=remote_journal,
            )
            client_error: str | None = None
            try:
                solver.settings.file.read_journal(file_name_list=[remote_journal])
            except Exception as exc:
                client_error = f"{type(exc).__name__}: {exc}"
                events.emit(
                    "native_queue_client_error",
                    error=client_error,
                    no_repeat=True,
                    note="Journal outcome must be reconciled from named endpoint pairs; no solve is replayed.",
                )

            completion: list[dict[str, Any]] = []
            for item in prepared:
                case_exists = remote_file_exists(solver, item["endpoint_case"])
                data_exists = remote_file_exists(solver, item["endpoint_data"])
                completion.append(
                    {
                        "experiment_id": item["experiment_id"],
                        "case_exists": case_exists,
                        "data_exists": data_exists,
                        "complete_pair": case_exists and data_exists,
                    }
                )
            all_complete = all(item["complete_pair"] for item in completion)
            final_status = "complete" if all_complete else "stopped_or_unresolved"
            final = {
                **manifest,
                "status": final_status,
                "client_error": client_error,
                "completion": completion,
            }
            write_new_json(local_root / f"{final_status}-manifest.json", final)
            write_status(status_path, final)
            events.emit("queue_reconciled", status=final_status, completion=completion)
            return 0 if all_complete else 3
    except Exception as exc:
        failed = {
            **manifest,
            "status": "failed_before_or_during_submission",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }
        write_new_json(local_root / "failure-manifest.json", failed)
        write_status(status_path, failed)
        events.emit("owner_failure", error=failed["error"])
        return 2
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        tee.close()


if __name__ == "__main__":
    raise SystemExit(main())
