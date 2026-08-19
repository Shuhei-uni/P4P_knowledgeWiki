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


def snapshot(
    iteration: int | None,
    *,
    flow_time: float | None = None,
    continuity: float = 1e-4,
) -> dict:
    return {
        "progress": {"iteration": iteration},
        "runtime": {"flow_time": flow_time},
        "monitors": {
            "residual": {
                "last_values": {"continuity": continuity} if iteration is not None else {},
            }
        },
        "fluent_version": "25.2.0",
    }


class CheckConnectionStatusTests(unittest.TestCase):
    def test_activity_is_running_when_iteration_advances(self) -> None:
        activity, reason = check_connection.classify_activity(snapshot(100), snapshot(106))
        self.assertEqual(activity, "RUNNING")
        self.assertEqual(reason, "iteration advanced")

    def test_activity_is_running_when_flow_time_advances_without_iteration_monitor(self) -> None:
        activity, reason = check_connection.classify_activity(
            snapshot(None, flow_time=0.10),
            snapshot(None, flow_time=0.12),
        )
        self.assertEqual(activity, "RUNNING")
        self.assertEqual(reason, "flow time advanced")

    def test_unchanged_progress_is_quiescent_not_idle(self) -> None:
        activity, reason = check_connection.classify_activity(snapshot(100), snapshot(100))
        self.assertEqual(activity, "QUIESCENT")
        self.assertIn("no progress detected", reason)

        output = io.StringIO()
        with redirect_stdout(output):
            check_connection.print_activity_summary(
                snapshot(100),
                snapshot(100),
                activity_window_seconds=2,
            )
        self.assertIn("QUIESCENT", output.getvalue())
        self.assertIn("not proof of idle", output.getvalue())
        self.assertNotIn("Activity : IDLE", output.getvalue())

    def test_status_summary_prints_delta_version_and_latest_residuals(self) -> None:
        first = snapshot(1250, flow_time=0.75, continuity=1.2e-4)
        second = snapshot(1255, flow_time=0.76, continuity=9.0e-5)
        output = io.StringIO()

        with redirect_stdout(output):
            activity = check_connection.print_activity_summary(
                first,
                second,
                activity_window_seconds=2,
            )

        text = output.getvalue()
        self.assertEqual(activity, "RUNNING")
        self.assertIn("Activity : RUNNING", text)
        self.assertIn("Iteration: 1250 -> 1255 (+5 in 2 s)", text)
        self.assertIn("Flow time: 0.75 -> 0.76 (+0.01 s)", text)
        self.assertIn("Fluent   : 25.2.0", text)
        self.assertIn("continuity", text)
        self.assertIn("9e-05", text)

    def test_snapshot_passes_previous_state_to_monitor(self) -> None:
        first = snapshot(42)
        second = snapshot(43)
        with patch.object(check_connection, "collect_snapshot", return_value=second) as collect:
            value, error = check_connection._collect_snapshot_with_timeout(
                object(),
                timeout_seconds=1,
                previous_state=first,
            )
        self.assertIsNone(error)
        self.assertEqual(value, second)
        collect.assert_called_once_with(
            unittest.mock.ANY,
            previous_state=first,
            monitor_sets=("residual",),
        )

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

    def test_console_stream_is_opt_in_and_prints_new_fluent_output(self) -> None:
        transcript = SimpleNamespace(
            is_streaming=True,
            stop=MagicMock(),
            start=MagicMock(),
        )
        solver = SimpleNamespace(transcript=transcript)
        output = io.StringIO()

        with redirect_stdout(output):
            returned = check_connection.start_console_stream(solver)

        self.assertIs(returned, transcript)
        transcript.stop.assert_called_once_with()
        transcript.start.assert_called_once_with(write_to_stdout=True)
        self.assertIn("Console  : STREAMING", output.getvalue())


if __name__ == "__main__":
    unittest.main()
