#!/usr/bin/env python3
"""Resume F10 from its existing hybrid-initialized pair, then run F12.

The first F10 carrier journal failed before creating a transcript or residual
file. This resume releases any stale native transcript left by the failed F08
journal, reloads the already-created F10 hybrid pair, and does not hybrid
initialize F10 a second time.
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

F10_HYBRID_CASE = r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F10\F10-hybrid-initialized-iter000000-20260820T054449Z.cas.h5"
F10_HYBRID_DATA = F10_HYBRID_CASE.replace(".cas.h5", ".dat.h5")
F10_ROOT = r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F10"


def reconnect(events: Any, reason: str) -> Any:
    events.emit("reconnect_attempt", reason=reason)
    solver = connect(server_id="1", start_transcript=False)
    if not solver.is_active():
        raise q.QueueBlocked("Fluent server 1 is inactive")
    events.emit("reconnected", reason=reason)
    return solver


def classify_post_error(solver: Any, error: Exception) -> tuple[bool, dict[str, Any]]:
    evidence: dict[str, Any] = {"error": repr(error)}
    inactive = False
    try:
        solver.settings.solution.controls.equations.get_state()
        evidence["solution_controls"] = "responsive"
    except Exception as exc:
        inactive = True
        evidence["solution_controls"] = f"inactive: {type(exc).__name__}: {exc}"
    try:
        evidence["number_of_iterations"] = solver.scheme.eval("(%rpgetvar 'number-of-iterations)")
    except Exception as exc:
        evidence["runtime_error"] = f"{type(exc).__name__}: {exc}"
    huge = False
    try:
        snapshot = q.h.collect_snapshot(solver, monitor_sets=("residual",))
        residuals = snapshot.get("monitors", {}).get("residual", {}).get("last_values", {})
        evidence["residuals"] = residuals
        huge = any(abs(float(value)) > 1.0e20 for value in residuals.values())
    except Exception as exc:
        evidence["snapshot_error"] = f"{type(exc).__name__}: {exc}"
    hard = inactive or huge
    evidence["confirmed_hard_failure"] = hard
    return hard, evidence


def run_stage(solver: Any, events: Any, *, branch: str, stage: str, root: str, expected: int, stamp: str) -> tuple[Any, bool]:
    q.h.stop_native_transcript_if_active(solver)
    try:
        solver = q.run_stage(
            solver, events, branch=branch, stage=stage, root=root,
            expected_iteration=expected, stamp=stamp,
        )
        return solver, True
    except Exception as exc:
        try:
            solver = reconnect(events, f"classify_failure:{branch}:{stage}")
        except Exception as reconnect_error:
            raise q.QueueBlocked(f"Cannot reconnect after {branch}/{stage}: {reconnect_error}") from exc
        hard, evidence = classify_post_error(solver, exc)
        events.emit(
            "post_failure_classification",
            branch=branch,
            stage=stage,
            classification="NUMERICAL_FAILURE" if hard else "UNRESOLVED",
            evidence=evidence,
            traceback=traceback.format_exc(),
        )
        if hard:
            events.emit("branch_skipped_after_confirmed_hard_failure", branch=branch, stage=stage, evidence=evidence)
            return solver, False
        raise q.QueueBlocked(f"Ambiguous failure in {branch}/{stage}; queue stopped") from exc


def verify_f10_hybrid(solver: Any) -> dict[str, Any]:
    state = q.h.state_readback(solver)
    q.h.verify_transition(
        state, state, velocity=q.h.VELOCITY_10,
        momentum_urf=0.5, full_mixture=False,
    )
    return state


def run_f10(solver: Any, events: Any, *, stamp: str) -> tuple[Any, bool]:
    if not remote_file_exists(solver, F10_HYBRID_CASE) or not remote_file_exists(solver, F10_HYBRID_DATA):
        raise q.QueueBlocked("F10 hybrid-initialized pair is unavailable")
    q.h.stop_native_transcript_if_active(solver)
    solver.settings.file.read_case_data(file_name=F10_HYBRID_CASE)
    state = verify_f10_hybrid(solver)
    events.emit("f10_hybrid_pair_loaded", case=F10_HYBRID_CASE, data=F10_HYBRID_DATA, state=state, hybrid_initialization_repeated=False)
    root = q.h.win(F10_ROOT, f"resume-{stamp}")
    q.h.ensure_remote_directory(solver, root)
    events.emit("f10_autosave_configured", root=root, autosave=q.h.configure_autosave(solver, root))

    stages = [
        ("carrier-10pct", 3000),
    ]
    for stage, expected in stages:
        solver, ok = run_stage(solver, events, branch="F10", stage=stage, root=root, expected=expected, stamp=stamp)
        if not ok:
            return solver, False
    solver = q.h.transition(solver, events, branch="F10", from_stage="carrier-10pct", to_stage="full-mixture-10pct", root=root, velocity=q.h.VELOCITY_10, momentum_urf=0.5, stamp=stamp)
    for stage, expected, velocity, from_stage, to_stage in [
        ("full-mixture-10pct", 6000, q.h.VELOCITY_20, "full-mixture-10pct", "full-mixture-20pct"),
        ("full-mixture-20pct", 9000, q.h.VELOCITY_40, "full-mixture-20pct", "full-mixture-40pct"),
        ("full-mixture-40pct", 12000, q.h.VELOCITY_80, "full-mixture-40pct", "full-mixture-80pct"),
        ("full-mixture-80pct", 15000, q.h.VELOCITY_100, "full-mixture-80pct", "full-mixture-100pct"),
        ("full-mixture-100pct", 18000, None, "", ""),
    ]:
        solver, ok = run_stage(solver, events, branch="F10", stage=stage, root=root, expected=expected, stamp=stamp)
        if not ok:
            return solver, False
        if velocity is not None:
            solver = q.h.transition(solver, events, branch="F10", from_stage=from_stage, to_stage=to_stage, root=root, velocity=velocity, momentum_urf=0.5, stamp=stamp)
    events.emit("branch_complete", branch="F10", final_stage="full-mixture-100pct")
    return solver, True


def run_f12(solver: Any, events: Any, *, stamp: str) -> tuple[Any, bool]:
    q.h.stop_native_transcript_if_active(solver)
    try:
        solver = q.run_independent_branch(solver, events, branch="F12", momentum_urf=0.3, stamp=stamp)
        events.emit("branch_complete", branch="F12", endpoint="fixed-block-result")
        return solver, True
    except Exception as exc:
        solver = reconnect(events, "classify_failure:F12")
        hard, evidence = classify_post_error(solver, exc)
        events.emit("post_failure_classification", branch="F12", classification="NUMERICAL_FAILURE" if hard else "UNRESOLVED", evidence=evidence, traceback=traceback.format_exc())
        if hard:
            events.emit("branch_skipped_after_confirmed_hard_failure", branch="F12", evidence=evidence)
            return solver, False
        raise q.QueueBlocked("Ambiguous F12 failure; queue stopped") from exc


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = PROJECT_ROOT / "output/03A-stage3/resume-f10-f12" / stamp
    events = q.EventLog(output_dir / "resume-events.jsonl", stamp)
    events.emit("resume_start", server_id="1", f08_status="skipped-after-reproduced-hard-failure-at-80pct", f10_source=F10_HYBRID_CASE, queue=("F10-resume", "F12"))
    solver = connect(server_id="1", start_transcript=False)
    if not solver.is_active():
        raise q.QueueBlocked("Fluent server 1 is inactive")
    events.emit("server_connected", fluent_version=str(solver.get_fluent_version()))
    solver, f10_ok = run_f10(solver, events, stamp=stamp)
    if not f10_ok:
        events.emit("branch_skipped", branch="F10", reason="confirmed_hard_failure")
    solver, f12_ok = run_f12(solver, events, stamp=stamp)
    if not f12_ok:
        events.emit("branch_skipped", branch="F12", reason="confirmed_hard_failure")
    events.emit("resume_complete", fixed_block_result=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
