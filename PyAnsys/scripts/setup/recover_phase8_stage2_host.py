"""Reconciled N10 continuation, with a detached WMI controller launch."""
import sys,json,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase8_stage2_f2_simple as r
from deploy_phase8_stage2 import HOST_REPO,HOST_OUT,quote
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
 s=r.attach()
 assert not r.remote_file_exists(s,str(HOST_OUT/'run-manifest.json'))
 previous=json.loads(r.read_text(s,str(HOST_OUT/'job-manifest.json')))
 assert previous['status']=='BLOCKED' and previous['runner']['return_code']==1
 assert json.loads((r.OUT/'restart-N10-verification.json').read_text())['native_iteration']==10
 job=json.loads(r.read_text(s,str(HOST_REPO/'phase8-stage2-job.json')))
 job['job'].update(id='phase8-stage2-f2-simple-retry01',manifest=str(HOST_OUT/'job-retry01-manifest.json'),worker_log=str(HOST_OUT/'worker-retry01.log'))
 job['runner']['log']=str(HOST_OUT/'runner-retry01.log');job['completion']['verifier_log']=str(HOST_OUT/'verifier-retry01.log')
 spec=HOST_REPO/'phase8-stage2-retry01-job.json'
 assert not r.remote_file_exists(s,str(HOST_OUT/'job-retry01-manifest.json'))
 write_ascii_text_new(s,str(spec),json.dumps(job,indent=2)+'\n')
 details=resolve_connection_kwargs('2',start_transcript=False)
 token=uuid.uuid4().hex[:8];script=r.WORK/('private-retry-launch-'+token+'.ps1');worker_pid=r.WORK/'retry01-worker-pid.json';launcher_pid=r.WORK/'retry01-launcher-pid.json'
 values={'FLUENT_IP2':details['ip'],'FLUENT_PORT2':details['port'],'FLUENT_PASSWORD2':details['password'],'FLUENT_ALLOW_REMOTE_HOST2':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE2':str(details['insecure_mode']).lower()}
 text="$ErrorActionPreference='Stop'\nStart-Sleep -Seconds 15\n"
 for key,value in values.items():text+='$env:'+key+' = '+quote(value)+'\n'
 text+='$p=Start-Process -FilePath '+quote(r.WORK/'controller-venv/Scripts/python.exe')+" -ArgumentList '-u',"+quote(HOST_REPO/'PyAnsys/scripts/orchestration/run_and_handoff.py')+",'--job',"+quote(spec)+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(r.WORK/'retry01-worker.stdout.log')+' -RedirectStandardError '+quote(r.WORK/'retry01-worker.stderr.log')+' -PassThru\n'
 text+='[IO.File]::WriteAllText('+quote(worker_pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 write_ascii_text_new(s,str(script),text)
 r.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(script)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
 command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
 code="$ErrorActionPreference='Stop'; $result=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(r.WORK)+"}; [IO.File]::WriteAllText("+quote(launcher_pid)+",($result|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)"
 r.powershell(s,code)
 receipt=json.loads(r.read_text(s,str(launcher_pid)));assert receipt['ReturnValue']==0,receipt
 receipt.update(server_id='2',job_manifest=str(HOST_OUT/'job-retry01-manifest.json'),runner_log=str(HOST_OUT/'runner-retry01.log'),worker_pid_receipt=str(worker_pid),method='WMI detached launcher; no Fluent process launch',native_verified_before_launch=10)
 r.dump(r.OUT/'host-retry01-launch.json',receipt);print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
