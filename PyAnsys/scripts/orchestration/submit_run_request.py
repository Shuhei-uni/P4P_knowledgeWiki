#!/usr/bin/env python3
"""Validate and atomically submit one narrow Fluent run request."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.run_worker import (  # noqa: E402
    RunRequest,
    RunRequestError,
    submit_run_request,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Submit a strict load/run/checkpoint/save request. Resume checkpoint "
            "selection remains the laptop agent's responsibility."
        )
    )
    parser.add_argument("request_json", help="Path to a run-request JSON file.")
    parser.add_argument(
        "--bridge-dir",
        default=os.getenv("FLUENT_BRIDGE_DIR", ""),
        help="Private shared bridge directory. Defaults to FLUENT_BRIDGE_DIR.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    bridge_dir = Path(args.bridge_dir).expanduser()
    if not args.bridge_dir or not bridge_dir.is_absolute():
        print("An absolute FLUENT_BRIDGE_DIR or --bridge-dir is required.", file=sys.stderr)
        return 2
    try:
        request = RunRequest.from_path(Path(args.request_json).expanduser())
        destination = submit_run_request(bridge_dir, request)
    except (OSError, ValueError, RunRequestError) as exc:
        print(f"Run request was not submitted: {exc}", file=sys.stderr)
        return 1
    print(f"Submitted run request: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
