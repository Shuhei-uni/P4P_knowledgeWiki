"""Recover an inherited frozen-growth batch and finish Server 4's schedule."""
from pathlib import Path,PureWindowsPath
import sys,json,time,math,argparse,fcntl,importlib.util,re,traceback,threading
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.connection import resolve_connection_kwargs
from run_phase72a_adaptive_film import FILM
spec=importlib.util.spec_from_file_location('server4_continuation',Path(__file__).with_name('continuation.py'))
cont=importlib.util.module_from_spec(spec);spec.loader.exec_module(cont)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live-transcript',required=True);args=parser.parse_args()
    out=run.OUT;tag=str(time.time_ns());evidence=out/('frozen-growth-resume-'+tag);evidence.mkdir()
    lock=(out/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    paths=json.loads((out/'server4-paths.json').read_text())
    for key,name in [('work','WORK'),('shared','SHARED'),('parent','PARENT'),('mesh_folder','MESH_FOLDER'),('host_python','HOST_PYTHON')]:setattr(run,name,PureWindowsPath(paths[key]))
    m=json.loads((out/'2_6M-run.json').read_text());run.dump(evidence/'inherited-run.json',m)
    dt=m['film_step_s']
    assert dt==2.5e-6 and not m['all_bulk_equations_active']
    assert not cont.pause_requested()
    # Passive stream and bounded idle checks; no SDK bootstrap while calculating.
    import grpc
    from ansys.api.fluent.v0 import settings_pb2,settings_pb2_grpc,transcript_pb2,transcript_pb2_grpc
    cfg=resolve_connection_kwargs('4',start_transcript=False,tcp_timeout_seconds=3)
    channel=grpc.insecure_channel(f"{cfg['ip']}:{cfg['port']}");md=(('password',cfg['password']),)
    stream=transcript_pb2_grpc.TranscriptStub(channel).BeginStreaming(transcript_pb2.TranscriptRequest(),metadata=md)
    def observe():
        try:
            with Path(args.live_transcript).open('a') as f:
                for response in stream:f.write(response.transcript);f.flush()
        except grpc.RpcError:pass
    observer=threading.Thread(target=observe,daemon=True);observer.start()
    stub=settings_pb2_grpc.SettingsStub(channel)
    while True:
        if cont.pause_requested():return
        req=settings_pb2.GetAttrsRequest();req.path_info.root='fluent';req.path_info.path='solution/run-calculation/iterate';req.attrs.append('active?')
        try:
            if stub.GetAttrs(req,metadata=md,timeout=5).values.value_map.m['active?'].boolean:break
        except grpc.RpcError:pass
        time.sleep(20)
    stream.cancel();observer.join(timeout=2);channel.close()
    s=run.attach();run.require_idle(s);n=run.native_iteration(s)
    print('MANUAL_HANDOFF_IDLE_NATIVE',n,flush=True)
    assert n in (25000,35000), 'Unexpected idle endpoint: preserve and reconcile before continuing'
    assert s.settings.solution.controls.equations.get_state()=={k:False for k in ['drift','flow','ke','mp']}
    run.require_bulk_audit(s);run.read_feed(s,1.0);drain.audit(s,True)
    params=dict(s.rp_vars('wall-film/model-parameters'))
    assert params['timestep-max']==dt
    age=0.03335+(n-25000)*dt
    # Preserve the actual loaded endpoint under a unique local name before any continuation.
    pair=run.save(s,run.WORK/'2_6M'/'ewf-200ms','manual-handoff-preserved-N'+str(n)+'-'+str(time.time_ns()))
    run.dump(evidence/'preserved-current-pair.json',{'pair':pair,'native_iteration':n,'accepted':False})
    if params['sub-iter-nums']!=50:
        s.rp_vars('wall-film/model-parameters',[(k,50 if k=='sub-iter-nums' else v) for k,v in params.items()])
    assert dict(s.rp_vars('wall-film/model-parameters'))['sub-iter-nums']==50
    print('MAX_SUBITERATIONS_READBACK',50,flush=True)
    if n==35000:
        text=run.read_text(s,m['active_transcript']);(evidence/'manual-handoff-native.trn').write_text(text)
        rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
        relevant=[row for row in rows if 0.03335<row[0]<=0.0583500001]
        assert all(all(math.isfinite(v) for v in row) and row[2]>=0 and math.isclose(row[1],dt,rel_tol=1e-7) for row in relevant)
        clock=run.film(s)['film_elapsed_time']
        assert math.isclose(clock,age,abs_tol=1e-10), 'Preserved endpoint film clock differs'
        run.dump(evidence/'historical-transcript-gap.json',{'status':'RECORDED_EVIDENCE_GAP','rows_in_old_transcript':len(rows),'relevant_rows':len(relevant),'requested_updates':10000,'native_endpoint':n,'saved_clock_s':clock,'acceptance_basis':'User-directed settings/counts continuation; exact native endpoint and paired save/hash/reopen clock/setup proof. Historical batch is not certified numerically healthy.','original_failure_preserved':True})
        print('HISTORICAL_TRANSCRIPT_GAP_RECORDED',len(relevant),10000,flush=True)
    m['prior_run_record']=str(evidence/'inherited-run.json')
    m['blocks']=[{'stage':'user-selected-N25000-manual-handoff','end':n,'film_end_s':age,'parent_case':str(run.WORK/'2_6M'/'ewf-200ms'/'auto-25000-1-25000.cas.h5'),'max_subiterations':50}]
    m.update(verified_native_end=n,active_target=None,status='RECONCILING_MANUAL_HANDOFF',all_bulk_equations_active=False)
    pair,proof=cont.checkpoint(s,m,'manual-handoff-reopened-N'+str(n))
    m.update(film_courant_limit=None,max_film_subiterations=50,status='CHECKPOINT_VERIFIED');run.dump(out/'2_6M-run.json',m)
    print('MANUAL_HANDOFF_RECONCILED_NO_COURANT_CEILING',n,age,flush=True)
    s.transcript.start(file_name=args.live_transcript,write_to_stdout=False)
    dt=5e-6
    frozen_updates=round((0.195-age)/dt)
    assert frozen_updates>=1000 and math.isclose(age+frozen_updates*dt,0.195,abs_tol=1e-12)
    frozen_end=n+frozen_updates;final_end=frozen_end+1000
    m.update(next_film_step_s=dt,frozen_target_native=frozen_end,final_target_native=final_end)
    run.dump(out/'2_6M-run.json',m)
    cont.set_stage(s,m,dt,False,'frozen-growth-5us')
    assert dict(s.rp_vars('wall-film/model-parameters'))['iters-per-dpm-step']==4
    assert dict(s.rp_vars('wall-film/model-parameters'))['sub-iter-nums']==50
    print('NEXT_STEP_VERIFIED',dt,'FROZEN_END',frozen_end,'FINAL_END',final_end,flush=True)
    while m['verified_native_end']<frozen_end:
        remaining=frozen_end-m['verified_native_end'];steps=min(10000,remaining)
        if 0<remaining-steps<1000:steps=remaining
        assert steps>=1000
        cont.batch(s,m,steps,'ewf-frozen-growth-5us',dt)
    assert math.isclose(m['blocks'][-1]['film_end_s'],0.195,abs_tol=1e-12)
    cont.set_stage(s,m,dt,True,'final-bulk-active-5us')
    cont.batch(s,m,1000,'ewf-final-bulk-active-5us',dt)
    assert m['verified_native_end']==final_end and math.isclose(m['blocks'][-1]['film_end_s'],0.2,abs_tol=1e-12)
    run.assert_bulk_active(s)
    m.update(status='EWF_COMPLETE',next_stage=None);run.dump(out/'2_6M-run.json',m)
    run.dump(out/'campaign-manifest.json',{'status':'EWF_COMPLETE','active_mesh':'2_6M','phase':'EWF_200MS','completed':['2_6M']})
    print('EWF_COMPLETE',final_end,0.2,flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        run.dump(run.OUT/('ewf-growth-resume-failure-'+str(time.time_ns())+'.json'),{'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),'never_exit_fluent':True})
        raise
