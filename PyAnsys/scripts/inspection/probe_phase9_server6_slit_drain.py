"""Matched seeded-film OFF/ON drain proof; restore production N5080 afterwards."""
import json,math,time,faulthandler
from phase9_server6_slit_common import attach,run,OUT
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.ewf_staged import FILM,history
from pyansys_fluent.stage4_native import exclusive_writer_lock
from run_phase72a_stage4_ewf_drain import define_reports,compute,facets,same_facets,instrument

def main():
 faulthandler.dump_traceback_later(90,repeat=True)
 with exclusive_writer_lock(OUT/'controller.lock'):
  prepared=json.loads((OUT/'slit154k-ewf-settings-current.json').read_text());pair=prepared['pair']
  s=attach();run.require_idle(s);assert run.native_iteration(s)==5080
  print('PROBE_ATTACHED_N5080',flush=True)
  original=run.base.state(s);upper=facets(s,'wall');clock=run.film(s)['film_elapsed_time']
  stamp=str(time.time_ns());folder=run.WORK/'slit154k'/('drain-proof-'+stamp)
  run.ensure_remote_directory(s,str(folder/'scratch'));arms={}
  try:
   define_reports(s)
   print('PROBE_REPORTS_DEFINED',flush=True)
   names=['p72d-total-mass','p72d-total-outflow','p72d-lower-mass','p72d-drain-rate','p72d-lower-inventory','p72d-total-courant']
   eq=s.settings.solution.controls.equations.get_state();s.settings.solution.controls.equations.set_state({k:False for k in eq})
   params=dict(s.rp_vars('wall-film/model-parameters'))
   delta={'secondary-phase-mode':0,'dpm-collection?':False,'dpm-splashing?':False,'film-stripping?':False,'film-separation?':False}
   s.rp_vars('wall-film/model-parameters',[(k,delta.get(k,v)) for k,v in params.items()])
   s.settings.setup.boundary_conditions.wall[drain.WALL].phase['mixture'].wall_film.film_height.set_state({'option':'value','value':1e-6})
   s.tui.define.models.eulerian_wallfilm.solution_options()
   # Isolated proof only: seed native lower film; no bulk initialization.
   s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
   print('PROBE_SEED_SAVE_BEGIN',flush=True)
   seeded=run.save(s,folder,'matched-seeded-film-N5080')
   print('PROBE_SEED_SAVE_VERIFIED',flush=True)
   for enabled in [False,True]:
    run.load(s,seeded);drain.set_enabled(s,enabled);drain.audit(s,enabled)
    label='on' if enabled else 'off'
    print('PROBE_ARM_ACTIVATION',label,flush=True)
    arm=run.save(s,folder,label+'-controls');run.load(s,arm)
    assert not any(s.settings.solution.controls.equations.get_state().values())
    start=run.native_iteration(s);t0=run.film(s)['film_elapsed_time'];bulk=run.base.state(s)['readback']['fields']
    paths=instrument(s,folder/(label+'-monitors'),names=names);initial=compute(s,names)
    trn=str(folder/(label+'.trn'));s.tui.file.start_transcript(trn)
    print('PROBE_ARM_SOLVE',label,start,start+100,flush=True)
    try:s.tui.solve.iterate(100)
    finally:s.tui.file.stop_transcript()
    text=run.read_text(s,trn);(OUT/('drain-proof-'+label+'-'+stamp+'.trn')).write_text(text)
    rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
    assert len(rows)==100 and run.native_iteration(s)==start+100
    assert all(math.isclose(row[1],1e-7,rel_tol=1e-7) for row in rows)
    assert math.isclose(rows[-1][0]-t0,1e-5,abs_tol=1e-10)
    after=compute(s,names);bulk_after=run.base.state(s)['readback']['fields']
    persistent={k:v for k,v in bulk.items() if not k.startswith('p72a-e2.7-ewf-')}
    run.require_match({'fields':{k:bulk_after[k] for k in persistent}},{'fields':persistent})
    h=history(run.read_text(s,paths['p72d-drain-rate']))
    removal=sum(h[i]*1e-7 for i in range(start+1,start+101))
    arms[label]={'initial':initial,'after':after,'integrated_drain_kg':removal,'film_start_s':t0,'film_end_s':rows[-1][0],
                 'bulk_fields_unchanged':True,'peak_courant':max(row[2] for row in rows),'transcript':trn,'history':paths['p72d-drain-rate']}
    run.dump(OUT/('drain-proof-arms-'+stamp+'.json'),arms)
  finally:
   print('PROBE_RESTORE_PRODUCTION_BEGIN',flush=True)
   run.load(s,pair)
   restored=run.base.state(s);run.require_match(restored['readback'],original['readback']);run.require_setup_same(restored['setup'],original['setup'])
   same_facets(upper,facets(s,'wall'))
   assert run.native_iteration(s)==5080 and math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12)
   run.assert_bulk_active(s);drain.audit(s,True)
   print('PROBE_PRODUCTION_RESTORED_N5080',flush=True)
  def change(arm):return sum(arms[arm]['after'][n][0]-arms[arm]['initial'][n][0] for n in ['p72d-total-mass','p72d-total-outflow'])
  removed=change('off')-change('on');integrated=arms['on']['integrated_drain_kg'];error=100*abs(removed-integrated)/max(integrated,1e-20)
  result={'status':'PASS' if integrated>0 and error<=1 else 'UNVERIFIED','setup_identity':'server6-slit154k-plan-v1',
          'server_id':'6','production_restored_iteration':5080,'production_restored_film_s':clock,'arms':arms,
          'matched_removed_kg':removed,'integrated_removal_kg':integrated,'ledger_error_percent':error,
          'frozen_bulk':True,'bulk_fields_unchanged':True,'direct_film_drain':True,'native_evidence_verified':True,
          'probe_updates_each':100,'seeded_lower_height_m':1e-6,'ledger_limit_percent':1,
          'interpretation':'Seeded functional removal on the actual lower film wall. Excludes probe time from production. Does not prove full production closure or incoming drainage to this wall.'}
  run.dump(OUT/'matched-drain-probe.json',result);print(json.dumps(result,indent=2),flush=True)
  if result['status']!='PASS':raise RuntimeError('Functional direct drain proof needs repair')
if __name__=='__main__':main()
