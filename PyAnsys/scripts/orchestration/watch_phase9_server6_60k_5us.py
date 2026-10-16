"""Read-only supervision; wake the originating chat on a terminal run event."""
import argparse,json,os,subprocess,time
import watch_phase10_server6_vertical_basic150ms as reader
reader.OUT=reader.ROOT/'PyAnsys/output/phase9-server6-60k-5us/20261013'
def main():
    p=argparse.ArgumentParser();p.add_argument('--thread-id',required=True);a=p.parse_args()
    guard=subprocess.Popen(['caffeinate','-i','-w',str(os.getpid())])
    failures=0
    while True:
        try:
            state=reader.snapshot();failures=0
            event=state['status'] if state['status'] in ['COMPLETE_200MS_REOPEN_VERIFIED','RECOVERY_REQUIRED'] else None
        except Exception as exc:
            failures+=1;state={'status':'READ_UNCONFIRMED','error_type':type(exc).__name__,'failures':failures}
            event='EVIDENCE_UNREACHABLE' if failures>=3 else None
        state.update(watcher_pid=os.getpid(),awake_guard_pid=guard.pid);reader.write('supervision.json',state)
        if event:
            prompt='Server6 Phase9 60k fixed5us run event: '+event+'. Read PyAnsys/output/phase9-server6-60k-5us/20261013/supervision.json and host-run-manifest.json. Human owns Server6 and chose original Phase9 60964cell N8081/0.660ms pair at5us to200ms total film time, inherited bulk active throughout. Exact horizon39868updates, finalN47949. Only timestep changed; no drain or physics changes. Reconcile controller, native transcript, film clock and savedpair before commands. Never replay uncertain solve or run beyond200ms. Recover execution errors within this scope. Report completion or material failure only. Preserve Fluent session and endpoint.'
            cli='/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
            r=subprocess.run([cli,'queue','--thread',a.thread_id,'--message',prompt],cwd=reader.ROOT,capture_output=True,text=True,timeout=20)
            reader.write('wake.json',{'event':event,'return_code':r.returncode})
            if r.returncode==0:return
        time.sleep(30)
if __name__=='__main__':main()
