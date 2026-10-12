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
import threading
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / 'PyAnsys/output/phase9-ewf-server3-997k/20261010'
sys.path.insert(0, str(REPO / 'PyAnsys/src'))


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
    result = subprocess.run(['/bin/ps', '-ww', '-p', str(pid), '-o', 'state=,command='],
                            capture_output=True, text=True, timeout=5, close_fds=False)
    line = result.stdout.strip()
    return bool(line) and not line.startswith('Z') and expected in line


def health():
    """Finite, authenticated, read-only health RPC; no SDK bootstrap or cleanup."""
    import grpc
    from grpc_health.v1 import health_pb2, health_pb2_grpc
    from pyansys_fluent.connection import resolve_connection_kwargs
    try:
        kw = resolve_connection_kwargs('3', start_transcript=False, tcp_timeout_seconds=3)
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
    receipt = read(OUT / 'desktop-controller.json')
    preparation = read(OUT / 'campaign-manifest.json')
    continuation = receipt.get('continuation_manifest')
    campaign = read(Path(continuation)) if continuation else preparation
    mesh = campaign.get('active_mesh')
    child = campaign if continuation else (read(OUT / f'{mesh}-run.json') if mesh else {})
    live, live_age = tail(receipt.get('live_transcript'))
    passive, passive_age = tail(OUT / 'passive-supervision.txt')
    if passive_age is not None and (live_age is None or passive_age < live_age):
        live, live_age = passive, passive_age
    log, log_age = tail(receipt.get('log'))
    ages = [age for age in [live_age, log_age] if age is not None]
    activity_age = min(ages) if ages else None
    running = alive(receipt.get('pid'), receipt.get('controller_process_match', 'run_phase9_mesh_startup.py campaign'))
    rows = re.findall(r'^\s*(\d+)\s+[\d.+eE-]+\s+[\d.+eE-]+', live, re.M)
    batches = re.findall(r'^BATCH (\S+) (\S+) (\d+) (\d+)', log, re.M)
    complete = campaign.get('status') in {'COMPLETE_PREPARATION_ONLY', 'COMPLETE_NATIVE_CONTINUATION', 'COMPLETE_NATIVE_SCHEDULE_FINAL_VERIFICATION_PENDING'}
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
            'completed_meshes': preparation.get('completed', []), 'active_mesh': mesh,
            'continuation_manifest': continuation,
            'child_status': child.get('status'),
            'verified_native_end': child.get('verified_native_end'),
            'active_journal': child.get('active_journal'),
            'latest_pair_iteration': child.get('latest_pair', {}).get('native_iteration'),
            'active_target': child.get('active_target'),
            'last_streamed_iteration': int(rows[-1]) if rows else None,
            'last_submitted_batch': batches[-1] if batches else None,
            'activity_age_seconds': activity_age, 'event': event,
            'never_exit_fluent': True, 'server_id': '3',
            'server_activity_evidence': 'Native transcript and controller receipts',
            'requires_desktop_running': True}


def notify(message):
    try:
        subprocess.run(['/usr/bin/osascript', '-e', 'display notification ' + json.dumps(message)
                        + ' with title "Phase 9 — Server 3"'],
                       capture_output=True, timeout=10, close_fds=False)
    except (OSError, subprocess.TimeoutExpired):
        pass


def wake(event, thread, executable):
    path = OUT / f'supervision-event-{time.time_ns()}.json'
    write(path, event)
    prompt = (
        f'Automatic Server 3 / 997604-cell EWF event: {event["event"]}. Read {path}, '
        f'{OUT}/run-manifest.json and current controller receipts. '
        'This chat owns Server 3 only following the human transfer on 10 October. '
        'Do not control Server 6 or other servers. Resume EWF Plan v1 from the '
        'verified N8080 parent with inherited 0.650 ms film age. Reconcile '
        'controller PID, active native journal, native iteration, accepted film '
        'age, and preserved pair before continuation. Never duplicate an active '
        'solve. Preserve Fluent; watcher must never stop it. Use the working '
        'desktop controller and native callback/save/reopen at control changes. '
        'Recover technical problems in scope. Verify checkpoint pairs and final '
        'N50900 / 200 ms endpoint with bulk active, including saved-pair reopening. '
        'Normal progress stays quiet. Notify on completion or material failure.')
    log_path = path.with_suffix('.codex.log')
    # Queue on the existing daemon-owned chat. A separate exec/resume writer
    # conflicts with the desktop writer even when this chat is not calculating.
    try:
        result = subprocess.run(
            [executable, 'queue', '--thread', thread, '--message', prompt], cwd=REPO,
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20, close_fds=False)
        log_path.write_text(result.stdout + result.stderr)
        return {'log': str(log_path), 'event_record': str(path), 'thread_id': thread,
                'status': 'QUEUED' if result.returncode == 0 else 'FAILED',
                'returncode': result.returncode}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'log': str(log_path), 'event_record': str(path), 'thread_id': thread,
                'status': 'FAILED', 'error_type': type(exc).__name__}


def capture_passive():
    """Observe native output while SDK bootstrap waits for a busy solver.

    Bounded streaming only; no Scheme, solve, interrupt, or exit requests.
    """
    import grpc
    from ansys.api.fluent.v0 import transcript_pb2, transcript_pb2_grpc
    from pyansys_fluent.connection import resolve_connection_kwargs
    kw = resolve_connection_kwargs('3', start_transcript=False, tcp_timeout_seconds=3)
    while read(OUT / 'human-pause.json').get('status') not in {'HUMAN_REQUESTED_PAUSE', 'PAUSED_BY_HUMAN'}:
        try:
            with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
                stream = transcript_pb2_grpc.TranscriptStub(channel).BeginStreaming(
                    transcript_pb2.TranscriptRequest(), timeout=60,
                    metadata=(('password', kw['password']),))
                with (OUT / 'passive-supervision.txt').open('a') as output:
                    for response in stream:
                        output.write(response.transcript)
                        output.flush()
        except grpc.RpcError:
            pass
        time.sleep(2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interval', type=float, default=30)
    parser.add_argument('--stall-seconds', type=float, default=600)
    parser.add_argument('--thread-id', default=os.environ.get('CODEX_THREAD_ID'))
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    if args.once:
        state = snapshot(args.stall_seconds)
        state['server_health'] = health()
        print(json.dumps(state, indent=2))
        return
    executable = shutil.which('codex') or '/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
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
    last_health = None
    last_wake_attempt = 0
    guard = subprocess.Popen(['/usr/bin/caffeinate', '-i', '-w', str(os.getpid())], close_fds=False)
    threading.Thread(target=capture_passive, daemon=True).start()
    while True:
        if read(OUT / 'human-pause.json').get('status') in {'HUMAN_REQUESTED_PAUSE', 'PAUSED_BY_HUMAN'}:
            write(OUT / 'continuous-supervision.json', {'status': 'PAUSED_BY_HUMAN', 'watcher_pid': os.getpid(), 'automatic_recovery_enabled': False, 'never_exit_fluent': True})
            guard.terminate()
            return
        state = snapshot(args.stall_seconds)
        if time.monotonic() - health_at >= 300 or state['event']:
            last_health = health()
            health_at = time.monotonic()
        state.update(server_health=last_health, interval_seconds=args.interval,
                     stall_review_seconds=args.stall_seconds, awake_guard_pid=guard.pid,
                     originating_thread=args.thread_id)
        event = state['event']
        key = json.dumps([state['controller_pid'], event, state['active_mesh'],
                          state['verified_native_end'], state['active_journal']])
        if event and key not in handled and time.monotonic() - last_wake_attempt >= 300:
            wake_record = wake(state, args.thread_id, executable)
            last_wake_attempt = time.monotonic()
            if wake_record['status'] == 'QUEUED':
                handled.append(key)
            notify('EWF schedule ended; endpoint verification is starting.' if
                   event == 'PREPARATION_COMPLETE' else
                   'Run supervision detected a stop or delay. Recovery review is starting.')
            print(json.dumps({'event': event, 'wake': wake_record}), flush=True)
        state.update(handled_event_keys=handled[-100:], wake=wake_record)
        write(OUT / 'continuous-supervision.json', state)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
