"""Deploy the reviewed resume path to idle Server 6 and relaunch its terminal job."""
import hashlib,json,time
from pathlib import Path,PureWindowsPath
from phase9_server6_slit_common import attach,run,OUT,ROOT
from deploy_phase9_server6_slit_ewf import quote
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
 import math
 functional=json.loads((OUT/'matched-drain-probe.json').read_text());assert functional['status']=='PASS'
 launch=json.loads((OUT/'host-launch.json').read_text());repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output'])
 failure=json.loads((OUT/'failed-0p1us-growth6.json').read_text())
 s=attach();run.require_idle(s);assert not s.settings.solution.run_calculation.iterating()
 native=json.loads(run.read_text(s,launch['run_manifest']));job=json.loads(run.read_text(s,str(hostout/'job-manifest.json')))
 transition=json.loads(run.read_text(s,str(hostout/'target100-transition.json')))
 assert transition['status']=='BLOCKED' and job['status']=='BLOCKED'
 assert native['status']=='RUNNING' and native['active_stage']=='target100-lowest-growth-6' and native['active_target']==70580
 assert run.native_iteration(s)==70580 and abs(run.film(s)['film_elapsed_time']-.01735)<1e-10
 assert failure['status']=='NUMERICAL_COURANT_FAILURE_ENDPOINT_PRESERVED' and failure['peak_courant']>.8
 tag=str(time.time_ns());probe=run.WORK/('human1us-recovery-process-'+tag+'.json')
 code="$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -like '*Phase9-Server6-slit154k*' -and ($_.CommandLine -like '*run_phase9_server6_slit_ewf*' -or $_.CommandLine -like '*run_and_handoff*' -or $_.CommandLine -like '*wait_and_revise_phase9_server6_slit_1us*')}); [IO.File]::WriteAllText("+quote(probe)+",(@{controller_count=$p.Count;process_ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);process=json.loads(run.read_text(s,str(probe)));assert process['controller_count']==0
 backup=hostout/('run-manifest-before-human1us-recovery-'+tag+'.json')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(launch['run_manifest'])+' -Destination '+quote(backup))
 run.dump(OUT/('manifest-before-human1us-recovery-'+tag+'.json'),native)
 for key in ['case','data']:
  assert run.remote_file_sha256(s,failure['pair'][key],str(run.WORK/(f'failed-growth6-{key}-{tag}.sha256.txt')))==failure['pair'][key+'_sha256']
 parent=native['latest_pair'];assert parent==failure['healthy_parent'] and parent['native_iteration']==60580
 for key in ['case','data']:
  assert run.remote_file_sha256(s,parent[key],str(run.WORK/(f'human1us-parent-{key}-{tag}.sha256.txt')))==parent[key+'_sha256']
 run.load(s,parent);assert run.native_iteration(s)==60580 and abs(run.film(s)['film_elapsed_time']-.01635)<1e-10
 assert not any(s.settings.solution.controls.equations.get_state().values());run.require_bulk_audit(s);run.read_feed(s,1.0)
 assert native['blocks'][-1]['pair']==parent and native['blocks'][-1]['peak_courant']<=.8
 accepted=native['schedule'][:len(native['blocks'])];assert [x[0] for x in accepted]==[b['stage'] for b in native['blocks']]
 remaining=[('human-1us-proof',1000,1e-6,False)]
 remaining += [(f'human-1us-growth-{i}',10000,1e-6,False) for i in range(1,8)]
 remaining += [('human-1us-to-95ms',7650,1e-6,False),('human-1us-bulk-95-to-100ms',5000,1e-6,True)]
 schedule=accepted+remaining
 assert abs(.01635+sum(x[1]*x[2] for x in remaining if not x[3])-.095)<1e-12
 assert 60580+sum(x[1] for x in remaining)==144230
 assert abs(native['start_film_s']+sum(x[1]*x[2] for x in schedule)-.1)<1e-10
 plan={'status':'RECONCILED_AND_REOPENED','server_id':'6','parent_pair':parent,'parent_film_s':.01635,'schedule':schedule,'target_film_s':.1,'final_bulk_start_s':.095,'step_s':1e-6,'courant_ceiling':.8,'failed_attempt':failure,'review':'Human requested1us fixed step and0.8 ceiling. Old0.1us growth6 completed10000updates but peak0.8694275 exceeds revised ceiling. FailedN70580/17.35ms pair hashes/transcript preserved; idle native, terminal job/transition and absent owned controller reconciled. Last acceptedN60580/16.35ms hashes checked/reopened. Exclude failed10000updates. Apply1us/DPM20/drainrefresh1us with save/reopen and readback, then1000-update qualification; retain inner100max/1e-5/99percent qualification. Final95-100ms bulkactive; nominalfinalN144230. No timeout replay.'}
 write_ascii_text_new(s,str(hostout/'human-1us-recovery-plan.json'),json.dumps(plan,indent=2)+'\n');run.dump(OUT/'human-1us-recovery-plan.json',plan)
 native.update(status='RECOVERY_READY',schedule=schedule,latest_pair=parent,verified_native_end=60580,accepted_film_s=.01635,active_target=None,active_stage=None,error=None,native_target_final=144230,target_film_s=.1,courant_ceiling=.8,resume_plan_file='human-1us-recovery-plan.json',recovery_plan=plan)
 stage=run.WORK/('human1us-recovery-manifest-'+tag+'.json');write_ascii_text_new(s,str(stage),json.dumps(native,indent=2)+'\n')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(stage)+' -Destination '+quote(launch['run_manifest'])+' -Force')
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
 transition_backup=hostout/('target100-transition-blocked-'+tag+'.json')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(hostout/'target100-transition.json')+' -Destination '+quote(transition_backup))
 transition.update(status='RESOLVED_BY_HUMAN_1US_RECOVERY',recovery_plan='human-1us-recovery-plan.json',blocked_evidence=str(transition_backup))
 transition_stage=run.WORK/('transition-resolved-'+tag+'.json');write_ascii_text_new(s,str(transition_stage),json.dumps(transition,indent=2)+'\n')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(transition_stage)+' -Destination '+quote(hostout/'target100-transition.json')+' -Force')
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
 run.dump(OUT/'human-1us-recovery-launch.json',{'status':'DISPATCHED','native_origin':60580,'film_origin_s':.01635,'nominal_final_native':144230,'step_s':1e-6,'courant_ceiling':.8,'process_reconciliation':process,'code_sha256':digest,'host_runner':str(target),'review':plan['review'],'launcher':receipt})
 print('SERVER6_SLIT_LOWER_STEP_RESUME_DISPATCHED',flush=True)
if __name__=='__main__':main()
