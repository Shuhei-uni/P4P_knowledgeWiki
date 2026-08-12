from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "connection" / "check_connection.py"

SPEC = importlib.util.spec_from_file_location("check_connection", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
check_connection = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_connection)


class CheckConnectionStatusTests(unittest.TestCase):
    def test_status_prints_iteration_and_latest_residuals(self) -> None:
        snapshot = {
            "progress": {"iteration": 1250},
            "monitors": {
                "residual": {
                    "last_values": {"continuity": 1.2e-4, "x-velocity": 3.4e-5},
                }
            },
            "runtime": {"flow_time": 0.75},
            "read_errors": [],
        }
        output = io.StringIO()

        with patch.object(check_connection, "collect_snapshot", return_value=snapshot):
            with redirect_stdout(output):
                check_connection.print_server_status(object())

        self.assertEqual(
            output.getvalue(),
            "Current iteration: 1250\n"
            "Latest residuals:\n"
            "  continuity: 0.00012\n"
            "  x-velocity: 3.4e-05\n"
            "Flow time: 0.75\n",
        )

    def test_status_reports_missing_monitor_iteration_without_failing(self) -> None:
        snapshot = {
            "progress": {"iteration": None},
            "monitors": {"residual": {"error": "monitor set is not exposed by Fluent"}},
            "runtime": {},
            "read_errors": ["monitor residual: unavailable"],
        }
        output = io.StringIO()

        with patch.object(check_connection, "collect_snapshot", return_value=snapshot):
            with redirect_stdout(output):
                check_connection.print_server_status(object())

        self.assertIn("Current iteration: unavailable", output.getvalue())
        self.assertIn("Latest residuals: unavailable", output.getvalue())
        self.assertIn("Status notes:", output.getvalue())

    def test_configuration_state_reads_calculation_and_dpm_branches(self) -> None:
        run_calculation = SimpleNamespace(
            get_active_child_names=lambda: ["number_of_iterations"],
            get_state=lambda: {"number_of_iterations": 500},
        )
        tracking = SimpleNamespace(get_state=lambda: {"enabled": True})
        interaction = SimpleNamespace(get_state=lambda: {"coupled": False})
        general_settings = SimpleNamespace(
            interaction=interaction,
            get_state=lambda: {"tracking": True},
        )
        dpm = SimpleNamespace(tracking=tracking, general_settings=general_settings)
        solver = SimpleNamespace(
            settings=SimpleNamespace(
                solution=SimpleNamespace(run_calculation=run_calculation),
                setup=SimpleNamespace(models=SimpleNamespace(discrete_phase=dpm)),
            )
        )
        output = io.StringIO()

        with redirect_stdout(output):
            check_connection.print_configuration_state(solver)

        text = output.getvalue()
        self.assertIn('run_calculation_active_children: [\n  "number_of_iterations"\n]', text)
        self.assertIn('dpm_tracking_state: {\n  "enabled": true\n}', text)
        self.assertIn('dpm_interaction_state: {\n  "coupled": false\n}', text)

    def test_wait_polls_the_full_window_and_reports_the_highest_iteration(self) -> None:
        unavailable = {
            "progress": {"iteration": None},
            "monitors": {"residual": {}},
            "runtime": {},
            "read_errors": [],
        }
        lower = {
            "progress": {"iteration": 42},
            "monitors": {"residual": {"last_values": {"continuity": 1e-4}}},
            "runtime": {},
            "read_errors": [],
        }
        higher = {
            "progress": {"iteration": 57},
            "monitors": {"residual": {"last_values": {"continuity": 2e-4}}},
            "runtime": {},
            "read_errors": [],
        }
        output = io.StringIO()
        clock = [0.0]

        def sleep(seconds: float) -> None:
            clock[0] += seconds

        with patch.object(check_connection, "collect_snapshot", side_effect=[unavailable, lower, higher]):
            with redirect_stdout(output):
                received = check_connection.wait_for_live_server_status(
                    object(),
                    timeout_seconds=3,
                    poll_interval_seconds=1,
                    monotonic_fn=lambda: clock[0],
                    sleep_fn=sleep,
                )

        self.assertTrue(received)
        self.assertIn("Completed 3 seconds of polling (2 successful monitor snapshots).", output.getvalue())
        self.assertIn("Highest iteration observed: 57", output.getvalue())
        self.assertNotIn("Highest iteration observed: 42", output.getvalue())

    def test_wait_times_out_when_no_progress_is_exposed(self) -> None:
        unavailable = {
            "progress": {"iteration": None},
            "monitors": {"residual": {"error": "monitor unavailable"}},
            "runtime": {},
            "read_errors": [],
        }
        times = iter([0.0, 0.0, 1.0])
        output = io.StringIO()

        with patch.object(check_connection, "collect_snapshot", return_value=unavailable):
            with redirect_stdout(output):
                received = check_connection.wait_for_live_server_status(
                    object(),
                    timeout_seconds=1,
                    poll_interval_seconds=1,
                    monotonic_fn=lambda: next(times),
                    sleep_fn=lambda _seconds: None,
                )

        self.assertFalse(received)
        self.assertIn("Timed out after 1 seconds", output.getvalue())

    def test_blocking_fluent_call_is_bounded_by_timeout(self) -> None:
        release = Event()
        value, error = check_connection._call_with_timeout(
            lambda: release.wait(timeout=1),
            timeout_seconds=0.001,
        )

        self.assertIsNone(value)
        self.assertIsInstance(error, TimeoutError)
        release.set()

    def test_endpoint_probe_reports_a_reachable_configured_tcp_target(self) -> None:
        connection = MagicMock()
        connection.__enter__.return_value = connection
        output = io.StringIO()

        with (
            patch.dict(
                check_connection.os.environ,
                {"FLUENT_IP": "192.0.2.10", "FLUENT_PORT": "50000"},
                clear=True,
            ),
            patch.object(check_connection, "load_dotenv"),
            patch.object(check_connection.socket, "create_connection", return_value=connection) as create_connection,
            redirect_stdout(output),
        ):
            verdict = check_connection.print_endpoint_reachability("1", timeout_seconds=3)

        create_connection.assert_called_once_with(("192.0.2.10", 50000), timeout=3)
        self.assertEqual(verdict, "reachable")
        self.assertIn("Target TCP reachability: reachable (192.0.2.10:50000", output.getvalue())

    def test_endpoint_probe_reports_a_refused_tcp_target(self) -> None:
        output = io.StringIO()

        with (
            patch.dict(
                check_connection.os.environ,
                {"FLUENT_IP": "192.0.2.10", "FLUENT_PORT": "50000"},
                clear=True,
            ),
            patch.object(check_connection, "load_dotenv"),
            patch.object(
                check_connection.socket,
                "create_connection",
                side_effect=ConnectionRefusedError("Connection refused"),
            ),
            redirect_stdout(output),
        ):
            check_connection.print_endpoint_reachability("1", timeout_seconds=3)

        self.assertIn("Target TCP reachability: unreachable", output.getvalue())
        self.assertIn("Connection refused", output.getvalue())


if __name__ == "__main__":
    unittest.main()
