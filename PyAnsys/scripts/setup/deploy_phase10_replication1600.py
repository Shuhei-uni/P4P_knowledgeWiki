"""Launch the authorized provisional carrier stage after idle/session proof."""
from __future__ import annotations
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/meshing')]
from deploy_phase10_bf01 import Bridge, psquote
from deploy_phase10_mesh_family import launcher_files
import probe_phase10_native_receipts as passive
from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.remote_text import write_ascii_text_new, read_text


def main():
    out = passive.OUT
    dest = out / 'replication1600-M04'
    launch_file = dest / 'carrier-launch.json'
    assert not launch_file.exists(), 'Prior launch requires reconciliation'
    cfg = json.loads((out / 'run-config.json').read_text())
    spec = json.loads((dest / 'job-spec.json').read_text())
    assert spec['carrier_first_authorized'] and spec['selected_mesh'] == 'M04'
    assert spec['additional_carrier_update_cap'] == 1500
    old = json.loads((out / 'bodyforce-BF01-launch.json').read_text())
    parent = json.loads((out / 'bodyforce-BF01-job-spec.json').read_text())['parent']['pair']
    restore = json.loads((out / 'predivergence-mesh-sensitivity/extraction.json').read_text())['restore_pair']
    b = Bridge(cfg)
    try:
        terminal = passive.read_receipt(b.stub, old['work'] + '/manifest.json', b.metadata, 262144)
        assert terminal['status'] == 'NUMERICAL_FAILURE_UNQUALIFIED'
        assert terminal['controller_pid'] == 24124
        from ansys.api.fluent.v0 import settings_pb2 as sp, settings_pb2_grpc as sg
        q = sp.ExecuteCommandRequest()
        q.path_info.root = 'fluent'; q.path_info.path = 'solution/report-definitions'
        q.command = 'compute'; q.args.value_map.m['report-defs'].value_list.lst.add().string = 'p10-iteration'
        response = sg.SettingsStub(b.channel).ExecuteCommand(q, metadata=b.metadata, timeout=15)
        n = response.reply.value_list.lst[0].value_map.m['p10-iteration'].value_list.lst[0].real
        assert n == 3005
        # The preceding live Settings preflight proved the endpoint idle and
        # equal to this preserved pair. Independently reconcile controller again.
        previous = json.loads((dest / 'preflight-live-state.json').read_text())
        assert previous['idle'] and previous['iteration'] == n
        rid = uuid.uuid4().hex[:8]
        work = 'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication1600-M04-' + rid
        ps = cfg['work'] + '/R1600-dispatch-' + rid + '.ps1'
        proof_path = ps + '.json'; runtime_path = ps + '-runtime.json'
        code = "$ErrorActionPreference='Stop'\n"
        code += "$workers=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -match 'run_phase10|resume_phase10|phase10_core'})\n"
        code += "$old=Get-Process -Id 24124 -ErrorAction SilentlyContinue\n"
        code += 'if($workers.Count -gt 0 -or $old){throw "Existing Phase10 controller"}\n'
        for pair in (parent, restore):
            for kind in ('case', 'data'):
                code += 'if((Get-FileHash -LiteralPath ' + psquote(pair[kind]) + ' -Algorithm SHA256).Hash -ne ' + psquote(pair[kind + '_sha256']) + '){throw "Saved pair hash mismatch"}\n'
        runtime = 'import sys,json,h5py,numpy,ansys.fluent.core as pf; print(json.dumps(dict(executable=sys.executable,pyfluent=pf.__version__)))'
        code += '& ' + psquote(cfg['host_python']) + ' -c ' + psquote(runtime) + ' | Set-Content -LiteralPath ' + psquote(runtime_path) + ' -Encoding Ascii\n'
        code += 'if($LASTEXITCODE -ne 0){throw "Host runtime check failed"}\n'
        code += 'New-Item -ItemType Directory -Path ' + psquote(work) + ' -ErrorAction Stop | Out-Null\n'
        code += '@{old_controller_absent=$true;workers=@();runtime=(Get-Content -Raw -LiteralPath ' + psquote(runtime_path) + ' | ConvertFrom-Json)} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath ' + psquote(proof_path) + ' -Encoding Ascii\n'
        write_ascii_text_new(b, ps, code); b.shell_file(ps)
        proof = json.loads(read_text(b, proof_path))
        assert proof['old_controller_absent'] and not proof['workers']
        assert proof['runtime']['pyfluent'] == '0.42.0'
        wrapper = read_text(b, old['script'])
        bootstrap = [line for line in wrapper.splitlines() if line.startswith("os.environ['PHASE10_EXTRA_PACKAGES'] =")]
        runner = (ROOT / 'scripts/setup/run_phase10_replication1600_carrier.py').read_text()
        if bootstrap:
            runner = runner.replace('import phase10_core as core', '\n'.join(bootstrap) + '\nimport phase10_core as core')
        sources = {'phase10_core.py': (ROOT / 'scripts/setup/run_phase10_mesh_family.py').read_text(),
            'execution_contract.py': (ROOT / 'src/pyansys_fluent/execution_contract.py').read_text(),
            'run_phase10_replication1600_carrier.py': runner}
        hashes = {}
        for name, text in sources.items():
            write_ascii_text_new(b, work + '/' + name, text)
            hashes[name] = hashlib.sha256(text.encode('ascii')).hexdigest()
        native_cfg = {'work': work, 'ip': cfg['ip'], 'port': cfg['port'], 'parent': parent,
            'preserved_BF01_pair': restore, 'BF01_manifest': old['work'] + '/manifest.json',
            'preflight': proof, 'budget': {'spent_upper_bound': 23559, 'campaign_cap': 35000,
                'selected_update_cap': 1500, 'retries_reset_budget': False},
            'report_names': terminal['report_names'], 'report_paths': terminal['report_paths'],
            'source_limits': spec['carrier_stage_source_limits']}
        config = work + '/run-config.json'
        write_ascii_text_new(b, config, json.dumps(native_cfg, indent=2))
        script = work + '/run_phase10_replication1600_carrier.py'
        files = launcher_files(work, rid, script, config, 'R1600', cfg['port'], cfg['host_python'])
        for key in ('launcher', 'cim'):
            files[key] = files[key].replace('/controller/', '/')
        write_ascii_text_new(b, files['launcher'], files['launcher_text'])
        write_ascii_text_new(b, files['cim'], files['cim_text'])
        intent = {'experiment': 'R1600_CARRIER', 'status': 'DEPLOYED_NOT_LAUNCHED',
            'work': work, 'script': script, 'config': config, 'port': cfg['port'],
            'source_hashes': hashes, 'preflight': proof, 'credentials_in_files': False,
            'provisional': True, 'DPM_tracking_authorized_now': False,
            'created_utc': datetime.now(timezone.utc).isoformat(),
            **{k: v for k, v in files.items() if not k.endswith('_text')}}
        launch_file.write_text(json.dumps(intent, indent=2) + '\n')
        if '--launch' not in sys.argv:
            print(json.dumps({'status': intent['status'], 'work': work})); return
        # Transient command and child environment only; never write credentials.
        command = '$env:PHASE10_API_PASSWORD=' + psquote(os.environ['PHASE10_API_PASSWORD']) + '; & ' + psquote(files['launcher'])
        encoded = base64.b64encode(command.encode('utf-16le')).decode('ascii')
        cmd = 'powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + files['cim'] + '" -EncodedCommand ' + encoded
        b.eval('(system "' + quote_scheme_string(cmd) + '")')
        created = json.loads(read_text(b, files['cim_receipt']))
        assert created['ReturnValue'] == 0
        intent.update(status='DETACHED_PROCESS_CREATED', launcher_process=created)
        launch_file.write_text(json.dumps(intent, indent=2) + '\n')
        (out / 'current-launch.json').write_text(json.dumps(intent, indent=2) + '\n')
        print(json.dumps({'status': intent['status'], 'work': work, 'launcher_process': created}))
    finally:
        b.channel.close()


if __name__ == '__main__':
    main()
