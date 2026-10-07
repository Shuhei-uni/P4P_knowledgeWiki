"""Supervised Server 3 film development from the verified 154k N5080 pair.

Reuse the recorded Stage 3 diagnostics; keep this mesh's parent and evidence
separate from the Server 1 experiment. Never initialize the bulk or film.
"""
from pathlib import Path, PureWindowsPath
import json
import math
import sys
import traceback
import numpy as np
import time
import uuid
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))
import continue_phase72a_stage3_film_development as ref
import run_phase72a_stage3_slit154k as source
import run_phase72a_e27_server1_continuation as pairs

OUT = ref.ROOT / 'output/phase72a-stage3-slit154k-film-development-server3/20261006'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage3\slit154k-film-development-20261006')
SOURCE = source.OUT / 'final-reopen.json'
ORIGINAL_COLLECT = ref.collect
ORIGINAL_BLOCK = ref.block
RESULTS = ref.ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/slit154k/film-development/results.md'


class SessionProxy:
    """Let technical recovery replace a failed channel without solver restart."""
    def __init__(self, session):
        self.session = session

    def __getattr__(self, name):
        return getattr(self.session, name)


def collect(*args):
    met = ORIGINAL_COLLECT(*args)
    # The old 60k experiment's 12.3 kg inventory bound is case-specific.
    # On this mesh, use actual field, Courant and ledger evidence instead.
    met['within_recovery_bounds'] = bool(met['peak_film_cfl'] <= 1
        and met['maximum_thickness_m'] <= .003 and math.isfinite(met['film_mass_kg'])
        and met['film_mass_kg'] >= 0 and met['film_ledger_error_percent'] <= 1)
    return met


def block(s, m, steps):
    """Record the initial native state and reconcile client loss without rerun."""
    start = ref.native_iteration(s)
    pending_path = ref.OUT / f'pending-N{start}-N{start+steps}.json'
    if pending_path.exists() or (ref.OUT / f'batch-N{start}-N{start+steps}.txt').exists():
        raise RuntimeError('Existing batch evidence requires reconciliation; refusing repeated compute')
    if start != m['verified_native_end'] or not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Verified idle native endpoint required before batch setup')
    autosave = s.settings.file.auto_save
    autosave.case_frequency = 'each-time'
    autosave.root_name = str(ref.WORK / f'auto-N{start}-N{start+steps}-%i')
    autosave.retain_most_recent_files = False
    autosave.data_frequency = 250 if steps >= 250 else 0
    initial = {'state': ref.state(s), 'film': ref.film(s), 'native_start': start,
               'native_end': start + steps, 'controls': dict(m['controlled_delta']),
               'native_autosave': autosave.get_state()}
    ref.dump(pending_path, initial)
    try:
        return ORIGINAL_BLOCK(s, m, steps)
    except Exception as error:
        ref.dump(ref.OUT / f'client-error-N{start}-N{start+steps}.json',
                 {'error': traceback.format_exc(), 'new_solve_calls': 0})
        # A Scheme timeout does not cancel the native command. Observe its
        # existing horizon; never submit a replacement batch while it runs.
        observed = None
        for unused in range(240):
            try:
                observed = source.attach()
                current = ref.native_iteration(observed)
                control = observed.settings.solution.run_calculation
                if current == start + steps and not control.iterate.is_active() and control.interrupt.is_active():
                    control.interrupt()
                if control.iterate.is_active():
                    break
            except Exception:
                observed = None
            time.sleep(15)
        if observed is None or not observed.settings.solution.run_calculation.iterate.is_active():
            raise RuntimeError('External connection block; native command must be reconciled before further solve') from error
        end = ref.native_iteration(observed)
        if not start < end <= start + steps:
            raise RuntimeError('Unexpected native horizon after client failure; no repeated solve') from error
        current_state = ref.state(observed)
        parent_state = json.loads((OUT / 'parent-state.json').read_text())['state']
        ref.invariant(current_state, parent_state, m['controlled_delta'])
        pair = ref.save(observed, f'recovered-N{end}-{uuid.uuid4().hex[:8]}')
        observed.settings.file.read_case(file_name=pair['case'])
        observed.settings.file.read_data(file_name=pair['data'])
        ref.require_match(ref.readback(observed), current_state['readback'])
        final = ref.film(observed)
        ref.dump(ref.OUT / f'recovered-completed-N{end}.json', {'pair': pair, 'state': ref.state(observed),
                 'film': final, 'initial': initial, 'reopen': 'PASS', 'new_solve_calls': 0})
        observed.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
        path = ref.OUT / f'batch-N{start}-N{start+steps}.trn'
        if not path.exists():
            path.write_text(ref.read_text(observed, str(ref.WORK / path.name)))
        met = collect(observed, m, start, end, initial['film'], final, initial['state']['readback']['fields'], path)
        met.update(output=str(ref.OUT), controls=dict(m['controlled_delta']), pair=pair,
                   wall_seconds=None, film_ms_per_wall_minute=None, execution_repeated=False,
                   requested_native_end=start+steps, communication_recovery='NATIVE_STATE_AND_TRANSCRIPT_RECONCILED')
        ref.dump(ref.OUT / f'endpoint-N{end}.json', {'pair': pair, 'state': ref.state(observed),
                 'film': final, 'metrics': met, 'reopen': 'PASS'})
        m['blocks'].append(met)
        m.update(status='BLOCK_COMPLETE', verified_native_end=end, latest_pair=pair,
                 latest_metrics=met, final_reopen='PASS', active_target=None)
        m.setdefault('communication_recoveries', []).append({'native_start': start, 'native_end': end,
                 'error': str(error), 'new_solve_calls': 0})
        ref.dump(ref.MANIFEST, m)
        # Keep the outer session object's live channel: the native endpoint is
        # now idle and its state can be checked before the next controller call.
        if isinstance(s, SessionProxy):
            s.session = observed
        elif ref.native_iteration(s) != end:
            raise RuntimeError('Original client channel remains unavailable; saved endpoint is ready for controller restart')
        return met


def configure():
    ref.OUT = ref.ROOT_OUT = OUT
    ref.WORK = ref.ROOT_WORK = WORK
    ref.MANIFEST = OUT / 'run-manifest.json'
    ref.SOURCE = SOURCE
    ref.attach = source.attach
    ref.collect = collect
    ref.block = block
    OUT.mkdir(parents=True, exist_ok=True)


def resume_folder(m):
    ref.OUT = Path(m.get('active_output', str(OUT)))
    ref.WORK = PureWindowsPath(m.get('active_work', str(WORK)))


def compare(arms, reference_label, candidate_label, step, context):
    left, right = arms[reference_label], arms[candidate_label]
    a, b = np.load(left['fields']), np.load(right['fields'])
    if not np.allclose(a['centroids'], b['centroids'], atol=1e-12, rtol=0):
        raise RuntimeError('Matched-time facet correspondence differs')
    if not math.isclose(left['metrics']['film_time_s'], right['metrics']['film_time_s'], abs_tol=1e-12):
        raise RuntimeError('Matched-time clocks differ')
    mass = a['film-mass']
    av = np.stack([a[f'film-{axis}-velocity'] for axis in 'xyz'], axis=1)
    bv = np.stack([b[f'film-{axis}-velocity'] for axis in 'xyz'], axis=1)
    alternative = any(x['metrics']['inner_reporting'] == 'UNAVAILABLE_ALTERNATIVE_IMPLICIT' for x in [left, right])
    q = {'mass_distribution_L1_percent': float(100*np.sum(np.abs(b['film-mass']-mass))/np.sum(mass)),
         'mass_weighted_velocity_difference_percent': float(100*np.sum(mass*np.linalg.norm(bv-av,axis=1))/max(np.sum(mass*np.linalg.norm(av,axis=1)),1e-30)),
         'maximum_thickness_difference_percent': float(100*abs(np.max(b['film-thickness'])-np.max(a['film-thickness']))/np.max(a['film-thickness'])),
         'drainage_difference_over_accretion_percent': float(100*abs(right['metrics']['drainage_kg_s']-left['metrics']['drainage_kg_s'])/max(abs(left['metrics']['accretion_kg_s']),1e-30)),
         'film_time_s': right['metrics']['film_time_s'], 'qualified_fixed_step_s': step,
         'reference_step_s': left['metrics']['printed_step_max_s'], 'equations': context,
         'inner_residuals': 'UNAVAILABLE_NOT_COUNTED_AS_PASS' if alternative else 'ORIGINAL_IMPLICIT_COMPLETE'}
    q['pass'] = bool(q['mass_distribution_L1_percent'] <= 1 and q['mass_weighted_velocity_difference_percent'] <= 2
        and q['maximum_thickness_difference_percent'] <= 2 and q['drainage_difference_over_accretion_percent'] <= 1
        and all(x['metrics']['within_recovery_bounds'] and x['metrics']['film_ledger_error_percent'] <= .1
                and (x['metrics']['eligible_for_step_increase'] or x['metrics']['inner_reporting'] == 'UNAVAILABLE_ALTERNATIVE_IMPLICIT') for x in [left, right]))
    return q


def endpoint_source(arm):
    return {'pair': dict(arm['pair']),
            'endpoint': str(Path(arm['metrics']['output']) / f"endpoint-N{arm['pair']['native_iteration']}.json")}


def qualified(m, met):
    return bool(met['within_recovery_bounds'] and met['film_ledger_error_percent'] <= .1
        and (met['eligible_for_step_increase'] or (m.get('alternative_method_qualification', {}).get('pass')
             and met['inner_reporting'] == 'UNAVAILABLE_ALTERNATIVE_IMPLICIT')))


def qualify_alternative(s, m, origin):
    """Recover with the reference alternative solver, never infer inner passes."""
    arms = {}
    token = uuid.uuid4().hex[:8]
    for name, step, updates in [('reference', .5e-6, 1000), ('candidate', 5e-6, 100)]:
        ref.restore_branch(s, m, origin, f'alternative-{name}-{token}')
        ref.controls(s, m, {'implicit-scheme-new?': True, 'ewf-adaptive?': False,
                            'timestep-max': step, 'sub-iter-nums': 30})
        arms[name] = capture(s, m, ref.block(s, m, updates), 'matched-alternative-fields')
    if arms['reference']['metrics']['updates'] != 1000 or arms['candidate']['metrics']['updates'] != 100:
        q = {'pass': False, 'reason': 'Alternative matched-time arm stopped by numerical guard'}
    else:
        q = compare(arms, 'reference', 'candidate', 5e-6, 'IDENTICAL_RECOVERY_PARENT_BULK_FIELDS')
    m['alternative_method_qualification'] = q
    ref.dump(OUT / f'alternative-method-screen-{token}.json', {'source': origin, 'arms': arms, 'comparison': q})
    ref.dump(ref.MANIFEST, m)
    if q['pass']:
        ref.restore_branch(s, m, endpoint_source(arms['candidate']), 'alternative-development-' + token)
        return 5e-6
    raise RuntimeError('Alternative numerical method failed its field/ledger comparison; both arms preserved')


def capture(s, m, met, label=None):
    arrays, path = ref.film_fields(s, label or f"film-fields-N{met['native_end']}")
    if not math.isclose(float(np.sum(arrays['film-mass'])), met['film_mass_kg'], rel_tol=2e-6, abs_tol=1e-9):
        raise RuntimeError('Native facet mass/report differs')
    met.update(facet_fields=path, field_coverage='FINITE_NONNEGATIVE_THICKNESS')
    ref.dump(ref.MANIFEST, m)
    return {'metrics': met, 'fields': path, 'pair': dict(m['latest_pair'])}


def publish(m, met, frozen, accepted=False, persist=True):
    """Refresh the owning result and figures from qualified checkpoints."""
    trace = m.setdefault('accepted_development_trace', [])
    if accepted and (not trace or met['film_time_s'] > trace[-1]['film_time_s']):
        trace.append({k: met[k] for k in ['film_time_s', 'film_mass_kg', 'accretion_kg_s',
                      'drainage_kg_s', 'film_ledger_error_percent', 'native_end']})
    if trace:
        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        times = [v['film_time_s']*1000 for v in trace]
        axes[0].plot(times, [v['film_mass_kg'] for v in trace], 'o-', color='tab:blue')
        axes[0].set_ylabel('Film mass (kg)')
        axes[1].plot(times, [v['accretion_kg_s'] for v in trace], 'o-', label='Accretion')
        axes[1].plot(times, [v['drainage_kg_s'] for v in trace], 'o-', label='Drainage')
        axes[1].set_ylabel('Liquid rate (kg/s)')
        axes[1].set_xlabel('Native film time (ms)')
        axes[1].legend()
        for ax in axes:
            ax.grid(alpha=.25)
        fig.suptitle('154k vertical-slit film development — qualified checkpoint windows')
        fig.tight_layout()
        fig.savefig(OUT / 'film-development.png', dpi=160)
        plt.close(fig)
    fields = met.get('facet_fields')
    if fields:
        data = np.load(fields)
        coords = data['centroids']
        angle = np.degrees(np.arctan2(coords[:, 2], coords[:, 0]))
        fig, ax = plt.subplots(figsize=(9, 4.5))
        view = ax.scatter(angle, coords[:, 1], c=data['film-thickness']*1000, s=5, cmap='viridis', vmin=0)
        fig.colorbar(view, ax=ax, label='Film thickness (mm)')
        ax.set(xlabel='Angle about the vertical y axis (degrees)', ylabel='Native y coordinate (m)',
               title=f"Wall film at {met['film_time_s']*1000:.3f} ms; N{met['native_end']}")
        fig.tight_layout()
        fig.savefig(OUT / 'wall-film-thickness.png', dpi=160)
        plt.close(fig)
    relative = Path(__import__('os').path.relpath(OUT, RESULTS.parent)).as_posix()
    rows = [('# Vertical-slit film development — current evidence\n\n'),
            '| Measure | Verified checkpoint |\n| --- | --- |\n',
            f"| Controller status | {m['status']} |\n",
            f"| Endpoint | N{met['native_end']}; paired save/reopen PASS |\n",
            f"| Native film time | {met['film_time_s']*1000:.6f} ms |\n",
            f"| Film mass | {met['film_mass_kg']:.6f} kg |\n",
            f"| Numerical qualification | {qualified(m, met)} |\n",
            f"| Bulk equations | {'Frozen; provisional film result' if frozen else 'All original equations active'} |\n",
            f"| Actual step | {met['final_accepted_step_s']*1e6:.6f} µs |\n",
            f"| Peak film Courant in window | {met['peak_film_cfl']:.6f} |\n",
            f"| Inner-film tolerance passes | {str(met['inner_pass_percent'])+'%' if met['inner_pass_percent'] is not None else 'Unavailable, not counted as passes'}; {met['inner_reporting']} |\n",
            f"| Terminal inner residuals above 1 | {met['inner_above_1_count'] if met['inner_above_1_count'] is not None else 'Unavailable'} |\n",
            f"| Film ledger error | {met['film_ledger_error_percent']:.6f}% |\n",
            f"| Accretion / drainage | {met['accretion_kg_s']:.6f} / {met['drainage_kg_s']:.6f} kg/s |\n",
            f"| Storage / drainage deficit | {met['storage_kg_s']:.6f} kg/s / {met['drainage_deficit_percent']:.6f}% |\n",
            f"| Maximum thickness in window | {met['maximum_thickness_m']*1000:.6f} mm |\n",
            f"| Steady-film screen | {m.get('steady_film', False)}; whole-separator qualification remains separate |\n",
            f"| Evidence | [Manifest]({relative}/run-manifest.json); [live supervision]({relative}/live-supervision.json); [setup](setup.md) |\n"]
    if trace:
        rows.append(f'\n![Film mass and transfer rates]({relative}/film-development.png)\n\nQualified development windows only; matched-time reference arms and rejected updates are excluded.\n')
    if fields:
        rows.append(f'\n![Wall film thickness]({relative}/wall-film-thickness.png)\n\nNative wall-facet values; angular projection can overlap non-cylindrical wall faces.\n')
    RESULTS.write_text(''.join(rows))
    if persist:
        ref.dump(ref.MANIFEST, m)


def grow(s, m, step_us):
    ref.restore_half(s, m, {'ewf-adaptive?': False, 'timestep-max': step_us/1e6,
                          'sub-iter-nums': 30}, f'matched-time-{step_us}us', frozen=True)
    arm = capture(s, m, ref.block(s, m, round(500/step_us)), 'matched-film-fields')
    arms = {'reference': m['sensitivity_arms']['conservative'], 'candidate': arm}
    if arm['metrics']['updates'] != round(500/step_us):
        q = {'pass': False, 'qualified_fixed_step_s': step_us/1e6,
             'reason': 'Candidate interrupted by live numerical guard; unequal horizon is excluded'}
    else:
        q = compare(arms, 'reference', 'candidate', step_us/1e6, 'FROZEN_IDENTICAL_154K_N5080_BULK_FIELDS')
    m.setdefault('step_screens', []).append({'comparison': q, 'arm': arm})
    if q['pass']:
        m['alternative_sensitivity'] = q
        m['selected_step_arm'] = arm
    m.update(status='MATCHED_TIME_SENSITIVITY_PASS' if q['pass'] else 'MATCHED_TIME_SENSITIVITY_RECOVERY_REQUIRED', active_target=None)
    ref.dump(OUT / f'matched-time-sensitivity-{step_us}us.json', {'comparison': q, 'arms': arms})
    ref.dump(ref.MANIFEST, m)
    print('STEP_SCREEN', json.dumps(q), flush=True)
    return q['pass']


def developed_screen(s, m, step, frozen):
    """Recheck the current developed fields over equal added film time."""
    source_point = endpoint_source({'pair': m['latest_pair'], 'metrics': m['latest_metrics']})
    arms = {}
    token = uuid.uuid4().hex[:8]
    for name, dt, updates in [('reference', step/5, 1000), ('candidate', step, 200)]:
        ref.restore_branch(s, m, source_point, f'developed-{name}-{token}')
        ref.controls(s, m, {'ewf-adaptive?': False, 'timestep-max': dt})
        arms[name] = capture(s, m, ref.block(s, m, updates), 'matched-film-fields')
    if arms['reference']['metrics']['updates'] != 1000 or arms['candidate']['metrics']['updates'] != 200:
        q = {'pass': False, 'qualified_fixed_step_s': step,
             'reason': 'Numerically interrupted matched-time arm; unequal horizon is excluded'}
    else:
        q = compare(arms, 'reference', 'candidate', step,
                    'FROZEN_IDENTICAL_DEVELOPED_BULK_FIELDS' if frozen else 'FULL_BULK_EQUAL_FILM_TIME_DIFFERENT_CARRIER_UPDATES')
    ref.dump(OUT / f'developed-step-screen-{token}.json', {'source': source_point, 'arms': arms, 'comparison': q})
    m.setdefault('developed_step_screens', []).append({'source': source_point, 'arms': arms, 'comparison': q})
    ref.dump(ref.MANIFEST, m)
    return q, arms, source_point


def supervise(s, m, resume_existing=False):
    """Run qualified film batches, recover smaller steps and restore bulk."""
    if not m.get('alternative_sensitivity', {}).get('pass'):
        raise RuntimeError('Initial matched-time screen must pass first')
    if resume_existing:
        if ref.native_iteration(s) != m['verified_native_end'] or not s.settings.solution.run_calculation.iterate.is_active():
            raise RuntimeError('Handoff must start from a verified idle checkpoint')
        expected = json.loads((ref.OUT / f"endpoint-N{m['verified_native_end']}.json").read_text())
        ref.require_match(ref.readback(s), expected['state']['readback'])
        if ref.film(s) != expected['film']:
            raise RuntimeError('Handoff film clock differs from verified endpoint')
        step = ref.film(s)['film_timestep']
        frozen = 'bulk-equations' in m['controlled_delta'] and not any(m['controlled_delta']['bulk-equations'].values())
        phase_start = m.get('full_bulk_start_film_time_s', m['parent_film_time_s'])
        next_review = max(.01, ref.film(s)['film_elapsed_time'])
    else:
        publish(m, m['latest_metrics'], True)
        m.setdefault('selected_step_arm', m['sensitivity_arms']['candidate'])
        for step_us in [10, 20, 50]:
            if step_us/1e6 > m['alternative_sensitivity']['qualified_fixed_step_s'] and not grow(s, m, step_us):
                break
        selected = m['selected_step_arm']
        step = m['alternative_sensitivity']['qualified_fixed_step_s']
        ref.restore_branch(s, m, endpoint_source(selected), 'film-development-' + uuid.uuid4().hex[:8])
        ref.controls(s, m, {'ewf-adaptive?': False, 'timestep-max': step})
        phase_start = ref.film(s)['film_elapsed_time']
        frozen, next_review = True, .01
    recoveries = max(m.get('step_recovery_count', 0), sum(not qualified(m, b) for b in m['blocks'] if b['updates'] > 100))
    begun = time.monotonic()
    next_full_bulk_review = m.get('full_bulk_start_film_time_s', phase_start) + .1
    if resume_existing and recoveries >= 2 and not m['controlled_delta'].get('implicit-scheme-new?', False):
        origin = endpoint_source({'pair': m['latest_pair'], 'metrics': m['latest_metrics']})
        step = qualify_alternative(s, m, origin)
        next_review = max(.01, ref.film(s)['film_elapsed_time'])
    for unused in range(500):
        if time.monotonic()-begun >= 24*3600:
            m.update(status='WALL_TIME_REVIEW_REQUIRED', active_target=None, steady_film=False)
            ref.dump(ref.MANIFEST, m)
            return
        if (OUT / 'stop-request.json').exists():
            request = json.loads((OUT / 'stop-request.json').read_text())
            m.update(status='CONTROLLER_HANDOFF_READY' if request.get('requested_by') == 'codex_technical_handoff' else 'USER_STOPPED_AT_CHECKPOINT', active_target=None)
            ref.dump(ref.MANIFEST, m)
            return
        previous = endpoint_source({'pair': m['latest_pair'], 'metrics': m['latest_metrics']})
        met = ref.block(s, m, 1000)
        capture(s, m, met)
        good = qualified(m, met)
        publish(m, met, frozen, accepted=good)
        if not good:
            while not good:
                recoveries += 1
                m['step_recovery_count'] = recoveries
                if (recoveries >= 2 or step <= .25e-6) and not m['controlled_delta'].get('implicit-scheme-new?', False):
                    step = qualify_alternative(s, m, previous)
                    good = True
                    break
                if recoveries > 16 or step <= .125e-6:
                    m.update(status='NUMERICAL_METHOD_RECOVERY_REQUIRED', numerical_recovery_parent=previous,
                             reason='Original and alternative methods exhausted conservative recovery range', active_target=None)
                    ref.dump(ref.MANIFEST, m)
                    return
                ref.restore_branch(s, m, previous, 'smaller-step-recovery-' + uuid.uuid4().hex[:8])
                step /= 2
                ref.controls(s, m, {'ewf-adaptive?': False, 'timestep-max': step})
                probe = ref.block(s, m, 100)
                capture(s, m, probe)
                good = qualified(m, probe)
                publish(m, probe, frozen, accepted=good)
            continue
        m['last_numerically_adequate_pair'] = dict(m['latest_pair'])
        tail = [b for b in m['blocks'] if b.get('output') == str(ref.OUT)][-3:]
        stationary = len(tail) == 3 and all(b['updates'] == 1000
            and qualified(m, b)
            and abs(b['drainage_deficit_percent']) <= 1
            and abs(b['storage_kg_s'])/max(abs(b['accretion_kg_s']),1e-30) <= .01 for b in tail)
        if frozen and (stationary or met['film_time_s'] >= next_review):
            q, arms, origin = developed_screen(s, m, step, True)
            if not q['pass']:
                step /= 2
                if step < .25e-6:
                    m.update(status='NUMERICAL_METHOD_RECOVERY_REQUIRED', numerical_recovery_parent=origin,
                             reason='Developed-state matched-time screens fail at conservative steps', active_target=None)
                    ref.dump(ref.MANIFEST, m)
                    return
                ref.restore_branch(s, m, origin, 'developed-step-recovery-' + uuid.uuid4().hex[:8])
                ref.controls(s, m, {'ewf-adaptive?': False, 'timestep-max': step})
                continue
            ref.restore_branch(s, m, endpoint_source(arms['candidate']), 'reviewed-development-' + uuid.uuid4().hex[:8])
            next_review = ref.film(s)['film_elapsed_time'] + .05
            if stationary or ref.film(s)['film_elapsed_time'] >= .5:
                original = json.loads((OUT / 'parent-state.json').read_text())['state']['readback']['controls']['equations']
                clock_before = ref.film(s)
                fields_before = ref.readback(s)['fields']
                equations = s.settings.solution.controls.equations
                for key, value in original.items():
                    equations[key] = value
                if equations.get_state() != original or ref.film(s) != clock_before:
                    raise RuntimeError('Full bulk restoration changed the native film state')
                ref.require_match({'fields': ref.readback(s)['fields']}, {'fields': fields_before})
                m['controlled_delta'].pop('bulk-equations')
                ref.controls(s, m, {})
                m['bulk_equations_restored'] = original
                frozen = False
                phase_start = ref.film(s)['film_elapsed_time']
                m['full_bulk_start_film_time_s'] = phase_start
                ref.dump(ref.MANIFEST, m)
        elif not frozen and stationary:
            spatial = ref.spatial_stationarity(m, ref.OUT)
            if spatial['pass']:
                q, arms, origin = developed_screen(s, m, step, False)
                m.update(status='FULL_BULK_FILM_STATIONARITY_SCREEN' if q['pass'] else 'FULL_BULK_STEP_REVIEW_REQUIRED',
                         steady_film=bool(q['pass']), spatial_stationarity=spatial,
                         full_bulk_matched_time_screen=q, active_target=None)
                publish(m, m['latest_metrics'], False)
                ref.dump(ref.MANIFEST, m)
                return
        if not frozen and met['film_time_s'] >= next_full_bulk_review:
            m.setdefault('full_bulk_horizon_reviews', []).append({'film_time_s': met['film_time_s'],
                 'native_end': met['native_end'], 'numerically_qualified': good,
                 'storage_kg_s': met['storage_kg_s'], 'drainage_deficit_percent': met['drainage_deficit_percent']})
            next_full_bulk_review = met['film_time_s'] + .1
            ref.dump(ref.MANIFEST, m)
        if not frozen and met['film_time_s']-phase_start >= 1:
            m.update(status='FULL_BULK_HORIZON_REVIEW_REQUIRED', steady_film=False, active_target=None)
            publish(m, met, False)
            ref.dump(ref.MANIFEST, m)
            return
    m.update(status='UPDATE_BUDGET_REVIEW_REQUIRED', steady_film=False, active_target=None)
    ref.dump(ref.MANIFEST, m)


def prepare(s):
    if ref.MANIFEST.exists():
        raise RuntimeError('Reconcile the existing film-development manifest')
    if not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Server 3 is active; do not replace a running case')
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors']:
        ref.ensure_remote_directory(s, str(folder))
    parent = json.loads(SOURCE.read_text())
    for kind in ['case', 'data']:
        digest = ref.remote_file_sha256(s, parent['pair'][kind], str(WORK / 'scratch' / f'source-{kind}.sha256'))
        if digest != parent['pair'][kind + '_sha256']:
            raise RuntimeError('154k parent hash differs: ' + kind)
    # The unrelated historical case has a different native iteration expression.
    historical = int(s.settings.setup.named_expressions['Hist08bIteration'].get_value())
    original_iteration = pairs.native_iteration
    try:
        pairs.native_iteration = lambda solver: historical
        preserved = pairs.pair_save(s, WORK / f'previous-server3-N{historical}.cas.h5', WORK / 'scratch', scratch_tag='previous')
    finally:
        pairs.native_iteration = original_iteration
    ref.dump(OUT / 'preserved-previous-server3.json', preserved)
    s.settings.file.read_case(file_name=parent['pair']['case'])
    s.settings.file.read_data(file_name=parent['pair']['data'])
    current = ref.state(s)
    ref.require_match(current['readback'], parent['state']['readback'])
    if ref.native_iteration(s) != 5080 or not math.isclose(ref.film(s)['film_elapsed_time'], .0035, abs_tol=1e-12):
        raise RuntimeError('Restored 154k parent iteration/film clock differs')
    m = {'status': 'PREPARING', 'server_id': '3',
         'authority': 'human_20261006_overwrite_server3_develop_wall_film_continuously',
         'parent_native_iteration': 5080, 'parent_pair': parent['pair'], 'work_root': str(WORK),
         'preserved_previous_endpoint': preserved, 'parent_film_time_s': ref.film(s)['film_elapsed_time'],
         'film_time_review_s': [.01, .05, .1, .2, .5], 'max_segment_updates': 200000,
         'segment_film_horizon_s': .5, 'blocks': [], 'control_trials': [], 'controlled_delta': {},
         'verified_native_end': 5080, 'solver_left_open': True, 'steady_film': False,
         'bulk_and_film_initialization': 'FORBIDDEN', 'mesh': 'Separator-vertical-slit-154k.msh.h5'}
    ref.dump(ref.MANIFEST, m)
    m['preserved_parent'] = ref.save(s, 'preserved-parent-N5080')
    ref.dump(OUT / 'parent-state.json', {'state': current, 'film': ref.film(s), 'pair': m['preserved_parent']})
    m['report_paths'] = ref.instrument(s, WORK / 'monitors')
    s.settings.file.auto_save.data_frequency = 0
    ref.controls(s, m, {'sub-iter-nums': 30})
    ref.film_fields(s, 'parent-film-fields-N5080')
    m.update(status='PREPARED_VERIFIED', prepared_reopen='PASS')
    ref.dump(ref.MANIFEST, m)
    return m


def screen(s, m):
    """Qualify 5 us with the original implicit solver, at identical forcing."""
    arms = {}
    for label, step, count in [('conservative', .5e-6, 1000), ('candidate', 5e-6, 100)]:
        ref.restore_half(s, m, {'ewf-adaptive?': False, 'timestep-max': step,
                              'sub-iter-nums': 30}, 'matched-time-' + label, frozen=True)
        met = ref.block(s, m, count)
        _, path = ref.film_fields(s, 'matched-film-fields')
        arms[label] = {'metrics': met, 'fields': path, 'pair': m['latest_pair']}
        m['sensitivity_arms'] = arms
        ref.dump(ref.MANIFEST, m)
    a, b = [np.load(arms[label]['fields']) for label in ['conservative', 'candidate']]
    if not np.allclose(a['centroids'], b['centroids'], atol=1e-12, rtol=0):
        raise RuntimeError('Matched-time facet correspondence differs')
    if not math.isclose(arms['conservative']['metrics']['film_time_s'], arms['candidate']['metrics']['film_time_s'], abs_tol=1e-12):
        raise RuntimeError('Matched-time clocks differ')
    mass = a['film-mass']
    av = np.stack([a[f'film-{axis}-velocity'] for axis in 'xyz'], axis=1)
    bv = np.stack([b[f'film-{axis}-velocity'] for axis in 'xyz'], axis=1)
    q = {'mass_distribution_L1_percent': float(100*np.sum(np.abs(b['film-mass']-mass))/np.sum(mass)),
         'mass_weighted_velocity_difference_percent': float(100*np.sum(mass*np.linalg.norm(bv-av,axis=1))/max(np.sum(mass*np.linalg.norm(av,axis=1)),1e-30)),
         'maximum_thickness_difference_percent': float(100*abs(np.max(b['film-thickness'])-np.max(a['film-thickness']))/np.max(a['film-thickness'])),
         'film_time_s': arms['candidate']['metrics']['film_time_s'], 'qualified_fixed_step_s': 5e-6,
         'reference_step_s': .5e-6, 'equations': 'FROZEN_IDENTICAL_154K_N5080_BULK_FIELDS',
         'inner_residuals': 'ORIGINAL_IMPLICIT_COMPLETE'}
    q['pass'] = bool(q['mass_distribution_L1_percent'] <= 1 and q['mass_weighted_velocity_difference_percent'] <= 2
                     and q['maximum_thickness_difference_percent'] <= 2
                     and all(x['metrics']['eligible_for_step_increase'] and x['metrics']['within_recovery_bounds'] for x in arms.values()))
    m['alternative_sensitivity'] = q
    m.update(status='MATCHED_TIME_SENSITIVITY_PASS' if q['pass'] else 'MATCHED_TIME_SENSITIVITY_RECOVERY_REQUIRED', active_target=None)
    ref.dump(OUT / 'matched-time-sensitivity.json', {'comparison': q, 'arms': arms})
    ref.dump(ref.MANIFEST, m)
    print('MATCHED_TIME_SCREEN', json.dumps(q), flush=True)


def main():
    configure()
    s = SessionProxy(source.attach())
    try:
        operation = sys.argv[1]
        if '--watcher-gate' in sys.argv:
            ref.dump(OUT / 'controller-online.json', {'controller_pid': os.getpid(),
                     'execution_host': 'SERVER3_WINDOWS', 'native_iteration': ref.native_iteration(s),
                     'status': 'WAITING_FOR_CACHED_NUMERICAL_GUARD'})
            ready = False
            for unused in range(300):
                path = OUT / 'watcher-ready.json'
                if path.exists():
                    receipt = json.loads(path.read_text())
                    if receipt.get('controller_pid') == os.getpid() and receipt.get('cached_interrupt_channel'):
                        ready = True
                        break
                time.sleep(1)
            if not ready:
                raise RuntimeError('Cached numerical watcher did not become ready; no solve submitted')
        if operation == 'prepare':
            m = prepare(s)
        else:
            m = json.loads(ref.MANIFEST.read_text())
            resume_folder(m)
            if operation == 'probe':
                met = ref.block(s, m, 100)
                _, path = ref.film_fields(s, f"film-fields-N{met['native_end']}")
                met['facet_fields'] = path
                ref.dump(ref.MANIFEST, m)
            elif operation == 'develop':
                ref.develop(s, m)
            elif operation == 'screen':
                screen(s, m)
            elif operation == 'supervise':
                supervise(s, m)
            elif operation == 'resume-supervise':
                supervise(s, m, resume_existing=True)
            else:
                raise ValueError(operation)
        if operation in ['supervise', 'resume-supervise'] and m.get('latest_metrics'):
            frozen = 'bulk-equations' in m['controlled_delta'] and not any(m['controlled_delta']['bulk-equations'].values())
            publish(m, m['latest_metrics'], frozen)
        print(json.dumps({'status': m['status'], 'native_iteration': ref.native_iteration(s), 'film': ref.film(s), 'metrics': m.get('latest_metrics')}, default=str), flush=True)
    except Exception:
        if ref.MANIFEST.exists():
            m = json.loads(ref.MANIFEST.read_text())
            m.update(status='RECONCILIATION_REQUIRED', error=traceback.format_exc(), failure_utc=datetime.now(timezone.utc).isoformat())
            ref.dump(ref.MANIFEST, m)
        raise


if __name__ == '__main__':
    main()
