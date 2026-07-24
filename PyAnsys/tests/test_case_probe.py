from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.case_probe import (  # noqa: E402
    CaseIdentityProbeClient,
)
from pyansys_fluent.host_worker import HostWorkerConfig  # noqa: E402
from pyansys_fluent.job_protocol import (  # noqa: E402
    FilesystemJobSpool,
    HealthStageContext,
    JobSpec,
    JobStageProcessor,
    ProtocolValidationError,
    ReceiptCommitError,
    StageReceipt,
)


NOW = "2026-07-24T12:00:00.000Z"


class FakeOwnedProcess:
    def __init__(self) -> None:
        self.alive = True


class FakeMesh:
    def get_surface_names(self):
        return ["inlet", "outlet", "wall"]

    def get_surface_ids(self):
        return [3, 4, 5]

    def get_surface_locs(self, surface_id):
        return [surface_id * 10, surface_id * 10 + 9]


class FakeCaseReader:
    def num_dimensions(self):
        return 3

    def precision(self):
        return 2

    def get_mesh(self):
        return FakeMesh()


class FakeFileCommands:
    def __init__(
        self,
        *,
        load_error: Exception | None = None,
        load_started: threading.Event | None = None,
        load_release: threading.Event | None = None,
    ) -> None:
        self.load_error = load_error
        self.load_started = load_started
        self.load_release = load_release
        self.calls: list[tuple[str, str]] = []

    def read_case(self, *, file_name: str) -> None:
        self.calls.append(("read_case", file_name))
        if self.load_started is not None:
            self.load_started.set()
        if self.load_release is not None:
            self.load_release.wait()
        if self.load_error is not None:
            raise self.load_error

    def read_data(self, **_kwargs) -> None:
        raise AssertionError("case_identity_probe must not call read_data")

    def read_case_data(self, **_kwargs) -> None:
        raise AssertionError("case_identity_probe must not call read_case_data")

    def write_case(self, **_kwargs) -> None:
        raise AssertionError("case_identity_probe must not call write_case")

    def write_data(self, **_kwargs) -> None:
        raise AssertionError("case_identity_probe must not call write_data")


class FakeBoundaryConditions:
    def get_state(self):
        return {
            "velocity_inlet": {"inlet": {}},
            "pressure_outlet": {"outlet": {}},
            "wall": {"wall": {}},
        }


class FakeModels:
    def get_active_child_names(self):
        return ["energy", "viscous"]


class FakeSetup:
    def __init__(self) -> None:
        self.boundary_conditions = FakeBoundaryConditions()
        self.models = FakeModels()


class FakeSettings:
    def __init__(self, file_commands: FakeFileCommands) -> None:
        self.file = file_commands
        self.setup = FakeSetup()


class FakeSession:
    def __init__(
        self,
        *,
        file_commands: FakeFileCommands | None = None,
        process: FakeOwnedProcess | None = None,
    ) -> None:
        self.file_commands = file_commands or FakeFileCommands()
        self.settings = FakeSettings(self.file_commands)
        self.process = process
        self.exit_calls: list[dict[str, object]] = []

    def is_active(self) -> bool:
        return True

    def get_fluent_version(self) -> str:
        return "25.2.0"

    def exit(self, **kwargs) -> None:
        self.exit_calls.append(kwargs)


def write_case(root: Path, name: str = "source.cas.h5") -> Path:
    path = root / name
    path.write_bytes(b"mock-fluent-case-content")
    return path.resolve()


def make_spec(case_path: Path | str, **overrides) -> JobSpec:
    values = {
        "job_id": "case-probe-001",
        "stage_type": "case_identity_probe",
        "submitted_at": NOW,
        "timeout_seconds": 1.0,
        "expected_worker_boot_id": "boot-abc",
        "expected_fluent_generation": 2,
        "case_path": str(case_path),
    }
    values.update(overrides)
    return JobSpec(**values)


def make_context(
    root: Path,
    *,
    boot_id: str = "boot-abc",
    generation: int = 2,
    process: FakeOwnedProcess | None = None,
) -> HealthStageContext:
    owned = process or FakeOwnedProcess()
    return HealthStageContext(
        worker_boot_id=boot_id,
        fluent_generation=generation,
        fluent_pid=9700,
        server_info_path=root / "fluent-server-info-002.txt",
        config=HostWorkerConfig(
            fluent_exe=root / "fluent.exe",
            work_dir=root,
            health_timeout_seconds=0.1,
        ),
        process_is_alive=lambda: owned.alive,
    )


def make_client(
    session: FakeSession,
    *,
    connected: list[bool] | None = None,
) -> CaseIdentityProbeClient:
    def connect(_path, _config):
        if connected is not None:
            connected.append(True)
        return session

    return CaseIdentityProbeClient(
        connect_factory=connect,
        pyfluent_version_factory=lambda: "0.40.2",
        case_reader_factory=lambda _path: FakeCaseReader(),
        timestamp_factory=lambda: NOW,
    )


class CaseJobSchemaTests(unittest.TestCase):
    def test_valid_case_load_job_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = write_case(Path(tmp))
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            spec = make_spec(
                source,
                expected_file_size_bytes=source.stat().st_size,
                expected_sha256=digest,
                compute_sha256=True,
            )

            self.assertEqual(JobSpec.from_dict(spec.to_dict()), spec)

    def test_relative_path_is_rejected(self) -> None:
        with self.assertRaises(ProtocolValidationError):
            make_spec(Path("relative.cas.h5")).validate()

    def test_unsupported_extension_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.dat.h5"
            source.write_bytes(b"data")
            with self.assertRaises(ProtocolValidationError):
                make_spec(source.resolve()).validate()


class CaseInputTests(unittest.TestCase):
    def test_missing_case_fails_before_fluent_connection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = (root / "missing.cas.h5").resolve()
            connected: list[bool] = []
            receipt = make_client(
                FakeSession(),
                connected=connected,
            ).execute(
                make_spec(missing),
                make_context(root),
            )

            self.assertEqual(receipt.status, "failed")
            self.assertEqual(receipt.error["type"], "CaseInputValidationError")
            self.assertFalse(receipt.error["retryable"])
            self.assertEqual(connected, [])
            self.assertFalse(receipt.fluent_accepted_case)

    def test_directory_case_path_is_rejected_before_connection(self) -> None:
        with tempfile.TemporaryDirectory(suffix=".cas.h5") as tmp:
            source = Path(tmp).resolve()
            connected: list[bool] = []
            receipt = make_client(
                FakeSession(),
                connected=connected,
            ).execute(
                make_spec(source),
                make_context(source.parent),
            )

            self.assertEqual(receipt.status, "failed")
            self.assertIn("not a file", receipt.error["message"])
            self.assertEqual(connected, [])

    def test_expected_file_size_mismatch_fails_before_connection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)
            connected: list[bool] = []
            receipt = make_client(
                FakeSession(),
                connected=connected,
            ).execute(
                make_spec(source, expected_file_size_bytes=999),
                make_context(root),
            )

            self.assertEqual(receipt.status, "failed")
            self.assertIn("size mismatch", receipt.error["message"])
            self.assertEqual(connected, [])


class CaseIdentityProbeTests(unittest.TestCase):
    def test_generation_mismatch_occurs_before_copy_or_connection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)
            connected: list[bool] = []
            receipt = make_client(
                FakeSession(),
                connected=connected,
            ).execute(
                make_spec(source, expected_fluent_generation=1),
                make_context(root, generation=2),
            )

            self.assertEqual(receipt.status, "failed")
            self.assertEqual(
                receipt.error["type"],
                "FluentGenerationMismatchError",
            )
            self.assertTrue(receipt.error["retryable"])
            self.assertEqual(connected, [])
            self.assertIsNone(receipt.disposable_case_path)

    def test_worker_boot_mismatch_occurs_before_connection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)
            connected: list[bool] = []
            receipt = make_client(
                FakeSession(),
                connected=connected,
            ).execute(
                make_spec(source, expected_worker_boot_id="old-boot"),
                make_context(root, boot_id="boot-abc"),
            )

            self.assertEqual(receipt.status, "failed")
            self.assertEqual(receipt.error["type"], "WorkerBootMismatchError")
            self.assertTrue(receipt.error["retryable"])
            self.assertEqual(connected, [])

    def test_successful_mocked_load_uses_only_disposable_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)
            original = source.read_bytes()
            process = FakeOwnedProcess()
            session = FakeSession(process=process)
            receipt = make_client(session).execute(
                make_spec(source, compute_sha256=True),
                make_context(root, process=process),
            )

            self.assertEqual(receipt.status, "success")
            self.assertTrue(receipt.fluent_accepted_case)
            self.assertFalse(receipt.data_loaded)
            self.assertEqual(receipt.fluent_version, "25.2.0")
            self.assertEqual(receipt.pyfluent_version, "0.40.2")
            self.assertEqual(receipt.requested_case_path, str(source))
            self.assertEqual(receipt.resolved_case_path, str(source))
            self.assertEqual(receipt.source_file_size_bytes, len(original))
            self.assertEqual(
                receipt.source_sha256,
                hashlib.sha256(original).hexdigest(),
            )
            disposable = Path(receipt.disposable_case_path)
            self.assertNotEqual(disposable, source)
            self.assertEqual(disposable.read_bytes(), original)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(
                session.file_commands.calls,
                [("read_case", str(disposable))],
            )
            self.assertEqual(receipt.case_identity["dimension"]["value"], 3)
            self.assertEqual(
                receipt.case_identity["precision"]["value"],
                "double",
            )
            self.assertEqual(
                receipt.case_identity["active_models"]["value"],
                ["energy", "viscous"],
            )
            self.assertTrue(receipt.client_detached)
            self.assertTrue(receipt.fluent_process_alive_after_detach)
            self.assertTrue(process.alive)
            self.assertEqual(len(session.exit_calls), 1)

    def test_fluent_load_failure_is_durable_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)
            commands = FakeFileCommands(load_error=RuntimeError("bad case"))
            session = FakeSession(file_commands=commands)
            receipt = make_client(session).execute(
                make_spec(source),
                make_context(root),
            )

            self.assertEqual(receipt.status, "failed")
            self.assertEqual(receipt.error["type"], "RuntimeError")
            self.assertFalse(receipt.error["retryable"])
            self.assertFalse(receipt.fluent_accepted_case)
            self.assertFalse(receipt.data_loaded)
            self.assertEqual(len(session.exit_calls), 1)

    def test_missing_optional_live_metadata_is_explicit_not_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)
            session = FakeSession()
            session.settings = SimpleNamespace(file=session.file_commands)

            receipt = make_client(session).execute(
                make_spec(source),
                make_context(root),
            )

            self.assertEqual(receipt.status, "success")
            self.assertIsNone(receipt.case_identity["boundary_zones"]["value"])
            self.assertIn(
                "unavailable_reason",
                receipt.case_identity["boundary_zones"],
            )
            self.assertIsNone(receipt.case_identity["active_models"]["value"])
            self.assertIn(
                "unavailable_reason",
                receipt.case_identity["active_models"],
            )

    def test_stage_timeout_is_failed_and_detached(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)
            started = threading.Event()
            release = threading.Event()
            commands = FakeFileCommands(
                load_started=started,
                load_release=release,
            )
            session = FakeSession(file_commands=commands)
            receipt = make_client(session).execute(
                make_spec(source, timeout_seconds=0.02),
                make_context(root),
            )
            self.assertTrue(started.is_set())
            release.set()

            self.assertEqual(receipt.status, "failed")
            self.assertEqual(receipt.error["type"], "TimeoutError")
            self.assertTrue(receipt.error["retryable"])
            self.assertFalse(receipt.fluent_accepted_case)
            self.assertEqual(len(session.exit_calls), 1)


class CaseProcessorTests(unittest.TestCase):
    def test_failed_case_load_moves_only_to_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)
            spec = make_spec(source)
            spool = FilesystemJobSpool(root)
            spool.submit(spec)
            processor = JobStageProcessor(
                spool,
                case_probe_client=make_client(
                    FakeSession(
                        file_commands=FakeFileCommands(
                            load_error=RuntimeError("rejected")
                        )
                    )
                ),
                timestamp_factory=lambda: NOW,
            )

            state = processor.process_next(make_context(root))

            self.assertEqual(state.status, "failed")
            self.assertTrue((spool.failed_dir / f"{spec.job_id}.json").is_file())
            self.assertFalse(any(spool.completed_dir.iterdir()))

    def test_case_receipt_persistence_failure_never_completes_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)

            class BrokenReceiptSpool(FilesystemJobSpool):
                def commit_receipt(self, receipt: StageReceipt) -> Path:
                    raise ReceiptCommitError("simulated disk failure")

            spool = BrokenReceiptSpool(root)
            spool.submit(make_spec(source))
            processor = JobStageProcessor(
                spool,
                case_probe_client=make_client(FakeSession()),
                timestamp_factory=lambda: NOW,
            )

            with self.assertRaises(ReceiptCommitError):
                processor.process_next(make_context(root))

            self.assertFalse(any(spool.completed_dir.iterdir()))
            self.assertEqual(len(list(spool.running_dir.iterdir())), 1)

    def test_successful_case_receipt_commits_before_completed_move(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_case(root)
            spec = make_spec(source)
            spool = FilesystemJobSpool(root)
            spool.submit(spec)
            processor = JobStageProcessor(
                spool,
                case_probe_client=make_client(FakeSession()),
                timestamp_factory=lambda: NOW,
            )

            state = processor.process_next(make_context(root))

            self.assertEqual(state.status, "completed")
            receipt_path = spool.receipts_dir / f"{spec.job_id}.json"
            self.assertTrue(receipt_path.is_file())
            receipt = StageReceipt.from_dict(
                json.loads(receipt_path.read_text(encoding="utf-8"))
            )
            self.assertEqual(receipt.status, "success")
            self.assertTrue(
                (spool.completed_dir / f"{spec.job_id}.json").is_file()
            )


if __name__ == "__main__":
    unittest.main()
