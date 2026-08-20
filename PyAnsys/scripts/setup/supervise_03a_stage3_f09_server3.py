#!/usr/bin/env python3
"""Supervise the independent F09 Stage-3 branch in native 250-step chunks."""

from __future__ import annotations

from datetime import datetime, timezone
import math
from pathlib import Path
import sys
import time
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from pyansys_fluent.dpm_reports import execute_tui  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.native_run_monitor import collect_snapshot  # noqa: E402
from run_03a_stage3_user_override_server3 import (  # noqa: E402
    EventLog,
    INLET_PHASES,
    INLET_ZONES,
    VELOCITIES,
    branch_root,
    connect_with_transport_backoff,
    data_path,
    nested_value,
    prepare_new_branch,
    readback,
    reconnect,
    set_stage_controls,
    snapshot_summary,
    stop_active_transcript,
    transition,
    velocity_values,
    verify_stage_state,
    win,
    write_pair,
)


SERVER_ID = "3"
CHUNK_SIZE = 250
STAGES = (
    ("10pct", VELOCITIES["10pct"], 3000),
    ("20pct", VELOCITIES["20pct"], 6000),
    ("40pct", VELOCITIES["40pct"], 9000),
    ("80pct", VELOCITIES["80pct"], 12000),
    ("100pct", VELOCITIES["100pct"], 15000),
)
NUMERICAL_MARKERS = (
    "floating-point",
    "floating point",
    "fpe",
    "divergence detected in amg solver",
    "non-finite",
    "nonfinite",
    "solver termination",
    "error at host",
)


def finite_residuals(summary: dict[str, Any]) -> tuple[bool, list[str]]:
    residuals = summary.get("residuals")
    if not isinstance(residuals, dict) or not residuals:
        return True, []
    bad: list[str] = []
    for key, value in residuals.items():
        try:
            if not math.isfinite(float(value)):
                bad.append(str(key))
        except (TypeError, ValueError):
            bad.append(str(key))
    return not bad, bad


def current_iteration(solver: Any) -> int | None:
    try:
        snapshot = collect_snapshot(solver, monitor_sets=("residual",))
        value = snapshot.get("progress", {}).get("iteration")
        return int(value) if value is not None else None
    except Exception:
        return None


def start_remote_transcript(solver: Any, path: str) -> None:
    execute_tui(solver, f'/file/start-transcript "{path}"')


def stop_remote_transcript(solver: Any) -> None:
    try:
        execute_tui(solver, "/file/stop-transcript")
    except Exception:
        pass


def run_stage_chunks(
    solver: Any,
    events: EventLog,
    *,
    stage: str,
    stage_iteration: int,
    total_iteration: int,
) -> tuple[Any, str]:
    root = branch_root("F09")
    stem = f"F09-{stage}-end-iter{total_iteration:06d}-supervised-{events.stamp}"
    terminal_case = win(root, stem + ".cas.h5")
    transcript = win(root, stem + ".trn")
    local_stream = PROJECT_ROOT / "output" / "03a_stage3" / "supervised" / events.stamp / (stem + ".stream.trn")
    local_stream.parent.mkdir(parents=True, exist_ok=True)

    stop_active_transcript(solver)
    start_remote_transcript(solver, transcript)
    events.emit(
        "f09_stage_start",
        branch="F09",
        stage=stage,
        stage_iterations=stage_iteration,
        cumulative_iteration=total_iteration,
        chunks=stage_iteration // CHUNK_SIZE,
        transcript=transcript,
        terminal_case=terminal_case,
        terminal_data=data_path(terminal_case),
    )

    collector = SessionTranscriptCapture(solver, stream_path=local_stream, echo=True)
    collector.start()
    numerical_failure: dict[str, Any] | None = None
    try:
        for chunk in range(1, stage_iteration // CHUNK_SIZE + 1):
            expected = total_iteration - stage_iteration + chunk * CHUNK_SIZE
            marker = collector.mark()
            started = time.monotonic()
            command_error: str | None = None
            try:
                execute_tui(solver, f"/solve/iterate {CHUNK_SIZE}")
            except Exception as exc:
                command_error = f"{type(exc).__name__}: {exc}"

            collector.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=8.0)
            output = collector.text_since(marker)
            lowered = output.lower()
            matched = [marker_text for marker_text in NUMERICAL_MARKERS if marker_text in lowered]
            summary = snapshot_summary(solver)
            residuals_ok, bad_residuals = finite_residuals(summary)
            observed = summary.get("iteration")
            transport_error = bool(
                command_error
                and any(
                    marker_text in command_error.lower()
                    for marker_text in (
                        "stream removed",
                        "recvmsg",
                        "grpc",
                        "transport",
                        "timed out",
                        "deadline exceeded",
                        "connection reset",
                        "failed to connect",
                    )
                )
            )
            events.emit(
                "f09_chunk_observed",
                branch="F09",
                stage=stage,
                chunk=chunk,
                of=stage_iteration // CHUNK_SIZE,
                expected_iteration=expected,
                observed_iteration=observed,
                elapsed_s=round(time.monotonic() - started, 2),
                command_error=command_error,
                transport_error=transport_error,
                numerical_markers=matched,
                residuals_finite=residuals_ok,
                nonfinite_residuals=bad_residuals,
                snapshot=summary,
            )

            if matched or not residuals_ok:
                numerical_failure = {
                    "stage": stage,
                    "chunk": chunk,
                    "expected_iteration": expected,
                    "observed_iteration": observed,
                    "markers": matched,
                    "nonfinite_residuals": bad_residuals,
                }
                break

            if command_error and not transport_error:
                raise RuntimeError(f"F09 non-transport client error at {stage} chunk {chunk}: {command_error}")

            if command_error and transport_error:
                events.emit(
                    "f09_transport_uncertain",
                    branch="F09",
                    stage=stage,
                    chunk=chunk,
                    error=command_error,
                    no_repeat=True,
                    no_reload=True,
                )
                solver = reconnect(events, reason=f"f09_transport:{stage}:chunk{chunk}")
                observed_after_reconnect = current_iteration(solver)
                events.emit(
                    "f09_transport_reconciled",
                    branch="F09",
                    stage=stage,
                    chunk=chunk,
                    observed_iteration=observed_after_reconnect,
                    expected_iteration=expected,
                    terminal_case_exists=False,
                    terminal_data_exists=False,
                    no_repeat=True,
                )
                if observed_after_reconnect is None or observed_after_reconnect < expected:
                    raise RuntimeError(
                        f"F09 transport outcome remains uncertain at {stage} chunk {chunk}; "
                        "no repeat or reload permitted"
                    )

            if observed is not None and int(observed) < expected and not command_error:
                raise RuntimeError(
                    f"F09 chunk stopped before expected iteration {expected}; observed {observed}"
                )

        if numerical_failure is not None:
            stop_remote_transcript(solver)
            events.emit(
                "f09_numerical_failure",
                branch="F09",
                stage=stage,
                failure=numerical_failure,
                transcript=transcript,
                terminal_pair_not_written=True,
                preserve_autosaves=True,
            )
            return solver, "numerical_failure"

        stop_remote_transcript(solver)
        write_pair(solver, terminal_case)
        if not isinstance(summary, dict):
            summary = snapshot_summary(solver)
        events.emit(
            "f09_stage_complete",
            branch="F09",
            stage=stage,
            cumulative_iteration=total_iteration,
            terminal_case=terminal_case,
            terminal_data=data_path(terminal_case),
            transcript=transcript,
            snapshot=snapshot_summary(solver),
        )
        return solver, "complete"
    finally:
        collector.close()


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = PROJECT_ROOT / "output" / "03a_stage3" / "supervised" / stamp
    events = EventLog(output_dir / "supervised-events.jsonl", stamp)
    events.emit("f09_supervised_start", branch="F09", server_id=SERVER_ID, no_competing_queue=True)

    solver = connect_with_transport_backoff(events)
    solver = prepare_new_branch(
        solver,
        events,
        branch="F09",
        momentum_urf=0.5,
        initial_velocity=VELOCITIES["10pct"],
    )
    settings = readback(solver)
    events.emit(
        "f09_setup_verified",
        branch="F09",
        settings=settings,
        velocity_values=velocity_values(settings),
        full_mixture=nested_value(settings["equations"], "mp") is True,
        momentum_urf=nested_value(settings["under_relaxation"], "mom"),
        hybrid_initialize_once=True,
    )

    previous_stage = "10pct"
    cumulative = 0
    for index, (stage, velocity, target) in enumerate(STAGES):
        if index:
            solver = transition(
                solver,
                events,
                branch="F09",
                from_stage=previous_stage,
                to_stage=stage,
                root=branch_root("F09"),
                velocity=velocity,
                momentum_urf=0.5,
            )
        solver, status = run_stage_chunks(
            solver,
            events,
            stage=stage,
            stage_iteration=3000,
            total_iteration=target,
        )
        if status != "complete":
            events.emit(
                "f09_branch_skipped_after_numerical_failure",
                branch="F09",
                failed_stage=stage,
                cumulative_iteration=cumulative,
                reason="User requested skip on confirmed floating-point/AMG/non-finite evidence",
            )
            return 3
        cumulative = target
        previous_stage = stage

    events.emit("f09_complete", branch="F09", final_iteration=cumulative, final_stage=previous_stage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
