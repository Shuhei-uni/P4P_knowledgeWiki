"""Bounded commercial-steel continuation of the verified N25815 film parent.

Attach to Server 1, preserve its idle endpoint, never initialize, and save locally.
"""
from pathlib import Path, PureWindowsPath
import copy
import json
import math
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from run_phase72a_stage3_early_ewf import attach
from run_phase72a_stage3_server3 import state, instrument, iterate
from run_phase72a_e27_server1_continuation import native_iteration, pair_save, dump
from run_phase72a_local_film_replay import require_match
from run_phase72a_adaptive_film import history, FILM
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256

OUT = ROOT / 'output/phase72a-commercial-steel/20261006'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage3\commercial-steel-20261006')
SOURCE = ROOT / 'output/phase72a-stage3-film-development-server1/20261005/transfer-final-N25815.json'
ORIGINAL = ROOT / 'output/phase72a-stage3-film-development-server1/20261005/parent-state.json'
WALLS = ['separator-purnanto:1', 'separator-purnanto:1:001', 'wall', 'wall:004']
MANIFEST = OUT / 'run-manifest.json'


def film(s):
    return dict(s.rp_vars('wall-film/solution-state'))


def save(s, label):
    return pair_save(s, WORK / f'{label}.cas.h5', WORK / 'scratch', scratch_tag=label)


def roughness(s):
    return {z: s.settings.setup.boundary_conditions.wall[z].phase['mixture'].turbulence.get_state()
            for z in WALLS + ['bottom']}


def prepare():
    if MANIFEST.exists():
        raise RuntimeError('Existing run must be reconciled; refusing duplicate execution')
    OUT.mkdir(parents=True, exist_ok=True)
    m = {'status': 'PREFLIGHT', 'authority': 'human_2026_10_06_commercial_steel_parent_continuation',
         'server_id': '1', 'parent_native_iteration': 25815, 'requested_updates': 1000,
         'target_native_iteration': 26815, 'roughness_height_m': 4.5e-5, 'roughness_constant': .5,
         'bulk_initialization': 'FORBIDDEN', 'film_initialization': 'FORBIDDEN', 'steady_film': False,
         'work_root': str(WORK), 'blocks': []}
    dump(MANIFEST, m)
    s = attach()
    if not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Server 1 is busy; no replacement performed')
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors']:
        ensure_remote_directory(s, str(folder))
    m['preserved_previous_endpoint'] = save(s, f'preserved-previous-N{native_iteration(s)}')
    dump(MANIFEST, m)
    source = json.loads(SOURCE.read_text())
    for kind in ['case', 'data']:
        digest = remote_file_sha256(s, source['pair'][kind], str(WORK / 'scratch' / f'parent-{kind}.sha256'))
        if digest != source['pair'][kind + '_sha256']:
            raise RuntimeError('Parent artifact hash mismatch: ' + kind)
    s.settings.file.read_case(file_name=source['pair']['case'])
    s.settings.file.read_data(file_name=source['pair']['data'])
    assert native_iteration(s) == 25815
    before = state(s)
    initial_clock = film(s)
    require_match({'fields': before['readback']['fields']}, {'fields': source['state']['readback']['fields']})
    assert math.isclose(initial_clock['film_elapsed_time'], source['film']['film_elapsed_time'], abs_tol=1e-12)
    dump(OUT / 'loaded-parent.json', {'state': before, 'film': initial_clock, 'pair': source['pair']})
    for z in WALLS:
        t = s.settings.setup.boundary_conditions.wall[z].phase['mixture'].turbulence
        assert t.roughness_height.get_state()['value'] == .0005
        assert t.roughness_const.get_state()['value'] == .5
        t.roughness_height = 4.5e-5
    expected_setup = copy.deepcopy(before['setup'])
    for z in WALLS:
        expected_setup['boundary_conditions']['wall'][z]['phase']['mixture']['turbulence']['roughness_height']['value'] = 4.5e-5
    original = json.loads(ORIGINAL.read_text())['state']['readback']['controls']['equations']
    for name, enabled in original.items():
        s.settings.solution.controls.equations[name] = enabled
    delta = {'ewf-adaptive?': False, 'timestep-max': 1e-6, 'sub-iter-nums': 30}
    params = dict(s.rp_vars('wall-film/model-parameters'))
    assert set(delta).issubset(params)
    s.rp_vars('wall-film/model-parameters', [(k, delta.get(k, v)) for k, v in params.items()])
    prepared = state(s)
    assert prepared['setup'] == expected_setup, 'Unexpected physical setup change'
    assert prepared['methods'] == before['methods'], 'Carrier method changed'
    assert prepared['readback']['controls']['equations'] == original
    require_match({'fields': prepared['readback']['fields']}, {'fields': before['readback']['fields']})
    assert film(s)['film_elapsed_time'] == initial_clock['film_elapsed_time']
    m.update(parent_pair=source['pair'], parent_film_time_s=initial_clock['film_elapsed_time'],
             restored_bulk_equations=original, numerical_delta=delta,
             parent_film_mass_kg=before['readback']['fields']['p72a-e2.7-ewf-film-mass-total'][0])
    m['report_paths'] = instrument(s, WORK / 'monitors')
    s.settings.file.auto_save.data_frequency = 0
    m['prepared_pair'] = save(s, 'commercial-steel-prepared-N25815')
    s.settings.file.read_case(file_name=m['prepared_pair']['case'])
    s.settings.file.read_data(file_name=m['prepared_pair']['data'])
    reopened = state(s)
    require_match(reopened['readback'], prepared['readback'])
    assert reopened['setup'] == expected_setup
    assert native_iteration(s) == 25815
    assert film(s)['film_elapsed_time'] == initial_clock['film_elapsed_time']
    dump(OUT / 'prepared-reopen.json', {'state': reopened, 'film': film(s), 'roughness': roughness(s), 'reopen': 'PASS'})
    m.update(status='PREPARED_VERIFIED', prepared_reopen='PASS', latest_pair=m['prepared_pair'])
    dump(MANIFEST, m)
    print('PREPARED_VERIFIED N25815 roughness=0.045mm bulk equations restored', flush=True)
    return s, m, expected_setup


def main():
    if '--resume-probe' in sys.argv:
        s, m, expected_setup = resume_probe()
        batches = [980]
    else:
        s, m, expected_setup = prepare()
        batches = [20, 980]
    # A short instrumentation probe is included in the declared 1000 updates.
    for steps in batches:
        start = native_iteration(s)
        end = start + steps
        tag = f'batch-N{start}-N{end}'
        remote = str(WORK / f'{tag}.trn').replace('\\', '/')
        s.transcript.start(file_name=str(OUT / f'{tag}.txt'), write_to_stdout=False)
        s.scheme.eval(f'(ti-menu-load-string "/file/start-transcript \\\"{remote}\\\"")')
        initial = film(s)
        fields = state(s)['readback']['fields']
        m.update(status='RUNNING', active_target=end)
        dump(MANIFEST, m)
        print('SUBMIT', start, end, flush=True)
        begun = time.monotonic()
        iterate(s, steps)
        final = film(s)
        endpoint = state(s)
        assert endpoint['setup'] == expected_setup
        pair = save(s, f'checkpoint-N{end}')
        s.settings.file.read_case(file_name=pair['case'])
        s.settings.file.read_data(file_name=pair['data'])
        require_match(state(s)['readback'], endpoint['readback'])
        assert math.isclose(film(s)['film_elapsed_time'], final['film_elapsed_time'], rel_tol=0, abs_tol=1e-12)
        s.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
        s.transcript.stop()
        text = read_text(s, str(WORK / f'{tag}.trn'))
        (OUT / f'{tag}.trn').write_text(text)
        histories = {}
        for name, path in m['report_paths'].items():
            raw = read_text(s, path)
            (OUT / f'{name}.out').write_text(raw)
            h = history(raw)
            assert set(range(25816, end + 1)).issubset(h), name
            assert all(math.isfinite(v) for v in h.values()), name
            histories[name] = h
        clocks = [list(map(float, f.groups())) for f in FILM.finditer(text)]
        assert len(clocks) == steps, 'Incomplete film clock evidence'
        accretion = 0.
        previous = initial['film_elapsed_time']
        for i, clock in zip(range(start + 1, end + 1), clocks):
            dt = clock[0] - previous
            assert dt > 0
            accretion += dt * histories['p72a-e2.7-ewf-secondary-phase-mass-total'][i]
            previous = clock[0]
        gain = histories['p72a-e2.7-ewf-film-mass-total'][end] - fields['p72a-e2.7-ewf-film-mass-total'][0]
        drainage = histories['p72a-e2.7-ewf-outflow-mass-total'][end] - fields['p72a-e2.7-ewf-outflow-mass-total'][0]
        elapsed = final['film_elapsed_time'] - initial['film_elapsed_time']
        met = {'native_start': start, 'native_end': end, 'updates': steps, 'pair': pair, 'reopen': 'PASS',
               'wall_seconds': time.monotonic() - begun, 'film_time_s': final['film_elapsed_time'],
               'added_film_time_s': elapsed, 'film_mass_kg': histories['p72a-e2.7-ewf-film-mass-total'][end],
               'peak_cfl': max(c[2] for c in clocks), 'film_storage_kg_s': gain / elapsed,
               'film_drainage_kg_s': drainage / elapsed, 'film_accretion_kg_s': accretion / elapsed,
               'film_ledger_error_percent': 100 * abs(gain + drainage - accretion) / max(abs(accretion), 1e-30)}
        m['blocks'].append(met)
        m.update(status='CHECKPOINT_VERIFIED', latest_pair=pair, verified_native_end=end, active_target=None)
        dump(OUT / f'completed-N{end}.json', {'metrics': met, 'state': endpoint, 'film': final})
        dump(MANIFEST, m)
        print('COMPLETE_BATCH', json.dumps(met), flush=True)
        if met['peak_cfl'] > 1 or met['film_ledger_error_percent'] > 1 or met['film_mass_kg'] > 12.3:
            m.update(status='NUMERICAL_RECOVERY_REQUIRED')
            dump(MANIFEST, m)
            return 2
    m.update(status='COMPLETE', final_reopen='PASS', idle=s.settings.solution.run_calculation.iterate.is_active())
    dump(MANIFEST, m)
    return 0


def resume_probe():
    """Reconcile the saved 20-update endpoint without repeating its solve."""
    m = json.loads(MANIFEST.read_text())
    assert m['status'] == 'EXECUTION_RECONCILIATION_REQUIRED'
    assert m['active_target'] == 25835 and not m['blocks']
    s = attach()
    assert native_iteration(s) == 25835 and s.settings.solution.run_calculation.iterate.is_active()
    final = film(s)
    parent = json.loads((OUT / 'loaded-parent.json').read_text())
    initial = parent['film']
    assert final['max_timestep_count'] == initial['max_timestep_count'] + 20
    assert math.isclose(final['film_elapsed_time'], initial['film_elapsed_time'] + 20e-6, rel_tol=0, abs_tol=1e-12)
    prepared = json.loads((OUT / 'prepared-reopen.json').read_text())
    endpoint = state(s)
    assert endpoint['setup'] == prepared['state']['setup']
    assert endpoint['readback']['controls']['equations'] == m['restored_bulk_equations']
    pair = {'case': str(WORK / 'checkpoint-N25835.cas.h5'), 'data': str(WORK / 'checkpoint-N25835.dat.h5'), 'native_iteration': 25835}
    for kind in ['case', 'data']:
        pair[kind + '_sha256'] = remote_file_sha256(s, pair[kind], str(WORK / 'scratch' / f'reconcile-{kind}.sha256'))
    text = read_text(s, str(WORK / 'batch-N25815-N25835.trn'))
    (OUT / 'batch-N25815-N25835.trn').write_text(text)
    clocks = [list(map(float, f.groups())) for f in FILM.finditer(text)]
    assert len(clocks) == 20
    histories = {}
    for name, path in m['report_paths'].items():
        raw = read_text(s, path)
        (OUT / f'{name}.out').write_text(raw)
        histories[name] = history(raw)
        assert set(range(25816, 25836)).issubset(histories[name]), name
    previous = initial['film_elapsed_time']
    accretion = 0.
    for i, clock in zip(range(25816, 25836), clocks):
        dt = clock[0] - previous
        assert dt > 0
        accretion += dt * histories['p72a-e2.7-ewf-secondary-phase-mass-total'][i]
        previous = clock[0]
    gain = histories['p72a-e2.7-ewf-film-mass-total'][25835] - parent['state']['readback']['fields']['p72a-e2.7-ewf-film-mass-total'][0]
    drainage = histories['p72a-e2.7-ewf-outflow-mass-total'][25835] - parent['state']['readback']['fields']['p72a-e2.7-ewf-outflow-mass-total'][0]
    elapsed = final['film_elapsed_time'] - initial['film_elapsed_time']
    met = {'native_start':25815, 'native_end':25835, 'updates':20, 'pair':pair, 'reopen':'PASS_FLOAT_SERIALIZATION_TOLERANCE_1E-12_S',
           'film_time_s':final['film_elapsed_time'], 'added_film_time_s':elapsed,
           'film_mass_kg':histories['p72a-e2.7-ewf-film-mass-total'][25835], 'peak_cfl':max(c[2] for c in clocks),
           'film_storage_kg_s':gain/elapsed, 'film_drainage_kg_s':drainage/elapsed, 'film_accretion_kg_s':accretion/elapsed,
           'film_ledger_error_percent':100*abs(gain+drainage-accretion)/max(abs(accretion),1e-30)}
    assert met['peak_cfl'] <= 1 and met['film_ledger_error_percent'] <= 1 and met['film_mass_kg'] <= 12.3
    m['blocks'].append(met)
    m.update(status='CHECKPOINT_VERIFIED',latest_pair=pair,verified_native_end=25835,active_target=None,
             recovery='Serialization clock check repaired; completed probe preserved; zero repeated solve updates')
    dump(OUT / 'completed-N25835.json', {'metrics':met,'state':endpoint,'film':final})
    dump(MANIFEST,m)
    print('PROBE_RECONCILED', json.dumps(met), flush=True)
    return s, m, prepared['state']['setup']


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        if MANIFEST.exists():
            m = json.loads(MANIFEST.read_text())
            m.update(status='EXECUTION_RECONCILIATION_REQUIRED', error=traceback.format_exc())
            dump(MANIFEST, m)
        raise
