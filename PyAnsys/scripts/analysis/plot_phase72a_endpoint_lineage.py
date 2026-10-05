"""Plot the evidenced field lineage of N45606 without joining sibling runs.

Inputs are native report files, transcripts, saved residual buffers and existing
paired endpoint receipts, including the verified OneDrive history upload. Older
compressed HDF residual samples are excluded; only the consecutive suffix is used.
"""
from pathlib import Path
import csv
import hashlib
import json
import re

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'PyAnsys/output/phase72a-lineage-N45606/20261005'
CLOUD = Path.home() / 'Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts'
BASE = ROOT / 'PyAnsys/output'
ADAPT = BASE / 'phase72a-adaptive-server1/20261005'
E27 = BASE / 'phase72a_ewf_student_e27_run_20260923T071523Z/E2.7'
CONT = BASE / 'phase72a_ewf_server1_e27_cont5000_20260923T102912Z'
UPLOAD = OUT / 'raw/history-recovery'
CONTACT = UPLOAD / 'PyAnsys/output/phase72a-contact-absorber-e27-restart/20261003T032636Z'
REPLAY = UPLOAD / 'PyAnsys/output/phase72a-contact-absorber-local-20000/20261004T081120Z'
NAMES = ['continuity', 'x-velocity', 'y-velocity', 'z-velocity', 'k', 'epsilon', 'vf-phase-2']
ROW = re.compile(r'^\s*(\d+)\s+' + r'\s+'.join([r'([\d.+-]+e[+-]\d+)'] * 7), re.M)
SUB = re.compile(r'sub-iteration: (\d+) residual - h: ([\deE.+-]+); u: ([\deE.+-]+); v: ([\deE.+-]+)')
REPORTS = {
    'bulk_liquid_kg': 'v2-total-liquid-mass',
    'phase2_steamoutlet_signed_kg_s': 'v2-flux-phase2-steamoutlet',
    'film_kg': 'p72a-e2.7-ewf-film-mass-total',
    'accretion_kg_s': 'p72a-e2.7-ewf-secondary-phase-mass-total',
    'cumulative_drainage_kg': 'p72a-e2.7-ewf-outflow-mass-total',
}
SOURCES = []
EVENTS = [
    (1580, 'A', 'Corrected inlet ramp starts; quarter-feed hold ends'),
    (3580, 'B', 'Full feed; SIMPLE to Coupled, Global Time Step'),
    (5586, 'C', 'E2.7 EWF phase accretion and coupled film ON; fixed 10 us'),
    (8586, 'D', 'E2.7 transferred to Server 1 and repartitioned; +5000, no model change'),
    (13586, 'E', 'Original E2.7 fields retained; R3 + corrected contact absorber; fixed 1 us'),
    (17586, 'F', 'Independent local four-rank replay begins; scientific settings retained'),
    (33586, 'G', 'Server 1; adaptive film ON, Courant target 0.05'),
]


def load(path):
    return json.loads(path.read_text())


def record_source(path, role):
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    SOURCES.append({'path': str(path), 'role': role, 'sha256': digest.hexdigest()})


def out_file(path):
    result = {}
    for line in path.read_text().splitlines():
        a = line.split()
        if len(a) == 2 and a[0].isdigit():
            i, v = int(a[0]), float(a[1])
            if i in result and result[i] != v:
                raise ValueError(f'Conflicting report duplicate {path} N{i}')
            result[i] = v
    return result


def add_reports(dest, path):
    h = load(path)
    record_source(path, 'selected lineage report history')
    for key, name in REPORTS.items():
        if name not in h:
            continue
        for i, v in zip(h[name]['iterations'], h[name]['values']):
            if i in dest[key] and not np.isclose(dest[key][i], v, rtol=1e-9, atol=1e-9):
                raise ValueError(f'Conflicting overlap {key} N{i}')
            dest[key][i] = v


def add_transcript(dest, film, path, low, high, marker=None):
    text = path.read_text()
    record_source(path, 'selected lineage residual transcript')
    if marker:
        pos = text.find(marker)
        if pos < 0:
            raise ValueError('Required parent-load marker missing')
        text = text[pos:]
    pending = []
    for line in text.splitlines():
        sub = SUB.search(line)
        if sub:
            pending.append((int(sub[1]), *[float(v) for v in sub.groups()[1:]]))
        m = ROW.match(line)
        if m:
            i = int(m[1])
            if low <= i <= high:
                dest[i] = [float(v) for v in m.groups()[1:]]
                if pending:
                    film[i] = {'last': pending[-1][1:], 'peak': np.max([v[1:] for v in pending], axis=0).tolist(), 'subiterations': pending[-1][0]}
            pending = []


def verify_upload(folder, monitor, low, high):
    """Require all 29 JSON exports to match their uploaded native .out files."""
    p = next(folder.glob('*histories.json'))
    h = load(p)
    ids = list(range(low, high + 1))
    if len(h) != 29:
        raise ValueError('Uploaded report count differs from 29')
    for name, record in h.items():
        native = monitor / f'{name}.out'
        raw = out_file(native)
        if record['iterations'] != ids or sorted(raw) != ids:
            raise ValueError(f'Incomplete uploaded history: {name}')
        if not np.allclose(record['values'], [raw[i] for i in ids], rtol=1e-12, atol=1e-12):
            raise ValueError(f'Uploaded JSON/native report mismatch: {name}')
        record_source(native, 'uploaded native report; independently agrees with JSON export')
    return p, {'native_range': [low, high], 'report_count': 29, 'points_each': len(ids),
               'JSON_against_native_out': 'PASS_ALL_29', 'history_file': str(p)}


def verify_fixed_clock(path, low, high, clock):
    text = path.read_text()
    pending = None
    observed = {}
    pattern = re.compile(r'Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+),')
    for line in text.splitlines():
        m = pattern.search(line)
        if m:
            pending = tuple(float(v) for v in m.groups())
        row = ROW.match(line)
        if row:
            i = int(row[1])
            if pending and low < i <= high:
                if abs(pending[0] - clock[i]) > 5.1e-8 or abs(pending[1] - 1e-6) > 1e-15:
                    raise ValueError(f'Uploaded native fixed clock differs at N{i}')
                observed[i] = pending
            pending = None
    if set(observed) != set(range(low + 1, high + 1)):
        raise ValueError('Uploaded native film-clock coverage is incomplete')
    return {'stream_updates': len(observed), 'fixed_step_s': 1e-6, 'clock_check': 'PASS_ALL_UPDATES'}


def consecutive_runs(ids):
    ids = np.asarray(sorted(ids), dtype=int)
    if not len(ids):
        return []
    return np.split(ids, np.where(np.diff(ids) != 1)[0] + 1)


def plot_records(ax, records, **kwargs):
    for run in consecutive_runs(records):
        label = kwargs.pop('label', None)
        ax.plot(run, [records[int(i)] for i in run], label=label, **kwargs)


def mark(ax, limits=(0, 45606), gaps=False):
    ax.set_xlim(*limits)
    for i, tag, _ in EVENTS:
        if limits[0] <= i <= limits[1]:
            ax.axvline(i, color='#666666', ls='--', lw=.8, alpha=.65)
            ax.text(i + 170, .98, tag, transform=ax.get_xaxis_transform(), va='top', fontsize=9,
                    bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .8})
    if gaps:
        ax.axvspan(13586, 33586, color='#888888', alpha=.09)
    ax.grid(alpha=.2)
    ax.set_xlabel('Native carrier iteration (not elapsed physical time)')


def save(fig, name, pdf):
    fig.savefig(OUT / f'{name}.png', dpi=180)
    fig.savefig(OUT / f'{name}.pdf')
    pdf.savefig(fig)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reports = {k: {} for k in REPORTS}
    for key in list(REPORTS)[:2]:
        p = OUT / 'recovered-r0-reports' / f'P71A-R0-SMOOTH-CONTROL-{REPORTS[key]}.out'
        reports[key].update(out_file(p));record_source(p, 'R0 native N1-N3580 report recovered from Server 1')
    for run in [3, 4]:
        add_reports(reports, BASE / f'phase71a_r0_control_run{run}/report-histories-batched.json')
    for folder in [E27, CONT]:
        add_reports(reports, folder / 'report-histories.json')
    contact_monitor = UPLOAD / 'FluentDirectUse/Phase72A-ContactAbsorber/20261002T222617Z/e27-restart4000-20261003T032636Z/monitors'
    replay_monitor = UPLOAD / 'FluentDirectUse/Phase72A-ContactAbsorber/local-replay20000-20261004T081120Z/monitors'
    contact_history, contact_proof = verify_upload(CONTACT, contact_monitor, 13586, 17586)
    replay_history, replay_proof = verify_upload(REPLAY, replay_monitor, 17586, 33586)
    contact_manifest, replay_manifest = load(CONTACT / 'run-manifest.json'), load(REPLAY / 'run-manifest.json')
    if not contact_manifest['original_field_restore_verified']:
        raise ValueError('Original E2.7 field restoration is unverified')
    for kind in ['case', 'data']:
        if contact_manifest['final_pair'][kind + '_sha256'] != replay_manifest['parent_pair'][kind + '_sha256']:
            raise ValueError('Contact/replay pair lineage differs')
    if replay_manifest['scientific_settings_changed']:
        raise ValueError('Unexpected replay settings change')
    for path in [CONTACT / 'run-manifest.json', REPLAY / 'run-manifest.json', UPLOAD.parent / 'history-recovery-import.json']:
        record_source(path, 'history-upload identity and field lineage proof')
    add_reports(reports, contact_history)
    add_reports(reports, replay_history)
    for key, name in REPORTS.items():
        p = ADAPT / 'recovered-N45606/reports' / f'{name}.out'
        reports[key].update(out_file(p));record_source(p, 'adaptive N33586-N45606 report')
    # Actual common parent at N17586; later Server 1 rows are a sibling branch.
    sibling = {}
    for key, name in REPORTS.items():
        p = OUT / 'server1-sibling-reports' / f'{name}.out'
        sibling[key] = out_file(p)
        reports[key][17586] = sibling[key][17586]
        record_source(p, 'separate Server 1 sibling; only N17586 parent belongs to selected lineage')
    for i in range(1, 5587):
        reports['film_kg'][i] = 0.0  # EWF explicitly OFF in this parent segment.
    ids = np.arange(1, 45607)
    # Film clock starts with E2.7. No bulk pseudo-time is converted to film time.
    clock = {i: (i - 5586) * 1e-5 for i in range(5586, 13587)}
    clock.update({i: .08 + (i - 13586) * 1e-6 for i in range(13586, 33587)})
    fp = ADAPT / 'recovered-N45606/film-history.csv'
    for row in csv.DictReader(fp.open()):
        clock[int(row['native_iteration'])] = float(row['native_film_clock_s'])
    record_source(fp, 'exact adaptive clock previously validated against native endpoint')
    contact_proof.update(verify_fixed_clock(CONTACT / 'transcript.txt', 13586, 17586, clock))
    replay_proof.update(verify_fixed_clock(REPLAY / 'transcript.txt', 17586, 33586, clock))
    drainage = {}
    for run in consecutive_runs(reports['cumulative_drainage_kg']):
        for i in run[1:]:
            if i in clock and i-1 in clock:
                drainage[int(i)] = (reports['cumulative_drainage_kg'][int(i)] - reports['cumulative_drainage_kg'][int(i-1)]) / (clock[int(i)] - clock[int(i-1)])
    residuals, film = {}, {}
    add_transcript(residuals, film, OUT / 'recovered-r0-transcript-extract.txt', 1, 5586,
                   '20260922T153000Z\\P71A-R0-SMOOTH-CONTROL-prepared.dat.h5')
    add_transcript(residuals, film, BASE / 'phase71a_r0_control_run3/transcript.txt', 3580, 3749)
    for run in [3, 4]:
        p = BASE / f'phase71a_r0_control_run{run}/residuals-batched-resume.json'
        j = load(p);record_source(p, 'native carrier residual export')
        for n, i in enumerate(j['iterations']):
            residuals[i] = [j['series'][name][n] for name in NAMES]
    for folder, lo, hi in [(E27, 5586, 8586), (CONT, 8586, 13586)]:
        add_transcript(residuals, film, folder / 'transcript-native-solve.txt', lo, hi)
    add_transcript(residuals, film, CONTACT / 'transcript.txt', 13586, 17586)
    add_transcript(residuals, film, REPLAY / 'transcript.txt', 17586, 33586)
    # The independent native transcript must agree with the captured replay stream.
    native_replay_residuals, native_replay_film = {}, {}
    native_replay_path = UPLOAD / 'FluentDirectUse/fluent-20261004-211726-40976.trn'
    add_transcript(native_replay_residuals, native_replay_film, native_replay_path, 17587, 33586)
    for i, values in native_replay_residuals.items():
        if not np.allclose(values, residuals[i], rtol=1e-12, atol=1e-12):
            raise ValueError('Replay native/client residuals differ')
    if set(native_replay_film) != set(range(17587, 33587)):
        raise ValueError('Native replay film residual coverage differs')
    for i in native_replay_film:
        if native_replay_film[i] != film[i]:
            raise ValueError('Replay native/client film subiteration summaries differ')
    replay_proof['native_transcript_against_client'] = 'PASS_16000_UPDATES'
    add_transcript(residuals, film, ADAPT / 'adaptive-smoke-transcript.txt', 33586, 33606)
    for p in sorted(ADAPT.glob('batch-*.txt')):
        lo, hi = map(int, re.findall(r'N(\d+)', p.name))
        add_transcript(residuals, film, p, lo, hi)
    # HDF uses raw residual / row normalization. Older compressed history entries
    # are interval reductions, not exact samples at the stored coordinate.
    saved = [
        CLOUD / 'Phase72A/ContactAbsorber/1us10000/20261003T070351Z/input-N17586.dat.h5',
        CLOUD / 'Phase72A/ContactAbsorber/local20000/20261004T081120Z/block-N33586.dat.h5',
        CLOUD / 'Phase72A/ContactAbsorber/adaptive-20261005/N45606/adaptive-recovered-N45606.dat.h5',
    ]
    hdf_receipts = []
    hdf_only = set()
    for p in saved:
        record_source(p, 'selected lineage saved data; final consecutive residual suffix only')
        with h5py.File(p) as f:
            groups = {name: g for phase in f['results/residuals'].values() for name, g in phase.items()}
            ii = groups['continuity']['iterations'][:].astype(int)
            last_gap = np.where(np.diff(ii) != 1)[0]
            start = int(last_gap[-1] + 2) if len(last_gap) else 0
            use = ii[start:]
            columns = []
            for name in NAMES:
                if not np.array_equal(groups[name]['iterations'][:].astype(int), ii):
                    raise ValueError('HDF residual coordinates differ by equation')
                a = groups[name]['data'][:]
                if not np.all(a[start:, 1] > 0):
                    raise ValueError('Invalid HDF scaling denominator')
                columns.append(a[start:, 0] / a[start:, 1])
            values = np.asarray(columns).T
            overlaps = []
            for i, v in zip(use, values):
                if i in residuals:
                    error = max(abs(v / np.asarray(residuals[int(i)]) - 1))
                    if error > 6e-5:
                        raise ValueError(f'HDF suffix differs from printed residual at N{i}: {error}')
                    overlaps.append(float(error))
                else:
                    residuals[int(i)] = v.tolist();hdf_only.add(int(i))
            hdf_receipts.append({'data': str(p), 'used_range': [int(use[0]), int(use[-1])], 'used_points': len(use),
                'discarded_compressed_points': start, 'printed_overlap_points': len(overlaps),
                'max_relative_overlap_error': max(overlaps) if overlaps else None,
                'endpoint_normalization': {name: float(groups[name]['data'][-1, 1]) for name in NAMES}})
    residual_gaps = []
    for run in consecutive_runs(set(ids) - set(residuals)):
        residual_gaps.append([int(run[0]), int(run[-1])])
    for key in ['bulk_liquid_kg', 'phase2_steamoutlet_signed_kg_s', 'film_kg']:
        if sorted(reports[key]) != ids.tolist():
            raise ValueError(f'Unexpected remaining history gap for {key}')
    if set(residuals) != set(ids):
        raise ValueError('Unexpected remaining carrier residual gap')
    if set(film) != set(range(5587, 45374)):
        raise ValueError('Unexpected film residual gap before lost final adaptive tail')
    film_quality = []
    for low, high, label in [(5586, 13586, 'E2.7 fixed 10 us'), (13586, 17586, 'Contact restart fixed 1 us'),
                              (17586, 33586, 'Local replay fixed 1 us'), (33586, 45373, 'Adaptive available transcript')]:
        selected = {i: v for i, v in film.items() if low < i <= high}
        high_ids = [i for i, v in selected.items() if max(v['last']) > 1]
        passed = sum(max(v['last']) <= 1e-5 for v in selected.values())
        film_quality.append({'segment': label, 'native_range': [low + 1, high], 'updates': len(selected),
            'updates_all_final_at_or_below_1e_minus_5': passed, 'fraction_all_final_at_or_below_stop': passed / len(selected),
            'updates_any_final_above_one': len(high_ids),
            'ranges_any_final_above_one': [[int(r[0]), int(r[-1])] for r in consecutive_runs(high_ids)]})
    film_ids = np.arange(13586, 45607)
    native_time = np.asarray([clock[int(i)] for i in film_ids])
    film_mass = np.asarray([reports['film_kg'][int(i)] for i in film_ids])
    accretion = np.asarray([reports['accretion_kg_s'][int(i)] for i in film_ids])
    cumulative_out = np.asarray([reports['cumulative_drainage_kg'][int(i)] for i in film_ids])
    accreted = float(np.sum(accretion[1:] * np.diff(native_time)))
    stored = float(film_mass[-1] - film_mass[0])
    drained = float(cumulative_out[-1] - cumulative_out[0])
    elapsed = float(native_time[-1] - native_time[0])
    development_summary = {'native_range': [13586, 45606], 'updates': 32020, 'added_film_time_s': elapsed,
        'film_mass_start_kg': float(film_mass[0]), 'film_mass_end_kg': float(film_mass[-1]),
        'film_mass_gain_kg': stored, 'accreted_kg': accreted, 'drained_kg': drained,
        'film_ledger_error_percent': 100 * abs(stored + drained - accreted) / accreted,
        'film_residual_quality': film_quality,
        'claim_limit': 'Film-side ledger only; high final inner residuals limit numerical adequacy even with small mass ledger error'}
    (OUT / 'corrected-film-development-summary.json').write_text(json.dumps(development_summary, indent=2) + '\n')
    coverage = {'report_gap': [], 'history_recovery': [contact_proof, replay_proof],
        'carrier_residual_gaps': residual_gaps, 'carrier_residual_points': len(residuals),
        'hdf_added_residual_points': len(hdf_only), 'hdf_suffix_validation': hdf_receipts,
        'normalization_ratio_N45606_to_N33586': {
            name: hdf_receipts[-1]['endpoint_normalization'][name] / hdf_receipts[-2]['endpoint_normalization'][name]
            for name in NAMES},
        'film_residual_ranges': [[int(r[0]), int(r[-1])] for r in consecutive_runs(film)],
        'film_subiteration_limit': 'Final subiteration and peak per carrier update plotted; all subiterations exported in native source transcripts',
        'film_residual_quality': film_quality,
        'events': [{'iteration': i, 'label': tag, 'change': text} for i, tag, text in EVENTS],
        'lineage': 'Prepared v2 -> R0 hold/ramp -> R0 Coupled -> E2.7 -> E2.7+5000 -> original-field contact restart -> local four-rank replay -> Server 1 adaptive N45606',
        'excluded': ['student independent v2 inlet ramp', 'old-absorber coarse R3/R4/R5', 'contact 10 us runaway', 'Server 1 N17586-N23586 sibling field continuation'],
        'missing': ['EWF subiteration/event transcript N45374-N45606'],
        'retrieval_status': 'UPLOADED_LOCAL_HISTORIES_VERIFIED_AND_JOINED',
        'film_residual_spikes': {
            f'{lo}-{hi}': {name: {'iteration': max((i for i in film if lo < i <= hi), key=lambda i: film[i]['last'][j]),
                                  'value': max(film[i]['last'][j] for i in film if lo < i <= hi)}
                            for j, name in enumerate(['h', 'u', 'v'])}
            for lo, hi in [(5586, 13586), (13586, 17586), (17586, 33586), (33586, 45373)]},
        'sources': SOURCES}
    (OUT / 'lineage-manifest.json').write_text(json.dumps(coverage, indent=2) + '\n')
    with (OUT / 'selected-lineage-histories.csv').open('w', newline='') as f:
        w = csv.writer(f);w.writerow(['native_iteration', *REPORTS, 'bulk_plus_ewf_kg', 'drainage_kg_s', 'native_film_clock_s', 'report_evidence'])
        for i in ids:
            vals = [reports[k].get(int(i), '') for k in REPORTS]
            combined = reports['bulk_liquid_kg'].get(int(i), np.nan) + reports['film_kg'].get(int(i), np.nan)
            w.writerow([i, *vals, '' if np.isnan(combined) else combined, drainage.get(int(i), ''), clock.get(int(i), ''),
                        'uploaded native report' if 13586 < i <= 33586 else 'native history'])
    with (OUT / 'carrier-residuals.csv').open('w', newline='') as f:
        w = csv.writer(f);w.writerow(['native_iteration', *NAMES, 'source_kind'])
        for i in sorted(residuals):
            w.writerow([i, *residuals[i], 'saved exact consecutive suffix' if i in hdf_only else 'native transcript/export'])
    with (OUT / 'film-residuals.csv').open('w', newline='') as f:
        w = csv.writer(f);w.writerow(['native_iteration', 'h_last', 'u_last', 'v_last', 'h_peak', 'u_peak', 'v_peak', 'last_subiteration'])
        for i, v in sorted(film.items()):
            w.writerow([i, *v['last'], *v['peak'], v['subiterations']])
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 12})
    with PdfPages(OUT / 'case-history-N45606.pdf') as pdf:
        fig, ax = plt.subplots(4, 1, figsize=(14, 13), layout='constrained')
        bulk = reports['bulk_liquid_kg']
        combined = {i: v + reports['film_kg'][i] for i, v in bulk.items()}
        plot_records(ax[0], bulk, color='#276B9D', lw=.9, label='Bulk phase-2 inventory')
        plot_records(ax[0], combined, color='#9B4E85', lw=.9, label='Bulk + EWF inventory')
        ax[0].set_ylabel('Liquid inventory (kg)');ax[0].legend(loc='upper right')
        plot_records(ax[1], reports['phase2_steamoutlet_signed_kg_s'], color='#276B9D', lw=.8)
        ax[1].set_ylabel('Phase-2 steamoutlet\nflux (kg/s, signed)')
        plot_records(ax[2], reports['film_kg'], color='#276B9D', lw=1)
        ax[2].set_ylabel('EWF film inventory (kg)')
        plot_records(ax[3], reports['accretion_kg_s'], color='#276B9D', lw=.7, label='Native accretion rate')
        plot_records(ax[3], drainage, color='#B87520', lw=.6, label='Drainage: per-update cumulative outflow difference / actual film step')
        ax[3].set_ylabel('Film mass rate (kg/s)');ax[3].legend(loc='upper right', fontsize=9)
        for a, key in zip(ax[1:], ['phase2_steamoutlet_signed_kg_s', 'film_kg', 'accretion_kg_s']):
            a.scatter([17586], [reports[key][17586]], marker='D', s=30, color='#276B9D', zorder=5)
        ax[0].scatter([17586], [bulk[17586]], marker='D', s=30, color='#276B9D', zorder=5)
        ax[0].scatter([17586], [combined[17586]], marker='D', s=30, color='#9B4E85', zorder=5)
        for a in ax: mark(a)
        fig.suptitle('History of the field branch leading to N45606\nA: inlet ramp  B: Coupled  C: EWF 10 µs  D: transfer/+5000  E: R3/contact + 1 µs  F: local replay  G: adaptive', fontsize=13)
        save(fig, 'entire-liquid-film-history', pdf)
        fig, ax = plt.subplots(3, 1, figsize=(14, 11), layout='constrained')
        colors = plt.cm.tab10.colors
        for j, name in enumerate(NAMES):
            a = ax[0] if j in [0, 6] else ax[1] if j in [1, 2, 3] else ax[2]
            plot_records(a, {i: v[j] for i, v in residuals.items()}, color=colors[j], lw=.55, label=name)
        for a in ax:
            a.set_yscale('log');a.set_ylabel('Fluent scaled residual');a.legend(loc='upper right');mark(a)
            for lo, hi in residual_gaps: a.axvspan(lo, hi, color='#888888', alpha=.12)
        fig.suptitle('Complete carrier residual history on the selected lineage — N1 to N45606\nUploaded transcripts fill local segments; saved data recovers the final 233 carrier residuals', fontsize=14)
        save(fig, 'entire-carrier-residuals', pdf)
        fig, ax = plt.subplots(2, 1, figsize=(14, 8), layout='constrained')
        for j, name in enumerate(['h', 'u', 'v']):
            for a, kind in zip(ax, ['last', 'peak']):
                plot_records(a, {i: v[kind][j] for i, v in film.items()}, color=colors[j], lw=.6, label=name)
        for a, title in zip(ax, ['Residual at final film subiteration of each carrier update', 'Maximum residual over all film subiterations in each carrier update']):
            a.set_yscale('log');a.set_ylabel('Native EWF residual');a.set_title(title);a.legend(loc='upper right');mark(a)
            a.axvspan(45374, 45606, color='#888888', alpha=.2)
        fig.suptitle('EWF residual history — h: thickness, u/v: film momentum\nComplete N5587–N45373; final 233 film subiteration records unavailable', fontsize=14)
        save(fig, 'entire-film-residuals', pdf)
        fig, ax = plt.subplots(3, 1, figsize=(13, 10), layout='constrained')
        for j, name in enumerate(NAMES):
            plot_records(ax[0], {i: v[j] for i, v in residuals.items() if i <= 6000}, color=colors[j], lw=.55, label=name)
        ax[0].set_yscale('log');ax[0].set_ylabel('Scaled residual');ax[0].legend(ncol=4, fontsize=8);mark(ax[0], (0, 6000))
        plot_records(ax[1], bulk, color='#276B9D', lw=.8);ax[1].set_ylabel('Bulk liquid (kg)');mark(ax[1], (0, 6000))
        cmd = OUT / 'recovered-r0-reports/P71A-R0-SMOOTH-CONTROL-v2-command.out'
        inlet = out_file(cmd);inlet = {i: v for i, v in inlet.items() if i > 1}
        plot_records(ax[2], inlet, color='#276B9D', lw=1, label='Reported liquid inlet / absorber command')
        ax[2].plot([3580, 5586], [116.92, 116.92], color='#276B9D', lw=1)
        ax[2].set_ylabel('Liquid feed command (kg/s)');ax[2].legend();mark(ax[2], (0, 6000))
        fig.suptitle('Early field-development detail\n25% inlet hold → corrected 2,000-update ramp → Coupled → EWF', fontsize=14)
        save(fig, 'early-development-detail', pdf)
        fig, ax = plt.subplots(2, 1, figsize=(13, 7), layout='constrained')
        for a, key, ylabel in [(ax[0], 'film_kg', 'Film inventory (kg)'), (ax[1], 'phase2_steamoutlet_signed_kg_s', 'Signed liquid outlet (kg/s)')]:
            plot_records(a, reports[key], color='#276B9D', lw=1, label='Selected lineage: local replay → N45606')
            plot_records(a, sibling[key], color='#B87520', lw=.8, label='Separate Server 1 N17586–N23586 branch')
            a.set_ylabel(ylabel);a.legend(fontsize=9);mark(a, (13586, 45606))
            a.scatter([17586], [reports[key][17586]], color='#276B9D', s=25, marker='D', zorder=4)
        ax[0].set_ylim(5.8, 6.42)
        ax[1].set_ylim(-3.72, -3.64)
        fig.suptitle('Branch check: the earlier Server 1 continuation is separate\nBlue uses the recovered local replay; orange uses the Server 1 sibling', fontsize=14)
        save(fig, 'separate-server1-branch', pdf)
        fig, ax = plt.subplots(3, 1, figsize=(13, 10), layout='constrained')
        time_ms = 1000 * (native_time - .08)
        ax[0].plot(time_ms, film_mass, color='#276B9D')
        ax[0].set_ylabel('EWF film inventory (kg)')
        ax[1].plot(time_ms, accretion, color='#276B9D', lw=.6, label='Native accretion')
        native_drain_rate = np.r_[np.nan, np.diff(cumulative_out) / np.diff(native_time)]
        ax[1].plot(time_ms, native_drain_rate, color='#B87520', lw=.6, label='Native drainage increment / actual film step')
        ax[1].set_ylabel('Film mass rate (kg/s)');ax[1].legend(fontsize=9)
        native_final_h = {i: v['last'][0] for i, v in film.items() if i >= 13587}
        for run in consecutive_runs(native_final_h):
            ax[2].plot([1000 * (clock[int(i)] - .08) for i in run], [native_final_h[int(i)] for i in run], color='#276B9D', lw=.65)
        ax[2].set_yscale('log');ax[2].set_ylabel('Final EWF thickness residual')
        ax[2].axhline(1e-5, color='#777777', ls=':', label='Recorded subiteration stop value 1e-5')
        ax[2].legend(fontsize=9)
        for a in ax:
            a.axvline(4, color='#666666', ls='--', lw=.8)
            a.axvline(20, color='#666666', ls='--', lw=.8)
            a.grid(alpha=.2);a.set_xlim(0, time_ms[-1]);a.set_xlabel('Added film time since corrected E2.7 restart (ms)')
            a.text(4.3, .97, 'Local replay', transform=a.get_xaxis_transform(), va='top', fontsize=9)
            a.text(20.3, .97, 'Adaptive', transform=a.get_xaxis_transform(), va='top', fontsize=9)
        fig.suptitle('Corrected contact film development — complete inventory and rate histories\nSmooth mass growth can coexist with high final film residuals', fontsize=14)
        save(fig, 'corrected-film-development', pdf)
    print(json.dumps({k: v for k, v in coverage.items() if k not in ['sources', 'events']}, indent=2))


if __name__ == '__main__':
    main()
