"""Read recorded Phase 9 report files. No case loads, setters, or solves."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import signal
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from pyansys_fluent.remote_text import read_text


def deadline(_signum, _frame):
    raise TimeoutError('Read-only Fluent extraction exceeded its deadline')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', choices=['3', '4'], required=True)
    args = parser.parse_args()
    label = '997k' if args.server == '3' else '2_6M'
    campaign = ROOT / 'output' / ('phase9-mesh-convergence' if args.server == '3'
                                 else 'phase9-mesh-convergence-server4') / '20261007'
    run_path = campaign / (label + '-run.json')
    if args.server == '3':
        selected = json.loads((campaign / 'initial-bulk-final-selection.json').read_text())
        endpoint = selected['pairs']['997k']['native_iteration']
    if args.server == '4':
        final = json.loads((campaign / 'final-initial-bulk.json').read_text())
        endpoint = final['native_iteration']
        run_path = Path(final['checkpoint_proof']).parent / 'original-run.json'
    run = json.loads(run_path.read_text())
    out = ROOT / 'output/phase9-mesh-comparison/20261009' / (label + '-N' + str(endpoint))
    raw = out / 'raw'
    raw.mkdir(parents=True, exist_ok=False)
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(30)
    if args.server == '3':
        import run_phase9_mesh_startup as transport
    else:
        import run_phase9_server4_2_6M as transport
    solver = transport.attach()
    signal.alarm(0)
    result, sources = {}, {}
    for name, path in run['report_paths'].items():
        signal.alarm(25)
        content = read_text(solver, path)
        signal.alarm(0)
        (raw / (name + '.out')).write_text(content)
        rows = {}
        for line in content.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit():
                i, value = int(parts[0]), float(parts[1])
                if 1580 <= i <= endpoint:
                    if i in rows and rows[i] != value:
                        raise RuntimeError(f'Conflicting duplicate: {name} N{i}')
                    if not math.isfinite(value):
                        raise RuntimeError(f'Nonfinite selected history: {name} N{i}')
                    rows[i] = value
        if not set(range(1581, endpoint + 1)).issubset(rows):
            raise RuntimeError('Selected endpoint history incomplete: ' + name)
        result[name] = rows
        sources[name] = {'server': args.server, 'remote_path': path,
                         'raw_sha256': hashlib.sha256(content.encode()).hexdigest(),
                         'first': min(rows), 'last': max(rows), 'points': len(rows)}
        print('READ_REPORT', label, name, len(rows), flush=True)
    (out / 'histories.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / 'extraction.json').write_text(json.dumps({
        'status': 'COMPLETE_READ_ONLY', 'selected_endpoint': endpoint,
        'sources': sources, 'case_loads': 0, 'setters': 0, 'solves': 0,
        'run_receipt': str(run_path)}, indent=2) + '\n')


if __name__ == '__main__':
    main()
