"""Load exact archived08b pair and native Replace Mesh on Server2; no solves."""
from pathlib import Path
import sys,json,copy,math,uuid
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase8_stage2_f2_simple as r
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
BASE_OUT=r.OUT;BASE_WORK=r.WORK
OUT=BASE_OUT/'08b-native997k';WORK=BASE_WORK/'08b-native997k'
r.OUT=OUT;r.WORK=WORK
CASE=r.SHARED/'P4P-Fluent-Artifacts/08b/TwoPhaseInletV2(Purnanto).cas.h5'
DATA=r.SHARED/'P4P-Fluent-Artifacts/08b/TwoPhaseInletV2(Purnanto)-25-10000.dat.h5'

def interaction(s):
 domain=next(d for d in s.rp_vars('domains') if d[0][2]=='interaction')
 return {'domain':domain,'compressibility':s.rp_vars('turb-compress-mod?'),'drag_modification':s.rp_vars('mp/modify-drag?')}

def snapshot(s):
 # RP variables contain tuples; stored JSON uses lists. Normalize containers.
 return json.loads(json.dumps({'settings':r.setup(s),'interaction':interaction(s),'reports':s.settings.solution.report_definitions.get_state(),'injection_names':s.settings.setup.models.discrete_phase.injections.get_object_names()}))

def field_metrics(s):
 defs=s.settings.solution.report_definitions;names=[]
 try:
  for name,kind,field,phase in [('p8-08b-tmp-liquid','volume-mass',None,'phase-2'),('p8-08b-tmp-vapor','volume-mass',None,'phase-1'),('p8-08b-tmp-alpha-min','volume-min','phase-2-vof','mixture'),('p8-08b-tmp-alpha-max','volume-max','phase-2-vof','mixture'),('p8-08b-tmp-speed-max','volume-max','velocity-magnitude','mixture')]:
   assert name not in defs.volume.get_object_names();defs.volume.create(name=name);v=defs.volume[name];names.append(name)
   v.report_type=kind;v.cell_zones=['fluid']
   if phase!='mixture':v.phase=phase
   if field:v.field=field
   v.create_report_file=False;v.create_report_plot=False
  iteration='p8-08b-tmp-iteration';assert iteration not in defs.single_valued_expression.get_object_names();defs.single_valued_expression.create(name=iteration);defs.single_valued_expression[iteration].definition='Iteration';names.append(iteration)
  values=defs.compute(report_defs=names)
  # Native compute receipt retained; all returned numeric field values finite.
  def numeric(x):
   if isinstance(x,(int,float)):assert math.isfinite(x),x
   elif isinstance(x,dict):
    for v in x.values():numeric(v)
   elif isinstance(x,(list,tuple)):
    for v in x:numeric(v)
  numeric(values)
  return values
 finally:
  for name in names:
   branch=defs.single_valued_expression if name=='p8-08b-tmp-iteration' else defs.volume
   if name in branch.get_object_names():branch.delete(name_list=[name])
  for branch in [s.settings.solution.monitor.report_files,s.settings.solution.monitor.report_plots]:
   extra=[name for name in branch.get_object_names() if name.startswith('p8-08b-tmp-')]
   if extra:branch.delete(name_list=extra)

def save(s,label):
 pair={k:str(WORK/(label+ext)) for k,ext in [('case','.cas.h5'),('data','.dat.h5')]}
 for path in pair.values():assert not r.remote_file_exists(s,path)
 s.settings.file.write_case(file_name=pair['case']);s.settings.file.write_data(file_name=pair['data'])
 for k in ['case','data']:pair[k+'_sha256']=r.hash_remote(s,pair[k],label+'-'+k)
 return pair

def inspect(s):
 assert not (OUT/'source-live.json').exists()
 for name in ['scratch','monitors']:r.ensure_remote_directory(s,str(WORK/name))
 old=json.loads((BASE_OUT/'step-enable2200/recovered-third-failure-run-manifest.json').read_text());assert old['status']=='EXECUTION_STOPPED_DIAGNOSIS_REQUIRED'
 pair=old['failed_pair_diagnostic_only'];assert r.native(s)==old['observed_native_iteration']==518
 for k in ['case','data']:assert r.hash_remote(s,pair[k],'preserved-old-'+k)==pair[k+'_sha256']
 r.dump(OUT/'prior-run-preserved.json',{'failed_pair':pair,'failed_iteration':518,'diagnostic_only':True,'solve_updates':0})
 identity=json.loads((OUT/'source-local-identity.json').read_text())
 for k,path in [('case',CASE),('data',DATA)]:assert r.hash_remote(s,path,'08b-'+k)==identity[k]['sha256']
 r.remote_chdir(s,str(WORK));s.settings.file.read_case(file_name=str(CASE))
 source=snapshot(s);source['case']=str(CASE);source['data']=str(DATA);source['identity']=identity
 r.dump(OUT/'source-live.json',source)
 if source['injection_names']:s.tui.file.write_injections(str(WORK/'source-08b-injections.inj'),*source['injection_names'],'()')
 print('SOURCE08B_CASE_LOADED_AND_SNAPSHOTTED',flush=True)

def target(s):
 source=json.loads((OUT/'source-live.json').read_text());assert list(source['settings']['setup']['cell_zone_conditions']['fluid'])==['fluid']
 mesh=next(x for x in json.loads((r.ROOT/'output/phase9-mesh-convergence/20261007/mesh-input-audit.json').read_text())['meshes'] if x['label']=='997k')
 assert r.hash_remote(s,r.MESH,'997k-mesh')==mesh['sha256']
 s.settings.file.read_mesh(file_name=str(r.MESH))
 from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest,SurfaceDataType
 import numpy as np
 xyz=np.asarray(s.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=['steamoutlet'],data_types=[SurfaceDataType.Vertices]))['steamoutlet'].vertices)
 height=float(xyz[:,1].mean());assert abs(height-6.261)<.01,'Target physical scale changed'
 walls=s.settings.setup.boundary_conditions.wall.get_object_names();merge=[name for name in walls if name!='bottom']
 assert set(merge)=={'wall','vessel-wall-wall-separator-purnanto','inlet-wall-1-wall-separator-purnanto','inlet-wall-2-wall-separator-purnanto','separator-purnanto:1'},merge
 s.settings.mesh.modify_zones.merge_zones(zone_names=merge)
 survivor=[name for name in s.settings.setup.boundary_conditions.wall.get_object_names() if name!='bottom'];assert len(survivor)==1
 if survivor[0]!='wall':s.settings.mesh.modify_zones.zone_name(zone_name=survivor[0],new_name='wall')
 s.settings.mesh.modify_zones.zone_name(zone_name='separator-purnanto',new_name='fluid')
 s.settings.mesh.modify_zones.zone_name(zone_name='interior--separator-purnanto',new_name='interior-fluid')
 for name in ['liquidinlet','steaminlet']:s.settings.mesh.modify_zones.zone_type(zone_names=[name],new_type='mass-flow-inlet')
 assert s.settings.setup.cell_zone_conditions.fluid.get_object_names()==['fluid']
 assert sorted(s.settings.setup.boundary_conditions.mass_flow_inlet.get_object_names())==['liquidinlet','steaminlet']
 s.settings.mesh.check();s.settings.mesh.size_info()
 legacy=WORK/'target-997604-08b-legacy.cas';assert not r.remote_file_exists(s,str(legacy))
 mode=s.settings.file.cff_files.get_state();s.settings.file.cff_files=False
 try:s.settings.file.write_case(file_name=str(legacy))
 finally:s.settings.file.cff_files=mode
 r.dump(OUT/'target-mapping.json',{'input':str(r.MESH),'sha256':mesh['sha256'],'cells':997604,'native_outlet_height_m':height,'scale_factor':1,'wall_union':merge,'zone_map':{'separator-purnanto':'fluid','interior--separator-purnanto':'interior-fluid'},'inlet_type':'mass-flow-inlet','legacy_case':str(legacy),'lower_absorber_partition':'Not added; original08b has one fluid zone'})
 print('TARGET997K_MATCHED_08B_NAMES_TYPES',flush=True)

def compare(s,source):
 actual=snapshot(s)
 def differences(a,b,path=''):
  if isinstance(a,dict) and isinstance(b,dict):
   return [d for k in sorted(set(a)|set(b)) for d in differences(a.get(k),b.get(k),path+'/'+str(k))]
  if a!=b:return [{'path':path,'source':a,'actual':b}]
  return []
 delta=differences({k:source[k] for k in actual},actual)
 if delta:r.dump(OUT/('settings-difference-'+uuid.uuid4().hex+'.json'),delta)
 assert actual['settings']==source['settings'],'08b settings differ after transfer/reopen'
 assert actual['interaction']==source['interaction'],'Native interaction domain changed'
 assert actual['injection_names']==source['injection_names'],'DPM injection inventory changed'
 assert actual['reports']==source['reports'],'Report definitions changed'
 return {'status':'EXACT_LOADED_08B_SETTINGS_MATCH','injections':len(actual['injection_names'])}

def repair_missing_injections(s,source):
 injections=s.settings.setup.models.discrete_phase.injections
 names=injections.get_object_names()
 if names==source['injection_names']:return
 record=OUT/'injection-import-repair.json'
 if not names:
  s.settings.file.read_injections(file_name=str(WORK/'source-08b-injections.inj'))
  actual=snapshot(s)
  r.dump(record,{'before_names':names,'after_names':actual['injection_names'],'source_names':source['injection_names'],'backup':str(WORK/'source-08b-injections.inj'),'actual_injection_state':actual['settings']['setup']['models']['discrete_phase']['injections']})
 else:
  proof=json.loads(record.read_text());assert proof['before_names']==[] and proof['after_names']==names
 expected=source['injection_names'];history=[]
 # Native import refreshes original objects and creates six collision copies.
 for _ in range(len(expected)):
  names=injections.get_object_names();extras=[n for n in names if n not in expected]
  if not extras:break
  assert all(names.count(n)==1 for n in expected)
  proof=json.loads(record.read_text());known=[n for n in proof['after_names'] if n not in expected]
  assert len(extras)<=len(known)==len(expected) and set(extras)<=set(known)
  injections.delete(name_list=[extras[0]])
  after=injections.get_object_names();assert len(after)==len(names)-1
  history.append({'deleted_import_copy':extras[0],'remaining_names':after})
 actual=snapshot(s)
 r.dump(OUT/'injection-collision-cleanup.json',{'bounded_import_count':len(expected),'history':history,'final_names':actual['injection_names']})
 assert actual['injection_names']==source['injection_names']

def restore_mesh_check_option(s,source):
 node=s.settings.setup.models.discrete_phase.numerics.high_res_tracking.quad_face_centroid_enabled
 value=source['settings']['setup']['models']['discrete_phase']['numerics']['high_res_tracking']['quad_face_centroid_enabled']
 old=node.get_state()
 if old!=value:
  node.set_state(value)
  r.dump(OUT/'mesh-check-option-restored.json',{'option':'DPM high_res_tracking.quad_face_centroid_enabled','source':value,'mesh_check_enabled':old,'restored':node.get_state(),'cause':'Native mesh check automatically enables tracking robustness on polyhedral cells'})

def transfer(s,resume_source=False,resume_mapped=False,resume_saved=False):
 source=json.loads((OUT/'source-live.json').read_text());mapping=json.loads((OUT/'target-mapping.json').read_text())
 r.remote_chdir(s,str(WORK))
 if resume_mapped or resume_saved:before=json.loads((OUT/'source-fields.json').read_text())
 else:
  if not resume_source:s.settings.file.read_case(file_name=str(CASE));s.settings.file.read_data(file_name=str(DATA))
  compare(s,source);before=field_metrics(s);r.dump(OUT/'source-fields.json',before)
  s.scheme.eval("(rpsetvar 'dynamesh/replace-mesh/partition-per-zone? #t)")
  s.settings.mesh.replace(file_name=mapping['legacy_case'],zones=False)
 if resume_saved:
  mapped=json.loads((OUT/'mapped-fields.json').read_text())
  diagnostic={k:str(WORK/('08b-on-997604-no-solve'+ext)) for k,ext in [('case','.cas.h5'),('data','.dat.h5')]}
  for k in ['case','data']:diagnostic[k+'_sha256']=r.hash_remote(s,diagnostic[k],'mesh-check-diagnostic-'+k)
  r.dump(OUT/'mesh-check-diagnostic-pair.json',diagnostic)
  restore_mesh_check_option(s,source);audit=compare(s,source)
  pair=save(s,'08b-on-997604-settings-restored-no-solve')
 else:
  repair_missing_injections(s,source)
  audit=compare(s,source);mapped=field_metrics(s);r.dump(OUT/'mapped-fields.json',mapped)
  s.settings.mesh.check();s.settings.mesh.size_info();restore_mesh_check_option(s,source);compare(s,source)
  pair=save(s,'08b-on-997604-no-solve')
 r.dump(OUT/'mapped-pair.json',pair)
 s.settings.file.read_case(file_name=pair['case']);s.settings.file.read_data(file_name=pair['data'])
 reopened=compare(s,source);fields=field_metrics(s);r.dump(OUT/'reopened-fields.json',fields)
 # Settings and reports remain original; relocate only output files/autosave before any future solve.
 redirected={}
 for name in s.settings.solution.monitor.report_files.get_object_names():
  node=s.settings.solution.monitor.report_files[name];old=node.file_name();new=str(WORK/'monitors'/(name+'.out')).replace('\\','/');node.file_name=new;redirected[name]={'old':old,'new':new}
 old_autosave=s.settings.file.auto_save.get_state();s.settings.file.auto_save.root_name=str(WORK/'checkpoint').replace('\\','/')
 ready=save(s,'08b-on-997604-ready-no-solve');s.settings.file.read_case(file_name=ready['case']);s.settings.file.read_data(file_name=ready['data']);compare(s,source)
 for name,paths in redirected.items():s.settings.solution.monitor.report_files[name].file_name=paths['new']
 s.settings.file.auto_save.root_name=str(WORK/'checkpoint').replace('\\','/')
 r.dump(OUT/'transfer-receipt.json',{'status':'LOADED_NATIVE_REPLACED_SAVE_REOPEN_VERIFIED_NO_SOLVES','server_id':'2','source_case':str(CASE),'source_data':str(DATA),'source_identity':source['identity'],'target_mesh':mapping,'audit':audit,'reopen_audit':reopened,'mapped_pair':pair,'ready_pair':ready,'fields_before':before,'fields_mapped':mapped,'fields_reopened':fields,'redirected_report_files':redirected,'source_autosave':old_autosave,'new_solve_iterations':0,'initialization':'None; native interpolation of archived08b data','field_limit':'Mesh interpolation need not preserve global liquid inventory; retained field is a transferred starting point'})
 print('08B_NATIVE997K_LOADED_VERIFIED_NO_SOLVES',flush=True)

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'raw').mkdir(exist_ok=True);s=r.attach()
 raw=OUT/'raw'/(sys.argv[1]+'-native.txt')
 if raw.exists():raw=OUT/'raw'/(sys.argv[1]+'-'+uuid.uuid4().hex+'-native.txt')
 with SessionTranscriptCapture(s,stream_path=raw,echo=False):{'inspect':inspect,'target':target,'transfer':transfer,'resume-source':lambda s:transfer(s,resume_source=True),'resume-mapped':lambda s:transfer(s,resume_mapped=True),'resume-saved':lambda s:transfer(s,resume_saved=True)}[sys.argv[1]](s)
