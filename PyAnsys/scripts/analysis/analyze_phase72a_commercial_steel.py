"""Five requested diagnostics from the verified N25815–N29815 continuation."""
from pathlib import Path
import csv
import json
import sys
import math
import hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from run_phase72a_adaptive_film import history, FILM, ROW
OUT = ROOT / 'output/phase72a-commercial-steel/20261006'
RAW = OUT / 'raw/N29815-20261007'
DOC = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/commercial-steel'
FIG = DOC / 'figures'
START, END = 25815, 29815


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    source = json.loads((RAW / 'extraction.json').read_text())
    parent = json.loads((OUT / 'loaded-parent.json').read_text())
    assert source['native_iteration'] == END
    FIG.mkdir(exist_ok=True)
    names = {'bulk':'v2-total-liquid-mass', 'flux':'v2-flux-phase2-steamoutlet',
             'film':'p72a-e2.7-ewf-film-mass-total', 'accretion':'p72a-e2.7-ewf-secondary-phase-mass-total',
             'drainage_mass':'p72a-e2.7-ewf-outflow-mass-total', 'cfl':'p72a-e2.7-ewf-courant-max'}
    histories = {key:history((RAW / f'{name}.out').read_text()) for key,name in names.items()}
    x = np.arange(START, END+1)
    for key, h in histories.items():
        assert set(x).issubset(h), f'Missing native report rows: {key}'
        assert all(math.isfinite(h[int(i)]) for i in x)
    values = {key:np.array([h[int(i)] for i in x]) for key,h in histories.items()}
    t0 = parent['film']['film_elapsed_time']
    time_s = t0 + (x - START)*1e-6
    assert abs(time_s[-1] - source['film']['film_elapsed_time']) < 1e-12
    residuals = {}
    printed_cfl = []
    transcripts = [(START,25835,'batch-N25815-N25835.trn'),
                   (25835,26815,'native-continuation-N25835-N26815.trn'),
                   (26815,END,'native-continuation-N26815-N29815.trn')]
    for start,end,name in transcripts:
        text = (RAW / name).read_text()
        clocks = [list(map(float,m.groups())) for m in FILM.finditer(text)]
        assert len(clocks) == end-start, f'Film clock coverage: {name}'
        expected_time = t0 + (np.arange(start+1,end+1)-START)*1e-6
        assert np.max(abs(np.array(clocks)[:,0] - expected_time)) < 5.1e-8
        assert all(abs(c[1] - 1e-6)<1e-15 for c in clocks)
        printed_cfl.extend(c[2] for c in clocks)
        for line in text.splitlines():
            match = ROW.match(line)
            if match:
                i = int(match[1])
                if START <= i <= END:
                    parts = line.split()[1:8]
                    if len(parts) == 7:
                        v = list(map(float, parts))
                        # Segment-start lines repeat the previous endpoint; they are not new solves.
                        if i in residuals:
                            assert residuals[i] == v, f'Conflicting residual join N{i}'
                        residuals[i] = v
    assert set(x).issubset(residuals), 'Continuity/residual history has gaps'
    continuity = np.array([residuals[int(i)][0] for i in x])
    assert np.all(np.isfinite(continuity)) and np.all(continuity>0)
    with (ROOT / 'output/phase72a-stage3-film-development-server1/20261005/selected-history/selected-case-history-N25815.csv').open() as stream:
        baseline = next(row for row in csv.DictReader(stream) if int(row['native_iteration']) == START)
    drainage = np.r_[np.nan, np.diff(values['drainage_mass'])/1e-6]
    storage = np.r_[np.nan, np.diff(values['film'])/1e-6]
    tail = x >= END-499
    metrics = {}
    for key in ['bulk','flux','film','accretion']:
        a = values[key]
        metrics[key] = {'parent':float(a[0]), 'final':float(a[-1]),
                        'change_percent':float(100*(a[-1]-a[0])/abs(a[0])),
                        'final500_mean':float(np.mean(a[tail])),
                        'final500_min':float(np.min(a[tail])), 'final500_max':float(np.max(a[tail]))}
    metrics['drainage'] = {'parent':float(baseline['drainage_kg_s']), 'final':float(drainage[-1]),
                            'final500_mean':float(np.mean(drainage[tail]))}
    metrics['continuity'] = {'inherited_last_bulk_solve':float(continuity[0]),'first_updated':float(continuity[1]),
                             'final':float(continuity[-1]), 'peak':float(np.max(continuity[1:])),
                             'final500_mean':float(np.mean(continuity[tail])),
                             'final500_min':float(np.min(continuity[tail])), 'final500_max':float(np.max(continuity[tail]))}
    integrated_accretion = float(np.sum(values['accretion'][1:])*1e-6)
    inventory_gain = float(values['film'][-1]-values['film'][0])
    drained = float(values['drainage_mass'][-1]-values['drainage_mass'][0])
    summary = {'native_start':START,'native_end':END,'updates':END-START,
               'parent_film_time_ms':t0*1000,'final_film_time_ms':time_s[-1]*1000,'added_film_time_ms':4.,
               'metrics':metrics, 'film_mean_accretion_kg_s':integrated_accretion/.004,
               'film_mean_drainage_kg_s':drained/.004,'film_mean_storage_kg_s':inventory_gain/.004,
               'film_ledger_error_percent':100*abs(inventory_gain+drained-integrated_accretion)/abs(integrated_accretion),
               'peak_film_cfl':max(printed_cfl),'report_points':len(x),'carrier_solve_rows':len(x)-1,
               'continuity_parent_limit':'N25815 holds the inherited N5080 residual; bulk equations were frozen in between',
               'roughness_causality_limit':'Bulk equations restored and film step changed with roughness; no isolated comparison',
               'film_inner_residuals':'Unavailable under inherited alternative implicit scheme; not counted as passed',
               'final500_film_storage_kg_s':float(np.mean(storage[tail])),
               'bulk_minimum_kg':float(np.min(values['bulk'])),
               'bulk_minimum_iteration':int(x[np.argmin(values['bulk'])]),
               'steady_film':False, 'new_solve_calls':0}
    dump(OUT / 'analysis-summary.json',summary)
    dump(OUT / 'carrier-residuals.json',residuals)
    with (OUT / 'requested-diagnostics-N25815-N29815.csv').open('w') as stream:
        writer = csv.writer(stream)
        writer.writerow(['native_iteration','film_time_s','bulk_liquid_kg','phase2_steamoutlet_signed_kg_s',
                         'ewf_liquid_kg','accretion_kg_s','drainage_kg_s','film_storage_kg_s','scaled_continuity'])
        for j,i in enumerate(x):
            writer.writerow([i,time_s[j],values['bulk'][j],values['flux'][j],values['film'][j],
                             values['accretion'][j],drainage[j],storage[j],continuity[j]])
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10})
    labels = [('bulk-liquid-inventory','Bulk liquid inventory','Liquid mass (kg)'),
              ('phase2-steamoutlet-flux','Phase-2 steamoutlet boundary flux','Signed flux (kg/s)'),
              ('ewf-liquid-inventory','EWF liquid inventory','Film mass (kg)'),
              ('film-mass-rates','Film accretion and drainage','Mass rate (kg/s)'),
              ('continuity','Scaled continuity residual','Scaled continuity')]
    def draw(ax,j):
        if j<3:
            key=['bulk','flux','film'][j]
            ax.plot(x,values[key],lw=.9,color='#1766a1')
            ax.axhline(values[key][0],color='#666666',ls='--',lw=.9,label='Saved parent value')
            if j==1:
                ax.text(.01,.05,'Negative flux = liquid leaves steamoutlet; user-source term excluded',transform=ax.transAxes,fontsize=8,bbox={'facecolor':'white','edgecolor':'none','alpha':.85})
        elif j==3:
            ax.plot(x,values['accretion'],label='Accretion',lw=1,color='#1766a1')
            ax.plot(x[1:],drainage[1:],label='Drainage: cumulative outflow / actual film step',lw=1,color='#d77816')
            ax.axhline(float(baseline['accretion_kg_s']),color='#1766a1',ls='--',lw=.8,label='Parent accretion')
            ax.axhline(float(baseline['drainage_kg_s']),color='#d77816',ls='--',lw=.8,label='Parent drainage')
        else:
            ax.semilogy(x[1:],continuity[1:],lw=.8,color='#1766a1')
            ax.set_ylim(1e-3, max(continuity[1:])*1.4)
            ax.scatter([START],[continuity[0]],s=22,color='#777777',label='Inherited last bulk residual (N5080)',zorder=4)
        ax.axvspan(END-499,END,color='#dca65c',alpha=.13,label='Final 500 iterations')
        ax.set_title(labels[j][1],loc='left')
        ax.set_ylabel(labels[j][2])
        ax.set_xlim(START,END)
        ax.ticklabel_format(axis='x',useOffset=False,style='plain')
        ax.grid(alpha=.2)
        if j in [0,3,4]:ax.legend(fontsize=7,loc='best',ncol=2 if j==3 else 1)
    fig,axes=plt.subplots(5,1,figsize=(10,12),sharex=True)
    for j,ax in enumerate(axes):draw(ax,j)
    axes[-1].set_xlabel('Native iteration')
    fig.suptitle('Commercial steel roughness: 0.5 → 0.045 mm at N25815\nBulk equations restored; 4000 updates; 4 ms additional film time',fontsize=13)
    fig.tight_layout(rect=(0,0,1,.955))
    fig.savefig(FIG / 'requested-diagnostics-N29815.png',dpi=180)
    fig.savefig(FIG / 'requested-diagnostics-N29815.pdf')
    plt.close(fig)
    for j,(slug,title,ylabel) in enumerate(labels):
        fig,ax=plt.subplots(figsize=(8,4.2))
        draw(ax,j)
        ax.set_xlabel('Native iteration')
        fig.tight_layout()
        fig.savefig(FIG / f'{slug}.png',dpi=180)
        fig.savefig(FIG / f'{slug}.pdf')
        plt.close(fig)
    manifest = {'inputs':{str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in RAW.iterdir() if p.is_file()},
                'figure_source':'native reports and 3 transcript segments; 20-update probe uses retained complete client stream',
                'coordinate':'native iteration; film time reconstructed from verified fixed 1 us accepted steps and counter',
                'rate_formula':'drainage=(D[n]-D[n-1])/1e-6; storage=(M[n]-M[n-1])/1e-6',
                'csv':str(OUT / 'requested-diagnostics-N25815-N29815.csv'), 'endpoint_pair':source['pair']}
    dump(OUT / 'figure-manifest.json',manifest)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
