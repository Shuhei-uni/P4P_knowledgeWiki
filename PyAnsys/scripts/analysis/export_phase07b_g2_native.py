"""Export matched N5000 Fluent contours, without solving or overwriting checkpoints.

Only Fluent APIs touch the PC. Native PNG bytes and SHA256 are read through
Fluent's embedded Python API because its Scheme text ports translate Windows
line endings and stop at Ctrl-Z, even with open-binary-input-file.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import base64
import fcntl
import hashlib
import json
import math
import signal
import sys

import numpy as np
from PIL import Image  # Validate native files only; never draw or alter them.

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'scripts/setup'))
from prepare_phase07b_collector import connect, ROOT, remote_file_exists, read_text

CASES = [
    ('S40 baseline', 'S40', 'p7b-s040-20260921T013001Z'),
    ('S40-T020', 'T020', 'p7b-s40-t020-resume-20260921T231240Z'),
    ('S40-T100', 'T100', 'p7b-s40-t100-20260922T022956Z'),
]
PLANES = [('y0p5', 'y', .5), ('y1p5', 'y', 1.5),
          ('y3p0', 'y', 3.), ('y5p0', 'y', 5.), ('x0', 'x', 0.), ('z0', 'z', 0.)]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--preview', action='store_true', help='Only T100 x0 and y0p5 VOF candidates')
    ap.add_argument('--axial-only', action='store_true', help='Repair only the six axial labels; no horizontal re-export')
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lock = (BASE / 'output/phase07b-server1-controller.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('Native export deadline; reconcile before retry')))
    record = {'status': 'EXPORTING', 'additional_iterations': 0,
              'exporter': str(Path(__file__).resolve()), 'figures': [], 'sources': {},
              'transfer': 'Fluent Scheme %py-eval: base64 bytes plus independent remote SHA256; no shell',
              'claim_limit': 'Finite discovery endpoints, not converged or physically qualified.',
              'created_utc': datetime.now(timezone.utc).isoformat()}

    def persist():
        (args.output / 'manifest.json').write_text(json.dumps(record, indent=2, default=str) + '\n')

    def py_eval(code):
        return s.scheme.eval('(%py-eval ' + json.dumps(code) + ')')

    def transfer(remote, local):
        data = base64.b64decode(py_eval("__import__('base64').b64encode(__import__('pathlib').Path(" + repr(remote) + ").read_bytes()).decode('ascii')"), validate=True)
        sha = hashlib.sha256(data).hexdigest()
        assert sha == py_eval("__import__('hashlib').sha256(__import__('pathlib').Path(" + repr(remote) + ").read_bytes()).hexdigest()")
        assert data.startswith(b'\x89PNG\r\n\x1a\n')
        local.write_bytes(data)
        with Image.open(local) as im:
            dimensions = im.size
            im.verify()
        return sha, dimensions

    manifests = {name: json.loads((BASE / 'output' / run / 'manifest.json').read_text()) for name, _, run in CASES}
    for m in manifests.values():
        assert m['status'] == 'HORIZON_COMPLETE_ANALYSIS_PENDING' and m['completed_iterations'] == 5000
    peak = 0
    for _, _, run in CASES:
        for f in (BASE / 'output' / run / 'final-sections').glob('*.npz'):
            with np.load(f) as a:
                peak = max(peak, float(a['velocity-magnitude'].max()))
    speed_max = math.ceil(peak / 10) * 10
    record['shared_ranges'] = {'phase-2-vof': [0, 1], 'velocity-magnitude': [0, speed_max]}
    record['speed_range_basis'] = 'Outward-rounded union of native N5000 facet values on all 12 horizontal cuts; live surface ranges checked below.'
    persist()
    signal.alarm(60)
    s = connect(server_id=1, start_transcript=False, tcp_timeout_seconds=5)
    s.transcript.start(file_name=str(args.output / 'export.trn'), write_to_stdout=False)
    current = manifests['S40-T100']
    assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value() == 5000
    live_sink = s.settings.setup.named_expressions['P7bSink'].definition()
    matching = [(label, m) for label, m in manifests.items() if m['definitions']['P7bSink'] == live_sink]
    assert len(matching) == 1, 'Reconcile the loaded source before any reload'
    live_label, live_manifest = matching[0]
    for k, v in live_manifest['definitions'].items():
        assert s.settings.setup.named_expressions[k].definition() == v
    live_summary = json.loads((BASE / 'output' / live_manifest['run_id'] / 'analysis/summary.json').read_text())
    live_water = s.settings.setup.named_expressions['P7bWaterVolume'].get_value()
    assert math.isclose(live_water, live_summary['latest_metrics']['whole_water_volume']['value'], rel_tol=1e-12)
    assert all(remote_file_exists(s, live_manifest['pairs']['final'].replace('.cas.h5', x)) for x in ['.cas.h5', '.dat.h5'])
    assert all(remote_file_exists(s, current['pairs']['final'].replace('.cas.h5', x)) for x in ['.cas.h5', '.dat.h5'])
    record['preserved_current_endpoint'] = current['pairs']['final']
    record['reconciled_start'] = {'case_id': live_label, 'iteration': 5000, 'water_volume': live_water,
                                'preserved_pair': live_manifest['pairs']['final']}
    record['fluent_version'] = str(s.get_fluent_version())
    selected = [CASES[-1]] if args.preview else CASES
    loaded_pair = live_manifest['pairs']['final']
    for label, short, run in selected:
        signal.alarm(600)
        m = manifests[label]
        pair = m['pairs']['final']
        assert all(remote_file_exists(s, pair.replace('.cas.h5', x)) for x in ['.cas.h5', '.dat.h5'])
        if pair != loaded_pair:
            print('load', label, flush=True)
            s.settings.file.read_case_data(file_name=pair)
        else:
            print('use reconciled endpoint', label, flush=True)
        assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value() == 5000
        for k, v in m['definitions'].items():
            assert s.settings.setup.named_expressions[k].definition() == v
        record['sources'][label] = {'case': pair, 'data': pair.replace('.cas.h5', '.dat.h5'), 'iteration': 5000,
                                  'water_volume_readback': s.settings.setup.named_expressions['P7bWaterVolume'].get_value()}
        expected_water = json.loads((BASE / 'output' / run / 'analysis/summary.json').read_text())['latest_metrics']['whole_water_volume']['value']
        assert math.isclose(record['sources'][label]['water_volume_readback'], expected_water, rel_tol=1e-12)
        loaded_pair = pair
        persist()
        planes = [PLANES[4], PLANES[0]] if args.preview else (PLANES[4:] if args.axial_only else PLANES)
        for plane, axis, value in planes:
            signal.alarm(100)
            iso = s.settings.results.surfaces.iso_surface
            surface = 'p7b-section-' + plane if axis == 'y' else 'p7b-e2-' + plane
            if surface not in iso.get_object_names():
                iso.create(name=surface)
                iso = s.settings.results.surfaces.iso_surface
                assert axis + '-coordinate' in iso[surface].field.allowed_values()
                iso[surface].set_state({'field': axis + '-coordinate', 'iso_values': [value]})
            surface_state = s.settings.results.surfaces.iso_surface[surface].get_state()
            assert surface_state['field'] == axis + '-coordinate' and surface_state['iso_values'] == [value]
            fields = ['phase-2-vof'] if args.preview or axis != 'y' else ['phase-2-vof', 'velocity-magnitude']
            for field in fields:
                signal.alarm(100)
                slug = short + '-N5000-' + plane + ('-liquid' if field == 'phase-2-vof' else '-speed')
                print('export', slug, flush=True)
                graphics = s.settings.results.graphics
                graphics.contour.create(name=slug)
                c = s.settings.results.graphics.contour[slug]
                assert field in c.field.allowed_values() and surface in c.surfaces_list.allowed_values()
                c.set_state({'field': field, 'surfaces_list': [surface], 'filled': True, 'node_values': False,
                             'draw_mesh': False, 'range_options': {'global_range': False, 'auto_range': True}})
                c.range_options.compute()
                observed = c.range_options.get_state()
                low, high = record['shared_ranges'][field]
                assert observed['minimum'] >= low - 1e-6 and observed['maximum'] <= high + 1e-6
                c.range_options.set_state({'global_range': False, 'auto_range': False, 'minimum': low, 'maximum': high, 'clip_to_range': False})
                c.colorings.set_state({'banded': False, 'smooth': True})
                c.color_map.set_state({'color': 'sequential-viridis', 'size': 11, 'log_scale': False,
                                      'format': '%0.2f' if field == 'phase-2-vof' else '%0.0f',
                                      'font_automatic': False, 'font_size': 24 if axis == 'y' else 18, 'visible': True})
                graphics.windows.logo = False
                graphics.windows.text.visible = False
                pic = graphics.picture
                pic.use_window_resolution = False
                pic.landscape = axis == 'y'
                pic.x_resolution = 2400 if axis == 'y' else 1600
                pic.y_resolution = 1800 if axis == 'y' else 2400
                # display() replaces the active display; no add_to_graphics or vectors.
                c.display()
                view = graphics.views
                view.auto_scale()
                target = [0, value, 0] if axis == 'y' else [0, 2.755, 0]
                position = [0, value + 20, 0] if axis == 'y' else ([20, 2.755, 0] if axis == 'x' else [0, 2.755, 20])
                up = [0, 0, -1] if axis == 'y' else [0, 1, 0]
                size = [3.2, 2.7] if axis == 'y' else [6.0, 10.2]
                view.camera.projection(type='orthographic')
                view.camera.position(xyz=position)
                view.camera.target(xyz=target)
                view.camera.up_vector(xyz=up)
                view.camera.field(width=size[0], height=size[1])
                # A repeated view name prompts for overwrite and blocks the RPC.
                # Each scalar export owns a unique view, including its field.
                view_name = 'g2-' + stamp + '-' + slug
                view.save_view(view_name=view_name)
                remote_view = ROOT + '/exports/g2-' + stamp + '-' + slug + '.vw'
                view.write_views(file_name=remote_view, view_list=[view_name])
                view_text = read_text(s, remote_view)
                (args.output / (slug + '.vw')).write_text(view_text)
                remote = ROOT + '/exports/g2-' + stamp + '-' + slug + '.png'
                assert not remote_file_exists(s, remote)
                state = c.get_state()
                pic_state = pic.get_state()
                pic.save_picture(file_name=remote)
                assert remote_file_exists(s, remote)
                local = args.output / (slug + '.png')
                sha, dimensions = transfer(remote, local)
                assert dimensions == ((2400, 1800) if axis == 'y' else (1600, 2400))
                record['figures'].append({'case_id': label, 'iteration': 5000, 'plane': plane, 'surface': surface,
                    'surface_state': surface_state, 'field': field, 'units': '1' if field == 'phase-2-vof' else 'm/s',
                    'observed_surface_range': observed, 'range_options': state['range_options'],
                    'contour_state': state, 'picture_state': pic_state, 'camera': {'position': position, 'target': target,
                    'up_vector': up, 'projection': 'orthographic', 'explicit_field_after_auto_scale': size, 'post_auto_scale_zoom': 1,
                    'native_view_readback': str((args.output / (slug + '.vw')).resolve())},
                    'local_file': str(local.resolve()), 'remote_file': remote, 'sha256': sha,
                    'remote_hash_matches': True, 'dimensions': dimensions, 'visual_qa': 'PENDING'})
                persist()
                graphics.contour.delete(name_list=[slug])
    signal.alarm(600)
    if loaded_pair != current['pairs']['final']:
        s.settings.file.read_case_data(file_name=current['pairs']['final'])
    assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value() == 5000
    assert s.settings.setup.named_expressions['P7bSink'].definition() == current['definitions']['P7bSink']
    assert math.isclose(s.settings.setup.named_expressions['P7bWaterVolume'].get_value(),
                        record['sources']['S40-T100']['water_volume_readback'], rel_tol=1e-12)
    record['restored_endpoint'] = current['pairs']['final']
    record['status'] = 'NATIVE_EXPORTS_COMPLETE_VISUAL_QA_PENDING'
    persist()
    s.transcript.stop()
    signal.alarm(0)
    print('COMPLETE', args.output, flush=True)


if __name__ == '__main__':
    main()
