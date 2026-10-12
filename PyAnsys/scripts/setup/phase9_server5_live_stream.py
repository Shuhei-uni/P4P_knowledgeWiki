"""Reconnectable passive Server 5 transcript; never sends solver commands."""
import json
import threading
import time
from pathlib import Path

import grpc
from ansys.api.fluent.v0 import transcript_pb2, transcript_pb2_grpc
from pyansys_fluent.connection import resolve_connection_kwargs


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
