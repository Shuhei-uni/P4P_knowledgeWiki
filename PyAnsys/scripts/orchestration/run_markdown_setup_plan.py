#!/usr/bin/env python3
"""Run a pinned, agent-authored Fluent build script on the Fluent PC."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.setup_plan import (  # noqa: E402
    MarkdownSetupPlan,
    capture_parent_identity,
    execute_pinned_build_script,
)


def _write_result(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"result_json: {path}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute one pinned agent-authored Fluent build script locally on the "
            "Fluent PC. Markdown supplies provenance, not Fluent commands."
        )
    )
    parser.add_argument("--plan", required=True, help="Tracked Markdown plan path.")
    parser.add_argument(
        "--result-json",
        required=True,
        help="Tracked compact result path to commit back through Git.",
    )
    parser.add_argument("--server-id", default="1")
    parser.add_argument(
        "--capture-parent-identity",
        action="store_true",
        help="Write the parent case size/SHA-256 only; do not run the build script.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    result_path = Path(args.result_json).expanduser().resolve()
    plan = MarkdownSetupPlan.from_path(plan_path)
    base: dict[str, object] = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "plan_path": str(plan_path),
        "plan_id": plan.plan_id,
        "plan_digest": plan.digest,
    }
    if args.capture_parent_identity:
        base.update(
            {
                "status": "identity_captured",
                "parent_identity": capture_parent_identity(plan.parent_case_path),
            }
        )
        _write_result(result_path, base)
        return 0

    try:
        base.update(
            execute_pinned_build_script(
                plan,
                project_root=PROJECT_ROOT,
                server_id=args.server_id,
            )
        )
    except Exception as exc:
        base.update(
            {
                "status": "failed",
                "error": {"type": type(exc).__name__, "message": str(exc)},
            }
        )
        _write_result(result_path, base)
        return 1
    _write_result(result_path, base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
