"""Preserve failed state and inspect N1000; no solve or solver changes."""
from pathlib import Path
import sys,json,traceback,base64,hashlib,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup'),str(ROOT/'scripts/inspection')]
import run_phase8_stage2_f2_simple as r
from pyansys_fluent.stage4_native import ensure_remote_directory
from export_phase8_storyline import camera
FIG=ROOT.parent/'Project/experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/figures'

def collect(s):
 m=json.loads((r.OUT/'host-run-manifest.json').read_text());p=r.OUT/'failure-inspection.json'
 receipt=json.loads(p.read_text()) if p.exists() else {'server_id':'2','solve_issued':False,'status':'INSPECTING'}
 receipt['live_iteration_before_inspection']=r.native(s);r.dump(p,receipt)
 raw=r.OUT/'raw/failure-report-histories.json'
 if not raw.exists():
  histories={name:r.read_text(s,path) for name,path in m['report_paths'].items()};r.dump(raw,histories)
  print('REPORTS_PRESERVED',len(histories),flush=True)
 if 'failed_pair' not in receipt and r.native(s)==1422:
  try:receipt['failed_pair']=r.save(s,'failed-state-N1422-diagnostic-only')
  except Exception:receipt['failed_save_error']=traceback.format_exc()
  r.dump(p,receipt)
 latest=m['checkpoints'][-1]
 for kind in ['case','data']:assert r.hash_remote(s,latest[kind],'inspect-N1000-'+kind)==latest[kind+'_sha256']
 r.load(s,latest);assert r.native(s)==1000
 receipt.update(checkpoint=latest,checkpoint_reopened_iteration=r.native(s),status='N1000_REOPEN_VERIFIED_DIAGNOSTICS_PENDING')
 r.dump(p,receipt);print('N1000_REOPEN_VERIFIED',flush=True)
 return receipt

def export(s,receipt):
 p=r.OUT/'failure-native-figures.json'
 record=json.loads(p.read_text()) if p.exists() else {'server_id':'2','solve_issued':False,'source_pair':receipt['checkpoint'],'native_iteration':1000,'figures':[]}
 assert r.native(s)==1000
 mapping=json.loads((r.OUT/'target-mapping.json').read_text())
 zones=mapping['mesh_audit']['face_zones'] if 'mesh_audit' in mapping else None
 # The native physical coordinate audit owns this value, in metres.
 def find(v):
  if isinstance(v,dict):
   if v.get('name')=='steaminlet' and 'bounds' in v:return v['bounds']
   for child in v.values():
    result=find(child)
    if result:return result
  if isinstance(v,list):
   for child in v:
    result=find(child)
    if result:return result
 bounds=find(mapping);assert bounds
 y=(bounds[0][1]+bounds[1][1])/2
 record['brief']={'question':'Where is liquid at N1000, and what circulation exists before the ramp fails?','source':'Saved and hash-verified N1000 at 25% feed','geometry':'997604 cells, native metres','planes':{'p8s2-vertical':{'method':'xy-plane','z':0.},'p8s2-inlet':{'method':'zx-plane','y':y}},'fields':['phase-2-vof','velocity-magnitude'],'liquid_range':[0,1],'claim_limit':'Pre-ramp unconverged state; no view of unsaved N1400 or exact onset cells'}
 g=s.settings.results.graphics;planes=s.settings.results.surfaces.plane_surface
 for name,state in record['brief']['planes'].items():
  if name not in planes.get_object_names():planes.create(name=name)
  planes[name].set_state(state)
 if 'p8s2-failure-scalar' not in g.contour.get_object_names():g.contour.create(name='p8s2-failure-scalar')
 c=g.contour['p8s2-failure-scalar'];remote=r.WORK/'figures/failure-N1000';ensure_remote_directory(s,str(remote));FIG.mkdir(parents=True,exist_ok=True)
 for field,label in [('phase-2-vof','liquid'),('velocity-magnitude','velocity')]:
  for plane,horizontal in [('p8s2-vertical',False),('p8s2-inlet',True)]:
   name='N1000-'+label+('-inlet' if horizontal else '-vertical')+'.png'
   if any(x['filename']==name for x in record['figures']):continue
   c.set_state({'field':field,'surfaces_list':[plane],'range_options':{'global_range':False,'auto_range':True},'options':{'filled':True,'node_values':True,'boundary_values':False,'contour_lines':False},'color_map':{'font_automatic':True,'font_size':.025,'width':8.}})
   c.range_options.compute();observed=c.range_options.get_state()
   limits=[0.,1.] if label=='liquid' else [0.,max(1.,math.ceil(observed['maximum']/5)*5.)]
   c.range_options.set_state({'global_range':False,'auto_range':False,'clip_to_range':False,'minimum':limits[0],'maximum':limits[1]})
   c.display();cam=camera(g,horizontal=horizontal)
   if horizontal:
    g.views.camera.target(xyz=[-.85,y,-.2]);g.views.camera.position(xyz=[-.85,y+10,-.2])
   g.picture.x_resolution=1600 if horizontal else 1200;g.picture.y_resolution=1200 if horizontal else 1600
   path=remote/name;assert not r.remote_file_exists(s,str(path));g.picture.save_picture(file_name=str(path))
   encoded=str(path)+'.base64.txt';r.powershell(s,'[IO.File]::WriteAllText('+r.q(encoded)+',[Convert]::ToBase64String([IO.File]::ReadAllBytes('+r.q(path)+')))')
   payload=base64.b64decode(r.read_text(s,encoded),validate=True);assert payload.startswith(b'\x89PNG\r\n\x1a\n');dest=FIG/name;assert not dest.exists();dest.write_bytes(payload)
   record['figures'].append({'filename':name,'local':str(dest),'remote':str(path),'sha256':hashlib.sha256(payload).hexdigest(),'field':field,'plane':plane,'range':limits,'observed_range':observed,'camera':cam,'graphics_state':c.get_state()});r.dump(p,record);print('EXPORTED',name,flush=True)
 record['status']='EXPORTED_AWAIT_VISUAL_QA';r.dump(p,record)

if __name__=='__main__':
 s=r.attach();receipt=collect(s);export(s,receipt)
