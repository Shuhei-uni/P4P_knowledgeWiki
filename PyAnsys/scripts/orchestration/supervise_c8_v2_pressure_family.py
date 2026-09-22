#!/usr/bin/env python3
"""Sequentially execute the corrected C8-D0 parent and pressure ladder.

This supervisor is intentionally conservative: one Server-3 child at a time,
fresh v2 all-wall parent identity for every pressure child, and no continuation
after a blocked child.  It is suitable for detached execution on the laptop;
the Fluent cases/checkpoints remain on Server 3 as declared by the arguments.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", required=True)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--server-id", default="3")
    ap.add_argument("--baseline-case", required=True)
    ap.add_argument("--baseline-data", required=True)
    ap.add_argument("--checkpoint-root", required=True)
    ap.add_argument("--final-root", required=True)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--stamp", required=True)
    args = ap.parse_args()
    root = args.root.resolve(); trigger = root / "c8-v2-trigger-receipt.json"; supervisor_manifest = root / "supervisor-manifest.json"
    state: dict[str, Any] = {"status": "RUNNING", "family": "P71A-C8-V2-DYNAMIC-THIN-OUTER", "server_id": args.server_id, "started_at": datetime.now(timezone.utc).isoformat(), "steps": []}
    write(supervisor_manifest, state)
    sys.path.insert(0, str(args.repo / "PyAnsys/src"))
    from pyansys_fluent.connection import connect
    solver = connect(args.server_id, start_transcript=False, tcp_timeout_seconds=5)
    while solver.settings.solution.run_calculation.iterating():
        state["waiting_for_server3_idle"] = True; state["last_wait_at"] = datetime.now(timezone.utc).isoformat(); write(supervisor_manifest, state)
        time.sleep(60)
    state["waiting_for_server3_idle"] = False; write(supervisor_manifest, state)
    setup_script = args.repo / "PyAnsys/scripts/setup/run_c8_v2_all_wall_development.py"
    cmd = [args.python, str(setup_script), "--server-id", args.server_id, "--parent-case", args.baseline_case, "--parent-data", args.baseline_data, "--checkpoint-root", args.checkpoint_root, "--final-root", args.final_root, "--local-dir", str(root / "c8-d0-v2"), "--stamp", args.stamp, "--trigger-receipt", str(trigger)]
    result = subprocess.run(cmd, cwd=args.repo)
    state["steps"].append({"step": "C8-D0-V2", "returncode": result.returncode, "manifest": str(root / "c8-d0-v2" / "run-manifest.json")}); write(supervisor_manifest, state)
    if result.returncode != 0 or not trigger.exists():
        state.update({"status": "BLOCKED", "failed_step": "C8-D0-V2", "completed_at": datetime.now(timezone.utc).isoformat()}); write(supervisor_manifest, state); return 1
    d0_manifest = root / "c8-d0-v2" / "run-manifest.json"
    d0 = json.loads(d0_manifest.read_text(encoding="utf-8")); parent_case = d0["artifacts"]["active5000"]; parent_data = parent_case.replace(".cas.h5", ".dat.h5")
    pressures = ("C8-P0", "C8-P10", "C8-P30", "C8-P60")
    pressure_script = args.repo / "PyAnsys/scripts/setup/run_c8_v2_dynamic_thin_outer.py"
    for index, case in enumerate(pressures, start=1):
        child = root / case.lower(); child_stamp = f"{args.stamp}-{case.lower()}"
        cmd = [args.python, str(pressure_script), "--server-id", args.server_id, "--case", case, "--parent-case", parent_case, "--parent-data", parent_data, "--checkpoint-root", args.checkpoint_root, "--final-root", args.final_root, "--local-dir", str(child), "--stamp", child_stamp, "--threshold-kg", json.loads(trigger.read_text(encoding="utf-8"))["threshold_kg"].__str__(), "--trigger-receipt", str(trigger)]
        result = subprocess.run(cmd, cwd=args.repo)
        child_manifest = child / "run-manifest.json"; state["steps"].append({"step": case, "returncode": result.returncode, "manifest": str(child_manifest)}); write(supervisor_manifest, state)
        if result.returncode != 0:
            state.update({"status": "BLOCKED", "failed_step": case, "completed_at": datetime.now(timezone.utc).isoformat()}); write(supervisor_manifest, state); return 1
    state.update({"status": "COMPLETE", "completed_at": datetime.now(timezone.utc).isoformat(), "pressure_parent": parent_case, "trigger_receipt": str(trigger)}); write(supervisor_manifest, state); return 0


if __name__ == "__main__": raise SystemExit(main())
