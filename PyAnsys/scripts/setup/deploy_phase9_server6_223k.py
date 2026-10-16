"""Deploy the reviewed, prepared 223k startup to its own Server6 host worker."""
from pathlib import PureWindowsPath
import base64,hashlib,io,json,time,zipfile
from prepare_phase9_server6_223k import connect,run,ROOT,OUT
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.stage4_native import write_remote_text_new
from deploy_phase9_server6_slit_ewf import quote

def main():
 if (OUT/'host-launch.json').exists():raise RuntimeError('Reconcile existing launch before dispatch')
 assert json.loads((OUT/'settings-match.json').read_text())['status']=='PASS'
 smoke=json.loads((OUT/'223k-run.json').read_text());assert smoke['instrumentation_smoke']=='PASS' and smoke['verified_native_end']==1600
 s=connect();assert run.native_iteration(s)==1600
 old=json.loads((ROOT/'output/phase9-server6-slit154k/20261010/host-launch.json').read_text());python=old['host_python']
 tag=str(time.time_ns());repo=run.WORK/'controller-repo';host_out=repo/'PyAnsys/output/phase9-server6-223k/20261015';scratch=run.WORK/'223k/scratch'
 probe=scratch/('runtime-'+tag+'.json')
 code="$ErrorActionPreference='Continue'; $r=(& "+quote(python)+" -E -c 'import sys,json,ansys.fluent.core,h5py,numpy,dotenv,yaml; print(json.dumps(dict(executable=sys.executable,version=sys.version,pyfluent=ansys.fluent.core.__version__)))' 2>&1|Out-String); $controllers=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -match 'prepare_phase9_server6_223k.*run|run_phase9_server6_.*ewf|run_phase9_server6_60k'} | Select-Object ProcessId,Name); [IO.File]::WriteAllText("+quote(probe)+",(@{return_code=$LASTEXITCODE;output=$r;controllers=$controllers;free_bytes=(Get-PSDrive C).Free}|ConvertTo-Json -Depth 4),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);runtime=json.loads(run.read_text(s,str(probe)));run.dump(OUT/'host-runtime.json',runtime)
 assert runtime['return_code']==0 and not runtime['controllers'] and runtime['free_bytes']>10*1024**3
 def convert(v):
  if isinstance(v,dict):return {k:convert(x) for k,x in v.items()}
  if isinstance(v,list):return [convert(x) for x in v]
  if isinstance(v,str) and str(ROOT.parent) in v:return v.replace(str(ROOT.parent),str(repo)).replace('/','\\')
  return v
 spec={'job':{'id':'phase9-server6-223k-startup-'+tag,'mode':'utility','manifest':str(host_out/'job-manifest.json'),'worker_log':str(host_out/'worker.log')},'runner':{'command':[python,'-E','-u',str(repo/'PyAnsys/scripts/setup/prepare_phase9_server6_223k.py'),'run'],'cwd':str(repo),'log':str(host_out/'runner.log')},'completion':{'required_files':[str(host_out/'startup-complete.json'),str(host_out/'223k-run.json')]},'codex':{'enabled':False}}
 blob=io.BytesIO();count=0
 with zipfile.ZipFile(blob,'w',zipfile.ZIP_DEFLATED) as z:
  files=[]
  for folder in ['src','scripts/setup','scripts/inspection','scripts/orchestration']:files.extend((ROOT/folder).rglob('*.py'))
  files.append(ROOT/'output/phase9-mesh-convergence/20261007/08b-approved-bulk-contract.json')
  for n in ['223k-prepared-audited.json','223k-run.json','08b-approved-bulk-contract.json','08b-settings-audit-approved.json','settings-match.json']:files.append(OUT/n)
  for p in sorted(set(files)):
   data=p.read_bytes()
   if p.suffix=='.json':data=(json.dumps(convert(json.loads(data)),indent=2)+'\n').encode()
   z.writestr(p.relative_to(ROOT.parent).as_posix(),data);count+=1
  z.writestr('phase9-server6-223k-job.json',json.dumps(spec,indent=2)+'\n')
 payload=blob.getvalue();encoded=run.WORK/('startup-bundle-'+tag+'.b64');package=run.WORK/('startup-bundle-'+tag+'.zip')
 write_remote_text_new(s,str(encoded),base64.b64encode(payload).decode())
 run.base.powershell(s,"$ErrorActionPreference='Stop'; [IO.File]::WriteAllBytes("+quote(package)+",[Convert]::FromBase64String([IO.File]::ReadAllText("+quote(encoded)+"))); Expand-Archive -LiteralPath "+quote(package)+' -DestinationPath '+quote(repo)+' -Force')
 digest=run.remote_file_sha256(s,str(package),str(scratch/('bundle-'+tag+'.sha256')));assert digest==hashlib.sha256(payload).hexdigest()
 checkpath=scratch/('import-'+tag+'.json');cmd="import sys;sys.path.insert(0,"+repr(str(repo/'PyAnsys/scripts/setup'))+");import prepare_phase9_server6_223k;print('IMPORT_PASS')"
 run.base.powershell(s,"$ErrorActionPreference='Continue'; $r=(& "+quote(python)+" -E -c "+quote(cmd)+" 2>&1|Out-String); [IO.File]::WriteAllText("+quote(checkpath)+",(@{return_code=$LASTEXITCODE;output=$r}|ConvertTo-Json),[Text.Encoding]::ASCII)")
 check=json.loads(run.read_text(s,str(checkpath)));assert check['return_code']==0 and 'IMPORT_PASS' in check['output'];run.dump(OUT/'host-import-check.json',check)
 # Endpoint credentials are confined to the temporary private launch file.
 k=resolve_connection_kwargs('6',start_transcript=False);assert 'ip' in k
 env={'FLUENT_SERVER_INFO_FILE6':'','FLUENT_IP6':k['ip'],'FLUENT_PORT6':k['port'],'FLUENT_PASSWORD6':k['password'],'FLUENT_ALLOW_REMOTE_HOST6':str(k['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE6':str(k['insecure_mode']).lower()}
 private=run.WORK/('private-startup-'+tag+'.ps1');pid=run.WORK/('startup-pid-'+tag+'.json');response=run.WORK/('startup-launch-'+tag+'.json')
 text="$ErrorActionPreference='Stop'\n"+''.join('$env:'+name+' = '+quote(value)+'\n' for name,value in env.items())
 text+='$p=Start-Process -FilePath '+quote(python)+" -ArgumentList '-E','-u',"+quote(repo/'PyAnsys/scripts/orchestration/run_and_handoff.py')+",'--job',"+quote(repo/'phase9-server6-223k-job.json')+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(run.WORK/'startup.stdout.log')+' -RedirectStandardError '+quote(run.WORK/'startup.stderr.log')+' -PassThru\n'
 text+='[IO.File]::WriteAllText('+quote(pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 run.write_ascii_text_new(s,str(private),text)
 run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(private)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
 command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(private)+'"'
 run.base.powershell(s,"$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(run.WORK)+"}; [IO.File]::WriteAllText("+quote(response)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)")
 launch=json.loads(run.read_text(s,str(response)));assert launch['ReturnValue']==0
 run.dump(OUT/'host-launch.json',{'status':'DISPATCHED','host_repo':str(repo),'host_output':str(host_out),'host_python':python,'runner_log':str(host_out/'runner.log'),'job_manifest':str(host_out/'job-manifest.json'),'run_manifest':str(host_out/'223k-run.json'),'bundle_sha256':digest,'bundle_files':count,'launcher':launch,'laptop_required':False,'retrieval':'Fluent RPC while reachable; native host files persist independently','credentials_in_bundle':False})
 print('223K_STARTUP_DISPATCHED',flush=True)
if __name__=='__main__':main()
