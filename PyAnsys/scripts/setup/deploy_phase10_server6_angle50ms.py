"""Deploy one reviewed angle50ms runner to the existing Server6 Python runtime."""
import hashlib,json,time
from pathlib import PureWindowsPath
import run_phase10_server6_angle50ms as a
from deploy_phase9_server6_slit_ewf import quote
from run_phase9_server6_slit_ewf import lane_file_sha256
from pyansys_fluent.connection import resolve_connection_kwargs

def main():
    prepared=json.loads((a.OUT/'prepared.json').read_text())
    assert prepared['status']=='PREPARED_REOPEN_VERIFIED'
    s,_=a.connect();a.idle(s)
    assert a.run.native_iteration(s)==30862
    assert abs(a.run.film(s)['film_elapsed_time']-.023705)<1e-10
    assert dict(s.rp_vars('wall-film/model-parameters'))['timestep-max']==1e-5
    old=json.loads((a.ROOT/'output/phase9-server6-slit154k/20261010/host-launch.json').read_text())
    repo=PureWindowsPath(old['host_repo']);hostout=repo/'PyAnsys/output/phase10-proposed-design/20261012/angle213k-to50ms'
    a.run.ensure_remote_directory(s,str(hostout))
    tag=str(time.time_ns());probe=a.run.WORK/('angle-owner-'+tag+'.json')
    command=("$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and (($_.CommandLine -like '*Phase9-Server6-slit154k*' -and ($_.CommandLine -like '*run_phase9_server6_slit_ewf*' -or $_.CommandLine -like '*wait_and_revise_phase9_server6_slit*')) -or $_.CommandLine -like '*run_phase10_server6_angle50ms.py*')}); [IO.File]::WriteAllText("+quote(probe)+",(@{controller_count=$p.Count;process_ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)")
    a.run.base.powershell(s,command);process=json.loads(a.run.read_text(s,str(probe)));assert process['controller_count']==0
    runner=a.ROOT/'scripts/setup/run_phase10_server6_angle50ms.py'
    target=repo/'PyAnsys/scripts/setup'/runner.name
    assert not a.run.remote_file_exists(s,str(hostout/'job-manifest.json'))
    text=runner.read_text()
    if a.run.remote_file_exists(s,str(target)):
        old_text=a.run.read_text(s,str(target))
        if old_text!=text:
            staged=a.run.WORK/('reviewed-angle-runner-'+tag+'.py')
            a.run.write_ascii_text_new(s,str(staged),text)
            a.run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(target)+' -Destination '+quote(str(target)+'.before-'+tag)+"; Copy-Item -LiteralPath "+quote(staged)+' -Destination '+quote(target)+' -Force')
    else:a.run.write_ascii_text_new(s,str(target),text)
    assert a.run.read_text(s,str(target))==text
    digest=lane_file_sha256(s,str(target),str(a.run.WORK/'scratch'/('angle-runner-'+tag+'.txt')))
    for name in ['prepared.json','run-manifest.json','code-review.json']:
        dest=hostout/name;source=(a.OUT/name).read_text()
        if a.run.remote_file_exists(s,str(dest)):
            if name=='code-review.json':
                staged=a.run.WORK/('angle-code-review-'+tag+'.json');a.run.write_ascii_text_new(s,str(staged),source)
                a.run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(dest)+' -Destination '+quote(str(dest)+'.before-'+tag)+"; Copy-Item -LiteralPath "+quote(staged)+' -Destination '+quote(dest)+' -Force')
            else:assert json.loads(a.run.read_text(s,str(dest)))==json.loads(source)
        else:a.run.write_ascii_text_new(s,str(dest),source)
    # Existing v252 host runtime, imports only: no Fluent command is sent by this probe.
    import_probe=a.run.WORK/('angle-import-'+tag+'.json')
    python_code='import sys\nsys.path.insert(0,'+repr(str(repo/'PyAnsys/scripts/setup'))+')\nimport run_phase10_server6_angle50ms\nprint("ANGLE_RUNNER_IMPORT_PASS")\n'
    python_probe=a.run.WORK/('angle-import-probe-'+tag+'.py');a.run.write_ascii_text_new(s,str(python_probe),python_code)
    ps="$ErrorActionPreference='Continue'; $t=(& "+quote(old['host_python'])+' -E -u '+quote(python_probe)+" 2>&1 | Out-String); $rc=$LASTEXITCODE; [IO.File]::WriteAllText("+quote(import_probe)+",(@{return_code=$rc;output=$t}|ConvertTo-Json),[Text.Encoding]::ASCII)"
    a.run.base.powershell(s,ps)
    for attempt in range(15):
        if a.run.remote_file_exists(s,str(import_probe)):break
        time.sleep(1)
    check=json.loads(a.run.read_text(s,str(import_probe)))
    assert check['return_code']==0 and 'ANGLE_RUNNER_IMPORT_PASS' in check['output']
    spec={'job':{'id':'phase10-server6-angle213k-50ms-'+tag,'mode':'utility',
                 'manifest':str(hostout/'job-manifest.json'),'worker_log':str(hostout/'worker.log')},
          'runner':{'command':[old['host_python'],'-E','-u',str(target)],'cwd':str(repo),'log':str(hostout/'runner.log')},
          'completion':{'required_files':[str(hostout/'run-manifest.json')]},'codex':{'enabled':False}}
    specpath=a.run.WORK/('angle-job-'+tag+'.json');a.run.write_ascii_text_new(s,str(specpath),json.dumps(spec,indent=2)+'\n')
    kw=resolve_connection_kwargs('6',start_transcript=False)
    script=a.run.WORK/('private-angle-launch-'+tag+'.ps1');pid=a.run.WORK/('angle-launch-pid-'+tag+'.json')
    env={'FLUENT_SERVER_INFO_FILE6':'','FLUENT_IP6':kw['ip'],'FLUENT_PORT6':kw['port'],
         'FLUENT_PASSWORD6':kw['password'],'FLUENT_ALLOW_REMOTE_HOST6':str(kw['allow_remote_host']).lower(),
         'FLUENT_INSECURE_MODE6':str(kw['insecure_mode']).lower()}
    body="$ErrorActionPreference='Stop'\n"
    for key,val in env.items():body+='$env:'+key+' = '+quote(val)+'\n'
    body+='$p=Start-Process -FilePath '+quote(old['host_python'])+" -ArgumentList '-E','-u',"+quote(repo/'PyAnsys/scripts/orchestration/run_and_handoff.py')+",'--job',"+quote(specpath)+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(hostout/'launcher.stdout.log')+' -RedirectStandardError '+quote(hostout/'launcher.stderr.log')+' -PassThru\n'
    body+='[IO.File]::WriteAllText('+quote(pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
    a.run.write_ascii_text_new(s,str(script),body)
    a.run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(script)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
    response=a.run.WORK/('angle-launch-response-'+tag+'.json')
    cmd='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
    a.run.base.powershell(s,"$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(cmd)+';CurrentDirectory='+quote(a.run.WORK)+"}; [IO.File]::WriteAllText("+quote(response)+",($r | Select-Object ProcessId,ReturnValue | ConvertTo-Json),[Text.Encoding]::ASCII)")
    result=json.loads(a.run.read_text(s,str(response)));assert result['ReturnValue']==0
    a.dump('host-launch.json',{'status':'DISPATCHED','server_id':'6','host_repo':str(repo),
           'host_output':str(hostout),'run_manifest':str(hostout/'run-manifest.json'),
           'job_manifest':str(hostout/'job-manifest.json'),'runner_log':str(hostout/'runner.log'),
           'code_sha256':digest,'import_probe':check,'process_preflight':process,'launcher':result,
           'target_film_s':.05,'main_step_s':1e-5,'numerical_thresholds':None,
           'laptop_required_for_solver':False,'retrieval':'Fluent RPC while endpoint responds; host files persist independently'})
    print('ANGLE_10US_HOST_RUN_DISPATCHED',flush=True)

if __name__=='__main__':main()
