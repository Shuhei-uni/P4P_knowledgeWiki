#!/usr/bin/env python3
"""Windows-host Fluent process ownership, health monitoring, and restart support.

This module intentionally does not load or mutate Fluent cases.  Its first job
is to prove that a long-lived process on the Fluent computer can:

1. launch Fluent with a fresh server-info file;
2. connect through PyFluent without taking cleanup ownership;
3. monitor both the OS process and the gRPC session;
4. relaunch Fluent after a process or connection failure; and
5. publish an atomic heartbeat/status document.

The host worker owns the Fluent process.  Short-lived setup, run, and analysis
clients should eventually submit work to it rather than launching Fluent
themselves.
"""

from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import time
import uuid
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO


STATUS_SCHEMA_VERSION = 1


class RestartLimitExceeded(RuntimeError):
    """Raised when too many Fluent restarts occur inside the configured window."""


class HostWorkerAlreadyRunning(RuntimeError):
    """Raised when another worker owns the host lock."""


class FluentGenerationRetryRequested(RuntimeError):
    """Raised after durable run state requests a fresh Fluent generation."""


@dataclass(frozen=True)
class HostWorkerConfig:
    """Validated launch and monitoring configuration for one Fluent host."""

    fluent_exe: Path
    work_dir: Path
    dimension: int = 3
    precision: str = "double"
    processor_count: int = 2
    gui: bool = False
    startup_timeout_seconds: float = 180.0
    connect_timeout_seconds: float = 60.0
    health_timeout_seconds: float = 10.0
    health_interval_seconds: float = 10.0
    heartbeat_interval_seconds: float = 5.0
    job_poll_interval_seconds: float = 1.0
    poll_interval_seconds: float = 0.5
    restart_delay_seconds: float = 5.0
    max_restarts: int = 3
    restart_window_seconds: float = 600.0
    extra_fluent_args: tuple[str, ...] = ()

    def validate(self, *, require_executable: bool = True) -> None:
        if self.dimension not in (2, 3):
            raise ValueError("dimension must be 2 or 3")
        if self.precision not in ("single", "double"):
            raise ValueError("precision must be 'single' or 'double'")
        if self.processor_count <= 0:
            raise ValueError("processor_count must be positive")
        if self.startup_timeout_seconds <= 0:
            raise ValueError("startup_timeout_seconds must be positive")
        if self.connect_timeout_seconds <= 0:
            raise ValueError("connect_timeout_seconds must be positive")
        if self.health_timeout_seconds <= 0:
            raise ValueError("health_timeout_seconds must be positive")
        if self.health_interval_seconds <= 0:
            raise ValueError("health_interval_seconds must be positive")
        if self.heartbeat_interval_seconds <= 0:
            raise ValueError("heartbeat_interval_seconds must be positive")
        if self.job_poll_interval_seconds <= 0:
            raise ValueError("job_poll_interval_seconds must be positive")
        if self.poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be positive")
        if self.restart_delay_seconds < 0:
            raise ValueError("restart_delay_seconds must be non-negative")
        if self.max_restarts < 0:
            raise ValueError("max_restarts must be non-negative")
        if self.restart_window_seconds <= 0:
            raise ValueError("restart_window_seconds must be positive")
        if require_executable and not self.fluent_exe.is_file():
            raise FileNotFoundError(f"Fluent executable does not exist: {self.fluent_exe}")

    @property
    def fluent_mode_argument(self) -> str:
        suffix = "ddp" if self.precision == "double" else "d"
        return f"{self.dimension}{suffix}"

    def server_info_path_for_generation(self, generation: int) -> Path:
        if generation <= 0:
            raise ValueError("generation must be positive")
        return self.work_dir / f"fluent-server-info-{generation:03d}.txt"

    @property
    def status_path(self) -> Path:
        return self.work_dir / "host-worker-status.json"


@dataclass
class ManagedFluentProcess:
    """One Fluent process generation and the resources opened for it."""

    process: subprocess.Popen[str]
    generation: int
    launched_unix_seconds: float
    server_info_path: Path
    stdout_path: Path
    stderr_path: Path
    stdout_handle: TextIO
    stderr_handle: TextIO
    process_tree_token: Any | None = None

    @property
    def pid(self) -> int:
        return int(self.process.pid)

    @property
    def is_alive(self) -> bool:
        return self.process.poll() is None


class AtomicJsonStatusStore:
    """Write worker state atomically on the Fluent host filesystem."""

    def __init__(self, path: Path):
        self.path = path

    def write(self, payload: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(
            f".{self.path.name}.tmp-{os.getpid()}-{threading.get_ident()}"
        )
        document = dict(payload)
        document.setdefault("schema_version", STATUS_SCHEMA_VERSION)
        try:
            with temporary.open("w", encoding="utf-8", newline="\n") as stream:
                json.dump(document, stream, indent=2, default=str)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()


class ExclusiveHostLock:
    """Cross-platform non-blocking file lock for one host-worker instance."""

    def __init__(self, path: Path):
        self.path = path
        self._stream: Any | None = None

    def acquire(self) -> None:
        if self._stream is not None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        stream = self.path.open("a+b")
        try:
            if os.name == "nt":
                import msvcrt

                stream.seek(0, os.SEEK_END)
                if stream.tell() == 0:
                    stream.write(b"\0")
                    stream.flush()
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            stream.close()
            raise HostWorkerAlreadyRunning(
                f"Another Fluent host worker owns lock: {self.path}"
            ) from exc

        self._stream = stream
        stream.seek(0)
        stream.truncate()
        stream.write(f"{os.getpid()}\n".encode("ascii"))
        stream.flush()
        os.fsync(stream.fileno())

    def release(self) -> None:
        stream = self._stream
        if stream is None:
            return
        try:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        finally:
            stream.close()
            self._stream = None

    def __enter__(self) -> "ExclusiveHostLock":
        self.acquire()
        return self

    def __exit__(self, _exc_type, _exc, _traceback) -> None:
        self.release()


def call_with_timeout(
    callback: Callable[[], Any],
    timeout_seconds: float,
    *,
    label: str,
    late_result_cleanup: Callable[[Any], None] | None = None,
) -> Any:
    """Run a possibly blocking PyFluent call in a daemon thread."""

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    result_queue: queue.Queue[tuple[bool, Any]] = queue.Queue(maxsize=1)
    timed_out = threading.Event()

    def invoke() -> None:
        try:
            value = callback()
            if timed_out.is_set():
                if late_result_cleanup is not None:
                    late_result_cleanup(value)
                return
            result_queue.put((True, value))
        except Exception as exc:
            if timed_out.is_set():
                return
            result_queue.put((False, exc))

    thread = threading.Thread(
        target=invoke,
        name=f"fluent-host-worker-{label}",
        daemon=True,
    )
    thread.start()
    try:
        succeeded, value = result_queue.get(timeout=timeout_seconds)
    except queue.Empty as exc:
        timed_out.set()
        try:
            succeeded, value = result_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            if succeeded and late_result_cleanup is not None:
                late_result_cleanup(value)
        raise TimeoutError(
            f"{label} did not complete within {timeout_seconds:.1f} seconds"
        ) from exc
    if succeeded:
        return value
    raise value


def close_session_best_effort(
    session: Any | None,
    *,
    timeout_seconds: float,
) -> bool:
    """Detach one cleanup-disabled client without trusting an unbounded exit."""

    if session is None:
        return True
    exit_session = getattr(session, "exit", None)
    if not callable(exit_session):
        return False
    try:
        call_with_timeout(
            lambda: exit_session(
                timeout=timeout_seconds,
                timeout_force=False,
                wait=False,
            ),
            timeout_seconds,
            label="session-detach",
        )
        return True
    except Exception:
        return False


def _health_value_is_serving(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    normalized = str(value).strip().lower()
    return normalized in {
        "1",
        "active",
        "healthy",
        "ok",
        "serving",
        "status.serving",
        "true",
    }


def validate_server_info_text(content: str) -> tuple[str, int]:
    """Validate Fluent server-info without returning or logging its password."""

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(lines) < 2:
        raise ValueError("Server-info must contain host:port and password lines")

    host_port = lines[0]
    password = lines[1]
    if ":" not in host_port:
        raise ValueError("Server-info host line does not contain a port")
    host, port_text = host_port.rsplit(":", 1)
    host = host.strip()
    if not host:
        raise ValueError("Server-info host is empty")
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ValueError("Server-info port is not an integer") from exc
    if not 1 <= port <= 65535:
        raise ValueError("Server-info port is outside 1..65535")
    if not password:
        raise ValueError("Server-info password is empty")
    return host, port


def session_is_active(session: Any) -> bool:
    """Check a PyFluent session across current and older API shapes."""

    active = getattr(session, "is_active", None)
    if callable(active):
        return _health_value_is_serving(active())

    health = getattr(session, "health_check", None)
    if health is None:
        raise AttributeError("Session exposes neither is_active() nor health_check")

    is_serving = getattr(health, "is_serving", None)
    if is_serving is not None:
        value = is_serving() if callable(is_serving) else is_serving
        return _health_value_is_serving(value)

    check_health = getattr(health, "check_health", None)
    if callable(check_health):
        return _health_value_is_serving(check_health())

    status = getattr(health, "status", None)
    if callable(status):
        return _health_value_is_serving(status())

    raise AttributeError("Session health API is unavailable")


def connect_from_server_info(server_info_path: Path, config: HostWorkerConfig) -> Any:
    """Connect to a worker-owned Fluent process without cleanup ownership."""

    import ansys.fluent.core as pyfluent

    try:
        pyfluent.config.check_health_timeout = max(
            1,
            int(config.health_timeout_seconds),
        )
    except Exception:
        # The outer daemon-thread timeout still bounds the worker's wait on
        # older PyFluent builds without the public configuration field.
        pass

    return pyfluent.connect_to_fluent(
        server_info_file_name=str(server_info_path),
        allow_remote_host=False,
        cleanup_on_exit=False,
        start_transcript=True,
        start_watchdog=False,
    )


class RestartBudget:
    """Track restart attempts inside a rolling time window."""

    def __init__(self, max_restarts: int, window_seconds: float):
        if max_restarts < 0:
            raise ValueError("max_restarts must be non-negative")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.max_restarts = max_restarts
        self.window_seconds = window_seconds
        self._timestamps: deque[float] = deque()

    def record(self, timestamp: float) -> int:
        threshold = timestamp - self.window_seconds
        while self._timestamps and self._timestamps[0] < threshold:
            self._timestamps.popleft()
        self._timestamps.append(timestamp)
        count = len(self._timestamps)
        if count > self.max_restarts:
            raise RestartLimitExceeded(
                f"Restart budget exceeded: {count} attempts inside "
                f"{self.window_seconds:.1f} seconds (limit {self.max_restarts})"
            )
        return count


class _WindowsJobObject:
    """Kill-on-close Windows Job Object for one worker-owned Fluent tree."""

    def __init__(self, handle: Any, close_handle: Callable[[Any], Any]):
        self._handle = handle
        self._close_handle = close_handle
        self._closed = False

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._handle:
            self._close_handle(self._handle)
            self._handle = None


def _assign_windows_kill_on_close_job(process: subprocess.Popen[str]) -> _WindowsJobObject:
    """Assign a newly launched process to a kill-on-close Windows Job Object."""

    if os.name != "nt":
        raise RuntimeError("Windows Job Objects are only available on Windows")

    import ctypes
    from ctypes import wintypes

    class JobObjectBasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class JobObjectExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JobObjectBasicLimitInformation),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    job_handle = kernel32.CreateJobObjectW(None, None)
    if not job_handle:
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        information = JobObjectExtendedLimitInformation()
        information.BasicLimitInformation.LimitFlags = 0x00002000
        if not kernel32.SetInformationJobObject(
            job_handle,
            9,
            ctypes.byref(information),
            ctypes.sizeof(information),
        ):
            raise ctypes.WinError(ctypes.get_last_error())

        process_handle = wintypes.HANDLE(int(getattr(process, "_handle")))
        if not kernel32.AssignProcessToJobObject(job_handle, process_handle):
            raise ctypes.WinError(ctypes.get_last_error())
    except Exception:
        kernel32.CloseHandle(job_handle)
        raise

    return _WindowsJobObject(job_handle, kernel32.CloseHandle)


class FluentProcessManager:
    """Launch and terminate Fluent processes owned by the current worker."""

    def __init__(
        self,
        config: HostWorkerConfig,
        *,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
        wall_time: Callable[[], float] = time.time,
    ):
        self.config = config
        self._sleep = sleep
        self._monotonic = monotonic
        self._wall_time = wall_time

    def launch(self, generation: int) -> ManagedFluentProcess:
        self.config.validate(require_executable=True)
        self.config.work_dir.mkdir(parents=True, exist_ok=True)

        server_info = self.config.server_info_path_for_generation(generation)
        if server_info.exists():
            server_info.unlink()

        stdout_path = self.config.work_dir / f"fluent-generation-{generation:03d}-stdout.log"
        stderr_path = self.config.work_dir / f"fluent-generation-{generation:03d}-stderr.log"
        stdout_handle = stdout_path.open("w", encoding="utf-8", errors="replace")
        stderr_handle = stderr_path.open("w", encoding="utf-8", errors="replace")

        command = [
            str(self.config.fluent_exe),
            self.config.fluent_mode_argument,
            f"-t{self.config.processor_count}",
        ]
        if not self.config.gui:
            command.append("-g")
        command.extend(self.config.extra_fluent_args)
        command.append(f"-sifile={server_info}")

        creationflags = 0
        if os.name == "nt":
            creationflags = int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=stdout_handle,
                stderr=stderr_handle,
                cwd=str(self.config.work_dir),
                text=True,
                bufsize=1,
                creationflags=creationflags,
            )
        except Exception:
            stdout_handle.close()
            stderr_handle.close()
            raise

        process_tree_token: Any | None = None
        if os.name == "nt":
            try:
                process_tree_token = _assign_windows_kill_on_close_job(process)
            except Exception:
                try:
                    process.terminate()
                    process.wait(timeout=20)
                finally:
                    stdout_handle.close()
                    stderr_handle.close()
                raise

        return ManagedFluentProcess(
            process=process,
            generation=generation,
            launched_unix_seconds=self._wall_time(),
            server_info_path=server_info,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            stdout_handle=stdout_handle,
            stderr_handle=stderr_handle,
            process_tree_token=process_tree_token,
        )

    def wait_for_server_info(self, managed: ManagedFluentProcess) -> Path:
        deadline = self._monotonic() + self.config.startup_timeout_seconds
        previous_content = ""
        stable_reads = 0

        while self._monotonic() < deadline:
            return_code = managed.process.poll()
            if return_code is not None:
                raise RuntimeError(
                    f"Fluent generation {managed.generation} exited before server-info "
                    f"was ready (return code {return_code})"
                )

            try:
                stat = managed.server_info_path.stat()
                content = managed.server_info_path.read_text(
                    encoding="utf-8",
                    errors="replace",
                ).strip()
            except OSError:
                content = ""
                stat = None

            if (
                stat is not None
                and stat.st_mtime + 2.0 < managed.launched_unix_seconds
            ):
                content = ""

            if content:
                try:
                    validate_server_info_text(content)
                except ValueError:
                    stable_reads = 0
                    previous_content = ""
                else:
                    if content == previous_content:
                        stable_reads += 1
                    else:
                        previous_content = content
                        stable_reads = 1
                    if stable_reads >= 2:
                        return managed.server_info_path

            self._sleep(self.config.poll_interval_seconds)

        raise TimeoutError(
            f"Timed out after {self.config.startup_timeout_seconds:.1f} seconds "
            f"waiting for server-info: {managed.server_info_path}"
        )

    def stop(self, managed: ManagedFluentProcess | None) -> None:
        if managed is None:
            return
        process = managed.process
        try:
            if managed.process_tree_token is not None:
                managed.process_tree_token.close()
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=30)
            elif os.name == "nt":
                subprocess.run(
                    [
                        "taskkill",
                        "/PID",
                        str(process.pid),
                        "/T",
                        "/F",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if process.poll() is None:
                    process.wait(timeout=30)
            elif process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=30)
        finally:
            try:
                if process.stdin is not None:
                    process.stdin.close()
            except Exception:
                pass
            managed.stdout_handle.close()
            managed.stderr_handle.close()
            try:
                managed.server_info_path.unlink(missing_ok=True)
            except OSError:
                pass


class FluentHostWorker:
    """Own, monitor, and relaunch one Fluent process on its Windows host."""

    def __init__(
        self,
        config: HostWorkerConfig,
        *,
        process_manager: FluentProcessManager | None = None,
        connect_factory: Callable[[Path, HostWorkerConfig], Any] = connect_from_server_info,
        status_store: AtomicJsonStatusStore | None = None,
        job_processor: Any | None = None,
        stop_event: threading.Event | None = None,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
        wall_time: Callable[[], float] = time.time,
    ):
        config.validate(require_executable=process_manager is None)
        self.config = config
        self.process_manager = process_manager or FluentProcessManager(
            config,
            sleep=sleep,
            monotonic=monotonic,
        )
        self.connect_factory = connect_factory
        self.status_store = status_store or AtomicJsonStatusStore(config.status_path)
        if job_processor is None:
            # Local import avoids making the protocol module part of Fluent's
            # low-level process-launch dependency graph.
            from .job_protocol import FilesystemJobSpool, JobStageProcessor

            job_processor = JobStageProcessor(FilesystemJobSpool(config.work_dir))
        self.job_processor = job_processor
        self.stop_event = stop_event or threading.Event()
        self._sleep = sleep
        self._monotonic = monotonic
        self._wall_time = wall_time
        self._worker_started = self._monotonic()
        self._boot_id = uuid.uuid4().hex
        self._heartbeat_sequence = 0
        self._last_health_success_unix_seconds: float | None = None
        self._generation = 0
        self._restart_count = 0
        self._last_error = ""
        self._fluent_version = ""

    def request_stop(self) -> None:
        self.stop_event.set()

    def _write_status(
        self,
        state: str,
        *,
        managed: ManagedFluentProcess | None = None,
        message: str = "",
        recent_restart_count: int = 0,
    ) -> None:
        self._heartbeat_sequence += 1
        self.status_store.write(
            {
                "schema_version": STATUS_SCHEMA_VERSION,
                "state": state,
                "message": message,
                "updated_unix_seconds": self._wall_time(),
                "heartbeat_sequence": self._heartbeat_sequence,
                "heartbeat_ttl_seconds": max(
                    self.config.heartbeat_interval_seconds * 3.0,
                    self.config.health_interval_seconds
                    + self.config.health_timeout_seconds,
                ),
                "worker_boot_id": self._boot_id,
                "worker_pid": os.getpid(),
                "worker_uptime_seconds": max(
                    0.0,
                    self._monotonic() - self._worker_started,
                ),
                "generation": self._generation,
                "fluent_pid": managed.pid if managed is not None else None,
                "fluent_process_alive": managed.is_alive if managed is not None else False,
                "fluent_version": self._fluent_version or None,
                "last_health_success_unix_seconds": (
                    self._last_health_success_unix_seconds
                ),
                "restart_count_total": self._restart_count,
                "restart_count_in_window": recent_restart_count,
                "last_error": self._last_error or None,
                "server_info_path": (
                    str(managed.server_info_path) if managed is not None else None
                ),
                "stdout_path": str(managed.stdout_path) if managed is not None else None,
                "stderr_path": str(managed.stderr_path) if managed is not None else None,
            }
        )

    def _connect(self, server_info_path: Path) -> Any:
        session = call_with_timeout(
            lambda: self.connect_factory(server_info_path, self.config),
            self.config.connect_timeout_seconds,
            label="connect",
            late_result_cleanup=lambda late_session: close_session_best_effort(
                late_session,
                timeout_seconds=self.config.health_timeout_seconds,
            ),
        )
        try:
            active = call_with_timeout(
                lambda: session_is_active(session),
                self.config.health_timeout_seconds,
                label="initial-health",
            )
            if not active:
                raise RuntimeError("PyFluent connected but the session is not active")
            self._last_health_success_unix_seconds = self._wall_time()

            get_version = getattr(session, "get_fluent_version", None)
            if callable(get_version):
                try:
                    self._fluent_version = str(
                        call_with_timeout(
                            get_version,
                            self.config.health_timeout_seconds,
                            label="fluent-version",
                        )
                    )
                except Exception:
                    self._fluent_version = "<unavailable>"
        except Exception:
            close_session_best_effort(
                session,
                timeout_seconds=self.config.health_timeout_seconds,
            )
            raise
        return session

    def _monitor(
        self,
        managed: ManagedFluentProcess,
        session: Any,
        *,
        deadline: float | None,
        recent_restart_count: int,
    ) -> None:
        next_health = self._monotonic()
        next_heartbeat = self._monotonic()
        next_job_poll = self._monotonic()

        while not self.stop_event.is_set():
            now = self._monotonic()
            if deadline is not None and now >= deadline:
                self.request_stop()
                break

            return_code = managed.process.poll()
            if return_code is not None:
                raise RuntimeError(
                    f"Fluent generation {managed.generation} exited with "
                    f"return code {return_code}"
                )

            if now >= next_health:
                active = call_with_timeout(
                    lambda: session_is_active(session),
                    self.config.health_timeout_seconds,
                    label="health",
                )
                if not active:
                    raise RuntimeError("Fluent gRPC session is no longer active")
                self._last_health_success_unix_seconds = self._wall_time()
                next_health = now + self.config.health_interval_seconds

            if now >= next_heartbeat:
                self._write_status(
                    "running",
                    managed=managed,
                    message="Fluent process and gRPC session are active",
                    recent_restart_count=recent_restart_count,
                )
                next_heartbeat = now + self.config.heartbeat_interval_seconds

            if now >= next_job_poll:
                try:
                    from .job_protocol import HealthStageContext

                    self.job_processor.process_next(
                        HealthStageContext(
                            worker_boot_id=self._boot_id,
                            fluent_generation=managed.generation,
                            fluent_pid=managed.pid,
                            server_info_path=managed.server_info_path,
                            config=self.config,
                            process_is_alive=lambda: managed.is_alive,
                        )
                    )
                except FluentGenerationRetryRequested:
                    # The run stage has already committed its retryable attempt
                    # state. Propagate to the outer lifecycle so this
                    # generation is stopped and the same running job can resume
                    # against the next server-info file.
                    raise
                except Exception as exc:
                    # A spool/receipt failure must be visible, but it must not
                    # restart an otherwise healthy Fluent generation.
                    self._last_error = (
                        f"Job protocol {type(exc).__name__}: {exc}"
                    )
                next_job_poll = now + self.config.job_poll_interval_seconds

            self._sleep(self.config.poll_interval_seconds)

    def run(self, *, max_runtime_seconds: float = 0.0) -> None:
        """Run until stopped, relaunching Fluent within the restart budget."""

        if max_runtime_seconds < 0:
            raise ValueError("max_runtime_seconds must be non-negative")

        deadline = (
            self._monotonic() + max_runtime_seconds
            if max_runtime_seconds > 0
            else None
        )
        budget = RestartBudget(
            self.config.max_restarts,
            self.config.restart_window_seconds,
        )
        managed: ManagedFluentProcess | None = None
        session: Any | None = None
        recent_restart_count = 0
        failed = False

        try:
            while not self.stop_event.is_set():
                if deadline is not None and self._monotonic() >= deadline:
                    self.request_stop()
                    break
                self._generation += 1
                self._fluent_version = ""
                try:
                    self._write_status(
                        "starting",
                        message=f"Launching Fluent generation {self._generation}",
                        recent_restart_count=recent_restart_count,
                    )
                    managed = self.process_manager.launch(self._generation)
                    self._write_status(
                        "waiting-for-server-info",
                        managed=managed,
                        message="Waiting for a fresh, stable server-info file",
                        recent_restart_count=recent_restart_count,
                    )
                    server_info_path = self.process_manager.wait_for_server_info(managed)
                    self._write_status(
                        "connecting",
                        managed=managed,
                        message="Connecting PyFluent to the worker-owned Fluent process",
                        recent_restart_count=recent_restart_count,
                    )
                    session = self._connect(server_info_path)
                    self._write_status(
                        "running",
                        managed=managed,
                        message="Fluent process and gRPC session are active",
                        recent_restart_count=recent_restart_count,
                    )
                    self._monitor(
                        managed,
                        session,
                        deadline=deadline,
                        recent_restart_count=recent_restart_count,
                    )
                    break
                except Exception as exc:
                    self._last_error = f"{type(exc).__name__}: {exc}"
                    close_session_best_effort(
                        session,
                        timeout_seconds=self.config.health_timeout_seconds,
                    )
                    session = None
                    self.process_manager.stop(managed)
                    managed = None
                    self._restart_count += 1
                    try:
                        recent_restart_count = budget.record(self._monotonic())
                    except RestartLimitExceeded:
                        failed = True
                        self._write_status(
                            "failed",
                            message="Fluent restart budget exhausted",
                            recent_restart_count=self.config.max_restarts + 1,
                        )
                        raise

                    self._write_status(
                        "restarting",
                        message=(
                            f"Restarting after generation {self._generation} failed: "
                            f"{self._last_error}"
                        ),
                        recent_restart_count=recent_restart_count,
                    )
                    if self.stop_event.is_set():
                        break
                    self._sleep(self.config.restart_delay_seconds)
        finally:
            close_session_best_effort(
                session,
                timeout_seconds=self.config.health_timeout_seconds,
            )
            self.process_manager.stop(managed)
            if not failed:
                self._write_status(
                    "stopped",
                    message="Host worker stopped; worker-owned Fluent process terminated",
                    recent_restart_count=recent_restart_count,
                )
