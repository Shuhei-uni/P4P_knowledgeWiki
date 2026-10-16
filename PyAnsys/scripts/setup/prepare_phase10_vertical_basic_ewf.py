"""Preserve Server6 angle endpoint; inspect vertical N31000 before basic EWF build."""
from pathlib import Path, PureWindowsPath
import json,time
import run_phase10_server6_angle50ms as angle
from run_phase9_server6_slit_ewf import lane_save,lane_file_sha256
from deploy_phase9_server6_slit_ewf import quote
OUT=angle.ROOT/'output/phase10-proposed-design/20261012/vertical-basic-ewf-10us'

def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
    assert not (OUT/'vertical-parent-inspected.json').exists(),'Reconcile before repeating load'
    s,oldwork=angle.connect();angle.idle(s)
    assert angle.run.native_iteration(s)==33492
    assert abs(angle.run.film(s)['film_elapsed_time']-.05)<1e-10
    host=json.loads((angle.OUT/'host-launch.json').read_text())
    assert json.loads(angle.run.read_text(s,host['host_output']+'\\job-manifest.json'))['status']=='COMPLETE'
    snapshot=json.loads((OUT/'angle-settings.json').read_text())
    snapshot['report_definitions']=s.settings.solution.report_definitions.get_state()
    snapshot['report_files']=s.settings.solution.monitor.report_files.get_state()
    dump('angle-settings.json',snapshot)
    stamp=str(time.time_ns())
    preserved=lane_save(s,angle.run.WORK,'preserved-angle50-before-vertical-basic-'+stamp)
    dump('preparation-state.json',{'status':'ANGLE_PRESERVED_VERTICAL_LOAD_PENDING','preserved_pair':preserved})
    profile=PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")'))
    folder=profile/'Documents/FluentRuns/Phase9-Server6-slit154k/20261010/slit154k/ewf-200ms'
    pair={'native_iteration':31000}
    for k,ext in [('case','cas.h5'),('data','dat.h5')]:
        pair[k]=str(folder/('auto-31000-1-31000.'+ext))
        pair[k+'_sha256']=lane_file_sha256(s,pair[k],str(angle.run.WORK/'scratch'/('vertical-parent-'+k+'-'+stamp+'.txt')))
    # Load in the original working directory to retain the recorded UDF runtime.
    angle.run.WORK=oldwork
    angle.run.load(s,pair)
    hooks=s.settings.setup.user_defined.function_hooks
    state={'status':'VERTICAL_PARENT_INSPECTED','source_pair':pair,'preserved_angle_pair':preserved,
           'native_iteration':angle.run.native_iteration(s),'film':angle.run.film(s),
           'parameters':dict(s.rp_vars('wall-film/model-parameters')),
           'boundary_conditions':s.settings.setup.boundary_conditions.get_state(),
           'hooks':hooks.get_state() if hooks.is_active() else {},
           'equations':s.settings.solution.controls.equations.get_state(),
           'working_directory':str(oldwork),'new_solve_calls':0}
    dump('vertical-parent-inspected.json',state)
    print(json.dumps({k:state[k] for k in ['status','native_iteration','film','hooks','equations']},indent=2))
if __name__=='__main__':main()
