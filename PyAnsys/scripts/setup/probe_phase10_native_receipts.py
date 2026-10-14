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


def receipt_target(cfg, launch):
    """Select the declared writer without changing the baseline configuration."""
    if launch.get('experiment') == 'R1600_TET_BENCHMARK':
        work = launch['work']
        prefix = 'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication1600-tet-'
        suffix = work[len(prefix):] if work.startswith(prefix) else ''
        if not re.fullmatch(r'[0-9a-f]{8}', suffix):
            raise ValueError('TET_BENCHMARK_NATIVE_ROOT_INVALID')
        if launch.get('port', cfg['port']) != cfg['port']:
            raise ValueError('TET_BENCHMARK_ENDPOINT_MISMATCH')
        return 'R1600_TET_BENCHMARK', work
    if launch.get('experiment') == 'REPLICATION_ENTHALPY_SWEEP':
        work = launch['work']
        prefix = 'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication-enthalpy-M04-'
        suffix = work[len(prefix):] if work.startswith(prefix) else ''
        if not re.fullmatch(r'[0-9a-f]{8}', suffix):
            raise ValueError('ENTHALPY_NATIVE_ROOT_INVALID')
        if launch.get('port', cfg['port']) != cfg['port']:
            raise ValueError('ENTHALPY_ENDPOINT_MISMATCH')
        return 'REPLICATION_ENTHALPY_SWEEP', work
    if launch.get('experiment') in ('R1600_DPM','R1600_DPM_LIMIT'):
        work = launch['work']
        expected = 'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/'
        suffix = work[len(expected):] if work.startswith(expected) else ''
        pattern=(r'replication1600-M04-[0-9a-f]{8}/DPM-run-[0-9a-f]{8}' if launch['experiment']=='R1600_DPM'
                 else r'replication1600-M04-[0-9a-f]{8}/DPM-limit(100000|1000000)-[0-9a-f]{8}')
        if not re.fullmatch(pattern, suffix):
            raise ValueError('R1600_DPM_NATIVE_ROOT_INVALID')
        if launch.get('port', cfg['port']) != cfg['port']:
            raise ValueError('R1600_DPM_ENDPOINT_MISMATCH')
        return launch['experiment'], work
    if launch.get('experiment') == 'R1600_CARRIER':
        work = launch['work']
        expected = 'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication1600-M04-'
        if not work.startswith(expected) or '/' in work[len(expected):]:
            raise ValueError('R1600_NATIVE_ROOT_INVALID')
        if launch.get('port', cfg['port']) != cfg['port']:
            raise ValueError('R1600_ENDPOINT_MISMATCH')
        return 'R1600_CARRIER', work
    if launch.get('experiment') == 'BF01':
        work = launch['work']
        expected = 'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/bodyforce-BF01-'
        if not work.startswith(expected) or '/' in work[len(expected):]:
            raise ValueError('BF01_NATIVE_ROOT_INVALID')
        if launch.get('port', cfg['port']) != cfg['port']:
            raise ValueError('BF01_ENDPOINT_MISMATCH')
        return 'BF01', work
    return 'BASELINE', cfg['work']


def main():
    cfg = json.loads((OUT / 'run-config.json').read_text())
    launch_path = OUT / 'current-launch.json'
    launch = json.loads(launch_path.read_text()) if launch_path.exists() else {}
    experiment, work = receipt_target(cfg, launch)
    result = {'native_work': work, 'ip': cfg['ip'], 'port': cfg['port'],
              'experiment': experiment, 'baseline_native_work': cfg['work']}
    channel = None
    try:
        endpoint, metadata = connection(cfg, os.environ)
        channel = grpc.insecure_channel(endpoint)
        stub = scheme_eval_pb2_grpc.SchemeEvalStub(channel)
        if experiment == 'R1600_TET_BENCHMARK':
            result['batch'] = read_receipt(stub, work + '/batch-manifest.json', metadata, limit=262144)
            batch = result['batch']
            if batch.get('experiment') != experiment or batch.get('selected_queue') != [1600]:
                raise ValueError('TET_BENCHMARK_BATCH_IDENTITY_MISMATCH')
            if launch.get('controller_pid') and launch['controller_pid'] != batch['controller_pid']:
                raise ValueError('TET_BENCHMARK_CONTROLLER_IDENTITY_MISMATCH')
            if batch.get('cases', {}).get('1600'):
                result['level'] = read_receipt(stub, work + '/H1600/manifest.json', metadata, limit=524288)
                if result['level'].get('enthalpy_kJ_kg') != 1600 or result['level'].get('level') != 'TET':
                    raise ValueError('TET_BENCHMARK_CASE_IDENTITY_MISMATCH')
        elif experiment == 'REPLICATION_ENTHALPY_SWEEP':
            result['batch'] = read_receipt(stub, work + '/batch-manifest.json', metadata, limit=262144)
            batch = result['batch']
            expected_queue = launch.get('selected_queue')
            if (expected_queue not in ([1440, 1520, 1680, 1760], [1760])
                or batch.get('experiment') != experiment or batch.get('selected_queue') != expected_queue):
                raise ValueError('ENTHALPY_BATCH_IDENTITY_MISMATCH')
            if launch.get('controller_pid') and batch['controller_pid'] != launch['controller_pid']:
                raise ValueError('ENTHALPY_CONTROLLER_IDENTITY_MISMATCH')
            enthalpy = batch.get('current_enthalpy_kJ_kg')
            if enthalpy in (1440, 1520, 1680, 1760):
                result['level'] = read_receipt(stub, work + '/H' + str(enthalpy) + '/manifest.json', metadata, limit=524288)
                if result['level'].get('enthalpy_kJ_kg') != enthalpy:
                    raise ValueError('ENTHALPY_CASE_IDENTITY_MISMATCH')
                result['level']['level'] = 'M04-H' + str(enthalpy)
        elif experiment in ('R1600_DPM','R1600_DPM_LIMIT'):
            result['DPM'] = read_receipt(stub, work + '/manifest.json', metadata, limit=262144)
            result['level'] = result['DPM']
            if result['level'].get('experiment') != experiment:
                raise ValueError('R1600_DPM_MANIFEST_IDENTITY_MISMATCH')
            if launch.get('controller_pid') and result['level']['controller_pid'] != launch['controller_pid']:
                raise ValueError('R1600_DPM_CONTROLLER_IDENTITY_MISMATCH')
            verification = launch.get('DPM_verification_manifest')
            if verification:
                if verification != work + '/verification.json':
                    raise ValueError('R1600_DPM_VERIFICATION_PATH_INVALID')
                verified = read_receipt(stub, verification, metadata, limit=65536)
                if (verified.get('controller_pid') != result['level']['controller_pid']
                    or not verified.get('mass_accounting_verified')
                    or verified.get('DPM_completed_updates') != 1):
                    raise ValueError('R1600_DPM_VERIFICATION_IDENTITY_MISMATCH')
                result['DPM_verification'] = verified
        elif experiment == 'R1600_CARRIER':
            result['replication1600'] = read_receipt(stub, work + '/manifest.json', metadata, limit=262144)
            result['level'] = result['replication1600']
            if result['level'].get('experiment') != experiment:
                raise ValueError('R1600_MANIFEST_IDENTITY_MISMATCH')
            if launch.get('controller_pid') and result['level']['controller_pid'] != launch['controller_pid']:
                raise ValueError('R1600_CONTROLLER_IDENTITY_MISMATCH')
            preparation = launch.get('DPM_preparation_manifest')
            if preparation:
                prefix = work + '/DPM-ready-'
                suffix = preparation[len(prefix):] if preparation.startswith(prefix) else ''
                if not re.fullmatch(r'[0-9a-f]{8}/manifest\.json', suffix):
                    raise ValueError('R1600_DPM_PREPARATION_PATH_INVALID')
                prepared = read_receipt(stub, preparation, metadata, limit=65536)
                if (prepared.get('experiment') != 'R1600_DPM_PREPARATION'
                    or prepared.get('status') != 'DPM_READY_N1500_SAVED_REOPENED'
                    or prepared.get('iteration') != 1500 or prepared.get('cells') != 946967
                    or not prepared.get('reopen_verified')):
                    raise ValueError('R1600_DPM_PREPARATION_IDENTITY_MISMATCH')
                result['DPM_preparation'] = prepared
        elif experiment == 'BF01':
            result['bodyforce'] = read_receipt(stub, work + '/manifest.json', metadata, limit=262144)
            result['level'] = result['bodyforce']
            if result['bodyforce'].get('experiment') != 'BF01':
                raise ValueError('BF01_MANIFEST_IDENTITY_MISMATCH')
            if launch.get('controller_pid') and result['bodyforce']['controller_pid'] != launch['controller_pid']:
                raise ValueError('BF01_CONTROLLER_IDENTITY_MISMATCH')
        else:
            result['batch'] = read_receipt(stub, work + '/batch-manifest.json', metadata)
            level = result['batch'].get('current_level')
            if level in [row['level'] for row in cfg['meshes']]:
                result['level'] = read_receipt(stub, work + '/' + level + '/manifest.json', metadata)
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
                               ('level', 'status', 'completed_iterations',
                                'completed_iteration', 'actual_iteration', 'solved_updates', 'error')}}))


if __name__ == '__main__':
    main()
