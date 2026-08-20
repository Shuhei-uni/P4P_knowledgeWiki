#!/usr/bin/env python3
"""Run F12 from immutable P0 after the confirmed F10 hard failure.

F08 was skipped after a reproduced numerical failure at 80%.  F10 was then
run from its existing hybrid-initialized checkpoint and its native transcript
confirmed a floating-point exception.  This controller therefore records
those decisions, resets Fluent from immutable P0, and supervises the complete
F12 fixed-block queue at momentum URF 0.3.
"""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import traceback
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


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

F10_FAILURE_TRANSCRIPT = (
    r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F10"
    r"\resume-20260820T055022Z\F10-carrier-10pct-iter003000-20260820T055022Z.trn"
)


def read_remote_forms(solver: Any, path: str) -> list[Any]:
    """Read a remote Fluent text artifact through Scheme's Lisp reader."""

    escaped = quote_scheme_string(path)
    expression = (
        f'(with-input-from-file "{escaped}" '
        "(lambda () (let loop ((x (read)) (out (quote ()))) "
        "(if (eof-object? x) (reverse out) (loop (read) (cons x out))))))"
    )
    payload = solver.scheme.eval(expression)
    return list(payload) if isinstance(payload, (list, tuple)) else [payload]


def record_f10_evidence(solver: Any, events: Any) -> None:
    evidence: dict[str, Any] = {
        "transcript": F10_FAILURE_TRANSCRIPT,
        "paired_checkpoint": False,
        "residual_export": False,
        "classification": "NUMERICAL_FAILURE",
        "reason": "native transcript contains floating point exception",
    }
    try:
        forms = read_remote_forms(solver, F10_FAILURE_TRANSCRIPT)
        transcript_text = " ".join(str(item) for item in forms)
        evidence["floating_point_exception_present"] = "floating point exception" in transcript_text.lower()
        evidence["transcript_tail"] = [str(item) for item in forms[-30:]]
    except Exception as exc:
        evidence["transcript_read_error"] = f"{type(exc).__name__}: {exc}"
    events.emit("f10_hard_failure_recorded", evidence=evidence)


def f12_stage_transcript(stamp: str, expected: int) -> str:
    root = q.h.win(q.h.REMOTE_QUEUE_ROOT, "F12")
    return q.h.win(root, f"F12-carrier-10pct-iter{expected:06d}-{stamp}.trn")


def classify_f12_failure(solver: Any, error: Exception, stamp: str, events: Any) -> bool:
    evidence: dict[str, Any] = {"error": repr(error)}
    hard = False
    try:
        solver.settings.solution.controls.equations.get_state()
        evidence["solution_controls"] = "responsive"
    except Exception as exc:
        hard = True
        evidence["solution_controls"] = f"inactive: {type(exc).__name__}: {exc}"
    try:
        evidence["number_of_iterations"] = solver.scheme.eval("(%rpgetvar 'number-of-iterations)")
    except Exception as exc:
        evidence["runtime_error"] = f"{type(exc).__name__}: {exc}"
    transcript = f12_stage_transcript(stamp, 3000)
    evidence["transcript"] = transcript
    try:
        if remote_file_exists(solver, transcript):
            forms = read_remote_forms(solver, transcript)
            text = " ".join(str(item) for item in forms)
            evidence["floating_point_exception_present"] = "floating point exception" in text.lower()
            evidence["transcript_tail"] = [str(item) for item in forms[-30:]]
            hard = hard or bool(evidence["floating_point_exception_present"])
    except Exception as exc:
        evidence["transcript_read_error"] = f"{type(exc).__name__}: {exc}"
    events.emit(
        "post_failure_classification",
        branch="F12",
        classification="NUMERICAL_FAILURE" if hard else "UNRESOLVED",
        evidence=evidence,
        traceback=traceback.format_exc(),
    )
    return hard


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = PROJECT_ROOT / "output/03A-stage3/resume-f12-after-f10-fpe" / stamp
    events = q.EventLog(output_dir / "resume-events.jsonl", stamp)
    events.emit(
        "resume_start",
        server_id="1",
        queue=("F12",),
        f08_status="skipped-after-reproduced-hard-failure-at-80pct",
        f10_status="skipped-after-confirmed-floating-point-exception",
        f10_failure_transcript=F10_FAILURE_TRANSCRIPT,
        p0=q.h.P0_REMOTE,
        p0_sha256=q.h.P0_SHA256,
        momentum_urf=0.3,
    )
    solver = connect(server_id="1", start_transcript=False)
    if not solver.is_active():
        raise q.QueueBlocked("Fluent server 1 is inactive")
    events.emit("server_connected", fluent_version=str(solver.get_fluent_version()))
    record_f10_evidence(solver, events)
    q.h.stop_native_transcript_if_active(solver)

    try:
        solver = q.run_independent_branch(
            solver,
            events,
            branch="F12",
            momentum_urf=0.3,
            stamp=stamp,
        )
        events.emit("branch_complete", branch="F12", endpoint="fixed-block-result")
        events.emit("resume_complete", fixed_block_result=True, remaining_branches=())
        return 0
    except Exception as exc:
        try:
            solver = connect(server_id="1", start_transcript=False)
            if not solver.is_active():
                raise q.QueueBlocked("Fluent server 1 inactive during F12 classification")
        except Exception as reconnect_error:
            events.emit("reconnect_failed", branch="F12", error=repr(reconnect_error))
            raise
        if classify_f12_failure(solver, exc, stamp, events):
            events.emit("branch_skipped_after_confirmed_hard_failure", branch="F12")
            events.emit("resume_complete", fixed_block_result=False, remaining_branches=())
            return 0
        raise q.QueueBlocked("Ambiguous F12 failure; queue stopped") from exc


if __name__ == "__main__":
    raise SystemExit(main())
