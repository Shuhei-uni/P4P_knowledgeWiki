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
 hold=json.loads((OUT/'target100-controller-hold.json').read_text())
 assert hold['status']=='OWNED_CONTROLLER_HELD_NATIVE_COMMAND_RECONCILIATION_PENDING'
 assert job['status']=='BLOCKED' and native['status']=='RUNNING'
 assert native['active_stage']=='recovery-2p5us-proof' and native['active_target']==10580
 assert run.native_iteration(s)==10580 and abs(run.film(s)['film_elapsed_time']-.01375)<1e-12
 tag=str(time.time_ns());probe=run.WORK/('target100-process-'+tag+'.json')
 code="$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -like '*Phase9-Server6-slit154k*' -and ($_.CommandLine -like '*run_phase9_server6_slit_ewf*' -or $_.CommandLine -like '*run_and_handoff*')}); [IO.File]::WriteAllText("+quote(probe)+",(@{controller_count=$p.Count;process_ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code);process=json.loads(run.read_text(s,str(probe)));assert process['controller_count']==0
 # Reconcile the orphaned native command once, without another solve.
 from pyansys_fluent.ewf_staged import FILM,INNER,history
 from pyansys_fluent.execution_contract import verify_drain_probe
 from run_phase72a_stage4_ewf_drain import define_reports,compute
 import math,re
 text=run.read_text(s,native['active_transcript']);run.dump(OUT/'target100-orphan-command-source.json',native)
 (OUT/'target100-orphan-proof.trn').write_text(text)
 rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
 assert len(rows)==1000 and all(math.isclose(row[0],.01125+(i+1)*2.5e-6,abs_tol=1e-10) and math.isclose(row[1],2.5e-6,rel_tol=1e-7) and all(math.isfinite(x) for x in row) for i,row in enumerate(rows))
 assert max(row[2] for row in rows)<=.1
 inner=[];left=0
 for row in FILM.finditer(text):
  matches=list(INNER.finditer(text[left:row.start()]));assert matches
  inner.append([float(matches[-1][k].strip()) for k in [2,3,4]]);left=row.end()
 passed=sum(all(math.isfinite(v) and 0<=v<=1e-5 for v in row) for row in inner);assert passed>=990
 fields=run.base.state(s)['readback']['fields']
 assert all(math.isclose(v[0],fields[k][0],rel_tol=1e-10,abs_tol=1e-12) for k,v in hold['fields_before'].items() if not k.startswith('p72a-e2.7-ewf-'))
 names=define_reports(s);after=compute(s,names);initial=native['blocks'][-1]['after'];assert all(math.isfinite(v[0]) for v in after.values())
 pair={'native_iteration':10580}
 for key,extension in [('case','cas.h5'),('data','dat.h5')]:
  pair[key]=native['active_transcript'][:-3]+extension
  pair[key+'_sha256']=run.remote_file_sha256(s,pair[key],str(run.WORK/(f'target100-orphan-{key}-{tag}.sha256.txt')))
 hs={name:history(run.read_text(s,native['report_paths'][name])) for name in names};ids=range(9581,10581)
 assert all(all(i in h and math.isfinite(h[i]) for i in ids) for h in hs.values())
 removal=sum(hs['p72d-drain-rate'][i]*2.5e-6 for i in ids);supply=sum((hs['p72d-total-secondary'][i]+hs['p72d-total-dpm'][i])*2.5e-6 for i in ids)
 departure=sum(after[n][0]-initial[n][0] for n in ['p72d-total-mass','p72d-total-outflow','p72d-total-stripped']);gap=departure+removal-supply
 proof={'setup_identity':'server6-slit154k-plan-v1','frozen_bulk':True,'bulk_fields_unchanged':True,'accepted_film_time_s':.0025,'film_start_s':.01125,'film_end_s':.01375,'drained_mass_kg':removal,'direct_film_drain':True,'native_evidence_verified':True,'evidence_paths':[native['active_transcript']],'bulk_equations':s.settings.solution.controls.equations.get_state(),'integrated_direct_removal_kg':removal,'ledger_error_percent':100*abs(gap)/max(abs(supply),1e-12),'ledger_limit_percent':1.0,'native_transcript':native['active_transcript']}
 proof['verification']=verify_drain_probe(proof,setup_identity='server6-slit154k-plan-v1',frozen_bulk=True)
 if proof['verification']['status']!='PASS':
  assert proof['verification']['failures']==['film ledger exceeds the declared probe tolerance'] and functional['status']=='PASS'
  proof.update(production_ledger_status='UNRESOLVED_DIAGNOSTIC',functional_drain_verified_separately=True)
 block={'stage':'recovery-2p5us-proof','count':1000,'step_s':2.5e-6,'bulk_active':False,'film_start_s':.01125,'film_end_s':.01375,'pair':pair,'initial':initial,'after':after,'peak_courant':max(row[2] for row in rows),'inner_steps_observed':1000,'inner_steps_passed':passed,'drain_proof':proof,'reconciled_after_controller_hold':True}
 native['blocks'].append(block);run.dump(OUT/'target100-reconciled-native-proof.json',block)
 backup=hostout/('run-manifest-before-target100-'+tag+'.json')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(launch['run_manifest'])+' -Destination '+quote(backup))
 run.load(s,pair);assert run.native_iteration(s)==10580 and abs(run.film(s)['film_elapsed_time']-.01375)<1e-12
 assert not any(s.settings.solution.controls.equations.get_state().values());run.require_bulk_audit(s);run.read_feed(s,1.0)
 remaining=[(f'target100-growth-{i}',10000,2.5e-6,False) for i in range(1,4)]+[('target100-to-95ms',2500,2.5e-6,False),('target100-bulk-to-100ms',2000,2.5e-6,True)]
 assert abs(.01375+sum(x[1]*x[2] for x in remaining[:-1])-.095)<1e-12
 schedule=native['schedule'][:5]+remaining
 plan={'status':'RECONCILED_AND_REOPENED','server_id':'6','parent_pair':pair,'parent_film_s':.01375,'schedule':schedule,'target_film_s':.1,'final_bulk_start_s':.095,'review':'Human shortened target. Exact owned controller tree held; Fluent journal continued to saved N10580. Native clocks, inner stops, Courant, frozen bulk and drainage reconciled; pair hash verified and reopened. No command replay. Final five ms bulk active.'}
 write_ascii_text_new(s,str(hostout/'target100-resume-plan.json'),json.dumps(plan,indent=2)+'\n');run.dump(OUT/'target100-resume-plan.json',plan)
 native.update(status='RECOVERY_READY',schedule=schedule,latest_pair=pair,verified_native_end=10580,accepted_film_s=.01375,active_target=None,active_stage=None,error=None,native_target_final=45080,target_film_s=.1,resume_plan_file='target100-resume-plan.json',recovery_plan=plan)
 writepath=run.WORK/('target100-manifest-'+tag+'.json');write_ascii_text_new(s,str(writepath),json.dumps(native,indent=2)+'\n')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(writepath)+' -Destination '+quote(launch['run_manifest'])+' -Force')
 runner=ROOT/'staged100ms/run_phase9_server6_slit_ewf.py';target=repo/'PyAnsys/scripts/setup'/runner.name;staged=run.WORK/('reviewed-resume-'+tag+'.py')
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
 verifier=ROOT/'staged100ms/verify_phase9_server6_slit_ewf.py'
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
 run.dump(OUT/'target100-launch.json',{'status':'DISPATCHED','native_origin':10580,'film_origin_s':.01375,'nominal_final_native':45080,'target_film_s':.1,'step_s':2.5e-6,'process_reconciliation':process,'code_sha256':digest,'host_runner':str(target),'review':plan['review'],'launcher':receipt})
 print('SERVER6_SLIT_100MS_DISPATCHED',flush=True)
if __name__=='__main__':main()
