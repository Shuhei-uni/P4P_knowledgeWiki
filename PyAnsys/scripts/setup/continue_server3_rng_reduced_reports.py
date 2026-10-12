"""Reduce output for the human's live RNG swirl trial, continue to reset +2000."""
from pathlib import Path, PureWindowsPath
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_phase9_mesh_startup as r

OUT = r.ROOT / 'output/server3-report-reduction/20261009'
KEEP = {
    'p72s3-pressure-inlet', 'p72s3-pressure-outlet',
    'v2-total-liquid-mass', 'v2-lower-liquid-mass',
    'v2-flux-phase2-steamoutlet', 'v2-flux-phase1-steamoutlet',
    'v2-flux-mixture-steamoutlet', 'v2-applied-absorber',
    'p72a-e2.7-ewf-film-mass-total', 'p72a-e2.7-ewf-outflow-mass-total',
    'p72a-e2.7-ewf-thickness-max', 'p72a-e2.7-ewf-courant-max',
}
TARGET = 8080 + 2000


def swirl(s):
    return {k: v for k, v in s.rp_vars().items() if 'swirl' in k.lower()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = OUT / 'continuation.json'
    if receipt.exists():
        raise RuntimeError('Reconcile the existing continuation before resubmitting')
    s = r.attach()
    r.require_idle(s)
    start = r.native_iteration(s)
    if not 8080 <= start < TARGET:
        raise RuntimeError('Live state outside the requested continuation interval')
    folder = PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")')) / 'Documents/FluentRuns/RNG-swirl-60k' / str(time.time_ns())
    r.ensure_remote_directory(s, str(folder / 'scratch'))
    m = {'status': 'APPLYING_REPORT_REDUCTION', 'server_id': '3',
         'reset_native_iteration': 8080, 'start_native_iteration': start,
         'target_native_iteration': TARGET, 'remaining_iterations': TARGET - start,
         'swirl_before': swirl(s), 'remote_folder': str(folder),
         'authority': 'human_reduce_reports_continue_live_state_to_reset_plus_2000'}
    r.dump(receipt, m)
    s.transcript.start(file_name=str(OUT / 'continuation-transcript.txt'), write_to_stdout=False)
    try:
        files = s.settings.solution.monitor.report_files
        existing = files.get_state()
        available = {d for f in existing.values() for d in f['report_defs']}
        if not KEEP <= available:
            raise RuntimeError('Requested core reports missing')
        m['report_files_before'] = existing
        for name, state in existing.items():
            obj = files[name]
            obj.frequency = 20
            obj.print = False
            obj.active = bool(set(state['report_defs']) & KEEP)
        for name in s.settings.solution.monitor.report_plots.get_object_names():
            s.settings.solution.monitor.report_plots[name].active = False
        m['previous_reporting_interval'] = s.settings.solution.run_calculation.reporting_interval.get_state()
        s.settings.solution.run_calculation.reporting_interval = 20
        film = dict(s.rp_vars('wall-film/model-parameters'))
        m['previous_film_message'] = film['film-message?']
        film['film-message?'] = False
        s.rp_vars('wall-film/model-parameters', list(film.items()))
        m['report_files_after'] = files.get_state()
        m['reporting_interval'] = s.settings.solution.run_calculation.reporting_interval.get_state()
        m['film_message'] = dict(s.rp_vars('wall-film/model-parameters'))['film-message?']
        m['swirl_after'] = swirl(s)
        if m['swirl_after'] != m['swirl_before']:
            raise RuntimeError('Swirl setting changed')
        m['start_pair'] = r.save(s, folder, 'reduced-report-start-N' + str(start))
        s.execute_tui('/file/start-transcript "' + str(folder / 'native.trn').replace('\\', '/') + '"')
        command = '/solve/iterate ' + str(TARGET - start)
        m.update(status='NATIVE_SOLVE_SUBMITTED', command=command)
        r.dump(receipt, m)
        print('SUBMIT', command, 'START', start, 'TARGET', TARGET, flush=True)
        s.execute_tui(command)
        end = r.native_iteration(s)
        m['end_pair'] = r.save(s, folder, 'reduced-report-end-N' + str(end))
        m.update(status='COMPLETE' if end == TARGET else 'STOPPED_BEFORE_TARGET', observed_native_end=end)
        r.dump(receipt, m)
        print(m['status'], end, flush=True)
    except BaseException:
        m.update(status='EXECUTION_ERROR', error=traceback.format_exc())
        r.dump(receipt, m)
        raise
    finally:
        try:
            s.execute_tui('/file/stop-transcript')
        except Exception:
            pass
        s.transcript.stop()


if __name__ == '__main__':
    main()
