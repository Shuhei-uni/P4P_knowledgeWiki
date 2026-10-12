"""Stage the reviewed 100 ms change; host waits for native completion."""
import json,time,hashlib
from pathlib import PureWindowsPath
from phase9_server6_slit_common import attach,run,OUT,ROOT
from deploy_phase9_server6_slit_ewf import quote
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
    s=attach();launch=json.loads((OUT/'host-launch.json').read_text())
    repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output'])
    hold=json.loads((OUT/'target100-controller-hold.json').read_text())
    assert hold['status']=='OWNED_CONTROLLER_HELD_NATIVE_COMMAND_RECONCILIATION_PENDING'
    job=json.loads(run.read_text(s,str(hostout/'job-manifest.json')))
    assert job['status']=='BLOCKED'
    # No settings/load/solve here. Only new scripts, receipts and a waiting host process.
    tag=str(time.time_ns());stage=repo/'PyAnsys/stagedhuman1us'
    run.ensure_remote_directory(s,str(stage))
    files={
        ROOT/'scripts/setup/run_phase9_server6_slit_ewf.py':stage/'run_phase9_server6_slit_ewf.py',
        ROOT/'scripts/inspection/verify_phase9_server6_slit_ewf.py':stage/'verify_phase9_server6_slit_ewf.py',
        ROOT/'scripts/setup/revise_phase9_server6_slit_1us.py':repo/'PyAnsys/scripts/setup/revise_phase9_server6_slit_1us.py',
        ROOT/'scripts/setup/wait_and_revise_phase9_server6_slit_1us.py':repo/'PyAnsys/scripts/setup/wait_and_revise_phase9_server6_slit_1us.py',
        OUT/'host-launch.json':hostout/'host-launch.json',
        OUT/'human-1us-controller-hold.json':hostout/'human-1us-controller-hold.json',
        OUT/'campaign-request.json':hostout/'campaign-request.json',
    }
    hashes={}
    for source,target in files.items():
        staging=run.WORK/('human1us-upload-'+tag+'-'+source.name)
        write_ascii_text_new(s,str(staging),source.read_text())
        if run.remote_file_exists(s,str(target)):
            run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(target)+' -Destination '+quote(str(target)+'.before-human1us-'+tag))
        run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(staging)+' -Destination '+quote(target)+' -Force')
        assert run.read_text(s,str(target))==source.read_text()
        hashes[str(target)]=hashlib.sha256(source.read_bytes()).hexdigest()
    wrapper=repo/'PyAnsys/scripts/setup/wait_and_revise_phase9_server6_slit_1us.py'
    details=resolve_connection_kwargs('6',start_transcript=False)
    launcher=run.WORK/('private-target100-'+tag+'.ps1');pid=run.WORK/('target100-transition-pid-'+tag+'.json')
    env={'FLUENT_SERVER_INFO_FILE6':'','FLUENT_IP6':details['ip'],'FLUENT_PORT6':details['port'],'FLUENT_PASSWORD6':details['password'],'FLUENT_ALLOW_REMOTE_HOST6':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE6':str(details['insecure_mode']).lower()}
    text="$ErrorActionPreference='Stop'\n"
    for key,value in env.items():text+='$env:'+key+' = '+quote(value)+'\n'
    text+='$p=Start-Process -FilePath '+quote(launch['host_python'])+" -ArgumentList '-E','-u',"+quote(wrapper)+' -WorkingDirectory '+quote(repo)+' -WindowStyle Hidden -RedirectStandardOutput '+quote(hostout/'target100-transition.stdout.log')+' -RedirectStandardError '+quote(hostout/'target100-transition.stderr.log')+' -PassThru\n'
    text+='[IO.File]::WriteAllText('+quote(pid)+",(@{transition_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
    write_ascii_text_new(s,str(launcher),text)
    run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(launcher)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
    result=run.WORK/('target100-transition-launched-'+tag+'.json')
    command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(launcher)+'"'
    run.base.powershell(s,"$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(run.WORK)+"}; [IO.File]::WriteAllText("+quote(result)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)")
    dispatched=json.loads(run.read_text(s,str(result)));assert dispatched['ReturnValue']==0
    run.dump(OUT/'human-1us-transition-deployed.json',{'status':'HOST_BOUNDARY_TRANSITION_DISPATCHED','launcher':dispatched,'source_hashes':hashes,'target_film_s':.1,'final_bulk_start_s':.095,'step_s':1e-6,'courant_ceiling':.8,'laptop_required_for_solve':False,'review':'Only held owned controller replaced after native boundary. Newly staged sources do not replace active code. Wrapper retries only busy preflight before any mutation; all other failures are terminal. Orphan solve reconciled, never replayed. Final horizon, exact counts, pair hash/reopen and native gates retained.'})
    print('TARGET100_HOST_BOUNDARY_TRANSITION_DISPATCHED',flush=True)

if __name__=='__main__':main()
