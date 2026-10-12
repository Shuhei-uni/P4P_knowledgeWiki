"""Native Fluent spatial reference from the retained Server 6 N84000 pair.

Postprocessing only: no solve, initialization, patch, or scientific setter.
"""
from pathlib import Path, PureWindowsPath
import argparse, base64, hashlib, json, math, struct, sys, time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts/setup')]
from phase9_server6_slit_common import attach, run
from run_phase9_server6_slit_ewf import lane_file_sha256, lane_save
from deploy_phase9_server6_slit_ewf import quote

OUT = ROOT/'output/phase10-proposed-design/20261012/slit154k-50p9ms-reference'
FIG = ROOT.parent/'Project/experiments/phase-10-proposed-design/vertical-slit154k/figures/slit154k-50p9ms'
SOURCE = ROOT/'output/phase9-server6-slit154k/20261010/retained-50p9ms.json'

def dump(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_text(json.dumps(value, indent=2, default=str)+'\n')

def read_state(s):
    names = ['p72s3-pressure-inlet', 'p72s3-pressure-outlet',
             'v2-total-liquid-mass', 'v2-total-vapor-mass', 'p72d-total-mass']
    return {'native_iteration': run.native_iteration(s), 'film': run.film(s),
            'bulk_equations': s.settings.solution.controls.equations.get_state(),
            'reports': s.settings.solution.report_definitions.compute(report_defs=names)}

def identity(s):
    run.require_idle(s)
    assert not s.settings.solution.run_calculation.iterating()
    state = read_state(s)
    assert state['native_iteration'] == 84000
    assert math.isclose(state['film']['film_elapsed_time'], .0509, abs_tol=1e-10)
    assert not any(state['bulk_equations'].values())
    return state

def nice_max(value):
    assert math.isfinite(value) and value > 0
    base = 10**math.floor(math.log10(value))
    return next(n*base for n in [1, 2, 5, 10] if n*base >= value)

def fetch(s, remote, target, scratch):
    encoded = remote+'.b64.txt'
    assert not run.remote_file_exists(s, encoded)
    code = ("$ErrorActionPreference='Stop'; [IO.File]::WriteAllText("+quote(encoded)+
            ",[Convert]::ToBase64String([IO.File]::ReadAllBytes("+quote(remote)+
            ")),[Text.Encoding]::ASCII)")
    assert run.base.powershell(s, code) in (0, None)
    payload = base64.b64decode(run.read_text(s, encoded).strip(), validate=True)
    assert payload.startswith(b'\x89PNG\r\n\x1a\n')
    digest = hashlib.sha256(payload).hexdigest()
    assert lane_file_sha256(s, remote, scratch) == digest
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.exists()
    target.write_bytes(payload)
    return {'sha256': digest, 'bytes': len(payload),
            'resolution': list(struct.unpack('>II', payload[16:24])),
            'native_pixels_unmodified': True}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['export', 'persist'], default='export')
    args = parser.parse_args()
    s = attach()
    before = identity(s)
    g = s.settings.results.graphics
    if args.stage == 'persist':
        receipt = json.loads((OUT/'figure-export.json').read_text())
        assert receipt['status'] == 'NATIVE_EXPORTS_COMPLETE'
        folder = PureWindowsPath(receipt['host_folder'])
        pair = lane_save(s, folder, 'derived-graphics-N84000-'+str(time.time_ns()))
        dump('derived-graphics-pending.json', {'pair': pair, 'before': before})
        run.load(s, pair)
        after = identity(s)
        assert before == after
        planes = s.settings.results.surfaces.plane_surface.get_object_names()
        assert {'p10-slit154k-inlet-top', 'p10-slit154k-radial-vertical'} <= set(planes)
        for figure in receipt['figures']:
            objects = g.contour if figure['kind'] == 'contour' else g.vector
            assert objects[figure['object_name']].get_state() == figure['graphics_readback']
        dump('derived-graphics-reopen.json', {'status': 'GRAPHICS_PAIR_REOPEN_VERIFIED',
             'pair': pair, 'before': before, 'after': after, 'new_solve_calls': 0,
             'source_pair_overwritten': False})
        return
    assert not (OUT/'figure-export.json').exists(), 'Reconcile previous export; do not replay blindly'
    source = json.loads(SOURCE.read_text())
    inspection = json.loads((OUT/'native-inspection.json').read_text())
    api = json.loads((OUT/'graphics-api-inspection.json').read_text())
    stamp = str(time.time_ns())
    folder = run.WORK/('phase10-spatial-reference-N84000-'+stamp)
    run.ensure_remote_directory(s, str(folder/'scratch'))
    for key in ['case', 'data']:
        assert lane_file_sha256(s, source['pair'][key], str(folder/'scratch'/(key+'.txt'))) == source['pair'][key+'_sha256']
    inlet = inspection['bounds']['liquidinlet']
    y = .5*(inlet['vertex_min_m'][1]+inlet['vertex_max_m'][1])
    slit = np.array(inspection['bounds']['verticalslit-wall-vertical-slit']['centroid_mean_m'])
    normal = np.array([-slit[2], 0., slit[0]])
    normal /= np.linalg.norm(normal)
    planes = s.settings.results.surfaces.plane_surface
    top, vertical = 'p10-slit154k-inlet-top', 'p10-slit154k-radial-vertical'
    for name in [top, vertical]:
        if name not in planes.get_object_names(): planes.create(name=name)
    planes[top].set_state({'method': 'zx-plane', 'y': y})
    planes[vertical].method = 'point-and-normal'
    normal_method = planes[vertical].normal_computation_method.allowed_values()
    assert 'normal' in normal_method, normal_method
    planes[vertical].set_state({'point': slit.tolist(),
                              'normal_computation_method': 'normal',
                              'normal': normal.tolist()})
    g.colors.graphics_color_theme = 'white'
    g.colors.titles.set_state({k: '' for k in ['left_top','left_bottom','right_top','right_middle','right_bottom']})
    g.windows.logo = False
    g.windows.axes.visible = False
    g.lighting.lights_on = False
    g.picture.invert_background = False
    g.picture.use_window_resolution = False
    g.picture.driver_options.hardcopy_format = 'png'
    g.picture.color_mode = 'color'
    cameras = {
        'top': {'target': [-.45, y, -.2], 'position': [-.45, y+12, -.2],
                'up': [0,0,-1], 'width': 4.0, 'height': 3.0, 'resolution': [2400,1800]},
        'vertical': {'target': [0,3.5,0], 'position': (normal*12+np.array([0,3.5,0])).tolist(),
                     'up': [0,1,0], 'width': 3.6, 'height': 7.6, 'resolution': [1400,2600]},
        'slit-detail': {'target': [-.1,2.454,-.1],
                        'position': (normal*12+np.array([-.1,2.454,-.1])).tolist(),
                        'up': [0,1,0], 'width': 3.4, 'height': 2.55, 'resolution': [2400,1800]}}
    jobs = [('topdown-liquid-volume-fraction','contour','phase-2-vof',top,'top',[0,1]),
            ('topdown-turbulent-kinetic-energy','contour','turb-kinetic-energy',top,'top',None),
            ('topdown-bulk-velocity-vectors','vector','velocity-magnitude',top,'top',None),
            ('vertical-slit-velocity-vectors','vector','velocity-magnitude',vertical,'vertical',None),
            ('vertical-slit-velocity-vectors-detail','vector','velocity-magnitude',vertical,'slit-detail',None)]
    receipt = {'status':'EXPORTING', 'server_id':'6', 'mesh_cells':154063,
               'source_pair':source['pair'], 'source_readback':before,
               'source_classification':'RETAINED_FINITE_CHECKPOINT_NUMERICAL_ACCURACY_UNQUALIFIED',
               'host_folder':str(folder), 'geometry_units':'m',
               'planes':{top:planes[top].get_state(),vertical:planes[vertical].get_state()},
               'vertical_plane_basis':'Through native slit centroid and nominal vessel axis x=z=0',
               'figures':[], 'new_solve_calls':0,
               'claim_limit':'Frozen bulk diagnostic from vertical slit; not the Phase10 angled-slit result. Film age does not date a transient bulk solve.'}
    dump('figure-export.json', receipt)
    velocity_max = None
    for label, kind, field, surface, view, limits in jobs:
        objects = g.contour if kind == 'contour' else g.vector
        name = 'p10-slit154k-'+label
        if name not in objects.get_object_names(): objects.create(name=name)
        obj = objects[name]
        assert field in api[kind]['field_allowed']
        obj.set_state({'field':field, 'surfaces_list':[surface],
                       'range_options':{'global_range':False,'auto_range':True,'clip_to_range':False}})
        if kind == 'contour':
            obj.options.set_state({'filled':True,'node_values':True,'boundary_values':False,'contour_lines':False})
            obj.colorings.set_state({'banded':False,'smooth':True})
        else:
            obj.vector_field = 'velocity'
            styles = obj.options.vector_style.allowed_values()
            assert 'arrow' in styles, styles
            obj.options.set_state({'auto_scale':False,'vector_style':'arrow','scale':.5,'skip':0})
            obj.vector_opt.set_state({'in_plane':True,'fixed_length':True,'color':''})
        if kind == 'vector' and velocity_max is None:
            obj.range_options.global_range = True
            obj.range_options.compute()
            velocity_max = nice_max(obj.range_options.maximum.get_state())
            obj.range_options.global_range = False
        obj.range_options.compute()
        observed = obj.range_options.get_state()
        if limits is None:
            if kind == 'vector':
                assert observed['maximum'] <= velocity_max
                limits = [0,velocity_max]
            else: limits = [0,nice_max(observed['maximum'])]
        obj.range_options.set_state({'global_range':False,'auto_range':False,'clip_to_range':False,
                                     'minimum':limits[0],'maximum':limits[1]})
        obj.color_map.set_state({'visible':True,'font_automatic':False,'font_size':.018,
                                 'length':.48,'width':3.,'format':'%0.2g','color':'field-velocity','title_elements':'Variable'})
        obj.display()
        c = cameras[view]
        camera = g.views.camera
        camera.projection(type='orthographic')
        camera.position(xyz=c['position']);camera.target(xyz=c['target']);camera.up_vector(xyz=c['up'])
        g.views.auto_scale()
        camera.position(xyz=c['position']);camera.target(xyz=c['target']);camera.up_vector(xyz=c['up'])
        camera.field(width=c['width'],height=c['height'])
        g.picture.landscape = view != 'vertical'
        g.picture.x_resolution, g.picture.y_resolution = c['resolution']
        remote = str(folder/(label+'.png'))
        assert not run.remote_file_exists(s,remote)
        g.picture.save_picture(file_name=remote)
        item = {'name':label,'kind':kind,'field':field,'surface':surface,'object_name':name,
                'observed_range':observed,'display_range':limits,'camera':c,
                'remote':remote,'local':str(FIG/(label+'.png')),
                'graphics_readback':obj.get_state(),'visual_qa':'PENDING'}
        item.update(fetch(s,remote,FIG/(label+'.png'),str(folder/'scratch'/(label+'-png-hash.txt'))))
        assert item['resolution'] == c['resolution']
        receipt['figures'].append(item)
        dump('figure-export.json', receipt)
        print('NATIVE_EXPORTED',label,observed,flush=True)
    after = identity(s)
    assert after == before
    receipt.update(status='NATIVE_EXPORTS_COMPLETE', scientific_state_unchanged=True,
                   after=after, source_pair_overwritten=False)
    dump('figure-export.json',receipt)

if __name__ == '__main__': main()
