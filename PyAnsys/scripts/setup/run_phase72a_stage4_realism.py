"""Selected Stage 4 mechanisms: N29815 +2000 coupled, then +50 ms film-only.

Attach only; no initialization. Local paired checkpoints; no endpoint overwrite.
Use verified v252 particle TUI recipe and native film parameter readback/reopen.
"""
from pathlib import Path, PureWindowsPath
import argparse,json,math,sys,time,traceback,re
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase72a_commercial_steel_continuation as parent
from run_phase72a_reentrainment_speeds import MODEL_ARGS
from run_phase72a_stage3_server3 import instrument,iterate,state
from run_phase72a_local_film_replay import require_match
from run_phase72a_adaptive_film import FILM,history
from pyansys_fluent.stage4_native import ensure_remote_directory
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.film_thickness_guard import assess_thickness
OUT=ROOT/'output/phase72a-stage4-realism/20261007'
WORK=PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\realism-20261007\verified-run')
MANIFEST=OUT/'run-manifest.json'
FLOW_MOMENTUM_COUPLING=True
# Human instruction, 7 October 2026: reaching 0.3 m makes a Stage 4 run unrealistic.
UNREALISTIC_FILM_THICKNESS_M=.3
TARGETS={'solve-wallfilm?':True,'solve-momentum?':True,'mom-equation?':True,
 'mom-gravity?':True,'mom-aero-drive?':True,'mom-pressure?':True,'mom-spreading?':True,
 'surface-tension?':True,'dpm-collection?':True,'dpm-splashing?':True,
 'film-separation?':True,'film-stripping?':True,'secondary-phase-mode':1,'film-coupled-solution?':True}
MASS='p72a-e2.7-ewf-film-mass-total';ACC='p72a-e2.7-ewf-secondary-phase-mass-total';DRAIN='p72a-e2.7-ewf-outflow-mass-total'
EXTRA={'p72s4-dpm-source':'film-dpm-mass-src','p72s4-stripped-mass':'film-stripped-mass','p72s4-separated-mass':'film-separated-mass'}

def dump(p,v):parent.dump(p,v)
def film(s):return parent.film(s)
def params(s):return dict(s.rp_vars('wall-film/model-parameters'))
def fields(s):
 result=state(s)['readback']['fields']
 for item in s.settings.solution.report_definitions.compute(report_defs=[ACC]+list(EXTRA)):result.update(item)
 return result
def save(s,label):return parent.pair_save(s,WORK/(label+'.cas.h5'),WORK/'scratch',scratch_tag=label)
def setparams(s,delta):
 p=params(s);assert set(delta).issubset(p)
 s.rp_vars('wall-film/model-parameters',[(k,delta.get(k,v)) for k,v in p.items()])
 assert all(params(s)[k]==v for k,v in delta.items())
def audit(s):
 p=params(s);assert all(p[k]==v for k,v in TARGETS.items())
 w=s.settings.setup.boundary_conditions.wall['wall'].phase['mixture'].wall_film.get_state()
 assert w['enable_flow_momentum_coupling'] is FLOW_MOMENTUM_COUPLING
 assert all(w[k] for k in ['eulerian_film_wall','enable_dpm_wall_splash','allow_film_boundary_separation'])
 assert not any(p[k] for k in ['solve-energy?','solve-scalar?','solve-vapor?','ewf-adaptive?'])
 for z,v in parent.roughness(s).items():assert v['roughness_height']['value']==(0 if z=='bottom' else 4.5e-5)
 return {'film_parameters':p,'wall':w,'equations':s.settings.solution.controls.equations.get_state()}
def reopen(s,pair):
 before=state(s);clock=film(s)
 s.settings.file.read_case(file_name=pair['case']);s.settings.file.read_data(file_name=pair['data'])
 after=state(s);require_match(after['readback'],before['readback'])
 assert after['setup']==before['setup'] and after['methods']==before['methods']
 assert math.isclose(film(s)['film_elapsed_time'],clock['film_elapsed_time'],abs_tol=1e-12,rel_tol=0)
 return audit(s)
def configure_step(s,dt,label):
 setparams(s,{'timestep-max':dt,'ewf-adaptive?':False,'sub-iter-nums':30})
 pair=save(s,label);reopen(s,pair);return pair

def prepare(s):
 if MANIFEST.exists():raise RuntimeError('Existing manifest must be reconciled; use --resume')
 assert parent.native_iteration(s)==29815 and s.settings.solution.run_calculation.iterate.is_active()
 m={'status':'PREPARING','authority':'human_2026_10_07_current_chat_settings_table',
 'parent_pair':json.loads((OUT/'parent-pair.json').read_text()),'parent_native_iteration':29815,
 'bulk_target_iteration':31815,'film_only_added_target_s':.05,'film_target_step_s':15e-6,
 'work_root':str(WORK),'output_root':str(OUT),'blocks':[],'initialization':'FORBIDDEN'}
 dump(MANIFEST,m)
 # Reopen exact preserved parent: remove all exploratory configuration changes.
 s.settings.file.read_case(file_name=m['parent_pair']['case']);s.settings.file.read_data(file_name=m['parent_pair']['data'])
 before=state(s);initial=film(s);dump(OUT/'loaded-parent.json',{'state':before,'film':initial})
 m['original_equations']=s.settings.solution.controls.equations.get_state();assert all(m['original_equations'].values())
 for folder in [WORK,WORK/'scratch',WORK/'monitors']:ensure_remote_directory(s,str(folder))
 material_name='water-liquid-at-psep-pcle'
 material=s.settings.setup.materials.inert_particle
 if material_name not in material.get_object_names():material.create(name=material_name)
 source=s.settings.setup.materials.fluid['water-liquid-at-psep'].get_state()
 material[material_name].density=source['density'];material[material_name].viscosity=source['viscosity']
 material[material_name].dpm_surften={'option':'value','value':params(s)['surface-tension']}
 for name in s.settings.setup.models.discrete_phase.injections.get_object_names():
  s.settings.setup.models.discrete_phase.injections[name].material=material_name
 m['dpm_material_compatibility']={'name':material_name,'density':source['density'],'viscosity':source['viscosity'],'inlet_feed':'UNCHANGED_NEGLIGIBLE'}
 dump(MANIFEST,m)
 remote=str(WORK/'configuration.trn');s.tui.file.start_transcript(remote)
 s.tui.define.models.eulerian_wallfilm.model_options(*MODEL_ARGS)
 # Preserve native coefficients; activate requested force terms in the native
 # model-parameter list. Paired reopen activates the stored film solver state.
 setparams(s,TARGETS)
 s.scheme.eval('(ti-menu-load-string "/define/boundary-conditions/set/wall wall () mixture film-splash-wall? yes film-boundary-separation? yes quit")')
 s.settings.setup.boundary_conditions.wall['wall'].phase['mixture'].wall_film.enable_flow_momentum_coupling=True
 s.tui.file.stop_transcript();(OUT/'configuration.trn').write_text(read_text(s,remote))
 audit(s);assert parent.native_iteration(s)==29815
 require_match({'fields':state(s)['readback']['fields']},{'fields':before['readback']['fields']})
 assert film(s)['film_elapsed_time']==initial['film_elapsed_time']
 definitions=s.settings.solution.report_definitions.surface;files=s.settings.solution.monitor.report_files
 for name,field in EXTRA.items():
  if name not in definitions.get_object_names():definitions.create(name=name)
  definitions[name].set_state({'report_type':'surface-sum','field':field,'surface_names':['wall']})
  if name not in files.get_object_names():files.create(name=name)
  files[name].report_defs=[name]
 m['report_paths']=instrument(s,WORK/'monitors')
 s.settings.file.auto_save.data_frequency=0
 m['prepared_pair']=save(s,'prepared-realism-N29815');m['prepared_reopen']=reopen(s,m['prepared_pair'])
 prepared=state(s);dump(OUT/'prepared-reopen.json',{'state':prepared,'film':film(s),'audit':m['prepared_reopen']})
 dump(OUT/'report-definitions.json',s.settings.solution.report_definitions.get_state())
 m.update(status='PREPARED_VERIFIED',latest_pair=m['prepared_pair'],verified_native_end=29815,parent_film_time_s=initial['film_elapsed_time'])
 dump(MANIFEST,m);print('PREPARED_VERIFIED',flush=True);return m

def batch(s,m,count,label,dt,frozen,completed=False):
 if m.get('run_classification')=='UNREALISTIC':
  raise RuntimeError('UNREALISTIC run cannot continue from its rejected endpoint')
 if completed:
  start=m['verified_native_end']
  checkpoint=json.loads((OUT/f"bulk-film-N{start}.json").read_text())
  initial=checkpoint['film'];before=checkpoint['fields']
  assert parent.native_iteration(s)==start+count
 else:start=parent.native_iteration(s);initial=film(s);before=fields(s)
 end=start+count
 path=WORK/(f'{label}-N{start}-N{end}.trn')
 if not completed:s.tui.file.start_transcript(str(path))
 m.pop('error',None);m.update(status='RUNNING',active_target=end,active_segment=label,active_step_s=dt);dump(MANIFEST,m)
 print('RECONCILE' if completed else 'SUBMIT',label,start,end,'dt',dt,flush=True);t0=time.monotonic()
 if not completed:iterate(s,count)
 pair=save(s,f'{label}-N{end}');print('SOLVE_ENDPOINT_SAVED',end,flush=True);final=film(s);after=fields(s)
 s.tui.file.stop_transcript();text=read_text(s,str(path));(OUT/path.name).write_text(text)
 assert parent.native_iteration(s)==end
 elapsed=final['film_elapsed_time']-initial['film_elapsed_time']
 assert math.isclose(elapsed,count*dt,rel_tol=1e-8,abs_tol=1e-10),'Accepted step differs'
 printed=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
 assert len(printed)==count,(len(printed),count)
 histories={}
 for name,source in m['report_paths'].items():
  raw=read_text(s,source);(OUT/(name+'.out')).write_text(raw);h=history(raw)
  assert set(range(start+1,end+1)).issubset(h),name
  assert all(math.isfinite(v) for v in h.values()),name
  histories[name]=h
 sums={name:sum(histories[name][i]*dt for i in range(start+1,end+1)) for name in [ACC,'p72s4-dpm-source']}
 changes={name:after[name][0]-before[name][0] for name in [MASS,DRAIN,'p72s4-stripped-mass','p72s4-separated-mass']}
 ledger=sum(changes.values())-sum(sums.values())
 met={'label':label,'native_start':start,'native_end':end,'updates':count,'step_s':dt,
 'frozen_bulk':frozen,'film_start_s':initial['film_elapsed_time'],'film_end_s':final['film_elapsed_time'],
 'film_elapsed_s':elapsed,'wall_seconds':time.monotonic()-t0,'peak_courant':max(x[2] for x in printed),
 'film_mass_kg':after[MASS][0],'mass_changes_kg':changes,'integrated_sources_kg':sums,
 'sampled_film_ledger_residual_kg':ledger,'sampled_ledger_error_percent':100*abs(ledger)/max(sum(abs(v) for v in sums.values()),1e-30),
 'inner_residual_rows':len(re.findall(r'sub-iteration:',text)),'pair':pair,'transcript':str(path),
 'max_thickness_m':after['p72a-e2.7-ewf-thickness-max'][0]}
 thickness=assess_thickness(
  {i:histories['p72a-e2.7-ewf-thickness-max'][i] for i in range(start+1,end+1)},
  min(params(s)['thickness-limit'],m.get('unrealistic_film_thickness_limit_m',UNREALISTIC_FILM_THICKNESS_M)))
 met['thickness_assessment']=thickness
 if thickness['first_crossing_native_iteration'] is not None:
  thickness['first_crossing_film_time_s']=initial['film_elapsed_time']+(thickness['first_crossing_native_iteration']-start)*dt
 reopened=reopen(s,pair);met['reopen']='PASS'
 dump(OUT/f'{label}-N{end}.json',{'metrics':met,'fields':after,'film':final,'audit':reopened})
 m['blocks'].append(met);m.update(status='CHECKPOINT_VERIFIED',latest_pair=pair,verified_native_end=end,verified_film_time_s=final['film_elapsed_time'],active_target=None)
 dump(MANIFEST,m);print('VERIFIED_BATCH',json.dumps(met),flush=True)
 if thickness['classification']=='UNREALISTIC':
  m.update(status='UNREALISTIC',run_classification='UNREALISTIC',unrealistic_thickness_assessment=thickness,
   unrealistic_film_thickness_limit_m=thickness['limit_m'],rejected_endpoint_pair=pair)
  dump(MANIFEST,m)
  raise RuntimeError('UNREALISTIC: film thickness limit reached; paired endpoint preserved; continuation stopped')
 if re.search(r'floating point exception|received signal|fatal error|Divergence detected',text,re.I) or met['peak_courant']>1:
  raise RuntimeError('Numerical recovery needed; endpoint preserved')
 if frozen:
  frozenfields=m['frozen_fields']
  names=['v2-total-liquid-mass','v2-flux-phase2-steamoutlet','v2-flux-phase1-steamoutlet']
  for name in names:assert math.isclose(after[name][0],frozenfields[name][0],rel_tol=1e-9,abs_tol=1e-10),name
 return met

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');args=parser.parse_args()
 global WORK
 s=parent.attach()
 if args.resume:
  m=json.loads(MANIFEST.read_text());WORK=PureWindowsPath(m['work_root'])
  if m['status'] not in ['CHECKPOINT_VERIFIED','PREPARED_VERIFIED','RECOVERY_PREPARED_VERIFIED'] or m.get('active_target') is not None:
   raise RuntimeError('Unresolved native command or blocked session: reconcile before resume')
  assert parent.native_iteration(s)==m['verified_native_end'];audit(s)
 else:m=prepare(s)
 while parent.native_iteration(s)<m['bulk_target_iteration']:
  left=m['bulk_target_iteration']-parent.native_iteration(s)
  count=20 if not m['blocks'] else min(left,1000)
  batch(s,m,count,'bulk-film',m.get('bulk_step_s',1e-6),False)
 if 'film_only_start_s' not in m:
  m['full_bulk_endpoint']=m['latest_pair'];m['frozen_fields']=state(s)['readback']['fields']
  m['film_only_start_s']=film(s)['film_elapsed_time'];m['film_only_target_s']=m['film_only_start_s']+.05
  for name in m['original_equations']:s.settings.solution.controls.equations[name]=False
  m['frozen_equations']=s.settings.solution.controls.equations.get_state();assert not any(m['frozen_equations'].values())
  m['latest_pair']=configure_step(s,15e-6,f"frozen-prepared-N{m['bulk_target_iteration']}");dump(MANIFEST,m)
  batch(s,m,20,'film-only-probe',15e-6,True)
 while film(s)['film_elapsed_time']<m['film_only_target_s']-1e-11:
  left=m['film_only_target_s']-film(s)['film_elapsed_time'];dt=params(s)['timestep-max']
  count=min(1000,int(math.floor((left+1e-12)/dt)))
  if count==0:
   dt=left;configure_step(s,dt,f'final-trim-controls-N{parent.native_iteration(s)}');count=1
  batch(s,m,count,'film-only',dt,True)
 m.update(status='COMPLETE',final_pair=m['latest_pair'],film_only_added_s=film(s)['film_elapsed_time']-m['film_only_start_s'],final_audit=audit(s),solver_left_open=True)
 dump(MANIFEST,m);print('COMPLETE',m['verified_native_end'],m['film_only_added_s'],flush=True)

if __name__=='__main__':
 try:main()
 except Exception:
  if MANIFEST.exists():
   m=json.loads(MANIFEST.read_text());m.update(status='UNREALISTIC' if m.get('run_classification')=='UNREALISTIC' else 'RECOVERY_REQUIRED',error=traceback.format_exc());dump(MANIFEST,m)
  raise
