"""Audit fixed synthetic pressure-driven vent tests against Bernoulli + vent loss."""
from pathlib import Path
import json,numpy as np,os,sys
from analyze_phase07b_screen import parse_history,parse_residuals
BASE=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'output/drainage-benchmark';r=json.loads((BASE/'campaign.json').read_text());answer=[]
for c in r['cases']:
 if c['status']!='COMPLETE':continue
 p=BASE/c['tag'];h,ha=parse_history(p/'native-history.out');v,va=parse_residuals(p/'native-transcript.trn');assert not ha['conflicting_indices'] and not va['conflicting_indices'];sl=h['iteration']>400;sr=v['iteration']>400;assert sum(sl)==100 and sum(sr)==100
 flow=abs(h['bout'][sl]);closure=100*abs(h['bin'][sl]+h['bout'][sl])/flow;u=h['bvel'][sl];pred=c['expected_U'];err=100*abs(u.mean()/pred-1);variation=100*np.ptp(flow)/flow.mean();pressvariation=100*max(np.ptp(h[k][sl]) for k in ['bpi','bpo'])/c['delta_total_to_ambient_Pa'];res={k:float(x[sr].max()) for k,x in v.items() if k!='iteration'}
 item={'tag':c['tag'],'predicted_velocity':pred,'measured_velocity':float(u.mean()),'flow_kg_s':float(flow.mean()),'prediction_error_pct':float(err),'max_closure_pct':float(closure.max()),'flow_variation_pct':float(variation),'pressure_variation_pct_driving_pressure':float(pressvariation),'residual_maxima':res,'history_audit':ha,'residual_audit':va};item['terminal_gates_passed']=bool(err<=2 and closure.max()<=.1 and variation<=.1 and pressvariation<=.1 and all(x<=1e-6 for x in res.values()));item['maximum_speed_all_iterations']=float(h['bmax'].max());item['startup_guard_breached']=bool(np.any(h['bmax']>20));item['passed']=item['terminal_gates_passed'] and not item['startup_guard_breached'];answer.append(item)
a={'cases':answer,'all_passed':len(answer)==4 and all(x['passed'] for x in answer),'claim_limit':'Synthetic single-phase slip-duct implementation verification only; not VOF/head-profile validation, actual valve calibration or separator qualification.'};(BASE/'analysis.json').write_text(json.dumps(a,indent=2));print(json.dumps({**a,'cases':[{k:v for k,v in x.items() if not k.endswith('audit')} for x in answer]},indent=2))
# Raw histories plus analytical reference; no smoothing or spatial reconstruction.
os.environ.setdefault('MPLCONFIGDIR','/tmp/drainage-bench-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axs=plt.subplots(2,1,figsize=(9,7),layout='constrained')
for c in r['cases']:
 if c['status']!='COMPLETE':continue
 h,_=parse_history(BASE/c['tag']/'native-history.out');v,_=parse_residuals(BASE/c['tag']/'native-transcript.trn');label=f"K={c['K']}, driving pressure={c['delta_total_to_ambient_Pa']} Pa"
 line=axs[0].semilogy(h['iteration'],h['bvel'],label=label)[0];axs[0].axhline(c['expected_U'],color=line.get_color(),ls=':',lw=.7)
 axs[1].semilogy(v['iteration'],v['continuity'],label=label,color='#46D2BA',ls={ 'k0-dp200':'-','k0-dp800':'--','k9-dp200':':','k9-dp800':'-.'}[c['tag']])
axs[0].set_ylabel('Outlet mean speed (m/s)');axs[0].legend(fontsize=8);axs[1].set_ylabel('Scaled continuity residual');axs[1].set_xlabel('Native steady iteration');axs[1].axhline(1e-6,color='grey',lw=.6);axs[1].legend(fontsize=8);fig.suptitle('Synthetic steady outlet-resistance verification\nDotted horizontal speeds: independent analytical prediction');fig.savefig(BASE/'verification.png',dpi=150);plt.close(fig)
