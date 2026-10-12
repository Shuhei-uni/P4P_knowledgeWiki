"""Preserve the idle interrupted endpoint and saved candidates; no solve/load."""
import json,time
from phase9_server6_slit_common import attach,run,OUT
from run_phase9_server6_slit_ewf import lane_save,lane_file_sha256
from deploy_phase9_server6_slit_ewf import quote

def main():
 s=attach();run.require_idle(s);assert not s.settings.solution.run_calculation.iterating()
 launch=json.loads((OUT/'host-launch.json').read_text());tag=str(time.time_ns());folder=run.WORK/'slit154k/ewf-200ms'
 native=run.native_iteration(s)
 first=lane_save(s,folder,f'pause50-interrupted-first-N{native}-{tag}')
 clock=run.film(s)['film_elapsed_time'];time.sleep(2)
 assert run.native_iteration(s)==native and abs(run.film(s)['film_elapsed_time']-clock)<1e-12
 pair=lane_save(s,folder,f'pause50-interrupted-stable-N{native}-{tag}')
 assert run.native_iteration(s)==native and abs(run.film(s)['film_elapsed_time']-clock)<1e-12
 if s.settings.file.stop_transcript.is_active():s.settings.file.stop_transcript()
 candidates=[]
 for n,age in [(83000,.0484),(84000,.0509)]:
  item={'native_iteration':n,'expected_film_s_from_schedule':age,'clock_reopen_verified':False}
  for key,suffix in [('case','cas.h5'),('data','dat.h5')]:
   source=str(folder/f'auto-{n}-1-{n}.{suffix}')
   target=str(folder/f'retained-pause50-candidate-N{n}-{tag}.{suffix}')
   assert run.remote_file_exists(s,source) and not run.remote_file_exists(s,target)
   run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(source)+' -Destination '+quote(target))
   source_hash=lane_file_sha256(s,source,str(folder/'scratch'/f'pause50-source-{n}-{key}-{tag}.txt'))
   assert source_hash==lane_file_sha256(s,target,str(folder/'scratch'/f'pause50-copy-{n}-{key}-{tag}.txt'))
   item[key]=target;item[key+'_sha256']=source_hash
  candidates.append(item)
 receipt={'status':'PAUSED_IDLE_ENDPOINT_AND_CANDIDATES_PRESERVED','native_iteration':native,'film':run.film(s),'pair':pair,'first_pair':first,'candidates':candidates,'no_solve':True,'never_exit_fluent':True,'automatic_angle_transition':False}
 run.dump(OUT/'pause50-preservation.json',receipt)
 # Preserve the failed host manifest; mark selected lane paused without discarding failure.
 m=json.loads(run.read_text(s,launch['run_manifest']));backup=run.WORK/f'pause50-manifest-before-{tag}.json'
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(launch['run_manifest'])+' -Destination '+quote(backup))
 m.update(status='PAUSED_BY_HUMAN',human_pause_authority='Keep at50ms; no further100ms/angle continuation',pause50_preservation=receipt)
 stage=run.WORK/f'pause50-manifest-{tag}.json';run.write_ascii_text_new(s,str(stage),json.dumps(m,indent=2)+'\n')
 run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(stage)+' -Destination '+quote(launch['run_manifest'])+' -Force')
 run.dump(OUT/'host-run-manifest.json',m)
 print('PAUSED_PRESERVED',native,clock,flush=True)
if __name__=='__main__':main()
