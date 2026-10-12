"""Recover completed frozen transition and continue; never repeat its solve."""
from pathlib import Path,PureWindowsPath
import sys,json,time,math,argparse,fcntl,importlib.util,re,traceback
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
from pyansys_fluent import ewf_local_drain as drain
from run_phase72a_adaptive_film import FILM
spec=importlib.util.spec_from_file_location('server4_continuation',ROOT/'scripts/setup/phase9_server4_ewf_continuation/run_phase9_server4_ewf.py')
cont=importlib.util.module_from_spec(spec);spec.loader.exec_module(cont)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live-transcript',required=True);args=parser.parse_args()
    out=run.OUT;tag=str(time.time_ns());evidence=out/('frozen-transition-recovery-'+tag);evidence.mkdir()
    lock=(out/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    paths=json.loads((out/'server4-paths.json').read_text())
    for key,name in [('work','WORK'),('shared','SHARED'),('parent','PARENT'),('mesh_folder','MESH_FOLDER'),('host_python','HOST_PYTHON')]:setattr(run,name,PureWindowsPath(paths[key]))
    m=json.loads((out/'2_6M-run.json').read_text());run.dump(evidence/'inherited-run.json',m)
    assert m['verified_native_end']==11080 and m['active_target']==12080
    assert not cont.pause_requested()
    s=run.attach();run.require_idle(s);assert run.native_iteration(s)==12080
    assert s.settings.solution.controls.equations.get_state()=={k:False for k in ['drift','flow','ke','mp']}
    run.require_bulk_audit(s);drain.audit(s,True)
    text=run.read_text(s,m['active_transcript']);(evidence/'native-frozen-transition.trn').write_text(text)
    rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
    assert len(rows)==1000
    assert not re.search(r'floating point exception|fatal error|Divergence detected',text,re.I)
    assert all(all(math.isfinite(v) for v in row) and 0<=row[2]<1 for row in rows)
    assert all(math.isclose(row[1],1e-7,rel_tol=1e-7) and math.isclose(row[0],0.00095+(i+1)*1e-7,abs_tol=1e-10,rel_tol=1e-6) for i,row in enumerate(rows))
    record={'stage':'ewf-frozen-transition','start':11080,'end':12080,'film_start_s':0.00095,
            'film_end_s':0.00105,'step_s':1e-7,'peak_film_courant':max(row[2] for row in rows),
            'transcript':m['active_transcript'],'bulk_active':False,'recovered_without_repeat_solve':True}
    provisional=json.loads(json.dumps(m));provisional['blocks'].append(record)
    provisional.update(verified_native_end=12080,active_target=None,status='CHECKPOINT_VERIFIED')
    pair,proof=cont.checkpoint(s,provisional,'recovered-frozen-transition-N12080')
    record.update(pair=pair,checkpoint_proof=proof);m=provisional;run.dump(out/'2_6M-run.json',m)
    run.dump(evidence/'recovery-receipt.json',{'status':'REOPEN_VERIFIED','native_iteration':12080,'film_end_s':0.00105,'pair':pair,'checkpoint_proof':proof,'no_repeat_solve':True})
    print('FROZEN_TRANSITION_RECOVERED_NO_REPEAT',12080,flush=True)
    s.transcript.start(file_name=args.live_transcript,write_to_stdout=False)
    cont.set_stage(s,m,2.5e-6,False,'frozen-growth-2p5us')
    cont.batch(s,m,1000,'ewf-frozen-growth-first',2.5e-6)
    for steps in [10000]*7+[6580]:cont.batch(s,m,steps,'ewf-frozen-growth',2.5e-6)
    assert m['verified_native_end']==89660 and math.isclose(m['blocks'][-1]['film_end_s'],0.195,abs_tol=1e-12)
    cont.set_stage(s,m,2.5e-6,True,'final-bulk-active')
    cont.batch(s,m,2000,'ewf-final-bulk-active',2.5e-6)
    assert m['verified_native_end']==91660 and math.isclose(m['blocks'][-1]['film_end_s'],0.2,abs_tol=1e-12)
    run.assert_bulk_active(s)
    m.update(status='EWF_COMPLETE',next_stage=None);run.dump(out/'2_6M-run.json',m)
    run.dump(out/'campaign-manifest.json',{'status':'EWF_COMPLETE','active_mesh':'2_6M','phase':'EWF_200MS','completed':['2_6M']})
    print('EWF_COMPLETE',91660,0.2,flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        run.dump(run.OUT/('ewf-frozen-recovery-failure-'+str(time.time_ns())+'.json'),{'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),'never_exit_fluent':True})
        raise
