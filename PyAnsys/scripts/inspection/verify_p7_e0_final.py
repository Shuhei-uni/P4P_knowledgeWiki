#!/usr/bin/env python3
"""Reopen and verify the Phase 07 E0 terminal pair on an existing Fluent server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from run_p7_e0_ref_discovery import verify_setup  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    solver = connect(server_id=args.server_id, start_transcript=False)
    if not remote_file_exists(solver, args.case):
        raise FileNotFoundError(args.case)
    if not remote_file_exists(solver, args.data):
        raise FileNotFoundError(args.data)
    solver.settings.file.read_case(file_name=args.case)
    solver.settings.file.read_data(file_name=args.data)
    payload = {
        "status": "PASS",
        "server_id": args.server_id,
        "case": args.case,
        "data": args.data,
        "setup_readback": verify_setup(solver),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
