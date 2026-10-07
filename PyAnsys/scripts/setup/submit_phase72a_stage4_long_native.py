"""Prepare and submit a Fluent-owned, guarded long EWF continuation.

Python transfers and verifies the setup, then exits. All iteration, guards,
checkpoints, progress and final writes execute in Fluent Scheme/TUI on Server 1.
"""
from pathlib import Path, PureWindowsPath
import argparse, json, sys, time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/setup'), str(ROOT / 'src')]
import run_phase72a_stage4_ewf_drain as d
from pyansys_fluent.remote_text import write_ascii_text_new, read_text
from pyansys_fluent.common import remote_file_exists, quote_scheme_string
from pyansys_fluent.stage4_native import ensure_remote_directory, configure_autosave, remote_file_sha256, normalized_windows_path

OUT = ROOT / 'output/phase72a-stage4-ewf-long-native/20261007'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\ewf-long-20261007')
MANIFEST = OUT / 'run-manifest.json'
START, COUNT, BLOCK, DT = 41483, 200000, 1000, 15e-6


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def native_code():
    root = WORK.as_posix()
    return r'''; Fluent-native long EWF job. No client-side controller.
(define p72l-root "ROOT")
(define p72l-start 41483)
(define p72l-total 200000)
(define p72l-block 1000)
(define p72l-completed 0)
(define p72l-status "PREPARED")
(define p72l-h '())
(define p72l-c '())
; Single-report files contain quoted headers followed by iteration/value pairs.
; Scan every saved sample, including earlier peaks that later disappear.
(define (p72l-scan path)
  (if (not (file-exists? path))
      (list -1 -1 0 0 #f)
      (let ((p (open-input-file path)))
        (let loop ((first -1) (last -1) (n 0) (peak 0) (valid #t))
          (let ((token (read p)))
            (cond
              ((eof-object? token)
               (close-input-port p) (list first last n peak valid))
              ((number? token)
               (let ((value (read p)))
                 (if (and (integer? token) (number? value)
                          (= value value) (>= value 0) (< value 1e100))
                     (loop (if (= n 0) token first) token (+ n 1)
                           (max peak value)
                           (and valid (or (= n 0) (= token (+ last 1)))))
                     (begin (close-input-port p)
                            (list first last n peak #f)))))
              ((or (string? token) (pair? token))
               (loop first last n peak valid))
              (else (close-input-port p) (list first last n peak #f))))))))
(define (p72l-history-complete? state target)
  (and (list-ref state 4)
       (or (= (car state) p72l-start) (= (car state) (+ p72l-start 1)))
       (= (list-ref state 1) target)
       (= (list-ref state 2) (+ 1 (- target (car state))))))
(define (p72l-classify h c target)
  (cond
    ((>= (list-ref h 3) 0.3) "UNREALISTIC")
    ((not (and (p72l-history-complete? h target)
               (p72l-history-complete? c target))) "EVIDENCE_OR_SOLVER_STOP")
    ((>= (list-ref c 3) 1.0) "NUMERICAL_REJECTED")
    (else "RUNNING")))
(define (p72l-progress)
  (with-output-to-file (string-append p72l-root "/native-status.scm")
    (lambda ()
      (write (list
        (cons 'status p72l-status)
        (cons 'completed-updates p72l-completed)
        (cons 'target-iteration (+ p72l-start p72l-total))
        (cons 'fixed-film-step-s 0.000015)
        (cons 'thickness-history p72l-h)
        (cons 'courant-history p72l-c)
        (cons 'requires-client #f)))
      (newline))))
(define (p72l-write-pair label)
  (ti-menu-load-string
    (string-append "/file/write-case-data \"" p72l-root "/" label ".cas.h5\"")))
(define (p72l-run)
  (set! p72l-completed 0)
  (set! p72l-status "RUNNING")
  (p72l-progress)
  (let loop ()
    (if (and (string=? p72l-status "RUNNING") (< p72l-completed p72l-total))
      (begin
        (ti-menu-load-string "/solve/iterate 1000")
        (set! p72l-completed (+ p72l-completed p72l-block))
        (set! p72l-h (p72l-scan
          (string-append p72l-root "/monitors/p72d-total-thickness.out")))
        (set! p72l-c (p72l-scan
          (string-append p72l-root "/monitors/p72d-total-courant.out")))
        (set! p72l-status (p72l-classify p72l-h p72l-c
          (+ p72l-start p72l-completed)))
        (p72l-progress)
        (display "P72L_NATIVE_PROGRESS ")
        (write (list p72l-status p72l-completed p72l-h p72l-c)) (newline)
        (loop))))
  (if (string=? p72l-status "RUNNING")
      (begin
        (p72l-write-pair "final-N241483")
        (set! p72l-status "HORIZON_REACHED_PENDING_VERIFICATION"))
      (p72l-write-pair "rejected-preserved"))
  (p72l-progress)
  (if (string=? p72l-status "UNREALISTIC")
      (with-output-to-file (string-append p72l-root "/UNREALISTIC.txt")
        (lambda () (display "A native film sample reached 0.3 m. Further solve blocks stopped.") (newline))))
  (ti-menu-load-string "/file/stop-transcript"))
'''.replace('ROOT', root)


def prepare():
    if MANIFEST.exists():
        prior = json.loads(MANIFEST.read_text())
        assert prior['status'] == 'PREPARING', 'Do not prepare or resubmit an existing native job'
    s = d.attach()
    assert s.settings.solution.run_calculation.iterate.is_active()
    assert d.q.r.parent.native_iteration(s) == START
    d.q.r.audit(s); d.drain.audit(s, 1)
    before = d.q.r.state(s)
    clock = d.q.r.film(s)
    parent = json.loads(d.MANIFEST.read_text())['branches']['on']['final_pair']
    m = dict(status='PREPARING', server_id='1', parent_pair=parent,
             parent_native_iteration=START, parent_film_time_s=clock['film_elapsed_time'],
             submitted_updates=COUNT, target_native_iteration=START + COUNT,
             added_target_film_time_s=COUNT * DT,
             target_film_time_s=clock['film_elapsed_time'] + COUNT * DT,
             fixed_film_step_s=DT, native_block_updates=BLOCK,
             requires_laptop_connection=False, execution='FLUENT_NATIVE_SCHEME_TUI',
             work_root=str(WORK), initialization='FORBIDDEN', bulk_equations_frozen=True,
             flow_momentum_coupling=False, drain_enabled=1, drain_capture_time_s=.0015,
             unrealistic_if_any_native_thickness_gte_m=.3, reject_if_any_native_courant_gte=1,
             guard_frequency_updates=BLOCK, guard_scope='ALL_SAMPLES_SINCE_NATIVE_START',
             steady_film='PENDING_ANALYSIS', final_completion='PENDING_VERIFICATION')
    dump(MANIFEST, m)
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors', WORK / 'checkpoints']:
        ensure_remote_directory(s, str(folder))
    # Keep the proven physical/numerical setup; retarget only output ownership.
    m['report_paths'] = d.instrument(s, WORK / 'monitors')
    m['autosave'] = configure_autosave(s, str(WORK / 'checkpoints'), data_frequency=5000)
    s.settings.file.auto_save.max_files = 12
    s.settings.solution.monitor.residual.options.plot = False
    m['autosave'] = s.settings.file.auto_save.get_state()
    assert m['autosave']['max_files'] == 12
    d.q.r.WORK = WORK
    case = WORK / 'prepared-N41483.cas.h5'
    data = WORK / 'prepared-N41483.dat.h5'
    if remote_file_exists(s, str(case)):
        assert remote_file_exists(s, str(data))
        pair = dict(case=str(case), data=str(data), native_iteration=START,
            case_sha256=remote_file_sha256(s, str(case), str(WORK / 'scratch/reconciled-case.sha256.txt')),
            data_sha256=remote_file_sha256(s, str(data), str(WORK / 'scratch/reconciled-data.sha256.txt')))
    else:
        pair = d.q.r.save(s, 'prepared-N41483')
    m['prepared_pair'] = pair
    dump(MANIFEST, m)
    m['prepared_reopen'] = d.reopen_pair(s, pair, 1)
    reopened_clock = d.q.r.film(s)
    # Native read-case can refresh the cached particle injection span. Stored
    # clock/counter/step and configured DPM controls must remain unchanged.
    assert all(reopened_clock[k] == clock[k] for k in clock if k != 'injection_interval')
    m['native_runtime_cache_readback'] = dict(before=clock, reopened=reopened_clock,
        original_verified_parent_injection_interval_s=6e-5,
        note='Native case reopen refreshed cached injection span; configured model/method controls and film clock/counter/step retained')
    after = d.q.r.state(s)
    assert before['setup'] == after['setup'] and before['methods'] == after['methods']
    d.persistent_reports_match(before['readback']['fields'], after['readback']['fields'])
    report_files = s.settings.solution.monitor.report_files.get_state()
    updates = {name: {'file_name': (WORK / 'monitors' / (v['report_defs'][0] + '.out')).as_posix()}
               for name, v in report_files.items() if v['active']}
    s.settings.solution.monitor.report_files.set_state(updates)
    m['report_paths'] = {v['report_defs'][0]: updates[name]['file_name']
                        for name, v in report_files.items() if v['active']}
    files_by_definition = {v['report_defs'][0]: v for v in
        s.settings.solution.monitor.report_files.get_state().values() if v['active']}
    for name, path in m['report_paths'].items():
        assert normalized_windows_path(files_by_definition[name]['file_name']) == normalized_windows_path(path)
    assert s.settings.file.auto_save.get_state() == m['autosave']
    dump(OUT / 'prepared-readback.json', dict(film=reopened_clock, audit=d.q.r.audit(s),
        drain=d.drain.audit(s, 1), state=after,
        reports=s.settings.solution.report_definitions.get_state(),
        report_files=s.settings.solution.monitor.report_files.get_state(), autosave=m['autosave']))
    finish_native_setup(s, m)


def finish_native_setup(s, m):
    code = native_code()
    scm = WORK / 'native-run.scm'
    journal = WORK / 'native-long-run.jou'
    transcript = WORK / 'native-long-run.trn'
    content = '\n'.join([
        '; Server 1: native long EWF development, parent N41483.',
        f'/file/start-transcript "{transcript.as_posix()}"',
        f'(load "{scm.as_posix()}")', '(p72l-run)', '',
    ])
    write_ascii_text_new(s, str(scm), code)
    write_ascii_text_new(s, str(journal), content)
    (OUT / scm.name).write_text(code)
    (OUT / journal.name).write_text(content)
    s.scheme.eval(f'(load "{scm.as_posix()}")')
    # Native scanner/decision proof: exact Fluent-format headers and samples.
    fixture = WORK / 'guard-proof.out'
    write_ascii_text_new(s, str(fixture), '"test"\n"Iteration" "test"\n("Iteration" "test")\n41483 0.01\n41484 0.3\n41485 0.02\n')
    scan = s.scheme.eval(f'(p72l-scan "{fixture.as_posix()}")')
    assert scan == [41483, 41485, 3, .3, True], scan
    classification = s.scheme.eval('(p72l-classify (list 41483 41485 3 .3 #t) (list 41483 41485 3 .1 #t) 41485)')
    assert classification == 'UNREALISTIC'
    healthy = s.scheme.eval('(p72l-classify (list 41483 42483 1001 .002 #t) (list 41483 42483 1001 .05 #t) 42483)')
    assert healthy == 'RUNNING'
    missing = s.scheme.eval('(p72l-classify (list 41483 42482 1000 .002 #t) (list 41483 42483 1001 .05 #t) 42483)')
    assert missing == 'EVIDENCE_OR_SOLVER_STOP'
    numerical = s.scheme.eval('(p72l-classify (list 41483 42483 1001 .002 #t) (list 41483 42483 1001 1.0 #t) 42483)')
    assert numerical == 'NUMERICAL_REJECTED'
    # Progress is overwritten by Fluent at every block; prove this native I/O
    # before relying on a long detached run.
    s.scheme.eval('(p72l-progress)')
    first_status = read_text(s, str(WORK / 'native-status.scm'))
    s.scheme.eval('(p72l-progress)')
    assert read_text(s, str(WORK / 'native-status.scm')) == first_status
    m.update(status='PREPARED_NATIVE_VERIFIED', native_journal=str(journal),
             native_scheme=str(scm), native_transcript=str(transcript),
             native_status_file=str(WORK / 'native-status.scm'),
             native_guard_proof=dict(scan=scan, peak_followed_by_recovery=classification,
                                    healthy=healthy, short_history=missing, courant_limit=numerical,
                                    native_progress_overwrite='PASS'),
             expected_final_pair=dict(case=str(WORK / 'final-N241483.cas.h5'),
                                      data=str(WORK / 'final-N241483.dat.h5')))
    dump(MANIFEST, m)
    print('PREPARED_NATIVE_VERIFIED', json.dumps(m['native_guard_proof']), flush=True)


def finish_prepared():
    """Reconcile a saved child after a readback-only client failure; zero solves."""
    import numpy as np
    m = json.loads(MANIFEST.read_text())
    assert m['status'] == 'PREPARING' and 'prepared_pair' in m
    s = d.attach()
    assert s.settings.solution.run_calculation.iterate.is_active()
    assert d.q.r.parent.native_iteration(s) == START
    before_setup = s.settings.setup.get_state()
    before_methods = s.settings.solution.methods.get_state()
    d.load_pair(s, m['prepared_pair'])
    audit = d.q.r.audit(s); source = d.drain.audit(s, 1)
    actual_clock = d.q.r.film(s)
    original = json.loads((d.OUT / 'verification.json').read_text())
    assert all(actual_clock[k] == original['film'][k] for k in actual_clock if k != 'injection_interval')
    assert s.settings.setup.get_state() == before_setup
    assert s.settings.solution.methods.get_state() == before_methods
    values = d.compute(s, d.BULK + ['p72d-total-mass', 'p72d-total-thickness', 'p72d-total-courant'])
    d.q.r.require_match({'fields': {k: values[k] for k in original['bulk']}}, {'fields': original['bulk']})
    facet_proof = {}
    for wall, label in [('wall', 'upper'), ('wall:004', 'lower')]:
        expected = dict(np.load(d.OUT / 'on' / (label + '-endpoint.npz')))
        d.same_facets(expected, d.facets(s, wall))
        facet_proof[label] = 'EXACT_STORED_NATIVE_FILM_MASS_THICKNESS_XYZ_VELOCITY'
    report_files = s.settings.solution.monitor.report_files.get_state()
    # Fluent converts report paths to relative paths on case read. Restore
    # explicit absolute POSIX paths after reopen; this changes no film setting.
    updates = {name: {'file_name': (WORK / 'monitors' / (v['report_defs'][0] + '.out')).as_posix()}
               for name, v in report_files.items() if v['active']}
    s.settings.solution.monitor.report_files.set_state(updates)
    m['report_paths'] = {v['report_defs'][0]: updates[name]['file_name']
                        for name, v in report_files.items() if v['active']}
    report_files = s.settings.solution.monitor.report_files.get_state()
    files_by_definition = {v['report_defs'][0]: v for v in report_files.values() if v['active']}
    for name, path in m['report_paths'].items():
        assert normalized_windows_path(files_by_definition[name]['file_name']) == normalized_windows_path(path)
        assert files_by_definition[name]['frequency'] == 1
    assert s.settings.file.auto_save.get_state() == m['autosave']
    m['prepared_reopen'] = 'PASS_NATIVE_CASE_DATA_FIELDS_SETTINGS_CLOCK_COUNTER'
    m['facet_preservation'] = facet_proof
    m['native_runtime_cache_readback'] = dict(original_verified_parent=original['film'], reopened=actual_clock,
        note='Native case reopen refreshed cached particle injection span; configured controls and stored film clock/counter/step retained')
    dump(MANIFEST, m)
    dump(OUT / 'prepared-readback.json', dict(film=actual_clock, audit=audit, drain=source,
        setup=before_setup, methods=before_methods, reports=s.settings.solution.report_definitions.get_state(),
        report_files=report_files, autosave=m['autosave'], fields=values, facet_preservation=facet_proof))
    finish_native_setup(s, m)


def submit():
    m = json.loads(MANIFEST.read_text())
    assert m['status'] == 'PREPARED_NATIVE_VERIFIED', 'Never duplicate a native submission'
    s = d.attach()
    assert s.settings.solution.run_calculation.iterate.is_active()
    assert d.q.r.parent.native_iteration(s) == START
    d.q.r.audit(s); d.drain.audit(s, 1)
    assert s.settings.file.auto_save.get_state() == m['autosave']
    files_by_definition = {v['report_defs'][0]: v for v in
        s.settings.solution.monitor.report_files.get_state().values() if v['active']}
    for name, path in m['report_paths'].items():
        assert normalized_windows_path(files_by_definition[name]['file_name']) == normalized_windows_path(path)
        assert not remote_file_exists(s, path), 'Unexpected prior report history: ' + path
    stream = OUT / 'submission-stream.txt'
    s.transcript.start(file_name=str(stream), write_to_stdout=False)
    m['status'] = 'SUBMITTING_NATIVE_TUI'; dump(MANIFEST, m)
    journal = m['native_journal'].replace('\\', '/')
    command = '(ti-menu-load-string "/file/read-journal \\\"' + journal + '\\\"")'
    response = s.scheme.exec((command,), wait=False, silent=False)
    m.update(status='SUBMITTED_NATIVE_TUI', native_async_acknowledgement=str(response))
    dump(MANIFEST, m)
    # A bounded stream observation only; no Python solve/control loop remains.
    for _ in range(30):
        time.sleep(1)
        raw = stream.read_text() if stream.exists() else ''
        if 'Film time =' in raw:
            m['native_execution_started'] = True
            m['submission_stream_observed_bytes'] = len(raw)
            break
    else:
        m['native_execution_started'] = 'ACKNOWLEDGED_NOT_YET_OBSERVED'
    dump(MANIFEST, m)
    s.transcript.stop()
    print(json.dumps({k: m[k] for k in ['status', 'native_execution_started',
          'target_native_iteration', 'target_film_time_s', 'requires_laptop_connection']}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'finish-prepared', 'submit'])
    args = parser.parse_args()
    {'prepare': prepare, 'finish-prepared': finish_prepared, 'submit': submit}[args.action]()
