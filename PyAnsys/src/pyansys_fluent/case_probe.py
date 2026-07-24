"""Transactional read-only case identity stage for the Fluent host worker."""

from __future__ import annotations

import hashlib
import shutil
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .host_worker import (
    HostWorkerConfig,
    call_with_timeout,
    close_session_best_effort,
    connect_from_server_info,
    session_is_active,
)
from .job_protocol import (
    HealthStageContext,
    JobSpec,
    SUPPORTED_CASE_EXTENSIONS,
    StageReceipt,
    structured_error,
    utc_timestamp,
)


class CaseInputValidationError(ValueError):
    """Raised before Fluent contact when the requested source is invalid."""


class WorkerBootMismatchError(RuntimeError):
    """Raised when a job targets a different worker boot."""


class FluentGenerationMismatchError(RuntimeError):
    """Raised when a job targets a different Fluent process generation."""


class FluentCaseLoadError(RuntimeError):
    """Raised when Fluent does not accept the disposable case copy."""


@dataclass(frozen=True)
class PreparedCaseInput:
    """Validated source identity plus a worker-owned disposable copy."""

    requested_path: str
    resolved_path: Path
    disposable_path: Path
    source_file_size_bytes: int
    source_sha256: str | None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def prepare_disposable_case_copy(
    spec: JobSpec,
    runtime_dir: Path,
) -> PreparedCaseInput:
    """Validate a source case and create a separate worker-owned copy."""

    spec.validate()
    if spec.stage_type not in {"case_identity_probe", "resumable_run"}:
        raise CaseInputValidationError(
            "prepare_disposable_case_copy requires a case-consuming stage"
        )
    assert spec.case_path is not None

    requested = spec.case_path
    try:
        source = Path(requested)
    except (OSError, ValueError) as exc:
        raise CaseInputValidationError(f"Malformed case path: {exc}") from exc
    if not source.is_absolute():
        raise CaseInputValidationError("Case path must be absolute")
    if not requested.lower().endswith(SUPPORTED_CASE_EXTENSIONS):
        raise CaseInputValidationError(
            "Unsupported case extension; expected .cas.h5, .cas.gz, or .cas"
        )

    try:
        resolved = source.resolve(strict=True)
    except (OSError, ValueError) as exc:
        raise CaseInputValidationError(
            f"Case file does not exist or cannot be resolved: {requested}"
        ) from exc
    if not resolved.is_file():
        raise CaseInputValidationError(f"Case path is not a file: {resolved}")

    before = resolved.stat()
    if before.st_size <= 0:
        raise CaseInputValidationError(f"Case file is empty: {resolved}")
    if (
        spec.expected_file_size_bytes is not None
        and before.st_size != spec.expected_file_size_bytes
    ):
        raise CaseInputValidationError(
            "Case file size mismatch: expected "
            f"{spec.expected_file_size_bytes}, observed {before.st_size}"
        )

    source_digest = None
    if spec.compute_sha256 or spec.expected_sha256 is not None:
        source_digest = _sha256(resolved)
        if (
            spec.expected_sha256 is not None
            and source_digest.lower() != spec.expected_sha256.lower()
        ):
            raise CaseInputValidationError(
                "Case SHA-256 mismatch: expected "
                f"{spec.expected_sha256.lower()}, observed {source_digest}"
            )

    artifact_dir = (
        Path(runtime_dir)
        / "stage_artifacts"
        / spec.stage_type
        / spec.job_id
        / uuid.uuid4().hex
    )
    artifact_dir.mkdir(parents=True, exist_ok=False)
    disposable = artifact_dir / resolved.name
    shutil.copy2(resolved, disposable)

    after = resolved.stat()
    copied = disposable.stat()
    if (
        after.st_size != before.st_size
        or after.st_mtime_ns != before.st_mtime_ns
    ):
        raise CaseInputValidationError(
            "Source case changed while the disposable copy was being created"
        )
    if copied.st_size != before.st_size:
        raise CaseInputValidationError(
            "Disposable case copy size differs from the source"
        )
    if source_digest is not None and _sha256(disposable) != source_digest:
        raise CaseInputValidationError(
            "Disposable case copy SHA-256 differs from the source"
        )

    return PreparedCaseInput(
        requested_path=requested,
        resolved_path=resolved,
        disposable_path=disposable.resolve(strict=True),
        source_file_size_bytes=before.st_size,
        source_sha256=source_digest,
    )


def _safe_value(callback: Callable[[], Any]) -> tuple[Any | None, str | None]:
    try:
        return callback(), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    try:
        return _json_safe(value.tolist())
    except Exception:
        pass
    try:
        return _json_safe(value.item())
    except Exception:
        return str(value)


def collect_offline_case_identity(
    case_path: Path,
    *,
    case_reader_factory: Callable[[Path], Any] | None = None,
) -> dict[str, Any]:
    """Collect stable file-reader evidence without contacting Fluent."""

    if case_reader_factory is None:
        from ansys.fluent.core.filereader.case_file import CaseFile

        case_reader_factory = lambda path: CaseFile(case_file_name=str(path))

    identity: dict[str, Any] = {
        "evidence_source": "PyFluent CaseFile on disposable copy",
        "dimension": None,
        "precision": None,
        "mesh": {
            "surface_count": None,
            "surfaces": None,
            "cell_count": None,
            "face_count": None,
            "count_note": (
                "Cell and total face counts are unavailable from the stable "
                "offline API used by this stage."
            ),
        },
        "boundary_zones": None,
        "active_models": None,
        "optional_metadata_errors": [],
    }

    reader, reader_error = _safe_value(lambda: case_reader_factory(case_path))
    if reader_error is not None:
        identity["optional_metadata_errors"].append(
            f"CaseFile initialization unavailable: {reader_error}"
        )
        return identity

    dimension, error = _safe_value(reader.num_dimensions)
    if error is None:
        identity["dimension"] = {
            "value": _json_safe(dimension),
            "source": "CaseFile.num_dimensions",
        }
    else:
        identity["optional_metadata_errors"].append(
            f"dimension unavailable: {error}"
        )

    precision, error = _safe_value(reader.precision)
    if error is None:
        precision_name = {1: "single", 2: "double"}.get(precision)
        identity["precision"] = {
            "raw_value": _json_safe(precision),
            "value": precision_name,
            "source": "CaseFile.precision",
        }
    else:
        identity["optional_metadata_errors"].append(
            f"precision unavailable: {error}"
        )

    mesh, error = _safe_value(reader.get_mesh)
    if error is not None:
        identity["optional_metadata_errors"].append(f"mesh unavailable: {error}")
        return identity

    surface_names, names_error = _safe_value(mesh.get_surface_names)
    surface_ids, ids_error = _safe_value(mesh.get_surface_ids)
    if names_error is not None:
        identity["optional_metadata_errors"].append(
            f"surface names unavailable: {names_error}"
        )
    if ids_error is not None:
        identity["optional_metadata_errors"].append(
            f"surface IDs unavailable: {ids_error}"
        )

    if isinstance(surface_names, (list, tuple)):
        identity["mesh"]["surface_count"] = len(surface_names)
        surfaces: list[dict[str, Any]] = []
        for index, name in enumerate(surface_names):
            surface: dict[str, Any] = {"name": str(name)}
            if isinstance(surface_ids, (list, tuple)) and index < len(surface_ids):
                surface_id = surface_ids[index]
                surface["id"] = _json_safe(surface_id)
                locations, location_error = _safe_value(
                    lambda value=surface_id: mesh.get_surface_locs(value)
                )
                if location_error is None:
                    surface["location_range"] = _json_safe(locations)
                else:
                    surface["location_range"] = None
                    identity["optional_metadata_errors"].append(
                        f"surface {name!r} location unavailable: {location_error}"
                    )
            surfaces.append(surface)
        identity["mesh"]["surfaces"] = surfaces
    return identity


def _summarize_boundary_state(state: Any) -> list[dict[str, str]]:
    if not isinstance(state, Mapping):
        raise TypeError("boundary condition state is not a mapping")
    zones: list[dict[str, str]] = []
    for boundary_type, members in state.items():
        if not isinstance(members, Mapping):
            continue
        for name in members:
            if str(name) == "settings":
                continue
            zones.append({"name": str(name), "type": str(boundary_type)})
    return sorted(zones, key=lambda item: (item["type"], item["name"]))


class CaseIdentityProbeClient:
    """Short-lived client that loads only a disposable case copy."""

    def __init__(
        self,
        *,
        connect_factory: Callable[
            [Path, HostWorkerConfig], Any
        ] = connect_from_server_info,
        pyfluent_version_factory: Callable[[], str] | None = None,
        case_reader_factory: Callable[[Path], Any] | None = None,
        prepare_case_factory: Callable[
            [JobSpec, Path], PreparedCaseInput
        ] = prepare_disposable_case_copy,
        monotonic: Callable[[], float] = time.monotonic,
        timestamp_factory: Callable[[], str] = utc_timestamp,
    ):
        self.connect_factory = connect_factory
        self.pyfluent_version_factory = (
            pyfluent_version_factory or self._installed_pyfluent_version
        )
        self.case_reader_factory = case_reader_factory
        self.prepare_case_factory = prepare_case_factory
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
        prepared: PreparedCaseInput | None = None
        identity: dict[str, Any] | None = None
        pyfluent_version: str | None = None
        fluent_version: str | None = None
        health_result: bool | None = None
        accepted = False
        detached = False
        error: dict[str, Any] | None = None

        def remaining(label: str) -> float:
            value = deadline - self._monotonic()
            if value <= 0:
                raise TimeoutError(
                    f"case_identity_probe timed out before {label} completed"
                )
            return value

        def optional_live_value(
            label: str,
            callback: Callable[[], Any],
        ) -> tuple[Any | None, str | None]:
            try:
                return (
                    call_with_timeout(
                        callback,
                        remaining(label),
                        label=f"case-probe-{label}",
                    ),
                    None,
                )
            except TimeoutError:
                raise
            except Exception as exc:
                return None, f"{type(exc).__name__}: {exc}"

        try:
            if spec.expected_worker_boot_id != context.worker_boot_id:
                raise WorkerBootMismatchError(
                    "Worker boot mismatch: expected "
                    f"{spec.expected_worker_boot_id}, observed "
                    f"{context.worker_boot_id}"
                )
            if spec.expected_fluent_generation != context.fluent_generation:
                raise FluentGenerationMismatchError(
                    "Fluent generation mismatch: expected "
                    f"{spec.expected_fluent_generation}, observed "
                    f"{context.fluent_generation}"
                )
            if not context.process_is_alive():
                raise FluentGenerationMismatchError(
                    f"Fluent generation {context.fluent_generation} is not alive"
                )

            prepared = call_with_timeout(
                lambda: self.prepare_case_factory(spec, context.config.work_dir),
                remaining("case input validation and copy"),
                label="case-probe-prepare",
            )
            identity = call_with_timeout(
                lambda: collect_offline_case_identity(
                    prepared.disposable_path,
                    case_reader_factory=self.case_reader_factory,
                ),
                remaining("offline case identity"),
                label="case-probe-offline-identity",
            )
            pyfluent_version = str(
                call_with_timeout(
                    self.pyfluent_version_factory,
                    remaining("PyFluent version read"),
                    label="case-probe-pyfluent-version",
                )
            )
            session = call_with_timeout(
                lambda: self.connect_factory(
                    context.server_info_path,
                    context.config,
                ),
                remaining("stage connection"),
                label="case-probe-connect",
                late_result_cleanup=lambda late_session: close_session_best_effort(
                    late_session,
                    timeout_seconds=context.config.health_timeout_seconds,
                ),
            )
            health_result = bool(
                call_with_timeout(
                    lambda: session_is_active(session),
                    remaining("initial health check"),
                    label="case-probe-initial-health",
                )
            )
            if not health_result:
                raise FluentCaseLoadError(
                    "Stage client connected but gRPC health is inactive"
                )

            file_settings = session.settings.file
            read_case = getattr(file_settings, "read_case", None)
            if not callable(read_case):
                raise FluentCaseLoadError(
                    "Fluent session does not expose settings.file.read_case"
                )
            call_with_timeout(
                lambda: read_case(file_name=str(prepared.disposable_path)),
                remaining("Fluent case load"),
                label="case-probe-read-case",
            )
            health_result = bool(
                call_with_timeout(
                    lambda: session_is_active(session),
                    remaining("post-load health check"),
                    label="case-probe-post-load-health",
                )
            )
            if not health_result:
                raise FluentCaseLoadError(
                    "Fluent became unhealthy after reading the case"
                )
            accepted = True

            get_version = getattr(session, "get_fluent_version", None)
            if callable(get_version):
                fluent_version = str(
                    call_with_timeout(
                        get_version,
                        remaining("Fluent version read"),
                        label="case-probe-fluent-version",
                    )
                )
            else:
                raise FluentCaseLoadError(
                    "Stage session does not expose get_fluent_version()"
                )

            assert identity is not None
            boundary_state, boundary_error = optional_live_value(
                "boundary-identity",
                lambda: session.settings.setup.boundary_conditions.get_state(),
            )
            if boundary_error is None:
                try:
                    identity["boundary_zones"] = {
                        "value": _summarize_boundary_state(boundary_state),
                        "source": "settings.setup.boundary_conditions.get_state",
                    }
                except Exception as exc:
                    boundary_error = f"{type(exc).__name__}: {exc}"
            if boundary_error is not None:
                identity["boundary_zones"] = {
                    "value": None,
                    "unavailable_reason": boundary_error,
                }

            active_models, models_error = optional_live_value(
                "active-model-identity",
                lambda: session.settings.setup.models.get_active_child_names(),
            )
            if models_error is None and isinstance(active_models, (list, tuple)):
                identity["active_models"] = {
                    "value": [str(value) for value in active_models],
                    "source": "settings.setup.models.get_active_child_names",
                }
            else:
                if models_error is None:
                    models_error = (
                        "get_active_child_names returned a non-list value"
                    )
                identity["active_models"] = {
                    "value": None,
                    "unavailable_reason": models_error,
                }
        except Exception as exc:
            retryable = isinstance(
                exc,
                (
                    TimeoutError,
                    ConnectionError,
                    WorkerBootMismatchError,
                    FluentGenerationMismatchError,
                ),
            )
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
            requested_case_path=spec.case_path,
            resolved_case_path=(
                str(prepared.resolved_path) if prepared is not None else None
            ),
            disposable_case_path=(
                str(prepared.disposable_path) if prepared is not None else None
            ),
            source_file_size_bytes=(
                prepared.source_file_size_bytes if prepared is not None else None
            ),
            source_sha256=(
                prepared.source_sha256 if prepared is not None else None
            ),
            fluent_accepted_case=accepted,
            case_identity=identity,
            data_loaded=False,
            error=error,
        )
