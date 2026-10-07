"""Deploy the Phase 8 Stage 2 controller onto Server 2."""
from pathlib import Path, PureWindowsPath
import base64
import hashlib
import io
import json
import sys
import time
import uuid
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase8_stage2_f2_simple as run
run.HOST_PYTHON=run.WORK/"controller-venv/Scripts/python.exe"
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.stage4_native import write_remote_text_new, quote_scheme_string
from pyansys_fluent.remote_text import write_ascii_text_new

HOST_REPO=run.WORK/'controller-repo'
HOST_OUT=HOST_REPO/'PyAnsys/output/phase8-stage2/20261007'


def quote(value):return "'"+str(value).replace("'","''")+"'"
def system(s,command):return s.scheme.eval('(system "'+quote_scheme_string(command)+'")')


def convert(value):
    if isinstance(value,dict):return {k:convert(v) for k,v in value.items()}
    if isinstance(value,list):return [convert(v) for v in value]
    if isinstance(value,str) and str(run.ROOT.parent) in value:
        return value.replace(str(run.ROOT.parent),str(HOST_REPO)).replace('/','\\')
    return value


def upload(s):
    if not s.settings.solution.run_calculation.iterate.is_active():raise RuntimeError('Require idle solver')
    assert json.loads((run.OUT/'build.json').read_text())['status']=='PREPARED_REOPEN_VERIFIED'
    blob=io.BytesIO();count=0
    with zipfile.ZipFile(blob,'w',zipfile.ZIP_DEFLATED) as archive:
        files=[]
        for folder in ['src','scripts/setup','scripts/analysis','scripts/post','scripts/inspection','scripts/orchestration']:
            files.extend((run.ROOT/folder).rglob('*.py'))
        files.extend(run.OUT.rglob('*'))
        for path in sorted(set(files)):
            if not path.is_file() or path.suffix=='.tmp':continue
            data=path.read_bytes()
            if path.suffix=='.json':data=(json.dumps(convert(json.loads(data)),indent=2)+'\n').encode()
            archive.writestr(path.relative_to(run.ROOT.parent).as_posix(),data);count+=1
        spec={'job':{'id':getattr(run,'HOST_JOB_ID','phase8-stage2-f2-simple-20261007'),'mode':'utility',
                     'manifest':str(HOST_OUT/'job-manifest.json'),'worker_log':str(HOST_OUT/'worker.log')},
              'runner':{'command':[str(run.HOST_PYTHON),'-u',str(HOST_REPO/'PyAnsys/scripts/setup'/getattr(run,'HOST_RUNNER','run_phase8_stage2_f2_simple.py')),'run'],
                        'cwd':str(HOST_REPO),'log':str(HOST_OUT/'runner.log')},
              'completion':{'required_files':[str(HOST_OUT/name) for name in ['run-manifest.json','report-histories.json','final-reopen.json']],
                            'verifier_command':[str(run.HOST_PYTHON),str(HOST_REPO/'PyAnsys/scripts/inspection'/getattr(run,'HOST_VERIFIER','verify_phase8_stage2.py'))],
                            'verifier_cwd':str(HOST_REPO),'verifier_log':str(HOST_OUT/'verifier.log')},
              'codex':{'enabled':False},
              'originating_task':getattr(run,'HOST_TASK','Phase 8 Stage 2 F2 SIMPLE; Server 2 only; 5000 total updates')}
        archive.writestr('phase8-stage2-job.json',json.dumps(spec,indent=2)+'\n')
    payload=blob.getvalue();token=uuid.uuid4().hex[:8]
    encoded=run.WORK/('controller-'+token+'.b64');package=run.WORK/('controller-'+token+'.zip')
    write_remote_text_new(s,str(encoded),base64.b64encode(payload).decode('ascii'))
    run.powershell(s,"$ErrorActionPreference='Stop'; [IO.File]::WriteAllBytes("+quote(package)+",[Convert]::FromBase64String([IO.File]::ReadAllText("+quote(encoded)+"))); Expand-Archive -LiteralPath "+quote(package)+' -DestinationPath '+quote(HOST_REPO)+' -Force')
    assert run.remote_file_exists(s,str(HOST_REPO/'phase8-stage2-job.json'))
    receipt={'host_repo':str(HOST_REPO),'host_output':str(HOST_OUT),'host_python':str(run.HOST_PYTHON),
             'bundle_files':count,'bundle_bytes':len(payload),'bundle_sha256':hashlib.sha256(payload).hexdigest(),
             'credentials_in_bundle':False,'mode':'utility','completion':getattr(run,'HOST_COMPLETION','N5000 save/reopen; hashes; full report coverage')}
    run.dump(run.OUT/'host-deployment.json',receipt);return receipt


def launch(s):
    if not s.settings.solution.run_calculation.iterate.is_active():raise RuntimeError('Require idle solver')
    if run.remote_file_exists(s,str(HOST_OUT/'job-manifest.json')):raise RuntimeError('Reconcile existing host job before relaunch')
    details=resolve_connection_kwargs('2',start_transcript=False)
    if 'server_info_file_name' in details:raise RuntimeError('Explicit Server 2 endpoint required')
    token=uuid.uuid4().hex[:8];script=run.WORK/('private-launch-'+token+'.ps1');pid=run.WORK/('host-pid-'+token+'.json')
    stdout=run.WORK/'host-worker.stdout.log';stderr=run.WORK/'host-worker.stderr.log'
    values={'FLUENT_IP2':details['ip'],'FLUENT_PORT2':details['port'],'FLUENT_PASSWORD2':details['password'],
            'FLUENT_ALLOW_REMOTE_HOST2':str(details['allow_remote_host']).lower(),'FLUENT_INSECURE_MODE2':str(details['insecure_mode']).lower()}
    text="$ErrorActionPreference='Stop'\n"
    for key,value in values.items():text+='$env:'+key+' = '+quote(value)+'\n'
    worker=HOST_REPO/'PyAnsys/scripts/orchestration/run_and_handoff.py'
    text+='$p = Start-Process -FilePath '+quote(run.HOST_PYTHON)+" -ArgumentList '-u',"+quote(worker)+",'--job',"+quote(HOST_REPO/'phase8-stage2-job.json')+",'--worker' -WindowStyle Hidden -RedirectStandardOutput "+quote(stdout)+' -RedirectStandardError '+quote(stderr)+' -PassThru\n'
    text+="[IO.File]::WriteAllText("+quote(pid)+",(@{worker_pid=$p.Id; execution_host='SERVER2_WINDOWS'} | ConvertTo-Json),[Text.Encoding]::ASCII)\nRemove-Item -LiteralPath $PSCommandPath -Force\n"
    write_ascii_text_new(s,str(script),text)
    system(s,'cmd /c powershell -NoProfile -Command "$me=[Security.Principal.WindowsIdentity]::GetCurrent().Name; & icacls.exe '+quote(script)+" /inheritance:r /grant:r ($me + ':(F)') 'SYSTEM:(F)' | Out-Null\"")
    command='powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+str(script)+'"'
    run.powershell(s,"$result=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="+quote(command)+";CurrentDirectory="+quote(run.WORK)+"}; if ($result.ReturnValue -ne 0) {throw 'Detached controller launch failed'}")
    for _ in range(30):
        if run.remote_file_exists(s,str(pid)):break
        time.sleep(1)
    else:raise RuntimeError('No launcher receipt; inspect before retry')
    receipt=json.loads(run.read_text(s,str(pid)))
    receipt.update(host_output=str(HOST_OUT),stdout=str(stdout),stderr=str(stderr),job_spec=str(HOST_REPO/'phase8-stage2-job.json'))
    run.dump(run.OUT/'host-launch.json',receipt);return receipt


if __name__=='__main__':
    s=run.attach()
    result=upload(s) if sys.argv[1]=='upload' else launch(s)
    print(json.dumps(result),flush=True)
