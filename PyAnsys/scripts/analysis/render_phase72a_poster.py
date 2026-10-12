"""Render the archived N45606 solution as an unlabelled, layered poster figure.

Read-only HDF5 extraction. No Fluent session is contacted. VTK interpolates the
saved primary steam velocity to mesh vertices and integrates illustrative
streamlines. The wall film remains a surface field at its actual wall location.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

import h5py
import numpy as np
import pyvista as pv
from vtkmodules.vtkCommonCore import vtkPoints, vtkIdList
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid, VTK_POLYHEDRON
from vtkmodules.util.numpy_support import numpy_to_vtk

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase72A/ContactAbsorber/adaptive-20261005/N45606')
OUT = ROOT / 'PyAnsys/output/poster-N45606/20261010'
RECEIPT = ROOT / 'PyAnsys/output/phase72a-adaptive-server1/20261005/recovered-N45606/endpoint.json'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def field(group, count, fill=np.nan):
    values = np.full(count, fill, dtype=float)
    for ds in group.values():
        lo, hi = int(ds.attrs['minId'][0]) - 1, int(ds.attrs['maxId'][0])
        values[lo:hi] = ds[:]
    return values


def surface(xyz, face_nodes, selected, values=None):
    packed = np.concatenate([np.r_[len(face_nodes[i]), face_nodes[i]] for i in selected])
    mesh = pv.PolyData(xyz, packed)
    if values is not None:
        mesh.cell_data['film_thickness_m'] = values[selected]
    return mesh.clean()


def extract(density):
    paths = {k: SOURCE / f'adaptive-recovered-N45606.{ext}.h5'
             for k, ext in [('case', 'cas'), ('data', 'dat')]}
    expected = json.loads(RECEIPT.read_text())['pair']
    hashes = {k: digest(p) for k, p in paths.items()}
    assert hashes['case'] == expected['case_sha256']
    assert hashes['data'] == expected['data_sha256']
    with h5py.File(paths['case']) as case, h5py.File(paths['data']) as data:
        m = case['meshes/1']
        count = int(m.attrs['cellCount'][0])
        xyz = next(iter(m['nodes/coords'].values()))[:]
        sizes = m['faces/nodes/1/nnodes'][:].astype(int)
        offsets = np.r_[0, np.cumsum(sizes)]
        nodes = m['faces/nodes/1/nodes'][:].astype(np.int64) - 1
        face_nodes = [nodes[a:b] for a, b in zip(offsets[:-1], offsets[1:])]
        c0 = field(m['faces/c0'], len(sizes), -1).astype(int) - 1
        c1 = field(m['faces/c1'], len(sizes), 0).astype(int) - 1
        zones = m['faces/zoneTopology']
        names = zones['name'][0].decode().split(';')
        ranges = {name: np.arange(int(lo)-1, int(hi)) for name, lo, hi
                  in zip(names, zones['minId'][:], zones['maxId'][:])}
        rp = case['settings/Rampant Variables'][0].decode()
        assert re.search(r'\(\(2 phase-domain phase-1\).*?\(material \. water-vapor-at-psep\)', rp, re.S)
        assert re.search(r'\(\(3 phase-domain phase-2\).*?\(material \. water-liquid-at-psep\)', rp, re.S)
        gas = data['results/1/phase-2/cells']
        velocity = np.column_stack([field(gas['SV_'+v], count) for v in ['U', 'V', 'W']])
        gas_fraction = field(gas['SV_VOF'], count)
        liquid = data['results/1/phase-3/cells']
        rho_l = field(liquid['SV_DENSITY'], count)
        alpha_l = field(liquid['SV_VOF'], count)
        assert np.all(np.isfinite(velocity))
        assert np.max(np.abs(gas_fraction + alpha_l - 1)) < 1e-10
        assert np.ptp(field(gas['SV_DENSITY'], count)) < 1e-9
        heights = field(data['results/1/phase-1/faces/SV_EFILM_HEIGHT'], len(sizes))
        cell_zones = m['cells/zoneTopology']
        separator_count = int(cell_zones['maxId'][0])
        assert count == 60964 and separator_count == 60249

    walls = surface(xyz, face_nodes, ranges['wall'])
    wall_ids = ranges['wall']
    wet_ids = wall_ids[np.isfinite(heights[wall_ids]) & (heights[wall_ids] > 1e-9)]
    film = surface(xyz, face_nodes, wet_ids, heights)
    # Fluent uses polygon area-vector magnitude. A sum of triangle magnitudes
    # is slightly different on nonplanar wall faces and overcounts this mass.
    mass_ids = wall_ids[np.isfinite(heights[wall_ids])]
    areas = []
    for i in mass_ids:
        p = xyz[face_nodes[i]]
        areas.append(np.linalg.norm(np.cross(p[1:-1]-p[0],p[2:]-p[0]).sum(0)/2))
    film_mass = float(np.dot(areas,heights[mass_ids]) * rho_l[0])
    recorded_mass = float(json.loads(RECEIPT.read_text())['readback']['fields']['p72a-e2.7-ewf-film-mass-total'][0])
    # Compare the area-integrated saved film with the native endpoint report.
    assert abs(film_mass / recorded_mass - 1) < 1e-9
    surfaces = {'shell': walls, 'film': film,
                'liquidinlet': surface(xyz, face_nodes, ranges['liquidinlet']),
                'steaminlet': surface(xyz, face_nodes, ranges['steaminlet']),
                'outlet': surface(xyz, face_nodes, ranges['steamoutlet']),
                'central_pipe': surface(xyz, face_nodes, ranges['separator-purnanto:1'])}
    print('Constructing exact polyhedral connectivity', flush=True)
    cell_faces = [[] for _ in range(count)]
    for i, ids in enumerate(face_nodes):
        cell_faces[c0[i]].append(ids)
        if c1[i] >= 0:
            cell_faces[c1[i]].append(ids[::-1])
    points = vtkPoints()
    points.SetData(numpy_to_vtk(xyz, deep=True))
    raw = vtkUnstructuredGrid()
    raw.SetPoints(points)
    raw.Allocate(count)
    for faces in cell_faces:
        packed = np.concatenate([np.array([len(faces)]),
                                 *[np.r_[len(ids), ids] for ids in faces]])
        ids = vtkIdList()
        ids.SetNumberOfIds(len(packed))
        for j, value in enumerate(packed):
            ids.SetId(j, int(value))
        raw.InsertNextCell(VTK_POLYHEDRON, ids)
    grid = pv.wrap(raw)
    grid.cell_data['steam_velocity_m_s'] = velocity
    grid.cell_data['steam_volume_fraction'] = gas_fraction
    grid.cell_data['fluent_cell_id'] = np.arange(1, count+1)
    absorber = grid.extract_cells(np.arange(separator_count, count)).extract_surface(algorithm='dataset_surface').clean()
    surfaces['absorber'] = absorber
    carrier = grid.extract_cells(np.arange(separator_count)).cell_data_to_point_data()
    carrier.set_active_vectors('steam_velocity_m_s')
    print('Tracing saved primary-steam velocity', flush=True)
    inlet = surfaces['steaminlet']
    bounds = inlet.bounds
    seeds = np.array([[bounds[0]+0.018, y, z] for y in np.linspace(bounds[2]+0.15, bounds[3]-0.15, 2)
                      for z in np.linspace(bounds[4]+0.17, bounds[5]-0.17, 2)])
    # The central outlet tube occupies r < about 0.36 m here. Seed the fluid
    # annulus outside it; never seed inside a solid or extrapolate into one.
    core = np.array([[0.48*np.cos(t), 3.9, 0.48*np.sin(t)]
                     for t in np.linspace(0, 2*np.pi, 4, endpoint=False)])
    if density == 'sparse':
        seeds = seeds[[0,3]]
        core = core[[0,2]]
    all_seeds = np.vstack([seeds,core])
    probe = pv.PolyData(all_seeds).sample(carrier)
    assert np.all(probe.point_data['vtkValidPointMask'] == 1)
    options = dict(vectors='steam_velocity_m_s', integration_direction='both',
                   integrator_type=45, initial_step_length=0.015, min_step_length=0.002,
                   max_step_length=0.04, step_unit='l', max_steps=7000,
                   terminal_speed=0.025, max_length=22.0, compute_vorticity=False)
    streams = carrier.streamlines_from_source(pv.PolyData(all_seeds), **options)
    assert streams.n_cells > 0
    # Reject tiny traces so that seed specks do not clutter the illustration.
    lengths = streams.compute_cell_sizes(length=True, area=False, volume=False).cell_data['Length']
    streams = streams.extract_cells(np.flatnonzero(lengths > 0.35)).extract_surface(algorithm='dataset_surface')
    surfaces['flow'] = streams
    for name, mesh in surfaces.items():
        mesh.save(OUT / f'{name}.vtp')
    manifest = {
        'native_iteration': 45606, 'source_paths': {k:str(p) for k,p in paths.items()},
        'sha256': hashes, 'archive_receipt': str(RECEIPT), 'cells': count,
        'field_mapping': {'steam_velocity': 'results/1/phase-2/cells/SV_U,SV_V,SV_W; domain 2 = Fluent phase-1 water-vapor-at-psep',
                          'film_thickness': 'results/1/phase-1/faces/SV_EFILM_HEIGHT; mixture/domain 1',
                          'absorber': 'cell zone p71a-v2-virtual-outlet; cells 60250–60964'},
        'checks': {'phase_volume_fraction_sum_max_error': float(np.max(np.abs(gas_fraction+alpha_l-1))),
                   'film_area_integrated_mass_kg':film_mass, 'recorded_film_mass_kg':recorded_mass,
                   'wet_wall_faces':len(wet_ids), 'film_thickness_max_m':float(np.nanmax(heights)),
                   'film_mass_relative_difference':film_mass/recorded_mass-1,
                   'all_streamline_seeds_inside_fluid':True,
                   'streamline_count':streams.n_cells},
        'streamline_method': 'VTK Runge–Kutta 4/5 on exact polyhedral mesh; saved steam cell velocity averaged to mesh vertices; inlet and core seeds; illustrative, not native Fluent pathlines',
        'streamline_seeds_m':np.vstack([seeds,core]).tolist(), 'streamline_settings':options,
        'streamline_density':density,
        'limits': ['Single N45606 snapshot. The film was still storing mass; no steady-film claim.',
                   'Film is drawn at the wall location, with no thickness enlargement.',
                   'Absorber is a numerical removal zone, not a resolved physical drain.',
                   'Independent transparent layers share a camera but lack mutual occlusion; use the scene composite for correct depth.']}
    (OUT/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return surfaces


def render(surfaces, size):
    # Vertical axis is native y. Cut away the front of the main vessel; retain
    # the inlet duct and the rear film. The cut is purely a viewing operation.
    camera_dir = np.array([-0.58, 0, 0.815])
    film = surfaces['film'].clip(normal=camera_dir, origin=(0,0,0), invert=True)
    shell = surfaces['shell']
    centres = shell.cell_centers().points
    keep = (centres @ camera_dir < 0.02) | (centres[:,0] < -1.0) | (centres[:,1] > 6.25)
    shell = shell.extract_cells(np.flatnonzero(keep)).extract_surface(algorithm='dataset_surface')
    components = {'geometry': [shell, surfaces['central_pipe'], surfaces['outlet']],
                  'film': [film], 'absorber': [surfaces['absorber']],
                  'inlets': [surfaces['steaminlet'], surfaces['liquidinlet']],
                  'flow': [surfaces['flow']]}
    camera = [(-10.3, 6.0, 14.5), (-0.25, 3.35, -0.05), (0,1,0)]
    def scene(selected, name, transparent):
        p = pv.Plotter(off_screen=True, window_size=size, lighting='three lights')
        p.set_background('white')
        p.enable_anti_aliasing('ssaa')
        p.enable_depth_peeling(number_of_peels=12, occlusion_ratio=0)
        for key in selected:
            meshes = components[key]
            if key == 'geometry':
                p.add_mesh(meshes[0],color='#D7E0E5',opacity=0.15,smooth_shading=True,show_scalar_bar=False)
                p.add_mesh(meshes[1],color='#9BAEBB',opacity=0.16,smooth_shading=True,show_scalar_bar=False)
                p.add_mesh(meshes[2],color='#CBD6DD',opacity=0.22,show_scalar_bar=False)
                edges = meshes[0].extract_feature_edges(boundary_edges=True,feature_edges=False,
                                                       manifold_edges=False,non_manifold_edges=False)
                if edges.n_points:
                    p.add_mesh(edges,color='#657D8D',opacity=0.36,line_width=1.0)
            elif key == 'film':
                p.add_mesh(meshes[0].cell_data_to_point_data(),scalars='film_thickness_m',cmap=['#C7EAF6','#85C5E2','#459BCC','#2779AF'],
                           clim=(0,0.00031),opacity=0.72,smooth_shading=True,show_scalar_bar=False,
                           ambient=0.35,diffuse=0.65,specular=0.12)
            elif key == 'absorber':
                p.add_mesh(meshes[0],color='#D59B45',opacity=0.82,smooth_shading=True,show_scalar_bar=False)
            elif key == 'inlets':
                p.add_mesh(meshes[0],color='#4EACB0',opacity=0.52,show_scalar_bar=False)
                p.add_mesh(meshes[1],color='#E0A23C',opacity=1,show_scalar_bar=False)
                p.add_mesh(meshes[1].extract_feature_edges(),color='#C47E17',line_width=3,show_scalar_bar=False)
            elif key == 'flow':
                p.add_mesh(meshes[0].tube(radius=0.008,n_sides=8),color='#42555E',opacity=0.86,
                           smooth_shading=True,show_scalar_bar=False,ambient=0.35,specular=0.15)
        p.camera_position = camera
        p.enable_parallel_projection()
        p.camera.parallel_scale = 3.95
        p.screenshot(OUT/name,transparent_background=transparent)
        p.close()
    order = ['geometry','film','absorber','inlets','flow']
    scene(order,'poster-composite.png',False)
    scene(order,'poster-composite-transparent.png',True)
    for key in order:
        scene([key],f'layer-{key}.png',True)
    # A second view retains the full wall film for a stronger film-led option.
    components['film'] = [surfaces['film']]
    scene(order,'poster-full-film.png',False)
    config = {'camera_position':camera,'parallel_scale':3.95,'image_size_px':size,
              'cutaway_horizontal_normal':camera_dir.tolist(),'layer_order':order,
              'film_colour_range_m':[0,0.00031],'flow_colour':'#42555E',
              'no_annotations':True,'no_thickness_enlargement':True}
    (OUT/'render-settings.json').write_text(json.dumps(config,indent=2)+'\n')


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--reuse',action='store_true',help='Reuse extracted VTP objects')
    parser.add_argument('--width',type=int,default=2400)
    parser.add_argument('--height',type=int,default=3200)
    parser.add_argument('--density',choices=['sparse','balanced'],default='sparse')
    args = parser.parse_args()
    if args.density == 'balanced':
        OUT = OUT / 'balanced'
    OUT.mkdir(parents=True,exist_ok=True)
    if args.reuse:
        surfaces = {p.stem:pv.read(p) for p in OUT.glob('*.vtp')}
    else:
        surfaces = extract(args.density)
    render(surfaces,(args.width,args.height))
    print('Saved poster scene and transparent layers:',OUT,flush=True)


if __name__ == '__main__':
    main()
