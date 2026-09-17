#!/usr/bin/env python3
"""Execute one reviewed/generated snippet over MCP; execution is not qualification.

For hypothesis jobs, invoke under the existing run_and_handoff.py supervisor.
The required-files/verifier contract still owns completion and self-wake.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pyansys_fluent.mcp_client import ExecutionUncertain, MCPCallError, open_fluent_mcp
from pyansys_fluent.mcp_policy import UPSTREAM_COMMIT, check_generated_code


async def execute(args, code: str) -> dict:
    record = {"upstream_commit": UPSTREAM_COMMIT, "server_alias": args.server_id,
              "code_sha256": hashlib.sha256(code.encode()).hexdigest(), "status": "BLOCKED",
              "scientifically_verified": False}
    try:
        check_generated_code(code)
        async with open_fluent_mcp(args.server_id, timeout=args.timeout) as client:
            record["result"] = await client.validate_and_run(code)
        record["status"] = "EXECUTED"
    except ExecutionUncertain as exc:
        record.update(status="EXECUTION_UNCERTAIN", message=str(exc), evidence=exc.payload)
    except Exception as exc:
        record.update(message=f"{type(exc).__name__}: {exc}", evidence=getattr(exc, "payload", None))
    record["observed_at"] = datetime.now(timezone.utc).isoformat()
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--code-file", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True, help="New evidence path from the existing run-paths.yaml; never phase-state.yaml.")
    parser.add_argument("--timeout", type=float, help="Optional MCP timeout; a timeout never proves the solve stopped.")
    args = parser.parse_args()
    code = args.code_file.read_text(encoding="utf-8")
    check_generated_code(code)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the final path before execution. Empty on abrupt termination is
    # deliberately NOT a completion receipt; a verifier must parse status.
    with args.output_json.open("x", encoding="utf-8") as stream:
        record = asyncio.run(execute(args, code))
        text = json.dumps(record, indent=2, default=str) + "\n"
        stream.write(text)
        stream.flush()
    print(text, end="")
    return 0 if record["status"] == "EXECUTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
