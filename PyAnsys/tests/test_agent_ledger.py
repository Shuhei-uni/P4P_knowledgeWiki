from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from pyansys_fluent.agent_ledger import AgentLedger


class AgentLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.path = Path(self.temporary_directory.name) / "agent-ledger.json"
        self.ledger = AgentLedger(self.path)
        self.ledger.create(
            job_id="setup-010v2b-build",
            phase="case_build",
            setup_plan_path="/plans/setup.md",
            connection_generation=13,
        )

    def test_step_transitions_preserve_verified_progress(self) -> None:
        started = self.ledger.start_step("enable_dpm", safe_to_retry=True)
        self.assertEqual(started["status"], "executing_step")
        self.assertTrue(started["current_step_safe_to_retry"])

        complete = self.ledger.complete_step("enable_dpm")
        self.assertEqual(complete["status"], "ready")
        self.assertEqual(complete["last_completed_step"], "enable_dpm")
        self.assertEqual(complete["completed_steps"], ["enable_dpm"])
        self.assertIsNone(complete["current_step"])

        with self.assertRaisesRegex(RuntimeError, "already complete"):
            self.ledger.start_step("enable_dpm")

    def test_checkpoint_loss_and_verified_recovery(self) -> None:
        self.ledger.start_step("create_injection_03", safe_to_retry=True)
        checkpointed = self.ledger.accept_checkpoint(
            r"C:\runs\checkpoint_06.cas.h5"
        )
        self.assertEqual(
            checkpointed["latest_case_checkpoint"],
            r"C:\runs\checkpoint_06.cas.h5",
        )
        self.assertIsNone(checkpointed["latest_data_checkpoint"])

        lost = self.ledger.connection_lost(generation=13)
        self.assertEqual(lost["status"], "connection_lost")
        recovered = self.ledger.recovered(
            generation=14,
            restored_state_verified=True,
        )
        self.assertEqual(recovered["status"], "recovered")
        self.assertEqual(recovered["connection_generation"], 14)
        self.assertEqual(recovered["current_step"], "create_injection_03")

    def test_unproven_recovery_requires_human_review(self) -> None:
        self.ledger.connection_lost(generation=13)
        state = self.ledger.recovered(
            generation=14,
            restored_state_verified=False,
        )
        self.assertEqual(state["status"], "human_review")

    def test_generation_cannot_move_backwards(self) -> None:
        self.ledger.connection_lost(generation=13)
        with self.assertRaisesRegex(ValueError, "newer"):
            self.ledger.recovered(generation=13, restored_state_verified=True)
        with self.assertRaisesRegex(ValueError, "backwards"):
            self.ledger.connection_lost(generation=12)

    def test_atomic_replace_leaves_previous_document_on_failure(self) -> None:
        before = self.path.read_text(encoding="utf-8")
        with mock.patch("pyansys_fluent.agent_ledger.os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                self.ledger.start_step("enable_dpm")
        self.assertEqual(self.path.read_text(encoding="utf-8"), before)
        self.assertEqual(list(self.path.parent.glob("*.tmp")), [])

    def test_credentials_are_rejected_before_write(self) -> None:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        payload["password"] = "must-not-persist"
        self.path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "credential field"):
            self.ledger.read()

    def test_create_does_not_overwrite_existing_ledger(self) -> None:
        with self.assertRaises(FileExistsError):
            self.ledger.create(job_id="other", phase="analysis")


if __name__ == "__main__":
    unittest.main()
