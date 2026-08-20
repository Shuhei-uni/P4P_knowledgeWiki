#!/usr/bin/env python3
"""Retry F08 at 80% from the durable completed 40% endpoint, then continue.

The failed 80% run is never overwritten. A new retry directory is used. If a
native retry produces the same hard solver failure and Fluent becomes unusable,
F08 is recorded as skipped and the supervisor proceeds independently with F10
and F12 from immutable P0. Ambiguous transport or setup errors block the queue.
"""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import traceback
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.common import remote_file_exists  # noqa: E402


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


q = load_module(
    "stage3_recovery_queue",
    PROJECT_ROOT / "scripts/setup/run_03a_stage3_recovery_safe_queue_server1.py",
)

SERVER_ID = "1"
PREVIOUS_ROOT = r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F08\recovery-20260820T044148Z"
F08_40_CASE = PREVIOUS_ROOT + r"\F08-full-mixture-40pct-iter012000-20260820T044148Z.cas.h5"
F08_40_DATA = F08_40_CASE.replace(".cas.h5", ".dat.h5")
F08_ROOT = r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F08"


def hard_failure_confirmed(solver: Any, error: Exception) -> tuple[bool, dict[str, Any]]:
    """Use post-error evidence, not the generic gRPC error string alone."""

    evidence: dict[str, Any] = {"error": repr(error)}
    inactive = False
    try:
        solver.settings.solution.controls.equations.get_state()
        evidence["solution_controls"] = "responsive"
    except Exception as exc:
        inactive = True
        evidence["solution_controls"] = f"inactive: {type(exc).__name__}: {exc}"

    try:
        for variable in ("current-iteration", "number-of-iterations"):
            evidence[variable] = solver.scheme.eval(f"(%rpgetvar '{variable})")
    except Exception as exc:
        evidence["runtime_read_error"] = f"{type(exc).__name__}: {exc}"

    huge_residual = False
    try:
        snapshot = q.h.collect_snapshot(solver, monitor_sets=("residual",))
        residuals = snapshot.get("monitors", {}).get("residual", {}).get("last_values", {})
        evidence["residuals"] = residuals
        huge_residual = any(abs(float(value)) > 1.0e100 for value in residuals.values())
    except Exception as exc:
        evidence["snapshot_error"] = f"{type(exc).__name__}: {exc}"

    error_object = "error object: #f" in str(error).lower()
    zero_iteration_limit = evidence.get("number-of-iterations") == 0
    confirmed = inactive or huge_residual or (error_object and zero_iteration_limit)
    evidence["confirmed_hard_failure"] = confirmed
    return confirmed, evidence


def state_at_40(solver: Any) -> dict[str, Any]:
    state = q.h.state_readback(solver)
    q.h.verify_transition(
        state,
        state,
        velocity=q.h.VELOCITY_40,
        momentum_urf=0.7,
        full_mixture=True,
    )
    return state


def run_native_with_hard_classification(
    solver: Any,
    events: Any,
    *,
    branch: str,
    stage: str,
    root: str,
    expected_iteration: int,
    stamp: str,
) -> tuple[Any, bool]:
    try:
        solver = q.run_stage(
            solver,
            events,
            branch=branch,
            stage=stage,
            root=root,
            expected_iteration=expected_iteration,
            stamp=stamp,
        )
        return solver, True
    except Exception as exc:
        try:
            solver = q.reconnect(events, reason=f"classify_failure:{branch}:{stage}")
        except Exception as reconnect_error:
            raise q.QueueBlocked(
                f"Cannot reconnect after {branch}/{stage} failure: {reconnect_error}"
            ) from exc
        hard, evidence = hard_failure_confirmed(solver, exc)
        events.emit(
            "post_failure_classification",
            branch=branch,
            stage=stage,
            classification="NUMERICAL_FAILURE" if hard else "UNRESOLVED",
            evidence=evidence,
        )
        if hard:
            events.emit(
                "branch_skipped_after_confirmed_hard_failure",
                branch=branch,
                stage=stage,
                evidence=evidence,
            )
            return solver, False
        raise q.QueueBlocked(f"Ambiguous failure in {branch}/{stage}; queue stopped") from exc


def run_independent_with_hard_classification(
    solver: Any,
    events: Any,
    *,
    branch: str,
    momentum_urf: float,
    stamp: str,
) -> tuple[Any, bool]:
    try:
        solver = q.run_independent_branch(
            solver,
            events,
            branch=branch,
            momentum_urf=momentum_urf,
            stamp=stamp,
        )
        return solver, True
    except Exception as exc:
        try:
            solver = q.reconnect(events, reason=f"classify_failure:{branch}")
        except Exception as reconnect_error:
            raise q.QueueBlocked(
                f"Cannot reconnect after {branch} failure: {reconnect_error}"
            ) from exc
        hard, evidence = hard_failure_confirmed(solver, exc)
        events.emit(
            "post_failure_classification",
            branch=branch,
            classification="NUMERICAL_FAILURE" if hard else "UNRESOLVED",
            evidence=evidence,
        )
        if hard:
            events.emit(
                "branch_skipped_after_confirmed_hard_failure",
                branch=branch,
                evidence=evidence,
            )
            return solver, False
        raise q.QueueBlocked(f"Ambiguous failure in {branch}; queue stopped") from exc


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = PROJECT_ROOT / "output/03A-stage3/recovery-retry80" / stamp
    events = q.EventLog(output_dir / "recovery-retry80-events.jsonl", stamp)
    events.emit(
        "retry_queue_start",
        server_id=SERVER_ID,
        source_case=F08_40_CASE,
        source_data=F08_40_DATA,
        prior_failed_run="C:\\Users\\syok443\\Documents\\FluentRuns\\03A-stage3\\F08\\recovery-20260820T044148Z",
        queue=("F08-80pct-retry", "F08-100pct", "F10", "F12"),
    )

    solver = connect(server_id=SERVER_ID, start_transcript=False)
    if not solver.is_active():
        raise q.QueueBlocked("Fluent server 1 is not active")
    events.emit("server_connected", fluent_version=str(solver.get_fluent_version()))

    if not remote_file_exists(solver, F08_40_CASE) or not remote_file_exists(solver, F08_40_DATA):
        raise q.QueueBlocked(f"Completed F08 40% source pair is unavailable: {F08_40_CASE}")

    # This is the explicit restart point requested by the user.
    solver.settings.file.read_case_data(file_name=F08_40_CASE)
    state = state_at_40(solver)
    events.emit(
        "f08_40_source_loaded",
        case=F08_40_CASE,
        data=F08_40_DATA,
        state=state,
        hybrid_initialization=False,
    )

    retry_root = q.h.win(F08_ROOT, f"recovery-retry80-{stamp}")
    q.h.ensure_remote_directory(solver, retry_root)
    events.emit("retry_autosave_configured", root=retry_root, autosave=q.h.configure_autosave(solver, retry_root))

    solver = q.h.transition(
        solver,
        events,
        branch="F08",
        from_stage="full-mixture-40pct",
        to_stage="full-mixture-80pct-retry",
        root=retry_root,
        velocity=q.h.VELOCITY_80,
        momentum_urf=0.7,
        stamp=stamp,
    )
    solver, f08_80_ok = run_native_with_hard_classification(
        solver,
        events,
        branch="F08",
        stage="full-mixture-80pct-retry",
        root=retry_root,
        expected_iteration=15000,
        stamp=stamp,
    )

    if f08_80_ok:
        solver = q.h.transition(
            solver,
            events,
            branch="F08",
            from_stage="full-mixture-80pct-retry",
            to_stage="full-mixture-100pct",
            root=retry_root,
            velocity=q.h.VELOCITY_100,
            momentum_urf=0.7,
            stamp=stamp,
        )
        solver, f08_100_ok = run_native_with_hard_classification(
            solver,
            events,
            branch="F08",
            stage="full-mixture-100pct",
            root=retry_root,
            expected_iteration=18000,
            stamp=stamp,
        )
        events.emit("branch_complete" if f08_100_ok else "branch_skipped", branch="F08")
    else:
        events.emit("branch_skipped", branch="F08", reason="confirmed_hard_failure_at_80pct")

    solver, f10_ok = run_independent_with_hard_classification(
        solver, events, branch="F10", momentum_urf=0.5, stamp=stamp
    )
    events.emit("branch_complete" if f10_ok else "branch_skipped", branch="F10")
    solver, f12_ok = run_independent_with_hard_classification(
        solver, events, branch="F12", momentum_urf=0.3, stamp=stamp
    )
    events.emit("branch_complete" if f12_ok else "branch_skipped", branch="F12")
    events.emit("retry_queue_complete", fixed_block_result=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
