"""Matched native histories and accepted continuation; no solver calls."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/phase72a-stage4-sensitivity/20261007'
DOC = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/setting-sensitivity'
FIG = DOC / 'figures'
PRIMARY_LABELS = {'stripping-on': 'Control: stripping + coupled ON',
                  'stripping-off': 'Stripping OFF; coupled ON',
                  'coupled-off': 'Stripping ON; coupled OFF'}
FORCE_BRANCHES = {'surface-tension-off-after-stripping': ('Surface tension OFF', {'surface-tension?': False}),
                  'spreading-off-after-stripping': ('Spreading OFF', {'mom-spreading?': False}),
                  'coupled-off-after-stripping': ('EWF coupled solution OFF', {'film-coupled-solution?': False}),
                  'curvature-smoothing-on-after-stripping': ('Curvature smoothing ON', {'film-smoothing?': True})}


def archive(name, label):
    folder = OUT / name
    dest = folder / 'raw' / label
    dest.mkdir(parents=True, exist_ok=True)
    inputs = (list(folder.glob('*.out')) + list(folder.glob('*.trn'))
              + list(folder.glob('*.json')) + [folder / 'diagnostics.csv'])
    hashes = {}
    for source in inputs:
        if source.name == 'evidence-manifest.json':
            continue
        target = dest / source.name
        if target.exists():
            assert target.read_bytes() == source.read_bytes(), target
        else:
            target.write_bytes(source.read_bytes())
        hashes[source.name] = hashlib.sha256(target.read_bytes()).hexdigest()
    record = dest / 'evidence-manifest.json'
    if record.exists():
        assert json.loads(record.read_text())['sha256'] == hashes
    else:
        record.write_text(json.dumps({'branch': name, 'label': label, 'sha256': hashes}, indent=2) + '\n')
    return dest


def stats(frame):
    result = {}
    for key in ['secondary', 'dpm', 'storage', 'stripping', 'separation', 'outflow']:
        values = frame[key].iloc[-500:].to_numpy()
        n = np.arange(len(values))
        detrended = values - np.polyval(np.polyfit(n, values, 1), n)
        sd = float(np.std(detrended))
        amplitude = float(np.hypot(2*np.mean(detrended*np.cos(2*np.pi*n/4)),
                                  2*np.mean(detrended*np.sin(2*np.pi*n/4))) / np.sqrt(2))
        result[key] = {'mean_kg_s': float(np.mean(values)), 'raw_sd_kg_s': float(np.std(values)),
                       'detrended_sd_kg_s': sd, 'four_step_rms_kg_s': amplitude,
                       'four_step_variance_fraction': min(1, (amplitude/sd)**2) if sd > 1e-12 else 0}
    return result


def native_values(path):
    result = {}
    pattern = re.compile(r'^\s*(\d+)\s+([-+\d.eE]+)\s*$')
    for line in path.read_text().splitlines():
        match = pattern.match(line)
        if match:
            result[int(match[1])] = float(match[2])
    return result


def add_courant(frame, raw):
    courant = native_values(raw / 'p72a-e2.7-ewf-courant-max.out')
    frame = frame.copy()
    frame['courant'] = [courant[int(i)] for i in frame.native_iteration]
    assert np.isfinite(frame.courant).all()
    return frame


def save_figure(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / (name+'.png'), dpi=160)
    fig.savefig(FIG / (name+'.pdf'))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--final', action='store_true')
    args = parser.parse_args()
    FIG.mkdir(exist_ok=True)
    master = json.loads((OUT / 'run-manifest.json').read_text())
    names = ['stripping-on', 'stripping-off']
    if 'coupled-off' in master.get('branches', {}):
        candidate = json.loads((OUT/'coupled-off/run-manifest.json').read_text())
        if candidate['status'] in ['SCREEN_COMPLETE_VERIFIED', 'COMPLETE']:
            names.append('coupled-off')
    sources, summaries, rows = {}, {}, {}
    for name in names:
        raw = OUT / name / 'raw/screen-N38149'
        if not raw.exists():
            raw = archive(name, 'screen-N38149')
        manifest = json.loads((raw / 'run-manifest.json').read_text())
        assert manifest['status'] == 'SCREEN_COMPLETE_VERIFIED'
        frame = pd.read_csv(raw / 'diagnostics.csv')
        assert len(frame) == 1000 and frame.native_iteration.iloc[-1] == 38149
        assert manifest['parent_native_iteration'] == 37149
        rows[name] = add_courant(frame, raw)
        summaries[name] = json.loads((raw / 'analysis-summary.json').read_text())
        summaries[name]['metrics'].update(stats(frame))
        for metric, field in [('peak_velocity_m_s', 'velocity-mag-max'),
                              ('peak_thickness_m', 'thickness-max')]:
            native = native_values(raw / f'p72a-e2.7-ewf-{field}.out')
            summaries[name][metric] = max(native[int(i)] for i in frame.native_iteration)
        sources[name] = str(raw.relative_to(ROOT.parent))
    control = summaries['stripping-on']
    comparisons = {}
    for name in names[1:]:
        ratios = {key: summaries[name]['metrics'][key]['detrended_sd_kg_s'] /
                  max(control['metrics'][key]['detrended_sd_kg_s'], 1e-12)
                  for key in ['secondary', 'storage', 'stripping']}
        comparisons[name] = {'sd_ratios_to_control': ratios,
             'passes_primary_screen': ratios['secondary'] <= .25 and ratios['storage'] <= .25
                                      and summaries[name]['peak_courant'] <= 1}
    result = {'matched_parent': 37149, 'screen_added_time_s': .015,
              'analysis_window_updates': 500, 'branches': summaries,
              'comparison': comparisons,
              'evidence_sources': sources}
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 11})
    fig, axes = plt.subplots(3, 2, figsize=(12, 9), sharex='col', sharey='row')
    for row, (key, title) in enumerate([('secondary', 'Signed secondary-phase source'),
                                      ('stripping', 'Stripping rate'), ('storage', 'Film storage rate')]):
        for col, window in enumerate(['first', 'last']):
            ax = axes[row, col]
            for name, frame in rows.items():
                window_frame = frame.iloc[:64] if window == 'first' else frame.iloc[-64:]
                ax.plot(window_frame.added_film_time_s*1000, window_frame[key], lw=1,
                        marker='.', ms=3, label=PRIMARY_LABELS[name])
            ax.set_title(title+' — '+window+' 64 updates', loc='left')
            ax.set_ylabel('kg/s')
            ax.grid(alpha=.2)
            if row == 0:
                ax.legend(fontsize=8)
            if row == 2:
                ax.set_xlabel('Added EWF time from N37149 (ms)')
    save_figure(fig, 'matched-rates')
    fig, axes = plt.subplots(1, 3, figsize=(11, 4))
    for ax, key, title in zip(axes, ['secondary', 'stripping', 'storage'],
                             ['Secondary-phase source', 'Stripping', 'Film storage']):
        ax.bar(['Control', 'Stripping\nOFF', 'Coupled\nOFF'][:len(names)],
               [summaries[name]['metrics'][key]['detrended_sd_kg_s'] for name in names])
        ax.set_title(title)
        ax.set_ylabel('Detrended standard deviation (kg/s)')
        ax.grid(axis='y', alpha=.2)
    fig.suptitle('Matched first 15 ms; variation in the final 7.5 ms', fontsize=12)
    save_figure(fig, 'variation-comparison')
    force_rows = {}
    reference_raw = OUT / 'stripping-off/raw/rejected-continuation-N39149'
    reference = pd.read_csv(reference_raw/'diagnostics.csv').iloc[-1000:].copy()
    reference['added_film_time_s'] -= .015
    reference = add_courant(reference, reference_raw)
    result['conditional_force_comparisons'] = {}
    for branch, (label, delta) in FORCE_BRANCHES.items():
        if branch not in master.get('branches', {}):
            continue
        folder = OUT/branch
        manifest = json.loads((folder/'run-manifest.json').read_text())
        if manifest['status'] not in ['SCREEN_COMPLETE_VERIFIED', 'COMPLETE', 'RECOVERY_REQUIRED']:
            continue
        raw_label = 'rejected-screen-N39149' if manifest['status'] == 'RECOVERY_REQUIRED' else 'screen-N39149'
        treatment_raw = folder/'raw'/raw_label
        if not treatment_raw.exists():
            treatment_raw = archive(branch, raw_label)
        raw_manifest = json.loads((treatment_raw/'run-manifest.json').read_text())
        assert raw_manifest['parent_native_iteration'] == 38149
        assert raw_manifest['physical_delta'] == delta
        treatment = add_courant(pd.read_csv(treatment_raw/'diagnostics.csv'), treatment_raw)
        assert np.array_equal(reference.native_iteration.to_numpy(), treatment.native_iteration.to_numpy())
        assert np.allclose(reference.added_film_time_s, treatment.added_film_time_s, atol=1e-12)
        assert len(treatment) == 1000
        initial = json.loads((treatment_raw/'loaded-parent.json').read_text())['fields']
        original_initial = json.loads((OUT/'stripping-off/raw/screen-N38149/screen-N38149.json').read_text())['fields']
        assert initial['p72a-e2.7-ewf-film-mass-total'] == original_initial['p72a-e2.7-ewf-film-mass-total']
        record = {'matched_parent': 38149, 'matched_added_time_s': .015, 'physical_delta': delta,
                  'stripping': 'OFF in both', 'reference_source': str(reference_raw.relative_to(ROOT.parent)),
                  'treatment_source': str(treatment_raw.relative_to(ROOT.parent)),
                  'reference_peak_courant': float(reference.courant.max()),
                  'treatment_peak_courant': float(treatment.courant.max()),
                  'passes_courant_screen': bool(treatment.courant.max() <= 1),
                  'treatment_raw_status': raw_manifest['status'],
                  'reference_metrics': stats(reference), 'treatment_metrics': stats(treatment),
                  'reference_film_final_kg': float(reference.film_mass_kg.iloc[-1]),
                  'treatment_film_final_kg': float(treatment.film_mass_kg.iloc[-1])}
        for prefix, raw, frame in [('reference', reference_raw, reference), ('treatment', treatment_raw, treatment)]:
            velocity = native_values(raw/'p72a-e2.7-ewf-velocity-mag-max.out')
            record[prefix+'_peak_velocity_m_s'] = max(velocity[int(i)] for i in frame.native_iteration)
            average_velocity = native_values(raw/'p72a-e2.7-ewf-velocity-mag-awavg.out')
            record[prefix+'_peak_area_average_velocity_m_s'] = max(average_velocity[int(i)] for i in frame.native_iteration)
            thickness = native_values(raw/'p72a-e2.7-ewf-thickness-max.out')
            record[prefix+'_peak_thickness_m'] = max(thickness[int(i)] for i in frame.native_iteration)
            exceeded = frame.loc[frame.courant > 1]
            record[prefix+'_first_courant_over_1_added_time_s'] = float(exceeded.added_film_time_s.iloc[0]) if len(exceeded) else None
        result['conditional_force_comparisons'][branch] = record
        force_rows[label] = (treatment, treatment_raw)
        sources[branch] = str(treatment_raw.relative_to(ROOT.parent))
    if force_rows:
        sources['force-reference'] = str(reference_raw.relative_to(ROOT.parent))
        fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
        for label, (frame, raw) in {'Reference: surface tension + spreading ON': (reference, reference_raw), **force_rows}.items():
            time = frame.added_film_time_s*1000
            axes[0].semilogy(time, frame.courant, lw=1, label=label)
            velocity = native_values(raw/'p72a-e2.7-ewf-velocity-mag-max.out')
            axes[1].semilogy(time, [velocity[int(i)] for i in frame.native_iteration], lw=1, label=label)
            axes[2].semilogy(time, frame.film_mass_kg, lw=1, label=label)
        axes[0].axhline(1, color='gray', ls='--', lw=.8, label='Declared Courant limit')
        axes[0].set_title('Setting contrasts from the same N38149 fields; stripping OFF throughout', loc='left')
        axes[0].set_ylabel('Film Courant (log scale)')
        axes[1].set_ylabel('Maximum film speed (m/s; log)')
        axes[2].set_ylabel('Film mass (kg; log scale)')
        axes[2].set_xlabel('Added EWF time from N38149 (ms)')
        for ax in axes:
            ax.legend(fontsize=8)
            ax.grid(alpha=.2)
        save_figure(fig, 'force-switch-comparison')
    if args.final:
        assert master['status'] == 'COMPLETE'
        name = master['selected_branch']
        manifest = json.loads((OUT/name/'run-manifest.json').read_text())
        assert manifest['status'] == 'COMPLETE'
        raw = archive(name, f"final-N{manifest['verified_native_end']}")
        continuation = add_courant(pd.read_csv(raw/'diagnostics.csv'), raw)
        analysis = json.loads((raw/'analysis-summary.json').read_text())
        if name.endswith('-after-stripping'):
            prefix = rows['stripping-off'].copy()
            continuation['added_film_time_s'] += .015
            prefix['stage'] = 'Stripping OFF'
            continuation['stage'] = 'Stripping + '+FORCE_BRANCHES[name][0].lower()
            accepted = pd.concat([prefix, continuation], ignore_index=True)
            result['accepted_lineage'] = [sources['stripping-off'], str(raw.relative_to(ROOT.parent))]
            assert manifest['parent_native_iteration'] == prefix.native_iteration.iloc[-1]
        else:
            accepted = continuation
            accepted['stage'] = name.replace('-', ' ')
            result['accepted_lineage'] = [str(raw.relative_to(ROOT.parent))]
        assert np.all(np.diff(accepted.native_iteration) == 1)
        assert abs(accepted.added_film_time_s.iloc[-1]-.05) < 1e-10
        result.update(selected_branch=name, continuation=analysis,
                      total_accepted_added_film_time_s=float(accepted.added_film_time_s.iloc[-1]),
                      total_accepted_updates=len(accepted), accepted_peak_courant=float(accepted.courant.max()))
        accepted.to_csv(OUT/'accepted-continuation.csv', index=False)
        nominal = accepted.iloc[:-1].copy()
        assert np.allclose(np.diff(np.r_[0, nominal.added_film_time_s]), 15e-6, rtol=0, atol=1e-12)
        complete_groups = len(nominal)//4
        averaged = nominal.iloc[:complete_groups*4].copy()
        averaged['group'] = np.arange(len(averaged))//4
        means = averaged.groupby('group', sort=False)[['secondary','storage','stripping','separation','dpm','outflow']].mean()
        means['added_film_time_s'] = averaged.groupby('group', sort=False).added_film_time_s.max()
        means.to_csv(OUT/'four-update-means.csv', index=False)
        result['diagnostic_averaging'] = {'updates_per_group':4, 'period_s':60e-6,
            'complete_groups':complete_groups, 'excluded_updates':len(accepted)-complete_groups*4,
            'purpose':'Expose slower rate trend; raw rates retained; not a solver repair or convergence test'}
        sources['selected-final'] = str(raw.relative_to(ROOT.parent))
        fig, axes = plt.subplots(4, 1, figsize=(10, 11), sharex=True)
        for stage, frame in accepted.groupby('stage', sort=False):
            axes[0].plot(frame.added_film_time_s*1000, frame.film_mass_kg, lw=1, label=stage)
            axes[1].plot(frame.added_film_time_s*1000, frame.courant, lw=1, label=stage)
        axes[0].set_ylabel('Film mass (kg)')
        axes[0].set_title('Accepted 50 ms continuation under frozen bulk; rejected interval excluded', loc='left')
        axes[0].legend(fontsize=8)
        axes[1].set_ylabel('Film Courant')
        for key, label in [('secondary','Secondary-phase source'), ('storage','Storage'), ('outflow','Wall film outflow')]:
            line, = axes[2].plot(accepted.added_film_time_s*1000, accepted[key], lw=.7, alpha=.3, label=label+' (raw)')
            if key != 'outflow':
                axes[2].plot(means.added_film_time_s*1000, means[key], color=line.get_color(), lw=1.1, label=label+' (4-update mean)')
        axes[2].set_ylabel('kg/s')
        axes[2].legend(fontsize=8, ncol=2)
        for key, label in [('stripping','Stripping'), ('separation','Edge separation'), ('dpm','DPM film source')]:
            line, = axes[3].plot(accepted.added_film_time_s*1000, accepted[key], lw=.7, alpha=.3, label=label+' (raw)')
            axes[3].plot(means.added_film_time_s*1000, means[key], color=line.get_color(), lw=1.1, label=label+' (4-update mean)')
        axes[3].set_ylabel('kg/s')
        axes[3].legend(fontsize=8, ncol=2)
        axes[3].set_xlabel('Accepted added EWF time from N37149 (ms)')
        for ax in axes:
            if name.endswith('-after-stripping'):
                ax.axvline(15, color='gray', ls='--', lw=.8)
            ax.grid(alpha=.2)
        save_figure(fig, 'selected-continuation')
    (OUT/'comparison-summary.json').write_text(json.dumps(result, indent=2)+'\n')
    (OUT/'figure-manifest.json').write_text(json.dumps({
        'new_solve_calls': 0, 'native_evidence_sources': sources,
        'figures': [str(p.relative_to(ROOT.parent)) for p in FIG.iterdir()]}, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ['comparison', 'conditional_force_comparisons', 'selected_branch', 'continuation'] if key in result}, indent=2))


if __name__ == '__main__':
    main()
