"""Analyse directly recovered Stage 4 histories; never issue solver updates."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'PyAnsys/output/phase72a-stage4-ewf-long-native/20261007'
RAW = OUT / 'raw/terminal-N68483'
DOC = ROOT / ('Project/experiments/phase-07-2a-wall-liquid-routing/'
              'stage-04-ewf-wall-parameters/ewf-only-drain/long-development')


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    receipt = json.loads((OUT / 'retrieval-20261008/receipt.json').read_text())
    reopened = json.loads((OUT / 'inspection/reopen-N68483.json').read_text())
    manifest = json.loads((OUT / 'run-manifest.json').read_text())
    prepared = json.loads((OUT / 'prepared-readback.json').read_text())
    ids = np.arange(41483, 68484)
    h = {}
    hashes = {}
    for record in receipt['sources']:
        path = RAW / record['path']
        contents = path.read_bytes()
        assert len(contents) == record['bytes']
        assert hashlib.sha256(contents).hexdigest() == record['sha256']
        hashes[str(path.relative_to(ROOT))] = record['sha256']
        if path.suffix == '.out':
            rows = []
            for line in contents.decode('ascii').splitlines():
                parts = line.split()
                if len(parts) == 2 and parts[0].isdigit():
                    rows.append((int(parts[0]), float(parts[1])))
            a = np.asarray(rows)
            assert np.array_equal(a[:, 0], ids), path.name
            assert np.isfinite(a[:, 1]).all(), path.name
            h[path.stem] = a[:, 1]
    text = (RAW / 'native-long-run.trn').read_text()
    film = np.asarray([tuple(map(float, m)) for m in re.findall(
        r'Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)', text)])
    assert len(film) == len(ids) - 1 == 27000
    assert np.all(film[:, 1] == 15e-6)
    assert text.count('/solve/iterate 1000') == 27
    assert reopened['native_iteration'] == ids[-1]
    dt = film[:, 1]
    t0 = prepared['film']['film_elapsed_time']
    elapsed = np.r_[0., np.cumsum(dt)]
    clock = t0 + elapsed
    assert np.max(np.abs(clock[1:] - film[:, 0])) < 5.1e-8
    assert abs(clock[-1] - reopened['film']['film_elapsed_time']) < 1e-9
    assert reopened['film']['max_timestep_count'] - prepared['film']['max_timestep_count'] == 27000
    assert np.allclose(film[:, 2], h['p72d-total-courant'][1:], atol=5.1e-7, rtol=1e-6)
    assert np.allclose(h['p72d-total-mass'], h['p72d-upper-mass'] + h['p72d-lower-mass'], rtol=1e-12, atol=1e-12)
    assert np.allclose(h['p72d-lower-inventory'], h['p72d-lower-mass'], rtol=1e-12, atol=1e-12)
    crossing = np.flatnonzero(h['p72d-total-courant'] >= 1)
    first = int(crossing[0])
    last_valid = first - 1
    assert np.max(h['p72d-lower-courant']) < 1
    assert np.array_equal(h['p72d-total-courant'], h['p72d-upper-courant'])

    def ledger(a, b):
        steps = dt[a:b]
        duration = float(np.sum(steps))
        changes = {k: float(h['p72d-total-' + k][b] - h['p72d-total-' + k][a])
                   for k in ['mass', 'outflow', 'stripped', 'separated']}
        inputs = {k: float(np.sum(h['p72d-total-' + k][a + 1:b + 1] * steps))
                  for k in ['secondary', 'dpm']}
        drain_left = float(np.sum(h['p72d-drain-rate'][a:b] * steps))
        drain_right = float(np.sum(h['p72d-drain-rate'][a + 1:b + 1] * steps))
        residual = sum(changes.values()) + drain_left - sum(inputs.values())
        residual_right = sum(changes.values()) + drain_right - sum(inputs.values())
        return dict(native_window=[int(ids[a]), int(ids[b])],
                    added_time_window_s=[float(elapsed[a]), float(elapsed[b])],
                    duration_s=duration, changes_kg=changes, inputs_kg=inputs,
                    direct_drain_left_kg=drain_left, direct_drain_right_kg=drain_right,
                    drain_quadrature_span_kg=abs(drain_right - drain_left),
                    ledger_residual_left_kg=residual, ledger_residual_right_kg=residual_right,
                    ledger_error_left_percent=100 * abs(residual) / sum(inputs.values()),
                    ledger_error_right_percent=100 * abs(residual_right) / sum(inputs.values()),
                    input_mean_kg_s=sum(inputs.values()) / duration,
                    direct_drain_mean_kg_s=drain_left / duration,
                    storage_mean_kg_s=changes['mass'] / duration,
                    storage_percent_of_input=100 * changes['mass'] / sum(inputs.values()),
                    contains_courant_guard_crossing=bool(np.any(h['p72d-total-courant'][a + 1:b + 1] >= 1)))

    whole = ledger(0, len(ids) - 1)
    before = ledger(0, last_valid)
    pre_15ms = ledger(last_valid - 1000, last_valid)
    pre_75ms = ledger(last_valid - 5000, last_valid)
    windows = [ledger(a, b) for a, b in zip([0, 5000, 10000, 15000, 20000, 25000],
                                           [5000, 10000, 15000, 20000, 25000, 27000])]
    bulk = {name: {'min': float(h[name].min()), 'max': float(h[name].max()),
                   'unchanged': bool(np.ptp(h[name]) == 0)}
            for name in ['v2-total-liquid-mass', 'v2-flux-phase2-steamoutlet', 'v2-flux-phase1-steamoutlet']}
    assert all(v['unchanged'] for v in bulk.values())
    assert not any(reopened['audit']['equations'].values())
    peak_c = int(np.argmax(h['p72d-total-courant']))
    peak_speed = int(np.argmax(h['p72a-e2.7-ewf-velocity-mag-max']))
    result = dict(
        status='STOPPED_NUMERICAL_GUARD_RECOVERED_ANALYSED', native_start=int(ids[0]),
        native_end=int(ids[-1]), updates=len(ids) - 1, planned_updates=manifest['submitted_updates'],
        full_horizon_reached=False, parent_film_clock_s=t0,
        endpoint_film_clock_s=reopened['film']['film_elapsed_time'],
        added_native_film_time_s=reopened['film']['film_elapsed_time'] - t0,
        time_verification='27000 printed accepted steps, printed film clocks, saved RP clock and counter agree',
        accepted_step_min_s=float(dt.min()), accepted_step_max_s=float(dt.max()),
        native_samples_per_report=len(ids), native_report_count=len(h),
        required_report_histories_complete=True, paired_endpoint_reopen='PASS',
        film_initial_kg=float(h['p72d-total-mass'][0]), film_final_kg=float(h['p72d-total-mass'][-1]),
        upper_initial_kg=float(h['p72d-upper-mass'][0]), upper_final_kg=float(h['p72d-upper-mass'][-1]),
        lower_initial_kg=float(h['p72d-lower-mass'][0]), lower_final_kg=float(h['p72d-lower-mass'][-1]),
        lower_min_kg=float(h['p72d-lower-mass'].min()), lower_max_kg=float(h['p72d-lower-mass'].max()),
        drain_final_kg_s=float(h['p72d-drain-rate'][-1]),
        direct_drain_active_with_frozen_bulk=True, bulk_reports=bulk,
        bulk_equation_groups_frozen=True,
        bulk_phase2_outlet_history_component='Boundary flux without sources; reopened source-inclusive report also contains User Mass Source',
        peak_thickness_m=float(h['p72d-total-thickness'].max()),
        peak_thickness_iteration=int(ids[np.argmax(h['p72d-total-thickness'])]),
        thickness_limit_reached=False, peak_courant=float(h['p72d-total-courant'][peak_c]),
        peak_courant_iteration=int(ids[peak_c]), final_courant=float(h['p72d-total-courant'][-1]),
        lower_peak_courant=float(h['p72d-lower-courant'].max()),
        first_courant_crossing_iteration=int(ids[first]),
        first_courant_crossing_added_time_s=float(elapsed[first]),
        samples_courant_gte_1=int(len(crossing)),
        updates_after_first_crossing=int(ids[-1] - ids[first]),
        peak_film_speed_m_s=float(h['p72a-e2.7-ewf-velocity-mag-max'][peak_speed]),
        peak_film_speed_iteration=int(ids[peak_speed]),
        final_film_speed_max_m_s=float(h['p72a-e2.7-ewf-velocity-mag-max'][-1]),
        speed_and_courant_peaks_same_iteration=peak_speed == peak_c,
        native_stop_classification='NUMERICAL_REJECTED',
        failure_tail_scope='Retained in figures and whole-run ledger; no qualification of post-crossing interval',
        full_run_ledger=whole, pre_guard_ledger=before,
        pre_guard_last_15ms=pre_15ms, pre_guard_last_75ms=pre_75ms, descriptive_windows=windows,
        accounting='Inputs: phase/DPM collection. Outputs: native outflow, stripped/separated transfer, and direct user sink once. Storage: total film mass change.',
        source_rate_quadrature='Collection: current native rate times accepted step; direct sink: preceding native rate, current-rate span also reported',
        steady_film=False, stationarity_qualification='FAILED_GUARD_AND_CONTINUING_STORAGE; 0.75 s qualification span not available',
        inner_residual_history='NOT_RECORDED_IN_SAVED_TRANSCRIPT',
        inner_residual_rows=len(re.findall(r'sub-iteration:\s*\d+ residual', text)),
        solver_fpe_or_divergence_message_in_saved_transcript=bool(re.search(r'floating.point.exception|divergence detected', text, re.I)),
        specific_setting_cause='UNRESOLVED; upper-wall location and speed/Courant spikes do not isolate one mechanism',
        physical_validation=False, source_sha256=hashes, new_solve_calls=0,
    )
    assert result['inner_residual_rows'] == 0
    dump(OUT / 'analysis-summary.json', result)
    names = sorted(h)
    with (OUT / 'film-history.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['native_iteration', 'film_time_s', 'added_film_time_s', *names])
        writer.writerows([int(ids[i]), float(clock[i]), float(elapsed[i]), *(float(h[n][i]) for n in names)]
                         for i in range(len(ids)))
    figs = DOC / 'figures'
    figs.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    x = elapsed * 1000
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7), constrained_layout=True)
    axes[0, 0].plot(x, h['p72d-total-mass'], color='#0072B2', label='Total film')
    axes[0, 0].plot(x, h['p72d-upper-mass'], color='#D55E00', ls='--', label='Upper film')
    axes[0, 0].set_ylabel('Film inventory (kg)')
    axes[0, 1].plot(x, h['p72d-lower-mass'] * 1000, color='#0072B2', label='Lower collector')
    axes[0, 1].set_ylabel('Lower film inventory (g)')
    axes[0, 1].secondary_yaxis('right', functions=(lambda g: g * (2/3), lambda rate: rate * 1.5)).set_ylabel('Direct drain rate (kg/s)')
    for scope, color in [('upper', '#0072B2'), ('lower', '#009E73')]:
        axes[1, 0].plot(x, h['p72d-' + scope + '-thickness'] * 1000, color=color, label=scope.capitalize())
        axes[1, 1].plot(x, h['p72d-' + scope + '-courant'], color=color, label=scope.capitalize())
    axes[1, 0].set_ylabel('Maximum thickness (mm)')
    axes[1, 1].set_ylabel('Maximum film Courant')
    axes[1, 1].set_yscale('log')
    axes[1, 1].axhline(1, color='#D55E00', ls='--', label='Declared guard = 1')
    for ax in axes.flat:
        ax.axvspan(x[first], x[-1], color='#D55E00', alpha=.13)
        ax.set_xlabel('Added native EWF time (ms)')
        ax.set_xlim(0, x[-1])
        ax.grid(alpha=.2)
        ax.legend(loc='best')
    fig.suptitle('EWF development with direct drain — bulk frozen; shaded tail starts at first Courant crossing')
    fig.savefig(figs / 'film-development.png', dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), constrained_layout=True)
    pos = np.arange(len(windows))
    bottom_in = np.zeros(len(windows))
    bottom_out = np.zeros(len(windows))
    for key, label, color in [('secondary', 'Phase collection', '#56B4E9'), ('dpm', 'DPM collection', '#CC79A7')]:
        values = np.array([w['inputs_kg'][key] / w['duration_s'] for w in windows])
        axes[0].bar(pos - .19, values, width=.36, bottom=bottom_in, label=label, color=color)
        bottom_in += values
    for key, label, color in [('drain', 'Direct drain', '#0072B2'), ('outflow', 'Native outflow', '#D55E00'),
                              ('transfer', 'Stripping + separation', '#009E73'), ('mass', 'Film storage', '#888888')]:
        values = np.array([(w['direct_drain_left_kg'] if key == 'drain' else
                            w['changes_kg']['stripped'] + w['changes_kg']['separated'] if key == 'transfer' else
                            w['changes_kg'][key]) / w['duration_s'] for w in windows])
        axes[0].bar(pos + .19, values, width=.36, bottom=bottom_out, label=label, color=color)
        bottom_out += values
    axes[0].set_xticks(pos, [f"{w['added_time_window_s'][0]*1000:.0f}–{w['added_time_window_s'][1]*1000:.0f}" + ('*' if w['contains_courant_guard_crossing'] else '') for w in windows])
    axes[0].set_xlabel('Added native EWF time window (ms); *includes rejected tail')
    axes[0].set_ylabel('Window mean rate (kg/s)')
    axes[0].set_title('Input (left) and output + storage (right)')
    axes[0].legend(fontsize=8, ncol=2, loc='upper center', bbox_to_anchor=(.5, -.20))
    inputs = np.r_[0., np.cumsum((h['p72d-total-secondary'][1:] + h['p72d-total-dpm'][1:]) * dt)]
    sink = np.r_[0., np.cumsum(h['p72d-drain-rate'][:-1] * dt)]
    changes = sum(h['p72d-total-' + k] - h['p72d-total-' + k][0] for k in ['mass', 'outflow', 'stripped', 'separated'])
    error = changes + sink - inputs
    axes[1].plot(x, error, color='#0072B2', label='Signed sampled ledger residual')
    axes[1].plot(x, .01 * inputs, color='#888888', ls='--', label='1% of integrated input')
    axes[1].axhline(0, color='k', lw=.5)
    axes[1].axvspan(x[first], x[-1], color='#D55E00', alpha=.13)
    axes[1].set_xlabel('Added native EWF time (ms)')
    axes[1].set_ylabel('Cumulative mass (kg)')
    axes[1].set_title('Film accounting; user sink added once')
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(axis='y', alpha=.2)
    fig.savefig(figs / 'film-balance.png', dpi=180)
    plt.close(fig)
    provenance_path = figs / 'provenance.json'
    provenance = json.loads(provenance_path.read_text())
    provenance['recovered_figures'] = {name: {
        'source': str((OUT / 'analysis-summary.json').relative_to(ROOT)),
        'script': str(Path(__file__).resolve().relative_to(ROOT)),
        'raw_source_sha256': hashes, 'native_window': [41483, 68483],
        'time_basis': result['time_verification'],
        'failure_tail_retained': True, 'visual_qa': 'PENDING'}
        for name in ['film-development.png', 'film-balance.png']}
    dump(provenance_path, provenance)
    print(json.dumps({k: result[k] for k in ['status', 'added_native_film_time_s', 'film_final_kg',
        'first_courant_crossing_iteration', 'lower_peak_courant', 'peak_film_speed_m_s', 'full_run_ledger',
        'pre_guard_last_15ms', 'inner_residual_history']}, indent=2))


if __name__ == '__main__':
    main()
