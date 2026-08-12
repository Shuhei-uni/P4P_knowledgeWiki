#!/usr/bin/env python3
"""Reusable remote Fluent connection helpers."""

from __future__ import annotations

import argparse
import atexit
import os
from pathlib import Path
import subprocess
import tempfile
import time

from pyansys_fluent.common import bool_env

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - local convenience fallback
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False


_LOCAL_FLUENT_PROCESSES: list[subprocess.Popen[str]] = []
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def _cleanup_local_fluent_processes() -> None:
    for process in list(_LOCAL_FLUENT_PROCESSES):
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
        except Exception:
            pass


atexit.register(_cleanup_local_fluent_processes)


def env_suffix(server_id: str | int | None) -> str:
    if server_id in (None, "", 1, "1"):
        return ""
    return str(server_id).strip()


def endpoint_env_namespace(server_id: str | int | None) -> tuple[str, str, str]:
    """Return display label, environment prefix, and numeric suffix for an endpoint.

    ``student`` is a named routing alias for the Windows Student Edition pool.
    It reads ``STUDENT_*`` variables directly, while all existing numeric aliases
    retain their ``FLUENT_*`` variable names and suffixes.
    """

    normalized = str(server_id or "1").strip().lower()
    if normalized == "student":
        return "student", "STUDENT", ""
    suffix = env_suffix(server_id)
    return suffix or "1", "FLUENT", suffix


def _launch_local_fluent(
    *,
    suffix: str,
    insecure_mode: bool,
):
    import ansys.fluent.core as pyfluent

    exe = os.getenv(f"FLUENT_LOCAL_EXE{suffix}", "").strip()
    if not exe:
        raise RuntimeError("Local Fluent launch requested without FLUENT_LOCAL_EXE configured.")

    dimension = os.getenv(f"FLUENT_LOCAL_DIMENSION{suffix}", os.getenv("FLUENT_LOCAL_DIMENSION", "3")).strip() or "3"
    precision = os.getenv(f"FLUENT_LOCAL_PRECISION{suffix}", os.getenv("FLUENT_LOCAL_PRECISION", "double")).strip() or "double"
    processor_count = int(
        os.getenv(
            f"FLUENT_LOCAL_PROCESSOR_COUNT{suffix}",
            os.getenv("FLUENT_LOCAL_PROCESSOR_COUNT", "2"),
        ).strip()
        or "2"
    )
    gui = bool_env(f"FLUENT_LOCAL_GUI{suffix}", bool_env("FLUENT_LOCAL_GUI", False))
    startup_timeout = int(
        os.getenv(
            f"FLUENT_LOCAL_STARTUP_TIMEOUT{suffix}",
            os.getenv("FLUENT_LOCAL_STARTUP_TIMEOUT", "120"),
        ).strip()
        or "120"
    )

    output_dir = Path(
        os.getenv(
            f"FLUENT_LOCAL_OUTPUT_DIR{suffix}",
            os.getenv("FLUENT_LOCAL_OUTPUT_DIR", tempfile.gettempdir()),
        )
    ).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    server_info = output_dir / f"serverinfo-local{suffix or '1'}.txt"
    stdout_log = output_dir / f"fluent-local{suffix or '1'}-stdout.log"
    stderr_log = output_dir / f"fluent-local{suffix or '1'}-stderr.log"
    if server_info.exists():
        server_info.unlink()

    launch_args = [
        exe,
        f"{dimension}ddp",
        f"-t{processor_count}",
    ]
    if not gui:
        launch_args.append("-g")
    launch_args.append(f"-sifile={server_info}")

    print(f"Launching local Fluent {suffix or '1'} via executable: {exe}")
    print(f"Local Fluent args: {launch_args}")

    process = subprocess.Popen(
        launch_args,
        stdin=subprocess.PIPE,
        stdout=stdout_log.open("w", encoding="utf-8", errors="replace"),
        stderr=stderr_log.open("w", encoding="utf-8", errors="replace"),
        cwd=str(output_dir),
        text=True,
    )
    _LOCAL_FLUENT_PROCESSES.append(process)

    deadline = time.time() + startup_timeout
    while time.time() < deadline:
        if server_info.exists() and server_info.stat().st_size > 0:
            print(f"Local Fluent server-info ready: {server_info}")
            session = pyfluent.connect_to_fluent(
                server_info_file_name=str(server_info),
                allow_remote_host=False,
                cleanup_on_exit=False,
                start_transcript=True,
                insecure_mode=insecure_mode,
            )
            setattr(session, "_codex_local_fluent_process", process)
            setattr(session, "_codex_local_fluent_server_info", str(server_info))
            setattr(session, "_codex_local_fluent_stdout_log", str(stdout_log))
            setattr(session, "_codex_local_fluent_stderr_log", str(stderr_log))
            return session
        if process.poll() is not None:
            raise RuntimeError(
                f"Local Fluent exited early with code {process.returncode}. "
                f"stdout={stdout_log} stderr={stderr_log}"
            )
        time.sleep(2)

    raise TimeoutError(
        f"Timed out waiting for local Fluent server-info file: {server_info}. "
        f"stdout={stdout_log} stderr={stderr_log}"
    )


def connect(server_id: str | int | None = None):
    load_dotenv(_ENV_FILE)
    import ansys.fluent.core as pyfluent

    label, env_prefix, suffix = endpoint_env_namespace(server_id)
    server_info_key = f"{env_prefix}_SERVER_INFO_FILE{suffix}"
    ip_key = f"{env_prefix}_IP{suffix}"
    port_key = f"{env_prefix}_PORT{suffix}"
    password_key = f"{env_prefix}_PASSWORD{suffix}"
    local_exe_key = f"{env_prefix}_LOCAL_EXE{suffix}"
    allow_remote_host_key = f"{env_prefix}_ALLOW_REMOTE_HOST{suffix}"
    insecure_mode_key = f"{env_prefix}_INSECURE_MODE{suffix}"

    server_info = os.getenv(server_info_key, "").strip()
    ip = os.getenv(ip_key, "").strip()
    port = os.getenv(port_key, "").strip()
    password = os.getenv(password_key, "").strip()
    local_exe = os.getenv(local_exe_key, "").strip()
    allow_remote_host = bool_env(
        allow_remote_host_key,
        bool_env("FLUENT_ALLOW_REMOTE_HOST", True),
    )
    insecure_mode = bool_env(
        insecure_mode_key,
        bool_env("FLUENT_INSECURE_MODE", False),
    )

    common = {
        "allow_remote_host": allow_remote_host,
        "cleanup_on_exit": False,
        "start_transcript": True,
        "insecure_mode": insecure_mode,
    }

    if server_info:
        path = Path(server_info).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"FLUENT_SERVER_INFO_FILE{suffix} does not exist: {path}")
        print(f"Connecting to Fluent server {label} using server-info file: {path}")
        return pyfluent.connect_to_fluent(server_info_file_name=str(path), **common)

    if not (ip and port and password):
        if local_exe:
            if env_prefix != "FLUENT":
                raise RuntimeError(
                    f"Local launch is not supported for the named {label!r} endpoint. "
                    "Use a numbered FLUENT_* endpoint for FLUENT_LOCAL_EXE."
                )
            return _launch_local_fluent(
                suffix=suffix,
                insecure_mode=insecure_mode,
            )
        local_launch_note = (
            f" Or set {local_exe_key} for local manual launch."
            if env_prefix == "FLUENT"
            else ""
        )
        raise RuntimeError(
            f"Missing connection details for Fluent server {label}. Set either "
            f"{server_info_key} or {ip_key}, {port_key}, and {password_key} in .env."
            f"{local_launch_note}"
        )

    print(f"Connecting to Fluent server {label} using IP/port: {ip}:{port}")
    return pyfluent.connect_to_fluent(
        ip=ip,
        port=int(port),
        password=password,
        **common,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Connect to one configured Fluent gRPC server and run non-mutating health checks."
    )
    parser.add_argument(
        "--server-id",
        default="1",
        help=(
            "Connection alias selecting the configured Fluent endpoint. "
            "It does not identify the case loaded in that session. "
            "Use 1 for FLUENT_IP, 2 for FLUENT_IP2, 3 for FLUENT_IP3, "
            "4 for FLUENT_IP4, or student for STUDENT_IP."
        ),
    )
    return parser
