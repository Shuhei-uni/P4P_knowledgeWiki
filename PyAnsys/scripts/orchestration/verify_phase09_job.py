"""Verify one bounded Phase 9 run and analyse it before the completion handoff."""
from pathlib import Path
import argparse
import json
import subprocess
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--start', type=int, required=True)
    p.add_argument('--iterations', type=int, required=True)
    args = p.parse_args()
    manifest = Path(json.loads(args.receipt.read_text())['run_manifest'])
    r = json.loads(manifest.read_text())
    out = manifest.parent
    # Analyse preserved stops too; an incomplete horizon remains BLOCKED.
    if (out / 'native-history.out').is_file() and (out / 'native-transcript.trn').is_file():
        subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] /
                        'analysis/analyze_phase09_block.py'), str(out)], check=True)
    assert r['status'] == 'BLOCK_COMPLETE', r
    assert r['start_iteration'] == args.start
    assert r['completed_iterations'] == args.iterations
    assert r['end_iteration'] == args.start + args.iterations
    assert r['pair_exists'] and not r['iterating']
    assert not r.get('capture_error') and not r.get('stop_reason')
    for name in ['native-history.out', 'native-transcript.trn',
                 'iteration-evidence.jsonl', 'analysis.json',
                 f'fields-n{args.start:05d}.npz',
                 f'fields-n{r["end_iteration"]:05d}.npz']:
        assert (out / name).is_file() and (out / name).stat().st_size > 0, name
    sections = json.loads((out / 'terminal-sections/index.json').read_text())
    assert set(sections['sections']) == {'p9-section-x0', 'p9-section-z0'}
    for item in sections['sections'].values():
        assert item['facets'] > 0 and (out / 'terminal-sections' / item['file']).is_file()
    print('Verified requested horizon, endpoint pair receipt, native histories, fields and sections.')
    print('Execution complete; scientific qualification is a separate decision.')


if __name__ == '__main__':
    main()
