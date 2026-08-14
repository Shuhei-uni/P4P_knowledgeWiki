#!/usr/bin/env python3
"""Prepare and start an enforced-step Fluent-native 02d VOF smoke screen.

The source patch fields are copied into unique restart artifacts after their
residual convergence checks are disabled.  Fluent owns the subsequent 2,000
transient-time-step calculations and all checkpoint writes; Python does not
iterate or save progress from a client loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


REMOTE_DIR = PureWindowsPath(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet")
STAMP = "20260814T025000Z"
TIME_STEP_S = 1.0e-5
TIME_STEP_COUNT = 2000
MAX_INNER_ITERATIONS = 20
RESIDUAL_HISTORY_SIZE = TIME_STEP_COUNT * MAX_INNER_ITERATIONS
QUEUE_ID = f"02d-vof-enforced-step-screen-{STAMP}"
REMOTE_JOURNAL = REMOTE_DIR / f"{QUEUE_ID}.jou"
LOCAL_JOURNAL = PROJECT_ROOT / "queues" / f"{QUEUE_ID}.jou"
LOCAL_READBACK = PROJECT_ROOT / "output" / f"{QUEUE_ID}-setup-readback.json"


@dataclass(frozen=True)
class Job:
    identifier: str
    clean_case: PureWindowsPath
    clean_data: PureWindowsPath | None
    prepared_case: PureWindowsPath
    prepared_data: PureWindowsPath | None
    hybrid_initialize: bool


JOBS = (
    Job(
        "VOF-IC0-P1120",
        REMOTE_DIR / "VOF-IC0-P1120-coarse-patch-platform-preinit-20260814T000000Z.cas.h5",
        None,
        REMOTE_DIR / f"VOF-IC0-P1120-coarse-enforced-step-source-{STAMP}.cas.h5",
        None,
        True,
    ),
    Job(
        "VOF-IC1-P1120",
        REMOTE_DIR / "VOF-IC1-P1120-coarse-patch-platform-20260814T000000Z.cas.h5",
        REMOTE_DIR / "VOF-IC1-P1120-coarse-patch-platform-20260814T000000Z.dat.h5",
        REMOTE_DIR / f"VOF-IC1-P1120-coarse-enforced-step-source-{STAMP}.cas.h5",
        REMOTE_DIR / f"VOF-IC1-P1120-coarse-enforced-step-source-{STAMP}.dat.h5",
        False,
    ),
    Job(
        "VOF-IC2-Y030-P1120",
        REMOTE_DIR / "VOF-IC2-Y030-P1120-coarse-patch-platform-20260814T000000Z.cas.h5",
        REMOTE_DIR / "VOF-IC2-Y030-P1120-coarse-patch-platform-20260814T000000Z.dat.h5",
        REMOTE_DIR / f"VOF-IC2-Y030-P1120-coarse-enforced-step-source-{STAMP}.cas.h5",
        REMOTE_DIR / f"VOF-IC2-Y030-P1120-coarse-enforced-step-source-{STAMP}.dat.h5",
        False,
    ),
)


def posix_path(path: PureWindowsPath) -> str:
    return path.as_posix()


def scheme_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def output_case(job: Job, time_steps: int) -> PureWindowsPath:
    return REMOTE_DIR / f"{job.identifier}-coarse-enforced-step-ts{time_steps}-{STAMP}.cas.h5"


def output_data(job: Job, time_steps: int) -> PureWindowsPath:
    return REMOTE_DIR / f"{job.identifier}-coarse-enforced-step-ts{time_steps}-{STAMP}.dat.h5"


def transcript(job: Job) -> PureWindowsPath:
    return REMOTE_DIR / f"{job.identifier}-coarse-enforced-step-{STAMP}.trn"


def write_remote_journal_expression(remote_journal: str, journal: str) -> str:
    body = " ".join(
        f'(display "{scheme_string(line)}") (newline)' for line in journal.splitlines()
    )
    return f'(with-output-to-file "{scheme_string(remote_journal)}" (lambda () {body}))'


def configure_enforced_step_controls(solver) -> dict:
    """Disable every live residual convergence check and set common controls."""

    run = solver.settings.solution.run_calculation
    transient = run.transient_controls
    transient.time_step_size = TIME_STEP_S
    transient.time_step_count = TIME_STEP_COUNT
    transient.max_iter_per_time_step = MAX_INNER_ITERATIONS

    residual = solver.settings.solution.monitor.residual
    residual.options.n_save = RESIDUAL_HISTORY_SIZE
    residual.options.n_display = RESIDUAL_HISTORY_SIZE
    equations = residual.equations
    before = equations.get_state()
    for name in before:
        equations[name].check_convergence = False
    after = equations.get_state()
    enabled = [name for name, state in after.items() if state.get("check_convergence")]
    if enabled:
        raise RuntimeError(f"Residual convergence checks remain enabled: {enabled}")
    conv = solver.settings.solution.monitor.convergence_conditions.get_state()
    if conv.get("convergence_reports"):
        raise RuntimeError(f"Physical convergence reports are active: {conv['convergence_reports']}")
    return {
        "transient_controls": transient.get_state(),
        "residual_equations": after,
        "residual_options": residual.options.get_state(),
        "convergence_conditions": conv,
    }


def write_prepared_input(solver, job: Job) -> None:
    solver.settings.file.write_case(file_name=str(job.prepared_case))
    if job.prepared_data is not None:
        solver.settings.file.write_data(file_name=str(job.prepared_data))


def render_journal() -> str:
    lines = [
        f"; Fluent-native enforced 2,000-time-step screen: {QUEUE_ID}",
        "; Source inputs were read-back verified with residual convergence checks disabled.",
        "; Completion requires transcript evidence of 2,000 transient steps / flow time 0.020 s.",
        "/file/confirm-overwrite? no",
    ]
    for job in JOBS:
        lines.extend([
            f"; BEGIN {job.identifier}",
            f'/file/read-case "{posix_path(job.prepared_case)}"',
        ])
        if job.prepared_data is not None:
            lines.append(f'/file/read-data "{posix_path(job.prepared_data)}"')
        if job.hybrid_initialize:
            lines.append("/solve/initialize/hyb-initialization")
        lines.extend([
            f'/file/start-transcript "{posix_path(transcript(job))}"',
            "/solve/monitors/residual/print? yes",
            "/solve/iterate 1000",
            f'/file/write-case-data "{posix_path(output_case(job, 1000))}"',
            "/solve/iterate 1000",
            f'/file/write-case-data "{posix_path(output_case(job, 2000))}"',
            "/file/stop-transcript",
            f"; END {job.identifier}",
        ])
    lines.append("; Queue complete; Fluent remains open.")
    return "\n".join(lines) + "\n"


def require_absent(solver, paths: list[PureWindowsPath]) -> None:
    for path in paths:
        if remote_file_exists(solver, str(path)):
            raise FileExistsError(f"Refusing to overwrite: {path}")


def main() -> int:
    solver = connect(server_id="student")
    planned = [REMOTE_JOURNAL]
    for job in JOBS:
        if not remote_file_exists(solver, str(job.clean_case)):
            raise FileNotFoundError(f"Missing clean source case: {job.clean_case}")
        if job.clean_data and not remote_file_exists(solver, str(job.clean_data)):
            raise FileNotFoundError(f"Missing clean source data: {job.clean_data}")
        planned.append(job.prepared_case)
        if job.prepared_data:
            planned.append(job.prepared_data)
        for step in (1000, 2000):
            planned.extend((output_case(job, step), output_data(job, step)))
    require_absent(solver, planned)

    readback: dict[str, dict] = {}
    for job in JOBS:
        solver.settings.file.read_case(file_name=str(job.clean_case))
        if job.clean_data is not None:
            solver.settings.file.read_data(file_name=str(job.clean_data))
        readback[job.identifier] = configure_enforced_step_controls(solver)
        write_prepared_input(solver, job)

    # Re-read every prepared artifact: data-file loading is the critical point
    # at which transient and convergence controls used to be reset.
    for job in JOBS:
        solver.settings.file.read_case(file_name=str(job.prepared_case))
        if job.prepared_data is not None:
            solver.settings.file.read_data(file_name=str(job.prepared_data))
        verify = configure_enforced_step_controls(solver)
        readback[job.identifier]["prepared_reload"] = verify

    LOCAL_READBACK.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_READBACK.write_text(json.dumps(readback, indent=2), encoding="utf-8")
    journal = render_journal()
    LOCAL_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_JOURNAL.write_text(journal, encoding="utf-8", newline="\n")
    solver.scheme.exec((write_remote_journal_expression(posix_path(REMOTE_JOURNAL), journal),))
    if not remote_file_exists(solver, str(REMOTE_JOURNAL)):
        raise RuntimeError(f"Fluent did not expose written journal: {REMOTE_JOURNAL}")
    solver.settings.file.read_journal(file_name_list=[str(REMOTE_JOURNAL)])
    print(f"local_journal: {LOCAL_JOURNAL}")
    print(f"readback: {LOCAL_READBACK}")
    print(f"remote_journal: {REMOTE_JOURNAL}")
    print("submitted_jobs: 3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
