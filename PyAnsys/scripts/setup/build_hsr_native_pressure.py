"""Build zero-feed hydrostatic control; never iterate."""
from build_steady_vof_simple import *
from build_steady_vof_simple import assert_contract as flow_contract

def assert_contract(s):
 flow_contract(s,inlet_velocity=0.)

def initialize(s,h,out):
 b=s.settings.solution;a=s.settings.setup
 b.initialization.defaults.set_state({'pressure':1120000,'x-velocity':0,'y-velocity':0,'z-velocity':0,'phase-2-mp':0,'k':0.01,'epsilon':0.01})
 b.initialization.standard_initialize()
 sv=s.fields.solution_variable_data
 xyz=np.asarray(sv.get_data(variable_name='SV_CENTROID',zone_names=[ZONE],domain_name='mixture')[ZONE]).reshape(-1,3)
 vol=np.asarray(sv.get_data(variable_name='SV_VOLUME',zone_names=[ZONE],domain_name='mixture')[ZONE])
 assert len(vol)==620431 and abs(vol.sum()-27.0630856948)<1e-7
 lo=xyz.min(axis=0)-.01;hi=xyz.max(axis=0)+.01;hi[1]=h
 regs=b.cell_registers
 if 'p9_pool' not in regs.get_object_names():regs.create(name='p9_pool')
 regs['p9_pool'].set_state({'type':{'option':'hexahedron','hexahedron':{'min_point':lo.tolist(),'max_point':hi.tolist(),'inside':True}}})
 b.initialization.patch.vof_smooth_options.set_state({'patch_reconstructed_interface':False,'use_volumetric_smoothing':False})
 b.initialization.patch.calculate_patch(domain='phase-2',registers=['p9_pool'],variable='mp',value=1.)
 # Native pressure expression patch; no direct SV_P write.
 pressure=np.ascontiguousarray(1120000+876.04*9.81*np.maximum(h-xyz[:,1],0),dtype=np.float64)
 expr='HsrHydrostaticPressure'
 if expr not in a.named_expressions.get_object_names():a.named_expressions.create(name=expr)
 a.named_expressions[expr].definition='1120000[Pa]+876.04[kg/m^3]*9.81[m/s^2]*max(0.10[m]-y,0[m])'
 patch=b.initialization.patch.calculate_patch
 # Context-free allowed_values is empty in this live v252 tree; native call validates the explicit mixture/pressure pair.
 patch(domain='mixture',cell_zones=[ZONE],variable='pressure',use_custom_field_function=False,value=expr)
 alpha=np.asarray(sv.get_data(variable_name='SV_VOF',zone_names=[ZONE],domain_name='phase-2')[ZONE])
 actual=np.asarray(sv.get_data(variable_name='SV_P',zone_names=[ZONE],domain_name='mixture')[ZONE])
 assert np.array_equal(alpha,(xyz[:,1]<=h).astype(float)), 'Native patch/cell selection disagree'
 assert np.allclose(actual,pressure,rtol=0,atol=1e-8)
 np.savez_compressed(out/'initial-fields.npz',xyz=xyz,volume=vol,alpha=alpha,pressure=actual)
 r={'pool_height_m':h,'cell_count':len(vol),'mesh_volume_m3':float(vol.sum()),'selected_cells':int(alpha.sum()),'selected_volume_m3':float(vol[alpha==1].sum()),'liquid_volume_m3':float(np.dot(alpha,vol)),'liquid_mass_kg':float(881.77*np.dot(alpha,vol)),'pressure_min_Pa':float(actual.min()),'pressure_max_Pa':float(actual.max()),'register':regs['p9_pool'].get_state()}
 for v in ['SV_U','SV_V','SV_W']:
  arr=np.asarray(sv.get_data(variable_name=v,zone_names=[ZONE],domain_name='mixture')[ZONE]);assert np.max(abs(arr))==0
 return r

def main():
 tag='native-pressure-k9-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 out=BASE/'output/hydrostatic-startup-recovery'/tag;out.mkdir(parents=True)
 r={'status':'BUILDING','tag':tag,'height':.1,'iterations_issued':0,'case':ROOT+'/case-data/'+tag+'-n00000.cas.h5','out':str(out)}
 def persist():(out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('Build deadline')));signal.alarm(600);persist()
 try:
  s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating()
  prior=Path(json.loads((BASE/'output/steady-vof-hydrostatic/n500-receipt.json').read_text())['run_manifest']);prev=json.loads(prior.read_text())
  assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==1
  assert_contract(s)
  assert all(remote_file_exists(s,prev['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  r['preserved_endpoint']=prev['case'];parent_path=Path(prev['build']);parent=json.loads(parent_path.read_text())
  r['configuration_parent_manifest']=str(parent_path);r['configuration_parent_case']=parent['case']
  s.settings.file.read_case_data(file_name=parent['case']);assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==0
  assert_contract(s);old=snapshot(s)
  for inlet in ['liquid-inlet','steam-inlet']:s.settings.setup.boundary_conditions.velocity_inlet[inlet].phase['mixture'].momentum.velocity_magnitude.value=0.
  assert_contract(s);r['controlled_delta']={'pressure_initialization':'native named-expression patch instead of direct SV_P assignment'}
  for n in s.settings.solution.monitor.report_files.get_object_names():s.settings.solution.monitor.report_files[n].active=False
  r['reports']=parent['reports'];r['initialization']=initialize(s,.1,out)
  a=np.load(out/'initial-fields.npz');b=np.load(parent_path.parent/'initial-fields.npz');assert all(np.allclose(a[k],b[k],rtol=0,atol=1e-8) if k=='pressure' else np.array_equal(a[k],b[k]) for k in a.files)
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
  r['status']='READY_FOR_SMOKE';persist();(BASE/'output/hydrostatic-startup-recovery/build-receipt.json').write_text(json.dumps({'manifest':str(out/'manifest.json')}));print(str(out/'manifest.json'),flush=True)
 except Exception as e:r.update(status='BUILD_REPAIR_REQUIRED',error=repr(e));persist();raise
 finally:signal.alarm(0)
if __name__=='__main__':main()
