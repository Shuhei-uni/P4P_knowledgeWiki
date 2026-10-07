"""Watch the owned Phase 9 controller and wake its originating chat on events.

Read-only with respect to Fluent. Recovery belongs to the awakened phase-loop.
Never submit a solve, replace a case, interrupt, exit, or restart Fluent here.
"""
from pathlib import Path
import argparse
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / 'PyAnsys/output/phase9-mesh-convergence-server4/20261007'
sys.path.insert(0, str(REPO / 'PyAnsys/src'))
from pyansys_fluent.execution_contract import should_check_health


def write(path, value):
    temp = path.with_suffix(f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def read(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def tail(path):
    if not path:
        return '', None
    try:
        path = Path(path)
        with path.open('rb') as stream:
            stream.seek(max(0, path.stat().st_size - 131072))
            text = stream.read().decode(errors='replace')
        return text, max(0, time.time() - path.stat().st_mtime)
    except OSError:
        return '', None


def alive(pid, expected):
    if not isinstance(pid, int):
        return False
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'state=,command='],
                            capture_output=True, text=True, timeout=5)
    line = result.stdout.strip()
    return bool(line) and not line.startswith('Z') and expected in line


def health():
    """Finite, authenticated, read-only health RPC; no SDK bootstrap or cleanup."""
    import grpc
    from grpc_health.v1 import health_pb2, health_pb2_grpc
    from pyansys_fluent.connection import resolve_connection_kwargs
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO/'PyAnsys/.env',override=True)
        kw = resolve_connection_kwargs('4', start_transcript=False, tcp_timeout_seconds=3)
        with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
            reply = health_pb2_grpc.HealthStub(channel).Check(
                health_pb2.HealthCheckRequest(), timeout=5,
                metadata=(('password', kw['password']),))
        return {'status': 'SERVING' if reply.status == 1 else 'NOT_SERVING',
                'code': reply.status}
    except Exception as exc:
        # No exception text: endpoint configuration can contain credentials.
        return {'status': 'UNCONFIRMED', 'error_type': type(exc).__name__,
                'rpc_code': exc.code().name if isinstance(exc, grpc.RpcError) else None,
                'interpretation': 'Timeout alone does not prove idle or failed Fluent.'}


def snapshot(stall_seconds=180):
    preflight=read(OUT/'connection-block.json')
    if preflight.get('status')=='WAITING_SERVER4_CREDENTIALS':
        status=health()
        return {'observed_utc':datetime.now(timezone.utc).isoformat(), 'watcher_pid':os.getpid(), 'controller_pid':None, 'controller_alive':False, 'campaign_status':'WAITING_SERVER4_CREDENTIALS', 'active_mesh':'2_6M', 'verified_native_end':None, 'event':'CONNECTION_READY_INSPECT_BEFORE_LAUNCH' if status['status']=='SERVING' else None, 'server_health':status, 'server_id':'4', 'never_exit_fluent':True, 'requires_desktop_running':True}
    receipt = read(OUT / 'desktop-controller.json')
    campaign = read(OUT / 'campaign-manifest.json')
    mesh = campaign.get('active_mesh')
    child = read(OUT / f'{mesh}-run.json') if mesh else {}
    live, live_age = tail(receipt.get('live_transcript'))
    log, log_age = tail(receipt.get('log'))
    ages = [age for age in [live_age, log_age] if age is not None]
    activity_age = min(ages) if ages else None
    running = alive(receipt.get('pid'), 'run_phase9_server4_2_6M.py campaign')
    rows = re.findall(r'^\s*(\d+)\s+[\d.+eE-]+\s+[\d.+eE-]+', live, re.M)
    batches = re.findall(r'^BATCH (\S+) (\S+) (\d+) (\d+)', log, re.M)
    complete = campaign.get('status') == 'COMPLETE_PREPARATION_ONLY'
    if complete:
        event = 'PREPARATION_COMPLETE'
    elif not running:
        event = 'CONTROLLER_STOPPED'
    elif activity_age is None or activity_age > stall_seconds:
        event = 'PROGRESS_STALLED_REVIEW_REQUIRED'
    else:
        event = None
    return {'observed_utc': datetime.now(timezone.utc).isoformat(),
            'watcher_pid': os.getpid(), 'controller_pid': receipt.get('pid'),
            'controller_alive': running, 'campaign_status': campaign.get('status'),
            'completed_meshes': campaign.get('completed', []), 'active_mesh': mesh,
            'child_status': child.get('status'),
            'verified_native_end': child.get('verified_native_end'),
            'latest_pair_iteration': child.get('latest_pair', {}).get('native_iteration'),
            'active_target': child.get('active_target'),
            'last_streamed_iteration': int(rows[-1]) if rows else None,
            'last_submitted_batch': batches[-1] if batches else None,
            'activity_age_seconds': activity_age, 'event': event,
            'never_exit_fluent': True, 'server_id': '4',
            'server_activity_evidence': 'Native transcript and controller receipts',
            'requires_desktop_running': True}


def notify(message):
    try:
        subprocess.run(['osascript', '-e', 'display notification ' + json.dumps(message)
                        + ' with title "Phase 9 — Server 4"'],
                       capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        pass


def wake(event, thread, executable):
    path = OUT / f'supervision-event-{time.time_ns()}.json'
    write(path, event)
    prompt = (
        'This chat owns ONLY Server 4 and mesh 2_6M. Never query or control Server 3. '
        'If the event is CONNECTION_READY_INSPECT_BEFORE_LAUNCH, authentication is restored but live state is not yet inspected. Read the Server 4 handoff, inspect the live session before acting, review and verify the new runner then prepare/launch it. '
        'The user authorized continuous Phase 9 supervision. This is an automatic '
        f'event from the watcher: {event["event"]}. Read {path} and current machine '
        'evidence. Use phase-loop to inspect Server 4 and finish ordinary recovery '
        'or verify completion without waiting for the human. Server 4 only. NEVER '
        'exit, terminate, or restart Fluent. Do not submit a duplicate solve or '
        'replace an active session. Reconcile controller PID, native iteration, '
        'active horizon, saved case/data and film clock before any continuation. '
        'The authorized endpoint is the 2_6M full-feed hold, all bulk equations '
        'active, provisional Stage 4 EWF; no bulk freeze or EWF-only continuation. '
        'Keep the approved 08b contract and human exceptions. Checkpoints on '
        'Windows local disk. Keep the watcher active. Notify the user only for '
        'meaningful changes, completion, failure, or required human input. If '
        'Fluent is still calculating or saving, continue observation quietly.'
    )
    log_path = path.with_suffix('.codex.log')
    # Queue on the existing daemon-owned chat. A separate exec/resume writer
    # conflicts with the desktop writer even when this chat is not calculating.
    try:
        result = subprocess.run(
            [executable, 'queue', '--thread', thread, '--message', prompt], cwd=REPO,
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20)
        log_path.write_text(result.stdout + result.stderr)
        return {'log': str(log_path), 'event_record': str(path), 'thread_id': thread,
                'status': 'QUEUED' if result.returncode == 0 else 'FAILED',
                'returncode': result.returncode}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'log': str(log_path), 'event_record': str(path), 'thread_id': thread,
                'status': 'FAILED', 'error_type': type(exc).__name__}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interval', type=float, default=30)
    parser.add_argument('--stall-seconds', type=float, default=180)
    parser.add_argument('--thread-id', default=os.environ.get('CODEX_THREAD_ID'))
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    if args.once:
        state = snapshot(args.stall_seconds)
        state['server_health'] = health()
        print(json.dumps(state, indent=2))
        return
    executable = shutil.which('codex')
    if not args.thread_id or not executable:
        raise RuntimeError('Exact originating chat and Codex executable required')
    lock = (OUT / 'supervision.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # A laptop/login restart must not revoke an explicit human pause.
    # Do not create an awake guard, check Fluent, or queue recovery while paused.
    while read(OUT / 'human-pause.json').get('status') in {
            'HUMAN_REQUESTED_PAUSE', 'PAUSED_BY_HUMAN'}:
        write(OUT / 'continuous-supervision.json', {
            'status':'PAUSED_BY_HUMAN','watcher_pid':os.getpid(),
            'observed_utc':datetime.now(timezone.utc).isoformat(),
            'automatic_recovery_enabled':False,'requires_explicit_resume':True})
        time.sleep(args.interval)
    previous = read(OUT / 'continuous-supervision.json')
    handled = previous.get('handled_event_keys', [])
    wake_record = previous.get('wake')
    health_at = 0
    previous_health_event = None
    last_health = None
    last_wake_attempt = 0
    guard = subprocess.Popen(['caffeinate', '-i', '-w', str(os.getpid())])
    while True:
        state = snapshot(args.stall_seconds)
        health_event = (state['controller_pid'], state['event'], state['active_mesh'], state['verified_native_end']) if state['event'] else None
        if should_check_health(time.monotonic(), health_at, health_event, previous_health_event):
            last_health = health()
            health_at = time.monotonic()
        previous_health_event = health_event
        state.update(server_health=last_health, interval_seconds=args.interval,
                     stall_review_seconds=args.stall_seconds, awake_guard_pid=guard.pid,
                     originating_thread=args.thread_id)
        event = state['event']
        key = json.dumps([state['controller_pid'], event, state['active_mesh'],
                          state['verified_native_end']])
        if event and key not in handled and time.monotonic() - last_wake_attempt >= 300:
            wake_record = wake(state, args.thread_id, executable)
            last_wake_attempt = time.monotonic()
            if wake_record['status'] == 'QUEUED':
                handled.append(key)
            notify('Preparation finished; endpoint verification is starting.' if
                   event == 'PREPARATION_COMPLETE' else
                   'Run supervision detected a stop or delay. Recovery review is starting.')
            print(json.dumps({'event': event, 'wake': wake_record}), flush=True)
        state.update(handled_event_keys=handled[-100:], wake=wake_record)
        write(OUT / 'continuous-supervision.json', state)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
