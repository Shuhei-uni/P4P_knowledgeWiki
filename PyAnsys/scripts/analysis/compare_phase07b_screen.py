"""Reproduce G1 comparisons from the five fixed Phase 7b evidence records.

No solver calls. S100's N4000 recovery fields are explicitly asynchronous with
four N5000 snapshots; failed terminal records are never pooled into late means.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
from analyze_phase07b_screen import parse_history,derive,parse_flux,parse_residuals,plt
from matplotlib.collections import PolyCollection
from plot_phase07b_sections import SECTIONS

BASE=Path(__file__).resolve().parents[2]
RUNS=['p7b-s020-20260920T221831Z','p7b-s040-20260921T013001Z',
      'p7b-s060-resume-20260921T113238Z','p7b-s080-20260921T130348Z','p7b-s100-20260921T160825Z']

def main():
 out=BASE/'output/phase07b-g1';out.mkdir(exist_ok=True)
 records={};data={};colors=plt.get_cmap('tab10').colors
 for case,run in zip(['S20','S40','S60','S80','S100'],RUNS):
  p=BASE/'output'/run
  h,a=max([parse_history(f) for f in p.glob('history-*.out')],key=lambda pair:pair[1]['last_iteration'])
  d,u=derive(h);x=h['iteration'];data[case]=(x,d)
  summary=json.loads((p/'analysis/summary.json').read_text())
  expected=4182 if case=='S100' else 5000
  for stream in ['history','collector_flux','residuals']:
   assert summary[stream]['complete_to_expected_end'],(case,stream)
   assert summary[stream]['last_iteration']==expected
  assert not summary['missing_required_derived_metrics']
  at=np.flatnonzero(x==4000)[0]
  record={'run':run,'source_history':a['source'],'analysis_sha256':hashlib.sha256((p/'analysis/summary.json').read_bytes()).hexdigest(),
    'last_completed_iteration':expected,'disposition':'NUMERICAL_FAILURE_ATTEMPTED_4183' if case=='S100' else 'HORIZON_COMPLETE_NUMERICAL_CRITERIA_FAILED',
    'n4000_metrics':{k:float(v[at]) for k,v in d.items()},
    'late_4501_5000':summary['fixed_late_windows']['windows']['4501-5000'],
    'screening_indicators':summary['declared_screening_indicators'],
    'spatial_stage':'checkpoint-04000' if case=='S100' else 'final',
    'spatial_iteration':4000 if case=='S100' else 5000,
    'latest_metrics':summary['latest_metrics'] if case!='S100' else None}
  records[case]=record
 # Common interval is deliberately separate from terminal and late-window evidence.
 fig,axes=plt.subplots(3,1,figsize=(10,9),sharex=True,layout='constrained')
 for i,(case,(x,d)) in enumerate(data.items()):
  select=x<=4000
  for ax,metric in zip(axes,['whole_water_volume','native_applied_removal','liquid_closure_percent_feed']):
   ax.plot(x[select],d[metric][select],label=case,color=colors[i],lw=.8)
 for ax,label in zip(axes,['Liquid volume (m³)','Applied removal (kg/s)','Liquid closure (% feed)']):
  ax.set_ylabel(label);ax.grid(alpha=.2)
 axes[0].legend(ncol=5);axes[1].axhline(records['S20']['n4000_metrics']['liquid_measured_feed'],color='black',ls=':',lw=1,label='Liquid feed')
 axes[1].legend();axes[2].axhline(0,color='black',lw=.5);axes[2].set_xlabel('Steady iteration (not physical time)')
 fig.suptitle('G1 — Matched N1–4000 history comparison\nRaw records; later histories and S100 failure are assessed separately')
 fig.savefig(out/'G1-common-history.png',dpi=160);plt.close(fig)
 fig,axes=plt.subplots(3,1,figsize=(10,9),sharex=True,layout='constrained')
 for i,(case,(x,d)) in enumerate(data.items()):
  if case=='S100':continue
  select=x>=4001
  for ax,metric in zip(axes,['whole_water_volume','native_applied_removal','liquid_closure_percent_feed']):
   ax.plot(x[select],d[metric][select],label=case,color=colors[i],lw=.8)
 for ax,label in zip(axes,['Liquid volume (m³)','Applied removal (kg/s)','Liquid closure (% feed)']):
  ax.set_ylabel(label);ax.grid(alpha=.2);ax.axvline(4500.5,color='black',ls='--',lw=.7)
 axes[0].legend(ncol=4);axes[1].axhline(records['S20']['n4000_metrics']['liquid_measured_feed'],color='black',ls=':',lw=1)
 axes[2].axhline(0,color='black',lw=.5);axes[2].set_xlabel('Steady iteration (not physical time)')
 fig.suptitle('G1 — Completed cases retain drift and open mass balance\nRaw N4001–5000; S100 has no complete prescribed late window')
 fig.savefig(out/'G1-late-history.png',dpi=160);plt.close(fig)
 # Identical scales/surfaces, explicit differing snapshot indices.
 fields=[('phase-2-vof','Liquid volume fraction',0,1),('velocity-magnitude','Mixture speed (m/s)',0,80),('phase-2-velocity-magnitude','Liquid speed (m/s)',0,80)]
 for field,title,lo,hi in fields:
  fig,axes=plt.subplots(4,5,figsize=(13,10),layout='constrained',sharex=True,sharey=True)
  for col,(case,r) in enumerate(records.items()):
   p=BASE/'output'/r['run']/(r['spatial_stage']+'-sections')
   index=json.loads((p/'index.json').read_text())
   for row,(name,height) in enumerate(SECTIONS):
    path=p/index['sections'][name]['file']
    with np.load(path) as f:
     vertices=f['vertices'];sizes=f['face_sizes'];conn=f['connectivity'];values=f[field]
     assert np.isfinite(values).all() and values.min()>=lo-1e-7 and values.max()<=hi+1e-7
     assert np.allclose(vertices[:,1],height,atol=2e-6,rtol=0)
     offsets=np.r_[0,np.cumsum(sizes)];polys=[vertices[conn[offsets[i]:offsets[i+1]]][:,[0,2]] for i in range(len(sizes))]
     ax=axes[row,col];collection=PolyCollection(polys,array=values,cmap='viridis',clim=(lo,hi),edgecolors='none',antialiased=False,rasterized=True)
     ax.add_collection(collection);ax.autoscale_view();ax.set_aspect('equal')
     if row==0:ax.set_title(f'{case} | N{r["spatial_iteration"]}'+('\nrecovery checkpoint' if case=='S100' else '\ncompleted horizon'),fontsize=10)
     if col==0:ax.set_ylabel(f'y={height:g} m\nz (m)')
     if row==3:ax.set_xlabel('x (m)')
   r.setdefault('spatial_sources',[]).append({'field':field,'index':str(p/'index.json')})
  fig.colorbar(collection,ax=axes,location='bottom',shrink=.55,pad=.035,label=title)
  fig.suptitle(f'G1 — Above-collector {title.lower()}\nNative facet values; common scales; S100 N4000 is not a matched N5000 endpoint')
  fig.savefig(out/f'G1-spatial-{field}.png',dpi=160);plt.close(fig)
 result={'cases':records,'qualification':False,'rule':'No pooled S100 terminal/late means. Common histories N1–4000; four completed-case late windows; S100 separate failure evidence.',
         'figures':sorted(str(p) for p in out.glob('G1-*.png'))}
 (out/'comparison.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'output':str(out),'cases':list(records),'figures':len(result['figures'])}))

if __name__=='__main__':main()
