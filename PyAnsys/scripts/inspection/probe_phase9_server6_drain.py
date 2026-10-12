"""Matched frozen OFF/ON probe; restore the preserved N10580 production pair."""
import json,math,time
from phase9_server6_997k_common import attach,run,OUT
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.ewf_staged import history
from run_phase72a_stage4_ewf_drain import define_reports,compute

def main():
 m=json.loads((OUT/'host-run-manifest.json').read_text());pair=m['latest_pair']
 s=attach();run.require_idle(s)
 assert run.native_iteration(s)==10580 and pair['native_iteration']==10580
 stamp=str(time.time_ns());folder=run.WORK/'997k'/('drain-probe-'+stamp)
 run.ensure_remote_directory(s,str(folder));names=define_reports(s);arms={}
 try:
  for enabled in [False,True]:
   run.load(s,pair);run.require_idle(s)
   assert not any(s.settings.solution.controls.equations.get_state().values())
   p=dict(s.rp_vars('wall-film/model-parameters'))
   delta={'secondary-phase-mode':0,'dpm-collection?':False,'dpm-splashing?':False,'film-stripping?':False,'film-separation?':False}
   s.rp_vars('wall-film/model-parameters',[(k,delta.get(k,v)) for k,v in p.items()]);drain.set_enabled(s,enabled);drain.audit(s,enabled)
   paths={};files=s.settings.solution.monitor.report_files
   for name in names:
    files[name].file_name=str(folder/(('on-' if enabled else 'off-')+name+'.out'));paths[name]=files[name].file_name()
   initial=compute(s,names);label='on' if enabled else 'off';trn=str(folder/(label+'.trn'))
   s.tui.file.start_transcript(trn);s.tui.solve.iterate(100);s.tui.file.stop_transcript()
   assert run.native_iteration(s)==10680
   after=compute(s,names);hs={n:history(run.read_text(s,paths[n])) for n in ['p72d-drain-rate']}
   removal=sum(hs['p72d-drain-rate'][i]*1e-7 for i in range(10581,10681))
   arms[label]={'initial':initial,'after':after,'integrated_drain_kg':removal,'transcript':trn,'history':paths['p72d-drain-rate']}
   print(label,json.dumps(arms[label]),flush=True)
 finally:
  run.load(s,pair);drain.audit(s,True)
  assert run.native_iteration(s)==10580 and math.isclose(run.film(s)['film_elapsed_time'],.0009,abs_tol=1e-12)
 def change(arm):return sum(arms[arm]['after'][n][0]-arms[arm]['initial'][n][0] for n in ['p72d-total-mass','p72d-total-outflow'])
 removed=change('off')-change('on');integrated=arms['on']['integrated_drain_kg'];error=100*abs(removed-integrated)/max(integrated,1e-20)
 result={'status':'PASS' if integrated>0 and error<=1 else 'UNVERIFIED','server_id':'6','production_restored_iteration':10580,'probe_updates_each':100,'probe_step_s':1e-7,'arms':arms,'matched_removed_kg':removed,'integrated_removal_kg':integrated,'ledger_error_percent':error,'interpretation':'Differential direct-sink probe only; production source ledger remains unresolved.'}
 run.dump(OUT/'matched-drain-probe.json',result);print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
