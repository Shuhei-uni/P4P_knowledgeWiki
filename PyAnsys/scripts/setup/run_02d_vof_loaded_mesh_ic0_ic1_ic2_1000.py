#!/usr/bin/env python3
"""Prepare and submit a native Fluent 1,000-step VOF run for IC0/IC1/IC2.

This script uses Python only for input verification, native-control preparation,
and journal submission.  Fluent owns Hybrid Initialization, transient stepping,
transcripts, and case/data checkpoint writes through the generated journal.

The timestep is deliberately conservative: ``1.0e-5 s``.  It is a numerical
smoke-test value retained from the repository's prior VOF stability screen, not
a production timestep qualified by a local cell-Courant survey.
"""

from __future__ import annotations

from dataclasses import dataclass
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
SOURCE_STAMP = "20260814T041658Z"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
TIME_STEP_S = 1.0e-5
TIME_STEP_COUNT = 1000
MAX_INNER_ITERATIONS = 20
RESIDUAL_HISTORY_SIZE = TIME_STEP_COUNT * MAX_INNER_ITERATIONS
QUEUE_ID = f"02d-loadedmesh-vof-ic0-ic1-ic2-1000-{STAMP}"
REMOTE_JOURNAL = REMOTE_DIR / f"{QUEUE_ID}.jou"
LOCAL_JOURNAL = PROJECT_ROOT / "queues" / f"{QUEUE_ID}.jou"
LOCAL_READBACK = PROJECT_ROOT / "output" / f"{QUEUE_ID}-setup-readback.json"


@dataclass(frozen=True)
class Job:
    identifier: str
    source_case: PureWindowsPath
    source_data: PureWindowsPath | None
    prepared_case: PureWindowsPath
    prepared_data: PureWindowsPath | None
    hybrid_initialize: bool


def source_case(stem: str) -> PureWindowsPath:
    return REMOTE_DIR / f"{stem}-{SOURCE_STAMP}.cas.h5"


def source_data(stem: str) -> PureWindowsPath:
    return REMOTE_DIR / f"{stem}-{SOURCE_STAMP}.dat.h5"


def prepared_case(stem: str) -> PureWindowsPath:
    return REMOTE_DIR / f"{stem}-run-source-{STAMP}.cas.h5"


def prepared_data(stem: str) -> PureWindowsPath:
    return REMOTE_DIR / f"{stem}-run-source-{STAMP}.dat.h5"


def checkpoint_case(name: str) -> PureWindowsPath:
    return REMOTE_DIR / f"{name}-loadedmesh-iter1000-{STAMP}.cas.h5"


def checkpoint_data(name: str) -> PureWindowsPath:
    return REMOTE_DIR / f"{name}-loadedmesh-iter1000-{STAMP}.dat.h5"


def transcript(name: str) -> PureWindowsPath:
    return REMOTE_DIR / f"{name}-loadedmesh-iter1000-{STAMP}.trn"


JOBS = (
    Job(
        "VOF-IC0-P1120",
        source_case("VOF-IC0-P1120-loadedmesh-preinit"),
        None,
        prepared_case("VOF-IC0-P1120-loadedmesh-preinit"),
        None,
        True,
    ),
    Job(
        "VOF-IC1-P1120",
        source_case("VOF-IC1-P1120-loadedmesh-patch-platform"),
        source_data("VOF-IC1-P1120-loadedmesh-patch-platform"),
        prepared_case("VOF-IC1-P1120-loadedmesh-patch-platform"),
        prepared_data("VOF-IC1-P1120-loadedmesh-patch-platform"),
        False,
    ),
    Job(
        "VOF-IC2-Y030-P1120",
        source_case("VOF-IC2-Y030-P1120-loadedmesh-patch-platform"),
        source_data("VOF-IC2-Y030-P1120-loadedmesh-patch-platform"),
        prepared_case("VOF-IC2-Y030-P1120-loadedmesh-patch-platform"),
        prepared_data("VOF-IC2-Y030-P1120-loadedmesh-patch-platform"),
        False,
    ),
)


def posix_path(path: PureWindowsPath) -> str:
    return path.as_posix()


def scheme_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def configure_native_controls(solver: Any) -> dict[str, Any]:
    """Set controls that must survive case/data reloads, then read them back."""

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
    remaining = [name for name, state in after.items() if state.get("check_convergence")]
    if remaining:
        raise RuntimeError(f"Residual convergence checks remain enabled: {remaining}")

    convergence = solver.settings.solution.monitor.convergence_conditions.get_state()
    reports = convergence.get("convergence_reports")
    if reports:
        raise RuntimeError(f"Physical convergence reports remain active: {reports}")

    transient_state = transient.get_state()
    if transient_state.get("time_step_size") != TIME_STEP_S:
        raise RuntimeError(f"Timestep readback mismatch: {transient_state}")
    if transient_state.get("time_step_count") != TIME_STEP_COUNT:
        raise RuntimeError(f"Timestep-count readback mismatch: {transient_state}")
    if transient_state.get("max_iter_per_time_step") != MAX_INNER_ITERATIONS:
        raise RuntimeError(f"Inner-iteration readback mismatch: {transient_state}")
    return {
        "transient_controls": transient_state,
        "residual_check_convergence": {
            name: bool(state.get("check_convergence")) for name, state in after.items()
        },
        "residual_history": residual.options.get_state(),
        "convergence_reports": reports or [],
    }


def write_prepared_input(solver: Any, job: Job) -> None:
    solver.settings.file.write_case(file_name=str(job.prepared_case))
    if job.prepared_data is not None:
        solver.settings.file.write_data(file_name=str(job.prepared_data))
    for path in (job.prepared_case, job.prepared_data):
        if path is not None and not remote_file_exists(solver, str(path)):
            raise RuntimeError(f"Fluent did not expose prepared input: {path}")


def render_journal() -> str:
    lines = [
        f"; Fluent-native 02d loaded-mesh 1,000-step queue: {QUEUE_ID}",
        "; Each job runs exactly one /solve/iterate 1000 command.",
        "; Timestep is reasserted after every case/data load: 1.0e-5 s.",
        "; Residual convergence auto-stop is disabled in the prepared source copies.",
        "; This is a numerical smoke test, not a production timestep qualification.",
        "/file/confirm-overwrite? no",
    ]
    for job in JOBS:
        lines.extend([
            f"; BEGIN {job.identifier}",
            f'/file/read-case "{posix_path(job.prepared_case)}"',
        ])
        if job.prepared_data is not None:
            lines.append(f'/file/read-data "{posix_path(job.prepared_data)}"')
        lines.extend([
            "; Reapply after data reads because Fluent may restore transient controls.",
            "/solve/set/transient-controls/time-step-size 1e-05",
            f'/file/start-transcript "{posix_path(transcript(job.identifier))}"',
            "/solve/monitors/residual/print? yes",
        ])
        if job.hybrid_initialize:
            lines.append("/solve/initialize/hyb-initialization")
        lines.extend([
            "/solve/iterate 1000",
            f'/file/write-case-data "{posix_path(checkpoint_case(job.identifier))}"',
            "/file/stop-transcript",
            f"; END {job.identifier}",
        ])
    lines.append("; Queue complete; Fluent remains open.")
    return "\n".join(lines) + "\n"


def write_remote_journal(solver: Any, journal: str) -> None:
    body = " ".join(
        f'(display "{scheme_string(line)}") (newline)' for line in journal.splitlines()
    )
    expression = (
        f'(with-output-to-file "{scheme_string(posix_path(REMOTE_JOURNAL))}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, str(REMOTE_JOURNAL)):
        raise RuntimeError(f"Fluent did not expose remote journal: {REMOTE_JOURNAL}")


def main() -> int:
    solver = connect(server_id="student")
    planned: list[PureWindowsPath] = [REMOTE_JOURNAL]
    for job in JOBS:
        if not remote_file_exists(solver, str(job.source_case)):
            raise FileNotFoundError(f"Missing source case: {job.source_case}")
        if job.source_data is not None and not remote_file_exists(solver, str(job.source_data)):
            raise FileNotFoundError(f"Missing source data: {job.source_data}")
        planned.extend((job.prepared_case, checkpoint_case(job.identifier), transcript(job.identifier)))
        if job.prepared_data is not None:
            planned.extend((job.prepared_data, checkpoint_data(job.identifier)))
    for path in planned:
        if remote_file_exists(solver, str(path)):
            raise FileExistsError(f"Refusing to overwrite existing run artifact: {path}")

    readback: dict[str, Any] = {}
    for job in JOBS:
        solver.settings.file.read_case(file_name=str(job.source_case))
        if job.source_data is not None:
            solver.settings.file.read_data(file_name=str(job.source_data))
        controls = configure_native_controls(solver)
        write_prepared_input(solver, job)
        readback[job.identifier] = {"prepared_controls": controls}

    # Verify controls after the prepared case/data reload, the point at which a
    # data file can restore unsafe/default transient values.
    for job in JOBS:
        solver.settings.file.read_case(file_name=str(job.prepared_case))
        if job.prepared_data is not None:
            solver.settings.file.read_data(file_name=str(job.prepared_data))
        readback[job.identifier]["prepared_reload_controls"] = configure_native_controls(solver)

    LOCAL_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    journal = render_journal()
    LOCAL_JOURNAL.write_text(journal, encoding="utf-8", newline="\n")
    write_remote_journal(solver, journal)

    LOCAL_READBACK.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_READBACK.write_text(
        json.dumps(
            {
                "queue_id": QUEUE_ID,
                "source_stamp": SOURCE_STAMP,
                "timestep_s": TIME_STEP_S,
                "time_step_count": TIME_STEP_COUNT,
                "max_inner_iterations": MAX_INNER_ITERATIONS,
                "jobs": readback,
                "remote_journal": str(REMOTE_JOURNAL),
                "local_journal": str(LOCAL_JOURNAL),
                "submitted": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Fluent owns all three native solve commands.  This call submits the
    # journal; it is not a Python iteration loop.
    solver.settings.file.read_journal(file_name_list=[str(REMOTE_JOURNAL)])
    readback_payload = json.loads(LOCAL_READBACK.read_text(encoding="utf-8"))
    readback_payload["submitted"] = True
    LOCAL_READBACK.write_text(json.dumps(readback_payload, indent=2) + "\n", encoding="utf-8")
    print(f"local_journal: {LOCAL_JOURNAL}")
    print(f"remote_journal: {REMOTE_JOURNAL}")
    print(f"readback: {LOCAL_READBACK}")
    print("submitted_jobs: 3")
    print("native_commands_per_job: /solve/iterate 1000")
    print(f"timestep_s: {TIME_STEP_S}")
    print("fluent_left_open: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
