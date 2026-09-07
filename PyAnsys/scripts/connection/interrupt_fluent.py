#!/usr/bin/env python3
"""Best-effort interrupt for the connected Fluent solver."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


def main() -> int:
    load_dotenv()
    solver = connect()
    print("connected")
    solver.settings.solution.run_calculation.interrupt()
    print("interrupt_sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
