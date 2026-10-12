"""Compare preserved original-mesh audits with the delivered single-inlet family.

This is a read-only analysis of existing native Fluent receipts. It does not
connect to Fluent or modify any mesh.
"""
import csv,json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/p4p-mesh-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'output/mesh-audits/2026-10-08-purnanto-remesh'
OUT=AUDIT/'single-family'

def main():
    manifest=json.loads((AUDIT/'source-manifest.json').read_text())
    old=[]
    for source in manifest:
        path=AUDIT/(source['name']+'.baseline.json')
        a=json.loads(path.read_text()); m=a['metrics']
        assert a['source']==source
        inlets=[b['name'] for b in a['boundaries'] if b['type']=='velocity-inlet']
        old.append(dict(family='old',file=source['name'],cells=a['cell_count'],
            inlet_layout='single' if inlets==['inlet'] else 'split',
            inlet_names=';'.join(inlets),min_oq=m['Orthogonal Quality'][1],
            mean_oq=m['Orthogonal Quality'][3],max_skewness=m['Skewness'][2],
            mean_skewness=m['Skewness'][3],max_aspect_ratio=m['FLUENT Aspect Ratio'][2],
            max_size_change=m['Size Change'][2],
            cells_below_oq03=sum(a['distributions']['Orthogonal Quality'][1][-3:]),
            free_faces=a['free_faces'],multi_faces=a['multi_faces'],
            audit=str(path.relative_to(ROOT.parent)),source_sha256=source['sha256']))
    old.sort(key=lambda r:r['cells'])
    new=[]
    for r in json.loads((OUT/'family-summary.json').read_text()):
        new.append(dict(r,family='new',inlet_layout='single',inlet_names='inlet',
            audit=str((OUT/(r['id']+'-reopened.json')).relative_to(ROOT.parent))))
    fields=['family','file','cells','inlet_layout','inlet_names','min_oq','mean_oq',
            'max_skewness','mean_skewness','max_aspect_ratio','max_size_change',
            'cells_below_oq03','free_faces','multi_faces','audit','source_sha256']
    with (OUT/'old-new-quality-comparison.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
        writer.writeheader();writer.writerows(old+new)
    fig,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained')
    for ax,key,label in zip(axes.flat,
        ['min_oq','mean_oq','max_aspect_ratio','max_size_change'],
        ['Minimum orthogonal quality (higher is better)',
         'Mean orthogonal quality (higher is better)',
         'Maximum Fluent aspect ratio','Maximum cell size change']):
        split=[r for r in old if r['inlet_layout']=='split']
        parent=[r for r in old if r['inlet_layout']=='single'][0]
        ax.scatter([r['cells']/1000 for r in split],[r[key] for r in split],
            marker='s',color='#b97a29',label='Old split-inlet meshes',s=45)
        ax.scatter([parent['cells']/1000],[parent[key]],marker='*',s=160,
            color='#333333',label='Old single-inlet 733k')
        ax.plot([r['cells']/1000 for r in new],[r[key] for r in new],
            'o-',color='#276b8f',label='New single-inlet family')
        ax.set(xscale='log',xlabel='Cells (thousands)',ylabel=label)
        ax.set_xticks([60,350,1000,5000],labels=['60','350','1,000','5,000'])
        if key=='min_oq':ax.set_ylim(0,.35)
        if key=='max_size_change':
            anchor=next(r for r in new if r['id']=='curvature-anchor')
            ax.annotate('682k: 882',xy=(anchor['cells']/1000,anchor[key]),
                xytext=(8,-18),textcoords='offset points',fontsize=9)
        ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    axes[0,0].legend(fontsize=8)
    fig.suptitle('Saved Fluent 2025 R2 audits: old meshes and new family\nCounts and inlet layouts differ; this is not a matched solver comparison',fontsize=12)
    fig.savefig(OUT/'old-new-quality-comparison.png',dpi=180)
    report=['# Old versus new mesh quality — 8 October 2026\n\n',
        '**Identity correction:** the human disputes the assignment of the seven audited source files as the intended old Purnanto-style refinement family. Numeric measurements remain tied to exact files; old/new labels are not verified lineage. One mesh was supplied, with refinement levels made for the convergence study. See the [Phase 10 metric register](../experiments/phase-10-single-inlet-mesh-convergence/results.md#mesh-metric-record-and-family-identity).\n\n',
        'Native Fluent 2025 R2 receipts exist for all seven original files. The new family is not uniformly better on every metric. Six original meshes use split `liquidinlet`/`steaminlet` boundaries; only the original 733k uses the same single-inlet layout as the new family. Counts also differ. These are mesh-statistic comparisons, not matched CFD results.\n\n',
        '| Family | File | Actual cells | Inlet | Min OQ | Mean OQ | Max skewness | Mean skewness | Max aspect ratio | Max size change |\n',
        '| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |\n']
    for r in old+new:
        report.append(f"| {r['family']} | `{r['file']}` | {r['cells']:,} | {r['inlet_layout']} | {r['min_oq']:.4f} | {r['mean_oq']:.4f} | {r['max_skewness']:.4f} | {r['mean_skewness']:.4f} | {r['max_aspect_ratio']:.2f} | {r['max_size_change']:.2f} |\n")
    report.append('\n![Old and new mesh metrics](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/old-new-quality-comparison.png)\n\n')
    report.append('Near 680k cells, the new mesh improves mean OQ but worsens minimum OQ, maximum skewness, aspect ratio and size change versus the old split-inlet 680k file. Versus the single-inlet 733k parent, the new 682k improves minimum OQ and maximum skewness, but worsens mean OQ, mean skewness, maximum aspect ratio and maximum size change.\n\n')
    report.append('The earlier seven-of-seven improvement statement refers to each new mesh before and after its recorded improvement pass. It does not mean seven-of-seven improvement over the old meshes. All old and new receipts record zero free/multiply connected boundary faces and positive minimum cell volume. Dimensionless quality metrics are compared here; original files contain mixed raw coordinate scales, so dimensional volume metrics are excluded.\n\n')
    report.append('Evidence: [source manifest](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/source-manifest.json), [comparison CSV with exact audit paths](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/old-new-quality-comparison.csv), [new-family summary](../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-summary.json).\n')
    path=ROOT.parent/'Project/technical/old-new-mesh-quality-20261008.md'
    path.write_text(''.join(report))
    print(path)
    for r in old:print(r['file'],r['cells'],r['min_oq'],r['max_skewness'],r['max_aspect_ratio'],r['max_size_change'])

if __name__=='__main__':main()
