#!/usr/bin/env python3
"""Deterministically verify P6-S6-H's declared remote final case/data pair."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.connection import connect


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--final-case", required=True)
    parser.add_argument("--final-data", required=True)
    args = parser.parse_args()
    solver = connect(server_id=args.server_id, start_transcript=False)
    checks = {
        "final_case": remote_file_exists(solver, args.final_case),
        "final_data": remote_file_exists(solver, args.final_data),
    }
    print(checks)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
