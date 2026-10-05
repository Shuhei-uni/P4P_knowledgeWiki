"""Numerical-control probes and film development from Stage 3 N5080, Server 1.

Never initialize fields, change scientific settings, or touch another server.
Native/server transcripts and paired local saves establish each completed batch.
"""
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import argparse
import json
import math
import re
import shutil
import sys
import time
import traceback
import uuid
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from run_phase72a_stage3_early_ewf import attach
from run_phase72a_stage3_server3 import state, instrument, iterate
from run_phase72a_local_film_replay import readback, require_match
from run_phase72a_e27_server1_continuation import native_iteration, pair_save, dump
from continue_phase72a_stage3_adaptive import clocks_and_residuals
from run_phase72a_adaptive_film import history, FILM, ROW
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256

OUT = ROOT / 'output/phase72a-stage3-film-development-server1/20261005'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage3\film-development-20261005')
SOURCE = ROOT / 'output/phase72a-stage3-early-ewf-server1/20261005/final-reopen.json'
MANIFEST = OUT / 'run-manifest.json'
ROOT_OUT, ROOT_WORK = OUT, WORK
SUB = re.compile(r'sub-iteration:\s*(\d+) residual - h:\s*([^;]+); u:\s*([^;]+); v:\s*(\S+)')


def film(s):
    return dict(s.rp_vars('wall-film/solution-state'))


def save(s, label):
    return pair_save(s, WORK / f'{label}.cas.h5', WORK / 'scratch', scratch_tag=label)


def invariant(actual, original, delta):
    for group in ['hooks', 'lower_film_wall', 'entry_faces', 'dpm', 'controls']:
        expected = dict(original['readback'][group])
        if group == 'controls' and 'bulk-equations' in delta:
            expected['equations'] = delta['bulk-equations']
        if actual['readback'][group] != expected:
            raise RuntimeError('Scientific invariant changed: ' + group)
    if actual['methods'] != original['methods'] or actual['setup'] != original['setup']:
        raise RuntimeError('Carrier methods or physical setup changed')
    for k, v in original['film_model'].items():
        wanted = delta.get(k, v)
        found = actual['film_model'][k]
        same = math.isclose(found, wanted, rel_tol=1e-12, abs_tol=1e-16) if type(wanted) is float else found == wanted
        if not same:
            raise RuntimeError('Film control differs: ' + k)


def controls(s, m, changes):
    before = state(s)
    clock = film(s)
    params = dict(s.rp_vars('wall-film/model-parameters'))
    if not set(changes).issubset(params):
        raise RuntimeError('Requested native film control unavailable')
    s.rp_vars('wall-film/model-parameters', [(k, changes.get(k, v)) for k, v in params.items()])
    m['controlled_delta'].update(changes)
    original = json.loads((OUT / 'parent-state.json').read_text())['state']
    prepared = state(s)
    invariant(prepared, original, m['controlled_delta'])
    require_match({'fields': prepared['readback']['fields']}, {'fields': before['readback']['fields']})
    label = f"controls-{len(m['control_trials']):02d}-N{native_iteration(s)}"
    pair = save(s, label)
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    after = state(s)
    require_match(after['readback'], prepared['readback'])
    clock_after = film(s)
    time_controls = {'timestep-max', 'ewf-adaptive?', 'courant-number', 'adapt-init-dt', 'adapt-tstp-inc', 'adapt-tstp-dec'}
    allowed_clock_changes = {'film_timestep', 'film_cfl_max'} if time_controls.intersection(changes) else set()
    if any(clock_after[k] != v for k, v in clock.items() if k not in allowed_clock_changes):
        raise RuntimeError('Film clock/fields changed during controls-only preparation')
    m['control_trials'].append({'changes': changes, 'native_iteration': native_iteration(s), 'pair': pair, 'reopen': 'PASS'})
    m['latest_pair'] = pair
    dump(OUT / f'{label}.json', {'state': after, 'film': film(s), 'pair': pair})
    dump(MANIFEST, m)


def prepare(s):
    if MANIFEST.exists():
        raise RuntimeError('Existing continuation must be reconciled, not replaced')
    if not s.settings.solution.run_calculation.iterate.is_active() or native_iteration(s) != 5080:
        raise RuntimeError('Exact idle N5080 parent required')
    source = json.loads(SOURCE.read_text())
    current = state(s)
    require_match(current['readback'], source['state']['readback'])
    for kind in ['case', 'data']:
        p = source['pair'][kind]
        # Use an explicitly local scratch directory; no source-file writes.
        ensure_remote_directory(s, str(WORK / 'scratch'))
        digest = remote_file_sha256(s, p, str(WORK / 'scratch' / f'parent-{kind}.sha256'))
        if digest != source['pair'][kind + '_sha256']:
            raise RuntimeError('Parent file hash differs')
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors']:
        ensure_remote_directory(s, str(folder))
    clock = film(s)
    if not math.isclose(clock['film_elapsed_time'], .0035, abs_tol=1e-12):
        raise RuntimeError('Parent film clock differs')
    m = {'status': 'PREPARING', 'server_id': '1', 'authority': 'human_2026_10_05_fastest_numerically_adequate_stage3_steady_film',
         'parent_native_iteration': 5080, 'parent_pair': source['pair'], 'work_root': str(WORK),
         'parent_film_time_s': clock['film_elapsed_time'], 'film_time_review_s': [.01, .05, .1, .2, .5],
         'max_segment_updates': 200000, 'segment_film_horizon_s': .5, 'blocks': [], 'control_trials': [],
         'controlled_delta': {}, 'verified_native_end': 5080, 'solver_left_open': True,
         'bulk_and_film_initialization': 'FORBIDDEN', 'steady_film': False}
    dump(MANIFEST, m)
    m['preserved_parent'] = save(s, 'preserved-parent-N5080')
    dump(OUT / 'parent-state.json', {'state': current, 'film': clock, 'pair': m['preserved_parent']})
    m['report_paths'] = instrument(s, WORK / 'monitors')
    s.settings.file.auto_save.data_frequency = 0
    controls(s, m, {'sub-iter-nums': 30})
    m.update(status='PREPARED_VERIFIED', prepared_reopen='PASS')
    dump(MANIFEST, m)
    print('N5080_PRESERVED_30_SUBITERATIONS_PREPARED', flush=True)


def collect(s, m, start, end, initial, final, fields, transcript):
    histories = {}
    for name, path in m['report_paths'].items():
        raw = read_text(s, path)
        (OUT / f'{name}.out').write_text(raw)
        h = history(raw)
        if not set(range(m.get('report_native_start', 5080) + 1, end + 1)).issubset(h):
            raise RuntimeError('Report coverage incomplete: ' + name)
        if not all(math.isfinite(v) for v in h.values()):
            raise RuntimeError('Nonfinite native report')
        histories[name] = h
    dump(OUT / 'report-histories.json', {k: {'iterations': sorted(h), 'values': [h[i] for i in sorted(h)], 'file': m['report_paths'][k]} for k, h in histories.items()})
    text = transcript.read_text()
    frozen = 'bulk-equations' in m['controlled_delta'] and not any(m['controlled_delta']['bulk-equations'].values())
    if frozen:
        printed = [list(map(float, f.groups())) for f in FILM.finditer(text)]
        if len(printed) != end - start or not math.isclose(printed[-1][0], final['film_elapsed_time'], abs_tol=5.1e-8):
            raise RuntimeError('Frozen-flow film clock count/endpoint differs')
        clocks, carrier, terminal = dict(zip(range(start + 1, end + 1), printed)), {}, 'Frozen-flow clocks mapped by exact count, native horizon and report rows'
    else:
        clocks, carrier, terminal = clocks_and_residuals(text, start, end, final['film_elapsed_time'])
    ewf, pending, last, film_index = {}, [], None, start
    for line in text.splitlines():
        match = SUB.search(line)
        if match:
            pending.append([int(match[1]), *map(float, match.groups()[1:])])
        if FILM.search(line):
            last, pending = pending, []
            if frozen:
                film_index += 1
                if last:
                    ewf[film_index] = last
                last = None
        match = ROW.match(line)
        if match and start < int(match[1]) <= end and last:
            ewf[int(match[1])], last = last, None
    if last and end not in ewf:
        ewf[end] = last
    alternate_no_inner = not ewf and m['controlled_delta'].get('implicit-scheme-new?', False)
    if set(ewf) != set(range(start + 1, end + 1)) and not alternate_no_inner:
        raise RuntimeError('Film inner residual coverage incomplete')
    for label, value in [('clocks', clocks), ('carrier', carrier), ('film-inner', ewf)]:
        dump(OUT / f'{label}-N{start}-N{end}.json', value)
    if final['max_timestep_count'] - initial['max_timestep_count'] != end - start:
        raise RuntimeError('Native film update count differs')
    integral, previous = 0., initial['film_elapsed_time']
    for i in range(start + 1, end + 1):
        dt = clocks[i][0] - previous
        if dt <= 0:
            raise RuntimeError('Film clock is not increasing')
        integral += dt * histories['p72a-e2.7-ewf-secondary-phase-mass-total'][i]
        previous = clocks[i][0]
    elapsed = final['film_elapsed_time'] - initial['film_elapsed_time']
    mass = histories['p72a-e2.7-ewf-film-mass-total'][end]
    gain = mass - fields['p72a-e2.7-ewf-film-mass-total'][0]
    drain = histories['p72a-e2.7-ewf-outflow-mass-total'][end] - fields['p72a-e2.7-ewf-outflow-mass-total'][0]
    bad = [i for i, rows in ewf.items() if max(rows[-1][1:]) > 1]
    passed = sum(max(rows[-1][1:]) <= 1e-5 for rows in ewf.values())
    met = {'native_start': start, 'native_end': end, 'updates': end - start,
           'film_time_s': final['film_elapsed_time'], 'added_film_time_s': elapsed,
           'final_accepted_step_s': final['film_timestep'], 'printed_step_min_s': min(v[1] for v in clocks.values()),
           'printed_step_max_s': max(v[1] for v in clocks.values()), 'peak_film_cfl': max(v[2] for v in clocks.values()),
           'film_mass_kg': mass, 'inventory_gain_kg': gain, 'accretion_kg_s': integral / elapsed,
           'drainage_kg_s': drain / elapsed, 'storage_kg_s': gain / elapsed,
           'drainage_deficit_percent': 100 * (integral - drain) / max(abs(integral), 1e-30),
           'film_ledger_error_percent': 100 * abs(gain + drain - integral) / max(abs(integral), 1e-30),
           'inner_pass_percent': 100 * passed / len(ewf) if ewf else None,
           'inner_above_1_count': len(bad) if ewf else None, 'inner_above_1_updates': bad,
           'inner_reporting': 'COMPLETE' if ewf else 'UNAVAILABLE_ALTERNATIVE_IMPLICIT',
           'inner_final_max_huv': [max(rows[-1][k] for rows in ewf.values()) for k in [1, 2, 3]] if ewf else None,
           'maximum_thickness_m': max(histories['p72a-e2.7-ewf-thickness-max'][i] for i in range(start + 1, end + 1)),
           'terminal_clock_mapping': terminal, 'carrier_residual_rows': len(carrier)}
    met['eligible_for_step_increase'] = bool(ewf) and met['inner_pass_percent'] >= 99 and not bad and met['film_ledger_error_percent'] <= .1
    met['within_recovery_bounds'] = met['peak_film_cfl'] <= 1 and met['maximum_thickness_m'] <= .003 and mass <= 12.3 and met['film_ledger_error_percent'] <= 1
    return met


def restore_half(s, m, changes=None, branch='half-step-recovery', frozen=False):
    """A distinct numerical contrast from exact preserved N5080 fields."""
    global OUT, WORK
    if native_iteration(s) != m['verified_native_end'] or not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Recovery requires preserved idle endpoint')
    old = {'pair': m['latest_pair'], 'metrics': m.get('latest_metrics'), 'output': str(OUT)}
    pair = m['preserved_parent']
    for kind in ['case', 'data']:
        digest = remote_file_sha256(s, pair[kind], str(WORK / 'scratch' / f'restore-{kind}.sha256'))
        if digest != pair[kind + '_sha256']:
            raise RuntimeError('Preserved recovery parent hash differs')
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    parent = json.loads((ROOT_OUT / 'parent-state.json').read_text())
    require_match(readback(s), parent['state']['readback'])
    if film(s) != parent['film'] or native_iteration(s) != 5080:
        raise RuntimeError('Restored parent film/native state differs')
    attempt = len(m.get('numerical_recoveries', [])) + 1
    OUT, WORK = ROOT_OUT / f'{branch}-{attempt}', ROOT_WORK / f'{branch}-{attempt}'
    OUT.mkdir(exist_ok=False)
    shutil.copyfile(ROOT_OUT / 'parent-state.json', OUT / 'parent-state.json')
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors']:
        ensure_remote_directory(s, str(folder))
    m['report_paths'] = instrument(s, WORK / 'monitors')
    m['controlled_delta'] = {}
    m['verified_native_end'] = 5080
    m['latest_pair'] = pair
    m['active_output'], m['active_work'] = str(OUT), str(WORK)
    step = 1e-6 / (2 ** attempt)
    changes = changes or {'ewf-adaptive?': False, 'timestep-max': step, 'sub-iter-nums': 30}
    m.setdefault('numerical_recoveries', []).append({'excluded_attempt': old, 'parent': pair, 'delta': changes})
    m.update(status='NUMERICAL_RECOVERY_PREPARING', active_target=None)
    dump(MANIFEST, m)
    if frozen:
        freeze(s, m, save_controls=False)
    controls(s, m, changes)
    m.update(status='PREPARED_VERIFIED', latest_metrics=None)
    dump(MANIFEST, m)


def freeze(s, m, save_controls=True):
    before = state(s)
    eq = s.settings.solution.controls.equations
    observed = eq.get_state()
    for name in observed:
        eq[name] = False
    expected = {name: False for name in observed}
    if eq.get_state() != expected:
        raise RuntimeError('Bulk equation freeze readback differs')
    m['controlled_delta']['bulk-equations'] = expected
    require_match({'fields': readback(s)['fields']}, {'fields': before['readback']['fields']})
    if save_controls:
        controls(s, m, {})


def film_fields(s, label):
    from ansys.fluent.core.fields.field_data_interfaces import ScalarFieldDataRequest, SurfaceFieldDataRequest, SurfaceDataType
    names = ['film-thickness', 'film-mass', 'film-x-velocity', 'film-y-velocity', 'film-z-velocity']
    metadata = s.fields._field_info._get_scalar_fields_info()
    if not set(names).issubset(metadata):
        raise RuntimeError('Native film field names unavailable')
    values = {}
    for name in names:
        result = s.fields.field_data.get_field_data(ScalarFieldDataRequest(surfaces=['wall'], field_name=name, node_value=False, boundary_value=True))
        values[name] = np.asarray(result['wall'], dtype=float).reshape(-1)
    geometry = s.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=['wall'], data_types=[SurfaceDataType.FacesCentroid]))
    values['centroids'] = np.asarray(geometry['wall'].face_centroids).reshape(-1, 3)
    if not all(len(v) == len(values['film-thickness']) for v in values.values()):
        raise RuntimeError('Film facet field/geometry lengths differ')
    if not all(np.isfinite(v).all() for v in values.values()) or np.min(values['film-thickness']) < 0:
        raise RuntimeError('Nonfinite or negative film field')
    target = OUT / f'{label}.npz'
    if target.exists():
        raise FileExistsError(target)
    np.savez_compressed(target, **values)
    dump(OUT / f'{label}.json', {'native_iteration': native_iteration(s), 'film': film(s),
                                'fields': {k: metadata[k] for k in names}, 'file': str(target),
                                'facet_count': len(values['film-thickness'])})
    return values, str(target)


def sensitivity(s, m):
    """Same exact fields/forcing; compare 0.5 and 5 µs at 0.5 ms added film time."""
    arms = {}
    for label, dt, steps in [('conservative', .5e-6, 1000), ('candidate', 5e-6, 100)]:
        restore_half(s, m, {'ewf-adaptive?': False, 'timestep-max': dt, 'sub-iter-nums': 30,
                            'implicit-scheme-new?': True}, 'matched-time-' + label)
        freeze(s, m)
        met = block(s, m, steps)
        arrays, path = film_fields(s, 'matched-film-fields')
        arms[label] = {'metrics': met, 'fields': path, 'pair': m['latest_pair']}
        m['sensitivity_arms'] = arms
        dump(MANIFEST, m)
    a, b = [np.load(arms[label]['fields']) for label in ['conservative', 'candidate']]
    if not np.allclose(a['centroids'], b['centroids'], atol=1e-12, rtol=0):
        raise RuntimeError('Surface facet coordinates/order differ')
    if not math.isclose(arms['conservative']['metrics']['film_time_s'], arms['candidate']['metrics']['film_time_s'], abs_tol=1e-12):
        raise RuntimeError('Sensitivity film times differ')
    mass = a['film-mass']
    av = np.stack([a[f'film-{axis}-velocity'] for axis in ['x', 'y', 'z']], axis=1)
    bv = np.stack([b[f'film-{axis}-velocity'] for axis in ['x', 'y', 'z']], axis=1)
    q = {'mass_distribution_L1_percent': 100 * np.sum(np.abs(b['film-mass'] - mass)) / np.sum(mass),
         'mass_weighted_velocity_difference_percent': 100 * np.sum(mass * np.linalg.norm(bv - av, axis=1)) / max(np.sum(mass * np.linalg.norm(av, axis=1)), 1e-30),
         'maximum_thickness_difference_percent': 100 * abs(np.max(b['film-thickness']) - np.max(a['film-thickness'])) / np.max(a['film-thickness']),
         'film_time_s': arms['candidate']['metrics']['film_time_s'], 'qualified_fixed_step_s': 5e-6,
         'reference_step_s': .5e-6, 'equations': 'FROZEN_IDENTICAL_N5080_BULK_FIELDS',
         'inner_residuals': 'UNAVAILABLE_NOT_COUNTED_AS_PASS'}
    q['pass'] = bool(q['mass_distribution_L1_percent'] <= 1 and q['mass_weighted_velocity_difference_percent'] <= 2 and q['maximum_thickness_difference_percent'] <= 2 and all(x['metrics']['film_ledger_error_percent'] <= .1 and x['metrics']['within_recovery_bounds'] for x in arms.values()))
    m['alternative_sensitivity'] = q
    m.update(status='MATCHED_TIME_SENSITIVITY_PASS' if q['pass'] else 'MATCHED_TIME_SENSITIVITY_RECOVERY_REQUIRED', active_target=None)
    dump(ROOT_OUT / 'matched-time-sensitivity.json', {'comparison': q, 'arms': arms})
    dump(MANIFEST, m)
    print('MATCHED_TIME_SENSITIVITY', json.dumps(q), flush=True)


def grow_sensitivity(s, m, step_us=10, resume=False):
    """Re-use the preserved 0.5 µs reference for a larger matched-time contrast."""
    if not m.get('alternative_sensitivity', {}).get('pass'):
        raise RuntimeError('The 5 µs screen must pass first')
    previous = dict(m['alternative_sensitivity'])
    step = step_us / 1e6
    changes = {'ewf-adaptive?': False, 'timestep-max': step, 'sub-iter-nums': 30, 'implicit-scheme-new?': True}
    if resume:
        parent = json.loads((ROOT_OUT / 'parent-state.json').read_text())
        if native_iteration(s) != 5080 or not math.isclose(film(s)['film_elapsed_time'], parent['film']['film_elapsed_time'], abs_tol=1e-15):
            raise RuntimeError('Resume only the unsolved exact-parent preparation')
        require_match({'fields': readback(s)['fields']}, {'fields': parent['state']['readback']['fields']})
        eq = s.settings.solution.controls.equations.get_state()
        if any(eq.values()):
            raise RuntimeError('Matched-time bulk equations must remain frozen')
        m['controlled_delta'] = {'bulk-equations': eq}
        m.setdefault('implementation_repairs', []).append({'error': m.pop('error', None), 'repair': 'Float control readback tolerance; native N5080 and parent fields verified; zero repeated solve'})
        controls(s, m, changes)
    else:
        restore_half(s, m, changes, f'matched-time-{step_us}us', frozen=True)
    met = block(s, m, round(500 / step_us))
    arrays, path = film_fields(s, 'matched-film-fields')
    reference = m['sensitivity_arms']['conservative']
    a = np.load(reference['fields'])
    if not np.allclose(a['centroids'], arrays['centroids'], atol=1e-12, rtol=0):
        raise RuntimeError('Sensitivity geometry/order differs')
    if not math.isclose(reference['metrics']['film_time_s'], met['film_time_s'], abs_tol=1e-12):
        raise RuntimeError('Sensitivity clocks differ')
    mass = a['film-mass']
    av = np.stack([a[f'film-{x}-velocity'] for x in ['x', 'y', 'z']], axis=1)
    bv = np.stack([arrays[f'film-{x}-velocity'] for x in ['x', 'y', 'z']], axis=1)
    q = {'mass_distribution_L1_percent': float(100 * np.sum(np.abs(arrays['film-mass'] - mass)) / np.sum(mass)),
         'mass_weighted_velocity_difference_percent': float(100 * np.sum(mass * np.linalg.norm(bv - av, axis=1)) / max(np.sum(mass * np.linalg.norm(av, axis=1)), 1e-30)),
         'maximum_thickness_difference_percent': float(100 * abs(np.max(arrays['film-thickness']) - np.max(a['film-thickness'])) / np.max(a['film-thickness'])),
         'film_time_s': met['film_time_s'], 'qualified_fixed_step_s': step, 'reference_step_s': .5e-6,
         'equations': 'FROZEN_IDENTICAL_N5080_BULK_FIELDS', 'inner_residuals': 'UNAVAILABLE_NOT_COUNTED_AS_PASS'}
    q['pass'] = q['mass_distribution_L1_percent'] <= 1 and q['mass_weighted_velocity_difference_percent'] <= 2 and q['maximum_thickness_difference_percent'] <= 2 and met['film_ledger_error_percent'] <= .1 and met['within_recovery_bounds']
    m.setdefault('sensitivity_comparisons', []).extend([previous, q])
    m['sensitivity_arms'][f'candidate_{step_us}us'] = {'metrics': met, 'fields': path, 'pair': m['latest_pair']}
    if q['pass']:
        m['alternative_sensitivity'] = q
    m.update(status='MATCHED_TIME_SENSITIVITY_PASS' if q['pass'] else 'MATCHED_TIME_SENSITIVITY_RECOVERY_REQUIRED', active_target=None)
    dump(ROOT_OUT / f'matched-time-sensitivity-{step_us}us.json', {'comparison': q, 'arms': m['sensitivity_arms']})
    dump(MANIFEST, m)
    print(f'MATCHED_TIME_SENSITIVITY_{step_us}US', json.dumps(q), flush=True)


def reconcile_sensitivity():
    """Repair numeric serialization from immutable facet arrays, with zero solve."""
    m = json.loads(MANIFEST.read_text())
    arms = m['sensitivity_arms']
    a, b = [{k: v.astype(float) for k, v in np.load(arms[label]['fields']).items()} for label in ['conservative', 'candidate']]
    if not np.allclose(a['centroids'], b['centroids'], atol=1e-12, rtol=0):
        raise RuntimeError('Surface facet coordinates/order differ')
    if not math.isclose(arms['conservative']['metrics']['film_time_s'], arms['candidate']['metrics']['film_time_s'], abs_tol=1e-12):
        raise RuntimeError('Sensitivity film times differ')
    mass = a['film-mass']
    av = np.stack([a[f'film-{x}-velocity'] for x in ['x', 'y', 'z']], axis=1)
    bv = np.stack([b[f'film-{x}-velocity'] for x in ['x', 'y', 'z']], axis=1)
    q = {'mass_distribution_L1_percent': float(100 * np.sum(np.abs(b['film-mass'] - mass)) / np.sum(mass)),
         'mass_weighted_velocity_difference_percent': float(100 * np.sum(mass * np.linalg.norm(bv - av, axis=1)) / max(np.sum(mass * np.linalg.norm(av, axis=1)), 1e-30)),
         'maximum_thickness_difference_percent': float(100 * abs(np.max(b['film-thickness']) - np.max(a['film-thickness'])) / np.max(a['film-thickness'])),
         'film_time_s': arms['candidate']['metrics']['film_time_s'], 'qualified_fixed_step_s': 5e-6, 'reference_step_s': .5e-6,
         'equations': 'FROZEN_IDENTICAL_N5080_BULK_FIELDS', 'inner_residuals': 'UNAVAILABLE_NOT_COUNTED_AS_PASS',
         'serialization_repair': 'Original native facet payloads recomputed in float64; no new solve; native single precision preserved in source NPZ'}
    q['pass'] = bool(q['mass_distribution_L1_percent'] <= 1 and q['mass_weighted_velocity_difference_percent'] <= 2 and q['maximum_thickness_difference_percent'] <= 2 and all(x['metrics']['film_ledger_error_percent'] <= .1 and x['metrics']['within_recovery_bounds'] for x in arms.values()))
    m.update(alternative_sensitivity=q, status='MATCHED_TIME_SENSITIVITY_PASS' if q['pass'] else 'MATCHED_TIME_SENSITIVITY_RECOVERY_REQUIRED', active_target=None)
    dump(ROOT_OUT / 'matched-time-sensitivity.json', {'comparison': q, 'arms': arms})
    dump(MANIFEST, m)
    print('MATCHED_TIME_SENSITIVITY_RECONCILED_NO_SOLVE', json.dumps(q), flush=True)


def develop_alternative(s, m):
    """Advance the best screened solver/step; frozen-film screen is provisional."""
    global OUT, WORK
    q = m.get('alternative_sensitivity', {})
    if not q.get('pass'):
        raise RuntimeError('Matched-time field/ledger screen required')
    qualified_step = q['qualified_fixed_step_s']
    candidates = [arm for arm in m['sensitivity_arms'].values() if math.isclose(arm['metrics']['printed_step_max_s'], qualified_step, rel_tol=1e-8)]
    chosen = candidates[-1]
    pair = chosen['pair']
    if not s.settings.solution.run_calculation.iterate.is_active() or native_iteration(s) != m['verified_native_end']:
        raise RuntimeError('Reconcile idle endpoint before continuation')
    for kind in ['case', 'data']:
        if remote_file_sha256(s, pair[kind], str(WORK / 'scratch' / f'development-{kind}.sha256')) != pair[kind + '_sha256']:
            raise RuntimeError('Screened parent hash differs')
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    expected = json.loads((Path(chosen['fields']).parent / f"endpoint-N{pair['native_iteration']}.json").read_text())
    require_match(readback(s), expected['state']['readback'])
    if film(s) != expected['film']:
        raise RuntimeError('Screened parent film state differs')
    OUT, WORK = ROOT_OUT / 'adaptive-development', ROOT_WORK / 'adaptive-development'
    OUT.mkdir(exist_ok=False)
    shutil.copyfile(ROOT_OUT / 'parent-state.json', OUT / 'parent-state.json')
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors']:
        ensure_remote_directory(s, str(folder))
    m['report_paths'] = instrument(s, WORK / 'monitors')
    m.update(active_output=str(OUT), active_work=str(WORK), report_native_start=pair['native_iteration'],
             verified_native_end=pair['native_iteration'], latest_pair=pair, development_parent=pair,
             controlled_delta=dict(chosen['metrics']['controls']), status='ADAPTIVE_DEVELOPMENT_PREPARING')
    dump(MANIFEST, m)
    target = min(.5, max(.1, chosen['metrics']['peak_film_cfl'] * 1.3))
    controls(s, m, {'ewf-adaptive?': True, 'courant-number': target, 'adapt-init-dt': qualified_step,
                     'adapt-tstp-inc': 1.3, 'adapt-tstp-dec': 2.0})
    relax_alternative(s, m, qualified_step)


def relax_alternative(s, m, qualified_step, start_probe=True):
    """Continue the current prepared frozen branch with the same stop checks."""
    for index in range(201):
        remaining = m['max_segment_updates'] - (m['verified_native_end'] - m['parent_native_iteration'])
        if remaining <= 0:
            m.update(status='UPDATE_BUDGET_REVIEW_REQUIRED', active_target=None)
            dump(MANIFEST, m)
            return
        previous_pair = dict(m['latest_pair'])
        met = block(s, m, min(100 if index == 0 and start_probe else 1000, remaining))
        arrays, path = film_fields(s, f"film-fields-N{met['native_end']}")
        native_mass = float(np.sum(arrays['film-mass'], dtype=float))
        if not math.isclose(native_mass, met['film_mass_kg'], rel_tol=2e-6, abs_tol=1e-9):
            raise RuntimeError('Native facet mass sum/report differs')
        met.update(facet_fields=path, field_coverage='FINITE_NONNEGATIVE_THICKNESS', initial_pair=previous_pair,
                   numerical_qualification='EARLY_MATCHED_TIME_SCREEN_ONLY_INNER_RESIDUALS_UNAVAILABLE')
        adequate = met['within_recovery_bounds'] and met['film_ledger_error_percent'] <= .1
        larger = met['printed_step_max_s'] > qualified_step * (1 + 1e-6)
        if not adequate or larger:
            m.update(status='NEXT_STEP_SENSITIVITY_REQUIRED' if adequate else 'NUMERICAL_RECOVERY_REQUIRED',
                     numerical_recovery_parent=previous_pair, active_target=None,
                     reason='Actual step exceeded screened range' if adequate else 'Native field/ledger recovery bound failed')
            dump(MANIFEST, m)
            return
        m['last_numerically_adequate_pair'] = m['latest_pair']
        tail = [b for b in m['blocks'] if b.get('output') == str(OUT)][-3:]
        steady = len(tail) == 3 and all(b['updates'] == 1000 and b.get('field_coverage') in ['FINITE_POSITIVE', 'FINITE_NONNEGATIVE_THICKNESS']
                   and abs(b['drainage_deficit_percent']) <= 1
                   and abs(b['storage_kg_s']) / max(abs(b['accretion_kg_s']), 1e-30) <= .01
                   and b['film_ledger_error_percent'] <= .1 for b in tail)
        if steady or met['film_time_s'] >= m['segment_film_horizon_s']:
            m.update(status='FROZEN_FILM_STATIONARITY_SCREEN' if steady else 'FILM_HORIZON_REVIEW_REQUIRED',
                     frozen_film_stationarity_screen=steady, steady_film=False,
                     full_bulk_restore_and_developed_step_check='REQUIRED', active_target=None)
            dump(MANIFEST, m)
            return
        dump(MANIFEST, m)


def recover_adaptive(s, m):
    """Preserve rejected horizon; repeat from the last passing pair at lower CFL."""
    pair = m['numerical_recovery_parent']
    source = {'pair': pair, 'endpoint': str(OUT / f"endpoint-N{pair['native_iteration']}.json")}
    rejected_metrics = next((b for b in reversed(m['blocks']) if not b['within_recovery_bounds']), m['latest_metrics'])
    rejected = {'pair': dict(rejected_metrics['pair']), 'metrics': dict(rejected_metrics),
                'reason': m.get('reason')}
    name = f"adaptive-recovery-from-N{pair['native_iteration']}"
    restore_branch(s, m, source, name)
    m.setdefault('adaptive_recoveries', []).append({'rejected': rejected, 'restart': source,
                 'fixed_probe_step_s': 5e-6, 'adaptive_courant': .2, 'growth': 1.15, 'reduction': 2})
    controls(s, m, {'ewf-adaptive?': False, 'timestep-max': 5e-6})
    met = block(s, m, 100)
    arrays, path = film_fields(s, f"film-fields-N{met['native_end']}")
    met.update(facet_fields=path, field_coverage='FINITE_NONNEGATIVE_THICKNESS')
    if not met['within_recovery_bounds'] or met['film_ledger_error_percent'] > .1:
        m.update(status='NUMERICAL_RECOVERY_REQUIRED', active_target=None,
                 numerical_recovery_parent=pair, reason='Smaller fixed-step restart failed')
        dump(MANIFEST, m)
        return
    controls(s, m, {'ewf-adaptive?': True, 'courant-number': .2, 'adapt-init-dt': 5e-6,
                    'adapt-tstp-inc': 1.15, 'adapt-tstp-dec': 2})
    relax_alternative(s, m, m['alternative_sensitivity']['qualified_fixed_step_s'])


def block(s, m, steps):
    start = native_iteration(s)
    if start != m['verified_native_end'] or not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Reconcile live state before submitting a batch')
    original = json.loads((OUT / 'parent-state.json').read_text())['state']
    before = state(s)
    invariant(before, original, m['controlled_delta'])
    initial = film(s)
    end = start + steps
    tag = f'batch-N{start}-N{end}'
    path = OUT / f'{tag}.txt'
    remote = str(WORK / f'{tag}.trn').replace('\\', '/')
    if path.exists():
        raise RuntimeError('Existing batch transcript; refusing duplicate compute')
    s.transcript.start(file_name=str(path), write_to_stdout=False)
    s.scheme.eval(f'(ti-menu-load-string "/file/start-transcript \\\"{remote}\\\"")')
    m.update(status='RUNNING', active_target=end, command=f'/solve/iterate {steps}')
    dump(MANIFEST, m)
    print('SUBMIT', start, end, flush=True)
    begun = time.monotonic()
    iterate(s, steps)
    current = state(s)
    invariant(current, original, m['controlled_delta'])
    pair = save(s, f'checkpoint-N{end}')
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(readback(s), current['readback'])
    final = film(s)
    # Preserve a completed horizon before analysis. A parser failure must never
    # make a saved, reopened calculation look like an unsolved batch.
    dump(OUT / f'completed-N{end}.json', {'pair': pair, 'state': state(s), 'film': final,
         'initial_film': initial, 'initial_fields': before['readback']['fields'],
         'native_start': start, 'native_end': end, 'reopen': 'PASS',
         'controls': dict(m['controlled_delta']), 'analysis': 'PENDING'})
    s.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
    time.sleep(.5)
    s.transcript.stop()
    native = OUT / f'{tag}.trn'
    native.write_text(read_text(s, str(WORK / f'{tag}.trn')))
    met = collect(s, m, start, end, initial, final, before['readback']['fields'], native)
    met['wall_seconds'] = time.monotonic() - begun
    met['film_ms_per_wall_minute'] = met['added_film_time_s'] * 1000 / (met['wall_seconds'] / 60)
    met['output'] = str(OUT)
    met['controls'] = dict(m['controlled_delta'])
    met['pair'] = pair
    dump(OUT / f'endpoint-N{end}.json', {'pair': pair, 'state': state(s), 'film': final, 'metrics': met, 'reopen': 'PASS'})
    m['blocks'].append(met)
    m.update(status='BLOCK_COMPLETE', verified_native_end=end, latest_pair=pair, latest_metrics=met, final_reopen='PASS')
    dump(MANIFEST, m)
    print('BLOCK_COMPLETE', json.dumps(met), flush=True)
    return met


def reconcile_timeout(s, m):
    """Recover a completed native batch after client loss, with zero solve calls."""
    if m['status'] != 'RECOVERY_REQUIRED' or 'Stream removed' not in m.get('error', ''):
        raise RuntimeError('Expected a preserved client-stream error')
    start, end = m['verified_native_end'], m['active_target']
    if native_iteration(s) != end:
        raise RuntimeError('Native horizon differs; observe active/partial state before recovery')
    run = s.settings.solution.run_calculation
    if not run.iterate.is_active() and run.interrupt.is_active():
        run.interrupt()
    if not run.iterate.is_active() or native_iteration(s) != end:
        raise RuntimeError('Completed idle horizon required')
    initial = json.loads((OUT / f'endpoint-N{start}.json').read_text())
    original = json.loads((OUT / 'parent-state.json').read_text())['state']
    current = state(s)
    invariant(current, original, m['controlled_delta'])
    pair = save(s, f'checkpoint-N{end}')
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(readback(s), current['readback'])
    final = film(s)
    dump(OUT / f'completed-N{end}.json', {'pair': pair, 'state': state(s), 'film': final,
         'initial_film': initial['film'], 'initial_fields': initial['state']['readback']['fields'],
         'native_start': start, 'native_end': end, 'reopen': 'PASS',
         'controls': dict(m['controlled_delta']), 'analysis': 'PENDING', 'new_solve_calls': 0})
    s.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
    native = OUT / f'batch-N{start}-N{end}.trn'
    if native.exists():
        raise FileExistsError('Do not overwrite native transcript evidence: ' + str(native))
    native.write_text(read_text(s, str(WORK / native.name)))
    met = collect(s, m, start, end, initial['film'], final, initial['state']['readback']['fields'], native)
    met.update(output=str(OUT), controls=dict(m['controlled_delta']), pair=pair,
               wall_seconds=None, film_ms_per_wall_minute=None, execution_repeated=False,
               communication_recovery='NATIVE_BATCH_COMPLETE_CLIENT_STREAM_LOST')
    arrays, path = film_fields(s, f'film-fields-N{end}')
    if not math.isclose(float(np.sum(arrays['film-mass'], dtype=float)), met['film_mass_kg'], rel_tol=2e-6, abs_tol=1e-9):
        raise RuntimeError('Reconciled facet mass/report differs')
    met.update(facet_fields=path, field_coverage='FINITE_NONNEGATIVE_THICKNESS', initial_pair=initial['pair'],
               numerical_qualification='EARLY_MATCHED_TIME_SCREEN_ONLY_INNER_RESIDUALS_UNAVAILABLE')
    dump(OUT / f'endpoint-N{end}.json', {'pair': pair, 'state': state(s), 'film': final, 'metrics': met, 'reopen': 'PASS'})
    m.setdefault('communication_recoveries', []).append({'error': m.pop('error'), 'native_start': start,
         'native_end': end, 'new_solve_calls': 0, 'native_records_recovered': end-start, 'pair': pair})
    m['blocks'].append(met)
    adequate = met['within_recovery_bounds'] and met['film_ledger_error_percent'] <= .1
    m.update(status='RECONCILED_CONNECTION_TIMEOUT' if adequate else 'NUMERICAL_RECOVERY_REQUIRED',
             verified_native_end=end, latest_pair=pair, latest_metrics=met, active_target=None,
             final_reopen='PASS', idle=True, reason='Completed native batch recovered after client timeout; no repeated solve')
    if adequate:
        m['last_numerically_adequate_pair'] = pair
    dump(MANIFEST, m)
    print('RECONCILED_TIMEOUT_NO_REPEAT_SOLVE', json.dumps(met), flush=True)


def restore_branch(s, m, source, name):
    """Restore a verified developed pair, with unchanged fields and no solve."""
    global OUT, WORK
    if not s.settings.solution.run_calculation.iterate.is_active() or native_iteration(s) != m['verified_native_end']:
        raise RuntimeError('Verified idle endpoint required before branch restore')
    endpoint = json.loads(Path(source['endpoint']).read_text())
    pair = source['pair']
    for kind in ['case', 'data']:
        digest = remote_file_sha256(s, pair[kind], str(WORK / 'scratch' / f'branch-{kind}-{uuid.uuid4().hex}.sha256'))
        if digest != pair[kind + '_sha256']:
            raise RuntimeError('Developed source hash differs')
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(readback(s), endpoint['state']['readback'])
    if film(s) != endpoint['film'] or native_iteration(s) != pair['native_iteration']:
        raise RuntimeError('Developed source film/native state differs')
    OUT, WORK = ROOT_OUT / name, ROOT_WORK / name
    OUT.mkdir(exist_ok=False)
    shutil.copyfile(ROOT_OUT / 'parent-state.json', OUT / 'parent-state.json')
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors']:
        ensure_remote_directory(s, str(folder))
    m['report_paths'] = instrument(s, WORK / 'monitors')
    m.update(active_output=str(OUT), active_work=str(WORK), report_native_start=pair['native_iteration'],
             verified_native_end=pair['native_iteration'], latest_pair=pair,
             controlled_delta=dict(endpoint['metrics']['controls']), active_target=None,
             status='DEVELOPED_BRANCH_PREPARING')
    dump(MANIFEST, m)


def developed_sensitivity(s, m):
    """Fivefold step contrast at the same developed state and film-time horizon."""
    if not m.get('frozen_film_stationarity_screen'):
        raise RuntimeError('Frozen-film stationary screen required first')
    source = m.get('developed_sensitivity_source')
    if source is None:
        source = {'pair': dict(m['latest_pair']),
                  'endpoint': str(OUT / f"endpoint-N{m['verified_native_end']}.json"),
                  'candidate_step_s': m['latest_metrics']['final_accepted_step_s']}
        m['developed_sensitivity_source'] = source
        dump(MANIFEST, m)
    candidate = source['candidate_step_s']
    arms = {}
    for label, dt, steps in [('reference', candidate / 5, 1000), ('candidate', candidate, 200)]:
        restore_branch(s, m, source, f'developed-step-{label}')
        controls(s, m, {'ewf-adaptive?': False, 'timestep-max': dt})
        met = block(s, m, steps)
        arrays, path = film_fields(s, 'matched-developed-fields')
        arms[label] = {'metrics': met, 'fields': path, 'pair': dict(m['latest_pair']),
                       'endpoint': str(OUT / f"endpoint-N{met['native_end']}.json")}
        m['developed_sensitivity_arms'] = arms
        dump(MANIFEST, m)
    a, b = [np.load(arms[label]['fields']) for label in ['reference', 'candidate']]
    if not np.allclose(a['centroids'], b['centroids'], atol=1e-12, rtol=0):
        raise RuntimeError('Developed sensitivity facet order differs')
    if not math.isclose(arms['reference']['metrics']['film_time_s'], arms['candidate']['metrics']['film_time_s'], abs_tol=1e-12):
        raise RuntimeError('Developed sensitivity time horizons differ')
    mass = a['film-mass']
    av = np.stack([a[f'film-{x}-velocity'] for x in ['x', 'y', 'z']], axis=1)
    bv = np.stack([b[f'film-{x}-velocity'] for x in ['x', 'y', 'z']], axis=1)
    ref, cand = [arms[x]['metrics'] for x in ['reference', 'candidate']]
    q = {'reference_step_s': candidate / 5, 'candidate_step_s': candidate,
         'film_time_s': cand['film_time_s'], 'added_film_time_s': cand['added_film_time_s'],
         'mass_distribution_L1_percent': float(100 * np.sum(np.abs(b['film-mass'] - mass)) / np.sum(mass)),
         'mass_weighted_velocity_difference_percent': float(100 * np.sum(mass * np.linalg.norm(bv - av, axis=1)) / max(np.sum(mass * np.linalg.norm(av, axis=1)), 1e-30)),
         'maximum_thickness_difference_percent': float(100 * abs(np.max(b['film-thickness']) - np.max(a['film-thickness'])) / np.max(a['film-thickness'])),
         'drainage_difference_over_accretion_percent': float(100 * abs(cand['drainage_kg_s'] - ref['drainage_kg_s']) / max(abs(ref['accretion_kg_s']), 1e-30)),
         'equations': 'FROZEN_IDENTICAL_DEVELOPED_BULK_FIELDS', 'inner_residuals': 'UNAVAILABLE_NOT_COUNTED_AS_PASS'}
    q['pass'] = bool(q['mass_distribution_L1_percent'] <= 1 and q['mass_weighted_velocity_difference_percent'] <= 2
                   and q['maximum_thickness_difference_percent'] <= 2 and q['drainage_difference_over_accretion_percent'] <= 1
                   and all(x['metrics']['film_ledger_error_percent'] <= .1 and x['metrics']['within_recovery_bounds'] for x in arms.values()))
    m.update(developed_sensitivity=q, status='DEVELOPED_STEP_SCREEN_PASS' if q['pass'] else 'DEVELOPED_STEP_RECOVERY_REQUIRED', active_target=None)
    dump(ROOT_OUT / 'developed-step-sensitivity.json', {'comparison': q, 'source': source, 'arms': arms})
    dump(MANIFEST, m)
    print('DEVELOPED_STEP_SENSITIVITY', json.dumps(q), flush=True)


def full_bulk_development(s, m):
    """Restore the parent bulk equations and qualify sustained film stationarity."""
    q = m.get('developed_sensitivity', {})
    if not q.get('pass'):
        raise RuntimeError('Developed film step comparison must pass first')
    if OUT.name != 'full-bulk-development':
        source = m['developed_sensitivity_arms']['candidate']
        restore_branch(s, m, source, 'full-bulk-development')
        before = state(s)
        clock_before = film(s)
        original = json.loads((ROOT_OUT / 'parent-state.json').read_text())['state']
        expected = original['readback']['controls']['equations']
        eq = s.settings.solution.controls.equations
        for name, value in expected.items():
            eq[name] = value
        if eq.get_state() != expected:
            raise RuntimeError('Original bulk equation restoration differs')
        m['controlled_delta'].pop('bulk-equations', None)
        require_match({'fields': readback(s)['fields']}, {'fields': before['readback']['fields']})
        if film(s) != clock_before:
            raise RuntimeError('Equation restoration changed the film clock')
        controls(s, m, {'ewf-adaptive?': True, 'courant-number': .5,
                        'adapt-init-dt': q['candidate_step_s'], 'adapt-tstp-inc': 1.3, 'adapt-tstp-dec': 2.0})
        m['bulk_equations_restored'] = expected
        m['full_bulk_start_film_time_s'] = film(s)['film_elapsed_time']
        dump(MANIFEST, m)
    for index in range(201):
        previous_pair = dict(m['latest_pair'])
        met = block(s, m, 100 if index == 0 else 1000)
        arrays, path = film_fields(s, f"film-fields-N{met['native_end']}")
        if not math.isclose(float(np.sum(arrays['film-mass'], dtype=float)), met['film_mass_kg'], rel_tol=2e-6, abs_tol=1e-9):
            raise RuntimeError('Full bulk facet mass/report differs')
        met.update(facet_fields=path, field_coverage='FINITE_NONNEGATIVE_THICKNESS', initial_pair=previous_pair,
                   numerical_qualification='DEVELOPED_MATCHED_TIME_SCREEN_INNER_RESIDUALS_UNAVAILABLE')
        adequate = met['within_recovery_bounds'] and met['film_ledger_error_percent'] <= .1
        # Adaptive reduction is accepted; growth beyond the developed-state
        # tested step requires another comparison, irrespective of timestep-max.
        larger = met['printed_step_max_s'] > q['candidate_step_s'] * (1 + 1e-6)
        if not adequate or larger:
            m.update(status='FULL_BULK_STEP_SENSITIVITY_REQUIRED' if adequate else 'FULL_BULK_NUMERICAL_RECOVERY_REQUIRED',
                     numerical_recovery_parent=previous_pair, active_target=None,
                     reason='Actual step exceeded developed screen' if adequate else 'Full bulk field/ledger bounds failed')
            dump(MANIFEST, m)
            return
        tail = [b for b in m['blocks'] if b.get('output') == str(OUT)][-3:]
        steady = len(tail) == 3 and all(b['updates'] == 1000 and b.get('field_coverage') == 'FINITE_NONNEGATIVE_THICKNESS'
                   and abs(b['drainage_deficit_percent']) <= 1
                   and abs(b['storage_kg_s']) / max(abs(b['accretion_kg_s']), 1e-30) <= .01
                   and b['film_ledger_error_percent'] <= .1 for b in tail)
        if steady or met['film_time_s'] - m['full_bulk_start_film_time_s'] >= .1:
            m.update(status='FULL_BULK_FILM_STATIONARITY_SCREEN' if steady else 'FULL_BULK_HORIZON_REVIEW_REQUIRED',
                     full_bulk_film_stationarity_screen=steady, steady_film=False,
                     final_history_review='REQUIRED_BEFORE_STEADY_CLAIM', active_target=None)
            dump(MANIFEST, m)
            return
        dump(MANIFEST, m)


def develop(s, m):
    """Qualify adaptive targets, then continue while checking each saved batch."""
    targets = [.05, .075, .10, .15, .20]
    current = state(s)['film_model']
    if not m.get('latest_metrics') or not m['latest_metrics']['eligible_for_step_increase']:
        raise RuntimeError('Repair and qualify the fixed-step film solver first')
    if not current['ewf-adaptive?']:
        controls(s, m, {'ewf-adaptive?': True, 'courant-number': .05, 'adapt-init-dt': 1e-6,
                         'adapt-tstp-inc': 1.3, 'adapt-tstp-dec': 2.0})
        met = block(s, m, 100)
        if not met['eligible_for_step_increase']:
            m.update(status='NUMERICAL_RECOVERY_REQUIRED', reason='First adaptive probe failed inner/ledger criteria')
            dump(MANIFEST, m)
            return
    for unused in range(200):
        remaining = m['max_segment_updates'] - (m['verified_native_end'] - m['parent_native_iteration'])
        if remaining <= 0:
            break
        before_pair = dict(m['latest_pair'])
        met = block(s, m, min(1000, remaining))
        met['initial_pair'] = before_pair
        dump(MANIFEST, m)
        if not met['eligible_for_step_increase'] or not met['within_recovery_bounds']:
            m.update(status='NUMERICAL_RECOVERY_REQUIRED', reason='Long window fails numerical/ledger criteria',
                     numerical_recovery_parent=before_pair, active_target=None)
            dump(MANIFEST, m)
            return
        m['last_numerically_adequate_pair'] = m['latest_pair']
        tail = [b for b in m['blocks'] if b.get('output', str(ROOT_OUT)) == str(OUT)][-3:]
        stationary = len(tail) == 3 and all(b['updates'] == 1000 and b['eligible_for_step_increase']
                        and abs(b['drainage_deficit_percent']) <= 1
                        and abs(b['storage_kg_s']) / max(abs(b['accretion_kg_s']), 1e-30) <= .01 for b in tail)
        if stationary or met['film_time_s'] >= m['segment_film_horizon_s']:
            m.update(status='STATIONARY_SCREEN_COMPLETE' if stationary else 'FILM_HORIZON_REVIEW_REQUIRED',
                     steady_film=stationary, active_target=None, idle=True)
            dump(MANIFEST, m)
            return
        target = state(s)['film_model']['courant-number']
        nxt = next((v for v in targets if v > target + 1e-10), None)
        if nxt:
            controls(s, m, {'courant-number': nxt})
            met = block(s, m, 100)
            if not met['eligible_for_step_increase'] or not met['within_recovery_bounds']:
                m.update(status='NUMERICAL_RECOVERY_REQUIRED', reason='Higher target probe failed criteria',
                         numerical_recovery_parent=m['last_numerically_adequate_pair'], active_target=None)
                dump(MANIFEST, m)
                return
    m.update(status='UPDATE_BUDGET_REVIEW_REQUIRED', active_target=None)
    dump(MANIFEST, m)


def main():
    global OUT, WORK
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'probe', 'adaptive-probe', 'batch', 'repair-half', 'repair-segregated', 'repair-implicit', 'develop', 'reconcile-alternative', 'probe-relative', 'probe-frozen', 'sensitivity', 'grow-sensitivity', 'resume-grow-sensitivity', 'reconcile-sensitivity', 'develop-alternative', 'recover-adaptive', 'developed-sensitivity', 'full-bulk-development', 'reconcile-timeout', 'continue-alternative'])
    parser.add_argument('--candidate-step-us', type=int, choices=[10, 20, 50], default=10)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.operation == 'reconcile-sensitivity':
        reconcile_sensitivity()
        return
    s = attach()
    try:
        if args.operation == 'prepare':
            prepare(s)
            return
        m = json.loads(MANIFEST.read_text())
        OUT, WORK = Path(m.get('active_output', str(ROOT_OUT))), PureWindowsPath(m.get('active_work', str(ROOT_WORK)))
        if args.operation == 'reconcile-timeout':
            reconcile_timeout(s, m)
            return
        if args.operation == 'continue-alternative':
            if m['status'] not in ['RECONCILED_CONNECTION_TIMEOUT', 'BLOCK_COMPLETE']:
                raise RuntimeError('Preserved, reconciled endpoint required before continuation')
            relax_alternative(s, m, m['alternative_sensitivity']['qualified_fixed_step_s'], start_probe=False)
            return
        if args.operation == 'reconcile-alternative':
            end, start = m['active_target'], m['verified_native_end']
            if native_iteration(s) != end or not s.settings.solution.run_calculation.iterate.is_active():
                raise RuntimeError('Completed idle horizon required; do not repeat solve')
            pair = {'case': str(WORK / f'checkpoint-N{end}.cas.h5'),
                    'data': str(WORK / f'checkpoint-N{end}.dat.h5'), 'native_iteration': end}
            for kind in ['case', 'data']:
                pair[kind + '_sha256'] = remote_file_sha256(s, pair[kind], str(WORK / 'scratch' / f'reconcile-{kind}.sha256'))
            current = state(s)
            s.settings.file.read_case(file_name=pair['case'])
            s.settings.file.read_data(file_name=pair['data'])
            require_match(readback(s), current['readback'])
            before = json.loads((OUT / f"controls-{len(m['control_trials'])-1:02d}-N{start}.json").read_text())
            final = film(s)
            met = collect(s, m, start, end, before['film'], final, before['state']['readback']['fields'], OUT / f'batch-N{start}-N{end}.trn')
            met.update(output=str(OUT), controls=dict(m['controlled_delta']), pair=pair,
                       wall_seconds=None, film_ms_per_wall_minute=None, execution_repeated=False)
            dump(OUT / f'endpoint-N{end}.json', {'pair': pair, 'state': state(s), 'film': final, 'metrics': met, 'reopen': 'PASS'})
            m['blocks'].append(met)
            m.update(status='ALTERNATIVE_INNER_EVIDENCE_REQUIRED', verified_native_end=end, latest_pair=pair,
                     latest_metrics=met, final_reopen='PASS', active_target=None)
            dump(MANIFEST, m)
            print('COMPLETED_ALTERNATIVE_RECONCILED_NO_REPEAT_SOLVE', json.dumps(met), flush=True)
            return
        if args.operation == 'recover-adaptive':
            if m['status'] == 'RECOVERY_REQUIRED' and 'Refusing to overwrite remote hash evidence' in m.get('error', ''):
                if m.get('active_target') is not None or native_iteration(s) != m['verified_native_end']:
                    raise RuntimeError('Hash-preparation repair requires an unsolved endpoint')
                expected = json.loads((OUT / f"endpoint-N{m['verified_native_end']}.json").read_text())
                require_match(readback(s), expected['state']['readback'])
                if film(s) != expected['film']:
                    raise RuntimeError('Hash repair endpoint changed')
                m.setdefault('implementation_repairs', []).append({'error': m.pop('error'),
                     'repair': 'Unique hash-evidence filenames; live endpoint unchanged; zero repeated solve'})
                m['status'] = 'NUMERICAL_RECOVERY_REQUIRED'
                dump(MANIFEST, m)
            if m['status'] == 'PAUSED_BY_USER':
                paused = json.loads((ROOT_OUT / 'pause-readback.json').read_text())
                if native_iteration(s) != paused['native_iteration'] or not s.settings.solution.run_calculation.iterate.is_active():
                    raise RuntimeError('Paused session differs; preserve/reconcile before resuming')
                require_match(readback(s), paused['state']['readback'])
                if film(s) != paused['film']:
                    raise RuntimeError('Paused film state differs')
                m.update(status=m['pre_pause_status'], resume_authority='explicit_human_resume_2026_10_05',
                         pause_reason=None, idle=True)
                dump(MANIFEST, m)
                print('PAUSED_N7190_LIVE_STATE_VERIFIED_RESUMING', flush=True)
            if m['status'] != 'NUMERICAL_RECOVERY_REQUIRED':
                raise RuntimeError('Recovery operation requires preserved numerical failure')
            recover_adaptive(s, m)
            return
        if m['status'] not in ['PREPARED_VERIFIED', 'BLOCK_COMPLETE', 'ALTERNATIVE_INNER_EVIDENCE_REQUIRED', 'MATCHED_TIME_SENSITIVITY_PASS', 'FROZEN_FILM_STATIONARITY_SCREEN', 'DEVELOPED_STEP_SCREEN_PASS'] and args.operation != 'resume-grow-sensitivity':
            raise RuntimeError('Prior operation needs reconciliation')
        if args.operation == 'developed-sensitivity':
            developed_sensitivity(s, m)
            return
        if args.operation == 'full-bulk-development':
            full_bulk_development(s, m)
            return
        if args.operation == 'probe-relative':
            controls(s, m, {'implicit-rel-residual?': True})
            block(s, m, 10)
            return
        if args.operation == 'probe-frozen':
            restore_half(s, m, {'ewf-adaptive?': False, 'timestep-max': 1e-6, 'sub-iter-nums': 30}, 'frozen-bulk-diagnostic')
            freeze(s, m)
            block(s, m, 100)
            return
        if args.operation == 'sensitivity':
            sensitivity(s, m)
            return
        if args.operation == 'grow-sensitivity':
            grow_sensitivity(s, m, args.candidate_step_us)
            return
        if args.operation == 'resume-grow-sensitivity':
            grow_sensitivity(s, m, args.candidate_step_us, resume=True)
            return
        if args.operation == 'develop-alternative':
            develop_alternative(s, m)
            return
        if args.operation == 'repair-half':
            restore_half(s, m)
            block(s, m, 100)
            return
        if args.operation == 'repair-segregated':
            restore_half(s, m, {'ewf-adaptive?': False, 'timestep-max': 1e-6, 'sub-iter-nums': 30,
                                'film-coupled-solution?': False}, 'segregated-film-probe')
            block(s, m, 100)
            return
        if args.operation == 'repair-implicit':
            # Fluent 252's generated TUI explicitly exposes this alternative
            # implicit scheme under eulerian_wallfilm.implicit_options (beta).
            restore_half(s, m, {'ewf-adaptive?': False, 'timestep-max': 1e-6, 'sub-iter-nums': 30,
                                'implicit-scheme-new?': True}, 'alternative-implicit-probe')
            block(s, m, 100)
            return
        if args.operation == 'develop':
            develop(s, m)
            return
        if args.operation == 'adaptive-probe':
            if not m['latest_metrics']['eligible_for_step_increase']:
                raise RuntimeError('Fixed-step probe needs numerical repair before step increase')
            controls(s, m, {'ewf-adaptive?': True, 'courant-number': .05, 'adapt-init-dt': 1e-6, 'adapt-tstp-inc': 1.3, 'adapt-tstp-dec': 2.0})
        block(s, m, 1000 if args.operation == 'batch' else 100)
    except Exception:
        if MANIFEST.exists():
            m = json.loads(MANIFEST.read_text())
            m.update(status='RECOVERY_REQUIRED', error=traceback.format_exc())
            dump(MANIFEST, m)
        try:
            s.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
            s.transcript.stop()
        except Exception:
            pass
        raise


if __name__ == '__main__':
    main()
