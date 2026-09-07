#!/usr/bin/env python3
"""Read-only setup-07n Fluent ownership, rank, and remote-file preflight.

The script deliberately does not load a mesh/case, change a setting, iterate,
save, or close Fluent.  It connects with the repository's normal
``cleanup_on_exit=False`` contract and writes one non-overwriting JSON record.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
)
from pyansys_fluent.connection import connect  # noqa: E402


EXPECTED_RANKS = 16


def capture_connected_clients(solver: Any) -> dict[str, Any]:
    """Capture Fluent's read-only connected-client console report."""

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        result = solver.tui.server.print_connected_clients()
        time.sleep(1.0)
        if result is not None:
            print(result)
    raw_report = buffer.getvalue()
    return {
        "command": "/server/print-connected-clients",
        "raw_report": raw_report,
        "nonempty_lines": [line.strip() for line in raw_report.splitlines() if line.strip()],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture a non-mutating setup-07n Fluent preflight record."
    )
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--path", action="append", default=[], help="Exact remote path to test.")
    parser.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return parser


def main() -> int:
    load_dotenv()
    args = build_parser().parse_args()
    output_path = Path(args.output_json).expanduser().resolve()
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite preflight evidence: {output_path}")

    import ansys.fluent.core as pyfluent

    solver = connect(
        server_id=args.server_id,
        tcp_timeout_seconds=args.tcp_timeout_seconds,
        # The read-only TUI/settings reports are delivered through PyFluent's
        # transcript stream.  Disabling it makes the rank/client captures empty.
        start_transcript=True,
    )
    payload: dict[str, Any] = {
        "schema_version": 1,
        "classification": "accepted diagnostic",
        "mutating_actions": [],
        "cleanup_on_exit": False,
        "server_id": str(args.server_id),
        "captured_epoch": time.time(),
        "pyfluent_version": str(getattr(pyfluent, "__version__", "unknown")),
        "health_status": str(solver.health_check.status()),
        "health_check": str(solver.health_check.check_health()),
        "fluent_version": str(solver.get_fluent_version()),
    }
    payload["connected_clients"] = capture_connected_clients(solver)
    payload["live_parallel_runtime"] = require_live_compute_node_count(
        solver, EXPECTED_RANKS
    )
    payload["remote_files"] = {
        path_text: remote_file_exists(solver, path_text) for path_text in args.path
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    print(f"preflight_record: {output_path}")
    print(f"server_id: {args.server_id}")
    print(f"health_status: {payload['health_status']}")
    print(f"fluent_version: {payload['fluent_version']}")
    print(f"compute_node_count: {payload['live_parallel_runtime']['compute_node_count']}")
    for path_text, exists in payload["remote_files"].items():
        print(f"remote_file_{'found' if exists else 'missing'}: {path_text}")
    print("This script did not change or close Fluent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
