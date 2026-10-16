"""Server5 only: preserve150ms slit pairs, apply recorded Planv1 and reach500ms.

The two designs run serially. A verified500ms pair precedes the next case load.
No socket or solver operation runs at import time.
"""
from pathlib import Path, PureWindowsPath
import argparse, hashlib, json, math, os, re, sys, time, traceback
ROOT=Path(__file__).resolve().parents[2]
DEPS=Path(os.environ.get('P4P_SERVER5_DEPS',str(ROOT.parents[1]/'runtime-deps')))
if DEPS.is_dir():sys.path.insert(0,str(DEPS))
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from phase9_server5_common import attach,run
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.ewf_staged import refresh_plan,FILM,FATAL,history
from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.stage4_native import exclusive_writer_lock
from run_phase72a_stage4_ewf_drain import facets as raw_facets,same_facets,define_reports,compute
from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest,SurfaceDataType
import numpy as np
OUT=ROOT/'output/phase10-proposed-design/20261015/server5-planv1-to500ms'


def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp-'+str(os.getpid()));temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)

def quote(value):return "'"+str(value).replace("'","''")+"'"

def config():
    result=json.loads((OUT/'campaign-config.json').read_text());assert result['server_id']=='5'
    return result

def idle(s):
    run.require_idle(s)
    assert not s.settings.solution.run_calculation.iterating(),'Server5 native solve active; observe, do not replace'

def connect():
    s=attach();run.OUT=OUT
    profile=PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")'))
    return s,profile/'Documents/FluentRuns/Phase10-Server5-slit-planv1-500ms/20261015'

def select_work(s,root,case):
    run.WORK=root/case['id'];run.ensure_remote_directory(s,str(run.WORK/'scratch'))

def facets(s,wall):
    values=raw_facets(s,wall)
    geometry=np.asarray(s.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=[wall],data_types=[SurfaceDataType.FacesCentroid]))[wall].face_centroids)
    assert len(np.unique(geometry,axis=0))==len(geometry)
    order=np.lexsort(geometry.T[::-1])
    return {key:value[order] for key,value in values.items()}

def snapshot(s):
    return {'iteration':run.native_iteration(s),'film':run.film(s),'parameters':dict(s.rp_vars('wall-film/model-parameters')),
            'equations':s.settings.solution.controls.equations.get_state(),'bulk':compute(s,['v2-total-liquid-mass','v2-total-vapor-mass','v2-total-liquid-volume'])}

def assert_inventories(a,b):
    assert a.keys()==b.keys()
    for key,v in a.items():assert math.isclose(v[0],b[key][0],rel_tol=1e-9,abs_tol=1e-9),key

def audit(s,parameters,bulk):
    assert dict(s.rp_vars('wall-film/model-parameters'))==parameters,'EWF parameters differ'
    eq=s.settings.solution.controls.equations.get_state();assert all(v==bulk for v in eq.values())
    run.require_bulk_audit(s);run.read_feed(s,1.0);d=drain.audit(s,True)
    for name in s.settings.setup.boundary_conditions.wall.get_object_names():
        obj=s.settings.setup.boundary_conditions.wall[name].phase['mixture']
        assert math.isclose(obj.turbulence.roughness_height()['value'],0 if name=='bottom' else 4.5e-5,abs_tol=1e-12)
        assert math.isclose(obj.turbulence.roughness_const()['value'],.5,abs_tol=1e-12)
        if name in ['wall',drain.WALL]:
            w=obj.wall_film.get_state();assert w['eulerian_film_wall'] and not w['enable_flow_momentum_coupling']
            assert w['enable_dpm_wall_splash'] and w['allow_film_boundary_separation']
    return d

def instrument(s,label):
    folder=run.WORK/'monitors'/label;run.ensure_remote_directory(s,str(folder));paths={}
    files=s.settings.solution.monitor.report_files
    for name,value in files.get_state().items():
        if not value.get('active'):continue
        assert len(value['report_defs'])==1
        path=str(folder/(name+'.out'));files[name].file_name=path;files[name].frequency=1;files[name].frequency_of='iteration'
        paths[value['report_defs'][0]]=path
    return paths

def read_local_or_remote(s,path):
    p=Path(path)
    return p.read_text(errors='replace') if os.name=='nt' and p.is_file() else run.read_text(s,path)

def save_reload(s,label,parameters,bulk):
    idle(s);before=snapshot(s);pair=run.save(s,run.WORK,label);run.load(s,pair)
    after=snapshot(s);assert after['iteration']==before['iteration']
    assert abs(after['film']['film_elapsed_time']-before['film']['film_elapsed_time'])<1e-10
    assert_inventories(before['bulk'],after['bulk']);audit(s,parameters,bulk)
    return pair

def schedule(clock):
    stages=[['planv1-smoke',10,1e-7,True],['bulk-adjustment',1490,1e-7,True],
            ['frozen-transition',1000,1e-7,False],['step-2p5us',1000,2.5e-6,False]]
    now=clock+sum(n*dt for _,n,dt,_ in stages)
    remaining=round((.5-now)/2.5e-6);assert remaining>0 and abs(now+remaining*2.5e-6-.5)<1e-10
    i=0
    while remaining:
        n=min(10000,remaining);stages.append(['frozen-growth-'+str(i+1),n,2.5e-6,False]);remaining-=n;i+=1
    return stages

def share_pair(s,pair,case_id,label):
    folder=run.SHARED/'P4P-Fluent-Artifacts/Phase10/planv1-500ms-server5'/case_id/(label+'-N'+str(pair['native_iteration'])+'-'+str(time.time_ns()))
    run.ensure_remote_directory(s,str(folder));shared={}
    for key,ext in [('case','cas.h5'),('data','dat.h5')]:
        target=folder/(label+'-N'+str(pair['native_iteration'])+'.'+ext)
        run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(pair[key])+' -Destination '+quote(target))
        digest=run.remote_file_sha256(s,str(target),str(run.WORK/'scratch'/('share-'+key+'-'+str(time.time_ns())+'.txt')))
        assert digest==pair[key+'_sha256'];shared[key]=str(target);shared[key+'_sha256']=digest
    return shared

def prepare(s,root,case):
    cfg=config();ev=OUT/case['id'];ev.mkdir(parents=True,exist_ok=True)
    assert not (ev/'prepared.json').exists(),'Existing preparation must be reconciled; no replay'
    idle(s);old_work=run.WORK
    # Preserve the actually loaded endpoint before replacing it, including failure evidence.
    prior=run.save(s,old_work,'preserved-before-'+case['id']+'-planv1-'+str(time.time_ns()))
    dump(ev/'preservation.json',{'status':'PREVIOUS_NATIVE_ENDPOINT_PRESERVED','pair':prior,'film':run.film(s)})
    if s.settings.file.stop_transcript.is_active():s.settings.file.stop_transcript()
    select_work(s,root,case);stamp=str(time.time_ns());source=dict(case['parent'])
    for key,ext in [('case','cas.h5'),('data','dat.h5')]:
        shared=run.SHARED/PureWindowsPath(source[key+'_shared_relative']);target=run.WORK/('source150-N'+str(source['native_iteration'])+'.'+ext)
        assert not run.remote_file_exists(s,str(target))
        digest=run.remote_file_sha256(s,str(shared),str(run.WORK/'scratch'/('source-'+key+'-'+stamp+'.txt')));assert digest==source[key+'_sha256']
        run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(shared)+' -Destination '+quote(target))
        assert run.remote_file_sha256(s,str(target),str(run.WORK/'scratch'/('copy-'+key+'-'+stamp+'.txt')))==digest
        source[key]=str(target)
    library=run.WORK/'libcontactv2';assert not run.remote_file_exists(s,str(library))
    # Identical existing contact UDF runtime from Server5; no compile or model change.
    run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(old_work/'libcontactv2')+' -Destination '+quote(library)+' -Recurse')
    dump(ev/'preparation-state.json',{'status':'SOURCE_STAGED_LOAD_PENDING','source':source,'previous_pair':prior})
    run.load(s,source);before=snapshot(s)
    assert before['iteration']==case['parent']['native_iteration'] and abs(before['film']['film_elapsed_time']-case['parent_film_s'])<1e-10
    upper=facets(s,'wall');np.savez_compressed(ev/'source-upper-film.npz',**upper)
    # Allocate new lower-film storage, then restore all existing data and upper-film fields.
    lower=s.settings.setup.boundary_conditions.wall[drain.WALL].phase['mixture'].wall_film
    assert not lower.eulerian_film_wall();lower.eulerian_film_wall=True
    lower.film_condition_type='film-wall-initial';lower.film_height.set_state({'option':'value','value':0.0})
    lower.enable_film_source_terms=False;lower.enable_flow_momentum_coupling=False
    s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model();s.settings.file.read_data(file_name=source['data'])
    same_facets(upper,facets(s,'wall'))
    assert max(abs(x) for x in facets(s,drain.WALL)['film-mass'])<1e-12
    assert abs(run.film(s)['film_elapsed_time']-case['parent_film_s'])<1e-10
    run.apply_approved_bulk(s)
    for name in s.settings.setup.boundary_conditions.wall.get_object_names():
        t=s.settings.setup.boundary_conditions.wall[name].phase['mixture'].turbulence
        t.roughness_height=0.0 if name=='bottom' else 4.5e-5;t.roughness_const=.5
    expected=cfg['parameter_template'];actual=dict(s.rp_vars('wall-film/model-parameters'))
    assert expected.keys()==actual.keys(),'Version-matched EWF parameter inventory differs'
    s.rp_vars('wall-film/model-parameters',list(expected.items()))
    s.tui.define.models.eulerian_wallfilm.model_options(*run.MODEL_ARGS)
    s.rp_vars('wall-film/model-parameters',list(expected.items()))
    for name in ['wall',drain.WALL]:
        w=s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film
        w.enable_flow_momentum_coupling=False;w.enable_dpm_wall_splash=True;w.allow_film_boundary_separation=True
    drain.configure(s,enabled=True,refresh_span_s=1e-7)
    eq=s.settings.solution.controls.equations.get_state();s.settings.solution.controls.equations.set_state({k:True for k in eq})
    define_reports(s);instrument(s,'prepared')
    same_facets(upper,facets(s,'wall'));assert_inventories(before['bulk'],snapshot(s)['bulk'])
    # Stored interaction-domain readback is refreshed by paired persistence.
    pair=run.save(s,run.WORK,'prepared-planv1-N'+str(before['iteration'])+'-'+stamp);run.load(s,pair)
    audit(s,expected,True);same_facets(upper,facets(s,'wall'))
    assert_inventories(before['bulk'],snapshot(s)['bulk'])
    assert run.native_iteration(s)==before['iteration'] and abs(run.film(s)['film_elapsed_time']-before['film']['film_elapsed_time'])<1e-10
    autosave=s.settings.file.auto_save;autosave.case_frequency='each-time';autosave.data_frequency=1000
    autosave.root_name=str(run.WORK/'planv1-auto-%i');autosave.retain_most_recent_files=False
    record={'status':'PREPARED_REOPEN_VERIFIED','case_id':case['id'],'server_id':'5','source_pair':source,'pair':pair,
            'native_iteration':before['iteration'],'film_s':before['film']['film_elapsed_time'],'parameters':expected,
            'bulk_active':True,'original_upper_film_exact':True,'new_lower_film_initial_mass_kg':0,
            'original_bulk_inventories_preserved':True,'schedule':schedule(before['film']['film_elapsed_time']),
            'host_work':str(run.WORK),'target_film_s':.5,'model_plan_sha256':cfg['plan_sha256'],'numerical_thresholds':None}
    record['shared_pre_run_pair']=share_pair(s,pair,case['id'],'prepared150ms-planv1')
    dump(ev/'prepared.json',record)
    return record

def case_run(s,root,case,prepared,resumed=None):
    select_work(s,root,case);ev=OUT/case['id'];path=ev/'run-manifest.json'
    assert resumed is not None or not path.exists(),'Reconcile an existing native command; no replay'
    m=resumed if resumed is not None else {'status':'READY','case_id':case['id'],'server_id':'5','verified_native_end':prepared['native_iteration'],
       'accepted_film_s':prepared['film_s'],'latest_pair':prepared['pair'],'parameters':prepared['parameters'],
       'bulk_active':True,'blocks':[],'target_film_s':.5,'target_native_iteration':prepared['native_iteration']+sum(x[1] for x in prepared['schedule'])}
    if resumed is not None:
        assert m['status']=='RECOVERY_REOPEN_VERIFIED' and m['case_id']==case['id']
        m['target_native_iteration']=m['verified_native_end']+sum(x[1] for x in prepared['schedule'])
    dump(path,m)
    for label,count,dt,bulk in prepared['schedule']:
        idle(s);assert run.native_iteration(s)==m['verified_native_end']
        assert abs(run.film(s)['film_elapsed_time']-m['accepted_film_s'])<1e-10
        desired=dict(m['parameters']);desired.update(refresh_plan(dt))
        scale=prepared.get('bulk_pseudo_time_recovery_scale') if bulk else prepared.get('restore_bulk_pseudo_time_scale')
        scale_obj=s.settings.solution.run_calculation.pseudo_time_settings.time_step_method.time_step_size_scale_factor if scale is not None else None
        scale_changed=scale is not None and scale_obj.get_state()!=scale
        if desired!=m['parameters'] or bulk!=m['bulk_active'] or scale_changed:
            if scale is not None:scale_obj.set_state(scale)
            s.rp_vars('wall-film/model-parameters',list(desired.items()))
            s.settings.setup.named_expressions['P72dRefreshSpan'].definition=f'{dt:.17g}[s]'
            eq=s.settings.solution.controls.equations.get_state();s.settings.solution.controls.equations.set_state({k:bulk for k in eq})
            m['last_activation_pair']=save_reload(s,'activated-'+label+'-'+str(time.time_ns()),desired,bulk)
            m.update(parameters=desired,bulk_active=bulk)
        if scale is not None:assert math.isclose(scale_obj.get_state(),scale,abs_tol=1e-12)
        audit(s,desired,bulk)
        before=snapshot(s);initial=compute(s,['p72d-total-mass','p72d-total-outflow','p72d-total-stripped','p72d-total-separated'])
        stamp=str(time.time_ns());stem=label+'-N'+str(m['verified_native_end']+count)+'-'+stamp
        paths=instrument(s,stem);transcript=str(run.WORK/(stem+'.trn'));journal=str(run.WORK/(stem+'.jou'))
        code='\n'.join(['/file/start-transcript "'+transcript.replace('\\','/')+'"','/solve/iterate '+str(count),'/file/write-case-data "'+str(run.WORK/(stem+'.cas.h5')).replace('\\','/')+'"','/file/stop-transcript',''])
        run.write_ascii_text_new(s,journal,code)
        m.update(status='RUNNING',active_stage=label,active_target=m['verified_native_end']+count,active_journal=journal,active_transcript=transcript,active_step_s=dt,report_paths=paths)
        dump(path,m);dump(OUT/'run-manifest.json',{'status':'RUNNING','server_id':'5','active_case':case['id'],'case_manifest':str(path),'target_film_s':.5,'active_stage':label,'active_target':m['active_target'],'verified_native_end':m['verified_native_end'],'accepted_film_s':m['accepted_film_s']})
        s.scheme.eval('(ti-menu-load-string "'+quote_scheme_string('/file/read-journal "'+journal.replace('\\','/')+'"')+'")')
        end=run.native_iteration(s)
        if end!=m['active_target']:
            partial=run.save(s,run.WORK,'preserved-partial-'+stamp);m.update(status='RECOVERY_REQUIRED',partial_pair=partial,partial_film=run.film(s));dump(path,m);raise RuntimeError('Native command ended early; partial preserved; never replay')
        text=read_local_or_remote(s,transcript);rows=[list(map(float,x.groups())) for x in FILM.finditer(text)]
        assert not FATAL.search(text) and len(rows)==count
        assert all(math.isclose(row[1],dt,abs_tol=1e-12) for row in rows)
        pair={'native_iteration':end,'case':str(run.WORK/(stem+'.cas.h5')),'data':str(run.WORK/(stem+'.dat.h5'))}
        for key in ['case','data']:pair[key+'_sha256']=run.remote_file_sha256(s,pair[key],str(run.WORK/'scratch'/(stem+'-'+key+'.txt')))
        run.load(s,pair);after=snapshot(s);audit(s,desired,bulk)
        target=m['accepted_film_s']+count*dt;assert abs(after['film']['film_elapsed_time']-target)<1e-10
        if not bulk:assert_inventories(before['bulk'],after['bulk'])
        block={'stage':label,'count':count,'dt':dt,'bulk_active':bulk,'native_end':end,'film_end_s':target,'pair':pair,'transcript':transcript,'film_rows':len(rows),'peak_courant_diagnostic':max(row[2] for row in rows)}
        if scale is not None:block['bulk_pseudo_time_scale_factor']=scale_obj.get_state()
        if label=='frozen-transition':
            names=['p72d-drain-rate','p72d-total-secondary','p72d-total-dpm','p72d-total-mass','p72d-total-outflow','p72d-total-stripped','p72d-total-separated']
            histories={n:history(read_local_or_remote(s,paths[n])) for n in names};ids=list(range(before['iteration']+1,end+1))
            assert all(all(i in histories[n] for i in ids) for n in names),'Missing frozen probe instrumentation'
            removal=sum(histories['p72d-drain-rate'][i] for i in ids)*dt
            supply=sum(sum(histories[n][i] for i in ids)*dt for n in ['p72d-total-secondary','p72d-total-dpm'])
            final={n:histories[n][end] for n in initial};departure=sum(final[n]-initial[n][0] for n in initial)
            separated=final['p72d-total-separated']-initial['p72d-total-separated'][0]
            probe={'status':'FROZEN_BULK_DIRECT_DRAIN_PROVED' if removal>0 else 'DIRECT_DRAIN_REMOVAL_NOT_OBSERVED','film_updates':count,'added_film_s':count*dt,'direct_removal_kg':removal,'positive_direct_removal':removal>0,'bulk_inventories_unchanged':True,'gross_ledger_residual_kg':departure+removal-supply,'v252_net_secondary_residual_kg':departure+removal-supply-separated,'ledger_diagnostic_only':True,'drain_audit':drain.audit(s,True)}
            dump(ev/'frozen-drain-proof.json',probe)
            assert removal>0,'Direct film removal not observed; inspect technical drain path before long growth'
        m['blocks'].append(block);m.update(status='CHECKPOINT_VERIFIED',verified_native_end=end,accepted_film_s=target,latest_pair=pair,active_target=None)
        dump(path,m)
    assert abs(m['accepted_film_s']-.5)<1e-10 and not any(s.settings.solution.controls.equations.get_state().values())
    shared=run.SHARED/'P4P-Fluent-Artifacts/Phase10/planv1-500ms-server5'/case['id']/('final500ms-N'+str(m['verified_native_end'])+'-'+str(time.time_ns()))
    run.ensure_remote_directory(s,str(shared));copies={}
    for key,ext in [('case','cas.h5'),('data','dat.h5')]:
        dest=shared/('final500ms-N'+str(m['verified_native_end'])+'.'+ext)
        run.base.powershell(s,"$ErrorActionPreference='Stop'; Copy-Item -LiteralPath "+quote(m['latest_pair'][key])+' -Destination '+quote(dest))
        digest=run.remote_file_sha256(s,str(dest),str(run.WORK/'scratch'/('shared-'+key+'-'+str(time.time_ns())+'.txt')));assert digest==m['latest_pair'][key+'_sha256'];copies[key]=str(dest);copies[key+'_sha256']=digest
    m.update(status='COMPLETE_500MS_REOPEN_AND_SHARED_HASH_VERIFIED',shared_pair=copies,final_film=run.film(s),active_stage=None);dump(path,m)
    return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--prepare-first',action='store_true');args=p.parse_args();cfg=config()
    with exclusive_writer_lock(OUT/'controller.lock'):
        s,root=connect();idle(s)
        if args.prepare_first:
            assert not (OUT/'prepared-first.json').exists()
            record=prepare(s,root,cfg['cases'][0]);dump(OUT/'prepared-first.json',record)
            dump(OUT/'run-manifest.json',{'status':'READY','server_id':'5','active_case':cfg['cases'][0]['id'],'target_film_s':.5});return
        m=json.loads((OUT/'run-manifest.json').read_text());assert m['status']=='READY','Existing campaign requires reconciliation, not replay'
        completed=[]
        try:
            for index,case in enumerate(cfg['cases']):
                prep=json.loads((OUT/'prepared-first.json').read_text()) if index==0 else prepare(s,root,case)
                result=case_run(s,root,case,prep);completed.append({'case_id':case['id'],'native_iteration':result['verified_native_end'],'film_s':result['accepted_film_s'],'shared_pair':result['shared_pair']})
                # Only a verified, shared500ms endpoint permits replacing this case.
                assert result['status']=='COMPLETE_500MS_REOPEN_AND_SHARED_HASH_VERIFIED'
                dump(OUT/'run-manifest.json',{'status':'CASE_COMPLETE' if index+1<len(cfg['cases']) else 'COMPLETE_BOTH_500MS','server_id':'5','completed':completed,'active_case':None,'target_film_s':.5,'fluent_left_open':True})
        except BaseException:
            dump(OUT/'campaign-error.json',{'status':'RECOVERY_REQUIRED','server_id':'5','error':traceback.format_exc(),'completed':completed,'no_timeout_replay':True,'preserve_fluent':True})
            current=json.loads((OUT/'run-manifest.json').read_text());current.update(status='RECOVERY_REQUIRED',error_evidence=str(OUT/'campaign-error.json'));dump(OUT/'run-manifest.json',current);raise

if __name__=='__main__':main()
