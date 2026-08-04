#!/usr/bin/env python3
"""Save the currently loaded remote Fluent case/data pair.

This script does not iterate, update DPM, or change setup. It only writes the
in-memory case and data to explicit remote paths.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Save the current remote Fluent case/data.")
    parser.add_argument("--server-id", default="1", help="Configured Fluent server id. Default: 1.")
    parser.add_argument("--case-file", required=True, help="Remote Windows .cas.h5 output path.")
    parser.add_argument("--data-file", required=True, help="Remote Windows .dat.h5 output path.")
    parser.add_argument(
        "--label",
        default="manual_recovery",
        help="Short label printed next to write_case/write_data actions.",
    )
    parser.add_argument(
        "--verified-completed-iterations",
        type=int,
        default=None,
        help=(
            "Only set when a controller log or equivalent source proves the solve completed "
            "this many iterations. Do not use Fluent's run setting for this."
        ),
    )
    parser.add_argument(
        "--expected-completed-iterations",
        type=int,
        default=None,
        help="Expected completed iterations for this recovered save, for manifest/status only.",
    )
    parser.add_argument(
        "--local-manifest",
        default="",
        help="Optional local JSON manifest describing the recovery save.",
    )
    parser.add_argument(
        "--remote-manifest",
        default="",
        help="Optional remote Windows JSON manifest path to write next to the saved case/data.",
    )
    parser.add_argument(
        "--allow-unverified-complete-label",
        action="store_true",
        help=(
            "Allow filenames/labels that imply completion, such as 1500, without a verified "
            "completed-iteration count. This is intentionally unsafe and should be rare."
        ),
    )
    return parser


def implies_completed_iteration_label(*values: str) -> bool:
    tokens = ("1500", "_final", "-final", "final", "complete", "completed")
    haystack = " ".join(value.lower() for value in values if value)
    return any(token in haystack for token in tokens)


def validate_recovery_label(args: argparse.Namespace) -> None:
    expected = args.expected_completed_iterations
    verified = args.verified_completed_iterations
    if expected is not None and verified is not None and verified != expected:
        raise ValueError(
            f"verified completed iterations ({verified}) does not match expected ({expected})"
        )
    if args.allow_unverified_complete_label:
        return
    if not implies_completed_iteration_label(args.case_file, args.data_file, args.label):
        return
    if expected is not None and verified == expected:
        return
    raise ValueError(
        "Refusing to save a recovery file with a completed-looking label/path without "
        "--verified-completed-iterations matching --expected-completed-iterations. "
        "Use an unverified/recovered label instead, or pass the verified count when a "
        "controller log proves completion."
    )


def main() -> int:
    load_dotenv()
    args = build_parser().parse_args()
    validate_recovery_label(args)

    solver = connect(server_id=args.server_id)
    print(f"connected: {solver.get_fluent_version()}")
    reported_iterations = sweep.read_iteration_count(solver)
    print(f"reported_number_of_iterations: {reported_iterations}")
    print(
        "reported_number_of_iterations_note: this is Fluent's current iteration/run setting; "
        "it is not proof that a disconnected controller completed that many iterations"
    )

    print_header("Save Current Case/Data")
    sweep.write_case_data_pair(solver, args.case_file, args.data_file, args.label)

    case_exists = sweep.remote_file_exists(solver, args.case_file)
    data_exists = sweep.remote_file_exists(solver, args.data_file)
    print(f"case_exists: {case_exists}")
    print(f"data_exists: {data_exists}")
    if not case_exists or not data_exists:
        return 1

    manifest = {
        "case_file": args.case_file,
        "data_file": args.data_file,
        "label": args.label,
        "reported_number_of_iterations": reported_iterations,
        "reported_number_of_iterations_is_completion_proof": False,
        "verified_completed_iterations": args.verified_completed_iterations,
        "expected_completed_iterations": args.expected_completed_iterations,
        "status": (
            "verified"
            if args.verified_completed_iterations is not None
            and (
                args.expected_completed_iterations is None
                or args.verified_completed_iterations == args.expected_completed_iterations
            )
            else "unverified"
        ),
        "notes": [
            "Manual recovery save. Treat as complete only if verified_completed_iterations is set.",
            "Do not infer completed iterations from reported_number_of_iterations.",
        ],
    }
    manifest_text = json.dumps(manifest, indent=2, default=str)
    if args.local_manifest:
        local_manifest = Path(args.local_manifest).expanduser().resolve()
        local_manifest.parent.mkdir(parents=True, exist_ok=True)
        local_manifest.write_text(manifest_text, encoding="utf-8")
        print(f"local_manifest: {local_manifest}")
    if args.remote_manifest:
        sweep.remote_text_write_best_effort(solver, args.remote_manifest, manifest_text)
        print(f"remote_manifest: {args.remote_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
