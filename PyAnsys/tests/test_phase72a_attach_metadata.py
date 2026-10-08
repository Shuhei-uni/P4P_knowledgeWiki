"""Bound optional connection metadata without leaking SDK patches."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/setup"))
import run_phase72a_stage4_analytical as runner
from ansys.fluent.core._grpc_services.application_runtime_service_v0 import ApplicationRuntimeService


class AttachMetadataTests(unittest.TestCase):
    def test_optional_metadata_calls_have_deadlines_and_patches_are_restored(self):
        names = ["get_build_info", "get_controller_process_info", "get_solver_process_info"]
        originals = {name: getattr(ApplicationRuntimeService, name) for name in names}
        stub = Mock()
        stub.GetBuildInfo.return_value = SimpleNamespace(build_time="time", build_id="id", vcs_revision="revision", vcs_branch="branch")
        process = SimpleNamespace(process_id=123, hostname="host", working_directory="path")
        stub.GetControllerProcessInfo.return_value = process
        stub.GetSolverProcessInfo.return_value = process
        service = SimpleNamespace(_stub=stub, _metadata=[])

        def attached():
            self.assertEqual(ApplicationRuntimeService.get_build_info(service), ("time", "id", "revision", "branch"))
            for name in names[1:]:
                self.assertEqual(getattr(ApplicationRuntimeService, name)(service), (123, "host", "path"))
            return "verified-session"

        with patch.object(runner, "base_attach", side_effect=attached):
            self.assertEqual(runner.attach(), "verified-session")
        for method in [stub.GetBuildInfo, stub.GetControllerProcessInfo, stub.GetSolverProcessInfo]:
            self.assertEqual(method.call_args.kwargs["timeout"], 5)
        for name, original in originals.items():
            self.assertIs(getattr(ApplicationRuntimeService, name), original)

    def test_failed_connection_also_restores_sdk_methods(self):
        original = ApplicationRuntimeService.get_build_info
        with patch.object(runner, "base_attach", side_effect=RuntimeError("connection failure")):
            with self.assertRaises(RuntimeError):
                runner.attach()
        self.assertIs(ApplicationRuntimeService.get_build_info, original)


if __name__ == "__main__":
    unittest.main()
