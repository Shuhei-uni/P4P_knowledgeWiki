"""Verify exact hydrostatic horizon or predeclared guarded stop, then audit quiescence."""
from pathlib import Path
import argparse,json,sys,os,yaml
import numpy as np
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'PyAnsys/scripts/analysis'))
from analyze_phase07b_screen import parse_history,parse_residuals
p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--iterations',type=int,required=True);args=p.parse_args()
rp=Path(json.loads(args.receipt.read_text())['run_manifest']);r=json.loads(rp.read_text());out=rp.parent
assert r['status'] in ['BLOCK_COMPLETE','STOPPED_AT_GATE']
assert r['start_iteration']==args.start and r['end_iteration']-args.start==r['completed_iterations']
assert 0<r['completed_iterations']<=args.iterations
assert r['completed_iterations']==args.iterations or r.get('stop_reason')
assert r['pair_exists'] and not r['iterating'] and not r.get('capture_error')
for f in ['native-history.out','native-transcript.trn','iteration-evidence.jsonl',f"fields-n{args.start:05d}.npz",f"fields-n{r['end_iteration']:05d}.npz"]:assert (out/f).stat().st_size>0
sections=json.loads((out/'terminal-sections/index.json').read_text());assert set(sections['sections'])=={'p9-section-x0','p9-section-z0'}
for v in sections['sections'].values():assert v['facets']>0 and (out/'terminal-sections'/v['file']).is_file()
h,ha=parse_history(out/'native-history.out');res,ra=parse_residuals(out/'native-transcript.trn');events=[json.loads(t) for t in (out/'iteration-evidence.jsonl').read_text().splitlines()]
expected=list(range(r['first_capture'],r['end_iteration']+1))
assert list(h['iteration'])==expected==[e['iteration'] for e in events]
assert list(res['iteration'])==expected
assert not ha['conflicting_indices'] and not ha['nonfinite_columns'] and not ra['conflicting_indices'] and not ra['nonfinite_columns']
assert set(res)=={'iteration','continuity','x-velocity','y-velocity','z-velocity','k','epsilon','vf-phase-2'}
aux=np.load(out/'terminal-aux.npz');assert all(np.isfinite(aux[k]).all() for k in ['SV_P_G','SV_DENSITY','SV_BF_V','SV_BFP_V'])
initial=r['initial_fields']['liquid_mass_kg'];delta=100*(h['p9liquidmass']/initial-1)
gross=np.array([max(max(f['positive_sum'],-f['negative_sum']) for ph in ['phase-1','phase-2'] for f in e['flux'][ph].values()) for e in events])
parity=0
for i,e in enumerate(events):
 for ph,key in [('phase-1','v'),('phase-2','l'),('mixture','m')]:
  for face,slug in [('liquid-inlet','li'),('steam-inlet','vi'),('brine-outlet','bo'),('steam-outlet','so')]:
   f=e['flux'][ph][face];assert np.isclose(f['positive_sum']+f['negative_sum'],f['signed_sum'],atol=1e-8);parity=max(parity,abs(f['signed_sum']+h['p9'+key+slug][i]))
assert parity<1e-7
window=len(events)>=100
checks={'throughout_inventory_within_0p1_percent':bool(np.max(abs(delta))<=.1),'final100_inventory_range_below_0p05_percent':bool(np.ptp(h['p9liquidmass'][-100:])/initial*100<.05) if window else None,'final100_speed_below_0p001_m_s':bool(np.max(h['p9maxspeed'][-100:])<=.001) if window else None,'final100_each_gross_phase_boundary_flux_below_0p01_kg_s':bool(gross[-100:].max()<=.01) if window else None}
f0=np.load(out/f'fields-n{args.start:05d}.npz');f1=np.load(out/f"fields-n{r['end_iteration']:05d}.npz");v=f0['mixture_SV_VOLUME'];mass=np.dot(v,f1['phase-2_SV_VOF'])*881.77;assert np.isclose(mass,r['terminal_metrics']['p9liquidmass'],rtol=1e-10)
lines=(out/'native-transcript.trn').read_text().splitlines()
a={'execution_verified':True,'qualified':False,'status':r['status'],'stop_reason':r.get('stop_reason'),'solved_iterations':r['completed_iterations'],'requested_iterations':args.iterations,'history':ha,'residuals':ra,'initial_mass_kg':initial,'final_mass_kg':mass,'inventory_change_pct':float(delta[-1]),'max_inventory_departure_pct':float(max(abs(delta))),'max_speed_m_s':float(h['p9maxspeed'].max()),'max_gross_phase_boundary_flux_kg_s':float(gross.max()),'last_speed_m_s':float(h['p9maxspeed'][-1]),'last_gross_phase_boundary_flux_kg_s':float(gross[-1]),'quiescence_checks':checks,'final100_window_available':window,'hydrodynamic_quiescence_pass':all(checks.values()),'face_native_max_error_kg_s':parity,'phase_sum_native_max_error_kg_s':float(np.max(abs(h['p9lnet']+h['p9vnet']-h['p9mnet']))),'weighted_rms_pressure_change_Pa':float(np.sqrt(np.dot(v,(f1['mixture_SV_P']-f0['mixture_SV_P'])**2)/v.sum())),'weighted_abs_alpha_change':float(np.dot(v,abs(f1['phase-2_SV_VOF']-f0['phase-2_SV_VOF']))/v.sum()),'residual_final':{k:float(x[-1]) for k,x in res.items() if k!='iteration'},'turbulent_viscosity_limit_lines':sum('turbulent viscosity limited' in s for s in lines),'claim_limit':'Homogeneous-liquid hydrostatic isolation only; no two-phase pool, physical-time or operating-separator qualification.'}
xyz=f1['mixture_SV_CENTROID'].reshape(-1,3);target_pressure=876.04*9.81*(.1-xyz[:,1])
a['homogeneous_liquid_checks']={'max_pressure_error_from_analytic_Pa':float(np.max(abs(f1['mixture_SV_P']-target_pressure))),'weighted_rms_pressure_error_Pa':float(np.sqrt(np.dot(v,(f1['mixture_SV_P']-target_pressure)**2)/v.sum())),'max_alpha_departure_from_one':float(np.max(abs(f1['phase-2_SV_VOF']-1))),'max_density_error_kg_m3':float(np.max(abs(aux['SV_DENSITY']-881.77)))}
(out/'analysis.json').write_text(json.dumps(a,indent=2)+'\n')
os.environ.setdefault('MPLCONFIGDIR','/tmp/hydrostatic-mpl');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(3,1,figsize=(9,8),layout='constrained');x=h['iteration'];ax[0].plot(x,delta);ax[0].set_ylabel('Inventory change (%)');ax[1].plot(x,h['p9maxspeed']);ax[1].set_ylabel('Maximum speed (m/s)');ax[2].plot(x,gross,label='Maximum phase gross flux')
for k,label in [('l','Liquid net'),('v','Vapor net'),('m','Mixture net')]:ax[2].plot(x,h['p9'+k+'net'],label=label)
ax[2].set_ylabel('Boundary flow (kg/s)');ax[2].set_xlabel('Steady iteration (not time)');ax[2].legend();fig.suptitle(r.get('investigation_label','Zero-feed diagnostic'));fig.savefig(out/'hydrostatic-evidence.png',dpi=160);plt.close(fig)
state=root/'Project/experiments/pressure-gravity-initialization/phase-state.yaml';s=yaml.safe_load(state.read_text());runs=[json.loads(q.read_text()) for q in (root/'PyAnsys/output/pressure-gravity-initialization').glob('**/run.json')];s.update(status='TERMINAL_REVIEW_REQUIRED',completed_iterations=sum(q.get('completed_iterations',q.get('issued_iterations',0)) for q in runs),solver_wall_seconds=sum(q.get('elapsed_s',0) for q in runs),solver_iterating=False,live_run_manifest=str(rp),current_action='Verified terminal evidence; planner to interpret and execute next justified in-scope contrast; monitor remains active');state.write_text(yaml.safe_dump(s,sort_keys=False));print(json.dumps({k:a[k] for k in ['execution_verified','stop_reason','solved_iterations','inventory_change_pct','max_speed_m_s','hydrodynamic_quiescence_pass']}))
