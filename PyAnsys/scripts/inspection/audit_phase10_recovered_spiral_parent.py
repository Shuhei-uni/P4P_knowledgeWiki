"""Load a hash-proven recovered parent, export settings, then restore M04 N1500.

No initialization, iterations, DPM update or source-file writes are issued.
The source keeps its archived settings; comparison and interpretation are offline.
"""
from pathlib import Path
import hashlib
import json
import sys
import uuid

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'PyAnsys/scripts/inspection'),str(ROOT/'PyAnsys/scripts/setup'),str(ROOT/'PyAnsys/src'),str(ROOT/'PyAnsys/src/pyansys_fluent')]
from extract_phase10_predivergence_fields import attach,counter
from deploy_phase10_bf01 import Bridge,psquote
from pyansys_fluent.remote_text import write_ascii_text_new,read_text
import run_phase10_mesh_family as core


def main():
    out=ROOT/'PyAnsys/output/phase10-single-inlet-mesh-convergence'
    dest=out/'replication1600-M04/spiral-recovered-parent'
    recovery=json.loads((dest/'recovery.json').read_text())
    cfg=json.loads((out/'run-config.json').read_text())
    final=json.loads((out/'replication1600-M04/carrier-evidence/raw/manifest.json').read_text())
    restore=final['final_pair']
    source='C:/Users/qtra338/P4P/experiments/parallel-andy-studies/enthalpy-dpm-replication/workbench-predecessors/Punanto_injections/h1600_files/dp0/FFF/Fluent/4800-iterations-300412-1.cas.h5'
    assert final['completed_iteration']==1500
    receipt={'source':source,'source_sha256':recovery['case_sha256'],'restore_pair':restore,
        'solved_updates':0,'DPM_updates':0,'initializations':0,'source_loaded':False,'restored':False}
    path=dest/'live-audit-receipt.json'
    if path.exists():
        old=json.loads(path.read_text())
        assert not old['source_loaded'] and old['solved_updates']==0,'Prior source load requires reconciliation'
        previous=dest/'audit-inactive-report-attempt.json'
        if not previous.exists():
            previous.write_text(json.dumps({'receipt':old,'error':"InactiveObjectError: '<session>.settings.solution.report_definitions.compute' is currently inactive.",
                'diagnosis':'Human loaded baseline case after the prior M04 completion; source audit had not mutated the solver.'},indent=2)+'\n')
    def persist():path.write_text(json.dumps(receipt,indent=2)+'\n')
    persist()
    s=attach(cfg)
    try:
        assert not s.settings.solution.run_calculation.iterating()
        reports=s.settings.solution.report_definitions.single_valued_expression.get_object_names()
        if 'p10-iteration' in reports:
            assert counter(s)==1500
            core.require_state_same(core.state(s),final['settings_readback'])
            receipt['before_audit_state']='VERIFIED_M04_N1500'
        else:
            # Preserve the manually loaded case; solution validity decides
            # whether a data file can be preserved as well.
            count=s.fields.solution_variable_info.get_zones_info()['fluid'].count
            assert count==5578299,'Unexpected loaded mesh; preserve/reconcile separately'
            import time
            work=json.loads((out/'current-launch.json').read_text())['work']
            base=work+'/manual-baseline-before-spiral-audit-'+uuid.uuid4().hex[:8]
            valid=s.fields.field_data.is_data_valid()
            s.settings.file.write_case(file_name=base+'.cas.h5')
            saved={'case':base+'.cas.h5','data_valid':bool(valid),'cells':count}
            if valid:
                s.settings.file.write_data(file_name=base+'.dat.h5');saved['data']=base+'.dat.h5'
            receipt.update(before_audit_state='MANUAL_BASELINE_PRESERVED',manual_baseline_preserved=saved)
            persist()
    finally:s._fluent_connection._channel.close()
    bridge=Bridge(cfg)
    try:
        rid=uuid.uuid4().hex[:8]
        work=json.loads((out/'current-launch.json').read_text())['work']
        ps=work+'/parent-audit-preflight-'+rid+'.ps1';proof_path=ps+'.json'
        code="$ErrorActionPreference='Stop'\ntry {\n"
        code+="$workers=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -match 'run_phase10|resume_phase10|phase10_core'})\nif($workers.Count -gt 0){throw 'Existing Phase10 controller'}\n"
        for p,expected in [(source,recovery['case_sha256']),*[(restore[k],restore[k+'_sha256']) for k in ['case','data']]]:
            code+='if((Get-FileHash -LiteralPath '+psquote(p)+' -Algorithm SHA256).Hash -ne '+psquote(expected)+'){throw "Source or preserved pair hash mismatch"}\n'
        code+='$manual=@()\n'
        for kind in ['case','data']:
            p=receipt.get('manual_baseline_preserved',{}).get(kind)
            if p:code+='$manual+=@{kind='+psquote(kind)+';path='+psquote(p)+';sha256=(Get-FileHash -LiteralPath '+psquote(p)+' -Algorithm SHA256).Hash}\n'
        code+='@{status="PASS";workers=@();source_and_restore_hashes_match=$true;manual_preserved_hashes=$manual} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath '+psquote(proof_path)+' -Encoding Ascii\n'
        code+='} catch { @{status="FAIL";error=$_.Exception.Message} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath '+psquote(proof_path)+' -Encoding Ascii }\n'
        write_ascii_text_new(bridge,ps,code);bridge.shell_file(ps)
        proof=json.loads(read_text(bridge,proof_path));receipt['preflight']=proof;persist()
        assert proof['status']=='PASS',proof
    finally:bridge.channel.close()
    s=attach(cfg)
    loaded=False
    try:
        assert not s.settings.solution.run_calculation.iterating()
        if receipt['before_audit_state']=='VERIFIED_M04_N1500':assert counter(s)==1500
        else:assert s.fields.solution_variable_info.get_zones_info()['fluid'].count==5578299
        # Mark the restore requirement before dispatch, including partial loads.
        loaded=True
        s.settings.file.read_case(file_name=source)
        receipt['source_loaded']=True;persist()
        setup=s.settings.setup.get_state()
        export={'setup':setup,'methods':s.settings.solution.methods.get_state(),
            'controls':s.settings.solution.controls.get_state(),
            'residual_equations':s.settings.solution.monitor.residual.equations.get_state(),
            'cells':s.fields.solution_variable_info.get_zones_info()['fluid'].count,
            'injection_names':s.settings.setup.models.discrete_phase.injections.get_object_names(),
            'idle':not s.settings.solution.run_calculation.iterating()}
        assert export['cells']==2964593 and export['idle']
        assert len(export['injection_names'])==9 and len(set(export['injection_names']))==9
        (dest/'live-source-settings.json').write_text(json.dumps(export,indent=2)+'\n')
        receipt.update(status='SOURCE_SETTINGS_EXPORTED',source_cells=export['cells'],injection_count=9)
        persist()
    except BaseException as error:
        receipt.update(status='AUDIT_ERROR',error=type(error).__name__+': '+str(error));persist()
        raise
    finally:
        if loaded:
            s.settings.file.read_case(file_name=restore['case'])
            s.settings.file.read_data(file_name=restore['data'])
            assert counter(s)==1500
            core.require_state_same(core.state(s),final['settings_readback'])
            assert not s.settings.solution.run_calculation.iterating()
            receipt.update(restored=True,restored_iteration=1500,restored_settings_exact=True)
            if receipt.get('status')=='SOURCE_SETTINGS_EXPORTED':receipt['status']='AUDIT_EXPORTED_M04_RESTORED'
            persist()
        s._fluent_connection._channel.close()
    print(json.dumps({k:receipt.get(k) for k in ['status','source_loaded','source_cells','injection_count','restored','restored_iteration','solved_updates']}))


if __name__=='__main__':
    main()
