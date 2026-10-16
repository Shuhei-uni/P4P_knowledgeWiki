"""Reviewed, stepwise Server 6 film-transfer build. Never launches or exits Fluent."""
from pathlib import Path, PureWindowsPath
import argparse
import base64
import gzip
import hashlib
import json
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts/setup')]
from phase9_server6_slit_common import attach, run
from pyansys_fluent.remote_text import read_text, write_ascii_text_new
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256
from pyansys_fluent.common import remote_file_exists, quote_scheme_string

OUT = ROOT/'output/phase9-ewf-server6-997k/20261016'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\NonzeroEWF\20261016')


def quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def dump(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT/name
    assert not path.exists(), f'Reconcile existing receipt: {path}'
    path.write_text(json.dumps(value, indent=2, default=str)+'\n')


def idle(s):
    assert not s.settings.solution.run_calculation.iterating()
    run.require_idle(s)


def snapshot(s):
    # These names and the iteration expression were checked on live v252.
    return {'native_iteration':run.native_iteration(s),
            'current_iteration_rp':s.rp_vars('current-iteration'),
            'last_casefile_name':s.rp_vars('last-casefile-name'),
            'film':dict(s.rp_vars('wall-film/solution-state')),
            'equations':s.settings.solution.controls.equations.get_state()}


def upload(s, local, remote):
    """Chunk compressed ASCII profiles; verify the final host file hash."""
    assert not remote_file_exists(s, str(remote))
    text = base64.b64encode(gzip.compress(local.read_bytes())).decode('ascii')
    chunks=[]
    for i, start in enumerate(range(0, len(text), 60000)):
        part=WORK/(remote.name+f'.{i}.b64')
        write_ascii_text_new(s, str(part), text[start:start+60000])
        chunks.append(part)
    code=("import base64,gzip,pathlib\n"
          f"parts={list(map(str,chunks))!r}\n"
          "blob=''.join(pathlib.Path(p).read_text() for p in parts)\n"
          f"pathlib.Path({str(remote)!r}).write_bytes(gzip.decompress(base64.b64decode(blob)))\n")
    script=WORK/(remote.name+'.decode.py')
    write_ascii_text_new(s,str(script),code)
    host=json.loads((ROOT/'output/phase9-server6-slit154k/20261010/host-launch.json').read_text())
    assert remote_file_exists(s,host['host_python'])
    run.base.powershell(s,'& '+quote(host['host_python'])+' -E '+quote(script))
    h=remote_file_sha256(s,str(remote),str(WORK/(remote.name+'.sha256.txt')))
    assert h==hashlib.sha256(local.read_bytes()).hexdigest()
    return {'path':str(remote),'sha256':h,'bytes':local.stat().st_size}


def preflight(s):
    idle(s)
    before=snapshot(s)
    dump('live-inspection-'+str(time.time_ns())+'.json',before)
    ensure_remote_directory(s,str(WORK/'scratch'))
    evidence=WORK/'preflight-host.json'
    source=json.loads((ROOT/'output/phase9-mesh-convergence-server4/20261007/final-initial-bulk.json').read_text())
    paths={k:v['path'] for k,v in source['onedrive']['files'].items()}
    code=("$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | "
          "Where-Object {$_.Name -eq 'python.exe'} | ForEach-Object {"
          "$m=[regex]::Matches($_.CommandLine,'[A-Za-z0-9_\\-]+\\.py');"
          "@{pid=$_.ProcessId;scripts=@($m|ForEach-Object {$_.Value})}});"
          "$f=@{};")
    for k,path in paths.items():
        code+=(f"if(Test-Path -LiteralPath {quote(path)}){{$i=Get-Item -LiteralPath {quote(path)};"
               f"$f[{quote(k)}]=@{{path=$i.FullName;bytes=$i.Length;attributes=[string]$i.Attributes}}}};")
    code+='[IO.File]::WriteAllText('+quote(evidence)+",(@{python_processes=$p;receiver_files=$f;free_bytes=(Get-PSDrive C).Free}|ConvertTo-Json -Depth 8),[Text.Encoding]::ASCII)"
    # A lost acknowledgement does not prove that the previous host check failed.
    if not remote_file_exists(s,str(evidence)):
        run.base.powershell(s,code)
    result={'state':before,'host':json.loads(read_text(s,str(evidence)))}
    dump('preflight.json',result)
    print(json.dumps(result,indent=2),flush=True)


def preserve(s):
    idle(s)
    assert not (OUT/'preserved-current.json').exists()
    before=snapshot(s)
    # Preserve before host-process inventory or shell-based directory creation.
    # This existing host-local parent is recorded in prior Server 6 receipts.
    profile=PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")'))
    folder=profile/'Documents/FluentRuns'
    assert remote_file_exists(s,str(folder))
    stamp=str(time.time_ns())
    case=folder/('preserved-before-nonzero-ewf-'+stamp+'.cas.h5')
    data=str(case)[:-7]+'.dat.h5'
    assert not remote_file_exists(s,str(case)) and not remote_file_exists(s,data)
    dump('preservation-intent-'+stamp+'.json',{'before':before,'case':str(case),'data':data})
    s.settings.file.write_case(file_name=str(case))
    dump('preservation-case-written-'+stamp+'.json',{'case':str(case)})
    s.settings.file.write_data(file_name=data)
    assert remote_file_exists(s,str(case)) and remote_file_exists(s,data)
    # Persist the paired-save acknowledgement before shell-based hash checks.
    pair={'case':str(case),'data':data,'native_iteration':before['native_iteration']}
    dump('preservation-pair-written-'+stamp+'.json',{'pair':pair,'after':snapshot(s)})
    for key in ['case','data']:
        pair[key+'_sha256']=remote_file_sha256(s,pair[key],str(folder/(f'nonzero-ewf-preserved-{stamp}-{key}.sha256.txt')))
    dump('preserved-current.json',{'before':before,'pair':pair,'after':snapshot(s)})
    print('CURRENT_ENDPOINT_PRESERVED',flush=True)


def stage(s):
    idle(s)
    assert (OUT/'preserved-current.json').exists()
    source=json.loads((ROOT/'output/phase9-mesh-convergence-server4/20261007/final-initial-bulk.json').read_text())
    pairs={}
    for k,v in source['onedrive']['files'].items():
        dest=WORK/('receiver-N8580.'+('cas' if k=='case' else 'dat')+'.h5')
        if not remote_file_exists(s,str(dest)):
            run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(v['path'])+' -Destination '+quote(dest))
        h=remote_file_sha256(s,str(dest),str(WORK/'scratch'/(k+'-receiver-'+str(time.time_ns())+'.sha256.txt')))
        assert h==v['sha256']
        pairs[k]=str(dest);pairs[k+'_sha256']=h
    profile=ROOT/'output/phase9-ewf-server6-997k/20261015/receiver-2_6M-N8580-normal-aware/receiver-film-candidate.prof'
    staged=upload(s,profile,WORK/'receiver-film-candidate.prof')
    pairs['native_iteration']=8580
    dump('staged.json',{'pair':pairs,'profile':staged})
    print('RECEIVER_PAIR_AND_PROFILE_HASH_VERIFIED',flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('step',choices=['preflight','preserve','stage'])
    args=p.parse_args()
    try:
        s=attach()
        globals()[args.step](s)
    except Exception as exc:
        dump('failure-'+str(time.time_ns())+'.json',{'step':args.step,
             'exception':str(exc),'traceback':traceback.format_exc(),
             'recovery':'Reconcile remote step before replay; never assume a lost acknowledgement means no effect'})
        raise


if __name__=='__main__':
    main()
