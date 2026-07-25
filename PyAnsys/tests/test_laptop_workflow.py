from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from pyansys_fluent.laptop_workflow import (
    LaptopWorkflow,
    LaptopWorkflowError,
)
from pyansys_fluent.run_worker import RunRequest


def _request(
    root: Path,
    *,
    job_id: str,
    generation: int,
    mode: str,
    source_case: str,
    source_data: str | None = None,
    completed: int = 0,
) -> RunRequest:
    return RunRequest.from_dict(
        {
            "schema_version": 2,
            "job_id": job_id,
            "expected_generation": generation,
            "mode": mode,
            "source_case": source_case,
            "source_data": source_data,
            "initialization_tui": (
                ["/solve/initialize/hyb-initialization"]
                if mode == "initialize"
                else None
            ),
            "target_total_iterations": 600,
            "completed_iterations": completed,
            "checkpoint_interval": 250,
            "report_interval": 25,
            "output_directory": str(root / f"{job_id}-output"),
            "overwrite": False,
        }
    )


def _receipt(
    path: Path,
    *,
    job_id: str,
    generation: int,
    status: str,
    iteration: int,
    case_path: str,
    data_path: str,
) -> Path:
    payload = {
        "schema_version": 2,
        "job_id": job_id,
        "status": status,
        "generation": generation,
        "mode": "initialize",
        "started_at": "2026-07-24T00:00:00+00:00",
        "finished_at": "2026-07-24T00:01:00+00:00",
        "target_total_iterations": 600,
        "completed_iterations": iteration,
        "last_checkpoint": {
            "iteration": iteration,
            "case_path": case_path,
            "data_path": data_path,
            "case_size_bytes": 10,
            "data_size_bytes": 20,
            "file_verified": True,
        },
        "final_data_path": data_path if status == "completed" else None,
        "initialization_log": [],
        "error": None,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class LaptopWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.plan = self.root / "setup.md"
        self.plan.write_text(
            "# Setup\n\nAgent-authored Fluent intent.\n", encoding="utf-8"
        )
        self.bridge = self.root / "bridge"
        self._publish_connection(4)
        self.workflow = LaptopWorkflow(self.root / "workflow")

    def _publish_connection(self, generation: int) -> None:
        self.bridge.mkdir(parents=True, exist_ok=True)
        (self.bridge / "latest_connection.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "generation": generation,
                    "previous_generation": generation - 1,
                    "status": "running",
                    "host": "10.0.0.5",
                    "port": 51000 + generation,
                    "password": "test-only-password",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "heartbeat_sequence": generation,
                }
            ),
            encoding="utf-8",
        )

    def _build_case(self) -> str:
        self.workflow.create(
            job_id="setup-build",
            setup_plan_path=self.plan,
            connection_generation=4,
            analysis_tasks=("flux", "residual"),
        )
        self.workflow.start_step("load_parent")
        self.workflow.complete_step("load_parent")
        self.workflow.start_step("enable_models", safe_to_retry=True)
        self.workflow.complete_step("enable_models")
        case_path = str(self.root / "verified.cas.h5")
        self.workflow.accept_case_checkpoint(case_path)
        self.workflow.mark_case_ready()
        return case_path

    def test_plan_to_completed_result_manifest(self) -> None:
        case_path = self._build_case()
        request = _request(
            self.root,
            job_id="run-600",
            generation=4,
            mode="initialize",
            source_case=case_path,
        )
        submitted = self.workflow.submit(request, bridge_dir=self.bridge)
        self.assertTrue(submitted.is_file())

        final_case = str(self.root / "final-600.cas.h5")
        final_data = str(self.root / "final-600.dat.h5")
        receipt = _receipt(
            self.root / "completed.json",
            job_id="run-600",
            generation=4,
            status="completed",
            iteration=600,
            case_path=final_case,
            data_path=final_data,
        )
        state = self.workflow.ingest_receipt(receipt)
        self.assertEqual(
            "run_completed_pending_verification", state["status"]
        )
        self.assertIsNone(
            self.workflow.ledger.read()["latest_data_checkpoint"]
        )

        state = self.workflow.verify_pending_checkpoint(
            case_path=final_case,
            data_path=final_data,
            generation=4,
        )
        self.assertEqual("analysis_ready", state["status"])

        flux = self.root / "flux.json"
        residual = self.root / "residual.png"
        flux.write_text('{"flux": 1}', encoding="utf-8")
        residual.write_bytes(b"png")
        self.workflow.start_analysis_task("flux")
        self.workflow.complete_analysis_task(
            "flux", artifacts=(flux,), notes="Read back from final pair."
        )
        self.workflow.start_analysis_task("residual")
        self.workflow.complete_analysis_task(
            "residual", artifacts=(residual,)
        )
        manifest_path, summary_path = self.workflow.finalize()

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual("setup-build", manifest["job_id"])
        self.assertEqual(final_data, manifest["final_checkpoint"]["data_path"])
        self.assertEqual(
            64, len(manifest["setup_plan"]["sha256"])
        )
        self.assertEqual(
            64,
            len(
                manifest["analysis"]["tasks"]["flux"]["artifacts"][0][
                    "sha256"
                ]
            ),
        )
        self.assertTrue(summary_path.is_file())
        self.assertEqual("complete", self.workflow.read()["status"])
        self.assertNotIn(
            "password",
            json.dumps(manifest).lower(),
        )

    def test_interrupted_pair_requires_new_generation_and_explicit_resume(self) -> None:
        case_path = self._build_case()
        initial = _request(
            self.root,
            job_id="run-initial",
            generation=4,
            mode="initialize",
            source_case=case_path,
        )
        self.workflow.submit(initial, bridge_dir=self.bridge)
        checkpoint_case = str(self.root / "checkpoint-250.cas.h5")
        checkpoint_data = str(self.root / "checkpoint-250.dat.h5")
        receipt = _receipt(
            self.root / "interrupted.json",
            job_id="run-initial",
            generation=4,
            status="interrupted",
            iteration=250,
            case_path=checkpoint_case,
            data_path=checkpoint_data,
        )
        state = self.workflow.ingest_receipt(receipt)
        self.assertEqual("recovery_required", state["status"])
        self.assertEqual(
            case_path,
            self.workflow.ledger.read()["latest_case_checkpoint"],
        )

        with self.assertRaises(ValueError):
            self.workflow.verify_pending_checkpoint(
                case_path=checkpoint_case,
                data_path=checkpoint_data,
                generation=4,
            )
        state = self.workflow.verify_pending_checkpoint(
            case_path=checkpoint_case,
            data_path=checkpoint_data,
            generation=5,
        )
        self.assertEqual("recovery_verified", state["status"])
        self._publish_connection(5)

        wrong_resume = _request(
            self.root,
            job_id="run-resume-wrong",
            generation=5,
            mode="resume",
            source_case=checkpoint_case,
            source_data=checkpoint_data,
            completed=200,
        )
        with self.assertRaises(LaptopWorkflowError):
            self.workflow.submit(wrong_resume, bridge_dir=self.bridge)

        resume = _request(
            self.root,
            job_id="run-resume",
            generation=5,
            mode="resume",
            source_case=checkpoint_case,
            source_data=checkpoint_data,
            completed=250,
        )
        resume_path = self.workflow.submit(resume, bridge_dir=self.bridge)
        self.assertTrue(resume_path.is_file())
        self.assertEqual("resume", json.loads(resume_path.read_text())["mode"])

    def test_does_not_parse_or_rewrite_setup_markdown(self) -> None:
        original = self.plan.read_bytes()
        state = self.workflow.create(
            job_id="opaque-plan",
            setup_plan_path=self.plan,
        )
        self.assertEqual(original, self.plan.read_bytes())
        self.assertEqual(64, len(state["setup_plan_sha256"]))

    def test_changed_setup_plan_blocks_further_execution(self) -> None:
        self.workflow.create(
            job_id="plan-drift",
            setup_plan_path=self.plan,
        )
        self.plan.write_text("# Changed setup\n", encoding="utf-8")
        with self.assertRaisesRegex(
            LaptopWorkflowError, "Setup plan changed"
        ):
            self.workflow.start_step("load_parent")

    def test_stale_run_generation_is_rejected_before_submission(self) -> None:
        case_path = self._build_case()
        self._publish_connection(5)
        request = _request(
            self.root,
            job_id="stale-run",
            generation=4,
            mode="initialize",
            source_case=case_path,
        )
        with self.assertRaisesRegex(
            LaptopWorkflowError, "stale Fluent generation"
        ):
            self.workflow.submit(request, bridge_dir=self.bridge)
        self.assertFalse(
            (self.bridge / "run_requests" / "incoming").exists()
        )

    def test_unproven_recovery_stops_for_human_review(self) -> None:
        case_path = self._build_case()
        request = _request(
            self.root,
            job_id="review-run",
            generation=4,
            mode="initialize",
            source_case=case_path,
        )
        self.workflow.submit(request, bridge_dir=self.bridge)
        receipt = _receipt(
            self.root / "review-interrupted.json",
            job_id="review-run",
            generation=4,
            status="interrupted",
            iteration=250,
            case_path=str(self.root / "review-250.cas.h5"),
            data_path=str(self.root / "review-250.dat.h5"),
        )
        self.workflow.ingest_receipt(receipt)
        state = self.workflow.require_human_review(
            generation=5,
            reason="Restored model state did not match the last verified step.",
        )
        self.assertEqual("human_review", state["status"])
        self.assertEqual(
            "human_review", self.workflow.ledger.read()["status"]
        )

    def test_setup_crash_restores_checkpoint_and_preserves_interrupted_step(self) -> None:
        self.workflow.create(
            job_id="setup-recovery",
            setup_plan_path=self.plan,
            connection_generation=4,
        )
        checkpoint = str(self.root / "models-enabled.cas.h5")
        self.workflow.accept_case_checkpoint(checkpoint)
        self.workflow.start_step(
            "create_injection_03", safe_to_retry=True
        )
        state = self.workflow.record_setup_connection_loss(generation=4)
        self.assertEqual("setup_recovery_required", state["status"])
        self.assertEqual(
            "create_injection_03",
            state["pending_checkpoint"]["interrupted_step"],
        )
        state = self.workflow.verify_setup_recovery(generation=5)
        self.assertEqual("case_build", state["status"])
        ledger = self.workflow.ledger.read()
        self.assertEqual("create_injection_03", ledger["current_step"])
        self.assertTrue(ledger["current_step_safe_to_retry"])
        self.workflow.complete_step("create_injection_03")

    def test_unsafe_interrupted_setup_step_requires_human_review(self) -> None:
        self.workflow.create(
            job_id="unsafe-setup-recovery",
            setup_plan_path=self.plan,
            connection_generation=4,
        )
        self.workflow.accept_case_checkpoint(
            str(self.root / "accepted.cas.h5")
        )
        self.workflow.start_step("unknown_partial_mutation")
        self.workflow.record_setup_connection_loss(generation=4)
        with self.assertRaisesRegex(
            LaptopWorkflowError, "not explicitly safe to retry"
        ):
            self.workflow.verify_setup_recovery(generation=5)
        state = self.workflow.require_human_review(
            generation=5,
            reason="Interrupted mutation is not safe to replay.",
        )
        self.assertEqual("human_review", state["status"])

    def test_finalize_requires_explicit_analysis_tasks(self) -> None:
        self._build_case()
        with self.assertRaises(LaptopWorkflowError):
            self.workflow.finalize()


if __name__ == "__main__":
    unittest.main()
