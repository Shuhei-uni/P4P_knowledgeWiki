"""Repair proven pre-solve launcher import failure; never replay an accepted solve."""
from pathlib import Path,PureWindowsPath
import json,time,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from deploy_phase10_server5_slit500 import OUT,q,dump
from phase9_server5_common import attach,run
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
    proof=json.loads((OUT/'launch-failure-reconciliation.json').read_text());assert not proof['job_manifest_exists'] and proof['processes']['count']==0 and not proof['iterating']
    assert proof['native_iteration']==44661 and 'ModuleNotFoundError' in proof['launcher.stderr.log']
    launch=json.loads((OUT/'host-launch.json').read_text());install=json.loads((OUT/'runtime-install-launch.json').read_text());repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output']);root=PureWindowsPath(install['host_work']);s=attach()
    assert not s.settings.solution.run_calculation.iterating() and run.native_iteration(s)==44661
    assert abs(run.film(s)['film_elapsed_time']-.15)<1e-10 and not run.remote_file_exists(s,launch['job_manifest'])
    tag=str(time.time_ns());probe=root/('handoff-import-fixed-'+tag+'.py');response=root/('handoff-import-fixed-'+tag+'.json')
    text='import sys\nsys.path[:0]=['+repr(install['dependencies'])+','+repr(str(repo/'PyAnsys/src'))+','+repr(str(repo/'PyAnsys/scripts/setup'))+']\nfrom pyansys_fluent.run_handoff import run_job\nimport run_phase10_server5_slits_planv1_500ms\nprint("FULL_HANDOFF_AND_RUNNER_IMPORT_PASS")\n'
    write_ascii_text_new(s,str(probe),text)
    run.base.powershell(s,"$ErrorActionPreference='Continue'; $v=(& "+q(install['host_python'])+' -E -u '+q(probe)+" 2>&1|Out-String);[IO.File]::WriteAllText("+q(response)+",(@{return_code=$LASTEXITCODE;output=$v}|ConvertTo-Json),[Text.Encoding]::ASCII)")
    check=json.loads(run.read_text(s,str(response)));dump('handoff-import-fixed.json',check);assert check['return_code']==0 and 'FULL_HANDOFF_AND_RUNNER_IMPORT_PASS' in check['output']
    spec={'job':{'id':'phase10-server5-slit500-fixed-'+tag,'mode':'utility','manifest':str(hostout/'job-manifest.json'),'worker_log':str(hostout/'worker.log')},'runner':{'command':[install['host_python'],'-E','-u',str(repo/'PyAnsys/scripts/setup/run_phase10_server5_slits_planv1_500ms.py')],'cwd':str(repo),'log':str(hostout/'runner.log')},'completion':{'required_files':[str(hostout/'run-manifest.json'),str(hostout/'vertical-slit154k/run-manifest.json'),str(hostout/'angled-slit213k/run-manifest.json')]},'codex':{'enabled':False}}
    specpath=root/('job-fixed-'+tag+'.json');write_ascii_text_new(s,str(specpath),json.dumps(spec,indent=2)+'\n')
    bootstrap=root/('handoff-bootstrap-'+tag+'.py');body='import sys,runpy\nsys.path.insert(0,'+repr(install['dependencies'])+')\nsys.argv=['+repr(str(repo/'PyAnsys/scripts/orchestration/run_and_handoff.py'))+',"--job",'+repr(str(specpath))+',"--worker"]\nrunpy.run_path(sys.argv[0],run_name="__main__")\n';write_ascii_text_new(s,str(bootstrap),body)
    k=resolve_connection_kwargs('5',start_transcript=False);pspath=root/('private-launch-fixed-'+tag+'.ps1')
    env={'FLUENT_SERVER_INFO_FILE5':'','FLUENT_IP5':k['ip'],'FLUENT_PORT5':k['port'],'FLUENT_PASSWORD5':k['password'],'FLUENT_ALLOW_REMOTE_HOST5':str(k['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE5':str(k['insecure_mode']).lower(),'P4P_SERVER5_DEPS':install['dependencies']}
    code="$ErrorActionPreference='Stop'\n"
    for name,value in env.items():code+='$env:'+name+' = '+q(value)+'\n'
    code+='Start-Process -FilePath '+q(install['host_python'])+" -ArgumentList '-E','-u',"+q(bootstrap)+' -WindowStyle Hidden -RedirectStandardOutput '+q(root/'launcher-fixed.stdout.log')+' -RedirectStandardError '+q(root/'launcher-fixed.stderr.log')+'\nRemove-Item -LiteralPath $PSCommandPath -Force\n';write_ascii_text_new(s,str(pspath),code)
    run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+q(pspath)+" /inheritance:r /grant:r ($me+':(F)') 'SYSTEM:(F)'|Out-Null")
    response=root/('dispatch-fixed-'+tag+'.json');command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(pspath)+'"'
    run.base.powershell(s,"$ErrorActionPreference='Stop';$r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+q(command)+';CurrentDirectory='+q(root)+"};[IO.File]::WriteAllText("+q(response)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)")
    result=json.loads(run.read_text(s,str(response)));assert result['ReturnValue']==0
    dump('initial-failed-host-launch.json',launch);launch.update(status='DISPATCHED_WITH_DEPENDENCY_BOOTSTRAP',import_probe=check,launcher=result,pre_solve_import_failure_repaired=True,no_native_solve_replayed=True);dump('host-launch.json',launch)
    print('SERVER5_FIXED_HANDOFF_DISPATCHED_NO_SOLVE_REPLAY',flush=True)
if __name__=='__main__':main()
