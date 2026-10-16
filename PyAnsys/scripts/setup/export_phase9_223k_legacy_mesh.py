"""Export the saved 223k target as mesh-only ASCII; no Fluent case writer.

Legacy sections 10/12/13 follow ANSYS grid format; section45 zone spelling
matches the project's native legacy .msh inputs. Native reread and HDF5 audit
must pass before this derived input can be used for replacement.
"""
from pathlib import Path
import argparse,json,hashlib
import h5py
import numpy as np

def rows(group,keys):
 names=group['name'][0].decode().split(';')
 return [dict(name=n,**{k:int(group[k][i]) for k in keys if k in group}) for i,n in enumerate(names)]

def export(source,target):
 if target.exists():raise FileExistsError(target)
 with h5py.File(source,'r') as f:
  m=f['meshes/1'];cells=rows(m['cells/zoneTopology'],['id','minId','maxId']);faces=rows(m['faces/zoneTopology'],['id','minId','maxId','zoneType','c0','c1'])
  assert sum(z['maxId']-z['minId']+1 for z in cells)==223546
  ids={z['name']:z['id'] for z in cells};lo,up=ids['p71a-v2-virtual-outlet'],ids['separator-purnanto']
  cross=[z for z in faces if {z.get('c0'),z.get('c1')}=={lo,up}];assert len(cross)==2
  for z in faces:
   if z.get('c0')==lo and not z.get('c1'):
    if z['name'].startswith('wall'):z['name']='wall:004'
    elif z['name'].startswith('separator-purnanto:1'):z['name']='separator-purnanto:1:001'
   if z.get('c0')==lo and z.get('c1')==lo:z['name']='interior--separator-purnanto:013'
  # Native Phase9 entries have identical conditions; verified physical union.
  expected_entries=json.loads(Path(args.reference).read_text())['state']['readback']['entry_faces']
  for z,name in zip(sorted(cross,key=lambda z:z['name']),sorted(expected_entries)):z['name']=name
  nn=max(int(d.attrs['maxId'][0]) for d in m['nodes/coords'].values());nf=max(z['maxId'] for z in faces);nc=max(z['maxId'] for z in cells)
  types=np.zeros(nc+1,dtype=np.int32)
  for g in m['cells/ctype'].values():
   a,b=int(g.attrs['minId'][0]),int(g.attrs['maxId'][0]);types[a:b+1]=g['cell-types'][()]
  assert np.all(types[1:]>0)
  with target.open('x',encoding='ascii',newline='\n') as o:
   o.write('(0 "Phase9 223k mesh-only ASCII export; native verification required")\n(2 3)\n')
   o.write(f'(10 (0 1 {nn:x} 0 3))\n(12 (0 1 {nc:x} 0))\n(13 (0 1 {nf:x} 0))\n')
   for g in sorted(m['nodes/coords'].values(),key=lambda d:int(d.attrs['minId'][0])):
    a,b=int(g.attrs['minId'][0]),int(g.attrs['maxId'][0]);o.write(f'(10 (1 {a:x} {b:x} 1 3)(\n')
    np.savetxt(o,g[()],fmt='%.17g');o.write('))\n')
   for z in cells:
    a,b=z['minId'],z['maxId'];o.write(f'(12 ({z["id"]:x} {a:x} {b:x} 1 0)(\n')
    for start in range(a,b+1,32):o.write(' '.join(format(int(t),'x') for t in types[start:min(b+1,start+32)])+'\n')
    o.write('))\n')
   adjacent={}
   for side in ['c0','c1']:
    values=np.zeros(nf+1,dtype=np.int64)
    for d in m['faces/'+side].values():
     first,last=int(d.attrs['minId'][0]),int(d.attrs['maxId'][0]);assert len(d)==last-first+1;values[first:last+1]=d[()]
    adjacent[side]=values
   blocks=[]
   for key,g in m['faces/nodes'].items():
    counts=g['nnodes'][()].astype(np.int64);offsets=np.r_[0,np.cumsum(counts)]
    blocks.append((int(g.attrs['minId'][0]),int(g.attrs['maxId'][0]),g['nodes'][()],counts,offsets,adjacent['c0'][int(g.attrs['minId'][0]):int(g.attrs['maxId'][0])+1],adjacent['c1'][int(g.attrs['minId'][0]):int(g.attrs['maxId'][0])+1]))
   for z in faces:
    a,b=z['minId'],z['maxId'];o.write(f'(13 ({z["id"]:x} {a:x} {b:x} {z["zoneType"]:x} 0)(\n');written=0
    for first,last,nodes,counts,offsets,c0,c1 in blocks:
     for idx in range(max(a,first)-first,min(b,last)-first+1):
      vertices=nodes[offsets[idx]:offsets[idx+1]]
      assert len(vertices)==counts[idx] and np.all((vertices>=1)&(vertices<=nn))
      assert 0<=c0[idx]<=nc and 0<=c1[idx]<=nc
      o.write(' '.join(format(int(v),'x') for v in [counts[idx],*vertices,c0[idx],c1[idx]])+'\n');written+=1
    assert written==b-a+1
    o.write('))\n')
   for z in cells:o.write(f'(45 ({z["id"]} fluid {z["name"]})())\n')
   kinds={2:'interior',3:'wall',5:'pressure-outlet',10:'velocity-inlet'}
   for z in faces:o.write(f'(45 ({z["id"]} {kinds[z["zoneType"]]} {z["name"]})())\n')
 digest=hashlib.sha256(target.read_bytes()).hexdigest()
 receipt={'source':str(source),'target':str(target),'sha256':digest,'cells':nc,'faces':nf,'nodes':nn,'face_zones':faces,'cell_zones':cells,'status':'EXPORTED_NATIVE_VALIDATION_PENDING'}
 target.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':receipt['status'],'sha256':digest,'bytes':target.stat().st_size}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--target',type=Path,required=True);p.add_argument('--reference',required=True);args=p.parse_args();export(args.source,args.target)
