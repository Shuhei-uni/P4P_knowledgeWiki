"""Offline G3 comparison and snapshot verification; no Fluent connection."""
from pathlib import Path
import argparse,csv,hashlib,json
from datetime import datetime,timezone
import numpy as np
from analyze_phase07b_screen import analyze,parse_history,parse_residuals,derive,plt
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from pyansys_fluent.phase07b_spike_monitor import SpikeSchedule

BASE=Path(__file__).resolve().parents[2]
ORIGINAL=BASE/'output/p7b-s40-t020-resume-20260921T231240Z'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--refresh',action='store_true');args=ap.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=args.refresh)
 runs=[('Original T020',ORIGINAL),('Diagnostic T020',args.run)];parsed=[];summary={}
 for label,run in runs:
  m=json.loads((run/'manifest.json').read_text());assert m['completed_iterations']==5000 and m['status']=='HORIZON_COMPLETE_ANALYSIS_PENDING'
  s=analyze(run,run/'analysis',render_sections=False)
  assert all(s[k]['complete_to_expected_end'] for k in ['history','collector_flux','residuals'])
  assert not s['missing_required_derived_metrics'];h,_=parse_history(Path(s['history']['source']['path']));r,_=parse_residuals(run/'solve.trn');v,units=derive(h);parsed.append((h,r,v))
  summary[label]={'run_id':run.name,'source_summary':str(run/'analysis/summary.json'),'indicators':s['declared_screening_indicators'],'source_lag':s['applied_source_lag_audit'],'latest':s['latest_metrics'],'late_windows':s['fixed_late_windows'],'residual_late_windows':s['residual_fixed_late_windows']}
  csvpath=out/('original-history.csv' if run==ORIGINAL else 'diagnostic-history.csv')
  with csvpath.open('w') as f:
   w=csv.writer(f);names=['iteration',*v,*[f'residual_{k}' for k in r if k!='iteration']];w.writerow(names)
   assert np.array_equal(h['iteration'],r['iteration'])
   for i,n in enumerate(h['iteration']):w.writerow([int(n),*[float(a[i]) for a in v.values()],*[float(a[i]) for k,a in r.items() if k!='iteration']])
  windows=[]
  for lo,hi in [(2201,2700),(2701,3200),(3201,3700),(3701,4200),(4201,4500),(4501,5000)]:
   sel=(r['iteration']>=lo)&(r['iteration']<=hi);speed=v['maximum_mixture_speed'][sel];eps=r['epsilon'][sel]
   windows.append({'start':lo,'end':hi,'epsilon_median':float(np.median(eps)),'epsilon_p95':float(np.percentile(eps,95)),'epsilon_max':float(max(eps)),'speed_max_m_s':float(max(speed)),'speed_ge500_count':int(sum(speed>=500))})
  peak=int(np.argmax(v['maximum_mixture_speed']));summary[label]['onset_windows']=windows;summary[label]['peak_speed']={'iteration':int(h['iteration'][peak]),'value_m_s':float(v['maximum_mixture_speed'][peak])};summary[label]['first_speed_ge500']=next((int(n) for n,vv in zip(h['iteration'],v['maximum_mixture_speed']) if vv>=500),None)
 ddir=args.run/'spike-diagnostics';d=json.loads((ddir/'manifest.json').read_text());assert d['error'] is None and d['last_iteration']==5000
 speed=[json.loads(x) for x in (ddir/'spike-history.jsonl').read_text().splitlines()];assert [x['iteration'] for x in speed]==list(range(1,5001));schedule=SpikeSchedule();expected={0}
 for row in speed:
  reasons=schedule.reasons(row['iteration'],row['max_speed_m_s']);assert reasons==row['snapshot_reasons']
  if reasons:expected.add(row['iteration'])
 assert expected=={x['iteration'] for x in d['snapshots']};assert np.allclose([x['max_speed_m_s'] for x in speed],parsed[1][2]['maximum_mixture_speed'],rtol=1e-12,atol=1e-10)
 geo=np.load(ddir/'geometry.npz');events=[];snapshots=[]
 for item in d['snapshots']:
  n=item['iteration'];path=ddir/f'fields-n{n:05}.npz';meta=json.loads(path.with_suffix('.json').read_text());digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==meta['sha256']==item['sha256'];assert meta['iteration']==n and meta['same_iteration_before_after']
  with np.load(path) as a:
   maxima={'speed':[],'k':[],'epsilon':[]};water=0;top=[]
   assert all(np.isfinite(a[k]).all() for k in a.files)
   for z in range(2):
    pre=f'z{z}_mixture_';v=np.sqrt(sum(a[pre+'SV_'+s]**2 for s in 'UVW'));k=a[pre+'SV_K'];eps=a[pre+'SV_D'];alpha=a[f'z{z}_phase-2_SV_VOF'];xyz=geo[pre+'SV_CENTROID'].reshape(-1,3)
    assert len(v)==len(geo[pre+'SV_VOLUME']);water+=float(np.dot(alpha,geo[pre+'SV_VOLUME']))
    for key,arr in [('speed',v),('k',k),('epsilon',eps)]:maxima[key].append(float(max(arr)))
    i=int(np.argmax(v));top.append({'zone':meta['zones'][z],'array_index':i,'xyz_m':xyz[i].tolist(),'speed_m_s':float(v[i]),'alpha_l':float(alpha[i]),'pressure_Pa':float(a[pre+'SV_P'][i]),'k_m2_s2':float(k[i]),'epsilon_m2_s3':float(eps[i])})
   reduced={k:max(v) for k,v in maxima.items()};reduced['water']=water
   assert all(np.isclose(reduced[k],meta['native'][k],rtol=1e-10,atol=1e-10) for k in reduced)
  best=max(top,key=lambda x:x['speed_m_s']);best.update(iteration=n,reasons=item['reasons'],sha256=digest,native=meta['native'],outside_collector=best['xyz_m'][1]>-.8827502413)
  if n:best['epsilon_residual']=float(parsed[1][1]['epsilon'][n-1])
  snapshots.append(best)
  if any('speed_ge' in x or 'followup' in x for x in item['reasons']):events.append(best)
 summary['snapshot_audit']={'status':'PASS','count':len(snapshots),'iterations':sorted(expected),'geometry_sha256':hashlib.sha256((ddir/'geometry.npz').read_bytes()).hexdigest(),'snapshots':snapshots,'events':events,'all_finite':True,'native_parity':True,'schedule_replay':True,'raw_mass_imbalance_calibrated':False}
 fig,axs=plt.subplots(4,2,figsize=(13,11),constrained_layout=True,sharex=True)
 names=[k for k in parsed[0][1] if k!='iteration']+['maximum_mixture_speed']
 for ax,name in zip(axs.flat,names):
  for (label,_),(h,r,v),color in zip(runs,parsed,['#586c85','#ba4c2f']):
   vals=v[name] if name in v else r[name];ax.plot(h['iteration'],vals,label=label,color=color,lw=.65,alpha=.9)
  ax.set_yscale('log');ax.set_title(name.replace('_',' '),fontsize=10);ax.axvline(2700,color='#777777',ls=':',lw=.7);ax.axvline(4284,color='#aa6699',ls='--',lw=.7);ax.grid(alpha=.15)
  ax.set_ylabel('m/s' if name=='maximum_mixture_speed' else 'Native scaled residual')
 for ax in axs[-1]:ax.set_xlabel('Steady iteration')
 triggers=[x for x in events if any('speed_ge' in reason for reason in x['reasons'])]
 for name,ax in [('epsilon',axs[2,1]),('maximum_mixture_speed',axs[3,1])]:
  ax.scatter([x['iteration'] for x in triggers],[x['epsilon_residual'] if name=='epsilon' else x['speed_m_s'] for x in triggers],facecolors='none',edgecolors='#167b52',s=45,zorder=5,label='Captured trigger')
  ax.legend(fontsize=7)
 axs[0,0].legend(fontsize=8);fig.suptitle('G3 — Raw original and diagnostic histories\nDotted: N2700 observation; dashed: diagnostic controller recovery at N4284',fontsize=12);fig.savefig(out/'G3-residual-speed-comparison.png',dpi=150);plt.close(fig)
 fig,axs=plt.subplots(3,2,figsize=(13,9),constrained_layout=True,sharex=True)
 for j,((label,_),(h,r,v)) in enumerate(zip(runs,parsed)):
  axs[0,j].plot(h['iteration'],v['whole_water_volume'],lw=.8);axs[0,j].set_title(label);axs[0,j].set_ylabel('Liquid volume (m³)')
  axs[1,j].plot(h['iteration'],v['native_applied_removal'],lw=.8,label='Native applied removal');axs[1,j].plot(h['iteration'],v['current_expression_removal'],lw=.5,alpha=.65,label='Current expression');axs[1,j].axhline(116.9212324585,ls=':',color='black',label='Liquid feed');axs[1,j].set_ylabel('Removal (kg/s)');axs[1,j].legend(fontsize=7)
  for phase in ['liquid','vapor','mixture']:axs[2,j].plot(h['iteration'],v[phase+'_closure_percent_feed'],lw=.65,label=phase)
  axs[2,j].set_ylabel('Source-inclusive closure (% feed)');axs[2,j].set_xlabel('Steady iteration');axs[2,j].legend(fontsize=7)
 for ax in axs.flat:ax.grid(alpha=.15)
 for row in axs:
  lo=min(ax.get_ylim()[0] for ax in row);hi=max(ax.get_ylim()[1] for ax in row)
  for ax in row:ax.set_ylim(lo,hi)
 fig.suptitle('G3 — Raw inventory, removal and conservation\nSource counted once; iteration slope is not physical storage',fontsize=12);fig.savefig(out/'G3-inventory-source-closure.png',dpi=150);plt.close(fig)
 summary.update(generated_utc=datetime.now(timezone.utc).isoformat(),status='HISTORIES_AND_SNAPSHOTS_COMPLETE_NATIVE_GRAPHICS_PENDING',claim_limit='Replication with instrumentation and recovered controller interruption; not bitwise trajectory replication, physical convergence or causal isolation.')
 (out/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:{x:v[x] for x in ['indicators','peak_speed','first_speed_ge500','onset_windows']} for k,v in summary.items() if k in [x[0] for x in runs]},indent=2))
if __name__=='__main__':main()
