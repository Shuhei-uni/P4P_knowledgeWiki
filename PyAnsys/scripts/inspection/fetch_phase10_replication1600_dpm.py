"""Retrieve byte-identical DPM evidence after terminal/idle/controller proof."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'PyAnsys/scripts/setup'),str(ROOT/'PyAnsys/scripts/inspection'),
             str(ROOT/'PyAnsys/src'),str(ROOT/'PyAnsys/src/pyansys_fluent')]
from deploy_phase10_bf01 import Bridge,psquote
from extract_phase10_predivergence_fields import attach,counter
from pyansys_fluent.remote_text import write_ascii_text_new,read_text
import probe_phase10_native_receipts as passive
import run_phase10_mesh_family as core


def main():
    out=ROOT/'PyAnsys/output/phase10-single-inlet-mesh-convergence'
    limit=int(sys.argv[sys.argv.index('--max-tracking-steps')+1]) if '--max-tracking-steps' in sys.argv else None
    name='DPM' if limit is None else 'DPM-limit'+str(limit)
    dest=out/('replication1600-M04/'+name+'-evidence')
    launch_path=out/('replication1600-M04/'+name+'-launch.json')
    cfg=json.loads((out/'run-config.json').read_text());launch=json.loads(launch_path.read_text())
    bridge=Bridge(cfg)
    try:manifest=passive.read_receipt(bridge.stub,launch['work']+'/manifest.json',bridge.metadata,262144)
    finally:bridge.channel.close()
    assert manifest['status']=='DPM_TRACKING_COMPLETE_EVIDENCE_PENDING' and manifest['transcript_closed']
    s=attach(cfg)
    try:
        assert not s.settings.solution.run_calculation.iterating() and counter(s)==1500
        core.require_state_same(core.state(s),manifest['settings_readback'])
    finally:s._fluent_connection._channel.close()
    bridge=Bridge(cfg)
    try:
        work=launch['work'];tag=uuid.uuid4().hex[:8];ps=work+'/retrieve-'+tag+'.ps1';bundle=ps+'.json'
        files={'manifest.json':work+'/manifest.json','DPM-tracking.trn':manifest['transcript'],
               'controller-stdout.log':launch['stdout'],'controller-stderr.log':launch['stderr']}
        files.update({path.replace('\\','/').rsplit('/',1)[-1]:path for path in manifest['report_files'].values()})
        expected={path.replace('\\','/').rsplit('/',1)[-1]:manifest['report_sha256'][name] for name,path in manifest['report_files'].items()}
        expected['DPM-tracking.trn']=manifest['transcript_sha256']
        code="$ErrorActionPreference='Stop'\ntry {\n"
        code+="$workers=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -match 'run_phase10|resume_phase10|phase10_core'})\nif($workers.Count -gt 0){throw 'Phase10 writer still active'}\n"
        for kind in ['case','data']:
            pair=manifest['final_pair'];code+='if((Get-FileHash -LiteralPath '+psquote(pair[kind])+' -Algorithm SHA256).Hash -ne '+psquote(pair[kind+'_sha256'])+'){throw "Final pair changed"}\n'
        code+='$rows=@()\n'
        for name,path in files.items():
            code+='$bytes=[IO.File]::ReadAllBytes('+psquote(path)+')\nif($bytes.Length -gt 524288){throw "Evidence file exceeds bound"}\n'
            code+='$h=(Get-FileHash -LiteralPath '+psquote(path)+' -Algorithm SHA256).Hash.ToLower()\n'
            if name in expected:code+='if($h -ne '+psquote(expected[name])+'){throw "Evidence hash changed"}\n'
            code+='$rows+=@{name='+psquote(name)+';path='+psquote(path)+';sha256=$h;bytes=$bytes.Length;base64=[Convert]::ToBase64String($bytes)}\n'
        code+='$payload=@{status="PASS";workers=@();final_pair_hashes_match=$true;files=$rows} | ConvertTo-Json -Depth 5\nif($payload.Length -gt 4000000){throw "Evidence bundle exceeds bound"}\n'
        code+='$payload | Set-Content -LiteralPath '+psquote(bundle)+' -Encoding Ascii\n'
        code+='} catch { @{status="FAIL";error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath '+psquote(bundle)+' -Encoding Ascii }\n'
        write_ascii_text_new(bridge,ps,code);bridge.shell_file(ps)
        data=json.loads(read_text(bridge,bundle));assert data['status']=='PASS',data
        raw=dest/'raw';raw.mkdir(parents=True,exist_ok=True)
        records=[]
        for row in data['files']:
            content=base64.b64decode(row['base64']);assert hashlib.sha256(content).hexdigest()==row['sha256']
            target=raw/row['name']
            if target.exists():assert target.read_bytes()==content,'Immutable raw evidence changed'
            else:target.write_bytes(content)
            records.append({k:v for k,v in row.items() if k!='base64'})
        receipt={'status':'PASS','native_manifest':work+'/manifest.json','files':records,
                 'controller_absent_verified':True,'solver_idle_verified':True,'iteration':1500,
                 'final_pair_hashes_match':True,'byte_identical_retrieval':True}
        (dest/'retrieval.json').write_text(json.dumps(receipt,indent=2)+'\n')
        launch.update(status=manifest['status'],controller_pid=manifest['controller_pid'],controller_exited_verified=True,
                      final_pair=manifest['final_pair'],DPM_completed_updates=1,solved_updates=0,evidence_retrieval=str(dest/'retrieval.json'))
        launch_path.write_text(json.dumps(launch,indent=2)+'\n')
        (out/'current-launch.json').write_text(json.dumps(launch,indent=2)+'\n')
        print(json.dumps({'status':'PASS','files':len(records),'DPM_completed_updates':1,'carrier_iteration':1500,'controller_absent':True}))
    finally:bridge.channel.close()


if __name__=='__main__':main()
