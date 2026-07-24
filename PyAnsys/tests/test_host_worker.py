from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.host_worker import (  # noqa: E402
    AtomicJsonStatusStore,
    ExclusiveHostLock,
    FluentHostWorker,
    FluentProcessManager,
    HostWorkerConfig,
    HostWorkerAlreadyRunning,
    ManagedFluentProcess,
    RestartBudget,
    RestartLimitExceeded,
    call_with_timeout,
    session_is_active,
    validate_server_info_text,
)


class FakeProcess:
    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.returncode = None
        self.stdin = None
        self.terminated = False

    def poll(self):
        return self.returncode

    def terminate(self) -> None:
        self.terminated = True
        self.returncode = 0

    def wait(self, timeout=None):
        return self.returncode


class FakeTextHandle:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeProcessTreeToken:
    def __init__(self, process: FakeProcess) -> None:
        self.process = process
        self.closed = False

    def close(self) -> None:
        self.closed = True
        self.process.returncode = 0


def fake_managed(root: Path, generation: int) -> ManagedFluentProcess:
    stdout_handle = FakeTextHandle()
    stderr_handle = FakeTextHandle()
    return ManagedFluentProcess(
        process=FakeProcess(1000 + generation),
        generation=generation,
        launched_unix_seconds=0.0,
        server_info_path=root / "fluent-server-info.txt",
        stdout_path=root / f"generation-{generation}-stdout.log",
        stderr_path=root / f"generation-{generation}-stderr.log",
        stdout_handle=stdout_handle,
        stderr_handle=stderr_handle,
    )


class HostWorkerConfigTests(unittest.TestCase):
    def test_mode_argument_respects_dimension_and_precision(self) -> None:
        base = {
            "fluent_exe": Path("fluent.exe"),
            "work_dir": Path("output"),
        }
        self.assertEqual(
            HostWorkerConfig(**base, dimension=3, precision="double").fluent_mode_argument,
            "3ddp",
        )
        self.assertEqual(
            HostWorkerConfig(**base, dimension=2, precision="single").fluent_mode_argument,
            "2d",
        )


class AtomicStatusTests(unittest.TestCase):
    def test_status_write_is_valid_json_and_leaves_no_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            store = AtomicJsonStatusStore(path)
            store.write({"state": "running", "generation": 2})

            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["state"], "running")
            self.assertFalse(
                any(".tmp-" in item.name for item in Path(tmp).iterdir())
            )


class ExclusiveHostLockTests(unittest.TestCase):
    def test_second_worker_cannot_acquire_same_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "host-worker.lock"
            first = ExclusiveHostLock(path)
            second = ExclusiveHostLock(path)
            first.acquire()
            try:
                with self.assertRaises(HostWorkerAlreadyRunning):
                    second.acquire()
            finally:
                first.release()

            second.acquire()
            second.release()


class TimeoutTests(unittest.TestCase):
    def test_timeout_does_not_block_worker_thread_exit(self) -> None:
        started = threading.Event()
        release = threading.Event()

        def block() -> None:
            started.set()
            release.wait()

        with self.assertRaises(TimeoutError):
            call_with_timeout(block, 0.02, label="blocked-test")
        self.assertTrue(started.is_set())
        release.set()

    def test_late_connect_result_is_cleaned_after_timeout(self) -> None:
        release = threading.Event()
        cleaned = threading.Event()
        value = object()

        def delayed():
            release.wait()
            return value

        with self.assertRaises(TimeoutError):
            call_with_timeout(
                delayed,
                0.02,
                label="late-result",
                late_result_cleanup=lambda result: (
                    cleaned.set() if result is value else None
                ),
            )
        release.set()
        self.assertTrue(cleaned.wait(timeout=1.0))


class HealthCompatibilityTests(unittest.TestCase):
    def test_prefers_current_is_active_api(self) -> None:
        class Session:
            def is_active(self):
                return True

        self.assertTrue(session_is_active(Session()))

    def test_falls_back_to_legacy_health_check(self) -> None:
        class Health:
            def check_health(self):
                return "SERVING"

        class Session:
            health_check = Health()

        self.assertTrue(session_is_active(Session()))


class RestartBudgetTests(unittest.TestCase):
    def test_restart_budget_uses_rolling_window(self) -> None:
        budget = RestartBudget(max_restarts=2, window_seconds=10)
        self.assertEqual(budget.record(0), 1)
        self.assertEqual(budget.record(5), 2)
        with self.assertRaises(RestartLimitExceeded):
            budget.record(6)

        fresh = RestartBudget(max_restarts=1, window_seconds=10)
        self.assertEqual(fresh.record(0), 1)
        self.assertEqual(fresh.record(11), 1)


class ServerInfoTests(unittest.TestCase):
    def test_server_info_validation_does_not_return_password(self) -> None:
        host, port = validate_server_info_text("127.0.0.1:50055\nsecret\n")
        self.assertEqual(host, "127.0.0.1")
        self.assertEqual(port, 50055)

    def test_server_info_rejects_partial_and_invalid_port(self) -> None:
        with self.assertRaises(ValueError):
            validate_server_info_text("127.0.0.1:50055\n")
        with self.assertRaises(ValueError):
            validate_server_info_text("127.0.0.1:70000\nsecret\n")

    def test_wait_requires_stable_valid_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = root / "fluent.exe"
            executable.write_text("", encoding="utf-8")
            config = HostWorkerConfig(
                fluent_exe=executable,
                work_dir=root,
                startup_timeout_seconds=2,
                poll_interval_seconds=0.1,
            )
            managed = fake_managed(root, 1)
            now = [0.0]
            sleeps = [0]

            def monotonic() -> float:
                return now[0]

            def sleep(seconds: float) -> None:
                now[0] += seconds
                sleeps[0] += 1
                if sleeps[0] == 1:
                    managed.server_info_path.write_text(
                        "127.0.0.1:50055\n",
                        encoding="utf-8",
                    )
                elif sleeps[0] == 2:
                    managed.server_info_path.write_text(
                        "127.0.0.1:50055\nsecret\n",
                        encoding="utf-8",
                    )

            manager = FluentProcessManager(
                config,
                sleep=sleep,
                monotonic=monotonic,
            )
            path = manager.wait_for_server_info(managed)

            self.assertEqual(path, managed.server_info_path)
            self.assertGreaterEqual(sleeps[0], 3)


class ProcessTreeTests(unittest.TestCase):
    def test_stop_closes_process_tree_token_and_all_handles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = root / "fluent.exe"
            executable.write_text("", encoding="utf-8")
            config = HostWorkerConfig(
                fluent_exe=executable,
                work_dir=root,
            )
            manager = FluentProcessManager(config)
            managed = fake_managed(root, 1)
            managed.server_info_path.write_text(
                "127.0.0.1:50055\nsecret\n",
                encoding="utf-8",
            )
            token = FakeProcessTreeToken(managed.process)
            managed.process_tree_token = token

            manager.stop(managed)

            self.assertTrue(token.closed)
            self.assertTrue(managed.stdout_handle.closed)
            self.assertTrue(managed.stderr_handle.closed)
            self.assertFalse(managed.server_info_path.exists())


class FakeProcessManager:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.launched: list[ManagedFluentProcess] = []
        self.stopped: list[int] = []

    def launch(self, generation: int) -> ManagedFluentProcess:
        managed = fake_managed(self.root, generation)
        self.launched.append(managed)
        return managed

    def wait_for_server_info(self, managed: ManagedFluentProcess) -> Path:
        managed.server_info_path.write_text(
            f"server-info-generation-{managed.generation}",
            encoding="utf-8",
        )
        return managed.server_info_path

    def stop(self, managed: ManagedFluentProcess | None) -> None:
        if managed is None:
            return
        self.stopped.append(managed.generation)
        managed.process.terminate()
        managed.stdout_handle.close()
        managed.stderr_handle.close()


class SequenceSession:
    def __init__(
        self,
        states: list[bool],
        *,
        stop_event: threading.Event | None = None,
    ) -> None:
        self.states = list(states)
        self.stop_event = stop_event
        self.exit_calls = 0

    def is_active(self) -> bool:
        if not self.states:
            if self.stop_event is not None:
                self.stop_event.set()
            return True
        value = self.states.pop(0)
        if not self.states and self.stop_event is not None:
            self.stop_event.set()
        return value

    def get_fluent_version(self) -> str:
        return "24.2-test"

    def exit(self, **_kwargs) -> None:
        self.exit_calls += 1


class DiesAfterVersionSession(SequenceSession):
    def __init__(self, process: FakeProcess) -> None:
        super().__init__([True])
        self.process = process

    def get_fluent_version(self) -> str:
        self.process.returncode = 99
        return "24.2-test"


class WorkerRestartTests(unittest.TestCase):
    def test_worker_relaunches_after_grpc_health_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = root / "fluent.exe"
            executable.write_text("", encoding="utf-8")
            config = HostWorkerConfig(
                fluent_exe=executable,
                work_dir=root,
                health_interval_seconds=0.001,
                heartbeat_interval_seconds=0.001,
                poll_interval_seconds=0.001,
                restart_delay_seconds=0,
                max_restarts=2,
            )
            stop_event = threading.Event()
            manager = FakeProcessManager(root)
            all_sessions = [
                SequenceSession([True, False]),
                SequenceSession([True, True], stop_event=stop_event),
            ]
            sessions = list(all_sessions)

            def connect(_path, _config):
                return sessions.pop(0)

            worker = FluentHostWorker(
                config,
                process_manager=manager,
                connect_factory=connect,
                stop_event=stop_event,
            )
            worker.run()

            self.assertEqual(len(manager.launched), 2)
            self.assertEqual(manager.stopped, [1, 2])
            status = json.loads(config.status_path.read_text(encoding="utf-8"))
            self.assertEqual(status["state"], "stopped")
            self.assertEqual(status["restart_count_total"], 1)
            self.assertGreaterEqual(status["heartbeat_sequence"], 1)
            self.assertIsNotNone(status["worker_boot_id"])
            self.assertIsNotNone(status["last_health_success_unix_seconds"])
            self.assertEqual([item.exit_calls for item in all_sessions], [1, 1])

    def test_worker_relaunches_after_os_process_death(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = root / "fluent.exe"
            executable.write_text("", encoding="utf-8")
            config = HostWorkerConfig(
                fluent_exe=executable,
                work_dir=root,
                health_interval_seconds=0.001,
                heartbeat_interval_seconds=0.001,
                poll_interval_seconds=0.001,
                restart_delay_seconds=0,
                max_restarts=2,
            )
            stop_event = threading.Event()
            manager = FakeProcessManager(root)
            connected_sessions: list[SequenceSession] = []

            def connect(_path, _config):
                if len(manager.launched) == 1:
                    session = DiesAfterVersionSession(manager.launched[-1].process)
                else:
                    session = SequenceSession([True, True], stop_event=stop_event)
                connected_sessions.append(session)
                return session

            worker = FluentHostWorker(
                config,
                process_manager=manager,
                connect_factory=connect,
                stop_event=stop_event,
            )
            worker.run()

            self.assertEqual(len(manager.launched), 2)
            self.assertEqual(manager.stopped, [1, 2])
            self.assertEqual(
                [item.exit_calls for item in connected_sessions],
                [1, 1],
            )


if __name__ == "__main__":
    unittest.main()
