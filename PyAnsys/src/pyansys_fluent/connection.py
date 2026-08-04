#!/usr/bin/env python3
"""Reusable remote Fluent connection helpers."""

from __future__ import annotations

import argparse
import os
import socket
from pathlib import Path

from pyansys_fluent.common import bool_env

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - local convenience fallback
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False


def env_suffix(server_id: str | int | None) -> str:
    if server_id in (None, "", 1, "1"):
        return ""
    return str(server_id).strip()


def float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return float(value)


def tcp_preflight(ip: str, port: int, timeout_seconds: float) -> None:
    if timeout_seconds <= 0:
        return
    try:
        with socket.create_connection((ip, port), timeout=timeout_seconds):
            return
    except OSError as exc:
        raise TimeoutError(
            f"TCP preflight failed for {ip}:{port} after {timeout_seconds:.1f}s. "
            "Check that Fluent is still running, the gRPC port is current, and the "
            "Windows firewall allows inbound TCP on that port."
        ) from exc


def connect(server_id: str | int | None = None, *, tcp_timeout_seconds: float | None = None):
    load_dotenv()
    import ansys.fluent.core as pyfluent

    suffix = env_suffix(server_id)

    server_info = os.getenv(f"FLUENT_SERVER_INFO_FILE{suffix}", "").strip()
    ip = os.getenv(f"FLUENT_IP{suffix}", "").strip()
    port = os.getenv(f"FLUENT_PORT{suffix}", "").strip()
    password = os.getenv(f"FLUENT_PASSWORD{suffix}", "").strip()
    allow_remote_host = bool_env(f"FLUENT_ALLOW_REMOTE_HOST{suffix}", bool_env("FLUENT_ALLOW_REMOTE_HOST", True))
    insecure_mode = bool_env(f"FLUENT_INSECURE_MODE{suffix}", bool_env("FLUENT_INSECURE_MODE", False))
    if tcp_timeout_seconds is None:
        tcp_timeout_seconds = float_env(
            f"FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS{suffix}",
            float_env("FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS", 5.0),
        )
    label = suffix or "1"

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
        raise RuntimeError(
            f"Missing connection details for Fluent server {label}. Set either "
            f"FLUENT_SERVER_INFO_FILE{suffix} or FLUENT_IP{suffix}, "
            f"FLUENT_PORT{suffix}, and FLUENT_PASSWORD{suffix} in .env."
        )

    print(f"Connecting to Fluent server {label} using IP/port: {ip}:{port}")
    tcp_preflight(ip, int(port), tcp_timeout_seconds)
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
        help="Configured Fluent server id to use. Use 1 for FLUENT_IP, 2 for FLUENT_IP2, 3 for FLUENT_IP3.",
    )
    parser.add_argument(
        "--tcp-timeout-seconds",
        type=float,
        default=None,
        help=(
            "TCP preflight timeout before connecting. Default reads "
            "FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS or uses 5 seconds. Use 0 to disable."
        ),
    )
    return parser
