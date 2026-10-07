"""Submit one server-owned journal; no laptop-side run controller."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_phase72a_commercial_steel_continuation as run
from pyansys_fluent.common import remote_file_exists, quote_scheme_string
from pyansys_fluent.remote_text import write_ascii_text_new


def main():
    m = json.loads(run.MANIFEST.read_text())
    if m['status'] != 'STOPPED_BY_HUMAN':
        raise RuntimeError('Reconcile existing submission before another solve')
    s = run.attach()
    assert s.settings.solution.run_calculation.iterate.is_active()
    assert run.native_iteration(s) == 25835
    clock = run.film(s)
    assert clock['max_timestep_count'] == 24255
    assert abs(clock['film_elapsed_time'] - .2652043386356889) < 1e-12
    for wall, value in run.roughness(s).items():
        assert value['roughness_height']['value'] == (0 if wall == 'bottom' else 4.5e-5)
        assert value['roughness_const']['value'] == .5
    assert all(s.settings.solution.controls.equations.get_state().values())
    params = dict(s.rp_vars('wall-film/model-parameters'))
    assert not params['ewf-adaptive?'] and params['timestep-max'] == 1e-6
    journal = str(run.WORK / 'native-continuation-N25835-N26815.jou').replace('\\', '/')
    transcript = str(run.WORK / 'native-continuation-N25835-N26815.trn').replace('\\', '/')
    case = str(run.WORK / 'native-final-N26815.cas.h5').replace('\\', '/')
    data = case.replace('.cas.h5', '.dat.h5')
    for path in [journal, transcript, case, data]:
        assert not remote_file_exists(s, path), 'Existing run artifact: ' + path
    content = '\n'.join([
        '; Native commercial-steel continuation; keep Fluent open.',
        f'/file/start-transcript "{transcript}"',
        '/solve/iterate 980',
        f'/file/write-case-data "{case}"',
        '/file/stop-transcript',
        '',
    ])
    write_ascii_text_new(s, journal, content)
    (run.OUT / 'native-continuation-N25835-N26815.jou').write_text(content)
    stream = run.OUT / 'native-submission-stream.txt'
    s.transcript.start(file_name=str(stream), write_to_stdout=False)
    m.update(status='SUBMITTING_NATIVE_TUI', execution='FLUENT_SERVER_OWNED_JOURNAL',
             authority='human_2026_10_06_resume_simple_TUI_laptop_independent',
             active_target=26815, submitted_updates=980, verified_native_start=25835,
             native_journal=journal, native_transcript=transcript,
             expected_final_pair={'case':case,'data':data},
             requires_laptop_connection=False, resume_requires_explicit_human_request=False)
    run.dump(run.MANIFEST,m)
    command = '(ti-menu-load-string "/file/read-journal \\\"' + journal + '\\\"")'
    response = s.scheme.exec((command,), wait=False, silent=False)
    m.update(status='SUBMITTED_NATIVE_TUI', native_async_acknowledgement=str(response),
             final_completion='PENDING_VERIFICATION', steady_film=False)
    run.dump(run.MANIFEST,m)
    # Observe streaming evidence only; no blocking solver-state query after submit.
    for _ in range(15):
        time.sleep(1)
        text = stream.read_text() if stream.exists() else ''
        if 'Film time =' in text and ' 25836 ' in text:
            m['native_execution_started'] = True
            run.dump(run.MANIFEST,m)
            break
    else:
        m['native_execution_started'] = 'ACKNOWLEDGED_NOT_YET_OBSERVED'
        run.dump(run.MANIFEST,m)
    s.transcript.stop()
    print(json.dumps({k:m[k] for k in ['status','native_execution_started','active_target','expected_final_pair','requires_laptop_connection']},indent=2))


if __name__ == '__main__':
    main()
