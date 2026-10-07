"""Deploy08b settings/new997k OFF continuation to the owned Server2."""
import sys,json,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase8_08b_native997k_off2000 as trial
r=trial.r
import deploy_phase8_stage2 as deployment
from deploy_phase8_stage2 import quote
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new
HOST_REPO=trial.transfer.BASE_WORK/'controller-repo-08b-off2000'
HOST_OUT=HOST_REPO/'PyAnsys/output/phase8-stage2/20261007/08b-native997k/run2000-off'
r.HOST_PYTHON=trial.transfer.BASE_WORK/'controller-venv/Scripts/python.exe'
r.HOST_RUNNER='run_phase8_08b_native997k_off2000.py';r.HOST_VERIFIER='verify_phase8_08b_native997k_off2000.py';r.HOST_JOB_ID='phase8-08b-settings-new997k-off2000'
r.HOST_TASK='Original08b settings with new997604 mesh,absorberOFF,2000additional carrier iterations,N10000 to12000,Server2 only'
r.HOST_COMPLETION='N12000,OFFthroughout,08b settings retained,paired reopen/hashes,17report histories,checkpointN11000'
deployment.HOST_REPO=HOST_REPO;deployment.HOST_OUT=HOST_OUT

def main():
 s=r.attach();b=json.loads((r.OUT/'build.json').read_text());assert trial.native(s)==10000;trial.audit(s,b['reference'])
 for name in ['run-manifest.json','job-manifest.json']:assert not r.remote_file_exists(s,str(HOST_OUT/name))
 for old in ['controller-repo-step-enable2200','controller-repo-slow-enable3000-retry01']:
  path=trial.transfer.BASE_WORK/old/'PyAnsys/output/phase8-stage2/20261007'/('step-enable2200' if 'step-enable' in old else 'slow-enable3000')/'job-manifest.json'
  assert json.loads(r.read_text(s,str(path)))['status']=='BLOCKED'
 receipt=deployment.upload(s)
 spec=HOST_REPO/'phase8-stage2-job.json';details=resolve_connection_kwargs('2',start_transcript=False)
 token=uuid.uuid4().hex[:8];script=r.WORK/('private-launch-'+token+'.ps1');pid=r.WORK/'worker-pid.json';launcher=r.WORK/'launcher-pid.json'
 values={'FLUENT_IP2':details['ip'],'FLUENT_PORT2':details['port'],'FLUENT_PASSWORD2':details['password'],'FLUENT_ALLOW_REMOTE_HOST2':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE2':str(details['insecure_mode']).lower()}
 text="$ErrorActionPreference='Stop'\nStart-Sleep -Seconds 15\n"
 for key,value in values.items():text+='$env:'+key+' = '+quote(value)+'\n'
 text+='$p=Start-Process -FilePath '+quote(r.HOST_PYTHON)+" -ArgumentList '-u',"+quote(HOST_REPO/'PyAnsys/scripts/orchestration/run_and_handoff.py')+",'--job',"+quote(spec)+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(r.WORK/'worker.stdout.log')+' -RedirectStandardError '+quote(r.WORK/'worker.stderr.log')+' -PassThru\n'
 text+='[IO.File]::WriteAllText('+quote(pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 write_ascii_text_new(s,str(script),text)
 r.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(script)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
 command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
 r.powershell(s,"$ErrorActionPreference='Stop'; $result=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(r.WORK)+"}; [IO.File]::WriteAllText("+quote(launcher)+",($result|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)")
 launch=json.loads(r.read_text(s,str(launcher)));assert launch['ReturnValue']==0
 launch.update(server_id='2',job_manifest=str(HOST_OUT/'job-manifest.json'),runner_log=str(HOST_OUT/'runner.log'),worker_pid_receipt=str(pid),native_before_launch=10000,method='Detached Windows Python controller; no Fluent launch/restart')
 r.dump(r.OUT/'host-launch.json',launch);print(json.dumps(launch),flush=True)
if __name__=='__main__':main()
