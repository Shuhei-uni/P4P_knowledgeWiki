"""Server-local Phase 10 fresh-start carrier series; credentials are env-only.

Native mesh transfer and strict settings/reopen checks precede every solve.
Use --prepare-only to build and smoke-test M01 before dispatching the batch.
"""
from __future__ import annotations
import argparse
import functools
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import sys
import threading
import time

if os.environ.get('PHASE10_EXTRA_PACKAGES'):
    sys.path.insert(0, os.environ['PHASE10_EXTRA_PACKAGES'])
import h5py
import numpy as np
import ansys.fluent.core as pf
from execution_contract import native_transcript, require_state_same


def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, default=str))
    temporary.replace(path)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def counts(path):
    with h5py.File(path, 'r') as f:
        mesh = f['meshes/1']
        return {k: int(mesh.attrs[attr][0]) for k, attr in
                [('cells', 'cellCount'), ('nodes', 'nodeCount')]}


def verify_solver_mesh(source, saved):
    """Allow removal of unused file vertices only after exact geometry proof.

    Compare all face polygons using canonical coordinate ranks, independently
    of partition/node/face numbering. Raw mesh files are never changed.
    """
    def read(path):
        with h5py.File(path, 'r') as f:
            mesh = f['meshes/1']
            xyz = np.concatenate([mesh['nodes/coords'][k][:]
                                  for k in sorted(mesh['nodes/coords'], key=int)])
            groups = mesh['faces/nodes']
            nn = np.concatenate([groups[k]['nnodes'][:]
                                 for k in sorted(groups, key=int)]).astype(np.int64)
            ids = np.concatenate([groups[k]['nodes'][:]
                                  for k in sorted(groups, key=int)]).astype(np.int64)
            return counts(path), int(mesh.attrs['faceCount'][0]), xyz, nn, ids

    sc, sf, xyz, nn, ids = read(source)
    tc, tf, txyz, tnn, tids = read(saved)
    assert sc['cells'] == tc['cells'] and sf == tf, 'Cell or face count changed'
    assert len(nn) == sf and len(tnn) == tf
    assert int(nn.sum()) == len(ids) and int(tnn.sum()) == len(tids)
    used = np.unique(ids) - 1
    target_used = np.unique(tids) - 1
    assert used.min() >= 0 and used.max() < len(xyz)
    assert target_used.min() >= 0 and target_used.max() < len(txyz)
    assert len(target_used) == tc['nodes'] == len(used), 'Referenced vertex count changed'
    active = xyz[used]
    order = np.lexsort((active[:, 2], active[:, 1], active[:, 0]))
    torder = np.lexsort((txyz[:, 2], txyz[:, 1], txyz[:, 0]))
    sorted_xyz = active[order]
    assert np.array_equal(sorted_xyz, txyz[torder]), 'Active coordinates changed'
    # Coincident coordinates share a rank; comparison is of face geometry.
    distinct = np.r_[True, np.any(sorted_xyz[1:] != sorted_xyz[:-1], axis=1)]
    ranks = np.cumsum(distinct) - 1
    source_rank = np.full(len(xyz), -1, dtype=np.int64)
    source_rank[used[order]] = ranks
    target_rank = np.empty(len(txyz), dtype=np.int64)
    target_rank[torder] = ranks

    def signature(lengths, vertices, rank):
        starts = np.r_[0, np.cumsum(lengths[:-1])]
        digest = hashlib.sha256()
        for n in np.unique(lengths):
            assert n >= 3
            selected = starts[lengths == n]
            matrix = rank[vertices[selected[:, None] + np.arange(n)] - 1]
            matrix.sort(axis=1)
            order = np.lexsort(tuple(matrix[:, j] for j in range(int(n)-1, -1, -1)))
            digest.update(np.asarray([n, len(selected)], dtype='<i8').tobytes())
            digest.update(np.asarray(matrix[order], dtype='<i8').tobytes())
        return digest.hexdigest()

    face_sha = signature(nn, ids, source_rank)
    assert face_sha == signature(tnn, tids, target_rank), 'Face polygon geometry changed'
    return {'status': 'PASS', 'input_counts': sc, 'solver_counts': tc,
            'faces': sf, 'input_unused_vertices': sc['nodes'] - len(used),
            'active_coordinate_sha256': hashlib.sha256(sorted_xyz.tobytes()).hexdigest(),
            'face_geometry_sha256': face_sha,
            'normalization': 'Removed only vertices unused by every face'}


def state(s):
    setup = s.settings.setup.get_state()
    fluid = setup['cell_zone_conditions']['fluid']
    assert list(fluid) == ['fluid']
    walls = setup['boundary_conditions']['wall']
    canonical_wall = dict(walls['wall']); canonical_wall.pop('name', None)
    for name, wall in walls.items():
        normalized = dict(wall); normalized.pop('name', None)
        if name != 'bottom':
            assert normalized == canonical_wall, 'Wall condition differs: ' + name
    return {
        'solver': setup['general']['solver'],
        'operating': setup['general']['operating_conditions'],
        'models': setup['models'], 'materials': setup['materials'],
        'fluid': fluid['fluid'],
        'inlet': setup['boundary_conditions']['mass_flow_inlet'],
        'outlet': setup['boundary_conditions']['pressure_outlet'],
        'wall': canonical_wall, 'bottom': walls['bottom'],
        'methods': s.settings.solution.methods.get_state(),
        'controls': s.settings.solution.controls.get_state(),
        'residual_equations': s.settings.solution.monitor.residual.equations.get_state(),
        'injections': s.settings.setup.models.discrete_phase.injections.get_object_names(),
    }


def save_pair(s, base):
    files = {kind: str(base) + ext for kind, ext in
             [('case', '.cas.h5'), ('data', '.dat.h5')]}
    assert not any(Path(p).exists() for p in files.values()), 'Existing checkpoint'
    s.settings.file.write_case(file_name=files['case'])
    s.settings.file.write_data(file_name=files['data'])
    for kind in ['case', 'data']:
        assert Path(files[kind]).is_file()
        files[kind + '_sha256'] = sha(files[kind])
    files['counts'] = counts(files['case'])
    return files


def reopen(s, pair):
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])


def reports(s, folder):
    defs = s.settings.solution.report_definitions
    names = []
    specifications = []
    for phase in ['mixture', 'phase-1', 'phase-2']:
        for boundary in ['inlet', 'steamoutlet']:
            name = 'p10-flux-' + phase + '-' + boundary
            defs.flux.create(name=name); report = defs.flux[name]
            report.report_type = 'flux-massflow'
            report.phase = phase; report.boundaries = [boundary]
            report.per_selection = False
            specifications.append((name, 'flux', 'kg/s'))
    for phase in ['phase-1', 'phase-2']:
        name = 'p10-mass-' + phase
        defs.volume.create(name=name); report = defs.volume[name]
        report.report_type = 'volume-mass'
        report.phase = phase; report.cell_zones = ['fluid']
        specifications.append((name, 'volume', 'kg'))
    for field, kind, label, unit in [
        ('velocity-magnitude', 'volume-average', 'speed-mean', 'm/s'),
        ('velocity-magnitude', 'volume-max', 'speed-max', 'm/s'),
        ('vorticity-mag', 'volume-average', 'vorticity-mean', '1/s')]:
        name = 'p10-' + label
        defs.volume.create(name=name); report = defs.volume[name]
        report.report_type = kind; report.field = field
        report.cell_zones = ['fluid']
        specifications.append((name, 'volume', unit))
    for boundary in ['inlet', 'steamoutlet']:
        for field, label, unit in [('pressure', 'pressure', 'Pa'),
                                   ('velocity-magnitude', 'speed', 'm/s')]:
            name = 'p10-' + label + '-' + boundary
            defs.surface.create(name=name); report = defs.surface[name]
            report.report_type = 'surface-areaavg'
            report.field = field; report.surface_names = [boundary]
            report.per_surface = False
            specifications.append((name, 'surface', unit))
    name = 'p10-iteration'
    defs.single_valued_expression.create(name=name)
    defs.single_valued_expression[name].definition = 'Iteration'
    specifications.append((name, 'single_valued_expression', 'iteration'))
    files = s.settings.solution.monitor.report_files
    old = files.get_object_names()
    if old: files.delete(name_list=old)
    paths = {}
    for name, branch, unit in specifications:
        report = getattr(defs, branch)[name]
        report.create_report_file = False; report.create_report_plot = False
        if 'average_over' in report.child_names: report.average_over = 1
        filename = str(folder / (name + '.out'))
        assert not Path(filename).exists()
        files.create(name=name + '-rfile')
        files[name + '-rfile'].set_state({'file_name': filename,
            'report_defs': [name], 'frequency': 10, 'active': True})
        assert files[name + '-rfile'].get_state()['report_defs'] == [name]
        names.append(name); paths[name] = {'file': filename, 'unit': unit}
    return names, paths


def iteration(s):
    raw = s.settings.solution.report_definitions.compute(report_defs=['p10-iteration'])
    return int(round(float(raw[0]['p10-iteration'][0])))


def compute(s, names):
    value = s.settings.solution.report_definitions.compute(report_defs=names)
    def finite(x):
        if isinstance(x, dict):
            for v in x.values(): finite(v)
        elif isinstance(x, (list, tuple)):
            for v in x: finite(v)
        elif isinstance(x, (int, float)):
            assert math.isfinite(x), 'Non-finite report value'
    finite(value)
    return value


def verify_histories(receipt, horizon):
    proof = {}
    for name, info in receipt['report_paths'].items():
        path = Path(info['file'])
        assert path.is_file() and path.stat().st_size > 0, 'Missing history: ' + name
        rows = []
        for line in path.read_text().splitlines():
            try: values = [float(x) for x in line.split()]
            except ValueError: continue
            if len(values) >= 2:
                assert all(math.isfinite(v) for v in values)
                rows.append(values)
        assert rows and rows[-1][0] >= horizon - 10, 'Incomplete history: ' + name
        assert all(a[0] < b[0] for a, b in zip(rows, rows[1:])), 'Repeated or reversed history: ' + name
        late = [r[1] for r in rows if r[0] >= horizon - 500]
        assert len(late) >= 50, 'Missing comparison window: ' + name
        mean = sum(late) / len(late)
        proof[name] = {'first_iteration': rows[0][0], 'last_iteration': rows[-1][0],
            'samples': len(rows), 'final_500_mean': mean,
            'final_500_range': max(late) - min(late),
            'final_500_relative_range': (max(late)-min(late))/abs(mean) if abs(mean)>1e-12 else None}
    return proof


def prepare(s, cfg, row, expected):
    root = Path(cfg['work']) / row['level']
    root.mkdir(parents=True, exist_ok=False)
    receipt = {'status': 'BUILDING', 'level': row['level'], 'mesh': row,
               'expected_iterations': cfg['iterations'], 'checkpoints': []}
    dump(root / 'manifest.json', receipt)
    with native_transcript(s.settings.file, root / 'build.trn'):
        assert sha(row['mesh']).lower() == row['sha256'].lower()
        assert counts(row['mesh']) == {'cells': row['cells'], 'nodes': row['nodes']}
        s.settings.file.read_mesh(file_name=row['mesh'])
        fluid = s.settings.setup.cell_zone_conditions.fluid.get_object_names()
        assert len(fluid) == 1
        if fluid[0] != 'fluid':
            s.settings.mesh.modify_zones.zone_name(zone_name=fluid[0], new_name='fluid')
        interiors = s.settings.setup.boundary_conditions.interior.get_object_names()
        assert len(interiors) == 1
        if interiors[0] != 'interior-fluid':
            s.settings.mesh.modify_zones.zone_name(zone_name=interiors[0], new_name='interior-fluid')
        types = s.settings.setup.boundary_conditions
        if 'inlet' not in types.mass_flow_inlet.get_object_names():
            s.settings.mesh.modify_zones.zone_type(zone_names=['inlet'], new_type='mass-flow-inlet')
        assert types.pressure_outlet.get_object_names() == ['steamoutlet']
        wall_names = types.wall.get_object_names()
        assert 'bottom' in wall_names and 'wall' in wall_names
        legacy = str(root / 'replacement.cas')
        cff = s.settings.file.cff_files.get_state()
        s.settings.file.cff_files = False
        try: s.settings.file.write_case(file_name=legacy)
        finally: s.settings.file.cff_files = cff
        s.settings.file.read_case(file_name=cfg['common_case'])
        require_state_same(state(s), expected)
        s.scheme.eval("(rpsetvar 'dynamesh/replace-mesh/partition-per-zone? #t)")
        s.settings.mesh.replace(file_name=legacy, zones=False)
        source_wall = dict(expected['wall'])
        for name in s.settings.setup.boundary_conditions.wall.get_object_names():
            if name not in ['bottom', 'wall']:
                s.settings.setup.boundary_conditions.wall[name].set_state(dict(source_wall, name=name))
        require_state_same(state(s), expected)
        s.settings.mesh.check()
        s.settings.mesh.size_info()
        (root / 'monitors').mkdir()
        names, paths = reports(s, root / 'monitors')
        s.settings.solution.monitor.residual.options.n_save = cfg['iterations'] + 100
        s.settings.solution.monitor.residual.options.n_display = cfg['iterations'] + 100
        s.settings.file.auto_save.data_frequency = 0
        s.settings.solution.initialization.hybrid_initialize()
        receipt['initial_reports'] = compute(s, names)
        # Fluent can report Iteration=1 immediately after Hybrid, before any
        # carrier update. The saved/reopened fresh pair reports the actual N0.
        receipt['pre_save_iteration_expression'] = iteration(s)
        assert receipt['pre_save_iteration_expression'] in (0, 1)
        receipt['report_names'] = names; receipt['report_paths'] = paths
        receipt['start_pair'] = save_pair(s, root / 'prepared-N0')
        receipt['solver_mesh_proof'] = verify_solver_mesh(row['mesh'], receipt['start_pair']['case'])
        reopen(s, receipt['start_pair'])
        require_state_same(state(s), expected)
        receipt['reopen_reports'] = compute(s, names)
        assert iteration(s) == 0
        receipt['start_iteration'] = 0
        receipt['settings_readback'] = state(s)
        receipt['status'] = 'PREPARED_REOPENED'
        receipt['wall_names'] = wall_names
        dump(root / 'manifest.json', receipt)
    return root, receipt



class NativeNumericalFailure(RuntimeError):
    """Native transcript proves numerical failure, even if reports stay finite."""


def native_numerical_error(path):
    with Path(path).open('rb') as stream:
        stream.seek(0, 2)
        size = stream.tell()
        stream.seek(max(0, size - 65536))
        tail = stream.read().decode(errors='replace')
    if 'floating point exception' in tail.lower():
        return 'Native floating point exception'
    return None


def validate_reconciliation(root, cfg, proof):
    assert proof['status'] == 'RECONCILED_NUMERICAL_FAILURE'
    assert proof['workers'] == []
    assert sha(root / 'batch-manifest.json') == proof['batch_manifest_sha256']
    assert json.loads((root / 'batch-manifest.json').read_text())['status'] == 'STOPPED_REQUIRES_REVIEW'
    excluded = proof['excluded_levels']
    assert excluded and len(set(excluded)) == len(excluded)
    assert set(excluded).issubset({row['level'] for row in cfg['meshes']})
    assert set(excluded) == {row['level'] for row in proof['failed_levels']}
    for level in excluded:
        path = root / level / 'manifest.json'
        assert sha(path) == proof['level_manifest_sha256'][level]
        assert json.loads(path.read_text())['status'] in (
            'STOPPED_REQUIRES_REVIEW', 'NUMERICAL_FAILURE_UNQUALIFIED')
    spent = sum(row['actual_iterations'] for row in proof['failed_levels'])
    additional = len(cfg['meshes']) - len(excluded)
    lost_updates_cap = proof.get('lost_updates_cap', 0)
    assert isinstance(lost_updates_cap, int) and lost_updates_cap >= 0
    assert spent + lost_updates_cap + additional * cfg['iterations'] <= 35000


def run(s, cfg, row, expected, prepare_only=False):
    root = Path(cfg['work']) / row['level']
    manifest = root / 'manifest.json'
    if manifest.exists():
        receipt = json.loads(manifest.read_text())
        assert receipt['status'] == 'SMOKE_VERIFIED', 'Existing level needs reconciliation'
        reopen(s, receipt['smoke_pair'])
        require_state_same(state(s), expected)
    else:
        root, receipt = prepare(s, cfg, row, expected)
    n = iteration(s)
    if n == 0:
        with native_transcript(s.settings.file, root / 'smoke.trn'):
            begin = time.perf_counter()
            s.settings.solution.run_calculation.iterate(iter_count=5)
            elapsed = time.perf_counter() - begin
        assert iteration(s) == 5, 'Smoke horizon incomplete'
        receipt['smoke_reports'] = compute(s, receipt['report_names'])
        receipt['smoke_seconds'] = elapsed
        receipt['smoke_pair'] = save_pair(s, root / 'smoke-N5')
        reopen(s, receipt['smoke_pair'])
        require_state_same(state(s), expected)
        assert iteration(s) == 5
        receipt['status'] = 'SMOKE_VERIFIED'; receipt['completed_iterations'] = 5
        dump(manifest, receipt)
    if prepare_only: return receipt
    try:
        receipt['status'] = 'RUNNING'; dump(manifest, receipt)
        for target in range(1000, cfg['iterations'] + 1, 1000):
            start = iteration(s)
            assert start < target
            with native_transcript(s.settings.file, root / ('solve-to-N%d.trn' % target)):
                begin = time.perf_counter()
                s.settings.solution.run_calculation.iterate(iter_count=target - start)
                elapsed = time.perf_counter() - begin
            actual = iteration(s)
            failure = native_numerical_error(root / ('solve-to-N%d.trn' % target))
            if failure:
                receipt['actual_failed_iteration'] = actual
                receipt['failed_block_solver_seconds'] = elapsed
                receipt['native_failure_transcript'] = str(root / ('solve-to-N%d.trn' % target))
                dump(manifest, receipt)
                raise NativeNumericalFailure(failure)
            values = compute(s, receipt['report_names'])
            endpoint = save_pair(s, root / ('checkpoint-N%d' % actual))
            receipt['checkpoints'].append({'requested_iteration': target, 'iteration': actual,
                'solver_seconds': elapsed, 'pair': endpoint, 'reports': values})
            receipt['completed_iterations'] = actual; dump(manifest, receipt)
            if actual != target:
                receipt['status'] = 'EARLY_STOP_REQUIRES_REVIEW'; dump(manifest, receipt)
                raise RuntimeError('Native run stopped before the requested horizon')
        receipt['status'] = 'COMPLETE_EXECUTION_UNQUALIFIED'
        receipt['solver_seconds'] = receipt['smoke_seconds'] + sum(
            c['solver_seconds'] for c in receipt['checkpoints'])
        receipt['final_pair'] = receipt['checkpoints'][-1]['pair']
        require_state_same(state(s), expected)
        receipt['history_verification'] = verify_histories(receipt, cfg['iterations'])
        dump(manifest, receipt)
        return receipt
    except BaseException as exc:
        receipt['status'] = 'STOPPED_REQUIRES_REVIEW'
        receipt['error'] = str(exc)
        dump(manifest, receipt)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--continue-reconciled', action='store_true')
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text())
    root = Path(cfg['work'])
    manifest = root / 'batch-manifest.json'
    reconciliation = None
    if args.continue_reconciled:
        assert not args.prepare_only
        reconciliation = json.loads(Path(cfg['reconciliation']).read_text())
        validate_reconciliation(root, cfg, reconciliation)
        archive = root / reconciliation['archive_directory']
        archive.mkdir(exist_ok=False)
        (archive / 'batch-manifest.json').write_bytes(manifest.read_bytes())
        for level in reconciliation['excluded_levels']:
            (archive / (level + '-manifest.json')).write_bytes(
                (root / level / 'manifest.json').read_bytes())
    elif not args.prepare_only and manifest.exists():
        raise RuntimeError('Existing batch needs process and endpoint reconciliation')
    # Reuse the version-matched 2025 R2 service selection proven by the existing
    # Stage 2 controller on this host. PyFluent 0.42 otherwise probes v1 services.
    import ansys.fluent.core._grpc_services as low
    import ansys.fluent.core.services as high
    from ansys.fluent.core.utils.fluent_version import FluentVersion
    low._server_supports_v1 = lambda channel: False
    high.create_service_factory = functools.partial(
        high.create_service_factory, product_version=FluentVersion.v252)
    pf.config.check_health = False
    connected = queue.Queue()
    def attach():
        try:
            connected.put(pf.connect_to_fluent(
                ip=cfg['ip'], port=int(os.environ['PHASE10_API_PORT']),
                password=os.environ['PHASE10_API_PASSWORD'], allow_remote_host=True,
                insecure_mode=True, cleanup_on_exit=False, start_watchdog=False,
                start_transcript=False))
        except BaseException as exc:
            connected.put(exc)
    print('CONNECTING', flush=True)
    threading.Thread(target=attach, daemon=True).start()
    try:
        s = connected.get(timeout=60)
    except queue.Empty:
        dump(root / ('startup-timeout-%d.json' % os.getpid()), {
            'status': 'CONNECTION_TIMEOUT_BEFORE_BUILD', 'controller_pid': os.getpid(),
            'port': int(os.environ['PHASE10_API_PORT']), 'solve_iterations': 0})
        print('CONNECTION_TIMEOUT_BEFORE_BUILD', flush=True)
        os._exit(2)
    if isinstance(s, BaseException):
        raise s
    s.events.stop()
    expected = json.loads((root / 'common-settings.json').read_text())
    batch = {'status': 'PREPARING' if args.prepare_only else 'RUNNING',
        'controller_pid': os.getpid(), 'started': datetime.now(timezone.utc).isoformat(),
        'common_case_sha256': cfg['common_case_sha256'], 'iterations_per_mesh': cfg['iterations'],
        'levels': [], 'phase': 'phase-10-single-inlet-mesh-convergence'}
    if reconciliation:
        batch['reconciliation'] = cfg['reconciliation']
        batch['failed_levels'] = reconciliation['failed_levels']
        batch['prior_lost_updates_cap'] = reconciliation.get('lost_updates_cap', 0)
        batch['technical_recovery'] = reconciliation.get('technical_recovery')
    assert sha(cfg['common_case']).lower() == cfg['common_case_sha256'].lower()
    if not args.prepare_only: dump(manifest, batch)
    try:
        for row in cfg['meshes'][:1] if args.prepare_only else cfg['meshes']:
            if reconciliation and row['level'] in reconciliation['excluded_levels']:
                continue
            batch['current_level'] = row['level']
            if not args.prepare_only: dump(manifest, batch)
            try:
                result = run(s, cfg, row, expected, args.prepare_only)
            except BaseException as exc:
                # Only a demonstrated numerical failure may skip a mesh. Build,
                # settings, artifact and connection errors still stop the batch.
                level_path = root / row['level'] / 'manifest.json'
                failed = json.loads(level_path.read_text()) if level_path.exists() else {}
                numerical = ((isinstance(exc, NativeNumericalFailure)
                              or str(exc) == 'Non-finite report value')
                             and (failed.get('checkpoints') or failed.get('smoke_pair')))
                if not numerical or args.prepare_only:
                    raise
                actual = iteration(s)
                failed['actual_failed_iteration'] = actual
                failed['failure_reports'] = s.settings.solution.report_definitions.compute(
                    report_defs=failed['report_names'])
                failed['status'] = 'NUMERICAL_FAILURE_UNQUALIFIED'
                dump(level_path, failed)
                batch.setdefault('failed_levels', []).append({
                    'level': row['level'], 'status': failed['status'],
                    'actual_iterations': actual,
                    'last_saved_iteration': failed['completed_iterations'],
                    'error': str(exc),
                    'manifest': str(level_path)})
                dump(manifest, batch)
                continue
            batch['levels'].append({'level': row['level'], 'status': result['status'],
                                    'manifest': str(root / row['level'] / 'manifest.json')})
            if not args.prepare_only: dump(manifest, batch)
        batch['status'] = ('SMOKE_VERIFIED' if args.prepare_only else
                           'COMPLETE_SERIES_WITH_FAILED_LEVELS' if batch.get('failed_levels') else
                           'COMPLETE_EXECUTION_UNQUALIFIED')
    except BaseException as exc:
        batch['status'] = 'STOPPED_REQUIRES_REVIEW'
        batch['error'] = type(exc).__name__ + ': ' + str(exc)
        raise
    finally:
        dump(root / ('pilot-manifest.json' if args.prepare_only else 'batch-manifest.json'), batch)


if __name__ == '__main__':
    main()
