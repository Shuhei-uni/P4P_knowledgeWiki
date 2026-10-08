"""Plot the supplied-parent bulk response from complete native histories."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import re
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/setup')]
from run_phase72a_adaptive_film import FILM, history
OUT = ROOT / 'output/phase72a-stage4-replacement/20261008'
DOC = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/replacement-parent'
COLORS = {'continuity': '#46D2BA', 'x-velocity': '#A199D9', 'y-velocity': '#FA1900',
          'z-velocity': '#2C8ED2', 'k': '#FC8500', 'epsilon': '#8BDD00', 'vf-phase-2': '#FB9DCD'}


def residuals(text):
    names, rows = [], {}
    for line in text.splitlines():
        tokens = line.split()
        if tokens and tokens[0] == 'iter' and 'continuity' in tokens:
            names = tokens[1:tokens.index('time/iter')] if 'time/iter' in tokens else tokens[1:]
        elif names and tokens and tokens[0].isdigit() and len(tokens) > len(names):
            try:
                v = list(map(float, tokens[1:len(names) + 1]))
            except ValueError:
                continue
            if all(math.isfinite(a) and a >= 0 for a in v): rows[int(tokens[0])] = dict(zip(names, v))
    return names, rows


def describe(series, x, window=200):
    tail = series[-window:]
    prev = series[-2 * window:-window]
    return {'start': float(series[0]), 'end': float(series[-1]),
            'total_change_percent': float(100 * (series[-1] - series[0]) / max(abs(series[0]), 1e-30)),
            'late_window': window, 'late_min': float(tail.min()), 'late_max': float(tail.max()),
            'late_mean': float(tail.mean()), 'previous_mean': float(prev.mean()) if len(prev) else None,
            'late_change_percent': float(100 * (tail[-1] - tail[0]) / max(abs(tail[0]), 1e-30)),
            'late_slope_per_iteration': float(np.polyfit(x[-window:], tail, 1)[0]),
            'window_mean_change_percent': float(100 * (tail.mean() - prev.mean()) / max(abs(prev.mean()), 1e-30)) if len(prev) else None}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--block', required=True)
    p.add_argument('--window', type=int, default=200)
    p.add_argument('--document-subdir', default='')
    a = p.parse_args()
    block = OUT / a.block
    m = json.loads((block / 'run-manifest.json').read_text())
    assert m['status'] == 'CHECKPOINT_VERIFIED'
    assert 1 < a.window <= m['count'] // 2
    x = np.arange(m['start'], m['target'] + 1)
    text = (block / 'native-run.trn').read_text()
    h = {n: history((block / (n + '.out')).read_text()) for n in m['report_paths']}
    # Fluent's computed mass-flux alias includes cell sources; its native report
    # file records the boundary component. Use the same definition at N8000.
    def initial_value(name):
        boundary = name + '(without-sources)'
        return m['initial_reports'].get(boundary, m['initial_reports'][name])[0]

    y = {n: np.array([initial_value(n)] + [h[n][int(i)] for i in x[1:]]) for n in h}
    assert all(np.all(np.isfinite(v)) for v in y.values()), 'Non-finite native report history'
    for n in ['v2-total-liquid-mass', 'v2-lower-liquid-mass', 'p72d-total-mass', 'p72d-lower-mass']:
        assert np.all(y[n] >= -1e-12), 'Negative liquid inventory: ' + n
    for n in ['v2-flux-phase2-steamoutlet', 'v2-flux-phase1-steamoutlet']:
        boundary = n + '(without-sources)'
        expected = m['final_reports'].get(boundary, m['final_reports'][n])[0]
        assert math.isclose(y[n][-1], expected, rel_tol=1e-7, abs_tol=1e-9), 'Native outlet history definition differs from boundary readback'
    names, res = residuals(text)
    res = {i: v for i, v in res.items() if m['start'] < i <= m['target']}
    assert len(res) == m['count'], 'Missing native bulk residual rows'
    clocks = [tuple(map(float, v.groups())) for v in FILM.finditer(text)]
    assert len(clocks) == m['count'], 'Unexpected accepted film updates per bulk iteration'
    t = np.array([m['before']['film']['film_elapsed_time']] + [v[0] for v in clocks])
    dt = np.diff(t)
    assert np.all(dt > 0)
    assert np.allclose(dt, m['step_s'], rtol=1e-7, atol=1e-12), 'Accepted film steps differ from the fixed step'
    stats = {n: describe(v, x, a.window) for n, v in y.items()}
    keys = ['p72d-total-mass', 'p72d-total-outflow', 'p72d-total-stripped', 'p72d-total-separated']
    departure = sum(y[n][-1] - y[n][0] for n in keys)
    sources = {n: float(np.sum(y[n][1:] * dt)) for n in ['p72d-total-secondary', 'p72d-total-dpm']}
    removed = float(np.sum(y['p72d-drain-rate'][1:] * dt))
    ledger = departure + removed - sum(sources.values())
    inner = re.findall(r'sub-iteration:\s*(\d+) residual - h:\s*([^;]+); u:\s*([^;]+); v:\s*(\S+)', text)
    summary = {'block': str(block.relative_to(ROOT.parent)), 'native_start': m['start'], 'native_end': m['target'],
               'bulk_updates': m['count'], 'added_film_time_s': float(t[-1] - t[0]),
               'series': stats, 'residuals': {n: describe(np.array([res[int(i)][n] for i in x[1:]]), x[1:], a.window) for n in names},
               'film_direct_removal_kg': removed, 'integrated_film_sources_kg': sources,
               'original_film_ledger_residual_kg': ledger,
               'original_film_ledger_error_percent': 100 * abs(ledger) / max(sum(abs(v) for v in sources.values()), 1e-30),
               'peak_courant': max(v[2] for v in clocks), 'peak_thickness_m': float(y['p72d-total-thickness'].max()),
               'peak_film_speed_m_s': float(y['p72r-film-speed-max'].max()), 'achieved_inner_residual_rows': len(inner),
               'dpm_tracking_events': len(re.findall(r'(?im)^\s*DPM Iteration', text)),
               'dpm_source_update_messages': len(re.findall(r'(?i)updating DPM sources', text)),
               'bulk_absorber_max_expression_discrepancy_kg_s': float(np.max(abs(-y['v2-applied-absorber'] - y['p72-contact-removal']))),
               'endpoint_outlet_api_components': {k: v for k, v in m['final_reports'].items() if 'steamoutlet' in k},
               'claim_limit': 'Bulk response and film development; DPM event mass and whole-system closure not qualified'}
    figdir = DOC / a.document_subdir / 'figures'
    figdir.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for n in names:
        ax.semilogy(x[1:], [res[int(i)][n] for i in x[1:]], color=COLORS.get(n), label=n, lw=.8)
    ax.axvspan(m['target'] - 2 * a.window + 1, m['target'] - a.window, color='#999999', alpha=.12)
    ax.axvspan(m['target'] - a.window + 1, m['target'], color='#2C8ED2', alpha=.08)
    ax.set(xlabel='Native iteration', ylabel='Scaled residual', title=f'Bulk-active residuals: N{m["start"]}–N{m["target"]}')
    ax.grid(alpha=.2); ax.legend(ncol=3, fontsize=8)
    fig.tight_layout(); fig.savefig(figdir / (a.block + '-residuals.png'), dpi=160); plt.close(fig)
    fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
    axes[0].plot(x, y['v2-total-liquid-mass'], lw=1, color='#2C8ED2')
    axes[0].set(ylabel='Bulk liquid (kg)', title='Bulk and film inventories')
    for n, label in [('p72d-total-mass', 'Total film'), ('p72d-upper-mass', 'Main wall'), ('p72d-lower-mass', 'Lower collector')]:
        axes[1].plot(x, y[n], lw=1, label=label)
    axes[1].set(ylabel='Film liquid (kg)'); axes[1].legend(fontsize=8)
    axes[2].plot(x, -y['v2-flux-phase2-steamoutlet'], lw=1, color='#FA1900')
    axes[2].set(ylabel='Outlet liquid (kg/s)', xlabel='Native iteration')
    axes[2].set_title('Boundary-only steamoutlet liquid: positive outward', fontsize=10, loc='left')
    for ax in axes: ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(figdir / (a.block + '-inventories.png'), dpi=160); plt.close(fig)
    fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
    axes[0].plot(x, y['p72-contact-removal'], label='Bulk expression', lw=1)
    axes[0].plot(x, -y['v2-applied-absorber'], label='Applied bulk UDF', lw=.8, ls='--')
    axes[0].set(ylabel='Bulk removal (kg/s)', title='Absorber and film transfer histories'); axes[0].legend(fontsize=8)
    for n, label in [('p72d-total-secondary', 'Phase Accretion (signed)'), ('p72d-total-dpm', 'Reported DPM source'), ('p72d-drain-rate', 'Direct film drain')]:
        axes[1].plot(x, y[n], label=label, lw=.8)
    axes[1].set(ylabel='Film rates (kg/s)'); axes[1].legend(fontsize=8)
    axes[2].plot(x, y['p72d-total-courant'], lw=1)
    axes[2].set(ylabel='Film Courant', xlabel='Native iteration')
    for ax in axes: ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(figdir / (a.block + '-absorbers.png'), dpi=160); plt.close(fig)
    with (block / 'histories.csv').open('w') as stream:
        writer = csv.writer(stream); writer.writerow(['native_iteration', 'film_time_s'] + list(y))
        writer.writerows([int(i), float(t[j])] + [float(v[j]) for v in y.values()] for j, i in enumerate(x))
    sources_files = list(block.glob('*.out')) + [block / 'native-run.trn', block / 'run-manifest.json']
    summary['source_hashes'] = {str(p.relative_to(ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources_files}
    (block / 'analysis-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: summary[k] for k in ['bulk_updates', 'added_film_time_s', 'peak_courant', 'original_film_ledger_error_percent']}, indent=2))
    for n in ['v2-total-liquid-mass', 'p72d-total-mass', 'v2-flux-phase2-steamoutlet']:
        print(n, stats[n])


if __name__ == '__main__': main()
