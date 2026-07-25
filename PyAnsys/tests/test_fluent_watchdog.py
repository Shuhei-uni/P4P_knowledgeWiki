from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.bridge import (  # noqa: E402
    AtomicJsonFile,
    BridgePaths,
    ConnectionDocumentError,
    ConnectionPublisher,
    FluentEndpoint,
    parse_server_info_text,
    read_latest_connection,
)
from pyansys_fluent.fluent_watchdog import (  # noqa: E402
    FluentProcessManager,
    FluentWatchdog,
    ManagedFluentProcess,
    RestartBudget,
    RestartLimitExceeded,
    WatchdogConfig,
)


class FakeProcess:
    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.returncode = None
        self.stdin = None
        self.killed = False

    def poll(self):
        return self.returncode

    def terminate(self) -> None:
        self.returncode = 0

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9

    def wait(self, timeout=None):
        return self.returncode


class FakeHandle:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeTreeToken:
    def __init__(self, process: FakeProcess) -> None:
        self.process = process
        self.closed = False

    def close(self) -> None:
        self.closed = True
        self.process.returncode = 0


def managed_process(root: Path, generation: int) -> ManagedFluentProcess:
    return ManagedFluentProcess(
        process=FakeProcess(1000 + generation),
        generation=generation,
        launched_unix_seconds=1_700_000_000 + generation,
        server_info_path=root / f"server-info-{generation}.txt",
        stdout_path=root / f"stdout-{generation}.log",
        stderr_path=root / f"stderr-{generation}.log",
        stdout_handle=FakeHandle(),
        stderr_handle=FakeHandle(),
    )


class FakeProcessManager:
    def __init__(
        self, root: Path, *, events: list[str] | None = None
    ) -> None:
        self.root = root
        self.events = events
        self.launched: list[ManagedFluentProcess] = []
        self.stopped: list[int] = []

    def launch(self, generation: int) -> ManagedFluentProcess:
        managed = managed_process(self.root, generation)
        self.launched.append(managed)
        return managed

    def wait_for_server_info(
        self, managed: ManagedFluentProcess
    ) -> Path:
        managed.server_info_path.write_text(
            f"127.0.0.1:{51000 + managed.generation}\n"
            f"secret-{managed.generation}\n",
            encoding="utf-8",
        )
        return managed.server_info_path

    def stop(self, managed: ManagedFluentProcess | None) -> None:
        if managed is None:
            return
        if self.events is not None:
            self.events.append(f"stop-{managed.generation}")
        self.stopped.append(managed.generation)
        managed.process.returncode = 0
        managed.stdout_handle.close()
        managed.stderr_handle.close()
        managed.server_info_path.unlink(missing_ok=True)


class SequenceSession:
    def __init__(
        self,
        health: list[bool],
        *,
        stop_event: threading.Event | None = None,
        process_to_kill: FakeProcess | None = None,
        events: list[str] | None = None,
    ) -> None:
        self.health = list(health)
        self.stop_event = stop_event
        self.process_to_kill = process_to_kill
        self.events = events
        self.health_calls = 0
        self.exit_calls = 0

    def is_active(self) -> bool:
        self.health_calls += 1
        value = self.health.pop(0) if self.health else True
        if not self.health and self.stop_event is not None:
            self.stop_event.set()
        return value

    def get_fluent_version(self) -> str:
        if self.process_to_kill is not None:
            self.process_to_kill.returncode = 99
        return "25.2-test"

    def exit(self, **_kwargs) -> None:
        self.exit_calls += 1
        if self.events is not None:
            self.events.append("detach")


def watchdog_config(root: Path, **overrides) -> WatchdogConfig:
    values = {
        "fluent_exe": root / "fluent.exe",
        "bridge_dir": root / "bridge",
        "advertised_host": "10.0.0.5",
        "runtime_dir": root / "runtime",
        "health_timeout_seconds": 0.1,
        "health_interval_seconds": 0.001,
        "heartbeat_interval_seconds": 0.001,
        "poll_interval_seconds": 0.001,
        "restart_delay_seconds": 0,
        "max_restarts": 2,
    }
    values.update(overrides)
    return WatchdogConfig(**values)


class BridgeTests(unittest.TestCase):
    def test_atomic_json_replacement_leaves_no_partial_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            store = AtomicJsonFile(path)
            store.write({"generation": 4})
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8"))["generation"], 4
            )
            self.assertFalse(
                any(".tmp-" in child.name for child in path.parent.iterdir())
            )
            with mock.patch(
                "pyansys_fluent.bridge.os.replace",
                side_effect=OSError("simulated replace failure"),
            ):
                with self.assertRaises(OSError):
                    store.write({"generation": 5})
            self.assertEqual(store.read()["generation"], 4)
            self.assertFalse(
                any(".tmp-" in child.name for child in path.parent.iterdir())
            )

    def test_server_info_parser_redacts_repr_and_replaces_host(self) -> None:
        endpoint = parse_server_info_text(
            "127.0.0.1:51382\nvery-secret\n",
            advertised_host="10.0.0.5",
        )
        self.assertEqual(endpoint.host, "10.0.0.5")
        self.assertEqual(endpoint.port, 51382)
        self.assertEqual(endpoint.password, "very-secret")
        self.assertNotIn("very-secret", repr(endpoint))

    def test_non_running_publication_clears_endpoint_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = BridgePaths(Path(tmp))
            publisher = ConnectionPublisher(paths)
            endpoint = FluentEndpoint("10.0.0.5", 51382, "very-secret")
            publisher.publish(
                "running",
                generation=3,
                previous_generation=2,
                heartbeat_sequence=8,
                endpoint=endpoint,
            )
            running = AtomicJsonFile(paths.latest_connection).read()
            self.assertEqual(running["password"], "very-secret")

            publisher.publish(
                "restarting",
                generation=3,
                previous_generation=2,
                heartbeat_sequence=9,
            )
            restarting = AtomicJsonFile(paths.latest_connection).read()
            self.assertIsNone(restarting["host"])
            self.assertIsNone(restarting["port"])
            self.assertIsNone(restarting["password"])

    def test_latest_connection_rejects_stale_and_old_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 7, 24, tzinfo=timezone.utc)
            ConnectionPublisher(BridgePaths(root)).publish(
                "running",
                generation=13,
                previous_generation=12,
                heartbeat_sequence=1,
                endpoint=FluentEndpoint("10.0.0.5", 51382, "secret"),
                updated_at=(now - timedelta(seconds=31)).isoformat(),
            )
            with self.assertRaises(ConnectionDocumentError):
                read_latest_connection(
                    root, max_age_seconds=30, now=now
                )
            with self.assertRaises(ConnectionDocumentError):
                read_latest_connection(root, min_generation=14)


class WatchdogPolicyTests(unittest.TestCase):
    def test_remote_grpc_options_are_launch_time_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = watchdog_config(
                root,
                allow_remote_host=True,
                insecure_mode=True,
            )
            self.assertEqual(
                config.grpc_launch_args(),
                ("-grpc-allow-remote-host", "-grpc-insecure-mode"),
            )

    def test_secure_local_launch_has_no_remote_grpc_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(watchdog_config(root).grpc_launch_args(), ())

    def test_production_defaults_match_recovery_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = WatchdogConfig(
                fluent_exe=root / "fluent.exe",
                bridge_dir=root / "bridge",
                advertised_host="10.0.0.5",
                runtime_dir=root / "runtime",
            )
            self.assertEqual(config.health_interval_seconds, 10.0)
            self.assertEqual(config.health_timeout_seconds, 10.0)
            self.assertEqual(config.restart_delay_seconds, 5.0)
            self.assertEqual(config.consecutive_health_failures, 3)
            self.assertEqual(config.max_restarts, 3)
            self.assertEqual(config.restart_window_seconds, 600.0)

    def test_restart_budget_is_rolling_and_bounded(self) -> None:
        budget = RestartBudget(2, 10)
        self.assertEqual(budget.record(0), 1)
        self.assertEqual(budget.record(5), 2)
        with self.assertRaises(RestartLimitExceeded):
            budget.record(6)
        fresh = RestartBudget(1, 10)
        self.assertEqual(fresh.record(0), 1)
        self.assertEqual(fresh.record(11), 1)

    def test_process_tree_token_is_closed_with_all_handles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = watchdog_config(root)
            manager = FluentProcessManager(config)
            managed = managed_process(root, 1)
            managed.server_info_path.write_text(
                "127.0.0.1:50001\nsecret\n", encoding="utf-8"
            )
            token = FakeTreeToken(managed.process)
            managed.process_tree_token = token
            manager.stop(managed)
            self.assertTrue(token.closed)
            self.assertTrue(managed.stdout_handle.closed)
            self.assertTrue(managed.stderr_handle.closed)
            self.assertFalse(managed.server_info_path.exists())

    def test_three_consecutive_health_failures_trigger_one_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = watchdog_config(root)
            stop_event = threading.Event()
            manager = FakeProcessManager(root)
            first = SequenceSession([True, False, False, False])
            second = SequenceSession([True, True], stop_event=stop_event)
            sessions = [first, second]
            watchdog = FluentWatchdog(
                config,
                process_manager=manager,
                connect_factory=lambda _path, _config: sessions.pop(0),
                stop_event=stop_event,
            )
            watchdog.run()
            self.assertEqual(first.health_calls, 4)
            self.assertEqual(len(manager.launched), 2)
            self.assertEqual(manager.stopped, [1, 2])
            final = AtomicJsonFile(
                BridgePaths(config.bridge_dir).latest_connection
            ).read()
            self.assertEqual(final["status"], "stopped")
            self.assertIsNone(final["password"])
            self.assertEqual(final["restart_count_total"], 1)
            self.assertEqual(first.exit_calls, 1)
            self.assertEqual(second.exit_calls, 1)

    def test_successful_health_resets_consecutive_failure_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = watchdog_config(root)
            stop_event = threading.Event()
            manager = FakeProcessManager(root)
            session = SequenceSession(
                [True, False, False, True, False, False, True],
                stop_event=stop_event,
            )
            watchdog = FluentWatchdog(
                config,
                process_manager=manager,
                connect_factory=lambda _path, _config: session,
                stop_event=stop_event,
            )
            watchdog.run()
            self.assertEqual(len(manager.launched), 1)
            self.assertEqual(manager.stopped, [1])

    def test_process_exit_restarts_without_waiting_for_health_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = watchdog_config(root)
            stop_event = threading.Event()
            manager = FakeProcessManager(root)
            sessions: list[SequenceSession] = []

            def connect(_path, _config):
                if len(manager.launched) == 1:
                    session = SequenceSession(
                        [True],
                        process_to_kill=manager.launched[-1].process,
                    )
                else:
                    session = SequenceSession(
                        [True, True], stop_event=stop_event
                    )
                sessions.append(session)
                return session

            watchdog = FluentWatchdog(
                config,
                process_manager=manager,
                connect_factory=connect,
                stop_event=stop_event,
            )
            watchdog.run()
            self.assertEqual(len(manager.launched), 2)
            self.assertEqual(sessions[0].health_calls, 1)
            self.assertEqual(manager.stopped, [1, 2])

    def test_restart_reason_redacts_server_info_password(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = watchdog_config(root)
            stop_event = threading.Event()
            manager = FakeProcessManager(root)
            attempts = [0]

            def connect(_path, _config):
                attempts[0] += 1
                if attempts[0] == 1:
                    raise RuntimeError("connection rejected secret-1")
                return SequenceSession([True, True], stop_event=stop_event)

            watchdog = FluentWatchdog(
                config,
                process_manager=manager,
                connect_factory=connect,
                stop_event=stop_event,
            )
            watchdog.run()
            document_text = (
                BridgePaths(config.bridge_dir)
                .latest_connection.read_text(encoding="utf-8")
            )
            self.assertNotIn("secret-1", document_text)
            self.assertIn("<redacted>", document_text)

    def test_generation_is_seeded_from_previous_watchdog_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = watchdog_config(root)
            ConnectionPublisher(BridgePaths(config.bridge_dir)).publish(
                "stopped",
                generation=14,
                previous_generation=13,
                heartbeat_sequence=20,
            )
            stop_event = threading.Event()
            manager = FakeProcessManager(root)
            session = SequenceSession(
                [True, True], stop_event=stop_event
            )
            FluentWatchdog(
                config,
                process_manager=manager,
                connect_factory=lambda _path, _config: session,
                stop_event=stop_event,
            ).run()
            self.assertEqual(manager.launched[0].generation, 15)
            final = AtomicJsonFile(
                BridgePaths(config.bridge_dir).latest_connection
            ).read()
            self.assertEqual(final["generation"], 15)
            self.assertEqual(final["previous_generation"], 14)

    def test_monitor_client_detaches_before_process_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = watchdog_config(root)
            events: list[str] = []
            stop_event = threading.Event()
            manager = FakeProcessManager(root, events=events)
            session = SequenceSession(
                [True, True],
                stop_event=stop_event,
                events=events,
            )
            FluentWatchdog(
                config,
                process_manager=manager,
                connect_factory=lambda _path, _config: session,
                stop_event=stop_event,
            ).run()
            self.assertEqual(events, ["detach", "stop-1"])


if __name__ == "__main__":
    unittest.main()
