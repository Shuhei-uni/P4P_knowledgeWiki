"""Recreate the four-panel history for the selected Stage 3 Server 1 field path.

Uses saved native reports and film clocks only. Excludes numerical probes,
rejected continuation tails and unselected timestep-comparison siblings.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DEVELOP = ROOT / 'output/phase72a-stage3-film-development-server1/20261005'
STARTUP = ROOT / 'output/phase72a-stage3-early-ewf-server1/20261005'
OLD = ROOT / 'output/phase72a-lineage-N45606/20261005'
DEST = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development'
REPORTS = {
    'bulk_liquid_kg': 'v2-total-liquid-mass',
    'phase2_steamoutlet_signed_kg_s': 'v2-flux-phase2-steamoutlet',
    'film_kg': 'p72a-e2.7-ewf-film-mass-total',
    'accretion_kg_s': 'p72a-e2.7-ewf-secondary-phase-mass-total',
    'cumulative_drainage_kg': 'p72a-e2.7-ewf-outflow-mass-total',
}


def native_report(path):
    rows = {}
    for line in path.read_text().splitlines():
        cells = line.split()
        if len(cells) == 2 and cells[0].isdigit():
            n, value = int(cells[0]), float(cells[1])
            if n in rows and rows[n] != value:
                raise ValueError(f'Conflicting duplicate in {path}: N{n}')
            rows[n] = value
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--end', type=int, help='Pin the last completed checkpoint')
    args = parser.parse_args()
    m = json.loads((DEVELOP/'run-manifest.json').read_text())
    early = json.loads((STARTUP/'run-manifest.json').read_text())
    end = args.end or m['verified_native_end']
    selected_end = next(b for b in reversed(m['blocks']) if b['native_end'] == end
                        and Path(b.get('output', '')).name.startswith('adaptive-'))
    assert selected_end['within_recovery_bounds'], 'Requested endpoint is outside recovery bounds'
    assert m['parent_pair']['case_sha256'] == early['final_pair']['case_sha256']
    assert m['parent_pair']['data_sha256'] == early['final_pair']['data_sha256']
    sources, joins, segments = [], [], []
    rows = {}

    def source(path, role):
        sources.append({'path': str(path), 'role': role,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

    for path in [DEVELOP/'run-manifest.json', STARTUP/'run-manifest.json']:
        source(path, 'checkpoint identities and selected-parent evidence')
    bulk_path = OLD/'recovered-r0-reports/P71A-R0-SMOOTH-CONTROL-v2-total-liquid-mass.out'
    flux_path = OLD/'recovered-r0-reports/P71A-R0-SMOOTH-CONTROL-v2-flux-phase2-steamoutlet.out'
    bulk, flux = native_report(bulk_path), native_report(flux_path)
    source(bulk_path, 'retained native low-feed bulk inventory')
    source(flux_path, 'retained native low-feed signed outlet flux')
    for n in range(1, 1581):
        rows[n] = {'bulk_liquid_kg': bulk[n], 'phase2_steamoutlet_signed_kg_s': flux[n],
                   'film_kg': 0., 'accretion_kg_s': 0., 'cumulative_drainage_kg': 0.,
                   'film_time_s': 0., 'drainage_kg_s': 0.,
                   'source_segment': 'retained R0 low-feed parent; EWF off'}
    segments.append({'label': 'retained R0 low-feed parent', 'native_start': 1, 'native_end': 1580,
                     'film_zero_basis': 'EWF off before dry-film activation at A', 'rows': 1580})

    def add_segment(label, folder, history_path, low, high, blocks=None, startup=False):
        data = json.loads(history_path.read_text())
        source(history_path, 'selected native-report JSON')
        reports = {}
        for key, name in REPORTS.items():
            record = data[name]
            reports[key] = dict(zip(record['iterations'], record['values']))
            raw_path = folder / (f'final-{name}.out' if startup else f'{name}.out')
            native = native_report(raw_path)
            source(raw_path, 'native report independently checked against JSON')
            assert all(n in native and n in reports[key] for n in range(low, high+1)), (label, key)
            assert np.allclose([native[n] for n in range(low, high+1)],
                               [reports[key][n] for n in range(low, high+1)], rtol=1e-12, atol=1e-12)
            assert np.isfinite([reports[key][n] for n in range(low, high+1)]).all()
        assert low == max(rows), 'Selected lineage has a gap or an unhandled overlap'
        join = {'native_iteration': low, 'from': rows[low]['source_segment'], 'to': label, 'fields': {}}
        for key in REPORTS:
            old, new = rows[low][key], reports[key][low]
            # Source rates may be freshly evaluated after controls preparation;
            # inventory, cumulative outflow and boundary flux must match.
            if key != 'accretion_kg_s':
                assert np.isclose(old, new, rtol=1e-8, atol=1e-8), (label, low, key, old, new)
            join['fields'][key] = {'parent': old, 'child': new}
        joins.append(join)
        clocks = {}
        exact_steps = {}
        if startup:
            path = folder/'film-clocks.json'
            recorded = json.loads(path.read_text())
            source(path, 'verified fixed 1 us startup film clocks')
            for n in range(low+1, high+1):
                assert np.isclose(recorded[str(n)][1], 1e-6, rtol=1e-12)
                clocks[n] = (n-1580)*1e-6
                exact_steps[n] = 1e-6
        else:
            for b in blocks:
                begin, finish = b['native_start'], b['native_end']
                path = folder/f'clocks-N{begin}-N{finish}.json'
                recorded = json.loads(path.read_text())
                source(path, 'completed native film-clock batch')
                assert set(map(int, recorded)) == set(range(begin+1, finish+1))
                t0 = b['film_time_s']-b['added_film_time_s']
                dt = b['final_accepted_step_s']
                constant = (b['printed_step_min_s'] == b['printed_step_max_s']
                            and np.isclose(dt*b['updates'], b['added_film_time_s'], rtol=1e-10, atol=1e-12))
                for n in range(begin+1, finish+1):
                    clocks[n] = t0+(n-begin)*dt if constant else recorded[str(n)][0]
                    if constant:
                        exact_steps[n] = dt
                clocks[finish] = b['film_time_s']
        assert set(clocks) == set(range(low+1, high+1)), 'Film clock coverage differs from report interval'
        for n in range(low+1, high+1):
            current = {key: reports[key][n] for key in REPORTS}
            dt = exact_steps.get(n, clocks[n]-rows[n-1]['film_time_s'])
            assert dt > 0 and np.isfinite(dt)
            current.update(film_time_s=clocks[n], actual_film_increment_s=dt,
                           drainage_kg_s=(current['cumulative_drainage_kg']-rows[n-1]['cumulative_drainage_kg'])/dt,
                           source_segment=label)
            rows[n] = current
        segments.append({'label': label, 'native_start': low, 'native_end': high, 'rows_added': high-low,
                         'history': str(history_path), 'native_reports_against_JSON': 'PASS_ALL_5',
                         'exact_constant_step_rows': len(exact_steps),
                         'variable_step_basis': 'Difference of printed native clocks, anchored by saved batch endpoints'})

    add_segment('early Coupled/EWF startup', STARTUP, STARTUP/'final-histories.json', 1580, 5080, startup=True)
    arm50 = next(a for a in m['sensitivity_arms'].values() if a['pair']['native_iteration'] == 5090)
    arm20 = m['mid_film_arms'][m['mid_film_selected_arm']]
    ordered = [
        ('matched-time-50us-8', 5080, 5090, [arm50['metrics']]),
        ('adaptive-development', 5090, 7190, None),
        ('adaptive-recovery-from-N7190', 7190, 13390, None),
        ('mid-film-candidate20-N13390', 13390, 13515, [arm20['metrics']]),
        ('adaptive-mid-film-N13390', 13515, 22615, None),
        ('adaptive-recovery-from-N22615', 22615, end, None),
    ]
    for name, low, high, blocks in ordered:
        if end <= low:
            break
        high = min(high, end)
        folder = DEVELOP/name
        if blocks is None:
            blocks = [b for b in m['blocks'] if Path(b.get('output', '')).name == name
                      and low <= b['native_start'] and b['native_end'] <= high]
        assert blocks[0]['native_start'] == low and blocks[-1]['native_end'] == high
        add_segment(name, folder, folder/'report-histories.json', low, high, blocks=blocks)
    assert sorted(rows) == list(range(1, end+1)), 'Selected history has missing native coordinates'
    endpoint = json.loads((Path(selected_end['output'])/f'endpoint-N{end}.json').read_text())
    source(Path(selected_end['output'])/f'endpoint-N{end}.json', 'selected saved/reopened endpoint')
    assert np.isclose(rows[end]['film_time_s'], endpoint['film']['film_elapsed_time'], rtol=0, atol=1e-12)
    assert np.isclose(rows[end]['film_kg'], endpoint['state']['readback']['fields']['p72a-e2.7-ewf-film-mass-total'][0])
    events = [(1580, 'A', 'Coupled/EWF + R3/contact', 'Dry film; 500-update quarter-feed hold'),
              (2080, 'B', 'inlet ramp', '2000-update ramp from quarter to full feed'),
              (4080, 'C', 'full feed', '1000-update target-feed hold'),
              (5080, 'D', 'frozen bulk / faster film', 'Alternative implicit; selected 50 us x10 arm, then adaptive from N5090'),
              (7190, 'E', 'lower-target recovery', 'Fixed 5 us x100, then adaptive target 0.2'),
              (13390, 'F', '20 us qualification', 'Selected 20 us x125 arm; adaptive target 0.5 from N13515'),
              (22615, 'G', 'smaller-step recovery', 'Fixed 5 us x100; adaptive target 0.2 from N22715')]
    ix = np.array(sorted(rows))
    get = lambda key: np.array([rows[int(n)][key] for n in ix])
    fig, axes = plt.subplots(4, 1, figsize=(14, 13), constrained_layout=True)
    axes[0].plot(ix, get('bulk_liquid_kg'), color='#1f77b4', lw=.85, label='Bulk phase-2 inventory')
    axes[0].plot(ix, get('bulk_liquid_kg')+get('film_kg'), color='#A34D91', lw=.9, label='Bulk + EWF inventory')
    axes[0].set_ylabel('Liquid inventory (kg)')
    axes[0].legend(loc='lower right', fontsize=9)
    axes[1].plot(ix, get('phase2_steamoutlet_signed_kg_s'), color='#1f77b4', lw=.85)
    axes[1].set_ylabel('Phase-2 steamoutlet\nflux (kg/s, signed)')
    axes[2].plot(ix, get('film_kg'), color='#1f77b4', lw=.85)
    axes[2].set_ylabel('EWF film inventory (kg)')
    axes[3].plot(ix, get('accretion_kg_s'), color='#1f77b4', lw=.8, label='Native accretion rate')
    axes[3].plot(ix, get('drainage_kg_s'), color='#B87520', lw=.65,
                 label='Drainage: cumulative outflow difference / film-time increment')
    axes[3].set_ylabel('Film mass rate (kg/s)')
    axes[3].legend(loc='lower right', fontsize=9)
    for ax in axes:
        ax.set_xlim(0, end+150)
        ax.grid(alpha=.2)
        ax.set_xlabel('Native iteration (bulk equations frozen after D; not elapsed physical time)')
        for n, tag, _, _ in events:
            if n <= end:
                ax.axvline(n, color='#666666', ls='--', lw=.7, alpha=.65)
                ax.text(n+65, .98, tag, transform=ax.get_xaxis_transform(), va='top', fontsize=9,
                        bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .85})
    for n in [7190, 13390, 22615]:
        if n <= end:
            axes[0].plot(n, rows[n]['bulk_liquid_kg'], 'D', ms=4, color='#1f77b4')
            axes[0].plot(n, rows[n]['bulk_liquid_kg']+rows[n]['film_kg'], 'D', ms=4, color='#A34D91')
            for ax, key in zip(axes[1:], ['phase2_steamoutlet_signed_kg_s', 'film_kg', 'accretion_kg_s']):
                ax.plot(n, rows[n][key], 'D', ms=4, color='#1f77b4')
    fig.suptitle(f'History of the selected Stage 3 field branch leading to N{end}\n'
                 'A: Coupled/EWF + R3/contact   B: inlet ramp   C: full feed   D: frozen bulk / faster film\n'
                 'E: lower-target recovery   F: 20 µs qualification   G: smaller-step recovery', fontsize=12)
    figures = DEST/'figures'
    figures.mkdir(parents=True, exist_ok=True)
    slug = f'selected-case-history-N{end}'
    png, pdf = figures/f'{slug}.png', figures/f'{slug}.pdf'
    fig.savefig(png, dpi=180)
    fig.savefig(pdf)
    plt.close(fig)
    output = DEVELOP/'selected-history'
    output.mkdir(exist_ok=True)
    csv_path = output/f'{slug}.csv'
    keys = ['native_iteration', *REPORTS, 'bulk_plus_ewf_kg', 'film_time_s', 'actual_film_increment_s', 'drainage_kg_s', 'source_segment']
    with csv_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        for n, row in rows.items():
            writer.writerow({'native_iteration': n, **row, 'bulk_plus_ewf_kg': row['bulk_liquid_kg']+row['film_kg'],
                             'actual_film_increment_s': row.get('actual_film_increment_s', 0.)})
    record = {'status': 'COMPLETE_HISTORY_VISUAL_QA_PENDING', 'native_range': [1, end], 'rows': len(rows),
              'missing_native_coordinates': [], 'source_pair': selected_end['pair'],
              'endpoint_film_time_s': rows[end]['film_time_s'], 'endpoint': rows[end],
              'endpoint_combined_liquid_kg': rows[end]['bulk_liquid_kg']+rows[end]['film_kg'],
              'segments': segments, 'joins': joins, 'events': [{'iteration': n, 'tag': t, 'label': l, 'detail': d} for n,t,l,d in events],
              'excluded': ['original/half-step/sequential/frozen diagnostics', 'unselected timestep comparison siblings',
                           'rejected adaptive N7190-N8190', 'rejected adaptive N22615-N23615'],
              'drainage_method': 'Per-update cumulative outflow difference / elapsed film-time increment. Constant-step intervals use verified exact saved steps; variable intervals retain native printed-clock resolution.',
              'flux_sign': 'Native signed steamoutlet flux; negative is outward flow',
              'claim_limit': 'Selected saved field path; frozen bulk after N5080. Film development is not steady-film or whole-model qualification.',
              'sources': sources, 'figures': [str(png), str(pdf)], 'csv': str(csv_path),
              'figure_sha256': hashlib.sha256(png.read_bytes()).hexdigest()}
    (output/f'{slug}-manifest.json').write_text(json.dumps(record, indent=2, allow_nan=False)+'\n')
    print('SELECTED_HISTORY_COMPLETE', end, 'rows', len(rows), 'endpoint film time', rows[end]['film_time_s'])


if __name__ == '__main__':
    main()
