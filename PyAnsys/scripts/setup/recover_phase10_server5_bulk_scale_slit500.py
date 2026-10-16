"""Retry the stopped vertical FPE with a smaller bulk pseudo-time scale only."""
from pathlib import Path
import json,sys,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase10_server5_slits_planv1_500ms as c

def schedule(clock):
    stages=[['bulk-scale-smoke',10,1e-8,True],['bulk-scale-adjustment',1470,1e-8,True],
            ['frozen-transition',1016,1e-7,False],['step-2p5us',1000,2.5e-6,False]]
    now=clock+sum(n*dt for _,n,dt,_ in stages);remaining=round((.5-now)/2.5e-6)
    assert abs(now+remaining*2.5e-6-.5)<1e-10
    i=0
    while remaining:
        n=min(10000,remaining);i+=1;stages.append(['bulk-scale-growth-'+str(i),n,2.5e-6,False]);remaining-=n
    return stages

def main():
    cfg=c.config();case=cfg['cases'][0];ev=c.OUT/case['id'];path=ev/'run-manifest.json';stamp=str(time.time_ns())
    with c.exclusive_writer_lock(c.OUT/'controller.lock'):
        s,root=c.connect();c.idle(s);c.select_work(s,root,case)
        m=json.loads(path.read_text());campaign=json.loads((c.OUT/'run-manifest.json').read_text())
        assert campaign['status']=='RECOVERY_REQUIRED' and m['status']=='RECOVERY_REQUIRED'
        assert m['active_stage']=='bulk-recovery' and m['verified_native_end']==44681
        assert c.run.native_iteration(s)==m['partial_pair']['native_iteration']==44857
        assert abs(c.run.film(s)['film_elapsed_time']-m['partial_film']['film_elapsed_time'])<1e-10
        text=c.read_local_or_remote(s,m['active_transcript']);assert 'floating point exception' in text.lower()
        for pair in [m['partial_pair'],m['latest_pair']]:
            for key in ['case','data']:
                assert c.run.remote_file_sha256(s,pair[key],str(c.run.WORK/'scratch'/('bulk-scale-hash-'+key+'-'+str(time.time_ns())+'.txt')))==pair[key+'_sha256']
        c.dump(ev/('pre-bulk-scale-failed-state-'+stamp+'.json'),m);c.dump(c.OUT/('pre-bulk-scale-failed-campaign-'+stamp+'.json'),campaign)
        try:
            s.settings.file.stop_transcript();c.run.load(s,m['latest_pair']);c.audit(s,m['parameters'],True)
            assert c.run.native_iteration(s)==44681 and abs(c.run.film(s)['film_elapsed_time']-m['accepted_film_s'])<1e-10
            scale=s.settings.solution.run_calculation.pseudo_time_settings.time_step_method.time_step_size_scale_factor.get_state()
            assert scale==1.0,'Restore point bulk pseudo-time scale differs from reviewed1.0'
            m.update(status='RECOVERY_REOPEN_VERIFIED',bulk_scale_recovery={'failure_iteration':44857,'failed_pair':m['partial_pair'],
                'restored_pair':m['latest_pair'],'bulk_pseudo_time_scale_from':scale,'bulk_pseudo_time_scale_to':.1,
                'restore_bulk_scale_when_frozen':scale,'film_step_s':1e-8,'model_physics_unchanged':True,
                'reason':'Film-step reduction alone failed; reduce bulk numerical pseudo-time scale while preserving Coupled and active equations',
                'no_timeout_replay':True})
            prep=dict(json.loads((ev/'prepared.json').read_text()));prep.update(schedule=schedule(m['accepted_film_s']),bulk_pseudo_time_recovery_scale=.1,restore_bulk_pseudo_time_scale=scale)
            c.dump(ev/('bulk-scale-recovery-plan-'+stamp+'.json'),{'state':m,'schedule':prep['schedule'],'bulk_scale':.1,'restored_when_frozen':scale})
            result=c.case_run(s,root,case,prep,resumed=m);assert result['status']=='COMPLETE_500MS_REOPEN_AND_SHARED_HASH_VERIFIED'
            completed=[{'case_id':case['id'],'native_iteration':result['verified_native_end'],'film_s':result['accepted_film_s'],'shared_pair':result['shared_pair']}]
            c.dump(c.OUT/'run-manifest.json',{'status':'CASE_COMPLETE','server_id':'5','completed':completed,'active_case':None,'target_film_s':.5})
            angle=cfg['cases'][1];prepared=c.prepare(s,root,angle);result=c.case_run(s,root,angle,prepared)
            assert result['status']=='COMPLETE_500MS_REOPEN_AND_SHARED_HASH_VERIFIED'
            completed.append({'case_id':angle['id'],'native_iteration':result['verified_native_end'],'film_s':result['accepted_film_s'],'shared_pair':result['shared_pair']})
            c.dump(c.OUT/'run-manifest.json',{'status':'COMPLETE_BOTH_500MS','server_id':'5','completed':completed,'active_case':None,'target_film_s':.5,'fluent_left_open':True})
        except BaseException:
            c.dump(c.OUT/('bulk-scale-error-'+stamp+'.json'),{'status':'RECOVERY_REQUIRED','error':traceback.format_exc(),'no_timeout_replay':True})
            current=json.loads((c.OUT/'run-manifest.json').read_text());current['status']='RECOVERY_REQUIRED';c.dump(c.OUT/'run-manifest.json',current);raise

if __name__=='__main__':main()
