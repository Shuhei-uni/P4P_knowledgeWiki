"""Read-only HDF5 boundary fingerprint for original/candidate mesh verification."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'python_packages'))
import h5py,numpy as np

def digest(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def inspect(path):
    with h5py.File(path,'r') as f:
        m=f['meshes/1']; n=int(m.attrs['nodeCount'][0]); xyz=np.empty((n,3))
        for ds in m['nodes/coords'].values():
            lo,hi=int(ds.attrs['minId'][0]),int(ds.attrs['maxId'][0]);xyz[lo-1:hi]=ds[...]
        topo=m['faces/zoneTopology']; raw=topo['name'][0]
        names=(raw.decode() if isinstance(raw,bytes) else str(raw)).split(';')
        zones=[]
        for i,zid in enumerate(topo['id'][...]):
            typ=int(topo['zoneType'][i]);lo=int(topo['minId'][i]);hi=int(topo['maxId'][i])
            if typ==2:continue
            pieces=[]
            for sec in m['faces/nodes'].values():
                slo=int(sec.attrs['minId'][0]);shi=int(sec.attrs['maxId'][0])
                if shi<lo or slo>hi:continue
                counts=np.asarray(sec['nnodes'][...],dtype=np.int64);ids=np.asarray(sec['nodes'][...],dtype=np.int64)
                offsets=np.r_[0,np.cumsum(counts)]
                for j in range(max(lo,slo)-slo,min(hi,shi)-slo+1):
                    points=xyz[ids[offsets[j]:offsets[j+1]]-1]
                    # Native node values are hashed exactly after canonical ordering.
                    order=np.lexsort((points[:,2],points[:,1],points[:,0]))
                    pieces.append(digest(points[order]))
            if len(pieces)!=hi-lo+1:raise ValueError('Incomplete boundary coverage '+names[i])
            zones.append(dict(name=names[i],type=typ,faces=hi-lo+1,geometry_connectivity_sha256=hashlib.sha256(''.join(sorted(pieces)).encode()).hexdigest()))
        return dict(file=str(path),counts={k:int(m.attrs[k][0]) for k in ['cellCount','faceCount','nodeCount']},
          bounds=[xyz.min(axis=0).tolist(),xyz.max(axis=0).tolist()],
          units={k:str(v) for k,v in m.attrs.items() if 'unit' in k.lower()},
          boundary=sorted(zones,key=lambda z:z['name']))
if __name__=='__main__':
    result=inspect(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(result,indent=2))
