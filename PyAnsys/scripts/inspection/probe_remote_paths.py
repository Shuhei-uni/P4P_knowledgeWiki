#!/usr/bin/env python3
"""Probe configured Fluent-PC paths without modifying the case."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


PATH_ENV_VARS = [
    "FLUENT_REMOTE_PROJECT_DIR",
    "FLUENT_REMOTE_CASE_DATA_DIR",
    "FLUENT_REMOTE_GEOM_DIR",
    "FLUENT_REMOTE_MESH_DIR",
    "FLUENT_REMOTE_CASE_FILE",
    "FLUENT_REMOTE_DATA_FILE",
    "FLUENT_REMOTE_GEOM_FILE",
    "FLUENT_REMOTE_MESH_FILE",
]


def check_remote_path(solver, label: str, path_text: str) -> None:
    print(f"\n{label}={path_text}")
    try:
        quoted_path = path_text.replace("\\", "\\\\").replace('"', '\\"')
        exists = solver.scheme.eval(f'(file-exists? "{quoted_path}")')
        status = "FOUND" if exists else "NOT FOUND"
        print(f"[{status}] {path_text}")
    except Exception as exc:
        print(f"[ERROR] Could not check remote path: {exc}")


def main() -> int:
    load_dotenv()
    paths = [(name, os.getenv(name, "").strip()) for name in PATH_ENV_VARS]
    configured = [(name, path) for name, path in paths if path]

    if not configured:
        print("No remote Fluent paths configured in .env.")
        print("Set FLUENT_REMOTE_PROJECT_DIR and related folder variables first.")
        return 2

    solver = connect()
    print("\nConnected. Probing Fluent-PC paths without modifying the case...")

    for name, path in configured:
        check_remote_path(solver, name, path)

    project_dir = os.getenv("FLUENT_REMOTE_PROJECT_DIR", "").strip()
    if project_dir:
        server_info_path = project_dir.rstrip("\\/") + r"\server_info.txt"
        check_remote_path(solver, "FLUENT_REMOTE_SERVER_INFO_FILE", server_info_path)

    print("\nPath probe finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
