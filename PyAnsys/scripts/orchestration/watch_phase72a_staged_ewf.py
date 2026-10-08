"""Read-only laptop watcher for the owned Server-1 staged EWF runner.

No Fluent imports or RPCs. Notify only on completion, failure or stalled output.
"""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import time


def read(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def alive(pid):
    if not isinstance(pid, int):
        return False
    p = subprocess.run(['ps', '-p', str(pid), '-o', 'state=,command='],
                       capture_output=True, text=True, timeout=5)
    line = p.stdout.strip()
    return bool(line) and not line.startswith('Z') and 'run_phase72a_staged_ewf.py' in line


def observe(output, stall_seconds=900):
    m = read(output / 'run-manifest.json')
    status = m.get('status')
    running = alive(m.get('pid'))
    event = None
    if status == 'COMPLETE_DEVELOPED_FILM_CHECKPOINT':
        event = 'COMPLETE'
    elif status and (status.startswith('STOPPED_') or status in ['EXECUTION_REVIEW_REQUIRED', 'NATIVE_RETURN_UNCONFIRMED']):
        event = status
    elif m and not running:
        event = 'CONTROLLER_STOPPED_RECONCILE_NATIVE_JOURNAL'
    age = None
    stream = m.get('passive_transcript')
    if status == 'RUNNING_NATIVE' and stream:
        p = Path(stream)
        age = time.time()-p.stat().st_mtime if p.exists() else time.time()-m.get('heartbeat_epoch', time.time())
        progress = read(Path(m.get('passive_progress', 'missing-progress.json')))
        if progress.get('observed_epoch'):
            age = min(age, time.time()-progress['observed_epoch'])
        if running and age > stall_seconds:
            event = 'PASSIVE_OUTPUT_STALLED_REVIEW_REQUIRED'
    elif running and time.time()-m.get('heartbeat_epoch', time.time()) > stall_seconds:
        event = 'CONTROLLER_ACTIVITY_STALLED_REVIEW_REQUIRED'
    return {'observed_epoch': time.time(), 'watcher_pid': os.getpid(), 'runner_pid': m.get('pid'),
            'runner_alive': running, 'status': status, 'stage': m.get('stage'),
            'verified_native_end': m.get('verified_native_end'), 'active_target': m.get('active_target'),
            'step_s': m.get('step_s'), 'passive_output_age_s': age, 'event': event,
            'fluent_queries': False, 'fluent_controls': False}


def write(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2)+'\n')
    tmp.replace(path)


def notify(event):
    message = 'Server 1 EWF: '+event
    subprocess.run(['osascript', '-e', 'display notification '+json.dumps(message)+
                    ' with title "Staged EWF"'], capture_output=True, timeout=10)


def wake(record, output, thread):
    executable = shutil.which('codex')
    if not thread or not executable:
        return {'status': 'UNAVAILABLE'}
    prompt = ('This chat owns the staged 60k N8000 EWF run on Server 1 only. '
              f'Watcher event: {record["event"]}. Read {output}/run-manifest.json and watcher-status.json. '
              'Reconcile the runner PID, native journal return, paired endpoint and film clock. '
              'Recover ordinary implementation errors in scope, or verify completion. '
              'Do not duplicate a solve, query Scheme during an active journal, reset production fields, '
              'or control other servers. The laptop remains active. Notify only for meaningful changes.')
    try:
        result = subprocess.run([executable, 'queue', '--thread', thread, '--message', prompt],
                                capture_output=True, text=True, timeout=20)
        return {'status': 'QUEUED' if result.returncode == 0 else 'FAILED', 'returncode': result.returncode}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'status': 'FAILED', 'error_type': type(exc).__name__}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--interval', type=float, default=30)
    p.add_argument('--stall-seconds', type=float, default=900)
    p.add_argument('--once', action='store_true')
    p.add_argument('--thread-id', default=os.environ.get('CODEX_THREAD_ID'))
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    seen = set()
    while True:
        record = observe(args.output, args.stall_seconds)
        write(args.output / 'watcher-status.json', record)
        key = (record['event'], record['active_target'], record['verified_native_end'])
        if record['event'] and key not in seen:
            seen.add(key)
            with (args.output / 'watcher-events.jsonl').open('a') as f:
                f.write(json.dumps(record)+'\n')
            if not args.once:
                try: notify(record['event'])
                except (OSError, subprocess.TimeoutExpired): pass
                write(args.output / 'watcher-wake.json', wake(record, args.output, args.thread_id))
        if args.once:
            print(json.dumps(record, indent=2));break
        if record['event'] == 'COMPLETE' or (record['event'] and not record['runner_alive']):
            break
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
