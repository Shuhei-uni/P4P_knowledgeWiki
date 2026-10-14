"""Fetch terminal M04 sweep evidence; never use OS commands during a solve."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'PyAnsys/scripts/setup'), str(ROOT / 'PyAnsys/src')]
from deploy_phase10_bf01 import Bridge, psquote
from prepare_phase10_replication1600_dpm import native_proof
from extract_phase10_predivergence_fields import attach
from pyansys_fluent.remote_text import read_text_bounded as read_text, write_ascii_text_new_labeled as write_ascii_text_new
import probe_phase10_native_receipts as passive
import run_phase10_mesh_family as core


def main():
    out = passive.OUT
    tet = '--tet-benchmark' in sys.argv
    dest = out / ('replication1600-tet-benchmark' if tet else 'replication-enthalpy-M04')
    launch_path = dest / ('launch.json' if tet else 'remainder-launch.json' if '--continue-reconciled' in sys.argv else 'sweep-launch.json')
    launch = json.loads(launch_path.read_text())
    cfg = json.loads((out / 'run-config.json').read_text())
    bridge = Bridge(cfg)
    try:
        batch = passive.read_receipt(bridge.stub, launch['work'] + '/batch-manifest.json', bridge.metadata, 262144)
        assert batch['experiment'] == ('R1600_TET_BENCHMARK' if tet else 'REPLICATION_ENTHALPY_SWEEP')
        if tet:
            assert batch['selected_queue'] == [1600] and batch['expected_cells'] == 2964593
        assert batch['status'] in ['COMPLETE_SERIES_EVIDENCE_VERIFIED_UNQUALIFIED', 'STOPPED_PRESERVE_ENDPOINT'], 'Native batch still active; use passive probe'
        manifests = {}
        for h in batch['cases']:
            manifests[h] = passive.read_receipt(bridge.stub, launch['work'] + '/H' + h + '/manifest.json', bridge.metadata, 524288)
        assert all(m['controller_pid'] == batch['controller_pid'] for m in manifests.values())
    finally:
        bridge.channel.close()
    session = attach(cfg)
    try:
        session.events.stop()
        assert not session.settings.solution.run_calculation.iterating()
        last = manifests[str(batch['selected_queue'][len(manifests) - 1])]
        assert core.iteration(session) == last['completed_iteration']
        core.require_state_same(core.state(session), last.get('settings_readback', last['settings_expected']))
        if last['status'] == 'COMPLETE_EVIDENCE_VERIFIED_UNQUALIFIED':
            assert core.iteration(session) == 1500
            core.require_state_same(core.state(session), last['settings_readback'])
    finally:
        session._fluent_connection._channel.close()
    pairs = [c['pair'] for m in manifests.values() for c in m['checkpoints']]
    pairs += [m['final_pair'] for m in manifests.values() if 'final_pair' in m]
    pairs += [m['tracked_pair'] for m in manifests.values() if 'tracked_pair' in m and 'final_pair' not in m]
    proof = native_proof(cfg, [(p[k], p[k + '_sha256']) for p in pairs for k in ['case', 'data']],
                         text_writer=write_ascii_text_new, text_reader=read_text)
    bridge = Bridge(cfg)
    try:
        for h, manifest in manifests.items():
            work = launch['work'] + '/H' + h
            tag = uuid.uuid4().hex[:8]
            ps = work + '/retrieve-' + tag + '.ps1'
            bundle = ps + '.json'
            files = {'manifest.json': work + '/manifest.json', 'preparation.trn': work + '/preparation.trn'}
            if h == next(iter(manifests)):
                files.update({'controller-stderr.log': launch['stderr'],
                              'batch-manifest.json': launch['work'] + '/batch-manifest.json'})
                if tet:
                    files.update({'tet-preparation.trn': launch['work'] + '/tet-preparation.trn',
                                  'preparation-manifest.json': launch['work'] + '/preparation-manifest.json',
                                  'runtime-proof.json': launch['work'] + '/runtime-proof.json'})
            for point in manifest['checkpoints']:
                if 'transcript' in point:
                    files[Path(point['transcript'].replace('\\', '/')).name] = point['transcript']
            files.update({Path(p.replace('\\', '/')).name: p for p in manifest.get('report_files', {}).values()})
            files.update({'monitors/' + n + '.out': p['file'] for n, p in manifest.get('report_paths', {}).items()})
            if manifest.get('DPM_transcript'):
                files['DPM-tracking.trn'] = manifest['DPM_transcript']
            elif manifest.get('DPM_update_dispatches'):
                files['DPM-tracking.trn'] = work + '/DPM-tracking.trn'
            # Capture the original current/failing transcript too, when present.
            if manifest.get('active_transcript'):
                p = manifest['active_transcript']
                files[Path(p.replace('\\', '/')).name] = p
            code = "$ErrorActionPreference='Stop'\n$rows=@()\n"
            for name, source in files.items():
                code += 'if(Test-Path -LiteralPath ' + psquote(source) + '){\n'
                code += '$bytes=[IO.File]::ReadAllBytes(' + psquote(source) + ')\nif($bytes.Length -gt 1048576){throw "Evidence file exceeds bound"}\n'
                code += '$rows+=@{name=' + psquote(name) + ';path=' + psquote(source) + ';sha256=(Get-FileHash -LiteralPath ' + psquote(source) + ' -Algorithm SHA256).Hash.ToLower();bytes=$bytes.Length;base64=[Convert]::ToBase64String($bytes)}\n}\n'
            code += '$payload=@{files=$rows} | ConvertTo-Json -Depth 5\nif($payload.Length -gt 8000000){throw "Evidence bundle exceeds bound"}\n'
            code += '$payload | Set-Content -LiteralPath ' + psquote(bundle) + ' -Encoding Ascii\n'
            write_ascii_text_new(bridge, ps, code)
            bridge.shell_file(ps)
            data = json.loads(read_text(bridge, bundle))
            raw = dest / ('H' + h) / 'raw'
            records = []
            for row in data['files']:
                content = base64.b64decode(row['base64'])
                assert hashlib.sha256(content).hexdigest() == row['sha256']
                target = raw / row['name']
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    assert target.read_bytes() == content, 'Immutable source bytes changed'
                else:
                    target.write_bytes(content)
                records.append({k: v for k, v in row.items() if k != 'base64'})
            receipt = {'status': 'BYTE_IDENTICAL_RETRIEVAL_VERIFIED', 'files': records,
                'native_pair_hashes': proof, 'native_controller_absent': True,
                'native_solver_idle': True, 'case_status': manifest['status']}
            (raw.parent / 'retrieval.json').write_text(json.dumps(receipt, indent=2) + '\n')
        core.dump(dest / 'batch-manifest.json', batch)
        launch.update(status=batch['status'], controller_pid=batch['controller_pid'],
            controller_exited_verified=True, solved_updates=batch['solved_updates'],
            native_pair_hashes_verified=True, evidence_retrieved=True)
        core.dump(launch_path, launch)
        core.dump(out / 'current-launch.json', launch)
        print(json.dumps({'status': batch['status'], 'cases_retrieved': list(manifests),
                          'solved_updates': batch['solved_updates'], 'controller_absent': True}))
    finally:
        bridge.channel.close()


if __name__ == '__main__':
    main()
