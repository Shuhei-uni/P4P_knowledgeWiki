"""Deploy the reviewed 680k-only controller to Server 1; no Fluent restart."""
from pathlib import Path
import base64,hashlib,io,json,sys,time,uuid,zipfile
from phase9_server1_680k_common import run,attach,OUT,ROOT
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.stage4_native import write_remote_text_new
from pyansys_fluent.remote_text import write_ascii_text_new


def quote(v):return "'"+str(v).replace("'","''")+"'"

def main():
 s=attach();run.require_idle(s)
 prepared=json.loads((OUT/'680k-ewf-settings-current.json').read_text())
 assert prepared['status']=='SETTINGS_APPLIED_REOPEN_VERIFIED' and run.native_iteration(s)==9080
 tag=str(time.time_ns());scratch=run.WORK/'680k'/'scratch'
 runtime=scratch/('runtime-'+tag+'.json')
 # Probe one host interpreter and its actual modules before installing/launching.
 code="$ErrorActionPreference='Stop'; $p='"+str(run.WORK/'controller-venv/Scripts/python.exe')+"'; if (!(Test-Path $p)) {throw 'Prepared Server 1 controller interpreter missing'}; $ErrorActionPreference='Continue'; $r=(& $p -E -c 'import sys,json,ansys.fluent.core,numpy,dotenv,yaml; print(json.dumps(dict(executable=sys.executable,version=sys.version)))' 2>&1 | Out-String); [IO.File]::WriteAllText("+quote(runtime)+",(@{executable=$p;return_code=$LASTEXITCODE;output=$r}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 if run.base.powershell(s,code) not in (0,None):raise RuntimeError('Host runtime probe failed')
 preflight=json.loads(run.read_text(s,str(runtime)));run.dump(OUT/'host-runtime.json',preflight)
 if preflight['return_code']!=0:raise RuntimeError('Selected host Python lacks required modules: '+preflight['output'])
 python=preflight['executable'];host_repo=run.WORK/'controller-repo';host_out=host_repo/'PyAnsys/output/phase9-ewf-server1-680k/20261009'
 if run.remote_file_exists(s,str(host_out/'job-manifest.json')):raise RuntimeError('Existing host job must be reconciled')
 blob=io.BytesIO();count=0
 def convert(v):
  if isinstance(v,dict):return {k:convert(x) for k,x in v.items()}
  if isinstance(v,list):return [convert(x) for x in v]
  if isinstance(v,str) and str(ROOT.parent) in v:return v.replace(str(ROOT.parent),str(host_repo)).replace('/','\\')
  return v
 with zipfile.ZipFile(blob,'w',zipfile.ZIP_DEFLATED) as z:
  files=[]
  for folder in ['src','scripts/setup','scripts/inspection','scripts/orchestration']:
   files.extend((ROOT/folder).rglob('*.py'))
  files.extend([OUT/'680k-ewf-settings-current.json',OUT/'08b-approved-bulk-contract.json'])
  for p in sorted(set(files)):
   data=p.read_bytes()
   if p.suffix=='.json':data=(json.dumps(convert(json.loads(data)),indent=2)+'\n').encode()
   z.writestr(p.relative_to(ROOT.parent).as_posix(),data);count+=1
  spec={'job':{'id':'phase9-server1-680k-ewf-20261009','mode':'utility','manifest':str(host_out/'job-manifest.json'),'worker_log':str(host_out/'worker.log')},
   'runner':{'command':[python,'-E','-u',str(host_repo/'PyAnsys/scripts/setup/run_phase9_server1_680k_ewf.py')],'cwd':str(host_repo),'log':str(host_out/'runner.log')},
   'completion':{'required_files':[str(host_out/'run-manifest.json'),str(host_out/'final-reopen.json')],
    'verifier_command':[python,'-E',str(host_repo/'PyAnsys/scripts/inspection/verify_phase9_server1_680k_ewf.py')],'verifier_cwd':str(host_repo),'verifier_log':str(host_out/'verifier.log')},
   'codex':{'enabled':False},'originating_task':'Shuhei: Server 1 owned; 680k only; EWF Plan v1; 200 ms total film age'}
  z.writestr('phase9-server1-680k-job.json',json.dumps(spec,indent=2)+'\n')
 payload=blob.getvalue();encoded=run.WORK/('controller-'+tag+'.b64');package=run.WORK/('controller-'+tag+'.zip')
 write_remote_text_new(s,str(encoded),base64.b64encode(payload).decode('ascii'))
 code="$ErrorActionPreference='Stop'; [IO.File]::WriteAllBytes("+quote(package)+",[Convert]::FromBase64String([IO.File]::ReadAllText("+quote(encoded)+"))); Expand-Archive -LiteralPath "+quote(package)+' -DestinationPath '+quote(host_repo)+' -Force'
 if run.base.powershell(s,code) not in (0,None):raise RuntimeError('Host extraction failed')
 digest=run.remote_file_sha256(s,str(package),str(scratch/('bundle-'+tag+'.sha256.txt')))
 assert digest==hashlib.sha256(payload).hexdigest()
 # Test the exact deployed runner import; no attachment or solve on this path.
 probe=scratch/('deployed-import-'+tag+'.json')
 cmd="import sys; sys.path[:0]=[r'"+str(host_repo/'PyAnsys/scripts/setup')+"']; import run_phase9_server1_680k_ewf; print('DEPLOYED_RUNNER_IMPORT_PASS')"
 code="$ErrorActionPreference='Continue'; $r=(& "+quote(python)+" -E -c "+quote(cmd)+" 2>&1 | Out-String); [IO.File]::WriteAllText("+quote(probe)+",(@{return_code=$LASTEXITCODE;output=$r}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);check=json.loads(run.read_text(s,str(probe)))
 if check['return_code']!=0:raise RuntimeError('Deployed runner import failed: '+check['output'])
 receipt={'status':'DEPLOYED_PREFLIGHT_PASS','host_repo':str(host_repo),'host_output':str(host_out),'host_python':python,'bundle_files':count,'bundle_sha256':digest,'runtime':preflight,'deployed_import':check,'credentials_in_bundle':False,'laptop_required':False,'retrieval_route':'Fluent Scheme read_text while endpoint reachable; host files persist independently; no independent retrieval route verified'}
 run.dump(OUT/'host-deployment.json',receipt)
 # Credentials exist only in a temporary private launcher, then its environment.
 details=resolve_connection_kwargs('1',start_transcript=False)
 if 'server_info_file_name' in details:raise RuntimeError('Explicit endpoint required for host launch')
 script=run.WORK/('private-launch-'+tag+'.ps1');pid=run.WORK/('host-pid-'+tag+'.json');launcher=run.WORK/('launcher-'+tag+'.json')
 values={'FLUENT_IP':details['ip'],'FLUENT_PORT':details['port'],'FLUENT_PASSWORD':details['password'],'FLUENT_ALLOW_REMOTE_HOST':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE':str(details['insecure_mode']).lower()}
 text="$ErrorActionPreference='Stop'\n"
 for key,value in values.items():text+='$env:'+key+' = '+quote(value)+'\n'
 worker=host_repo/'PyAnsys/scripts/orchestration/run_and_handoff.py'
 text+='$p=Start-Process -FilePath '+quote(python)+" -ArgumentList '-E','-u',"+quote(worker)+",'--job',"+quote(host_repo/'phase9-server1-680k-job.json')+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(run.WORK/'host-worker.stdout.log')+' -RedirectStandardError '+quote(run.WORK/'host-worker.stderr.log')+' -PassThru\n'
 text+='[IO.File]::WriteAllText('+quote(pid)+",(@{worker_pid=$p.Id;execution_host='SERVER1_WINDOWS'}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 write_ascii_text_new(s,str(script),text)
 run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(script)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
 command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
 code="$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(run.WORK)+"}; [IO.File]::WriteAllText("+quote(launcher)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);launch=json.loads(run.read_text(s,str(launcher)))
 assert launch['ReturnValue']==0
 receipt.update(status='HOST_CONTROLLER_LAUNCH_DISPATCHED',launcher=launch,worker_pid_receipt=str(pid),job_spec=str(host_repo/'phase9-server1-680k-job.json'),run_manifest=str(host_out/'run-manifest.json'),runner_log=str(host_out/'runner.log'))
 run.dump(OUT/'host-launch.json',receipt);print(json.dumps({k:receipt[k] for k in ['status','host_output','host_python','laptop_required']}),flush=True)

if __name__=='__main__':main()
