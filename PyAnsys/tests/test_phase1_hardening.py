from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.host_worker import HostWorkerConfig  # noqa: E402
from pyansys_fluent.job_protocol import HealthStageContext, JobSpec  # noqa: E402
from pyansys_fluent.phase1_hardening import (  # noqa: E402
    ClaimedControlRequest,
    ControlledFluentHostWorker,
    FreshClientCheckpointVerifier,
    GenerationControlSpool,
    GenerationTerminationRequest,
    ReopenVerifiedResumableRunStageClient,
)
from pyansys_fluent.resumable_run import (  # noqa: E402
    AtomicRunStateStore,
    FluentRunOperations,
)

NOW = "2026-07-24T12:00:00.000Z"


class FakeSession:
    def __init__(self) -> None:
        self.exit_calls: list[dict[str, object]] = []

    def is_active(self) -> bool:
        return True

    def get_fluent_version(self) -> str:
        return "25.2.0"

    def exit(self, **kwargs) -> None:
        self.exit_calls.append(kwargs)


class RecordingOperations(FluentRunOperations):
    def __init__(self) -> None:
        self.read_case_paths: list[Path] = []
        self.read_data_paths: list[Path] = []
        self.write_case_paths: list[Path] = []
        self.write_data_paths: list[Path] = []
        self.initialize_calls = 0
        self.iterate_calls: list[int] = []

    def read_case(self, _session, path: Path) -> None:
        self.read_case_paths.append(path)

    def read_data(self, _session, path: Path) -> None:
        self.read_data_paths.append(path)

    def hybrid_initialize(self, _session) -> None:
        self.initialize_calls += 1

    def iterate(self, _session, count: int) -> None:
        self.iterate_calls.append(count)

    def write_case(self, _session, path: Path) -> None:
        self.write_case_paths.append(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"case")

    def write_data(self, _session, path: Path) -> None:
        self.write_data_paths.append(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"data")


class FakeProcess:
    def __init__(self) -> None:
        self.returncode = None
        self.pid = 321

    def poll(self):
        return self.returncode


class FakeProcessManager:
    def __init__(self) -> None:
        self.stop_calls = 0

    def stop(self, managed) -> None:
        self.stop_calls += 1
        managed.process.returncode = 1


class FakeJobProcessor:
    def process_next(self, _context):
        return None


class Phase1HardeningTests(unittest.TestCase):
    def test_control_spool_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spool = GenerationControlSpool(root)
            request = GenerationTerminationRequest(
                request_id="terminate-live-001",
                expected_worker_boot_id="boot-1",
                expected_fluent_generation=2,
                submitted_at=NOW,
            )
            incoming = spool.submit(request)
            self.assertTrue(incoming.is_file())
            claim = spool.claim_next("boot-1")
            self.assertIsNotNone(claim)
            assert claim is not None
            self.assertEqual(claim.request, request)
            receipt = {
                "schema_version": 1,
                "request_id": request.request_id,
                "action": request.action,
                "status": "success",
                "termination_observed": True,
            }
            receipt_path = spool.finish(claim, receipt)
            self.assertEqual(
                json.loads(receipt_path.read_text(encoding="utf-8")),
                receipt,
            )
            self.assertTrue((spool.completed_dir / incoming.name).is_file())

    def test_worker_control_rejects_wrong_boot_without_stopping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manager = FakeProcessManager()
            worker = ControlledFluentHostWorker(
                HostWorkerConfig(fluent_exe=root / "fluent.exe", work_dir=root),
                process_manager=manager,
                job_processor=FakeJobProcessor(),
            )
            managed = SimpleNamespace(
                process=FakeProcess(),
                generation=1,
                pid=321,
                server_info_path=root / "fluent-server-info-001.txt",
                process_tree_token=object(),
            )
            request = GenerationTerminationRequest(
                request_id="wrong-boot",
                expected_worker_boot_id="different-boot",
                expected_fluent_generation=1,
                submitted_at=NOW,
            )
            path = root / "control" / "running" / "wrong-boot.json"
            path.parent.mkdir(parents=True)
            path.write_text("{}", encoding="utf-8")
            worker._handle_control_claim(
                ClaimedControlRequest(path, "wrong-boot.json", request),
                managed,
            )
            self.assertEqual(manager.stop_calls, 0)
            receipt = json.loads(
                (root / "control" / "receipts" / "wrong-boot.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(receipt["status"], "failed")
            self.assertFalse(receipt["termination_requested"])

    def test_worker_control_terminates_owned_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manager = FakeProcessManager()
            worker = ControlledFluentHostWorker(
                HostWorkerConfig(fluent_exe=root / "fluent.exe", work_dir=root),
                process_manager=manager,
                job_processor=FakeJobProcessor(),
            )
            managed = SimpleNamespace(
                process=FakeProcess(),
                generation=3,
                pid=321,
                server_info_path=root / "fluent-server-info-003.txt",
                process_tree_token=object(),
            )
            request = GenerationTerminationRequest(
                request_id="terminate-owned",
                expected_worker_boot_id=worker._boot_id,
                expected_fluent_generation=3,
                submitted_at=NOW,
            )
            path = root / "control" / "running" / "terminate-owned.json"
            path.parent.mkdir(parents=True)
            path.write_text("{}", encoding="utf-8")
            worker._handle_control_claim(
                ClaimedControlRequest(path, "terminate-owned.json", request),
                managed,
            )
            self.assertEqual(manager.stop_calls, 1)
            receipt = json.loads(
                (root / "control" / "receipts" / "terminate-owned.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(receipt["status"], "success")
            self.assertTrue(receipt["termination_requested"])
            self.assertTrue(receipt["termination_observed"])

    def test_fresh_client_reopen_reads_case_and_data_without_running(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case_path = root / "candidate.cas.h5"
            data_path = root / "candidate.dat.h5"
            case_path.write_bytes(b"case")
            data_path.write_bytes(b"data")
            operations = RecordingOperations()
            session = FakeSession()
            verifier = FreshClientCheckpointVerifier(
                operations=operations,
                timestamp_factory=lambda: NOW,
            )
            context = HealthStageContext(
                worker_boot_id="boot",
                fluent_generation=2,
                fluent_pid=456,
                server_info_path=root / "server-info.txt",
                config=HostWorkerConfig(
                    fluent_exe=root / "fluent.exe",
                    work_dir=root,
                    health_timeout_seconds=0.1,
                ),
                process_is_alive=lambda: True,
            )
            evidence = verifier.verify(
                case_path=case_path,
                data_path=data_path,
                context=context,
                connect_factory=lambda _path, _config: session,
                call=lambda _label, callback: callback(),
            )
            self.assertEqual(operations.read_case_paths, [case_path])
            self.assertEqual(operations.read_data_paths, [data_path])
            self.assertEqual(operations.initialize_calls, 0)
            self.assertEqual(operations.iterate_calls, [])
            self.assertTrue(evidence["verified"])
            self.assertTrue(evidence["data_loaded"])
            self.assertTrue(evidence["client_detached"])

    def test_checkpoint_is_committed_only_after_reopen_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = (root / "source.cas.h5").resolve()
            source.write_bytes(b"source")
            spec = JobSpec(
                job_id="verified-checkpoint",
                stage_type="resumable_run",
                submitted_at=NOW,
                timeout_seconds=30,
                expected_worker_boot_id="boot",
                expected_fluent_generation=1,
                case_path=str(source),
                total_iterations=25,
                chunk_iterations=25,
                command_timeout_seconds=10,
                max_resume_attempts=2,
            )
            state = {
                "schema_version": 1,
                "job_id": spec.job_id,
                "status": "running",
                "worker_boot_id": "boot",
                "initial_fluent_generation": 1,
                "requested_case_path": str(source),
                "resolved_case_path": str(source),
                "disposable_case_path": str(source),
                "source_file_size_bytes": source.stat().st_size,
                "source_sha256": None,
                "total_iterations": 25,
                "completed_iterations": 0,
                "initialization_count": 1,
                "resume_count": 0,
                "attempts": [],
                "last_checkpoint": None,
                "started_at": NOW,
                "updated_at": NOW,
            }
            operations = RecordingOperations()
            session = FakeSession()
            client = ReopenVerifiedResumableRunStageClient(
                operations=operations,
                connect_factory=lambda _path, _config: FakeSession(),
                timestamp_factory=lambda: NOW,
            )
            context = HealthStageContext(
                worker_boot_id="boot",
                fluent_generation=1,
                fluent_pid=456,
                server_info_path=root / "server-info.txt",
                config=HostWorkerConfig(
                    fluent_exe=root / "fluent.exe",
                    work_dir=root,
                    health_timeout_seconds=0.1,
                ),
                process_is_alive=lambda: True,
            )
            store = AtomicRunStateStore(root / "run-state.json")
            client._write_and_commit_checkpoint(
                spec,
                state,
                store,
                session,
                context,
                attempt_index=1,
                iteration=25,
                call=lambda _label, callback: callback(),
            )
            committed = store.load(spec=spec)
            assert committed is not None
            self.assertEqual(committed["completed_iterations"], 25)
            verification = committed["last_checkpoint"]["verification"]
            self.assertTrue(verification["verified"])
            self.assertTrue(verification["data_loaded"])
            self.assertEqual(operations.initialize_calls, 0)
            self.assertEqual(operations.iterate_calls, [])


if __name__ == "__main__":
    unittest.main()
