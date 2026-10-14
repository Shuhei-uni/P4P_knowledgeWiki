"""Reviewable source compilation and guarded deployment for the M04 sweep."""
import ast
import base64
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import sys
import threading
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'PyAnsys/scripts/setup'), str(ROOT / 'PyAnsys/scripts/inspection'),
               str(ROOT / 'PyAnsys/src'), str(ROOT / 'PyAnsys/src/pyansys_fluent')]
from prepare_phase10_replication1600_dpm import overlay, native_proof
from extract_phase10_predivergence_fields import attach
from deploy_phase10_bf01 import Bridge, psquote
from deploy_phase10_mesh_family import launcher_files
from pyansys_fluent.remote_text import write_ascii_text_new_labeled as write_ascii_text_new, read_text_bounded as read_text
from pyansys_fluent.common import quote_scheme_string
import run_phase10_mesh_family as core
import probe_phase10_native_receipts as passive

OUT = ROOT / 'PyAnsys/output/phase10-single-inlet-mesh-convergence'
DEST = OUT / 'replication-enthalpy-M04'


def compile_cases():
    prepared = json.loads((OUT / 'replication1600-M04/spiral-recovered-parent/DPM-preparation-receipt.json').read_text())
    index = json.loads((OUT / 'replication-enthalpy-candidates/candidate-index.json').read_text())
    cases = []
    for row in index['candidates']:
        h = row['enthalpy_kJ_kg']
        assert h in [1440, 1520, 1680, 1760]
        sources = {}
        for artifact in row['artifacts']:
            file = ROOT / artifact['file']
            assert hashlib.sha256(file.read_bytes()).hexdigest() == artifact['sha256']
            sources[file.name] = artifact
        manifest = json.loads((ROOT / next(v['file'] for n, v in sources.items()
                                           if n.endswith('_manifest.json') and '_flow_' not in n)).read_text())
        flow = json.loads((ROOT / next(v['file'] for n, v in sources.items() if n.endswith('_flow_manifest.json'))).read_text())
        exact = manifest['injection_readbacks']
        assert exact == manifest['post_dpm_injection_readbacks'] == flow['injection_readbacks']
        assert flow['inlet_readback'] == manifest['inlet_readback']
        assert len(exact) == 9 and set(exact) == set(prepared['settings']['injections'])
        assert abs(sum(v['initial_values']['mass_flow_rate']['total_flow_rate'] for v in exact.values()) - row['liquid_kg_s']) < 1e-8
        target = copy.deepcopy(prepared['settings'])
        inlet = copy.deepcopy(manifest['inlet_readback'])
        for phase in inlet['phase'].values():
            if 'dpm' in phase:
                phase['discrete_phase'] = phase.pop('dpm')
                if 'discrete_phase_bc_type' in phase['discrete_phase']:
                    phase['discrete_phase']['bc_type'] = phase['discrete_phase'].pop('discrete_phase_bc_type')
        # All historical inlet fields except the two specified phase flows
        # must equal the verified Case4 parent. Do not silently ignore a delta.
        inlet_normalized = copy.deepcopy(inlet)
        for phase in ['phase-1', 'phase-2']:
            inlet_normalized['phase'][phase]['momentum']['mass_flow_rate']['value'] = target['inlet']['inlet']['phase'][phase]['momentum']['mass_flow_rate']['value']
        assert overlay(target['inlet']['inlet'], inlet_normalized) == target['inlet']['inlet']
        target['inlet']['inlet'] = overlay(target['inlet']['inlet'], inlet)
        for name, source in exact.items():
            assert source['initial_values']['reference_frame'] == 'global'
            translated = copy.deepcopy(source)
            translated['initial_values'].pop('reference_frame')
            target['models']['discrete_phase']['injections'][name] = overlay(
                target['models']['discrete_phase']['injections'][name], translated)
        target['models']['discrete_phase']['tracking']['max_num_steps'] = 100000
        cases.append(dict(case=row['case'], enthalpy_kJ_kg=h, steam_kg_s=row['steam_kg_s'],
            liquid_kg_s=row['liquid_kg_s'], settings=target, source_artifacts=sources,
            historical_summary=manifest['case_summary']))
    assert [c['enthalpy_kJ_kg'] for c in cases] == [1440, 1520, 1680, 1760]
    return prepared, cases


def sources():
    # Extract the unchanged, previously verified Final-mass audit. Its parser
    # runs on the host without project path assumptions or plotting imports.
    analyzer = (ROOT / 'PyAnsys/scripts/analysis/analyze_phase10_replication1600_dpm.py').read_text()
    tree = ast.parse(analyzer)
    audit = 'import re\nfrom dpm_reports import parse_mass_transfer_rows, parse_fate_rows, _MASS_ROW_RE\n'
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'TERMINAL' for t in node.targets):
            audit += ast.get_source_segment(analyzer, node) + '\n'
        if isinstance(node, ast.FunctionDef) and node.name in ['half_unit', 'audit_report']:
            audit += ast.get_source_segment(analyzer, node) + '\n'
    parser = (ROOT / 'PyAnsys/src/pyansys_fluent/dpm_reports.py').read_text()
    # Only parsing functions are used on the host. Preserve the quoting helper
    # for module import without requiring the full project package deployment.
    common = (ROOT / 'PyAnsys/src/pyansys_fluent/common.py').read_text()
    quote = next(n for n in ast.parse(common).body if isinstance(n, ast.FunctionDef) and n.name == 'quote_scheme_string')
    parser = parser.replace('from pyansys_fluent.common import quote_scheme_string', ast.get_source_segment(common, quote))
    return {
        'run_phase10_replication_enthalpies.py': (ROOT / 'PyAnsys/scripts/setup/run_phase10_replication_enthalpies.py').read_text(),
        'phase10_core.py': (ROOT / 'PyAnsys/scripts/setup/run_phase10_mesh_family.py').read_text(),
        'execution_contract.py': (ROOT / 'PyAnsys/src/pyansys_fluent/execution_contract.py').read_text(),
        'phase10_dpm_audit.py': audit,
        'dpm_reports.py': parser}


def main():
    prepared, cases = compile_cases()
    continuation = '--continue-reconciled' in sys.argv
    recovery = None
    if continuation:
        recovery = json.loads((DEST / 'H1680/verified-manifest.json').read_text())
        assert recovery['status'] == 'COMPLETE_EVIDENCE_VERIFIED_UNQUALIFIED'
        assert recovery['solved_updates'] == 1500 and recovery['DPM_completed_updates'] == 1
        assert recovery['strict_reopen_verified'] and recovery['controller_absent_verified']
        for h in [1440, 1520]:
            completed = json.loads((DEST / ('H' + str(h)) / 'raw/manifest.json').read_text())
            assert completed['status'] == 'COMPLETE_EVIDENCE_VERIFIED_UNQUALIFIED'
            assert completed['solved_updates'] == 1500 and completed['DPM_completed_updates'] == 1
        assert not (DEST / 'H1760/raw/manifest.json').exists()
        cases = [c for c in cases if c['enthalpy_kJ_kg'] == 1760]
    DEST.mkdir(exist_ok=True)
    spec = {'experiment': 'REPLICATION_ENTHALPY_SWEEP', 'human_selected': True,
        'mesh': 'M04', 'cells': 946967, 'cases': cases, 'fresh_Hybrid_per_case': True,
        'carrier_updates_per_case': 1500, 'DPM_updates_per_case': 1, 'tracking_max_num_steps': 100000,
        'budget': {'spent_lower_bound': 24369, 'spent_upper_bound': 25059, 'campaign_cap': 35000,
                   'selected_update_cap': 6000, 'upper_bound_after_no_retries': 31059,
                   'retries_reset_budget': False},
        'incomplete_assumption': 'Incomplete particle mass is assumed separated for efficiency, by human direction.',
        'source_limit': 'Recovered spiral parent plus direct historical enthalpy readbacks; exact July binaries/full exports not located.'}
    if continuation:
        spec['budget'].update(spent_lower_bound=28869, spent_upper_bound=29559, selected_update_cap=1500)
        spec['recovery'] = {'original_batch': str(DEST / 'batch-manifest.json'),
            'verified_H1680': str(DEST / 'H1680/verified-manifest.json'),
            'prior_carrier_updates': 4500, 'prior_DPM_updates': 3,
            'only_unfinished_case_selected': 1760, 'repeated_carrier_or_DPM_updates': 0}
    compiled = sources()
    for code in compiled.values():
        ast.parse(code)
    spec['code_sha256_LF'] = {n: hashlib.sha256(c.encode('ascii')).hexdigest() for n, c in compiled.items()}
    (DEST / ('remaining-job-spec.json' if continuation else 'job-spec.json')).write_text(json.dumps(spec, indent=2) + '\n')
    if '--offline' in sys.argv:
        print(json.dumps({'status': 'SOURCE_INPUTS_AND_CODE_COMPILED', 'queue': [c['enthalpy_kJ_kg'] for c in cases]}))
        return
    launch_file = DEST / ('remainder-launch.json' if continuation else 'sweep-launch.json')
    assert not launch_file.exists(), 'Reconcile existing sweep before deployment'
    cfg = json.loads((OUT / 'run-config.json').read_text())
    previous = json.loads((OUT / 'current-launch.json').read_text())
    if continuation:
        assert previous['experiment'] == 'REPLICATION_ENTHALPY_SWEEP'
        assert previous['status'] == 'STOPPED_PRESERVE_ENDPOINT' and previous['controller_exited_verified']
        old = recovery
        parent = recovery['final_pair']
    else:
        assert previous['experiment'] == 'R1600_DPM_LIMIT' and previous['mass_accounting_verified']
        old = json.loads((OUT / 'replication1600-M04/DPM-limit100000-evidence/raw/manifest.json').read_text())
        parent = previous['final_pair']
    # Bounded attach and live state proof precede all Fluent-mediated OS access.
    attached = queue.Queue()
    def connect():
        try:
            attached.put(attach(cfg))
        except BaseException as error:
            attached.put(error)
    threading.Thread(target=connect, daemon=True).start()
    session = attached.get(timeout=60)
    if isinstance(session, BaseException):
        raise session
    try:
        session.events.stop()
        assert not session.settings.solution.run_calculation.iterating() and core.iteration(session) == 1500
        core.require_state_same(core.state(session), old['settings_readback'])
    finally:
        session._fluent_connection._channel.close()
    rid = uuid.uuid4().hex[:8]
    work = 'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication-enthalpy-M04-' + rid
    proof = native_proof(cfg, [(p[k], p[k + '_sha256']) for p in [parent, prepared['pair']]
                              for k in ['case', 'data']], work, text_writer=write_ascii_text_new, text_reader=read_text)
    bridge = Bridge(cfg)
    try:
        wrapper = read_text(bridge, json.loads((OUT / 'replication1600-M04/carrier-launch.json').read_text())['script'])
        bootstrap = [line for line in wrapper.splitlines() if line.startswith("os.environ['PHASE10_EXTRA_PACKAGES'] =")]
        if bootstrap:
            compiled['run_phase10_replication_enthalpies.py'] = compiled['run_phase10_replication_enthalpies.py'].replace(
                'import phase10_core as core', '\n'.join(bootstrap) + '\nimport phase10_core as core')
        hashes = {}
        for name, code in compiled.items():
            write_ascii_text_new(bridge, work + '/' + name, code)
            assert read_text(bridge, work + '/' + name).replace('\r\n', '\n') == code.replace('\r\n', '\n')
            hashes[name] = hashlib.sha256(code.encode('ascii')).hexdigest()
        # Preserve exact archived source bytes through base64; JSON/text line
        # endings must not change the source hashes used by the native guard.
        ps = work + '/source-and-runtime-proof.ps1'
        runtime = work + '/runtime-proof.json'
        ps_code = "$ErrorActionPreference='Stop'\nNew-Item -ItemType Directory -Path " + psquote(work + '/sources') + ' | Out-Null\n'
        write_ascii_text_new(bridge, work + '/create-sources.ps1', ps_code)
        bridge.shell_file(work + '/create-sources.ps1')
        ps_code = "$ErrorActionPreference='Stop'\n"
        for case in cases:
            for name, identity in case['source_artifacts'].items():
                data = (ROOT / identity['file']).read_bytes()
                target = work + '/sources/' + name
                upload = '[IO.File]::WriteAllBytes(' + psquote(target) + ',[Convert]::FromBase64String(' + psquote(base64.b64encode(data).decode('ascii')) + '))\n'
                upload += 'if((Get-FileHash -LiteralPath ' + psquote(target) + ' -Algorithm SHA256).Hash -ne ' + psquote(identity['sha256']) + '){throw "Archived source changed"}\n'
                upload_path = work + '/upload-' + name + '.ps1'
                write_ascii_text_new(bridge, upload_path, "$ErrorActionPreference='Stop'\n" + upload)
                bridge.shell_file(upload_path)
        check = 'import sys,json;sys.path.insert(0,' + repr(work) + ');import phase10_core,phase10_dpm_audit,ansys.fluent.core as pf;print(json.dumps(dict(executable=sys.executable,pyfluent=pf.__version__)))'
        ps_code += '& ' + psquote(cfg['host_python']) + ' -c ' + psquote(check) + ' | Set-Content -LiteralPath ' + psquote(runtime) + ' -Encoding Ascii\nif($LASTEXITCODE -ne 0){throw "Native runtime failed"}\n'
        write_ascii_text_new(bridge, ps, ps_code)
        bridge.shell_file(ps)
        runtime_proof = json.loads(read_text(bridge, runtime))
        assert runtime_proof['pyfluent'] == '0.42.0'
        carrier = json.loads((OUT / 'replication1600-M04/carrier-evidence/raw/manifest.json').read_text())
        native_cfg = {'work': work, 'ip': cfg['ip'], 'port': cfg['port'], 'cases': cases,
            'preserved_pair': parent, 'preserved_settings': old['settings_readback'],
            'fresh_parent': prepared['pair'], 'fresh_parent_settings': prepared['settings'],
            'report_names': carrier['report_names'], 'report_paths': carrier['report_paths'],
            'budget': spec['budget'], 'preflight': proof}
        config = work + '/run-config.json'
        write_ascii_text_new(bridge, config, json.dumps(native_cfg, indent=2) + '\n')
        assert json.loads(read_text(bridge, config)) == native_cfg
        script = work + '/run_phase10_replication_enthalpies.py'
        files = launcher_files(work, rid, script, config, 'ENTHALPY', cfg['port'], cfg['host_python'])
        for key in ['launcher', 'cim']:
            files[key] = files[key].replace('/controller/', '/')
            write_ascii_text_new(bridge, files[key], files[key + '_text'])
        intent = {'experiment': 'REPLICATION_ENTHALPY_SWEEP', 'status': 'DEPLOYED_NOT_LAUNCHED',
            'work': work, 'script': script, 'config': config, 'port': cfg['port'], 'preflight': proof,
            'source_hashes_LF': hashes, 'source_readback_verified': True, 'runtime': runtime_proof,
            'credentials_in_files': False, 'selected_queue': [c['enthalpy_kJ_kg'] for c in cases],
            'tracking_max_num_steps': 100000, 'budget': spec['budget'],
            'created_utc': datetime.now(timezone.utc).isoformat(),
            **{k: v for k, v in files.items() if not k.endswith('_text')}}
        if continuation:
            intent['recovery'] = spec['recovery']
        launch_file.write_text(json.dumps(intent, indent=2) + '\n')
        if '--launch' not in sys.argv:
            print(json.dumps({'status': intent['status'], 'work': work}))
            return
        command = '$env:PHASE10_API_PASSWORD=' + psquote(os.environ['PHASE10_API_PASSWORD']) + '; & ' + psquote(files['launcher'])
        encoded = base64.b64encode(command.encode('utf-16le')).decode('ascii')
        cmd = 'powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + files['cim'] + '" -EncodedCommand ' + encoded
        bridge.eval('(system "' + quote_scheme_string(cmd) + '")')
        created = json.loads(read_text(bridge, files['cim_receipt']))
        assert created['ReturnValue'] == 0
        intent.update(status='DETACHED_PROCESS_CREATED', launcher_process=created)
        launch_file.write_text(json.dumps(intent, indent=2) + '\n')
        (OUT / 'current-launch.json').write_text(json.dumps(intent, indent=2) + '\n')
        print(json.dumps({'status': intent['status'], 'work': work, 'launcher_process': created}))
    finally:
        bridge.channel.close()


if __name__ == '__main__':
    main()
