"""Caller-owned local conservative absorber discovery; no launch/exit/attach."""
from pathlib import Path
import math
import json
from pyansys_fluent.ewf_absorber import define_expressions, LOWER_ZONE
from run_phase72a_r3_ewf_absorber_direct import dump, save_pair, file_history, apply_roughness, film_mass, configure_autosave

ENTRY_FACES = ['interior--separator-purnanto:010','interior--separator-purnanto:007']
TAUS = {'1ms': 1e-3, '100us': 1e-4, '10us': 1e-5, '1us':1e-6}

def configure_bulk(s, label, library):
    tau = TAUS[label]
    mat = s.settings.setup.models.multiphase.phases['phase-2'].material()
    rho = float(s.settings.setup.materials.fluid[mat].density.get_state()['value'])
    define_expressions(s, {
        'P72ContactTau': f'{tau:.17g}[s]',
        'P72ContactRho': f'{rho:.17g}[kg/m^3]',
        'P71V2Sink': '-P72ContactRho*P71V2Alpha/P72ContactTau',
        'P72ContactInventory': 'P72ContactRho*P71V2AvailableVolume',
        'P72ContactRemoval': f'-VolumeInt(P71V2Sink,["{LOWER_ZONE}"])',
    })
    z = s.settings.setup.cell_zone_conditions.fluid[LOWER_ZONE]
    z.phase['phase-2'].sources.terms['mass'].set_state([{'option':'udf','udf': f'contact_mass_{label}::{library}'}])
    for axis in 'xyz':
        z.phase['mixture'].sources.terms[f'{axis}-momentum'].set_state([{'option':'udf','udf':f'contact_{axis}_{label}::{library}'}])
    assert not z.phase['phase-1'].sources.enable()
    return z.get_state()

def prepare(s, work, out, library):
    upper_before=film_mass(s)
    lower=s.settings.setup.boundary_conditions.wall['wall:004'].phase['mixture'].wall_film
    assert not lower.eulerian_film_wall()
    params=s.rp_vars('wall-film/model-parameters')
    s.rp_vars('wall-film/model-parameters',[(k,1.0 if k=='thickness-limit' else v) for k,v in params])
    rough=apply_roughness(s,'R3',5e-4,.5)
    assert abs(film_mass(s)-upper_before)<1e-8
    reports=s.settings.solution.report_definitions
    for name,exp in {'p72-contact-inventory':'P72ContactInventory','p72-contact-removal':'P72ContactRemoval'}.items():
        if name not in reports.single_valued_expression.get_object_names(): reports.single_valued_expression.create(name=name)
        reports.single_valued_expression[name].definition=exp
    if 'p72-contact-alpha-max' not in reports.volume.get_object_names(): reports.volume.create(name='p72-contact-alpha-max')
    reports.volume['p72-contact-alpha-max'].set_state({'report_type':'volume-max','field':'phase-2-vof','cell_zones':[LOWER_ZONE]})
    manifest={'status':'PREPARED','work_root':str(work),'execution':'direct-fluent-use','server_access':False,
      'parent_native_iteration':13586,'upper_film_mass_before_kg':upper_before,'roughness':rough,
      'bulk_policy':'independent_implicit_liquid_depletion','film_policy':'native_outflow_at_lower_EWF_edge',
      'region':'existing_cell_centroid_selected_lower_zone_not_fitted_y0p1_plane','screens':[]}
    dump(out/'run-manifest.json',manifest)
    return manifest

def instrument(s, folder):
    folder.mkdir(parents=True,exist_ok=False)
    files=s.settings.solution.monitor.report_files
    names=['p72-contact-inventory','p72-contact-removal','p72-contact-alpha-max']
    for name in names:
        if name not in files.get_object_names(): files.create(name=name)
        files[name].report_defs=[name]
    paths={}
    for name in files.get_object_names():
        obj=files[name]
        defs=obj.report_defs()
        if len(defs)!=1: raise RuntimeError(f'Multi-report file not supported: {name}')
        report=defs[0]
        if report in paths: raise RuntimeError(f'Duplicate report history: {report}')
        path=folder/f'{report}.out'
        obj.file_name=str(path);obj.frequency_of='iteration';obj.frequency=1;obj.active=True
        paths[report]=path
    return paths

def snapshot(s):
    names=['p72-contact-inventory','p72-contact-removal','p72-contact-alpha-max',
      'p72a-e2.7-ewf-film-mass-total','p72a-e2.7-ewf-thickness-max',
      'p72a-e2.7-ewf-outflow-mass-total','v2-total-liquid-mass',
      'v2-flux-phase2-liquidinlet','v2-flux-phase1-steaminlet',
      'v2-applied-absorber','v2-flux-phase2-steamoutlet','v2-flux-phase1-steamoutlet']
    available={name for group in s.settings.solution.report_definitions.get_state().values()
               if isinstance(group,dict) for name in group}
    selected=[n for n in names if n in available]
    values={}
    for record in s.settings.solution.report_definitions.compute(report_defs=selected): values.update(record)
    return values

def run_screen(s, work, out, label, library, parent_data, count=100, film_dt=1e-5, tag=None):
    # Fresh physical data for each coefficient. Case settings/source hooks persist.
    s.settings.file.read_data(file_name=str(parent_data))
    # EWF RP parameters are also restored by read-data, so apply AFTER that.
    parameters=s.rp_vars('wall-film/model-parameters')
    s.rp_vars('wall-film/model-parameters',[(k,1.0 if k=='thickness-limit' else film_dt if k=='timestep-max' else v) for k,v in parameters])
    hooks=configure_bulk(s,label,library)
    tag=tag or label
    paths=instrument(s,work/tag/'monitors')
    prepared=save_pair(s,work/tag/'prepared-N13586.cas.h5',13586)
    s.settings.file.read_case(file_name=prepared['case'])
    s.settings.file.read_data(file_name=prepared['data'])
    s.tui.define.models.eulerian_wallfilm.solve_wallfilm_equation('yes')
    configure_autosave(s,str(work),data_frequency=1000)
    before=snapshot(s)
    record={'label':label,'tag':tag,'tau_s':TAUS[label],'count':count,'hooks':hooks,'before':before,
            'film_parameters':dict(s.rp_vars('wall-film/model-parameters')),'prepared_pair':prepared}
    dump(out/f'{tag}-screen.json',record)
    s.tui.solve.iterate(count)
    record['after']=snapshot(s)
    histories={name:file_history(path) for name,path in paths.items()}
    coordinate=histories['p72-contact-inventory']['iterations'][-1]
    record['native_end']=coordinate
    record['checkpoint']=save_pair(s,work/tag/f'screen-N{coordinate}.cas.h5',coordinate)
    dump(out/f'{tag}-histories.json',histories)
    record['history_path']=str(out/f'{tag}-histories.json')
    record['status']='COMPLETE_SCREEN'
    dump(out/f'{tag}-screen.json',record)
    print('CONTACT_SCREEN_COMPLETE',label,coordinate,record['after'],flush=True)
    return record

def prepare_dpm_fixture(s):
    """Disposable liquid-density inert parcels; carrier mass is not reinjected."""
    from pyansys_fluent.setup_dpm import ensure_inert_particle_material
    dpm=s.settings.setup.models.discrete_phase
    original=dpm.injections.get_state()
    dpm.injections.delete(name_list=list(original))
    for name in ['contact-proof-down','contact-proof-up']: dpm.injections.create(name=name)
    ensure_inert_particle_material(s,'contact-proof-liquid',881.2108764648438,strict=True)
    dpm.general_settings.interaction.enabled=False
    dpm.tracking.max_num_steps=50000
    dpm.tracking.step_size_controls.set_state({'option':'step-length-factor','step_length_factor':5})
    bc=s.settings.setup.boundary_conditions
    for zone in ENTRY_FACES:
        bc.set_zone_type(zone_list=[zone],new_type='porous-jump')
        jump=bc.porous_jump[zone].phase['mixture']
        jump.porous_jump.dm=0
        jump.porous_jump.c2=0
        jump.discrete_phase.bc_type='escape'
    for zone in ['bottom','wall:004','separator-purnanto:1:001']:
        bc.wall[zone].phase['mixture'].discrete_phase.bc_type='escape'
    for name,vy in [('contact-proof-down',-20.0),('contact-proof-up',20.0)]:
        inj=dpm.injections[name]
        inj.particle_type='inert';inj.material='contact-proof-liquid'
        inj.injection_type.option='single'
        inj.initial_values.location.set_state({'x':0.80,'y':0.30,'z':0.0})
        # Mesh-verified fluid vertex-centroid of cell 13970, adjacent to
        # steamoutlet face 6741. Fluid lies ABOVE its y=6.261 cut plane.
        if name=='contact-proof-up':
            inj.initial_values.location.set_state({'x':0.0051531635,'y':6.2665159,'z':0.00122780561})
            vy=-20.0
        inj.initial_values.velocity.set_state({'x_velocity':0.,'y_velocity':vy,'z_velocity':0.})
        inj.initial_values.particle_size.set_state({'option':'uniform','diameter':0.005})
        inj.initial_values.mass_flow_rate.flow_rate=0.001
        inj.physical_models.turbulent_dispersion.enabled=False
    return {'original_injections':original,
            'entry_faces':{z:bc.porous_jump[z].get_state() for z in ENTRY_FACES},
            'injections':dpm.injections.get_state(),'interaction':dpm.general_settings.interaction.get_state()}

def test_dpm_capture(s,work,out,capture,include_down=True,suffix='proof'):
    from run_dpm_particle_tracks import configure_particle_track_summary
    from pyansys_fluent.dpm_transcript import track_one_injection_streamed
    fixture=prepare_dpm_fixture(s)
    dump(out/f'dpm-{suffix}-fixture-setup.json',fixture)
    configure_particle_track_summary(s)
    s.scheme.eval('(ti-menu-load-string "/report/dpm-zone-summaries-per-injection? yes")')
    records=[]
    dpm=s.settings.setup.models.discrete_phase
    for interacting in [False,True]:
        dpm.general_settings.interaction.enabled=interacting
        for factor in [5,20]:
            dpm.tracking.step_size_controls.step_length_factor=factor
            for diameter in [50e-6,500e-6,5e-3]:
                for name in (['contact-proof-down','contact-proof-up'] if include_down else ['contact-proof-up']):
                    dpm.injections[name].initial_values.particle_size.diameter=diameter
                    tag=f'{suffix}-{name}-{diameter:g}-step{factor}-interaction{interacting}'
                    result=track_one_injection_streamed(s,{'name':name,'index':dpm.injections.get_object_names().index(name)},capture,
                        timeout_seconds=60,raw_output_path=out/f'{tag}.txt')
                    result.update(diameter_m=diameter,step_length_factor=factor,interaction=interacting)
                    records.append(result)
                    dump(out/f'dpm-{suffix}.json',{'fixture':fixture,'records':records})
                    if result['status']!='ok': raise RuntimeError(f'Incomplete DPM proof: {tag}')
                    counts=result['parsed']['counts']
                    if counts['tracked']<1 or any(counts[k] for k in ['aborted','incomplete','evaporated','trapped']):
                        raise RuntimeError(f'Unresolved/unintended DPM fate: {tag}: {counts}')
    # Restore inherited injection definitions and one-way model after the fixture.
    dpm.injections.delete(name_list=dpm.injections.get_object_names())
    for name,state in fixture['original_injections'].items():
        dpm.injections.create(name=name);dpm.injections[name].set_state(state)
    dpm.general_settings.interaction.enabled=False
    return {'fixture':fixture,'records':records,'inherited_injections_restored':dpm.injections.get_state()}

def qualify(s,work,out,start_data):
    """Bounded screen with early rejection of unphysical film transport."""
    s.settings.file.read_data(file_name=str(start_data))
    s.tui.define.models.eulerian_wallfilm.solve_wallfilm_equation('yes')
    configure_autosave(s,str(work/'qualification'),data_frequency=1000)
    paths=instrument(s,work/'qualification'/'monitors')
    result={'status':'RUNNING','blocks':[],'native_start':13686,'planned_iterations':1000,
      'block_size':200,'reason_for_short_blocks':'screen for previously observed explosive EWF instability',
      'before':snapshot(s),'film_parameters':dict(s.rp_vars('wall-film/model-parameters'))}
    dump(out/'qualification.json',result)
    for block in range(1,6):
        s.tui.solve.iterate(200)
        h={n:file_history(p) for n,p in paths.items()}
        coordinate=h['p72-contact-inventory']['iterations'][-1]
        stats={n:{'last':v['values'][-1],'max':max(v['values'][-200:])} for n,v in h.items()}
        receipt={'native_iteration':coordinate,'after':snapshot(s),'stats':stats,
          'pair':save_pair(s,work/'qualification'/f'block{block}-N{coordinate}.cas.h5',coordinate)}
        result['blocks'].append(receipt)
        dump(out/'qualification-histories.json',h)
        dump(out/'qualification.json',result)
        print('CONTACT_QUALIFICATION_CHECKPOINT',coordinate,stats['p72-contact-alpha-max'],
              stats['p72a-e2.7-ewf-thickness-max'],stats['p72a-e2.7-ewf-courant-max'],flush=True)
        if stats['p72a-e2.7-ewf-courant-max']['max']>1 or stats['p72a-e2.7-ewf-thickness-max']['max']>0.01:
            result['status']='REJECTED_EWF_INSTABILITY';break
    else: result['status']='COMPLETE_NUMERICAL_SCREEN_NOT_CONVERGENCE_CLAIM'
    result['actual_iterations']=result['blocks'][-1]['native_iteration']-13686
    result['final_pair']=result['blocks'][-1]['pair']
    dump(out/'qualification.json',result)
    return result

def run_remote_prepared_blocks(s,work,out,tag,native_start,count=6000,block_size=1000):
    """Continue an already verified remote parent; never attach, launch or exit."""
    import sys
    from pathlib import PureWindowsPath
    from pyansys_fluent.stage4_native import ensure_remote_directory
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'inspection'))
    from extract_report_plot_histories import parse_report_forms,read_remote_forms
    from run_phase72a_e27_server1_continuation import pair_save,native_iteration
    work=PureWindowsPath(work)
    folder=work/'monitors'
    ensure_remote_directory(s,str(folder))
    configure_autosave(s,str(work),data_frequency=1000)
    files=s.settings.solution.monitor.report_files
    paths={}
    for name in files.get_object_names():
        obj=files[name]
        defs=obj.report_defs()
        if len(defs)!=1 or defs[0] in paths:
            raise RuntimeError(f'Ambiguous remote report: {name}')
        report=defs[0]
        path=str(folder/f'{report}.out')
        from pyansys_fluent.common import remote_file_exists
        if remote_file_exists(s,path):
            raise FileExistsError(path)
        obj.file_name=path
        obj.frequency_of='iteration';obj.frequency=1;obj.active=True
        paths[report]=path
    result={'status':'RUNNING','native_start':native_start,'planned_iterations':count,
      'block_size':block_size,'execution':'attach_only_remote','report_paths':paths,
      'before':snapshot(s),'blocks':[],
      'source_hooks':s.settings.setup.cell_zone_conditions.fluid[LOWER_ZONE].get_state(),
      'methods':s.settings.solution.methods.get_state(),
      'controls':s.settings.solution.controls.get_state(),
      'film_parameters':dict(s.rp_vars('wall-film/model-parameters'))}
    dump(out/f'{tag}.json',result)
    completed=0
    while completed<count:
        steps=min(block_size,count-completed)
        s.settings.solution.run_calculation.iterate(iter_count=steps)
        current=native_iteration(s)
        if current!=native_start+completed+steps:
            raise RuntimeError(f'Remote continuation stopped at {current}')
        pair=pair_save(s,work/f'block-N{current}.cas.h5',work,
                       scratch_tag=f'checkpoint-{current}')
        h={name:parse_report_forms(read_remote_forms(s,path)) for name,path in paths.items()}
        expected=list(range(native_start,current+1))
        if any(v['iterations']!=expected for v in h.values()):
            raise RuntimeError('Remote histories do not cover the exact native window')
        if any(not math.isfinite(v) for hist in h.values() for v in hist['values']):
            raise RuntimeError('Nonfinite remote report evidence')
        stats={n:{'last':v['values'][-1],'max':max(v['values'][-steps:])} for n,v in h.items()}
        result['blocks'].append({'native_iteration':current,'after':snapshot(s),
                                'stats':stats,'pair':pair})
        completed+=steps
        result['actual_iterations']=completed
        dump(out/f'{tag}-histories.json',h);dump(out/f'{tag}.json',result)
        print('CONTACT_REMOTE_CHECKPOINT',current,
              stats['p72a-e2.7-ewf-film-mass-total'],
              stats['p72a-e2.7-ewf-thickness-max'],
              stats['p72a-e2.7-ewf-courant-max'],flush=True)
    result.update(status='COMPLETE_CONTINUATION_STEADY_ASSESSMENT_PENDING',
                  final_pair=result['blocks'][-1]['pair'])
    dump(out/f'{tag}.json',result)
    return result

def recover_qualification(s,work,out):
    result=json.loads((out/'qualification.json').read_text())
    assert not result['blocks']
    configure_autosave(s,str(work/'qualification'),data_frequency=1000)
    files=s.settings.solution.monitor.report_files
    paths={files[n].report_defs()[0]:work/'qualification'/'monitors'/f'{files[n].report_defs()[0]}.out' for n in files.get_object_names()}
    current=file_history(paths['p72-contact-inventory'])['iterations'][-1]
    if 'interruption' not in result:
        result['interruption']={'native_iteration':current,'cause':'Inherited autosave directory from remote parent does not exist locally',
          'preserved_pair':save_pair(s,work/'qualification'/f'path-interruption-N{current}.cas.h5',current)}
    dump(out/'qualification.json',result)
    for block,target in enumerate(range(13886,14687,200),1):
        s.settings.solution.run_calculation.iterate(iter_count=target-current)
        h={n:file_history(p) for n,p in paths.items()}
        current=h['p72-contact-inventory']['iterations'][-1]
        if current!=target: raise RuntimeError(f'Qualification stopped at {current}, expected {target}')
        stats={n:{'last':v['values'][-1],'max':max(v['values'][-200:])} for n,v in h.items()}
        receipt={'native_iteration':current,'after':snapshot(s),'stats':stats,
          'pair':save_pair(s,work/'qualification'/f'block{block}-N{current}.cas.h5',current)}
        result['blocks'].append(receipt)
        dump(out/'qualification-histories.json',h);dump(out/'qualification.json',result)
        print('CONTACT_QUALIFICATION_CHECKPOINT',current,stats['p72-contact-alpha-max'],
              stats['p72a-e2.7-ewf-thickness-max'],stats['p72a-e2.7-ewf-courant-max'],flush=True)
        if stats['p72a-e2.7-ewf-courant-max']['max']>1 or stats['p72a-e2.7-ewf-thickness-max']['max']>0.01:
            result['status']='REJECTED_EWF_INSTABILITY';break
    else: result['status']='COMPLETE_NUMERICAL_SCREEN_NOT_CONVERGENCE_CLAIM'
    result['actual_iterations']=current-13686;result['final_pair']=result['blocks'][-1]['pair']
    dump(out/'qualification.json',result)
    return result

def run_prepared_blocks(s,work,out,tag,native_start,count=1000,block_size=200,native_tui=False,
                        initial_block_size=None,stop_on_film_instability=True):
    """Run a caller-prepared, verified child; preserve numerical failures too."""
    configure_autosave(s,str(work/tag),data_frequency=1000)
    paths=instrument(s,work/tag/'monitors')
    result={'status':'RUNNING','native_start':native_start,'planned_iterations':count,
      'block_size':block_size,'native_tui':native_tui,
      'initial_block_size':initial_block_size,'stop_on_film_instability':stop_on_film_instability,
      'before':snapshot(s),'blocks':[],
      'source_hooks':s.settings.setup.cell_zone_conditions.fluid[LOWER_ZONE].get_state(),
      'methods':s.settings.solution.methods.get_state(),
      'controls':s.settings.solution.controls.get_state(),
      'film_parameters':dict(s.rp_vars('wall-film/model-parameters'))}
    dump(out/f'{tag}.json',result)
    completed=0
    while completed<count:
        steps=min(initial_block_size if completed==0 and initial_block_size else
                  block_size-completed%block_size,count-completed)
        if native_tui:
            s.tui.solve.iterate(steps)
        else:
            s.settings.solution.run_calculation.iterate(iter_count=steps)
        h={n:file_history(p) for n,p in paths.items()}
        current=h['p72-contact-inventory']['iterations'][-1]
        if current!=native_start+completed+steps:
            raise RuntimeError(f'Prepared trial stopped at {current}')
        stats={n:{'last':v['values'][-1],'max':max(v['values'][-steps:])} for n,v in h.items()}
        result['blocks'].append({'native_iteration':current,'after':snapshot(s),'stats':stats,
          'pair':save_pair(s,work/tag/f'block-N{current}.cas.h5',current)})
        completed+=steps
        dump(out/f'{tag}-histories.json',h);dump(out/f'{tag}.json',result)
        print('CONTACT_PREPARED_CHECKPOINT',tag,current,stats['p72-contact-alpha-max'],
              stats['p72a-e2.7-ewf-thickness-max'],stats['p72a-e2.7-ewf-courant-max'],flush=True)
        if (stop_on_film_instability and
            (stats['p72a-e2.7-ewf-courant-max']['max']>1 or stats['p72a-e2.7-ewf-thickness-max']['max']>0.01)):
            result['status']='REJECTED_EWF_INSTABILITY';break
    else: result['status']='COMPLETE_NUMERICAL_SCREEN_NOT_CONVERGENCE_CLAIM'
    result['actual_iterations']=completed;result['final_pair']=result['blocks'][-1]['pair']
    dump(out/f'{tag}.json',result)
    return result
