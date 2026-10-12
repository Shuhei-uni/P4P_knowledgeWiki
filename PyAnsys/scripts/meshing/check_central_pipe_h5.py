"""Read-only comparison of cells near the central pipe in two saved meshes."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'python_packages'))
import numpy as np,h5py

def inspect(path):
    with h5py.File(path,'r') as f:
        m=f['meshes/1'];nc=int(m.attrs['cellCount'][0]);nn=int(m.attrs['nodeCount'][0])
        xyz=np.empty((nn,3))
        for ds in m['nodes/coords'].values():
            lo,hi=int(ds.attrs['minId'][0]),int(ds.attrs['maxId'][0]);xyz[lo-1:hi]=ds[...]
        sums=np.zeros((nc+1,3));weights=np.zeros(nc+1)
        for name,sec in m['faces/nodes'].items():
            counts=np.asarray(sec['nnodes'][...],dtype=np.int64);ids=np.asarray(sec['nodes'][...],dtype=np.int64)
            starts=np.r_[0,np.cumsum(counts)[:-1]]
            midpoint=np.add.reduceat(xyz[ids-1],starts,axis=0)/counts[:,None]
            for side in ['c0','c1']:
                adjacent=np.asarray(m['faces'][side][name][...],dtype=np.int64).reshape(-1)
                if len(adjacent)!=len(counts):raise ValueError('Face adjacency shape mismatch')
                weights+=np.bincount(adjacent,minlength=nc+1)
                for axis in range(3):sums[:,axis]+=np.bincount(adjacent,weights=midpoint[:,axis],minlength=nc+1)
        if np.any(weights[1:]==0):raise ValueError('Cells without face coverage')
        centers=sums[1:]/weights[1:,None]
        radius=np.hypot(centers[:,0],centers[:,2]);height=centers[:,1]
        core=(radius<.25)&(height>.25)&(height<5.5)
        bands=[]
        for lo,hi in [(0,.5),(.5,1.5),(1.5,2.5),(2.5,3.5),(3.5,4.5),(4.5,5.5),(5.5,5.761),(5.761,6.261),(6.261,6.995)]:
            mask=(height>lo)&(height<hi)
            bands.append(dict(y_range_m=[lo,hi],core_r_lt025_cells=int(np.count_nonzero(mask&(radius<.25))),
                min_cell_center_radius_m=float(radius[mask].min()) if np.any(mask) else None))
        ct=m['cells/zoneTopology'];raw=ct['name'][0]
        names=(raw.decode() if isinstance(raw,bytes) else str(raw)).split(';')
        ft=m['faces/zoneTopology'];raw=ft['name'][0]
        fn=(raw.decode() if isinstance(raw,bytes) else str(raw)).split(';')
        j=fn.index('separator-purnanto:1');lo=int(ft['minId'][j]);hi=int(ft['maxId'][j])
        vertices=[]
        for sec in m['faces/nodes'].values():
            slo=int(sec.attrs['minId'][0]);shi=int(sec.attrs['maxId'][0])
            if shi<lo or slo>hi:continue
            counts=np.asarray(sec['nnodes'][...],dtype=np.int64);ids=np.asarray(sec['nodes'][...],dtype=np.int64)
            offsets=np.r_[0,np.cumsum(counts)]
            vertices.extend(ids[offsets[max(lo,slo)-slo]:offsets[min(hi,shi)-slo+1]].tolist())
        p=xyz[np.unique(vertices)-1];r=np.hypot(p[:,0],p[:,2])
        # Small diagram payload from the mid-plane, bounded for API transfer.
        cut=centers[(abs(centers[:,2])<.035)&(abs(centers[:,0])<.65)]
        cut=cut[::max(1,len(cut)//1200)]
        return dict(file=str(path),cell_count=nc,cell_zone_names=names,
            deep_pipe_core_cells=int(core.sum()),bands=bands,
            central_wall=dict(bounds=[p.min(axis=0).tolist(),p.max(axis=0).tolist()],
                min_radius_m=float(r.min()),max_radius_m=float(r.max())),
            cell_center_method='Mean of cell face vertex means; used only well inside the pipe void',
            slice_cell_centers_xy_m=cut[:1200,:2].round(5).tolist())

if __name__=='__main__':
    rows=[inspect(p) for p in sys.argv[2:]]
    Path(sys.argv[1]).write_text(json.dumps(rows,separators=(',',':')))
