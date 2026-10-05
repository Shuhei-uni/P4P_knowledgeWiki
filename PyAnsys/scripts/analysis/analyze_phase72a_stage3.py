"""Audit Stage 3 native histories, bounded clock gaps, and finite startup results.

Spatial figures are separate native Fluent exports. This script plots histories
only; it does not reconstruct or composite spatial fields.
"""
from pathlib import Path
import json
import re
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from run_phase72a_adaptive_film import FILM, ROW
OUT = ROOT / 'output/phase72a-stage3-server3/20261005'
PROJECT = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction'
FIG = PROJECT / 'figures'
COLORS = {'fixed': '#0072b2', 'adaptive': '#d55e00'}
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})


def load(name):
    return json.loads((OUT / name).read_text())


def hist(label):
    h = load(f'{label}-histories.json')
    expected = np.arange(1, 3001) if label == 'bulk' else np.arange(3000, 6001)
    for name, record in h.items():
        if not np.array_equal(record['iterations'], expected):
            raise RuntimeError(f'Incomplete/duplicate history: {label} {name}')
        if not np.isfinite(record['values']).all():
            raise RuntimeError(f'Nonfinite history: {label} {name}')
    return h


def values(h, name):
    return np.asarray(h[name]['values'], dtype=float)


def mean_window(v, count=500):
    a = np.asarray(v)[-count:]
    return {'mean': float(a.mean()), 'std': float(a.std()), 'min': float(a.min()),
            'max': float(a.max()), 'window': count,
            'change_first_to_last': float(a[-1] - a[0]),
            'slope_per_iteration': float(np.polyfit(np.arange(count), a, 1)[0])}


def metric_arrays(h):
    return {'liquid_carryover_kg_s': -values(h, 'v2-flux-phase2-steamoutlet'),
            'vapor_outlet_kg_s': -values(h, 'v2-flux-phase1-steamoutlet'),
            'bulk_inventory_kg': values(h, 'v2-total-liquid-mass'),
            'pressure_drop_Pa': values(h, 'p72s3-pressure-inlet') - values(h, 'p72s3-pressure-outlet'),
            'contact_removal_kg_s': -values(h, 'v2-applied-absorber')}


def validate_report_semantics(label, h, endpoint):
    fields = endpoint['readback']['fields']
    for name in ['v2-flux-phase2-liquidinlet', 'v2-flux-phase2-steamoutlet']:
        without = fields[name + '(without-sources)'][0]
        source = fields['v2-applied-absorber'][0]
        if not np.isclose(fields[name][0] - source, without, atol=1e-7, rtol=1e-8):
            raise RuntimeError('Computed source-inclusive report decomposition changed')
        if not np.isclose(values(h, name)[-1], without, atol=1e-7, rtol=1e-8):
            raise RuntimeError(f'{label}: report-file boundary semantics changed')
    for name in ['v2-applied-absorber', 'p72-contact-removal', 'v2-total-liquid-mass', 'p72a-e2.7-ewf-film-mass-total']:
        if not np.isclose(values(h, name)[-1], fields[name][0], atol=1e-7, rtol=1e-8):
            raise RuntimeError(f'{label}: final history does not match saved fields')
    err = values(h, 'p72-contact-removal') + values(h, 'v2-applied-absorber')
    if np.max(np.abs(err)) > 1e-7:
        raise RuntimeError('Applied contact removal does not match independent source expression')
    return {'report_file_fluxes': 'Boundary-only; confirmed against without-sources saved endpoint values',
            'compute_fluxes': 'Include the user mass source in each computed phase-2 report',
            'boundary_flux_history_source_subtraction': 'NONE; subtracting source again would double count',
            'contact_source_max_expression_error_kg_s': float(np.max(np.abs(err)))}


def parse_segment(filename, endpoint):
    clocks, residuals, pending = {}, {}, None
    text = (OUT / filename).read_text()
    for line in text.splitlines():
        match = FILM.search(line)
        if match:
            if pending is not None:
                raise RuntimeError(f'Unmapped nonterminal native film line: {filename}')
            pending = [float(v) for v in match.groups()]
        elif ROW.match(line):
            n = int(ROW.match(line)[1])
            try:
                row = [float(v) for v in line.split()[1:8]]
                if len(row) == 7:
                    residuals[n] = row
            except ValueError:
                pass
            if pending is not None:
                if n in clocks and clocks[n] != pending:
                    raise RuntimeError('Conflicting native clock duplicate')
                clocks[n] = pending
                pending = None
    reconciliation = None
    if pending is not None:
        # The final printed film clock is followed by endpoint reports and paired
        # save, while the final residual row is absent. The paired endpoint proves
        # the native coordinate. Retain this explicit mapping and residual gap.
        if max(clocks, default=0) != endpoint - 1 or 'Writing to' not in text:
            raise RuntimeError('Terminal clock cannot be reconciled to a saved endpoint')
        clocks[endpoint] = pending
        reconciliation = {'native_iteration': endpoint, 'film_clock_s': pending[0],
                          'basis': 'Last printed film line + paired saved/reopened native endpoint; terminal residual row absent'}
    return clocks, residuals, reconciliation, text


def film_arm(arm, manifest, h):
    segments = manifest.get('adaptive_transcript_segments', [f'{arm}-film-transcript.txt']) if arm == 'adaptive' else [f'{arm}-film-transcript.txt']
    clocks, residuals, reconciliations, text = {}, {}, [], ''
    for filename in segments:
        endpoint = 4404 if filename == 'adaptive-film-transcript.txt' else 6000
        c, r, rec, raw = parse_segment(filename, endpoint)
        if set(clocks).intersection(c):
            raise RuntimeError('Unexpected overlapping immutable transcript segments')
        clocks.update(c); residuals.update(r); text += raw
        if rec:
            reconciliations.append(rec)
    ids = np.array(sorted(clocks))
    if ids[0] != 3001 or ids[-1] != 6000:
        raise RuntimeError('Native film endpoints missing')
    initial = clocks[3001][0] - clocks[3001][1]
    t = np.array([clocks[int(i)][0] - initial for i in ids])
    if np.any(np.diff(t) <= 0):
        raise RuntimeError('Non-increasing native film clock')
    mass = values(h, 'p72a-e2.7-ewf-film-mass-total')
    drain = values(h, 'p72a-e2.7-ewf-outflow-mass-total')
    acc = values(h, 'p72a-e2.7-ewf-secondary-phase-mass-total')
    lower, upper, known_time, known_mass, known_drain = [0.], [0.], [0.], [mass[0]], [0.]
    previous_n, previous_t = 3000, 0.
    gaps = []
    for n, time_value in zip(ids, t):
        width = time_value - previous_t
        if n == previous_n + 1:
            lo = hi = acc[n - 3000] * width
        else:
            rates = acc[previous_n - 3000 + 1:n - 3000 + 1]
            lo, hi = float(rates.min() * width), float(rates.max() * width)
            gaps.append({'missing_start': int(previous_n + 1), 'missing_end': int(n - 1),
                         'bounded_interval_s': float(width), 'rate_min_kg_s': float(rates.min()),
                         'rate_max_kg_s': float(rates.max()),
                         'integrated_accretion_lower_kg': lo, 'integrated_accretion_upper_kg': hi})
        lower.append(lower[-1] + lo); upper.append(upper[-1] + hi)
        known_time.append(time_value); known_mass.append(mass[n - 3000]); known_drain.append(drain[n - 3000] - drain[0])
        previous_n, previous_t = n, time_value
    storage_plus_drain = mass[-1] - mass[0] + drain[-1] - drain[0]
    ledger_lo = storage_plus_drain - upper[-1]
    ledger_hi = storage_plus_drain - lower[-1]
    worst = 100 * max(abs(ledger_lo), abs(ledger_hi)) / max(lower[-1], 1e-30)
    windows = []
    for begin, end in [(3000, 4000), (4000, 5000), (5000, 6000)]:
        t0 = 0 if begin == 3000 else clocks[begin][0] - initial
        t1 = clocks[end][0] - initial
        dmass = mass[end - 3000] - mass[begin - 3000]
        ddrain = drain[end - 3000] - drain[begin - 3000]
        windows.append({'native_start': begin, 'native_end': end, 'film_time_s': t1 - t0,
                        'inventory_growth_kg_s': float(dmass / (t1 - t0)),
                        'drainage_kg_s': float(ddrain / (t1 - t0)),
                        'accretion_mean_kg_s': float(np.mean(acc[begin - 3000 + 1:end - 3000 + 1]))})
    missing = sorted(set(range(3001, 6001)) - set(clocks))
    info = {'native_updates': 3000, 'native_end': 6000, 'film_elapsed_s': float(t[-1]),
            'initial_native_clock_s': float(initial), 'observed_clock_records': len(ids),
            'missing_clock_updates': missing, 'clock_gap_bounds': gaps,
            'terminal_clock_reconciliations': reconciliations,
            'printed_step_min_s': min(v[1] for v in clocks.values()),
            'printed_step_max_s': max(v[1] for v in clocks.values()),
            'observed_peak_film_cfl': max(v[2] for v in clocks.values()),
            'film_mass_end_kg': float(mass[-1]), 'drained_mass_kg': float(drain[-1] - drain[0]),
            'integrated_accretion_lower_kg': lower[-1], 'integrated_accretion_upper_kg': upper[-1],
            'film_ledger_residual_lower_kg': ledger_lo, 'film_ledger_residual_upper_kg': ledger_hi,
            'film_ledger_worst_bound_percent': float(worst), 'film_ledger_1_percent_screen_pass': bool(worst <= 1),
            'windows': windows,
            'warnings': {'reverse_flow_messages': text.count('Reversed flow'),
                         'viscosity_limit_messages': text.count('turbulent viscosity limited'),
                         'fatal_messages': len(re.findall(r'floating point exception|divergence detected|Error at host', text, flags=re.I))},
            'residual_last_500': {name: mean_window([row[k] for n, row in sorted(residuals.items()) if n >= 5500], min(500, len([n for n in residuals if n >= 5500]))) for k, name in enumerate(['continuity', 'x_velocity', 'y_velocity', 'z_velocity', 'k', 'epsilon', 'phase2_vof'])}}
    return {'info': info, 'clocks': clocks, 'residuals': residuals,
            'time': np.asarray(known_time), 'mass': np.asarray(known_mass), 'drain': np.asarray(known_drain),
            'acc_lower': np.asarray(lower), 'acc_upper': np.asarray(upper)}


def style(ax, ylabel=None):
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(alpha=.2)


def savefig(fig, filename):
    fig.tight_layout(); fig.savefig(FIG / filename, dpi=180, bbox_inches='tight'); plt.close(fig)


def figures(bulk, histories, arms, refs):
    x = np.asarray(bulk['v2-total-liquid-mass']['iterations'])
    b = metric_arrays(bulk)
    fig, axs = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    axs[0].plot(x, values(bulk, 'v2-flux-phase2-liquidinlet'), label='Liquid feed', lw=1.3)
    axs[0].plot(x, b['contact_removal_kg_s'], label='Contact removal', lw=.7, alpha=.8)
    axs[0].plot(x, b['liquid_carryover_kg_s'], label='Liquid outlet', lw=1)
    axs[0].legend(); axs[0].set_title('Carrier startup with film equations off')
    axs[1].plot(x, b['bulk_inventory_kg']); axs[1].axhline(refs['bulk_inventory_kg'], color='k', ls='--', label='Developed reference snapshot'); axs[1].legend()
    axs[2].plot(x, b['pressure_drop_Pa'] / 1000); axs[2].axhline(refs['pressure_drop_Pa'] / 1000, color='k', ls='--')
    for a, unit in zip(axs, ['kg/s', 'Bulk liquid (kg)', 'Pressure drop (kPa)']):
        style(a, unit)
        for n in [1500, 2500]: a.axvline(n, color='.6', ls=':', lw=.8)
    axs[-1].set_xlabel('Native iteration; low feed to 1500, ramp to 2500, target hold to 3000')
    savefig(fig, 'bulk-startup.png')
    fig, axs = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    for arm, a in arms.items():
        c = COLORS[arm]; axs[0].plot(a['time'] * 1000, a['mass'], label=arm, color=c, ls='--' if arm == 'adaptive' else '-')
        axs[1].plot(a['time'] * 1000, (a['acc_lower'] + a['acc_upper']) / 2, color=c, label=arm + ' accretion')
        axs[1].plot(a['time'] * 1000, a['drain'], color=c, ls=':', label=arm + ' drainage')
        ledger_l = a['mass'] - a['mass'][0] + a['drain'] - a['acc_upper']
        ledger_u = a['mass'] - a['mass'][0] + a['drain'] - a['acc_lower']
        axs[2].plot(a['time'] * 1000, (ledger_l + ledger_u) / 2 * 1e6, color=c, label=arm)
        axs[2].fill_between(a['time'] * 1000, ledger_l * 1e6, ledger_u * 1e6, color=c, alpha=.2)
    axs[0].set_title('Only 3 ms of film development: fixed and adaptive traces overlap')
    axs[0].text(.04, .85, f"Reference film inventory: {refs['film_mass_kg']:.3f} kg (outside startup scale)", transform=axs[0].transAxes)
    for a, unit in zip(axs, ['Film inventory (kg)', 'Integrated mass (kg)', 'Ledger residual (mg)']): style(a, unit); a.legend(fontsize=9)
    axs[-1].set_xlabel('Elapsed native film time (ms); adaptive ledger band bounds 13 missing clocks')
    savefig(fig, 'film-matched-time.png')
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for arm, a in arms.items():
        ns = np.arange(3001, 6001)
        step = np.array([a['clocks'].get(int(n), [np.nan] * 3)[1] * 1e6 for n in ns])
        cfl = np.array([a['clocks'].get(int(n), [np.nan] * 3)[2] for n in ns])
        axs[0].plot(ns - 3000, step, label=arm, color=COLORS[arm], ls='--' if arm == 'adaptive' else '-')
        axs[1].plot(ns - 3000, cfl, label=arm, color=COLORS[arm], ls='--' if arm == 'adaptive' else '-')
    axs[0].set_ylim(.95, 1.05); axs[0].set_title('Printed native steps stayed at 1 µs')
    axs[1].axhline(.1, color='k', ls=':', label='Adaptive target 0.1'); axs[1].set_title('Film Courant number remained below target')
    for a, unit in zip(axs, ['Printed step (µs)', 'Maximum film Courant number']): style(a, unit); a.set_xlabel('Film updates'); a.legend(fontsize=9)
    savefig(fig, 'accepted-film-steps.png')
    fig, axs = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    specs = [('liquid_carryover_kg_s', 'Liquid outlet (kg/s)', 1), ('bulk_inventory_kg', 'Bulk inventory (kg)', 1),
             ('vapor_outlet_kg_s', 'Vapor outlet (kg/s)', 1), ('pressure_drop_Pa', 'Pressure drop (kPa)', .001)]
    for ax, (key, unit, factor) in zip(axs.flat, specs):
        for arm, h in histories.items():
            v = metric_arrays(h)[key]; xx = np.asarray(h['v2-total-liquid-mass']['iterations'])
            mask = xx >= 5000
            ax.plot(xx[mask], v[mask] * factor, color=COLORS[arm], alpha=.4, lw=.7)
            roll = np.convolve(v, np.ones(100) / 100, mode='valid')
            roll_x = xx[99:]; roll_mask = roll_x >= 5000
            ax.plot(roll_x[roll_mask], roll[roll_mask] * factor, color=COLORS[arm], label=arm + ' 100-update mean', lw=1.4)
        ax.axhline(refs[key] * factor, color='k', ls='--', label='Reference snapshot')
        style(ax, unit); ax.set_xlim(5000, 6000); ax.legend(fontsize=8)
    for a in axs[-1]: a.set_xlabel('Native iteration (film enabled at 3000)')
    savefig(fig, 'carrier-final-window.png')
    fig, axs = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    for arm, h in histories.items():
        ns = np.asarray(h['v2-total-liquid-mass']['iterations'])
        mask = ns >= 5000
        feed = values(h, 'v2-flux-phase2-liquidinlet'); carry = -values(h, 'v2-flux-phase2-steamoutlet')
        sink = -values(h, 'v2-applied-absorber'); acc = values(h, 'p72a-e2.7-ewf-secondary-phase-mass-total')
        axs[0].plot(ns[mask], sink[mask], color=COLORS[arm], lw=.8, alpha=.7, label=arm)
        axs[1].plot(ns[mask], (feed - carry - sink)[mask], color=COLORS[arm], lw=.8, label=arm + ' bulk boundary + contact residual')
        axs[1].plot(ns[mask], acc[mask], color=COLORS[arm], ls='--', lw=1, label=arm + ' film accretion')
        r = arms[arm]['residuals']; xx = np.asarray([n for n in sorted(r) if n >= 5000])
        axs[2].semilogy(xx, [r[int(n)][0] for n in xx], color=COLORS[arm], alpha=.7, lw=.8, label=arm + ' continuity')
        axs[2].semilogy(xx, [r[int(n)][6] for n in xx], color=COLORS[arm], ls='--', alpha=.7, lw=.8, label=arm + ' phase-2 fraction')
    axs[0].set_title('Contact source fluctuates despite similar carrier scalar means')
    for a, unit in zip(axs, ['Contact removal (kg/s)', 'Rates (kg/s)', 'Scaled residual']): style(a, unit); a.legend(fontsize=8); a.set_xlim(5000, 6000)
    axs[-1].set_xlabel('Native iteration; no interpolation of missing residual rows')
    savefig(fig, 'numerical-accounting.png')
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for arm, h in histories.items():
        ns = np.asarray(h['p72a-e2.7-ewf-thickness-max']['iterations'])
        axs[0].plot(ns - 3000, values(h, 'p72a-e2.7-ewf-thickness-max') * 1e3, color=COLORS[arm], label=arm + ' maximum')
        axs[0].plot(ns - 3000, values(h, 'p72a-e2.7-ewf-thickness-awavg') * 1e3, color=COLORS[arm], ls='--', label=arm + ' area mean')
        ratios = [values(h, 'p72a-e2.7-ewf-film-mass-total')[-1] / refs['film_mass_kg'],
                  values(h, 'p72a-e2.7-ewf-thickness-max')[-1] / refs['film_max_m'],
                  values(h, 'p72a-e2.7-ewf-thickness-awavg')[-1] / refs['film_mean_m']]
        pos = np.arange(3) + (-.16 if arm == 'fixed' else .16)
        axs[1].bar(pos, np.asarray(ratios) * 100, width=.32, color=COLORS[arm], label=arm)
    axs[0].set(xlabel='Film updates', ylabel='Film thickness (mm)', title='Peak thickness falls while total film inventory grows')
    axs[1].axhspan(90, 110, color='#009e73', alpha=.15, label='±10% reference screen band')
    axs[1].set_xticks(range(3), ['Inventory', 'Maximum thickness', 'Mean thickness']); axs[1].set_ylim(0, 115)
    axs[1].set(ylabel='Percentage of reference snapshot', title='Film reproduction screen fails')
    for a in axs: style(a); a.legend(fontsize=8)
    savefig(fig, 'film-reproduction.png')


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    m = load('run-manifest.json')
    if m['status'] != 'STARTUP_SCREENS_COMPLETE_ANALYSIS_REQUIRED' or m.get('final_reopen') != 'PASS':
        raise RuntimeError('Both completed saved/reopened startup screens are required')
    refstate = load('reference-state.json'); ref = refstate['readback']['fields']; extra = load('reference-extra-reports.json')
    refs = {'liquid_carryover_kg_s': -ref['v2-flux-phase2-steamoutlet(without-sources)'][0],
            'vapor_outlet_kg_s': -ref['v2-flux-phase1-steamoutlet'][0],
            'bulk_inventory_kg': ref['v2-total-liquid-mass'][0],
            'pressure_drop_Pa': extra['p72s3-pressure-inlet'][0] - extra['p72s3-pressure-outlet'][0],
            'contact_removal_kg_s': ref['p72-contact-removal'][0],
            'film_mass_kg': ref['p72a-e2.7-ewf-film-mass-total'][0],
            'film_max_m': ref['p72a-e2.7-ewf-thickness-max'][0],
            'film_mean_m': extra['p72a-e2.7-ewf-thickness-awavg'][0]}
    bulk = hist('bulk'); histories = {arm: hist(arm) for arm in ['fixed', 'adaptive']}
    semantics = {'bulk': validate_report_semantics('bulk', bulk, load('bulk-endpoint.json'))}
    arms = {}
    summary = {'status': 'TESTED_RECIPE_CARRIER_SCREEN_PASSES_FILM_REPRODUCTION_FAILS',
               'reference': refs, 'reference_native_iteration': 33586,
               'reference_stationarity': 'NOT_QUALIFIED', 'arms': {},
               'bulk_final_500': {k: mean_window(v) for k, v in metric_arrays(bulk).items()}}
    for arm, h in histories.items():
        endpoint = load(f'{arm}-endpoint-N6000.json')
        require = load(f'{arm}-final-reopen.json')
        if require['readback'] != endpoint['state']['readback']:
            raise RuntimeError('Saved endpoint did not reopen exactly')
        semantics[arm] = validate_report_semantics(arm, h, endpoint['state'])
        a = film_arm(arm, m, h); arms[arm] = a; info = a['info']
        info['comparisons'] = {}
        for key, v in metric_arrays(h).items():
            tol = 5 if key in ['vapor_outlet_kg_s', 'pressure_drop_Pa'] else 10
            windows = {str(w): mean_window(v, w) for w in [250, 500, 1000]}
            mean = windows['500']['mean']; error = 100 * (mean - refs[key]) / abs(refs[key])
            info['comparisons'][key] = {'final_500_mean': mean, 'reference_snapshot': refs[key],
                                        'difference_percent': error, 'screen_tolerance_percent': tol,
                                        'scalar_screen_pass': abs(error) <= tol, 'windows': windows}
        for key, name in [('film_mass_kg', 'p72a-e2.7-ewf-film-mass-total'), ('film_max_m', 'p72a-e2.7-ewf-thickness-max'), ('film_mean_m', 'p72a-e2.7-ewf-thickness-awavg')]:
            v = values(h, name); info['comparisons'][key] = {'endpoint': float(v[-1]), 'final_500_mean': float(v[-500:].mean()),
                                                            'reference_snapshot': refs[key], 'endpoint_difference_percent': float(100 * (v[-1] - refs[key]) / refs[key]),
                                                            'screen_tolerance_percent': 10, 'scalar_screen_pass': bool(abs(100 * (v[-500:].mean() - refs[key]) / refs[key]) <= 10)}
        bulk_net = values(h, 'v2-flux-phase2-liquidinlet') + values(h, 'v2-flux-phase2-steamoutlet') + values(h, 'v2-applied-absorber')
        info['bulk_accounting'] = {'boundary_plus_contact_final_500_kg_s': mean_window(bulk_net),
                                   'conditional_minus_film_accretion_final_500_kg_s': mean_window(bulk_net - values(h, 'p72a-e2.7-ewf-secondary-phase-mass-total')),
                                   'interpretation': 'Boundary + user-source residual excludes EWF transfers; conditional subtraction is not a verified whole-separator balance; steady pseudo-time inventory slope is not physical dM/dt'}
        thickness = values(h, 'p72a-e2.7-ewf-thickness-max')
        info['peak_thickness_m'] = float(thickness.max())
        info['peak_thickness_native_iteration'] = int(h['p72a-e2.7-ewf-thickness-max']['iterations'][int(thickness.argmax())])
        info['documented_block_wall_seconds'] = sum(b['wall_seconds'] for b in m['blocks'] if b.get('arm') == arm)
        info['wall_cost_complete'] = arm == 'fixed'
        info['unrecorded_solve_updates_for_cost'] = 404 if arm == 'adaptive' else 0
        summary['arms'][arm] = info
    summary['history_semantics'] = semantics
    summary['bulk_wall_seconds_including_smoke'] = m['bulk_wall_seconds'] + m['smoke']['wall_seconds']
    summary['fixed_recipe_measured_wall_seconds'] = summary['bulk_wall_seconds_including_smoke'] + summary['arms']['fixed']['documented_block_wall_seconds']
    summary['film_endpoint_fixed_adaptive_difference_percent'] = 100 * (summary['arms']['adaptive']['film_mass_end_kg'] - summary['arms']['fixed']['film_mass_end_kg']) / summary['arms']['fixed']['film_mass_end_kg']
    summary['claim_limits'] = ['Finite 3 ms film startup; developing reference', 'No steady whole-separator qualification',
                              'No adaptive speedup observed', '13 adaptive clock records missing; ledger bounded without step interpolation',
                              'No new DPM fate audit', 'Adaptive measured cost excludes pre-stop N4000–N4404 solve duration',
                              'No paired-film 0.2–0.5 s extension or mesh family selected']
    # Spatial summaries use sampled native fields only for numerical diagnostics;
    # all deliverable spatial images come from native Fluent graphics exports.
    spatial = {}
    for case in ['bulk', 'fixed', 'adaptive']:
        refplane = np.load(OUT / 'reference-p72s3-xy-z0.npz'); plane = np.load(OUT / f'{case}-p72s3-xy-z0.npz')
        if not np.array_equal(plane['centroids'], refplane['centroids']):
            raise RuntimeError('Spatial sample coordinates differ; no facetwise comparison permitted')
        spatial[case] = {}
        for field in ['phase-2-vof', 'velocity-magnitude']:
            diff = plane[field] - refplane[field]
            spatial[case][field] = {'unweighted_facet_rms_difference': float(np.sqrt(np.mean(diff ** 2))),
                                    'unweighted_facet_max_absolute_difference': float(np.max(np.abs(diff))),
                                    'basis': 'Same native Z=0 facet samples; not volume/area weighted or a physical validation tolerance'}
    summary['spatial_diagnostics'] = spatial
    figures(bulk, histories, arms, refs)
    (OUT / 'analysis-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'status': summary['status'], 'film': {k: v['info'] for k, v in arms.items()}, 'fixed_recipe_minutes': summary['fixed_recipe_measured_wall_seconds'] / 60}, indent=2))


if __name__ == '__main__':
    main()
