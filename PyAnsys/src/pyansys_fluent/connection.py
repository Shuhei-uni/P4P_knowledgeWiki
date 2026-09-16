#!/usr/bin/env python3
"""Endpoint resolution for MCP and reviewed deterministic P4P workers.

Connections are attach-only. The MCP owns generic discovery and generated
execution; existing domain workers retain this narrow transport seam.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import socket
import sys

from pyansys_fluent.mcp_policy import SessionPolicyError

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def env_suffix(server_id: str | int | None) -> str:
    if server_id in (None, "", 1, "1"):
        return ""
    return str(server_id).strip()


def endpoint_env_namespace(server_id: str | int | None) -> tuple[str, str, str]:
    normalized = str(server_id or "1").strip().lower()
    if normalized == "student":
        return "student", "STUDENT", ""
    suffix = env_suffix(server_id)
    return suffix or "1", "FLUENT", suffix


def float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None or not value.strip() else float(value)


def tcp_preflight(ip: str, port: int, timeout_seconds: float) -> None:
    if timeout_seconds <= 0:
        return
    try:
        with socket.create_connection((ip, port), timeout=timeout_seconds):
            return
    except OSError as exc:
        raise TimeoutError("Fluent endpoint is unreachable; reconcile the fleet before reconnecting.") from exc


def resolve_connection_kwargs(
    server_id: str | int | None = None,
    *,
    start_transcript: bool | None = True,
    tcp_timeout_seconds: float | None = None,
) -> dict:
    """Resolve existing endpoint configuration without launching or loading Fluent.

    Contains credentials: do not write the returned mapping to logs or evidence.
    Server-info paths are local to the MCP/worker host, not necessarily Fluent.
    """
    load_dotenv(_ENV_FILE)
    label, prefix, suffix = endpoint_env_namespace(server_id)
    key = lambda name: f"{prefix}_{name}{suffix}"
    server_info = os.getenv(key("SERVER_INFO_FILE"), "").strip()
    ip = os.getenv(key("IP"), "").strip()
    port = os.getenv(key("PORT"), "").strip()
    password = os.getenv(key("PASSWORD"), "").strip()
    if start_transcript is None:
        start_transcript = _bool_env(key("STREAM_TRANSCRIPT"), _bool_env("FLUENT_STREAM_TRANSCRIPT", True))
    common = {
        "allow_remote_host": _bool_env(key("ALLOW_REMOTE_HOST"), _bool_env("FLUENT_ALLOW_REMOTE_HOST", True)),
        "cleanup_on_exit": False,
        "start_transcript": start_transcript,
        "insecure_mode": _bool_env(key("INSECURE_MODE"), _bool_env("FLUENT_INSECURE_MODE", False)),
    }
    if server_info:
        path = Path(server_info).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Configured {key('SERVER_INFO_FILE')} is not a file.")
        return {"server_info_file_name": str(path), **common}
    if not (ip and port and password):
        if os.getenv(key("LOCAL_EXE"), "").strip():
            raise SessionPolicyError("Automatic Fluent launch is disabled. Attach to an existing session.")
        raise RuntimeError(
            f"Missing connection details for Fluent server {label}. Set {key('SERVER_INFO_FILE')} "
            f"or {key('IP')}, {key('PORT')}, and {key('PASSWORD')} in PyAnsys/.env."
        )
    port_number = int(port)
    if not 1 <= port_number <= 65535:
        raise ValueError("Fluent port must be between 1 and 65535.")
    if tcp_timeout_seconds is None:
        tcp_timeout_seconds = float_env(key("TCP_PREFLIGHT_TIMEOUT_SECONDS"), float_env("FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS", 0.0))
    tcp_preflight(ip, port_number, tcp_timeout_seconds)
    return {"ip": ip, "port": port_number, "password": password, **common}


def _launch_local_fluent(**_kwargs):
    """Compatibility failure for old launch callers; never start a process."""
    raise SessionPolicyError("Automatic Fluent launch is disabled. Attach to an existing session.")


def connect(server_id: str | int | None = None, *, start_transcript: bool | None = True,
            tcp_timeout_seconds: float | None = None):
    kwargs = resolve_connection_kwargs(server_id, start_transcript=start_transcript,
                                       tcp_timeout_seconds=tcp_timeout_seconds)
    import ansys.fluent.core as pyfluent
    label, _, _ = endpoint_env_namespace(server_id)
    print(f"Attaching to configured Fluent server {label}; session will be preserved.", file=sys.stderr)
    return pyfluent.connect_to_fluent(**kwargs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Attach to an existing Fluent endpoint; never launch or terminate it.")
    parser.add_argument("--server-id", default="1", help="Transport alias: 1, 2, 3, 4, or student. Not case identity.")
    return parser
