#!/usr/bin/env python3
"""Supervise one setup-07j run without competing PyFluent clients.

The supervisor uses a local OS lock to enforce one writer per configured
server/run namespace.  Readiness uses raw TCP only, so it never opens a
throwaway PyFluent client immediately before the production client.  A failed
preparation is never retried automatically.  Qualification is resumed from a
saved checkpoint only when the recorded error is recognizably connection-
related; numerical and physics failures remain stopped for diagnosis.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import env_suffix  # noqa: E402

import prepare_setup07j_transient_vof as prepare07j  # noqa: E402


PYTHON = str(PROJECT_ROOT / ".venv" / "bin" / "python")
PREPARATION_SCRIPT = "scripts/setup/prepare_setup07j_transient_vof.py"
QUALIFICATION_SCRIPT = "scripts/setup/run_setup07j_transient_vof_qualification.py"
GUARD_SCRIPT = "scripts/connection/run_guarded.py"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    result.add_argument("--target-steps", type=int, default=1000)
    result.add_argument("--wait-hours", type=float, default=18.0)
    result.add_argument("--poll-seconds", type=float, default=60.0)
    result.add_argument("--connection-retries", type=int, default=2)
    result.add_argument(
        "--resume-zero-flow-ratio-gate",
        action="store_true",
        help=(
            "Resume an existing step checkpoint only when the prior failure was the "
            "known zero-outlet-flow 0/0 composition-ratio startup gate."
        ),
    )
    result.add_argument(
        "--resume-time-step-proof-gate",
        action="store_true",
        help=(
            "Resume an existing numeric checkpoint only when the prior failure was "
            "the known multi-step early-return clock-proof mismatch."
        ),
    )
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def configured_endpoint(server_id: str) -> tuple[str, int]:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    suffix = env_suffix(server_id)
    ip = os.getenv(f"FLUENT_IP{suffix}", "").strip()
    port = os.getenv(f"FLUENT_PORT{suffix}", "").strip()
    if not ip or not port:
        raise RuntimeError(
            f"raw readiness requires FLUENT_IP{suffix} and FLUENT_PORT{suffix}"
        )
    return ip, int(port)


def tcp_ready(server_id: str, timeout_seconds: float = 5.0) -> tuple[bool, str]:
    try:
        ip, port = configured_endpoint(server_id)
        with socket.create_connection((ip, port), timeout=timeout_seconds):
            return True, f"{ip}:{port}"
    except (OSError, RuntimeError, ValueError) as exc:
        return False, f"{type(exc).__name__}: {exc}"


def connection_failure(error: Any) -> bool:
    text = str(error or "").lower()
    signatures = (
        "grpc",
        "_inactiverpcerror",
        "statuscode.unavailable",
        "socket closed",
        "connection reset",
        "connection refused",
        "failed to connect",
        "timed out",
        "timeout",
        "invalidpassword",
        "cortex properties unobtainable",
    )
    return any(signature in text for signature in signatures)


def numerical_failure_evidence(
    qualification: dict[str, Any], log_paths: tuple[Path, ...] = ()
) -> bool:
    evidence = [str(qualification.get("error") or "")]
    for block in qualification.get("blocks", []):
        evidence.extend(str(item) for item in block.get("gross_gate_failures", []))
    for path in log_paths:
        try:
            # The tail contains Fluent's crash/signal report without loading a
            # potentially very large iteration transcript into memory.
            with path.open("rb") as stream:
                stream.seek(0, os.SEEK_END)
                size = stream.tell()
                stream.seek(max(0, size - 2_000_000))
                evidence.append(stream.read().decode("utf-8", errors="replace"))
        except OSError:
            continue
    text = "\n".join(evidence).lower()
    signatures = (
        "sigsegv",
        "segmentation",
        "floating point",
        "non-finite",
        "nan detected",
        "divergence detected",
        "amg solver divergence",
        "gross transient startup gate failed",
        "gross boundary flux",
        "boundedness failure",
    )
    return any(signature in text for signature in signatures)


def safely_resumable_connection_failure(
    qualification: dict[str, Any], log_paths: tuple[Path, ...] = ()
) -> bool:
    return (
        connection_failure(qualification.get("error"))
        and has_numeric_checkpoint(qualification)
        and not numerical_failure_evidence(qualification, log_paths)
    )


def safely_resumable_guard_timeout(
    exit_code: int,
    qualification: dict[str, Any],
    log_paths: tuple[Path, ...] = (),
) -> bool:
    """Allow a guarded client timeout to restart only from saved case/data."""
    return (
        exit_code == 124
        and qualification.get("status") == "running"
        and has_numeric_checkpoint(qualification)
        and not numerical_failure_evidence(qualification, log_paths)
    )


def zero_flow_ratio_gate_failure(qualification: dict[str, Any]) -> bool:
    error = str(qualification.get("error") or "").lower()
    required = (
        "non-finite steamoutlet_quality_percent=nan",
        "non-finite brineoutlet_liquid_fraction_percent=nan",
    )
    return all(item in error for item in required) and has_numeric_checkpoint(qualification)


def time_step_proof_failure(qualification: dict[str, Any]) -> bool:
    """Recognize only the bounded multi-step early-return recovery case."""
    error = str(qualification.get("error") or "").lower()
    return (
        "time-step proof failed:" in error
        and "expected=" in error
        and "actual=" in error
        and has_numeric_checkpoint(qualification)
    )


def has_numeric_checkpoint(qualification: dict[str, Any]) -> bool:
    for key, pair in (qualification.get("checkpoints") or {}).items():
        try:
            int(key)
        except (TypeError, ValueError):
            continue
        if isinstance(pair, dict) and pair.get("case") and pair.get("data"):
            return True
    return False


def acquire_lock(path: Path) -> TextIO:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError("a setup-07j supervisor already holds this server's writer lock")
    handle.seek(0)
    handle.truncate()
    handle.write(f"pid={os.getpid()} started={timestamp()}\n")
    handle.flush()
    return handle


def wait_for_endpoint(
    server_id: str,
    state: dict[str, Any],
    supervisor_manifest: Path,
    *,
    wait_hours: float,
    poll_seconds: float,
) -> bool:
    deadline = time.monotonic() + max(0.0, wait_hours) * 3600.0
    while True:
        ready, detail = tcp_ready(server_id)
        state.update(
            {
                "status": "waiting_for_fluent" if not ready else "fluent_tcp_ready",
                "last_tcp_check": timestamp(),
                "last_tcp_detail": detail,
                "heartbeat_epoch": time.time(),
            }
        )
        write_json(supervisor_manifest, state)
        if ready:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(max(5.0, poll_seconds))


def run_guarded_child(
    command: list[str],
    log_path: Path,
    state: dict[str, Any],
    supervisor_manifest: Path,
    *,
    stage: str,
    idle_timeout_seconds: float,
    wall_timeout_seconds: float,
) -> int:
    wrapped = [
        PYTHON,
        GUARD_SCRIPT,
        "--idle-timeout-seconds",
        str(idle_timeout_seconds),
        "--wall-timeout-seconds",
        str(wall_timeout_seconds),
        "--log-file",
        str(log_path),
        "--",
        *command,
    ]
    environment = dict(os.environ)
    environment["PYTHONUNBUFFERED"] = "1"
    child = subprocess.Popen(wrapped, cwd=PROJECT_ROOT, env=environment)
    state.update(
        {
            "status": stage,
            "child_pid": child.pid,
            "child_started": timestamp(),
            "heartbeat_epoch": time.time(),
        }
    )
    write_json(supervisor_manifest, state)
    while child.poll() is None:
        state["heartbeat_epoch"] = time.time()
        state["last_heartbeat"] = timestamp()
        write_json(supervisor_manifest, state)
        time.sleep(15.0)
    state["child_exit_code"] = int(child.returncode or 0)
    state["heartbeat_epoch"] = time.time()
    write_json(supervisor_manifest, state)
    return int(child.returncode or 0)


def main() -> int:
    args = parser().parse_args()
    if args.target_steps < 1:
        raise ValueError("--target-steps must be positive")
    if args.connection_retries < 0:
        raise ValueError("--connection-retries cannot be negative")

    run_label = prepare07j.run_label_for_server(args.server_id)
    run_root = prepare07j.local_root_for_server(args.server_id)
    run_root.mkdir(parents=True, exist_ok=True)
    supervisor_manifest = run_root / "supervisor_manifest.json"
    preparation_manifest = run_root / "preparation_manifest.json"
    qualification_manifest = run_root / "qualification_manifest.json"
    try:
        lock_handle = acquire_lock(run_root / "supervisor.lock")
    except RuntimeError as exc:
        print(str(exc), flush=True)
        return 0

    state: dict[str, Any] = {
        "study_id": prepare07j.STUDY_ID,
        "run_label": run_label,
        "server_id": args.server_id,
        "pid": os.getpid(),
        "status": "starting",
        "started": timestamp(),
        "target_steps": args.target_steps,
        "policy": (
            "one locked writer; raw-TCP readiness only; no automatic preparation retry; "
            "checkpoint resume only for recorded connection failures"
        ),
    }
    write_json(supervisor_manifest, state)
    try:
        qualification = load_json(qualification_manifest)
        if (
            qualification.get("status") == "completed"
            and int(qualification.get("time_steps_completed", 0)) >= args.target_steps
        ):
            state.update({"status": "completed", "finished": timestamp()})
            write_json(supervisor_manifest, state)
            return 0

        if not wait_for_endpoint(
            args.server_id,
            state,
            supervisor_manifest,
            wait_hours=args.wait_hours,
            poll_seconds=args.poll_seconds,
        ):
            state.update(
                {
                    "status": "unresolved",
                    "error": "Fluent TCP endpoint did not become ready before the deadline",
                    "finished": timestamp(),
                }
            )
            write_json(supervisor_manifest, state)
            return 1

        preparation = load_json(preparation_manifest)
        if preparation.get("status") != "accepted":
            code = run_guarded_child(
                [PYTHON, PREPARATION_SCRIPT, "--server-id", args.server_id],
                run_root / "supervisor_preparation.log",
                state,
                supervisor_manifest,
                stage="preparing",
                idle_timeout_seconds=900.0,
                wall_timeout_seconds=7200.0,
            )
            preparation = load_json(preparation_manifest)
            if code != 0 or preparation.get("status") != "accepted":
                state.update(
                    {
                        "status": "unresolved",
                        "stage": "preparation",
                        "error": preparation.get(
                            "error", "preparation did not produce an accepted manifest"
                        ),
                        "finished": timestamp(),
                    }
                )
                write_json(supervisor_manifest, state)
                return 1

        resume = False
        qualification = load_json(qualification_manifest)
        if qualification.get("status") == "failed":
            resume = safely_resumable_connection_failure(
                qualification,
                tuple(run_root.glob("supervisor_qualification_attempt*.log")),
            )
            if args.resume_zero_flow_ratio_gate and zero_flow_ratio_gate_failure(
                qualification
            ):
                resume = True
            if args.resume_time_step_proof_gate and time_step_proof_failure(
                qualification
            ):
                resume = True
            if not resume:
                state.update(
                    {
                        "status": "unresolved",
                        "stage": "qualification",
                        "error": (
                            "existing qualification failure is not safely resumable: "
                            f"{qualification.get('error')}"
                        ),
                        "finished": timestamp(),
                    }
                )
                write_json(supervisor_manifest, state)
                return 1

        for attempt in range(args.connection_retries + 1):
            command = [
                PYTHON,
                QUALIFICATION_SCRIPT,
                "--server-id",
                args.server_id,
                "--target-steps",
                str(args.target_steps),
            ]
            if resume:
                command.append("--resume")
            code = run_guarded_child(
                command,
                run_root / f"supervisor_qualification_attempt{attempt + 1}.log",
                state,
                supervisor_manifest,
                stage="qualifying",
                # One physical step normally returns in tens of seconds. A
                # 15-minute silence bounds a wedged client/RPC without
                # interrupting ordinary inner-iteration work.
                idle_timeout_seconds=900.0,
                wall_timeout_seconds=86400.0,
            )
            qualification = load_json(qualification_manifest)
            if (
                code == 0
                and qualification.get("status") == "completed"
                and int(qualification.get("time_steps_completed", 0)) >= args.target_steps
            ):
                state.update(
                    {
                        "status": "completed",
                        "classification": qualification.get("classification"),
                        "time_steps_completed": qualification.get("time_steps_completed"),
                        "finished": timestamp(),
                    }
                )
                write_json(supervisor_manifest, state)
                return 0

            attempt_log = run_root / f"supervisor_qualification_attempt{attempt + 1}.log"
            safe_guard_resume = safely_resumable_guard_timeout(
                code,
                qualification,
                (attempt_log,),
            )
            if safe_guard_resume:
                qualification.update(
                    {
                        "status": "failed",
                        "classification": "diagnostic / interrupted RPC",
                        "error": (
                            "Guarded qualification client idle timeout; no partial "
                            "step credited; resume only from latest numeric checkpoint"
                        ),
                        "failed_epoch": time.time(),
                    }
                )
                write_json(qualification_manifest, qualification)

            safe_connection_resume = safely_resumable_connection_failure(
                qualification,
                (attempt_log,),
            )
            if not (safe_connection_resume or safe_guard_resume) or attempt >= args.connection_retries:
                state.update(
                    {
                        "status": "unresolved",
                        "stage": "qualification",
                        "classification": qualification.get("classification", "diagnostic"),
                        "time_steps_completed": qualification.get("time_steps_completed", 0),
                        "error": qualification.get(
                            "error", f"qualification child exited with code {code}"
                        ),
                        "finished": timestamp(),
                    }
                )
                write_json(supervisor_manifest, state)
                return 1

            resume = True
            state["connection_resumes"] = int(state.get("connection_resumes", 0)) + 1
            if not wait_for_endpoint(
                args.server_id,
                state,
                supervisor_manifest,
                wait_hours=args.wait_hours,
                poll_seconds=args.poll_seconds,
            ):
                state.update(
                    {
                        "status": "unresolved",
                        "error": "Fluent did not return for checkpoint resume",
                        "finished": timestamp(),
                    }
                )
                write_json(supervisor_manifest, state)
                return 1
        return 1
    except KeyboardInterrupt:
        state.update(
            {
                "status": "cancelled",
                "cancelled_by_user": True,
                "cancelled": timestamp(),
                "error": "Supervisor interrupted by user",
            }
        )
        write_json(supervisor_manifest, state)
        return 130
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
