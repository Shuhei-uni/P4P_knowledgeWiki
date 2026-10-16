"""Preserve three existing Planv1 states; verify readback and restore final."""
import json,time,math
from pathlib import PureWindowsPath
from phase9_server6_60k_planv1_common import attach,run,OUT
from run_phase9_server6_slit_ewf import lane_file_sha256
from deploy_phase9_server6_slit_ewf import quote

def main():
 s=attach();run.require_idle(s);assert not s.settings.solution.run_calculation.iterating()
 m=json.loads((OUT/'host-run-manifest.json').read_text());assert m['status']=='COMPLETE_VERIFIED'
 final=m['latest_pair'];assert run.native_iteration(s)==50899 and math.isclose(run.film(s)['film_elapsed_time'],.2,abs_tol=1e-12)
 growth=next(x for x in m['blocks'] if x['stage']=='growth-to-195ms')['pair']
 folder=PureWindowsPath(growth['case']).parent
 stamp=PureWindowsPath(growth['case']).name.split('-')[-1].split('.')[0]
 freeze={'case':str(folder/('controls-frozen-transition-'+stamp+'.cas.h5')),'data':str(folder/('controls-frozen-transition-'+stamp+'.dat.h5')),'native_iteration':9582}
 entries=[('bulk-frozen-N9582-0p815ms',freeze,.000815,False),('195ms-N49899-bulk-frozen',growth,.195,False),('200ms-N50899-bulk-active',final,.2,True)]
 tag=str(time.time_ns());shared=run.SHARED/'P4P-Fluent-Artifacts/Phase9/Server6/60k'/('selected-checkpoints-20261015-'+tag)
 run.ensure_remote_directory(s,str(shared));receipt={'status':'COPY_AND_READBACK_IN_PROGRESS','shared_folder':str(shared),'checkpoints':[],'new_solve_calls':0}
 try:
  for label,pair,clock,active in entries:
   for k in ['case','data']:assert run.remote_file_exists(s,pair[k]),pair[k]
   hashes={k:lane_file_sha256(s,pair[k],str(folder/'scratch'/('selection-source-'+label+'-'+k+'-'+tag+'.txt'))) for k in ['case','data']}
   for k in ['case','data']:
    if k+'_sha256' in pair:assert hashes[k]==pair[k+'_sha256']
   run.load(s,pair)
   film=run.film(s);eq=s.settings.solution.controls.equations.get_state()
   assert run.native_iteration(s)==pair['native_iteration'] and math.isclose(film['film_elapsed_time'],clock,abs_tol=1e-12)
   assert all(v==active for v in eq.values())
   copied={}
   for k,ext in [('case','cas.h5'),('data','dat.h5')]:
    dest=str(shared/(label+'.'+ext));assert not run.remote_file_exists(s,dest)
    run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(pair[k])+' -Destination '+quote(dest))
    assert lane_file_sha256(s,dest,str(folder/'scratch'/('selection-copy-'+label+'-'+k+'-'+tag+'.txt')))==hashes[k]
    copied[k]=dest;copied[k+'_sha256']=hashes[k]
   receipt['checkpoints'].append({'label':label,'source_pair':pair,'shared_pair':copied,'film_time_s':clock,'native_iteration':pair['native_iteration'],'bulk_active':active,'reopened_readback_verified':True})
   run.dump(OUT/'selected-checkpoints.json',receipt)
   print('CHECKPOINT_SAVED',label,flush=True)
 finally:
  run.load(s,final)
  assert run.native_iteration(s)==50899 and math.isclose(run.film(s)['film_elapsed_time'],.2,abs_tol=1e-12)
  assert all(s.settings.solution.controls.equations.get_state().values())
  receipt['final_live_endpoint_restored']=True
  run.dump(OUT/'selected-checkpoints.json',receipt)
 receipt.update(status='THREE_PAIRS_VERIFIED_SAVED',cloud_upload_independently_verified=False)
 run.write_ascii_text_new(s,str(shared/'checkpoint-manifest.json'),json.dumps(receipt,indent=2)+'\n')
 run.dump(OUT/'selected-checkpoints.json',receipt)
 print('THREE_PAIRS_VERIFIED_SAVED',str(shared),flush=True)
if __name__=='__main__':main()
