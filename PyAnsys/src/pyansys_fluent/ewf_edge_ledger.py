"""Attribute saved native cumulative EWF outflow to adjacent mesh boundaries.

Refuse face-level attribution when one EWF face borders multiple destinations.
Fluent's Film Outflow Mass is cumulative kg, so differences are interval mass.
"""
from collections import defaultdict
import h5py
import numpy as np


def native_ewf_edge_ledger(case_path, parent_data, child_data, film_wall='wall'):
    with h5py.File(case_path,'r') as f:
        mesh=f['meshes/1']; topo=mesh['faces/zoneTopology']
        names=topo['name'][0].decode().split(';')
        spans=list(zip(names,topo['minId'][:],topo['maxId'][:]))
        boundary={int(fid):name for (name,lo,hi),c1 in zip(spans,topo['c1'][:])
                  if c1==0 for fid in range(int(lo),int(hi)+1)}
        coordinate_groups=list(mesh['nodes/coords'].values())
        if len(coordinate_groups)!=1: raise ValueError('Requires merged global coordinates')
        coords=coordinate_groups[0][:]
        counts=mesh['faces/nodes/1/nnodes'][:]; nodes=mesh['faces/nodes/1/nodes'][:]
        offsets=np.r_[0,np.cumsum(counts)]; edges=defaultdict(list)
        for fid in boundary:
            ns=nodes[offsets[fid-1]:offsets[fid]]
            for a,b in zip(ns,np.roll(ns,-1)):
                edges[tuple(sorted((int(a),int(b))))].append(fid)
    face_targets=defaultdict(set); target_edges=defaultdict(list)
    for edge,ids in edges.items():
        upper=[fid for fid in ids if boundary[fid]==film_wall]
        if len(upper)!=1: continue
        others=sorted({boundary[fid] for fid in ids if boundary[fid]!=film_wall})
        target=','.join(others) if others else 'unconnected'
        face_targets[upper[0]].add(target);target_edges[target].append(edge)
    ambiguous={fid:sorted(v) for fid,v in face_targets.items() if len(v)!=1}
    if ambiguous: raise ValueError(f'Ambiguous per-face outflow attribution: {ambiguous}')

    def read_native(path):
        result={}
        with h5py.File(path,'r') as f:
            for dataset in f['results/1/phase-1/faces/SV_EFILM_OUTFLOW_MASS_SUM'].values():
                lo=int(np.asarray(dataset.attrs['minId']).ravel()[0])
                result.update({lo+i:float(v) for i,v in enumerate(dataset[:])})
        return result
    initial,final=read_native(parent_data),read_native(child_data)
    if initial.keys()!=final.keys(): raise ValueError('Parent/child film face IDs differ')
    rows={}
    for target,es in target_edges.items():
        ids=sorted(fid for fid,labels in face_targets.items() if target in labels)
        vertex_y=coords[np.asarray(es).ravel()-1,1]
        start=sum(initial[fid] for fid in ids);end=sum(final[fid] for fid in ids)
        rows[target]={'upper_global_face_ids':ids,'edge_count':len(es),
          'interface_vertex_y_min_m':float(vertex_y.min()),'interface_vertex_y_max_m':float(vertex_y.max()),
          'initial_cumulative_kg':start,'final_cumulative_kg':end,'increment_kg':end-start}
    nonborder=set(final)-set(face_targets)
    return {'by_adjacent_boundary':rows,'whole_wall_increment_kg':sum(final.values())-sum(initial.values()),
            'nonborder_increment_kg':sum(final[fid]-initial[fid] for fid in nonborder)}
