"""Compare native saved fields before divergence; no Fluent or solver calls.

Volume-weighted common-bin projections are diagnostic flow comparisons, not
pointwise discretisation errors or Richardson/GCI estimates.
"""
import csv,hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity'
LEVELS=['M01','M02','M03','M04','M05','M06']
COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#D55E00','#333333']

def rows_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def reduce_fields(a,edges):
    xyz=a['centroid'];vol=a['volume'];ix=[np.searchsorted(e,xyz[:,i],side='right')-1 for i,e in enumerate(edges)]
    shape=tuple(len(e)-1 for e in edges);assert all(((j>=0)&(j<shape[i])).all() for i,j in enumerate(ix))
    ids=np.ravel_multi_index(tuple(ix),shape);n=int(np.prod(shape));weight=np.bincount(ids,weights=vol,minlength=n)
    count=np.bincount(ids,minlength=n)
    values={k:np.divide(np.bincount(ids,weights=vol*a[k],minlength=n),weight,out=np.zeros(n),where=weight>0) for k in ['u','v','w','pressure','alpha']}
    values.update(volume=weight,count=count)
    return values

def comparison(a,b):
    valid=(a['volume']>0)&(b['volume']>0);weights=np.minimum(a['volume'],b['volume'])[valid];W=weights.sum()
    va=np.column_stack([a[k][valid] for k in ['u','v','w']]);vb=np.column_stack([b[k][valid] for k in ['u','v','w']])
    rms=lambda x:float(np.sqrt(np.dot(weights,x*x)/W))
    du=float(np.sqrt(np.sum(weights[:,None]*(va-vb)**2)/W));uref=float(np.sqrt(np.sum(weights[:,None]*vb**2)/W))
    pa=a['pressure'][valid];pb=b['pressure'][valid];pa=pa-np.dot(weights,pa)/W;pb=pb-np.dot(weights,pb)/W
    return dict(shared_min_volume_m3=float(W),reference_volume_coverage_percent=float(100*W/b['volume'].sum()),
        velocity_vector_RMS_difference_m_s=du,velocity_vector_difference_percent_of_reference_RMS=100*du/uref,
        liquid_fraction_RMS_absolute_difference=rms(a['alpha'][valid]-b['alpha'][valid]),
        pressure_shape_RMS_difference_Pa=rms(pa-pb))

def main():
    receipt=json.loads((D/'extraction.json').read_text());assert receipt['status']=='EXTRACTED' and receipt['restore_verified'] and receipt['solves_issued']==0
    sources=receipt['sources'];bounds=np.array([s['native_cell_centroid_bounds'] for s in sources]);lo=np.floor(bounds[:,0,:].min(axis=0)*10)/10-.001;hi=np.ceil(bounds[:,1,:].max(axis=0)*10)/10+.001
    edges=[np.linspace(lo[i],hi[i]+1e-10,n+1) for i,n in enumerate([20,70,20])]
    low_edges=[np.linspace(lo[i],hi[i]+1e-10,n+1) for i,n in enumerate([10,35,10])]
    axial_edges=np.linspace(lo[1],hi[1],71)
    fields={};low={};profiles={};scalars=[];provenance=[]
    output_root=D.parent
    manifests=json.loads((output_root/'restart-native-manifests-60569-20261010.json').read_text())['levels']
    for level,date in [('M05','20261011'),('M06','20261012')]:
        manifests[level]=json.loads((output_root/f'vpn-restored-{date}/{level}-manifest.json').read_text())
    timing=[]
    for level in LEVELS[1:]:
        checkpoint=next(c for c in manifests[level]['checkpoints'] if c['iteration']==2000)
        timing.append(dict(level=level,start_iteration=1000,end_iteration=2000,solved_updates=1000,
            solver_seconds=checkpoint['solver_seconds'],seconds_per_update=checkpoint['solver_seconds']/1000,
            status='ATTEMPT_COST_NOT_TIME_TO_QUALIFICATION'))
    for s in sources:
        name=f"{s['level']}-N{s['iteration']}";path=D/'raw'/(name+'-native.npz')
        assert hashlib.sha256(path.read_bytes()).hexdigest()==s['local_array_sha256']
        with np.load(path) as a:
            fields[name]=reduce_fields(a,edges);low[name]=reduce_fields(a,low_edges)
            vol=a['volume'];xyz=a['centroid'];speed=np.sqrt(a['u']**2+a['v']**2+a['w']**2);r=np.hypot(xyz[:,0],xyz[:,2]);swirl=np.divide(xyz[:,2]*a['u']-xyz[:,0]*a['w'],r,out=np.zeros(len(r)),where=r>0)
            iy=np.searchsorted(axial_edges,xyz[:,1],side='right')-1;ws=np.bincount(iy,weights=vol,minlength=70)
            data={'speed':speed,'alpha':a['alpha'],'axial_velocity':a['v'],'signed_swirl_velocity':swirl,'pressure':a['pressure']}
            p={k:np.divide(np.bincount(iy,weights=vol*v,minlength=70),ws,out=np.full(70,np.nan),where=ws>0) for k,v in data.items()};p['volume']=ws;profiles[name]=p
            liquid_mean_height=float(np.dot(vol*a['alpha'],xyz[:,1])/np.dot(vol,a['alpha']))
        report={k:v[0] for d in s['original_checkpoint_reports'] for k,v in d.items()}
        scalars.append(dict(level=s['level'],iteration=s['iteration'],cells=s['cells'],effective_h_m=(s['total_volume_m3']/s['cells'])**(1/3),
           pressure_drop_Pa=report['p10-pressure-inlet']-report['p10-pressure-steamoutlet'],mean_speed_m_s=report['p10-speed-mean'],
           mean_vorticity_s_inverse=report['p10-vorticity-mean'],outlet_speed_m_s=report['p10-speed-steamoutlet'],liquid_inventory_kg=report['p10-mass-phase-2'],
           liquid_volume_weighted_mean_height_m=liquid_mean_height,
           liquid_outflow_kg_s=-report['p10-flux-phase-2-steamoutlet'],liquid_closure_error_percent=100*abs(report['p10-flux-phase-2-inlet']+report['p10-flux-phase-2-steamoutlet'])/116.92,
           mixture_closure_error_percent=100*abs(report['p10-flux-mixture-inlet']+report['p10-flux-mixture-steamoutlet'])/197.61))
        provenance.append(dict(local=str(path.relative_to(ROOT)),sha256=s['local_array_sha256'],source_pair=s['pair']))
    comparisons=[];binsensitivity=[]
    for n in [1000,2000]:
        ref='M06-N'+str(n)
        for level in LEVELS:
            name=level+'-N'+str(n)
            if name not in fields:continue
            if level!='M06':
                comparisons.append(dict(comparison='MESH_TO_M06',level=level,iteration=n,**comparison(fields[name],fields[ref])))
                binsensitivity.append(dict(comparison='COARSER_PROJECTION_MESH_TO_M06',level=level,iteration=n,**comparison(low[name],low[ref])))
        present=[x for x in LEVELS if x+'-N'+str(n) in fields]
        for a,b in zip(present[:-1],present[1:]):
            comparisons.append(dict(comparison='ADJACENT_MESH_'+b,level=a,iteration=n,**comparison(fields[a+'-N'+str(n)],fields[b+'-N'+str(n)])))
    for l in LEVELS[1:]:comparisons.append(dict(comparison='ITERATION_N1000_TO_N2000',level=l,iteration=2000,**comparison(fields[l+'-N1000'],fields[l+'-N2000'])))
    rows_csv(D/'scalar-comparison.csv',scalars);rows_csv(D/'field-comparison.csv',comparisons);rows_csv(D/'projection-sensitivity.csv',binsensitivity)
    rows_csv(D/'attempt-solver-cost.csv',timing)
    prows=[]
    for name,p in profiles.items():
        for j,y in enumerate((axial_edges[:-1]+axial_edges[1:])/2):prows.append(dict(snapshot=name,height_m=float(y),**{k:float(v[j]) for k,v in p.items()}))
    rows_csv(D/'height-profiles.csv',prows)
    for n in [1000,2000]:
        fig,axes=plt.subplots(1,3,figsize=(11,6),sharey=True);y=(axial_edges[:-1]+axial_edges[1:])/2
        for l,c in zip(LEVELS,COLORS):
            name=l+'-N'+str(n)
            if name not in profiles:continue
            p=profiles[name]
            for ax,k in zip(axes,['speed','signed_swirl_velocity','alpha']):ax.plot(p[k],y,label=l,color=c,lw=1.4)
        for ax,x in zip(axes,['Mean speed (m/s)','Mean signed swirl (m/s)','Mean liquid volume fraction']):ax.set_xlabel(x);ax.grid(alpha=.25)
        axes[0].set_ylabel('Height y (m)');axes[0].legend(loc='best');fig.suptitle(f'Saved OFF fields at N{n}: volume-weighted height profiles\nUnconverged states; equal iteration is not equal numerical maturity',fontsize=12)
        fig.tight_layout();fig.savefig(D/f'height-profiles-N{n}.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(10,7))
    for ax,key,label in zip(axes.ravel(),['pressure_drop_Pa','mean_speed_m_s','liquid_inventory_kg','mean_vorticity_s_inverse'],['Pressure drop (kPa)','Mean speed (m/s)','Liquid inventory (kg)','Mean vorticity (1/s)']):
        for n,sty in [(1000,'o-'),(2000,'s--')]:
            r=[r for r in scalars if r['iteration']==n];ax.plot([x['cells']/1e6 for x in r],[x[key]/(1000 if key=='pressure_drop_Pa' else 1) for x in r],sty,label=f'N{n}')
        ax.set(xlabel='Cells (millions)',ylabel=label);ax.grid(alpha=.25);ax.legend()
    fig.suptitle('Pre-divergence mesh sensitivity: checkpoint reports\nIteration-dependent outputs; no mesh independence established',fontsize=12);fig.tight_layout();fig.savefig(D/'scalar-refinement.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.5))
    for n,sty in [(1000,'o-'),(2000,'s--')]:
        r=[r for r in comparisons if r['iteration']==n and r['comparison']=='MESH_TO_M06'];ax.plot([next(s['cells'] for s in scalars if s['level']==x['level'])/1e6 for x in r],[x['velocity_vector_difference_percent_of_reference_RMS'] for x in r],sty,label=f'Mesh difference vs M06 at N{n}')
    r=[r for r in comparisons if r['comparison']=='ITERATION_N1000_TO_N2000'];ax.plot([next(s['cells'] for s in scalars if s['level']==x['level'])/1e6 for x in r],[x['velocity_vector_difference_percent_of_reference_RMS'] for x in r],'d:',color='black',label='Same mesh: N1000 vs N2000')
    ax.set(xlabel='Cells (millions)',ylabel='Velocity-vector RMS difference (%)');ax.grid(alpha=.25);ax.legend();ax.set_title('Volume-weighted common-bin velocity comparison\nM06 is a diagnostic reference, not the exact solution');fig.tight_layout();fig.savefig(D/'field-refinement.png',dpi=180);plt.close(fig)
    summary=dict(status='PRE_DIVERGENCE_MESH_SENSITIVITY_COMPLETE',convergence_established=False,new_solved_updates=0,
       sources=provenance,scalar_rows=scalars,field_comparisons=comparisons,projection_sensitivity=binsensitivity,attempt_solver_cost=timing,
       common_projection=dict(method='Native cell-centroid assignment; volume-weighted bin means; RMS over jointly occupied bins weighted by min bin volume',bounds_m=[lo.tolist(),hi.tolist()],shape=[20,70,20],check_shape=[10,35,10],pressure_policy='Remove volume-weighted mean on common bins before pressure RMS comparison'),
       height_profile_method='Native cell-volume-weighted means in 70 fixed height slabs; signed swirl=(z*u-x*w)/sqrt(x*x+z*z), axis through x=z=0',
       limits=['Fixed iteration comparison is not a converged steady-state mesh study','M01 failed before N2000; N2000 contains M02-M06 only','M07 user-skipped and BF01 ON excluded','Common-bin differences are projected field differences, not pointwise discretisation errors','Azimuthally averaged height profiles can hide local differences','Geometry discretisation varies slightly; M05 had an interrupted startup before preserved restart','No qualified tet comparison or GCI/Richardson estimate'])
    (D/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=summary['status'],snapshots=len(sources),fields=comparisons[-7:]),indent=2))
if __name__=='__main__':main()
