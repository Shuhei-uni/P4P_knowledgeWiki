"""Read-only supervision; wake the originating chat on a terminal run event."""
import argparse,json,os,subprocess,time
import watch_phase10_server6_vertical_basic150ms as reader
reader.OUT=reader.ROOT/'PyAnsys/output/phase9-server6-60k-planv1/20261014'
def main():
    p=argparse.ArgumentParser();p.add_argument('--thread-id',required=True);a=p.parse_args()
    guard=subprocess.Popen(['caffeinate','-i','-w',str(os.getpid())])
    failures=0
    while True:
        try:
            state=reader.snapshot();failures=0
            event=state['status'] if state['status']=='COMPLETE_VERIFIED' or (state['status']=='RECOVERY_REQUIRED' and state['job_status']!='RUNNING') else None
        except Exception as exc:
            failures+=1;state={'status':'READ_UNCONFIRMED','error_type':type(exc).__name__,'failures':failures}
            event='EVIDENCE_UNREACHABLE' if failures>=3 else None
        state.update(watcher_pid=os.getpid(),awake_guard_pid=guard.pid);reader.write('supervision.json',state)
        if event:
            prompt='Server6 Phase9 60k EWF Planv1 event: '+event+'. Read PyAnsys/output/phase9-server6-60k-planv1/20261014/supervision.json and host-run-manifest.json. Human14October2026 requests exact EWFPlanv1 settings and200ms endpoint. ParentN8082/0.665ms; 60964cells. Sequential film, flow momentum couplingOFF, surface tension0.04041, smoothingON, direct lowerwall1.5ms drainON. Staged0.1->2.5->5us; bulk frozen after1500active updates to195ms then bulk active to200ms; nominalfinalN50899. Preserve session/endpoints and reconcile controllers/native output/filmclock/savedpairs before mutations. No uncertain replay. Recover in scope; Planv1 lower-step recovery may be used after numerical failure. Report only completion or material failure.' 
            cli='/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
            r=subprocess.run([cli,'queue','--thread',a.thread_id,'--message',prompt],cwd=reader.ROOT,capture_output=True,text=True,timeout=20)
            reader.write('wake.json',{'event':event,'return_code':r.returncode})
            if r.returncode==0:return
        time.sleep(30)
if __name__=='__main__':main()
