"""Bounded Server 3 adaptive contrast from the verified N6000 endpoint.

Attach only; no initialization. A 20-update instrumentation check is part of
the requested 2000 updates. Unique local checkpoints preserve both parents.
"""
from pathlib import Path
from datetime import datetime, timezone
import functools
import argparse
import json
import math
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from run_phase72a_stage3_server3 import state, instrument, iterate, WORK, OUT as PARENT_OUT
from run_phase72a_e27_server1_continuation import native_iteration, pair_save, dump
from run_phase72a_local_film_replay import require_match
from run_phase72a_adaptive_film import history, FILM, ROW
from pyansys_fluent.connection import connect
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256

OUT = PARENT_OUT / 'adaptive-aggressive-N6000-N8000'
REMOTE = WORK / 'adaptive-aggressive-N6000-N8000'
DELTA = {'ewf-adaptive?': True, 'adapt-init-dt': 2e-6,
         'adapt-tstp-inc': 1.3, 'adapt-tstp-dec': 2.0,
         'courant-number': .15, 'timestep-max': 2e-6}


def attach():
    import ansys.fluent.core._grpc_services as low
    import ansys.fluent.core.services as high
    from ansys.fluent.core.utils.fluent_version import FluentVersion
    from ansys.fluent.core import config
    low._server_supports_v1 = lambda channel: False
    high.create_service_factory = functools.partial(high.create_service_factory, product_version=FluentVersion.v252)
    config.check_health = False
    solver = connect('3', start_transcript=False, tcp_timeout_seconds=5)
    assert '2025 R2' in str(solver.get_fluent_version())
    return solver


def film_state(s):
    return dict(s.rp_vars('wall-film/solution-state'))


def save(s, label):
    return pair_save(s, REMOTE / f'{label}.cas.h5', REMOTE / 'scratch', scratch_tag=label)


def invariant_check(actual, original):
    assert actual['methods'] == original['methods']
    assert actual['setup'] == original['setup']
    for k, v in original['readback'].items():
        if k not in ('fields', 'film_parameters'):
            assert actual['readback'][k] == v, k
    for k, v in original['film_model'].items():
        assert actual['film_model'][k] == DELTA.get(k, v), k


def clocks_and_residuals(text, start, end, endpoint_clock):
    clocks, residuals, pending = {}, {}, None
    for line in text.splitlines():
        f = FILM.search(line)
        if f:
            if pending is not None:
                raise RuntimeError('Unmapped nonterminal film clock')
            pending = [float(v) for v in f.groups()]
        elif ROW.match(line):
            n = int(ROW.match(line)[1])
            if start < n <= end:
                residuals[n] = [float(v) for v in line.split()[1:8]]
                if pending is not None:
                    clocks[n] = pending
                    pending = None
    terminal_mapping = None
    if pending is not None and set(clocks) == set(range(start + 1, end)):
        if not math.isclose(pending[0], endpoint_clock, abs_tol=5.1e-8):
            raise RuntimeError('Terminal native film clock differs')
        clocks[end] = pending
        terminal_mapping = 'Terminal film line mapped using saved native endpoint; residual row absent'
    if set(clocks) != set(range(start + 1, end + 1)):
        raise RuntimeError('Native per-update film clock coverage incomplete')
    return clocks, residuals, terminal_mapping


def collect(s, paths, start, end, before_film, after_film, initial_fields, transcript):
    histories = {}
    for name, path in paths.items():
        raw = read_text(s, path)
        (OUT / f'{name}.out').write_text(raw)
        h = history(raw)
        if not set(range(6001, end + 1)).issubset(h):
            raise RuntimeError(f'Missing native report rows: {name}')
        if not all(math.isfinite(v) for v in h.values()):
            raise RuntimeError(f'Nonfinite report values: {name}')
        histories[name] = h
    dump(OUT / 'report-histories.json', {name: {'iterations': sorted(h), 'values': [h[i] for i in sorted(h)], 'file': paths[name]} for name, h in histories.items()})
    clocks, residuals, terminal = clocks_and_residuals(transcript.read_text(), start, end, after_film['film_elapsed_time'])
    dump(OUT / f'clocks-N{start}-N{end}.json', clocks)
    dump(OUT / f'residuals-N{start}-N{end}.json', residuals)
    previous = before_film['film_elapsed_time']
    integrated = 0.0
    actual_steps = []
    for n in range(start + 1, end + 1):
        dt = clocks[n][0] - previous
        if dt <= 0:
            raise RuntimeError('Non-increasing native film time')
        actual_steps.append(dt)
        integrated += histories['p72a-e2.7-ewf-secondary-phase-mass-total'][n] * dt
        previous = clocks[n][0]
    if abs(previous - after_film['film_elapsed_time']) > 5.1e-8:
        raise RuntimeError('Native clock endpoint differs')
    assert after_film['max_timestep_count'] - before_film['max_timestep_count'] == end - start
    mass = histories['p72a-e2.7-ewf-film-mass-total']
    drain = histories['p72a-e2.7-ewf-outflow-mass-total']
    m0 = initial_fields['p72a-e2.7-ewf-film-mass-total'][0]
    d0 = initial_fields['p72a-e2.7-ewf-outflow-mass-total'][0]
    elapsed = after_film['film_elapsed_time'] - before_film['film_elapsed_time']
    gain, drained = mass[end] - m0, drain[end] - d0
    count = min(500, end - start)
    ids = list(range(end - count + 1, end + 1))
    avg = lambda name, sign=1: sign * sum(histories[name][i] for i in ids) / count
    return {'native_start': start, 'native_end': end, 'updates': end - start,
            'added_film_time_s': elapsed, 'native_film_clock_end_s': after_film['film_elapsed_time'],
            'printed_step_min_s': min(v[1] for v in clocks.values()),
            'printed_step_max_s': max(v[1] for v in clocks.values()),
            'peak_film_cfl': max(v[2] for v in clocks.values()),
            'film_inventory_end_kg': mass[end], 'inventory_gain_kg': gain,
            'drained_mass_kg': drained, 'integrated_accretion_kg': integrated,
            'film_ledger_error_percent': 100 * abs(gain + drained - integrated) / abs(integrated),
            'film_inventory_growth_kg_s': gain / elapsed,
            'maximum_thickness_m': max(histories['p72a-e2.7-ewf-thickness-max'][i] for i in range(start + 1, end + 1)),
            'final_window_updates': count,
            'bulk_inventory_mean_kg': avg('v2-total-liquid-mass'),
            'liquid_carryover_mean_kg_s': avg('v2-flux-phase2-steamoutlet', -1),
            'vapor_outlet_mean_kg_s': avg('v2-flux-phase1-steamoutlet', -1),
            'contact_removal_mean_kg_s': avg('p72-contact-removal'),
            'pressure_drop_mean_Pa': avg('p72s3-pressure-inlet') - avg('p72s3-pressure-outlet'),
            'continuity_mean': sum(v[0] for i, v in residuals.items() if i in ids) / len([i for i in ids if i in residuals]),
            'residual_rows': len(residuals), 'terminal_clock_mapping': terminal,
            'accounting_limit': 'Film ledger only; bulk is steady pseudo-time, whole separator remains unqualified'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume-after-clock-repair', action='store_true')
    args = parser.parse_args()
    if (OUT / 'run-manifest.json').exists() and not args.resume_after_clock_repair:
        raise RuntimeError('Reconcile existing continuation; refusing duplicate run')
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {'status': 'PREFLIGHT', 'server_id': '3',
                'authority': 'human_2026_10_05_more_aggressive_adaptive_2000_full_server3',
                'requested_updates': 2000, 'target_native_iteration': 8000,
                'controlled_delta': DELTA, 'native_maximum_step_bound': 'NOT_VERIFIED; timestep-max is not claimed as adaptive ceiling',
                'work_root': str(REMOTE), 'blocks': [], 'solver_left_open': True}
    if args.resume_after_clock_repair:
        manifest = json.loads((OUT / 'run-manifest.json').read_text())
        assert manifest['status'] == 'RECOVERY_REQUIRED'
        assert 'Native clock endpoint differs' in manifest['error']
    else:
        dump(OUT / 'run-manifest.json', manifest)
    s = attach()
    active_transcript = False
    try:
        assert s.settings.solution.run_calculation.iterate.is_active()
        if args.resume_after_clock_repair:
            return resume_after_clock_repair(s, manifest)
        assert native_iteration(s) == 6000
        before = state(s)
        reference = json.loads((PARENT_OUT / 'adaptive-endpoint-N6000.json').read_text())
        require_match(before['readback'], reference['state']['readback'])
        assert before['setup'] == reference['state']['setup'] and before['methods'] == reference['state']['methods']
        for folder in [REMOTE, REMOTE / 'scratch', REMOTE / 'monitors']:
            ensure_remote_directory(s, str(folder))
        for kind in ['case', 'data']:
            observed = remote_file_sha256(s, reference['pair'][kind], str(REMOTE / 'scratch' / f'parent-{kind}.sha256.txt'))
            assert observed == reference['pair'][kind + '_sha256']
        manifest['parent_pair'] = reference['pair']
        manifest['preserved_live_parent'] = save(s, 'parent-N6000')
        initial_film = film_state(s)
        dump(OUT / 'parent-state.json', {'state': before, 'film_solution_state': initial_film})
        params = s.rp_vars('wall-film/model-parameters')
        assert set(DELTA).issubset(dict(params))
        s.rp_vars('wall-film/model-parameters', [(k, DELTA.get(k, v)) for k, v in params])
        paths = instrument(s, REMOTE / 'monitors')
        prepared = state(s)
        invariant_check(prepared, before)
        require_match({'fields': prepared['readback']['fields']}, {'fields': before['readback']['fields']})
        pair = save(s, 'prepared-N6000')
        s.settings.file.read_case(file_name=pair['case'])
        s.settings.file.read_data(file_name=pair['data'])
        reopened = state(s)
        require_match(reopened['readback'], prepared['readback'])
        invariant_check(reopened, before)
        assert native_iteration(s) == 6000
        assert film_state(s)['film_elapsed_time'] == initial_film['film_elapsed_time']
        dump(OUT / 'prepared-reopen.json', {'pair': pair, 'state': reopened, 'film_solution_state': film_state(s), 'checks': 'PASS'})
        manifest.update(status='PREPARED_VERIFIED', prepared_pair=pair, report_paths=paths, parent_native_film_clock_s=initial_film['film_elapsed_time'], verified_native_end=6000)
        dump(OUT / 'run-manifest.json', manifest)
        print('PREPARED_REOPEN_PASS', json.dumps(DELTA), flush=True)
        for target in [6020, 7000, 8000]:
            start = native_iteration(s)
            initial = state(s)
            initial_clock = film_state(s)
            transcript = OUT / f'batch-N{start}-N{target}.txt'
            s.transcript.start(file_name=str(transcript), write_to_stdout=False)
            active_transcript = True
            manifest.update(status='RUNNING', active_target=target, command=f'/solve/iterate {target-start}', started_utc=datetime.now(timezone.utc).isoformat())
            dump(OUT / 'run-manifest.json', manifest)
            print('SUBMIT', start, target, flush=True)
            t = time.monotonic()
            iterate(s, target - start)
            current = state(s)
            final_clock = film_state(s)
            invariant_check(current, before)
            pair = save(s, f'checkpoint-N{target}')
            # RP solution-state is host-cached during solve; saved data holds
            # the updated native film clock. Reload the exact paired endpoint.
            s.settings.file.read_case(file_name=pair['case'])
            s.settings.file.read_data(file_name=pair['data'])
            require_match(state(s)['readback'], current['readback'])
            final_clock = film_state(s)
            # File-backed endpoint reports are flushed by paired saving.
            time.sleep(.5)
            s.transcript.stop()
            active_transcript = False
            metrics = collect(s, paths, start, target, initial_clock, final_clock, initial['readback']['fields'], transcript)
            metrics['wall_seconds'] = time.monotonic() - t
            dump(OUT / f'endpoint-N{target}.json', {'pair': pair, 'state': current, 'film_solution_state': final_clock, 'metrics': metrics})
            manifest['blocks'].append(metrics)
            manifest.update(status='BLOCK_COMPLETE', verified_native_end=target, latest_pair=pair)
            dump(OUT / 'run-manifest.json', manifest)
            print('BLOCK_COMPLETE', json.dumps(metrics), flush=True)
            if (metrics['peak_film_cfl'] > 1 or metrics['maximum_thickness_m'] > .003 or metrics['film_ledger_error_percent'] > 1):
                raise RuntimeError('Numerical recovery limit exceeded; paired checkpoint preserved')
            if target == 6020 and metrics['printed_step_max_s'] <= 1.01e-6:
                raise RuntimeError('New adaptive controls did not increase accepted film step; inspect before remaining updates')
        s.settings.file.read_case(file_name=pair['case'])
        s.settings.file.read_data(file_name=pair['data'])
        require_match(state(s)['readback'], current['readback'])
        assert native_iteration(s) == 8000
        assert s.settings.solution.run_calculation.iterate.is_active()
        manifest.update(status='COMPLETE', final_reopen='PASS', idle=True, completed_utc=datetime.now(timezone.utc).isoformat(), total_added_film_time_s=final_clock['film_elapsed_time'] - initial_film['film_elapsed_time'])
        dump(OUT / 'run-manifest.json', manifest)
        print('COMPLETE_N8000', manifest['total_added_film_time_s'], flush=True)
    except Exception:
        if active_transcript:
            try: s.transcript.stop()
            except Exception: pass
        manifest.update(status='RECOVERY_REQUIRED', error=traceback.format_exc())
        dump(OUT / 'run-manifest.json', manifest)
        raise


def resume_after_clock_repair(s, manifest):
    """Reconcile the saved 20-update smoke, then run only 1980 remaining."""
    assert native_iteration(s) == 6020
    before_record = json.loads((OUT / 'parent-state.json').read_text())
    before = before_record['state']
    initial_film = before_record['film_solution_state']
    current = state(s)
    invariant_check(current, before)
    clock = film_state(s)
    assert abs(clock['film_elapsed_time'] - .003064737050000074) < 1e-9
    paths = manifest['report_paths']
    metrics = collect(s, paths, 6000, 6020, initial_film, clock, before['readback']['fields'], OUT / 'batch-N6000-N6020.txt')
    pair = {'case': str(REMOTE / 'checkpoint-N6020.cas.h5'), 'data': str(REMOTE / 'checkpoint-N6020.dat.h5'), 'native_iteration': 6020}
    for kind in ['case', 'data']:
        pair[kind + '_sha256'] = remote_file_sha256(s, pair[kind], str(REMOTE / 'scratch' / f'reconciled-N6020-{kind}.sha256.txt'))
    dump(OUT / 'endpoint-N6020.json', {'pair': pair, 'state': current, 'film_solution_state': clock, 'metrics': metrics})
    manifest['blocks'].append(metrics)
    manifest.update(status='SMOKE_RECONCILED', verified_native_end=6020, latest_pair=pair,
                    recovery='Reload exact saved data for updated native film solution-state; no repeated updates')
    manifest.pop('error', None)
    dump(OUT / 'run-manifest.json', manifest)
    print('SMOKE_RECONCILED', json.dumps(metrics), flush=True)
    active_transcript = False
    try:
        for target in [7000, 8000]:
            start = native_iteration(s)
            initial = state(s)
            start_clock = film_state(s)
            transcript = OUT / f'batch-N{start}-N{target}.txt'
            s.transcript.start(file_name=str(transcript), write_to_stdout=False)
            active_transcript = True
            manifest.update(status='RUNNING', active_target=target, command=f'/solve/iterate {target-start}')
            dump(OUT / 'run-manifest.json', manifest)
            print('SUBMIT', start, target, flush=True)
            t = time.monotonic()
            iterate(s, target - start)
            current = state(s)
            invariant_check(current, before)
            pair = save(s, f'checkpoint-N{target}')
            dump(OUT / f'saved-N{target}.json', {'pair': pair, 'state': current})
            s.settings.file.read_case(file_name=pair['case'])
            s.settings.file.read_data(file_name=pair['data'])
            require_match(state(s)['readback'], current['readback'])
            clock = film_state(s)
            time.sleep(.5)
            s.transcript.stop()
            active_transcript = False
            metrics = collect(s, paths, start, target, start_clock, clock, initial['readback']['fields'], transcript)
            metrics['wall_seconds'] = time.monotonic() - t
            dump(OUT / f'endpoint-N{target}.json', {'pair': pair, 'state': current, 'film_solution_state': clock, 'metrics': metrics})
            manifest['blocks'].append(metrics)
            manifest.update(status='BLOCK_COMPLETE', verified_native_end=target, latest_pair=pair)
            dump(OUT / 'run-manifest.json', manifest)
            print('BLOCK_COMPLETE', json.dumps(metrics), flush=True)
            if metrics['peak_film_cfl'] > 1 or metrics['maximum_thickness_m'] > .003 or metrics['film_ledger_error_percent'] > 1:
                raise RuntimeError('Numerical recovery limit exceeded; paired checkpoint preserved')
        assert native_iteration(s) == 8000
        assert s.settings.solution.run_calculation.iterate.is_active()
        manifest.update(status='COMPLETE', final_reopen='PASS', idle=True,
                        completed_utc=datetime.now(timezone.utc).isoformat(), total_added_film_time_s=clock['film_elapsed_time'] - initial_film['film_elapsed_time'])
        dump(OUT / 'run-manifest.json', manifest)
        print('COMPLETE_N8000', manifest['total_added_film_time_s'], flush=True)
    except Exception:
        if active_transcript:
            try: s.transcript.stop()
            except Exception: pass
        manifest.update(status='RECOVERY_REQUIRED', error=traceback.format_exc())
        dump(OUT / 'run-manifest.json', manifest)
        raise


if __name__ == '__main__':
    main()
