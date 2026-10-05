"""Native mesh transfer of the verified early-EWF startup on owned Server 3."""
from pathlib import Path, PureWindowsPath
import argparse
import functools
import json
import math
import sys
import time
import traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists, remote_chdir
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256
from run_phase72a_e27_server1_continuation import pair_save, native_iteration, dump
import run_phase72a_stage3_server3 as base
from run_phase72a_local_film_replay import readback, require_match

OUT = ROOT / 'output/phase72a-stage3-slit154k-server3/20261005'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage3\slit154k-20261005')
SHARED_ROOT = PureWindowsPath(r'C:\Users\syok443\OneDrive - The University of Auckland')
MESH = SHARED_ROOT / '2026 Sem 1/700/P4PCFD/CAD PurnantoV2/Design improvement/Separator-vertical-slit-154k.msh.h5'
PARENT = SHARED_ROOT / 'P4P-Fluent-Artifacts/Phase72A/Stage3/early-ewf-startup/prepared-A-N1580/prepared-A-N1580'
PARENT_HASHES = {'case': '5907e357654ebe5437c64f4e6abea19cbbc66b1edd2312f6b2eb63fe408c2b72',
                 'data': '72a7134f6358ea68615907f336e71d6e518c713418674477703fc638e41816af'}
SHARED = SHARED_ROOT / 'P4P-Fluent-Artifacts/Phase72A/Stage3/slit154k-20261005'
base.OUT, base.WORK = OUT, WORK


def attach():
    import ansys.fluent.core._grpc_services as low
    import ansys.fluent.core.services as high
    from ansys.fluent.core.utils.fluent_version import FluentVersion
    from ansys.fluent.core import config
    low._server_supports_v1 = lambda channel: False
    high.create_service_factory = functools.partial(high.create_service_factory, product_version=FluentVersion.v252)
    config.check_health = False
    solver = connect('3', start_transcript=False, tcp_timeout_seconds=5)
    if '2025 R2' not in str(solver.get_fluent_version()):
        raise RuntimeError('Requires the reference Fluent 2025 R2')
    return solver


def save(s, label):
    return pair_save(s, WORK / f'{label}.cas.h5', WORK / 'scratch', scratch_tag=label)


def inspect_target(s):
    path = OUT / 'run-manifest.json'
    if path.exists():
        raise RuntimeError('Reconcile previous mesh inspection before reuse')
    if not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Owned server is solving; preserve through controlled interruption first')
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors']:
        ensure_remote_directory(s, str(folder))
    for p in [MESH, str(PARENT) + '.cas.h5', str(PARENT) + '.dat.h5']:
        if not remote_file_exists(s, str(p)):
            raise FileNotFoundError(str(p))
    m = {'status': 'PREFLIGHT', 'server_id': '3', 'authority': 'human_full_server3_ownership_new_slit_mesh_20261005',
         'mesh': str(MESH), 'work_root': str(WORK), 'parent': str(PARENT), 'blocks': []}
    dump(path, m)
    for kind, ext in [('case', 'cas.h5'), ('data', 'dat.h5')]:
        actual = remote_file_sha256(s, str(PARENT) + '.' + ext, str(WORK / 'scratch' / f'parent-{kind}.sha256.txt'))
        if actual != PARENT_HASHES[kind]:
            raise RuntimeError('Prepared A parent hash differs: ' + kind)
    m['parent_hashes'] = PARENT_HASHES
    m['mesh_sha256'] = remote_file_sha256(s, str(MESH), str(WORK / 'scratch' / 'mesh.sha256.txt'))
    m['preserved_previous_endpoint'] = save(s, f'previous-server3-N{native_iteration(s)}')
    dump(path, m)
    remote_chdir(s, str(WORK))
    s.transcript.start(file_name=str(OUT / 'target-mesh-inspection.txt'), write_to_stdout=False)
    s.settings.file.read_mesh(file_name=str(MESH))
    s.settings.mesh.check()
    s.settings.mesh.size_info()
    s.tui.mesh.modify_zones.list_zones()
    s.transcript.stop()
    snapshot = {'bc': s.settings.setup.boundary_conditions.get_state(),
                'cell_zones': s.settings.setup.cell_zone_conditions.get_state(),
                'replace_mesh': {'args': s.settings.file.replace_mesh.argument_names, 'help': s.settings.file.replace_mesh.__doc__}}
    dump(OUT / 'target-mesh-state.json', snapshot)
    m.update(status='TARGET_MESH_INSPECTED')
    dump(path, m)
    print(json.dumps(snapshot, indent=2, default=str), flush=True)


def map_target(s):
    from run_p7_e5_cz import create_lower_register
    m = json.loads((OUT / 'run-manifest.json').read_text())
    if m['status'] != 'TARGET_MESH_INSPECTED':
        raise RuntimeError('Requires inspected target mesh')
    s.transcript.start(file_name=str(OUT / 'map-target-transcript.txt'), write_to_stdout=False)
    modify = s.settings.mesh.modify_zones
    # Native transfer matches names. Preserve physical identity in the mapping
    # receipt; the new inlet/slit solids receive the reference non-film wall BC.
    renames = {'vertical-slit': 'separator-purnanto',
               'vertical-slit:1': 'separator-purnanto:1',
               'interior--vertical-slit': 'interior--separator-purnanto'}
    for old, new in renames.items():
        modify.zone_name(zone_name=old, new_name=new)
    register, register_state = create_lower_register(s)
    modify.sep_cell_zone_mark(cell_zone_name='separator-purnanto', register=register, move_faces=True)
    generated = [n for n in s.settings.setup.cell_zone_conditions.fluid.get_object_names() if n != 'separator-purnanto']
    if len(generated) != 1:
        raise RuntimeError('Expected exactly one lower collector region')
    modify.zone_name(zone_name=generated[0], new_name='p71a-v2-virtual-outlet')
    s.settings.mesh.check()
    s.settings.mesh.size_info()
    modify.list_zones()
    # Read native topology before selecting generated boundary names.
    state = {'bc': s.settings.setup.boundary_conditions.get_state(),
             'cells': s.settings.setup.cell_zone_conditions.get_state(), 'register': register_state}
    dump(OUT / 'split-target-state.json', state)
    s.transcript.stop()
    m.update(status='TARGET_SPLIT_NAMES_REQUIRED', target_renames=renames, lower_register=register_state)
    dump(OUT / 'run-manifest.json', m)
    print('SPLIT_TARGET', {k:list(v) for k,v in state['bc'].items() if isinstance(v,dict)}, flush=True)


def transfer(s):
    m = json.loads((OUT / 'run-manifest.json').read_text())
    if m['status'] != 'TARGET_SPLIT_NAMES_REQUIRED':
        raise RuntimeError('Requires verified target split')
    s.transcript.start(file_name=str(OUT / 'native-transfer-transcript.txt'), write_to_stdout=False)
    # These correspondences were proved by the native saved-mesh c0/c1 zone
    # topology, not by assuming that generated suffixes have fixed meanings.
    renames = {'wall:001': 'wall:004',
               'interior--separator-purnanto:004': 'interior--separator-purnanto:013',
               'interior--separator-purnanto:003': 'interior--separator-purnanto:010',
               'interior--separator-purnanto:002': 'interior--separator-purnanto:007'}
    for old, new in renames.items():
        s.settings.mesh.modify_zones.zone_name(zone_name=old, new_name=new)
    m['target_renames'].update(renames)
    m['collector_topology_proof'] = {'start_mesh_sha256': 'f50b7814dec1985423a471ebd6ae6c2f877da64e65161a6f4df84750e38e0295',
        'lower_cell_count': 837, 'upper_cell_count': 153226,
        'entry_faces': {'interior--separator-purnanto:010': 276, 'interior--separator-purnanto:007': 362}}
    legacy = WORK / 'mapped-target.cas'
    if remote_file_exists(s, str(legacy)):
        raise FileExistsError(str(legacy))
    s.settings.file.cff_files = False
    s.settings.file.write_case(file_name=str(legacy))
    s.settings.file.cff_files = True
    if not remote_file_exists(s, str(legacy)):
        raise RuntimeError('Legacy mesh-bearing case was not written')
    m['native_replacement_input'] = str(legacy)
    # Load the exact prepared A. The original model settings are transferred
    # by Fluent; Python does not rebuild the turbulence, EWF or source setup.
    archive = base.SOURCE / 'contact-libraries.zip'
    actual = remote_file_sha256(s, str(archive), str(WORK / 'scratch' / 'contact-archive.sha256.txt'))
    if actual != base.HASHES['contact-libraries.zip']:
        raise RuntimeError('Contact UDF archive differs')
    base.powershell(s, f"$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath '{archive}' -DestinationPath '{WORK}'")
    local_parent = {}
    for kind, ext in [('case', 'cas.h5'), ('data', 'dat.h5')]:
        target = WORK / f'parent-A-N1580.{ext}'
        base.powershell(s, f"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath '{PARENT}.{ext}' -Destination '{target}'")
        if remote_file_sha256(s, str(target), str(WORK / 'scratch' / f'local-parent-{kind}.sha256.txt')) != PARENT_HASHES[kind]:
            raise RuntimeError('Copied A bytes differ')
        local_parent[kind] = str(target)
    remote_chdir(s, str(WORK))
    s.settings.file.read_case(file_name=local_parent['case'])
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    s.settings.file.read_data(file_name=local_parent['data'])
    source = base.state(s)
    source['reports'] = s.settings.solution.report_definitions.get_state()
    source['run_calculation'] = s.settings.solution.run_calculation.get_state()
    dump(OUT / 'loaded-source.json', source)
    expected = json.loads((ROOT / 'output/phase72a-stage3-early-ewf-server1/20261005/prepared-reopen.json').read_text())['state']
    for group in ['hooks', 'lower_film_wall', 'entry_faces', 'dpm', 'film_parameters', 'controls']:
        if source['readback'][group] != expected['readback'][group]:
            raise RuntimeError('Source settings differ before mesh transfer: ' + group)
    if source['methods'] != expected['methods'] or native_iteration(s) != 1580:
        raise RuntimeError('Source methods or coordinate differ')
    if not math.isclose(source['readback']['fields']['v2-total-liquid-mass'][0], 31.35713621088837, rel_tol=1e-9):
        raise RuntimeError('Source A bulk mass differs')
    s.tui.file.write_settings(str(WORK / 'source-A-settings.set'))
    names=s.settings.setup.models.discrete_phase.injections.get_object_names()
    s.tui.file.write_injections(str(WORK/'source-A.inj'),*names,'()')
    # Version-matched native replacement retains settings and interpolates data.
    # Partition per zone avoids implicit cross-zone interpolation in parallel.
    s.scheme.eval("(rpsetvar 'dynamesh/replace-mesh/partition-per-zone? #t)")
    s.settings.mesh.replace(file_name=str(legacy), zones=False)
    dump(OUT / 'native-transfer-before-new-wall.json', {'setup': s.settings.setup.get_state(),
         'methods': s.settings.solution.methods.get_state(), 'reports': s.settings.solution.report_definitions.get_state()})
    s.settings.file.read_injections(file_name=str(WORK/'source-A.inj'))
    finish_transfer(s, m, source)


def recover_transfer(s):
    m = json.loads((OUT / 'run-manifest.json').read_text())
    if m['blocks'] or not (OUT / 'native-transfer-before-new-wall.json').exists():
        raise RuntimeError('Only unrun native-transfer recovery is allowed')
    s.transcript.start(file_name=str(OUT / 'native-transfer-recovery.txt'), write_to_stdout=False)
    source = json.loads((OUT / 'loaded-source.json').read_text())
    finish_transfer(s, m, source)


def remap(s):
    m = json.loads((OUT / 'run-manifest.json').read_text())
    if m['blocks']:
        raise RuntimeError('Cannot remap a solved child')
    remote_chdir(s,str(WORK))
    s.transcript.start(file_name=str(OUT/'remap-native-transcript.txt'),write_to_stdout=False)
    s.settings.file.read_case(file_name=str(WORK/'parent-A-N1580.cas.h5'))
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    s.settings.file.read_data(file_name=str(WORK/'parent-A-N1580.dat.h5'))
    source=json.loads((OUT/'loaded-source.json').read_text())
    require_match(readback(s),source['readback'])
    names=s.settings.setup.models.discrete_phase.injections.get_object_names()
    s.tui.file.write_injections(str(WORK/'source-A.inj'),*names,'()')
    if not remote_file_exists(s,str(WORK/'source-A.inj')):
        raise RuntimeError('Native injection export file absent')
    s.scheme.eval("(rpsetvar 'dynamesh/replace-mesh/partition-per-zone? #t)")
    s.settings.mesh.replace(file_name=str(WORK/'mapped-target.cas'),zones=False)
    fields=readback(s)['fields']
    dump(OUT/'mapped-before-injection-recovery.json',fields)
    if fields['v2-total-liquid-mass'][0]<=0:
        raise RuntimeError('Native mapped bulk field is empty')
    s.settings.file.read_injections(file_name=str(WORK/'source-A.inj'))
    finish_transfer(s,m,source)


def finish_transfer(s, m, source):
    m['transfer_attempts'] = m.get('transfer_attempts', 0) + 1
    dump(OUT / 'run-manifest.json', m)
    injections=s.settings.setup.models.discrete_phase.injections
    for _ in range(7):
        extras=set(injections.get_object_names())-set(source['readback']['dpm']['injections'])
        if not extras:
            break
        if not all(n.startswith('imported-inj-') for n in extras):
            raise RuntimeError('Unexpected non-imported diagnostic injection')
        # This Fluent import may assign the same collision name to all six
        # duplicates. A native delete removes one such object per call.
        injections.delete(name_list=sorted(extras))
    else:
        raise RuntimeError('Native duplicate injection cleanup did not finish')
    report_target = json.loads(json.dumps(source['reports']))
    report_maps = {}
    for group, definitions in report_target.items():
        if not isinstance(definitions, dict):
            continue
        for name, record in definitions.items():
            if isinstance(record, dict) and 'separator-purnanto:1:001' in record.get('surface_names', []):
                record['surface_names'] = ['verticalslit-wall-vertical-slit' if n == 'separator-purnanto:1:001' else n for n in record['surface_names']]
                getattr(s.settings.solution.report_definitions, group)[name].surface_names = record['surface_names']
                report_maps[name] = record['surface_names']
    # The additional slit solid is unmatched by name. Copy its complete native
    # reference non-film rough-wall BC; only the new wall's name is changed.
    slit = 'verticalslit-wall-vertical-slit'
    wall_state = dict(source['setup']['boundary_conditions']['wall']['separator-purnanto:1'])
    wall_state['name'] = slit
    if s.settings.setup.boundary_conditions.wall[slit].get_state()!=wall_state:
        s.settings.setup.boundary_conditions.wall[slit].set_state(wall_state)
    s.settings.file.auto_save.data_frequency = 0
    paths = base.instrument(s, WORK / 'monitors' / f'transfer-{m["transfer_attempts"]}')
    after = base.state(s)
    for group in ['hooks', 'lower_film_wall', 'entry_faces', 'dpm', 'film_parameters', 'controls']:
        if after['readback'][group] != source['readback'][group]:
            raise RuntimeError('Native transfer changed invariant: ' + group)
    for group in set(source['setup'])-{'boundary_conditions','cell_zone_conditions'}:
        if after['setup'][group] != source['setup'][group]:
            raise RuntimeError('Native setup transfer changed invariant: ' + group)
    if after['methods'] != source['methods']:
        raise RuntimeError('Native transfer changed methods')
    if s.settings.solution.report_definitions.get_state() != report_target:
        raise RuntimeError('Native transfer changed report definitions')
    if after['readback']['fields']['p72a-e2.7-ewf-film-mass-total'][0] != 0:
        raise RuntimeError('Mapped dry film is not dry')
    for name in ['separator-purnanto:1', 'verticalslit-wall-vertical-slit', 'wall', 'wall:004']:
        mom = s.settings.setup.boundary_conditions.wall[name].phase['mixture'].turbulence.get_state()
        if not math.isclose(mom['roughness_height']['value'], 5e-4, abs_tol=1e-12) or mom['roughness_const']['value'] != .5:
            raise RuntimeError('R3 roughness changed on ' + name)
    m.update(status='TRANSFERRED_REOPEN_REQUIRED', native_start=native_iteration(s), requested_updates=3500,
             native_target=native_iteration(s)+3500, report_paths=paths, bulk_reinitialized=False,
             bulk_mapping='Fluent native Replace Mesh, same-name zone interpolation',
             film_step_s=1e-6, low_hold_updates=500, ramp_updates=2000, final_hold_updates=1000,
             additional_wall_mapping={'target':slit,'source':'separator-purnanto:1','scope':'complete non-film rough-wall BC'})
    m['report_surface_mapping'] = report_maps
    m['injection_transfer'] = 'Native Write/Read Injections after native mesh replacement'
    dump(OUT / 'run-manifest.json', m)
    dump(OUT / f'transfer-{m["transfer_attempts"]}-before-reopen.json', after)
    pair = save(s, f'prepared-mapped-A-N{native_iteration(s)}-transfer-{m["transfer_attempts"]}')
    m['prepared_pair']=pair
    dump(OUT/'run-manifest.json',m)
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    reopened = base.state(s)
    dump(OUT / f'transfer-{m["transfer_attempts"]}-after-reopen.json', reopened)
    try:
        require_match(reopened['readback'], after['readback'])
    except RuntimeError:
        # Interpolated face fluxes may be rebuilt on the first native reopen.
        # Inventories, source values and all settings must remain unchanged.
        a=after['readback'];b=reopened['readback']
        nonflux={n:v for n,v in a['fields'].items() if 'flux' not in n}
        require_match({**b,'fields':{n:b['fields'][n] for n in nonflux}}, {**a,'fields':nonflux})
        m['initial_face_flux_refresh']={n:{'before':v,'after':b['fields'][n]} for n,v in a['fields'].items() if v!=b['fields'][n]}
        if any('flux' not in n for n in m['initial_face_flux_refresh']):
            raise RuntimeError('Reopen changed non-flux scientific evidence')
        after=reopened
        pair=save(s,f'prepared-mapped-stable-A-N{native_iteration(s)}-transfer-{m["transfer_attempts"]}')
        m['prepared_pair']=pair
        dump(OUT/'run-manifest.json',m)
        s.settings.file.read_case(file_name=pair['case'])
        s.settings.file.read_data(file_name=pair['data'])
        reopened=base.state(s)
        require_match(reopened['readback'],after['readback'])
    if reopened['setup'] != after['setup'] or reopened['methods'] != after['methods']:
        raise RuntimeError('Transferred setup differs after reopen')
    clock = dict(s.rp_vars('wall-film/solution-state'))
    if clock['film_elapsed_time'] != 0:
        raise RuntimeError('Prepared film clock is not zero')
    s.settings.mesh.check()
    s.settings.mesh.size_info()
    s.settings.parallel.show_connectivity(compute_node=0)
    time.sleep(1)
    s.transcript.stop()
    dump(OUT / 'prepared-reopen.json', {'state':reopened,'pair':pair,'film_solution_state':clock})
    m.update(status='PREPARED_VERIFIED', prepared_pair=pair, prepared_reopen='PASS', verified_native_end=native_iteration(s),
             mapped_bulk_liquid_mass_kg=reopened['readback']['fields']['v2-total-liquid-mass'][0])
    m.pop('error', None)
    dump(OUT / 'run-manifest.json', m)
    print('PREPARED_NATIVE_TRANSFER_VERIFIED', m['native_start'], m['mapped_bulk_liquid_mass_kg'], flush=True)


def share(s, pair, label):
    folder = SHARED / label
    ensure_remote_directory(s, str(folder))
    for kind, ext in [('case', 'cas.h5'), ('data', 'dat.h5')]:
        target = str(folder / f'{label}.{ext}')
        if remote_file_exists(s, target):
            raise FileExistsError(target)
        base.powershell(s, f"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath '{pair[kind]}' -Destination '{target}'")
        if remote_file_sha256(s, target, str(WORK / 'scratch' / f'{label}-{kind}-shared.sha256.txt')) != pair[kind + '_sha256']:
            raise RuntimeError('Shared pair bytes differ')
    return str(folder)


def checkpoint(s, m, label, target):
    pair = save(s, f'{label}-N{target}')
    current = base.state(s)
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(readback(s), current['readback'])
    clock = dict(s.rp_vars('wall-film/solution-state'))
    if not math.isclose(clock['film_elapsed_time'], (target - m['native_start']) * 1e-6, abs_tol=1e-12):
        raise RuntimeError('Fixed film clock does not match carrier updates')
    dump(OUT / f'endpoint-N{target}.json', {'state':base.state(s), 'pair':pair,'film_solution_state':clock})
    fields = current['readback']['fields']
    if not all(math.isfinite(v[0]) for v in fields.values()) or fields['p72a-e2.7-ewf-thickness-max'][0] > .003:
        raise RuntimeError('Reference recovery limit exceeded; paired endpoint saved')
    h = base.collect(s, m['report_paths'], f'checkpoint-N{target}')
    required = set(range(m['native_start'] + 1, target + 1))
    if any(not required.issubset(v['iterations']) for v in h.values()):
        raise RuntimeError('Native report coverage has gaps')
    vals = lambda name: dict(zip(h[name]['iterations'],h[name]['values']))
    mass, drain, acc = [vals(k) for k in ['p72a-e2.7-ewf-film-mass-total','p72a-e2.7-ewf-outflow-mass-total','p72a-e2.7-ewf-secondary-phase-mass-total']]
    integrated = sum(acc[i]*1e-6 for i in sorted(required))
    initial_fields = json.loads((OUT/'prepared-reopen.json').read_text())['state']['readback']['fields']
    initial_mass = initial_fields['p72a-e2.7-ewf-film-mass-total'][0]
    initial_drain = initial_fields['p72a-e2.7-ewf-outflow-mass-total'][0]
    ledger = 100 * abs(mass[target]-initial_mass+drain[target]-initial_drain-integrated)/max(abs(integrated),1e-30)
    if max(vals('p72a-e2.7-ewf-courant-max')[i] for i in required)>1 or max(vals('p72a-e2.7-ewf-thickness-max')[i] for i in required)>.003 or ledger>1:
        raise RuntimeError('Reference film history limit exceeded; paired endpoint saved')
    return {'pair':pair,'film_ledger_error_percent':ledger,'fields':fields}


def smoke(s):
    m = json.loads((OUT/'run-manifest.json').read_text())
    if m['status']!='PREPARED_VERIFIED' or m['blocks']:
        raise RuntimeError('Smoke requires the verified unrun transferred case')
    expected = json.loads((OUT/'prepared-reopen.json').read_text())['state']
    require_match(readback(s),expected['readback'])
    if native_iteration(s)!=m['native_start']:
        raise RuntimeError('Prepared coordinate changed; refusing duplicate solve')
    m['shared_prepared_pair'] = share(s,m['prepared_pair'],f'prepared-A-N{m["native_start"]}')
    dump(OUT/'run-manifest.json',m)
    start=time.monotonic()
    s.transcript.start(file_name=str(OUT/'smoke-transcript.txt'),write_to_stdout=False)
    feed=base.loading(s,.25)
    target=m['native_start']+20
    m.update(status='SMOKE_RUNNING',active_target=target,command='/solve/iterate 20',started_utc=datetime.now(timezone.utc).isoformat())
    dump(OUT/'run-manifest.json',m)
    base.iterate(s,20)
    proof=checkpoint(s,m,'low-hold-smoke',target)
    s.transcript.stop()
    m['blocks'].append({'stage':'low-hold-smoke','native_start':m['native_start'],'native_end':target,'feed':feed,**proof})
    m.update(status='SMOKE_VERIFIED',verified_native_end=target,smoke_wall_seconds=time.monotonic()-start)
    dump(OUT/'run-manifest.json',m)
    print('SMOKE_VERIFIED',target,m['smoke_wall_seconds'],flush=True)


def prepare_resume(s):
    m=json.loads((OUT/'run-manifest.json').read_text())
    paused=m['status'].startswith('PAUSED') or (m['status']=='RECOVERY_REQUIRED' and m.get('pause_native_iteration_api_verified')==3550)
    if not paused or not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Resume preparation requires the user-paused idle session')
    intent=json.loads((OUT/'pause-save-intent.json').read_text())
    resume_tag=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    n=m['pause_native_iteration_api_verified']
    if native_iteration(s)!=n:
        raise RuntimeError('Live pause coordinate changed; reconcile before loading data')
    for key,obj in [('setup',s.settings.setup),('methods',s.settings.solution.methods),('controls',s.settings.solution.controls)]:
        if obj.get_state()!=intent['before'][key]:
            raise RuntimeError('Pause setup invariant differs: '+key)
    pair=intent['pair']
    for kind in ['case','data']:
        if not remote_file_exists(s,pair[kind]):
            raise FileNotFoundError(pair[kind])
        pair[kind+'_sha256']=remote_file_sha256(s,pair[kind],str(WORK/'scratch'/f'resume-parent-{resume_tag}-{kind}.sha256.txt'))
    # The interrupted pause/reopen left a case-only session. Restore the exact
    # native saved pair and validate against the captured pre-save field state.
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    if native_iteration(s)!=n or not s.settings.solution.report_definitions.compute.is_active():
        raise RuntimeError('Saved pause data did not restore the expected field')
    fields={}
    for record in s.settings.solution.report_definitions.compute(report_defs=list(m['report_paths'])):
        fields.update(record)
    diagnostic_cache={'p72a-e2.7-ewf-secondary-phase-collection-awavg','p72a-e2.7-ewf-secondary-phase-mass-total'}
    expected_fields=intent['before']['fields']
    require_match({'fields':{k:v for k,v in fields.items() if k not in diagnostic_cache}},
                  {'fields':{k:v for k,v in expected_fields.items() if k not in diagnostic_cache}})
    resets={k:{'before':expected_fields[k],'after':fields[k]} for k in diagnostic_cache if fields[k]!=expected_fields[k]}
    if any(v['after'][0]!=0 for v in resets.values()):
        raise RuntimeError('Unexpected EWF diagnostic change on pause-data reopen')
    m['pause_reopen_diagnostic_reset']=resets
    clock=dict(s.rp_vars('wall-film/solution-state'))
    if not math.isclose(clock['film_elapsed_time'],(n-m['native_start'])*1e-6,abs_tol=1e-12):
        raise RuntimeError('Pause data film clock changed')
    fraction=.25+.75*(n-m['native_start']-500-10)/2000
    actual_feed={}
    for zone,phase,rate,key in [('liquidinlet','phase-2',116.92,'liquid_kg_s'),('steaminlet','phase-1',80.69,'vapor_kg_s')]:
        value=s.settings.setup.boundary_conditions.mass_flow_inlet[zone].phase[phase].momentum.mass_flow_rate.get_state()['value']
        if not math.isclose(value,rate*fraction,rel_tol=1e-10):
            raise RuntimeError('Paused ramp command differs: '+zone)
        actual_feed[key]=value
    actual_feed['multiplier']=fraction
    proof=checkpoint(s,m,'resume-start-'+resume_tag,n)
    if m['verified_native_end']<n:
        if m['verified_native_end']!=n-10 or m['active_target']!=n:
            raise RuntimeError('Cannot reconcile the interrupted ramp block')
        m['blocks'].append({'stage':'ramp','native_start':n-10,'native_end':n,'feed':actual_feed,'pause_reconciled':True})
    m.update(status='RESUME_VERIFIED',verified_native_end=n,resume_pair=proof['pair'],resume_reopen='PASS',
             pause_parent_pair=pair,remaining_updates=m['native_target']-n,resumed_at_utc=datetime.now(timezone.utc).isoformat())
    m.pop('error',None)
    dump(OUT/'resume-preflight.json',{'state':base.state(s),'pair':proof['pair'],'pause_parent_pair':pair,'proof':proof,'feed':actual_feed})
    dump(OUT/'run-manifest.json',m)
    print('RESUME_VERIFIED',n,m['remaining_updates'],flush=True)


def run(s, resume=False):
    m=json.loads((OUT/'run-manifest.json').read_text())
    start_n=m['verified_native_end'] if resume else m['native_start']+20
    required_status='RESUME_VERIFIED' if resume else 'SMOKE_VERIFIED'
    if m['status']!=required_status or native_iteration(s)!=start_n:
        raise RuntimeError('Run requires its verified starting endpoint; refusing duplicate compute')
    expected=json.loads((OUT/f'endpoint-N{start_n}.json').read_text())['state']
    current=base.state(s)
    require_match(current['readback'],expected['readback'])
    if current['setup']!=expected['setup'] or current['methods']!=expected['methods']:
        raise RuntimeError('Verified smoke model changed before long run')
    initial=m['native_start']
    stages=[('low-hold',initial+500,.25)]
    stages += [('ramp',initial+500+r+10,.25+.75*r/2000) for r in range(0,2000,10)]
    stages += [('target-hold',initial+3500,1.)]
    stages=[stage for stage in stages if stage[1]>start_n]
    start=time.monotonic()
    transcript=f'run-transcript-resume-N{start_n}.txt' if resume else 'run-transcript.txt'
    m.setdefault('transcript_files',['smoke-transcript.txt','run-transcript.txt'])
    if transcript not in m['transcript_files']:
        m['transcript_files'].append(transcript)
    dump(OUT/'run-manifest.json',m)
    s.transcript.start(file_name=str(OUT/transcript),write_to_stdout=False)
    for label,target,fraction in stages:
        feed=base.loading(s,fraction)
        n=native_iteration(s)
        m.update(status='RUNNING',active_stage=label,active_target=target,command=f'/solve/iterate {target-n}')
        dump(OUT/'run-manifest.json',m)
        base.iterate(s,target-n)
        record={'stage':label,'native_start':n,'native_end':target,'feed':feed}
        if label!='ramp' or (target-initial-500)%500==0:
            record.update(checkpoint(s,m,label,target))
            print('CHECKPOINT',label,target,record['fields']['v2-total-liquid-mass'][0],flush=True)
        m['blocks'].append(record)
        m['verified_native_end']=target
        dump(OUT/'run-manifest.json',m)
    s.transcript.stop()
    base.collect(s,m['report_paths'],'final')
    pair=m['blocks'][-1]['pair']
    before=base.state(s)
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(readback(s),before['readback'])
    dump(OUT/'final-reopen.json',{'state':base.state(s),'pair':pair,'film_solution_state':dict(s.rp_vars('wall-film/solution-state'))})
    m['shared_final_pair']=share(s,pair,f'final-N{initial+3500}')
    m.update(status='COMPLETE_ANALYSIS_REQUIRED',final_pair=pair,final_reopen='PASS',live_idle=s.settings.solution.run_calculation.iterate.is_active(),
             wall_seconds_scope='Resumed segment plus original smoke only; pause excluded' if resume else 'Original uninterrupted execution',
             resumed_wall_seconds=time.monotonic()-start if resume else None,
             wall_seconds=m['smoke_wall_seconds']+time.monotonic()-start,completed_utc=datetime.now(timezone.utc).isoformat())
    dump(OUT/'run-manifest.json',m)
    print('SLIT_STARTUP_COMPLETE',initial+3500,flush=True)


def verify(_s=None):
    m=json.loads((OUT/'run-manifest.json').read_text())
    h=json.loads((OUT/'final-histories.json').read_text())
    required=set(range(m['native_start']+1,m['native_target']+1))
    if m['verified_native_end']!=m['native_target'] or m.get('final_reopen')!='PASS' or not m.get('final_pair'):
        raise RuntimeError('Final endpoint has not been proved')
    if any(not required.issubset(v['iterations']) for v in h.values()):
        raise RuntimeError('Final reports incomplete')
    print('EXACT_HORIZON_FINAL_PAIR_REPORTS_VERIFIED',m['native_target'],len(h),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['inspect-target', 'map-target', 'transfer', 'recover-transfer', 'remap', 'smoke', 'run', 'prepare-resume', 'resume', 'verify'])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    solver = None if args.operation=='verify' else attach()
    try:
        {'inspect-target': inspect_target, 'map-target': map_target, 'transfer': transfer, 'recover-transfer': recover_transfer,
         'remap':remap,'smoke':smoke,'run':run,'prepare-resume':prepare_resume,
         'resume':lambda s:run(s,resume=True),'verify':verify}[args.operation](solver)
    except Exception:
        path = OUT / 'run-manifest.json'
        if path.exists():
            manifest = json.loads(path.read_text())
            manifest.update(status='RECOVERY_REQUIRED', error=traceback.format_exc())
            dump(path, manifest)
        try:
            solver.transcript.stop()
        except Exception:
            pass
        raise
