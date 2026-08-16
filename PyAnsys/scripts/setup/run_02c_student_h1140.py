#!/usr/bin/env python3
"""Submit the single 02c-H Student 1.140 MPa screen as a native Fluent journal."""

from __future__ import annotations

import argparse
from pathlib import Path, PureWindowsPath
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.positive_backpressure_queue import (  # noqa: E402
    NativeQueueJob,
    NativeSequentialQueue,
    render_native_sequential_queue,
)


def scheme_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def write_remote_journal(solver: object, remote_journal: PureWindowsPath, journal: str) -> None:
    body = " ".join(
        f'(display "{scheme_string(line)}") (newline)' for line in journal.splitlines()
    )
    expression = (
        f'(with-output-to-file "{scheme_string(remote_journal.as_posix())}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, str(remote_journal)):
        raise RuntimeError(f"Student did not expose the native journal: {remote_journal}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--preinit-case", required=True)
    parser.add_argument("--queue-stamp", required=True)
    parser.add_argument("--local-journal", type=Path, required=True)
    args = parser.parse_args()

    remote_dir = PureWindowsPath(args.preinit_case).parent
    stem = f"02c-H-brine-p1140kpa-unprimed-student-iter500-{args.queue_stamp}"
    output = remote_dir / f"{stem}.cas.h5"
    data = PureWindowsPath(str(output).replace(".cas.h5", ".dat.h5"))
    residual = remote_dir / f"{stem}-residuals.out"
    remote_journal = remote_dir / f"{stem}.jou"
    transcript = remote_dir / f"{stem}.trn"
    job = NativeQueueJob(
        case_id="02c-H",
        preinit_case=args.preinit_case,
        output_case_data=str(output),
        residual_file=str(residual),
    )
    config = NativeSequentialQueue(
        queue_id=stem,
        transcript_file=str(transcript),
        autosave_root=str(remote_dir / stem),
        jobs=(job,),
        iterations=500,
    )
    journal = render_native_sequential_queue(config)
    local_journal = args.local_journal.expanduser().resolve()
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")

    solver = connect(args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    if not solver.is_active():
        raise RuntimeError("Student Fluent session is not active")
    if not remote_file_exists(solver, args.preinit_case):
        raise FileNotFoundError(f"Student pre-initialization case is not visible: {args.preinit_case}")
    for path in (str(output), str(data), str(residual), str(remote_journal), str(transcript)):
        if remote_file_exists(solver, path):
            raise FileExistsError(f"Refusing to overwrite existing Student run artifact: {path}")

    write_remote_journal(solver, remote_journal, journal)
    solver.settings.file.read_journal(file_name_list=[str(remote_journal)])
    print(f"local_journal: {local_journal}", flush=True)
    print(f"remote_journal: {remote_journal}", flush=True)
    print(f"remote_transcript: {transcript}", flush=True)
    print(f"expected_case: {output}", flush=True)
    print(f"expected_data: {data}", flush=True)
    print("submitted_jobs: 1", flush=True)
    print("native_iterations: 500", flush=True)
    print("fluent_left_open: true", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
