"""Reconstruct Phase 10 failure history from immutable native text copies.

No Fluent connection or solver writes. This is a diagnostic, not qualification.
"""
import csv
import hashlib
import json
import math
import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'PyAnsys/output/phase10-single-inlet-mesh-convergence'
DEST = OUT / 'divergence-diagnosis-20261011'
RAW = DEST / 'raw'
LEVELS = ['M01', 'M02', 'M03', 'M04']
FAILED = dict(zip(LEVELS, [1756, 4488, 2769, 3911]))
EQUATIONS = ['continuity', 'x-velocity', 'y-velocity', 'z-velocity', 'k', 'epsilon', 'vf-phase-2']
RESIDUAL_COLORS = ['#46D2BA', '#A199D9', '#FA1900', '#2C8ED2', '#FC8500', '#8BDD00', '#FB9DCD']
COLORS = dict(zip(LEVELS + ['M05-current'], ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#777777']))


def read_report(path):
    rows = {}
    for line in path.read_text().splitlines():
        try:
            parts = [float(x) for x in line.split()]
        except ValueError:
            continue
        if len(parts) != 2:
            continue
        iteration, value = parts
        assert iteration.is_integer() and math.isfinite(value), path
        assert int(iteration) not in rows, 'Duplicate native report coordinate'
        rows[int(iteration)] = value
    assert rows, path
    assert list(rows) == sorted(rows), 'Reversed native report coordinate'
    return rows


def read_transcripts(folder):
    residuals, warnings, files = {}, [], []
    for path in sorted(folder.glob('*.trn'), key=lambda p: int(re.search(r'N(\d+)', p.name)[1])):
        text = path.read_text()
        last = None
        files.append({'file': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'floating_point_exception': 'floating point exception' in text})
        for number, line in enumerate(text.splitlines(), 1):
            parts = line.split()
            if len(parts) >= 9 and parts[0].isdigit():
                try:
                    values = [float(x) for x in parts[1:8]]
                except ValueError:
                    continue
                if not all(math.isfinite(x) for x in values):
                    continue
                last = int(parts[0])
                if last in residuals:
                    assert residuals[last] == values, 'Conflicting transcript overlap'
                residuals[last] = values
            kind = None
            if 'Divergence detected in AMG solver:' in line:
                kind = 'AMG_DIVERGENCE'
            elif 'turbulent viscosity limited' in line:
                kind = 'TURBULENT_VISCOSITY_LIMIT'
            elif 'Reversed flow on' in line:
                kind = 'REVERSED_OUTLET_FLOW'
            elif 'floating point exception' in line:
                kind = 'FLOATING_POINT_EXCEPTION'
            if kind:
                warnings.append({'file': str(path.relative_to(ROOT)), 'line': number,
                                 'after_printed_iteration': last, 'kind': kind, 'text': line.strip()})
    return residuals, warnings, files


def main():
    manifests = json.loads((OUT / 'restart-native-manifests-60569-20261010.json').read_text())['levels']
    qualities = list(csv.DictReader((ROOT / 'PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/mesh-quality-summary.csv').open()))
    settings = manifests['M01']['settings_readback']
    parity = {level: manifests[level]['settings_readback'] == settings for level in LEVELS}
    assert all(parity.values()), 'Scientific settings mismatch'
    assert settings['solver']['time'] == 'steady'
    assert list(settings['outlet']) == ['steamoutlet']
    assert settings['bottom']['phase']['mixture']['momentum']['shear_condition'] == 'No Slip'
    liquid_in = settings['inlet']['inlet']['phase']['phase-2']['momentum']['mass_flow_rate']['value']
    vapor_in = settings['inlet']['inlet']['phase']['phase-1']['momentum']['mass_flow_rate']['value']
    liquid_rho = settings['materials']['fluid']['water-liquid-at-psep']['density']['value']
    vapor_rho = settings['materials']['fluid']['water-vapor-at-psep']['density']['value']
    inventory, summary, provenance = {}, {}, []
    all_reports, all_residuals = [], []
    all_warnings = []
    for index, level in enumerate(LEVELS + ['M05-current']):
        folder = RAW / level
        reports = {f.stem: read_report(f) for f in folder.glob('*.out')}
        residuals, warnings, files = read_transcripts(folder)
        assert residuals, 'No residual transcript'
        severe = next((n for n in sorted(residuals) if residuals[n][0] > 10), None)
        speed_severe = next((n for n, v in reports['p10-speed-max'].items() if v > 1000), None)
        cutoffs = [n for n in [severe, speed_severe] if n is not None]
        cutoff = min(cutoffs) if cutoffs else None
        coordinates = sorted(set.intersection(*(set(v) for v in reports.values())))
        assert coordinates, 'No common report coordinates'
        before = [n for n in coordinates if cutoff is None or n < cutoff]
        n = before[-1]
        mass = reports['p10-mass-phase-2']
        outlet = reports['p10-flux-phase-2-steamoutlet']
        first = coordinates[0]
        row = {
            'level': level, 'status': 'NUMERICAL_FAILURE_UNQUALIFIED' if level in FAILED else 'PARTIAL_NO_FPE_IN_COPIED_TRANSCRIPT',
            'actual_failed_iteration': FAILED.get(level), 'last_printed_iteration': max(residuals),
            'report_samples': len(coordinates), 'last_report_iteration': coordinates[-1],
            'first_continuity_residual_above_10': severe,
            'first_sample_max_speed_above_1000_m_s': speed_severe,
            'descriptive_blowup_cutoff': cutoff,
            'comparison_iteration_before_severe_blowup': n,
            'initial_sample_iteration': first, 'initial_sample_liquid_mass_kg': mass[first],
            'liquid_mass_kg': mass[n], 'liquid_outflow_net_kg_s': -outlet[n],
            'liquid_deficit_kg_s': liquid_in + outlet[n],
            'liquid_deficit_percent': 100 * abs(liquid_in + outlet[n]) / liquid_in,
            'mixture_deficit_percent': 100 * abs(liquid_in + vapor_in + reports['p10-flux-mixture-steamoutlet'][n]) / (liquid_in + vapor_in),
            'max_speed_m_s': reports['p10-speed-max'][n],
            'continuity_at_comparison_row': residuals[n][0],
            'first_epsilon_residual_above_1': next((j for j in sorted(residuals) if residuals[j][5] > 1), None),
            'first_k_residual_above_1': next((j for j in sorted(residuals) if residuals[j][4] > 1), None),
            'amg_first_warning': next((w for w in warnings if w['kind'] == 'AMG_DIVERGENCE'), None),
            'floating_point_exception_seen': any(f['floating_point_exception'] for f in files),
            'min_oq': float(qualities[min(index, 4)]['min_oq']),
            'max_size_change': float(qualities[min(index, 4)]['max_size_change']),
        }
        if level in LEVELS:
            assert row['floating_point_exception_seen']
            assert max(residuals) + 1 == FAILED[level], 'Failed horizon conflicts with printed transcript'
            row['last_full_checkpoint'] = max(c['iteration'] for c in manifests[level]['checkpoints'] if c['iteration'] == c['requested_iteration'])
            row['cells'] = manifests[level]['mesh']['cells']
            row['initial_settings_match'] = parity[level]
            volume = float(qualities[index]['volume_m3'])
            row['liquid_mean_volume_fraction'] = mass[n] / liquid_rho / volume
            row['maximum_reported_volume_relative_error'] = max(abs(reports['p10-mass-phase-1'][j] / vapor_rho + mass[j] / liquid_rho - volume) / volume for j in coordinates)
            row['last_500_sample_inventory_change_percent'] = 100 * (mass[n] - mass[next(j for j in before if j >= n - 500)]) / mass[next(j for j in before if j >= n - 500)]
        inventory[level] = {'reports': reports, 'coordinates': coordinates, 'residuals': residuals}
        summary[level] = row
        provenance.extend(files)
        for j in coordinates:
            all_reports.append({'level': level, 'iteration': j, **{k: v[j] for k, v in reports.items()},
                                'before_descriptive_blowup_cutoff': cutoff is None or j < cutoff})
        for j, values in sorted(residuals.items()):
            all_residuals.append({'level': level, 'iteration': j, **dict(zip(EQUATIONS, values))})
        all_warnings.extend(dict(level=level, **w) for w in warnings)

    for name, rows in [('reports.csv', all_reports), ('residuals.csv', all_residuals), ('warnings.csv', all_warnings)]:
        fields = list(dict.fromkeys(k for row in rows for k in row))
        with (DEST / name).open('w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    result = {'status': 'DIAGNOSTIC_NOT_CAUSAL_PROOF', 'levels': summary, 'same_initial_settings': parity,
              'liquid_inlet_kg_s': liquid_in, 'vapor_inlet_kg_s': vapor_in,
              'native_report_sign': 'inlet positive; outward flux negative; outflow plotted as minus outlet report',
              'density_ratio_liquid_to_vapor': liquid_rho / vapor_rho,
              'implicit_body_force': settings['models']['multiphase']['advanced_formulation']['implicit_body_force'],
              'source_manifest': str((OUT / 'restart-native-manifests-60569-20261010.json').relative_to(ROOT)),
              'transcript_provenance': provenance,
              'limitations': ['No physical time in these steady iterations; inventory slope is not kg/s.',
                              'First continuity residual above 10 or sampled max speed above 1000 m/s defines only a descriptive pre-blowup window.',
                              'No spatial location of the first unstable cell and no controlled numerical contrast.',
                              'Report sampling is every ten iterations; residuals are printed every iteration.',
                              'M05 reports and transcript are passive partial snapshots, not a saved endpoint.']}
    (DEST / 'summary.json').write_text(json.dumps(result, indent=2, allow_nan=False))

    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.1), constrained_layout=True)
    for level, data in inventory.items():
        ns = [n for n in data['coordinates'] if n <= summary[level]['comparison_iteration_before_severe_blowup']]
        style = '--' if level == 'M05-current' else '-'
        label = level.replace('-current', ' (partial)')
        axes[0].plot(ns, [data['reports']['p10-mass-phase-2'][n] for n in ns], style, color=COLORS[level], label=label)
        axes[1].plot(ns, [-data['reports']['p10-flux-phase-2-steamoutlet'][n] for n in ns], style, color=COLORS[level])
    axes[1].axhline(liquid_in, color='black', linestyle=':', label=f'Liquid inlet: {liquid_in:.2f} kg/s')
    axes[0].set(ylabel='Liquid held inside (kg)', xlabel='Solver iteration', title='Liquid inventory rises across the family')
    axes[1].set(ylabel='Net liquid flow out (kg/s)', xlabel='Solver iteration', title='Liquid discharge does not settle at the feed')
    axes[0].legend(); axes[1].legend(loc='upper left')
    for ax in axes: ax.grid(alpha=0.2)
    fig.savefig(DEST / 'liquid-balance.png', dpi=170); plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    for ax, level in zip(axes.flat, LEVELS):
        data = inventory[level]; ns = sorted(data['residuals'])
        for k, (eq, color) in enumerate(zip(EQUATIONS, RESIDUAL_COLORS)):
            ax.semilogy(ns, [data['residuals'][n][k] for n in ns], color=color, label=eq, lw=0.85)
        ax.axhline(1e-4, color='black', ls=':', lw=0.7)
        ax.axhline(1e-3, color='grey', ls=':', lw=0.7)
        ax.set(title=f'{level}: FPE at N{FAILED[level]}', xlabel='Solver iteration', ylabel='Printed scaled residual', ylim=(1e-6, 1e2))
        ax.grid(alpha=0.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside upper center', ncol=4, fontsize=9)
    fig.savefig(DEST / 'failure-residuals.png', dpi=170); plt.close(fig)
    print(json.dumps({level: {k: row[k] for k in ['comparison_iteration_before_severe_blowup', 'liquid_mass_kg', 'liquid_outflow_net_kg_s', 'liquid_deficit_percent', 'first_continuity_residual_above_10', 'last_printed_iteration']} for level, row in summary.items()}, indent=2))


if __name__ == '__main__':
    main()
