"""Offline section integrals from immutable Fluent case/data; no Fluent connection.
Cell fields are piecewise constant; polygon geometry and first moments are exact
for the stored planar-face mesh. Closed segment cycles are checked for each cut, including concave and multi-loop cuts.
"""
from pathlib import Path
from collections import defaultdict
import hashlib, json, csv
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase9/initial-bulk-development-final/selected-1791516474564823000')
OUT = ROOT / 'PyAnsys/output/swirl-997k/20261009'
R = 1.067


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def polygon(segments):
    # Join the actual face-cut edges, rather than taking a convex hull.
    adj = defaultdict(list)
    for a, b in segments:
        a, b = tuple(np.round(a, 11)), tuple(np.round(b, 11))
        if a == b: continue
        adj[a].append(b); adj[b].append(a)
    assert len(adj) >= 3 and all(len(v) == 2 for v in adj.values()), 'Nonclosed cut polygon'
    remaining = set(adj); loops = []
    while remaining:
        start = next(iter(remaining)); prev = None; cur = start; points = []
        while True:
            points.append(cur); remaining.remove(cur)
            nxt = next(v for v in adj[cur] if v != prev)
            prev, cur = cur, nxt
            if cur == start: break
            assert cur in remaining, 'Invalid cycle'
        p = np.array(points); q = np.roll(p, -1, axis=0)
        cross = p[:, 0] * q[:, 1] - q[:, 0] * p[:, 1]
        signed = cross.sum() / 2
        assert abs(signed) > 1e-16
        centre = ((p + q) * cross[:, None]).sum(0) / (6 * signed)
        loops.append((p, abs(signed), centre))
    # Distinct cut islands add; nested loops remove their enclosed holes.
    from matplotlib.path import Path as PolygonPath
    signs = [(-1)**sum(PolygonPath(other).contains_point(p[0])
                      for j,(other,_,_) in enumerate(loops) if j != i)
             for i,(p,_,_) in enumerate(loops)]
    area = sum(sign*a for sign,(_,a,_) in zip(signs,loops))
    assert area > 0
    centre = sum(sign*a*c for sign,(_,a,c) in zip(signs,loops))/area
    return area, centre


def cut(y, xyz, counts, offsets, nodes, c0, c1, face_ymin, face_ymax, n_separator):
    selected = np.flatnonzero((face_ymin < y) & (face_ymax > y))
    segs = defaultdict(list)
    boundary_segments = []
    for face in selected:
        p = xyz[nodes[offsets[face]:offsets[face + 1]]]
        q = np.roll(p, -1, axis=0)
        mask = (p[:, 1] < y) != (q[:, 1] < y)
        a, b = p[mask], q[mask]
        pts = a + (y - a[:, 1])[:, None] / (b[:, 1] - a[:, 1])[:, None] * (b - a)
        # A concave face can cross the plane more than twice. Its planar
        # intersection segments alternate along the intersection line.
        assert len(pts) >= 2 and len(pts) % 2 == 0
        if len(pts) > 2:
            order = np.argsort(pts[:, np.argmax(np.ptp(pts, axis=0))])
            pts = pts[order]
        for j in range(0, len(pts), 2):
            segment = (pts[j, [0, 2]], pts[j+1, [0, 2]])
            if (0 <= c0[face] < n_separator) != (0 <= c1[face] < n_separator):
                boundary_segments.append(segment)
            for cid in [c0[face], c1[face]]:
                if 0 <= cid < n_separator: segs[int(cid)].append(segment)
    cell_ids = np.array(sorted(segs))
    geometry = [polygon(segs[i]) for i in cell_ids]
    area = np.array([a for a, p in geometry]); centre = np.array([p for a, p in geometry])
    boundary_area, _ = polygon(boundary_segments)
    assert abs(area.sum() - boundary_area) < 1e-7, "Section area differs from independent boundary cut"
    perimeter = sum(np.linalg.norm(a-b) for a,b in boundary_segments)
    return cell_ids, area, centre, boundary_area, perimeter


def fluxes(ids, area, centre, fields, radius):
    rho, ux, uy, uz = (fields[k][ids] for k in ['rho', 'u', 'v', 'w'])
    x, z = centre.T
    angular = area * rho * uy * (z * ux - x * uz)
    axial = area * rho * uy**2
    mass = area * rho * uy
    out = {}
    for name, mask in [('all', np.ones(len(ids),bool)), ('up', uy > 0), ('down', uy < 0)]:
        den = axial[mask].sum(); num = angular[mask].sum()
        out[name] = {'S_outer_radius': float(num / (radius * den)) if den else None,
                     'Gtheta_N_m': float(num), 'Gy_N': float(den),
                     'mass_flux_kg_s': float(mass[mask].sum()),
                     'area_m2': float(area[mask].sum()),
                     'mean_axial_velocity_m_s': float(np.average(uy[mask], weights=area[mask])) if np.any(mask) else None}
    out['absolute_transport_ratio_outer_radius'] = float(np.abs(angular).sum() / (radius * axial.sum()))
    out['counterflow_momentum_fraction'] = float(axial[uy < 0].sum()/axial.sum())
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = {k: SOURCE/'997k'/f'997k-initial-bulk-N8080.{ext}.h5' for k, ext in [('case','cas'),('data','dat')]}
    manifest = json.loads((SOURCE/'selection-manifest.json').read_text())['pairs']['997k']
    hashes = {k: digest(p) for k,p in paths.items()}
    assert hashes == manifest['hashes'], 'Files differ from selected checkpoint'
    with h5py.File(paths['case']) as case, h5py.File(paths['data']) as data:
        mesh = case['meshes/1']; n = int(mesh.attrs['cellCount'][0]); assert n == 997604
        coords = list(mesh['nodes/coords'].values()); assert len(coords) == 1 and int(coords[0].attrs['minId'][0]) == 1
        xyz = coords[0][:]
        counts = mesh['faces/nodes/1/nnodes'][:].astype(np.int64)
        offsets = np.r_[0, np.cumsum(counts)]
        nodes = mesh['faces/nodes/1/nodes'][:].astype(np.int64) - 1
        assert offsets[-1] == len(nodes)
        c0 = mesh['faces/c0/1'][:].astype(np.int64) - 1
        c1 = np.full(len(c0), -1, dtype=np.int64)
        ds = mesh['faces/c1/1']; c1[int(ds.attrs['minId'][0])-1:int(ds.attrs['maxId'][0])] = ds[:].astype(np.int64)-1
        assert len(c0) == len(counts)
        face_ymin = np.minimum.reduceat(xyz[nodes,1],offsets[:-1])
        face_ymax = np.maximum.reduceat(xyz[nodes,1],offsets[:-1])
        # Exclude the separate virtual collector cell zone.
        n_separator = int(mesh['cells/zoneTopology/maxId'][0]); assert n_separator == 974673
        fields = {}
        for ph, label in [('phase-1','mixture'),('phase-2','vapour'),('phase-3','liquid')]:
            g = data[f'results/1/{ph}/cells']; vals = {}
            for alias,key in [('rho','SV_DENSITY'),('u','SV_U'),('v','SV_V'),('w','SV_W')]:
                ds = g[key+'/1']; assert ds.shape == (n,) and int(ds.attrs['minId'][0]) == 1
                vals[alias] = ds[:]; assert np.all(np.isfinite(vals[alias]))
            if label != 'mixture': vals['alpha'] = g['SV_VOF/1'][:]
            fields[label] = vals
        vap,liq,mix = fields['vapour'],fields['liquid'],fields['mixture']
        density_error = np.max(np.abs(mix['rho'] - vap['alpha']*vap['rho'] - liq['alpha']*liq['rho']))
        alpha_error = np.max(np.abs(vap['alpha']+liq['alpha']-1))
        assert alpha_error < 1e-12 and density_error < 1e-9
        for ph in ['vapour','liquid']:
            fields[ph]['rho'] *= fields[ph]['alpha']
        zones = mesh['faces/zoneTopology']; names = zones['name'][0].decode().split(';')
        bounds = {}
        inlet_fluxes = {}
        for name,lo,hi in zip(names,zones['minId'][:],zones['maxId'][:]):
            if name in ['liquidinlet','steaminlet','steamoutlet','bottom']:
                p = xyz[np.unique(nodes[offsets[int(lo)-1]:offsets[int(hi)]])]
                bounds[name] = {'min':p.min(0).tolist(),'max':p.max(0).tolist()}
                if name in ['liquidinlet','steaminlet']:
                    face_ids = np.arange(int(lo),int(hi)+1)
                    centres=[]; areas=[]
                    for face in face_ids-1:
                        vertices=xyz[nodes[offsets[face]:offsets[face+1]]]
                        a,c=polygon(list(zip(vertices[:,[1,2]],np.roll(vertices[:,[1,2]],-1,axis=0))))
                        areas.append(a);centres.append([vertices[0,0],c[0],c[1]])
                    centres=np.asarray(centres);areas=np.asarray(areas)
                    phase_records={}
                    for ph,label in [('phase-1','mixture'),('phase-2','vapour'),('phase-3','liquid')]:
                        g=data[f'results/1/{ph}/faces']
                        def subset(key):
                            ds=g[key+'/1']; start=int(ds.attrs['minId'][0]); assert start<=lo and int(ds.attrs['maxId'][0])>=hi
                            return ds[int(lo)-start:int(hi)-start+1]
                        inward=-subset('SV_FLUX'); ux=subset('SV_U'); uz=subset('SV_W')
                        phase_records[label]={'inward_mass_flow_kg_s':float(inward.sum()),
                            'inward_angular_momentum_flux_N_m':float(np.sum(inward*(centres[:,2]*ux-centres[:,0]*uz))),
                            'area_weighted_ux_m_s':float(np.average(ux,weights=areas)),
                            'area_weighted_uz_m_s':float(np.average(uz,weights=areas))}
                    inlet_fluxes[name]={'area_m2':float(areas.sum()),'area_weighted_centroid_xyz_m':np.average(centres,weights=areas,axis=0).tolist(),'phases':phase_records}
    rows=[]
    heights = sorted(set([.3,.6,.9,1.2,1.5,1.65,2.6,3.,4.,5.,5.8] + [h+d for h in [.3,.9,1.5] for d in [-.02,.02]]))
    for y in heights:
        ids,area,centre,boundary_area,perimeter = cut(y,xyz,counts,offsets,nodes,c0,c1,face_ymin,face_ymax,n_separator)
        results = {label:fluxes(ids,area,centre,values,R) for label,values in fields.items()}
        hydraulic_radius = area.sum()/perimeter
        for values in results.values():
            for direction in ['all','up','down']:
                values[direction]['S_hydraulic_radius'] = values[direction]['S_outer_radius']*R/hydraulic_radius if values[direction]['S_outer_radius'] is not None else None
        row={'hydraulic_radius_A_over_P_m':float(hydraulic_radius),'wetted_perimeter_m':float(perimeter),'boundary_area_m2':float(boundary_area),'y_m':y,'cut_cells':len(ids),'area_m2':float(area.sum()),'xz_bounds_of_cut_centroids_m':[centre.min(0).tolist(),centre.max(0).tolist()], 'fluxes':results}
        rows.append(row)
        print(y, len(ids), area.sum(), {k:round(v['all']['S_outer_radius'],5) for k,v in results.items()},flush=True)
        if y in [.3,.9,1.5]:
            np.savez_compressed(OUT/f'cut-y{y:.2f}.npz',cell_id=ids+1,area_m2=area,centroid_xz_m=centre,
                                **{f'{label}_{k}':vals[k][ids] for label,vals in fields.items() for k in ['rho','u','v','w']})
    result={'status':'OFFLINE_PIECEWISE_CONSTANT_SECTION_INTEGRALS','native_iteration_from_selected_manifest':8080,
            'mesh_cells':n,'separator_cells':n_separator,'paths':{k:str(v) for k,v in paths.items()},'sha256':hashes,
            'script_sha256':digest(Path(__file__)),'axis':'global +Y through x=z=0; angular momentum component z*u_x-x*u_z',
            'reference_radius_m':R,'normalization':'S_outer_radius uses 1.067 m; S_hydraulic_radius uses actual section A/P with all solid boundary perimeters.',
            'method':'Reconstruct closed cut polygon from mesh face intersections; exact area and centroid; piecewise constant saved cell velocities/density. Phase fluxes weighted by volume fraction.',
            'checks':{'hashes_match_selected_manifest':True,'all_cut_polygons_closed':True,'summed_cell_cut_areas_match_independent_boundary_cut':True,'alpha_sum_max_error':float(alpha_error),'mixture_density_reconstruction_max_error_kg_m3':float(density_error)},
            'boundary_bounds_m':bounds,'inlet_fluxes':inlet_fluxes,'sections':rows,
            'limits':['Saved initial bulk-development checkpoint, not a qualified steady solution.','No Fluent-native interpolation or gradient reconstruction; values are offline finite-volume estimates.','Up/down denote signs of global Y velocity; compare magnitudes when assessing swirl strength.','Phase fluxes cover Eulerian bulk only; wall film and particles are excluded.','Absolute transport ratio is a cancellation diagnostic, not the signed swirl number.','No pressure or turbulent stress contribution included in axial momentum flux.']}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    with (OUT/'sections.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['y_m','area_m2','S_mixture','S_vapour','S_liquid','S_up_mixture','S_down_mixture','absolute_transport_ratio_mixture','Gtheta_N_m','Gy_N','mass_flux_kg_s','down_momentum_fraction'])
        for row in rows:
            a=row['fluxes'];m=a['mixture'];w.writerow([row['y_m'],row['area_m2'],*[a[p]['all']['S_outer_radius'] for p in ['mixture','vapour','liquid']],m['up']['S_outer_radius'],m['down']['S_outer_radius'],m['absolute_transport_ratio_outer_radius'],m['all']['Gtheta_N_m'],m['all']['Gy_N'],m['all']['mass_flux_kg_s'],m['counterflow_momentum_fraction']])
    fig,axes=plt.subplots(1,2,figsize=(10,5))
    vessel=rows;yy=[a['y_m'] for a in vessel]
    for label in fields:
        axes[0].plot([abs(a['fluxes'][label]['all']['S_outer_radius']) for a in vessel],yy,'o-',ms=3,label=label.capitalize())
    axes[0].axvline(.5,color='gray',ls='--',label='0.5 reference')
    for direction,title in [('up','Upward flow'),('down','Downward flow (≥1% momentum)')]:
        axes[1].plot([abs(a['fluxes']['mixture'][direction]['S_outer_radius']) if a['fluxes']['mixture'][direction]['S_outer_radius'] is not None and (direction != 'down' or a['fluxes']['mixture']['counterflow_momentum_fraction'] >= .01) else np.nan for a in vessel],yy,'o-',ms=3,label=title)
    axes[1].plot([a['fluxes']['mixture']['absolute_transport_ratio_outer_radius'] for a in vessel],yy,':',label='Absolute transport ratio')
    for ax in axes:
        ax.axhspan(1.704,2.428,color='gray',alpha=.10,label='Inlet height');ax.set(xlabel='Swirl ratio magnitude (outer radius = 1.067 m)',ylabel='Height y (m)');ax.grid(alpha=.25);ax.legend(fontsize=8)
    axes[0].set_title('Signed section integral: magnitude');axes[1].set_title('Mixture: counterflow and cancellation')
    fig.suptitle('997,604 cells — saved N8080 bulk fields\nOffline cell-constant integration; shaded band marks inlet height',fontsize=11)
    fig.tight_layout();fig.savefig(OUT/'swirl-profile.png',dpi=170);plt.close(fig)

if __name__ == '__main__': main()
