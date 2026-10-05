"""Build zero-feed hydrostatic control; never iterate."""
from build_steady_vof_simple import *
from build_steady_vof_simple import assert_contract as flow_contract

def assert_contract(s):
 flow_contract(s,inlet_velocity=0.)

def main():
 tag='hydrostatic-k9-simple-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 out=BASE/'output/steady-vof-hydrostatic'/tag;out.mkdir(parents=True)
 r={'status':'BUILDING','tag':tag,'height':.1,'iterations_issued':0,'case':ROOT+'/case-data/'+tag+'-n00000.cas.h5','out':str(out)}
 def persist():(out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('Build deadline')));signal.alarm(600);persist()
 try:
  s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating()
  prior=Path(json.loads((BASE/'output/steady-vof-solver-method/low-start-n1000-receipt.json').read_text())['run_manifest']);prev=json.loads(prior.read_text())
  assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==1000
  flow_contract(s)
  assert all(remote_file_exists(s,prev['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  r['preserved_endpoint']=prev['case'];parent_path=Path(prev['build']);parent=json.loads(parent_path.read_text())
  r['configuration_parent_manifest']=str(parent_path);r['configuration_parent_case']=parent['case']
  s.settings.file.read_case_data(file_name=parent['case']);assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==0
  flow_contract(s);old=snapshot(s)
  for inlet in ['liquid-inlet','steam-inlet']:s.settings.setup.boundary_conditions.velocity_inlet[inlet].phase['mixture'].momentum.velocity_magnitude.value=0.
  assert_contract(s);r['controlled_delta']={'inlet_velocity_m_s':{'liquid-inlet':0,'steam-inlet':0}}
  for n in s.settings.solution.monitor.report_files.get_object_names():s.settings.solution.monitor.report_files[n].active=False
  r['reports']=parent['reports'];r['initialization']=initialize(s,.1,out)
  a=np.load(out/'initial-fields.npz');b=np.load(parent_path.parent/'initial-fields.npz');assert all(np.array_equal(a[k],b[k]) for k in a.files)
  r['initial_fields_identical_to_flow_N0']=True;r['before']=snapshot(s)
  # No physical/numerical changes beyond the declared inlet velocity controls.
  for key in ['solver','operating','models','materials','zones','methods','controls']:
   assert old[key]==r['before'][key],key
  before_bc=copy.deepcopy(old['boundaries']);after_bc=copy.deepcopy(r['before']['boundaries'])
  for inlet in ['liquid-inlet','steam-inlet']:
   before_bc['velocity_inlet'][inlet]['phase']['mixture']['momentum']['velocity_magnitude']['value']=0.
  assert before_bc==after_bc,'Unexpected boundary change'
  s.settings.file.write_case_data(file_name=r['case']);assert all(remote_file_exists(s,r['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  s.settings.file.read_case_data(file_name=r['case']);assert_contract(s);r['after']=snapshot(s)
  for key in ['solver','operating','models','materials','boundaries','zones','methods','controls','expressions','residual_options','residual_equations','pseudo_time']:assert r['before'][key]==r['after'][key],key
  r['initial_native_iteration']=s.settings.setup.named_expressions['P9Iteration'].get_value();assert r['initial_native_iteration']==0
  metrics={k:float(v[0]) for row in s.settings.solution.report_definitions.compute(report_defs=r['reports']) for k,v in row.items()};r['initial_metrics']=metrics
  for ph in ['l','v','m']:
   for boundary in ['li','vi','bo','so','net']:assert abs(metrics['p9'+ph+boundary])<1e-12
  assert metrics['p9maxspeed']==0
  r['status']='READY_FOR_SMOKE';persist();(BASE/'output/steady-vof-hydrostatic/build-receipt.json').write_text(json.dumps({'manifest':str(out/'manifest.json')}));print(str(out/'manifest.json'),flush=True)
 except Exception as e:r.update(status='BUILD_REPAIR_REQUIRED',error=repr(e));persist();raise
 finally:signal.alarm(0)
if __name__=='__main__':main()
