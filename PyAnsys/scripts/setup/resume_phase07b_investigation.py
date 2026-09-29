"""Resume verified E6/E7 live checkpoint to N5000 without reinitialization.

Requires a separately repaired, complete diagnostic prefix. No failed evidence
is overwritten, no counter offset is allowed, and no foreign callback is removed.
"""
from run_phase07b_screen import *
import shutil
import threading
from pyansys_fluent.phase07b_spike_monitor import Phase07bSpikeMonitor, SpikeSchedule
from analyze_phase07b_screen import parse_history, derive
from pathlib import PureWindowsPath

START = 50
HORIZON = 5000
TARGETS = [55] + list(range(500, HORIZON + 1, 500))
FATAL = ['SEGMENTATION VIOLATION', 'floating point exception', 'Divergence detected']


def fingerprint(path):
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def jsonl(path, end):
    text = path.read_text()
    assert text.endswith('\n'), ('Incomplete JSONL', str(path))
    rows = [json.loads(line) for line in text.splitlines()]
    assert [row['iteration'] for row in rows] == list(range(1, end + 1)), str(path)
    return rows


def validate_inputs(parent_manifest, preservation_receipt, recovered):
    """File-only contract validation; no connection or mutation."""
    old = json.loads(parent_manifest.read_text())
    receipt = json.loads(preservation_receipt.read_text())
    parent = parent_manifest.parent
    expected_cases = {'E6': ('S40-T020-COUPLED-CFL20-NPHASE', .02),
                      'E7': ('S40-T100-COUPLED-CFL20-NPHASE', .1)}
    case, tau = expected_cases[old['experiment_id']]
    assert old['case_id'] == case
    assert old['percent'] == 40 and old['tau_s'] == tau and old['requested_iterations'] == HORIZON
    assert old['selected_methods']['p_v_coupling']['solve_n_phase'] is True
    assert old['selected_controls']['p_v_controls']['flow_courant_number'] == 20.
    assert old['actual_iteration'] == START
    expected = expected_residual_equations(old)
    assert len(expected) == 8 and 'vf-phase-1' in expected
    assert receipt['status'] == 'PRESERVED_PAUSED_STATE' and receipt['parent_run_id'] == old['run_id']
    assert receipt['iteration'] == START and receipt['iterating'] is False and receipt['iterations_issued'] == 0
    assert receipt['pair_exists'] is True and receipt['case'].endswith('.cas.h5')
    assert receipt['data'] == receipt['case'].replace('.cas.h5', '.dat.h5')
    exact_parity(old['selected_methods'], receipt['selected_methods'], 'preserved methods')
    exact_parity(old['selected_controls'], receipt['selected_controls'], 'preserved controls')
    native = receipt['native_field_checks']
    assert native['iteration'] == START
    for key in ['same_iteration_before_after', 'physical_fields_finite', 'geometry_matches_initial']:
        assert native[key] is True, key
    assert Path(native['source_lag_evidence']).is_file()
    flux = jsonl(parent / 'collector-flux.jsonl', START)
    assert all(np.isfinite(row[key]) for row in flux for key in ['delivery_kg_s', 'escape_kg_s', 'net_outward_kg_s'])
    speed = jsonl(recovered / 'spike-history.jsonl', START)
    assert all(np.isfinite(row['max_speed_m_s']) for row in speed)
    dm = json.loads((recovered / 'manifest.json').read_text())
    assert dm['last_iteration'] == START and dm['error'] is None
    schedule = SpikeSchedule()
    required = {0: ['scheduled_initial_proof']}
    for row in speed:
        reasons = schedule.reasons(row['iteration'], row['max_speed_m_s'])
        assert reasons == row['snapshot_reasons'], row['iteration']
        if reasons: required[row['iteration']] = reasons
    assert len({snap['iteration'] for snap in dm['snapshots']}) == len(dm['snapshots'])
    extras = old.get('verified_recovery_snapshot_iterations', [])
    assert set(extras) <= {505, 687, 1631, 2185, 2505, 3227} and (not extras or old['experiment_id']=='E7')
    for iteration in extras:
        assert iteration <= START
        required[iteration] = ['recovery_semantics_validation']
    assert {snap['iteration'] for snap in dm['snapshots']} == set(required)
    with np.load(recovered / 'geometry.npz') as geo, np.load(parent / 'spike-diagnostics/geometry.npz') as original:
        assert set(geo.files) == set(original.files)
        assert all(np.array_equal(geo[key], original[key]) for key in geo.files)
        for snap in dm['snapshots']:
            path = recovered / f"fields-n{snap['iteration']:05d}.npz"
            assert fingerprint(path)['sha256'] == snap['sha256']
            meta = json.loads(path.with_suffix('.json').read_text())
            assert meta['iteration'] == snap['iteration'] and meta['same_iteration_before_after'] is True
            assert snap['reasons'] == meta['reasons'] == required[snap['iteration']]
            assert meta['sha256'] == snap['sha256']
            if snap['iteration']:
                assert meta['inventory_reconstruction']['mode'] == 'cellwise_normalized_raw_phase_vector'
            with np.load(path) as fields:
                assert all(np.isfinite(fields[key]).all() for key in fields.files)
                maxima = {key: max(float(np.max(fields[f'z{i}_mixture_SV_{variable}'])) for i in range(2))
                          for key, variable in [('k', 'K'), ('epsilon', 'D')]}
                maxima['speed'] = max(float(np.sqrt(sum(fields[f'z{i}_mixture_SV_{axis}']**2 for axis in 'UVW')).max()) for i in range(2))
                water = 0.
                for i in range(2):
                    alpha = fields[f'z{i}_phase-2_SV_VOF']
                    primary = f'z{i}_phase-1_SV_VOF'
                    if primary in fields:
                        total = alpha + fields[primary]
                        assert np.isfinite(total).all() and np.all(total > 0), (snap['iteration'], primary)
                        alpha = alpha / total
                    else:
                        # Immutable original N0 predates the added primary capture.
                        assert snap['iteration'] == 0 and np.all(alpha == 0), 'Missing E6 primary raw fraction'
                    water += float(np.dot(alpha, geo[f'z{i}_mixture_SV_VOLUME']))
                maxima['water'] = water
                for key, value in maxima.items():
                    assert math.isclose(value, meta['native'][key], rel_tol=1e-9, abs_tol=1e-12), (snap['iteration'], key)
                if snap['iteration']:
                    assert meta['native']['speed'] == speed[snap['iteration']-1]['max_speed_m_s']
    for folder in ['initial-sections', 'initial-axial-sections']:
        assert (parent / folder / 'index.json').is_file()
    for name in ['initial-parity.json', 'initial-geometry-parity.json']:
        assert (parent / name).is_file()
    return old, receipt, dm, speed, flux


def scalar_audit(path, end):
    data, audit = parse_history(path)
    assert np.array_equal(data['iteration'], np.arange(1, end + 1))
    assert not audit['conflicting_indices'] and not audit['nonfinite_columns']
    derived, _ = derive(data)
    lag = float(np.max(np.abs(derived['native_applied_removal'][1:] - derived['current_expression_removal'][:-1])))
    return {'history': audit, 'source_lag_max_abs_error_kg_s': lag,
            'source_lag_pairs': end - 1, 'source_lag_warning': lag > 1e-9}


def residual_audit(path, expected, end):
    data, audit = parse_residuals(path)
    assert set(data) == {'iteration'} | expected
    assert np.array_equal(data['iteration'], np.arange(1, end + 1))
    assert not audit['conflicting_indices'] and not audit['nonfinite_columns']
    assert not any(marker in path.read_text() for marker in FATAL)
    return audit


def resolved_native_report_path(state, requested):
    """Accept only the requested report or its live-reported iteration suffix."""
    base=PureWindowsPath(requested)
    actual=PureWindowsPath(state['file_name'])
    if not actual.is_absolute():
        assert actual.parent==PureWindowsPath('reports'), actual
        actual=base.parent/actual.name
    assert actual.parent==base.parent, (actual,base)
    index=str(state.get('itr_index',''))
    allowed={base.name}
    if index.isdigit(): allowed.add(base.stem+'_'+index+base.suffix)
    assert actual.name in allowed, (actual,allowed)
    return actual.as_posix()


def read_scalar_snapshot(s, manifest, out, end):
    """Join an immutable checkpoint prefix to Fluent's distinct native segment.

    Fluent rolls an existing report destination to an iteration-suffixed file
    after a case reload. Preserve that segment verbatim and require strict
    continuity before constructing the combined analysis history. A repeated
    checkpoint row is allowed only if every scalar exactly matches the prefix.
    """
    if manifest.get('native_report_segment_base'):
        state=s.settings.solution.monitor.report_files['p7b-screen-history'].get_state()
        manifest['report']=resolved_native_report_path(state,manifest['native_report_segment_base'])
        manifest.setdefault('native_report_path_readbacks',[]).append({'iteration':end,'path':manifest['report'],'itr_index':state.get('itr_index')})
    remote = read_text(s, manifest['report'])
    raw = out/f'native-history-segment-{end:05d}.out'
    assert not raw.exists(); raw.write_text(remote)
    prefix = manifest.get('native_scalar_prefix')
    if prefix:
        path = Path(prefix['path'])
        assert fingerprint(path)['sha256'] == prefix['sha256']
        first, fa = parse_history(path); segment, sa = parse_history(raw)
        assert fa['native_header'] == sa['native_header']
        assert np.array_equal(first['iteration'], np.arange(1, prefix['end_iteration']+1))
        start=int(segment['iteration'][0]); boundary=prefix['end_iteration']
        assert start in {boundary,boundary+1}
        assert np.array_equal(segment['iteration'], np.arange(start,end+1))
        if start==boundary:
            assert all(first[key][-1]==segment[key][0] for key in first), 'Conflicting native restart boundary row'
        assert not sa['conflicting_indices'] and not sa['nonfinite_columns'] and not sa['rejected_lines']
        remote = path.read_text().rstrip('\n')+'\n'+remote
    combined=out/f'history-{end:05d}.out'
    assert not combined.exists(); combined.write_text(remote)
    return scalar_audit(combined,end)


def main():
    global START, TARGETS
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-manifest', type=Path, required=True)
    ap.add_argument('--preservation-receipt', type=Path, required=True)
    ap.add_argument('--recovered-diagnostic-directory', type=Path, required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--start-iteration', type=int, choices=[50, 500, 505, 687, 1631, 2185, 2500, 3227], default=50,
                    help='Exact verified live checkpoint; never a counter offset')
    ap.add_argument('--validate-only', action='store_true', help='Validate local receipts and evidence without connecting')
    a = ap.parse_args()
    START = a.start_iteration
    TARGETS = ([] if START in {505, 687, 1631, 2185, 3227} else [START + 5]) + list(range((START // 500 + 1) * 500, HORIZON + 1, 500))
    assert re.fullmatch(r'p7b-[a-z0-9-]+-[0-9]{8}T[0-9]{6}Z', a.run_id)
    old, receipt, dm, speed, flux = validate_inputs(a.parent_manifest, a.preservation_receipt, a.recovered_diagnostic_directory)
    assert a.run_id != old['run_id']
    if a.validate_only:
        print(json.dumps({'status': 'LOCAL_RECOVERY_INPUTS_PASS', 'start_iteration': START, 'targets': TARGETS,
                          'residuals': sorted(expected_residual_equations(old)), 'fluent_connections': 0})); return
    parent = a.parent_manifest.parent
    lock = (BASE / 'output/phase07b-server1-controller.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    out = BASE / 'output' / a.run_id; out.mkdir()
    lock.seek(0); lock.truncate(); lock.write(json.dumps({'pid': os.getpid(), 'run_id': a.run_id})); lock.flush()
    r = copy.deepcopy(old)
    r.update(run_id=a.run_id, controller_pid=os.getpid(), steps=[], status='VERIFYING_RECOVERY', error=None,
             actual_iteration=START, start_iteration=START, prefix_end=START, segment_iterations=0,
             parent_manifest=str(a.parent_manifest.resolve()), preservation_receipt=str(a.preservation_receipt.resolve()),
             recovered_diagnostic_directory=str(a.recovered_diagnostic_directory.resolve()),
             resume_mode=f'unchanged verified live N{START}; no controller reload/initialization/counter offset',
             recovery_inputs=[fingerprint(a.parent_manifest), fingerprint(a.preservation_receipt), fingerprint(a.recovered_diagnostic_directory/'manifest.json')],
             recovery_targets=TARGETS, remote_flux_readbacks=[])
    r.pop('callback_cleanup_error', None)
    r.pop('pause_registration_ids', None)
    r['pairs'][f'n{START:05d}'] = receipt['case']
    r['pairs']['recovery-preserved'] = receipt['case']
    r['implementation_sha256'][str(Path(__file__).resolve())] = fingerprint(Path(__file__))['sha256']
    monitor_path=Path(sys.modules[Phase07bSpikeMonitor.__module__].__file__).resolve()
    r['implementation_sha256'][str(monitor_path)] = fingerprint(monitor_path)['sha256']
    r['remote_transcript_prefix'] = old['remote_transcript']
    r['remote_transcript'] = ROOT + '/reports/' + a.run_id + '-solve.trn'
    mux = threading.RLock()
    def persist():
        with mux:
            temp=out/'manifest.tmp'; temp.write_text(json.dumps(r, indent=2, default=str)+'\n'); temp.replace(out/'manifest.json')
    def timeout(*_): raise TimeoutError('RPC deadline; reconcile before retry')
    signal.signal(signal.SIGALRM, timeout)
    def step(name, fn, seconds=90):
        event={'name':name, 'state':'STARTED', 'started_utc':datetime.now(timezone.utc).isoformat()}; r['steps'].append(event); persist(); print(name, flush=True); signal.alarm(seconds)
        try:
            value=fn(); event.update(state='PASS', value='attached, cleanup_on_exit=False' if name=='connect' else value); return value
        except Exception as exc: event.update(state='FAIL', error=str(exc)); raise
        finally: signal.alarm(0); event['ended_utc']=datetime.now(timezone.utc).isoformat(); persist()
    s=m=diag=None; transcript_cb=None
    try:
        s=step('connect', lambda:connect(1, start_transcript=False, tcp_timeout_seconds=5), 90)
        def n():
            value=s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()
            assert np.isfinite(value) and value == int(value); return int(value)
        def verify():
            assert n()==START and not s.settings.solution.run_calculation.iterating()
            assert all(remote_file_exists(s, receipt[key]) for key in ['case', 'data'])
            for name, definition in old['definitions'].items(): assert s.settings.setup.named_expressions[name].definition()==definition, name
            for zone, phases in old['source_slots'].items():
                for phase, slots in phases.items(): exact_parity(slots, s.settings.setup.cell_zone_conditions.fluid[zone].phase[phase].sources.get_state(), zone+'.'+phase)
            for key, live in [('selected_methods', s.settings.solution.methods), ('selected_controls', s.settings.solution.controls),
                              ('residual_options', s.settings.solution.monitor.residual.options), ('residual_equations', s.settings.solution.monitor.residual.equations),
                              ('report_definitions', s.settings.solution.report_definitions)]: exact_parity(old[key], live.get_state(), key)
            assert s.settings.solution.run_calculation.profile_update_interval()==1
            report_file=s.settings.solution.monitor.report_files['p7b-screen-history'].get_state()
            wanted=PureWindowsPath(old['report'])
            assert PureWindowsPath(report_file['file_name']) in {wanted,PureWindowsPath('reports')/wanted.name}
            assert report_file['active'] and report_file['frequency_of']=='iteration' and report_file['frequency']==1
            info=s.fields.solution_variable_info.get_zones_info()
            assert info['p7b-collector'].count==COUNTS[40] and sum(info[z].count for z in old['fluid_zones'])==620431
            # Recheck the preserved endpoint against the repaired full-cell snapshot.
            with np.load(a.recovered_diagnostic_directory/'geometry.npz') as geometry, np.load(a.recovered_diagnostic_directory/f'fields-n{START:05d}.npz') as fields:
                arrays={key:geometry[key] for key in geometry.files}; arrays.update({key:fields[key] for key in fields.files if 'MASS_IMBALANCE' not in key})
                requests={tuple(key.split('_',2)[1:]) for key in arrays}
                for domain, variable in sorted(requests):
                    values=s.fields.solution_variable_data.get_data(variable_name=variable,zone_names=old['fluid_zones'],domain_name=domain)
                    for i, zone in enumerate(old['fluid_zones']):
                        key=f'z{i}_{domain}_{variable}'; assert np.array_equal(np.asarray(values[zone]),arrays[key]), key
            endpoint=json.loads((a.recovered_diagnostic_directory/f'fields-n{START:05d}.json').read_text())
            for key, name in [('speed','P7bMaximumSpeed'),('k','P7bDiagnosticMaxK'),('epsilon','P7bDiagnosticMaxEpsilon'),('water','P7bWaterVolume')]:
                value=float(s.settings.setup.named_expressions[name].get_value())
                assert math.isclose(value,endpoint['native'][key],rel_tol=1e-9,abs_tol=1e-12), (key,value,endpoint['native'][key])
            scalar=read_scalar_snapshot(s,old,out,START)
            native=read_text(s,old['remote_transcript']); (out/'solve.trn').write_text(native)
            residual=residual_audit(out/'solve.trn',expected_residual_equations(old),START)
            assert json.loads(read_text(s,flux[-1]['remote_path']))==flux[-1]
            assert n()==START and not s.settings.solution.run_calculation.iterating()
            return {'live_iteration':START,'iterating':False,'exact_endpoint_fields':True,'settings_match':True,
                    'scalar':scalar,'residual':residual,'native_flux_prefix_readback':True,'iterations_issued':0}
        r['recovery_verification']=step('verify_live_state_and_prefix',verify,240)
        if old.get('start_new_native_report_segment'):
            assert old['experiment_id']=='E7' and START==2500
            prefix=parent/f'history-{START:05d}.out'
            assert scalar_audit(prefix,START)['source_lag_max_abs_error_kg_s']<=1e-9
            destination=ROOT+'/reports/'+a.run_id+'-scalar.out'
            assert not remote_file_exists(s,destination)
            report_file=s.settings.solution.monitor.report_files['p7b-screen-history']
            report_file.file_name=destination
            actual=resolved_native_report_path(report_file.get_state(),destination)
            assert not remote_file_exists(s,actual)
            r['native_scalar_prefix']={**fingerprint(prefix),'end_iteration':START}
            r['report']=actual
            r['native_report_segment_base']=destination
            r['native_report_segment_policy']='Fresh absent destination after exact prefix verification; preserve immutable prefix and raw native segment separately'
            persist()
        r['remote_flux_readbacks'].append({'iteration':START,'path':flux[-1]['remote_path'],'matches_local':True})
        for folder in ['initial-sections','initial-axial-sections','pre-reopen-initial','pre-reopen-prepared']:
            if (parent/folder).exists(): shutil.copytree(parent/folder,out/folder)
        for name in ['initial-parity.json','initial-geometry-parity.json','configuration-parity.json','setup.trn','smoke-n00050.json']:
            if (parent/name).exists(): shutil.copy2(parent/name,out/name)
        for path in parent.glob('interface-*.npz'): shutil.copy2(path,out/path.name)
        for path in parent.glob('history-*.out'):
            if not (out/path.name).exists(): shutil.copy2(path,out/path.name)
        def append_transcript(text):
            with (out/'solve.trn').open('a') as stream: stream.write(text)
        s.transcript.start(file_name=str(out/'solve-segment.trn'),write_to_stdout=False)
        transcript_cb=s.transcript.register_callback(append_transcript,keep_new_lines=True)
        if s.settings.file.stop_transcript.is_active(): step('close_preserved_native_transcript',s.settings.file.stop_transcript)
        assert not remote_file_exists(s,r['remote_transcript'])
        step('start_unique_native_transcript',lambda:s.settings.file.start_transcript(file_name=r['remote_transcript']))
        diag=Phase07bSpikeMonitor(s,old['fluid_zones'],out/'spike-diagnostics',solve_n_phase=True)
        for path in a.recovered_diagnostic_directory.glob('fields-*'): shutil.copy2(path,diag.directory/path.name)
        shutil.copy2(a.recovered_diagnostic_directory/'geometry.npz',diag.directory/'geometry.npz')
        with np.load(diag.directory/'geometry.npz') as geo: diag.geometry={key:geo[key] for key in geo.files}
        for snap in dm['snapshots']:
            snap=dict(snap); snap['path']=str((diag.directory/Path(snap['path']).name).resolve()); diag.snapshots.append(snap)
        for row in speed: assert diag.schedule.reasons(row['iteration'],row['max_speed_m_s'])==row['snapshot_reasons']
        diag.file.write((a.recovered_diagnostic_directory/'spike-history.jsonl').read_text()); diag.file.flush(); diag.last_iteration=START; diag.persist()
        faces=[FluxFaceZone(**value) for value in old['flux_monitor']['face_zones']]
        m=Phase07bFluxMonitor(s,face_zones=faces,start_iteration=START,local_jsonl=out/'collector-flux.jsonl',remote_directory=ROOT+'/reports',prefix_source=parent/'collector-flux.jsonl',after_capture=diag.capture)
        callback_id=m.register()
        # Persist the exact pause owned by this one controller for interruption
        # recovery. Discovery of a monitor alone is not ownership evidence.
        pause_ids=dict(s.events._sync_event_ids)
        assert callback_id in pause_ids and len(pause_ids)==1, pause_ids
        r['pause_registration_ids']=pause_ids
        persist()
        m.assert_complete(START); diag.assert_complete(START)
        r.update(status='RUNNING',flux_monitor=m.manifest(),spike_diagnostics=diag.manifest(),
                 instrumentation_smoke=f'Recovered N1-{START} scalar, exact-face flux, all eight residuals and full native diagnostics verified before continuation')
        if START==505:
            r['recovery_smoke']='N501-505 scalar/flux/all eight residuals/diagnostics and preserved paired checkpoint PASS; native report rollover reconciled without repeating any iteration'
        elif START==687:
            r['recovery_smoke']='Native N1-687 scalar/all eight residuals, exact-face flux, speed and paired endpoint recovered after retired recorder RPC stall; no replay or scientific change'
        elif START==1631:
            r['recovery_smoke']='Native N1-1631 scalar/all eight residuals, recovered idle endpoint face flux/speed and paired checkpoint verified after host sleep interrupted transport; no replay or scientific change'
        elif START==2185:
            r['recovery_smoke']='Native N1-2185 scalar/all eight residuals, recovered idle endpoint face flux/speed and paired checkpoint verified after network loss; no replay or scientific change'
        elif START==3227:
            r['recovery_smoke']='Native N1-3227 scalar/all eight residuals, recovered idle endpoint face flux/speed and unique paired checkpoint verified after sleep-associated transport loss; no replay or scientific change'
        (out/f'smoke-n{START:05d}.json').write_text(json.dumps(r['recovery_verification'],indent=2)+'\n')
        (out/'recovery-verification.json').write_text(json.dumps(r['recovery_verification'],indent=2)+'\n'); persist()
        current=START
        for target in TARGETS:
            assert START < target <= HORIZON
            step(f'iterate_{current}_to_{target}',lambda current=current,target=target:s.settings.solution.run_calculation.iterate(iter_count=target-current),max(600,(target-current)*20))
            r['actual_iteration']=n(); assert r['actual_iteration']==target and not s.settings.solution.run_calculation.iterating()
            m.assert_complete(target); diag.assert_complete(target)
            if target==START+5 and not any(snap['iteration']==target for snap in diag.snapshots):
                step(f'verify_n{target}_normalized_inventory_snapshot',lambda:diag.snapshot(target,diag.value('P7bMaximumSpeed'),['recovery_semantics_validation']),180)
                diag.assert_complete(target)
                if r['experiment_id']=='E7':
                    r['verified_recovery_snapshot_iterations']=sorted(set(r.get('verified_recovery_snapshot_iterations',[]))|{target})
            r.update(flux_monitor=m.manifest(),spike_diagnostics=diag.manifest())
            last=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1]); assert json.loads(read_text(s,last['remote_path']))==last
            r['remote_flux_readbacks'].append({'iteration':target,'path':last['remote_path'],'matches_local':True})
            r['scalar_coverage']=read_scalar_snapshot(s,r,out,target)
            r['residual_coverage']=residual_audit(out/'solve.trn',expected_residual_equations(r),target)
            r['latest_metrics']=step(f'metrics_{target}',lambda:s.settings.solution.report_definitions.compute(report_defs=s.settings.solution.monitor.report_files['p7b-screen-history'].report_defs()))
            tag='final' if target==HORIZON else f'n{target:05d}'
            path=ROOT+'/case-data/'+a.run_id+'-'+tag+'.cas.h5'
            assert not any(remote_file_exists(s,path.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            step('save_'+tag,lambda:s.settings.file.write_case_data(file_name=path),180)
            assert all(remote_file_exists(s,path.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            r['pairs'][tag]=path; current=target; r['segment_iterations']=current-START
            if target==START+5: r['recovery_smoke']=f'N{START+1}-{target} scalar/flux/all eight residuals/diagnostic continuation and paired checkpoint PASS'
            persist()
        m.unregister(); r['flux_monitor']=m.manifest(); m=None
        r['final_sections']=step('extract_final_sections',lambda:export_sections(s,r['sections'],out/'final-sections'),180)
        r['final_axial_sections']=step('extract_final_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'final-axial-sections'),180)
        step('stop_native_transcript',s.settings.file.stop_transcript)
        assert n()==HORIZON and not s.settings.solution.run_calculation.iterating()
        r.update(status='HORIZON_COMPLETE_ANALYSIS_PENDING',completed_iterations=HORIZON); persist()
    except Exception as exc:
        signal.alarm(0); r.update(status='BLOCKED_EXECUTION',error=str(exc)); (out/'error.txt').write_text(traceback.format_exc()); persist(); raise
    finally:
        signal.alarm(0)
        if m is not None:
            try: m.unregister()
            except Exception as exc: r['callback_cleanup_error']=str(exc)
            r['flux_monitor']=m.manifest()
        if s is not None:
            try:
                if transcript_cb is not None: s.transcript.unregister_callback(transcript_cb)
                s.transcript.stop()
            except Exception: pass
        if diag is not None: diag.close(); r['spike_diagnostics']=diag.manifest()
        persist(); print('EVIDENCE',out,flush=True)


if __name__=='__main__': main()
