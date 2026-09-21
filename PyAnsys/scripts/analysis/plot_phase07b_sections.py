"""Render exported native facet values without spatial interpolation.

All sections and both endpoints use common scales. For multi-case comparison,
pass the same --scales JSON to every run; widen and regenerate all figures if
any later case exceeds the range. No Fluent connection is made.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'p7b-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

SECTIONS = [('p7b-section-y0p5', .5), ('p7b-section-y1p5', 1.5),
            ('p7b-section-y3p0', 3.), ('p7b-section-y5p0', 5.)]
CORE = [('phase-2-vof', 'Liquid volume fraction'),
        ('velocity-magnitude', 'velocity-magnitude\n(m/s)'),
        ('phase-2-velocity-magnitude', 'phase-2-velocity-magnitude\n(m/s)')]
COMPONENTS = [(prefix+direction+'-velocity', f'{prefix}{direction}-velocity\n(m/s)')
              for prefix,label in [('', 'Mixture'), ('phase-2-', 'Liquid')]
              for direction in 'xyz']


def render(run, output, scales_path=None):
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((run/'manifest.json').read_text())
    recovery_path=run/'recovery-sections.json'
    recovery=json.loads(recovery_path.read_text()) if recovery_path.exists() else None
    if recovery:
        stage=recovery['stage']; iteration=recovery['iteration']
        assert stage not in ['initial','final'] and '/' not in stage and '\\' not in stage
        assert isinstance(iteration,int) and 0<iteration<5000
        directory=Path(recovery.get('directory',stage+'-sections'))
        assert not directory.is_absolute() and '..' not in directory.parts
        stages={'initial':(run/'initial-sections',0), stage:(run/directory,iteration)}
    else:
        stages={'initial':(run/'initial-sections',0), 'final':(run/'final-sections',manifest['completed_iterations'])}
    evidence, datasets = {}, {}
    for stage,(directory,iteration) in stages.items():
        index_path = directory/'index.json'
        if not index_path.exists():
            raise ValueError(f'Missing {stage} section index')
        index=json.loads(index_path.read_text()); datasets[stage]={}; evidence[stage]={}
        for name,height in SECTIONS:
            path=index_path.parent/index['sections'][name]['file']
            with np.load(path) as archive:
                data={key:archive[key] for key in archive.files}
            vertices=data['vertices']; sizes=data['face_sizes']; connectivity=data['connectivity']
            assert len(sizes)>0 and np.all(sizes>=3) and sum(sizes)==len(connectivity)
            assert np.allclose(vertices[:,1],height,rtol=0,atol=2e-6)
            assert np.all(np.isfinite(vertices)) and connectivity.min()>=0 and connectivity.max()<len(vertices)
            offset=np.r_[0,np.cumsum(sizes)]
            polygons=[vertices[connectivity[offset[i]:offset[i+1]]][:,[0,2]] for i in range(len(sizes))]
            areas=np.array([abs(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1)))/2 for p in polygons])
            assert np.all(areas>=0) and areas.sum()>0
            fields={}
            for field in index['fields']:
                values=data[field]; assert len(values)==len(sizes) and np.isfinite(values).all()
                fields[field]={'minimum':float(values.min()),'maximum':float(values.max()),
                               'area_weighted_mean':float(np.average(values,weights=areas))}
            evidence[stage][name]={'source':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                   'height_m':height,'facets':len(sizes),'zero_projected_area_facets':int(np.count_nonzero(areas==0)),
                                   'area_m2':float(areas.sum()),'fields':fields}
            datasets[stage][name]=(data,polygons)
            if stage!='initial':
                initial=datasets['initial'][name][0]
                for key in ['vertices','centroids','face_sizes','connectivity']:
                    assert np.array_equal(data[key],initial[key]), (name,key,'initial/comparison geometry mismatch')
    if scales_path:
        scales=json.loads(scales_path.read_text())
    else:
        peak=max(float(abs(data[field]).max()) for stage in datasets.values() for data,_ in stage.values()
                 for field,_ in CORE[1:]+COMPONENTS)
        bound=max(10.,10*math.ceil(peak/10))
        scales={'phase-2-vof':[0.,1.]}
        scales.update({f:[0.,bound] for f,_ in CORE[1:]})
        scales.update({f:[-bound,bound] for f,_ in COMPONENTS})
    figures=[]
    for stage,(_,iteration) in stages.items():
        for group,fields in [('above-cap-fields',CORE),('velocity-components',COMPONENTS)]:
            fig,axes=plt.subplots(4,len(fields),figsize=(3.05*len(fields),10.7),layout='constrained',sharex=True,sharey=True)
            for row,(name,height) in enumerate(SECTIONS):
                data,polygons=datasets[stage][name]
                for col,(field,label) in enumerate(fields):
                    limits=scales[field]; values=data[field]
                    if values.min()<limits[0]-1e-7 or values.max()>limits[1]+1e-7:
                        raise ValueError(f'{stage}/{name}/{field} exceeds shared scale; widen and regenerate all cases')
                    ax=axes[row,col]
                    collection=PolyCollection(polygons,array=values,cmap='RdBu_r' if group=='velocity-components' else 'viridis',
                                              clim=limits,edgecolors='none',antialiased=False,rasterized=True)
                    ax.add_collection(collection); ax.autoscale_view(); ax.set_aspect('equal')
                    if row==0: ax.set_title(label,fontsize=10)
                    if col==0: ax.set_ylabel(f'y = {height:g} m\nz (m)')
                    if row==3: ax.set_xlabel('x (m)')
                    if row==3:
                        fig.colorbar(collection,ax=axes[:,col],shrink=.42,location='bottom',pad=.03,
                                     ticks=[limits[0],sum(limits)/2,limits[1]])
            stage_label=f'RECOVERY CHECKPOINT, N={iteration}' if recovery and stage!='initial' else f'{stage}, N={iteration}'
            fig.suptitle(f'F3 — {run.name} | {stage_label}\nNative facet values; horizontal sections above maximum collector top y=0.020 m',fontsize=11)
            name=f'F3-{stage}-{group}.png'; fig.savefig(output/name,dpi=160); plt.close(fig)
            figures.append(str((output/name).resolve()))
    summary={'run_id':run.name,'source_case_data':manifest.get('pairs'),
             'rendering':'Piecewise constant native Fluent iso-surface facet values; no interpolation or smoothing.',
             'field_identity_limit':'Exact API field names are retained. No captured field metadata independently verifies the unqualified velocity fields as mixture fields.',
             'initial_comparison_geometry_identical':True,'scales':scales,
             'comparison_rule':'Reuse these scales across cases; if exceeded, widen and regenerate every comparison figure.',
             'claim_limit':'Finite unconverged field snapshots; no thickness effect can be inferred from a single case.',
             'evidence':evidence,'figures':figures}
    if recovery:
        summary['recovery_sections']={'receipt':str(recovery_path.resolve()),
                                      'sha256':hashlib.sha256(recovery_path.read_bytes()).hexdigest(), **recovery}
        summary['claim_limit']='Recovery-checkpoint fields, not a final or successful endpoint. No matched N5000 spatial comparison is available.'
    else:
        summary['initial_final_geometry_identical']=True
    metadata_path=run/'field-metadata.json'
    if metadata_path.exists():
        metadata=json.loads(metadata_path.read_text())
        expected={field:('phase-2' if field.startswith('phase-2-') else 'mixture')
                  for field in metadata}
        assert all(metadata[field]['domain']==domain for field,domain in expected.items())
        summary['field_metadata']={'path':str(metadata_path.resolve()),
                                   'sha256':hashlib.sha256(metadata_path.read_bytes()).hexdigest(),
                                   'domains':expected}
        summary['field_identity_limit']='Run-local API metadata identifies unqualified pressure/velocity fields as mixture and phase-2-prefixed fields as phase-2.'
    (output/'section-scales.json').write_text(json.dumps(scales,indent=2)+'\n')
    (output/'section-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('run',type=Path)
    parser.add_argument('--output',type=Path); parser.add_argument('--scales',type=Path)
    args=parser.parse_args(); result=render(args.run,args.output or args.run/'analysis',args.scales)
    print(json.dumps({'run_id':result['run_id'],'figures':result['figures'],'scales':result['scales']},indent=2))
