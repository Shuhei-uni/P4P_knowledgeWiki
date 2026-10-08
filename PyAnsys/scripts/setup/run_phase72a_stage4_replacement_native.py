"""Native bulk-active replacement-parent holds and terminal capture."""
from pathlib import PureWindowsPath
from datetime import datetime, timezone
import argparse
import json
import math
import re
import time
import run_phase72a_stage4_replacement as r


def run_journal(work, count, end):
    return '\n'.join([
        f'/file/start-transcript "{(work / "native-run.trn").as_posix()}"',
        f'/solve/iterate {count}',
        f'/file/write-case-data "{(work / ("final-N" + str(end) + ".cas.h5")).as_posix()}"',
        f'/plot/residuals-set/plot-to-file "{(work / "residuals.xy").as_posix()}"',
        '/plot/residuals', '/plot/residuals-set/end-plot-to-file',
        f'(with-output-to-file "{(work / "returned.txt").as_posix()}" (lambda () (display "NATIVE_COMMAND_RETURNED") (newline)))',
        '/file/stop-transcript', ''])


def submit(count, checkpoint_frequency=1000):
    assert count >= 1000
    assert 0 < checkpoint_frequency <= count
    m = json.loads(r.MANIFEST.read_text())
    assert m['status'] in ['DRAIN_PROVED_READY_FOR_BULK_1000', 'CHECKPOINT_VERIFIED']
    s = r.base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    assert r.base.native_iteration(s) == m['verified_native_end']
    r.audit(s)
    start = r.base.native_iteration(s)
    end = start + count
    label = f'bulk-N{start}-N{end}'
    work, local = r.WORK / label, r.OUT / label
    local.mkdir(exist_ok=False)
    for folder in [work, work / 'monitors', work / 'scratch', work / 'checkpoints']:
        r.base.ensure_remote_directory(s, str(folder))
    autosave = r.base.native.configure_autosave(
        s, str(work / 'checkpoints'), data_frequency=checkpoint_frequency)
    paths = r.instrument(s, work / 'monitors', m['report_names'])
    before = r.snapshot(s)
    initial = r.values(s, m['report_names'])
    journal = run_journal(work, count, end)
    assert journal.count('/solve/iterate ') == 1
    r.write_ascii_text_new(s, str(work / 'native-run.jou'), journal)
    (local / 'native-run.jou').write_text(journal)
    record = {'status': 'SUBMITTING_NATIVE', 'start': start, 'target': end, 'count': count,
              'step_s': r.DT, 'before': before, 'initial_reports': initial,
              'autosave': autosave, 'checkpoint_frequency': checkpoint_frequency,
              'parent_pair': m['latest_pair'],
              'execution': 'FLUENT_OWNED_NATIVE_TUI_JOURNAL',
              'report_paths': paths, 'work': str(work), 'native_transcript': str(work / 'native-run.trn'),
              'submitted_utc': datetime.now(timezone.utc).isoformat(), 'requires_laptop_for_solve': False}
    r.base.dump(local / 'run-manifest.json', record)
    m.update(status='SUBMITTING_NATIVE', active_block=str(local.relative_to(r.ROOT.parent)), active_target=end)
    r.dump('run-manifest.json', m)
    s.transcript.start(file_name=str(local / 'submission-stream.txt'), write_to_stdout=False)
    path = (work / 'native-run.jou').as_posix()
    command = '(ti-menu-load-string "/file/read-journal \\\"' + path + '\\\"")'
    acknowledgement = s.scheme.exec((command,), wait=False, silent=False)
    m.update(status='SUBMITTED_NATIVE', acknowledgement=str(acknowledgement))
    r.dump('run-manifest.json', m)
    print('SUBMITTED_NATIVE', start, end, flush=True)
    for _ in range(10):
        time.sleep(1)
        stream = local / 'submission-stream.txt'
        if stream.exists() and 'Film time =' in stream.read_text(): break
    s.transcript.stop()


def observe(seconds):
    import grpc
    from ansys.api.fluent.v0 import transcript_pb2, transcript_pb2_grpc
    from pyansys_fluent.connection import resolve_connection_kwargs
    assert 1 <= seconds <= 60
    m = json.loads(r.MANIFEST.read_text())
    local = r.ROOT.parent / m['active_block']
    cfg = resolve_connection_kwargs('1', start_transcript=False, tcp_timeout_seconds=5)
    channel = grpc.insecure_channel(f"{cfg['ip']}:{cfg['port']}")
    chunks = []
    try:
        for response in transcript_pb2_grpc.TranscriptStub(channel).BeginStreaming(
                transcript_pb2.TranscriptRequest(), metadata=[('password', cfg['password'])], timeout=seconds):
            chunks.append(response.transcript)
    except grpc.RpcError as error:
        if error.code() != grpc.StatusCode.DEADLINE_EXCEEDED: raise
    finally:
        channel.close()
        text = ''.join(chunks)
        path = local / ('observer-' + datetime.now(timezone.utc).strftime('%H%M%S%f') + '.txt')
        path.write_text(text)
    clocks = re.findall(r'Film time = ([\deE.+-]+)', text)
    iterations = re.findall(r'^\s*(\d+)\s+[-+\deE.]+', text, re.M)
    print('PASSIVE_OBSERVATION', len(text), 'chars, last iteration', iterations[-1] if iterations else None,
          'last film clock', clocks[-1] if clocks else None,
          'terminal_seen', '/file/stop-transcript' in text, flush=True)
    print(text[-1800:], flush=True)


def capture():
    m = json.loads(r.MANIFEST.read_text())
    assert m['status'] in ['SUBMITTED_NATIVE', 'SUBMITTING_NATIVE']
    local = r.ROOT.parent / m['active_block']
    rec = json.loads((local / 'run-manifest.json').read_text())
    work = PureWindowsPath(rec['work'])
    s = r.base.attach()
    assert not s.settings.solution.run_calculation.iterating(), 'Observe passively until native solve returns'
    assert r.base.remote_file_exists(s, str(work / 'returned.txt')), 'Native command has not reached its terminal write'
    text = r.read_text(s, rec['native_transcript'])
    (local / 'native-run.trn').write_text(text)
    live = r.snapshot(s)
    live_reports = r.values(s, m['report_names'])
    h = {}
    for n, path in rec['report_paths'].items():
        raw = r.read_text(s, path)
        (local / (n + '.out')).write_text(raw)
        h[n] = r.history(raw)
    if r.base.remote_file_exists(s, str(work / 'residuals.xy')):
        (local / 'residuals.xy').write_text(r.read_text(s, str(work / 'residuals.xy')))
    pair = {'case': str(work / f"final-N{rec['target']}.cas.h5"),
            'data': str(work / f"final-N{rec['target']}.dat.h5"), 'native_iteration': live['native_iteration']}
    for kind in ['case', 'data']:
        pair[kind + '_sha256'] = r.base.checked_remote_sha256(s, pair[kind], str(work / 'scratch' / (kind + '-' + str(time.time_ns()) + '.txt')))
    rec.update(live_before_data_reopen=live, live_reports_before_data_reopen=live_reports, pair=pair)
    r.base.dump(local / 'run-manifest.json', rec)
    r.audit(s)
    # The loaded case was paired-reopen verified at preparation. Avoid repeating
    # full case reads that invoke GUI warnings in this session. Reopen the saved
    # data, then compare all controls and reports against the live endpoint.
    s.settings.file.read_data(file_name=pair['data'])
    r.audit(s)
    reopened = r.snapshot(s)
    assert reopened['native_iteration'] == live['native_iteration']
    assert reopened['parameters'] == live['parameters']
    assert reopened['walls'] == live['walls']
    assert reopened['cell_zones'] == live['cell_zones']
    assert reopened['methods'] == live['methods']
    final = reopened
    finalreports = r.values(s, m['report_names'])
    # The instantaneous Phase Accretion rate resets to zero on read-data; it is
    # not a stored inventory. Keep its terminal native history as the evidence.
    volatile = {n for n in live_reports if n.endswith('-secondary')}
    r.base.d.q.r.require_match(
        {'fields': {n: v for n, v in finalreports.items() if n not in volatile}},
        {'fields': {n: v for n, v in live_reports.items() if n not in volatile}})
    rec['source_rate_reopen_note'] = 'Instantaneous Phase Accretion rate resets on data read; use original native histories for source accounting.'
    rec['native_endpoint_reports'] = {n: [series[rec['target']], live_reports[n][1]]
                                      for n, series in h.items() if rec['target'] in series}
    r.dump(str(local.relative_to(r.OUT) / 'reopened.json'), reopened)
    printed = [tuple(map(float, x.groups())) for x in r.FILM.finditer(text)]
    if printed:
        assert math.isclose(final['film']['film_elapsed_time'], printed[-1][0], abs_tol=5e-9)
    rows_ok = all(set(range(rec['start'] + 1, rec['target'] + 1)).issubset(v) for v in h.values())
    fatal = bool(re.search(r'floating point exception|received signal|fatal error|Divergence detected', text, re.I))
    complete = final['native_iteration'] == rec['target'] and rows_ok and not fatal
    rec.update(status='CHECKPOINT_VERIFIED' if complete else 'PARTIAL_ENDPOINT_PRESERVED',
               verified_updates=final['native_iteration'] - rec['start'], history_complete=rows_ok,
               final_readback=final, final_reports=finalreports,
               fatal_solver_event=fatal, reopen='DATA_REOPEN_AND_CONTROL_REPORT_MATCH_PASS',
               case_verification='Saved case hash verified; live controls match prepared case. Final case was not reloaded to avoid GUI warnings.',
               printed_film_updates=len(printed),
               peak_courant=max(x[2] for x in printed) if printed else None,
               peak_thickness_m=max(h['p72d-total-thickness'].values()),
               added_film_time_s=final['film']['film_elapsed_time'] - rec['before']['film']['film_elapsed_time'],
               all_reports_finite=all(math.isfinite(v) for series in h.values() for v in series.values()))
    r.base.dump(local / 'run-manifest.json', rec)
    m.update(status=rec['status'], latest_pair=pair, verified_native_end=final['native_iteration'],
             verified_film_time_s=final['film']['film_elapsed_time'], active_target=None,
             new_bulk_solve_submitted=True, new_bulk_updates_verified=rec['verified_updates'],
             session_live_state='IDLE_CHECKPOINT_DATA_REOPENED', external_block=None)
    m['blocks'].append(str(local.relative_to(r.ROOT.parent)))
    r.dump('run-manifest.json', m)
    print(rec['status'], final['native_iteration'], 'film clock', final['film']['film_elapsed_time'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['submit', 'observe', 'capture', 'prove-drain', 'resume-drain'])
    p.add_argument('--count', type=int, default=1000)
    p.add_argument('--checkpoint-frequency', type=int, default=1000)
    p.add_argument('--seconds', type=int, default=30)
    a = p.parse_args()
    {'submit': lambda: submit(a.count, a.checkpoint_frequency), 'observe': lambda: observe(a.seconds), 'capture': capture,
     'prove-drain': r.prove_drain, 'resume-drain': r.resume_drain_proof}[a.action]()
