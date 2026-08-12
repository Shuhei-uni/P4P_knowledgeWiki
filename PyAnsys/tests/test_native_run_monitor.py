from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import pyansys_fluent.native_run_monitor as monitor  # noqa: E402


class FakeHealth:
    def status(self):
        return "SERVING"

    def check_health(self):
        return "SERVING"


class FakeScheme:
    def __init__(self, values: dict[str, object]):
        self.values = values
        self.calls: list[str] = []

    def eval(self, expression: str):
        self.calls.append(expression)
        variable = expression.split("'")[-1].rstrip(")")
        if variable not in self.values:
            raise RuntimeError(f"missing {variable}")
        return self.values[variable]


class FakeMonitors:
    def __init__(self, iteration: int = 11):
        self.names = ["residual"]
        self.iteration = iteration

    def get_monitor_set_names(self):
        return self.names

    def get_monitor_set_data(self, *, monitor_set_name: str):
        if monitor_set_name not in self.names:
            raise RuntimeError("missing monitor")
        return [self.iteration - 1, self.iteration], {"continuity": [1.0e-2, 1.0e-3]}


class FakeSolver:
    def __init__(self, iteration: int = 11):
        self.health_check = FakeHealth()
        self.scheme = FakeScheme(
            {
                "number-of-iterations": iteration,
                "flow-time": 0.0,
                "time-step": 0.0,
                "physical-time-step": 0.0,
            }
        )
        self.monitors = FakeMonitors(iteration=iteration)
        self.exit_called = False
        self.force_exit_called = False

    def get_fluent_version(self):
        return "test-fluent"

    def exit(self):
        self.exit_called = True
        raise AssertionError("monitor must not shut down Fluent")

    def force_exit(self):
        self.force_exit_called = True
        raise AssertionError("monitor must not force-shut down Fluent")


class DeadSolver:
    class Health:
        def status(self):
            raise ConnectionError("health channel lost")

        def check_health(self):
            raise ConnectionError("health channel lost")

    def __init__(self):
        self.health_check = self.Health()
        self.scheme = self
        self.monitors = self

    def eval(self, _expression):
        raise ConnectionError("scheme channel lost")

    def get_fluent_version(self):
        raise ConnectionError("version channel lost")

    def get_monitor_set_names(self):
        raise ConnectionError("monitor channel lost")


class NativeRunMonitorTests(unittest.TestCase):
    def test_collect_snapshot_reports_progress_and_does_not_shutdown_solver(self) -> None:
        solver = FakeSolver(iteration=11)
        previous = {"progress": {"iteration": 10}}

        original_exists = monitor.remote_file_exists
        monitor.remote_file_exists = lambda _solver, path: path.endswith(".cas.h5")
        try:
            snapshot = monitor.collect_snapshot(
                solver,
                previous_state=previous,
                checkpoint_pairs=(monitor.CheckpointPair("run-500.cas.h5", "run-500.dat.h5"),),
            )
        finally:
            monitor.remote_file_exists = original_exists

        self.assertEqual(snapshot["progress"]["state"], "advancing")
        self.assertEqual(snapshot["progress"]["delta"], 1)
        self.assertEqual(snapshot["progress"]["source"], "monitor_x_value")
        self.assertEqual(snapshot["runtime"]["configured_number_of_iterations"], 11)
        self.assertEqual(snapshot["monitors"]["residual"]["latest_iteration"], 11)
        self.assertEqual(snapshot["checkpoints"][0]["status"], "partial")
        self.assertTrue(snapshot["read_only"])
        self.assertFalse(solver.exit_called)
        self.assertFalse(solver.force_exit_called)

    def test_collect_snapshot_uses_highest_iteration_when_monitor_history_is_unsorted(self) -> None:
        solver = FakeSolver(iteration=11)
        solver.monitors.get_monitor_set_data = lambda **_kwargs: (
            [4204, 4164, 4356, 4146],
            {"continuity": [0.21, 0.22, 0.19, 0.23]},
        )

        snapshot = monitor.collect_snapshot(solver)

        residual = snapshot["monitors"]["residual"]
        self.assertEqual(residual["latest_iteration"], 4356)
        self.assertEqual(residual["highest_iteration"], 4356)
        self.assertEqual(residual["last_values"]["continuity"], 0.19)
        self.assertEqual(snapshot["progress"]["iteration"], 4356)

    def test_retry_then_reconnect_persists_latest_state_and_events(self) -> None:
        attempts: list[str] = []
        sleeps: list[float] = []
        solver = FakeSolver(iteration=25)

        def connect_fn(server_id: str):
            attempts.append(server_id)
            if len(attempts) == 1:
                raise ConnectionError("temporary outage")
            return solver

        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            events_path = Path(directory) / "events.jsonl"
            config = monitor.MonitorConfig(
                server_id="student",
                once=True,
                reconnect_initial_delay_seconds=0.25,
                reconnect_max_delay_seconds=1.0,
                state_json=state_path,
                events_jsonl=events_path,
            )
            result = monitor.run_monitor(
                config,
                connect_fn=connect_fn,
                sleep_fn=sleeps.append,
            )

            self.assertEqual(result, 0)
            self.assertEqual(attempts, ["student", "student"])
            self.assertEqual(sleeps, [0.25])
            saved = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["progress"]["iteration"], 25)
            events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([event["event"] for event in events], ["reconnect_failed", "connected", "snapshot"])
            self.assertEqual(events[1]["case_identity"], "not_inferred_from_server_id")

    def test_retry_limit_returns_nonzero_without_claiming_solver_failure(self) -> None:
        events: list[dict[str, object]] = []
        sleeps: list[float] = []

        config = monitor.MonitorConfig(
            max_reconnect_attempts=2,
            once=True,
            reconnect_initial_delay_seconds=0.1,
            reconnect_max_delay_seconds=0.2,
        )
        result = monitor.run_monitor(
            config,
            connect_fn=lambda _server_id: (_ for _ in ()).throw(ConnectionError("offline")),
            sleep_fn=sleeps.append,
            emit_fn=events.append,
        )

        self.assertEqual(result, 2)
        self.assertEqual(sleeps, [0.1])
        self.assertEqual(events[-1]["event"], "retry_limit_exhausted")
        self.assertNotIn("solver_stopped", json.dumps(events))

    def test_snapshot_connection_loss_drops_client_and_reconnects(self) -> None:
        attempts: list[int] = []
        events: list[dict[str, object]] = []
        sleeps: list[float] = []
        healthy_solver = FakeSolver(iteration=40)

        def connect_fn(_server_id: str):
            attempts.append(1)
            return DeadSolver() if len(attempts) == 1 else healthy_solver

        config = monitor.MonitorConfig(
            once=True,
            reconnect_initial_delay_seconds=0.2,
            reconnect_max_delay_seconds=1.0,
        )
        result = monitor.run_monitor(
            config,
            connect_fn=connect_fn,
            sleep_fn=sleeps.append,
            emit_fn=events.append,
        )

        self.assertEqual(result, 0)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(sleeps, [0.2])
        self.assertEqual(
            [event["event"] for event in events],
            ["connected", "connection_lost", "connected", "snapshot"],
        )
        self.assertEqual(events[1]["action"], "drop_client_reference_and_reconnect_without_shutdown")
        self.assertFalse(healthy_solver.exit_called)


if __name__ == "__main__":
    unittest.main()
