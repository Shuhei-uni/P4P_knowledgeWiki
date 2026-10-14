"""OFF/ON M04 diagnostic evidence; native failure is not qualification.

Read immutable text copies only. Keep real iteration coordinates and failure
tails; distinguish the ON restart from the original OFF continuation.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'PyAnsys/output/phase10-single-inlet-mesh-convergence'
DEST = OUT / 'bodyforce-BF01-evidence'
RAW = DEST / 'raw'
OFF = OUT / 'divergence-diagnosis-20261011/raw/M04'
EQUATIONS = ['continuity', 'x-velocity', 'y-velocity', 'z-velocity', 'k', 'epsilon', 'vf-phase-2']


def report(path):
    rows = {}
    for line in path.read_text().splitlines():
        try:
            values = [float(x) for x in line.split()]
        except ValueError:
            continue
        if len(values) != 2:
            continue
        n, value = values
        assert n.is_integer() and math.isfinite(value), str(path)
        assert int(n) not in rows, 'Duplicate report coordinate: '+str(path)
        if n >= 3000:
            rows[int(n)] = value
    assert rows and list(rows) == sorted(rows), str(path)
    return rows


def residuals(paths):
    rows = {}
    for path in paths:
        for line in path.read_text().splitlines():
            parts = line.split()
            if len(parts) < 9 or not parts[0].isdigit():
                continue
            try:
                values = [float(x) for x in parts[1:8]]
            except ValueError:
                continue
            n = int(parts[0])
            assert all(math.isfinite(x) for x in values)
            if n < 3000:
                continue
            if n in rows:
                assert rows[n] == values, 'Conflicting residual overlap'
            rows[n] = values
    assert rows
    return dict(sorted(rows.items()))


def main():
    m = json.loads((RAW/'manifest.json').read_text())
    proof = json.loads((DEST/'terminal-proof.json').read_text())
    assert m['actual_iteration'] == 3567 and m['solved_updates'] == 567
    assert m['status'] == 'NUMERICAL_FAILURE_UNQUALIFIED'
    assert proof['owned_controller_absent'] and not proof['workers']
    assert proof['flag_readback'] == {'primary': True, 'expert': True}
    sources = {
        'OFF': [RAW/'OFF-M04-solve-to-N4000.trn'],
        'ON': [RAW/'smoke-to-N3005.trn', RAW/'solve-to-N4000.trn'],
    }
    res = {label: residuals(paths) for label, paths in sources.items()}
    reports = {}
    provenance = []
    names = ['p10-speed-max', 'p10-mass-phase-2', 'p10-flux-phase-2-steamoutlet',
             'p10-flux-phase-1-steamoutlet', 'p10-flux-mixture-steamoutlet']
    for label, folder in [('OFF', OFF), ('ON', RAW)]:
        reports[label] = {name: report(folder/(name+'.out')) for name in names}
        for path in sources[label]+[folder/(name+'.out') for name in names]:
            provenance.append({'case':label, 'path':str(path.relative_to(ROOT)),
                               'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    summary = {'experiment':'BF01', 'mesh':'M04', 'cells':946967,
               'ON_restart_iteration':3000, 'requested_ON_horizon':4000,
               'ON_actual_failed_iteration':3567, 'ON_new_updates':567,
               'OFF_actual_failed_iteration':3911, 'last_verified_ON_pair':3005,
               'last_verified_ON_pair_hashes':m['checkpoints'][-1]['pair'],
               'primary_and_expert_ON_verified':True, 'other_scientific_state_verified':True,
               'controller_exited':True, 'campaign_spend_lower_bound':22302+567,
               'campaign_spend_upper_bound':22992+567,
               'ON_N4000_final_500_evidence':'UNAVAILABLE_N4000_NOT_REACHED',
               'qualification':False,
               'observation':'The ON restart failed before N4000; native k AMG divergence and FPE were preserved.',
               'interpretation_status':'CONSEQUENTIAL_INTERPRETATION_RESERVED_FOR_DESIGNATED_ASTRA_PLANNER',
               'comparison_limit':'ON is a saved-field N3000 restart; OFF is the original continuation. Failure timing alone does not isolate a unique divergence cause.',
               'cases':{}, 'provenance':provenance}
    for label in ('OFF','ON'):
        speed = reports[label]['p10-speed-max']
        severe_speed = next((n for n,v in speed.items() if v>1000),None)
        severe_continuity = next((n for n,v in res[label].items() if v[0]>10),None)
        cut = min(n for n in (severe_speed,severe_continuity) if n is not None)
        common = sorted(set.intersection(*(set(rows) for rows in reports[label].values())))
        sample = max(n for n in common if n<cut)
        liquid = reports[label]['p10-mass-phase-2']
        snapshots = {name:rows[sample] for name,rows in reports[label].items()}
        summary['cases'][label] = {'report_first':min(speed),'report_last':max(speed),
            'residual_first':min(res[label]),'residual_last':max(res[label]),
            'first_speed_sample_over_1000':severe_speed,
            'first_continuity_row_over_10':severe_continuity,
            'last_report_coordinate_before_these_diagnostic_thresholds':sample,
            'finite_pre_threshold_reports':snapshots,
            'liquid_inventory_first_kg':liquid[min(liquid)],
            'liquid_inventory_last_report_kg':liquid[max(liquid)],
            'liquid_feed_deficit_fraction_at_pre_threshold_sample':
                (116.92+snapshots['p10-flux-phase-2-steamoutlet'])/116.92,
            'thresholds_are_diagnostic_not_qualification':True}
    (DEST/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with (DEST/'residuals.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['case','iteration',*EQUATIONS])
        for label,rows in res.items():
            writer.writerows([label,n,*v] for n,v in rows.items())
    fig, axes=plt.subplots(3,1,figsize=(8.2,8.2),sharex=True,constrained_layout=True)
    for label,color,style in [('OFF','#0072B2','-'),('ON','#D55E00','--')]:
        speed=reports[label]['p10-speed-max'];mass=reports[label]['p10-mass-phase-2']
        axes[0].plot(list(speed),list(speed.values()),color=color,ls=style,label=label+' (10-update reports)')
        axes[1].plot(list(res[label]),[v[0] for v in res[label].values()],color=color,ls=style)
        axes[2].plot(list(mass),list(mass.values()),color=color,ls=style)
        for ax in axes:
            ax.axvline(3567 if label=='ON' else 3911,color=color,ls=':',lw=1)
    axes[0].set_yscale('log');axes[0].set_ylabel('Maximum speed (m/s)');axes[0].legend(fontsize=9)
    axes[1].set_yscale('log');axes[1].set_ylabel('Continuity residual')
    axes[2].set_ylabel('Liquid inventory (kg)');axes[2].set_xlabel('Native iteration')
    for ax in axes:
        ax.grid(alpha=.25);ax.set_xlim(3000,4000)
    fig.suptitle('M04: original OFF continuation and ON N3000 restart\nBoth runs failed; dotted lines mark native FPE coordinates',fontsize=11)
    fig.savefig(DEST/'off-on-comparison.png',dpi=160)
    plt.close(fig)
    print(json.dumps({k:summary[k] for k in ('ON_actual_failed_iteration','ON_new_updates','OFF_actual_failed_iteration','campaign_spend_lower_bound','campaign_spend_upper_bound','cases')},indent=2))


if __name__=='__main__':
    main()
