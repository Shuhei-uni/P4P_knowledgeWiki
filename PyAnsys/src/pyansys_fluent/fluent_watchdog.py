"""Narrow self-healing Fluent host supervisor.

The watchdog owns only Fluent availability:

* launch a Fluent process and its process tree;
* verify process and gRPC health;
* publish the current generation's endpoint through the private bridge; and
* replace genuinely dead or repeatedly unhealthy Fluent generations.

It intentionally contains no setup construction, job dispatch, case selection,
iteration control, or automatic scientific recovery logic.
"""

from __future__ import annotations

import os
import queue
import signal
import subprocess
import threading
import time
import uuid
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from pyansys_fluent.bridge import (
    BridgePaths,
    ConnectionPublisher,
    FluentEndpoint,
    read_published_generation,
    read_server_info,
    utc_timestamp,
)


class RestartLimitExceeded(RuntimeError):
    """Raised when Fluent exhausts its rolling restart budget."""


class WatchdogAlreadyRunning(RuntimeError):
    """Raised when another watchdog owns the same runtime lock."""


class ProcessExited(RuntimeError):
    """Raised when the worker-owned Fluent process exits."""


class HealthFailureThresholdExceeded(RuntimeError):
    """Raised after consecutive gRPC health failures reach the threshold."""


@dataclass(frozen=True)
class WatchdogConfig:
    """Validated launch and monitoring configuration."""

    fluent_exe: Path
    bridge_dir: Path
    advertised_host: str
    runtime_dir: Path
    dimension: int = 3
    precision: str = "double"
    processor_count: int = 2
    gui: bool = False
    allow_remote_host: bool = False
    insecure_mode: bool = False
    startup_timeout_seconds: float = 180.0
    connect_timeout_seconds: float = 60.0
    health_timeout_seconds: float = 10.0
    health_interval_seconds: float = 10.0
    heartbeat_interval_seconds: float = 5.0
    poll_interval_seconds: float = 0.5
    restart_delay_seconds: float = 5.0
    consecutive_health_failures: int = 3
    max_restarts: int = 3
    restart_window_seconds: float = 600.0
    extra_fluent_args: tuple[str, ...] = ()

    def validate(self, *, require_executable: bool = True) -> None:
        if require_executable and not self.fluent_exe.is_file():
            raise FileNotFoundError(
                f"Fluent executable does not exist: {self.fluent_exe}"
            )
        if not self.bridge_dir.is_absolute():
            raise ValueError("FLUENT_BRIDGE_DIR must be an absolute path")
        if not self.runtime_dir.is_absolute():
            raise ValueError("watchdog runtime_dir must be an absolute path")
        if not self.advertised_host.strip():
            raise ValueError("FLUENT_ADVERTISED_HOST must not be empty")
        if self.dimension not in (2, 3):
            raise ValueError("dimension must be 2 or 3")
        if self.precision not in ("single", "double"):
            raise ValueError("precision must be 'single' or 'double'")
        if self.processor_count <= 0:
            raise ValueError("processor_count must be positive")
        positive_fields = {
            "startup_timeout_seconds": self.startup_timeout_seconds,
            "connect_timeout_seconds": self.connect_timeout_seconds,
            "health_timeout_seconds": self.health_timeout_seconds,
            "health_interval_seconds": self.health_interval_seconds,
            "heartbeat_interval_seconds": self.heartbeat_interval_seconds,
            "poll_interval_seconds": self.poll_interval_seconds,
            "restart_window_seconds": self.restart_window_seconds,
        }
        for name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.restart_delay_seconds < 0:
            raise ValueError("restart_delay_seconds must be non-negative")
        if self.consecutive_health_failures <= 0:
            raise ValueError("consecutive_health_failures must be positive")
        if self.max_restarts < 0:
            raise ValueError("max_restarts must be non-negative")

    @property
    def fluent_mode_argument(self) -> str:
        suffix = "ddp" if self.precision == "double" else "d"
        return f"{self.dimension}{suffix}"

    def server_info_path(self, generation: int) -> Path:
        if generation <= 0:
            raise ValueError("generation must be positive")
        return self.runtime_dir / f"fluent-server-info-{generation:03d}.txt"

    def grpc_launch_args(self) -> tuple[str, ...]:
        """Return the launch-time gRPC exposure settings for this generation.

        Fluent 2025 R2 decides whether remote gRPC clients are permitted when
        the process starts.  Rewriting ``localhost`` in the published
        server-info document cannot change a loopback-only listener.
        """

        args: list[str] = []
        if self.allow_remote_host:
            args.append("-grpc-allow-remote-host")
        if self.insecure_mode:
            args.append("-grpc-insecure-mode")
        return tuple(args)

    @property
    def lock_path(self) -> Path:
        return self.runtime_dir / "fluent-watchdog.lock"


@dataclass
class ManagedFluentProcess:
    """One watchdog-owned Fluent generation."""

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


class ExclusiveWatchdogLock:
    """Cross-platform, non-blocking lock for one watchdog runtime."""

    def __init__(self, path: Path):
        self.path = Path(path)
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
            raise WatchdogAlreadyRunning(
                f"Another Fluent watchdog owns lock: {self.path}"
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

    def __enter__(self) -> "ExclusiveWatchdogLock":
        self.acquire()
        return self

    def __exit__(self, _exc_type, _exc, _traceback) -> None:
        self.release()


def call_with_timeout(
    callback: Callable[[], Any],
    timeout_seconds: float,
    *,
    label: str,
) -> Any:
    """Run a possibly blocking PyFluent call behind a hard caller timeout."""

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    result_queue: queue.Queue[tuple[bool, Any]] = queue.Queue(maxsize=1)
    abandoned = threading.Event()

    def invoke() -> None:
        try:
            value = callback()
            if not abandoned.is_set():
                result_queue.put((True, value))
        except Exception as exc:
            if not abandoned.is_set():
                result_queue.put((False, exc))

    threading.Thread(
        target=invoke,
        name=f"fluent-watchdog-{label}",
        daemon=True,
    ).start()
    try:
        succeeded, value = result_queue.get(timeout=timeout_seconds)
    except queue.Empty as exc:
        abandoned.set()
        raise TimeoutError(
            f"{label} did not complete within {timeout_seconds:.1f} seconds"
        ) from exc
    if succeeded:
        return value
    raise value


def close_monitor_session_best_effort(
    session: Any | None,
    *,
    timeout_seconds: float,
) -> bool:
    """Close the cleanup-disabled watchdog client without owning Fluent exit."""

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
            label="monitor-detach",
        )
        return True
    except Exception:
        return False


def _health_value_is_serving(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {
        "1",
        "active",
        "healthy",
        "ok",
        "serving",
        "status.serving",
        "true",
    }


def session_is_active(session: Any) -> bool:
    """Check current and older PyFluent health API shapes."""

    active = getattr(session, "is_active", None)
    if callable(active):
        return _health_value_is_serving(active())
    health = getattr(session, "health_check", None)
    if health is None:
        raise AttributeError("Session has no supported health API")
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


def connect_from_server_info(path: Path, config: WatchdogConfig) -> Any:
    """Connect a monitoring client without assuming Fluent cleanup ownership."""

    import ansys.fluent.core as pyfluent

    try:
        pyfluent.config.check_health_timeout = max(
            1, int(config.health_timeout_seconds)
        )
    except Exception:
        pass
    return pyfluent.connect_to_fluent(
        server_info_file_name=str(path),
        allow_remote_host=False,
        cleanup_on_exit=False,
        start_transcript=False,
        start_watchdog=False,
        insecure_mode=config.insecure_mode,
    )


class RestartBudget:
    """Track restart attempts in a rolling window."""

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
    """Kill-on-close Windows Job Object."""

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


def _assign_windows_kill_on_close_job(
    process: subprocess.Popen[str],
) -> _WindowsJobObject:
    if os.name != "nt":
        raise RuntimeError("Windows Job Objects are available only on Windows")

    import ctypes
    from ctypes import wintypes

    class BasicLimits(ctypes.Structure):
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

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimits),
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
    kernel32.AssignProcessToJobObject.argtypes = [
        wintypes.HANDLE,
        wintypes.HANDLE,
    ]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    job_handle = kernel32.CreateJobObjectW(None, None)
    if not job_handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = 0x00002000
        if not kernel32.SetInformationJobObject(
            job_handle,
            9,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
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
    """Launch and terminate only processes owned by this watchdog."""

    def __init__(
        self,
        config: WatchdogConfig,
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
        self.config.runtime_dir.mkdir(parents=True, exist_ok=True)
        if os.name != "nt":
            try:
                self.config.runtime_dir.chmod(0o700)
            except OSError:
                pass
        server_info = self.config.server_info_path(generation)
        server_info.unlink(missing_ok=True)
        stdout_path = (
            self.config.runtime_dir
            / f"fluent-generation-{generation:03d}-stdout.log"
        )
        stderr_path = (
            self.config.runtime_dir
            / f"fluent-generation-{generation:03d}-stderr.log"
        )
        stdout_handle = stdout_path.open(
            "w", encoding="utf-8", errors="replace"
        )
        stderr_handle = stderr_path.open(
            "w", encoding="utf-8", errors="replace"
        )
        command = [
            str(self.config.fluent_exe),
            self.config.fluent_mode_argument,
            f"-t{self.config.processor_count}",
        ]
        if not self.config.gui:
            command.append("-g")
        command.extend(self.config.grpc_launch_args())
        command.extend(self.config.extra_fluent_args)
        command.append(f"-sifile={server_info}")

        creationflags = 0
        start_new_session = False
        if os.name == "nt":
            creationflags = int(
                getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            )
        else:
            start_new_session = True
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=stdout_handle,
                stderr=stderr_handle,
                cwd=str(self.config.runtime_dir),
                text=True,
                bufsize=1,
                creationflags=creationflags,
                start_new_session=start_new_session,
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
                # Some managed Windows environments already assign the child
                # to a job.  taskkill /T remains the bounded fallback.
                process_tree_token = None
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
        previous_endpoint: FluentEndpoint | None = None
        stable_reads = 0
        while self._monotonic() < deadline:
            return_code = managed.process.poll()
            if return_code is not None:
                raise ProcessExited(
                    f"Fluent generation {managed.generation} exited before "
                    f"server-info was ready (return code {return_code})"
                )
            try:
                endpoint = read_server_info(managed.server_info_path)
            except (OSError, ValueError):
                endpoint = None
            if endpoint is not None:
                if endpoint == previous_endpoint:
                    stable_reads += 1
                else:
                    previous_endpoint = endpoint
                    stable_reads = 1
                if stable_reads >= 2:
                    if os.name != "nt":
                        try:
                            managed.server_info_path.chmod(0o600)
                        except OSError:
                            pass
                    return managed.server_info_path
            else:
                previous_endpoint = None
                stable_reads = 0
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
                        process.wait(timeout=10)
            elif os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if process.poll() is None:
                    try:
                        process.kill()
                    finally:
                        process.wait(timeout=10)
            else:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                if process.poll() is None:
                    try:
                        process.wait(timeout=20)
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        process.wait(timeout=10)
                # The launcher may exit before MPI descendants.  A final
                # group kill is scoped to the new session created at launch.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
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


def _safe_error(exc: BaseException, endpoint: FluentEndpoint | None) -> str:
    text = str(exc).replace("\r", " ").replace("\n", " ").strip()
    if endpoint is not None and endpoint.password:
        text = text.replace(endpoint.password, "<redacted>")
    if len(text) > 500:
        text = text[:497] + "..."
    return f"{type(exc).__name__}: {text}" if text else type(exc).__name__


class FluentWatchdog:
    """Own, monitor, and relaunch one Fluent process."""

    def __init__(
        self,
        config: WatchdogConfig,
        *,
        process_manager: FluentProcessManager | None = None,
        connect_factory: Callable[[Path, WatchdogConfig], Any] = (
            connect_from_server_info
        ),
        publisher: ConnectionPublisher | None = None,
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
            wall_time=wall_time,
        )
        self.connect_factory = connect_factory
        self.publisher = publisher or ConnectionPublisher(
            BridgePaths(config.bridge_dir)
        )
        self.stop_event = stop_event or threading.Event()
        self._sleep = sleep
        self._monotonic = monotonic
        self._wall_time = wall_time
        self._boot_id = uuid.uuid4().hex
        self._heartbeat_sequence = 0
        self._generation = 0
        self._restart_count = 0
        self._fluent_version: str | None = None
        self._started_at: str | None = None
        self._restart_reason: str | None = None
        self._last_health_at: str | None = None

    def request_stop(self) -> None:
        self.stop_event.set()

    def _publish(
        self,
        status: str,
        *,
        endpoint: FluentEndpoint | None = None,
        managed: ManagedFluentProcess | None = None,
        recent_restart_count: int = 0,
        consecutive_health_failures: int = 0,
    ) -> None:
        self._heartbeat_sequence += 1
        self.publisher.publish(
            status,
            generation=self._generation,
            previous_generation=(
                self._generation - 1 if self._generation > 1 else None
            ),
            heartbeat_sequence=self._heartbeat_sequence,
            endpoint=endpoint,
            fluent_pid=managed.pid if managed is not None else None,
            fluent_version=self._fluent_version,
            started_at=self._started_at,
            restart_reason=self._restart_reason,
            updated_at=utc_timestamp(self._wall_time()),
            extra={
                "watchdog_boot_id": self._boot_id,
                "watchdog_pid": os.getpid(),
                "restart_count_total": self._restart_count,
                "restart_count_in_window": recent_restart_count,
                "consecutive_health_failures": (
                    consecutive_health_failures
                ),
                "last_health_at": self._last_health_at,
            },
        )

    def _connect(self, server_info_path: Path) -> Any:
        session = call_with_timeout(
            lambda: self.connect_factory(server_info_path, self.config),
            self.config.connect_timeout_seconds,
            label="connect",
        )
        try:
            active = call_with_timeout(
                lambda: session_is_active(session),
                self.config.health_timeout_seconds,
                label="initial-health",
            )
            if not active:
                raise RuntimeError(
                    "PyFluent connected but health is not serving"
                )
            self._last_health_at = utc_timestamp(self._wall_time())
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
            else:
                self._fluent_version = "<unavailable>"
        except Exception:
            close_monitor_session_best_effort(
                session,
                timeout_seconds=self.config.health_timeout_seconds,
            )
            raise
        return session

    def _monitor(
        self,
        managed: ManagedFluentProcess,
        session: Any,
        endpoint: FluentEndpoint,
        *,
        deadline: float | None,
        recent_restart_count: int,
    ) -> None:
        next_health = self._monotonic() + self.config.health_interval_seconds
        next_heartbeat = self._monotonic()
        failures = 0
        while not self.stop_event.is_set():
            now = self._monotonic()
            if deadline is not None and now >= deadline:
                self.request_stop()
                break
            return_code = managed.process.poll()
            if return_code is not None:
                raise ProcessExited(
                    f"Fluent generation {managed.generation} exited with "
                    f"return code {return_code}"
                )
            if now >= next_health:
                try:
                    active = call_with_timeout(
                        lambda: session_is_active(session),
                        self.config.health_timeout_seconds,
                        label="health",
                    )
                    if not active:
                        raise RuntimeError("Fluent gRPC health is not serving")
                except Exception as exc:
                    failures += 1
                    if failures >= self.config.consecutive_health_failures:
                        raise HealthFailureThresholdExceeded(
                            f"{failures} consecutive Fluent gRPC health "
                            f"failures; latest was {type(exc).__name__}"
                        ) from exc
                else:
                    failures = 0
                    self._last_health_at = utc_timestamp(self._wall_time())
                next_health = now + self.config.health_interval_seconds
            if now >= next_heartbeat:
                self._publish(
                    "running",
                    endpoint=endpoint,
                    managed=managed,
                    recent_restart_count=recent_restart_count,
                    consecutive_health_failures=failures,
                )
                next_heartbeat = now + self.config.heartbeat_interval_seconds
            self._sleep(self.config.poll_interval_seconds)

    def run(self, *, max_runtime_seconds: float = 0.0) -> None:
        """Run until stopped, replacing Fluent only within the restart budget."""

        if max_runtime_seconds < 0:
            raise ValueError("max_runtime_seconds must be non-negative")
        deadline = (
            self._monotonic() + max_runtime_seconds
            if max_runtime_seconds
            else None
        )
        budget = RestartBudget(
            self.config.max_restarts,
            self.config.restart_window_seconds,
        )
        try:
            durable_generation = read_published_generation(
                self.config.bridge_dir
            )
        except FileNotFoundError:
            durable_generation = 0
        self._generation = max(self._generation, durable_generation)
        managed: ManagedFluentProcess | None = None
        session: Any | None = None
        endpoint: FluentEndpoint | None = None
        recent_restarts = 0
        terminal_failure = False
        try:
            while not self.stop_event.is_set():
                if deadline is not None and self._monotonic() >= deadline:
                    self.request_stop()
                    break
                self._generation += 1
                self._fluent_version = None
                self._started_at = None
                endpoint = None
                self._publish(
                    "starting",
                    recent_restart_count=recent_restarts,
                )
                try:
                    managed = self.process_manager.launch(self._generation)
                    self._started_at = utc_timestamp(
                        managed.launched_unix_seconds
                    )
                    server_info_path = (
                        self.process_manager.wait_for_server_info(managed)
                    )
                    endpoint = read_server_info(
                        server_info_path,
                        advertised_host=self.config.advertised_host,
                    )
                    session = self._connect(server_info_path)
                    self._publish(
                        "running",
                        endpoint=endpoint,
                        managed=managed,
                        recent_restart_count=recent_restarts,
                    )
                    self._monitor(
                        managed,
                        session,
                        endpoint,
                        deadline=deadline,
                        recent_restart_count=recent_restarts,
                    )
                    break
                except Exception as exc:
                    self._restart_reason = _safe_error(exc, endpoint)
                    close_monitor_session_best_effort(
                        session,
                        timeout_seconds=self.config.health_timeout_seconds,
                    )
                    session = None
                    self.process_manager.stop(managed)
                    managed = None
                    endpoint = None
                    self._restart_count += 1
                    try:
                        recent_restarts = budget.record(self._monotonic())
                    except RestartLimitExceeded:
                        terminal_failure = True
                        self._publish(
                            "failed",
                            recent_restart_count=self.config.max_restarts + 1,
                        )
                        raise
                    self._publish(
                        "restarting",
                        recent_restart_count=recent_restarts,
                    )
                    if self.stop_event.is_set():
                        break
                    self._sleep(self.config.restart_delay_seconds)
        finally:
            close_monitor_session_best_effort(
                session,
                timeout_seconds=self.config.health_timeout_seconds,
            )
            session = None
            self.process_manager.stop(managed)
            if not terminal_failure:
                self._publish(
                    "stopped",
                    recent_restart_count=recent_restarts,
                )
