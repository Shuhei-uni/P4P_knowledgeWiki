"""Preserve terminal deployment and resume the verified Server 1 checkpoint."""
from pathlib import Path,PureWindowsPath
import argparse,base64,hashlib,json,time
from phase9_server1_680k_common import run,attach,OUT,ROOT
from deploy_phase9_server1_680k_ewf import quote
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--recovery-step',type=float,choices=[1e-7,1e-6,2.5e-6]);parser.add_argument('--bounded-count',type=int);args=parser.parse_args()
 s=attach();run.require_idle(s)
 native=run.native_iteration(s)
 old=json.loads((OUT/'host-launch.json').read_text());tag=str(time.time_ns())
 host_repo=PureWindowsPath(old['host_repo']);host_out=PureWindowsPath(old['host_output']);python=old['host_python']
 m=json.loads(run.read_text(s,str(host_out/'run-manifest.json')))
 assert m['status'] in ['RECOVERY_REQUIRED','BOUNDED_COMPLETE_VERIFIED'] and m['verified_native_end']==native and m['server_id']=='1' and m['cells']==679970
 # Reject any surviving controller, without terminating any process.
 probe=run.WORK/('resume-process-'+tag+'.json')
 code="$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -match 'run_phase9_server1_680k_ewf.py|run_and_handoff.py' }); [IO.File]::WriteAllText("+quote(probe)+",(@{count=$p.Count}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);assert json.loads(run.read_text(s,str(probe)))['count']==0
 run.dump(OUT/('host-run-manifest-before-resume-'+tag+'.json'),m)
 changes={}
 for relative,backup in [('scripts/setup/run_phase9_server1_680k_ewf.py','/tmp/phase9-original-controller.py'),('scripts/inspection/verify_phase9_server1_680k_ewf.py','/tmp/phase9-original-verifier.py')]:
  local=ROOT/relative;target=host_repo/'PyAnsys'/relative
  expected=hashlib.sha256(Path(backup).read_bytes()).hexdigest()
  deployed=run.read_text(s,str(target))
  if deployed.replace('\r\n','\n') not in [Path(backup).read_text(),local.read_text()]:raise RuntimeError('Unexpected runtime source change')
  oldhash=hashlib.sha256(deployed.encode()).hexdigest()
  staged=run.WORK/('resume-'+tag+'-'+target.name+'.b64');write_ascii_text_new(s,str(staged),base64.b64encode(local.read_bytes()).decode())
  digestpath=run.WORK/'680k/scratch'/('new-hash-'+target.name+'-'+tag+'.txt')
  code="$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(target)+' -Destination '+quote(str(target)+'.before-'+tag)+"; [IO.File]::WriteAllBytes("+quote(target)+",[Convert]::FromBase64String([IO.File]::ReadAllText("+quote(staged)+"))); [IO.File]::WriteAllText("+quote(digestpath)+",(Get-FileHash -LiteralPath "+quote(target)+" -Algorithm SHA256).Hash,[Text.Encoding]::ASCII)"
  if run.base.powershell(s,code) not in (0,None):raise RuntimeError('Runtime replacement failed')
  digest=run.read_text(s,str(digestpath)).strip().lower()
  assert digest==hashlib.sha256(local.read_bytes()).hexdigest()
  changes[relative]={'before':oldhash,'after':digest}
 specpath=host_repo/('phase9-server1-680k-resume-'+tag+'.json')
 jobmanifest=host_out/('resume-job-manifest-'+tag+'.json');runnerlog=host_out/('resume-runner-'+tag+'.log')
 spec={'job':{'id':'phase9-server1-680k-resume-'+tag,'mode':'utility','manifest':str(jobmanifest),'worker_log':str(host_out/('resume-worker-'+tag+'.log'))},'runner':{'command':[python,'-E','-u',str(host_repo/'PyAnsys/scripts/setup/run_phase9_server1_680k_ewf.py'),'--resume','--ledger-diagnostic-only']+(['--recovery-step',str(args.recovery_step)] if args.recovery_step is not None else [])+(['--bounded-count',str(args.bounded_count)] if args.bounded_count is not None else []),'cwd':str(host_repo),'log':str(runnerlog)},'completion':{'required_files':[str(host_out/'run-manifest.json'),str(host_out/'final-reopen.json')],'verifier_command':[python,'-E',str(host_repo/'PyAnsys/scripts/inspection/verify_phase9_server1_680k_ewf.py')],'verifier_cwd':str(host_repo),'verifier_log':str(host_out/('resume-verifier-'+tag+'.log'))},'codex':{'enabled':False},'originating_task':('Human: resume Server1 680k; retain 1us and 3000 iterations; Courant limit0.8' if args.bounded_count is not None else 'Human: just keep running; Server 1; 680k only; ledger diagnostic without stop')}
 write_ascii_text_new(s,str(specpath),json.dumps(spec,indent=2)+'\n')
 details=resolve_connection_kwargs('1',start_transcript=False)
 script=run.WORK/('private-resume-'+tag+'.ps1');pid=run.WORK/('resume-pid-'+tag+'.json');launcher=run.WORK/('resume-launcher-'+tag+'.json')
 values={'FLUENT_IP':details['ip'],'FLUENT_PORT':details['port'],'FLUENT_PASSWORD':details['password'],'FLUENT_ALLOW_REMOTE_HOST':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE':str(details['insecure_mode']).lower()}
 text="$ErrorActionPreference='Stop'\n"
 for key,value in values.items():text+='$env:'+key+' = '+quote(value)+'\n'
 worker=host_repo/'PyAnsys/scripts/orchestration/run_and_handoff.py'
 text+='$p=Start-Process -FilePath '+quote(python)+" -ArgumentList '-E','-u',"+quote(worker)+",'--job',"+quote(specpath)+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(run.WORK/('resume-stdout-'+tag+'.log'))+' -RedirectStandardError '+quote(run.WORK/('resume-stderr-'+tag+'.log'))+' -PassThru\n'
 text+='[IO.File]::WriteAllText('+quote(pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 write_ascii_text_new(s,str(script),text)
 run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(script)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
 command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
 code="$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(run.WORK)+"}; [IO.File]::WriteAllText("+quote(launcher)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);launch=json.loads(run.read_text(s,str(launcher)));assert launch['ReturnValue']==0
 receipt={'status':'RESUME_DISPATCHED','host_repo':str(host_repo),'host_output':str(host_out),'host_python':python,'changes':changes,'job_spec':str(specpath),'job_manifest':str(jobmanifest),'run_manifest':str(host_out/'run-manifest.json'),'runner_log':str(runnerlog),'launcher':launch,'laptop_required':False,'ledger_diagnostic_only':True,'fixed_step_s':args.recovery_step,'bounded_count':args.bounded_count}
 run.dump(OUT/'resume-host-launch.json',receipt);print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
