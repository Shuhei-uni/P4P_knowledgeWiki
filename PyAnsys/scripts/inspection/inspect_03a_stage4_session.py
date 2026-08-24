#!/usr/bin/env python3
"""Inspect one 03A Stage-4 Fluent session without changing solver state.

This transport audit deliberately performs no load, initialization, iteration,
save, interrupt, or shutdown action.  Results are printed only; ``server_id``
is not written into report-facing evidence or artifact names.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import time
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import (  # noqa: E402
    capture_parallel_connectivity_roster,
    remote_file_exists,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.native_run_monitor import collect_snapshot  # noqa: E402


def capture_connected_clients(solver: Any) -> dict[str, Any]:
    """Capture Fluent's read-only connected-client console report."""

    buffer = io.StringIO()
    command = "/server/print-connected-grpc-clients"
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        try:
            result = solver.tui.server.print_connected_grpc_clients()
        except AttributeError:
            command = "/server/print-connected-clients"
            result = solver.tui.server.print_connected_clients()
        time.sleep(1.0)
        if result is not None:
            print(result)
    raw_report = buffer.getvalue()
    return {
        "command": command,
        "raw_report": raw_report,
        "nonempty_lines": [line.strip() for line in raw_report.splitlines() if line.strip()],
    }


def safe_call(label: str, func: Any) -> dict[str, Any]:
    try:
        return {"label": label, "value": func()}
    except Exception as exc:
        return {"label": label, "error": f"{type(exc).__name__}: {exc}"}


def case_identity_probes(solver: Any) -> list[dict[str, Any]]:
    """Probe common read-only case-name variables without assuming one release path."""

    return [
        safe_call(expression, lambda expression=expression: solver.scheme.eval(expression))
        for expression in (
            "(rpgetvar 'case-name)",
            "(rpgetvar 'case-filename)",
            "(rpgetvar 'case-file-name)",
        )
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--path", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    solver = connect(server_id=args.server_id, start_transcript=True)
    first = collect_snapshot(solver, monitor_sets=("residual",))
    time.sleep(3.0)
    second = collect_snapshot(solver, previous_state=first, monitor_sets=("residual",))
    payload = {
        "health_status": str(solver.health_check.status()),
        "health_check": str(solver.health_check.check_health()),
        "is_active": bool(solver.is_active()),
        "fluent_version": str(solver.get_fluent_version()),
        "connected_clients": capture_connected_clients(solver),
        "parallel_runtime": capture_parallel_connectivity_roster(solver),
        "snapshot_first": first,
        "snapshot_second": second,
        "case_identity_probes": case_identity_probes(solver),
        "autosave": safe_get_state(solver.settings.file.auto_save, "native autosave"),
        "report_files": safe_get_state(
            solver.settings.solution.monitor.report_files,
            "report files",
        ),
        "remote_files": {
            path_text: bool(remote_file_exists(solver, path_text))
            for path_text in args.path
        },
        "mutating_actions": [],
        "cleanup_on_exit": False,
    }
    payload["parallel_runtime"].pop("raw_report", None)
    print(json.dumps(payload, indent=2, default=str))
    print("Read-only inspection complete; Fluent was not changed or closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
