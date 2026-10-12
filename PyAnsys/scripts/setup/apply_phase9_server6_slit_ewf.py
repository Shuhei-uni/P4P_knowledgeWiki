"""Apply Phase 9 controls to the verified 154k N5080 child on Server 6."""
from pathlib import Path
import json,time,math
from phase9_server6_slit_common import run,attach,OUT
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.ewf_staged import refresh_plan
from pyansys_fluent.stage4_native import exclusive_writer_lock
from run_phase72a_stage4_ewf_drain import facets,same_facets

tag=str(time.time_ns());out=OUT
lock_context=exclusive_writer_lock(OUT/'controller.lock');lock=lock_context.__enter__()
evidence=out/('ewf-settings-'+tag);evidence.mkdir()
if (out/'slit154k-ewf-settings-current.json').exists():raise RuntimeError('Reconcile existing child before replay')
record=json.loads((OUT/'parent-loaded.json').read_text());parent=record['parent']
s=attach();run.require_idle(s)
assert not s.settings.solution.run_calculation.iterating()
run.load(s,parent)
assert run.native_iteration(s)==5080
clock=run.film(s)['film_elapsed_time'];assert math.isclose(clock,.0035,abs_tol=1e-12)
before=run.base.state(s)
run.require_match(before['readback'],record['state']['readback'])
assert before['methods']==record['state']['methods']
run.read_feed(s,1.0)
# Explicitly selected Phase 9 bulk surface-tension and interaction flags.
run.apply_approved_bulk(s)
# v252 domains is a stored snapshot; native save/reopen refreshes its readback.
bulk_pair=run.save(s,run.WORK/'slit154k','bulk-corrected-N5080-'+tag)
run.load(s,bulk_pair);run.require_bulk_audit(s)
eq=s.settings.solution.controls.equations.get_state()
s.settings.solution.controls.equations.set_state({k:True for k in eq});run.assert_bulk_active(s)
roughness={}
for name in s.settings.setup.boundary_conditions.wall.get_object_names():
    t=s.settings.setup.boundary_conditions.wall[name].phase['mixture'].turbulence
    t.roughness_height=0.0 if name=='bottom' else 4.5e-5
    t.roughness_const=.5
    roughness[name]=t.get_state()
    assert math.isclose(roughness[name]['roughness_height']['value'],0.0 if name=='bottom' else 4.5e-5,abs_tol=1e-12)
upper=facets(s,'wall')
run.dump(evidence/'before.json',{'state':before,'film':run.film(s),'parent':parent})
print('SERVER6_SLIT154K_IDLE_PARENT_VERIFIED',flush=True)
for key in ['case','data']:assert run.remote_file_exists(s,parent[key])
lower=s.settings.setup.boundary_conditions.wall[drain.WALL].phase['mixture'].wall_film
assert not lower.eulerian_film_wall()
lower.eulerian_film_wall=True;lower.film_condition_type='film-wall-initial'
lower.film_height.set_state({'option':'value','value':0.0})
lower.enable_film_source_terms=False;lower.enable_flow_momentum_coupling=False
upper_wall=s.settings.setup.boundary_conditions.wall['wall'].phase['mixture'].wall_film
upper_wall.film_condition_type='film-wall-initial'
upper_wall.film_height.set_state({'option':'value','value':0.0})
# Allocate the newly enabled wall, then restore every original production field.
# This performs no bulk initialization and no iteration.
s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
s.settings.file.read_data(file_name=parent['data'])
same_facets(upper,facets(s,'wall'))
assert run.native_iteration(s)==5080
assert math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12)
assert max(abs(x) for x in facets(s,drain.WALL)['film-mass'])<1e-12
print('LOWER_STORAGE_ALLOCATED_ORIGINAL_FIELDS_RESTORED',flush=True)
changes={'film-coupled-solution?':False,'time-scheme':2,'implicit-scheme-new?':False,
         'mass-scheme':0,'mom-scheme':0,'sub-iter-nums':100,'sub-iter-stop':1e-5,
         'film-smoothing?':True,'film-smooth-level':2,'film-smooth-factor':0.5,
         'ewf-adaptive?':False,**refresh_plan(1e-7)}
changes['surface-tension']=0.04041
p=dict(s.rp_vars('wall-film/model-parameters'))
required={'solve-wallfilm?':True,'solve-momentum?':True,'mom-equation?':True,
 'mom-gravity?':True,'mom-aero-drive?':True,'mom-wall-visc?':True,'mom-advection?':True,'mom-pressure?':True,'mom-spreading?':True,
 'surface-tension?':True,'dpm-collection?':True,'dpm-splashing?':True,
 'film-separation?':True,'film-stripping?':True,'secondary-phase-mode':1}
assert set(required).issubset(p),'Unknown inherited film options'
changes.update(required)
assert set(changes).issubset(p),'Unknown EWF setting'
s.rp_vars('wall-film/model-parameters',[(k,changes.get(k,v)) for k,v in p.items()])
actual=dict(s.rp_vars('wall-film/model-parameters'));assert all(actual[k]==v for k,v in changes.items())
s.tui.define.models.eulerian_wallfilm.model_options(*run.MODEL_ARGS)
# Reapply exact selected values after the global model callback.
s.rp_vars('wall-film/model-parameters',[(k,changes.get(k,v)) for k,v in dict(s.rp_vars('wall-film/model-parameters')).items()])
for name in ['wall',drain.WALL]:
    wall=s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film
    wall.enable_flow_momentum_coupling=False
    wall.enable_dpm_wall_splash=True
    wall.allow_film_boundary_separation=True
drain_config=drain.configure(s,enabled=True,refresh_span_s=1e-7)
run.assert_bulk_active(s);run.require_bulk_audit(s);run.read_feed(s,1.0)
same_facets(upper,facets(s,'wall'))
s.tui.define.models.eulerian_wallfilm.solution_options()
configured=run.base.state(s)
run.require_match({'fields':configured['readback']['fields']},{'fields':before['readback']['fields']})
assert configured['methods']==before['methods']
folder=run.WORK/'slit154k'
pair=run.save(s,folder,'ewf-N5080-'+tag)
run.dump(evidence/'prepared.json',{'status':'SAVED_REOPEN_PENDING','pair':pair,'changes':changes,'drain':drain_config})
print('EWF_CHILD_SAVED_HASHED',flush=True)
run.load(s,pair)
after=run.base.state(s)
run.require_match(after['readback'],configured['readback'])
run.require_setup_same(after['setup'],configured['setup'])
assert after['methods']==configured['methods']
same_facets(upper,facets(s,'wall'))
assert run.native_iteration(s)==5080 and math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12)
run.assert_bulk_active(s);run.require_bulk_audit(s)
drain.audit(s,True)
assert all(dict(s.rp_vars('wall-film/model-parameters'))[k]==v for k,v in changes.items())
receipt={'status':'SETTINGS_APPLIED_REOPEN_VERIFIED',
         'server_id':'6','mesh':'slit154k','parent':parent,'pair':pair,'changes':changes,'drain':drain_config,
         'before':before,'after':after,'film':run.film(s),'native_iteration':5080,'no_solve_submitted':True,
         'original_main_film_facets_preserved':True,'all_bulk_equations_active':True,
         'pending_setting':None,
         'review':'Server6-only attach; exclusive lock; idle N5080 parent match; allocate lower storage and restore original data; exact main-film facets; settings/readback; local save/hash/reopen. No solve or bulk initialization.',
         'roughness':roughness,'cells':154063,'future_steps':{'bulk_active_adjustment':1500,'frozen_transition':1000,'check_2p5us':1000,'check_5us':1000,'growth_at_5us':36750,'final_bulk_active_at_5us':1000}}
run.dump(evidence/'settings-receipt.json',receipt);run.dump(out/'slit154k-ewf-settings-current.json',receipt)
print('SETTINGS_CHILD_REOPEN_VERIFIED',receipt['status'],str(pair['case']),flush=True)
