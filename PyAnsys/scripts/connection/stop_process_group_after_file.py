#!/usr/bin/env python3
"""Stop a detached process group once a completion marker file exists."""

from __future__ import annotations

import argparse
import os
import signal
import time
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-file", required=True)
    parser.add_argument("--process-group-pid", type=int, required=True)
    parser.add_argument("--poll-seconds", type=float, default=0.25)
    parser.add_argument("--timeout-seconds", type=float, default=172800.0)
    parser.add_argument("--log-file", required=True)
    return parser


def append_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def process_group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def main() -> int:
    args = build_parser().parse_args()
    target = Path(args.target_file).expanduser().resolve()
    log_path = Path(args.log_file).expanduser().resolve()
    deadline = time.monotonic() + args.timeout_seconds
    append_log(log_path, f"armed target={target} pgid={args.process_group_pid}")

    while time.monotonic() < deadline:
        if target.is_file():
            append_log(log_path, "completion marker detected; sending SIGTERM")
            try:
                os.killpg(args.process_group_pid, signal.SIGTERM)
            except ProcessLookupError:
                append_log(log_path, "process group had already exited")
                return 0
            append_log(log_path, "SIGTERM sent; Case 1 outputs were already complete")
            return 0
        if not process_group_exists(args.process_group_pid):
            append_log(log_path, "process group exited before completion marker appeared")
            return 1
        time.sleep(max(0.05, args.poll_seconds))

    append_log(log_path, "timeout expired before completion marker appeared")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
