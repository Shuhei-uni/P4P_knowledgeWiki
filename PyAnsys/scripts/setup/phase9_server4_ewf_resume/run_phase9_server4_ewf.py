"""Observe the inherited Server 4 batch, recover its endpoint, submit no solve."""
from pathlib import Path,PureWindowsPath
import sys,json,time,threading,argparse,fcntl,math,re,traceback
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent import ewf_local_drain as drain
from run_phase72a_adaptive_film import FILM
import grpc
from ansys.api.fluent.v0 import settings_pb2,settings_pb2_grpc,transcript_pb2,transcript_pb2_grpc

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live-transcript',required=True);args=parser.parse_args()
    out=run.OUT;tag=str(time.time_ns());evidence=out/('ewf-resume-'+tag);evidence.mkdir()
    lock=(out/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    m=json.loads((out/'2_6M-run.json').read_text());assert m['verified_native_end']==8580 and m['active_target']==11080
    run.dump(evidence/'inherited-run.json',m)
    cfg=resolve_connection_kwargs('4',start_transcript=False,tcp_timeout_seconds=3)
    channel=grpc.insecure_channel(f"{cfg['ip']}:{cfg['port']}");metadata=(('password',cfg['password']),)
    stream=transcript_pb2_grpc.TranscriptStub(channel).BeginStreaming(transcript_pb2.TranscriptRequest(),metadata=metadata)
    stop=threading.Event()
    def observe():
        try:
            with Path(args.live_transcript).open('a') as f:
                for reply in stream:
                    if stop.is_set():break
                    f.write(reply.transcript);f.flush()
        except grpc.RpcError as exc:
            run.dump(evidence/'passive-stream-end.json',{'rpc_code':exc.code().name,'not_solver_failure_proof':True})
    observer=threading.Thread(target=observe,daemon=True);observer.start()
    print('OBSERVING_INHERITED_NATIVE_BATCH',8580,11080,flush=True)
    stub=settings_pb2_grpc.SettingsStub(channel)
    while True:
        request=settings_pb2.GetAttrsRequest();request.path_info.root='fluent'
        request.path_info.path='solution/run-calculation/iterate';request.attrs.append('active?')
        try:
            response=stub.GetAttrs(request,metadata=metadata,timeout=5)
            idle=response.values.value_map.m['active?'].boolean
            run.dump(evidence/'bounded-idle.json',{'observed_epoch':time.time(),'idle':idle})
            if idle:break
        except grpc.RpcError:
            pass
        if json.loads((out/'human-pause.json').read_text()).get('status')!='EWF_RUN_AUTHORISED':return
        time.sleep(20)
    stop.set();stream.cancel();observer.join(timeout=2);channel.close()
    for key,name in [('work','WORK'),('shared','SHARED'),('parent','PARENT'),('mesh_folder','MESH_FOLDER'),('host_python','HOST_PYTHON')]:setattr(run,name,PureWindowsPath(json.loads((out/'server4-paths.json').read_text())[key]))
    s=run.attach();run.require_idle(s);end=run.native_iteration(s);assert end==11080
    run.require_bulk_audit(s);run.assert_bulk_active(s);run.read_feed(s,1.0);drain.audit(s,True)
    s.settings.file.stop_transcript()
    text=run.read_text(s,m['active_transcript']);(evidence/'native-adjustment.trn').write_text(text)
    rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
    assert len(rows)==2500 and re.search(r'^\s*11080\s+',text,re.M)
    assert not re.search(r'floating point exception|fatal error|Divergence detected',text,re.I)
    assert all(all(math.isfinite(v) for v in row) and 0<=row[2]<1 for row in rows)
    assert all(math.isclose(row[1],1e-7,rel_tol=1e-7) and math.isclose(row[0],0.0007+(i+1)*1e-7,abs_tol=1e-10,rel_tol=1e-6) for i,row in enumerate(rows))
    before=run.base.state(s)
    pair=run.save(s,run.WORK/'2_6M'/'ewf-200ms','recovered-adjustment-N11080-'+tag)
    proof_path=evidence/'checkpoint-proof.json';proof={'status':'SAVED_REOPEN_PENDING','pair':pair,'before':before};run.dump(proof_path,proof)
    run.load(s,pair);after=run.base.state(s)
    run.require_match(after['readback'],before['readback']);run.require_setup_same(after['setup'],before['setup'])
    assert before['methods']==after['methods'];run.require_bulk_audit(s);run.assert_bulk_active(s);drain.audit(s,True)
    assert math.isclose(run.film(s)['film_elapsed_time'],0.00095,abs_tol=1e-12)
    proof.update(status='REOPEN_VERIFIED',after=after,film=run.film(s));run.dump(proof_path,proof)
    record={'stage':'ewf-bulk-active-adjustment','start':8580,'end':11080,'film_start_s':0.0007,'film_end_s':0.00095,
            'step_s':1e-7,'peak_film_courant':max(row[2] for row in rows),'transcript':m['active_transcript'],
            'pair':pair,'checkpoint_proof':str(proof_path),'recovered_after':'laptop closure; no repeat solve'}
    m['blocks'].append(record);m.update(status='EWF_ADJUSTMENT_COMPLETE',verified_native_end=11080,active_target=None,latest_pair=pair,next_stage='frozen-transition-1000-at-0p1us')
    run.dump(out/'2_6M-run.json',m)
    run.dump(out/'ewf-adjustment-current.json',{'status':'EWF_ADJUSTMENT_COMPLETE','block':record,'next_stage':m['next_stage']})
    run.dump(out/'campaign-manifest.json',{'status':'EWF_ADJUSTMENT_COMPLETE','active_mesh':'2_6M','phase':'EWF_200MS','completed':[]})
    print('EWF_ADJUSTMENT_COMPLETE_RECOVERED_NO_SOLVE',11080,flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        run.dump(run.OUT/('ewf-resume-failure-'+str(time.time_ns())+'.json'),{'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),'no_solve_submitted':True})
        raise
