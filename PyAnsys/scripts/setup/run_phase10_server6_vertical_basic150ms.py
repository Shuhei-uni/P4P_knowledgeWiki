"""Continue the verified vertical basic-EWF endpoint by100ms:50->150ms,10us."""
from pathlib import Path, PureWindowsPath
import argparse, json, math, os, time, traceback
from phase9_server6_slit_common import attach, run, ROOT
from run_phase9_server6_slit_ewf import lane_save, lane_file_sha256, lane_read_text, render_journal
from deploy_phase9_server6_slit_ewf import quote
from pyansys_fluent.stage4_native import exclusive_writer_lock
from pyansys_fluent.ewf_staged import FILM

OUT = ROOT/'output/phase10-proposed-design/20261013/vertical-basic-ewf-to150ms'
OUT.mkdir(parents=True, exist_ok=True)


def dump(name, value):
    p=OUT/name;tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(p)

def connect():
    s=attach()
    previous_work=run.WORK
    profile=PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")'))
    run.WORK=profile/'Documents/FluentRuns/Phase10-Server6-vertical-basic-ewf/20261012'
    run.OUT=OUT
    return s,previous_work

def idle(s):
    if s.settings.setup.cell_zone_conditions.is_active():
        run.require_idle(s)
        assert not s.settings.solution.run_calculation.iterating()

def parameters(s, dt):
    original=dict(s.rp_vars('wall-film/model-parameters'))
    assert 'timestep-max' in original
    s.rp_vars('wall-film/model-parameters',[(k,dt if k=='timestep-max' else v) for k,v in original.items()])
    actual=dict(s.rp_vars('wall-film/model-parameters'))
    assert all(actual[k]==(dt if k=='timestep-max' else v) for k,v in original.items())
    return actual

def route_monitors(s):
    # The paused pair came from another Windows account. Keep all histories on
    # this Fluent host; no numerical setting or threshold changes here.
    run.ensure_remote_directory(s,str(run.WORK/'monitors-to150ms-20261013'))
    files=s.settings.solution.monitor.report_files
    for name,value in files.get_state().items():
        files[name].file_name=str(run.WORK/'monitors-to150ms-20261013'/(name+'.out'))
    return files.get_state()

def wall_audit(s):
    expected=json.loads((OUT/'angle-settings.json').read_text())['boundary_conditions']['wall']
    actual=s.settings.setup.boundary_conditions.wall.get_state()
    mapping={'verticalslit-wall-vertical-slit':'angled-slit-wall-simple-spiral-separator--brine-outlet-'}
    checks={}
    for name,value in actual.items():
        target=expected[mapping.get(name,name)]['phase']['mixture']
        current=value['phase']['mixture']
        checks[name]={key:current[key]==target[key] for key in ['wall_film','turbulence','discrete_phase']}
    assert all(all(v.values()) for v in checks.values()),checks
    assert float(s.settings.setup.named_expressions['P72dEnabled'].get_value())==0
    return checks

def prepare():
    assert not (OUT/'prepared.json').exists(),'Reconcile existing child before repeating preparation'
    preflight=json.loads((OUT/'preflight-reconciliation.json').read_text())
    assert preflight['status']=='IDLE_NATIVE_AND_HOST_RECONCILED'
    s,_=connect();idle(s)
    assert run.native_iteration(s)==34661
    clock=run.film(s)['film_elapsed_time'];assert abs(clock-.05)<1e-10
    assert dict(s.rp_vars('wall-film/model-parameters'))==preflight['parameters']
    wall_audit(s);assert s.settings.solution.controls.equations.get_state()==preflight['bulk_equations']
    stamp=str(time.time_ns())
    # Unique preservation pair; the already shared50ms checkpoint remains unchanged.
    preserved=lane_save(s,run.WORK,'preserved-50ms-before-to150-'+stamp)
    dump('preparation-state.json',{'status':'50MS_PRESERVED_TIMESTEP_CHANGE_PENDING','pair':preserved})
    params=parameters(s,1e-5)
    active=lane_save(s,run.WORK,'activated-10us-to150-N34661-'+stamp);run.load(s,active)
    assert run.native_iteration(s)==34661 and abs(run.film(s)['film_elapsed_time']-clock)<1e-10
    assert dict(s.rp_vars('wall-film/model-parameters'))==params
    checks=wall_audit(s);assert s.settings.solution.controls.equations.get_state()==preflight['bulk_equations']
    autosave=s.settings.file.auto_save
    autosave.case_frequency='each-time';autosave.root_name=str(run.WORK/'to150-auto-%i')
    autosave.data_frequency=1000;autosave.retain_most_recent_files=False
    record={'status':'PREPARED_REOPEN_VERIFIED','server_id':'6','mesh_cells':154063,
      'source_pair':preflight['source_pair'],'preserved_pair':preserved,'activated_pair':active,
      'film':run.film(s),'parameters':params,'bulk_equations':preflight['bulk_equations'],
      'wall_checks':checks,'host_work':str(run.WORK),'parent_native_iteration':34661,
      'parent_film_s':clock,'schedule':[['ten-us-to150ms',10000,1e-5]],
      'target_film_s':.15,'target_native_iteration':44661,'numerical_thresholds':None,
      'never_exit_fluent':True,'new_solve_calls':0,'continuation_updates':10000,
      'unchanged_ewf_physics':True,'bulk_frozen':True,'drain_probe_reused_from':'20261012/vertical-basic-ewf-10us/smoke-proof.json'}
    dump('prepared.json',record)
    dump('run-manifest.json',dict(record,status='READY',verified_native_end=34661,accepted_film_s=clock,blocks=[]))
    print('VERTICAL_BASIC_TO150_10US_PREPARED_REOPEN_VERIFIED',flush=True)

def solve():
    with exclusive_writer_lock(OUT/'controller.lock'):
        m=json.loads((OUT/'run-manifest.json').read_text())
        assert m['status']=='READY', 'Existing command must be reconciled; no replay'
        s,_=connect();idle(s)
        assert run.native_iteration(s)==m['parent_native_iteration'] and math.isclose(run.film(s)['film_elapsed_time'],m['parent_film_s'],abs_tol=1e-10)
        assert dict(s.rp_vars('wall-film/model-parameters'))==m['parameters']
        wall_audit(s)
        m.update(status='RUNNING',controller_pid=os.getpid());dump('run-manifest.json',m)
        try:
            for label,count,dt in m['schedule']:
                idle(s);start=run.native_iteration(s);clock=m['accepted_film_s'];stamp=str(time.time_ns())
                assert start==m['verified_native_end']
                if dict(s.rp_vars('wall-film/model-parameters'))['timestep-max']!=dt:
                    params=parameters(s,dt)
                    active=lane_save(s,run.WORK,'activated-final-endpoint-'+stamp);run.load(s,active)
                    assert dict(s.rp_vars('wall-film/model-parameters'))==params
                    assert run.native_iteration(s)==start and math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-10)
                basename=label+'-N'+str(start+count)+'-'+stamp
                m['report_files']=route_monitors(s)
                remote=str(run.WORK/(basename+'.jou'));transcript=str(run.WORK/(basename+'.trn'))
                journal=render_journal(run.WORK,basename,count)
                run.write_ascii_text_new(s,remote,journal)
                m.update(active_stage=label,active_target=start+count,active_step_s=dt,active_journal=remote,active_transcript=transcript)
                dump('run-manifest.json',m)
                print('BATCH',label,start,start+count,dt,flush=True)
                from pyansys_fluent.common import quote_scheme_string
                s.scheme.eval('(ti-menu-load-string "'+quote_scheme_string('/file/read-journal "'+remote.replace('\\','/')+'"')+'")')
                end=run.native_iteration(s)
                # Preserve any partial endpoint before reporting a technical stop.
                if end!=start+count:
                    partial=lane_save(s,run.WORK,'interrupted-N'+str(end)+'-'+stamp)
                    m.update(partial_pair=partial,partial_film=run.film(s));dump('run-manifest.json',m)
                    raise RuntimeError('Native command ended early; partial preserved, do not replay')
                text=lane_read_text(s,transcript);rows=[list(map(float,x.groups())) for x in FILM.finditer(text)]
                pair={'native_iteration':end,'case':str(run.WORK/(basename+'.cas.h5')),'data':str(run.WORK/(basename+'.dat.h5'))}
                for key in ['case','data']:pair[key+'_sha256']=lane_file_sha256(s,pair[key],str(run.WORK/'scratch'/(basename+'-'+key+'.txt')))
                run.load(s,pair);film=run.film(s)
                wall_audit(s)
                assert s.settings.solution.controls.equations.get_state()==m['bulk_equations']
                expected_params=dict(m['parameters']);expected_params['timestep-max']=dt
                assert dict(s.rp_vars('wall-film/model-parameters'))==expected_params
                target=clock+count*dt
                assert math.isclose(film['film_elapsed_time'],target,abs_tol=1e-10), 'Target clock unconfirmed; no replay'
                block={'label':label,'updates':count,'native_end':end,'film_end_s':target,'step_s':dt,'pair':pair,
                       'transcript':transcript,'film_rows_observed':len(rows),
                       'peak_courant_diagnostic':max((row[2] for row in rows),default=None)}
                m['blocks'].append(block)
                m.update(verified_native_end=end,accepted_film_s=target,latest_pair=pair,active_target=None)
                dump('run-manifest.json',m)
            assert run.native_iteration(s)==m['target_native_iteration'] and math.isclose(run.film(s)['film_elapsed_time'],m['target_film_s'],abs_tol=1e-10)
            shared=run.SHARED/'P4P-Fluent-Artifacts/Phase10/proposed-design/vertical-slit-basic-ewf-10us'/('final-150ms-N'+str(m['target_native_iteration'])+'-'+str(time.time_ns()))
            run.ensure_remote_directory(s,str(shared));copied={}
            for key in ['case','data']:
                dest=str(shared/('final-150ms-N'+str(m['target_native_iteration'])+'.'+('cas.h5' if key=='case' else 'dat.h5')))
                run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(m['latest_pair'][key])+' -Destination '+quote(dest))
                h=lane_file_sha256(s,dest,str(run.WORK/'scratch'/('shared-'+key+'-'+str(time.time_ns())+'.txt')))
                assert h==m['latest_pair'][key+'_sha256'];copied[key]=dest;copied[key+'_sha256']=h
            m.update(status='COMPLETE_150MS_REOPEN_VERIFIED',active_stage=None,active_target=None,shared_pair=copied,
                     final_film=run.film(s),fluent_left_open=True,cloud_upload_independently_verified=False)
            dump('run-manifest.json',m);print('COMPLETE_150MS_REOPEN_VERIFIED',flush=True)
        except BaseException:
            m.update(status='RECOVERY_REQUIRED',error=traceback.format_exc(),never_exit_fluent=True)
            dump('run-manifest.json',m)
            raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');a=p.parse_args()
    prepare() if a.prepare else solve()
