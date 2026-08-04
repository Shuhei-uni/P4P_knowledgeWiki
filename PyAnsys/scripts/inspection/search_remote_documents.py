#!/usr/bin/env python3
"""Search the remote Fluent PC's Documents folder for Fluent input files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


def scheme_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def powershell_quote(value: str) -> str:
    return value.replace("'", "''")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recursively list Fluent case/data/mesh files on the remote PC."
    )
    parser.add_argument(
        "--root",
        default=r"C:\Users\qtra338\Documents",
        help="Remote Windows directory to search.",
    )
    parser.add_argument(
        "--pattern",
        default="",
        help="Optional case-insensitive substring required in the full path.",
    )
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--tcp-timeout-seconds", type=float, default=None)
    return parser


def main() -> int:
    load_dotenv()
    args = build_parser().parse_args()
    solver = connect(
        server_id=args.server_id,
        tcp_timeout_seconds=args.tcp_timeout_seconds,
    )

    scratch = str(Path(args.root) / "_codex_remote_file_search.txt").replace("/", "\\")
    root = powershell_quote(args.root)
    output = powershell_quote(scratch)
    pattern = powershell_quote(args.pattern)
    pattern_filter = (
        f" | Where-Object {{ $_.FullName -like '*{pattern}*' }}" if pattern else ""
    )
    command = (
        "powershell -NoProfile -ExecutionPolicy Bypass -Command "
        f"\"Get-ChildItem -Path '{root}\\*' -Recurse -File "
        "-Include '*.cas','*.cas.h5','*.dat','*.dat.h5','*.msh','*.msh.h5' "
        "-ErrorAction SilentlyContinue"
        f"{pattern_filter} | Sort-Object FullName | ForEach-Object {{ $_.FullName }} "
        f"| Out-File -Encoding ascii -FilePath '{output}'\""
    )
    status = solver.scheme.eval(f'(system "{scheme_quote(command)}")')
    print(f"Remote search command status: {status}", flush=True)
    result = sweep.remote_text_read_best_effort(solver, scratch).strip()
    print(result or "No matching Fluent files found.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
