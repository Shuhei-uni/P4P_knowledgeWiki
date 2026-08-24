#!/usr/bin/env python3
"""Shared utilities for remote Fluent automation scripts."""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any


_CONNECTIVITY_NODE_ROW = re.compile(
    r"^\s*n(?P<node_id>\d+)\*?\s+\S+\s+"
    r"(?P<core_index>\d+)/(?P<hardware_cores>\d+)\s+",
    re.MULTILINE,
)


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


def parse_parallel_connectivity_roster(text: str) -> dict[str, Any]:
    """Parse Fluent's connectivity table without confusing cores and ranks."""

    rows = [
        {
            "node_id": int(match.group("node_id")),
            "core_index": int(match.group("core_index")),
            "hardware_cores": int(match.group("hardware_cores")),
        }
        for match in _CONNECTIVITY_NODE_ROW.finditer(text)
    ]
    unique_rows = {row["node_id"]: row for row in rows}
    if not unique_rows:
        raise RuntimeError(
            "path/version issue: Fluent parallel connectivity output contained no compute-node rows"
        )
    node_ids = sorted(unique_rows)
    expected_ids = list(range(node_ids[-1] + 1))
    if node_ids != expected_ids:
        raise RuntimeError(
            "invalid value/format issue: Fluent parallel connectivity node IDs "
            f"are not contiguous from zero: actual={node_ids}"
        )
    return {
        "compute_node_count": len(node_ids),
        "compute_node_ids": node_ids,
        "hardware_core_counts": sorted(
            {row["hardware_cores"] for row in unique_rows.values()}
        ),
        "rows": [unique_rows[node_id] for node_id in node_ids],
    }


def capture_parallel_connectivity_roster(solver: Any) -> dict[str, Any]:
    """Capture and parse Fluent's read-only parallel connectivity report."""

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        result = solver.settings.parallel.show_connectivity(compute_node=0)
        time.sleep(1.0)
        if result is not None:
            print(result)
    text = buffer.getvalue()
    parsed = parse_parallel_connectivity_roster(text)
    parsed["raw_report"] = text
    return parsed


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
