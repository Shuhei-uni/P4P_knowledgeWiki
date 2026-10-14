"""Compare mass-based assumed-capture efficiency with historical spiral tet."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'PyAnsys/scripts/analysis'))
from analyze_phase10_replication1600_dpm import audit_report, TERMINAL

OUT = ROOT / 'PyAnsys/output/phase10-single-inlet-mesh-convergence'
DEST = OUT / 'replication-enthalpy-M04'


def main():
    spec = json.loads((DEST / 'job-spec.json').read_text())
    rows = []
    for item in spec['cases']:
        h = item['enthalpy_kJ_kg']
        folder = DEST / ('H' + str(h))
        if not (folder / 'raw/manifest.json').exists():
            continue
        manifest_path = folder / ('verified-manifest.json' if (folder / 'verified-manifest.json').exists() else 'raw/manifest.json')
        manifest = json.loads(manifest_path.read_text())
        if manifest['status'] != 'COMPLETE_EVIDENCE_VERIFIED_UNQUALIFIED':
            continue
        assert manifest['solved_updates'] == manifest['completed_iteration'] == 1500
        assert manifest['DPM_completed_updates'] == manifest['DPM_update_dispatches'] == 1
        assert manifest['strict_reopen_verified'] and manifest['transcript_closed']
        assert manifest['carrier_reports_unchanged']
        assert manifest['settings_readback'] == item['settings']
        mass = audit_report((folder / 'raw/DPM-aggregate.txt').read_text(), item['liquid_kg_s'])
        inject = {name: audit_report((folder / 'raw' / ('DPM-' + name + '.txt')).read_text(),
            values['initial_values']['mass_flow_rate']['total_flow_rate'])
            for name, values in item['settings']['models']['discrete_phase']['injections'].items()}
        tolerance = mass['printed_roundoff_bound_kg_s'] + sum(v['printed_roundoff_bound_kg_s'] for v in inject.values())
        for fate in TERMINAL:
            assert abs(sum(v['final_mass_kg_s'][fate] for v in inject.values()) - mass['final_mass_kg_s'][fate]) <= tolerance
        assert sum(v['tracked_count'] for v in inject.values()) == mass['tracked_count']
        (folder / 'summary.json').write_text(json.dumps({'aggregate': mass, 'injections': inject,
            'source_manifest': str(folder / 'raw/manifest.json'), 'efficiency_assumption': spec['incomplete_assumption']}, indent=2) + '\n')
        current = mass['final_mass_kg_s']
        old = item['historical_summary']
        rows.append(dict(enthalpy_kJ_kg=h, injected_kg_s=item['liquid_kg_s'],
            M04_escaped_kg_s=current['escaped'], M04_trapped_kg_s=current['trapped'],
            M04_incomplete_kg_s=current['incomplete'],
            M04_efficiency_percent=100 * (1 - current['escaped'] / item['liquid_kg_s']),
            tet_escaped_kg_s=float(old['escaped_kgs']), tet_trapped_kg_s=float(old['trapped_kgs']),
            tet_incomplete_kg_s=float(old['incomplete_kgs']),
            tet_efficiency_percent=100 * (1 - float(old['escaped_kgs']) / item['liquid_kg_s'])))
    case4 = json.loads((OUT / 'replication1600-M04/DPM-limit100000-evidence/summary.json').read_text())
    mass = case4['aggregate']['final_mass_kg_s']
    old = case4['historical_rounded_mass_kg_s']
    rows.append(dict(enthalpy_kJ_kg=1600, injected_kg_s=116.92,
        M04_escaped_kg_s=mass['escaped'], M04_trapped_kg_s=mass['trapped'], M04_incomplete_kg_s=mass['incomplete'],
        M04_efficiency_percent=100 * (1 - mass['escaped'] / 116.92),
        tet_escaped_kg_s=old['escaped'], tet_trapped_kg_s=old['trapped'], tet_incomplete_kg_s=old['incomplete'],
        tet_efficiency_percent=100 * (1 - old['escaped'] / 116.92)))
    rows.sort(key=lambda row: row['enthalpy_kJ_kg'])
    for row in rows:
        row['difference_percentage_points'] = row['M04_efficiency_percent'] - row['tet_efficiency_percent']
    with (DEST / 'efficiency-comparison.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {'status': 'COMPLETE_COMPARISON' if len(rows) == 5 else 'PARTIAL_COMPARISON',
        'incomplete_assumption': spec['incomplete_assumption'], 'tracking_max_num_steps': 100000,
        'rows': rows, 'carrier_qualified': False,
        'limits': ['Current M04 uses 100000 steps; original July tracking cap unverified.',
                   'Historical mass values use their reported precision.',
                   'Fixed horizons and assumed capture do not prove mesh independence or physical validation.']}
    (DEST / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout='constrained')
    h = [r['enthalpy_kJ_kg'] for r in rows]
    for key, label, color in [('tet', 'Historical tet', '#858f99'), ('M04', 'M04', '#286e9d')]:
        axes[0].plot(h, [r[key + '_efficiency_percent'] for r in rows], 'o-', label=label, color=color)
        axes[1].plot(h, [100 * r[key + '_incomplete_kg_s'] / r['injected_kg_s'] for r in rows], 'o-', label=label, color=color)
    axes[0].set_ylabel('Efficiency: incomplete assumed separated (%)')
    axes[1].set_ylabel('Incomplete liquid mass (%)')
    for ax in axes:
        ax.set_xlabel('Inlet enthalpy (kJ/kg)')
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(alpha=.25)
        ax.legend(frameon=False)
    fig.suptitle('Spiral full-flow N1500 comparison: reconstructed M04 settings')
    fig.savefig(DEST / 'efficiency-comparison.png', dpi=170)
    plt.close(fig)
    print(json.dumps({'status': summary['status'], 'enthalpies': h}))


if __name__ == '__main__':
    main()
