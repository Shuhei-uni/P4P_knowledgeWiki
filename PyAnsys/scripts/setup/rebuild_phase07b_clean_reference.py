"""Rebuild the approved Phase7b carrier from the clean mesh; no UDFs or solve.

Only selected audited reference fields are replayed. Never load the old case.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, signal, sys, traceback
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'src'))
from dotenv import load_dotenv
load_dotenv(BASE/'.env')
from pyansys_fluent.connection import connect
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.common import remote_file_exists
ZONE='simple-spiral-separator--brine-outlet-'
ROOT='C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal'

def subset(expected,actual,path=''):
    if isinstance(expected,dict):
        for k,v in expected.items():
            assert k in actual, f'Missing {path}.{k}'
            subset(v,actual[k],path+'.'+k)
    else:
        assert expected==actual, f'Mismatch {path}: expected {expected!r}, got {actual!r}'

def main():
    p=BASE/'output/phase07b_preparation'; old=json.loads((p/'reference-preparation-save-reload.json').read_text())['before']
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    r={'stamp':stamp,'source':'clean original mesh plus audited Phase7b settings','status':'CONNECTING','applied':[],'case':ROOT+'/case-data/p7b-clean-reference-'+stamp+'.cas.h5','transcript':ROOT+'/logs/p7b-clean-reference-'+stamp+'.trn'}
    out=p/'clean-reference-rebuild.json'
    def persist(): out.write_text(json.dumps(r,indent=2,default=str)+'\n')
    def stage(x): r['status']=x; persist(); print(x,flush=True)
    signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('API deadline')))
    signal.alarm(30); s=connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5); signal.alarm(0)
    assert s.settings.setup.cell_zone_conditions.fluid.get_object_names()==[ZONE]
    assert s.settings.setup.user_defined.auto_compile_compiled_functions() is False
    assert s.settings.setup.user_defined.memory.memory_locations()==0
    assert s.settings.setup.models.multiphase.model()=='none'
    s.settings.file.start_transcript(file_name=r['transcript'])
    checks=[]
    def setcheck(path,value):
        obj=s.settings
        for bit in path.split('.'): obj=getattr(obj,bit)
        obj.set_state(value); subset(value,obj.get_state(),path); checks.append((path,value)); r['applied'].append(path); persist()
    try:
        stage('GENERAL_AND_MATERIALS')
        setcheck('setup.general.solver',old['general']['solver'])
        setcheck('setup.general.operating_conditions.gravity',old['general']['operating_conditions']['gravity'])
        setcheck('setup.general.operating_conditions.operating_pressure',0)
        setcheck('setup.models.energy',{'enabled':False})
        setcheck('setup.models.viscous.model','k-epsilon')
        setcheck('setup.models.viscous.k_epsilon_model','rng')
        setcheck('setup.models.viscous.rng',old['viscous']['rng'])
        setcheck('setup.models.viscous.near_wall_treatment',old['viscous']['near_wall_treatment'])
        setcheck('setup.models.viscous.options',old['viscous']['options'])
        for name in ['water-vapor-purnanto2013','water-liquid-purnanto2013']:
            mats=s.settings.setup.materials.fluid
            if name not in mats.get_object_names(): mats.create(name=name)
            mats[name].set_state(old['materials'][name]); subset(old['materials'][name],mats[name].get_state(),name)
        stage('MIXTURE_AND_BOUNDARIES')
        setcheck('setup.models.multiphase.model','mixture')
        for ph,mat in [('phase-1','water-vapor-purnanto2013'),('phase-2','water-liquid-purnanto2013')]:
            s.settings.setup.models.multiphase.phases[ph].material=mat
            assert s.settings.setup.models.multiphase.phases[ph].material()==mat
        if 'brine-outlet' not in s.settings.setup.boundary_conditions.wall.get_object_names():
            s.settings.setup.boundary_conditions.set_zone_type(zone_list=['brine-outlet'],new_type='wall')
        for kind in ['velocity_inlet','pressure_outlet','wall']:
            for name,value in old['boundaries'][kind].items():
                getattr(s.settings.setup.boundary_conditions,kind)[name].set_state(value)
                subset(value,getattr(s.settings.setup.boundary_conditions,kind)[name].get_state(),name)
        setcheck('setup.general.operating_conditions.operating_density',old['general']['operating_conditions']['operating_density'])
        stage('NUMERICS_AND_INITIALIZATION_SETTINGS')
        for key in ['p_v_coupling','spatial_discretization','pseudo_time_method']:
            setcheck('solution.methods.'+key,old['methods'][key])
        setcheck('solution.controls.under_relaxation',old['controls']['under_relaxation'])
        setcheck('solution.controls.equations',old['controls']['equations'])
        setcheck('solution.controls.limits',old['controls']['limits'])
        setcheck('solution.initialization',old['initialization'])
        setcheck('setup.models.discrete_phase.general_settings.interaction.enabled',False)
        assert s.settings.setup.models.discrete_phase.injections.get_object_names()==[]
        for ph in ['mixture','phase-1','phase-2']:
            s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources.enable=False
        def snap():
            return {'solver':s.settings.setup.general.solver.get_state(),'operating':s.settings.setup.general.operating_conditions.get_state(),'materials':s.settings.setup.materials.fluid.get_state(),'multiphase':s.settings.setup.models.multiphase.get_state(),'viscous':s.settings.setup.models.viscous.get_state(),'boundaries':s.settings.setup.boundary_conditions.get_state(),'methods':s.settings.solution.methods.get_state(),'controls':s.settings.solution.controls.get_state(),'initialization':s.settings.solution.initialization.get_state(),'udf':s.settings.setup.user_defined.get_state(),'domains':s.rp_vars('domains')}
        r['before']=snap(); stage('SAVING_CLEAN_REFERENCE')
        s.settings.file.write_case(file_name=r['case']); assert remote_file_exists(s,r['case'])
        stage('REOPENING_CLEAN_REFERENCE'); signal.alarm(120)
        s.settings.file.read_case(file_name=r['case']); signal.alarm(0)
        r['after']=snap(); r['exact_readback_equal']=r['before']==r['after']
        # The Cortex copy of domains can be empty until a case read synchronizes
        # it. Compare Settings configuration exactly; inspect solver-domain
        # physics separately rather than treating lazy metadata as setup drift.
        r['settings_readback_equal']={k:v for k,v in r['before'].items() if k!='domains'}=={k:v for k,v in r['after'].items() if k!='domains'}
        assert r['settings_readback_equal']
        stage('READBACK_PASS')
    except Exception as exc:
        signal.alarm(0); r['error']=str(exc); (p/'clean-reference-error.txt').write_text(traceback.format_exc()); stage('BLOCKED')
        raise
    finally:
        s.settings.file.stop_transcript()
        txt=read_text(s,r['transcript']); (p/'clean-reference-rebuild.trn').write_text(txt)
        r['cortex_fault_count']=txt.count('SEGMENTATION VIOLATION'); r['compilation_attempted']='C sources:' in txt
        if r['cortex_fault_count']: r['status']='CORTEX_FAULT'
        persist()
    assert r['cortex_fault_count']==0 and not r['compilation_attempted']
    print('CLEAN_REFERENCE_SAVE_REOPEN_PASS',r['case'],flush=True)
if __name__=='__main__': main()
