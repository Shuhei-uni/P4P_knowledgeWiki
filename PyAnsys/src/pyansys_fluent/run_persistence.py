#!/usr/bin/env python3
"""Robust autosave, final-save, and resume helpers for Fluent runs."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any

from pyansys_fluent.common import write_json_snapshot
from pyansys_fluent.setup_io import checkpoint_paths, rolling_autosave_path, write_case_data_pair, write_case_only


_ITERATION_PATTERN = re.compile(r"-iter(?P<iteration>\d+)\.cas\.h5$", re.IGNORECASE)


def _strip_fluent_suffix(path_text: str) -> str:
    name = PureWindowsPath(path_text).name
    if name.endswith(".cas.h5"):
        return name[:-7]
    if name.endswith(".dat.h5"):
        return name[:-7]
    return PureWindowsPath(path_text).stem


def build_run_state_path(path_text: str) -> str:
    path = PureWindowsPath(path_text)
    return str(path.with_name(f"{_strip_fluent_suffix(path_text)}-run-state.json"))


def build_checkpoint_paths(case_path: str, data_path: str, iteration: int) -> tuple[str, str]:
    return checkpoint_paths(case_path, iteration), checkpoint_paths(data_path, iteration)


def build_autosave_paths(case_path: str, data_path: str) -> tuple[str, str]:
    return rolling_autosave_path(case_path), rolling_autosave_path(data_path)


def _existing_file(path_text: str) -> Path | None:
    path = Path(path_text)
    return path if path.exists() else None


def _parse_iteration_from_history_case(case_path: Path) -> int:
    match = _ITERATION_PATTERN.search(case_path.name)
    return int(match.group("iteration")) if match else 0


def _candidate_history_pairs(case_path: str, data_path: str) -> list[tuple[int, float, str, str]]:
    case_root = Path(case_path)
    data_root = Path(data_path)
    directory = case_root.parent
    prefix = _strip_fluent_suffix(case_path)

    candidates: list[tuple[int, float, str, str]] = []
    for case_file in directory.glob(f"{prefix}-iter*.cas.h5"):
        iteration = _parse_iteration_from_history_case(case_file)
        if iteration <= 0:
            continue
        data_file = data_root.parent / case_file.name.replace(".cas.h5", ".dat.h5")
        if not data_file.exists():
            continue
        try:
            mtime = max(case_file.stat().st_mtime, data_file.stat().st_mtime)
        except OSError:
            mtime = 0.0
        candidates.append((iteration, mtime, str(case_file), str(data_file)))
    return candidates


def prune_checkpoint_history(
    output_case: str,
    output_data: str,
    *,
    keep_pairs: int = 2,
) -> None:
    """Delete old numbered case/data checkpoints after a verified save.

    The default policy retains the newest pair and its immediate predecessor.
    The final output pair is managed separately by :class:`RunPersistence`.
    """

    if keep_pairs < 0:
        raise ValueError("keep_pairs must be non-negative")
    candidates = sorted(
        _candidate_history_pairs(output_case, output_data),
        key=lambda item: (item[0], item[1]),
        reverse=True,
    )
    for _iteration, _mtime, case_path_text, data_path_text in candidates[keep_pairs:]:
        Path(case_path_text).unlink(missing_ok=True)
        Path(data_path_text).unlink(missing_ok=True)


def discover_latest_resume_source(
    output_case: str,
    output_data: str,
    *,
    resume_case: str = "",
    resume_data: str = "",
    resume_state_json: str = "",
) -> "ResumeSource":
    """Resolve the best available case/data pair for resuming a run."""

    if resume_case and resume_data:
        return ResumeSource(
            case_path=resume_case,
            data_path=resume_data,
            completed_iterations=0,
            source="explicit",
            state_path=resume_state_json,
        )

    if resume_state_json:
        try:
            state = load_run_state(resume_state_json)
        except (OSError, json.JSONDecodeError, ValueError):
            state = {}
        if state:
            last_checkpoint = state.get("last_checkpoint", {})
            case_path = str(last_checkpoint.get("case_path") or state.get("resume_case") or "")
            data_path = str(last_checkpoint.get("data_path") or state.get("resume_data") or "")
            completed_iterations = int(state.get("completed_iterations", last_checkpoint.get("iteration", 0)) or 0)
            if case_path and data_path:
                return ResumeSource(
                    case_path=case_path,
                    data_path=data_path,
                    completed_iterations=completed_iterations,
                    source="state",
                    state_path=resume_state_json,
                    checkpoint_case_path=str(last_checkpoint.get("history_case_path") or ""),
                    checkpoint_data_path=str(last_checkpoint.get("history_data_path") or ""),
                )

    history_candidates = _candidate_history_pairs(output_case, output_data)
    if history_candidates:
        iteration, _, case_path, data_path = max(history_candidates, key=lambda item: (item[0], item[1]))
        return ResumeSource(
            case_path=case_path,
            data_path=data_path,
            completed_iterations=iteration,
            source="history-checkpoint",
            state_path=resume_state_json,
            checkpoint_case_path=case_path,
            checkpoint_data_path=data_path,
        )

    autosave_case, autosave_data = build_autosave_paths(output_case, output_data)
    if _existing_file(autosave_case) and _existing_file(autosave_data):
        return ResumeSource(
            case_path=autosave_case,
            data_path=autosave_data,
            completed_iterations=0,
            source="autosave",
            state_path=resume_state_json,
            checkpoint_case_path=autosave_case,
            checkpoint_data_path=autosave_data,
        )

    return ResumeSource(source="none", state_path=resume_state_json)


def load_run_state(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_run_state(path_text: str, payload: dict[str, Any]) -> None:
    if not path_text.strip():
        return
    write_json_snapshot(path_text, payload)


@dataclass(frozen=True)
class ResumeSource:
    case_path: str = ""
    data_path: str = ""
    completed_iterations: int = 0
    source: str = "none"
    state_path: str = ""
    checkpoint_case_path: str = ""
    checkpoint_data_path: str = ""

    @property
    def is_available(self) -> bool:
        return bool(self.case_path and self.data_path)


@dataclass
class RunPersistence:
    output_case: str
    output_data: str
    checkpoint_interval: int = 0
    report_interval: int = 100
    state_json: str = ""
    # False means rolling retention: newest checkpoint plus one predecessor.
    # True is retained as an explicit opt-in for long historical archives.
    keep_history: bool = False

    def state_path(self) -> str:
        return self.state_json.strip() or build_run_state_path(self.output_case)

    def checkpoint_pair(self, completed_iterations: int) -> tuple[str, str]:
        return build_checkpoint_paths(self.output_case, self.output_data, completed_iterations)

    def autosave_pair(self) -> tuple[str, str]:
        return build_autosave_paths(self.output_case, self.output_data)

    def _write_state(
        self,
        *,
        status: str,
        completed_iterations: int,
        total_iterations: int | None = None,
        last_checkpoint_iteration: int | None = None,
        last_checkpoint_case: str = "",
        last_checkpoint_data: str = "",
        saved_case: str = "",
        saved_data: str = "",
        resume_case: str = "",
        resume_data: str = "",
        notes: list[str] | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "status": status,
            "completed_iterations": completed_iterations,
            "total_iterations": total_iterations,
            "output_case": self.output_case,
            "output_data": self.output_data,
            "checkpoint_interval": self.checkpoint_interval,
            "report_interval": self.report_interval,
            "keep_history": self.keep_history,
            "saved_case": saved_case,
            "saved_data": saved_data,
            "resume_case": resume_case,
            "resume_data": resume_data,
            "last_checkpoint": {
                "iteration": last_checkpoint_iteration,
                "case_path": last_checkpoint_case,
                "data_path": last_checkpoint_data,
            },
            "notes": notes or [],
        }
        save_run_state(self.state_path(), payload)

    def record_run_start(self, total_iterations: int, *, completed_iterations: int = 0) -> None:
        self._write_state(
            status="running",
            completed_iterations=completed_iterations,
            total_iterations=total_iterations,
            notes=["run started"],
        )

    def record_checkpoint(
        self,
        solver,
        *,
        completed_iterations: int,
        total_iterations: int | None = None,
    ) -> None:
        if self.checkpoint_interval <= 0:
            return

        notes: list[str] = []
        saved_case = ""
        saved_data = ""
        checkpoint_case, checkpoint_data = self.checkpoint_pair(completed_iterations)

        try:
            write_case_data_pair(
                solver,
                checkpoint_case,
                checkpoint_data,
                f"write_checkpoint_{completed_iterations}",
            )
            saved_case = checkpoint_case
            saved_data = checkpoint_data
            if not self.keep_history:
                prune_checkpoint_history(
                    self.output_case,
                    self.output_data,
                    keep_pairs=2,
                )
        except Exception as exc:
            notes.append(f"rolling checkpoint failed: {type(exc).__name__}: {exc}")

        if not saved_case or not saved_data:
            raise RuntimeError(
                f"Failed to write checkpoint at iteration {completed_iterations}: {'; '.join(notes) or 'unknown error'}"
            )

        self._write_state(
            status="checkpointed",
            completed_iterations=completed_iterations,
            total_iterations=total_iterations,
            last_checkpoint_iteration=completed_iterations,
            last_checkpoint_case=saved_case,
            last_checkpoint_data=saved_data,
            saved_case=saved_case,
            saved_data=saved_data,
            notes=notes,
        )

    def record_final(
        self,
        solver,
        *,
        completed_iterations: int | None = None,
        total_iterations: int | None = None,
        allow_case_only: bool = False,
    ) -> str:
        saved_kind = write_case_data_pair(
            solver,
            self.output_case,
            self.output_data,
            "write_final_case_data",
            allow_case_only=allow_case_only,
        )
        if not self.keep_history:
            prune_checkpoint_history(
                self.output_case,
                self.output_data,
                keep_pairs=1,
            )
        self._write_state(
            status="completed",
            completed_iterations=completed_iterations if completed_iterations is not None else 0,
            total_iterations=total_iterations,
            last_checkpoint_iteration=completed_iterations,
            last_checkpoint_case=self.output_case,
            last_checkpoint_data=self.output_data if saved_kind != "case-only" else "",
            saved_case=self.output_case,
            saved_data=self.output_data if saved_kind != "case-only" else "",
            notes=[f"final save kind: {saved_kind}"],
        )
        return saved_kind

    def record_case_only(
        self,
        solver,
        *,
        completed_iterations: int | None = None,
        total_iterations: int | None = None,
    ) -> None:
        write_case_only(solver, self.output_case, "write_final_case_only")
        if not self.keep_history:
            prune_checkpoint_history(
                self.output_case,
                self.output_data,
                keep_pairs=1,
            )
        self._write_state(
            status="completed",
            completed_iterations=completed_iterations if completed_iterations is not None else 0,
            total_iterations=total_iterations,
            last_checkpoint_iteration=completed_iterations,
            last_checkpoint_case=self.output_case,
            last_checkpoint_data="",
            saved_case=self.output_case,
            saved_data="",
            notes=["final save kind: case-only"],
        )

    def record_interrupt(
        self,
        solver,
        *,
        completed_iterations: int,
        total_iterations: int | None = None,
        allow_case_only: bool = False,
    ) -> str:
        saved_kind = write_case_data_pair(
            solver,
            self.output_case,
            self.output_data,
            "write_interrupt_case_data",
            allow_case_only=allow_case_only,
        )
        if not self.keep_history:
            prune_checkpoint_history(
                self.output_case,
                self.output_data,
                keep_pairs=1,
            )
        self._write_state(
            status="interrupted",
            completed_iterations=completed_iterations,
            total_iterations=total_iterations,
            last_checkpoint_iteration=completed_iterations,
            last_checkpoint_case=self.output_case,
            last_checkpoint_data=self.output_data if saved_kind != "case-only" else "",
            saved_case=self.output_case,
            saved_data=self.output_data if saved_kind != "case-only" else "",
            notes=[f"interrupt save kind: {saved_kind}"],
        )
        return saved_kind
