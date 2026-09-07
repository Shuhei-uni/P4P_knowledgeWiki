#!/usr/bin/env python3
"""Run the guarded setup-07f sink thickness/rate matrix sequentially."""

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
STUDY_ID = "split_inlet_sink_thickness_rate_matrix_20260811"
STUDY_DIR = PROJECT_ROOT / "output" / STUDY_ID
QUEUE_MANIFEST = STUDY_DIR / "queue_manifest.json"
LOCK_FILE = STUDY_DIR / "controller.lock"
RUNNER = Path(__file__).with_name("run_setup07d_from_prepared07c.py")

CASES = (
    {
        "run_label": "mesh-900k_band0p280331_tau0p020_v3_rpc25",
        "thickness_m": 0.28033050723644936,
        "tau_s": 0.020,
        "purpose": "isolate a 2x band-thickness change at the qualified 07d rate",
    },
    {
        "run_label": "mesh-900k_band0p280331_tau0p005_v6_single_controller",
        "thickness_m": 0.28033050723644936,
        "tau_s": 0.005,
        "purpose": "isolate a 4x sink-rate increase at the doubled thickness",
    },
    {
        "run_label": "mesh-900k_band0p420496_tau0p005_v6_single_controller",
        "thickness_m": 0.42049576085467404,
        "tau_s": 0.005,
        "purpose": "isolate a further 1.5x band-thickness increase at the faster rate",
    },
)


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_manifest(payload: dict[str, Any]) -> None:
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    temporary = QUEUE_MANIFEST.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(QUEUE_MANIFEST)


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_lock() -> None:
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            old_pid = -1
        if old_pid > 0 and process_exists(old_pid):
            raise RuntimeError(f"setup-07f controller already active as PID {old_pid}")
        LOCK_FILE.unlink(missing_ok=True)
    descriptor = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(f"{os.getpid()}\n")


def terminal_case_manifest(run_label: str) -> dict[str, Any] | None:
    path = STUDY_DIR / run_label / "qualification_manifest.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if payload.get("status") in {"completed", "failed"} else None


def main() -> int:
    acquire_lock()
    queue: dict[str, Any] = {
        "study_id": STUDY_ID,
        "status": "running",
        "classification": "diagnostic sink thickness/rate matrix",
        "controller_pid": os.getpid(),
        "started_at": now(),
        "clean_origin": (
            "each case restores setup-07c's clean-original prepared checkpoint, "
            "changes only the RP sink thickness/tau controls, and fresh Hybrid Initializes"
        ),
        "dpm": "off; no injection update or tracking",
        "case_order": [case["run_label"] for case in CASES],
        "cases": [],
    }
    write_manifest(queue)
    exit_code = 0
    try:
        for index, case in enumerate(CASES, start=1):
            previous = terminal_case_manifest(case["run_label"])
            if previous is not None:
                queue["cases"].append(
                    {
                        **case,
                        "queue_index": index,
                        "status": "skipped_existing_terminal",
                        "terminal_status": previous.get("status"),
                        "classification": previous.get("classification"),
                    }
                )
                write_manifest(queue)
                continue

            entry = {
                **case,
                "queue_index": index,
                "status": "running",
                "started_at": now(),
            }
            queue["active_run_label"] = case["run_label"]
            queue["cases"].append(entry)
            write_manifest(queue)

            command = [
                sys.executable,
                str(RUNNER),
                "--study-id",
                STUDY_ID,
                "--run-label",
                case["run_label"],
                "--setup-branch",
                "07f guarded sink thickness/rate diagnostic matrix",
                "--initial-tau-s",
                str(case["tau_s"]),
                "--layer-thickness-m",
                str(case["thickness_m"]),
                "--minimum-r1-iterations",
                "1000",
                "--maximum-r1-iterations",
                "2000",
                "--block",
                "25",
                "--static-mask-schedule",
            ]
            result = subprocess.run(command, check=False)
            case_manifest = terminal_case_manifest(case["run_label"])
            entry.update(
                {
                    "status": "completed" if result.returncode == 0 else "failed",
                    "return_code": result.returncode,
                    "completed_at": now(),
                    "terminal_manifest_status": (
                        case_manifest.get("status") if case_manifest else None
                    ),
                    "classification": (
                        case_manifest.get("classification") if case_manifest else None
                    ),
                    "stop_reason": (
                        case_manifest.get("stop_reason") if case_manifest else None
                    ),
                }
            )
            write_manifest(queue)
            if result.returncode != 0 or case_manifest is None:
                exit_code = result.returncode or 1
                queue["status"] = "stopped_after_case_failure"
                queue["stop_reason"] = (
                    f"{case['run_label']} did not produce a valid terminal manifest"
                )
                break

        if exit_code == 0:
            queue["status"] = "completed"
            queue["stop_reason"] = "all queued cases reached terminal controller states"
        queue.pop("active_run_label", None)
        queue["completed_at"] = now()
        write_manifest(queue)
        return exit_code
    finally:
        LOCK_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
