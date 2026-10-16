"""Wait for the verified adjustment, then execute Server 4's remaining schedule.

The waiting successor never connects to Fluent while its predecessor is alive.
Only the exclusive controller-lock owner can send commands.
"""
from pathlib import Path, PureWindowsPath
import sys, json, time, os, argparse, fcntl, subprocess, math, re, traceback, hashlib
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.ewf_staged import refresh_plan
from run_phase72a_adaptive_film import FILM

OUT=run.OUT

def read(name):
    return json.loads((OUT/name).read_text())

def predecessor_alive(pid):
    row=subprocess.run(['ps','-p',str(pid),'-o','stat=,command='],capture_output=True,text=True,timeout=5).stdout.strip()
    return bool(row) and not row.startswith('Z') and 'run_phase9_server4_ewf.py' in row

def pause_requested():
    return read('human-pause.json').get('status') != 'EWF_RUN_AUTHORISED'

def checkpoint(s,m,label):
    run.require_idle(s)
    before=run.base.state(s)
    pair=run.save(s,run.WORK/'2_6M'/'ewf-200ms',label+'-'+str(time.time_ns()))
    proof={'status':'SAVED_REOPEN_PENDING','pair':pair,'before':before}
    path=OUT/('ewf-checkpoint-'+str(time.time_ns())+'.json');run.dump(path,proof)
    run.load(s,pair)
    after=run.base.state(s)
    run.require_match(after['readback'],before['readback'])
    run.require_setup_same(after['setup'],before['setup'])
    assert after['methods']==before['methods']
    run.require_bulk_audit(s);drain.audit(s,True)
    expected_clock=m['blocks'][-1]['film_end_s']
    assert math.isclose(run.film(s)['film_elapsed_time'],expected_clock,abs_tol=1e-12)
    assert run.native_iteration(s)==m['verified_native_end']
    proof.update(status='REOPEN_VERIFIED',after=after,film=run.film(s));run.dump(path,proof)
    m['latest_pair']=pair
    run.dump(OUT/'2_6M-run.json',m)
    return pair,str(path)

def set_stage(s,m,dt,bulk,label):
    run.require_idle(s)
    assert run.native_iteration(s)==m['verified_native_end']
    if pause_requested():raise RuntimeError('User pause: no settings or solve submitted')
    clock=m['blocks'][-1]['film_end_s']
    equations={key:bulk for key in ['drift','flow','ke','mp']}
    s.settings.solution.controls.equations.set_state(equations)
    p=dict(s.rp_vars('wall-film/model-parameters'));delta=refresh_plan(dt)
    s.rp_vars('wall-film/model-parameters',[(k,delta.get(k,v)) for k,v in p.items()])
    drain.configure(s,enabled=True,refresh_span_s=dt)
    assert s.settings.solution.controls.equations.get_state()==equations
    assert all(dict(s.rp_vars('wall-film/model-parameters'))[k]==v for k,v in delta.items())
    m.update(all_bulk_equations_active=bulk,film_step_s=dt,active_stage=label)
    checkpoint(s,m,'transition-'+label+'-N'+str(m['verified_native_end']))
    assert math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12)

def batch(s,m,steps,label,dt):
    run.require_idle(s)
    if pause_requested():raise RuntimeError('User pause: no new solve submitted')
    start=run.native_iteration(s);assert start==m['verified_native_end']
    end=start+steps;before_clock=m['blocks'][-1]['film_end_s']
    transcript=run.WORK/'2_6M'/'ewf-200ms'/f'{label}-N{start}-N{end}-{time.time_ns()}.trn'
    with run.native_batch_transcript(s,transcript):
        m.update(status='RUNNING',active_target=end,active_stage=label,active_transcript=str(transcript))
        run.dump(OUT/'2_6M-run.json',m)
        print('BATCH','2_6M',label,start,end,flush=True)
        run.base.iterate(s,steps)
    text=run.read_text(s,str(transcript))
    local=OUT/('ewf-'+transcript.name);local.write_text(text)
    rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
    assert len(rows)==steps
    assert run.native_iteration(s)==end
    if m['all_bulk_equations_active']:
        assert re.search(r'^\s*'+str(end)+r'\s+',text,re.M)
    assert not re.search(r'floating point exception|fatal error|Divergence detected',text,re.I)
    assert all(all(math.isfinite(v) for v in row) and 0<=row[2]<=0.8 for row in rows)
    assert all(math.isclose(row[1],dt,rel_tol=1e-7) and
               math.isclose(row[0],before_clock+(i+1)*dt,abs_tol=1e-10,rel_tol=1e-6)
               for i,row in enumerate(rows))
    record={'stage':label,'start':start,'end':end,'film_start_s':before_clock,
            'film_end_s':before_clock+steps*dt,'step_s':dt,'peak_film_courant':max(row[2] for row in rows),
            'transcript':str(transcript),'bulk_active':m['all_bulk_equations_active']}
    # Hold a separate provisional copy until paired persistence is proved.
    provisional=json.loads(json.dumps(m));provisional['blocks'].append(record)
    provisional.update(verified_native_end=end,active_target=None,status='CHECKPOINT_VERIFIED')
    pair,proof=checkpoint(s,provisional,label+'-N'+str(end))
    record.update(pair=pair,checkpoint_proof=proof)
    m.clear();m.update(provisional);run.dump(OUT/'2_6M-run.json',m)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--predecessor-pid',type=int,required=True)
    parser.add_argument('--live-transcript',required=True);parser.add_argument('--log',required=True)
    args=parser.parse_args()
    reservation=(OUT/'ewf-successor.lock').open('a+')
    fcntl.flock(reservation,fcntl.LOCK_EX|fcntl.LOCK_NB)
    ready={'status':'WAITING_VERIFIED_ADJUSTMENT','pid':os.getpid(),'predecessor_pid':args.predecessor_pid,
           'server_id':'4','native_start_required':11080,'no_fluent_connection_while_waiting':True,
           'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'requires_desktop_running':True,'log':args.log,'live_transcript':args.live_transcript,
           'remaining_commands':[1000,1000]+[10000]*7+[6580,2000],
           'final_native_iteration':91660,'final_film_age_s':0.2}
    run.dump(OUT/'ewf-successor.json',ready)
    while predecessor_alive(args.predecessor_pid):
        if pause_requested():
            ready['status']='CANCELLED_BY_USER_PAUSE';run.dump(OUT/'ewf-successor.json',ready);return
        ready['observed_utc']=datetime.now(timezone.utc).isoformat()
        run.dump(OUT/'ewf-successor.json',ready);time.sleep(10)
    if pause_requested():return
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==ready['runner_sha256']
    m=read('2_6M-run.json');completed=read('ewf-adjustment-current.json')
    assert m['status']=='EWF_ADJUSTMENT_COMPLETE' and m['verified_native_end']==11080
    assert completed['status']=='EWF_ADJUSTMENT_COMPLETE'
    assert completed['block']['end']==11080
    assert read('campaign-manifest.json')['status']=='EWF_ADJUSTMENT_COMPLETE'
    proof=json.loads(Path(completed['block']['checkpoint_proof']).read_text())
    assert proof['status']=='REOPEN_VERIFIED' and proof['pair']==m['latest_pair']
    controller=(OUT/'controller.lock').open('a+')
    fcntl.flock(controller,fcntl.LOCK_EX|fcntl.LOCK_NB)
    ready['status']='HANDOFF_ACCEPTED';run.dump(OUT/'ewf-successor.json',ready)
    paths=read('server4-paths.json')
    for key,name in [('work','WORK'),('shared','SHARED'),('parent','PARENT'),('mesh_folder','MESH_FOLDER'),('host_python','HOST_PYTHON')]:setattr(run,name,PureWindowsPath(paths[key]))
    run.dump(OUT/'desktop-controller.json',{'status':'EWF_CONTINUATION_PREFLIGHT','pid':os.getpid(),
        'argv':sys.argv,'server_id':'4','log':args.log,'live_transcript':args.live_transcript,
        'requires_desktop_running':True,'verified_native_end':11080,'active_target':12080})
    run.dump(OUT/'campaign-manifest.json',{'status':'EWF_CONTINUATION_RUNNING','active_mesh':'2_6M','phase':'EWF_200MS','completed':[]})
    s=run.attach();run.require_idle(s);assert run.native_iteration(s)==11080
    run.require_bulk_audit(s);run.assert_bulk_active(s);run.read_feed(s,1.0);drain.audit(s,True)
    expected=read('ewf-settings-current.json')['changes']
    actual=dict(s.rp_vars('wall-film/model-parameters'))
    assert all(actual[k]==v for k,v in expected.items())
    for name in ['wall','wall:004']:
        wall=s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film.get_state()
        assert wall['eulerian_film_wall'] and not wall['enable_flow_momentum_coupling']
    assert math.isclose(run.film(s)['film_elapsed_time'],0.00095,abs_tol=1e-12)
    for key in ['case','data']:assert run.remote_file_exists(s,m['latest_pair'][key])
    s.transcript.start(file_name=args.live_transcript,write_to_stdout=False)
    set_stage(s,m,1e-7,False,'frozen-transition')
    batch(s,m,1000,'ewf-frozen-transition',1e-7)
    set_stage(s,m,2.5e-6,False,'frozen-growth-2p5us')
    batch(s,m,1000,'ewf-frozen-growth-first',2.5e-6)
    for steps in [10000]*7+[6580]:batch(s,m,steps,'ewf-frozen-growth',2.5e-6)
    assert m['verified_native_end']==89660 and math.isclose(m['blocks'][-1]['film_end_s'],0.195,abs_tol=1e-12)
    set_stage(s,m,2.5e-6,True,'final-bulk-active')
    batch(s,m,2000,'ewf-final-bulk-active',2.5e-6)
    assert m['verified_native_end']==91660 and math.isclose(m['blocks'][-1]['film_end_s'],0.2,abs_tol=1e-12)
    run.assert_bulk_active(s)
    m.update(status='EWF_COMPLETE',next_stage=None);run.dump(OUT/'2_6M-run.json',m)
    run.dump(OUT/'campaign-manifest.json',{'status':'EWF_COMPLETE','active_mesh':'2_6M','phase':'EWF_200MS','completed':['2_6M']})
    ready.update(status='EWF_COMPLETE',pair=m['latest_pair']);run.dump(OUT/'ewf-successor.json',ready)
    print('EWF_COMPLETE',91660,0.2,flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        run.dump(OUT/('ewf-successor-failure-'+str(time.time_ns())+'.json'),
                 {'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),
                  'no_blind_solve_retry':True,'never_exit_fluent':True})
        raise
