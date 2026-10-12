"""Phase 10 operations on the human-selected persistent direct Fluent solver.

No launch, exit or remote session access. Every stage preserves native evidence.
"""
from pathlib import Path
import copy
import hashlib
import json
import math
import shutil
import time
import traceback

import run_phase72a_local_film_replay as replay
import run_phase72a_stage3_server3 as base
from run_p7_e5_cz import create_lower_register
from run_phase72a_e27_server1_continuation import native_iteration
from pyansys_fluent.execution_contract import native_transcript
from run_phase72a_adaptive_film import history, FILM

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / 'PyAnsys/output/phase10-proposed-design/20261011'
WORK = Path(r'C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse\Phase10-ProposedDesign-213k-20261011')
SHARED = Path(r'C:\Users\Shuhei Yokkaichi\OneDrive\OneDrive - The University of Auckland')
MESH = SHARED / '2026 Sem 1/700/P4PCFD/CAD PurnantoV2/Design improvement/Separator-angle-slit-213k.msh.h5'
PARENT = SHARED / 'P4P-Fluent-Artifacts/Phase72A/Stage3/early-ewf-startup/prepared-A-N1580/prepared-A-N1580'
HASHES = {'cas.h5': '5907e357654ebe5437c64f4e6abea19cbbc66b1edd2312f6b2eb63fe408c2b72',
          'dat.h5': '72a7134f6358ea68615907f336e71d6e518c713418674477703fc638e41816af'}


def dump(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / name
    temporary = destination.with_suffix(destination.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, default=str) + '\n')
    temporary.replace(destination)
    if name == 'run-manifest.json':
        import yaml
        path = REPO / 'Project/experiments/phase-10-proposed-design/phase-state.yaml'
        state = yaml.safe_load(path.read_text())
        state['status'] = value['status']
        state['observed_film_age_s'] = value.get('observed_film_age_s')
        state['observed_native_iteration'] = value.get('native_end')
        state['active_target'] = value.get('active_target')
        state['frozen_bulk_drain_proof'] = value.get('frozen_bulk_drain_proof', 'PENDING')
        state['final_pair_verified'] = value['status'] == 'COMPLETE_100MS_ENDPOINT_REOPEN_VERIFIED'
        path.write_text(yaml.safe_dump(state, sort_keys=False))


def save(s, name):
    path = WORK / (name + '.cas.h5')
    s.settings.file.write_case_data(file_name=str(path))
    pair = {'case': str(path), 'data': str(WORK / (name + '.dat.h5'))}
    for kind in ['case', 'data']:
        file = Path(pair[kind])
        if not file.is_file() or file.stat().st_size == 0:
            raise RuntimeError('Missing paired artifact: ' + str(file))
        with file.open('rb') as stream:
            pair[kind + '_sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
    dump(name + '-pair.json', pair)
    return pair


def prepare_parent(s):
    if not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Direct session is busy')
    WORK.mkdir(exist_ok=False)
    before = base.state(s)
    dump('previous-session.json', {'state': before, 'clock': dict(s.rp_vars('wall-film/solution-state'))})
    save(s, 'preserved-previous-session')
    for ext, expected in HASHES.items():
        source = Path(str(PARENT) + '.' + ext)
        with source.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != expected:
                raise RuntimeError('Parent hash differs')
        shutil.copy2(source, WORK / ('parent-A-N1580.' + ext))
    s.settings.file.read_case(file_name=str(WORK / 'parent-A-N1580.cas.h5'))
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    s.settings.file.read_data(file_name=str(WORK / 'parent-A-N1580.dat.h5'))
    source = base.state(s)
    source['reports'] = s.settings.solution.report_definitions.get_state()
    source['clock'] = dict(s.rp_vars('wall-film/solution-state'))
    if not all(s.settings.solution.controls.equations.get_state().values()):
        raise RuntimeError('Parent bulk equations are not active')
    if source['clock']['film_elapsed_time'] != 0:
        raise RuntimeError('Parent film clock is not dry A')
    if not math.isclose(source['readback']['fields']['v2-total-liquid-mass'][0], 31.35713621088837, rel_tol=1e-9):
        raise RuntimeError('Parent bulk inventory differs')
    dump('source-state.json', source)
    names = s.settings.setup.models.discrete_phase.injections.get_object_names()
    s.tui.file.write_injections('"' + (WORK / 'source-A.inj').as_posix() + '"', *names, '()')
    dump('run-manifest.json', {'status': 'SOURCE_VERIFIED', 'target_total_film_age_s': .100,
         'work': str(WORK), 'parent_hashes': HASHES, 'session': 'direct-local-252',
         'review': 'Pinned local session; prior pair preserved; hash-verified dry A; no launch/exit in this worker',
         'blocks': []})
    print('PHASE10_SOURCE_VERIFIED', flush=True)


def recover_source(s):
    s.settings.file.read_case(file_name=str(WORK / 'parent-A-N1580.cas.h5'))
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    s.settings.file.read_data(file_name=str(WORK / 'parent-A-N1580.dat.h5'))
    source = base.state(s)
    source['reports'] = s.settings.solution.report_definitions.get_state()
    source['clock'] = dict(s.rp_vars('wall-film/solution-state'))
    if source['clock']['film_elapsed_time'] != 0:
        raise RuntimeError('Recovery source is not dry A')
    dump('source-state.json', source)
    names = s.settings.setup.models.discrete_phase.injections.get_object_names()
    s.tui.file.write_injections('"' + (WORK / 'source-A.inj').as_posix() + '"', *names, '()')
    if not (WORK / 'source-A.inj').is_file():
        raise RuntimeError('Native injection export absent')
    dump('run-manifest.json', {'status': 'SOURCE_VERIFIED', 'target_total_film_age_s': .100,
         'work': str(WORK), 'parent_hashes': HASHES, 'session': 'direct-local-252',
         'review': 'Recovered quoted native export path after preserving prior session; no solve issued', 'blocks': []})
    print('PHASE10_SOURCE_VERIFIED_EXPORT_RECOVERED', flush=True)


def inspect_target(s):
    s.settings.file.read_mesh(file_name=str(MESH))
    s.settings.mesh.check()
    s.settings.mesh.size_info()
    dump('target-native-state.json', {'boundaries': s.settings.setup.boundary_conditions.get_state(),
                                     'cells': s.settings.setup.cell_zone_conditions.get_state()})
    print('PHASE10_TARGET_READ', flush=True)


def split_target(s):
    from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest, SurfaceDataType
    import numpy as np
    geometry = s.fields.field_data.get_field_data(SurfaceFieldDataRequest(
        surfaces=['steamoutlet'], data_types=[SurfaceDataType.Vertices]))
    height = float(np.asarray(geometry['steamoutlet'].vertices)[:, 1].mean())
    if abs(height - 6261) < 10:
        scale = .001
        s.settings.mesh.scale(x_scale=scale, y_scale=scale, z_scale=scale)
    elif abs(height - 6.261) < .01:
        scale = 1
    else:
        raise RuntimeError('Unverified physical scale: outlet height ' + str(height))
    renames = {'simple-spiral-separator--brine-outlet-': 'separator-purnanto',
               'simple-spiral-separator--brine-outlet-:1': 'separator-purnanto:1',
               'interior--simple-spiral-separator--brine-outlet-': 'interior--separator-purnanto'}
    for old, new in renames.items():
        s.settings.mesh.modify_zones.zone_name(zone_name=old, new_name=new)
    register, selection = create_lower_register(s)
    s.settings.mesh.modify_zones.sep_cell_zone_mark(cell_zone_name='separator-purnanto',
                                                   register=register, move_faces=True)
    generated = [n for n in s.settings.setup.cell_zone_conditions.fluid.get_object_names()
                 if n != 'separator-purnanto']
    if len(generated) != 1:
        raise RuntimeError('Expected one lower collector zone')
    s.settings.mesh.modify_zones.zone_name(zone_name=generated[0], new_name='p71a-v2-virtual-outlet')
    s.settings.mesh.check()
    s.settings.file.write_case(file_name=str(WORK / 'split-target.cas.h5'))
    dump('target-split.json', {'scale_applied': scale, 'native_outlet_height_before': height,
         'register': selection, 'renames': renames,
         'boundaries': s.settings.setup.boundary_conditions.get_state(),
         'cells': s.settings.setup.cell_zone_conditions.get_state()})
    print('PHASE10_TARGET_SPLIT_READY_FOR_TOPOLOGY', flush=True)


def map_target(s):
    import h5py
    path = WORK / 'split-target.cas.h5'
    with h5py.File(path) as f:
        z = f['meshes/1/faces/zoneTopology']
        names = z['name'][0].decode().split(';')
        topology = {n: {k: int(z[k][i]) for k in ['c0', 'c1', 'id', 'zoneType']}
                    for i, n in enumerate(names)}
        cells = f['meshes/1/cells/zoneTopology']
        ids = dict(zip(cells['name'][0].decode().split(';'), map(int, cells['id'][()])))
    low, high = ids['p71a-v2-virtual-outlet'], ids['separator-purnanto']
    cross = [n for n, z in topology.items() if {z['c0'], z['c1']} == {low, high}]
    if len(cross) != 2 or topology['wall:001']['c0'] != low:
        raise RuntimeError('Unexpected lower-region topology')
    source = json.loads((OUT / 'source-state.json').read_text())
    entries = source['readback']['entry_faces']
    clean = lambda item: {k: v for k, v in item.items() if k != 'name'}
    if clean(list(entries.values())[0]) != clean(list(entries.values())[1]):
        raise RuntimeError('Reference entry boundary conditions differ')
    s.settings.file.read_case(file_name=str(path))
    renames = {'wall:001': 'wall:004', 'interior--separator-purnanto:004': 'interior--separator-purnanto:013'}
    renames.update(dict(zip(sorted(cross), sorted(entries))))
    for old, new in renames.items():
        s.settings.mesh.modify_zones.zone_name(zone_name=old, new_name=new)
    prior = s.settings.file.cff_files.get_state()
    try:
        s.settings.file.cff_files = False
        s.settings.file.write_case(file_name=str(WORK / 'mapped-target.cas'))
    finally:
        s.settings.file.cff_files = prior
    dump('target-map.json', {'topology': topology, 'cell_zone_ids': ids, 'renames': renames,
         'entry_basis': 'Same lower/upper adjacency; identical source conditions',
         'absent_parent_wall': 'separator-purnanto:1:001',
         'new_slit_wall': 'angled-slit-wall-simple-spiral-separator--brine-outlet-'})
    print('PHASE10_NATIVE_TARGET_MAPPED', flush=True)


def load(s, pair):
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    s.settings.file.read_data(file_name=pair['data'])
    manifest = OUT / 'run-manifest.json'
    if manifest.is_file():
        m = json.loads(manifest.read_text())
        clock = dict(s.rp_vars('wall-film/solution-state'))
        m.update(observed_film_age_s=clock['film_elapsed_time'],
                 film_update_count=clock['max_timestep_count'], native_end=native_iteration(s))
        dump('run-manifest.json', m)


def transfer(s, partition_per_zone=True):
    source = json.loads((OUT / 'source-state.json').read_text())
    load(s, {'case': str(WORK / 'parent-A-N1580.cas.h5'), 'data': str(WORK / 'parent-A-N1580.dat.h5')})
    replay.require_match(replay.readback(s), source['readback'])
    flag = '#t' if partition_per_zone else '#f'
    s.scheme.eval("(rpsetvar 'dynamesh/replace-mesh/partition-per-zone? " + flag + ")")
    dump('active-transfer-policy.json', {'partition_per_zone': partition_per_zone,
         'reason': 'Avoid source repartition SIGSEGV' if not partition_per_zone else 'Same-name zone mapping',
         'limit': 'Parallel native interpolation may map across zones; record inventory changes separately'})
    s.settings.mesh.replace(file_name=str(WORK / 'mapped-target.cas'), zones=False)
    injections = s.settings.setup.models.discrete_phase.injections
    expected = list(source['readback']['dpm']['injections'])
    actual = injections.get_object_names()
    if not actual:
        s.settings.file.read_injections(file_name=str(WORK / 'source-A.inj'))
    for _ in range(len(expected) + 1):
        actual = injections.get_object_names()
        extras = set(actual) - set(expected)
        if not extras:
            break
        if not all(n.startswith('imported-inj-') for n in extras):
            raise RuntimeError('Untraced injection transfer')
        injections.delete(name_list=sorted(extras))
    if sorted(injections.get_object_names()) != sorted(expected):
        raise RuntimeError('Injection object inventory differs')
    slit = 'angled-slit-wall-simple-spiral-separator--brine-outlet-'
    boundary = copy.deepcopy(source['setup']['boundary_conditions']['wall']['separator-purnanto:1'])
    boundary['name'] = slit
    s.settings.setup.boundary_conditions.wall[slit].set_state(boundary)
    reports = s.settings.solution.report_definitions
    for group, items in source['reports'].items():
        if not isinstance(items, dict):
            continue
        for name, record in items.items():
            if isinstance(record, dict) and 'separator-purnanto:1:001' in record.get('surface_names', []):
                surfaces = [n for n in record['surface_names'] if n != 'separator-purnanto:1:001']
                surfaces.append(slit)
                getattr(reports, group)[name].surface_names = surfaces
    after = base.state(s)
    for group in ['hooks', 'lower_film_wall', 'entry_faces', 'dpm', 'film_parameters', 'controls']:
        if after['readback'][group] != source['readback'][group]:
            dump('transfer-invariant-error.json', {'group': group, 'actual': after['readback'][group],
                                                   'expected': source['readback'][group]})
            raise RuntimeError('Transferred invariant differs: ' + group)
    if after['methods'] != source['methods']:
        raise RuntimeError('Bulk methods changed')
    if after['readback']['fields']['v2-total-liquid-mass'][0] <= 0:
        raise RuntimeError('Mapped bulk fields are empty')
    if after['readback']['fields']['p72a-e2.7-ewf-film-mass-total'][0] != 0:
        raise RuntimeError('Mapped film is not dry')
    s.settings.file.auto_save.data_frequency = 0
    base.add_pressure_reports(s)
    paths = instrument(s, 'startup')
    before = base.state(s)
    pair = save(s, 'prepared-dry-A')
    load(s, pair)
    after = base.state(s)
    nonflux = {n: v for n, v in before['readback']['fields'].items() if 'flux' not in n}
    replay.require_match({**after['readback'], 'fields': {n: after['readback']['fields'][n] for n in nonflux}},
                         {**before['readback'], 'fields': nonflux})
    if before['setup'] != after['setup'] or before['methods'] != after['methods']:
        raise RuntimeError('Paired reopen changed setup')
    if before['readback']['fields'] != after['readback']['fields']:
        pair = save(s, 'prepared-dry-A-stable-flux')
        before = after
        load(s, pair)
        after = base.state(s)
        replay.require_match(after['readback'], before['readback'])
    clock = dict(s.rp_vars('wall-film/solution-state'))
    if clock['film_elapsed_time'] != 0:
        raise RuntimeError('Transfer advanced dry-film clock')
    dump('prepared-reopen.json', {'pair': pair, 'state': after, 'clock': clock, 'paths': paths,
         'slit_mapping': 'Complete reference non-film rough-wall condition',
         'report_mapping': 'Outer-wall union excludes absent parent subface and includes new slit'})
    m = json.loads((OUT / 'run-manifest.json').read_text())
    m.update(status='PREPARED_REOPEN_VERIFIED', latest_pair=pair, paths=paths)
    dump('run-manifest.json', m)
    print('PHASE10_CHILD_REOPEN_VERIFIED', flush=True)


def instrument(s, label):
    folder = WORK / 'monitors' / label
    folder.mkdir(parents=True, exist_ok=False)
    paths = {}
    for name in s.settings.solution.monitor.report_files.get_object_names():
        obj = s.settings.solution.monitor.report_files[name]
        definitions = obj.report_defs()
        if len(definitions) != 1:
            raise RuntimeError('Expected one definition per report file')
        path = folder / (definitions[0] + '.out')
        obj.file_name = str(path)
        obj.frequency_of = 'iteration'
        obj.frequency = 1
        obj.active = True
        paths[definitions[0]] = str(path)
    return paths


def report_histories(s, m):
    """Follow native report-file renaming on reopen; keep all source files intact."""
    routes = m.setdefault('report_path_history', {name: [path] for name, path in m['paths'].items()})
    for item in s.settings.solution.monitor.report_files.get_state().values():
        definitions = item['report_defs']
        if len(definitions) != 1 or definitions[0] not in routes:
            raise RuntimeError('Native report route differs')
        path = Path(item['file_name'])
        if not path.is_absolute():
            path = WORK.parent / path
        path = path.resolve()
        if not path.is_relative_to(WORK.resolve()) or not path.is_file():
            raise RuntimeError('Native report source unavailable: ' + str(path))
        if str(path) not in routes[definitions[0]]:
            routes[definitions[0]].append(str(path))
    result = {}
    for name, files in routes.items():
        rows = {}
        for file in files:
            rows.update(history(Path(file).read_text()))
        result[name] = rows
    return result


def batch(s, steps, label, checkpoint=True):
    m = json.loads((OUT / 'run-manifest.json').read_text())
    start = native_iteration(s)
    initial = dict(s.rp_vars('wall-film/solution-state'))
    initial['film_elapsed_time'] = m.get('observed_film_age_s', initial['film_elapsed_time'])
    initial['max_timestep_count'] = m.get('film_update_count', initial['max_timestep_count'])
    path = WORK / (label + '.trn')
    m.update(status='RUNNING_' + label, active_target=start + steps,
             native_start=start, started_epoch=time.time(), transcript=str(path))
    dump('run-manifest.json', m)
    print('PHASE10_NATIVE_BATCH', label, start, steps, flush=True)
    try:
        with native_transcript(s.settings.file, path):
            base.iterate(s, steps)
        end = native_iteration(s)
        if end != start + steps:
            raise RuntimeError('Native iteration horizon differs')
        # Writing data synchronizes the host's film solution state from nodes.
        pair = save(s, label + '-N' + str(end)) if checkpoint else None
        films = [list(map(float, match.groups())) for match in FILM.finditer(path.read_text())]
        if len(films) != steps:
            raise RuntimeError('Native film clock coverage incomplete')
        clock = dict(s.rp_vars('wall-film/solution-state'))
        if not checkpoint:
            clock['film_elapsed_time'] = films[-1][0]
            clock['max_timestep_count'] = initial['max_timestep_count'] + steps
        if end != start + steps or clock['max_timestep_count'] - initial['max_timestep_count'] != steps:
            raise RuntimeError('Native iteration or film-update horizon differs')
        histories = report_histories(s, m)
        expected = set(range(start + 1, end + 1))
        if any(not expected.issubset(h) or not all(math.isfinite(v) for i, v in h.items() if i in expected)
               for h in histories.values()):
            raise RuntimeError('Native report coverage incomplete or nonfinite')
        if histories['p72a-e2.7-ewf-thickness-max'][end] > .003:
            raise RuntimeError('Film thickness exceeds the development bound')
        record = {'label': label, 'native_start': start, 'native_end': end,
                  'film_age_s': clock['film_elapsed_time'], 'wall_seconds': time.time() - m['started_epoch'],
                  'added_film_time_s': clock['film_elapsed_time'] - initial['film_elapsed_time'],
                  'film_mass_kg': histories['p72a-e2.7-ewf-film-mass-total'][end],
                  'peak_courant': max(v[2] for v in films), 'pair': pair, 'transcript': str(path)}
        if not any(s.settings.solution.controls.equations.get_state().values()):
            mass = histories['p72a-e2.7-ewf-film-mass-total']
            drain = histories['p72a-e2.7-ewf-outflow-mass-total']
            accretion = histories['p72a-e2.7-ewf-secondary-phase-mass-total']
            previous = initial['film_elapsed_time']
            supplied = 0.0
            for i, film in zip(range(start + 1, end + 1), films):
                supplied += accretion[i] * (film[0] - previous)
                previous = film[0]
            gain, removed = mass[end] - mass[start], drain[end] - drain[start]
            record.update(integrated_input_kg=supplied, integrated_removal_kg=removed,
                          film_storage_kg=gain,
                          ledger_error_percent=100 * abs(gain + removed - supplied) / max(abs(supplied), 1e-30))
        m.setdefault('blocks', []).append(record)
        m.update(status='IDLE_VERIFIED', active_target=None, native_end=end, observed_film_age_s=clock['film_elapsed_time'])
        m['film_update_count'] = clock['max_timestep_count']
        if pair:
            m['latest_pair'] = pair
        dump(label + '-metrics.json', record)
        dump('run-manifest.json', m)
        print('PHASE10_BATCH_VERIFIED', label, end, clock['film_elapsed_time'], flush=True)
        return record
    except BaseException:
        m.update(status='RECOVERY_REQUIRED', error=traceback.format_exc())
        dump('run-manifest.json', m)
        raise


def reconcile_smoke(s):
    m = json.loads((OUT / 'run-manifest.json').read_text())
    if m['native_start'] != 1580 or m['active_target'] != 1600 or native_iteration(s) != 1600:
        raise RuntimeError('Unexpected failed-smoke horizon')
    pair = save(s, 'startup-smoke-N1600')
    clock = dict(s.rp_vars('wall-film/solution-state'))
    films = [list(map(float, match.groups())) for match in FILM.finditer(Path(m['transcript']).read_text())]
    histories = {name: history(Path(file).read_text()) for name, file in m['paths'].items()}
    if len(films) != 20 or any(not set(range(1581, 1601)).issubset(h) for h in histories.values()):
        raise RuntimeError('Smoke evidence coverage incomplete')
    if not math.isclose(clock['film_elapsed_time'], 20e-6, abs_tol=1e-12):
        raise RuntimeError('Saved smoke film clock differs from printed endpoint')
    record = {'label': 'startup-smoke', 'native_start': 1580, 'native_end': 1600,
              'film_age_s': clock['film_elapsed_time'], 'film_mass_kg': histories['p72a-e2.7-ewf-film-mass-total'][1600],
              'peak_courant': max(v[2] for v in films), 'pair': pair,
              'transcript': m['transcript'], 'reconciliation': 'Completed solve counted once; saved data synchronizes host clock'}
    m.update(status='IDLE_VERIFIED', native_end=1600, active_target=None,
             observed_film_age_s=clock['film_elapsed_time'], film_update_count=clock['max_timestep_count'],
             latest_pair=pair, blocks=[record])
    m['reconciled_error'] = m.pop('error')
    dump('startup-smoke-metrics.json', record)
    dump('run-manifest.json', m)
    print('PHASE10_SMOKE_RECONCILED_NO_REPEAT', clock, flush=True)


def startup_smoke(s):
    m = json.loads((OUT / 'run-manifest.json').read_text())
    if m['status'] != 'PREPARED_REOPEN_VERIFIED':
        raise RuntimeError('Smoke requires verified prepared child')
    from pyansys_fluent.stage4_native import configure_autosave
    autosave = configure_autosave(s, str(WORK), data_frequency=500)
    dump('startup-autosave.json', autosave)
    return batch(s, 20, 'startup-smoke')


def full_feed_screen(m):
    histories = {n: history(Path(p).read_text()) for n, p in m['paths'].items()}
    end = m['native_end']
    coordinates = range(end - 999, end + 1)
    p_in, p_out = histories['p72s3-pressure-inlet'], histories['p72s3-pressure-outlet']
    quantities = {'pressure': [p_in[i] - p_out[i] for i in coordinates],
                  'bulk': [histories['v2-total-liquid-mass'][i] for i in coordinates],
                  'liquid_outlet': [histories['v2-flux-phase2-steamoutlet'][i] for i in coordinates]}
    ranges = {name: 100 * (max(v) - min(v)) / max(abs(sum(v) / len(v)), 1e-30)
              for name, v in quantities.items() if name != 'liquid_outlet'}
    ranges['liquid_outlet'] = 100 * (max(quantities['liquid_outlet']) - min(quantities['liquid_outlet'])) / 116.92
    return {'native_end': end, 'ranges_percent': ranges,
            'pass': ranges['pressure'] <= 5 and ranges['bulk'] <= 10 and ranges['liquid_outlet'] <= 5}


def startup(s):
    m = json.loads((OUT / 'run-manifest.json').read_text())
    if len(m.get('blocks', [])) != 1 or m['blocks'][0]['label'] != 'startup-smoke':
        raise RuntimeError('Startup requires the single counted smoke block')
    batch(s, 980, 'low-feed-hold')
    for offset in range(10, 2001, 10):
        base.loading(s, .25 + .75 * offset / 2000)
        batch(s, 10, 'ramp-' + str(offset), checkpoint=offset % 500 == 0)
    passing = 0
    for block in range(1, 21):
        batch(s, 1000, 'full-feed-hold-' + str(block))
        m = json.loads((OUT / 'run-manifest.json').read_text())
        screen = full_feed_screen(m)
        m.setdefault('full_feed_screens', []).append(screen)
        passing = passing + 1 if screen['pass'] else 0
        dump('run-manifest.json', m)
        if block >= 2 and passing >= 2:
            m.update(status='FULL_FEED_PREPARED', full_feed_screen_pass=True)
            dump('run-manifest.json', m)
            print('PHASE10_FULL_FEED_PREPARED', flush=True)
            return
    raise RuntimeError('Bulk preparation budget exhausted; preserve endpoint before next decision')


def parameters(s, changes):
    original = dict(s.rp_vars('wall-film/model-parameters'))
    if not set(changes).issubset(original):
        raise RuntimeError('Unknown live film parameter')
    s.rp_vars('wall-film/model-parameters', [(k, changes.get(k, v)) for k, v in original.items()])
    actual = dict(s.rp_vars('wall-film/model-parameters'))
    if any(actual[k] != changes.get(k, v) for k, v in original.items()):
        raise RuntimeError('Film parameter readback failed')


def film_fields(s):
    import numpy as np
    from ansys.fluent.core.fields.field_data_interfaces import ScalarFieldDataRequest
    fields = ['film-mass', 'film-thickness', 'film-x-velocity', 'film-y-velocity', 'film-z-velocity']
    return {name: np.asarray(s.fields.field_data.get_field_data(ScalarFieldDataRequest(
        surfaces=['wall'], field_name=name, node_value=False, boundary_value=True))['wall']).reshape(-1)
        for name in fields}


def compare_film(reference, candidate):
    import numpy as np
    m = reference['film-mass']
    if any(not np.isfinite(v).all() for v in candidate.values()):
        raise RuntimeError('Nonfinite film fields')
    if any(candidate[k].shape != v.shape for k, v in reference.items()):
        raise RuntimeError('Film field shapes differ')
    mass = 100 * np.abs(candidate['film-mass'] - m).sum() / max(abs(m).sum(), 1e-30)
    rv = np.stack([reference['film-' + a + '-velocity'] for a in 'xyz'], axis=1)
    cv = np.stack([candidate['film-' + a + '-velocity'] for a in 'xyz'], axis=1)
    velocity = 100 * (abs(m) * np.linalg.norm(cv - rv, axis=1)).sum() / max(
        (abs(m) * np.linalg.norm(rv, axis=1)).sum(), 1e-30)
    thickness = 100 * abs(candidate['film-thickness'].max() - reference['film-thickness'].max()) / max(
        abs(reference['film-thickness'].max()), 1e-30)
    return {'mass_l1_percent': float(mass), 'weighted_velocity_percent': float(velocity),
            'maximum_thickness_percent': float(thickness),
            'fields_pass': mass <= 1 and velocity <= 2 and thickness <= 2}


def qualify_film(s):
    import numpy as np
    m = json.loads((OUT / 'run-manifest.json').read_text())
    if m['status'] != 'FULL_FEED_PREPARED':
        raise RuntimeError('Frozen development requires full-feed preparation')
    before = replay.readback(s)
    equations = s.settings.solution.controls.equations
    original = equations.get_state()
    for name in original:
        equations[name] = False
    if any(equations.get_state().values()):
        raise RuntimeError('Bulk freeze failed')
    replay.require_match({'fields': replay.readback(s)['fields']}, {'fields': before['fields']})
    parameters(s, {'implicit-scheme-new?': True, 'ewf-adaptive?': False, 'timestep-max': .5e-6})
    parent = save(s, 'frozen-qualification-parent')
    original_mass = before['fields']['v2-total-liquid-mass'][0]
    ref = batch(s, 1000, 'film-reference-0p5us')
    reference = film_fields(s)
    np.savez_compressed(OUT / 'film-reference-fields.npz', **reference)
    if ref['ledger_error_percent'] > .1:
        raise RuntimeError('Conservative film ledger fails qualification')
    tested = []
    # Use the smaller historically tested candidate first; stability is the priority.
    for step, count in [(5e-6, 100), (1e-6, 500)]:
        load(s, parent)
        parameters(s, {'timestep-max': step})
        trial = batch(s, count, 'film-candidate-' + str(round(step * 1e6)) + 'us')
        comparison = compare_film(reference, film_fields(s))
        comparison.update(step_s=step, candidate=trial, reference=ref)
        passed = comparison['fields_pass'] and trial['ledger_error_percent'] <= .1
        comparison['pass'] = passed
        tested.append(comparison)
        dump('film-step-qualification.json', tested)
        if passed:
            if not math.isclose(replay.readback(s)['fields']['v2-total-liquid-mass'][0], original_mass, rel_tol=1e-10):
                raise RuntimeError('Bulk inventory changed during frozen qualification')
            m = json.loads((OUT / 'run-manifest.json').read_text())
            m.update(status='FILM_STEP_QUALIFIED', film_step_s=step, bulk_original_equations=original,
                     frozen_bulk_mass_kg=original_mass, qualification_parent=parent,
                     numerical_limit='Alternative implicit solver does not provide inner residuals',
                     frozen_bulk_drain_proof='PENDING_POSITIVE_REMOVAL')
            dump('run-manifest.json', m)
            return step
    load(s, ref['pair'])
    m = json.loads((OUT / 'run-manifest.json').read_text())
    m.update(status='FILM_STEP_QUALIFIED', film_step_s=.5e-6, bulk_original_equations=original,
             frozen_bulk_mass_kg=original_mass, qualification_parent=parent,
             numerical_limit='Conservative reference retained; no faster candidate passed; alternative inner residuals unavailable',
             latest_pair=ref['pair'], frozen_bulk_drain_proof='PENDING_POSITIVE_REMOVAL')
    dump('run-manifest.json', m)
    return .5e-6


def bulk_persistence(parent, child):
    import h5py
    import numpy as np
    checks = []
    with h5py.File(parent['data']) as a, h5py.File(child['data']) as b:
        for phase in ['phase-1', 'phase-2']:
            for field in ['SV_U', 'SV_V', 'SV_W', 'SV_P', 'SV_K', 'SV_D', 'SV_VOF',
                          'SV_SLIP_U', 'SV_SLIP_V', 'SV_SLIP_W']:
                key = 'results/1/' + phase + '/cells/' + field
                if key not in a:
                    continue
                if key not in b or set(a[key]) != set(b[key]):
                    raise RuntimeError('Saved bulk field inventory differs: ' + key)
                equal = all(np.array_equal(a[key][n][()], b[key][n][()]) for n in a[key])
                checks.append({'field': key, 'exact_equal': equal})
    if len(checks) < 3 or not all(item['exact_equal'] for item in checks):
        dump('frozen-bulk-persistence-error.json', checks)
        raise RuntimeError('Frozen bulk fields changed')
    return checks


def finish_run(s):
    """Validated dependency boundary for queued execution after bulk startup.

    A failed startup cannot enter film development. Solver stays open on return.
    """
    try:
        step = qualify_film(s)
        m = json.loads((OUT / 'run-manifest.json').read_text())
        parent = m['qualification_parent']
        checks = bulk_persistence(parent, m['latest_pair'])
        candidate = next(b for b in reversed(m['blocks']) if b.get('pair') == m['latest_pair'])
        if candidate.get('integrated_removal_kg', 0) > 1e-10 and candidate['ledger_error_percent'] <= .1:
            m['frozen_bulk_drain_proof'] = 'PASS_DIRECT_NATIVE_EWF_OUTFLOW_WITH_IDENTICAL_BULK_FIELDS'
        else:
            # One bounded functional probe: transport may need time to reach the drain.
            probe = batch(s, 100, 'frozen-drain-functional-probe')
            m = json.loads((OUT / 'run-manifest.json').read_text())
            checks = bulk_persistence(parent, m['latest_pair'])
            if probe['integrated_removal_kg'] <= 1e-10 or probe['ledger_error_percent'] > .1:
                raise RuntimeError('Direct frozen-bulk removal proof remains incomplete')
            m['frozen_bulk_drain_proof'] = 'PASS_DIRECT_NATIVE_EWF_OUTFLOW_WITH_IDENTICAL_BULK_FIELDS'
        dump('frozen-drain-proof.json', {'status': 'PASS', 'bulk_checks': checks,
                                       'removal_route': 'Native EWF outflow at lower edge of upper film wall'})
        m.update(status='FILM_DEVELOPING', selected_film_step_s=step)
        dump('run-manifest.json', m)
        for index in range(1, 201):
            m = json.loads((OUT / 'run-manifest.json').read_text())
            remaining = .100 - m['observed_film_age_s']
            if remaining <= 1e-12:
                break
            steps = min(1000, max(1, int(math.ceil(remaining / step - 1e-9))))
            if steps < 1000:
                # The finite endpoint is the next required decision; use fixed exact steps.
                final_step = remaining / steps
                parameters(s, {'timestep-max': final_step})
            result = batch(s, steps, 'film-development-' + str(index))
            m = json.loads((OUT / 'run-manifest.json').read_text())
            if result['ledger_error_percent'] > .1:
                raise RuntimeError('Film ledger exceeds the qualified development tolerance')
            bulk_persistence(parent, m['latest_pair'])
            if not math.isclose(replay.readback(s)['fields']['v2-total-liquid-mass'][0],
                                m['frozen_bulk_mass_kg'], rel_tol=1e-10):
                raise RuntimeError('Frozen bulk mass changed')
        else:
            raise RuntimeError('Finite film development update budget exhausted')
        m = json.loads((OUT / 'run-manifest.json').read_text())
        if abs(m['observed_film_age_s'] - .100) > 1e-10:
            raise RuntimeError('Requested 100 ms horizon not attained')
        before = replay.readback(s)
        pair = save(s, 'final-100ms')
        load(s, pair)
        replay.require_match(replay.readback(s), before)
        clock = dict(s.rp_vars('wall-film/solution-state'))
        if abs(clock['film_elapsed_time'] - .100) > 1e-10:
            raise RuntimeError('Final reopen film clock differs')
        final_fields = film_fields(s)
        import numpy as np
        np.savez_compressed(OUT / 'final-100ms-film-fields.npz', **final_fields)
        m = json.loads((OUT / 'run-manifest.json').read_text())
        m.update(status='COMPLETE_100MS_ENDPOINT_REOPEN_VERIFIED', final_pair=pair,
                 observed_film_age_s=clock['film_elapsed_time'], active_target=None,
                 solver_left_open=True, completed_epoch=time.time(),
                 claim='Finite frozen-bulk basic EWF development; steady film and whole-separator closure unqualified')
        dump('final-reopen.json', {'pair': pair, 'clock': clock, 'readback': replay.readback(s)})
        dump('run-manifest.json', m)
        plot_final(s, m, final_fields)
        print('PHASE10_COMPLETE_100MS_ENDPOINT_REOPEN_VERIFIED', flush=True)
    except BaseException:
        m = json.loads((OUT / 'run-manifest.json').read_text())
        m.update(status='RECOVERY_REQUIRED', error=traceback.format_exc(), solver_left_open=True)
        dump('run-manifest.json', m)
        print('PHASE10_RECOVERY_REQUIRED_ENDPOINTS_PRESERVED', flush=True)
        raise


def plot_final(s, m, fields):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest, SurfaceDataType
    selected = 'film-candidate-' + str(round(m['selected_film_step_s'] * 1e6)) + 'us'
    if m['selected_film_step_s'] == .5e-6:
        selected = 'film-reference-0p5us'
    blocks = [b for b in m['blocks'] if b['label'].startswith(('startup-', 'low-feed-', 'ramp-',
        'full-feed-', 'film-development-', 'frozen-drain-')) or b['label'] == selected]
    directory = REPO / 'Project/experiments/phase-10-proposed-design/figures'
    directory.mkdir(exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    axes[0].plot([0] + [b['film_age_s'] * 1000 for b in blocks],
                 [0] + [b['film_mass_kg'] for b in blocks], marker='.', lw=1)
    axes[0].set_ylabel('Film mass (kg)')
    frozen = [b for b in blocks if 'integrated_input_kg' in b]
    for key, label in [('integrated_input_kg', 'Accretion'), ('integrated_removal_kg', 'Removal'),
                       ('film_storage_kg', 'Storage')]:
        axes[1].plot([b['film_age_s'] * 1000 for b in frozen],
                     [b[key] / b['added_film_time_s'] for b in frozen], marker='.', label=label)
    axes[1].set_ylabel('Window mean (kg/s)')
    axes[1].set_xlabel('Total native film age (ms)')
    axes[1].legend()
    for ax in axes:
        ax.grid(alpha=.25)
    fig.suptitle('Phase 10 proposed design — basic EWF, finite 100 ms endpoint')
    fig.tight_layout()
    fig.savefig(directory / 'film-development-100ms.png', dpi=160)
    plt.close(fig)
    geom = s.fields.field_data.get_field_data(SurfaceFieldDataRequest(
        surfaces=['wall'], data_types=[SurfaceDataType.FacesCentroid]))
    centroids = np.asarray(geom['wall'].face_centroids)
    np.savez_compressed(OUT / 'final-wall-centroids.npz', centroids=centroids)
    fig, ax = plt.subplots(figsize=(6, 8))
    im = ax.scatter(centroids[:, 0], centroids[:, 1], c=fields['film-thickness'] * 1000,
                    s=2, vmin=0, cmap='viridis')
    ax.set_aspect('equal')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title('Upper film wall at 100 ms — x/y projection')
    fig.colorbar(im, ax=ax, label='Film thickness (mm)')
    fig.tight_layout()
    fig.savefig(directory / 'film-thickness-100ms.png', dpi=160)
    plt.close(fig)
    path = REPO / 'Project/experiments/phase-10-proposed-design/results.md'
    text = path.read_text()
    text = text.replace('| Current run | Bulk low-feed hold launched | Ramp, full-feed preparation and 100 ms film endpoint pending |',
        '| Current run | 100 ms final pair saved/reopened; Fluent left open | Frozen-bulk development; steady film and whole-separator closure unqualified |')
    text += '\n![Film development](figures/film-development-100ms.png)\n\n' \
            'Selected continuation only; qualification sibling branches excluded. Frozen-bulk rates use accepted film time.\n\n' \
            '![Film thickness](figures/film-thickness-100ms.png)\n\n' \
            'Native upper-film-wall facet values; projected x/y view.\n'
    path.write_text(text)
