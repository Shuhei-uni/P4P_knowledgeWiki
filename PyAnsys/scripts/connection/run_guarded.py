#!/usr/bin/env python3
"""Run a command and kill it if it stops producing output.

This is useful for PyFluent calls against a remote Fluent session.  A Fluent
gRPC port can remain open even when the session is wedged, causing the local
client to block indefinitely.  This wrapper keeps that failure bounded.
"""

from __future__ import annotations

import argparse
import os
import selectors
import signal
import subprocess
import sys
import time
from pathlib import Path


TIMEOUT_EXIT_CODE = 124


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{seconds:02d}s"
    if minutes:
        return f"{minutes}m{seconds:02d}s"
    return f"{seconds}s"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a command with idle and wall-clock timeouts.")
    parser.add_argument(
        "--idle-timeout-seconds",
        type=float,
        default=300.0,
        help="Kill the command if it emits no output for this long. Use 0 to disable.",
    )
    parser.add_argument(
        "--wall-timeout-seconds",
        type=float,
        default=0.0,
        help="Kill the command after this total runtime. Use 0 to disable.",
    )
    parser.add_argument(
        "--log-file",
        default="",
        help="Optional local file to tee combined stdout/stderr into.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Write child output only to the log file instead of mirroring it to stdout.",
    )
    parser.add_argument(
        "--heartbeat-seconds",
        type=float,
        default=300.0,
        help="In quiet mode, print a compact heartbeat at this interval. Use 0 to disable.",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --.")
    return parser


def kill_process_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return


def main() -> int:
    args = build_parser().parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("No command supplied. Use: run_guarded.py [options] -- command ...", file=sys.stderr)
        return 2

    log_handle = None
    log_path = None
    if args.log_file:
        log_path = Path(args.log_file).expanduser().resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_handle = log_path.open("a", encoding="utf-8")
        print(f"guarded_log: {log_path}", flush=True)
    elif args.quiet:
        print("run_guarded: --quiet was requested without --log-file; child output will be hidden.", flush=True)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True,
    )
    assert process.stdout is not None

    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)

    started = time.monotonic()
    last_output = started
    last_heartbeat = started
    timed_out_reason = ""

    def emit_heartbeat(now: float, *, force: bool = False) -> None:
        nonlocal last_heartbeat
        if not args.quiet or args.heartbeat_seconds <= 0:
            return
        if not force and now - last_heartbeat < args.heartbeat_seconds:
            return
        log_label = str(log_path) if log_path else "<none>"
        print(
            "run_guarded: running "
            f"elapsed={format_duration(now - started)} "
            f"idle={format_duration(now - last_output)} "
            f"log={log_label}",
            flush=True,
        )
        last_heartbeat = now

    print(
        "run_guarded: started "
        f"pid={process.pid} mode={'quiet' if args.quiet else 'stream'}",
        flush=True,
    )
    try:
        while True:
            if process.poll() is not None:
                remaining = process.stdout.read()
                if remaining:
                    if log_handle:
                        log_handle.write(remaining)
                        log_handle.flush()
                    if not args.quiet:
                        print(remaining, end="", flush=True)
                return_code = process.returncode or 0
                if args.quiet:
                    print(
                        "run_guarded: exited "
                        f"code={return_code} "
                        f"elapsed={format_duration(time.monotonic() - started)}",
                        flush=True,
                    )
                return return_code

            now = time.monotonic()
            if args.wall_timeout_seconds > 0 and now - started > args.wall_timeout_seconds:
                timed_out_reason = f"wall timeout {args.wall_timeout_seconds:.1f}s exceeded"
                break
            if args.idle_timeout_seconds > 0 and now - last_output > args.idle_timeout_seconds:
                timed_out_reason = f"idle timeout {args.idle_timeout_seconds:.1f}s exceeded"
                break
            emit_heartbeat(now)

            for key, _event in selector.select(timeout=1.0):
                chunk = key.fileobj.readline()
                if not chunk:
                    continue
                last_output = time.monotonic()
                if log_handle:
                    log_handle.write(chunk)
                    log_handle.flush()
                if not args.quiet:
                    print(chunk, end="", flush=True)
    except KeyboardInterrupt:
        print("\nrun_guarded: interrupted; terminating child process", file=sys.stderr, flush=True)
        kill_process_group(process)
        return 130
    finally:
        selector.close()
        if log_handle:
            log_handle.close()

    print(f"\nrun_guarded: TIMEOUT -> {timed_out_reason}", file=sys.stderr, flush=True)
    kill_process_group(process)
    return TIMEOUT_EXIT_CODE


if __name__ == "__main__":
    raise SystemExit(main())
