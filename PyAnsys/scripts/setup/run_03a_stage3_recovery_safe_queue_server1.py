#!/usr/bin/env python3
"""Run the recovery-safe 03A Stage-3 continuation queue on Fluent server 1.

F08 resumes from the verified full-Mixture 20% / iteration-9000 pair. F10 and
F12 are seeded independently from the immutable P0 by the reviewed Schedule-D
preparation path. Each solve is one Fluent-native 3,000-iteration journal;
Python supervises stage boundaries and paired endpoint evidence only.

This file intentionally does not call ``run_03a_stage3_overnight_journal.py``'s
main function, because that function restarts F08 from P0.
"""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
import argparse
from pathlib import Path
import sys
import time
import traceback
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.common import remote_file_exists  # noqa: E402


SERVER_ID = "1"
STAGE_ITERATIONS = 3000
PAIR_WAIT_SECONDS = 4 * 60 * 60
F08_CASE = (
    r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F08"
    r"\F08-full-mixture-20pct-iter009000-20260819T061715Z.cas.h5"
)
F08_DATA = F08_CASE.replace(".cas.h5", ".dat.h5")
F08_ROOT = r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F08"


def load_reviewed_helpers():
    path = Path(__file__).with_name("run_03a_stage3_overnight_journal.py")
    spec = importlib.util.spec_from_file_location("stage3_reviewed_helpers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load reviewed Stage-3 helpers: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


h = load_reviewed_helpers()


class QueueBlocked(RuntimeError):
    """The queue cannot safely advance without operator recovery."""


class EventLog:
    def __init__(self, path: Path, stamp: str) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stamp = stamp

    def emit(self, kind: str, **fields: Any) -> None:
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "kind": kind,
            "stamp": self.stamp,
            **fields,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, default=str) + "\n")
            handle.flush()
        print(json.dumps(payload, default=str), flush=True)


def remote_pair_exists(solver: Any, case_path: str) -> bool:
    return remote_file_exists(solver, case_path) and remote_file_exists(
        solver, h.data_path(case_path)
    )


def verify_f08_state(solver: Any) -> dict[str, Any]:
    state = h.state_readback(solver)
    h.verify_transition(
        state,
        state,
        velocity=h.VELOCITY_20,
        momentum_urf=0.7,
        full_mixture=True,
    )
    return state


def reconnect(events: EventLog, *, reason: str) -> Any:
    events.emit("reconnect_attempt", reason=reason)
    solver = connect(server_id=SERVER_ID, start_transcript=False)
    if not solver.is_active():
        raise QueueBlocked("Fluent server 1 is not active after reconnect")
    events.emit("reconnected", reason=reason)
    return solver


def wait_for_pair(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    stage: str,
    case_path: str,
) -> Any:
    deadline = time.monotonic() + PAIR_WAIT_SECONDS
    probe = solver
    while time.monotonic() < deadline:
        try:
            if remote_pair_exists(probe, case_path):
                events.emit(
                    "native_pair_verified",
                    branch=branch,
                    stage=stage,
                    case=case_path,
                    data=h.data_path(case_path),
                    snapshot=h.snapshot_summary(probe),
                )
                return probe
        except Exception as exc:
            events.emit(
                "transport_observation_error",
                branch=branch,
                stage=stage,
                error=repr(exc),
            )
            probe = reconnect(events, reason=f"pair_wait:{branch}:{stage}")
        time.sleep(10.0)
    raise QueueBlocked(
        f"Timed out waiting for paired endpoint {case_path} / {h.data_path(case_path)}"
    )


def is_hard_failure(exc: Exception) -> bool:
    text = f"{type(exc).__name__}: {exc}".lower()
    return any(
        marker in text
        for marker in (
            "floating point",
            "floating-point",
            "fpe",
            "unrecoverable amg",
            "amg termination",
            "non-finite",
            "nonfinite",
            "solver termination",
        )
    )


def run_stage(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    stage: str,
    root: str,
    expected_iteration: int,
    stamp: str,
) -> Any:
    case_path = h.win(root, f"{branch}-{stage}-iter{expected_iteration:06d}-{stamp}.cas.h5")
    events.emit(
        "stage_intent",
        branch=branch,
        stage=stage,
        iterations=STAGE_ITERATIONS,
        expected_iteration=expected_iteration,
        case=case_path,
        data=h.data_path(case_path),
    )
    try:
        solver, _ = h.run_native_stage(
            solver,
            events,
            branch=branch,
            stage=stage,
            root=root,
            iterations=STAGE_ITERATIONS,
            expected_iteration=expected_iteration,
            stamp=stamp,
        )
        return solver
    except Exception as exc:
        events.emit(
            "native_stage_client_error",
            branch=branch,
            stage=stage,
            error=repr(exc),
            note="The native stage is never repeated until its paired endpoint is reconciled.",
        )
        try:
            solver = reconnect(events, reason=f"stage_error:{branch}:{stage}")
            if remote_pair_exists(solver, case_path):
                events.emit("native_stage_reconciled_after_client_error", branch=branch, stage=stage)
                solver.settings.file.read_case_data(file_name=case_path)
                return solver
        except Exception as reconnect_error:
            events.emit(
                "reconcile_failed",
                branch=branch,
                stage=stage,
                error=repr(reconnect_error),
            )
        if is_hard_failure(exc):
            raise
        raise QueueBlocked(
            f"Unresolved transport or execution uncertainty in {branch}/{stage}; queue stopped"
        ) from exc


def run_f08(solver: Any, events: EventLog, *, stamp: str, reload_pair: bool) -> Any:
    if not remote_pair_exists(solver, F08_CASE):
        raise QueueBlocked(f"Verified F08 recovery pair is incomplete: {F08_CASE}")
    if reload_pair:
        solver.settings.file.read_case_data(file_name=F08_CASE)
        load_mode = "paired-read_case_data"
    else:
        load_mode = "already-loaded-state-verified"
    state = verify_f08_state(solver)
    events.emit(
        "f08_recovery_loaded",
        case=F08_CASE,
        data=F08_DATA,
        state=state,
        load_mode=load_mode,
        hybrid_initialization=False,
    )
    root = h.win(F08_ROOT, f"recovery-{stamp}")
    h.ensure_remote_directory(solver, root)
    autosave = h.configure_autosave(solver, root)
    events.emit("f08_autosave_configured", root=root, autosave=autosave)

    solver = h.transition(
        solver,
        events,
        branch="F08",
        from_stage="full-mixture-20pct",
        to_stage="full-mixture-40pct",
        root=root,
        velocity=h.VELOCITY_40,
        momentum_urf=0.7,
        stamp=stamp,
    )
    solver = run_stage(
        solver, events, branch="F08", stage="full-mixture-40pct", root=root,
        expected_iteration=12000, stamp=stamp,
    )
    solver = h.transition(
        solver,
        events,
        branch="F08",
        from_stage="full-mixture-40pct",
        to_stage="full-mixture-80pct",
        root=root,
        velocity=h.VELOCITY_80,
        momentum_urf=0.7,
        stamp=stamp,
    )
    solver = run_stage(
        solver, events, branch="F08", stage="full-mixture-80pct", root=root,
        expected_iteration=15000, stamp=stamp,
    )
    solver = h.transition(
        solver,
        events,
        branch="F08",
        from_stage="full-mixture-80pct",
        to_stage="full-mixture-100pct",
        root=root,
        velocity=h.VELOCITY_100,
        momentum_urf=0.7,
        stamp=stamp,
    )
    solver = run_stage(
        solver, events, branch="F08", stage="full-mixture-100pct", root=root,
        expected_iteration=18000, stamp=stamp,
    )
    events.emit("branch_complete", branch="F08", final_stage="full-mixture-100pct")
    return solver


def run_independent_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    momentum_urf: float,
    stamp: str,
) -> Any:
    events.emit("independent_branch_start", branch=branch, p0=h.P0_REMOTE, momentum_urf=momentum_urf)
    solver = h.run_from_scratch_branch(
        solver,
        events,
        branch=branch,
        momentum_urf=momentum_urf,
        stamp=stamp,
    )
    return solver


def guarded_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    runner: Callable[[Any], Any],
) -> Any:
    try:
        return runner(solver)
    except Exception as exc:
        if is_hard_failure(exc):
            events.emit(
                "branch_skipped_after_hard_failure",
                branch=branch,
                classification="NUMERICAL_FAILURE",
                error=repr(exc),
                traceback=traceback.format_exc(),
            )
            return reconnect(events, reason=f"after_hard_failure:{branch}")
        events.emit(
            "queue_blocked",
            branch=branch,
            classification="UNRESOLVED_EXECUTION_OR_TRANSPORT_FAILURE",
            error=repr(exc),
            traceback=traceback.format_exc(),
        )
        raise QueueBlocked(f"Queue stopped at {branch}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the recovery-safe F08 -> F10 -> F12 Stage-3 queue.")
    parser.add_argument(
        "--use-current-f08-state",
        action="store_true",
        help="Use the already-verified live F08 state; do not repeat the blocking case/data reload.",
    )
    parser.add_argument(
        "--reload-f08",
        action="store_true",
        help="Reload the verified F08 case/data pair before continuing.",
    )
    args = parser.parse_args()
    if args.use_current_f08_state == args.reload_f08:
        parser.error("choose exactly one of --use-current-f08-state or --reload-f08")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = PROJECT_ROOT / "output" / "03A-stage3" / "recovery-safe" / stamp
    events = EventLog(output_dir / "recovery-safe-events.jsonl", stamp)
    events.emit(
        "queue_start",
        server_id=SERVER_ID,
        queue=("F08", "F10", "F12"),
        policy="recovery-safe-F08-resume; independent-F10-F12-from-immutable-P0; fixed-3000-native-stages",
        f08_case=F08_CASE,
        f08_data=F08_DATA,
    )
    solver = connect(server_id=SERVER_ID, start_transcript=False)
    if not solver.is_active():
        raise QueueBlocked("Fluent server 1 is not active")
    version = str(solver.get_fluent_version())
    if "2025 R2" not in version:
        raise QueueBlocked(f"Unexpected Fluent version: {version!r}")
    events.emit("server_connected", fluent_version=version)

    # The operator has confirmed the GUI Ready prompt. This live readback is
    # still recorded before the verified F08 pair is loaded.
    events.emit("operator_ready_confirmation_required_by_workflow", confirmed=True)
    solver = guarded_branch(
        solver,
        events,
        branch="F08",
        runner=lambda s: run_f08(s, events, stamp=stamp, reload_pair=args.reload_f08),
    )
    solver = guarded_branch(
        solver,
        events,
        branch="F10",
        runner=lambda s: run_independent_branch(s, events, branch="F10", momentum_urf=0.5, stamp=stamp),
    )
    solver = guarded_branch(
        solver,
        events,
        branch="F12",
        runner=lambda s: run_independent_branch(s, events, branch="F12", momentum_urf=0.3, stamp=stamp),
    )
    events.emit("queue_complete", endpoint_qualification="fixed-block-result; 3000 at 100pct")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
