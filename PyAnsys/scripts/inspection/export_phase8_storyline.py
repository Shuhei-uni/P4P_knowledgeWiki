"""Native Fluent exports from the verified Phase 8 storyline catalog; no solve."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import traceback

ROOT=Path(__file__).resolve().parents[3]
VERTICAL="story-vertical"
INLET="story-inlet"
INLET_Y=2.065999984741211  # midpoint of live steaminlet y bounds

def dump(out,name,data):
    (out/name).write_text(json.dumps(data,indent=2,default=str)+"\n",encoding="utf-8")

def prepare(solver,entry):
    solver.settings.file.read_case(file_name=entry["pair"]["case"])
    solver.settings.file.read_data(file_name=entry["pair"]["data"])
    p=solver.settings.results.surfaces.plane_surface
    for name,state in [(VERTICAL,{"method":"xy-plane","z":0.}),
                       (INLET,{"method":"zx-plane","y":INLET_Y})]:
        if name not in p.get_object_names():p.create(name=name)
        p[name].set_state(state)
    g=solver.settings.results.graphics
    for group,name in [(g.contour,"story-scalar"),(g.vector,"story-vector")]:
        if name not in group.get_object_names():group.create(name=name)
    return g

def scan(solver,out):
    catalog=json.loads((out/"catalog.json").read_text())
    receipt={"status":"SCANNING","version":str(solver.get_fluent_version()),"solve_issued":False,"cases":{},
             "surfaces":{"vertical":{"method":"xy-plane","z_m":0},"inlet":{"method":"zx-plane","y_m":INLET_Y}},
             "geometry_source":"geometry-probe.json: live surface coordinate bounds; vertical axis y"}
    if (out/"range-receipt.json").exists():receipt=json.loads((out/"range-receipt.json").read_text())
    locked_display_ranges=receipt.get("display_ranges")
    ranges={"velocity-magnitude":[],"pressure":[]}
    for previous in receipt["cases"].values():
        for name,state in previous["observed"].items():
            field=name.split("/")[0]
            if field in ranges:ranges[field].extend([state["minimum"],state["maximum"]])
    for entry in catalog:
        if entry["role"]=="particle-views":continue
        if entry["id"] in receipt["cases"]:continue
        g=prepare(solver,entry);c=g.contour["story-scalar"]
        record={"source":entry,"observed":{}}
        for field,surfaces in [("phase-2-vof",[VERTICAL]),("velocity-magnitude",[VERTICAL,INLET]),("pressure",[VERTICAL])]:
            for surface in surfaces:
                c.set_state({"field":field,"surfaces_list":[surface],"range_options":{"global_range":False,"auto_range":True},"options":{"boundary_values":False}})
                c.range_options.compute();state=c.range_options.get_state()
                record["observed"][field+"/"+surface]=state
                if field in ranges:ranges[field].extend([state["minimum"],state["maximum"]])
        if entry["family"]=="F4":
            record["film_fields"]=[f for f in c.field.allowed_values() if "film" in f or "ewf" in f]
            record["vector_fields"]=g.vector["story-vector"].vector_field.allowed_values()
        receipt["cases"][entry["id"]]=record
        dump(out,"range-receipt.json",receipt)
        print("Scanned "+entry["id"],flush=True)
    if locked_display_ranges:
        receipt["display_ranges"]=locked_display_ranges
        receipt["display_range_policy"]="Retain the previously verified common ranges so new matched SIMPLE views compare directly with existing Coupled views."
    else:
        receipt["display_ranges"]={"phase-2-vof":[0.,1.],
                                   "velocity-magnitude":[0.,math.ceil(max(ranges["velocity-magnitude"])/10)*10.],
                                   "pressure":[math.floor(min(ranges["pressure"])/10000)*10000.,math.ceil(max(ranges["pressure"])/10000)*10000.]}
    receipt["status"]="RANGES_VERIFIED"
    dump(out,"range-receipt.json",receipt)

def camera(g,horizontal=False,wall=False):
    ds=g.views.display_states
    if "story-clean" not in ds.get_object_names():ds.create(name="story-clean")
    ds.use_active(state_name="story-clean")
    ds["story-clean"].set_state({"reflections":"disable","static_shadows":"disable","dynamic_shadows":"disable","grid_plane":"disable"})
    ds.apply(state_name="story-clean")
    c=g.views.camera
    if horizontal:
        target=[-.85,INLET_Y,-.2];position=[-.85,INLET_Y+10,-.2];up=[0,0,-1];field=[4.8,3.6];landscape=True
    elif wall:
        target=[0,3.495,0];position=[8,4.5,10];up=[0,1,0];field=[5.5,8.0];landscape=False
    else:
        target=[0,3.495,0];position=[0,3.495,10];up=[0,1,0];field=[4.8,7.6];landscape=False
    c.projection(type="orthographic");c.target(xyz=target);c.position(xyz=position);c.up_vector(xyz=up)
    g.views.auto_scale();c.field(width=field[0],height=field[1])
    g.picture.use_window_resolution=False;g.picture.landscape=landscape
    g.picture.x_resolution=2400 if landscape else 1800;g.picture.y_resolution=1800 if landscape else 2400
    return {"target":target,"position":position,"up":up,"projection":"orthographic","field":field}

def picture(g,path,state,cam):
    path.parent.mkdir(parents=True,exist_ok=True)
    g.picture.save_picture(file_name=str(path))
    if not path.exists() or path.stat().st_size<1000:raise RuntimeError(f"Invalid export: {path}")
    return {"path":str(path.relative_to(ROOT)).replace("\\","/"),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "graphics_state":state,"camera":cam,"picture":g.picture.get_state(),"native_fluent_export":True}

def export(solver,out,only=None):
    catalog=json.loads((out/"catalog.json").read_text())
    ranges=json.loads((out/"range-receipt.json").read_text())["display_ranges"]
    rp=out/"export-receipt.json"
    receipt=json.loads(rp.read_text()) if rp.exists() else {"status":"EXPORTING","solve_issued":False,"cases":{}}
    for entry in catalog:
        if only and entry["id"] not in only:continue
        if entry["role"]=="particle-views":continue
        old=receipt["cases"].get(entry["id"],{})
        if old.get("status")=="EXPORTED":continue
        try:
            g=prepare(solver,entry);c=g.contour["story-scalar"];v=g.vector["story-vector"]
            folder=ROOT/entry["figure_dir"]
            record={"source":entry,"images":{},"status":"EXPORTING"}
            for name,field,surface,horizontal in [("liquid","phase-2-vof",VERTICAL,False),("inlet-liquid","phase-2-vof",INLET,True)]:
                lo,hi=ranges[field]
                c.set_state({"field":field,"surfaces_list":[surface],"range_options":{"global_range":False,"auto_range":False,"clip_to_range":False,"minimum":lo,"maximum":hi},"options":{"filled":True,"node_values":True,"boundary_values":False,"contour_lines":False},"color_map":{"font_automatic":True,"font_size":.025,"width":8.}})
                c.display();cam=camera(g,horizontal)
                record["images"][name]=picture(g,folder/f"{entry['id']}-{name}.png",c.get_state(),cam)
            for name,surface,horizontal in [("vertical-vectors",VERTICAL,False),("inlet-vectors",INLET,True)]:
                lo,hi=ranges["velocity-magnitude"]
                v.set_state({"vector_field":"velocity","field":"velocity-magnitude","surfaces_list":[surface],"range_options":{"global_range":False,"auto_range":False,"clip_to_range":False,"minimum":lo,"maximum":hi},"options":{"auto_scale":False,"scale":.1,"skip":0},"style":"arrow","vector_opt":{"in_plane":True,"fixed_length":True,"color":""},"color_map":{"font_automatic":True,"font_size":.025,"width":8.}})
                v.display();cam=camera(g,horizontal)
                record["images"][name]=picture(g,folder/f"{entry['id']}-{name}.png",v.get_state(),cam)
            if entry["speed"]==26.81:
                lo,hi=ranges["pressure"]
                c.set_state({"field":"pressure","surfaces_list":[VERTICAL],"range_options":{"global_range":False,"auto_range":False,"minimum":lo,"maximum":hi}})
                c.display();cam=camera(g)
                record["images"]["pressure"]=picture(g,folder/f"{entry['id']}-pressure.png",c.get_state(),cam)
            if entry["family"]=="F4":
                fields=c.field.allowed_values()
                film=[f for f in fields if "film" in f.lower() and "thickness" in f.lower()]
                if len(film)!=1:raise RuntimeError(f"Film thickness field is ambiguous: {film}")
                c.set_state({"field":film[0],"surfaces_list":["wall"],"range_options":{"global_range":False,"auto_range":True}})
                c.range_options.compute();observed=c.range_options.get_state()
                record["film_observed_range"]=observed
                upper=math.ceil(observed["maximum"]/0.00005)*0.00005
                c.range_options.set_state({"global_range":False,"auto_range":False,"minimum":0.,"maximum":upper})
                c.display();cam=camera(g,wall=True)
                record["images"]["film-thickness"]=picture(g,folder/f"{entry['id']}-film-thickness.png",c.get_state(),cam)
                cv=solver.settings.results.custom_vectors
                if "story-film-velocity" not in cv.get_object_names():cv.create(name="story-film-velocity")
                fcv=cv["story-film-velocity"]
                fcv.set_state({"x_component":"film-x-velocity","y_component":"film-y-velocity","z_component":"film-z-velocity"})
                record["film_custom_vector"]=fcv.get_state()
                allowed=v.vector_field.allowed_values()
                vf=[f for f in allowed if "film" in f.lower()]
                if vf:
                    scalar=[f for f in fields if f=="film-velocity-mag"]
                    if len(vf)==1 and len(scalar)==1:
                        v.set_state({"vector_field":vf[0],"field":scalar[0],"surfaces_list":["wall"],"vector_opt":{"in_plane":False,"fixed_length":True},"range_options":{"global_range":False,"auto_range":True}})
                        v.range_options.compute();vr=v.range_options.get_state();record["film_velocity_observed_range"]=vr
                        v.range_options.set_state({"global_range":False,"auto_range":False,"minimum":0.,"maximum":math.ceil(vr["maximum"])})
                        v.display();cam=camera(g,wall=True)
                        record["images"]["film-vectors"]=picture(g,folder/f"{entry['id']}-film-vectors.png",v.get_state(),cam)
                    else:record["film_vectors_gap"]={"vector_fields":vf,"scalar_fields":scalar}
                else:record["film_vectors_gap"]="Native vector-field selector does not expose film velocity."
            record["status"]="EXPORTED"
            receipt["cases"][entry["id"]]=record
        except Exception:
            receipt["cases"][entry["id"]]={"source":entry,"status":"ERROR","traceback":traceback.format_exc()}
            dump(out,"export-receipt.json",receipt)
            raise
        dump(out,"export-receipt.json",receipt)
        print("Exported "+entry["id"],flush=True)
    receipt["status"]="EXPORTED_AWAIT_VISUAL_QA"
    dump(out,"export-receipt.json",receipt)

def refresh_inlet_views(solver,out,only=None):
    """Increase native legend clearance without altering scientific fields."""
    receipt=json.loads((out/"export-receipt.json").read_text())
    for id,r in receipt['cases'].items():
        if only and id not in only:continue
        if r.get('inlet_layout_refreshed'):continue
        g=prepare(solver,r['source'])
        for kind,group,name in [('inlet-liquid',g.contour,'story-scalar'),('inlet-vectors',g.vector,'story-vector')]:
            prior=r['images'][kind];obj=group[name];state=prior['graphics_state']
            keys=['field','surfaces_list','range_options','options','color_map']
            if kind=='inlet-vectors':keys+=['vector_field','vector_opt','style']
            obj.set_state({k:state[k] for k in keys})
            obj.display();cam=camera(g,horizontal=True)
            r['images'][kind]=picture(g,ROOT/prior['path'],obj.get_state(),cam)
        r['inlet_layout_refreshed']=True
        dump(out,'export-receipt.json',receipt)
        print('Refreshed inlet layout '+id,flush=True)

def tracks(solver,out,only=None):
    catalog=json.loads((out/"catalog.json").read_text())
    rp=out/"track-export-receipt.json"
    receipt=json.loads(rp.read_text()) if rp.exists() else {"solve_issued":False,"cases":{}}
    for entry in catalog:
        if not entry["tracks"] or (only and entry["id"] not in only):continue
        if entry['id'] in receipt['cases']:continue
        g=prepare(solver,entry)
        if 'story-boundary' not in g.mesh.get_object_names():g.mesh.create(name='story-boundary')
        mesh=g.mesh['story-boundary']
        mesh.set_state({'surfaces_list':['wall','steaminlet','steamoutlet'],'options':{'edges':True,'faces':False,'nodes':False},'edge_type_options':{'edge_type':'outline'}})
        if "story-tracks" not in g.particle_track.get_object_names():g.particle_track.create(name="story-tracks")
        p=g.particle_track["story-tracks"]
        allowed_particle_fields=p.field.allowed_values() or []
        diameter_field='Particle Diameter' if 'Particle Diameter' in allowed_particle_fields else 'particle-diameter'
        before=solver.settings.setup.models.discrete_phase.get_state()
        images={}
        for diameter in ["07","35","89"]:
            injection=f"09cv3-finemist-{diameter}um"
            p.set_state({"field":diameter_field,"injections_list":[injection],"track_single_particle_stream":{"enabled":True,"stream_id":0},"skip":0,"coarsen":1,"range_options":{"auto_range":False,"minimum":0.000005,"maximum":0.0001},"style_attributes":{"style":"line","line_width":2},"color_map":{"font_automatic":False,"font_size":16,"width":8.},'draw_mesh':True,'mesh_object':'story-boundary'})
            p.display();g.mesh.add_to_graphics(object_name='story-boundary');cam=camera(g,wall=True)
            images[diameter]=picture(g,ROOT/entry["figure_dir"]/f"{entry['id']}-track-{diameter}um-stream0.png",p.get_state(),cam)
        after=solver.settings.setup.models.discrete_phase.get_state()
        if before!=after:raise RuntimeError("DPM settings changed during trajectory display")
        receipt["cases"][entry["id"]]={"source":entry,"images":images,"dpm_settings_unchanged":True,"stream_id":0,'mesh_state':mesh.get_state(),
                                     "selection_note":"One deterministic inlet stream per size; illustrative trajectories, not population statistics."}
        dump(out,"track-export-receipt.json",receipt)
        print("Exported selected tracks "+entry["id"],flush=True)



