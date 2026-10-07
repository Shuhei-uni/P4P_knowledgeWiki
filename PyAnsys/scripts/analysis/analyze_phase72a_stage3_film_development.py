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


def write_results(lines):
    """Refresh numerical results while retaining authored figures and findings."""
    path = DEST / 'results.md'
    retained = []
    if path.exists():
        previous = path.read_text()
        for label in ['selected case history', 'wall thickness views', 'transfer findings']:
            start = f'<!-- BEGIN retained {label} -->'
            end = f'<!-- END retained {label} -->'
            if start in previous or end in previous:
                if previous.count(start) != 1 or previous.count(end) != 1:
                    raise RuntimeError(f'{label} markers are incomplete or duplicated')
                first, last = previous.index(start), previous.index(end)
                if last < first:
                    raise RuntimeError(f'{label} markers are out of order')
                retained.append(previous[first:last + len(end)])
    generated = '\n'.join(lines).rstrip()
    path.write_text('\n\n'.join([generated, *retained]) + '\n')


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
    if m.get('mid_film_selected_arm'):
        selected = m['mid_film_arms'][m['mid_film_selected_arm']]
        plotted = [*plotted, Path(selected['metrics']['output'])]
    for folder, bb in branches.items():
        if folder not in plotted:
            continue
        # The rejected N8190 history remains in its native branch. The figure
        # follows the selected field lineage through the N7190 restart.
        cutoff = None
        if folder.name == 'adaptive-development' and m.get('adaptive_recoveries'):
            cutoff = m['adaptive_recoveries'][0]['restart']['pair']['native_iteration']
            bb = [b for b in bb if b['native_end'] <= cutoff]
        if m.get('mid_film_source') and folder == Path(m['mid_film_source']['endpoint']).parent:
            cutoff = m['mid_film_source']['pair']['native_iteration']
            bb = [b for b in bb if b['native_end'] <= cutoff]
        for recovery in m.get('adaptive_recoveries', []):
            if folder == Path(recovery['restart']['endpoint']).parent:
                cutoff = recovery['restart']['pair']['native_iteration']
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
        for metric, style, color in [('accretion_kg_s', 'o-', '#1f77b4'),
                                     ('drainage_kg_s', 's--', '#d17a19'),
                                     ('storage_kg_s', 'x:', '#2ca02c')]:
            name = metric.split('_')[0]
            legend_label = name.capitalize() if name.capitalize() not in axes[1].get_legend_handles_labels()[1] else '_nolegend_'
            axes[1].plot(centers, [b[metric] for b in bb], style, color=color, label=legend_label)
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
             '| Branch limit | Initial probes share N5080; selected recoveries restart passing N7190 and N22615. Rejected N8190 and N23615 continuations are excluded from the selected field history; do not add sibling film times |',
             '| Fixed science | Full feed, R3, corrected absorber, bulk Coupled, film equations/forces/sources/boundaries and flow feedback |',
             f"| Bulk advancement | {'Original bulk equations restored; full-model film checks underway' if m.get('bulk_equations_restored') else 'Temporarily frozen during matched-time checks and relaxation; restoration required before goal closure'} |",
             '| Applying the findings | [Findings to apply to another case](#findings-to-apply-to-another-case): observed gains, reusable procedure and transfer limits |',
             '| Spatial film development | [Wall-film thickness on the separator](#wall-film-thickness-on-the-separator): shared-scale saved-snapshot comparison |',
             '| Complete selected history | [Four-panel selected case history](#four-panel-selected-case-history): inventory, signed outlet flux, film mass, accretion and drainage |',
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
    if m.get('mid_film_comparisons'):
        lines += ['', '| Mid-development matched-time arm | Mass L1 (%) | Velocity difference (%) | Thickness difference (%) | Drainage difference / accretion (%) | Ledger (%) | Peak Courant | Screen |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
        for comparison in m['mid_film_comparisons']:
            step = comparison['qualified_fixed_step_s']
            arm = next(v for v in m['mid_film_arms'].values() if abs(v['metrics']['final_accepted_step_s']-step) < 1e-12)
            met = arm['metrics']
            lines.append(f"| {step*1e6:g} µs versus 2.5 µs; identical N{comparison['source_native_iteration']} fields; +2.5 ms | {comparison['mass_distribution_L1_percent']:.6g} | {comparison['mass_weighted_velocity_difference_percent']:.6g} | {comparison['maximum_thickness_difference_percent']:.6g} | {comparison['drainage_difference_over_accretion_percent']:.6g} | {met['film_ledger_error_percent']:.6g} | {met['peak_film_cfl']:.6g} | {'PASS' if comparison['pass'] else 'FAIL'} |")
        lines += ['', '| Mid-development decision | Evidence |', '| --- | --- |',
                  '| 25 µs rejected | 0.1339% ledger error exceeds 0.1%; field agreement alone does not qualify the step |',
                  '| Smaller candidates | 20 µs, then 12.5 µs if needed; reuse the preserved reference and same 2.5 ms horizon |']
    if q:
        lines += ['', '| Matched film-time comparison | Observation |', '| --- | --- |',
                  f"| Native film time | {q['film_time_s']*1000:.6g} ms; {q['equations']} |",
                  f"| Reference / candidate step | {q['reference_step_s']*1e6:.6g} / {q['qualified_fixed_step_s']*1e6:.6g} µs |",
                  f"| Mass-distribution L1 difference | {q['mass_distribution_L1_percent']:.6g}% |",
                  f"| Film-mass-weighted velocity difference | {q['mass_weighted_velocity_difference_percent']:.6g}% |",
                  f"| Maximum thickness difference | {q['maximum_thickness_difference_percent']:.6g}% |",
                  f"| Predeclared local screen | {'PASS' if q['pass'] else 'FAIL'}; applies to this state and time range |",
                  '| Inner-solve limit | No inner residuals available from the alternative solver; no tolerance-pass claim |']
    parent = json.loads((OUT / 'parent-state.json').read_text())
    parent_bulk = parent['state']['readback']['fields']['v2-total-liquid-mass'][0]
    parent_film = parent['state']['readback']['fields']['p72a-e2.7-ewf-film-mass-total'][0]
    endpoint = json.loads((Path(b['output']) / f"endpoint-N{b['native_end']}.json").read_text())
    bulk = endpoint['state']['readback']['fields']['v2-total-liquid-mass'][0]
    lines += ['', '| Total liquid inventory | Bulk phase-2 liquid (kg) | EWF film (kg) | Sum (kg) |',
              '| --- | ---: | ---: | ---: |',
              f'| Startup endpoint N5080 | {parent_bulk:.6f} | {parent_film:.6f} | {parent_bulk+parent_film:.6f} |',
              f"| Latest saved state N{b['native_end']} | {bulk:.6f} | {b['film_mass_kg']:.6f} | {bulk+b['film_mass_kg']:.6f} |",
              '', '| Inventory interpretation | Limit |', '| --- | --- |',
              '| Definition | Bulk Eulerian phase-2 liquid plus EWF film; diagnostic DPM particles are excluded |',
              '| Frozen development | Bulk inventory is held by the disabled bulk equations; its constant value is not proof of bulk stationarity. Film accumulation increases the sum. Restore all bulk equations to judge full-model inventory and conservation. |',
              '| Physical rate | The film storage rate uses actual film time. Do not assign a physical bulk storage rate from steady pseudo-time updates. |']
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
    if m.get('transfer_receipt'):
        receipt = json.loads(Path(m['transfer_receipt']).read_text())
        row = (f"| Transfer status | N{receipt['native_iteration']} pair saved/reopened; "
               f"`{receipt['status']}`; Server 1 idle; student server not yet loaded. "
               f"[Transfer verification](../../../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/{Path(m['transfer_receipt']).name}) |")
        lines.insert(6, row)
    write_results(lines)
    (OUT / 'analysis-summary.json').write_text(json.dumps({'status': m['status'], 'blocks': blocks, 'figures': [str(DEST / 'film-development.png'), str(DEST / 'film-solver-health.png')], 'visual_qa': 'PENDING'}, indent=2))
    print('ANALYSIS_COMPLETE', len(blocks), flush=True)


if __name__ == '__main__':
    analyze()
