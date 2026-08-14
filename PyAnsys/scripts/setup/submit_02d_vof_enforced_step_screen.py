#!/usr/bin/env python3
"""Submit the already verified 02d enforced-time-step native Fluent queue."""

from __future__ import annotations

from pathlib import Path, PureWindowsPath
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

ROOT = PureWindowsPath(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet")
SOURCE_STAMP = "20260814T025000Z"
STAMP = "20260814T026000Z"
QUEUE_ID = f"02d-vof-enforced-step-screen-{STAMP}"
REMOTE_JOURNAL = ROOT / f"{QUEUE_ID}.jou"
LOCAL_JOURNAL = PROJECT_ROOT / "queues" / f"{QUEUE_ID}.jou"
JOBS = (
    ("VOF-IC0-P1120", ROOT / f"VOF-IC0-P1120-coarse-enforced-step-source-{SOURCE_STAMP}.cas.h5", None, True),
    ("VOF-IC1-P1120", ROOT / f"VOF-IC1-P1120-coarse-enforced-step-source-{SOURCE_STAMP}.cas.h5", ROOT / f"VOF-IC1-P1120-coarse-enforced-step-source-{SOURCE_STAMP}.dat.h5", False),
    ("VOF-IC2-Y030-P1120", ROOT / f"VOF-IC2-Y030-P1120-coarse-enforced-step-source-{SOURCE_STAMP}.cas.h5", ROOT / f"VOF-IC2-Y030-P1120-coarse-enforced-step-source-{SOURCE_STAMP}.dat.h5", False),
)


def p(path: PureWindowsPath) -> str:
    return path.as_posix()


def q(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def output(case: str, checkpoint: int) -> PureWindowsPath:
    return ROOT / f"{case}-coarse-enforced-step-ts{checkpoint}-{STAMP}.cas.h5"


def output_data(case: str, checkpoint: int) -> PureWindowsPath:
    return ROOT / f"{case}-coarse-enforced-step-ts{checkpoint}-{STAMP}.dat.h5"


def render() -> str:
    lines = [
        f"; Enforced transient-time-step queue: {QUEUE_ID}",
        "; Prepared sources have 1e-5 s dt, 2,000 steps, max 20 inner iterations,",
        "; all residual check-convergence flags disabled, and no convergence reports.",
        "; Transcript verification, not filenames, determines actual completed steps.",
        "/file/confirm-overwrite? no",
    ]
    for name, case, data, hybrid in JOBS:
        lines.extend((f"; BEGIN {name}", f'/file/read-case "{p(case)}"'))
        if data:
            lines.append(f'/file/read-data "{p(data)}"')
        if hybrid:
            lines.append("/solve/initialize/hyb-initialization")
        lines.extend((
            f'/file/start-transcript "{p(ROOT / f"{name}-coarse-enforced-step-{STAMP}.trn")}"',
            "/solve/monitors/residual/print? yes",
            "/solve/iterate 1000",
            f'/file/write-case-data "{p(output(name, 1000))}"',
            "/solve/iterate 1000",
            f'/file/write-case-data "{p(output(name, 2000))}"',
            "/file/stop-transcript",
            f"; END {name}",
        ))
    return "\n".join(lines) + "\n"


def main() -> int:
    solver = connect(server_id="student")
    planned = [REMOTE_JOURNAL]
    for _, case, data, _ in JOBS:
        if not remote_file_exists(solver, str(case)):
            raise FileNotFoundError(case)
        if data and not remote_file_exists(solver, str(data)):
            raise FileNotFoundError(data)
    for name, _, _, _ in JOBS:
        for step in (1000, 2000):
            planned.extend((output(name, step), output_data(name, step)))
    for path in planned:
        if remote_file_exists(solver, str(path)):
            raise FileExistsError(f"Refusing to overwrite: {path}")
    journal = render()
    LOCAL_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_JOURNAL.write_text(journal, encoding="utf-8", newline="\n")
    body = " ".join(f'(display "{q(line)}") (newline)' for line in journal.splitlines())
    solver.scheme.exec((f'(with-output-to-file "{q(p(REMOTE_JOURNAL))}" (lambda () {body}))',))
    solver.settings.file.read_journal(file_name_list=[str(REMOTE_JOURNAL)])
    print(f"local_journal: {LOCAL_JOURNAL}")
    print(f"remote_journal: {REMOTE_JOURNAL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
