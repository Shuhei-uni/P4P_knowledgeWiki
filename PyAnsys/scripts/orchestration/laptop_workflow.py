#!/usr/bin/env python3
"""Operate the laptop-owned Markdown-to-results workflow state."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.laptop_workflow import (  # noqa: E402
    LaptopWorkflow,
    LaptopWorkflowError,
)
from pyansys_fluent.run_worker import RunRequest  # noqa: E402


def _workflow(args: argparse.Namespace) -> LaptopWorkflow:
    return LaptopWorkflow(args.workspace)


def _print_json(value) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Track agent-proved setup progress, explicit run handoffs, "
            "recovery verification, analysis artifacts, and final results. "
            "This command never interprets setup Markdown or builds a case."
        )
    )
    parser.add_argument(
        "--workspace",
        required=True,
        help="Untracked laptop workflow directory.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    initialize = commands.add_parser("init")
    initialize.add_argument("--job-id", required=True)
    initialize.add_argument("--setup-plan", required=True)
    initialize.add_argument("--generation", type=int)
    initialize.add_argument(
        "--analysis-task", action="append", default=[]
    )

    commands.add_parser("status")

    generation = commands.add_parser("connection-generation")
    generation.add_argument("generation", type=int)

    step_start = commands.add_parser("step-start")
    step_start.add_argument("step")
    step_start.add_argument("--safe-to-retry", action="store_true")

    step_complete = commands.add_parser("step-complete")
    step_complete.add_argument("step")

    accept_case = commands.add_parser("accept-case")
    accept_case.add_argument("case_path")

    commands.add_parser("case-ready")

    connection_lost = commands.add_parser("setup-connection-lost")
    connection_lost.add_argument("--generation", required=True, type=int)

    setup_recovered = commands.add_parser("setup-recovered")
    setup_recovered.add_argument("--generation", required=True, type=int)

    submit = commands.add_parser("submit")
    submit.add_argument("request_json")
    submit.add_argument(
        "--bridge-dir",
        default=os.getenv("FLUENT_BRIDGE_DIR", ""),
    )
    submit.add_argument(
        "--max-connection-age-seconds",
        type=float,
        default=float(
            os.getenv("FLUENT_CONNECTION_MAX_AGE_SECONDS", "45")
        ),
    )

    receipt = commands.add_parser("ingest-receipt")
    receipt.add_argument("receipt_json")

    verify = commands.add_parser("verify-checkpoint")
    verify.add_argument("--case-path", required=True)
    verify.add_argument("--data-path", required=True)
    verify.add_argument("--generation", required=True, type=int)

    human_review = commands.add_parser("human-review")
    human_review.add_argument("--generation", required=True, type=int)
    human_review.add_argument("--reason", required=True)

    add_tasks = commands.add_parser("analysis-add")
    add_tasks.add_argument("task", nargs="+")

    analysis_start = commands.add_parser("analysis-start")
    analysis_start.add_argument("task")

    analysis_complete = commands.add_parser("analysis-complete")
    analysis_complete.add_argument("task")
    analysis_complete.add_argument(
        "--artifact", action="append", required=True
    )
    analysis_complete.add_argument("--notes")

    analysis_mark = commands.add_parser("analysis-mark")
    analysis_mark.add_argument("task")
    analysis_mark.add_argument(
        "--status", required=True, choices=("interrupted", "failed")
    )
    analysis_mark.add_argument("--notes", required=True)

    commands.add_parser("finalize")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    workflow = _workflow(args)
    try:
        if args.command == "init":
            result = workflow.create(
                job_id=args.job_id,
                setup_plan_path=args.setup_plan,
                connection_generation=args.generation,
                analysis_tasks=args.analysis_task,
            )
        elif args.command == "status":
            result = {
                "workflow": workflow.read(),
                "ledger": workflow.ledger.read(),
                "analysis": workflow.read_analysis(),
            }
        elif args.command == "connection-generation":
            result = workflow.observe_connection_generation(args.generation)
        elif args.command == "step-start":
            result = workflow.start_step(
                args.step, safe_to_retry=args.safe_to_retry
            )
        elif args.command == "step-complete":
            result = workflow.complete_step(args.step)
        elif args.command == "accept-case":
            result = workflow.accept_case_checkpoint(args.case_path)
        elif args.command == "case-ready":
            result = workflow.mark_case_ready()
        elif args.command == "setup-connection-lost":
            result = workflow.record_setup_connection_loss(
                generation=args.generation
            )
        elif args.command == "setup-recovered":
            result = workflow.verify_setup_recovery(
                generation=args.generation
            )
        elif args.command == "submit":
            if not args.bridge_dir:
                raise ValueError(
                    "An absolute --bridge-dir or FLUENT_BRIDGE_DIR is required"
                )
            request = RunRequest.from_path(
                Path(args.request_json).expanduser()
            )
            destination = workflow.submit(
                request,
                bridge_dir=Path(args.bridge_dir),
                max_connection_age_seconds=args.max_connection_age_seconds,
            )
            result = {"submitted_request": str(destination)}
        elif args.command == "ingest-receipt":
            result = workflow.ingest_receipt(args.receipt_json)
        elif args.command == "verify-checkpoint":
            result = workflow.verify_pending_checkpoint(
                case_path=args.case_path,
                data_path=args.data_path,
                generation=args.generation,
            )
        elif args.command == "human-review":
            result = workflow.require_human_review(
                generation=args.generation,
                reason=args.reason,
            )
        elif args.command == "analysis-add":
            result = workflow.add_analysis_tasks(args.task)
        elif args.command == "analysis-start":
            result = workflow.start_analysis_task(args.task)
        elif args.command == "analysis-complete":
            result = workflow.complete_analysis_task(
                args.task,
                artifacts=args.artifact,
                notes=args.notes,
            )
        elif args.command == "analysis-mark":
            result = workflow.mark_analysis_task(
                args.task,
                status=args.status,
                notes=args.notes,
            )
        else:
            manifest, summary = workflow.finalize()
            result = {
                "result_manifest": str(manifest),
                "result_summary": str(summary),
            }
    except (
        FileNotFoundError,
        FileExistsError,
        KeyError,
        ValueError,
        LaptopWorkflowError,
    ) as exc:
        print(f"Workflow command failed: {exc}", file=sys.stderr)
        return 1
    _print_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
