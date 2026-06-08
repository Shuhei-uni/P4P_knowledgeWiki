#!/usr/bin/env python3
"""Connect to an already-running remote Fluent session.

This is the script to run when you are at/near the Fluent PC and have started
Fluent's gRPC server.

It uses either:
- FLUENT_SERVER_INFO_FILE, or
- FLUENT_IP + FLUENT_PORT + FLUENT_PASSWORD

from a .env file or shell environment.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import ansys.fluent.core as pyfluent


def bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def connect():
    load_dotenv()

    server_info = os.getenv("FLUENT_SERVER_INFO_FILE", "").strip()
    ip = os.getenv("FLUENT_IP", "").strip()
    port = os.getenv("FLUENT_PORT", "").strip()
    password = os.getenv("FLUENT_PASSWORD", "").strip()
    allow_remote_host = bool_env("FLUENT_ALLOW_REMOTE_HOST", True)
    insecure_mode = bool_env("FLUENT_INSECURE_MODE", False)

    common = {
        "allow_remote_host": allow_remote_host,
        "cleanup_on_exit": False,
        "start_transcript": True,
        "insecure_mode": insecure_mode,
    }

    if server_info:
        path = Path(server_info).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"FLUENT_SERVER_INFO_FILE does not exist: {path}")
        print(f"Connecting using server-info file: {path}")
        return pyfluent.connect_to_fluent(server_info_file_name=str(path), **common)

    if not (ip and port and password):
        raise RuntimeError(
            "Missing connection details. Set either FLUENT_SERVER_INFO_FILE "
            "or FLUENT_IP, FLUENT_PORT, and FLUENT_PASSWORD in .env."
        )

    print(f"Connecting using IP/port: {ip}:{port}")
    return pyfluent.connect_to_fluent(
        ip=ip,
        port=int(port),
        password=password,
        **common,
    )


def main() -> int:
    solver = connect()

    print("\nConnected to Fluent.")

    # Different PyFluent versions expose health checks slightly differently,
    # so try a few non-mutating ways.
    try:
        print("Health status:", solver.health_check.status())
    except Exception as exc:
        print("Health status method not available:", exc)

    try:
        print("Health check:", solver.health_check.check_health())
    except Exception as exc:
        print("Health check method not available:", exc)

    try:
        print("Fluent version:", solver.get_fluent_version())
    except Exception as exc:
        print("Version check failed:", exc)

    print("\nDone. This script did not close Fluent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
