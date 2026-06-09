#!/usr/bin/env python3
"""Small local PyFluent smoke test for solver launch and basic setup actions.

This script is intentionally conservative:
- it launches a local Fluent solver session from the installed Ansys copy,
- optionally attempts to load a user-supplied mesh/case file,
- applies a few low-risk setup changes,
- prints what worked and what failed,
- exits without saving over any existing files.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path
import sys
import traceback

import ansys.fluent.core as pyfluent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Launch local Fluent and perform a few basic setup smoke tests."
    )
    parser.add_argument(
        "--input-file",
        default="",
        help="Optional local Fluent mesh/case file to try loading.",
    )
    parser.add_argument(
        "--read-mode",
        choices=("auto", "mesh", "case"),
        default="auto",
        help="How to load --input-file. Default: auto.",
    )
    parser.add_argument(
        "--processor-count",
        type=int,
        default=2,
        help="Processor count to request when launching Fluent. Default: 2.",
    )
    parser.add_argument(
        "--dimension",
        type=int,
        choices=(2, 3),
        default=3,
        help="Fluent solver dimension. Default: 3.",
    )
    return parser


def detect_read_mode(path: Path) -> str:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    name = path.name.lower()
    if name.endswith(".cas") or name.endswith(".cas.h5"):
        return "case"
    if (
        name.endswith(".msh")
        or name.endswith(".msh.h5")
        or name.endswith(".mesh")
        or name.endswith(".mesh.h5")
        or name.endswith(".meshdat")
    ):
        return "mesh"
    return "case"


def print_boundary_summary(solver) -> None:
    try:
        boundary_state = solver.settings.setup.boundary_conditions.get_state()
    except Exception as exc:
        print(f"BOUNDARY_SUMMARY_UNAVAILABLE: {exc}")
        return

    if not isinstance(boundary_state, Mapping):
        print("BOUNDARY_SUMMARY_UNAVAILABLE: unexpected state shape")
        return

    print("BOUNDARY_SUMMARY:")
    for boundary_type, zones in sorted(boundary_state.items()):
        if not isinstance(zones, Mapping):
            continue
        names = [str(name) for name in zones.keys() if str(name) != "settings"]
        if names:
            print(f"  {boundary_type}: {', '.join(sorted(names))}")


def try_load_input_file(solver, input_path: Path, read_mode: str) -> None:
    chosen_mode = detect_read_mode(input_path) if read_mode == "auto" else read_mode
    print(f"INPUT_FILE: {input_path}")
    print(f"READ_MODE: {chosen_mode}")

    if chosen_mode == "mesh":
        solver.settings.file.read_mesh(file_name=str(input_path))
    else:
        solver.settings.file.read_case(file_name=str(input_path))

    print("FILE_LOAD_OK")


def apply_smoke_test_actions(solver) -> None:
    # Gravity can be toggled even before setup panels become active.
    solver.scheme.eval("(rpsetvar 'gravity? #t)")
    gravity_enabled = solver.scheme.eval("(rpgetvar 'gravity?)")
    print(f"GRAVITY_ENABLED: {gravity_enabled}")

    # This TUI path worked reliably in this environment during testing.
    solver.tui.define.models.viscous.kw_sst("yes")
    print("VISCOUS_MODEL_SET: k-omega SST")

    print("CONFIGURATION_AFTER_CHANGES:")
    print(solver.tui.file.show_configuration())


def main() -> int:
    args = build_parser().parse_args()
    solver = None
    input_path = Path(args.input_file).expanduser().resolve() if args.input_file else None

    if input_path and not input_path.exists():
        print(f"INPUT_FILE_MISSING: {input_path}")
        return 2

    try:
        solver = pyfluent.Solver.from_install(
            precision="double",
            processor_count=args.processor_count,
            dimension=args.dimension,
        )
        print(f"LAUNCH_OK: {solver.get_fluent_version()}")
        print(f"HEALTH: {solver.health_check.check_health()}")

        if input_path is not None:
            try:
                try_load_input_file(solver, input_path, args.read_mode)
                print_boundary_summary(solver)
            except Exception as exc:
                print(f"FILE_LOAD_FAILED: {type(exc).__name__}: {exc}")
                traceback.print_exc()
                return 3

        apply_smoke_test_actions(solver)
        print("SMOKE_TEST_OK")
        return 0
    except Exception as exc:
        print(f"SMOKE_TEST_FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return 1
    finally:
        if solver is not None:
            try:
                solver.exit()
                print("EXIT_OK")
            except Exception as exc:
                print(f"EXIT_FAILED: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
