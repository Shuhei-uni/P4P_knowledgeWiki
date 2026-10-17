"""Extract selected Phase 9 snapshots and embedded residuals without Fluent.

Only reads the selected OneDrive sources. No case load, solver command or
reinitialisation is used. Report buffers are endpoint samples, not histories.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np
from ansys.fluent.core.filereader.case_file import lispy

ROOT = Path(__file__).resolve().parents[3]
CLOUD = Path.home() / 'OneDrive/OneDrive - The University of Auckland/P4P-Fluent-Artifacts/Phase9'
OUT = ROOT / 'PyAnsys/output/phase9-selected-results/20261017'
SELECTION = [
    ('60k', 60964, 'start', 9582, 'Server6/60k/selected-checkpoints*/bulk-frozen*.cas.h5', 'bulk freeze'),
    ('60k', 60964, '195ms', 49899, 'Server6/60k/selected-checkpoints*/195ms*.cas.h5', 'bulk frozen'),
    ('342k', 342609, 'start', 8580, 'Server5/342k/selected*/342k-pre*.cas.h5', 'pre-EWF schedule'),
    ('342k', 342609, '195ms', 111460, 'Server5/342k/selected*/342k-ewf-final*.cas.h5', 'bulk frozen'),
    ('680k', 679970, 'start', 10580, 'Server1/680k/ewf-200ms*/bulk-freeze*.cas.h5', 'bulk freeze; flags reconstructed without iterations'),
    ('680k', 679970, '195ms', 103080, 'Server1/680k/ewf-200ms*/frozen-195ms*.cas.h5', 'bulk frozen'),
    ('997k', 997604, 'start', 9580, 'ewf-server3-997k/*/final*/997k-ewf-end-bulk*.cas.h5', 'immediately before freeze'),
    ('997k', 997604, '195ms', 49900, 'ewf-server3-997k/*/final*/997k-ewf-195ms*.cas.h5', 'bulk frozen'),
    ('2.6M', 2596657, 'start', 8580, 'Server4/2_6M/final*/final*.cas.h5', 'initial bulk; provisional EWF settings'),
]


def unquote(x):
    return str(x).strip('"')


def parse_vars(text):
    return {str(v[0]): v[1] for v in lispy.parse(text)[1]}


def pairs(x):
    return {str(v[0]): v[1] for v in x if isinstance(v, (list, tuple)) and len(v) == 2}


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def collect_expected_hashes():
    expected = {}

    def walk(obj, parent):
        if isinstance(obj, dict):
            for kind in ('case', 'data'):
                if kind in obj and kind + '_sha256' in obj:
                    expected[Path(str(obj[kind]).replace('\\', '/')).name] = obj[kind + '_sha256']
            if 'name' in obj and 'sha256' in obj:
                expected[obj['name']] = obj['sha256']
            if 'path' in obj and 'sha256' in obj:
                expected[Path(str(obj['path']).replace('\\', '/')).name] = obj['sha256']
            for v in obj.values():
                walk(v, parent)
        elif isinstance(obj, list):
            for v in obj:
                walk(v, parent)

    for p in CLOUD.rglob('*.json'):
        if 'archive' not in p.parts:
            walk(json.loads(p.read_text(encoding='utf-8-sig')), p.parent)
    return expected


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    expected = collect_expected_hashes()
    records = []
    for label, cells, stage, native, pattern, role in SELECTION:
        matches = list(CLOUD.glob(pattern))
        if len(matches) != 1:
            raise RuntimeError(f'{label}/{stage}: expected one case, found {len(matches)}')
        case = matches[0]
        data = case.with_name(case.name.replace('.cas.h5', '.dat.h5'))
        if not data.is_file():
            raise FileNotFoundError(data)
        folder = OUT / (label + '-' + stage)
        folder.mkdir(exist_ok=True)
        print('READ', label, stage, flush=True)
        with h5py.File(case, 'r') as c, h5py.File(data, 'r') as d:
            rv = parse_vars(c['settings/Rampant Variables'][0].decode())
            dv = parse_vars(d['settings/Data Variables'][0].decode())
            actual_cells = int(c['meshes/1'].attrs['cellCount'][0])
            assert actual_cells == cells
            reports = {}
            for name, scope, state in dv.get('monitor/average-over-state', []):
                if len(state) != 3 or not isinstance(state[2], list) or len(state[2]) != 1:
                    continue
                value = state[2][0]
                if not isinstance(value, (float, int)):
                    continue
                reports[unquote(name)] = {
                    'value': value, 'sample_iteration': state[1], 'scope_ids': scope,
                    'at_selected_iteration': abs(float(state[1]) - native) < 0.1,
                }
            film = pairs(dv.get('wall-film/solution-state', []))
            defs = {}
            for entry in rv.get('monitor/report-definitions', []):
                name = unquote(pairs(entry).get('name', ''))
                defs[name] = entry
            file_settings = []
            for entry in rv.get('monitor/monitorsets', []):
                item = pairs(entry)
                if 'file-name' in item:
                    file_settings.append({k: item[k] for k in ['name', 'file-name', 'report-defs', 'frequency', 'active?'] if k in item})
            residuals = {}
            if 'results/residuals' in d:
                for phase in d['results/residuals'].values():
                    for name, g in phase.items():
                        x = g['iterations'][:]
                        a = g['data'][:]
                        valid = (x <= native) & np.isfinite(x) & np.all(np.isfinite(a), axis=1)
                        x, a = x[valid], a[valid]
                        if not len(x):
                            continue
                        path = folder / ('residual-' + name + '.csv')
                        np.savetxt(path, np.column_stack([x, a]), delimiter=',',
                                   header='native_iteration,raw_residual,normalization,column_2,column_3', comments='')
                        unique, count = np.unique(np.diff(x), return_counts=True)
                        residuals[name] = {'first': float(x[0]), 'last': float(x[-1]),
                            'points': len(x), 'strides': dict(zip(map(str, unique), map(int, count))),
                            'is_active_at_save': bool(g.attrs.get('isActive', [False])[0]),
                            'csv': str(path.relative_to(ROOT)),
                            'last_raw': float(a[-1, 0]), 'last_normalization': float(a[-1, 1])}
            record = {'mesh': label, 'cells': cells, 'stage': stage, 'role': role,
                'selected_native_iteration': native, 'case': str(case), 'data': str(data),
                'film_state': film, 'reports': reports, 'residuals': residuals,
                'report_history_buffer_count': len(dv.get('monitor/all-mon-values', [])),
                'report_files': file_settings,
                'bulk_settings': {k: v for k, v in rv.items() if k in ['flow?', 'ke?', 'mp?', 'drift?', 'solve/flow?', 'solve/ke?', 'solve/mp?', 'solve/drift?']},
                'film_parameters': rv.get('wall-film/model-parameters', []),
                'dpm_summary': dv.get('dpm/summary', []),
                'dpm_per_injection': dv.get('dpm/summaries-per-injection', [])}
            write_json(folder / 'report-definitions.json', defs)
            write_json(folder / 'record.json', record)
        for kind, path in [('case', case), ('data', data)]:
            hashed = digest(path)
            ref = expected.get(path.name)
            if ref and hashed != ref:
                raise RuntimeError('Source hash mismatch: ' + path.name)
            record[kind + '_identity'] = {'bytes': path.stat().st_size, 'sha256': hashed,
                'reference_hash_available': ref is not None, 'reference_match': hashed == ref if ref else None}
        write_json(folder / 'record.json', record)
        records.append(record)
        write_json(OUT / 'selected-results.json', records)
        present = [n for n, v in reports.items() if v['at_selected_iteration']]
        print('EXTRACTED', label, stage, 'film_ms', round(1000 * film.get('film_elapsed_time', 0), 6),
              'current_reports', len(present), 'residual_end', residuals.get('continuity', {}).get('last'), flush=True)
    write_json(OUT / 'extraction.json', {'status': 'COMPLETE_OFFLINE', 'source_count': len(records),
        'generator': str(Path(__file__).relative_to(ROOT)), 'generator_sha256': digest(Path(__file__)),
        'case_loads': 0, 'solve_calls': 0, 'source_files_modified': False,
        'report_histories': 'Endpoint report buffers only; all-mon-values inspected explicitly.',
        'missing_pairs': ['2.6M/195ms']})


if __name__ == '__main__':
    main()
