"""Correct only the loaded Phase7b N0 speed report, preserve and reopen it."""
from prepare_phase07b_collector import *

def main():
    run='speed-report-repair-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=BASE/'output/phase07b_preparation'/run;out.mkdir();r={'status':'INSPECTING','steps':[]}
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('bounded report repair deadline')))
    def persist():(out/'result.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
    def step(k,f,seconds=60):
        print(k,flush=True);e={'name':k,'state':'STARTED'};r['steps'].append(e);persist();signal.alarm(seconds)
        try:v=f();e.update(state='PASS',value=v);return v
        except Exception as x:e.update(state='FAIL',error=str(x));raise
        finally:signal.alarm(0);persist()
    s=None
    try:
        s=step('connect',lambda:connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5),30)
        s.transcript.start(file_name=str(out/'repair.trn'),write_to_stdout=False)
        assert s.settings.setup.general.solver.time()=='steady'
        assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==0
        assert set(s.settings.setup.cell_zone_conditions.fluid.get_object_names())=={ZONE,'p7b-collector'}
        old=json.loads((BASE/'output/p7b-s020-20260918T065338Z/manifest.json').read_text())
        for name,d in old['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==d,(name,'live definition changed')
        before=s.settings.setup.get_state();r['before_definition']=s.settings.setup.named_expressions['P7bMaximumSpeed'].definition()
        r['preserved_case']=ROOT+'/case-data/'+run+'-before.cas.h5'
        step('preserve_live_pair',lambda:s.settings.file.write_case_data(file_name=r['preserved_case']),150)
        d='Maximum(VelocityMagnitude(phase="mixture"),["'+ZONE+'", "p7b-collector"])'
        step('correct_speed_context',lambda:s.settings.setup.named_expressions['P7bMaximumSpeed'].definition.set_state(d))
        assert s.settings.setup.named_expressions['P7bMaximumSpeed'].definition()==d
        r['corrected_definition']=d
        r['speed_value']=step('evaluate_corrected_speed',lambda:s.settings.setup.named_expressions['P7bMaximumSpeed'].get_value())
        r['report_value']=step('compute_corrected_report',lambda:s.settings.solution.report_definitions.compute(report_defs=['p7bmaximumspeed']))
        r['corrected_case']=ROOT+'/case-data/'+run+'-corrected.cas.h5'
        step('save_corrected_pair',lambda:s.settings.file.write_case_data(file_name=r['corrected_case']),150)
        assert all(remote_file_exists(s,r['corrected_case'].replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
        step('reopen_corrected_pair',lambda:s.settings.file.read_case_data(file_name=r['corrected_case']),150)
        assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==0
        assert s.settings.setup.named_expressions['P7bMaximumSpeed'].definition()==d
        r['reopened_report']=step('recompute_after_reopen',lambda:s.settings.solution.report_definitions.compute(report_defs=['p7bmaximumspeed']))
        r['sources']={z:{p:s.settings.setup.cell_zone_conditions.fluid[z].phase[p].sources.get_state() for p in ['mixture','phase-1','phase-2']} for z in [ZONE,'p7b-collector']}
        assert r['sources']==old['source_slots']
        reports=s.settings.solution.monitor.report_files['p7b-screen-history'].report_defs()
        r['all_reports']=step('all_report_definitions_compute',lambda:s.settings.solution.report_definitions.compute(report_defs=reports),120)
        s.transcript.stop();t=(out/'repair.trn').read_text();assert 'SEGMENTATION VIOLATION' not in t
        r['status']='CORRECTED_SAVED_REOPENED_NO_SOLVE';r['iteration']=0
    except Exception as e:r.update(status='FAILED',error=str(e));(out/'error.txt').write_text(traceback.format_exc());raise
    finally:
        signal.alarm(0)
        if s is not None:
            try:s.transcript.stop()
            except Exception:pass
        persist();print('EVIDENCE',out,flush=True)
if __name__=='__main__':main()
