"""Local, single-owner execution of the human-selected Phase 9 60k EWF pilot.

Invoked with an already live direct-fluent-use solver. Never launches/exits it.
Native journals own fixed solves; observation uses local files only.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import shutil
import statistics
import time
import traceback

import numpy as np
from ansys.fluent.core.fields.field_data_interfaces import ScalarFieldDataRequest
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent import ewf_staged as policy
from pyansys_fluent.stage4_native import configure_autosave

FILM = [n for n in policy.FILM_REPORTS if n != 'p72d-upper-mass']
BULK = ['v2-total-liquid-mass', 'v2-total-vapor-mass',
        'v2-flux-phase2-steamoutlet', 'v2-flux-phase1-steamoutlet',
        'p72s3-pressure-inlet', 'p72s3-pressure-outlet', 'v2-applied-absorber']


def dump(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, default=str, allow_nan=False)+'\n')
    temporary.replace(path)


class Pilot:
    def __init__(self, solver, repo, parent):
        self.s, self.repo, self.parent = solver, Path(repo), Path(parent)
        self.work = Path(r'C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse') / ('phase9-60k-ewf-'+time.strftime('%Y%m%d-%H%M%S'))
        self.work.mkdir(exist_ok=False)
        self.m = {'status':'PREPARING', 'pid':os.getpid(), 'work':str(self.work),
                  'authority':'human_20261009_execute_60k_plan_v1_surface_tension_0.04041',
                  'parent_case':str(self.parent/'60k-initial-bulk-N8080.cas.h5'),
                  'parent_data':str(self.parent/'60k-initial-bulk-N8080.dat.h5'),
                  'target_total_film_age_s':0.2, 'blocks':[],
                  'reporting':'frequency-1 fallback: dense stocks preserve existing assessment',
                  'source_accounting':'record both ledgers; user directs execution despite prior source discrepancy',
                  'review':'single native journal owner; no RPC during solve; fixed 1000+ commands; local checkpoints; exact clock and endpoint checks'}
        self.pending = False
        self.flush()

    def flush(self, **changes):
        self.m.update(changes, updated_epoch=time.time())
        dump(self.work/'run-manifest.json', self.m)

    def clock(self):
        return float(dict(self.s.rp_vars('wall-film/solution-state'))['film_elapsed_time'])

    def iteration(self):
        return int(round(float(self.s.settings.setup.named_expressions['P71V2Iteration'].get_value())))

    def params(self):
        return dict(self.s.rp_vars('wall-film/model-parameters'))

    def setparams(self, changes):
        p = self.params()
        assert set(changes).issubset(p), set(changes)-set(p)
        self.s.rp_vars('wall-film/model-parameters',[(k,changes.get(k,v)) for k,v in p.items()])
        actual = self.params()
        assert all(actual[k]==v for k,v in changes.items()), 'Film parameter readback differs'

    def values(self, names):
        raw = {}
        for group in self.s.settings.solution.report_definitions.compute(report_defs=names):
            raw.update(group)
        return {n:float(raw.get(n+'(without-sources)',raw[n])[0]) for n in names}

    def fields(self, wall):
        return {f:np.asarray(self.s.fields.field_data.get_field_data(ScalarFieldDataRequest(
            surfaces=[wall],field_name=f,node_value=False,boundary_value=True))[wall]).reshape(-1)
            for f in ['film-mass','film-thickness','film-x-velocity','film-y-velocity','film-z-velocity']}

    def save(self, label, reopen=False):
        assert not self.pending
        case = self.work/(label+'.cas.h5')
        self.s.settings.file.write_case_data(file_name=str(case))
        data = case.with_name(label+'.dat.h5')
        pair = {'case':str(case),'data':str(data),'native_iteration':self.iteration(),'film_age_s':self.clock()}
        for key in ['case','data']:
            file = Path(pair[key])
            assert file.is_file() and file.stat().st_size > 0
            pair[key+'_sha256'] = hashlib.sha256(file.read_bytes()).hexdigest()
        if reopen:
            p, equations, clock = self.params(), self.s.settings.solution.controls.equations.get_state(), self.clock()
            self.s.settings.file.read_case(file_name=str(case))
            self.s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
            self.s.settings.file.read_data(file_name=str(data))
            assert self.params()==p and self.s.settings.solution.controls.equations.get_state()==equations
            assert math.isclose(self.clock(),clock,abs_tol=1e-12)
            pair['reopened_verified'] = True
        self.flush(latest_pair=pair)
        return pair

    def build(self):
        assert self.iteration()==8080
        self.original_equations = self.s.settings.solution.controls.equations.get_state()
        assert all(self.original_equations.values())
        assert self.s.settings.solution.methods.p_v_coupling.flow_scheme()=='Coupled'
        original_clock, upper = self.clock(), self.fields('wall')
        original_sources = self.s.settings.setup.cell_zone_conditions.fluid.get_state()
        dump(self.work/'parent-readback.json',{'parameters':self.params(),'clock':original_clock,
             'equations':self.original_equations,'sources':original_sources,
             'materials':self.s.settings.setup.materials.fluid.get_state(),
             'walls':self.s.settings.setup.boundary_conditions.wall.get_state()})
        np.savez_compressed(self.work/'parent-upper-film.npz',**upper)
        preserved = self.save('preserved-parent-N8080')
        lower = self.s.settings.setup.boundary_conditions.wall[drain.WALL].phase['mixture'].wall_film
        lower.eulerian_film_wall = True
        lower.film_condition_type = 'film-wall-initial'
        lower.film_height.set_state({'option':'value','value':0.0})
        lower.enable_film_source_terms = False
        lower.enable_flow_momentum_coupling = False
        self.s.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        self.s.settings.file.read_data(file_name=preserved['data'])
        assert math.isclose(self.clock(),original_clock,abs_tol=1e-12)
        after = self.fields('wall')
        for f in upper:
            assert np.array_equal(upper[f],after[f]), 'Existing upper film changed: '+f
        for name in ['wall',drain.WALL]:
            w = self.s.settings.setup.boundary_conditions.wall[name].phase['mixture'].wall_film
            w.enable_flow_momentum_coupling = False
            w.enable_dpm_wall_splash = True
            w.allow_film_boundary_separation = True
        self.setparams({'film-coupled-solution?':False, 'surface-tension':0.04041,
                        'sub-iter-nums':100,'sub-iter-stop':1e-5,'sub-iter-interval':100,
                        'film-smoothing?':True,'film-smooth-level':2,'film-smooth-factor':0.5,
                        'film-message?':True})
        force = self.s.tui.define.phases.set_domain_properties.interaction_domain.forces.surface_tension
        force.sfc_tension_coeff('yes','constant',0.04041)
        self.step(1e-7)
        self.define_reports()
        residual = self.s.settings.solution.monitor.residual
        residual.options.print=True
        residual.options.plot=False
        for n in residual.equations.get_object_names():
            residual.equations[n].check_convergence=False
        assert self.s.settings.setup.cell_zone_conditions.fluid.get_state()==original_sources
        assert self.params()['surface-tension']==0.04041
        assert self.iteration()==8080 and math.isclose(self.clock(),original_clock,abs_tol=1e-12)
        pair = self.save('prepared-N8080',reopen=True)
        dump(self.work/'build-receipt.json',{'status':'PASS','parent_preserved':preserved,
             'prepared_pair':pair,'parameters':self.params(),'drain':drain.audit(self.s,True),
             'upper_film_fields_preserved':True,'original_bulk_source_hooks_preserved':True,
             'equations':self.s.settings.solution.controls.equations.get_state()})
        self.flush(status='READY',initial_film_age_s=original_clock)
        print('PILOT_BUILD_VERIFIED',self.work,flush=True)

    def step(self, dt):
        assert not self.pending
        self.setparams(policy.refresh_plan(dt))
        drain.configure(self.s,enabled=True,refresh_span_s=10e-6)
        assert math.isclose(drain.audit(self.s,True)['rate_s_inverse'],1/.0015,rel_tol=1e-12)
        self.dt = dt

    def verified_step(self, dt):
        """Reopen a controls-only child so changed RP parameters reach native nodes."""
        before=self.clock()
        self.step(dt)
        label=f'controls-step-{dt:.9g}-N{self.iteration()}-{len(self.m["blocks"]):03}'
        pair=self.save(label,reopen=True)
        assert math.isclose(self.clock(),before,abs_tol=1e-12)
        dump(self.work/(label+'-readback.json'),{'pair':pair,'parameters':self.params(),
             'solution_state':dict(self.s.rp_vars('wall-film/solution-state')),
             'no_iterations_advanced':True})

    def define_reports(self):
        surface = self.s.settings.solution.report_definitions.surface
        fields={'mass':('surface-sum','film-mass'),'outflow':('surface-sum','film-outflow-mass'),
                'secondary':('surface-sum','film-phase2-mass'),'dpm':('surface-sum','film-dpm-mass-src'),
                'stripped':('surface-sum','film-stripped-mass'),'separated':('surface-sum','film-separated-mass'),
                'thickness':('surface-facetmax','film-thickness'),'courant':('surface-facetmax','film-courant-number')}
        for key,(kind,field) in fields.items():
            n='p72d-total-'+key
            if n not in surface.get_object_names(): surface.create(name=n)
            surface[n].set_state({'report_type':kind,'field':field,'surface_names':['wall',drain.WALL]})
        for n,kind,field,walls in [('p72d-lower-mass','surface-sum','film-mass',[drain.WALL]),
                ('p72r-film-speed-max','surface-facetmax','film-velocity-mag',['wall',drain.WALL])]:
            if n not in surface.get_object_names(): surface.create(name=n)
            surface[n].set_state({'report_type':kind,'field':field,'surface_names':walls})
        expr=self.s.settings.solution.report_definitions.single_valued_expression
        if 'p72d-drain-rate' not in expr.get_object_names(): expr.create(name='p72d-drain-rate')
        expr['p72d-drain-rate'].definition='P72dRemoval'
        expr['p72d-drain-rate'].average_over=1

    def bulk(self, active):
        assert not self.pending
        expected={n:v if active else False for n,v in self.original_equations.items()}
        for n,v in expected.items(): self.s.settings.solution.controls.equations[n]=v
        assert self.s.settings.solution.controls.equations.get_state()==expected
        self.flush(bulk_active=active)

    def block(self,count,label):
        assert not self.pending and count>=1000
        start, clock = self.iteration(), self.clock()
        directory=self.work/f'{len(self.m["blocks"])+1:03}-{label}-N{start}'
        directory.mkdir()
        checkpoints=directory/'checkpoints'
        checkpoints.mkdir()
        names=FILM+(BULK if any(self.s.settings.solution.controls.equations.get_state().values()) else [])
        initial=self.values(names)
        files=self.s.settings.solution.monitor.report_files
        for n in files.get_object_names(): files[n].active=False
        for n in self.s.settings.solution.monitor.report_plots.get_object_names():
            self.s.settings.solution.monitor.report_plots[n].active=False
        paths={}
        for n in names:
            writer='p9pilot-'+n
            if writer not in files.get_object_names(): files.create(name=writer)
            path=directory/(n+'.out')
            files[writer].set_state({'report_defs':[n],'file_name':path.as_posix(),
                'frequency_of':'iteration','frequency':1,'active':True,
                'write_instantaneous_values':True})
            files[writer].print=False
            paths[n]=path
        configure_autosave(self.s,str(checkpoints),data_frequency=1000)
        journal=directory/'native-run.jou'
        journal.write_text(policy.journal(directory,count,start+count,token=label),encoding='ascii')
        record={'label':label,'status':'RUNNING','start':start,'target':start+count,
                'count':count,'step_s':self.dt,'initial_clock_s':clock,'initial':initial,
                'directory':str(directory),'started_epoch':time.time()}
        dump(directory/'block.json',record)
        self.m['blocks'].append(record)
        self.flush(status='RUNNING_NATIVE',active_block=str(directory),native_target=start+count)
        print('SUBMIT_NATIVE',label,count,'step',self.dt,'target',start+count,flush=True)
        self.pending=True
        self.s.scheme.exec(('(ti-menu-load-string '+json.dumps('/file/read-journal "'+journal.as_posix()+'"')+')',),wait=True,silent=True)
        self.pending=False
        assert (directory/'returned.txt').read_text().strip()=='NATIVE_COMMAND_RETURNED'
        assert self.iteration()==start+count
        assert math.isclose(self.clock()-clock,count*self.dt,abs_tol=1e-10)
        text=(directory/'native-run.trn').read_text(errors='replace')
        histories={n:policy.history(path.read_text(errors='replace')) for n,path in paths.items()}
        assessment=policy.assess_block(text,histories,initial,start,count,self.dt,clock,
                ledger_basis='gross-reported-sources',require_all_inner=True)
        separated=assessment['separated_mass_increment_kg']
        assessment['net_secondary_candidate_residual_kg']=assessment['ledger_residual_kg']-separated
        assessment['net_secondary_candidate_fraction']=abs(assessment['net_secondary_candidate_residual_kg'])/max(sum(abs(v) for v in assessment['integrated_sources_kg'].values()),1e-12)
        # Latest human instruction accepts the known source-accounting uncertainty.
        # Keep its failure visible; do not promote it to a conservation pass.
        stopping=[f for f in assessment['failures'] if f!='FILM_LEDGER_OPERATING_LIMIT']
        if assessment['peak_thickness_m']>=self.params()['thickness-limit']:
            stopping.append('INHERITED_THICKNESS_CAP')
        summary={k:v for k,v in assessment.items() if k not in ['histories','residuals']}
        record.update(status='COMPLETE',end=start+count,final_clock_s=self.clock(),
            wall_seconds=time.time()-record['started_epoch'],assessment=summary)
        dump(directory/'block.json',record)
        self.flush(status='ASSESSING',latest_film_age_s=self.clock(),verified_native_end=start+count)
        print('NATIVE_COMPLETE',label,json.dumps(summary),flush=True)
        if stopping:
            raise RuntimeError('Numerical guard failed: '+','.join(stopping))
        return assessment

    def readiness(self, assessment):
        h=assessment['histories']
        pressure=[a-b for a,b in zip(h['p72s3-pressure-inlet'][-1000:],h['p72s3-pressure-outlet'][-1000:])]
        liquid=h['v2-total-liquid-mass'][-1000:]
        outlet=h['v2-flux-phase2-steamoutlet'][-1000:]
        checks={'pressure_range_fraction':(max(pressure)-min(pressure))/max(abs(statistics.fmean(pressure)),1e-12),
                'inventory_range_fraction':(max(liquid)-min(liquid))/max(abs(statistics.fmean(liquid)),1e-12),
                'outlet_range_feed_fraction':(max(outlet)-min(outlet))/116.92}
        checks['pass']=checks['pressure_range_fraction']<=.05 and checks['inventory_range_fraction']<=.1 and checks['outlet_range_feed_fraction']<=.05
        self.flush(latest_bulk_screen=checks)
        return checks['pass']

    def run(self, resume_after_adjustment=False, resume_after_transition=False, fallback_growth=False, repair_growth=False, sequential_1us=False):
        try:
            if not resume_after_adjustment and not resume_after_transition and not fallback_growth and not repair_growth and not sequential_1us:
                self.bulk(True)
                result=self.block(1000,'active-adjustment')
                extra=0
                while not self.readiness(result) and extra<10000:
                    result=self.block(1000,'active-adjustment-recovery')
                    extra+=1000
                if not self.readiness(result): raise RuntimeError('Bulk freeze readiness failed within contingency')
                self.save('pre-freeze',reopen=True)
            elif resume_after_adjustment:
                assert self.m['latest_bulk_screen']['pass']
                assert self.iteration()==9080 and math.isclose(self.clock(),.00075,abs_tol=1e-12)
            if sequential_1us:
                assert self.iteration()==30000 and math.isclose(self.clock(),.05795,abs_tol=1e-12)
                assert not any(self.s.settings.solution.controls.equations.get_state().values())
                assert not self.params()['film-coupled-solution?']
            elif repair_growth:
                assert self.iteration()==30000 and math.isclose(self.clock(),.05795,abs_tol=1e-12)
                assert not any(self.s.settings.solution.controls.equations.get_state().values())
                assert self.params()['film-coupled-solution?']
            elif fallback_growth:
                assert self.iteration()==14000 and math.isclose(self.clock(),.01795,abs_tol=1e-12)
                assert not any(self.s.settings.solution.controls.equations.get_state().values())
            elif not resume_after_transition:
                self.bulk(False)
                self.block(1000,'frozen-transition')
            else:
                assert self.iteration()==10080 and math.isclose(self.clock(),.00085,abs_tol=1e-12)
                assert not any(self.s.settings.solution.controls.equations.get_state().values())
            sequential_step=self.m.get('production_step_s',1e-6)
            sequential_label='sequential-0p1us-qualification' if sequential_step==1e-7 else 'sequential-1us-qualification'
            self.verified_step(sequential_step if sequential_1us else 2.5e-6)
            self.block(1000,sequential_label if sequential_1us else 'repair-coupled-qualification' if repair_growth else 'fallback-qualify-2p5us' if fallback_growth else 'qualify-2p5us')
            if not fallback_growth and not repair_growth and not sequential_1us:
                self.verified_step(5e-6)
                self.block(1000,'qualify-5us')
            production_step=self.dt
            # Adjust the exact age using >=1000 fixed-step commands, keeping DPM
            # cadence at a declared 20 us. 0.1 us is the inherited qualified step.
            remaining=(.195-self.clock())/self.dt
            fractional=remaining-round(remaining)
            if not math.isclose(self.clock()+round(remaining)*self.dt,.195,abs_tol=1e-10,rel_tol=0):
                remainder=(.195-self.clock()) % self.dt
                fine_count=1000+int(round(remainder/1e-7))
                self.step(1e-7)
                self.block(fine_count,'clock-alignment')
                self.verified_step(production_step)
            remaining=int(round((.195-self.clock())/self.dt))
            assert math.isclose(self.clock()+remaining*self.dt,.195,abs_tol=1e-10)
            for count in [5000]:
                self.block(count,'first-growth')
                remaining-=count
            while remaining:
                count=remaining if remaining<=11000 else 10000
                assert count>=1000
                self.block(count,'frozen-growth')
                remaining-=count
            self.save('pre-reactivation-195ms',reopen=True)
            self.bulk(True)
            final=self.block(int(round(.005/self.dt)),'final-active-195-to-200ms')
            assert math.isclose(self.clock(),.2,abs_tol=1e-10)
            self.readiness(final)
            pair=self.save('final-200ms',reopen=True)
            shared=Path(os.environ['OneDrive'])/'P4P-Fluent-Artifacts/Phase9/ewf-development-final'/self.work.name/'60k'
            shared.mkdir(parents=True,exist_ok=False)
            for key in ['case','data']: shutil.copy2(pair[key],shared/Path(pair[key]).name)
            dump(shared/'endpoint-manifest.json',{'pair':pair,'local_work':str(self.work),'film_age_s':self.clock(),
                'bulk_screen':self.m['latest_bulk_screen'],'source_accounting_qualified':False})
            self.flush(status='COMPLETE',final_pair=pair,shared_final=str(shared))
            print('PILOT_COMPLETE',self.work,flush=True)
        except BaseException as exc:
            self.flush(status='STOPPED_WITH_EVIDENCE',error=str(exc),traceback=traceback.format_exc())
            print('PILOT_STOPPED',str(exc),self.work,flush=True)
            raise


def main():
    import argparse
    import sys
    import ansys.fluent.core as pyfluent
    parser=argparse.ArgumentParser()
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--resume-from-prefreeze',action='store_true')
    parser.add_argument('--resume-from-transition',action='store_true')
    parser.add_argument('--fallback-2p5us',action='store_true')
    parser.add_argument('--repair-coupled',action='store_true')
    parser.add_argument('--sequential-1us',action='store_true')
    parser.add_argument('--sequential-0p1us',action='store_true')
    parser.add_argument('--server-info',type=Path)
    args=parser.parse_args()
    if args.sequential_0p1us:
        args.sequential_1us=True
    work=args.work.resolve()
    if args.fallback_2p5us or args.sequential_1us:
        assert args.server_info and args.server_info.is_file()
        solver=pyfluent.connect_to_fluent(server_info_file_name=str(args.server_info),cleanup_on_exit=False,start_transcript=False)
    elif args.resume_from_prefreeze or args.resume_from_transition or args.repair_coupled:
        os.chdir(work.parent)
        solver=pyfluent.launch_fluent(product_version='25.2',
            fluent_path=r'C:\Program Files\ANSYS Inc\ANSYS Student\v252\fluent\ntbin\win64\fluent.exe',
            cwd=str(work.parent),mode='solver',dimension=3,precision='double',
            processor_count=4,ui_mode='no_gui',py=True,cleanup_on_exit=False,start_transcript=False)
    else:
        connection_file=work/'controller-connection.json'
        connection=json.loads(connection_file.read_text())
        solver=pyfluent.connect_to_fluent(**connection,cleanup_on_exit=False,start_transcript=False)
        connection_file.unlink()
    pilot=Pilot.__new__(Pilot)
    pilot.s=solver
    pilot.repo=Path(__file__).resolve().parents[3]
    pilot.work=work
    pilot.m=json.loads((work/'run-manifest.json').read_text())
    pilot.parent=Path(pilot.m['parent_case']).parent
    pilot.pending=False
    pilot.original_equations={'drift':True,'flow':True,'ke':True,'mp':True}
    pilot.dt=1e-7
    pilot.flush(status='VERIFYING_PREPARED',pid=os.getpid(),controller_script=str(Path(__file__).resolve()),
                controller_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    # The preparation case read completed; recover the interrupted verification
    # with its exact paired data. No solve is repeated and no field is reset.
    if args.sequential_1us:
        assert pilot.m['accepted_terminal_iteration']==30000
        pair=pilot.m['accepted_terminal_pair']
        for key in ['case','data']:
            assert hashlib.sha256(Path(pair[key]).read_bytes()).hexdigest()==pair[key+'_sha256']
        old=pilot.m['blocks'][-1]
        assert old['label']==('sequential-1us-qualification' if args.sequential_0p1us else 'repair-coupled-qualification') and old['end']==31000
        old['excluded_from_accepted_lineage']=True
        dump(Path(old['directory'])/'block.json',old)
        solver.settings.file.read_case(file_name=pair['case'])
        solver.settings.setup.user_defined.load(udf_library_name='libcontactv2')
        solver.settings.file.read_data(file_name=pair['data'])
        assert pilot.iteration()==30000 and math.isclose(pilot.clock(),.05795,abs_tol=1e-12)
        assert not pilot.params()['film-coupled-solution?']
        completed=sum(Path(b['directory'],'native-run.trn').read_text(errors='replace').count('Film time = ') for b in pilot.m['blocks'])
        requested_step=1e-7 if args.sequential_0p1us else 1e-6
        remaining=int(round((.2-pilot.clock())/requested_step))
        pilot.flush(error=None,traceback=None,terminal_outcome=None,continuation_authorized=True,
            authority='human_20261010_lower_to_'+('0p1us' if args.sequential_0p1us else '1us')+'_sequential_continue_200ms',
            production_step_s=requested_step,recovery_iteration=30000,recovery_film_age_s=.05795,
            controller_logs='sequential-0p1us-controller' if args.sequential_0p1us else 'sequential-1us-controller',revised_completed_native_updates=completed,
            revised_remaining_updates=remaining,revised_projected_total_updates=completed+remaining,
            budget_basis='Human explicitly authorized '+str(requested_step)+' s sequential route beyond Plan v1 practical budget; exact remaining age to 200 ms, no further numerical search')
    elif args.repair_coupled:
        assert not pilot.m.get('coupled_repair_used'), 'One repair allowance already used'
        old=pilot.m['blocks'][-1]
        assert old['start']==30000 and old['label']=='frozen-growth'
        old.update(status='DISCARDED_NUMERICAL_FAILURE',reason='Persistent flat inner residuals at 2.5 us; owned busy session stopped; restore accepted N30000')
        dump(Path(old['directory'])/'block.json',old)
        pair={'case':str(work/'010-frozen-growth-N20000/final-N30000.cas.h5'),
              'data':str(work/'010-frozen-growth-N20000/final-N30000.dat.h5')}
        expected_hashes={'case':'d882bbe91715c98789ca8fc8ce6ac741e073200db954b00fed6714c8d406abc0',
                         'data':'c65a096845d9986666bf453dc28f20c7144893ec4192ba58239f1055ff1a0213'}
        for key in pair:
            assert hashlib.sha256(Path(pair[key]).read_bytes()).hexdigest()==expected_hashes[key]
        completed_native_updates=sum(Path(b['directory'],'native-run.trn').read_text(errors='replace').count('Film time = ') for b in pilot.m['blocks'])
        remaining_updates=int(round((.2-.05795)/2.5e-6))
        assert completed_native_updates+remaining_updates<=92000, 'Plan fallback contingency exhausted'
        solver.settings.file.read_case(file_name=pair['case'])
        solver.settings.setup.user_defined.load(udf_library_name='libcontactv2')
        solver.settings.file.read_data(file_name=pair['data'])
        assert pilot.iteration()==30000 and math.isclose(pilot.clock(),.05795,abs_tol=1e-12)
        original_params=pilot.params()
        before_fields={wall:pilot.fields(wall) for wall in ['wall',drain.WALL]}
        pilot.setparams({'film-coupled-solution?':True})
        pilot.save('coupled-repair-controls-N30000',reopen=True)
        after_params=pilot.params()
        assert {k:v for k,v in original_params.items() if k!='film-coupled-solution?'}=={k:v for k,v in after_params.items() if k!='film-coupled-solution?'}
        for wall,fields in before_fields.items():
            after=pilot.fields(wall)
            assert all(np.array_equal(value,after[name]) for name,value in fields.items())
        pilot.flush(error=None,traceback=None,coupled_repair_used=True,
            repair_completed_native_updates=completed_native_updates,repair_remaining_updates=remaining_updates,
            repair_projected_total_updates=completed_native_updates+remaining_updates,
            numerical_repair='Coupled film mass/momentum at unchanged 2.5 us; one 1000-update qualification; no further numerical search if it fails',
            controller_logs='coupled-repair-controller',recovery_iteration=30000,recovery_film_age_s=.05795)
    elif args.fallback_2p5us:
        old=pilot.m['blocks'][-1]
        assert old['label']=='first-growth' and old['end']==17080
        old['accepted_prefix_end']=14000
        old['discarded_continuation_start']=14001
        old['recovery_reason']='N14575 final momentum residuals missed limit; N14000 prefix passed every inner solve'
        checkpoint=work/'007-first-growth-N12080/checkpoints'
        pair={'case':str(checkpoint/'checkpoint-14000-1-14000.cas.h5'),
              'data':str(checkpoint/'checkpoint-14000-1-14000.dat.h5')}
        solver.settings.file.read_case(file_name=pair['case'])
        solver.settings.setup.user_defined.load(udf_library_name='libcontactv2')
        solver.settings.file.read_data(file_name=pair['data'])
        assert pilot.iteration()==14000 and math.isclose(pilot.clock(),.01795,abs_tol=1e-12)
        pilot.dt=5e-6
        pilot.flush(error=None,traceback=None,fallback_production_step_s=2.5e-6,
            accepted_prefix_assessment=str(work/'N14000-prefix-assessment.json'),
            recovery_iteration=14000,recovery_film_age_s=.01795,
            budget_basis='Plan v1 authorized 2.5 us fallback; approximately 82k nominal plus 10k contingency')
    elif args.resume_from_transition:
        old=pilot.m['blocks'][-1]
        assert old['label']=='qualify-2p5us'
        old.update(status='DISCARDED_STEP_MISMATCH_BRANCH',reason='Configured 2.5 us but native output retained 0.1 us; restore verified transition')
        pair={'case':str(work/'003-frozen-transition-N9080/final-N10080.cas.h5'),
              'data':str(work/'003-frozen-transition-N9080/final-N10080.dat.h5')}
        solver.settings.file.read_case(file_name=pair['case'])
        solver.settings.setup.user_defined.load(udf_library_name='libcontactv2')
        solver.settings.file.read_data(file_name=pair['data'])
        assert pilot.iteration()==10080 and math.isclose(pilot.clock(),.00085,abs_tol=1e-12)
    elif args.resume_from_prefreeze:
        old=pilot.m['blocks'][-1]
        assert old['status']=='RUNNING' and old['label']=='frozen-transition'
        old.update(status='INTERRUPTED_DISCARDED_BRANCH',last_observed_iteration=9672,
                   last_observed_film_age_s=.0008092,
                   reason='Controller and Fluent absent; no fatal event in preserved native transcript')
        pair=pilot.m['latest_pair']
        assert pair['native_iteration']==9080
        for key in ['case','data']:
            assert hashlib.sha256(Path(pair[key]).read_bytes()).hexdigest()==pair[key+'_sha256']
        solver.settings.file.read_case(file_name=pair['case'])
        solver.settings.setup.user_defined.load(udf_library_name='libcontactv2')
        solver.settings.file.read_data(file_name=pair['data'])
        assert pilot.iteration()==9080
        assert math.isclose(pilot.clock(),.00075,abs_tol=1e-12)
    else:
        solver.settings.file.read_data(file_name=str(work/'prepared-N8080.dat.h5'))
        assert pilot.iteration()==8080
        assert math.isclose(pilot.clock(),.00065,abs_tol=1e-12)
    assert pilot.params()['surface-tension']==.04041
    assert pilot.params()['film-coupled-solution?']==args.repair_coupled
    expected_equations={n:False for n in pilot.original_equations} if args.resume_from_transition or args.fallback_2p5us or args.repair_coupled or args.sequential_1us else pilot.original_equations
    assert solver.settings.solution.controls.equations.get_state()==expected_equations
    audit=drain.audit(solver,True)
    receipt=work/('sequential-0p1us-readback.json' if args.sequential_0p1us else 'sequential-1us-readback.json' if args.sequential_1us else 'coupled-repair-readback.json' if args.repair_coupled else 'fallback-recovery-readback.json' if args.fallback_2p5us else 'transition-recovery-readback.json' if args.resume_from_transition else 'recovery-readback.json' if args.resume_from_prefreeze else 'build-receipt.json')
    dump(receipt,{'status':'PASS','native_iteration':pilot.iteration(),
         'film_age_s':pilot.clock(),'parameters':pilot.params(),'drain':audit,
         'prepared_case_data_readback_verified':True,'source_library_loaded':True,
         'controlled_surface_tension_N_per_m':.04041,
         'preparation_recovery':'Interrupted case-read verification completed; exact paired data restored; no iterations advanced'})
    pilot.flush(status='READY',recovery_start_film_age_s=pilot.clock())
    print('PILOT_BUILD_VERIFIED',work,flush=True)
    pilot.run(resume_after_adjustment=args.resume_from_prefreeze,resume_after_transition=args.resume_from_transition,fallback_growth=args.fallback_2p5us,repair_growth=args.repair_coupled,sequential_1us=args.sequential_1us)


if __name__=='__main__':
    main()
