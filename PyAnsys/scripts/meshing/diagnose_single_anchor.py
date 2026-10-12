"""Preserve and inspect the current meshing candidate without repairing it."""
from build_single_inlet_family import *
s=connect();s.events.stop();logs=[]
s.transcript.register_callback(lambda text:logs.append(text));s.transcript.start()
path=WORK+'/anchor-rebuild-diagnostic.msh.h5'
if not remote_file_exists(s,path):s.meshing.File.WriteMesh(FileName=path)
u=s.meshing_utilities
print('before',u.get_free_faces_count(face_zone_name_pattern='*'),flush=True)
s.meshing.File.ReadMesh(FileName=path)
data=audit(s);save_json(OUT/'anchor-rebuild-diagnostic-reopened.json',data)
print(json.dumps(data),flush=True)
(OUT/'anchor-rebuild-diagnostic-transcript.txt').write_text(''.join(logs));s.transcript.stop()
