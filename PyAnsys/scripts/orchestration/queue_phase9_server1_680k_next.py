"""Wait on a verified Server 1 job, then submit exactly one next native block.

The waiting path reads local Windows files only. It never attaches to Fluent,
changes the running controller, or sends solver commands before the parent ends.
"""
from pathlib import Path
import argparse,hashlib,json,math,os,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from pyansys_fluent.stage4_native import exclusive_writer_lock


def parent_gate(parent,manifest,reopen,expected_job):
 if parent.get('job_id')!=expected_job:raise RuntimeError('Parent job identity changed')
 if parent.get('status') in ['RUNNING','VERIFYING']:return False
 if parent.get('status')!='COMPLETE':raise RuntimeError('Parent job failed or has an unknown state; no continuation')
 if parent['runner'].get('return_code')!=0 or not parent['verification']['verifier'].get('passed'):raise RuntimeError('Parent completion verification failed')
 if not all(x.get('passed') for x in parent['verification']['required_files']):raise RuntimeError('Parent files unverified')
 if manifest.get('status')!='BOUNDED_COMPLETE_VERIFIED' or manifest.get('server_id')!='1' or manifest.get('cells')!=679970:raise RuntimeError('Wrong owned endpoint')
 if manifest.get('verified_native_end')!=24580 or not math.isclose(manifest.get('accepted_film_s',0),.0395,abs_tol=1e-12):raise RuntimeError('Parent native/film coordinate changed')
 if len(manifest['blocks'])!=7 or len(manifest['schedule'])!=7:raise RuntimeError('Parent schedule changed')
 if manifest.get('film_courant_limit')!=.8 or not manifest.get('ledger_diagnostic_only'):raise RuntimeError('Run policies changed')
 if reopen.get('pair')!=manifest['latest_pair']:raise RuntimeError('Parent reopen pair differs')
 return True


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--spec',type=Path,required=True);args=parser.parse_args()
 spec=json.loads(args.spec.read_text());receipt=Path(spec['receipt']);out=receipt.parent
 def save(state):
  tmp=receipt.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(receipt)
 with exclusive_writer_lock(out/'next-command-queue.lock'):
  if receipt.exists():raise RuntimeError('Queue already dispatched; no replay')
  state={'status':'WAITING_FOR_PARENT_VERIFIED','pid':os.getpid(),'parent_job_id':spec['parent_job_id'],'parent_job_manifest':spec['parent_job_manifest'],'current_native_target':24580,'next_native_target':27580,'next_film_target_s':.0425,'next_count':3000,'next_step_s':1e-6,'courant_limit':.8,'fluent_calls_while_waiting':0,'laptop_required':False,'new_solve_submitted':False,'run_manifest':spec['run_manifest']};save(state)
  try:
   deadline=time.monotonic()+86400
   while True:
    if Path(spec['cancel_file']).exists():state['status']='CANCELLED_BEFORE_SOLVE';save(state);return
    if time.monotonic()>deadline:raise RuntimeError('Parent not verified within24h; no solve submitted')
    try:parent=json.loads(Path(spec['parent_job_manifest']).read_text())
    except (FileNotFoundError,json.JSONDecodeError):time.sleep(10);continue
    # Do not read mutable run/reopen records until the exact parent is terminal.
    if parent.get('job_id')!=spec['parent_job_id']:raise RuntimeError('Wrong parent job')
    if parent.get('status') in ['RUNNING','VERIFYING']:time.sleep(10);continue
    manifest=json.loads(Path(spec['run_manifest']).read_text());reopen=json.loads(Path(spec['reopen']).read_text())
    if parent_gate(parent,manifest,reopen,spec['parent_job_id']):break
   for key in ['runner','verifier']:
    p=Path(spec[key]);assert hashlib.sha256(p.read_bytes()).hexdigest()==spec[key+'_sha256'],'Runtime source changed; queue blocked'
   (out/(receipt.stem+'-parent-run-manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
   state.update(status='STARTING_NEXT_BLOCK',parent_verified=True);save(state)
   command=[sys.executable,'-E','-u',spec['runner'],'--resume','--ledger-diagnostic-only','--recovery-step','1e-6','--bounded-count','3000']
   with Path(spec['runner_log']).open('x') as log:
    child=subprocess.Popen(command,cwd=spec['repo'],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
    state.update(status='NEXT_CONTROLLER_RUNNING',controller_pid=child.pid,command=command);save(state);code=child.wait()
   state['controller_return_code']=code
   if code:raise RuntimeError('Next controller returned failure; no automatic retry')
   done=json.loads(Path(spec['run_manifest']).read_text())
   if done.get('status')!='BOUNDED_COMPLETE_VERIFIED' or done.get('verified_native_end')!=27580 or not math.isclose(done.get('accepted_film_s',0),.0425,abs_tol=1e-12):raise RuntimeError('Next saved endpoint differs')
   with Path(spec['verifier_log']).open('x') as log:check=subprocess.run([sys.executable,'-E',spec['verifier']],cwd=spec['repo'],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
   if check.returncode:raise RuntimeError('Next endpoint verifier failed')
   state.update(status='COMPLETE_VERIFIED',native_end=27580,film_end_s=.0425,new_solve_submitted=True,further_commands_queued=False);save(state)
  except BaseException:
   state.update(status='BLOCKED',error=traceback.format_exc());save(state);raise

if __name__=='__main__':main()
