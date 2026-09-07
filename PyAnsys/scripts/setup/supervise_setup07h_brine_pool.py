#!/usr/bin/env python3
"""Wait for Fluent, then prepare and run setup 07h exactly once.

The supervisor is intentionally conservative: endpoint/authentication failures
are retried, but a preparation or solver failure is preserved and not rerun
blindly.  This prevents duplicate controllers and accidental checkpoint
overwrites while still allowing an overnight launch after Fluent recovers.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_resolved_brine_outlet_20260813"
    / "brine620k_07h_pool_y0_equal_psep_v1"
)
SUPERVISOR_MANIFEST = RUN_ROOT / "supervisor_manifest.json"
READINESS_LOG = RUN_ROOT / "supervisor_readiness.log"
PREPARATION_MANIFEST = RUN_ROOT / "preparation_manifest.json"
QUALIFICATION_MANIFEST = RUN_ROOT / "qualification_manifest.json"
PYTHON = str(PROJECT_ROOT / ".venv" / "bin" / "python")
SETUP_LABEL = "07h"
STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = "brine620k_07h_pool_y0_equal_psep_v1"
STATUS_SCRIPT = "scripts/connection/check_setup07h_status.py"
PREPARATION_SCRIPT = "scripts/setup/prepare_setup07h_brine_pool.py"
QUALIFICATION_SCRIPT = "scripts/setup/run_setup07h_brine_pool_qualification.py"
READINESS_REQUIRED = True
PREPARATION_IDLE_TIMEOUT_SECONDS = 1800.0


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(payload: dict[str, Any]) -> None:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    SUPERVISOR_MANIFEST.write_text(
        json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8"
    )


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def run_logged(command: list[str], log_name: str, wall_seconds: float) -> int:
    log_path = RUN_ROOT / log_name
    wrapped = [
        PYTHON,
        "scripts/connection/run_guarded.py",
        "--idle-timeout-seconds",
        str(PREPARATION_IDLE_TIMEOUT_SECONDS),
        "--wall-timeout-seconds",
        str(wall_seconds),
        "--log-file",
        str(log_path),
        "--",
        *command,
    ]
    environment = dict(os.environ)
    environment["PYTHONUNBUFFERED"] = "1"
    return subprocess.run(
        wrapped,
        cwd=PROJECT_ROOT,
        check=False,
        env=environment,
    ).returncode


def main() -> int:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    prior = load_json(SUPERVISOR_MANIFEST)
    prior_pid = int(prior.get("pid", 0) or 0)
    if (
        prior_pid > 0
        and prior_pid != os.getpid()
        and prior.get("status") in {"waiting_for_fluent", "preparing", "qualifying"}
        and process_exists(prior_pid)
    ):
        print(f"setup-{SETUP_LABEL} supervisor already active as PID {prior_pid}")
        return 0
    state: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "pid": os.getpid(),
        "status": "waiting_for_fluent",
        "started": datetime.now().astimezone().isoformat(timespec="seconds"),
        "readiness_attempts": 0,
        "policy": (
            "retry endpoint/authentication only; never repeat a failed preparation "
            "or qualification blindly"
        ),
    }
    write_json(state)

    deadline = time.monotonic() + 18.0 * 3600.0
    while READINESS_REQUIRED and time.monotonic() < deadline:
        completed = load_json(QUALIFICATION_MANIFEST)
        if completed.get("status") == "completed":
            state.update(
                {
                    "status": "completed",
                    "classification": completed.get("classification"),
                    "iterations_completed": completed.get("iterations_completed", 0),
                    "finished": datetime.now().astimezone().isoformat(timespec="seconds"),
                }
            )
            write_json(state)
            return 0 if completed.get("classification") == "accepted" else 2

        probe = subprocess.run(
            [PYTHON, STATUS_SCRIPT],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=45,
        )
        state["readiness_attempts"] += 1
        state["last_readiness_exit_code"] = probe.returncode
        state["last_readiness_check"] = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
        with READINESS_LOG.open("a", encoding="utf-8") as stream:
            stream.write(
                f"\n[{state['last_readiness_check']}] exit={probe.returncode}\n"
            )
            stream.write(probe.stdout)
            stream.write(probe.stderr)
        write_json(state)
        if probe.returncode == 0:
            break
        time.sleep(300.0)
    else:
        if not READINESS_REQUIRED:
            state.update(
                {
                    "readiness_skipped": True,
                    "readiness_skip_reason": (
                        "setup-specific direct connection avoids a second PyFluent client "
                        "immediately before preparation"
                    ),
                }
            )
            write_json(state)
        else:
            state.update(
                {
                    "status": "unresolved",
                    "error": "Fluent did not pass the bounded readiness check in 18 hours",
                    "finished": datetime.now().astimezone().isoformat(timespec="seconds"),
                }
            )
            write_json(state)
            return 1

    preparation = load_json(PREPARATION_MANIFEST)
    if preparation.get("status") != "accepted":
        state["status"] = "preparing"
        write_json(state)
        code = run_logged(
            [PYTHON, PREPARATION_SCRIPT],
            "supervisor_preparation.log",
            3600.0,
        )
        preparation = load_json(PREPARATION_MANIFEST)
        if code != 0 or preparation.get("status") != "accepted":
            state.update(
                {
                    "status": "unresolved",
                    "stage": "preparation",
                    "exit_code": code,
                    "error": preparation.get("error", "preparation did not produce accepted manifest"),
                    "finished": datetime.now().astimezone().isoformat(timespec="seconds"),
                }
            )
            write_json(state)
            return 1

    state["status"] = "qualifying"
    write_json(state)
    code = run_logged(
        [PYTHON, QUALIFICATION_SCRIPT],
        "supervisor_qualification.log",
        43200.0,
    )
    qualification = load_json(QUALIFICATION_MANIFEST)
    state.update(
        {
            "status": qualification.get("status", "unresolved"),
            "classification": qualification.get("classification", "diagnostic"),
            "iterations_completed": qualification.get("iterations_completed", 0),
            "exit_code": code,
            "error": qualification.get("error"),
            "finished": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    )
    write_json(state)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
