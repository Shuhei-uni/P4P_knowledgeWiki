"""Deploy the reviewed resume path to idle Server 6 and relaunch its terminal job."""
import hashlib,json,time
from pathlib import Path,PureWindowsPath
from phase9_server6_slit_common import attach,run,OUT,ROOT
from deploy_phase9_server6_slit_ewf import quote
from run_phase9_server6_slit_ewf import lane_file_sha256,lane_read_text
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.remote_text import write_ascii_text_new

def main():
 import math,re
 from pyansys_fluent.ewf_staged import FILM,INNER,history
 from pyansys_fluent.execution_contract import verify_drain_probe
 from run_phase72a_stage4_ewf_drain import define_reports,compute
 # This preflight is the only retryable branch. No settings, files or solve sent while busy.
 s=attach();run.require_idle(s)
 if s.settings.solution.run_calculation.iterating():raise RuntimeError('Server6 busy; no mutation submitted')
 functional=json.loads((OUT/'matched-drain-probe.json').read_text());assert functional['status']=='PASS'
 launch=json.loads((OUT/'host-launch.json').read_text());repo=PureWindowsPath(launch['host_repo']);hostout=PureWindowsPath(launch['host_output'])
 native=json.loads(run.read_text(s,launch['run_manifest']));job=json.loads(run.read_text(s,str(hostout/'job-manifest.json')))
 hold=json.loads((OUT/'continue100-controller-hold.json').read_text())
 assert hold['status']=='OWNED_CONTROLLER_HELD_NATIVE_COMMAND_RECONCILIATION_PENDING'
 assert job['status']=='BLOCKED' and native['status']=='RUNNING'
 assert native['active_journal']==hold['manifest']['active_journal']
 end=native['active_target'];start=native['verified_native_end'];count=end-start;dt=native['active_step_s'];clock0=native['accepted_film_s']
 assert count==10000 and dt==1e-6 and native['bulk_active'] is False
 if run.native_iteration(s)<end:raise RuntimeError('Server6 busy; no mutation submitted')
 assert run.native_iteration(s)==end
 for extension in ['cas.h5','dat.h5']:
  if not run.remote_file_exists(s,native['active_transcript'][:-3]+extension):raise RuntimeError('Server6 busy; no mutation submitted')
 tag=str(time.time_ns());probe=run.WORK/('human1us-process-'+tag+'.json')
 code="$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -like '*Phase9-Server6-slit154k*' -and ($_.CommandLine -like '*run_phase9_server6_slit_ewf*' -or $_.CommandLine -like '*run_and_handoff*')}); [IO.File]::WriteAllText("+quote(probe)+",(@{controller_count=$p.Count;process_ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);process=json.loads(run.read_text(s,str(probe)));assert process['controller_count']==0
 text=lane_read_text(s,native['active_transcript']);(OUT/'human-1us-orphan-proof.trn').write_text(text)
 rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
 assert len(rows)==count and all(math.isclose(row[0],clock0+(i+1)*dt,abs_tol=1e-10) and math.isclose(row[1],dt,rel_tol=1e-7) and all(math.isfinite(x) for x in row) for i,row in enumerate(rows))
 assert not re.search(r'floating point exception|fatal error|received signal|Divergence detected',text,re.I)
 peak=max(row[2] for row in rows)
 clock=rows[-1][0];assert abs(run.film(s)['film_elapsed_time']-clock)<1e-10
 inner=[];left=0
 for row in FILM.finditer(text):
  matches=list(INNER.finditer(text[left:row.start()]))
  if matches:inner.append([float(matches[-1][k].strip()) for k in [2,3,4]])
  left=row.end()
 passed=sum(all(math.isfinite(v) and 0<=v<=1e-5 for v in r) for r in inner)
 fields=run.base.state(s)['readback']['fields']
 assert all(math.isclose(v[0],fields[k][0],rel_tol=1e-10,abs_tol=1e-12) for k,v in hold['fields_before'].items() if not k.startswith('p72a-e2.7-ewf-'))
 names=define_reports(s);after=compute(s,names);initial={};assert all(math.isfinite(v[0]) for v in after.values())
 pair={'native_iteration':end}
 for key,extension in [('case','cas.h5'),('data','dat.h5')]:
  pair[key]=native['active_transcript'][:-3]+extension
  pair[key+'_sha256']=lane_file_sha256(s,pair[key],str(run.WORK/(f'human1us-orphan-{key}-{tag}.sha256.txt')))
 # Resolve Fluent's live suffixed report paths; never read superseded failed-attempt files.
 paths={}
 for obj in s.settings.solution.monitor.report_files.get_state().values():
  if len(obj['report_defs'])!=1 or obj['report_defs'][0] not in names:continue
  assert obj['active'] and obj['frequency_of']=='iteration' and obj['frequency']==1
  p=PureWindowsPath(obj['file_name']);paths[obj['report_defs'][0]]=str(p if p.is_absolute() else run.WORK/p)
 assert set(paths)==set(names)
 proof={'production_ledger_status':'DIAGNOSTIC_NOT_RECONSTRUCTED_AT_CONTROLLER_HANDOFF','raw_evidence_paths':[native['active_transcript']]+list(paths.values()),'bulk_fields_unchanged':True}
 block={'stage':native['active_stage'],'count':count,'step_s':dt,'bulk_active':False,'film_start_s':clock0,'film_end_s':clock,'pair':pair,'initial':initial,'after':after,'peak_courant':peak,'courant_ceiling':.8,'numerical_acceptance_policy':'diagnostics_only','courant_exceeded_diagnostic':peak>.8,'inner_convergence_status':'DIAGNOSTIC_ONLY','inner_steps_observed':len(inner),'inner_steps_passed':passed,'drain_proof':proof,'report_paths':paths,'reconciled_after_controller_hold':True}
 native['blocks'].append(block);run.dump(OUT/'continue100-reconciled-native-proof.json',block)
 backup=hostout/('run-manifest-before-human1us-'+tag+'.json')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(launch['run_manifest'])+' -Destination '+quote(backup))
 run.load(s,pair);assert run.native_iteration(s)==end and abs(run.film(s)['film_elapsed_time']-clock)<1e-10
 assert not any(s.settings.solution.controls.equations.get_state().values());run.require_bulk_audit(s);run.read_feed(s,1.0)
 frozen=round((.095-clock)/1e-6);assert abs(clock+frozen*1e-6-.095)<1e-10 and frozen>=1000
 remaining=[];left=frozen;i=1
 while left:
  n=min(10000,left)
  if 0<left-n<1000:n-=1000-(left-n)
  assert n>=1000
  remaining.append((f'continue100-1us-growth-{i}',n,1e-6,False));left-=n;i+=1
 remaining.append(('continue100-1us-bulk-95-to-100ms',5000,1e-6,True))
 accepted=native['schedule'][:len(native['blocks'])];assert [x[0] for x in accepted]==[b['stage'] for b in native['blocks']]
 schedule=accepted+remaining;final_native=end+sum(x[1] for x in remaining)
 assert abs(clock+sum(x[1]*x[2] for x in remaining)-.1)<1e-10
 plan={'status':'RECONCILED_AND_REOPENED','server_id':'6','parent_pair':pair,'parent_film_s':clock,'schedule':schedule,'target_film_s':.1,'final_bulk_start_s':.095,'step_s':1e-6,'courant_ceiling':.8,'native_target_final':final_native,'review':'Human: no keep running to100ms. Hold only exactownedPythonrunner, preserve currentnative10000-update command withoutinterrupt/replay; reconcilecompleted80580/27.35ms pair, clocks andfinite state. Inner/Courant/ledger recordedasdiagnostics only, threshold0.8 recordedbutdoesnotstoporrollback. Preserve current1us andremainingcounts fromcompletednativefilmclock, final95-100msbulkactive. Pairedhashes verified,reopen before resume; hostcontroller code/hash/import verified. Nootherlanechanges orFluentexit.'}
 write_ascii_text_new(s,str(hostout/'continue100-resume-plan.json'),json.dumps(plan,indent=2)+'\n');run.dump(OUT/'continue100-resume-plan.json',plan)
 native.update(numerical_acceptance_policy='diagnostics_only',status='RECOVERY_READY',schedule=schedule,latest_pair=pair,verified_native_end=end,accepted_film_s=clock,active_target=None,active_stage=None,error=None,native_target_final=final_native,target_film_s=.1,courant_ceiling=.8,resume_plan_file='continue100-resume-plan.json',recovery_plan=plan)
 writepath=run.WORK/('human1us-manifest-'+tag+'.json');write_ascii_text_new(s,str(writepath),json.dumps(native,indent=2)+'\n')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(writepath)+' -Destination '+quote(launch['run_manifest'])+' -Force')
 runner=ROOT/'stagedcontinue100/run_phase9_server6_slit_ewf.py';target=repo/'PyAnsys/scripts/setup'/runner.name;staged=run.WORK/('reviewed-resume-'+tag+'.py')
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
 verifier=ROOT/'stagedcontinue100/verify_phase9_server6_slit_ewf.py'
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
 run.dump(OUT/'continue100-launch.json',{'status':'DISPATCHED','native_origin':end,'film_origin_s':clock,'nominal_final_native':final_native,'target_film_s':.1,'step_s':1e-6,'courant_ceiling':.8,'process_reconciliation':process,'code_sha256':digest,'host_runner':str(target),'review':plan['review'],'launcher':receipt})
 print('SERVER6_SLIT_100MS_DISPATCHED',flush=True)
if __name__=='__main__':main()
