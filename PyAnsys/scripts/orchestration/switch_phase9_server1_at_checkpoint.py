"""Replace the old Python command owner only after its saved idle endpoint.

Waiting reads Windows files only. No Fluent interrupt or process stop is sent.
The old Python runner is stopped at its verified checkpoint before it can issue
another section. Its paired endpoint is reconciled before the new ramp starts.
"""
import argparse,hashlib,json,math,os,re,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from pyansys_fluent.stage4_native import exclusive_writer_lock

def checkpoint_ready(m,spec):
 if m.get('verified_native_end',0)>spec['boundary_native']:raise RuntimeError('Boundary already passed; do not replay')
 if m.get('status')!='RUNNING':
  error=m.get('error','').strip().splitlines()[-1:]
  limit_error=error and error[0]=='RuntimeError: Film Courant exceeds operating ceiling; review step before continuation'
  if error and error[0]=='RuntimeError: Frozen drain proof requires repair before next step':
   failures=m['blocks'][-1].get('drain_proof',{}).get('verification',{}).get('failures',[])
   limit_error=bool(failures) and all(x in ('film ledger exceeds the declared probe tolerance','accepted film advancement and positive direct removal are required') for x in failures)
  if not (m.get('status')=='RECOVERY_REQUIRED' and limit_error and m.get('verified_native_end')==spec['boundary_native']):raise RuntimeError('Original controller reported an error before boundary')
 if m.get('verified_native_end')!=spec['boundary_native']:return False
 if m.get('active_target') is not None:raise RuntimeError('Old owner already submitted another command; do not interrupt')
 b=m['blocks'][-1]
 if b['stage']!=spec['boundary_stage'] or b['pair']['native_iteration']!=spec['boundary_native']:raise RuntimeError('Wrong boundary pair')
 if not math.isclose(b['film_end_s'],spec['boundary_film_s'],abs_tol=1e-12):raise RuntimeError('Wrong boundary film time')
 return True

def reconcile(spec,m):
 from phase9_server1_680k_common import attach,run,OUT
 from pyansys_fluent.ewf_staged import FILM,history
 from pyansys_fluent.execution_contract import verify_drain_probe
 with exclusive_writer_lock(OUT/'controller.lock'):
  s=attach();run.require_idle(s)
  if run.native_iteration(s)!=spec['boundary_native']:raise RuntimeError('Live endpoint differs; no replay')
  b=m['blocks'][-1];pair=b['pair'];parent=m['blocks'][-2]['pair']
  for key in ('case','data'):
   with Path(pair[key]).open('rb') as f:
    if hashlib.file_digest(f,'sha256').hexdigest()!=pair[key+'_sha256']:raise RuntimeError('Boundary hash differs')
  rows=[tuple(map(float,x.groups())) for x in FILM.finditer(Path(m['active_transcript']).read_text())]
  if len(rows)!=b['count'] or any(not all(math.isfinite(v) for v in row) for row in rows):raise RuntimeError('Missing/nonfinite completed film rows')
  if any(not math.isclose(row[0],b['film_start_s']+(i+1)*b['step_s'],abs_tol=1e-10) for i,row in enumerate(rows)):raise RuntimeError('Completed film clock differs')
  if re.search(r'floating point exception|fatal error|received signal|Divergence detected',Path(m['active_transcript']).read_text(),re.I):raise RuntimeError('Native error at boundary')
  run.load(s,pair);current=run.base.state(s)['readback']['fields']
  run.load(s,parent);previous=run.base.state(s)['readback']['fields'];run.load(s,pair)
  unchanged=all(math.isclose(v[0],previous[k][0],rel_tol=1e-10,abs_tol=1e-12) for k,v in current.items() if not k.startswith('p72a-e2.7-ewf-'))
  if not unchanged:raise RuntimeError('Frozen bulk fields changed at boundary')
  if run.native_iteration(s)!=spec['boundary_native'] or not math.isclose(run.film(s)['film_elapsed_time'],spec['boundary_film_s'],abs_tol=1e-12):raise RuntimeError('Boundary reopen differs')
  names=list(b['initial']);hs={name:history(Path(m['report_paths'][name]).read_text()) for name in names}
  ids=range(spec['boundary_native']-b['count']+1,spec['boundary_native']+1)
  if any(not all(i in h and math.isfinite(h[i]) for i in ids) for h in hs.values()):raise RuntimeError('Boundary histories missing/nonfinite')
  dt=b['step_s'];initial=b['initial'];after=b['after']
  removal=sum(hs['p72d-drain-rate'][i]*dt for i in ids)
  supply=sum((hs['p72d-total-secondary'][i]+hs['p72d-total-dpm'][i])*dt for i in ids)
  gap=sum(after[n][0]-initial[n][0] for n in ('p72d-total-mass','p72d-total-outflow','p72d-total-stripped'))+removal-supply
  proof={'setup_identity':'server1-680k-plan-v1','frozen_bulk':True,'bulk_fields_unchanged':unchanged,'accepted_film_time_s':b['count']*dt,'film_start_s':b['film_start_s'],'film_end_s':b['film_end_s'],'drained_mass_kg':removal,'direct_film_drain':True,'native_evidence_verified':True,'evidence_paths':[m['active_transcript'],m['report_paths']['p72d-drain-rate']],'bulk_equations':s.settings.solution.controls.equations.get_state(),'integrated_direct_removal_kg':removal,'ledger_error_percent':100*abs(gap)/max(abs(supply),1e-12),'ledger_limit_percent':1.0,'ledger_residual_kg':gap,'gross_ledger_residual_kg':gap+after['p72d-total-separated'][0]-initial['p72d-total-separated'][0],'ledger_basis':'v252-net-secondary-consistency','native_transcript':m['active_transcript'],'continuation':'NUMERICAL_LIMITS_DIAGNOSTIC_ONLY'}
  proof['verification']=verify_drain_probe(proof,setup_identity='server1-680k-plan-v1',frozen_bulk=True);b['drain_proof']=proof
  m.update(status='RECOVERY_REQUIRED',active_target=None,recovery_ready=True,recovery_reason='Human changed next step at saved checkpoint; no native solve interrupted or replayed',no_limit_checks=True,film_courant_limit=None)
  m.pop('error',None);run.dump(OUT/'run-manifest.json',m)

def main():
 p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);a=p.parse_args();spec=json.loads(a.spec.read_text())
 receipt=Path(spec['receipt']);mp=Path(spec['run_manifest'])
 def save(state):
  tmp=receipt.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(receipt)
 if receipt.exists():raise RuntimeError('Existing boundary receipt; refuse replay')
 state={'status':'WAITING_FOR_SAVED_BOUNDARY','pid':os.getpid(),'boundary_native':spec['boundary_native'],'boundary_film_s':spec['boundary_film_s'],'next_step_s':2.5e-6,'next_count':10000,'later_step_s':5e-6,'target_film_s':.2,'laptop_required':False,'fluent_interrupt_sent':False};save(state)
 try:
  # Validate the exact Python owner once, then keep an OS handle to that same
  # process. This prevents PID reuse and avoids PowerShell startup latency at
  # the checkpoint boundary. No process is changed during this validation.
  code="$ErrorActionPreference='Stop'; $p=Get-CimInstance Win32_Process -Filter 'ProcessId = "+str(spec['old_controller_pid'])+"'; if(-not $p -or $p.CommandLine -notlike '"+('*'+spec['old_runner']+'*').replace("'","''")+"') {throw 'Original controller identity mismatch'}"
  check=subprocess.run(['powershell.exe','-NoProfile','-Command',code],capture_output=True,text=True)
  if check.returncode:raise RuntimeError('Original controller identity failed')
  import ctypes
  from ctypes import wintypes
  kernel=ctypes.WinDLL('kernel32',use_last_error=True)
  kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
  kernel.TerminateProcess.argtypes=[wintypes.HANDLE,wintypes.UINT];kernel.TerminateProcess.restype=wintypes.BOOL
  kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];kernel.WaitForSingleObject.restype=wintypes.DWORD
  kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
  handle=kernel.OpenProcess(0x100001,False,spec['old_controller_pid'])
  if not handle:raise ctypes.WinError(ctypes.get_last_error())
  state.update(owner_handle_ready=True,old_controller_pid=spec['old_controller_pid']);save(state)
  while True:
   try:m=json.loads(mp.read_text())
   except (FileNotFoundError,json.JSONDecodeError):time.sleep(.01);continue
   if m.get('server_id')!='1' or m.get('cells')!=679970:raise RuntimeError('Wrong owned lane')
   if checkpoint_ready(m,spec):break
   time.sleep(.01)
  # The manifest marks a completed native journal and hashed pair. Stop the
  # Python owner immediately; Fluent is a separate process and stays open.
  if kernel.WaitForSingleObject(handle,0)!=0 and not kernel.TerminateProcess(handle,0):raise ctypes.WinError(ctypes.get_last_error())
  if kernel.WaitForSingleObject(handle,5000)!=0:raise RuntimeError('Original command owner did not exit')
  kernel.CloseHandle(handle)
  try:latest=json.loads(mp.read_text())
  except json.JSONDecodeError:latest=m
  if not checkpoint_ready(latest,spec):raise RuntimeError('Boundary ownership changed; no new solve')
  m=latest
  (receipt.parent/(receipt.stem+'-original-boundary.json')).write_text(json.dumps(m,indent=2)+'\n')
  state.update(status='RECONCILING_SAVED_BOUNDARY',old_python_controller_stopped=True);save(state)
  for key in ('runner','verifier'):
   if hashlib.sha256(Path(spec[key]).read_bytes()).hexdigest()!=spec[key+'_sha256']:raise RuntimeError('Staged source hash changed')
  reconcile(spec,m)
  with Path(spec['runner_log']).open('x') as log:
   child=subprocess.Popen([sys.executable,'-E','-u',spec['runner'],'--resume','--ledger-diagnostic-only','--no-limit-checks','--ramp-to-5us'],cwd=spec['repo'],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
   state.update(status='RAMP_CONTROLLER_RUNNING',controller_pid=child.pid);save(state);code=child.wait()
  if code:raise RuntimeError('Ramp controller returned an execution error; no replay')
  with Path(spec['verifier_log']).open('x') as log:
   check=subprocess.run([sys.executable,'-E',spec['verifier']],cwd=spec['repo'],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
  if check.returncode:raise RuntimeError('Final ramp endpoint verification failed')
  state.update(status='COMPLETE_VERIFIED',native_end=104080,film_end_s=.2);save(state)
 except BaseException:
  state.update(status='ERROR',error=traceback.format_exc());save(state);raise

if __name__=='__main__':
 with exclusive_writer_lock(ROOT/'output/phase9-ewf-server1-680k/20261009/step-change-queue.lock'):
  main()
