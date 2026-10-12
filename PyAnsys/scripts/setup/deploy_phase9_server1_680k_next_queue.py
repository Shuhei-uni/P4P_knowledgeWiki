"""Stage a separate next-command queue without modifying the active solve."""
from pathlib import PureWindowsPath
import json,time,base64,hashlib
from phase9_server1_680k_common import run,OUT,ROOT
from phase9_server1_file_transport import attach_files
from deploy_phase9_server1_680k_ewf import quote
from pyansys_fluent.connection import resolve_connection_kwargs


def main():
 launch=json.loads((OUT/'resume-host-launch.json').read_text());repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output']);tag=str(time.time_ns())
 assert launch['bounded_count']==3000 and launch['fixed_step_s']==1e-6
 # This attachment is used only for host file/process operations. No settings,
 # iteration, interrupt, save or load commands are sent to the active solver.
 s=attach_files(launch['host_repo'])
 local=ROOT/'scripts/orchestration/queue_phase9_server1_680k_next.py';target=repo/'PyAnsys/scripts/orchestration'/('queue_phase9_server1_680k_next-'+tag+'.py')
 stage=run.WORK/('next-queue-'+tag+'.b64');run.write_ascii_text_new(s,str(stage),base64.b64encode(local.read_bytes()).decode())
 digestpath=run.WORK/'680k/scratch'/('queue-hash-'+tag+'.txt')
 code="$ErrorActionPreference='Stop'; if(Test-Path -LiteralPath "+quote(target)+") {throw 'Unique queue path already exists'}; [IO.File]::WriteAllBytes("+quote(target)+",[Convert]::FromBase64String([IO.File]::ReadAllText("+quote(stage)+"))); [IO.File]::WriteAllText("+quote(digestpath)+",(Get-FileHash -LiteralPath "+quote(target)+" -Algorithm SHA256).Hash,[Text.Encoding]::ASCII)"
 assert run.base.powershell(s,code) in (0,None)
 digest=run.read_text(s,str(digestpath)).strip().lower();assert digest==hashlib.sha256(local.read_bytes()).hexdigest()
 specpath=repo/('server1-next-queue-'+tag+'.json');receipt=hostout/('next-command-queue-'+tag+'.json')
 parent_job=PureWindowsPath(launch['job_spec']).stem
 spec={'repo':str(repo),'parent_job_id':parent_job,'parent_job_manifest':launch['job_manifest'],'run_manifest':launch['run_manifest'],'reopen':str(hostout/'final-reopen.json'),'receipt':str(receipt),'runner':str(repo/'PyAnsys/scripts/setup/run_phase9_server1_680k_ewf.py'),'runner_sha256':launch['changes']['scripts/setup/run_phase9_server1_680k_ewf.py']['after'],'verifier':str(repo/'PyAnsys/scripts/inspection/verify_phase9_server1_680k_ewf.py'),'verifier_sha256':launch['changes']['scripts/inspection/verify_phase9_server1_680k_ewf.py']['after'],'runner_log':str(hostout/('queued-runner-'+tag+'.log')),'verifier_log':str(hostout/('queued-verifier-'+tag+'.log')),'cancel_file':str(hostout/('next-command-queue-'+tag+'.cancel'))}
 # Job spec basename is the owned job ID in the existing run-and-handoff worker.
 assert parent_job.startswith('phase9-server1-680k-resume-')
 run.write_ascii_text_new(s,str(specpath),json.dumps(spec,indent=2)+'\n')
 details=resolve_connection_kwargs('1',start_transcript=False);python=launch['host_python'];private=run.WORK/('private-next-queue-'+tag+'.ps1');pidpath=run.WORK/('next-queue-pid-'+tag+'.json');launchpath=run.WORK/('next-queue-launch-'+tag+'.json')
 values={'FLUENT_IP':details['ip'],'FLUENT_PORT':details['port'],'FLUENT_PASSWORD':details['password'],'FLUENT_ALLOW_REMOTE_HOST':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE':str(details['insecure_mode']).lower()}
 text="$ErrorActionPreference='Stop'\n"
 for key,value in values.items():text+='$env:'+key+' = '+quote(value)+'\n'
 text+='$p=Start-Process -FilePath '+quote(python)+" -ArgumentList '-E','-u',"+quote(target)+",'--spec',"+quote(specpath)+" -WindowStyle Hidden -RedirectStandardOutput "+quote(hostout/('next-queue-stdout-'+tag+'.log'))+' -RedirectStandardError '+quote(hostout/('next-queue-stderr-'+tag+'.log'))+' -PassThru\n'
 text+='[IO.File]::WriteAllText('+quote(pidpath)+",(@{queue_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 run.write_ascii_text_new(s,str(private),text)
 run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(private)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
 command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(private)+'"'
 code="$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(run.WORK)+"}; [IO.File]::WriteAllText("+quote(launchpath)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);start=json.loads(run.read_text(s,str(launchpath)));assert start['ReturnValue']==0
 r={'status':'NEXT_QUEUE_DISPATCHED','host_receipt':str(receipt),'host_spec':str(specpath),'parent_job_id':parent_job,'parent_job_manifest':launch['job_manifest'],'queue_script':str(target),'queue_sha256':digest,'source_hash_guards':{k:spec[k] for k in ['runner_sha256','verifier_sha256']},'current_target_native':24580,'current_target_film_s':.0395,'next_count':3000,'next_step_s':1e-6,'next_target_native':27580,'next_target_film_s':.0425,'courant_limit':.8,'laptop_required':False,'current_controller_modified':False,'current_solve_interrupted':False,'codex_wakeup_required':False,'launcher':start}
 run.dump(OUT/'next-command-queue-launch.json',r);print(json.dumps(r,indent=2),flush=True)

if __name__=='__main__':main()
