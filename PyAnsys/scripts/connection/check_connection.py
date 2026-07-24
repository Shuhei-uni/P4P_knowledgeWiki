#!/usr/bin/env python3
"""Connect to an already-running remote Fluent session.

This is the script to run when you are at/near the Fluent PC and have started
Fluent's gRPC server.

It uses a local `FLUENT_SERVER_INFO_FILE{N}` or launches local Fluent through
`FLUENT_LOCAL_EXE{N}`. Run it on the same Windows computer as Fluent.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import build_parser, connect  # noqa: E402


def _normalize_server_id(value: str) -> str:
    normalized = value.strip().lower()
    if normalized.startswith("ip"):
        normalized = normalized[2:]
    return normalized or "1"


def main() -> int:
    args = build_parser().parse_args()
    server_id = _normalize_server_id(str(args.server_id))
    print(f"Using Fluent server id: {server_id}")
    solver = connect(server_id=server_id)

    print("\nConnected to Fluent.")

    # Different PyFluent versions expose health checks slightly differently,
    # so try a few non-mutating ways.
    try:
        print("Health status:", solver.health_check.status())
    except Exception as exc:
        print("Health status method not available:", exc)

    try:
        print("Health check:", solver.health_check.check_health())
    except Exception as exc:
        print("Health check method not available:", exc)

    try:
        print("Fluent version:", solver.get_fluent_version())
    except Exception as exc:
        print("Version check failed:", exc)

    print("\nDone. This script did not close Fluent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
