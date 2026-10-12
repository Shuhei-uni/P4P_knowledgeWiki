#!/usr/bin/env python3
"""Audit and conservatively improve a preserved Fluent Meshing family.
Credentials are supplied by environment, never written to the receipt.
"""
import argparse,base64,json,os,sys,time
from pathlib import Path
from collections.abc import Mapping,Iterable
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from dotenv import dotenv_values
import ansys.fluent.core as pf
from pyansys_fluent.common import quote_scheme_string,remote_file_exists
from pyansys_fluent.remote_text import read_text

def plain(x):
    if isinstance(x,Mapping):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(str,int,float,bool)) or x is None:return x
    if isinstance(x,Iterable):return [plain(v) for v in x]
    return str(x)

def audit(s):
    u=s.meshing_utilities
    cells=list(u.get_cell_zones(filter='*'))
    faces=list(u.get_face_zones(filter='*'))
    names=list(u.convert_zone_ids_to_name_strings(zone_id_list=faces))
    b=[]
    for z,n in zip(faces,names):
        typ=u.get_zone_type(zone_id=z)
        if typ=='interior':continue
        b.append(dict(id=z,name=n,type=typ,area=u.get_face_zone_area(face_zone_id_list=[z]),
          bounds=plain(u.get_bounding_box_of_zone_list(zone_id_list=[z])),
          face_count=u.get_face_zone_count(face_zone_id_list=[z]),
          node_count=u.get_face_zone_node_count(face_zone_id=z)))
    mids=['Orthogonal Quality','Skewness','FLUENT Aspect Ratio','Size Change','Size']
    metrics={m:plain(u.get_cell_quality_limits(cell_zone_id_list=cells,measure=m)) for m in mids}
    dist={m:plain(u.get_cell_mesh_distribution(cell_zone_id_list=cells,measure=m,partitions=10,range=[0,1])) for m in mids[:2]}
    dist['Size Change >= 300']=plain(u.get_cell_mesh_distribution(
        cell_zone_id_list=cells,measure='Size Change',partitions=5,range=[300,100000]))
    boundaries=[x['id'] for x in b]
    s.tui.mesh.check_mesh()
    return plain(dict(cell_zones=cells,cell_count=u.get_cell_zone_count(cell_zone_id_list=cells),
        volume=u.get_cell_zone_volume(cell_zone_id_list=cells),boundaries=b,metrics=metrics,distributions=dist,
        free_faces=u.get_free_faces_count(face_zone_id_list=boundaries),
        multi_faces=u.get_multi_faces_count(face_zone_id_list=boundaries)))

def save_json(path,data):path.write_text(json.dumps(plain(data),indent=2))
def remote_ps(s,code):
    enc=base64.b64encode(code.encode('utf-16le')).decode()
    return s.scheme.eval('(system "'+quote_scheme_string('powershell -NoProfile -NonInteractive -EncodedCommand '+enc)+'")')

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['baseline','discover'],required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    out=args.output;manifest=json.loads((out/'source-manifest.json').read_text())
    cfg=dotenv_values(ROOT/'.env')
    s=pf.connect_to_fluent(ip=cfg['FLUENT_IP'],port=56319,password=os.environ['MESH_API_PASSWORD'],
      allow_remote_host=True,insecure_mode=True,cleanup_on_exit=False,start_watchdog=False,start_transcript=False)
    logs=[];s.transcript.register_callback(lambda text:logs.append(text));s.transcript.start()
    remote='C:/Users/syok443/P4P-mesh-audit-20261008'
    if args.stage=='discover':
        code=r'''
$paths=@()
Get-Command python,python3,py -ErrorAction SilentlyContinue | ForEach-Object {$paths+=$_.Source}
$root=Join-Path $env:AWP_ROOT252 'commonfiles\CPython'
if(Test-Path $root){$paths+=@(Get-ChildItem -LiteralPath $root -Filter python.exe -File -Recurse | Select-Object -ExpandProperty FullName)}
$paths | ConvertTo-Json | Set-Content 'C:\Users\syok443\P4P-mesh-audit-20261008\python-paths.json' -Encoding Ascii
'''
        remote_ps(s,code);txt=read_text(s,remote+'/python-paths.json');print(txt,flush=True)
        (out/'python-paths.json').write_text(txt)
    else:
        # Read smallest first to verify the process before larger files.
        for item in sorted(manifest,key=lambda x:x['bytes']):
            name=item['name'];dest=out/(name+'.baseline.json')
            if dest.exists():continue
            print('READ',name,flush=True)
            start=len(logs)
            s.meshing.File.ReadMesh(FileName=item['local_original'].replace('\\','/'))
            data=audit(s);data.update(source=item,version=str(s.get_fluent_version()))
            save_json(dest,data)
            (out/(name+'.baseline-transcript.txt')).write_text(''.join(logs[start:]))
            print('AUDITED',name,data['cell_count'],data['metrics'],flush=True)
        s.meshing.File.ReadMesh(FileName=remote+'/loaded-before-improvement.msh.h5')
        print('RESTORED original live mesh',flush=True)
    s.transcript.stop()
if __name__=='__main__':main()
