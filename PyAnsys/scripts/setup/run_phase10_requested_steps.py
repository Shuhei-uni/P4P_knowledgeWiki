"""Apply the human-requested timestep sequence to the existing Phase 10 solver.

No launch, initialization or session replacement. Reconcile the completed native
batch before the first parameter change. Keep the established evidence guards.
"""
import json
import math
import time
import traceback

import run_phase10_proposed_design as p


def state():
    return json.loads((p.OUT / 'run-manifest.json').read_text())


def check(s, record):
    m = state()
    if record['ledger_error_percent'] > .1:
        raise RuntimeError('Film ledger exceeds development tolerance')
    p.bulk_persistence(m['qualification_parent'], m['latest_pair'])
    if not math.isclose(p.replay.readback(s)['fields']['v2-total-liquid-mass'][0],
                        m['frozen_bulk_mass_kg'], rel_tol=1e-10):
        raise RuntimeError('Frozen bulk mass changed')


def reconcile(s):
    m = state()
    # The RPC query returns after the already-submitted native solve. No new solve.
    end = p.native_iteration(s)
    if end != m['active_target'] or m['native_start'] != m['native_end']:
        raise RuntimeError('Interrupted controller batch did not reach its target')
    pair = p.save(s, 'human-step-change-parent-N' + str(end))
    clock = dict(s.rp_vars('wall-film/solution-state'))
    steps = end - m['native_start']
    elapsed = clock['film_elapsed_time'] - m['observed_film_age_s']
    if clock['max_timestep_count'] - m['film_update_count'] != steps or not math.isclose(
            elapsed, steps * .5e-6, abs_tol=1e-10):
        raise RuntimeError('Completed batch film clock differs')
    histories = {name: p.history(p.Path(path).read_text()) for name, path in m['paths'].items()}
    expected = set(range(m['native_start'] + 1, end + 1))
    if any(not expected.issubset(h) or not all(math.isfinite(h[i]) for i in expected)
           for h in histories.values()):
        raise RuntimeError('Completed batch report coverage differs')
    mass = histories['p72a-e2.7-ewf-film-mass-total']
    drain = histories['p72a-e2.7-ewf-outflow-mass-total']
    supplied = sum(histories['p72a-e2.7-ewf-secondary-phase-mass-total'][i] * .5e-6 for i in expected)
    gain = mass[end] - mass[m['native_start']]
    removed = drain[end] - drain[m['native_start']]
    peak = max(histories['p72a-e2.7-ewf-courant-max'][i] for i in expected)
    if histories['p72a-e2.7-ewf-thickness-max'][end] > .003:
        raise RuntimeError('Completed batch film bound exceeded')
    record = dict(label='film-development-18-reconciled-human-change',
                  native_start=m['native_start'], native_end=end,
                  film_age_s=clock['film_elapsed_time'], added_film_time_s=elapsed,
                  film_mass_kg=mass[end], peak_courant=peak, pair=pair,
                  transcript=m['transcript'], integrated_input_kg=supplied,
                  integrated_removal_kg=removed, film_storage_kg=gain,
                  ledger_error_percent=100 * abs(gain + removed - supplied) / max(abs(supplied), 1e-30),
                  reconciliation='Controller interrupted; native solve completed once. Full report coverage and saved native clock establish endpoint.')
    m.setdefault('blocks', []).append(record)
    m.update(status='IDLE_VERIFIED', latest_pair=pair, native_end=end, active_target=None,
             observed_film_age_s=clock['film_elapsed_time'], film_update_count=clock['max_timestep_count'])
    m['reconciled_error'] = m.pop('error', None)
    p.dump('human-step-change-reconciliation.json', record)
    p.dump('run-manifest.json', m)
    check(s, record)
    return record


def finalize(s):
    m = state()
    if abs(m['observed_film_age_s'] - .100) > 1e-10:
        raise RuntimeError('Requested 100 ms horizon not attained')
    before = p.replay.readback(s)
    pair = p.save(s, 'final-100ms')
    p.load(s, pair)
    p.replay.require_match(p.replay.readback(s), before)
    clock = dict(s.rp_vars('wall-film/solution-state'))
    if abs(clock['film_elapsed_time'] - .100) > 1e-10:
        raise RuntimeError('Final reopen film clock differs')
    fields = p.film_fields(s)
    import numpy as np
    np.savez_compressed(p.OUT / 'final-100ms-film-fields.npz', **fields)
    m = state()
    m.update(status='COMPLETE_100MS_ENDPOINT_REOPEN_VERIFIED', final_pair=pair,
             observed_film_age_s=clock['film_elapsed_time'], active_target=None,
             solver_left_open=True, completed_epoch=time.time(),
             claim='Finite frozen-bulk basic EWF development with human-requested timestep changes; faster steps are not matched-time qualified')
    p.dump('final-reopen.json', {'pair': pair, 'clock': clock, 'readback': p.replay.readback(s)})
    p.dump('run-manifest.json', m)
    p.plot_final(s, m, fields)
    print('PHASE10_COMPLETE_100MS_ENDPOINT_REOPEN_VERIFIED', flush=True)


def controls(s, step):
    before = p.replay.readback(s)
    p.parameters(s, {'timestep-max': step})
    pair = p.save(s, 'human-controls-' + str(step) + '-N' + str(p.native_iteration(s)))
    p.load(s, pair)
    p.replay.require_match({'fields': p.replay.readback(s)['fields']}, {'fields': before['fields']})
    if dict(s.rp_vars('wall-film/model-parameters'))['timestep-max'] != step:
        raise RuntimeError('Reopened timestep controls differ')
    if abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - state()['observed_film_age_s']) > 1e-12:
        raise RuntimeError('Control activation changed film age')
    m = state()
    m.update(latest_pair=pair, active_target=None, status='IDLE_VERIFIED')
    m.pop('error', None)
    p.dump('run-manifest.json', m)


def recover_completed_1us(s):
    m = state()
    end = p.native_iteration(s)
    if m['native_start'] != 25580 or end != 28580:
        raise RuntimeError('Completed 1us horizon differs')
    films = [list(map(float, match.groups())) for match in p.FILM.finditer(p.Path(m['transcript']).read_text())]
    if len(films) != 3000 or any(abs(f[1] - 1e-6) > 1e-12 for f in films):
        raise RuntimeError('Completed 1us native timestep coverage differs')
    pair = p.save(s, 'recovered-human-1us-3000-N28580')
    clock = dict(s.rp_vars('wall-film/solution-state'))
    if abs(clock['film_elapsed_time'] - .018) > 1e-10 or clock['max_timestep_count'] - m['film_update_count'] != 3000:
        raise RuntimeError('Completed 1us saved clock differs')
    histories = p.report_histories(s, m)
    expected = set(range(25581, 28581))
    if any(not expected.issubset(h) or not all(math.isfinite(h[i]) for i in expected) for h in histories.values()):
        raise RuntimeError('Recovered native report coverage differs')
    mass = histories['p72a-e2.7-ewf-film-mass-total']
    drain = histories['p72a-e2.7-ewf-outflow-mass-total']
    supplied = sum(histories['p72a-e2.7-ewf-secondary-phase-mass-total'][i] * 1e-6 for i in expected)
    gain, removed = mass[end] - mass[25580], drain[end] - drain[25580]
    if histories['p72a-e2.7-ewf-thickness-max'][end] > .003:
        raise RuntimeError('Recovered film thickness exceeds development bound')
    record = dict(label='film-development-human-1us-3000', native_start=25580, native_end=end,
                  film_age_s=clock['film_elapsed_time'], added_film_time_s=.003,
                  film_mass_kg=mass[end], peak_courant=max(f[2] for f in films), pair=pair,
                  transcript=m['transcript'], integrated_input_kg=supplied,
                  integrated_removal_kg=removed, film_storage_kg=gain,
                  ledger_error_percent=100 * abs(gain + removed - supplied) / abs(supplied),
                  reconciliation='Recovered Fluent-renamed native report files; completed 3000 updates counted once')
    m['blocks'].append(record)
    m['reconciled_error'] = m.pop('error', None)
    m.update(status='IDLE_VERIFIED', native_end=end, active_target=None, latest_pair=pair,
             observed_film_age_s=clock['film_elapsed_time'], film_update_count=clock['max_timestep_count'])
    p.dump('recovered-human-1us-3000-metrics.json', record)
    p.dump('run-manifest.json', m)
    check(s, record)


def run(s, prepared=False, one_us_done=False):
    try:
        if not prepared:
            reconcile(s)
        m = state()
        if not one_us_done and m['observed_film_age_s'] + .003 >= .100:
            raise RuntimeError('Insufficient horizon for requested 3000 updates')
        m['human_timestep_sequence'] = {'authority': 'Human: 1us for 3000 iterations, then 2.5us until 100ms',
                                      'initial_step_s': 1e-6, 'initial_updates': 3000,
                                      'final_step_s': 2.5e-6, 'target_film_age_s': .100,
                                      'matched_time_qualified': False}
        p.dump('run-manifest.json', m)
        if not one_us_done:
            controls(s, 1e-6)
            p.dump('human-1us-controls.json', dict(s.rp_vars('wall-film/model-parameters')))
            result = p.batch(s, 3000, 'film-development-human-1us-3000')
            if abs(result['added_film_time_s'] - .003) > 1e-10:
                raise RuntimeError('Effective 1us timestep differs')
            check(s, result)
        m = state()
        m['human_timestep_sequence']['initial_updates_verified'] = 3000
        m['human_timestep_sequence']['initial_endpoint_s'] = m['observed_film_age_s']
        p.dump('run-manifest.json', m)
        controls(s, 2.5e-6)
        p.dump('human-2p5us-controls.json', dict(s.rp_vars('wall-film/model-parameters')))
        for index in range(1, 101):
            remaining = .100 - state()['observed_film_age_s']
            if remaining <= 1e-12:
                break
            steps = min(1000, max(1, int(math.ceil(remaining / 2.5e-6 - 1e-9))))
            if steps < 1000:
                controls(s, remaining / steps)
            result = p.batch(s, steps, 'film-development-human-2p5us-' + str(index))
            if abs(result['added_film_time_s'] - min(steps * 2.5e-6, remaining)) > 1e-10:
                raise RuntimeError('Effective 2.5us timestep differs')
            check(s, result)
        else:
            raise RuntimeError('Requested sequence update budget exhausted')
        finalize(s)
    except BaseException:
        m = state()
        m.update(status='RECOVERY_REQUIRED', error=traceback.format_exc(), solver_left_open=True)
        p.dump('run-manifest.json', m)
        raise
