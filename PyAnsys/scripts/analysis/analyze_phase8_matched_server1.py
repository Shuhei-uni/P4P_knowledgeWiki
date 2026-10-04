"""Verify the scoped ten-case batch and compare its declared native window.

Read-only analysis: no Fluent connection, field edits, or extra iterations.
"""
from pathlib import Path
import csv
from datetime import datetime
import hashlib
import json
import re

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / 'output/phase8-server1-matched-20261003'
SHARE = Path(r'C:\Users\Shuhei Yokkaichi\OneDrive\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase8\Matched-20261003\Final')
ROW = re.compile(r'^\s*(\d+)\s+([-+\d.eE]+)\s*$', re.M)
RESIDUAL = re.compile(r'^\s*(\d+)\s+(\d+\.\d+e[+-]\d+)', re.M | re.I)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def mesh_digest(path):
    digest = hashlib.sha256()
    with h5py.File(path) as case:
        def visit(name, item):
            if isinstance(item, h5py.Dataset):
                digest.update(name.encode())
                digest.update(str((item.shape, item.dtype)).encode())
                digest.update(np.asarray(item[()]).tobytes())
        case['meshes'].visititems(visit)
    return digest.hexdigest()


def main():
    spec = json.loads((BATCH / 'batch-spec.json').read_text(encoding="utf-8"))
    batch = json.loads((BATCH / 'batch-manifest.json').read_text(encoding="utf-8"))
    assert batch['status'] == 'COMPLETE' and len(batch['completed']) == 10
    coordinates = np.arange(15500, 16001, 10)
    residual_coordinates = range(15501, 16001)
    runs, receipts = [], {}
    for point in spec['points']:
        folder = BATCH / point['id']
        m = json.loads((folder / 'manifest.json').read_text(encoding="utf-8"))
        assert m['status'] == 'COMPLETE' and m['server_id'] == '1'
        assert m['last_verified_native_iteration'] == 16000
        assert m['achieved_additional_iterations'] == point['additional_iterations']
        assert m['configured'] == m['start_reopen'] == m['final_reopen']
        assert [c['native_iteration'] for c in m['checkpoints']] == list(range(point['start_iteration'] + 1000, 16001, 1000))
        files = {}
        for key, suffix in [('case', 'cas'), ('data', 'dat')]:
            path = SHARE / point['id'] / f'final.{suffix}.h5'
            assert path.is_file(), path
            actual = sha(path)
            assert actual == m['final_pair'][key + '_sha256'], path
            files[key] = {'local_synced_path': str(path), 'sha256': actual, 'bytes': path.stat().st_size}
        mesh = mesh_digest(Path(files['case']['local_synced_path']))
        if point['family'] == 'F3':
            with h5py.File(files['case']['local_synced_path']) as case:
                variables = case['settings/Rampant Variables'][0].decode()
                assert '(wall-film/model-parameters ())' in variables, 'F3 has film model parameters'
        reports = {}
        for name in m['report_paths']:
            path = folder / 'monitors' / f'{name}.out'
            history = {int(i): float(v) for i, v in ROW.findall(path.read_text(encoding="utf-8"))}
            assert set(coordinates) <= history.keys(), (point['id'], name)
            reports[name] = np.array([history[i] for i in coordinates])
            assert np.isfinite(reports[name]).all()
        def v(name):
            return reports['p8-' + name]
        inlet = v('flux-mixture-liquidinlet') + v('flux-mixture-steaminlet')
        liquid_inlet = v('flux-phase2-liquidinlet') + v('flux-phase2-steaminlet')
        liquid_outlet = -v('flux-phase2-steamoutlet')
        dpm_feed = m['configured']['dpm']['dpm_total_kg_s']
        total_water = liquid_inlet + dpm_feed
        source = v('dpm-mass-source-total')
        assert m['report_definitions']['p8-dpm-mass-source-total']['kind'] == 'volume-sum'
        boundary_gap = inlet + v('flux-mixture-steamoutlet')
        transcript = (folder / 'transcript.txt').read_text(encoding='utf-8', errors='replace')
        residuals = {int(i): float(x) for i, x in RESIDUAL.findall(transcript)}
        assert set(residual_coordinates) <= residuals.keys()
        continuity = np.array([residuals[i] for i in residual_coordinates])
        inventory = v('mass-phase2-total')
        # This is the Eulerian boundary-plus-DPM ledger, not whole-system film closure.
        partial_gap = boundary_gap + source
        r = {
            'id': point['id'], 'family': point['family'], 'speed_m_s': point['speed_m_s'],
            'dpm_fraction': point['fraction'], 'window': [15500, 16000], 'report_samples': len(coordinates),
            'residual_samples': len(continuity), 'manifest': str(folder / 'manifest.json'),
            'final_pair_verification': files, 'mesh_dataset_sha256': mesh,
            'elapsed_wall_minutes': (datetime.fromisoformat(m['completed_at']) - datetime.fromisoformat(m['started_at'])).total_seconds() / 60,
            'eulerian_inlet_mean_kg_s': float(inlet.mean()), 'dpm_feed_kg_s': dpm_feed,
            'total_water_feed_mean_kg_s': float(total_water.mean()),
            'liquid_outlet_mean_kg_s': float(liquid_outlet.mean()),
            'eulerian_liquid_outlet_percent_total_water': float(100 * np.mean(liquid_outlet / total_water)),
            'eulerian_liquid_outlet_percent_eulerian_liquid': float(100 * np.mean(liquid_outlet / liquid_inlet)),
            'bulk_liquid_inventory_start_end_kg': [float(inventory[0]), float(inventory[-1])],
            'bulk_liquid_inventory_slope_kg_per_iteration': float(np.polyfit(coordinates, inventory, 1)[0]),
            'eulerian_boundary_mean_absolute_gap_percent_eulerian_feed': float(100 * np.mean(np.abs(boundary_gap) / inlet)),
            'eulerian_boundary_plus_dpm_mean_absolute_gap_percent_eulerian_feed': float(100 * np.mean(np.abs(partial_gap) / inlet)),
            'dpm_mass_source_mean_kg_s': float(source.mean()),
            'continuity_min_max': [float(continuity.min()), float(continuity.max())],
            'continuity_max_below_0p02': bool(continuity.max() < 0.02),
            'fatal_event': bool(re.search(r'floating point exception|amg solver diverged|error:.*(?:diverg|non-finite)', transcript, re.I)),
            'reverse_flow_warnings': transcript.count('Reversed flow on'),
            'viscosity_limit_warnings': transcript.count('turbulent viscosity limited'),
        }
        if point['family'] == 'F4':
            r['film'] = {name.removeprefix('p8-ewf-'): {'start': float(values[0]), 'end': float(values[-1]), 'mean': float(values.mean())}
                         for name, values in reports.items() if name.startswith('p8-ewf-')}
            r['film_unavailable_reports'] = list(m['film_reports'].get('unavailable', {}))
        receipts[point['id']] = m
        runs.append(r)
        print(point['id'], 'verified', flush=True)
    assert len({r['mesh_dataset_sha256'] for r in runs}) == 1
    film_configs = [receipts[r['id']]['configured']['film'] for r in runs if r['family'] == 'F4']
    for film in film_configs:
        for key in ['model_parameters', 'film_wall', 'bottom_wall_film']:
            assert film[key] == film_configs[0][key], 'F4 film package mismatch'
    pairs = []
    for r3 in [r for r in runs if r['family'] == 'F3']:
        r4 = next(r for r in runs if r['family'] == 'F4' and (r['speed_m_s'], r['dpm_fraction']) == (r3['speed_m_s'], r3['dpm_fraction']))
        a, b = receipts[r3['id']]['configured'], receipts[r4['id']]['configured']
        assert a['dpm'] == b['dpm'], 'Carrier/DPM setting mismatch in pair'
        assert a['controls'] == b['controls'], 'Carrier controls mismatch in pair'
        pairs.append({'F3': r3['id'], 'F4': r4['id'], 'carrier_dpm_and_controls_identical': True,
                      'liquid_outlet_percentage_point_change_F4_minus_F3': r4['eulerian_liquid_outlet_percent_total_water'] - r3['eulerian_liquid_outlet_percent_total_water'],
                      'bulk_inventory_end_change_kg_F4_minus_F3': r4['bulk_liquid_inventory_start_end_kg'][1] - r3['bulk_liquid_inventory_start_end_kg'][1]})
    output = {'status': 'VERIFIED_COMPLETE', 'comparison_window': [15500, 16000], 'runs': runs, 'pairs': pairs,
              'film_checks': {'F3_case_model_parameters_empty': True, 'F4_package_identical_across_five_points': True},
              'claim_limit': 'Steady-iteration inventory slopes are not physical storage rates. Eulerian outlet fractions omit terminal DPM fates and film transfers. EWF is provisional E2.7; film transfer rates/whole-system closure are incomplete. No convergence claim or further solve is authorized.'}
    (BATCH / 'matched-analysis.json').write_text(json.dumps(output, indent=2) + '\n')
    columns = ['id', 'family', 'speed_m_s', 'dpm_fraction', 'elapsed_wall_minutes', 'liquid_outlet_mean_kg_s', 'eulerian_liquid_outlet_percent_total_water', 'bulk_liquid_inventory_slope_kg_per_iteration', 'eulerian_boundary_mean_absolute_gap_percent_eulerian_feed', 'dpm_mass_source_mean_kg_s']
    with (BATCH / 'matched-comparison.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(runs)


if __name__ == '__main__':
    main()
