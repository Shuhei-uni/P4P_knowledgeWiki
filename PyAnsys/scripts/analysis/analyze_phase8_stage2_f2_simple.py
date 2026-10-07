"""File-backed Stage 2 F2 carrier analysis; no Fluent calls or extra solves."""
from pathlib import Path
import json,re,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/phase8-stage2/20261007'
PROJECT=ROOT.parent/'Project/experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple'
FULL_FEED='--full-feed3000' in sys.argv
TARGET=3000 if FULL_FEED else 5000
if FULL_FEED:
 OUT=OUT/'full-feed3000';PROJECT=PROJECT/'full-feed3000'
ROW=re.compile(r'^\s*(\d+)\s+([-+\d.eE]+)\s*$',re.M)
RESIDUAL=re.compile(r'^\s*(\d+)\s+(\d+\.\d+e[+-]\d+)',re.M|re.I)

def main():
 manifest_path=OUT/('run-manifest.json' if (OUT/'run-manifest.json').exists() else 'host-run-manifest.json')
 manifest=json.loads(manifest_path.read_text())
 assert manifest['status']=='COMPLETE_VERIFIED_ANALYSIS_REQUIRED'
 assert manifest['verified_native_iteration']==TARGET and manifest['server_id']=='2'
 raw=json.loads((OUT/('report-histories.json' if (OUT/'report-histories.json').exists() else 'host-report-histories.json')).read_text())
 coordinates=np.arange(10,TARGET+1,10)
 reports={}
 for name,text in raw.items():
  history={int(i):float(v) for i,v in ROW.findall(text)}
  assert set(coordinates)<=history.keys(),name
  values=np.array([history[i] for i in coordinates]);assert np.isfinite(values).all(),name
  reports[name]=values
 def v(name):return reports['p8-'+name]
 inlet={p:v(f'flux-{p}-liquidinlet')+v(f'flux-{p}-steaminlet') for p in ['mixture','phase1','phase2']}
 outlet={p:-v(f'flux-{p}-steamoutlet') for p in inlet}
 gap={p:inlet[p]-outlet[p] for p in inlet}
 inventory=v('mass-phase2-total')
 pressure=(v('pressure-steaminlet')-v('pressure-steamoutlet'))/1000
 final=(coordinates>=TARGET-500)&(coordinates<=TARGET)
 def stats(x):return {'mean':float(x[final].mean()),'min':float(x[final].min()),'max':float(x[final].max())}
 windows=[]
 for start,end in ([(500,1000),(1500,2000),(2500,3000)] if FULL_FEED else [(2500,3000),(3500,4000),(4500,5000)]):
  mask=(coordinates>=start)&(coordinates<=end)
  windows.append({'window':[start,end],'liquid_inventory_start_end_kg':[float(inventory[mask][0]),float(inventory[mask][-1])],'inventory_slope_kg_per_iteration':float(np.polyfit(coordinates[mask],inventory[mask],1)[0])})
 transcript=(OUT/'raw/host-native-transcript.txt').read_text() if (OUT/'raw/host-native-transcript.txt').exists() else '\n'.join(Path(p).read_text() for p in manifest.get('transcript_files',[str(OUT/'raw/native-transcript.txt')]))
 residuals={int(i):float(v) for i,v in RESIDUAL.findall(transcript)}
 rcoords=np.array(sorted(i for i in residuals if 1<=i<=TARGET));rvalues=np.array([residuals[i] for i in rcoords])
 summary={'status':'ANALYSED_BOUNDED_CARRIER','native_window':[TARGET-500,TARGET],'samples':int(final.sum()),'source_manifest':str(manifest_path),'report_stride_iterations':10,'liquid_outlet_kg_s':stats(outlet['phase2']),'liquid_outlet_percent_feed':stats(100*outlet['phase2']/inlet['phase2']),'pressure_difference_steamface_to_outlet_kPa':stats(pressure),'terminal_report_liquid_inventory_kg':float(inventory[-1]),'late_inventory_windows':windows,'phase_balance_mean_absolute_percent_feed':{p:float(np.mean(100*np.abs(gap[p][final])/inlet[p][final])) for p in inlet},'residual_history':{'native_samples':len(rcoords),'missing_coordinates':sorted(set(range(1,TARGET+1))-set(rcoords))},'claim_limits':['One mesh and one speed; no mesh independence','Closed bottom and no liquid-removal path','Steady iterations are not physical time','Numerical completion is not physical validation']}
 if len(rcoords):summary['late_continuity_residual_range']=[float(rvalues[rcoords>=TARGET-500].min()),float(rvalues[rcoords>=TARGET-500].max())]
 figures=PROJECT/'figures';figures.mkdir(parents=True,exist_ok=True)
 plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.25})
 def phases(ax):
  for n in ([] if FULL_FEED else [1000,2000]):ax.axvline(n,color='0.5',linestyle='--',linewidth=.8)
  ax.set_xlim(0,TARGET);ax.set_xlabel('Native steady iteration')
 fig,axes=plt.subplots(3,1,figsize=(8,8),sharex=True)
 axes[0].plot(coordinates,inlet['phase2'],label='Liquid inlet');axes[0].plot(coordinates,outlet['phase2'],label='Liquid steam-outlet');axes[0].set_ylabel('Liquid flow (kg/s)');axes[0].legend()
 axes[1].plot(coordinates,inventory,color='tab:blue');axes[1].set_ylabel('Bulk liquid mass (kg)')
 for p,label in [('mixture','Native mixture'),('phase1','Vapor'),('phase2','Liquid')]:axes[2].plot(coordinates,100*gap[p]/inlet[p],label=label)
 axes[2].axhline(0,color='black',linewidth=.6);axes[2].set_ylabel('Signed boundary gap (% feed)');axes[2].legend()
 for ax in axes:phases(ax)
 fig.suptitle('F2–SIMPLE, 997,604 cells, nominal 26.81 m/s');fig.tight_layout();fig.savefig(figures/'routing-inventory-balance.png',dpi=160);plt.close(fig)
 fig,axes=plt.subplots(2,1,figsize=(8,5),sharex=True)
 axes[0].plot(coordinates,pressure);axes[0].set_ylabel('Steam-face − outlet\npressure (kPa)')
 if len(rcoords):axes[1].semilogy(rcoords,np.maximum(rvalues,1e-30),linewidth=.6)
 axes[1].set_ylabel('Scaled continuity residual')
 for ax in axes:phases(ax)
 fig.tight_layout();fig.savefig(figures/'pressure-continuity.png',dpi=160);plt.close(fig)
 (OUT/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
