#!/usr/bin/env python3
"""Small, atomic progress ledger for laptop-controlled Fluent work.

The ledger records what the agent has proved about a case.  It deliberately
does not describe how to build a setup or execute Fluent commands.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping


SCHEMA_VERSION = 1
_FORBIDDEN_KEY_PARTS = ("password", "secret", "credential")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _assert_no_secrets(value: Any, *, location: str = "ledger") -> None:
    """Reject credential-shaped fields before they reach persistent storage."""

    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if any(part in key_text for part in _FORBIDDEN_KEY_PARTS):
                raise ValueError(f"{location} must not contain credential field {key!r}")
            _assert_no_secrets(child, location=f"{location}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_no_secrets(child, location=f"{location}[{index}]")


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Replace *path* atomically with a private UTF-8 JSON document."""

    _assert_no_secrets(payload)
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    temp_path = Path(temp_name)
    try:
        try:
            os.chmod(temp_path, 0o600)
        except OSError:
            pass
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temp_path.unlink(missing_ok=True)
        raise


def _validate_ledger(payload: Mapping[str, Any]) -> dict[str, Any]:
    _assert_no_secrets(payload)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported agent ledger schema_version: {payload.get('schema_version')!r}"
        )
    for field in ("job_id", "phase", "status"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            raise ValueError(f"Agent ledger requires a non-empty {field}")
    generation = payload.get("connection_generation")
    if generation is not None and (
        not isinstance(generation, int) or isinstance(generation, bool) or generation < 0
    ):
        raise ValueError("connection_generation must be a non-negative integer or null")
    completed = payload.get("completed_steps")
    if not isinstance(completed, list) or not all(
        isinstance(step, str) and step.strip() for step in completed
    ):
        raise ValueError("completed_steps must be a list of non-empty strings")
    if len(completed) != len(set(completed)):
        raise ValueError("completed_steps must not contain duplicates")
    return deepcopy(dict(payload))


class AgentLedger:
    """Persistent proof-of-progress state owned by the laptop agent."""

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()

    def create(
        self,
        *,
        job_id: str,
        phase: str,
        setup_plan_path: str = "",
        connection_generation: int | None = None,
        analysis_manifest_path: str | None = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        if self.path.exists() and not overwrite:
            raise FileExistsError(f"Agent ledger already exists: {self.path}")
        now = _utc_now()
        payload = {
            "schema_version": SCHEMA_VERSION,
            "job_id": job_id,
            "phase": phase,
            "status": "ready",
            "connection_generation": connection_generation,
            "setup_plan_path": setup_plan_path,
            "last_completed_step": None,
            "current_step": None,
            "current_step_safe_to_retry": False,
            "latest_case_checkpoint": None,
            "latest_data_checkpoint": None,
            "completed_steps": [],
            "analysis_manifest_path": analysis_manifest_path,
            "created_at": now,
            "updated_at": now,
        }
        self._write(payload)
        return deepcopy(payload)

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"Agent ledger does not exist: {self.path}")
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Agent ledger is not valid JSON: {self.path}") from exc
        if not isinstance(payload, Mapping):
            raise ValueError("Agent ledger root must be a JSON object")
        return _validate_ledger(payload)

    def start_step(self, step: str, *, safe_to_retry: bool = False) -> dict[str, Any]:
        step = step.strip()
        if not step:
            raise ValueError("step must be non-empty")
        payload = self.read()
        if payload.get("current_step") is not None:
            raise RuntimeError(
                f"Cannot start {step!r}; step {payload['current_step']!r} is still active"
            )
        if step in payload["completed_steps"]:
            raise RuntimeError(f"Step {step!r} is already complete")
        payload.update(
            status="executing_step",
            current_step=step,
            current_step_safe_to_retry=bool(safe_to_retry),
        )
        return self._save_transition(payload)

    def complete_step(self, step: str) -> dict[str, Any]:
        step = step.strip()
        payload = self.read()
        if payload.get("current_step") != step:
            raise RuntimeError(
                f"Cannot complete {step!r}; active step is {payload.get('current_step')!r}"
            )
        payload["completed_steps"].append(step)
        payload.update(
            status="ready",
            last_completed_step=step,
            current_step=None,
            current_step_safe_to_retry=False,
        )
        return self._save_transition(payload)

    def accept_checkpoint(
        self,
        case_path: str,
        *,
        data_path: str | None = None,
    ) -> dict[str, Any]:
        """Record a checkpoint only after the caller has verified it in Fluent."""

        if not case_path.strip():
            raise ValueError("case_path must be non-empty")
        if data_path is not None and not data_path.strip():
            raise ValueError("data_path must be non-empty when supplied")
        payload = self.read()
        payload["latest_case_checkpoint"] = case_path
        payload["latest_data_checkpoint"] = data_path
        return self._save_transition(payload)

    def set_phase(self, phase: str, *, status: str = "ready") -> dict[str, Any]:
        """Move the laptop-owned workflow to a new explicit phase."""

        phase = phase.strip()
        status = status.strip()
        if not phase or not status:
            raise ValueError("phase and status must be non-empty")
        payload = self.read()
        if payload.get("current_step") is not None:
            raise RuntimeError("Cannot change phase while a setup step is active")
        payload["phase"] = phase
        payload["status"] = status
        return self._save_transition(payload)

    def observe_connection_generation(self, generation: int) -> dict[str, Any]:
        """Record the generation used by a verified laptop connection."""

        if isinstance(generation, bool) or not isinstance(generation, int):
            raise ValueError("generation must be an integer")
        if generation < 0:
            raise ValueError("generation must be non-negative")
        payload = self.read()
        current = payload.get("connection_generation")
        if current is not None and generation < current:
            raise ValueError("Connection generation cannot move backwards")
        payload["connection_generation"] = generation
        return self._save_transition(payload)

    def connection_lost(self, *, generation: int | None = None) -> dict[str, Any]:
        payload = self.read()
        if generation is not None:
            current = payload.get("connection_generation")
            if current is not None and generation < current:
                raise ValueError("Lost connection generation cannot move backwards")
            payload["connection_generation"] = generation
        payload["status"] = "connection_lost"
        return self._save_transition(payload)

    def recovered(
        self,
        *,
        generation: int,
        restored_state_verified: bool,
    ) -> dict[str, Any]:
        """Record reconnection after the caller inspects restored Fluent state."""

        payload = self.read()
        if payload.get("status") != "connection_lost":
            raise RuntimeError("Recovery can only be recorded after connection_lost")
        previous = payload.get("connection_generation")
        if previous is not None and generation <= previous:
            raise ValueError(
                f"Recovery generation {generation} must be newer than {previous}"
            )
        payload["connection_generation"] = generation
        payload["status"] = "recovered" if restored_state_verified else "human_review"
        return self._save_transition(payload)

    def _save_transition(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload["updated_at"] = _utc_now()
        self._write(payload)
        return deepcopy(payload)

    def _write(self, payload: Mapping[str, Any]) -> None:
        validated = _validate_ledger(payload)
        _atomic_write_json(self.path, validated)
