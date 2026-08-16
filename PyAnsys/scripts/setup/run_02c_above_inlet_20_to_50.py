#!/usr/bin/env python3
"""Submit the coarse 02c H20--H50 sweep to Fluent as one native queue.

This script verifies the independently built pre-initialization children,
writes the already-rendered Fluent journal to the remote host, and submits it
to Fluent. Fluent owns Hybrid Initialization, iterations, and paired writes;
Python does not loop over solver iterations or checkpoints.
"""

from __future__ import annotations

import argparse
from pathlib import Path, PureWindowsPath
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


REMOTE_DIR = PureWindowsPath(r"C:\Users\syok443\P4P simulation\brine outlet")
CASES = (
    ("02c-H20", "brine-p1160kpa-unprimed"),
    ("02c-H25", "brine-p1165kpa-unprimed"),
    ("02c-H30", "brine-p1170kpa-unprimed"),
    ("02c-H35", "brine-p1175kpa-unprimed"),
    ("02c-H40", "brine-p1180kpa-unprimed"),
    ("02c-H45", "brine-p1185kpa-unprimed"),
    ("02c-H50", "brine-p1190kpa-unprimed"),
)


def scheme_string(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


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
        raise RuntimeError(f"Fluent did not expose remote journal: {remote_journal}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--build-stamp", required=True)
    parser.add_argument("--queue-stamp", required=True)
    parser.add_argument("--local-journal", type=Path, required=True)
    args = parser.parse_args()

    journal = args.local_journal.expanduser().resolve().read_text(encoding="utf-8")
    remote_journal = REMOTE_DIR / f"02c-above-inlet-20-to-50-queue-{args.queue_stamp}.jou"
    transcript = REMOTE_DIR / f"02c-above-inlet-20-to-50-queue-{args.queue_stamp}.trn"

    solver = connect(server_id=args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    if not solver.is_active():
        raise RuntimeError("Fluent session is not active")

    parent = REMOTE_DIR / "02c-B-brine-p1120kpa-unprimed-preinit-20260812T043007Z.cas.h5"
    if not remote_file_exists(solver, str(parent)):
        raise FileNotFoundError(f"Frozen 02c parent is not visible: {parent}")
    for case_id, suffix in CASES:
        preinit = REMOTE_DIR / f"{case_id}-{suffix}-preinit-{args.build_stamp}.cas.h5"
        output = REMOTE_DIR / f"{case_id}-{suffix}-iter500-{args.queue_stamp}.cas.h5"
        data = PureWindowsPath(str(output).replace(".cas.h5", ".dat.h5"))
        if not remote_file_exists(solver, str(preinit)):
            raise FileNotFoundError(f"Missing {case_id} pre-initialization child: {preinit}")
        for path in (output, data, transcript, remote_journal):
            if remote_file_exists(solver, str(path)):
                raise FileExistsError(f"Refusing to overwrite existing queue artifact: {path}")

    write_remote_journal(solver, remote_journal, journal)
    solver.settings.file.read_journal(file_name_list=[str(remote_journal)])

    print(f"local_journal: {args.local_journal.resolve()}")
    print(f"remote_journal: {remote_journal}")
    print(f"remote_transcript: {transcript}")
    print("submitted_cases: 7")
    print("native_iterations_per_case: 500")
    print("fluent_left_open: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
