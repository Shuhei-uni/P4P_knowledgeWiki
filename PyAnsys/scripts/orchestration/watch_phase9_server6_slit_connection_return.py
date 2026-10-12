"""One-shot Server 6 slit connectivity wake; no Fluent commands or solve replay."""
from pathlib import Path
import fcntl
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'PyAnsys/src'))
from pyansys_fluent.connection import resolve_connection_kwargs

OUT = ROOT / 'PyAnsys/output/phase9-server6-slit154k/20261010'
THREAD = '01a1248b-42cc-7960-80c1-06f28d165070'
CODEX = '/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'


def main():
    lock = (OUT / 'connection-return.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    while True:
        pause = OUT / 'human-pause.json'
        if pause.exists() and json.loads(pause.read_text()).get('status') == 'PAUSED_BY_HUMAN':
            return
        kw = resolve_connection_kwargs('6', start_transcript=False, tcp_timeout_seconds=0)
        reachable = False
        try:
            with socket.create_connection((kw['ip'], kw['port']), timeout=3):
                reachable = True
        except OSError:
            pass
        native_read_error = None
        if reachable:
            try:
                from watch_phase9_server6_slit_ewf import snapshot
                snapshot()
            except Exception as exc:
                reachable = False
                native_read_error = type(exc).__name__
        state = {'status': 'REACHABLE_RECONCILIATION_REQUIRED' if reachable else 'WAITING_FOR_CONNECTION',
                 'server_id': '6', 'lane': 'slit154k', 'pid': os.getpid(),
                 'observed_utc': datetime.now(timezone.utc).isoformat(),
                 'interval_seconds': 30, 'fluent_commands_submitted': 0}
        if native_read_error:
            state.update(status='WAITING_FOR_NATIVE_EVIDENCE', native_read_error=native_read_error)
        if reachable:
            prompt = (
                'Server 6 vertical-slit connectivity has returned after EVIDENCE_UNREACHABLE. '
                f'Read {OUT}/network-reconciliation.json and {OUT}/connection-return.json. '
                'Use the existing read-only watcher snapshot to refresh the host job and run manifests, '
                'then reconcile the controller, native iteration/film clock, transcripts and saved pairs '
                'before any solve or settings command. TCP reachability is not proof of solver health. '
                'Never replay from the earlier timeout. Own only Server 6 slit154k; preserve Fluent '
                'and all endpoints. Parent N5080/3.5 ms; target 200 ms, final 195–200 ms bulk active. '
                'Recover within the recorded Phase 9 settings and timestep ladder. '
                'Read the lane CONTEXT.md and setup.md. Notify only on completion, meaningful failure '
                'or required user action; normal progress stays quiet.'
                f' Read {OUT}/lower-step-code-review.json if present. A 2.5 us recovery installer is '
                'staged in PyAnsys/scripts/setup/resume_phase9_server6_slit_ewf.py for an exact '
                'terminal N14580/36.25 ms Courant failure. Review its code and prerequisites before '
                'execution; it requires a terminal host job, idle Fluent, failed-pair preservation, '
                'and hash-verified healthy N9580/11.25 ms restoration. If the refreshed state differs, '
                'adapt recovery to actual evidence; never replay the timed-out batch.'
            )
            try:
                result = subprocess.run([CODEX, 'queue', '--thread', THREAD, '--message', prompt],
                                        cwd=ROOT, capture_output=True, text=True, timeout=20)
                state['wake_returncode'] = result.returncode
                (OUT / 'connection-return.codex.log').write_text(result.stdout + result.stderr)
            except (OSError, subprocess.TimeoutExpired):
                state['wake_returncode'] = 'UNCONFIRMED'
        receipt = OUT / 'connection-return.json'
        temporary = receipt.with_suffix('.tmp')
        temporary.write_text(json.dumps(state, indent=2) + '\n')
        temporary.replace(receipt)
        if state.get('wake_returncode') == 0:
            return
        time.sleep(30)


if __name__ == '__main__':
    main()
