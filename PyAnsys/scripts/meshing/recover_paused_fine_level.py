"""Preserve and verify the matching live finer mesh after a paused RPC worker."""
from build_single_inlet_family import *

def main():
    rid='selected-fine-2'
    statuspath=OUT/(rid+'-status.json')
    old=json.loads(statuspath.read_text())
    if old['status']!='FAILED':raise RuntimeError('Expected interrupted worker receipt')
    failure=OUT/(rid+'-pause-resume-failure.json')
    if failure.exists():raise FileExistsError(failure)
    save_json(failure,old)
    receipt={'id':rid,'scale':.65,'status':'RUNNING','stage':'RECOVERY CONNECT',
             'parent':'Separator-purnanto-single-733k.msh.h5','cad':CAD,
             'recovery':'Matching live volume preserved; quality task invoked with iteration limit 26',
             'quality_iteration_limit':26}
    save_json(statuspath,receipt)
    s=connect();s.events.stop();logs=[]
    transcript=OUT/(rid+'-recovery-transcript.txt')
    transcript.write_text('')
    def capture(text):
        logs.append(text)
        with transcript.open('a') as f:f.write(text)
    s.transcript.register_callback(capture);s.transcript.start()
    def update(stage,**kw):
        receipt.update(stage=stage,**kw);save_json(statuspath,receipt)
        print(stage,json.dumps(kw),flush=True)
    try:
        args={n:plain(s.workflow.TaskObject[n].Arguments.get_state()) for n in
              ['Import Geometry','facesize_1','Generate the Surface Mesh',
               'smooth-transition_1','Generate the Volume Mesh','Improve Volume Mesh']}
        save_json(OUT/(rid+'-recovery-readback.json'),args)
        if args['Import Geometry']['FileName']!=CAD:raise RuntimeError('Unexpected CAD')
        surf=args['Generate the Surface Mesh']['CFDSurfaceMeshControls']
        for k,v in {'CurvatureNormalAngle':6,'MaxSize':.0325,'MinSize':.0065}.items():
            if abs(surf[k]-v)>1e-12:raise RuntimeError('Unexpected surface control '+k)
        if abs(args['facesize_1']['BOISize']-.0325)>1e-12:raise RuntimeError('Unexpected outlet sizing')
        if abs(args['Generate the Volume Mesh']['VolumeFillControls']['HexMaxSize']-.052)>1e-12:
            raise RuntimeError('Unexpected hexcore size')
        layers=args['smooth-transition_1']
        if layers['NumberOfLayers']!=12 or abs(layers['Rate']-1.15)>1e-12:
            raise RuntimeError('Unexpected wall-layer controls')
        u=s.meshing_utilities;zones=list(u.get_cell_zones(filter='*'))
        if u.get_cell_zone_count(cell_zone_id_list=zones)!=1430497:
            raise RuntimeError('Matching live mesh changed before recovery')
        preserved=WORK+'/resume-preserved-fine2-1430k.msh.h5'
        if remote_file_exists(s,preserved):raise FileExistsError(preserved)
        update('PRESERVE RECOVERED VOLUME',preserved_mesh=preserved)
        s.meshing.File.WriteMesh(FileName=preserved)
        s.workflow.SaveWorkflow(FilePath=WORK+'/resume-preserved-fine2-1430k.wft')
        if not remote_file_exists(s,preserved):raise RuntimeError('Recovery preservation failed')
        before=audit(s);save_json(OUT/(rid+'-before-improve.json'),before)
        task=s.workflow.TaskObject['Improve Volume Mesh']
        prefs=dict(args['Improve Volume Mesh']['VMImprovePreferences'])
        prefs.update(VIQualityIterations=26,VIgnoreFeature='no')
        task.Arguments.set_state({'VMImprovePreferences':prefs})
        w=recipe(.65)
        for k,t in w['workflow']['ROOT'].items():
            if k.startswith('TaskObject:') and t['_name_']=='Improve Volume Mesh':
                t['Arguments']['VMImprovePreferences']['VIQualityIterations']=26
        save_json(OUT/(rid+'-recipe.json'),w)
        update('EXECUTE RECOVERY Improve Volume Mesh')
        task.Execute()
        if task.State.get_state()!='Up-to-date' or task.Errors.get_state():
            raise RuntimeError('Recovery quality task did not complete')
        count=u.get_cell_zone_count(cell_zone_id_list=list(u.get_cell_zones(filter='*')))
        mesh=WORK+'/Separator-purnanto-single-'+str(round(count/1000))+'k.msh.h5'
        if remote_file_exists(s,mesh):raise FileExistsError(mesh)
        update('SAVE RECOVERED MESH',mesh=mesh,cells=count)
        s.meshing.File.WriteMesh(FileName=mesh)
        s.workflow.SaveWorkflow(FilePath=mesh.removesuffix('.msh.h5')+'.wft')
        s.meshing.File.ReadMesh(FileName=mesh)
        after=audit(s);save_json(OUT/(rid+'-reopened.json'),after)
        save_json(OUT/(rid+'-audit.json'),after)
        original=json.loads((OUT.parent/'Separator-purnanto-single-733k.msh.h5.baseline.json').read_text())
        if {b['name']:b['type'] for b in after['boundaries']}!={b['name']:b['type'] for b in original['boundaries']}:
            raise RuntimeError('Recovered boundary names/types differ')
        if after['cell_count']!=count or after['free_faces'] or after['multi_faces'] or after['metrics']['Size'][1]<=0:
            raise RuntimeError('Recovered saved-file check failed')
        update('COMPLETE',status='COMPLETE',mesh=mesh,cells=count,metrics=after['metrics'])
    except BaseException as e:
        update('FAILED',status='FAILED',error=str(e));raise
    finally:
        s.transcript.stop();transcript.write_text(''.join(logs))

if __name__=='__main__':main()
