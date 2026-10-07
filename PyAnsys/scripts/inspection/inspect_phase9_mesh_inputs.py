"""Read-only audit of the five supplied Phase 9 Fluent CFF meshes."""
from pathlib import Path
import argparse
import hashlib
import json

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
LABELS = ['60k', '342k', '680k', '997k', '2_6M']


def topology(group):
    names = group['name'][0].decode().split(';')
    return [dict(name=name, **{key: int(group[key][i]) for key in
            ['id', 'minId', 'maxId', 'zoneType', 'c0', 'c1'] if key in group})
            for i, name in enumerate(names)]


def audit(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    with h5py.File(path, 'r') as source:
        mesh = source['meshes/1']
        cell_zones = topology(mesh['cells/zoneTopology'])
        face_zones = topology(mesh['faces/zoneTopology'])
        coordinate_groups = mesh['nodes/coords']
        node_count = max(int(d.attrs['maxId'][0]) for d in coordinate_groups.values())
        xyz = np.empty((node_count + 1, 3))
        xyz[0] = np.nan
        for data in coordinate_groups.values():
            xyz[int(data.attrs['minId'][0]):int(data.attrs['maxId'][0]) + 1] = data[()]
        boundary_volume = 0.0
        for zone in face_zones:
            zone['face_count'] = zone['maxId'] - zone['minId'] + 1
            if zone['zoneType'] == 2 and zone.get('c0') == zone.get('c1'):
                continue
            blocks = []
            for key, adjacent in mesh['faces/c0'].items():
                lo, hi = int(adjacent.attrs['minId'][0]), int(adjacent.attrs['maxId'][0])
                if lo <= zone['minId'] and hi >= zone['maxId']:
                    blocks.append(key)
            if len(blocks) != 1:
                raise RuntimeError(f'Boundary block mapping unresolved: {zone["name"]}')
            nodes = mesh['faces/nodes'][blocks[0]]
            all_sizes = nodes['nnodes'][()].astype(np.int64)
            block_start = int(mesh['faces/c0'][blocks[0]].attrs['minId'][0])
            first, last = zone['minId'] - block_start, zone['maxId'] - block_start + 1
            sizes = all_sizes[first:last]
            offset, end = int(all_sizes[:first].sum()), int(all_sizes[:last].sum())
            ids = nodes['nodes'][offset:end].astype(np.int64)
            starts = np.r_[0, np.cumsum(sizes)[:-1]]
            next_index = np.arange(len(ids)) + 1
            next_index[np.cumsum(sizes) - 1] = starts
            points = xyz[ids]
            crosses = np.cross(points, points[next_index])
            area_vectors = np.add.reduceat(crosses, starts) / 2
            zone['area_coordinate_units_squared'] = float(np.linalg.norm(area_vectors, axis=1).sum())
            zone['bounds'] = [points.min(axis=0).tolist(), points.max(axis=0).tolist()]
            zone['enclosed_volume_contribution'] = float(np.einsum('ij,ij->i', xyz[ids[starts]], area_vectors).sum() / 3)
            if not zone.get('c1', 0):
                boundary_volume += zone['enclosed_volume_contribution']
        cell_types = np.concatenate([d['cell-types'][()] for d in mesh['cells/ctype'].values()
                                     if isinstance(d, h5py.Group) and 'cell-types' in d]) if any(
            isinstance(d, h5py.Group) and 'cell-types' in d for d in mesh['cells/ctype'].values()) else np.array([], dtype=int)
        types, counts = np.unique(cell_types, return_counts=True)
        return {'file': str(path), 'bytes': path.stat().st_size, 'sha256': digest.hexdigest(),
                'cells': sum(z['maxId'] - z['minId'] + 1 for z in cell_zones),
                'nodes': node_count, 'faces': sum(z['face_count'] for z in face_zones),
                'bounds': [xyz[1:].min(axis=0).tolist(), xyz[1:].max(axis=0).tolist()],
                'boundary_enclosed_volume_coordinate_units_cubed': abs(boundary_volume),
                'cell_type_counts': dict(zip(map(str, types), map(int, counts))),
                'cell_zones': cell_zones, 'face_zones': face_zones,
                'native_scale_and_quality': 'PENDING_FLUENT_CHECK'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh-folder', type=Path)
    parser.add_argument('--single-mesh', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.single_mesh:
        args.output.write_text(json.dumps(audit(args.single_mesh), indent=2) + '\n')
        return
    if not args.mesh_folder:
        parser.error('--mesh-folder or --single-mesh is required')
    records = []
    for label in LABELS:
        result = audit(args.mesh_folder / f'Separator-purnanto-{label}.msh.h5')
        result['label'] = label
        records.append(result)
        print(label, result['cells'], result['nodes'], result['bounds'],
              result['boundary_enclosed_volume_coordinate_units_cubed'], flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'status': 'INPUT_AUDIT_COMPLETE_NATIVE_CHECK_PENDING',
        'coordinate_units': 'File coordinates; physical scale must be confirmed in Fluent',
        'meshes': records}, indent=2) + '\n')


if __name__ == '__main__':
    main()
