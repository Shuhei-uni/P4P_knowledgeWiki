"""Recover an inherited frozen-growth batch and finish Server 4's schedule."""
from pathlib import Path,PureWindowsPath
import sys,json,time,math,argparse,fcntl,importlib.util,re,traceback,threading
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.connection import resolve_connection_kwargs
from run_phase72a_adaptive_film import FILM
spec=importlib.util.spec_from_file_location('server4_continuation',ROOT/'scripts/setup/phase9_server4_ewf_continuation/run_phase9_server4_ewf.py')
cont=importlib.util.module_from_spec(spec);spec.loader.exec_module(cont)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live-transcript',required=True);args=parser.parse_args()
    out=run.OUT;tag=str(time.time_ns());evidence=out/('frozen-growth-resume-'+tag);evidence.mkdir()
    lock=(out/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    paths=json.loads((out/'server4-paths.json').read_text())
    for key,name in [('work','WORK'),('shared','SHARED'),('parent','PARENT'),('mesh_folder','MESH_FOLDER'),('host_python','HOST_PYTHON')]:setattr(run,name,PureWindowsPath(paths[key]))
    m=json.loads((out/'2_6M-run.json').read_text());run.dump(evidence/'inherited-run.json',m)
    start=m['verified_native_end'];end=m['active_target'];dt=m['film_step_s'];before_age=m['blocks'][-1]['film_end_s']
    assert dt==2.5e-6 and not m['all_bulk_equations_active'] and start<end<=89660
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
    s=run.attach();run.require_idle(s);assert run.native_iteration(s)==end
    assert s.settings.solution.controls.equations.get_state()=={k:False for k in ['drift','flow','ke','mp']}
    run.require_bulk_audit(s);run.read_feed(s,1.0);drain.audit(s,True)
    assert dict(s.rp_vars('wall-film/model-parameters'))['timestep-max']==dt
    # Suspended controller left the known native transcript open.
    s.settings.file.stop_transcript()
    text=run.read_text(s,m['active_transcript']);(evidence/'native-inherited-batch.trn').write_text(text)
    rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
    assert len(rows)==end-start
    assert not re.search(r'floating point exception|fatal error|Divergence detected',text,re.I)
    assert all(all(math.isfinite(v) for v in row) and 0<=row[2]<1 for row in rows)
    assert all(math.isclose(row[1],dt,rel_tol=1e-7) and math.isclose(row[0],before_age+(i+1)*dt,abs_tol=1e-10,rel_tol=1e-6) for i,row in enumerate(rows))
    record={'stage':m['active_stage'],'start':start,'end':end,'film_start_s':before_age,
            'film_end_s':before_age+(end-start)*dt,'step_s':dt,'peak_film_courant':max(row[2] for row in rows),
            'transcript':m['active_transcript'],'bulk_active':False,'recovered_without_repeat_solve':True}
    provisional=json.loads(json.dumps(m));provisional['blocks'].append(record)
    provisional.update(verified_native_end=end,active_target=None,status='CHECKPOINT_VERIFIED')
    pair,proof=cont.checkpoint(s,provisional,'recovered-frozen-growth-N'+str(end))
    record.update(pair=pair,checkpoint_proof=proof);m=provisional;run.dump(out/'2_6M-run.json',m)
    run.dump(evidence/'recovery-receipt.json',{'status':'REOPEN_VERIFIED','native_iteration':end,'film_end_s':record['film_end_s'],'pair':pair,'checkpoint_proof':proof,'no_repeat_solve':True})
    print('FROZEN_GROWTH_RECOVERED_NO_REPEAT',end,record['film_end_s'],flush=True)
    s.transcript.start(file_name=args.live_transcript,write_to_stdout=False)
    while m['verified_native_end']<89660:
        remaining=89660-m['verified_native_end'];steps=min(10000,remaining)
        if 0<remaining-steps<1000:steps=remaining
        assert steps>=1000
        cont.batch(s,m,steps,'ewf-frozen-growth',dt)
    assert math.isclose(m['blocks'][-1]['film_end_s'],0.195,abs_tol=1e-12)
    cont.set_stage(s,m,dt,True,'final-bulk-active')
    cont.batch(s,m,2000,'ewf-final-bulk-active',dt)
    assert m['verified_native_end']==91660 and math.isclose(m['blocks'][-1]['film_end_s'],0.2,abs_tol=1e-12)
    run.assert_bulk_active(s)
    m.update(status='EWF_COMPLETE',next_stage=None);run.dump(out/'2_6M-run.json',m)
    run.dump(out/'campaign-manifest.json',{'status':'EWF_COMPLETE','active_mesh':'2_6M','phase':'EWF_200MS','completed':['2_6M']})
    print('EWF_COMPLETE',91660,0.2,flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        run.dump(run.OUT/('ewf-growth-resume-failure-'+str(time.time_ns())+'.json'),{'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),'never_exit_fluent':True})
        raise
