"""Shared-file bridge primitives for laptop-controlled Fluent sessions.

The bridge directory is an out-of-band recovery channel.  It is deliberately
small: the watchdog publishes the current Fluent endpoint, while laptop-side
clients reread that document after a generation change.  This module contains
no setup, run, or recovery decision logic.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


CONNECTION_SCHEMA_VERSION = 1
LATEST_CONNECTION_FILENAME = "latest_connection.json"
RUNNING_STATUS = "running"
CONNECTION_STATUSES = frozenset(
    {"starting", "running", "restarting", "failed", "stopped"}
)


class ConnectionDocumentError(ValueError):
    """Raised when a published connection document is unusable."""


@dataclass(frozen=True)
class FluentEndpoint:
    """One Fluent gRPC endpoint.

    The password is excluded from the generated representation so exceptions
    and debug output cannot reveal it accidentally.
    """

    host: str
    port: int
    password: str

    def __init__(self, host: str, port: int, password: str) -> None:
        host = str(host).strip()
        password = str(password).strip()
        if not host:
            raise ValueError("Fluent endpoint host is empty")
        if not 1 <= int(port) <= 65535:
            raise ValueError("Fluent endpoint port is outside 1..65535")
        if not password:
            raise ValueError("Fluent endpoint password is empty")
        object.__setattr__(self, "host", host)
        object.__setattr__(self, "port", int(port))
        object.__setattr__(self, "password", password)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(host={self.host!r}, port={self.port!r}, "
            "password=<redacted>)"
        )


@dataclass(frozen=True)
class BridgePaths:
    """Canonical paths inside one private shared bridge directory."""

    root: Path

    def __post_init__(self) -> None:
        root = Path(self.root).expanduser()
        if not root.is_absolute():
            raise ValueError("FLUENT_BRIDGE_DIR must be an absolute path")
        object.__setattr__(self, "root", root)

    @property
    def latest_connection(self) -> Path:
        return self.root / LATEST_CONNECTION_FILENAME

    @property
    def run_requests(self) -> Path:
        return self.root / "run_requests"


class AtomicJsonFile:
    """Read and atomically replace one JSON document."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def write(self, payload: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        _restrict_directory_best_effort(self.path.parent)
        temporary = self.path.with_name(
            f".{self.path.name}.tmp-{os.getpid()}-{threading.get_ident()}"
        )
        try:
            with temporary.open("w", encoding="utf-8", newline="\n") as stream:
                json.dump(dict(payload), stream, indent=2, default=str)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            _restrict_file_best_effort(temporary)
            os.replace(temporary, self.path)
            _restrict_file_best_effort(self.path)
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass

    def read(self) -> dict[str, Any]:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ConnectionDocumentError("JSON document must be an object")
        return payload


def _restrict_directory_best_effort(path: Path) -> None:
    if os.name == "nt":
        return
    try:
        path.chmod(0o700)
    except OSError:
        pass


def _restrict_file_best_effort(path: Path) -> None:
    if os.name == "nt":
        return
    try:
        path.chmod(0o600)
    except OSError:
        pass


def parse_server_info_text(
    content: str,
    *,
    advertised_host: str | None = None,
) -> FluentEndpoint:
    """Parse Fluent server-info content without returning it in errors.

    Fluent writes ``host:port`` on the first significant line and the gRPC
    password on the second.  The locally written host can be replaced by the
    address that the laptop can reach.
    """

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(lines) < 2:
        raise ValueError("Server-info must contain endpoint and password lines")
    host_port = lines[0]
    password = lines[1]
    if ":" not in host_port:
        raise ValueError("Server-info endpoint does not contain a port")
    local_host, port_text = host_port.rsplit(":", 1)
    local_host = local_host.strip()
    if not local_host:
        raise ValueError("Server-info host is empty")
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ValueError("Server-info port is not an integer") from exc

    host = str(advertised_host).strip() if advertised_host is not None else local_host
    return FluentEndpoint(host=host, port=port, password=password)


def read_server_info(
    path: Path,
    *,
    advertised_host: str | None = None,
) -> FluentEndpoint:
    """Read one server-info file without logging its secret content."""

    return parse_server_info_text(
        Path(path).read_text(encoding="utf-8", errors="replace"),
        advertised_host=advertised_host,
    )


def utc_timestamp(value: float | None = None) -> str:
    """Return a timezone-aware ISO-8601 timestamp."""

    moment = (
        datetime.now(timezone.utc)
        if value is None
        else datetime.fromtimestamp(value, timezone.utc)
    )
    return moment.isoformat()


class ConnectionPublisher:
    """Publish the latest watchdog state and conditionally expose credentials."""

    def __init__(self, paths: BridgePaths):
        self.paths = paths
        self.store = AtomicJsonFile(paths.latest_connection)

    def publish(
        self,
        status: str,
        *,
        generation: int,
        previous_generation: int | None,
        heartbeat_sequence: int,
        endpoint: FluentEndpoint | None = None,
        fluent_pid: int | None = None,
        fluent_version: str | None = None,
        started_at: str | None = None,
        restart_reason: str | None = None,
        updated_at: str | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if status not in CONNECTION_STATUSES:
            raise ValueError(f"Unsupported connection status: {status}")
        if isinstance(generation, bool) or not isinstance(generation, int):
            raise ValueError("generation must be an integer")
        if generation < 0:
            raise ValueError("generation must be non-negative")
        if isinstance(heartbeat_sequence, bool) or not isinstance(
            heartbeat_sequence, int
        ):
            raise ValueError("heartbeat_sequence must be an integer")
        if heartbeat_sequence < 0:
            raise ValueError("heartbeat_sequence must be non-negative")
        if status == RUNNING_STATUS and endpoint is None:
            raise ValueError("running status requires a Fluent endpoint")

        document: dict[str, Any] = {
            "schema_version": CONNECTION_SCHEMA_VERSION,
            "generation": generation,
            "previous_generation": previous_generation,
            "status": status,
            "host": endpoint.host if status == RUNNING_STATUS and endpoint else None,
            "port": endpoint.port if status == RUNNING_STATUS and endpoint else None,
            "password": (
                endpoint.password if status == RUNNING_STATUS and endpoint else None
            ),
            "fluent_pid": fluent_pid,
            "fluent_version": fluent_version,
            "started_at": started_at,
            "updated_at": updated_at or utc_timestamp(),
            "heartbeat_sequence": heartbeat_sequence,
            "restart_reason": restart_reason,
        }
        if extra:
            forbidden = {"host", "port", "password", "status", "generation"}
            overlap = forbidden.intersection(extra)
            if overlap:
                raise ValueError(
                    "extra connection fields cannot replace protected fields: "
                    + ", ".join(sorted(overlap))
                )
            document.update(extra)
        self.store.write(document)
        return document


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ConnectionDocumentError("updated_at must be an ISO-8601 timestamp")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ConnectionDocumentError("updated_at is not valid ISO-8601") from exc
    if result.tzinfo is None:
        raise ConnectionDocumentError("updated_at must include a timezone")
    return result.astimezone(timezone.utc)


def read_latest_connection(
    path_or_bridge_dir: Path,
    *,
    max_age_seconds: float | None = None,
    min_generation: int | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Read and validate a currently usable published Fluent endpoint."""

    candidate = Path(path_or_bridge_dir)
    path = (
        candidate / LATEST_CONNECTION_FILENAME
        if candidate.name != LATEST_CONNECTION_FILENAME
        else candidate
    )
    document = AtomicJsonFile(path).read()
    if document.get("schema_version") != CONNECTION_SCHEMA_VERSION:
        raise ConnectionDocumentError("Unsupported connection schema_version")
    if document.get("status") != RUNNING_STATUS:
        raise ConnectionDocumentError(
            f"Fluent connection is not running (status={document.get('status')!r})"
        )
    try:
        generation = document["generation"]
        if isinstance(generation, bool) or not isinstance(generation, int):
            raise TypeError("generation must be an integer")
        if generation < 0:
            raise ValueError("generation must be non-negative")
        port = document["port"]
        if isinstance(port, bool) or not isinstance(port, int):
            raise TypeError("port must be an integer")
        FluentEndpoint(
            host=document["host"],
            port=port,
            password=document["password"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConnectionDocumentError(
            "Running connection document has an invalid endpoint"
        ) from exc
    if min_generation is not None and generation < min_generation:
        raise ConnectionDocumentError(
            f"Connection generation {generation} is older than required "
            f"generation {min_generation}"
        )
    if max_age_seconds is not None:
        if max_age_seconds <= 0:
            raise ValueError("max_age_seconds must be positive")
        updated = _parse_timestamp(document.get("updated_at"))
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("now must include a timezone")
        current = current.astimezone(timezone.utc)
        age = (current - updated).total_seconds()
        if age > max_age_seconds:
            raise ConnectionDocumentError(
                f"Connection heartbeat is stale by {age:.1f} seconds"
            )
        if age < -60:
            raise ConnectionDocumentError(
                "Connection heartbeat is implausibly far in the future"
            )
    return document


def read_published_generation(path_or_bridge_dir: Path) -> int:
    """Read the last durable generation regardless of connection status.

    Watchdogs use this before launching so generation identifiers remain
    monotonic even when the watchdog process itself is restarted.
    """

    candidate = Path(path_or_bridge_dir)
    path = (
        candidate / LATEST_CONNECTION_FILENAME
        if candidate.name != LATEST_CONNECTION_FILENAME
        else candidate
    )
    document = AtomicJsonFile(path).read()
    if document.get("schema_version") != CONNECTION_SCHEMA_VERSION:
        raise ConnectionDocumentError("Unsupported connection schema_version")
    generation = document.get("generation")
    if (
        isinstance(generation, bool)
        or not isinstance(generation, int)
        or generation < 0
    ):
        raise ConnectionDocumentError(
            "Published connection generation must be a non-negative integer"
        )
    return generation
