"""Build zero-feed hydrostatic control; never iterate."""
from build_steady_vof_simple import *
from build_steady_vof_simple import assert_contract as flow_contract
from ansys.fluent.core.field_data_interfaces import SurfaceFieldDataRequest,SurfaceDataType

def assert_contract(s, inlet_velocity=0.):
 a=s.settings.setup;b=s.settings.solution
 assert b.methods.multiphase_numerics.advanced_stability_controls.p_v_coupling.rhie_chow_flux.low_order_rhie_chow() is True
 assert b.methods.expert.disable_rhie_chow_flux() is True
 assert b.methods.vof_numerics.high_order_rc() is True
 assert not b.methods.vof_numerics.high_order_rc_hybrid_treatment.is_active()
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
 # All physical boundary vertices must be enclosed by the other five region faces.
 boundary_state=a.boundary_conditions.get_state()
 names=[name for group in boundary_state.values() if isinstance(group,dict) for name in group if name != ZONE]
 surface_names=s.fields.field_info.get_surfaces_info()
 names=[name for name in names if name in surface_names]
 assert {'liquid-inlet','steam-inlet','brine-outlet','steam-outlet'}.issubset(names)
 geo=s.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=names,data_types=[SurfaceDataType.Vertices]))
 vertices=np.concatenate([np.asarray(geo[name].vertices).reshape(-1,3) for name in names])
 lo=np.minimum(vertices.min(axis=0),xyz.min(axis=0))-1.;hi=np.maximum(vertices.max(axis=0),xyz.max(axis=0))+1.;hi[1]=h
 assert np.all(vertices[:,[0,2]]>lo[[0,2]]) and np.all(vertices[:,[0,2]]<hi[[0,2]]) and np.all(vertices[:,1]>lo[1])
 (out/'region-enclosure.json').write_text(json.dumps({'boundaries':names,'vertex_min':vertices.min(axis=0).tolist(),'vertex_max':vertices.max(axis=0).tolist(),'region_min':lo.tolist(),'region_max':hi.tolist()}))
 regs=b.cell_registers
 if 'p9_pool' not in regs.get_object_names():regs.create(name='p9_pool')
 regs['p9_pool'].set_state({'type':{'option':'hexahedron','hexahedron':{'min_point':lo.tolist(),'max_point':hi.tolist(),'inside':True}}})
 b.initialization.patch.vof_smooth_options.set_state({'patch_reconstructed_interface':True,'use_volumetric_smoothing':False})
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
 assert np.isfinite(alpha).all() and alpha.min()>=0 and alpha.max()<=1
 assert np.count_nonzero((alpha>1e-12)&(alpha<1-1e-12))>0, 'No fractional cells: reconstruction not proved'
 assert np.allclose(actual,pressure,rtol=0,atol=1e-8)
 np.savez_compressed(out/'initial-fields.npz',xyz=xyz,volume=vol,alpha=alpha,pressure=actual)
 r={'pool_height_m':h,'cell_count':len(vol),'mesh_volume_m3':float(vol.sum()),'fractional_cells':int(np.count_nonzero((alpha>1e-12)&(alpha<1-1e-12))),'selected_volume_m3':float(vol[alpha==1].sum()),'liquid_volume_m3':float(np.dot(alpha,vol)),'liquid_mass_kg':float(881.77*np.dot(alpha,vol)),'pressure_min_Pa':float(actual.min()),'pressure_max_Pa':float(actual.max()),'register':regs['p9_pool'].get_state()}
 for v in ['SV_U','SV_V','SV_W']:
  arr=np.asarray(sv.get_data(variable_name=v,zone_names=[ZONE],domain_name='mixture')[ZONE]);assert np.max(abs(arr))==0
 return r

def capture_aux(s,path):
 data={};stats={}
 for name in ['SV_P_G','SV_DENSITY','SV_BF_V','SV_BFP_V']:
  a=np.asarray(s.fields.solution_variable_data.get_data(variable_name=name,zone_names=[ZONE],domain_name='mixture')[ZONE]);data[name]=a;stats[name]={'shape':list(a.shape),'min':float(a.min()),'max':float(a.max())}
 np.savez_compressed(path,**data);return stats

def main():
 tag='low-order-rhie-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 out=BASE/'output/pressure-gravity-initialization'/tag;out.mkdir(parents=True)
 r={'status':'BUILDING','tag':tag,'height':.1,'iterations_issued':0,'case':ROOT+'/case-data/'+tag+'-n00000.cas.h5','out':str(out)}
 def persist():(out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('Build deadline')));signal.alarm(600);persist()
 try:
  s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating()
  prior=Path(json.loads((BASE/'output/pressure-gravity-initialization/bodyforce-one-n500-receipt.json').read_text())['run_manifest']);prev=json.loads(prior.read_text())
  assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==1
  from build_bodyforce_one import assert_contract as prior_contract
  from build_reconstructed_interface import assert_contract as reference_contract
  prior_contract(s)
  assert all(remote_file_exists(s,prev['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  r['preserved_endpoint']=prev['case'];parent_path=Path(json.loads((BASE/'output/discrete-interface-initialization/build-receipt.json').read_text())['manifest']);parent=json.loads(parent_path.read_text())
  r['configuration_parent_manifest']=str(parent_path);r['configuration_parent_case']=parent['case']
  s.settings.file.read_case_data(file_name=parent['case']);assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==0
  reference_contract(s);old=snapshot(s)
  rc=s.settings.solution.methods.multiphase_numerics.advanced_stability_controls.p_v_coupling.rhie_chow_flux.low_order_rhie_chow
  assert rc.is_active() and rc() is False
  rc.set_state(True);assert rc() is True
  old['methods']['multiphase_numerics']['advanced_stability_controls']['p_v_coupling']['rhie_chow_flux']['low_order_rhie_chow']=True
  old['methods']['expert']['disable_rhie_chow_flux']=True
  old['methods']['vof_numerics']['high_order_rc']=True
  old['methods']['vof_numerics'].pop('high_order_rc_hybrid_treatment',None)
  s.settings.solution.methods.spatial_discretization.discretization_scheme['pressure']='modified-body-force-weighted'
  assert s.settings.solution.methods.spatial_discretization.discretization_scheme['pressure']()=='modified-body-force-weighted'
  old['methods']['spatial_discretization']['discretization_scheme']['pressure']='modified-body-force-weighted'
  for inlet in ['liquid-inlet','steam-inlet']:s.settings.setup.boundary_conditions.velocity_inlet[inlet].phase['mixture'].momentum.velocity_magnitude.value=0.
  assert_contract(s);r['controlled_delta']={'face_flux_interpolation':'low_order_rhie_chow false to true only, relative to reconstructed-interface all-URF0.3 reference; momentum stays second-order upwind'}
  for n in s.settings.solution.monitor.report_files.get_object_names():s.settings.solution.monitor.report_files[n].active=False
  r['reports']=parent['reports'];r['initialization']=initialize(s,.1,out)
  a=np.load(out/'initial-fields.npz');b=np.load(parent_path.parent/'initial-fields.npz');assert all(np.allclose(a[k],b[k],rtol=0,atol=1e-8) if k=='pressure' else np.array_equal(a[k],b[k]) for k in ['xyz','volume','pressure','alpha'])
  r['pressure_geometry_identical_to_reference_N0']=True;r['initial_mass_difference_kg']=float(881.77*np.dot(a['alpha']-b['alpha'],a['volume']));r['before']=snapshot(s)
  # No physical/numerical changes beyond the declared inlet velocity controls.
  for key in ['solver','operating','models','materials','zones','methods','controls']:
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
