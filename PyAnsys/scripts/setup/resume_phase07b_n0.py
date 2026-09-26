"""Continue the verified E7 prepared live N0 after diagnostic-schema failure.

No reload, reinitialization, counter offset, or scientific change. Original
failed evidence is immutable; all continuation evidence has a new run identity.
"""
from resume_phase07b_investigation import *


def validate_parent(path):
    old=json.loads(path.read_text())
    assert old['experiment_id']=='E7' and old['case_id']=='S40-T100-COUPLED-CFL20-NPHASE'
    assert old['status']=='BLOCKED_EXECUTION' and old.get('actual_iteration',0)==0
    assert old['tau_s']==.1 and old['requested_iterations']==5000
    assert not any(event['name'].startswith('iterate_') for event in old['steps'])
    assert old['steps'][-1]['name']=='prove_coupled_initial_fields' and old['steps'][-1]['state']=='FAIL'
    assert old['build_verification']=='SOURCE_MASK_SETUP_REPORTS_SAVE_REOPEN_PASS'
    assert old['source_treatment']['status']=='EXACT_TAU_ONLY_DELTA_PASS'
    assert old['numerical_treatment']['nphase_before_hybrid'] is True
    assert old['pre_reopen_initial_parity']['status']=='PRE_REOPEN_N0_PHYSICAL_EXACT_GEOMETRY_ROUNDOFF_PASS'
    assert old['pre_reopen_prepared_parity']['status']=='PRE_REOPEN_N0_PHYSICAL_GEOMETRY_EXACT_PARITY_PASS'
    assert len(expected_residual_equations(old))==8
    assert old['spike_diagnostics']['last_iteration']==0 and old['spike_diagnostics']['error'] is None
    assert (path.parent/'spike-diagnostics/spike-history.jsonl').stat().st_size==0
    setup=(path.parent/'setup.trn').read_text()
    assert not any(marker in setup for marker in FATAL)
    counts=re.findall(r'^\s*0\s+(620431)\s+(2852567)\s+(\d+)\s+(16)\s*$',setup,re.M)
    assert len(counts)>=2 and counts[0]==counts[1]
    return old


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-manifest',type=Path,required=True)
    ap.add_argument('--run-id',required=True)
    ap.add_argument('--validate-only',action='store_true')
    a=ap.parse_args(); old=validate_parent(a.parent_manifest); parent=a.parent_manifest.parent
    assert re.fullmatch(r'p7b-s40-t100-coupled-cfl20-nphase-resume-[0-9]{8}T[0-9]{6}Z',a.run_id)
    if a.validate_only:
        print('E7 PREPARED N0 LOCAL INPUTS PASS; no Fluent connection'); return
    lock=(BASE/'output/phase07b-server1-controller.lock').open('a+')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    out=BASE/'output'/a.run_id; out.mkdir()
    lock.seek(0);lock.truncate();lock.write(json.dumps({'pid':os.getpid(),'run_id':a.run_id}));lock.flush()
    r=copy.deepcopy(old)
    r.update(run_id=a.run_id,controller_pid=os.getpid(),steps=[],status='VERIFYING_PREPARED_N0',error=None,
             start_iteration=0,actual_iteration=0,segment_iterations=0,parent_manifest=str(a.parent_manifest.resolve()),
             resume_mode='unchanged prepared live N0; no reload/initialization/counter offset',
             recovery_inputs=[fingerprint(a.parent_manifest)],remote_flux_readbacks=[])
    r['implementation_sha256'][str(Path(__file__).resolve())]=fingerprint(Path(__file__))['sha256']
    r['report']=ROOT+'/reports/'+a.run_id+'.out';r['remote_transcript']=ROOT+'/logs/'+a.run_id+'.trn'
    def persist():
        temp=out/'manifest.tmp';temp.write_text(json.dumps(r,indent=2,default=str)+'\n');temp.replace(out/'manifest.json')
    def timeout(*_):raise TimeoutError('RPC deadline; reconcile before retry')
    signal.signal(signal.SIGALRM,timeout)
    def step(name,fn,seconds=90):
        event={'name':name,'state':'STARTED','started_utc':datetime.now(timezone.utc).isoformat()};r['steps'].append(event);persist();print(name,flush=True);signal.alarm(seconds)
        try:
            value=fn();event.update(state='PASS',value='attached, cleanup_on_exit=False' if name=='connect' else value);return value
        except Exception as exc:event.update(state='FAIL',error=str(exc));raise
        finally:signal.alarm(0);event['ended_utc']=datetime.now(timezone.utc).isoformat();persist()
    s=m=diag=None
    try:
        s=step('connect',lambda:connect(1,start_transcript=False,tcp_timeout_seconds=5),90)
        s.transcript.start(file_name=str(out/'recovery.trn'),write_to_stdout=False)
        def n():
            value=s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()
            assert np.isfinite(value) and value==int(value);return int(value)
        def verify_live():
            assert n()==0 and not s.settings.solution.run_calculation.iterating()
            assert all(remote_file_exists(s,old['pairs']['prepared'].replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            for name,definition in old['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==definition,name
            for zone,phases in old['source_slots'].items():
                for phase,slots in phases.items():exact_parity(slots,s.settings.setup.cell_zone_conditions.fluid[zone].phase[phase].sources.get_state(),zone+'.'+phase)
            for key,live in [('selected_methods',s.settings.solution.methods),('selected_controls',s.settings.solution.controls),('residual_options',s.settings.solution.monitor.residual.options),('residual_equations',s.settings.solution.monitor.residual.equations),('report_definitions',s.settings.solution.report_definitions)]:exact_parity(old[key],live.get_state(),key)
            assert s.settings.solution.run_calculation.profile_update_interval()==1
            # Fluent reopens this stored absolute report path as reports\\<name>.
            # Accept only that exact relative representation, then select a new
            # absolute output below; no pre-existing history is reused at N0.
            from pathlib import PureWindowsPath
            report_file=s.settings.solution.monitor.report_files['p7b-screen-history'].get_state()
            actual_path=PureWindowsPath(report_file['file_name'])
            assert actual_path in {PureWindowsPath(old['report']),PureWindowsPath('reports')/PureWindowsPath(old['report']).name}, report_file
            assert report_file['active'] and report_file['frequency_of']=='iteration' and report_file['frequency']==1
            info=s.fields.solution_variable_info.get_zones_info()
            assert info['p7b-collector'].count==COUNTS[40] and sum(info[z].count for z in old['fluid_zones'])==620431
            arrays={}
            for file in ['geometry.npz','fields-n00000.npz']:
                with np.load(parent/'spike-diagnostics'/file) as data:arrays.update({key:data[key] for key in data.files if 'MASS_IMBALANCE' not in key})
            for domain,variable in sorted({tuple(key.split('_',2)[1:]) for key in arrays}):
                values=s.fields.solution_variable_data.get_data(variable_name=variable,zone_names=old['fluid_zones'],domain_name=domain)
                for i,zone in enumerate(old['fluid_zones']):
                    key=f'z{i}_{domain}_{variable}';assert np.array_equal(np.asarray(values[zone]),arrays[key]),key
            assert s.settings.setup.named_expressions['P7bWaterVolume'].get_value()==0
            assert n()==0 and not s.settings.solution.run_calculation.iterating()
            return {'live_iteration':0,'iterating':False,'exact_endpoint_fields':True,'settings_match':True,'iterations_issued':0,'prepared_pair_exists':True,'previous_report_file':report_file}
        r['recovery_verification']=step('verify_unchanged_live_n0',verify_live,240)
        for folder in ['initial-sections','initial-axial-sections','pre-reopen-initial','pre-reopen-prepared']:
            shutil.copytree(parent/folder,out/folder)
        shutil.copy2(parent/'setup.trn',out/'setup.trn')
        for path in parent.glob('interface-*.npz'):shutil.copy2(path,out/path.name)
        diag=Phase07bSpikeMonitor(s,old['fluid_zones'],out/'spike-diagnostics',solve_n_phase=True)
        step('recapture_live_n0_diagnostics',diag.prepare,300)
        r['initial_field_parity']=step('prove_original_n0_fields',lambda:initial_field_parity(out,allow_nphase_primary_n0=True))
        ref=BASE/'output/p7b-s40-t020-diag-20260922T071533Z/spike-diagnostics/geometry.npz'
        with np.load(out/'spike-diagnostics/geometry.npz') as actual,np.load(ref) as expected:
            assert set(actual.files)==set(expected.files) and all(np.array_equal(actual[key],expected[key]) for key in actual.files)
        r['initial_geometry_parity']={'status':'GEOMETRY_FIELDS_EXACTLY_EQUAL','reference':str(ref)}
        (out/'initial-geometry-parity.json').write_text(json.dumps(r['initial_geometry_parity'],indent=2)+'\n')
        rf=s.settings.solution.monitor.report_files['p7b-screen-history']
        assert not remote_file_exists(s,r['report']);rf.file_name=r['report'];reports=rf.report_defs()
        from pathlib import PureWindowsPath
        assert PureWindowsPath(rf.file_name())==PureWindowsPath(r['report'])
        def save(tag):
            path=ROOT+'/case-data/'+a.run_id+'-'+tag+'.cas.h5'
            assert not any(remote_file_exists(s,path.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            step('save_'+tag,lambda:s.settings.file.write_case_data(file_name=path),180)
            assert all(remote_file_exists(s,path.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            r['pairs'][tag]=path;persist();return path
        save('recovery-n00000')
        assert n()==0
        r['recovery_verification']['unique_n0_pair']=r['pairs']['recovery-n00000']
        (out/'recovery-verification.json').write_text(json.dumps(r['recovery_verification'],indent=2)+'\n')
        if s.settings.file.stop_transcript.is_active():step('close_inherited_transcript',s.settings.file.stop_transcript)
        s.transcript.stop();s.transcript.start(file_name=str(out/'solve.trn'),write_to_stdout=False)
        assert not remote_file_exists(s,r['remote_transcript'])
        step('start_native_transcript',lambda:s.settings.file.start_transcript(file_name=r['remote_transcript']))
        faces=[FluxFaceZone(name,value['outward_sign'],value['count']) for name,value in old['interface_proof'].items() if value.get('all_faces_cross_centroid_mask')]
        m=Phase07bFluxMonitor(s,face_zones=faces,start_iteration=0,local_jsonl=out/'collector-flux.jsonl',remote_directory=ROOT+'/reports',after_capture=diag.capture)
        m.register();r.update(status='RUNNING',flux_monitor=m.manifest(),spike_diagnostics=diag.manifest());persist();current=0
        for target in [50]+list(range(500,5001,500)):
            step(f'iterate_{current}_to_{target}',lambda current=current,target=target:s.settings.solution.run_calculation.iterate(iter_count=target-current),max(600,(target-current)*20))
            r['actual_iteration']=n();assert n()==target and not s.settings.solution.run_calculation.iterating()
            m.assert_complete(target);diag.assert_complete(target)
            r.update(flux_monitor=m.manifest(),spike_diagnostics=diag.manifest())
            last=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1]);assert json.loads(read_text(s,last['remote_path']))==last
            r['remote_flux_readbacks'].append({'iteration':target,'path':last['remote_path'],'matches_local':True})
            (out/f'history-{target:05d}.out').write_text(read_text(s,r['report']))
            r['scalar_coverage']=scalar_audit(out/f'history-{target:05d}.out',target)
            r['residual_coverage']=residual_audit(out/'solve.trn',expected_residual_equations(r),target)
            r['latest_metrics']=step(f'metrics_{target}',lambda:s.settings.solution.report_definitions.compute(report_defs=reports))
            save('final' if target==5000 else f'n{target:05d}');current=target;r['segment_iterations']=target
            if target==50:
                r['instrumentation_smoke']='N1-50 scalar, exact-face flux, all eight residuals, source lag and native diagnostics PASS'
                (out/'smoke-n00050.json').write_text(json.dumps({'status':'PASS','iteration':50,'scalar':r['scalar_coverage'],'residuals':r['residual_coverage'],'pair':r['pairs']['n00050'],'diagnostics':diag.manifest()},indent=2)+'\n')
            persist()
        m.unregister();r['flux_monitor']=m.manifest();m=None
        r['final_sections']=step('extract_final_sections',lambda:export_sections(s,r['sections'],out/'final-sections'),180)
        r['final_axial_sections']=step('extract_final_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'final-axial-sections'),180)
        step('stop_native_transcript',s.settings.file.stop_transcript)
        assert n()==5000 and not s.settings.solution.run_calculation.iterating()
        r.update(status='HORIZON_COMPLETE_ANALYSIS_PENDING',completed_iterations=5000);persist()
    except Exception as exc:
        signal.alarm(0);r.update(status='BLOCKED_EXECUTION',error=str(exc));(out/'error.txt').write_text(traceback.format_exc());persist();raise
    finally:
        signal.alarm(0)
        if m is not None:
            try:m.unregister()
            except Exception as exc:r['callback_cleanup_error']=str(exc)
            r['flux_monitor']=m.manifest()
        if s is not None:
            try:s.transcript.stop()
            except Exception:pass
        if diag is not None:diag.close();r['spike_diagnostics']=diag.manifest()
        persist();print('EVIDENCE',out,flush=True)


if __name__=='__main__':main()
