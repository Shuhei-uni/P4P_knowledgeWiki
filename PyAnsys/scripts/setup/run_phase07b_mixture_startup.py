"""E8: one bounded documented Mixture startup contrast, with stage-aware evidence.

Imports and --validate-only are file-only. Execution requires --execute and an
absent unique run directory. There is deliberately no automatic resume/replay:
after any uncertain RPC, reconcile the recorded live iteration and owned pause.
No initialization, counter manipulation, source change, or Fluent termination.
"""
from run_phase07b_screen import *
from resume_phase07b_investigation import resolved_native_report_path
from analyze_phase07b_screen import parse_history, derive, table
from pyansys_fluent.phase07b_spike_monitor import Phase07bSpikeMonitor

ACTIVE_FLOW = {'continuity', 'x-velocity', 'y-velocity', 'z-velocity', 'k', 'epsilon'}
ACTIVE_FULL = ACTIVE_FLOW | {'vf-phase-1', 'vf-phase-2'}
CONDITIONING_TARGETS = [50] + list(range(200, 1001, 100))
FATAL = ['SEGMENTATION VIOLATION', 'floating point exception', 'Divergence detected']
SLIP_VARIABLES = ['SV_SLIP_U','SV_SLIP_V','SV_SLIP_W']


def fingerprint(path):
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def verify_frozen_phase_arrays(current, initial, zones):
    """Exact raw VF and actual stored slip parity; derived velocities diagnostic."""
    assert set(current)==set(initial)
    evidence=[]; stored=[]
    for i,z in enumerate(zones):
        for ph in ['phase-1','phase-2']:
            key=f'z{i}_{ph}_SV_VOF'; assert np.array_equal(current[key],initial[key]), ('Frozen raw VF changed',key)
        for ph in ['mixture','phase-1','phase-2']:
            for variable in SLIP_VARIABLES:
                key=f'z{i}_{ph}_{variable}'
                assert np.array_equal(current[key],initial[key]), ('Frozen stored slip changed',key)
                stored.append(key)
        for axis in 'UVW':
            delta=current[f'z{i}_phase-2_SV_{axis}']-current[f'z{i}_phase-1_SV_{axis}']
            before=initial[f'z{i}_phase-2_SV_{axis}']-initial[f'z{i}_phase-1_SV_{axis}']
            evidence.append({'zone':z,'axis':axis,'max_difference_m_s':float(np.max(abs(delta-before)))})
    return {'raw_fractions_exact':True,'actual_stored_slip_exact':True,'stored_slip_keys':stored,'derived_phase_velocity_comparisons':evidence,
            'slip_claim_limit':'Actual SV_SLIP_U/V/W arrays checked in all three exposed domains. Derived phase2-minus-phase1 differences are diagnostic and may change under reconstruction.'}


def parse_stage_residuals(path, stage, start, end):
    """Keep native inactive columns, but never label them solved residuals.

    Fluent may retain monitored VF columns while their equations are disabled.
    Stage membership comes from verified equation switches, not a zero value.
    The active six/eight curves must be present on every advancing iteration.
    A native printed chunk boundary is excluded explicitly, not shifted.
    """
    active = ACTIVE_FLOW if stage == 'conditioning' else ACTIVE_FULL
    assert stage in {'conditioning', 'full'} and 0 <= start < end <= 5000
    names = None; rows = []; headers = []; inactive = set(); boundaries = []
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        words = line.split()
        if words and words[0] == 'iter' and 'continuity' in words:
            names = words[1:words.index('time/iter')] if 'time/iter' in words else words[1:]
            assert len(set(names)) == len(names) and active <= set(names) <= ACTIVE_FULL, (lineno, names)
            if stage == 'full': assert set(names) == ACTIVE_FULL
            inactive.update(set(names) - active); headers.append({'line': lineno, 'columns': names})
            continue
        if not names or not words or not words[0].isdigit(): continue
        if len(words) < len(names) + 1 or not any(':' in v for v in words[len(names)+1:]): continue
        iteration = int(words[0])
        native = dict(zip(names, [float(v) for v in words[1:len(names)+1]]))
        assert all(np.isfinite(v) for v in native.values()), (lineno, native)
        assert start <= iteration <= end, ('Unexpected stage index', iteration, start, end)
        if iteration == start:
            boundaries.append({'iteration': iteration, 'line': lineno}); continue
        rows.append((iteration, [native[k] for k in sorted(active)]))
    data, audit = table(rows, sorted(active))
    assert np.array_equal(data['iteration'], np.arange(start+1, end+1)), 'Missing active residual records'
    assert not audit['conflicting_indices'] and not audit['nonfinite_columns']
    audit.update(stage=stage, start_exclusive=start, end_inclusive=end,
                 active_equations=sorted(active), native_headers=headers,
                 inactive_native_columns=sorted(inactive), excluded_start_boundary=boundaries,
                 source=fingerprint(path), inactive_policy='Preserved verbatim in transcript; excluded from active residual gate')
    return data, audit


def conditioning_gate(history, residuals, end):
    """Predeclared investigator gate; no scalar/residual interpolation allowed."""
    assert end in range(200, 1001, 100)
    assert set(residuals) == ACTIVE_FLOW | {'iteration'}
    masks = []
    for lo, hi in [(end-199, end-100), (end-99, end)]:
        mask = (history['iteration'] >= lo) & (history['iteration'] <= hi)
        assert np.array_equal(history['iteration'][mask], np.arange(lo, hi+1))
        masks.append(mask)
    rm = (residuals['iteration'] >= end-99) & (residuals['iteration'] <= end)
    assert np.array_equal(residuals['iteration'][rm], np.arange(end-99, end+1))
    derived, _ = derive(history)
    maxima = {k: float(np.max(residuals[k][rm])) for k in sorted(ACTIVE_FLOW)}
    assert all(np.isfinite(v) and v >= 0 for v in maxima.values())
    closure = derived['mixture_closure_percent_feed'][masks[1]]
    assert np.isfinite(closure).all()
    changes = {}
    for key, floor in [('liquid_inlet_pressure_drop', 100.), ('steam_inlet_pressure_drop', 100.),
                       ('maximum_mixture_speed', 1.)]:
        values = derived[key]; assert np.isfinite(values).all()
        means = [float(values[m].mean()) for m in masks]
        changes[key] = {'earlier_mean': means[0], 'later_mean': means[1], 'denominator_floor': floor,
                        'absolute_change_percent': 100*abs(means[1]-means[0])/max(floor, *map(abs, means))}
    closure_ma = float(np.abs(closure).mean())
    passed = all(v < 1e-3 for v in maxima.values()) and closure_ma <= 1. and all(v['absolute_change_percent'] <= 1. for v in changes.values())
    return {'iteration': end, 'passed': bool(passed), 'active_residual_maxima': maxima,
            'mixture_closure_mean_absolute_percent_feed': closure_ma, 'mean_changes': changes,
            'windows': [[end-199, end-100], [end-99, end]], 'threshold_origin': 'Prospective investigator choices; not vendor numerical thresholds'}


def validate_inputs(reference_manifest, predecessor_manifest, setup_path):
    ref = json.loads(reference_manifest.read_text()); previous = json.loads(predecessor_manifest.read_text())
    assert ref['experiment_id'] == 'E6' and ref['tau_s'] == .02 and ref['percent'] == 40
    assert ref['completed_iterations'] == 5000 and ref['selected_methods']['p_v_coupling']['solve_n_phase'] is True
    assert ref['selected_controls']['equations'] == {'flow': True, 'ke': True, 'mp': True, 'drift': True}
    assert expected_residual_equations(ref) == ACTIVE_FULL
    assert previous['experiment_id'] == 'E7' and previous['completed_iterations'] == 5000
    assert previous['status'] == 'HORIZON_COMPLETE_ANALYSIS_PENDING'
    assert setup_path.is_file()
    original = Path(ref['parent_manifest']).parent
    assert (original/'pre-reopen-prepared/fields-n00000.npz').is_file()
    assert (original/'pre-reopen-prepared/geometry.npz').is_file()
    assert ref['pairs']['prepared'].endswith('-prepared.cas.h5')
    return ref, previous, original


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference-manifest', required=True, type=Path)
    ap.add_argument('--predecessor-manifest', required=True, type=Path)
    ap.add_argument('--setup', required=True, type=Path)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--recover-n0-from',type=Path,help='Preserved zero-iteration build failure only; exact live N0 is independently verified without reload')
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--validate-only', action='store_true'); mode.add_argument('--execute', action='store_true')
    mode.add_argument('--prepare-only', action='store_true', help='Live zero-iteration capability/save/reopen proof; never registers a solve callback')
    a = ap.parse_args()
    ref, previous, original = validate_inputs(a.reference_manifest, a.predecessor_manifest, a.setup)
    recovery=None
    if a.recover_n0_from:
        recovery=json.loads(a.recover_n0_from.read_text())
        assert recovery['experiment_id']=='E8' and recovery['iterations_issued']==0
        assert recovery['status']=='BLOCKED_EXECUTION_RECONCILE_REQUIRED'
        assert recovery['error'] in {'E6 physics user_defined.auto_compile_compiled_functions: reference mismatch','E6 physics reference_values.zone: reference mismatch'}
        assert recovery['parent_case']==ref['pairs']['prepared']
        assert any(v['name']=='verify_original_ordered_n0' and v['state']=='PASS' for v in recovery['steps'])
    assert re.fullmatch(r'p7b-[a-z0-9-]+-[0-9]{8}T[0-9]{6}Z', a.run_id)
    if a.validate_only:
        print(json.dumps({'status': 'E8_OFFLINE_INPUTS_PASS', 'connections': 0, 'conditioning_targets': CONDITIONING_TARGETS,
                          'absolute_cap': 5000, 'prepared_parent': ref['pairs']['prepared']})); return
    lock = (BASE/'output/phase07b-server1-controller.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    out = BASE/'output'/a.run_id; out.mkdir()
    lock.seek(0); lock.truncate(); lock.write(json.dumps({'pid': os.getpid(), 'run_id': a.run_id})); lock.flush()
    inherited = ['tau_s','percent','fluid_zones','definitions','source_slots','selected_methods','selected_controls',
                 'residual_equations','residual_options','report_definitions','sections','axial_sections','interface_proof']
    r = {k: copy.deepcopy(ref[k]) for k in inherited}
    r.update(run_id=a.run_id, experiment_id='E8', case_id='S40-T020-COUPLED-CFL20-NPHASE-STAGED',
             controller_pid=os.getpid(), status='BUILDING', steps=[], pairs={}, requested_iterations=5000,
             conditioning_cap=1000, minimum_full_equation_iterations=4000, actual_iteration=0, iterations_issued=0,
             start_iteration=0, selected_setup=str(a.setup.resolve()), expected_residual_equations=sorted(ACTIVE_FULL),
             parent_case=ref['pairs']['prepared'], comparison_reference=fingerprint(a.reference_manifest),
             predecessor=fingerprint(a.predecessor_manifest), design=fingerprint(a.setup),
             implementation=[fingerprint(Path(__file__)), fingerprint(BASE/'src/pyansys_fluent/phase07b_flux_monitor.py'),
                             fingerprint(BASE/'src/pyansys_fluent/phase07b_spike_monitor.py')],
             resume_policy='No automatic retry/replay; reconcile exact live counter and owned pause after uncertain RPC',
             conditioning_gates=[], residual_stages={}, remote_flux_readbacks=[])
    def persist():
        tmp=out/'manifest.tmp'; tmp.write_text(json.dumps(r, indent=2, default=str)+'\n'); tmp.replace(out/'manifest.json')
    def timeout(*_): raise TimeoutError('Uncertain RPC outcome: reconcile live state before retry')
    signal.signal(signal.SIGALRM, timeout)
    def step(name, fn, seconds=180):
        event={'name':name, 'state':'STARTED', 'started_utc':datetime.now(timezone.utc).isoformat()}
        r['steps'].append(event); persist(); print(name, flush=True); signal.alarm(seconds)
        try:
            value=fn(); event.update(state='PASS', value='attached' if name=='connect' else value); return value
        except Exception as exc: event.update(state='FAIL', error=str(exc)); raise
        finally: signal.alarm(0); event['ended_utc']=datetime.now(timezone.utc).isoformat(); persist()
    s=m=diag=None
    try:
        s=step('connect', lambda:connect(1,start_transcript=False,tcp_timeout_seconds=5),90)
        def n():
            value=s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()
            assert np.isfinite(value) and value==int(value); return int(value)
        def save(tag):
            p=ROOT+'/case-data/'+a.run_id+'-'+tag+'.cas.h5'
            assert not any(remote_file_exists(s,p.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            step('save_'+tag,lambda:s.settings.file.write_case_data(file_name=p),300)
            assert all(remote_file_exists(s,p.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            r['pairs'][tag]=p; persist(); return p
        def verify_settings(reference, frozen=False):
            controls=copy.deepcopy(reference['selected_controls'])
            if frozen: controls['equations'].update(mp=False,drift=False)
            for key, node in [('selected_methods',s.settings.solution.methods),('residual_options',s.settings.solution.monitor.residual.options),
                              ('report_definitions',s.settings.solution.report_definitions)]:
                exact_parity(reference[key],node.get_state(),key)
            monitors=s.settings.solution.monitor.residual.equations.get_state()
            required=ACTIVE_FLOW if frozen else ACTIVE_FULL
            assert required<=set(monitors)<=ACTIVE_FULL, ('Unexpected monitor visibility',monitors)
            for eq,value in monitors.items(): exact_parity(reference['residual_equations'][eq],value,'residual policy '+eq)
            r.setdefault('monitor_visibility_readbacks',[]).append({'iteration':n(),'frozen':frozen,'exposed_monitors':sorted(monitors)})
            exact_parity(controls,s.settings.solution.controls.get_state(),'controls')
            for name,d in reference['definitions'].items(): assert s.settings.setup.named_expressions[name].definition()==d,name
            for z,phases in reference['source_slots'].items():
                for ph,slots in phases.items(): exact_parity(slots,s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state(),z+'.'+ph)
            assert s.settings.solution.run_calculation.profile_update_interval()==1
            return controls
        def exact_original_n0(tag):
            assert n()==0 and not s.settings.solution.run_calculation.iterating()
            directory=out/tag; directory.mkdir(); records=[]
            for filename in ['geometry.npz','fields-n00000.npz']:
                reference=original/'pre-reopen-prepared'/filename; actual={}
                with np.load(reference) as expected:
                    keys=[k for k in expected.files if 'MASS_IMBALANCE' not in k]
                    for domain,var in sorted({tuple(k.split('_',2)[1:]) for k in keys}):
                        data=s.fields.solution_variable_data.get_data(variable_name=var,zone_names=r['fluid_zones'],domain_name=domain)
                        for i,z in enumerate(r['fluid_zones']): actual[f'z{i}_{domain}_{var}']=np.asarray(data[z])
                    np.savez_compressed(directory/filename,**actual)
                    assert set(actual)==set(keys)
                    for k in keys: assert np.array_equal(actual[k],expected[k]), ('N0 parity',tag,k)
                records.append({'reference':fingerprint(reference),'actual':fingerprint(directory/filename)})
            assert n()==0
            return {'status':'EXACT_ORDERED_N0_FIELDS_GEOMETRY_PASS','datasets':records,'iterations_issued':0}
        def phase_state(tag):
            data={}
            for ph in ['mixture','phase-1','phase-2']:
                variables=SLIP_VARIABLES+(['SV_VOF','SV_U','SV_V','SV_W'] if ph!='mixture' else [])
                inventory=s.fields.solution_variable_info.get_variables_info(zone_names=r['fluid_zones'],domain_name=ph)
                exposed=list(inventory.solution_variables)
                assert set(variables)<=set(exposed), ('Required N0/current phase storage unavailable',ph,variables,exposed)
                r.setdefault('phase_storage_inventory',{})[ph]=exposed
                for var in variables:
                    arrays=s.fields.solution_variable_data.get_data(variable_name=var,zone_names=r['fluid_zones'],domain_name=ph)
                    for i,z in enumerate(r['fluid_zones']):
                        data[f'z{i}_{ph}_{var}']=np.asarray(arrays[z])
                        with np.load(original/'pre-reopen-prepared/geometry.npz') as geometry:
                            assert data[f'z{i}_{ph}_{var}'].size==len(geometry[f'z{i}_mixture_SV_VOLUME'])>0, ('Phase storage cell count',ph,var,z)
                        assert np.isfinite(data[f'z{i}_{ph}_{var}']).all()
            p=out/(tag+'.npz'); assert not p.exists(); np.savez_compressed(p,**data)
            return data
        def verify_frozen_phases(current, initial):
            return verify_frozen_phase_arrays(current,initial,r['fluid_zones'])
        assert not s.settings.solution.run_calculation.iterating()
        assert all(remote_file_exists(s,previous['pairs']['final'].replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
        if recovery is None:
            assert n()==5000
            step('verify_preserved_e7_settings',lambda:verify_settings(previous))
            save('e7-predecessor-preserved')
            if s.settings.file.stop_transcript.is_active(): s.settings.file.stop_transcript()
            step('load_verified_e6_prepared_n0',lambda:s.settings.file.read_case_data(file_name=r['parent_case']),600)
        else:
            assert n()==0
            r['recovered_n0_from']=fingerprint(a.recover_n0_from)
            r['pairs']['e7-predecessor-preserved']=recovery['pairs']['e7-predecessor-preserved']
            assert all(remote_file_exists(s,r['pairs']['e7-predecessor-preserved'].replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            r['n0_recovery']={'reloads':0,'initializations':0,'counter_offsets':0,'iterations_issued':0}
        step('verify_e6_prepared_settings',lambda:verify_settings(ref))
        r['initial_parity']=step('verify_original_ordered_n0',lambda:exact_original_n0('loaded-n0-parity'),300)
        # Session preference, not a scientific source/model delta. The original
        # Python-only E6 reference explicitly requires this false.
        before_setup=s.settings.setup.get_state()
        assert ref['reference_setup']['user_defined']['auto_compile_compiled_functions'] is False
        s.settings.setup.user_defined.auto_compile_compiled_functions=False
        expected_setup=copy.deepcopy(before_setup)
        expected_setup['user_defined']['auto_compile_compiled_functions']=False
        baseline_setup=s.settings.setup.get_state()
        exact_parity(expected_setup,baseline_setup,'sole restored session preference')
        assert n()==0
        r['restored_session_preference']={'before':before_setup['user_defined']['auto_compile_compiled_functions'],'after':False,'basis':'Exact original E6 Python-only reference; no compiled source added'}
        # reference_setup predates the already verified E6 collector partition.
        # Accept only the observed reference-zone label and exact wall clone;
        # no boundary/material/flow setting is changed to make this comparison.
        comparable=copy.deepcopy(ref['reference_setup'])
        assert comparable['reference_values']['zone']==''
        assert baseline_setup['reference_values']['zone']==ZONE
        comparable['reference_values']['zone']=ZONE
        walls=comparable['boundary_conditions']['wall']
        assert set(baseline_setup['boundary_conditions']['wall'])==set(walls)|{'wall:010'}
        walls['wall:010']=copy.deepcopy(walls['wall']);walls['wall:010']['name']='wall:010'
        for key in set(comparable)-{'cell_zone_conditions','boundary_conditions','named_expressions'}:
            exact_parity(comparable[key],baseline_setup[key],'E6 physics '+key)
        for key in set(comparable['boundary_conditions'])-{'interior'}:
            exact_parity(comparable['boundary_conditions'][key],baseline_setup['boundary_conditions'][key],'E6 boundary '+key)
        r['prepared_partition_metadata']={'reference_zone':ZONE,'additional_wall':'wall:010','wall_properties':'exact clone of original wall','settings_mutated':False,'basis':'Original E6 prepared pair includes collector partition; reference_setup is prepartition'}
        refzone=copy.deepcopy(ref['reference_setup']['cell_zone_conditions']['fluid'][ZONE]); refzone.pop('name')
        for ph in refzone['phase']: refzone['phase'][ph].pop('sources')
        for zone in r['fluid_zones']:
            child=copy.deepcopy(baseline_setup['cell_zone_conditions']['fluid'][zone]); child.pop('name')
            for ph in child['phase']: child['phase'][ph].pop('sources')
            exact_parity(refzone,child,'E6 fluid properties '+zone)
        (out/'prepared-setup.json').write_text(json.dumps(baseline_setup,indent=2))
        loaded_phase=phase_state('loaded-phase-n00000')
        def equations(frozen):
            wanted=copy.deepcopy(ref['selected_controls']['equations'])
            if frozen: wanted.update(mp=False,drift=False)
            s.settings.solution.controls.equations.set_state(wanted)
            verify_settings(ref,frozen)
            exact_parity(baseline_setup,s.settings.setup.get_state(),'startup setup invariant')
            assert n()==0
            return s.settings.solution.controls.equations.get_state()
        r['freeze_probe']=step('probe_freeze_both_no_solve',lambda:equations(True))
        step('verify_frozen_n0_fields',lambda:exact_original_n0('probe-frozen-n0-parity'),300)
        r['restore_probe']=step('probe_restore_both_no_solve',lambda:equations(False))
        step('verify_restored_n0_fields',lambda:exact_original_n0('probe-restored-n0-parity'),300)
        step('freeze_both_for_conditioning',lambda:equations(True))
        prepared=save('prepared-frozen-n00000')
        step('reopen_child_frozen_n0',lambda:s.settings.file.read_case_data(file_name=prepared),600)
        step('verify_reopened_child_controls',lambda:verify_settings(ref,True))
        step('verify_reopened_ordered_n0',lambda:exact_original_n0('reopened-n0-parity'),300)
        exact_parity(baseline_setup,s.settings.setup.get_state(),'reopened setup invariant')
        frozen_initial=phase_state('frozen-phase-n00000')
        assert all(np.array_equal(frozen_initial[k],loaded_phase[k]) for k in loaded_phase), 'Zero-step freeze/restore/reopen changed phase storage'
        r['frozen_phase_reference']=fingerprint(out/'frozen-phase-n00000.npz')
        assert all(np.all(frozen_initial[f'z{i}_phase-1_SV_VOF']==1) and np.all(frozen_initial[f'z{i}_phase-2_SV_VOF']==0) for i in range(len(r['fluid_zones'])))
        if a.prepare_only:
            r.update(status='PREPARED_ZERO_ITERATION_CAPABILITY_PASS',actual_iteration=n(),iterations_issued=0,
                     next_action='Read-only prepared-state proof complete. This script does not auto-resume or solve a prepared-only run.')
            persist(); return
        files=s.settings.solution.monitor.report_files
        for name in files.get_object_names(): files[name].active=False
        report=files['p7b-screen-history']; destination=ROOT+'/reports/'+a.run_id+'-scalar.out'
        assert not remote_file_exists(s,destination)
        report.file_name=destination; report.active=True
        r['report']=resolved_native_report_path(report.get_state(),destination)
        assert not remote_file_exists(s,r['report'])
        assert report.frequency()==1
        r['report_policy']=report.get_state(); r['native_report_segment_base']=destination
        r['initial_sections']=step('initial_sections',lambda:export_sections(s,r['sections'],out/'initial-sections'),300)
        r['initial_axial_sections']=step('initial_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'initial-axial-sections'),300)
        diag=Phase07bSpikeMonitor(s,r['fluid_zones'],out/'spike-diagnostics',solve_n_phase=True)
        step('prepare_normalized_native_diagnostics',diag.prepare,300)
        faces=[FluxFaceZone(**v) for v in ref['flux_monitor']['face_zones']]
        m=Phase07bFluxMonitor(s,face_zones=faces,start_iteration=0,local_jsonl=out/'collector-flux.jsonl',remote_directory=ROOT+'/reports',after_capture=diag.capture)
        cb=m.register(); r['pause_registration_ids']=dict(s.events._sync_event_ids)
        assert cb in r['pause_registration_ids'] and len(r['pause_registration_ids'])==1
        def begin_stage(stage):
            local=out/(stage+'-solve.trn'); remote=ROOT+'/reports/'+a.run_id+'-'+stage+'.trn'
            assert not remote_file_exists(s,remote)
            s.transcript.start(file_name=str(local),write_to_stdout=False)
            s.settings.file.start_transcript(file_name=remote)
            r['residual_stages'][stage]={'local':str(local),'remote':remote,'start_exclusive':n()}; persist()
        def end_stage():
            s.settings.file.stop_transcript(); s.transcript.stop()
        current=0; switch=None; begin_stage('conditioning'); r['status']='CONDITIONING_RUNNING'; persist()
        def advance(target,stage):
            nonlocal current
            verify_settings(ref,stage=='conditioning'); assert n()==current
            r['issued_block']={'start':current,'end':target,'stage':stage}; r['iterations_issued']+=target-current; persist()
            step(f'iterate_{stage}_{current}_to_{target}',lambda:s.settings.solution.run_calculation.iterate(iter_count=target-current),max(600,(target-current)*20))
            assert n()==target and not s.settings.solution.run_calculation.iterating()
            current=target; r['actual_iteration']=target
            m.assert_complete(target); diag.assert_complete(target)
            r['flux_monitor']=m.manifest(); r['spike_diagnostics']=diag.manifest()
            verify_settings(ref,stage=='conditioning')
            r['report']=resolved_native_report_path(report.get_state(),destination)
            path=out/f'history-{target:05d}.out'; assert not path.exists(); path.write_text(read_text(s,r['report']))
            history,ha=parse_history(path)
            assert np.array_equal(history['iteration'],np.arange(1,target+1))
            assert not ha['conflicting_indices'] and not ha['nonfinite_columns'] and not ha['rejected_lines']
            derived,_=derive(history); lag=float(np.max(abs(derived['native_applied_removal'][1:]-derived['current_expression_removal'][:-1])))
            assert lag<=1e-9, ('Source lag mismatch',lag)
            r['scalar_coverage']={'audit':ha,'lag_pairs':target-1,'lag_max_abs_error_kg_s':lag}
            tr=out/f'{stage}-native-to-{target:05d}.trn'; tr.write_text(read_text(s,r['residual_stages'][stage]['remote']))
            assert not any(marker in tr.read_text() for marker in FATAL)
            data,ra=parse_stage_residuals(tr,stage,r['residual_stages'][stage]['start_exclusive'],target)
            r['residual_stages'][stage].update(latest_native_snapshot=str(tr),audit=ra,end_inclusive=target)
            last=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1])
            assert json.loads(read_text(s,last['remote_path']))==last
            r['remote_flux_readbacks'].append({'iteration':target,'path':last['remote_path'],'matches_local':True})
            if stage=='conditioning':
                phase=phase_state(f'frozen-phase-n{target:05d}')
                r.setdefault('frozen_field_proofs',{})[str(target)]=verify_frozen_phases(phase,frozen_initial)
            if target==50 or target%500==0: save('final' if target==5000 else f'n{target:05d}')
            if target==50:
                smoke={'status':'CONDITIONING_N50_RECORDING_PASS','active_residuals':sorted(ACTIVE_FLOW),'iteration':50,
                       'source_lag':r['scalar_coverage'],'frozen_field_proof':r['frozen_field_proofs']['50']}
                (out/'smoke-n00050.json').write_text(json.dumps(smoke,indent=2))
            persist(); return history,data
        for target in CONDITIONING_TARGETS:
            history,residuals=advance(target,'conditioning')
            if target>=200:
                gate=conditioning_gate(history,residuals,target); r['conditioning_gates'].append(gate); persist()
                if gate['passed']: switch=target; break
        end_stage(); r['conditioning_end_iteration']=current
        if switch is not None:
            assert 200<=switch<=1000
            if not any(v['iteration']==switch for v in diag.snapshots): diag.snapshot(switch,diag.value('P7bMaximumSpeed'),['conditioning_switch'])
            save(f'conditioning-pass-n{switch:05d}')
            before=phase_state(f'switch-before-n{switch:05d}')
            s.settings.solution.controls.equations.set_state(ref['selected_controls']['equations'])
            step('verify_full_equations_restored',lambda:verify_settings(ref))
            after=phase_state(f'switch-after-n{switch:05d}')
            assert all(np.array_equal(before[k],after[k]) for k in before), 'Equation restore changed fields before solve'
            exact_parity(baseline_setup,s.settings.setup.get_state(),'switch setup invariant'); assert n()==switch
            save(f'full-equations-restored-n{switch:05d}')
            r.update(status='FULL_EQUATIONS_RUNNING',switch_iteration=switch); begin_stage('full')
            for target in range((switch//500+1)*500,5001,500): advance(target,'full')
            end_stage(); assert current==5000 and current-switch>=4000
            r['full_equation_iterations']=current-switch
            r['status']='HORIZON_COMPLETE_ANALYSIS_PENDING'
        else:
            assert current==1000
            save('conditioning-gate-not-met-final')
            r.update(status='CONDITIONING_GATE_NOT_MET',full_equation_iterations=0,
                     numerical_disposition='Initial flow did not meet the prospectively bounded conditioning gate; full-equation startup contrast untested')
        m.unregister(); r['flux_monitor']=m.manifest(); m=None
        r['final_sections']=step('final_sections',lambda:export_sections(s,r['sections'],out/'final-sections'),300)
        r['final_axial_sections']=step('final_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'final-axial-sections'),300)
        r['completed_iterations']=current; r['terminal_artifacts_verified']=True; persist()
    except Exception as exc:
        signal.alarm(0); r.update(status='BLOCKED_EXECUTION_RECONCILE_REQUIRED',error=str(exc))
        (out/'error.txt').write_text(traceback.format_exc()); persist(); raise
    finally:
        signal.alarm(0)
        if m is not None:
            try: m.unregister()
            except Exception as exc: r['callback_cleanup_error']=str(exc)
            r['flux_monitor']=m.manifest()
        if diag is not None: diag.close(); r['spike_diagnostics']=diag.manifest()
        if s is not None:
            try: s.transcript.stop()
            except Exception: pass
        persist(); print('EVIDENCE',out,flush=True)


if __name__=='__main__': main()
