"""Provisional M04 carrier stage; preserve DPM parity as a separate open gate.

Fresh Hybrid start from the verified OFF M04 setup, 1500 total new updates.
No particle material guesses, injection setters or DPM tracking are issued.
Deploy server locally with phase10_core.py and execution_contract.py.
"""
from __future__ import annotations
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
    cfg = json.loads(Path(sys.argv[sys.argv.index('--config') + 1]).read_text())
    root = Path(cfg['work'])
    manifest = root / 'manifest.json'
    assert not manifest.exists(), 'Existing attempt must be reconciled'
    assert cfg['preflight']['old_controller_absent'] and not cfg['preflight']['workers']
    assert cfg['budget']['spent_upper_bound'] + 1500 <= cfg['budget']['campaign_cap']
    parent = cfg['parent']
    restore = cfg['preserved_BF01_pair']
    for pair in (parent, restore):
        for kind in ('case', 'data'):
            assert core.sha(pair[kind]).lower() == pair[kind + '_sha256'].lower()
        assert core.counts(pair['case']) == pair['counts']
    receipt = {'experiment': 'R1600_CARRIER', 'level': 'M04', 'status': 'CONNECTING',
        'controller_pid': os.getpid(), 'parent': parent, 'preserved_BF01_pair': restore,
        'provisional': True, 'exact_historical_settings_parity_verified': False,
        'historical_family': 'SPIRAL_CASE4_20260725', 'fresh_start': True,
        'target_iterations': 1500, 'solved_updates': 0, 'checkpoints': [],
        'DPM_tracking_issued': False, 'DPM_stage': 'WAITING_FOR_EXACT_PARENT_CONTROLS_AND_MATERIAL',
        'budget': cfg['budget'], 'source_limits': cfg['source_limits']}
    core.dump(manifest, receipt)
    low._server_supports_v1 = lambda channel: False
    high.create_service_factory = functools.partial(
        high.create_service_factory, product_version=FluentVersion.v252)
    core.pf.config.check_health = False
    attached = queue.Queue()

    def attach():
        try:
            attached.put(core.pf.connect_to_fluent(ip=cfg['ip'], port=cfg['port'],
                password=os.environ['PHASE10_API_PASSWORD'], allow_remote_host=True,
                insecure_mode=True, cleanup_on_exit=False, start_watchdog=False,
                start_transcript=False))
        except BaseException as error:
            attached.put(error)

    threading.Thread(target=attach, daemon=True).start()
    try:
        s = attached.get(timeout=60)
    except queue.Empty:
        receipt['status'] = 'CONNECTION_TIMEOUT_BEFORE_MUTATION'
        core.dump(manifest, receipt)
        os._exit(2)
    if isinstance(s, BaseException):
        receipt.update(status='CONNECTION_ERROR_BEFORE_MUTATION', error=str(s))
        core.dump(manifest, receipt)
        raise s
    s.events.stop()
    initialized = False
    try:
        assert not s.settings.solution.run_calculation.iterating()
        assert core.iteration(s) == 3005
        expected_ON = json.loads(Path(cfg['BF01_manifest']).read_text())['settings_after']
        core.require_state_same(core.state(s), expected_ON)
        with core.native_transcript(s.settings.file, root / 'build.trn'):
            core.reopen(s, parent)
            assert core.iteration(s) == 3000
            state = core.state(s)
            expected_OFF = json.loads(Path(cfg['BF01_manifest']).read_text())['settings_before']
            core.require_state_same(state, expected_OFF)
            assert not state['models']['multiphase']['advanced_formulation']['implicit_body_force']
            assert state['injections'] == []
            assert state['models']['discrete_phase']['general_settings']['interaction']['enabled'] is False
            inlet = state['inlet']['inlet']['phase']
            assert inlet['phase-1']['momentum']['mass_flow_rate']['value'] == 80.69
            assert inlet['phase-2']['momentum']['mass_flow_rate']['value'] == 116.92
            assert inlet['mixture']['momentum']['supersonic_gauge_pressure']['value'] == 1140000.0
            assert inlet['mixture']['turbulence']['turbulent_intensity'] == 0.02109999952837825
            assert inlet['mixture']['turbulence']['hydraulic_diameter'] == 0.724
            assert s.fields.solution_variable_info.get_zones_info()['fluid'].count == 946967
            receipt['settings_readback'] = state
            receipt['carrier_settings_match_recovered_OFF_M04'] = True
            core.dump(root / 'carrier-settings.json', state)
            names = cfg['report_names']
            files = s.settings.solution.monitor.report_files
            (root / 'monitors').mkdir(exist_ok=False)
            paths = {}
            for name, info in cfg['report_paths'].items():
                path = str(root / 'monitors' / (name + '.out'))
                files[name + '-rfile'].set_state({'file_name': path,
                    'report_defs': [name], 'frequency': 10, 'active': True})
                assert Path(files[name + '-rfile'].get_state()['file_name']) == Path(path)
                paths[name] = {'file': path, 'unit': info['unit']}
            receipt.update(report_names=names, report_paths=paths)
            s.settings.file.auto_save.data_frequency = 0
            s.settings.solution.monitor.residual.options.n_save = 1600
            s.settings.solution.monitor.residual.options.n_display = 1600
            # Only history-storage lengths and file destinations change.
            core.require_state_same(core.state(s), state)
            s.settings.solution.initialization.hybrid_initialize()
            initialized = True
            saved = core.save_pair(s, root / 'prepared-N0')
            assert saved['counts'] == parent['counts']
            core.reopen(s, saved)
            assert core.iteration(s) == 0
            core.require_state_same(core.state(s), state)
            receipt['checkpoints'].append({'iteration': 0, 'pair': saved,
                'strict_reopen_verified': True, 'reports': core.compute(s, names)})
            receipt.update(status='PREPARED_REOPENED', completed_iteration=0)
            core.dump(manifest, receipt)
        # One smoke; then a fixed 1000-update block; final 499 ends at the
        # historical 1500 boundary. Monitoring does not split these solves.
        for target, label in ((1, 'smoke'), (1001, 'carrier'), (1500, 'carrier')):
            start = core.iteration(s)
            assert start == (0 if target == 1 else 1 if target == 1001 else 1001)
            assert 0 < target - start <= 1500 - receipt['solved_updates']
            trn = root / ('%s-to-N%d.trn' % (label, target))
            receipt.update(status='RUNNING_SMOKE' if target == 1 else 'RUNNING',
                requested_target=target, active_transcript=str(trn))
            core.dump(manifest, receipt)
            with core.native_transcript(s.settings.file, trn):
                begin = time.perf_counter()
                s.settings.solution.run_calculation.iterate(iter_count=target - start)
                elapsed = time.perf_counter() - begin
            actual = core.iteration(s)
            receipt.update(actual_iteration=actual, solved_updates=actual)
            core.dump(manifest, receipt)
            error = core.native_numerical_error(trn)
            if error:
                receipt['native_failure_transcript'] = str(trn)
                raise core.NativeNumericalFailure(error)
            assert actual == target
            values = core.compute(s, names)
            saved = core.save_pair(s, root / ('checkpoint-N%d' % actual))
            core.reopen(s, saved)
            assert core.iteration(s) == actual
            core.require_state_same(core.state(s), state)
            receipt['checkpoints'].append({'iteration': actual, 'pair': saved,
                'reports': values, 'solver_seconds': elapsed, 'strict_reopen_verified': True})
            receipt.update(completed_iteration=actual, smoke_verified=True)
            core.dump(manifest, receipt)
        receipt.update(status='CARRIER_COMPLETE_DPM_PENDING_UNQUALIFIED', final_pair=saved,
            history_verification=core.verify_histories(receipt, 1500))
        core.dump(manifest, receipt)
    except BaseException as error:
        if initialized:
            try:
                actual = core.iteration(s)
                receipt.update(actual_iteration=actual, solved_updates=actual)
            except BaseException:
                receipt['pending_updates_upper_bound'] = receipt.get('requested_target', 0)
        receipt.update(status='NUMERICAL_FAILURE_UNQUALIFIED' if isinstance(error, core.NativeNumericalFailure)
            else 'STOPPED_REQUIRES_REVIEW', error=type(error).__name__ + ': ' + str(error))
        core.dump(manifest, receipt)
        raise
    finally:
        s._fluent_connection._channel.close()


if __name__ == '__main__':
    main()
