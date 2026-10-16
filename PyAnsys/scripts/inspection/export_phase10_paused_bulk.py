"""Native Fluent spatial figures and bulk reports for the paused N30862 pair.

Postprocessing only. No iterate, initialize, save case/data or scientific edits.
"""
from pathlib import Path
import hashlib
import json
import math
import time

import numpy as np
import run_phase10_proposed_design as p

FIG = p.REPO / 'Project/experiments/phase-10-proposed-design/figures/paused-23p705ms'


def run(s):
    pre = json.loads((p.OUT / 'spatial-preflight.json').read_text())
    source = json.loads((p.OUT / 'paused-furthest-reopen.json').read_text())
    assert p.native_iteration(s) == 30862
    assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - .023705) < 1e-12
    assert not any(s.settings.solution.controls.equations.get_state().values())
    for key in ['case', 'data']:
        with Path(source['pair'][key]).open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == source['pair'][key + '_sha256']
    FIG.mkdir(parents=True, exist_ok=True)
    report = {'source_pair': source['pair'], 'native_iteration': 30862, 'film_time_s': .023705,
              'bulk_frozen': True, 'solve_issued': False, 'figures': [],
              'view_basis': 'Top-down X-Z cut at mean liquid inlet height; inlet-facing central Y-Z cut, parallel to actual inlet faces',
              'inlet_geometry_m': pre['inlet_geometry']}
    zones = s.settings.setup.cell_zone_conditions.fluid.get_object_names()
    report['bulk_cell_zones'] = zones
    jobs = [('volume', 'volume-zonevol', None), ('mixture-mass', 'volume-mass', None),
            ('liquid-vf-mean', 'volume-average', 'phase-2-vof'),
            ('speed-mean', 'volume-average', 'velocity-magnitude'), ('speed-max', 'volume-max', 'velocity-magnitude'),
            ('k-mean', 'volume-average', 'turb-kinetic-energy'), ('k-max', 'volume-max', 'turb-kinetic-energy'),
            ('epsilon-mean', 'volume-average', 'turb-diss-rate'), ('pressure-mean', 'volume-average', 'pressure')]
    rd = s.settings.solution.report_definitions
    names = []
    for label, kind, field in jobs:
        name = 'p10-bulk-' + label
        if name not in rd.volume.get_object_names():
            rd.volume.create(name=name)
        obj = rd.volume[name]
        obj.report_type = kind
        obj.cell_zones = zones
        if field:
            assert field in obj.field.allowed_values(), field
            obj.field = field
        names.append(name)
    names += list(json.loads((p.OUT / 'run-manifest.json').read_text())['paths'])
    values = {}
    for item in rd.compute(report_defs=names):
        values.update(item)
    report['native_reports'] = values
    report['report_definitions'] = {name: rd.volume[name].get_state() for name in names if name.startswith('p10-bulk-')}
    p.dump('paused-bulk-export.json', report)
    graphics = s.settings.results.graphics
    planes = s.settings.results.surfaces.plane_surface
    inlet_y = pre['inlet_geometry']['liquidinlet']['mean'][1]
    configs = {
        'top-down-inlet-height': {'name': 'p10-inlet-xz', 'plane': {'method': 'zx-plane', 'y': inlet_y},
                                'position': [-.8, inlet_y + 10, -.20], 'target': [-.8, inlet_y, -.20],
                                'up': [0, 0, -1], 'width': 4.2, 'height': 3.5, 'resolution': [2400, 2000]},
        'inlet-facing-central': {'name': 'p10-centre-yz', 'plane': {'method': 'yz-plane', 'x': 0.0},
                                 'position': [-10, 3.50, 0], 'target': [0, 3.50, 0],
                                 'up': [0, 1, 0], 'width': 3.0, 'height': 7.8, 'resolution': [1600, 3200]}}
    graphics.colors.graphics_color_theme = 'white'
    graphics.lighting.lights_on = False
    graphics.windows.axes.visible = True
    if graphics.windows.logo.is_active():
        graphics.windows.logo = False
    objects = []
    for view, config in configs.items():
        if config['name'] not in planes.get_object_names():
            planes.create(name=config['name'])
        planes[config['name']].set_state(config['plane'])
        for label, field in [('liquid-volume-fraction', 'phase-2-vof'), ('turbulent-kinetic-energy', 'turb-kinetic-energy')]:
            name = 'P10-' + ('VF' if field == 'phase-2-vof' else 'k') + '-' + ('top' if view.startswith('top') else 'inlet')
            if name not in graphics.contour.get_object_names():
                graphics.contour.create(name=name)
            obj = graphics.contour[name]
            assert field in obj.field.allowed_values()
            obj.set_state({'field': field, 'surfaces_list': [config['name']],
                           'range_options': {'global_range': False, 'auto_range': True, 'clip_to_range': False},
                           'options': {'filled': True, 'node_values': True, 'boundary_values': False, 'contour_lines': False}})
            obj.range_options.compute()
            observed = obj.range_options.get_state()
            objects.append((view, config, label, field, obj, observed))
    kmax = max(float(r['maximum']) for _, _, _, f, _, r in objects if f == 'turb-kinetic-energy')
    scale = 10 ** math.floor(math.log10(max(kmax, 1e-30)))
    kupper = next(v * scale for v in [1, 2, 5, 10] if v * scale >= kmax)
    for view, config, label, field, obj, observed in objects:
        upper = 1.0 if field == 'phase-2-vof' else kupper
        obj.range_options.set_state({'global_range': False, 'auto_range': False, 'clip_to_range': False,
                                     'minimum': 0, 'maximum': upper})
        cmap = obj.color_map.get_state()
        cmap.update({'font_size': .016, 'length': .48, 'width': 4.0})
        obj.color_map.set_state(cmap)
        obj.display()
        camera = graphics.views.camera
        camera.projection(type='orthographic')
        camera.position(xyz=config['position']); camera.target(xyz=config['target']); camera.up_vector(xyz=config['up'])
        graphics.views.auto_scale()
        camera.position(xyz=config['position']); camera.target(xyz=config['target']); camera.up_vector(xyz=config['up'])
        camera.field(width=config['width'], height=config['height'])
        if graphics.picture.use_window_resolution.is_active():
            graphics.picture.use_window_resolution = False
        graphics.picture.invert_background = False
        graphics.picture.landscape = view.startswith('top')
        graphics.picture.x_resolution, graphics.picture.y_resolution = config['resolution']
        output = FIG / (view + '-' + label + '.png')
        graphics.picture.save_picture(file_name=str(output))
        assert output.is_file() and output.stat().st_size > 1000
        report['figures'].append({'path': str(output), 'view': view, 'field': field, 'observed_range': observed,
                                  'display_range': [0, upper], 'plane': planes[config['name']].get_state(), 'camera': config})
        p.dump('paused-bulk-export.json', report)
        print('P10_NATIVE_EXPORT', str(output), flush=True)
    assert p.native_iteration(s) == 30862
    assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - .023705) < 1e-12
    report.update(status='EXPORTED_NATIVE_PAUSED_UNCHANGED', completed_epoch=time.time())
    p.dump('paused-bulk-export.json', report)
