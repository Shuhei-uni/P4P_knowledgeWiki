"""Extract meeting geometry and axial fields from preserved Phase7b pairs; never solve."""
import sys,json,signal,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'setup'))
from prepare_phase07b_collector import connect,remote_file_exists
from export_phase07b_sections import export_sections,FIELDS
from ansys.fluent.core.field_data_interfaces import SurfaceFieldDataRequest,SurfaceDataType
BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'output/phase07b-meeting-20260922'
RUNS={'S100':'p7b-s100-20260921T160825Z','S20':'p7b-s020-20260920T221831Z','S40':'p7b-s040-20260921T013001Z','S60':'p7b-s060-resume-20260921T113238Z','S80':'p7b-s080-20260921T130348Z'}
def main():
 OUT.mkdir(exist_ok=True);r={'started_utc':datetime.now(timezone.utc).isoformat(),'iterations_issued':0,'cases':{},'steps':[]}
 def persist(): (OUT/'extraction.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 def timeout(*_):raise TimeoutError('Report API deadline; reconcile before retry')
 signal.signal(signal.SIGALRM,timeout)
 def step(name,fn,seconds=120):
  print(name,flush=True);r['steps'].append({'name':name,'status':'STARTED'});persist();signal.alarm(seconds)
  try:v=fn();r['steps'][-1]['status']='PASS';return v
  finally:signal.alarm(0);persist()
 try:
  s=step('connect',lambda:connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5),30)
  m=json.loads((BASE/'output'/RUNS['S100']/'manifest.json').read_text());restore=m['pairs']['n04000']
  counter=lambda:s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()
  assert counter()==4000
  for name,d in m['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==d
  assert all(remote_file_exists(s,restore.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
  r['restore_case']=restore
  s.transcript.start(file_name=str(OUT/'extraction.trn'),write_to_stdout=False)
  info=s.fields.field_info.get_surfaces_info();names=[n for n,v in info.items() if v['zone_type'] in ['wall','velocity-inlet','pressure-outlet']]
  g=step('native_boundary_geometry',lambda:s.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=names,data_types=[SurfaceDataType.Vertices,SurfaceDataType.FacesConnectivity])))
  gd=OUT/'geometry';gd.mkdir(exist_ok=False);idx={}
  for i,name in enumerate(names):
   a=g[name];sizes=np.array([len(f) for f in a.connectivity],dtype=np.int64);nodes=np.concatenate(a.connectivity).astype(np.int64);vertices=np.asarray(a.vertices)
   assert len(sizes)>0 and np.isfinite(vertices).all()
   filename=f'boundary-{i:02d}.npz';np.savez_compressed(gd/filename,vertices=vertices,face_sizes=sizes,connectivity=nodes)
   idx[name]={'file':filename,'zone_type':info[name]['zone_type'],'facets':len(sizes),'bounds':[vertices.min(axis=0).tolist(),vertices.max(axis=0).tolist()]}
  (gd/'index.json').write_text(json.dumps({'source_case':restore,'surfaces':idx,'method':'Native Fluent boundary vertices and face connectivity; no geometry invention'},indent=2)+'\n')
  for case,run in RUNS.items():
   m=json.loads((BASE/'output'/run/'manifest.json').read_text());n=4000 if case=='S100' else 5000;path=m['pairs']['n04000' if case=='S100' else 'final']
   assert all(remote_file_exists(s,path.replace('.cas.h5',ext)) for ext in ['.cas.h5','.dat.h5'])
   if case!='S100':step('load_'+case,lambda:s.settings.file.read_case_data(file_name=path),180)
   assert counter()==n and s.settings.setup.general.solver.time()=='steady'
   for name,d in m['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==d
   r['cases'][case]={'run':run,'case':path,'data':path.replace('.cas.h5','.dat.h5'),'iteration':n,'role':'recovery checkpoint' if case=='S100' else 'completed horizon','water_volume_readback':s.settings.setup.named_expressions['P7bWaterVolume'].get_value()};persist()
   sections={}
   for axis in ['x','z']:
    name='p7b-meeting-'+axis+'0';group=s.settings.results.surfaces.iso_surface
    assert name not in group.get_object_names();group.create(name=name);group[name].set_state({'field':axis+'-coordinate','iso_values':[0.]});sections[name]={axis+'_m':0.}
   step('export_axial_'+case,lambda:export_sections(s,sections,OUT/case),180)
   metadata=s.fields.field_info.get_scalar_fields_info();metadata={f:metadata[f] for f in FIELDS}
   assert all(v['domain']==('phase-2' if k.startswith('phase-2-') else 'mixture') for k,v in metadata.items())
   (OUT/case/'field-metadata.json').write_text(json.dumps(metadata,indent=2,default=str)+'\n')
   assert counter()==n
  step('restore_preserved_S100_N4000',lambda:s.settings.file.read_case_data(file_name=restore),180)
  assert counter()==4000;r['restored_iteration']=4000;r['status']='COMPLETE_NO_SOLVE_OR_CHECKPOINT_OVERWRITE';persist();s.transcript.stop();print(r['status'],flush=True)
 except Exception as e:
  r.update(status='EXTRACTION_ERROR_RECONCILE_BEFORE_RETRY',error=str(e));persist();(OUT/'error.txt').write_text(traceback.format_exc());raise
if __name__=='__main__':main()
