"""Passive Windows watcher for the local Phase 9 60k controller.

Reads bounded file tails and exact controller process identity. No Fluent API.
The controller, not this watcher, owns stage transitions and queued solves.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time


def read_json(path):
    return json.loads(path.read_text())


def tail(path, size=16384):
    if not path.exists():
        return '', None
    with path.open('rb') as stream:
        stream.seek(max(0, path.stat().st_size-size))
        text=stream.read(size).decode('utf-8',errors='replace')
    return text,time.time()-path.stat().st_mtime


def controller_alive(pid):
    if not isinstance(pid,int) or pid<=0:
        return False
    command=f"$p=Get-CimInstance Win32_Process -Filter 'ProcessId={pid}'; if($p -and $p.CommandLine -like '*run_phase9_60k_direct_ewf.py*'){{'MATCH'}}"
    result=subprocess.run(['powershell.exe','-NoProfile','-Command',command],
        capture_output=True,text=True,timeout=8,
        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    return result.returncode==0 and result.stdout.strip()=='MATCH'


def observe(work, alive=controller_alive, stall_seconds=900):
    m=read_json(work/'run-manifest.json')
    block=Path(m['active_block']) if m.get('active_block') else None
    text,age=tail(block/'native-run.trn') if block else ('',None)
    clocks=list(re.finditer(r'Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)',text))
    report,_=tail(block/'p72d-total-mass.out') if block else ('',None)
    rows=re.findall(r'^\s*(\d+)\s+[-+\deE.]+\s*$',report,re.M)
    terminal=(block/'returned.txt').exists() if block else False
    running=alive(m.get('pid'))
    status=m.get('status')
    requested_step=m.get('blocks',[{}])[-1].get('step_s') if m.get('blocks') else None
    last=clocks[-1] if clocks else None
    event=None
    if status=='COMPLETE': event='COMPLETE'
    elif status and status.startswith('STOPPED'): event='STOPPED_WITH_EVIDENCE'
    elif not running: event='CONTROLLER_ABSENT'
    elif re.search(r'floating point exception|received signal|fatal error|Divergence detected',text,re.I):
        event='NATIVE_FAILURE'
    elif status=='RUNNING_NATIVE' and last and requested_step and abs(float(last[2])-requested_step)>max(1e-12,requested_step*1e-7):
        event='EFFECTIVE_TIMESTEP_MISMATCH'
    elif status=='RUNNING_NATIVE' and terminal: event='NATIVE_COMMAND_RETURNED'
    elif status=='RUNNING_NATIVE' and age is not None and age>stall_seconds:
        event='NATIVE_OUTPUT_STALLED'
    elif status!='RUNNING_NATIVE' and time.time()-m.get('updated_epoch',time.time())>stall_seconds:
        event='CONTROLLER_TRANSITION_STALLED'
    return {'observed_epoch':time.time(),'watcher_pid':os.getpid(),'controller_pid':m.get('pid'),
        'controller_alive':running,'controller_status':status,'active_block':str(block) if block else None,
        'native_command_return_marker':terminal,'observed_native_iteration':int(rows[-1]) if rows else None,
        'observed_film_age_s':float(last[1]) if last else None,
        'observed_step_s':float(last[2]) if last else None,
        'requested_step_s':requested_step,
        'observed_courant':float(last[3]) if last else None,
        'transcript_age_seconds':age,'target_iteration':m.get('native_target'),
        'verified_native_end':m.get('verified_native_end'),'latest_pair':m.get('latest_pair'),
        'event':event,'error':m.get('error'),'command_owner':'controller only; subsequent stages sequenced after native return and assessment'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--interval',type=float,default=15)
    parser.add_argument('--once',action='store_true')
    args=parser.parse_args()
    work=args.work.resolve()
    previous=None
    while True:
        try:
            observation=observe(work)
            temporary=work/'watcher-status.tmp'
            temporary.write_text(json.dumps(observation,indent=2)+'\n')
            temporary.replace(work/'watcher-status.json')
            token=(observation['active_block'],observation['event'],observation['controller_status'])
            if token!=previous:
                event={k:observation[k] for k in ['observed_epoch','active_block','event','controller_status',
                    'native_command_return_marker','observed_native_iteration','controller_alive']}
                with (work/'watcher-events.jsonl').open('a') as stream:
                    stream.write(json.dumps(event)+'\n')
                previous=token
            if args.once:
                print(json.dumps(observation))
                break
            if observation['controller_status']=='COMPLETE':
                break
        except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
            # A transient read/probe error cannot authorize solver commands.
            print('WATCHER_PROBE_ERROR',type(exc).__name__,flush=True)
            if args.once: raise
        time.sleep(max(5,args.interval))


if __name__=='__main__':
    main()
