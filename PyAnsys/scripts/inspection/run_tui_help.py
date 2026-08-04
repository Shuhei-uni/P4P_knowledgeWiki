#!/usr/bin/env python3
"""Run a Fluent TUI help/list command and print its transcript."""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="TUI command string, for example '/define/models/dpm/injections ?'")
    args = parser.parse_args()

    load_dotenv()
    solver = connect()
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        try:
            result = solver.scheme.exec((f'(ti-menu-load-string "{args.command}")',))
            if result is not None:
                print(result)
        except Exception as exc:
            print(f"ERROR: {type(exc).__name__}: {exc}")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
