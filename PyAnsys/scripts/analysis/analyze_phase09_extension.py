from pathlib import Path
import sys,json,os,hashlib
import numpy as np
sys.path.insert(0,str(Path.cwd()/'PyAnsys/scripts/analysis'))
from analyze_phase07b_screen import parse_history,parse_residuals
os.environ['MPLCONFIGDIR']='/tmp/p9-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
base=Path('PyAnsys/output/phase09-preflight/user-extension-n2000');paths=[Path(json.loads((base/x).read_text())['run_manifest']) for x in ['receipt.json','recovery-receipt.json']];runs=[json.loads(p.read_text()) for p in paths]
def stitch(kind):
 rows={};audits=[]
 for p in paths:
  file=p.parent/('native-history.out' if kind=='h' else 'native-transcript.trn');d,a=(parse_history if kind=='h' else parse_residuals)(file);audits.append({'path':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'audit':a})
  for j,n in enumerate(d['iteration']):
   row={k:float(v[j]) for k,v in d.items()}
   if n in rows:assert all(np.isclose(rows[n][k],v,rtol=1e-6,atol=1e-8) for k,v in row.items()),(kind,n)
   rows[n]=row
 return {k:np.array([rows[n][k] for n in sorted(rows)]) for k in next(iter(rows.values()))},audits
h,ha=stitch('h');v,va=stitch('v');mask=(h['iteration']>1000)&(h['iteration']<=2000);assert np.array_equal(h['iteration'][mask],np.arange(1001,2001));a={'sources':ha+va,'qualified':False,'history_window':[1001,2000],'history_rows':1000,'closure':{},'inventory':{},'residuals':{},'routing':{}}
for k,feed in [('l',116.921232458),('v',80.689902358),('m',197.611134816)]:
 x=100*np.abs(h['p9'+k+'net'][mask])/feed;a['closure'][k]={'mean_abs_pct':float(x.mean()),'max_abs_pct':float(x.max()),'final_pct':float(x[-1])}
for k in ['p9liquidmass','p9lowerliquid']:
 x=h[k][mask];a['inventory'][k]={'start':runs[0]['initial_metrics'][k],'final':float(x[-1]),'change_pct':float(100*(x[-1]/runs[0]['initial_metrics'][k]-1)),'range_pct':float(100*np.ptp(x)/x.mean()),'half_mean_change_pct':float(100*(x[500:].mean()-x[:500].mean())/x.mean()),'last200_change_kg':float(x[-1]-x[-201])}
m=(v['iteration']>1000)&(v['iteration']<=2000);a['residual_missing_iterations']=sorted(set(range(1001,2001))-set(v['iteration'][m].astype(int)))
for k,x in v.items():
 if k!='iteration':a['residuals'][k]={'max':float(x[m].max()),'final':float(x[m][-1])}
e={}
for p in paths:
 for line in (p.parent/'iteration-evidence.jsonl').read_text().splitlines():
  row=json.loads(line);e[row['iteration']]=row
a['original_callback_gap']=[1764];a['callback_note']='Original N1764 callback absent; recovery initial-state callback at unchanged N1764 exists, labelled as recovery observation, not original iteration event.'
a['combined_missing_flux_coordinates']=sorted(set(range(1001,2001))-set(e))
for ph,feed in [('phase-1',80.689902358),('phase-2',116.921232458)]:
 a['routing'][ph]={face:{'max_reverse_pct':float(max(-e[n]['flux'][ph][face]['negative_sum']/feed*100 for n in range(1001,2001))),'final_outward_kg_s':e[2000]['flux'][ph][face]['signed_sum']} for face in ['brine-outlet','steam-outlet']}
f0=np.load(paths[0].parent/'fields-n01000.npz');f1=np.load(paths[1].parent/'fields-n02000.npz');vol=f0['mixture_SV_VOLUME'];alpha0=f0['phase-2_SV_VOF'];alpha1=f1['phase-2_SV_VOF'];a['spatial']={'volume_weighted_absolute_alpha_change':float(np.dot(vol,abs(alpha1-alpha0))/vol.sum()),'liquid_volume_change_m3':float(np.dot(vol,alpha1-alpha0)),'limit':'Endpoint difference only; connected-interface stationarity and persistence not established.'}
rr=[json.loads(p.read_text()) for p in Path('PyAnsys/output/phase09').glob('**/run.json')];a['budget']={'completed_iterations':sum(r.get('completed_iterations',0) for r in rr),'recorded_controller_wall_hours':sum(r.get('elapsed_s',0) for r in rr)/3600,'limit':'Recorded controller runtime; disconnected idle and separate recovery I/O excluded.'}
fig,axs=plt.subplots(3,1,figsize=(10,9),layout='constrained');axs[0].plot(h['iteration'],100*abs(h['p9lnet'])/116.921232458);axs[0].set_ylabel('Liquid imbalance (% feed)');axs[1].plot(h['iteration'],h['p9liquidmass']);axs[1].set_ylabel('Liquid inventory (kg)');colors={'continuity':'#46D2BA','x-velocity':'#A199D9','y-velocity':'#FA1900','z-velocity':'#2C8ED2','k':'#FC8500','epsilon':'#8BDD00','vf-phase-2':'#FB9DCD'}
for k,x in v.items():
 if k!='iteration':axs[2].semilogy(v['iteration'],x,label=k,color=colors[k])
for ax in axs:ax.axvline(1764,color='grey',ls='--',lw=.7)
axs[2].legend(ncol=3);axs[2].set_ylabel('Scaled residual');axs[2].set_xlabel('Native steady iteration (not physical time)');fig.suptitle('Phase 9 high-pool extension — unqualified\nStitched at N1764 after connection interruption');fig.savefig(base/'extension-review.png',dpi=150);plt.close(fig)
(base/'extension-review.json').write_text(json.dumps(a,indent=2));print(json.dumps({k:v for k,v in a.items() if k!='sources'},indent=2))
