"""Disposable exact-cell collector-interface capability proof; no solution iterations."""
from prepare_phase07b_collector import *
import numpy as np

def main():
    run='p7b-interface-proof-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=BASE/'output/phase07b_preparation'/run;out.mkdir();r={'run_id':run,'steps':[]}
    def timeout(*_):raise TimeoutError('interface proof RPC deadline')
    signal.signal(signal.SIGALRM,timeout)
    def step(n,f,seconds=90):
        print(n,flush=True);e={'name':n};r['steps'].append(e);signal.alarm(seconds)
        try:v=f();e.update(state='PASS',value=v);return v
        except Exception as x:e.update(state='FAIL',error=str(x));raise
        finally:signal.alarm(0);(out/'result.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
    s=step('connect',lambda:connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5),30)
    s.transcript.start(file_name=str(out/'probe.trn'),write_to_stdout=False)
    parent=ROOT+'/case-data/p7b-source-proof-s20-20260918T063831Z-final.cas.h5'
    r['parent']=parent
    step('load_preserved_n50',lambda:s.settings.file.read_case_data(file_name=parent),120)
    for name in s.settings.solution.monitor.report_files.get_object_names():s.settings.solution.monitor.report_files[name].active=False
    for ph in ['mixture','phase-1','phase-2']:s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources.enable=False
    def variable(zone,var,domain):
        a=s.fields.solution_variable_data.get_data(variable_name=var,zone_names=[zone],domain_name=domain)[zone]
        np.save(out/f'{zone}-{domain}-{var}.npy',a)
        return {'size':a.size,'sum':float(a.sum()),'min':float(a.min()),'max':float(a.max()),'positive':float(a[a>0].sum()),'negative':float(a[a<0].sum())}
    step('known_inlet_phase_flux',lambda:variable('liquid-inlet','SV_FLUX','phase-2'))
    step('known_outlet_phase_flux',lambda:variable('steam-outlet','SV_FLUX','phase-2'))
    step('mesh_before',lambda:s.settings.mesh.size_info())
    regs=s.settings.solution.cell_registers;regs.create(name='p7b_exact_s20')
    regs['p7b_exact_s20'].set_state({'type':{'option':'hexahedron','hexahedron':{'min_point':[-100,-1.4845837354660034,-100],'max_point':[100,TOPS[20],100],'inside':True}}})
    step('register_readback',lambda:regs['p7b_exact_s20'].get_state())
    before=s.settings.setup.cell_zone_conditions.fluid.get_object_names()
    step('separate_centroid_mask',lambda:s.settings.mesh.modify_zones.sep_cell_zone_mark(cell_zone_name=ZONE,register='p7b_exact_s20',move_faces=True),120)
    after=s.settings.setup.cell_zone_conditions.fluid.get_object_names();new=list(set(after)-set(before));assert len(new)==1,new
    step('rename_collector',lambda:s.settings.mesh.modify_zones.zone_name(zone_name=new[0],new_name='p7b-collector'))
    step('mesh_after',lambda:s.settings.mesh.size_info())
    step('mesh_check',lambda:s.settings.mesh.check())
    info=s.fields.solution_variable_info.get_zones_info()
    r['zones']={n:{'id':info[n].zone_id,'type':info[n].zone_type,'count':info[n].count} for n in info.zone_names}
    assert info['p7b-collector'].count==COUNTS[20],r['zones']
    n=s.settings.setup.named_expressions
    for name,d in {'P7bSplitVolume':'Volume(["p7b-collector"])','P7bSplitMismatch':f'VolumeInt(1-P7bMask,["p7b-collector"])+VolumeInt(P7bMask,["{ZONE}"])'}.items():
        n.create(name=name);n[name].definition=d;step(name,lambda name=name:n[name].get_value())
    assert math.isclose(n['P7bSplitVolume'].get_value(),VOLUMES[20],rel_tol=1e-9)
    assert n['P7bSplitMismatch'].get_value()==0
    interiors=s.settings.setup.boundary_conditions.interior.get_object_names()
    r['interiors']={}
    for face in interiors:
        r['interiors'][face]=s.settings.setup.boundary_conditions.interior[face].get_state()
        vars=s.fields.solution_variable_info.get_variables_info(zone_names=[face],domain_name='phase-2').solution_variables
        r['interiors'][face]['variables']=vars
        if info[face].count<100000:
            step('orient_'+face,lambda face=face:s.settings.setup.boundary_conditions.orient_face_zone(zone_name=face))
            for var in ['SV_FLUX','SV_AREA','SV_CENTROID']:
                if var in vars:step(face+'_'+var,lambda face=face,var=var:variable(face,var,'phase-2'))
    r['saved_case']=ROOT+'/case-data/'+run+'.cas.h5'
    step('save_disposable_pair',lambda:s.settings.file.write_case_data(file_name=r['saved_case']),120)
    s.transcript.stop();r['status']='GEOMETRIC_SPLIT_PASS_FLUX_REVIEW_REQUIRED'
    (out/'result.json').write_text(json.dumps(r,indent=2,default=str)+'\n');print('EVIDENCE',out)
if __name__=='__main__':main()
