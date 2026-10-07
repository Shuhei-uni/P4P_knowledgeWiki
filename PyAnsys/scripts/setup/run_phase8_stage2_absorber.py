"""Matched full-feed absorber-ON contrast; 3000 updates on Server 2 only."""
from pathlib import Path
import sys,json,math,copy
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase8_stage2_full_feed as trial
from run_phase72a_contact_absorber import configure_bulk,LOWER_ZONE
from pyansys_fluent.ewf_absorber import define_expressions
base=trial.base
OFF_OUT=trial.OUT;OFF_WORK=trial.WORK
OUT=trial.BASE_OUT/'absorber3000';WORK=trial.BASE_WORK/'absorber3000'
trial.OUT=OUT;trial.WORK=WORK;base.OUT=OUT;base.WORK=WORK
LIB_ZIP=base.SHARED/'P4P-Fluent-Artifacts/Phase72A/ContactAbsorber/local20000/20261004T081120Z/contact-libraries.zip'
ZIP_SHA='446428fb0d41e98efb55454f30dff656c935d044cfb6229669c9dab05507be3e'
OFF_AUDIT=base.parity_audit

def audit(s,exact_flows=True):
 b=json.loads((OUT/'build.json').read_text()) if (OUT/'build.json').exists() else json.loads((OFF_OUT/'build.json').read_text())
 off=b.get('matched_off_settings',b['settings']);actual=base.setup(s)
 assert actual['methods']==off['methods'] and actual['controls']==off['controls']
 for key in set(off['setup'])-{'named_expressions','user_defined','cell_zone_conditions'}:assert actual['setup'][key]==off['setup'][key],key
 fixed_actual=copy.deepcopy(actual['setup']['cell_zone_conditions']);fixed_off=copy.deepcopy(off['setup']['cell_zone_conditions'])
 for fixed in [fixed_actual,fixed_off]:
  for cell in fixed['fluid'].values():
   for phase in cell['phase'].values():phase.pop('sources',None)
 assert fixed_actual==fixed_off,'non-source cell-zone settings changed'
 zones=actual['setup']['cell_zone_conditions']['fluid']
 for name,state in zones.items():
  for phase,value in state['phase'].items():
   allowed=name==LOWER_ZONE and phase in ['mixture','phase-2']
   assert bool(value['sources']['enable'])==allowed,(name,phase,value['sources']['enable'])
 z=s.settings.setup.cell_zone_conditions.fluid[LOWER_ZONE]
 assert z.phase['phase-2'].sources.terms['mass'].get_state()==[{'option':'udf','udf':'contact_mass_10us::libcontactv2'}]
 for term in ['k','epsilon']:
  assert z.phase['mixture'].sources.terms[term].get_state()==[{'option':'value','value':0.0}]
 for axis in 'xyz':assert z.phase['mixture'].sources.terms[axis+'-momentum'].get_state()==[{'option':'udf','udf':f'contact_{axis}_10us::libcontactv2'}]
 return {'matched_methods_controls_and_fixed_setup':'PASS','absorber_tau_s':1e-5,'hooks':z.get_state(),'native_iteration':base.native(s)}

def prepare(s):
 assert not (OUT/'build.json').exists()
 assert base.native(s) in [0,717]
 base.ensure_remote_directory(s,str(WORK/'scratch'));base.ensure_remote_directory(s,str(WORK/'monitors'));base.ensure_remote_directory(s,str(WORK/'autosaves'))
 off=json.loads((OFF_OUT/'build.json').read_text());parent=off['prepared_pair']
 for kind in ['case','data']:assert base.hash_remote(s,parent[kind],'absorber-parent-'+kind)==parent[kind+'_sha256']
 assert base.hash_remote(s,LIB_ZIP,'contact-library')==ZIP_SHA
 base.powershell(s,"$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath "+base.q(LIB_ZIP)+' -DestinationPath '+base.q(WORK)+' -Force')
 base.remote_chdir(s,str(WORK));base.load(s,parent);assert base.native(s)==0
 before=base.setup(s);assert before['methods']==off['settings']['methods'] and before['controls']==off['settings']['controls']
 assert before['setup']==off['settings']['setup']
 s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
 define_expressions(s,{'P71V2Sink':'0 [kg/m^3/s]','P71V2SinkK':'0 [kg/m/s^3]','P71V2SinkEpsilon':'0 [kg/m/s^4]',**{f'P71V2Sink{axis}':'0 [kg/m^2/s^2]' for axis in 'XYZ'},'P71V2Alpha':'Volumefraction(phase="phase-2")','P71V2AvailableVolume':f'VolumeInt(P71V2Alpha,["{LOWER_ZONE}"])'})
 z=s.settings.setup.cell_zone_conditions.fluid[LOWER_ZONE]
 # Disabled OFF sources retain obsolete expressions. Fluent activates the
 # flag before rejecting those expressions; replace every enabled term.
 for phase in ['phase-2','mixture']:
  try:z.phase[phase].sources.enable=True
  except RuntimeError:
   assert z.phase[phase].sources.enable()
 for term in ['k','epsilon']:
  z.phase['mixture'].sources.terms[term].set_state([{'option':'value','value':0.0}])
 hooks=configure_bulk(s,'10us','libcontactv2')
 definitions=copy.deepcopy(off['report_definitions']);paths={}
 name='p8-applied-absorber';volume=s.settings.solution.report_definitions.volume
 volume.create(name=name);volume[name].report_type='volume-sum';volume[name].field='phase-2-user-mass-source';volume[name].cell_zones=[LOWER_ZONE]
 volume[name].average_over=1;volume[name].per_selection=False
 definitions[name]={'kind':'volume-sum','state':volume[name].get_state(),'units':'kg/s','sign':'negative removes liquid'}
 files=s.settings.solution.monitor.report_files;files.create(name=name+'-rfile');files[name+'-rfile'].report_defs=[name];files[name+'-rfile'].frequency=10;files[name+'-rfile'].active=True
 for name in definitions:
  path=str(WORK/'monitors'/(name+'.out')).replace('\\','/');assert not base.remote_file_exists(s,path)
  files[name+'-rfile'].file_name=path;paths[name]=path
 # Native autosaves run inside large TUI batches; preserve all diagnostic files.
 autosave=s.settings.file.auto_save
 autosave.set_state({'case_frequency':'each-time','data_frequency':100,'root_name':str(WORK/'autosaves/checkpoint').replace('\\','/'),'retain_most_recent_files':False,'append_file_name_with':{'file_suffix_type':'time-step','file_decimal_digit':6}})
 assert autosave.data_frequency()==100 and not autosave.retain_most_recent_files()
 base.check_stage2_reports(s,definitions,paths)
 matched=audit(s);pair=base.save(s,'prepared-absorber-N0');base.load(s,pair);assert base.native(s)==0
 # Case/data reopen must retain the source library, functions and controls.
 reopened=audit(s);base.check_stage2_reports(s,definitions,paths)
 build={'status':'PREPARED_REOPEN_VERIFIED','server_id':'2','target_iteration':3000,'initialization':'Exact fresh full-feed OFF N0 case/data field; absorber added without solve or reinitialization','parent_settings_pair':parent,'prepared_pair':pair,'start_feed':off['start_feed'],'report_definitions':definitions,'report_paths':paths,'parity_audit':reopened,'settings':base.setup(s),'matched_off_settings':before,'mesh_cells':997604,'schedule':[[1000,1.0]]*3,'new_trial_budget':3000,'absorber':{'library':'libcontactv2','zip':str(LIB_ZIP),'zip_sha256':ZIP_SHA,'tau_s':1e-5,'lower_zone':LOWER_ZONE,'hooks':hooks,'native_source_report':'p8-applied-absorber','independent_removal':'p8-mass-phase2-lower / 1e-5 seconds','vapor_mass_source':False},'autosave':autosave.get_state()}
 base.dump(OUT/'build.json',build);print('ABSORBER_N0_REOPEN_VERIFIED_MATCHED_OFF_FIELD',flush=True)

# The bounded full-feed driver uses this source-aware matched audit.
base.parity_audit=audit
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);s=base.attach()
 if sys.argv[1]=='prepare':prepare(s)
 else:
  # Cortex stores report paths relative to its home directory on case write.
  base.remote_chdir(s,r'C:\Users\syok443')
  original_load=base.load
  def reopen_with_absolute_paths(session,pair):
   original_load(session,pair)
   b=json.loads((OUT/'build.json').read_text())
   for name,path in b['report_paths'].items():
    session.settings.solution.monitor.report_files[name+'-rfile'].file_name=path
   session.settings.file.auto_save.root_name=str(WORK/'autosaves/checkpoint').replace('\\','/')
   base.check_stage2_reports(session,b['report_definitions'],b['report_paths'])
   audit(session)
  base.load=reopen_with_absolute_paths
  trial.run(s)
