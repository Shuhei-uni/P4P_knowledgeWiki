"""CLI for bounded upstream MCP inspection; no case loading or parent activation."""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from pyansys_fluent.mcp_client import MCPCallError, open_fluent_mcp
from pyansys_fluent.mcp_policy import UPSTREAM_COMMIT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--root-path", default="setup.models", help="Compatibility alias for a single requested path.")
    parser.add_argument("--paths", nargs="+", help="Exact branches to inspect; no recursive P4P tree walk.")
    parser.add_argument("--query", help="Offline find_api query; does not attach to Fluent.")
    parser.add_argument("--status-only", action="store_true", help="Attach and capture MCP session/solver status only; do not request Settings state.")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--timeout", type=float, help="Optional tool timeout. No automatic retries.")
    return parser


async def inspect(args: argparse.Namespace) -> dict:
    if args.query and args.status_only:
        raise ValueError("--query and --status-only cannot be used together")
    paths = [] if args.status_only else args.paths or [args.root_path]
    payload = {"schema": "p4p.mcp-inspection.v1", "observed_at": datetime.now(timezone.utc).isoformat(),
               "upstream_commit": UPSTREAM_COMMIT, "server_alias": args.server_id,
               "identity_status": "UNVERIFIED", "paths": paths, "results": {}, "errors": {}}
    async with open_fluent_mcp(args.server_id, timeout=args.timeout, connect=not args.query) as client:
        calls = [("find_api", {"query": args.query})] if args.query else [
            ("session_status", {}), ("solver_status", {}),
        ]
        if not args.query and not args.status_only:
            calls.extend([("describe_path", {"paths": paths}), ("get_state", {"paths": paths})])
        for name, arguments in calls:
            try:
                payload["results"][name] = await client.call(name, arguments)
            except MCPCallError as exc:
                evidence = exc.payload
                if hasattr(evidence, "model_dump"):
                    evidence = evidence.model_dump(mode="json")
                payload["errors"][name] = {"message": str(exc), "payload": evidence}
    payload["status"] = "BLOCKED" if payload["errors"] else "OBSERVED"
    return payload


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = asyncio.run(inspect(args))
    except Exception as exc:
        print(f"MCP inspection blocked ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 2
    text = json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        # Evidence captures are immutable; choose a new output for each observation.
        with args.output_json.open("x", encoding="utf-8") as stream:
            stream.write(text)
    print(text, end="")
    return 2 if payload["status"] == "BLOCKED" else 0
