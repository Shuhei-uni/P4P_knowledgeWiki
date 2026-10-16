"""Recover a proven stopped FPE from its verified pair; Server5 only."""
from pathlib import Path
import json,sys,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase10_server5_slits_planv1_500ms as c

def recovery_schedule(clock):
    # Ten accepted original updates remain accepted. Complete the other1490
    # bulk updates at0.01us; align the frozen0.1us transition to the2.5us grid.
    stages=[['recovery-smoke',10,1e-8,True],['bulk-recovery',1480,1e-8,True],
            ['frozen-transition',1016,1e-7,False],['step-2p5us',1000,2.5e-6,False]]
    now=clock+sum(n*dt for _,n,dt,_ in stages)
    remaining=round((.5-now)/2.5e-6)
    assert abs(now+remaining*2.5e-6-.5)<1e-10
    i=0
    while remaining:
        n=min(10000,remaining);i+=1
        stages.append(['recovered-growth-'+str(i),n,2.5e-6,False]);remaining-=n
    return stages

def main():
    cfg=c.config();case=cfg['cases'][0];ev=c.OUT/case['id'];path=ev/'run-manifest.json'
    with c.exclusive_writer_lock(c.OUT/'controller.lock'):
        s,root=c.connect();c.idle(s)
        m=json.loads(path.read_text());campaign=json.loads((c.OUT/'run-manifest.json').read_text())
        assert campaign['status']=='RECOVERY_REQUIRED' and m['status']=='RECOVERY_REQUIRED'
        assert m['active_stage']=='bulk-adjustment' and m['verified_native_end']==44671
        assert c.run.native_iteration(s)==m['partial_pair']['native_iteration']==45047
        assert abs(c.run.film(s)['film_elapsed_time']-m['partial_film']['film_elapsed_time'])<1e-10
        # Require affirmative native failure, not a client timeout.
        text=c.read_local_or_remote(s,m['active_transcript'])
        assert 'floating point exception' in text.lower() and c.FATAL.search(text)
        c.select_work(s,root,case);stamp=str(time.time_ns())
        for pair in [m['partial_pair'],m['latest_pair']]:
            for key in ['case','data']:
                assert c.run.remote_file_sha256(s,pair[key],str(c.run.WORK/'scratch'/('recovery-check-'+key+'-'+str(time.time_ns())+'.txt')))==pair[key+'_sha256']
        c.dump(ev/('failed-attempt-'+stamp+'.json'),m)
        c.dump(c.OUT/('failed-campaign-'+stamp+'.json'),campaign)
        try:
            # Closing only the failed transcript leaves Fluent itself open.
            s.settings.file.stop_transcript()
            c.run.load(s,m['latest_pair']);c.audit(s,m['parameters'],True)
            assert c.run.native_iteration(s)==44671
            assert abs(c.run.film(s)['film_elapsed_time']-m['accepted_film_s'])<1e-10
            m.update(status='RECOVERY_REOPEN_VERIFIED',recovery={'failure_iteration':45047,'failed_pair':m['partial_pair'],
                'restored_pair':m['latest_pair'],'film_step_s':1e-8,'model_physics_unchanged':True,
                'reason':'Film divergence/FPE at lowest planned0.1us; reduce numerical film step for remaining bulk adjustment',
                'no_timeout_replay':True})
            prep=dict(json.loads((ev/'prepared.json').read_text()));prep['schedule']=recovery_schedule(m['accepted_film_s'])
            c.dump(ev/('recovery-plan-'+stamp+'.json'),{'state':m,'schedule':prep['schedule']})
            result=c.case_run(s,root,case,prep,resumed=m)
            completed=[{'case_id':case['id'],'native_iteration':result['verified_native_end'],'film_s':result['accepted_film_s'],'shared_pair':result['shared_pair']}]
            assert result['status']=='COMPLETE_500MS_REOPEN_AND_SHARED_HASH_VERIFIED'
            c.dump(c.OUT/'run-manifest.json',{'status':'CASE_COMPLETE','server_id':'5','completed':completed,'active_case':None,'target_film_s':.5})
            angle=cfg['cases'][1];prepared=c.prepare(s,root,angle);result=c.case_run(s,root,angle,prepared)
            assert result['status']=='COMPLETE_500MS_REOPEN_AND_SHARED_HASH_VERIFIED'
            completed.append({'case_id':angle['id'],'native_iteration':result['verified_native_end'],'film_s':result['accepted_film_s'],'shared_pair':result['shared_pair']})
            c.dump(c.OUT/'run-manifest.json',{'status':'COMPLETE_BOTH_500MS','server_id':'5','completed':completed,'active_case':None,'target_film_s':.5,'fluent_left_open':True})
        except BaseException:
            c.dump(c.OUT/('recovery-error-'+stamp+'.json'),{'status':'RECOVERY_REQUIRED','error':traceback.format_exc(),'no_timeout_replay':True})
            current=json.loads((c.OUT/'run-manifest.json').read_text());current['status']='RECOVERY_REQUIRED';c.dump(c.OUT/'run-manifest.json',current)
            raise

if __name__=='__main__':main()
