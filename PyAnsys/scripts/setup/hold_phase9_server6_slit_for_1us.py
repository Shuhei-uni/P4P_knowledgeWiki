"""Hold the owned controller for the human's 100 ms revision; preserve Fluent."""
import json,time
from phase9_server6_slit_common import attach,run,OUT
from deploy_phase9_server6_slit_ewf import quote

def main():
    s=attach()
    launch=json.loads((OUT/'host-launch.json').read_text())
    m=json.loads(run.read_text(s,launch['run_manifest']))
    assert m['status']=='RUNNING' and m['active_stage'].startswith('target100-lowest-growth-')
    assert m['active_target']==m['verified_native_end']+10000 and m['bulk_active'] is False
    tag=str(time.time_ns())
    receipt={'status':'HOLD_REQUESTED_FOR_HUMAN_100MS_TARGET','manifest':m,
             'native_before':run.native_iteration(s),'film_before':run.film(s),
             'fields_before':run.base.state(s)['readback']['fields'],
             'target_film_s':.1,'final_bulk_start_s':.095,'requested_step_s':1e-6,'requested_courant_ceiling':.8,
             'review':'Terminate only the exact owned Python runner. Leave native journal and Fluent intact. Its recorded 10000-update command and paired save must be reconciled before a new solve. No settings, load or solve commands in this script.'}
    run.dump(OUT/('target100-controller-hold-'+tag+'.json'),receipt)
    result=run.WORK/('target100-held-process-'+tag+'.json')
    code=("$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {"
          "$_.Name -eq 'python.exe' -and $_.CommandLine -like '*Phase9-Server6-slit154k*' "
          "-and $_.CommandLine -like '*run_phase9_server6_slit_ewf.py*'}); "
          "if ($p.Count -lt 1 -or $p.Count -gt 2) {throw 'Expected owned runner and optional venv child'}; "
          "$ids=@($p.ProcessId); $allowed=@("+str(json.loads(run.read_text(s,launch['host_output']+'\\job-manifest.json'))['worker_pid'])+")+$ids; "
          "if (@($p | Where-Object {$_.ParentProcessId -notin $allowed}).Count -gt 0) {throw 'Runner tree differs'}; "
          "[IO.File]::WriteAllText("+quote(result)+",(@{selected_runner_pids=$ids;fluent_terminated=$false}|ConvertTo-Json),[Text.Encoding]::ASCII); "
          "$p | Sort-Object @{Expression={if ($_.ParentProcessId -in $ids) {0} else {1}}} | ForEach-Object {Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue}")
    if run.base.powershell(s,code) not in (0,None):raise RuntimeError('Owned runner hold failed; reconcile before retry')
    receipt.update(status='OWNED_CONTROLLER_HELD_NATIVE_COMMAND_RECONCILIATION_PENDING',
                   process=json.loads(run.read_text(s,str(result))))
    old=OUT/'target100-controller-hold.json'
    if old.exists():run.dump(OUT/('controller-hold-before-1us-'+tag+'.json'),json.loads(old.read_text()))
    run.dump(old,receipt)
    run.dump(OUT/'human-1us-controller-hold.json',receipt)
    print('OWNED_CONTROLLER_HELD_FLUENT_PRESERVED',flush=True)

if __name__=='__main__':main()
