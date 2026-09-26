from pathlib import Path
import sys,json,hashlib,re,argparse
import numpy as np
sys.path[:0]=['PyAnsys/scripts/analysis','PyAnsys/src']
from analyze_phase07b_screen import parse_history,parse_residuals,derive
from pyansys_fluent.phase07b_spike_monitor import SpikeSchedule

def snapshot_fractions(fields, geometry, zone, iteration, nphase):
 raw=fields[f'z{zone}_phase-2_SV_VOF'];alpha=raw
 result={'raw_liquid_volume_m3':float(np.dot(raw,geometry[f'z{zone}_mixture_SV_VOLUME']))}
 if nphase:
  key=f'z{zone}_phase-1_SV_VOF'
  if key not in fields:
   assert iteration==0 and np.all(raw==0), 'Primary raw fraction missing outside immutable N0'
   result['raw_phase_sum_available']=False
  else:
   total=raw+fields[key];assert np.isfinite(total).all() and (total>0).all()
   alpha=raw/total
   result.update(raw_phase_sum_available=True,raw_phase_sum_min=float(total.min()),
                 raw_phase_sum_max=float(total.max()),raw_phase_sum_max_abs_defect=float(np.max(np.abs(total-1))))
 result['comparison_liquid_volume_m3']=float(np.dot(alpha,geometry[f'z{zone}_mixture_SV_VOLUME']))
 result['comparison_basis']='cellwise_normalized_raw_phase_vector' if nphase else 'raw_secondary_fraction'
 return alpha,result

ap=argparse.ArgumentParser();ap.add_argument('--experiment',choices=['E4','E5','E6','E7'],default='E4');ap.add_argument('--child',type=Path);a=ap.parse_args()
out=Path('PyAnsys/output/phase07b-g'+a.experiment[1:]);records={}
cases=[('SIMPLE','p7b-s40-t020-resume-20260921T231240Z'),('Coupled-Off','p7b-s40-t020-coupled-off-20260922T134224Z')] if a.experiment=='E4' else [('Coupled-CFL200','p7b-s40-t020-coupled-off-20260922T134224Z'),('Coupled-CFL20','p7b-s40-t020-coupled-cfl20-20260922T202845Z')]
if a.experiment in ['E6','E7']:
 assert a.child and a.child.parent==Path('PyAnsys/output')
 manifest=json.loads((a.child/'manifest.json').read_text());assert manifest['experiment_id']==a.experiment and manifest['completed_iterations']==5000
 cases=([('Coupled-CFL20','p7b-s40-t020-coupled-cfl20-20260922T202845Z'),('Coupled-CFL20-NPhase',a.child.name)] if a.experiment=='E6' else [('NPhase-T020','p7b-s40-t020-coupled-cfl20-nphase-resume-20260923T231816Z'),('NPhase-T100',a.child.name)])
for label,name in cases:
 run=Path('PyAnsys/output')/name;h,_=parse_history(run/'history-05000.out');r,_=parse_residuals(run/'solve.trn');d,_=derive(h);windows=[]
 for lo,hi in [(2201,2700),(2701,3200),(3201,3700),(3701,4200),(4201,4500),(4501,5000)]:
  sel=(h['iteration']>=lo)&(h['iteration']<=hi);v=d['maximum_mixture_speed'][sel];e=r['epsilon'][sel];vapor=d['vapor_closure_percent_feed'][sel]
  windows.append(dict(start=lo,end=hi,epsilon_median=float(np.median(e)),epsilon_p95=float(np.percentile(e,95)),epsilon_max=float(max(e)),speed_max_m_s=float(max(v)),speed_ge500_count=int(sum(v>=500)),vapor_error_lag1_correlation=float(np.corrcoef(vapor[:-1],vapor[1:])[0,1])))
 trn=(run/'solve.trn').read_text();limited=[int(v) for v in re.findall(r'turbulent viscosity limited to viscosity ratio of [\d.e+\-]+ in\s+(\d+) cells',trn)]
 records[label]={'run':str(run),'onset_windows':windows,'viscosity_limit_messages':len(limited),'maximum_limited_cells':max(limited,default=0),'reverse_flow_messages':trn.count('Reversed flow'),'late_means':{k:float(np.mean(v[-500:])) for k,v in d.items()},'peak_speed_iteration':int(h['iteration'][np.argmax(d['maximum_mixture_speed'])]),'peak_speed_m_s':float(max(d['maximum_mixture_speed']))}
 if label==cases[-1][0]:
  dd=run/'spike-diagnostics';dm=json.loads((dd/'manifest.json').read_text());rows=[json.loads(x) for x in (dd/'spike-history.jsonl').read_text().splitlines()];schedule=SpikeSchedule();expected={0}
  for row in rows:
   reasons=schedule.reasons(row['iteration'],row['max_speed_m_s']);assert reasons==row['snapshot_reasons']
   if reasons:expected.add(row['iteration'])
  actual={x['iteration'] for x in dm['snapshots']};assert len(actual)==len(dm['snapshots'])
  extra=actual-expected
  assert extra <= ({55} if a.experiment=='E6' else set()) and expected<=actual
  for item in dm['snapshots']:
   if item['iteration'] in extra:assert item['reasons']==['recovery_semantics_validation']
  assert np.allclose([x['max_speed_m_s'] for x in rows],d['maximum_mixture_speed'],rtol=1e-12)
  snaps=[]
  with np.load(dd/'geometry.npz') as geo:
   for item in dm['snapshots']:
    meta=json.loads(Path(item['path']).with_suffix('.json').read_text());candidates=[];fraction_checks=[]
    with np.load(item['path']) as f:
     for z in range(2):
      speed=np.sqrt(sum(f[f'z{z}_mixture_SV_{axis}']**2 for axis in 'UVW'));idx=int(np.argmax(speed));xyz=geo[f'z{z}_mixture_SV_CENTROID'].reshape(-1,3)[idx]
      alpha,check=snapshot_fractions(f,geo,z,item['iteration'],a.experiment in ['E6','E7']);check['zone']=meta['zones'][z];fraction_checks.append(check)
      candidates.append({'zone':meta['zones'][z],'index':idx,'xyz_m':xyz.tolist(),'speed_m_s':float(speed[idx]),'alpha_l':float(alpha[idx]),'alpha_l_raw':float(f[f'z{z}_phase-2_SV_VOF'][idx]),'alpha_l_basis':check['comparison_basis']})
    reconstructed=sum(x['comparison_liquid_volume_m3'] for x in fraction_checks)
    assert np.isclose(reconstructed,meta['native']['water'],rtol=1e-9,atol=1e-12), ('Snapshot native inventory parity',item['iteration'])
    snaps.append({'iteration':item['iteration'],'reasons':item['reasons'],'maximum':max(candidates,key=lambda v:v['speed_m_s']),'phase_fraction_evidence':fraction_checks,'native_liquid_volume_m3':meta['native']['water'],'reconstructed_minus_native_volume_m3':reconstructed-meta['native']['water']})
  records['diagnostics']={'schedule_replay':'PASS','speed_scalar_parity':'PASS','snapshot_maxima':snaps,'trigger_count':sum(any('speed_ge' in v for v in x['reasons']) for x in dm['snapshots']),'raw_mass_imbalance_calibrated':False}
  section_audit=[]
  for folder in ['initial-sections','initial-axial-sections','final-sections','final-axial-sections']:
   index=json.loads((run/folder/'index.json').read_text());assert len(index['fields'])==10
   for name,info in index['sections'].items():
    path=run/folder/info['file']
    with np.load(path) as f:assert all(np.isfinite(f[k]).all() for k in f.files)
    section_audit.append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'facets':info['facets']})
  records['sections']={'status':'PASS','arrays':section_audit}
(out/'diagnostic-comparison.json').write_text(json.dumps(records,indent=2,allow_nan=False)+'\n')
for k,_ in cases:print(k,json.dumps({v:records[k][v] for v in ['onset_windows','viscosity_limit_messages','maximum_limited_cells','reverse_flow_messages','peak_speed_m_s']}))
