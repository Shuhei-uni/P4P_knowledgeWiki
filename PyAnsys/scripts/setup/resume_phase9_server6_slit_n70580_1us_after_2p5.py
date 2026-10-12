"""Deploy the reviewed resume path to idle Server 6 and relaunch its terminal job."""
import hashlib,json,time
from pathlib import Path,PureWindowsPath
from phase9_server6_slit_common import attach,run,OUT,ROOT
from deploy_phase9_server6_slit_ewf import quote
from run_phase9_server6_slit_ewf import lane_file_sha256
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
 import math
 functional=json.loads((OUT/'matched-drain-probe.json').read_text());assert functional['status']=='PASS'
 launch=json.loads((OUT/'host-launch.json').read_text());repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output'])
 selected=json.loads((OUT/'failed-0p1us-growth6.json').read_text())
 preserved=json.loads((OUT/'n80580-host-native-summary.json').read_text())
 assert preserved['status']=='HOST_NATIVE_TRANSCRIPT_AND_PAIR_SUMMARY' and preserved['film_rows']==10000 and preserved['peak_courant']>.8 and preserved['clocks_match'] and preserved['finite_film_rows'] and not preserved['fatal_lines']
 s=attach();run.require_idle(s);assert not s.settings.solution.run_calculation.iterating()
 native=json.loads(run.read_text(s,launch['run_manifest']));job=json.loads(run.read_text(s,str(hostout/'job-manifest.json')))
 transition=json.loads(run.read_text(s,str(hostout/'target100-transition.json')))
 assert job['status']=='BLOCKED' and native['status']=='RECOVERY_REQUIRED' and native['active_stage']=='n70580-2p5us-growth-1'
 assert run.native_iteration(s)==preserved['pair']['native_iteration'] and abs(run.film(s)['film_elapsed_time']-preserved['last_film_row'][0])<1e-10
 tag=str(time.time_ns());probe=run.WORK/('n70580-owner-process-'+tag+'.json')
 code="$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -like '*Phase9-Server6-slit154k*' -and ($_.CommandLine -like '*run_phase9_server6_slit_ewf*' -or $_.CommandLine -like '*run_and_handoff*' -or $_.CommandLine -like '*wait_and_revise_phase9_server6_slit*')}); [IO.File]::WriteAllText("+quote(probe)+",(@{controller_count=$p.Count;process_ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);process=json.loads(run.read_text(s,str(probe)));assert process['controller_count']==0
 backup=hostout/('run-manifest-before-N70580-'+tag+'.json')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(launch['run_manifest'])+' -Destination '+quote(backup))
 run.dump(OUT/('manifest-before-N70580-'+tag+'.json'),native)
 for key in ['case','data']:
  assert lane_file_sha256(s,preserved['pair'][key],str(run.WORK/(f'preserved-partial-{key}-{tag}.sha256.txt')))==preserved['pair'][key+'_sha256']
 parent=selected['pair'];assert parent['native_iteration']==70580
 for key in ['case','data']:
  assert lane_file_sha256(s,parent[key],str(run.WORK/(f'selected-N70580-{key}-{tag}.sha256.txt')))==parent[key+'_sha256']
 run.load(s,parent);assert run.native_iteration(s)==70580 and abs(run.film(s)['film_elapsed_time']-.01735)<1e-10
 assert not any(s.settings.solution.controls.equations.get_state().values());run.require_bulk_audit(s);run.read_feed(s,1.0)
 remaining=[(f'n70580-recovery-1us-growth-{i}',10000,1e-6,False) for i in range(1,8)]
 remaining += [('n70580-recovery-1us-to-95ms',7650,1e-6,False),('n70580-recovery-1us-bulk-95-to-100ms',5000,1e-6,True)]
 assert abs(.01735+sum(x[1]*x[2] for x in remaining if not x[3])-.095)<1e-12
 assert 70580+sum(x[1] for x in remaining)==153230
 assert abs(.01735+sum(x[1]*x[2] for x in remaining)-.1)<1e-10
 plan={'status':'RECONCILED_AND_REOPENED','server_id':'6','parent_pair':parent,'parent_film_s':.01735,'schedule':remaining,'target_film_s':.1,'final_bulk_start_s':.095,'step_s':1e-6,'courant_ceiling':.8,'human_selected_parent_prior_courant_peak':selected['peak_courant'],'failed_2p5us_attempt':preserved,'review':'2.5us command completed10000updates N80580/42.35ms; nativeclock,fulltranscript andpairedSHA256 verified. Controller firstfailedreadingemptycertutilhash output; hoststreamsummary revealed peakCourant4.292395>0.8, so preservedfailedpair andno acceptance/replay. Recover fromexplicitlyselected70580/17.35ms atnextlower1us,DPM20/drainrefresh1us;100max/1e-5 unchangedanddiagnosticsonly. First10000fixedupdates thenlonggrowth; noinner/ledgerqualificationgate. NewServer6-onlyPowerShellGetFileHash withdurableASCIIoutput,finitepollingandexactknownhashcomparison replacesfragilecertutilforactivation/block/finalcopyhashes. 77650frozenupdates to95ms,5000bulkactive to100ms;nominal153230. Preserveoldmanifests,failedpairs,sourceparentprovenance; noFluentexit orotherlanechanges.'}
 name='n70580-recovery-1us-plan.json'
 write_ascii_text_new(s,str(hostout/name),json.dumps(plan,indent=2)+'\n');run.dump(OUT/name,plan)
 native.update(status='RECOVERY_READY',campaign_original_start_pair=native.get('campaign_original_start_pair',native['start_pair']),campaign_original_start_film_s=native.get('campaign_original_start_film_s',native['start_film_s']),human_adopted_checkpoint=selected,start_pair=parent,start_film_s=.01735,blocks=[],schedule=remaining,latest_pair=parent,verified_native_end=70580,accepted_film_s=.01735,active_target=None,active_stage=None,active_journal=None,active_transcript=None,error=None,native_target_final=153230,target_film_s=.1,courant_ceiling=.8,resume_plan_file=name,recovery_plan=plan,numerical_acceptance_policy='courant_only')
 stage=run.WORK/('n70580-manifest-'+tag+'.json');write_ascii_text_new(s,str(stage),json.dumps(native,indent=2)+'\n')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(stage)+' -Destination '+quote(launch['run_manifest'])+' -Force')
 runner=ROOT/'scripts/setup/run_phase9_server6_slit_ewf.py';target=repo/'PyAnsys/scripts/setup'/runner.name;staged=run.WORK/('reviewed-resume-'+tag+'.py')
 text=runner.read_text();write_ascii_text_new(s,str(staged),text)
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(target)+' -Destination '+quote(str(target)+'.before-'+tag)+"; Copy-Item -LiteralPath "+quote(staged)+' -Destination '+quote(target)+' -Force')
 digest=lane_file_sha256(s,str(target),str(run.WORK/('resume-code-'+tag+'.sha256.txt')));assert run.read_text(s,str(target))==text
 staged_digest=lane_file_sha256(s,str(staged),str(run.WORK/('resume-staged-'+tag+'.sha256.txt')));assert digest==staged_digest
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
 transition.update(status='RESOLVED_BY_N70580_1US_RECOVERY',recovery_plan='n70580-recovery-1us-plan.json',blocked_evidence=str(transition_backup))
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
 run.dump(OUT/'n70580-recovery-1us-launch.json',{'status':'DISPATCHED','native_origin':70580,'film_origin_s':.01735,'nominal_final_native':153230,'step_s':1e-6,'courant_ceiling':.8,'process_reconciliation':process,'code_sha256':digest,'host_runner':str(target),'review':plan['review'],'launcher':receipt})
 print('SERVER6_SLIT_LOWER_STEP_RESUME_DISPATCHED',flush=True)
if __name__=='__main__':main()
