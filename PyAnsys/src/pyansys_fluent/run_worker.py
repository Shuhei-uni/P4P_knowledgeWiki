"""Narrow Fluent-PC run worker controlled by laptop-authored request files.

The worker is intentionally not a general Fluent job dispatcher.  It accepts
only one operation: load an explicit case (and, for resume, data), run to an
absolute iteration target, write recovery checkpoints, and preserve the final
data artifact.  It retains only the newest verified checkpoint pair and its
immediate predecessor during a run; after completion it retains the final pair
and the newest recovery pair.  It never launches or restarts Fluent and never
selects a resume checkpoint for the controller.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, Callable, Mapping

from pyansys_fluent.bridge import (
    ConnectionDocumentError,
    read_latest_connection,
)
from pyansys_fluent.common import bool_env


RUN_REQUEST_SCHEMA_VERSION = 1
RUN_RECEIPT_SCHEMA_VERSION = 1
_JOB_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_WORKER_CHECKPOINT = re.compile(
    r"^(?P<job>.+)-checkpoint-(?P<iteration>\d+)\.cas\.h5$",
    re.IGNORECASE,
)
_REQUEST_FIELDS = {
    "schema_version",
    "job_id",
    "expected_generation",
    "mode",
    "source_case",
    "source_data",
    "target_total_iterations",
    "completed_iterations",
    "checkpoint_interval",
    "report_interval",
    "output_directory",
    "overwrite",
}


class RunRequestError(ValueError):
    """Raised when a run request violates the narrow worker contract."""


class GenerationChanged(ConnectionError):
    """Raised when the worker's pinned Fluent generation is no longer active."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(
            json.dumps(dict(payload), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _absolute_path(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RunRequestError(f"{field} must be a non-empty absolute path")
    text = value.strip()
    if not (Path(text).is_absolute() or PureWindowsPath(text).is_absolute()):
        raise RunRequestError(f"{field} must be an absolute path")
    return text


def _integer(value: Any, field: str, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise RunRequestError(f"{field} must be an integer >= {minimum}")
    return value


@dataclass(frozen=True)
class RunRequest:
    job_id: str
    expected_generation: int
    mode: str
    source_case: str
    source_data: str | None
    target_total_iterations: int
    completed_iterations: int
    output_directory: str
    checkpoint_interval: int = 250
    report_interval: int = 25
    overwrite: bool = False
    schema_version: int = RUN_REQUEST_SCHEMA_VERSION

    @classmethod
    def from_dict(cls, payload: Any) -> "RunRequest":
        if not isinstance(payload, Mapping):
            raise RunRequestError("Run request must be a JSON object")
        unknown = set(payload) - _REQUEST_FIELDS
        if unknown:
            raise RunRequestError(f"Unknown run request fields: {sorted(unknown)}")
        if payload.get("schema_version") != RUN_REQUEST_SCHEMA_VERSION:
            raise RunRequestError(
                f"schema_version must be {RUN_REQUEST_SCHEMA_VERSION}"
            )
        job_id = payload.get("job_id")
        if not isinstance(job_id, str) or not _JOB_ID.fullmatch(job_id):
            raise RunRequestError("job_id contains unsupported characters")
        mode = payload.get("mode")
        if mode not in {"initialize", "resume"}:
            raise RunRequestError("mode must be 'initialize' or 'resume'")
        source_case = _absolute_path(payload.get("source_case"), "source_case")
        if not source_case.lower().endswith(".cas.h5"):
            raise RunRequestError("source_case must end with .cas.h5")
        source_data_value = payload.get("source_data")
        source_data: str | None
        if mode == "resume":
            source_data = _absolute_path(source_data_value, "source_data")
            if not source_data.lower().endswith(".dat.h5"):
                raise RunRequestError("source_data must end with .dat.h5")
        else:
            if source_data_value is not None:
                raise RunRequestError("initialize mode requires source_data=null")
            source_data = None
        target = _integer(
            payload.get("target_total_iterations"),
            "target_total_iterations",
            minimum=0,
        )
        completed = _integer(
            payload.get("completed_iterations"),
            "completed_iterations",
            minimum=0,
        )
        if completed > target:
            raise RunRequestError(
                "completed_iterations cannot exceed target_total_iterations"
            )
        if mode == "initialize" and completed != 0:
            raise RunRequestError(
                "initialize mode requires completed_iterations=0"
            )
        checkpoint_interval = _integer(
            payload.get("checkpoint_interval", 250),
            "checkpoint_interval",
            minimum=1,
        )
        report_interval = _integer(
            payload.get("report_interval", 25),
            "report_interval",
            minimum=1,
        )
        overwrite = payload.get("overwrite", False)
        if overwrite is not False:
            raise RunRequestError("overwrite must be false")
        request = cls(
            schema_version=RUN_REQUEST_SCHEMA_VERSION,
            job_id=job_id,
            expected_generation=_integer(
                payload.get("expected_generation"),
                "expected_generation",
                minimum=1,
            ),
            mode=mode,
            source_case=source_case,
            source_data=source_data,
            target_total_iterations=target,
            completed_iterations=completed,
            checkpoint_interval=checkpoint_interval,
            report_interval=report_interval,
            output_directory=_absolute_path(
                payload.get("output_directory"), "output_directory"
            ),
            overwrite=False,
        )
        return request

    @classmethod
    def from_path(cls, path: Path) -> "RunRequest":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "job_id": self.job_id,
            "expected_generation": self.expected_generation,
            "mode": self.mode,
            "source_case": self.source_case,
            "source_data": self.source_data,
            "target_total_iterations": self.target_total_iterations,
            "completed_iterations": self.completed_iterations,
            "checkpoint_interval": self.checkpoint_interval,
            "report_interval": self.report_interval,
            "output_directory": self.output_directory,
            "overwrite": self.overwrite,
        }


def _read_connection(path: Path, expected_generation: int) -> dict[str, Any]:
    try:
        payload = read_latest_connection(
            path,
            min_generation=expected_generation,
        )
    except (OSError, json.JSONDecodeError, ConnectionDocumentError) as exc:
        raise GenerationChanged(
            "No usable running Fluent generation is published"
        ) from exc
    if payload["generation"] != expected_generation:
        raise GenerationChanged(
            "Fluent generation changed from the request's expected generation"
        )
    return payload


def _source_stem(case_path: str) -> str:
    name = PureWindowsPath(case_path).name
    if name.lower().endswith(".cas.h5"):
        return name[:-7]
    return PureWindowsPath(case_path).stem


def _checkpoint_paths(
    request: RunRequest, iteration: int, *, final: bool
) -> tuple[Path, Path]:
    output = Path(request.output_directory)
    if final:
        stem = f"{_source_stem(request.source_case)}_{iteration}"
    else:
        stem = f"{request.job_id}-checkpoint-{iteration:08d}"
    return output / f"{stem}.cas.h5", output / f"{stem}.dat.h5"


def _prune_worker_checkpoints(
    output_directory: Path,
    job_id: str,
    *,
    keep_pairs: int,
) -> None:
    """Keep only the newest verified worker checkpoint pairs.

    The final case/data pair is stored under its canonical final name and is
    not part of this numbered recovery history.  Pruning is performed only
    after a new pair has passed file verification, so the previous usable
    pair remains available if Fluent dies while writing the new one.
    """

    if keep_pairs < 0:
        raise ValueError("keep_pairs must be non-negative")
    pairs: list[tuple[int, Path, Path]] = []
    for case_path in output_directory.glob(f"{job_id}-checkpoint-*.cas.h5"):
        match = _WORKER_CHECKPOINT.match(case_path.name)
        if match is None or match.group("job") != job_id:
            continue
        data_path = case_path.with_suffix("").with_suffix(".dat.h5")
        if not data_path.is_file():
            continue
        pairs.append((int(match.group("iteration")), case_path, data_path))
    pairs.sort(key=lambda item: item[0], reverse=True)
    for _iteration, case_path, data_path in pairs[keep_pairs:]:
        case_path.unlink(missing_ok=True)
        data_path.unlink(missing_ok=True)


def _redacted_error(
    exc: BaseException,
    connection: Mapping[str, Any] | None,
) -> dict[str, str]:
    message = str(exc)
    if connection is not None:
        password = connection.get("password")
        if isinstance(password, str) and password:
            message = message.replace(password, "<redacted>")
    return {"type": type(exc).__name__, "message": message}


def verify_stable_pair(
    case_path: Path,
    data_path: Path,
    *,
    sleep: Callable[[float], None] = time.sleep,
    stability_delay_seconds: float = 2.0,
) -> tuple[int, int]:
    def sizes() -> tuple[int, int]:
        if not case_path.is_file() or not data_path.is_file():
            raise RuntimeError("Checkpoint case/data pair is incomplete")
        values = (case_path.stat().st_size, data_path.stat().st_size)
        if values[0] <= 0 or values[1] <= 0:
            raise RuntimeError("Checkpoint case/data pair contains an empty file")
        return values

    first = sizes()
    sleep(stability_delay_seconds)
    second = sizes()
    if first != second:
        raise RuntimeError(
            f"Checkpoint sizes are not stable: first={first}, second={second}"
        )
    return second


class FluentRunOperations:
    """Minimal PyFluent operations used by the deterministic run worker."""

    def connect(self, connection: Mapping[str, Any]) -> Any:
        import ansys.fluent.core as pyfluent

        try:
            return pyfluent.connect_to_fluent(
                ip=str(connection["host"]),
                port=int(connection["port"]),
                password=str(connection["password"]),
                allow_remote_host=True,
                cleanup_on_exit=False,
                start_transcript=True,
                insecure_mode=bool_env("FLUENT_INSECURE_MODE", False),
            )
        except Exception as exc:
            raise ConnectionError(
                "Could not attach to the published Fluent generation"
            ) from exc

    def is_active(self, session: Any) -> bool:
        active = getattr(session, "is_active", None)
        if callable(active):
            return bool(active())
        health = getattr(session, "health_check", None)
        if health is not None:
            for name in ("is_serving", "check_health", "status"):
                checker = getattr(health, name, None)
                if checker is None:
                    continue
                value = checker() if callable(checker) else checker
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
        raise AttributeError("Session has no supported health API")

    def read_case(self, session: Any, path: Path) -> None:
        session.settings.file.read_case(file_name=str(path))

    def read_data(self, session: Any, path: Path) -> None:
        session.settings.file.read_data(file_name=str(path))

    def initialize(self, session: Any) -> None:
        session.settings.solution.initialization.hybrid_initialize()

    def iterate(self, session: Any, iterations: int) -> None:
        session.settings.solution.run_calculation.iterate(iter_count=iterations)

    def write_case(self, session: Any, path: Path) -> None:
        session.settings.file.write_case(file_name=str(path))

    def write_data(self, session: Any, path: Path) -> None:
        session.settings.file.write_data(file_name=str(path))

    def detach(self, session: Any) -> None:
        exit_method = getattr(session, "exit", None)
        if callable(exit_method):
            exit_method(
                timeout=5,
                timeout_force=False,
                wait=False,
            )


def execute_run_request(
    request: RunRequest,
    *,
    latest_connection_path: Path,
    operations: FluentRunOperations | None = None,
    pair_verifier: Callable[[Path, Path], tuple[int, int]] | None = None,
) -> dict[str, Any]:
    """Execute one pinned request without restarting or selecting recovery state."""

    ops = operations or FluentRunOperations()
    verify_pair = pair_verifier or (
        lambda case_path, data_path: verify_stable_pair(case_path, data_path)
    )
    started_at = utc_now()
    output_dir = Path(request.output_directory)
    connection: dict[str, Any] | None = None
    session: Any | None = None
    completed = request.completed_iterations
    last_checkpoint: dict[str, Any] | None = None
    status = "failed"
    error: dict[str, str] | None = None
    final_data_path: str | None = None

    def ensure_generation() -> None:
        _read_connection(latest_connection_path, request.expected_generation)

    def write_checkpoint(iteration: int, *, final: bool) -> None:
        nonlocal last_checkpoint, final_data_path
        case_path, data_path = _checkpoint_paths(
            request, iteration, final=final
        )
        if case_path.exists() or data_path.exists():
            raise FileExistsError(
                f"Refusing to overwrite checkpoint output: {case_path} / {data_path}"
            )
        ops.write_case(session, case_path)
        ops.write_data(session, data_path)
        case_size, data_size = verify_pair(case_path, data_path)
        if not final:
            _prune_worker_checkpoints(
                output_dir,
                request.job_id,
                keep_pairs=2,
            )
        last_checkpoint = {
            "iteration": iteration,
            "case_path": str(case_path),
            "data_path": str(data_path),
            "case_size_bytes": case_size,
            "data_size_bytes": data_size,
            "file_verified": True,
        }
        if final:
            final_data_path = str(data_path)

    try:
        source_case = Path(request.source_case)
        if not source_case.is_file():
            raise FileNotFoundError(
                f"source_case is not a host-visible file: {source_case}"
            )
        if request.mode == "resume":
            assert request.source_data is not None
            source_data = Path(request.source_data)
            if not source_data.is_file():
                raise FileNotFoundError(
                    f"source_data is not a host-visible file: {source_data}"
                )
        if output_dir.exists() and not output_dir.is_dir():
            raise RunRequestError("output_directory exists but is not a directory")
        output_dir.mkdir(parents=True, exist_ok=True)
        connection = _read_connection(
            latest_connection_path, request.expected_generation
        )
        session = ops.connect(connection)
        if not ops.is_active(session):
            raise GenerationChanged("Fluent gRPC health is unavailable")
        if request.mode == "initialize":
            ops.read_case(session, Path(request.source_case))
            ops.initialize(session)
        else:
            assert request.source_data is not None
            ops.read_case(session, Path(request.source_case))
            ops.read_data(session, Path(request.source_data))

        while completed < request.target_total_iterations:
            ensure_generation()
            next_checkpoint = (
                (completed // request.checkpoint_interval) + 1
            ) * request.checkpoint_interval
            chunk = min(
                request.report_interval,
                request.target_total_iterations - completed,
                max(1, next_checkpoint - completed),
            )
            ops.iterate(session, chunk)
            completed += chunk
            ensure_generation()
            if (
                completed < request.target_total_iterations
                and completed % request.checkpoint_interval == 0
            ):
                write_checkpoint(completed, final=False)

        ensure_generation()
        write_checkpoint(completed, final=True)
        _prune_worker_checkpoints(output_dir, request.job_id, keep_pairs=1)
        status = "completed"
    except Exception as exc:
        connection_lost = isinstance(exc, (GenerationChanged, ConnectionError))
        if not connection_lost and session is not None:
            try:
                connection_lost = not ops.is_active(session)
            except Exception:
                connection_lost = True
        status = "interrupted" if connection_lost else "failed"
        error = _redacted_error(exc, connection)
    finally:
        if session is not None:
            try:
                ops.detach(session)
            except Exception:
                pass

    return {
        "schema_version": RUN_RECEIPT_SCHEMA_VERSION,
        "job_id": request.job_id,
        "status": status,
        "generation": request.expected_generation,
        "mode": request.mode,
        "started_at": started_at,
        "finished_at": utc_now(),
        "target_total_iterations": request.target_total_iterations,
        "completed_iterations": completed,
        "last_checkpoint": last_checkpoint,
        "final_data_path": final_data_path,
        "error": error,
    }


class RunRequestSpool:
    """Atomic single-request queue rooted in the private bridge directory."""

    def __init__(self, bridge_dir: Path):
        self.root = bridge_dir / "run_requests"
        self.incoming = self.root / "incoming"
        self.running = self.root / "running"
        self.completed = self.root / "completed"
        self.failed = self.root / "failed"
        self.receipts = bridge_dir / "run_receipts"

    def ensure_layout(self) -> None:
        for path in (
            self.incoming,
            self.running,
            self.completed,
            self.failed,
            self.receipts,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def claim_next(
        self,
    ) -> tuple[Path, RunRequest | None, dict[str, str] | None] | None:
        self.ensure_layout()
        for source in sorted(self.incoming.glob("*.json")):
            destination = self.running / source.name
            try:
                os.replace(source, destination)
            except FileNotFoundError:
                continue
            try:
                request = RunRequest.from_path(destination)
            except Exception as exc:
                return (
                    destination,
                    None,
                    {"type": type(exc).__name__, "message": str(exc)},
                )
            return destination, request, None
        return None

    def submit(self, request: RunRequest) -> Path:
        """Publish one validated immutable request to the incoming queue."""

        request_path = self.incoming / f"{request.job_id}.json"
        self.ensure_layout()
        collisions = [
            directory / request_path.name
            for directory in (
                self.incoming,
                self.running,
                self.completed,
                self.failed,
            )
        ]
        if any(path.exists() for path in collisions):
            raise FileExistsError(
                f"A run request already exists for job_id={request.job_id}"
            )
        _atomic_write_json(request_path, request.to_dict())
        return request_path

    def finish(
        self, claimed_path: Path, request: RunRequest, receipt: Mapping[str, Any]
    ) -> Path:
        status = receipt.get("status")
        terminal_dir = self.completed if status == "completed" else self.failed
        receipt_path = self.receipts / f"{request.job_id}.json"
        _atomic_write_json(receipt_path, receipt)
        terminal_path = terminal_dir / claimed_path.name
        os.replace(claimed_path, terminal_path)
        return receipt_path


class FluentRunWorker:
    def __init__(
        self,
        bridge_dir: Path,
        *,
        operations: FluentRunOperations | None = None,
        pair_verifier: Callable[[Path, Path], tuple[int, int]] | None = None,
    ):
        self.bridge_dir = bridge_dir
        self.spool = RunRequestSpool(bridge_dir)
        self.operations = operations
        self.pair_verifier = pair_verifier

    def process_next(self) -> Path | None:
        claim = self.spool.claim_next()
        if claim is None:
            return None
        path, request, validation_error = claim
        if request is None:
            job_id = path.stem if _JOB_ID.fullmatch(path.stem) else "invalid-request"
            receipt = {
                "schema_version": RUN_RECEIPT_SCHEMA_VERSION,
                "job_id": job_id,
                "status": "failed",
                "generation": None,
                "mode": None,
                "started_at": utc_now(),
                "finished_at": utc_now(),
                "target_total_iterations": None,
                "completed_iterations": 0,
                "last_checkpoint": None,
                "final_data_path": None,
                "error": validation_error,
            }
            receipt_path = self.spool.receipts / f"{job_id}.json"
            _atomic_write_json(receipt_path, receipt)
            os.replace(path, self.spool.failed / path.name)
            return receipt_path
        receipt = execute_run_request(
            request,
            latest_connection_path=self.bridge_dir / "latest_connection.json",
            operations=self.operations,
            pair_verifier=self.pair_verifier,
        )
        return self.spool.finish(path, request, receipt)


def submit_run_request(bridge_dir: Path, request: RunRequest) -> Path:
    """Laptop-side convenience wrapper for atomic run-request publication."""

    return RunRequestSpool(bridge_dir).submit(request)
