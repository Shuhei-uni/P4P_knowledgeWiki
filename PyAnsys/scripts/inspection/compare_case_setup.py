#!/usr/bin/env python3
"""Compare MCP snapshots offline. This command never connects to or reloads Fluent."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pyansys_fluent.setup_snapshot_diff import compare_snapshots, diff_values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-snapshot", type=Path, required=True)
    parser.add_argument("--candidate-snapshot", type=Path, required=True)
    parser.add_argument("--allow-change", action="append", default=[], help="Declared changed path/glob; repeat for each approved delta.")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    try:
        base = json.loads(args.base_snapshot.read_text(encoding="utf-8"))
        candidate = json.loads(args.candidate_snapshot.read_text(encoding="utf-8"))
        payload = compare_snapshots(base, candidate, args.allow_change)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    payload.update(base_snapshot=str(args.base_snapshot), candidate_snapshot=str(args.candidate_snapshot))
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        with args.output_json.open("x", encoding="utf-8") as stream:
            stream.write(text)
    print(text, end="")
    return 2 if payload["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
