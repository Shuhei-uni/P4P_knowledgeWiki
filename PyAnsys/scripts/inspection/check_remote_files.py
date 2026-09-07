#!/usr/bin/env python3
"""Check exact file paths on the remote Fluent machine.

This is intentionally read-only: it connects to the running Fluent session and
uses Scheme's file-exists? on the Windows side.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check remote Fluent-PC file existence.")
    parser.add_argument("paths", nargs="+", help="Exact Windows paths to check.")
    parser.add_argument(
        "--server-id",
        default=None,
        help="Configured Fluent server id to use, matching FLUENT_IP{N}/PORT{N}/PASSWORD{N}.",
    )
    parser.add_argument(
        "--tcp-timeout-seconds",
        type=float,
        default=None,
        help="Optional TCP preflight timeout before connecting.",
    )
    return parser


def main() -> int:
    load_dotenv()
    args = build_parser().parse_args()
    solver = connect(server_id=args.server_id, tcp_timeout_seconds=args.tcp_timeout_seconds)

    missing = 0
    for path_text in args.paths:
        exists = remote_file_exists(solver, path_text)
        status = "FOUND" if exists else "MISSING"
        if not exists:
            missing += 1
        print(f"{status}: {path_text}", flush=True)

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
