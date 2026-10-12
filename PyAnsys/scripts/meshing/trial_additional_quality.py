"""Test a documented additional criterion on the preserved anchor."""
from build_single_inlet_family import *
s=connect();s.events.stop();logs=[]
s.transcript.register_callback(lambda text:logs.append(text));s.transcript.start()
try:
    result=s.meshing.ImproveVolumeMesh(QualityMethod='Orthogonal',CellQualityLimit=.3,
        AddMultipleQualityMethods='Yes',QualityMethodList=['Max Fluent Aspect Ratio'],QualityCriteriaList=['100'],
        VMImprovePreferences={'VIgnoreFeature':'no','VIQualityIterations':5,'VIQualityMinAngle':0})
    print('command result',result,flush=True)
    mesh=WORK+'/anchor-additional-quality-trial.msh.h5'
    if remote_file_exists(s,mesh):raise FileExistsError(mesh)
    s.meshing.File.WriteMesh(FileName=mesh);s.meshing.File.ReadMesh(FileName=mesh)
    data=audit(s);save_json(OUT/'anchor-additional-quality-trial.json',data)
    print(json.dumps(data['metrics']),flush=True)
finally:
    (OUT/'anchor-additional-quality-transcript.txt').write_text(''.join(logs));s.transcript.stop()
