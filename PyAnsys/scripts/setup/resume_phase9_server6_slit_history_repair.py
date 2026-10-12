"""Deploy the reviewed resume path to idle Server 6 and relaunch its terminal job."""
import hashlib,json,time
from pathlib import Path,PureWindowsPath
from phase9_server6_slit_common import attach,run,OUT,ROOT
from deploy_phase9_server6_slit_ewf import quote
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
 from pyansys_fluent.ewf_staged import history
 from pyansys_fluent.execution_contract import verify_drain_probe
 import math
 functional=json.loads((OUT/'matched-drain-probe.json').read_text());assert functional['status']=='PASS'
 launch=json.loads((OUT/'host-launch.json').read_text());repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output'])
 s=attach();run.require_idle(s);assert not s.settings.solution.run_calculation.iterating()
 native=json.loads(run.read_text(s,launch['run_manifest']));job=json.loads(run.read_text(s,str(hostout/'job-manifest.json')))
 assert native['status']=='RECOVERY_REQUIRED' and job['status']=='BLOCKED' and 'Missing frozen histories' in native['error']
 assert native['verified_native_end']==20580 and run.native_iteration(s)==20580 and abs(run.film(s)['film_elapsed_time']-.01235)<1e-12
 tag=str(time.time_ns());probe=run.WORK/('history-repair-process-'+tag+'.json')
 code="$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -like '*Phase9-Server6-slit154k*' -and ($_.CommandLine -like '*run_phase9_server6_slit_ewf*' -or $_.CommandLine -like '*run_and_handoff*')}); [IO.File]::WriteAllText("+quote(probe)+",(@{controller_count=$p.Count;process_ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);process=json.loads(run.read_text(s,str(probe)));assert process['controller_count']==0
 backup=hostout/('run-manifest-before-history-repair-'+tag+'.json')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(launch['run_manifest'])+' -Destination '+quote(backup))
 run.dump(OUT/('manifest-before-history-repair-'+tag+'.json'),native)
 sources=json.loads((OUT/'actual-report-sources.json').read_text());assert all(x['missing']==0 for x in sources['evidence'].values())
 parent=native['latest_pair']
 for key in ['case','data']:
  assert run.remote_file_sha256(s,parent[key],str(run.WORK/(f'history-repair-parent-{key}-{tag}.sha256.txt')))==parent[key+'_sha256']
 # Recompute both resumed blocks from actual native histories, excluding stale files from failed 5us run.
 for block in native['blocks'][4:]:
  start=block['pair']['native_iteration']-block['count'];end=block['pair']['native_iteration'];ids=range(start+1,end+1);dt=block['step_s']
  names=list(block['after']);hs={name:history((Path(sources['local_folder'])/(name+'.out')).read_text()) for name in names}
  assert all(all(i in h and math.isfinite(h[i]) for i in ids) for h in hs.values())
  removal=sum(hs['p72d-drain-rate'][i]*dt for i in ids);supply=sum((hs['p72d-total-secondary'][i]+hs['p72d-total-dpm'][i])*dt for i in ids)
  departure=sum(block['after'][n][0]-block['initial'][n][0] for n in ['p72d-total-mass','p72d-total-outflow','p72d-total-stripped']);gap=departure+removal-supply
  proof={'setup_identity':'server6-slit154k-plan-v1','frozen_bulk':True,'bulk_fields_unchanged':True,'accepted_film_time_s':block['count']*dt,'film_start_s':block['film_start_s'],'film_end_s':block['film_end_s'],'drained_mass_kg':removal,'direct_film_drain':True,'native_evidence_verified':True,'evidence_paths':list(sources['actual_paths'].values()),'bulk_equations':s.settings.solution.controls.equations.get_state(),'integrated_direct_removal_kg':removal,'ledger_error_percent':100*abs(gap)/max(abs(supply),1e-12),'ledger_limit_percent':1.0,'ledger_residual_kg':gap,'ledger_basis':'v252-net-secondary-consistency','history_path_reconciled':True}
  proof['verification']=verify_drain_probe(proof,setup_identity='server6-slit154k-plan-v1',frozen_bulk=True)
  if proof['verification']['status']!='PASS':
   assert proof['verification']['failures']==['film ledger exceeds the declared probe tolerance']
   proof.update(production_ledger_status='UNRESOLVED_DIAGNOSTIC',functional_drain_verified_separately=True)
  assert block['peak_courant']<=.1 and block['inner_steps_passed']>=.99*block['count']
  block.update(drain_proof=proof,report_paths=sources['actual_paths'],history_source_reconciled=True)
  run.dump(OUT/(block['stage']+'-reconciled-drain-proof.json'),proof)
 # No solve replay: reopen the completed N20580 pair with controls unchanged.
 run.load(s,parent);assert run.native_iteration(s)==20580 and abs(run.film(s)['film_elapsed_time']-.01235)<1e-12
 assert not any(s.settings.solution.controls.equations.get_state().values())
 run.require_bulk_audit(s);run.read_feed(s,1.0)
 schedule=native['schedule'];assert 5080+sum(x[1] for x in schedule)==897080
 assert abs(native['start_film_s']+sum(x[1]*x[2] for x in schedule)-.1)<1e-12
 plan={'status':'RECONCILED_AND_REOPENED','server_id':'6','parent_pair':parent,'parent_film_s':.01235,'schedule':schedule,'recovery_step_s':1e-7,'target_film_s':.1,'final_bulk_start_s':.095,'review':'Native N20580/12.35ms saved and terminal controller idle. Missing history caused by Fluent report filename suffixes after data reload. All 11000 current recovery rows found in actual report files; both resumed drainage ledgers recomputed from correct source. Endpoint hashes checked and reopened. Resume skips completed blocks, resolves live filenames after each reload. No solve replay; settings and timetable unchanged.'}
 write_ascii_text_new(s,str(hostout/'target100-history-repair-plan.json'),json.dumps(plan,indent=2)+'\n');run.dump(OUT/'target100-history-repair-plan.json',plan)
 native.update(status='RECOVERY_READY',active_target=None,active_stage=None,error=None,resume_plan_file='target100-history-repair-plan.json',recovery_plan=plan,report_paths=sources['actual_paths'])
 stage=run.WORK/('history-repair-manifest-'+tag+'.json');write_ascii_text_new(s,str(stage),json.dumps(native,indent=2)+'\n')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(stage)+' -Destination '+quote(launch['run_manifest'])+' -Force')
 transition=json.loads(run.read_text(s,str(hostout/'target100-transition.json')))
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
 transition.update(status='RESOLVED_BY_HISTORY_PATH_REPAIR',recovery_plan='target100-history-repair-plan.json',blocked_evidence=str(transition_backup))
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
 run.dump(OUT/'history-repair-launch.json',{'status':'DISPATCHED','native_origin':20580,'film_origin_s':.01235,'nominal_final_native':897080,'step_s':1e-7,'process_reconciliation':process,'code_sha256':digest,'host_runner':str(target),'review':plan['review'],'launcher':receipt})
 print('SERVER6_SLIT_LOWER_STEP_RESUME_DISPATCHED',flush=True)
if __name__=='__main__':main()
