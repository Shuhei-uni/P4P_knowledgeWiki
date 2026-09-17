"""Upstream Fluent MCP with P4P's attach-only session policy.

No copied discovery engine, solver proxy, retries, research state, or recipes.
Private upstream extension points are isolated here and covered by contract tests.
"""
from __future__ import annotations

import asyncio
import contextlib
import sys
from typing import Any

from ansys.fluent.mcp.common.base import FluidsLeafMCP
from ansys.fluent.mcp.common.models import ConnectResult, RunCodeResult
from ansys.fluent.mcp.solve.backends.pyfluent import PyFluentBackend
from ansys.fluent.mcp.solve.lib.domain_tools import get_solve_domain_tools

from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.mcp_policy import CORE_TOOLS, DOMAIN_TOOLS, SessionPolicyError, check_generated_code


class PreservingBackend(PyFluentBackend):
    """Change lifecycle authority only; inherit discovery, validation and execution."""

    def __init__(self, server_id: str = "1") -> None:
        super().__init__(label=f"P4P Fluent endpoint {server_id}")
        self.server_id = server_id
        self._attached_once = False

    async def connect(self, **kwargs: Any) -> ConnectResult:
        # Bind each MCP process to one configured fleet alias. Agent arguments
        # cannot switch endpoints, load a case, enable cleanup, or launch Fluent.
        if kwargs:
            return ConnectResult(status="error", error_code="p4p_attach_only", message="Call connect without connect_kwargs; the server launcher selects the endpoint.")
        async with self._lock:
            if self._attached_once:
                return ConnectResult(status="error", error_code="p4p_reconcile_required", message="Already attached once. Reconcile live state before starting another MCP client.")
            try:
                options = resolve_connection_kwargs(self.server_id)
                from ansys.fluent.core import connect_to_fluent
                def attach():
                    # PyFluent startup output must not corrupt MCP's STDIO stream.
                    with contextlib.redirect_stdout(sys.stderr):
                        return connect_to_fluent(**options)
                task = asyncio.create_task(asyncio.to_thread(attach))
                try:
                    self._solver = await asyncio.shield(task)
                except asyncio.CancelledError:
                    self._solver = await task
                    self._attached_once = True
                    raise
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                return ConnectResult(status="error", error_code="p4p_attach_failed", message=f"Attach failed ({type(exc).__name__}); check endpoint configuration. No solver was launched.")
            self._attached_once = True
            self._mode = "attach"
            self.endpoint = f"configured:{self.server_id}"
            self.invalidate_live_caches()
            self.invalidate_mesh_cache()
            return ConnectResult(status="ok", backend_kind=self.kind, endpoint=self.endpoint, message="Attached; Fluent is preserved on MCP shutdown. Endpoint is not case identity.")

    async def disconnect(self) -> None:
        raise SessionPolicyError("P4P preserves Fluent. Close the MCP transport, not the solver.")

    def close_sync(self) -> None:
        # Upstream cleanup calls solver.exit(), even for attached sessions.
        # Retain the handle until process teardown; cleanup_on_exit=False was
        # supplied at construction, so PyFluent must not terminate Fluent.
        return None

    async def run_code(self, code: str, **kwargs: Any) -> RunCodeResult:
        try:
            check_generated_code(code)
        except (SessionPolicyError, SyntaxError) as exc:
            return RunCodeResult(status="error", error_code="p4p_policy_block", message=str(exc))
        return await super().run_code(code, **kwargs)

    async def validate_code(self, code: str, **kwargs: Any) -> RunCodeResult:
        try:
            check_generated_code(code)
        except (SessionPolicyError, SyntaxError) as exc:
            return RunCodeResult(status="error", error_code="p4p_policy_block", message=str(exc))
        return await super().validate_code(code, **kwargs)


class P4PFluentMCP(FluidsLeafMCP):
    leaf_name = "solve"
    default_backend_kind = "pyfluent"
    component_label = "fluent"

    # Override only the misleading launch/exit guidance in upstream resources.
    _TOOLSET_CATALOGUE = {
        **FluidsLeafMCP._TOOLSET_CATALOGUE,
        "connection": {
            "description": "Attach to the existing P4P fleet endpoint.",
            "skill": "Call connect without arguments once. Inspect loaded artifact identity separately. MCP shutdown preserves Fluent; lifecycle operations are unavailable.",
            "tools": ["session_status", "connect"],
        },
    }

    def __init__(self, server_id: str = "1", **kwargs: Any) -> None:
        super().__init__(backends={"pyfluent": PreservingBackend(server_id)}, expose_tools=CORE_TOOLS,
                         name=f"p4p-fluent-{server_id}", **kwargs)

    def _register_tools(self) -> None:
        super()._register_tools()
        # Upstream domain tools bypass expose_tools. Filter explicitly: notably
        # compare_files launches ephemeral Fluent processes and is not permitted.
        tools = [tool for tool in get_solve_domain_tools() if tool.spec.name in DOMAIN_TOOLS]
        found = {tool.spec.name for tool in tools}
        if found != DOMAIN_TOOLS:
            raise RuntimeError(f"Upstream MCP contract changed; missing domain tools: {sorted(DOMAIN_TOOLS - found)}")
        self._register_domain_tools(tools)
