"""Caller-owned local 60k EWF development using the reviewed staged method.

No launch, exit or remote attachment. The caller supplies the live direct-use
session after loading and hash-verifying the original N8000 pair. Local disk
replaces remote transport; scientific gates and native journals are reused.
"""
from pathlib import Path, PureWindowsPath
import hashlib
import json
import math
import os
import threading
import time

import run_phase72a_staged_ewf as staged
from run_phase72a_staged_ewf import r, policy, write


class LocalObserver:
    """Native disk transcript is the observation route; never query Server 1."""
    def __init__(self, *_args):
        self.thread = threading.Thread(target=lambda: None)

    def stop(self):
        self.thread.join(timeout=1)


def install_local_transport():
    """Process-local adapters; existing remote controllers are unaffected."""
    def mkdir(_s, path):
        Path(path).mkdir(parents=True, exist_ok=True)

    def sha(_s, path, _scratch):
        with Path(path).open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()

    def create(_s, path, content):
        with Path(path).open('x', encoding='ascii') as stream:
            stream.write(content)

    r.base.ensure_remote_directory = mkdir
    r.base.remote_file_exists = lambda _s, path: Path(path).is_file()
    r.base.checked_remote_sha256 = sha
    r.read_text = lambda _s, path: Path(path).read_text(errors='replace')
    r.write_ascii_text_new = create
    staged.PassiveProgress = LocalObserver
    r.instrument = instrument_local


def instrument_local(s, folder, names):
    """Set native monitor states in batches; verify the selected writers."""
    Path(str(folder)).mkdir(parents=True, exist_ok=True)
    files = s.settings.solution.monitor.report_files
    existing = set(files.get_object_names())
    if existing:
        files.set_state({name: {'active': False} for name in existing})
    paths, changes = {}, {}
    for name in names:
        # Fresh writers avoid v252 retaining a saved writer's old directory.
        # Unique basenames use Fluent's unchanged local working directory.
        writer = 'replacement-' + folder.parent.name + '-' + name
        if writer not in existing:
            files.create(name=writer)
        monitor_name = 'monitor-' + folder.parent.name + '-' + name + '.out'
        path = (folder.parents[2] / monitor_name).as_posix()
        if Path(path).exists():
            raise RuntimeError('Native monitor file already exists: '+path)
        changes[writer] = {'report_defs': [name], 'file_name': monitor_name,
                           'frequency_of': 'iteration', 'frequency': 1, 'active': True}
        paths[name] = path
    files.set_state(changes)
    actual = files.get_state()
    if {n for n, v in actual.items() if v['active']} != set(changes):
        raise RuntimeError('Native active monitor writers differ')
    for name, state in changes.items():
        for key, value in state.items():
            observed = actual[name][key]
            if key == 'file_name':
                observed = Path(observed.strip('"').replace(chr(92), '/'))
                if not observed.is_absolute():
                    observed = Path(str(folder)).parents[2] / observed
                matches = observed.resolve() == Path(paths[state['report_defs'][0]]).resolve()
            else:
                matches = observed == value
            if not matches:
                raise RuntimeError(f'Native monitor controls differ: {name} / {key}: {observed!r} != {value!r}')
    plots = s.settings.solution.monitor.report_plots
    plot_names = plots.get_object_names()
    if plot_names:
        plots.set_state({name: {'active': False} for name in plot_names})
    return paths


class DirectDevelopment(staged.Runner):
    def __init__(self, solver, work, output, parent_pair):
        install_local_transport()
        state = r.snapshot(solver)
        if state['native_iteration'] != 8000:
            raise RuntimeError('Fresh direct development requires the original N8000')
        if not all(state['equations'].values()):
            raise RuntimeError('Original bulk equations must be active')
        for kind in ('case', 'data'):
            digest = r.base.checked_remote_sha256(solver, parent_pair[kind], None)
            if digest != parent_pair[kind+'_sha256']:
                raise RuntimeError('Original pair hash differs')
        production = dict(state['parameters'])
        required = {name: True for name in [
            'solve-wallfilm?', 'solve-momentum?', 'mom-equation?',
            'mom-gravity?', 'mom-aero-drive?', 'mom-wall-visc?', 'mom-pressure?',
            'mom-spreading?', 'mom-advection?', 'surface-tension?',
            'dpm-collection?', 'dpm-splashing?', 'film-separation?',
            'film-stripping?', 'film-coupled-solution?']}
        required.update({'secondary-phase-mode': 1, 'ewf-adaptive?': False,
                         'thickness-limit': .3, 'sub-iter-stop': 1e-5})
        if not set(required).issubset(production):
            raise RuntimeError('Version-matched production controls unavailable')
        production.update(required)
        production.update(policy.refresh_plan(1e-6))
        spec = {
            'work': str(work), 'output': str(output), 'server_id': 'direct-local',
            'native_cells': 60964, 'parent_pair': {**parent_pair, 'native_iteration': 8000},
            'original_equations': state['equations'],
            'original_parameters': state['parameters'],
            'original_cell_zones': state['cell_zones'],
            'original_expression_definitions': {
                name: value['definition'] for name, value in state['expressions'].items()},
            'original_film_clock_s': state['film']['film_elapsed_time'],
            'production_parameters': production,
            'liquid_feed_kg_s': 116.92,
        }
        super().__init__(spec)
        self.s = solver
        self.local_work = Path(work)
        write(self.out/'original-parent-readback.json', state)
        write(self.out/'job.json', spec)
        self.flush(server_id='direct-local', host=os.environ['COMPUTERNAME'],
                   authority='human_20261008_keep_testing_until_reliable_300ms',
                   target_added_film_time_s=.3, original_parent_pair=parent_pair,
                   remote_server1_mutated=False,
                   observation_route='LOCAL_NATIVE_TRANSCRIPTS_NO_REMOTE_RPC',
                   claim_limit='Declared-age developed film; steady state and timestep independence unqualified')

    def load_original(self):
        """Parent already loaded by caller; no redundant file load or initialization."""
        self.idle()
        if r.base.native_iteration(self.s) != 8000:
            raise RuntimeError('Loaded original parent has changed')
        if dict(self.s.rp_vars('wall-film/model-parameters')) != self.spec['original_parameters']:
            raise RuntimeError('Original controls changed before startup')
        self.dt = self.spec['original_parameters']['timestep-max']
        residual = self.s.settings.solution.monitor.residual
        residual.options.print = True
        residual.options.plot = False
        for name in residual.equations.get_object_names():
            residual.equations[name].check_convergence = False
        for name in self.s.settings.solution.monitor.report_plots.get_object_names():
            self.s.settings.solution.monitor.report_plots[name].active = False
        values = self.values()
        self.pressure_floor = max(abs(values['p72s3-pressure-inlet']-values['p72s3-pressure-outlet'])*.001, 1.)
        self.flush(status='RUNNING', stage='A_BULK_BASELINE',
                   pressure_floor_pa=self.pressure_floor, original_readback_verified=True)

    def configure(self):
        super().configure()
        self.flush(target_film_clock_s=self.m['production_origin_film_clock_s']+.3,
                   target_added_film_time_s=.3)

    def save(self, label):
        if (Path(str(self.work))/'pairs'/(label+'.cas.h5')).exists():
            label += '-retry-'+str(time.time_ns())
        return super().save(label)

    def apply_step(self, dt, fixture=False):
        """Propagate controls through a preserved full-pair reopen on v252.

        RP parameter readback alone left the accepted fixed step unchanged in
        the live fixture. Reopen allocates solver controls without initializing
        or advancing the saved fields. Printed steps remain the acceptance test.
        """
        self.idle()
        clock = self.clock()
        iteration = r.base.native_iteration(self.s)
        fields = {n: r.base.d.facets(self.s, n) for n in ['wall', r.drain.WALL]}
        equations = self.s.settings.solution.controls.equations.get_state()
        super().apply_step(dt, fixture=fixture)
        params = dict(self.s.rp_vars('wall-film/model-parameters'))
        pair = self.save(f'controls-{dt*1e6:g}us-N{iteration}-{time.time_ns()}')
        self.s.settings.file.read_case(file_name=pair['case'])
        self.s.settings.file.read_data(file_name=pair['data'])
        if dict(self.s.rp_vars('wall-film/model-parameters')) != params:
            raise RuntimeError('Full-pair reopen changed film controls')
        if self.s.settings.solution.controls.equations.get_state() != equations:
            raise RuntimeError('Full-pair reopen changed bulk equation flags')
        if r.base.native_iteration(self.s) != iteration or not math.isclose(self.clock(), clock, abs_tol=1e-12):
            raise RuntimeError('Full-pair reopen changed the production coordinate')
        for n, before in fields.items():
            r.base.d.same_facets(before, r.base.d.facets(self.s, n))
        write(self.out / (Path(pair['case']).stem+'.json'), {
            'status': 'CONTROLS_FULL_PAIR_REOPEN_PASS', 'pair': pair,
            'dt_s': dt, 'film_clock_s': clock, 'fixture': fixture,
            'film_fields_preserved': True, 'bulk_equations_preserved': True,
            'accepted_step_verification': 'Required in each native block',
        })

    def stabilize(self, stage, max_updates=10000):
        """Keep the freeze gate; cap active development at the human film age."""
        finite_stage = stage.startswith(('C', 'E'))
        if not (self.production and finite_stage):
            return super().stabilize(stage, max_updates=max(max_updates, 30000))
        self.windows = []
        self.flush(stage=stage)
        remaining = max(0., self.m['target_film_clock_s']-self.clock())
        minimum_blocks = 3 if stage.startswith('E') else 0
        blocks = max(30, math.ceil(remaining/(1000*self.dt)), minimum_blocks)
        completed_blocks = 0
        for _ in range(blocks):
            block = self.batch(1000,stage)
            completed_blocks += 1
            self.windows.append(block['assessment'])
            gate = policy.bulk_gate(self.windows,self.spec['liquid_feed_kg_s'],self.pressure_floor)
            self.flush(bulk_gate=gate)
            if self.clock()+1e-12 >= self.m['target_film_clock_s'] and completed_blocks >= minimum_blocks:
                self.save(stage+'-cutoff-N'+str(r.base.native_iteration(self.s)))
                self.flush(finite_cutoff_reached_active_bulk=True,bulk_stability_qualified=gate['pass'])
                return
            if gate['pass'] and completed_blocks >= minimum_blocks:
                self.save(stage+'-stable-N'+str(r.base.native_iteration(self.s)))
                return
        raise RuntimeError('Bounded C development ended before its age or stability decision')

    def develop_and_finalize(self):
        if not self.m.get('finite_cutoff_reached_active_bulk'):
            original_ladder = policy.LADDER
            ceiling = self.spec.get('max_production_film_step_s')
            if ceiling is not None:
                policy.refresh_plan(ceiling, self.spec.get('physical_dpm_interval_s',20e-6))
                limited = [step for step in original_ladder if step.dt <= ceiling]
                if not any(math.isclose(step.dt,ceiling,abs_tol=1e-12) for step in limited):
                    limited.append(policy.LadderBlock(ceiling,1000))
                policy.LADDER = tuple(sorted(limited,key=lambda step:step.dt))
            try:
                return super().develop_and_finalize()
            finally:
                policy.LADDER = original_ladder
        # The requested finite age can be reached while bulk remains active.
        # A failed stability gate must never trigger a freeze at this endpoint.
        self.audit()
        final = self.save('final-active-cutoff-N'+str(r.base.native_iteration(self.s)))
        fields = {n:r.base.d.facets(self.s,n) for n in ['wall',r.drain.WALL]}
        clock = self.clock()
        equations = self.s.settings.solution.controls.equations.get_state()
        params = dict(self.s.rp_vars('wall-film/model-parameters'))
        self.s.settings.file.read_data(file_name=final['data'])
        self.audit()
        if self.s.settings.solution.controls.equations.get_state() != equations or dict(
                self.s.rp_vars('wall-film/model-parameters')) != params:
            raise RuntimeError('Final data reopen changed controls')
        for name,before in fields.items():
            r.base.d.same_facets(before,r.base.d.facets(self.s,name))
        if not math.isclose(clock,self.clock(),abs_tol=1e-12):
            raise RuntimeError('Final data reopen changed film age')
        self.flush(status='COMPLETE_DEVELOPED_FILM_CHECKPOINT',stage='F_VERIFIED_ACTIVE_CUTOFF',
                   final_pair=final,final_bulk_equations='ACTIVE',
                   actual_added_film_time_s=clock-self.m['production_origin_film_clock_s'],
                   horizon_overshoot_s=max(0,clock-self.m['target_film_clock_s']),
                   final_reopen='DATA_REOPEN_CONTROLS_AND_BOTH_WALL_FILM_FIELDS_MATCH',
                   frozen_development_used=False,steady_film_qualified=False,
                   timestep_independence_qualified=False)
        self.make_plot()

    def run(self):
        if self.m.get('verified_native_end') == 8020 and not self.production:
            # Reuse the separately verified startup without repeating its solve.
            self.resume_startup = True
            r.base.attach = lambda: self.s
        return super().run()

    def batch(self, *args, **kwargs):
        print('DIRECT_SUBMIT', args, kwargs, flush=True)
        result = super().batch(*args, **kwargs)
        import h5py
        import numpy as np
        check = {'pair': result['pair'], 'fields': {}, 'pass': True}
        with h5py.File(result['pair']['data'], 'r') as data:
            faces = data['results/1/phase-1/faces']
            for name in ['SV_EFILM_HEIGHT', 'SV_EFILM_U', 'SV_EFILM_V', 'SV_EFILM_W']:
                values = np.concatenate([dataset[:].reshape(-1) for dataset in faces[name].values()])
                finite = bool(np.isfinite(values).all())
                valid = finite and (name != 'SV_EFILM_HEIGHT' or bool((values >= -1e-12).all()))
                check['fields'][name] = {'count': len(values), 'finite': finite,
                                         'nonfinite_count': int((~np.isfinite(values)).sum()),
                                         'min': float(values.min()) if finite else None,
                                         'max': float(values.max()) if finite else None, 'pass': valid}
                check['pass'] = check['pass'] and valid
        write(Path(self.m['active_block'])/'film-field-check.json', check)
        if not check['pass']:
            self.flush(status='NATIVE_FILM_FIELD_CHECK_FAILED', native_film_field_check=check)
            raise RuntimeError('Native film field check failed')
        write(self.out/'latest-summary.json', {
            'stage': self.m['stage'], 'iteration': result['end'],
            'film_clock_s': result['final_clock_s'],
            'production_added_ms': 1000*(result['final_clock_s']-self.m.get('production_origin_film_clock_s', result['final_clock_s'])),
            'step_s': self.dt, 'native_seconds': result['native_command_seconds'],
            'assessment': self.m['last_assessment'],
        })
        if not kwargs.get('fixture',False) and self.m.get('capture_next_active_sources'):
            self.flush(capture_next_active_sources=False)
            receipt = self.capture_native_source_storages('active-production')
            self.flush(active_native_source_receipt=receipt)
        return result

    def recover_selected_packet(self):
        """After baseline FPE, apply selected feedback-OFF packet before C.

        Caller must restore the last verified pair in a healthy owned session.
        No baseline stability is claimed. The post-configuration gate remains
        mandatory before any frozen film development.
        """
        self.idle()
        if r.base.native_iteration(self.s) != self.m['verified_native_end']:
            raise RuntimeError('Recovery did not restore the verified endpoint')
        self.flush(stage='B_COMPLETE_SETTINGS', status='RECOVERING_SELECTED_PACKET',
                   baseline_stability_qualified=False,
                   sequence_repair='Apply already-selected feedback-OFF production packet after original-settings FPE; qualify bulk in C')
        self.configure()
        self.stabilize('C_ACTIVE_ADJUSTMENT')
        self.develop_and_finalize()

    def run_recovery_guarded(self):
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            try:
                self.batch(1000, 'feedback-off-recovery', film=False)
                self.recover_selected_packet()
            except Exception as exc:
                import traceback
                write(self.out/'last-error.json', {
                    'error': str(exc), 'traceback': traceback.format_exc(),
                    'native_pending': self.native_pending,
                    'recorded_state': self.m, 'epoch': time.time(),
                })
                raise

    def resume_drain_proof_guarded(self):
        """Repeat only the disposable proof from restored prepared production."""
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            try:
                self.idle()
                prepared = json.loads((self.out/'drain-refresh-proof.json').read_text())['production_pair']
                if r.base.native_iteration(self.s) != prepared['native_iteration']:
                    raise RuntimeError('Prepared production endpoint was not restored')
                self.prove_refresh(prepared)
                self.flush(production_origin_film_clock_s=self.clock(),
                           target_film_clock_s=self.clock()+.3,
                           target_added_film_time_s=.3,
                           configuration_persistence='Full controls pairs reopened; fields, clock and equation flags checked')
                self.stabilize('C_ACTIVE_ADJUSTMENT')
                self.develop_and_finalize()
            except Exception as exc:
                import traceback
                write(self.out/'last-error.json', {
                    'error': str(exc), 'traceback': traceback.format_exc(),
                    'native_pending': self.native_pending,
                    'recorded_state': self.m, 'epoch': time.time(),
                })
                raise

    def resume_ledger_recovery_guarded(self, inner_stop=1e-6, step_s=None):
        """Retry a finite ledger-only failure from the last passing pair.

        Tighten film convergence or reduce the physical step at the same source
        laws and physical particle-update interval.
        Preserve the failed child; its advancement is excluded from the active
        production lineage. The bulk and film acceptance limits stay unchanged.
        """
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            try:
                self.idle()
                if self.native_pending:
                    raise RuntimeError('Native journal still pending')
                failed_path = self.m['blocks'][-1]
                failed = json.loads(Path(failed_path).read_text())
                if failed['assessment']['failures'] != ['FILM_LEDGER_OPERATING_LIMIT']:
                    raise RuntimeError('This recovery handles only a finite ledger failure')
                if r.base.native_iteration(self.s) != failed['end']:
                    raise RuntimeError('Failed endpoint differs from the idle session')
                passed = next(
                    json.loads(Path(path).read_text())
                    for path in reversed(self.m['blocks'][:-1])
                    if 'fixture' not in path
                    and json.loads(Path(path).read_text())['assessment']['pass'])
                if passed['end'] != failed['start']:
                    raise RuntimeError('Last passing endpoint is not the failed block parent')
                for block in [passed, failed]:
                    for kind in ['case', 'data']:
                        pair = block['pair']
                        if r.base.checked_remote_sha256(self.s, pair[kind], None) != pair[kind+'_sha256']:
                            raise RuntimeError('Recovery pair hash differs')
                self.s.settings.file.read_case(file_name=passed['pair']['case'])
                self.s.settings.file.read_data(file_name=passed['pair']['data'])
                if r.base.native_iteration(self.s) != passed['end'] or not math.isclose(
                        self.clock(), passed['final_clock_s'], abs_tol=1e-12):
                    raise RuntimeError('Last passing production coordinate was not restored')
                values = self.values()
                for name in ['v2-total-liquid-mass', 'v2-lower-liquid-mass',
                             'v2-total-vapor-mass', 'p72d-total-mass',
                             'p72d-lower-mass', 'p72d-total-thickness']:
                    if not math.isclose(values[name], passed['final_reports'][name],
                                        rel_tol=1e-9, abs_tol=1e-9):
                        raise RuntimeError('Restored persistent field differs: '+name)
                params = dict(self.s.rp_vars('wall-film/model-parameters'))
                old_stop = params['sub-iter-stop']
                new_stop = old_stop if inner_stop is None else inner_stop
                new_step = passed['dt'] if step_s is None else step_s
                if not 0 < new_stop <= old_stop or not 0 < new_step <= passed['dt']:
                    raise ValueError('Recovery must retain or tighten the saved numerical controls')
                if new_stop == old_stop and new_step == passed['dt']:
                    raise ValueError('Recovery requires a numerical control change')
                policy.refresh_plan(new_step)
                self.dt = passed['dt']
                self.spec['production_parameters']['sub-iter-stop'] = old_stop
                self.audit()
                params['sub-iter-stop'] = new_stop
                self.s.rp_vars('wall-film/model-parameters', list(params.items()))
                self.spec['production_parameters']['sub-iter-stop'] = new_stop
                self.apply_step(new_step)
                self.audit()
                discarded = self.m.get('discarded_block_paths', [])+[failed_path]
                receipt = {'epoch': time.time(), 'parent_pair': passed['pair'],
                           'failed_pair_preserved': failed['pair'],
                           'failed_ledger_fraction': failed['assessment']['ledger_fraction'],
                           'old_inner_stop': old_stop, 'new_inner_stop': new_stop,
                           'old_step_s': passed['dt'], 'step_s': self.dt,
                           'physical_sources_unchanged': True,
                           'restored_clock_s': self.clock(),
                           'reason': 'Test stricter numerical controls for the ledger-only failure; no acceptance limit relaxed'}
                write(self.out/f'ledger-recovery-{self.block_number}-{time.time_ns()}.json', receipt)
                stage = 'C_REDUCED_STEP_LEDGER' if new_step < passed['dt'] else 'C_TIGHTER_INNER'
                self.flush(status='RECOVERING_FILM_LEDGER', stage=stage,
                           discarded_block_paths=discarded, latest_pair=passed['pair'],
                           verified_native_end=passed['end'], verified_film_clock_s=self.clock(),
                           inner_convergence_recovery=receipt)
                self.stabilize(stage)
                self.develop_and_finalize()
            except Exception as exc:
                import traceback
                write(self.out/'last-error.json', {
                    'error': str(exc), 'traceback': traceback.format_exc(),
                    'native_pending': self.native_pending,
                    'recorded_state': self.m, 'epoch': time.time(),
                })
                raise

    def probe_ledger_sources_guarded(self, arm_labels=None):
        """Disposable frozen-bulk accounting arms; never advance production age."""
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            self.idle()
            if self.native_pending:
                raise RuntimeError('Cannot probe while a native journal is pending')
            failed_path = next(path for path in reversed(self.m['blocks']) if 'fixture' not in path)
            failed = json.loads(Path(failed_path).read_text())
            if failed['assessment']['failures'] != ['FILM_LEDGER_OPERATING_LIMIT']:
                raise RuntimeError('Source probes require the preserved ledger-only failure')
            passed = next(json.loads(Path(path).read_text())
                          for path in reversed(self.m['blocks'])
                          if 'fixture' not in path
                          and json.loads(Path(path).read_text())['assessment']['pass'])
            parent = passed['pair']
            current = r.base.native_iteration(self.s)
            restored = self.m['status'] in {
                'ACCOUNTING_DIAGNOSTIC_COMPLETE_PRODUCTION_RESTORED',
                'ACCOUNTING_DIAGNOSTIC_FAILED_PRODUCTION_RESTORED'}
            if current != failed['end'] and not (restored and current == passed['end']):
                raise RuntimeError('Live source-probe parent differs from the preserved failure or restored parent')
            for kind in ['case', 'data']:
                if r.base.checked_remote_sha256(self.s, parent[kind], None) != parent[kind+'_sha256']:
                    raise RuntimeError('Source-probe parent hash differs')
            def restore():
                self.s.settings.file.read_case(file_name=parent['case'])
                self.s.settings.file.read_data(file_name=parent['data'])
                self.dt = passed['dt']
                self.spec['production_parameters']['sub-iter-stop'] = dict(
                    self.s.rp_vars('wall-film/model-parameters'))['sub-iter-stop']
                self.set_bulk(True)
                self.audit()
                if r.base.native_iteration(self.s) != passed['end'] or not math.isclose(
                        self.clock(), passed['final_clock_s'], abs_tol=1e-12):
                    raise RuntimeError('Source-probe restore changed the production coordinate')
            restore()
            fields = {n: r.base.d.facets(self.s, n) for n in ['wall', r.drain.WALL]}
            bulk = self.values()
            receipt = {'status': 'TESTING', 'production_pair': parent,
                       'production_clock_s': self.clock(), 'arms': [],
                       'production_restored': False, 'bulk_stability_qualified': False}
            receipt_path = self.out/f'ledger-source-probes-{time.time_ns()}.json'
            discarded = list(dict.fromkeys(self.m.get('discarded_block_paths', [])+[failed_path]))
            self.flush(stage='DIAGNOSTIC_SOURCE_LEDGER', status='SOURCE_ACCOUNTING_PROBES',
                       discarded_block_paths=discarded, accounting_probe_receipt=str(receipt_path))
            no_release = {'film-stripping?': False, 'film-separation?': False}
            no_dpm = {**no_release, 'dpm-collection?': False, 'dpm-splashing?': False}
            available = {'full': {}, 'no-release': no_release,
                         'accretion-only': no_dpm, 'closed-transport': {**no_dpm, 'secondary-phase-mode': 0},
                         'no-stripping': {'film-stripping?': False},
                         'no-separation': {'film-separation?': False},
                         'no-accretion': {'secondary-phase-mode': 0},
                         'no-dpm': {'dpm-collection?': False, 'dpm-splashing?': False},
                         'no-splashing': {'dpm-splashing?': False},
                         'implicit-second': {'time-scheme': 3},
                         'explicit-first': {'time-scheme': 0},
                         'segregated-implicit': {'film-coupled-solution?': False, 'time-scheme': 2},
                         'small-film-cutoff': {'thickness-small': 1e-10},
                         'tiny-film-cutoff': {'thickness-small': 1e-12},
                         'dpm-every-step': {'iters-per-dpm-step': 1}}
            labels = arm_labels or ['full', 'no-release', 'accretion-only', 'closed-transport']
            if not set(labels).issubset(available) or len(set(labels)) != len(labels):
                raise ValueError('Unknown or duplicated disposable accounting arm')
            arms = [(label, available[label]) for label in labels]
            try:
                for label, changes in arms:
                    restore()
                    self.set_bulk(False)
                    r.setparams(self.s, changes)
                    self.apply_step(passed['dt'], fixture=True)
                    if 'iters-per-dpm-step' in changes:
                        r.setparams(self.s, changes)
                        controls = self.save(f'fixture-{label}-controls-N{passed["end"]}-{time.time_ns()}')
                        self.s.settings.file.read_case(file_name=controls['case'])
                        self.s.settings.file.read_data(file_name=controls['data'])
                    params = dict(self.s.rp_vars('wall-film/model-parameters'))
                    release = [n for n, key in [('p72d-total-stripped', 'film-stripping?'),
                               ('p72d-total-separated', 'film-separation?')] if params[key]]
                    sources = (["p72d-total-secondary"] if params['secondary-phase-mode'] else [])
                    if params['dpm-collection?']:
                        sources += ['p72d-total-dpm']
                    self.names = ['v2-total-liquid-mass', 'v2-lower-liquid-mass', 'v2-total-vapor-mass',
                                  'p72d-total-mass', 'p72d-lower-mass', 'p72d-total-outflow',
                                  'p72d-drain-rate', 'p72d-total-courant', 'p72d-total-thickness',
                                  'p72r-film-speed-max']+release+sources
                    block = self.batch(100, 'ledger-'+label+'-fixture', film=False, fixture=True)
                    a = block['assessment']; h = a['histories']
                    native_sources = {}
                    for field in (['film-phase2-mass'] if params['secondary-phase-mode'] else [])+(
                            ['film-dpm-mass-src'] if params['dpm-collection?'] else []):
                        arrays = self.s.fields.field_data.get_field_data(r.base.d.ScalarFieldDataRequest(
                            surfaces=['wall', r.drain.WALL], field_name=field,
                            node_value=False, boundary_value=True))
                        native_sources[field] = {wall: r.base.d.np.asarray(arrays[wall]).reshape(-1).tolist()
                                                 for wall in ['wall', r.drain.WALL]}
                    source_path = Path(self.m['active_block'])/'source-field-snapshot.json'
                    write(source_path, {'native_iteration': block['end'], 'film_clock_s': self.clock(),
                                        'fields': native_sources})
                    source_totals = {}
                    for field, walls in native_sources.items():
                        vals = [v for array in walls.values() for v in array]
                        source_totals[field] = {'sum': sum(vals),
                            'positive_sum': sum(v for v in vals if v > 0),
                            'negative_sum': sum(v for v in vals if v < 0)}
                    departure = sum(h[n][-1]-block['initial'][n] for n in
                                    ['p72d-total-mass', 'p72d-total-outflow']+release)
                    supply = {n: sum(h[n])*self.dt for n in sources}
                    drain = sum(h['p72d-drain-rate'])*self.dt
                    error = departure+drain-sum(supply.values())
                    receipt['arms'].append({'label': label, 'changes': changes, 'actual_parameters': params, 'pair': block['pair'],
                        'added_fixture_time_s': a['added_film_time_s'], 'departure_kg': departure,
                        'supply_kg': supply, 'drain_kg': drain, 'ledger_residual_kg': error,
                        'ledger_fraction': abs(error)/sum(supply.values()) if sum(supply.values()) > 1e-12 else None,
                        'relative_to_seed_film': abs(error)/block['initial']['p72d-total-mass'],
                        'native_source_fields': str(source_path), 'native_source_totals': source_totals,
                        'operating_assessment': {k:v for k,v in a.items() if k not in ['histories','residuals']}})
                    write(receipt_path, receipt)
                    if a['fatal_solver_event'] or a['peak_courant'] >= 1:
                        raise RuntimeError('Fatal source-probe operating event')
                receipt['status'] = 'DIAGNOSTIC_ARMS_COMPLETE'
            except Exception as exc:
                receipt.update(status='DIAGNOSTIC_FAILED', error=str(exc))
                raise
            finally:
                if self.native_pending:
                    receipt['status'] = 'RESTORE_DEFERRED_NATIVE_RETURN_UNCONFIRMED'
                    write(receipt_path, receipt)
                    raise RuntimeError('Source-probe restore deferred while native command is unresolved')
                restore()
                for n, before in fields.items():
                    r.base.d.same_facets(before, r.base.d.facets(self.s, n))
                after = self.values()
                for n in ['v2-total-liquid-mass', 'v2-lower-liquid-mass', 'v2-total-vapor-mass']:
                    if not math.isclose(bulk[n], after[n], rel_tol=1e-10, abs_tol=1e-10):
                        raise RuntimeError('Source-probe restore changed bulk inventory')
                receipt['production_restored'] = True
                write(receipt_path, receipt)
                status = ('ACCOUNTING_DIAGNOSTIC_COMPLETE_PRODUCTION_RESTORED'
                          if receipt['status'] == 'DIAGNOSTIC_ARMS_COMPLETE'
                          else 'ACCOUNTING_DIAGNOSTIC_FAILED_PRODUCTION_RESTORED')
                self.flush(status=status,
                           latest_pair=parent, verified_native_end=passed['end'],
                           verified_film_clock_s=self.clock(), accounting_probe_receipt=str(receipt_path))

    def resume_time_scheme_guarded(self, label, active_timestep_screen=False, source_receipt=None):
        """Qualify a full-physics numerical candidate from restored production."""
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            try:
                self.idle()
                receipt_path = Path(source_receipt or self.m['accounting_probe_receipt'])
                receipt = json.loads(receipt_path.read_text())
                if not receipt.get('production_restored'):
                    raise RuntimeError('Accounting fixture has not restored production')
                arm = next(a for a in receipt['arms'] if a['label'] == label)
                if not arm['changes'] or not set(arm['changes']).issubset(
                        {'time-scheme', 'film-coupled-solution?', 'mass-scheme', 'mom-scheme', 'thickness-small'}):
                    raise RuntimeError('Candidate changes physical source options')
                if not arm['operating_assessment']['pass'] or arm['ledger_fraction'] is None or arm['ledger_fraction'] > .01:
                    raise RuntimeError('Numerical candidate has not passed its smoke balance')
                parent = receipt['production_pair']
                for kind in ['case', 'data']:
                    if r.base.checked_remote_sha256(self.s, parent[kind], None) != parent[kind+'_sha256']:
                        raise RuntimeError('Numerical candidate parent hash differs')
                if r.base.native_iteration(self.s) != parent['native_iteration'] or not math.isclose(
                        self.clock(), receipt['production_clock_s'], abs_tol=1e-12):
                    raise RuntimeError('Numerical candidate production coordinate differs')
                self.set_bulk(True)
                self.audit()
                r.setparams(self.s, arm['changes'])
                self.spec['production_parameters'].update(arm['changes'])
                self.apply_step(self.dt)
                self.audit()
                review = {'candidate': label, 'changes': arm['changes'], 'parent_pair': parent,
                          'smoke_receipt': str(receipt_path),
                          'production_clock_s': self.clock(), 'physical_sources_unchanged': True,
                          'acceptance_limits_unchanged': True}
                write(self.out/f'time-scheme-recovery-{time.time_ns()}.json', review)
                self.flush(status='QUALIFYING_NUMERICAL_CANDIDATE', stage='C_'+label.upper().replace('-', '_'),
                           numerical_candidate=review)
                if active_timestep_screen:
                    screened = []
                    for step, count in [(1e-6, 1000), (2e-6, 1000), (5e-6, 1000), (10e-6, 1000)]:
                        self.apply_step(step)
                        self.audit()
                        block = self.batch(count, f'C-active-screen-{step*1e6:g}us')
                        screened.append({'step_s': step, 'count': count, 'pair': block['pair'],
                                         'film_ms_per_wall_minute': block['assessment']['film_ms_per_wall_minute']})
                        self.flush(active_bulk_timestep_screen=screened,
                                   timestep_screen_claim='Continuous active-bulk stability and throughput; timestep error not isolated')
                    selected = max(screened, key=lambda b: b['film_ms_per_wall_minute'])['step_s']
                    self.apply_step(selected)
                    self.audit()
                    self.flush(selected_active_step_s=selected)
                self.stabilize(self.m['stage'])
                self.develop_and_finalize()
            except Exception as exc:
                import traceback
                write(self.out/'last-error.json', {
                    'error': str(exc), 'traceback': traceback.format_exc(),
                    'native_pending': self.native_pending, 'recorded_state': self.m, 'epoch': time.time()})
                raise

    def resume_verified_accounting_guarded(self, receipt_path):
        """Qualify the measured v252 net-source overlap, then resume full physics.

        No saved failed assessment is rewritten. The 1% consistency bound and
        every other operating guard remain active on newly solved blocks.
        """
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            try:
                self.idle()
                receipt = json.loads(Path(receipt_path).read_text(encoding='utf-8'))
                if receipt['status'] != 'DIAGNOSTIC_ARMS_COMPLETE' or not receipt['production_restored']:
                    raise RuntimeError('Source control sequence has not completed and restored production')
                labels = ['full', 'no-stripping', 'no-separation', 'no-accretion', 'no-release']
                arms = {a['label']: a for a in receipt['arms']}
                if not set(labels).issubset(arms):
                    raise RuntimeError('Missing source-overlap controls')
                blocks = {label: json.loads((self.out/'blocks'/Path(arms[label]['pair']['case']).parent.name/
                           'block.json').read_text(encoding='utf-8')) for label in labels}
                increments, corrected = {}, {}
                for label in labels:
                    a = arms[label]
                    failures = a['operating_assessment']['failures']
                    diagnostic_inner_limit = label == 'no-accretion' and failures == ['ACHIEVED_INNER_RESIDUAL_LIMIT']
                    if failures and not diagnostic_inner_limit:
                        raise RuntimeError('A source control failed an operating guard')
                    block = blocks[label]
                    if any(block['equations'].values()):
                        raise RuntimeError('Source controls were not frozen forcing')
                    h = block['assessment']['histories']
                    increments[label] = {key: h[key][-1]-block['initial'][key] for key in
                        ['p72d-total-stripped', 'p72d-total-separated'] if key in h}
                    error = a['ledger_residual_kg']
                    if label in ['full', 'no-stripping']:
                        error -= increments[label]['p72d-total-separated']
                    fraction = abs(error)/max(sum(abs(v) for v in a['supply_kg'].values()),1e-12)
                    corrected[label] = {'residual_kg': error, 'fraction': fraction,
                                        'operating_assessment':a['operating_assessment'],
                                        'diagnostic_inner_limit':diagnostic_inner_limit}
                    if fraction > .01:
                        raise RuntimeError('Net-source consistency failed a held-out source control')
                gross = arms['no-release']['supply_kg']['p72d-total-secondary']
                reconstructed = {}
                for label in ['full', 'no-stripping', 'no-separation']:
                    reconstructed[label] = arms[label]['supply_kg']['p72d-total-secondary']+sum(increments[label].values())
                    if abs(reconstructed[label]-gross)/max(abs(gross),1e-12) > .001:
                        raise RuntimeError('Secondary report does not establish the measured release overlap')
                parent = receipt['production_pair']
                if r.base.native_iteration(self.s) != parent['native_iteration'] or not math.isclose(
                        self.clock(),receipt['production_clock_s'],abs_tol=1e-12):
                    raise RuntimeError('Source controls did not restore the production coordinate')
                for kind in ['case','data']:
                    if r.base.checked_remote_sha256(self.s,parent[kind],None) != parent[kind+'_sha256']:
                        raise RuntimeError('Restored accounting parent hash differs')
                version = self.s.get_fluent_version().value
                if not version.startswith('25.2'):
                    raise RuntimeError('Net-source accounting was established only for Fluent 25.2')
                proof = {'status':'PASS','version':version,'source_receipt':str(receipt_path),
                         'parent_pair':parent,'gross_secondary_control_kg':gross,
                         'net_secondary_plus_release_kg':reconstructed,'control_consistency':corrected,
                         'basis':'verified-v252-net-secondary','limit':.01,
                         'claim_limit':'Measured native net-source consistency; whole-system/event closure remains unqualified',
                         'original_failed_assessments_preserved':True,'physical_source_options_changed':False}
                proof_path = self.out/f'net-source-accounting-proof-{time.time_ns()}.json'
                write(proof_path,proof)
                self.spec['film_ledger_basis'] = proof['basis']
                self.spec['film_ledger_basis_proof'] = str(proof_path)
                write(self.out/'job.json',self.spec)
                self.set_bulk(True)
                self.audit()
                self.flush(status='QUALIFYING_NET_SOURCE_CONSISTENCY',stage='C_NET_SOURCE_CONSISTENCY',
                           film_ledger_basis=proof['basis'],film_ledger_basis_proof=str(proof_path))
                screened = []
                for step in [2e-6,5e-6,10e-6]:
                    self.apply_step(step)
                    self.audit()
                    block = self.batch(1000,f'C-net-source-screen-{step*1e6:g}us')
                    screened.append({'step_s':step,'pair':block['pair'],
                                     'film_ms_per_wall_minute':block['assessment']['film_ms_per_wall_minute']})
                    self.flush(active_bulk_net_source_screen=screened)
                selected = max(screened,key=lambda b:b['film_ms_per_wall_minute'])['step_s']
                self.apply_step(selected)
                self.audit()
                self.flush(selected_active_step_s=selected)
                self.stabilize('C_NET_SOURCE_ADJUSTMENT')
                self.develop_and_finalize()
            except Exception as exc:
                import traceback
                write(self.out/'last-error.json',{'error':str(exc),'traceback':traceback.format_exc(),
                      'native_pending':self.native_pending,'recorded_state':self.m,'epoch':time.time()})
                raise

    def capture_native_source_storages(self, label):
        """Compile and run a passive version-matched face/cell source read."""
        self.idle()
        stamp = time.time_ns()
        library = 'libp72cells_'+str(stamp)
        source = Path(__file__).resolve().parents[1]/'inspection/phase72a_ewf_source_probe.c'
        copied = self.local_work/f'phase72a_ewf_source_cells_{stamp}.c'
        copied.write_bytes(source.read_bytes())
        fields = {wall:r.base.d.facets(self.s,wall) for wall in ['wall',r.drain.WALL]}
        before = {'iteration':r.base.native_iteration(self.s),'clock_s':self.clock(),
                  'parameters':dict(self.s.rp_vars('wall-film/model-parameters')),
                  'equations':self.s.settings.solution.controls.equations.get_state(),'reports':self.values()}
        udf = self.s.settings.setup.user_defined
        udf.compiled_udf(library_name=library,source_files=[str(copied)],header_files=[],use_built_in_compiler=True)
        udf.load(udf_library_name=library)
        transcript = self.local_work/f'native-source-cells-{label}-{stamp}.trn'
        try:
            self.s.settings.file.start_transcript(file_name=transcript.as_posix())
            try:
                udf.execute_on_demand(lib_name='phase72a_ewf_source_probe::'+library)
                self.s.settings.results.report.discrete_phase.summary()
            finally:
                self.s.settings.file.stop_transcript()
        finally:
            udf.unload(udf_library_name=[library])
        after = {'iteration':r.base.native_iteration(self.s),'clock_s':self.clock(),
                 'parameters':dict(self.s.rp_vars('wall-film/model-parameters')),
                 'equations':self.s.settings.solution.controls.equations.get_state(),'reports':self.values()}
        if before != after:
            raise RuntimeError('Passive source probe changed solver readback')
        for wall,values in fields.items():
            r.base.d.same_facets(values,r.base.d.facets(self.s,wall))
        receipt_path = self.out/f'native-source-cells-{label}-{stamp}.json'
        write(receipt_path,{'status':'PASS_READ_ONLY','before':before,'after':after,'fields_exactly_preserved':True,
                           'source_file':str(copied),'source_sha256':hashlib.file_digest(copied.open('rb'),'sha256').hexdigest(),
                           'native_transcript':str(transcript),
                           'transcript_sha256':hashlib.file_digest(transcript.open('rb'),'sha256').hexdigest(),
                           'native_storage_lines':[line.strip() for line in transcript.read_text(errors='replace').splitlines()
                                                   if line.startswith('P72_EWF_')],
                           'claim_limit':'Storage availability and matched sums establish interpretation; unavailable or stale caches do not mean zero transfer'})
        return str(receipt_path)

    def probe_particle_cadence_guarded(self, intervals=(20e-6,100e-6,200e-6), step=10e-6, count=100):
        """Matched frozen-field tracking screens; restore production exactly."""
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            self.idle()
            passed = next(json.loads(Path(p).read_text(encoding='utf-8')) for p in reversed(self.m['blocks'])
                          if 'fixture' not in p and json.loads(Path(p).read_text(encoding='utf-8'))['assessment']['pass'])
            parent = passed['pair']
            if r.base.native_iteration(self.s) != passed['end']:
                raise RuntimeError('Particle screen requires the latest accepted production coordinate')
            for kind in ['case','data']:
                if r.base.checked_remote_sha256(self.s,parent[kind],None) != parent[kind+'_sha256']:
                    raise RuntimeError('Particle screen parent hash differs')
            original_interval = self.spec.get('physical_dpm_interval_s',20e-6)
            def restore():
                self.spec['physical_dpm_interval_s'] = original_interval
                self.s.settings.file.read_case(file_name=parent['case'])
                self.s.settings.file.read_data(file_name=parent['data'])
                self.dt = passed['dt']
                self.set_bulk(True)
                self.audit()
                if r.base.native_iteration(self.s) != passed['end'] or not math.isclose(
                        self.clock(),passed['final_clock_s'],abs_tol=1e-12):
                    raise RuntimeError('Particle screen changed production coordinates')
            restore()
            fields = {wall:r.base.d.facets(self.s,wall) for wall in ['wall',r.drain.WALL]}
            initial_bulk = self.values()
            receipt_path = self.out/f'particle-cadence-screen-{time.time_ns()}.json'
            receipt = {'status':'TESTING','production_pair':parent,'production_clock_s':self.clock(),
                       'film_step_s':step,'fixture_updates':count,'arms':[],'production_restored':False,
                       'bounds':{'mass_field_l1_fraction':.02,'mass_weighted_velocity_difference_fraction':.05},
                       'claim_limit':'Operating and short matched-field sensitivity screen; no timestep or particle-interval independence claim'}
            write(receipt_path,receipt)
            self.flush(status='PARTICLE_CADENCE_PROBES',stage='DIAGNOSTIC_PARTICLE_CADENCE',
                       particle_cadence_receipt=str(receipt_path))
            reference = None
            try:
                for interval in intervals:
                    if count*step < 5*interval-1e-12:
                        raise ValueError('Particle smoke needs at least five tracking intervals')
                    restore()
                    self.spec['physical_dpm_interval_s'] = interval
                    self.set_bulk(False)
                    self.apply_step(step,fixture=True)
                    self.audit()
                    block = self.batch(count,f'particle-{interval*1e6:g}us-fixture',fixture=True)
                    end_fields = {wall:r.base.d.facets(self.s,wall) for wall in fields}
                    field_path = Path(self.m['active_block'])/'film-facets.npz'
                    r.base.d.np.savez(field_path,**{wall+'::'+key:values for wall,vals in end_fields.items()
                                                  for key,values in vals.items()})
                    if reference is None:
                        reference = end_fields
                    np = r.base.d.np
                    mass_l1, velocity_numerator, velocity_denominator, total_mass = 0.,0.,0.,0.
                    for wall, values in end_fields.items():
                        ref = reference[wall]
                        mass = values['film-mass']; ref_mass = ref['film-mass']
                        mass_l1 += float(np.abs(mass-ref_mass).sum())
                        total_mass += float(ref_mass.sum())
                        velocity = np.column_stack([values['film-'+c+'-velocity'] for c in 'xyz'])
                        ref_velocity = np.column_stack([ref['film-'+c+'-velocity'] for c in 'xyz'])
                        weights = .5*(mass+ref_mass)
                        velocity_numerator += float((weights*np.linalg.norm(velocity-ref_velocity,axis=1)).sum())
                        velocity_denominator += float((weights*np.linalg.norm(ref_velocity,axis=1)).sum())
                    differences = {'mass_field_l1_fraction':mass_l1/max(total_mass,1e-12),
                                   'mass_weighted_velocity_difference_fraction':velocity_numerator/max(velocity_denominator,1e-12)}
                    accepted = block['assessment']['pass'] and all(differences[k] <= limit for k,limit in receipt['bounds'].items())
                    receipt['arms'].append({'particle_interval_s':interval,'pair':block['pair'],
                        'fields':str(field_path),'differences':differences,'pass':accepted,
                        'actual_parameters':dict(self.s.rp_vars('wall-film/model-parameters')),
                        'assessment':{k:v for k,v in block['assessment'].items() if k not in ['histories','residuals']}})
                    write(receipt_path,receipt)
                    if interval == intervals[0] and not accepted:
                        raise RuntimeError('Reference particle screen failed its operating limits')
                    if interval == intervals[0]:
                        receipt['native_source_probe'] = self.capture_native_source_storages('particle-reference')
                        write(receipt_path,receipt)
                receipt['status'] = 'SCREEN_COMPLETE'
            finally:
                if self.native_pending:
                    receipt['status'] = 'RESTORE_DEFERRED_NATIVE_RETURN_UNCONFIRMED'
                    write(receipt_path,receipt)
                    raise RuntimeError('Particle screen restore deferred while native return is unconfirmed')
                restore()
                for wall,before in fields.items():
                    r.base.d.same_facets(before,r.base.d.facets(self.s,wall))
                after = self.values()
                for key in ['v2-total-liquid-mass','v2-lower-liquid-mass','v2-total-vapor-mass']:
                    if not math.isclose(initial_bulk[key],after[key],rel_tol=1e-10,abs_tol=1e-10):
                        raise RuntimeError('Particle screen restore changed bulk inventory')
                receipt['production_restored'] = True
                write(receipt_path,receipt)
                self.flush(status='PARTICLE_CADENCE_SCREEN_PRODUCTION_RESTORED',latest_pair=parent,
                           verified_native_end=passed['end'],verified_film_clock_s=self.clock(),
                           particle_cadence_receipt=str(receipt_path))

    def resume_particle_cadence_guarded(self, interval, step=10e-6):
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            try:
                self.idle()
                receipt = json.loads(Path(self.m['particle_cadence_receipt']).read_text(encoding='utf-8'))
                if receipt['status'] != 'SCREEN_COMPLETE' or not receipt['production_restored']:
                    raise RuntimeError('Particle screen has not completed and restored production')
                arm = next(a for a in receipt['arms'] if math.isclose(a['particle_interval_s'],interval,abs_tol=1e-12))
                if not arm['pass'] or step != receipt['film_step_s']:
                    raise RuntimeError('Particle candidate has not passed the matched-field screen')
                a = arm['assessment']
                if a['inner_steps_observed'] != receipt['fixture_updates'] or a['inner_steps_passed'] != receipt['fixture_updates']:
                    raise RuntimeError('New particle interval has a failed or missing inner step')
                parent = receipt['production_pair']
                if r.base.native_iteration(self.s) != parent['native_iteration'] or not math.isclose(
                        self.clock(),receipt['production_clock_s'],abs_tol=1e-12):
                    raise RuntimeError('Particle candidate live parent differs')
                self.spec['physical_dpm_interval_s'] = interval
                self.spec['require_all_inner_steps'] = True
                write(self.out/'job.json',self.spec)
                self.set_bulk(True)
                self.apply_step(step)
                self.audit()
                self.flush(stage='C_PARTICLE_CADENCE_QUALIFICATION',status='QUALIFYING_PARTICLE_CADENCE',
                           selected_particle_interval_s=interval,particle_interval_independence_qualified=False,
                           capture_next_active_sources=True)
                self.batch(1000,f'C-particle-{interval*1e6:g}us-qualification')
                self.stabilize('C_PARTICLE_CADENCE_ADJUSTMENT')
                self.develop_and_finalize()
            except Exception as exc:
                import traceback
                write(self.out/'last-error.json',{'error':str(exc),'traceback':traceback.format_exc(),
                      'native_pending':self.native_pending,'recorded_state':self.m,'epoch':time.time()})
                raise

    def probe_active_particle_cadence_guarded(self, intervals=(100e-6,200e-6)):
        """Replay only diagnostic arms against an already completed reference.

        Production stays at the accepted reference endpoint. Both candidate
        replays start at that reference block's saved start, with bulk active.
        """
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            self.idle()
            reference = next(json.loads(Path(p).read_text(encoding='utf-8')) for p in reversed(self.m['blocks'])
                             if 'fixture' not in p and json.loads(Path(p).read_text(encoding='utf-8'))['assessment']['pass'])
            if reference['count'] != 1000 or reference['dt'] != 5e-6:
                raise RuntimeError('Active particle replay needs the completed fixed 5us reference')
            production_pair = reference['pair']
            seed = next(json.loads(Path(p).read_text(encoding='utf-8')) for p in reversed(self.m['blocks'])
                        if 'fixture' not in p and json.loads(Path(p).read_text(encoding='utf-8'))['end'] == reference['start'])
            if r.base.native_iteration(self.s) != reference['end']:
                raise RuntimeError('Active particle replay production coordinate differs')
            for pair in [production_pair,seed['pair']]:
                for kind in ['case','data']:
                    if r.base.checked_remote_sha256(self.s,pair[kind],None) != pair[kind+'_sha256']:
                        raise RuntimeError('Active particle replay pair hash differs')
            original_interval = self.spec.get('physical_dpm_interval_s',20e-6)
            def load(block):
                self.spec['physical_dpm_interval_s'] = original_interval
                self.s.settings.file.read_case(file_name=block['pair']['case'])
                self.s.settings.file.read_data(file_name=block['pair']['data'])
                self.dt = block['dt']
                self.set_bulk(True)
                self.audit()
                if r.base.native_iteration(self.s) != block['end'] or not math.isclose(
                        self.clock(),block['final_clock_s'],abs_tol=1e-12):
                    raise RuntimeError('Active particle replay load changed coordinates')
            load(reference)
            fields = {wall:r.base.d.facets(self.s,wall) for wall in ['wall',r.drain.WALL]}
            before = self.values()
            receipt_path = self.out/f'active-particle-cadence-screen-{time.time_ns()}.json'
            receipt = {'status':'TESTING','production_pair':production_pair,'production_clock_s':self.clock(),
                       'reference_pair':production_pair,'seed_pair':seed['pair'],'film_step_s':reference['dt'],
                       'fixture_updates':1000,'bulk_mode':'ACTIVE','arms':[],'production_restored':False,
                       'reference_assessment':{k:v for k,v in reference['assessment'].items() if k not in ['histories','residuals']},
                       'bounds':{'mass_field_l1_fraction':.02,'mass_weighted_velocity_difference_fraction':.05},
                       'claim_limit':'Matched active-bulk operating and field-sensitivity replays; no interval independence claim'}
            self.flush(status='ACTIVE_PARTICLE_CADENCE_PROBES',stage='DIAGNOSTIC_ACTIVE_PARTICLE_CADENCE',
                       particle_cadence_receipt=str(receipt_path))
            write(receipt_path,receipt)
            try:
                for interval in intervals:
                    load(seed)
                    self.spec['physical_dpm_interval_s'] = interval
                    self.apply_step(reference['dt'],fixture=True)
                    self.audit()
                    block = self.batch(1000,f'active-particle-{interval*1e6:g}us-fixture',fixture=True)
                    end_fields = {wall:r.base.d.facets(self.s,wall) for wall in fields}
                    field_path = Path(self.m['active_block'])/'film-facets.npz'
                    r.base.d.np.savez(field_path,**{wall+'::'+key:values for wall,vals in end_fields.items()
                                                  for key,values in vals.items()})
                    np = r.base.d.np
                    mass_l1, total_mass, velocity_numerator, velocity_denominator = 0.,0.,0.,0.
                    for wall,values in end_fields.items():
                        ref = fields[wall]
                        mass = values['film-mass']; ref_mass = ref['film-mass']
                        mass_l1 += float(np.abs(mass-ref_mass).sum()); total_mass += float(ref_mass.sum())
                        velocity = np.column_stack([values['film-'+c+'-velocity'] for c in 'xyz'])
                        ref_velocity = np.column_stack([ref['film-'+c+'-velocity'] for c in 'xyz'])
                        weights = .5*(mass+ref_mass)
                        velocity_numerator += float((weights*np.linalg.norm(velocity-ref_velocity,axis=1)).sum())
                        velocity_denominator += float((weights*np.linalg.norm(ref_velocity,axis=1)).sum())
                    differences = {'mass_field_l1_fraction':mass_l1/max(total_mass,1e-12),
                                   'mass_weighted_velocity_difference_fraction':velocity_numerator/max(velocity_denominator,1e-12)}
                    accepted = block['assessment']['pass'] and all(differences[k] <= limit for k,limit in receipt['bounds'].items())
                    receipt['arms'].append({'particle_interval_s':interval,'pair':block['pair'],'fields':str(field_path),
                        'differences':differences,'pass':accepted,'actual_parameters':dict(self.s.rp_vars('wall-film/model-parameters')),
                        'assessment':{k:v for k,v in block['assessment'].items() if k not in ['histories','residuals']}})
                    write(receipt_path,receipt)
                    if block['assessment']['pass'] and 'native_source_probe' not in receipt:
                        receipt['native_source_probe'] = self.capture_native_source_storages('active-particle-candidate')
                        write(receipt_path,receipt)
                receipt['status'] = 'SCREEN_COMPLETE'
            finally:
                if self.native_pending:
                    receipt['status'] = 'RESTORE_DEFERRED_NATIVE_RETURN_UNCONFIRMED'
                    write(receipt_path,receipt)
                    raise RuntimeError('Active particle replay restore deferred while native return is unconfirmed')
                load(reference)
                for wall,values in fields.items():
                    r.base.d.same_facets(values,r.base.d.facets(self.s,wall))
                after = self.values()
                for key in ['v2-total-liquid-mass','v2-lower-liquid-mass','v2-total-vapor-mass']:
                    if not math.isclose(before[key],after[key],rel_tol=1e-10,abs_tol=1e-10):
                        raise RuntimeError('Active particle replay restore changed bulk inventory')
                receipt['production_restored'] = True
                write(receipt_path,receipt)
                self.flush(status='PARTICLE_CADENCE_SCREEN_PRODUCTION_RESTORED',latest_pair=production_pair,
                           verified_native_end=reference['end'],verified_film_clock_s=self.clock(),
                           particle_cadence_receipt=str(receipt_path))

    def recover_inner_stall_guarded(self):
        """Retry a preserved inner-only failure with documented smoothing.

        Full coupled film momentum and physical source flags stay unchanged.
        Return after the fixed qualification block for the next decision.
        """
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            try:
                self.idle()
                records = [(path,json.loads(Path(path).read_text(encoding='utf-8')))
                           for path in self.m['blocks'] if 'fixture' not in Path(path).parent.name]
                failed_path,failed = records[-1]
                if failed['assessment']['failures'] != ['ALL_INNER_STEPS_REQUIRED']:
                    raise RuntimeError('Smoothing recovery requires the preserved inner-only failure')
                _,passed = next((path,block) for path,block in reversed(records)
                                if block['assessment']['pass'] and path not in self.m.get('discarded_block_paths',[]))
                parent = passed['pair']
                if r.base.native_iteration(self.s) != failed['end']:
                    raise RuntimeError('Inner recovery live coordinate differs from the saved failure')
                for block in [failed,passed]:
                    for kind in ['case','data']:
                        if r.base.checked_remote_sha256(self.s,block['pair'][kind],None) != block['pair'][kind+'_sha256']:
                            raise RuntimeError('Inner recovery paired checkpoint hash differs')
                self.s.settings.file.read_case(file_name=parent['case'])
                self.s.settings.file.read_data(file_name=parent['data'])
                self.dt = passed['dt']
                self.set_bulk(True)
                self.audit()
                if r.base.native_iteration(self.s) != passed['end'] or not math.isclose(
                        self.clock(),passed['final_clock_s'],abs_tol=1e-12):
                    raise RuntimeError('Inner recovery parent coordinate differs')
                changes = {'film-smoothing?':True,'film-smooth-level':2,'film-smooth-factor':.5}
                r.setparams(self.s,changes)
                self.spec['production_parameters'].update(changes)
                self.spec['require_all_inner_steps'] = True
                write(self.out/'job.json',self.spec)
                self.apply_step(passed['dt'])
                self.audit()
                review = {'parent_pair':parent,'failed_pair':failed['pair'],'changes':changes,
                          'physics_flags_and_drain_law_unchanged':True,
                          'documentation':'https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_time_coupl.html',
                          'claim_limit':'Numerical operating qualification; no smoothing or timestep independence claim'}
                write(self.out/f'inner-stall-recovery-{time.time_ns()}.json',review)
                self.flush(stage='C_CURVATURE_SMOOTHING_QUALIFICATION',status='QUALIFYING_INNER_STALL_REPAIR',
                           discarded_block_paths=list(dict.fromkeys(self.m.get('discarded_block_paths',[])+[failed_path])),
                           numerical_candidate=review)
                block = self.batch(1000,'C-curvature-smoothing-qualification')
                self.windows = [block['assessment']]
                self.flush(bulk_gate=policy.bulk_gate(self.windows,self.spec['liquid_feed_kg_s'],self.pressure_floor))
                return block
            except Exception as exc:
                import traceback
                write(self.out/'last-error.json',{'error':str(exc),'traceback':traceback.format_exc(),
                      'native_pending':self.native_pending,'recorded_state':self.m,'epoch':time.time()})
                raise

    def run_guarded(self):
        """Keep the caller's solver alive for direct inspection/repair on failure."""
        with staged.exclusive_writer_lock(self.out/'writer.lock'):
            write(self.out/'code-review.json', {
                'script_sha256': hashlib.file_digest(Path(__file__).open('rb'), 'sha256').hexdigest(),
                'review': 'Caller-owned v252 session; original hashes; local file transport; inherited native solve/save/marker and gates; 300ms target after configuration proof',
                'commands': ['readback', '20-update startup', 'bulk stability',
                             'complete setup/readback/data reopen', 'disposable drain proof and exact restore',
                             'bulk adjustment', 'freeze', 'continuous timestep screen',
                             'film development', 'reactivate bulk', 'save/hash/data reopen'],
                'remote_queries': False,
            })
            try:
                self.run()
            except Exception as exc:
                import traceback
                write(self.out/'last-error.json', {
                    'error': str(exc), 'traceback': traceback.format_exc(),
                    'native_pending': self.native_pending, 'recorded_state': self.m,
                    'epoch': time.time(),
                })
                raise
