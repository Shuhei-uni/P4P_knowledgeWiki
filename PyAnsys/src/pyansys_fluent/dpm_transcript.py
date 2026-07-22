#!/usr/bin/env python3
"""Completion-aware Fluent transcript capture for DPM tracking.

PyFluent's ``execute_tui`` can return before the transcript stream has delivered
all lines printed by a long-running Fluent command. Capturing Python stdout is
not sufficient because Fluent transcript callbacks run on a streaming worker
thread. This module registers directly with ``solver.transcript``, waits for a
complete DPM Summary block, and persists each injection before another command
is submitted.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pyansys_fluent.dpm_reports import (
    build_track_command,
    dpm_flow_closure,
    execute_tui,
    parse_particle_track_summary,
)


class SessionTranscriptCapture:
    """Collect Fluent transcript chunks without taking ownership of the stream."""

    def __init__(
        self,
        solver: Any,
        *,
        stream_path: Path | None = None,
        echo: bool = False,
    ) -> None:
        self.solver = solver
        self.transcript = getattr(solver, "transcript", None)
        if self.transcript is None:
            raise RuntimeError(
                "PyFluent transcript service is unavailable. Reconnect with start_transcript=True."
            )

        self.stream_path = stream_path
        self.echo = echo
        self._condition = threading.Condition()
        self._chunks: list[str] = []
        self._last_chunk_at = time.monotonic()
        self._callback_id: str | None = None
        self._started_stream = False
        self._stream_handle = None

    @staticmethod
    def _is_streaming(transcript: Any) -> bool:
        try:
            value = getattr(transcript, "is_streaming")
            return bool(value() if callable(value) else value)
        except Exception:
            return False

    def start(self) -> "SessionTranscriptCapture":
        if self._callback_id is not None:
            return self

        if self.stream_path is not None:
            self.stream_path.parent.mkdir(parents=True, exist_ok=True)
            self._stream_handle = self.stream_path.open(
                "w", encoding="utf-8", buffering=1
            )

        try:
            self._callback_id = self.transcript.register_callback(
                self._on_chunk, keep_new_lines=True
            )
        except TypeError:
            # Older PyFluent releases do not expose the keep_new_lines keyword.
            self._callback_id = self.transcript.register_callback(self._on_chunk)

        if not self._is_streaming(self.transcript):
            self.transcript.start()
            self._started_stream = True
        return self

    def close(self) -> None:
        if self._callback_id is not None:
            try:
                self.transcript.unregister_callback(self._callback_id)
            except Exception:
                pass
            self._callback_id = None

        # Do not stop a transcript stream that was already owned by the session.
        if self._started_stream:
            try:
                self.transcript.stop()
            except Exception:
                pass
            self._started_stream = False

        if self._stream_handle is not None:
            self._stream_handle.flush()
            self._stream_handle.close()
            self._stream_handle = None

    def __enter__(self) -> "SessionTranscriptCapture":
        return self.start()

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    def _on_chunk(self, chunk: Any) -> None:
        text = str(chunk)
        if text and not text.endswith("\n"):
            text += "\n"
        now = time.monotonic()
        with self._condition:
            self._chunks.append(text)
            self._last_chunk_at = now
            if self._stream_handle is not None:
                self._stream_handle.write(text)
                self._stream_handle.flush()
            if self.echo:
                print(text, end="", flush=True)
            self._condition.notify_all()

    def mark(self) -> int:
        with self._condition:
            return len(self._chunks)

    def text_since(self, marker: int) -> str:
        with self._condition:
            return "".join(self._chunks[marker:])

    def wait_until_quiet(
        self,
        *,
        quiet_seconds: float = 0.25,
        timeout_seconds: float = 5.0,
    ) -> bool:
        deadline = time.monotonic() + max(timeout_seconds, 0.0)
        with self._condition:
            while True:
                remaining_quiet = quiet_seconds - (
                    time.monotonic() - self._last_chunk_at
                )
                if remaining_quiet <= 0.0:
                    return True
                remaining_total = deadline - time.monotonic()
                if remaining_total <= 0.0:
                    return False
                self._condition.wait(timeout=min(remaining_quiet, remaining_total))

    @staticmethod
    def _summary_has_terminal_section(raw_output: str) -> bool:
        parsed = parse_particle_track_summary(raw_output)
        return (
            parsed.get("counts", {}).get("tracked") is not None
            and "Mass Transfer Summary" in raw_output
            and bool(parsed.get("mass_transfer_rows"))
        )

    def wait_for_dpm_summary(
        self,
        marker: int,
        *,
        timeout_seconds: float = 600.0,
        quiet_seconds: float = 1.0,
    ) -> tuple[str, bool, float]:
        """Wait for a complete Summary block followed by a quiet transcript."""
        started_at = time.monotonic()
        deadline = started_at + max(timeout_seconds, 0.0)
        with self._condition:
            while True:
                raw_output = "".join(self._chunks[marker:])
                complete = self._summary_has_terminal_section(raw_output)
                quiet = time.monotonic() - self._last_chunk_at >= quiet_seconds
                if complete and quiet:
                    return raw_output, True, time.monotonic() - started_at

                remaining = deadline - time.monotonic()
                if remaining <= 0.0:
                    return raw_output, False, time.monotonic() - started_at

                wait_for = min(0.25, remaining)
                if complete:
                    wait_for = min(
                        max(
                            quiet_seconds - (time.monotonic() - self._last_chunk_at),
                            0.01,
                        ),
                        remaining,
                    )
                self._condition.wait(timeout=wait_for)


def _write_text_immediately(path: Path | None, text: str) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def track_one_injection_streamed(
    solver: Any,
    item: Mapping[str, Any],
    collector: SessionTranscriptCapture,
    *,
    timeout_seconds: float = 600.0,
    quiet_seconds: float = 1.0,
    raw_output_path: Path | None = None,
) -> dict[str, Any]:
    """Submit one track command and wait until its transcript block is complete."""
    collector.wait_until_quiet(quiet_seconds=0.25, timeout_seconds=5.0)
    marker = collector.mark()
    name = str(item["name"])
    command = build_track_command(name)

    returned: Any = None
    command_error: str | None = None
    submitted_at = time.monotonic()
    try:
        returned = execute_tui(solver, command)
    except Exception as exc:
        command_error = f"{type(exc).__name__}: {exc}"
    command_call_seconds = time.monotonic() - submitted_at

    raw_output, transcript_complete, wait_seconds = collector.wait_for_dpm_summary(
        marker,
        timeout_seconds=timeout_seconds,
        quiet_seconds=quiet_seconds,
    )
    _write_text_immediately(raw_output_path, raw_output)

    parsed = parse_particle_track_summary(raw_output)
    parsed_ok = parsed.get("counts", {}).get("tracked") is not None
    status = "ok" if transcript_complete and parsed_ok and command_error is None else "failed"
    error_parts: list[str] = []
    if command_error:
        error_parts.append(command_error)
    if not transcript_complete:
        error_parts.append(
            f"Timed out after {wait_seconds:.1f}s before a complete quiet DPM Summary block was observed."
        )
    elif not parsed_ok:
        error_parts.append("Transcript completed but the tracked count was not parseable.")

    return {
        "index": int(item["index"]),
        "name": name,
        "diameter_um": item.get("diameter_um"),
        "status": status,
        "error": "; ".join(error_parts) or None,
        "command": command,
        "returned": repr(returned),
        "raw_output": raw_output,
        "raw_output_path": str(raw_output_path) if raw_output_path else None,
        "parsed": parsed,
        "closure": dpm_flow_closure(parsed),
        "completion": {
            "confirmed": transcript_complete,
            "safe_to_submit_next": transcript_complete,
            "wait_seconds": wait_seconds,
            "timeout_seconds": timeout_seconds,
            "quiet_seconds": quiet_seconds,
            "command_call_seconds": command_call_seconds,
        },
    }
