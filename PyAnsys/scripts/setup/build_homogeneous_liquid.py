"""Build homogeneous-liquid hydrostatic isolation control; never iterate."""
from build_steady_vof_simple import *
from build_steady_vof_simple import assert_contract as flow_contract
from ansys.fluent.core.field_data_interfaces import SurfaceFieldDataRequest,SurfaceDataType

def assert_contract(s, inlet_velocity=0.):
 a=s.settings.setup;b=s.settings.solution
 assert a.general.operating_conditions.gravity.components()==[0.,-9.81,0.]
 assert a.general.operating_conditions.operating_pressure()==1120000
 assert a.boundary_conditions.pressure_outlet['steam-outlet'].phase['mixture'].momentum.gauge_pressure.value()=='P9BrinePressure'
 for name in ['liquid-inlet','steam-inlet']:assert a.boundary_conditions.velocity_inlet[name].phase['mixture'].momentum.initial_gauge_pressure.value()==20000
 assert a.named_expressions['P9BrinePressure'].definition()=='876.04[kg/m^3]*9.81[m/s^2]*(0.10[m]-y)'
 assert a.boundary_conditions.pressure_outlet['steam-outlet'].phase['phase-2'].multiphase.backflow_volume_fraction.value()==1
 assert a.boundary_conditions.pressure_outlet['steam-outlet'].phase['mixture'].momentum.pressure_spec()=='Gauge Pressure'
 assert a.boundary_conditions.pressure_outlet['steam-outlet'].phase['mixture'].momentum.pressure_profile_multiplier()==1
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
 assert 'brine-outlet' in a.boundary_conditions.outlet_vent.get_object_names()
 v=a.boundary_conditions.outlet_vent['brine-outlet']
 assert v.phase['mixture'].momentum.loss_coefficient.value()==9
 assert v.phase['mixture'].momentum.gauge_pressure.value()=='P9BrinePressure'
 assert v.phase['phase-2'].multiphase.backflow_volume_fraction.value()==1
 for n,alpha in [('liquid-inlet',1),('steam-inlet',1)]:
  o=a.boundary_conditions.velocity_inlet[n]
  assert o.phase['mixture'].momentum.velocity_magnitude.value()==inlet_velocity
  assert o.phase['phase-2'].multiphase.volume_fraction.value()==alpha

def initialize(s,h,out):
 b=s.settings.solution;a=s.settings.setup
 b.initialization.defaults.set_state({'pressure':0,'x-velocity':0,'y-velocity':0,'z-velocity':0,'phase-2-mp':1,'k':0.01,'epsilon':0.01})
 b.initialization.standard_initialize()
 b.initialization.patch.calculate_patch(domain='phase-2',cell_zones=[ZONE],variable='mp',value=1.)
 sv=s.fields.solution_variable_data
 xyz=np.asarray(sv.get_data(variable_name='SV_CENTROID',zone_names=[ZONE],domain_name='mixture')[ZONE]).reshape(-1,3)
 vol=np.asarray(sv.get_data(variable_name='SV_VOLUME',zone_names=[ZONE],domain_name='mixture')[ZONE])
 pressure=876.04*9.81*(h-xyz[:,1])
 a.named_expressions['HsrHydrostaticPressure'].definition='876.04[kg/m^3]*9.81[m/s^2]*(0.10[m]-y)'
 b.initialization.patch.calculate_patch(domain='mixture',cell_zones=[ZONE],variable='pressure',use_custom_field_function=False,value='HsrHydrostaticPressure')
 alpha=np.asarray(sv.get_data(variable_name='SV_VOF',zone_names=[ZONE],domain_name='phase-2')[ZONE])
 actual=np.asarray(sv.get_data(variable_name='SV_P',zone_names=[ZONE],domain_name='mixture')[ZONE])
 density=np.asarray(sv.get_data(variable_name='SV_DENSITY',zone_names=[ZONE],domain_name='mixture')[ZONE])
 assert np.all(alpha==1.) and np.allclose(actual,pressure,rtol=0,atol=1e-8)
 assert np.allclose(density,881.77,rtol=0,atol=1e-8)
 assert len(vol)==620431 and abs(vol.sum()-27.0630856948)<1e-7
 for key in ['SV_U','SV_V','SV_W']:assert np.max(abs(np.asarray(sv.get_data(variable_name=key,zone_names=[ZONE],domain_name='mixture')[ZONE])))==0
 np.savez_compressed(out/'initial-fields.npz',xyz=xyz,volume=vol,alpha=alpha,pressure=actual)
 return {'liquid_mass_kg':float(881.77*vol.sum()),'cell_count':len(vol),'mesh_volume_m3':float(vol.sum()),'alpha_min':float(alpha.min()),'alpha_max':float(alpha.max()),'pressure_min_Pa':float(actual.min()),'pressure_max_Pa':float(actual.max()),'density_max_error':float(np.max(abs(density-881.77)))}

def capture_aux(s,path):
 data={};stats={}
 for name in ['SV_P_G','SV_DENSITY','SV_BF_V','SV_BFP_V']:
  a=np.asarray(s.fields.solution_variable_data.get_data(variable_name=name,zone_names=[ZONE],domain_name='mixture')[ZONE]);data[name]=a;stats[name]={'shape':list(a.shape),'min':float(a.min()),'max':float(a.max())}
 np.savez_compressed(path,**data);return stats

def main():
 tag='homogeneous-liquid-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 out=BASE/'output/pressure-gravity-initialization'/tag;out.mkdir(parents=True)
 r={'status':'BUILDING','tag':tag,'height':.1,'iterations_issued':0,'case':ROOT+'/case-data/'+tag+'-n00000.cas.h5','out':str(out)}
 def persist():(out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('Build deadline')));signal.alarm(600);persist()
 try:
  s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating()
  prior=Path(json.loads((BASE/'output/pressure-gravity-initialization/hydrostatic-datum-n500-receipt.json').read_text())['run_manifest']);prev=json.loads(prior.read_text())
  assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==1
  from build_hydrostatic_datum import assert_contract as prior_contract
  from build_hydrostatic_datum import assert_contract as reference_contract
  prior_contract(s)
  assert all(remote_file_exists(s,prev['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  r['preserved_endpoint']=prev['case'];parent_path=Path('/Users/andy/Desktop/P4P/P4P_shared/PyAnsys/output/pressure-gravity-initialization/hydrostatic-datum-20261002T152545Z/manifest.json');parent=json.loads(parent_path.read_text())
  r['configuration_parent_manifest']=str(parent_path);r['configuration_parent_case']=parent['case']
  s.settings.file.read_case_data(file_name=parent['case']);assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==0
  reference_contract(s);old=snapshot(s)
  a=s.settings.setup
  a.boundary_conditions.pressure_outlet['steam-outlet'].phase['mixture'].momentum.gauge_pressure.value='P9BrinePressure'
  a.boundary_conditions.pressure_outlet['steam-outlet'].phase['phase-2'].multiphase.backflow_volume_fraction.value=1.
  a.boundary_conditions.velocity_inlet['steam-inlet'].phase['phase-2'].multiphase.volume_fraction.value=1.
  old['expressions']['HsrHydrostaticPressure']['definition']='876.04[kg/m^3]*9.81[m/s^2]*(0.10[m]-y)'
  old['boundaries']['pressure_outlet']['steam-outlet']['phase']['mixture']['momentum']['gauge_pressure']['value']='P9BrinePressure'
  old['boundaries']['pressure_outlet']['steam-outlet']['phase']['phase-2']['multiphase']['backflow_volume_fraction']['value']=1.
  old['boundaries']['velocity_inlet']['steam-inlet']['phase']['phase-2']['multiphase']['volume_fraction']['value']=1.
  assert_contract(s);r['controlled_delta']={'homogeneous_liquid_isolation':'All cells/potentialphaseinflows alpha1; linear full-liquid pressure acrossdomain and bothoutlets. Remaining physics/numerics unchanged.'}
  for n in s.settings.solution.monitor.report_files.get_object_names():s.settings.solution.monitor.report_files[n].active=False
  r['reports']=parent['reports'];r['initialization']=initialize(s,.1,out)
  a=np.load(out/'initial-fields.npz');b=np.load(parent_path.parent/'initial-fields.npz');assert all(np.array_equal(a[k],b[k]) for k in ['xyz','volume'])
  r['geometry_identical_to_reference_N0']=True;r['uniform_liquid_verified']=bool(np.all(a['alpha']==1.));r['before']=snapshot(s)
  # No physical/numerical changes beyond the declared inlet velocity controls.
  for key in ['solver','operating','models','materials','zones','methods','controls','expressions']:
   assert old[key]==r['before'][key],key
  before_bc=copy.deepcopy(old['boundaries']);after_bc=copy.deepcopy(r['before']['boundaries'])
  for inlet in ['liquid-inlet','steam-inlet']:
   before_bc['velocity_inlet'][inlet]['phase']['mixture']['momentum']['velocity_magnitude']['value']=0.
  assert before_bc==after_bc,'Unexpected boundary change'
  r['aux_before_write']=capture_aux(s,out/'aux-before-write.npz')
  s.settings.file.write_case_data(file_name=r['case']);assert all(remote_file_exists(s,r['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  s.settings.file.read_case_data(file_name=r['case']);assert_contract(s);r['after']=snapshot(s)
  r['aux_after_reopen']=capture_aux(s,out/'aux-after-reopen.npz')
  for key in ['solver','operating','models','materials','boundaries','zones','methods','controls','expressions','residual_options','residual_equations','pseudo_time']:assert r['before'][key]==r['after'][key],key
  assert s.settings.solution.methods.spatial_discretization.discretization_scheme['pressure']()=='modified-body-force-weighted'
  assert s.settings.solution.initialization.patch.vof_smooth_options.get_state()=={'patch_reconstructed_interface':True,'use_volumetric_smoothing':False}
  sv=s.fields.solution_variable_data
  assert np.array_equal(np.asarray(sv.get_data(variable_name='SV_VOF',zone_names=[ZONE],domain_name='phase-2')[ZONE]),a['alpha'])
  assert np.allclose(np.asarray(sv.get_data(variable_name='SV_P',zone_names=[ZONE],domain_name='mixture')[ZONE]),a['pressure'],rtol=0,atol=1e-8)
  r['initial_native_iteration']=s.settings.setup.named_expressions['P9Iteration'].get_value();assert r['initial_native_iteration']==0
  metrics={k:float(v[0]) for row in s.settings.solution.report_definitions.compute(report_defs=r['reports']) for k,v in row.items()};r['initial_metrics']=metrics
  for ph in ['l','v','m']:
   for boundary in ['li','vi','bo','so','net']:assert abs(metrics['p9'+ph+boundary])<1e-12
  assert metrics['p9maxspeed']==0
  r['status']='READY_FOR_SMOKE';persist();(BASE/'output/pressure-gravity-initialization/build-receipt.json').write_text(json.dumps({'manifest':str(out/'manifest.json')}));print(str(out/'manifest.json'),flush=True)
 except Exception as e:r.update(status='BUILD_REPAIR_REQUIRED',error=repr(e));persist();raise
 finally:signal.alarm(0)
if __name__=='__main__':main()
