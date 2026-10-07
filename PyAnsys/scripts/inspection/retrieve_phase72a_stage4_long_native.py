"""Read the necessary saved Stage 4 evidence directly through Fluent.

No archive, compression, shell command, solve, or case/data replacement.
Raw copies must reproduce the previously recorded server SHA-256 exactly.
"""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.remote_text import read_text
import run_phase72a_stage4_ewf_drain as drain_run
import submit_phase72a_stage4_long_native as job

EXTRA = {
    'v2-total-liquid-mass', 'v2-flux-phase2-steamoutlet',
    'v2-flux-phase1-steamoutlet', 'p72a-e2.7-ewf-velocity-mag-max',
    'p72a-e2.7-ewf-velocity-mag-awavg', 'p72a-e2.7-ewf-thickness-awavg',
}
NATIVE = {'native-status.scm', 'native-long-run.jou', 'native-run.scm', 'native-long-run.trn'}


def chunked_text(solver, path):
    """Bound memory and message size while reading a larger native text file."""
    quoted = quote_scheme_string(path)
    solver.scheme.eval('(define p72retrieval-input (open-input-file "' + quoted + '"))')
    chunks = []
    expression = (
        "(let loop ((chars '()) (n 0)) "
        "(if (= n 131072) (list->string (reverse chars)) "
        "(let ((c (read-char p72retrieval-input))) "
        "(if (eof-object? c) (list->string (reverse chars)) "
        "(loop (cons c chars) (+ n 1))))))"
    )
    try:
        while True:
            part = solver.scheme.eval(expression)
            if not isinstance(part, str):
                raise RuntimeError('Non-text native file chunk')
            if not part:
                break
            chunks.append(part)
    finally:
        solver.scheme.eval('(close-input-port p72retrieval-input)')
    return ''.join(chunks)


def exact_bytes(text, record):
    """Account for Windows text-mode newline translation; require exact hash."""
    contents = text.encode('ascii')
    candidates = [contents, contents.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')]
    for candidate in candidates:
        if len(candidate) == record['bytes'] and hashlib.sha256(candidate).hexdigest() == record['sha256']:
            return candidate
    raise ValueError('Direct native copy does not match server bytes/hash: ' + record['path'])


def main():
    stop = json.loads((job.OUT / 'inspection/check-20261008.json').read_text())
    assert 'NUMERICAL_REJECTED' in stop['state'] and '27000' in stop['state']
    solver = drain_run.attach()
    folder = job.OUT / 'retrieval-20261008'
    folder.mkdir(exist_ok=True)
    remote = job.WORK.as_posix()
    # Metadata was successfully written before the previous archive operation
    # failed. Reading it requires no new remote export or shell command.
    meta = json.loads(read_text(solver, remote + '/scratch/terminal-evidence-20261008.json'))
    selected = []
    for record in meta['sources']:
        record = dict(record)
        record['path'] = record['path'].replace('\\', '/')
        name = Path(record['path']).stem
        if name.startswith('p72d-') or name in EXTRA or record['path'] in NATIVE:
            selected.append(record)
    raw = job.OUT / 'raw/terminal-N68483'
    raw.mkdir(parents=True, exist_ok=True)
    completed = []
    for record in selected:
        target = raw / record['path']
        assert target.resolve().is_relative_to(raw.resolve())
        if target.exists():
            contents = target.read_bytes()
            assert len(contents) == record['bytes']
            assert hashlib.sha256(contents).hexdigest() == record['sha256']
        else:
            path = remote + '/' + record['path']
            text = chunked_text(solver, path) if record['bytes'] > 2_000_000 else read_text(solver, path)
            contents = exact_bytes(text, record)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contents)
        completed.append(record)
        print('DIRECT_READ_HASH_VERIFIED ' + record['path'], flush=True)
    for kind in ['case', 'data']:
        expected = json.loads(job.MANIFEST.read_text())['prepared_pair'][kind + '_sha256']
        extension = 'cas.h5' if kind == 'case' else 'dat.h5'
        observed = next(p['sha256'] for p in meta['pairs'] if p['path'].endswith('prepared-N41483.' + extension))
        assert observed == expected
    (folder / 'export-metadata.json').write_text(json.dumps(meta, indent=2) + '\n')
    receipt = dict(
        status='TERMINAL_NECESSARY_NATIVE_FILES_DIRECTLY_RETRIEVED_HASH_VERIFIED',
        native_status=stop['state'], source_count=len(completed), sources=completed,
        raw_directory=str(raw), pair_metadata=meta['pairs'],
        transfer='DIRECT_NATIVE_TEXT_READ_NO_ARCHIVE',
        no_solve_issued=True, no_case_data_replaced=True)
    (folder / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ['status','source_count','transfer','no_solve_issued']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
