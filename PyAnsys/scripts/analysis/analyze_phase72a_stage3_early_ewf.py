"""Audit the completed early-EWF screen and compare the prescribed ramps."""
from pathlib import Path
import csv
import hashlib
import json
import re
import sys
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/analysis'))
from plot_phase72a_endpoint_lineage import ROW, SUB, NAMES, out_file
OUT = ROOT / 'output/phase72a-stage3-early-ewf-server1/20261005'
OLD = ROOT / 'output/phase72a-lineage-N45606/20261005'
PROJECT = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup'
FIG = PROJECT / 'figures'
CLOUD = Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts')
FILM = re.compile(r'Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)')


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def stats(values):
    a = np.asarray(values)
    return {'peak': float(a.max()), 'p95': float(np.percentile(a, 95)), 'mean': float(a.mean()), 'end': float(a[-1])}


def main():
    manifest = json.loads((OUT / 'run-manifest.json').read_text())
    assert manifest['verified_native_end'] == 5080 and manifest['final_reopen'] == 'PASS'
    endpoint = json.loads((OUT / 'final-reopen.json').read_text())
    histories = json.loads((OUT / 'final-histories.json').read_text())
    ids = np.arange(1580, 5081)
    h = {}
    for name, record in histories.items():
        assert record['iterations'] == ids.tolist(), name
        native = out_file(OUT / f'final-{name}.out')
        assert sorted(native) == ids.tolist(), name
        a = np.array(record['values'])
        assert np.isfinite(a).all() and np.array_equal(a, [native[int(i)] for i in ids]), name
        h[name] = a
    fields = endpoint['state']['readback']['fields']
    for name in ['v2-flux-phase2-liquidinlet', 'v2-flux-phase2-steamoutlet']:
        assert np.isclose(h[name][-1], fields[name + '(without-sources)'][0], atol=1e-8)
    source_error = abs(h['v2-applied-absorber'] + h['p72-contact-removal'])
    assert source_error[1:].max() < 1e-8
    residuals, film, clocks = {}, {}, {}
    pending, clock = [], None
    for line in (OUT / 'run-transcript.txt').read_text().splitlines():
        m = SUB.search(line)
        if m:
            pending.append([int(m[1]), *[float(v) for v in m.groups()[1:]]])
        m = FILM.search(line)
        if m:
            clock = [float(v) for v in m.groups()]
        m = ROW.match(line)
        if m:
            i = int(m[1])
            value = [float(v) for v in m.groups()[1:]]
            if i in residuals:
                assert residuals[i] == value, ('conflicting carrier residual', i)
            residuals[i] = value
            if pending:
                film[i] = {'last': pending[-1][1:], 'peak': np.max([v[1:] for v in pending], axis=0).tolist(), 'subiterations': pending[-1][0]}
            if clock:
                clocks[i] = clock
            pending, clock = [], None
    wanted = set(range(1581, 5081))
    assert wanted.issubset(residuals) and set(film) == wanted and set(clocks) == wanted
    assert np.allclose([clocks[i][1] for i in sorted(wanted)], 1e-6, atol=1e-15, rtol=0)
    assert np.allclose([clocks[i][0] for i in sorted(wanted)], np.arange(1, 3501) * 1e-6, atol=1e-12, rtol=0)
    assert np.isclose(endpoint['film_solution_state']['film_elapsed_time'], .0035, atol=1e-12)
    dump('carrier-residuals.json', residuals)
    dump('film-residuals.json', film)
    dump('film-clocks.json', clocks)
    # Verify shared final bytes, then read residual normalization from saved data.
    paths = {'A': CLOUD / 'Phase72A/Stage3/early-ewf-startup/parent-A/parent-A.dat.h5',
             'historical_B': CLOUD / 'Phase71A/FamilyR/finals/P71A-R0-SMOOTH-CONTROL/20260922T025211Z/P71A-R0-SMOOTH-CONTROL-full-loading-final.dat.h5',
             'new_N5080': CLOUD / 'Phase72A/Stage3/early-ewf-startup/final-N5080/final-N5080.dat.h5'}
    hashes, normalization = {}, {}
    final_folder = paths['new_N5080'].parent
    for kind, ext in [('case', 'cas.h5'), ('data', 'dat.h5')]:
        p = final_folder / ('final-N5080.' + ext)
        with p.open('rb') as f:
            hashes[kind] = hashlib.file_digest(f, 'sha256').hexdigest()
        assert hashes[kind] == manifest['final_pair'][kind + '_sha256']
    for label, p in paths.items():
        with h5py.File(p) as f:
            g = {n: g for phase in f['results/residuals'].values() for n, g in phase.items()}
            normalization[label] = {n: {'last': float(g[n]['data'][-1, 1]),
                                        'minimum': float(g[n]['data'][:, 1].min()),
                                        'maximum': float(g[n]['data'][:, 1].max())} for n in NAMES}
            continuity = g['continuity']
            selected = continuity['iterations'][:] >= 1580
            normalization[label]['continuity']['from_A_minimum'] = float(continuity['data'][:, 1][selected].min())
            normalization[label]['continuity']['from_A_maximum'] = float(continuity['data'][:, 1][selected].max())
    assert len({r['continuity']['last'] for r in normalization.values()}) == 1
    assert all(r['continuity']['from_A_minimum'] == r['continuity']['from_A_maximum'] for r in normalization.values())
    old = {int(r['native_iteration']): r for r in csv.DictReader((OLD / 'selected-lineage-histories.csv').open())}
    oldr = {int(r['native_iteration']): [float(r[k]) for k in NAMES] for r in csv.DictReader((OLD / 'carrier-residuals.csv').open())}
    oldcmd = out_file(OLD / 'recovered-r0-reports/P71A-R0-SMOOTH-CONTROL-v2-command.out')
    newcmd = dict(zip(ids.tolist(), h['v2-command'].tolist()))
    diffs = {i: newcmd[i + 500] - oldcmd[i] for i in range(1581, 3581) if abs(newcmd[i + 500] - oldcmd[i]) > 1e-8}
    assert set(diffs) == set(range(1591, 3580, 10))
    assert np.allclose(list(diffs.values()), .43845, atol=1e-10, rtol=0)
    ramp_blocks = [b for b in manifest['blocks'] if b['stage'] == 'ramp']
    assert len(ramp_blocks) == 200
    for k, b in enumerate(ramp_blocks):
        assert b['native_start'] == 2080 + 10 * k and b['native_end'] == 2090 + 10 * k
        assert np.isclose(b['feed']['multiplier'], .25 + .75 * k / 200, atol=1e-12)
    def newmetric(lo, hi):
        sl = (ids >= lo) & (ids <= hi)
        r = np.array([residuals[i] for i in range(lo, hi + 1)])
        return {'continuity': stats(r[:, 0]), 'scaled_phase_fraction': stats(r[:, 6]),
                'bulk_plus_film_kg': stats((h['v2-total-liquid-mass'] + h['p72a-e2.7-ewf-film-mass-total'])[sl]),
                'outward_liquid_kg_s': stats(-h['v2-flux-phase2-steamoutlet'][sl])}
    def oldmetric(lo, hi):
        r = np.array([oldr[i] for i in range(lo, hi + 1)])
        return {'continuity': stats(r[:, 0]), 'scaled_phase_fraction': stats(r[:, 6]),
                'bulk_plus_film_kg': stats([float(old[i]['bulk_plus_ewf_kg']) for i in range(lo, hi + 1)]),
                'outward_liquid_kg_s': stats([-float(old[i]['phase2_steamoutlet_signed_kg_s']) for i in range(lo, hi + 1)])}
    comparison = {'ramp': {'historical': oldmetric(1581, 3580), 'early_ewf': newmetric(2081, 4080)},
                  'final_500_of_matched_1000_target_hold': {'historical': oldmetric(4081, 4580), 'early_ewf': newmetric(4581, 5080)}}
    bad = [i for i, v in film.items() if max(v['last']) > 1e-5]
    mass, drainage, accretion = [h[k] for k in ['p72a-e2.7-ewf-film-mass-total', 'p72a-e2.7-ewf-outflow-mass-total', 'p72a-e2.7-ewf-secondary-phase-mass-total']]
    integrated = float(accretion[1:].sum() * 1e-6)
    late = ids > 4580
    at4580 = int(np.where(ids == 4580)[0][0])
    summary = {'status': 'COMPLETE_ANALYSED', 'native_window': [1580, 5080], 'updates': 3500,
               'report_count': len(h), 'report_rows_each': len(ids), 'native_reports_against_JSON': 'PASS_ALL_31',
               'carrier_rows': len(wanted), 'film_residual_rows': len(film), 'film_clock_rows': len(clocks), 'history_gaps': [],
               'wall_minutes': manifest['wall_seconds'] / 60, 'live': json.loads((OUT / 'analysis-live-status.json').read_text()),
               'shared_final_hashes': hashes, 'normalization': normalization, 'comparison': comparison,
               'activation_hold': newmetric(1581, 2080), 'ramp_boundary_blocks_verified': 200,
               'command_cache_difference': {'count': len(diffs), 'new_minus_old_kg_s': .43845, 'scope': 'First report row after each of 199 feed increments; original cache lags one update; physical prescribed schedule unchanged'},
               'source_tracking_max_error_after_N1580_kg_s': float(source_error[1:].max()),
               'initial_parent_source_report_cache_error_kg_s': float(source_error[0]),
               'final_bulk_kg': float(h['v2-total-liquid-mass'][-1]), 'final_film_kg': float(mass[-1]),
               'final_combined_kg': float(h['v2-total-liquid-mass'][-1] + mass[-1]),
               'final_outward_liquid_kg_s': float(-h['v2-flux-phase2-steamoutlet'][-1]),
               'film_time_s': endpoint['film_solution_state']['film_elapsed_time'], 'peak_film_cfl': float(h['p72a-e2.7-ewf-courant-max'][1:].max()),
               'maximum_thickness_peak_mm': float(h['p72a-e2.7-ewf-thickness-max'][1:].max() * 1000),
               'maximum_thickness_final_mm': float(h['p72a-e2.7-ewf-thickness-max'][-1] * 1000),
               'integrated_accretion_kg': integrated, 'drained_mass_kg': float(drainage[-1]),
               'film_ledger_error_percent': float(100 * abs(mass[-1] + drainage[-1] - integrated) / integrated),
               'film_inner_failed_updates': bad, 'film_inner_failed_count': len(bad),
               'film_inner_final_residual_max_huv': np.max([v['last'] for v in film.values()], axis=0).tolist(),
               'ramp_film_inner_failed_count': sum(2081 <= i <= 4080 for i in bad),
               'last_100_film_inner_failed_count': sum(i > 4980 for i in bad),
               'final_500_bulk_gain_kg': float(h['v2-total-liquid-mass'][-1] - h['v2-total-liquid-mass'][at4580]),
               'final_500_film_gain_kg': float(mass[-1] - mass[at4580]),
               'final_500_accretion_kg_s': float(accretion[late].mean()),
               'final_500_drainage_kg_s': float((drainage[-1] - drainage[at4580]) / .0005),
               'final_500_film_storage_kg_s': float((mass[-1] - mass[at4580]) / .0005),
               'final_500_boundary_contact_residual_kg_s': float(np.mean(h['v2-flux-phase2-liquidinlet'][late] + h['v2-flux-phase2-steamoutlet'][late] - h['p72-contact-removal'][late])),
               'claim': 'Smaller continuity excursion and liquid storage/carryover during the ramp; activation spike and late film inner failures remain; combined recipe only'}
    dump('analysis-summary.json', summary)
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    new_color, old_color = '#0072b2', '#a6662b'
    with PdfPages(OUT / 'startup-comparison.pdf') as pdf:
        fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True, layout='constrained')
        x = np.arange(1, 3001)
        oi, ni = x + 1580, x + 2080
        arrays = [([oldr[i][0] for i in oi], [residuals[i][0] for i in ni], 'Continuity residual', True),
                  ([oldr[i][6] for i in oi], [residuals[i][6] for i in ni], 'Scaled phase fraction\n(normalization differs)', True),
                  ([float(old[i]['bulk_plus_ewf_kg']) for i in oi], [(h['v2-total-liquid-mass'] + mass)[i-1580] for i in ni], 'Bulk + film liquid (kg)', False),
                  ([-float(old[i]['phase2_steamoutlet_signed_kg_s']) for i in oi], [-h['v2-flux-phase2-steamoutlet'][i-1580] for i in ni], 'Outward liquid (kg/s)', False)]
        for ax, (a, b, ylabel, log) in zip(axes, arrays):
            ax.plot(x, a, color=old_color, lw=.7, label='Historical: EWF off; Coupled after ramp')
            ax.plot(x, b, color=new_color, lw=.8, label='Early EWF: R3/contact; 500-update low hold')
            ax.axvline(2000, color='#777777', ls='--', lw=1)
            ax.axvspan(2000, 3000, color='#777777', alpha=.06)
            ax.set_ylabel(ylabel);ax.grid(alpha=.2)
            if log:ax.set_yscale('log')
        axes[0].legend(fontsize=8);axes[-1].set_xlabel('Updates since ramp start: 1–2000 ramp; 2001–3000 target-feed hold')
        fig.suptitle('Matched loading comparison — raw native histories\nContinuity improves; inventory and carryover fall; phase-fraction scales differ')
        fig.savefig(FIG / 'ramp-comparison.png', dpi=160);pdf.savefig(fig);plt.close(fig)
        fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True, layout='constrained')
        rr = np.array([residuals[int(i)] for i in ids])
        for j, name in enumerate(NAMES):
            ax = axes[0] if j in [0, 6] else axes[1] if j in [1, 2, 3] else axes[2]
            ax.plot(ids, rr[:, j], lw=.7, label=name)
        for ax in axes:
            ax.set_yscale('log');ax.set_ylabel('Scaled carrier residual');ax.grid(alpha=.2);ax.legend(fontsize=8)
            ax.axvspan(1580, 2080, color='#b87520', alpha=.08)
            for i in [2080, 4080]:ax.axvline(i, color='#777777', ls='--', lw=1)
        axes[-1].set_xlabel('Native iteration: activate at A=1580; ramp starts 2080; full-feed hold starts 4080')
        fig.suptitle('Entire new startup — activation spike remains visible\n500 low-feed updates separate model activation from inlet loading')
        fig.savefig(FIG / 'startup-carrier-residuals.png', dpi=160);pdf.savefig(fig);plt.close(fig)
        fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True, layout='constrained')
        time_ms = np.arange(1, 3501) * .001
        axes[0].plot(time_ms, mass[1:], color=new_color);axes[0].set_ylabel('Film inventory (kg)')
        axes[1].plot(time_ms, accretion[1:], color=new_color, lw=.8, label='Accretion')
        axes[1].plot(time_ms, np.diff(drainage) / 1e-6, color=old_color, lw=.8, label='Drainage')
        axes[1].set_ylabel('Film rate (kg/s)');axes[1].legend(fontsize=8)
        axes[2].plot(time_ms, h['p72a-e2.7-ewf-thickness-max'][1:] * 1000, color=new_color);axes[2].set_ylabel('Maximum thickness (mm)')
        for j, name in enumerate(['h', 'u', 'v']):
            axes[3].plot(time_ms, [film[i]['last'][j] for i in range(1581, 5081)], lw=.7, label=name)
        axes[3].axhline(1e-5, color='#777777', ls=':', label='Inner tolerance');axes[3].set_yscale('log');axes[3].set_ylabel('Final film residual');axes[3].legend(ncol=4, fontsize=8)
        for ax in axes:
            ax.grid(alpha=.2)
            for t in [.5, 2.5]:ax.axvline(t, color='#777777', ls='--', lw=1)
        axes[-1].set_xlabel('Native film time since dry A start (ms)')
        fig.suptitle('Film development — 3.5 ms, with repeated inner failures near the end\nSmall film ledger error does not prove every inner solve converged')
        fig.savefig(FIG / 'film-development.png', dpi=160);pdf.savefig(fig);plt.close(fig)
    print(json.dumps({k: summary[k] for k in ['status', 'comparison', 'film_inner_failed_count', 'film_ledger_error_percent']}, indent=2))


if __name__ == '__main__':
    main()
