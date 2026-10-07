"""Move the owned film controller to Server 3 without repeating a solve.

Uploads executable sources and the completed machine record. Credentials are
passed only to a restricted temporary launcher, then held in child environments.
"""
from pathlib import Path, PureWindowsPath
import base64
import hashlib
import io
import json
import sys
import uuid
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import continue_phase72a_slit154k_film as run
from pyansys_fluent.stage4_native import ensure_remote_directory, write_remote_text_new, quote_scheme_string, remote_text_read
from pyansys_fluent.connection import resolve_connection_kwargs

HOST_REPO = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\S3Film-20261006')
HOST_PYTHON = run.WORK / 'controller-venv/Scripts/python.exe'
HOST_OUT = HOST_REPO / PureWindowsPath(str(run.OUT.relative_to(run.ref.ROOT.parent)))


def ps_quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def system(s, command):
    return s.scheme.eval('(system "' + quote_scheme_string(command) + '")')


def convert(value):
    if isinstance(value, dict):
        return {k: convert(v) for k, v in value.items()}
    if isinstance(value, list):
        return [convert(v) for v in value]
    if isinstance(value, str) and str(run.ref.ROOT.parent) in value:
        return value.replace(str(run.ref.ROOT.parent), str(HOST_REPO)).replace('/', '\\')
    return value


def upload_bundle(s):
    if not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Handoff requires idle Fluent at its verified paired checkpoint')
    m = json.loads((run.OUT / 'run-manifest.json').read_text())
    if run.ref.native_iteration(s) != m['verified_native_end']:
        raise RuntimeError('Handoff native iteration differs')
    endpoint = json.loads((Path(m['active_output']) / f"endpoint-N{m['verified_native_end']}.json").read_text())
    run.ref.require_match(run.ref.readback(s), endpoint['state']['readback'])
    if run.ref.film(s) != endpoint['film']:
        raise RuntimeError('Handoff native film clock differs')
    m.update(status='CONTROLLER_HANDOFF_READY', execution_host='SERVER3_WINDOWS',
             host_repo=str(HOST_REPO), controller_handoff_reason='Remove dependency on the Mac network and sleep state')
    run.ref.dump(run.OUT / 'run-manifest.json', m)
    blob = io.BytesIO()
    count = 0
    with zipfile.ZipFile(blob, 'w', zipfile.ZIP_DEFLATED) as archive:
        files = []
        for folder in ['src', 'scripts/setup', 'scripts/analysis', 'scripts/post', 'scripts/inspection']:
            files.extend((run.ref.ROOT / folder).rglob('*.py'))
        files.extend(run.OUT.rglob('*'))
        files.append(run.SOURCE)
        files.extend(run.RESULTS.parent.glob('*.md'))
        for path in sorted(set(files)):
            if not path.is_file() or path.suffix == '.tmp' or path.name in ['stop-request.json', 'watcher-ready.json', 'live-supervision.json', 'supervisor-exit.json', 'host-deployment.json', 'host-launch.json']:
                continue
            relative = path.relative_to(run.ref.ROOT.parent).as_posix()
            content = path.read_bytes()
            if path.suffix == '.json':
                content = (json.dumps(convert(json.loads(content)), indent=2, default=str) + '\n').encode()
            archive.writestr(relative, content)
            count += 1
    payload = blob.getvalue()
    token = uuid.uuid4().hex[:8]
    package = run.WORK / f'controller-bundle-{token}.zip'
    encoded = run.WORK / f'controller-bundle-{token}.b64'
    write_remote_text_new(s, str(encoded), base64.b64encode(payload).decode('ascii'))
    script = run.WORK / f'expand-controller-{token}.ps1'
    text = "$ErrorActionPreference = 'Stop'\n[IO.File]::WriteAllBytes(" + ps_quote(package) + ",[Convert]::FromBase64String([IO.File]::ReadAllText(" + ps_quote(encoded) + ")))\nExpand-Archive -LiteralPath " + ps_quote(package) + ' -DestinationPath ' + ps_quote(HOST_REPO) + " -Force\n"
    write_remote_text_new(s, str(script), text)
    print('Private launcher written; applying file permissions', flush=True)
    expansion_log = run.WORK / f'expand-controller-{token}.log'
    system(s, 'cmd /c powershell -NoProfile -ExecutionPolicy Bypass -File "' + str(script) + '" > "' + str(expansion_log) + '" 2>&1')
    from pyansys_fluent.common import remote_file_exists
    if not remote_file_exists(s, str(HOST_REPO / 'PyAnsys/scripts/setup/continue_phase72a_slit154k_film.py')):
        raise RuntimeError('Controller source extraction failed: ' + remote_text_read(s, str(expansion_log))[-2000:])
    receipt = {'host_repo': str(HOST_REPO), 'host_python': str(HOST_PYTHON), 'host_output': str(HOST_OUT),
               'bundle_file_count': count, 'bundle_bytes': len(payload),
               'bundle_sha256': hashlib.sha256(payload).hexdigest(), 'native_iteration': m['verified_native_end'],
               'film_time_s': endpoint['film']['film_elapsed_time'], 'reopen_source': 'MATCHED_VERIFIED_ENDPOINT',
               'new_solve_calls': 0, 'credentials_in_bundle': False}
    run.ref.dump(run.OUT / 'host-deployment.json', receipt)
    return receipt


def launch(s):
    details = resolve_connection_kwargs('3', start_transcript=False)
    if 'server_info_file_name' in details:
        raise RuntimeError('Use explicit Server 3 endpoint credentials for the server-local launcher')
    token = uuid.uuid4().hex[:8]
    script = run.WORK / f'private-launch-controller-{token}.ps1'
    pid_path = run.WORK / f'host-controller-pids-{token}.json'
    controller = HOST_REPO / 'PyAnsys/scripts/setup/continue_phase72a_slit154k_film.py'
    watcher = HOST_REPO / 'PyAnsys/scripts/setup/watch_phase72a_slit154k_film.py'
    stdout = run.WORK / 'host-controller.stdout.log'
    stderr = run.WORK / 'host-controller.stderr.log'
    watch_stdout = run.WORK / 'host-watcher.stdout.log'
    watch_stderr = run.WORK / 'host-watcher.stderr.log'
    values = {'FLUENT_IP3': details['ip'], 'FLUENT_PORT3': details['port'], 'FLUENT_PASSWORD3': details['password'],
              'FLUENT_ALLOW_REMOTE_HOST3': str(details['allow_remote_host']).lower(),
              'FLUENT_INSECURE_MODE3': str(details['insecure_mode']).lower()}
    text = "$ErrorActionPreference = 'Stop'\n"
    for key, value in values.items():
        text += '$env:' + key + ' = ' + ps_quote(value) + '\n'
    text += "$c = Start-Process -FilePath " + ps_quote(HOST_PYTHON) + " -ArgumentList '-u'," + ps_quote(controller) + ",'resume-supervise','--watcher-gate' -WindowStyle Hidden -RedirectStandardOutput " + ps_quote(stdout) + ' -RedirectStandardError ' + ps_quote(stderr) + ' -PassThru\n'
    text += "$w = Start-Process -FilePath " + ps_quote(HOST_PYTHON) + " -ArgumentList '-u'," + ps_quote(watcher) + ",'--controller-pid',$c.Id -WindowStyle Hidden -RedirectStandardOutput " + ps_quote(watch_stdout) + ' -RedirectStandardError ' + ps_quote(watch_stderr) + ' -PassThru\n'
    text += '@{controller_pid=$c.Id; watcher_pid=$w.Id; execution_host=\'SERVER3_WINDOWS\'} | ConvertTo-Json | Set-Content -LiteralPath ' + ps_quote(pid_path) + '\n'
    text += 'Remove-Item -LiteralPath $PSCommandPath -Force\n'
    write_remote_text_new(s, str(script), text)
    # Restrict the launcher before execution. The password is never logged or
    # passed on a command line; the launcher removes itself after process start.
    acl = 'cmd /c powershell -NoProfile -Command "$me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe ' + ps_quote(script) + " /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null\""
    system(s, acl)
    print('Starting detached server launcher', flush=True)
    # Fluent must release its Scheme command before either child connects to
    # its main-thread services. Waiting for PowerShell here can deadlock that
    # connection. Read the receipt only after the detached launcher returns.
    system(s, 'cmd /c start "S3FilmLauncher" /min powershell -NoProfile -ExecutionPolicy Bypass -File "' + str(script) + '"')
    import time
    from pyansys_fluent.common import remote_file_exists
    for _ in range(60):
        if remote_file_exists(s, str(pid_path)):
            break
        time.sleep(1)
    else:
        raise RuntimeError('Detached launcher did not write its process receipt; inspect server logs before retrying')
    receipt = json.loads(remote_text_read(s, str(pid_path)))
    receipt.update(controller_stdout=str(stdout), controller_stderr=str(stderr), watcher_stdout=str(watch_stdout),
                   watcher_stderr=str(watch_stderr), host_repo=str(HOST_REPO), host_output=str(HOST_OUT))
    run.ref.dump(run.OUT / 'host-launch.json', receipt)
    return receipt


def main():
    run.configure()
    s = run.source.attach()
    if sys.argv[1] == 'upload':
        result = upload_bundle(s)
    elif sys.argv[1] == 'launch':
        result = launch(s)
    else:
        raise ValueError(sys.argv[1])
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
