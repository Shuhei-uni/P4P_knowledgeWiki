"""Bounded passive native receipt reads without session startup or solver writes."""
import json
import os
import re
from pathlib import Path

import grpc
from ansys.api.fluent.v0 import scheme_eval_pb2 as proto, scheme_eval_pb2_grpc
from ansys.fluent.core.services.scheme_eval import (
    Symbol, _convert_py_value_to_scheme_pointer, _convert_scheme_pointer_to_py_value,
)

OUT = Path(__file__).resolve().parents[2] / 'output/phase10-single-inlet-mesh-convergence'


def passive_stream(channel, metadata):
    """Read health and a finite stream when a native solve blocks Scheme reads.

    Printed progress is evidence of activity, not a verified saved endpoint.
    """
    from grpc_health.v1 import health_pb2, health_pb2_grpc
    from ansys.api.fluent.v0 import transcript_pb2, transcript_pb2_grpc
    result = {}
    try:
        health = health_pb2_grpc.HealthStub(channel).Check(
            health_pb2.HealthCheckRequest(), metadata=metadata, timeout=4)
        result['health_status'] = health_pb2.HealthCheckResponse.ServingStatus.Name(health.status)
    except grpc.RpcError as error:
        result['health_status'] = error.code().name
    parts = []
    try:
        stream = transcript_pb2_grpc.TranscriptStub(channel).BeginStreaming(
            transcript_pb2.TranscriptRequest(), metadata=metadata, timeout=8)
        for item in stream:
            parts.append(item.transcript)
            if sum(map(len, parts)) >= 65536:
                stream.cancel()
                break
    except grpc.RpcError as error:
        result['stream_status'] = error.code().name
    tail = ''.join(parts)[-6000:]
    result['live_transcript_tail'] = tail
    result['printed_iterations'] = [int(x) for x in re.findall(
        r'^\s*(\d+)\s+\d\.\d+e[+-]\d+', tail, re.M)]
    return result


def read_receipt(stub, path, metadata, limit=131072):
    path = path.replace('\\', '/').replace('"', '\\"')
    expression = ('(let ((p (open-input-file "' + path + '"))) '
                  '(let loop ((chars (quote ())) (left ' + str(limit) + ')) '
                  '(let ((c (read-char p))) '
                  '(cond ((eof-object? c) (close-input-port p) (list->string (reverse chars))) '
                  '((= left 0) (close-input-port p) (error "receipt bound")) '
                  '(else (loop (cons c chars) (- left 1)))))))')
    request = proto.SchemeEvalRequest()
    value = (Symbol('eval'), (Symbol('with-input-from-string'), expression, Symbol('read')),
             Symbol('user-initial-environment'))
    _convert_py_value_to_scheme_pointer(value, request.input, '25.2.0')
    response = stub.SchemeEval(request, metadata=metadata, timeout=15)
    return json.loads(_convert_scheme_pointer_to_py_value(response.output, '25.2.0'))


def connection(cfg, environment):
    port = int(cfg['port'])
    password = environment.get('PHASE10_API_PASSWORD')
    if not password:
        if environment.get('MESH_API_PORT') != str(port):
            raise ValueError('PHASE10_CREDENTIAL_ROUTE_MISSING')
        password = environment.get('MESH_API_PASSWORD')
    if not password:
        raise ValueError('PHASE10_CREDENTIAL_ROUTE_MISSING')
    return cfg['ip'] + ':' + str(port), [('password', password)]


def main():
    cfg = json.loads((OUT / 'run-config.json').read_text())
    result = {'native_work': cfg['work'], 'ip': cfg['ip'], 'port': cfg['port']}
    channel = None
    try:
        endpoint, metadata = connection(cfg, os.environ)
        channel = grpc.insecure_channel(endpoint)
        stub = scheme_eval_pb2_grpc.SchemeEvalStub(channel)
        result['batch'] = read_receipt(stub, cfg['work'] + '/batch-manifest.json', metadata)
        level = result['batch'].get('current_level')
        if level in [row['level'] for row in cfg['meshes']]:
            result['level'] = read_receipt(stub, cfg['work'] + '/' + level + '/manifest.json', metadata)
        result['probe_status'] = 'PASS'
    except ValueError as error:
        result['probe_status'] = str(error)
    except grpc.RpcError as error:
        result['probe_status'] = error.code().name
        if error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            result.update(passive_stream(channel, metadata))
    finally:
        if channel:
            channel.close()
    from datetime import datetime, timezone
    result['checked_utc'] = datetime.now(timezone.utc).isoformat()
    (OUT / 'latest-native-receipts.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({'probe_status': result['probe_status'], 'batch': result.get('batch'),
                     'level': {k:result.get('level', {}).get(k) for k in
                               ('level', 'status', 'completed_iterations', 'error')}}))


if __name__ == '__main__':
    main()
