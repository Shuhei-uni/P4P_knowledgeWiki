"""Build zero-feed hydrostatic control; never iterate."""
from build_steady_vof_simple import *
from build_steady_vof_simple import assert_contract as flow_contract

def assert_contract(s, inlet_velocity=0.):
 a=s.settings.setup;b=s.settings.solution
 assert a.general.solver.time()=='steady'
 assert a.models.multiphase.model()=='vof' and a.models.multiphase.vof_parameters.vof_formulation()=='implicit'
 assert b.methods.p_v_coupling.flow_scheme()=='SIMPLE'
 assert not b.methods.pseudo_time_method.is_active() and not b.run_calculation.pseudo_time_settings.is_active()
 assert b.controls.under_relaxation.get_state()=={k:.3 for k in ['body-force','density','epsilon','k','mom','mp','pressure','turb-viscosity']}
 assert a.general.operating_conditions.operating_density.get_state()=={'method':'user-input','value':5.73}
 assert a.models.multiphase.advanced_formulation.implicit_body_force()
 assert a.cell_zone_conditions.fluid.get_object_names()==[ZONE]
 assert not a.models.energy.enabled() and not a.models.discrete_phase.general_settings.interaction.enabled()
 assert not a.models.discrete_phase.injections.get_object_names()
 for ph in ['mixture','phase-1','phase-2']:assert not a.cell_zone_conditions.fluid[ZONE].phase[ph].sources.enable()
 if 'brine-outlet' in a.boundary_conditions.wall.get_object_names():
  m=a.boundary_conditions.wall['brine-outlet'].phase['mixture'].momentum
  if m.wall_motion.is_active():assert m.wall_motion()=='Stationary Wall'
  assert 'specified' in m.shear_condition().lower() and 'shear' in m.shear_condition().lower()
  assert all(abs(x['value'])<1e-15 for x in m.shear_stress.get_state())
 else:assert 'brine-outlet' in a.boundary_conditions.outlet_vent.get_object_names()
 for n,alpha in [('liquid-inlet',1),('steam-inlet',0)]:
  o=a.boundary_conditions.velocity_inlet[n]
  assert o.phase['mixture'].momentum.velocity_magnitude.value()==inlet_velocity
  assert o.phase['phase-2'].multiphase.volume_fraction.value()==alpha

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
 tag='sealed-brine-mbfw-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 out=BASE/'output/hydrostatic-startup-recovery'/tag;out.mkdir(parents=True)
 r={'status':'BUILDING','tag':tag,'height':.1,'iterations_issued':0,'case':ROOT+'/case-data/'+tag+'-n00000.cas.h5','out':str(out)}
 def persist():(out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('Build deadline')));signal.alarm(600);persist()
 try:
  s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating()
  prior=Path(json.loads((BASE/'output/hydrostatic-startup-recovery/modified-bfw-n500-receipt.json').read_text())['run_manifest']);prev=json.loads(prior.read_text())
  assert int(s.settings.setup.named_expressions['P9Iteration'].get_value()) in [0,1]
  assert_contract(s)
  assert all(remote_file_exists(s,prev['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  r['preserved_endpoint']=prev['case'];parent_path=Path(prev['build']);parent=json.loads(parent_path.read_text())
  r['configuration_parent_manifest']=str(parent_path);r['configuration_parent_case']=parent['case']
  s.settings.file.read_case_data(file_name=parent['case']);assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==0
  assert_contract(s);old=snapshot(s)
  bc=s.settings.setup.boundary_conditions
  bc.set_zone_type(zone_list=['brine-outlet'],new_type='wall')
  wall=bc.wall['brine-outlet'].phase['mixture'].momentum
  wall.wall_motion='Stationary Wall'
  choices=wall.shear_condition.allowed_values();choice=[x for x in choices if 'specified' in x.lower() and 'shear' in x.lower()];assert len(choice)==1,choices
  wall.shear_condition=choice[0]
  stresses=wall.shear_stress.get_state();wall.shear_stress.set_state([{'option':'value','value':0.} for x in stresses])
  r['wall_readback']=wall.get_state()
  assert_contract(s)
  for inlet in ['liquid-inlet','steam-inlet']:s.settings.setup.boundary_conditions.velocity_inlet[inlet].phase['mixture'].momentum.velocity_magnitude.value=0.
  assert_contract(s);r['controlled_delta']={'brine_boundary':'outlet vent to stationary zero-shear impermeable wall; steam pressure outlet unchanged'}
  for n in s.settings.solution.monitor.report_files.get_object_names():s.settings.solution.monitor.report_files[n].active=False
  r['reports']=parent['reports'];r['initialization']=initialize(s,.1,out)
  a=np.load(out/'initial-fields.npz');b=np.load(parent_path.parent/'initial-fields.npz');assert all(np.allclose(a[k],b[k],rtol=0,atol=1e-8) if k=='pressure' else np.array_equal(a[k],b[k]) for k in a.files)
  r['initial_fields_identical_to_flow_N0']=True;r['before']=snapshot(s)
  # No physical/numerical changes beyond the declared inlet velocity controls.
  for key in ['solver','operating','models','materials','zones','methods','controls']:
   assert old[key]==r['before'][key],key
  before_bc=copy.deepcopy(old['boundaries']);after_bc=copy.deepcopy(r['before']['boundaries'])
  before_bc['outlet_vent'].pop('brine-outlet');after_bc['wall'].pop('brine-outlet')
  before_bc={k:v for k,v in before_bc.items() if v};after_bc={k:v for k,v in after_bc.items() if v}
  assert before_bc==after_bc,'Unexpected other boundary change'
  assert 'brine-outlet' in s.settings.setup.boundary_conditions.wall.get_object_names()
  s.settings.file.write_case_data(file_name=r['case']);assert all(remote_file_exists(s,r['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  s.settings.file.read_case_data(file_name=r['case']);assert_contract(s);r['after']=snapshot(s)
  for key in ['solver','operating','models','materials','boundaries','zones','methods','controls','expressions','residual_options','residual_equations','pseudo_time']:assert r['before'][key]==r['after'][key],key
  assert s.settings.solution.methods.spatial_discretization.discretization_scheme['pressure']()=='modified-body-force-weighted'
  r['initial_native_iteration']=s.settings.setup.named_expressions['P9Iteration'].get_value();assert r['initial_native_iteration']==0
  metrics={k:float(v[0]) for row in s.settings.solution.report_definitions.compute(report_defs=r['reports']) for k,v in row.items()};r['initial_metrics']=metrics
  for ph in ['l','v','m']:
   for boundary in ['li','vi','bo','so','net']:assert abs(metrics['p9'+ph+boundary])<1e-12
  assert metrics['p9maxspeed']==0
  r['status']='READY_FOR_SMOKE';persist();(BASE/'output/hydrostatic-startup-recovery/build-receipt.json').write_text(json.dumps({'manifest':str(out/'manifest.json')}));print(str(out/'manifest.json'),flush=True)
 except Exception as e:r.update(status='BUILD_REPAIR_REQUIRED',error=repr(e));persist();raise
 finally:signal.alarm(0)
if __name__=='__main__':main()
