"""Apply the explicit Plan v1 settings to Server 3 / 342k without solving."""
from pathlib import Path, PureWindowsPath
import sys, json, time, math, fcntl
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_mesh_startup as run
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.ewf_staged import refresh_plan
from run_phase72a_stage4_ewf_drain import facets, same_facets

tag=str(time.time_ns());out=run.OUT
evidence=out/('ewf-settings-'+tag);evidence.mkdir()
lock=(out/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
parent=json.loads((out/'342k-run.json').read_text())['final_pair']
s=run.attach();run.require_idle(s)
run.load(s,parent)
assert run.native_iteration(s)==parent['native_iteration']==8580
run.assert_bulk_active(s);run.require_bulk_audit(s);run.read_feed(s,1.0)
before=run.base.state(s);clock=run.film(s)['film_elapsed_time']
known=json.loads(Path(json.loads((out/'342k-run.json').read_text())['blocks'][-1]['checkpoint_proof']).read_text())['after']
run.require_match(before['readback'],known['readback'])
assert before['methods']==known['methods']
run.require_setup_same(before['setup'],known['setup'])
upper=facets(s,'wall')
run.dump(evidence/'before.json',{'state':before,'film':run.film(s),'parent':parent})
print('SERVER3_342K_IDLE_PARENT_VERIFIED',flush=True)
for key in ['case','data']:assert run.remote_file_exists(s,parent[key])
lower=s.settings.setup.boundary_conditions.wall[drain.WALL].phase['mixture'].wall_film
assert not lower.eulerian_film_wall()
lower.eulerian_film_wall=True;lower.film_condition_type='film-wall-initial'
lower.film_height.set_state({'option':'value','value':0.0})
lower.enable_film_source_terms=False;lower.enable_flow_momentum_coupling=False
# Allocate the newly enabled wall, then restore every original production field.
# This performs no bulk initialization and no iteration.
s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
s.settings.file.read_data(file_name=parent['data'])
same_facets(upper,facets(s,'wall'))
assert run.native_iteration(s)==8580
assert math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12)
assert max(abs(x) for x in facets(s,drain.WALL)['film-mass'])<1e-12
print('LOWER_STORAGE_ALLOCATED_ORIGINAL_FIELDS_RESTORED',flush=True)
for name in ['wall',drain.WALL]:
    wall=s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film
    wall.enable_flow_momentum_coupling=False
    wall.enable_dpm_wall_splash=True
    wall.allow_film_boundary_separation=True
changes={'film-coupled-solution?':False,'time-scheme':2,'implicit-scheme-new?':False,
         'mass-scheme':0,'mom-scheme':0,'sub-iter-nums':100,'sub-iter-stop':1e-5,
         'film-smoothing?':True,'film-smooth-level':2,'film-smooth-factor':0.5,
         'ewf-adaptive?':False,**refresh_plan(1e-7)}
changes['surface-tension']=0.04041
p=dict(s.rp_vars('wall-film/model-parameters'))
s.rp_vars('wall-film/model-parameters',[(k,changes.get(k,v)) for k,v in p.items()])
actual=dict(s.rp_vars('wall-film/model-parameters'));assert all(actual[k]==v for k,v in changes.items())
drain_config=drain.configure(s,enabled=True,refresh_span_s=1e-7)
run.assert_bulk_active(s);run.require_bulk_audit(s);run.read_feed(s,1.0)
same_facets(upper,facets(s,'wall'))
configured=run.base.state(s)
run.require_match({'fields':configured['readback']['fields']},{'fields':before['readback']['fields']})
assert configured['methods']==before['methods']
folder=run.WORK/'342k'
pair=run.save(s,folder,'ewf-N8580-'+tag)
run.dump(evidence/'prepared.json',{'status':'SAVED_REOPEN_PENDING','pair':pair,'changes':changes,'drain':drain_config})
print('EWF_CHILD_SAVED_HASHED',flush=True)
run.load(s,pair)
after=run.base.state(s)
run.require_match(after['readback'],configured['readback'])
run.require_setup_same(after['setup'],configured['setup'])
assert after['methods']==configured['methods']
same_facets(upper,facets(s,'wall'))
assert run.native_iteration(s)==8580 and math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12)
run.assert_bulk_active(s);run.require_bulk_audit(s)
drain.audit(s,True)
assert all(dict(s.rp_vars('wall-film/model-parameters'))[k]==v for k,v in changes.items())
receipt={'status':'SETTINGS_APPLIED_REOPEN_VERIFIED',
         'server_id':'3','mesh':'342k','parent':parent,'pair':pair,'changes':changes,'drain':drain_config,
         'before':before,'after':after,'film':run.film(s),'native_iteration':8580,'no_solve_submitted':True,
         'original_main_film_facets_preserved':True,'all_bulk_equations_active':True,
         'pending_setting':None,
         'review':'Server3-only attach; exclusive lock; idle N8580 parent match; allocate lower storage and restore original data; exact main-film facets; settings/readback; local save/hash/reopen. No solve or bulk initialization.',
         'future_steps':{'bulk_active_adjustment':1500,'frozen_transition':1000,'check_2p5us':1000,'check_5us':1000,'growth_at_5us':37310,'final_bulk_active_at_5us':1000}}
run.dump(evidence/'settings-receipt.json',receipt);run.dump(out/'342k-ewf-settings-current.json',receipt)
print('SETTINGS_CHILD_REOPEN_VERIFIED',receipt['status'],str(pair['case']),flush=True)
