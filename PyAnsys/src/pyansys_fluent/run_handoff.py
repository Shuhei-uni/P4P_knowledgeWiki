"""Detached run orchestration with terminal manifests and Codex handoff.

The long-running simulation command is deterministic. This module does not
interpret CFD results or alter Fluent settings. It owns only process execution,
terminal verification, durable local status, and the optional event-driven
handoff to a Codex session after the run reaches a terminal state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Mapping, Sequence

import yaml


TERMINAL_STATUSES = {"COMPLETE", "BLOCKED"}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _as_command(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{label} must be a non-empty YAML list of command arguments")
    return tuple(value)


def _resolve(root: Path, value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


@dataclass(frozen=True)
class RequiredFile:
    path: Path
    min_size_bytes: int = 1


@dataclass(frozen=True)
class CodexHandoff:
    enabled: bool
    session_id: str | None
    executable: str
    working_directory: Path
    prompt: str
    log_path: Path
    trigger_on: tuple[str, ...] = ("COMPLETE", "BLOCKED")

    def validate(self) -> None:
        if not self.enabled:
            return
        if not self.session_id:
            raise ValueError(
                "codex.session_id is required when Codex handoff is enabled; "
                "do not use --last for autonomous multi-job handoff"
            )
        invalid = [status for status in self.trigger_on if status not in TERMINAL_STATUSES]
        if invalid:
            raise ValueError(f"codex.trigger_on contains unsupported status values: {invalid}")


@dataclass(frozen=True)
class RunHandoffSpec:
    job_id: str
    repo_root: Path
    command: tuple[str, ...]
    working_directory: Path
    environment: Mapping[str, str]
    manifest_path: Path
    runner_log_path: Path
    worker_log_path: Path
    required_files: tuple[RequiredFile, ...]
    verifier_command: tuple[str, ...] | None
    verifier_working_directory: Path
    verifier_log_path: Path
    codex: CodexHandoff

    def validate(self) -> None:
        if not self.job_id.strip():
            raise ValueError("job.id must not be empty")
        if not self.command:
            raise ValueError("runner.command must not be empty")
        for item in self.required_files:
            if item.min_size_bytes < 0:
                raise ValueError("completion.required_files min_size_bytes must be zero or greater")
        if not self.required_files and self.verifier_command is None:
            raise ValueError(
                "completion must declare required_files and/or verifier_command so a zero exit code "
                "is not mistaken for a verified final save"
            )
        self.codex.validate()


def load_spec(path: Path, *, repo_root: Path) -> RunHandoffSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("job spec must contain a YAML mapping")

    job = raw.get("job", {})
    runner = raw.get("runner", {})
    completion = raw.get("completion", {})
    codex_raw = raw.get("codex", {})
    if not all(isinstance(section, Mapping) for section in (job, runner, completion, codex_raw)):
        raise ValueError("job, runner, completion, and codex sections must be YAML mappings")

    job_id = str(job.get("id", "")).strip()
    command = _as_command(runner.get("command"), "runner.command")
    working_directory = _resolve(repo_root, str(runner.get("cwd", ".")))

    env_raw = runner.get("env", {})
    if not isinstance(env_raw, Mapping):
        raise ValueError("runner.env must be a mapping")
    environment = {str(key): str(value) for key, value in env_raw.items()}

    default_output = Path("PyAnsys/output/run-handoff") / job_id
    manifest_path = _resolve(repo_root, str(job.get("manifest", default_output / "job_manifest.json")))
    runner_log_path = _resolve(repo_root, str(runner.get("log", default_output / "runner.log")))
    worker_log_path = _resolve(repo_root, str(job.get("worker_log", default_output / "worker.log")))

    required_files_raw = completion.get("required_files", [])
    if not isinstance(required_files_raw, list):
        raise ValueError("completion.required_files must be a list")
    required_files: list[RequiredFile] = []
    for item in required_files_raw:
        if isinstance(item, str):
            required_files.append(RequiredFile(path=_resolve(repo_root, item)))
            continue
        if not isinstance(item, Mapping) or "path" not in item:
            raise ValueError("each completion.required_files entry must be a path string or mapping")
        required_files.append(
            RequiredFile(
                path=_resolve(repo_root, str(item["path"])),
                min_size_bytes=int(item.get("min_size_bytes", 1)),
            )
        )

    verifier_command_raw = completion.get("verifier_command")
    verifier_command = (
        _as_command(verifier_command_raw, "completion.verifier_command")
        if verifier_command_raw is not None
        else None
    )
    verifier_working_directory = _resolve(repo_root, str(completion.get("verifier_cwd", ".")))
    verifier_log_path = _resolve(repo_root, str(completion.get("verifier_log", default_output / "verifier.log")))

    codex_enabled = bool(codex_raw.get("enabled", False))
    trigger_on_raw = codex_raw.get("trigger_on", ["COMPLETE", "BLOCKED"])
    if not isinstance(trigger_on_raw, list) or not all(isinstance(item, str) for item in trigger_on_raw):
        raise ValueError("codex.trigger_on must be a list of terminal status names")
    codex = CodexHandoff(
        enabled=codex_enabled,
        session_id=str(codex_raw.get("session_id", "")).strip() or None,
        executable=str(codex_raw.get("executable", "codex")),
        working_directory=_resolve(repo_root, str(codex_raw.get("cwd", "."))),
        prompt=str(
            codex_raw.get(
                "prompt",
                "The Fluent job has reached a terminal state. Read the job manifest, "
                "inspect the execution evidence, and continue the scientific workflow. "
                "If the run completed, analyse it; if it blocked, diagnose the blocker."
            )
        ),
        log_path=_resolve(repo_root, str(codex_raw.get("log", default_output / "codex_handoff.log"))),
        trigger_on=tuple(trigger_on_raw),
    )

    spec = RunHandoffSpec(
        job_id=job_id,
        repo_root=repo_root,
        command=command,
        working_directory=working_directory,
        environment=environment,
        manifest_path=manifest_path,
        runner_log_path=runner_log_path,
        worker_log_path=worker_log_path,
        required_files=tuple(required_files),
        verifier_command=verifier_command,
        verifier_working_directory=verifier_working_directory,
        verifier_log_path=verifier_log_path,
        codex=codex,
    )
    spec.validate()
    return spec


def verify_required_files(required_files: Sequence[RequiredFile]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for required in required_files:
        exists = required.path.is_file()
        size = required.path.stat().st_size if exists else None
        passed = bool(exists and size is not None and size >= required.min_size_bytes)
        checks.append(
            {
                "path": str(required.path),
                "exists": exists,
                "size_bytes": size,
                "min_size_bytes": required.min_size_bytes,
                "passed": passed,
            }
        )
    return checks


def build_codex_command(codex: CodexHandoff, manifest_path: Path, status: str) -> tuple[str, ...]:
    codex.validate()
    if not codex.enabled:
        raise ValueError("Codex handoff is disabled")
    prompt = (
        f"{codex.prompt}\n\n"
        f"Job terminal status: {status}\n"
        f"Job manifest: {manifest_path}\n"
        "Treat the manifest and referenced execution artifacts as the handoff source of truth."
    )
    return (codex.executable, "exec", "resume", str(codex.session_id), prompt)


def _run_verifier(spec: RunHandoffSpec) -> dict[str, Any] | None:
    if spec.verifier_command is None:
        return None
    spec.verifier_log_path.parent.mkdir(parents=True, exist_ok=True)
    started = utc_timestamp()
    with spec.verifier_log_path.open("a", encoding="utf-8") as log:
        completed = subprocess.run(
            spec.verifier_command,
            cwd=spec.verifier_working_directory,
            env={**os.environ, **spec.environment},
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            check=False,
            text=True,
        )
    return {
        "command": list(spec.verifier_command),
        "cwd": str(spec.verifier_working_directory),
        "started_at_utc": started,
        "finished_at_utc": utc_timestamp(),
        "return_code": completed.returncode,
        "passed": completed.returncode == 0,
        "log": str(spec.verifier_log_path),
    }


def _base_manifest(spec: RunHandoffSpec) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "job_id": spec.job_id,
        "status": "PENDING",
        "worker_pid": os.getpid(),
        "repo_root": str(spec.repo_root),
        "runner": {
            "command": list(spec.command),
            "cwd": str(spec.working_directory),
            "log": str(spec.runner_log_path),
        },
        "verification": {
            "required_files": [],
            "verifier": None,
        },
        "handoff": {
            "enabled": spec.codex.enabled,
            "status": "NOT_STARTED" if spec.codex.enabled else "DISABLED",
        },
    }


def run_job(spec: RunHandoffSpec, *, allow_existing_terminal: bool = False) -> dict[str, Any]:
    spec.validate()
    if spec.manifest_path.exists() and not allow_existing_terminal:
        try:
            existing = json.loads(spec.manifest_path.read_text(encoding="utf-8"))
        except Exception:
            existing = None
        if isinstance(existing, Mapping) and existing.get("status") in TERMINAL_STATUSES:
            raise FileExistsError(
                f"Refusing to repeat terminal job {spec.job_id}; manifest already exists at {spec.manifest_path}"
            )
        raise FileExistsError(
            f"Refusing to start job {spec.job_id}; manifest already exists at {spec.manifest_path}. "
            "Reconcile the previous run before retrying."
        )

    manifest = _base_manifest(spec)
    manifest["status"] = "RUNNING"
    manifest["started_at_utc"] = utc_timestamp()
    atomic_write_json(spec.manifest_path, manifest)

    spec.runner_log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with spec.runner_log_path.open("a", encoding="utf-8") as log:
            completed = subprocess.run(
                spec.command,
                cwd=spec.working_directory,
                env={**os.environ, **spec.environment},
                stdout=log,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                check=False,
                text=True,
            )
        manifest["runner"]["return_code"] = completed.returncode
        manifest["runner"]["finished_at_utc"] = utc_timestamp()
    except Exception as exc:
        manifest["runner"]["return_code"] = None
        manifest["runner"]["finished_at_utc"] = utc_timestamp()
        manifest["runner"]["exception"] = f"{type(exc).__name__}: {exc}"

    manifest["status"] = "VERIFYING"
    atomic_write_json(spec.manifest_path, manifest)

    file_checks = verify_required_files(spec.required_files)
    manifest["verification"]["required_files"] = file_checks
    try:
        verifier = _run_verifier(spec)
    except Exception as exc:
        verifier = {
            "passed": False,
            "exception": f"{type(exc).__name__}: {exc}",
            "log": str(spec.verifier_log_path),
        }
    manifest["verification"]["verifier"] = verifier

    runner_ok = manifest["runner"].get("return_code") == 0
    files_ok = all(item["passed"] for item in file_checks)
    verifier_ok = verifier is None or bool(verifier.get("passed"))
    manifest["status"] = "COMPLETE" if runner_ok and files_ok and verifier_ok else "BLOCKED"
    manifest["finished_at_utc"] = utc_timestamp()
    atomic_write_json(spec.manifest_path, manifest)
    return manifest


def _detached_process_kwargs() -> dict[str, Any]:
    if os.name == "nt":
        flags = 0
        flags |= int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
        flags |= int(getattr(subprocess, "DETACHED_PROCESS", 0))
        return {"creationflags": flags, "close_fds": True}
    return {"start_new_session": True, "close_fds": True}


def launch_codex_handoff(spec: RunHandoffSpec, manifest: dict[str, Any]) -> dict[str, Any]:
    status = str(manifest.get("status"))
    if not spec.codex.enabled:
        result = {"enabled": False, "status": "DISABLED"}
        manifest["handoff"] = result
        atomic_write_json(spec.manifest_path, manifest)
        return result
    if status not in spec.codex.trigger_on:
        result = {"enabled": True, "status": "SKIPPED", "reason": f"status {status} not in trigger_on"}
        manifest["handoff"] = result
        atomic_write_json(spec.manifest_path, manifest)
        return result

    command = build_codex_command(spec.codex, spec.manifest_path, status)
    executable = shutil.which(spec.codex.executable)
    if executable is None:
        result = {
            "enabled": True,
            "status": "FAILED",
            "error": f"Codex executable not found on PATH: {spec.codex.executable}",
            "command": list(command),
        }
        manifest["handoff"] = result
        atomic_write_json(spec.manifest_path, manifest)
        return result

    spec.codex.log_path.parent.mkdir(parents=True, exist_ok=True)
    log = None
    try:
        log = spec.codex.log_path.open("a", encoding="utf-8")
        process = subprocess.Popen(
            command,
            cwd=spec.codex.working_directory,
            env=os.environ.copy(),
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            **_detached_process_kwargs(),
        )
    except Exception as exc:
        if log is not None:
            log.close()
        result = {
            "enabled": True,
            "status": "FAILED",
            "error": f"{type(exc).__name__}: {exc}",
            "command": list(command),
            "log": str(spec.codex.log_path),
        }
    else:
        log.close()
        result = {
            "enabled": True,
            "status": "LAUNCHED",
            "pid": process.pid,
            "command": list(command),
            "cwd": str(spec.codex.working_directory),
            "log": str(spec.codex.log_path),
            "launched_at_utc": utc_timestamp(),
        }
    manifest["handoff"] = result
    atomic_write_json(spec.manifest_path, manifest)
    return result


def launch_detached_worker(
    script_path: Path, spec_path: Path, worker_log_path: Path, *, force: bool = False
) -> int:
    worker_log_path.parent.mkdir(parents=True, exist_ok=True)
    log = worker_log_path.open("a", encoding="utf-8")
    command = [
        sys.executable,
        str(script_path),
        "--job",
        str(spec_path),
        "--worker",
    ]
    if force:
        command.append("--force")
    try:
        process = subprocess.Popen(
            command,
            cwd=script_path.parents[3],
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            **_detached_process_kwargs(),
        )
    except Exception:
        log.close()
        raise
    log.close()
    return process.pid
