from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pyansys_fluent.run_worker import (
    FluentRunWorker,
    RunRequest,
    RunRequestError,
    execute_run_request,
    submit_run_request,
    verify_stable_pair,
)


class FakeOperations:
    def __init__(self):
        self.calls: list[tuple] = []
        self.active = True
        self.iteration = 0

    def connect(self, connection):
        self.calls.append(("connect", connection["generation"]))
        return self

    def is_active(self, session):
        return self.active

    def read_case(self, session, path):
        self.calls.append(("read_case", str(path)))

    def read_data(self, session, path):
        self.calls.append(("read_data", str(path)))

    def execute_tui(self, session, command):
        self.calls.append(("execute_tui", command))
        return f"executed: {command}"

    def iterate(self, session, iterations):
        self.iteration += iterations
        self.calls.append(("iterate", iterations))

    def write_case(self, session, path):
        path.write_bytes(f"case-{self.iteration}".encode())
        self.calls.append(("write_case", str(path)))

    def write_data(self, session, path):
        path.write_bytes(f"data-{self.iteration}".encode())
        self.calls.append(("write_data", str(path)))

    def detach(self, session):
        self.calls.append(("detach",))


def request_payload(root: Path, **updates):
    payload = {
        "schema_version": 2,
        "job_id": "test-run",
        "expected_generation": 4,
        "mode": "initialize",
        "source_case": str(root / "source.cas.h5"),
        "source_data": None,
        "initialization_tui": [
            "/solve/initialize/hyb-initialization",
            "/report/system/proc-stats",
        ],
        "target_total_iterations": 600,
        "completed_iterations": 0,
        "checkpoint_interval": 250,
        "report_interval": 100,
        "output_directory": str(root / "output"),
        "overwrite": False,
    }
    payload.update(updates)
    if payload["mode"] == "resume" and "initialization_tui" not in updates:
        payload["initialization_tui"] = None
    return payload


class RunRequestTests(unittest.TestCase):
    def test_unknown_fields_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            payload = request_payload(Path(temp), surprise=True)
            with self.assertRaises(RunRequestError):
                RunRequest.from_dict(payload)

    def test_resume_requires_data(self):
        with tempfile.TemporaryDirectory() as temp:
            payload = request_payload(
                Path(temp), mode="resume", completed_iterations=250
            )
            with self.assertRaises(RunRequestError):
                RunRequest.from_dict(payload)

    def test_initialize_cannot_claim_completed_iterations(self):
        with tempfile.TemporaryDirectory() as temp:
            payload = request_payload(Path(temp), completed_iterations=1)
            with self.assertRaises(RunRequestError):
                RunRequest.from_dict(payload)

    def test_initialize_requires_nonempty_tui_sequence(self):
        with tempfile.TemporaryDirectory() as temp:
            payload = request_payload(Path(temp), initialization_tui=[])
            with self.assertRaisesRegex(RunRequestError, "non-empty"):
                RunRequest.from_dict(payload)

    def test_initialize_rejects_non_string_tui_entry(self):
        with tempfile.TemporaryDirectory() as temp:
            payload = request_payload(
                Path(temp), initialization_tui=["/solve/initialize/foo", 3]
            )
            with self.assertRaisesRegex(RunRequestError, "index 1"):
                RunRequest.from_dict(payload)

    def test_resume_rejects_initialization_tui(self):
        with tempfile.TemporaryDirectory() as temp:
            payload = request_payload(
                Path(temp),
                mode="resume",
                source_data=str(Path(temp) / "resume.dat.h5"),
                completed_iterations=250,
                initialization_tui=["/solve/initialize/hyb-initialization"],
            )
            with self.assertRaisesRegex(RunRequestError, "resume mode"):
                RunRequest.from_dict(payload)

    def test_overwrite_true_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            payload = request_payload(Path(temp), overwrite=True)
            with self.assertRaises(RunRequestError):
                RunRequest.from_dict(payload)

    def test_checkpoint_interval_defaults_to_250(self):
        with tempfile.TemporaryDirectory() as temp:
            payload = request_payload(Path(temp))
            payload.pop("checkpoint_interval")
            self.assertEqual(250, RunRequest.from_dict(payload).checkpoint_interval)

    def test_submit_is_atomic_and_rejects_duplicate_job_id(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = RunRequest.from_dict(request_payload(root))
            destination = submit_run_request(root / "bridge", request)
            self.assertTrue(destination.is_file())
            self.assertEqual(request.to_dict(), json.loads(destination.read_text()))
            with self.assertRaises(FileExistsError):
                submit_run_request(root / "bridge", request)


class RunExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "source.cas.h5").write_bytes(b"source-case")
        (self.root / "resume.dat.h5").write_bytes(b"resume-data")
        self.connection_path = self.root / "latest_connection.json"
        self.connection_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "generation": 4,
                    "status": "running",
                    "host": "10.0.0.5",
                    "port": 50000,
                    "password": "secret",
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def verifier(case_path, data_path):
        return case_path.stat().st_size, data_path.stat().st_size

    def test_initialize_checkpoints_and_final_data(self):
        request = RunRequest.from_dict(request_payload(self.root))
        operations = FakeOperations()
        receipt = execute_run_request(
            request,
            latest_connection_path=self.connection_path,
            operations=operations,
            pair_verifier=self.verifier,
        )
        self.assertEqual("completed", receipt["status"])
        self.assertEqual(600, receipt["completed_iterations"])
        self.assertEqual(
            [
                (
                    "execute_tui",
                    "/solve/initialize/hyb-initialization",
                ),
                ("execute_tui", "/report/system/proc-stats"),
            ],
            [call for call in operations.calls if call[0] == "execute_tui"],
        )
        self.assertEqual(
            ["completed", "completed"],
            [entry["status"] for entry in receipt["initialization_log"]],
        )
        self.assertEqual(
            "/report/system/proc-stats",
            receipt["initialization_log"][1]["command"],
        )
        self.assertTrue(receipt["final_data_path"].endswith("_600.dat.h5"))
        written_cases = [
            call for call in operations.calls if call[0] == "write_case"
        ]
        self.assertEqual(3, len(written_cases))
        checkpoint_cases = sorted(
            path.name for path in (self.root / "output").glob("*-checkpoint-*.cas.h5")
        )
        self.assertEqual(["test-run-checkpoint-00000500.cas.h5"], checkpoint_cases)
        self.assertEqual(
            2,
            len(list((self.root / "output").glob("*.cas.h5"))),
        )
        self.assertEqual(
            2,
            len(list((self.root / "output").glob("*.dat.h5"))),
        )

    def test_resume_never_initializes_and_runs_remaining_iterations(self):
        payload = request_payload(
            self.root,
            mode="resume",
            source_data=str(self.root / "resume.dat.h5"),
            completed_iterations=250,
            target_total_iterations=600,
        )
        request = RunRequest.from_dict(payload)
        operations = FakeOperations()
        receipt = execute_run_request(
            request,
            latest_connection_path=self.connection_path,
            operations=operations,
            pair_verifier=self.verifier,
        )
        self.assertEqual("completed", receipt["status"])
        self.assertFalse(
            any(call[0] == "execute_tui" for call in operations.calls)
        )
        self.assertEqual([], receipt["initialization_log"])
        self.assertTrue(any(call[0] == "read_data" for call in operations.calls))
        self.assertEqual(350, operations.iteration)

    def test_tui_failure_stops_sequence_before_iterations(self):
        request = RunRequest.from_dict(request_payload(self.root))
        operations = FakeOperations()

        def fail_second_command(session, command):
            operations.calls.append(("execute_tui", command))
            if command.endswith("proc-stats"):
                raise RuntimeError("verified command failed in production")
            return "ok"

        operations.execute_tui = fail_second_command
        receipt = execute_run_request(
            request,
            latest_connection_path=self.connection_path,
            operations=operations,
            pair_verifier=self.verifier,
        )
        self.assertEqual("failed", receipt["status"])
        self.assertEqual(
            ["completed", "failed"],
            [entry["status"] for entry in receipt["initialization_log"]],
        )
        self.assertFalse(any(call[0] == "iterate" for call in operations.calls))

    def test_generation_change_interrupts_without_retry(self):
        request = RunRequest.from_dict(request_payload(self.root))
        operations = FakeOperations()
        original_iterate = operations.iterate

        def changing_iterate(session, iterations):
            original_iterate(session, iterations)
            payload = json.loads(self.connection_path.read_text())
            payload["generation"] = 5
            self.connection_path.write_text(json.dumps(payload))

        operations.iterate = changing_iterate
        receipt = execute_run_request(
            request,
            latest_connection_path=self.connection_path,
            operations=operations,
            pair_verifier=self.verifier,
        )
        self.assertEqual("interrupted", receipt["status"])
        self.assertEqual(100, receipt["completed_iterations"])
        self.assertIsNone(receipt["last_checkpoint"])

    def test_ordinary_command_error_is_failed(self):
        request = RunRequest.from_dict(request_payload(self.root))
        operations = FakeOperations()

        def invalid_value(session, iterations):
            raise ValueError("invalid Fluent value")

        operations.iterate = invalid_value
        receipt = execute_run_request(
            request,
            latest_connection_path=self.connection_path,
            operations=operations,
            pair_verifier=self.verifier,
        )
        self.assertEqual("failed", receipt["status"])

    def test_missing_source_is_failed_without_connecting(self):
        payload = request_payload(
            self.root, source_case=str(self.root / "missing.cas.h5")
        )
        operations = FakeOperations()
        receipt = execute_run_request(
            RunRequest.from_dict(payload),
            latest_connection_path=self.connection_path,
            operations=operations,
            pair_verifier=self.verifier,
        )
        self.assertEqual("failed", receipt["status"])
        self.assertFalse(any(call[0] == "connect" for call in operations.calls))

    def test_existing_output_is_not_overwritten(self):
        payload = request_payload(
            self.root,
            target_total_iterations=0,
        )
        output = self.root / "output"
        output.mkdir()
        existing = output / "source_0.cas.h5"
        existing.write_bytes(b"keep-existing")
        operations = FakeOperations()
        receipt = execute_run_request(
            RunRequest.from_dict(payload),
            latest_connection_path=self.connection_path,
            operations=operations,
            pair_verifier=self.verifier,
        )
        self.assertEqual("failed", receipt["status"])
        self.assertEqual(b"keep-existing", existing.read_bytes())
        self.assertFalse(any(call[0] == "write_case" for call in operations.calls))
        self.assertEqual(b"source-case", (self.root / "source.cas.h5").read_bytes())

    def test_pair_verification_requires_stable_nonempty_files(self):
        case_path = self.root / "stable.cas.h5"
        data_path = self.root / "stable.dat.h5"
        case_path.write_bytes(b"case")
        data_path.write_bytes(b"data")

        def mutate_during_delay(_seconds):
            data_path.write_bytes(b"data-changed")

        with self.assertRaisesRegex(RuntimeError, "not stable"):
            verify_stable_pair(
                case_path,
                data_path,
                sleep=mutate_during_delay,
                stability_delay_seconds=0,
            )

    def test_connection_error_redacts_password_from_receipt(self):
        request = RunRequest.from_dict(request_payload(self.root))
        operations = FakeOperations()

        def leaking_connect(connection):
            raise RuntimeError(f"could not connect with {connection['password']}")

        operations.connect = leaking_connect
        receipt = execute_run_request(
            request,
            latest_connection_path=self.connection_path,
            operations=operations,
            pair_verifier=self.verifier,
        )
        self.assertNotIn("secret", json.dumps(receipt))
        self.assertIn("<redacted>", receipt["error"]["message"])

    def test_spool_writes_receipt_without_password(self):
        bridge = self.root / "bridge"
        connection = bridge / "latest_connection.json"
        connection.parent.mkdir(parents=True)
        connection.write_text(self.connection_path.read_text(), encoding="utf-8")
        incoming = bridge / "run_requests" / "incoming"
        incoming.mkdir(parents=True)
        (incoming / "test-run.json").write_text(
            json.dumps(request_payload(self.root)), encoding="utf-8"
        )
        worker = FluentRunWorker(
            bridge,
            operations=FakeOperations(),
            pair_verifier=self.verifier,
        )
        receipt_path = worker.process_next()
        self.assertIsNotNone(receipt_path)
        text = receipt_path.read_text(encoding="utf-8")
        self.assertNotIn("secret", text)
        self.assertEqual("completed", json.loads(text)["status"])

    def test_invalid_spooled_request_fails_without_connecting(self):
        bridge = self.root / "bridge"
        incoming = bridge / "run_requests" / "incoming"
        incoming.mkdir(parents=True)
        (incoming / "bad-request.json").write_text(
            json.dumps({"schema_version": 2, "job_id": "bad-request"}),
            encoding="utf-8",
        )
        operations = FakeOperations()
        receipt_path = FluentRunWorker(
            bridge,
            operations=operations,
            pair_verifier=self.verifier,
        ).process_next()
        self.assertEqual("failed", json.loads(receipt_path.read_text())["status"])
        self.assertFalse(any(call[0] == "connect" for call in operations.calls))


if __name__ == "__main__":
    unittest.main()
