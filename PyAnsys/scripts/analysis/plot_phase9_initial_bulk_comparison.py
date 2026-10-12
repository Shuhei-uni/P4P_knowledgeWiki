"""Compare human-selected Phase 9 endpoints using recorded native histories."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN = ROOT / 'PyAnsys/output/phase9-mesh-convergence/20261007'
SERVER4 = ROOT / 'PyAnsys/output/phase9-mesh-convergence-server4/20261007'
HISTORY_OUT = ROOT / 'PyAnsys/output/phase9-mesh-comparison/20261009'
PREVIOUS_OUT = HISTORY_OUT / 'selected-N8080'
OUT = HISTORY_OUT / 'selected-N8080-last2000'
WINDOW_UPDATES = 2000
FIGURES = ROOT / 'Project/experiments/phase-09-mesh-convergence/figures'
MESHES = [('60k', 60964), ('342k', 342609), ('680k', 679970),
          ('997k', 997604), ('2_6M', 2596657)]
COLORS = ['#4477AA', '#EE6677', '#228833', '#AA3377', '#CCBB44']
NAMES = {
    'carryover': 'v2-flux-phase2-steamoutlet',
    'bulk': 'v2-total-liquid-mass',
    'collector': 'v2-applied-absorber',
    'film': 'p72a-e2.7-ewf-film-mass-total',
    'accretion': 'p72a-e2.7-ewf-secondary-phase-mass-total',
    'thickness_mean': 'p72a-e2.7-ewf-thickness-awavg',
    'thickness_max': 'p72a-e2.7-ewf-thickness-max',
    'speed_mean': 'p72a-e2.7-ewf-velocity-mag-awavg',
    'speed_max': 'p72a-e2.7-ewf-velocity-mag-max',
    'courant': 'p72a-e2.7-ewf-courant-max',
    'film_outflow': 'p72a-e2.7-ewf-outflow-mass-total',
    'vapor_outflow': 'v2-flux-phase1-steamoutlet',
}
CORE = [('pressure_drop', 'Area-averaged static pressure difference', 'kPa', .001),
        ('carryover', 'Boundary liquid flow at steam outlet', 'kg/s', 1),
        ('bulk', 'Bulk liquid inventory', 'kg', 1),
        ('collector', 'Eulerian collector removal', 'kg/s', 1)]
UNITS = {'pressure_drop': 'Pa', 'carryover': 'kg/s', 'bulk': 'kg',
         'collector': 'kg/s', 'film': 'kg', 'accretion': 'native reported source value',
         'thickness_mean': 'm', 'thickness_max': 'm', 'speed_mean': 'm/s',
         'speed_max': 'm/s', 'courant': 'dimensionless', 'film_outflow': 'kg',
         'vapor_outflow': 'kg/s', 'carryover_percent_feed': '%',
         'collector_percent_feed': '%', 'vapor_net_percent_feed': '%'}


def source_path(path):
    # Preserve the inputs used here. Other chats can advance campaign manifests.
    # Existing snapshots are never overwritten on regeneration.
    if not path.is_relative_to(OUT):
        snapshot = OUT / 'source-records' / path.relative_to(ROOT)
        if not snapshot.exists():
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            with snapshot.open('xb') as stream:
                previous_snapshot = PREVIOUS_OUT / 'source-records' / path.relative_to(ROOT)
                source = previous_snapshot if previous_snapshot.exists() else path
                stream.write(source.read_bytes())
        path = snapshot
    return path


def read(path):
    return json.loads(source_path(path).read_text())


def stats(values):
    a = np.asarray(values)
    avg = float(a.mean())
    return {'endpoint': float(a[-1]), 'mean': avg, 'min': float(a.min()),
            'max': float(a.max()), 'first': float(a[0]),
            'net_change': float(a[-1] - a[0]),
            'net_change_percent_mean': 100 * float(a[-1] - a[0]) / max(abs(avg), 1e-30),
            'range_percent_mean': 100 * float(np.ptp(a)) / max(abs(avg), 1e-30),
            'last_half_mean': float(a[-WINDOW_UPDATES // 2:].mean()),
            'preceding_half_mean': float(a[:WINDOW_UPDATES // 2].mean())}


def gather():
    selection, final4 = read(CAMPAIGN / 'initial-bulk-final-selection.json'), read(SERVER4 / 'final-initial-bulk.json')
    cases = []
    for label, cells in MESHES:
        run_path = CAMPAIGN / (label + '-run.json') if label != '2_6M' else Path(final4['checkpoint_proof']).parent / 'original-run.json'
        run = read(run_path)
        pair = selection['pairs'][label]['source'] if label != '2_6M' else final4['local_pair']
        end = pair['native_iteration']
        path = CAMPAIGN / (label + '-histories.json') if label in ['60k', '342k', '680k'] else HISTORY_OUT / label / 'histories.json'
        h = {k: {int(i): float(v) for i, v in rows.items()} for k, rows in read(path).items()}
        ids = np.arange(end - WINDOW_UPDATES + 1, end + 1)
        full = np.arange(run['full_hold_start'] + 1, end + 1)
        assert len(ids) == WINDOW_UPDATES and ids[0] > run['full_hold_start']
        for rows in h.values():
            assert set(range(1581, end + 1)).issubset(rows)
            assert all(math.isfinite(rows[int(i)]) for i in full)
        def vals(name, indices=ids):
            return np.asarray([h[name][int(i)] for i in indices])
        signals = {key: vals(name) for key, name in NAMES.items()}
        signals['pressure_drop'] = vals('p72s3-pressure-inlet') - vals('p72s3-pressure-outlet')
        for key in ['carryover', 'collector', 'vapor_outflow']:
            signals[key] = -signals[key]
        signals['carryover_percent_feed'] = 100 * signals['carryover'] / 116.92
        signals['collector_percent_feed'] = 100 * signals['collector'] / 116.92
        signals['vapor_net_percent_feed'] = 100 * (80.69 - signals['vapor_outflow']) / 80.69
        assert np.allclose(vals('v2-flux-phase2-liquidinlet', full), 116.92, rtol=1e-10)
        assert np.allclose(vals('v2-flux-phase1-steaminlet', full), 80.69, rtol=1e-10)
        if label == '997k':
            if end == 8080:
                proof_path = Path(next(b['checkpoint_proof'] for b in run['blocks'] if b['end'] == end))
                fields = read(proof_path)['after']['readback']['fields']
            else:
                selected = read(CAMPAIGN / 'human-selected-initial-bulk-live.json')
                assert selected['native_iteration'] == end
                fields = selected['state']['readback']['fields']
            age = selection['film']['film_elapsed_time']
        elif label == '2_6M':
            proof = read(Path(final4['checkpoint_proof']))
            fields, age = proof['after']['readback']['fields'], final4['film_end_s']
        else:
            block = next(b for b in run['blocks'] if b['end'] == end)
            fields, age = block['fields'], run['final_film']['film_elapsed_time']
        # Native file flux is boundary-only; the compute API also returns a
        # source-inclusive value. Check the correct component explicitly.
        for report in ['v2-flux-phase2-steamoutlet', 'v2-flux-phase2-liquidinlet']:
            assert math.isclose(h[report][end], fields[report + '(without-sources)'][0], rel_tol=1e-10, abs_tol=1e-10)
        for report in ['v2-total-liquid-mass', 'v2-applied-absorber', NAMES['film'], NAMES['thickness_max']]:
            assert math.isclose(h[report][end], fields[report][0], rel_tol=1e-10, abs_tol=1e-10)
        assert math.isclose(age, (end - 1580) * 1e-7, rel_tol=1e-9, abs_tol=1e-12)
        series = {key: vals(name, ids) for key, name in NAMES.items()}
        cases.append({'label': label, 'cells': cells, 'end': end, 'ids': ids,
                      'full_ids': full, 'full_start': run['full_hold_start'], 'age_s': age,
                      'comparison_window': [int(ids[0]), int(ids[-1])],
                      'series': series, 'signals': signals,
                      'stats': {key: stats(a) for key, a in signals.items()},
                      'pair': pair, 'history_path': str(path.relative_to(ROOT)),
                      'history_input_path': str(source_path(path).relative_to(ROOT)),
                      'run_receipt': str(run_path.relative_to(ROOT)),
                      'history_sha256': hashlib.sha256(source_path(path).read_bytes()).hexdigest()})
    return cases


def style(ax):
    ax.grid(alpha=.23)
    ax.spines[['top', 'right']].set_visible(False)


def mesh_axis(ax, cases):
    ax.set_xscale('log')
    ax.set_xticks([c['cells'] for c in cases], [c['label'].replace('2_6M', '2.6M') for c in cases], rotation=25)
    ax.tick_params(axis='x', labelsize=9)
    ax.minorticks_off()
    ax.set_xlim(45000, 3500000)
    ax.set_xlabel('Fluid cell count (log scale; mesh labels)')
    style(ax)


def save(fig, name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / (name + '.png'), dpi=190)
    fig.savefig(FIGURES / (name + '.pdf'))
    plt.close(fig)


def figures(cases):
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 11, 'axes.labelsize': 10})
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    for ax, (key, title, unit, scale) in zip(axes.flat, CORE):
        x = np.array([c['cells'] for c in cases])
        mean = np.array([c['stats'][key]['mean'] for c in cases]) * scale
        low = np.array([c['stats'][key]['min'] for c in cases]) * scale
        high = np.array([c['stats'][key]['max'] for c in cases]) * scale
        end = np.array([c['stats'][key]['endpoint'] for c in cases]) * scale
        ax.errorbar(x, mean, yerr=[mean - low, high - mean], fmt='D', ms=5,
                    capsize=5, color='#D88320', label=f'Final {WINDOW_UPDATES} mean and min–max')
        ax.plot(x, end, 'o', ms=6, color='#263F5E', label='Selected saved state')
        for xi, yi in zip(x, end):
            ax.annotate(f'{yi:.3f}' if key != 'bulk' else f'{yi:.2f}', (xi, yi),
                        xytext=(5, 6), textcoords='offset points', fontsize=8)
        mesh_axis(ax, cases)
        ax.set(title=title, ylabel=f'{unit}')
        ax.margins(y=.23)
    fig.suptitle('Phase 9: initial bulk-development mesh response', y=.98, fontsize=15)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc='upper center', bbox_to_anchor=(.5, .945), ncol=2, frameon=False)
    endpoint_text = ' / '.join('N' + str(c['end']) for c in cases)
    ages = [c['age_s'] * 1000 for c in cases]
    fig.text(.5, .015, endpoint_text + f'. Unequal film ages ({min(ages):.3f}–{max(ages):.3f} ms).\nBars show within-run variation, not confidence intervals. Static pressure difference is a report proxy.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.86, bottom=.14, hspace=.43, wspace=.28)
    save(fig, 'initial-bulk-mesh-response')

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    for ax, (key, title, unit, scale) in zip(axes.flat, CORE):
        for c, color in zip(cases, COLORS):
            ax.plot(c['ids'] - c['end'], c['signals'][key] * scale, color=color, lw=1.3,
                    label=f"{c['label'].replace('2_6M', '2.6M')}: N{c['ids'][0]}–{c['end']}")
        ax.set(title=title, ylabel=unit, xlabel='Native iteration relative to selected endpoint')
        style(ax)
    fig.suptitle(f'Phase 9: raw final-{WINDOW_UPDATES} histories', y=.98, fontsize=15)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc='upper center', bbox_to_anchor=(.5, .95), ncol=3, frameon=False, fontsize=9)
    fig.text(.5, .018, 'All traces are full-feed, bulk-active. Endpoint alignment does not match film age or bulk maturity.\nRaw histories end at each human-selected checkpoint.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.83, bottom=.14, hspace=.43, wspace=.28)
    save(fig, f'initial-bulk-final{WINDOW_UPDATES}-histories')

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    for c, color in zip(cases, COLORS):
        t = (c['ids'] - 1580) * 1e-4
        axes[0].plot(t, c['series']['film'] * 1000, color=color, lw=1.5,
                     label=c['label'].replace('2_6M', '2.6M'))
        axes[0].plot(t[-1], c['series']['film'][-1] * 1000, 'o', color=color, ms=4)
    axes[0].set(title=f'Film mass over final {WINDOW_UPDATES} iterations', xlabel='Recorded film age (ms)', ylabel='Film mass (g)')
    style(axes[0])
    x = np.array([c['cells'] for c in cases])
    for key, label, marker in [('thickness_mean', 'Area-weighted mean', 'o'), ('thickness_max', 'Local maximum', '^')]:
        axes[1].plot(x, [c['stats'][key]['endpoint'] * 1e6 for c in cases], marker, label=label, ms=6)
    axes[1].set(title='Selected film thickness', ylabel='Thickness (µm)', yscale='log')
    mesh_axis(axes[1], cases)
    axes[1].legend(fontsize=9, frameon=False)
    for key, label, marker in [('speed_mean', 'Area-weighted mean', 'o'), ('speed_max', 'Local maximum', '^')]:
        axes[2].plot(x, [c['stats'][key]['endpoint'] for c in cases], marker, label=label, ms=6)
    axes[2].set(title='Selected film speed', ylabel='Speed (m/s)', yscale='log')
    mesh_axis(axes[2], cases)
    axes[2].legend(fontsize=9, frameon=False)
    fig.suptitle('Phase 9: early film response under the provisional setup', y=.98, fontsize=15)
    fig.legend(*axes[0].get_legend_handles_labels(), loc='upper center', bbox_to_anchor=(.5, .92), ncol=5, frameon=False)
    fig.text(.5, .02, 'Film age is the EWF clock; it is not physical bulk time. Each trace contains the final 2000 full-feed samples.\nFilm values use the recorded wall-report scope. Local maxima depend on face resolution. Film growth continues.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.77, bottom=.20, wspace=.30)
    save(fig, 'initial-bulk-early-film-response')


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    OUT = args.output.resolve()
    cases = gather()
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {'status': 'VERIFIED_SELECTED_ENDPOINT_COMPARISON',
               'liquid_feed_kg_s': 116.92, 'vapor_feed_kg_s': 80.69,
               'window_updates': WINDOW_UPDATES, 'half_window_updates': WINDOW_UPDATES // 2, 'film_dt_s': 1e-7,
               'metric_units': UNITS,
               'analysis_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'pressure_definition': 'Area-weighted static pressure on liquidinlet+steaminlet minus steamoutlet',
               'flux_definition': 'Native file boundary-only flux, checked against API without-sources component; outflow plotted positive',
               'variation_definition': f'Raw final-{WINDOW_UPDATES} min–max; descriptive variation, not uncertainty bounds',
               'source_record_snapshots': 'source-records/ (immutable inputs used by this analysis)',
               'limits': ['Initial bulk development only', 'Unequal film ages and startup horizons',
                          'No total liquid separation efficiency or conservation qualification',
                          'No steady-state, mesh-independence, GCI, or physical-validation claim'],
               'cases': [{k: v for k, v in c.items() if k not in ['ids', 'full_ids', 'series', 'signals']} for c in cases]}
    (OUT / 'comparison.json').write_text(json.dumps(summary, indent=2) + '\n')
    with (OUT / 'comparison.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['mesh', 'cells', 'native_endpoint', 'film_age_ms', 'full_feed_updates',
                         'metric', 'unit', 'endpoint', f'last{WINDOW_UPDATES}_mean', f'last{WINDOW_UPDATES}_min', f'last{WINDOW_UPDATES}_max',
                         f'last{WINDOW_UPDATES}_net_change_percent_mean', f'last{WINDOW_UPDATES // 2}_mean', f'preceding{WINDOW_UPDATES // 2}_mean'])
        for c in cases:
            for key, s in c['stats'].items():
                writer.writerow([c['label'], c['cells'], c['end'], c['age_s'] * 1000,
                                 c['end'] - c['full_start'], key, UNITS[key], s['endpoint'], s['mean'],
                                 s['min'], s['max'], s['net_change_percent_mean'],
                                 s['last_half_mean'], s['preceding_half_mean']])
    figures(cases)
    for c in cases:
        print(c['label'], 'N' + str(c['end']), {key: round(s['endpoint'], 6) for key, s in c['stats'].items()})


if __name__ == '__main__':
    main()
