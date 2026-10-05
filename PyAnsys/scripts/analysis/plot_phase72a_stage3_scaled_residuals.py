"""Plot the seven native scaled carrier residuals for the selected Stage 3 startup."""
from pathlib import Path
import csv
import hashlib
import json
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
EARLY = ROOT / 'output/phase72a-stage3-early-ewf-server1/20261005'
OLD = ROOT / 'output/phase72a-lineage-N45606/20261005'
OUT = ROOT / 'output/phase72a-stage3-film-development-server1/20261005/selected-history'
DEST = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development'
NAMES = ['continuity', 'x-velocity', 'y-velocity', 'z-velocity', 'k', 'epsilon', 'vf-phase-2']


def main():
    parent_path = OLD / 'carrier-residuals.csv'
    startup_path = EARLY / 'carrier-residuals.json'
    transcript_path = EARLY / 'run-transcript.txt'
    parent = {int(row['native_iteration']): [float(row[k]) for k in NAMES]
              for row in csv.DictReader(parent_path.open()) if int(row['native_iteration']) <= 1580}
    startup = {int(k): v for k, v in json.loads(startup_path.read_text()).items()}
    pattern = re.compile(r'^\s*(\d+)\s+' + r'\s+'.join([r'([\d.+-]+e[+-]\d+)'] * 7), re.M)
    native = {}
    for match in pattern.finditer(transcript_path.read_text()):
        n, values = int(match[1]), [float(v) for v in match.groups()[1:]]
        if n in native:
            assert native[n] == values, f'Conflicting native residual N{n}'
        native[n] = values
    assert all(startup[n] == native[n] for n in range(1580, 5081))
    assert np.allclose(parent[1580], startup[1580], rtol=1e-5, atol=1e-12), 'Parent join differs'
    rows = {**parent, **{n: startup[n] for n in range(1581, 5081)}}
    assert sorted(rows) == list(range(1, 5081)), 'Residual coverage gap'
    x = np.array(sorted(rows))
    y = np.array([rows[int(n)] for n in x])
    assert y.shape == (5080, 7) and np.isfinite(y).all() and (y > 0).all()
    fig, ax = plt.subplots(figsize=(12, 5.8), layout='constrained')
    for j, name in enumerate(NAMES):
        ax.semilogy(x, y[:, j], lw=.8, label=name)
    for n, label in [(1580, 'A: Coupled + EWF'), (2080, 'B: inlet ramp'), (4080, 'C: full feed')]:
        ax.axvline(n, color='0.5', ls='--', lw=.7)
        ax.text(n + 30, .98, label, transform=ax.get_xaxis_transform(), va='top', fontsize=9)
    ax.set(xlim=(0, 5080), xlabel='Native carrier iteration', ylabel='Scaled residual (log scale)',
           title='Stage 3 — scaled carrier residuals, N1–N5080')
    ax.grid(alpha=.2)
    ax.legend(loc='lower left', ncol=4, fontsize=9)
    fig.text(.5, -.025, 'Bulk equations frozen after N5080; no later carrier residuals plotted. Raw values; no smoothing.',
             ha='center', fontsize=9)
    slug = 'selected-scaled-residuals-N5080'
    figures = DEST / 'figures'
    figures.mkdir(parents=True, exist_ok=True)
    paths = [figures / f'{slug}.png', figures / f'{slug}.pdf']
    for path in paths:
        fig.savefig(path, dpi=180, bbox_inches='tight')
    plt.close(fig)
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f'{slug}.csv'
    with csv_path.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['native_iteration', *NAMES])
        writer.writerows([n, *rows[n]] for n in sorted(rows))
    record = {'status': 'VERIFIED_DATA_VISUAL_QA_PENDING', 'range': [1, 5080], 'rows': 5080,
              'missing_coordinates': [], 'residuals': NAMES, 'startup_native_crosscheck': 'PASS',
              'parent_join': 'PASS', 'final_scaled_residuals': dict(zip(NAMES, rows[5080])),
              'sources': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in [parent_path, startup_path, transcript_path]],
              'limits': ['Native scaling retained without renormalisation.',
                         'Carrier equations frozen after N5080; no later carrier residuals.',
                         'EWF inner residuals are separate and are not included.'],
              'figures': [str(p) for p in paths], 'csv': str(csv_path)}
    (OUT / f'{slug}-manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'rows': len(rows), 'figures': record['figures'], 'final': record['final_scaled_residuals']}))


if __name__ == '__main__':
    main()
