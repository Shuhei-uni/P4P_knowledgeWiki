"""Reconnectable passive Server 5 transcript; never sends solver commands."""
import json
import threading
import time
from pathlib import Path

import grpc
from ansys.api.fluent.v0 import transcript_pb2, transcript_pb2_grpc, settings_pb2, settings_pb2_grpc
from pyansys_fluent.connection import resolve_connection_kwargs


def read_stream_tail(path, limit=131072):
    path = Path(path)
    if not path.exists():
        return ''
    with path.open('rb') as stream:
        stream.seek(max(0, path.stat().st_size-limit))
        return stream.read().decode(errors='replace')


def journal_idle_from_attributes(attributes):
    # Require explicit loaded-case, idle-solve and closed-transcript proof.
    return (attributes.get('setup/cell-zone-conditions') is True and
            attributes.get('solution/run-calculation/iterate') is True and
            attributes.get('file/start-transcript') is True and
            attributes.get('file/stop-transcript') is False)


def native_journal_idle():
    """Finite Server 5 read-only fallback when completion text was missed."""
    try:
        kw = resolve_connection_kwargs('5', start_transcript=False, tcp_timeout_seconds=3)
        attributes = {}
        with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
            stub = settings_pb2_grpc.SettingsStub(channel)
            for path in ['setup/cell-zone-conditions', 'solution/run-calculation/iterate', 'file/start-transcript', 'file/stop-transcript']:
                request = settings_pb2.GetAttrsRequest()
                request.path_info.root = 'fluent'
                request.path_info.path = path
                request.attrs.append('active?')
                reply = stub.GetAttrs(request, metadata=(('password', kw['password']),), timeout=5)
                values = reply.values.value_map.m
                if 'active?' not in values or values['active?'].WhichOneof('value') != 'boolean':
                    return None
                attributes[path] = values['active?'].boolean
        return journal_idle_from_attributes(attributes)
    except (grpc.RpcError, TimeoutError):
        return None


def wait_for_native_journal(path, probe=native_journal_idle, sleeper=time.sleep, clock=time.monotonic):
    next_check = 0
    while True:
        text = read_stream_tail(path)
        closed = '/file/stop-transcript' in text and 'Transcript closed.' in text
        if closed or clock() >= next_check:
            idle = probe()
            next_check = clock()+60
            if idle is True:
                return
        sleeper(15)


def start_live_stream(path):
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    path.touch()
    statepath = path.with_suffix('.stream-state.json')

    def observe():
        reconnects = 0
        with path.open('a', buffering=1) as output:
            while True:
                state = {'server_id': '5', 'reconnects': reconnects, 'mutations_submitted': 0}
                try:
                    kw = resolve_connection_kwargs('5', start_transcript=False, tcp_timeout_seconds=0)
                    with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
                        stream = transcript_pb2_grpc.TranscriptStub(channel).BeginStreaming(
                            transcript_pb2.TranscriptRequest(),
                            metadata=(('password', kw['password']),), timeout=60)
                        for response in stream:
                            output.write(response.transcript)
                            output.flush()
                except grpc.RpcError as exc:
                    state['last_rpc_code'] = exc.code().name
                except Exception as exc:
                    state['error_type'] = type(exc).__name__
                state['observed_unix_s'] = time.time()
                statepath.write_text(json.dumps(state, indent=2)+'\n')
                reconnects += 1
                time.sleep(1)

    thread = threading.Thread(target=observe, name='server5-passive-transcript', daemon=True)
    thread.start()
    return thread
