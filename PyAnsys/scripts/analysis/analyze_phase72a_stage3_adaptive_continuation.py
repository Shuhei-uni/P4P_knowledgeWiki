"""Reduce the bounded N6000-N8000 adaptive contrast; plot measured histories."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/phase72a-stage3-server3/20261005/adaptive-aggressive-N6000-N8000'
PROJECT = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction'


def main():
    read = lambda name: json.loads((OUT / name).read_text())
    manifest = read('run-manifest.json')
    assert manifest['status'] == 'COMPLETE' and manifest['verified_native_end'] == 8000
    parent = read('parent-state.json')
    end = read('endpoint-N8000.json')
    histories = read('report-histories.json')
    ids = np.arange(6001, 8001)
    h = {}
    for name, record in histories.items():
        assert record['iterations'] in [ids.tolist(), np.arange(6000, 8001).tolist()], name
        selected = dict(zip(record['iterations'], record['values']))
        h[name] = np.asarray([selected[int(i)] for i in ids])
        assert np.isfinite(h[name]).all(), name
    clocks, residuals = {}, {}
    for start, stop in [(6000, 6020), (6020, 7000), (7000, 8000)]:
        c = read(f'clocks-N{start}-N{stop}.json')
        assert set(map(int, c)) == set(range(start + 1, stop + 1))
        clocks.update({int(k): v for k, v in c.items()})
        residuals.update({int(k): v for k, v in read(f'residuals-N{start}-N{stop}.json').items()})
    assert len(clocks) == 2000
    t = np.array([clocks[int(i)][0] for i in ids])
    steps = np.array([clocks[int(i)][1] for i in ids])
    cfl = np.array([clocks[int(i)][2] for i in ids])
    assert np.all(np.diff(t) > 0)
    assert abs(t[-1] - end['film_solution_state']['film_elapsed_time']) < 5.1e-8
    f0 = parent['state']['readback']['fields']
    fe = end['state']['readback']['fields']
    for name in ['v2-flux-phase2-liquidinlet', 'v2-flux-phase2-steamoutlet']:
        assert np.isclose(h[name][-1], fe[name + '(without-sources)'][0], atol=1e-7)
    assert np.max(abs(h['p72-contact-removal'] + h['v2-applied-absorber'])) < 1e-7
    mass = h['p72a-e2.7-ewf-film-mass-total']
    gain = mass[-1] - f0['p72a-e2.7-ewf-film-mass-total'][0]
    drain = h['p72a-e2.7-ewf-outflow-mass-total'][-1] - f0['p72a-e2.7-ewf-outflow-mass-total'][0]
    integrated = sum(b['integrated_accretion_kg'] for b in manifest['blocks'])
    ref = json.loads((OUT.parent / 'analysis-summary.json').read_text())['reference']
    metrics = {'pressure_drop_Pa': h['p72s3-pressure-inlet'] - h['p72s3-pressure-outlet'],
               'vapor_outlet_kg_s': -h['v2-flux-phase1-steamoutlet'],
               'liquid_carryover_kg_s': -h['v2-flux-phase2-steamoutlet'],
               'bulk_inventory_kg': h['v2-total-liquid-mass']}
    summary = {'native_window': [6000, 8000], 'updates': 2000,
        'report_count': len(h), 'report_rows_each': 2000,
        'initial_film_clock_s': parent['film_solution_state']['film_elapsed_time'],
        'final_film_clock_s': end['film_solution_state']['film_elapsed_time'],
        'added_film_time_s': manifest['total_added_film_time_s'],
        'film_time_advance_ratio_to_2000_at_1us': manifest['total_added_film_time_s'] / .002,
        'printed_step_range_s': [float(steps.min()), float(steps.max())],
        'exact_native_final_step_s': end['film_solution_state']['film_timestep'],
        'peak_film_cfl': float(cfl.max()), 'final_film_cfl': float(cfl[-1]),
        'film_inventory_start_kg': f0['p72a-e2.7-ewf-film-mass-total'][0],
        'film_inventory_end_kg': float(mass[-1]),
        'film_inventory_percent_of_reference': float(100 * mass[-1] / ref['film_mass_kg']),
        'maximum_thickness_end_m': float(h['p72a-e2.7-ewf-thickness-max'][-1]),
        'maximum_thickness_peak_m': float(h['p72a-e2.7-ewf-thickness-max'].max()),
        'inventory_gain_kg': float(gain), 'drained_mass_kg': float(drain),
        'integrated_accretion_kg': float(integrated),
        'film_ledger_error_percent': float(100 * abs(gain + drain - integrated) / integrated),
        'final_500_carrier': {k: {'mean': float(v[-500:].mean()), 'std': float(v[-500:].std()),
             'difference_from_reference_percent': float(100 * (v[-500:].mean() / ref[k] - 1))} for k, v in metrics.items()},
        'final_500_continuity_mean': float(np.mean([v[0] for i, v in residuals.items() if i > 7500])),
        'residual_rows': len(residuals),
        'contact_removal_final_500_mean_kg_s': float(h['p72-contact-removal'][-500:].mean()),
        'contact_removal_final_500_std_kg_s': float(h['p72-contact-removal'][-500:].std()),
        'bulk_inventory_start_kg': f0['v2-total-liquid-mass'][0],
        'bulk_inventory_end_kg': float(h['v2-total-liquid-mass'][-1]),
        'final_reopen': manifest['final_reopen'], 'idle': manifest['idle'],
        'claim_limits': ['Film developing; reference snapshot not stationary',
                         'Film-time advancement ratio is not measured wall-clock speedup',
                         'Whole-separator accounting and steady convergence remain unqualified']}
    (OUT / 'analysis-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')
    ax = axes[0, 0]
    ax.plot(ids, steps * 1e6, color='#276b9d', label='Accepted step')
    ax.axhline(1, color='#777777', linestyle='--', label='Previous 1 µs step')
    ax.set_ylabel('Printed film step (µs)');ax.set_xlabel('Native iteration')
    ax.legend(loc='upper left', fontsize=8)
    twin = ax.twinx();twin.plot(ids, cfl, color='#b87520', alpha=.8)
    twin.axhline(.15, color='#b87520', linestyle=':', linewidth=1)
    twin.set_ylabel('Film Courant number', color='#b87520')
    axes[0, 1].plot(t * 1000, mass, color='#276b9d')
    axes[0, 1].set_xlabel('Total film time since dry startup (ms)')
    axes[0, 1].set_ylabel('Film inventory (kg)')
    axes[0, 1].set_title(f"Final inventory: {summary['film_inventory_percent_of_reference']:.1f}% of developed reference")
    ni = np.array(sorted(residuals));cv = np.array([residuals[int(i)][0] for i in ni])
    axes[1, 0].plot(ni, cv, color='#276b9d', alpha=.7, linewidth=.8)
    axes[1, 0].axhline(.0888, color='#777777', linestyle='--', label='N6000 late mean')
    axes[1, 0].set_ylabel('Scaled continuity residual');axes[1, 0].set_xlabel('Native iteration')
    axes[1, 0].legend(fontsize=8)
    axes[1, 1].plot(ids, metrics['liquid_carryover_kg_s'], color='#276b9d', alpha=.7, linewidth=.8)
    axes[1, 1].axhline(ref['liquid_carryover_kg_s'], color='#777777', linestyle='--', label='Developed reference snapshot')
    axes[1, 1].set_ylabel('Liquid carryover (kg/s)');axes[1, 1].set_xlabel('Native iteration')
    axes[1, 1].legend(fontsize=8)
    for ax in axes.flat: ax.grid(alpha=.2)
    fig.suptitle('Server 3: adaptive EWF continuation, N6000–N8000')
    figure = PROJECT / 'figures/adaptive-aggressive-N6000-N8000.png'
    fig.savefig(figure, dpi=180);plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
