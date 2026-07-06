#!/usr/bin/env python3
"""Probe Student-edition Fluent by starting a manual server and setting safe values.

This bypasses PyFluent's local launcher wrapper so we can distinguish:
- Fluent launch failure,
- gRPC connection failure,
- and settings-path/value-setting failure.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

import ansys.fluent.core as pyfluent


DEFAULT_FLUENT_EXE = (
    r"C:\Program Files\ANSYS Inc\ANSYS Student\v261\fluent\ntbin\win64\fluent.exe"
)
DEFAULT_MESH = (
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\purnanto-extended.msh"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Start Student Fluent manually and probe live value-setting."
    )
    parser.add_argument(
        "--fluent-exe",
        default=DEFAULT_FLUENT_EXE,
        help="Path to fluent.exe.",
    )
    parser.add_argument(
        "--mesh",
        default=DEFAULT_MESH,
        help="Mesh path to load after connecting.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path("output") / "student_manual_probe"),
        help="Directory for server-info and launch logs.",
    )
    parser.add_argument(
        "--processor-count",
        type=int,
        default=2,
        help="Processor count to request from Fluent. Default: 2.",
    )
    parser.add_argument(
        "--start-timeout",
        type=int,
        default=120,
        help="Seconds to wait for the server-info file. Default: 120.",
    )
    return parser


def print_kv(key: str, value) -> None:
    print(f"{key}: {value}")


def start_fluent(
    fluent_exe: Path,
    output_dir: Path,
    processor_count: int,
) -> tuple[subprocess.Popen[str], Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    server_info = output_dir / "server_info_student_probe.txt"
    stdout_log = output_dir / "fluent_stdout.log"
    stderr_log = output_dir / "fluent_stderr.log"

    if server_info.exists():
        server_info.unlink()

    args = [
        str(fluent_exe),
        "3ddp",
        f"-t{processor_count}",
        "-g",
        f"-sifile={server_info}",
    ]
    print_kv("launch_command", args)
    process = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=stdout_log.open("w", encoding="utf-8", errors="replace"),
        stderr=stderr_log.open("w", encoding="utf-8", errors="replace"),
        cwd=str(output_dir),
        text=True,
    )
    print_kv("launch_pid", process.pid)
    return process, server_info, stdout_log, stderr_log


def wait_for_server_info(process: subprocess.Popen[str], server_info: Path, timeout: int) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if server_info.exists() and server_info.stat().st_size > 0:
            print_kv("server_info_ready", server_info)
            print(server_info.read_text(encoding="utf-8", errors="replace"))
            return
        if process.poll() is not None:
            raise RuntimeError(f"Fluent exited early with code {process.returncode}")
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for server-info file: {server_info}")


def probe_value_setting(solver, mesh_path: Path) -> None:
    print_kv("fluent_version", solver.get_fluent_version())
    print_kv("health", solver.health_check.check_health())

    solver.settings.file.read_mesh(file_name=str(mesh_path))
    print_kv("mesh_load", "OK")

    op = solver.settings.setup.general.operating_conditions
    op.operating_pressure = 0
    print_kv("operating_pressure_readback", getattr(op, "operating_pressure", "<unavailable>"))

    op.gravity.enable = True
    op.gravity.components = [0.0, -9.81, 0.0]
    print_kv("gravity_enable_readback", getattr(op.gravity, "enable", "<unavailable>"))
    print_kv("gravity_components_readback", getattr(op.gravity, "components", "<unavailable>"))

    solver.tui.define.models.viscous.rng_ke("yes")
    print_kv("viscous_model", "rng_ke via TUI OK")

    solver.scheme.exec(('(ti-menu-load-string "/define/models/dpm yes")',))
    print_kv("dpm_enable", "TUI OK")

    configuration = solver.tui.file.show_configuration()
    print("configuration_after_changes:")
    print(configuration)


def read_log_excerpt(path: Path, tail_lines: int = 40) -> str:
    if not path.exists():
        return "<missing>"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    excerpt = lines[-tail_lines:]
    return "\n".join(excerpt) if excerpt else "<empty>"


def main() -> int:
    args = build_parser().parse_args()
    fluent_exe = Path(args.fluent_exe)
    mesh_path = Path(args.mesh)
    output_dir = Path(args.output_dir).resolve()

    if not fluent_exe.exists():
        print_kv("fluent_exe_missing", fluent_exe)
        return 2
    if not mesh_path.exists():
        print_kv("mesh_missing", mesh_path)
        return 3

    process = None
    solver = None
    server_info = None
    stdout_log = None
    stderr_log = None

    try:
        process, server_info, stdout_log, stderr_log = start_fluent(
            fluent_exe=fluent_exe,
            output_dir=output_dir,
            processor_count=args.processor_count,
        )
        wait_for_server_info(process, server_info, args.start_timeout)

        solver = pyfluent.connect_to_fluent(
            server_info_file_name=str(server_info),
            cleanup_on_exit=False,
            start_transcript=True,
            allow_remote_host=False,
        )
        print_kv("connect_to_fluent", "OK")

        probe_value_setting(solver, mesh_path)
        print_kv("probe_status", "OK")
        return 0
    except Exception as exc:
        print_kv("probe_failed", f"{type(exc).__name__}: {exc}")
        if process is not None:
            print_kv("process_alive", process.poll() is None)
            print_kv("process_returncode", process.poll())
        if stdout_log is not None:
            print("stdout_log_tail:")
            print(read_log_excerpt(stdout_log))
        if stderr_log is not None:
            print("stderr_log_tail:")
            print(read_log_excerpt(stderr_log))
        return 1
    finally:
        if solver is not None:
            try:
                solver.exit()
                print_kv("solver_exit", "OK")
            except Exception as exc:
                print_kv("solver_exit_failed", exc)
        elif process is not None and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=20)
                print_kv("process_terminate", "OK")
            except Exception as exc:
                print_kv("process_terminate_failed", exc)


if __name__ == "__main__":
    raise SystemExit(main())
