#!/usr/bin/env python3
"""Generate a one-go Fluent-native 02c pressure-sweep queue journal."""

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
ABOVE_INLET_JOBS = (
    ("02c-H20", "brine-p1160kpa-unprimed"),
    ("02c-H25", "brine-p1165kpa-unprimed"),
    ("02c-H30", "brine-p1170kpa-unprimed"),
    ("02c-H35", "brine-p1175kpa-unprimed"),
    ("02c-H40", "brine-p1180kpa-unprimed"),
    ("02c-H45", "brine-p1185kpa-unprimed"),
    ("02c-H50", "brine-p1190kpa-unprimed"),
)
ABOVE_INLET_COARSE_JOBS = (
    ("02c-I20", "brine-p1160kpa-unprimed-coarse130"),
    ("02c-I40", "brine-p1180kpa-unprimed-coarse130"),
    ("02c-I60", "brine-p1200kpa-unprimed-coarse130"),
    ("02c-I80", "brine-p1220kpa-unprimed-coarse130"),
    ("02c-I100", "brine-p1240kpa-unprimed-coarse130"),
    ("02c-I120", "brine-p1260kpa-unprimed-coarse130"),
    ("02c-I140", "brine-p1280kpa-unprimed-coarse130"),
    ("02c-I160", "brine-p1300kpa-unprimed-coarse130"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stamp", required=True, help="UTC queue stamp, e.g. 20260814T120000Z")
    parser.add_argument("--output-journal", type=Path, required=True)
    parser.add_argument(
        "--remote-dir",
        default=str(REMOTE_DIR),
        help="Absolute Windows output directory visible to the selected Fluent session.",
    )
    parser.add_argument(
        "--artifact-tag",
        default="",
        help="Optional filename tag shared by pre-initialization and endpoint artifacts.",
    )
    parser.add_argument(
        "--preinit-stamp",
        default="",
        help="Pre-initialization child timestamp for an above-inlet matrix.",
    )
    parser.add_argument(
        "--matrix",
        choices=("positive-d-to-g", "above-inlet-20-to-50", "above-inlet-20-to-130-coarse"),
        default="positive-d-to-g",
        help="Select the named 02c pressure matrix to render.",
    )
    args = parser.parse_args()
    remote_dir = PureWindowsPath(args.remote_dir)
    if not remote_dir.is_absolute():
        parser.error("--remote-dir must be an absolute Windows path")

    if args.matrix != "positive-d-to-g" and not args.preinit_stamp:
        parser.error("--preinit-stamp is required for an above-inlet matrix")
    matrix_jobs = {
        "positive-d-to-g": JOBS,
        "above-inlet-20-to-50": tuple(
            (case_id, suffix, args.preinit_stamp) for case_id, suffix in ABOVE_INLET_JOBS
        ),
        "above-inlet-20-to-130-coarse": tuple(
            (case_id, suffix, args.preinit_stamp) for case_id, suffix in ABOVE_INLET_COARSE_JOBS
        ),
    }[args.matrix]
    queue_prefix = {
        "positive-d-to-g": "02c-positive-backpressure-queue",
        "above-inlet-20-to-50": "02c-above-inlet-20-to-50-queue",
        "above-inlet-20-to-130-coarse": "02c-above-inlet-20-to-130-coarse-queue",
    }[args.matrix]
    artifact_tag = f"-{args.artifact_tag.strip()}" if args.artifact_tag.strip() else ""
    queue_stem = f"{queue_prefix}-{args.stamp}"
    jobs = tuple(
        NativeQueueJob(
            case_id=case_id,
            preinit_case=str(remote_dir / f"{case_id}-{suffix}{artifact_tag}-preinit-{preinit_stamp}.cas.h5"),
            output_case_data=str(remote_dir / f"{case_id}-{suffix}{artifact_tag}-iter500-{args.stamp}.cas.h5"),
            residual_file=str(remote_dir / f"{case_id}-{suffix}{artifact_tag}-iter500-{args.stamp}-residuals.out"),
        )
        for case_id, suffix, preinit_stamp in matrix_jobs
    )
    config = NativeSequentialQueue(
        queue_id=queue_stem,
        transcript_file=str(remote_dir / f"{queue_stem}.trn"),
        autosave_root=str(remote_dir / queue_stem),
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
