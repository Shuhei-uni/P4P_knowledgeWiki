#!/usr/bin/env python3
"""Queue later setup-07m ramp stages without creating a second Fluent writer."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN_ROOT = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_resolved_brine_outlet_20260813"
    / "brine620k_07m_pressure_opening_campaign_v1"
)
CURRENT_MANIFEST = (
    CAMPAIGN_ROOT
    / "progressive_micro_ramp_dt1e-7_inner100"
    / "ramp_manifest.json"
)
PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
STAGE_SCRIPT = PROJECT_ROOT / "scripts" / "setup" / "run_setup07m_progressive_ramp_stage.py"


def wait_for_manifest(path: Path, *, timeout_s: float) -> dict:
    started = time.monotonic()
    last_status = "missing"
    while time.monotonic() - started < timeout_s:
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = {}
            status = str(payload.get("status", "unknown"))
            if status != last_status:
                print(f"07m queue: {path.parent.name} status={status}", flush=True)
                last_status = status
            if status in {"completed", "failed"}:
                return payload
        print("07m queue: waiting for active ramp stage", flush=True)
        time.sleep(30)
    raise TimeoutError(f"timed out waiting for {path}")


def run_stage(stage: str, server_id: str) -> None:
    command = [str(PYTHON), str(STAGE_SCRIPT), stage, "--server-id", server_id]
    print(f"07m queue: launching stage={stage}", flush=True)
    completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"setup-07m stage {stage} exited {completed.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    parser.add_argument("--wait-timeout-seconds", type=float, default=43200.0)
    args = parser.parse_args()

    current = wait_for_manifest(CURRENT_MANIFEST, timeout_s=args.wait_timeout_seconds)
    if current.get("status") != "completed":
        print("07m queue: current stage failed; later stages withheld", flush=True)
        return 2
    # Allow the preceding PyFluent process to close its channel after writing
    # the terminal manifest.  No Fluent client exists in this supervisor.
    time.sleep(15)
    run_stage("mid", args.server_id)
    time.sleep(15)
    run_stage("high", args.server_id)
    print("07m queue: all configured ramp stages completed", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
