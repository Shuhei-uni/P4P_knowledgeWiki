"""Build and prove a direct lower-film drain on owned Server 1; retain all parents."""
from pathlib import Path,PureWindowsPath
import argparse,copy,functools,json,math,re,sys,time,traceback
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts/setup'),str(ROOT/'src')]
import run_phase72a_stage4_setting_sensitivity as q
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.stage4_native import ensure_remote_directory,remote_file_sha256
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.film_thickness_guard import assess_thickness
from ansys.fluent.core.fields.field_data_interfaces import ScalarFieldDataRequest,SurfaceFieldDataRequest,SurfaceDataType
from run_phase72a_adaptive_film import FILM,history
OUT=ROOT/'output/phase72a-stage4-ewf-drain/20261007'
WORK=PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\ewf-drain-20261007')
MANIFEST=OUT/'run-manifest.json'
PARENT=ROOT/'output/phase72a-stage4-film-limit/20261007/run-manifest.json'
DT=15e-6
BULK=['v2-total-liquid-mass','v2-flux-phase2-steamoutlet','v2-flux-phase1-steamoutlet']


def attach():
    q.use_branch('stripping-on');s=q.r.parent.attach()
    s.rp_vars.allowed_values=functools.lru_cache(maxsize=1)(s.rp_vars.allowed_values)
    q.r.WORK=WORK
    print('CONNECTED_SERVER1',flush=True);return s


def facets(s,wall):
    result={}
    for field in ['film-mass','film-thickness','film-x-velocity','film-y-velocity','film-z-velocity']:
        result[field]=np.asarray(s.fields.field_data.get_field_data(ScalarFieldDataRequest(
            surfaces=[wall],field_name=field,node_value=False,boundary_value=True))[wall]).reshape(-1)
    assert all(np.isfinite(v).all() for v in result.values())
    assert (result['film-thickness']>=0).all()
    return result


def same_facets(before,after):
    assert before.keys()==after.keys()
    for key in before:assert np.array_equal(before[key],after[key]),'Changed existing film facets: '+key


def check_upper_reference(s):
    """Match mesh-face coordinates across restart/parallel reorderings."""
    old_geometry=np.load(OUT/'wall-geometry.npz')['centroids']
    geometry=np.asarray(s.fields.field_data.get_field_data(SurfaceFieldDataRequest(
        surfaces=['wall'],data_types=[SurfaceDataType.FacesCentroid]))['wall'].face_centroids)
    old_order=np.lexsort(old_geometry.T[::-1]);new_order=np.lexsort(geometry.T[::-1])
    assert len(np.unique(geometry,axis=0))==len(geometry)
    assert np.array_equal(old_geometry[old_order],geometry[new_order])
    before=dict(np.load(OUT/'parent-film-facets.npz'));after=facets(s,'wall')
    same_facets({k:v[old_order] for k,v in before.items()},{k:v[new_order] for k,v in after.items()})
    return {'unique_face_centres_matched':len(geometry),'film_mass_thickness_xyz_velocity_exact':True,
            'comparison_basis':'Geometry-matched faces; native stream order can change after a parallel restart'}


def define_reports(s):
    surface=s.settings.solution.report_definitions.surface
    fields={'mass':('surface-sum','film-mass'),'outflow':('surface-sum','film-outflow-mass'),
            'secondary':('surface-sum','film-phase2-mass'),'dpm':('surface-sum','film-dpm-mass-src'),
            'stripped':('surface-sum','film-stripped-mass'),'separated':('surface-sum','film-separated-mass'),
            'thickness':('surface-facetmax','film-thickness'),'courant':('surface-facetmax','film-courant-number')}
    names=[]
    for scope,walls in [('upper',['wall']),('lower',[drain.WALL]),('total',['wall',drain.WALL])]:
        for key,(report_type,field) in fields.items():
            name=f'p72d-{scope}-{key}'
            if name not in surface.get_object_names():surface.create(name=name)
            surface[name].set_state({'report_type':report_type,'field':field,'surface_names':walls})
            names.append(name)
    expr=s.settings.solution.report_definitions.single_valued_expression
    for suffix,expression in [('drain-rate','P72dRemoval'),('lower-inventory','P72dInventory')]:
        name='p72d-'+suffix
        if name not in expr.get_object_names():expr.create(name=name)
        expr[name].definition=expression;expr[name].average_over=1;names.append(name)
    files=s.settings.solution.monitor.report_files
    for name in names:
        if name not in files.get_object_names():files.create(name=name)
        files[name].report_defs=[name];files[name].frequency=1;files[name].active=True
    return names


def compute(s,names):
    result={}
    for group in s.settings.solution.report_definitions.compute(report_defs=names):result.update(group)
    return result


def load_pair(s,pair):
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    assert q.r.parent.native_iteration(s)==pair['native_iteration']


def reopen_pair(s,pair,enabled,production=True):
    before=q.r.state(s);clock=q.r.film(s)
    load_pair(s,pair);after=q.r.state(s)
    q.r.require_match(after['readback'],before['readback'])
    assert after['setup']==before['setup'] and after['methods']==before['methods']
    assert q.r.film(s)==clock
    assert not any(s.settings.solution.controls.equations.get_state().values())
    if production:q.r.audit(s)
    return drain.audit(s,enabled)


def instrument(s,folder,names=None):
    ensure_remote_directory(s,str(folder));paths={}
    files=s.settings.solution.monitor.report_files
    for name in files.get_object_names():
        obj=files[name];defs=obj.report_defs();assert len(defs)==1
        obj.active=names is None or defs[0] in names
        if not obj.active():continue
        path=str(folder/(defs[0]+'.out'))
        from pyansys_fluent.common import remote_file_exists
        if remote_file_exists(s,path):raise FileExistsError(path)
        obj.file_name=path;obj.frequency_of='iteration';obj.frequency=1
        assert defs[0] not in paths;paths[defs[0]]=path
    return paths


def persistent_reports_match(before,after):
    nonpersistent={name:{'native_solved':value,'reopened':after[name],
        'reason':'Instantaneous phase-accretion rate is cleared by native data read; solved file history owns the source ledger'}
        for name,value in before.items() if name.endswith('-secondary')}
    persistent={k:v for k,v in before.items() if k not in nonpersistent}
    q.r.require_match({'fields':{k:after[k] for k in persistent}},{'fields':persistent})
    return nonpersistent


def execute(s,arm,count,label,work,out,names,paths,enabled,production=True,reopen_now=True):
    """One native batch, followed by immutable source capture and persistence."""
    start=q.r.parent.native_iteration(s);end=start+count
    initial=compute(s,names);bulk=compute(s,BULK);clock=q.r.film(s)
    parameters=q.r.params(s);drain.audit(s,enabled)
    assert not any(s.settings.solution.controls.equations.get_state().values())
    if production:q.r.audit(s)
    tag=f'{label}-N{start}-N{end}';remote=work/(tag+'.trn')
    arm.update(status='RUNNING',active_target=end,active_segment=tag)
    q.r.dump(out/'run-manifest.json',arm)
    print('SUBMIT',tag,'film_dt',DT,flush=True)
    begun=time.monotonic();s.tui.file.start_transcript(str(remote))
    q.r.iterate(s,count)
    assert q.r.parent.native_iteration(s)==end
    pair=q.r.save(s,tag)
    final=compute(s,names);finalclock=q.r.film(s)
    s.tui.file.stop_transcript()
    rawdir=out/'raw'/tag;rawdir.mkdir(parents=True,exist_ok=False)
    transcript=read_text(s,str(remote));(rawdir/'solve.trn').write_text(transcript)
    printed=[tuple(map(float,v.groups())) for v in FILM.finditer(transcript)]
    assert len(printed)==count,(len(printed),count)
    assert all(math.isclose(v[1],DT,rel_tol=1e-7,abs_tol=1e-12) for v in printed)
    assert all(b[0]>a[0] for a,b in zip(printed,printed[1:]))
    printed_elapsed=printed[-1][0]-printed[0][0]+printed[0][1]
    assert math.isclose(printed_elapsed,count*DT,rel_tol=1e-6,abs_tol=1e-6), 'Printed film clock span differs'
    native_elapsed=finalclock['film_elapsed_time']-clock['film_elapsed_time']
    if production:
        assert math.isclose(native_elapsed,count*DT,rel_tol=1e-8,abs_tol=1e-10)
        time_basis='native RP film clock; native printed accepted steps cross-check'
    else:
        # Native fixture initialization can leave the RP cumulative clock
        # stale. The actual invocation count and printed film clocks govern.
        native_elapsed=count*DT
        time_basis='native printed accepted steps and film invocation count'
    h={}
    for name,source in paths.items():
        raw=read_text(s,source);(rawdir/(name+'.out')).write_text(raw)
        h[name]=history(raw)
        assert set(range(start+1,end+1)).issubset(h[name]),name
        assert all(math.isfinite(v) for v in h[name].values()),name
    assert q.r.params(s)==parameters
    q.r.require_match({'fields':compute(s,BULK)},{'fields':bulk})
    for wall in ['wall',drain.WALL]:facets(s,wall)
    thickness=assess_thickness({i:h['p72d-total-thickness'][i] for i in range(start+1,end+1)},.3)
    met={'native_start':start,'native_end':end,'updates':count,'step_s':DT,
         'film_elapsed_s':native_elapsed,'rp_film_clock_before':clock,'rp_film_clock_after':finalclock,
         'time_basis':time_basis,'printed_clock_first_s':printed[0][0],'printed_clock_last_s':printed[-1][0],
         'peak_courant':max(v[2] for v in printed),'thickness_assessment':thickness,
         'before':initial,'after':final,'bulk_before':bulk,'bulk_after':compute(s,BULK),
         'pair':pair,'raw_directory':str(rawdir.relative_to(ROOT.parent)),
         'wall_seconds':time.monotonic()-begun}
    if reopen_now:
        reopen_pair(s,pair,enabled,production)
        met['nonpersistent_reopen_reports']=persistent_reports_match(final,compute(s,names))
        met['reopen']='PASS'
    else:
        # Save the probe, but preserve native source cadence for the next 980
        # updates. The important prepared and final pairs are reopened.
        met['reopen']='PROBE_PAIR_SAVED_CONTINUE_WITHOUT_RELOAD'
    q.r.dump(out/(tag+'.json'),met)
    arm.setdefault('blocks',[]).append(met)
    arm.update(status='CHECKPOINT_VERIFIED',latest_pair=pair,verified_native_end=end,active_target=None)
    q.r.dump(out/'run-manifest.json',arm)
    if thickness['classification']=='UNREALISTIC':
        arm.update(status='UNREALISTIC',run_classification='UNREALISTIC');q.r.dump(out/'run-manifest.json',arm)
        raise RuntimeError('UNREALISTIC: 0.3 m film limit reached; endpoint preserved')
    assert met['peak_courant']<=1
    assert not re.search(r'floating point exception|received signal|fatal error|Divergence detected',transcript,re.I)
    print('BATCH_VERIFIED',tag,'CFL',met['peak_courant'],flush=True)
    return met,h


def restore_common(s,m):
    load_pair(s,m['common_parent_pair'])
    expected=json.loads((OUT/'common-reopened.json').read_text())
    actual=q.r.state(s)
    q.r.require_match(actual['readback'],expected['state']['readback'])
    assert actual['setup']==expected['state']['setup'] and actual['methods']==expected['state']['methods']
    assert q.r.film(s)==expected['film']
    facet_verification=check_upper_reference(s)
    assert np.max(np.abs(facets(s,drain.WALL)['film-mass']))<1e-12
    return {'native_iteration':q.r.parent.native_iteration(s),'film':q.r.film(s),
            'upper_film_facets_unchanged':True,'facet_verification':facet_verification,'lower_mass_zero':True,
            'drain':drain.audit(s,False),'bulk':compute(s,BULK)}


def prove_source(s):
    m=json.loads(MANIFEST.read_text());assert m['status']=='COMMON_PARENT_REOPEN_VERIFIED'
    work=WORK/'proof';out=OUT/'proof';out.mkdir(exist_ok=False)
    record={'status':'PREPARING','production_pair':m['common_parent_pair'],'seed_height_m':1e-4,
            'updates_per_arm':100,'arms':{},'step_s':DT}
    q.r.dump(out/'proof.json',record)
    try:
        restore_common(s,m)
        for folder in [work,work/'scratch']:ensure_remote_directory(s,str(folder))
        q.r.WORK=work
        changes={k:False for k in ['mom-gravity?','mom-aero-drive?','mom-wall-visc?',
             'mom-pressure?','mom-spreading?','surface-tension?','dpm-collection?',
             'dpm-splashing?','film-separation?','film-stripping?']}
        changes['secondary-phase-mode']=0;q.r.setparams(s,changes)
        for name in ['wall',drain.WALL]:
            wall=s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film
            wall.film_condition_type='film-wall-initial'
            wall.film_height.set_state({'option':'value','value':1e-4 if name==drain.WALL else 0.0})
        s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        assert q.r.params(s)['film-coupled-solution?']
        seed_fields=facets(s,drain.WALL)
        for key in ['film-x-velocity','film-y-velocity','film-z-velocity']:
            assert np.max(np.abs(seed_fields[key]))<1e-12
        assert np.max(np.abs(facets(s,'wall')['film-mass']))<1e-12
        selected=['p72d-lower-mass','p72d-lower-outflow','p72d-lower-thickness',
                  'p72d-lower-courant','p72d-total-thickness','p72d-drain-rate','p72d-lower-inventory']
        # Disabled mechanism fields need not exist in the fixture.
        for name in s.settings.solution.monitor.report_files.get_object_names():
            s.settings.solution.monitor.report_files[name].active=False
        fixture=q.r.save(s,'seed-N'+str(q.r.parent.native_iteration(s)))
        record.update(seed_pair=fixture,fixture_parameters=q.r.params(s),seed_fields={k:v.tolist() for k,v in seed_fields.items()})
        q.r.dump(out/'proof.json',record)
        for name,enabled in [('off',False),('on',True)]:
            load_pair(s,fixture);drain.set_enabled(s,enabled)
            armwork=work/name;armout=out/name;armout.mkdir(exist_ok=False)
            for folder in [armwork,armwork/'scratch']:ensure_remote_directory(s,str(folder))
            q.r.WORK=armwork;paths=instrument(s,armwork/'monitors',selected)
            arm={'status':'PREPARED','source_enabled':enabled,'parent_pair':fixture,'report_paths':paths,'blocks':[]}
            met,h=execute(s,arm,100,'source-proof',armwork,armout,selected,paths,enabled,production=False)
            x=np.arange(met['native_start']+1,met['native_end']+1)
            mass=np.array([met['before']['p72d-lower-mass'][0]]+[h['p72d-lower-mass'][int(i)] for i in x])
            rate=np.array([met['before']['p72d-drain-rate'][0]]+[h['p72d-drain-rate'][int(i)] for i in x])
            inventory=np.array([met['before']['p72d-lower-inventory'][0]]+[h['p72d-lower-inventory'][int(i)] for i in x])
            assert np.allclose(mass,inventory,rtol=1e-5,atol=1e-10)
            record['arms'][name]={'metrics':met,'mass_kg':mass.tolist(),'rate_kg_s':rate.tolist(),
                'native_iteration':[met['native_start']]+x.tolist(),'elapsed_film_time_s':(np.arange(101)*DT).tolist()}
            q.r.dump(out/'proof.json',record)
        off=record['arms']['off'];on=record['arms']['on'];a=np.array(on['mass_kg']);rate=np.array(on['rate_kg_s'])
        assert math.isclose(off['mass_kg'][0],a[0],rel_tol=1e-10)
        off_change=off['mass_kg'][-1]-off['mass_kg'][0]
        loss=-np.diff(a);fraction=loss/a[:-1]
        errors=loss/(rate[:-1]*DT)-1
        removed=a[0]-a[-1]
        native_outflow=on['metrics']['after']['p72d-lower-outflow'][0]-on['metrics']['before']['p72d-lower-outflow'][0]
        assert abs(off_change)<a[0]*1e-5 and removed>0 and a.min()>=0
        assert fraction.min()>=-1e-6 and fraction.max()<=.0105 and np.max(np.abs(errors))<=.03
        assert max(off['rate_kg_s'])==0
        if abs(native_outflow-removed)<removed*.03:convention='USER_DRAIN_INCLUDED_IN_NATIVE_OUTFLOW'
        elif abs(native_outflow)<removed*1e-5:convention='USER_DRAIN_EXCLUDED_FROM_NATIVE_OUTFLOW'
        else:raise RuntimeError('Native outflow/source counting convention remains unresolved')
        record.update(status='SOURCE_PROVED_PENDING_RESTORE',off_change_kg=off_change,on_removed_kg=removed,
            depletion_fraction_min=float(fraction.min()),depletion_fraction_max=float(fraction.max()),
            source_integral_relative_error_max=float(np.max(np.abs(errors))),native_outflow_change_kg=native_outflow,
            outflow_convention=convention,physical_validation=False)
    finally:
        q.r.WORK=WORK
        try:record['production_restoration']=restore_common(s,m)
        finally:q.r.dump(out/'proof.json',record)
    assert record['status']=='SOURCE_PROVED_PENDING_RESTORE'
    record['status']='SOURCE_REMOVAL_VERIFIED';q.r.dump(out/'proof.json',record)
    m.update(status='SOURCE_PROOF_VERIFIED',source_proof=str((out/'proof.json').relative_to(ROOT.parent)),
             outflow_convention=record['outflow_convention']);q.r.dump(MANIFEST,m)
    print('SOURCE_REMOVAL_VERIFIED',record['on_removed_kg'],record['outflow_convention'],flush=True)


def screen(s,name):
    enabled=name=='on';m=json.loads(MANIFEST.read_text())
    assert m['status'] in ['SOURCE_PROOF_VERIFIED','DRAIN_SCREENS_RUNNING','DRAIN_SCREEN_VERIFIED']
    assert name not in m['branches'],'Matched branch already exists: reconcile its native receipt'
    work=WORK/name;out=OUT/name;out.mkdir(exist_ok=False)
    load_pair(s,m['common_parent_pair']);drain.set_enabled(s,enabled)
    for folder in [work,work/'scratch']:ensure_remote_directory(s,str(folder))
    q.r.WORK=work;paths=instrument(s,work/'monitors')
    names=m['report_names'];initial=compute(s,names)
    prepared=q.r.save(s,'prepared-N40483');reopen_pair(s,prepared,enabled)
    check_upper_reference(s)
    assert initial['p72d-lower-mass'][0]==0 and initial['p72d-drain-rate'][0]==0
    arm={'status':'PREPARED_VERIFIED','source_enabled':enabled,'common_parent_pair':m['common_parent_pair'],
         'prepared_pair':prepared,'report_paths':paths,'initial':initial,'parent_native_iteration':40483,
         'parent_film_time_s':q.r.film(s)['film_elapsed_time'],'outflow_convention':m['outflow_convention'],'blocks':[]}
    q.r.dump(out/'run-manifest.json',arm)
    m['status']='DRAIN_SCREENS_RUNNING';m['branches'][name]={'status_owner':str((out/'run-manifest.json').relative_to(ROOT.parent)),'status':arm['status']}
    q.r.dump(MANIFEST,m)
    for count,label in ([(20,'drain-probe'),(980,'drain-screen')] if enabled else [(1000,'drain-screen')]):
        execute(s,arm,count,label,work,out,names,paths,enabled,reopen_now=label!='drain-probe')
    arm.update(status='SCREEN_COMPLETE_VERIFIED',final_pair=arm['latest_pair'],
               final=compute(s,names),film=q.r.film(s),drain=drain.audit(s,enabled))
    q.r.dump(out/'run-manifest.json',arm)
    np.savez_compressed(out/'upper-endpoint.npz',**facets(s,'wall'))
    np.savez_compressed(out/'lower-endpoint.npz',**facets(s,drain.WALL))
    m['branches'][name].update(status=arm['status'],final_pair=arm['final_pair'])
    m.update(status='DRAIN_SCREEN_VERIFIED',latest_pair=arm['final_pair'])
    if all(v['status']=='SCREEN_COMPLETE_VERIFIED' for v in m['branches'].values()) and set(m['branches'])=={'off','on'}:
        m.update(status='DRAIN_COMPLETE_VERIFIED',final_pair=m['branches']['on']['final_pair'],
                 solver_left_open=True,bulk_equations_frozen=True)
        if name!='on':load_pair(s,m['final_pair'])
    q.r.dump(MANIFEST,m);q.r.WORK=WORK
    print('SCREEN_COMPLETE_VERIFIED',name,flush=True)
    if m['status']=='DRAIN_COMPLETE_VERIFIED':verify_final(s)


def verify_final(s):
    m=json.loads(MANIFEST.read_text());assert m['status']=='DRAIN_COMPLETE_VERIFIED'
    assert q.r.parent.native_iteration(s)==m['final_pair']['native_iteration']==41483
    common=json.loads((OUT/'common-reopened.json').read_text())
    current=q.r.state(s);expected=copy.deepcopy(common['state']['setup'])
    expected['named_expressions']['P72dEnabled']['definition']='1'
    assert current['setup']==expected
    assert current['methods']==common['state']['methods']
    assert current['film_model']==common['state']['film_model']
    assert not any(s.settings.solution.controls.equations.get_state().values())
    q.r.audit(s);da=drain.audit(s,True)
    clock=q.r.film(s);assert math.isclose(clock['film_elapsed_time']-m['parent_film_time_s'],.015,rel_tol=0,abs_tol=1e-10)
    before=json.loads((OUT/'before-build.json').read_text())['state']['readback']['fields']
    expectedbulk={k:v for k,v in before.items() if k in compute(s,BULK)}
    bulk=compute(s,BULK)
    q.r.require_match({'fields':{k:bulk[k] for k in expectedbulk}},{'fields':expectedbulk})
    for name in ['off','on']:
        arm=json.loads((OUT/name/'run-manifest.json').read_text())
        assert arm['status']=='SCREEN_COMPLETE_VERIFIED' and sum(b['updates'] for b in arm['blocks'])==1000
        assert arm['blocks'][-1]['reopen']=='PASS'
        assert all(b['reopen'] in ['PASS','PROBE_PAIR_SAVED_CONTINUE_WITHOUT_RELOAD'] and b['peak_courant']<=1 and b['thickness_assessment']['classification']!='UNREALISTIC' for b in arm['blocks'])
    source=json.loads((OUT/'proof/proof.json').read_text());assert source['status']=='SOURCE_REMOVAL_VERIFIED'
    proof={'status':'PASS','native_iteration':41483,'film':clock,'bulk':bulk,
           'bulk_equations':s.settings.solution.controls.equations.get_state(),'drain':da,
           'only_production_physical_delta_from_expanded_common_parent':'P72dEnabled 0 → 1',
           'original_upper_film_physics_and_numerics_retained':True,
           'matched_screens_verified_updates_each':1000,'native_source_proof':'PASS',
           'film_limit_m':.3,'final_pair':m['final_pair'],'physical_validation':False}
    q.r.dump(OUT/'verification.json',proof);m['final_verification']='PASS';q.r.dump(MANIFEST,m)
    print('FINAL_VERIFICATION_PASS',flush=True)


def reconcile_screen(s,name):
    """Recover a completed batch's restart-rate check; never issue a solve."""
    m=json.loads(MANIFEST.read_text());assert m['status']=='IMPLEMENTATION_RECOVERY_REQUIRED'
    assert "Local parent/readback mismatch: {'fields': False}" in m['error']
    work=WORK/name;out=OUT/name;q.r.WORK=work
    arm=json.loads((out/'run-manifest.json').read_text());assert arm['status']=='RUNNING'
    end=arm['active_target'];assert q.r.parent.native_iteration(s)==end==41483
    assert not arm['blocks'] and name=='off', 'Only the unrecorded first OFF endpoint is reconciled here'
    start=arm['parent_native_iteration'];count=end-start;assert count==1000
    tag=arm['active_segment'];raw=out/'raw'/tag;assert raw.is_dir()
    h={n:history((raw/(n+'.out')).read_text()) for n in arm['report_paths']}
    assert all(set(range(start+1,end+1)).issubset(v) for v in h.values())
    solved={n:[h[n][end],arm['initial'][n][1]] for n in arm['initial']}
    nonpersistent=persistent_reports_match(solved,compute(s,list(solved)))
    pair={'case':str(work/(tag+'.cas.h5')),'data':str(work/(tag+'.dat.h5')),'native_iteration':end}
    stamp=str(time.time_ns())
    for kind in ['case','data']:
        pair[kind+'_sha256']=remote_file_sha256(s,pair[kind],str(work/'scratch'/f'reconcile-{stamp}-{kind}.sha256'))
    q.r.audit(s);drain.audit(s,False)
    common=json.loads((OUT/'common-reopened.json').read_text());clock=q.r.film(s)
    assert math.isclose(clock['film_elapsed_time']-common['film']['film_elapsed_time'],count*DT,abs_tol=1e-10)
    text=(raw/'solve.trn').read_text();printed=[tuple(map(float,v.groups())) for v in FILM.finditer(text)]
    assert len(printed)==count and all(math.isclose(v[1],DT,rel_tol=1e-7) for v in printed)
    assert all(b[0]>a[0] for a,b in zip(printed,printed[1:]))
    assert math.isclose(printed[-1][0]-printed[0][0]+DT,count*DT,abs_tol=1e-6)
    thickness=assess_thickness({i:h['p72d-total-thickness'][i] for i in range(start+1,end+1)},.3)
    assert thickness['classification']!='UNREALISTIC' and max(v[2] for v in printed)<=1
    beforebulk=compute(s,BULK)
    knownbulk={k:v for k,v in common['state']['readback']['fields'].items() if k in beforebulk}
    q.r.require_match({'fields':{k:beforebulk[k] for k in knownbulk}},{'fields':knownbulk})
    met={'native_start':start,'native_end':end,'updates':count,'step_s':DT,'film_elapsed_s':count*DT,
         'rp_film_clock_before':common['film'],'rp_film_clock_after':clock,
         'time_basis':'Native RP film clock and complete native printed-step history',
         'printed_clock_first_s':printed[0][0],'printed_clock_last_s':printed[-1][0],
         'peak_courant':max(v[2] for v in printed),'thickness_assessment':thickness,
         'before':arm['initial'],'after':solved,'bulk_before':beforebulk,'bulk_after':compute(s,BULK),
         'pair':pair,'raw_directory':str(raw.relative_to(ROOT.parent)),'reopen':'PASS',
         'nonpersistent_reopen_reports':nonpersistent,'reconciliation_new_solver_updates':0,
         'reconstructed_from':'Saved pair, complete immutable native report/transcript files, recorded initial fields'}
    q.r.dump(out/(tag+'.json'),met)
    q.r.dump(OUT/('screen-reconciliation-'+stamp+'.json'),{'original_error':m.pop('error'),
             'new_solver_updates':0,'nonpersistent_reopen_reports':nonpersistent,'paired_endpoint':pair})
    arm.update(status='SCREEN_COMPLETE_VERIFIED',blocks=[met],latest_pair=pair,final_pair=pair,
               verified_native_end=end,active_target=None,final=compute(s,list(solved)),film=clock,drain=drain.audit(s,False))
    q.r.dump(out/'run-manifest.json',arm)
    np.savez_compressed(out/'upper-endpoint.npz',**facets(s,'wall'))
    np.savez_compressed(out/'lower-endpoint.npz',**facets(s,drain.WALL))
    m['branches'][name].update(status=arm['status'],final_pair=pair)
    m.update(status='DRAIN_SCREEN_VERIFIED',latest_pair=pair);q.r.dump(MANIFEST,m);q.r.WORK=WORK
    print('SCREEN_RECONCILED_NO_NEW_SOLVES',name,flush=True)


def build(s,reconcile=False):
    if MANIFEST.exists():
        if not reconcile:raise RuntimeError('Existing drain build must be reconciled, not repeated')
        previous=json.loads(MANIFEST.read_text())
        assert previous['status']=='IMPLEMENTATION_RECOVERY_REQUIRED'
        q.r.dump(OUT/('build-failure-'+str(time.time_ns())+'.json'),previous)
    parent=json.loads(PARENT.read_text())
    assert parent['status']=='CONFIGURED_REOPEN_VERIFIED'
    for folder in [WORK,WORK/'scratch',WORK/'monitors']:ensure_remote_directory(s,str(folder))
    if 'P71V2Iteration' in s.settings.setup.named_expressions.get_object_names():
        current_n=q.r.parent.native_iteration(s)
        if current_n!=40483:
            q.r.save(s,'preserved-restart-N'+str(current_n)+'-'+str(time.time_ns()))
    elif s.settings.setup.boundary_conditions.is_active():
        assert not s.settings.setup.boundary_conditions.wall.get_object_names(), 'Unidentified loaded restart case'
    s.settings.file.read_case(file_name=parent['final_pair']['case'])
    s.settings.file.read_data(file_name=parent['final_pair']['data'])
    assert q.r.parent.native_iteration(s)==40483
    before=q.r.state(s);clock=q.r.film(s);original=facets(s,'wall')
    assert before['film_model']['thickness-limit']==.3 and not any(q.r.audit(s)['equations'].values())
    known=json.loads((PARENT.parent/'reopened.json').read_text())
    q.r.require_match(before['readback'],known['state']['readback'])
    for kind in ['case','data']:
        assert remote_file_sha256(s,parent['final_pair'][kind],str(WORK/'scratch'/f'parent-{kind}-{time.time_ns()}.sha256'))==parent['final_pair'][kind+'_sha256']
    m={'status':'BUILDING','authority':'human_20261007_direct_EWF_only_drain','server_id':'1',
       'parent_pair':parent['final_pair'],'parent_native_iteration':40483,'parent_film_time_s':clock['film_elapsed_time'],
       'work_root':str(WORK),'output_root':str(OUT),'film_step_s':DT,'film_limit_m':.3,
       'bulk_equations_frozen':True,'physical_validation':False,'tau_s':.0015,'branches':{}}
    q.r.dump(MANIFEST,m);q.r.dump(OUT/'before-build.json',{'state':before,'film':clock})
    lower=s.settings.setup.boundary_conditions.wall[drain.WALL].phase['mixture'].wall_film
    lower.eulerian_film_wall=True;lower.film_condition_type='film-wall-initial'
    lower.film_height.set_state({'option':'value','value':0.0})
    lower.enable_flow_momentum_coupling=False
    lower.enable_film_source_terms=False
    # Fluent does not safely expose an added wall's film fields until storage
    # is allocated. Never query the lower fields before this operation.
    m['status']='ALLOCATING_NEW_STORAGE_RESTORING_PARENT_DATA';q.r.dump(MANIFEST,m)
    print('ALLOCATE_NEW_LOWER_FILM_STORAGE',flush=True)
    s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
    s.settings.file.read_data(file_name=parent['final_pair']['data'])
    q.r.setparams(s,before['film_model'])
    added=facets(s,drain.WALL)
    assert np.max(np.abs(added['film-mass']))<1e-12
    m['new_storage_allocation']='NATIVE_ALLOCATION_THEN_EXACT_ORIGINAL_DATA_RESTORED'
    same_facets(original,facets(s,'wall'))
    assert q.r.parent.native_iteration(s)==40483 and q.r.film(s)==clock
    q.r.require_match({'fields':q.r.state(s)['readback']['fields']},{'fields':before['readback']['fields']})
    m['drain_configuration']=drain.configure(s,enabled=False)
    m['report_names']=define_reports(s)
    m['report_paths']=q.r.instrument(s,WORK/'monitors')
    s.settings.file.auto_save.data_frequency=0
    current=q.r.state(s)
    expected=copy.deepcopy(before['setup'])
    expected['boundary_conditions']['wall'][drain.WALL]['phase']['mixture']['wall_film']=current['setup']['boundary_conditions']['wall'][drain.WALL]['phase']['mixture']['wall_film']
    expected['named_expressions']=current['setup']['named_expressions']
    for name,value in before['setup']['named_expressions'].items():assert current['setup']['named_expressions'][name]==value
    assert current['setup']==expected and current['methods']==before['methods']
    assert current['film_model']==before['film_model']
    pair=q.r.save(s,'common-N40483');q.r.reopen(s,pair)
    same_facets(original,facets(s,'wall'))
    assert q.r.film(s)==clock and q.r.parent.native_iteration(s)==40483
    assert np.max(np.abs(facets(s,drain.WALL)['film-mass']))<1e-12
    q.r.dump(OUT/'common-reopened.json',{'state':q.r.state(s),'film':q.r.film(s),'drain':drain.audit(s,False),
             'reports':compute(s,m['report_names'])})
    m.update(status='COMMON_PARENT_REOPEN_VERIFIED',common_parent_pair=pair,latest_pair=pair,
             unchanged_existing_upper_film_facets=True,original_bulk_data_restored=True,unchanged_bulk_reports=True,
             new_lower_initial_mass_kg=0,ready_step_s=DT)
    q.r.dump(MANIFEST,m);print('COMMON_PARENT_REOPEN_VERIFIED',json.dumps(pair),flush=True)


def main():
    p=argparse.ArgumentParser();actions=p.add_mutually_exclusive_group(required=True)
    actions.add_argument('--build',action='store_true');actions.add_argument('--reconcile-build',action='store_true')
    actions.add_argument('--proof',action='store_true');actions.add_argument('--reconcile-proof',action='store_true')
    actions.add_argument('--screen',choices=['off','on']);actions.add_argument('--reconcile-screen',choices=['off','on'])
    actions.add_argument('--verify',action='store_true');args=p.parse_args()
    s=attach()
    if args.build or args.reconcile_build:build(s,reconcile=args.reconcile_build)
    elif args.proof:prove_source(s)
    elif args.reconcile_proof:
        m=json.loads(MANIFEST.read_text());proof=json.loads((OUT/'proof/proof.json').read_text())
        assert m['status']=='IMPLEMENTATION_RECOVERY_REQUIRED' and proof['status']=='PREPARING' and not proof['arms']
        assert 'Changed existing film facets' in m['error']
        verification=restore_common(s,m)
        stamp=str(time.time_ns());(OUT/'proof').rename(OUT/('proof-preflight-recovery-'+stamp))
        q.r.dump(OUT/('proof-preflight-reconciliation-'+stamp+'.json'),{'original_error':m.pop('error'),
            'verification':verification,'new_solver_updates':0,'cause':'Native face stream order changed after Server 1 restart; all geometry-matched face values are exactly preserved'})
        m['status']='COMMON_PARENT_REOPEN_VERIFIED';q.r.dump(MANIFEST,m);prove_source(s)
    elif args.screen:screen(s,args.screen)
    elif args.reconcile_screen:reconcile_screen(s,args.reconcile_screen)
    elif args.verify:verify_final(s)
    else:raise RuntimeError('Select an explicit operation')


if __name__=='__main__':
    try:main()
    except Exception:
        if MANIFEST.exists():
            m=json.loads(MANIFEST.read_text())
            rejected=any((OUT/name/'run-manifest.json').exists() and json.loads((OUT/name/'run-manifest.json').read_text()).get('run_classification')=='UNREALISTIC' for name in ['off','on'])
            m.update(status='UNREALISTIC' if rejected else 'IMPLEMENTATION_RECOVERY_REQUIRED',error=traceback.format_exc());q.r.dump(MANIFEST,m)
        raise
