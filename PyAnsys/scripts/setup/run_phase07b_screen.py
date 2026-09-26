"""Build and execute one authorized Phase 7b thickness, with exact-face evidence.

No C, no pool patch, no transient solve, and no remote session shutdown.
This runner never resumes an uncertain solve automatically.
"""
from prepare_phase07b_collector import *
import re
import fcntl
import os
import hashlib
import copy
import numpy as np
from pyansys_fluent.phase07b_flux_monitor import FluxFaceZone, Phase07bFluxMonitor
sys.path.insert(0,str(BASE/'scripts/inspection'))
from export_phase07b_sections import export_sections
sys.path.insert(0,str(BASE/'scripts/analysis'))
from analyze_phase07b_screen import parse_residuals, expected_residual_equations, BASE_RESIDUAL_EQUATIONS


def preserved_predecessor(receipt, manifest):
    """Accept the verified meeting restore without relabelling failed S100."""
    assert receipt['status']=='COMPLETE_NO_SOLVE_OR_CHECKPOINT_OVERWRITE'
    assert receipt['iterations_issued']==0
    matches=[v for v in receipt['cases'].values()
             if v['case']==receipt['restore_case'] and v['run']==manifest['run_id']]
    assert len(matches)==1
    state=matches[0]
    assert state['iteration']==receipt['restored_iteration']
    assert state['case'] in manifest['pairs'].values()
    assert state['data']==state['case'].replace('.cas.h5','.dat.h5')
    return state


def exact_parity(expected, actual, path=''):
    if isinstance(expected,dict):
        assert set(expected)==set(actual),f'{path}: keys differ'
        for k,v in expected.items():exact_parity(v,actual[k],path+'.'+k)
    else:
        assert expected==actual,f'{path}: reference mismatch'


def verify_e7_delta(control, child):
    """E7 is exactly the E6 treatment with a fivefold weaker source coefficient."""
    assert control['experiment_id']=='E6' and control['completed_iterations']==5000
    assert control['tau_s']==.02 and child['tau_s']==.1
    for key in ['selected_methods','selected_controls','source_slots','fluid_zones','reference_setup']:
        exact_parity(control[key],child[key],'E7 unchanged '+key)
    expected=copy.deepcopy(control['definitions'])
    zones=json.dumps(child['fluid_zones'])
    sink=definitions(40,.1)['P7bSink'].replace(f'["{ZONE}"]',zones)
    expected['P7bSink']=sink
    exact_parity(expected,child['definitions'],'E7 tau-only expression delta')
    assert control['definitions']['P7bSink']!=sink
    return {'status':'EXACT_TAU_ONLY_DELTA_PASS','control_run':control['run_id'],
            'old_tau_s':.02,'new_tau_s':.1,'fixed_field_coefficient_ratio':.2,
            'changed_definitions':['P7bSink'],'methods_controls_sources_unchanged':True}


def apply_coupled_off(s, methods, controls, capability_path, flow_courant=200., solve_n_phase=False, nphase_before_hybrid=False):
    """Apply the verified Coupled baseline and the declared E5/E6 deltas."""
    assert not nphase_before_hybrid or solve_n_phase
    proof=json.loads(capability_path.read_text())
    assert proof['status']=='COUPLED_OFF_PROBE_COMPLETE_ENDPOINT_RESTORED'
    assert proof['iterations_issued']==0 and proof['activated_iteration']==5000
    exact_parity(proof['methods'],methods,'capability parent methods')
    exact_parity(proof['controls'],controls,'capability parent controls')
    expected=copy.deepcopy(methods)
    expected['p_v_coupling']['flow_scheme']='Coupled'
    expected['pseudo_time_method']['formulation']={'coupled_solver':'off'}
    exact_parity(expected,proof['activated_methods'],'capability method delta')
    if nphase_before_hybrid:expected['p_v_coupling']['solve_n_phase']=True
    setup=s.settings.setup.get_state()
    residual=s.settings.solution.monitor.residual.options.get_state()
    assert residual['normalize'] is False
    assert residual['residual_values']=={'scale_residuals':True,'compute_local_scale':False}
    assert 'Coupled' in s.settings.solution.methods.p_v_coupling.flow_scheme.allowed_values()
    s.settings.solution.methods.p_v_coupling.flow_scheme='Coupled'
    assert 'off' in s.settings.solution.methods.pseudo_time_method.formulation.coupled_solver.allowed_values()
    s.settings.solution.methods.pseudo_time_method.formulation.coupled_solver='off'
    s.settings.solution.controls.p_v_controls.set_state({
        'flow_courant_number':flow_courant,'explicit_pressure_under_relaxation':.5,
        'explicit_momentum_under_relaxation':.5})
    selected_methods=s.settings.solution.methods.get_state()
    selected_controls=s.settings.solution.controls.get_state()
    exact_parity(expected,selected_methods,'E4 methods')
    expected_controls=copy.deepcopy(proof['activated_controls'])
    expected_controls['p_v_controls']['flow_courant_number']=flow_courant
    exact_parity(expected_controls,selected_controls,'Coupled activated controls')
    if flow_courant==20.:
        e4=json.loads((BASE/'output/p7b-s40-t020-coupled-off-20260922T134224Z/manifest.json').read_text())
        expected_e4=copy.deepcopy(e4['selected_methods'])
        if nphase_before_hybrid:expected_e4['p_v_coupling']['solve_n_phase']=True
        exact_parity(expected_e4,selected_methods,'E5/E6 versus E4 methods')
        e4controls=copy.deepcopy(e4['selected_controls']);e4controls['p_v_controls']['flow_courant_number']=20.
        exact_parity(e4controls,selected_controls,'E5 versus E4 CFL-only controls')
    if solve_n_phase:
        assert flow_courant==20.
        e5=json.loads((BASE/'output/p7b-s40-t020-coupled-cfl20-20260922T202845Z/manifest.json').read_text())
        expected_e5=copy.deepcopy(e5['selected_methods'])
        if nphase_before_hybrid:expected_e5['p_v_coupling']['solve_n_phase']=True
        exact_parity(expected_e5,selected_methods,'E6 E5 treatment baseline methods')
        exact_parity(e5['selected_controls'],selected_controls,'E6 E5 treatment baseline controls')
        assert s.settings.solution.methods.p_v_coupling.solve_n_phase.is_active()
        if nphase_before_hybrid:
            assert s.settings.solution.methods.p_v_coupling.solve_n_phase() is True
        else:
            s.settings.solution.methods.p_v_coupling.solve_n_phase=True
        expected_nphase=copy.deepcopy(e5['selected_methods']);expected_nphase['p_v_coupling']['solve_n_phase']=True
        selected_methods=s.settings.solution.methods.get_state()
        selected_controls=s.settings.solution.controls.get_state()
        exact_parity(expected_nphase,selected_methods,'E6 N-phase-only method delta')
        exact_parity(e5['selected_controls'],selected_controls,'E6 unchanged E5 controls')
    exact_parity(setup,s.settings.setup.get_state(),'Coupled treatment physics unchanged')
    exact_parity(residual,s.settings.solution.monitor.residual.options.get_state(),'E4 residual presentation unchanged')
    assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==0
    return {'methods':selected_methods,'controls':selected_controls,'residual_options':residual,
            'capability':str(capability_path),'capability_sha256':hashlib.sha256(capability_path.read_bytes()).hexdigest(),
            'status':'EXACT_PREDECLARED_DELTA_PASS','flow_courant':flow_courant,'solve_n_phase':solve_n_phase,'nphase_before_hybrid':nphase_before_hybrid}


def enable_nphase_before_hybrid(s, methods, controls):
    """N0 allocation-order recovery: preserve SIMPLE and all physical settings."""
    assert methods['p_v_coupling']['flow_scheme']=='SIMPLE'
    assert methods['p_v_coupling']['solve_n_phase'] is False
    exact_parity(methods,s.settings.solution.methods.get_state(),'pre-Hybrid clean methods')
    exact_parity(controls,s.settings.solution.controls.get_state(),'pre-Hybrid clean controls')
    setup=s.settings.setup.get_state()
    residual=s.settings.solution.monitor.residual.options.get_state()
    hybrid=s.settings.solution.initialization.hybrid_init_options.get_state()
    assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==0
    assert s.settings.solution.methods.p_v_coupling.solve_n_phase.is_active()
    s.settings.solution.methods.p_v_coupling.solve_n_phase=True
    post_enable_iteration=s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()
    assert post_enable_iteration in (0,1), ('Unexpected pre-Hybrid counter',post_enable_iteration)
    expected=copy.deepcopy(methods);expected['p_v_coupling']['solve_n_phase']=True
    exact_parity(expected,s.settings.solution.methods.get_state(),'pre-Hybrid sole N-phase delta')
    exact_parity(controls,s.settings.solution.controls.get_state(),'pre-Hybrid controls unchanged')
    exact_parity(setup,s.settings.setup.get_state(),'pre-Hybrid setup unchanged')
    exact_parity(residual,s.settings.solution.monitor.residual.options.get_state(),'pre-Hybrid residual presentation unchanged')
    exact_parity(hybrid,s.settings.solution.initialization.hybrid_init_options.get_state(),'pre-Hybrid initialization options unchanged')
    return {'status':'SIMPLE_NPHASE_ONLY_PRE_HYBRID_DELTA_PASS','methods':expected,
            'controls':controls,'residual_options':residual,'hybrid_options':hybrid,
            'raw_iteration_before_enable':0,'raw_iteration_after_enable':post_enable_iteration,
            'iterations_issued':0}


def mapped_n0_array_parity(actual_geometry, expected_geometry, actual_fields, expected_fields):
    """E6 initial capture only: bijective cells, bounded geometry, exact physics.

    The 1e-10 m rounded coordinates identify cells; they are NOT the acceptance
    tolerance. Matched coordinates must be within 1e-14 m in Euclidean distance.
    This does not modify raw arrays or relax the strict checks after pair reload.
    """
    assert set(actual_geometry)==set(expected_geometry), 'N0 geometry inventory differs'
    prefixes=sorted(key.removesuffix('_mixture_SV_CENTROID') for key in expected_geometry
                    if key.endswith('_mixture_SV_CENTROID'))
    assert prefixes and set(expected_geometry)=={
        prefix+'_mixture_'+variable for prefix in prefixes for variable in ['SV_CENTROID','SV_VOLUME']}
    field_keys={key for key in expected_fields if 'MASS_IMBALANCE' not in key}
    assert {key for key in actual_fields if 'MASS_IMBALANCE' not in key}==field_keys
    result={'matching':'bijective rounded centroids; exact physical values after cell permutation',
            'coordinate_label_decimal_places':10,'maximum_centroid_distance_m':1e-14,
            'maximum_volume_absolute_difference_m3':1e-18,'zones':[]}
    checked=set()
    for prefix in prefixes:
        centroid_key=prefix+'_mixture_SV_CENTROID';volume_key=prefix+'_mixture_SV_VOLUME'
        actual=np.asarray(actual_geometry[centroid_key]);expected=np.asarray(expected_geometry[centroid_key])
        assert actual.shape==expected.shape and actual.size>0 and actual.size%3==0, centroid_key
        actual=actual.reshape(-1,3);expected=expected.reshape(-1,3)
        assert np.isfinite(actual).all() and np.isfinite(expected).all(), centroid_key
        actual_labels=np.round(actual,10);expected_labels=np.round(expected,10)
        assert len(np.unique(actual_labels,axis=0))==len(actual), 'Ambiguous actual cell coordinates: '+prefix
        assert len(np.unique(expected_labels,axis=0))==len(expected), 'Ambiguous reference cell coordinates: '+prefix
        actual_order=np.lexsort(actual_labels.T[::-1]);expected_order=np.lexsort(expected_labels.T[::-1])
        assert np.array_equal(actual_labels[actual_order],expected_labels[expected_order]), 'Cell coordinate bijection failed: '+prefix
        # permutation maps each reference-array index to its actual-array index.
        permutation=np.empty(len(expected),dtype=np.int64);permutation[expected_order]=actual_order
        distance=float(np.max(np.linalg.norm(actual[permutation]-expected,axis=1)))
        assert distance<=1e-14, ('N0 centroid bound exceeded',prefix,distance)
        actual_volume=np.asarray(actual_geometry[volume_key]);expected_volume=np.asarray(expected_geometry[volume_key])
        assert actual_volume.shape==expected_volume.shape==(len(expected),), volume_key
        assert np.isfinite(actual_volume).all() and np.isfinite(expected_volume).all(), volume_key
        volume_difference=float(np.max(np.abs(actual_volume[permutation]-expected_volume)))
        assert volume_difference<=1e-18, ('N0 volume bound exceeded',prefix,volume_difference)
        zone_fields=sorted(key for key in field_keys if key.startswith(prefix+'_'))
        assert zone_fields, 'Missing N0 physical fields: '+prefix
        for key in zone_fields:
            values=np.asarray(actual_fields[key]);reference=np.asarray(expected_fields[key])
            assert values.shape==reference.shape==(len(expected),), key
            assert np.isfinite(values).all() and np.isfinite(reference).all(), key
            assert np.array_equal(values[permutation],reference), 'Mapped N0 physical field differs: '+key
            checked.add(key)
        result['zones'].append({'zone':prefix,'cells':len(expected),'coordinate_bijection':True,
            'reordered_cells':int(np.count_nonzero(permutation!=np.arange(len(expected)))),
            'permutation_sha256':hashlib.sha256(permutation.tobytes()).hexdigest(),
            'max_centroid_distance_m':distance,'max_volume_absolute_difference_m3':volume_difference,
            'exact_physical_keys':zone_fields})
    assert checked==field_keys, 'Unmapped physical fields'
    result['status']='MAPPED_N0_PHYSICAL_EXACT_GEOMETRY_ROUNDOFF_PASS'
    return result


def pre_reopen_n0_parity(s, zones, out, tag):
    """Capture physical/geometry arrays without report definitions or solver advance."""
    original=BASE/'output/p7b-s40-t020-diag-20260922T071533Z/spike-diagnostics'
    directory=out/('pre-reopen-'+tag);directory.mkdir()
    iteration=lambda:s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()
    assert tag in ('initial','prepared')
    raw_iteration=iteration()
    assert raw_iteration in ((0,1) if tag=='initial' else (0,)), ('Unexpected pre-reopen counter',tag,raw_iteration)
    assert s.settings.solution.methods.p_v_coupling.solve_n_phase() is True
    if tag=='initial':
        assert s.settings.solution.methods.p_v_coupling.flow_scheme()=='SIMPLE'
        for zone in zones:
            for phase in ['mixture','phase-1','phase-2']:
                assert not s.settings.setup.cell_zone_conditions.fluid[zone].phase[phase].sources.enable()
    result={'raw_iteration':raw_iteration,'zones':list(zones),'reference':str(original),'datasets':[],'iterations_issued':0,
            'required_iteration_after_reopen':0,'source_free_hybrid_capture':tag=='initial'}
    captured={};references={}
    for filename in ['geometry.npz','fields-n00000.npz']:
        reference=original/filename
        actual={}
        with np.load(reference) as expected:
            keys=[key for key in expected.files if 'MASS_IMBALANCE' not in key]
            requests={tuple(key.split('_',2)[1:]) for key in keys}
            for domain,variable in sorted(requests):
                data=s.fields.solution_variable_data.get_data(variable_name=variable,zone_names=zones,domain_name=domain)
                for i,zone in enumerate(zones):
                    key=f'z{i}_{domain}_{variable}'
                    actual[key]=np.asarray(data[zone])
            path=directory/filename
            np.savez_compressed(path,**actual)  # Retain evidence even if parity fails.
            assert set(actual)==set(keys), 'Unexpected N0 field/geometry inventory'
            captured[filename]=actual;references[filename]={key:expected[key] for key in keys}
            for key in keys:
                assert np.isfinite(actual[key]).all(), key
                if tag=='prepared':
                    assert np.array_equal(actual[key],expected[key]), f'Pre-reopen N0 mismatch: {filename}:{key}'
        result['datasets'].append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'reference':str(reference),'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
            'checked_keys':keys})
        if tag=='prepared':result['datasets'][-1]['exact_equal_keys']=keys
    if tag=='initial':
        result['mapped_parity']=mapped_n0_array_parity(captured['geometry.npz'],references['geometry.npz'],
                                                     captured['fields-n00000.npz'],references['fields-n00000.npz'])
    assert iteration()==raw_iteration
    result['status']=('PRE_REOPEN_N0_PHYSICAL_EXACT_GEOMETRY_ROUNDOFF_PASS' if tag=='initial'
                      else 'PRE_REOPEN_N0_PHYSICAL_GEOMETRY_EXACT_PARITY_PASS')
    (directory/'parity.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def initial_field_parity(out, *, allow_nphase_primary_n0=False):
    original=BASE/'output/p7b-s40-t020-diag-20260922T071533Z'
    evidence={'reference':str(original),'datasets':[]}
    files=list((out/'initial-sections').glob('*.npz'))+list((out/'initial-axial-sections').glob('*.npz'))
    assert len(files)==6
    files.append(out/'spike-diagnostics/fields-n00000.npz')
    for path in files:
        reference=original/path.relative_to(out)
        with np.load(path) as actual,np.load(reference) as expected:
            extra=set(actual.files)-set(expected.files)
            assert not set(expected.files)-set(actual.files), 'Missing original N0 fields'
            permitted={'z0_phase-1_SV_VOF','z1_phase-1_SV_VOF'}
            if extra:
                assert allow_nphase_primary_n0 and path.name=='fields-n00000.npz' and extra==permitted, extra
                for key in sorted(extra):
                    secondary=key.replace('phase-1','phase-2')
                    assert actual[key].shape==actual[secondary].shape
                    assert np.isfinite(actual[key]).all() and np.all(actual[key]==1), key
                    assert np.all(actual[secondary]==0), secondary
            checked=[]
            for key in expected.files:
                # Raw solver imbalance storage is not an initialization field.
                if 'MASS_IMBALANCE' in key:continue
                assert np.isfinite(actual[key]).all()
                assert np.array_equal(actual[key],expected[key]),f'N0 field differs: {path.name}:{key}'
                checked.append(key)
        evidence['datasets'].append({'file':str(path),'reference':str(reference),'exact_equal_keys':checked,
                                    'additional_primary_n0_exact_one_secondary_exact_zero':sorted(extra)})
    evidence['status']='INITIAL_PHYSICAL_FIELDS_EXACTLY_EQUAL'
    (out/'initial-parity.json').write_text(json.dumps(evidence,indent=2)+'\n')
    return evidence


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--percent',type=int,choices=list(TOPS),required=True)
    ap.add_argument('--previous-manifest',type=Path,required=True)
    ap.add_argument('--preserved-state-receipt',type=Path)
    ap.add_argument('--tau-s',type=positive_tau,default=BASELINE_TAU_S)
    ap.add_argument('--case-id')
    ap.add_argument('--reference-manifest',type=Path)
    ap.add_argument('--spike-diagnostics',action='store_true')
    ap.add_argument('--coupled-off-capability',type=Path)
    ap.add_argument('--coupled-flow-courant',type=float,choices=[20.,200.],default=200.)
    ap.add_argument('--solve-n-phase',action='store_true')
    ap.add_argument('--nphase-before-hybrid',action='store_true',help='E6 only: initialize N-phase storage before original SIMPLE Hybrid; require pre-reopen exact N0 parity')
    ap.add_argument('--run-id')
    ap.add_argument('--iterations',type=int,default=5000);a=ap.parse_args()
    assert 1<=a.iterations<=5000
    if a.tau_s!=BASELINE_TAU_S:
        allowed=[(40,.02,'S40-T020'),(40,.1,'S40-T100')]
        if a.spike_diagnostics:allowed=[(40,.02,'S40-T020-DIAG')]
        if a.coupled_off_capability:allowed=[(40,.02,'S40-T020-COUPLED-OFF'),(40,.02,'S40-T020-COUPLED-CFL20')]
        if a.solve_n_phase:allowed=[(40,.02,'S40-T020-COUPLED-CFL20-NPHASE'),(40,.1,'S40-T100-COUPLED-CFL20-NPHASE')]
        assert (a.percent,a.tau_s,a.case_id) in allowed, 'Outside approved E2/E3 points'
        assert a.reference_manifest, 'E2 requires the original S40 manifest'
    e7=a.case_id=='S40-T100-COUPLED-CFL20-NPHASE'
    if a.spike_diagnostics:assert a.case_id in ['S40-T020-DIAG','S40-T020-COUPLED-OFF','S40-T020-COUPLED-CFL20','S40-T020-COUPLED-CFL20-NPHASE','S40-T100-COUPLED-CFL20-NPHASE'] and a.tau_s==(.1 if e7 else .02) and a.iterations==5000
    if a.coupled_off_capability:
        assert a.spike_diagnostics and (a.case_id,a.coupled_flow_courant) in [('S40-T020-COUPLED-OFF',200.),('S40-T020-COUPLED-CFL20',20.),('S40-T020-COUPLED-CFL20-NPHASE',20.),('S40-T100-COUPLED-CFL20-NPHASE',20.)]
    else:assert a.coupled_flow_courant==200.
    assert a.solve_n_phase == (a.case_id in ['S40-T020-COUPLED-CFL20-NPHASE','S40-T100-COUPLED-CFL20-NPHASE']), 'N-phase is restricted to E6/E7'
    if a.solve_n_phase:assert a.percent==40 and a.tau_s==(.1 if e7 else .02) and a.coupled_off_capability and a.coupled_flow_courant==20. and a.spike_diagnostics and a.iterations==5000
    if e7:assert a.nphase_before_hybrid, 'E7 requires the verified allocation order'
    assert not a.nphase_before_hybrid or a.solve_n_phase, 'Early N-phase initialization is exclusively E6'
    identity=f's{a.percent:03d}' if a.tau_s==BASELINE_TAU_S else a.case_id.lower()
    run=a.run_id or f'p7b-{identity}-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    assert re.fullmatch(f'p7b-{re.escape(identity)}-[0-9]{{8}}T[0-9]{{6}}Z',run)
    out=BASE/'output'/run;out.mkdir();r={'run_id':run,'case_id':a.case_id or f'S{a.percent}', 'tau_s':a.tau_s,'percent':a.percent,'requested_iterations':a.iterations,'steps':[], 'status':'BUILDING','controller_pid':os.getpid()}
    lock=(BASE/'output/phase07b-server1-controller.lock').open('a+')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    lock.seek(0);lock.truncate();lock.write(json.dumps({'pid':os.getpid(),'run_id':run}));lock.flush()
    reference=json.loads(a.reference_manifest.read_text()) if a.reference_manifest else None
    if reference:
        assert reference['percent']==40 and reference['completed_iterations']==5000
        r['comparison_reference']={'manifest':str(a.reference_manifest),'sha256':hashlib.sha256(a.reference_manifest.read_bytes()).hexdigest()}
    r['implementation_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),BASE/'scripts/setup/prepare_phase07b_collector.py']}
    if a.spike_diagnostics:
        r['experiment_id']='E3';r['replication_of']='p7b-s40-t020-resume-20260921T231240Z'
        for p in [BASE/'src/pyansys_fluent/phase07b_flux_monitor.py',BASE/'src/pyansys_fluent/phase07b_spike_monitor.py']:
            r['implementation_sha256'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    if a.coupled_off_capability:
        r['experiment_id']='E5' if a.coupled_flow_courant==20. else 'E4';r.pop('replication_of',None)
        r['controlled_contrast_to']='p7b-s40-t020-resume-20260921T231240Z'
        r['selected_setup']='Project/experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/'+('coupled-cfl20' if a.coupled_flow_courant==20. else 'coupled-off')+'/setup.md'
        if a.coupled_flow_courant==20.:r['controlled_contrast_to']='p7b-s40-t020-coupled-off-20260922T134224Z'
    if a.solve_n_phase:
        r['experiment_id']='E6';r['controlled_contrast_to']='p7b-s40-t020-coupled-cfl20-20260922T202845Z'
        r['selected_setup']='Project/experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/coupled-nphase/setup.md'
    if e7:
        r['experiment_id']='E7';r['controlled_contrast_to']='p7b-s40-t020-coupled-cfl20-nphase-resume-20260923T231816Z'
        r['selected_setup']='Project/experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/coupled-nphase-weaker-sink/setup.md'
    if a.nphase_before_hybrid:
        r['recovery_initialization_order']='N-phase enabled before unchanged SIMPLE Hybrid; exact physical/geometry parity required before N0 pair reopens'
    r['parent_case']=ROOT+'/case-data/p7b-clean-initial-20260912T080713Z.cas.h5'
    r['report']=ROOT+'/reports/'+run+'.out';r['remote_transcript']=ROOT+'/logs/'+run+'.trn'
    def persist(): (out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
    def timeout(*_):raise TimeoutError('RPC deadline; reconcile before any repeat solve')
    signal.signal(signal.SIGALRM,timeout)
    def step(n,f,sec=90):
        print(n,flush=True);e={'name':n,'state':'STARTED','started_utc':datetime.now(timezone.utc).isoformat()};r['steps'].append(e);persist();signal.alarm(sec)
        try:v=f();e.update(state='PASS',value=v);return v
        except Exception as x:e.update(state='FAIL',error=str(x));raise
        finally:signal.alarm(0);e['ended_utc']=datetime.now(timezone.utc).isoformat();persist()
    s=None;m=None;diagnostic=None
    def named(name,d):
        g=s.settings.setup.named_expressions
        if name not in g.get_object_names():g.create(name=name)
        g[name].definition=d;assert g[name].definition()==d
    def nvalue(name):return s.settings.setup.named_expressions[name].get_value()
    def save(tag):
        p=ROOT+'/case-data/'+run+'-'+tag+'.cas.h5'
        assert not any(remote_file_exists(s,p.replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5']), 'Refuse checkpoint overwrite'
        step('save_'+tag,lambda:s.settings.file.write_case_data(file_name=p),180)
        assert all(remote_file_exists(s,p.replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
        r.setdefault('pairs',{})[tag]=p;persist();return p
    try:
        s=step('connect',lambda:connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5),90 if a.nphase_before_hybrid else 30)
        assert not s.settings.solution.run_calculation.iterating(), 'Existing solver operation is active'
        r['fluent_version']=str(s.get_fluent_version())
        if a.nphase_before_hybrid:
            assert reference['reference_setup']['user_defined']['auto_compile_compiled_functions'] is False
            before=s.settings.setup.user_defined.auto_compile_compiled_functions()
            s.settings.setup.user_defined.auto_compile_compiled_functions=False
            assert s.settings.setup.user_defined.auto_compile_compiled_functions() is False
            r['restored_session_preference']={'auto_compile_compiled_functions_before':before,'after':False,'basis':'Exact original reference; Python-only preparation'}
        s.transcript.start(file_name=str(out/'setup.trn'),write_to_stdout=False)
        if a.previous_manifest:
            prior=json.loads(a.previous_manifest.read_text())
            if a.preserved_state_receipt:
                state=preserved_predecessor(json.loads(a.preserved_state_receipt.read_text()),prior)
                pair=state['case'];previous_iteration=state['iteration']
                assert math.isclose(nvalue('P7bWaterVolume'),state['water_volume_readback'],rel_tol=1e-12)
            else:
                assert prior['status']=='HORIZON_COMPLETE_ANALYSIS_PENDING' and prior['completed_iterations']==5000
                pair=prior['pairs']['final'];previous_iteration=prior['completed_iterations']
            assert nvalue('P7bGlobalIteration')==previous_iteration
            for name,d in prior['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==d,(name,'unexpected live case')
            for z,phases in prior['source_slots'].items():
                for ph,slots in phases.items():exact_parity(slots,s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state(),z+'.'+ph)
            assert all(remote_file_exists(s,pair.replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
            r['previous_endpoint']={'manifest':str(a.previous_manifest),'preserved_case':pair,'live_iteration_verified':previous_iteration,'saved_pair_exists':True,'receipt':str(a.preserved_state_receipt) if a.preserved_state_receipt else None};persist()
            # Preserve the reconciled live field, including any unsaved display state.
            save('predecessor-preserved')
            assert nvalue('P7bGlobalIteration')==previous_iteration
            def close_inherited_native_transcript():
                command=s.settings.file.stop_transcript
                was_active=command.is_active()
                if was_active:command()
                return {'was_active':was_active,'action':'closed' if was_active else 'already_closed'}
            step('close_inherited_native_transcript',close_inherited_native_transcript)
        assert all(remote_file_exists(s,r['parent_case'].replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
        step('load_clean_n0',lambda:s.settings.file.read_case_data(file_name=r['parent_case']),180)
        assert nvalue('P7bGlobalIteration')==0
        for name in s.settings.solution.monitor.report_files.get_object_names():s.settings.solution.monitor.report_files[name].active=False
        assert s.settings.setup.general.solver.time()=='steady'
        r['reference_setup']=s.settings.setup.get_state()
        r['reference_methods']=s.settings.solution.methods.get_state()
        r['reference_controls']=s.settings.solution.controls.get_state()
        if reference:
            exact_parity(reference['reference_setup'],r['reference_setup'],'reference_setup')
            audited=json.loads((BASE/'output/phase07b_preparation/clean-reference-rebuild.json').read_text())['after']
            exact_parity(audited['methods'],r['reference_methods'],'methods')
            exact_parity(audited['controls'],r['reference_controls'],'controls')
            r['reference_parity']='PASS: exact original S40 setup and audited clean-reference methods/controls'
        for ph in ['mixture','phase-1','phase-2']:assert not s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources.enable()
        residuals=s.settings.solution.monitor.residual.equations
        for eq in residuals.get_object_names():residuals[eq].check_convergence=False
        r['residual_equations']=residuals.get_state()
        r['residual_options']=s.settings.solution.monitor.residual.options.get_state()
        # Partition labels only: preserve all existing mesh cells and faces.
        step('mesh_before',lambda:s.settings.mesh.size_info())
        regs=s.settings.solution.cell_registers;regs.create(name='p7b_exact_collector')
        regs['p7b_exact_collector'].set_state({'type':{'option':'hexahedron','hexahedron':{'min_point':[-100,-1.4845837354660034,-100],'max_point':[100,TOPS[a.percent],100],'inside':True}}})
        old=s.settings.setup.cell_zone_conditions.fluid.get_object_names()
        step('split_collector_cells',lambda:s.settings.mesh.modify_zones.sep_cell_zone_mark(cell_zone_name=ZONE,register='p7b_exact_collector',move_faces=True),180)
        new=list(set(s.settings.setup.cell_zone_conditions.fluid.get_object_names())-set(old));assert len(new)==1,new
        s.settings.mesh.modify_zones.zone_name(zone_name=new[0],new_name='p7b-collector')
        zones=[ZONE,'p7b-collector'];loc=json.dumps(zones)
        step('mesh_after',lambda:s.settings.mesh.size_info());step('mesh_check',lambda:s.settings.mesh.check())
        info=s.fields.solution_variable_info.get_zones_info()
        assert info['p7b-collector'].count==COUNTS[a.percent]
        assert sum(info[z].count for z in zones)==620431
        defs={k:v.replace(f'["{ZONE}"]',loc) for k,v in definitions(a.percent,a.tau_s).items()}
        defs.update({'P7bSplitVolume':'Volume(["p7b-collector"])','P7bSplitMismatch':f'VolumeInt(1-P7bMask,["p7b-collector"])+VolumeInt(P7bMask,["{ZONE}"])',
                     'P7bMinimumPressure':f'Minimum(StaticPressure,{loc})','P7bMaximumPressure':f'Maximum(StaticPressure,{loc})','P7bMaximumSpeed':f'Maximum(VelocityMagnitude(phase="mixture"),{loc})'})
        for name,d in defs.items():step('define_'+name,lambda name=name,d=d:named(name,d))
        assert nvalue('P7bCount')==COUNTS[a.percent]
        assert math.isclose(nvalue('P7bSplitVolume'),VOLUMES[a.percent],rel_tol=1e-9)
        assert nvalue('P7bSplitMismatch')==0
        r['definitions']=defs;r['fluid_zones']=zones;r['interface_proof']={};face_zones=[];all_centroids=[]
        if reference:
            expected=dict(reference['definitions']);expected['P7bSink']=defs['P7bSink']
            exact_parity(expected,defs,'tau-only definitions')
        for face in s.settings.setup.boundary_conditions.interior.get_object_names():
            def fetch(var):return np.asarray(s.fields.solution_variable_data.get_data(variable_name=var,zone_names=[face],domain_name='phase-2')[face])
            f=fetch('SV_CENTROID').reshape(-1,3);d0=fetch('SV_FACE_DR0').reshape(-1,3);d1=fetch('SV_FACE_DR1').reshape(-1,3)
            m0=(f-d0)[:,1]<=TOPS[a.percent];m1=(f-d1)[:,1]<=TOPS[a.percent]
            cross=m0!=m1
            if not cross.any():
                r['interface_proof'][face]={'count':len(f),'crossing_faces':0}
                continue
            assert cross.all(),f'Mixed interface/internal zone {face}'
            assert m0.all() or m1.all(),f'Mixed orientation requires explicit per-face mapping: {face}'
            area=fetch('SV_AREA').reshape(-1,3);assert (np.einsum('ij,ij->i',area,d0-d1)>0).all()
            sign=1 if m0.all() else -1;assert len(f)==info[face].count
            assert len(np.unique(f,axis=0))==len(f)
            all_centroids.append(f);face_zones.append(FluxFaceZone(face,sign,len(f)))
            r['interface_proof'][face]={'count':len(f),'outward_sign':sign,'all_faces_cross_centroid_mask':True,'area_dot_c1_minus_c0_positive':True}
            np.savez_compressed(out/(f'interface-{info[face].zone_id}.npz'),centroids=f,dr0=d0,dr1=d1,area=area)
        assert face_zones
        cf=np.vstack(all_centroids);assert len(np.unique(cf,axis=0))==len(cf)
        if reference:exact_parity(reference['interface_proof'],r['interface_proof'],'collector interfaces')
        # Same fresh Hybrid initialization settings and no liquid patch.
        r['hybrid_options']=s.settings.solution.initialization.hybrid_init_options.get_state()
        if reference:exact_parity(reference['hybrid_options'],r['hybrid_options'],'fresh Hybrid options')
        if a.nphase_before_hybrid:
            r['pre_hybrid_nphase']=step('enable_nphase_before_original_simple_hybrid',lambda:enable_nphase_before_hybrid(s,r['reference_methods'],r['reference_controls']))
        step('fresh_hybrid_initialize',lambda:s.settings.solution.initialization.hybrid_initialize(),180)
        assert nvalue('P7bWaterVolume')==0
        if a.nphase_before_hybrid:
            r['pre_reopen_initial_parity']=step('verify_nphase_hybrid_n0_before_initial_reopen',lambda:pre_reopen_n0_parity(s,zones,out,'initial'),300)
        initial=save('initial');step('reopen_initial',lambda:s.settings.file.read_case_data(file_name=initial),180)
        assert nvalue('P7bGlobalIteration')==0
        if a.nphase_before_hybrid:
            exact_parity(r['pre_hybrid_nphase']['methods'],s.settings.solution.methods.get_state(),'reopened N-phase SIMPLE methods')
            exact_parity(r['reference_controls'],s.settings.solution.controls.get_state(),'reopened N-phase SIMPLE controls')
            exact_parity(r['hybrid_options'],s.settings.solution.initialization.hybrid_init_options.get_state(),'reopened Hybrid options')
        # Reacquire everything after read; source only on exact collector cells.
        for z in zones:
            for ph in ['mixture','phase-1','phase-2']:s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.enable=False
        for ph,terms in HOOKS.items():
            src=s.settings.setup.cell_zone_conditions.fluid['p7b-collector'].phase[ph].sources;src.enable=True
            for eq,ex in terms.items():
                src.terms[eq].resize(size=1);src.terms[eq][0].set_state({'option':'value','value':ex});assert src.terms[eq][0].value()==ex
        r['source_slots']={z:{ph:s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state() for ph in ['mixture','phase-1','phase-2']} for z in zones}
        if reference:exact_parity(reference['source_slots'],r['source_slots'],'source bindings')
        r['explicit_jacobian']='No derivative slot assigned; unchanged native expression sources'
        s.settings.solution.run_calculation.profile_update_interval=1
        skip={'P7bAlpha','P7bMask','P7bK','P7bEpsilon','P7bSink','P7bLiquidX','P7bLiquidY','P7bLiquidZ','P7bSinkX','P7bSinkY','P7bSinkZ','P7bSinkK','P7bSinkEpsilon','P7bCount','P7bGeometryVolume','P7bSplitVolume','P7bSplitMismatch'}
        reports=[]
        for name in defs:
            if name in skip:continue
            rn=name.lower();g=s.settings.solution.report_definitions.single_valued_expression;g.create(name=rn);g[rn].definition=name;reports.append(rn)
        # Native applied source is lagged; retain it separately from S(alpha_N).
        for rn,typ,field in [('p7b-applied-source','volume-sum','phase-2-user-mass-source'),('p7b-native-water','volume-integral','phase-2-vof')]:
            g=s.settings.solution.report_definitions.volume;g.create(name=rn);assert typ in g[rn].report_type.allowed_values();g[rn].set_state({'report_type':typ,'field':field,'cell_zones':zones});reports.append(rn)
        if a.spike_diagnostics:
            for name,field in [('P7bDiagnosticMaxK','TurbulentKineticEnergyk'),('P7bDiagnosticMaxEpsilon','TurbulenceDissipationRate')]:
                named(name,f'Maximum({field},{loc})')
                rn=name.lower();g=s.settings.solution.report_definitions.single_valued_expression
                g.create(name=rn);g[rn].definition=name;reports.append(rn)
        r['sections']={}
        for yy in [.5,1.5,3.,5.]:
            name='p7b-section-y'+str(yy).replace('.','p');g=s.settings.results.surfaces.iso_surface;g.create(name=name);g[name].set_state({'field':'y-coordinate','iso_values':[yy]})
            named('P7bSectionArea'+str(yy).replace('.','p'),f'Area(["{name}"])')
            area=nvalue('P7bSectionArea'+str(yy).replace('.','p'));assert area>0;r['sections'][name]={'y_m':yy,'area_m2':area}
        r['axial_sections']={}
        for axis in ['x','z']:
            name='p7b-e2-'+axis+'0';g=s.settings.results.surfaces.iso_surface;g.create(name=name)
            g[name].set_state({'field':axis+'-coordinate','iso_values':[0.]});r['axial_sections'][name]={axis+'_m':0.}
        rf=s.settings.solution.monitor.report_files;rf.create(name='p7b-screen-history');rf['p7b-screen-history'].set_state({'file_name':r['report'],'report_defs':reports,'frequency':1,'active':True})
        r['report_definitions']=s.settings.solution.report_definitions.get_state();r['initial_metrics']=step('initial_metrics',lambda:s.settings.solution.report_definitions.compute(report_defs=reports))
        r['selected_methods']=r['reference_methods'];r['selected_controls']=r['reference_controls']
        if a.coupled_off_capability:
            r['numerical_treatment']=step('apply_verified_coupled_off',lambda:apply_coupled_off(s,r['reference_methods'],r['reference_controls'],a.coupled_off_capability,a.coupled_flow_courant,a.solve_n_phase,a.nphase_before_hybrid))
            r['selected_methods']=r['numerical_treatment']['methods'];r['selected_controls']=r['numerical_treatment']['controls']
        if e7:
            control=json.loads((BASE/'output'/r['controlled_contrast_to']/'manifest.json').read_text())
            r['source_treatment']=verify_e7_delta(control,r)
        # Treatment can expose additional equation monitors; enumerate before save/solve.
        residuals=s.settings.solution.monitor.residual.equations
        before_monitors=r['residual_equations']
        names=residuals.get_object_names()
        assert BASE_RESIDUAL_EQUATIONS.issubset(names), 'Treatment removed a baseline residual'
        for eq in names:
            residuals[eq].monitor=True
            residuals[eq].check_convergence=False
        refreshed=residuals.get_state()
        for eq in before_monitors:exact_parity(before_monitors[eq],refreshed[eq],'existing residual policy '+eq)
        r['residual_equations_before_treatment']=before_monitors
        r['residual_equations']=refreshed
        r['expected_residual_equations']=list(names)
        r['added_residual_equations']=sorted(set(names)-set(before_monitors))
        expected_residual_equations(r)
        if a.nphase_before_hybrid:
            r['pre_reopen_prepared_parity']=step('verify_nphase_n0_before_prepared_reopen',lambda:pre_reopen_n0_parity(s,zones,out,'prepared'),300)
        prepared=save('prepared');step('reopen_prepared',lambda:s.settings.file.read_case_data(file_name=prepared),180)
        assert nvalue('P7bGlobalIteration')==0 and nvalue('P7bWaterVolume')==0
        for name,d in defs.items():assert s.settings.setup.named_expressions[name].definition()==d
        for z in zones:
            for ph in ['mixture','phase-1','phase-2']:assert s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state()==r['source_slots'][z][ph]
        exact_parity(r['selected_methods'],s.settings.solution.methods.get_state(),'reopened methods')
        exact_parity(r['selected_controls'],s.settings.solution.controls.get_state(),'reopened controls')
        exact_parity(r['residual_options'],s.settings.solution.monitor.residual.options.get_state(),'reopened residual options')
        exact_parity(r['residual_equations'],s.settings.solution.monitor.residual.equations.get_state(),'reopened residual equations')
        exact_parity(r['report_definitions'],s.settings.solution.report_definitions.get_state(),'reopened reports')
        assert s.settings.solution.run_calculation.profile_update_interval()==1
        r['reopened_metrics']=step('compute_reopened_reports',lambda:s.settings.solution.report_definitions.compute(report_defs=reports))
        r['build_verification']='SOURCE_MASK_SETUP_REPORTS_SAVE_REOPEN_PASS'
        r['initial_sections']=step('extract_initial_sections',lambda:export_sections(s,r['sections'],out/'initial-sections'),180)
        r['initial_axial_sections']=step('extract_initial_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'initial-axial-sections'),180)
        if a.spike_diagnostics:
            from pyansys_fluent.phase07b_spike_monitor import Phase07bSpikeMonitor
            diagnostic=Phase07bSpikeMonitor(s,zones,out/'spike-diagnostics',solve_n_phase=a.solve_n_phase)
            step('prove_spike_diagnostics_n0',diagnostic.prepare,300)
            r['spike_diagnostics']=diagnostic.manifest();persist()
        if a.coupled_off_capability:
            r['initial_field_parity']=step('prove_coupled_initial_fields',lambda:initial_field_parity(out,allow_nphase_primary_n0=a.solve_n_phase))
            refgeo=BASE/'output/p7b-s40-t020-diag-20260922T071533Z/spike-diagnostics/geometry.npz'
            with np.load(out/'spike-diagnostics/geometry.npz') as actual,np.load(refgeo) as expected:
                assert set(actual.files)==set(expected.files)
                assert all(np.array_equal(actual[k],expected[k]) for k in actual.files)
            r['initial_geometry_parity']={'status':'GEOMETRY_FIELDS_EXACTLY_EQUAL','reference':str(refgeo)}
            (out/'initial-geometry-parity.json').write_text(json.dumps(r['initial_geometry_parity'],indent=2)+'\n')
        s.transcript.stop();setup=(out/'setup.trn').read_text();assert 'SEGMENTATION VIOLATION' not in setup
        counts=re.findall(r'^\s*0\s+(620431)\s+(2852567)\s+(\d+)\s+(16)\s*$',setup,re.M);assert len(counts)>=2 and counts[0]==counts[1]
        s.transcript.start(file_name=str(out/'solve.trn'),write_to_stdout=False)
        step('start_remote_transcript',lambda:s.settings.file.start_transcript(file_name=r['remote_transcript']))
        m=Phase07bFluxMonitor(s,face_zones=face_zones,start_iteration=0,local_jsonl=out/'collector-flux.jsonl',remote_directory=ROOT+'/reports',after_capture=diagnostic.capture if diagnostic else None);m.register()
        r['status']='RUNNING';r['flux_monitor']=m.manifest();persist()
        targets=sorted(set([min(50,a.iterations)]+list(range(500,a.iterations+1,500))+[a.iterations]));current=0
        for target in targets:
            step(f'iterate_{current}_to_{target}',lambda target=target,current=current:s.settings.solution.run_calculation.iterate(iter_count=target-current),max(600,(target-current)*20))
            actual=int(nvalue('P7bGlobalIteration'));r['actual_iteration']=actual;assert actual==target,(actual,target)
            m.assert_complete(actual);r['flux_monitor']=m.manifest()
            if diagnostic:
                diagnostic.assert_complete(actual);r['spike_diagnostics']=diagnostic.manifest()
            # Verify the durable last row and complete native scalar history.
            last=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1]);assert json.loads(read_text(s,last['remote_path']))==last
            r.setdefault('remote_flux_readbacks',[]).append({'iteration':actual,'path':last['remote_path'],'matches_local':True})
            history=read_text(s,r['report']);(out/f'history-{actual:05d}.out').write_text(history)
            rows=np.loadtxt(history.splitlines(),skiprows=3);rows=np.atleast_2d(rows)
            assert np.array_equal(rows[:,0],np.arange(1,actual+1));assert np.isfinite(rows).all()
            solve=(out/'solve.trn').read_text();assert not any(x in solve for x in ['SEGMENTATION VIOLATION','floating point exception','Divergence detected'])
            residual_data,residual_audit=parse_residuals(out/'solve.trn')
            assert set(residual_data)=={'iteration'} | expected_residual_equations(r) and not residual_audit['conflicting_indices'] and not residual_audit['nonfinite_columns']
            assert set(range(1,actual+1)).issubset(residual_data['iteration']), 'Missing residual iterations'
            r['residual_coverage']=residual_audit
            if actual==50:r['instrumentation_smoke']=f'N1-50 scalar, exact-face flux, remote readback and all {len(r["expected_residual_equations"])} exposed residuals PASS'
            r['latest_metrics']=step(f'metrics_{actual}',lambda:s.settings.solution.report_definitions.compute(report_defs=reports))
            save('final' if actual==a.iterations else f'n{actual:05d}');current=actual;persist()
        m.unregister();r['flux_monitor']=m.manifest();m=None
        r['final_sections']=step('extract_final_sections',lambda:export_sections(s,r['sections'],out/'final-sections'),180)
        r['final_axial_sections']=step('extract_final_axial_sections',lambda:export_sections(s,r['axial_sections'],out/'final-axial-sections'),180)
        s.settings.file.stop_transcript();s.transcript.stop()
        r['status']='HORIZON_COMPLETE_ANALYSIS_PENDING' if a.iterations==5000 else 'PARTIAL_DIAGNOSTIC_COMPLETE';r['completed_iterations']=current;persist()
    except Exception as e:
        signal.alarm(0);r['status']='BLOCKED_EXECUTION';r['error']=str(e);(out/'error.txt').write_text(traceback.format_exc());persist();raise
    finally:
        signal.alarm(0)
        if m is not None:
            try:m.unregister()
            except Exception as e:r['callback_cleanup_error']=str(e)
            r['flux_monitor']=m.manifest()
        if s is not None:
            try:s.transcript.stop()
            except Exception:pass
        if diagnostic is not None:
            diagnostic.close();r['spike_diagnostics']=diagnostic.manifest()
        persist();print('EVIDENCE',out,flush=True)
if __name__=='__main__':main()
