"""08b settings on supplied997k: Server2, N10000->12000, absorberOFF."""
from pathlib import Path
import sys,json,math,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
import transfer_phase8_08b_native997k as transfer
t=transfer;r=t.r
PARENT_OUT=t.OUT;PARENT_WORK=t.WORK
OUT=PARENT_OUT/'run2000-off';WORK=PARENT_WORK/'run2000-off'
t.OUT=OUT;t.WORK=WORK;r.OUT=OUT;r.WORK=WORK
START=10000;TARGET=12000
ITERATION='P8BRunIteration'
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture

def native(s):return int(round(float(s.settings.setup.named_expressions[ITERATION].get_value())))
def fields(s):return t.field_metrics(s)
def snapshot(s):return t.snapshot(s)
def pair(s,label):
 p=t.save(s,label);p['native_iteration']=native(s);return p

def audit(s,reference):
 actual=snapshot(s)
 assert actual==reference,'Instrumented08b settings/reports changed'
 assert list(actual['settings']['setup']['cell_zone_conditions']['fluid'])==['fluid']
 for cell in actual['settings']['setup']['cell_zone_conditions']['fluid'].values():
  for phase in cell['phase'].values():assert not phase['sources']['enable'],'Absorber/cell source active'
 assert actual['settings']['methods']['p_v_coupling']['flow_scheme']=='SIMPLE'
 assert len(actual['injection_names'])==6
 return {'fixed_08b_settings':'PASS','absorber_enabled':False,'native_iteration':native(s),'DPM_injections':6}

def paths(s,b):
 for name,path in b['report_paths'].items():
  node=s.settings.solution.monitor.report_files[name+'-rfile'];node.file_name=path
  state=node.get_state();assert state['active'] and state['frequency']==10 and state['report_defs']==[name]
 s.settings.file.auto_save.root_name=str(WORK/'autosaves/checkpoint').replace('\\','/')

def reports(s):
 defs=s.settings.solution.report_definitions;definitions={};report_paths={}
 for phase in ['phase-1','phase-2','mixture']:
  for boundary in ['liquidinlet','steaminlet','steamoutlet']:
   name='p8b-flux-'+phase.replace('-','')+'-'+boundary
   assert name not in defs.flux.get_object_names();defs.flux.create(name=name)
   v=defs.flux[name];v.report_type='flux-massflow';v.boundaries=[boundary];v.phase=phase;v.average_over=1;v.per_selection=False;v.create_report_file=False;v.create_report_plot=False
   definitions[name]={'kind':'flux-massflow','phase':phase,'boundary':boundary,'fluent_sign':'positive into domain','units':'kg/s','state':v.get_state()}
 for name,kind,field,phase in [('p8b-liquid-mass','volume-mass',None,'phase-2'),('p8b-vapor-mass','volume-mass',None,'phase-1'),('p8b-alpha-min','volume-min','phase-2-vof','mixture'),('p8b-alpha-max','volume-max','phase-2-vof','mixture'),('p8b-speed-max','volume-max','velocity-magnitude','mixture')]:
  assert name not in defs.volume.get_object_names();defs.volume.create(name=name)
  v=defs.volume[name];v.report_type=kind;v.cell_zones=['fluid'];v.average_over=1;v.per_selection=False
  if phase!='mixture':v.phase=phase
  if field:v.field=field
  v.create_report_file=False;v.create_report_plot=False
  definitions[name]={'kind':kind,'phase':phase,'field':field,'state':v.get_state()}
 for boundary in ['liquidinlet','steaminlet','steamoutlet']:
  name='p8b-pressure-'+boundary;assert name not in defs.surface.get_object_names();defs.surface.create(name=name)
  v=defs.surface[name];v.report_type='surface-areaavg';v.field='pressure';v.surface_names=[boundary];v.average_over=1;v.per_surface=False;v.create_report_file=False;v.create_report_plot=False
  definitions[name]={'kind':'surface-areaavg','boundary':boundary,'units':'Pa','state':v.get_state()}
 for name in definitions:
  path=str(WORK/'monitors'/(name+'.out')).replace('\\','/');assert not r.remote_file_exists(s,path)
  branch=s.settings.solution.monitor.report_files;branch.create(name=name+'-rfile');branch[name+'-rfile'].set_state({'file_name':path,'report_defs':[name],'frequency':10,'active':True});report_paths[name]=path
 return definitions,report_paths

def prepare(s):
 assert not (OUT/'build.json').exists()
 for folder in ['scratch','monitors','autosaves']:r.ensure_remote_directory(s,str(WORK/folder))
 parent=json.loads((PARENT_OUT/'transfer-receipt.json').read_text());source=json.loads((PARENT_OUT/'source-live.json').read_text())
 t.compare(s,source)
 for kind in ['case','data']:assert r.hash_remote(s,parent['ready_pair'][kind],'parent-'+kind)==parent['ready_pair'][kind+'_sha256']
 before=fields(s);assert next(x['p8-08b-tmp-iteration'][0] for x in before if 'p8-08b-tmp-iteration' in x)==START
 r.remote_chdir(s,str(WORK))
 expr=s.settings.setup.named_expressions;assert ITERATION not in expr.get_object_names();expr.create(name=ITERATION);expr[ITERATION].definition='Iteration';assert native(s)==START
 definitions,report_paths=reports(s)
 residual_before=s.settings.solution.monitor.residual.get_state();r.configure_residual_history(s,13000)
 for name in s.settings.solution.monitor.residual.equations.get_object_names():s.settings.solution.monitor.residual.equations[name].check_convergence=False
 s.settings.file.auto_save.set_state({'case_frequency':'each-time','data_frequency':100,'root_name':str(WORK/'autosaves/checkpoint').replace('\\','/'),'retain_most_recent_files':False,'append_file_name_with':{'file_suffix_type':'time-step','file_decimal_digit':6}})
 reference=snapshot(s);start_pair=pair(s,'prepared-N10000-off')
 s.settings.file.read_case(file_name=start_pair['case']);s.settings.file.read_data(file_name=start_pair['data'])
 b={'status':'PREPARED_REOPEN_VERIFIED','server_id':'2','cells':997604,'start_iteration':START,'target_iteration':TARGET,'additional_iterations':2000,'parent_pair':parent['ready_pair'],'prepared_pair':start_pair,'reference':reference,'report_definitions':definitions,'report_paths':report_paths,'residual_before':residual_before,'residual_after':s.settings.solution.monitor.residual.get_state(),'initial_fields':before,'absorber_enabled':False,'initialization':'None; continue transferred08b fields','allowed_changes':'Reports/iteration expression, residual history/stop checks and local autosave/output paths only','batches':[1000,1000]}
 paths(s,b);b['audit']=audit(s,reference);assert native(s)==START
 r.dump(OUT/'build.json',b);print('PREPARED08B_SETTINGS_NEW997K_N10000_OFF',flush=True)

def run(s):
 assert not (OUT/'run-manifest.json').exists()
 b=json.loads((OUT/'build.json').read_text());r.remote_chdir(s,str(WORK));paths(s,b);audit(s,b['reference']);assert native(s)==START
 m={'status':'RUNNING','server_id':'2','start_iteration':START,'target_iteration':TARGET,'additional_iterations':2000,'verified_native_iteration':START,'absorber_enabled':False,'segments':[],'checkpoints':[],'started_utc':r.now()};r.dump(OUT/'run-manifest.json',m)
 try:
  with SessionTranscriptCapture(s,stream_path=OUT/'raw/native-transcript.txt',echo=False) as capture:
   for count in b['batches']:
    begin=native(s);audit(s,b['reference']);m['active_segment']={'start':begin,'target':begin+count};r.dump(OUT/'run-manifest.json',m);print('SOLVE',begin,begin+count,'ABSORBER_OFF',flush=True)
    marker=capture.mark();s.tui.solve.iterate(count);capture.wait_until_quiet(quiet_seconds=.25,timeout_seconds=5)
    end=native(s);failed=bool(r.FAILURE_MARKER.search(capture.text_since(marker)));m['segments'].append({'start':begin,'end':end,'absorber_enabled':False,'failure_marker':failed});m['observed_native_iteration']=end
    if failed or end!=begin+count:raise RuntimeError(f'Stopped N{end}, expected{begin+count}, solver failure marker{failed}')
    m['checkpoints'].append(pair(s,f'checkpoint-N{end}-off'));m['verified_native_iteration']=end;r.dump(OUT/'run-manifest.json',m)
   assert native(s)==TARGET
   final=m['checkpoints'][-1];before=fields(s);s.settings.file.read_case(file_name=final['case']);s.settings.file.read_data(file_name=final['data']);paths(s,b);a=audit(s,b['reference']);after=fields(s)
   def flat(x):return {k:v[0] for row in x for k,v in row.items()}
   for k,val in flat(before).items():assert math.isclose(val,flat(after)[k],rel_tol=1e-9,abs_tol=1e-10),(k,val,flat(after)[k])
   histories={name:r.read_text(s,path) for name,path in b['report_paths'].items()};coverage={}
   for name,txt in histories.items():
    ids={int(line.split()[0]) for line in txt.splitlines() if line.split() and line.split()[0].isdigit()};missing=sorted(set(range(START+10,TARGET+1,10))-ids);coverage[name]={'missing':missing,'samples':len(ids)};assert not missing,(name,missing)
   r.dump(OUT/'report-histories.json',histories);r.dump(OUT/'final-reopen.json',{'native_iteration':native(s),'pair':final,'audit':a,'fields_before_reopen':before,'fields_after_reopen':after,'report_coverage':coverage})
   m.update(status='COMPLETE_VERIFIED_ANALYSIS_REQUIRED',final_pair=final,completed_utc=r.now());r.dump(OUT/'run-manifest.json',m)
 except Exception:
  m.update(status='EXECUTION_STOPPED_DIAGNOSIS_REQUIRED',error=traceback.format_exc(),stopped_utc=r.now())
  try:
   n=native(s);m['observed_native_iteration']=n;m['failed_pair_diagnostic_only']=pair(s,f'failed-N{n}-diagnostic-only')
   r.dump(OUT/'report-histories.json',{name:r.read_text(s,path) for name,path in b['report_paths'].items() if r.remote_file_exists(s,path)})
  except Exception:m['preservation_error']=traceback.format_exc()
  r.dump(OUT/'run-manifest.json',m);raise

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'raw').mkdir(exist_ok=True);s=r.attach()
 if sys.argv[1]=='prepare':
  with SessionTranscriptCapture(s,stream_path=OUT/'raw/preparation-native.txt',echo=False):prepare(s)
 else:run(s)
