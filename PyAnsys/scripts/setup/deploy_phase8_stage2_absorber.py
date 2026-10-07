"""Deploy and launch a fresh 3000-update full-feed trial."""
import sys,json,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase8_stage2_absorber as trial
trial.BASE_WORK=trial.trial.BASE_WORK
r=trial.base
import deploy_phase8_stage2 as deployment
from deploy_phase8_stage2 import quote
HOST_REPO=trial.BASE_WORK/"controller-repo-absorber3000-retry02"
HOST_OUT=HOST_REPO/"PyAnsys/output/phase8-stage2/20261007/absorber3000"
r.HOST_PYTHON=trial.BASE_WORK/"controller-venv/Scripts/python.exe"
r.HOST_RUNNER="run_phase8_stage2_absorber.py"
r.HOST_VERIFIER="verify_phase8_stage2_absorber.py"
r.HOST_JOB_ID="phase8-stage2-absorber3000"
r.HOST_TASK="Fresh F2 SIMPLE 997604 cells; full feed from N0; 3000 total updates; Server 2 only"
r.HOST_COMPLETION="N3000 save/reopen, full feed, hashes, checkpoints and all 18 histories"
deployment.HOST_REPO=HOST_REPO;deployment.HOST_OUT=HOST_OUT
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
 s=r.attach()
 old=trial.trial.BASE_WORK/'controller-repo-absorber3000-retry01/PyAnsys/output/phase8-stage2/20261007/absorber3000/job-manifest.json'
 assert json.loads(r.read_text(s,str(old)))['status']=='BLOCKED'
 r.remote_chdir(s,r'C:\Users\syok443')
 assert not r.remote_file_exists(s,str(HOST_OUT/'run-manifest.json'))
 assert r.native(s)==0
 trial.audit(s)
 assert not r.remote_file_exists(s,str(HOST_OUT/'job-manifest.json'))
 deployment.upload(s)
 job=json.loads(r.read_text(s,str(HOST_REPO/'phase8-stage2-job.json')))
 job['job'].update(id='phase8-stage2-absorber3000',manifest=str(HOST_OUT/'job-manifest.json'),worker_log=str(HOST_OUT/'worker.log'))
 job['runner']['log']=str(HOST_OUT/'runner.log');job['completion']['verifier_log']=str(HOST_OUT/'verifier.log')
 spec=HOST_REPO/'phase8-stage2-absorber3000-job.json'
 assert not r.remote_file_exists(s,str(HOST_OUT/'job-manifest.json'))
 write_ascii_text_new(s,str(spec),json.dumps(job,indent=2)+'\n')
 details=resolve_connection_kwargs('2',start_transcript=False)
 token=uuid.uuid4().hex[:8];script=r.WORK/('private-retry-launch-'+token+'.ps1');worker_pid=r.WORK/'absorber3000-worker-pid.json';launcher_pid=r.WORK/'absorber3000-launcher-pid.json'
 values={'FLUENT_IP2':details['ip'],'FLUENT_PORT2':details['port'],'FLUENT_PASSWORD2':details['password'],'FLUENT_ALLOW_REMOTE_HOST2':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE2':str(details['insecure_mode']).lower()}
 text="$ErrorActionPreference='Stop'\nStart-Sleep -Seconds 15\n"
 for key,value in values.items():text+='$env:'+key+' = '+quote(value)+'\n'
 text+='$p=Start-Process -FilePath '+quote(r.HOST_PYTHON)+" -ArgumentList '-u',"+quote(HOST_REPO/'PyAnsys/scripts/orchestration/run_and_handoff.py')+",'--job',"+quote(spec)+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(r.WORK/'absorber3000-worker.stdout.log')+' -RedirectStandardError '+quote(r.WORK/'absorber3000-worker.stderr.log')+' -PassThru\n'
 text+='[IO.File]::WriteAllText('+quote(worker_pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 write_ascii_text_new(s,str(script),text)
 r.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(script)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
 command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
 code="$ErrorActionPreference='Stop'; $result=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(r.WORK)+"}; [IO.File]::WriteAllText("+quote(launcher_pid)+",($result|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)"
 r.powershell(s,code)
 receipt=json.loads(r.read_text(s,str(launcher_pid)));assert receipt['ReturnValue']==0,receipt
 receipt.update(server_id='2',job_manifest=str(HOST_OUT/'job-manifest.json'),runner_log=str(HOST_OUT/'runner.log'),worker_pid_receipt=str(worker_pid),method='WMI detached launcher; no Fluent process launch',native_verified_before_launch=0)
 r.dump(r.OUT/'host-absorber3000-retry02-launch.json',receipt);print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
