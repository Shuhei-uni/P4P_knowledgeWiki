"""Offline, partial-history diagnostic for Andy's observed post-N2700 spikes.

Snapshot inputs before reading; this never connects to Fluent or changes a run.
The observation-selected windows are descriptive, not convergence criteria.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import re
import shutil

import numpy as np
from analyze_phase07b_screen import (
    parse_history, parse_residuals, parse_flux, coverage, derive, fingerprint, plt,
)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('run', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--reuse-snapshot', action='store_true')
    args = ap.parse_args()
    out = args.output
    raw = out / 'raw'
    if not args.reuse_snapshot:
        out.mkdir(parents=True, exist_ok=False)
        raw.mkdir()
        for name in ['manifest.json', 'history-04500.out', 'solve.trn', 'collector-flux.jsonl']:
            shutil.copyfile(args.run / name, raw / name)
    h, ha = parse_history(raw / 'history-04500.out')
    r, ra = parse_residuals(raw / 'solve.trn')
    f, fa = parse_flux(raw / 'collector-flux.jsonl')
    end = 4500
    for data, audit in [(h, ha), (r, ra), (f, fa)]:
        coverage(audit, data, end)
        assert audit['complete_to_expected_end'], audit
    assert set(r) == {'iteration', 'continuity', 'x-velocity', 'y-velocity',
                     'z-velocity', 'k', 'epsilon', 'vf-phase-2'}
    r = {k: v[r['iteration'] <= end] for k, v in r.items()}
    f = {k: v[f['iteration'] <= end] for k, v in f.items()}
    d, _ = derive(h)
    n = h['iteration']
    assert np.array_equal(n, r['iteration']) and np.array_equal(n, f['iteration'])

    # Warning lines occur before the associated residual row. Missing warning
    # lines remain NaN (not an inferred zero). Ignore checkpoint echo duplicates.
    warning_rows = {}
    pending = {}
    for line in (raw / 'solve.trn').read_text().splitlines():
        match = re.search(r'turbulent viscosity limited .* in\s+(\d+) cells', line)
        if match:
            pending['limited_cells'] = int(match[1])
        match = re.search(r'Reversed flow on\s+(\d+) faces of pressure-outlet', line)
        if match:
            pending['reversed_faces'] = int(match[1])
        words = line.split()
        if len(words) >= 10 and words[0].isdigit() and ':' in words[8]:
            i = int(words[0])
            if 1 <= i <= end and i not in warning_rows:
                warning_rows[i] = dict(pending)
            pending.clear()
    warnings = {key: np.array([warning_rows.get(int(i), {}).get(key, np.nan) for i in n])
                for key in ['limited_cells', 'reversed_faces']}

    def stats(v):
        v = v[np.isfinite(v)]
        return {'recorded_samples': len(v), 'mean': float(v.mean()),
                'minimum': float(v.min()), 'maximum': float(v.max())} if len(v) else {}

    windows = {}
    for a, b in [(2001, 2700), (2701, 3400), (3401, 4100), (4101, 4500)]:
        q = (n >= a) & (n <= b)
        residual_stats = {}
        for key, v in r.items():
            if key == 'iteration':
                continue
            changes = np.abs(np.diff(np.log10(v[q])))
            residual_stats[key] = dict(stats(v[q]),
                p95_absolute_adjacent_log10_change=float(np.percentile(changes, 95)),
                adjacent_factor_above_1p5_count=int((changes > np.log10(1.5)).sum()))
        keys = ['whole_water_mass', 'collector_water_mass', 'native_applied_removal',
                'maximum_mixture_speed', 'liquid_closure_percent_feed']
        windows[f'{a}-{b}'] = {'residuals': residual_stats,
            'metrics': {key: stats(d[key][q]) for key in keys},
            'warnings': {key: stats(v[q]) for key, v in warnings.items()}}

    # Same-iteration and neighbouring co-occurrence are descriptive only.
    events = []
    for i in [2821, 3760, 3786, 4124, 4140, 4328]:
        q = (n >= i - 2) & (n <= i + 2)
        events.append({'iteration': i,
            'epsilon_at_iteration': float(r['epsilon'][i - 1]),
            'maximum_speed_at_iteration_m_s': float(d['maximum_mixture_speed'][i - 1]),
            'epsilon_peak_within_2_iterations': float(r['epsilon'][q].max()),
            'speed_peak_within_2_iterations_m_s': float(d['maximum_mixture_speed'][q].max())})
    lag = d['native_applied_removal'][1:] - d['current_expression_removal'][:-1]
    manifest = json.loads((raw / 'manifest.json').read_text())
    summary = {'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'run': str(args.run), 'status': 'PARTIAL_DIAGNOSTIC_N1_TO_N4500',
        'human_observation': 'Residuals appear more spiky after roughly N2700.',
        'window_selection': 'Descriptive windows around the human observation; no fitted change point.',
        'inputs': [fingerprint(x) for x in sorted(raw.iterdir())],
        'audits': {'scalar': ha, 'residuals': ra, 'flux': fa}, 'windows': windows,
        'selected_events': events,
        'source_lag_maximum_absolute_error_kg_s': float(np.abs(lag).max()),
        'solver_block_steps': [x['name'] for x in manifest['steps'] if x['name'].startswith('iterate_')],
        'limitations': ['Global extrema do not locate the affected cells.',
            'No controlled perturbation isolates pressure, turbulence, phase transport or source coupling.',
            'Steady iteration inventory slope is not a physical storage rate.',
            'Warnings are assigned to the following residual row; absent warnings are not zero.',
            'Final endpoint and predeclared late-window judgement remain pending.']}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')

    plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': .18})
    view = n >= 1800
    fig, axes = plt.subplots(4, 2, figsize=(13, 11), sharex=True, layout='constrained')
    for ax, key in zip(axes.flat, [k for k in r if k != 'iteration']):
        ax.semilogy(n[view], r[key][view], lw=.85)
        ax.set_title(key, loc='left')
        ax.set_ylabel('Native residual')
    ax = axes.flat[-1]
    ax.plot(n, d['maximum_mixture_speed'], color='tab:red', lw=.85)
    ax.set_title('Maximum mixture speed: brief excursions', loc='left')
    ax.set_ylabel('m/s')
    for ax in axes.flat:
        ax.axvline(2700, color='black', ls='--', lw=.9)
        ax.set_xlim(1800, 4500)
    for ax in axes[-1]:
        ax.set_xlabel('Steady solver iteration')
    fig.suptitle('S40-T020: raw residuals and speed | partial evidence through N4500\nDashed line: Andy’s approximate N2700 observation, not an identified change point')
    fig.savefig(out / 'residuals-and-speed.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(4, 1, figsize=(13, 12), sharex=True, layout='constrained')
    ax = axes[0]
    ax.plot(n, d['native_applied_removal'], label='Native applied removal', lw=1)
    ax.plot(n, f['delivery_kg_s'], label='Gross collector delivery', lw=.8, alpha=.8)
    ax.plot(n, f['escape_kg_s'], label='Gross collector escape', lw=.8)
    ax.plot(n, d['liquid_measured_feed'], '--', color='black', label='Measured liquid feed', lw=.9)
    ax.set_ylabel('kg/s'); ax.legend(ncol=2, loc='upper left')
    ax = axes[1]
    ax.plot(n, d['whole_water_mass'], label='Whole-vessel liquid', color='tab:blue')
    ax.set_ylabel('Whole-vessel liquid (kg)', color='tab:blue')
    other = ax.twinx()
    other.plot(n, d['collector_water_mass'], color='tab:orange', lw=.9)
    other.set_ylabel('Collector liquid (kg)', color='tab:orange'); other.grid(False)
    ax = axes[2]
    ax.plot(n, warnings['limited_cells'], color='tab:purple', lw=.8)
    ax.set_ylabel('Viscosity-limited cells', color='tab:purple')
    other = ax.twinx()
    other.plot(n, warnings['reversed_faces'], color='tab:gray', lw=.7, alpha=.8)
    other.set_ylabel('Outlet reversed-flow faces', color='tab:gray'); other.grid(False)
    ax = axes[3]
    for phase in ['liquid', 'vapor', 'mixture']:
        ax.plot(n, d[phase + '_closure_percent_feed'], label=phase, lw=.9)
    ax.axhline(0, color='black', lw=.7)
    ax.set_ylabel('Applied-source closure\n(% of phase / mixture feed)')
    ax.legend(ncol=3)
    for ax in axes:
        ax.axvline(2700, color='black', ls='--', lw=.9)
        ax.set_xlim(1800, 4500)
    axes[-1].set_xlabel('Steady solver iteration (not physical time)')
    fig.suptitle('S40-T020: coupled histories around the residual change\nPartial evidence through N4500; shared timing does not establish causation')
    fig.savefig(out / 'coupled-histories.png', dpi=180)
    plt.close(fig)
    print(json.dumps({'output': str(out), 'windows': windows, 'events': events}))


if __name__ == '__main__':
    main()
