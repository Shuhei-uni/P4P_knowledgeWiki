"""Laptop controller for continuous EWF development from original 60k N8000.

Fixed blocks use Fluent-owned journals; while a journal is active this process
waits for native return and observes a passive Monitor stream. The laptop stays active.
Never launch/exit Fluent, reset production fields, or restart a comparison.
"""
from pathlib import Path, PureWindowsPath
import argparse
import csv
import json
import math
import os
import statistics
import sys
import threading
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
import run_phase72a_stage4_replacement as r
from pyansys_fluent import ewf_staged as policy
from pyansys_fluent.stage4_native import exclusive_writer_lock, configure_autosave


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False, default=str) + '\n')
    temp.replace(path)


class PassiveProgress:
    """One passive v252 monitor stream; no Cortex/Settings calls."""
    def __init__(self, path, start, end):
        self.path, self.start, self.end = path, start, end
        self.channel = None
        self.stream = None
        self.done = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def run(self):
        import grpc
        from ansys.api.fluent.v0 import monitor_pb2, monitor_pb2_grpc
        from pyansys_fluent.connection import resolve_connection_kwargs
        try:
            cfg = resolve_connection_kwargs('1', start_transcript=False, tcp_timeout_seconds=5)
            self.channel = grpc.insecure_channel(f"{cfg['ip']}:{cfg['port']}")
            self.stream = monitor_pb2_grpc.MonitorStub(self.channel).BeginStreaming(
                monitor_pb2.StreamingRequest(), metadata=[('password', cfg['password'])])
            for response in self.stream:
                if self.done.is_set(): break
                i = response.xaxisdata.xaxisindex
                if self.start < i <= self.end:
                    write(self.path, {'observed_epoch': time.time(), 'iteration': i,
                                     'start': self.start, 'target': self.end, 'method': 'PASSIVE_MONITOR_V0'})
        except Exception:
            # Passive observation failure cannot authorize a new solve or RPC.
            pass
        finally:
            if self.channel: self.channel.close()

    def stop(self):
        self.done.set()
        if self.stream: self.stream.cancel()
        self.thread.join(timeout=2)


class Runner:
    def __init__(self, spec, resume_startup=False):
        self.spec = spec
        self.work = PureWindowsPath(spec['work'])
        self.out = Path(spec['output'])
        self.out.mkdir(parents=True, exist_ok=True)
        self.manifest = self.out / 'run-manifest.json'
        if self.manifest.exists() and not resume_startup:
            raise RuntimeError('Existing job must be reconciled; fresh launch cannot overwrite or resubmit it')
        self.m = {'status': 'STARTING', 'stage': 'PARENT', 'pid': os.getpid(),
                  'server_id': '1', 'work': str(self.work), 'parent_pair': spec['parent_pair'],
                  'blocks': [], 'requires_laptop_for_solve': False, 'requires_laptop_for_transitions': True,
                  'requires_laptop_for_supervision': True,
                  'authority': 'human_20261008_run_staged_method_from_original_60k_N8000',
                  'claim_limit': 'Sequential operating screen; timestep error, event closure and inner residual availability remain explicit'}
        self.resume_startup = resume_startup
        if resume_startup:
            self.m = json.loads(self.manifest.read_text())
            if self.m['status'] != 'VERIFIED_STARTUP_READY_TO_RESUME' or self.m['verified_native_end'] != 8020:
                raise RuntimeError('Resume is limited to the verified original-parent startup checkpoint')
            self.m['pid'] = os.getpid()
        self.s = None
        self.names = policy.BULK
        self.params = None
        self.production = False
        self.windows = []
        self.block_number = len(self.m['blocks'])
        self.native_pending = False
        self.flush()

    def flush(self, **changes):
        self.m.update(changes, heartbeat_epoch=time.time())
        write(self.manifest, self.m)

    def idle(self):
        if self.native_pending:
            raise RuntimeError('Native journal return is unconfirmed; no Settings RPC is allowed')
        if self.s.settings.solution.run_calculation.iterating():
            raise RuntimeError('Settings changes are forbidden while a native journal runs')

    def clock(self):
        return float(dict(self.s.rp_vars('wall-film/solution-state'))['film_elapsed_time'])

    def values(self):
        raw = r.values(self.s, self.names)
        # Computed aliases include User Mass Source; file histories are boundary-only.
        return {n: raw.get(n+'(without-sources)', raw[n])[0] for n in self.names}

    def save(self, label):
        self.idle()
        folder = PureWindowsPath(str(self.work / 'pairs'))
        r.base.ensure_remote_directory(self.s, str(folder))
        r.base.ensure_remote_directory(self.s, str(folder / 'scratch'))
        pair = r.reports.save_pair(self.s, folder, label)
        self.flush(latest_pair=pair, verified_native_end=pair['native_iteration'],
                   verified_film_clock_s=self.clock())
        return pair

    def set_bulk(self, active):
        self.idle()
        original = self.spec['original_equations']
        for name, enabled in original.items():
            self.s.settings.solution.controls.equations[name] = enabled if active else False
        actual = self.s.settings.solution.controls.equations.get_state()
        expected = original if active else {n: False for n in original}
        if actual != expected:
            raise RuntimeError('Bulk equation readback differs')
        bulk_reports = policy.BULK if active else ['v2-total-liquid-mass', 'v2-lower-liquid-mass', 'v2-total-vapor-mass']
        self.names = list(dict.fromkeys(bulk_reports + (policy.FILM_REPORTS if self.production else [])))
        self.flush(bulk_equations='ACTIVE' if active else 'FROZEN')

    def apply_step(self, dt, fixture=False):
        self.idle()
        changes = policy.refresh_plan(dt, self.spec.get('physical_dpm_interval_s', 20e-6))
        r.setparams(self.s, changes)
        self.s.settings.solution.run_calculation.profile_update_interval = 1
        if self.production or fixture:
            r.drain.configure(self.s, enabled=True, refresh_span_s=10e-6)
            proof = r.drain.audit(self.s, True)
            if not math.isclose(proof['rate_s_inverse'], 1/.0015, rel_tol=1e-12):
                raise RuntimeError('Depletion protection silently changed the drain law')
        self.dt = dt
        self.flush(step_s=dt, cadence=changes, source_refresh_span_s=10e-6)

    def load_original(self):
        self.s = r.base.attach()
        self.idle()
        if r.base.native_iteration(self.s) != self.spec['preserved_current_pair']['native_iteration']:
            raise RuntimeError('Server 1 changed since preservation; reconcile before loading')
        for kind in ['case', 'data']:
            pair = self.spec['preserved_current_pair']
            digest = r.base.checked_remote_sha256(self.s, pair[kind], str(self.work / (kind+'-preserved.sha256')))
            if digest != pair[kind+'_sha256']:
                raise RuntimeError('Preserved endpoint hash differs')
        for kind in ['case', 'data']:
            pair = self.spec['parent_pair']
            digest = r.base.checked_remote_sha256(self.s, pair[kind], str(self.work / (kind+'-parent.sha256')))
            if digest != pair[kind+'_sha256']:
                raise RuntimeError('Original N8000 hash differs')
        # Proven v252 prompt order from the replacement-parent recovery receipt.
        # Refuse overwrites, keep errors visible in transcript, hide GUI answers,
        # and do not redisplay questions. Read the parent case exactly once.
        self.s.tui.file.set_batch_options('no', 'no', 'yes', 'no')
        self.s.settings.file.read_case(file_name=pair['case'])
        self.s.settings.file.read_data(file_name=pair['data'])
        if r.base.native_iteration(self.s) != 8000:
            raise RuntimeError('Loaded parent is not N8000')
        state = r.snapshot(self.s)
        write(self.out / 'original-parent-readback.json', state)
        if state['equations'] != self.spec['original_equations'] or state['cell_zones'] != self.spec['original_cell_zones']:
            raise RuntimeError('Original bulk basis differs')
        if state['parameters'] != self.spec['original_parameters']:
            raise RuntimeError('Original EWF basis differs')
        self.dt = state['parameters']['timestep-max']
        if not math.isclose(self.clock(), self.spec['original_film_clock_s'], abs_tol=1e-12):
            raise RuntimeError('Original film clock differs')
        residual = self.s.settings.solution.monitor.residual
        residual.options.print = True
        residual.options.plot = False
        for n in residual.equations.get_object_names():
            residual.equations[n].check_convergence = False
        for n in self.s.settings.solution.monitor.report_plots.get_object_names():
            self.s.settings.solution.monitor.report_plots[n].active = False
        pressure = self.values()
        self.pressure_floor = max(abs(pressure['p72s3-pressure-inlet']-pressure['p72s3-pressure-outlet'])*.001, 1.0)
        self.flush(status='RUNNING', stage='A_BULK_BASELINE', original_readback_verified=True,
                   native_cells=self.spec['native_cells'], initial_film_clock_s=self.clock(),
                   pressure_floor_pa=self.pressure_floor, step_s=self.dt)

    def batch(self, count, label, film=True, fixture=False, allow_step_rejection=False):
        self.idle()
        if count < 1000 and not fixture and label != 'startup-smoke':
            raise ValueError('Production blocks require at least 1000 updates')
        self.block_number += 1
        start = r.base.native_iteration(self.s)
        end = start+count
        token = f'{self.block_number:03}-{label}-N{start}-N{end}'
        directory = self.work / 'blocks' / token
        local = self.out / 'blocks' / token
        local.mkdir(parents=True, exist_ok=False)
        r.base.ensure_remote_directory(self.s, str(directory))
        for n in ['monitors', 'scratch', 'checkpoints']:
            r.base.ensure_remote_directory(self.s, str(directory / n))
        paths = r.instrument(self.s, PureWindowsPath(str(directory / 'monitors')), self.names)
        configure_autosave(self.s, str(directory / 'checkpoints'), data_frequency=1000)
        initial = self.values()
        initial_clock = self.clock()
        before_equations = self.s.settings.solution.controls.equations.get_state()
        text = policy.journal(directory, count, end, token=token)
        journal = directory / 'native-run.jou'
        r.write_ascii_text_new(self.s, str(journal), text)
        (local / 'native-run.jou').write_text(text, encoding='ascii')
        record = {'status': 'SUBMITTING_NATIVE', 'start': start, 'end': end, 'count': count,
                  'dt': self.dt, 'initial': initial, 'initial_clock_s': initial_clock,
                  'equations': before_equations, 'journal': str(journal), 'reports': paths}
        write(local / 'block.json', record)
        stream = local / 'live-native.txt'
        self.s.transcript.start(file_name=str(stream), write_to_stdout=False)
        self.flush(active_block=str(local), active_target=end, status='RUNNING_NATIVE',
                   native_transcript=str(directory / 'native-run.trn'), passive_transcript=str(stream),
                   passive_progress=str(local / 'monitor-progress.json'), native_started_epoch=time.time(),
                   native_return_seen=False)
        # This blocking dispatch is the final Cortex/Scheme call until the
        # journal stops its transcript and writes the terminal marker.
        command = '(ti-menu-load-string "/file/read-journal \\\"'+journal.as_posix()+'\\\"")'
        submitted = time.monotonic()
        self.native_pending = True
        observer = PassiveProgress(local / 'monitor-progress.json', start, end)
        observer.thread.start()
        try:
            # SDK v0 documents wait=True as waiting for execution to complete.
            # Do not rely on its transcript stream: it is silent on this session.
            self.s.scheme.exec((command,), wait=True, silent=True)
        finally:
            observer.stop()
        self.s.transcript.stop()
        self.native_pending = False
        solve_seconds = time.monotonic()-submitted
        self.flush(status='COLLECTING_ENDPOINT', native_return_seen=True)
        marker = directory / 'returned.txt'
        if r.read_text(self.s, str(marker)).strip() != 'NATIVE_COMMAND_RETURNED':
            raise RuntimeError('Native terminal marker differs')
        self.idle()
        if r.base.native_iteration(self.s) != end:
            raise RuntimeError('Native iteration horizon differs')
        raw = r.read_text(self.s, str(directory / 'native-run.trn'))
        (local / 'native-run.trn').write_text(raw)
        histories = {}
        for n, p in paths.items():
            report = r.read_text(self.s, p)
            (local / (n+'.out')).write_text(report)
            histories[n] = policy.history(report)
        assessment = policy.assess_block(raw, histories, initial, start, count, self.dt, initial_clock, film,
                                         ledger_basis=self.spec.get('film_ledger_basis', 'gross-reported-sources'),
                                         require_all_inner=self.spec.get('require_all_inner_steps',False))
        actual_clock = self.clock()
        if not math.isclose(actual_clock-initial_clock, count*self.dt, abs_tol=1e-10):
            raise RuntimeError('Native terminal film clock differs')
        if self.s.settings.solution.controls.equations.get_state() != before_equations:
            raise RuntimeError('Bulk mode changed during solve')
        pair = {'case': str(directory / f'final-N{end}.cas.h5'), 'data': str(directory / f'final-N{end}.dat.h5'), 'native_iteration': end}
        for kind in ['case', 'data']:
            pair[kind+'_sha256'] = r.base.checked_remote_sha256(self.s, pair[kind], str(directory / 'scratch' / (kind+'.sha256')))
        assessment['film_ms_per_wall_minute'] = assessment['added_film_time_s']*1000/(max(solve_seconds, 1e-9)/60)
        record.update(status='CHECKPOINT_VERIFIED', pair=pair, assessment=assessment,
                      final_clock_s=actual_clock, final_reports=self.values(), native_return_verified=True,
                      native_command_seconds=solve_seconds,
                      collection_seconds=time.monotonic()-submitted-solve_seconds)
        if not any(before_equations.values()):
            for n in ['v2-total-liquid-mass', 'v2-lower-liquid-mass', 'v2-total-vapor-mass']:
                if any(not math.isclose(v, initial[n], rel_tol=1e-10, abs_tol=1e-10) for v in assessment['histories'][n]):
                    assessment['failures'].append('FROZEN_BULK_INVENTORY_CHANGED')
                    assessment['pass'] = False
        write(local / 'block.json', record)
        self.m['blocks'].append(str(local / 'block.json'))
        self.flush(status='RUNNING', active_target=None, latest_pair=pair,
                   verified_native_end=end, verified_film_clock_s=actual_clock,
                   last_assessment={k: v for k, v in assessment.items() if k not in ['histories', 'residuals']})
        print('VERIFIED_BLOCK', label, start, end, self.dt, assessment['failures'], flush=True)
        if not fixture and not assessment['pass'] and not allow_step_rejection:
            self.flush(status='STOPPED_OPERATING_GUARD', stop_reason=assessment['failures'])
            raise OperatingStop('Saved block did not pass the operating screen')
        return record

    def stabilize(self, stage, max_updates=10000):
        self.windows = []
        self.flush(stage=stage)
        for _ in range(max_updates//1000):
            block = self.batch(1000, stage, film=self.production)
            self.windows.append(block['assessment'])
            gate = policy.bulk_gate(self.windows, self.spec['liquid_feed_kg_s'], self.pressure_floor)
            self.flush(bulk_gate=gate)
            if gate['pass']:
                self.save(stage+'-stable-N'+str(r.base.native_iteration(self.s)))
                return
        self.flush(status='STOPPED_BULK_NOT_STABLE', stop_reason='Declared bulk-stability allowance exhausted')
        raise OperatingStop('Bulk stability gate did not pass')

    def configure(self):
        self.flush(stage='B_COMPLETE_SETTINGS')
        self.idle()
        before = self.save('before-configuration-N'+str(r.base.native_iteration(self.s)))
        upper = r.base.d.facets(self.s, 'wall')
        bulk = self.values()
        clock = self.clock()
        params = dict(self.spec['production_parameters'])
        params.update(policy.refresh_plan(1e-6))
        r.setparams(self.s, params)
        lower = self.s.settings.setup.boundary_conditions.wall[r.drain.WALL].phase['mixture'].wall_film
        lower.eulerian_film_wall = True
        lower.film_condition_type = 'film-wall-initial'
        lower.film_height.set_state({'option': 'value', 'value': 0.0})
        lower.enable_film_source_terms = False
        lower.enable_flow_momentum_coupling = False
        self.s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        self.s.settings.file.read_data(file_name=before['data'])
        r.setparams(self.s, params)
        r.base.d.same_facets(upper, r.base.d.facets(self.s, 'wall'))
        if not math.isclose(self.clock(), clock, abs_tol=1e-12):
            raise RuntimeError('Configuration reset production film age')
        for name in ['wall', r.drain.WALL]:
            wall = self.s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film
            wall.enable_flow_momentum_coupling = False
            wall.enable_dpm_wall_splash = True
            wall.allow_film_boundary_separation = True
        self.production = True
        self.apply_step(1e-6)
        r.base.d.define_reports(self.s)
        reports = self.s.settings.solution.report_definitions.surface
        if 'p72r-film-speed-max' not in reports.get_object_names():
            reports.create(name='p72r-film-speed-max')
        reports['p72r-film-speed-max'].set_state({'report_type': 'surface-facetmax', 'field': 'film-velocity-mag', 'surface_names': ['wall', r.drain.WALL]})
        self.set_bulk(True)
        after_bulk = self.values()
        for n, v in bulk.items():
            if not math.isclose(after_bulk[n], v, rel_tol=1e-10, abs_tol=1e-10):
                raise RuntimeError('Configuration changed a bulk diagnostic')
        self.params = dict(self.s.rp_vars('wall-film/model-parameters'))
        self.audit()
        prepared = self.save('prepared-N'+str(r.base.native_iteration(self.s)))
        state = r.snapshot(self.s)
        original = json.loads((self.out / 'original-parent-readback.json').read_text())
        for n in ['methods', 'materials', 'inlets', 'multiphase', 'cell_zones']:
            if state[n] != original[n]:
                raise RuntimeError('Configuration changed the original '+n+' basis')
        write(self.out / 'prepared-readback.json', state)
        self.s.settings.file.read_data(file_name=prepared['data'])
        self.audit()
        if dict(self.s.rp_vars('wall-film/model-parameters')) != self.params or not math.isclose(self.clock(), clock, abs_tol=1e-12):
            raise RuntimeError('Prepared-data reopen does not retain controls/clock')
        self.prove_refresh(prepared)
        self.flush(production_origin_film_clock_s=self.clock(),
                   target_film_clock_s=self.clock()+.05,
                   configuration_persistence='Data reopened; controls/fields checked; case saved/hashed, not reloaded to avoid repeated GUI file dialogs')

    def audit(self):
        self.idle()
        p = dict(self.s.rp_vars('wall-film/model-parameters'))
        expected = dict(self.spec['production_parameters'])
        expected.update(policy.refresh_plan(self.dt, self.spec.get('physical_dpm_interval_s', 20e-6)))
        if p != expected:
            raise RuntimeError('Full production film parameter readback differs')
        if self.s.settings.setup.cell_zone_conditions.fluid.get_state() != self.spec['original_cell_zones']:
            raise RuntimeError('Bulk source hooks changed')
        expressions = self.s.settings.setup.named_expressions
        for name, definition in self.spec['original_expression_definitions'].items():
            if expressions[name].definition() != definition:
                raise RuntimeError('Original expression changed: '+name)
        r.drain.audit(self.s, True)
        for name in ['wall', r.drain.WALL]:
            w = self.s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film.get_state()
            if not w['eulerian_film_wall'] or w['enable_flow_momentum_coupling'] or not w['enable_dpm_wall_splash'] or not w['allow_film_boundary_separation']:
                raise RuntimeError('Film wall flags differ')

    def prove_refresh(self, prepared):
        """Disposable zero-forcing film only; restore exact production data after.

        This is drainage/cadence proof, not a restarted production comparison.
        """
        saved_params = dict(self.s.rp_vars('wall-film/model-parameters'))
        saved_walls = {n: self.s.settings.setup.boundary_conditions.wall[n].phase['mixture'].wall_film.get_state() for n in ['wall', r.drain.WALL]}
        saved_names = self.names
        saved_bulk = {n: self.values()[n] for n in ['v2-total-liquid-mass', 'v2-lower-liquid-mass', 'v2-total-vapor-mass']}
        proof = {'status': 'TESTING', 'production_pair': prepared, 'steps': [], 'bulk_reference': saved_bulk}
        try:
            self.set_bulk(False)
            disabled = {k: False for k in ['mom-gravity?', 'mom-aero-drive?', 'mom-wall-visc?', 'mom-pressure?', 'mom-spreading?', 'surface-tension?', 'dpm-collection?', 'dpm-splashing?', 'film-separation?', 'film-stripping?']}
            disabled['secondary-phase-mode'] = 0
            r.setparams(self.s, disabled)
            for name in saved_walls:
                w = self.s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film
                w.film_condition_type = 'film-wall-initial'
                w.film_height.set_state({'option': 'value', 'value': 1e-4 if name == r.drain.WALL else 0.0})
            self.s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
            seed = self.save('cadence-fixture-seed-N'+str(r.base.native_iteration(self.s)))
            self.names = policy.BULK + ['p72d-lower-mass', 'p72d-drain-rate', 'p72d-total-thickness', 'p72d-total-courant']
            for ladder in policy.LADDER:
                self.s.settings.file.read_data(file_name=seed['data'])
                self.apply_step(ladder.dt, fixture=True)
                b = self.batch(100, 'drain-fixture-'+str(round(ladder.dt*1e6))+'us', film=False, fixture=True)
                a = b['assessment']['histories']
                masses = [b['initial']['p72d-lower-mass']]+a['p72d-lower-mass']
                rates = [b['initial']['p72d-drain-rate']]+a['p72d-drain-rate']
                errors = [abs((x-y)/(z*ladder.dt)-1) for x, y, z in zip(masses, masses[1:], rates) if z > 0]
                if len(errors) != 100 or max(errors) > .03 or masses[-1] >= masses[0] or min(masses) < 0:
                    raise RuntimeError('Direct removal/source-refresh fixture failed')
                fractions = [(x-y)/x for x, y in zip(masses, masses[1:])]
                if max(fractions) > .01*(1+1e-7):
                    raise RuntimeError('Drain depletion guard failed')
                for n, value in saved_bulk.items():
                    if not math.isclose(b['final_reports'][n], value, rel_tol=1e-10, abs_tol=1e-10):
                        raise RuntimeError('Frozen fixture changed bulk inventory')
                proof['steps'].append({'dt': ladder.dt, 'max_relative_source_error': max(errors), 'removed_kg': masses[0]-masses[-1], 'max_depletion_fraction': max(fractions), 'pair': b['pair']})
            proof['status'] = 'PASS_ALL_FOUR_REFRESH_STEPS'
        finally:
            if self.native_pending:
                proof.update(status='RESTORE_DEFERRED_NATIVE_RETURN_UNCONFIRMED', production_restored=False)
                write(self.out / 'drain-refresh-proof.json', proof)
                # Do not enter Cortex from an exception handler while its
                # submitted journal may still be running.
                raise RuntimeError('Native fixture return unconfirmed; restore deferred')
            r.setparams(self.s, saved_params)
            for n, st in saved_walls.items():
                w = self.s.settings.setup.boundary_conditions.wall[n].phase['mixture'].wall_film
                w.film_condition_type = st['film_condition_type']
                w.film_height.set_state(st['film_height'])
            self.s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
            self.s.settings.file.read_data(file_name=prepared['data'])
            self.names = saved_names
            self.apply_step(1e-6)
            self.set_bulk(True)
            self.audit()
            if r.base.native_iteration(self.s) != prepared['native_iteration']:
                raise RuntimeError('Production restore changed native coordinate')
            proof['restored_production_clock_s'] = self.clock()
            proof['production_restored'] = True
            write(self.out / 'drain-refresh-proof.json', proof)
            self.flush(latest_pair=prepared, verified_native_end=prepared['native_iteration'], verified_film_clock_s=self.clock())

    def run(self):
        if self.resume_startup:
            self.s = r.base.attach()
            self.idle()
            if r.base.native_iteration(self.s) != self.m['verified_native_end'] or not math.isclose(self.clock(), self.m['verified_film_clock_s'], abs_tol=1e-12):
                raise RuntimeError('Verified startup endpoint changed before resume')
            if dict(self.s.rp_vars('wall-film/model-parameters')) != self.spec['original_parameters']:
                raise RuntimeError('Original controls changed before startup resume')
            self.dt = self.spec['original_parameters']['timestep-max']
            self.pressure_floor = self.m['pressure_floor_pa']
            self.flush(status='RUNNING', stage='A_BULK_BASELINE', step_s=self.dt)
        else:
            self.load_original()
            self.batch(20, 'startup-smoke', film=False)
        self.stabilize('A_BULK_BASELINE')
        self.configure()
        self.stabilize('C_ACTIVE_ADJUSTMENT')
        self.develop_and_finalize()

    def develop_and_finalize(self):
        """Continue a configured, bulk-qualified child through D/E/F."""
        self.save('before-freeze-N'+str(r.base.native_iteration(self.s)))
        self.set_bulk(False)
        self.flush(stage='D_CONTINUOUS_LADDER')
        candidates = []
        previous = None
        for step in policy.LADDER:
            self.save('before-'+f'{step.dt*1e6:g}'+'us-N'+str(r.base.native_iteration(self.s)))
            self.apply_step(step.dt)
            self.audit()
            block = self.batch(step.count, 'ladder-'+f'{step.dt*1e6:g}'+'us', allow_step_rejection=True)
            a = block['assessment']
            if previous is None:
                self.flush(frozen_production_drain_proof={'positive_direct_removal': a['direct_removal_kg'] > 0,
                           'direct_removal_kg': a['direct_removal_kg'], 'bulk_mode': 'FROZEN',
                           'accepted_added_film_time_s': a['added_film_time_s'], 'ledger_fraction': a['ledger_fraction']})
                if a['direct_removal_kg'] <= 0:
                    a['failures'].append('NO_DIRECT_DRAIN_IN_FROZEN_PRODUCTION_PROBE')
            if previous is not None:
                for name in ['p72r-film-speed-max', 'p72d-total-thickness']:
                    before = statistics.median(previous['histories'][name][-200:])
                    after = statistics.median(a['histories'][name][:200])
                    if before > 1e-12 and after > 2*before:
                        a['failures'].append('PERSISTENT_SWITCH_RESPONSE_'+name)
            if a['failures']:
                fatal = a['fatal_solver_event'] or a['peak_courant'] >= 1 or any(
                    n in a['failures'] for n in ['THICKNESS_LIMIT', 'NEGATIVE_FILM_FIELD', 'FROZEN_BULK_INVENTORY_CHANGED'])
                if not candidates or fatal:
                    self.flush(status='STOPPED_OPERATING_GUARD', stop_reason=a['failures'])
                    raise OperatingStop('Saved film block did not pass the operating screen')
                # Recover a finite operating-limit failure by reducing the step
                # in the current fields, without restarting a comparison.
                fallback = max(candidates, key=lambda v:v['film_ms_per_wall_minute'])
                self.flush(stage='D_REDUCED_STEP_RECOVERY', rejected_step_s=step.dt, rejected_step_reasons=a['failures'])
                self.apply_step(fallback['step_s'])
                self.audit()
                self.batch(1000, 'reduced-step-recovery')
                self.flush(step_ladder_stopped_at=step.dt)
                break
            candidates.append({'step_s': step.dt, 'film_ms_per_wall_minute': a['film_ms_per_wall_minute']})
            previous = a
            self.flush(ladder_completed=candidates)
        choice = max(candidates, key=lambda a: a['film_ms_per_wall_minute'])
        self.apply_step(choice['step_s'])
        self.audit()
        self.flush(selected_step_s=self.dt, stage='D_FROZEN_DEVELOPMENT')
        # Reserve >=3000 active-bulk iterations at the actual selected film step.
        boundary = self.m['target_film_clock_s']-3000*self.dt
        count = math.floor((boundary-self.clock())/self.dt+1e-6)
        if count >= 1000:
            self.batch(count, 'frozen-development')
        self.save('before-reactivation-N'+str(r.base.native_iteration(self.s)))
        self.set_bulk(True)
        self.stabilize('E_ACTIVE_FINAL_CHECK')
        while self.clock()+1e-12 < self.m['target_film_clock_s']:
            self.stabilize('E_TARGET_EXTENSION', max_updates=10000)
        self.audit()
        final = self.save('final-N'+str(r.base.native_iteration(self.s)))
        fields = self.values()
        clock = self.clock()
        self.s.settings.file.read_data(file_name=final['data'])
        self.audit()
        after = self.values()
        for n in [x for x in fields if not x.endswith('-secondary')]:
            if not math.isclose(fields[n], after[n], rel_tol=1e-9, abs_tol=1e-9):
                raise RuntimeError('Final data reopen changed persistent report '+n)
        if not math.isclose(clock, self.clock(), abs_tol=1e-12):
            raise RuntimeError('Final data reopen changed film age')
        self.flush(status='COMPLETE_DEVELOPED_FILM_CHECKPOINT', stage='F_VERIFIED',
                   final_pair=final, final_bulk_equations='ACTIVE', actual_added_film_time_s=clock-self.m['production_origin_film_clock_s'],
                   horizon_overshoot_s=max(0, clock-self.m['target_film_clock_s']),
                   final_reopen='DATA_REOPEN_CONTROL_AND_PERSISTENT_REPORT_MATCH',
                   steady_film_qualified=False, timestep_independence_qualified=False)
        self.make_plot()

    def make_plot(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        rows = []
        for path in self.m['blocks']:
            b = json.loads(Path(path).read_text())
            if path in self.m.get('discarded_block_paths', []) or not b['assessment']['pass']:
                continue
            if 'fixture' in Path(path).parent.name or not any(n.startswith('p72d-') for n in b['assessment']['histories']):
                continue
            a = b['assessment']
            for j in range(b['count']):
                rows.append([b['start']+j+1, (b['initial_clock_s']+(j+1)*b['dt']-self.m['production_origin_film_clock_s'])*1000,
                             a['histories']['v2-total-liquid-mass'][j], a['histories']['p72d-total-mass'][j],
                             a['histories']['p72d-drain-rate'][j], a['histories']['p72d-total-courant'][j]])
        if not rows:
            return
        with (self.out / 'histories.csv').open('w', newline='') as stream:
            w = csv.writer(stream);w.writerow(['iteration','added_film_ms','bulk_kg','film_kg','drain_kg_s','courant']);w.writerows(rows)
        fig, axes = plt.subplots(4, 1, figsize=(9, 9), sharex=True)
        for ax, column, label in zip(axes, [2,3,4,5], ['Bulk liquid (kg)','Film liquid (kg)','Direct drain (kg/s)','Film Courant']):
            ax.plot([x[1] for x in rows], [x[column] for x in rows], lw=.8)
            ax.set_ylabel(label);ax.grid(alpha=.2)
        axes[-1].set_xlabel('Added production film time (ms)')
        fig.tight_layout();fig.savefig(self.out / 'development.png', dpi=160);plt.close(fig)


class OperatingStop(RuntimeError):
    pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', type=Path, required=True)
    parser.add_argument('--resume-startup', action='store_true', help='Resume only the verified N8020 startup after observer repair; no case/data reload')
    args = parser.parse_args()
    spec = json.loads(args.job.read_text())
    if spec['server_id'] != '1' or spec['native_cells'] != 60964 or spec['parent_pair']['native_iteration'] != 8000:
        raise RuntimeError('This job owns only Server 1 and original 60k N8000')
    with exclusive_writer_lock(Path(spec['output']) / 'runner.lock'):
        owner = Runner(spec, resume_startup=args.resume_startup)
        try:
            owner.run()
        except OperatingStop:
            owner.make_plot()
        except BaseException as exc:
            # A native journal may still own Fluent. Preserve that ambiguity;
            # never probe/interrupt it, launch a duplicate, or reload a case here.
            owner.flush(status='EXECUTION_REVIEW_REQUIRED', error_type=type(exc).__name__)
            traceback.print_exc()
            try: owner.make_plot()
            except Exception: pass
            raise


if __name__ == '__main__':
    main()
