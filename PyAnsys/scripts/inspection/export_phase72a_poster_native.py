"""Native Fluent poster graphics, restricted to user-authorized Server 6.

Preserve its loaded endpoint before loading the immutable archived N45606 pair.
No initialization, iteration, model change or solver exit is permitted here.
"""
from pathlib import Path, PureWindowsPath
import argparse
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts/setup'), str(ROOT/'scripts/inspection')]
from phase9_server6_997k_common import attach, run
from pyansys_fluent.stage4_native import ensure_remote_directory
from run_phase72a_e27_server1_continuation import pair_save, native_iteration
from run_phase72a_stage4_analytical import checked_remote_sha256
from export_phase72a_stage4_spatial import short_system, fetch_png

OUT = ROOT/'output/poster-N45606-native/20261010'
ARCHIVE_RECEIPT = ROOT/'output/phase72a-adaptive-server1/20261005/recovered-N45606/endpoint.json'


def dump(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_text(json.dumps(value, indent=2, default=str)+'\n')


def state(s):
    reports = s.settings.solution.report_definitions
    fields = reports.compute(report_defs=['v2-total-liquid-mass', 'p72a-e2.7-ewf-film-mass-total',
                                          'p72a-e2.7-ewf-thickness-max'])
    return {'native_iteration':native_iteration(s), 'film_clock':run.film(s),
            'fields':fields, 'fluid_zones':s.settings.setup.cell_zone_conditions.fluid.get_object_names()}


def prepare(s):
    if (OUT/'prepared.json').exists():
        raise RuntimeError('Preparation already recorded. Inspect existing receipt before another case load.')
    assert not s.settings.solution.run_calculation.iterating()
    before = state(s)
    folder = PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")'))/'Documents/FluentRuns/Poster-N45606/20261010'
    ensure_remote_directory(s,str(folder/'scratch'))
    # Check only the controller that owns this endpoint. Do not touch any other
    # Fluent or Python process. The failed controller must have exited first.
    process_path = str(folder/'controller-preflight.json')
    q = lambda p: "'"+str(p).replace("'","''")+"'"
    run.base.powershell(s,"$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -like '*Phase9-Server6-997k*' -and ($_.CommandLine -like '*run_phase9_server6_997k_ewf*' -or $_.CommandLine -like '*run_and_handoff*')}); [IO.File]::WriteAllText("+q(process_path)+",(@{controller_count=$p.Count;process_ids=@($p.ProcessId)}|ConvertTo-Json),[Text.Encoding]::ASCII)")
    processes=json.loads(run.read_text(s,process_path))
    assert processes['controller_count']==0, 'A Server 6 controller remains active; reconcile it before replacing the case.'
    if (OUT/'previous-endpoint.json').exists():
        previous=json.loads((OUT/'previous-endpoint.json').read_text())
        preserved=previous['preserved_pair']
        assert before['native_iteration']==preserved['native_iteration']
        assert before['fields']==previous['previous_state']['fields']
    else:
        preserved=pair_save(s,folder/f'preserved-before-poster-N{before["native_iteration"]}.cas.h5',folder/'scratch',scratch_tag='preserve')
        previous={'server_id':'6','previous_state':before,'preserved_pair':preserved,'controller_preflight':processes}
        dump('previous-endpoint.json',previous)
    # Saving synchronizes cached EWF RP clocks after the earlier interrupted
    # solve. Verify the preserved data directly; do not mistake that cache
    # refresh for another solve or overwrite the already preserved pair.
    s.settings.file.read_data(file_name=preserved['data'])
    canonical=state(s)
    assert canonical['native_iteration']==preserved['native_iteration']
    assert canonical['fields']==previous['previous_state']['fields']
    previous['saved_reopened_state']=canonical
    previous['clock_cache_refreshed_on_save']=canonical['film_clock']!=previous['previous_state']['film_clock']
    dump('previous-endpoint.json',previous)
    source=run.SHARED/'P4P-Fluent-Artifacts/Phase72A/ContactAbsorber/adaptive-20261005/N45606'
    expected=json.loads(ARCHIVE_RECEIPT.read_text())['pair']
    local={}
    for key,ext in [('case','cas'),('data','dat')]:
        shared=str(source/f'adaptive-recovered-N45606.{ext}.h5')
        assert run.remote_file_exists(s,shared), shared
        target=str(folder/f'input-N45606.{ext}.h5')
        assert not run.remote_file_exists(s,target), target
        short_system(s,f'cmd /c copy /b "{shared}" "{target}"')
        digest=checked_remote_sha256(s,target,str(folder/'scratch'/f'input-{key}.sha256.txt'))
        assert digest==expected[key+'_sha256']
        local[key]=target
        local[key+'_sha256']=digest
    # Two explicitly matched members. Loading saved data, without initializing
    # or running, preserves the source solution and its elapsed film time.
    s.settings.file.read_case(file_name=local['case'])
    s.settings.file.read_data(file_name=local['data'])
    after=state(s)
    assert after['native_iteration']==45606
    receipt={'server_id':'6','version':s.scheme.eval('(cx-version)'), 'remote_root':str(folder),
             'source_pair':local,'previous_endpoint_receipt':str(OUT/'previous-endpoint.json'),
             'source_readback':after,'solve_issued':False,
             'review':'Server 6 only; idle and controller-free preflight; unique preservation pair; source hashes match archive; explicit case then data read; no initialization, solve, model setter or exit.'}
    dump('prepared.json',receipt)
    print('N45606_PREPARED',json.dumps(after),flush=True)


def inspect(s):
    assert not s.settings.solution.run_calculation.iterating()
    assert native_iteration(s)==45606
    g=s.settings.results.graphics
    result={'state':state(s),'graphics_children':g.child_names,'surfaces':s.fields._field_info._get_surfaces_info(),
            'picture':g.picture.get_state(),'windows':g.windows.get_state(),'colors':g.colors.get_state(),
            'lighting':g.lighting.get_state(),'view_children':g.views.child_names}
    # Create only isolated graphics objects to read live defaults and options.
    for kind in ['mesh','contour','pathline']:
        objects=getattr(g,kind)
        name='Poster-'+kind
        if name not in objects.get_object_names():objects.create(name=name)
        obj=objects[name]
        result[kind]={'state':obj.get_state(),'children':obj.child_names}
        for key in ['field','velocity_domain','color_by','phase','style','surfaces_list','release_from_surfaces','coloring']:
            if key in obj.child_names:
                item=getattr(obj,key)
                if hasattr(item,'allowed_values'):
                    result[kind][key+'_allowed']=item.allowed_values()
    scene=s.settings.results.scene
    name='Poster-composite'
    if name not in scene.get_object_names():scene.create(name=name)
    result['scene']={'state':scene[name].get_state(),'children':scene[name].child_names}
    dump('graphics-inspection.json',result)
    summary={k:v for k,v in result.items() if k not in ['surfaces','windows','colors']}
    for kind in ['contour','pathline']:
        values=summary[kind].get('field_allowed',[])
        summary[kind]['field_allowed']=[v for v in values if 'velocity' in v or 'film-thickness' in v]
    print(json.dumps(summary,indent=2,default=str),flush=True)


def configure(s):
    before=state(s)
    assert before['native_iteration']==45606
    assert not s.settings.solution.run_calculation.iterating()
    g=s.settings.results.graphics
    clips=s.settings.results.surfaces.iso_clip
    name='poster-rear-film'
    if name not in clips.get_object_names():clips.create(name=name)
    clips[name].set_state({'field':'z-coordinate','surfaces':['wall','wall:004'],
                          'range':{'minimum':-2.0,'maximum':0.0}})
    wet='poster-wet-film'
    if wet not in clips.get_object_names():clips.create(name=wet)
    assert 'film-thickness' in clips[wet].field.allowed_values()
    clips[wet].set_state({'field':'film-thickness','surfaces':['poster-rear-film'],
                         'range':{'minimum':1e-8,'maximum':0.00031}})
    front='poster-front-shell'
    if front not in clips.get_object_names():clips.create(name=front)
    clips[front].set_state({'field':'z-coordinate','surfaces':['wall'],
                           'range':{'minimum':0.001,'maximum':2.0}})
    meshes={
        'Poster-shell':(['poster-front-shell'],'light gray',True),
        'Poster-absorber':(['bottom'],'orange',True),
        'Poster-film-surface':(['poster-wet-film'],'pastel cyan',True),
        'Poster-absorber-full':(['wall:004','bottom','separator-purnanto:1:001',
                                  'interior--separator-purnanto:007','interior--separator-purnanto:010'],'orange',True),
        'Poster-steam-inlet':(['steaminlet'],'pastel cyan',True),
        'Poster-liquid-inlet':(['liquidinlet'],'orange',True)}
    for name,(surfaces,color,faces) in meshes.items():
        if name not in g.mesh.get_object_names():g.mesh.create(name=name)
        obj=g.mesh[name]
        obj.surfaces_list=surfaces
        obj.options.set_state({'faces':faces,'edges':False,'nodes':False})
        if obj.edge_type_options.is_active():
            assert 'outline' in obj.edge_type_options.edge_type.allowed_values()
            obj.edge_type_options.edge_type='outline'
        obj.coloring_options.option='uniform'
        obj.coloring_options.faces=color
        obj.annotations_list=[]
    film=g.contour['Poster-contour']
    film.set_state({'field':'film-thickness','surfaces_list':['poster-wet-film'],
                    'range_options':{'global_range':False,'auto_range':False,'clip_to_range':False,
                                     'minimum':0.0,'maximum':0.00031},
                    'options':{'filled':True,'node_values':True,'boundary_values':True,'contour_lines':False},
                    'colorings':{'banded':False,'smooth':True},
                    'color_map':{'visible':False,'color':'blue-light'},'annotations_list':[]})
    flow=g.pathline['Poster-pathline']
    flow.set_state({'velocity_domain':'phase-1','field':'phase-1-velocity-magnitude',
                    'release_from_surfaces':['steaminlet'],
                    'range_options':{'auto_range':False,'minimum':0.0,'maximum':65.0},
                    'style_attributes':{'style':'line','line_width':2},
                    'option':{'oil_flow':False,'reverse':False,'relative':False,'node_values':True,
                              'accuracy_controls':True,'tolerance':0.001,'step':2000,'skip':160,'coarsen':1},
                    'color_map':{'visible':False,'color':'sequential-inferno'},'annotations_list':[]})
    g.colors.graphics_color_theme='white'
    g.colors.titles.set_state({key:'' for key in ['left_top','left_bottom','right_top','right_middle','right_bottom']})
    g.windows.logo=False
    g.windows.axes.visible=False
    g.windows.scale.visible=False
    g.windows.text.visible=False
    g.windows.ruler=False
    g.views.rendering_options.show_colormap=False
    g.picture.use_window_resolution=False
    g.picture.invert_background=False
    g.picture.driver_options.hardcopy_format='png'
    g.picture.landscape=False
    g.views.rendering_options.line_weight=1
    states=g.views.display_states
    display_name='poster-clean'
    if display_name not in states.get_object_names():states.create(name=display_name)
    states[display_name].set_state({'axes':'disable','ruler':'disable','title':'disable',
                                   'boundary_marker':'disable','anti_aliasing':'enable',
                                   'reflections':'disable','static_shadows':'disable','dynamic_shadows':'disable',
                                   'grid_plane':'disable','headlights':'on','lighting':'gouraud'})
    for name in meshes:g.mesh[name].display_state_name=display_name
    film.display_state_name=display_name
    flow.display_state_name=display_name
    components={'geometry':['Poster-shell'],'film':['Poster-film-surface'],
                'flow':['Poster-pathline'],'absorber':['Poster-absorber'],
                'inlets':['Poster-steam-inlet','Poster-liquid-inlet']}
    composite=sum(components.values(),[])
    variants={**components,'composite':composite,'film-thickness':['Poster-contour'],
              'absorber-full':['Poster-absorber-full'],
              'quantitative-composite':[name if name!='Poster-film-surface' else 'Poster-contour' for name in composite]}
    for key,names in variants.items():
        scene_name='Poster-'+key+'-scene'
        scenes=s.settings.results.scene
        if scene_name not in scenes.get_object_names():scenes.create(name=scene_name)
        scene=scenes[scene_name]
        scene.display_state_name=display_name
        # Replace only our isolated scene's members when the visual selection
        # changes. These are display objects, never solver entities.
        obsolete=[name for name in scene.graphics_objects.get_object_names() if name not in names]
        if obsolete:scene.graphics_objects.delete(name_list=obsolete)
        for name in names:
            if name not in scene.graphics_objects.get_object_names():scene.graphics_objects.add(name=name)
            obj=scene.graphics_objects[name]
            if obj.transparency.is_active():
                obj.transparency=(95 if name=='Poster-shell' else
                                  40 if name in ['Poster-contour','Poster-film-surface'] else 0)
        assert set(scene.graphics_objects.get_object_names())==set(names)
    assert state(s)==before
    result={'components':components,'variants':variants,'state_before':before,'state_after':state(s),
            'film':film.get_state(),'pathline':{k:v for k,v in flow.get_state().items() if k not in ['curves','axes']},
            'meshes':{name:g.mesh[name].get_state() for name in meshes},
            'film_cutaway':clips['poster-rear-film'].get_state(),
            'film_threshold':clips['poster-wet-film'].get_state(),
            'shell_cutaway':clips['poster-front-shell'].get_state(),
            'display_state':states[display_name].get_state(),
            'centre_film_style':'Uniform pastel-cyan native wet-wall surface; quantitative thickness contour exported separately',
            'centre_absorber_style':'Native bottom boundary shown as absorber footprint; full cell-zone exterior exported separately',
            'review':'Graphics/surfaces only; primary steam phase-1 pathline domain explicitly selected; no model or solve change; scene transparency read back.'}
    dump('configured.json',result)
    print('NATIVE_GRAPHICS_CONFIGURED',flush=True)


def export(s,preview):
    before=state(s)
    assert before['native_iteration']==45606
    config=json.loads((OUT/'configured.json').read_text())
    prepared=json.loads((OUT/'prepared.json').read_text())
    stamp=str(time.time_ns())
    folder=PureWindowsPath(prepared['remote_root'])/('graphics-'+stamp)
    ensure_remote_directory(s,str(folder))
    local=OUT/('preview-'+stamp if preview else 'native-'+stamp)
    local.mkdir()
    g=s.settings.results.graphics
    camera={'position':[-5.0,5.0,12.0],'target':[-0.45,3.45,-0.05],
            'up':[0,1,0],'width':4.8,'height':8.0}
    resolution=[1080,1800] if preview else [2400,4000]
    g.picture.x_resolution,g.picture.y_resolution=resolution
    jobs=['geometry','film','flow','absorber','inlets','film-thickness','absorber-full','quantitative-composite','composite']
    if preview:jobs=['composite']
    receipt={'server_id':'6','source_pair':prepared['source_pair'],'state_before':before,
             'camera':camera,'resolution':resolution,'figures':[],
             'renderer':'FLUENT_2025_R2_NATIVE_SCENE_AND_SAVE_PICTURE','solve_issued':False}
    jobs_and_backgrounds=[(job,'white') for job in jobs]
    if not preview:
        jobs_and_backgrounds += [(job,'black') for job in ['geometry','film','flow','absorber','inlets','composite']]
    for job,background in jobs_and_backgrounds:
        g.colors.graphics_color_theme=background
        scene=s.settings.results.scene['Poster-'+job+'-scene']
        scene.display()
        c=g.views.camera
        c.projection(type='orthographic')
        c.position(xyz=camera['position']);c.target(xyz=camera['target']);c.up_vector(xyz=camera['up'])
        c.field(width=camera['width'],height=camera['height'])
        target=local/(f'native-{job}.png' if background=='white' else f'native-{job}-black.png')
        remote=str(folder/target.name)
        g.picture.save_picture(file_name=remote)
        identity=fetch_png(s,remote,target)
        assert identity['resolution']==resolution
        receipt['figures'].append({'component':job,'background':background,'local':str(target),'remote':remote,
                                  'scene':scene.get_state(),**identity})
        dump('latest-export.json',receipt)
        print('NATIVE_FIGURE',job,background,str(target),flush=True)
    if not preview:
        # Actual inlet faces, viewed normal to their plane. The 6.75 mm liquid
        # strip is too narrow to distinguish reliably in the complete vessel.
        g.colors.graphics_color_theme='white'
        inlet_camera={'position':[-6.0,2.066,-1.1075],
                      'target':[-2.06703442,2.066,-1.1075],
                      'up':[0,1,0],'width':0.85,'height':0.85}
        scene=s.settings.results.scene['Poster-inlets-scene']
        scene.display()
        c=g.views.camera
        c.projection(type='orthographic')
        c.position(xyz=inlet_camera['position']);c.target(xyz=inlet_camera['target']);c.up_vector(xyz=inlet_camera['up'])
        c.field(width=inlet_camera['width'],height=inlet_camera['height'])
        g.picture.x_resolution,g.picture.y_resolution=[1600,1600]
        target=local/'native-inlet-detail.png'
        remote=str(folder/target.name)
        g.picture.save_picture(file_name=remote)
        identity=fetch_png(s,remote,target)
        assert identity['resolution']==[1600,1600]
        receipt['figures'].append({'component':'inlet-detail','background':'white',
                                  'camera':inlet_camera,'local':str(target),'remote':remote,**identity})
        dump('latest-export.json',receipt)
        print('NATIVE_FIGURE inlet-detail white',str(target),flush=True)
        g.picture.x_resolution,g.picture.y_resolution=resolution
    g.colors.graphics_color_theme='white'
    s.settings.results.scene['Poster-composite-scene'].display()
    assert state(s)==before
    receipt.update(status='EXPORTED',scientific_state_unchanged=True,state_after=state(s))
    dump('latest-export.json',receipt)
    (local/'export-receipt.json').write_text(json.dumps(receipt,indent=2,default=str)+'\n')


def preserve_graphics(s):
    before=state(s)
    prepared=json.loads((OUT/'prepared.json').read_text())
    folder=PureWindowsPath(prepared['remote_root'])
    g=s.settings.results.graphics
    g.colors.graphics_color_theme='white'
    s.settings.results.scene['Poster-composite-scene'].display()
    camera=json.loads((OUT/'latest-export.json').read_text())['camera']
    c=g.views.camera
    c.projection(type='orthographic')
    c.position(xyz=camera['position']);c.target(xyz=camera['target']);c.up_vector(xyz=camera['up'])
    c.field(width=camera['width'],height=camera['height'])
    # Fluent normalizes saved view names to lowercase when a case is reopened.
    view_name='poster-n45606-camera'
    if view_name not in g.views.display_states['poster-clean'].view_name.allowed_values():
        g.views.save_view(view_name=view_name)
    assert view_name in g.views.display_states['poster-clean'].view_name.allowed_values()
    g.views.display_states['poster-clean'].view_name=view_name
    pair=pair_save(s,folder/f'poster-graphics-N45606-{time.time_ns()}.cas.h5',folder/'scratch',scratch_tag='poster-graphics')
    dump('saved-graphics-pending.json',{'pair':pair,'state_before':before,
                                      'graphics_reopen_verified':False,'server_id':'6','solve_issued':False})
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    assert state(s)==before
    scene=s.settings.results.scene['Poster-composite-scene']
    assert set(scene.graphics_objects.get_object_names())==set(json.loads((OUT/'configured.json').read_text())['variants']['composite'])
    clean=s.settings.results.graphics.views.display_states['poster-clean'].get_state()
    assert all(clean[k]=='disable' for k in ['axes','title','reflections','static_shadows','dynamic_shadows','grid_plane'])
    scene.display()
    assert clean['view_name']==view_name
    dump('saved-graphics.json',{'pair':pair,'state_before':before,'state_after':state(s),
                               'graphics_reopen_verified':True,'display_state':clean,'server_id':'6','solve_issued':False})
    print('POSTER_GRAPHICS_SAVED_REOPENED',pair['case'],flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['prepare','inspect','configure','preview','export','save'])
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    s=attach()
    if args.stage=='prepare':prepare(s)
    elif args.stage=='inspect':inspect(s)
    elif args.stage=='configure':configure(s)
    elif args.stage=='save':preserve_graphics(s)
    else:export(s,args.stage=='preview')


if __name__=='__main__':main()
