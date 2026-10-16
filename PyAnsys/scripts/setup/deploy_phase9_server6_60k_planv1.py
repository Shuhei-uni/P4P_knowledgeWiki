"""Deploy the fixed60k continuation to the existing Server6 host runtime."""
import hashlib,json,time
from pathlib import PureWindowsPath
import phase9_server6_60k_planv1_common as a
a.connect=lambda:(a.attach(),None)
def idle(s):
 a.run.require_idle(s)
 assert not s.settings.solution.run_calculation.iterating()
a.idle=idle
a.dump=lambda n,v:a.run.dump(a.OUT/n,v)
from deploy_phase9_server6_slit_ewf import quote
from pyansys_fluent.connection import resolve_connection_kwargs
def main():
    p=json.loads((a.OUT/'60k-ewf-settings-current.json').read_text());assert p['status']=='SETTINGS_APPLIED_REOPEN_VERIFIED'
    s,_=a.connect();a.idle(s)
    assert a.run.native_iteration(s)==8082
    old=json.loads((a.ROOT/'output/phase9-server6-slit154k/20261010/host-launch.json').read_text())
    repo=PureWindowsPath(old['host_repo']);out=repo/'PyAnsys/output/phase9-server6-60k-planv1/20261014'
    a.run.ensure_remote_directory(s,str(out))
    source=a.ROOT/'scripts/setup/run_phase9_server6_60k_planv1.py';target=repo/'PyAnsys/scripts/setup'/source.name
    a.run.write_ascii_text_new(s,str(target),source.read_text());assert a.run.read_text(s,str(target))==source.read_text()
    a.run.write_ascii_text_new(s,str(out/'60k-ewf-settings-current.json'),(a.OUT/'60k-ewf-settings-current.json').read_text())
    for local,target_rel in [(a.ROOT/'scripts/setup/phase9_server6_60k_planv1_common.py','PyAnsys/scripts/setup/phase9_server6_60k_planv1_common.py')]:
        a.run.write_ascii_text_new(s,str(repo/target_rel),local.read_text())
    for name in ['matched-drain-probe.json']:
        a.run.write_ascii_text_new(s,str(out/name),(a.OUT/name).read_text())
    probe=a.run.WORK/('planv1-runtime-import-'+str(time.time_ns())+'.json')
    command="import sys; sys.path[:0]=["+repr(str(repo/'PyAnsys/scripts/setup'))+"]; import run_phase9_server6_60k_planv1; print('PLANV1_RUNNER_IMPORT_PASS')"
    a.run.base.powershell(s,"$ErrorActionPreference='Continue'; $t=(& "+quote(old['host_python'])+" -E -c "+quote(command)+" 2>&1 | Out-String); [IO.File]::WriteAllText("+quote(probe)+",(@{return_code=$LASTEXITCODE;output=$t}|ConvertTo-Json),[Text.Encoding]::ASCII)")
    check=json.loads(a.run.read_text(s,str(probe)));assert check['return_code']==0 and 'PLANV1_RUNNER_IMPORT_PASS' in check['output']
    a.dump('host-import-check.json',check)
    tag=str(time.time_ns());specpath=a.run.WORK/('job-'+tag+'.json')
    spec={'job':{'id':'phase9-server6-60k-planv1-'+tag,'mode':'utility','manifest':str(out/'job-manifest.json'),'worker_log':str(out/'worker.log')},'runner':{'command':[old['host_python'],'-E','-u',str(target)],'cwd':str(repo),'log':str(out/'runner.log')},'completion':{'required_files':[str(out/'run-manifest.json')]},'codex':{'enabled':False}}
    spec['completion']['required_files'] += [str(out/'final-reopen.json')]
    a.run.write_ascii_text_new(s,str(specpath),json.dumps(spec,indent=2)+'\n')
    kw=resolve_connection_kwargs('6',start_transcript=False)
    env={'FLUENT_SERVER_INFO_FILE6':'','FLUENT_IP6':kw['ip'],'FLUENT_PORT6':kw['port'],'FLUENT_PASSWORD6':kw['password'],'FLUENT_ALLOW_REMOTE_HOST6':str(kw['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE6':str(kw['insecure_mode']).lower()}
    private=a.run.WORK/('private-launch-'+tag+'.ps1');pid=a.run.WORK/('worker-pid-'+tag+'.json')
    body="$ErrorActionPreference='Stop'\n"
    for k,v in env.items():body+='$env:'+k+' = '+quote(v)+'\n'
    body+='$p=Start-Process -FilePath '+quote(old['host_python'])+" -ArgumentList '-E','-u',"+quote(repo/'PyAnsys/scripts/orchestration/run_and_handoff.py')+",'--job',"+quote(specpath)+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(out/'launcher.stdout.log')+' -RedirectStandardError '+quote(out/'launcher.stderr.log')+' -PassThru\n'
    body+='[IO.File]::WriteAllText('+quote(pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
    a.run.write_ascii_text_new(s,str(private),body)
    a.run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(private)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
    response=a.run.WORK/('launch-response-'+tag+'.json');cmd='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(private)+'"'
    a.run.base.powershell(s,"$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(cmd)+';CurrentDirectory='+quote(a.run.WORK)+"}; [IO.File]::WriteAllText("+quote(response)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)")
    result=json.loads(a.run.read_text(s,str(response)));assert result['ReturnValue']==0
    a.dump('host-launch.json',{'status':'DISPATCHED','host_output':str(out),'run_manifest':str(out/'run-manifest.json'),'job_manifest':str(out/'job-manifest.json'),'runner_log':str(out/'runner.log'),'code_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'launcher':result,'laptop_required':False,'retrieval':'Fluent RPC while reachable; host files persist independently'})
    print('60K_HOST_RUN_DISPATCHED',flush=True)
if __name__=='__main__':main()
