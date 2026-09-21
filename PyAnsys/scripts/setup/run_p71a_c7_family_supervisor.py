#!/usr/bin/env python3
"""Keep the four C7 inlet-development cases moving through paired checkpoints.

The individual C7 runner remains the authority for Fluent configuration and
evidence.  This wrapper only waits for an owned runner to exit, identifies the
newest durable paired checkpoint recorded by its manifest, and starts a fresh
continuation.  It never attaches to or terminates the independent C8 Server-3
process.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv" / "bin" / "python"
RUNNER = ROOT / "scripts" / "setup" / "run_p71a_c7_inlet_development.py"
OUT = ROOT / "output" / "phase07_c7"
# The student-visible OneDrive prepared pair is the scientific source.  Keep
# the same verified parent for each unfinished child; checkpoints stay on the
# student's local disk and only terminal pairs are published to OneDrive.
SERVER_ID = "student"
PREPARED = r"C:\Users\Shuhei Yokkaichi\OneDrive\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase07\C7\20260921T000000Z\P71A-thin-outer-baseline-prepared.cas.h5"
PREPARED_DATA = PREPARED.replace(".cas.h5", ".dat.h5")
CHECKPOINT_ROOT = r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\C7\student-continuations"
FINAL_ROOT = r"C:\Users\Shuhei Yokkaichi\OneDrive\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase07\C7\finals"
BUILD_RECEIPT = OUT / "c7-all-wall-build-manifest.json"
CASES = ("C7-R0", "C7-R25", "C7-R50", "C7-R75")


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def owned_runner_running() -> bool:
    out = subprocess.run(
        ["ps", "-ax", "-o", "command="], capture_output=True, text=True, check=True
    ).stdout
    # Scope the wait to this C7 family on student.  An independent C8 runner on
    # Server 3 is deliberately allowed to remain alive.
    return "run_p71a_c7_inlet_development.py --case C7-" in out


def wait_for_owned_runner() -> None:
    while owned_runner_running():
        time.sleep(30)


def manifests(case: str) -> list[Path]:
    return sorted(OUT.glob(f"{case}*/run-manifest.json"), key=lambda p: p.stat().st_mtime)


def latest_case_manifest(case: str) -> Path | None:
    ms = manifests(case)
    return ms[-1] if ms else None


def checkpoint_from_manifest(path: Path) -> tuple[int, str, str] | None:
    """Return newest paired checkpoint recorded by a blocked/running manifest."""
    m = load(path)
    candidates: list[tuple[int, str, str]] = []
    # The manifest predeclares every target path before the run starts.  Those
    # paths are not evidence of a saved checkpoint.  Only events emitted after
    # ``save_pair`` has verified both remote files are eligible here.
    for event in m.get("events", []):
        active = event.get("active_iteration")
        case = event.get("checkpoint_case")
        if isinstance(active, int) and case and active in (1000, 2000, 3000, 4000):
            candidates.append((active, str(case), str(case).replace(".cas.h5", ".dat.h5")))
    if not candidates:
        return None
    return max(candidates, key=lambda x: x[0])


def complete_manifest(case: str) -> Path | None:
    for path in reversed(manifests(case)):
        try:
            if load(path).get("status") == "COMPLETE" and load(path).get("achieved_active_iterations") == 5000:
                return path
        except Exception:
            continue
    return None


def launch(case: str, parent_case: str, parent_data: str, receipt: Path, start: int, label: str) -> Path:
    stamp = now_stamp()
    local = OUT / f"{case}-supervisor-{start:04d}-{stamp}"
    cmd = [
        str(PYTHON), str(RUNNER), "--case", case,
        "--parent-case", parent_case, "--parent-data", parent_data,
        "--checkpoint-root", CHECKPOINT_ROOT, "--final-root", FINAL_ROOT,
        "--local-dir", str(local), "--server-id", SERVER_ID, "--stamp", stamp,
        "--parent-identity-receipt", str(receipt), "--family-label", label,
        "--start-active", str(start),
    ]
    log = local.with_suffix(".supervisor.log")
    local.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as stream:
        stream.write("COMMAND: " + " ".join(cmd) + "\n")
        stream.flush()
        result = subprocess.run(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode == 0:
        return local / "run-manifest.json"
    return local / "run-manifest.json"


def run_case(case: str, initial_parent: tuple[str, str, Path], initial_start: int = 0) -> Path:
    parent_case, parent_data, receipt = initial_parent
    start = initial_start
    label = "P71A-INLET-DEVELOPMENT-RAMP"
    last_receipt = receipt
    while True:
        if complete_manifest(case):
            return complete_manifest(case)  # type: ignore[return-value]
        wait_for_owned_runner()
        # A runner that was already in progress before this supervisor was
        # started may have saved a newer checkpoint than its initial parent.
        # Adopt that checkpoint before launching any fresh child.
        current = latest_case_manifest(case)
        if current:
            try:
                checkpoint = checkpoint_from_manifest(current)
            except Exception:
                checkpoint = None
            if checkpoint is not None and checkpoint[0] > start:
                start, parent_case, parent_data = checkpoint
                last_receipt = current
        path = launch(case, parent_case, parent_data, last_receipt, start, label)
        try:
            m = load(path)
        except Exception:
            time.sleep(10)
            continue
        if m.get("status") == "COMPLETE" and m.get("achieved_active_iterations") == 5000:
            return path
        checkpoint = checkpoint_from_manifest(path)
        if checkpoint is None or checkpoint[0] <= start:
            # Give Fluent/Server 1 a short recovery window, then retry from
            # the same verified parent.  The child directory is never reused.
            time.sleep(30)
            continue
        start, parent_case, parent_data = checkpoint
        last_receipt = path


def main() -> int:
    # This supervisor is intentionally single-owner and serial.  It may be
    # started while an existing C7 runner is active; it waits before creating
    # its first continuation and never considers the Server-3 C8 runner.
    for case in CASES:
        if case == "C7-R0":
            # The currently active resumed R0 run is discovered from its latest
            # manifest.  Its parent is the durable active-2000 pair already in
            # that manifest, so do not restart from the prepared parent.
            existing = latest_case_manifest(case)
            if existing:
                m = load(existing)
                parent = (m.get("parent_case"), m.get("parent_data"), existing)
                if not parent[0] or not parent[1]:
                    parent = (PREPARED, PREPARED_DATA, BUILD_RECEIPT)
            else:
                parent = (PREPARED, PREPARED_DATA, BUILD_RECEIPT)
        else:
            parent = (PREPARED, PREPARED_DATA, BUILD_RECEIPT)
        initial_start = 0
        if case == "C7-R0" and existing:
            initial_start = int(load(existing).get("start_active_iteration", 0))
        run_case(case, parent, initial_start)  # type: ignore[arg-type]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
