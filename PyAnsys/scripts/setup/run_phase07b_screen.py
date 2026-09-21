"""Build and execute one authorized Phase 7b thickness, with exact-face evidence.

No C, no pool patch, no transient solve, and no remote session shutdown.
This runner never resumes an uncertain solve automatically.
"""
from prepare_phase07b_collector import *
import re
import numpy as np
from pyansys_fluent.phase07b_flux_monitor import FluxFaceZone, Phase07bFluxMonitor
sys.path.insert(0,str(BASE/'scripts/inspection'))
from export_phase07b_sections import export_sections


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--percent',type=int,choices=list(TOPS),required=True)
    ap.add_argument('--previous-manifest',type=Path)
    ap.add_argument('--iterations',type=int,default=5000);a=ap.parse_args()
    assert 1<=a.iterations<=5000
    run=f'p7b-s{a.percent:03d}-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=BASE/'output'/run;out.mkdir();r={'run_id':run,'percent':a.percent,'requested_iterations':a.iterations,'steps':[], 'status':'BUILDING'}
    r['parent_case']=ROOT+'/case-data/p7b-clean-initial-20260912T080713Z.cas.h5'
    r['report']=ROOT+'/reports/'+run+'.out';r['remote_transcript']=ROOT+'/logs/'+run+'.trn'
    def persist(): (out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
    def timeout(*_):raise TimeoutError('RPC deadline; reconcile before any repeat solve')
    signal.signal(signal.SIGALRM,timeout)
    def step(n,f,sec=90):
        print(n,flush=True);e={'name':n,'state':'STARTED'};r['steps'].append(e);persist();signal.alarm(sec)
        try:v=f();e.update(state='PASS',value=v);return v
        except Exception as x:e.update(state='FAIL',error=str(x));raise
        finally:signal.alarm(0);persist()
    s=None;m=None
    def named(name,d):
        g=s.settings.setup.named_expressions
        if name not in g.get_object_names():g.create(name=name)
        g[name].definition=d;assert g[name].definition()==d
    def nvalue(name):return s.settings.setup.named_expressions[name].get_value()
    def save(tag):
        p=ROOT+'/case-data/'+run+'-'+tag+'.cas.h5';step('save_'+tag,lambda:s.settings.file.write_case_data(file_name=p),180)
        assert all(remote_file_exists(s,p.replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
        r.setdefault('pairs',{})[tag]=p;persist();return p
    try:
        s=step('connect',lambda:connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5),30)
        s.transcript.start(file_name=str(out/'setup.trn'),write_to_stdout=False)
        if a.previous_manifest:
            prior=json.loads(a.previous_manifest.read_text())
            assert prior['status']=='HORIZON_COMPLETE_ANALYSIS_PENDING' and prior['completed_iterations']==5000
            assert nvalue('P7bGlobalIteration')==prior['completed_iterations']
            for name,d in prior['definitions'].items():assert s.settings.setup.named_expressions[name].definition()==d,(name,'unexpected live case')
            assert all(remote_file_exists(s,prior['pairs']['final'].replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
            r['previous_endpoint']={'manifest':str(a.previous_manifest),'final_case':prior['pairs']['final'],'live_iteration_verified':5000,'saved_pair_exists':True};persist()
        step('load_clean_n0',lambda:s.settings.file.read_case_data(file_name=r['parent_case']),180)
        assert nvalue('P7bGlobalIteration')==0
        for name in s.settings.solution.monitor.report_files.get_object_names():s.settings.solution.monitor.report_files[name].active=False
        assert s.settings.setup.general.solver.time()=='steady'
        r['reference_setup']=s.settings.setup.get_state()
        for ph in ['mixture','phase-1','phase-2']:assert not s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources.enable()
        residuals=s.settings.solution.monitor.residual.equations
        for eq in residuals.get_object_names():residuals[eq].check_convergence=False
        r['residual_equations']=residuals.get_state()
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
        defs={k:v.replace(f'["{ZONE}"]',loc) for k,v in definitions(a.percent).items()}
        defs.update({'P7bSplitVolume':'Volume(["p7b-collector"])','P7bSplitMismatch':f'VolumeInt(1-P7bMask,["p7b-collector"])+VolumeInt(P7bMask,["{ZONE}"])',
                     'P7bMinimumPressure':f'Minimum(StaticPressure,{loc})','P7bMaximumPressure':f'Maximum(StaticPressure,{loc})','P7bMaximumSpeed':f'Maximum(VelocityMagnitude(phase="mixture"),{loc})'})
        for name,d in defs.items():step('define_'+name,lambda name=name,d=d:named(name,d))
        assert nvalue('P7bCount')==COUNTS[a.percent]
        assert math.isclose(nvalue('P7bSplitVolume'),VOLUMES[a.percent],rel_tol=1e-9)
        assert nvalue('P7bSplitMismatch')==0
        r['definitions']=defs;r['fluid_zones']=zones;r['interface_proof']={};face_zones=[];all_centroids=[]
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
        # Same fresh Hybrid initialization settings and no liquid patch.
        r['hybrid_options']=s.settings.solution.initialization.hybrid_init_options.get_state()
        step('fresh_hybrid_initialize',lambda:s.settings.solution.initialization.hybrid_initialize(),180)
        assert nvalue('P7bWaterVolume')==0
        initial=save('initial');step('reopen_initial',lambda:s.settings.file.read_case_data(file_name=initial),180)
        assert nvalue('P7bGlobalIteration')==0
        # Reacquire everything after read; source only on exact collector cells.
        for z in zones:
            for ph in ['mixture','phase-1','phase-2']:s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.enable=False
        for ph,terms in HOOKS.items():
            src=s.settings.setup.cell_zone_conditions.fluid['p7b-collector'].phase[ph].sources;src.enable=True
            for eq,ex in terms.items():
                src.terms[eq].resize(size=1);src.terms[eq][0].set_state({'option':'value','value':ex});assert src.terms[eq][0].value()==ex
        r['source_slots']={z:{ph:s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state() for ph in ['mixture','phase-1','phase-2']} for z in zones}
        s.settings.solution.run_calculation.profile_update_interval=1
        skip={'P7bAlpha','P7bMask','P7bK','P7bEpsilon','P7bSink','P7bLiquidX','P7bLiquidY','P7bLiquidZ','P7bSinkX','P7bSinkY','P7bSinkZ','P7bSinkK','P7bSinkEpsilon','P7bCount','P7bGeometryVolume','P7bSplitVolume','P7bSplitMismatch'}
        reports=[]
        for name in defs:
            if name in skip:continue
            rn=name.lower();g=s.settings.solution.report_definitions.single_valued_expression;g.create(name=rn);g[rn].definition=name;reports.append(rn)
        # Native applied source is lagged; retain it separately from S(alpha_N).
        for rn,typ,field in [('p7b-applied-source','volume-sum','phase-2-user-mass-source'),('p7b-native-water','volume-integral','phase-2-vof')]:
            g=s.settings.solution.report_definitions.volume;g.create(name=rn);assert typ in g[rn].report_type.allowed_values();g[rn].set_state({'report_type':typ,'field':field,'cell_zones':zones});reports.append(rn)
        r['sections']={}
        for yy in [.5,1.5,3.,5.]:
            name='p7b-section-y'+str(yy).replace('.','p');g=s.settings.results.surfaces.iso_surface;g.create(name=name);g[name].set_state({'field':'y-coordinate','iso_values':[yy]})
            named('P7bSectionArea'+str(yy).replace('.','p'),f'Area(["{name}"])')
            area=nvalue('P7bSectionArea'+str(yy).replace('.','p'));assert area>0;r['sections'][name]={'y_m':yy,'area_m2':area}
        rf=s.settings.solution.monitor.report_files;rf.create(name='p7b-screen-history');rf['p7b-screen-history'].set_state({'file_name':r['report'],'report_defs':reports,'frequency':1,'active':True})
        r['report_definitions']=s.settings.solution.report_definitions.get_state();r['initial_metrics']=step('initial_metrics',lambda:s.settings.solution.report_definitions.compute(report_defs=reports))
        prepared=save('prepared');step('reopen_prepared',lambda:s.settings.file.read_case_data(file_name=prepared),180)
        assert nvalue('P7bGlobalIteration')==0 and nvalue('P7bWaterVolume')==0
        for name,d in defs.items():assert s.settings.setup.named_expressions[name].definition()==d
        for z in zones:
            for ph in ['mixture','phase-1','phase-2']:assert s.settings.setup.cell_zone_conditions.fluid[z].phase[ph].sources.get_state()==r['source_slots'][z][ph]
        r['initial_sections']=step('extract_initial_sections',lambda:export_sections(s,r['sections'],out/'initial-sections'),180)
        s.transcript.stop();setup=(out/'setup.trn').read_text();assert 'SEGMENTATION VIOLATION' not in setup
        counts=re.findall(r'^\s*0\s+(620431)\s+(2852567)\s+(\d+)\s+(16)\s*$',setup,re.M);assert len(counts)>=2 and counts[0]==counts[1]
        s.transcript.start(file_name=str(out/'solve.trn'),write_to_stdout=False)
        step('start_remote_transcript',lambda:s.settings.file.start_transcript(file_name=r['remote_transcript']))
        m=Phase07bFluxMonitor(s,face_zones=face_zones,start_iteration=0,local_jsonl=out/'collector-flux.jsonl',remote_directory=ROOT+'/reports');m.register()
        r['status']='RUNNING';r['flux_monitor']=m.manifest();persist()
        targets=sorted(set([min(50,a.iterations)]+list(range(500,a.iterations+1,500))+[a.iterations]));current=0
        for target in targets:
            step(f'iterate_{current}_to_{target}',lambda target=target,current=current:s.settings.solution.run_calculation.iterate(iter_count=target-current),max(600,(target-current)*20))
            actual=int(nvalue('P7bGlobalIteration'));r['actual_iteration']=actual;assert actual==target,(actual,target)
            m.assert_complete(actual);r['flux_monitor']=m.manifest()
            # Verify the durable last row and complete native scalar history.
            last=json.loads((out/'collector-flux.jsonl').read_text().splitlines()[-1]);assert json.loads(read_text(s,last['remote_path']))==last
            r.setdefault('remote_flux_readbacks',[]).append({'iteration':actual,'path':last['remote_path'],'matches_local':True})
            history=read_text(s,r['report']);(out/f'history-{actual:05d}.out').write_text(history)
            rows=np.loadtxt(history.splitlines(),skiprows=3);rows=np.atleast_2d(rows)
            assert np.array_equal(rows[:,0],np.arange(1,actual+1));assert np.isfinite(rows).all()
            solve=(out/'solve.trn').read_text();assert not any(x in solve for x in ['SEGMENTATION VIOLATION','floating point exception','Divergence detected'])
            r['latest_metrics']=step(f'metrics_{actual}',lambda:s.settings.solution.report_definitions.compute(report_defs=reports))
            save('final' if actual==a.iterations else f'n{actual:05d}');current=actual;persist()
        m.unregister();r['flux_monitor']=m.manifest();m=None
        r['final_sections']=step('extract_final_sections',lambda:export_sections(s,r['sections'],out/'final-sections'),180)
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
        persist();print('EVIDENCE',out,flush=True)
if __name__=='__main__':main()
