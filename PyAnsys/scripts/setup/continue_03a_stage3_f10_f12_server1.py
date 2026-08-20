#!/usr/bin/env python3
"""Continue 03A Stage-3 with independent F10 and F12 after F08 is skipped."""

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


def hard_failure_confirmed(solver: Any, error: Exception) -> tuple[bool, dict[str, Any]]:
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
    huge_residual = False
    try:
        snapshot = q.h.collect_snapshot(solver, monitor_sets=("residual",))
        residuals = snapshot.get("monitors", {}).get("residual", {}).get("last_values", {})
        evidence["residuals"] = residuals
        huge_residual = any(abs(float(value)) > 1.0e20 for value in residuals.values())
    except Exception as exc:
        evidence["snapshot_error"] = f"{type(exc).__name__}: {exc}"
    confirmed = inactive or huge_residual
    evidence["confirmed_hard_failure"] = confirmed
    return confirmed, evidence


def reconnect(events: Any, reason: str) -> Any:
    events.emit("reconnect_attempt", reason=reason)
    solver = connect(server_id="1", start_transcript=False)
    if not solver.is_active():
        raise q.QueueBlocked("Fluent server 1 is inactive")
    events.emit("reconnected", reason=reason)
    return solver


def run_branch(solver: Any, events: Any, *, branch: str, momentum_urf: float, stamp: str) -> tuple[Any, bool]:
    try:
        solver = q.run_independent_branch(
            solver,
            events,
            branch=branch,
            momentum_urf=momentum_urf,
            stamp=stamp,
        )
        events.emit("branch_complete", branch=branch, endpoint="fixed-block-result")
        return solver, True
    except Exception as exc:
        solver = reconnect(events, f"classify_failure:{branch}")
        hard, evidence = hard_failure_confirmed(solver, exc)
        events.emit(
            "post_failure_classification",
            branch=branch,
            classification="NUMERICAL_FAILURE" if hard else "UNRESOLVED",
            evidence=evidence,
            traceback=traceback.format_exc(),
        )
        if hard:
            events.emit("branch_skipped_after_confirmed_hard_failure", branch=branch, evidence=evidence)
            return solver, False
        raise q.QueueBlocked(f"Ambiguous {branch} failure; queue stopped") from exc


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = PROJECT_ROOT / "output/03A-stage3/continuation-f10-f12" / stamp
    events = q.EventLog(output_dir / "continuation-events.jsonl", stamp)
    events.emit(
        "continuation_start",
        server_id="1",
        f08_status="skipped-after-reproduced-hard-failure-at-80pct",
        queue=("F10", "F12"),
        p0=q.h.P0_REMOTE,
    )
    solver = connect(server_id="1", start_transcript=False)
    if not solver.is_active():
        raise q.QueueBlocked("Fluent server 1 is inactive")
    events.emit("server_connected", fluent_version=str(solver.get_fluent_version()))

    solver, f10_ok = run_branch(solver, events, branch="F10", momentum_urf=0.5, stamp=stamp)
    if not f10_ok:
        events.emit("branch_skipped", branch="F10", reason="confirmed_hard_failure")
    solver, f12_ok = run_branch(solver, events, branch="F12", momentum_urf=0.3, stamp=stamp)
    if not f12_ok:
        events.emit("branch_skipped", branch="F12", reason="confirmed_hard_failure")
    events.emit("continuation_complete", fixed_block_result=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
