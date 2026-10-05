"""Export matched native Fluent contours; restore the preserved adaptive endpoint."""
from pathlib import Path
import base64
import functools
import hashlib
import json
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from run_phase72a_stage3_server3 import OUT, WORK, state, powershell
from run_phase72a_local_film_replay import require_match
from pyansys_fluent.connection import connect
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256

PROJECT = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction'
FIG = PROJECT / 'figures'


def main():
    import ansys.fluent.core._grpc_services as low
    import ansys.fluent.core.services as high
    from ansys.fluent.core.utils.fluent_version import FluentVersion
    from ansys.fluent.core import config
    low._server_supports_v1 = lambda channel: False
    high.create_service_factory = functools.partial(high.create_service_factory, product_version=FluentVersion.v252)
    # The health RPC times out on this idle endpoint; authenticated product and
    # controller RPCs respond. Prove version, idle state and exact fields below.
    config.check_health = False
    s = connect('3', start_transcript=False, tcp_timeout_seconds=5)
    assert '2025 R2' in str(s.get_fluent_version())
    assert s.settings.solution.run_calculation.iterate.is_active()
    manifest = json.loads((OUT / 'run-manifest.json').read_text())
    assert manifest['status'] == 'STARTUP_SCREENS_COMPLETE_ANALYSIS_REQUIRED'
    final = json.loads((OUT / 'adaptive-endpoint-N6000.json').read_text())
    require_match(state(s)['readback'], final['state']['readback'])
    assert int(s.settings.setup.named_expressions['P71V2Iteration'].get_value()) == 6000
    pairs = {'reference': manifest['reference_pair'], 'bulk-dry': manifest['film_start_pair'],
             'fixed': json.loads((OUT / 'fixed-endpoint-N6000.json').read_text())['pair'],
             'adaptive': final['pair']}
    expected = {'reference': json.loads((OUT / 'reference-state.json').read_text()),
                'bulk-dry': manifest['film_start_state'],
                'fixed': json.loads((OUT / 'fixed-endpoint-N6000.json').read_text())['state'],
                'adaptive': final['state']}
    preview = '--preview' in sys.argv
    manifest_path = OUT / ('native-camera-preview.json' if preview else 'native-figure-manifest.json')
    if preview:
        pairs = {'reference': pairs['reference']}
    record = {'status': 'EXPORTING', 'server_id': '3', 'solve_issued': False,
              'source_pairs': pairs, 'figures': [], 'restored_adaptive_endpoint': False,
              'brief': {'question': 'Does short startup reproduce carrier distribution and developed wall film?',
                        'geometry': 'Verified 60964-cell separator, coordinates in m',
                        'plane': 'XY at Z=0 m; orthographic +Z view',
                        'film_surface': 'wall; only active EWF wall in verified boundary readback',
                        'comparison': 'Reference N33586; dry N3000; fixed/adaptive N6000 after 3 ms',
                        'ranges': {'phase-2-vof': [0, 1], 'velocity-magnitude': [0, 85],
                                   'film-thickness': [0, .00035]},
                        'claim_limit': 'Finite startup states; no stationarity or mesh-convergence claim'}}
    stamp = time.strftime('%H%M%S')
    remote = WORK / 'figures' / ('native-' + stamp)
    marker = str(remote / 'directory-created.txt')
    powershell(s, f"[IO.Directory]::CreateDirectory('{remote}') | Out-Null; [IO.File]::WriteAllText('{marker}','native export directory')")
    if not remote_file_exists(s, marker):
        raise RuntimeError('Could not verify native export directory')
    FIG.mkdir(parents=True, exist_ok=True)
    try:
        for label, pair in pairs.items():
            for kind in ['case', 'data']:
                digest = remote_file_sha256(s, pair[kind], str(WORK / 'scratch' / f'figures-{stamp}-{label}-{kind}.sha256.txt'))
                if digest != pair[kind + '_sha256']:
                    raise RuntimeError(f'Source identity mismatch: {label} {kind}')
            s.settings.file.read_case(file_name=pair['case'])
            s.settings.file.read_data(file_name=pair['data'])
            require_match(state(s)['readback'], expected[label]['readback'])
            n = int(s.settings.setup.named_expressions['P71V2Iteration'].get_value())
            if n != pair['native_iteration']:
                raise RuntimeError('Loaded coordinate differs from source pair')
            planes = s.settings.results.surfaces.plane_surface
            plane = 'p72s3-report-xy-z0'
            if plane not in planes.get_object_names():
                planes.create(name=plane)
            planes[plane].set_state({'method': 'xy-plane', 'z': 0.0})
            graphics = s.settings.results.graphics
            fields = [('phase-2-vof', [plane], [0, 1]),
                      ('velocity-magnitude', [plane], [0, 85])]
            if label != 'bulk-dry':
                fields.append(('film-thickness', ['wall'], [0, .00035]))
            if preview:
                fields = [f for f in fields if f[0] == 'film-thickness']
            for field, surfaces, limits in fields:
                name = {'phase-2-vof': 'Liquid-fraction', 'velocity-magnitude': 'Velocity',
                        'film-thickness': 'Film-thickness'}[field]
                contours = graphics.contour
                if name not in contours.get_object_names():
                    contours.create(name=name)
                c = contours[name]
                if field not in c.field.allowed_values():
                    raise RuntimeError(f'Unavailable native field: {field}')
                c.set_state({'field': field, 'surfaces_list': surfaces,
                             'range_options': {'global_range': False, 'auto_range': False,
                                               'clip_to_range': False, 'minimum': limits[0], 'maximum': limits[1]},
                             'options': {'filled': True, 'node_values': True,
                                         'boundary_values': False, 'contour_lines': False}})
                c.display()
                camera = graphics.views.camera
                camera.projection(type='orthographic')
                camera.target(xyz=[0, 3.495, 0])
                camera.position(xyz=[0, 3.495, 10])
                camera.up_vector(xyz=[0, 1, 0])
                graphics.views.auto_scale()
                camera.target(xyz=[0, 3.495, 0])
                camera.position(xyz=[0, 3.495, 10])
                camera.field(width=10.67, height=8.0)
                camera.zoom(factor=1.0)
                graphics.picture.use_window_resolution = False
                graphics.picture.landscape = True
                graphics.picture.x_resolution = 2400
                graphics.picture.y_resolution = 1800
                filename = f'native-{"preview-" if preview else ""}{label}-N{n}-{field}.png'
                path = str(remote / filename)
                if remote_file_exists(s, path):
                    raise FileExistsError(path)
                graphics.picture.save_picture(file_name=path)
                encoded = path + '.base64.txt'
                powershell(s, f"[IO.File]::WriteAllText('{encoded}',[Convert]::ToBase64String([IO.File]::ReadAllBytes('{path}')))")
                payload = base64.b64decode(read_text(s, encoded), validate=True)
                if not payload.startswith(b'\x89PNG\r\n\x1a\n'):
                    raise RuntimeError('Native PNG transfer failed')
                (FIG / filename).write_bytes(payload)
                sample_label = 'bulk' if label == 'bulk-dry' else label
                sample_surface = 'wall' if field == 'film-thickness' else 'p72s3-xy-z0'
                sample_path = OUT / f'{sample_label}-{sample_surface}.npz'
                samples = np.load(sample_path)[field]
                record['figures'].append({'filename': filename, 'local': str(FIG / filename),
                                          'remote': path, 'sha256': hashlib.sha256(payload).hexdigest(),
                                          'source': label, 'native_iteration': n, 'field': field,
                                          'range': limits, 'surfaces': surfaces,
                                          'observed_native_facet_range': [float(samples.min()), float(samples.max())],
                                          'range_discovery': 'Preserved native face-field samples on exact checkpoint surface; contours use nodal interpolation',
                                          'contour_readback': c.get_state(), 'plane_readback': planes[plane].get_state(),
                                          'camera': {'position': [0, 3.495, 10], 'target': [0, 3.495, 0],
                                                     'up': [0, 1, 0], 'projection': 'orthographic',
                                                     'post_auto_scale_zoom': 1.0,
                                                     'explicit_field_width': 10.67, 'explicit_field_height': 8.0},
                                          'picture_readback': graphics.picture.get_state(),
                                          'resolution': [2400, 1800], 'visual_qa': 'PENDING'})
                manifest_path.write_text(json.dumps(record, indent=2) + '\n')
                print('NATIVE_FIGURE_EXPORTED', filename, flush=True)
        record['status'] = 'EXPORTED_VISUAL_QA_REQUIRED'
    finally:
        s.settings.file.read_case(file_name=final['pair']['case'])
        s.settings.file.read_data(file_name=final['pair']['data'])
        require_match(state(s)['readback'], final['state']['readback'])
        record['restored_adaptive_endpoint'] = True
        manifest_path.write_text(json.dumps(record, indent=2) + '\n')
        print('RESTORED_ADAPTIVE_N6000', flush=True)


if __name__ == '__main__':
    main()
