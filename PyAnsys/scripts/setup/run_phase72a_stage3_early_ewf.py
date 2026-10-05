"""Stage 3 early EWF contrast from the exact historical A bulk fields.

Attach to explicitly owned Server 1. Preserve its endpoint before replacement.
Preparation and the solve are separate; no bulk initialization is allowed.
"""
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import argparse
import functools
import json
import math
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_chdir, remote_file_exists
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256
from run_phase72a_e27_server1_continuation import pair_save, native_iteration, dump
from run_phase72a_local_film_replay import readback, require_match
from run_phase72a_r3_ewf_absorber_direct import validate_roughness
import run_phase72a_stage3_server3 as base

OUT = ROOT / 'output/phase72a-stage3-early-ewf-server1/20261005'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage3\early-ewf-startup-20261005')
A = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase71A\FamilyR\P71A-R0-SMOOTH-CONTROL\paused-current-20260922T024707Z\P71A-R0-SMOOTH-CONTROL-paused-current')
SHARED = PureWindowsPath(r'C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\Stage3\early-ewf-startup')
HASHES = {'cas.h5': '232e72ff86c657b2d90bff56f6e9cb84336e30905e365fa89d7c699ef653bf57',
          'dat.h5': 'ff64317d4e6e77661d7faf13d26d4c04ac3d5db2ea78eed461762a3b3531c187'}
base.OUT, base.WORK = OUT, WORK


def attach():
    import ansys.fluent.core._grpc_services as low
    import ansys.fluent.core.services as high
    from ansys.fluent.core.utils.fluent_version import FluentVersion
    from ansys.fluent.core import config
    low._server_supports_v1 = lambda channel: False
    high.create_service_factory = functools.partial(high.create_service_factory, product_version=FluentVersion.v252)
    config.check_health = False
    s = connect('1', start_transcript=False, tcp_timeout_seconds=5)
    if '2025 R2' not in str(s.get_fluent_version()):
        raise RuntimeError('Version differs from verified 2025 R2 model')
    return s


def save(s, label):
    return pair_save(s, WORK / f'{label}.cas.h5', WORK / 'scratch', scratch_tag=label)


def verify_arrays():
    import hashlib
    import h5py
    import numpy as np
    shared = Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase72A/Stage3/early-ewf-startup')
    source = shared / 'parent-A/parent-A.dat.h5'
    prepared = shared / 'prepared-A-N1580/prepared-A-N1580.dat.h5'
    manifest = json.loads((OUT / 'run-manifest.json').read_text())
    for path, expected in [(source, HASHES['dat.h5']), (prepared, manifest['prepared_pair']['data_sha256'])]:
        with path.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != expected:
                raise RuntimeError('Local synchronized data hash differs')
    checks = []
    with h5py.File(source) as a, h5py.File(prepared) as b:
        for phase in ['phase-1', 'phase-2', 'phase-3']:
            names = ['SV_U', 'SV_V', 'SV_W', 'SV_VOF']
            if phase == 'phase-1':
                names = ['SV_U', 'SV_V', 'SV_W', 'SV_P', 'SV_K', 'SV_D', 'SV_SLIP_U', 'SV_SLIP_V', 'SV_SLIP_W']
            for name in names:
                key = f'results/1/{phase}/cells/{name}'
                av = np.concatenate([a[key][n][()] for n in sorted(a[key], key=int)])
                bv = np.concatenate([b[key][n][()] for n in sorted(b[key], key=int)])
                equal = av.shape == bv.shape and np.array_equal(av, bv)
                checks.append({'path': key, 'shape': list(av.shape), 'exact_equal': equal,
                               'max_absolute_difference': float(np.max(abs(av - bv))) if av.shape == bv.shape else None})
    proof = {'status': 'PASS' if all(c['exact_equal'] for c in checks) else 'FAIL',
             'source_data': str(source), 'prepared_data': str(prepared), 'datasets': checks,
             'scope': 'Stored bulk cell pressure, turbulence, velocity, slip and phase fraction; dry film initialized separately'}
    dump(OUT / 'bulk-array-verification.json', proof)
    if proof['status'] != 'PASS':
        raise RuntimeError('Prepared cell fields differ from A; do not run')
    print('EXACT_A_BULK_ARRAYS_PASS', len(checks), flush=True)


def share(s, pair, label):
    folder = SHARED / label
    ensure_remote_directory(s, str(folder))
    for kind, ext in [('case', 'cas.h5'), ('data', 'dat.h5')]:
        target = str(folder / f'{label}.{ext}')
        if remote_file_exists(s, target):
            raise FileExistsError(target)
        base.powershell(s, f"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath '{pair[kind]}' -Destination '{target}'")
        actual = remote_file_sha256(s, target, str(WORK / 'scratch' / f'{label}-{kind}-shared.sha256.txt'))
        if actual != pair[kind + '_sha256']:
            raise RuntimeError('Shared paired file hash differs')
    return str(folder)


def prepare(s):
    if (OUT / 'run-manifest.json').exists():
        raise RuntimeError('Reconcile existing preparation before repeating it')
    if not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Server 1 is busy; preserve current calculation before replacement')
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors']:
        ensure_remote_directory(s, str(folder))
    m = {'status': 'PREFLIGHT', 'server_id': '1', 'authority': 'human_2026_10_05_stage3_early_ewf_full_server1',
         'setup': 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/setup.md',
         'work_root': str(WORK), 'native_start': 1580, 'requested_updates': 3500, 'native_target': 5080,
         'blocks': [], 'bulk_reinitialized': False, 'solver_left_open': True}
    dump(OUT / 'run-manifest.json', m)
    for ext, expected in HASHES.items():
        actual = remote_file_sha256(s, str(A) + '.' + ext, str(WORK / 'scratch' / f'A-{ext}.sha256.txt'))
        if actual != expected:
            raise RuntimeError('Historical A parent hash differs')
    m['a_parent'] = {'case': str(A) + '.cas.h5', 'data': str(A) + '.dat.h5', 'hashes': HASHES}
    template = base.state(s)
    validate_roughness(s)
    old_n = native_iteration(s)
    m['preserved_previous_endpoint'] = save(s, f'previous-server1-N{old_n}')
    dump(OUT / 'model-template-state.json', template)
    dump(OUT / 'run-manifest.json', m)
    # Keep the current case topology, source hooks and wall assignments. Restore
    # only the historical bulk data. Reapply controls that data files can carry.
    s.transcript.start(file_name=str(OUT / 'prepare-transcript.txt'), write_to_stdout=False)
    s.settings.file.read_data(file_name=str(A) + '.dat.h5')
    s.settings.solution.methods.set_state(template['methods'])
    s.settings.solution.controls.set_state(template['readback']['controls'])
    base.loading(s, .25)
    s.rp_vars('wall-film/model-parameters', list(template['film_model'].items()))
    s.tui.define.models.eulerian_wallfilm.solve_wallfilm_equation('yes')
    s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
    changes = {'ewf-adaptive?': False, 'timestep-max': 1e-6, 'courant-number': .05,
               'sub-iter-nums': 10, 'film-message?': True, 'film-coupled-solution?': True,
               'thickness-limit': 1.0}
    params = dict(s.rp_vars('wall-film/model-parameters'))
    if not set(changes).issubset(params):
        raise RuntimeError('Required film settings unavailable')
    s.rp_vars('wall-film/model-parameters', [(k, changes.get(k, v)) for k, v in params.items()])
    validate_roughness(s)
    for key in ['hooks', 'lower_film_wall', 'entry_faces', 'dpm']:
        if readback(s)[key] != template['readback'][key]:
            raise RuntimeError('Current model invariant differs after A data load: ' + key)
    if native_iteration(s) != 1580:
        raise RuntimeError('Loaded A native coordinate is not N1580')
    fields = readback(s)['fields']
    if not math.isclose(fields['v2-total-liquid-mass'][0], 31.35713621088837, rel_tol=1e-9):
        raise RuntimeError('A bulk mass does not match recovered history')
    if fields['p72a-e2.7-ewf-film-mass-total'][0] != 0:
        raise RuntimeError('Film did not initialize dry')
    # Prevent inherited autosaves from writing into the older continuation.
    s.settings.file.auto_save.data_frequency = 0
    base.add_pressure_reports(s)
    m['report_paths'] = base.instrument(s, WORK / 'monitors')
    before = base.state(s)
    m['prepared_pair'] = save(s, 'prepared-A-N1580')
    s.settings.file.read_case(file_name=m['prepared_pair']['case'])
    s.settings.file.read_data(file_name=m['prepared_pair']['data'])
    after = base.state(s)
    require_match(after['readback'], before['readback'])
    if after['methods'] != before['methods'] or after['setup'] != before['setup']:
        raise RuntimeError('Prepared setup changed after reopen')
    s.transcript.stop()
    dump(OUT / 'prepared-reopen.json', {'state': after, 'film_solution_state': dict(s.rp_vars('wall-film/solution-state'))})
    m['shared_prepared_pair'] = share(s, m['prepared_pair'], 'prepared-A-N1580')
    m.update(status='PREPARED_REOPEN_VERIFIED_FIELD_ARRAY_CHECK_REQUIRED', verified_native_end=1580,
             prepared_reopen='PASS', film_step_s=1e-6, low_hold_updates=500, ramp_updates=2000, final_hold_updates=1000)
    dump(OUT / 'run-manifest.json', m)
    print('PREPARED_A_FIELDS_RETAINED', flush=True)


def run(s):
    m = json.loads((OUT / 'run-manifest.json').read_text())
    proof = json.loads((OUT / 'bulk-array-verification.json').read_text())
    if m['status'] != 'PREPARED_REOPEN_VERIFIED_FIELD_ARRAY_CHECK_REQUIRED' or proof['status'] != 'PASS':
        raise RuntimeError('Verified unrun child and A field-array proof required')
    expected = json.loads((OUT / 'prepared-reopen.json').read_text())['state']
    require_match(readback(s), expected['readback'])
    if native_iteration(s) != 1580:
        raise RuntimeError('Live prepared coordinate changed; refusing duplicate run')
    if not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Server 1 is busy')
    # The first 20 instrumented updates are included in the selected 500 hold.
    stages = [('low-hold-smoke', 1600, .25), ('low-hold', 2080, .25)]
    stages += [('ramp', 2080 + r + 10, .25 + .75 * r / 2000) for r in range(0, 2000, 10)]
    stages += [('target-hold', 5080, 1.)]
    start = time.monotonic()
    s.transcript.start(file_name=str(OUT / 'run-transcript.txt'), write_to_stdout=False)
    for label, target, fraction in stages:
        feed = base.loading(s, fraction)
        n = native_iteration(s)
        m.update(status='RUNNING', active_stage=label, active_target=target, command=f'/solve/iterate {target-n}')
        dump(OUT / 'run-manifest.json', m)
        base.iterate(s, target - n)
        record = {'stage': label, 'native_start': n, 'native_end': target, 'feed': feed}
        if label != 'ramp' or (target - 2080) % 500 == 0:
            record['pair'] = save(s, f'{label}-N{target}')
            current = base.state(s)
            s.settings.file.read_case(file_name=record['pair']['case'])
            s.settings.file.read_data(file_name=record['pair']['data'])
            require_match(readback(s), current['readback'])
            clock = dict(s.rp_vars('wall-film/solution-state'))
            if not math.isclose(clock['film_elapsed_time'], (target - 1580) * 1e-6, abs_tol=1e-12):
                raise RuntimeError('Saved fixed-step film clock differs from requested updates')
            dump(OUT / f'endpoint-N{target}.json', {'state': base.state(s), 'pair': record['pair'], 'film_solution_state': clock})
            fields = current['readback']['fields']
            if not all(math.isfinite(v[0]) for v in fields.values()) or fields['p72a-e2.7-ewf-thickness-max'][0] > .003:
                raise RuntimeError('Film numerical recovery limit exceeded; endpoint saved')
            h = base.collect(s, m['report_paths'], f'checkpoint-N{target}')
            if any(not set(range(1581, target + 1)).issubset(v['iterations']) for v in h.values()):
                raise RuntimeError('Checkpoint report coverage incomplete')
            vals = lambda name: dict(zip(h[name]['iterations'], h[name]['values']))
            ids = range(1581, target + 1)
            mass, drain, acc = [vals(k) for k in ['p72a-e2.7-ewf-film-mass-total', 'p72a-e2.7-ewf-outflow-mass-total', 'p72a-e2.7-ewf-secondary-phase-mass-total']]
            integrated = sum(acc[i] * 1e-6 for i in ids)
            ledger = 100 * abs(mass[target] + drain[target] - integrated) / max(abs(integrated), 1e-30)
            record['film_ledger_error_percent'] = ledger
            if max(vals('p72a-e2.7-ewf-courant-max')[i] for i in ids) > 1 or max(vals('p72a-e2.7-ewf-thickness-max')[i] for i in ids) > .003 or ledger > 1:
                raise RuntimeError('Film history recovery limit exceeded; endpoint saved')
            print('CHECKPOINT', label, target, fields['v2-total-liquid-mass'][0], flush=True)
        m['blocks'].append(record)
        m['verified_native_end'] = target
        dump(OUT / 'run-manifest.json', m)
    s.transcript.stop()
    histories = base.collect(s, m['report_paths'], 'final')
    required = set(range(1581, 5081))
    if any(not required.issubset(h['iterations']) for h in histories.values()):
        raise RuntimeError('Final native report coverage incomplete')
    pair = m['blocks'][-1]['pair']
    before = base.state(s)
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(readback(s), before['readback'])
    final_clock = dict(s.rp_vars('wall-film/solution-state'))
    dump(OUT / 'final-reopen.json', {'state': base.state(s), 'film_solution_state': final_clock, 'pair': pair})
    m['shared_final_pair'] = share(s, pair, 'final-N5080')
    m.update(status='COMPLETE_ANALYSIS_REQUIRED', final_pair=pair, final_reopen='PASS',
             wall_seconds=time.monotonic() - start, completed_utc=datetime.now(timezone.utc).isoformat())
    dump(OUT / 'run-manifest.json', m)
    print('EARLY_EWF_COMPLETE_N5080', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'verify-arrays', 'run'])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.operation == 'verify-arrays':
        verify_arrays()
        return
    s = attach()
    try:
        (prepare if args.operation == 'prepare' else run)(s)
    except Exception:
        path = OUT / 'run-manifest.json'
        if path.exists():
            m = json.loads(path.read_text())
            m.update(status='RECOVERY_REQUIRED', error=traceback.format_exc())
            dump(path, m)
        try:
            s.transcript.stop()
        except Exception:
            pass
        raise


if __name__ == '__main__':
    main()
