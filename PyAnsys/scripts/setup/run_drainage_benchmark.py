"""Four fixed steady single-liquid outlet-vent verification controls, never separator solves."""
from pathlib import Path
import sys,json,fcntl,time,yaml,signal
from datetime import datetime,timezone
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.remote_text import read_text
from ansys.fluent.core.streaming_services.events_streaming import SolverEvent
BASE=Path(__file__).resolve().parents[2];out=BASE/'output/drainage-benchmark';state=BASE.parent/'Project/experiments/drainage-boundary-verification/phase-state.yaml'
def guard_reason(metrics, expired):
 if expired:return 'deadline'
 if not all(np.isfinite(x) for x in metrics.values()):return 'nonfinite_metrics'
 if metrics['bmax']>20:return 'maximum_speed_above_20_m_s'
 return None

def main():
 lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 cfg=yaml.safe_load(state.read_text());deadline=datetime.fromisoformat(cfg['execution_deadline_utc']);assert datetime.now(timezone.utc)<deadline
 ledger={'status':'CONFIGURING','completed_iterations':0,'cases':[],'started_utc':datetime.now(timezone.utc).isoformat(),'controller_pid':__import__('os').getpid()};lp=out/'campaign.json'
 def persist():lp.write_text(json.dumps(ledger,indent=2))
 assert not lp.exists(),'Reconcile existing campaign before retry';persist()
 s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating();assert s.settings.setup.cell_zone_conditions.fluid.get_object_names()==['fluid']
 root='C:/Users/qtra338/P4P/experiments/phase-09-steady-vof-pool/case-data'
 a=s.settings.setup;b=s.settings.solution
 assert a.models.multiphase.model()=='none' and a.models.viscous.model()=='laminar'
 assert not a.general.operating_conditions.gravity.enable()
 b.initialization.initialization_type='standard'
 print('DEFAULTS',b.initialization.defaults.get_state(),flush=True)
 definitions={'biter':'Iteration','bin':'MassFlow(["inlet"])','bout':'MassFlow(["outlet"])','bpi':'AreaAve(StaticPressure,["inlet"])','bpo':'AreaAve(StaticPressure,["outlet"])','bvel':'AreaAve(VelocityMagnitude,["outlet"])','bmax':'Maximum(VelocityMagnitude,["fluid"])'}
 for name,expr in definitions.items():
  if name not in b.report_definitions.single_valued_expression.get_object_names():b.report_definitions.single_valued_expression.create(name=name)
  b.report_definitions.single_valued_expression[name].definition=expr
 b.monitor.residual.options.set_state({'n_save':2500,'normalize':False,'print':True,'plot':False})
 for eq in b.monitor.residual.equations.get_object_names():b.monitor.residual.equations[eq].check_convergence=False
 def snap():return {'models':a.models.get_state(),'operating':a.general.operating_conditions.get_state(),'material':a.materials.fluid['benchmark-liquid'].get_state(),'zones':a.cell_zone_conditions.get_state(),'bc':a.boundary_conditions.get_state(),'methods':b.methods.get_state()}
 def scalar():
  z=b.report_definitions.compute(report_defs=list(definitions));d={}
  for x in z:
   if isinstance(x,dict):d.update(x)
  return {k:float(v[0]) for k,v in d.items()}
 try:
  for k,dp in [(0,200),(0,800),(9,200),(9,800)]:
   assert datetime.now(timezone.utc)<deadline
   tag=f'k{k}-dp{dp}';p=out/tag;p.mkdir();r={'tag':tag,'K':k,'delta_total_to_ambient_Pa':dp,'expected_U':float(np.sqrt(2*dp/(881.77*(1+k)))),'iterations':0,'status':'PREPARING'};ledger['cases'].append(r);persist()
   a.boundary_conditions.pressure_inlet['inlet'].momentum.gauge_total_pressure.value=dp
   a.boundary_conditions.outlet_vent['outlet'].momentum.loss_coefficient.value=k
   b.initialization.defaults.set_state({'pressure':0,'x-velocity':0,'y-velocity':0,'z-velocity':0});b.initialization.standard_initialize()
   for name in b.monitor.report_files.get_object_names():b.monitor.report_files[name].active=False
   if 'bench-history' not in b.monitor.report_files.get_object_names():b.monitor.report_files.create(name='bench-history')
   report=root+'/'+tag+'-20260930.out';trn=root+'/'+tag+'-20260930.trn';case=root+'/'+tag+'-20260930-initial.cas.h5'
   b.monitor.report_files['bench-history'].set_state({'file_name':report,'report_defs':list(definitions),'frequency':1,'frequency_of':'iteration','active':True,'print':False})
   before=snap();s.settings.file.write_case_data(file_name=case);s.settings.file.read_case_data(file_name=case);assert snap()==before,'Save/reopen settings mismatch'
   b.monitor.report_files['bench-history'].file_name=report
   (p/'settings.json').write_text(json.dumps(before,indent=2));r['initial_case']=case;r['saved_reopened']=True;r['initial_metrics']=scalar();start=int(r['initial_metrics']['biter']);r['start_iteration']=start
   s.settings.file.start_transcript(file_name=trn);r['status']='RUNNING';ledger['status']='RUNNING';persist();print('RUNNING',tag,flush=True)
   def guard(session,event_info):
    try:
     values=scalar();r['last_guard_iteration']=int(values['biter'])
     reason=guard_reason(values,datetime.now(timezone.utc)>=deadline)
     if reason:
      r['stop_reason']=reason;persist();session.settings.solution.run_calculation.interrupt(interrupt_at='end of iteration')
    except Exception as e:
     r['capture_error']=repr(e);persist();session.settings.solution.run_calculation.interrupt(interrupt_at='end of iteration')
   cb=s.events.register_callback(SolverEvent.ITERATION_ENDED,guard)
   try:s.tui.solve.iterate(500)
   finally:s.events.unregister_callback(cb)
   r['terminal_metrics']=scalar();r['iterations']=int(r['terminal_metrics']['biter'])-start;ledger['completed_iterations']+=r['iterations'];assert ledger['completed_iterations']<=2000
   case=root+'/'+tag+'-20260930-final.cas.h5';s.settings.file.write_case_data(file_name=case);r['case']=case;r['pair_exists']=all(remote_file_exists(s,case.replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5']);assert r['pair_exists']
   s.settings.file.stop_transcript();(p/'native-history.out').write_text(read_text(s,report));(p/'native-transcript.trn').write_text(read_text(s,trn));r['status']='COMPLETE' if r['iterations']==500 else 'PARTIAL';persist();print('COMPLETE',tag,r['terminal_metrics'],flush=True)
   assert r['iterations']==500 and np.isfinite(list(r['terminal_metrics'].values())).all() and r['terminal_metrics']['bmax']<20
  ledger['status']='COMPLETE'
 except Exception as e:ledger['status']='RECONCILE_REQUIRED';ledger['error']=repr(e);raise
 finally:persist()
if __name__=='__main__':main()
