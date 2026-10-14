"""Compare live recovered source to historical readbacks and M04 carrier."""
from pathlib import Path
import json
import math

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'PyAnsys/output/phase10-single-inlet-mesh-convergence'
DEST=OUT/'replication1600-M04/spiral-recovered-parent'


def current_boundary_schema(value):
    """Translate only the observed historical DPM boundary API names.

    Values remain unchanged; both original exports remain immutable.
    Fluent 25.2 groups wall coefficients under reflection_coefficients.
    """
    if isinstance(value,list):return [current_boundary_schema(v) for v in value]
    if not isinstance(value,dict):return value
    result={('discrete_phase' if k=='dpm' else 'bc_type' if k=='discrete_phase_bc_type' else 'turbo_specific_nrbc' if k=='turbo_sepcific_nrbc' else k):
            current_boundary_schema(v) for k,v in value.items()}
    coefficients={}
    for old,new in [('normal_coefficient','normal'),('tangential_coefficient','tangential')]:
        if old in result:coefficients[new]=result.pop(old)
    if coefficients:result['reflection_coefficients']=coefficients
    return result


def carrier_boundary(value):
    if isinstance(value,list):return [carrier_boundary(v) for v in value]
    if not isinstance(value,dict):return value
    return {k:carrier_boundary(v) for k,v in value.items() if k not in ('name','discrete_phase','dpm')}


def differences(expected,actual,path='',subset=False):
    result=[]
    if isinstance(expected,dict) and isinstance(actual,dict):
        keys=set(expected) if subset else set(expected)|set(actual)
        for key in sorted(keys):
            child=path+'/'+key
            if key not in expected:result.append({'path':child,'expected':'<absent>','actual':actual[key]})
            elif key not in actual:result.append({'path':child,'expected':expected[key],'actual':'<absent>'})
            else:result.extend(differences(expected[key],actual[key],child,subset))
    elif isinstance(expected,list) and isinstance(actual,list):
        if len(expected)!=len(actual):result.append({'path':path,'expected':expected,'actual':actual})
        else:
            for i,(a,b) in enumerate(zip(expected,actual)):result.extend(differences(a,b,path+'/'+str(i),subset))
    elif isinstance(expected,(int,float)) and not isinstance(expected,bool) and isinstance(actual,(int,float)) and not isinstance(actual,bool):
        if not math.isclose(expected,actual,rel_tol=1e-12,abs_tol=1e-12):result.append({'path':path,'expected':expected,'actual':actual})
    elif expected!=actual:result.append({'path':path,'expected':expected,'actual':actual})
    return result


def main():
    source=json.loads((DEST/'live-source-settings.json').read_text())
    old=json.loads((OUT/'replication1600-M04/spiral-reference/raw/baseline_inspection/case_1_1600_25pct_spiral_baseline_full.json').read_text())
    m04=json.loads((OUT/'replication1600-M04/carrier-evidence/raw/manifest.json').read_text())['settings_readback']
    setup=source['setup'];model=setup['models'];bc=setup['boundary_conditions']
    names=source['injection_names'];inj=model['discrete_phase']['injections']
    assert len(names)==len(set(names))==9
    rp=json.loads((DEST/'raw/rp-vars.json').read_text())
    archived_frames={name:next(row[1] for row in values if len(row)==2 and row[0]=='local-reference-frame')
                     for name,values in rp['dpm/injections-list']}
    parent_diffs={}
    for x in old['all_injections']:
        actual=json.loads(json.dumps(inj[x['injection_name']]))
        # The stationary-frame field is omitted by the current live schema.
        # Check its value in the immutable archived RP export, not a default.
        actual['initial_values']['reference_frame']=archived_frames[x['injection_name']]
        parent_diffs[x['injection_name']]=differences(x['state'],actual,subset=True)
    boundary_diffs=differences(current_boundary_schema(old['boundary_conditions']),bc,subset=True)
    general_diffs=differences(old['dpm_general_settings'],model['discrete_phase']['general_settings'],subset=True)
    carrier_groups={
        'solver':(setup['general']['solver'],m04['solver']),
        'operating':(setup['general']['operating_conditions'],m04['operating']),
        'energy':(model['energy'],m04['models']['energy']),
        'multiphase':(model['multiphase'],m04['models']['multiphase']),
        'viscous':(model['viscous'],m04['models']['viscous']),
        'fluid_materials':(setup['materials']['fluid'],m04['materials']['fluid']),
        'methods':(source['methods'],m04['methods']),
        'controls':(source['controls'],m04['controls']),
        'residual_equations':(source['residual_equations'],m04['residual_equations']),
        'fluid_zone':(carrier_boundary(setup['cell_zone_conditions']['fluid']['fluid']),carrier_boundary(m04['fluid'])),
        'inlet':(carrier_boundary(bc['mass_flow_inlet']['inlet']),carrier_boundary(m04['inlet']['inlet'])),
        'top_outlet':(carrier_boundary(bc['pressure_outlet']['outlet']),carrier_boundary(m04['outlet']['steamoutlet'])),
        'bottom':(carrier_boundary(bc['wall']['bottom']),carrier_boundary(m04['bottom'])),
        'vessel_wall':(carrier_boundary(bc['wall']['wall-fluid']),carrier_boundary(m04['wall']))}
    carrier_diffs={key:differences(a,b) for key,(a,b) in carrier_groups.items()}
    dpm=model['discrete_phase'];current=m04['models']['discrete_phase']
    dpm_diffs=differences({k:v for k,v in dpm.items() if k!='injections'},
                          {k:v for k,v in current.items() if k!='injections'})
    case4=json.loads((OUT/'replication1600-M04/spiral-reference/exact-injection-readbacks.json').read_text())
    overrides={name:differences(case4[name],{**inj[name],'initial_values':{**inj[name]['initial_values'],
        'reference_frame':archived_frames[name]}},subset=True) for name in case4}
    expected_bc_values={'inlet_escape':bc['mass_flow_inlet']['inlet']['phase']['mixture']['discrete_phase'],
        'outlet_escape':bc['pressure_outlet']['outlet']['phase']['mixture']['discrete_phase'],
        'bottom_trap':bc['wall']['bottom']['phase']['mixture']['discrete_phase'],
        'wall_reflect':bc['wall']['wall-fluid']['phase']['mixture']['discrete_phase']}
    summary={'status':'AUDITED_SOURCE_COMPARISON','source_parent_injection_subset_differences':parent_diffs,
        'source_parent_boundary_subset_differences':boundary_diffs,'source_parent_general_DPM_differences':general_diffs,
        'all_recorded_parent_settings_match':not boundary_diffs and not general_diffs and not any(parent_diffs.values()),
        'source_to_M04_carrier_differences':carrier_diffs,'carrier_groups_exactly_match':not any(carrier_diffs.values()),
        'source_to_M04_DPM_global_differences':dpm_diffs,'source_to_Case4_injection_differences':overrides,
        'source_boundary_particle_controls':expected_bc_values,'global_DPM_settings':{k:v for k,v in dpm.items() if k!='injections'},
        'particle_material':setup['materials']['inert_particle']['liquid-water'],'source_cells':source['cells'],
        'historical_full_July_source_export_available':False,'solved_updates':0,
        'archived_injection_reference_frames':archived_frames,
        'boundary_role_mapping':{'outlet':'steamoutlet','bottom':'bottom','wall-fluid':'wall','inlet':'inlet'},
        'boundary_schema_translation':{'dpm':'discrete_phase','discrete_phase_bc_type':'bc_type','turbo_sepcific_nrbc':'turbo_specific_nrbc',
            'normal_coefficient':'reflection_coefficients/normal','tangential_coefficient':'reflection_coefficients/tangential'},
        'comparison_tolerance':'Scalar roundoff only: relative/absolute 1e-12; strings/flags/names exact; historical export compared as a subset of the current schema, with explicitly listed DPM boundary API name translations.'}
    (DEST/'settings-comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'historical_parent_matches':summary['all_recorded_parent_settings_match'],
        'parent_boundary_differences':boundary_diffs,'parent_injection_difference_counts':{k:len(v) for k,v in parent_diffs.items()},
        'carrier_differences':carrier_diffs,'global_DPM_differences':dpm_diffs,
        'Case4_injection_difference_counts':{k:len(v) for k,v in overrides.items()}},indent=2))


if __name__=='__main__':main()
