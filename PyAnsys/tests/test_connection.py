from __future__ import annotations

import sys
import unittest
import contextlib
import io
import os
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import endpoint_env_namespace  # noqa: E402
from pyansys_fluent import connection  # noqa: E402


class EndpointEnvironmentNamespaceTests(unittest.TestCase):
    def test_default_endpoint_uses_unsuffixed_fluent_variables(self) -> None:
        self.assertEqual(endpoint_env_namespace(None), ("1", "FLUENT", ""))

    def test_numbered_endpoint_preserves_existing_fluent_suffix_convention(self) -> None:
        self.assertEqual(endpoint_env_namespace("3"), ("3", "FLUENT", "3"))

    def test_student_endpoint_uses_named_student_variables(self) -> None:
        self.assertEqual(endpoint_env_namespace("student"), ("student", "STUDENT", ""))


class ConnectionCompatibilityTests(unittest.TestCase):
    """Exercise routing with fake clients; no .env reads or network calls."""

    def setUp(self) -> None:
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.dict(os.environ, {}, clear=True))
        self.load_dotenv = stack.enter_context(patch.object(connection, "load_dotenv"))
        self.socket_connect = stack.enter_context(
            patch.object(connection.socket, "create_connection")
        )
        self.local_launch = stack.enter_context(
            patch.object(connection, "_launch_local_fluent")
        )
        self.output = io.StringIO()
        stack.enter_context(contextlib.redirect_stdout(self.output))
        ansys = ModuleType("ansys")
        fluent = ModuleType("ansys.fluent")
        core = ModuleType("ansys.fluent.core")
        core.connect_to_fluent = MagicMock()
        fluent.core = core
        ansys.fluent = fluent
        stack.enter_context(patch.dict(sys.modules, {
            "ansys": ansys, "ansys.fluent": fluent, "ansys.fluent.core": core,
        }))
        self.client_connect = core.connect_to_fluent

    def configure_endpoint(self, prefix: str = "FLUENT", suffix: str = "") -> None:
        os.environ.update({
            f"{prefix}_IP{suffix}": "192.0.2.10",
            f"{prefix}_PORT{suffix}": "12345",
            f"{prefix}_PASSWORD{suffix}": "test-placeholder",
        })

    def test_default_transcript_and_no_tcp_preflight_are_preserved(self) -> None:
        self.configure_endpoint()
        os.environ["FLUENT_STREAM_TRANSCRIPT"] = "false"
        connection.connect()
        self.assertTrue(self.client_connect.call_args.kwargs["start_transcript"])
        self.assertFalse(self.client_connect.call_args.kwargs["cleanup_on_exit"])
        self.socket_connect.assert_not_called()
        self.load_dotenv.assert_called_once_with(connection._ENV_FILE)
        for value in ("192.0.2.10", "12345", "test-placeholder"):
            self.assertNotIn(value, self.output.getvalue())

    def test_explicit_transcript_value_overrides_environment(self) -> None:
        self.configure_endpoint()
        os.environ["FLUENT_STREAM_TRANSCRIPT"] = "true"
        connection.connect(start_transcript=False)
        self.assertFalse(self.client_connect.call_args.kwargs["start_transcript"])

    def test_opt_in_transcript_environment_uses_numbered_endpoint(self) -> None:
        self.configure_endpoint(suffix="3")
        os.environ.update({
            "FLUENT_STREAM_TRANSCRIPT": "true",
            "FLUENT_STREAM_TRANSCRIPT3": "false",
        })
        connection.connect("3", start_transcript=None)
        self.assertFalse(self.client_connect.call_args.kwargs["start_transcript"])

    def test_named_endpoint_keeps_its_own_connection_and_optional_settings(self) -> None:
        self.configure_endpoint(prefix="STUDENT")
        os.environ.update({
            "STUDENT_STREAM_TRANSCRIPT": "false",
            "STUDENT_TCP_PREFLIGHT_TIMEOUT_SECONDS": "2.5",
            "FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS": "7",
        })
        connection.connect("student", start_transcript=None)
        self.assertFalse(self.client_connect.call_args.kwargs["start_transcript"])
        self.socket_connect.assert_called_once_with(("192.0.2.10", 12345), timeout=2.5)

    def test_explicit_timeout_takes_precedence(self) -> None:
        self.configure_endpoint(suffix="2")
        os.environ["FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS2"] = "9"
        connection.connect("2", tcp_timeout_seconds=1.5)
        self.socket_connect.assert_called_once_with(("192.0.2.10", 12345), timeout=1.5)

    def test_zero_timeout_disables_configured_preflight(self) -> None:
        self.configure_endpoint()
        os.environ["FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS"] = "9"
        connection.connect(tcp_timeout_seconds=0)
        self.socket_connect.assert_not_called()

    def test_numbered_timeout_falls_back_to_shared_setting(self) -> None:
        self.configure_endpoint(suffix="2")
        os.environ["FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS"] = "4"
        os.environ["FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS2"] = " "
        connection.connect("2")
        self.socket_connect.assert_called_once_with(("192.0.2.10", 12345), timeout=4.0)

    def test_failed_preflight_stops_before_pyfluent_connect(self) -> None:
        self.configure_endpoint()
        self.socket_connect.side_effect = OSError("test connection refused")
        with self.assertRaisesRegex(TimeoutError, "configured server after 2.0s"):
            connection.connect(tcp_timeout_seconds=2)
        self.client_connect.assert_not_called()

    def test_server_info_route_bypasses_tcp_probe(self) -> None:
        os.environ["STUDENT_SERVER_INFO_FILE"] = "/test/server-info.txt"
        with patch.object(connection.Path, "exists", return_value=True):
            connection.connect("student", start_transcript=False, tcp_timeout_seconds=2)
        self.socket_connect.assert_not_called()
        self.client_connect.assert_called_once_with(
            server_info_file_name="/test/server-info.txt",
            allow_remote_host=True, cleanup_on_exit=False,
            start_transcript=False, insecure_mode=False,
        )

    def test_missing_named_server_info_reports_correct_variable(self) -> None:
        os.environ["STUDENT_SERVER_INFO_FILE"] = "/test/missing.txt"
        with patch.object(connection.Path, "exists", return_value=False):
            with self.assertRaisesRegex(FileNotFoundError, "STUDENT_SERVER_INFO_FILE"):
                connection.connect("student")
        self.client_connect.assert_not_called()

    def test_local_launch_preserves_route_and_explicit_transcript(self) -> None:
        os.environ["FLUENT_LOCAL_EXE2"] = "/test/fluent"
        connection.connect("2", start_transcript=False, tcp_timeout_seconds=2)
        self.local_launch.assert_called_once_with(
            suffix="2", insecure_mode=False, start_transcript=False,
        )
        self.socket_connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
