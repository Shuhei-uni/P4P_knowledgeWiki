"""Deploy the reviewed resume path to idle Server 6 and relaunch its terminal job."""
import hashlib,json,time
from pathlib import Path,PureWindowsPath
from phase9_server6_slit_common import attach,run,OUT,ROOT
from deploy_phase9_server6_slit_ewf import quote
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
 functional=json.loads((OUT/'matched-drain-probe.json').read_text());assert functional['status']=='PASS'
 launch=json.loads((OUT/'host-launch.json').read_text());repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output'])
 s=attach();run.require_idle(s);assert not s.settings.solution.run_calculation.iterating()
 native=json.loads(run.read_text(s,launch['run_manifest']));job=json.loads(run.read_text(s,str(hostout/'job-manifest.json')))
 assert native['status']=='RECOVERY_REQUIRED' and job['status']=='BLOCKED'
 assert 'Film Courant exceeds operating ceiling' in native['error']
 assert native['verified_native_end']==14580 and abs(native['accepted_film_s']-.03625)<1e-12
 assert run.native_iteration(s)==14580 and abs(run.film(s)['film_elapsed_time']-.03625)<1e-12
 tag=str(time.time_ns());probe=run.WORK/('resume-process-'+tag+'.json')
 code="$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -like '*Phase9-Server6-slit154k*' -and ($_.CommandLine -like '*run_phase9_server6_slit_ewf*' -or $_.CommandLine -like '*run_and_handoff*')}); [IO.File]::WriteAllText("+quote(probe)+",(@{controller_count=$p.Count;process_ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);process=json.loads(run.read_text(s,str(probe)));assert process['controller_count']==0
 # Controller termination and failed endpoint preservation precede rollback.
 run.dump(OUT/('failed-5us-attempt-'+tag+'.json'),native)
 backup=hostout/('run-manifest-before-recovery-'+tag+'.json')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(launch['run_manifest'])+' -Destination '+quote(backup))
 healthy=native['blocks'][3]
 assert healthy['stage']=='step-5us' and healthy['peak_courant']<=.1 and healthy['pair']['native_iteration']==9580
 parent=healthy['pair']
 for key in ['case','data']:
  assert run.remote_file_sha256(s,parent[key],str(run.WORK/(f'recovery-parent-{key}-{tag}.sha256.txt')))==parent[key+'_sha256']
 # Failed endpoint already saved and hashed by the terminal controller; retain it unchanged.
 for key in ['case','data']:
  assert run.remote_file_exists(s,native['latest_pair'][key])
 run.load(s,parent)
 assert run.native_iteration(s)==9580 and abs(run.film(s)['film_elapsed_time']-.01125)<1e-12
 assert not any(s.settings.solution.controls.equations.get_state().values())
 run.require_bulk_audit(s);run.read_feed(s,1.0)
 accepted=native['schedule'][:4]
 remaining=[('recovery-2p5us-proof',1000,2.5e-6,False)]
 remaining += [(f'recovery-growth-{i}',10000,2.5e-6,False) for i in range(1,8)]
 remaining += [('recovery-to-195ms',2500,2.5e-6,False),('recovery-bulk-to-200ms',2000,2.5e-6,True)]
 assert abs(.01125+sum(x[1]*x[2] for x in remaining[:-1])-.195)<1e-12
 assert abs(sum(x[1]*x[2] for x in remaining[-1:])-.005)<1e-12
 schedule=accepted+remaining
 plan={'status':'RECONCILED_AND_REOPENED','server_id':'6','parent_pair':parent,'parent_film_s':.01125,'schedule':schedule,'failed_attempt':str(backup),'recovery_step_s':2.5e-6,'review':'Terminal Courant failure; old host controller absent; failed pair preserved; exact healthy N9580 pair hash verified and reopened. Reduce only step/cadence, use 1000-update proof then fixed long blocks. Final 195–200 ms bulk active; exclude failed 5000 updates.'}
 write_ascii_text_new(s,str(hostout/'lower-step-recovery-plan.json'),json.dumps(plan,indent=2)+'\n');run.dump(OUT/'lower-step-recovery-plan.json',plan)
 native.update(status='RECOVERY_READY',blocks=native['blocks'][:4],schedule=schedule,latest_pair=parent,verified_native_end=9580,accepted_film_s=.01125,active_target=None,active_stage=None,error=None,native_target_final=85080,recovery_plan=plan)
 writepath=run.WORK/('reconciled-manifest-'+tag+'.json');write_ascii_text_new(s,str(writepath),json.dumps(native,indent=2)+'\n')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(writepath)+' -Destination '+quote(launch['run_manifest'])+' -Force')
 runner=ROOT/'scripts/setup/run_phase9_server6_slit_ewf.py';target=repo/'PyAnsys/scripts/setup'/runner.name;staged=run.WORK/('reviewed-resume-'+tag+'.py')
 text=runner.read_text();write_ascii_text_new(s,str(staged),text)
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(target)+' -Destination '+quote(str(target)+'.before-'+tag)+"; Copy-Item -LiteralPath "+quote(staged)+' -Destination '+quote(target)+' -Force')
 digest=run.remote_file_sha256(s,str(target),str(run.WORK/('resume-code-'+tag+'.sha256.txt')));assert run.read_text(s,str(target))==text
 staged_digest=run.remote_file_sha256(s,str(staged),str(run.WORK/('resume-staged-'+tag+'.sha256.txt')));assert digest==staged_digest
 if run.remote_file_exists(s,str(hostout/'matched-drain-probe.json')):
  assert json.loads(run.read_text(s,str(hostout/'matched-drain-probe.json')))==functional
 else:write_ascii_text_new(s,str(hostout/'matched-drain-probe.json'),json.dumps(functional,indent=2)+'\n')
 # Verify the exact deployed runner import in the existing host runtime.
 import_probe=run.WORK/('resume-import-'+tag+'.json')
 import_code="import sys;sys.path[:0]=["+repr(str(repo/'PyAnsys/scripts/setup'))+"];import run_phase9_server6_slit_ewf;print('DEPLOYED_RESUME_IMPORT_PASS')"
 ps="$ErrorActionPreference='Stop'; $t=(& "+quote(launch['host_python'])+" -E -c "+quote(import_code)+" 2>&1 | Out-String); $rc=$LASTEXITCODE; [IO.File]::WriteAllText("+quote(import_probe)+",(@{return_code=$rc;output=$t}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,ps);import_result=json.loads(run.read_text(s,str(import_probe)));assert import_result['return_code']==0 and 'DEPLOYED_RESUME_IMPORT_PASS' in import_result['output']
 verifier=ROOT/'scripts/inspection/verify_phase9_server6_slit_ewf.py'
 verifier_target=repo/'PyAnsys/scripts/inspection'/verifier.name
 verifier_stage=run.WORK/('reviewed-verifier-'+tag+'.py')
 write_ascii_text_new(s,str(verifier_stage),verifier.read_text())
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(verifier_target)+' -Destination '+quote(str(verifier_target)+'.before-'+tag)+"; Copy-Item -LiteralPath "+quote(verifier_stage)+' -Destination '+quote(verifier_target)+' -Force')
 assert run.read_text(s,str(verifier_target))==verifier.read_text()
 oldspec=json.loads(run.read_text(s,launch['job_spec']));spec=oldspec.copy();spec['runner']=dict(oldspec['runner']);spec['runner']['command']=[arg for arg in spec['runner']['command'] if arg!='--resume']+['--resume'];spec['runner']['log']=str(hostout/('resume-runner-'+tag+'.log'))
 specpath=repo/('phase9-server6-resume-'+tag+'.json');write_ascii_text_new(s,str(specpath),json.dumps(spec,indent=2)+'\n')
 details=resolve_connection_kwargs('6',start_transcript=False);script=run.WORK/('private-resume-'+tag+'.ps1');pid=run.WORK/('resume-pid-'+tag+'.json')
 values={'FLUENT_SERVER_INFO_FILE6':'','FLUENT_IP6':details['ip'],'FLUENT_PORT6':details['port'],'FLUENT_PASSWORD6':details['password'],'FLUENT_ALLOW_REMOTE_HOST6':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE6':str(details['insecure_mode']).lower()}
 content="$ErrorActionPreference='Stop'\n"
 for k,v in values.items():content+='$env:'+k+' = '+quote(v)+'\n'
 content+='$p=Start-Process -FilePath '+quote(launch['host_python'])+" -ArgumentList '-E','-u',"+quote(repo/'PyAnsys/scripts/orchestration/run_and_handoff.py')+",'--job',"+quote(specpath)+",'--worker','--force' -WindowStyle Hidden -RedirectStandardOutput "+quote(run.WORK/('resume-worker-'+tag+'.stdout.log'))+' -RedirectStandardError '+quote(run.WORK/('resume-worker-'+tag+'.stderr.log'))+' -PassThru\n'
 content+='[IO.File]::WriteAllText('+quote(pid)+",(@{worker_pid=$p.Id}|ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
 write_ascii_text_new(s,str(script),content)
 run.base.powershell(s,"$ErrorActionPreference='Stop'; $me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe "+quote(script)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null")
 result=run.WORK/('resume-launch-'+tag+'.json');command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
 run.base.powershell(s,"$ErrorActionPreference='Stop'; $r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+';CurrentDirectory='+quote(run.WORK)+"}; [IO.File]::WriteAllText("+quote(result)+",($r|Select-Object ProcessId,ReturnValue|ConvertTo-Json),[Text.Encoding]::ASCII)")
 receipt=json.loads(run.read_text(s,str(result)));assert receipt['ReturnValue']==0
 launch.update(job_spec=str(specpath),runner_log=spec['runner']['log'],resume_launcher=receipt,resume_code_sha256=digest);run.dump(OUT/'host-launch.json',launch)
 run.dump(OUT/'resume-launch.json',{'status':'DISPATCHED','native_origin':9580,'film_origin_s':.01125,'nominal_final_native':85080,'step_s':2.5e-6,'process_reconciliation':process,'code_sha256':digest,'host_runner':str(target),'review':'Healthy N9580 restored; failed N14580 pair preserved; terminal worker and idle native state verified; no active host controller; reviewed --resume preserves first four stages and recalculates remaining horizon at 2.5 us; clock, bulk and Courant gates retained.','launcher':receipt})
 print('SERVER6_SLIT_LOWER_STEP_RESUME_DISPATCHED',flush=True)
if __name__=='__main__':main()
