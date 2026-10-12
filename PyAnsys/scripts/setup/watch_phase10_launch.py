"""One bounded local retry job for the user-authorized Phase 10 launch.

Wait for this assigned endpoint; reconcile its pilot, then dispatch the selected
server-local run. Credentials are inherited from environment, never persisted.
The local computer must remain awake until dispatch is verified.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/meshing'), str(ROOT / 'src')]
from publish_single_family import connect, read_text
from pyansys_fluent.common import remote_file_exists

OUT = ROOT / 'output/phase10-single-inlet-mesh-convergence'
WORK = json.loads((OUT / 'run-config.json').read_text())['work']
PORT = int(os.environ['MESH_API_PORT'])
IP = json.loads((OUT / 'run-config.json').read_text())['ip']
STATUS = OUT / 'launch-retry-status.json'


def save(status, **fields):
    value = {'status': status, 'pid': os.getpid(), 'port': PORT,
             'checked_utc': datetime.now(timezone.utc).isoformat(), **fields}
    tmp = STATUS.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(value, indent=2)); tmp.replace(STATUS)


def healthy():
    channel = grpc.insecure_channel(IP + ':' + str(PORT))
    try:
        result = health_pb2_grpc.HealthStub(channel).Check(
            health_pb2.HealthCheckRequest(),
            metadata=[('password', os.environ['MESH_API_PASSWORD'])], timeout=3)
        return result.status == health_pb2.HealthCheckResponse.SERVING
    except grpc.RpcError:
        return False
    finally:
        channel.close()


def inspect():
    # Do not run a Windows shell/CIM query through Fluent while a controller
    # is using it. Passive receipt reads avoid that extra external command.
    s = connect(); s.events.stop()
    cfg = json.loads((OUT / 'run-config.json').read_text())
    levels = []
    for row in cfg['meshes']:
        path = WORK + '/' + row['level'] + '/manifest.json'
        if remote_file_exists(s, path):
            levels.append({'path': path, 'text': read_text(s, path)})
    def optional(name):
        path = WORK + '/' + name
        return json.loads(read_text(s, path)) if remote_file_exists(s, path) else None
    return {'levels': levels, 'batch': optional('batch-manifest.json'),
            'pilot': optional('pilot-manifest.json'), 'workers': None,
            'process_check': 'NOT_QUERIED_DURING_LIVE_CONTROL'}


def main():
    deadline = time.monotonic() + 4 * 3600
    save('WAITING_FOR_API', maximum_wait_seconds=4 * 3600,
         local_computer_required_until_dispatch=True, full_batch_launched=False)
    print('WAITING_FOR_API', PORT, flush=True)
    while time.monotonic() < deadline:
        if not healthy():
            save('WAITING_FOR_API', maximum_wait_seconds=4 * 3600,
                 local_computer_required_until_dispatch=True, full_batch_launched=False)
            time.sleep(30)
            continue
        evidence = inspect()
        (OUT / 'launch-retry-inspection.json').write_text(json.dumps(evidence, indent=2))
        if evidence['batch']:
            save('BATCH_ALREADY_PRESENT', batch=evidence['batch'])
            return
        levels = evidence['levels']
        if any(json.loads(item['text'])['status'] in
               ['BUILDING', 'PREPARED_REOPENED', 'RUNNING'] for item in levels):
            save('WAITING_FOR_PILOT_TERMINAL_RECEIPT', process_check=evidence['process_check'])
            time.sleep(30)
            continue
        if not levels:
            intent_path = OUT / 'current-launch.json'
            intent = json.loads(intent_path.read_text()) if intent_path.exists() else {}
            if intent.get('port') == PORT and intent.get('status') in (
                    'DISPATCHING', 'DETACHED_PROCESS_CREATED'):
                save('WAITING_FOR_EXISTING_LAUNCH_RECEIPT')
                time.sleep(30)
                continue
            mode = 'pilot'
        elif len(levels) == 1 and json.loads(levels[0]['text'])['status'] == 'SMOKE_VERIFIED':
            if (evidence.get('pilot') or {}).get('status') != 'SMOKE_VERIFIED':
                save('WAITING_FOR_PILOT_TERMINAL_RECEIPT')
                time.sleep(30)
                continue
            mode = 'batch'
        else:
            save('PILOT_RECONCILIATION_REQUIRED', levels=levels, full_batch_launched=False)
            return
        save('DISPATCHING_' + mode.upper())
        result = subprocess.run([sys.executable,
            str(ROOT / 'scripts/setup/deploy_phase10_mesh_family.py'), mode],
            cwd=ROOT.parent, timeout=120)
        if result.returncode:
            save('LAUNCH_RECONCILIATION_REQUIRED', mode=mode, returncode=result.returncode)
            return
        if mode == 'batch':
            # Deployment proves process creation; native manifest must prove run start.
            time.sleep(20)
            evidence = inspect()
            if evidence['batch']:
                save('BATCH_START_VERIFIED', batch=evidence['batch'], full_batch_launched=True,
                     local_computer_required_until_dispatch=False)
            else:
                save('BATCH_DISPATCHED_START_UNCONFIRMED', evidence=evidence)
            return
        time.sleep(30)
    save('API_UNAVAILABLE_WAIT_LIMIT', full_batch_launched=False)


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        save('RETRY_STOPPED', error=str(exc))
        raise
