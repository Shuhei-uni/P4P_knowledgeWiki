"""Native vector-only inlet-height cut of the verified paused Phase 10 pair."""
import json
import time
import run_phase10_proposed_design as p
from export_phase10_paused_bulk import FIG


def run(s):
    receipt = json.loads((p.OUT / 'paused-bulk-export.json').read_text())
    config = next(f['camera'] for f in receipt['figures'] if f['view'].startswith('top'))
    assert p.native_iteration(s) == 30862
    graphics = s.settings.results.graphics
    obj = graphics.vector['P10-top-velocity']
    obj.set_state({'vector_field': 'velocity', 'field': 'velocity-magnitude',
                   'surfaces_list': [config['name']],
                   'range_options': {'global_range': False, 'auto_range': True, 'clip_to_range': False},
                   'options': {'auto_scale': True, 'vector_style': '3d arrow', 'scale': .04, 'skip': 0},
                   'vector_opt': {'in_plane': True, 'fixed_length': True, 'color': ''}})
    obj.range_options.compute()
    observed = obj.range_options.get_state()
    upper = (int(float(observed['maximum']) / 10) + 1) * 10
    obj.range_options.set_state({'global_range': False, 'auto_range': False, 'clip_to_range': False,
                                 'minimum': 0, 'maximum': upper})
    cmap = obj.color_map.get_state()
    cmap.update({'font_size': .016, 'length': .48, 'width': 4.0, 'visible': True})
    obj.color_map.set_state(cmap)
    obj.display()
    camera = graphics.views.camera
    camera.projection(type='orthographic')
    camera.position(xyz=config['position']); camera.target(xyz=config['target']); camera.up_vector(xyz=config['up'])
    camera.field(width=config['width'], height=config['height'])
    if graphics.picture.use_window_resolution.is_active():
        graphics.picture.use_window_resolution = False
    graphics.picture.invert_background = False
    graphics.picture.landscape = True
    graphics.picture.x_resolution, graphics.picture.y_resolution = config['resolution']
    path = FIG / 'top-down-inlet-height-velocity-vectors.png'
    graphics.picture.save_picture(file_name=str(path))
    assert path.is_file() and path.stat().st_size > 1000
    assert p.native_iteration(s) == 30862
    assert abs(dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] - .023705) < 1e-12
    p.dump('paused-top-vectors.json', {'source_pair': receipt['source_pair'], 'path': str(path),
                                     'film_time_s': .023705, 'camera': config,
                                     'vector': obj.get_state(), 'observed_speed_range': observed,
                                     'interpretation': 'All vectors; in-plane direction, fixed length, colour gives 3D mixture speed',
                                     'solve_issued': False, 'completed_epoch': time.time()})
    print('P10_NATIVE_VECTOR_EXPORT', str(path), flush=True)
