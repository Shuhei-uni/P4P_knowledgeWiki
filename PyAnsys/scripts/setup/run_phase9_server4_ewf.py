"""Server 4-only native EWF adjustment; next transition is a verified boundary."""
from pathlib import Path, PureWindowsPath
import sys, json, time, argparse, fcntl, traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
from pyansys_fluent import ewf_local_drain as drain

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--live-transcript',required=True)
    args=parser.parse_args()
    out=run.OUT
    lock=(out/'controller.lock').open('a+')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    tag=str(time.time_ns());evidence=out/('ewf-adjustment-'+tag);evidence.mkdir()
    previous=json.loads((out/'2_6M-run.json').read_text())
    run.dump(evidence/'original-preparation-run.json',previous)
    paths=json.loads((out/'server4-paths.json').read_text())
    for key,name in [('work','WORK'),('shared','SHARED'),('parent','PARENT'),('mesh_folder','MESH_FOLDER'),('host_python','HOST_PYTHON')]:setattr(run,name,PureWindowsPath(paths[key]))
    prepared=json.loads((out/'ewf-settings-current.json').read_text())
    assert prepared['status']=='SETTINGS_APPLIED_REOPEN_VERIFIED'
    m={'status':'PREFLIGHT','label':'2_6M','cells':2596657,'verified_native_end':8580,
       'latest_pair':prepared['pair'],'report_paths':previous['report_paths'],
       'blocks':[{'stage':'prepared-ewf-origin','end':8580,'film_end_s':0.0007}],
       'phase':'EWF_200MS','next_stage':'bulk-active-adjustment','all_bulk_equations_active':True,
       'stage_iterations':2500,'final_target_film_age_s':0.2,'evidence':str(evidence)}
    run.dump(evidence/'review.json',{'server':'4','starting_pair':prepared['pair'],
        'sequence':['exclusive lock','idle N8580 and saved settings readback','local monitor/autosave paths',
                    'native transcript start','one TUI solve 2500','terminal/clock validation','paired local save/hash/reopen'],
        'no_other_attach_helpers_called':True,'solve':'/solve/iterate 2500'})
    s=run.attach();run.require_idle(s)
    assert run.native_iteration(s)==8580
    for key in ['case','data']:assert run.remote_file_exists(s,prepared['pair'][key])
    run.require_bulk_audit(s);run.assert_bulk_active(s);run.read_feed(s,1.0)
    actual=dict(s.rp_vars('wall-film/model-parameters'))
    assert all(actual[k]==v for k,v in prepared['changes'].items())
    drain.audit(s,True)
    for name in ['wall','wall:004']:
        w=s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film.get_state()
        assert w['eulerian_film_wall'] and not w['enable_flow_momentum_coupling']
    print('PREFLIGHT_PASS_SERVER4_N8580',flush=True)
    folder=run.WORK/'2_6M'/'ewf-200ms'
    run.ensure_remote_directory(s,str(folder/'monitors'))
    expressions=s.settings.solution.report_definitions.single_valued_expression
    files=s.settings.solution.monitor.report_files
    for name,value in [('p72d-drain-rate','P72dRemoval'),('p72d-lower-inventory','P72dInventory')]:
        if name not in expressions.get_object_names():expressions.create(name=name)
        expressions[name].definition=value;expressions[name].average_over=1
        if name not in files.get_object_names():files.create(name=name)
        target=str(folder/'monitors'/(name+'.out'))
        files[name].set_state({'report_defs':[name],'file_name':target,'frequency':1,
                              'active':True})
        m['report_paths'][name]=target
    autosave=s.settings.file.auto_save
    autosave.case_frequency='each-time';autosave.root_name=str(folder/'auto-%i')
    autosave.retain_most_recent_files=False;autosave.data_frequency=500
    s.transcript.start(file_name=args.live_transcript,write_to_stdout=False)
    run.dump(out/'2_6M-run.json',m)
    run.dump(out/'campaign-manifest.json',{'status':'EWF_RUNNING','active_mesh':'2_6M','phase':'EWF_200MS','completed':[]})
    try:
        record=run.batch(s,m,2500,'ewf-bulk-active-adjustment')
        m.update(status='EWF_ADJUSTMENT_COMPLETE',next_stage='frozen-transition-1000-at-0p1us')
        run.dump(out/'2_6M-run.json',m)
        run.dump(out/'ewf-adjustment-current.json',{'status':'EWF_ADJUSTMENT_COMPLETE','block':record,'next_stage':m['next_stage']})
        run.dump(out/'campaign-manifest.json',{'status':'EWF_ADJUSTMENT_COMPLETE','active_mesh':'2_6M','phase':'EWF_200MS','completed':[]})
        print('EWF_ADJUSTMENT_COMPLETE',11080,flush=True)
    except BaseException as exc:
        run.dump(evidence/'failure.json',{'error_type':type(exc).__name__,'error':str(exc),
                                          'traceback':traceback.format_exc(),'active_target':m.get('active_target')})
        raise

if __name__=='__main__':main()
