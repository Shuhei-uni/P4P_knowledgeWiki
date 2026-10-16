"""Human-selected 60k N8080 continuation on Server6 at fixed10us to200ms."""
from pathlib import Path, PureWindowsPath
import argparse, hashlib, json, math, os, time, traceback
from phase9_server6_slit_common import attach, run, ROOT
from run_phase9_server6_slit_ewf import lane_save, lane_file_sha256, lane_read_text, render_journal
from deploy_phase9_server6_slit_ewf import quote
from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.ewf_staged import FILM

OUT=ROOT/'output/phase9-server6-60k-10us/20261013'
OUT.mkdir(parents=True,exist_ok=True)
def dump(name,value):
    p=OUT/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(value,indent=2)+'\n');t.replace(p)
def connect():
    s=attach();previous=run.WORK
    run.WORK=PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")'))/'Documents/FluentRuns/Phase9-Server6-60k-10us/20261013'
    run.OUT=OUT
    run.ensure_remote_directory(s,str(run.WORK/'scratch'))
    return s,previous
def idle(s):
    run.require_idle(s)
    assert not s.settings.solution.run_calculation.iterating()
def prepare():
    assert not (OUT/'prepared.json').exists(),'Reconcile before repeating preparation'
    s,old=connect();idle(s)
    pre=json.loads((OUT/'preflight.json').read_text())
    assert pre['idle'] and not pre['host']['controllers']
    preserved=lane_save(s,run.WORK,'preserved-server6-before-60k')
    dump('preparation-state.json',{'status':'PREVIOUS_PRESERVED','pair':preserved})
    expected=json.loads((ROOT/'output/phase9-mesh-convergence/20261007/60k-final-selection-N8080.json').read_text())['selected_pair']
    pair={'native_iteration':8080}
    for k,ext in [('case','cas.h5'),('data','dat.h5')]:
        source=next(f['FullName'] for f in pre['host']['parents'] if f['FullName'].endswith('.'+ext))
        actual=lane_file_sha256(s,source,str(run.WORK/'scratch'/('parent-'+k+'.txt')))
        assert actual==expected[k+'_sha256'],'Parent hash differs'
        dest=str(run.WORK/('parent-N8080.'+ext))
        assert not run.remote_file_exists(s,dest)
        run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(source)+' -Destination '+quote(dest))
        assert lane_file_sha256(s,dest,str(run.WORK/'scratch'/('copied-'+k+'.txt')))==actual
        pair[k]=dest;pair[k+'_sha256']=actual
    run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(old/'libcontactv2')+' -Destination '+quote(run.WORK/'libcontactv2')+' -Recurse')
    run.load(s,pair)
    clock=run.film(s)['film_elapsed_time'];assert math.isclose(clock,.00065,abs_tol=1e-12)
    original=dict(s.rp_vars('wall-film/model-parameters'))
    equations=s.settings.solution.controls.equations.get_state()
    assert all(equations.values())
    s.rp_vars('wall-film/model-parameters',[(k,1e-5 if k=='timestep-max' else v) for k,v in original.items()])
    params=dict(s.rp_vars('wall-film/model-parameters'))
    assert params==dict(original,**{'timestep-max':1e-5})
    controls=lane_save(s,run.WORK,'activated-10us-N8080');run.load(s,controls)
    assert dict(s.rp_vars('wall-film/model-parameters'))==params
    assert run.native_iteration(s)==8080 and math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12)
    monitors=run.WORK/'monitors';run.ensure_remote_directory(s,str(monitors))
    files=s.settings.solution.monitor.report_files
    for n,v in files.get_state().items():files[n].file_name=str(monitors/(n+'.out'))
    auto=s.settings.file.auto_save;auto.case_frequency='each-time';auto.root_name=str(run.WORK/'auto-%i');auto.data_frequency=1000;auto.retain_most_recent_files=False
    # Prevent residual convergence from ending a requested fixed solve early.
    residual=s.settings.solution.monitor.residual
    for n in residual.equations.get_object_names():residual.equations[n].check_convergence=False
    prepared=lane_save(s,run.WORK,'prepared-10us-N8080');run.load(s,prepared)
    # Data reload can rename reports; use the final live paths.
    for n,v in files.get_state().items():files[n].file_name=str(monitors/(n+'.out'))
    dump('prepared.json',{'status':'PREPARED_REOPEN_VERIFIED','parent':pair,'prepared_pair':prepared,'previous_pair':preserved,'parameters':params,'parent_parameters':original,'film':run.film(s),'equations':equations,'work':str(run.WORK),'target_film_s':.2,'remaining_updates':19935,'target_native_iteration':28015,'report_files':files.get_state(),'physics_changes':[],'new_solve_calls':0})
    print('PREPARED_60K_10US',flush=True)
def solve():
    assert not (OUT/'run-manifest.json').exists(),'Reconcile existing command; never replay'
    p=json.loads((OUT/'prepared.json').read_text());s,_=connect();idle(s)
    assert run.native_iteration(s)==8080 and math.isclose(run.film(s)['film_elapsed_time'],.00065,abs_tol=1e-12)
    assert dict(s.rp_vars('wall-film/model-parameters'))==p['parameters']
    assert s.settings.solution.controls.equations.get_state()==p['equations']
    m=dict(p,status='RUNNING',controller_pid=os.getpid(),blocks=[]);dump('run-manifest.json',m)
    try:
        # One update proves the effective native step; it counts toward the horizon.
        for label,count in [('smoke-10us',1),('fixed-10us-to200ms',19934)]:
            idle(s);start=run.native_iteration(s);clock=run.film(s)['film_elapsed_time']
            journal=render_journal(run.WORK,label,count);remote=str(run.WORK/(label+'.jou'));trn=str(run.WORK/(label+'.trn'))
            run.write_ascii_text_new(s,remote,journal)
            m.update(active_stage=label,active_target=start+count,active_transcript=trn);dump('run-manifest.json',m)
            s.scheme.eval('(ti-menu-load-string "'+quote_scheme_string('/file/read-journal "'+remote.replace('\\','/')+'"')+'")')
            end=run.native_iteration(s);film=run.film(s)
            assert end==start+count,'Native solve ended early; do not replay'
            assert math.isclose(film['film_elapsed_time'],clock+count*1e-5,abs_tol=1e-10),'Effective step differs'
            if label.startswith('smoke'):
                rows=[tuple(map(float,x.groups())) for x in FILM.finditer(lane_read_text(s,trn))]
                assert rows and math.isclose(rows[-1][1],1e-5,abs_tol=1e-12),'Native timestep unconfirmed'
            pair={'case':str(run.WORK/(label+'.cas.h5')),'data':str(run.WORK/(label+'.dat.h5')),'native_iteration':end}
            for k in ['case','data']:pair[k+'_sha256']=lane_file_sha256(s,pair[k],str(run.WORK/'scratch'/(label+'-'+k+'.txt')))
            m['blocks'].append({'label':label,'updates':count,'film':film,'pair':pair})
            m.update(accepted_film_s=film['film_elapsed_time'],verified_native_end=end,latest_pair=pair);dump('run-manifest.json',m)
        run.load(s,m['latest_pair']);assert run.native_iteration(s)==28015
        assert math.isclose(run.film(s)['film_elapsed_time'],.2,abs_tol=1e-10)
        assert s.settings.solution.controls.equations.get_state()==p['equations']
        shared=run.SHARED/'P4P-Fluent-Artifacts/Phase9/ewf-development-final/server6-60k-10us-20261013'
        run.ensure_remote_directory(s,str(shared));copied={}
        for k,ext in [('case','cas.h5'),('data','dat.h5')]:
            dest=str(shared/('final-200ms-N28015.'+ext));assert not run.remote_file_exists(s,dest)
            run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(m['latest_pair'][k])+' -Destination '+quote(dest))
            assert lane_file_sha256(s,dest,str(run.WORK/'scratch'/('final-shared-'+k+'.txt')))==m['latest_pair'][k+'_sha256'];copied[k]=dest
        m.update(status='COMPLETE_200MS_REOPEN_VERIFIED',shared_pair=copied,active_stage=None,fluent_left_open=True);dump('run-manifest.json',m)
    except BaseException:
        m.update(status='RECOVERY_REQUIRED',error=traceback.format_exc());dump('run-manifest.json',m);raise
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--prepare',action='store_true');p=a.parse_args()
    prepare() if p.prepare else solve()
