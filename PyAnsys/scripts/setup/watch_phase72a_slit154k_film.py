"""Observe streamed film evidence and interrupt a numerically unsafe batch.

This watcher never submits a solve. Each update is recorded on local disk.
The calculation controller owns normal checkpoints and numerical recovery.
"""
from pathlib import Path
import argparse
import json
import math
import os
import sys
import time
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))
import continue_phase72a_slit154k_film as run


def record(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f'.{os.getpid()}.tmp')
    temporary.write_text(json.dumps(value, indent=2, default=str) + '\n')
    temporary.replace(path)


def alive(pid):
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        try:
            code = wintypes.DWORD()
            return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def notify(message):
    statement = 'display notification ' + json.dumps(message) + ' with title "Server 3 wall film"'
    try:
        return subprocess.run(['osascript', '-e', statement], check=False, capture_output=True, timeout=10).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def inspect_text(path):
    pending, rows = [], []
    for line in path.read_text(errors='replace').splitlines():
        match = run.ref.SUB.search(line)
        if match:
            pending.append(list(map(float, match.groups()[1:])))
        match = run.ref.FILM.search(line)
        if match:
            values = list(map(float, match.groups()))
            terminal = pending[-1] if pending else []
            values.append((max(terminal) if all(math.isfinite(x) for x in terminal) else float('nan')) if terminal else None)
            rows.append(values)
            pending = []
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controller-pid', type=int, required=True)
    parser.add_argument('--notify', action='store_true', help='Local desktop alert on a numerical stop or controller exit')
    args = parser.parse_args()
    run.ref.dump = record
    run.configure()
    s = run.source.attach()
    control = s.settings.solution.run_calculation
    control.interrupt.is_active()
    control.iterate.is_active()
    run.ref.dump(run.OUT / 'watcher-ready.json', {'controller_pid': args.controller_pid,
                 'watcher_pid': os.getpid(), 'cached_interrupt_channel': True,
                 'observed_utc': datetime.now(timezone.utc).isoformat()})
    alerted = False
    stopped_batches = set()
    while alive(args.controller_pid):
        m = json.loads(run.ref.MANIFEST.read_text())
        folder = Path(m.get('active_output', str(run.OUT)))
        start, end = m['verified_native_end'], m.get('active_target')
        path = folder / f'batch-N{start}-N{end}.txt'
        rows = inspect_text(path) if m['status'] == 'RUNNING' and path.exists() else []
        unsafe = [v for v in rows if not all(math.isfinite(x) for x in v if x is not None)
                  or v[2] > 1 or (v[3] is not None and v[3] > 1)]
        missed = 0
        clustered = []
        for value in rows:
            missed = missed + 1 if value[3] is not None and value[3] > 1e-5 else 0
            if missed >= 2:
                clustered.append(value)
        unsafe += clustered
        status = {'observed_utc': datetime.now(timezone.utc).isoformat(), 'controller_pid': args.controller_pid,
                  'controller_alive': True, 'manifest_status': m['status'], 'verified_native_end': start,
                  'active_target': end, 'active_transcript': str(path), 'streamed_updates': len(rows),
                  'last_streamed_film_time_s': rows[-1][0] if rows else None,
                  'peak_streamed_film_cfl': max(v[2] for v in rows) if rows else None,
                  'terminal_inner_above_1': sum(v[3] is not None and v[3] > 1 for v in rows),
                  'terminal_inner_tolerance_misses': sum(v[3] is not None and v[3] > 1e-5 for v in rows),
                  'unsafe_live_record_count': len(unsafe), 'steady_film': False}
        run.ref.dump(run.OUT / 'live-supervision.json', status)
        if unsafe and str(path) not in stopped_batches:
            latest = json.loads(run.ref.MANIFEST.read_text())
            if latest['status'] != 'RUNNING' or latest.get('active_target') != end or latest['verified_native_end'] != start or Path(latest.get('active_output', str(run.OUT))) != folder:
                time.sleep(1)
                continue
            alerted = True
            stopped_batches.add(str(path))
            run.ref.dump(run.OUT / 'live-numerical-stop.json', {'status': status, 'first_unsafe_record': unsafe[0]})
            if args.notify:
                notify('A numerical guard triggered. The supervisor is checking the native run and preserving its endpoint.')
            if control.interrupt.is_active() and not control.iterate.is_active():
                control.interrupt()
            print('INTERRUPTED_UNSAFE_FILM_BATCH', json.dumps(status), flush=True)
        time.sleep(1)
    m = json.loads(run.ref.MANIFEST.read_text())
    run.ref.dump(run.OUT / 'supervisor-exit.json', {'observed_utc': datetime.now(timezone.utc).isoformat(),
                 'controller_pid': args.controller_pid, 'controller_alive': False,
                 'manifest_status': m['status'], 'numerical_interrupt_requested': alerted})
    if args.notify:
        notify('The film controller stopped at status: ' + m['status'] + '. The saved run record has the result.')


if __name__ == '__main__':
    main()
