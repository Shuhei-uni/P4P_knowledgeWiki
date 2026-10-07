"""Replace only the owned Python controller at a verified checkpoint.

Does not attach to, interrupt, exit, or restart Fluent. The native solve finishes
before the checkpoint boundary; the replacement resumes the paired endpoint.
"""
from pathlib import Path
import argparse
import json
import os
import signal
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO/'PyAnsys/scripts/setup'))
import run_phase9_mesh_startup as run


def atomic(path, value):
    temp=path.with_suffix(f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-pid',type=int,required=True)
    parser.add_argument('--reason',default='HUMAN_LIMIT_CHANGE')
    args=parser.parse_args()
    out=run.OUT;receipt_path=out/'desktop-controller.json'
    job=out/'pending-controller-update.json'
    state={'status':'WAITING_FOR_VERIFIED_CHECKPOINT','worker_pid':os.getpid(),
           'expected_controller_pid':args.expected_pid,'limits':run.hold_limits(),
           'never_exit_fluent':True,'reason':args.reason}
    atomic(job,state)
    while True:
        receipt=json.loads(receipt_path.read_text())
        if receipt['pid']!=args.expected_pid:
            raise RuntimeError('Controller changed; refuse to replace a different controller')
        process=subprocess.run(['ps','-p',str(args.expected_pid),'-o','state=,command='],
                               capture_output=True,text=True,timeout=5).stdout.strip()
        if not process or 'run_phase9_mesh_startup.py campaign' not in process:
            raise RuntimeError('Expected owned controller is absent')
        campaign=json.loads((out/'campaign-manifest.json').read_text())
        label=campaign.get('active_mesh')
        if not label:
            state.update(status='CAMPAIGN_ALREADY_ENDED');atomic(job,state);return
        path=out/(label+'-run.json')
        try:m=json.loads(path.read_text())
        except (OSError,ValueError):time.sleep(.02);continue
        if m['status']!='CHECKPOINT_VERIFIED':time.sleep(.02);continue
        os.kill(args.expected_pid,signal.SIGSTOP)
        m=json.loads(path.read_text())
        if m['status']!='CHECKPOINT_VERIFIED' or m.get('active_target') is not None:
            os.kill(args.expected_pid,signal.SIGCONT);time.sleep(.02);continue
        assert m['latest_pair']['native_iteration']==m['verified_native_end']
        tag=str(time.time_ns())
        atomic(out/f'{label}-before-controller-update-{tag}.json',m)
        receipt.update(status='REPLACED_AT_VERIFIED_CHECKPOINT',replacement_reason=args.reason)
        atomic(out/f'desktop-controller-ended-{args.expected_pid}.json',receipt)
        os.kill(args.expected_pid,signal.SIGTERM);os.kill(args.expected_pid,signal.SIGCONT)
        for _ in range(100):
            status=subprocess.run(['ps','-p',str(args.expected_pid),'-o','state='],
                                  capture_output=True,text=True,timeout=5).stdout.strip()
            if not status or status.startswith('Z'):break
            time.sleep(.1)
        else:raise RuntimeError('Old controller did not end; refuse duplicate launch')
        log=out/f'desktop-controller-{tag}.log';live=out/f'live-campaign-{tag}.txt'
        with log.open('w') as stream:
            child=subprocess.Popen([sys.executable,'-u',str(Path(run.__file__)),'campaign',
                '--live-transcript',str(live),'--controller-receipt',str(receipt_path)],
                stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        guard=subprocess.Popen(['caffeinate','-i','-w',str(child.pid)])
        receipt.update(status='SPAWNED',pid=child.pid,awake_guard_pid=guard.pid,
            log=str(log),live_transcript=str(live),resume_verified_native=m['verified_native_end'],
            observed_native_iteration=m['verified_native_end'],active_mesh=label,
            active_stage=m.get('active_stage'),batch_target=None,hold_limits=run.hold_limits())
        receipt.pop('ended_utc',None);atomic(receipt_path,receipt)
        state.update(status='APPLIED_CONTROLLER_RELAUNCHED',new_controller_pid=child.pid,
                     resume_verified_native=m['verified_native_end'],active_mesh=label)
        atomic(job,state);print(json.dumps(state),flush=True)
        thread=os.environ.get('CODEX_THREAD_ID')
        if thread:
            try:
                result=subprocess.run(['codex','queue','--thread',thread,'--message',
                    f'Phase 9 checkpoint controller replacement completed for {args.reason}. '
                    f'Read {job} and current machine evidence. Verify the new controller '
                    'resumes the saved checkpoint and its first native batch transcript '
                    'uses one start/stop pair without errors. Do not replace an active '
                    'controller or submit duplicate solves. Server 3 only; never exit or '
                    'restart Fluent. Report the verified change briefly.'],
                    capture_output=True,text=True,timeout=20)
                state['notification_queued']=result.returncode==0
            except (OSError,subprocess.TimeoutExpired):state['notification_queued']=False
            atomic(job,state)
        return


if __name__=='__main__':
    try:main()
    except Exception as exc:
        path=run.OUT/'pending-controller-update.json'
        state=json.loads(path.read_text()) if path.exists() else {}
        state.update(status='UPDATE_FAILED',error_type=type(exc).__name__,error=str(exc))
        atomic(path,state)
        thread=os.environ.get('CODEX_THREAD_ID')
        if thread:
            subprocess.run(['codex','queue','--thread',thread,'--message',
                f'Phase 9 controller update failed. Read {path}; recover within the existing '
                'Server 3 authority. Never exit or restart Fluent.'],timeout=20)
        raise
