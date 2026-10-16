"""Stage limit-free continuation without modifying the active controller."""
from pathlib import PureWindowsPath
import json,time,base64,hashlib
from phase9_server1_680k_common import run,OUT,ROOT
from phase9_server1_file_transport import attach_files
from deploy_phase9_server1_680k_ewf import quote
from pyansys_fluent.connection import resolve_connection_kwargs


def main():
 launch=json.loads((OUT/'resume-host-launch.json').read_text());repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output']);tag=str(time.time_ns())
 assert launch['bounded_count'] is None and launch['fixed_step_s']==1e-6
 # This attachment is used only for host file/process operations. No settings,
 # iteration, interrupt, save or load commands are sent to the active solver.
 s=attach_files(launch['host_repo'])
 deployed={}
 for key,relative in [('queue','scripts/orchestration/continue_phase9_server1_without_limits.py'),('runner','scripts/setup/run_phase9_server1_680k_ewf.py'),('verifier','scripts/inspection/verify_phase9_server1_680k_ewf.py')]:
  local=ROOT/relative;target=repo/'PyAnsys'/str(PureWindowsPath(relative).parent)/(local.stem+'-no-limits-'+tag+'.py')
  stage=run.WORK/('no-limits-'+key+'-'+tag+'.b64');run.write_ascii_text_new(s,str(stage),base64.b64encode(local.read_bytes()).decode())
  digestpath=run.WORK/'680k/scratch'/('no-limits-hash-'+key+'-'+tag+'.txt')
  code="$ErrorActionPreference='Stop'; if(Test-Path -LiteralPath "+quote(target)+") {throw 'Unique staged path already exists'}; [IO.File]::WriteAllBytes("+quote(target)+",[Convert]::FromBase64String([IO.File]::ReadAllText("+quote(stage)+"))); [IO.File]::WriteAllText("+quote(digestpath)+",(Get-FileHash -LiteralPath "+quote(target)+" -Algorithm SHA256).Hash,[Text.Encoding]::ASCII)"
  assert run.base.powershell(s,code) in (0,None)
  digest=run.read_text(s,str(digestpath)).strip().lower();assert digest==hashlib.sha256(local.read_bytes()).hexdigest()
  deployed[key]={'path':str(target),'sha256':digest}
 target=PureWindowsPath(deployed['queue']['path']);digest=deployed['queue']['sha256']
 specpath=repo/('server1-no-limits-'+tag+'.json');receipt=hostout/('no-limits-continuation-'+tag+'.json')
 parent_job=PureWindowsPath(launch['job_spec']).stem
 spec={'repo':str(repo),'parent_job_id':parent_job,'parent_job_manifest':launch['job_manifest'],'run_manifest':launch['run_manifest'],'receipt':str(receipt),'runner':deployed['runner']['path'],'runner_sha256':deployed['runner']['sha256'],'verifier':deployed['verifier']['path'],'verifier_sha256':deployed['verifier']['sha256'],'runner_log':str(hostout/('no-limits-runner-'+tag+'.log')),'verifier_log':str(hostout/('no-limits-verifier-'+tag+'.log')),'authority':'human: remove all limit checks; run to final film time unless error; 20261012'}
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
 r={'status':'NO_LIMITS_CONTINUATION_DISPATCHED','host_receipt':str(receipt),'host_spec':str(specpath),'parent_job_id':parent_job,'parent_job_manifest':launch['job_manifest'],'deployed':deployed,'target_film_s':.2,'target_native':185080,'numerical_limit_checks':False,'laptop_required':False,'current_controller_modified':False,'current_solve_interrupted':False,'codex_wakeup_required':False,'launcher':start,'authority':spec['authority']}
 run.dump(OUT/'no-limits-continuation-launch.json',r);print(json.dumps(r,indent=2),flush=True)

if __name__=='__main__':main()
