#!/usr/bin/env python3
"""Run the three Student-only 02c I-pressure smoke probes natively in Fluent.

This is explicitly a mesh-derived Student surrogate, not an authoritative 02c
parent-derived screen. Fluent owns the three independent Hybrid-initialized
50-iteration jobs; Python only validates files, writes the journal, submits it,
and leaves Fluent open.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PureWindowsPath

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.positive_backpressure_queue import (  # noqa: E402
    NativeQueueJob,
    NativeSequentialQueue,
    render_native_sequential_queue,
)


REMOTE_DIR = PureWindowsPath(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case")
BUILD_STAMP = "20260816T020200Z"
JOBS = (
    ("02c-I20", "brine-p1160kpa-unprimed-coarse130-student-smoke"),
    ("02c-I40", "brine-p1180kpa-unprimed-coarse130-student-smoke"),
    ("02c-I60", "brine-p1200kpa-unprimed-coarse130-student-smoke"),
)


def scheme_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def remote_journal_expression(remote_journal: PureWindowsPath, journal: str) -> str:
    body = " ".join(f'(display "{scheme_string(line)}") (newline)' for line in journal.splitlines())
    return f'(with-output-to-file "{scheme_string(remote_journal.as_posix())}" (lambda () {body}))'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--queue-stamp", required=True)
    parser.add_argument("--local-journal", type=Path, required=True)
    args = parser.parse_args()

    queue_id = f"02c-student-I20-I60-iter50-{args.queue_stamp}"
    remote_journal = REMOTE_DIR / f"{queue_id}.jou"
    transcript = REMOTE_DIR / f"{queue_id}.trn"
    jobs = tuple(
        NativeQueueJob(
            case_id=case_id,
            preinit_case=str(REMOTE_DIR / f"{case_id}-{suffix}-preinit-{BUILD_STAMP}.cas.h5"),
            output_case_data=str(REMOTE_DIR / f"{case_id}-{suffix}-iter50-{args.queue_stamp}.cas.h5"),
            residual_file=str(REMOTE_DIR / f"{case_id}-{suffix}-iter50-{args.queue_stamp}-residuals.out"),
        )
        for case_id, suffix in JOBS
    )
    config = NativeSequentialQueue(
        queue_id=queue_id,
        transcript_file=str(transcript),
        autosave_root=str(REMOTE_DIR / queue_id),
        jobs=jobs,
        iterations=50,
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
    for job in jobs:
        if not remote_file_exists(solver, job.preinit_case):
            raise FileNotFoundError(f"Missing Student probe source: {job.preinit_case}")
        data = PureWindowsPath(job.output_case_data.replace(".cas.h5", ".dat.h5"))
        for path in (job.output_case_data, str(data), job.residual_file):
            if remote_file_exists(solver, path):
                raise FileExistsError(f"Refusing to overwrite Student smoke artifact: {path}")
    for path in (str(remote_journal), str(transcript)):
        if remote_file_exists(solver, path):
            raise FileExistsError(f"Refusing to overwrite Student smoke queue artifact: {path}")

    solver.scheme.exec((remote_journal_expression(remote_journal, journal),))
    if not remote_file_exists(solver, str(remote_journal)):
        raise RuntimeError(f"Fluent did not expose the written Student smoke journal: {remote_journal}")
    solver.settings.file.read_journal(file_name_list=[str(remote_journal)])
    print(f"local_journal: {local_journal}")
    print(f"remote_journal: {remote_journal}")
    print(f"remote_transcript: {transcript}")
    print("submitted_jobs: 3")
    print("native_iterations_per_job: 50")
    print("fluent_left_open: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
