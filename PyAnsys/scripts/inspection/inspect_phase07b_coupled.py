"""Capability audit, optionally probing Coupled/Off then restoring the saved pair."""
import sys, json, fcntl, signal
from pathlib import Path
from datetime import datetime, timezone
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'scripts/setup'))
from prepare_phase07b_collector import connect,remote_file_exists

out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
lock=(BASE/'output/phase07b-server1-controller.lock').open('a+')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('Read-only capability audit timed out')))
signal.alarm(120)
s=connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5)
assert not s.settings.solution.run_calculation.iterating()
prior=json.loads((BASE/'output/p7b-s40-t020-diag-resume-20260922T122811Z/manifest.json').read_text())
assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==5000
for k,v in prior['definitions'].items():assert s.settings.setup.named_expressions[k].definition()==v
assert all(remote_file_exists(s,prior['pairs']['final'].replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
r={'utc':datetime.now(timezone.utc).isoformat(),'version':str(s.get_fluent_version()),'iteration':5000,'preserved_pair':prior['pairs']['final'],'iterations_issued':0,'settings_changed':False}
for k,node in [('methods',s.settings.solution.methods),('controls',s.settings.solution.controls),('residual',s.settings.solution.monitor.residual),('multiphase',s.settings.setup.models.multiphase),('run_calculation',s.settings.solution.run_calculation)]:
 r[k]=node.get_state()
r['flow_scheme_allowed']=s.settings.solution.methods.p_v_coupling.flow_scheme.allowed_values()
r['pseudo_formulation_children']=s.settings.solution.methods.pseudo_time_method.formulation.child_names
try:r['coupled_pseudo_allowed']=s.settings.solution.methods.pseudo_time_method.formulation.coupled_solver.allowed_values()
except Exception as e:r['coupled_pseudo_inactive']=str(e)
r['status']='READ_ONLY_CAPABILITY_AUDIT_COMPLETE'
if '--probe-coupled-off' in sys.argv[2:]:
 r['status']='PROBING_COUPLED_OFF_NO_SOLVE'
 (out/'receipt.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 try:
  s.settings.solution.methods.p_v_coupling.flow_scheme='Coupled'
  r['activated_pseudo_allowed']=s.settings.solution.methods.pseudo_time_method.formulation.coupled_solver.allowed_values()
  assert 'off' in r['activated_pseudo_allowed']
  s.settings.solution.methods.pseudo_time_method.formulation.coupled_solver='off'
  r['activated_methods']=s.settings.solution.methods.get_state()
  r['activated_controls']=s.settings.solution.controls.get_state()
  r['activated_residual_options']=s.settings.solution.monitor.residual.options.get_state()
  r['control_children']=s.settings.solution.controls.child_names
  r['activated_iteration']=s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()
  assert r['activated_iteration']==5000
 finally:
  (out/'receipt.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
  signal.alarm(600)
  s.settings.file.read_case_data(file_name=prior['pairs']['final'])
  assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==5000
  assert s.settings.solution.methods.get_state()==r['methods']
  assert s.settings.solution.controls.get_state()==r['controls']
  r['restored_endpoint']=prior['pairs']['final']
  r['status']='COUPLED_OFF_PROBE_COMPLETE_ENDPOINT_RESTORED'
  r['settings_changed']=True
  r['persistent_scientific_change']=False
(out/'receipt.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
signal.alarm(0)
print(json.dumps({k:r[k] for k in ['version','iteration','flow_scheme_allowed','pseudo_formulation_children','status']}))
