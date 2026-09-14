#!/usr/bin/env python3
"""Recover Phase-07 treatment report histories from manifest-declared paths.

This is deliberately read-only with respect to the Fluent case.  It connects
to an existing session only to use Fluent's Scheme file reader, then parses
the exact report-file paths recorded by the treatment manifest into a portable
local JSON artifact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

from extract_report_plot_histories import parse_report_forms  # noqa: E402


def read_remote_forms(solver: Any, path: str) -> Any:
    escaped = quote_scheme_string(path)
    expression = (
        f'(with-input-from-file "{escaped}" '
        "(lambda () (let loop ((x (read)) (out (quote ()))) "
        "(if (eof-object? x) (reverse out) (loop (read) (cons x out))))))"
    )
    return solver.scheme.eval(expression)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    # A continuation may have to redirect inherited Report File definitions
    # after a save/reopen.  Prefer the paths actually used for the solve while
    # retaining compatibility with older manifests.
    report_files = (
        manifest.get("report_files_used_for_solve")
        or manifest.get("report_files_after_reopen")
        or manifest.get("report_files")
    )
    if not isinstance(report_files, dict) or not report_files:
        raise RuntimeError("manifest has no report_files mapping")

    solver = connect(server_id=args.server_id, start_transcript=False)
    reports: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, str]] = []
    for monitor_name, raw_path in report_files.items():
        path = str(raw_path)
        try:
            if not remote_file_exists(solver, path):
                raise FileNotFoundError(path)
            record = parse_report_forms(read_remote_forms(solver, path))
            record.update(
                {
                    "monitor_name": monitor_name,
                    "resolved_file_name": path,
                    "setup_id": manifest.get("setup_id"),
                }
            )
            reports[monitor_name] = record
            print(f"{monitor_name}: {record['points']} points", flush=True)
        except Exception as exc:
            errors.append(
                {
                    "monitor_name": monitor_name,
                    "path": path,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            print(f"{monitor_name}: FAILED {type(exc).__name__}: {exc}", flush=True)

    payload = {
        "kind": "phase07_treatment_report_histories",
        "setup_id": manifest.get("setup_id"),
        "run_id": manifest.get("run_id"),
        "server_id": args.server_id,
        "manifest": str(args.manifest),
        "report_count": len(reports),
        "errors": errors,
        "reports": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(reports)} report histories to {args.output}")
    return 0 if reports and not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
