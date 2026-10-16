"""Stage the reviewed FPE recovery and launch a new, uniquely named host job."""
from pathlib import Path,PureWindowsPath
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from deploy_phase10_server5_slit500 import OUT,q,dump
from phase9_server5_common import attach,run
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--bulk-scale',action='store_true');args=parser.parse_args()
    receipt='bulk-scale-recovery-launch.json' if args.bulk_scale else 'recovery-launch.json'
    driver='recover_phase10_server5_bulk_scale_slit500.py' if args.bulk_scale else 'recover_phase10_server5_slit500.py'
    launch=json.loads((OUT/'host-launch.json').read_text());install=json.loads((OUT/'runtime-install-launch.json').read_text())
    assert not (OUT/receipt).exists(),'Reconcile any previous recovery before another launch'
    repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output']);root=PureWindowsPath(install['host_work']);stamp=str(time.time_ns())
    s=attach();assert not s.settings.solution.run_calculation.iterating() and run.native_iteration(s)==(44857 if args.bulk_scale else 45047)
    old=json.loads(run.read_text(s,launch['job_manifest']));assert old['status']=='BLOCKED' and old['runner']['return_code']==1
    response=root/('recovery-owner-'+stamp+'.json')
    run.base.powershell(s,"$ErrorActionPreference='Stop';$p=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -eq 'python.exe' -and ($_.CommandLine -like '*run_phase10_server5_slits_planv1_500ms.py*' -or $_.CommandLine -like '*recover_phase10_server5*slit500.py*')});[IO.File]::WriteAllText("+q(response)+",(@{count=$p.Count;ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)")
    processes=json.loads(run.read_text(s,str(response)));assert processes['count']==0
    staged={}
    for name in ['run_phase10_server5_slits_planv1_500ms.py',driver]:
        local=ROOT/'scripts/setup'/name;target=repo/'PyAnsys/scripts/setup'/name
        if run.remote_file_exists(s,str(target)):
            run.base.powershell(s,"$ErrorActionPreference='Stop';Move-Item -LiteralPath "+q(target)+' -Destination '+q(str(target)+'.before-recovery-'+stamp))
        write_ascii_text_new(s,str(target),local.read_text())
        # Fluent's Windows text writer translates LF to CRLF. Normalise the
        # staged source before checking its byte hash against the reviewed LF file.
        run.base.powershell(s,"$ErrorActionPreference='Stop';$p="+q(target)+";$t=[IO.File]::ReadAllText($p).Replace(\"`r`n\",\"`n\");[IO.File]::WriteAllText($p,$t,[Text.Encoding]::ASCII)")
        digest=hashlib.sha256(local.read_bytes()).hexdigest()
        assert run.remote_file_sha256(s,str(target),str(root/('recovery-code-'+name+'-'+stamp+'.txt')))==digest
        staged[name]=digest
    probe=root/('recovery-import-'+stamp+'.py');response=root/('recovery-import-'+stamp+'.json')
    test='x=r.schedule(.1500011000000096)\nassert sum(a[1] for a in x)==142449' if args.bulk_scale else 'x=r.recovery_schedule(.1500010000000096)\nassert sum(a[1] for a in x)==142459'
    body='import sys\nsys.path[:0]=['+repr(install['dependencies'])+','+repr(str(repo/'PyAnsys/src'))+','+repr(str(repo/'PyAnsys/scripts/setup'))+']\nimport '+driver[:-3]+' as r\n'+test+'\nprint("RECOVERY_IMPORT_AND_CLOCK_PASS")\n'
    write_ascii_text_new(s,str(probe),body)
    run.base.powershell(s,"$ErrorActionPreference='Continue';$v=(& "+q(install['host_python'])+' -E -u '+q(probe)+" 2>&1|Out-String);[IO.File]::WriteAllText("+q(response)+",(@{return_code=$LASTEXITCODE;output=$v}|ConvertTo-Json),[Text.Encoding]::ASCII)")
    check=json.loads(run.read_text(s,str(response)));assert check['return_code']==0 and 'RECOVERY_IMPORT_AND_CLOCK_PASS' in check['output']
    # Separate job receipt preserves the failed job, log and PID evidence.
    jobpath=hostout/('recovery-job-'+stamp+'.json');log=hostout/('recovery-runner-'+stamp+'.log')
    spec={'job':{'id':'phase10-server5-fpe-recovery-'+stamp,'mode':'utility','manifest':str(jobpath),'worker_log':str(hostout/('recovery-worker-'+stamp+'.log'))},'runner':{'command':[install['host_python'],'-E','-u',str(repo/'PyAnsys/scripts/setup'/driver)],'cwd':str(repo),'log':str(log)},'completion':{'required_files':[str(hostout/'run-manifest.json'),str(hostout/'vertical-slit154k/run-manifest.json'),str(hostout/'angled-slit213k/run-manifest.json')]},'codex':{'enabled':False}}
    specpath=root/('recovery-spec-'+stamp+'.json');write_ascii_text_new(s,str(specpath),json.dumps(spec,indent=2)+'\n')
    bootstrap=root/('recovery-bootstrap-'+stamp+'.py');write_ascii_text_new(s,str(bootstrap),'import sys,runpy\nsys.path.insert(0,'+repr(install['dependencies'])+')\nsys.argv=['+repr(str(repo/'PyAnsys/scripts/orchestration/run_and_handoff.py'))+',"--job",'+repr(str(specpath))+',"--worker"]\nrunpy.run_path(sys.argv[0],run_name="__main__")\n')
    k=resolve_connection_kwargs('5',start_transcript=False);private=root/('private-recovery-'+stamp+'.ps1')
    env={'FLUENT_SERVER_INFO_FILE5':'','FLUENT_IP5':k['ip'],'FLUENT_PORT5':k['port'],'FLUENT_PASSWORD5':k['password'],'FLUENT_ALLOW_REMOTE_HOST5':str(k['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE5':str(k['insecure_mode']).lower(),'P4P_SERVER5_DEPS':install['dependencies']}
    code="$ErrorActionPreference='Stop'\n"
    for name,value in env.items():code+='$env:'+name+' = '+q(value)+'\n'
    code+='Start-Process -FilePath '+q(install['host_python'])+" -ArgumentList '-E','-u',"+q(bootstrap)+' -WindowStyle Hidden -RedirectStandardOutput '+q(root/('recovery-launch-'+stamp+'.stdout.log'))+' -RedirectStandardError '+q(root/('recovery-launch-'+stamp+'.stderr.log'))+'\nRemove-Item -LiteralPath $PSCommandPath -Force\n'
    write_ascii_text_new(s,str(private),code)
    run.base.powershell(s,"$ErrorActionPreference='Stop';$me=[Security.Principal.WindowsIdentity]::GetCurrent().Name;& icacls.exe "+q(private)+" /inheritance:r /grant:r ($me+':(F)') 'SYSTEM:(F)'|Out-Null")
    response=root/('recovery-dispatch-'+stamp+'.json');command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(private)+'"'
    run.base.powershell(s,"$ErrorActionPreference='Stop';$r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+q(command)+';CurrentDirectory='+q(root)+"};[IO.File]::WriteAllText("+q(response)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)")
    result=json.loads(run.read_text(s,str(response)));assert result['ReturnValue']==0
    dump('pre-'+receipt,launch);launch.update(status='RECOVERY_DISPATCHED',job_manifest=str(jobpath),runner_log=str(log),recovery_code=staged,recovery_import_probe=check,recovery_process_preflight=processes,launcher=result)
    dump('host-launch.json',launch);dump(receipt,launch);print('SERVER5_RECOVERY_DISPATCHED',flush=True)

if __name__=='__main__':main()
