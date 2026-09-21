"""Repair the verified S20 N0 report context and execute its authorized screen.

Only accepts the specific unadvanced prepared child. Never restarts a solve of
uncertain progress; preserves old evidence and writes a new run identity.
"""
from prepare_phase07b_collector import *
import numpy as np
from pyansys_fluent.phase07b_flux_monitor import FluxFaceZone,Phase07bFluxMonitor
sys.path.insert(0,str(BASE/'scripts/inspection'))
from export_phase07b_sections import export_sections

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepared-receipt',type=Path);args=ap.parse_args()
    parent_manifest=BASE/'output/p7b-s020-20260918T065338Z/manifest.json'
    old=json.loads(parent_manifest.read_text());assert old['actual_iteration']==0
    if args.prepared_receipt:
        repair=json.loads(args.prepared_receipt.read_text());assert repair['status']=='CORRECTED_SAVED_REOPENED_NO_SOLVE'
        old['pairs']['prepared']=repair['corrected_case']
    run='p7b-s020-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=BASE/'output'/run;out.mkdir();r={'run_id':run,'percent':20,'requested_iterations':5000,'parent_manifest':str(parent_manifest),'parent_prepared':old['pairs']['prepared'],'steps':[],'status':'REPAIRING_UNADVANCED_PREPARED','definitions':dict(old['definitions']),'sections':old['sections'],'source_slots':old['source_slots'],'pairs':{}}
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
        p=ROOT+'/case-data/'+run+'-'+tag+'.cas.h5';step('save_'+tag,lambda:s.settings.file.write_case_data(file_name=p),180)
        assert all(remote_file_exists(s,p.replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5']);r['pairs'][tag]=p;persist();return p
    try:
        s=step('connect',lambda:connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5),30)
        s.transcript.start(file_name=str(out/'setup.trn'),write_to_stdout=False)
        step('load_verified_n0_prepared',lambda:s.settings.file.read_case_data(file_name=r['parent_prepared']),180)
        assert n()==0
        name='P7bMaximumSpeed';d='Maximum(VelocityMagnitude(phase="mixture"),["'+ZONE+'","p7b-collector"])'
        r['definitions'][name]=d;s.settings.setup.named_expressions[name].definition=d;assert s.settings.setup.named_expressions[name].definition()==d
        for z in [ZONE,'p7b-collector']:
            for ph in ['mixture','phase-1','phase-2']:assert s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state()==old['source_slots'][z][ph]
        assert all(not v['check_convergence'] for v in s.settings.solution.monitor.residual.equations.get_state().values())
        rf=s.settings.solution.monitor.report_files['p7b-screen-history'];rf.file_name=r['report'];r['reports']=rf.report_defs()
        r['initial_metrics']=step('compute_initial_reports',lambda:s.settings.solution.report_definitions.compute(report_defs=r['reports']))
        prepared=save('prepared');step('reopen_corrected_prepared',lambda:s.settings.file.read_case_data(file_name=prepared),180)
        assert n()==0 and s.settings.setup.named_expressions[name].definition()==d
        # Verify small fixed-section extraction before long computation.
        r['initial_sections']=step('extract_initial_sections',lambda:export_sections(s,r['sections'],out/'initial-sections'),180)
        s.transcript.stop();assert 'SEGMENTATION VIOLATION' not in (out/'setup.trn').read_text()
        s.transcript.start(file_name=str(out/'solve.trn'),write_to_stdout=False)
        step('start_durable_transcript',lambda:s.settings.file.start_transcript(file_name=r['remote_transcript']))
        faces=[FluxFaceZone(x['name'],x['outward_sign'],x['expected_owned_count']) for x in old['flux_monitor']['face_zones']]
        m=Phase07bFluxMonitor(s,face_zones=faces,start_iteration=0,local_jsonl=out/'collector-flux.jsonl',remote_directory=ROOT+'/reports');m.register()
        r['status']='RUNNING';r['flux_monitor']=m.manifest();persist();current=0
        for target in [50]+list(range(500,5001,500)):
            step(f'iterate_{current}_to_{target}',lambda current=current,target=target:s.settings.solution.run_calculation.iterate(iter_count=target-current),max(600,(target-current)*20))
            r['actual_iteration']=n();assert r['actual_iteration']==target;r['flux_monitor']=m.manifest();m.assert_complete(target)
            last=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1]);assert json.loads(read_text(s,last['remote_path']))==last
            history=read_text(s,r['report']);(out/f'history-{target:05d}.out').write_text(history);rows=np.atleast_2d(np.loadtxt(history.splitlines(),skiprows=3));assert np.array_equal(rows[:,0],np.arange(1,target+1));assert np.isfinite(rows).all()
            solve=(out/'solve.trn').read_text();assert not any(x in solve for x in ['SEGMENTATION VIOLATION','floating point exception','Divergence detected'])
            r['latest_metrics']=step(f'metrics_{target}',lambda:s.settings.solution.report_definitions.compute(report_defs=r['reports']))
            save('final' if target==5000 else f'n{target:05d}');current=target;persist()
        m.unregister();m=None
        r['final_sections']=step('extract_final_sections',lambda:export_sections(s,r['sections'],out/'final-sections'),180)
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
