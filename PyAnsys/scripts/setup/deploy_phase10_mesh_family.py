"""Deploy the selected Phase 10 controller using detached WMI process creation.

Credentials stay in environment variables and transient command arguments.
Launcher/config/receipts contain no passwords. Never relaunch an existing job
without inspecting its process and endpoint first.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import os
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/meshing'), str(ROOT / 'src')]
from publish_single_family import connect, psquote
from pyansys_fluent.common import quote_scheme_string, remote_file_exists
from pyansys_fluent.remote_text import write_ascii_text_new

OUT = ROOT / 'output/phase10-single-inlet-mesh-convergence'
HOST_PYTHON = ('C:/Users/syok443/Documents/FluentRuns/Phase8/Stage2/20261007/'
               'controller-venv/Scripts/python.exe')


def read_launch_receipt(s, path, limit=131072):
    """Bound native receipt reads; oversized preflight data must not block launch."""
    if not remote_file_exists(s, path):
        raise FileNotFoundError(path)
    quoted = quote_scheme_string(path.replace('\\', '/'))
    expression = (
        '(let ((p (open-input-file "' + quoted + '"))) '
        "(let loop ((chars '()) (left " + str(limit) + ')) '
        '(let ((c (read-char p))) '
        '(cond ((eof-object? c) (close-input-port p) (list->string (reverse chars))) '
        '((= left 0) (close-input-port p) (error "Phase10 receipt exceeds read bound")) '
        '(else (loop (cons c chars) (- left 1)))))))'
    )
    value = s.scheme.eval(expression)
    if not isinstance(value, str):
        raise RuntimeError('Expected text receipt: ' + path)
    return value


def launcher_files(work, rid, script, config, mode, port, host_python=HOST_PYTHON):
    receipt = work + '/' + mode + '-launch-' + rid + '.json'
    stdout = work + '/' + mode + '-' + rid + '-stdout.log'
    stderr = work + '/' + mode + '-' + rid + '-stderr.log'
    launcher = work + '/controller/launch-' + rid + '.ps1'
    cim = work + '/controller/cim-' + rid + '.ps1'
    cim_receipt = work + '/' + mode + '-cim-' + rid + '.json'
    argv = ["'-u'", psquote(script), "'--config'", psquote(config)]
    if mode == 'pilot': argv.append("'--prepare-only'")
    if mode == 'resume': argv.append("'--continue-reconciled'")
    launch_text = ("$ErrorActionPreference='Stop'\n"
        '$p=Start-Process -FilePath ' + psquote(host_python)
        + ' -ArgumentList @(' + ','.join(argv) + ')'
        + ' -WorkingDirectory ' + psquote(work)
        + ' -RedirectStandardOutput ' + psquote(stdout)
        + ' -RedirectStandardError ' + psquote(stderr)
        + ' -WindowStyle Hidden -PassThru\n'
        + '@{pid=$p.Id;script=' + psquote(script) + ';config=' + psquote(config)
        + ';stdout=' + psquote(stdout) + ';stderr=' + psquote(stderr)
        + ';port=' + str(port) + ';mode=' + psquote(mode)
        + '} | ConvertTo-Json | Set-Content -LiteralPath ' + psquote(receipt)
        + ' -Encoding Ascii\n')
    cim_text = ("param([Parameter(Mandatory=$true)][string]$EncodedCommand)\n"
        "$ErrorActionPreference='Stop'\n"
        "$command='powershell.exe -NoProfile -NonInteractive -EncodedCommand '+$EncodedCommand\n"
        '$result=Invoke-CimMethod -ClassName Win32_Process -MethodName Create '
        '-Arguments @{CommandLine=$command;CurrentDirectory=' + psquote(work) + '}\n'
        '$result | Select-Object ProcessId,ReturnValue | ConvertTo-Json | '
        'Set-Content -LiteralPath ' + psquote(cim_receipt) + ' -Encoding Ascii\n'
        "if($result.ReturnValue -ne 0){throw 'WMI launcher rejected process creation'}\n")
    return {'launcher': launcher, 'launcher_text': launch_text, 'cim': cim,
            'cim_text': cim_text, 'cim_receipt': cim_receipt, 'receipt': receipt,
            'stdout': stdout, 'stderr': stderr}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['pilot', 'batch', 'resume'])
    args = parser.parse_args()
    cfg = json.loads((OUT / 'run-config.json').read_text())
    work = cfg['work']; rid = uuid.uuid4().hex[:8]
    port = int(os.environ['MESH_API_PORT'])
    s = connect(); s.events.stop()
    # Reject an unfinished receipt before any OS command through Fluent.
    passive_levels = []
    for row in cfg['meshes']:
        path = work + '/' + row['level'] + '/manifest.json'
        if remote_file_exists(s, path):
            passive_levels.append(json.loads(read_launch_receipt(s, path)))
    if args.mode == 'pilot':
        assert not passive_levels, 'Existing pilot requires endpoint reconciliation'
    elif args.mode == 'resume':
        cfg['reconciliation'] = cfg.get('reconciliation', work + '/wifi-reconciliation-20261009.json')
        proof = json.loads(read_launch_receipt(s, cfg['reconciliation']))
        assert proof['status'] == 'RECONCILED_NUMERICAL_FAILURE'
        assert proof['workers'] == [] and proof['checkpoint_reopen_verified']
        assert {r['level'] for r in passive_levels} == set(proof['excluded_levels'])
        assert all(r['status'] in ('STOPPED_REQUIRES_REVIEW', 'NUMERICAL_FAILURE_UNQUALIFIED')
                   for r in passive_levels)
    else:
        assert len(passive_levels) == 1 and passive_levels[0]['status'] == 'SMOKE_VERIFIED'
        pilot = json.loads(read_launch_receipt(s, work + '/pilot-manifest.json'))
        assert pilot['status'] == 'SMOKE_VERIFIED', 'Pilot controller is not terminal'
    selected = '@(' + ','.join(psquote(row['level']) for row in cfg['meshes']) + ')'
    guard = work + '/launch-preflight-' + rid + '.json'
    stage = work + '/controller/' + rid
    preflight_script = work + '/controller/preflight-' + rid + '.ps1'
    preflight_code = ("$ErrorActionPreference='Stop'\n"
        '$workers=@(Get-CimInstance Win32_Process | Where-Object {'
        "$_.Name -match 'python' -and $_.CommandLine -like '*run_phase10_mesh_family*'})\n"
        '$manifests=@(Get-ChildItem -LiteralPath ' + psquote(work)
        + " -Filter 'manifest.json' -Recurse | Where-Object {$_.Directory.Name -in "
        + selected + "} | ForEach-Object {"
        '$m=Get-Content -LiteralPath $_.FullName -Raw|ConvertFrom-Json;'
        '[pscustomobject]@{path=[string]$_.FullName;status=[string]$m.status;level=[string]$m.level}})\n'
        '@{workers=@($workers|Select-Object ProcessId,Name);manifests=$manifests;'
        'common_sha256=(Get-FileHash -LiteralPath ' + psquote(cfg['common_case'])
        + ').Hash;batch_exists=(Test-Path -LiteralPath '
        + psquote(work + '/batch-manifest.json') + ')} | ConvertTo-Json -Depth 3 | '
        'Set-Content -LiteralPath ' + psquote(guard) + ' -Encoding Ascii\n'
        'if(-not $workers.Count){New-Item -ItemType Directory -Path '
        + psquote(stage) + ' -ErrorAction Stop | Out-Null}\n')
    write_ascii_text_new(s, preflight_script, preflight_code)
    command = ('powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'
               + preflight_script + '"')
    s.scheme.eval('(system "' + quote_scheme_string(command) + '")')
    preflight = json.loads(read_launch_receipt(s, guard))
    (OUT / ('launch-preflight-' + rid + '.json')).write_text(json.dumps(preflight, indent=2))
    assert not preflight['workers'], 'Existing controller requires reconciliation'
    assert preflight['common_sha256'].lower() == cfg['common_case_sha256'].lower()
    if args.mode != 'resume':
        assert not preflight['batch_exists'], 'Existing batch requires reconciliation'
    else:
        assert preflight['batch_exists']
    levels = preflight['manifests']
    if args.mode == 'pilot':
        assert not levels, 'Existing pilot requires endpoint reconciliation'
    elif args.mode == 'resume':
        assert {r['level'] for r in levels} == set(proof['excluded_levels'])
        assert all(r['status'] in ('STOPPED_REQUIRES_REVIEW', 'NUMERICAL_FAILURE_UNQUALIFIED')
                   for r in levels)
    else:
        assert len(levels) == 1 and levels[0]['status'] == 'SMOKE_VERIFIED'
    script = stage + '/run_phase10_mesh_family-' + rid + '.py'
    config = work + '/run-config-' + rid + '.json'
    source = (ROOT / 'scripts/setup/run_phase10_mesh_family.py').read_text()
    dependency = (ROOT / 'src/pyansys_fluent/execution_contract.py').read_text()
    write_ascii_text_new(s, stage + '/execution_contract.py', dependency)
    write_ascii_text_new(s, script, source)
    write_ascii_text_new(s, config, json.dumps(cfg, indent=2))
    files = launcher_files(work, rid, script, config, args.mode, port,
                           cfg.get('host_python', HOST_PYTHON))
    for key in ['launcher', 'cim']:
        write_ascii_text_new(s, files[key], files[key + '_text'])
    transient = ("Start-Sleep -Seconds 15;$env:PHASE10_API_PORT=" + psquote(str(port))
        + ';$env:PHASE10_API_PASSWORD=' + psquote(os.environ['MESH_API_PASSWORD'])
        + ';& ' + psquote(files['launcher']))
    encoded = base64.b64encode(transient.encode('utf-16le')).decode()
    command = ('powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'
        + files['cim'] + '" -EncodedCommand ' + encoded)
    assert len(command) < 1800
    intent = {k: v for k, v in files.items() if not k.endswith('_text')}
    intent.update(status='DISPATCHING', mode=args.mode, script=script, config=config,
        port=port, credentials_in_files=False, command_chars=len(command),
        runner_sha256=hashlib.sha256(source.encode()).hexdigest())
    (OUT / 'current-launch.json').write_text(json.dumps(intent, indent=2))
    s.scheme.eval('(system "' + quote_scheme_string(command) + '")')
    created = json.loads(read_launch_receipt(s, files['cim_receipt']))
    assert created['ReturnValue'] == 0
    intent.update(status='DETACHED_PROCESS_CREATED', launcher_process=created)
    (OUT / 'current-launch.json').write_text(json.dumps(intent, indent=2))
    print(json.dumps(intent), flush=True)


if __name__ == '__main__':
    main()
