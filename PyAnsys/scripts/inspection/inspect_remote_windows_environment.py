#!/usr/bin/env python3
"""Read-only Windows environment and exact-file discovery through Fluent."""

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


def quote_scheme(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--filename", default="brine-outlet-620kcell.msh.h5")
    result.add_argument(
        "--read-existing",
        action="store_true",
        help="Read the existing scratch result without launching another Windows scan.",
    )
    return result


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    args = parser().parse_args()
    solver = connect(server_id=args.server_id)

    scratch = r"C:\Users\Public\Documents\codex_remote_environment.txt"
    filename = args.filename.replace("'", "''")
    output = scratch.replace("'", "''")
    powershell = (
        "powershell -NoProfile -ExecutionPolicy Bypass -Command "
        '"$lines = @(); '
        "$lines += ('USERNAME=' + $env:USERNAME); "
        "$lines += ('USERPROFILE=' + $env:USERPROFILE); "
        "$lines += ('HOMEDRIVE=' + $env:HOMEDRIVE); "
        "$lines += ('PWD=' + (Get-Location).Path); "
        "$lines += 'USERS='; "
        "$lines += (Get-ChildItem -Path 'C:\\Users' -Directory -ErrorAction SilentlyContinue | ForEach-Object {$_.FullName}); "
        "$lines += 'DRIVES='; "
        "$drives = Get-PSDrive -PSProvider FileSystem | ForEach-Object {$_.Root}; "
        "$lines += $drives; "
        "$lines += 'MATCHES='; "
        f"foreach ($drive in $drives) {{ $lines += (Get-ChildItem -Path ($drive + 'Users\\*') -Recurse -File -Filter '{filename}' -ErrorAction SilentlyContinue | ForEach-Object {{$_.FullName}}) }}; "
        f"$lines | Out-File -Encoding ascii -FilePath '{output}'"
        '"'
    )
    if not args.read_existing:
        status = solver.scheme.eval(f'(system "{quote_scheme(powershell)}")')
        print(f"remote_environment_command_status: {status}")
    text = sweep.remote_text_read_best_effort(solver, scratch).strip()
    print(text or "Remote environment output was empty.")
    print("inspection_complete: no Fluent settings or calculations were changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
