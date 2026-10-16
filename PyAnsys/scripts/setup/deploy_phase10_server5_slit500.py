"""Stage/hash/import-check then dispatch the reviewed Server5-only slit campaign."""
from pathlib import Path,PureWindowsPath
import json,time,hashlib,os,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from phase9_server5_common import attach,run
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new
from pyansys_fluent.stage4_native import remote_file_sha256,ensure_remote_directory
OUT=ROOT/'output/phase10-proposed-design/20261015/server5-planv1-to500ms'
def q(value):return "'"+str(value).replace("'","''")+"'"
def dump(name,data):(OUT/name).write_text(json.dumps(data,indent=2)+'\n')
def main():
    assert not (OUT/'host-launch.json').exists(),'Existing deployment must be reconciled'
    install=json.loads((OUT/'runtime-install-launch.json').read_text());bundle=json.loads((OUT/'code-bundle.json').read_text());prepared=json.loads((OUT/'prepared-first.json').read_text())
    assert prepared['status']=='PREPARED_REOPEN_VERIFIED' and 'shared_pre_run_pair' in prepared
    s=attach();assert not s.settings.solution.run_calculation.iterating()
    assert run.native_iteration(s)==prepared['native_iteration'] and abs(run.film(s)['film_elapsed_time']-prepared['film_s'])<1e-10
    root=PureWindowsPath(install['host_work']);repo=root/('controller-repo-'+bundle['sha256'][:12]);hostout=repo/'PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms';tag=str(time.time_ns())
    assert not run.remote_file_exists(s,str(repo)),'Existing staged code requires reconciliation'
    shared=run.SHARED/PureWindowsPath(bundle['shared_relative'])
    assert remote_file_sha256(s,str(shared),str(root/('bundle-hash-'+tag+'.txt')))==bundle['sha256']
    run.base.powershell(s,"$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath "+q(shared)+' -DestinationPath '+q(repo))
    assert not run.remote_file_exists(s,str(hostout/'job-manifest.json'))
    # Mirror exact native preparation receipts, not another solve.
    for name in ['prepared-first.json','run-manifest.json']:
        write_ascii_text_new(s,str(hostout/name),(OUT/name).read_text())
    ensure_remote_directory(s,str(hostout/'vertical-slit154k'))
    write_ascii_text_new(s,str(hostout/'vertical-slit154k/prepared.json'),(OUT/'vertical-slit154k/prepared.json').read_text())
    target=repo/'PyAnsys/scripts/setup/run_phase10_server5_slits_planv1_500ms.py'
    digest=remote_file_sha256(s,str(target),str(root/('runner-hash-'+tag+'.txt')))
    assert digest==bundle['source_runner_sha256']
    # Import-only check on the exact Windows interpreter and isolated dependencies.
    probe=root/('campaign-import-'+tag+'.py');response=root/('campaign-import-'+tag+'.json')
    code='import sys,json\nsys.path[:0]=['+repr(str(install['dependencies']))+','+repr(str(repo/'PyAnsys/scripts/setup'))+']\nfrom pyansys_fluent.run_handoff import run_job\nimport run_phase10_server5_slits_planv1_500ms as a\nassert a.config()["server_id"]=="5"\nprint("SERVER5_CAMPAIGN_IMPORT_PASS")\n'
    write_ascii_text_new(s,str(probe),code)
    run.base.powershell(s,"$ErrorActionPreference='Continue'; $r=(& "+q(install['host_python'])+' -E -u '+q(probe)+" 2>&1|Out-String); [IO.File]::WriteAllText("+q(response)+",(@{return_code=$LASTEXITCODE;output=$r}|ConvertTo-Json),[Text.Encoding]::ASCII)")
    check=json.loads(run.read_text(s,str(response)));dump('host-import-probe.json',check)
    assert check['return_code']==0 and 'SERVER5_CAMPAIGN_IMPORT_PASS' in check['output']
    # Exclude installers/import probes; no other live Server5 CFD writer may own the session.
    owner=root/('owner-'+tag+'.json')
    run.base.powershell(s,"$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -eq 'python.exe' -and ($_.CommandLine -like '*run_phase10_server5_slits_planv1_500ms.py*' -or $_.CommandLine -like '*run_phase9_server5_342k_ewf.py*')}); [IO.File]::WriteAllText("+q(owner)+",(@{controller_count=$p.Count;controller_ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)")
    processes=json.loads(run.read_text(s,str(owner)));assert processes['controller_count']==0
    job={'job':{'id':'phase10-server5-slits500-'+tag,'mode':'utility','manifest':str(hostout/'job-manifest.json'),'worker_log':str(hostout/'worker.log')},'runner':{'command':[install['host_python'],'-E','-u',str(target)],'cwd':str(repo),'log':str(hostout/'runner.log')},'completion':{'required_files':[str(hostout/'run-manifest.json'),str(hostout/'vertical-slit154k/run-manifest.json'),str(hostout/'angled-slit213k/run-manifest.json')]},'codex':{'enabled':False}}
    spec=root/('job-'+tag+'.json');write_ascii_text_new(s,str(spec),json.dumps(job,indent=2)+'\n')
    bootstrap=root/('handoff-bootstrap-'+tag+'.py')
    bootstrap_code='import sys,runpy\nsys.path.insert(0,'+repr(install['dependencies'])+')\nsys.argv=['+repr(str(repo/'PyAnsys/scripts/orchestration/run_and_handoff.py'))+',\"--job\",'+repr(str(spec))+',\"--worker\"]\nrunpy.run_path(sys.argv[0],run_name=\"__main__\")\n'
    write_ascii_text_new(s,str(bootstrap),bootstrap_code)
    k=resolve_connection_kwargs('5',start_transcript=False);script=root/('private-launch-'+tag+'.ps1');pid=root/('launch-pid-'+tag+'.json')
    env={'FLUENT_SERVER_INFO_FILE5':'','FLUENT_IP5':k['ip'],'FLUENT_PORT5':k['port'],'FLUENT_PASSWORD5':k['password'],'FLUENT_ALLOW_REMOTE_HOST5':str(k['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE5':str(k['insecure_mode']).lower(),'P4P_SERVER5_DEPS':install['dependencies']}
    body="$ErrorActionPreference='Stop'\n"
    for name,value in env.items():body+='$env:'+name+' = '+q(value)+'\n'
    body+='$p=Start-Process -FilePath '+q(install['host_python'])+" -ArgumentList '-E','-u',"+q(bootstrap)+" -WindowStyle Hidden -RedirectStandardOutput "+q(root/'launcher.stdout.log')+' -RedirectStandardError '+q(root/'launcher.stderr.log')+' -PassThru\n'
    body+='[IO.File]::WriteAllText('+q(pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
    write_ascii_text_new(s,str(script),body)
    run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+q(script)+" /inheritance:r /grant:r ($me+':(F)') 'SYSTEM:(F)'|Out-Null")
    resultpath=root/('dispatch-'+tag+'.json');command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
    run.base.powershell(s,"$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+q(command)+';CurrentDirectory='+q(root)+"}; [IO.File]::WriteAllText("+q(resultpath)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)")
    result=json.loads(run.read_text(s,str(resultpath)));assert result['ReturnValue']==0
    dump('host-launch.json',{'status':'DISPATCHED','server_id':'5','host_repo':str(repo),'host_output':str(hostout),'run_manifest':str(hostout/'run-manifest.json'),'job_manifest':str(hostout/'job-manifest.json'),'runner_log':str(hostout/'runner.log'),'code_sha256':digest,'bundle_sha256':bundle['sha256'],'import_probe':check,'process_preflight':processes,'launcher':result,'target_film_s':.5,'laptop_required_for_solver':False,'execution_order':['vertical-slit154k','angled-slit213k'],'retrieval':'boundedFluentRPC and passive transcript; host files persist independently'})
    print('SERVER5_TWO_SLIT_500MS_CAMPAIGN_DISPATCHED',flush=True)
if __name__=='__main__':main()
