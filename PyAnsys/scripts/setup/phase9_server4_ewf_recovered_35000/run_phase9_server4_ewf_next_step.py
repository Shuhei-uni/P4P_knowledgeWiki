"""Wait for the accepted 5us batch; apply user-selected 10us at idle only."""
from pathlib import Path, PureWindowsPath
import sys,json,time,os,argparse,fcntl,subprocess,importlib.util,math,traceback
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
spec=importlib.util.spec_from_file_location('server4_continuation',Path(__file__).with_name('continuation.py'))
cont=importlib.util.module_from_spec(spec);spec.loader.exec_module(cont)
def main():
 p=argparse.ArgumentParser();p.add_argument('--predecessor',type=int,required=True);p.add_argument('--live-transcript',required=True);p.add_argument('--controller-label');args=p.parse_args()
 out=run.OUT
 reservation=(out/'next-step-successor.lock').open('a+');fcntl.flock(reservation,fcntl.LOCK_EX|fcntl.LOCK_NB)
 def pause():return json.loads((out/'human-pause.json').read_text())['status']=='PAUSED_BY_USER'
 while True:
  if pause():print('USER_PAUSED_SUCCESSOR',flush=True);return
  row=subprocess.run(['ps','-p',str(args.predecessor),'-o','stat=,command='],capture_output=True,text=True,timeout=5).stdout.strip()
  if not row or row.startswith('Z'):break
  time.sleep(10)
 lock=(out/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if pause():return
 m=json.loads((out/'2_6M-run.json').read_text())
 assert m['verified_native_end']==45000 and m['active_target'] is None and m['status']=='CHECKPOINT_VERIFIED', 'Predecessor did not verify required endpoint'
 assert math.isclose(m['blocks'][-1]['film_end_s'],.10835,abs_tol=1e-12)
 proof=json.loads(Path(m['blocks'][-1]['checkpoint_proof']).read_text());assert proof['status']=='REOPEN_VERIFIED'
 run.dump(out/'human-pause.json',{'status':'EWF_RUN_AUTHORISED','automatic_recovery_enabled':True,'requires_explicit_resume':False,'authority':'User requests 10us next; predecessor completed and checkpoint verified'})
 paths=json.loads((out/'server4-paths.json').read_text())
 for key,name in [('work','WORK'),('shared','SHARED'),('parent','PARENT'),('mesh_folder','MESH_FOLDER'),('host_python','HOST_PYTHON')]:setattr(run,name,PureWindowsPath(paths[key]))
 d=json.loads((out/'desktop-controller.json').read_text());d.update(status='APPLYING_NEXT_10US',live_transcript=args.live_transcript,verified_native_end=45000,active_target=None);run.dump(out/'desktop-controller.json',d)
 s=run.attach();run.require_idle(s);assert run.native_iteration(s)==45000
 assert s.settings.solution.controls.equations.get_state()=={k:False for k in ['drift','flow','ke','mp']}
 s.transcript.start(file_name=args.live_transcript,write_to_stdout=False)
 dt=1e-5;age=m['blocks'][-1]['film_end_s'];count=round((.195-age)/dt)
 assert count==8665 and math.isclose(age+count*dt,.195,abs_tol=1e-12)
 cont.set_stage(s,m,dt,False,'frozen-growth-10us')
 params=dict(s.rp_vars('wall-film/model-parameters'));assert params['iters-per-dpm-step']==2 and params['sub-iter-nums']==50 and not params['ewf-adaptive?']
 m.update(next_film_step_s=dt,frozen_target_native=53665,final_target_native=54165,film_courant_limit=None,max_film_subiterations=50);run.dump(out/'2_6M-run.json',m)
 print('NEXT_STEP_VERIFIED_10US',count,'FINAL_BULK_UPDATES',500,flush=True)
 cont.batch(s,m,count,'ewf-frozen-growth-10us',dt)
 assert math.isclose(m['blocks'][-1]['film_end_s'],.195,abs_tol=1e-12)
 cont.set_stage(s,m,dt,True,'final-bulk-active-10us')
 # 500 updates are the exact remaining 195-200ms stage, bounded by its endpoint.
 cont.batch(s,m,500,'ewf-final-bulk-active-10us',dt)
 assert m['verified_native_end']==54165 and math.isclose(m['blocks'][-1]['film_end_s'],.2,abs_tol=1e-12)
 run.assert_bulk_active(s);m.update(status='EWF_COMPLETE',next_stage=None);run.dump(out/'2_6M-run.json',m)
 run.dump(out/'campaign-manifest.json',{'status':'EWF_COMPLETE','active_mesh':'2_6M','phase':'EWF_200MS','completed':['2_6M']})
 print('EWF_COMPLETE',54165,.2,flush=True)
if __name__=='__main__':
 try:main()
 except BaseException as exc:
  run.dump(run.OUT/('next-step-10us-failure-'+str(time.time_ns())+'.json'),{'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),'never_exit_fluent':True});raise
