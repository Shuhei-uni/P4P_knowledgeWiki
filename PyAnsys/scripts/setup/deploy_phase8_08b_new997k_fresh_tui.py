"""Launch native journal from a detached Server2 process; no laptop dependency."""
from pathlib import Path
import sys,json,uuid
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_phase8_08b_new997k_fresh_tui10000 as fresh
r=fresh.r
from pyansys_fluent.remote_text import write_ascii_text_new
from pyansys_fluent.connection import resolve_connection_kwargs
HOST_REPO=fresh.old.transfer.BASE_WORK/'controller-repo-08b-off2000'
HOST_PYTHON=fresh.old.transfer.BASE_WORK/'controller-venv/Scripts/python.exe'

def main():
 s=r.attach();b=json.loads((fresh.OUT/'build.json').read_text());fresh.old.OUT=fresh.OUT;fresh.old.WORK=fresh.WORK;fresh.old.audit(s,b['reference']);assert fresh.old.native(s)==0
 root=fresh.WORK
 for name in ['job-manifest.json','run-manifest.json','journal-endpoint.cas.h5','journal-endpoint.dat.h5']:assert not r.remote_file_exists(s,str(root/name))
 driver=root/'native-journal-driver.py';source=(r.ROOT/'scripts/setup/phase8_08b_new997k_fresh_tui_hostdriver.py').read_text();write_ascii_text_new(s,str(driver),source)
 worker=HOST_REPO/'PyAnsys/scripts/orchestration/run_and_handoff.py'
 spec={'job':{'id':'phase8-08b-settings-new997k-fresh-tui10000-off','mode':'utility','manifest':str(root/'job-manifest.json'),'worker_log':str(root/'worker.log')},'runner':{'command':[str(HOST_PYTHON),'-u',str(driver),str(HOST_REPO/'PyAnsys/scripts/setup'),str(root)],'cwd':str(root),'log':str(root/'driver.log')},'completion':{'required_files':[str(root/name) for name in ['run-manifest.json','report-histories.json','final-reopen.json','journal-endpoint.cas.h5','journal-endpoint.dat.h5','raw/native-run.trn']]},'codex':{'enabled':False},'originating_task':'User-authorized fresh initialization,08b settings/new997604mesh,absorberOFF,one native TUI iterate10000,laptop mayclose'}
 job=root/'native-journal-job.json';write_ascii_text_new(s,str(job),json.dumps(spec,indent=2)+'\n');r.dump(fresh.OUT/'host-job-spec.json',spec)
 details=resolve_connection_kwargs('2',start_transcript=False);token=uuid.uuid4().hex[:8];script=root/('private-launch-'+token+'.ps1');pid=root/'worker-pid.json';launcher=root/'launcher-pid.json'
 values={'FLUENT_IP2':details['ip'],'FLUENT_PORT2':details['port'],'FLUENT_PASSWORD2':details['password'],'FLUENT_ALLOW_REMOTE_HOST2':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE2':str(details['insecure_mode']).lower()}
 text="$ErrorActionPreference='Stop'\nStart-Sleep -Seconds 15\n"
 for key,value in values.items():text+='$env:'+key+' = '+r.q(value)+'\n'
 text+='$p=Start-Process -FilePath '+r.q(HOST_PYTHON)+" -ArgumentList '-u',"+r.q(worker)+",'--job',"+r.q(job)+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+r.q(root/'worker.stdout.log')+' -RedirectStandardError '+r.q(root/'worker.stderr.log')+' -PassThru\n'
 text+='[IO.File]::WriteAllText('+r.q(pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 write_ascii_text_new(s,str(script),text)
 r.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+r.q(script)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
 command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
 r.powershell(s,"$result=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+r.q(command)+';CurrentDirectory='+r.q(root)+"}; [IO.File]::WriteAllText("+r.q(launcher)+",($result|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)")
 launch=json.loads(r.read_text(s,str(launcher)));assert launch['ReturnValue']==0
 launch.update(server_id='2',execution_host='SERVER2_WINDOWS',laptop_required=False,journal=str(root/'run10000-off.jou'),tui_command='/solve/iterate 10000',job_manifest=str(root/'job-manifest.json'),run_manifest=str(root/'run-manifest.json'),native_transcript=str(root/'raw/native-run.trn'),native_before_launch=0)
 r.dump(fresh.OUT/'host-launch.json',launch);print(json.dumps(launch),flush=True)
if __name__=='__main__':main()
