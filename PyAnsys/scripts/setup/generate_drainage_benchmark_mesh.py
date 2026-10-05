#!/usr/bin/env python3
"""Generate the 320-cell rectangular drainage benchmark mesh without Fluent.

Format: Ansys Fluent 2025 R2 User's Guide, B.3 Grid Sections:
https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/tgd_user_format_gridsect.html
Face vertex right-hand normals point TOWARD c0. Hex cell type=4;
quad face type=4; interior/inlet/outlet/symmetry bc types=2/4/5/7.
Zone names use section 45 (decimal zone IDs; grid indices are hexadecimal).
Outlet is pressure-outlet and must be converted to outlet-vent by setup.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def generate(path: Path):
    nx, ny, nz = 20, 4, 4
    dx, dy, dz = 1/nx, .5/ny, .5/nz
    node = lambda i, j, k: 1 + i + (nx+1)*(j+(ny+1)*k)
    cell = lambda i, j, k: 1 + i + nx*(j+ny*k)
    points = {node(i,j,k):(i*dx,j*dy,k*dz)
              for k in range(nz+1) for j in range(ny+1) for i in range(nx+1)}
    centers = {cell(i,j,k):((i+.5)*dx,(j+.5)*dy,(k+.5)*dz)
               for k in range(nz) for j in range(ny) for i in range(nx)}
    # Zone IDs: node 1, fluid 2, interior 3, inlet 4, outlet 5, symmetry 6.
    zones = {3:[], 4:[], 5:[], 6:[]}

    def add(vertices, c0, c1, zone):
        p = [points[n] for n in vertices]
        center = tuple(sum(v[a] for v in p)/4 for a in range(3))
        normal = cross(sub(p[1],p[0]), sub(p[3],p[0]))
        if dot(normal, sub(centers[c0],center)) < 0:
            vertices = tuple(reversed(vertices))
        zones[zone].append((vertices,c0,c1))

    for i in range(nx+1):
        for j in range(ny):
            for k in range(nz):
                v = (node(i,j,k),node(i,j+1,k),node(i,j+1,k+1),node(i,j,k+1))
                add(v,cell(0,j,k) if i==0 else cell(i-1,j,k),
                    cell(i,j,k) if 0<i<nx else 0, 4 if i==0 else 5 if i==nx else 3)
    for j in range(ny+1):
        for i in range(nx):
            for k in range(nz):
                v = (node(i,j,k),node(i+1,j,k),node(i+1,j,k+1),node(i,j,k+1))
                add(v,cell(i,0,k) if j==0 else cell(i,j-1,k),
                    cell(i,j,k) if 0<j<ny else 0, 6 if j in (0,ny) else 3)
    for k in range(nz+1):
        for i in range(nx):
            for j in range(ny):
                v = (node(i,j,k),node(i+1,j,k),node(i+1,j+1,k),node(i,j+1,k))
                add(v,cell(i,j,0) if k==0 else cell(i,j,k-1),
                    cell(i,j,k) if 0<k<nz else 0, 6 if k in (0,nz) else 3)

    faces = [face for z in zones.values() for face in z]
    counts = Counter()
    volumes = {c:0. for c in centers}
    areas = {c:[0.,0.,0.] for c in centers}
    cell_nodes = {c:set() for c in centers}
    keys = set()
    for vertices,c0,c1 in faces:
        key = tuple(sorted(vertices))
        assert key not in keys, 'Duplicate face'
        keys.add(key)
        p = [points[n] for n in vertices]
        fc = tuple(sum(v[a] for v in p)/4 for a in range(3))
        av = cross(sub(p[1],p[0]),sub(p[3],p[0]))
        assert dot(av,sub(centers[c0],fc))>0, 'c0 orientation'
        if c1:
            assert dot(av,sub(centers[c1],fc))<0, 'c1 orientation'
        for c,sign in ((c0,-1),(c1,1)):
            if not c:
                continue
            counts[c]+=1
            cell_nodes[c].update(vertices)
            volumes[c]+=sign*dot(av,fc)/3
            for a in range(3):
                areas[c][a]+=sign*av[a]
    assert len(points)==525 and len(centers)==320 and len(faces)==1136
    assert all(counts[c]==6 and len(cell_nodes[c])==8 for c in centers)
    assert all(abs(v-dx*dy*dz)<1e-14 and v>0 for v in volumes.values())
    assert all(abs(a)<1e-14 for vec in areas.values() for a in vec)
    assert abs(sum(volumes.values())-.25)<1e-13
    assert {z:len(f) for z,f in zones.items()}=={3:784,4:16,5:16,6:320}
    lines = ['(0 "320-cell drainage benchmark; SI metres")','(2 3)',
             f'(10 (0 1 {len(points):x} 0))',f'(12 (0 1 {len(centers):x} 0))',
             f'(13 (0 1 {len(faces):x} 0))',f'(10 (1 1 {len(points):x} 1 3)(']
    lines += [' '.join(f'{x:.17g}' for x in p) for p in points.values()]
    lines += ['))',f'(12 (2 1 {len(centers):x} 1 4))']
    first = 1
    for z, fs in zones.items():
        bc = {3:2,4:4,5:5,6:7}[z]
        lines.append(f'(13 ({z:x} {first:x} {first+len(fs)-1:x} {bc:x} 4)(')
        lines += [' '.join(f'{v:x}' for v in (*vertices,c0,c1)) for vertices,c0,c1 in fs]
        lines.append('))')
        first+=len(fs)
    for z,kind,name in ((2,'fluid','fluid'),(3,'interior','interior'),
                        (4,'pressure-inlet','inlet'),(5,'pressure-outlet','outlet'),
                        (6,'symmetry','sides')):
        lines.append(f'(45 ({z} {kind} {name} 1)())')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(lines)+'\n')
    return {'mesh':str(path.resolve()),'nodes':len(points),'cells':len(centers),
            'faces':len(faces),'faces_by_zone':{str(z):len(fs) for z,fs in zones.items()},
            'min_cell_volume_m3':min(volumes.values()),'max_cell_volume_m3':max(volumes.values()),
            'total_volume_m3':sum(volumes.values()),'verified':'unique faces; 6 faces and 8 nodes per cell; inward c0 and outward c1 normals; closed area vectors; positive divergence volumes',
            'fluent_read_verified':False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[2]/'output/drainage-benchmark/duct.msh')
    args = parser.parse_args()
    print(json.dumps(generate(args.output),indent=2))
