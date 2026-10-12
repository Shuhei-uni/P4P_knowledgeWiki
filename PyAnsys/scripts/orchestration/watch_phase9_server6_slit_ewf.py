"""Bounded, read-only Server 6 supervision; queue recovery in the owning chat."""
from pathlib import Path
import argparse,fcntl,json,os,subprocess,sys,time
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'PyAnsys/src'))
OUT=ROOT/'PyAnsys/output/phase9-server6-slit154k/20261010'

def write(name,value):
 p=OUT/name;t=p.with_name(p.name+f'.tmp-{os.getpid()}-{time.time_ns()}');t.write_text(json.dumps(value,indent=2)+'\n');t.replace(p)
def read(name):
 try:return json.loads((OUT/name).read_text())
 except (OSError,ValueError):return {}

def snapshot():
 import grpc
 from ansys.api.fluent.v0 import scheme_eval_pb2,scheme_eval_pb2_grpc
 from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import Symbol,_convert_py_value_to_scheme_pointer,_convert_scheme_pointer_to_py_value
 from pyansys_fluent.connection import resolve_connection_kwargs
 launch=read('host-launch.json');kw=resolve_connection_kwargs('6',start_transcript=False,tcp_timeout_seconds=3)
 state={'server_id':'6','cells':154063,'observed_utc':datetime.now(timezone.utc).isoformat(),'watcher_pid':os.getpid(),'watcher_mutations':0,'never_exit_fluent':True,'requires_desktop_running':True}
 with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
  stub=scheme_eval_pb2_grpc.SchemeEvalStub(channel)
  def evaluate(expression):
   request=scheme_eval_pb2.SchemeEvalRequest()
   _convert_py_value_to_scheme_pointer((Symbol('eval'),(Symbol('with-input-from-string'),expression,Symbol('read')),Symbol('user-initial-environment')),request.input)
   response=stub.SchemeEval(request,metadata=(('password',kw['password']),),timeout=5)
   return _convert_scheme_pointer_to_py_value(response.output)
  def text(path):
   path=path.replace('\\','/').replace('"','\\"')
   return evaluate('(let ((p (open-input-file "'+path+'"))) (let loop ((chars \'())) (let ((c (read-char p))) (if (eof-object? c) (begin (close-input-port p) (list->string (reverse chars))) (loop (cons c chars))))))')
  job=json.loads(text(launch['host_output']+'\\job-manifest.json'));write('host-job-manifest.json',job)
  state['job_status']=job.get('status')
  path=launch['run_manifest'].replace('\\','/').replace('"','\\"')
  if not evaluate('(file-exists? "'+path+'")'):
   state.update(status='HOST_STARTUP' if job.get('status')=='RUNNING' else 'HOST_PREPARATION_BLOCKED',event=None if job.get('status')=='RUNNING' else 'CONTROLLER_BLOCKED')
   write('host-runner-startup.log',{'text':text(launch['runner_log'])})
   return state
  manifest=json.loads(text(launch['run_manifest']));write('host-run-manifest.json',manifest)
  state.update(status=manifest['status'],active_stage=manifest.get('active_stage'),active_target=manifest.get('active_target'),verified_native_end=manifest.get('verified_native_end'),accepted_film_s=manifest.get('accepted_film_s'),active_journal=manifest.get('active_journal'),latest_pair=manifest.get('latest_pair'))
  state['event']='COMPLETE' if state['status']=='COMPLETE_VERIFIED' else ('RECOVERY_REQUIRED' if state['status']=='RECOVERY_REQUIRED' else ('CONTROLLER_BLOCKED' if job.get('status')=='BLOCKED' else None))
  hold=read('target100-controller-hold.json')
  if (state['status']=='RUNNING' and job.get('status')=='BLOCKED' and
      hold.get('status')=='OWNED_CONTROLLER_HELD_NATIVE_COMMAND_RECONCILIATION_PENDING' and
      manifest.get('active_journal')==hold.get('manifest',{}).get('active_journal')):
   state.update(event=None,planned_controller_hold=True)
  transition_path=launch['host_output']+'\\target100-transition.json'
  escaped_transition=transition_path.replace('\\','/').replace('"','\\"')
  if evaluate('(file-exists? "'+escaped_transition+'")'):
   transition=json.loads(text(transition_path));write('host-target100-transition.json',transition)
   state['target100_transition_status']=transition.get('status')
   if transition.get('status')=='BLOCKED':state['event']='TARGET100_TRANSITION_BLOCKED'
 return state

def main():
 p=argparse.ArgumentParser();p.add_argument('--thread-id',required=True);p.add_argument('--interval',type=float,default=120);p.add_argument('--once',action='store_true');a=p.parse_args()
 lock=(OUT/'supervision.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 prior=read('continuous-supervision.json');handled=prior.get('handled_event_keys',[]);failures=prior.get('consecutive_read_failures',0)
 guard=subprocess.Popen(['caffeinate','-i','-w',str(os.getpid())],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 while True:
  if read('human-pause.json').get('status')=='PAUSED_BY_HUMAN':return
  try:
   previously_unreachable=failures>=3
   state=snapshot();failures=0
   if previously_unreachable and read('native-control-recovery.json').get('status')=='NATIVE_CONTROL_REPAIR_STAGED_RECONCILIATION_PENDING':state['event']='ENDPOINT_READ_RESTORED_REPAIR_PENDING'
  except Exception as exc:
   failures+=1;state={'status':'READ_UNCONFIRMED','error_type':type(exc).__name__,'event':'EVIDENCE_UNREACHABLE' if failures>=3 else None,'interpretation':'No solve replay is authorized by a timeout alone.','server_id':'6','watcher_pid':os.getpid(),'observed_utc':datetime.now(timezone.utc).isoformat(),'rpc_code':exc.code().name if hasattr(exc,'code') else None}
  state.update(originating_thread=a.thread_id,interval_seconds=a.interval,consecutive_read_failures=failures,awake_guard_pid=guard.pid)
  key=json.dumps([state.get('event'),state.get('active_stage'),state.get('verified_native_end'),state.get('active_journal')])
  if state.get('event') and key not in handled and not a.once:
   event_path=OUT/('supervision-event-'+str(time.time_ns())+'.json');event_path.write_text(json.dumps(state,indent=2)+'\n')
   campaign=read('campaign-request.json')
   scope=(f'Human revised campaign: read {OUT}/campaign-request.json. Vertical slit target 100 ms, final 95–100 ms bulk active; after verified completion and endpoint preservation, start the angle slit 213232-cell mesh on Server 6 with the same Phase 9 procedure and 100 ms target. Do not load angle mesh before the vertical completion gate. '
          if campaign.get('status')=='VERTICAL_100MS_THEN_ANGLE_SLIT' else 'This chat owns Server 6 slit154k only. Target 200 ms, final 195–200 ms bulk active. ')
   prompt=f'Automatic Server 6 vertical-slit Phase 9 event: {state["event"]}. Read {event_path}, {OUT}/host-run-manifest.json and {OUT}/host-job-manifest.json. '+scope+'Parent N5080/3.5 ms from OneDrive. Reconcile the host controller and native state before any solve or settings command. Never replay a solve from a timeout alone. Preserve all endpoints and Fluent. Recover technical failures within the selected Phase 9 settings and timestep ladder, with save/reopen at control changes. Do not modify other servers or unrelated lanes. Read Project/experiments/phase-10-proposed-design/vertical-slit154k/CONTEXT.md and setup.md. Notify only on completion, a meaningful failure or required user action. Normal progress stays quiet.'
   try:
    result=subprocess.run(['/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex','queue','--thread',a.thread_id,'--message',prompt],cwd=ROOT,capture_output=True,text=True,timeout=20)
    event_path.with_suffix('.codex.log').write_text(result.stdout+result.stderr);state['wake_returncode']=result.returncode
    if result.returncode==0:handled.append(key)
   except (OSError,subprocess.TimeoutExpired):state['wake_returncode']='UNCONFIRMED'
  state['handled_event_keys']=handled[-100:];write('continuous-supervision.json',state)
  if a.once:print(json.dumps(state,indent=2));return
  if state.get('event')=='COMPLETE':return
  time.sleep(a.interval)
if __name__=='__main__':main()
