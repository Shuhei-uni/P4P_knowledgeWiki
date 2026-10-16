"""Replot roughness evidence and draw the report's conceptual liquid-route map.

No Fluent connection or source-data changes. Run with PyAnsys/.venv/bin/python.
The overview is editable as SVG and Python, with a PDF for document export.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Project/Final research report/Shuhei Report/figures'
SOURCE = ROOT / 'PyAnsys/output/phase72a_family_r/analysis-20260923T054600Z-cs-sensitivity-v2/tail-summary.csv'
EXPECTED = '869db8e0b06e411c773cf02b82e313c15541f73a5afab6c5094da39c0ef44be0'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(fig, stem, record):
    outputs = {}
    for suffix in ('png', 'pdf', 'svg'):
        p = OUT / f'{stem}.{suffix}'
        fig.savefig(p, dpi=300, facecolor='white', bbox_inches='tight')
        outputs[suffix] = {'filename': p.name, 'sha256': digest(p)}
    record.update(figure=stem, output=outputs,
                  script={'path': str(Path(__file__).relative_to(ROOT)), 'sha256': digest(Path(__file__))},
                  software={'matplotlib': matplotlib.__version__, 'numpy': np.__version__})
    record['plot_text'] = [t.get_text() for t in fig.findobj(matplotlib.text.Text) if t.get_text()]
    (OUT / f'{stem}.provenance.json').write_text(json.dumps(record, indent=2, ensure_ascii=False)+'\n')
    plt.close(fig)

def roughness():
    if digest(SOURCE) != EXPECTED:
        raise ValueError('Roughness source hash changed')
    with SOURCE.open(newline='') as f:
        rows = list(csv.DictReader(f))
    height = rows[:8]
    x = np.array([float(r['k_s_m'])*1000 for r in height])
    y = np.array([-float(r['phase2_outlet_mean_last_500_kg_s']) for r in height])
    loss = -float(height[-1]['whole_run_total_liquid_mass_change_kg'])
    assert np.isclose(loss, 187.10913983241068, rtol=0, atol=1e-10)
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.2), sharey=True)
    fig.subplots_adjust(left=.10, right=.98, bottom=.18, top=.76, wspace=.18)
    axes[0].plot(x, y, 'o-', color='#0072B2', lw=1.2, ms=4)
    axes[0].axhline(y[0], color='#777777', linestyle='--', linewidth=.8)
    axes[0].set(xlabel='Roughness height, kₛ (mm)', ylabel='Outward bulk-liquid flow (kg/s)',
                title='(a) Height sweep at Cₛ = 0.5', ylim=(0, 36))
    axes[0].annotate('Small roughness raises outlet flow', (x[1], y[1]), xytext=(1.0, 33),
                     fontsize=7.5, arrowprops={'arrowstyle':'-', 'color':'#777777', 'lw':.7})
    axes[0].annotate(f'8 mm: outlet −44.09%\nBulk inventory loss: {loss:.3f} kg',
                     (x[-1], y[-1]), xytext=(2.3, 5.8), fontsize=7.5,
                     arrowprops={'arrowstyle':'-', 'color':'#777777', 'lw':.7})
    for k, color in ((.0005, '#0072B2'), (.002, '#D55E00')):
        selected = sorted([r for r in rows if float(r['k_s_m']) == k], key=lambda r: float(r['C_s']))
        axes[1].plot([float(r['C_s']) for r in selected],
                     [-float(r['phase2_outlet_mean_last_500_kg_s']) for r in selected],
                     'o-', color=color, lw=1.2, ms=4, label=f'{k*1000:g} mm roughness')
    axes[1].axhline(y[0], color='#777777', linestyle='--', linewidth=.8, label='Smooth-wall continuation')
    axes[1].set(xlabel='Roughness constant, Cₛ', title='(b) Constant sweep at fixed height')
    axes[1].legend(frameon=False, fontsize=7.5, loc='upper right')
    for ax in axes:
        ax.grid(color='#dddddd', linewidth=.6, alpha=.7)
        ax.set_axisbelow(True)
    fig.suptitle('Roughness response is non-monotonic\nFilm disabled; means over iterations 8087–8586', fontsize=10, y=.97)
    save(fig, 'results-described-roughness', {
        'processing':'Unchanged twelve-case CSV means; lines connect settings and are not fitted curves. Inventory annotation uses whole-run change, separately from the tail-500 outlet mean.',
        'sources':{'roughness_summary':{'path':str(SOURCE.relative_to(ROOT)), 'sha256':EXPECTED}},
        'checks':{'height_sweep_mm':x.tolist(), 'height_sweep_outward_kg_s':y.tolist(),
                  'mean_window':[8087,8586], 'whole_run_R7_inventory_loss_kg':loss},
        'claim_limit':'Outlet reduction with depletion does not establish increased collection or an optimum roughness.'})

def overview():
    fig, ax = plt.subplots(figsize=(9.3, 4.7))
    fig.subplots_adjust(left=.01, right=.99, top=.92, bottom=.04)
    ax.set(xlim=(0,20), ylim=(0,10))
    ax.axis('off')
    colours = {'bulk':'#0072B2', 'film':'#B86D20', 'droplets':'#8A4C9F',
               'outlet':'#B54736', 'removal':'#268066', 'inlet':'#666666'}
    nodes = {
        'inlet':(1.7,6.2,'Inlet liquid','inlet'),
        'bulk':(5.5,6.2,'Bulk liquid\nstorage and\ntransport','bulk'),
        'film':(9.3,6.2,'Wall film\nstorage and\ntransport','film'),
        'droplets':(13.1,6.2,'Released droplets\ntracked\nseparately','droplets'),
        'outlet':(17.5,6.2,'Liquid leaving\nwith steam','outlet'),
        'collector':(5.5,2.4,'Bulk collector\nnumerical\nmass sink','removal'),
        'native':(9.3,2.4,'Native film\noutflow at\nfilm-domain edge','removal'),
        'direct':(13.1,2.4,'Direct film drain\nnumerical\nmass sink','removal'),
    }
    for key,(x,y,label,c) in nodes.items():
        ax.add_patch(FancyBboxPatch((x-1.5,y-.75),3,1.50,boxstyle='round,pad=0.05,rounding_size=0.12',
                                    linewidth=1.1,edgecolor=colours[c],facecolor='white'))
        ax.text(x,y,label,ha='center',va='center',fontsize=11,color=colours[c])
    def arrow(points, label=None, label_xy=None, color='#555555', dashed=False):
        for i,(p,q) in enumerate(zip(points,points[1:])):
            ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>' if i==len(points)-2 else '-',
                                         mutation_scale=10,lw=1,color=color,
                                         linestyle='--' if dashed else '-',shrinkA=0,shrinkB=0))
        if label:
            ax.text(*label_xy,label,ha='center',va='center',fontsize=10,color=color,
                    bbox={'facecolor':'white','edgecolor':'none','pad':1.5})
    arrow([(3.25,6.2),(3.95,6.2)],'feed',(3.6,6.65))
    arrow([(7.05,6.2),(7.75,6.2)],'accretion',(7.4,6.65))
    arrow([(5.5,6.99),(5.5,9.0),(17.5,9.0),(17.5,6.99)],
          'Bulk liquid leaving with steam',(11.5,9.05),colours['outlet'])
    arrow([(9.3,6.99),(9.3,7.65),(13.1,7.65),(13.1,6.99)],
          'stripping / edge separation',(11.2,7.7),colours['droplets'])
    arrow([(13.1,5.41),(13.1,4.75),(9.3,4.75),(9.3,5.41)],
          'droplet collection',(11.2,4.75),colours['droplets'])
    arrow([(14.65,6.2),(15.95,6.2)],'possible\nescape',(15.3,6.95),colours['outlet'],True)
    arrow([(5.5,5.41),(5.5,3.19)],'contact\ncapture',(5.5,4.25),colours['removal'])
    arrow([(8.6,5.41),(8.6,3.19)],'edge\noutflow',(8.6,3.75),colours['removal'])
    arrow([(10.5,5.41),(10.5,4.0),(13.1,4.0),(13.1,3.19)],
          'local removal',(12.0,4.0),colours['removal'])
    ax.text(10, .75, 'Internal transfer changes the liquid representation; removal takes liquid out of the model.',
            ha='center',fontsize=8.3)
    ax.text(10, .25, 'Routes tested in separate configurations • Frozen bulk does not advance reciprocal depletion',
            ha='center',fontsize=7.5,color='#555555')
    fig.suptitle('Wall capture is one stage of collection',fontsize=12,y=.98)
    save(fig,'report-liquid-destinations-overview',{
        'type':'Conceptual map; no measured rates, geometry or mass-balance closure implied.',
        'basis':['draft/02-model-and-methods.md §§3.2–3.3', 'draft/03-results.md §§4.7,4.10–4.11',
                 'draft/04-discussion-conclusions-and-future-work.md §§5.3–5.6'],
        'nodes':{k:{'x':v[0],'y':v[1],'label':v[2],'role':v[3]} for k,v in nodes.items()},
        'internal_transfers':['bulk → film: accretion','film → droplets: stripping / edge separation',
                              'droplets → film: droplet collection'],
        'external_routes':['bulk → steam outlet','droplets → steam outlet: possible escape, fate unresolved',
                           'bulk → numerical collector','film → native edge outflow','film → numerical direct drain'],
        'claim_limit':'Separate configurations; droplet fate requires tracking. Native film-edge outflow is distinct from the direct sink and physical brine discharge. Frozen-bulk film development is not full-model conservation.',
        'connected_diagram_tool':'Whimsical generation attempted; account object limit blocked content creation. Local SVG/PDF/Python fallback.'})

if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none',
                         'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    roughness()
    overview()
    print('Roughness source hash and inventory checks PASS; overview PNG/PDF/SVG generated.')
