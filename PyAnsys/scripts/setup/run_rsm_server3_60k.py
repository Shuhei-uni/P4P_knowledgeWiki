"""Human-directed default RSM experiment: selected Phase 9 60k parent, +2000."""
from pathlib import Path, PureWindowsPath
import json
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_phase9_mesh_startup as r

OUT = r.ROOT / 'output/rsm-server3-60k/20261009'
COMMANDS = [
    '/define/models/viscous/reynolds-stress-model yes',
    '/define/models/viscous/rsm-linear-pressure-strain yes',
    '/define/models/viscous/rsm-wall-echo yes',
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = OUT / 'run-manifest.json'
    if receipt.exists():
        raise RuntimeError('Existing run: inspect its outcome before another submission')
    s = r.attach()
    r.require_idle(s)
    folder = PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")')) / 'Documents/FluentRuns/RSM-60k' / str(time.time_ns())
    r.ensure_remote_directory(s, str(folder / 'scratch'))
    parent = json.loads((r.OUT / '60k-final-selection-N8080.json').read_text())['selected_pair']
    m = {'status': 'PREPARING', 'server_id': '3', 'parent': parent,
         'mesh_cells': 60964, 'requested_new_iterations': 2000, 'target_native_iteration': 10080,
         'authority': 'human_20261009_server3_full_ownership_default_RSM_TUI_2000',
         'guide': 'https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_rsm_setup.html',
         'commands': COMMANDS + ['/solve/iterate 2000'], 'remote_folder': str(folder),
         'runtime_note': 'Native solve runs on Server 3; local client records completion while desktop stays running.'}
    r.dump(receipt, m)
    s.transcript.start(file_name=str(OUT / 'client-transcript.txt'), write_to_stdout=False)
    try:
        m['replaced_session_pair'] = r.save(s, folder, 'prior-session')
        r.dump(receipt, m)
        r.load(s, parent)
        m['parent_film'] = r.film(s)
        m['parent_viscous'] = s.settings.setup.models.viscous.get_state()
        m['report_paths'] = r.base.instrument(s, folder / 'monitors')
        s.settings.file.auto_save.data_frequency = 0
        s.execute_tui('/file/start-transcript "' + str(folder / 'native.trn').replace('\\', '/') + '"')
        for command in COMMANDS:
            print('TUI', command, flush=True)
            s.execute_tui(command)
        m['rsm_settings'] = s.settings.setup.models.viscous.get_state()
        m['equations'] = s.settings.solution.controls.equations.get_state()
        m['methods'] = s.settings.solution.methods.get_state()
        m['controls'] = s.settings.solution.controls.get_state()
        r.dump(receipt, m)
        if m['rsm_settings']['model'] != 'reynolds-stress':
            raise RuntimeError('RSM command did not activate RSM')
        if not all(m['equations'].values()):
            raise RuntimeError('Parent contains disabled bulk equations')
        m['rsm_start_pair'] = r.save(s, folder, 'rsm-N8080')
        m.update(status='SUBMITTING_NATIVE_2000', started_utc=r.datetime.now(r.timezone.utc).isoformat())
        r.dump(receipt, m)
        print('TUI /solve/iterate 2000; START 8080; TARGET 10080', flush=True)
        s.execute_tui('/solve/iterate 2000')
        m['observed_native_end'] = r.native_iteration(s)
        m['end_film'] = r.film(s)
        m['end_pair'] = r.save(s, folder, 'rsm-end-N' + str(m['observed_native_end']))
        m['status'] = 'COMPLETE_2000' if m['observed_native_end'] == 10080 else 'STOPPED_BEFORE_TARGET'
        r.dump(receipt, m)
        print(m['status'], m['observed_native_end'], flush=True)
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
