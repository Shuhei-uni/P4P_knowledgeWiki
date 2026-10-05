"""Reconstruct the verified Phase 7.2A model on the explicitly owned Server 3.

Attach only; unique local Windows artifacts; no process launch or termination.
The prepare operation is separate from the long solve and refuses a loaded case.
"""
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import argparse
import base64
import json
import math
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_chdir, quote_scheme_string, remote_file_exists
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256
from run_phase72a_e27_server1_continuation import pair_save, dump, native_iteration
from run_phase72a_local_film_replay import readback, require_match
from run_phase72a_r3_ewf_absorber_direct import validate_roughness
from pyansys_fluent.common import parse_parallel_connectivity_roster

OUT = ROOT / 'output/phase72a-stage3-server3/20261005'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage3\20261005')
SOURCE = PureWindowsPath(r'C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\ContactAbsorber\local20000\20261004T081120Z')
HASHES = {'block-N33586.cas.h5': '1dedd5e01fca7b694c7af4c9da23f823c328931b6ee64a7aa717a63b25e0fe11',
          'block-N33586.dat.h5': '5810d6049a6862d04e2c55791eee75de9a471d349ab73052366ca69f3c87c25e',
          'contact-libraries.zip': '446428fb0d41e98efb55454f30dff656c935d044cfb6229669c9dab05507be3e'}


def powershell(s, code):
    encoded = base64.b64encode(code.encode('utf-16le')).decode('ascii')
    command = f'cmd /c powershell -NoProfile -EncodedCommand {encoded}'
    return s.scheme.eval(f'(system "{quote_scheme_string(command)}")')


def save(s, name):
    return pair_save(s, WORK / f'{name}.cas.h5', WORK / 'scratch', scratch_tag=name)


def state(s):
    return {'readback': readback(s), 'setup': s.settings.setup.get_state(),
            'methods': s.settings.solution.methods.get_state(),
            'film_model': dict(s.rp_vars('wall-film/model-parameters'))}


def loading(s, multiplier):
    bc = s.settings.setup.boundary_conditions.mass_flow_inlet
    for zone, phase, target in [('liquidinlet', 'phase-2', 116.92), ('steaminlet', 'phase-1', 80.69)]:
        momentum = bc[zone].phase[phase].momentum
        momentum.mass_flow_rate = target * multiplier
        value = momentum.mass_flow_rate.get_state()['value']
        if not math.isclose(value, target * multiplier, rel_tol=1e-10):
            raise RuntimeError('Inlet loading readback failed')
    return {'multiplier': multiplier, 'liquid_kg_s': 116.92 * multiplier, 'vapor_kg_s': 80.69 * multiplier}


def instrument(s, folder):
    ensure_remote_directory(s, str(folder))
    paths = {}
    for name in s.settings.solution.monitor.report_files.get_object_names():
        obj = s.settings.solution.monitor.report_files[name]
        defs = obj.report_defs()
        if len(defs) != 1:
            raise RuntimeError(f'Multiple definitions in report file {name}')
        path = str(folder / f'{defs[0]}.out')
        if remote_file_exists(s, path):
            raise FileExistsError(path)
        obj.file_name = path
        obj.frequency_of = 'iteration'
        obj.frequency = 1
        obj.active = True
        paths[defs[0]] = path
    return paths


def add_pressure_reports(s):
    definitions = s.settings.solution.report_definitions.surface
    files = s.settings.solution.monitor.report_files
    for name, surfaces in [('p72s3-pressure-inlet', ['liquidinlet', 'steaminlet']),
                           ('p72s3-pressure-outlet', ['steamoutlet'])]:
        if name not in definitions.get_object_names():
            definitions.create(name=name)
        definitions[name].set_state({'report_type': 'surface-areaavg', 'field': 'pressure', 'surface_names': surfaces})
        if name not in files.get_object_names():
            files.create(name=name)
        files[name].report_defs = [name]
    return definitions.get_state()


def spatial(s, label):
    import numpy as np
    from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest, ScalarFieldDataRequest, SurfaceDataType
    plane = 'p72s3-xy-z0'
    planes = s.settings.results.surfaces.plane_surface
    if plane not in planes.get_object_names():
        planes.create(name=plane)
    planes[plane].set_state({'method': 'xy-plane', 'z': 0.0})
    walls = ['wall', 'separator-purnanto:1']
    names = [plane] + walls
    geometry = s.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=names, data_types=[SurfaceDataType.Vertices, SurfaceDataType.FacesConnectivity, SurfaceDataType.FacesCentroid]))
    for name in names:
        g = geometry[name]
        payload = {'vertices': np.asarray(g.vertices), 'centroids': np.asarray(g.face_centroids),
                   'face_sizes': np.array([len(f) for f in g.connectivity]), 'connectivity': np.concatenate(g.connectivity)}
        for field in (['phase-2-vof', 'velocity-magnitude', 'pressure'] if name == plane else ['film-thickness']):
            data = s.fields.field_data.get_field_data(ScalarFieldDataRequest(field_name=field, surfaces=[name], node_value=False, boundary_value=False))
            values = np.asarray(data[name])
            if len(values) != len(payload['centroids']) or not np.isfinite(values).all():
                raise RuntimeError(f'Invalid spatial field {field} on {name}')
            payload[field] = values
        np.savez_compressed(OUT / f'{label}-{name}.npz', **payload)


def diagnostics(s):
    manifest = json.loads((OUT / 'run-manifest.json').read_text())
    recovery = manifest['status'] == 'RECOVERY_REQUIRED' and ('ModuleNotFoundError' in manifest.get('error', '') or 'capture_parallel_connectivity_roster' in manifest.get('error', ''))
    if (manifest['status'] != 'PREPARED_VERIFIED' and not recovery) or manifest['blocks']:
        raise RuntimeError('Diagnostics require an unrun, verified startup')
    expected = json.loads((OUT / 'prepared-state.json').read_text())
    if not recovery and state(s) != expected:
        raise RuntimeError('Startup has changed before diagnostics')
    s.settings.file.read_case(file_name=manifest['reference_pair']['case'])
    s.settings.file.read_data(file_name=manifest['reference_pair']['data'])
    add_pressure_reports(s)
    names = ['p72s3-pressure-inlet', 'p72s3-pressure-outlet', 'p72a-e2.7-ewf-thickness-awavg',
             'p72a-e2.7-ewf-secondary-phase-mass-total']
    values = {}
    for record in s.settings.solution.report_definitions.compute(report_defs=names):
        values.update(record)
    dump(OUT / 'reference-extra-reports.json', values)
    spatial(s, 'reference')
    s.transcript.start(file_name=str(OUT / 'parallel-connectivity.txt'), write_to_stdout=False)
    s.settings.parallel.show_connectivity(compute_node=0)
    time.sleep(1)
    s.transcript.stop()
    manifest['parallel_roster'] = parse_parallel_connectivity_roster((OUT / 'parallel-connectivity.txt').read_text())
    s.settings.file.read_case(file_name=manifest['prepared_pair']['case'])
    s.settings.file.read_data(file_name=manifest['prepared_pair']['data'])
    require_match(readback(s), expected['readback'])
    add_pressure_reports(s)
    manifest['report_paths'] = instrument(s, WORK / 'monitors' / 'bulk-instrumented')
    manifest['prepared_pair_before_diagnostics'] = manifest['prepared_pair']
    manifest['prepared_pair'] = save(s, 'startup-instrumented')
    before = state(s)
    s.settings.file.read_case(file_name=manifest['prepared_pair']['case'])
    s.settings.file.read_data(file_name=manifest['prepared_pair']['data'])
    require_match(readback(s), before['readback'])
    dump(OUT / 'prepared-state.json', state(s))
    # Reopen refreshes the initialization-time cached iteration expression.
    manifest['native_start'] = native_iteration(s)
    manifest['verified_native_end'] = manifest['native_start']
    manifest['required_diagnostics'] = 'PRESSURE_SOURCE_FILM_AND_MATCHED_SPATIAL'
    manifest['status'] = 'PREPARED_VERIFIED'
    manifest.pop('error', None)
    dump(OUT / 'run-manifest.json', manifest)
    print('REQUIRED_DIAGNOSTICS_VERIFIED', flush=True)


def smoke(s):
    manifest = json.loads((OUT / 'run-manifest.json').read_text())
    if manifest['status'] != 'PREPARED_VERIFIED' or manifest['blocks'] or manifest.get('smoke'):
        raise RuntimeError('Smoke requires a verified unrun startup')
    expected = json.loads((OUT / 'prepared-state.json').read_text())
    if state(s) != expected:
        raise RuntimeError('Live setup differs before smoke')
    start = native_iteration(s)
    manifest['native_start'] = start
    s.transcript.start(file_name=str(OUT / 'startup-smoke.txt'), write_to_stdout=False)
    t = time.monotonic()
    s.tui.solve.iterate(20)
    s.transcript.stop()
    end = native_iteration(s)
    if end != start + 20:
        raise RuntimeError('Smoke did not reach 20 updates')
    current = state(s)
    if not all(math.isfinite(v[0]) for v in current['readback']['fields'].values()):
        raise RuntimeError('Nonfinite smoke reports')
    if current['film_model']['solve-wallfilm?'] or current['readback']['fields']['p72a-e2.7-ewf-film-mass-total'][0] != 0:
        raise RuntimeError('Film equations or inventory changed during bulk startup')
    histories = collect(s, manifest['report_paths'], 'smoke')
    if any(not set(range(start + 1, end + 1)).issubset(h['iterations']) for h in histories.values()):
        raise RuntimeError('Required smoke report history missing')
    pair = save(s, f'startup-smoke-N{end}')
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(readback(s), current['readback'])
    dump(OUT / 'prepared-state.json', state(s))
    manifest.update(verified_native_end=end, smoke={'updates': 20, 'wall_seconds': time.monotonic() - t, 'pair': pair, 'reopen': 'PASS'},
                    status='PREPARED_VERIFIED')
    dump(OUT / 'run-manifest.json', manifest)
    print('SMOKE_VERIFIED', end, manifest['smoke']['wall_seconds'], flush=True)


def prepare(s, recover=False):
    previous_path = OUT / 'run-manifest.json'
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else None
    if recover and (not previous or previous['status'] != 'RECOVERY_REQUIRED' or previous.get('blocks')):
        raise RuntimeError('Recovery is allowed only for this failed, unrun preparation')
    if s.settings.setup.boundary_conditions.is_active() and not recover:
        raise RuntimeError('Server 3 now has a loaded case; reconcile and preserve it before preparation')
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors']:
        ensure_remote_directory(s, str(folder))
    manifest = {'status': 'PREFLIGHT', 'authority': 'human_2026_10_05_full_server3_ownership_stage3',
                'server_id': '3', 'host': s.scheme.eval('(getenv "COMPUTERNAME")'),
                'version': str(s.get_fluent_version()), 'source': str(SOURCE),
                'reference_native_iteration': 33586, 'work_root': str(WORK), 'blocks': []}
    dump(OUT / 'run-manifest.json', manifest)
    for filename, expected in HASHES.items():
        tag = datetime.now(timezone.utc).strftime('%H%M%S%f')
        actual = remote_file_sha256(s, str(SOURCE / filename), str(WORK / 'scratch' / f'source-{tag}-{filename}.sha256.txt'))
        if actual != expected:
            raise RuntimeError(f'Source hash mismatch: {filename}')
        destination = WORK / filename
        if remote_file_exists(s, str(destination)) and not recover:
            raise FileExistsError(str(destination))
        if not remote_file_exists(s, str(destination)):
            powershell(s, f"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath '{SOURCE / filename}' -Destination '{destination}'")
        if remote_file_sha256(s, str(destination), str(WORK / 'scratch' / f'copy-{tag}-{filename}.sha256.txt')) != expected:
            raise RuntimeError(f'Destination hash mismatch: {filename}')
    if not remote_file_exists(s, str(WORK / 'libcontactv2' / 'win64' / '3ddp_host' / 'libudf.dll')):
        powershell(s, f"$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath '{WORK / 'contact-libraries.zip'}' -DestinationPath '{WORK}'")
    remote_chdir(s, str(WORK))
    s.transcript.start(file_name=str(OUT / ('reference-load-recovery.txt' if recover else 'reference-load.txt')), write_to_stdout=False)
    s.settings.file.read_case(file_name=str(WORK / 'block-N33586.cas.h5'))
    # The case carries obsolete source-machine library paths. Load the verified
    # archive from this run's working directory and retain the exact hook names.
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    s.settings.file.read_data(file_name=str(WORK / 'block-N33586.dat.h5'))
    s.transcript.stop()
    if native_iteration(s) != 33586:
        raise RuntimeError('Reference iteration differs')
    ref = state(s)
    expected = json.loads((ROOT / 'output/phase72a-adaptive-server1/20261005/loaded-parent.json').read_text())
    # Native mass-flow reports contain a separately evaluated user-source term.
    # The source-machine receipt had zero cached source values after loading.
    # Boundary-only fluxes and inventories must match; verify the now evaluated
    # source against the independent depletion expression, not that stale cache.
    source_dependent = {'v2-flux-phase2-liquidinlet', 'v2-flux-phase2-liquidinlet(User Mass Source)',
                        'v2-flux-phase2-steamoutlet', 'v2-flux-phase2-steamoutlet(User Mass Source)',
                        'v2-applied-absorber'}
    actual_clean = {**ref['readback'], 'fields': {k: v for k, v in ref['readback']['fields'].items() if k not in source_dependent}}
    expected_clean = {**expected, 'fields': {k: v for k, v in expected['fields'].items() if k not in source_dependent}}
    require_match(actual_clean, expected_clean)
    fields = ref['readback']['fields']
    if not math.isclose(-fields['v2-applied-absorber'][0], fields['p72-contact-removal'][0], rel_tol=1e-9):
        raise RuntimeError('Evaluated UDF source differs from independent depletion expression')
    dump(OUT / 'source-cache-reconciliation.json', {
        'source_receipt': expected['fields'], 'server3_evaluated': fields,
        'note': 'Frozen settings, inventories and boundary-only fluxes match; source-dependent cached reports differ. Native UDF source matches independent depletion expression.',
        'reference_applied_source_kg_s': fields['v2-applied-absorber'][0]})
    validate_roughness(s)
    dump(OUT / 'reference-state.json', ref)
    if previous and previous.get('reference_pair'):
        manifest['reference_pair'] = previous['reference_pair']
    else:
        manifest['reference_pair'] = save(s, 'reference-N33586')
    manifest['reference_verification'] = 'MATCH_INVENTORIES_BOUNDARY_FLUXES_AND_SETTINGS_SOURCE_CACHE_RECONCILED'
    dump(OUT / 'run-manifest.json', manifest)
    print('REFERENCE_PRESERVED', flush=True)
    # Keep the native EWF model and wall assignments. Only its solve switch is
    # off during carrier development; reset film and carrier fields for startup.
    s.tui.define.models.eulerian_wallfilm.solve_wallfilm_equation('no')
    manifest['initial_loading'] = loading(s, .25)
    s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
    s.settings.solution.initialization.hybrid_initialize()
    manifest['native_start'] = native_iteration(s)
    manifest['report_paths'] = instrument(s, WORK / 'monitors' / 'bulk')
    manifest['prepared_pair'] = save(s, 'startup-prepared')
    before = state(s)
    s.settings.file.read_case(file_name=manifest['prepared_pair']['case'])
    s.settings.file.read_data(file_name=manifest['prepared_pair']['data'])
    after = state(s)
    require_match(after['readback'], before['readback'])
    if after['setup'] != before['setup'] or after['methods'] != before['methods']:
        raise RuntimeError('Prepared startup setup differs after reopen')
    dump(OUT / 'prepared-state.json', after)
    manifest.update(status='PREPARED_VERIFIED', verified_native_end=native_iteration(s),
                    preparation_reopen='PASS', solver_left_open=True)
    dump(OUT / 'run-manifest.json', manifest)
    print('STARTUP_PREPARED', manifest['native_start'], flush=True)


def collect(s, paths, label):
    histories = {}
    for name, path in paths.items():
        text = read_text(s, path)
        (OUT / f'{label}-{name}.out').write_text(text)
        values = {}
        for line in text.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit():
                values[int(parts[0])] = float(parts[1])
        histories[name] = {'iterations': sorted(values), 'values': [values[i] for i in sorted(values)], 'file': path}
    dump(OUT / f'{label}-histories.json', histories)
    return histories


def iterate(s, steps):
    """Submit a known absolute native command without dynamic menu discovery."""
    if not isinstance(steps, int) or steps <= 0:
        raise ValueError('Positive native solve count required')
    run_control = s.settings.solution.run_calculation
    expected = native_iteration(s) + steps
    if not run_control.iterate.is_active():
        raise RuntimeError('Native solve remains active before a new batch; reconcile its endpoint')
    result = s.scheme.eval(f'(ti-menu-load-string "/solve/iterate {steps}")')
    if native_iteration(s) != expected:
        raise RuntimeError('Native command did not reach its requested endpoint; do not resubmit')
    # This endpoint retains a solve-active UI flag after a completed native
    # command. Clear it only after the exact requested horizon is proved.
    if not run_control.iterate.is_active() and run_control.interrupt.is_active():
        run_control.interrupt()
        if native_iteration(s) != expected or not run_control.iterate.is_active():
            raise RuntimeError('Could not restore idle native run control at the completed endpoint')
        print('NATIVE_IDLE_BARRIER', expected, flush=True)
    return result


def run(s, resume=False):
    manifest = json.loads((OUT / 'run-manifest.json').read_text())
    allowed_status = 'RECOVERY_REQUIRED' if resume else 'PREPARED_VERIFIED'
    if manifest['status'] != allowed_status or native_iteration(s) != manifest['verified_native_end']:
        raise RuntimeError('Reconcile prior execution before run')
    before = state(s)
    expected = json.loads((OUT / 'prepared-state.json').read_text())
    if resume:
        if not any(cause in manifest.get('error', '') for cause in ['menu not found', 'Bulk solve returned before declared horizon']) or any('arm' in b for b in manifest['blocks']):
            raise RuntimeError('This recovery path is only for a reconciled bulk menu-lookup failure')
        last = manifest['blocks'][-1]
        if last['native_end'] != manifest['verified_native_end'] or not last.get('pair'):
            raise RuntimeError('Resume requires the verified paired bulk checkpoint')
        # Compare fixed settings, not the evolved carrier solution fields.
        if any(before['readback'][k] != v for k, v in expected['readback'].items() if k != 'fields') or before['methods'] != expected['methods']:
            raise RuntimeError('Bulk model settings changed before recovery')
        loading(s, last['feed']['multiplier'])
        tag = datetime.now(timezone.utc).strftime('%H%M%S%f')
        dump(OUT / f"recovery-N{last['native_end']}-{tag}.json", {'previous_manifest': manifest, 'live_state': before,
              'recovery': 'Resume same live fields with absolute native solve command; no initialization'})
        for kind in ['case', 'data']:
            tag = datetime.now(timezone.utc).strftime('%H%M%S%f')
            observed = remote_file_sha256(s, last['pair'][kind], str(WORK / 'scratch' / f'recovery-{tag}-{kind}.sha256.txt'))
            if observed != last['pair'][kind + '_sha256']:
                raise RuntimeError('N1000 recovery checkpoint hash differs')
        manifest.pop('error', None)
        manifest['recovery_transport'] = 'ABSOLUTE_NATIVE_TI_MENU_LOAD_STRING_WITH_EXACT_HORIZON_IDLE_BARRIER'
        print('RESUME_VERIFIED', last['native_end'], flush=True)
    elif before != expected:
        raise RuntimeError('Live startup differs from saved preparation')
    start = manifest['native_start']
    schedule = [(1000, .25), (1500, .25)]
    schedule += [(1500 + 100 * k, .25 + .075 * k) for k in range(1, 11)]
    schedule += [(3000, 1.0)]
    clock = time.monotonic()
    transcript_name = f"bulk-resume-N{manifest['verified_native_end']}-{datetime.now(timezone.utc).strftime('%H%M%S')}.txt" if resume else 'bulk-transcript.txt'
    s.transcript.start(file_name=str(OUT / transcript_name), write_to_stdout=False)
    previous_bulk_seconds = sum(b['wall_seconds'] for b in manifest['blocks'] if 'startup_end' in b) if resume else 0
    for end, multiplier in schedule:
        if start + end <= manifest['verified_native_end']:
            continue
        feed = loading(s, multiplier)
        n = native_iteration(s)
        steps = start + end - n
        manifest.update(status='RUNNING_BULK', command=f'/solve/iterate {steps}', active_target=start + end)
        dump(OUT / 'run-manifest.json', manifest)
        print('SUBMIT_BULK', n, steps, feed, flush=True)
        t = time.monotonic()
        iterate(s, steps)
        if native_iteration(s) != start + end:
            raise RuntimeError('Bulk solve returned before declared horizon')
        record = {'startup_end': end, 'native_end': native_iteration(s), 'feed': feed, 'wall_seconds': time.monotonic() - t}
        if end % 1000 == 0:
            record['pair'] = save(s, f'bulk-N{native_iteration(s)}')
        manifest['blocks'].append(record)
        manifest['verified_native_end'] = native_iteration(s)
        dump(OUT / 'run-manifest.json', manifest)
        print('BULK_BLOCK_COMPLETE', end, record['wall_seconds'], flush=True)
    s.transcript.stop()
    collect(s, manifest['report_paths'], 'bulk')
    dump(OUT / 'bulk-endpoint.json', state(s))
    spatial(s, 'bulk')
    manifest['bulk_wall_seconds'] = previous_bulk_seconds + time.monotonic() - clock
    # Preserve the same dry carrier state for both timestep contrasts.
    s.tui.define.models.eulerian_wallfilm.solve_wallfilm_equation('yes')
    s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
    params = s.rp_vars('wall-film/model-parameters')
    s.rp_vars('wall-film/model-parameters', [(k, False if k == 'ewf-adaptive?' else 1e-6 if k == 'timestep-max' else v) for k, v in params])
    manifest['film_start_state'] = state(s)
    manifest['film_start_pair'] = save(s, 'film-start-dry')
    for arm in ['fixed', 'adaptive']:
        if arm == 'adaptive':
            s.settings.file.read_case(file_name=manifest['film_start_pair']['case'])
            s.settings.file.read_data(file_name=manifest['film_start_pair']['data'])
            require_match(readback(s), manifest['film_start_state']['readback'])
            params = s.rp_vars('wall-film/model-parameters')
            changes = {'ewf-adaptive?': True, 'adapt-init-dt': 1e-6, 'adapt-tstp-inc': 1.2, 'adapt-tstp-dec': 2.0, 'courant-number': .1}
            if not set(changes).issubset(dict(params)):
                raise RuntimeError('Native adaptive controls missing')
            s.rp_vars('wall-film/model-parameters', [(k, changes.get(k, v)) for k, v in params])
        paths = instrument(s, WORK / 'monitors' / arm)
        arm_start = native_iteration(s)
        s.transcript.start(file_name=str(OUT / f'{arm}-film-transcript.txt'), write_to_stdout=False)
        for block in range(1, 4):
            manifest.update(status=f'RUNNING_FILM_{arm.upper()}', command='/solve/iterate 1000', active_target=arm_start + 1000 * block)
            dump(OUT / 'run-manifest.json', manifest)
            print('SUBMIT_FILM', arm, block, flush=True)
            t = time.monotonic()
            iterate(s, 1000)
            if native_iteration(s) != arm_start + 1000 * block:
                raise RuntimeError('Film solve returned before declared horizon')
            current = state(s)
            pair = save(s, f'{arm}-film-N{native_iteration(s)}')
            record = {'arm': arm, 'block': block, 'native_end': native_iteration(s), 'wall_seconds': time.monotonic() - t, 'pair': pair, 'state': current}
            dump(OUT / f'{arm}-endpoint-N{native_iteration(s)}.json', record)
            manifest['blocks'].append({k: v for k, v in record.items() if k != 'state'})
            manifest['latest_pair'] = pair
            dump(OUT / 'run-manifest.json', manifest)
            # These are declared recovery limits, not reproduction tolerances.
            fields = current['readback']['fields']
            if not all(math.isfinite(v[0]) for v in fields.values()) or fields['p72a-e2.7-ewf-thickness-max'][0] > .003:
                raise RuntimeError('Film instability recovery limit exceeded; endpoint preserved')
            print('FILM_BLOCK_COMPLETE', arm, block, fields['p72a-e2.7-ewf-film-mass-total'], flush=True)
        s.transcript.stop()
        collect(s, paths, arm)
        spatial(s, arm)
        s.settings.file.read_case(file_name=pair['case'])
        s.settings.file.read_data(file_name=pair['data'])
        require_match(readback(s), current['readback'])
        dump(OUT / f'{arm}-final-reopen.json', state(s))
    manifest.update(status='STARTUP_SCREENS_COMPLETE_ANALYSIS_REQUIRED', wall_seconds=time.monotonic() - clock,
                    final_reopen='PASS', solver_left_open=True)
    dump(OUT / 'run-manifest.json', manifest)
    print('STAGE3_SCREENS_COMPLETE', flush=True)


def resume_film(s):
    """Continue the user-paused adaptive arm without resetting its fields/history."""
    manifest = json.loads((OUT / 'run-manifest.json').read_text())
    receipt = json.loads((OUT / 'user-stop-receipt.json').read_text())
    n = native_iteration(s)
    if manifest['status'] != 'PAUSED_BY_USER' or n != receipt['native_iteration']:
        raise RuntimeError('Resume requires the exact preserved user-stop endpoint')
    expected = json.loads((OUT / 'adaptive-endpoint-N4000.json').read_text())['state']
    current = state(s)
    if current['methods'] != expected['methods'] or any(
            current['readback'][key] != value for key, value in expected['readback'].items() if key != 'fields'):
        raise RuntimeError('Adaptive model settings changed while paused')
    if not current['film_model']['ewf-adaptive?'] or not 4000 <= n < 6000:
        raise RuntimeError('This continuation requires the existing adaptive startup arm')
    stamp = datetime.now(timezone.utc).strftime('%H%M%S%f')
    for kind in ['case', 'data']:
        digest = remote_file_sha256(s, receipt['pair'][kind],
                                   str(WORK / 'scratch' / f'user-resume-{stamp}-{kind}.sha256.txt'))
        if digest != receipt['pair'][kind + '_sha256']:
            raise RuntimeError('User-stop checkpoint hash differs')
    paths = {}
    for name in s.settings.solution.monitor.report_files.get_object_names():
        obj = s.settings.solution.monitor.report_files[name]
        definitions = obj.report_defs()
        path = obj.file_name()
        if len(definitions) != 1 or not remote_file_exists(s, path) or not obj.active():
            raise RuntimeError('Existing adaptive history instrumentation is incomplete')
        paths[definitions[0]] = path
    transcript = f'adaptive-film-resume-N{n}-{stamp}.txt'
    dump(OUT / f'user-resume-N{n}-{stamp}.json', {
        'native_start': n, 'live_state': current, 'parent_pair': receipt['pair'],
        'controlled_delta': 'Remaining updates only; no initialization or timestep change',
        'transcript': transcript, 'report_paths': paths})
    manifest.setdefault('adaptive_transcript_segments', ['adaptive-film-transcript.txt']).append(transcript)
    manifest['user_resume_native_start'] = n
    manifest['user_resume_authority'] = 'human_2026_10_05_nevermind_continue'
    s.transcript.start(file_name=str(OUT / transcript), write_to_stdout=False)
    print('USER_RESUME_VERIFIED', n, 'remaining', 6000 - n, flush=True)
    clock = time.monotonic()
    for target in [5000, 6000]:
        begin = native_iteration(s)
        if begin >= target:
            continue
        steps = target - begin
        manifest.update(status='RUNNING_FILM_ADAPTIVE', active_target=target,
                        command=f'/solve/iterate {steps}')
        dump(OUT / 'run-manifest.json', manifest)
        print('SUBMIT_FILM_RESUME', begin, steps, flush=True)
        t = time.monotonic()
        iterate(s, steps)
        current = state(s)
        pair = save(s, f'adaptive-film-N{target}')
        record = {'arm': 'adaptive', 'block': (target - 3000) // 1000,
                  'native_start': begin, 'native_end': target, 'updates_this_submission': steps,
                  'wall_seconds': time.monotonic() - t, 'pair': pair, 'state': current,
                  'cost_basis': 'This resumed submission plus endpoint readback/checkpoint only'}
        dump(OUT / f'adaptive-endpoint-N{target}.json', record)
        manifest['blocks'].append({key: value for key, value in record.items() if key != 'state'})
        manifest.update(latest_pair=pair, verified_native_end=target,
                        last_verified_native_iteration=target)
        dump(OUT / 'run-manifest.json', manifest)
        fields = current['readback']['fields']
        if not all(math.isfinite(value[0]) for value in fields.values()) or fields['p72a-e2.7-ewf-thickness-max'][0] > .003:
            raise RuntimeError('Film recovery limit exceeded; checkpoint preserved')
        print('FILM_BLOCK_COMPLETE', 'adaptive', target, fields['p72a-e2.7-ewf-film-mass-total'], flush=True)
    s.transcript.stop()
    collect(s, paths, 'adaptive')
    spatial(s, 'adaptive')
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(readback(s), current['readback'])
    dump(OUT / 'adaptive-final-reopen.json', state(s))
    manifest.update(status='STARTUP_SCREENS_COMPLETE_ANALYSIS_REQUIRED', final_reopen='PASS',
                    resumed_wall_seconds=time.monotonic() - clock, solver_left_open=True)
    dump(OUT / 'run-manifest.json', manifest)
    print('STAGE3_SCREENS_COMPLETE', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'diagnostics', 'smoke', 'run', 'resume-bulk', 'resume-film'])
    parser.add_argument('--recover-preparation', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.operation == 'prepare' and (OUT / 'run-manifest.json').exists() and not args.recover_preparation:
        raise RuntimeError('Existing preparation: reconcile before repeat')
    # Fluent 2025 R2 exposes the v0 services (verified on this endpoint).
    # This PyFluent build's unauthenticated reflection can wait indefinitely,
    # although authenticated reflection and the actual v0 RPCs respond.
    # Pin only this worker's transport; never edit the installed package.
    import ansys.fluent.core._grpc_services as services
    import ansys.fluent.core.services as high_level_services
    from ansys.fluent.core.utils.fluent_version import FluentVersion
    import functools
    services._server_supports_v1 = lambda channel: False
    # The version-discovery StringEval RPC can also stall after interrupt.
    # Select the already verified 252 service factory; check the actual product
    # version through ApplicationRuntime immediately after attachment.
    high_level_services.create_service_factory = functools.partial(
        high_level_services.create_service_factory, product_version=FluentVersion.v252)
    s = connect('3', start_transcript=False, tcp_timeout_seconds=5)
    if '2025 R2' not in str(s.get_fluent_version()):
        raise RuntimeError('The pinned v0 worker requires the verified Fluent 2025 R2 endpoint')
    try:
        if args.operation == 'prepare':
            prepare(s, recover=args.recover_preparation)
        elif args.operation == 'diagnostics':
            diagnostics(s)
        elif args.operation == 'smoke':
            smoke(s)
        elif args.operation == 'resume-film':
            resume_film(s)
        else:
            run(s, resume=args.operation == 'resume-bulk')
    except Exception:
        p = OUT / 'run-manifest.json'
        manifest = json.loads(p.read_text()) if p.exists() else {}
        manifest.update(status='RECOVERY_REQUIRED', error=traceback.format_exc(), solver_left_open=True)
        dump(p, manifest)
        raise


if __name__ == '__main__':
    main()
