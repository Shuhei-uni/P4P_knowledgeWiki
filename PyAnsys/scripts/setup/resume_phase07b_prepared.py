"""Execute a verified, unadvanced Phase 7b child after a startup-only failure.

Only accepts the specific unadvanced prepared child. Never restarts a solve of
uncertain progress; preserves old evidence and writes a new run identity.
"""
from prepare_phase07b_collector import *
import copy
import fcntl
import os
import hashlib
import numpy as np
from run_phase07b_screen import exact_parity, parse_residuals
from pyansys_fluent.phase07b_flux_monitor import FluxFaceZone,Phase07bFluxMonitor
sys.path.insert(0,str(BASE/'scripts/inspection'))
from export_phase07b_sections import export_sections

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepared-receipt',type=Path)
    ap.add_argument('--parent-manifest',type=Path,required=True);args=ap.parse_args()
    parent_manifest=args.parent_manifest
    old=json.loads(parent_manifest.read_text());assert old.get('actual_iteration',0)==0
    assert old['status']=='BLOCKED_EXECUTION'
    assert not any(x['name'].startswith('iterate_') for x in old['steps']), 'A solve was dispatched; reconcile using a continuation workflow'
    if args.prepared_receipt:
        repair=json.loads(args.prepared_receipt.read_text());assert repair['status']=='CORRECTED_SAVED_REOPENED_NO_SOLVE'
        old['pairs']['prepared']=repair['corrected_case']
    run='p7b-'+old.get('case_id',f"s{old['percent']:03d}").lower()+'-resume-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=BASE/'output'/run;out.mkdir();r=copy.deepcopy(old)
    for key in ['error','flux_monitor','actual_iteration','completed_iterations']:r.pop(key,None)
    r.update(run_id=run,requested_iterations=5000,parent_manifest=str(parent_manifest),parent_prepared=old['pairs']['prepared'],steps=[],status='VERIFYING_UNADVANCED_PREPARED',pairs={'initial':old['pairs']['initial']},controller_pid=os.getpid())
    r['resume_implementation_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    lock=(BASE/'output/phase07b-server1-controller.lock').open('a+')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    lock.seek(0);lock.truncate();lock.write(json.dumps({'pid':os.getpid(),'run_id':run}));lock.flush()
    r['report']=ROOT+'/reports/'+run+'.out';r['remote_transcript']=ROOT+'/logs/'+run+'.trn'
    def persist(): (out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('RPC deadline; reconcile before repeating')))
    def step(name,f,seconds=90):
        print(name,flush=True);e={'name':name,'state':'STARTED'};r['steps'].append(e);persist();signal.alarm(seconds)
        try:v=f();e.update(state='PASS',value=v);return v
        except Exception as x:e.update(state='FAIL',error=str(x));raise
        finally:signal.alarm(0);persist()
    s=None;m=None
    def n():return int(s.settings.setup.named_expressions['P7bGlobalIteration'].get_value())
    def save(tag):
        p=ROOT+'/case-data/'+run+'-'+tag+'.cas.h5'
        assert not any(remote_file_exists(s,p.replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
        step('save_'+tag,lambda:s.settings.file.write_case_data(file_name=p),180)
        assert all(remote_file_exists(s,p.replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5']);r['pairs'][tag]=p;persist();return p
    try:
        s=step('connect',lambda:connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5),30)
        s.transcript.start(file_name=str(out/'setup.trn'),write_to_stdout=False)
        # Reconcile before any reload or report mutation. No iterations were issued.
        assert n()==0 and s.settings.setup.named_expressions['P7bWaterVolume'].get_value()==0
        assert all(remote_file_exists(s,r['parent_prepared'].replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
        for name,d in r['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==d
        for z in [ZONE,'p7b-collector']:
            for ph in ['mixture','phase-1','phase-2']:assert s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state()==old['source_slots'][z][ph]
        assert all(not v['check_convergence'] for v in s.settings.solution.monitor.residual.equations.get_state().values())
        if 'reference_methods' in old:
            exact_parity(old['reference_methods'],s.settings.solution.methods.get_state(),'live methods')
            exact_parity(old['reference_controls'],s.settings.solution.controls.get_state(),'live controls')
        assert n()==0
        r['resume_verification']='UNCHANGED_VERIFIED_PREPARED_N0_NO_SOLVE_NO_REINITIALIZATION'
        step('close_inherited_native_transcript',lambda:s.settings.file.stop_transcript())
        rf=s.settings.solution.monitor.report_files['p7b-screen-history'];rf.file_name=r['report'];r['reports']=rf.report_defs()
        r['initial_metrics']=step('compute_initial_reports',lambda:s.settings.solution.report_definitions.compute(report_defs=r['reports']))
        prepared=save('prepared');step('reopen_corrected_prepared',lambda:s.settings.file.read_case_data(file_name=prepared),180)
        assert n()==0
        for name,d in r['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==d
        for z,phases in r['source_slots'].items():
            for ph,slots in phases.items():exact_parity(slots,s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state(),z+'.'+ph)
        r['reopened_metrics']=step('compute_reopened_reports',lambda:s.settings.solution.report_definitions.compute(report_defs=r['reports']))
        # Verify small fixed-section extraction before long computation.
        r['initial_sections']=step('extract_initial_sections',lambda:export_sections(s,r['sections'],out/'initial-sections'),180)
        if r.get('axial_sections'):
            r['initial_axial_sections']=step('extract_initial_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'initial-axial-sections'),180)
        s.transcript.stop();assert 'SEGMENTATION VIOLATION' not in (out/'setup.trn').read_text()
        s.transcript.start(file_name=str(out/'solve.trn'),write_to_stdout=False)
        step('start_durable_transcript',lambda:s.settings.file.start_transcript(file_name=r['remote_transcript']))
        if 'interface_proof' in old:
            faces=[FluxFaceZone(name,x['outward_sign'],x['count']) for name,x in old['interface_proof'].items() if x.get('all_faces_cross_centroid_mask')]
        else:
            faces=[FluxFaceZone(x['name'],x['outward_sign'],x['expected_owned_count']) for x in old['flux_monitor']['face_zones']]
        m=Phase07bFluxMonitor(s,face_zones=faces,start_iteration=0,local_jsonl=out/'collector-flux.jsonl',remote_directory=ROOT+'/reports');m.register()
        r['status']='RUNNING';r['flux_monitor']=m.manifest();persist();current=0
        for target in [50]+list(range(500,5001,500)):
            step(f'iterate_{current}_to_{target}',lambda current=current,target=target:s.settings.solution.run_calculation.iterate(iter_count=target-current),max(600,(target-current)*20))
            r['actual_iteration']=n();assert r['actual_iteration']==target;r['flux_monitor']=m.manifest();m.assert_complete(target)
            last=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1]);assert json.loads(read_text(s,last['remote_path']))==last
            r.setdefault('remote_flux_readbacks',[]).append({'iteration':target,'path':last['remote_path'],'matches_local':True})
            history=read_text(s,r['report']);(out/f'history-{target:05d}.out').write_text(history);rows=np.atleast_2d(np.loadtxt(history.splitlines(),skiprows=3));assert np.array_equal(rows[:,0],np.arange(1,target+1));assert np.isfinite(rows).all()
            solve=(out/'solve.trn').read_text();assert not any(x in solve for x in ['SEGMENTATION VIOLATION','floating point exception','Divergence detected'])
            residual_data,residual_audit=parse_residuals(out/'solve.trn')
            assert len(residual_data)==8 and not residual_audit['conflicting_indices'] and not residual_audit['nonfinite_columns']
            assert set(range(1,target+1)).issubset(residual_data['iteration'])
            r['residual_coverage']=residual_audit
            if target==50:r['instrumentation_smoke']='N1-50 scalar, exact-face flux, remote readback and seven residuals PASS'
            r['latest_metrics']=step(f'metrics_{target}',lambda:s.settings.solution.report_definitions.compute(report_defs=r['reports']))
            save('final' if target==5000 else f'n{target:05d}');current=target;persist()
        m.unregister();r['flux_monitor']=m.manifest();m=None
        r['final_sections']=step('extract_final_sections',lambda:export_sections(s,r['sections'],out/'final-sections'),180)
        if r.get('axial_sections'):
            r['final_axial_sections']=step('extract_final_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'final-axial-sections'),180)
        s.settings.file.stop_transcript();s.transcript.stop();r.update(status='HORIZON_COMPLETE_ANALYSIS_PENDING',completed_iterations=current);persist()
    except Exception as e:
        signal.alarm(0);r.update(status='BLOCKED_EXECUTION',error=str(e));(out/'error.txt').write_text(traceback.format_exc());raise
    finally:
        signal.alarm(0)
        if m is not None:
            try:m.unregister()
            except Exception as e:r['cleanup_error']=str(e)
            r['flux_monitor']=m.manifest()
        if s is not None:
            try:s.transcript.stop()
            except Exception:pass
        persist();print('EVIDENCE',out,flush=True)
if __name__=='__main__':main()
