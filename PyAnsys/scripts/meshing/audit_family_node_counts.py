"""Read global node/cell counts from saved mesh headers on the Fluent PC."""
from publish_single_family import *

def main():
    rows=collect()
    sources=[REMOTE+'/single-parent/Separator-purnanto-single-733k.msh.h5']+[r['remote_mesh'] for r in rows]
    script=WORK+'/header-counts-'+uuid.uuid4().hex+'.py'
    receipt=WORK+'/header-counts-'+uuid.uuid4().hex+'.json'
    payload="""import json,sys
from pathlib import Path
sys.path.insert(0,"""+repr(REMOTE+'/python_packages')+""")
import h5py
sources="""+repr(sources)+"""
rows=[]
for path in sources:
    with h5py.File(path,'r') as f:
        m=f['meshes/1']
        nodes=int(m.attrs['nodeCount'][0])
        cells=int(m.attrs['cellCount'][0])
        coords=sum(ds.shape[0] for ds in m['nodes/coords'].values())
        if coords!=nodes:raise ValueError('Coordinate/header node count mismatch '+path)
        rows.append(dict(file=Path(path).name,remote_mesh=path,cells=cells,
            nodes=nodes,coordinate_rows=coords,bytes=Path(path).stat().st_size))
Path("""+repr(receipt)+""").write_text(json.dumps(rows,indent=2))
"""
    s=connect();s.events.stop()
    write_ascii_text_new(s,script,payload)
    exe='C:/Program Files/ANSYS Inc/v252/commonfiles/CPython/3_10/winx64/Release/python/python.exe'
    remote_ps_file(s,"$ErrorActionPreference='Stop'\n& "+psquote(exe)+' '+psquote(script)+
        '\nif($LASTEXITCODE -ne 0){throw "Mesh header audit failed"}')
    counts=json.loads(read_text(s,receipt))
    if len(counts)!=len(sources):raise RuntimeError('Incomplete header receipt')
    for row,count in zip(rows,counts[1:]):
        if row['cells']!=count['cells'] or row['file']!=count['file']:
            raise RuntimeError('Mesh header identity mismatch')
    save_json(OUT/'family-node-counts.json',counts)
    print(json.dumps(counts,indent=2),flush=True)

if __name__=='__main__':main()
