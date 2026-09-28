"""Offline evidence audit for the September 2026 Phase 7b planning review.

Reads existing artifacts only; never imports a Fluent client. Run from repo root
with PyAnsys/.venv/bin/python. Output is derived evidence, not a run disposition.
"""
from pathlib import Path
import argparse
import csv
import json
import subprocess
import numpy as np

from analyze_phase07b_screen import parse_history, parse_residuals, derive, fingerprint


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = {'status': 'OFFLINE_REVIEW_ONLY', 'qualified': False,
              'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    base = Path('Project/experiments/phase-07-2a-wall-liquid-routing/ewf-family/figures')
    csv_path = base / 'E2.7-CONT5000-requested-histories.csv'
    manifest_path = base / 'E2.7-CONT5000-requested-histories-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    with csv_path.open() as f:
        rows = list(csv.DictReader(f))
    x = np.array([int(r['native_iteration']) for r in rows])
    assert np.array_equal(x, np.arange(8586, 13587))
    mapping = {
        'total_liquid_mass_kg': 'v2-total-liquid-mass',
        'phase2_steamoutlet_flux_kg_s': 'v2-flux-phase2-steamoutlet',
        'ewf_film_mass_kg': 'p72a-e2.7-ewf-film-mass-total',
        'ewf_velocity_area_weighted_average_m_s': 'p72a-e2.7-ewf-velocity-mag-awavg',
        'ewf_maximum_film_thickness_mm': 'p72a-e2.7-ewf-thickness-max',
    }
    arrays = {}; series = {}
    for key, native in mapping.items():
        y = np.array([float(r[key]) for r in rows]); arrays[key] = y
        assert np.isfinite(y).all()
        stats = {'count': len(y), 'first': float(y[0]), 'last': float(y[-1]),
                 'minimum': float(y.min()), 'maximum': float(y.max()),
                 'mean_final_500': float(y[-500:].mean()),
                 'slope_final_500_per_iteration': float((y[-1]-y[-500])/499)}
        assert all(np.isclose(v, manifest['series'][native][k], rtol=1e-12, atol=1e-12)
                   for k, v in stats.items())
        stats.update(change=float(y[-1]-y[0]), change_percent=100*float(y[-1]/y[0]-1),
                     strictly_increasing=bool(np.all(np.diff(y)>0)),
                     whole_window_mean=float(y.mean()))
        stats['tails'] = {str(n): {
            'start': int(x[-n]), 'end': int(x[-1]),
            'ols_slope_per_native_iteration': float(np.polyfit(x[-n:]-x[-n:].mean(), y[-n:], 1)[0]),
            'endpoint_change_percent': float(100*(y[-1]/y[-n]-1))}
            for n in [500, 1000, 2000]}
        series[key] = stats
    raw_paths = [manifest['source_manifest'], manifest['source_histories'],
                 manifest['ewf_area']['wetted_area_source']]
    result['ewf_export_audit'] = {
        'inputs': [fingerprint(csv_path), fingerprint(manifest_path)],
        'consecutive_coordinates': True, 'manifest_statistics_match': True,
        'series': series,
        'combined_bulk_film_storage_change_kg': float(
            arrays['total_liquid_mass_kg'][-1]+arrays['ewf_film_mass_kg'][-1]
            -arrays['total_liquid_mass_kg'][0]-arrays['ewf_film_mass_kg'][0]),
        'native_bundle_availability': {p: Path(p).exists() for p in raw_paths},
        'limit': 'Five exported series verified; no film-time or full native mass ledger in this CSV.'}
    cases = {}
    for gate in [4, 5, 6]:
        p = Path(f'PyAnsys/output/phase07b-g{gate}/comparison.json')
        comparison = json.loads(p.read_text())
        for label, record in comparison['cases'].items():
            run = Path(record['run'])
            if str(run) in cases:
                continue
            h, audit = max([parse_history(q) for q in run.glob('history-*.out')],
                           key=lambda z: z[1]['last_iteration'])
            assert np.array_equal(h['iteration'], np.arange(1, 5001))
            d, _ = derive(h); late = h['iteration'] >= 4501
            prior = (h['iteration'] >= 4001) & (h['iteration'] <= 4500)
            closure = {phase: float(np.abs(d[phase+'_closure_percent_feed'][late]).mean())
                       for phase in ['liquid', 'vapor', 'mixture']}
            a = d['whole_water_volume'][prior].mean(); b = d['whole_water_volume'][late].mean()
            inv = float(100*(b-a)/max(abs(a),abs(b),1e-6))
            res, ra = parse_residuals(run/'solve.trn')
            maxima = {k: float(v[res['iteration'] >= 4501].max()) for k,v in res.items() if k != 'iteration'}
            expected = record['indicators']
            assert all(np.isclose(v,expected['closure'][k]['mean_absolute_percent_feed']) for k,v in closure.items())
            assert np.isclose(inv, expected['inventory']['window_mean_change_percent_of_larger_mean'])
            assert all(np.isclose(v,expected['residuals'][k]['maximum']) for k,v in maxima.items())
            cases[str(run)] = {'label':label, 'history':audit['source'], 'residuals':ra['source'],
                               'comparison':fingerprint(p), 'closure_mean_absolute_percent_feed':closure,
                               'inventory_window_change_percent':inv, 'residual_late_maxima':maxima,
                               'recorded_indicators_match_raw_recalculation':True}
    result['phase7b_terminal_cases'] = cases
    # This is a retrospective startup diagnostic, never an acceptance window.
    early = {}
    for label, run in [
        ('E6', 'p7b-s40-t020-coupled-cfl20-nphase-resume-20260923T231816Z'),
        ('E7', 'p7b-s40-t100-coupled-cfl20-nphase-resume-20260924T054531Z')]:
        p = Path('PyAnsys/output')/run/'history-00500.out'
        h, a = parse_history(p); d, _ = derive(h)
        mask = (h['iteration'] >= 401) & (h['iteration'] <= 500)
        assert np.array_equal(h['iteration'][mask], np.arange(401,501))
        early[label] = {'input':a['source'], 'window':[401,500],
                        'closure_mean_absolute_percent_feed':{k:float(np.abs(d[k+'_closure_percent_feed'][mask]).mean()) for k in ['liquid','vapor','mixture']},
                        'mean_applied_removal_kg_s':float(d['native_applied_removal'][mask].mean()),
                        'inventory_at_500_m3':float(d['whole_water_volume'][h['iteration']==500][0])}
    result['early_diagnostic_not_acceptance'] = early
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'], 'terminal_cases_recomputed':len(cases),
                      'exported_ewf_samples':len(x), 'output':str(args.output/'audit.json')}))


if __name__ == '__main__':
    main()
