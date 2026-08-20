from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "setup" / "run_03a_stage3_override_native_queue_server2.py"
)


def load_queue_module():
    """Load the supervisor without invoking its ``main`` entry point."""

    spec = importlib.util.spec_from_file_location("stage3_native_queue", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EventRecorder:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def emit(self, kind: str, **fields: object) -> None:
        self.events.append((kind, fields))


class Stage3QueueResumeTests(unittest.TestCase):
    def test_ledger_round_trip_persists_prepared_branch_and_submitted_stage(self) -> None:
        queue = load_queue_module()

        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "campaign"
            ledger = queue.RunLedger.create(run_dir, stamp="20260820T000000Z")
            ledger.branch_prepared(
                "F02",
                root=r"C:\\FluentRuns\\03A-stage3\\F02\\run-20260820T000000Z",
                start_case=r"C:\\FluentRuns\\03A-stage3\\F02\\start.cas.h5",
            )
            ledger.stage_submitted(
                "F02",
                "carrier-100pct",
                case_path=r"C:\\FluentRuns\\03A-stage3\\F02\\carrier-end.cas.h5",
            )

            # A laptop shutdown after submission is not evidence that Fluent
            # finished the native stage.  Reload must retain ``submitted``.
            resumed = queue.RunLedger.load(run_dir)
            submitted = resumed.state["branches"]["F02"]["stages"]["carrier-100pct"]
            self.assertEqual(submitted["status"], "submitted")
            self.assertEqual(
                submitted["case_path"],
                r"C:\\FluentRuns\\03A-stage3\\F02\\carrier-end.cas.h5",
            )

            durable = json.loads((run_dir / queue.RunLedger.filename).read_text(encoding="utf-8"))
            self.assertEqual(durable["stamp"], "20260820T000000Z")
            self.assertEqual(
                durable["branches"]["F02"]["prepared"]["start_case"],
                r"C:\\FluentRuns\\03A-stage3\\F02\\start.cas.h5",
            )

    def test_stage_completion_is_the_only_transition_that_marks_stage_complete(self) -> None:
        queue = load_queue_module()

        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "campaign"
            ledger = queue.RunLedger.create(run_dir, stamp="20260820T000000Z")
            ledger.branch_prepared("F05", root=r"C:\\FluentRuns\\F05", start_case=r"C:\\FluentRuns\\F05\\start.cas.h5")
            ledger.stage_submitted(
                "F05",
                "full-mixture-100pct",
                case_path=r"C:\\FluentRuns\\F05\\end.cas.h5",
            )
            ledger.stage_complete(
                "F05",
                "full-mixture-100pct",
                case_path=r"C:\\FluentRuns\\F05\\end.cas.h5",
            )

            completed = queue.RunLedger.load(run_dir).state["branches"]["F05"]["stages"]["full-mixture-100pct"]
            self.assertEqual(completed["status"], "complete")

    def test_terminal_fpe_skips_only_that_branch_after_reconnect(self) -> None:
        queue = load_queue_module()
        events = EventRecorder()
        original_solver = object()
        replacement_solver = object()

        def terminal_runner(_solver, _events, *, stamp):
            self.assertEqual(stamp, "20260820T000000Z")
            raise queue.TerminalNativeStageError(
                branch="F02",
                stage="carrier-100pct",
                journal_error=RuntimeError("Floating point exception"),
            )

        with patch.object(queue, "reconnect", return_value=replacement_solver) as reconnect:
            solver, successful, can_continue = queue.guarded_branch(
                original_solver,
                events,
                branch="F02",
                runner=terminal_runner,
                stamp="20260820T000000Z",
            )

        self.assertIs(solver, replacement_solver)
        self.assertFalse(successful)
        self.assertTrue(can_continue)
        reconnect.assert_called_once()
        kinds = [kind for kind, _fields in events.events]
        self.assertIn("branch_failure", kinds)
        self.assertIn("branch_skipped", kinds)
        failure = next(fields for kind, fields in events.events if kind == "branch_failure")
        self.assertEqual(failure["classification"], "NUMERICAL_FAILURE")

    def test_terminal_skip_is_persisted_and_honored_on_resume(self) -> None:
        queue = load_queue_module()
        events = EventRecorder()
        original_solver = object()
        replacement_solver = object()

        def terminal_runner(_solver, _events, *, stamp):
            self.assertEqual(stamp, "20260820T000000Z")
            raise queue.TerminalNativeStageError(
                branch="F02",
                stage="carrier-100pct",
                journal_error=RuntimeError("Floating point exception"),
            )

        with tempfile.TemporaryDirectory() as directory:
            ledger = queue.RunLedger.create(Path(directory), stamp="20260820T000000Z")
            with patch.object(queue, "reconnect", return_value=replacement_solver):
                solver, successful, can_continue = queue.guarded_branch(
                    original_solver,
                    events,
                    branch="F02",
                    runner=terminal_runner,
                    stamp="20260820T000000Z",
                    ledger=ledger,
                )

            self.assertIs(solver, replacement_solver)
            self.assertFalse(successful)
            self.assertTrue(can_continue)
            self.assertEqual(queue.RunLedger.load(Path(directory)).branch_status("F02"), "skipped")

            def unexpected_runner(_solver, _events, *, stamp):
                raise AssertionError(f"skipped branch was replayed at {stamp}")

            solver, successful, can_continue = queue.guarded_branch(
                replacement_solver,
                events,
                branch="F02",
                runner=unexpected_runner,
                stamp="20260820T000000Z",
                ledger=queue.RunLedger.load(Path(directory)),
            )
            self.assertIs(solver, replacement_solver)
            self.assertFalse(successful)
            self.assertTrue(can_continue)

    def test_idle_preflight_rejects_observed_progress(self) -> None:
        queue = load_queue_module()
        events = EventRecorder()
        snapshots = [
            {"health": {"status": "Status.SERVING"}, "progress": {"iteration": 10}, "runtime": {"flow_time": 0.0}},
            {"health": {"status": "Status.SERVING"}, "progress": {"iteration": 11}, "runtime": {"flow_time": 0.0}},
        ]
        with patch.object(queue, "collect_snapshot", side_effect=snapshots), patch.object(queue.time, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "iteration changed"):
                queue.idle_preflight(object(), events)


if __name__ == "__main__":
    unittest.main()
