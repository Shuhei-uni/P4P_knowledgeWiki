#!/usr/bin/env python3
"""Show the current shared Fluent endpoint without exposing its password."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.bridge import read_latest_connection  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bridge-dir",
        default=os.getenv("FLUENT_BRIDGE_DIR", ""),
        help="Private shared bridge directory (defaults to FLUENT_BRIDGE_DIR).",
    )
    parser.add_argument("--max-age-seconds", type=float, default=30.0)
    parser.add_argument("--minimum-generation", type=int)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.bridge_dir:
        raise SystemExit("--bridge-dir or FLUENT_BRIDGE_DIR is required")
    document = read_latest_connection(
        Path(args.bridge_dir).expanduser(),
        max_age_seconds=args.max_age_seconds,
        min_generation=args.minimum_generation,
    )
    safe_fields = (
        "schema_version",
        "generation",
        "previous_generation",
        "status",
        "host",
        "port",
        "fluent_pid",
        "fluent_version",
        "started_at",
        "updated_at",
        "heartbeat_sequence",
        "restart_reason",
    )
    safe = {key: document.get(key) for key in safe_fields}
    print(json.dumps(safe, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
