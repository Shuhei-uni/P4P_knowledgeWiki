import argparse
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pyansys_fluent import mcp_inspection


class FakeClient:
    def __init__(self):
        self.calls = []

    async def call(self, name, arguments):
        self.calls.append((name, arguments))
        return {"status": "ok", "tool": name}


def args(**overrides):
    values = {
        "server_id": "2", "timeout": None, "query": None,
        "status_only": False, "paths": None, "root_path": "setup.models",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def fake_mcp(client):
    @asynccontextmanager
    async def open_mcp(*_args, **_kwargs):
        yield client
    return open_mcp


def test_status_only_captures_mcp_session_and_solver_status(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(mcp_inspection, "open_fluent_mcp", fake_mcp(client))

    payload = asyncio.run(mcp_inspection.inspect(args(status_only=True)))

    assert payload["status"] == "OBSERVED"
    assert payload["paths"] == []
    assert [name for name, _ in client.calls] == ["session_status", "solver_status"]


def test_path_inspection_includes_status_before_path_evidence(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(mcp_inspection, "open_fluent_mcp", fake_mcp(client))

    payload = asyncio.run(mcp_inspection.inspect(args(paths=["setup.models.viscous"])))

    assert payload["status"] == "OBSERVED"
    assert [name for name, _ in client.calls] == [
        "session_status", "solver_status", "describe_path", "get_state",
    ]


def test_query_and_status_only_are_mutually_exclusive():
    with pytest.raises(ValueError, match="cannot be used together"):
        asyncio.run(mcp_inspection.inspect(args(query="turbulence", status_only=True)))
