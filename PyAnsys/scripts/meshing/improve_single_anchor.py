"""Check a longer feature-preserving quality pass on the saved anchor."""
from build_single_inlet_family import *
s=connect();s.events.stop();logs=[]
s.transcript.register_callback(lambda text:logs.append(text));s.transcript.start()
s.meshing.ImproveVolumeMesh(CellQualityLimit=.3,QualityMethod='Orthogonal',
    VMImprovePreferences={'VIgnoreFeature':'no','VIQualityIterations':20,'VIQualityMinAngle':0})
path=WORK+'/anchor-long-pass.msh.h5'
if remote_file_exists(s,path):raise FileExistsError(path)
s.meshing.File.WriteMesh(FileName=path);s.meshing.File.ReadMesh(FileName=path)
data=audit(s);save_json(OUT/'anchor-long-pass-audit.json',data)
print(json.dumps(data['metrics']),flush=True)
(OUT/'anchor-long-pass-transcript.txt').write_text(''.join(logs));s.transcript.stop()
