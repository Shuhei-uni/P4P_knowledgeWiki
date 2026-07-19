#!/usr/bin/env python3
"""Load a Fluent case, initialize it, iterate, and save only a data file via TUI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PureWindowsPath

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists, remote_chdir  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Load a remote .cas.h5, hybrid-initialize it, run X iterations, "
            "and save only name_X.dat.h5 next to the input case."
        )
    )
    parser.add_argument("case_path", help="Remote .cas.h5 file visible to Fluent.")
    parser.add_argument("iterations", type=int, help="Iterations to run after initialization.")
    parser.add_argument(
        "--server-id",
        default="1",
        help="Configured Fluent server id to use. Example: 2 for FLUENT_IP2/PORT2/PASSWORD2.",
    )
    parser.add_argument(
        "--report-interval",
        type=int,
        default=25,
        help="Progress print interval during iteration. Default: 25.",
    )
    return parser


def build_output_data_path(case_path: str, iterations: int) -> str:
    case = PureWindowsPath(case_path)
    name = case.name
    if not name.endswith(".cas.h5"):
        raise ValueError(f"Expected a .cas.h5 file, got: {case_path}")
    stem = name[: -len(".cas.h5")]
    return str(case.with_name(f"{stem}_{iterations}.dat.h5"))


def run_tui_command(solver, command: str, *, label: str) -> None:
    print(f"{label}: {command}", flush=True)
    solver.scheme.eval(f'(ti-menu-load-string "{quote_scheme_string(command)}")')


def load_case_only_tui(solver, case_path: str) -> None:
    print_header("Load Case")
    if not remote_file_exists(solver, case_path):
        raise FileNotFoundError(f"Fluent cannot see case file: {case_path}")
    remote_chdir(solver, str(PureWindowsPath(case_path).parent))
    run_tui_command(solver, f'/file/read-case "{case_path}"', label="read_case_tui")


def initialize_case_tui(solver) -> None:
    print_header("Initialize Target Case")
    run_tui_command(solver, "/solve/initialize/hyb-initialization", label="hybrid_initialize_tui")


def iterate_without_persistence(solver, iterations: int, report_interval: int) -> None:
    print_header("Run Target Case")
    if iterations <= 0:
        print("iterate: SKIPPED")
        return

    chunk = max(1, report_interval)
    completed = 0
    while completed < iterations:
        step = min(chunk, iterations - completed)
        run_tui_command(solver, f"/solve/iterate {step}", label=f"iterate_tui_{completed + step}")
        completed += step
        print(f"progress: {completed}/{iterations}", flush=True)


def write_data_only(solver, data_path: str) -> None:
    print_header("Write Data Only")
    remote_chdir(solver, str(PureWindowsPath(data_path).parent))
    run_tui_command(solver, f'/file/write-data "{data_path}"', label="write_data_tui")
    if not remote_file_exists(solver, data_path):
        raise RuntimeError(f"Fluent reported success but data file is not visible: {data_path}")


def run_case_to_data(*, server_id: str, case_path: str, iterations: int, report_interval: int) -> str:
    if iterations < 0:
        raise ValueError("iterations must be >= 0")

    output_data = build_output_data_path(case_path, iterations)
    solver = connect(server_id=server_id)

    load_case_only_tui(solver, case_path)
    initialize_case_tui(solver)
    iterate_without_persistence(solver, iterations, report_interval)
    write_data_only(solver, output_data)

    print(f"\nOutput data: {output_data}", flush=True)
    return output_data


def main() -> int:
    args = build_parser().parse_args()
    output_data = run_case_to_data(
        server_id=str(args.server_id),
        case_path=args.case_path,
        iterations=args.iterations,
        report_interval=args.report_interval,
    )
    print(f"completed: {output_data}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
