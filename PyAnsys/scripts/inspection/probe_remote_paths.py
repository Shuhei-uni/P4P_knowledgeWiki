#!/usr/bin/env python3
"""Probe configured Fluent-PC paths without modifying the case."""

from __future__ import annotations

import os
import sys
from pathlib import Path, PureWindowsPath

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import build_parser, connect  # noqa: E402


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


def check_remote_path(solver, label: str, path_text: str) -> bool:
    print(f"\n{label}={path_text}")
    try:
        exists = remote_file_exists(solver, path_text)
        status = "FOUND" if exists else "NOT FOUND"
        print(f"[{status}] {path_text}")
        return exists
    except Exception as exc:
        print(f"[ERROR] Could not check remote path: {exc}")
        return False


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.description = "Check absolute PC paths through Fluent without changing its state."
    parser.add_argument(
        "--path", action="append", default=[],
        help="Absolute Fluent-PC file or folder to check; repeat as needed. Overrides .env paths.",
    )
    args = parser.parse_args(argv)
    load_dotenv(PROJECT_ROOT / ".env")
    if args.path:
        configured = [(f"PATH_{i}", path.strip()) for i, path in enumerate(args.path, 1)]
    else:
        paths = [(name, os.getenv(name, "").strip()) for name in PATH_ENV_VARS]
        configured = [(name, path) for name, path in paths if path]

    if not configured:
        print("No remote Fluent paths configured in .env.")
        print("Set FLUENT_REMOTE_PROJECT_DIR and related variables, or supply --path.")
        return 2

    for label, path in configured:
        if not (path.startswith("/") or PureWindowsPath(path).is_absolute()):
            print(f"[ERROR] {label} must be an absolute Fluent-PC path: {path!r}")
            return 2

    try:
        solver = connect(server_id=args.server_id, start_transcript=False, tcp_timeout_seconds=5)
    except Exception as exc:
        print(f"[ERROR] Connection failed: {type(exc).__name__}: {exc}")
        return 2
    print(f"\nConnected to server {args.server_id}. Probing paths without modifying Fluent...")

    found = True
    for name, path in configured:
        found = check_remote_path(solver, name, path) and found

    print("\nPath probe finished. Existence only; file contents and output write access are unverified.")
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
