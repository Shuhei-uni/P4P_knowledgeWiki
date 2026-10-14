"""Compare verified fixed-horizon tet and M04 Case4 cost and DPM fates."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'PyAnsys/output/phase10-single-inlet-mesh-convergence'
DEST = OUT / 'replication1600-tet-benchmark'


def main():
    paths = [DEST / 'H1600/raw/manifest.json',
             OUT / 'replication1600-M04/carrier-evidence/raw/manifest.json',
             OUT / 'replication1600-M04/DPM-limit100000-evidence/raw/manifest.json',
             OUT / 'replication1600-M04/DPM-limit100000-evidence/summary.json']
    tet, m04_carrier, m04_raw, m04_summary = [json.loads(p.read_text()) for p in paths]
    assert m04_summary['aggregate']['mass_accounting_verified']
    assert m04_raw['tracking_seconds'] == m04_summary['tracking_seconds']
    m04_dpm = {**m04_raw, **m04_summary}
    retrieval = json.loads((DEST / 'H1600/retrieval.json').read_text())
    assert retrieval['native_controller_absent'] and retrieval['native_solver_idle']
    assert tet['status'] == 'COMPLETE_EVIDENCE_VERIFIED_UNQUALIFIED'
    assert tet['solved_updates'] == tet['completed_iteration'] == 1500
    assert tet['DPM_completed_updates'] == tet['DPM_update_dispatches'] == 1
    assert tet['strict_reopen_verified'] and tet['mass_accounting_verified']
    assert tet['final_pair']['counts']['cells'] == 2964593
    rows = []
    for name, carrier, dpm, cells in [('M04', m04_carrier, m04_dpm, 946967),
                                     ('TET', tet, tet, 2964593)]:
        assert carrier['solved_updates'] == 1500
        seconds = sum(p.get('solver_seconds', 0) for p in carrier['checkpoints'])
        mass = dpm['aggregate']['final_mass_kg_s']
        rows.append({'mesh': name, 'cells': cells, 'carrier_updates': 1500,
                     'carrier_seconds': seconds, 'carrier_seconds_per_update': seconds / 1500,
                     'DPM_seconds': dpm['tracking_seconds'],
                     'combined_compute_seconds': seconds + dpm['tracking_seconds'],
                     'efficiency_percent_incomplete_assumed_separated': 100 * (1 - mass['escaped'] / dpm['aggregate']['injected_kg_s']),
                     'escaped_kg_s': mass['escaped'], 'trapped_kg_s': mass['trapped'],
                     'incomplete_kg_s': mass['incomplete']})
    with (DEST / 'cost-output-comparison.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    summary = {'status': 'FIXED_HORIZON_COMPARISON_EVIDENCE_VERIFIED_UNQUALIFIED', 'rows': rows,
               'tet_to_M04_carrier_time_ratio': rows[1]['carrier_seconds'] / rows[0]['carrier_seconds'],
               'tet_to_M04_DPM_time_ratio': rows[1]['DPM_seconds'] / rows[0]['DPM_seconds'],
               'campaign_carrier_spend_after': [31869, 32559],
               'sources': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
               'excluded_time': ['preparation', 'initialization', 'checkpoint save/reopen', 'transfer', 'post-solve extraction'],
               'configuration_stage_limit': 'M04 original1600 carrier ran before DPM injection installation; tet carrier has uncoupled injection definitions present, with only one tracking dispatch afterN1500.',
               'initial_volume_comparison': json.loads((DEST / 'initial-volume-comparison.json').read_text()),
               'mesh_only_speedup_established': False,
               'claim_limit': 'Cost/output at1500 carrier updates; not time-to-convergence, validation, mesh independence or improved accuracy.'}
    (DEST / 'comparison-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'status': summary['status'], 'tet_to_M04_carrier_time_ratio': summary['tet_to_M04_carrier_time_ratio'],
                      'tet_to_M04_DPM_time_ratio': summary['tet_to_M04_DPM_time_ratio']}))


if __name__ == '__main__':
    main()
