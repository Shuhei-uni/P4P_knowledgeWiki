"""Inspect Server 3 and read archived 997k files without changing its case."""
from pathlib import Path
import hashlib
import json
import math
import signal
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
import run_phase9_mesh_startup as transport
from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.remote_text import read_text


def timeout(_signum, _frame):
    raise TimeoutError('Server 3 read-only inspection deadline exceeded')


def main():
    out = ROOT / 'output/phase9-997k-checkpoints/20261009'
    raw = out / 'raw'
    raw.mkdir(parents=True, exist_ok=False)
    campaign = ROOT / 'output/phase9-mesh-convergence/20261007'
    run = json.loads((campaign / '997k-run.json').read_text())
    pairs = {}
    for n in [6080, 7080, 8080]:
        p = next(campaign.glob(f'997k-checkpoint-{n}-*.json'))
        d = json.loads(p.read_text())
        pairs[str(n)] = {'pair': d['pair'], 'receipt': str(p), 'reopen_status': d['status']}
    extra = json.loads((campaign / '997k-extra2000/1791507047505279000/run-manifest.json').read_text())
    pairs['9080'] = {'pair': extra['midpoint_pair'], 'reopen_status': 'NOT_CHECKED_BY_THIS_READ_ONLY_INSPECTION'}
    selection = json.loads((campaign / 'initial-bulk-final-selection.json').read_text())
    pairs['9103'] = {'pair': selection['pairs']['997k']['source'], 'reopen_status': selection['shared_997k_reopen']['status']}
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    s = transport.attach()
    before = {'native_iteration': transport.native_iteration(s),
              'iterating': s.settings.solution.run_calculation.iterating()}
    print('SERVER3_CURRENT', json.dumps(before), flush=True)
    for n, item in pairs.items():
        item['files_present'] = {kind: remote_file_exists(s, item['pair'][kind]) for kind in ['case', 'data']}
        print('CHECKPOINT_FILES', n, json.dumps(item['files_present']), flush=True)
    signal.alarm(0)
    names = ['p72s3-pressure-inlet', 'p72s3-pressure-outlet',
             'v2-flux-phase2-steamoutlet', 'v2-total-liquid-mass', 'v2-applied-absorber',
             'p72a-e2.7-ewf-film-mass-total', 'p72a-e2.7-ewf-thickness-max',
             'p72a-e2.7-ewf-velocity-mag-max', 'p72a-e2.7-ewf-outflow-mass-total']
    histories, sources = {}, {}
    for name in names:
        path = run['report_paths'][name]
        signal.alarm(25)
        content = read_text(s, path)
        signal.alarm(0)
        (raw / (name + '.out')).write_text(content)
        rows = {}
        for line in content.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit():
                n, value = int(parts[0]), float(parts[1])
                if 1581 <= n <= 9103:
                    if n in rows and rows[n] != value:
                        raise RuntimeError('Conflicting duplicate native report coordinate')
                    assert math.isfinite(value)
                    rows[n] = value
        assert set(range(1581, 9104)).issubset(rows), name
        histories[name] = rows
        sources[name] = {'remote_path': path, 'sha256': hashlib.sha256(content.encode()).hexdigest()}
        print('READ_ARCHIVED_REPORT', name, len(rows), flush=True)
    signal.alarm(25)
    after = {'native_iteration': transport.native_iteration(s),
             'iterating': s.settings.solution.run_calculation.iterating()}
    signal.alarm(0)
    (out / 'histories.json').write_text(json.dumps(histories, indent=2) + '\n')
    (out / 'inspection.json').write_text(json.dumps({
        'status': 'COMPLETE_READ_ONLY', 'server': '3', 'before': before, 'after': after,
        'pairs': pairs, 'sources': sources, 'case_loads': 0, 'solves': 0, 'setters': 0,
        'inspection_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }, indent=2) + '\n')
    print('SERVER3_AFTER', json.dumps(after), flush=True)


if __name__ == '__main__':
    main()
