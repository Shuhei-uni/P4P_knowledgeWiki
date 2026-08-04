#!/usr/bin/env python3
"""Report local Purnanto sweep progress without connecting to Fluent."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "enthalpy_sweep_verified_20260721_v2"
CASE_LABELS = {
    1: "1600 -25%",
    2: "1440",
    3: "1520",
    4: "1600",
    5: "1680",
    6: "1760",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--watch", action="store_true", help="Refresh until interrupted.")
    parser.add_argument("--interval", type=float, default=10.0, help="Watch refresh interval in seconds.")
    return parser


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, ValueError):
        return False
    except PermissionError:
        return True
    return True


def active_pid_files(log_dir: Path) -> list[tuple[str, int]]:
    active: list[tuple[str, int]] = []
    for path in sorted(log_dir.glob("*.pid")):
        try:
            pid = int(path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            continue
        if process_exists(pid):
            active.append((path.stem, pid))
    return active


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def completed_cases(output_dir: Path) -> dict[int, Path]:
    completed: dict[int, Path] = {}
    for path in output_dir.glob("case_*_manifest.json"):
        payload = load_json(path)
        if not payload:
            continue
        match = re.search(r"Case\s+(\d+)", str(payload.get("case", "")), flags=re.IGNORECASE)
        if not match:
            continue
        case_number = int(match.group(1))
        verified = payload.get("verified_completed_iterations", payload.get("iterations_verified"))
        if verified != 1500:
            continue
        previous = completed.get(case_number)
        if previous is None or path.stat().st_mtime > previous.stat().st_mtime:
            completed[case_number] = path
    return completed


def quality_from_manifest(manifest: Path) -> float | None:
    summary_path = manifest.with_name(manifest.name.replace("_manifest.json", "_case_summary.csv"))
    if not summary_path.is_file():
        return None
    try:
        with summary_path.open(newline="", encoding="utf-8-sig") as handle:
            row = next(csv.DictReader(handle))
        gas = float(row["gas_mass_flow_kgs"])
        escaped = float(row["escaped_kgs"])
    except (OSError, StopIteration, KeyError, TypeError, ValueError):
        return None
    denominator = gas + escaped
    return gas / denominator * 100.0 if denominator else None


def newest_run_log(log_dir: Path) -> Path | None:
    excluded = ("launcher", "caffeinate", "stop_after", "handoff")
    candidates = [
        path
        for path in log_dir.glob("*.log")
        if not any(token in path.name for token in excluded) and path.stat().st_size > 0
    ]
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None


def parse_log(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    case_matches = list(
        re.finditer(r"^=== (?:Run|Continue) Case\s+(\d+)\s+/\s+(.+?)\s+===$", text, re.MULTILINE)
    )
    progress_matches = list(re.finditer(r"^progress:\s+(\d+)/(\d+)\s*$", text, re.MULTILINE))
    residual_matches = list(re.finditer(r"^\s*(\d+)\s+[0-9.eE+\-]+(?:\s+[0-9.eE+\-]+){6}", text, re.MULTILINE))
    case_number = int(case_matches[-1].group(1)) if case_matches else None
    condition = case_matches[-1].group(2).strip() if case_matches else None
    progress = (
        (int(progress_matches[-1].group(1)), int(progress_matches[-1].group(2)))
        if progress_matches
        else None
    )
    latest_iteration = int(residual_matches[-1].group(1)) if residual_matches else None
    error_matches = list(re.finditer(r"^(?:RuntimeError|[A-Za-z]+Error):\s+(.+)$", text, re.MULTILINE))
    completed = "=== Sweep Complete ===" in text or "=== Continuation Complete ===" in text
    return {
        "case_number": case_number,
        "condition": condition,
        "progress": progress,
        "latest_iteration": latest_iteration,
        "error": error_matches[-1].group(0) if error_matches else "",
        "completed": completed,
    }


def age_text(seconds: float) -> str:
    seconds = max(0, int(seconds))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def render(output_dir: Path) -> str:
    log_dir = output_dir / "logs"
    active = active_pid_files(log_dir)
    completed = completed_cases(output_dir)
    run_log = newest_run_log(log_dir)
    now = time.time()

    lines = [f"Purnanto sweep status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for case_number, condition in CASE_LABELS.items():
        manifest = completed.get(case_number)
        if manifest:
            quality = quality_from_manifest(manifest)
            suffix = f", steam quality {quality:.3f}%" if quality is not None else ""
            lines.append(f"[DONE]    Case {case_number}: {condition}, 1500 iterations{suffix}")
        else:
            lines.append(f"[PENDING] Case {case_number}: {condition}")

    lines.append("")
    if run_log:
        parsed = parse_log(run_log)
        age = now - run_log.stat().st_mtime
        lines.append(f"Latest log: {run_log.name} (updated {age_text(age)} ago)")
        if parsed["case_number"] is not None:
            lines.append(f"Active/logged case: Case {parsed['case_number']} / {parsed['condition']}")
        if parsed["latest_iteration"] is not None:
            lines.append(f"Latest Fluent iteration: {parsed['latest_iteration']}")
        if parsed["progress"]:
            current, total = parsed["progress"]
            lines.append(f"Controller progress: {current}/{total}")
        if parsed["error"]:
            lines.append(f"Last error in log: {parsed['error']}")
    else:
        lines.append("Latest log: none")

    lines.append("")
    if active:
        lines.append("Active background processes:")
        lines.extend(f"  {name}: PID {pid}" for name, pid in active)
    else:
        lines.append("Active background processes: none")
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    if not output_dir.is_dir():
        print(f"Output directory not found: {output_dir}")
        return 1
    try:
        while True:
            if args.watch:
                print("\033[2J\033[H", end="")
            print(render(output_dir), flush=True)
            if not args.watch:
                return 0
            time.sleep(max(1.0, args.interval))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
