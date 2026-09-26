"""Recover E3 after local-controller loss; never reload, initialize or terminate Fluent.

Requires preserved live N4284 and the complete N1..4283 local prefix. Recover
N4284 from its unchanged native state, then advance only to global N5000.
"""
from run_phase07b_screen import *
import shutil,time,threading
from types import SimpleNamespace
from pyansys_fluent.phase07b_spike_monitor import Phase07bSpikeMonitor
from ansys.fluent.core.streaming_services.events_streaming import SolverEvent


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--parent-manifest',type=Path,required=True);ap.add_argument('--preservation-receipt',type=Path,required=True);ap.add_argument('--run-id',required=True);a=ap.parse_args()
    old=json.loads(a.parent_manifest.read_text());receipt=json.loads(a.preservation_receipt.read_text());parent=a.parent_manifest.parent
    assert old['case_id']=='S40-T020-DIAG' and old['tau_s']==.02 and receipt['status']=='PRESERVED_PAUSED_STATE' and receipt['pair_exists']
    start=4284;prefix_end=start-1;out=BASE/'output'/a.run_id;out.mkdir()
    lock=(BASE/'output/phase07b-server1-controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);lock.seek(0);lock.truncate();lock.write(json.dumps({'pid':os.getpid(),'run_id':a.run_id}));lock.flush()
    r=dict(old);r.update(run_id=a.run_id,controller_pid=os.getpid(),steps=[],status='VERIFYING_RECOVERY',actual_iteration=start,parent_manifest=str(a.parent_manifest),preservation_receipt=str(a.preservation_receipt),resume_mode='unchanged live N4284; no reload/initialization',start_iteration=start,prefix_end=prefix_end,orphan_pause_events=[],error=None)
    r['pairs']=dict(old['pairs']);r['pairs']['recovery-preserved']=receipt['case'];r['implementation_sha256']=dict(old['implementation_sha256']);r['implementation_sha256'][str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    mux=threading.RLock()
    def persist():
        with mux:
            temp=out/'manifest.tmp';temp.write_text(json.dumps(r,indent=2,default=str)+'\n');temp.replace(out/'manifest.json')
    def timeout(*_):raise TimeoutError('RPC deadline; reconcile before retry')
    signal.signal(signal.SIGALRM,timeout)
    def step(name,fn,seconds=90):
        e={'name':name,'state':'STARTED','started_utc':datetime.now(timezone.utc).isoformat()};r['steps'].append(e);persist();print(name,flush=True);signal.alarm(seconds)
        try:
            v=fn();e.update(state='PASS',value='attached, cleanup_on_exit=False' if name=='connect' else v);return v
        except Exception as x:e.update(state='FAIL',error=str(x));raise
        finally:signal.alarm(0);e['ended_utc']=datetime.now(timezone.utc).isoformat();persist()
    s=m=diag=None;observer=None;transcript_cb=None
    try:
        s=step('connect',lambda:connect(1,start_transcript=False,tcp_timeout_seconds=5),30)
        n=lambda:int(s.settings.setup.named_expressions['P7bGlobalIteration'].get_value())
        def verify():
            assert n()==start and not s.settings.solution.run_calculation.iterating()
            retired=s.scheme.eval("(map (lambda (i) (check-monitor-existence (string->symbol (format #f \"pause-on-solution-events-~d\" i)))) '(12 13))")
            assert retired==[False,False],retired
            assert all(remote_file_exists(s,receipt['case'].replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            for name,d in old['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==d,name
            for z,phases in old['source_slots'].items():
                for ph,slots in phases.items():exact_parity(slots,s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state(),z+'.'+ph)
            exact_parity(old['reference_methods'],s.settings.solution.methods.get_state(),'methods')
            exact_parity(old['reference_controls'],s.settings.solution.controls.get_state(),'controls')
            exact_parity(old['report_definitions'],s.settings.solution.report_definitions.get_state(),'reports')
            assert s.settings.solution.run_calculation.profile_update_interval()==1
            info=s.fields.solution_variable_info.get_zones_info();assert info['p7b-collector'].count==COUNTS[40] and info[ZONE].count+info['p7b-collector'].count==620431
            history=read_text(s,old['report']);(out/f'history-{start:05d}.out').write_text(history);rows=np.loadtxt(history.splitlines(),skiprows=3);assert np.array_equal(rows[:,0],np.arange(1,start+1)) and np.isfinite(rows).all()
            transcript=read_text(s,old['remote_transcript']);(out/'solve.trn').write_text(transcript);res,au=parse_residuals(out/'solve.trn');assert len(res)==8 and set(range(1,start)).issubset(res['iteration']),au
            # The old callback pause preceded printing N4284. Fluent normally
            # reprints its current residual row on the next iterate command.
            # Permit only that known boundary omission before the five-step
            # recovery smoke; require all rows after it, without interpolation.
            missing=sorted(set(range(1,start+1))-set(res['iteration']))
            assert missing in ([],[start]),missing
            r['pending_native_boundary_residual']=missing
            assert not au['conflicting_indices'] and not au['nonfinite_columns']
            assert not any(x in transcript for x in ['SEGMENTATION VIOLATION','floating point exception','Divergence detected'])
            last=json.loads((parent/'collector-flux.jsonl').read_text().splitlines()[-1]);assert last['iteration']==prefix_end and json.loads(read_text(s,last['remote_path']))==last
            speed=[json.loads(x) for x in (parent/'spike-diagnostics/spike-history.jsonl').read_text().splitlines()];assert [x['iteration'] for x in speed]==list(range(1,start))
            assert n()==start
            return {'live_iteration':start,'iterating':False,'settings_match':True,'scalar_through':start,'residual_through':int(au['last_iteration']),'pending_boundary_residual':missing,'prefix_through':prefix_end,'native_flux_prefix_readback':True}
        r['recovery_verification']=step('verify_live_state_and_prefix',verify,180)
        for folder in ['initial-sections','initial-axial-sections']:
            shutil.copytree(parent/folder,out/folder)
        for file in ['initial-parity.json','configuration-parity.json','smoke-n00050.json']:
            if (parent/file).exists():shutil.copy2(parent/file,out/file)
        for file in parent.glob('history-*.out'):
            if not (out/file.name).exists():shutil.copy2(file,out/file.name)
        def append_transcript(text):
            with (out/'solve.trn').open('a') as f:f.write(text)
        s.transcript.start(file_name=str(out/'solve-segment.trn'),write_to_stdout=False);transcript_cb=s.transcript.register_callback(append_transcript,keep_new_lines=True)
        diag=Phase07bSpikeMonitor(s,[ZONE,'p7b-collector'],out/'spike-diagnostics')
        old_diag=json.loads((parent/'spike-diagnostics/manifest.json').read_text());assert old_diag['error'] is None
        for file in (parent/'spike-diagnostics').glob('fields-*'):shutil.copy2(file,diag.directory/file.name)
        shutil.copy2(parent/'spike-diagnostics/geometry.npz',diag.directory/'geometry.npz')
        with np.load(diag.directory/'geometry.npz') as geo:diag.geometry={k:geo[k] for k in geo.files}
        for snap in old_diag['snapshots']:
            snap=dict(snap);snap['path']=str((diag.directory/Path(snap['path']).name).resolve());diag.snapshots.append(snap)
        speed_prefix=(parent/'spike-diagnostics/spike-history.jsonl').read_text()
        for row in map(json.loads,speed_prefix.splitlines()):assert diag.schedule.reasons(row['iteration'],row['max_speed_m_s'])==row['snapshot_reasons']
        diag.file.write(speed_prefix);diag.file.flush();diag.last_iteration=prefix_end;diag.persist()
        faces=[FluxFaceZone(**x) for x in old['flux_monitor']['face_zones']]
        m=Phase07bFluxMonitor(s,face_zones=faces,start_iteration=prefix_end,local_jsonl=out/'collector-flux.jsonl',remote_directory=ROOT+'/reports',prefix_source=parent/'collector-flux.jsonl',after_capture=diag.capture)
        # An observed unknown pause may belong to the departed controller. Only
        # recover a single such registration on this verified, exclusively owned
        # E3 session, and capture its iteration before releasing it.
        def observe_pause(session,event_info):
            event_id=int(event_info.level)
            if event_id in session.events._sync_event_ids.values():return
            if r['orphan_pause_events'] and event_id!=r['orphan_pause_events'][0]['registration_id']:raise RuntimeError('More than one unknown pause registration; reconcile')
            index=int(event_info.index);assert n()==index
            m._capture(session,SimpleNamespace(index=index));m.assert_complete(index);diag.assert_complete(index)
            row={'registration_id':event_id,'iteration':index,'action':'captured then unregister/resume departed controller pause'};r['orphan_pause_events'].append(row);persist()
            session._app_utilities.unregister_pause_on_solution_events(registration_id=event_id)
            session._app_utilities.resume_on_solution_event(registration_id=event_id)
        observer=s.events.register_callback(SolverEvent.SOLUTION_PAUSED,observe_pause)
        m.register();r['pause_registration_ids']=dict(s.events._sync_event_ids);persist()
        step('recover_completed_n4284_callback',lambda:m._capture(s,SimpleNamespace(index=start)),120)
        m.assert_complete(start);diag.assert_complete(start);assert n()==start and not s.settings.solution.run_calculation.iterating()
        last=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1]);assert json.loads(read_text(s,last['remote_path']))==last
        r['recovered_current_row']={'iteration':start,'mode':'captured unchanged native state before any continuation','remote_flux_readback':True,'native_speed':json.loads((diag.directory/'spike-history.jsonl').read_text().splitlines()[-1])['max_speed_m_s']}
        r.update(status='RUNNING',flux_monitor=m.manifest(),spike_diagnostics=diag.manifest());persist()
        current=start
        for target in [start+5,4500,5000]:
            step(f'iterate_{current}_to_{target}',lambda current=current,target=target:s.settings.solution.run_calculation.iterate(iter_count=target-current),max(600,(target-current)*20))
            assert n()==target and not s.settings.solution.run_calculation.iterating();m.assert_complete(target);diag.assert_complete(target);r.update(actual_iteration=target,flux_monitor=m.manifest(),spike_diagnostics=diag.manifest())
            last=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1]);assert json.loads(read_text(s,last['remote_path']))==last;r.setdefault('remote_flux_readbacks',[]).append({'iteration':target,'path':last['remote_path'],'matches_local':True})
            history=read_text(s,r['report']);(out/f'history-{target:05d}.out').write_text(history);rows=np.loadtxt(history.splitlines(),skiprows=3);assert np.array_equal(rows[:,0],np.arange(1,target+1)) and np.isfinite(rows).all()
            res,au=parse_residuals(out/'solve.trn');assert len(res)==8 and set(range(1,target+1)).issubset(res['iteration']) and not au['conflicting_indices'] and not au['nonfinite_columns'];r['residual_coverage']=au;r['pending_native_boundary_residual']=[]
            assert not any(x in (out/'solve.trn').read_text() for x in ['SEGMENTATION VIOLATION','floating point exception','Divergence detected'])
            r['latest_metrics']=step(f'metrics_{target}',lambda:s.settings.solution.report_definitions.compute(report_defs=s.settings.solution.monitor.report_files['p7b-screen-history'].report_defs()))
            tag='final' if target==5000 else f'n{target:05d}';path=ROOT+'/case-data/'+a.run_id+'-'+tag+'.cas.h5';assert not any(remote_file_exists(s,path.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
            step('save_'+tag,lambda:s.settings.file.write_case_data(file_name=path),180);assert all(remote_file_exists(s,path.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5']);r['pairs'][tag]=path;current=target;r['segment_iterations']=current-start;persist()
        m.unregister();r['flux_monitor']=m.manifest();m=None;s.events.unregister_callback(observer);observer=None
        r['final_sections']=step('extract_final_sections',lambda:export_sections(s,r['sections'],out/'final-sections'),180)
        r['final_axial_sections']=step('extract_final_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'final-axial-sections'),180)
        step('stop_native_transcript',s.settings.file.stop_transcript);r.update(status='HORIZON_COMPLETE_ANALYSIS_PENDING',completed_iterations=5000);persist()
    except Exception as ex:
        signal.alarm(0);r.update(status='BLOCKED_EXECUTION',error=str(ex));(out/'error.txt').write_text(traceback.format_exc());persist();raise
    finally:
        signal.alarm(0)
        if m is not None:
            try:m.unregister()
            except Exception as ex:r['callback_cleanup_error']=str(ex)
            r['flux_monitor']=m.manifest()
        if s is not None:
            if observer is not None:
                try:s.events.unregister_callback(observer)
                except Exception:pass
            try:
                if transcript_cb is not None:s.transcript.unregister_callback(transcript_cb)
                s.transcript.stop()
            except Exception:pass
        if diag is not None:diag.close();r['spike_diagnostics']=diag.manifest()
        persist();print('EVIDENCE',out,flush=True)

if __name__=='__main__':main()
