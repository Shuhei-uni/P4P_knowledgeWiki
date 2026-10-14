"""Guarded BF01 deployment after a user-requested baseline stop.

No OS command is sent until native receipts prove the baseline stopped.
The password exists only in environment and transient encoded launch arguments.
"""
from __future__ import annotations
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/meshing')]
import probe_phase10_native_receipts as passive
from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.remote_text import write_ascii_text_new, read_text
from deploy_phase10_mesh_family import launcher_files


def psquote(value):
    return "'" + str(value).replace("'", "''") + "'"


class Bridge:
    def __init__(self, cfg):
        endpoint, self.metadata = passive.connection(cfg, os.environ)
        self.channel = passive.grpc.insecure_channel(endpoint)
        self.stub = passive.scheme_eval_pb2_grpc.SchemeEvalStub(self.channel)
        self.scheme = self

    def eval(self, expression):
        req = passive.proto.SchemeEvalRequest()
        value = (passive.Symbol('eval'),
                 (passive.Symbol('with-input-from-string'), expression, passive.Symbol('read')),
                 passive.Symbol('user-initial-environment'))
        passive._convert_py_value_to_scheme_pointer(value, req.input, '25.2.0')
        reply = self.stub.SchemeEval(req, metadata=self.metadata, timeout=60)
        return passive._convert_scheme_pointer_to_py_value(reply.output, '25.2.0')

    def shell_file(self, path):
        command = 'powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + path + '"'
        return self.eval('(system "' + quote_scheme_string(command) + '")')


def main():
    out = passive.OUT
    cfg = json.loads((out / 'run-config.json').read_text())
    spec = json.loads((out / 'bodyforce-BF01-job-spec.json').read_text())
    state = yaml.safe_load((ROOT.parent / 'Project/experiments/phase-10-single-inlet-mesh-convergence/phase-state.yaml').read_text())
    assert not state['paused_by_user'] and not spec.get('paused_by_user'), 'Human pause blocks deployment'
    assert spec['dispatch'].get('human_skipped_M07'), 'User skip must be recorded first'
    assert not spec['deployed']
    assert not (out/'bodyforce-BF01-launch.json').exists(), 'Existing deployment requires reconciliation'
    b = Bridge(cfg)
    try:
        batch = passive.read_receipt(b.stub, cfg['work']+'/batch-manifest.json', b.metadata)
        level = passive.read_receipt(b.stub, cfg['work']+'/M07/manifest.json', b.metadata)
        assert batch['status']=='STOPPED_REQUIRES_REVIEW' and batch['controller_pid']==2572
        assert level['status']=='STOPPED_REQUIRES_REVIEW'
        assert level['error']=='Native run stopped before the requested horizon'
        assert level['completed_iterations']==level['checkpoints'][-1]['iteration']
        # A stale terminal manifest is insufficient: require a responsive live
        # report at the stopped endpoint before any OS command through Fluent.
        from ansys.api.fluent.v0 import settings_pb2, settings_pb2_grpc
        request = settings_pb2.ExecuteCommandRequest()
        request.path_info.root = 'fluent'
        request.path_info.path = 'solution/report-definitions'
        request.command = 'compute'
        request.args.value_map.m['report-defs'].value_list.lst.add().string = 'p10-iteration'
        response = settings_pb2_grpc.SettingsStub(b.channel).ExecuteCommand(
            request, metadata=b.metadata, timeout=15)
        value = response.reply.value_list.lst[0].value_map.m['p10-iteration'].value_list.lst[0].real
        assert value == level['completed_iterations'], 'Live solver differs from stopped baseline'
        rid = uuid.uuid4().hex[:8]
        work = 'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/bodyforce-BF01-'+rid
        preflight_script = cfg['work']+'/BF01-preflight-'+rid+'.ps1'
        preflight_path = cfg['work']+'/BF01-preflight-'+rid+'.json'
        runtime_path = cfg['work']+'/BF01-runtime-'+rid+'.json'
        parent = spec['parent']['pair']
        saved = level['checkpoints'][-1]['pair']
        code = "$ErrorActionPreference='Stop'\n"
        code += "$workers=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -match 'run_phase10|resume_phase10|phase10_core|run_phase10_bodyforce_bf01'})\n"
        code += "$old=Get-Process -Id 2572 -ErrorAction SilentlyContinue\n"
        code += "$files=@()\n"
        for label, pair in (('parent', parent), ('M07_saved', saved)):
            for kind in ('case', 'data'):
                code += '$h=(Get-FileHash -LiteralPath '+psquote(pair[kind])+' -Algorithm SHA256).Hash\n'
                code += 'if($h -ne '+psquote(pair[kind+'_sha256'])+'){throw "Checkpoint hash mismatch"}\n'
                code += '$files+=@{label='+psquote(label)+';kind='+psquote(kind)+';sha256=$h}\n'
        code += 'if(-not (Test-Path -LiteralPath '+psquote(cfg['host_python'])+')){throw "Host Python missing"}\n'
        runtime_code = ('import sys,json,h5py,numpy,ansys.fluent.core as pf; '
                        'import ansys.fluent.core._grpc_services,ansys.api.fluent.v0; '
                        'print(json.dumps(dict(executable=sys.executable,python=sys.version,'
                        'pyfluent=pf.__version__,h5py=h5py.__version__,numpy=numpy.__version__)))')
        code += '& '+psquote(cfg['host_python'])+' -c '+psquote(runtime_code)+' | Set-Content -LiteralPath '+psquote(runtime_path)+' -Encoding Ascii\n'
        code += 'if($LASTEXITCODE -ne 0){throw "Host runtime imports failed"}\n'
        code += '$runtime=Get-Content -LiteralPath '+psquote(runtime_path)+' -Raw | ConvertFrom-Json\n'
        code += '@{old_controller_absent=($null -eq $old);workers=@($workers | Select-Object ProcessId,Name);files=$files;runtime=$runtime;baseline_terminal=$true;live_stopped_iteration='+str(value)+';M07_saved_iteration='+str(level['completed_iterations'])+'} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath '+psquote(preflight_path)+' -Encoding Ascii\n'
        code += 'if($old -or $workers.Count){throw "Existing writer remains"}\n'
        code += 'New-Item -ItemType Directory -Path '+psquote(work) +' -ErrorAction Stop | Out-Null\n'
        write_ascii_text_new(b, preflight_script, code)
        b.shell_file(preflight_script)
        proof = json.loads(read_text(b, preflight_path))
        (out/('BF01-preflight-'+rid+'.json')).write_text(json.dumps(proof, indent=2)+'\n')
        assert proof['old_controller_absent'] and not proof['workers']
        assert proof['runtime']['pyfluent'] == '0.42.0'
        # Reuse the reviewed and unchanged core/runtime route from the old writer.
        old = json.loads((out/'current-launch.json').read_text())
        wrapper = read_text(b, old['script'])
        original_launcher = read_text(b, old['launcher'])
        (out/'BF01-parent-wrapper-audit.txt').write_text(wrapper)
        (out/'BF01-parent-launcher-audit.txt').write_text(original_launcher)
        spent = sum(x['actual_iterations'] for x in batch['failed_levels']) + level['completed_iterations']
        budget = {'campaign_cap':35000, 'spent_lower_bound':spent+305,
                  'spent_upper_bound':spent+995, 'BF01_update_cap':1000}
        assert budget['spent_upper_bound']+1000<=35000
        native_config = {'work':work,'ip':cfg['ip'],'port':cfg['port'],'spec':spec,
                         'parent_manifest':'C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/M04/manifest.json',
                         'reconciliation':proof, 'budget':budget}
        # Pull only explicit package-path bootstrap statements from the audited
        # wrapper, never endpoint credentials or run logic.
        bootstrap = []
        for line in wrapper.splitlines():
            if line.startswith("os.environ['PHASE10_EXTRA_PACKAGES'] ="):
                bootstrap.append(line)
        script = work+'/run_phase10_bodyforce_bf01.py'
        source = (ROOT/'scripts/setup/run_phase10_bodyforce_bf01.py').read_text()
        if bootstrap:
            source = source.replace('import phase10_core as core', '\n'.join(bootstrap)+'\nimport phase10_core as core')
        sources = {'phase10_core.py':(ROOT/'scripts/setup/run_phase10_mesh_family.py').read_text(),
                   'execution_contract.py':(ROOT/'src/pyansys_fluent/execution_contract.py').read_text(),
                   'run_phase10_bodyforce_bf01.py':source}
        hashes = {}
        for name, text in sources.items():
            write_ascii_text_new(b, work+'/'+name, text)
            hashes[name] = hashlib.sha256(text.encode('ascii')).hexdigest()
        config_path = work+'/run-config.json'
        write_ascii_text_new(b, config_path, json.dumps(native_config, indent=2))
        files = launcher_files(work, rid, script, config_path, 'BF01', cfg['port'], cfg['host_python'])
        # launcher_files normally writes into work/controller; keep all files
        # directly inside this already created unique BF01 directory.
        for key in ('launcher','cim'):
            files[key] = files[key].replace('/controller/', '/')
        write_ascii_text_new(b, files['launcher'], files['launcher_text'])
        write_ascii_text_new(b, files['cim'], files['cim_text'])
        intent = {'status':'DEPLOYED_NOT_YET_LAUNCHED','experiment':'BF01','work':work,
                  'script':script,'config':config_path,'source_hashes':hashes,
                  'preflight':proof,'budget':budget,'credentials_in_files':False,
                  **{k:v for k,v in files.items() if not k.endswith('_text')}}
        (out/'bodyforce-BF01-launch.json').write_text(json.dumps(intent, indent=2)+'\n')
        if '--launch' not in sys.argv:
            print(json.dumps({'status':intent['status'],'work':work,'bootstrap_lines':bootstrap,'hashes':hashes}))
            return
        # Secrets appear only in transient launch arguments and child memory.
        command = '$env:PHASE10_API_PASSWORD='+psquote(os.environ['PHASE10_API_PASSWORD'])+'; & '+psquote(files['launcher'])
        encoded = base64.b64encode(command.encode('utf-16le')).decode('ascii')
        cmd = 'powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+files['cim']+'" -EncodedCommand '+encoded
        b.eval('(system "'+quote_scheme_string(cmd)+'")')
        created = json.loads(read_text(b,files['cim_receipt']))
        assert created['ReturnValue']==0
        intent.update(status='DETACHED_PROCESS_CREATED', launcher_process=created,
                      checked_utc=datetime.now(timezone.utc).isoformat())
        (out/'bodyforce-BF01-launch.json').write_text(json.dumps(intent,indent=2)+'\n')
        print(json.dumps({'status':intent['status'],'work':work,'launcher_process':created}))
    finally:
        b.channel.close()


if __name__ == '__main__':
    main()
