"""Finish the already-authorized 42.35 ms handoff after preservation succeeds.

This waits on the existing preservation process. It never sends an interrupt,
retries an installer, or treats a transport timeout as permission to solve.
"""
from pathlib import Path
import argparse, fcntl, hashlib, json, os, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'PyAnsys/output/phase9-server6-slit154k/20261010'

def write(value):
    p = OUT / 'from4235-handoff-supervision.json'
    tmp = p.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(p)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preserver-pid', type=int, required=True)
    parser.add_argument('--thread-id', required=True)
    args = parser.parse_args()
    lock = (OUT / 'from4235-handoff.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    guard = subprocess.Popen(['caffeinate', '-i', '-w', str(os.getpid())])
    state = dict(status='WAITING_PRESERVED_IDLE_ENDPOINT', pid=os.getpid(),
                 preserver_pid=args.preserver_pid, server_id='6',
                 native_origin=80580, film_origin_s=.04235, step_s=2.5e-6,
                 target_film_s=.1, solve_replayed=False, never_exit_fluent=True)
    write(state)
    try:
        while True:
            receipt = json.loads((OUT / 'from4235-partial-preservation.json').read_text())
            if receipt['status'] == 'PARTIAL_NATIVE_ENDPOINT_PRESERVED_IDLE':
                assert receipt['reopen_verified'] and receipt['no_solve_replay']
                break
            try:
                os.kill(args.preserver_pid, 0)
            except ProcessLookupError:
                raise RuntimeError('Preservation process ended without a verified idle endpoint')
            time.sleep(10)
        review = json.loads((OUT / 'from4235-code-review.json').read_text())
        assert review['status'] == 'REVIEWED'
        for path, digest in review['source_hashes'].items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
        # Fail closed on any previous dispatch. The installer executes exactly once.
        assert not (OUT / 'from4235-2p5us-launch.json').exists()
        state.update(status='INSTALLER_STARTED_AFTER_VERIFIED_PRESERVATION',
                     preserved_iteration=receipt['native_iteration'],
                     preserved_film_s=receipt['film']['film_elapsed_time'])
        write(state)
        installer = ROOT / 'PyAnsys/scripts/setup/resume_phase9_server6_slit_from4235ms.py'
        with (OUT / 'from4235-2p5us-installer.log').open('a') as log:
            completed = subprocess.run([sys.executable, '-u', str(installer)], cwd=ROOT,
                                       stdout=log, stderr=subprocess.STDOUT)
        assert completed.returncode == 0, 'Installer failed; reconcile before any retry'
        launch = json.loads((OUT / 'from4235-2p5us-launch.json').read_text())
        assert launch['status'] == 'DISPATCHED'
        state.update(status='RECONCILED_PARENT_AND_DISPATCHED', launch=launch)
        write(state)
    except Exception as exc:
        state.update(status='HANDOFF_REQUIRES_RECONCILIATION', error=str(exc))
        write(state)
        prompt = (f'Server 6 slit154k from42.35 handoff needs recovery. Read {OUT}/'
                  'from4235-handoff-supervision.json and from4235-partial-preservation.json, '
                  'then reconcile host/native state. Human selected N80580/42.35ms, '
                  '2.5us to100ms; numerical diagnostics only, no automatic rollback. '
                  'Never replay a timeout or rerun an installer without reconciliation. '
                  'Preserve all pairs and Fluent. Own only Server6 slit154k.')
        cli = '/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
        queued = subprocess.run([cli, 'queue', '--thread', args.thread_id, '--message', prompt],
                                cwd=ROOT, capture_output=True, text=True, timeout=20)
        (OUT / 'from4235-handoff-wake.log').write_text(queued.stdout + queued.stderr)
        raise
    finally:
        guard.terminate()

if __name__ == '__main__':
    main()
