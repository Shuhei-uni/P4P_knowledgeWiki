"""Recoverable-child proof of the v252 native EWF solution-options callback.

Execute only after reconciling the previous host controller and native command.
Preserve any interrupted branch first. Restore the N10580 production pair.
"""
import sys,json,time,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'scripts/setup'),str(ROOT/'src')]
from phase9_server6_997k_common import attach,run,OUT
from pyansys_fluent.ewf_staged import refresh_plan,FILM
from pyansys_fluent import ewf_local_drain as drain

def main():
 launch=json.loads((OUT/'host-launch.json').read_text());s=attach();run.require_idle(s)
 if s.settings.solution.run_calculation.iterating():raise RuntimeError('Native command still active; no mutation')
 job=json.loads(run.read_text(s,launch['host_output']+'\\job-manifest.json'))
 if job['status']!='BLOCKED':raise RuntimeError('Previous host worker not terminal; reconcile first')
 m=json.loads(run.read_text(s,launch['run_manifest']));assert m['verified_native_end']==10580
 tag=str(time.time_ns());folder=run.WORK/'997k'/('native-step-proof-'+tag);run.ensure_remote_directory(s,str(folder))
 current=run.native_iteration(s);preserved=run.save(s,folder,'preserved-before-repair-N'+str(current))
 proof={'status':'PROBE_STARTED','preserved_branch':preserved,'production_pair':m['latest_pair'],'server_id':'6','steps':[],'native_recipe':'RP parameter delta; /define/models/eulerian-wallfilm/solution-options with retained defaults; full parameter equality; local save/reopen; accepted film clocks'}
 run.dump(OUT/('native-step-proof-'+tag+'.json'),proof)
 try:
  run.load(s,m['latest_pair']);assert run.native_iteration(s)==10580
  for dt in [2.5e-6,5e-6]:
   p=dict(s.rp_vars('wall-film/model-parameters'));delta=refresh_plan(dt)
   s.rp_vars('wall-film/model-parameters',[(k,delta.get(k,v)) for k,v in p.items()]);expected=dict(s.rp_vars('wall-film/model-parameters'))
   s.tui.define.models.eulerian_wallfilm.solution_options()
   assert dict(s.rp_vars('wall-film/model-parameters'))==expected
   s.settings.setup.named_expressions['P72dRefreshSpan'].definition=f'{dt:.17g}[s]';drain.audit(s,True)
   paths=run.base.instrument(s,folder/('monitors-'+str(dt)))
   pair=run.save(s,folder,'configured-'+str(dt)+'-N'+str(run.native_iteration(s)));run.load(s,pair)
   assert dict(s.rp_vars('wall-film/model-parameters'))==expected;drain.audit(s,True)
   # Reopen retains own fresh report names; one diagnostic native update.
   start=run.native_iteration(s);trn=str(folder/('step-'+str(dt)+'.trn'))
   s.tui.file.start_transcript(trn);s.tui.solve.iterate(1);s.tui.file.stop_transcript()
   text=run.read_text(s,trn);rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
   assert len(rows)==1 and math.isclose(rows[0][1],dt,rel_tol=1e-7) and run.native_iteration(s)==start+1
   proof['steps'].append({'requested_step_s':dt,'accepted':rows[0],'configured_pair':pair,'transcript':trn,'full_parameters_equal':True,'save_reopen_verified':True})
 finally:
  if s.settings.solution.run_calculation.iterating():raise RuntimeError('Unexpected active solve; restore prohibited')
  run.load(s,m['latest_pair']);assert run.native_iteration(s)==10580 and math.isclose(run.film(s)['film_elapsed_time'],.0009,abs_tol=1e-12);drain.audit(s,True)
 proof.update(status='PASS',production_restored_native=10580);run.dump(OUT/'native-step-proof.json',proof);print(json.dumps(proof,indent=2),flush=True)
if __name__=='__main__':main()
