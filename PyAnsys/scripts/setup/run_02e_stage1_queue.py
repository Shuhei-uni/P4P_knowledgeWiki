#!/usr/bin/env python3
"""Submit the Setup 02e Stage-1 Fluent-native 500-iteration queue.

This launcher only renders and submits a Fluent journal.  The solve loop is
owned by Fluent's native ``/solve/iterate 500`` command for every independent
child; Python never iterates solver steps.
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

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


REMOTE_DIR = PureWindowsPath(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet")


def posix(path: PureWindowsPath | str) -> str:
    return str(path).replace("\\", "/")


def scheme_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def endpoint(case_path: str, queue_stamp: str) -> tuple[str, str, str]:
    source = PureWindowsPath(case_path)
    stem = source.name[:-7]  # remove .cas.h5
    root = source.parent / f"{stem.replace('-pre-run-', '-')}-stage1-iter500-{queue_stamp}"
    case = str(PureWindowsPath(str(root) + ".cas.h5"))
    data = str(PureWindowsPath(str(root) + ".dat.h5"))
    transcript = str(PureWindowsPath(str(root) + ".trn"))
    return case, data, transcript


def render_journal(children: list[dict[str, Any]], queue_stamp: str) -> tuple[str, list[dict[str, Any]]]:
    lines = [
        f"; Setup 02e Stage-1 native queue: {queue_stamp}",
        "; Each child is a paired, initialized Y010 case/data artifact.",
        "; Each child executes exactly one Fluent-native /solve/iterate 500 command.",
        "; Residual auto-stop is disabled in the frozen setup; this queue is supervised externally.",
        "/file/confirm-overwrite? no",
    ]
    outputs: list[dict[str, Any]] = []
    for child in children:
        case, data, transcript = endpoint(child["pre_run_case"], queue_stamp)
        outputs.append({"case_id": child["case_id"], "family": child["family"], "control": child["control"], "pre_run_case": child["pre_run_case"], "pre_run_data": child["pre_run_data"], "endpoint_case": case, "endpoint_data": data, "transcript": transcript})
        lines.extend(
            [
                f"; BEGIN {child['case_id']}",
                f"/file/read-case-data \"{posix(child['pre_run_case'])}\"",
                "/solve/monitors/residual/print? yes",
                f"/file/start-transcript \"{posix(transcript)}\"",
                "/solve/iterate 500",
                f"/file/write-case-data \"{posix(case)}\"",
                "/file/stop-transcript",
                f"; END {child['case_id']}",
            ]
        )
    lines.append("; Stage-1 queue complete; Fluent remains open.")
    return "\n".join(lines) + "\n", outputs


def write_remote_journal(solver: Any, remote_journal: str, journal: str) -> None:
    body = " ".join(f'(display "{scheme_string(line)}") (newline)' for line in journal.splitlines())
    expression = f'(with-output-to-file "{scheme_string(posix(remote_journal))}" (lambda () {body}))'
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, remote_journal):
        raise RuntimeError(f"Remote journal was not created: {remote_journal}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--build-snapshot", type=Path, required=True)
    parser.add_argument("--queue-stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--local-journal", type=Path, required=True)
    parser.add_argument("--skip-case", action="append", default=[], help="Case ID to exclude after a recorded native failure; repeat as needed.")
    args = parser.parse_args()

    snapshot = json.loads(args.build_snapshot.expanduser().resolve().read_text(encoding="utf-8"))
    skipped = set(args.skip_case)
    children = [child for child in snapshot["children"] if child["case_id"] not in skipped]
    if not children:
        raise ValueError("No Stage-1 children remain after exclusions")
    journal, outputs = render_journal(children, args.queue_stamp)
    args.local_journal.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    args.local_journal.expanduser().resolve().write_text(journal, encoding="utf-8", newline="\n")

    solver = connect(server_id=args.server_id)
    remote_journal = str(REMOTE_DIR / f"02e-Stage1-native-queue-{args.queue_stamp}.jou")
    if remote_file_exists(solver, remote_journal):
        raise FileExistsError(f"Refusing to overwrite remote journal: {remote_journal}")
    for child in children:
        for path in (child["pre_run_case"], child["pre_run_data"]):
            if not remote_file_exists(solver, path):
                raise FileNotFoundError(f"Missing paired Stage-1 input: {path}")
    for item in outputs:
        for path in (item["endpoint_case"], item["endpoint_data"], item["transcript"]):
            if remote_file_exists(solver, path):
                raise FileExistsError(f"Refusing to overwrite Stage-1 queue artifact: {path}")

    # A Fluent journal interrupted by a floating-point exception can leave its
    # transcript open.  Close only that stale native I/O state before starting
    # a continuation queue; this does not touch the loaded solution fields.
    try:
        solver.tui.file.stop_transcript()
    except Exception:
        pass
    write_remote_journal(solver, remote_journal, journal)
    solver.settings.file.read_journal(file_name_list=[remote_journal])
    manifest = {
        "queue_stamp": args.queue_stamp,
        "server_id": args.server_id,
        "remote_journal": remote_journal,
        "local_journal": str(args.local_journal.expanduser().resolve()),
        "native_iterations_per_case": 500,
        "submitted_cases": len(outputs),
        "skipped_cases": sorted(skipped),
        "outputs": outputs,
        "fluent_version": solver.get_fluent_version(),
    }
    manifest_path = args.local_journal.expanduser().resolve().with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, default=str))
    print(f"manifest_json: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
