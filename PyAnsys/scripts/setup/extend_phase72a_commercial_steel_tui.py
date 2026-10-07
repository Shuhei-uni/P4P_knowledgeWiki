"""Verify the previous native endpoint and submit a server-owned continuation."""
import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_phase72a_commercial_steel_continuation as run
from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.remote_text import write_ascii_text_new, read_text
from pyansys_fluent.stage4_native import remote_file_sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iterations', type=int, required=True)
    args = parser.parse_args()
    if args.iterations <= 0:
        raise ValueError('Positive iteration count required')
    m = json.loads(run.MANIFEST.read_text())
    assert m['status'] == 'SUBMITTED_NATIVE_TUI', 'Reconcile existing execution before submitting'
    s = run.attach()
    assert s.settings.solution.run_calculation.iterate.is_active(), 'Solver is still busy'
    start = run.native_iteration(s)
    assert start == m['active_target'], 'Previous native run did not reach its target'
    clock = run.film(s)
    original = json.loads((run.OUT / 'loaded-parent.json').read_text())
    assert clock['max_timestep_count'] == original['film']['max_timestep_count'] + start - 25815
    for wall, settings in run.roughness(s).items():
        assert settings['roughness_height']['value'] == (0 if wall == 'bottom' else 4.5e-5)
        assert settings['roughness_const']['value'] == .5
    assert all(s.settings.solution.controls.equations.get_state().values())
    params = dict(s.rp_vars('wall-film/model-parameters'))
    assert not params['ewf-adaptive?'] and params['timestep-max'] == 1e-6
    pair = dict(m['expected_final_pair'], native_iteration=start)
    for kind in ['case', 'data']:
        assert remote_file_exists(s, pair[kind]), 'Previous endpoint save missing'
        pair[kind + '_sha256'] = remote_file_sha256(s, pair[kind], str(run.WORK / 'scratch' / f'extend-N{start}-{kind}.sha256'))
    prior_text = read_text(s, m['native_transcript'])
    (run.OUT / f'native-continuation-N{m["verified_native_start"]}-N{start}.trn').write_text(prior_text)
    # Verify native endpoint write and completion from the server transcript.
    assert f' {start} ' in prior_text and 'Done.' in prior_text
    endpoint = {'pair':pair, 'native_iteration':start, 'film':clock,
                'readback':run.state(s)['readback'],
                'terminal_status':'NATIVE_TARGET_AND_PAIRED_FILES_HASH_VERIFIED',
                'reopen':'NOT_REPEATED_BEFORE_EXTENSION'}
    run.dump(run.OUT / f'native-completed-N{start}.json', endpoint)
    end = start + args.iterations
    tag = f'native-continuation-N{start}-N{end}'
    journal = str(run.WORK / f'{tag}.jou').replace('\\', '/')
    transcript = str(run.WORK / f'{tag}.trn').replace('\\', '/')
    case = str(run.WORK / f'native-final-N{end}.cas.h5').replace('\\', '/')
    data = case.replace('.cas.h5', '.dat.h5')
    for path in [journal, transcript, case, data]:
        assert not remote_file_exists(s, path), 'Existing run artifact; do not submit twice'
    content = '\n'.join([
        '; Server-owned continuation; keep Fluent open.',
        f'/file/start-transcript "{transcript}"',
        f'/solve/iterate {args.iterations}',
        f'/file/write-case-data "{case}"',
        '/file/stop-transcript',
        '',
    ])
    write_ascii_text_new(s, journal, content)
    (run.OUT / f'{tag}.jou').write_text(content)
    stream = run.OUT / f'{tag}-submission-stream.txt'
    assert not stream.exists()
    s.transcript.start(file_name=str(stream), write_to_stdout=False)
    m.setdefault('verified_native_segments', []).append({
        'native_start':m['verified_native_start'], 'native_end':start,
        'updates':start-m['verified_native_start'], 'pair':pair,
        'native_transcript':m['native_transcript'], 'completion':'TARGET_AND_PAIRED_FILES_VERIFIED'})
    m.pop('error', None)
    m.update(status='SUBMITTING_NATIVE_TUI',
             authority='human_2026_10_07_additional_3000_native_iterations',
             active_target=end, submitted_updates=args.iterations, verified_native_start=start,
             verified_native_end=start, last_observed_native_iteration=start,
             completed_updates=start-25815, remaining_updates=args.iterations,
             latest_pair=pair, latest_saved_pair=pair, film_time_s=clock['film_elapsed_time'],
             native_journal=journal, native_transcript=transcript,
             expected_final_pair={'case':case,'data':data},
             requires_laptop_connection=False, final_completion='PENDING_VERIFICATION',
             native_execution_started=False)
    run.dump(run.MANIFEST,m)
    command = '(ti-menu-load-string "/file/read-journal \\\"' + journal + '\\\"")'
    response = s.scheme.exec((command,), wait=False, silent=False)
    m.update(status='SUBMITTED_NATIVE_TUI', native_async_acknowledgement=str(response), live_idle=False)
    run.dump(run.MANIFEST,m)
    for _ in range(15):
        time.sleep(1)
        text = stream.read_text() if stream.exists() else ''
        rows = [int(x) for x in re.findall(r'^\s*(\d+)\s+[\d.+-]+e[+-]\d+\s+',text,re.M)]
        if rows and max(rows) > start and 'Film time =' in text:
            m.update(native_execution_started=True, last_streamed_native_iteration=max(rows))
            run.dump(run.MANIFEST,m)
            break
    s.transcript.stop()
    # Stream flush can make the first observed rows available at stop.
    text = stream.read_text() if stream.exists() else ''
    rows = [int(x) for x in re.findall(r'^\s*(\d+)\s+[\d.+-]+e[+-]\d+\s+',text,re.M)]
    if rows and max(rows) > start:
        m.update(native_execution_started=True, last_streamed_native_iteration=max(rows))
        run.dump(run.MANIFEST,m)
    print(json.dumps({k:m[k] for k in ['status','verified_native_start','active_target','submitted_updates','native_execution_started','expected_final_pair']},indent=2))


if __name__ == '__main__':
    main()
