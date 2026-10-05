"""Compare the two saved scale-0.1 starts without treating iterations as physical time."""
from pathlib import Path
import json,sys,os
import numpy as np
from analyze_phase07b_screen import parse_history,parse_residuals
os.environ.setdefault('MPLCONFIGDIR','/tmp/p9-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
BASE=Path(__file__).resolve().parents[2]
out=BASE/'output/phase09/comparison';out.mkdir(exist_ok=True)
result={};series={}
for label,directory,height in [('low','recovery-screen',.1),('high','high-pool-screen',.3)]:
 tables=[];residuals=[];faces=[];sources=[]
 for stage in ['smoke','continuation']:
  receipt=BASE/'output/phase09-preflight'/directory/(stage+'-receipt.json');p=Path(json.loads(receipt.read_text())['run_manifest']);r=json.loads(p.read_text());assert r['status']=='BLOCK_COMPLETE' and r['pair_exists']
  h,ha=parse_history(p.parent/'native-history.out');v,va=parse_residuals(p.parent/'native-transcript.trn');assert not ha['conflicting_indices'] and not va['conflicting_indices'];tables.append(h);residuals.append(v);faces.append([json.loads(x) for x in (p.parent/'iteration-evidence.jsonl').read_text().splitlines()]);sources.append({'manifest':str(p),'history':ha['source'],'residuals':va['source']})
  if stage=='smoke':initial=r['initial_fields']['liquid_mass_kg']
 for group in [tables,residuals]:
  for k in group[0]:
   if k=='iteration':continue
   assert np.allclose(group[0][k][group[0]['iteration']==50],group[1][k][group[1]['iteration']==50],rtol=1e-10,atol=1e-10),(label,k)
 def stitch(group):return {k:np.concatenate([group[0][k][group[0]['iteration']<=50],group[1][k][group[1]['iteration']>50]]) for k in group[0]}
 h=stitch(tables);v=stitch(residuals);flux=faces[0]+[x for x in faces[1] if x['iteration']>50]
 assert list(h['iteration'])==list(v['iteration'])==[x['iteration'] for x in flux]==list(range(1,1001))
 b={'height_m':height,'sources':sources,'samples':1000,'initial_liquid_kg':initial,'final_liquid_kg':float(h['p9liquidmass'][-1]),'inventory_change_from_N0_pct':float(100*(h['p9liquidmass'][-1]/initial-1)),'closure':{},'inventory':{},'routing':{},'residuals':{},'qualified':False}
 for k,feed in [('l',h['p9lli']),('v',h['p9vvi']),('m',h['p9mli']+h['p9mvi'])]:
  err=100*abs(h['p9'+k+'net'])/feed;b['closure'][k]={'mean_absolute_pct':float(err.mean()),'max_absolute_pct':float(err.max()),'final_absolute_pct':float(err[-1]),'pass':bool(err.mean()<=.5 and err.max()<=1)}
 for k in ['p9liquidmass','p9lowerliquid','p9upperliquid']:
  a=h[k];mean=a.mean();b['inventory'][k]={'final_kg':float(a[-1]),'range_pct':float(100*np.ptp(a)/mean),'half_mean_change_pct':float(100*(a[500:].mean()-a[:500].mean())/mean),'last_200_change_kg':float(a[-1]-a[-200])}
 for k,values in v.items():
  if k!='iteration':b['residuals'][k]={'max':float(values.max()),'final':float(values[-1]),'pass':bool(values.max()<=1e-3)}
 for phase,k,dest,feed in [('phase-2','l','bo',h['p9lli']),('phase-1','v','so',h['p9vvi'])]:
  b['routing'][k]={'desired_net_outflow_final_pct':float(-100*h['p9'+k+dest][-1]/feed[-1]),'reverse_inflow_max_pct':{face:float(100*max(-x['flux'][phase][face]['negative_sum']/feed[i] for i,x in enumerate(flux))) for face in ['brine-outlet','steam-outlet']}}
 f=np.load(p.parent/'fields-n01000.npz');y=f['mixture_SV_CENTROID'].reshape(-1,3)[:,1];a=f['phase-2_SV_VOF'];vol=f['mixture_SV_VOLUME'];q=(y>=-.51)&(y<0);b['drain_band_liquid_occupancy']=float(np.dot(a[q],vol[q])/vol[q].sum())
 b['native_mixture_phase_sum_max_error_kg_s']=float(np.max(abs(h['p9lnet']+h['p9vnet']-h['p9mnet'])))
 result[label]=b;series[label]=(h,v,initial)
result['claim_limit']='Both trajectories are unconverged. Matched iteration is not matched physical time or established common steady equilibrium. No qualified parent or physical impossibility claim.'
(out/'two-start-comparison.json').write_text(json.dumps(result,indent=2))
fig,axs=plt.subplots(3,1,figsize=(10,9),layout='constrained')
for label,color,style in [('low','#2C8ED2','-'),('high','#FC8500','--')]:
 h,v,initial=series[label];name=f"Initial pool {result[label]['height_m']:.2f} m"
 axs[0].plot(h['iteration'],100*abs(h['p9lnet'])/h['p9lli'],color=color,ls=style,label=name)
 axs[1].plot(h['iteration'],100*(h['p9liquidmass']/initial-1),color=color,ls=style,label=name)
 axs[2].semilogy(v['iteration'],v['continuity'],color='#46D2BA',ls=style,label=name)
axs[0].set_ylabel('Absolute liquid imbalance (% feed)');axs[0].axhline(.5,color='grey',lw=.7);axs[1].set_ylabel('Liquid inventory change from N0 (%)');axs[2].set_ylabel('Scaled continuity residual');axs[2].axhline(1e-3,color='grey',lw=.7);axs[2].set_xlabel('Native steady iteration (not physical time)')
for ax in axs:ax.legend(fontsize=8)
fig.suptitle('Phase 9 — two initial pools, same scale 0.1 and downstream head\nNeither trajectory satisfies steady acceptance')
fig.savefig(out/'two-start-comparison.png',dpi=160);plt.close(fig)
print(json.dumps({k:{q:v[q] for q in ['initial_liquid_kg','final_liquid_kg','inventory_change_from_N0_pct','drain_band_liquid_occupancy']} for k,v in result.items() if isinstance(v,dict)},indent=2))
