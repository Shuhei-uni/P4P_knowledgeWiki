#!/usr/bin/env python3
"""Preserve the current task-owned R0 control field after a requested pause."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.stage4_native import data_path, remote_file_sha256  # noqa: E402


def dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")


def native_clock(solver: Any) -> dict[str, Any]:
    result = {}
    for name in ("current-iteration", "flow-time", "time-step"):
        try:
            result[name] = solver.scheme.eval(f"(%rpgetvar '{name})")
        except Exception as exc:
            result[name] = f"{type(exc).__name__}: {exc}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-dir", type=Path, required=True)
    parser.add_argument("--remote-case", required=True)
    args = parser.parse_args()
    solver = connect(server_id="1", start_transcript=True, tcp_timeout_seconds=10)
    for _ in range(120):
        try:
            if not bool(solver.settings.solution.run_calculation.iterating()):
                break
        except Exception:
            pass
        time.sleep(1)
    else:
        raise RuntimeError("Fluent remained active; pause checkpoint not attempted")
    case = args.remote_case
    data = data_path(case)
    if remote_file_exists(solver, case) or remote_file_exists(solver, data):
        raise FileExistsError(f"pause pair already exists: {case}")
    solver.settings.file.write_case(file_name=case)
    solver.settings.file.write_data(file_name=data)
    payload = {
        "status": "PAUSED",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "remote_case": case,
        "remote_data": data,
        "native_clock": native_clock(solver),
        "methods": safe_get_state(solver.settings.solution.methods, "methods"),
        "general": safe_get_state(solver.settings.setup.general, "general"),
        "report_files": safe_get_state(solver.settings.solution.monitor.report_files, "report files"),
        "case_sha256": remote_file_sha256(solver, case, case + ".sha256.txt"),
        "data_sha256": remote_file_sha256(solver, data, data + ".sha256.txt"),
    }
    args.local_dir.mkdir(parents=True, exist_ok=True)
    dump(args.local_dir / "pause-checkpoint.json", payload)
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
