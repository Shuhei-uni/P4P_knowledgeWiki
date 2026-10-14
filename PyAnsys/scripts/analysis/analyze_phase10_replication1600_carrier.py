"""File-backed N1500 carrier evidence; no DPM or exact-replication claims."""
from pathlib import Path
import csv
import hashlib
import json
import math
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/carrier-evidence'
RAW = DEST / 'raw'
EQ = ['continuity', 'x-velocity', 'y-velocity', 'z-velocity', 'k', 'epsilon', 'vf-phase-2']
COLORS = ['#46D2BA', '#A199D9', '#FA1900', '#2C8ED2', '#FC8500', '#8BDD00', '#FB9DCD']


def history(path):
    result = {}
    for line in path.read_text().splitlines():
        try:
            row = [float(v) for v in line.split()]
        except ValueError:
            continue
        if len(row) != 2:
            continue
        n, value = row
        assert n.is_integer() and math.isfinite(value)
        assert int(n) not in result
        result[int(n)] = value
    assert list(result) == list(range(10, 1501, 10))
    return result


def main():
    manifest = json.loads((RAW / 'manifest.json').read_text())
    proof = json.loads((DEST / 'terminal-proof.json').read_text())
    assert manifest['solved_updates'] == manifest['completed_iteration'] == 1500
    assert proof['controller_exited'] and proof['live']['idle']
    assert len(proof['checkpoint_pairs']) == 8
    reports = {name: history(RAW / 'monitors' / (name + '.out')) for name in manifest['report_paths']}
    residuals = {}
    overlaps = []
    native_failure = []
    for name in ['smoke-to-N1.trn', 'carrier-to-N1001.trn', 'carrier-to-N1500.trn']:
        text = (RAW / name).read_text()
        for pattern in ['floating point exception', 'divergence detected in amg solver']:
            if pattern in text.lower():
                native_failure.append((name, pattern))
        for line in text.splitlines():
            tokens = line.split()
            if len(tokens) < 9 or not tokens[0].isdigit():
                continue
            try:
                values = [float(v) for v in tokens[1:8]]
            except ValueError:
                continue
            n = int(tokens[0])
            assert all(math.isfinite(v) for v in values)
            if n < 1:
                continue
            if n in residuals:
                assert residuals[n] == values, 'Changed overlap at N%d' % n
                overlaps.append({'iteration': n, 'file': name, 'values_identical': True})
            residuals[n] = values
    assert sorted(residuals) == list(range(1, 1501))
    assert not native_failure
    window = list(range(1010, 1501, 10))
    summary = {'status': 'CARRIER_COMPLETE_DPM_PENDING_UNQUALIFIED', 'mesh': 'M04', 'cells': 946967,
        'carrier_updates': 1500, 'qualification': False, 'DPM_tracking_issued': False,
        'historical_full_settings_parity_verified': False, 'report_sample_count': 150,
        'final_500_updates': [1001, 1500], 'final_500_report_samples': len(window),
        'residual_rows': len(residuals), 'identical_residual_overlaps_removed': overlaps,
        'controller_exited': True, 'live_settings_match': proof['live']['strict_carrier_settings_match'],
        'native_fatal_numerical_errors': native_failure, 'final_pair': manifest['final_pair'],
        'all_pairs_rehashed': True, 'native_source_identity_normalization': 'CRLF to LF only; both hashes retained',
        'campaign_spend_lower_bound': 22869 + 1500, 'campaign_spend_upper_bound': 23559 + 1500,
        'campaign_remaining_lower_bound': 35000 - 23559 - 1500,
        'solver_seconds': sum(c.get('solver_seconds', 0) for c in manifest['checkpoints']),
        'histories': {}, 'phase_closure': {}, 'residuals_final_500': {}}
    for name, rows in reports.items():
        values = [rows[n] for n in window]
        mean = sum(values) / len(values)
        summary['histories'][name] = {'mean': mean, 'minimum': min(values), 'maximum': max(values),
            'relative_range_percent': 100 * (max(values) - min(values)) / abs(mean) if abs(mean) > 1e-12 else None,
            'at_N1000': rows[1000], 'at_N1500': rows[1500]}
    for phase in ['mixture', 'phase-1', 'phase-2']:
        inlet = reports['p10-flux-' + phase + '-inlet']
        outlet = reports['p10-flux-' + phase + '-steamoutlet']
        errors = [100 * abs(inlet[n] + outlet[n]) / abs(inlet[n]) for n in window]
        summary['phase_closure'][phase] = {'mean_absolute_error_percent_of_inlet': sum(errors)/len(errors),
            'maximum_error_percent_of_inlet': max(errors), 'passes_1_percent': max(errors) <= 1}
    liquid = reports['p10-mass-phase-2']
    delta = 100 * (liquid[1500] - liquid[1000]) / liquid[1000]
    summary['liquid_inventory'] = {'N1000_kg': liquid[1000], 'N1500_kg': liquid[1500],
        'change_percent_N1000_to_N1500': delta, 'passes_1_percent': abs(delta) <= 1}
    for i, eq in enumerate(EQ):
        values = [residuals[n][i] for n in range(1001, 1501)]
        criterion = 1e-4 if eq == 'continuity' else 1e-3
        summary['residuals_final_500'][eq] = {'minimum': min(values), 'maximum': max(values),
            'at_N1500': values[-1], 'criterion': criterion, 'all_below_criterion': max(values) <= criterion}
    summary['interpretation_status'] = 'CONSEQUENTIAL_INTERPRETATION_RESERVED_FOR_ASTRA_PLANNER'
    (DEST / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    with (DEST / 'residual-history.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['iteration', *EQ])
        for n in sorted(residuals):
            w.writerow([n, *residuals[n]])
    fig, axes = plt.subplots(3, 1, figsize=(8.8, 8.0), sharex=True, constrained_layout=True)
    ns = sorted(residuals)
    for i, (eq, color) in enumerate(zip(EQ, COLORS)):
        axes[0].semilogy(ns, [max(residuals[n][i], 1e-20) for n in ns], label=eq, color=color, linewidth=0.8)
    axes[0].set_ylabel('Scaled residual'); axes[0].legend(ncol=4, fontsize=8)
    nr = sorted(liquid)
    axes[1].plot(nr, [liquid[n] for n in nr], color='#2C8ED2')
    axes[1].set_ylabel('Liquid inventory (kg)')
    for phase, color in [('phase-1', '#FC8500'), ('phase-2', '#2C8ED2')]:
        inlet = reports['p10-flux-' + phase + '-inlet']; outlet = reports['p10-flux-' + phase + '-steamoutlet']
        axes[2].plot(nr, [100*abs(inlet[n]+outlet[n])/abs(inlet[n]) for n in nr], color=color, label=phase)
    axes[2].axhline(1, color='black', linestyle='--', linewidth=0.8, label='1% criterion')
    axes[2].set_ylabel('Absolute closure error (%)'); axes[2].set_xlabel('Native carrier iteration'); axes[2].legend(fontsize=8)
    for ax in axes:
        ax.axvspan(1000, 1500, color='grey', alpha=0.08); ax.grid(alpha=0.2)
    fig.suptitle('M04, 1600 kJ/kg: provisional carrier stage — DPM not tracked')
    fig.savefig(DEST / 'carrier-evidence.png', dpi=160)
    plt.close(fig)
    print(json.dumps({'updates': 1500, 'residual_rows': len(residuals), 'phase_closure': summary['phase_closure'],
        'liquid_inventory': summary['liquid_inventory'], 'N1500_continuity': residuals[1500][0],
        'solver_minutes': summary['solver_seconds']/60}))


if __name__ == '__main__':
    main()
