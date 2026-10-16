"""Prepare spatial EWF profiles from immutable Fluent HDF5 artifacts.

No Fluent connection or case/data modification. Mapping is nearest compatible
face within the same named wall, with target-tangent velocity projection. Outputs remain
unverified initialisation candidates until a native Fluent round trip passes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np
from scipy.spatial import cKDTree


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def face_fields(path):
    result = {}
    with h5py.File(path, 'r') as f:
        group = f['results/1/phase-1/faces']
        for field in ['HEIGHT', 'U', 'V', 'W']:
            chunks = []
            for ds in group['SV_EFILM_' + field].values():
                lo, hi = int(ds.attrs['minId'][0]), int(ds.attrs['maxId'][0])
                a = np.asarray(ds[:], dtype=float)
                assert a.shape == (hi - lo + 1,) and np.isfinite(a).all()
                chunks.append((lo, hi, a))
            result[field] = chunks
    return result


def geometry(path, names):
    result = {}
    with h5py.File(path, 'r') as f:
        mesh = f['meshes/1']
        zones = mesh['faces/zoneTopology']
        zone_names = zones['name'][0].decode().rstrip(';').split(';')
        coordinates = {}
        for ds in mesh['nodes/coords'].values():
            coordinates[int(ds.attrs['minId'][0])] = np.asarray(ds[:])
        # Current selected artifacts contain one contiguous coordinate section.
        assert len(coordinates) == 1 and 1 in coordinates
        xyz = coordinates[1]
        for name in names:
            i = zone_names.index(name)
            assert int(zones['zoneType'][i]) == 3
            lo, hi = int(zones['minId'][i]), int(zones['maxId'][i])
            points, areas, normals = [], [], []
            for section in mesh['faces/nodes'].values():
                s_lo, s_hi = int(section.attrs['minId'][0]), int(section.attrs['maxId'][0])
                begin, end = max(lo, s_lo), min(hi, s_hi)
                if begin > end:
                    continue
                counts = np.asarray(section['nnodes'][:], dtype=np.int64)
                offsets = np.r_[0, np.cumsum(counts)]
                first, last = begin - s_lo, end - s_lo + 1
                raw = section['nodes'][int(offsets[first]):int(offsets[last])]
                local = offsets[first:last + 1] - offsets[first]
                for a, b in zip(local[:-1], local[1:]):
                    p = xyz[raw[int(a):int(b)].astype(np.int64) - 1]
                    anchor = p.mean(axis=0)
                    q = np.roll(p, -1, axis=0)
                    vectors = .5 * np.cross(p - anchor, q - anchor)
                    weights = np.linalg.norm(vectors, axis=1)
                    area_vector = vectors.sum(axis=0)
                    area = np.linalg.norm(area_vector)
                    assert area > 0 and weights.sum() > 0
                    points.append(np.average((p + q + anchor) / 3, axis=0, weights=weights))
                    areas.append(area)
                    normals.append(area_vector / area)
            assert len(points) == hi - lo + 1
            result[name] = dict(lo=lo, hi=hi, points=np.array(points),
                                areas=np.array(areas), normals=np.array(normals))
    return result


def select(chunks, lo, hi):
    values = np.full(hi - lo + 1, np.nan)
    for a, b, data in chunks:
        left, right = max(lo, a), min(hi, b)
        if left <= right:
            assert np.isnan(values[left-lo:right-lo+1]).all()
            values[left-lo:right-lo+1] = data[left-a:right-a+1]
    assert np.isfinite(values).all(), 'Film data do not cover the complete wall'
    return values


def write_profile(path, walls):
    with path.open('x') as stream:
        for i, wall in enumerate(walls.values()):
            fields = dict(zip(['x', 'y', 'z'], wall['points'].T))
            fields.update(height=wall['height'])
            fields.update(dict(zip(['film-u', 'film-v', 'film-w'], wall['velocity'].T)))
            stream.write(f'((ewf-seed-{i} point {len(wall["height"])})\n')
            for field, values in fields.items():
                stream.write('(' + field + '\n')
                np.savetxt(stream, values, fmt='%.17g')
                stream.write(')\n')
            stream.write(')\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-case', type=Path, required=True)
    p.add_argument('--source-data', type=Path, required=True)
    p.add_argument('--target-case', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert not args.output.exists(), 'Use a new output folder'
    hashes = {k: digest(getattr(args, k)) for k in ['source_case', 'source_data', 'target_case']}
    names = ['wall', 'wall:004']
    fields = face_fields(args.source_data)
    source = geometry(args.source_case, names)
    target = geometry(args.target_case, names)
    report = {'status': 'OFFLINE_CANDIDATE_NATIVE_INITIALISATION_UNVERIFIED',
              'input_hashes': hashes, 'source_case': str(args.source_case),
              'source_data': str(args.source_data), 'target_case': str(args.target_case),
              'mapping': 'Nearest of 64 face centroids within same named wall with normal dot product >= 0.9; velocity projected to target tangent',
              'height_scaling_or_clipping': False, 'solver_mutations': 0, 'walls': {}}
    for name in names:
        s, t = source[name], target[name]
        s['height'] = select(fields['HEIGHT'], s['lo'], s['hi'])
        s['velocity'] = np.column_stack([select(fields[k], s['lo'], s['hi']) for k in ['U', 'V', 'W']])
        assert (s['height'] >= 0).all()
        distances, neighbours = cKDTree(s['points']).query(t['points'], k=min(64, len(s['height'])))
        alignment = np.einsum('ijk,ik->ij', s['normals'][neighbours], t['normals'])
        compatible = alignment >= .9
        assert compatible.any(axis=1).all(), 'No compatible donor face among nearest 64'
        choices = np.where(compatible, distances, np.inf).argmin(axis=1)
        rows = np.arange(len(t['points']))
        distance, indices = distances[rows, choices], neighbours[rows, choices]
        t['height'] = s['height'][indices]
        velocity = s['velocity'][indices]
        t['velocity'] = velocity - np.einsum('ij,ij->i', velocity, t['normals'])[:, None] * t['normals']
        source_volume = float(np.dot(s['height'], s['areas']))
        target_volume = float(np.dot(t['height'], t['areas']))
        report['walls'][name] = {
            'profile_name': 'ewf-seed-' + str(names.index(name)),
            'source_faces': len(s['height']), 'target_faces': len(t['height']),
            'source_area_m2': float(s['areas'].sum()), 'target_area_m2': float(t['areas'].sum()),
            'source_film_volume_m3': source_volume, 'mapped_film_volume_m3': target_volume,
            'volume_change_percent': 100 * (target_volume / source_volume - 1) if source_volume else None,
            'mapping_distance_m_max': float(distance.max()),
            'mapping_distance_m_p95': float(np.quantile(distance, .95)),
            'nearest_face_rejected_for_normal_count': int(np.count_nonzero(~compatible[:, 0])),
            'minimum_normal_alignment': float(np.einsum('ij,ij->i', s['normals'][indices], t['normals']).min()),
            'target_thickness_max_m': float(t['height'].max()),
            'target_velocity_normal_component_max_m_s': float(np.abs(np.einsum('ij,ij->i', t['velocity'], t['normals'])).max())}
    args.output.mkdir(parents=True)
    write_profile(args.output / 'donor-film.prof', source)
    write_profile(args.output / 'receiver-film-candidate.prof', target)
    for label in ['donor-film.prof', 'receiver-film-candidate.prof']:
        report[label + '_sha256'] = digest(args.output / label)
    (args.output / 'mapping-receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
