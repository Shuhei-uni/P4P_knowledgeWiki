"""Resume a hash-verified Phase 10 N5 pair in a new evidence directory.

The original interrupted run remains untouched. One controller performs the
reopen/settings check, five-update smoke, and the remaining selected queue.
"""
import functools
import json
import os
from pathlib import Path
import queue
import sys
import threading
import time

import phase10_core as core
import ansys.fluent.core._grpc_services as low
import ansys.fluent.core.services as high
from ansys.fluent.core.utils.fluent_version import FluentVersion


def main():
    config_path = sys.argv[sys.argv.index('--config') + 1]
    cfg = json.loads(Path(config_path).read_text())
    root = Path(cfg['work'])
    proof = json.loads(Path(cfg['reconciliation']).read_text())
    core.validate_reconciliation(root, cfg, proof)
    recovery = proof['technical_recovery']
    assert recovery['resume_iteration'] == 5
    assert recovery['previous_attempt_updates_upper_bound'] == 1000
    assert proof['lost_updates_cap'] == 995
    pair = recovery['pair']
    for kind in ('case', 'data'):
        assert core.sha(pair[kind]) == pair[kind + '_sha256']
    assert core.sha(cfg['common_case']) == cfg['common_case_sha256']
    expected = json.loads((root / 'common-settings.json').read_text())
    level = recovery['level']
    folder = root / level
    receipt = json.loads((folder / 'manifest.json').read_text())
    assert receipt['status'] == 'STOPPED_REQUIRES_REVIEW'
    assert receipt['completed_iterations'] == 5 and receipt['checkpoints'] == []
    assert receipt['solver_mesh_proof']['status'] == 'PASS'
    low._server_supports_v1 = lambda channel: False
    high.create_service_factory = functools.partial(
        high.create_service_factory, product_version=FluentVersion.v252)
    core.pf.config.check_health = False
    connected = queue.Queue()

    def attach():
        try:
            connected.put(core.pf.connect_to_fluent(
                ip=cfg['ip'], port=int(os.environ['PHASE10_API_PORT']),
                password=os.environ['PHASE10_API_PASSWORD'], allow_remote_host=True,
                insecure_mode=True, cleanup_on_exit=False, start_watchdog=False,
                start_transcript=False))
        except BaseException as error:
            connected.put(error)

    threading.Thread(target=attach, daemon=True).start()
    try:
        s = connected.get(timeout=60)
    except queue.Empty:
        core.dump(root / 'resume-startup.json', {'status': 'TIMEOUT_BEFORE_REOPEN',
                  'controller_pid': os.getpid(), 'solved_updates': 0})
        os._exit(2)
    if isinstance(s, BaseException):
        raise s
    s.events.stop()
    try:
        with core.native_transcript(s.settings.file, folder / 'resume-reopen-smoke.trn'):
            core.reopen(s, pair)
            core.require_state_same(core.state(s), expected)
            assert core.iteration(s) == 5
            core.compute(s, receipt['report_names'])
            s.settings.parallel.timer.usage()
            monitors = folder / 'monitors'
            monitors.mkdir(exist_ok=False)
            files = s.settings.solution.monitor.report_files
            assert set(files.get_object_names()) == {
                name + '-rfile' for name in receipt['report_paths']}
            for name, info in receipt['report_paths'].items():
                path = str(monitors / (name + '.out'))
                files[name + '-rfile'].set_state({'file_name': path,
                    'report_defs': [name], 'frequency': 10, 'active': True})
                assert Path(files[name + '-rfile'].get_state()['file_name']) == Path(path)
                info['file'] = path
            begin = time.perf_counter()
            s.settings.solution.run_calculation.iterate(iter_count=5)
            seconds = time.perf_counter() - begin
            failure = core.native_numerical_error(folder / 'resume-reopen-smoke.trn')
            if failure:
                raise core.NativeNumericalFailure(failure)
            assert core.iteration(s) == 10
            receipt['resume_smoke_reports'] = core.compute(s, receipt['report_names'])
            new_pair = core.save_pair(s, folder / 'resume-smoke-N10')
            assert new_pair['counts'] == pair['counts']
            core.reopen(s, new_pair)
            core.require_state_same(core.state(s), expected)
            assert core.iteration(s) == 10
            receipt.update(status='SMOKE_VERIFIED', completed_iterations=10,
                smoke_pair=new_pair, original_smoke_pair=pair,
                smoke_seconds=receipt['smoke_seconds'] + seconds,
                recovery_smoke_seconds=seconds, technical_recovery=recovery)
            receipt.pop('error', None)
            core.dump(folder / 'manifest.json', receipt)
            core.dump(root / 'resume-startup.json', {'status': 'RESUME_SMOKE_VERIFIED',
                'controller_pid': os.getpid(), 'resumed_level': level,
                'resumed_from': 5, 'verified_iteration': 10,
                'pair': new_pair, 'exact_settings_verified': True,
                'no_reinitialization': True, 'original_evidence_preserved': True})
            proof['checkpoint_reopen_verified'] = True
            proof['reopened_level'] = level
            proof['reopened_iteration'] = 10
            core.dump(cfg['reconciliation'], proof)
    except BaseException as error:
        core.dump(root / 'resume-startup.json', {'status': 'RESUME_FAILED',
                  'controller_pid': os.getpid(), 'error': str(error)})
        raise
    print('RESUME_SMOKE_VERIFIED_N10', flush=True)
    # The unchanged native queue path reopens this N10 pair, continues to N1000,
    # and then uses N1000 blocks. Numerical failures preserve and skip a level.
    sys.argv = [sys.argv[0], '--config', config_path, '--continue-reconciled']
    core.main()


if __name__ == '__main__':
    main()
