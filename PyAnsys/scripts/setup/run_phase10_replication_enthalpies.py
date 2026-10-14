"""One native writer for four fresh M04 spiral carrier/DPM repeats.

Each case has a fresh Hybrid start, N1500 including smoke, and one one-way
DPM update at 100000 steps. Stop the queue on any failed evidence check.
No automatic retries, numerical changes, or reuse of another case's fields.
"""
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
from phase10_dpm_audit import audit_report, TERMINAL
from ansys.fluent.core.filereader.case_file import CaseFile
import ansys.fluent.core._grpc_services as low
import ansys.fluent.core.services as high
from ansys.fluent.core.utils.fluent_version import FluentVersion


def verify_pair(s, pair, expected, iteration, expected_cells=946967, initialized_zero=False):
    core.reopen(s, pair)
    actual = core.iteration(s)
    if initialized_zero and iteration == 0:
        assert actual in (0, 1), 'Fresh initialized counter outside the verified zero-update range'
    else:
        assert actual == iteration
    assert pair['counts']['cells'] == expected_cells
    core.require_state_same(core.state(s), expected)
    records = CaseFile(case_file_name=pair['case']).rp_vars()['dpm/injections-list']
    frames = {name: next(r[1] for r in values if len(r) == 2 and r[0] == 'local-reference-frame')
              for name, values in records}
    assert len(frames) == 9 and all(value == 'global' for value in frames.values())


def run_case(s, cfg, item, batch, batch_path):
    cells = cfg.get('expected_cells', 946967)
    root = Path(cfg['work']) / ('H' + str(item['enthalpy_kJ_kg']))
    root.mkdir(exist_ok=False)
    path = root / 'manifest.json'
    receipt = {'experiment': 'REPLICATION_ENTHALPY_CASE', 'enthalpy_kJ_kg': item['enthalpy_kJ_kg'],
        'case': item['case'], 'level': cfg.get('level', 'M04'), 'controller_pid': os.getpid(),
        'status': 'PREPARING', 'solved_updates': 0, 'completed_iteration': 0,
        'checkpoints': [], 'DPM_update_dispatches': 0, 'DPM_completed_updates': 0,
        'source_artifacts': item['source_artifacts'], 'settings_expected': item['settings'],
        'incomplete_assumption': 'Count incomplete mass as separated in the efficiency estimate',
        'carrier_qualified': False, 'exact_July_binary_provenance_verified': False}
    batch['cases'][str(item['enthalpy_kJ_kg'])] = {'manifest': str(path), 'status': 'PREPARING'}
    def persist():
        core.dump(path, receipt)
        batch['cases'][str(item['enthalpy_kJ_kg'])].update(status=receipt['status'],
            solved_updates=receipt['solved_updates'], completed_iteration=receipt['completed_iteration'],
            DPM_completed_updates=receipt['DPM_completed_updates'])
        batch['solved_updates'] = sum(c.get('solved_updates', 0) for c in batch['cases'].values())
        core.dump(batch_path, batch)
    persist()
    initialized = False
    expected = item['settings']
    try:
        with core.native_transcript(s.settings.file, root / 'preparation.trn'):
            core.reopen(s, cfg['fresh_parent'])
            if cfg.get('fresh_parent_initialized', False):
                assert cfg['fresh_parent_iteration'] in (0, 1) and core.iteration(s) in (0, 1)
            else:
                assert core.iteration(s) == cfg.get('fresh_parent_iteration', 1500)
            core.require_state_same(core.state(s), cfg['fresh_parent_settings'])
            inlet = s.settings.setup.boundary_conditions.mass_flow_inlet['inlet']
            for phase in ['phase-1', 'phase-2']:
                inlet.phase[phase].momentum.mass_flow_rate.value = expected['inlet']['inlet']['phase'][phase]['momentum']['mass_flow_rate']['value']
            injections = s.settings.setup.models.discrete_phase.injections
            for name, values in expected['models']['discrete_phase']['injections'].items():
                injections[name].set_state(values)
                initial = injections[name].initial_values
                initial.mass_flow_rate.scale_by_area = False
                initial.mass_flow_rate.total_flow_rate = values['initial_values']['mass_flow_rate']['total_flow_rate']
                initial.velocity.use_face_normal_direction = True
                initial.velocity.magnitude = values['initial_values']['velocity']['magnitude']
            s.settings.setup.models.discrete_phase.tracking.max_num_steps = 100000
            core.require_state_same(core.state(s), expected)
            assert not s.settings.setup.models.discrete_phase.general_settings.interaction.enabled()
            assert s.fields.solution_variable_info.get_zones_info()['fluid'].count == cells
            (root / 'monitors').mkdir()
            receipt['report_names'] = cfg['report_names']
            receipt['report_paths'] = {}
            files = s.settings.solution.monitor.report_files
            for name, info in cfg['report_paths'].items():
                filename = str(root / 'monitors' / (name + '.out'))
                files[name + '-rfile'].set_state({'file_name': filename, 'report_defs': [name],
                                                'frequency': 10, 'active': True})
                assert Path(files[name + '-rfile'].get_state()['file_name']) == Path(filename)
                receipt['report_paths'][name] = {'file': filename, 'unit': info['unit']}
            s.settings.file.auto_save.data_frequency = 0
            s.settings.solution.monitor.residual.options.n_save = 1600
            s.settings.solution.monitor.residual.options.n_display = 1600
            core.require_state_same(core.state(s), expected)
            if cfg.get('fresh_parent_initialized', False):
                assert cfg['fresh_parent_iteration'] in (0, 1)
                assert core.iteration(s) in (0, 1)
            else:
                s.settings.solution.initialization.hybrid_initialize()
            initialized = True
            pair = core.save_pair(s, root / 'prepared-N0')
            verify_pair(s, pair, expected, 0, cells, cfg.get('fresh_parent_initialized', False))
            receipt['checkpoints'].append({'iteration': 0, 'pair': pair, 'strict_reopen_verified': True,
                                           'reports': core.compute(s, cfg['report_names'])})
            receipt['status'] = 'PREPARED_REOPENED'
            persist()
        for start, target in [(0, 1), (1, 1001), (1001, 1500)]:
            if start == 0 and cfg.get('fresh_parent_initialized', False):
                assert core.iteration(s) in (0, 1)
            else:
                assert core.iteration(s) == start
            assert cfg['budget']['spent_upper_bound'] + batch['solved_updates'] + target - start <= 35000
            transcript = root / ('carrier-to-N' + str(target) + '.trn')
            receipt.update(status='RUNNING_SMOKE' if target == 1 else 'RUNNING_CARRIER',
                           requested_target=target, active_transcript=str(transcript))
            persist()
            with core.native_transcript(s.settings.file, transcript):
                begin = time.perf_counter()
                s.settings.solution.run_calculation.iterate(iter_count=target - start)
                seconds = time.perf_counter() - begin
            actual = core.iteration(s)
            receipt.update(solved_updates=actual, actual_iteration=actual)
            persist()
            error = core.native_numerical_error(transcript)
            if error:
                raise core.NativeNumericalFailure(error)
            assert actual == target
            if target == 1 and cfg.get('fresh_parent_initialized', False):
                import re
                rows = re.findall(r'^\s*(\d+)\s+\d\.\d+e[+-]\d+', transcript.read_text(), re.M)
                assert rows == ['1'], 'Smoke must prove exactly one native carrier update at N1'
            reports = core.compute(s, cfg['report_names'])
            pair = core.save_pair(s, root / ('checkpoint-N' + str(actual)))
            verify_pair(s, pair, expected, actual, cells)
            receipt['checkpoints'].append({'iteration': actual, 'pair': pair,
                'strict_reopen_verified': True, 'reports': reports, 'solver_seconds': seconds,
                'transcript': str(transcript), 'transcript_sha256': core.sha(transcript)})
            receipt.update(completed_iteration=actual, smoke_verified=True, last_verified_pair=pair)
            persist()
        receipt['history_verification'] = core.verify_histories(receipt, 1500)
        receipt['carrier_pair'] = pair
        before = core.compute(s, cfg['report_names'])
        dpm_transcript = root / 'DPM-tracking.trn'
        with core.native_transcript(s.settings.file, dpm_transcript):
            report = s.settings.results.report.discrete_phase
            report.set_per_injection_zone_summaries(enable=True, reset_dpm_summaries=False)
            core.require_state_same(core.state(s), expected)
            receipt.update(status='TRACKING_DPM', DPM_update_dispatches=1, tracking_issued=True)
            persist()
            begin = time.perf_counter()
            s.tui.solve.dpm_update()
            receipt.update(DPM_completed_updates=1, tracking_seconds=time.perf_counter() - begin,
                           status='TRACKED_REPORTS_PENDING')
            persist()
            assert core.iteration(s) == 1500
            core.require_state_same(core.state(s), expected)
            core.require_state_same(core.compute(s, cfg['report_names']), before)
            pair = core.save_pair(s, root / 'tracked-N1500')
            receipt['tracked_pair'] = pair
            persist()
            receipt['report_files'] = {}
            for name in ['aggregate'] + expected['injections']:
                filename = root / ('DPM-' + name + '.txt')
                args = dict(write_to_file=True, file_name=str(filename), include_in_domain_particles=False,
                            pick_injection=name != 'aggregate')
                if name != 'aggregate':
                    args['injection'] = name
                report.extended_summary(**args)
                assert filename.is_file() and filename.stat().st_size > 0
                receipt['report_files'][name] = str(filename)
                persist()
            aggregate = audit_report(Path(receipt['report_files']['aggregate']).read_text(), item['liquid_kg_s'])
            individual = {name: audit_report(Path(receipt['report_files'][name]).read_text(),
                values['initial_values']['mass_flow_rate']['total_flow_rate'])
                for name, values in expected['models']['discrete_phase']['injections'].items()}
            tolerance = aggregate['printed_roundoff_bound_kg_s'] + sum(v['printed_roundoff_bound_kg_s'] for v in individual.values())
            for fate in TERMINAL:
                assert abs(sum(v['final_mass_kg_s'][fate] for v in individual.values()) - aggregate['final_mass_kg_s'][fate]) <= tolerance
            assert sum(v['tracked_count'] for v in individual.values()) == aggregate['tracked_count']
            assert aggregate['terminal_counts']['aborted'] == 0, 'Aborted tracks require review'
            receipt.update(aggregate=aggregate, injection_results=individual,
                efficiency_percent=100 * (1 - aggregate['final_mass_kg_s']['escaped'] / item['liquid_kg_s']),
                historical_summary=item['historical_summary'], mass_accounting_verified=True,
                report_sha256={n: core.sha(p) for n, p in receipt['report_files'].items()})
            verify_pair(s, pair, expected, 1500, cells)
            core.require_state_same(core.compute(s, cfg['report_names']), before)
            receipt.update(final_pair=pair, settings_readback=core.state(s), strict_reopen_verified=True,
                           carrier_reports_unchanged=True, status='COMPLETE_EVIDENCE_VERIFIED_UNQUALIFIED')
            persist()
        receipt.update(DPM_transcript=str(dpm_transcript), DPM_transcript_sha256=core.sha(dpm_transcript),
                       transcript_closed=True)
        persist()
        return receipt
    except BaseException as error:
        if initialized:
            try:
                receipt['solved_updates'] = core.iteration(s)
            except BaseException:
                receipt['pending_updates_upper_bound'] = receipt.get('requested_target', 0)
        receipt.update(status='STOPPED_PRESERVE_ENDPOINT', error=type(error).__name__ + ': ' + str(error))
        persist()
        raise


def main():
    cfg = json.loads(Path(sys.argv[sys.argv.index('--config') + 1]).read_text())
    root = Path(cfg['work'])
    path = root / 'batch-manifest.json'
    assert not path.exists(), 'Reconcile previous batch before replay'
    allocation = 1500 * len(cfg['cases'])
    assert cfg['budget']['selected_update_cap'] == allocation
    assert cfg['budget']['spent_upper_bound'] + allocation <= 35000
    for pair in [cfg['preserved_pair'], cfg['fresh_parent']]:
        for kind in ['case', 'data']:
            assert core.sha(pair[kind]) == pair[kind + '_sha256']
    for item in cfg['cases']:
        for name, identity in item['source_artifacts'].items():
            assert core.sha(root / 'sources' / name) == identity['sha256']
    batch = {'experiment': 'REPLICATION_ENTHALPY_SWEEP', 'status': 'CONNECTING',
        'controller_pid': os.getpid(), 'selected_queue': [c['enthalpy_kJ_kg'] for c in cfg['cases']],
        'cases': {}, 'solved_updates': 0, 'budget': cfg['budget'], 'tracking_max_num_steps': 100000}
    core.dump(path, batch)
    low._server_supports_v1 = lambda channel: False
    high.create_service_factory = functools.partial(high.create_service_factory, product_version=FluentVersion.v252)
    core.pf.config.check_health = False
    attached = queue.Queue()
    def connect():
        try:
            attached.put(core.pf.connect_to_fluent(ip=cfg['ip'], port=cfg['port'],
                password=os.environ['PHASE10_API_PASSWORD'], allow_remote_host=True, insecure_mode=True,
                cleanup_on_exit=False, start_watchdog=False, start_transcript=False))
        except BaseException as error:
            attached.put(error)
    threading.Thread(target=connect, daemon=True).start()
    try:
        s = attached.get(timeout=60)
    except queue.Empty:
        batch['status'] = 'CONNECTION_TIMEOUT_BEFORE_MUTATION'
        core.dump(path, batch)
        os._exit(2)
    if isinstance(s, BaseException):
        batch.update(status='CONNECTION_ERROR_BEFORE_MUTATION', error=str(s))
        core.dump(path, batch)
        raise s
    s.events.stop()
    try:
        assert not s.settings.solution.run_calculation.iterating() and core.iteration(s) == 1500
        core.require_state_same(core.state(s), cfg['preserved_settings'])
        for item in cfg['cases']:
            batch.update(status='RUNNING', current_enthalpy_kJ_kg=item['enthalpy_kJ_kg'])
            core.dump(path, batch)
            run_case(s, cfg, item, batch, path)
        batch.update(status='COMPLETE_SERIES_EVIDENCE_VERIFIED_UNQUALIFIED', current_enthalpy_kJ_kg=None,
                     DPM_completed_updates=len(cfg['cases']))
        core.dump(path, batch)
    except BaseException as error:
        batch.update(status='STOPPED_PRESERVE_ENDPOINT', error=type(error).__name__ + ': ' + str(error))
        core.dump(path, batch)
        raise
    finally:
        s._fluent_connection._channel.close()


if __name__ == '__main__':
    main()
