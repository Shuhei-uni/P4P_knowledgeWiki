"""Wait for the existing Server6 preparation; dispatch the reviewed150ms job once.

No Fluent command is sent while the preparation is incomplete. This utility
never reruns preparation or deployment from a timeout.
"""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,subprocess,time,sys
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'PyAnsys/output/phase10-proposed-design/20261013/vertical-basic-ewf-to150ms'
PYTHON=ROOT/'PyAnsys/.venv/bin/python'
DEPLOY=ROOT/'PyAnsys/scripts/setup/deploy_phase10_server6_vertical_basic150ms.py'
WATCH=ROOT/'PyAnsys/scripts/orchestration/watch_phase10_server6_vertical_basic150ms.py'

def dump(value):
    p=OUT/'preparation-waiter.json';tmp=p.with_suffix('.tmp-'+str(os.getpid()));tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(p)
def wake(thread,message):
    cli='/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
    result=subprocess.run([cli,'queue','--thread',thread,'--message',message],cwd=ROOT,capture_output=True,text=True,timeout=20)
    return result.returncode

def main():
    p=argparse.ArgumentParser();p.add_argument('--preparation-pid',type=int,required=True);p.add_argument('--thread-id',required=True);args=p.parse_args()
    lock=(OUT/'preparation-waiter.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    review=json.loads((OUT/'code-review.json').read_text());assert hashlib.sha256(DEPLOY.read_bytes()).hexdigest()==review['deployment_sha256']
    guard=subprocess.Popen(['caffeinate','-i','-w',str(os.getpid())])
    state={'status':'WAITING_FOR_EXISTING_PREPARATION','waiter_pid':os.getpid(),'preparation_pid':args.preparation_pid,'awake_guard_pid':guard.pid,'solve_replayed':False,'preparation_replayed':False,'server_id':'6'}
    dump(state)
    while True:
        pause=OUT/'human-pause.json'
        if pause.exists() and json.loads(pause.read_text()).get('status')=='PAUSED_BY_HUMAN':
            state['status']='PAUSED_BY_HUMAN';dump(state);return
        result=subprocess.run(['ps','-p',str(args.preparation_pid),'-o','command='],capture_output=True,text=True)
        alive='run_phase10_server6_vertical_basic150ms.py --prepare' in result.stdout
        if alive:
            time.sleep(30);continue
        prepared=OUT/'prepared.json';manifest=OUT/'run-manifest.json'
        if not prepared.exists() or not manifest.exists():
            state['status']='RECOVERY_REQUIRED_NO_VERIFIED_PREPARATION';dump(state)
            wake(args.thread_id,f'Server6 vertical basicEWF150ms preparation ended without a verified child. Read {OUT}/preparation-waiter.json and preflight-reconciliation.json. Preserve Fluent and all endpoints. Reconcile native settings, clock and any saved pairs before any mutation. No solve or preparation replay from a timeout. Own this vertical branch only.');return
        m=json.loads(manifest.read_text());prep=json.loads(prepared.read_text())
        assert prep['status']=='PREPARED_REOPEN_VERIFIED' and m['status']=='READY'
        assert prep['parent_native_iteration']==34661 and prep['target_native_iteration']==44661 and prep['schedule']==[['ten-us-to150ms',10000,1e-5]]
        assert not (OUT/'host-launch.json').exists(),'Existing dispatch must be reconciled'
        assert hashlib.sha256(DEPLOY.read_bytes()).hexdigest()==review['deployment_sha256']
        state['status']='DEPLOYMENT_DISPATCHED_ONCE';dump(state)
        with (OUT/'deployment-waiter.log').open('ab') as log:
            deploy=subprocess.run([str(PYTHON),'-u',str(DEPLOY)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        state['deployment_return_code']=deploy.returncode
        if deploy.returncode!=0:
            state['status']='RECOVERY_REQUIRED_DEPLOYMENT_UNCONFIRMED';dump(state)
            wake(args.thread_id,f'Server6 vertical basicEWF150ms dispatch needs reconciliation. Read {OUT}/deployment-waiter.log and any host-launch.json. Do not replay deployment or solve. Own Server6 vertical branch only; preserve Fluent.');return
        with (OUT/'watcher.log').open('ab') as log:
            observer=subprocess.Popen([str(PYTHON),'-u',str(WATCH),'--thread-id',args.thread_id],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        (OUT/'watcher-launch.json').write_text(json.dumps({'status':'DISPATCHED','pid':observer.pid,'thread_id':args.thread_id,'server_id':'6','notification_policy':'completion, meaningful failure or user action only'},indent=2)+'\n')
        state.update(status='HOST_RUN_DISPATCHED_WATCHER_STARTED',watcher_pid=observer.pid);dump(state)
        wake(args.thread_id,f'Server6 vertical basicEWF150ms host continuation dispatched after the existing preparation completed and paired reopen was verified. Read {OUT}/prepared.json, host-launch.json and preparation-waiter.json. Refresh the read-only watcher snapshot and verify native10us transcript startup; never replay a timeout. Target N44661/150ms, one10000-update command, preserve50ms pair, no thresholds, no other case. Normal progress stays quiet.');return

if __name__=='__main__':main()
