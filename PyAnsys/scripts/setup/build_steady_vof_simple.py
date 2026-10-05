"""Initialize the selected fresh steady VOF setup; no iterations or timesteps."""
from pathlib import Path
import sys,json,signal,hashlib,traceback,copy,fcntl
import numpy as np
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'src'))
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists,quote_scheme_string
from pyansys_fluent.remote_text import read_text
ROOT='C:/Users/qtra338/P4P/experiments/phase-09-steady-vof-pool'
ZONE='simple-spiral-separator--brine-outlet-'

def snapshot(s):
 a=s.settings.setup;b=s.settings.solution
 return {'solver':a.general.solver.get_state(),'operating':a.general.operating_conditions.get_state(),'models':a.models.get_state(),'materials':a.materials.fluid.get_state(),'boundaries':a.boundary_conditions.get_state(),'zones':a.cell_zone_conditions.get_state(),'methods':b.methods.get_state(),'controls':b.controls.get_state(),'expressions':a.named_expressions.get_state(),'reports':b.report_definitions.get_state(),'report_files':b.monitor.report_files.get_state(),'residual_options':b.monitor.residual.options.get_state(),'residual_equations':b.monitor.residual.equations.get_state(),'pseudo_time':b.run_calculation.pseudo_time_settings.get_state() if b.run_calculation.pseudo_time_settings.is_active() else {'active':False}}

def assert_contract(s, inlet_velocity=27.118):
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
 lo=xyz.min(axis=0)-.01;hi=xyz.max(axis=0)+.01;hi[1]=h
 regs=b.cell_registers
 if 'p9_pool' not in regs.get_object_names():regs.create(name='p9_pool')
 regs['p9_pool'].set_state({'type':{'option':'hexahedron','hexahedron':{'min_point':lo.tolist(),'max_point':hi.tolist(),'inside':True}}})
 b.initialization.patch.vof_smooth_options.set_state({'patch_reconstructed_interface':False,'use_volumetric_smoothing':False})
 b.initialization.patch.calculate_patch(domain='phase-2',registers=['p9_pool'],variable='mp',value=1.)
 # Public SVAR setter patches only pressure; phase patch uses Fluent's native API.
 pressure=np.ascontiguousarray(1120000+876.04*9.81*np.maximum(h-xyz[:,1],0),dtype=np.float64)
 sv.set_data(variable_name='SV_P',zone_names_to_data={ZONE:pressure},domain_name='mixture')
 alpha=np.asarray(sv.get_data(variable_name='SV_VOF',zone_names=[ZONE],domain_name='phase-2')[ZONE])
 actual=np.asarray(sv.get_data(variable_name='SV_P',zone_names=[ZONE],domain_name='mixture')[ZONE])
 assert np.array_equal(alpha,(xyz[:,1]<=h).astype(float)), 'Native patch/cell selection disagree'
 assert np.array_equal(actual,pressure)
 np.savez_compressed(out/'initial-fields.npz',xyz=xyz,volume=vol,alpha=alpha,pressure=actual)
 r={'pool_height_m':h,'cell_count':len(vol),'mesh_volume_m3':float(vol.sum()),'selected_cells':int(alpha.sum()),'selected_volume_m3':float(vol[alpha==1].sum()),'liquid_volume_m3':float(np.dot(alpha,vol)),'liquid_mass_kg':float(881.77*np.dot(alpha,vol)),'pressure_min_Pa':float(actual.min()),'pressure_max_Pa':float(actual.max()),'register':regs['p9_pool'].get_state()}
 for v in ['SV_U','SV_V','SV_W']:
  arr=np.asarray(sv.get_data(variable_name=v,zone_names=[ZONE],domain_name='mixture')[ZONE]);assert np.max(abs(arr))==0
 return r

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--height',type=float,choices=[.1,.3],default=.1);p.add_argument('--scale',type=float,choices=[.1,.3],default=.1);args=p.parse_args()
 tag='simple-k9-h'+str(args.height).replace('.','p')+'-urf0p3-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 out=BASE/'output'/'steady-vof-solver-method'/tag;out.mkdir(parents=True)
 r={'status':'BUILDING','tag':tag,'height':args.height,'iterations_issued':0,'case':ROOT+'/case-data/'+tag+'-n00000.cas.h5','report':ROOT+'/reports/'+tag+'.out','transcript':ROOT+'/logs/'+tag+'.trn','out':str(out)}
 def persist():(out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 persist();signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('Reconcile state before retry')));signal.alarm(600)
 try:
  s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating()
  parent_path=BASE/'output/full-geometry-drain-resistance/drain-k9-h0p1-scale0p1-20260930T064024Z/manifest.json'
  parent=json.loads(parent_path.read_text());assert parent['initial_native_iteration']==0
  preserved=json.loads((BASE/'output/drainage-benchmark/restore-parent.json').read_text())['case']
  assert all(remote_file_exists(s,preserved.replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  s.settings.file.read_case_data(file_name=parent['case'])
  assert s.settings.setup.named_expressions['P9Iteration'].get_value()==0
  r.update(configuration_parent_manifest=str(parent_path),configuration_parent_case=parent['case'],preserved_separator=preserved,controlled_delta={'brine_boundary':'outlet-vent','K':9},fresh_reinitialization=True)
  assert 'brine-outlet' in s.settings.setup.boundary_conditions.outlet_vent.get_object_names()
  for which in ['low','high']:
   rp=Path(json.loads((BASE/f'output/full-geometry-drain-resistance/{which}-start-n1000-receipt.json').read_text())['run_manifest']);pr=json.loads(rp.read_text())
   assert all(remote_file_exists(s,pr['case'].replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
  s.settings.solution.methods.p_v_coupling.flow_scheme='SIMPLE'
  urfs=s.settings.solution.controls.under_relaxation.get_state();s.settings.solution.controls.under_relaxation.set_state({k:.3 for k in urfs})
  r['controlled_delta']={'flow_scheme':'SIMPLE','pseudo_time':'Off/inactive for segregated VOF','standard_urfs':{k:.3 for k in urfs}}
  vent=s.settings.setup.boundary_conditions.outlet_vent['brine-outlet']
  vent.phase['mixture'].momentum.loss_coefficient.option='constant'
  vent.phase['mixture'].momentum.loss_coefficient.value=9
  assert s.settings.setup.named_expressions['P9BrinePressure'].definition()==parent['before']['expressions']['P9BrinePressure']['definition']
  for inlet in ['liquid-inlet','steam-inlet']:s.settings.setup.boundary_conditions.velocity_inlet[inlet].phase['mixture'].momentum.velocity_magnitude.value=27.118
  assert_contract(s)
  a=s.settings.setup;b=s.settings.solution
  r['algorithm_dependent_controls']=b.controls.get_state()
  for name in b.monitor.report_files.get_object_names():b.monitor.report_files[name].active=False
  b.monitor.residual.options.set_state({'n_save':15000,'normalize':False,'print':True,'plot':False})
  for name in b.monitor.residual.equations.get_object_names():b.monitor.residual.equations[name].check_convergence=False
  loc=json.dumps([ZONE]);d={'P9Iteration':'Iteration','P9LiquidMass':f'881.77[kg/m^3]*VolumeInt(Volumefraction(phase="phase-2"),{loc})','P9VaporMass':f'5.73[kg/m^3]*VolumeInt(Volumefraction(phase="phase-1"),{loc})','P9LowerLiquid':f'881.77[kg/m^3]*VolumeInt(IF(y<0.5[m],Volumefraction(phase="phase-2"),0),{loc})','P9UpperLiquid':'P9LiquidMass-P9LowerLiquid','P9MaxSpeed':f'Maximum(VelocityMagnitude,{loc})','P9MinPressure':f'Minimum(StaticPressure,{loc})','P9MaxPressure':f'Maximum(StaticPressure,{loc})','P9MinAlpha':f'Minimum(Volumefraction(phase="phase-2"),{loc})','P9MaxAlpha':f'Maximum(Volumefraction(phase="phase-2"),{loc})'}
  for ph,short in [('phase-2','L'),('phase-1','V'),('mixture','M')]:
   for face,slug in [('liquid-inlet','LI'),('steam-inlet','VI'),('brine-outlet','BO'),('steam-outlet','SO')]:d['P9'+short+slug]=f'MassFlow(["{face}"],phase="{ph}")'
   d['P9'+short+'Net']='+'.join('P9'+short+k for k in ['LI','VI','BO','SO'])
  for face,slug in [('liquid-inlet','LI'),('steam-inlet','VI'),('brine-outlet','BO'),('steam-outlet','SO')]:d['P9P'+slug]=f'AreaAve(StaticPressure,["{face}"])'
  d['P9Drop']='P9PVI-P9PSO'
  reports=[]
  existing_expressions=set(a.named_expressions.get_object_names())
  existing_reports=set(b.report_definitions.single_valued_expression.get_object_names())
  print('Configuring native reports',flush=True)
  for name,expr in d.items():
   g=a.named_expressions
   if name not in existing_expressions:g.create(name=name)
   g[name].definition=expr
   rn=name.lower();g=b.report_definitions.single_valued_expression
   if rn not in existing_reports:g.create(name=rn)
   g[rn].definition=name;reports.append(rn)
  rf=b.monitor.report_files
  if 'p9-history' not in rf.get_object_names():rf.create(name='p9-history')
  rf['p9-history'].set_state({'file_name':r['report'],'report_defs':reports,'frequency':1,'frequency_of':'iteration','active':True,'print':False})
  r['definitions']=d;r['reports']=reports;persist()
  print('Initializing and verifying pool',flush=True)
  r['initialization']=initialize(s,args.height,out)
  reference=np.load(parent_path.parent/'initial-fields.npz');fresh=np.load(out/'initial-fields.npz')
  for key in reference.files:assert np.array_equal(reference[key],fresh[key]),('Fresh field mismatch',key)
  r['initial_fields_identical_to_reference']=True
  physical_snapshot=snapshot(s)
  for key in ['solver','operating','models','materials','boundaries','zones']:
   assert physical_snapshot[key]==parent['after'][key],('Physical setup changed',key)
  r['initial_native_iteration']=a.named_expressions['P9Iteration'].get_value();assert r['initial_native_iteration'] in [0,1]
  r['initial_metrics']=b.report_definitions.compute(report_defs=reports)
  r['before']=snapshot(s);persist()
  print('Saving and reopening verified initial state',flush=True)
  s.settings.file.write_case_data(file_name=r['case']);assert all(remote_file_exists(s,r['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
  s.settings.file.read_case_data(file_name=r['case']);assert_contract(s)
  r['after']=snapshot(s)
  before=copy.deepcopy(r['before']);after=copy.deepcopy(r['after'])
  for snap in [before,after]:snap['report_files']['p9-history'].pop('file_name')
  assert before==after,'Save/reopen scientific configuration changed'
  r['report_path_policy']='Rebind absolute report path before run; verify actual native writes'
  r['reopened_metrics']=s.settings.solution.report_definitions.compute(report_defs=reports)
  r['pre_save_native_iteration']=r['initial_native_iteration'];r['initial_native_iteration']=s.settings.setup.named_expressions['P9Iteration'].get_value()
  oldmetrics={k:float(v[0]) for row in r['initial_metrics'] for k,v in row.items()};newmetrics={k:float(v[0]) for row in r['reopened_metrics'] for k,v in row.items()}
  for k in oldmetrics:
   if k!='p9iteration':assert np.isclose(oldmetrics[k],newmetrics[k],rtol=1e-10,atol=1e-10)
  r['status']='READY_FOR_SMOKE';persist();(BASE/'output/steady-vof-solver-method/build-receipt.json').write_text(json.dumps({'manifest':str(out/'manifest.json')}));print(str(out/'manifest.json'),flush=True)
 except Exception as e:r['status']='BUILD_REPAIR_REQUIRED';r['error']=str(e);persist();raise
 finally:signal.alarm(0)
if __name__=='__main__':main()
