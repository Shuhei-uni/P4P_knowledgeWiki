"""Small MCP wire client for P4P inspection and generated-code workers.

No automatic retry, generic Settings proxy, independent run manifest or cache.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import json
from pathlib import Path
import sys
from typing import Any, AsyncIterator

from pyansys_fluent.mcp_policy import FORBIDDEN_TOOLS, check_generated_code


class MCPCallError(RuntimeError):
    """Tool or protocol failure, with the original response retained as evidence."""
    def __init__(self, message: str, payload: Any = None) -> None:
        super().__init__(message)
        self.payload = payload


class ExecutionUncertain(MCPCallError):
    """Fluent may have changed. Persist BLOCKED and reconcile before any retry."""


def decode_result(result: Any) -> Any:
    """Accept standard MCP structured results or a single JSON text block."""
    if getattr(result, "isError", False):
        raise MCPCallError("MCP tool returned an error.", result)
    payload = getattr(result, "structuredContent", None)
    if payload is None:
        text = [part.text for part in getattr(result, "content", []) if getattr(part, "type", None) == "text"]
        if len(text) != 1:
            raise MCPCallError("Expected one structured or JSON-text result; preserve raw response.", result)
        try:
            payload = json.loads(text[0])
        except (TypeError, ValueError) as exc:
            raise MCPCallError("MCP returned non-JSON text.", result) from exc
    if isinstance(payload, dict) and (payload.get("status") == "error" or payload.get("ok") is False or payload.get("valid") is False or payload.get("error")):
        raise MCPCallError("MCP operation failed; inspect the attached payload.", payload)
    return payload


class FluentMCPClient:
    def __init__(self, session: Any, timeout: float | None = None) -> None:
        if timeout is not None and timeout <= 0:
            raise ValueError("timeout must be positive or None")
        self.session = session
        self.timeout = timeout
        self.uncertain = False

    async def call(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        if name in FORBIDDEN_TOOLS:
            raise MCPCallError(f"{name} is excluded by P4P's session policy.")
        if self.uncertain and name in {"connect", "run_code"}:
            raise ExecutionUncertain("Previous execution is unresolved; only inspection is permitted.")
        try:
            async with asyncio.timeout(self.timeout):
                result = await self.session.call_tool(name, arguments=arguments or {})
            return decode_result(result)
        except BaseException as exc:
            if name == "run_code":
                # Even a returned error may follow a partially applied snippet.
                self.uncertain = True
                if isinstance(exc, (KeyboardInterrupt, SystemExit, asyncio.CancelledError)):
                    raise
                raise ExecutionUncertain("Execution failed or its response was lost; do not replay. Reconcile live state and existing run evidence.", getattr(exc, "payload", None)) from exc
            raise

    async def validate_and_run(self, code: str) -> Any:
        check_generated_code(code)
        validation = await self.call("validate_code", {"code": code})
        if not isinstance(validation, dict):
            raise MCPCallError("Unrecognised validation response.", validation)
        # The pinned backend returns status=ok on successful prechecks.
        if validation.get("status") != "ok" and validation.get("valid") is not True:
            raise MCPCallError("Validation did not explicitly pass.", validation)
        return await self.call("run_code", {"code": code})


@asynccontextmanager
async def open_fluent_mcp(server_id: str = "1", *, timeout: float | None = None,
                          connect: bool = True) -> AsyncIterator[FluentMCPClient]:
    """One MCP process per selected endpoint; closing STDIO never exits Fluent.

    No short default timeout: the existing P4P supervisor owns long-run budgets.
    Fleet orchestration must still enforce a single writer per Fluent session,
    including reviewed direct-PyFluent workers on other hosts.
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    script = Path(__file__).resolve().parents[2] / "scripts" / "connection" / "fluent_mcp_server.py"
    params = StdioServerParameters(command=sys.executable, args=[str(script), "--server-id", str(server_id)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            names: set[str] = set()
            cursor = None
            while True:
                page = await session.list_tools(cursor=cursor)
                names.update(tool.name for tool in page.tools)
                cursor = page.nextCursor
                if not cursor:
                    break
            required = {"connect", "get_state", "describe_path", "validate_code", "run_code"}
            if not required <= names or names & FORBIDDEN_TOOLS:
                raise MCPCallError("Unexpected P4P MCP tool surface; inspect pinned dependency and server configuration.")
            client = FluentMCPClient(session, timeout)
            if connect:
                attached = await client.call("connect")
                if not isinstance(attached, dict) or attached.get("status") != "ok":
                    raise MCPCallError("Fluent attachment did not explicitly succeed.", attached)
            yield client
