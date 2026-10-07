"""Server 2 only: 200 low OFF, enable, 500 low ON, 25-point steps, 1000 full."""
from pathlib import Path
import sys,json,copy,math,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase8_stage2_absorber as absorber
base=absorber.base
BASE_WORK=absorber.trial.BASE_WORK
OUT=absorber.trial.BASE_OUT/'step-enable2200';WORK=BASE_WORK/'step-enable2200'
PARENT_OUT=absorber.OUT
PREVIOUS_OUT=absorber.trial.BASE_OUT/'slow-enable3000'
SCHEDULE=[[200,.25],[500,.25],[250,.5],[250,.75],[1000,1.0]]
base.OUT=OUT;base.WORK=WORK
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture

def paths_after_reload(s,b):
 for name,path in b['report_paths'].items():s.settings.solution.monitor.report_files[name+'-rfile'].file_name=path
 s.settings.file.auto_save.root_name=str(WORK/'autosaves/checkpoint').replace('\\','/')
 enabled=bool(s.settings.setup.cell_zone_conditions.fluid[absorber.LOWER_ZONE].phase['phase-2'].sources.enable())
 s.settings.solution.monitor.report_files['p8-applied-absorber-rfile'].active=enabled
 required={name:d for name,d in b['report_definitions'].items() if enabled or name!='p8-applied-absorber'}
 base.check_stage2_reports(s,required,b['report_paths'])

def switch(s,enabled):
 z=s.settings.setup.cell_zone_conditions.fluid[absorber.LOWER_ZONE]
 for p in ['phase-2','mixture']:z.phase[p].sources.enable=enabled
 assert not z.phase['phase-1'].sources.enable()
 assert z.phase['phase-2'].sources.enable()==z.phase['mixture'].sources.enable()==enabled
 if enabled:
  absorber.configure_bulk(s,'10us','libcontactv2')
  for term in ['k','epsilon']:z.phase['mixture'].sources.terms[term].set_state([{'option':'value','value':0.0}])
 return z.get_state()

def audit(s,multiplier,enabled,reference):
 actual=base.setup(s)
 assert actual['methods']==reference['methods'] and actual['controls']==reference['controls']
 a=copy.deepcopy(actual['setup']);b=copy.deepcopy(reference['setup'])
 for x in [a,b]:
  x.pop('named_expressions',None);x.pop('user_defined',None)
  for cell in x['cell_zone_conditions']['fluid'].values():
   for phase in cell['phase'].values():phase.pop('sources',None)
  for zone in x['boundary_conditions']['mass_flow_inlet'].values():
   for phase in zone['phase'].values():
    if 'momentum' in phase:phase['momentum'].pop('mass_flow_rate',None)
 assert a==b,'Fixed scientific setup changed'
 for name,cell in actual['setup']['cell_zone_conditions']['fluid'].items():
  for ph,value in cell['phase'].items():assert bool(value['sources']['enable'])==(enabled and name==absorber.LOWER_ZONE and ph in ['mixture','phase-2'])
 bc=s.settings.setup.boundary_conditions.mass_flow_inlet
 for zone,phase,expected in [('liquidinlet','phase-2',base.TARGET_LIQUID*multiplier),('liquidinlet','phase-1',0),('steaminlet','phase-1',base.TARGET_VAPOR*multiplier),('steaminlet','phase-2',0)]:
  assert math.isclose(float(bc[zone].phase[phase].momentum.mass_flow_rate.get_state()['value']),expected,rel_tol=1e-12,abs_tol=1e-9)
 if enabled:
  z=s.settings.setup.cell_zone_conditions.fluid[absorber.LOWER_ZONE]
  assert z.phase['phase-2'].sources.terms['mass'].get_state()==[{'option':'udf','udf':'contact_mass_10us::libcontactv2'}]
  for term in ['k','epsilon']:assert z.phase['mixture'].sources.terms[term].get_state()==[{'option':'value','value':0.0}]
  for axis in 'xyz':assert z.phase['mixture'].sources.terms[axis+'-momentum'].get_state()==[{'option':'udf','udf':f'contact_{axis}_10us::libcontactv2'}]
 return {'fixed_settings':'PASS','feed_multiplier':multiplier,'absorber_enabled':enabled,'native_iteration':base.native(s)}

def prepare(s):
 assert not (OUT/'build.json').exists()
 recovery=json.loads((PREVIOUS_OUT/'second-shutdown-recovery.json').read_text())
 parent=json.loads((PARENT_OUT/'build.json').read_text())
 for directory in ['scratch','monitors','autosaves']:base.ensure_remote_directory(s,str(WORK/directory))
 for k in ['case','data']:assert base.hash_remote(s,parent['prepared_pair'][k],'parent-'+k)==parent['prepared_pair'][k+'_sha256']
 assert base.hash_remote(s,absorber.LIB_ZIP,'library')==absorber.ZIP_SHA
 base.powershell(s,"$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath "+base.q(absorber.LIB_ZIP)+' -DestinationPath '+base.q(WORK)+' -Force')
 base.remote_chdir(s,str(WORK));base.load(s,parent['prepared_pair'])
 # Load verified library explicitly in this restarted session before activation.
 base.remote_chdir(s,str(WORK));s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
 switch(s,False);flow=base.feed(s,.25)
 definitions=copy.deepcopy(parent['report_definitions']);paths={name:str(WORK/'monitors'/(name+'.out')).replace('\\','/') for name in definitions}
 for name,path in paths.items():assert not base.remote_file_exists(s,path);s.settings.solution.monitor.report_files[name+'-rfile'].file_name=path
 s.settings.file.auto_save.set_state({'case_frequency':'each-time','data_frequency':100,'root_name':str(WORK/'autosaves/checkpoint').replace('\\','/'),'retain_most_recent_files':False,'append_file_name_with':{'file_suffix_type':'time-step','file_decimal_digit':6}})
 base.configure_residual_history(s,4000);s.settings.solution.initialization.hybrid_initialize();base.ensure_iteration_expression(s)
 reference=parent['matched_off_settings'];audit(s,.25,False,reference)
 pair=base.save(s,'prepared-step-OFF-N0');base.load(s,pair);assert base.native(s)==0
 pair['pre_save_expression_readback']=pair['native_iteration'];pair['native_iteration']=0;pair['executed_stage_iterations']=0
 b={'status':'PREPARED_REOPEN_VERIFIED','server_id':'2','mesh_cells':997604,'target_iteration':2200,'prepared_pair':pair,'parent_settings_pair':parent['prepared_pair'],'prior_failure_recovery':recovery,'initialization':'Fresh Hybrid at 25% feed, absorber OFF; no failed data retained','report_definitions':definitions,'report_paths':paths,'settings_reference':reference,'start_feed':flow,'absorber':parent['absorber'],'schedule':SCHEDULE,'enable_absorber_at_iteration':200}
 paths_after_reload(s,b);b['audit']=audit(s,.25,False,reference);b['settings']=base.setup(s);base.dump(OUT/'build.json',b);print('SLOW_ENABLE_N0_PREPARED_REOPEN_VERIFIED',flush=True)

def run(s):
 assert not (OUT/'run-manifest.json').exists()
 b=json.loads((OUT/'build.json').read_text());base.remote_chdir(s,str(WORK));base.load(s,b.get('verification_pair',b['prepared_pair']));paths_after_reload(s,b);assert base.native(s)==b.get('pre_run_verification_updates',0);audit(s,.25,False,b['settings_reference'])
 m={'status':'RUNNING','server_id':'2','requested_total_iterations':2200,'verified_native_iteration':b.get('pre_run_verification_updates',0),'pre_run_verification_updates':b.get('pre_run_verification_updates',0),'segments':[],'checkpoints':[],'started_utc':base.now()};base.dump(OUT/'run-manifest.json',m)
 try:
  with SessionTranscriptCapture(s,stream_path=OUT/'raw/native-transcript.txt',echo=False) as capture:
   enabled=False
   for count,fraction in b['schedule']:
    begin=base.native(s)
    if begin==200 and not enabled:
     before=base.save(s,'pre-enable-N200');switch(s,True);assert base.native(s)==200
     on=audit(s,.25,True,b['settings_reference']);after=base.save(s,'post-enable-N200');paths_after_reload(s,b)
     m['activation']={'native_iteration':200,'before_pair':before,'after_pair':after,'audit':on};enabled=True
    feed=base.feed(s,fraction);audit(s,fraction,enabled,b['settings_reference']);paths_after_reload(s,b)
    m['active_segment']={'start':begin,'target':begin+count,'feed':feed,'absorber_enabled':enabled};base.dump(OUT/'run-manifest.json',m);print('SOLVE',begin,begin+count,fraction,'ABSORBER',enabled,flush=True)
    marker=capture.mark();s.tui.solve.iterate(count);capture.wait_until_quiet(quiet_seconds=.25,timeout_seconds=5);end=base.native(s);failed=bool(base.FAILURE_MARKER.search(capture.text_since(marker)))
    m['segments'].append({'start':begin,'end':end,'feed':feed,'absorber_enabled':enabled,'solver_failure_markers':failed})
    if failed or end!=begin+count:raise RuntimeError(f'Stopped N{end}; target {begin+count}; failure marker {failed}')
    if end in [200,700,950,1200,2200]:m['checkpoints'].append(base.save(s,f'checkpoint-N{end}'))
    m['verified_native_iteration']=end;base.dump(OUT/'run-manifest.json',m)
   assert base.native(s)==2200
   final=m['checkpoints'][-1];base.load(s,final);paths_after_reload(s,b);a=audit(s,1.,True,b['settings_reference'])
   histories={name:base.read_text(s,path) for name,path in b['report_paths'].items()};coverage={}
   for name,t in histories.items():
    ids={int(line.split()[0]) for line in t.splitlines() if line.strip() and line.split()[0].isdigit()};missing=sorted(set(range(210 if name=='p8-applied-absorber' else 10,2201,10))-ids);coverage[name]={'missing':missing,'samples':len(ids)};assert not missing,(name,missing)
   base.dump(OUT/'report-histories.json',histories);base.dump(OUT/'final-reopen.json',{'native_iteration':2200,'pair':final,'audit':a,'report_coverage':coverage})
   m.update(status='COMPLETE_VERIFIED_ANALYSIS_REQUIRED',final_pair=final,completed_utc=base.now());base.dump(OUT/'run-manifest.json',m)
 except Exception:
  m.update(status='EXECUTION_STOPPED_DIAGNOSIS_REQUIRED',error=traceback.format_exc(),stopped_utc=base.now())
  try:
   n=base.native(s);m['observed_native_iteration']=n;m['failed_pair_diagnostic_only']=base.save(s,f'failed-state-N{n}-diagnostic-only');base.dump(OUT/'report-histories.json',{name:base.read_text(s,path) for name,path in b['report_paths'].items() if base.remote_file_exists(s,path)})
  except Exception:m['preservation_error']=traceback.format_exc()
  base.dump(OUT/'run-manifest.json',m);raise

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'raw').mkdir(exist_ok=True);s=base.attach();{'prepare':prepare,'run':run}[sys.argv[1]](s)
