#!/usr/bin/env python3
"""Generate the one-go Fluent-native D -> E -> F -> G queue journal."""

from __future__ import annotations

import argparse
from pathlib import Path, PureWindowsPath
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.positive_backpressure_queue import (  # noqa: E402
    NativeQueueJob,
    NativeSequentialQueue,
    render_native_sequential_queue,
)


REMOTE_DIR = PureWindowsPath(r"C:\Users\syok443\P4P simulation\brine outlet")
JOBS = (
    ("02c-D", "brine-p1122p5kpa-unprimed", "20260812T102345Z"),
    ("02c-E", "brine-p1127p5kpa-unprimed", "20260812T102546Z"),
    ("02c-F", "brine-p1130kpa-unprimed", "20260812T102700Z"),
    ("02c-G", "brine-p1135kpa-unprimed", "20260812T102800Z"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stamp", required=True, help="UTC queue stamp, e.g. 20260814T120000Z")
    parser.add_argument("--output-journal", type=Path, required=True)
    args = parser.parse_args()

    queue_stem = f"02c-positive-backpressure-queue-{args.stamp}"
    jobs = tuple(
        NativeQueueJob(
            case_id=case_id,
            preinit_case=str(REMOTE_DIR / f"{case_id}-{suffix}-preinit-{preinit_stamp}.cas.h5"),
            output_case_data=str(REMOTE_DIR / f"{case_id}-{suffix}-iter500-{args.stamp}.cas.h5"),
            residual_file=str(REMOTE_DIR / f"{case_id}-{suffix}-iter500-{args.stamp}-residuals.out"),
        )
        for case_id, suffix, preinit_stamp in JOBS
    )
    config = NativeSequentialQueue(
        queue_id=queue_stem,
        transcript_file=str(REMOTE_DIR / f"{queue_stem}.trn"),
        autosave_root=str(REMOTE_DIR / queue_stem),
        jobs=jobs,
    )
    payload = render_native_sequential_queue(config)
    destination = args.output_journal.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(payload, encoding="utf-8", newline="\n")
    print(f"journal: {destination}")
    print(f"remote_transcript: {config.transcript_file}")
    for job in jobs:
        print(f"{job.case_id}: {job.output_case_data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
