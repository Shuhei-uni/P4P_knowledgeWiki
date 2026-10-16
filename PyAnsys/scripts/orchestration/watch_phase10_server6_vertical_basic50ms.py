"""Read-only supervision of the one authorized Server6 vertical-slit basic-EWF 50 ms run."""
from pathlib import Path
import argparse, fcntl, json, os, subprocess, sys, time
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'PyAnsys/src'))
OUT=ROOT/'PyAnsys/output/phase10-proposed-design/20261012/vertical-basic-ewf-10us'

def write(name,value):
    p=OUT/name;tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(p)

def snapshot():
    import grpc
    from pyansys_fluent.connection import resolve_connection_kwargs
    from pyansys_fluent.common import quote_scheme_string
    from ansys.api.fluent.v0 import scheme_eval_pb2 as pb,scheme_eval_pb2_grpc as rpc
    from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import Symbol as S,_convert_py_value_to_scheme_pointer as put,_convert_scheme_pointer_to_py_value as get
    launch=json.loads((OUT/'host-launch.json').read_text())
    kw=resolve_connection_kwargs('6',start_transcript=False,tcp_timeout_seconds=3)
    with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
        def text(path):
            q=quote_scheme_string(path.replace('\\','/'))
            expr='(let ((p (open-input-file "'+q+'"))) (let loop ((chars \'())) (let ((c (read-char p))) (if (eof-object? c) (begin (close-input-port p) (list->string (reverse chars))) (loop (cons c chars))))))'
            req=pb.SchemeEvalRequest();put((S('eval'),(S('with-input-from-string'),expr,S('read')),S('user-initial-environment')),req.input)
            return get(rpc.SchemeEvalStub(channel).SchemeEval(req,timeout=5,metadata=(('password',kw['password']),)).output)
        m=json.loads(text(launch['run_manifest']));write('host-run-manifest.json',m)
        j=json.loads(text(launch['job_manifest']));write('host-job-manifest.json',j)
    return {'status':m['status'],'job_status':j['status'],'active_stage':m.get('active_stage'),
            'accepted_film_s':m.get('accepted_film_s'),'active_target':m.get('active_target'),
            'server_id':'6','solver_mutations':0,'observed_utc':datetime.now(timezone.utc).isoformat()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--thread-id');p.add_argument('--once',action='store_true');a=p.parse_args()
    if a.once:
        value=snapshot();write('requested-snapshot.json',value);print(json.dumps(value,indent=2));return
    assert a.thread_id
    lock=(OUT/'watcher.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    guard=subprocess.Popen(['caffeinate','-i','-w',str(os.getpid())])
    handled=set();failures=0
    while True:
        pause=OUT/'human-pause.json'
        if pause.exists() and json.loads(pause.read_text()).get('status')=='PAUSED_BY_HUMAN':return
        try:
            state=snapshot();failures=0
            event=state['status'] if state['status'] in ['COMPLETE_50MS_REOPEN_VERIFIED','RECOVERY_REQUIRED'] else None
        except Exception as e:
            failures+=1;state={'status':'READ_UNCONFIRMED','error_type':type(e).__name__,'consecutive_failures':failures,'solver_mutations':0}
            event='EVIDENCE_UNREACHABLE' if failures>=3 else None
        state.update(watcher_pid=os.getpid(),awake_guard_pid=guard.pid);write('supervision.json',state)
        if event and event not in handled:
            prompt=(f'Automatic Server6 Phase10 vertical-slit basic-EWF 50ms event: {event}. Read {OUT}/supervision.json, host-run-manifest.json and host-job-manifest.json. '
                    'Human selected vertical154063-cell N31000/13.392ms with exact angled basicEWF parameters and wall/drain settings,10us to50ms, final8us update for exactclock. No numerical thresholds or qualification gates. Read Project/experiments/phase-10-proposed-design/vertical-slit154k/basic-ewf-10us/setup.md. '
                    'Own only Server6 vertical slit154k basic-EWF branch. Reconcile native clock/transcript/savedpair/controller before any command; never replay a timeout. '
                    'Preserve Fluent and all endpoints. Do not run beyond50ms or start another case. Notify only completion, meaningful failure or required user action.')
            cli='/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
            r=subprocess.run([cli,'queue','--thread',a.thread_id,'--message',prompt],cwd=ROOT,capture_output=True,text=True,timeout=20)
            write('wake-'+str(time.time_ns())+'.json',{'event':event,'return_code':r.returncode})
            if r.returncode==0:handled.add(event)
        if event=='COMPLETE_50MS_REOPEN_VERIFIED':return
        time.sleep(30)

if __name__=='__main__':main()
