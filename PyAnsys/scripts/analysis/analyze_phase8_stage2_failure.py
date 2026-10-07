"""File-backed diagnosis of the F2 Stage 2 ramp failure."""
from pathlib import Path
import json,re,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/phase8-stage2/20261007';FIG=ROOT.parent/'Project/experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/figures'
FULL_FEED='--full-feed3000' in sys.argv
if FULL_FEED:OUT=OUT/'full-feed3000';FIG=FIG.parent/'full-feed3000/figures'
FAILED=717 if FULL_FEED else 1422
SAVED=0 if FULL_FEED else 1000
VALID_END=700 if FULL_FEED else 1410
CHECKPOINTS=[100,300,500,600,680,700,710] if FULL_FEED else [1000,1300,1390,1400,1410,1420]
RESIDUAL_POINTS=[600,630,680,695,700,704,709,710,716] if FULL_FEED else [1000,1300,1390,1393,1400,1410,1414,1415,1421]
raw=json.loads((OUT/('host-report-histories.json' if FULL_FEED else 'raw/failure-report-histories.json')).read_text());row=re.compile(r'^\s*(\d+)\s+([-+\d.eE]+)\s*$',re.M)
h={k:{int(n):float(v) for n,v in row.findall(t)} for k,t in raw.items()}
ids=sorted(set.intersection(*(set(v) for v in h.values())));assert (600 in ids and 700 in ids) if FULL_FEED else (1000 in ids and 1400 in ids)
for k,v in h.items():assert all(np.isfinite(x) for x in v.values()),k
def v(k,n):return h['p8-'+k][n]
def metric(n):
 flows={p:v('flux-'+p+'-liquidinlet',n)+v('flux-'+p+'-steaminlet',n) for p in ['mixture','phase1','phase2']}
 outputs={p:-v('flux-'+p+'-steamoutlet',n) for p in flows}
 return {'iteration':n,'liquid_feed_kg_s':flows['phase2'],'liquid_outlet_kg_s':outputs['phase2'],'liquid_outlet_percent_feed':100*outputs['phase2']/flows['phase2'],'liquid_inventory_kg':v('mass-phase2-total',n),'lower_liquid_inventory_kg':v('mass-phase2-lower',n),'signed_boundary_gap_percent_feed':{p:100*(flows[p]-outputs[p])/flows[p] for p in flows},'steam_face_pressure_minus_outlet_kPa':(v('pressure-steaminlet',n)-v('pressure-steamoutlet',n))/1000}
transcript=(OUT/'raw/host-native-transcript.txt').read_text();pattern=re.compile(r'^\s*(\d+)\s+((?:\d+\.\d+e[+-]\d+\s+){6}\d+\.\d+e[+-]\d+)',re.M|re.I)
res={int(n):list(map(float,text.split())) for n,text in pattern.findall(transcript)}
summary={'status':f'FAILED_AT_N{FAILED}_DIAGNOSED_FROM_HISTORIES','saved_checkpoint':SAVED,'failure_native_iteration':FAILED,'feed_at_failure':1. if FULL_FEED else .625,'nominal_speed_label_at_failure_m_s':26.81*(1. if FULL_FEED else .625),'report_coordinates':[min(ids),max(ids)],'checkpoints':{str(n):metric(n) for n in CHECKPOINTS if n in ids},'residuals':{str(n):dict(zip(['continuity','u','v','w','k','epsilon','liquid_fraction'],res[n])) for n in RESIDUAL_POINTS if n in res},'warning_counts':{'reverse_flow_messages':transcript.count('Reversed flow'),'viscosity_limit_messages':transcript.count('turbulent viscosity limited')},'claim_limits':['N1000 is a pre-ramp finite checkpoint, not a converged state','No saved N1400 field; histories do not locate the onset cell','N1422 failed-state fields are diagnostic only','Ramp-associated failure is not proof that inlet speed alone caused the error','Closed bottom and no removal path; no separation efficiency or stationary pool claim']}
window=[n for n in ids if (500 if FULL_FEED else 900)<=n<=(600 if FULL_FEED else 1000)];summary['N500_N600_liquid_inventory_slope_kg_per_iteration' if FULL_FEED else 'N900_N1000_liquid_inventory_slope_kg_per_iteration']=float(np.polyfit(window,[v('mass-phase2-total',n) for n in window],1)[0])
FIG.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.25})
ns=np.array(sorted(res));values=np.array([res[n] for n in ns])
fig,axes=plt.subplots(2,1,figsize=(8,6))
for ax,limits in zip(axes,[(0,709),(680,717)] if FULL_FEED else [(0,1414),(1390,1422)]):
 for index,label in [(0,'Continuity'),(4,'k'),(5,'epsilon'),(6,'Liquid fraction')]:ax.semilogy(ns[ns<=limits[1]],values[ns<=limits[1],index],label=label,linewidth=.8)
 ax.set_xlim(*limits);ax.set_ylabel('Scaled residual');ax.axvline(710 if FULL_FEED else 1400,color='tab:red',ls='--');ax.set_xlabel('Native steady iteration')
axes[0].legend(ncol=4);fig.suptitle('F2 SIMPLE: full-feed failure at N717; turbulence spikes before blow-up' if FULL_FEED else 'F2 SIMPLE: ramp failure at N1422; residual rise starts before N1400');fig.tight_layout();fig.savefig(FIG/'failure-residuals.png',dpi=160);plt.close(fig)
coords=[n for n in ids if n<=VALID_END];metrics=[metric(n) for n in coords]
fig,axes=plt.subplots(3,1,figsize=(8,7),sharex=True)
axes[0].plot(coords,[m['liquid_feed_kg_s'] for m in metrics],label='Liquid inlet');axes[0].plot(coords,[m['liquid_outlet_kg_s'] for m in metrics],label='Liquid at steam outlet');axes[0].set_ylabel('Liquid flow (kg/s)');axes[0].legend()
axes[1].plot(coords,[m['liquid_inventory_kg'] for m in metrics],label='Whole separator');axes[1].plot(coords,[m['lower_liquid_inventory_kg'] for m in metrics],label='Lower 0.1 m region');axes[1].set_ylabel('Liquid inventory (kg)');axes[1].legend()
for p,label in [('mixture','Native mixture'),('phase1','Vapor'),('phase2','Liquid')]:axes[2].plot(coords,[m['signed_boundary_gap_percent_feed'][p] for m in metrics],label=label)
axes[2].set_ylabel('Boundary gap (% feed)');axes[2].legend();axes[2].set_xlabel('Native steady iteration')
for ax in axes:ax.axvline(FAILED,color='tab:red',ls='--');ax.set_xlim(0,FAILED)
fig.suptitle('F2 SIMPLE full-feed histories through N700; N710 onset sample excluded' if FULL_FEED else 'F2 SIMPLE histories through N1410; divergent N1420 sample excluded');fig.tight_layout();fig.savefig(FIG/'failure-routing-inventory.png',dpi=160);plt.close(fig)
if FULL_FEED:summary['claim_limits']=['No pre-failure checkpoint after fresh N0','N717 failed fields are diagnostic only','Finite report values through N700 do not establish a converged state','Full-feed failure shows a ramp is not required; root cause remains unlocated','Closed bottom has no liquid-removal path; no stationary separation claim']
(OUT/'failure-analysis.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
