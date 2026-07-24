from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.host_worker import (  # noqa: E402
    FluentGenerationRetryRequested,
    HostWorkerConfig,
)
from pyansys_fluent.job_protocol import (  # noqa: E402
    FilesystemJobSpool,
    HealthStageContext,
    JobSpec,
    JobStageProcessor,
    ProtocolValidationError,
    StageReceipt,
)
from pyansys_fluent.resumable_run import (  # noqa: E402
    AtomicRunStateStore,
    CheckpointVerificationError,
    FluentRunOperations,
    ResumableRunStageClient,
    RunStateValidationError,
    verify_checkpoint_pair,
)


NOW = "2026-07-24T12:00:00.000Z"


class FakeOwnedProcess:
    def __init__(self) -> None:
        self.alive = True


class FakeSession:
    def __init__(self) -> None:
        self.exit_calls: list[dict[str, object]] = []

    def is_active(self) -> bool:
        return True

    def get_fluent_version(self) -> str:
        return "25.2.0"

    def exit(self, **kwargs) -> None:
        self.exit_calls.append(kwargs)


class FakeRunOperations(FluentRunOperations):
    def __init__(
        self,
        process: FakeOwnedProcess,
        *,
        fail_iterate_calls: set[int] | None = None,
        failure: BaseException | None = None,
    ) -> None:
        self.process = process
        self.fail_iterate_calls = set(fail_iterate_calls or set())
        self.failure = failure or ConnectionError("simulated Fluent loss")
        self.read_case_paths: list[Path] = []
        self.read_data_paths: list[Path] = []
        self.initialize_calls = 0
        self.iterate_calls: list[int] = []
        self.write_case_paths: list[Path] = []
        self.write_data_paths: list[Path] = []

    def read_case(self, _session, path: Path) -> None:
        self.read_case_paths.append(path)

    def read_data(self, _session, path: Path) -> None:
        self.read_data_paths.append(path)

    def hybrid_initialize(self, _session) -> None:
        self.initialize_calls += 1

    def iterate(self, _session, count: int) -> None:
        call_number = len(self.iterate_calls) + 1
        self.iterate_calls.append(count)
        if call_number in self.fail_iterate_calls:
            self.process.alive = False
            raise self.failure

    def write_case(self, _session, path: Path) -> None:
        self.write_case_paths.append(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"case:{path.name}".encode())

    def write_data(self, _session, path: Path) -> None:
        self.write_data_paths.append(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"data:{path.name}".encode())


def write_source_case(root: Path) -> Path:
    path = (root / "source.cas.h5").resolve()
    path.write_bytes(b"immutable-source-case")
    return path


def make_config(root: Path) -> HostWorkerConfig:
    return HostWorkerConfig(
        fluent_exe=root / "fluent.exe",
        work_dir=root,
        health_timeout_seconds=0.1,
        poll_interval_seconds=0.001,
    )


def make_context(
    root: Path,
    process: FakeOwnedProcess,
    *,
    generation: int,
) -> HealthStageContext:
    return HealthStageContext(
        worker_boot_id="boot-run",
        fluent_generation=generation,
        fluent_pid=25000 + generation,
        server_info_path=root / f"fluent-server-info-{generation:03d}.txt",
        config=make_config(root),
        process_is_alive=lambda: process.alive,
    )


def make_spec(source: Path, **overrides) -> JobSpec:
    values = {
        "job_id": "run-live-001",
        "stage_type": "resumable_run",
        "submitted_at": NOW,
        "timeout_seconds": 2.0,
        "expected_worker_boot_id": "boot-run",
        "expected_fluent_generation": 1,
        "case_path": str(source),
        "compute_sha256": True,
        "total_iterations": 10,
        "chunk_iterations": 5,
        "command_timeout_seconds": 1.0,
        "max_resume_attempts": 2,
    }
    values.update(overrides)
    return JobSpec(**values)


def make_client(
    process: FakeOwnedProcess,
    operations: FakeRunOperations,
    sessions: list[FakeSession],
) -> ResumableRunStageClient:
    return ResumableRunStageClient(
        connect_factory=lambda _path, _config: sessions.pop(0),
        pyfluent_version_factory=lambda: "0.40.2",
        operations=operations,
        timestamp_factory=lambda: NOW,
    )


class ResumableRunSchemaTests(unittest.TestCase):
    def test_valid_job_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = make_spec(write_source_case(Path(tmp)))
            self.assertEqual(JobSpec.from_dict(spec.to_dict()), spec)

    def test_rejects_relative_case_and_incomplete_policy(self) -> None:
        with self.assertRaises(ProtocolValidationError):
            make_spec(Path("relative.cas.h5")).validate()
        with tempfile.TemporaryDirectory() as tmp:
            source = write_source_case(Path(tmp))
            with self.assertRaises(ProtocolValidationError):
                make_spec(source, total_iterations=None).validate()
            with self.assertRaises(ProtocolValidationError):
                make_spec(
                    source,
                    total_iterations=5,
                    chunk_iterations=10,
                ).validate()

    def test_run_state_store_rejects_partial_or_non_monotonic_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_spec(write_source_case(root))
            store = AtomicRunStateStore(root / "run-state.json")
            invalid = {
                "schema_version": 1,
                "job_id": spec.job_id,
                "status": "running",
                "worker_boot_id": "boot-run",
                "requested_case_path": spec.case_path,
                "resolved_case_path": spec.case_path,
                "disposable_case_path": spec.case_path,
                "total_iterations": 10,
                "completed_iterations": 5,
                "initialization_count": 1,
                "resume_count": 0,
                "attempts": [],
                "last_checkpoint": None,
                "started_at": NOW,
                "updated_at": NOW,
            }
            with self.assertRaises(RunStateValidationError):
                store.commit(invalid, spec=spec)


class CheckpointVerificationTests(unittest.TestCase):
    def test_pair_requires_both_nonempty_stable_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case_path = root / "checkpoint.cas.h5"
            data_path = root / "checkpoint.dat.h5"
            case_path.write_bytes(b"case")
            data_path.write_bytes(b"data")
            self.assertEqual(
                verify_checkpoint_pair(
                    case_path,
                    data_path,
                    timeout_seconds=0.1,
                    poll_seconds=0.001,
                ),
                (4, 4),
            )

    def test_missing_data_is_never_verified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case_path = root / "checkpoint.cas.h5"
            case_path.write_bytes(b"case")
            with self.assertRaises(CheckpointVerificationError):
                verify_checkpoint_pair(
                    case_path,
                    root / "checkpoint.dat.h5",
                    timeout_seconds=0.01,
                    poll_seconds=0.001,
                )


class ResumableRunClientTests(unittest.TestCase):
    def test_fresh_run_initializes_once_and_commits_each_chunk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_source_case(root)
            digest_before = hashlib.sha256(source.read_bytes()).hexdigest()
            process = FakeOwnedProcess()
            operations = FakeRunOperations(process)
            session = FakeSession()
            client = make_client(process, operations, [session])

            receipt = client.execute(
                make_spec(source),
                make_context(root, process, generation=1),
            )

            self.assertEqual(receipt.status, "success")
            self.assertEqual(receipt.completed_iterations, 10)
            self.assertEqual(receipt.initialization_count, 1)
            self.assertEqual(receipt.resume_count, 0)
            self.assertEqual(receipt.generation_history, (1,))
            self.assertEqual(operations.initialize_calls, 1)
            self.assertEqual(operations.iterate_calls, [5, 5])
            self.assertEqual(len(operations.write_case_paths), 3)
            self.assertEqual(len(operations.write_data_paths), 3)
            self.assertEqual(
                hashlib.sha256(source.read_bytes()).hexdigest(),
                digest_before,
            )
            self.assertEqual(len(session.exit_calls), 1)

            state = AtomicRunStateStore(Path(receipt.run_state_path)).load(
                spec=make_spec(source)
            )
            assert state is not None
            self.assertEqual(state["status"], "completed")
            self.assertEqual(state["last_checkpoint"]["iteration"], 10)
            self.assertFalse(
                any(
                    ".tmp-" in path.name
                    for path in Path(receipt.run_state_path).parent.iterdir()
                )
            )

    def test_generation_loss_resumes_last_pair_without_reinitializing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_source_case(root)
            spool = FilesystemJobSpool(root)
            spec = make_spec(source)
            spool.submit(spec)

            first_process = FakeOwnedProcess()
            first_ops = FakeRunOperations(
                first_process,
                fail_iterate_calls={2},
            )
            first_session = FakeSession()
            first_processor = JobStageProcessor(
                spool,
                resumable_run_client=make_client(
                    first_process,
                    first_ops,
                    [first_session],
                ),
                timestamp_factory=lambda: NOW,
            )

            with self.assertRaises(FluentGenerationRetryRequested):
                first_processor.process_next(
                    make_context(root, first_process, generation=1)
                )

            self.assertEqual(len(list(spool.running_dir.glob("*.json"))), 1)
            self.assertFalse(any(spool.completed_dir.iterdir()))
            self.assertFalse(any(spool.failed_dir.iterdir()))
            self.assertFalse(any(spool.receipts_dir.iterdir()))
            state_path = (
                root
                / "stage_artifacts"
                / "resumable_run"
                / spec.job_id
                / "run-state.json"
            )
            interrupted = AtomicRunStateStore(state_path).load(spec=spec)
            assert interrupted is not None
            self.assertEqual(interrupted["status"], "retryable")
            self.assertEqual(interrupted["completed_iterations"], 5)

            second_process = FakeOwnedProcess()
            second_ops = FakeRunOperations(second_process)
            second_session = FakeSession()
            second_processor = JobStageProcessor(
                spool,
                resumable_run_client=make_client(
                    second_process,
                    second_ops,
                    [second_session],
                ),
                timestamp_factory=lambda: NOW,
            )
            terminal = second_processor.process_next(
                make_context(root, second_process, generation=2)
            )

            assert terminal is not None
            self.assertEqual(terminal.status, "completed")
            self.assertEqual(second_ops.initialize_calls, 0)
            self.assertEqual(len(second_ops.read_case_paths), 1)
            self.assertEqual(len(second_ops.read_data_paths), 1)
            self.assertEqual(second_ops.iterate_calls, [5])
            receipt = StageReceipt.from_dict(
                json.loads(
                    (spool.receipts_dir / f"{spec.job_id}.json").read_text(
                        encoding="utf-8"
                    )
                )
            )
            self.assertEqual(receipt.completed_iterations, 10)
            self.assertEqual(receipt.initialization_count, 1)
            self.assertEqual(receipt.resume_count, 1)
            self.assertEqual(receipt.generation_history, (1, 2))
            self.assertTrue(
                (spool.completed_dir / f"{spec.job_id}.json").is_file()
            )
            self.assertFalse(any(spool.running_dir.iterdir()))

    def test_timeout_is_retryable_and_keeps_job_nonterminal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_source_case(root)
            process = FakeOwnedProcess()
            release = threading.Event()

            class BlockingOperations(FakeRunOperations):
                def iterate(self, _session, count: int) -> None:
                    self.iterate_calls.append(count)
                    release.wait()

            operations = BlockingOperations(process)
            client = ResumableRunStageClient(
                connect_factory=lambda _path, _config: FakeSession(),
                pyfluent_version_factory=lambda: "0.40.2",
                operations=operations,
                timestamp_factory=lambda: NOW,
            )
            spec = make_spec(
                source,
                command_timeout_seconds=0.02,
                timeout_seconds=0.2,
            )

            with self.assertRaises(FluentGenerationRetryRequested):
                client.execute(
                    spec,
                    make_context(root, process, generation=1),
                )
            release.set()

            state = AtomicRunStateStore(
                root
                / "stage_artifacts"
                / "resumable_run"
                / spec.job_id
                / "run-state.json"
            ).load(spec=spec)
            assert state is not None
            self.assertEqual(state["status"], "retryable")
            self.assertEqual(state["completed_iterations"], 0)
            self.assertEqual(state["attempts"][0]["error"]["type"], "TimeoutError")

    def test_missing_committed_pair_fails_before_resume_connection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_source_case(root)
            spec = make_spec(source)
            first_process = FakeOwnedProcess()
            first_ops = FakeRunOperations(
                first_process,
                fail_iterate_calls={1},
            )
            first_client = make_client(
                first_process,
                first_ops,
                [FakeSession()],
            )
            with self.assertRaises(FluentGenerationRetryRequested):
                first_client.execute(
                    spec,
                    make_context(root, first_process, generation=1),
                )

            state_path = (
                root
                / "stage_artifacts"
                / "resumable_run"
                / spec.job_id
                / "run-state.json"
            )
            interrupted = AtomicRunStateStore(state_path).load(spec=spec)
            assert interrupted is not None
            Path(interrupted["last_checkpoint"]["data_path"]).unlink()

            connected: list[bool] = []
            second_process = FakeOwnedProcess()
            second_client = ResumableRunStageClient(
                connect_factory=lambda _path, _config: connected.append(True),
                pyfluent_version_factory=lambda: "0.40.2",
                operations=FakeRunOperations(second_process),
                timestamp_factory=lambda: NOW,
            )
            receipt = second_client.execute(
                spec,
                make_context(root, second_process, generation=2),
            )

            self.assertEqual(receipt.status, "failed")
            self.assertEqual(
                receipt.error["type"],
                "CheckpointVerificationError",
            )
            self.assertEqual(connected, [])

    def test_retry_budget_exhaustion_produces_failed_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_source_case(root)
            spec = make_spec(source, max_resume_attempts=1)
            spool = FilesystemJobSpool(root)
            spool.submit(spec)

            for generation, expect_retry in ((1, True), (2, False)):
                process = FakeOwnedProcess()
                operations = FakeRunOperations(
                    process,
                    fail_iterate_calls={1},
                )
                processor = JobStageProcessor(
                    spool,
                    resumable_run_client=make_client(
                        process,
                        operations,
                        [FakeSession()],
                    ),
                    timestamp_factory=lambda: NOW,
                )
                context = make_context(root, process, generation=generation)
                if expect_retry:
                    with self.assertRaises(FluentGenerationRetryRequested):
                        processor.process_next(context)
                else:
                    state = processor.process_next(context)
                    assert state is not None
                    self.assertEqual(state.status, "failed")

            receipt = StageReceipt.from_dict(
                json.loads(
                    (spool.receipts_dir / f"{spec.job_id}.json").read_text(
                        encoding="utf-8"
                    )
                )
            )
            self.assertEqual(receipt.status, "failed")
            self.assertEqual(receipt.completed_iterations, 0)
            self.assertEqual(receipt.generation_history, (1, 2))
            self.assertTrue(
                (spool.failed_dir / f"{spec.job_id}.json").is_file()
            )
            self.assertFalse(any(spool.completed_dir.iterdir()))


if __name__ == "__main__":
    unittest.main()
