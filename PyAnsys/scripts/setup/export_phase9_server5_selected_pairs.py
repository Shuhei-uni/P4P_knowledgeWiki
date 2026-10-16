"""One-shot selected-pair export. Never loads, solves, exits or restarts Fluent."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
OUT=ROOT/'output/phase9-ewf-server5/20261009'


def write_receipt(data):
    path=OUT/'onedrive-export-status.json'
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data,indent=2)+'\n');temporary.replace(path)


def attempt():
    from phase9_server5_common import attach,run
    config=json.loads((OUT/'onedrive-copy-config.json').read_text())
    s=attach()
    destination=run.SHARED/config['destination_relative']
    proofpath=str(destination/'copy-verification.json')
    from pyansys_fluent.common import remote_file_exists
    if remote_file_exists(s,proofpath):
        proof=json.loads(run.read_text(s,proofpath).lstrip('\ufeff'))
        if proof.get('status')=='COPIED_SOURCE_AND_DESTINATION_HASH_VERIFIED':
            verify_proof(proof,config);write_receipt(proof);return
    folder=run.WORK/'342k'/'selected-pair-export'
    run.ensure_remote_directory(s,str(folder))
    stamp=str(time.time_ns())
    ps=folder/(stamp+'.ps1');cfg=folder/(stamp+'.json')
    run.write_ascii_text_new(s,str(ps),(ROOT/'scripts/setup/copy_phase9_server5_selected_pairs.ps1').read_text())
    run.write_ascii_text_new(s,str(cfg),json.dumps(config,ensure_ascii=True,indent=2))
    literal=lambda value:"'"+str(value).replace("'","''")+"'"
    code="$ErrorActionPreference='Stop'; & "+literal(ps)+' -ConfigPath '+literal(cfg)
    result=run.base.powershell(s,code)
    if result not in (0,None):raise RuntimeError('Windows file export failed; inspect copy-verification.json')
    proof=json.loads(run.read_text(s,proofpath).lstrip('\ufeff'))
    verify_proof(proof,config);write_receipt(proof)


def verify_proof(proof,config):
    if proof.get('status')!='COPIED_SOURCE_AND_DESTINATION_HASH_VERIFIED':raise RuntimeError('Copy verification did not pass')
    expected={x['name']:x['sha256'] for x in config['files']}
    actual={x['name']:x['sha256'] for x in proof['files']}
    if actual!=expected or any(x['bytes']<=0 for x in proof['files']):raise RuntimeError('Exported pair identities differ')


def ready():
    import grpc
    from grpc_health.v1 import health_pb2,health_pb2_grpc
    from ansys.api.fluent.v0 import scheme_eval_pb2,scheme_eval_pb2_grpc
    from pyansys_fluent.connection import resolve_connection_kwargs
    try:
        kw=resolve_connection_kwargs('5',start_transcript=False,tcp_timeout_seconds=3)
        with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
            md=(('password',kw['password']),)
            if health_pb2_grpc.HealthStub(channel).Check(health_pb2.HealthCheckRequest(),metadata=md,timeout=5).status!=1:return False
            scheme_eval_pb2_grpc.SchemeEvalStub(channel).StringEval(scheme_eval_pb2.StringEvalRequest(input='(cx-version)'),metadata=md,timeout=5)
        return True
    except (grpc.RpcError,TimeoutError):return False


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',action='store_true');args=parser.parse_args()
    if args.attempt:attempt();return
    import fcntl
    lock=(OUT/'onedrive-export.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    while True:
        if ready():
            with (OUT/'onedrive-export-attempt.log').open('a') as log:
                child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--attempt'],cwd=ROOT.parent,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
                try:child.wait(timeout=180)
                except subprocess.TimeoutExpired:
                    child.terminate();child.wait()
            receipt=json.loads((OUT/'onedrive-export-status.json').read_text()) if (OUT/'onedrive-export-status.json').exists() else {}
            if receipt.get('status')=='COPIED_SOURCE_AND_DESTINATION_HASH_VERIFIED':
                codex=shutil.which('codex')
                if codex:
                    prompt=f'Server 5 selected-pair OneDrive export completed. Read {OUT}/onedrive-export-status.json, verify the four copied case/data files from another synced computer if available, and report their folder and hashes. Do not resume any simulation, watcher, or continuation. Selected final endpoint remains frozen 195ms; never exit or restart Fluent. Server 5 only.'
                    subprocess.run([codex,'queue','--thread','01a11318-855f-7d63-8a0c-76f4eb8e3c08','--message',prompt],capture_output=True,text=True,timeout=20)
                return
        write_receipt({'status':'WAITING_FOR_SERVER5_FILE_EXPORT','pid':os.getpid(),'server_id':'5','observed_unix_s':time.time(),'fluent_solve_load_exit_restart_commands':0})
        time.sleep(30)


if __name__=='__main__':main()
