"""Transactional chunked Fluent run stage with generation-loss recovery.

This module deliberately supports one narrow policy:

* start from a case-only artifact;
* hybrid-initialize exactly before the first committed checkpoint;
* iterate in fixed chunks;
* write and verify a case/data pair after every chunk;
* commit the pair atomically into a run-state document; and
* after Fluent loss, load the latest committed pair without reinitializing.

An uncommitted or partial checkpoint is never selected as a resume source.
"""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from .case_probe import PreparedCaseInput, prepare_disposable_case_copy
from .host_worker import (
    FluentGenerationRetryRequested,
    HostWorkerConfig,
    call_with_timeout,
    close_session_best_effort,
    connect_from_server_info,
    session_is_active,
)
from .job_protocol import (
    HealthStageContext,
    JobSpec,
    StageReceipt,
    structured_error,
    utc_timestamp,
)


RUN_STATE_SCHEMA_VERSION = 1
RUN_STATE_STATUSES = frozenset({"running", "retryable", "completed", "failed"})


class RunStateValidationError(ValueError):
    """Raised when durable run state is missing required invariants."""


class CheckpointVerificationError(RuntimeError):
    """Raised when a Fluent checkpoint pair is absent, empty, or unstable."""


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


def _non_negative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RunStateValidationError(
            f"{field_name} must be a non-negative integer"
        )
    return value


def validate_run_state(
    payload: Mapping[str, Any],
    *,
    spec: JobSpec | None = None,
) -> dict[str, Any]:
    """Validate and normalize a persisted resumable-run state document."""

    if not isinstance(payload, Mapping):
        raise RunStateValidationError("Run state must be a JSON object")
    state = dict(payload)
    if state.get("schema_version") != RUN_STATE_SCHEMA_VERSION:
        raise RunStateValidationError(
            "Unsupported run-state schema_version "
            f"{state.get('schema_version')!r}"
        )
    job_id = state.get("job_id")
    if not isinstance(job_id, str) or not job_id:
        raise RunStateValidationError("Run state job_id must be non-empty")
    if state.get("status") not in RUN_STATE_STATUSES:
        raise RunStateValidationError(
            f"Invalid run-state status {state.get('status')!r}"
        )
    for field_name in (
        "total_iterations",
        "completed_iterations",
        "initialization_count",
        "resume_count",
    ):
        _non_negative_int(state.get(field_name), field_name)
    if state["total_iterations"] <= 0:
        raise RunStateValidationError("total_iterations must be positive")
    if state["completed_iterations"] > state["total_iterations"]:
        raise RunStateValidationError(
            "completed_iterations cannot exceed total_iterations"
        )
    for field_name in (
        "worker_boot_id",
        "requested_case_path",
        "resolved_case_path",
        "disposable_case_path",
        "started_at",
        "updated_at",
    ):
        if not isinstance(state.get(field_name), str) or not state[field_name]:
            raise RunStateValidationError(f"{field_name} must be non-empty")
    if not isinstance(state.get("attempts"), list):
        raise RunStateValidationError("attempts must be a list")

    checkpoint = state.get("last_checkpoint")
    if checkpoint is not None:
        if not isinstance(checkpoint, Mapping):
            raise RunStateValidationError(
                "last_checkpoint must be an object or null"
            )
        iteration = _non_negative_int(
            checkpoint.get("iteration"),
            "last_checkpoint.iteration",
        )
        if iteration != state["completed_iterations"]:
            raise RunStateValidationError(
                "last checkpoint iteration must equal completed_iterations"
            )
        for field_name in ("case_path", "data_path", "committed_at"):
            if (
                not isinstance(checkpoint.get(field_name), str)
                or not checkpoint[field_name]
            ):
                raise RunStateValidationError(
                    f"last_checkpoint.{field_name} must be non-empty"
                )
        for field_name in ("case_size_bytes", "data_size_bytes"):
            value = checkpoint.get(field_name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise RunStateValidationError(
                    f"last_checkpoint.{field_name} must be positive"
                )
    elif state["completed_iterations"] != 0:
        raise RunStateValidationError(
            "positive completed_iterations require a committed checkpoint"
        )

    if state["status"] == "completed":
        if checkpoint is None:
            raise RunStateValidationError(
                "completed run state requires a checkpoint"
            )
        if state["completed_iterations"] != state["total_iterations"]:
            raise RunStateValidationError(
                "completed run state must reach total_iterations"
            )

    if spec is not None:
        spec.validate()
        if spec.stage_type != "resumable_run":
            raise RunStateValidationError(
                "Run state can only be checked against resumable_run"
            )
        if state["job_id"] != spec.job_id:
            raise RunStateValidationError("Run-state job_id does not match job")
        if state["total_iterations"] != spec.total_iterations:
            raise RunStateValidationError(
                "Run-state total_iterations does not match job"
            )
        if state["requested_case_path"] != spec.case_path:
            raise RunStateValidationError(
                "Run-state requested_case_path does not match job"
            )
        if state["worker_boot_id"] != spec.expected_worker_boot_id:
            raise RunStateValidationError(
                "Run-state worker_boot_id does not match job"
            )
    return state


class AtomicRunStateStore:
    """Atomic JSON persistence for one resumable run."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self, *, spec: JobSpec | None = None) -> dict[str, Any] | None:
        if not self.path.is_file():
            return None
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return validate_run_state(payload, spec=spec)

    def commit(
        self,
        payload: Mapping[str, Any],
        *,
        spec: JobSpec | None = None,
    ) -> dict[str, Any]:
        validated = validate_run_state(payload, spec=spec)
        _atomic_write_json(self.path, validated)
        committed = self.load(spec=spec)
        if committed != validated:
            raise RunStateValidationError(
                "Committed run-state readback differs from requested state"
            )
        assert committed is not None
        return committed


def verify_checkpoint_pair(
    case_path: Path,
    data_path: Path,
    *,
    timeout_seconds: float,
    stable_reads_required: int = 2,
    poll_seconds: float = 0.1,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[int, int]:
    """Wait for a non-empty, size-stable local case/data pair."""

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if stable_reads_required < 2:
        raise ValueError("stable_reads_required must be at least 2")
    deadline = monotonic() + timeout_seconds
    previous: tuple[int, int] | None = None
    stable_reads = 0
    last_error = "files are not visible"

    while monotonic() < deadline:
        try:
            case_size = case_path.stat().st_size
            data_size = data_path.stat().st_size
            if case_size <= 0 or data_size <= 0:
                last_error = "one or both files are empty"
                stable_reads = 0
                previous = None
            else:
                current = (case_size, data_size)
                if current == previous:
                    stable_reads += 1
                else:
                    previous = current
                    stable_reads = 1
                if stable_reads >= stable_reads_required:
                    return current
        except OSError as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            stable_reads = 0
            previous = None
        remaining = max(0.0, deadline - monotonic())
        sleep(
            min(
                poll_seconds,
                timeout_seconds / (stable_reads_required + 1),
                remaining,
            )
        )

    raise CheckpointVerificationError(
        f"Checkpoint pair did not stabilize within {timeout_seconds:.1f}s: "
        f"{last_error}; case={case_path}; data={data_path}"
    )


class FluentRunOperations:
    """Minimal version-stable Settings API operations used by the run stage."""

    def read_case(self, session: Any, path: Path) -> None:
        session.settings.file.read_case(file_name=str(path))

    def read_data(self, session: Any, path: Path) -> None:
        session.settings.file.read_data(file_name=str(path))

    def hybrid_initialize(self, session: Any) -> None:
        session.settings.solution.initialization.hybrid_initialize()

    def iterate(self, session: Any, count: int) -> None:
        session.settings.solution.run_calculation.iterate(iter_count=count)

    def write_case(self, session: Any, path: Path) -> None:
        session.settings.file.write_case(file_name=str(path))

    def write_data(self, session: Any, path: Path) -> None:
        session.settings.file.write_data(file_name=str(path))


class ResumableRunStageClient:
    """Execute or resume one chunked run against a worker-owned generation."""

    def __init__(
        self,
        *,
        connect_factory: Callable[
            [Path, HostWorkerConfig], Any
        ] = connect_from_server_info,
        pyfluent_version_factory: Callable[[], str] | None = None,
        prepare_case_factory: Callable[
            [JobSpec, Path], PreparedCaseInput
        ] = prepare_disposable_case_copy,
        operations: FluentRunOperations | None = None,
        checkpoint_verifier: Callable[..., tuple[int, int]] = verify_checkpoint_pair,
        monotonic: Callable[[], float] = time.monotonic,
        timestamp_factory: Callable[[], str] = utc_timestamp,
    ):
        self.connect_factory = connect_factory
        self.pyfluent_version_factory = (
            pyfluent_version_factory or self._installed_pyfluent_version
        )
        self.prepare_case_factory = prepare_case_factory
        self.operations = operations or FluentRunOperations()
        self.checkpoint_verifier = checkpoint_verifier
        self._monotonic = monotonic
        self._timestamp_factory = timestamp_factory

    @staticmethod
    def _installed_pyfluent_version() -> str:
        import ansys.fluent.core as pyfluent

        return str(pyfluent.__version__)

    @staticmethod
    def _job_root(spec: JobSpec, context: HealthStageContext) -> Path:
        return (
            context.config.work_dir
            / "stage_artifacts"
            / "resumable_run"
            / spec.job_id
        )

    def execute(
        self,
        spec: JobSpec,
        context: HealthStageContext,
    ) -> StageReceipt:
        spec.validate()
        if spec.stage_type != "resumable_run":
            raise ValueError("ResumableRunStageClient requires resumable_run")
        assert spec.case_path is not None
        assert spec.total_iterations is not None
        assert spec.chunk_iterations is not None
        assert spec.command_timeout_seconds is not None
        assert spec.max_resume_attempts is not None

        attempt_started_at = self._timestamp_factory()
        deadline = self._monotonic() + float(spec.timeout_seconds)
        job_root = self._job_root(spec, context)
        state_store = AtomicRunStateStore(job_root / "run-state.json")
        state: dict[str, Any] | None = None
        session: Any | None = None
        fluent_version: str | None = None
        pyfluent_version: str | None = None
        health_result: bool | None = None
        detached = False
        terminal_error: dict[str, Any] | None = None
        retry_exception: BaseException | None = None
        attempt_index = 0

        def remaining(label: str) -> float:
            value = deadline - self._monotonic()
            if value <= 0:
                raise TimeoutError(
                    f"resumable_run timed out before {label} completed"
                )
            return min(value, float(spec.command_timeout_seconds))

        def call(label: str, callback: Callable[[], Any]) -> Any:
            return call_with_timeout(
                callback,
                remaining(label),
                label=f"resumable-run-{label}",
            )

        def commit_state() -> None:
            assert state is not None
            state["updated_at"] = self._timestamp_factory()
            state_store.commit(state, spec=spec)

        try:
            if spec.expected_worker_boot_id != context.worker_boot_id:
                raise RuntimeError(
                    "Worker boot mismatch: expected "
                    f"{spec.expected_worker_boot_id}, observed "
                    f"{context.worker_boot_id}"
                )
            if not context.process_is_alive():
                raise ConnectionError(
                    f"Fluent generation {context.fluent_generation} is not alive"
                )

            state = state_store.load(spec=spec)
            if state is None:
                if spec.expected_fluent_generation != context.fluent_generation:
                    raise RuntimeError(
                        "Initial Fluent generation mismatch: expected "
                        f"{spec.expected_fluent_generation}, observed "
                        f"{context.fluent_generation}"
                    )
                prepared = call(
                    "case-input-copy",
                    lambda: self.prepare_case_factory(
                        spec,
                        context.config.work_dir,
                    ),
                )
                job_root.mkdir(parents=True, exist_ok=True)
                state = {
                    "schema_version": RUN_STATE_SCHEMA_VERSION,
                    "job_id": spec.job_id,
                    "status": "running",
                    "worker_boot_id": context.worker_boot_id,
                    "initial_fluent_generation": context.fluent_generation,
                    "requested_case_path": prepared.requested_path,
                    "resolved_case_path": str(prepared.resolved_path),
                    "disposable_case_path": str(prepared.disposable_path),
                    "source_file_size_bytes": prepared.source_file_size_bytes,
                    "source_sha256": prepared.source_sha256,
                    "total_iterations": spec.total_iterations,
                    "completed_iterations": 0,
                    "initialization_count": 0,
                    "resume_count": 0,
                    "attempts": [],
                    "last_checkpoint": None,
                    "started_at": attempt_started_at,
                    "updated_at": attempt_started_at,
                }
            elif state["status"] == "completed":
                return self._receipt_from_completed_state(
                    spec,
                    context,
                    state,
                    state_store.path,
                )
            elif len(state["attempts"]) > spec.max_resume_attempts:
                raise RuntimeError(
                    "Resume-attempt budget was already exhausted"
                )

            attempt_index = len(state["attempts"]) + 1
            if attempt_index > 1:
                state["resume_count"] += 1
            attempt = {
                "attempt_number": attempt_index,
                "fluent_generation": context.fluent_generation,
                "fluent_pid": context.fluent_pid,
                "started_at": attempt_started_at,
                "completed_at": None,
                "status": "running",
                "resumed_from_iteration": state["completed_iterations"],
                "error": None,
            }
            state["status"] = "running"
            state["attempts"].append(attempt)
            commit_state()

            checkpoint = state["last_checkpoint"]
            if checkpoint is not None:
                checkpoint_case = Path(checkpoint["case_path"])
                checkpoint_data = Path(checkpoint["data_path"])
                observed_sizes = call(
                    "revalidate-resume-checkpoint",
                    lambda: self.checkpoint_verifier(
                        checkpoint_case,
                        checkpoint_data,
                        timeout_seconds=max(
                            0.001,
                            min(
                                float(spec.command_timeout_seconds),
                                max(
                                    1.0,
                                    context.config.health_timeout_seconds,
                                ),
                            )
                            * 0.8,
                        ),
                    ),
                )
                expected_sizes = (
                    checkpoint["case_size_bytes"],
                    checkpoint["data_size_bytes"],
                )
                if observed_sizes != expected_sizes:
                    raise CheckpointVerificationError(
                        "Committed resume checkpoint sizes changed: expected "
                        f"{expected_sizes}, observed {observed_sizes}"
                    )

            pyfluent_version = str(
                call("pyfluent-version", self.pyfluent_version_factory)
            )
            session = call(
                "connect",
                lambda: self.connect_factory(
                    context.server_info_path,
                    context.config,
                ),
            )
            health_result = bool(
                call("initial-health", lambda: session_is_active(session))
            )
            if not health_result:
                raise ConnectionError(
                    "Run client connected but gRPC health is inactive"
                )
            get_version = getattr(session, "get_fluent_version", None)
            if not callable(get_version):
                raise AttributeError(
                    "Run session does not expose get_fluent_version()"
                )
            fluent_version = str(call("fluent-version", get_version))

            if checkpoint is None:
                call(
                    "read-source-case",
                    lambda: self.operations.read_case(
                        session,
                        Path(state["disposable_case_path"]),
                    ),
                )
                call(
                    "hybrid-initialize",
                    lambda: self.operations.hybrid_initialize(session),
                )
                state["initialization_count"] += 1
                commit_state()
                self._write_and_commit_checkpoint(
                    spec,
                    state,
                    state_store,
                    session,
                    context,
                    attempt_index=attempt_index,
                    iteration=0,
                    call=call,
                )
            else:
                call(
                    "read-resume-case",
                    lambda: self.operations.read_case(
                        session,
                        Path(checkpoint["case_path"]),
                    ),
                )
                call(
                    "read-resume-data",
                    lambda: self.operations.read_data(
                        session,
                        Path(checkpoint["data_path"]),
                    ),
                )

            while state["completed_iterations"] < spec.total_iterations:
                step = min(
                    spec.chunk_iterations,
                    spec.total_iterations - state["completed_iterations"],
                )
                call(
                    f"iterate-{state['completed_iterations'] + step}",
                    lambda step=step: self.operations.iterate(session, step),
                )
                next_iteration = state["completed_iterations"] + step
                self._write_and_commit_checkpoint(
                    spec,
                    state,
                    state_store,
                    session,
                    context,
                    attempt_index=attempt_index,
                    iteration=next_iteration,
                    call=call,
                )

            health_result = bool(
                call("final-health", lambda: session_is_active(session))
            )
            if not health_result:
                raise ConnectionError(
                    "Run completed but final gRPC health is inactive"
                )
            state["status"] = "completed"
            state["fluent_version"] = fluent_version
            state["pyfluent_version"] = pyfluent_version
            attempt["status"] = "completed"
            attempt["completed_at"] = self._timestamp_factory()
            commit_state()
        except Exception as exc:
            process_alive = context.process_is_alive()
            retryable = (
                isinstance(exc, (TimeoutError, ConnectionError))
                or not process_alive
            )
            if state is not None and attempt_index > 0:
                attempt = state["attempts"][-1]
                attempt["status"] = "retryable" if retryable else "failed"
                attempt["completed_at"] = self._timestamp_factory()
                attempt["error"] = structured_error(exc, retryable=retryable)
                attempts_used = len(state["attempts"])
                retry_budget_available = (
                    attempts_used <= spec.max_resume_attempts
                )
                if retryable and retry_budget_available:
                    state["status"] = "retryable"
                    commit_state()
                    retry_exception = exc
                else:
                    state["status"] = "failed"
                    commit_state()
                    terminal_error = structured_error(exc, retryable=False)
            else:
                terminal_error = structured_error(exc, retryable=retryable)
        finally:
            if session is not None:
                detached = close_session_best_effort(
                    session,
                    timeout_seconds=min(
                        context.config.health_timeout_seconds,
                        float(spec.command_timeout_seconds),
                    ),
                )

        alive_after_detach = context.process_is_alive()
        if (
            retry_exception is None
            and terminal_error is None
            and state is not None
            and state["status"] == "completed"
            and not alive_after_detach
            and len(state["attempts"]) <= spec.max_resume_attempts
        ):
            retry_exception = ConnectionError(
                "Fluent terminated after the final checkpoint was committed"
            )
            attempt = state["attempts"][-1]
            attempt["status"] = "retryable"
            attempt["completed_at"] = self._timestamp_factory()
            attempt["error"] = structured_error(
                retry_exception,
                retryable=True,
            )
            state["status"] = "retryable"
            commit_state()

        if retry_exception is not None:
            raise FluentGenerationRetryRequested(
                f"Run {spec.job_id} committed retryable attempt "
                f"{attempt_index} for generation {context.fluent_generation}: "
                f"{type(retry_exception).__name__}: {retry_exception}"
            ) from retry_exception

        if terminal_error is None and not detached:
            terminal_error = structured_error(
                RuntimeError("Run client could not detach cleanly"),
                retryable=False,
            )
        if terminal_error is None and not alive_after_detach:
            terminal_error = structured_error(
                RuntimeError("Fluent terminated after final checkpoint"),
                retryable=False,
            )

        assert state is not None or terminal_error is not None
        if state is not None and terminal_error is not None:
            state["status"] = "failed"
            state["updated_at"] = self._timestamp_factory()
            state_store.commit(state, spec=spec)

        checkpoint = state.get("last_checkpoint") if state is not None else None
        generation_history = (
            tuple(
                int(attempt["fluent_generation"])
                for attempt in state["attempts"]
            )
            if state is not None
            else None
        )
        return StageReceipt(
            job_id=spec.job_id,
            stage_type=spec.stage_type,
            status="success" if terminal_error is None else "failed",
            worker_boot_id=context.worker_boot_id,
            fluent_generation=context.fluent_generation,
            fluent_pid=context.fluent_pid,
            fluent_version=fluent_version,
            pyfluent_version=pyfluent_version,
            started_at=(
                state["started_at"] if state is not None else attempt_started_at
            ),
            completed_at=self._timestamp_factory(),
            observed_health_result=health_result,
            client_detached=detached,
            fluent_process_alive_after_detach=alive_after_detach,
            requested_case_path=spec.case_path,
            resolved_case_path=(
                state.get("resolved_case_path") if state is not None else None
            ),
            disposable_case_path=(
                state.get("disposable_case_path") if state is not None else None
            ),
            source_file_size_bytes=(
                state.get("source_file_size_bytes")
                if state is not None
                else None
            ),
            source_sha256=(
                state.get("source_sha256") if state is not None else None
            ),
            run_state_path=(
                str(state_store.path.resolve())
                if state is not None
                else None
            ),
            requested_iterations=spec.total_iterations,
            completed_iterations=(
                state.get("completed_iterations") if state is not None else None
            ),
            checkpoint_case_path=(
                checkpoint.get("case_path") if checkpoint is not None else None
            ),
            checkpoint_data_path=(
                checkpoint.get("data_path") if checkpoint is not None else None
            ),
            initialization_count=(
                state.get("initialization_count") if state is not None else None
            ),
            resume_count=(
                state.get("resume_count") if state is not None else None
            ),
            generation_history=generation_history,
            error=terminal_error,
        )

    def _write_and_commit_checkpoint(
        self,
        spec: JobSpec,
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
            f"checkpoint-{iteration:08d}-"
            f"generation-{context.fluent_generation:03d}-"
            f"attempt-{attempt_index:03d}"
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
            f"verify-checkpoint-{iteration}",
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
        }
        state["updated_at"] = self._timestamp_factory()
        state_store.commit(state, spec=spec)

    def _receipt_from_completed_state(
        self,
        spec: JobSpec,
        context: HealthStageContext,
        state: dict[str, Any],
        state_path: Path,
    ) -> StageReceipt:
        """Recreate a success receipt after a prior receipt-commit failure."""

        checkpoint = state["last_checkpoint"]
        generations = tuple(
            int(attempt["fluent_generation"]) for attempt in state["attempts"]
        )
        return StageReceipt(
            job_id=spec.job_id,
            stage_type=spec.stage_type,
            status="success",
            worker_boot_id=context.worker_boot_id,
            fluent_generation=context.fluent_generation,
            fluent_pid=context.fluent_pid,
            fluent_version=str(state.get("fluent_version") or "recorded"),
            pyfluent_version=str(state.get("pyfluent_version") or "recorded"),
            started_at=state["started_at"],
            completed_at=self._timestamp_factory(),
            observed_health_result=True,
            client_detached=True,
            fluent_process_alive_after_detach=context.process_is_alive(),
            requested_case_path=state["requested_case_path"],
            resolved_case_path=state["resolved_case_path"],
            disposable_case_path=state["disposable_case_path"],
            source_file_size_bytes=state["source_file_size_bytes"],
            source_sha256=state.get("source_sha256"),
            run_state_path=str(state_path.resolve()),
            requested_iterations=state["total_iterations"],
            completed_iterations=state["completed_iterations"],
            checkpoint_case_path=checkpoint["case_path"],
            checkpoint_data_path=checkpoint["data_path"],
            initialization_count=state["initialization_count"],
            resume_count=state["resume_count"],
            generation_history=generations,
        )
