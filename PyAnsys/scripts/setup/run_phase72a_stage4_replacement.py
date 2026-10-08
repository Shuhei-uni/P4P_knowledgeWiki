"""Inspect and develop the supplied Phase72A N8000 pair on owned Server 1."""
from pathlib import Path, PureWindowsPath
import argparse
import hashlib
import json
import sys
import time
import math
import re
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
import run_phase72a_stage4_analytical as base
import run_phase72a_stage4_report_cost as reports
from pyansys_fluent.remote_text import read_text, write_ascii_text_new
from pyansys_fluent import ewf_local_drain as drain
from run_phase72a_adaptive_film import FILM, history

OUT = ROOT / 'output/phase72a-stage4-replacement/20261008'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\replacement-20261008')
SHARED = PureWindowsPath(r'C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A')
LOCAL = Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase72A')
MANIFEST = OUT / 'run-manifest.json'
DT = 1e-6
BULK = ['v2-total-liquid-mass', 'v2-lower-liquid-mass', 'v2-total-vapor-mass',
        'v2-flux-phase2-steamoutlet', 'v2-flux-phase1-steamoutlet',
        'p72-contact-removal', 'p72-contact-inventory', 'v2-applied-absorber']


def values(s, names):
    return base.d.compute(s, names)


def setparams(s, changes):
    p = dict(s.rp_vars('wall-film/model-parameters'))
    assert set(changes).issubset(p)
    s.rp_vars('wall-film/model-parameters', [(k, changes.get(k, v)) for k, v in p.items()])
    actual = dict(s.rp_vars('wall-film/model-parameters'))
    assert all(actual[k] == v for k, v in changes.items())


def load_pair(s, pair):
    print('LOAD_PAIR', pair['native_iteration'], flush=True)
    for kind in ['case', 'data']:
        command = '/file/read-' + kind + ' "' + pair[kind].replace('\\', '/') + '"'
        s.scheme.eval('(ti-menu-load-string ' + json.dumps(command) + ')')
    assert base.native_iteration(s) == pair['native_iteration']
    print('LOAD_PAIR_VERIFIED', pair['native_iteration'], flush=True)


def instrument(s, folder, names):
    base.ensure_remote_directory(s, str(folder))
    files = s.settings.solution.monitor.report_files
    for name in files.get_object_names():
        files[name].active = False
    paths = {}
    for name in names:
        writer = 'replacement-' + name
        if writer not in files.get_object_names():
            files.create(name=writer)
        path = (folder / (name + '.out')).as_posix()
        assert not base.remote_file_exists(s, path)
        files[writer].set_state({'report_defs': [name], 'file_name': path, 'frequency_of': 'iteration',
                                 'frequency': 1, 'active': True})
        paths[name] = path
    for name in s.settings.solution.monitor.report_plots.get_object_names():
        s.settings.solution.monitor.report_plots[name].active = False
    return paths


def audit(s, frozen=False):
    p = dict(s.rp_vars('wall-film/model-parameters'))
    expected = json.loads((ROOT / 'output/phase72a-stage4-core-development/20261008/core17/run-manifest.json').read_text())['parent_parameters']
    expected['timestep-max'] = DT
    assert p == expected
    equations = s.settings.solution.controls.equations.get_state()
    assert all(v == (not frozen) for v in equations.values())
    for n in ['wall', drain.WALL]:
        w = s.settings.setup.boundary_conditions.wall[n].phase['mixture'].wall_film.get_state()
        assert w['eulerian_film_wall'] and not w['enable_flow_momentum_coupling']
        assert w['enable_dpm_wall_splash'] and w['allow_film_boundary_separation']
    original = json.loads((OUT / 'parent-readback.json').read_text())
    assert s.settings.setup.cell_zone_conditions.fluid.get_state() == original['cell_zones']
    for n, item in original['expressions'].items():
        assert s.settings.setup.named_expressions[n].definition() == item['definition']
    return {'parameters': p, 'equations': equations, 'drain': drain.audit(s, True),
            'bulk_absorber': 'Original phase-2 10 us contact UDF and matched momentum sinks retained'}


def prepare():
    m = json.loads(MANIFEST.read_text())
    assert m['status'] == 'PARENT_LOADED_INSPECTED'
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    assert base.native_iteration(s) == 8000
    before = snapshot(s)
    original = base.d.facets(s, 'wall')
    np.savez_compressed(OUT / 'parent-upper-fields.npz', **original)
    bulk = values(s, BULK)
    params = json.loads((ROOT / 'output/phase72a-stage4-core-development/20261008/core17/run-manifest.json').read_text())['parent_parameters']
    params['timestep-max'] = DT
    setparams(s, params)
    lower = s.settings.setup.boundary_conditions.wall[drain.WALL].phase['mixture'].wall_film
    lower.eulerian_film_wall = True
    lower.film_condition_type = 'film-wall-initial'
    lower.film_height.set_state({'option': 'value', 'value': 0.0})
    lower.enable_flow_momentum_coupling = False
    lower.enable_film_source_terms = False
    # Allocate the added lower wall, then restore every original stored field.
    s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
    s.settings.file.read_data(file_name=m['parent_pair']['data'])
    setparams(s, params)
    base.d.same_facets(original, base.d.facets(s, 'wall'))
    assert np.max(np.abs(base.d.facets(s, drain.WALL)['film-mass'])) < 1e-12
    assert dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] == before['film']['film_elapsed_time']
    base.d.q.r.require_match({'fields': values(s, BULK)}, {'fields': bulk})
    for n in ['wall', drain.WALL]:
        w = s.settings.setup.boundary_conditions.wall[n].phase['mixture'].wall_film
        w.enable_flow_momentum_coupling = False
        w.enable_dpm_wall_splash = True
        w.allow_film_boundary_separation = True
    # Protect the maximum inherited ten film updates between bulk profile refreshes.
    drain.configure(s, enabled=True, refresh_span_s=DT * params['film-per-flow-iters'])
    base.d.define_reports(s)
    # Velocity maxima on both film walls.
    surf = s.settings.solution.report_definitions.surface
    speed = 'p72r-film-speed-max'
    if speed not in surf.get_object_names(): surf.create(name=speed)
    surf[speed].set_state({'report_type': 'surface-facetmax', 'field': 'film-velocity-mag',
                          'surface_names': ['wall', drain.WALL]})
    names = sorted((reports.CORE - {'p72a-e2.7-ewf-velocity-mag-max'}) | {speed} | set(BULK))
    for folder in [WORK / 'prepared', WORK / 'prepared' / 'scratch', WORK / 'prepared' / 'monitors']:
        base.ensure_remote_directory(s, str(folder))
    paths = instrument(s, WORK / 'prepared' / 'monitors', names)
    residuals = s.settings.solution.monitor.residual
    residuals.options.print = True
    # Run the complete fixed horizon regardless of residual stop thresholds.
    residuals.options.plot = False
    for name in residuals.equations.get_object_names():
        residuals.equations[name].check_convergence = False
    s.settings.file.auto_save.data_frequency = 0
    prepared = snapshot(s)
    check = audit(s)
    pair = reports.save_pair(s, WORK / 'prepared', 'prepared-N8000')
    load_pair(s, pair)
    check = audit(s)
    reopened = snapshot(s)
    assert reopened['parameters'] == prepared['parameters']
    assert reopened['walls'] == prepared['walls']
    assert reopened['cell_zones'] == prepared['cell_zones']
    assert reopened['methods'] == before['methods']
    assert reopened['inlets'] == before['inlets']
    assert reopened['film']['film_elapsed_time'] == before['film']['film_elapsed_time']
    base.d.q.r.require_match({'fields': values(s, BULK)}, {'fields': bulk})
    # Geometry-matched upper fields are checked after the parallel reload.
    parent_mass = float(original['film-mass'].sum())
    assert math.isclose(float(base.d.facets(s, 'wall')['film-mass'].sum()), parent_mass, rel_tol=1e-12)
    dump('prepared-readback.json', reopened)
    dump('preparation-proof.json', {'audit': check, 'bulk_before': bulk, 'bulk_after': values(s, BULK),
                                  'upper_fields_exact_before_reopen': True, 'upper_mass_preserved_after_reopen': True,
                                  'new_lower_storage_initial_mass_kg': 0.0,
                                  'guide_release': '2025 R2', 'guide_figures': ['30.1', '30.2', '30.6', '30.9'],
                                  'guide_use': 'Force dependencies, phase prerequisites, film mass/XYZ source hooks, wall DPM toggles',
                                  'settings_route': 'Existing v252 Settings/API plus verified model-parameter readback; native film allocation followed by original data restore'})
    m.update(status='PREPARED_REOPEN_VERIFIED', prepared_pair=pair, latest_pair=pair,
             prepared_parameters=reopened['parameters'], report_names=names, report_paths=paths,
             bulk_reference=bulk, verified_native_end=8000, verified_film_time_s=reopened['film']['film_elapsed_time'],
             step_s=DT, bulk_equations='ACTIVE', requires_laptop_for_solve=False, blocks=[])
    dump('run-manifest.json', m)
    print('PREPARED_REOPEN_VERIFIED', pair['native_iteration'], 'bulk active, film step', DT, flush=True)


def run_probe(s, label, count, names):
    print('PREPARE_PROBE', label, count, flush=True)
    work = WORK / label
    local = OUT / label
    local.mkdir(exist_ok=False)
    for folder in [work, work / 'scratch', work / 'monitors']:
        base.ensure_remote_directory(s, str(folder))
    paths = instrument(s, work / 'monitors', names)
    initial = values(s, names)
    bulk = values(s, BULK)
    clock = dict(s.rp_vars('wall-film/solution-state'))
    start = base.native_iteration(s)
    s.tui.file.start_transcript((work / 'probe.trn').as_posix())
    t0 = time.monotonic()
    print('SUBMIT_PROBE', label, start, start + count, flush=True)
    base.d.q.r.iterate(s, count)
    seconds = time.monotonic() - t0
    final = values(s, names)
    finalclock = dict(s.rp_vars('wall-film/solution-state'))
    pair = reports.save_pair(s, work, 'final-N' + str(base.native_iteration(s)))
    s.tui.file.stop_transcript()
    text = read_text(s, (work / 'probe.trn').as_posix())
    (local / 'probe.trn').write_text(text)
    h = {}
    for n, path in paths.items():
        raw = read_text(s, path)
        (local / (n + '.out')).write_text(raw)
        h[n] = history(raw)
        assert set(range(start + 1, start + count + 1)).issubset(h[n])
    assert base.native_iteration(s) == start + count
    printed = [tuple(map(float, x.groups())) for x in FILM.finditer(text)]
    assert len(printed) == count
    assert all(math.isclose(v[1], DT, rel_tol=1e-8) for v in printed)
    base.d.q.r.require_match({'fields': values(s, BULK)}, {'fields': bulk})
    record = {'native_start': start, 'native_end': start + count, 'count': count,
              'before': initial, 'after': final, 'bulk_before': bulk, 'bulk_after': values(s, BULK),
              'clock_before': clock, 'clock_after': finalclock, 'printed_clock_count': len(printed),
              'accepted_clock_before_s': printed[0][0] - printed[0][1],
              'accepted_clock_after_s': printed[-1][0],
              'printed_added_film_time_s': count * DT, 'peak_courant': max(x[2] for x in printed),
              'pair': pair, 'solve_seconds': seconds, 'report_paths': paths,
              'bulk_equations': s.settings.solution.controls.equations.get_state()}
    dump(label + '/probe.json', record)
    print('PROBE_VERIFIED', label, record['native_end'], flush=True)
    return record, h


def prove_drain():
    m = json.loads(MANIFEST.read_text())
    assert m['status'] == 'PREPARED_REOPEN_VERIFIED'
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    prepared = m['prepared_pair']
    # The child case is already loaded and paired-reopen verified. Reading it
    # repeatedly re-enters GUI file-load warnings on this Windows session.
    audit(s)
    assert base.native_iteration(s) == prepared['native_iteration']
    original_params = dict(s.rp_vars('wall-film/model-parameters'))
    original_walls = {n: s.settings.setup.boundary_conditions.wall[n].phase['mixture'].wall_film.get_state()
                      for n in ['wall', drain.WALL]}
    attempt = str(time.time_ns())

    def restore_production():
        setparams(s, original_params)
        for n, saved in original_walls.items():
            w = s.settings.setup.boundary_conditions.wall[n].phase['mixture'].wall_film
            w.film_condition_type = saved['film_condition_type']
            w.film_height.set_state(saved['film_height'])
        drain.set_enabled(s, True)
        for name in s.settings.solution.controls.equations.get_state():
            s.settings.solution.controls.equations[name] = True
        # Re-enable and allocate source/stripping/separation arrays before data
        # restoration. The fixture disabled these models and removed storage.
        s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        print('RESTORE_PRODUCTION_DATA', flush=True)
        s.settings.file.read_data(file_name=prepared['data'])
        assert base.native_iteration(s) == prepared['native_iteration']
        audit(s)

    proof = {'status': 'PREPARING', 'fixture_updates_per_arm': 100, 'production_smoke_updates': 20,
             'production_pair': prepared, 'attempt': attempt,
             'case_reload_policy': 'Use loaded verified case; restore controls and data without repeated case reloads',
             'claim': 'Direct film removal works with bulk frozen; no physical validation'}
    dump('drain-proof.json', proof)
    try:
        for name in s.settings.solution.controls.equations.get_state():
            s.settings.solution.controls.equations[name] = False
        changes = {k: False for k in ['mom-gravity?', 'mom-aero-drive?', 'mom-wall-visc?',
                   'mom-pressure?', 'mom-spreading?', 'surface-tension?', 'dpm-collection?',
                   'dpm-splashing?', 'film-separation?', 'film-stripping?']}
        changes['secondary-phase-mode'] = 0
        setparams(s, changes)
        for n in ['wall', drain.WALL]:
            w = s.settings.setup.boundary_conditions.wall[n].phase['mixture'].wall_film
            w.film_condition_type = 'film-wall-initial'
            w.film_height.set_state({'option': 'value', 'value': 1e-4 if n == drain.WALL else 0.0})
        s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        work = WORK / 'fixture'
        for folder in [work, work / 'scratch']: base.ensure_remote_directory(s, str(folder))
        fixture = reports.save_pair(s, work, 'seed-N8000-' + str(time.time_ns()))
        proof['fixture_pair'] = fixture
        dump('drain-proof.json', proof)
        selected = ['p72d-lower-mass', 'p72d-lower-thickness', 'p72d-lower-courant',
                    'p72d-drain-rate', 'p72d-lower-inventory']
        arms = {}
        for label, enabled in [('source-off', False), ('source-on', True)]:
            if arms:
                # Reset the same fixture fields and counter through data only.
                s.settings.file.read_data(file_name=prepared['data'])
                s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
            drain.set_enabled(s, enabled)
            arm, h = run_probe(s, label + '-' + attempt, 100, selected)
            x = range(arm['native_start'] + 1, arm['native_end'] + 1)
            mass = np.array([arm['before']['p72d-lower-mass'][0]] + [h['p72d-lower-mass'][i] for i in x])
            rate = np.array([arm['before']['p72d-drain-rate'][0]] + [h['p72d-drain-rate'][i] for i in x])
            arm['mass_history_kg'] = mass.tolist()
            arm['rate_history_kg_s'] = rate.tolist()
            arms[label] = arm
            if enabled:
                loss = -np.diff(mass)
                relative = loss / (rate[:-1] * DT) - 1
                assert mass.min() >= 0 and loss.sum() > 0
                assert np.max(np.abs(relative)) < .03
                assert np.max(loss / mass[:-1]) <= .01
                proof['source_integral_relative_error_max'] = float(np.max(np.abs(relative)))
                proof['source_removed_kg'] = float(loss.sum())
            else:
                assert np.max(np.abs(mass - mass[0])) <= mass[0] * 1e-5
                assert np.max(np.abs(rate)) == 0
        proof['fixture_arms'] = arms
        restore_production()
        for name in s.settings.solution.controls.equations.get_state():
            s.settings.solution.controls.equations[name] = False
        audit(s, frozen=True)
        selected = sorted((reports.CORE - {'p72a-e2.7-ewf-velocity-mag-max'}) | {'p72r-film-speed-max'})
        arm, h = run_probe(s, 'frozen-production-smoke-' + attempt, 20, selected)
        drain_mass = sum(h['p72d-drain-rate'][i] * DT for i in range(arm['native_start'] + 1, arm['native_end'] + 1))
        changes = sum(arm['after'][n][0] - arm['before'][n][0] for n in
                      ['p72d-total-mass', 'p72d-total-outflow', 'p72d-total-stripped', 'p72d-total-separated'])
        incoming = sum(h[n][i] * DT for n in ['p72d-total-secondary', 'p72d-total-dpm']
                       for i in range(arm['native_start'] + 1, arm['native_end'] + 1))
        ledger = changes + drain_mass - incoming
        ledger_fraction = abs(ledger) / max(abs(incoming), 1e-30)
        assert drain_mass > 0
        assert math.isclose(arm['accepted_clock_after_s'] - arm['accepted_clock_before_s'], 20 * DT, abs_tol=1e-12)
        assert arm['peak_courant'] < 1
        assert ledger_fraction <= .05, 'Production probe film ledger exceeds declared 5% functional tolerance'
        proof.update(status='DRAIN_FUNCTION_VERIFIED_PENDING_RESTORE', production_smoke=arm,
                     production_direct_removal_kg=drain_mass, production_original_ledger_kg=ledger,
                     production_original_ledger_percent=100 * ledger_fraction,
                     native_outflow_convention='Direct user source excluded; established source fixture evidence retained')
    except BaseException as error:
        proof['error'] = repr(error)
        print('DRAIN_PROOF_ERROR', repr(error), flush=True)
        raise
    finally:
        restore_production()
        proof['restored_audit'] = audit(s)
        proof['restored_native_iteration'] = base.native_iteration(s)
        proof['restored_bulk'] = values(s, BULK)
        base.d.q.r.require_match({'fields': proof['restored_bulk']}, {'fields': m['bulk_reference']})
        dump('drain-proof.json', proof)
    assert proof['status'] == 'DRAIN_FUNCTION_VERIFIED_PENDING_RESTORE'
    proof['status'] = 'FROZEN_BULK_DIRECT_FILM_REMOVAL_VERIFIED'
    dump('drain-proof.json', proof)
    m.update(status='DRAIN_PROVED_READY_FOR_BULK_1000', diagnostic_updates=220, diagnostic_production_updates=20,
             diagnostics_restored_to_prepared_parent=True, external_block=None,
             session_live_state='IDLE_N8000_RESTORED')
    dump('run-manifest.json', m)
    print('FROZEN_DRAIN_PROVED', drain_mass, 'kg, restored N8000', flush=True)


def resume_drain_proof():
    """Reuse verified fixture arms; recover storage and finish the smoke only."""
    m = json.loads(MANIFEST.read_text())
    proof = json.loads((OUT / 'drain-proof.json').read_text())
    assert set(proof['fixture_arms']) == {'source-off', 'source-on'}
    assert proof['source_removed_kg'] > 0 and proof['source_integral_relative_error_max'] < .03
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    audit(s)
    prepared = m['prepared_pair']

    def restore():
        for name in s.settings.solution.controls.equations.get_state():
            s.settings.solution.controls.equations[name] = True
        s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        s.settings.file.read_data(file_name=prepared['data'])
        audit(s)
        assert base.native_iteration(s) == 8000
        base.d.q.r.require_match({'fields': values(s, BULK)}, {'fields': m['bulk_reference']})

    try:
        restore()
        for name in s.settings.solution.controls.equations.get_state():
            s.settings.solution.controls.equations[name] = False
        selected = sorted((reports.CORE - {'p72a-e2.7-ewf-velocity-mag-max'}) | {'p72r-film-speed-max'})
        arm, h = run_probe(s, 'frozen-production-smoke-recovery-' + str(time.time_ns()), 20, selected)
        indices = range(arm['native_start'] + 1, arm['native_end'] + 1)
        removed = sum(h['p72d-drain-rate'][i] * DT for i in indices)
        changes = sum(arm['after'][n][0] - arm['before'][n][0] for n in
                      ['p72d-total-mass', 'p72d-total-outflow', 'p72d-total-stripped', 'p72d-total-separated'])
        incoming = sum(h[n][i] * DT for n in ['p72d-total-secondary', 'p72d-total-dpm'] for i in indices)
        ledger = changes + removed - incoming
        fraction = abs(ledger) / max(abs(incoming), 1e-30)
        assert removed > 0 and arm['peak_courant'] < 1
        assert math.isclose(arm['accepted_clock_after_s'] - arm['accepted_clock_before_s'], 20 * DT, abs_tol=1e-12)
        assert fraction <= .05, 'Production probe film ledger exceeds 5% functional tolerance'
        proof.update(status='DRAIN_FUNCTION_VERIFIED_PENDING_RESTORE', production_smoke=arm,
                     production_direct_removal_kg=removed, production_original_ledger_kg=ledger,
                     production_original_ledger_percent=100 * fraction,
                     recovery='Reallocated production film effects before data restore; verified fixture arms reused.',
                     native_outflow_convention='Direct user source excluded; established source fixture evidence retained')
        proof.pop('error', None)
    except BaseException as error:
        proof['error'] = repr(error)
        print('DRAIN_PROOF_ERROR', repr(error), flush=True)
        raise
    finally:
        restore()
        proof['restored_audit'] = audit(s)
        proof['restored_native_iteration'] = base.native_iteration(s)
        proof['restored_bulk'] = values(s, BULK)
        dump('drain-proof.json', proof)
    proof['status'] = 'FROZEN_BULK_DIRECT_FILM_REMOVAL_VERIFIED'
    dump('drain-proof.json', proof)
    m.update(status='DRAIN_PROVED_READY_FOR_BULK_1000', diagnostic_updates=220,
             diagnostic_production_updates=20, diagnostics_restored_to_prepared_parent=True,
             external_block=None, session_live_state='IDLE_N8000_RESTORED')
    dump('run-manifest.json', m)
    print('FROZEN_DRAIN_PROVED', removed, 'kg, restored N8000', flush=True)


def recover_preparation():
    """Recover an already saved child without rebuilding or issuing a solve."""
    m = json.loads(MANIFEST.read_text())
    assert m['status'] == 'PARENT_LOADED_INSPECTED'
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    pair = {'case': str(WORK / 'prepared' / 'prepared-N8000.cas.h5'),
            'data': str(WORK / 'prepared' / 'prepared-N8000.dat.h5'), 'native_iteration': 8000}
    for kind in ['case', 'data']:
        pair[kind + '_sha256'] = base.checked_remote_sha256(s, pair[kind], str(WORK / 'scratch' / (kind + '-recovery-' + str(time.time_ns()) + '.txt')))
    print('PREPARED_PAIR_HASHED', flush=True)
    # Native TUI avoids the stalled Settings read-case response path.
    s.transcript.start(file_name=str(OUT / 'reopen-recovery-stream.txt'), write_to_stdout=False)
    for kind in ['case', 'data']:
        command = '/file/read-' + kind + ' "' + pair[kind].replace('\\', '/') + '"'
        print('REOPEN', kind, flush=True)
        s.scheme.eval('(ti-menu-load-string ' + json.dumps(command) + ')')
    s.transcript.stop()
    print('PAIR_REOPEN_RETURNED', flush=True)
    check = audit(s)
    state = snapshot(s)
    original = json.loads((OUT / 'parent-readback.json').read_text())
    assert state['native_iteration'] == 8000
    assert state['film']['film_elapsed_time'] == original['film']['film_elapsed_time']
    assert state['methods'] == original['methods']
    assert state['inlets'] == original['inlets']
    reference = {'v2-total-liquid-mass': [48.87851611854502, 'kg'], 'v2-lower-liquid-mass': [0.0002360346406965334, 'kg'],
                 'v2-total-vapor-mass': [130.7091660121107, 'kg']}
    actual = values(s, BULK)
    base.d.q.r.require_match({'fields': {k: actual[k] for k in reference}}, {'fields': reference})
    names = sorted((reports.CORE - {'p72a-e2.7-ewf-velocity-mag-max'}) | {'p72r-film-speed-max'} | set(BULK))
    paths = {n: (WORK / 'prepared' / 'monitors' / (n + '.out')).as_posix() for n in names}
    dump('prepared-readback.json', state)
    dump('preparation-proof.json', {'audit': check, 'bulk_reference': actual, 'pair': pair,
                                  'reopen_route': 'Native read-case then read-data; no initialization or solve',
                                  'guide_release': '2025 R2', 'guide_figures': ['30.1', '30.2', '30.6', '30.9'],
                                  'guide_use': 'Force dependencies, phase prerequisites, source hooks and wall DPM toggles',
                                  'recovery_reason': 'Saved child read-case Settings command stalled; native retry and readback'})
    m.update(status='PREPARED_REOPEN_VERIFIED', prepared_pair=pair, latest_pair=pair,
             prepared_parameters=state['parameters'], report_names=names, report_paths=paths,
             bulk_reference=actual, verified_native_end=8000, verified_film_time_s=state['film']['film_elapsed_time'],
             step_s=DT, bulk_equations='ACTIVE', requires_laptop_for_solve=False, blocks=[])
    dump('run-manifest.json', m)
    print('PREPARED_RECOVERY_VERIFIED', flush=True)


def dump(name, value):
    base.dump(OUT / name, value)


def snapshot(s):
    setup = s.settings.setup
    result = {
        'version': str(s.get_fluent_version()), 'native_iteration': base.native_iteration(s),
        'film': dict(s.rp_vars('wall-film/solution-state')),
        'parameters': dict(s.rp_vars('wall-film/model-parameters')),
        'equations': s.settings.solution.controls.equations.get_state(),
        'methods': s.settings.solution.methods.get_state(),
        'multiphase': setup.models.multiphase.get_state(),
        'dpm': setup.models.discrete_phase.get_state(),
        'walls': setup.boundary_conditions.wall.get_state(),
        'cell_zones': setup.cell_zone_conditions.fluid.get_state(),
        'expressions': setup.named_expressions.get_state(),
        'reports': s.settings.solution.report_definitions.get_state(),
        'materials': setup.materials.get_state(),
        'inlets': {name: getattr(setup.boundary_conditions, name).get_state()
                   for name in ['mass_flow_inlet', 'velocity_inlet']
                   if getattr(setup.boundary_conditions, name).is_active()},
        'run_controls': s.settings.solution.run_calculation.get_state(),
    }
    return result


def inspect_current():
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    state = snapshot(s)
    dump('parent-readback.json', state)
    m = json.loads(MANIFEST.read_text())
    assert state['native_iteration'] == 8000
    m['parent_pair']['native_iteration'] = state['native_iteration']
    m.update(status='PARENT_LOADED_INSPECTED', parent_film_time_s=state['film']['film_elapsed_time'])
    dump('run-manifest.json', m)
    print('PARENT_INSPECTED', state['native_iteration'], state['film'], flush=True)


def inspect_parent():
    if MANIFEST.exists():
        raise RuntimeError('Reconcile existing replacement manifest before loading again')
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    for folder in [WORK, WORK / 'scratch', WORK / 'parent']:
        base.ensure_remote_directory(s, str(folder))
    before = base.snapshot(s)
    previous = json.loads((ROOT / 'output/phase72a-stage4-core-development/20261008/core17/run-manifest.json').read_text())
    assert before['native_iteration'] == previous['verified_native_end'] == 48483
    assert before['parameters'] == previous['parent_parameters']
    assert before['film']['film_elapsed_time'] == previous['verified_film_time_s']
    preserved = previous['latest_pair']
    for kind in ['case', 'data']:
        digest = base.checked_remote_sha256(s, preserved[kind], str(WORK / 'scratch' / (kind + '-preserved-' + str(time.time_ns()) + '.txt')))
        assert digest == preserved[kind + '_sha256']
    pair = {}
    for kind, ext in [('case', 'cas.h5'), ('data', 'dat.h5')]:
        name = 'auto-8000-1-08000.' + ext
        source = SHARED / name
        with (LOCAL / name).open('rb') as stream:
            expected = hashlib.file_digest(stream, 'sha256').hexdigest()
        actual = base.checked_remote_sha256(s, str(source), str(WORK / 'scratch' / (kind + '-source-' + str(time.time_ns()) + '.txt')))
        assert actual == expected, 'Shared pair differs between computers'
        target = WORK / 'parent' / name
        assert not base.remote_file_exists(s, str(target))
        command = f'cmd /c copy /b "{source}" "{target}"'
        assert len(command) < 1024
        codes = ' '.join(str(v) for v in command.encode('ascii'))
        result = s.scheme.eval("(system (list->string (map integer->char '(" + codes + "))))")
        assert result in [0, None]
        digest = base.checked_remote_sha256(s, str(target), str(WORK / 'scratch' / (kind + '-local-' + str(time.time_ns()) + '.txt')))
        assert digest == expected
        pair[kind] = str(target)
        pair[kind + '_sha256'] = digest
    dump('preserved-previous.json', {'pair': preserved, 'live': before})
    dump('run-manifest.json', {'status': 'PARENT_COPIED', 'parent_pair': pair, 'preserved_previous': preserved,
                              'authority': 'human_20261008_replacement_bulk_1000_then_decide', 'server_id': '1',
                              'work_root': str(WORK), 'initialization': 'NO_BULK_INITIALIZATION'})
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    state = snapshot(s)
    dump('parent-readback.json', state)
    m = json.loads(MANIFEST.read_text())
    pair['native_iteration'] = state['native_iteration']
    m.update(status='PARENT_LOADED_INSPECTED', parent_pair=pair, parent_film_time_s=state['film']['film_elapsed_time'])
    dump('run-manifest.json', m)
    print('PARENT_INSPECTED', state['native_iteration'], 'film', state['film'], flush=True)
    print('EQUATIONS', state['equations'], flush=True)
    print('ZONES', list(state['cell_zones']), flush=True)
    print('WALLS', list(state['walls']), flush=True)
    print('EXPRESSIONS', list(state['expressions']), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['inspect-parent', 'inspect-current', 'prepare', 'recover-preparation'])
    a = p.parse_args()
    {'inspect-parent': inspect_parent, 'inspect-current': inspect_current, 'prepare': prepare,
     'recover-preparation': recover_preparation}[a.action]()
