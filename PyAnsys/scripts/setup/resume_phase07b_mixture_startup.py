"""Resume independently preserved E8 live N50 without reload/init/offset/replay.

Receipt schema is explicit in validate_inputs. All local guards run before any
Fluent connection. A failure never retries a solve, edits a counter, reloads a
case, or terminates Fluent. Existing parent/raw recovery files remain immutable.
"""
from run_phase07b_mixture_startup import *
import shutil
from pyansys_fluent.phase07b_spike_monitor import SpikeSchedule

START=50


def load_arrays(path):
    with np.load(path) as data:return {k:data[k] for k in data.files}


def complete_jsonl(path,end=START):
    content=path.read_text();assert content.endswith('\n')
    rows=[json.loads(v) for v in content.splitlines()]
    assert [v['iteration'] for v in rows]==list(range(1,end+1)), path
    return rows


def scalar_prefix_parity(prefix, current, end):
    """Current report remains native continuous 1..N, including immutable 1..50."""
    first,fa=parse_history(prefix);data,audit=parse_history(current)
    assert np.array_equal(first['iteration'],np.arange(1,START+1))
    assert np.array_equal(data['iteration'],np.arange(1,end+1))
    assert fa['native_header']==audit['native_header']
    assert not audit['conflicting_indices'] and not audit['nonfinite_columns'] and not audit['rejected_lines']
    assert all(np.array_equal(first[k],data[k][:START]) for k in first), 'Original scalar prefix changed'
    return data,audit


def joined_conditioning_residuals(prefix, segment, output, end):
    """Keep both raw files; accept only exact native repeated N50 boundary."""
    parse_stage_residuals(prefix,'conditioning',0,START)
    first=None
    for line in segment.read_text().splitlines():
        words=line.split()
        if words and words[0].isdigit() and len(words)>=8 and any(':' in w for w in words[7:]):
            first=int(words[0]);break
    assert first in (START,START+1), ('Unexpected resumed residual boundary',first)
    _,segment_audit=parse_stage_residuals(segment,'conditioning',first-1,end)
    assert not output.exists()
    output.write_text(prefix.read_text().rstrip('\n')+'\n'+segment.read_text())
    data,audit=parse_stage_residuals(output,'conditioning',0,end)
    assert set(audit['duplicate_indices'])-set(segment_audit['duplicate_indices']) <= {START}, 'Unexpected overlap with original prefix'
    return data,audit


def validate_inputs(parent_path,receipt_path):
    parent=json.loads(parent_path.read_text());receipt=json.loads(receipt_path.read_text())
    assert parent['experiment_id']=='E8' and parent['tau_s']==.02 and parent['percent']==40
    assert parent['requested_iterations']==5000 and parent['conditioning_cap']==1000
    assert not parent.get('conditioning_gates') and not parent.get('switch_iteration')
    assert receipt['status']=='N50_PRESERVED_NATIVE_RECORDING_AND_SETTINGS_PASS'
    assert receipt['parent_run_id']==parent['run_id'] and receipt['iteration']==START
    assert receipt['iterating'] is False and receipt['iterations_issued']==0 and receipt['pair_exists'] is True
    assert receipt['data']==receipt['case'].replace('.cas.h5','.dat.h5')
    assert receipt['reloads_issued']==0 and receipt['fluent_exit_called'] is False
    assert receipt['scientific_changes'] is False and receipt['geometry_exact'] and receipt['settings_exact']
    assert all(step['status']=='RETURNED' for step in receipt['steps'])
    for k,v in receipt['files'].items():assert fingerprint(Path(v['path']))['sha256']==v['sha256'], ('Changed recovery file',k)
    keys={'geometry':'diagnostics/geometry.npz','fields':'diagnostics/fields-n00050.npz',
          'field_metadata':'diagnostics/fields-n00050.json','frozen_phase':'frozen-phase-n00050.npz',
          'history':'history-00050.out','conditioning_transcript':'conditioning-native-to-00050.trn',
          'speed':'spike-history.jsonl','diagnostic_manifest':'diagnostics/manifest.json'}
    files={k:Path(receipt['files'][v]['path']) for k,v in keys.items()}
    files['flux']=Path(receipt['flux']['file']);files['baseline_setup']=parent_path.parent/'prepared-setup.json'
    assert receipt['scalar']['file']==str(files['history']) and receipt['residual']['file']==str(files['conditioning_transcript'])
    assert receipt['flux']['native_readback_exact'] and receipt['flux']['independent_current_face_reduction_exact']
    assert receipt['speed']['scalar_fullcell_native_parity'] and receipt['speed']['recovered_index']==START
    controls=copy.deepcopy(parent['selected_controls']);controls['equations'].update(mp=False,drift=False)
    exact_parity(controls,receipt['selected_controls'],'preserved frozen controls')
    for k in ['selected_methods','source_slots','report_definitions','residual_options']:
        exact_parity(parent[k],receipt[k],k)
    for k,value in receipt['residual_equations'].items():exact_parity(parent['residual_equations'][k],value,'residual policy '+k)
    assert ACTIVE_FLOW<=set(receipt['residual_equations'])<=ACTIVE_FULL
    assert receipt['report_policy']['active'] and receipt['report_policy']['frequency']==1
    resolved=resolved_native_report_path(receipt['report_policy'],parent['native_report_segment_base'])
    assert resolved==parent['report']
    # Derived routing only; no new physical/recovery claim is inserted in raw receipt.
    receipt=copy.deepcopy(receipt);receipt['report']=resolved
    receipt['native_conditioning_transcript']=parent['residual_stages']['conditioning']['remote']
    history,ha=scalar_prefix_parity(files['history'],files['history'],START)
    rd,ra=parse_stage_residuals(files['conditioning_transcript'],'conditioning',0,START)
    flux=complete_jsonl(files['flux']);speed=complete_jsonl(files['speed'])
    receipt['face_zones']=[{k:z[k] for k in ['name','outward_sign','expected_owned_count']} for z in flux[-1]['zones']]
    geometry=load_arrays(files['geometry']);field=load_arrays(files['fields']);phase=load_arrays(files['frozen_phase'])
    original=load_arrays(parent_path.parent/'spike-diagnostics/geometry.npz')
    assert set(geometry)==set(original) and all(np.array_equal(geometry[k],original[k]) for k in geometry)
    initial=load_arrays(parent_path.parent/'frozen-phase-n00000.npz')
    verify_frozen_phase_arrays(phase,initial,parent['fluid_zones'])
    for key,array in phase.items():assert array.size==len(geometry[key.split('_',1)[0]+'_mixture_SV_VOLUME']) and np.isfinite(array).all()
    metadata=json.loads(files['field_metadata'].read_text());assert metadata['iteration']==START and metadata['same_iteration_before_after']
    assert metadata['sha256']==fingerprint(files['fields'])['sha256']
    water=0.
    for i in range(len(parent['fluid_zones'])):
        secondary=field[f'z{i}_phase-2_SV_VOF'];total=secondary+field[f'z{i}_phase-1_SV_VOF']
        assert (total>0).all();water+=float(np.dot(secondary/total,geometry[f'z{i}_mixture_SV_VOLUME']))
    assert np.isclose(water,metadata['native']['water'],rtol=1e-9,atol=1e-12)
    assert metadata['native']['speed']==speed[-1]['max_speed_m_s']==history['p7bmaximumspeed'][-1]
    dm=json.loads(files['diagnostic_manifest'].read_text());assert dm['last_iteration']==START and dm['error'] is None
    assert [snap['iteration'] for snap in dm['snapshots']]==[50]
    parent_dm=json.loads((parent_path.parent/'spike-diagnostics/manifest.json').read_text())
    assert [snap['iteration'] for snap in parent_dm['snapshots']]==[0]
    dm['snapshots']=copy.deepcopy(parent_dm['snapshots'])+dm['snapshots']
    schedule=SpikeSchedule()
    for row in speed:assert schedule.reasons(row['iteration'],row['max_speed_m_s'])==row['snapshot_reasons']
    return parent,receipt,files,dm,history,flux,speed


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-manifest',type=Path,required=True);ap.add_argument('--preservation-receipt',type=Path,required=True)
    ap.add_argument('--run-id',required=True);ap.add_argument('--validate-only',action='store_true')
    a=ap.parse_args();old,receipt,files,dm,history50,flux,speed=validate_inputs(a.parent_manifest,a.preservation_receipt)
    assert re.fullmatch(r'p7b-[a-z0-9-]+-[0-9]{8}T[0-9]{6}Z',a.run_id)
    if a.validate_only:
        print(json.dumps({'status':'E8_N50_LOCAL_RECOVERY_INPUTS_PASS','connections':0,'start':50,'next_target':200,'cap':5000}));return
    lock=(BASE/'output/phase07b-server1-controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    out=BASE/'output'/a.run_id;out.mkdir();lock.seek(0);lock.truncate();lock.write(json.dumps({'pid':os.getpid(),'run_id':a.run_id}));lock.flush()
    parent=a.parent_manifest.parent;r=copy.deepcopy(old)
    for key in ['error','callback_cleanup_error','pause_registration_ids','issued_block']:r.pop(key,None)
    r.update(run_id=a.run_id,controller_pid=os.getpid(),status='VERIFYING_LIVE_N50',steps=[],actual_iteration=START,iterations_issued=0,retained_iterations=START,
             parent_manifest=str(a.parent_manifest.resolve()),start_iteration=START,segment_iterations=0,prefix_end=START,
             recovery_receipt=fingerprint(a.preservation_receipt),recovery_inputs={k:fingerprint(p) for k,p in files.items()},residual_stages={},
             resume_policy='Unchanged independently preserved live N50; no reload, initialization, offset or replay')
    r['pairs']['n00050']=receipt['case'];r['implementation'].append(fingerprint(Path(__file__)))
    def persist():
        p=out/'manifest.tmp';p.write_text(json.dumps(r,indent=2,default=str)+'\n');p.replace(out/'manifest.json')
    def timeout(*_):raise TimeoutError('Uncertain RPC: reconcile live state before retry')
    signal.signal(signal.SIGALRM,timeout)
    def step(name,fn,seconds=180):
        e={'name':name,'state':'STARTED','started_utc':datetime.now(timezone.utc).isoformat()};r['steps'].append(e);persist();print(name,flush=True);signal.alarm(seconds)
        try:
            v=fn();e.update(state='PASS',value='attached' if name=='connect' else v);return v
        except Exception as exc:e.update(state='FAIL',error=str(exc));raise
        finally:signal.alarm(0);e['ended_utc']=datetime.now(timezone.utc).isoformat();persist()
    s=m=diag=None;transcript_cb=None
    baseline_setup=json.loads(files['baseline_setup'].read_text());initial=load_arrays(parent/'frozen-phase-n00000.npz')
    try:
        s=step('connect',lambda:connect(1,start_transcript=False,tcp_timeout_seconds=5),90)
        def n():
            value=s.settings.setup.named_expressions['P7bGlobalIteration'].get_value();assert np.isfinite(value) and value==int(value);return int(value)
        def verify_settings(frozen=True):
            controls=copy.deepcopy(old['selected_controls'])
            if frozen:controls['equations'].update(mp=False,drift=False)
            exact_parity(controls,s.settings.solution.controls.get_state(),'unchanged controls')
            for k,node in [('selected_methods',s.settings.solution.methods),('residual_options',s.settings.solution.monitor.residual.options),('report_definitions',s.settings.solution.report_definitions)]:
                exact_parity(old[k],node.get_state(),k)
            monitors=s.settings.solution.monitor.residual.equations.get_state();required=ACTIVE_FLOW if frozen else ACTIVE_FULL
            assert required<=set(monitors)<=ACTIVE_FULL
            for k,value in monitors.items():exact_parity(old['residual_equations'][k],value,'residual policy '+k)
            for name,value in old['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==value,name
            for zone,phases in old['source_slots'].items():
                for phase,value in phases.items():exact_parity(value,s.settings.setup.cell_zone_conditions.fluid[zone].phase[phase].sources.get_state(),zone+'.'+phase)
            exact_parity(baseline_setup,s.settings.setup.get_state(),'preserved full setup')
            assert s.settings.solution.run_calculation.profile_update_interval()==1
            state=s.settings.solution.monitor.report_files['p7b-screen-history'].get_state()
            assert resolved_native_report_path(state,old['native_report_segment_base'])==receipt['report']
            exact_parity(receipt['report_policy'],state,'unchanged report policy')
            return {'frozen':frozen,'exposed_monitors':sorted(monitors),'iteration':n()}
        geometry=load_arrays(files['geometry'])
        def live_arrays(expected):
            actual={}
            for domain,variable in sorted({tuple(k.split('_',2)[1:]) for k in expected}):
                data=s.fields.solution_variable_data.get_data(variable_name=variable,zone_names=r['fluid_zones'],domain_name=domain)
                for i,z in enumerate(r['fluid_zones']):
                    key=f'z{i}_{domain}_{variable}';actual[key]=np.asarray(data[z]);assert np.isfinite(actual[key]).all()
                    expected_count=len(geometry[f'z{i}_mixture_SV_VOLUME'])*(3 if variable=='SV_CENTROID' else 1)
                    assert actual[key].size==expected_count>0,key
            return actual
        def parity_file(path):
            expected=load_arrays(path);expected={k:v for k,v in expected.items() if 'MASS_IMBALANCE' not in k}
            actual=live_arrays(expected);assert set(actual)==set(expected)
            for key in expected:assert np.array_equal(actual[key],expected[key]), ('Live N50 differs',key)
        def verify_live():
            assert n()==START and not s.settings.solution.run_calculation.iterating()
            verify_settings();assert all(remote_file_exists(s,receipt[k]) for k in ['case','data'])
            for k in ['geometry','fields','frozen_phase']:parity_file(files[k])
            p=out/'history-00050.out';p.write_text(read_text(s,receipt['report']));scalar_prefix_parity(files['history'],p,START)
            native=read_text(s,receipt['native_conditioning_transcript']);p=out/'conditioning-native-to-00050.trn';p.write_text(native)
            actual,_=parse_stage_residuals(p,'conditioning',0,START);expected,_=parse_stage_residuals(files['conditioning_transcript'],'conditioning',0,START)
            assert all(np.array_equal(actual[k],expected[k]) for k in actual)
            assert json.loads(read_text(s,flux[-1]['remote_path']))==flux[-1]
            assert n()==START and not s.settings.solution.run_calculation.iterating()
            return {'iteration':START,'exact_live_fields_geometry_slip':True,'native_prefixes_match':True,'iterations_issued':0,'reloads':0}
        r['recovery_verification']=step('verify_exact_live_n50_and_native_prefixes',verify_live,600)
        for folder in ['initial-sections','initial-axial-sections']:
            shutil.copytree(parent/folder,out/folder)
        for name in ['prepared-setup.json','frozen-phase-n00000.npz','loaded-phase-n00000.npz']:
            shutil.copy2(parent/name,out/name)
        shutil.copy2(files['frozen_phase'],out/'frozen-phase-n00050.npz')
        shutil.copy2(files['baseline_setup'],out/'preserved-setup.json')
        diag=Phase07bSpikeMonitor(s,r['fluid_zones'],out/'spike-diagnostics',solve_n_phase=True)
        diag.geometry=geometry;np.savez_compressed(diag.directory/'geometry.npz',**geometry)
        for iteration,origin in [(0,parent/'spike-diagnostics'),(50,files['fields'].parent)]:
            src=(origin/f'fields-n{iteration:05d}.npz') if iteration==0 else files['fields']
            meta=(origin/f'fields-n{iteration:05d}.json') if iteration==0 else files['field_metadata']
            shutil.copy2(src,diag.directory/f'fields-n{iteration:05d}.npz');shutil.copy2(meta,diag.directory/f'fields-n{iteration:05d}.json')
        for snap in dm['snapshots']:
            item=copy.deepcopy(snap);item['path']=str(diag.directory/f"fields-n{snap['iteration']:05d}.npz");diag.snapshots.append(item)
        for row in speed:assert diag.schedule.reasons(row['iteration'],row['max_speed_m_s'])==row['snapshot_reasons']
        diag.file.write(files['speed'].read_text());diag.file.flush();diag.last_iteration=START;diag.persist()
        r['frozen_field_proofs']={'50':verify_frozen_phase_arrays(load_arrays(files['frozen_phase']),initial,r['fluid_zones'])}
        r['report']=receipt['report'];r['spike_diagnostics']=diag.manifest()
        smoke={'status':'CONDITIONING_N50_RECOVERED_RECORDING_PASS','iteration':50,'active_residuals':sorted(ACTIVE_FLOW),'preservation':fingerprint(a.preservation_receipt),'verification':r['recovery_verification']}
        (out/'smoke-n00050.json').write_text(json.dumps(smoke,indent=2)+'\n')
        faces=[FluxFaceZone(**v) for v in receipt['face_zones']]
        m=Phase07bFluxMonitor(s,face_zones=faces,start_iteration=START,local_jsonl=out/'collector-flux.jsonl',remote_directory=ROOT+'/reports',prefix_source=files['flux'],after_capture=diag.capture)
        callback=m.register();r['pause_registration_ids']=dict(s.events._sync_event_ids)
        assert callback in r['pause_registration_ids'] and len(r['pause_registration_ids'])==1
        current=START;switch=None
        if s.settings.file.stop_transcript.is_active():step('close_retired_native_transcript',s.settings.file.stop_transcript)
        def begin_stage(stage):
            nonlocal transcript_cb
            local=out/(stage+'-solve.trn');remote=ROOT+'/reports/'+a.run_id+'-'+stage+'.trn'
            assert not remote_file_exists(s,remote)
            if stage=='conditioning':
                local.write_text(files['conditioning_transcript'].read_text().rstrip('\n')+'\n')
                s.transcript.start(file_name=str(out/'conditioning-resume-segment.trn'),write_to_stdout=False)
                def append(text):
                    with local.open('a') as stream:stream.write(text)
                transcript_cb=s.transcript.register_callback(append,keep_new_lines=True)
            else:s.transcript.start(file_name=str(local),write_to_stdout=False)
            s.settings.file.start_transcript(file_name=remote)
            r['residual_stages'][stage]={'local':str(local),'remote':remote,'start_exclusive':0 if stage=='conditioning' else current,
                'segment_start_exclusive':current,'immutable_prefix':fingerprint(files['conditioning_transcript']) if stage=='conditioning' else None};persist()
        def end_stage():
            nonlocal transcript_cb
            s.settings.file.stop_transcript()
            if transcript_cb is not None:s.transcript.unregister_callback(transcript_cb);transcript_cb=None
            s.transcript.stop()
        def save(tag):
            path=ROOT+'/case-data/'+a.run_id+'-'+tag+'.cas.h5'
            assert not any(remote_file_exists(s,path.replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
            step('save_'+tag,lambda:s.settings.file.write_case_data(file_name=path),300)
            assert all(remote_file_exists(s,path.replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
            r['pairs'][tag]=path;persist()
        def phase_capture(tag):
            values=live_arrays(initial);path=out/(tag+'.npz');assert not path.exists();np.savez_compressed(path,**values);return values
        begin_stage('conditioning');r['status']='CONDITIONING_RUNNING';r['flux_monitor']=m.manifest();persist()
        def advance(target,stage):
            nonlocal current
            verify_settings(stage=='conditioning');assert n()==current
            r['issued_block']={'start':current,'end':target,'stage':stage};r['iterations_issued']+=target-current;persist()
            step(f'iterate_{stage}_{current}_to_{target}',lambda:s.settings.solution.run_calculation.iterate(iter_count=target-current),max(600,(target-current)*20))
            assert n()==target and not s.settings.solution.run_calculation.iterating()
            current=target;r.update(actual_iteration=current,segment_iterations=current-START,retained_iterations=current)
            m.assert_complete(current);diag.assert_complete(current);verify_settings(stage=='conditioning')
            r.update(flux_monitor=m.manifest(),spike_diagnostics=diag.manifest())
            hp=out/f'history-{current:05d}.out';assert not hp.exists();hp.write_text(read_text(s,receipt['report']))
            history,ha=scalar_prefix_parity(files['history'],hp,current);derived,_=derive(history)
            lag=float(np.max(abs(derived['native_applied_removal'][1:]-derived['current_expression_removal'][:-1])));assert lag<=1e-9
            r['scalar_coverage']={'audit':ha,'lag_pairs':current-1,'lag_max_abs_error_kg_s':lag}
            raw=out/f'{stage}-native-resume-segment-to-{current:05d}.trn';raw.write_text(read_text(s,r['residual_stages'][stage]['remote']))
            assert not any(v in raw.read_text() for v in FATAL)
            tr=out/f'{stage}-native-to-{current:05d}.trn'
            if stage=='conditioning':data,ra=joined_conditioning_residuals(files['conditioning_transcript'],raw,tr,current)
            else:
                shutil.copy2(raw,tr);data,ra=parse_stage_residuals(tr,'full',switch,current)
            r['residual_stages'][stage].update(latest_native_snapshot=str(tr),end_inclusive=current,audit=ra)
            row=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1]);assert json.loads(read_text(s,row['remote_path']))==row
            r['remote_flux_readbacks'].append({'iteration':current,'path':row['remote_path'],'matches_local':True})
            if stage=='conditioning':r['frozen_field_proofs'][str(current)]=verify_frozen_phase_arrays(phase_capture(f'frozen-phase-n{current:05d}'),initial,r['fluid_zones'])
            if current%500==0:save('final' if current==5000 else f'n{current:05d}')
            persist();return history,data
        for target in range(200,1001,100):
            history,data=advance(target,'conditioning');gate=conditioning_gate(history,data,target)
            r['conditioning_gates'].append(gate);persist()
            if gate['passed']:switch=target;break
        end_stage();r['conditioning_end_iteration']=current
        if switch is not None:
            if not any(v['iteration']==switch for v in diag.snapshots):diag.snapshot(switch,diag.value('P7bMaximumSpeed'),['conditioning_switch'])
            save(f'conditioning-pass-n{switch:05d}');before=phase_capture(f'switch-before-n{switch:05d}')
            s.settings.solution.controls.equations.set_state(old['selected_controls']['equations']);verify_settings(False)
            after=phase_capture(f'switch-after-n{switch:05d}');assert all(np.array_equal(before[k],after[k]) for k in before)
            assert n()==switch;save(f'full-equations-restored-n{switch:05d}')
            r.update(status='FULL_EQUATIONS_RUNNING',switch_iteration=switch);begin_stage('full')
            for target in range((switch//500+1)*500,5001,500):advance(target,'full')
            end_stage();assert current==5000 and current-switch>=4000
            r.update(full_equation_iterations=current-switch,status='HORIZON_COMPLETE_ANALYSIS_PENDING')
        else:
            assert current==1000;save('conditioning-gate-not-met-final')
            r.update(status='CONDITIONING_GATE_NOT_MET',full_equation_iterations=0,
                     numerical_disposition='Initial flow did not meet the prospective gate within 1000; full-equation startup endpoint untested')
        m.unregister();r['flux_monitor']=m.manifest();m=None
        r['final_sections']=step('final_sections',lambda:export_sections(s,r['sections'],out/'final-sections'),300)
        r['final_axial_sections']=step('final_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'final-axial-sections'),300)
        r.update(completed_iterations=current,terminal_artifacts_verified=True);persist()
    except Exception as exc:
        signal.alarm(0);r.update(status='BLOCKED_EXECUTION_RECONCILE_REQUIRED',error=str(exc));(out/'error.txt').write_text(traceback.format_exc());persist();raise
    finally:
        signal.alarm(0)
        if m is not None:
            try:m.unregister()
            except Exception as exc:r['callback_cleanup_error']=str(exc)
            r['flux_monitor']=m.manifest()
        if diag is not None:diag.close();r['spike_diagnostics']=diag.manifest()
        if s is not None:
            try:
                if transcript_cb is not None:s.transcript.unregister_callback(transcript_cb)
                s.transcript.stop()
            except Exception:pass
        persist();print('EVIDENCE',out,flush=True)


if __name__=='__main__':main()
