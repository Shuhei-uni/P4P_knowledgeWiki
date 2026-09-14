from __future__ import annotations

import importlib.util
from contextlib import redirect_stdout
import io
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


def solver_with_iterating(value: object) -> SimpleNamespace:
    return SimpleNamespace(
        settings=SimpleNamespace(
            solution=SimpleNamespace(
                run_calculation=SimpleNamespace(iterating=lambda: value),
            ),
        ),
    )


class CheckConnectionStatusTests(unittest.TestCase):
    def test_activity_is_running_only_for_exact_boolean_true(self) -> None:
        state, reason = check_connection.read_iterating_state(solver_with_iterating(True))
        self.assertTrue(state)
        self.assertEqual(reason, "solution.run_calculation.iterating returned true")

    def test_false_is_not_running(self) -> None:
        state, reason = check_connection.read_iterating_state(solver_with_iterating(False))
        self.assertFalse(state)
        self.assertIn("not true", reason)

    def test_unknown_return_is_not_running(self) -> None:
        state, reason = check_connection.read_iterating_state(solver_with_iterating(None))
        self.assertFalse(state)
        self.assertIn("not true", reason)

    def test_truthy_non_boolean_return_is_not_running(self) -> None:
        state, reason = check_connection.read_iterating_state(solver_with_iterating(1))
        self.assertFalse(state)
        self.assertIn("not true", reason)

    def test_query_exception_is_not_running(self) -> None:
        def failing_query() -> bool:
            raise RuntimeError("stale Fluent value")

        solver = solver_with_iterating(False)
        solver.settings.solution.run_calculation.iterating = failing_query
        state, reason = check_connection.read_iterating_state(solver)
        self.assertFalse(state)
        self.assertIn("did not return true", reason)
        self.assertIn("RuntimeError", reason)

    def test_missing_query_is_not_running(self) -> None:
        solver = SimpleNamespace(
            settings=SimpleNamespace(
                solution=SimpleNamespace(run_calculation=SimpleNamespace()),
            ),
        )
        state, reason = check_connection.read_iterating_state(solver)
        self.assertFalse(state)
        self.assertIn("did not return true", reason)

    def test_activity_query_timeout_is_not_running(self) -> None:
        release = Event()
        solver = solver_with_iterating(False)
        solver.settings.solution.run_calculation.iterating = lambda: release.wait(timeout=1)

        state, reason = check_connection.read_iterating_state_with_timeout(solver, 0.001)

        self.assertFalse(state)
        self.assertIn("did not return true", reason)
        self.assertIn("TimeoutError", reason)
        release.set()

    def test_activity_output_is_binary_and_has_no_residuals(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            check_connection.print_activity(False, "query did not return true")
        text = output.getvalue()
        self.assertIn("Activity : NOT RUNNING", text)
        self.assertNotIn("UNKNOWN", text)
        self.assertNotIn("Residual", text)
        self.assertNotIn("Monitor", text)

    def test_tcp_output_is_binary_and_uses_tcp_label(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            check_connection.print_endpoint_probe(
                {
                    "status": "unavailable",
                    "detail": "configure FLUENT_IP and FLUENT_PORT",
                },
            )
        text = output.getvalue()
        self.assertIn("TCP      : NOT CONNECTED", text)
        self.assertNotIn("Endpoint", text)
        self.assertNotIn("UNKNOWN", text)

    def test_blocking_fluent_call_is_bounded_by_timeout(self) -> None:
        release = Event()
        value, error = check_connection._call_with_timeout(
            lambda: release.wait(timeout=1),
            timeout_seconds=0.001,
        )
        self.assertIsNone(value)
        self.assertIsInstance(error, TimeoutError)
        release.set()

    def test_endpoint_probe_reports_reachable_target(self) -> None:
        connection = MagicMock()
        connection.__enter__.return_value = connection
        with (
            patch.dict(
                check_connection.os.environ,
                {"FLUENT_IP": "192.0.2.10", "FLUENT_PORT": "50000"},
                clear=True,
            ),
            patch.object(check_connection, "load_dotenv"),
            patch.object(check_connection.socket, "create_connection", return_value=connection) as create_connection,
        ):
            probe = check_connection.probe_endpoint("1", timeout_seconds=2)

        create_connection.assert_called_once_with(("192.0.2.10", 50000), timeout=2)
        self.assertEqual(probe["status"], "reachable")
        self.assertEqual(probe["target"], "192.0.2.10:50000")

    def test_endpoint_probe_reports_refused_target(self) -> None:
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
        ):
            probe = check_connection.probe_endpoint("1", timeout_seconds=2)

        self.assertEqual(probe["status"], "unreachable")
        self.assertIn("Connection refused", probe["detail"])

if __name__ == "__main__":
    unittest.main()
