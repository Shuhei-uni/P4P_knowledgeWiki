#!/usr/bin/env python3
"""Submit one Setup 02e Stage-2 native 500-iteration journal.

Each invocation owns one Fluent-native ``/solve/iterate 500`` command.  The
separate invocation boundary is intentional: a floating-point exception in
one child must not prevent the remaining independently initialized children
from being attempted.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, quote_scheme_string  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


REMOTE_DIR = PureWindowsPath(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet")


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def endpoint(pre_run_case: str, stamp: str) -> tuple[str, str, str]:
    source = PureWindowsPath(pre_run_case)
    stem = source.name[:-7]
    root = source.parent / f"{stem}-stage2-iter500-{stamp}"
    return str(PureWindowsPath(str(root) + ".cas.h5")), str(PureWindowsPath(str(root) + ".dat.h5")), str(PureWindowsPath(str(root) + ".trn"))


def render_journal(pre_run_case: str, endpoint_case: str, endpoint_data: str, transcript: str, stamp: str) -> str:
    return "\n".join(
        [
            f"; Setup 02e Stage-2 native case journal: {stamp}",
            "; Fluent owns this single 500-iteration solve; Python does not iterate.",
            "/file/confirm-overwrite? no",
            f'/file/read-case-data "{posix(pre_run_case)}"',
            "/solve/monitors/residual/print? yes",
            f'/file/start-transcript "{posix(transcript)}"',
            "/solve/iterate 500",
            f'/file/write-case-data "{posix(endpoint_case)}"',
            "/file/stop-transcript",
            "; Stage-2 native case journal finished; Fluent remains open.",
            "",
        ]
    )


def write_remote_journal(solver: Any, remote_journal: str, journal: str) -> None:
    body = " ".join(f'(display "{quote_scheme_string(line)}") (newline)' for line in journal.splitlines())
    expression = f'(with-output-to-file "{quote_scheme_string(posix(remote_journal))}" (lambda () {body}))'
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, remote_journal):
        raise RuntimeError(f"Remote journal was not created: {remote_journal}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--build-snapshot", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--queue-stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--local-journal", type=Path, required=True)
    args = parser.parse_args()

    snapshot = json.loads(args.build_snapshot.expanduser().resolve().read_text(encoding="utf-8"))
    matching = [child for child in snapshot["children"] if child["case_id"] == args.case_id]
    if len(matching) != 1:
        raise ValueError(f"Expected one child matching {args.case_id!r}; found {len(matching)}")
    child = matching[0]
    endpoint_case, endpoint_data, transcript = endpoint(child["pre_run_case"], args.queue_stamp)
    remote_journal = str(REMOTE_DIR / f"02e-Stage2-native-{args.case_id}-{args.queue_stamp}.jou")
    args.local_journal.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    journal = render_journal(child["pre_run_case"], endpoint_case, endpoint_data, transcript, args.queue_stamp)
    args.local_journal.expanduser().resolve().write_text(journal, encoding="utf-8", newline="\n")

    solver = connect(server_id=args.server_id)
    for path in (child["pre_run_case"], child["pre_run_data"]):
        if not remote_file_exists(solver, path):
            raise FileNotFoundError(f"Missing paired Stage-2 input: {path}")
    if remote_file_exists(solver, remote_journal):
        raise FileExistsError(f"Refusing to overwrite remote journal: {remote_journal}")
    for path in (endpoint_case, endpoint_data, transcript):
        if remote_file_exists(solver, path):
            raise FileExistsError(f"Refusing to overwrite Stage-2 output: {path}")

    try:
        solver.tui.file.stop_transcript()
    except Exception:
        pass
    write_remote_journal(solver, remote_journal, journal)
    manifest = {
        "case_id": args.case_id,
        "family": child["family"],
        "control": child["control"],
        "queue_stamp": args.queue_stamp,
        "server_id": args.server_id,
        "remote_journal": remote_journal,
        "local_journal": str(args.local_journal.expanduser().resolve()),
        "pre_run_case": child["pre_run_case"],
        "pre_run_data": child["pre_run_data"],
        "endpoint_case": endpoint_case,
        "endpoint_data": endpoint_data,
        "transcript": transcript,
        "native_iterations_requested": 500,
        "fluent_version": solver.get_fluent_version(),
    }
    manifest_path = args.local_journal.expanduser().resolve().with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, default=str), flush=True)
    print(f"manifest_json: {manifest_path}", flush=True)
    solver.settings.file.read_journal(file_name_list=[remote_journal])
    print(f"native_journal_returned: {remote_journal}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
