"""Restore full quality arguments and execute the native recovery command."""
from build_single_inlet_family import *

def main():
    rid='selected-fine-2';p=OUT/(rid+'-status.json');previous=json.loads(p.read_text())
    if previous['status']!='COMPLETE':raise RuntimeError('Expected preserved complete level')
    backup=OUT/(rid+'-before-quality-control-fix-status.json')
    if backup.exists():raise FileExistsError(backup)
    save_json(backup,previous)
    save_json(OUT/(rid+'-before-quality-control-fix-audit.json'),json.loads((OUT/(rid+'-reopened.json')).read_text()))
    r=dict(previous,status='RUNNING',stage='RESTORE EXPLICIT QUALITY CONTROLS')
    save_json(p,r)
    s=connect();s.events.stop();logs=[]
    transcript=OUT/(rid+'-control-fix-transcript.txt');transcript.write_text('')
    def capture(text):
        logs.append(text)
        with transcript.open('a') as f:f.write(text)
    s.transcript.register_callback(capture);s.transcript.start()
    def update(stage,**kw):
        r.update(stage=stage,**kw);save_json(p,r);print(stage,json.dumps(kw),flush=True)
    try:
        wf=previous['mesh'].removesuffix('.msh.h5')+'.wft'
        s.workflow.LoadWorkflow(FilePath=wf)
        s.meshing.File.ReadMesh(FileName=previous['mesh'])
        before=audit(s)
        if before['cell_count']!=previous['cells']:raise RuntimeError('Wrong preserved level')
        save_json(OUT/(rid+'-before-improve.json'),before)
        prefs={'VIQualityIterations':26,'VIgnoreFeature':'no','VIQualityMinAngle':0,
               'ShowVMImprovePreferences':False}
        quality={'QualityMethod':'Orthogonal','CellQualityLimit':.3,
                 'AddMultipleQualityMethods':'No','VMImprovePreferences':prefs}
        s.workflow.TaskObject['Improve Volume Mesh'].Arguments.set_state(quality)
        readback=plain(s.workflow.TaskObject['Improve Volume Mesh'].Arguments.get_state())
        save_json(OUT/(rid+'-explicit-quality-readback.json'),readback)
        if readback['CellQualityLimit']!=.3 or readback['QualityMethod']!='Orthogonal':
            raise RuntimeError('Quality readback differs')
        update('EXECUTE NATIVE RECOVERY QUALITY COMMAND')
        s.meshing.ImproveVolumeMesh(**quality)
        folder=WORK+'/fine2-quality-recovery'
        remote_ps(s,"New-Item -ItemType Directory -Path '"+folder+"' -Force | Out-Null")
        zones=list(s.meshing_utilities.get_cell_zones(filter='*'))
        count=s.meshing_utilities.get_cell_zone_count(cell_zone_id_list=zones)
        mesh=folder+'/Separator-purnanto-single-'+str(round(count/1000))+'k.msh.h5'
        if remote_file_exists(s,mesh):raise FileExistsError(mesh)
        update('SAVE AND REOPEN',mesh=mesh,cells=count)
        s.meshing.File.WriteMesh(FileName=mesh)
        s.workflow.SaveWorkflow(FilePath=mesh.removesuffix('.msh.h5')+'.wft')
        s.meshing.File.ReadMesh(FileName=mesh)
        after=audit(s)
        expected={b['name']:b['type'] for b in before['boundaries']}
        if {b['name']:b['type'] for b in after['boundaries']}!=expected:
            raise RuntimeError('Boundary names/types differ')
        if after['cell_count']!=count or after['free_faces'] or after['multi_faces'] or after['metrics']['Size'][1]<=0:
            raise RuntimeError('Saved-file audit failed')
        save_json(OUT/(rid+'-reopened.json'),after);save_json(OUT/(rid+'-audit.json'),after)
        update('COMPLETE',status='COMPLETE',mesh=mesh,cells=count,metrics=after['metrics'],
               recovery='Matching live volume preserved; full quality arguments restored; native command executed with iteration limit 26',
               quality_iteration_limit=26)
    except BaseException as e:
        update('FAILED',status='FAILED',error=str(e));raise
    finally:
        s.transcript.stop();transcript.write_text(''.join(logs))

if __name__=='__main__':main()
