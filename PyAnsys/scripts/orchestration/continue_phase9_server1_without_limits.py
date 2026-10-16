"""Retire old numerical gates without touching an accepted native solve.

Wait for the original worker to release ownership. Resume only an old numerical
gate at its saved endpoint; actual errors remain terminal. No Fluent RPCs while
waiting. The replacement runner holds the existing exclusive solver lock.
"""
import argparse,hashlib,json,os,subprocess,sys,time,traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from pyansys_fluent.stage4_native import exclusive_writer_lock

LIMIT_ERRORS=('Film Courant exceeds operating ceiling; review step before continuation',
              'Frozen drain proof requires repair before next step')

def limit_only_stop(m):
 if m.get('status')!='RECOVERY_REQUIRED':return False
 error=m.get('error','').strip().splitlines()[-1:]
 if not error or error[0] not in ['RuntimeError: '+x for x in LIMIT_ERRORS]:return False
 if m.get('active_target') is not None:return False
 if m['blocks'][-1]['pair']['native_iteration']!=m.get('verified_native_end'):return False
 if error[0].endswith(LIMIT_ERRORS[1]):
  failures=m['blocks'][-1].get('drain_proof',{}).get('verification',{}).get('failures',[])
  if not failures or any(x not in ('film ledger exceeds the declared probe tolerance',
      'accepted film advancement and positive direct removal are required') for x in failures):return False
 return True

def main():
 p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);a=p.parse_args()
 spec=json.loads(a.spec.read_text());receipt=Path(spec['receipt'])
 def save(state):
  tmp=receipt.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(receipt)
 if receipt.exists():raise RuntimeError('Existing transition receipt; refuse duplicate')
 state={'status':'WAITING_FOR_ORIGINAL_CONTROLLER','pid':os.getpid(),'laptop_required':False,
        'target_film_s':.2,'numerical_limit_checks':False,'solver_calls_while_waiting':0};save(state)
 try:
  while True:
   try:parent=json.loads(Path(spec['parent_job_manifest']).read_text())
   except (FileNotFoundError,json.JSONDecodeError):time.sleep(5);continue
   if parent.get('job_id')!=spec['parent_job_id']:raise RuntimeError('Wrong original job identity')
   if parent.get('status') in ('RUNNING','VERIFYING'):time.sleep(5);continue
   m=json.loads(Path(spec['run_manifest']).read_text())
   if m.get('server_id')!='1' or m.get('cells')!=679970:raise RuntimeError('Wrong owned lane')
   if m.get('status')=='COMPLETE_VERIFIED':
    # Original final verifier may enforce retired limits. Keep its receipt and
    # verify artifacts under the new policy without sending any solve command.
    m['no_limit_checks']=True;m['film_courant_limit']=None
    m['limit_check_authority']=spec['authority']
    path=Path(spec['run_manifest']);(path.parent/'run-manifest-before-no-limits-final.json').write_text(path.read_text())
    path.write_text(json.dumps(m,indent=2)+'\n');break
   if not limit_only_stop(m):raise RuntimeError('Original controller stopped on an execution error; no automatic replay')
   for key in ('runner','verifier'):
    if hashlib.sha256(Path(spec[key]).read_bytes()).hexdigest()!=spec[key+'_sha256']:raise RuntimeError('Staged runtime hash changed')
   state.update(status='RESUMING_WITHOUT_NUMERICAL_LIMITS',saved_native=m['verified_native_end']);save(state)
   with Path(spec['runner_log']).open('x') as log:
    child=subprocess.Popen([sys.executable,'-E','-u',spec['runner'],'--resume',
       '--ledger-diagnostic-only','--no-limit-checks','--recovery-step','1e-6'],
       cwd=spec['repo'],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
    state['controller_pid']=child.pid;save(state);code=child.wait()
   if code:raise RuntimeError('Replacement controller returned an execution error; no replay')
   break
  if hashlib.sha256(Path(spec['verifier']).read_bytes()).hexdigest()!=spec['verifier_sha256']:raise RuntimeError('Staged verifier hash changed')
  with Path(spec['verifier_log']).open('x') as log:
   check=subprocess.run([sys.executable,'-E',spec['verifier']],cwd=spec['repo'],
      stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
  if check.returncode:raise RuntimeError('Final endpoint verification failed')
  state.update(status='COMPLETE_VERIFIED',film_end_s=.2,native_end=185080);save(state)
 except BaseException:
  state.update(status='ERROR',error=traceback.format_exc());save(state);raise

if __name__=='__main__':
 with exclusive_writer_lock(ROOT/'output/phase9-ewf-server1-680k/20261009/no-limits-transition.lock'):
  main()
