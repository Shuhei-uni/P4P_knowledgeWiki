from __future__ import annotations

import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.fluent_watchdog import (  # noqa: E402
    FluentWatchdog,
    ManagedFluentProcess,
    WatchdogConfig,
)
from pyansys_fluent.laptop_workflow import LaptopWorkflow  # noqa: E402
from pyansys_fluent.run_worker import (  # noqa: E402
    FluentRunWorker,
    RunRequest,
)


class _Process:
    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.returncode: int | None = None
        self.stdin = None

    def poll(self) -> int | None:
        return self.returncode


class _Handle:
    def close(self) -> None:
        pass


class _ProcessManager:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.launched: list[ManagedFluentProcess] = []
        self.stopped: list[int] = []

    def launch(self, generation: int) -> ManagedFluentProcess:
        self.root.mkdir(parents=True, exist_ok=True)
        managed = ManagedFluentProcess(
            process=_Process(2000 + generation),
            generation=generation,
            launched_unix_seconds=time.time(),
            server_info_path=self.root / f"server-info-{generation}.txt",
            stdout_path=self.root / f"stdout-{generation}.log",
            stderr_path=self.root / f"stderr-{generation}.log",
            stdout_handle=_Handle(),
            stderr_handle=_Handle(),
        )
        self.launched.append(managed)
        return managed

    def wait_for_server_info(
        self, managed: ManagedFluentProcess
    ) -> Path:
        managed.server_info_path.write_text(
            f"127.0.0.1:{52000 + managed.generation}\n"
            f"watchdog-secret-{managed.generation}\n",
            encoding="utf-8",
        )
        return managed.server_info_path

    def stop(self, managed: ManagedFluentProcess | None) -> None:
        if managed is None:
            return
        self.stopped.append(managed.generation)
        managed.process.returncode = 0
        managed.server_info_path.unlink(missing_ok=True)


class _MonitorSession:
    def is_active(self) -> bool:
        return True

    def get_fluent_version(self) -> str:
        return "25.2-integration-test"

    def exit(self, **_kwargs) -> None:
        pass


def _wait_for_running_generation(
    connection_path: Path,
    generation: int,
    *,
    timeout: float = 2.0,
) -> dict:
    deadline = time.monotonic() + timeout
    last_document: dict = {}
    while time.monotonic() < deadline:
        try:
            last_document = json.loads(
                connection_path.read_text(encoding="utf-8")
            )
        except (FileNotFoundError, json.JSONDecodeError):
            time.sleep(0.002)
            continue
        if (
            last_document.get("status") == "running"
            and last_document.get("generation") == generation
        ):
            return last_document
        time.sleep(0.002)
    raise AssertionError(
        f"generation {generation} did not become running; "
        f"last document={last_document}"
    )


class _RunOperations:
    def __init__(
        self,
        *,
        process_manager: _ProcessManager,
        connection_path: Path,
        kill_generation_one: bool,
    ) -> None:
        self.process_manager = process_manager
        self.connection_path = connection_path
        self.kill_generation_one = kill_generation_one
        self.killed = False
        self.iteration = 0
        self.calls: list[tuple] = []

    def connect(self, connection):
        self.calls.append(("connect", connection["generation"]))
        return self

    def is_active(self, _session) -> bool:
        return True

    def read_case(self, _session, path: Path) -> None:
        self.calls.append(("read_case", str(path)))

    def read_data(self, _session, path: Path) -> None:
        self.calls.append(("read_data", str(path)))

    def execute_tui(self, _session, command: str) -> str:
        self.calls.append(("execute_tui", command))
        return f"executed: {command}"

    def iterate(self, _session, iterations: int) -> None:
        self.iteration += iterations
        self.calls.append(("iterate", iterations))
        if (
            self.kill_generation_one
            and not self.killed
            and self.iteration > 250
        ):
            self.killed = True
            self.process_manager.launched[0].process.returncode = 99
            _wait_for_running_generation(self.connection_path, 2)

    def write_case(self, _session, path: Path) -> None:
        path.write_bytes(f"case-{self.iteration}".encode())
        self.calls.append(("write_case", str(path)))

    def write_data(self, _session, path: Path) -> None:
        path.write_bytes(f"data-{self.iteration}".encode())
        self.calls.append(("write_data", str(path)))

    def detach(self, _session) -> None:
        self.calls.append(("detach",))


def _request(
    *,
    job_id: str,
    generation: int,
    mode: str,
    source_case: Path,
    source_data: Path | None,
    completed_iterations: int,
    output_directory: Path,
) -> RunRequest:
    return RunRequest.from_dict(
        {
            "schema_version": 2,
            "job_id": job_id,
            "expected_generation": generation,
            "mode": mode,
            "source_case": str(source_case),
            "source_data": (
                str(source_data) if source_data is not None else None
            ),
            "initialization_tui": (
                ["/solve/initialize/hyb-initialization"]
                if mode == "initialize"
                else None
            ),
            "target_total_iterations": 500,
            "completed_iterations": completed_iterations,
            "checkpoint_interval": 250,
            "report_interval": 100,
            "output_directory": str(output_directory),
            "overwrite": False,
        }
    )


class WatchdogRunWorkerIntegrationTests(unittest.TestCase):
    def test_crash_requires_explicit_new_generation_resume_request(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bridge = root / "bridge"
            runtime = root / "runtime"
            source_case = root / "parent.cas.h5"
            source_case.write_bytes(b"parent-case-must-not-change")
            setup_plan = root / "setup.md"
            setup_plan.write_text(
                "# Integration setup\n\nAgent-controlled intent.\n",
                encoding="utf-8",
            )
            laptop = LaptopWorkflow(root / "laptop-workflow")
            laptop.create(
                job_id="integration-build",
                setup_plan_path=setup_plan,
                connection_generation=1,
                analysis_tasks=("result_check",),
            )
            laptop.start_step("verify_parent_case")
            laptop.complete_step("verify_parent_case")
            laptop.accept_case_checkpoint(str(source_case))
            laptop.mark_case_ready()
            connection_path = bridge / "latest_connection.json"

            config = WatchdogConfig(
                fluent_exe=root / "fluent.exe",
                bridge_dir=bridge,
                advertised_host="10.0.0.5",
                runtime_dir=runtime,
                health_timeout_seconds=0.1,
                health_interval_seconds=0.01,
                heartbeat_interval_seconds=0.005,
                poll_interval_seconds=0.001,
                restart_delay_seconds=0,
                max_restarts=2,
            )
            process_manager = _ProcessManager(runtime)
            watchdog = FluentWatchdog(
                config,
                process_manager=process_manager,
                connect_factory=lambda _path, _config: _MonitorSession(),
            )
            watchdog_errors: list[BaseException] = []

            def run_watchdog() -> None:
                try:
                    watchdog.run()
                except BaseException as exc:
                    watchdog_errors.append(exc)

            watchdog_thread = threading.Thread(
                target=run_watchdog,
                name="test-fluent-watchdog",
                daemon=True,
            )
            watchdog_thread.start()
            try:
                generation_one = _wait_for_running_generation(
                    connection_path, 1
                )
                self.assertEqual(
                    generation_one["password"], "watchdog-secret-1"
                )

                initial_operations = _RunOperations(
                    process_manager=process_manager,
                    connection_path=connection_path,
                    kill_generation_one=True,
                )
                initial_request = _request(
                    job_id="workflow-initial",
                    generation=1,
                    mode="initialize",
                    source_case=source_case,
                    source_data=None,
                    completed_iterations=0,
                    output_directory=root / "initial-output",
                )
                laptop.submit(initial_request, bridge_dir=bridge)
                initial_receipt_path = FluentRunWorker(
                    bridge,
                    operations=initial_operations,
                    pair_verifier=lambda case, data: (
                        case.stat().st_size,
                        data.stat().st_size,
                    ),
                ).process_next()
                self.assertIsNotNone(initial_receipt_path)
                initial_receipt = json.loads(
                    initial_receipt_path.read_text(encoding="utf-8")
                )

                self.assertEqual(initial_receipt["status"], "interrupted")
                self.assertEqual(initial_receipt["generation"], 1)
                self.assertEqual(initial_receipt["completed_iterations"], 350)
                checkpoint = initial_receipt["last_checkpoint"]
                self.assertEqual(checkpoint["iteration"], 250)
                self.assertTrue(checkpoint["file_verified"])
                checkpoint_case = Path(checkpoint["case_path"])
                checkpoint_data = Path(checkpoint["data_path"])
                self.assertTrue(checkpoint_case.is_file())
                self.assertTrue(checkpoint_data.is_file())
                self.assertEqual(
                    [],
                    list((bridge / "run_requests" / "incoming").glob("*.json")),
                )
                self.assertTrue(
                    (
                        bridge
                        / "run_requests"
                        / "failed"
                        / "workflow-initial.json"
                    ).is_file()
                )
                laptop_state = laptop.ingest_receipt(initial_receipt_path)
                self.assertEqual(
                    "recovery_required", laptop_state["status"]
                )
                self.assertEqual(
                    str(source_case),
                    laptop.ledger.read()["latest_case_checkpoint"],
                )

                generation_two = _wait_for_running_generation(
                    connection_path, 2
                )
                self.assertEqual(
                    generation_two["password"], "watchdog-secret-2"
                )
                self.assertNotEqual(
                    generation_one["port"], generation_two["port"]
                )
                laptop_state = laptop.verify_pending_checkpoint(
                    case_path=str(checkpoint_case),
                    data_path=str(checkpoint_data),
                    generation=2,
                )
                self.assertEqual(
                    "recovery_verified", laptop_state["status"]
                )

                resume_operations = _RunOperations(
                    process_manager=process_manager,
                    connection_path=connection_path,
                    kill_generation_one=False,
                )
                resume_request = _request(
                    job_id="workflow-resume",
                    generation=2,
                    mode="resume",
                    source_case=checkpoint_case,
                    source_data=checkpoint_data,
                    completed_iterations=250,
                    output_directory=root / "resume-output",
                )
                laptop.submit(resume_request, bridge_dir=bridge)
                resume_receipt_path = FluentRunWorker(
                    bridge,
                    operations=resume_operations,
                    pair_verifier=lambda case, data: (
                        case.stat().st_size,
                        data.stat().st_size,
                    ),
                ).process_next()
                self.assertIsNotNone(resume_receipt_path)
                resume_receipt = json.loads(
                    resume_receipt_path.read_text(encoding="utf-8")
                )

                self.assertEqual(resume_receipt["status"], "completed")
                self.assertEqual(resume_receipt["generation"], 2)
                self.assertEqual(resume_receipt["completed_iterations"], 500)
                self.assertEqual(resume_operations.iteration, 250)
                self.assertNotIn(("initialize",), resume_operations.calls)
                self.assertTrue(
                    any(
                        call[0] == "read_data"
                        for call in resume_operations.calls
                    )
                )
                self.assertEqual(
                    source_case.read_bytes(),
                    b"parent-case-must-not-change",
                )
                self.assertEqual(
                    [managed.generation for managed in process_manager.launched],
                    [1, 2],
                )
                laptop_state = laptop.ingest_receipt(resume_receipt_path)
                self.assertEqual(
                    "run_completed_pending_verification",
                    laptop_state["status"],
                )
                final_checkpoint = resume_receipt["last_checkpoint"]
                laptop_state = laptop.verify_pending_checkpoint(
                    case_path=final_checkpoint["case_path"],
                    data_path=final_checkpoint["data_path"],
                    generation=2,
                )
                self.assertEqual("analysis_ready", laptop_state["status"])
                analysis_artifact = root / "result-check.json"
                analysis_artifact.write_text(
                    '{"check": "complete"}\n', encoding="utf-8"
                )
                laptop.start_analysis_task("result_check")
                laptop.complete_analysis_task(
                    "result_check",
                    artifacts=(analysis_artifact,),
                )
                result_manifest, result_summary = laptop.finalize()
                self.assertTrue(result_manifest.is_file())
                self.assertTrue(result_summary.is_file())
                manifest = json.loads(
                    result_manifest.read_text(encoding="utf-8")
                )
                self.assertEqual(
                    final_checkpoint["data_path"],
                    manifest["final_checkpoint"]["data_path"],
                )
                self.assertEqual("complete", laptop.read()["status"])
            finally:
                watchdog.request_stop()
                watchdog_thread.join(timeout=2)

            self.assertFalse(watchdog_thread.is_alive())
            self.assertEqual(watchdog_errors, [])


if __name__ == "__main__":
    unittest.main()
