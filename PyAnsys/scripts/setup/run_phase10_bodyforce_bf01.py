"""Native M04 N3000 restart: implicit body force ON, exactly 1000 new updates.

Deploy only after the baseline writer has exited and its partial pair is saved.
Passwords are supplied in the process environment; no initialization is used.
"""
from __future__ import annotations

import copy
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


def without_bodyforce(value):
    result = copy.deepcopy(value)
    result['models']['multiphase']['advanced_formulation'].pop('implicit_body_force')
    result['methods']['expert'].pop('implicit_bodyforce_treatment')
    return result


def main():
    cfg = json.loads(Path(sys.argv[sys.argv.index('--config') + 1]).read_text())
    root = Path(cfg['work'])
    manifest = root / 'manifest.json'
    assert not manifest.exists(), 'Existing attempt needs reconciliation'
    assert cfg['reconciliation']['old_controller_absent']
    assert cfg['reconciliation']['baseline_terminal']
    assert cfg['budget']['spent_upper_bound'] + 1000 <= 35000
    spec = cfg['spec']
    assert spec['run']['additional_updates_cap_including_smoke_and_retries'] == 1000
    pair = spec['parent']['pair']
    for kind in ('case', 'data'):
        assert core.sha(pair[kind]) == pair[kind + '_sha256']
    assert core.counts(pair['case']) == pair['counts']
    receipt = {'experiment': 'BF01', 'level': 'M04', 'status': 'CONNECTING',
               'controller_pid': os.getpid(), 'parent': pair, 'start_iteration': 3000,
               'final_iteration': 4000, 'additional_update_cap': 1000,
               'solved_updates': 0, 'checkpoints': [], 'reinitialize': False,
               'budget': cfg['budget'], 'reconciliation': cfg['reconciliation']}
    core.dump(manifest, receipt)
    low._server_supports_v1 = lambda channel: False
    high.create_service_factory = functools.partial(
        high.create_service_factory, product_version=FluentVersion.v252)
    core.pf.config.check_health = False
    attached = queue.Queue()

    def attach():
        try:
            attached.put(core.pf.connect_to_fluent(
                ip=cfg['ip'], port=cfg['port'], password=os.environ['PHASE10_API_PASSWORD'],
                allow_remote_host=True, insecure_mode=True, cleanup_on_exit=False,
                start_watchdog=False, start_transcript=False))
        except BaseException as exc:
            attached.put(exc)

    threading.Thread(target=attach, daemon=True).start()
    try:
        s = attached.get(timeout=60)
    except queue.Empty:
        receipt.update(status='CONNECTION_TIMEOUT_BEFORE_REOPEN')
        core.dump(manifest, receipt)
        os._exit(2)
    if isinstance(s, BaseException):
        receipt.update(status='CONNECTION_ERROR_BEFORE_REOPEN', error=str(s))
        core.dump(manifest, receipt)
        raise s
    s.events.stop()
    try:
        with core.native_transcript(s.settings.file, root / 'prepare-ON-N3000.trn'):
            core.reopen(s, pair)
            assert core.iteration(s) == 3000
            before = core.state(s)
            parent_manifest = json.loads(Path(cfg['parent_manifest']).read_text())
            core.require_state_same(before, parent_manifest['settings_readback'])
            primary = s.settings.setup.models.multiphase.advanced_formulation.implicit_body_force
            assert before['models']['multiphase']['advanced_formulation']['implicit_body_force'] is False
            primary.set_state(True)
            after = core.state(s)
            assert after['models']['multiphase']['advanced_formulation']['implicit_body_force'] is True
            core.require_state_same(without_bodyforce(before), without_bodyforce(after))
            expert_before = before['methods']['expert']['implicit_bodyforce_treatment']
            expert_after = after['methods']['expert']['implicit_bodyforce_treatment']
            alias = expert_before != expert_after
            if alias:
                # Prove that the expert delta follows only the primary setter.
                primary.set_state(False)
                core.require_state_same(core.state(s), before)
                primary.set_state(True)
                core.require_state_same(core.state(s), after)
            receipt.update(settings_before=before, settings_after=after,
                           expert_alias_proven=alias, expert_before=expert_before,
                           expert_after=expert_after, scientific_delta_verified=True)
            core.dump(manifest, receipt)
            # Retain the parent's report definitions; redirect only output files.
            names = parent_manifest['report_names']
            files = s.settings.solution.monitor.report_files
            paths = {}
            (root / 'monitors').mkdir(exist_ok=False)
            for name, info in parent_manifest['report_paths'].items():
                file_path = str(root / 'monitors' / (name + '.out'))
                files[name + '-rfile'].set_state({'file_name': file_path,
                    'report_defs': [name], 'frequency': 10, 'active': True})
                readback = files[name + '-rfile'].get_state()
                assert Path(readback['file_name']) == Path(file_path)
                assert readback['frequency'] == 10 and readback['active']
                paths[name] = {'file': file_path, 'unit': info['unit']}
            receipt.update(report_names=names, report_paths=paths,
                           initial_reports=core.compute(s, names))
            saved = core.save_pair(s, root / 'ON-N3000')
            assert saved['counts'] == pair['counts']
            core.reopen(s, saved)
            assert core.iteration(s) == 3000
            core.require_state_same(core.state(s), after)
            receipt['checkpoints'].append({'iteration': 3000, 'pair': saved})
            receipt.update(status='ON_N3000_SAVED_REOPENED', completed_iteration=3000)
            core.dump(manifest, receipt)
        for target, label in ((3005, 'smoke'), (4000, 'solve')):
            start = core.iteration(s)
            assert start == (3000 if target == 3005 else 3005)
            assert 0 < target - start <= 1000 - receipt['solved_updates']
            transcript = root / ('%s-to-N%d.trn' % (label, target))
            receipt.update(status='RUNNING_SMOKE' if target == 3005 else 'RUNNING',
                           requested_target=target, active_transcript=str(transcript))
            core.dump(manifest, receipt)
            with core.native_transcript(s.settings.file, transcript):
                begin = time.perf_counter()
                s.settings.solution.run_calculation.iterate(iter_count=target-start)
                elapsed = time.perf_counter()-begin
            actual = core.iteration(s)
            receipt.update(actual_iteration=actual, solved_updates=actual-3000)
            core.dump(manifest, receipt)
            assert 0 <= receipt['solved_updates'] <= 1000
            failure = core.native_numerical_error(transcript)
            if failure:
                receipt['native_failure_transcript'] = str(transcript)
                raise core.NativeNumericalFailure(failure)
            values = core.compute(s, names)
            saved = core.save_pair(s, root / ('ON-N%d' % actual))
            assert saved['counts'] == pair['counts']
            receipt['checkpoints'].append({'iteration': actual, 'pair': saved,
                                          'reports': values, 'solver_seconds': elapsed})
            receipt['completed_iteration'] = actual
            core.dump(manifest, receipt)
            assert actual == target, 'Incomplete BF01 horizon'
            core.reopen(s, saved)
            assert core.iteration(s) == actual
            core.require_state_same(core.state(s), after)
            receipt['checkpoints'][-1]['strict_reopen_verified'] = True
            core.dump(manifest, receipt)
        receipt.update(history_verification=core.verify_histories(receipt, 4000),
                       status='COMPLETE_EXECUTION_UNQUALIFIED', final_pair=saved)
        core.dump(manifest, receipt)
    except BaseException as exc:
        try:
            actual = core.iteration(s)
            receipt.update(actual_iteration=actual, solved_updates=max(0, actual-3000))
        except BaseException:
            receipt['current_iteration_unverified'] = True
            receipt['pending_updates_upper_bound'] = receipt.get('requested_target', 3000)-3000
        receipt.update(status='NUMERICAL_FAILURE_UNQUALIFIED' if isinstance(exc, core.NativeNumericalFailure)
                       else 'STOPPED_REQUIRES_REVIEW', error=type(exc).__name__+': '+str(exc))
        core.dump(manifest, receipt)
        raise


if __name__ == '__main__':
    main()
