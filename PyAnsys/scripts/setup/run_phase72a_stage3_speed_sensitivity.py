"""Monitored Server 1 campaign: reference, low and high speed to 500 ms film time.

Existing native-run helpers retain transcripts, reports and paired checkpoints.
The controller never declares 500 ms to be steady film and never initializes a
continued field. Other servers are outside this campaign's authority.
"""
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import json
import math
import os
import sys
import time
import traceback
import uuid

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts/setup')]
import continue_phase72a_stage3_film_development as c
from run_phase72a_stage3_server3 import state, powershell
from run_phase72a_local_film_replay import readback, require_match
from run_phase72a_e27_server1_continuation import dump, native_iteration
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256

CAMPAIGN = ROOT/'output/phase72a-stage3-speed-sensitivity-server1/20261006'
JOB = CAMPAIGN/'run-manifest.json'
BASE_ROOT = c.ROOT_OUT
BASE_WORK = c.ROOT_WORK
SPEEDS = [('reference', 26.81), ('low', 20.11), ('high', 32.14)]
HORIZON = .5


def event(job, status, **kwargs):
    job.update(status=status, updated_utc=datetime.now(timezone.utc).isoformat(), **kwargs)
    dump(JOB, job)
    print(status, json.dumps(kwargs, default=str), flush=True)


def bind(root, work):
    c.ROOT_OUT, c.ROOT_WORK = Path(root), PureWindowsPath(work)
    c.MANIFEST = c.ROOT_OUT/'run-manifest.json'
    m = json.loads(c.MANIFEST.read_text())
    c.OUT = Path(m.get('active_output', str(root)))
    c.WORK = PureWindowsPath(m.get('active_work', str(work)))
    return m


def endpoint(m):
    return c.OUT/f"endpoint-N{m['verified_native_end']}.json"


def reconcile_completed(s, m, error):
    """Observe a submitted native batch and finish its receipt without re-solving."""
    start, end = m['verified_native_end'], m['active_target']
    if end is None:
        raise RuntimeError('No submitted native horizon to reconcile') from error
    while True:
        try:
            n = native_iteration(s)
            if n > end:
                raise RuntimeError('Unexpected extra native updates')
            if n == end:
                run = s.settings.solution.run_calculation
                if not run.iterate.is_active() and run.interrupt.is_active():
                    run.interrupt()
                if run.iterate.is_active():
                    break
        except Exception:
            time.sleep(10)
            s = c.attach()
        time.sleep(10)
    completed = c.OUT/f'completed-N{end}.json'
    if completed.exists():
        native = c.OUT/f'batch-N{start}-N{end}.trn'
        if not native.exists():
            s.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
            native.write_text(read_text(s, str(c.WORK/native.name)))
        c.reconcile_boundary(s, m)
        return s, m['latest_metrics']
    before = state(s)
    final = c.film(s)
    pair = c.save(s, f'recovered-N{end}-{uuid.uuid4().hex[:8]}')
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(readback(s), before['readback'])
    if c.film(s) != final:
        raise RuntimeError('Reopened native film state differs')
    s.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
    native = c.OUT/f'batch-N{start}-N{end}.trn'
    if not native.exists():
        native.write_text(read_text(s, str(c.WORK/native.name)))
    initial = json.loads((c.OUT/f'endpoint-N{start}.json').read_text())
    met = c.collect(s, m, start, end, initial['film'], final,
                    initial['state']['readback']['fields'], native)
    met.update(output=str(c.OUT), controls=dict(m['controlled_delta']), pair=pair,
               wall_seconds=None, film_ms_per_wall_minute=None, execution_repeated=False,
               communication_recovery=str(error), new_solve_calls=0)
    dump(c.OUT/f'endpoint-N{end}.json', {'pair':pair, 'state':state(s), 'film':final,
                                      'metrics':met, 'reopen':'PASS'})
    m['blocks'].append(met)
    m.update(status='BLOCK_COMPLETE', verified_native_end=end, latest_pair=pair,
             latest_metrics=met, active_target=None, final_reopen='PASS')
    dump(c.MANIFEST, m)
    print('NATIVE_BATCH_RECOVERED_NO_REPEAT', start, end, flush=True)
    return s, met


def batch(s, m, steps):
    try:
        met = c.block(s, m, steps)
    except Exception as error:
        print('RECONCILING_SUBMITTED_BATCH', repr(error), flush=True)
        s, met = reconcile_completed(s, m, error)
    met.setdefault('wall_seconds', None)
    met.setdefault('film_ms_per_wall_minute', None)
    # Verify the endpoint's native spatial film, separately from report smoothness.
    path = c.OUT/f"film-fields-N{met['native_end']}.npz"
    if path.exists():
        arrays = dict(np.load(path))
    else:
        arrays, _ = c.film_fields(s, path.stem)
    if not math.isclose(float(np.sum(arrays['film-mass'], dtype=float)), met['film_mass_kg'], rel_tol=2e-6, abs_tol=1e-9):
        raise RuntimeError('Facet inventory/report differs')
    met.update(facet_fields=str(path), field_coverage='FINITE_NONNEGATIVE_THICKNESS')
    m['latest_metrics'] = met
    receipt = json.loads(endpoint(m).read_text())
    receipt['metrics'] = met
    dump(endpoint(m), receipt)
    dump(c.MANIFEST, m)
    return s, met


def share_final(s, m, label):
    pair = m['latest_pair']
    folder = PureWindowsPath(r'C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\Stage3\speed-sensitivity-500ms\20261006')/label
    ensure_remote_directory(s, str(folder))
    shared = {}
    for kind, ext in [('case', 'cas.h5'), ('data', 'dat.h5')]:
        target = str(folder/f'{label}-500ms.{ext}')
        if not remote_file_exists(s, target):
            powershell(s, f"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath '{pair[kind]}' -Destination '{target}'")
        digest = remote_file_sha256(s, target, str(c.WORK/'scratch'/f'shared-{kind}-{uuid.uuid4().hex}.txt'))
        if digest != pair[kind+'_sha256']:
            raise RuntimeError('Shared final differs from preserved local pair')
        shared[kind] = {'path':target, 'sha256':digest}
    m.update(status='COMPLETE_500MS_LOCAL_REOPEN_SHARED_HASH_VERIFIED', shared_final=shared,
             film_horizon_s=HORIZON, active_target=None, idle=True, steady_film=False)
    dump(c.MANIFEST, m)
    return shared


def develop_to_horizon(s, m, job, label, speed, qualified_step):
    """Continue/recover in-scope; stationarity is an observation, not an early stop."""
    probe = True
    recovery_count = 0
    while c.film(s)['film_elapsed_time'] < HORIZON-1e-12:
        previous = {'pair':dict(m['latest_pair']), 'endpoint':str(endpoint(m))}
        remaining = HORIZON-c.film(s)['film_elapsed_time']
        current_step = c.film(s)['film_timestep']
        # Leave enough space for native growth; cut the last update to the target.
        steps = min(100 if probe else 1000, max(1, math.floor(remaining/max(current_step, 1e-12))))
        if steps == 1 and remaining < current_step:
            c.controls(s, m, {'ewf-adaptive?':False, 'timestep-max':remaining})
        event(job, 'RUNNING', active_case=label, nominal_speed_m_s=speed,
              film_time_s=c.film(s)['film_elapsed_time'], verified_native_end=m['verified_native_end'],
              active_target=m['verified_native_end']+steps, active_run_manifest=str(c.MANIFEST),
              active_client_transcript=str(c.OUT/f"batch-N{m['verified_native_end']}-N{m['verified_native_end']+steps}.txt"))
        s, met = batch(s, m, steps)
        # Inventory review bound scales with commanded throughput for the new arms.
        inventory_limit = 12.3*speed/26.81
        adequate = (met['peak_film_cfl'] <= 1 and met['maximum_thickness_m'] <= .003
                    and met['film_mass_kg'] <= inventory_limit and met['film_ledger_error_percent'] <= .1)
        large = c.exceeds_screened_step(met, qualified_step)
        if not adequate or large:
            recovery_count += 1
            m.setdefault('campaign_rejected_blocks', []).append(dict(met))
            c.restore_branch(s, m, previous, f'adaptive-campaign-recovery-{label}-{recovery_count}-N{previous["pair"]["native_iteration"]}')
            dt = min(current_step/2, qualified_step/2)
            c.controls(s, m, {'ewf-adaptive?':False, 'timestep-max':dt,
                             'sub-iter-nums':30, 'implicit-scheme-new?':True})
            s, repair = batch(s, m, 100)
            if repair['peak_film_cfl'] > 1 or repair['film_ledger_error_percent'] > .1:
                qualified_step = min(qualified_step, dt)
            c.controls(s, m, {'ewf-adaptive?':True, 'adapt-init-dt':dt,
                             'courant-number':max(.01, float(m['controlled_delta'].get('courant-number', .2))/2),
                             'adapt-tstp-inc':1.15, 'adapt-tstp-dec':2.0})
            probe = True
            event(job, 'NUMERICAL_RECOVERY_RUNNING', active_case=label,
                  rejected_native_end=met['native_end'], restart_native_end=previous['pair']['native_iteration'])
            continue
        probe = False
        m['last_numerically_adequate_pair'] = dict(m['latest_pair'])
        m.update(status='CAMPAIGN_CONTINUING_TO_500MS', active_target=None,
                 campaign_qualified_step_s=qualified_step)
        dump(c.MANIFEST, m)
        event(job, 'BATCH_VERIFIED', active_case=label, film_time_s=met['film_time_s'],
              verified_native_end=met['native_end'], film_mass_kg=met['film_mass_kg'],
              accepted_step_s=met['final_accepted_step_s'], peak_film_cfl=met['peak_film_cfl'],
              ledger_error_percent=met['film_ledger_error_percent'])
    elapsed = c.film(s)['film_elapsed_time']
    if abs(elapsed-HORIZON) > max(qualified_step, 1e-10):
        raise RuntimeError('500 ms endpoint exceeded by more than one qualified step')
    shared = share_final(s, m, label)
    job['cases'][label].update(status='COMPLETE_500MS', film_time_s=elapsed,
        native_iteration=m['verified_native_end'], pair=m['latest_pair'], shared=shared,
        run_manifest=str(c.MANIFEST), endpoint=str(endpoint(m)))
    event(job, 'CASE_COMPLETE', active_case=label, film_time_s=elapsed)
    return s


def main():
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    if JOB.exists():
        job = json.loads(JOB.read_text())
        if job.get('pause_requested'):
            print('PAUSED: explicit user resume and endpoint reconciliation required', flush=True)
            return
        if job['status'] == 'COMPLETE':
            return
    else:
        job = {'status':'PREPARING', 'server_id':'1', 'authority':'human_2026_10_06_three_inlet_speeds_500ms_continuous_monitoring',
               'film_horizon_s':HORIZON, 'runner':str(Path(__file__).resolve()), 'pid':os.getpid(),
               'cases':{label:{'status':'PENDING','nominal_speed_m_s':speed,
                              'liquid_feed_kg_s':116.92*speed/26.81,'vapor_feed_kg_s':80.69*speed/26.81}
                        for label,speed in SPEEDS},
               'comparison_limit':'Film development under separately developed, frozen bulk fields; 500 ms is not stationarity',
               'startup_parent':str(ROOT/'output/phase72a-stage3-early-ewf-server1/20261005/run-manifest.json')}
        dump(JOB, job)
    job['pid'] = os.getpid()
    dump(JOB, job)
    s = c.attach()
    try:
        for label, speed in SPEEDS:
            if job['cases'][label]['status'] == 'COMPLETE_500MS':
                continue
            if label == 'reference':
                m = bind(BASE_ROOT, BASE_WORK)
                if m.get('active_target') is not None:
                    s, _ = reconcile_completed(s, m, RuntimeError('Prior controller interrupted'))
                expected = json.loads(endpoint(m).read_text())
                if native_iteration(s) != m['verified_native_end']:
                    raise RuntimeError('Live reference differs from preserved parent')
                require_match(readback(s), expected['state']['readback'])
                if c.film(s) != expected['film']:
                    raise RuntimeError('Reference film clock differs')
                m.pop('transfer_receipt', None)
                m.update(status='CAMPAIGN_CONTINUING_TO_500MS', campaign_manifest=str(JOB))
                dump(c.MANIFEST, m)
                qualified = 20e-6
            else:
                # Imported only after the reference endpoint is preserved.
                from prepare_phase72a_stage3_speed_case import prepare_case
                s, m, qualified = prepare_case(s, job, label, speed)
            s = develop_to_horizon(s, m, job, label, speed, qualified)
        event(job, 'COMPLETE', active_case=None, active_target=None, server_idle=True,
              goal_claim='Three verified 500 ms film endpoints; no steady-model claim')
    except Exception:
        event(job, 'RECOVERY_REQUIRED', error=traceback.format_exc())
        raise
    finally:
        s._fluent_connection.exit_on_delete = False


if __name__ == '__main__':
    main()
