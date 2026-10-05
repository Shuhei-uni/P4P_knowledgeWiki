"""Plot only verified Server 1 film-development blocks and preserve branch identity."""
from pathlib import Path
import json
import re
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/phase72a-stage3-film-development-server1/20261005'
DEST = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development'


def analyze():
    m = json.loads((OUT / 'run-manifest.json').read_text())
    blocks = m['blocks']
    if not blocks:
        return
    branches = {}
    for b in blocks:
        branches.setdefault(Path(b.get('output', str(OUT))), []).append(b)
    plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': .25})
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, constrained_layout=True)
    fig2, health = plt.subplots(2, 1, figsize=(10, 7), sharex=True, constrained_layout=True)
    active = [p for p in branches if p.name.startswith('adaptive-') or p.name == 'full-bulk-development']
    plotted = active or [p for p in branches if p.name.startswith('matched-time-conservative') or p == list(branches)[-1]]
    for folder, bb in branches.items():
        if folder not in plotted:
            continue
        # The rejected N8190 history remains in its native branch. The figure
        # follows the selected field lineage through the N7190 restart.
        cutoff = None
        if folder.name == 'adaptive-development' and m.get('adaptive_recoveries'):
            cutoff = m['adaptive_recoveries'][0]['restart']['pair']['native_iteration']
            bb = [b for b in bb if b['native_end'] <= cutoff]
        if not bb:
            continue
        label = folder.name if folder != OUT else 'Coupled film, 1 µs, 30 subiterations'
        clocks, inner = {}, {}
        for b in bb:
            tag = f"N{b['native_start']}-N{b['native_end']}"
            clocks.update({int(k): v for k, v in json.loads((folder / f'clocks-{tag}.json').read_text()).items()})
            inner.update({int(k): v for k, v in json.loads((folder / f'film-inner-{tag}.json').read_text()).items()})
        histories = json.loads((folder / 'report-histories.json').read_text())
        def hist(name):
            h = histories[name]
            return dict(zip(h['iterations'], h['values']))
        mass = hist('p72a-e2.7-ewf-film-mass-total')
        ix = sorted(clocks)
        t = np.array([clocks[i][0] for i in ix]) * 1000
        axes[0].plot(t, [mass[i] for i in ix], label=label)
        centers = [(b['film_time_s'] - .5 * b['added_film_time_s']) * 1000 for b in bb]
        for metric, style in [('accretion_kg_s', 'o-'), ('drainage_kg_s', 's--'), ('storage_kg_s', 'x:')]:
            axes[1].plot(centers, [b[metric] for b in bb], style, label=f'{label}: {metric.split("_")[0]}')
        health[0].plot(t, [clocks[i][1] * 1e6 for i in ix], label=label)
        health[1].plot(t, [clocks[i][2] for i in ix], label=label)
    axes[0].set(ylabel='Film inventory (kg)', title='Film development on the selected branch')
    axes[1].set(ylabel='Film transfer rate (kg/s)', xlabel='Film time since dry start at A (ms)', title='Block averages using actual accepted film-time increments')
    health[0].set(ylabel='Printed accepted film step (µs)', title='Step and Courant evidence; alternative inner residuals unavailable')
    health[1].set(ylabel='Maximum film Courant', xlabel='Film time since dry start at A (ms)')
    if active:
        health[1].axhline(m['controlled_delta']['courant-number'], color='k', ls='--', lw=1, label='Current adaptive target')
        health[1].axhline(1, color='r', ls=':', lw=1, label='Recovery limit')
    for ax in [*axes, *health]:
        ax.legend(fontsize=7, loc='best')
    DEST.mkdir(exist_ok=True, parents=True)
    fig.savefig(DEST / 'film-development.png', dpi=160)
    fig2.savefig(DEST / 'film-solver-health.png', dpi=160)
    plt.close('all')
    lines = ['# Stage 3 — Film development results', '',
             '| Current state | Evidence |', '| --- | --- |',
             f"| Goal | Fastest numerically adequate film development; stationary film remains {'screened, confirmation pending' if m.get('steady_film') else 'unreached'} |",
             f"| Server / parent | Server 1; preserved early-start N5080; 3.5 ms, 0.164512 kg |",
             f"| Controller | `{m['status']}`; verified N{m['verified_native_end']}; active target {m.get('active_target')} |",
             f"| Current restart / film | N{m['latest_pair']['native_iteration']}; {m['latest_metrics']['film_time_s']*1000:.6f} ms; {m['latest_metrics']['film_mass_kg']:.6f} kg |",
             '| Branch limit | Initial probes share N5080; adaptive recovery restarts passing N7190. Exclude rejected N8190 from selected field lineage; do not add sibling film times |',
             '| Fixed science | Full feed, R3, corrected absorber, bulk Coupled, film equations/forces/sources/boundaries and flow feedback |',
             f"| Bulk advancement | {'Original bulk equations restored; full-model film checks underway' if m.get('bulk_equations_restored') else 'Temporarily frozen during matched-time checks and relaxation; restoration required before goal closure'} |",
             '', '| Branch / native interval | Film step (µs) | Added time (ms) | Final film (kg) | Inner pass (%) | Final residual >1 (updates) | Ledger error (%) | Film ms / wall min |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for b in blocks:
        folder = Path(b.get('output', str(OUT)))
        name = folder.name if folder != OUT else 'Initial 30-subiteration probe'
        passed = f"{b['inner_pass_percent']:.2f}" if b['inner_pass_percent'] is not None else 'Unavailable'
        cost = f"{b['film_ms_per_wall_minute']:.4g}" if b['film_ms_per_wall_minute'] is not None else 'Not recovered'
        failed = b['inner_above_1_count'] if b['inner_above_1_count'] is not None else 'Unavailable'
        lines.append(f"| {name}; N{b['native_start']}–N{b['native_end']} | {b['printed_step_min_s']*1e6:.4g}–{b['printed_step_max_s']*1e6:.4g} | {b['added_film_time_s']*1000:.6g} | {b['film_mass_kg']:.6f} | {passed} | {failed} | {b['film_ledger_error_percent']:.6g} | {cost} |")
    b = m['latest_metrics']
    if m.get('adaptive_recoveries'):
        recovery = m['adaptive_recoveries'][-1]
        rejected = recovery['rejected']['metrics']
        lines += ['', '| Adaptive recovery | Evidence / selected change |', '| --- | --- |',
                  f"| Rejected batch | N{rejected['native_start']}–N{rejected['native_end']}; peak Courant {rejected['peak_film_cfl']:.6g} exceeds 1; local pair preserved |",
                  f"| Restart | Exact passing N{recovery['restart']['pair']['native_iteration']} fields; no initialization |",
                  '| Numerical change | Fixed 5 µs ×100; then adaptive Courant 0.2, growth 1.15, reduction 2 |',
                  '| Figure lineage | Original passing branch through N7190, followed by the selected recovery; rejected continuation is excluded |']
    q = m.get('alternative_sensitivity')
    if q:
        lines += ['', '| Matched film-time comparison | Observation |', '| --- | --- |',
                  f"| Native film time | {q['film_time_s']*1000:.6g} ms; identical frozen N5080 bulk fields |",
                  f"| Reference / candidate step | {q['reference_step_s']*1e6:.6g} / {q['qualified_fixed_step_s']*1e6:.6g} µs |",
                  f"| Mass-distribution L1 difference | {q['mass_distribution_L1_percent']:.6g}% |",
                  f"| Film-mass-weighted velocity difference | {q['mass_weighted_velocity_difference_percent']:.6g}% |",
                  f"| Maximum thickness difference | {q['maximum_thickness_difference_percent']:.6g}% |",
                  f"| Predeclared local screen | {'PASS' if q['pass'] else 'FAIL'}; applies to this state and time range |",
                  '| Inner-solve limit | No inner residuals available from the alternative solver; no tolerance-pass claim |']
    lines += ['', '| Latest complete window | Rate / interpretation |', '| --- | --- |',
              f"| Accretion / drainage / storage | {b['accretion_kg_s']:.6f} / {b['drainage_kg_s']:.6f} / {b['storage_kg_s']:.6f} kg/s |",
              f"| Drainage deficit | {b['drainage_deficit_percent']:.6f}% |",
              f"| Peak film Courant / maximum thickness | {b['peak_film_cfl']:.6g} / {b['maximum_thickness_m']*1000:.6g} mm |",
              '| Observation | Inventory is still increasing; film ledger agreement does not establish inner-solve convergence |',
              '| Stationary screen | Three consecutive 1000-update windows with drainage deficit and absolute storage/accretion ≤1%; ledger ≤0.1%; finite fields with nonnegative film thickness; inspect histories |',
              '| Numerical criterion | Original solver: ≥99% inner pass and zero final residual >1. Alternative: matched-time facet-field agreement; inner residuals unavailable; repeat on developed film |',
              '| Goal closure | Restore all bulk equations; verify sustained full-model film stationarity and developed-film timestep agreement |',
              '| Claim limit | Successful startup remains supported; steady film, step-independent film distribution and whole-separator closure remain unqualified |',
              '| Alternative implicit limit | Fluent beta route printed film clocks but no h/u/v subiterations in the tested batch; absence of residuals is not convergence evidence |',
              '', '![Film development](film-development.png)', '', '![Film solver health](film-solver-health.png)', '',
              '| Evidence route | Record |', '| --- | --- |',
              '| Intent / criteria | [Setup](setup.md) |',
              '| Native reports, transcripts, residuals, clocks and paired checkpoints | [Manifest](../../../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/run-manifest.json) |',
              '| Reproducible figures | [Analysis script](../../../../../../PyAnsys/scripts/analysis/analyze_phase72a_stage3_film_development.py) |', '']
    (DEST / 'results.md').write_text('\n'.join(lines))
    (OUT / 'analysis-summary.json').write_text(json.dumps({'status': m['status'], 'blocks': blocks, 'figures': [str(DEST / 'film-development.png'), str(DEST / 'film-solver-health.png')], 'visual_qa': 'PENDING'}, indent=2))
    print('ANALYSIS_COMPLETE', len(blocks), flush=True)


if __name__ == '__main__':
    analyze()
