#!/usr/bin/env python3
"""Reusable remote Fluent connection helpers."""

from __future__ import annotations

import argparse
import atexit
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from typing import Any

from pyansys_fluent.bridge import ConnectionDocumentError, read_latest_connection
from pyansys_fluent.common import bool_env

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - local convenience fallback
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False


_LOCAL_FLUENT_PROCESSES: list[subprocess.Popen[str]] = []
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
_DEFAULT_BRIDGE_MAX_AGE_SECONDS = 45.0


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
            return _verify_fluent_session(session)
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


def _health_result_is_unhealthy(result: Any) -> bool:
    if result is None or result is False:
        return True
    normalized = str(result).strip().lower().replace("-", "_").replace(" ", "_")
    if not normalized:
        return True
    return any(
        marker in normalized
        for marker in ("not_serving", "unhealthy", "unavailable", "failed", "error")
    )


def _verify_fluent_session(session: Any) -> Any:
    """Require a responsive gRPC health service and readable Fluent version."""

    health_check = getattr(session, "health_check", None)
    attempts: list[str] = []
    healthy = False
    for method_name in ("is_serving", "check_health", "status"):
        method = getattr(health_check, method_name, None)
        if not callable(method):
            continue
        try:
            result = method()
        except Exception as exc:
            attempts.append(f"{method_name}: {type(exc).__name__}")
            continue
        if _health_result_is_unhealthy(result):
            attempts.append(f"{method_name}: unhealthy")
            continue
        healthy = True
        break
    if not healthy:
        detail = ", ".join(attempts) or "health API unavailable"
        raise RuntimeError(f"Connected Fluent session failed health verification ({detail})")

    get_version = getattr(session, "get_fluent_version", None)
    if not callable(get_version):
        raise RuntimeError("Connected Fluent session does not expose get_fluent_version()")
    try:
        version = get_version()
    except Exception as exc:
        raise RuntimeError("Connected Fluent session failed version verification") from exc
    if version is None or not str(version).strip():
        raise RuntimeError("Connected Fluent session returned an empty Fluent version")
    setattr(session, "_codex_fluent_version", str(version))
    return session


def _bridge_dir_for_suffix(suffix: str) -> str:
    return os.getenv(
        f"FLUENT_BRIDGE_DIR{suffix}",
        os.getenv("FLUENT_BRIDGE_DIR", ""),
    ).strip()


def _bridge_max_age_for_suffix(suffix: str) -> float:
    text = os.getenv(
        f"FLUENT_CONNECTION_MAX_AGE_SECONDS{suffix}",
        os.getenv(
            "FLUENT_CONNECTION_MAX_AGE_SECONDS",
            str(_DEFAULT_BRIDGE_MAX_AGE_SECONDS),
        ),
    ).strip()
    try:
        value = float(text)
    except ValueError as exc:
        raise ValueError("FLUENT_CONNECTION_MAX_AGE_SECONDS must be numeric") from exc
    if value <= 0:
        raise ValueError("FLUENT_CONNECTION_MAX_AGE_SECONDS must be positive")
    return value


def connect(
    server_id: str | int | None = None,
    *,
    minimum_generation: int | None = None,
):
    """Connect and verify Fluent using the current configured connection source.

    When ``FLUENT_BRIDGE_DIR`` is configured, ``latest_connection.json`` is
    reread on every call.  No endpoint or password is cached in this process.
    """

    load_dotenv(_ENV_FILE)
    import ansys.fluent.core as pyfluent

    suffix = env_suffix(server_id)

    bridge_dir = _bridge_dir_for_suffix(suffix)
    server_info = os.getenv(f"FLUENT_SERVER_INFO_FILE{suffix}", "").strip()
    ip = os.getenv(f"FLUENT_IP{suffix}", "").strip()
    port = os.getenv(f"FLUENT_PORT{suffix}", "").strip()
    password = os.getenv(f"FLUENT_PASSWORD{suffix}", "").strip()
    local_exe = os.getenv(f"FLUENT_LOCAL_EXE{suffix}", "").strip()
    allow_remote_host = bool_env(f"FLUENT_ALLOW_REMOTE_HOST{suffix}", bool_env("FLUENT_ALLOW_REMOTE_HOST", True))
    insecure_mode = bool_env(f"FLUENT_INSECURE_MODE{suffix}", bool_env("FLUENT_INSECURE_MODE", False))
    label = suffix or "1"

    common = {
        "allow_remote_host": allow_remote_host,
        "cleanup_on_exit": False,
        "start_transcript": True,
        "insecure_mode": insecure_mode,
    }

    if bridge_dir:
        path = Path(bridge_dir).expanduser()
        if not path.is_absolute():
            raise ValueError(f"FLUENT_BRIDGE_DIR{suffix} must be an absolute path")
        try:
            document = read_latest_connection(
                path,
                max_age_seconds=_bridge_max_age_for_suffix(suffix),
                min_generation=minimum_generation,
            )
        except (OSError, json.JSONDecodeError, ConnectionDocumentError) as exc:
            raise RuntimeError(
                f"No usable current Fluent connection is published in {path}"
            ) from exc
        generation = int(document["generation"])
        host = str(document["host"])
        port_number = int(document["port"])
        print(
            f"Connecting to published Fluent generation {generation} "
            f"at {host}:{port_number}"
        )
        session = pyfluent.connect_to_fluent(
            ip=host,
            port=port_number,
            password=document["password"],
            allow_remote_host=True,
            cleanup_on_exit=False,
            start_transcript=True,
            insecure_mode=insecure_mode,
        )
        session = _verify_fluent_session(session)
        setattr(session, "_codex_connection_generation", generation)
        setattr(session, "_codex_connection_source", str(path / "latest_connection.json"))
        return session

    if server_info:
        path = Path(server_info).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"FLUENT_SERVER_INFO_FILE{suffix} does not exist: {path}")
        print(f"Connecting to Fluent server {label} using server-info file: {path}")
        return _verify_fluent_session(
            pyfluent.connect_to_fluent(server_info_file_name=str(path), **common)
        )

    if not (ip and port and password):
        if local_exe:
            return _launch_local_fluent(
                suffix=suffix,
                insecure_mode=insecure_mode,
            )
        raise RuntimeError(
            f"Missing connection details for Fluent server {label}. Set either "
            f"FLUENT_SERVER_INFO_FILE{suffix} or FLUENT_IP{suffix}, "
            f"FLUENT_PORT{suffix}, and FLUENT_PASSWORD{suffix} in .env. "
            f"Or set FLUENT_LOCAL_EXE{suffix} for local manual launch."
        )

    print(f"Connecting to Fluent server {label} using IP/port: {ip}:{port}")
    return _verify_fluent_session(
        pyfluent.connect_to_fluent(
            ip=ip,
            port=int(port),
            password=password,
            **common,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Connect to one configured Fluent gRPC server and run non-mutating health checks."
    )
    parser.add_argument(
        "--server-id",
        default="1",
        help="Configured Fluent server id to use. Use 1 for FLUENT_IP, 2 for FLUENT_IP2, 3 for FLUENT_IP3, 4 for FLUENT_IP4.",
    )
    return parser
