"""Phase 9: prepare consistent mesh children and stop at full-load bulk holds.

Attach only to the explicitly owned Server 3. Never freeze bulk equations.
Inputs remain immutable; all checkpoints and reports use server-local disk.
"""
from pathlib import Path, PureWindowsPath
import argparse
import copy
import json
import math
import sys
import time
import re
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts/setup'), str(ROOT/'scripts/inspection')]
import run_phase72a_stage3_slit154k as previous
import run_phase72a_stage3_server3 as base
from run_phase72a_e27_server1_continuation import pair_save, native_iteration, dump
from run_phase72a_local_film_replay import require_match
from run_phase72a_reentrainment_speeds import MODEL_ARGS
from pyansys_fluent.common import remote_chdir, remote_file_exists
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256
from pyansys_fluent.remote_text import read_text, write_ascii_text_new

OUT = ROOT/'output/phase9-mesh-convergence/20261007'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase9\20261007')
SHARED = PureWindowsPath(r'C:\Users\syok443\OneDrive - The University of Auckland')
PARENT = SHARED/'P4P-Fluent-Artifacts/Phase72A/Stage3/early-ewf-startup/prepared-A-N1580/prepared-A-N1580'
MESH_FOLDER = SHARED/'2026 Sem 1/700/P4PCFD/CAD PurnantoV2'
WALL_PARTS = ['wall', 'vessel-wall-wall-separator-purnanto',
              'inlet-wall-1-wall-separator-purnanto', 'inlet-wall-2-wall-separator-purnanto']
HOST_PYTHON = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage3\slit154k-film-development-20261006\controller-venv\Scripts\python.exe')


def attach():
    """Bound the v252 client's initial version query; preserve its session."""
    from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import SchemeInterpreterService
    from ansys.api.fluent.v0 import scheme_eval_pb2
    original=SchemeInterpreterService.string_eval
    def initial_version(self,expression):
        if expression=='(cx-version)':
            return self._stub.StringEval(scheme_eval_pb2.StringEvalRequest(input=expression),
                                         metadata=self._metadata,timeout=5).output
        return original(self,expression)
    SchemeInterpreterService.string_eval=initial_version
    try:
        return previous.attach()
    finally:
        SchemeInterpreterService.string_eval=original


def source_receipt():
    return OUT/'source-template-audited.json'


def prepared_receipt(label):
    return OUT/(label+'-prepared-audited.json')


def bulk_audit(s):
    """Read archived interaction controls only after a native case reopen."""
    domains=s.rp_vars('domains')
    interaction=next(domain for domain in domains if domain[0][2]=='interaction')
    values={item[0]:item[1:] for item in interaction[1:]}
    result={key:values[key] for key in ['sfc-modeling?','sfc-model-type',
            'sfc-tension-coeff','turbulence-interaction','drag','slip-velocity',
            'wall-adhesion?','jump-adhesion?']}
    result.update(compressibility_flag=s.rp_vars('turb-compress-mod?'),
                  drag_modification_flag=s.rp_vars('mp/modify-drag?'))
    return json.loads(json.dumps(result))


def require_bulk_audit(s):
    result=bulk_audit(s)
    expected=json.loads((OUT/'08b-approved-bulk-contract.json').read_text())
    if result!=expected:raise RuntimeError('Nested bulk settings differ from approved 08b contract')
    return result


def apply_approved_bulk(s):
    """Version-252 native force setters; keep selected later controls."""
    force=s.tui.define.phases.set_domain_properties.interaction_domain.forces.surface_tension
    force.sfc_tension_coeff('yes','constant',0.04041000083088875)
    force.sfc_modeling('yes')
    # CSF is already selected. Do not invoke the model-type yes/no prompt.
    s.rp_vars('turb-compress-mod?',True)
    s.rp_vars('mp/modify-drag?',True)


def restore_stored_interaction(s,pair,folder,label):
    """Require the approved native contract; never patch case archives to force it."""
    load(s,pair)
    require_bulk_audit(s)
    return pair


def audit_existing(s,label=None):
    """Correct a preserved dry low-feed pair without overwriting its receipt."""
    path=prepared_receipt(label) if label else source_receipt()
    if path.exists():
        record=json.loads(path.read_text());load(s,record['pair']);require_bulk_audit(s)
        return record
    original=OUT/(label+'-prepared.json') if label else OUT/'source-template.json'
    record=json.loads(original.read_text());load(s,record['pair'])
    before=base.state(s)
    apply_approved_bulk(s)
    folder=WORK/label if label else WORK
    pair=save(s,folder,'08b-audited-native-low-feed-N1580')
    pair=restore_stored_interaction(s,pair,folder,'08b-audited-low-feed-N1580')
    require_bulk_audit(s)
    after=base.state(s);require_match(after['readback'],before['readback'])
    if after['methods']!=before['methods']:raise RuntimeError('Audit altered selected methods')
    assert_bulk_active(s)
    record.update(pair=pair,state=after,bulk_audit=bulk_audit(s),
                  audit_parent_pair=record['pair'],settings_audit='08b-approved',
                  status='PREPARED_REOPEN_VERIFIED' if label else 'SOURCE_REOPEN_VERIFIED')
    dump(path,record);print('BULK_AUDIT_REOPEN_VERIFIED',label or 'source',flush=True)
    return record


def save(s, folder, label):
    require_idle(s)
    ensure_remote_directory(s, str(folder/'scratch'))
    return pair_save(s, folder/(label+'.cas.h5'), folder/'scratch', scratch_tag=label)


def require_idle(s):
    # Never replace a loaded case or change its feed during an active solve.
    if (s.settings.setup.cell_zone_conditions.is_active() and
        not s.settings.solution.run_calculation.iterate.is_active()):
        raise RuntimeError('Owned Server 3 is busy; no mutation submitted')


def set_loading(s, multiplier):
    require_idle(s)
    return base.loading(s, multiplier)


def read_feed(s, multiplier):
    bc=s.settings.setup.boundary_conditions.mass_flow_inlet
    result={'multiplier':multiplier}
    for zone,phase,target,key in [('liquidinlet','phase-2',116.92,'liquid_kg_s'),
                                   ('steaminlet','phase-1',80.69,'vapor_kg_s')]:
        value=bc[zone].phase[phase].momentum.mass_flow_rate.get_state()['value']
        if not math.isfinite(value) or not math.isclose(value,target*multiplier,rel_tol=1e-10):
            raise RuntimeError('Final inlet loading differs from full feed')
        result[key]=value
    return result


def load(s, pair):
    require_idle(s)
    # Check both members before replacing the current case.
    for key in ['case','data']:
        if not remote_file_exists(s,pair[key]):raise FileNotFoundError(pair[key])
    print('PAIR_LOAD_CHDIR',str(WORK),flush=True)
    remote_chdir(s, str(WORK))
    print('PAIR_LOAD_CASE',pair['case'],flush=True)
    s.settings.file.read_case(file_name=pair['case'])
    print('PAIR_LOAD_UDF','libcontactv2',flush=True)
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    print('PAIR_LOAD_DATA',pair['data'],flush=True)
    s.settings.file.read_data(file_name=pair['data'])
    if 'native_iteration' in pair and native_iteration(s)!=pair['native_iteration']:
        raise RuntimeError('Loaded pair native iteration differs from saved receipt')
    print('PAIR_LOAD_COMPLETE',flush=True)


def assert_bulk_active(s):
    state = s.settings.solution.controls.equations.get_state()
    if state != {'drift': True, 'flow': True, 'ke': True, 'mp': True}:
        raise RuntimeError('All four reference bulk equations must remain active')
    return state


def require_setup_same(actual, expected):
    """Keep exact setup equality except native rounding of ramp inlet flows."""
    normalized=copy.deepcopy(actual);rounding=[]
    for zone,phase in [('liquidinlet','phase-2'),('steaminlet','phase-1')]:
        path=['boundary_conditions','mass_flow_inlet',zone,'phase',phase,
              'momentum','mass_flow_rate','value']
        a=normalized;e=expected
        for key in path[:-1]:a=a[key];e=e[key]
        av=a[path[-1]];ev=e[path[-1]]
        if av!=ev and isinstance(av,(int,float)) and isinstance(ev,(int,float)):
            if math.isfinite(av) and math.isfinite(ev) and math.isclose(av,ev,rel_tol=1e-12,abs_tol=1e-12):
                rounding.append({'path':'/'.join(path),'before':ev,'after':av})
                a[path[-1]]=ev
    if normalized!=expected:
        raise RuntimeError('Solved child setup changed beyond inlet-flow serialization rounding')
    return {'status':'PASS','inlet_flow_rounding':rounding,'all_other_setup_values':'EXACT'}


def apply_selected_settings(s,selected):
    model=selected['audit']['film_parameters']
    s.tui.define.models.eulerian_wallfilm.model_options(*MODEL_ARGS)
    material='water-liquid-at-psep-pcle'
    particles=s.settings.setup.materials.inert_particle
    if material not in particles.get_object_names():particles.create(name=material)
    particle_state=selected['state']['setup']['materials']['inert_particle'][material]
    particles[material].set_state(particle_state)
    injections=s.settings.setup.models.discrete_phase.injections
    for name in injections.get_object_names():injections[name].material=material
    for name in ['separator-purnanto:1','separator-purnanto:1:001','wall','wall:004']:
        s.settings.setup.boundary_conditions.wall[name].phase['mixture'].turbulence.roughness_height=4.5e-5
    s.settings.setup.boundary_conditions.wall['wall'].phase['mixture'].wall_film.set_state(selected['audit']['wall'])
    s.rp_vars('wall-film/model-parameters',list(model.items()))
    s.settings.solution.methods.set_state(selected['state']['methods'])
    s.settings.solution.controls.set_state(selected['state']['readback']['controls'])
    s.settings.solution.run_calculation.pseudo_time_settings.set_state(selected['run_controls']['pseudo_time_settings'])
    return model


def prepare_source(s):
    if source_receipt().exists():
        record=json.loads(source_receipt().read_text());load(s,record['pair'])
        require_bulk_audit(s);assert_bulk_active(s)
        return record
    path = OUT/'source-template.json'
    if path.exists():
        record=json.loads(path.read_text());load(s,record['pair']);assert_bulk_active(s)
        return record
    if not (OUT/'server3-preservation.json').exists():
        raise RuntimeError('Preserve the previous Server 3 pair before replacement')
    for folder in [WORK, WORK/'scratch', WORK/'source-monitors']:
        ensure_remote_directory(s,str(folder))
    for kind,ext in [('case','cas.h5'),('data','dat.h5')]:
        digest=remote_file_sha256(s,str(PARENT)+'.'+ext,str(WORK/'scratch'/('parent-'+kind+'.sha256')))
        if digest != previous.PARENT_HASHES[kind]:
            raise RuntimeError('Prepared low-feed A parent hash differs')
    archive=base.SOURCE/'contact-libraries.zip'
    if remote_file_sha256(s,str(archive),str(WORK/'scratch'/'contact.sha256')) != base.HASHES['contact-libraries.zip']:
        raise RuntimeError('Contact UDF archive differs')
    base.powershell(s,"$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath '"+str(archive)+"' -DestinationPath '"+str(WORK)+"' -Force")
    remote_chdir(s,str(WORK))
    s.settings.file.read_case(file_name=str(PARENT)+'.cas.h5')
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    s.settings.file.read_data(file_name=str(PARENT)+'.dat.h5')
    before=base.state(s)
    selected=json.loads((OUT/'raw/provisional-stage4-selection.json').read_text())
    model=apply_selected_settings(s,selected)
    set_loading(s,.25)
    s.settings.file.auto_save.data_frequency=0
    base.add_pressure_reports(s)
    paths=base.instrument(s,WORK/'source-monitors')
    after=base.state(s)
    require_match({'fields':after['readback']['fields']},{'fields':before['readback']['fields']})
    assert_bulk_active(s)
    if dict(s.rp_vars('wall-film/solution-state'))['film_elapsed_time'] != 0:
        raise RuntimeError('Prepared low-feed film clock must be zero')
    if after['film_model'] != model:raise RuntimeError('Stage 4 provisional film settings differ')
    pair=save(s,WORK,'provisional-stage4-low-feed-A-N1580')
    load(s,pair)
    reopened=base.state(s);require_match(reopened['readback'],after['readback'])
    if reopened['setup']!=after['setup'] or reopened['methods']!=after['methods']:
        raise RuntimeError('Source template setup differs after reopen')
    record={'status':'SOURCE_REOPEN_VERIFIED','pair':pair,'state':reopened,
            'film':dict(s.rp_vars('wall-film/solution-state')),
            'parent_hashes':previous.PARENT_HASHES,'bulk_reinitialized':False,
            'stage4_settings_owner':'PyAnsys/output/phase72a-stage4-realism/20261007/recovery1-prepared.json',
            'provisional_ewf':True,'report_paths':paths}
    dump(path,record)
    print('SOURCE_REOPEN_VERIFIED',flush=True)
    return record


@contextmanager
def client_capture(s,path):
    """Capture one setup step without closing the campaign's live stream."""
    if path.exists():raise FileExistsError(path)
    path.touch(exist_ok=False)
    def append(text):
        with path.open('a',encoding='utf-8') as stream:stream.write(text)
    already_streaming=s.transcript.is_streaming
    callback=s.transcript.register_callback(append,keep_new_lines=True)
    try:
        if not already_streaming:s.transcript.start(write_to_stdout=False)
        yield
    finally:
        s.transcript.unregister_callback(callback)
        if not already_streaming:s.transcript.stop()


def inspect_target(s,label):
    folder=WORK/label;ensure_remote_directory(s,str(folder))
    source=prepare_source(s)
    mesh=MESH_FOLDER/('Separator-purnanto-'+label+'.msh.h5')
    if not remote_file_exists(s,str(mesh)):raise FileNotFoundError(str(mesh))
    expected=next(m for m in json.loads((OUT/'mesh-input-audit.json').read_text())['meshes'] if m['label']==label)
    digest=remote_file_sha256(s,str(mesh),str(folder/'input.sha256'))
    if digest!=expected['sha256']:raise RuntimeError('Mesh has not synced unchanged to Server 3')
    remote_chdir(s,str(folder))
    with client_capture(s,OUT/(label+'-target-inspection-'+str(time.time_ns())+'.txt')):
        s.settings.file.read_mesh(file_name=str(mesh))
        s.settings.mesh.check();s.settings.mesh.size_info();s.tui.mesh.modify_zones.list_zones()
        record={'label':label,'mesh':str(mesh),'sha256':digest,'cells':expected['cells'],
                'boundary_conditions':s.settings.setup.boundary_conditions.get_state(),
                'cell_zones':s.settings.setup.cell_zone_conditions.get_state(),
                'scale_args':s.settings.mesh.scale.argument_names,
                'scale_help':s.settings.mesh.scale.__doc__,
                'merge_args':s.settings.mesh.modify_zones.merge_zones.argument_names}
    dump(OUT/(label+'-target.json'),record)
    print('TARGET_INSPECTED',label,flush=True)


def remote_audit(s, mesh, folder):
    script=WORK/'inspect_phase9_mesh_inputs.py'
    if not remote_file_exists(s,str(script)):
        write_ascii_text_new(s,str(script),(ROOT/'scripts/inspection/inspect_phase9_mesh_inputs.py').read_text())
    audit_tag=str(time.time_ns())
    result=folder/('native-topology-'+audit_tag+'.json');log=folder/('native-topology-'+audit_tag+'.log')
    command="$phase9AuditLog=(& '"+str(HOST_PYTHON)+"' '"+str(script)+"' --single-mesh '"+str(mesh)+"' --output '"+str(result)+"' 2>&1 | Out-String); [IO.File]::WriteAllText('"+str(log)+"',$phase9AuditLog,[Text.Encoding]::ASCII)"
    base.powershell(s,command)
    if not remote_file_exists(s,str(result)):
        raise RuntimeError('Remote mesh audit failed: '+read_text(s,str(log)))
    return json.loads(read_text(s,str(result)))


def map_target(s,label,resume=False):
    """Prove physical scale and collector topology before native replacement."""
    from run_p7_e5_cz import create_lower_register
    folder=WORK/label
    with client_capture(s,OUT/(label+'-map-'+str(time.time_ns())+'.txt')):
        target_cff=folder/'split-target.cas.h5'
        if resume:
            s.settings.file.read_case(file_name=str(target_cff))
            scale=1; height=6.261; parts=['wall']; selection={'recovered_from':str(target_cff)}
        else:
            # Use native vertex coordinates, not the raw file's units flag.
            from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest, SurfaceDataType
            import numpy as np
            geometry=s.fields.field_data.get_field_data(SurfaceFieldDataRequest(
                surfaces=['steamoutlet'],data_types=[SurfaceDataType.Vertices]))
            vertices=np.asarray(geometry['steamoutlet'].vertices)
            height=float(vertices[:,1].mean())
            if abs(height-6.261)<.01:scale=1.0
            elif abs(height-6261)<10:scale=.001
            else:raise RuntimeError(f'Unexpected native outlet height: {height}')
            if scale!=1:s.settings.mesh.scale(x_scale=scale,y_scale=scale,z_scale=scale)
            walls=s.settings.setup.boundary_conditions.wall
            parts=[n for n in WALL_PARTS if n in walls.get_object_names()]
            if 'wall' not in parts:raise RuntimeError('Original physical wall role missing')
            if len(parts)>1:
                reference=walls['wall'].get_state()
                for name in parts:
                    item=copy.deepcopy(reference);item['name']=name;walls[name].set_state(item)
                s.settings.mesh.modify_zones.merge_zones(zone_names=parts)
                survivors=[n for n in parts if n in walls.get_object_names()]
                if len(survivors)!=1:raise RuntimeError('Physical wall union merge failed')
                if survivors[0]!='wall':s.settings.mesh.modify_zones.zone_name(zone_name=survivors[0],new_name='wall')
            register,selection=create_lower_register(s)
            s.settings.mesh.modify_zones.sep_cell_zone_mark(cell_zone_name='separator-purnanto',register=register,move_faces=True)
            generated=[n for n in s.settings.setup.cell_zone_conditions.fluid.get_object_names() if n!='separator-purnanto']
            if len(generated)!=1:raise RuntimeError('Expected one lower collector cell zone')
            s.settings.mesh.modify_zones.zone_name(zone_name=generated[0],new_name='p71a-v2-virtual-outlet')
            s.settings.file.write_case(file_name=str(target_cff))
        topo=remote_audit(s,target_cff,folder)
        zones={z['name']:z['id'] for z in topo['cell_zones']}
        lower,upper=zones['p71a-v2-virtual-outlet'],zones['separator-purnanto']
        cross=[z for z in topo['face_zones'] if {z.get('c0'),z.get('c1')}=={lower,upper}]
        if len(cross)!=2:raise RuntimeError('Expected two verified collector entry face zones; inspect topology')
        source=json.loads(source_receipt().read_text())['state']
        entries=source['readback']['entry_faces']
        clean=lambda item:{k:v for k,v in item.items() if k!='name'}
        if clean(list(entries.values())[0])!=clean(list(entries.values())[1]):
            raise RuntimeError('Reference entry conditions differ; individual geometric correspondence needed')
        renames={}
        for z in topo['face_zones']:
            if z.get('c0')==lower and not z.get('c1'):
                if z['name'].startswith('wall') and z['name']!='bottom':renames[z['name']]='wall:004'
                elif z['name'].startswith('separator-purnanto:1'):renames[z['name']]='separator-purnanto:1:001'
            if z.get('c0')==lower and z.get('c1')==lower:
                renames[z['name']]='interior--separator-purnanto:013'
        # Both entry boundaries have identical physical conditions; their union
        # and lower/upper adjacency are the invariant, not their generated suffix.
        for z,name in zip(sorted(cross,key=lambda item:item['name']),sorted(entries)):
            renames[z['name']]=name
        for old,new in renames.items():
            if old!=new:s.settings.mesh.modify_zones.zone_name(zone_name=old,new_name=new)
        s.settings.mesh.check();s.settings.mesh.size_info()
        legacy=folder/'mapped-target.cas'
        s.settings.file.cff_files=False;s.settings.file.write_case(file_name=str(legacy));s.settings.file.cff_files=True

    record={'status':'TARGET_MAPPED','scale_applied':scale,'native_outlet_height_before':height,
            'wall_union':parts,'collector_register':selection,'topology':topo,'renames':renames,
            'entry_mapping_basis':'Identical reference conditions; same physical lower/upper interface union',
            'native_replacement_input':str(legacy)}
    dump(OUT/(label+'-mapped.json'),record);print('TARGET_MAPPED',label,flush=True)
    return record


def prepare_child(s,label):
    path=prepared_receipt(label);folder=WORK/label
    if path.exists():return json.loads(path.read_text())
    if (OUT/(label+'-prepared.json')).exists():return audit_existing(s,label)
    source=json.loads(source_receipt().read_text())
    ensure_remote_directory(s,str(folder))
    if label=='60k':
        load(s,source['pair'])
        mapped={'source_mesh_reused':True,'basis':'Same 60964-cell historical A mesh; supplied geometry audit retained'}
    else:
        if (OUT/(label+'-mapped.json')).exists():
            mapped=json.loads((OUT/(label+'-mapped.json')).read_text())
        else:
            inspect_target(s,label);mapped=map_target(s,label)
        transfer_parent={'case':str(PARENT)+'.cas.h5','data':str(PARENT)+'.dat.h5'}
        load(s,transfer_parent)
        transfer_parameters=dict(s.rp_vars('wall-film/model-parameters'))
        if transfer_parameters['film-stripping?'] or transfer_parameters['film-separation?']:
            raise RuntimeError('Native transfer requires the original non-stripping A parent')
        injection_names=s.settings.setup.models.discrete_phase.injections.get_object_names()
        injection_backup=folder/'source.inj'
        s.tui.file.write_injections(str(injection_backup),*injection_names,'()')
        s.scheme.eval("(rpsetvar 'dynamesh/replace-mesh/partition-per-zone? #t)")
        with client_capture(s,OUT/(label+'-transfer-'+str(time.time_ns())+'.txt')):
            s.settings.mesh.replace(file_name=mapped['native_replacement_input'],zones=False)
            injections=s.settings.setup.models.discrete_phase.injections
            if set(injections.get_object_names())!=set(injection_names):
                if injections.get_object_names():raise RuntimeError('Unexpected partial injection transfer')
                s.settings.file.read_injections(file_name=str(injection_backup))
            for _ in range(7):
                extras=set(injections.get_object_names())-set(injection_names)
                if not extras:break
                if not all(name.startswith('imported-inj-') for name in extras):
                    raise RuntimeError('Unexpected diagnostic injection after native import')
                injections.delete(name_list=sorted(extras))
            if set(injections.get_object_names())!=set(injection_names):raise RuntimeError('DPM injection names differ')

        print('NATIVE_TRANSFER_INJECTIONS_VERIFIED',label,flush=True)
        transfer_fields=base.state(s)['readback']['fields']
        selected=json.loads((OUT/'raw/provisional-stage4-selection.json').read_text())
        apply_selected_settings(s,selected)
        apply_approved_bulk(s)
        set_loading(s,.25)
        require_match({'fields':base.state(s)['readback']['fields']},{'fields':transfer_fields})
        mapped['transfer_settings_basis']='Verified original non-stripping/non-separating E2.7 A; Stage 4 settings applied after interpolation'
    assert_bulk_active(s)
    print('CHECKING_CHILD_INVARIANTS',label,flush=True)
    actual=base.state(s)
    for group in ['hooks','lower_film_wall','entry_faces','dpm','film_parameters','controls']:
        if actual['readback'][group]!=source['state']['readback'][group]:
            raise RuntimeError('Transferred invariant differs: '+group)
    if actual['methods']!=source['state']['methods']:raise RuntimeError('Carrier methods differ')
    for group in set(source['state']['setup'])-{'boundary_conditions','cell_zone_conditions'}:
        if actual['setup'][group]!=source['state']['setup'][group]:
            raise RuntimeError('Transferred setup group differs: '+group)
    if actual['readback']['fields']['v2-total-liquid-mass'][0]<=0:raise RuntimeError('Mapped bulk field is empty')
    if actual['readback']['fields']['p72a-e2.7-ewf-film-mass-total'][0]!=0:raise RuntimeError('Mapped initial film is not dry')
    if native_iteration(s)!=1580:raise RuntimeError('Mapped parent iteration differs')
    s.settings.file.auto_save.data_frequency=0
    extras={'p72s4-dpm-source':'film-dpm-mass-src','p72s4-stripped-mass':'film-stripped-mass',
            'p72s4-separated-mass':'film-separated-mass'}
    definitions=s.settings.solution.report_definitions.surface
    files=s.settings.solution.monitor.report_files
    for name,field in extras.items():
        if name not in definitions.get_object_names():definitions.create(name=name)
        definitions[name].set_state({'report_type':'surface-sum','field':field,'surface_names':['wall']})
        if name not in files.get_object_names():files.create(name=name)
        files[name].report_defs=[name]
    paths=base.instrument(s,folder/'monitors')
    before=base.state(s);pair=save(s,folder,'prepared-low-feed-N1580')
    print('CHILD_PAIR_SAVED',label,flush=True)
    pair=restore_stored_interaction(s,pair,folder,'prepared-08b-low-feed-N1580')
    load(s,pair);after=base.state(s)
    try:require_match(after['readback'],before['readback'])
    except RuntimeError:
        # Native interpolation can rebuild face fluxes on the first reopen.
        keep={n:v for n,v in before['readback']['fields'].items() if 'flux' not in n}
        require_match({**after['readback'],'fields':{n:after['readback']['fields'][n] for n in keep}},
                      {**before['readback'],'fields':keep})
        pair=save(s,folder,'prepared-stable-low-feed-N1580');before=after
        load(s,pair);after=base.state(s);require_match(after['readback'],before['readback'])
    if after['setup']!=before['setup'] or after['methods']!=before['methods']:raise RuntimeError('Child setup changed on reopen')
    if label!='60k':
        native_mesh=remote_audit(s,pair['case'],folder)
        expected=next(m['cells'] for m in json.loads((OUT/'mesh-input-audit.json').read_text())['meshes'] if m['label']==label)
        if native_mesh['cells']!=expected:raise RuntimeError('Prepared native cell count differs from supplied mesh')
    else:native_mesh={'cells':60964,'source_mesh_reused':True}
    require_bulk_audit(s)
    record={'status':'PREPARED_REOPEN_VERIFIED','label':label,'pair':pair,'state':after,
            'bulk_audit':bulk_audit(s),'settings_audit':'08b-approved',
            'mapping':mapped,'report_paths':paths,'bulk_reinitialized':False,
            'film':dict(s.rp_vars('wall-film/solution-state')),'native_mesh':native_mesh}
    dump(path,record);print('CHILD_PREPARED',label,flush=True);return record


def film(s):return dict(s.rp_vars('wall-film/solution-state'))


def histories(s,paths,names):
    from run_phase72a_adaptive_film import history
    return {name:history(read_text(s,paths[name])) for name in names}


def hold_limits():
    return {'pressure_drop_range_percent_mean':5.0,
            'bulk_mass_range_percent_mean':10.0,
            'liquid_flux_range_percent_full_inlet':5.0}


def assess_hold_screen(screen):
    limits=hold_limits()
    result=copy.deepcopy(screen)
    result.update(limits=limits,pass_rule='ALL_THREE_WITHIN_LIMITS')
    result['pass']=all(math.isfinite(result.get(key,float('nan'))) and
                       0<=result[key]<=limit for key,limit in limits.items())
    return result


def refresh_hold_screens(m):
    m['hold_screens']=[assess_hold_screen(screen) for screen in m.get('hold_screens',[])]
    count=0
    for screen in m['hold_screens']:
        count=count+1 if screen['pass'] else 0
    m.update(stable_windows=count,hold_limits=hold_limits())


def hold_screen(s,m):
    import numpy as np
    names=['p72s3-pressure-inlet','p72s3-pressure-outlet',
           'v2-total-liquid-mass','v2-flux-phase2-steamoutlet']
    h=histories(s,m['report_paths'],names)
    end=m['verified_native_end'];start=max(m['full_hold_start']+1,end-999)
    ids=list(range(start,end+1))
    if len(ids)<1000:return {'pass':False,'reason':'Fewer than 1000 full-feed updates'}
    if any(not set(ids).issubset(v) for v in h.values()):raise RuntimeError('Full-feed monitor coverage incomplete')
    pressure=np.array([h[names[0]][i]-h[names[1]][i] for i in ids])
    mass=np.array([h[names[2]][i] for i in ids])
    liquid=np.array([h[names[3]][i] for i in ids])
    prange=100*float(np.ptp(pressure))/max(abs(float(pressure.mean())),1e-12)
    mrange=100*float(np.ptp(mass))/max(abs(float(mass.mean())),1e-12)
    lrange=100*float(np.ptp(liquid))/116.92
    return assess_hold_screen({'window':[start,end],
            'pressure_drop_range_percent_mean':prange,'bulk_mass_range_percent_mean':mrange,
            'liquid_flux_range_percent_full_inlet':lrange,'pressure_drop_mean_pa':float(pressure.mean()),
            'bulk_mass_mean_kg':float(mass.mean()),'signed_liquid_outlet_mean_kg_s':float(liquid.mean())})


@contextmanager
def native_batch_transcript(s,path):
    """One start/stop pair; close on a failed solve without masking its error."""
    start=s.settings.file.start_transcript
    # Only recover an inherited transcript when starting a new one is disabled.
    # Do not stop again after a normally closed preceding batch.
    if not start.is_active():
        stop=s.settings.file.stop_transcript
        if not stop.is_active():
            raise RuntimeError('Native transcript start unavailable; reconcile session state')
        stop()
    start(file_name=str(path))
    try:
        yield
    except BaseException:
        try:s.settings.file.stop_transcript()
        except Exception as exc:
            print('TRANSCRIPT_CLOSE_AFTER_FAILURE',type(exc).__name__,flush=True)
        raise
    else:
        s.settings.file.stop_transcript()


def batch(s,m,steps,label,checkpoint=True):
    from run_phase72a_adaptive_film import FILM
    if not isinstance(steps,int) or isinstance(steps,bool) or steps<=0:
        raise ValueError('A batch needs a positive integer update count')
    require_idle(s)
    folder=WORK/m['label'];start=native_iteration(s);end=start+steps
    if start!=m['verified_native_end']:raise RuntimeError('Live iteration differs from verified campaign endpoint')
    assert_bulk_active(s)
    dt=dict(s.rp_vars('wall-film/model-parameters'))['timestep-max']
    if not math.isfinite(dt) or dt<=0:raise RuntimeError('Invalid fixed film step')
    # Cortex's solution-state archive is refreshed by native save/reopen.
    # Use accepted transcript time between checkpoints.
    before_time=m['blocks'][-1]['film_end_s'] if m['blocks'] else film(s)['film_elapsed_time']
    remote=folder/(f'{label}-N{start}-N{end}-{time.time_ns()}.trn')
    with native_batch_transcript(s,remote):
        m.update(status='RUNNING',active_stage=label,active_target=end,active_transcript=str(remote))
        dump(OUT/(m['label']+'-run.json'),m)
        print('BATCH',m['label'],label,start,end,flush=True);t0=time.monotonic()
        base.iterate(s,steps)
    text=read_text(s,str(remote));(OUT/(m['label']+'-'+remote.name)).write_text(text)
    rows=[tuple(map(float,match.groups())) for match in FILM.finditer(text)]
    if len(rows)!=steps:raise RuntimeError('Native film-time evidence incomplete')
    if (any(not all(math.isfinite(value) for value in row) for row in rows)
        or any(row[2]<0 or row[2]>1 for row in rows)
        or re.search(r'floating point exception|fatal error|Divergence detected',text,re.I)):
        raise RuntimeError('Numerical recovery required; verified endpoint not advanced')
    if any(not math.isclose(row[0],before_time+(i+1)*dt,abs_tol=1e-10,rel_tol=1e-6)
           for i,row in enumerate(rows)):
        raise RuntimeError('Native film clock is not consecutive')
    accepted_end=rows[-1][0]
    if (not all(math.isclose(row[1],dt,rel_tol=1e-7) for row in rows)
        or not math.isclose(accepted_end-before_time,steps*dt,abs_tol=1e-10,rel_tol=1e-6)):
        raise RuntimeError('Accepted film time differs from requested fixed step')
    record={'stage':label,'start':start,'end':end,'film_start_s':before_time,
            'film_end_s':accepted_end,'step_s':dt,'peak_film_courant':max(row[2] for row in rows),
            'wall_seconds':time.monotonic()-t0,'transcript':str(remote)}
    if checkpoint:
        before_state=base.state(s)
        if not all(math.isfinite(v[0]) for v in before_state['readback']['fields'].values()):
            raise RuntimeError('Nonfinite fields; preserve and recover')
        pair=save(s,folder,f'{label}-N{end}-{time.time_ns()}')
        proof_path=OUT/(m['label']+'-checkpoint-'+str(end)+'-'+str(time.time_ns())+'.json')
        proof={'status':'SAVED_REOPEN_PENDING','pair':pair,'block':record,'before':before_state}
        dump(proof_path,proof)
        load(s,pair)
        require_bulk_audit(s)
        after_state=base.state(s);proof.update(status='REOPEN_CHECKS_PENDING',after=after_state)
        dump(proof_path,proof)
        require_match(after_state['readback'],before_state['readback'])
        proof['setup_check']=require_setup_same(after_state['setup'],before_state['setup'])
        if before_state['methods']!=after_state['methods']:
            raise RuntimeError('Solved child methods changed on reopen')
        if not math.isclose(film(s)['film_elapsed_time'],accepted_end,abs_tol=1e-12):
            raise RuntimeError('Film clock changed on reopen')
        record['pair']=pair;m['latest_pair']=pair
        record['fields']=after_state['readback']['fields']
        proof.update(status='REOPEN_VERIFIED',film=film(s));dump(proof_path,proof)
        record['checkpoint_proof']=str(proof_path)
    m['blocks'].append(record);m.update(status='CHECKPOINT_VERIFIED' if checkpoint else 'RAMP_PROGRESS_VERIFIED',
                                     verified_native_end=end,active_target=None)
    dump(OUT/(m['label']+'-run.json'),m)
    return record


def run_child(s,label,smoke_only=False):
    audit_path=OUT/'08b-settings-audit-approved.json'
    if not audit_path.exists() or json.loads(audit_path.read_text()).get('status')!='APPLIED_REOPEN_VERIFIED':
        raise RuntimeError('Complete the human-requested 08b settings audit before Phase 9 solves')
    path=OUT/(label+'-run.json')
    if path.exists():
        m=json.loads(path.read_text())
        if m['status'].startswith('FULL_FEED_PREPARED'):return m
        if m['status']=='RUNNING':raise RuntimeError('Reconcile pending native solve before resuming')
        load(s,m['latest_pair'])
        coordinate=native_iteration(s)
        if coordinate!=m['verified_native_end']:
            if m.get('active_stage')!='ramp' or coordinate>m['verified_native_end']:
                raise RuntimeError('Checkpoint coordinate differs')
            recovery=OUT/(label+'-ramp-resume-'+str(time.time_ns())+'.json')
            dump(recovery,{'previous_manifest':copy.deepcopy(m),'rollback_native':coordinate,
                           'reason':'Resume the last paired ramp checkpoint; repeat unsaved updates'})
            m['blocks']=[block for block in m['blocks'] if block['end']<=coordinate]
            m.update(verified_native_end=coordinate,status='CHECKPOINT_VERIFIED')
            dump(path,m)
        require_bulk_audit(s)
    else:
        record=prepare_child(s,label)
        load(s,record['pair'])
        require_bulk_audit(s)
        cells=next(m['cells'] for m in json.loads((OUT/'mesh-input-audit.json').read_text())['meshes'] if m['label']==label)
        ratio=(cells/60964)**(1/3)
        low=500*math.ceil(ratio-1e-12);minimum=1000*math.ceil(ratio-1e-12)
        m={'status':'READY','label':label,'cells':cells,'verified_native_end':1580,
           'latest_pair':record['pair'],'report_paths':record['report_paths'],'blocks':[],
           'low_hold_end':1580+low,'ramp_end':1580+low+2000,'minimum_full_hold':minimum,
           'full_hold_budget':20000,'bulk_freeze':False,'ewf_settings_final':False}
        dump(path,m)
    # Native autosaves protect large batches; checkpoints stay on local disk.
    autosave=s.settings.file.auto_save
    autosave.case_frequency='each-time';autosave.root_name=str(WORK/label/'auto-%i')
    autosave.retain_most_recent_files=False;autosave.data_frequency=500
    if m['verified_native_end']==1580:
        set_loading(s,.25);batch(s,m,20,'low-feed-smoke')
        proof=histories(s,m['report_paths'],list(m['report_paths']))
        if any(not set(range(1581,1601)).issubset(v) for v in proof.values()):
            raise RuntimeError('Smoke instrumentation coverage incomplete')
        m['instrumentation_smoke']='PASS';dump(path,m)
    if smoke_only:return m
    if m['verified_native_end']<m['low_hold_end']:
        set_loading(s,.25);batch(s,m,m['low_hold_end']-m['verified_native_end'],'low-feed-hold')
    while m['verified_native_end']<m['ramp_end']:
        progress=m['verified_native_end']-m['low_hold_end']
        set_loading(s,.25+.75*progress/2000)
        batch(s,m,10,'ramp',checkpoint=(progress+10)%500==0)
    set_loading(s,1.0)
    m.setdefault('full_hold_start',m['ramp_end']);m.setdefault('stable_windows',0)
    if (m['verified_native_end']-m['full_hold_start']>=1000 and
        (not m.get('hold_screens') or m['hold_screens'][-1]['window'][-1]!=m['verified_native_end'])):
        m.setdefault('hold_screens',[]).append(hold_screen(s,m))
    refresh_hold_screens(m);dump(path,m)
    while m['verified_native_end']-m['full_hold_start']<m['full_hold_budget']:
        if m['verified_native_end']-m['full_hold_start']>=m['minimum_full_hold'] and m['stable_windows']>=2:break
        batch(s,m,1000,'full-feed-hold')
        screen=hold_screen(s,m);m.setdefault('hold_screens',[]).append(screen)
        m['stable_windows']=m['stable_windows']+1 if screen['pass'] else 0
        dump(path,m)
        if m['verified_native_end']-m['full_hold_start']>=m['minimum_full_hold'] and m['stable_windows']>=2:break
    h=histories(s,m['report_paths'],list(m['report_paths']))
    # A recovered report file can retain later failed updates. Keep the final
    # exported histories within the preserved endpoint; native files stay intact.
    h={name:{iteration:value for iteration,value in values.items()
             if iteration<=m['verified_native_end']} for name,values in h.items()}
    ids=set(range(1581,m['verified_native_end']+1))
    if any(not ids.issubset(v) for v in h.values()):raise RuntimeError('Final monitor coverage incomplete')
    dump(OUT/(label+'-histories.json'),h)
    m.update(status='FULL_FEED_PREPARED_STABILITY_SCREEN_PASS' if m['stable_windows']>=2 else 'FULL_FEED_PREPARED_NONSTATIONARY_BUDGET',
             final_pair=m['latest_pair'],final_film=film(s),final_equations=assert_bulk_active(s),
             final_feed=read_feed(s,1.0),final_report_coverage='PASS',completed_utc=datetime.now(timezone.utc).isoformat())
    dump(path,m);return m


def campaign(s):
    path=OUT/'campaign-manifest.json'
    m=json.loads(path.read_text()) if path.exists() else {'status':'STARTED','server_id':'3',
       'authority':'human_20261007_phase9_full_server3_only','mesh_order':['60k','342k','680k','997k','2_6M'],
       'endpoint_boundary':'FULL_FEED_HOLD_BULK_ACTIVE','completed':[]}
    m.update(requires_explicit_resume=False,supervision_paused_by_human=False)
    if m.get('error'):
        prior={'error':m.pop('error'),'active_mesh':m.get('active_mesh')}
        for key in ['failure_pair','preservation_error']:
            if key in m:prior[key]=m.pop(key)
        m.setdefault('previous_failures',[]).append(prior)
    for label in m['mesh_order']:
        if label in m['completed']:continue
        m.update(status='RUNNING',active_mesh=label);dump(path,m)
        try:
            result=run_child(s,label)
            m['completed'].append(label);m.setdefault('results',{})[label]=result['status'];dump(path,m)
        except Exception:
            m.update(status='RECOVERY_REQUIRED',error=traceback.format_exc())
            try:m['failure_pair']=save(s,WORK/label,f'failure-N{native_iteration(s)}-{time.time_ns()}')
            except Exception:m['preservation_error']=traceback.format_exc()
            dump(path,m);raise
    m.update(status='COMPLETE_PREPARATION_ONLY',active_mesh=None);dump(path,m)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['source','inspect','map','finish-map','prepare','smoke','run','campaign'])
    parser.add_argument('--label',choices=['60k','342k','680k','997k','2_6M'])
    parser.add_argument('--live-transcript',help='Optional client-side live transcript for campaign monitoring')
    parser.add_argument('--controller-receipt',help='Optional desktop launch receipt to update when the campaign ends')
    args=parser.parse_args()
    # A client-only diagnostic signal never interrupts or exits Fluent.
    if sys.platform!='win32':
        import faulthandler
        import signal
        faulthandler.register(signal.SIGUSR1,all_threads=True)
    # The desktop controller holds this lock for its entire lifetime.
    # A second controller fails before attaching or issuing any Fluent call.
    if sys.platform!='win32':
        import fcntl
        controller_lock=(OUT/'controller.lock').open('a+')
        try:fcntl.flock(controller_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('Another Phase 9 controller owns the call stream')
    s=attach()
    # An empty restarted solver has no active iterate command. Distinguish
    # that state from a loaded session whose calculation is running.
    has_mesh=s.settings.setup.cell_zone_conditions.is_active()
    if has_mesh and not s.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Owned Server 3 is busy')
    if args.live_transcript:
        s.transcript.start(file_name=args.live_transcript,write_to_stdout=False)
    if args.action=='source':prepare_source(s)
    elif args.action=='inspect':inspect_target(s,args.label)
    elif args.action=='map':map_target(s,args.label)
    elif args.action=='finish-map':map_target(s,args.label,resume=True)
    elif args.action=='prepare':prepare_child(s,args.label)
    elif args.action=='smoke':run_child(s,args.label,smoke_only=True)
    elif args.action=='run':run_child(s,args.label)
    elif args.action=='campaign':
        try:
            campaign(s)
        finally:
            if args.controller_receipt:
                receipt_path=Path(args.controller_receipt)
                receipt=json.loads(receipt_path.read_text())
                manifest_path=OUT/'campaign-manifest.json'
                manifest=json.loads(manifest_path.read_text())
                receipt.update(status=manifest['status'],active_mesh=manifest.get('active_mesh'),
                               campaign_manifest=str(manifest_path),
                               ended_utc=datetime.now(timezone.utc).isoformat())
                dump(receipt_path,receipt)


if __name__=='__main__':main()
