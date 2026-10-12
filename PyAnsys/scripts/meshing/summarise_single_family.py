"""Summarise verified single-inlet meshes and plot the achieved refinement."""
import json,os,re
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/p4p-mesh-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from build_single_inlet_family import OUT,ROOT

IDS=['curvature-trial','curvature-middle','curvature-anchor','selected-fine-1','selected-fine-2','selected-fine-3','selected-fine-4']

def distribution_count(data):
    # Fluent returns [0] when no cells fall in the requested interval.
    if data==[0]:return 0
    if len(data)<2 or not isinstance(data[1],list):
        raise RuntimeError('Unexpected quality-distribution response '+str(data))
    return sum(data[1])

def collect():
    baseline=json.loads((OUT.parent/'Separator-purnanto-single-733k.msh.h5.baseline.json').read_text())
    original={b['name']:b for b in baseline['boundaries']}
    rows=[]
    for rid in IDS:
        path=OUT/(rid+'-status.json')
        if not path.exists():continue
        receipt=json.loads(path.read_text())
        if receipt['status']!='COMPLETE':continue
        a=json.loads((OUT/(rid+'-reopened.json')).read_text());m=a['metrics']
        tail_audit=a
        anchor_path=OUT/'final-loaded-anchor.json'
        if rid=='curvature-anchor' and anchor_path.exists():
            tail_audit=json.loads(anchor_path.read_text())
            if tail_audit['cell_count']!=a['cell_count']:raise RuntimeError('Anchor tail audit mismatch')
        beforepath=OUT/(rid+'-before-improve.json')
        before=json.loads(beforepath.read_text()) if beforepath.exists() else None
        volume_delta=a['volume']/baseline['volume']-1
        area_deltas={b['name']:b['area']/original[b['name']]['area']-1 for b in a['boundaries']}
        bound_deltas={b['name']:max(abs(v-original[b['name']]['bounds'][j][k])
            for j,p in enumerate(b['bounds']) for k,v in enumerate(p)) for b in a['boundaries']}
        # CAD is identical; these tolerances concern its polygonal representation.
        # Retain all differences in the receipt instead of claiming exact mesh
        # coordinate equality across different surface discretisations.
        if abs(volume_delta)>.005:raise RuntimeError('Volume differs by more than 0.5% '+rid)
        if max(abs(v) for v in area_deltas.values())>.01:raise RuntimeError('Wall area differs by more than 1% '+rid)
        if max(abs(area_deltas[n]) for n in ['inlet','steamoutlet'])>.005:
            raise RuntimeError('Inlet/outlet area differs by more than 0.5% '+rid)
        if any(b['type']=='velocity-inlet' and b['name']!='inlet' for b in a['boundaries']):
            raise RuntimeError('Unexpected inlet '+rid)
        h=(a['volume']/a['cell_count'])**(1/3)
        log=(OUT/(rid+'-run.txt')).read_text()
        generation=re.findall(r'FINISHED Generate the Volume Mesh (\{[^\n]*\})',log)
        warnings=json.loads(generation[-1]).get('warnings') if generation else None
        rows.append(dict(id=rid,scale=receipt['scale'],file=Path(receipt['mesh']).name,
            remote_mesh=receipt['mesh'],cells=a['cell_count'],effective_h_m=h,
            min_oq=m['Orthogonal Quality'][1],mean_oq=m['Orthogonal Quality'][3],
            max_skewness=m['Skewness'][2],mean_skewness=m['Skewness'][3],
            max_aspect_ratio=m['FLUENT Aspect Ratio'][2],max_size_change=m['Size Change'][2],
            min_cell_volume_m3=m['Size'][1],volume_m3=a['volume'],
            volume_delta=volume_delta,area_deltas=area_deltas,bounds_max_deltas_m=bound_deltas,
            before_min_oq=before['metrics']['Orthogonal Quality'][1] if before else .13234739,
            before_max_skewness=before['metrics']['Skewness'][2] if before else None,
            before_max_aspect_ratio=before['metrics']['FLUENT Aspect Ratio'][2] if before else None,
            cells_below_oq03=sum(a['distributions']['Orthogonal Quality'][1][-3:]),
            cells_size_change_ge300=distribution_count(tail_audit['distributions']['Size Change >= 300'])
                if 'Size Change >= 300' in tail_audit['distributions'] else (0 if m['Size Change'][2]<300 else None),
            quality_iteration_limit=receipt.get('quality_iteration_limit',25),
            recovery=receipt.get('recovery'),
            volume_generation_warnings=warnings,
            free_faces=a['free_faces'],multi_faces=a['multi_faces']))
    for left,right in zip(rows,rows[1:]):
        if left['cells']>=right['cells']:raise RuntimeError('Refinement is not monotonic')
        right['cell_ratio_to_previous']=right['cells']/left['cells']
        right['h_ratio_from_previous']=left['effective_h_m']/right['effective_h_m']
    return rows

def main():
    rows=collect();(OUT/'family-summary.json').write_text(json.dumps(rows,indent=2))
    print(json.dumps([{k:r[k] for k in ['id','cells','min_oq','max_skewness','max_aspect_ratio','volume_delta']} for r in rows],indent=2))
    if not rows:return
    fig,axes=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
    x=[r['cells']/1000 for r in rows]
    axes[0].plot(range(1,len(rows)+1),x,'o-',color='#276b8f')
    axes[0].set(xlabel='Refinement level (coarse to fine)',ylabel='Cells (thousands)',yscale='log')
    axes[0].set_xticks(range(1,len(rows)+1))
    axes[0].set_yticks([350,500,1000,2000,5000],labels=['350','500','1,000','2,000','5,000'])
    axes[1].plot(x,[r['before_min_oq'] for r in rows],'o--',color='#9e9e9e',label='Before recorded quality pass')
    axes[1].plot(x,[r['min_oq'] for r in rows],'o-',color='#276b8f',label='Saved result')
    axes[1].axhline(.3,color='#c18b2e',linestyle=':',label='Improvement target')
    axes[1].set(xlabel='Cells (thousands)',ylabel='Minimum orthogonal quality',xscale='log',ylim=(0,.35))
    axes[1].set_xticks([350,500,1000,2000,5000],labels=['350','500','1,000','2,000','5,000'])
    axes[1].legend(fontsize=8)
    for ax in axes:ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.savefig(OUT/'family-quality.png',dpi=180)

if __name__=='__main__':main()
