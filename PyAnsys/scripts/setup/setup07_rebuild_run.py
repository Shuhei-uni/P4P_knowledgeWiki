#!/usr/bin/env python3
"""Rebuild intended setup 07 on a new mesh, with live-archive fallback."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - local convenience fallback
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.run_persistence import RunPersistence  # noqa: E402
from pyansys_fluent.setup_recipes import (  # noqa: E402
    CarrierRunConfig,
    CheckpointConfig,
    require_setup07_paths,
    run_setup07_carrier_recipe,
)
from pyansys_fluent.setup_run import RunInterrupted  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Apply intended setup 07 to a target mesh, fall back to archived "
            "actual settings when necessary, then initialize and run."
        )
    )
    parser.add_argument(
        "--server-id",
        default="1",
        help="Configured local Fluent server id. Use 1 for FLUENT_SERVER_INFO_FILE, 2 for FLUENT_SERVER_INFO_FILE2, and so on.",
    )
    parser.add_argument("--target-mesh", default="", help="Remote target mesh file.")
    parser.add_argument("--output-case", required=True, help="Remote final case file.")
    parser.add_argument("--output-data", required=True, help="Remote final data file.")
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Iterations after initialization. Default: 100.",
    )
    parser.add_argument(
        "--report-interval",
        type=int,
        default=100,
        help="Console progress interval. Default: 100.",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=1000,
        help="Overwrite a rolling autosave case/data checkpoint every N iterations. Default: 1000.",
    )
    parser.add_argument(
        "--initialized-case",
        default="",
        help="Optional remote case file to write immediately after initialization.",
    )
    parser.add_argument(
        "--initialized-data",
        default="",
        help="Optional remote data file to write immediately after initialization.",
    )
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Apply setup and initialize, but do not iterate.",
    )
    parser.add_argument(
        "--resume-case",
        default="",
        help="Optional remote case file to resume from instead of rebuilding from mesh.",
    )
    parser.add_argument(
        "--resume-data",
        default="",
        help="Optional remote data file to resume from instead of rebuilding from mesh.",
    )
    parser.add_argument(
        "--resume-state-json",
        default="",
        help="Optional run-state JSON to resume from when no explicit resume case/data pair is provided.",
    )
    parser.add_argument(
        "--resume-latest",
        action="store_true",
        help="Resume from the latest autosave or numbered checkpoint matching the output paths.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    run_config = CarrierRunConfig(
        target_mesh=args.target_mesh,
        resume_case=args.resume_case,
        resume_data=args.resume_data,
        resume_state_json=args.resume_state_json,
        resume_latest=args.resume_latest,
    )
    checkpoint_config = CheckpointConfig(
        output_case=args.output_case,
        output_data=args.output_data,
        initialized_case=args.initialized_case,
        initialized_data=args.initialized_data,
        checkpoint_interval=args.checkpoint_interval,
        report_interval=args.report_interval,
    )
    require_setup07_paths(run_config)

    try:
        solver = connect(server_id=args.server_id)
        print(f"\nConnected to Fluent {solver.get_fluent_version()}")
        run_setup07_carrier_recipe(
            solver,
            run_config,
            checkpoint_config,
            iterations=args.iterations,
            skip_run=args.skip_run,
        )
    except RunInterrupted as exc:
        print_header("Interrupt Save")
        print(
            "Keyboard interrupt received. Saving current solver state so it can be resumed "
            f"from {args.output_case} and {args.output_data}."
        )
        persistence = RunPersistence(
            output_case=args.output_case,
            output_data=args.output_data,
            checkpoint_interval=args.checkpoint_interval,
            report_interval=args.report_interval,
        )
        persistence.record_interrupt(
            solver,
            completed_iterations=exc.completed_iterations,
            allow_case_only=False,
        )
        print(f"\nPaused run saved after approximately {exc.completed_iterations} completed iterations.")
        return 130

    print("\nSetup 07 rebuild finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
