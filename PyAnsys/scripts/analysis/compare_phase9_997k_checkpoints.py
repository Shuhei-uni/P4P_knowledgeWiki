"""Compare archived 997k checkpoints with fixed initial-bulk reference states."""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'PyAnsys/output/phase9-997k-checkpoints/20261009'
FIG = ROOT / 'Project/experiments/phase-09-mesh-convergence/figures/997k-checkpoint-comparison.png'
CHECKPOINTS = [6080, 7080, 8080, 9080, 9103]
CORE = ['pressure_drop', 'carryover', 'bulk', 'collector']


def main():
    history_path = OUT / 'histories.json'
    h = {name: {int(n): v for n, v in rows.items()}
         for name, rows in json.loads(history_path.read_text()).items()}
    source = ROOT / 'PyAnsys/output/phase9-mesh-comparison/20261009/comparison.json'
    # Fix the reference comparison used here; future regenerations retain it.
    frozen = OUT / 'reference-comparison.json'
    if not frozen.exists():
        with frozen.open('xb') as stream:
            stream.write(source.read_bytes())
    reference = json.loads(frozen.read_text())
    targets = {c['label']: c for c in reference['cases'] if c['label'] in ['680k', '2_6M']}
    ids = np.arange(6080, 9104)
    v = lambda name: np.asarray([h[name][int(n)] for n in ids])
    series = {
        'pressure_drop': v('p72s3-pressure-inlet') - v('p72s3-pressure-outlet'),
        'carryover': -v('v2-flux-phase2-steamoutlet'),
        'bulk': v('v2-total-liquid-mass'),
        'collector': -v('v2-applied-absorber'),
        'film': v('p72a-e2.7-ewf-film-mass-total')}
    candidates = []
    for n in CHECKPOINTS:
        signals = {key: float(a[n - 6080]) for key, a in series.items()}
        # N6080's last-1000 starts earlier than the plotted trace.
        tail_ids = range(n - 999, n + 1)
        tail = {
            'pressure_drop': [h['p72s3-pressure-inlet'][i] - h['p72s3-pressure-outlet'][i] for i in tail_ids],
            'carryover': [-h['v2-flux-phase2-steamoutlet'][i] for i in tail_ids],
            'bulk': [h['v2-total-liquid-mass'][i] for i in tail_ids],
            'collector': [-h['v2-applied-absorber'][i] for i in tail_ids]}
        means = {key: float(np.mean(a)) for key, a in tail.items()}
        errors, mean_errors = {}, {}
        for label, target in targets.items():
            errors[label] = {key: 100 * (signals[key] / target['stats'][key]['endpoint'] - 1) for key in CORE}
            mean_errors[label] = {key: 100 * (means[key] / target['stats'][key]['mean'] - 1) for key in CORE}
        candidates.append({'native_iteration': n, 'film_age_ms': (n - 1580) * .0001,
                           'full_feed_updates': n - 5080, 'endpoint': signals,
                           'last1000_mean': means,
                           'last1000_bulk_change_percent_mean': 100 * (tail['bulk'][-1] - tail['bulk'][0]) / means['bulk'],
                           'relative_difference_percent': errors,
                           'mean_absolute_relative_difference_percent': {label: float(np.mean(np.abs(list(e.values())))) for label, e in errors.items()},
                           'last1000_mean_absolute_relative_difference_percent': {label: float(np.mean(np.abs(list(e.values())))) for label, e in mean_errors.items()}})
    result = {'status': 'RECENT_997K_CHECKPOINT_COMPARISON',
              'history_sha256': hashlib.sha256(history_path.read_bytes()).hexdigest(),
              'reference_comparison_sha256': hashlib.sha256(frozen.read_bytes()).hexdigest(),
              'comparison_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'ranking_rule': 'Equal-weight mean absolute relative difference in static pressure difference, boundary liquid outflow, bulk inventory and Eulerian collector removal',
              'ranking_limit': 'Descriptive similarity only; does not select or qualify a scientific endpoint. Correlated metrics and different startup maturity remain.',
              'targets': {label: {'native_iteration': c['end'], 'film_age_ms': c['age_s'] * 1000,
                                  'full_feed_updates': c['end'] - c['full_start'],
                                  'endpoint': {key: c['stats'][key]['endpoint'] for key in [*CORE, 'film']}}
                          for label, c in targets.items()},
              'candidates': candidates}
    (OUT / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    with (OUT / 'comparison.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['native_iteration', 'film_age_ms', 'full_feed_updates',
                         'static_pressure_difference_kPa', 'boundary_liquid_outflow_kg_s',
                         'bulk_liquid_kg', 'collector_removal_kg_s', 'reported_film_g',
                         'mean_absolute_difference_to_680k_percent', 'mean_absolute_difference_to_2_6M_percent'])
        for c in candidates:
            a = c['endpoint']; e = c['mean_absolute_relative_difference_percent']
            writer.writerow([c['native_iteration'], c['film_age_ms'], c['full_feed_updates'],
                             a['pressure_drop'] / 1000, a['carryover'], a['bulk'], a['collector'], a['film'] * 1000,
                             e['680k'], e['2_6M']])
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.2))
    specs = [('pressure_drop', 'Static pressure difference', 'kPa', .001),
             ('carryover', 'Boundary liquid flow at steam outlet', 'kg/s', 1),
             ('bulk', 'Bulk liquid inventory', 'kg', 1),
             ('collector', 'Eulerian collector removal', 'kg/s', 1)]
    for ax, (key, title, unit, scale) in zip(axes.flat, specs):
        ax.plot(ids, series[key] * scale, color='#4477AA', lw=1.4, label='997k raw history')
        ax.plot(CHECKPOINTS, [c['endpoint'][key] * scale for c in candidates], 'o',
                color='#4477AA', ms=5, label='997k saved checkpoints')
        ax.plot(7080, next(c['endpoint'][key] * scale for c in candidates if c['native_iteration'] == 7080),
                'o', ms=9, markerfacecolor='none', markeredgecolor='#222222', label='N7080: closest overall bulk match')
        for label, color, line in [('680k', '#228833', '--'), ('2_6M', '#CC8800', ':')]:
            target = targets[label]
            ax.axhline(target['stats'][key]['endpoint'] * scale, color=color, ls=line,
                       label=f"{label.replace('2_6M', '2.6M')} selected N{target['end']}")
        ax.set(title=title, xlabel='997k native iteration', ylabel=unit)
        ax.set_xticks([6080, 7080, 8080, 9080])
        ax.grid(alpha=.23)
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('997k checkpoints compared with selected 680k and 2.6M states', fontsize=14, y=.98)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc='upper center', bbox_to_anchor=(.5, .95), ncol=3, frameon=False, fontsize=9)
    fig.text(.5, .015, '997k checkpoints: N6080, N7080, N8080, N9080, N9103. All samples have full feed and active bulk.\nReference lines are saved endpoint values. Similarity does not establish mesh convergence or equal maturity.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.83, bottom=.14, hspace=.4, wspace=.25)
    fig.savefig(FIG, dpi=190)
    fig.savefig(FIG.with_suffix('.pdf'))
    plt.close(fig)
    for c in candidates:
        print('N' + str(c['native_iteration']), 'endpoint score',c['mean_absolute_relative_difference_percent'],
              'window score', c['last1000_mean_absolute_relative_difference_percent'])


if __name__ == '__main__':
    main()
