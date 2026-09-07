#!/usr/bin/env python3
"""Report setup-07j progress without connecting to Fluent."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import prepare_setup07j_transient_vof as prepare07j  # noqa: E402


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def age(value: Any) -> str:
    try:
        seconds = max(0, int(time.time() - float(value)))
    except (TypeError, ValueError):
        return "unknown"
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    args = parser.parse_args()
    run_root = prepare07j.local_root_for_server(args.server_id)
    supervisor = load_json(run_root / "supervisor_manifest.json")
    preparation = load_json(run_root / "preparation_manifest.json")
    qualification = load_json(run_root / "qualification_manifest.json")

    print(
        "Setup 07j local status - "
        + datetime.now().astimezone().isoformat(timespec="seconds")
    )
    print(f"Server id: {args.server_id}")
    print(f"Run label: {prepare07j.run_label_for_server(args.server_id)}")
    print(
        "Supervisor: "
        f"{supervisor.get('status', 'not started')}"
        f" | PID {supervisor.get('pid', 'n/a')}"
        f" | heartbeat age {age(supervisor.get('heartbeat_epoch'))}"
    )
    print(
        "Preparation: "
        f"{preparation.get('status', 'not started')}"
        f" | {preparation.get('classification', 'no classification')}"
    )
    print(
        "Qualification: "
        f"{qualification.get('status', 'not started')}"
        f" | {qualification.get('classification', 'no classification')}"
        f" | steps {qualification.get('time_steps_completed', 0)}/"
        f"{qualification.get('target_time_steps', supervisor.get('target_steps', 0))}"
    )
    checkpoints = qualification.get("checkpoints") or preparation.get("prepared_checkpoint") or {}
    print(f"Checkpoints: {', '.join(map(str, checkpoints)) if checkpoints else 'none'}")
    error = qualification.get("error") or preparation.get("error") or supervisor.get("error")
    if error:
        print(f"Latest error: {error}")
    print("Local-only check: no Fluent connection, settings, or calculations were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
