"""Reduce the Stage 3 startup screens without promoting them to stationarity."""
from pathlib import Path
import json
import re
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from run_phase72a_adaptive_film import film_records
OUT = ROOT / 'output/phase72a-stage3-server3/20261005'
PROJECT = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction'
FIG = PROJECT / 'figures'


def load(name):
    return json.loads((OUT / name).read_text())


def array(histories, name):
    record = histories[name]
    return np.asarray(record['iterations']), np.asarray(record['values'])


def film(arm):
    h = load(f'{arm}-histories.json')
    clocks = film_records((OUT / f'{arm}-film-transcript.txt').read_text())
    ids = np.array(sorted(clocks))
    if len(ids) != 3000 or not np.all(np.diff(ids) == 1):
        raise RuntimeError(f'{arm}: film clock does not cover all 3000 requested updates')
    t = np.array([clocks[int(i)][0] for i in ids])
    printed_step = np.array([clocks[int(i)][1] for i in ids])
    initial = t[0] - printed_step[0]
    dt = np.diff(np.r_[initial, t])
    if np.any(dt <= 0):
        raise RuntimeError('Non-increasing native film clock')
    def values(name):
        x, y = array(h, name)
        mapping = dict(zip(x, y))
        if not set(ids).issubset(mapping) or ids[0] - 1 not in mapping:
            raise RuntimeError(f'Missing film history {name}')
        return np.r_[mapping[ids[0] - 1], [mapping[i] for i in ids]]
    mass = values('p72a-e2.7-ewf-film-mass-total')
    drain = values('p72a-e2.7-ewf-outflow-mass-total')
    acc = values('p72a-e2.7-ewf-secondary-phase-mass-total')
    integrated = np.r_[0, np.cumsum(acc[1:] * dt)]
    gain = mass - mass[0]
    discharged = drain - drain[0]
    ledger = gain + discharged - integrated
    time = np.r_[0, t - initial]
    info = {'film_elapsed_s': float(time[-1]), 'native_updates': len(ids),
            'initial_native_clock_s': float(initial), 'native_end': int(ids[-1]),
            'film_mass_start_kg': float(mass[0]), 'film_mass_end_kg': float(mass[-1]),
            'inventory_gain_kg': float(gain[-1]), 'drained_mass_kg': float(discharged[-1]),
            'integrated_accretion_kg': float(integrated[-1]),
            'film_ledger_error_percent': float(100 * abs(ledger[-1]) / max(abs(integrated[-1]), 1e-30)),
            'accepted_step_min_s': float(dt.min()), 'accepted_step_max_s': float(dt.max()),
            'peak_film_cfl': float(max(v[2] for v in clocks.values())),
            'time_basis': 'Native film clock differences; first step uses native printed initial step'}
    return h, time, mass, discharged, integrated, printed_step, ids, info


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    manifest = load('run-manifest.json')
    if manifest['status'] != 'STARTUP_SCREENS_COMPLETE_ANALYSIS_REQUIRED':
        raise RuntimeError('Both verified screens are required before final analysis')
    reference = load('reference-state.json')['readback']['fields']
    reference_extra = load('reference-extra-reports.json')
    ref_dp = reference_extra['p72s3-pressure-inlet'][0] - reference_extra['p72s3-pressure-outlet'][0]
    bulk = load('bulk-histories.json')
    fig, ax = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    for name in ['v2-flux-phase2-liquidinlet', 'v2-flux-phase1-steaminlet', 'p72-contact-removal']:
        x, y = array(bulk, name)
        ax[0].plot(x, y, label=name.replace('v2-flux-', '').replace('p72-contact-', 'contact '), lw=.9)
    x, y = array(bulk, 'v2-total-liquid-mass')
    ax[1].plot(x, y, lw=.9)
    ax[1].axhline(reference['v2-total-liquid-mass'][0], ls='--', color='k', label='Developed reference snapshot')
    x, pi = array(bulk, 'p72s3-pressure-inlet'); xo, po = array(bulk, 'p72s3-pressure-outlet')
    if not np.array_equal(x, xo):
        raise RuntimeError('Pressure histories have different coordinates')
    ax[2].plot(x, (pi - po) / 1000, lw=.9)
    ax[2].axhline(ref_dp / 1000, ls='--', color='k')
    for a, title, unit in zip(ax, ['Feed/source development; native source-inclusive liquid flux', 'Bulk liquid inventory', 'Area-mean inlet minus outlet pressure'], ['kg/s', 'kg', 'kPa']):
        a.set_title(title); a.set_ylabel(unit); a.grid(alpha=.2)
    ax[0].legend(fontsize=8); ax[1].legend(fontsize=8); ax[2].set_xlabel('Native bulk iteration')
    fig.tight_layout(); fig.savefig(FIG / 'bulk-startup.png', dpi=180); plt.close(fig)
    arms = {arm: film(arm) for arm in ['fixed', 'adaptive']}
    fig, ax = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    summary = {'status': 'SCREEN_COMPLETE_REPRODUCTION_NOT_YET_QUALIFIED', 'reference_basis': 'N33586 developed snapshot; no stationary reference window', 'arms': {}}
    common_time = min(arms['fixed'][1][-1], arms['adaptive'][1][-1])
    for arm, (h, time, mass, drain, acc, steps, ids, info) in arms.items():
        ax[0].plot(time, mass, label=arm, lw=1)
        ax[1].plot(time, drain, label=f'{arm} drainage', lw=1)
        ax[1].plot(time, acc, label=f'{arm} accretion', lw=1, ls='--')
        ax[2].plot(time, mass - mass[0] + drain - acc, label=arm, lw=1)
        info['film_mass_at_common_time_kg'] = float(np.interp(common_time, time, mass))
        info['common_time_s'] = float(common_time)
        final = load(f'{arm}-endpoint-N{ids[-1]}.json')['state']['readback']['fields']
        # Compare final window to the exact preserved snapshot. Native flux
        # subreports at the endpoint check the user-source subtraction first.
        source = final['v2-applied-absorber'][0]
        for report in ['v2-flux-phase2-liquidinlet', 'v2-flux-phase2-steamoutlet']:
            if not np.isclose(final[report][0] - source, final[report + '(without-sources)'][0], rtol=1e-8, atol=1e-7):
                raise RuntimeError('Native mass-flow subreports do not support source subtraction')
        _, native_out = array(h, 'v2-flux-phase2-steamoutlet')
        _, user_source = array(h, 'v2-applied-absorber')
        carry = -(native_out - user_source)
        _, vapor = array(h, 'v2-flux-phase1-steamoutlet')
        _, inventory = array(h, 'v2-total-liquid-mass')
        _, p_in = array(h, 'p72s3-pressure-inlet'); _, p_out = array(h, 'p72s3-pressure-outlet')
        comparisons = {}
        for name, vals, ref, tolerance in [
                ('liquid_carryover_kg_s', carry, -reference['v2-flux-phase2-steamoutlet(without-sources)'][0], 10),
                ('vapor_outlet_kg_s', -vapor, -reference['v2-flux-phase1-steamoutlet'][0], 5),
                ('bulk_inventory_kg', inventory, reference['v2-total-liquid-mass'][0], 10),
                ('pressure_drop_Pa', p_in - p_out, ref_dp, 5)]:
            mean = float(np.mean(vals[-500:])); error = float(100 * (mean - ref) / abs(ref)) if ref else None
            comparisons[name] = {'final_500_mean': mean, 'reference_snapshot': ref, 'difference_percent': error,
                                 'screen_tolerance_percent': tolerance, 'scalar_screen_pass': error is not None and abs(error) <= tolerance}
        info['comparisons'] = comparisons
        info['wall_seconds'] = sum(b['wall_seconds'] for b in manifest['blocks'] if b.get('arm') == arm)
        summary['arms'][arm] = info
    for a, title, unit in zip(ax, ['Film development from the same dry-film parent', 'Cumulative drainage and integrated accretion', 'Film ledger: storage + drainage − accretion'], ['kg', 'kg', 'kg']):
        a.set_title(title); a.set_ylabel(unit); a.grid(alpha=.2); a.legend(fontsize=8)
    ax[0].axhline(reference['p72a-e2.7-ewf-film-mass-total'][0], color='k', ls=':', label='Developed reference')
    ax[-1].set_xlabel('Elapsed native film time (s)')
    fig.tight_layout(); fig.savefig(FIG / 'film-matched-time.png', dpi=180); plt.close(fig)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for arm, (_, time, _, _, _, steps, ids, info) in arms.items():
        ax[0].plot(time[1:], steps * 1e6, label=arm)
        ax[1].plot(np.arange(1, len(ids) + 1), time[1:], label=arm)
    ax[0].set(xlabel='Elapsed film time (s)', ylabel='Printed accepted step (µs)')
    ax[1].set(xlabel='Film updates', ylabel='Elapsed film time (s)')
    for a in ax: a.legend(); a.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(FIG / 'accepted-film-steps.png', dpi=180); plt.close(fig)
    cases = ['reference', 'fixed', 'adaptive']
    data = {case: np.load(OUT / f'{case}-p72s3-xy-z0.npz') for case in cases}
    fig, ax = plt.subplots(2, 3, figsize=(12, 10))
    for row, field in enumerate(['phase-2-vof', 'velocity-magnitude']):
        vmax = max(float(d[field].max()) for d in data.values())
        for col, case in enumerate(cases):
            d = data[case]; split = np.cumsum(d['face_sizes'])[:-1]
            faces = np.split(d['connectivity'], split)
            polygons = [d['vertices'][face, :2] for face in faces]
            p = PolyCollection(polygons, array=d[field], cmap='viridis', clim=(0, vmax), edgecolors='none')
            ax[row, col].add_collection(p); ax[row, col].autoscale_view(); ax[row, col].set_aspect('equal')
            ax[row, col].set_title(f'{case}: {field}'); ax[row, col].set_xlabel('x (m)'); ax[row, col].set_ylabel('y (m)')
            fig.colorbar(p, ax=ax[row, col], shrink=.65)
    fig.tight_layout(); fig.savefig(FIG / 'matched-spatial-fields.png', dpi=180); plt.close(fig)
    summary['bulk_wall_seconds'] = manifest['bulk_wall_seconds'] + manifest.get('smoke', {}).get('wall_seconds', 0)
    summary['claim_limits'] = ['3000 film updates per arm are startup screens', 'Developed reference is not stationary',
                              'No mesh-family extension selected', 'No physical validation', 'Matched-time endpoint values are interpolated from native histories']
    (OUT / 'analysis-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    rows = []
    for arm, info in summary['arms'].items():
        rows.append(f"| {arm} | {info['film_elapsed_s']:.6g} | {info['wall_seconds']/60:.2f} | {info['film_mass_end_kg']:.6g} | {info['film_ledger_error_percent']:.4g} |")
    text = '\n'.join([
        '# Stage 3 — Shortened reconstruction result', '',
        '| Item | Result |', '| --- | --- |',
        '| Execution | 3000 bulk startup updates; 3000 fixed and 3000 adaptive film updates; paired endpoints reopened |',
        '| Reproduction | Scalar startup comparison completed; stationarity and full reproduction remain unqualified |',
        f"| Bulk startup cost | {summary['bulk_wall_seconds']/60:.2f} min; timing includes the smoke verification cost |",
        '| Reference | Preserved corrected R3/contact N33586; developed, not steady-qualified |',
        '| Controls and decision rules | [Setup](setup.md) |',
        '| Machine evidence | [Analysis summary](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/analysis-summary.json) |', '',
        '![Bulk startup](figures/bulk-startup.png)', '',
        'Native report histories; the dotted reference is a preserved snapshot.', '',
        '| Film arm | Native film time (s) | Solve cost (min) | Final film mass (kg) | Film ledger error (%) |',
        '| --- | ---: | ---: | ---: | ---: |', *rows, '',
        '![Matched elapsed film time](figures/film-matched-time.png)', '',
        'Inventories and transfers use native film clocks. Fixed/adaptive agreement must be judged within their common time interval.', '',
        '![Accepted film steps](figures/accepted-film-steps.png)', '',
        '![Same-plane spatial comparison](figures/matched-spatial-fields.png)', '',
        'Native facet values on Z=0; each field uses one shared scale across all three cases.', '',
        '| Claim limit | Consequence |', '| --- | --- |',
        '| Drifting developed reference | A startup comparison cannot prove a steady state |',
        '| 3000-update film screens | No automatic long-horizon or mesh-convergence claim |',
        '| Source-inclusive native reports | Subtract the verified user-source contribution once per boundary report |',
        '| Full separator closure and DPM fate audit | Complete before a strong reproduction claim |',
        '| Next action | Review scalar tolerances, accounting, distributions and film drift; select the smallest in-scope continuation |', ''])
    (PROJECT / 'results.md').write_text(text)
    # Update only this chat's Stage 3 machine-state node. Preserve all other
    # phase lanes exactly, including concurrent Server 1 work.
    state_path = PROJECT.parent / 'phase-state.yaml'
    state_text = state_path.read_text()
    match = re.search(r'(?ms)^stage3_reconstruction:\n.*?(?=^[^\s#]|\Z)', state_text)
    if not match:
        raise RuntimeError('Stage 3 machine-state node missing')
    block = match.group(0)
    for key, value in {'status': 'STARTUP_SCREENS_COMPLETE_REPRODUCTION_UNQUALIFIED',
                       'last_verified_native_iteration': str(summary['arms']['adaptive']['native_end'])}.items():
        block = re.sub(rf'(?m)^  {key}:.*$', f'  {key}: {value}', block)
    block += ('  analysis_summary: PyAnsys/output/phase72a-stage3-server3/20261005/analysis-summary.json\n'
              '  film_time_basis: VERIFIED_NATIVE_CLOCKS\n'
              '  fixed_and_adaptive_final_reopen: PASS\n')
    state_path.write_text(state_text[:match.start()] + block + state_text[match.end():])
    print('STAGE3_ANALYSIS_COMPLETE', json.dumps(summary['arms']), flush=True)


if __name__ == '__main__':
    main()
