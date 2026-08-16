"""Render Fluent-native sequential journals for the 02c pressure screen.

The returned journal is a Fluent program: it owns case loads, Hybrid
Initialization, iteration, autosave, and case/data writes.  Python only
creates or submits the journal; it must never own a loop of iterate calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PureWindowsPath


def _fluent_path(value: str, *, label: str) -> str:
    path = PureWindowsPath(str(value).strip())
    if not path.is_absolute() or not path.drive:
        raise ValueError(f"{label} must be an absolute Windows path: {value!r}")
    rendered = path.as_posix()
    if any(character in rendered for character in ('"', '\n', '\r')):
        raise ValueError(f"{label} contains journal-unsafe characters")
    return rendered


@dataclass(frozen=True)
class NativeQueueJob:
    case_id: str
    preinit_case: str
    output_case_data: str
    residual_file: str


@dataclass(frozen=True)
class NativeSequentialQueue:
    queue_id: str
    transcript_file: str
    autosave_root: str
    jobs: tuple[NativeQueueJob, ...]
    iterations: int = 500

    def validate(self) -> None:
        if not self.jobs:
            raise ValueError("Native queue must contain at least one job")
        if self.iterations <= 0:
            raise ValueError("iterations must be positive")
        _fluent_path(self.transcript_file, label="transcript_file")
        _fluent_path(self.autosave_root, label="autosave_root")
        for job in self.jobs:
            _fluent_path(job.preinit_case, label=f"{job.case_id} preinit_case")
            _fluent_path(job.output_case_data, label=f"{job.case_id} output_case_data")
            _fluent_path(job.residual_file, label=f"{job.case_id} residual_file")


def render_native_sequential_queue(config: NativeSequentialQueue) -> str:
    """Return one Fluent-native sequential queue journal.

    ``write-case-data`` follows every completed screen. This is deliberately
    self-contained: the Fluent 2025 R2 autosave menu has release-specific
    interactive prompts, while the explicit end-of-screen paired write has
    already been verified in this project.
    """

    config.validate()
    transcript = _fluent_path(config.transcript_file, label="transcript_file")
    autosave_root = _fluent_path(config.autosave_root, label="autosave_root")
    lines = [
        f"; Fluent-native queue: {config.queue_id}",
        "; Matrix members are independent pre-initialization cases; no solved field is reused.",
        "; Python does not own iterations or checkpoint timing.",
        "/file/confirm-overwrite? no",
        f'/file/start-transcript "{transcript}"',
        "/solve/monitors/residual/print? yes",
        "/solve/monitors/residual/plot? yes",
        "/solve/monitors/residual/n-save 600",
        f"; Native autosave root reserved for this queue: {autosave_root}",
        "; Every completed screen is protected by its explicit write-case-data below.",
    ]
    for job in config.jobs:
        source = _fluent_path(job.preinit_case, label=f"{job.case_id} preinit_case")
        output = _fluent_path(job.output_case_data, label=f"{job.case_id} output_case_data")
        residual = _fluent_path(job.residual_file, label=f"{job.case_id} residual_file")
        lines.extend(
            [
                f"; BEGIN {job.case_id}",
                f'/file/read-case "{source}"',
                "/solve/initialize/hyb-initialization",
                f"/solve/iterate {config.iterations}",
                f'/file/write-case-data "{output}"',
                f'/plot/residuals-set/plot-to-file "{residual}"',
                "/plot/residuals",
                "/plot/residuals-set/end-plot-to-file",
                f"; END {job.case_id}",
            ]
        )
    lines.extend(["/file/stop-transcript", "; Queue complete; Fluent remains open."])
    return "\n".join(lines) + "\n"
