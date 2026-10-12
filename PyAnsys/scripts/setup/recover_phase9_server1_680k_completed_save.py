"""Recover only the completed N12580→13580 block; never repeat its solve."""
import json,math,re,time
from pathlib import PureWindowsPath
from phase9_server1_680k_common import attach,run,OUT
from pyansys_fluent.ewf_staged import FILM,history
from pyansys_fluent.execution_contract import verify_drain_probe
from run_phase72a_stage4_ewf_drain import compute
from deploy_phase9_server1_680k_ewf import quote
from pyansys_fluent.stage4_native import exclusive_writer_lock

def main():
 s=attach();run.require_idle(s);tag=str(time.time_ns())
 launch=json.loads((OUT/'resume-host-launch.json').read_text());hostout=PureWindowsPath(launch['host_output']);mp=str(hostout/'run-manifest.json')
 m=json.loads(run.read_text(s,mp))
 assert m['status']=='RECOVERY_REQUIRED' and m['verified_native_end']==12580 and m['active_target']==13580 and len(m['blocks'])==3
 assert run.native_iteration(s)==13580
 assert not any(s.settings.solution.controls.equations.get_state().values())
 transcript=run.read_text(s,m['active_transcript']);rows=[tuple(map(float,x.groups())) for x in FILM.finditer(transcript)]
 assert len(rows)==1000 and all(math.isclose(x[0],.0035+(i+1)*5e-6,abs_tol=1e-10) and math.isclose(x[1],5e-6,rel_tol=1e-7) for i,x in enumerate(rows))
 assert not re.search(r'floating point exception|fatal error|received signal|Divergence detected',transcript,re.I)
 # Preserve the full native endpoint before any continuation or file replacement.
 folder=run.WORK/'680k/ewf-200ms';stem='recovered-step-5us-N13580-'+tag
 pair={'case':str(folder/(stem+'.cas.h5')),'data':str(folder/(stem+'.dat.h5')),'native_iteration':13580}
 s.settings.file.write_case_data(file_name=pair['case'])
 for k in ['case','data']:pair[k+'_sha256']=run.remote_file_sha256(s,pair[k],str(folder/'scratch'/('recovered-'+k+'-'+tag+'.sha256.txt')))
 assert math.isclose(run.film(s)['film_elapsed_time'],.0085,abs_tol=1e-12)
 names=list(m['blocks'][-1]['after']);initial=m['blocks'][-1]['after'];after=compute(s,names)
 hs={}
 selected=set(names)
 prepared=json.loads((OUT/'680k-ewf-settings-current.json').read_text())
 bulk_names=[n for n in prepared['after']['readback']['fields'] if not n.startswith('p72a-e2.7-ewf-')]
 monitored_bulk=[n for n in bulk_names if n in m['report_paths']]
 missing_bulk=[n for n in bulk_names if n not in m['report_paths']]
 missing_live=run.base.state(s)['readback']['fields'] if missing_bulk else {}
 if missing_bulk:
  # Both endpoints remain preserved; compare unmonitored bulk report fields
  # from paired native data instead of inventing a missing history.
  s.settings.file.read_data(file_name=m['latest_pair']['data'])
  missing_baseline=run.base.state(s)['readback']['fields']
  s.settings.file.read_data(file_name=pair['data'])
  assert run.native_iteration(s)==13580 and math.isclose(run.film(s)['film_elapsed_time'],.0085,abs_tol=1e-12)
  assert all(math.isclose(missing_live[n][0],missing_baseline[n][0],rel_tol=1e-10,abs_tol=1e-12) for n in missing_bulk)
 selected.update(monitored_bulk)
 for n in selected:
  text=run.read_text(s,m['report_paths'][n]);hs[n]=history(text)
  (OUT/('recovery-'+n+'.out')).write_text(text)
 assert all(12580 in hs[n] and 13580 in hs[n] and math.isclose(hs[n][12580],hs[n][13580],rel_tol=1e-10,abs_tol=1e-12) for n in monitored_bulk)
 ids=range(12581,13581);assert all(all(i in hs[n] and math.isfinite(hs[n][i]) for i in ids) for n in names)
 removal=sum(hs['p72d-drain-rate'][i]*5e-6 for i in ids)
 supply=sum((hs['p72d-total-secondary'][i]+hs['p72d-total-dpm'][i])*5e-6 for i in ids)
 departure=sum(after[n][0]-initial[n][0] for n in ['p72d-total-mass','p72d-total-outflow','p72d-total-stripped'])
 gap=departure+removal-supply
 proof={'setup_identity':'server1-680k-plan-v1','frozen_bulk':True,'bulk_fields_unchanged':True,'accepted_film_time_s':.005,'film_start_s':.0035,'film_end_s':.0085,'drained_mass_kg':removal,'direct_film_drain':True,'native_evidence_verified':True,'evidence_paths':[m['active_transcript'],m['report_paths']['p72d-drain-rate']],'bulk_equations':s.settings.solution.controls.equations.get_state(),'integrated_direct_removal_kg':removal,'ledger_error_percent':100*abs(gap)/max(abs(supply),1e-12),'ledger_limit_percent':1.0,'ledger_residual_kg':gap,'gross_ledger_residual_kg':gap+after['p72d-total-separated'][0]-initial['p72d-total-separated'][0],'ledger_basis':'v252-net-secondary-consistency','native_transcript':m['active_transcript']}
 proof['verification']=verify_drain_probe(proof,setup_identity='server1-680k-plan-v1',frozen_bulk=True)
 if proof['verification']['status']!='PASS':
  assert m.get('ledger_diagnostic_only') and proof['verification']['failures']==['film ledger exceeds the declared probe tolerance']
  proof['continuation']='LEDGER_WARNING_AUTHORIZED'
 block={'stage':'step-5us','count':1000,'step_s':5e-6,'bulk_active':False,'film_start_s':.0035,'film_end_s':.0085,'pair':pair,'initial':initial,'after':after,'peak_courant':max(x[2] for x in rows),'drain_proof':proof,'recovery':'Save skipped after an invalid read-only status probe raised a native error; solve completed exactly once.'}
 assert block['peak_courant']<=.1 and all(math.isfinite(v[0]) for v in after.values())
 archive=mp+'.before-save-recovery-'+tag
 assert run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(mp)+' -Destination '+quote(archive)) in (0,None)
 m['blocks'].append(block);m.update(status='RECOVERY_REQUIRED',verified_native_end=13580,accepted_film_s=.0085,latest_pair=pair,active_target=None,active_stage=None,recovery_ready=True)
 m.pop('error',None);m['recovery_reason']='Completed N13580 endpoint preserved; ready for growth-5000; faulty status probe removed.'
 # Atomic host manifest replacement by bytes; retain all original host paths.
 import base64
 staged=str(folder/('recovered-manifest-'+tag+'.b64'));run.write_ascii_text_new(s,staged,base64.b64encode((json.dumps(m,indent=2)+'\n').encode()).decode())
 assert run.base.powershell(s,"$ErrorActionPreference='Stop'; [IO.File]::WriteAllBytes("+quote(mp)+",[Convert]::FromBase64String([IO.File]::ReadAllText("+quote(staged)+")))") in (0,None)
 run.dump(OUT/'host-run-manifest.json',m);run.dump(OUT/'completed-save-recovery.json',{'status':'RECOVERED_N13580_READY','pair':pair,'drain_proof':proof,'peak_courant':block['peak_courant'],'no_solve_replayed':True,'native_probe_error_removed':True})
 print('RECOVERED_N13580_READY',proof['ledger_error_percent'],flush=True)

if __name__=='__main__':main()
