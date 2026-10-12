"""Refine only native Fluent visual settings; preserve every candidate PNG."""
import argparse, json, time
from pathlib import Path
from export_phase10_slit154k_reference import attach, run, OUT, FIG, dump, identity, fetch

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args()
    receipt = json.loads((OUT/'figure-export.json').read_text())
    assert receipt['status'] == 'NATIVE_EXPORTS_COMPLETE'
    s = attach();before = identity(s);g = s.settings.results.graphics
    stamp = str(time.time_ns());folder = run.WORK/('phase10-spatial-refinement-'+stamp)
    run.ensure_remote_directory(s,str(folder/'scratch'))
    record = {'status':'REFINING','new_solve_calls':0,'before':before,'figures':[]}
    for figure in receipt['figures'][:1] if args.preview else receipt['figures']:
        f = dict(figure)
        obj = (g.contour if f['kind']=='contour' else g.vector)[f['object_name']]
        title = {'phase-2-vof':'Liquid VF [-]', 'turb-kinetic-energy':'k [m^2/s^2]',
                 'velocity-magnitude':'Speed [m/s]'}[f['field']]
        obj.color_map.set_state({'visible':True,'font_automatic':False,'font_size':28.,
                                 'show_all':False,'user_skip':10,'length':.50,'width':4.,
                                 'title_elements':'Variable Name'})
        if f['kind']=='vector':
            obj.options.scale = .025
            mesh_name = 'p10-slit154k-outline-'+f['name']
            if mesh_name not in g.mesh.get_object_names():g.mesh.create(name=mesh_name)
            mesh = g.mesh[mesh_name]
            mesh.surfaces_list = [f['surface'],'verticalslit-wall-vertical-slit']
            mesh.options.set_state({'nodes':False,'faces':False,'edges':True})
            assert 'outline' in mesh.edge_type_options.edge_type.allowed_values()
            mesh.edge_type_options.edge_type = 'outline'
            mesh.coloring_options.option = 'uniform'
            mesh.coloring_options.faces = '#303030'
            if 'edges' in mesh.coloring_options.child_names:mesh.coloring_options.edges = 'black'
            scene_name = 'p10-slit154k-scene-'+f['name']
            scenes = s.settings.results.scene
            if scene_name not in scenes.get_object_names():scenes.create(name=scene_name)
            scene = scenes[scene_name]
            for name in [f['object_name'],mesh_name]:
                if name not in scene.graphics_objects.get_object_names():scene.graphics_objects.add(name=name)
            assert set(scene.graphics_objects.get_object_names()) == {f['object_name'],mesh_name}
            f['scene_readback'] = scene.get_state()
            f['outline_readback'] = mesh.get_state()
            f['scene_name'] = scene_name
            scene.display()
        else:obj.display()
        c=dict(f['camera'])
        if f['name'].startswith('topdown'):
            c.update(target=[-.6,c['target'][1],-.2],position=[-.6,c['position'][1],-.2],width=4.4,height=3.3)
        f['camera']=c
        camera=g.views.camera
        camera.projection(type='orthographic')
        camera.position(xyz=c['position']);camera.target(xyz=c['target']);camera.up_vector(xyz=c['up'])
        camera.field(width=c['width'],height=c['height'])
        g.picture.landscape = c['resolution'][0] > c['resolution'][1]
        g.picture.x_resolution,g.picture.y_resolution = c['resolution']
        remote=str(folder/(f['name']+'-readable.png'))
        g.picture.save_picture(file_name=remote)
        target=FIG/(f['name']+'-readable-'+stamp+'.png')
        f.update(remote=remote,local=str(target),graphics_readback=obj.get_state(),visual_qa='PENDING')
        f.update(fetch(s,remote,target,str(folder/'scratch'/(f['name']+'-hash.txt'))))
        record['figures'].append(f)
        dump('refinement-'+stamp+'.json',record)
        print('REFINED',f['name'],target,flush=True)
    assert identity(s)==before
    record['status']='NATIVE_REFINEMENT_COMPLETE'
    record['scientific_state_unchanged']=True
    dump('refinement-'+stamp+'.json',record)
    dump('latest-refinement.json',record)

if __name__=='__main__':main()
