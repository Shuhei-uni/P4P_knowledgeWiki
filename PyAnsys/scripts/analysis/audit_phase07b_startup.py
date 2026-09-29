"""Local-only stage-aware E8 prefix/terminal audit. Never attaches to Fluent."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
import numpy as np

BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'scripts/setup'))
from run_phase07b_mixture_startup import parse_stage_residuals, conditioning_gate, verify_frozen_phase_arrays, ACTIVE_FLOW, ACTIVE_FULL
from analyze_phase07b_screen import parse_history, derive
from pyansys_fluent.phase07b_spike_monitor import SpikeSchedule


def rows(path):
    content=path.read_text(); assert content.endswith('\n'), ('Incomplete JSONL',path)
    data=[json.loads(line) for line in content.splitlines()]
    assert [x['iteration'] for x in data]==list(range(1,len(data)+1)), ('Prefix gap/conflict',path)
    return data


def verify_iteration_accounting(r, end):
    if 'start_iteration' not in r:
        assert r['iterations_issued']==end
        return
    assert r['start_iteration']==r['prefix_end']==50
    assert r['segment_iterations']==r['iterations_issued']==end-50
    assert r['retained_iterations']==end
    receipt=Path(r['recovery_receipt']['path'])
    assert hashlib.sha256(receipt.read_bytes()).hexdigest()==r['recovery_receipt']['sha256']
    evidence=json.loads(receipt.read_text())
    assert evidence['status']=='N50_PRESERVED_NATIVE_RECORDING_AND_SETTINGS_PASS'
    assert evidence['iteration']==50 and evidence['iterations_issued']==0 and not evidence['iterating']
    assert evidence['reloads_issued']==0 and not evidence['scientific_changes']
    parent=json.loads(Path(r['parent_manifest']).read_text())
    assert parent['run_id']==evidence['parent_run_id'] and parent['iterations_issued']==50


def audit(directory,terminal=False):
    r=json.loads((directory/'manifest.json').read_text()); assert r['experiment_id']=='E8'
    errors=[]; result={'run_id':r['run_id'],'checked_utc':datetime.now(timezone.utc).isoformat(),
                      'local_only':True,'terminal':terminal,'errors':errors,'manifest_status':r['status']}
    lock=(BASE/'output/phase07b-server1-controller.lock').open('r')
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB); result['controller_lock_free']=True
        fcntl.flock(lock,fcntl.LOCK_UN)
    except BlockingIOError: result['controller_lock_free']=False
    finally:lock.close()
    if terminal: assert result['controller_lock_free'], 'Controller still owns session'
    flux=rows(directory/'collector-flux.jsonl'); speed=rows(directory/'spike-diagnostics/spike-history.jsonl')
    for row in flux:
        assert all(np.isfinite(row[k]) for k in ['delivery_kg_s','escape_kg_s','net_outward_kg_s'])
        assert abs(row['delivery_kg_s']-row['escape_kg_s']+row['net_outward_kg_s'])<=1e-9
    assert all(np.isfinite(row['max_speed_m_s']) for row in speed)
    result.update(flux_end=len(flux),speed_end=len(speed))
    stage_results={}; residual_end=0
    for stage,item in r['residual_stages'].items():
        path=Path(item['local'])
        if terminal: path=Path(item['latest_native_snapshot'])
        end=0
        for line in path.read_text().splitlines():
            words=line.split()
            if words and words[0].isdigit() and len(words)>=8 and any(':' in w for w in words[7:]):end=max(end,int(words[0]))
        if end<=item['start_exclusive']:continue
        data,ra=parse_stage_residuals(path,stage,item['start_exclusive'],end)
        stage_results[stage]=ra; residual_end=max(residual_end,end)
    result['residual_stages']=stage_results;result['residual_end']=residual_end
    histories=sorted(directory.glob('history-*.out')); assert histories
    history,ha=parse_history(histories[-1]); end=int(history['iteration'][-1])
    assert np.array_equal(history['iteration'],np.arange(1,end+1))
    assert not ha['conflicting_indices'] and not ha['nonfinite_columns'] and not ha['rejected_lines']
    derived,_=derive(history)
    lag=float(np.max(abs(derived['native_applied_removal'][1:]-derived['current_expression_removal'][:-1])))
    assert lag<=1e-9
    result.update(scalar_end=end,scalar_source=str(histories[-1]),source_lag_pairs=end-1,source_lag_max_abs_error_kg_s=lag,
                  common_live_prefix_end=min(len(flux),len(speed),residual_end),common_scalar_prefix_end=min(end,len(flux),len(speed),residual_end))
    dm=json.loads((directory/'spike-diagnostics/manifest.json').read_text()); assert dm['error'] is None
    assert r.get('flux_monitor',{}).get('error') is None
    snapshots=dm['snapshots']; snapshot_by_index={v['iteration']:v for v in snapshots}
    assert len(snapshot_by_index)==len(snapshots)
    schedule=SpikeSchedule(); required={0}
    for row in speed:
        reasons=schedule.reasons(row['iteration'],row['max_speed_m_s'])
        assert row['snapshot_reasons']==reasons
        if reasons:required.add(row['iteration'])
    assert required<=set(snapshot_by_index), ('Missing scheduled/event snapshot',required-set(snapshot_by_index))
    assert set(snapshot_by_index)-required<=({r['switch_iteration']} if 'switch_iteration' in r else set())
    with np.load(directory/'spike-diagnostics/geometry.npz') as geometry:
        for n,snap in snapshot_by_index.items():
            path=directory/f'spike-diagnostics/fields-n{n:05d}.npz'
            assert hashlib.sha256(path.read_bytes()).hexdigest()==snap['sha256']
            meta=json.loads(path.with_suffix('.json').read_text()); assert meta['same_iteration_before_after']
            with np.load(path) as fields:
                assert all(np.isfinite(fields[k]).all() for k in fields.files)
                water=0.
                for i in range(len(r['fluid_zones'])):
                    a=fields[f'z{i}_phase-2_SV_VOF']; total=a+fields[f'z{i}_phase-1_SV_VOF']
                    assert (total>0).all()
                    water+=float(np.dot(a/total,geometry[f'z{i}_mixture_SV_VOLUME']))
                assert np.isclose(water,meta['native']['water'],rtol=1e-9,atol=1e-12)
                if n: assert meta['native']['speed']==speed[n-1]['max_speed_m_s']
    result['snapshot_iterations']=sorted(snapshot_by_index)
    with np.load(directory/'frozen-phase-n00000.npz') as baseline:
        initial={k:baseline[k] for k in baseline.files}
        with np.load(directory/'spike-diagnostics/geometry.npz') as geometry:
            counts={f'z{i}':len(geometry[f'z{i}_mixture_SV_VOLUME']) for i in range(len(r['fluid_zones']))}
        for path in sorted(directory.glob('frozen-phase-n*.npz')):
            with np.load(path) as fields:
                for key in fields.files:
                    assert fields[key].size==counts[key.split('_',1)[0]]>0, ('Phase storage cell count',path,key)
                verify_frozen_phase_arrays({k:fields[k] for k in fields.files},initial,r['fluid_zones'])
    result['frozen_phase_storage_parity']='PASS'
    for gate in r['conditioning_gates']:
        gh,_=parse_history(directory/f"history-{gate['iteration']:05d}.out")
        gr,_=parse_stage_residuals(directory/f"conditioning-native-to-{gate['iteration']:05d}.trn",'conditioning',0,gate['iteration'])
        assert conditioning_gate(gh,gr,gate['iteration'])==gate
    if terminal:
        assert r['terminal_artifacts_verified'] and r['status'] in {'CONDITIONING_GATE_NOT_MET','HORIZON_COMPLETE_ANALYSIS_PENDING'}
        expected=1000 if r['status']=='CONDITIONING_GATE_NOT_MET' else 5000
        assert r['completed_iterations']==r['actual_iteration']==expected
        assert all(v==expected for v in [end,len(flux),len(speed),residual_end])
        verify_iteration_accounting(r,expected)
        required_pairs={'n00050'}|{f'n{x:05d}' for x in range(500,expected+1,500) if x!=5000}
        required_pairs.add('conditioning-gate-not-met-final' if expected==1000 else 'final')
        assert required_pairs<=set(r['pairs'])
        for folder in ['initial-sections','initial-axial-sections','final-sections','final-axial-sections']:
            assert (directory/folder/'index.json').is_file(),folder
        if expected==5000:
            switch=r['switch_iteration'];assert 200<=switch<=1000 and r['full_equation_iterations']==5000-switch>=4000
            assert r['conditioning_gates'][-1]['passed']
            assert all(not g['passed'] for g in r['conditioning_gates'][:-1])
        else:assert len(r['conditioning_gates'])==9 and not any(g['passed'] for g in r['conditioning_gates'])
    result['status']='E8_TERMINAL_LOCAL_AUDIT_PASS' if terminal else 'E8_RUNNING_LOCAL_PREFIX_AUDIT_PASS'
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);p.add_argument('--terminal',action='store_true');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    try:r=audit(a.directory,a.terminal)
    except Exception as exc:
        r={'status':'E8_LOCAL_AUDIT_FAILED','local_only':True,'error':str(exc),'checked_utc':datetime.now(timezone.utc).isoformat()}
        a.output.write_text(json.dumps(r,indent=2)+'\n');raise
    a.output.write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2))


if __name__=='__main__':main()
