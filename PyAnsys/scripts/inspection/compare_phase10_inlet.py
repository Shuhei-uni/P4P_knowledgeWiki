"""Three-case inlet-band postprocessing. No solve or scientific setting changes."""
from pathlib import Path
import hashlib
import json
import math
import time

import numpy as np
from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest, SurfaceDataType, ScalarFieldDataRequest
import run_phase10_proposed_design as p

OUT = p.REPO / 'PyAnsys/output/phase10-inlet-comparison/20261012'
FIG = p.REPO / 'Project/experiments/phase-10-proposed-design/figures/inlet-comparison-50ms'
SHARED = p.SHARED / 'P4P-Fluent-Artifacts/Phase10'
SOURCES = {
    'baseline': p.WORK.parent / 'phase9-60k-ewf-20261009-170630/014-sequential-0p1us-qualification-N30000/final-N31000',
    'vertical': SHARED / 'proposed-design/vertical-slit-reference-50p9ms/vertical-slit-N84000-50p9ms',
    'angled': SHARED / 'proposed-design-213k/final-50ms-N33492-1791790200415874900/final-50ms-N33492'}
BAND = [1.5, 2.8]
TOP = {'position': [-.8, 12.066, -.20], 'target': [-.8, 2.066, -.20], 'up': [0, 0, -1], 'width': 4.2, 'height': 3.5}
WALL = {'position': [-6, 2.15, -5], 'target': [0, 2.15, 0], 'up': [0, 1, 0], 'width': 3.4, 'height': 2.7}


def dump(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / name
    tmp = dest.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2, default=str) + '\n')
    tmp.replace(dest)


def identity(stem):
    result = {}
    for kind, ext in [('case', 'cas.h5'), ('data', 'dat.h5')]:
        path = Path(str(stem) + '.' + ext)
        with path.open('rb') as stream:
            result[kind + '_sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
        result[kind] = str(path)
    return result


def load(s, pair):
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    s.settings.file.read_data(file_name=pair['data'])


def surfaces(s):
    walls = {}
    for name in s.settings.setup.boundary_conditions.wall.get_object_names():
        state = s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film.get_state()
        if state.get('eulerian_film_wall'):
            walls[name] = state
    assert 'wall' in walls, 'Primary film wall missing'
    planes = s.settings.results.surfaces.plane_surface
    if 'ic-top' not in planes.get_object_names():
        planes.create(name='ic-top')
    planes['ic-top'].set_state({'method': 'zx-plane', 'y': 2.066})
    clips = s.settings.results.surfaces.iso_clip
    if 'ic-film-band' not in clips.get_object_names():
        clips.create(name='ic-film-band')
    clips['ic-film-band'].set_state({'field': 'y-coordinate', 'surfaces': ['wall'],
                                    'range': {'minimum': BAND[0], 'maximum': BAND[1]}})
    custom = s.settings.results.custom_vectors
    if 'ic-film-velocity' not in custom.get_object_names():
        custom.create(name='ic-film-velocity')
    custom['ic-film-velocity'].set_state({'x_component': 'film-x-velocity', 'y_component': 'film-y-velocity',
                                         'z_component': 'film-z-velocity'})
    return walls


def contour(s, label, field, surface, limits=None):
    coll = s.settings.results.graphics.contour
    name = 'ic-' + label
    if name not in coll.get_object_names():
        coll.create(name=name)
    obj = coll[name]
    assert field in obj.field.allowed_values(), field
    obj.set_state({'field': field, 'surfaces_list': [surface],
                   'range_options': {'global_range': False, 'auto_range': True, 'clip_to_range': False},
                   'options': {'filled': True, 'node_values': True, 'boundary_values': field.startswith('film-'), 'contour_lines': False}})
    obj.range_options.compute()
    observed = obj.range_options.get_state()
    if limits:
        obj.range_options.set_state({'global_range': False, 'auto_range': False, 'clip_to_range': False,
                                     'minimum': limits[0], 'maximum': limits[1]})
    return obj, observed


def vector(s, label, vector_field, speed, surface, limits=None):
    coll = s.settings.results.graphics.vector
    name = 'ic-' + label
    if name not in coll.get_object_names():
        coll.create(name=name)
    obj = coll[name]
    assert vector_field in obj.vector_field.allowed_values(), (vector_field, obj.vector_field.allowed_values())
    obj.set_state({'vector_field': vector_field, 'field': speed, 'surfaces_list': [surface],
                   'range_options': {'global_range': False, 'auto_range': True, 'clip_to_range': False},
                   'options': {'auto_scale': True, 'vector_style': '3d arrow', 'scale': .035, 'skip': 0},
                   'vector_opt': {'in_plane': False, 'fixed_length': True, 'color': ''}})
    if surface == 'ic-top':
        obj.vector_opt.in_plane = True
    obj.range_options.compute()
    observed = obj.range_options.get_state()
    if limits:
        obj.range_options.set_state({'global_range': False, 'auto_range': False, 'clip_to_range': False,
                                     'minimum': limits[0], 'maximum': limits[1]})
    return obj, observed


def metrics(s):
    rd = s.settings.solution.report_definitions
    specs = [('area', 'surface-area', None), ('film-mass', 'surface-sum', 'film-mass'),
             ('film-thickness-mean', 'surface-areaavg', 'film-thickness'),
             ('film-thickness-max', 'surface-facetmax', 'film-thickness'),
             ('film-speed-mean', 'surface-areaavg', 'film-velocity-mag'),
             ('film-y-mean', 'surface-areaavg', 'film-y-velocity')]
    names = []
    for label, kind, field in specs:
        name = 'ic-' + label
        if name not in rd.surface.get_object_names():
            rd.surface.create(name=name)
        obj = rd.surface[name]
        assert kind in obj.report_type.allowed_values(), (kind, obj.report_type.allowed_values())
        obj.report_type = kind
        obj.surface_names = ['ic-film-band']
        if field:
            obj.field = field
        names.append(name)
    values = {}
    for item in rd.compute(report_defs=names):
        values.update(item)
    return values


def inspect_case(s, name, pair):
    load(s, pair)
    clock = dict(s.rp_vars('wall-film/solution-state'))
    n = p.native_iteration(s)
    active = surfaces(s)
    geometry = {}
    zones = ['liquidinlet', 'steaminlet'] + [n for n in s.settings.setup.boundary_conditions.wall.get_object_names() if 'slit' in n]
    for zone in zones:
        xyz = np.asarray(s.fields.field_data.get_field_data(SurfaceFieldDataRequest(
            surfaces=[zone], data_types=[SurfaceDataType.FacesCentroid]))[zone].face_centroids)
        geometry[zone] = {'min': xyz.min(axis=0).tolist(), 'max': xyz.max(axis=0).tolist(), 'mean': xyz.mean(axis=0).tolist()}
    ranges = {}
    for label, field, surface in [('thickness', 'film-thickness', 'ic-film-band'), ('vf', 'phase-2-vof', 'ic-top')]:
        _, ranges[label] = contour(s, label, field, surface)
    probe = s.settings.results.graphics.vector
    if 'ic-vector-inspect' not in probe.get_object_names():
        probe.create(name='ic-vector-inspect')
    vector_fields = probe['ic-vector-inspect'].vector_field.allowed_values()
    film_vector = next((v for v in vector_fields if v == 'ic-film-velocity'), None)
    assert film_vector, vector_fields
    for label, vf, speed, surface in [('film-vectors', film_vector, 'film-velocity-mag', 'ic-film-band'),
                                     ('bulk-vectors', 'velocity', 'velocity-magnitude', 'ic-top')]:
        _, ranges[label] = vector(s, label, vf, speed, surface)
    result = {'name': name, 'pair': pair, 'native_iteration': n, 'film_clock': clock,
              'bulk_equations': s.settings.solution.controls.equations.get_state(), 'film_walls': active,
              'film_parameters': dict(s.rp_vars('wall-film/model-parameters')), 'geometry': geometry,
              'ranges': ranges, 'film_vector_field': film_vector, 'band_m': BAND, 'metrics': metrics(s)}
    assert p.native_iteration(s) == n
    assert dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] == clock['film_elapsed_time']
    dump(name + '-inspection.json', result)
    print('INLET_INSPECTION', name, clock['film_elapsed_time'], flush=True)
    return result


def limits():
    records = [json.loads((OUT / (name + '-inspection.json')).read_text()) for name in SOURCES]
    result = {'vf': [0, .5]}
    for label in ['thickness', 'film-vectors', 'bulk-vectors']:
        high = max(r['ranges'][label]['maximum'] for r in records)
        scale = 10 ** math.floor(math.log10(max(high, 1e-30)))
        upper = next(v * scale for v in [1, 2, 5, 10] if v * scale >= high)
        result[label] = [0, upper]
    return result


def picture(s, obj, path, camera):
    g = s.settings.results.graphics
    g.colors.graphics_color_theme = 'white'
    g.lighting.lights_on = False
    g.windows.axes.visible = True
    cmap = obj.color_map.get_state()
    cmap.update({'visible': True, 'font_size': .014, 'length': .48, 'width': 4.0})
    obj.color_map.set_state(cmap)
    obj.display()
    c = g.views.camera
    c.projection(type='orthographic')
    c.position(xyz=camera['position']); c.target(xyz=camera['target']); c.up_vector(xyz=camera['up'])
    c.field(width=camera['width'], height=camera['height'])
    if g.picture.use_window_resolution.is_active():
        g.picture.use_window_resolution = False
    g.picture.invert_background = False
    g.picture.landscape = True
    g.picture.x_resolution = 2400
    g.picture.y_resolution = 2000
    g.picture.save_picture(file_name=str(path))
    assert path.is_file() and path.stat().st_size > 1000


def facet_metrics(s, name):
    geom = s.fields.field_data.get_field_data(SurfaceFieldDataRequest(
        surfaces=['wall'], data_types=[SurfaceDataType.Vertices, SurfaceDataType.FacesConnectivity, SurfaceDataType.FacesCentroid]))['wall']
    vertices = np.asarray(geom.vertices)
    centres = np.asarray(geom.face_centroids)
    area = np.asarray([.5 * np.linalg.norm(np.cross(vertices[ids], np.roll(vertices[ids], -1, axis=0)).sum(axis=0))
                       for ids in geom.connectivity])
    fields = {field: np.asarray(s.fields.field_data.get_field_data(ScalarFieldDataRequest(
        surfaces=['wall'], field_name=field, node_value=False, boundary_value=True))['wall']).reshape(-1)
        for field in ['film-thickness', 'film-mass', 'film-x-velocity', 'film-y-velocity', 'film-z-velocity']}
    assert all(v.shape == area.shape and np.isfinite(v).all() for v in fields.values())
    band = (centres[:, 1] >= BAND[0]) & (centres[:, 1] <= BAND[1])
    wet = band & (fields['film-thickness'] >= 1e-6)
    speed = np.sqrt(sum(fields['film-' + axis + '-velocity'] ** 2 for axis in 'xyz'))
    stats = {'selection': 'Original wall faces selected by centroid Y, 1.5 to 2.8 m; wetted threshold >=1um',
             'faces': int(band.sum()), 'area_m2': float(area[band].sum()), 'wet_area_m2': float(area[wet].sum()),
             'wet_fraction': float(area[wet].sum() / area[band].sum()),
             'film_mass_kg': float(fields['film-mass'][band].sum()),
             'mean_thickness_m': float(np.average(fields['film-thickness'][band], weights=area[band])),
             'max_thickness_m': float(fields['film-thickness'][band].max()),
             'wet_mean_speed_ms': float(np.average(speed[wet], weights=area[wet])),
             'wet_mean_y_velocity_ms': float(np.average(fields['film-y-velocity'][wet], weights=area[wet])),
             'max_speed_ms': float(speed[band].max())}
    dump(name + '-facet-metrics.json', stats)
    np.savez_compressed(OUT / (name + '-wall-facets.npz'), centres=centres, area=area, band=band, wet=wet, **fields)


def export_case(s, name, scale):
    record = json.loads((OUT / (name + '-inspection.json')).read_text())
    load(s, record['pair'])
    assert p.native_iteration(s) == record['native_iteration']
    surfaces(s)
    facet_metrics(s, name)
    FIG.mkdir(parents=True, exist_ok=True)
    figures = []
    jobs = [('vf', 'phase-2-vof', 'ic-top', TOP),
            ('bulk-vectors', 'velocity', 'ic-top', TOP)]
    for label, field, surface, camera in jobs:
        if 'vectors' in label:
            speed = 'film-velocity-mag' if label.startswith('film') else 'velocity-magnitude'
            obj, observed = vector(s, label, field, speed, surface, scale[label])
        else:
            obj, observed = contour(s, label, field, surface, scale[label])
        path = FIG / (name + '-' + label + '.png')
        picture(s, obj, path, camera)
        figures.append({'label': label, 'path': str(path), 'camera': camera,
                        'display_range': scale[label], 'observed': observed, 'object': obj.get_state()})
        dump(name + '-figures.json', figures)
        print('INLET_FIGURE', name, label, flush=True)
    assert p.native_iteration(s) == record['native_iteration']
    assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - record['film_clock']['film_elapsed_time']) < 1e-12


def run(s, stage='inspect'):
    restore = json.loads((p.OUT / 'paused-furthest-reopen.json').read_text())
    dump('review.json', {'stage': stage, 'commands': 'Saved-pair read, temporary surfaces, native reports and graphics only',
                         'solve_issued': False, 'restore_pair': restore['pair'], 'band_m': BAND,
                         'source_stems': SOURCES, 'scientific_parameters_changed': False,
                         'native_iteration_before': p.native_iteration(s), 'epoch': time.time()})
    try:
        if stage == 'inspect':
            for name, stem in SOURCES.items():
                inspect_case(s, name, identity(stem))
            dump('shared-ranges.json', limits())
        else:
            scale = json.loads((OUT / 'shared-ranges.json').read_text())
            for name in SOURCES:
                export_case(s, name, scale)
    finally:
        load(s, restore['pair'])
        assert p.native_iteration(s) == restore['native_iteration']
        assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - restore['clock']['film_elapsed_time']) < 1e-12
        dump('restored-session.json', {'pair': restore['pair'], 'native_iteration': p.native_iteration(s),
                                      'film_clock': dict(s.rp_vars('wall-film/solution-state')), 'solver_paused': True})
        print('INLET_SESSION_RESTORED_PAUSED', flush=True)


def top_only(s):
    restore = json.loads((p.OUT / 'paused-furthest-reopen.json').read_text())
    try:
        for name in SOURCES:
            record = json.loads((OUT / (name + '-inspection.json')).read_text())
            load(s, record['pair'])
            surfaces(s)
            obj, observed = contour(s, 'top-k', 'turb-kinetic-energy', 'ic-top', [0, 25])
            assert observed['maximum'] <= 25, 'TKE common range needs expansion'
            path = FIG / (name + '-tke.png')
            picture(s, obj, path, TOP)
            figures = [f for f in json.loads((OUT / (name + '-figures.json')).read_text())
                       if f['label'] in ['vf', 'bulk-vectors']]
            figures.append({'label': 'tke', 'path': str(path), 'camera': TOP,
                            'display_range': [0, 25], 'observed': observed, 'object': obj.get_state()})
            dump(name + '-top-figures.json', figures)
            assert p.native_iteration(s) == record['native_iteration']
            assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - record['film_clock']['film_elapsed_time']) < 1e-12
            print('TOP_ONLY_COMPLETE', name, flush=True)
    finally:
        load(s, restore['pair'])
        assert p.native_iteration(s) == restore['native_iteration']
        assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - restore['clock']['film_elapsed_time']) < 1e-12
        dump('restored-session.json', {'pair': restore['pair'], 'native_iteration': p.native_iteration(s),
                                      'film_clock': dict(s.rp_vars('wall-film/solution-state')), 'solver_paused': True,
                                      'analysis_scope': 'TOP_DOWN_ONLY'})
        print('TOP_ONLY_SESSION_RESTORED_PAUSED', flush=True)


def change_vf_range(s):
    restore = json.loads((p.OUT / 'paused-furthest-reopen.json').read_text())
    assert p.native_iteration(s) == restore['native_iteration'], 'Session changed; reconcile before replacement'
    assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - restore['clock']['film_elapsed_time']) < 1e-12
    try:
        for name, stem in SOURCES.items():
            record = json.loads((OUT / (name + '-inspection.json')).read_text())
            assert identity(stem) == record['pair'], 'Source pair changed'
            load(s, record['pair'])
            surfaces(s)
            obj, observed = contour(s, 'vf', 'phase-2-vof', 'ic-top', [0, .5])
            path = FIG / (name + '-vf.png')
            picture(s, obj, path, TOP)
            updated = {'label': 'vf', 'path': str(path), 'camera': TOP, 'display_range': [0, .5],
                       'observed': observed, 'object': obj.get_state(), 'display_policy': 'Values above 0.5 use upper colour; no surface clipping'}
            for suffix in ['-figures.json', '-top-figures.json']:
                figures = json.loads((OUT / (name + suffix)).read_text())
                figures = [updated if f['label'] == 'vf' else f for f in figures]
                dump(name + suffix, figures)
            assert p.native_iteration(s) == record['native_iteration']
            assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - record['film_clock']['film_elapsed_time']) < 1e-12
            print('VF_RANGE_UPDATED', name, flush=True)
        scale = json.loads((OUT / 'shared-ranges.json').read_text())
        scale['vf'] = [0, .5]
        dump('shared-ranges.json', scale)
        receipt = json.loads((OUT / 'comparison-receipt.json').read_text())
        for name in SOURCES:
            receipt['cases'][name]['figures'] = json.loads((OUT / (name + '-top-figures.json')).read_text())
        receipt['vf_display_policy'] = 'Shared 0 to 0.5; higher values saturated; user requested'
        dump('comparison-receipt.json', receipt)
    finally:
        load(s, restore['pair'])
        assert p.native_iteration(s) == restore['native_iteration']
        assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - restore['clock']['film_elapsed_time']) < 1e-12
        dump('restored-session.json', {'pair': restore['pair'], 'native_iteration': p.native_iteration(s),
                                      'film_clock': dict(s.rp_vars('wall-film/solution-state')), 'solver_paused': True,
                                      'analysis_scope': 'TOP_DOWN_ONLY', 'vf_range': [0, .5]})
        print('VF_RANGE_SESSION_RESTORED_PAUSED', flush=True)


def adjust_bulk_vectors(s):
    restore = json.loads((p.OUT / 'paused-furthest-reopen.json').read_text())
    assert p.native_iteration(s) == restore['native_iteration'], 'Session changed; reconcile before replacement'
    assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - restore['clock']['film_elapsed_time']) < 1e-12
    try:
        for name, stem in SOURCES.items():
            record = json.loads((OUT / (name + '-inspection.json')).read_text())
            assert identity(stem) == record['pair'], 'Source pair changed'
            load(s, record['pair'])
            surfaces(s)
            obj, observed = vector(s, 'bulk-vectors', 'velocity', 'velocity-magnitude', 'ic-top', [0, 50])
            obj.options.scale = .042
            camera = dict(TOP)
            camera.update(width=4.5, height=3.75)
            if name == 'angled':
                camera['position'] = [TOP['position'][0] + .2, TOP['position'][1], TOP['position'][2]]
                camera['target'] = [TOP['target'][0] + .2, TOP['target'][1], TOP['target'][2]]
            path = FIG / (name + '-bulk-vectors.png')
            picture(s, obj, path, camera)
            actual = obj.get_state()
            assert math.isclose(actual['options']['scale'], .042, rel_tol=1e-12)
            updated = {'label': 'bulk-vectors', 'path': str(path), 'camera': camera, 'display_range': [0, 50],
                       'observed': observed, 'object': actual,
                       'presentation_revision': 'Shared 7% wider camera field and 20% larger native arrow scale; angled view panned +0.2m in X'}
            for suffix in ['-figures.json', '-top-figures.json']:
                figures = json.loads((OUT / (name + suffix)).read_text())
                dump(name + suffix, [updated if f['label'] == 'bulk-vectors' else f for f in figures])
            assert p.native_iteration(s) == record['native_iteration']
            assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - record['film_clock']['film_elapsed_time']) < 1e-12
            print('BULK_VECTOR_PRESENTATION_UPDATED', name, flush=True)
        receipt = json.loads((OUT / 'comparison-receipt.json').read_text())
        for name in SOURCES:
            receipt['cases'][name]['figures'] = json.loads((OUT / (name + '-top-figures.json')).read_text())
        receipt['vector_presentation_revision'] = 'All three top-down vector views: width 4.5m, height 3.75m, arrow factor 0.042. Angled camera +0.2m X only.'
        dump('comparison-receipt.json', receipt)
    finally:
        load(s, restore['pair'])
        assert p.native_iteration(s) == restore['native_iteration']
        assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - restore['clock']['film_elapsed_time']) < 1e-12
        dump('restored-session.json', {'pair': restore['pair'], 'native_iteration': p.native_iteration(s),
                                      'film_clock': dict(s.rp_vars('wall-film/solution-state')), 'solver_paused': True,
                                      'analysis_scope': 'TOP_DOWN_ONLY', 'vf_range': [0, .5],
                                      'vector_presentation_updated': True})
        print('BULK_VECTOR_SESSION_RESTORED_PAUSED', flush=True)


def redo_with_latest_baseline(s):
    restore = json.loads((p.OUT / 'paused-furthest-reopen.json').read_text())
    assert p.native_iteration(s) == restore['native_iteration'], 'Session changed; reconcile before replacement'
    assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - restore['clock']['film_elapsed_time']) < 1e-12
    baseline_pair = identity(SOURCES['baseline'])
    owner = json.loads((SOURCES['baseline'].parents[1] / 'run-manifest.json').read_text())
    assert baseline_pair == owner['accepted_terminal_pair'], 'New baseline is not the accepted source pair'
    try:
        baseline = inspect_case(s, 'baseline', baseline_pair)
        assert baseline['native_iteration'] == 31000
        assert abs(baseline['film_clock']['film_elapsed_time'] - .05805) < 1e-12
        facet_metrics(s, 'baseline')
        cases = {}
        for name in SOURCES:
            record = json.loads((OUT / (name + '-inspection.json')).read_text())
            assert identity(SOURCES[name]) == record['pair'], 'Source pair changed'
            if name != 'baseline':
                load(s, record['pair'])
                surfaces(s)
            figures = []
            for label, field in [('vf', 'phase-2-vof'), ('bulk-vectors', 'velocity'), ('tke', 'turb-kinetic-energy')]:
                camera = dict(TOP)
                if label == 'bulk-vectors':
                    obj, observed = vector(s, label, field, 'velocity-magnitude', 'ic-top', [0, 50])
                    assert observed['maximum'] <= 50, 'Velocity common range needs expansion'
                    obj.options.scale = .042
                    camera.update(width=4.5, height=3.75)
                    if name == 'angled':
                        camera['position'] = [TOP['position'][0] + .2, TOP['position'][1], TOP['position'][2]]
                        camera['target'] = [TOP['target'][0] + .2, TOP['target'][1], TOP['target'][2]]
                    display_range = [0, 50]
                else:
                    display_range = [0, .5] if label == 'vf' else [0, 25]
                    obj, observed = contour(s, label, field, 'ic-top', display_range)
                    if label == 'tke':
                        assert observed['maximum'] <= 25, 'TKE common range needs expansion'
                path = FIG / (name + '-' + label + '.png')
                picture(s, obj, path, camera)
                figures.append({'label': label, 'path': str(path), 'camera': camera,
                                'display_range': display_range, 'observed': observed, 'object': obj.get_state(),
                                'source_film_age_s': record['film_clock']['film_elapsed_time']})
                dump(name + '-top-figures.json', figures)
                print('BASELINE_REDO_FIGURE', name, label, flush=True)
            dump(name + '-figures.json', figures)
            assert p.native_iteration(s) == record['native_iteration']
            assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - record['film_clock']['film_elapsed_time']) < 1e-12
            cases[name] = {'source_pair': record['pair'], 'film_clock_s': record['film_clock']['film_elapsed_time'],
                           'figures': figures, 'visual_qa_passed': False}
        dump('comparison-receipt.json', {'status': 'REEXPORTED_WITH_ACCEPTED_58P05MS_BASELINE', 'cases': cases,
                                         'solve_issued': False, 'baseline_selection': 'Human selected latest accepted 58.05ms pair; no 100ms source available',
                                         'vf_display_policy': 'Shared 0 to 0.5; higher values saturated',
                                         'vector_presentation_revision': 'Field 4.5x3.75m; arrow factor 0.042; angled pan +0.2m X'})
    finally:
        load(s, restore['pair'])
        assert p.native_iteration(s) == restore['native_iteration']
        assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - restore['clock']['film_elapsed_time']) < 1e-12
        dump('restored-session.json', {'pair': restore['pair'], 'native_iteration': p.native_iteration(s),
                                      'film_clock': dict(s.rp_vars('wall-film/solution-state')), 'solver_paused': True,
                                      'analysis_scope': 'TOP_DOWN_ONLY', 'baseline_film_age_s': .05805})
        print('BASELINE_REDO_SESSION_RESTORED_PAUSED', flush=True)
