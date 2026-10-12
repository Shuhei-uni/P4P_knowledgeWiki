"""Retain the explicitly selected 50.9 ms autosave; never solve."""
import json,time,math
from pathlib import PureWindowsPath
from phase9_server6_slit_common import attach,run,OUT
from run_phase9_server6_slit_ewf import lane_file_sha256
from deploy_phase9_server6_slit_ewf import quote

def main():
 d=json.loads((OUT/'pause50-preservation.json').read_text());assert d['status']=='PAUSED_IDLE_ENDPOINT_AND_CANDIDATES_PRESERVED'
 s=attach();run.require_idle(s);assert not s.settings.solution.run_calculation.iterating()
 assert run.native_iteration(s)==d['native_iteration'] and math.isclose(run.film(s)['film_elapsed_time'],d['film']['film_elapsed_time'],abs_tol=1e-12)
 pair=next(x for x in d['candidates'] if x['native_iteration']==84000);tag=str(time.time_ns());folder=run.WORK/'slit154k/ewf-200ms'
 for key in ['case','data']:
  assert lane_file_sha256(s,pair[key],str(folder/'scratch'/f'retain50p9-{key}-{tag}.txt'))==pair[key+'_sha256']
 run.load(s,pair);film=run.film(s)
 assert run.native_iteration(s)==84000 and math.isclose(film['film_elapsed_time'],.0509,abs_tol=1e-10)
 assert math.isclose(film['film_timestep'],2.5e-6,abs_tol=1e-14)
 assert not s.settings.solution.run_calculation.iterating()
 shared=run.SHARED/'P4P-Fluent-Artifacts/Phase9/Server6/slit154k'/f'retained-50p9ms-N84000-{tag}'
 run.ensure_remote_directory(s,str(shared));shared_pair={}
 for key in ['case','data']:
  target=str(shared/PureWindowsPath(pair[key]).name);assert not run.remote_file_exists(s,target)
  run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(pair[key])+' -Destination '+quote(target))
  h=lane_file_sha256(s,target,str(folder/'scratch'/f'retain50p9-shared-{key}-{tag}.txt'));assert h==pair[key+'_sha256']
  shared_pair[key]=target;shared_pair[key+'_sha256']=h
 receipt={'status':'RETAINED_50P9MS_REOPEN_VERIFIED','native_iteration':84000,'film':film,'pair':pair,'shared_pair':shared_pair,'cloud_upload_independently_verified':False,'reopen_verified':True,'new_solve_calls':0,'fluent_preserved':True,'campaign_paused':True,'angle_transition_disabled':True,'superseded_endpoint_preserved':d['pair']}
 run.dump(OUT/'retained-50p9ms.json',receipt)
 launch=json.loads((OUT/'host-launch.json').read_text());m=json.loads(run.read_text(s,launch['run_manifest']));m.update(status='PAUSED_BY_HUMAN',retained_endpoint=receipt,active_stage=None,active_target=None,human_selected_retained_film_s=.0509,automatic_angle_transition=False)
 stage=run.WORK/f'retained50p9-manifest-{tag}.json';run.write_ascii_text_new(s,str(stage),json.dumps(m,indent=2)+'\n')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(stage)+' -Destination '+quote(launch['run_manifest'])+' -Force');run.dump(OUT/'host-run-manifest.json',m)
 print('RETAINED_50P9MS_REOPEN_VERIFIED',flush=True)
if __name__=='__main__':main()
