#!/usr/bin/env python3
"""Run a background hypothesis job and wake its originating Codex thread."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
PYANSYS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PYANSYS_ROOT / "src"))

from pyansys_fluent.run_handoff import (  # noqa: E402
    launch_detached_worker,
    load_spec,
    run_job,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Launch a long-running hypothesis-test runner independently of the current agent. "
            "The worker writes COMPLETE/BLOCKED terminal evidence and then wakes the exact "
            "originating Codex thread. Discovery runs should stay agent-attached instead."
        )
    )
    parser.add_argument("--job", required=True, help="YAML run-and-handoff job specification")
    parser.add_argument(
        "--worker",
        action="store_true",
        help="Internal foreground worker mode. Omit this for normal detached launch.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacing an existing terminal manifest. Use only after reconciling prior work.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    spec_path = Path(args.job).expanduser().resolve()
    spec = load_spec(spec_path, repo_root=REPO_ROOT)

    if not args.worker:
        if spec.manifest_path.exists() and not args.force:
            print(f"Refusing duplicate launch: {spec.manifest_path} already exists", file=sys.stderr)
            return 2
        pid = launch_detached_worker(
            Path(__file__).resolve(), spec_path, spec.worker_log_path, force=args.force
        )
        print(f"Detached run worker started: job={spec.job_id} mode={spec.mode} pid={pid}")
        print(f"Originating Codex thread: {spec.codex.session_id}")
        print(f"Manifest: {spec.manifest_path}")
        print(f"Worker log: {spec.worker_log_path}")
        return 0

    try:
        manifest = run_job(spec, allow_existing_terminal=args.force)
    except Exception as exc:
        print(f"Run worker failed before terminal handoff: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    handoff = manifest.get("handoff", {})
    print(f"Job terminal status: {manifest['status']}")
    print(f"Manifest: {spec.manifest_path}")
    print(f"Codex handoff: {handoff.get('status')}")
    return 0 if manifest["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
