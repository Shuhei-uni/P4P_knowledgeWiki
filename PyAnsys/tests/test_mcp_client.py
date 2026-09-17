import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pyansys_fluent.mcp_client import FluentMCPClient, ExecutionUncertain, MCPCallError, decode_result


def envelope(payload=None, text=None, error=False):
    return SimpleNamespace(structuredContent=payload, isError=error, content=[] if text is None else [SimpleNamespace(type='text', text=text)])


@pytest.mark.parametrize('payload', [{'status':'error'}, {'ok':False}, {'valid':False}, {'error':'failed'}])
def test_typed_failure_is_not_success(payload):
    with pytest.raises(MCPCallError):
        decode_result(envelope(payload))


def test_standard_result_shapes():
    assert decode_result(envelope({'status':'ok'})) == {'status':'ok'}
    assert decode_result(envelope(text='{"a":null,"b":[]}')) == {'a':None,'b':[]}
    with pytest.raises(MCPCallError):
        decode_result(envelope(text='not json'))
    with pytest.raises(MCPCallError):
        decode_result(envelope({'status':'ok'}, error=True))


class FakeSession:
    def __init__(self, results):
        self.results = iter(results)
        self.calls = []
    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        value = next(self.results)
        if isinstance(value, BaseException):
            raise value
        return envelope(value)


def test_validate_precedes_execution():
    session = FakeSession([{'status':'ok'}, {'status':'ok'}])
    asyncio.run(FluentMCPClient(session).validate_and_run('value = 3'))
    assert [x[0] for x in session.calls] == ['validate_code','run_code']


def test_validation_failure_never_executes():
    session = FakeSession([{'status':'error'}])
    with pytest.raises(MCPCallError):
        asyncio.run(FluentMCPClient(session).validate_and_run('value = 3'))
    assert len(session.calls) == 1


def test_partial_failure_blocks_replay_but_allows_inspection():
    async def scenario():
        session = FakeSession([{'status':'error','message':'partial'}, {'value':4}])
        client = FluentMCPClient(session)
        with pytest.raises(ExecutionUncertain):
            await client.call('run_code', {'code':'value = 3'})
        with pytest.raises(ExecutionUncertain):
            await client.call('run_code', {'code':'value = 3'})
        with pytest.raises(ExecutionUncertain):
            await client.call('connect')
        assert await client.call('get_state') == {'value':4}
        assert len(session.calls) == 2
    asyncio.run(scenario())


def test_lost_response_is_uncertain_and_not_retried():
    session = FakeSession([ConnectionError('lost response')])
    with pytest.raises(ExecutionUncertain):
        asyncio.run(FluentMCPClient(session).call('run_code'))
    assert len(session.calls) == 1


def test_timeout_does_not_claim_solver_stopped():
    class SlowSession:
        async def call_tool(self, name, arguments):
            await asyncio.sleep(1)
    client = FluentMCPClient(SlowSession(), timeout=0.001)
    with pytest.raises(ExecutionUncertain):
        asyncio.run(client.call('run_code'))
    assert client.uncertain


@pytest.mark.parametrize('tool', ['disconnect','manage_fluent','compare_files'])
def test_session_tools_rejected_before_wire_call(tool):
    session = FakeSession([])
    with pytest.raises(MCPCallError):
        asyncio.run(FluentMCPClient(session).call(tool))
    assert not session.calls
