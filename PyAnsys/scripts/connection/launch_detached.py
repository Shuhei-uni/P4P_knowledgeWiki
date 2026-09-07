#!/usr/bin/env python3
"""Launch a long-running command detached from the current terminal."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch a command detached and write a PID file.")
    parser.add_argument("--pid-file", required=True, help="File that receives the launched process PID.")
    parser.add_argument("--launcher-log", required=True, help="File receiving launcher stdout/stderr.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("No command supplied. Use: launch_detached.py --pid-file PID --launcher-log LOG -- command ...")
        return 2

    pid_path = Path(args.pid_file).expanduser().resolve()
    launcher_log_path = Path(args.launcher_log).expanduser().resolve()
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    launcher_log_path.parent.mkdir(parents=True, exist_ok=True)

    log_handle = launcher_log_path.open("a", encoding="utf-8")
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
        close_fds=True,
        cwd=os.getcwd(),
    )
    pid_path.write_text(f"{process.pid}\n", encoding="utf-8")
    print(f"launched_pid: {process.pid}")
    print(f"pid_file: {pid_path}")
    print(f"launcher_log: {launcher_log_path}")
    print(f"command: {' '.join(command)}")
    log_handle.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
