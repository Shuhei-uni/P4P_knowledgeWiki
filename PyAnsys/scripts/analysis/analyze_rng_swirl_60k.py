"""Paired native-history comparison of the recorded RNG 0.07/0.1 trials."""
from pathlib import Path
import json
import re
import hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'PyAnsys/output/server3-report-reduction/20261009/analysis'
FIG = ROOT / 'Project/experiments/phase-07-2a-wall-liquid-routing/rng-swirl-60k/figures'
FIG.mkdir(exist_ok=True)
a = json.loads((OUT / 'histories.json').read_text())
b = json.loads((OUT / 'baseline-histories.json').read_text())
NAMES = {
    'pressure_drop_Pa': ('p72s3-pressure-inlet', 'p72s3-pressure-outlet'),
    'liquid_inventory_kg': ('v2-total-liquid-mass',),
    'liquid_outlet_kg_s': ('v2-flux-phase2-steamoutlet',),
    'collector_removal_kg_s': ('v2-applied-absorber',),
    'film_mass_kg': ('p72a-e2.7-ewf-film-mass-total',),
    'max_film_thickness_m': ('p72a-e2.7-ewf-thickness-max',),
    'film_Courant': ('p72a-e2.7-ewf-courant-max',),
}


def values(h, key, ids):
    keys = NAMES[key]
    v = np.array([h[keys[0]][str(i)] for i in ids])
    if len(keys) == 2:
        v -= np.array([h[keys[1]][str(i)] for i in ids])
    if key in ['liquid_outlet_kg_s', 'collector_removal_kg_s']:
        v = -v
    return v


result = {'windows': {}, 'source_hashes': {}, 'report_flux_definition':
          'Negative of native boundary-only file flux; do not use source-inclusive API totals.'}
for lo, hi in [(8900, 9080), (9160, 9340)]:
    ids = list(range(lo, hi + 1, 20))
    window = {'paired_native_iterations': ids, 'metrics': {}}
    for key in NAMES:
        av, bv = values(a, key, ids), values(b, key, ids)
        window['metrics'][key] = {'baseline_mean': float(bv.mean()), 'swirl01_mean': float(av.mean()),
                                 'difference': float(av.mean() - bv.mean()),
                                 'relative_difference_percent': float(100 * (av.mean() / bv.mean() - 1))}
    result['windows'][f'{lo}-{hi}'] = window
for name in ['histories.json', 'baseline-histories.json']:
    result['source_hashes'][name] = hashlib.sha256((OUT / name).read_bytes()).hexdigest()

ids = list(range(8720, 9361, 20))
fig, axes = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True)
for ax, key, factor, label in [
    (axes[0, 0], 'pressure_drop_Pa', 1, 'Pressure-drop change (Pa)'),
    (axes[0, 1], 'liquid_outlet_kg_s', 1000, 'Outlet liquid-flow change (g/s)'),
    (axes[1, 0], 'collector_removal_kg_s', 1, 'Collector-removal change (kg/s)'),
]:
    delta = (values(a, key, ids) - values(b, key, ids)) * factor
    ax.plot(np.array(ids) - 8080, delta, '.-', color='#2C8ED2', lw=1)
    ax.axhline(0, color='0.5', lw=.7)
    ax.set_ylabel(label)
ax = axes[1, 1]
for key, label, color in [('liquid_inventory_kg', 'Bulk liquid inventory', '#2C8ED2'),
                          ('film_mass_kg', 'Film mass', '#FC8500')]:
    delta = 100 * (values(a, key, ids) / values(b, key, ids) - 1)
    ax.plot(np.array(ids) - 8080, delta, '.-', label=label, color=color, lw=1)
ax.axhline(0, color='0.5', lw=.7)
ax.set_ylabel('Inventory change (%)')
ax.legend(fontsize=8)
for ax in axes.flat:
    ax.grid(alpha=.2)
for ax in axes[1]:
    ax.set_xlabel('Iterations since N8080 reset')
fig.suptitle('RNG swirl factor 0.1 minus 0.07 — matched pre-divergence samples')
fig.tight_layout()
fig.savefig(FIG / 'swirl-factor-paired-changes.png', dpi=180)
plt.close(fig)

text = (OUT.parent / 'continuation-transcript.txt').read_text(errors='replace')
film = [tuple(map(float, match.groups())) for match in
        re.finditer(r'Film time = ([\deE+.-]+).*?max_cfl: ([\deE+.-]+)', text)]
film_ids = [8080 + round((time - .00065) / 1e-7) for time, cfl in film]
first_film = next((i for i, row in zip(film_ids, film) if row[1] > .01), None)
baseline_first = next(int(i) for i, v in sorted(b[NAMES['film_Courant'][0]].items(), key=lambda x: int(x[0]))
                      if int(i) > 8080 and v > .01)
res = []
for line in text.splitlines():
    cells = line.split()
    if len(cells) >= 10 and cells[0].isdigit() and 8703 < int(cells[0]) <= 9380:
        try:
            res.append([int(cells[0])] + list(map(float, cells[1:8])))
        except ValueError:
            pass
res = np.array(res)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
base_ids = sorted(int(i) for i in b[NAMES['film_Courant'][0]] if 9200 <= int(i) <= 9518)
axes[0].semilogy(base_ids, values(b, 'film_Courant', base_ids), label='0.07 baseline', color='0.4')
axes[0].semilogy(film_ids, [v[1] for v in film], label='0.1 native stream', color='#2C8ED2')
axes[0].set_xlim(9200, 9520)
axes[0].set_ylabel('Maximum film Courant')
axes[0].axvline(first_film, color='#2C8ED2', ls=':', lw=1)
axes[0].axvline(baseline_first, color='0.4', ls=':', lw=1)
axes[0].legend(fontsize=8)
for index, label, color in [(1, 'Continuity', '#46D2BA'), (2, 'x momentum', '#A199D9'),
                            (3, 'y momentum', '#FA1900'), (4, 'z momentum', '#2C8ED2'),
                            (5, 'k', '#FC8500'), (6, 'epsilon', '#8BDD00')]:
    axes[1].semilogy(res[:, 0], res[:, index], '.-', label=label, color=color, lw=1)
axes[1].set_xlim(9200, 9385)
axes[1].set_ylabel('Scaled residual — 0.1 run')
axes[1].legend(fontsize=8, ncol=2)
for ax in axes:
    ax.set_xlabel('Native iteration')
    ax.grid(alpha=.2)
fig.suptitle('Failure tail: film growth and bulk residuals; residual output every 20 iterations')
fig.tight_layout()
fig.savefig(FIG / 'swirl-factor-failure-tail.png', dpi=180)
plt.close(fig)
result.update(swirl01_first_native_film_Courant_above_001=first_film,
              baseline_first_report_film_Courant_above_001=baseline_first,
              swirl01_terminal_iteration=9380, baseline_terminal_iteration=9519,
              manual_swirl_change_iteration='NOT_RECORDED; constant 0.1 confirmed at N8703',
              parent_swirl_constant=.07, final_pair_physical_comparison_valid=False)
(OUT / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result['windows'], indent=2))
