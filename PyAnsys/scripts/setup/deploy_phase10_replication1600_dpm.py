"""Guarded native DPM deployment; credentials only in transient environment."""
import base64
import copy
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'PyAnsys/scripts/setup'),str(ROOT/'PyAnsys/src'),str(ROOT/'PyAnsys/src/pyansys_fluent')]
from prepare_phase10_replication1600_dpm import native_proof
from deploy_phase10_bf01 import Bridge,psquote
from deploy_phase10_mesh_family import launcher_files
from pyansys_fluent.remote_text import write_ascii_text_new,read_text
from pyansys_fluent.common import quote_scheme_string


def main():
    out=ROOT/'PyAnsys/output/phase10-single-inlet-mesh-convergence';dest=out/'replication1600-M04'
    limit=int(sys.argv[sys.argv.index('--max-tracking-steps')+1]) if '--max-tracking-steps' in sys.argv else None
    if limit is not None:assert limit in (100000,1000000),'Unreviewed sensitivity limit'
    launch=dest/('DPM-launch.json' if limit is None else 'DPM-limit'+str(limit)+'-launch.json')
    assert not launch.exists(),'Reconcile previous DPM launch before replay'
    cfg=json.loads((out/'run-config.json').read_text())
    prepared=json.loads((dest/'spiral-recovered-parent/DPM-preparation-receipt.json').read_text())
    pre=json.loads((dest/('DPM-live-preflight.json' if limit is None else 'DPM-limit-live-preflight.json')).read_text())
    assert prepared['reopen_verified'] and pre['idle'] and pre['iteration']==1500
    assert pre['settings_match_prepared_pair'] if limit is None else pre['settings_match_preserved_DPM_10000']
    assert prepared['DPM_updates']==0 and not prepared['tracking_issued']
    parent=prepared['pair'];settings_before=prepared['settings'];settings=copy.deepcopy(settings_before)
    if limit is not None:
        prior=json.loads((dest/'DPM-evidence/raw/manifest.json').read_text())
        assert prior['DPM_completed_updates']==1 and prior['strict_reopen_verified']
        parent=prior['final_pair'];settings_before=prior['settings_readback'];settings=copy.deepcopy(settings_before)
        settings['models']['discrete_phase']['tracking']['max_num_steps']=limit
    rid=uuid.uuid4().hex[:8];work=str(Path(prepared['work']).parent).replace('\\','/')+('/DPM-run-' if limit is None else '/DPM-limit'+str(limit)+'-')+rid
    pairs=[parent] if limit is None else [parent,prepared['pair']]
    proof=native_proof(cfg,[(p[kind],p[kind+'_sha256']) for p in pairs for kind in ['case','data']],work)
    bridge=Bridge(cfg)
    try:
        # Reuse the exact verified host/runtime bootstrap, without credentials.
        old=json.loads((dest/'carrier-launch.json').read_text())
        wrapper=read_text(bridge,old['script'])
        bootstrap=[line for line in wrapper.splitlines() if line.startswith("os.environ['PHASE10_EXTRA_PACKAGES'] =")]
        runner=(ROOT/'PyAnsys/scripts/setup/run_phase10_replication1600_dpm.py').read_text()
        if bootstrap:runner=runner.replace('import phase10_core as core','\n'.join(bootstrap)+'\nimport phase10_core as core')
        sources={'run_phase10_replication1600_dpm.py':runner,
                 'phase10_core.py':(ROOT/'PyAnsys/scripts/setup/run_phase10_mesh_family.py').read_text(),
                 'execution_contract.py':(ROOT/'PyAnsys/src/pyansys_fluent/execution_contract.py').read_text()}
        hashes={}
        for name,code in sources.items():
            path=work+'/'+name;write_ascii_text_new(bridge,path,code)
            assert read_text(bridge,path).replace('\r\n','\n')==code.replace('\r\n','\n')
            hashes[name]=hashlib.sha256(code.replace('\r\n','\n').encode('ascii')).hexdigest()
        # Validate native imports before launching the solver writer.
        ps=work+'/runtime-proof.ps1';runtime=work+'/runtime-proof.json'
        check='import sys,json,h5py,numpy,ansys.fluent.core as pf;sys.path.insert(0,'+repr(work)+');import phase10_core;print(json.dumps(dict(executable=sys.executable,pyfluent=pf.__version__)))'
        write_ascii_text_new(bridge,ps,'& '+psquote(cfg['host_python'])+' -c '+psquote(check)+' | Set-Content -LiteralPath '+psquote(runtime)+' -Encoding Ascii\nif($LASTEXITCODE -ne 0){throw "Native DPM runtime check failed"}\n')
        bridge.shell_file(ps);runtime_proof=json.loads(read_text(bridge,runtime));assert runtime_proof['pyfluent']=='0.42.0'
        carrier=json.loads((dest/'carrier-evidence/raw/manifest.json').read_text())
        native_cfg={'work':work,'ip':cfg['ip'],'port':cfg['port'],'parent':parent,
                    'settings':settings,'injection_names':prepared['settings']['injections'],
                    'carrier_reports':carrier['report_names'],'preflight':proof,
                    'source_limits':[prepared['historical_limit'],'Historical Fluent 2024 R2 versus current 2025 R2; carrier remains unqualified.']}
        experiment='R1600_DPM'
        if limit is not None:
            experiment='R1600_DPM_LIMIT'
            native_cfg.update(experiment=experiment,settings_before=settings_before,
                              tracking_max_num_steps=limit,fresh_DPM_parent=prepared['pair'])
            native_cfg['source_limits'].append('Tracking-limit sensitivity; original 10000-step replication remains preserved.')
        config=work+'/run-config.json';write_ascii_text_new(bridge,config,json.dumps(native_cfg,indent=2)+'\n')
        script=work+'/run_phase10_replication1600_dpm.py'
        files=launcher_files(work,rid,script,config,'R1600_DPM',cfg['port'],cfg['host_python'])
        for key in ['launcher','cim']:files[key]=files[key].replace('/controller/','/')
        for key in ['launcher','cim']:write_ascii_text_new(bridge,files[key],files[key+'_text'])
        intent={'experiment':experiment,'status':'DEPLOYED_NOT_LAUNCHED','work':work,'script':script,'config':config,
                'port':cfg['port'],'source_hashes_LF':hashes,'source_readback_verified':True,'preflight':proof,
                'runtime':runtime_proof,'credentials_in_files':False,'parent_preparation_manifest':prepared['native_manifest'],
                'created_utc':datetime.now(timezone.utc).isoformat(),**{k:v for k,v in files.items() if not k.endswith('_text')}}
        if limit is not None:intent['tracking_max_num_steps']=limit
        launch.write_text(json.dumps(intent,indent=2)+'\n')
        if '--launch' not in sys.argv:print(json.dumps({'status':intent['status'],'work':work}));return
        command='$env:PHASE10_API_PASSWORD='+psquote(os.environ['PHASE10_API_PASSWORD'])+'; & '+psquote(files['launcher'])
        encoded=base64.b64encode(command.encode('utf-16le')).decode('ascii')
        cmd='powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+files['cim']+'" -EncodedCommand '+encoded
        bridge.eval('(system "'+quote_scheme_string(cmd)+'")')
        created=json.loads(read_text(bridge,files['cim_receipt']));assert created['ReturnValue']==0
        intent.update(status='DETACHED_PROCESS_CREATED',launcher_process=created)
        launch.write_text(json.dumps(intent,indent=2)+'\n');(out/'current-launch.json').write_text(json.dumps(intent,indent=2)+'\n')
        print(json.dumps({'status':intent['status'],'work':work,'launcher_process':created}))
    finally:bridge.channel.close()


if __name__=='__main__':main()
