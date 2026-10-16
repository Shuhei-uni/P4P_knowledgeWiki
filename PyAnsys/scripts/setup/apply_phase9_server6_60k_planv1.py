"""Apply the explicit Plan v1 settings to Server 6 / 60k without solving."""
from pathlib import Path, PureWindowsPath
import sys, json, time, math, fcntl
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from phase9_server6_60k_planv1_common import run,attach,ROOT,OUT
from run_phase9_server6_slit_ewf import lane_save,lane_file_sha256
from deploy_phase9_server6_slit_ewf import quote
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.ewf_staged import refresh_plan
from run_phase72a_stage4_ewf_drain import facets, same_facets

tag=str(time.time_ns());out=OUT
evidence=out/('ewf-settings-'+tag);evidence.mkdir()
lock=(out/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)

s=attach();run.require_idle(s)
if (out/'60k-ewf-settings-current.json').exists():raise RuntimeError('Existing child must be reconciled before setup replay')
# Isolated local work directories and explicit shared input copies.
run.base.powershell(s,"$ErrorActionPreference='Stop'; New-Item -ItemType Directory -Force -Path '"+str(run.WORK/'60k'/'scratch')+"','"+str(run.WORK/'60k'/'monitors')+"' | Out-Null")
if s.settings.setup.boundary_conditions.is_active():
    if s.settings.setup.boundary_conditions.wall.get_object_names():
        s.settings.file.write_case(file_name=str(run.WORK/('preserved-before-load-'+tag+'.cas.h5')))
        s.settings.file.write_data(file_name=str(run.WORK/('preserved-before-load-'+tag+'.dat.h5')))
source=json.loads((ROOT/'output/phase9-server6-60k-5us/20261013/recovery-receipt.json').read_text())['pair']
assert source['native_iteration']==8082
parent={'native_iteration':8082}
for key,ext in [('case','cas.h5'),('data','dat.h5')]:
 target=run.WORK/'60k'/('source-N8082-'+tag+'.'+ext)
 digest=lane_file_sha256(s,source[key],str(run.WORK/'60k/scratch'/('source-'+key+'-'+tag+'.txt')))
 assert digest==source[key+'_sha256']
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(source[key])+' -Destination '+quote(target))
 assert lane_file_sha256(s,str(target),str(run.WORK/'60k/scratch'/('parent-'+key+'-'+tag+'.txt')))==digest
 parent[key]=str(target);parent[key+'_sha256']=digest
library=PureWindowsPath(source['case']).parent/'libcontactv2'
run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(library)+' -Destination '+quote(run.WORK/'libcontactv2')+' -Recurse')
run.load(s,parent)
assert run.native_iteration(s)==parent['native_iteration']==8082
run.assert_bulk_active(s);run.read_feed(s,1.0)
before=run.base.state(s);clock=run.film(s)['film_elapsed_time']
assert math.isclose(clock,.000665,abs_tol=1e-12)
upper=facets(s,'wall')
run.dump(evidence/'before.json',{'state':before,'film':run.film(s),'parent':parent})
print('SERVER6_60K_IDLE_PARENT_VERIFIED',flush=True)
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
assert run.native_iteration(s)==8082
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
required={'solve-wallfilm?':True,'solve-momentum?':True,'mom-equation?':True,
 'mom-gravity?':True,'mom-aero-drive?':True,'mom-wall-visc?':True,'mom-advection?':True,'mom-pressure?':True,'mom-spreading?':True,
 'surface-tension?':True,'dpm-collection?':True,'dpm-splashing?':True,
 'film-separation?':True,'film-stripping?':True,'secondary-phase-mode':1}
assert all(p[k]==v for k,v in required.items()),'Parent inherited model options differ'
changes.update(required)
assert set(changes).issubset(p),'Unknown EWF setting'
s.rp_vars('wall-film/model-parameters',[(k,changes.get(k,v)) for k,v in p.items()])
actual=dict(s.rp_vars('wall-film/model-parameters'));assert all(actual[k]==v for k,v in changes.items())
force=s.tui.define.phases.set_domain_properties.interaction_domain.forces.surface_tension
force.sfc_tension_coeff('yes','constant',0.04041)
force.sfc_modeling('yes')
for name in s.settings.setup.boundary_conditions.wall.get_object_names():
 t=s.settings.setup.boundary_conditions.wall[name].phase['mixture'].turbulence
 t.roughness_height=0.0 if name=='bottom' else 4.5e-5
 t.roughness_const=.5
drain_config=drain.configure(s,enabled=True,refresh_span_s=1e-7)
run.assert_bulk_active(s);run.read_feed(s,1.0)
same_facets(upper,facets(s,'wall'))
configured=run.base.state(s)
run.require_match({'fields':configured['readback']['fields']},{'fields':before['readback']['fields']})
assert configured['methods']==before['methods']
folder=run.WORK/'60k'
from run_phase72a_stage4_ewf_drain import define_reports
define_reports(s)
run.base.instrument(s,folder/'monitors')
pair=lane_save(s,folder,'ewf-N8082-'+tag)
run.dump(evidence/'prepared.json',{'status':'SAVED_REOPEN_PENDING','pair':pair,'changes':changes,'drain':drain_config})
print('EWF_CHILD_SAVED_HASHED',flush=True)
run.load(s,pair)
after=run.base.state(s)
run.require_match(after['readback'],configured['readback'])
run.require_setup_same(after['setup'],configured['setup'])
assert after['methods']==configured['methods']
same_facets(upper,facets(s,'wall'))
assert run.native_iteration(s)==8082 and math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12)
run.assert_bulk_active(s)
drain.audit(s,True)
assert all(dict(s.rp_vars('wall-film/model-parameters'))[k]==v for k,v in changes.items())
receipt={'status':'SETTINGS_APPLIED_REOPEN_VERIFIED',
         'server_id':'6','mesh':'60k','parent':parent,'pair':pair,'changes':changes,'drain':drain_config,
         'before':before,'after':after,'film':run.film(s),'native_iteration':8082,'no_solve_submitted':True,
         'original_main_film_facets_preserved':True,'all_bulk_equations_active':True,
         'pending_setting':None,
         'review':'Server6-only attach; exclusive lock; idle N8082 parent match; allocate lower storage and restore original data; exact main-film facets; settings/readback; local save/hash/reopen. No solve or bulk initialization.',
         'future_steps':{'bulk_active_adjustment':1500,'frozen_transition':1000,'check_2p5us':1000,'check_5us':1000,'growth_at_5us':37317,'final_bulk_active_at_5us':1000}}
run.dump(evidence/'settings-receipt.json',receipt);run.dump(out/'60k-ewf-settings-current.json',receipt)
print('SETTINGS_CHILD_REOPEN_VERIFIED',receipt['status'],str(pair['case']),flush=True)

run.dump(out/'bulk-plan-readback.json',run.bulk_audit(s))
