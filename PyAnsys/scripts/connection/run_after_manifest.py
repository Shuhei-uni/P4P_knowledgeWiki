#!/usr/bin/env python3
"""Run a command only after a watched job writes a valid JSON manifest."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Completion manifest to wait for.")
    parser.add_argument("--watched-pid", type=int, required=True, help="PID expected to create the manifest.")
    parser.add_argument("--timeout-seconds", type=float, default=43200.0)
    parser.add_argument("--poll-seconds", type=float, default=15.0)
    parser.add_argument("--results-csv", default="", help="Optional DPM results CSV to validate.")
    parser.add_argument("--expected-result-rows", type=int, default=0)
    parser.add_argument("--expected-injected-total", type=float, default=None)
    parser.add_argument("--mass-balance-tolerance-fraction", type=float, default=0.002)
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="KEY=JSON_VALUE",
        help="Required top-level manifest value. May be repeated.",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --.")
    return parser


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def requirements(values: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --require value: {value!r}")
        key, expected = value.split("=", 1)
        parsed[key] = json.loads(expected)
    return parsed


def valid_manifest(path: Path, expected: dict[str, Any]) -> tuple[bool, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"manifest unreadable: {exc}"
    mismatches = {
        key: {"expected": value, "actual": payload.get(key)}
        for key, value in expected.items()
        if payload.get(key) != value
    }
    if mismatches:
        return False, f"manifest requirements failed: {json.dumps(mismatches, default=str)}"
    return True, "manifest requirements verified"


def validate_results_csv(args: argparse.Namespace) -> tuple[bool, str]:
    if not args.results_csv:
        return True, "results CSV validation not requested"
    path = Path(args.results_csv).expanduser().resolve()
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        return False, f"results CSV unreadable: {exc}"
    if args.expected_result_rows and len(rows) != args.expected_result_rows:
        return False, f"results CSV has {len(rows)} rows; expected {args.expected_result_rows}"

    required = ("injected_mass_flow_kgs", "escaped_kgs", "trapped_kgs", "incomplete_kgs")
    failures: list[str] = []
    injected_total = 0.0
    for index, row in enumerate(rows, start=1):
        missing = [field for field in required if row.get(field, "").strip() == ""]
        if missing:
            failures.append(f"row {index} missing {missing}")
            continue
        injected = float(row["injected_mass_flow_kgs"])
        fate_total = sum(float(row[field]) for field in required[1:])
        tolerance = max(1e-5, injected * args.mass_balance_tolerance_fraction)
        if abs(fate_total - injected) > tolerance:
            failures.append(
                f"row {index} fate_total={fate_total:.9g}, injected={injected:.9g}, "
                f"tolerance={tolerance:.9g}"
            )
        injected_total += injected
    if args.expected_injected_total is not None:
        tolerance = max(1e-5, args.expected_injected_total * 1e-6)
        if abs(injected_total - args.expected_injected_total) > tolerance:
            failures.append(
                f"injected total={injected_total:.9g}; expected={args.expected_injected_total:.9g}"
            )
    if failures:
        return False, "results CSV validation failed: " + "; ".join(failures)
    return True, f"results CSV verified: {len(rows)} rows, injected_total={injected_total:.9g} kg/s"


def main() -> int:
    args = build_parser().parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        print("No command supplied after --", file=sys.stderr)
        return 2

    manifest = Path(args.manifest).expanduser().resolve()
    expected = requirements(args.require)
    deadline = time.monotonic() + args.timeout_seconds
    next_heartbeat = 0.0
    print(f"waiting_for_manifest: {manifest}", flush=True)
    print(f"watched_pid: {args.watched_pid}", flush=True)
    print(f"requirements: {json.dumps(expected, default=str)}", flush=True)

    while time.monotonic() < deadline:
        if manifest.is_file():
            valid, reason = valid_manifest(manifest, expected)
            if not valid:
                print(reason, file=sys.stderr, flush=True)
                return 1
            print(reason, flush=True)
            valid, reason = validate_results_csv(args)
            if not valid:
                print(reason, file=sys.stderr, flush=True)
                return 1
            print(reason, flush=True)
            print(f"launching: {' '.join(command)}", flush=True)
            return subprocess.run(command, check=False).returncode
        if not process_exists(args.watched_pid):
            print("watched process exited before producing the completion manifest", file=sys.stderr)
            return 1
        now = time.monotonic()
        if now >= next_heartbeat:
            print("waiting: Case 1 is still running", flush=True)
            next_heartbeat = now + 300.0
        time.sleep(args.poll_seconds)

    print("timeout waiting for completion manifest", file=sys.stderr)
    return 124


if __name__ == "__main__":
    raise SystemExit(main())
