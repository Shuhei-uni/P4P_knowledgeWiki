"""Phase 1 hardening for worker-owned Fluent recovery.

This module layers two live-test fixes over the proven Phase 1 implementation:

* a worker-owned filesystem control channel that can terminate the complete
  current Fluent generation without exposing server-info credentials; and
* fresh-client case/data reopen verification before a checkpoint is committed
  as the next resumable source.

The checkpoint verifier intentionally uses a second cleanup-disabled PyFluent
client connected to the same worker-owned Fluent generation. This avoids
requiring a second concurrent Fluent licence while still proving that Fluent can
read the candidate case/data pair before ``run-state.json`` advances.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .host_worker import (
    FluentGenerationRetryRequested,
    FluentHostWorker,
    HostWorkerConfig,
    ManagedFluentProcess,
    call_with_timeout,
    close_session_best_effort,
    session_is_active,
)
from .job_protocol import (
    FilesystemJobSpool,
    HealthStageContext,
    JobStageProcessor,
    utc_timestamp,
)
from .resumable_run import (
    AtomicRunStateStore,
    CheckpointVerificationError,
    FluentRunOperations,
    ResumableRunStageClient,
)

CONTROL_SCHEMA_VERSION = 1
CONTROL_ACTION = "terminate_current_generation"
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.tmp-{os.getpid()}-{threading.get_ident()}-{uuid.uuid4().hex}"
    )
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(dict(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


@dataclass(frozen=True)
class GenerationTerminationRequest:
    """Version-pinned request to stop the worker-owned current generation."""

    request_id: str
    expected_worker_boot_id: str
    expected_fluent_generation: int
    submitted_at: str = field(default_factory=utc_timestamp)
    action: str = CONTROL_ACTION
    schema_version: int = CONTROL_SCHEMA_VERSION

    def validate(self) -> None:
        if self.schema_version != CONTROL_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported control schema {self.schema_version}; "
                f"expected {CONTROL_SCHEMA_VERSION}"
            )
        if not isinstance(self.request_id, str) or not _REQUEST_ID_PATTERN.fullmatch(
            self.request_id
        ):
            raise ValueError("request_id must contain 1-128 safe filename characters")
        if self.request_id in {".", ".."}:
            raise ValueError("request_id cannot be '.' or '..'")
        if self.action != CONTROL_ACTION:
            raise ValueError(f"Unsupported control action {self.action!r}")
        if (
            not isinstance(self.expected_worker_boot_id, str)
            or not self.expected_worker_boot_id.strip()
        ):
            raise ValueError("expected_worker_boot_id must be non-empty")
        _positive_int(
            self.expected_fluent_generation,
            "expected_fluent_generation",
        )
        if not isinstance(self.submitted_at, str) or not self.submitted_at.strip():
            raise ValueError("submitted_at must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "action": self.action,
            "submitted_at": self.submitted_at,
            "expected_worker_boot_id": self.expected_worker_boot_id,
            "expected_fluent_generation": self.expected_fluent_generation,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "GenerationTerminationRequest":
        if not isinstance(payload, Mapping):
            raise ValueError("Control request must be a JSON object")
        allowed = {
            "schema_version",
            "request_id",
            "action",
            "submitted_at",
            "expected_worker_boot_id",
            "expected_fluent_generation",
        }
        unknown = set(payload) - allowed
        if unknown:
            raise ValueError(f"Unknown control request fields: {sorted(unknown)}")
        request = cls(
            schema_version=payload["schema_version"],
            request_id=payload["request_id"],
            action=payload["action"],
            submitted_at=payload["submitted_at"],
            expected_worker_boot_id=payload["expected_worker_boot_id"],
            expected_fluent_generation=payload["expected_fluent_generation"],
        )
        request.validate()
        return request


@dataclass(frozen=True)
class ClaimedControlRequest:
    path: Path
    original_name: str
    request: GenerationTerminationRequest | None
    validation_error: str | None = None


class GenerationControlSpool:
    """Atomic local control queue independent of the blocking job stage queue."""

    def __init__(self, runtime_dir: Path):
        root = Path(runtime_dir) / "control"
        self.incoming_dir = root / "incoming"
        self.running_dir = root / "running"
        self.completed_dir = root / "completed"
        self.failed_dir = root / "failed"
        self.receipts_dir = root / "receipts"

    def ensure_layout(self) -> None:
        for directory in (
            self.incoming_dir,
            self.running_dir,
            self.completed_dir,
            self.failed_dir,
            self.receipts_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def submit(self, request: GenerationTerminationRequest) -> Path:
        request.validate()
        self.ensure_layout()
        path = self.incoming_dir / f"{request.request_id}.json"
        if path.exists():
            raise FileExistsError(f"Control request already exists: {request.request_id}")
        _atomic_write_json(path, request.to_dict())
        return path

    def claim_next(self, worker_boot_id: str) -> ClaimedControlRequest | None:
        self.ensure_layout()
        for source in sorted(self.incoming_dir.glob("*.json")):
            destination = self.running_dir / (
                f"{source.stem}.{worker_boot_id}.{uuid.uuid4().hex}.json"
            )
            try:
                os.replace(source, destination)
            except FileNotFoundError:
                continue
            try:
                request = GenerationTerminationRequest.from_dict(
                    json.loads(destination.read_text(encoding="utf-8"))
                )
            except Exception as exc:
                return ClaimedControlRequest(
                    path=destination,
                    original_name=source.name,
                    request=None,
                    validation_error=f"{type(exc).__name__}: {exc}",
                )
            return ClaimedControlRequest(
                path=destination,
                original_name=source.name,
                request=request,
            )
        return None

    def finish(self, claim: ClaimedControlRequest, receipt: Mapping[str, Any]) -> Path:
        self.ensure_layout()
        request_id = str(receipt["request_id"])
        receipt_path = self.receipts_dir / f"{request_id}.json"
        _atomic_write_json(receipt_path, receipt)
        committed = json.loads(receipt_path.read_text(encoding="utf-8"))
        if committed != dict(receipt):
            raise RuntimeError("Committed control receipt readback differs")
        destination_dir = (
            self.completed_dir if receipt.get("status") == "success" else self.failed_dir
        )
        destination = destination_dir / claim.original_name
        _atomic_write_json(
            claim.path,
            {
                "request": claim.request.to_dict() if claim.request else None,
                "receipt_path": str(receipt_path.resolve()),
                "receipt": dict(receipt),
            },
        )
        os.replace(claim.path, destination)
        return receipt_path


def submit_generation_termination_request(
    runtime_dir: Path,
    *,
    request_id: str,
    expected_worker_boot_id: str,
    expected_fluent_generation: int,
) -> Path:
    """Publish one safe, generation-pinned local termination request."""

    return GenerationControlSpool(runtime_dir).submit(
        GenerationTerminationRequest(
            request_id=request_id,
            expected_worker_boot_id=expected_worker_boot_id,
            expected_fluent_generation=expected_fluent_generation,
        )
    )


def _read_server_port_without_credentials(server_info_path: Path) -> int | None:
    try:
        with server_info_path.open("r", encoding="utf-8", errors="replace") as stream:
            host_port = stream.readline().strip()
    except OSError:
        return None
    if ":" not in host_port:
        return None
    try:
        port = int(host_port.rsplit(":", 1)[1])
    except ValueError:
        return None
    return port if 1 <= port <= 65535 else None


def discover_grpc_server_pid(server_info_path: Path) -> int | None:
    """Find the local listening PID from only the non-secret server-info port."""

    if os.name != "nt":
        return None
    port = _read_server_port_without_credentials(server_info_path)
    if port is None:
        return None
    try:
        result = subprocess.run(
            ["netstat", "-ano", "-p", "tcp"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    for raw_line in result.stdout.splitlines():
        parts = raw_line.split()
        if len(parts) < 5 or parts[0].upper() != "TCP":
            continue
        if parts[-2].upper() != "LISTENING":
            continue
        try:
            local_port = int(parts[1].rsplit(":", 1)[1])
            pid = int(parts[-1])
        except (IndexError, ValueError):
            continue
        if local_port == port and pid > 0:
            return pid
    return None


def _process_exists(pid: int | None) -> bool:
    if pid is None or pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    handle = kernel32.OpenProcess(0x1000, False, pid)
    if not handle:
        return False
    kernel32.CloseHandle(handle)
    return True


class ControlledFluentHostWorker(FluentHostWorker):
    """Host worker with an independent generation-control polling thread."""

    control_poll_seconds = 0.2

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.control_spool = GenerationControlSpool(self.config.work_dir)

    @staticmethod
    def _launcher_alive(managed: ManagedFluentProcess | None) -> bool:
        return bool(managed is not None and managed.process.poll() is None)

    def _grpc_server_pid(self, managed: ManagedFluentProcess | None) -> int | None:
        if managed is None:
            return None
        return discover_grpc_server_pid(managed.server_info_path)

    def _process_tree_alive(self, managed: ManagedFluentProcess | None) -> bool:
        if managed is None:
            return False
        grpc_pid = self._grpc_server_pid(managed)
        if grpc_pid is not None:
            return _process_exists(grpc_pid)
        return self._launcher_alive(managed)

    def _observed_fluent_pid(self, managed: ManagedFluentProcess) -> int:
        return self._grpc_server_pid(managed) or managed.pid

    def _write_status(
        self,
        state: str,
        *,
        managed: ManagedFluentProcess | None = None,
        message: str = "",
        recent_restart_count: int = 0,
    ) -> None:
        super()._write_status(
            state,
            managed=managed,
            message=message,
            recent_restart_count=recent_restart_count,
        )
        try:
            payload = json.loads(self.config.status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        grpc_pid = self._grpc_server_pid(managed)
        tree_alive = self._process_tree_alive(managed)
        payload.update(
            {
                "launcher_pid": managed.pid if managed is not None else None,
                "launcher_process_alive": self._launcher_alive(managed),
                "grpc_server_pid": grpc_pid,
                "process_tree_owned": bool(
                    managed is not None and managed.process_tree_token is not None
                ),
                "process_tree_alive": tree_alive,
                "fluent_pid": (
                    grpc_pid
                    if grpc_pid is not None
                    else (managed.pid if managed is not None else None)
                ),
                "fluent_process_alive": tree_alive,
            }
        )
        self.status_store.write(payload)

    def _handle_control_claim(
        self,
        claim: ClaimedControlRequest,
        managed: ManagedFluentProcess,
    ) -> None:
        started_at = utc_timestamp()
        request = claim.request
        request_id = request.request_id if request is not None else claim.path.stem
        grpc_pid = self._grpc_server_pid(managed)
        receipt: dict[str, Any] = {
            "schema_version": CONTROL_SCHEMA_VERSION,
            "request_id": request_id,
            "action": CONTROL_ACTION,
            "status": "failed",
            "started_at": started_at,
            "completed_at": started_at,
            "expected_worker_boot_id": (
                request.expected_worker_boot_id if request is not None else None
            ),
            "observed_worker_boot_id": self._boot_id,
            "expected_fluent_generation": (
                request.expected_fluent_generation if request is not None else None
            ),
            "observed_fluent_generation": managed.generation,
            "launcher_pid": managed.pid,
            "grpc_server_pid": grpc_pid,
            "process_tree_owned": managed.process_tree_token is not None,
            "termination_requested": False,
            "termination_observed": False,
            "error": claim.validation_error,
        }
        try:
            if request is None:
                raise ValueError(claim.validation_error or "Malformed control request")
            request.validate()
            if request.expected_worker_boot_id != self._boot_id:
                raise RuntimeError(
                    "Worker boot mismatch: expected "
                    f"{request.expected_worker_boot_id}, observed {self._boot_id}"
                )
            if request.expected_fluent_generation != managed.generation:
                raise RuntimeError(
                    "Fluent generation mismatch: expected "
                    f"{request.expected_fluent_generation}, observed {managed.generation}"
                )
            if managed.process_tree_token is None and os.name == "nt":
                raise RuntimeError("Worker does not own a Windows Job Object")
            receipt["termination_requested"] = True
            self.process_manager.stop(managed)
            deadline = time.monotonic() + 30.0
            while self._process_tree_alive(managed) and time.monotonic() < deadline:
                time.sleep(0.1)
            receipt["termination_observed"] = not self._process_tree_alive(managed)
            if not receipt["termination_observed"]:
                raise RuntimeError("Fluent process tree remained alive after termination")
            receipt["status"] = "success"
            receipt["error"] = None
        except Exception as exc:
            receipt["error"] = {
                "type": type(exc).__name__,
                "message": str(exc) or type(exc).__name__,
                "retryable": False,
            }
        finally:
            receipt["completed_at"] = utc_timestamp()
            self.control_spool.finish(claim, receipt)

    def _control_loop(
        self,
        managed: ManagedFluentProcess,
        stop_event: threading.Event,
    ) -> None:
        while not stop_event.is_set() and not self.stop_event.is_set():
            claim = self.control_spool.claim_next(self._boot_id)
            if claim is None:
                stop_event.wait(self.control_poll_seconds)
                continue
            self._handle_control_claim(claim, managed)
            if not self._process_tree_alive(managed):
                return

    def _monitor(
        self,
        managed: ManagedFluentProcess,
        session: Any,
        *,
        deadline: float | None,
        recent_restart_count: int,
    ) -> None:
        control_stop = threading.Event()
        control_thread = threading.Thread(
            target=self._control_loop,
            args=(managed, control_stop),
            name=f"fluent-generation-{managed.generation}-control",
            daemon=True,
        )
        control_thread.start()
        next_health = self._monotonic()
        next_heartbeat = self._monotonic()
        next_job_poll = self._monotonic()
        try:
            while not self.stop_event.is_set():
                now = self._monotonic()
                if deadline is not None and now >= deadline:
                    self.request_stop()
                    break
                if not self._process_tree_alive(managed):
                    raise RuntimeError(
                        f"Fluent generation {managed.generation} process tree exited"
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
                        message="Fluent process tree and gRPC session are active",
                        recent_restart_count=recent_restart_count,
                    )
                    next_heartbeat = now + self.config.heartbeat_interval_seconds
                if now >= next_job_poll:
                    try:
                        self.job_processor.process_next(
                            HealthStageContext(
                                worker_boot_id=self._boot_id,
                                fluent_generation=managed.generation,
                                fluent_pid=self._observed_fluent_pid(managed),
                                server_info_path=managed.server_info_path,
                                config=self.config,
                                process_is_alive=lambda: self._process_tree_alive(managed),
                            )
                        )
                    except FluentGenerationRetryRequested:
                        raise
                    except Exception as exc:
                        self._last_error = (
                            f"Job protocol {type(exc).__name__}: {exc}"
                        )
                    next_job_poll = now + self.config.job_poll_interval_seconds
                self._sleep(self.config.poll_interval_seconds)
        finally:
            control_stop.set()
            control_thread.join(timeout=2.0)


class FreshClientCheckpointVerifier:
    """Reopen a candidate pair through a second cleanup-disabled client."""

    def __init__(
        self,
        *,
        operations: FluentRunOperations | None = None,
        timestamp_factory: Callable[[], str] = utc_timestamp,
    ):
        self.operations = operations or FluentRunOperations()
        self.timestamp_factory = timestamp_factory

    def verify(
        self,
        *,
        case_path: Path,
        data_path: Path,
        context: HealthStageContext,
        connect_factory: Callable[[Path, HostWorkerConfig], Any],
        call: Callable[[str, Callable[[], Any]], Any],
    ) -> dict[str, Any]:
        started_at = self.timestamp_factory()
        session: Any | None = None
        detached = False
        health_result = False
        data_loaded = False
        fluent_version: str | None = None
        try:
            session = call(
                "checkpoint-reopen-connect",
                lambda: connect_factory(context.server_info_path, context.config),
            )
            if not bool(call("checkpoint-reopen-health", lambda: session_is_active(session))):
                raise CheckpointVerificationError(
                    "Checkpoint verification client connected with inactive health"
                )
            call(
                "checkpoint-reopen-case",
                lambda: self.operations.read_case(session, case_path),
            )
            call(
                "checkpoint-reopen-data",
                lambda: self.operations.read_data(session, data_path),
            )
            data_loaded = True
            health_result = bool(
                call(
                    "checkpoint-reopen-final-health",
                    lambda: session_is_active(session),
                )
            )
            if not health_result:
                raise CheckpointVerificationError(
                    "Fluent health failed after checkpoint case/data reopen"
                )
            get_version = getattr(session, "get_fluent_version", None)
            if callable(get_version):
                fluent_version = str(call("checkpoint-reopen-version", get_version))
        finally:
            if session is not None:
                detached = close_session_best_effort(
                    session,
                    timeout_seconds=context.config.health_timeout_seconds,
                )
        if not detached:
            raise CheckpointVerificationError(
                "Checkpoint verification client could not detach cleanly"
            )
        return {
            "mode": "fresh-client-same-generation",
            "verified": True,
            "verification_generation": context.fluent_generation,
            "verification_pid": context.fluent_pid,
            "started_at": started_at,
            "completed_at": self.timestamp_factory(),
            "case_path": str(case_path),
            "data_path": str(data_path),
            "data_loaded": data_loaded,
            "health_result": health_result,
            "client_detached": detached,
            "fluent_version": fluent_version,
            "case_identity": {
                "dimension": context.config.dimension,
                "precision": context.config.precision,
            },
        }


class ReopenVerifiedResumableRunStageClient(ResumableRunStageClient):
    """Resumable run client that reopens each candidate before committing it."""

    def __init__(
        self,
        *,
        reopen_verifier: FreshClientCheckpointVerifier | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.reopen_verifier = reopen_verifier or FreshClientCheckpointVerifier(
            operations=self.operations,
            timestamp_factory=self._timestamp_factory,
        )

    def _write_and_commit_checkpoint(
        self,
        spec: Any,
        state: dict[str, Any],
        state_store: AtomicRunStateStore,
        session: Any,
        context: HealthStageContext,
        *,
        attempt_index: int,
        iteration: int,
        call: Callable[[str, Callable[[], Any]], Any],
    ) -> None:
        checkpoint_dir = state_store.path.parent / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        stem = (
            f"candidate-{iteration:08d}-"
            f"generation-{context.fluent_generation:03d}-"
            f"attempt-{attempt_index:03d}-{uuid.uuid4().hex[:12]}"
        )
        case_path = (checkpoint_dir / f"{stem}.cas.h5").resolve()
        data_path = (checkpoint_dir / f"{stem}.dat.h5").resolve()
        call(
            f"write-case-{iteration}",
            lambda: self.operations.write_case(session, case_path),
        )
        call(
            f"write-data-{iteration}",
            lambda: self.operations.write_data(session, data_path),
        )
        case_size, data_size = call(
            f"verify-checkpoint-files-{iteration}",
            lambda: self.checkpoint_verifier(
                case_path,
                data_path,
                timeout_seconds=max(
                    0.001,
                    min(
                        float(spec.command_timeout_seconds),
                        max(1.0, context.config.health_timeout_seconds),
                    )
                    * 0.8,
                ),
            ),
        )
        verification = self.reopen_verifier.verify(
            case_path=case_path,
            data_path=data_path,
            context=context,
            connect_factory=self.connect_factory,
            call=call,
        )
        if not verification.get("verified") or not verification.get("data_loaded"):
            raise CheckpointVerificationError(
                "Candidate checkpoint did not pass reopen verification"
            )
        if not bool(call("primary-health-after-reopen", lambda: session_is_active(session))):
            raise CheckpointVerificationError(
                "Primary run client became unhealthy after checkpoint verification"
            )
        state["completed_iterations"] = iteration
        state["last_checkpoint"] = {
            "iteration": iteration,
            "case_path": str(case_path),
            "data_path": str(data_path),
            "case_size_bytes": case_size,
            "data_size_bytes": data_size,
            "committed_at": self._timestamp_factory(),
            "fluent_generation": context.fluent_generation,
            "fluent_pid": context.fluent_pid,
            "verification": verification,
        }
        state["updated_at"] = self._timestamp_factory()
        state_store.commit(state, spec=spec)


def build_hardened_job_processor(runtime_dir: Path) -> JobStageProcessor:
    """Construct the standard processor with reopen-verified run checkpoints."""

    return JobStageProcessor(
        FilesystemJobSpool(runtime_dir),
        resumable_run_client=ReopenVerifiedResumableRunStageClient(),
    )
