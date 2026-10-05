"""Audit Phase 9 native evidence; do not infer physical storage from steady iterations."""
from pathlib import Path
import sys,json,os
import numpy as np
from analyze_phase07b_screen import parse_history,parse_residuals
os.environ.setdefault('MPLCONFIGDIR','/tmp/p9-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
COLORS={'continuity':'#46D2BA','x-velocity':'#A199D9','y-velocity':'#FA1900','z-velocity':'#2C8ED2','k':'#FC8500','epsilon':'#8BDD00','vf-phase-2':'#FB9DCD'}
p=Path(sys.argv[1]);r=json.loads((p/'run.json').read_text())
h,ha=parse_history(p/'native-history.out');res,ra=parse_residuals(p/'native-transcript.trn')
e=[json.loads(x) for x in (p/'iteration-evidence.jsonl').read_text().splitlines()]
assert list(h['iteration'])==list(range(r['first_capture'],r['end_iteration']+1))
assert [x['iteration'] for x in e]==list(h['iteration'])
assert not ha['conflicting_indices'] and not ha['nonfinite_columns']
assert not ra['conflicting_indices'] and not ra['nonfinite_columns']
assert set(res)=={'iteration','continuity','x-velocity','y-velocity','z-velocity','k','epsilon','vf-phase-2'}
assert np.isclose(r['terminal_fields']['liquid_mass_kg'],r['terminal_metrics']['p9liquidmass'],rtol=1e-10,atol=1e-8)
a={'history':ha,'residuals':ra,'mode':r['mode'],'status':r['status'],'iterations':r['end_iteration']-r['start_iteration'],'captured_samples':len(e),'qualified':False}
last=e[-1];m=r['terminal_metrics'];parity={}
for ph,key in [('mixture','m'),('phase-1','v'),('phase-2','l')]:
 for face,short in [('liquid-inlet','li'),('steam-inlet','vi'),('brine-outlet','bo'),('steam-outlet','so')]:
  f=last['flux'][ph][face]['signed_sum'];v=m['p9'+key+short]
  parity[ph+'/'+face]={'native_inward':v,'stored_flux_sum':f,'opposite_sign_error':float(abs(f+v))}
  assert np.isclose(f,-v,rtol=1e-6,atol=1e-7),parity[ph+'/'+face]
a['independent_flux_parity']=parity
a['liquid_inventory_initial_kg']=r['initial_fields']['liquid_mass_kg'];a['liquid_inventory_final_kg']=r['terminal_fields']['liquid_mass_kg'];a['liquid_inventory_change_pct']=100*(a['liquid_inventory_final_kg']/a['liquid_inventory_initial_kg']-1)
a['max_speed_final_m_s']=m['p9maxspeed']
a['phase_sum_max_error_kg_s']=float(np.max(abs(h['p9lnet']+h['p9vnet']-h['p9mnet'])))
if r['mode']=='rest':
 a['rest_gates']={'inventory':abs(a['liquid_inventory_change_pct'])<=.1,'brine_flow':abs(m['p9lbo'])<=1.16921233,'speed':m['p9maxspeed']<=.5}
 a['rest_pass']=all(a['rest_gates'].values()) and len(e)==50
else:
 a['closure_final_pct']={k:100*abs(m['p9'+k+'net'])/feed for k,feed in [('l',116.921233),('v',80.689903),('m',197.611136)]}
 a['acceptance_window_available']=len(e)>=1000
 # Descriptive for short screens; only a complete 1000-row tail can test gates.
 count=min(len(e),1000);sl=slice(-count,None)
 feeds={'l':h['p9lli'][sl]+h['p9lvi'][sl],'v':h['p9vli'][sl]+h['p9vvi'][sl]}
 feeds['m']=feeds['l']+feeds['v']
 assert all(np.all(x>0) for x in feeds.values())
 stats={'rows':count,'first_iteration':int(h['iteration'][sl][0]),'last_iteration':int(h['iteration'][-1]),'closure':{},'inventory':{},'routing':{},'residuals':{}}
 for k in feeds:
  error=100*np.abs(h['p9'+k+'net'][sl])/feeds[k]
  stats['closure'][k]={'mean_absolute_pct':float(error.mean()),'maximum_absolute_pct':float(error.max()),'pass':bool(error.mean()<=.5 and error.max()<=1)}
 for k in ['p9liquidmass','p9lowerliquid','p9upperliquid']:
  arr=h[k][sl];mean=float(arr.mean());half=len(arr)//2
  stats['inventory'][k]={'mean_kg':mean,'range_kg':float(np.ptp(arr)),'range_pct':float(100*np.ptp(arr)/mean) if mean else None,'half_mean_change_pct':float(100*(arr[half:].mean()-arr[:half].mean())/mean) if mean and half else None,'slope_kg_per_iteration':float(np.polyfit(h['iteration'][sl],arr,1)[0]) if count>1 else None}
 for ph,k,outlet,short in [('phase-2','l','brine-outlet','bo'),('phase-1','v','steam-outlet','so')]:
  fraction=-h['p9'+k+short][sl]/feeds[k]
  reverse={face:np.array([-row['flux'][ph][face]['negative_sum'] for row in e[-count:]])/feeds[k] for face in ['brine-outlet','steam-outlet']}
  stats['routing'][k]={'desired_net_outflow_min_pct':float(100*fraction.min()),'desired_net_outflow_mean_pct':float(100*fraction.mean()),'reverse_inflow_max_pct':{face:float(100*x.max()) for face,x in reverse.items()},'pass':bool(fraction.min()>=.99 and all(x.max()<.001 for x in reverse.values()))}
 ri=np.isin(res['iteration'],h['iteration'][sl])
 stats['residual_coverage_complete']=bool(np.array_equal(res['iteration'][ri],h['iteration'][sl]))
 for k,x in res.items():
  if k!='iteration' and ri.any():stats['residuals'][k]={'maximum':float(x[ri].max()),'final':float(x[ri][-1]),'pass':bool(np.all(x[ri]<=1e-3))}
 stats['claim_limit']='Descriptive block evidence; spatial stationarity, two independent starts, clipping audit and save/reopen persistence remain separate requirements.'
 a['tail_statistics']=stats
fig,ax=plt.subplots(3,1,figsize=(10,9),layout='constrained')
for key,label in [('p9lnet','Liquid'),('p9vnet','Vapor'),('p9mnet','Mixture')]:ax[0].plot(h['iteration'],h[key],label=label)
ax[0].set_ylabel('Net inward mass rate (kg/s)');ax[0].legend();ax[0].axhline(0,color='grey',lw=.6)
for key,label in [('p9liquidmass','Whole domain'),('p9lowerliquid','Below y=0.5 m'),('p9upperliquid','Above y=0.5 m')]:ax[1].plot(h['iteration'],h[key],label=label)
ax[1].set_ylabel('Liquid inventory (kg)');ax[1].legend()
for key,values in res.items():
 if key!='iteration':ax[2].semilogy(res['iteration'],values,label=key,color=COLORS.get(key))
ax[2].set_ylabel('Scaled residual');ax[2].set_xlabel('Native steady iteration');ax[2].legend(ncol=3,fontsize=8)
fig.suptitle(r.get('investigation_label','Phase 9')+' '+r['mode']+' diagnostic — no steady qualification')
fig.savefig(p/'balance-inventory-residual.png',dpi=160);plt.close(fig)
(p/'analysis.json').write_text(json.dumps(a,indent=2));print(json.dumps({k:v for k,v in a.items() if k not in ['history','residuals','independent_flux_parity']},indent=2))
