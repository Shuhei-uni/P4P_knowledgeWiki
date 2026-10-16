"""Verify/reopen the exact Server 3 terminal pair; never iterate or exit Fluent."""
from pathlib import Path, PureWindowsPath
import fcntl
import hashlib
import json
import math
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from phase9_server3_997k_common import run, attach, OUT
from pyansys_fluent import ewf_local_drain as drain


def main():
    lock = (OUT / 'controller.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest = OUT / 'run-manifest.json'
    m = json.loads(manifest.read_text())
    if m['status'] == 'COMPLETE_VERIFIED':
        assert json.loads((OUT / 'final-reopen.json').read_text())['status'] == 'PASS'
        print('ALREADY_COMPLETE_VERIFIED', flush=True)
        return
    assert m['status'] == 'COMPLETE_NATIVE_SCHEDULE_FINAL_VERIFICATION_PENDING'
    assert m['server_id'] == '3' and m['cells'] == 997604
    assert len(m['blocks']) == len(m['schedule']) == 10
    assert sum(b['count'] for b in m['blocks']) == 42820
    native, clock = 8080, m['start_film_s']
    for block, schedule in zip(m['blocks'], m['schedule']):
        assert [block['stage'], block['count'], block['step_s'], block['bulk_active']] == schedule
        assert math.isclose(block['film_start_s'], clock, abs_tol=1e-10)
        clock += block['count'] * block['step_s']
        native += block['count']
        assert block['pair']['native_iteration'] == native
        assert math.isclose(block['film_end_s'], clock, abs_tol=1e-10)
    assert native == m['verified_native_end'] == 50900
    assert math.isclose(clock, .2, abs_tol=1e-10)
    assert math.isclose(m['accepted_film_s'], .2, abs_tol=1e-10)
    pair = m['latest_pair']
    profile = str(PureWindowsPath(*PureWindowsPath(pair['case']).parts[:3]))
    s = attach(profile=profile)
    run.require_idle(s)
    assert run.native_iteration(s) == 50900
    assert math.isclose(run.film(s)['film_elapsed_time'], .2, abs_tol=1e-10)
    run.assert_bulk_active(s)
    before = run.base.state(s)
    run.dump(OUT / 'final-before-reopen.json', {'state': before, 'film': run.film(s), 'pair': pair})
    stamp = str(time.time_ns())
    scratch = run.WORK / '997k' / 'scratch'
    checkpoint_checks = []
    for block in m['blocks']:
        checked = {'stage': block['stage'], 'native_iteration': block['pair']['native_iteration']}
        for key in ['case', 'data']:
            digest = run.remote_file_sha256(s, block['pair'][key], str(scratch / f'final-check-{block["pair"]["native_iteration"]}-{key}-{stamp}.txt'))
            assert digest == block['pair'][key + '_sha256'], 'Checkpoint hash differs'
            checked[key + '_sha256'] = digest
        checkpoint_checks.append(checked)
        print('CHECKPOINT_PAIR_HASH_VERIFIED', checked['native_iteration'], flush=True)
    run.dump(OUT / 'final-checkpoint-hashes.json', checkpoint_checks)
    last = m['blocks'][-1]
    assert last['bulk_active'] and last['count'] == 1000
    transcript = run.read_text(s, pair['case'][:-7] + '.trn')
    rows = re.findall(r'Film time = ([\d.eE+-]+) with timestep = ([\d.eE+-]+), \(max_cfl: ([\d.eE+-]+)\)', transcript)
    assert len(rows) == 1000
    assert not re.search(r'floating point exception|fatal error|Divergence detected', transcript, re.I)
    previous = .195
    for row in rows:
        film, step, cfl = map(float, row)
        assert all(math.isfinite(x) for x in [film, step, cfl])
        assert math.isclose(step, 5e-6, abs_tol=1e-12)
        assert math.isclose(film - previous, step, abs_tol=1e-10)
        previous = film
    assert math.isclose(previous, .2, abs_tol=1e-10)
    assert '/file/write-case-data' in transcript and '/file/stop-transcript' in transcript
    report_checks = {}
    for name, path in m['report_paths'].items():
        text = run.read_text(s, path)
        points = []
        for line in text.splitlines():
            fields = line.split()
            if len(fields) >= 2 and fields[0].isdigit():
                value = float(fields[1])
                assert math.isfinite(value), f'Nonfinite report: {name}'
                points.append(int(fields[0]))
        assert points and points[-1] == 50900, f'Incomplete report: {name}'
        assert points == list(range(points[0], 50901)), f'Report gap/duplicate: {name}'
        assert points[0] in [49900, 49901], f'Unexpected report start: {name}'
        report_checks[name] = {'path': path, 'first': points[0], 'last': points[-1], 'rows': len(points)}
    run.dump(OUT / 'final-report-history-checks.json', report_checks)
    print('FINAL_REPORT_HISTORIES_VERIFIED', len(report_checks), flush=True)
    run.load(s, pair)
    after = run.base.state(s)
    persistent = {k: v for k, v in before['readback']['fields'].items() if 'secondary-phase-mass' not in k}
    for value in persistent.values():
        assert math.isfinite(float(value[0]))
    run.require_match({**after['readback'], 'fields': {k: after['readback']['fields'][k] for k in persistent}},
                      {**before['readback'], 'fields': persistent})
    run.require_setup_same(after['setup'], before['setup'])
    assert after['methods'] == before['methods']
    assert run.native_iteration(s) == 50900
    film = run.film(s)
    assert math.isclose(film['film_elapsed_time'], .2, abs_tol=1e-10)
    equations = run.assert_bulk_active(s)
    run.require_bulk_audit(s)
    feed = run.read_feed(s, 1.0)
    drain.audit(s, True)
    proof = {'status': 'PASS', 'server_id': '3', 'cells': 997604, 'pair': pair,
             'native_iteration': 50900, 'film_s': film['film_elapsed_time'],
             'equations': equations, 'feed': feed, 'before': before, 'after': after,
             'checkpoint_pairs_rehashed': len(checkpoint_checks), 'report_histories_verified': len(report_checks),
             'final_accepted_updates': len(rows), 'bulk_active': True,
             'persistent_fields_setup_methods_preserved': True,
             'no_new_iterations': True, 'fluent_preserved': True,
             'numerical_limit_checks_enabled': False,
             'claim_limit': 'Scheduled numerical endpoint; no steady film, mass closure, or physical validation claim.'}
    run.dump(OUT / 'final-reopen.json', proof)
    m.update(status='COMPLETE_VERIFIED', active_stage=None, active_target=None,
             final_verification=str(OUT / 'final-reopen.json'), bulk_active=True)
    run.dump(manifest, m)
    receipt = json.loads((OUT / 'desktop-controller.json').read_text())
    receipt['status'] = 'COMPLETE_VERIFIED'
    run.dump(OUT / 'desktop-controller.json', receipt)
    print('COMPLETE_VERIFIED_SERVER3_N50900_200MS', flush=True)


if __name__ == '__main__':
    main()
