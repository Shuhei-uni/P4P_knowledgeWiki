#!/usr/bin/env python3
"""Request safe termination of the current worker-owned Fluent generation."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.phase1_hardening import (  # noqa: E402
    submit_generation_termination_request,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Publish a generation-pinned local control request. The owning host "
            "worker closes its Windows Job Object; callers never inspect or log "
            "server-info credentials and never guess a Fluent child PID."
        )
    )
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--request-id", default="")
    parser.add_argument("--expected-worker-boot-id", default="")
    parser.add_argument("--expected-generation", type=int, default=0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    work_dir = Path(args.work_dir).expanduser().resolve()
    status_path = work_dir / "host-worker-status.json"
    if not status_path.is_file():
        print(f"Host-worker status does not exist: {status_path}", file=sys.stderr)
        return 2
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read host-worker status: {exc}", file=sys.stderr)
        return 2
    expected_boot = args.expected_worker_boot_id or str(status.get("worker_boot_id") or "")
    expected_generation = args.expected_generation or int(status.get("generation") or 0)
    request_id = args.request_id or f"terminate-generation-{expected_generation}-{uuid.uuid4().hex[:8]}"
    if status.get("state") != "running":
        print(
            f"Host worker is not running: {status.get('state')!r}",
            file=sys.stderr,
        )
        return 2
    try:
        path = submit_generation_termination_request(
            work_dir,
            request_id=request_id,
            expected_worker_boot_id=expected_boot,
            expected_fluent_generation=expected_generation,
        )
    except Exception as exc:
        print(f"Could not submit termination request: {exc}", file=sys.stderr)
        return 1
    print(f"Submitted control request: {request_id}")
    print(f"Incoming file: {path}")
    print(f"Expected worker boot ID: {expected_boot}")
    print(f"Expected Fluent generation: {expected_generation}")
    print(f"Receipt path: {work_dir / 'control' / 'receipts' / (request_id + '.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
