#!/usr/bin/env python3
"""Load the configured Fluent case/data files from the remote Fluent PC.

This changes the active Fluent session. It does not run iterations.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import PureWindowsPath
from pathlib import Path

from dotenv import load_dotenv

# Allow importing check_connection.py from the same folder.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_connection import connect  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load FLUENT_REMOTE_CASE_FILE and optionally FLUENT_REMOTE_DATA_FILE."
    )
    parser.add_argument(
        "--case-only",
        action="store_true",
        help="Read only the case file, not the data file.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm that replacing the active Fluent session is intentional.",
    )
    return parser


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required .env value: {name}")
    return value


def file_exists(solver, path_text: str) -> bool:
    quoted_path = path_text.replace("\\", "\\\\").replace('"', '\\"')
    return bool(solver.scheme.eval(f'(file-exists? "{quoted_path}")'))


def chdir_remote(solver, path_text: str) -> None:
    quoted_path = path_text.replace("\\", "\\\\").replace('"', '\\"')
    solver.scheme.eval(f'(chdir "{quoted_path}")')


def main() -> int:
    args = build_parser().parse_args()
    if not args.yes:
        print("Refusing to load case/data without --yes.")
        print("Loading a case/data file replaces the active Fluent session state.")
        return 2

    load_dotenv()
    case_file = require_env("FLUENT_REMOTE_CASE_FILE")
    data_file = os.getenv("FLUENT_REMOTE_DATA_FILE", "").strip()
    case_path = PureWindowsPath(case_file)
    case_dir = str(case_path.parent)
    case_name = case_path.name

    solver = connect()
    print("\nConnected. Verifying remote files before loading...")

    if not file_exists(solver, case_file):
        raise FileNotFoundError(f"Fluent cannot see case file: {case_file}")
    print(f"[FOUND] Case file: {case_file}")

    if not args.case_only:
        if not data_file:
            raise RuntimeError("FLUENT_REMOTE_DATA_FILE is empty. Use --case-only or set it in .env.")
        if not file_exists(solver, data_file):
            raise FileNotFoundError(f"Fluent cannot see data file: {data_file}")
        print(f"[FOUND] Data file: {data_file}")

    print(f"\nChanging Fluent working directory to: {case_dir}")
    chdir_remote(solver, case_dir)
    if not file_exists(solver, case_name):
        raise FileNotFoundError(f"Fluent cannot see case file after chdir: {case_name}")

    if args.case_only:
        print("\nReading case file...")
        solver.settings.file.read_case(file_name=case_file)
    else:
        print("\nReading case and data files...")
        expected_data_name = case_name.removesuffix(".cas.h5") + ".dat.h5"
        data_name = PureWindowsPath(data_file).name
        if data_name == expected_data_name:
            solver.settings.file.read_case_data(file_name=case_file)
        else:
            print(
                "Data filename does not match Fluent's default paired case/data name; "
                "reading explicit data file after case load."
            )
            solver.settings.file.read_case(file_name=case_file)
            solver.settings.file.read_data(file_name=data_file)

    print("\nLoad command completed. No iterations were run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
