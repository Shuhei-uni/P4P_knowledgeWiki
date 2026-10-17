"""Make report-sized Phase 9 snapshot plots; never invent missing histories."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.collections import PolyCollection

from gather_phase9_selected_results import ROOT, OUT, digest, write_json, parse_vars, pairs, unquote

FIG = ROOT / 'Project/experiments/phase-09-mesh-convergence/figures'
ORDER = ['60k', '342k', '680k', '997k', '2.6M']
COLORS = ['#4477AA', '#EE6677', '#228833', '#AA3377', '#CCBB44']


def report(r, *names):
    for n in names:
        s = r['reports'].get(n)
        if s and s['at_selected_iteration']:
            return s['value']
    return np.nan


def field(g, name, first, stop):
    values = np.full(stop - first, np.nan)
    if name not in g:
        return values
    for ds in g[name].values():
        a, b = int(ds.attrs['minId'][0]) - 1, int(ds.attrs['maxId'][0])
        lo, hi = max(first, a), min(stop, b)
        if hi > lo:
            values[lo-first:hi-first] = ds[lo-a:hi-a]
    return values


def cumulative(g, name, first, stop):
    a = field(g, name, first, stop)
    return float(a.sum()) if np.all(np.isfinite(a)) else None


def surface_extract(r):
    path = OUT / (r['mesh'] + '-' + r['stage']) / 'surfaces.npz'
    meta_path = path.with_suffix('.json')
    if path.exists() and meta_path.exists():
        cached = json.loads(meta_path.read_text())
        if cached.get('schema_version') == 4:
            return cached
    arrays = {}
    meta = {'schema_version': 4, 'walls': {}}
    with h5py.File(r['case'], 'r') as c, h5py.File(r['data'], 'r') as d:
        mesh = c['meshes/1']
        topo = mesh['faces/zoneTopology']
        names = topo['name'][0].decode().split(';')
        nn = mesh['faces/nodes/1/nnodes'][:].astype(np.int64)
        offsets = np.r_[0, np.cumsum(nn)]
        nodes = mesh['faces/nodes/1/nodes']
        xyz = next(iter(mesh['nodes/coords'].values()))[:]
        assert np.max(np.abs(xyz)) < 30, 'Unexpected coordinates; metres not established'
        liquid = d['results/1/phase-3']
        densities = np.concatenate([ds[:] for ds in liquid['cells/SV_DENSITY'].values()])
        rho = float(np.median(densities))
        assert np.max(np.abs(densities - rho)) < 1e-6
        meta['liquid_density_kg_m3'] = rho
        for wall in ['wall', 'wall:004']:
            if wall not in names:
                continue
            i = names.index(wall)
            first, stop = int(topo['minId'][i]) - 1, int(topo['maxId'][i])
            count = nn[first:stop]
            idx = nodes[offsets[first]:offsets[stop]].astype(np.int64) - 1
            points = xyz[idx]
            starts = np.r_[0, np.cumsum(count)[:-1]]
            nxt = np.arange(len(points)) + 1
            nxt[np.cumsum(count)-1] = starts
            avec = .5 * np.add.reduceat(np.cross(points, points[nxt]), starts)
            area = np.linalg.norm(avec, axis=1)
            centre = np.add.reduceat(points, starts) / count[:, None]
            g = d['results/1/phase-1/faces']
            height = field(g, 'SV_EFILM_HEIGHT', first, stop)
            if np.all(np.isnan(height)):
                meta['walls'][wall] = {'film_allocated': False, 'area_m2': float(area.sum())}
                continue
            assert np.all(np.isfinite(height)) and np.min(height) >= 0
            u, v, w = [field(g, n, first, stop) for n in ['SV_EFILM_U', 'SV_EFILM_V', 'SV_EFILM_W']]
            key = 'upper' if wall == 'wall' else 'lower'
            for name, a in [('xyz', centre), ('area', area), ('height', height), ('u', u), ('v', v), ('w', w)]:
                arrays[key + '_' + name] = a
            arrays[key + '_vertices'] = points
            arrays[key + '_nnodes'] = count
            meta['walls'][wall] = {'film_allocated': True, 'area_m2': float(area.sum()),
                'film_mass_kg': float(np.dot(area, height) * rho),
                'maximum_thickness_mm': float(height.max() * 1000),
                'area_weighted_thickness_mm': float(np.dot(area, height) / area.sum() * 1000),
                'native_outflow_cumulative_kg': cumulative(g, 'SV_EFILM_OUTFLOW_MASS_SUM', first, stop),
                'stripped_cumulative_kg': cumulative(g, 'SV_EFILM_STRIPPED_MASS_SUM', first, stop),
                'separated_cumulative_kg': cumulative(g, 'SV_EFILM_SEPARATED_MASS_SUM', first, stop)}
        i = names.index('steamoutlet')
        first, stop = int(topo['minId'][i]) - 1, int(topo['maxId'][i])
        flux = field(liquid['faces'], 'SV_FLUX', first, stop)
        assert np.all(np.isfinite(flux))
        meta['boundary_liquid_outward_kg_s'] = float(flux.sum())
        cached = -report(r, 'v2-flux-phase2-steamoutlet')
        meta['boundary_flux_abs_difference_vs_cached_report'] = float(abs(meta['boundary_liquid_outward_kg_s']-cached))
        upper = meta['walls'].get('wall', {}).get('film_mass_kg', 0)
        upper_report = report(r, 'p72d-upper-mass', 'p72a-e2.7-ewf-film-mass-total')
        meta['upper_film_abs_difference_vs_cached_report_kg'] = float(abs(upper-upper_report))
        # Film and liquid material density equality is checked by independent
        # agreement with Fluent's saved upper-wall film-mass report.
        assert abs(upper-upper_report) < max(1e-6, abs(upper_report)*2e-5)
        assert meta['boundary_flux_abs_difference_vs_cached_report'] < 1e-5
        rv = parse_vars(c['settings/Rampant Variables'][0].decode())
        expressions = {}
        for entry in rv.get('named-expressions', []):
            e = pairs(entry)
            if 'name' in e and 'definition' in e:
                expressions[unquote(e['name'])] = unquote(e['definition']).replace('\\"', '"')
        # Some Fluent files use the namespace-prefixed expression key.
        if not expressions:
            for key, entries in rv.items():
                if 'named-expressions' not in key or not isinstance(entries, list): continue
                for entry in entries:
                    e = pairs(entry)
                    if 'name' in e and 'definition' in e:
                        expressions[unquote(e['name'])] = unquote(e['definition']).replace('\\"', '"')
        if 'P72dRemoval' in expressions:
            assert expressions['P72dRate'] == 'min(1/P72dTau,P72dMaxFraction/P72dRefreshSpan)'
            assert expressions['P72dSink'] == '-P72dEnabled*P72dRate*P72dDensity*P72dHeight'
            assert expressions['P72dHeight'] == 'max(FilmThickness,0[m])'
            scalar = lambda key: float(expressions[key].split('[')[0])
            enabled = scalar('P72dEnabled')
            factor = min(1/scalar('P72dTau'), scalar('P72dMaxFraction')/scalar('P72dRefreshSpan'))
            assert abs(scalar('P72dDensity')-rho) < 1e-6
            assert 'P72dSink' in c['settings/Thread Variables'][0].decode()
            lower = meta['walls'].get('wall:004', {}).get('film_mass_kg', 0)
            meta['film_drain_expression_kg_s'] = enabled*factor*lower
            meta['film_drain_definitions'] = {k:v for k,v in expressions.items() if k.startswith('P72d')}
            saved_rate = report(r, 'p72d-drain-rate')
            if np.isfinite(saved_rate):
                err = abs(saved_rate-meta['film_drain_expression_kg_s'])
                assert err < max(1e-7, abs(saved_rate)*1e-5)
                meta['drain_expression_abs_difference_vs_cached_report'] = err
    np.savez_compressed(path, **arrays)
    write_json(meta_path, meta)
    return meta


def save(fig, stem, records, note):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / (stem + '.png'), dpi=300, bbox_inches='tight')
    fig.savefig(FIG / (stem + '.pdf'), bbox_inches='tight')
    plt.close(fig)
    write_json(FIG / (stem + '.provenance.json'), {
        'generator': str(Path(__file__).relative_to(ROOT)), 'generator_sha256': digest(Path(__file__)),
        'sources': [{'mesh': r['mesh'], 'stage': r['stage'], 'iteration': r['selected_native_iteration'],
            'case': r['case'], 'data': r['data'], 'case_identity': r['case_identity'], 'data_identity': r['data_identity']}
            for r in records], 'note': note, 'case_loads': 0, 'solve_calls': 0,
        'png_sha256': digest(FIG / (stem + '.png'))})


def style(ax):
    ax.grid(axis='y', alpha=.2, linewidth=.6)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_axisbelow(True)


def compare(ax, rows, key, ylabel, title):
    for stage, dx, color, marker, label in [
        ('start', -.10, '#666666', 'o', 'Pre-EWF / freeze boundary'),
        ('195ms', .10, '#0072B2', 's', '195 ms; bulk frozen')]:
        rs = [r for r in rows if r['stage'] == stage]
        x = [ORDER.index(r['mesh']) + dx for r in rs]
        y = [key(r) for r in rs]
        ax.scatter(x, y, s=32, c=color, marker=marker, label=label, zorder=3)
    ax.set(xticks=range(5), xticklabels=ORDER, ylabel=ylabel, title=title, xlim=(-.45, 4.45))
    style(ax)


def main():
    rows = json.loads((OUT / 'selected-results.json').read_text())
    assert len(rows) in (8, 9)
    for r in rows:
        print('SURFACES', r['mesh'], r['stage'], flush=True)
        r['surface'] = surface_extract(r)
    write_json(OUT / 'selected-results-with-surfaces.json', rows)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
        'axes.titlesize': 10, 'axes.labelsize': 9, 'legend.fontsize': 8,
        'pdf.fonttype': 42, 'ps.fonttype': 42})
    note = 'Discrete saved states, not time histories. The 2.6M starting state uses provisional EWF settings; its 195 ms pair is missing.'
    fig, ax = plt.subplots(1, 3, figsize=(7.1, 2.8), layout='constrained')
    compare(ax[0], rows, lambda r: r['surface']['boundary_liquid_outward_kg_s'], 'Liquid outflow (kg/s)', '(a) Steam outlet: bulk liquid')
    compare(ax[1], rows, lambda r: report(r, 'v2-absorber-removal', 'p72-contact-removal'), 'Collector removal (kg/s)', '(b) Bulk collector')
    compare(ax[2], rows, lambda r: r['surface'].get('film_drain_expression_kg_s', np.nan), 'Film sink rate (kg/s)', '(c) Lower-wall film drain')
    fig.legend(*ax[0].get_legend_handles_labels(), loc='outside upper center', ncol=2, frameon=False)
    for a in ax: a.set_xlabel('Mesh (cells, nominal)')
    save(fig, 'selected-liquid-routing', rows, note + ' Boundary liquid flux independently reconstructed from phase-3/SV_FLUX; phase-3 is HDF5 liquid, corresponding to Fluent phase-2. Film drain is the saved named-expression sink integrated over saved lower-wall film; checked against cached native drain reports where present. This is an endpoint rate, not interval removal.')

    fig, ax = plt.subplots(1, 3, figsize=(7.1, 2.8), layout='constrained')
    compare(ax[0], rows, lambda r: report(r, 'v2-total-liquid-mass'), 'Bulk liquid mass (kg)', '(a) Bulk inventory')
    compare(ax[1], rows, lambda r: sum(w.get('film_mass_kg', 0) for w in r['surface']['walls'].values()), 'Film mass (kg)', '(b) Total film inventory')
    compare(ax[2], rows, lambda r: r['surface']['walls'].get('wall:004', {}).get('film_mass_kg', np.nan), 'Lower-wall film mass (kg)', '(c) Lower-wall film inventory')
    fig.legend(*ax[0].get_legend_handles_labels(), loc='outside upper center', ncol=2, frameon=False)
    for a in ax: a.set_xlabel('Mesh (cells, nominal)')
    save(fig, 'selected-liquid-inventory', rows, note + ' Film mass reconstructed from saved face area and thickness; density verified against Fluent upper-wall film-mass report. No inventory slopes are inferred.')

    fig, axes = plt.subplots(2, 2, figsize=(7.1, 4.9), layout='constrained')
    metrics = [
        (lambda r: r['surface']['boundary_liquid_outward_kg_s'], 'Liquid outflow (kg/s)', '(a) Steam outlet: bulk liquid'),
        (lambda r: report(r, 'v2-total-liquid-mass'), 'Bulk liquid mass (kg)', '(b) Bulk inventory'),
        (lambda r: sum(w.get('film_mass_kg', 0) for w in r['surface']['walls'].values()), 'Film mass (kg)', '(c) Total film inventory'),
        (lambda r: r['surface'].get('film_drain_expression_kg_s', np.nan), 'Film sink rate (kg/s)', '(d) Lower-wall film drain')]
    for ax, (key, ylabel, title) in zip(axes.flat, metrics):
        compare(ax, rows, key, ylabel, title)
        ax.set_xlabel('Mesh (cells, nominal)')
    fig.legend(*axes.flat[0].get_legend_handles_labels(), loc='outside upper center', ncol=2, frameon=False)
    save(fig, 'selected-mesh-response', rows, note + ' Report-facing summary. Endpoint dots do not imply histories or independent samples. See selected-liquid-routing and selected-liquid-inventory provenance for reconstruction checks.')

    fig, axes = plt.subplots(2, 3, figsize=(7.1, 4.6), layout='constrained')
    starts = [r for r in rows if r['stage'] == 'start']
    for ax, r, color in zip(axes.flat, starts, COLORS):
        for eq, ls in [('continuity', '-'), ('vf-phase-2', '--')]:
            p = ROOT / r['residuals'][eq]['csv']
            a = np.loadtxt(p, delimiter=',', skiprows=1)
            a = a[a[:, 0] >= 1580]
            y = np.divide(a[:, 1], a[:, 2], out=np.full(len(a), np.nan), where=a[:, 2] != 0)
            ax.plot(a[:, 0], y, color=('#46D2BA' if eq == 'continuity' else '#FB9DCD'), ls=ls, lw=.85, label=eq)
        ax.set(title=f'{r["mesh"]}: through N{r["selected_native_iteration"]}', xlabel='Native iteration', ylabel='Scaled bulk residual', yscale='log')
        style(ax)
    axes.flat[0].legend(fontsize=7)
    for unused in list(axes.flat)[len(starts):-1]:
        unused.axis('off')
    axes.flat[-1].axis('off')
    axes.flat[-1].text(0, .9, 'Saved samples only.\nEarly samples are decimated.\n\n195 ms bulk residuals are\nheld values during frozen flow;\nthey are not plotted as convergence.', va='top', fontsize=9)
    save(fig, 'selected-bulk-residuals', starts, 'Embedded HDF5 residual data: column 0 / normalization column 1. This normalization is independently checked against existing native transcript evidence in the audit. Coordinates are native; no interpolation of missing samples. Only starting states are shown because all 195 ms states hold bulk equations frozen.')

    paired = [r for r in rows if r['stage'] == '195ms']
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.8), layout='constrained')
    for ax, key, title in zip(axes, ['stripped_cumulative_kg', 'separated_cumulative_kg'], ['(a) Film stripping', '(b) Edge separation']):
        vals = []
        for r in paired:
            before = next(x for x in rows if x['mesh'] == r['mesh'] and x['stage'] == 'start')
            def get(x):
                values = [w[key] for w in x['surface']['walls'].values() if w['film_allocated']]
                assert all(v is not None for v in values), 'Missing cumulative field; do not substitute zero'
                return sum(values)
            vals.append(get(r) - get(before))
        assert min(vals) >= -1e-8, 'Cumulative counter reset; cannot difference selected pairs'
        ax.bar([r['mesh'] for r in paired], vals, width=.55, color=COLORS[:4])
        ax.set(title=title, ylabel='Counter increase (kg)', xlabel='Mesh (cells, nominal)')
        style(ax)
    save(fig, 'selected-film-release', rows, 'Differences of saved cumulative film stripping and edge-separation counters between each selected start and 195 ms. Internal transfers, not external carryover or collection. Starting ages differ, and 342k includes a bulk-active adjustment. No complete film ledger can be inferred without source/drain histories.')

    fig, axes = plt.subplots(2, 4, figsize=(7.1, 5.0), layout='constrained', sharex=True, sharey=True)
    norm = Normalize(0, .30)
    for col, mesh in enumerate(ORDER[:4]):
        for row, stage in enumerate(['start', '195ms']):
            r = next(x for x in rows if x['mesh'] == mesh and x['stage'] == stage)
            p = OUT / (mesh + '-' + stage) / 'surfaces.npz'
            with np.load(p) as d:
                xyz = d['upper_xyz']; theta = np.degrees(np.arctan2(xyz[:, 2], xyz[:, 0]))
                radius = np.hypot(xyz[:, 0], xyz[:, 2])
                vessel = (np.abs(radius-1.067) < .08) & (xyz[:, 1] >= .1)
                ax = axes[row, col]
                vertices = d['upper_vertices']; counts = d['upper_nnodes']
                offsets = np.r_[0, np.cumsum(counts)]
                angle = np.degrees(np.arctan2(vertices[:, 2], vertices[:, 0]))
                ctheta = np.repeat(theta, counts)
                angle = ctheta + (angle-ctheta+180) % 360 - 180
                mapped = np.column_stack([angle, vertices[:, 1]])
                polygons = [mapped[offsets[i]:offsets[i+1]] for i in np.flatnonzero(vessel)]
                image = PolyCollection(polygons, array=d['upper_height'][vessel]*1000,
                    cmap='viridis', norm=norm, edgecolors='none', rasterized=True)
                ax.add_collection(image)
                # Bin velocities to keep arrows readable independent of mesh density.
                bins = []
                for t in np.arange(-150, 180, 60):
                    for y in np.arange(.5, 5.6, 1.0):
                        sel = vessel & (abs(theta-t)<25) & (abs(xyz[:, 1]-y)<.35) & (d['upper_height']>1e-8)
                        if np.count_nonzero(sel) < 2: continue
                        rad = np.radians(theta[sel]); weight = d['upper_area'][sel]
                        vt = -np.sin(rad)*d['upper_u'][sel]+np.cos(rad)*d['upper_w'][sel]
                        bins.append((t, y, np.average(vt, weights=weight), np.average(d['upper_v'][sel], weights=weight)))
                if bins:
                    b = np.array(bins); mag = np.hypot(b[:, 2], b[:, 3]); good = mag>1e-10
                    ax.quiver(b[good, 0], b[good, 1], b[good, 2]/mag[good]*.3/1.067*180/np.pi, b[good, 3]/mag[good]*.3,
                        angles='xy', scale_units='xy', scale=1, color='white', width=.007)
                ax.set(title=f'{mesh}: {r["film_state"]["film_elapsed_time"]*1000:.3f} ms', xlim=(-180, 180), ylim=(.1, 6), xticks=[-180, 0, 180])
                if col == 0:ax.set_ylabel(('Starting state' if row == 0 else '195 ms') + '\nHeight y (m)')
    fig.supxlabel('Angle about +Y (degrees)', fontsize=9)
    fig.colorbar(image, ax=axes, shrink=.8, label='Film thickness (mm); values >0.30 clipped')
    save(fig, 'selected-film-thickness', rows, 'Offline face-constant polygons on the cylindrical vessel wall, unwrapped using atan2(z,x); inlet and lower collector are excluded by physical radius/height. Colour limits common at 0–0.30 mm, thicker values saturated; maxima retained in endpoint CSV. White arrows show area-weighted binned film-velocity direction, each normalized to a 0.3 m path length, not speed. Starting film ages differ. This is not a Fluent-native contour or an interpolated field.')

    columns = ['mesh', 'stage', 'native_iteration', 'film_age_ms', 'bulk_liquid_kg', 'film_total_kg', 'film_lower_kg',
        'bulk_liquid_outlet_kg_s', 'bulk_collector_kg_s', 'film_drain_expression_kg_s', 'pressure_difference_kPa', 'film_thickness_max_mm']
    table = []
    for r in rows:
        w = r['surface']['walls']
        vals = [r['mesh'], r['stage'], r['selected_native_iteration'], r['film_state']['film_elapsed_time']*1000,
            report(r, 'v2-total-liquid-mass'), sum(v.get('film_mass_kg', 0) for v in w.values()),
            w.get('wall:004', {}).get('film_mass_kg', np.nan), r['surface']['boundary_liquid_outward_kg_s'],
            report(r, 'v2-absorber-removal', 'p72-contact-removal'), r['surface'].get('film_drain_expression_kg_s', np.nan),
            (report(r, 'p72s3-pressure-inlet')-report(r, 'p72s3-pressure-outlet'))/1000,
            max(v.get('maximum_thickness_mm', 0) for v in w.values())]
        table.append(dict(zip(columns, [None if isinstance(v, float) and not np.isfinite(v) else v for v in vals])))
    with (OUT/'endpoint-results.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns); writer.writeheader(); writer.writerows(table)
    write_json(OUT/'endpoint-results.json', table)
    audit = {
        'date_local': '2026-10-17', 'timezone': 'Pacific/Auckland',
        'snapshots': [{'mesh':r['mesh'], 'stage':r['stage'], 'native_iteration':r['selected_native_iteration'],
            'film_age_ms':r['film_state']['film_elapsed_time']*1000,
            'current_report_samples':sum(s['at_selected_iteration'] for s in r['reports'].values()),
            'embedded_report_history_buffers':r['report_history_buffer_count'],
            'continuity_samples':r['residuals']['continuity'],
            'film_subiteration_residual_history_present':any('film' in name for name in r['residuals']),
            'dpm_summary_present':bool(r['dpm_summary']),
            'record':str((OUT/(r['mesh']+'-'+r['stage'])/'record.json').relative_to(ROOT))} for r in rows],
        'standalone_shared_history_files': [],
        'other_local_history': 'The 20261009 local 60k pilot is a different run and is excluded from production results; one pilot transcript validates the HDF5 residual normalization format only.',
        'remote_availability': {'1':'TCP_UNREACHABLE','3':'TCP_UNREACHABLE','4':'TCP_UNREACHABLE','5':'NO_LOCAL_CONNECTION_CONFIG','6':'NO_LOCAL_CONNECTION_CONFIG'},
        'missing': [
            '2.6M 195 ms case/data pair',
            'Selected-run continuous bulk flux and liquid inventory histories',
            'Selected-run film source and direct-drain histories needed for interval integrals',
            'Selected-run native film subiteration residual transcripts',
            'DPM outlet mass/fate evidence and verified internal-transfer receiving representation'],
        'consequences': [
            'No inventory slopes, late-window means, film ledger closure, or total separator efficiency calculated.',
            'Residual arrays are decimated. Frozen-stage repetitions are excluded from convergence plots.',
            'Direct drain reconstructed only as an endpoint expression rate, not integrated removal.',
            'Stripping/separation counter differences are internal transfer diagnostics only.'],
        'normalization_check':'residual-normalization-check.json',
        'recovery': 'Retrieve the report files identified in each record.json/report_files and the corresponding native transcripts from the owning Fluent hosts. Do not rerun production solely to regenerate missing old histories.'}
    write_json(OUT/'history-audit.json', audit)
    print('PLOTS_COMPLETE', len(table), flush=True)


if __name__ == '__main__':
    main()
