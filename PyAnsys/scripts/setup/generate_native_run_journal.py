#!/usr/bin/env python3
"""Generate a Fluent-native steady-run journal with durable logging."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.native_run_journal import (  # noqa: E402
    SteadyNativeRunJournal,
    render_steady_native_run_journal,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a journal that Fluent executes natively. It starts a native "
            "transcript, prints per-iteration residuals, runs one steady iteration "
            "command, exports retained residual history, and leaves Fluent open."
        )
    )
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument(
        "--transcript-file",
        required=True,
        help=r"Absolute path on the Fluent Windows host, for example C:\FluentRuns\case-01\run.trn.",
    )
    parser.add_argument(
        "--residual-file",
        required=True,
        help=r"Absolute path on the Fluent Windows host for the final residual-history export.",
    )
    parser.add_argument(
        "--residual-history-size",
        type=int,
        default=None,
        help=(
            "Optional number of residual points Fluent retains in data/history. "
            "Omit to preserve the loaded case setting."
        ),
    )
    parser.add_argument(
        "--no-residual-plot",
        action="store_true",
        help="Disable the live residual graphics plot; residual printing and files remain enabled.",
    )
    parser.add_argument(
        "--output-journal",
        type=Path,
        required=True,
        help="Local path for the generated .jou file; copy it to the Fluent host before execution.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = SteadyNativeRunJournal(
        iterations=args.iterations,
        transcript_file=args.transcript_file,
        residual_file=args.residual_file,
        residual_history_size=args.residual_history_size,
        plot_residuals=not args.no_residual_plot,
    )
    payload = render_steady_native_run_journal(config)
    output = args.output_journal.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8", newline="\n")
    print(f"journal: {output}")
    print(f"iterations: {config.iterations}")
    print(f"native_transcript: {config.transcript_file}")
    print(f"post_run_residual_export: {config.residual_file}")
    print("run_policy: Fluent-native; this generator does not connect, initialize, iterate, or close Fluent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
