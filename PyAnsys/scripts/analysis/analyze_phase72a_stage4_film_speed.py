"""Read verified native HDF5 film fields without connecting to Fluent."""
from pathlib import Path
import hashlib
import json
import math
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/phase72a-stage4-replacement/20261008/film-speed-N13000'
DOC = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/replacement-parent'
SHARED = Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase72A/stage4-replacement-20261008')


def main():
    block = ROOT / 'output/phase72a-stage4-replacement/20261008/bulk-N9000-N13000'
    receipt = json.loads((block / 'run-manifest.json').read_text())
    assert receipt['status'] == 'CHECKPOINT_VERIFIED' and receipt['target'] == 13000
    paths = {k: SHARED / f'final-N13000.{ext}' for k, ext in [('case', 'cas.h5'), ('data', 'dat.h5')]}
    hashes = {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in paths.items()}
    assert all(hashes[k] == receipt['pair'][k + '_sha256'] for k in paths)
    rho = receipt['final_readback']['materials']['fluid']['water-liquid-at-psep']['density']['value']
    with h5py.File(paths['case'], 'r') as case, h5py.File(paths['data'], 'r') as data:
        fields = data['results/1/phase-1/faces']
        height_dataset = fields['SV_EFILM_HEIGHT/1']
        height = height_dataset[:]
        first = int(height_dataset.attrs['minId'][0])
        ids = np.arange(first, first + len(height))
        velocity = np.column_stack([fields[n + '/1'][:] for n in ['SV_EFILM_U', 'SV_EFILM_V', 'SV_EFILM_W']])
        speed = np.linalg.norm(velocity, axis=1)
        for name in ['SV_EFILM_U', 'SV_EFILM_V', 'SV_EFILM_W']:
            assert int(fields[name + '/1'].attrs['minId'][0]) == first
            assert fields[name + '/1'].shape == height.shape
        mesh = case['meshes/1']
        coordinates = list(mesh['nodes/coords'].values())
        assert len(coordinates) == 1 and int(coordinates[0].attrs['minId'][0]) == 1
        xyz = coordinates[0][:]
        counts = mesh['faces/nodes/1/nnodes'][:]
        offsets = np.r_[0, np.cumsum(counts, dtype=np.int64)]
        node_ids = mesh['faces/nodes/1/nodes'][:]
        areas, centres = [], []
        for face in ids - 1:
            vertices = xyz[node_ids[offsets[face]:offsets[face + 1]].astype(np.int64) - 1]
            area_vector = .5 * np.cross(vertices[1:-1] - vertices[0], vertices[2:] - vertices[0]).sum(axis=0)
            areas.append(np.linalg.norm(area_vector))
            centres.append(vertices.mean(axis=0))
        zones = mesh['faces/zoneTopology']
        names = zones['name'][0].decode().split(';')
        selected_zones = {name: [int(lo), int(hi)] for name, lo, hi in zip(names, zones['minId'][:], zones['maxId'][:]) if name in ['wall', 'wall:004']}
        expected_ids = np.concatenate([np.arange(lo, hi + 1) for lo, hi in selected_zones.values()])
        assert np.array_equal(ids, expected_ids), 'Stored film faces differ from designated film walls'
    mass = rho * height * np.asarray(areas)
    assert np.all(np.isfinite(speed)) and np.all(mass >= 0)
    expected_mass = receipt['final_reports']['p72d-total-mass'][0]
    expected_speed = receipt['final_reports']['p72r-film-speed-max'][0]
    assert math.isclose(mass.sum(), expected_mass, rel_tol=1e-10, abs_tol=1e-12)
    assert math.isclose(speed.max(), expected_speed, rel_tol=1e-7, abs_tol=1e-6)
    order = np.argsort(speed)
    cdf = np.cumsum(mass[order]) / mass.sum()
    peak = int(np.argmax(speed))
    summary = {
        'native_iteration': 13000, 'source_paths': {k: str(v) for k, v in paths.items()}, 'source_sha256': hashes,
        'field_names': ['SV_EFILM_HEIGHT', 'SV_EFILM_U', 'SV_EFILM_V', 'SV_EFILM_W'],
        'film_face_zones': selected_zones, 'film_mass_reconstructed_kg': float(mass.sum()),
        'mass_weighted_mean_speed_m_s': float(np.average(speed, weights=mass)),
        'mass_weighted_percentiles_m_s': {str(q): float(np.interp(q / 100, cdf, speed[order])) for q in [50, 90, 95, 99]},
        'film_mass_fraction_above_speed': {str(v): float(mass[speed > v].sum() / mass.sum()) for v in [1, 10, 30, 50, 80]},
        'fastest_face': {'id': int(ids[peak]), 'speed_m_s': float(speed[peak]), 'thickness_m': float(height[peak]),
                         'film_mass_kg': float(mass[peak]), 'vertex_average_xyz_m': centres[peak].tolist(), 'velocity_xyz_m_s': velocity[peak].tolist()},
        'signed_y_mass_weighted_velocity_m_s': float(np.average(velocity[:, 1], weights=mass)),
        'verification': 'SHA256 paired files; reconstructed total film mass and maximum speed match native endpoint reports',
        'limits': 'One saved endpoint; velocity components use global coordinates; wet-film motion is not physical validation; force balance remains unmeasured.'}
    OUT.mkdir(exist_ok=True)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    figures = DOC / 'figures'; figures.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(speed[order], 100 * cdf, lw=1.5, color='#2C8ED2')
    ax.axvline(summary['mass_weighted_mean_speed_m_s'], ls='--', color='#777777', label='Mass-weighted mean: 24.1 m/s')
    ax.scatter([50], [100 * mass[speed <= 50].sum() / mass.sum()], color='#FA1900', zorder=3)
    ax.annotate('12.9% of film mass above 50 m/s', (50, 87.1), xytext=(28, 60), arrowprops={'arrowstyle': '->'}, fontsize=9)
    ax.set(xlabel='Film speed magnitude (m/s)', ylabel='Film mass at or below this speed (%)', title='N13000: liquid-mass-weighted film speed', xlim=(0, 95), ylim=(0, 102))
    ax.grid(alpha=.2); ax.legend(loc='lower right', fontsize=9)
    fig.tight_layout(); fig.savefig(figures / 'N13000-film-speed-mass-cdf.png', dpi=160); plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()
