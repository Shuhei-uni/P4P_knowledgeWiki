from __future__ import annotations

import contextlib
import importlib.util
import io
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/inspection/probe_remote_paths.py"
SPEC = importlib.util.spec_from_file_location("probe_remote_paths", SCRIPT)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class RemotePathProbeTests(unittest.TestCase):
    def setUp(self):
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.dict(os.environ, {}, clear=True))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.load_env = stack.enter_context(patch.object(probe, "load_dotenv"))
        self.connect = stack.enter_context(patch.object(probe, "connect"))
        self.exists = stack.enter_context(patch.object(probe, "remote_file_exists", return_value=True))

    def test_explicit_paths_use_selected_server_and_override_old_environment_paths(self):
        os.environ["FLUENT_REMOTE_MESH_FILE"] = "C:/old-study/mesh.msh.h5"
        path = "D:/P4P/phase-7b/inputs/mesh.msh.h5"
        self.assertEqual(probe.main(["--server-id", "2", "--path", path]), 0)
        self.connect.assert_called_once_with(server_id="2", start_transcript=False, tcp_timeout_seconds=5)
        self.exists.assert_called_once_with(self.connect.return_value, path)
        self.load_env.assert_called_once_with(probe.PROJECT_ROOT / ".env")

    def test_missing_input_fails_but_remaining_paths_are_still_checked(self):
        self.exists.side_effect = [False, True]
        self.assertEqual(probe.main(["--path", "D:/missing.msh.h5", "--path", "D:/runs"]), 1)
        self.assertEqual(self.exists.call_count, 2)

    def test_api_error_is_not_success(self):
        self.exists.side_effect = RuntimeError("file service unavailable")
        self.assertEqual(probe.main(["--path", "D:/mesh.msh.h5"]), 1)

    def test_relative_path_rejected_before_connecting(self):
        self.assertEqual(probe.main(["--path", "inputs/mesh.msh.h5"]), 2)
        self.connect.assert_not_called()

    def test_empty_configuration_does_not_connect(self):
        self.assertEqual(probe.main([]), 2)
        self.connect.assert_not_called()

    def test_environment_paths_do_not_invent_server_info_file(self):
        os.environ["FLUENT_REMOTE_PROJECT_DIR"] = "D:/P4P/phase-7b"
        self.assertEqual(probe.main([]), 0)
        self.exists.assert_called_once_with(self.connect.return_value, "D:/P4P/phase-7b")

    def test_connection_failure_is_reported_as_failure(self):
        self.connect.side_effect = TimeoutError("endpoint unavailable")
        self.assertEqual(probe.main(["--path", "D:/mesh.msh.h5"]), 2)
        self.exists.assert_not_called()


if __name__ == "__main__":
    unittest.main()
