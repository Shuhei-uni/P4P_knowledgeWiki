"""Supersede owned boundary waiter, interrupt one native solve, preserve partial pair."""
import json,time
from phase9_server6_slit_common import attach,run,OUT
from deploy_phase9_server6_slit_ewf import quote

def main():
 s=attach();launch=json.loads((OUT/'host-launch.json').read_text());m=json.loads(run.read_text(s,launch['run_manifest']))
 assert m['status']=='RUNNING' and m['active_stage']=='strict-parent-0p1-known-window' and m['active_target']==64580
 tag=str(time.time_ns());probe=run.WORK/('cancel-courant-waiter-'+tag+'.json')
 code=("$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -like '*Phase9-Server6-slit154k*' -and $_.CommandLine -like '*wait_and_revise_phase9_server6_slit_courant_only.py*'}); if ($p.Count -lt 1 -or $p.Count -gt 2) {throw 'Unexpected waiter tree'}; $ids=@($p.ProcessId); if ($p.Count -eq 2 -and @($p | Where-Object {$_.ParentProcessId -in $ids}).Count -ne 1) {throw 'Waiter tree differs'}; [IO.File]::WriteAllText("+quote(probe)+",(@{selected_waiter_pids=$ids;fluent_terminated=$false}|ConvertTo-Json),[Text.Encoding]::ASCII); $p | Sort-Object @{Expression={if ($_.ParentProcessId -in $ids) {0} else {1}}} | ForEach-Object {Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue}")
 assert run.base.powershell(s,code) in (0,None)
 state={'status':'OWNED_WAITER_CANCELLED_INTERRUPT_PENDING','manifest':m,'process':json.loads(run.read_text(s,str(probe))),'native_before':run.native_iteration(s),'film_before':run.film(s),'never_exit_fluent':True,'authority':'Human: continue N70580 at2.5us'}
 run.dump(OUT/'n70580-partial-preservation.json',state)
 control=s.settings.solution.run_calculation
 if control.interrupt.is_active() and not control.iterate.is_active():
  state['interrupt_submitted']=True;run.dump(OUT/'n70580-partial-preservation.json',state);control.interrupt()
 else:state['interrupt_submitted']=False
 # Wait for native journal completion/idle; no replay of interrupted iterations.
 for attempt in range(36):
  try:
   run.require_idle(s)
   if control.iterating():raise RuntimeError('still iterating')
   n=run.native_iteration(s);clock=run.film(s)['film_elapsed_time'];time.sleep(2)
   if n!=run.native_iteration(s) or abs(clock-run.film(s)['film_elapsed_time'])>1e-12:raise RuntimeError('clock changing')
   break
  except RuntimeError:
   time.sleep(5)
 else:raise RuntimeError('Native idle unconfirmed; do not load or replay')
 pair=run.save(s,run.WORK/'slit154k/ewf-200ms',f'preserved-before-N70580-partial-N{n}-{tag}')
 assert run.native_iteration(s)==n and abs(run.film(s)['film_elapsed_time']-clock)<1e-12
 state.update(status='PARTIAL_NATIVE_ENDPOINT_PRESERVED_IDLE',native_iteration=n,film=run.film(s),pair=pair,no_solve_replay=True)
 run.dump(OUT/'n70580-partial-preservation.json',state)
 print('PARTIAL_NATIVE_ENDPOINT_PRESERVED_IDLE',n,clock,flush=True)
if __name__=='__main__':main()
