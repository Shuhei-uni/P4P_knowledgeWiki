"""Read-only continuous supervision and final OneDrive hash checks for the campaign."""
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'scripts/setup')]
from run_phase72a_e27_server1_continuation import dump

CAMPAIGN = ROOT/'output/phase72a-stage3-speed-sensitivity-server1/20261006'
CLOUD = Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase72A/Stage3/speed-sensitivity-500ms/20261006')
PATTERN = re.compile(r'Film time = (\S+) with timestep = (\S+), \(max_cfl: (\S+)\)')


def snapshot():
    job = json.loads((CAMPAIGN/'run-manifest.json').read_text())
    alive = True
    try:
        os.kill(job['pid'], 0)
    except ProcessLookupError:
        alive = False
    label = job.get('active_case')
    source = Path(job['active_run_manifest']) if job.get('active_run_manifest') else None
    arm_manifest = CAMPAIGN/str(label)/'film-development/run-manifest.json'
    if label in ['low', 'high'] and arm_manifest.exists():
        source = arm_manifest
    run = json.loads(source.read_text()) if source and source.exists() else {}
    transcript = Path(job['active_client_transcript']) if job.get('active_client_transcript') else None
    if run.get('status')=='RUNNING' and run.get('active_target') and run.get('active_output'):
        transcript = Path(run['active_output'])/f"batch-N{run['verified_native_end']}-N{run['active_target']}.txt"
    messages = []
    age = None
    if transcript and transcript.exists():
        with transcript.open('rb') as stream:
            stream.seek(max(0, transcript.stat().st_size-65536))
            messages = PATTERN.findall(stream.read().decode(errors='replace'))
        age = time.time()-transcript.stat().st_mtime
    result = {'observed_utc':datetime.now(timezone.utc).isoformat(), 'monitor_pid':os.getpid(),
              'controller_alive':alive, 'controller_status':job['status'], 'active_case':label,
              'source_run_manifest':str(source) if source else None,
              'verified_native_end':run.get('verified_native_end'), 'active_native_target':run.get('active_target'),
              'latest_verified_metrics':run.get('latest_metrics'), 'stream_age_seconds':age,
              'streamed_film_time_s':float(messages[-1][0]) if messages else None,
              'printed_step_s':float(messages[-1][1]) if messages else None,
              'streamed_film_cfl':float(messages[-1][2]) if messages else None,
              'status':'RUNNING_STREAM_ACTIVE'}
    if not alive and job['status']!='COMPLETE':
        result.update(status='CONTROLLER_EXITED_RECOVERY_REQUIRED', error=job.get('error'))
    elif job['status']=='RECOVERY_REQUIRED':
        result.update(status='RECOVERY_REQUIRED', error=job.get('error'))
    elif run.get('status')=='RUNNING' and age is not None and age>180:
        result['status']='STREAM_STALE_NATIVE_STATE_CHECK_REQUIRED'
    elif run.get('status')!='RUNNING' or not run.get('active_target'):
        result['status']='CHECKPOINT_OR_CASE_PREPARATION'
    verified = {}
    for case, entry in job['cases'].items():
        if entry['status']!='COMPLETE_500MS':
            continue
        files = {}
        for kind, item in entry['shared'].items():
            path = CLOUD/case/PureWindowsPath(item['path']).name
            if not path.exists():
                files[kind]={'status':'SYNC_PENDING','path':str(path)}
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            files[kind]={'status':'PASS' if digest==item['sha256'] else 'HASH_MISMATCH',
                         'path':str(path),'sha256':digest,'expected_sha256':item['sha256'],
                         'bytes':path.stat().st_size}
        verified[case]={'status':'PASS' if all(x['status']=='PASS' for x in files.values()) else 'PENDING_OR_MISMATCH',
                        'film_time_s':entry['film_time_s'],'files':files}
    result['final_mac_verification']=verified
    if job['status']=='COMPLETE':
        result['status']='COMPLETE_VERIFIED' if len(verified)==3 and all(x['status']=='PASS' for x in verified.values()) else 'FINAL_ONEDRIVE_VERIFICATION_PENDING'
    return result


def main():
    previous = None
    while True:
        try:
            result = snapshot()
            dump(CAMPAIGN/'monitor-state.json',result)
            marker=(result['status'],result['active_case'],result['verified_native_end'])
            if marker!=previous:
                print('MONITOR',json.dumps({k:result[k] for k in ['status','active_case','verified_native_end','active_native_target','streamed_film_time_s']}),flush=True)
                previous=marker
            if result['status']=='COMPLETE_VERIFIED':
                return
        except Exception as error:
            print('MONITOR_READ_RETRY',repr(error),flush=True)
        time.sleep(20)


if __name__=='__main__':
    main()
