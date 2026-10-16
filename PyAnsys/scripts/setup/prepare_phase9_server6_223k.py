"""Prepare the human-selected 223546-cell bottom-closed Phase9 mesh on Server6."""
from pathlib import Path, PureWindowsPath
import sys,json,time,copy,argparse,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from phase9_server6_slit_common import attach,run
from pyansys_fluent.common import remote_chdir
from pyansys_fluent.stage4_native import exclusive_writer_lock
OUT=ROOT/'output/phase9-server6-223k/20261015'

def connect():
 s=attach();run.OUT=OUT
 run.WORK=PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")'))/'Documents/FluentRuns/Phase9-Server6-223k/20261015'
 run.require_idle(s)
 if s.settings.solution.run_calculation.iterating():raise RuntimeError('Server6 is solving')
 run.ensure_remote_directory(s,str(run.WORK/'223k/scratch'))
 return s

def inspect(s):
 audit=json.loads((OUT/'input-audit.json').read_text())
 mesh=run.SHARED/'2026 Sem 2/700/Purnanto-new/thin-inner-thick-outer/purnanto-separator(bottomrings)-223k.msh.h5'
 digest=run.remote_file_sha256(s,str(mesh),str(run.WORK/'223k/scratch/input.sha256'))
 if digest!=audit['sha256']:raise RuntimeError('Server6 mesh hash differs')
 run.dump(OUT/'replaced-session.json',{'iteration':run.native_iteration(s),'film':run.film(s),'save_waived_by_user':True,'setup':s.settings.setup.get_state()})
 with run.client_capture(s,OUT/('target-inspection-'+str(time.time_ns())+'.txt')):
  s.settings.file.read_mesh(file_name=str(mesh))
  s.settings.mesh.check();s.settings.mesh.size_info();s.tui.mesh.modify_zones.list_zones()
  run.dump(OUT/'target-live.json',{'mesh':str(mesh),'sha256':digest,'boundaries':s.settings.setup.boundary_conditions.get_state(),'cell_zones':s.settings.setup.cell_zone_conditions.get_state(),'zone_type_args':s.settings.mesh.modify_zones.zone_type.argument_names})
 print('TARGET_LOADED_INSPECTED',flush=True)

def map_mesh(s, resume=False):
 raise RuntimeError('Old legacy-case writer disabled for 223k; use convert and validate-ascii')

def close_bottoms(s,audit,bottoms):
 with run.client_capture(s,OUT/('bottom-map-'+str(time.time_ns())+'.txt')):
  outlets=s.settings.setup.boundary_conditions.pressure_outlet.get_object_names()
  to_wall=[n for n in bottoms if n in outlets]
  s.settings.mesh.modify_zones.zone_type(zone_names=to_wall,new_type='wall')
  walls=s.settings.setup.boundary_conditions.wall
  reference=walls['bottom'].get_state()
  for name in bottoms:
   item=copy.deepcopy(reference);item['name']=name;walls[name].set_state(item)
  s.settings.mesh.modify_zones.merge_zones(zone_names=bottoms)
  survivors=[n for n in bottoms if n in s.settings.setup.boundary_conditions.wall.get_object_names()]
  if len(survivors)!=1:raise RuntimeError('Bottom merge incomplete')
  if survivors[0]!='bottom':s.settings.mesh.modify_zones.zone_name(zone_name=survivors[0],new_name='bottom')
  run.dump(OUT/'bottom-map.json',{'original_bottoms':bottoms,'converted_pressure_outlets':to_wall,'merged_as':'bottom','basis':'All five boundary coordinate bounds lie at y=0; copy original bottom wall state'})
def recover_legacy(s):
 """Validate the completed legacy input; never repeat the stalled writer."""
 folder=run.WORK/'223k';legacy=folder/'mapped-target.cas'
 if not run.remote_file_exists(s,str(legacy)):raise FileNotFoundError(str(legacy))
 old=json.loads((ROOT/'output/phase9-server6-slit154k/20261010/host-launch.json').read_text())
 run.HOST_PYTHON=PureWindowsPath(old['host_python'])
 with run.client_capture(s,OUT/('recover-legacy-'+str(time.time_ns())+'.txt')):
  s.settings.file.cff_files=True
  print('VALIDATING_EXISTING_LEGACY',str(legacy),flush=True)
  s.settings.file.read_case(file_name=str(legacy))
  s.settings.mesh.check();s.settings.mesh.size_info()
  walls=s.settings.setup.boundary_conditions.wall.get_object_names()
  expected={'wall','wall:004','bottom','separator-purnanto:1','separator-purnanto:1:001'}
  if set(walls)!=expected:raise RuntimeError('Recovered legacy wall map differs: '+str(walls))
  if s.settings.setup.boundary_conditions.pressure_outlet.get_object_names()!=['steamoutlet']:raise RuntimeError('Bottom pressure outlet remains')
  if set(s.settings.setup.cell_zone_conditions.fluid.get_object_names())!={'separator-purnanto','p71a-v2-virtual-outlet'}:raise RuntimeError('Collector map differs')
  snapshot=folder/('validated-mapped-'+str(time.time_ns())+'.cas.h5')
  s.settings.file.cff_files=True
  s.settings.file.write_case(file_name=str(snapshot))
  topo=run.remote_audit(s,snapshot,folder)
  if topo['cells']!=223546:raise RuntimeError('Recovered cell count differs')
  zones={z['name']:z['id'] for z in topo['cell_zones']}
  lo,up=zones['p71a-v2-virtual-outlet'],zones['separator-purnanto']
  cross=[z for z in topo['face_zones'] if {z.get('c0'),z.get('c1')}=={lo,up}]
  source=json.loads(run.source_receipt().read_text())['state']
  if {z['name'] for z in cross}!=set(source['readback']['entry_faces']):raise RuntimeError('Collector entry mapping differs')
  digest=run.remote_file_sha256(s,str(legacy),str(folder/'scratch/validated-legacy.sha256'))
  record={'status':'TARGET_MAPPED_EXISTING_LEGACY_REOPEN_VERIFIED','native_replacement_input':str(legacy),'sha256':digest,'topology':topo,'recovery_snapshot':str(snapshot),'scale_applied':1,'bottom_map':json.loads((OUT/'bottom-map.json').read_text()),'recovery':'Existing write validated by native reopen, mesh check, cell/zone/adjacency audit; stalled writer not replayed'}
  run.dump(OUT/'223k-mapped.json',record)
 print('EXISTING_LEGACY_VALIDATED',flush=True)

def convert_mesh(s):
 old=json.loads((ROOT/'output/phase9-server6-slit154k/20261010/host-launch.json').read_text())
 python=old['host_python'];folder=run.WORK/'223k'
 from deploy_phase9_server6_slit_ewf import quote
 tag=str(time.time_ns());script=run.WORK/('export-mesh-'+tag+'.py');ref=run.WORK/('reference-'+tag+'.json')
 run.write_ascii_text_new(s,str(script),(ROOT/'scripts/setup/export_phase9_223k_legacy_mesh.py').read_text())
 run.write_ascii_text_new(s,str(ref),(OUT/'source-template-audited.json').read_text())
 target=folder/('mapped-ascii-'+tag+'.msh');log=folder/('export-'+tag+'.log')
 code="$ErrorActionPreference='Continue'; $r=(& "+quote(python)+" -E "+quote(script)+" --source "+quote(folder/'split-target.cas.h5')+" --target "+quote(target)+" --reference "+quote(ref)+" 2>&1|Out-String); [IO.File]::WriteAllText("+quote(log)+",(@{return_code=$LASTEXITCODE;output=$r}|ConvertTo-Json),[Text.Encoding]::ASCII)"
 run.base.powershell(s,code)
 result=json.loads(run.read_text(s,str(log)));run.dump(OUT/'ascii-export-execution.json',result)
 if result['return_code']!=0:raise RuntimeError('Mesh export failed: '+result['output'])
 receipt=json.loads(run.read_text(s,str(target.with_suffix('.json'))));run.dump(OUT/'ascii-export.json',receipt)
 print('MESH_ONLY_ASCII_EXPORTED',str(target),flush=True)

def validate_ascii(s):
 record=json.loads((OUT/'ascii-export.json').read_text());target=record['target'];folder=run.WORK/'223k'
 old=json.loads((ROOT/'output/phase9-server6-slit154k/20261010/host-launch.json').read_text());run.HOST_PYTHON=PureWindowsPath(old['host_python'])
 with run.client_capture(s,OUT/('ascii-validation-'+str(time.time_ns())+'.txt')):
  s.settings.file.cff_files=True
  s.settings.file.read_mesh(file_name=target)
  s.settings.mesh.check();s.settings.mesh.size_info()
  if set(s.settings.setup.boundary_conditions.wall.get_object_names())!={'wall','wall:004','bottom','separator-purnanto:1','separator-purnanto:1:001'}:raise RuntimeError('ASCII wall map differs')
  if s.settings.setup.boundary_conditions.pressure_outlet.get_object_names()!=['steamoutlet']:raise RuntimeError('Unexpected pressure outlet')
  snapshot=folder/('validated-ascii-'+str(time.time_ns())+'.cas.h5');s.settings.file.write_case(file_name=str(snapshot))
  topo=run.remote_audit(s,snapshot,folder)
  if topo['cells']!=223546:raise RuntimeError('Native cell count differs')
  expected=record['face_zones'];clean=lambda z:{k:z[k] for k in ['name','id','minId','maxId','zoneType','c0','c1']}
  if sorted(map(clean,topo['face_zones']),key=lambda z:z['id'])!=sorted(map(clean,expected),key=lambda z:z['id']):raise RuntimeError('Native topology differs after ASCII conversion')
  original=run.remote_audit(s,folder/'split-target.cas.h5',folder)
  if topo['bounds']!=original['bounds']:raise RuntimeError('Native coordinates changed')
  for z in topo['face_zones']:
   parent=next(v for v in original['face_zones'] if v['id']==z['id'])
   if z.get('bounds')!=parent.get('bounds') or z.get('area_coordinate_units_squared')!=parent.get('area_coordinate_units_squared'):raise RuntimeError('Boundary geometry changed')
  run.dump(OUT/'223k-mapped.json',{'status':'TARGET_MAPPED_ASCII_NATIVE_VERIFIED','native_replacement_input':target,'sha256':record['sha256'],'topology':topo,'snapshot':str(snapshot),'scale_applied':1,'recovery':'Mesh-only ASCII export; original failed binary case write disabled; exact native topology, coordinates and boundary-area audit passed'})
 print('ASCII_INPUT_NATIVE_VERIFIED',flush=True)

def build(s):
 mapped=json.loads((OUT/'223k-mapped.json').read_text())
 if mapped['status']!='TARGET_MAPPED_ASCII_NATIVE_VERIFIED':raise RuntimeError('Require verified mesh-only ASCII replacement input')
 if not s.settings.file.cff_files.get_state():raise RuntimeError('Restore CFF output mode before build')
 old=json.loads((ROOT/'output/phase9-server6-slit154k/20261010/host-launch.json').read_text())
 run.HOST_PYTHON=PureWindowsPath(old['host_python'])
 # Original non-stripping A parent is required for robust native interpolation.
 run.PARENT=run.SHARED/'P4P-Fluent-Artifacts/Phase72A/Stage3/early-ewf-startup/prepared-A-N1580/prepared-A-N1580'
 for key,ext in [('case','cas.h5'),('data','dat.h5')]:
  digest=run.remote_file_sha256(s,str(run.PARENT)+'.'+ext,str(run.WORK/'223k/scratch'/('transfer-parent-'+key+'.sha256')))
  if digest!=run.previous.PARENT_HASHES[key]:raise RuntimeError('Transfer parent hash differs')
 archive=run.SHARED/'P4P-Fluent-Artifacts/Phase72A/ContactAbsorber/local20000/20261004T081120Z/contact-libraries.zip'
 digest=run.remote_file_sha256(s,str(archive),str(run.WORK/'223k/scratch/udf.sha256'))
 if digest!=run.base.HASHES['contact-libraries.zip']:raise RuntimeError('UDF archive hash differs')
 code="$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath '"+str(archive)+"' -DestinationPath '"+str(run.WORK)+"' -Force"
 if run.base.powershell(s,code) not in (0,None):raise RuntimeError('UDF extraction failed')
 child=run.prepare_child(s,'223k')
 run.dump(OUT/'build-review.json',{'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'review':'Reviewed existing v252 map_target/prepare_child and their dependency path. Server6 idle, previous save waived by human. Target hash and native extents checked; five y=0 bottoms closed/merged. Verified original N1580 pair and UDF hashes. Native replacement, injection inventory repair, settings/field audit and paired reopen required. Build step submits no solve.','status':child['status']})
 print('PHASE9_223K_PREPARED',child['pair'],flush=True)

def audit_settings(s):
 source=json.loads((OUT/'source-template-audited.json').read_text())['state']
 child=json.loads((OUT/'223k-prepared-audited.json').read_text())['state']
 def diff(a,b,path=''):
  if isinstance(a,dict) and isinstance(b,dict):
   return sum((diff(a.get(k),b.get(k),path+'/'+k) for k in sorted(set(a)|set(b))),[])
  return [] if a==b else [{'path':path,'reference':a,'child':b}]
 differences=diff(source['setup'],child['setup'])
 checks={'complete_setup_including_boundaries_and_cell_zones':not differences,'methods':source['methods']==child['methods'],'film_model':source['film_model']==child['film_model']}
 for key in ['hooks','lower_film_wall','entry_faces','dpm','film_parameters','controls']:checks[key]=source['readback'][key]==child['readback'][key]
 names=s.settings.setup.models.discrete_phase.injections.get_object_names()
 reference_names=list(source['setup']['models']['discrete_phase']['injections'])
 checks['injection_inventory_no_duplicates']=len(names)==len(set(names))==len(reference_names) and set(names)==set(reference_names)
 selected=json.loads((OUT/'raw/provisional-stage4-selection.json').read_text())
 checks['pseudo_time_settings']=s.settings.solution.run_calculation.pseudo_time_settings.get_state()==selected['run_controls']['pseudo_time_settings']
 run.assert_bulk_active(s);feed=run.read_feed(s,.25);run.require_bulk_audit(s)
 result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'differences':differences,'feed':feed,'injections':names,'iteration':run.native_iteration(s),'reference':'source-template-audited.json','child':'223k-prepared-audited.json'}
 run.dump(OUT/'settings-match.json',result)
 print('COMPLETE_SETTINGS_AUDIT',json.dumps(result),flush=True)
 if result['status']!='PASS':raise RuntimeError('Complete template settings comparison failed')
 origin=ROOT/'output/phase9-mesh-convergence/20261007/08b-settings-audit-approved.json'
 approval=json.loads(origin.read_text());approval.update(status='APPLIED_REOPEN_VERIFIED',child='223k',proof='settings-match.json',source_approval=str(origin));run.dump(OUT/'08b-settings-audit-approved.json',approval)

def startup(s):
 import traceback
 try:
  if not (OUT/'settings-match.json').exists() or json.loads((OUT/'settings-match.json').read_text())['status']!='PASS':raise RuntimeError('Complete exact template audit before run')
  result=run.run_child(s,'223k',smoke_only=False)
  run.dump(OUT/'startup-complete.json',{'status':result['status'],'pair':result['final_pair'],'iteration':result['verified_native_end'],'film':result['final_film'],'final_feed':result['final_feed'],'final_equations':result['final_equations']})
 except BaseException:
  error={'status':'RECOVERY_REQUIRED','error':traceback.format_exc()}
  try:error['preserved_pair']=run.save(s,run.WORK/'223k','startup-failure-'+str(time.time_ns()))
  except BaseException:error['preservation_error']=traceback.format_exc()
  run.dump(OUT/'startup-failure.json',error);raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('step',choices=['inspect','map','map-resume','recover-legacy','build','smoke','convert','validate-ascii','run','audit']);a=p.parse_args()
 with exclusive_writer_lock(OUT/'controller.lock'):
  s=connect()
  {'inspect':inspect,'map':map_mesh,'map-resume':lambda s:map_mesh(s,resume=True),'recover-legacy':recover_legacy,'build':build,'audit':audit_settings,'run':startup,'convert':convert_mesh,'validate-ascii':validate_ascii,'smoke':lambda s:run.run_child(s,'223k',smoke_only=True)}[a.step](s)
