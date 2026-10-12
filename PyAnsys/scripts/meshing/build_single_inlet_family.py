#!/usr/bin/env python3
"""Regenerate a single-inlet mesh family from the preserved 733k recipe."""
import argparse,copy,json,os,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_family_quality import *
from pyansys_fluent.remote_text import write_ascii_text_new

REMOTE='C:/Users/syok443/P4P-mesh-audit-20261008'
CAD=REMOTE+'/single-parent/separator-purnanto(single-homo).agdb'
OUT=ROOT/'output/mesh-audits/2026-10-08-purnanto-remesh/single-family'
WORK=REMOTE+'/single-family'


def recipe(scale):
    out=ROOT/'output/mesh-audits/2026-10-08-purnanto-remesh'
    w=json.loads((out/'single733-source.wft').read_text())
    tasks=w['workflow']['ROOT']
    for k,t in tasks.items():
        if not k.startswith('TaskObject:'):continue
        args=t.get('Arguments')
        if not isinstance(args,dict):continue
        name=t['_name_']
        if name=='Import Geometry':args['FileName']=CAD
        elif name=='Generate the Surface Mesh':
            args['CFDSurfaceMeshControls']={'MinSize':.01*scale,'MaxSize':.05*scale,
                'CurvatureNormalAngle':6,'SizeFunctions':'Curvature & Proximity'}
        elif name=='facesize_1':args['BOISize']=.05*scale
        elif name=='Improve Surface Mesh':args['SQMinSize']=.01*scale
        elif name=='Generate the Volume Mesh':args['VolumeFillControls']['HexMaxSize']=.08*scale
        elif name=='Improve Volume Mesh':
            args['CellQualityLimit']=.3
            args['AddMultipleQualityMethods']='No'
            args['VMImprovePreferences']['VIgnoreFeature']='no'
            args['VMImprovePreferences']['VIQualityIterations']=25
    return w


def connect():
    return pf.connect_to_fluent(ip=dotenv_values(ROOT/'.env')['FLUENT_IP'],port=int(os.environ.get('MESH_API_PORT','56319')),password=os.environ['MESH_API_PASSWORD'],
      allow_remote_host=True,insecure_mode=True,cleanup_on_exit=False,start_watchdog=False,start_transcript=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--scale',type=float,required=True);p.add_argument('--id',required=True)
    args=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    rid=args.id
    statuspath=OUT/(rid+'-status.json')
    if statuspath.exists():
        old=json.loads(statuspath.read_text())
        if old['status']=='COMPLETE':print('Already complete',rid);return
        raise RuntimeError('Existing unfinished receipt requires reconciliation: '+str(statuspath))
    receipt={'id':rid,'scale':args.scale,'status':'RUNNING','stage':'connect','parent':'Separator-purnanto-single-733k.msh.h5','cad':CAD}
    save_json(statuspath,receipt)
    s=connect();s.events.stop();logs=[]
    transcript_path=OUT/(rid+'-transcript.txt')
    transcript_path.write_text('')
    def capture(text):
        logs.append(text)
        with transcript_path.open('a') as stream:stream.write(text)
    s.transcript.register_callback(capture);s.transcript.start()
    def update(stage,**kw):
        receipt.update(stage=stage,**kw);save_json(statuspath,receipt)
        print(stage,json.dumps(kw),flush=True)
    try:
        remote_ps(s,r"New-Item -ItemType Directory -Path 'C:\Users\syok443\P4P-mesh-audit-20261008\single-family' -Force | Out-Null")
        w=recipe(args.scale);save_json(OUT/(rid+'-recipe.json'),w)
        wf=WORK+'/'+rid+'.wft'
        if not remote_file_exists(s,wf):write_ascii_text_new(s,wf,json.dumps(w,indent=2))
        s.workflow.ResetWorkflow();s.workflow.LoadWorkflow(FilePath=wf)
        # WFT task IDs define the intended active order; compound tasks own children.
        names={k.split(':',1)[1]:v['_name_'] for k,v in w['workflow']['ROOT'].items() if k.startswith('TaskObject:')}
        order=[names[k] for k in w['workflow']['ROOT']['Workflow']['TaskList']]
        for name in order:
            if name=='Improve Volume Mesh':
                save_json(OUT/(rid+'-before-improve.json'),audit(s))
            update('EXECUTE '+name)
            task=s.workflow.TaskObject[name]
            task.Execute()
            state=task.State.get_state();errors=plain(task.Errors.get_state());warnings=plain(task.Warnings.get_state())
            update('FINISHED '+name,state=state,errors=errors,warnings=warnings)
            if errors:raise RuntimeError(name+' reported '+str(errors))
            if state!='Up-to-date':raise RuntimeError(name+' state '+state)
        update('COUNT AND SAVE')
        original=json.loads((ROOT/'output/mesh-audits/2026-10-08-purnanto-remesh/Separator-purnanto-single-733k.msh.h5.baseline.json').read_text())
        expected={x['name']:x['type'] for x in original['boundaries']}
        cell_zones=list(s.meshing_utilities.get_cell_zones(filter='*'))
        cells=s.meshing_utilities.get_cell_zone_count(cell_zone_id_list=cell_zones)
        label=str(round(cells/1000))+'k'
        mesh=WORK+'/Separator-purnanto-single-'+label+'.msh.h5'
        if remote_file_exists(s,mesh):raise FileExistsError(mesh)
        update('SAVE',mesh=mesh,cells=cells)
        s.meshing.File.WriteMesh(FileName=mesh)
        if not remote_file_exists(s,mesh):raise RuntimeError('Mesh save failed')
        update('REOPEN')
        s.workflow.SaveWorkflow(FilePath=WORK+'/Separator-purnanto-single-'+label+'.wft')
        s.meshing.File.ReadMesh(FileName=mesh)
        reopened=audit(s);save_json(OUT/(rid+'-reopened.json'),reopened)
        save_json(OUT/(rid+'-audit.json'),reopened)
        if reopened['cell_count']!=cells:raise RuntimeError('Cell count changed after reopen')
        if {x['name']:x['type'] for x in reopened['boundaries']}!=expected:raise RuntimeError('Naming changed after reopen')
        # In-memory generation retains dead surface entities. The native writer
        # removes them; connectivity must be judged on the reopened artifact.
        if reopened['free_faces'] or reopened['multi_faces']:raise RuntimeError('Saved boundary connectivity check failed')
        if reopened['metrics']['Size'][1]<=0:raise RuntimeError('Non-positive cell volume')
        update('COMPLETE',status='COMPLETE',mesh=mesh,cells=cells,metrics=reopened['metrics'])
    except BaseException as e:
        update('FAILED',status='FAILED',error=str(e))
        raise
    finally:
        s.transcript.stop()
        transcript_path.write_text(''.join(logs))
if __name__=='__main__':main()
