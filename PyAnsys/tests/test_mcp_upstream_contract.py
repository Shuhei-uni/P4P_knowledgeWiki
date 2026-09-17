"""Real pinned-upstream contract tests; never use a licensed/live Fluent solver."""
import asyncio
from pathlib import Path
import sys
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
pytest.importorskip('ansys.fluent.mcp', reason='Install requirements-mcp.txt to run upstream/STDIO contract tests')
from pyansys_fluent import mcp_server
from pyansys_fluent.mcp_client import open_fluent_mcp
from pyansys_fluent.mcp_policy import CORE_TOOLS, DOMAIN_TOOLS, FORBIDDEN_TOOLS, SessionPolicyError


def test_real_upstream_registration_and_offline_stdio():
    async def scenario():
        async with open_fluent_mcp(connect=False) as client:
            tools = await client.session.list_tools()
            names = {tool.name for tool in tools.tools}
            assert set(CORE_TOOLS) | DOMAIN_TOOLS <= names
            assert not names & FORBIDDEN_TOOLS
            result = await client.call('validate_code', {'code':'answer = 2 + 2'})
            assert result['status'] == 'ok'
    asyncio.run(scenario())


def test_preserving_attach_and_cleanup(monkeypatch):
    import ansys.fluent.core as pyfluent
    solver = Mock()
    attach = Mock(return_value=solver)
    monkeypatch.setattr(pyfluent,'connect_to_fluent',attach)
    monkeypatch.setattr(pyfluent,'launch_fluent',Mock(side_effect=AssertionError('must not launch')))
    monkeypatch.setattr(mcp_server,'resolve_connection_kwargs',lambda *args: {'ip':'127.0.0.1','port':5000,'password':'test','cleanup_on_exit':False})
    async def scenario():
        backend = mcp_server.PreservingBackend('2')
        assert (await backend.connect()).status == 'ok'
        assert (await backend.connect()).status == 'error'
        backend.close_sync()
        with pytest.raises(SessionPolicyError):
            await backend.disconnect()
        solver.exit.assert_not_called()
        solver.close.assert_not_called()
        assert attach.call_args.kwargs['cleanup_on_exit'] is False
    asyncio.run(scenario())


def test_endpoint_overrides_and_lifecycle_snippets_rejected():
    async def scenario():
        backend = mcp_server.PreservingBackend()
        assert (await backend.connect(ip='elsewhere',port=5)).status == 'error'
        assert (await backend.run_code('solver.exit()')).status == 'error'
        assert (await backend.validate_code('solver.tui.exit()')).status == 'error'
    asyncio.run(scenario())
