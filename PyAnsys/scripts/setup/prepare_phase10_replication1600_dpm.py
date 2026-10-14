"""Apply audited spiral Case 4 DPM settings to preserved M04 N1500.

No carrier iterations, initialization or particle tracking. Save a new pair,
reopen and compare settings. Restore the carrier pair on any setup failure.
"""
from pathlib import Path
import copy
import hashlib
import json
import sys
import uuid

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'PyAnsys/scripts/inspection'),str(ROOT/'PyAnsys/scripts/setup'),
             str(ROOT/'PyAnsys/scripts/analysis'),str(ROOT/'PyAnsys/src'),str(ROOT/'PyAnsys/src/pyansys_fluent')]
from extract_phase10_predivergence_fields import attach,counter
from deploy_phase10_bf01 import Bridge,psquote
from pyansys_fluent.remote_text import write_ascii_text_new,read_text
from compare_phase10_recovered_spiral_settings import differences,carrier_boundary
import run_phase10_mesh_family as core

OUT=ROOT/'PyAnsys/output/phase10-single-inlet-mesh-convergence'
DEST=OUT/'replication1600-M04/spiral-recovered-parent'


def overlay(base,delta):
    value=copy.deepcopy(base)
    for key,item in delta.items():
        value[key]=overlay(value[key],item) if isinstance(item,dict) and isinstance(value.get(key),dict) else copy.deepcopy(item)
    return value


def carrier_invariants(state):
    result=copy.deepcopy(state)
    result['models'].pop('discrete_phase')
    result['materials'].pop('inert_particle',None)
    result.pop('injections')
    for key in ['inlet','outlet','wall','bottom']:result[key]=carrier_boundary(result[key])
    return result


def native_proof(cfg,paths,create_directory=None,*,text_writer=write_ascii_text_new,text_reader=read_text):
    bridge=Bridge(cfg)
    try:
        rid=uuid.uuid4().hex[:8];base=cfg['work']+'/DPM-setup-proof-'+rid
        script=base+'.ps1';receipt=base+'.json'
        code="$ErrorActionPreference='Stop'\ntry {\n"
        code+="$workers=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -match 'run_phase10|resume_phase10|phase10_core'})\nif($workers.Count -gt 0){throw 'Existing Phase10 controller'}\n"
        if create_directory:
            code+='if(Test-Path -LiteralPath '+psquote(create_directory)+'){throw "Existing DPM child folder"}\n'
            code+='New-Item -ItemType Directory -Path '+psquote(create_directory)+' | Out-Null\n'
        code+='$files=@()\n'
        for path,expected in paths:
            code+='$h=(Get-FileHash -LiteralPath '+psquote(path)+' -Algorithm SHA256).Hash.ToLower()\n'
            if expected:code+='if($h -ne '+psquote(expected)+'){throw "Preserved input hash mismatch"}\n'
            code+='$files+=@{path='+psquote(path)+';sha256=$h}\n'
        code+='@{status="PASS";workers=@();files=$files} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath '+psquote(receipt)+' -Encoding Ascii\n'
        code+='} catch { @{status="FAIL";error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath '+psquote(receipt)+' -Encoding Ascii }\n'
        text_writer(bridge,script,code);bridge.shell_file(script)
        proof=json.loads(text_reader(bridge,receipt));assert proof['status']=='PASS',proof
        proof['native_receipt']=receipt
        return proof
    finally:bridge.channel.close()


def saved_injection_frames(cfg,work,case):
    """Read serialized injection properties; live RP variable lists names only."""
    bridge=Bridge(cfg)
    try:
        script=work+'/inspect-saved-frames.py';result=work+'/saved-frames.json';ps=script+'.ps1'
        code='from pathlib import Path\nimport json\nfrom ansys.fluent.core.filereader.case_file import CaseFile\n'
        code+='reader=CaseFile(case_file_name='+repr(case)+')\n'
        code+='records=reader.rp_vars()["dpm/injections-list"]\n'
        code+='frames={name:next(row[1] for row in values if len(row)==2 and row[0]=="local-reference-frame") for name,values in records}\n'
        code+='Path('+repr(result)+').write_text(json.dumps(frames))\n'
        write_ascii_text_new(bridge,script,code)
        exe='C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/controller-venv/Scripts/python.exe'
        write_ascii_text_new(bridge,ps,'& '+psquote(exe)+' '+psquote(script)+'\nif($LASTEXITCODE -ne 0){throw "Saved-frame inspection failed"}\n')
        bridge.shell_file(ps)
        return json.loads(read_text(bridge,result))
    finally:bridge.channel.close()


def main():
    cfg=json.loads((OUT/'run-config.json').read_text())
    manifest=json.loads((OUT/'replication1600-M04/carrier-evidence/raw/manifest.json').read_text())
    source=json.loads((DEST/'live-source-settings.json').read_text())
    comparison=json.loads((DEST/'settings-comparison.json').read_text())
    exact=json.loads((OUT/'replication1600-M04/spiral-reference/exact-injection-readbacks.json').read_text())
    assert comparison['all_recorded_parent_settings_match'] and comparison['carrier_groups_exactly_match']
    path=DEST/'DPM-preparation-receipt.json';assert not path.exists(),'Reconcile previous attempt before replay'
    parent=manifest['final_pair'];before=manifest['settings_readback']
    work=json.loads((OUT/'current-launch.json').read_text())['work']+'/DPM-ready-'+uuid.uuid4().hex[:8]
    receipt={'status':'PREFLIGHT','work':work,'parent':parent,'source_sha256':json.loads((DEST/'recovery.json').read_text())['case_sha256'],
             'solved_updates':0,'DPM_updates':0,'initializations':0,'restored_on_error':False,
             'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    def persist():path.write_text(json.dumps(receipt,indent=2)+'\n')
    s=attach(cfg);mutated=False;transcript=False
    try:
        assert not s.settings.solution.run_calculation.iterating() and counter(s)==1500
        core.require_state_same(core.state(s),before)
        receipt['preflight']=native_proof(cfg,[(parent[k],parent[k+'_sha256']) for k in ['case','data']],work)
        persist()
        s.settings.file.start_transcript(file_name=work+'/preparation.trn');transcript=True
        mutated=True
        # Version-matched repository recipe: an injection must exist before
        # the inert-particle material create command is active in Fluent 25.2.
        for name in exact:s.settings.setup.models.discrete_phase.injections.create(name=name)
        material=source['setup']['materials']['inert_particle']['liquid-water']
        group=s.settings.setup.materials.inert_particle
        assert 'liquid-water' not in group.get_object_names()
        group.create(name='liquid-water');group['liquid-water'].set_state(material)
        model=source['setup']['models']['discrete_phase']
        targets={}
        for name,case4 in exact.items():
            target=overlay(model['injections'][name],case4)
            # Current API hides reference_frame for stationary absolute flow.
            # Read the stored global value independently through RP below.
            target['initial_values'].pop('reference_frame',None)
            targets[name]=target
            injections=s.settings.setup.models.discrete_phase.injections
            injections[name].set_state(target)
            # Selector hooks reset flow/speed during a whole-object write.
            # Write dimensional values after the dependent selectors settle.
            initial=injections[name].initial_values
            initial.mass_flow_rate.scale_by_area=False
            initial.mass_flow_rate.total_flow_rate=target['initial_values']['mass_flow_rate']['total_flow_rate']
            initial.velocity.use_face_normal_direction=True
            initial.velocity.magnitude=target['initial_values']['velocity']['magnitude']
        for key,value in model.items():
            if key!='injections':getattr(s.settings.setup.models.discrete_phase,key).set_state(value)
        bc=source['setup']['boundary_conditions']
        m04bc=s.settings.setup.boundary_conditions
        m04bc.mass_flow_inlet['inlet'].phase['mixture'].discrete_phase.set_state(bc['mass_flow_inlet']['inlet']['phase']['mixture']['discrete_phase'])
        m04bc.pressure_outlet['steamoutlet'].phase['mixture'].discrete_phase.set_state(bc['pressure_outlet']['outlet']['phase']['mixture']['discrete_phase'])
        for name in m04bc.wall.get_object_names():
            role='bottom' if name=='bottom' else 'wall-fluid'
            m04bc.wall[name].phase['mixture'].discrete_phase.set_state(bc['wall'][role]['phase']['mixture']['discrete_phase'])
        def verify():
            state=core.state(s)
            receipt['latest_settings_readback']=state
            receipt['DPM_differences']=differences(overlay(model,{'injections':targets}),state['models']['discrete_phase'])
            persist()
            assert not differences(carrier_invariants(before),carrier_invariants(state)),'Carrier settings changed'
            assert counter(s)==1500 and not s.settings.solution.run_calculation.iterating()
            assert s.fields.solution_variable_info.get_zones_info()['fluid'].count==946967
            assert set(state['injections'])==set(exact) and len(state['injections'])==9
            assert not differences(material,state['materials']['inert_particle']['liquid-water'])
            assert not receipt['DPM_differences'],receipt['DPM_differences']
            for target,current in [(bc['mass_flow_inlet']['inlet'],state['inlet']['inlet']),
                                   (bc['pressure_outlet']['outlet'],state['outlet']['steamoutlet']),
                                   (bc['wall']['bottom'],state['bottom']),(bc['wall']['wall-fluid'],state['wall'])]:
                assert target['phase']['mixture']['discrete_phase']==current['phase']['mixture']['discrete_phase']
            return state
        state=verify();receipt.update(status='APPLIED_READBACK_VERIFIED',settings=state);persist()
        pair={'case':work+'/M04-N1500-spiral-Case4-DPM-ready.cas.h5','data':work+'/M04-N1500-spiral-Case4-DPM-ready.dat.h5'}
        s.settings.file.write_case(file_name=pair['case']);s.settings.file.write_data(file_name=pair['data'])
        s.settings.file.read_case(file_name=pair['case']);s.settings.file.read_data(file_name=pair['data'])
        reopened=verify();assert not differences(state,reopened),'Saved settings differ'
        frames=saved_injection_frames(cfg,work,pair['case'])
        assert frames==comparison['archived_injection_reference_frames'],frames
        receipt['reference_frames']=frames
        proof=native_proof(cfg,[(pair[k],None) for k in ['case','data']])
        for kind in ['case','data']:pair[kind+'_sha256']=next(x['sha256'] for x in proof['files'] if x['path']==pair[kind])
        receipt.update(status='DPM_READY_N1500_SAVED_REOPENED',pair=pair,hash_proof=proof,reopen_verified=True,
                       carrier_invariants_preserved=True,iteration=1500,cells=946967,tracking_issued=False,
                       historical_limit='Recovered matching h1600 parent plus direct July Case4 overrides; exact July binary and full July settings export not found.')
        persist()
    except BaseException as error:
        receipt.update(status='PREPARATION_ERROR',error=type(error).__name__+': '+str(error));persist()
        if mutated:
            s.settings.file.read_case(file_name=parent['case']);s.settings.file.read_data(file_name=parent['data'])
            core.require_state_same(core.state(s),before);assert counter(s)==1500
            receipt['restored_on_error']=True;persist()
        raise
    finally:
        if transcript:s.settings.file.stop_transcript()
        s._fluent_connection._channel.close()
    print(json.dumps({k:receipt[k] for k in ['status','iteration','cells','solved_updates','DPM_updates','reopen_verified']}))


if __name__=='__main__':main()
