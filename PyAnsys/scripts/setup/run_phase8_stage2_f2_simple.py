"""Stage 2 F2 carrier: attach to Server 2 only; bounded N0--N5000 startup.

Use native Replace Mesh, verified parent settings, and a fresh low-feed field.
Never launch, exit, terminate, or restart Fluent. Keep intermediate pairs local.
"""
from pathlib import Path, PureWindowsPath
import argparse,base64,copy,functools,hashlib,json,math,re,sys,time,traceback,uuid
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup'),str(ROOT/'scripts/inspection')]
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists,remote_chdir,quote_scheme_string
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.stage4_native import ensure_remote_directory,remote_file_sha256,configure_residual_history
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from run_phase72a_stage3_server3 import powershell
from build_phase8_purnanto_parity_pilots import configure_purnanto_parity,audit as parity_audit,TARGET_LIQUID,TARGET_VAPOR
from run_phase8_parity_carrier import configure_reports,check_reports,dump,ITERATION_ROW,FAILURE_MARKER
from run_p7_e5_cz import create_lower_register
OUT=ROOT/'output/phase8-stage2/20261007'
WORK=PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase8\Stage2\20261007')
SHARED=PureWindowsPath(r'C:\Users\syok443\OneDrive - The University of Auckland')
MESH=SHARED/'2026 Sem 1/700/P4PCFD/CAD PurnantoV2/Separator-purnanto-997k.msh.h5'
SOURCE_LOCAL=Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase8/F2-26.81-N10000/final.cas.h5')
SOURCE=WORK/'source-F2-26p81-N10000.cas.h5'
EXPECTED_SOURCE='e31dbdf82b75966503b4a8b46dcd0d0cab31cb647092e0de5a88d5f83d37c0c0'
WALL_PARTS=['wall','vessel-wall-wall-separator-purnanto','inlet-wall-1-wall-separator-purnanto','inlet-wall-2-wall-separator-purnanto']

def attach():
 import ansys.fluent.core._grpc_services as low
 import ansys.fluent.core.services as high
 from ansys.fluent.core.utils.fluent_version import FluentVersion
 from ansys.fluent.core import config
 low._server_supports_v1=lambda channel:False
 high.create_service_factory=functools.partial(high.create_service_factory,product_version=FluentVersion.v252)
 config.check_health=False
 s=connect('2',start_transcript=False,tcp_timeout_seconds=5)
 assert '2025 R2' in str(s.get_fluent_version())
 return s

def check_stage2_reports(s,definitions,paths):
 def normalized(value):
  p=PureWindowsPath(re.sub(r'\\+',lambda m:'\\',str(value).replace('/','\\')))
  resolved=p if p.is_absolute() else PureWindowsPath(r'C:\Users\syok443')/p if p.parts and p.parts[0].casefold()=='documents' else WORK/p
  return str(resolved).casefold()
 for name,definition in definitions.items():
  kind=definition['kind']
  branch=s.settings.solution.report_definitions.flux if kind=='flux-massflow' else s.settings.solution.report_definitions.volume if kind in ['volume-mass','volume-integral','volume-sum'] else s.settings.solution.report_definitions.surface
  assert branch[name].get_state()['report_type']==kind
  state=s.settings.solution.monitor.report_files[name+'-rfile'].get_state()
  assert state['report_defs']==[name]
  assert state['active'] and int(state['frequency'])==10
  assert normalized(state['file_name'])==normalized(paths[name]),(name,state['file_name'],paths[name])

def now():return datetime.now(timezone.utc).isoformat()
def q(value):return "'"+str(value).replace("'","''")+"'"
def native(s):
 value=int(round(float(s.settings.setup.named_expressions['P8S2NativeIteration'].get_value())))
 proof=OUT/'iteration-coordinate-proof.json'
 offset=json.loads(proof.read_text())['expression_offset'] if proof.exists() else 0
 return value-offset

def ensure_iteration_expression(s):
 expr=s.settings.setup.named_expressions
 if 'P8S2NativeIteration' not in expr.get_object_names():expr.create(name='P8S2NativeIteration')
 expr['P8S2NativeIteration'].definition='Iteration'

def save(s,label):
 p=WORK/(label+'.cas.h5');d=WORK/(label+'.dat.h5')
 assert not remote_file_exists(s,str(p)) and not remote_file_exists(s,str(d))
 s.settings.file.write_case(file_name=str(p));s.settings.file.write_data(file_name=str(d))
 assert remote_file_exists(s,str(p)) and remote_file_exists(s,str(d))
 return {'case':str(p),'data':str(d),'native_iteration':native(s),'case_sha256':remote_file_sha256(s,str(p),str(WORK/'scratch'/(label+'-case.sha256'))),'data_sha256':remote_file_sha256(s,str(d),str(WORK/'scratch'/(label+'-data.sha256')))}
def load(s,pair):
 s.settings.file.read_case(file_name=pair['case']);s.settings.file.read_data(file_name=pair['data'])
def setup(s):return {'setup':s.settings.setup.get_state(),'methods':s.settings.solution.methods.get_state(),'controls':s.settings.solution.controls.get_state()}
def hash_remote(s,p,label):return remote_file_sha256(s,str(p),str(WORK/'scratch'/(label+'-'+uuid.uuid4().hex[:8]+'.sha256')))
def feed(s,m):
 bc=s.settings.setup.boundary_conditions.mass_flow_inlet
 expected={'liquidinlet':{'phase-1':0.0,'phase-2':TARGET_LIQUID*m},'steaminlet':{'phase-1':TARGET_VAPOR*m,'phase-2':0.0}}
 for zone,values in expected.items():
  for phase,value in values.items():
   node=bc[zone].phase[phase].momentum.mass_flow_rate
   node.value=value
   assert math.isclose(float(node.get_state()['value']),value,rel_tol=1e-12,abs_tol=1e-9)
 return {'multiplier':m,'flows_kg_s':expected}
def upload(s):
 ensure_remote_directory(s,str(WORK/'scratch'))
 if remote_file_exists(s,str(SOURCE)):
  assert hash_remote(s,SOURCE,'parent')==EXPECTED_SOURCE;return
 blob=SOURCE_LOCAL.read_bytes();assert hashlib.sha256(blob).hexdigest()==EXPECTED_SOURCE
 encoded=base64.b64encode(blob).decode('ascii');paths=[]
 for n,start in enumerate(range(0,len(encoded),262144)):
  p=WORK/'scratch'/f'parent-chunk-{n:03}.b64';paths.append(p)
  if not remote_file_exists(s,str(p)):
   # Base64 alphabet contains no Scheme string escapes. Verify final binary hash.
   payload=encoded[start:start+262144]
   s.scheme.eval('(with-output-to-file "'+quote_scheme_string(str(p).replace('\\','/'))+'" (lambda () (display "'+payload+'")))')
  if n%10==0:print('PARENT_UPLOAD_CHUNK',n,flush=True)
 cmd="$ErrorActionPreference='Stop'; $encoded=(Get-ChildItem -LiteralPath "+q(WORK/'scratch')+" -Filter 'parent-chunk-*.b64' | Sort-Object Name | ForEach-Object {[IO.File]::ReadAllText($_.FullName)}) -join ''; [IO.File]::WriteAllBytes("+q(SOURCE)+",[Convert]::FromBase64String($encoded))"
 powershell(s,cmd);assert hash_remote(s,SOURCE,'parent')==EXPECTED_SOURCE
 dump(OUT/'parent-transfer.json',{'source_local':str(SOURCE_LOCAL),'case':str(SOURCE),'sha256':EXPECTED_SOURCE,'data_loaded':False,'intent':'Settings-only parent; fresh Hybrid initialization after native replacement'})

def inspect_source(s):
 if s.settings.setup.models.is_active():
  if not s.settings.solution.run_calculation.iterate.is_active():raise RuntimeError('Server 2 contains a busy case; reconcile before replacement')
  if not (OUT/'server2-preservation.json').exists():dump(OUT/'server2-preservation.json',save(s,'server2-preserved-before-stage2'))
 upload(s);remote_chdir(s,str(WORK))
 s.settings.file.read_case(file_name=str(SOURCE))
 a=setup(s);dump(OUT/'source-settings.json',a)
 print('SOURCE_LOADED',list(a['setup']['boundary_conditions']),flush=True)
 return a

def prepare_target(s,source):
 expected=next(m for m in json.loads((ROOT/'output/phase9-mesh-convergence/20261007/mesh-input-audit.json').read_text())['meshes'] if m['label']=='997k')
 assert hash_remote(s,MESH,'target-input')==expected['sha256']
 s.settings.file.read_mesh(file_name=str(MESH))
 from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest,SurfaceDataType
 import numpy as np
 vertices=np.asarray(s.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=['steamoutlet'],data_types=[SurfaceDataType.Vertices]))['steamoutlet'].vertices)
 height=float(vertices[:,1].mean())
 if abs(height-6261)<10:scale=.001;s.settings.mesh.scale(x_scale=scale,y_scale=scale,z_scale=scale)
 elif abs(height-6.261)<.01:scale=1
 else:raise RuntimeError('Unknown physical scale')
 walls=s.settings.setup.boundary_conditions.wall
 parts=[p for p in WALL_PARTS if p in walls.get_object_names()]
 if len(parts)>1:
  ref=walls['wall'].get_state()
  for name in parts:
   value=copy.deepcopy(ref);value['name']=name;walls[name].set_state(value)
  s.settings.mesh.modify_zones.merge_zones(zone_names=parts)
  survivors=[n for n in parts if n in walls.get_object_names()];assert len(survivors)==1
  if survivors[0]!='wall':s.settings.mesh.modify_zones.zone_name(zone_name=survivors[0],new_name='wall')
 register,selection=create_lower_register(s)
 s.settings.mesh.modify_zones.sep_cell_zone_mark(cell_zone_name='separator-purnanto',register=register,move_faces=True)
 generated=[n for n in s.settings.setup.cell_zone_conditions.fluid.get_object_names() if n!='separator-purnanto'];assert len(generated)==1
 s.settings.mesh.modify_zones.zone_name(zone_name=generated[0],new_name='p71a-v2-virtual-outlet')
 mapped=WORK/'target-split.cas.h5';s.settings.file.write_case(file_name=str(mapped))
 # Native zone list captures zone IDs/types and adjacency for mapping below.
 from pyansys_fluent.remote_text import write_ascii_text_new
 inspector=WORK/'scratch/inspect_stage2_mesh_with_deps.py'
 if not remote_file_exists(s,str(inspector)):
  host_record=json.loads((OUT/'host-python.json').read_text())
  dependency_path=host_record.get('dependency_path')
  prefix=('import sys\nsys.path.insert(0, '+repr(str(dependency_path))+')\n') if dependency_path else ''
  write_ascii_text_new(s,str(inspector),prefix+(ROOT/'scripts/inspection/inspect_phase9_mesh_inputs.py').read_text())
 # A host Python is preferred for topology; verified present path is supplied by caller receipt.
 host=json.loads((OUT/'host-python.json').read_text())['path']
 topo_path=WORK/'scratch/target-topology.json';log=WORK/'scratch/target-topology.log'
 cmd="$ErrorActionPreference='Stop'; $text=(& "+q(host)+' '+q(inspector)+' --single-mesh '+q(mapped)+' --output '+q(topo_path)+" 2>&1 | Out-String); [IO.File]::WriteAllText("+q(log)+",$text,[Text.Encoding]::ASCII)"
 powershell(s,cmd)
 topology=json.loads(read_text(s,str(topo_path)));assert topology['cells']==997604
 zones={z['name']:z['id'] for z in topology['cell_zones']};lo,up=zones['p71a-v2-virtual-outlet'],zones['separator-purnanto']
 cross=[z for z in topology['face_zones'] if {z.get('c0'),z.get('c1')}=={lo,up}]
 source_bc=source['setup']['boundary_conditions'];entries={}
 source_topo=json.loads((OUT/'source-topology.json').read_text())
 sz={z['name']:z['id'] for z in source_topo['cell_zones']}
 source_cross=[z['name'] for z in source_topo['face_zones'] if {z.get('c0'),z.get('c1')}=={sz['separator-purnanto'],sz['p71a-v2-virtual-outlet']}]
 for branch in ['porous_jump','interior']:
  for name,state in source_bc.get(branch,{}).items():
   if name in source_cross:entries[name]=(branch,state)
 assert len(cross)==len(entries)==2,(cross,entries)
 clean=lambda st:{k:v for k,v in st.items() if k!='name'}
 assert len({json.dumps(clean(v[1]),sort_keys=True) for v in entries.values()})==1
 renames={}
 for z in topology['face_zones']:
  if z.get('c0')==lo and not z.get('c1'):
   if z['name'].startswith('wall') and z['name']!='bottom':renames[z['name']]='wall:004'
   elif z['name'].startswith('separator-purnanto:1'):renames[z['name']]='separator-purnanto:1:001'
  if z.get('c0')==lo and z.get('c1')==lo:renames[z['name']]='interior--separator-purnanto:013'
 for z,name in zip(sorted(cross,key=lambda x:x['name']),sorted(entries)):renames[z['name']]=name
 for old,new in renames.items():
  if old!=new:s.settings.mesh.modify_zones.zone_name(zone_name=old,new_name=new)
 s.settings.mesh.check();s.settings.mesh.size_info()
 legacy=WORK/'target-native-replacement.cas'
 s.settings.file.cff_files=False
 try:s.settings.file.write_case(file_name=str(legacy))
 finally:s.settings.file.cff_files=True
 record={'status':'TARGET_MAPPED','mesh_input':str(MESH),'input_sha256':expected['sha256'],'native_cells':topology['cells'],'native_outlet_height_before':height,'scale_applied':scale,'wall_union':parts,'lower_register':selection,'topology':topology,'renames':renames,'replacement_input':str(legacy)}
 dump(OUT/'target-mapping.json',record);return record

def prepare(s):
 if (OUT/'build.json').exists():raise RuntimeError('Existing build receipt; reconcile instead of rebuilding')
 source=json.loads((OUT/'source-settings.json').read_text()) if (OUT/'source-settings.json').exists() else inspect_source(s)
 upload(s)
 remote_chdir(s,str(WORK))
 target=prepare_target(s,source)
 s.settings.file.read_case(file_name=str(SOURCE))
 s.scheme.eval("(rpsetvar 'dynamesh/replace-mesh/partition-per-zone? #t)")
 s.settings.mesh.replace(file_name=target['replacement_input'],zones=False)
 actual=setup(s)
 for key in set(source['setup'])-{'boundary_conditions','cell_zone_conditions'}:
  assert actual['setup'][key]==source['setup'][key],f'Unexpected transferred setup difference: {key}'
 # Preserve full boundary states on physically mapped names, including passive entries.
 for branch in ['mass_flow_inlet','pressure_outlet','wall','porous_jump','interior']:
  for name,state in source['setup']['boundary_conditions'].get(branch,{}).items():
   obj=getattr(s.settings.setup.boundary_conditions,branch)
   assert name in obj.get_object_names(),f'Missing mapped boundary {branch}/{name}'
   obj[name].set_state(state)
 for name,state in source['setup']['cell_zone_conditions']['fluid'].items():s.settings.setup.cell_zone_conditions.fluid[name].set_state(state)
 # Selected SIMPLE parity numerics and historical inlet/outlet turbulence inputs.
 configure_purnanto_parity(s)
 monitor=s.settings.solution.monitor
 for branch in [monitor.report_files,monitor.report_plots]:
  names=branch.get_object_names()
  if names:branch.delete(name_list=names)
 for branch_name in s.settings.solution.report_definitions.child_names:
  obj=getattr(s.settings.solution.report_definitions,branch_name)
  if hasattr(obj,'get_object_names'):
   names=obj.get_object_names()
   if names:obj.delete(name_list=names)
 s.settings.file.auto_save.data_frequency=0
 ensure_remote_directory(s,str(WORK/'monitors'))
 definitions,paths=configure_reports(s,Path(str(WORK/'monitors')),create_local_directory=False)
 for name in s.settings.solution.monitor.residual.equations.get_object_names():s.settings.solution.monitor.residual.equations[name].check_convergence=False
 configure_residual_history(s,6000)
 start_feed=feed(s,.25)
 s.settings.solution.initialization.hybrid_initialize()
 ensure_iteration_expression(s)
 assert native(s) in [0,1]
 before=parity_audit(s,exact_flows=False);pair=save(s,'prepared-N0')
 load(s,pair);after=parity_audit(s,exact_flows=False);assert before==after
 check_stage2_reports(s,definitions,paths);assert native(s) in [0,1]
 record={'status':'PREPARED_REOPEN_VERIFIED','server_id':'2','version':str(s.get_fluent_version()),'parent_case':str(SOURCE),'parent_case_sha256':EXPECTED_SOURCE,'parent_data_loaded':False,'mesh':target,'initialization':'fresh Hybrid at 25% feed','prepared_pair':pair,'parity_audit':after,'start_feed':start_feed,'report_definitions':definitions,'report_paths':paths,'settings':setup(s),'target_iteration':5000,'schedule':[[1000,.25]]+[[100,.25+.75*i/10] for i in range(1,11)]+[[1000,1.0]]*3}
 dump(OUT/'build.json',record);print('PREPARED_REOPEN_VERIFIED_N0',flush=True)

def finalize_initialized(s):
 """Finish the already initialized, unrun child after counter inspection."""
 if (OUT/'build.json').exists():raise RuntimeError('Build already finalized')
 ensure_iteration_expression(s)
 assert native(s) in [0,1]
 before=parity_audit(s,exact_flows=False)
 assert math.isclose(before['summed_phase_flows_kg_s']['phase-1'],TARGET_VAPOR*.25,abs_tol=1e-8)
 assert math.isclose(before['summed_phase_flows_kg_s']['phase-2'],TARGET_LIQUID*.25,abs_tol=1e-8)
 definitions={};paths={}
 reports=s.settings.solution.report_definitions
 for branch_name in ['flux','volume','surface']:
  branch=getattr(reports,branch_name)
  for name in branch.get_object_names():
   if not name.startswith('p8-'):continue
   state=branch[name].get_state();definitions[name]={'kind':state['report_type'],'state':state}
 for name in s.settings.solution.monitor.report_files.get_object_names():
  state=s.settings.solution.monitor.report_files[name].get_state()
  if len(state['report_defs'])==1 and state['report_defs'][0] in definitions:
   paths[state['report_defs'][0]]=state['file_name']
 assert len(definitions)==len(paths)==17
 case=WORK/'prepared-N0.cas.h5';data=WORK/'prepared-N0.dat.h5'
 if remote_file_exists(s,str(case)):
  assert remote_file_exists(s,str(data))
  pair={'case':str(case),'data':str(data),'native_iteration':native(s),'case_sha256':hash_remote(s,case,'prepared-case-reconcile'),'data_sha256':hash_remote(s,data,'prepared-data-reconcile')}
 else:pair=save(s,'prepared-N0')
 pair['executed_stage_iterations']=0
 load(s,pair);after=parity_audit(s,exact_flows=False);assert before==after
 check_stage2_reports(s,definitions,paths)
 record={'status':'PREPARED_REOPEN_VERIFIED_COUNTER_PROBE_PENDING','server_id':'2','version':str(s.get_fluent_version()),'parent_case':str(SOURCE),'parent_case_sha256':EXPECTED_SOURCE,'parent_data_loaded':False,'mesh':json.loads((OUT/'target-mapping.json').read_text()),'initialization':'fresh Hybrid at 25% feed; no carrier solve updates yet','prepared_pair':pair,'parity_audit':after,'start_feed':{'multiplier':.25},'report_definitions':definitions,'report_paths':paths,'settings':setup(s),'target_iteration':5000,'schedule':[[1000,.25]]+[[100,.25+.75*i/10] for i in range(1,11)]+[[1000,1.0]]*3}
 dump(OUT/'build.json',record);print('PREPARED_REOPEN_VERIFIED_INITIALIZED',flush=True)

def counter_probe(s):
 """Ten authorized low-feed updates; establish coordinate mapping empirically."""
 if (OUT/'iteration-coordinate-proof.json').exists():raise RuntimeError('Coordinate probe already performed; no duplicate solve')
 b=json.loads((OUT/'build.json').read_text());load(s,b['prepared_pair'])
 check_stage2_reports(s,b['report_definitions'],b['report_paths'])
 assert not any(v['check_convergence'] for v in s.settings.solution.monitor.residual.equations.get_state().values())
 initial_raw=float(s.settings.setup.named_expressions['P8S2NativeIteration'].get_value())
 feed(s,.25)
 path=OUT/'raw/low-feed-verification-10.txt'
 dump(OUT/'probe-state.json',{'status':'RUNNING_10_WITHIN_BUDGET','requested_steps':10,'pre_solve_expression':initial_raw,'solve_issued':True})
 with SessionTranscriptCapture(s,stream_path=path,echo=False) as capture:
  marker=capture.mark();s.tui.solve.iterate(10);capture.wait_until_quiet(quiet_seconds=.25,timeout_seconds=5)
  text=capture.text_since(marker)
  rows=sorted(set(map(int,ITERATION_ROW.findall(text))))
  if FAILURE_MARKER.search(text):raise RuntimeError('Solver failure in bounded verification')
  assert len(rows)==10 and rows==list(range(rows[0],rows[0]+10)),rows
  actual_raw=float(s.settings.setup.named_expressions['P8S2NativeIteration'].get_value())
  report_coordinate_offset=rows[-1]-10
  expression_offset=int(round(actual_raw))-10
  proof={'status':'VERIFIED_10_UPDATES_WITHIN_5000','executed_stage_iterations':10,'pre_solve_expression':initial_raw,'post_solve_expression':actual_raw,'expression_offset':expression_offset,'report_coordinate_offset':report_coordinate_offset,'native_transcript_iterations':rows,'transcript':str(path),'cached_cortex_iteration':s.scheme.eval("(rpgetvar 'current-iteration)"),'coordinate_policy':'Retain raw solver/report coordinates; stage coordinate subtracts measured offset'}
  dump(OUT/'iteration-coordinate-proof.json',proof);assert native(s)==10
  pair=save(s,'verified-low-feed-N10');load(s,pair);assert native(s)==10
  b.update(status='PREPARED_REOPEN_VERIFIED',verification_pair=pair,pre_run_verification_updates=10,iteration_proof=proof,schedule=[[990,.25]]+[[100,.25+.75*i/10] for i in range(1,11)]+[[1000,1.0]]*3)
  dump(OUT/'build.json',b);dump(OUT/'probe-state.json',{'status':'COMPLETE_VERIFIED','executed_stage_iterations':10,'pair':pair})
 print('VERIFIED_10_UPDATES_COUNTED_WITHIN_BUDGET',flush=True)

def run(s):
 if (OUT/'run-manifest.json').exists():raise RuntimeError('Reconcile existing run before launch')
 build=json.loads((OUT/'build.json').read_text());load(s,build.get('verification_pair',build['prepared_pair']))
 initial=build.get('pre_run_verification_updates',0)
 assert native(s)==initial and s.settings.solution.run_calculation.iterate.is_active()
 m={'status':'RUNNING','server_id':'2','started_utc':now(),'requested_total_iterations':5000,'verified_native_iteration':initial,'pre_run_verification_updates':initial,'transcript_files':([build['iteration_proof']['transcript']] if initial else [])+[str(OUT/'raw/native-transcript.txt')],'report_paths':build['report_paths'],'checkpoints':[],'segments':[]}
 dump(OUT/'run-manifest.json',m)
 with SessionTranscriptCapture(s,stream_path=OUT/'raw/native-transcript.txt',echo=False) as capture:
  for steps,multiplier in build['schedule']:
   begin=native(s);assert begin+steps<=5000
   flows=feed(s,multiplier);marker=capture.mark();t=time.monotonic()
   m.update(active_segment={'start':begin,'target':begin+steps,'feed':flows,'command':f'/solve/iterate {steps}'},updated_utc=now());dump(OUT/'run-manifest.json',m)
   print('SOLVE',begin,'to',begin+steps,'feed',round(multiplier,6),flush=True)
   s.tui.solve.iterate(steps)
   capture.wait_until_quiet(quiet_seconds=.25,timeout_seconds=5)
   end=native(s);assert end==begin+steps,(end,begin+steps)
   transcript=capture.text_since(marker)
   segment={'start':begin,'end':end,'feed':flows,'wall_seconds':time.monotonic()-t,'solver_failure_markers':bool(FAILURE_MARKER.search(transcript))}
   m['segments'].append(segment);m.update(verified_native_iteration=end,updated_utc=now())
   if end in [1000,2000,3000,4000,5000]:m['checkpoints'].append(save(s,f'checkpoint-N{end}'))
   dump(OUT/'run-manifest.json',m)
   if segment['solver_failure_markers']:raise RuntimeError('Native solver failure marker; preserved checkpoint if available')
  final=m['checkpoints'][-1];load(s,final);assert native(s)==5000
  audit=parity_audit(s,exact_flows=True);check_stage2_reports(s,build['report_definitions'],build['report_paths'])
  histories={name:read_text(s,path) for name,path in build['report_paths'].items()}
  dump(OUT/'report-histories.json',histories)
  # Report rows occur every ten iterations; require full coverage of the budget.
  coverage={}
  for name,text in histories.items():
   offset=build.get('iteration_proof',{}).get('report_coordinate_offset',0)
   ids={int(line.split()[0])-offset for line in text.splitlines() if line.strip() and line.split()[0].isdigit()}
   missing=sorted(set(range(10,5001,10))-ids);coverage[name]={'samples':len(ids),'missing':missing};assert not missing,(name,missing[:10])
  dump(OUT/'final-reopen.json',{'pair':final,'native_iteration':native(s),'parity_audit':audit,'report_coverage':coverage})
  m.update(status='COMPLETE_VERIFIED_ANALYSIS_REQUIRED',completed_utc=now(),final_pair=final,final_reopen='PASS',report_coverage='PASS');dump(OUT/'run-manifest.json',m)
 print('COMPLETE_VERIFIED_N5000',flush=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['upload','inspect-source','prepare','finalize','counter-probe','run']);args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 s=attach()
 try:
  if args.action=='upload':upload(s)
  elif args.action=='inspect-source':inspect_source(s)
  elif args.action=='finalize':finalize_initialized(s)
  elif args.action=='counter-probe':counter_probe(s)
  elif args.action=='prepare':
   with SessionTranscriptCapture(s,stream_path=OUT/('raw/preparation-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.txt'),echo=False) as capture:
    prepare(s)
    capture.wait_until_quiet(quiet_seconds=.25,timeout_seconds=5)
  else:run(s)
 except Exception as exc:
  dump(OUT/(args.action+'-error.json'),{'status':'IMPLEMENTATION_OR_EXECUTION_ERROR','action':args.action,'error':str(exc),'traceback':traceback.format_exc(),'time':now()});raise
if __name__=='__main__':main()
