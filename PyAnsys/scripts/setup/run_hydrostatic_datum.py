"""Bounded zero-feed hydrostatic control, native evidence and quiescence guards."""
from build_hydrostatic_datum import *
import argparse,time,fcntl,os,yaml
from ansys.fluent.core.streaming_services.events_streaming import SolverEvent
FACES=['liquid-inlet','steam-inlet','brine-outlet','steam-outlet']

def scalar_metrics(s,names):
 raw=s.settings.solution.report_definitions.compute(report_defs=names)
 # Version-252 single-valued expressions return one dictionary per report.
 if isinstance(raw,(list,tuple)):
  vals={}
  for item in raw:
   if isinstance(item,dict):vals.update(item)
 else:vals=raw
 result={k:float(v[0] if isinstance(v,(list,tuple)) else v) for k,v in vals.items()}
 assert set(result)==set(names),(list(result),names)
 return result

def fields(s,out,n):
 sv=s.fields.solution_variable_data;d={}
 for domain,variables in [('mixture',['SV_CENTROID','SV_VOLUME','SV_P','SV_U','SV_V','SV_W']),('phase-2',['SV_VOF'])]:
  for variable in variables:d[domain+'_'+variable]=np.asarray(sv.get_data(variable_name=variable,zone_names=[ZONE],domain_name=domain)[ZONE])
 assert all(np.isfinite(a).all() for a in d.values())
 np.savez_compressed(out/f'fields-n{n:05d}.npz',**d)
 return {'liquid_mass_kg':float(881.77*np.dot(d['mixture_SV_VOLUME'],d['phase-2_SV_VOF'])),'max_speed_m_s':float(np.sqrt(sum(d['mixture_'+v]**2 for v in ['SV_U','SV_V','SV_W'])).max())}

def main():
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--mode',choices=['rest','flow'],required=True);p.add_argument('--iterations',type=int,required=True);p.add_argument('--expected-start',type=int,default=0);p.add_argument('--receipt',type=Path);p.add_argument('--parent-run',type=Path);args=p.parse_args()
 assert 0<args.iterations<=500
 phase_state=yaml.safe_load((BASE.parent/'Project/experiments/pressure-gravity-initialization/phase-state.yaml').read_text())
 assert phase_state.get('unsuccessful_contrasts',0)<phase_state['max_unsuccessful_contrasts']
 deadline_value=phase_state.get('execution_deadline_utc')
 deadline=datetime.fromisoformat(str(deadline_value).replace('Z','+00:00')) if deadline_value else None
 if deadline:assert deadline.tzinfo is not None and datetime.now(timezone.utc)<deadline,'Human execution deadline has expired'
 prior_runs=[]
 for prior in (BASE/'output/pressure-gravity-initialization').glob('**/run.json'):
  q=json.loads(prior.read_text())
  if q.get('status') in ['RUNNING','CONNECTING','RECONCILE_REQUIRED']:raise RuntimeError('Reconcile existing run first: '+str(prior))
  prior_runs.append(q)
 spent_iterations=sum(q.get('completed_iterations',q.get('issued_iterations',0)) for q in prior_runs)
 spent_seconds=sum(q.get('elapsed_s',0) for q in prior_runs)
 assert spent_iterations+args.iterations<=4000 and spent_seconds<8*3600
 build=json.loads(args.build.read_text());assert build['status']=='READY_FOR_SMOKE'
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');tag=f"{build['tag']}-{args.mode}-n{args.expected_start:05d}-{stamp}"
 out=args.build.parent/tag;out.mkdir();r={'status':'CONNECTING','mode':args.mode,'requested_iterations':args.iterations,'expected_start':args.expected_start,'controller_pid':os.getpid(),'tag':tag,'build':str(args.build),'report':ROOT+'/reports/'+tag+'.out','transcript':ROOT+'/logs/'+tag+'.trn','case':ROOT+'/case-data/'+tag+'-final.cas.h5'}
 lock=(BASE/'output/phase09-preflight/server1.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 def persist():(out/'run.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 r['investigation_label']='Steady VOF gravity-on equivalent-pressure-datum diagnostic'
 r['execution_deadline_utc']=deadline.isoformat() if deadline else None
 if args.receipt:
  args.receipt.parent.mkdir(parents=True,exist_ok=True)
  with args.receipt.open('x') as f:json.dump({'run_manifest':str((out/'run.json').resolve())},f)
 persist();s=None;callback=None;capture=None;started=time.monotonic();badcount=0
 signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('RPC deadline; reconcile before retry')));signal.alarm(240)
 try:
  s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating();assert_contract(s)
  assert s.settings.solution.methods.get_state()==build['after']['methods']
  assert s.settings.setup.boundary_conditions.get_state()==build['after']['boundaries']
  assert phase_state['status'] in ['READY_TO_RUN','RUNNING']
  assert s.settings.solution.initialization.patch.vof_smooth_options.get_state()=={'patch_reconstructed_interface':True,'use_volumetric_smoothing':False}
  n=lambda:int(s.settings.setup.named_expressions['P9Iteration'].get_value())
  assert n()==args.expected_start
  r['start_iteration']=n();r['prior_phase_iterations']=spent_iterations;r['prior_phase_wall_s']=spent_seconds
  b=s.settings.solution
  for name in b.monitor.report_files.get_object_names():b.monitor.report_files[name].active=False
  b.monitor.report_files['p9-history'].set_state({'active':True,'file_name':r['report']})
  s.settings.file.start_transcript(file_name=r['transcript'])
  r['initial_metrics']=scalar_metrics(s,build['reports'])
  if args.parent_run:
   parent=json.loads(args.parent_run.read_text())
   assert args.mode==parent['mode'] and parent['status'] in ['BLOCK_COMPLETE','RECOVERED_PARTIAL']
   if parent['status']=='RECOVERED_PARTIAL':
    assert parent.get('recovery') and parent.get('iterating') is False
    assert parent['completed_iterations']==parent['end_iteration']-parent['start_iteration']
   assert parent['pair_exists'] and parent['end_iteration']==args.expected_start and parent['build']==str(args.build)
   for key,value in parent['terminal_metrics'].items():assert np.isclose(r['initial_metrics'][key],value,rtol=1e-10,atol=1e-8),(key,value,r['initial_metrics'][key])
   r['continuation_parent']=str(args.parent_run.resolve());r['continuation_parent_case']=parent['case']
  if args.mode=='rest' and args.expected_start==0:assert all(abs(r['initial_metrics'][k])<1e-12 for k in ['p9lli','p9vvi','p9lnet','p9vnet','p9mnet'])
  r['initial_fields']=fields(s,out,n());persist()
  guard_names=['p9liquidmass','p9maxspeed','p9lnet','p9vnet','p9mnet','p9minalpha','p9maxalpha']
  capture=(out/'iteration-evidence.jsonl').open('x');r['last_capture']=None;r['event_count']=0
  def guard(session,event_info):
   nonlocal badcount
   try:
    i=int(event_info.index)
    if i==r['last_capture']:return
    if r['last_capture'] is None:
     assert i in [args.expected_start,args.expected_start+1],('Unexpected initial event',i,args.expected_start)
     r['first_capture']=i
    else:assert i==r['last_capture']+1,('Capture gap',i,r['last_capture'])
    row={'iteration':i,'metrics':scalar_metrics(session,guard_names),'flux':{}}
    for ph in ['mixture','phase-1','phase-2']:
     data=session.fields.solution_variable_data.get_data(variable_name='SV_FLUX',zone_names=FACES,domain_name=ph)
     row['flux'][ph]={}
     for face in FACES:
      a=np.asarray(data[face]);assert np.isfinite(a).all()
      row['flux'][ph][face]={'count':len(a),'signed_sum':float(a.sum()),'positive_sum':float(np.maximum(a,0).sum()),'negative_sum':float(np.minimum(a,0).sum())}
    capture.write(json.dumps(row)+'\n');capture.flush();r['last_capture']=i;r['event_count']+=1;r['last_metrics']=row['metrics'];r['elapsed_s']=time.monotonic()-started
    v=row['metrics'];assert all(np.isfinite(x) for x in v.values())
    reason=None
    if v['p9maxspeed']>2:reason='rest_maximum_speed_above_2_m_s'
    if abs(v['p9liquidmass']/build['initial_metrics']['p9liquidmass']-1)>.02:reason='rest_inventory_departure_above_2_percent'
    if v['p9minalpha'] < -1e-6 or v['p9maxalpha']>1+1e-6:reason='invalid_phase_bounds'
    if any(max(f['positive_sum'],-f['negative_sum'])>1 for ph in ['phase-1','phase-2'] for f in row['flux'][ph].values()):badcount+=1
    else:badcount=0
    if badcount>=20:reason='rest_gross_boundary_flux_above_1_kg_s_for_20'
    if spent_seconds+time.monotonic()-started>8*3600:reason='wall_budget'
    if deadline and datetime.now(timezone.utc)>=deadline:reason='human_execution_deadline'
    if reason:
     r['stop_reason']=reason;session.settings.solution.run_calculation.interrupt(interrupt_at='end of iteration')
    elif args.expected_start==0 and i==1 and not r.get('instrumentation_smoke_passed'):
     r['instrumentation_smoke_requested']=True;session.settings.solution.run_calculation.interrupt(interrupt_at='end of iteration')
    persist()
   except Exception as e:
    r['capture_error']=repr(e);persist();session.settings.solution.run_calculation.interrupt(interrupt_at='end of iteration')
  callback=s.events.register_callback(SolverEvent.ITERATION_ENDED,guard)
  if deadline:assert datetime.now(timezone.utc)<deadline,'Human execution deadline expired during preparation'
  r['callback_id']=callback;r['status']='RUNNING';r['issued_iterations']=args.iterations;persist();print('RUNNING',str(out),flush=True)
  signal.alarm(0)
  s.tui.solve.iterate(args.iterations)
  if r.get('instrumentation_smoke_requested') and not r.get('stop_reason') and not r.get('capture_error'):
   assert n()==1 and not s.settings.solution.run_calculation.iterating()
   assert r['last_capture']==1 and remote_file_exists(s,r['report'])
   proof=read_text(s,r['report']);assert len(proof.splitlines())>=4
   (out/'smoke-native-history.out').write_text(proof)
   r['instrumentation_smoke_passed']=True;r['N1_fields']=fields(s,out,1);r['N1_aux']=capture_aux(s,out/'N1-aux.npz');persist()
   if args.iterations>1:s.tui.solve.iterate(args.iterations-1)
  signal.alarm(300)
  s.events.unregister_callback(callback);callback=None
  r['end_iteration']=n();r['completed_iterations']=r['end_iteration']-r['start_iteration'];r['iterating']=s.settings.solution.run_calculation.iterating();assert not r['iterating']
  # Fluent can emit the starting-state event again on continuation.
  # Retain that sample as evidence, but do not count it as a solved iteration.
  assert r['event_count']==r['end_iteration']-r['first_capture']+1
  r['terminal_metrics']=scalar_metrics(s,build['reports']);r['terminal_fields']=fields(s,out,n());r['terminal_aux']=capture_aux(s,out/'terminal-aux.npz')
  if args.mode in ['rest','flow']:
   sys.path.insert(0,str(BASE/'scripts/inspection'))
   import export_phase07b_sections as export_api
   export_api.FIELDS=['phase-2-vof','pressure','velocity-magnitude']
   sections=[]
   for axis in ['x','z']:
    name='p9-section-'+axis+'0';g=s.settings.results.surfaces.iso_surface
    if name not in g.get_object_names():g.create(name=name)
    g[name].set_state({'field':axis+'-coordinate','iso_values':[0.]});sections.append(name)
   r['sections']=export_api.export_sections(s,sections,out/'terminal-sections')
  s.settings.file.write_case_data(file_name=r['case']);r['pair_exists']=all(remote_file_exists(s,r['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5']);assert r['pair_exists']
  s.settings.file.stop_transcript()
  (out/'native-history.out').write_text(read_text(s,r['report']));(out/'native-transcript.trn').write_text(read_text(s,r['transcript']))
  r['status']='STOPPED_AT_GATE' if r.get('stop_reason') else ('CAPTURE_REPAIR_REQUIRED' if r.get('capture_error') else 'BLOCK_COMPLETE')
  if r['status']=='BLOCK_COMPLETE':assert r['completed_iterations']==args.iterations and r['last_capture']==r['end_iteration']
  r['elapsed_s']=time.monotonic()-started;persist();print(r['status'],r['end_iteration'],r.get('stop_reason'),flush=True)
 except Exception as e:
  r['status']='RECONCILE_REQUIRED';r['error']=repr(e);persist()
  try:
   if s is not None and not s.settings.solution.run_calculation.iterating():
    r['end_iteration']=int(s.settings.setup.named_expressions['P9Iteration'].get_value());r['completed_iterations']=r['end_iteration']-r.get('start_iteration',args.expected_start)
    s.settings.file.write_case_data(file_name=r['case']);r['pair_exists']=all(remote_file_exists(s,r['case'].replace('.cas.h5',ex)) for ex in ['.cas.h5','.dat.h5'])
    r['iterating']=False;r['elapsed_s']=time.monotonic()-started
  except Exception as preservation_error:r['preservation_error']=repr(preservation_error)
  persist();raise
 finally:
  signal.alarm(0)
  if callback is not None and s is not None:
   try:s.events.unregister_callback(callback)
   except Exception:pass
  if capture is not None:capture.close()
  persist()
if __name__=='__main__':main()
