"""Read-only Server5 slit500 campaign watcher; never sends solve/settings commands."""
from pathlib import Path
import argparse,fcntl,json,os,subprocess,sys,time
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'PyAnsys/src'))
OUT=ROOT/'PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms'
def write(name,value):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp-'+str(os.getpid()));tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(p)
def snapshot():
    import grpc
    from pyansys_fluent.connection import resolve_connection_kwargs
    from pyansys_fluent.common import quote_scheme_string
    from ansys.api.fluent.v0 import scheme_eval_pb2 as pb,scheme_eval_pb2_grpc as rpc
    from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import Symbol as S,_convert_py_value_to_scheme_pointer as put,_convert_scheme_pointer_to_py_value as get
    launch=json.loads((OUT/'host-launch.json').read_text());kw=resolve_connection_kwargs('5',start_transcript=False,tcp_timeout_seconds=3)
    with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
        def read(path,limit=200000):
            q=quote_scheme_string(path.replace('\\','/'))
            expr='(if (file-exists? "'+q+'") (let ((p (open-input-file "'+q+'"))) (let loop ((chars \'()) (n 0)) (let ((c (read-char p))) (if (or (eof-object? c) (>= n '+str(limit)+')) (begin (close-input-port p) (list->string (reverse chars))) (loop (cons c chars) (+ n 1)))))) #f)'
            request=pb.SchemeEvalRequest();put((S('eval'),(S('with-input-from-string'),expr,S('read')),S('user-initial-environment')),request.input)
            return get(rpc.SchemeEvalStub(channel).SchemeEval(request,timeout=5,metadata=(('password',kw['password']),)).output)
        campaign=json.loads(read(launch['run_manifest']));job=json.loads(read(launch['job_manifest']));write('host-run-manifest.json',campaign);write('host-job-manifest.json',job)
        cases={}
        for name in ['vertical-slit154k','angled-slit213k']:
            value=read(launch['host_output']+'\\'+name+'\\run-manifest.json')
            if value:
                m=json.loads(value);write(name+'/host-run-manifest.json',m)
                cases[name]={k:m.get(k) for k in ['status','verified_native_end','accepted_film_s','active_stage','active_target']}
                # One bounded early transcript prefix; report as startup, never as latest clock.
                if m.get('active_transcript') and not (OUT/name/'native-startup-prefix.trn').exists():
                    text=read(m['active_transcript'],50000)
                    if text and 'Film time =' in text:(OUT/name/'native-startup-prefix.trn').write_text(text)
    return {'status':campaign['status'],'job_status':job['status'],'server_id':'5','active_case':campaign.get('active_case'),'cases':cases,'solver_mutations':0,'observed_utc':datetime.now(timezone.utc).isoformat()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--once',action='store_true');p.add_argument('--thread-id');a=p.parse_args()
    if a.once:r=snapshot();write('requested-snapshot.json',r);print(json.dumps(r,indent=2));return
    assert a.thread_id
    lock=(OUT/'watcher.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    sys.path.insert(0,str(ROOT/'PyAnsys/scripts/setup'))
    from phase9_server5_live_stream import start_live_stream
    stream=OUT/('server5-native-live-'+str(time.time_ns())+'.txt')
    start_live_stream(stream);write('passive-stream.json',{'server_id':'5','path':str(stream),'solver_mutations':0})
    prior=json.loads((OUT/'supervision.json').read_text()) if (OUT/'supervision.json').exists() else {}
    needs_reconciliation=prior.get('status')=='READ_UNCONFIRMED' and prior.get('consecutive_failures',0)>=3
    guard=subprocess.Popen(['caffeinate','-i','-w',str(os.getpid())]);handled=set();failures=0
    if needs_reconciliation:
        handled.add(('EVIDENCE_UNREACHABLE',json.loads((OUT/'host-launch.json').read_text())['job_manifest']))
    while True:
        pause=OUT/'human-pause.json'
        if pause.exists() and json.loads(pause.read_text()).get('status')=='PAUSED_BY_HUMAN':return
        try:
            state=snapshot();failures=0
            # A newly dispatched recovery may still be restoring the previous
            # failed pair. Its RUNNING job must not replay the old failure alert.
            event='COMPLETE_BOTH_500MS' if state['status']=='COMPLETE_BOTH_500MS' else None
            if state['status']=='RECOVERY_REQUIRED' and state['job_status']!='RUNNING':event='RECOVERY_REQUIRED'
            if state['job_status'] in ['BLOCKED','FAILED','ERROR']:event='RECOVERY_REQUIRED'
            if not event and state['cases'].get('vertical-slit154k',{}).get('status')=='COMPLETE_500MS_REOPEN_AND_SHARED_HASH_VERIFIED':event='VERTICAL500_COMPLETE_ANGLE_SELECTED'
            if needs_reconciliation and not event:event='NATIVE_CONTROL_RESTORED_RECONCILIATION_REQUIRED'
        except Exception as e:
            failures+=1;state={'status':'READ_UNCONFIRMED','error_type':type(e).__name__,'consecutive_failures':failures,'solver_mutations':0};event='EVIDENCE_UNREACHABLE' if failures>=3 else None
            if failures>=3:needs_reconciliation=True
        state.update(watcher_pid=os.getpid(),awake_guard_pid=guard.pid);write('supervision.json',state)
        # A recovery has its own host job. Its failure must still wake the chat
        # after an earlier job already emitted RECOVERY_REQUIRED.
        job_identity=json.loads((OUT/'host-launch.json').read_text())['job_manifest']
        event_key=(event,job_identity)
        if event and event_key not in handled:
            prompt=f'Automatic Server5 Phase10 slit500 Planv1 event: {event}. Read {OUT}/supervision.json, host-run-manifest.json, host-job-manifest.json and case host-run-manifest.json files. Own Server5 only; never query another server. Human selected both retained150ms slit cases to500ms with exact current Phase9 EWF Planv1: sequential/originalimplicit EWF,0.045mm roughness,lowerdirectfilm drain; initial0.1us thenServer5 selected2.5us; no numerical thresholds. Read Project/experiments/phase-10-proposed-design/server5-planv1-500ms.md. Preserve source150ms and all endpoints. Reconcile controller/native iteration/filmclock/transcript/savedpair before any mutation; never replay a timeout. Vertical500ms must be verified/shared before angle load. Preserve Fluent; no work beyond500ms or another case. Recover technical/numerical failures in the selected settings/ladder with save/reopen at control changes. Notify only completion, meaningful failure or required user action; routine progress stays quiet.'
            cli='/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex';r=subprocess.run([cli,'queue','--thread',a.thread_id,'--message',prompt],cwd=ROOT,capture_output=True,text=True,timeout=20);write('wake-'+str(time.time_ns())+'.json',{'event':event,'return_code':r.returncode})
            if r.returncode==0:
                handled.add(event_key)
                if event!='EVIDENCE_UNREACHABLE':needs_reconciliation=False
        if state.get('status')=='COMPLETE_BOTH_500MS':return
        time.sleep(45)
if __name__=='__main__':main()
