#!/usr/bin/env python3
"""Create and start a small Fluent-native sequential VOF queue smoke test.

The Fluent journal—not Python—owns loading, Hybrid Initialization, the 75
iteration screen, and paired case/data write for every job.  All three jobs
deliberately reload the same clean IC0 source so this is a queue-mechanics
demonstration rather than a sensitivity or result-producing study.
"""

from __future__ import annotations

from pathlib import Path, PureWindowsPath
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


REMOTE_DIR = PureWindowsPath(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet")
STAMP = "20260814T000000Z"
QUEUE_ID = f"vof-queue-smoke-test-{STAMP}"
SOURCE_CASE = REMOTE_DIR / "VOF-IC0-P1120-coarse-patch-platform-preinit-20260814T000000Z.cas.h5"
REMOTE_JOURNAL = REMOTE_DIR / f"{QUEUE_ID}.jou"
TRANSCRIPT = REMOTE_DIR / f"{QUEUE_ID}.trn"
LOCAL_JOURNAL = PROJECT_ROOT / "queues" / f"{QUEUE_ID}.jou"


def posix_path(path: PureWindowsPath) -> str:
    return path.as_posix()


def scheme_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def write_remote_journal_expression(remote_journal: str, journal: str) -> str:
    """Render a Scheme expression that writes literal Fluent journal lines.

    Fluent's Scheme parser preserved ``\\n`` as text in this environment, so
    each journal line is emitted through an explicit ``newline`` call instead.
    """

    body = " ".join(
        f'(display "{scheme_string(line)}") (newline)' for line in journal.splitlines()
    )
    return f'(with-output-to-file "{scheme_string(remote_journal)}" (lambda () {body}))'


def render() -> str:
    source = posix_path(SOURCE_CASE)
    lines = [
        f"; Fluent-native queue smoke test: {QUEUE_ID}",
        "; Every job reloads the same clean IC0 pre-initialization case.",
        "; This is a queue-mechanics test only; Fluent owns initialization, iterations, and saves.",
        "/file/confirm-overwrite? no",
        f'/file/start-transcript "{posix_path(TRANSCRIPT)}"',
    ]
    for index in range(1, 4):
        output = REMOTE_DIR / f"VOF-QUEUE-TEST-{index:02d}-ITER75-{STAMP}.cas.h5"
        lines.extend(
            [
                f"; BEGIN queue test job {index}",
                f'/file/read-case "{source}"',
                "/solve/initialize/hyb-initialization",
                "/solve/iterate 75",
                f'/file/write-case-data "{posix_path(output)}"',
                f"; END queue test job {index}",
            ]
        )
    lines.extend(["/file/stop-transcript", "; Queue complete; Fluent remains open."])
    return "\n".join(lines) + "\n"


def main() -> int:
    journal = render()
    LOCAL_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_JOURNAL.write_text(journal, encoding="utf-8", newline="\n")

    solver = connect(server_id="student")
    if not remote_file_exists(solver, str(SOURCE_CASE)):
        raise FileNotFoundError(f"Fluent cannot see the clean source case: {SOURCE_CASE}")
    for index in range(1, 4):
        for suffix in ("cas.h5", "dat.h5"):
            target = REMOTE_DIR / f"VOF-QUEUE-TEST-{index:02d}-ITER75-{STAMP}.{suffix}"
            if remote_file_exists(solver, str(target)):
                raise FileExistsError(f"Refusing to overwrite test endpoint: {target}")
    # Store the exact submitted program on the Fluent host, then run it natively.
    # The named journal is a disposable smoke-test artifact and is regenerated
    # before submission to correct any interrupted prior attempt.
    remote_journal = posix_path(REMOTE_JOURNAL)
    solver.scheme.exec((write_remote_journal_expression(remote_journal, journal),))
    if not remote_file_exists(solver, str(REMOTE_JOURNAL)):
        raise RuntimeError(f"Fluent did not expose the written remote journal: {REMOTE_JOURNAL}")
    solver.settings.file.read_journal(file_name_list=[str(REMOTE_JOURNAL)])
    print(f"local_journal: {LOCAL_JOURNAL}")
    print(f"remote_journal: {REMOTE_JOURNAL}")
    print("submitted_jobs: 3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
