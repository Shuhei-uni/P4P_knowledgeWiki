"""Matched Stage 4 mechanism toggles; preserve N37149 and freeze carrier equations."""
from pathlib import Path,PureWindowsPath
import argparse,json,sys,math,time,traceback,functools
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts/setup'),str(ROOT/'src')]
import retry_phase72a_stage4_feedback_off as previous
r=previous.run
from pyansys_fluent.stage4_native import ensure_remote_directory
from run_phase72a_adaptive_film import history
BASE=ROOT/'output/phase72a-stage4-sensitivity/20261007'
WORK=PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\sensitivity-20261007')
MASTER=BASE/'run-manifest.json'
OLD_TARGETS=dict(r.TARGETS)
BASE_FIELDS=r.fields
SOURCE=ROOT/'output/phase72a-stage4-realism/20261007/feedback-off/run-manifest.json'
CANDIDATES={'stripping-on':{},'stripping-off':{'film-stripping?':False},'surface-tension-off':{'surface-tension?':False},'surface-tension-off-after-stripping':{'film-stripping?':False,'surface-tension?':False},'spreading-off-after-stripping':{'film-stripping?':False,'mom-spreading?':False},'coupled-off-after-stripping':{'film-stripping?':False,'film-coupled-solution?':False},'curvature-smoothing-on-after-stripping':{'film-stripping?':False,'film-smoothing?':True},'coupled-off':{'film-coupled-solution?':False}}


def use_branch(name):
 r.OUT=BASE/name;r.MANIFEST=r.OUT/'run-manifest.json';r.WORK=WORK/name
 r.TARGETS=dict(OLD_TARGETS);r.TARGETS.update(CANDIDATES[name]);r.FLOW_MOMENTUM_COUPLING=False
 r.fields=BASE_FIELDS


def compatible_fields(s,m):
 # Disabled mechanism fields can disappear. Never present a synthetic value as a native history.
 result=r.state(s)['readback']['fields']
 names=[r.ACC]+list(r.EXTRA)
 if m.get('stripping_report_mode')=='INACTIVE_MODEL_OFF':names.remove('p72s4-stripped-mass')
 for item in s.settings.solution.report_definitions.compute(report_defs=names):result.update(item)
 if m.get('stripping_report_mode')=='INACTIVE_MODEL_OFF':
  result['p72s4-stripped-mass']=[m['disabled_stripping_cumulative_reference_kg'],'kg']
 return result


def sync_master(m):
 master=json.loads(MASTER.read_text());name=m['branch']
 master.setdefault('branches',{})[name]={'status_owner':str(r.MANIFEST.relative_to(ROOT.parent)),
  'status':m['status'],'verified_native_end':m['verified_native_end'],'added_film_time_s':m.get('verified_film_time_s',m['parent_film_time_s'])-m['parent_film_time_s']}
 master['active_branch']=name;r.dump(MASTER,master)


def prepare(s,name,source):
 use_branch(name)
 if r.MANIFEST.exists():raise RuntimeError('Existing branch requires explicit reconciliation')
 r.OUT.mkdir(parents=True,exist_ok=True)
 for folder in [r.WORK,r.WORK/'scratch',r.WORK/'monitors']:ensure_remote_directory(s,str(folder))
 s.settings.file.read_case(file_name=source['case']);s.settings.file.read_data(file_name=source['data'])
 parent_n=source['native_iteration'];assert r.parent.native_iteration(s)==parent_n
 before=r.state(s);clock=r.film(s);params=r.params(s)
 inactive_parent=params['film-stripping?'] is False
 reference=json.loads(MASTER.read_text()).get('disabled_stripping_cumulative_reference_kg')
 initialfields=compatible_fields(s,{'stripping_report_mode':'INACTIVE_MODEL_OFF','disabled_stripping_cumulative_reference_kg':reference}) if inactive_parent else BASE_FIELDS(s)
 assert not any(s.settings.solution.controls.equations.get_state().values())
 r.dump(r.OUT/'loaded-parent.json',{'state':before,'film':clock,'fields':initialfields,'pair':source})
 numerical_delta={'thickness-limit':r.UNREALISTIC_FILM_THICKNESS_M}
 delta={**CANDIDATES[name],**numerical_delta}
 r.setparams(s,delta);afterparams=r.params(s)
 assert afterparams=={k:delta.get(k,v) for k,v in params.items()}
 assert r.state(s)['methods']==before['methods']
 r.require_match({'fields':r.state(s)['readback']['fields']},{'fields':before['readback']['fields']})
 assert r.film(s)['film_elapsed_time']==clock['film_elapsed_time']
 m={'branch':name,'status':'PREPARING','authority':'human_20261007_targeted_setting_sensitivity','parent_pair':source,
 'parent_native_iteration':parent_n,'parent_film_time_s':clock['film_elapsed_time'],'work_root':str(r.WORK),
 'output_root':str(r.OUT),'physical_delta':{k:v for k,v in CANDIDATES[name].items() if params[k]!=v},
 'numerical_delta':numerical_delta,'unrealistic_film_thickness_limit_m':r.UNREALISTIC_FILM_THICKNESS_M,'step_s':15e-6,'blocks':[],
 'frozen_fields':before['readback']['fields'],'stripping_report_mode':'INACTIVE_MODEL_OFF' if inactive_parent else 'NATIVE','verified_native_end':parent_n}
 # Probe the already-defined cumulative report before relying on it after disabling the mechanism.
 if inactive_parent:m['disabled_stripping_cumulative_reference_kg']=reference
 if name.endswith('-after-stripping'):m['continuation_horizon_s']=.035;m['inherited_verified_film_time_s']=.015
 if r.TARGETS['film-stripping?'] is False and not inactive_parent:
  try:
   answer=s.settings.solution.report_definitions.compute(report_defs=['p72s4-stripped-mass'])
   value={k:v for item in answer for k,v in item.items()}['p72s4-stripped-mass'][0]
   assert math.isfinite(value)
   m['disabled_stripping_initial_native_kg']=value
  except Exception as exc:
   m['stripping_report_mode']='INACTIVE_MODEL_OFF';m['disabled_stripping_cumulative_reference_kg']=initialfields['p72s4-stripped-mass'][0]
   m['stripping_field_capability_gap']=str(exc)
 r.fields=lambda session:compatible_fields(session,m)
 paths={}
 files=s.settings.solution.monitor.report_files
 for namefile in files.get_object_names():
  obj=files[namefile];key=obj.report_defs()[0]
  if key=='p72s4-stripped-mass' and m['stripping_report_mode']=='INACTIVE_MODEL_OFF':obj.active=False;continue
  path=str(r.WORK/'monitors'/(key+'.out'));obj.file_name=path;paths[key]=path
 m['report_paths']=paths
 # Keep names short: pair_save repeats the label in the Windows hash-evidence path.
 pair=r.save(s,f'prep-N{parent_n}-'+str(time.time_ns()));audit=r.reopen(s,pair)
 try:prepared_fields=r.fields(s)
 except Exception as exc:
  assert r.params(s)['film-stripping?'] is False
  m['stripping_report_mode']='INACTIVE_MODEL_OFF';m['disabled_stripping_cumulative_reference_kg']=initialfields['p72s4-stripped-mass'][0];m['stripping_field_capability_gap']=str(exc)
  prepared_fields=r.fields(s)
  for report_name in files.get_object_names():
   obj=files[report_name]
   if obj.report_defs()==['p72s4-stripped-mass']:obj.active=False
  m['report_paths'].pop('p72s4-stripped-mass',None)
  pair=r.save(s,f'prepared-inactive-report-repair-N{parent_n}-'+str(time.time_ns()));audit=r.reopen(s,pair)
 m.update(status='PREPARED_VERIFIED',prepared_pair=pair,latest_pair=pair,prepared_audit=audit)
 r.dump(r.OUT/'prepared-reopen.json',{'state':r.state(s),'film':r.film(s),'audit':audit,'fields':prepared_fields})
 r.dump(r.OUT/'report-definitions.json',s.settings.solution.report_definitions.get_state())
 r.dump(r.MANIFEST,m);sync_master(m);print('BRANCH_PREPARED',name,flush=True);return m


def summary(m):
 h={name:history((r.OUT/(name+'.out')).read_text()) for name in m['report_paths']}
 x=np.arange(m['parent_native_iteration']+1,m['verified_native_end']+1)
 dt=np.concatenate([np.full(b['updates'],b['step_s']) for b in m['blocks']]);assert len(x)==len(dt)
 prepared=json.loads((r.OUT/'prepared-reopen.json').read_text())['fields']
 signals={'secondary':np.array([h[r.ACC][int(i)] for i in x]),'dpm':np.array([h['p72s4-dpm-source'][int(i)] for i in x])}
 for key,name in [('storage',r.MASS),('stripping','p72s4-stripped-mass'),('separation','p72s4-separated-mass'),('outflow',r.DRAIN)]:
  if name not in h:
   assert key=='stripping' and m['stripping_report_mode']=='INACTIVE_MODEL_OFF';signals[key]=np.zeros(len(x));continue
  values=np.array([prepared[name][0]]+[h[name][int(i)] for i in x]);signals[key]=np.diff(values)/dt
 film=np.array([h[r.MASS][int(i)] for i in x]);elapsed=np.cumsum(dt)
 window=np.flatnonzero(np.isclose(dt,m['step_s'],rtol=0,atol=1e-12))[-500:]
 metrics={}
 for key,values in signals.items():
  v=values[window];n=np.arange(len(v));z=v-np.polyval(np.polyfit(n,v,1),n)
  c=np.cos(2*np.pi*n/4);q=np.sin(2*np.pi*n/4);amp=math.hypot(2*np.mean(z*c),2*np.mean(z*q))/math.sqrt(2)
  sd=float(np.std(z));metrics[key]={'mean_kg_s':float(np.mean(v)),'raw_sd_kg_s':float(np.std(v)),'detrended_sd_kg_s':sd,
   'four_step_rms_kg_s':amp,'four_step_variance_fraction':min(1,(amp/sd)**2) if sd>1e-12 else 0,
   'lag2':float(np.corrcoef(z[:-2],z[2:])[0,1]) if sd>1e-12 else None,
   'min_kg_s':float(v.min()),'max_kg_s':float(v.max())}
 import csv
 with (r.OUT/'diagnostics.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['native_iteration','added_film_time_s','film_mass_kg']+list(signals))
  for j,i in enumerate(x):w.writerow([i,elapsed[j],film[j]]+[signals[k][j] for k in signals])
 a={'branch':m['branch'],'metrics':metrics,'film_initial_kg':prepared[r.MASS][0],'film_final_kg':float(film[-1]),
 'updates':len(x),'added_time_s':float(elapsed[-1]),'window_updates':len(window),
 'analysis_window_native_range':[int(x[window[0]]),int(x[window[-1]])],
 'trimmed_steps_excluded_from_metrics':int(np.sum(~np.isclose(dt,m['step_s'],rtol=0,atol=1e-12))),
 'peak_courant':max(b['peak_courant'] for b in m['blocks']),'stripping_report_mode':m['stripping_report_mode'],
 'frozen_bulk_verified':True,'physical_delta':m['physical_delta']}
 r.dump(r.OUT/'analysis-summary.json',a);return a


def run_screen(s,name,source):
 m=prepare(s,name,source)
 if name!='stripping-on':r.batch(s,m,20,'screen-probe',15e-6,True);sync_master(m)
 left=m['parent_native_iteration']+1000-r.parent.native_iteration(s)
 r.batch(s,m,left,'screen',15e-6,True);sync_master(m)
 m['status']='SCREEN_COMPLETE_VERIFIED';m['screen_summary']=summary(m);r.dump(r.MANIFEST,m);sync_master(m)
 print('SCREEN_COMPLETE',name,json.dumps(m['screen_summary']),flush=True)
 return m


def main():
 p=argparse.ArgumentParser();p.add_argument('--branch',choices=list(CANDIDATES));p.add_argument('--continue-branch',choices=list(CANDIDATES));args=p.parse_args()
 s=r.parent.attach()
 # This family retains the same RP variable names. Cache names, never their values.
 # Recent PyFluent otherwise fetches/parses all 9984 names for every read.
 s.rp_vars.allowed_values=functools.lru_cache(maxsize=1)(s.rp_vars.allowed_values)
 if args.continue_branch:
  use_branch(args.continue_branch);m=json.loads(r.MANIFEST.read_text());r.fields=lambda session:compatible_fields(session,m)
  assert m['status']=='SCREEN_COMPLETE_VERIFIED' and r.parent.native_iteration(s)==m['verified_native_end']
  r.audit(s)
  if r.params(s)['thickness-limit']!=r.UNREALISTIC_FILM_THICKNESS_M:
   r.setparams(s,{'thickness-limit':r.UNREALISTIC_FILM_THICKNESS_M})
   m['latest_pair']=r.save(s,f'limit03-N{r.parent.native_iteration(s)}');r.reopen(s,m['latest_pair'])
  m['unrealistic_film_thickness_limit_m']=r.UNREALISTIC_FILM_THICKNESS_M;r.dump(r.MANIFEST,m)
  target=m['parent_film_time_s']+m.get('continuation_horizon_s',.05)
  while r.film(s)['film_elapsed_time']<target-1e-11:
   left=target-r.film(s)['film_elapsed_time'];dt=r.params(s)['timestep-max'];count=min(1000,int(math.floor((left+1e-12)/dt)))
   if count==0:dt=left;r.configure_step(s,dt,f'trim-controls-N{r.parent.native_iteration(s)}');count=1
   r.batch(s,m,count,'continuation',dt,True);sync_master(m)
  m['horizon_endpoint_pair']=m['latest_pair'];m['latest_pair']=r.configure_step(s,15e-6,f'final-ready-15us-N{r.parent.native_iteration(s)}')
  m.update(status='COMPLETE',final_pair=m['latest_pair'],final_audit=r.audit(s),ready_step_s=15e-6,solver_left_open=True)
  m['continuation_summary']=summary(m);r.dump(r.MANIFEST,m);sync_master(m)
  master=json.loads(MASTER.read_text());master.update(status='COMPLETE',selected_branch=args.continue_branch,final_status_owner=str(r.MANIFEST.relative_to(ROOT.parent)));r.dump(MASTER,master)
  print('CONTINUATION_COMPLETE',m['verified_native_end'],r.film(s)['film_elapsed_time']-m['parent_film_time_s'],flush=True);return
 if not MASTER.exists():
  assert r.parent.native_iteration(s)==37149
  for folder in [WORK,WORK/'scratch']:ensure_remote_directory(s,str(folder))
  r.WORK=WORK;preserved=r.save(s,'preserved-current-N37149')
  source=json.loads(SOURCE.read_text())['final_pair']
  r.dump(MASTER,{'status':'SCREENING','authority':'human_20261007_targeted_setting_sensitivity','parent_pair':source,'preserved_live_pair':preserved,'branches':{},'initialization':'FORBIDDEN'})
 else:
  assert args.branch,'Existing campaign: specify a new matched branch, or reconcile before resuming'
  master=json.loads(MASTER.read_text());source=master['secondary_parent_pair'] if args.branch.endswith('-after-stripping') else master['parent_pair']
 names=[args.branch] if args.branch else ['stripping-on','stripping-off']
 for name in names:run_screen(s,name,source)
 master=json.loads(MASTER.read_text());master['status']='SCREENS_COMPLETE_REVIEW';r.dump(MASTER,master)
 print('SCREENS_READY_FOR_COMPARISON',flush=True)

if __name__=='__main__':
 try:main()
 except Exception:
  if r.MANIFEST.exists() and str(r.MANIFEST).startswith(str(BASE)):
   m=json.loads(r.MANIFEST.read_text());m.update(status='UNREALISTIC' if m.get('run_classification')=='UNREALISTIC' else 'RECOVERY_REQUIRED',error=traceback.format_exc());r.dump(r.MANIFEST,m)
  if MASTER.exists():
   master=json.loads(MASTER.read_text());unrealistic=r.MANIFEST.exists() and json.loads(r.MANIFEST.read_text()).get('run_classification')=='UNREALISTIC'
   master.update(status='UNREALISTIC' if unrealistic else 'RECOVERY_REQUIRED',error=traceback.format_exc())
   if unrealistic:master.update(run_classification='UNREALISTIC',unrealistic_status_owner=str(r.MANIFEST.relative_to(ROOT.parent)))
   r.dump(MASTER,master)
  raise
