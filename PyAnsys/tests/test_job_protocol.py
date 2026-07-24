from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.host_worker import (  # noqa: E402
    HostWorkerConfig,
    connect_from_server_info,
)
from pyansys_fluent.job_protocol import (  # noqa: E402
    FilesystemJobSpool,
    HealthCheckStageClient,
    HealthStageContext,
    JobSpec,
    JobStageProcessor,
    JobState,
    ProtocolValidationError,
    ReceiptCommitError,
    StageReceipt,
)


NOW = "2026-07-24T12:00:00.000Z"


class FakeSession:
    def __init__(
        self,
        *,
        active: bool = True,
        fluent_version: str = "25.2.0",
        process: "FakeOwnedProcess | None" = None,
    ) -> None:
        self.active = active
        self.fluent_version = fluent_version
        self.process = process
        self.exit_calls: list[dict[str, object]] = []

    def is_active(self) -> bool:
        return self.active

    def get_fluent_version(self) -> str:
        return self.fluent_version

    def exit(self, **kwargs) -> None:
        self.exit_calls.append(kwargs)
        # cleanup_on_exit=False means this detaches the client. A fake stage
        # client must never mutate the supervisor-owned process state.


class FakeOwnedProcess:
    def __init__(self) -> None:
        self.alive = True


def make_config(root: Path) -> HostWorkerConfig:
    return HostWorkerConfig(
        fluent_exe=root / "fluent.exe",
        work_dir=root,
        health_timeout_seconds=0.1,
    )


def make_context(
    root: Path,
    *,
    generation: int = 2,
    process: FakeOwnedProcess | None = None,
) -> HealthStageContext:
    owned = process or FakeOwnedProcess()
    return HealthStageContext(
        worker_boot_id="boot-abc",
        fluent_generation=generation,
        fluent_pid=25200,
        server_info_path=root / "fluent-server-info-002.txt",
        config=make_config(root),
        process_is_alive=lambda: owned.alive,
    )


def success_receipt(job_id: str = "health-001") -> StageReceipt:
    return StageReceipt(
        job_id=job_id,
        stage_type="health_check",
        status="success",
        worker_boot_id="boot-abc",
        fluent_generation=2,
        fluent_pid=25200,
        fluent_version="25.2.0",
        pyfluent_version="0.40.2",
        started_at=NOW,
        completed_at=NOW,
        observed_health_result=True,
        client_detached=True,
        fluent_process_alive_after_detach=True,
    )


class SchemaValidationTests(unittest.TestCase):
    def test_models_round_trip(self) -> None:
        spec = JobSpec(
            job_id="health-001",
            submitted_at=NOW,
            expected_worker_boot_id="boot-abc",
            expected_fluent_generation=2,
        )
        self.assertEqual(JobSpec.from_dict(spec.to_dict()), spec)

        receipt = success_receipt()
        self.assertEqual(StageReceipt.from_dict(receipt.to_dict()), receipt)

        state = JobState(
            job_id=spec.job_id,
            status="completed",
            updated_at=NOW,
            worker_boot_id="boot-abc",
            fluent_generation=2,
            fluent_pid=25200,
            receipt_path="receipts/health-001.json",
        )
        self.assertEqual(JobState.from_dict(state.to_dict()), state)

    def test_rejects_unknown_schema_and_unsafe_job_id(self) -> None:
        payload = JobSpec(job_id="valid", submitted_at=NOW).to_dict()
        payload["schema_version"] = 99
        with self.assertRaises(ProtocolValidationError):
            JobSpec.from_dict(payload)
        with self.assertRaises(ProtocolValidationError):
            JobSpec(job_id="../escape", submitted_at=NOW).validate()

    def test_success_receipt_requires_health_versions_and_detachment(self) -> None:
        payload = success_receipt().to_dict()
        payload["client_detached"] = False
        with self.assertRaises(ProtocolValidationError):
            StageReceipt.from_dict(payload)


class FilesystemSpoolTests(unittest.TestCase):
    def test_layout_and_atomic_job_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spool = FilesystemJobSpool(Path(tmp))
            submitted = spool.submit(JobSpec(job_id="health-claim", submitted_at=NOW))
            self.assertTrue(submitted.is_file())

            claim = spool.claim_next("worker-one")
            self.assertIsNotNone(claim)
            assert claim is not None
            self.assertEqual(claim.spec.job_id, "health-claim")
            self.assertFalse(submitted.exists())
            self.assertEqual(claim.path.parent, spool.running_dir)

    def test_two_workers_cannot_claim_same_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = FilesystemJobSpool(root)
            second = FilesystemJobSpool(root)
            first.submit(JobSpec(job_id="health-race", submitted_at=NOW))
            barrier = threading.Barrier(3)
            claims: list[object] = []

            def claim(spool: FilesystemJobSpool, boot_id: str) -> None:
                barrier.wait()
                claims.append(spool.claim_next(boot_id))

            threads = [
                threading.Thread(target=claim, args=(first, "worker-one")),
                threading.Thread(target=claim, args=(second, "worker-two")),
            ]
            for thread in threads:
                thread.start()
            barrier.wait()
            for thread in threads:
                thread.join(timeout=2)

            self.assertEqual(sum(item is not None for item in claims), 1)
            self.assertEqual(len(list(first.running_dir.glob("*.json"))), 1)

    def test_receipt_commit_is_atomic_and_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spool = FilesystemJobSpool(Path(tmp))
            path = spool.commit_receipt(success_receipt())

            committed = StageReceipt.from_dict(
                json.loads(path.read_text(encoding="utf-8"))
            )
            self.assertEqual(committed.status, "success")
            self.assertFalse(
                any(".tmp-" in item.name for item in spool.receipts_dir.iterdir())
            )

    def test_job_cannot_complete_without_committed_valid_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spool = FilesystemJobSpool(Path(tmp))
            spec = JobSpec(job_id="health-no-receipt", submitted_at=NOW)
            spool.submit(spec)
            claim = spool.claim_next("worker-one")
            assert claim is not None
            state = JobState(
                job_id=spec.job_id,
                status="completed",
                updated_at=NOW,
                worker_boot_id="worker-one",
                fluent_generation=1,
                fluent_pid=1001,
                receipt_path=str(spool.receipts_dir / f"{spec.job_id}.json"),
            )

            with self.assertRaises(ReceiptCommitError):
                spool.finish(
                    claim,
                    spec=spec,
                    state=state,
                    receipt_path=spool.receipts_dir / f"{spec.job_id}.json",
                )
            self.assertTrue(claim.path.is_file())
            self.assertFalse(any(spool.completed_dir.iterdir()))


class HealthStageTests(unittest.TestCase):
    def test_successful_health_stage_records_versions_and_detaches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            process = FakeOwnedProcess()
            session = FakeSession(process=process)
            client = HealthCheckStageClient(
                connect_factory=lambda _path, _config: session,
                pyfluent_version_factory=lambda: "0.40.2",
                timestamp_factory=lambda: NOW,
            )
            receipt = client.execute(
                JobSpec(
                    job_id="health-success",
                    submitted_at=NOW,
                    expected_worker_boot_id="boot-abc",
                    expected_fluent_generation=2,
                ),
                make_context(root, process=process),
            )

            self.assertEqual(receipt.status, "success")
            self.assertEqual(receipt.fluent_version, "25.2.0")
            self.assertEqual(receipt.pyfluent_version, "0.40.2")
            self.assertTrue(receipt.observed_health_result)
            self.assertTrue(receipt.client_detached)
            self.assertTrue(process.alive)
            self.assertEqual(len(session.exit_calls), 1)
            self.assertEqual(
                session.exit_calls[0],
                {"timeout": 0.1, "timeout_force": False, "wait": False},
            )

    def test_inactive_health_stage_fails_and_detaches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = FakeSession(active=False)
            client = HealthCheckStageClient(
                connect_factory=lambda _path, _config: session,
                pyfluent_version_factory=lambda: "0.40.2",
                timestamp_factory=lambda: NOW,
            )
            receipt = client.execute(
                JobSpec(job_id="health-inactive", submitted_at=NOW),
                make_context(root),
            )

            self.assertEqual(receipt.status, "failed")
            self.assertFalse(receipt.observed_health_result)
            self.assertEqual(receipt.error["type"], "RuntimeError")
            self.assertEqual(len(session.exit_calls), 1)

    def test_stage_timeout_is_failed_not_successful(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            release = threading.Event()

            class BlockingSession(FakeSession):
                def is_active(self) -> bool:
                    release.wait()
                    return True

            session = BlockingSession()
            client = HealthCheckStageClient(
                connect_factory=lambda _path, _config: session,
                pyfluent_version_factory=lambda: "0.40.2",
                timestamp_factory=lambda: NOW,
            )
            receipt = client.execute(
                JobSpec(
                    job_id="health-timeout",
                    submitted_at=NOW,
                    timeout_seconds=0.02,
                ),
                make_context(root),
            )
            release.set()

            self.assertEqual(receipt.status, "failed")
            self.assertEqual(receipt.error["type"], "TimeoutError")
            self.assertTrue(receipt.error["retryable"])

    def test_generation_mismatch_fails_without_connecting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            connected = []
            client = HealthCheckStageClient(
                connect_factory=lambda _path, _config: connected.append(True),
                pyfluent_version_factory=lambda: "0.40.2",
                timestamp_factory=lambda: NOW,
            )
            receipt = client.execute(
                JobSpec(
                    job_id="health-stale",
                    submitted_at=NOW,
                    expected_fluent_generation=1,
                ),
                make_context(Path(tmp), generation=2),
            )

            self.assertEqual(receipt.status, "failed")
            self.assertIn("generation mismatch", receipt.error["message"].lower())
            self.assertEqual(connected, [])
            self.assertEqual(receipt.fluent_generation, 2)

    def test_cleanup_disabled_connector_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = make_config(root)
            with mock.patch(
                "ansys.fluent.core.connect_to_fluent",
                return_value=object(),
            ) as connect:
                connect_from_server_info(root / "server-info.txt", config)

            kwargs = connect.call_args.kwargs
            self.assertIs(kwargs["cleanup_on_exit"], False)
            self.assertIs(kwargs["start_watchdog"], False)


class ProcessorTests(unittest.TestCase):
    def test_success_moves_job_only_after_receipt_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spool = FilesystemJobSpool(root)
            spec = JobSpec(job_id="health-processor", submitted_at=NOW)
            spool.submit(spec)
            session = FakeSession()
            processor = JobStageProcessor(
                spool,
                health_client=HealthCheckStageClient(
                    connect_factory=lambda _path, _config: session,
                    pyfluent_version_factory=lambda: "0.40.2",
                    timestamp_factory=lambda: NOW,
                ),
                timestamp_factory=lambda: NOW,
            )

            state = processor.process_next(make_context(root))

            self.assertEqual(state.status, "completed")
            self.assertTrue(
                (spool.completed_dir / f"{spec.job_id}.json").is_file()
            )
            self.assertTrue((spool.receipts_dir / f"{spec.job_id}.json").is_file())
            self.assertFalse(any(spool.running_dir.iterdir()))

    def test_failed_health_stage_moves_job_to_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spool = FilesystemJobSpool(root)
            spec = JobSpec(job_id="health-failed", submitted_at=NOW)
            spool.submit(spec)
            processor = JobStageProcessor(
                spool,
                health_client=HealthCheckStageClient(
                    connect_factory=lambda _path, _config: FakeSession(active=False),
                    pyfluent_version_factory=lambda: "0.40.2",
                    timestamp_factory=lambda: NOW,
                ),
                timestamp_factory=lambda: NOW,
            )

            state = processor.process_next(make_context(root))

            self.assertEqual(state.status, "failed")
            self.assertTrue((spool.failed_dir / f"{spec.job_id}.json").is_file())
            receipt = StageReceipt.from_dict(
                json.loads(
                    (spool.receipts_dir / f"{spec.job_id}.json").read_text(
                        encoding="utf-8"
                    )
                )
            )
            self.assertEqual(receipt.fluent_generation, 2)
            self.assertEqual(receipt.fluent_pid, 25200)

    def test_malformed_job_is_quarantined_with_failure_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spool = FilesystemJobSpool(root)
            spool.ensure_layout()
            (spool.incoming_dir / "bad-job.json").write_text(
                "{not-json",
                encoding="utf-8",
            )
            processor = JobStageProcessor(
                spool,
                timestamp_factory=lambda: NOW,
            )

            state = processor.process_next(make_context(root))

            self.assertEqual(state.status, "failed")
            self.assertTrue((spool.failed_dir / "bad-job.json").is_file())
            receipt = StageReceipt.from_dict(
                json.loads(
                    (spool.receipts_dir / "bad-job.json").read_text(
                        encoding="utf-8"
                    )
                )
            )
            self.assertEqual(receipt.stage_type, "invalid")
            self.assertFalse(receipt.error["retryable"])

    def test_receipt_commit_failure_never_moves_job_to_completed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            class BrokenReceiptSpool(FilesystemJobSpool):
                def commit_receipt(self, receipt: StageReceipt) -> Path:
                    raise ReceiptCommitError("simulated disk failure")

            spool = BrokenReceiptSpool(root)
            spool.submit(JobSpec(job_id="health-disk-failure", submitted_at=NOW))
            processor = JobStageProcessor(
                spool,
                health_client=HealthCheckStageClient(
                    connect_factory=lambda _path, _config: FakeSession(),
                    pyfluent_version_factory=lambda: "0.40.2",
                    timestamp_factory=lambda: NOW,
                ),
                timestamp_factory=lambda: NOW,
            )

            with self.assertRaises(ReceiptCommitError):
                processor.process_next(make_context(root))

            self.assertFalse(any(spool.completed_dir.iterdir()))
            self.assertEqual(len(list(spool.running_dir.iterdir())), 1)


if __name__ == "__main__":
    unittest.main()
