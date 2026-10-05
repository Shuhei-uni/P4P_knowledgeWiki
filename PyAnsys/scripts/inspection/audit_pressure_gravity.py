"""Extract native N1/N0 pressure/density auxiliary state without solving; restore N1."""
from pathlib import Path
import sys,json,signal,fcntl,os
from datetime import datetime,timezone
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'setup'))
from build_reconstructed_interface import connect,assert_contract,remote_file_exists,ZONE,BASE
out=BASE/'output/pressure-gravity-audit';out.mkdir(exist_ok=True)
r={'status':'AUDITING','started_at_utc':datetime.now(timezone.utc).isoformat(),'solves_issued':0,'pid':os.getpid(),'stages':{}}
def persist():(out/'audit.json').write_text(json.dumps(r,indent=2)+'\n')
persist();signal.alarm(480)
lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
s=None;terminal=None
try:
 s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating();assert_contract(s)
 rp=Path(json.loads((BASE/'output/discrete-interface-initialization/n500-receipt.json').read_text())['run_manifest']);prev=json.loads(rp.read_text());build=json.loads(Path(prev['build']).read_text());terminal=prev['case'];assert all(remote_file_exists(s,terminal.replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
 r.update(terminal_parent=terminal,fresh_parent=build['case'],operating=s.settings.setup.general.operating_conditions.get_state(),implicit_body_force=s.settings.setup.models.multiphase.advanced_formulation.implicit_body_force());persist()
 for tag,case in [('N1',None),('N0',build['case'])]:
  if case:s.settings.file.read_case_data(file_name=case)
  assert_contract(s);d={};stage={'iteration':s.settings.setup.named_expressions['P9Iteration'].get_value(),'variables':{},'errors':{}}
  for ph,vs in [('mixture',['SV_CENTROID','SV_VOLUME','SV_P','SV_P_G','SV_DENSITY','SV_BF_V','SV_BFP_V','SV_U','SV_V','SV_W']),('phase-1',['SV_DENSITY']),('phase-2',['SV_DENSITY','SV_VOF'])]:
   available=s.fields.solution_variable_info.get_variables_info(zone_names=[ZONE],domain_name=ph).solution_variables
   for name in vs:
    key=ph+'_'+name
    if name not in available:stage['errors'][key]='not allocated';continue
    try:
     a=np.asarray(s.fields.solution_variable_data.get_data(variable_name=name,zone_names=[ZONE],domain_name=ph)[ZONE]);d[key]=a;stage['variables'][key]={'shape':list(a.shape),'finite':bool(np.isfinite(a).all()),'min':float(a.min()),'max':float(a.max())}
    except Exception as e:stage['errors'][key]=repr(e)
  np.savez_compressed(out/(tag+'-native.npz'),**d)
  alpha=d['phase-2_SV_VOF'];rho=d['mixture_SV_DENSITY'];pred=(1-alpha)*d['phase-1_SV_DENSITY']+alpha*d['phase-2_SV_DENSITY'];stage['mixture_density_minus_vof_mix_max_abs']=float(np.max(abs(rho-pred)))
  if 'mixture_SV_P_G' in d:
   grad=d['mixture_SV_P_G'].reshape(-1,3);y=d['mixture_SV_CENTROID'].reshape(-1,3)[:,1]
   stage['gradient_band_statistics']={label:{'count':int(mask.sum()),'component_min':grad[mask].min(axis=0).tolist(),'component_max':grad[mask].max(axis=0).tolist(),'component_mean':grad[mask].mean(axis=0).tolist()} for label,mask in [('bulk_vapor',y>.3),('bulk_liquid',y<-.1),('interface',abs(y-.1)<.1)]}
  r['stages'][tag]=stage;persist();print('EXTRACTED',tag,flush=True)
 r['status']='AUDIT_COMPLETE'
except Exception as e:r.update(status='AUDIT_REPAIR_REQUIRED',error=repr(e));raise
finally:
 if s is not None and terminal:
  try:
   assert not s.settings.solution.run_calculation.iterating();s.settings.file.read_case_data(file_name=terminal);assert_contract(s);r['restored_iteration']=s.settings.setup.named_expressions['P9Iteration'].get_value();r['terminal_restored']=r['restored_iteration']==1
  except Exception as e:r['restore_error']=repr(e);r['status']='AUDIT_REPAIR_REQUIRED'
 r['finished_at_utc']=datetime.now(timezone.utc).isoformat();persist();signal.alarm(0)
