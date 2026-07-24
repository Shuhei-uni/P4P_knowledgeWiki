"""Filesystem-backed jobs and stage receipts for the Fluent host worker.

The protocol supports two read-only stages: ``health_check`` and
``case_identity_probe``. Job files are claimed with an atomic rename, stage
receipts are committed atomically, and a successful job is moved to
``completed`` only after its receipt has been validated and committed.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .host_worker import (
    HostWorkerConfig,
    call_with_timeout,
    close_session_best_effort,
    connect_from_server_info,
    session_is_active,
)


JOB_SCHEMA_VERSION = 2
JOB_STATE_SCHEMA_VERSION = 1
STAGE_RECEIPT_SCHEMA_VERSION = 2
SUPPORTED_STAGE_TYPES = frozenset({"health_check", "case_identity_probe"})
SUPPORTED_CASE_EXTENSIONS = (".cas.h5", ".cas.gz", ".cas")
JOB_STATUSES = frozenset({"incoming", "running", "completed", "failed"})
RECEIPT_STATUSES = frozenset({"success", "failed"})
_JOB_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ProtocolValidationError(ValueError):
    """Raised when a job, state, or receipt violates the protocol schema."""


class ReceiptCommitError(RuntimeError):
    """Raised when a valid receipt cannot be committed atomically."""


def utc_timestamp() -> str:
    """Return a stable, timezone-aware UTC timestamp."""

    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _validate_timestamp(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProtocolValidationError(f"{field_name} must be a non-empty string")
    normalized = value.strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProtocolValidationError(
            f"{field_name} must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None:
        raise ProtocolValidationError(f"{field_name} must include a timezone")
    return normalized


def _validate_job_id(value: Any) -> str:
    if not isinstance(value, str) or not _JOB_ID_PATTERN.fullmatch(value):
        raise ProtocolValidationError(
            "job_id must contain 1-128 letters, digits, dots, underscores, or hyphens"
        )
    if value in {".", ".."}:
        raise ProtocolValidationError("job_id cannot be '.' or '..'")
    return value


def _validate_schema_version(value: Any, expected: int, model_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProtocolValidationError(f"{model_name}.schema_version must be an integer")
    if value != expected:
        raise ProtocolValidationError(
            f"Unsupported {model_name} schema_version {value}; expected {expected}"
        )
    return value


def _validate_optional_positive_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ProtocolValidationError(f"{field_name} must be a positive integer")
    return value


def _validate_positive_int(value: Any, field_name: str) -> int:
    validated = _validate_optional_positive_int(value, field_name)
    if validated is None:
        raise ProtocolValidationError(f"{field_name} must be a positive integer")
    return validated


def _reject_unknown_fields(
    payload: Mapping[str, Any],
    allowed: set[str],
    model_name: str,
) -> None:
    unknown = set(payload) - allowed
    if unknown:
        raise ProtocolValidationError(
            f"{model_name} contains unknown fields: {sorted(unknown)}"
        )


def _validate_error(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ProtocolValidationError("error must be an object or null")
    error_type = value.get("type")
    message = value.get("message")
    retryable = value.get("retryable")
    if not isinstance(error_type, str) or not error_type.strip():
        raise ProtocolValidationError("error.type must be a non-empty string")
    if not isinstance(message, str) or not message.strip():
        raise ProtocolValidationError("error.message must be a non-empty string")
    if not isinstance(retryable, bool):
        raise ProtocolValidationError("error.retryable must be a boolean")
    return {
        "type": error_type.strip(),
        "message": message.strip(),
        "retryable": retryable,
    }


def structured_error(exc: BaseException, *, retryable: bool) -> dict[str, Any]:
    """Convert an exception into the protocol's non-traceback error shape."""

    return {
        "type": type(exc).__name__,
        "message": str(exc) or type(exc).__name__,
        "retryable": retryable,
    }


@dataclass(frozen=True)
class JobSpec:
    """Versioned request for one host-worker stage."""

    job_id: str
    stage_type: str = "health_check"
    submitted_at: str = field(default_factory=utc_timestamp)
    timeout_seconds: float = 30.0
    expected_worker_boot_id: str | None = None
    expected_fluent_generation: int | None = None
    case_path: str | None = None
    expected_file_size_bytes: int | None = None
    expected_sha256: str | None = None
    compute_sha256: bool = False
    schema_version: int = JOB_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if isinstance(self.expected_sha256, str):
            object.__setattr__(self, "expected_sha256", self.expected_sha256.lower())

    def validate(self) -> None:
        _validate_schema_version(self.schema_version, JOB_SCHEMA_VERSION, "JobSpec")
        _validate_job_id(self.job_id)
        if self.stage_type not in SUPPORTED_STAGE_TYPES:
            raise ProtocolValidationError(
                f"Unsupported stage_type {self.stage_type!r}; "
                f"supported values: {sorted(SUPPORTED_STAGE_TYPES)}"
            )
        _validate_timestamp(self.submitted_at, "submitted_at")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not 0 < float(self.timeout_seconds) <= 3600
        ):
            raise ProtocolValidationError(
                "timeout_seconds must be greater than 0 and at most 3600"
            )
        if self.expected_worker_boot_id is not None:
            if (
                not isinstance(self.expected_worker_boot_id, str)
                or not self.expected_worker_boot_id.strip()
            ):
                raise ProtocolValidationError(
                    "expected_worker_boot_id must be a non-empty string or null"
                )
        _validate_optional_positive_int(
            self.expected_fluent_generation,
            "expected_fluent_generation",
        )
        if self.case_path is not None and (
            not isinstance(self.case_path, str) or not self.case_path.strip()
        ):
            raise ProtocolValidationError("case_path must be a non-empty string or null")
        _validate_optional_positive_int(
            self.expected_file_size_bytes,
            "expected_file_size_bytes",
        )
        if self.expected_sha256 is not None:
            if (
                not isinstance(self.expected_sha256, str)
                or not re.fullmatch(r"[0-9a-fA-F]{64}", self.expected_sha256)
            ):
                raise ProtocolValidationError(
                    "expected_sha256 must contain exactly 64 hexadecimal characters"
                )
        if not isinstance(self.compute_sha256, bool):
            raise ProtocolValidationError("compute_sha256 must be a boolean")

        if self.stage_type == "health_check":
            if any(
                value is not None
                for value in (
                    self.case_path,
                    self.expected_file_size_bytes,
                    self.expected_sha256,
                )
            ) or self.compute_sha256:
                raise ProtocolValidationError(
                    "health_check jobs cannot contain case input fields"
                )
        elif self.stage_type == "case_identity_probe":
            if self.case_path is None:
                raise ProtocolValidationError(
                    "case_identity_probe requires case_path"
                )
            case_path = Path(self.case_path)
            if not case_path.is_absolute():
                raise ProtocolValidationError(
                    "case_identity_probe case_path must be absolute"
                )
            if not self.case_path.lower().endswith(SUPPORTED_CASE_EXTENSIONS):
                raise ProtocolValidationError(
                    "case_identity_probe case_path must end with one of "
                    f"{SUPPORTED_CASE_EXTENSIONS}"
                )
            if self.expected_worker_boot_id is None:
                raise ProtocolValidationError(
                    "case_identity_probe requires expected_worker_boot_id"
                )
            if self.expected_fluent_generation is None:
                raise ProtocolValidationError(
                    "case_identity_probe requires expected_fluent_generation"
                )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "job_id": self.job_id,
            "stage_type": self.stage_type,
            "submitted_at": self.submitted_at,
            "timeout_seconds": float(self.timeout_seconds),
            "expected_worker_boot_id": self.expected_worker_boot_id,
            "expected_fluent_generation": self.expected_fluent_generation,
            "case_path": self.case_path,
            "expected_file_size_bytes": self.expected_file_size_bytes,
            "expected_sha256": (
                self.expected_sha256.lower()
                if self.expected_sha256 is not None
                else None
            ),
            "compute_sha256": self.compute_sha256,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "JobSpec":
        if not isinstance(payload, Mapping):
            raise ProtocolValidationError("JobSpec document must be an object")
        allowed = {
            "schema_version",
            "job_id",
            "stage_type",
            "submitted_at",
            "timeout_seconds",
            "expected_worker_boot_id",
            "expected_fluent_generation",
            "case_path",
            "expected_file_size_bytes",
            "expected_sha256",
            "compute_sha256",
        }
        _reject_unknown_fields(payload, allowed, "JobSpec")
        try:
            spec = cls(
                schema_version=payload["schema_version"],
                job_id=payload["job_id"],
                stage_type=payload["stage_type"],
                submitted_at=payload["submitted_at"],
                timeout_seconds=payload.get("timeout_seconds", 30.0),
                expected_worker_boot_id=payload.get("expected_worker_boot_id"),
                expected_fluent_generation=payload.get(
                    "expected_fluent_generation"
                ),
                case_path=payload.get("case_path"),
                expected_file_size_bytes=payload.get(
                    "expected_file_size_bytes"
                ),
                expected_sha256=payload.get("expected_sha256"),
                compute_sha256=payload.get("compute_sha256", False),
            )
        except KeyError as exc:
            raise ProtocolValidationError(
                f"JobSpec is missing required field: {exc.args[0]}"
            ) from exc
        spec.validate()
        return spec


@dataclass(frozen=True)
class JobState:
    """Versioned state recorded when a claimed job reaches a terminal queue."""

    job_id: str
    status: str
    updated_at: str
    worker_boot_id: str | None = None
    fluent_generation: int | None = None
    fluent_pid: int | None = None
    receipt_path: str | None = None
    error: dict[str, Any] | None = None
    schema_version: int = JOB_STATE_SCHEMA_VERSION

    def validate(self) -> None:
        _validate_schema_version(
            self.schema_version,
            JOB_STATE_SCHEMA_VERSION,
            "JobState",
        )
        _validate_job_id(self.job_id)
        if self.status not in JOB_STATUSES:
            raise ProtocolValidationError(
                f"Unsupported job status {self.status!r}; "
                f"supported values: {sorted(JOB_STATUSES)}"
            )
        _validate_timestamp(self.updated_at, "updated_at")
        if self.worker_boot_id is not None and (
            not isinstance(self.worker_boot_id, str)
            or not self.worker_boot_id.strip()
        ):
            raise ProtocolValidationError(
                "worker_boot_id must be a non-empty string or null"
            )
        _validate_optional_positive_int(self.fluent_generation, "fluent_generation")
        _validate_optional_positive_int(self.fluent_pid, "fluent_pid")
        if self.receipt_path is not None and (
            not isinstance(self.receipt_path, str) or not self.receipt_path.strip()
        ):
            raise ProtocolValidationError(
                "receipt_path must be a non-empty string or null"
            )
        validated_error = _validate_error(self.error)
        if self.status == "completed" and validated_error is not None:
            raise ProtocolValidationError("completed JobState cannot contain an error")
        if self.status == "failed" and validated_error is None:
            raise ProtocolValidationError("failed JobState requires an error")
        if self.status in {"completed", "failed"} and not self.receipt_path:
            raise ProtocolValidationError(
                f"{self.status} JobState requires receipt_path"
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "job_id": self.job_id,
            "status": self.status,
            "updated_at": self.updated_at,
            "worker_boot_id": self.worker_boot_id,
            "fluent_generation": self.fluent_generation,
            "fluent_pid": self.fluent_pid,
            "receipt_path": self.receipt_path,
            "error": _validate_error(self.error),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "JobState":
        if not isinstance(payload, Mapping):
            raise ProtocolValidationError("JobState document must be an object")
        _reject_unknown_fields(
            payload,
            {
                "schema_version",
                "job_id",
                "status",
                "updated_at",
                "worker_boot_id",
                "fluent_generation",
                "fluent_pid",
                "receipt_path",
                "error",
            },
            "JobState",
        )
        try:
            state = cls(
                schema_version=payload["schema_version"],
                job_id=payload["job_id"],
                status=payload["status"],
                updated_at=payload["updated_at"],
                worker_boot_id=payload.get("worker_boot_id"),
                fluent_generation=payload.get("fluent_generation"),
                fluent_pid=payload.get("fluent_pid"),
                receipt_path=payload.get("receipt_path"),
                error=payload.get("error"),
            )
        except KeyError as exc:
            raise ProtocolValidationError(
                f"JobState is missing required field: {exc.args[0]}"
            ) from exc
        state.validate()
        return state


@dataclass(frozen=True)
class StageReceipt:
    """Durable evidence for one attempted stage."""

    job_id: str
    stage_type: str
    status: str
    worker_boot_id: str
    fluent_generation: int
    fluent_pid: int
    fluent_version: str | None
    pyfluent_version: str | None
    started_at: str
    completed_at: str
    observed_health_result: bool | None
    client_detached: bool
    fluent_process_alive_after_detach: bool
    requested_case_path: str | None = None
    resolved_case_path: str | None = None
    disposable_case_path: str | None = None
    source_file_size_bytes: int | None = None
    source_sha256: str | None = None
    fluent_accepted_case: bool | None = None
    case_identity: dict[str, Any] | None = None
    data_loaded: bool | None = None
    error: dict[str, Any] | None = None
    schema_version: int = STAGE_RECEIPT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if isinstance(self.source_sha256, str):
            object.__setattr__(self, "source_sha256", self.source_sha256.lower())

    def validate(self) -> None:
        _validate_schema_version(
            self.schema_version,
            STAGE_RECEIPT_SCHEMA_VERSION,
            "StageReceipt",
        )
        _validate_job_id(self.job_id)
        if not isinstance(self.stage_type, str) or not self.stage_type.strip():
            raise ProtocolValidationError("stage_type must be a non-empty string")
        if self.status not in RECEIPT_STATUSES:
            raise ProtocolValidationError(
                f"Unsupported receipt status {self.status!r}; "
                f"supported values: {sorted(RECEIPT_STATUSES)}"
            )
        if not isinstance(self.worker_boot_id, str) or not self.worker_boot_id.strip():
            raise ProtocolValidationError("worker_boot_id must be a non-empty string")
        _validate_positive_int(self.fluent_generation, "fluent_generation")
        _validate_positive_int(self.fluent_pid, "fluent_pid")
        started = _validate_timestamp(self.started_at, "started_at")
        completed = _validate_timestamp(self.completed_at, "completed_at")
        if datetime.fromisoformat(completed.replace("Z", "+00:00")) < datetime.fromisoformat(
            started.replace("Z", "+00:00")
        ):
            raise ProtocolValidationError("completed_at cannot precede started_at")
        if self.observed_health_result is not None and not isinstance(
            self.observed_health_result, bool
        ):
            raise ProtocolValidationError(
                "observed_health_result must be a boolean or null"
            )
        if not isinstance(self.client_detached, bool):
            raise ProtocolValidationError("client_detached must be a boolean")
        if not isinstance(self.fluent_process_alive_after_detach, bool):
            raise ProtocolValidationError(
                "fluent_process_alive_after_detach must be a boolean"
            )
        for value, field_name in (
            (self.requested_case_path, "requested_case_path"),
            (self.resolved_case_path, "resolved_case_path"),
            (self.disposable_case_path, "disposable_case_path"),
        ):
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ProtocolValidationError(
                    f"{field_name} must be a non-empty string or null"
                )
        _validate_optional_positive_int(
            self.source_file_size_bytes,
            "source_file_size_bytes",
        )
        if self.source_sha256 is not None and (
            not isinstance(self.source_sha256, str)
            or not re.fullmatch(r"[0-9a-fA-F]{64}", self.source_sha256)
        ):
            raise ProtocolValidationError(
                "source_sha256 must contain exactly 64 hexadecimal characters"
            )
        if self.fluent_accepted_case is not None and not isinstance(
            self.fluent_accepted_case,
            bool,
        ):
            raise ProtocolValidationError(
                "fluent_accepted_case must be a boolean or null"
            )
        if self.case_identity is not None and not isinstance(
            self.case_identity,
            Mapping,
        ):
            raise ProtocolValidationError("case_identity must be an object or null")
        if self.data_loaded is not None and not isinstance(self.data_loaded, bool):
            raise ProtocolValidationError("data_loaded must be a boolean or null")
        validated_error = _validate_error(self.error)
        if self.status == "success":
            if validated_error is not None:
                raise ProtocolValidationError("successful receipt cannot contain error")
            if self.observed_health_result is not True:
                raise ProtocolValidationError(
                    "successful receipt requires observed_health_result=true"
                )
            if not self.client_detached:
                raise ProtocolValidationError(
                    "successful receipt requires client_detached=true"
                )
            if not self.fluent_process_alive_after_detach:
                raise ProtocolValidationError(
                    "successful receipt requires Fluent to remain alive after detach"
                )
            if not self.fluent_version or not self.pyfluent_version:
                raise ProtocolValidationError(
                    "successful receipt requires Fluent and PyFluent versions"
                )
            if self.stage_type == "case_identity_probe":
                if self.fluent_accepted_case is not True:
                    raise ProtocolValidationError(
                        "successful case probe requires fluent_accepted_case=true"
                    )
                if self.data_loaded is not False:
                    raise ProtocolValidationError(
                        "successful case probe requires data_loaded=false"
                    )
                if not all(
                    (
                        self.requested_case_path,
                        self.resolved_case_path,
                        self.disposable_case_path,
                    )
                ):
                    raise ProtocolValidationError(
                        "successful case probe requires all case paths"
                    )
                case_paths = (
                    Path(self.requested_case_path),
                    Path(self.resolved_case_path),
                    Path(self.disposable_case_path),
                )
                if not all(path.is_absolute() for path in case_paths):
                    raise ProtocolValidationError(
                        "successful case probe requires absolute case paths"
                    )
                if case_paths[1] == case_paths[2]:
                    raise ProtocolValidationError(
                        "disposable_case_path must differ from resolved_case_path"
                    )
                if self.source_file_size_bytes is None:
                    raise ProtocolValidationError(
                        "successful case probe requires source_file_size_bytes"
                    )
                if self.case_identity is None:
                    raise ProtocolValidationError(
                        "successful case probe requires case_identity"
                    )
        elif validated_error is None:
            raise ProtocolValidationError("failed receipt requires structured error")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "job_id": self.job_id,
            "stage_type": self.stage_type,
            "status": self.status,
            "worker_boot_id": self.worker_boot_id,
            "fluent_generation": self.fluent_generation,
            "fluent_pid": self.fluent_pid,
            "fluent_version": self.fluent_version,
            "pyfluent_version": self.pyfluent_version,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "observed_health_result": self.observed_health_result,
            "client_detached": self.client_detached,
            "fluent_process_alive_after_detach": (
                self.fluent_process_alive_after_detach
            ),
            "requested_case_path": self.requested_case_path,
            "resolved_case_path": self.resolved_case_path,
            "disposable_case_path": self.disposable_case_path,
            "source_file_size_bytes": self.source_file_size_bytes,
            "source_sha256": (
                self.source_sha256.lower()
                if self.source_sha256 is not None
                else None
            ),
            "fluent_accepted_case": self.fluent_accepted_case,
            "case_identity": (
                dict(self.case_identity)
                if self.case_identity is not None
                else None
            ),
            "data_loaded": self.data_loaded,
            "error": _validate_error(self.error),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "StageReceipt":
        if not isinstance(payload, Mapping):
            raise ProtocolValidationError("StageReceipt document must be an object")
        _reject_unknown_fields(
            payload,
            {
                "schema_version",
                "job_id",
                "stage_type",
                "status",
                "worker_boot_id",
                "fluent_generation",
                "fluent_pid",
                "fluent_version",
                "pyfluent_version",
                "started_at",
                "completed_at",
                "observed_health_result",
                "client_detached",
                "fluent_process_alive_after_detach",
                "requested_case_path",
                "resolved_case_path",
                "disposable_case_path",
                "source_file_size_bytes",
                "source_sha256",
                "fluent_accepted_case",
                "case_identity",
                "data_loaded",
                "error",
            },
            "StageReceipt",
        )
        try:
            receipt = cls(
                schema_version=payload["schema_version"],
                job_id=payload["job_id"],
                stage_type=payload["stage_type"],
                status=payload["status"],
                worker_boot_id=payload["worker_boot_id"],
                fluent_generation=payload["fluent_generation"],
                fluent_pid=payload["fluent_pid"],
                fluent_version=payload.get("fluent_version"),
                pyfluent_version=payload.get("pyfluent_version"),
                started_at=payload["started_at"],
                completed_at=payload["completed_at"],
                observed_health_result=payload.get("observed_health_result"),
                client_detached=payload["client_detached"],
                fluent_process_alive_after_detach=payload[
                    "fluent_process_alive_after_detach"
                ],
                requested_case_path=payload.get("requested_case_path"),
                resolved_case_path=payload.get("resolved_case_path"),
                disposable_case_path=payload.get("disposable_case_path"),
                source_file_size_bytes=payload.get("source_file_size_bytes"),
                source_sha256=payload.get("source_sha256"),
                fluent_accepted_case=payload.get("fluent_accepted_case"),
                case_identity=payload.get("case_identity"),
                data_loaded=payload.get("data_loaded"),
                error=payload.get("error"),
            )
        except KeyError as exc:
            raise ProtocolValidationError(
                f"StageReceipt is missing required field: {exc.args[0]}"
            ) from exc
        receipt.validate()
        return receipt


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


@dataclass(frozen=True)
class ClaimedJob:
    """One atomically claimed file, valid or malformed."""

    path: Path
    original_name: str
    spec: JobSpec | None
    validation_error: dict[str, Any] | None = None


class FilesystemJobSpool:
    """Local filesystem queues and receipt storage below a worker runtime."""

    def __init__(self, runtime_dir: Path):
        self.runtime_dir = Path(runtime_dir)
        self.jobs_dir = self.runtime_dir / "jobs"
        self.incoming_dir = self.jobs_dir / "incoming"
        self.running_dir = self.jobs_dir / "running"
        self.completed_dir = self.jobs_dir / "completed"
        self.failed_dir = self.jobs_dir / "failed"
        self.receipts_dir = self.runtime_dir / "receipts"

    def ensure_layout(self) -> None:
        for directory in (
            self.incoming_dir,
            self.running_dir,
            self.completed_dir,
            self.failed_dir,
            self.receipts_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def submit(self, spec: JobSpec) -> Path:
        """Atomically publish a new job into ``jobs/incoming``."""

        spec.validate()
        self.ensure_layout()
        path = self.incoming_dir / f"{spec.job_id}.json"
        if path.exists():
            raise FileExistsError(f"Incoming job already exists: {spec.job_id}")
        _atomic_write_json(path, spec.to_dict())
        return path

    def claim_next(self, worker_boot_id: str) -> ClaimedJob | None:
        """Claim one incoming file with a same-volume atomic replacement."""

        if not worker_boot_id.strip():
            raise ValueError("worker_boot_id must be non-empty")
        self.ensure_layout()
        for source in sorted(self.incoming_dir.glob("*.json")):
            claim_token = uuid.uuid4().hex
            destination = self.running_dir / (
                f"{source.stem}.{worker_boot_id}.{claim_token}.json"
            )
            try:
                os.replace(source, destination)
            except FileNotFoundError:
                continue
            except OSError:
                if not source.exists():
                    continue
                raise

            try:
                payload = json.loads(destination.read_text(encoding="utf-8"))
                spec = JobSpec.from_dict(payload)
            except Exception as exc:
                return ClaimedJob(
                    path=destination,
                    original_name=source.name,
                    spec=None,
                    validation_error=structured_error(exc, retryable=False),
                )
            return ClaimedJob(
                path=destination,
                original_name=source.name,
                spec=spec,
            )
        return None

    def commit_receipt(self, receipt: StageReceipt) -> Path:
        """Validate and atomically commit a receipt before any terminal move."""

        receipt.validate()
        self.ensure_layout()
        path = self.receipts_dir / f"{receipt.job_id}.json"
        try:
            _atomic_write_json(path, receipt.to_dict())
            committed = StageReceipt.from_dict(
                json.loads(path.read_text(encoding="utf-8"))
            )
        except Exception as exc:
            raise ReceiptCommitError(
                f"Could not commit valid receipt for {receipt.job_id}: {exc}"
            ) from exc
        if committed != receipt:
            raise ReceiptCommitError(
                f"Committed receipt readback differs for {receipt.job_id}"
            )
        return path

    def finish(
        self,
        claim: ClaimedJob,
        *,
        spec: JobSpec,
        state: JobState,
        receipt_path: Path,
    ) -> Path:
        """Move a job to its terminal queue only after receipt verification."""

        spec.validate()
        state.validate()
        if state.job_id != spec.job_id:
            raise ProtocolValidationError("JobState job_id does not match JobSpec")
        if not receipt_path.is_file():
            raise ReceiptCommitError(
                f"Cannot finish {spec.job_id}: receipt does not exist"
            )
        receipt = StageReceipt.from_dict(
            json.loads(receipt_path.read_text(encoding="utf-8"))
        )
        if receipt.job_id != spec.job_id:
            raise ReceiptCommitError(
                f"Cannot finish {spec.job_id}: receipt belongs to {receipt.job_id}"
            )
        expected_status = "completed" if receipt.status == "success" else "failed"
        if state.status != expected_status:
            raise ProtocolValidationError(
                f"JobState status {state.status!r} conflicts with receipt "
                f"status {receipt.status!r}"
            )

        record = {
            "schema_version": JOB_SCHEMA_VERSION,
            "job": spec.to_dict(),
            "state": state.to_dict(),
        }
        _atomic_write_json(claim.path, record)
        destination_dir = (
            self.completed_dir if state.status == "completed" else self.failed_dir
        )
        destination = destination_dir / claim.original_name
        os.replace(claim.path, destination)
        return destination


@dataclass(frozen=True)
class HealthStageContext:
    """Immutable identity of the worker-owned Fluent generation."""

    worker_boot_id: str
    fluent_generation: int
    fluent_pid: int
    server_info_path: Path
    config: HostWorkerConfig
    process_is_alive: Callable[[], bool]


class HealthCheckStageClient:
    """Short-lived cleanup-disabled client for a read-only health stage."""

    def __init__(
        self,
        *,
        connect_factory: Callable[
            [Path, HostWorkerConfig], Any
        ] = connect_from_server_info,
        pyfluent_version_factory: Callable[[], str] | None = None,
        monotonic: Callable[[], float] = time.monotonic,
        timestamp_factory: Callable[[], str] = utc_timestamp,
    ):
        self.connect_factory = connect_factory
        self.pyfluent_version_factory = (
            pyfluent_version_factory or self._installed_pyfluent_version
        )
        self._monotonic = monotonic
        self._timestamp_factory = timestamp_factory

    @staticmethod
    def _installed_pyfluent_version() -> str:
        import ansys.fluent.core as pyfluent

        return str(pyfluent.__version__)

    def execute(
        self,
        spec: JobSpec,
        context: HealthStageContext,
    ) -> StageReceipt:
        spec.validate()
        started_at = self._timestamp_factory()
        deadline = self._monotonic() + float(spec.timeout_seconds)
        session: Any | None = None
        fluent_version: str | None = None
        pyfluent_version: str | None = None
        health_result: bool | None = None
        detached = False
        error: dict[str, Any] | None = None

        def remaining(label: str) -> float:
            value = deadline - self._monotonic()
            if value <= 0:
                raise TimeoutError(
                    f"health_check timed out before {label} completed"
                )
            return value

        try:
            if (
                spec.expected_worker_boot_id is not None
                and spec.expected_worker_boot_id != context.worker_boot_id
            ):
                raise RuntimeError(
                    "Worker boot mismatch: expected "
                    f"{spec.expected_worker_boot_id}, observed "
                    f"{context.worker_boot_id}"
                )
            if (
                spec.expected_fluent_generation is not None
                and spec.expected_fluent_generation != context.fluent_generation
            ):
                raise RuntimeError(
                    "Fluent generation mismatch: expected "
                    f"{spec.expected_fluent_generation}, observed "
                    f"{context.fluent_generation}"
                )
            if not context.process_is_alive():
                raise RuntimeError(
                    f"Fluent generation {context.fluent_generation} is not alive"
                )

            pyfluent_version = str(
                call_with_timeout(
                    self.pyfluent_version_factory,
                    remaining("PyFluent version read"),
                    label="stage-pyfluent-version",
                )
            )
            session = call_with_timeout(
                lambda: self.connect_factory(
                    context.server_info_path,
                    context.config,
                ),
                remaining("stage connection"),
                label="stage-connect",
                late_result_cleanup=lambda late_session: close_session_best_effort(
                    late_session,
                    timeout_seconds=context.config.health_timeout_seconds,
                ),
            )
            health_result = bool(
                call_with_timeout(
                    lambda: session_is_active(session),
                    remaining("stage health check"),
                    label="stage-health",
                )
            )
            if not health_result:
                raise RuntimeError("Stage client connected but gRPC health is inactive")

            get_version = getattr(session, "get_fluent_version", None)
            if not callable(get_version):
                raise AttributeError("Stage session does not expose get_fluent_version()")
            fluent_version = str(
                call_with_timeout(
                    get_version,
                    remaining("Fluent version read"),
                    label="stage-fluent-version",
                )
            )
        except Exception as exc:
            retryable = isinstance(exc, (TimeoutError, ConnectionError, RuntimeError))
            error = structured_error(exc, retryable=retryable)
        finally:
            if session is not None:
                detached = close_session_best_effort(
                    session,
                    timeout_seconds=min(
                        context.config.health_timeout_seconds,
                        max(0.1, float(spec.timeout_seconds)),
                    ),
                )

        alive_after_detach = context.process_is_alive()
        if error is None and not detached:
            error = structured_error(
                RuntimeError("Stage client could not detach cleanly"),
                retryable=True,
            )
        if error is None and not alive_after_detach:
            error = structured_error(
                RuntimeError("Fluent process terminated during stage detachment"),
                retryable=True,
            )

        return StageReceipt(
            job_id=spec.job_id,
            stage_type=spec.stage_type,
            status="success" if error is None else "failed",
            worker_boot_id=context.worker_boot_id,
            fluent_generation=context.fluent_generation,
            fluent_pid=context.fluent_pid,
            fluent_version=fluent_version,
            pyfluent_version=pyfluent_version,
            started_at=started_at,
            completed_at=self._timestamp_factory(),
            observed_health_result=health_result,
            client_detached=detached,
            fluent_process_alive_after_detach=alive_after_detach,
            error=error,
        )


class JobStageProcessor:
    """Claim and execute at most one stage during a worker polling cycle."""

    def __init__(
        self,
        spool: FilesystemJobSpool,
        *,
        health_client: HealthCheckStageClient | None = None,
        case_probe_client: Any | None = None,
        timestamp_factory: Callable[[], str] = utc_timestamp,
    ):
        self.spool = spool
        self.health_client = health_client or HealthCheckStageClient()
        if case_probe_client is None:
            from .case_probe import CaseIdentityProbeClient

            case_probe_client = CaseIdentityProbeClient()
        self.case_probe_client = case_probe_client
        self._timestamp_factory = timestamp_factory

    @staticmethod
    def _malformed_job_id(claim: ClaimedJob) -> str:
        stem = Path(claim.original_name).stem
        if _JOB_ID_PATTERN.fullmatch(stem) and stem not in {".", ".."}:
            return stem
        return f"invalid-{uuid.uuid4().hex}"

    def process_next(self, context: HealthStageContext) -> JobState | None:
        claim = self.spool.claim_next(context.worker_boot_id)
        if claim is None:
            return None

        if claim.spec is None:
            job_id = self._malformed_job_id(claim)
            spec = JobSpec(job_id=job_id)
            receipt = StageReceipt(
                job_id=job_id,
                stage_type="invalid",
                status="failed",
                worker_boot_id=context.worker_boot_id,
                fluent_generation=context.fluent_generation,
                fluent_pid=context.fluent_pid,
                fluent_version=None,
                pyfluent_version=None,
                started_at=self._timestamp_factory(),
                completed_at=self._timestamp_factory(),
                observed_health_result=None,
                client_detached=True,
                fluent_process_alive_after_detach=context.process_is_alive(),
                error=claim.validation_error
                or {
                    "type": "ProtocolValidationError",
                    "message": "Malformed job",
                    "retryable": False,
                },
            )
        elif claim.spec.stage_type == "health_check":
            spec = claim.spec
            receipt = self.health_client.execute(spec, context)
        elif claim.spec.stage_type == "case_identity_probe":
            spec = claim.spec
            receipt = self.case_probe_client.execute(spec, context)
        else:
            raise ProtocolValidationError(
                f"No stage client for {claim.spec.stage_type!r}"
            )

        receipt_path = self.spool.commit_receipt(receipt)
        terminal_status = "completed" if receipt.status == "success" else "failed"
        state = JobState(
            job_id=spec.job_id,
            status=terminal_status,
            updated_at=self._timestamp_factory(),
            worker_boot_id=context.worker_boot_id,
            fluent_generation=context.fluent_generation,
            fluent_pid=context.fluent_pid,
            receipt_path=str(receipt_path),
            error=receipt.error,
        )
        self.spool.finish(
            claim,
            spec=spec,
            state=state,
            receipt_path=receipt_path,
        )
        return state
