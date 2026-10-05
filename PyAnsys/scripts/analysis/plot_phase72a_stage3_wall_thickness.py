"""Plot saved native EWF face values on verified separator wall polygons.

Uses the user's requested Matplotlib plot style. These are Python renderings
of Fluent field data, not native Fluent graphics exports. No interpolation,
solution loading, setting change or solve is performed by this script.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/phase72a-stage3-film-development-server1/20261005'
DEST = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/figures'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--latest', type=int, help='Use this verified snapshot rather than the latest completed block')
    args = parser.parse_args()
    manifest = json.loads((OUT / 'run-manifest.json').read_text())
    latest = next(b for b in reversed(manifest['blocks']) if b.get('facet_fields')
                  and (args.latest is None or b['native_end'] == args.latest))
    early = next(b for b in manifest['blocks'] if b['native_end'] == 5190
                 and Path(b.get('output', '')).name == 'adaptive-development')
    middle = next(b for b in manifest['blocks'] if b['native_end'] == 13390
                  and Path(b.get('output', '')).name == 'adaptive-recovery-from-N7190')
    chosen = [early, middle, latest]
    folder = OUT / 'wall-thickness-views'
    geometry_path = folder / 'wall-geometry.npz'
    geo = np.load(geometry_path)
    vertices = geo['vertices'].astype(float)
    face_indices = np.split(geo['connectivity'], np.cumsum(geo['face_sizes'])[:-1])
    polygons = [vertices[ix] for ix in face_indices]
    areas = np.array([.5*np.linalg.norm(np.cross(p, np.roll(p, -1, axis=0)).sum(axis=0)) for p in polygons])
    assert np.isfinite(vertices).all() and np.all(areas > 0)
    # Fluent's y axis is vertical; map to Matplotlib's third plotting axis.
    display_polygons = [p[:, [0, 2, 1]] for p in polygons]
    lo, hi = vertices.min(axis=0), vertices.max(axis=0)
    limits = [(lo[i], hi[i]) for i in [0, 2, 1]]
    widths = np.array([b-a for a, b in limits])
    norm = Normalize(0, .30)
    cmap = plt.get_cmap('viridis')
    sources = []
    values = []
    for block in chosen:
        path = Path(block['facet_fields'])
        a = np.load(path)
        assert np.allclose(a['centroids'], geo['centroids'], rtol=0, atol=1e-7), 'Snapshot wall-face order differs from geometry'
        thickness = a['film-thickness'].astype(float)
        assert len(thickness) == len(polygons) and np.isfinite(thickness).all() and np.all(thickness >= 0)
        assert np.isclose(a['film-mass'].sum(), block['film_mass_kg'], rtol=2e-6)
        assert thickness.max()*1000 <= norm.vmax, 'Shared range clips a source snapshot'
        values.append(thickness*1000)
        sources.append({'native_iteration': block['native_end'], 'film_time_ms': block['film_time_s']*1000,
                        'film_mass_kg': block['film_mass_kg'], 'snapshot_max_thickness_mm': thickness.max()*1000,
                        'wall_area_m2': areas.sum(),
                        'area_at_least_1um_percent': 100*areas[thickness >= 1e-6].sum()/areas.sum(),
                        'area_at_least_0p1mm_percent': 100*areas[thickness >= 1e-4].sum()/areas.sum(),
                        'field_file': str(path), 'field_sha256': digest(path),
                        'pair': block['pair'], 'centroid_match': 'PASS', 'facet_mass_report_match': 'PASS'})
    DEST.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13})

    def draw(ax, data, source, angle):
        ax.add_collection3d(Poly3DCollection(display_polygons, facecolors=cmap(norm(data)),
                                           edgecolors='none', linewidths=0, antialiased=False,
                                           zsort='average'))
        for setter, (minimum, maximum) in zip([ax.set_xlim, ax.set_ylim, ax.set_zlim], limits):
            pad = .025*(maximum-minimum)
            setter(minimum-pad, maximum+pad)
        ax.set_box_aspect(widths)
        ax.view_init(elev=12, azim=angle)
        ax.set_proj_type('ortho')
        ax.set_xlabel('X (m)', labelpad=5)
        ax.set_ylabel('Z (m)', labelpad=5)
        ax.set_zlabel('Height Y (m)', labelpad=8)
        ax.set_xticks([-2, 0, 1])
        ax.set_yticks([-1, 0, 1])
        ax.set_zticks([0, 2, 4, 6])
        ax.tick_params(labelsize=9, pad=0)
        ax.grid(False)
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.set_facecolor((1, 1, 1, 0))
            axis.pane.set_edgecolor((.9, .9, .9, .4))
        ax.set_title(f"N{source['native_iteration']}  |  {source['film_time_ms']:.2f} ms\n"
                     f"Film mass {source['film_mass_kg']:.3f} kg", pad=8)

    mapper = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    fig = plt.figure(figsize=(15, 8), facecolor='white')
    axes = [fig.add_subplot(1, 3, i+1, projection='3d') for i in range(3)]
    for ax, data, source in zip(axes, values, sources):
        draw(ax, data, source, -135)
    fig.subplots_adjust(left=.01, right=.91, top=.86, bottom=.12, wspace=.02)
    bar = fig.colorbar(mapper, cax=fig.add_axes([.93, .24, .014, .49]), ticks=np.arange(0, .301, .05))
    bar.set_label('Wall-film thickness (mm)', labelpad=12)
    fig.suptitle('Wall-film development on the separator', fontsize=20, y=.96)
    fig.text(.5, .025, 'Same wall faces, camera and colour scale. Actual Fluent facet values; no spatial smoothing.\n'
             'Film time since dry start at A. Different development times; these snapshots do not establish steady film.',
             ha='center', fontsize=11)
    comparison = DEST / f'wall-film-thickness-development-N{latest["native_end"]}.png'
    fig.savefig(comparison, dpi=180)
    plt.close(fig)

    fig = plt.figure(figsize=(12, 9), facecolor='white')
    axes = [fig.add_subplot(1, 2, i+1, projection='3d') for i in range(2)]
    for ax, angle in zip(axes, [-135, 45]):
        draw(ax, values[-1], sources[-1], angle)
    fig.subplots_adjust(left=.02, right=.90, top=.86, bottom=.12, wspace=.04)
    bar = fig.colorbar(mapper, cax=fig.add_axes([.92, .25, .018, .48]), ticks=np.arange(0, .301, .05))
    bar.set_label('Wall-film thickness (mm)', labelpad=12)
    fig.suptitle('Latest saved wall film — opposite views', fontsize=20, y=.96)
    fig.text(.5, .025, f"Same N{latest['native_end']} snapshot from opposite sides. Maximum facet thickness "
             f"{sources[-1]['snapshot_max_thickness_mm']:.3f} mm.\n"
             'Colour shows thickness on the EWF wall, not bulk liquid volume fraction or a liquid pool.',
             ha='center', fontsize=11)
    current = DEST / f'wall-film-thickness-opposite-views-N{latest["native_end"]}.png'
    fig.savefig(current, dpi=180)
    plt.close(fig)
    record = {'status': 'FIGURES_CREATED_VISUAL_QA_PENDING', 'field': 'film-thickness', 'units': 'mm',
              'surface': 'wall', 'range_mm': [0, .30], 'colormap': 'viridis', 'node_interpolation': False,
              'renderer': 'Matplotlib Poly3DCollection of native Fluent wall faces; not a Fluent graphics export',
              'geometry_file': str(geometry_path), 'geometry_sha256': digest(geometry_path),
              'geometry_readback': json.loads((folder/'geometry-readback.json').read_text()),
              'facet_count': len(polygons), 'sources': sources,
              'camera': {'projection': 'orthographic', 'elevation_deg': 12,
                         'comparison_azimuth_deg': -135, 'opposite_azimuth_deg': 45,
                         'display_axis_mapping': ['X', 'Z', 'Y'], 'coordinate_units': 'm'},
              'figures': [{'path': str(p), 'sha256': digest(p)} for p in [comparison, current]],
              'claim_limit': 'Finite saved film development; frozen bulk; no steady-film or whole-separator qualification.'}
    (folder/f'figure-manifest-N{latest["native_end"]}.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
