from __future__ import annotations

from datetime import datetime, timedelta, timezone
import io
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

from pyansys_fluent.bridge import (
    BridgePaths,
    ConnectionPublisher,
    FluentEndpoint,
)
from pyansys_fluent.connection import connect


class _Health:
    def __init__(self, result: str = "SERVING"):
        self.result = result

    def check_health(self) -> str:
        return self.result


class _ServingHealth:
    def is_serving(self) -> bool:
        return True


class _Session:
    def __init__(self, *, health: str = "SERVING", version: str = "25.2.0"):
        self.health_check = _Health(health)
        self.version = version

    def get_fluent_version(self) -> str:
        return self.version


class _ServingSession(_Session):
    def __init__(self, *, version: str = "25.2.0"):
        super().__init__(version=version)
        self.health_check = _ServingHealth()


def _fake_pyfluent(connect_mock: mock.Mock) -> dict[str, types.ModuleType]:
    ansys = types.ModuleType("ansys")
    fluent = types.ModuleType("ansys.fluent")
    core = types.ModuleType("ansys.fluent.core")
    core.connect_to_fluent = connect_mock
    ansys.fluent = fluent
    fluent.core = core
    return {
        "ansys": ansys,
        "ansys.fluent": fluent,
        "ansys.fluent.core": core,
    }


class BridgeConnectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.bridge_dir = Path(self.temporary_directory.name).resolve()
        self.publisher = ConnectionPublisher(BridgePaths(self.bridge_dir))

    def _publish(
        self,
        generation: int,
        *,
        port: int = 50001,
        password: str = "private-password",
        updated_at: str | None = None,
    ) -> None:
        self.publisher.publish(
            "running",
            generation=generation,
            previous_generation=generation - 1,
            heartbeat_sequence=generation,
            endpoint=FluentEndpoint("10.0.0.5", port, password),
            fluent_pid=1000 + generation,
            fluent_version="25.2.0",
            updated_at=updated_at,
        )

    def _connect_with_environment(
        self,
        connect_mock: mock.Mock,
        environment: dict[str, str],
        **kwargs,
    ):
        with (
            mock.patch.dict(os.environ, environment, clear=True),
            mock.patch("pyansys_fluent.connection.load_dotenv", return_value=False),
            mock.patch.dict(sys.modules, _fake_pyfluent(connect_mock)),
        ):
            return connect(**kwargs)

    def test_bridge_is_reread_and_remote_connection_is_forced(self) -> None:
        self._publish(13, port=50013, password="first-password")
        connect_mock = mock.Mock(side_effect=[_Session(), _Session()])
        environment = {
            "FLUENT_BRIDGE_DIR": str(self.bridge_dir),
            "FLUENT_ALLOW_REMOTE_HOST": "false",
            "FLUENT_INSECURE_MODE": "true",
            "FLUENT_CONNECTION_MAX_AGE_SECONDS": "60",
        }

        first = self._connect_with_environment(connect_mock, environment)
        self._publish(14, port=50014, password="second-password")
        second = self._connect_with_environment(
            connect_mock,
            environment,
            minimum_generation=14,
        )

        first_call, second_call = connect_mock.call_args_list
        self.assertEqual(first_call.kwargs["port"], 50013)
        self.assertEqual(first_call.kwargs["password"], "first-password")
        self.assertEqual(second_call.kwargs["port"], 50014)
        self.assertEqual(second_call.kwargs["password"], "second-password")
        self.assertTrue(first_call.kwargs["allow_remote_host"])
        self.assertFalse(first_call.kwargs["cleanup_on_exit"])
        self.assertTrue(first_call.kwargs["start_transcript"])
        self.assertEqual(first._codex_connection_generation, 13)
        self.assertEqual(second._codex_connection_generation, 14)
        self.assertEqual(second._codex_fluent_version, "25.2.0")

    def test_stale_bridge_document_is_rejected_without_leaking_password(self) -> None:
        stale = datetime.now(timezone.utc) - timedelta(minutes=5)
        self._publish(13, updated_at=stale.isoformat())
        connect_mock = mock.Mock(return_value=_Session())
        output = io.StringIO()
        with mock.patch("sys.stdout", output):
            with self.assertRaisesRegex(RuntimeError, "No usable current Fluent connection"):
                self._connect_with_environment(
                    connect_mock,
                    {
                        "FLUENT_BRIDGE_DIR": str(self.bridge_dir),
                        "FLUENT_CONNECTION_MAX_AGE_SECONDS": "30",
                    },
                )
        self.assertNotIn("private-password", output.getvalue())
        self.assertEqual(connect_mock.call_count, 0)

    def test_minimum_generation_is_enforced(self) -> None:
        self._publish(13)
        connect_mock = mock.Mock(return_value=_Session())
        with self.assertRaisesRegex(RuntimeError, "No usable current Fluent connection"):
            self._connect_with_environment(
                connect_mock,
                {"FLUENT_BRIDGE_DIR": str(self.bridge_dir)},
                minimum_generation=14,
            )
        self.assertEqual(connect_mock.call_count, 0)

    def test_legacy_ip_port_password_connection_remains_supported(self) -> None:
        connect_mock = mock.Mock(return_value=_Session())
        session = self._connect_with_environment(
            connect_mock,
            {
                "FLUENT_IP": "10.0.0.8",
                "FLUENT_PORT": "50100",
                "FLUENT_PASSWORD": "legacy-password",
            },
        )
        self.assertIsInstance(session, _Session)
        self.assertEqual(connect_mock.call_args.kwargs["ip"], "10.0.0.8")
        self.assertEqual(connect_mock.call_args.kwargs["port"], 50100)
        self.assertTrue(connect_mock.call_args.kwargs["allow_remote_host"])
        self.assertFalse(connect_mock.call_args.kwargs["cleanup_on_exit"])

    def test_legacy_server_info_connection_remains_supported(self) -> None:
        server_info = self.bridge_dir / "legacy-server-info.txt"
        server_info.write_text("localhost:50101\nprivate\n", encoding="utf-8")
        connect_mock = mock.Mock(return_value=_Session())
        self._connect_with_environment(
            connect_mock,
            {"FLUENT_SERVER_INFO_FILE": str(server_info)},
        )
        self.assertEqual(
            connect_mock.call_args.kwargs["server_info_file_name"],
            str(server_info),
        )
        self.assertFalse(connect_mock.call_args.kwargs["cleanup_on_exit"])

    def test_unhealthy_session_fails_verification(self) -> None:
        self._publish(13)
        connect_mock = mock.Mock(return_value=_Session(health="NOT_SERVING"))
        with self.assertRaisesRegex(RuntimeError, "failed health verification"):
            self._connect_with_environment(
                connect_mock,
                {"FLUENT_BRIDGE_DIR": str(self.bridge_dir)},
            )

    def test_is_serving_health_api_is_supported(self) -> None:
        self._publish(13)
        connect_mock = mock.Mock(return_value=_ServingSession())
        session = self._connect_with_environment(
            connect_mock,
            {"FLUENT_BRIDGE_DIR": str(self.bridge_dir)},
        )
        self.assertEqual(session._codex_connection_generation, 13)


if __name__ == "__main__":
    unittest.main()
