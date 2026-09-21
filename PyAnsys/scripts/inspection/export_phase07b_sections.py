"""Read fixed Phase 7b section fields directly through Fluent's field-data API."""
from pathlib import Path
import json
import numpy as np
from ansys.fluent.core.field_data_interfaces import SurfaceFieldDataRequest, ScalarFieldDataRequest, SurfaceDataType

FIELDS=['phase-2-vof','pressure','velocity-magnitude','x-velocity','y-velocity','z-velocity','phase-2-velocity-magnitude','phase-2-x-velocity','phase-2-y-velocity','phase-2-z-velocity']

def export_sections(solver, section_names, output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    index={'fields':FIELDS,'sampling':'Fluent iso-surface facet values; node_value=False','sections':{}}
    names=list(section_names)
    geometry=solver.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=names,data_types=[SurfaceDataType.Vertices,SurfaceDataType.FacesConnectivity,SurfaceDataType.FacesCentroid]))
    data={name:{} for name in names}
    for name in names:
        g=geometry[name];vertices=np.asarray(g.vertices);centroids=np.asarray(g.face_centroids);faces=g.connectivity
        assert vertices.ndim==2 and vertices.shape[1]==3 and len(vertices)>0
        assert centroids.ndim==2 and centroids.shape[1]==3 and len(centroids)>0
        sizes=np.array([len(f) for f in faces],dtype=np.int64);connectivity=np.concatenate(faces).astype(np.int64)
        assert len(sizes)==len(centroids) and connectivity.min()>=0 and connectivity.max()<len(vertices)
        data[name].update(vertices=vertices,centroids=centroids,face_sizes=sizes,connectivity=connectivity)
    for field in FIELDS:
        values=solver.fields.field_data.get_field_data(ScalarFieldDataRequest(field_name=field,surfaces=names,node_value=False,boundary_value=False))
        for name in names:
            a=np.asarray(values[name]);assert len(a)==len(data[name]['centroids']) and np.isfinite(a).all(),(field,name,a.shape)
            data[name][field]=a
    for name in names:
        np.savez_compressed(output/(name+'.npz'),**data[name])
        index['sections'][name]={'file':name+'.npz','facets':len(data[name]['centroids']),'vertices':len(data[name]['vertices'])}
    (output/'index.json').write_text(json.dumps(index,indent=2)+'\n');return index
