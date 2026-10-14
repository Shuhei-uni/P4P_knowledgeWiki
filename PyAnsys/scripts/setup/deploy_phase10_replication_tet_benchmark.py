"""Guarded deployment of one matched tet benchmark in the owned session."""
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
from deploy_phase10_replication_enthalpies import sources
from prepare_phase10_replication1600_dpm import native_proof
from extract_phase10_predivergence_fields import attach
from deploy_phase10_bf01 import Bridge, psquote
from deploy_phase10_mesh_family import launcher_files
from pyansys_fluent.remote_text import write_ascii_text_new_labeled as write_new, read_text_bounded as read_text
from pyansys_fluent.common import quote_scheme_string
import run_phase10_mesh_family as core
import probe_phase10_native_receipts as passive

OUT = ROOT / 'PyAnsys/output/phase10-single-inlet-mesh-convergence'
DEST = OUT / 'replication1600-tet-benchmark'
SOURCE = 'C:/Users/qtra338/P4P/experiments/parallel-andy-studies/enthalpy-dpm-replication/workbench-predecessors/Punanto_injections/h1600_files/dp0/FFF/Fluent/4800-iterations-300412-1.cas.h5'


def packet():
    prepared = json.loads((OUT / 'replication1600-M04/spiral-recovered-parent/DPM-preparation-receipt.json').read_text())
    tracked = json.loads((OUT / 'replication1600-M04/DPM-limit100000-evidence/raw/manifest.json').read_text())
    source = json.loads((OUT / 'replication1600-M04/spiral-recovered-parent/recovery.json').read_text())
    terminal = json.loads((OUT / 'replication-enthalpy-M04/verified-series-terminal.json').read_text())
    old = json.loads((OUT / 'replication-enthalpy-M04/H1760/raw/manifest.json').read_text())
    assert old['status'] == 'COMPLETE_EVIDENCE_VERIFIED_UNQUALIFIED'
    assert old['solved_updates'] == 1500 and old['strict_reopen_verified']
    assert terminal['campaign_carrier_spend'] == [30369, 31059]
    local_source = ROOT / source['case_copy']
    assert hashlib.sha256(local_source.read_bytes()).hexdigest() == source['case_sha256']
    expected = copy.deepcopy(prepared['settings'])
    expected['models']['discrete_phase']['tracking']['max_num_steps'] = 100000
    core.require_state_same(expected, tracked['settings_readback'])
    injections = expected['models']['discrete_phase']['injections']
    assert len(injections) == 9
    assert all(v['material'] == 'liquid-water' for v in injections.values())
    liquid = expected['inlet']['inlet']['phase']['phase-2']['momentum']['mass_flow_rate']['value']
    assert abs(sum(v['initial_values']['mass_flow_rate']['total_flow_rate'] for v in injections.values()) - liquid) < 1e-8
    reference = {'mesh': 'M04', 'cells': 946967, 'carrier_seconds': 2520.4988059001043,
                 'DPM_seconds': tracked['tracking_seconds'],
                 'artifact': str(OUT.relative_to(ROOT) / 'replication1600-M04/DPM-limit100000-evidence/raw/manifest.json')}
    spec = {'experiment': 'R1600_TET_BENCHMARK', 'human_selected': True, 'expected_cells': 2964593,
            'source_case': SOURCE, 'source_sha256': source['case_sha256'], 'reference': reference,
            'cases': [{'case': 4, 'enthalpy_kJ_kg': 1600, 'liquid_kg_s': liquid,
                       'settings': expected, 'source_artifacts': {}, 'historical_summary': tracked.get('historical_comparison', {})}],
            'budget': {'spent_lower_bound': 30369, 'spent_upper_bound': 31059, 'campaign_cap': 35000,
                       'selected_update_cap': 1500, 'upper_bound_after_no_retries': 32559,
                       'retries_reset_budget': False},
            'carrier_updates': 1500, 'DPM_updates': 1, 'tracking_max_num_steps': 100000,
            'preserved_pair': old['final_pair'], 'preserved_M04_pair': old['final_pair'],
            'preserved_settings': old['settings_readback'],
            'boundary_role_renames': {'outlet': 'steamoutlet', 'wall-fluid': 'wall'},
            'exact_historical_binary_provenance_verified': False}
    compiled = sources()
    compiled['run_phase10_replication_tet_benchmark.py'] = Path(__file__).with_name('run_phase10_replication_tet_benchmark.py').read_text()
    for code in compiled.values():
        ast.parse(code)
    spec['code_sha256_LF'] = {name: hashlib.sha256(code.encode('ascii')).hexdigest() for name, code in compiled.items()}
    return spec, compiled, old


def main():
    spec, compiled, old = packet()
    DEST.mkdir(exist_ok=True)
    (DEST / 'job-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    if '--offline' in sys.argv:
        print(json.dumps({'status': 'OFFLINE_SOURCE_SETTINGS_CODE_BUDGET_VERIFIED', 'cells': spec['expected_cells'],
                          'injections': 9, 'selected_updates': 1500, 'campaign_upper_bound_after': 32559}))
        return
    launch_path = DEST / 'launch.json'
    resume_zero = '--resume-prepared-zero' in sys.argv
    recovery = '--recover-zero-preparation' in sys.argv or resume_zero
    assert not launch_path.exists() or recovery, 'Reconcile prior deployment before replay'
    if recovery:
        attempt = 'attempt-02' if resume_zero else 'attempt-01'
        failed = json.loads((DEST / attempt / 'raw/preparation-manifest.json').read_text())
        assert failed['solved_updates'] == 0 and failed['DPM_updates'] == 0
        if resume_zero:
            stopped = json.loads((DEST / attempt / 'raw/level-manifest.json').read_text())
            assert stopped['solved_updates'] == 0 and stopped.get('requested_target') is None
            assert failed['status'] == 'PREPARED_N0_REOPENED_SETTINGS_VERIFIED'
            assert failed['strict_reopen_verified'] and failed['initializations'] == 1
            spec['prepared_zero_resume'] = failed
            spec['preserved_pair'] = failed['pair']
            spec['preserved_settings'] = failed['settings_readback']
            (DEST / 'job-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
        else:
            assert failed['status'] == 'PREPARATION_ERROR_ZERO_SOLVED_UPDATES'
            assert failed['preserved_M04_restored_on_error']
        previous_launch = json.loads(launch_path.read_text())
        backup = DEST / attempt / 'launch.json'
        if not backup.exists():
            backup.write_text(json.dumps(previous_launch, indent=2) + '\n')
    cfg = json.loads((OUT / 'run-config.json').read_text())
    assert cfg['processor_count'] == 16
    previous = json.loads((OUT / 'current-launch.json').read_text())
    assert previous['experiment'] == ('R1600_TET_BENCHMARK' if recovery else 'REPLICATION_ENTHALPY_SWEEP')
    attached = queue.Queue()
    def connect():
        try:
            attached.put(attach(cfg))
        except BaseException as error:
            attached.put(error)
    threading.Thread(target=connect, daemon=True).start()
    s = attached.get(timeout=60)
    if isinstance(s, BaseException):
        raise s
    try:
        s.events.stop()
        assert not s.settings.solution.run_calculation.iterating()
        if resume_zero:
            assert core.iteration(s) in (0, 1)
        else:
            assert core.iteration(s) == 1500
        core.require_state_same(core.state(s), spec['preserved_settings'])
        residual = s.settings.solution.monitor.residual.get_state()
        plots = s.settings.solution.monitor.report_plots.get_state()
        session_version = s.get_fluent_version().value
        assert session_version.startswith('25.2')
    finally:
        s._fluent_connection._channel.close()
    bridge = Bridge(cfg)
    try:
        batch = passive.read_receipt(bridge.stub, previous['work'] + '/batch-manifest.json', bridge.metadata, limit=262144)
        if recovery:
            assert batch['status'] == 'STOPPED_PRESERVE_ENDPOINT'
            assert batch['solved_updates'] == 0
            if not resume_zero:
                assert not batch['cases']
            assert batch['controller_pid'] == failed['controller_pid']
        else:
            assert batch['status'] == 'COMPLETE_SERIES_EVIDENCE_VERIFIED_UNQUALIFIED'
            assert batch['solved_updates'] == 1500 and batch['DPM_completed_updates'] == 1
    finally:
        bridge.channel.close()
    rid = uuid.uuid4().hex[:8]
    work = 'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication1600-tet-' + rid
    pairs = [spec['preserved_pair'], spec['preserved_M04_pair']]
    paths = [(spec['source_case'], spec['source_sha256'])] + list(dict.fromkeys(
        (pair[k], pair[k + '_sha256']) for pair in pairs for k in ['case', 'data']))
    proof = native_proof(cfg, paths, work, text_writer=write_new, text_reader=read_text)
    bridge = Bridge(cfg)
    try:
        wrapper = read_text(bridge, json.loads((OUT / 'replication1600-M04/carrier-launch.json').read_text())['script'])
        bootstrap = [line for line in wrapper.splitlines() if line.startswith("os.environ['PHASE10_EXTRA_PACKAGES'] =")]
        if bootstrap:
            compiled['run_phase10_replication_tet_benchmark.py'] = compiled['run_phase10_replication_tet_benchmark.py'].replace(
                'import phase10_core as core', '\n'.join(bootstrap) + '\nimport phase10_core as core')
        hashes = {}
        for name, code in compiled.items():
            write_new(bridge, work + '/' + name, code)
            assert read_text(bridge, work + '/' + name).replace('\r\n', '\n') == code.replace('\r\n', '\n')
            hashes[name] = hashlib.sha256(code.encode('ascii')).hexdigest()
        runtime = work + '/runtime-proof.json'
        ps = work + '/runtime-proof.ps1'
        check = 'import sys,json;sys.path.insert(0,' + repr(work) + ');import phase10_core,phase10_dpm_audit,ansys.fluent.core as pf;print(json.dumps(dict(executable=sys.executable,pyfluent=pf.__version__)))'
        ps_code = "$ErrorActionPreference='Stop'\n& " + psquote(cfg['host_python']) + ' -c ' + psquote(check) + ' | Set-Content -LiteralPath ' + psquote(runtime) + ' -Encoding Ascii\nif($LASTEXITCODE -ne 0){throw "Native runtime failed"}\n'
        write_new(bridge, ps, ps_code)
        bridge.shell_file(ps)
        runtime_proof = json.loads(read_text(bridge, runtime))
        assert runtime_proof['pyfluent'] == '0.42.0'
        native_cfg = {**spec, 'work': work, 'ip': cfg['ip'], 'port': cfg['port'], 'level': 'TET',
                      'preflight': proof, 'processor_count': 16, 'fluent_version': session_version,
                      'reference_report_names': old['report_names'],
                      'reference_report_paths': old['report_paths'],
                      'reference_residual_monitor': residual, 'reference_report_plots': plots}
        config = work + '/run-config.json'
        write_new(bridge, config, json.dumps(native_cfg, indent=2) + '\n')
        assert json.loads(read_text(bridge, config)) == native_cfg
        script = work + '/run_phase10_replication_tet_benchmark.py'
        files = launcher_files(work, rid, script, config, 'TET_BENCHMARK', cfg['port'], cfg['host_python'])
        for key in ['launcher', 'cim']:
            files[key] = files[key].replace('/controller/', '/')
            write_new(bridge, files[key], files[key + '_text'])
        intent = {'experiment': 'R1600_TET_BENCHMARK', 'status': 'DEPLOYED_NOT_LAUNCHED',
                  'work': work, 'script': script, 'config': config, 'port': cfg['port'],
                  'preflight': proof, 'source_hashes_LF': hashes, 'runtime': runtime_proof,
                  'credentials_in_files': False, 'selected_queue': [1600], 'budget': spec['budget'],
                  'created_utc': datetime.now(timezone.utc).isoformat(),
                  'code_review': 'Source/preserved hashes; settings/injections parity; version-matched rename API; fresh N0; shared 1/1000/499 runner and DPM audit; no automatic retries.',
                  **{k: v for k, v in files.items() if not k.endswith('_text')}}
        launch_path.write_text(json.dumps(intent, indent=2) + '\n')
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
        launch_path.write_text(json.dumps(intent, indent=2) + '\n')
        (OUT / 'current-launch.json').write_text(json.dumps(intent, indent=2) + '\n')
        print(json.dumps({'status': intent['status'], 'work': work, 'launcher_process': created}))
    finally:
        bridge.channel.close()


if __name__ == '__main__':
    main()
