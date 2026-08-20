#!/usr/bin/env python3
"""Continue F12 from the already verified carrier-only preinit on Server 1.

The normal P0 preparation reached F12's preinit case, but the client hung
while waiting for Fluent's acknowledgement of a redundant preinit reload.
Fluent is responsive and its live state is verified, so this controller uses
that live preinit exactly once, performs Hybrid Initialization, and then owns
the six native 3,000-iteration blocks and their paired checkpoints.
"""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
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

PREINIT = (
    r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F12"
    r"\F12-D-M1-S1-U0p3-preinit-20260820T055715Z.cas.h5"
)


def read_remote_forms(solver: Any, path: str) -> list[Any]:
    escaped = quote_scheme_string(path)
    expression = (
        f'(with-input-from-file "{escaped}" '
        "(lambda () (let loop ((x (read)) (out (quote ()))) "
        "(if (eof-object? x) (reverse out) (loop (read) (cons x out))))))"
    )
    payload = solver.scheme.eval(expression)
    return list(payload) if isinstance(payload, (list, tuple)) else [payload]


def verify_live_preinit(solver: Any) -> dict[str, Any]:
    state = q.h.state_readback(solver)
    q.h.verify_transition(
        state,
        state,
        velocity=q.h.VELOCITY_10,
        momentum_urf=0.3,
        full_mixture=False,
    )
    return state


def run_f12_blocks(solver: Any, events: Any, *, root: str, stamp: str) -> Any:
    solver = q.run_stage(
        solver, events, branch="F12", stage="carrier-10pct", root=root,
        expected_iteration=3000, stamp=stamp,
    )
    transitions = [
        ("carrier-10pct", "full-mixture-10pct", q.h.VELOCITY_10, "full-mixture-10pct", 6000),
        ("full-mixture-10pct", "full-mixture-20pct", q.h.VELOCITY_20, "full-mixture-20pct", 9000),
        ("full-mixture-20pct", "full-mixture-40pct", q.h.VELOCITY_40, "full-mixture-40pct", 12000),
        ("full-mixture-40pct", "full-mixture-80pct", q.h.VELOCITY_80, "full-mixture-80pct", 15000),
        ("full-mixture-80pct", "full-mixture-100pct", q.h.VELOCITY_100, "full-mixture-100pct", 18000),
    ]
    for from_stage, to_stage, velocity, stage, expected in transitions:
        solver = q.h.transition(
            solver, events, branch="F12", from_stage=from_stage,
            to_stage=to_stage, root=root, velocity=velocity,
            momentum_urf=0.3, stamp=stamp,
        )
        solver = q.run_stage(
            solver, events, branch="F12", stage=stage, root=root,
            expected_iteration=expected, stamp=stamp,
        )
    return solver


def classify_failure(solver: Any, error: Exception, *, root: str, stamp: str, events: Any) -> bool:
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
    # Inspect all F12 native transcripts created by this run for explicit FPE
    # or AMG evidence. A gRPC '#f' alone remains unresolved.
    transcripts = []
    for expected, stage in (
        (3000, "carrier-10pct"), (6000, "full-mixture-10pct"),
        (9000, "full-mixture-20pct"), (12000, "full-mixture-40pct"),
        (15000, "full-mixture-80pct"), (18000, "full-mixture-100pct"),
    ):
        path = q.h.win(root, f"F12-{stage}-iter{expected:06d}-{stamp}.trn")
        try:
            if remote_file_exists(solver, path):
                forms = read_remote_forms(solver, path)
                text = " ".join(str(item) for item in forms).lower()
                transcripts.append({
                    "path": path,
                    "floating_point_exception": "floating point exception" in text,
                    "amg_failure": "unrecoverable amg" in text or "amg termination" in text,
                    "tail": [str(item) for item in forms[-24:]],
                })
                hard = hard or transcripts[-1]["floating_point_exception"] or transcripts[-1]["amg_failure"]
        except Exception as exc:
            transcripts.append({"path": path, "read_error": f"{type(exc).__name__}: {exc}"})
    evidence["transcripts"] = transcripts
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
    output_dir = PROJECT_ROOT / "output/03A-stage3/f12-from-verified-preinit" / stamp
    events = q.EventLog(output_dir / "f12-events.jsonl", stamp)
    events.emit(
        "f12_resume_start",
        server_id="1",
        preinit=PREINIT,
        preinit_reload_skipped=True,
        reason="live preinit state verified after client-side read_case acknowledgement hang",
        momentum_urf=0.3,
        fixed_block_iterations=3000,
    )
    solver = connect(server_id="1", start_transcript=False)
    if not solver.is_active():
        raise q.QueueBlocked("Fluent server 1 is inactive")
    events.emit("server_connected", fluent_version=str(solver.get_fluent_version()))
    if not remote_file_exists(solver, PREINIT):
        raise q.QueueBlocked(f"F12 preinit artifact unavailable: {PREINIT}")
    q.h.stop_native_transcript_if_active(solver)
    state = verify_live_preinit(solver)
    events.emit("f12_live_preinit_verified", preinit=PREINIT, state=state, hybrid_initialization_repeated=False)

    root = q.h.win(
        q.h.win(q.h.REMOTE_QUEUE_ROOT, "F12"),
        f"recovery-{stamp}",
    )
    q.h.ensure_remote_directory(solver, root)
    autosave = q.h.configure_autosave(solver, root)
    events.emit("f12_autosave_configured", root=root, autosave=autosave)
    solver.settings.solution.initialization.hybrid_initialize()
    start = q.h.win(root, f"F12-hybrid-initialized-iter000000-{stamp}.cas.h5")
    q.h.write_pair(solver, start)
    events.emit("hybrid_initialized_once", start_case=start, start_data=q.h.data_path(start))

    try:
        solver = run_f12_blocks(solver, events, root=root, stamp=stamp)
    except Exception as exc:
        try:
            solver = connect(server_id="1", start_transcript=False)
            if not solver.is_active():
                raise q.QueueBlocked("Fluent server 1 inactive during F12 classification")
        except Exception as reconnect_error:
            events.emit("reconnect_failed", branch="F12", error=repr(reconnect_error))
            raise
        if classify_failure(solver, exc, root=root, stamp=stamp, events=events):
            events.emit("branch_skipped_after_confirmed_hard_failure", branch="F12")
            events.emit("f12_resume_complete", fixed_block_result=False)
            return 0
        raise q.QueueBlocked("Ambiguous F12 failure; queue stopped") from exc

    events.emit("branch_complete", branch="F12", final_stage="full-mixture-100pct")
    events.emit("f12_resume_complete", fixed_block_result=True, qualification_note="18,000 fixed-block endpoint; not 5,000-at-100pct qualification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
