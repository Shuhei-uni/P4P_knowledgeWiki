"""Compare the predeclared native reconstructed-fill contrast with the binary reference."""
from pathlib import Path
import json,os
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'PyAnsys/output/discrete-interface-initialization'
rp=Path(json.loads((out/'n500-receipt.json').read_text())['run_manifest']);r=json.loads(rp.read_text());assert r['status'] in ['STOPPED_AT_GATE','BLOCK_COMPLETE']
refp=Path(json.loads((root/'PyAnsys/output/hydrostatic-startup-recovery/modified-bfw-n500-receipt.json').read_text())['run_manifest']);ref=json.loads(refp.read_text())
audit=json.loads((rp.parent/'analysis.json').read_text());refaudit=json.loads((refp.parent/'analysis.json').read_text())
events=[json.loads(x) for x in (rp.parent/'iteration-evidence.jsonl').read_text().splitlines()];first=next(e for e in events if e['iteration']==1)
rows={};arrays={}
for name,runp in [('Binary reference',refp),('Reconstructed interface',rp)]:
 run=json.loads(runp.read_text());a=np.load(runp.parent/'fields-n00000.npz');b=np.load(runp.parent/f"fields-n{run['end_iteration']:05d}.npz");xyz=a['mixture_SV_CENTROID'].reshape(-1,3);vol=a['mixture_SV_VOLUME'];alpha=a['phase-2_SV_VOF'];speed=np.sqrt(sum(b['mixture_'+v]**2 for v in ['SV_U','SV_V','SV_W']));i=int(speed.argmax());mixed=(alpha>1e-12)&(alpha<1-1e-12)
 rows[name]={'run':str(runp),'end_iteration':run['end_iteration'],'initial_mass_kg':float(881.77*np.dot(vol,alpha)),'fractional_cells':int(mixed.sum()),'fractional_centroid_y_range_m':[float(xyz[mixed,1].min()),float(xyz[mixed,1].max())] if mixed.any() else None,'max_speed_m_s':float(speed[i]),'max_speed_location_m':xyz[i].tolist(),'terminal_liquid_net_inward_kg_s':run['terminal_metrics']['p9lnet'],'initial_alpha_at_speed_max':float(alpha[i]),'inventory_change_pct':100*(run['terminal_metrics']['p9liquidmass']/(881.77*np.dot(vol,alpha))-1)}
 arrays[name]=(xyz,alpha,speed)
assert np.array_equal(arrays['Binary reference'][0],arrays['Reconstructed interface'][0])
ratio=first['metrics']['p9maxspeed']/refaudit['max_speed_m_s'];n1delta=100*(first['metrics']['p9liquidmass']/audit['initial_mass_kg']-1)
result={'rows':rows,'n1_speed_ratio_to_reference':ratio,'n1_inventory_change_pct':n1delta,'material_suppression_gate':bool(ratio<=.1 and abs(n1delta)<=abs(refaudit['inventory_change_pct'])),'execution':audit,'claim_limit':'Only initialization representation at fixed height; native geometric fill is not proof of discrete pressure-gravity balance, no operating drainage qualification.'}
(out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
os.environ.setdefault('MPLCONFIGDIR','/tmp/interface-mpl');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(2,2,figsize=(10,7),layout='constrained')
for col,(name,(xyz,alpha,speed)) in enumerate(arrays.items()):
 band=abs(xyz[:,1]-.1)<=.15;y=xyz[band,1]
 ax[0,col].scatter(y,alpha[band],s=1,alpha=.3,rasterized=True);ax[1,col].scatter(y,speed[band],s=1,alpha=.3,rasterized=True)
 ax[0,col].set_title(name);ax[0,col].set_ylim(-.03,1.03);ax[1,col].set_ylim(0,max(x[2].max() for x in arrays.values())*1.05)
 for row in [0,1]:ax[row,col].axvline(.1,color='red',lw=1,label='Initial surface');ax[row,col].set_xlabel('Cell centroid y (m)')
 ax[0,col].set_ylabel('N0 liquid volume fraction');ax[1,col].set_ylabel(f"N{rows[name]['end_iteration']} speed (m/s)")
fig.suptitle('Interface initialization and startup motion\nRaw cell values within 0.15 m of prescribed surface; no time interpretation');fig.savefig(out/'interface-comparison.png',dpi=160);plt.close(fig)
print(json.dumps({'ratio':ratio,'n1_inventory_change_pct':n1delta,'material_suppression_gate':result['material_suppression_gate'],'rows':rows},indent=2))
