#!/usr/bin/env python3
"""Shared utilities for remote Fluent automation scripts."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any


def bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def quote_scheme_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def remote_file_exists(solver: Any, path_text: str) -> bool:
    quoted = quote_scheme_string(path_text)
    return bool(solver.scheme.eval(f'(file-exists? "{quoted}")'))


def remote_chdir(solver: Any, path_text: str) -> None:
    quoted = quote_scheme_string(path_text)
    solver.scheme.eval(f'(chdir "{quoted}")')


def safe_get_state(obj: Any, label: str) -> Any:
    try:
        state = obj.get_state()
        if isinstance(state, Mapping):
            return dict(state)
        return state
    except Exception as exc:
        return {"_capture_error": f"{label}: {type(exc).__name__}: {exc}"}


def try_action(label: str, func: Callable[[], Any], *, critical: bool = False) -> bool:
    try:
        func()
        print(f"{label}: OK", flush=True)
        return True
    except Exception as exc:
        print(f"{label}: FAILED -> {exc}", flush=True)
        if critical:
            raise RuntimeError(f"{label} failed") from exc
        return False


def write_json_snapshot(path_text: str, payload: Mapping[str, Any]) -> None:
    if not path_text.strip():
        return
    path = Path(path_text).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"snapshot_json: {path}", flush=True)
