"""Run checkpoint selection on Server1 independently of the laptop."""
import base64,hashlib,json,time
from pathlib import PureWindowsPath
from phase9_server1_680k_common import run,OUT,ROOT
from phase9_server1_file_transport import attach_files
from deploy_phase9_server1_680k_ewf import quote
from pyansys_fluent.connection import resolve_connection_kwargs

def main():
 old=json.loads((OUT/'resume-host-launch.json').read_text());tag=str(time.time_ns())
 repo=PureWindowsPath(old['host_repo']);hostout=PureWindowsPath(old['host_output']);s=attach_files(old['host_repo'])
 m=json.loads(run.read_text(s,old['run_manifest']))
 assert m['status']=='COMPLETE_VERIFIED' and m['verified_native_end']==104080
 source=ROOT/'scripts/setup/save_phase9_server1_selected_pairs.py';target=repo/'PyAnsys/scripts/setup'/('save_phase9_server1_selected_pairs-'+tag+'.py')
 staged=run.WORK/('selected-pairs-'+tag+'.b64');run.write_ascii_text_new(s,str(staged),base64.b64encode(source.read_bytes()).decode())
 check=run.WORK/('selected-pairs-hash-'+tag+'.txt')
 code="$ErrorActionPreference='Stop'; if(Test-Path -LiteralPath "+quote(target)+") {throw 'Staged path exists'}; [IO.File]::WriteAllBytes("+quote(target)+",[Convert]::FromBase64String([IO.File]::ReadAllText("+quote(staged)+"))); [IO.File]::WriteAllText("+quote(check)+",(Get-FileHash -LiteralPath "+quote(target)+" -Algorithm SHA256).Hash,[Text.Encoding]::ASCII)"
 assert run.base.powershell(s,code) in (0,None)
 digest=run.read_text(s,str(check)).strip().lower();assert digest==hashlib.sha256(source.read_bytes()).hexdigest()
 python=old['host_python'];specpath=repo/('server1-selected-pairs-'+tag+'.json');jobmanifest=hostout/('selected-pairs-job-'+tag+'.json');receipt=hostout/('selected-checkpoints-'+tag+'.json');log=hostout/('selected-pairs-runner-'+tag+'.log')
 spec={'job':{'id':'server1-selected-pairs-'+tag,'mode':'utility','manifest':str(jobmanifest),'worker_log':str(hostout/('selected-pairs-worker-'+tag+'.log'))},'runner':{'command':[python,'-E','-u',str(target),'--tag',tag],'cwd':str(repo),'log':str(log)},'completion':{'required_files':[str(receipt)]},'codex':{'enabled':False},'originating_task':'Human: also save freeze-onset and195ms pairs; preserve live200ms endpoint; no solve'}
 run.write_ascii_text_new(s,str(specpath),json.dumps(spec,indent=2)+'\n')
 details=resolve_connection_kwargs('1',start_transcript=False);private=run.WORK/('private-selected-pairs-'+tag+'.ps1');pidpath=run.WORK/('selected-pairs-pid-'+tag+'.json');launchpath=run.WORK/('selected-pairs-launch-'+tag+'.json')
 text="$ErrorActionPreference='Stop'\n"
 for key,value in {'FLUENT_IP':details['ip'],'FLUENT_PORT':details['port'],'FLUENT_PASSWORD':details['password'],'FLUENT_ALLOW_REMOTE_HOST':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE':str(details['insecure_mode']).lower()}.items():text+='$env:'+key+' = '+quote(value)+'\n'
 worker=repo/'PyAnsys/scripts/orchestration/run_and_handoff.py'
 text+='$p=Start-Process -FilePath '+quote(python)+" -ArgumentList '-E','-u',"+quote(worker)+",'--job',"+quote(specpath)+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(hostout/('selected-pairs-stdout-'+tag+'.log'))+' -RedirectStandardError '+quote(hostout/('selected-pairs-stderr-'+tag+'.log'))+' -PassThru\n'
 text+='[IO.File]::WriteAllText('+quote(pidpath)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 run.write_ascii_text_new(s,str(private),text)
 assert run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(private)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null") in (0,None)
 command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(private)+'"'
 code="$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(run.WORK)+"}; [IO.File]::WriteAllText("+quote(launchpath)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)"
 assert run.base.powershell(s,code) in (0,None)
 launch=json.loads(run.read_text(s,str(launchpath)));assert launch['ReturnValue']==0
 r={'status':'SELECTED_PAIR_EXPORT_DISPATCHED','tag':tag,'host_receipt':str(receipt),'job_manifest':str(jobmanifest),'runner_log':str(log),'source_path':str(target),'source_sha256':digest,'host_repo':str(repo),'laptop_required':False,'new_iterations':0,'launcher':launch}
 run.dump(OUT/'selected-pairs-export-launch.json',r);print(json.dumps(r,indent=2))

if __name__=='__main__':main()
