"""Read-only local supervision of a running Phase 7b controller; no Fluent client.

Only checkpoint-complete scalar copies are consumed. Independently streamed
histories may differ by one iteration while the synchronous callback completes.
The caller owns scientific interpretation and phase-state updates.
"""
import argparse
from datetime import datetime,timezone
import fcntl
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
from analyze_phase07b_screen import parse_history,parse_residuals,derive,expected_residual_equations


def read_json(path):
    # A controller updates its small mutable manifest in place.
    for attempt in range(5):
        try:return json.loads(path.read_text())
        except json.JSONDecodeError:
            if attempt==4:raise
            time.sleep(.05)


def jsonl_prefix(path):
    text=path.read_text();lines=text.splitlines()
    incomplete=bool(text and not text.endswith('\n'))
    if incomplete:lines=lines[:-1]
    rows=[json.loads(line) for line in lines]
    assert [x['iteration'] for x in rows]==list(range(1,len(rows)+1)),path
    return rows,incomplete


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('run',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--terminal',action='store_true');a=ap.parse_args()
    run=a.run;m=read_json(run/'manifest.json')
    assert m['status']==('HORIZON_COMPLETE_ANALYSIS_PENDING' if a.terminal else 'RUNNING') and not m.get('error'), 'Reconcile changed controller disposition'
    if a.terminal:
        assert m['completed_iterations']==5000 and 'final' in m['pairs']
        assert not m['flux_monitor']['registered'] and m['flux_monitor']['error'] is None
    base=Path(__file__).resolve().parents[2]
    lock=(base/'output/phase07b-server1-controller.lock').open('a+')
    held=False
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        fcntl.flock(lock,fcntl.LOCK_UN)
    except BlockingIOError:held=True
    assert held != a.terminal, 'Reconcile controller lock state'
    flux,flux_partial=jsonl_prefix(run/'collector-flux.jsonl')
    speed,speed_partial=jsonl_prefix(run/'spike-diagnostics/spike-history.jsonl')
    assert flux and speed
    assert all(np.isfinite(row[k]) for row in flux for k in ['delivery_kg_s','escape_kg_s','net_outward_kg_s'])
    assert all(np.isfinite(row['max_speed_m_s']) for row in speed)
    residual,ra=parse_residuals(run/'solve.trn')
    expected={'iteration'} | expected_residual_equations(m)
    assert set(residual)==expected and not ra['conflicting_indices'] and not ra['nonfinite_columns']
    assert np.array_equal(residual['iteration'],np.arange(1,len(residual['iteration'])+1))
    common=min(len(flux),len(speed),int(residual['iteration'][-1]))
    checkpoint=5000 if a.terminal else max(int(tag[1:]) for tag in m['pairs'] if tag.startswith('n') and tag[1:].isdigit())
    if a.terminal:
        assert common==len(flux)==len(speed)==len(residual['iteration'])==5000
        assert {f'n{n:05d}' for n in [50]+list(range(500,5000,500))}.issubset(m['pairs'])
    h,ha=parse_history(run/f'history-{checkpoint:05d}.out');d,_=derive(h)
    assert np.array_equal(h['iteration'],np.arange(1,checkpoint+1))
    assert not ha['conflicting_indices'] and not ha['nonfinite_columns']
    assert checkpoint<=common
    lag=float(np.max(np.abs(d['native_applied_removal'][1:]-d['current_expression_removal'][:-1])))
    assert any(row['iteration']==checkpoint and row['matches_local'] for row in m['remote_flux_readbacks'])
    dm=read_json(run/'spike-diagnostics/manifest.json');assert dm['error'] is None
    verified=[]
    nphase=m.get('selected_methods',{}).get('p_v_coupling',{}).get('solve_n_phase',False)
    inventory_policy={'mode':'cellwise_normalized_raw_phase_vector' if nphase else 'raw_secondary_volume_fraction',
                      'relative_tolerance':1e-9 if nphase else 1e-10,'absolute_tolerance_m3':1e-12,
                      'basis':'N-phase snapshot monitor native-volume parity tolerance' if nphase else 'existing audit tolerance'}
    with np.load(run/'spike-diagnostics/geometry.npz') as geometry:
        for snap in dm['snapshots']:
            path=Path(snap['path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==snap['sha256']
            meta=read_json(path.with_suffix('.json'));assert meta['iteration']==snap['iteration'] and meta['same_iteration_before_after']
            with np.load(path) as fields:
                assert all(np.isfinite(fields[k]).all() for k in fields.files)
                native={
                    'speed':max(float(np.sqrt(sum(fields[f'z{i}_mixture_SV_{axis}']**2 for axis in 'UVW')).max()) for i in range(2)),
                    'k':max(float(fields[f'z{i}_mixture_SV_K'].max()) for i in range(2)),
                    'epsilon':max(float(fields[f'z{i}_mixture_SV_D'].max()) for i in range(2)),
                    'water':sum(float(np.dot(fields[f'z{i}_phase-2_SV_VOF'],geometry[f'z{i}_mixture_SV_VOLUME'])) for i in range(2))}
                if nphase:
                    water=0.
                    for i in range(2):
                        alpha=fields[f'z{i}_phase-2_SV_VOF'];primary=f'z{i}_phase-1_SV_VOF'
                        if primary in fields:
                            total=alpha+fields[primary]
                            assert np.isfinite(total).all() and np.all(total>0), (snap['iteration'],primary)
                            alpha=alpha/total
                        else:
                            assert snap['iteration']==0 and np.all(alpha==0), 'Missing E6 primary raw phase field'
                        water+=float(np.dot(alpha,geometry[f'z{i}_mixture_SV_VOLUME']))
                    native['water']=water
                    if snap['iteration']:
                        assert meta['inventory_reconstruction']['mode']=='cellwise_normalized_raw_phase_vector'
                for key,value in native.items():
                    rtol=inventory_policy['relative_tolerance'] if key=='water' else 1e-10
                    assert math.isclose(value,meta['native'][key],rel_tol=rtol,abs_tol=1e-12), (snap['iteration'],key,value,meta['native'][key])
            verified.append(snap['iteration'])
    trn=(run/'solve.trn').read_text()
    fatal=[x for x in ['floating point exception','Divergence detected','SEGMENTATION VIOLATION','Traceback'] if x in trn]
    assert not fatal,fatal
    latest_utc=datetime.fromisoformat(speed[-1]['captured_utc']);now=datetime.now(timezone.utc)
    age=(now-latest_utc).total_seconds()
    expected_snapshots={0,50}|set(range(500,checkpoint+1,500))|{n for n in [2600,2700,2800] if n<=checkpoint}
    for row in speed:
        if row['iteration']<=checkpoint and row['snapshot_reasons']:expected_snapshots.add(row['iteration'])
    assert expected_snapshots.issubset(verified), 'Required checkpoint/event snapshot missing'
    result={'status':'TERMINAL_LOCAL_EVIDENCE_AUDIT_PASS' if a.terminal else 'RUNNING_LOCAL_EVIDENCE_AUDIT_PASS','utc':now.isoformat(),'run_id':m['run_id'],
            'controller_pid':m['controller_pid'],'controller_lock_held':held,'last_common_local_iteration':common,
            'last_flux_iteration':len(flux),'last_speed_iteration':len(speed),'last_residual_iteration':int(residual['iteration'][-1]),
            'latest_capture_utc':speed[-1]['captured_utc'],'capture_age_seconds':age,
            'scalar_complete_through':checkpoint,'paired_checkpoint_verified_through':checkpoint,
            'paired_case':m['pairs']['final' if a.terminal else f'n{checkpoint:05d}'],'pair_presence_basis':'Controller Fluent-API save and existence checks',
            'remote_checkpoint_flux_readback_exact':True,'verified_snapshots':verified,'diagnostic_error':None,
            'inventory_snapshot_validation':inventory_policy,
            'source_lag_max_abs_error_kg_s':lag,'source_lag_pairs':checkpoint-1,'fatal_markers':fatal,
            'last_speed_m_s':speed[-1]['max_speed_m_s'],'max_observed_speed_m_s':max(row['max_speed_m_s'] for row in speed),
            'incomplete_trailing_jsonl_ignored':{'flux':flux_partial,'speed':speed_partial},
            'scientific_warning': 'Investigate changed source update lag' if lag>1e-9 else None,
            'freshness_warning':'Capture has not updated in over five minutes; reconcile current step before any intervention' if age>300 and not a.terminal else None,
            'claim_limit':'Recording audit only, not numerical adequacy; phase-state and interpretation are maintained separately.'}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x') as file:json.dump(result,file,indent=2);file.write('\n')
    print(json.dumps(result))


if __name__=='__main__':main()
