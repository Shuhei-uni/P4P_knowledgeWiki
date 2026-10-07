"""Verify accepted 50 ms lineage, immutable evidence, and live settings; no solves."""
from pathlib import Path
import sys, json, hashlib, re, functools
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'scripts/analysis'), str(ROOT/'scripts/setup'), str(ROOT/'src')]
import analyze_phase72a_stage4_setting_sensitivity as a
import run_phase72a_stage4_setting_sensitivity as q
b=a.OUT
master=json.loads((b/'run-manifest.json').read_text())
assert master['status']=='COMPLETE'
name=master['selected_branch'];q.use_branch(name)
m=json.loads(q.r.MANIFEST.read_text());assert m['status']=='COMPLETE'
checked=[]
for manifest in b.glob('**/raw/**/evidence-manifest.json'):
 for fn,digest in json.loads(manifest.read_text())['sha256'].items():
  assert hashlib.sha256((manifest.parent/fn).read_bytes()).hexdigest()==digest,(manifest,fn)
 checked.append(str(manifest.relative_to(b)))
frame=pd.read_csv(b/'accepted-continuation.csv');assert len(frame)==3334
assert frame.native_iteration.iloc[0]==37150 and frame.native_iteration.iloc[-1]==40483
assert np.all(np.diff(frame.native_iteration)==1)
assert abs(frame.added_film_time_s.iloc[-1]-.05)<1e-10
assert frame.courant.max()<=1
assert np.isfinite(frame.select_dtypes('number').to_numpy()).all()
if name=='stripping-on':
 prefix=pd.read_csv(b/'stripping-on/raw/screen-N38149/diagnostics.csv')
 columns=list(prefix.columns)
 assert np.allclose(frame[columns].iloc[:1000].to_numpy(),prefix.to_numpy(),rtol=1e-10,atol=1e-10), 'Accepted prefix differs from archived screen'
lineage=[(name,'final-N40483',37150,40483)] if m['parent_native_iteration']==37149 else [('stripping-off','screen-N38149',37150,38149),(name,'final-N40483',38150,40483)]
peak_thickness=0.;peak_velocity=0.;final_velocity=None;peak_average_velocity=0.;final_average_velocity=None
for branch,raw,low,high in lineage:
 folder=b/branch/'raw'/raw
 for fn in ['v2-total-liquid-mass.out','v2-flux-phase2-steamoutlet.out','v2-flux-phase1-steamoutlet.out']:
  values=a.native_values(folder/fn);x=np.array([values[n] for n in range(low,high+1)])
  assert np.allclose(x,x[0],rtol=0,atol=1e-8),(fn,x.min(),x.max())
 for field in ['thickness-max', 'velocity-mag-max', 'velocity-mag-awavg']:
  values=a.native_values(folder/f'p72a-e2.7-ewf-{field}.out')
  x=np.array([values[n] for n in range(low,high+1)])
  assert np.isfinite(x).all()
  if field=='thickness-max':peak_thickness=max(peak_thickness,float(x.max()));assert x.max()<1
  elif field=='velocity-mag-max':peak_velocity=max(peak_velocity,float(x.max()));final_velocity=float(x[-1])
  else:peak_average_velocity=max(peak_average_velocity,float(x.max()));final_average_velocity=float(x[-1])
for block in m['blocks']:
 transcript=q.r.OUT/Path(block['transcript'].replace('\\','/')).name
 films=list(q.r.FILM.finditer(transcript.read_text()))
 assert len(films)==block['updates']
 assert abs(block['film_elapsed_s']-block['updates']*block['step_s'])<1e-10
 assert block['reopen']=='PASS' and block['frozen_bulk']
 assert block['peak_courant']<=1
 assert all(len(block['pair'][key])==64 for key in ['case_sha256','data_sha256'])
s=q.r.parent.attach();s.rp_vars.allowed_values=functools.lru_cache(maxsize=1)(s.rp_vars.allowed_values);q.r.fields=lambda session:q.compatible_fields(session,m)
live={'native_iteration':q.r.parent.native_iteration(s),'film':q.r.film(s),'audit':q.r.audit(s),'state':q.r.state(s),'fields':q.r.fields(s)}
assert live['native_iteration']==40483
assert abs(live['film']['film_elapsed_time']-(m['parent_film_time_s']+m.get('continuation_horizon_s',.05)))<1e-10
assert live['audit']['film_parameters']['timestep-max']==15e-6
assert not any(live['audit']['equations'].values())
assert live['audit']['film_parameters']['film-stripping?'] is q.r.TARGETS['film-stripping?']
assert live['audit']['film_parameters']['surface-tension?'] is True
assert all(live['audit']['film_parameters'][key] == value for key,value in q.r.TARGETS.items())
expected=json.loads((b/'live-parent-readback.json').read_text())['audit']['film_parameters']
expected.update(q.CANDIDATES[name])
assert live['audit']['film_parameters']==expected, 'Unexpected film-control or property change'
assert abs(live['fields'][q.r.MASS][0]-frame.film_mass_kg.iloc[-1])<1e-8
q.r.dump(b/'final-live-readback.json',live)
result={'status':'PASS','raw_manifests_verified':checked,'accepted_updates':len(frame),'accepted_added_film_time_s':float(frame.added_film_time_s.iloc[-1]),'accepted_peak_courant':float(frame.courant.max()),'final_native_iteration':40483,'final_film_clock_s':live['film']['film_elapsed_time'],'ready_step_s':15e-6,'bulk_frozen':True,'solver_left_open':True,'new_solve_calls':0}
result.update(accepted_peak_thickness_m=peak_thickness, accepted_peak_reported_velocity_m_s=peak_velocity,
              final_maximum_reported_velocity_m_s=final_velocity,
              accepted_peak_area_average_velocity_m_s=peak_average_velocity,
              final_area_average_velocity_m_s=final_average_velocity,
              frozen_native_scalar_histories=['v2-total-liquid-mass','v2-flux-phase2-steamoutlet','v2-flux-phase1-steamoutlet'],
              all_film_parameters_match_expected=True, physical_validation=False)
q.r.dump(b/'verification.json',result)
print(json.dumps(result,indent=2))
