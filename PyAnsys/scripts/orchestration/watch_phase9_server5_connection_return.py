"""One-shot Server 5 reachability wake-up; never submits a Fluent command."""
import argparse
import fcntl
import json
import shutil
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from pyansys_fluent.connection import resolve_connection_kwargs
import watch_phase9_server5_ewf as watcher


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-ready', action='store_true', help='Require a bounded read-only native reply, not only an open TCP port')
    args = parser.parse_args()
    lock = (watcher.OUT / 'connection-return.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    executable = shutil.which('codex')
    if not executable:
        raise RuntimeError('Codex queue executable required')
    receipt = watcher.OUT / 'connection-return.json'
    while True:
        pause = watcher.read(watcher.OUT / 'human-pause.json')
        if pause.get('status') in {'HUMAN_REQUESTED_PAUSE', 'PAUSED_BY_HUMAN'}:
            watcher.write(receipt, {'status': 'STOPPED_BY_HUMAN_PAUSE', 'server_id': '5'})
            return
        kw = resolve_connection_kwargs('5', start_transcript=False, tcp_timeout_seconds=0)
        reachable = False
        try:
            with socket.create_connection((kw['ip'], kw['port']), timeout=5):
                reachable = True
        except OSError:
            pass
        native_error = None
        if reachable and args.native_ready:
            import grpc
            from ansys.api.fluent.v0 import scheme_eval_pb2, scheme_eval_pb2_grpc
            with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
                try:
                    scheme_eval_pb2_grpc.SchemeEvalStub(channel).StringEval(
                        scheme_eval_pb2.StringEvalRequest(input='(cx-version)'),
                        metadata=(('password', kw['password']),), timeout=5)
                except grpc.RpcError as exc:
                    reachable = False
                    native_error = exc.code().name
        state = {'server_id': '5', 'observed_utc': datetime.now(timezone.utc).isoformat(),
                 'status': 'REACHABLE_RECONCILIATION_REQUIRED' if reachable else 'WAITING_FOR_CONNECTION',
                 'fluent_commands_submitted': 0, 'require_native_ready': args.native_ready,
                 'native_error': native_error}
        if reachable:
            event = watcher.snapshot()
            event['event'] = 'SERVER_NATIVE_CONTROL_RESTORED_REVIEW_REQUIRED' if args.native_ready else 'SERVER_CONNECTION_RESTORED_REVIEW_REQUIRED'
            state['wake'] = watcher.wake(event, '01a11318-855f-7d63-8a0c-76f4eb8e3c08', executable)
            watcher.write(receipt, state)
            if state['wake']['status'] == 'QUEUED':
                return
        else:
            watcher.write(receipt, state)
        time.sleep(60)


if __name__ == '__main__':
    main()
