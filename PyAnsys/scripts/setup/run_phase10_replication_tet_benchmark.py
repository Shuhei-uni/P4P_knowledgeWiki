"""Fresh, matched tet Case4 benchmark; reuse the verified carrier/DPM runner."""
import functools
import json
import os
from pathlib import Path
import queue
import sys
import threading
import time

import phase10_core as core
import run_phase10_replication_enthalpies as repeat
import ansys.fluent.core._grpc_services as low
import ansys.fluent.core.services as high
from ansys.fluent.core.utils.fluent_version import FluentVersion


def prepare(s, cfg):
    root = Path(cfg['work'])
    path = root / 'preparation-manifest.json'
    receipt = {'experiment': 'R1600_TET_BENCHMARK', 'status': 'PREPARING',
               'source_case': cfg['source_case'], 'source_sha256': cfg['source_sha256'],
               'solved_updates': 0, 'DPM_updates': 0, 'initializations': 0,
               'preserved_pair': cfg['preserved_pair'], 'controller_pid': os.getpid()}
    core.dump(path, receipt)
    expected = cfg['cases'][0]['settings']
    begin = time.perf_counter()
    loaded = False
    try:
        with core.native_transcript(s.settings.file, root / 'tet-preparation.trn'):
            if cfg.get('prepared_zero_resume'):
                resume = cfg['prepared_zero_resume']
                assert resume['solved_updates'] == 0 and resume['DPM_updates'] == 0
                for kind in ['case', 'data']:
                    assert core.sha(resume['pair'][kind]) == resume['pair'][kind + '_sha256']
                core.reopen(s, resume['pair'])
                repeat.verify_pair(s, resume['pair'], expected, 0, 2964593, initialized_zero=True)
                receipt.update(status='PREPARED_N0_REUSED_REOPENED_SETTINGS_VERIFIED',
                               pair=resume['pair'], settings_readback=core.state(s),
                               strict_reopen_verified=True, initialization_repeated=False,
                               initialized_raw_iteration_counter=core.iteration(s))
                core.dump(path, receipt)
                cfg.update(fresh_parent=resume['pair'], fresh_parent_settings=expected,
                           fresh_parent_iteration=core.iteration(s), fresh_parent_initialized=True,
                           report_names=cfg['reference_report_names'], report_paths=cfg['reference_report_paths'])
                core.dump(root / 'prepared-run-config.json', cfg)
                return
            loaded = True
            s.settings.file.read_case(file_name=cfg['source_case'])
            assert s.fields.solution_variable_info.get_zones_info()['fluid'].count == 2964593
            bc = s.settings.setup.boundary_conditions
            assert bc.pressure_outlet.get_object_names() == ['outlet']
            assert set(bc.wall.get_object_names()) == {'wall-fluid', 'bottom'}
            bc.pressure_outlet.rename(new='steamoutlet', old='outlet')
            bc.wall.rename(new='wall', old='wall-fluid')
            assert bc.pressure_outlet.get_object_names() == ['steamoutlet']
            assert set(bc.wall.get_object_names()) == {'wall', 'bottom'}
            injections = s.settings.setup.models.discrete_phase.injections
            assert set(injections.get_object_names()) == set(expected['injections'])
            for name, values in expected['models']['discrete_phase']['injections'].items():
                injections[name].set_state(values)
                initial = injections[name].initial_values
                initial.mass_flow_rate.scale_by_area = False
                initial.mass_flow_rate.total_flow_rate = values['initial_values']['mass_flow_rate']['total_flow_rate']
                initial.velocity.use_face_normal_direction = True
                initial.velocity.magnitude = values['initial_values']['velocity']['magnitude']
            # M04 has one unused inert material in its namespace. Mirror it for
            # strict whole-state parity; every injection uses liquid-water.
            materials = s.settings.setup.materials.inert_particle
            for name, values in expected['materials']['inert_particle'].items():
                if name not in materials.get_object_names():
                    materials.create(name=name)
                    materials[name].set_state(values)
            s.settings.setup.models.discrete_phase.tracking.max_num_steps = 100000
            core.require_state_same(core.state(s), expected)
            monitors = root / 'preparation-monitors'
            monitors.mkdir()
            cfg['report_names'], cfg['report_paths'] = core.reports(s, monitors)
            assert cfg['report_names'] == cfg['reference_report_names']
            # Equal reporting overhead, including residual settings and plots.
            s.settings.solution.monitor.residual.set_state(cfg['reference_residual_monitor'])
            plots = s.settings.solution.monitor.report_plots
            names = plots.get_object_names()
            if names:
                plots.delete(name_list=names)
            for name, values in cfg['reference_report_plots'].items():
                plots.create(name=name)
                plots[name].set_state(values)
            core.require_state_same(plots.get_state(), cfg['reference_report_plots'])
            s.settings.file.auto_save.data_frequency = 0
            core.require_state_same(core.state(s), expected)
            # The recovered case carries a historical iteration/history clock.
            # Clear that history only in this explicitly fresh, zero-solve child.
            s.settings.solution.monitor.residual.reset()
            # Exactly one fresh initialization; the shared runner reloads N0.
            receipt['status'] = 'INITIALIZING_FRESH_HYBRID'
            core.dump(path, receipt)
            s.settings.solution.initialization.hybrid_initialize()
            receipt['initializations'] = 1
            initial_counter = core.iteration(s)
            receipt['initialized_raw_iteration_counter'] = initial_counter
            core.dump(path, receipt)
            assert initial_counter in (0, 1), 'Unexpected counter after fresh Hybrid initialization'
            pair = core.save_pair(s, root / 'tet-prepared-N0')
            repeat.verify_pair(s, pair, expected, 0, 2964593, initialized_zero=True)
            receipt.update(status='PREPARED_N0_REOPENED_SETTINGS_VERIFIED', pair=pair,
                           settings_readback=core.state(s), strict_reopen_verified=True,
                           preparation_seconds=time.perf_counter() - begin,
                           source_mesh_counts=pair['counts'],
                           boundary_role_renames={'outlet': 'steamoutlet', 'wall-fluid': 'wall'},
                           reports=core.compute(s, cfg['report_names']))
            core.dump(path, receipt)
            cfg.update(fresh_parent=pair, fresh_parent_settings=expected,
                       fresh_parent_iteration=core.iteration(s), fresh_parent_initialized=True)
            core.dump(root / 'prepared-run-config.json', cfg)
    except BaseException as error:
        receipt.update(status='PREPARATION_ERROR_ZERO_SOLVED_UPDATES',
                       error=type(error).__name__ + ': ' + str(error))
        core.dump(path, receipt)
        if loaded:
            core.reopen(s, cfg['preserved_pair'])
            assert core.iteration(s) == 1500
            core.require_state_same(core.state(s), cfg['preserved_settings'])
            receipt['preserved_M04_restored_on_error'] = True
            core.dump(path, receipt)
        raise


def main():
    cfg = json.loads(Path(sys.argv[sys.argv.index('--config') + 1]).read_text())
    root = Path(cfg['work'])
    path = root / 'batch-manifest.json'
    assert not path.exists(), 'Existing tet benchmark must be reconciled before replay'
    assert cfg['expected_cells'] == 2964593 and cfg['level'] == 'TET'
    assert [c['enthalpy_kJ_kg'] for c in cfg['cases']] == [1600]
    assert cfg['budget']['selected_update_cap'] == 1500
    assert cfg['budget']['spent_upper_bound'] + 1500 <= cfg['budget']['campaign_cap'] == 35000
    assert core.sha(cfg['source_case']) == cfg['source_sha256']
    for kind in ['case', 'data']:
        assert core.sha(cfg['preserved_pair'][kind]) == cfg['preserved_pair'][kind + '_sha256']
    batch = {'experiment': 'R1600_TET_BENCHMARK', 'status': 'CONNECTING',
             'controller_pid': os.getpid(), 'selected_queue': [1600], 'cases': {},
             'solved_updates': 0, 'budget': cfg['budget'], 'tracking_max_num_steps': 100000,
             'expected_cells': 2964593, 'reference': cfg['reference']}
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
        assert not s.settings.solution.run_calculation.iterating()
        if cfg.get('prepared_zero_resume'):
            assert core.iteration(s) in (0, 1)
        else:
            assert core.iteration(s) == 1500
        core.require_state_same(core.state(s), cfg['preserved_settings'])
        prepare(s, cfg)
        batch.update(status='RUNNING', current_enthalpy_kJ_kg=1600,
                     preparation_manifest=str(root / 'preparation-manifest.json'))
        core.dump(path, batch)
        repeat.run_case(s, cfg, cfg['cases'][0], batch, path)
        batch.update(status='COMPLETE_SERIES_EVIDENCE_VERIFIED_UNQUALIFIED',
                     current_enthalpy_kJ_kg=None, DPM_completed_updates=1)
        core.dump(path, batch)
    except BaseException as error:
        batch.update(status='STOPPED_PRESERVE_ENDPOINT', error=type(error).__name__ + ': ' + str(error))
        core.dump(path, batch)
        raise
    finally:
        s._fluent_connection._channel.close()


if __name__ == '__main__':
    main()
