"""Prepare each speed arm from the saved dry-film A pair, then screen its film step."""
from pathlib import Path, PureWindowsPath
import json
import math
import time
import uuid

import continue_phase72a_stage3_film_development as c
from run_phase72a_stage3_speed_sensitivity import CAMPAIGN, event, batch, endpoint
from run_phase72a_stage3_server3 import state, loading, instrument, iterate
from run_phase72a_e27_server1_continuation import dump, native_iteration
from run_phase72a_local_film_replay import readback, require_match
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256
from pyansys_fluent.remote_text import read_text
from run_phase72a_adaptive_film import history, FILM, ROW

ROOT = Path(__file__).resolve().parents[2]
SEED_ROOT = ROOT/'output/phase72a-stage3-early-ewf-server1/20261005'
LOCAL_WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage3\speed-sensitivity-500ms-20261006')


def wait_submitted(s, target):
    """Never resubmit a startup command after loss of its client reply."""
    while True:
        try:
            n = native_iteration(s)
            if n > target:
                raise RuntimeError('Startup exceeded the submitted native horizon')
            if n == target:
                run = s.settings.solution.run_calculation
                if not run.iterate.is_active() and run.interrupt.is_active():
                    run.interrupt()
                if run.iterate.is_active():
                    return s
        except Exception as error:
            print('STARTUP_RECONNECT', repr(error), flush=True)
            time.sleep(10)
            s = c.attach()
        time.sleep(10)


def startup(s, job, label, speed, root, work):
    """Reproduce the 500/2000/1000 schedule; change both feed commands together."""
    out, remote = root/'startup', work/'startup'
    c.OUT, c.WORK = out, remote
    feed_factor = speed/26.81
    if (out/'run-manifest.json').exists():
        manifest=json.loads((out/'run-manifest.json').read_text())
        n=manifest['verified_native_end']
        if not s.settings.solution.run_calculation.iterate.is_active() or native_iteration(s)!=n:
            raise RuntimeError('Startup resume requires its verified idle endpoint')
        if manifest.get('active_target') not in [None,n]:
            raise RuntimeError('Reconcile the submitted startup horizon before resuming')
        expected=json.loads((out/f'endpoint-N{n}.json').read_text())
        require_match(readback(s),expected['state']['readback'])
        if c.film(s)!=expected['film']:
            raise RuntimeError('Startup resume clock differs from preserved endpoint')
        report_paths=manifest['report_paths']
        manifest.setdefault('native_transcript_parts',[str(remote/'startup.trn').replace('\\','/')])
        s.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
        attempt=len(manifest['native_transcript_parts'])
        trn_remote=str(remote/f'startup-resume-{attempt}.trn').replace('\\','/')
        client_transcript=out/f'run-transcript-resume-{attempt}.txt'
        s.transcript.start(file_name=str(client_transcript),write_to_stdout=False)
        from pyansys_fluent.common import quote_scheme_string
        command=f'/file/start-transcript "{trn_remote}"'
        s.scheme.eval(f'(ti-menu-load-string "{quote_scheme_string(command)}")')
        manifest['native_transcript_parts'].append(trn_remote)
        manifest['status']='RUNNING'
        dump(out/'run-manifest.json',manifest)
    else:
        out.mkdir(parents=True, exist_ok=False)
        for folder in [remote, remote/'scratch', remote/'monitors']:
            ensure_remote_directory(s, str(folder))
        # The preceding case is already locally paired and shared before replacement.
        assert s.settings.solution.run_calculation.iterate.is_active()
        source = json.loads((SEED_ROOT/'run-manifest.json').read_text())['prepared_pair']
        for kind in ['case', 'data']:
            actual = remote_file_sha256(s, source[kind], str(remote/'scratch'/f'seed-{kind}-{uuid.uuid4().hex}.txt'))
            if actual != source[kind+'_sha256']:
                raise RuntimeError('Prepared A pair differs')
        s.settings.file.read_case(file_name=source['case'])
        s.settings.file.read_data(file_name=source['data'])
        seed = json.loads((SEED_ROOT/'prepared-reopen.json').read_text())
        require_match(readback(s), seed['state']['readback'])
        if native_iteration(s) != 1580 or c.film(s)['film_elapsed_time'] != 0:
            raise RuntimeError('Exact dry-film A restart required')
        equations = s.settings.solution.controls.equations.get_state()
        if not all(equations.values()):
            raise RuntimeError('All original bulk equations must advance during startup')
        c.OUT, c.WORK = out, remote
        feed_factor = speed/26.81
        loading(s, .25*feed_factor)
        initial = state(s)
        if not math.isclose(initial['readback']['fields']['v2-total-liquid-mass'][0],
                            seed['state']['readback']['fields']['v2-total-liquid-mass'][0], rel_tol=1e-10):
            raise RuntimeError('Boundary-only speed change altered initial bulk inventory')
        report_paths = instrument(s, remote/'monitors')
        s.settings.file.auto_save.data_frequency = 0
        s.transcript.start(file_name=str(out/'run-transcript.txt'), write_to_stdout=False)
        trn_remote = str(remote/'startup.trn').replace('\\', '/')
        s.scheme.eval(f'(ti-menu-load-string "/file/start-transcript \\\"{trn_remote}\\\"")')
        prepared = c.save(s, 'prepared-A-N1580')
        prepared_clock=c.film(s)
        s.settings.file.read_case(file_name=prepared['case'])
        s.settings.file.read_data(file_name=prepared['data'])
        require_match(readback(s),initial['readback'])
        if c.film(s)!=prepared_clock or native_iteration(s)!=1580:
            raise RuntimeError('Prepared speed-arm reopen changed fields or clock')
        dump(out/'prepared-reopen.json',{'state':state(s),'film_solution_state':prepared_clock,'pair':prepared})
        manifest = {'status':'RUNNING', 'speed_m_s':speed, 'feed_factor':feed_factor,
                    'source_pair':source, 'prepared_pair':prepared, 'report_paths':report_paths,
                    'verified_native_end':1580, 'blocks':[], 'initialization_calls':0, 'native_transcript_parts':[trn_remote]}
        dump(out/'run-manifest.json', manifest)
        client_transcript=out/'run-transcript.txt'
    stages = [('low-hold',2080,.25)]
    stages += [('ramp',2080+r+10,.25+.75*r/2000) for r in range(0,2000,10)]
    stages += [('target-hold',5080,1.)]
    for stage, target, fraction in stages:
        if target<=native_iteration(s):
            continue
        feed = loading(s, fraction*feed_factor)
        begin = native_iteration(s)
        event(job,'STARTUP_RUNNING',active_case=label, nominal_speed_m_s=speed,
              startup_stage=stage, verified_native_end=begin, active_target=target,
              active_client_transcript=str(client_transcript), active_run_manifest=str(out/'run-manifest.json'))
        manifest.update(active_target=target, active_stage=stage, feed=feed)
        dump(out/'run-manifest.json',manifest)
        try:
            iterate(s,target-begin)
        except Exception as error:
            manifest['client_error']=repr(error);dump(out/'run-manifest.json',manifest)
            s=wait_submitted(s,target)
        record={'stage':stage,'native_start':begin,'native_end':target,'feed':feed}
        if stage!='ramp' or (target-2080)%500==0:
            before=state(s);clock=c.film(s);pair=c.save(s,f'{stage}-N{target}')
            s.settings.file.read_case(file_name=pair['case']);s.settings.file.read_data(file_name=pair['data'])
            require_match(readback(s),before['readback'])
            reopened_clock=c.film(s)
            expected_time=(target-1580)*1e-6
            if native_iteration(s)!=target or not math.isclose(reopened_clock['film_elapsed_time'],expected_time,abs_tol=1e-12):
                raise RuntimeError('Saved startup clock/native horizon differs')
            if reopened_clock!=clock:
                proof='\n'.join(read_text(s,path) for path in manifest['native_transcript_parts'])
                native_clocks=[list(map(float,x.groups())) for x in FILM.finditer(proof)]
                if len(native_clocks)!=target-1580 or not math.isclose(native_clocks[-1][0],expected_time,abs_tol=1e-12):
                    raise RuntimeError('Changed live clock lacks native accepted-step proof')
                if not all(math.isclose(row[1],1e-6,abs_tol=1e-15) for row in native_clocks):
                    raise RuntimeError('Startup accepted step differs from 1 us')
                if not math.isclose(reopened_clock['film_mass_outflow'],before['readback']['fields']['p72a-e2.7-ewf-outflow-mass-total'][0],rel_tol=1e-7,abs_tol=1e-15):
                    raise RuntimeError('Reopened cumulative film outflow differs from native field')
                manifest.setdefault('clock_reconciliations',[]).append({'native_iteration':target,'live_before_save':clock,'saved_reopened':reopened_clock,'native_updates_confirmed':len(native_clocks),'new_solve_calls':0})
            clock=reopened_clock
            fields=before['readback']['fields']
            if not all(math.isfinite(v[0]) for v in fields.values()) or fields['p72a-e2.7-ewf-thickness-max'][0]>.003:
                raise RuntimeError('Startup finite-field/thickness review; endpoint preserved')
            record['pair']=pair
            dump(out/f'endpoint-N{target}.json',{'state':state(s),'film':clock,'pair':pair,'reopen':'PASS'})
            print('SPEED_STARTUP_CHECKPOINT',label,target,clock['film_elapsed_time'],flush=True)
        manifest['blocks'].append(record);manifest['verified_native_end']=target
        dump(out/'run-manifest.json',manifest)
    s.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
    s.transcript.stop()
    native='\n'.join(read_text(s,path) for path in manifest['native_transcript_parts']);(out/'startup.trn').write_text(native)
    clocks=[list(map(float,x.groups())) for x in FILM.finditer(native)]
    assert len(clocks)==3500 and math.isclose(clocks[-1][0],.0035,abs_tol=1e-12)
    assert all(math.isclose(x[1],1e-6,abs_tol=1e-15) for x in clocks)
    carriers={}
    for line in native.splitlines():
        match=ROW.match(line)
        if match:
            n=int(match[1]);values=[float(v) for v in line.split()[1:8]]
            if len(values)!=7 or not all(math.isfinite(v) for v in values):
                raise RuntimeError('Incomplete/nonfinite carrier residual row')
            if n in carriers and carriers[n]!=values:
                raise RuntimeError(f'Conflicting startup carrier row N{n}')
            carriers[n]=values
    assert set(range(1581,5081)).issubset(carriers),'Startup carrier residual gap'
    dump(out/'carrier-residuals.json',carriers)
    histories={}
    for name,path in report_paths.items():
        text=read_text(s,path);(out/f'final-{name}.out').write_text(text);values=history(text)
        assert set(range(1581,5081)).issubset(values),name
        histories[name]={'iterations':sorted(values),'values':[values[n] for n in sorted(values)]}
    dump(out/'final-histories.json',histories)
    pair=manifest['blocks'][-1]['pair'];clock=c.film(s)
    final={'state':state(s),'film_solution_state':clock,'pair':pair}
    dump(out/'final-reopen.json',final)
    manifest.update(status='COMPLETE_STARTUP_REOPEN_VERIFIED',final_pair=pair,final_reopen='PASS',active_target=None)
    dump(out/'run-manifest.json',manifest)
    return s,out/'final-reopen.json'


def prepare_case(s, job, label, speed):
    root=CAMPAIGN/label;work=LOCAL_WORK/label
    development=root/'film-development'
    if development.joinpath('run-manifest.json').exists():
        from run_phase72a_stage3_speed_sensitivity import bind
        m=bind(development,work/'film-development')
        expected=json.loads(endpoint(m).read_text())
        if native_iteration(s)!=m['verified_native_end']:
            raise RuntimeError('Speed-arm resume differs from saved endpoint')
        require_match(readback(s),expected['state']['readback'])
        return s,m,m.get('campaign_qualified_step_s',m['alternative_sensitivity']['qualified_fixed_step_s'])
    event(job,'PREPARING_SPEED_CASE',active_case=label,nominal_speed_m_s=speed)
    s,source=startup(s,job,label,speed,root,work)
    c.ROOT_OUT,c.ROOT_WORK=development,work/'film-development'
    c.OUT,c.WORK=c.ROOT_OUT,c.ROOT_WORK;c.MANIFEST=development/'run-manifest.json';c.SOURCE=source
    development.mkdir(parents=True,exist_ok=False)
    c.prepare(s);m=json.loads(c.MANIFEST.read_text())
    m.update(speed_m_s=speed,feed_factor=speed/26.81,campaign_manifest=str(CAMPAIGN/'run-manifest.json'))
    dump(c.MANIFEST,m)
    event(job,'QUALIFYING_SPEED_ARM_TIMESTEP',active_case=label)
    c.sensitivity(s,m)
    if not m['alternative_sensitivity']['pass']:
        raise RuntimeError('Per-speed matched-time comparison requires numerical repair')
    for candidate in [10,20]:
        c.grow_sensitivity(s,m,step_us=candidate)
        if m['status']!='MATCHED_TIME_SENSITIVITY_PASS':
            break
    qualified=m['alternative_sensitivity']['qualified_fixed_step_s']
    chosen=next(a for a in reversed(list(m['sensitivity_arms'].values()))
                if math.isclose(a['metrics']['printed_step_max_s'],qualified,rel_tol=1e-8))
    source={'pair':chosen['pair'],'endpoint':str(Path(chosen['metrics']['output'])/f"endpoint-N{chosen['pair']['native_iteration']}.json")}
    c.restore_branch(s,m,source,'adaptive-development')
    c.controls(s,m,{'ewf-adaptive?':True,'courant-number':.2,'adapt-init-dt':qualified,
                    'adapt-tstp-inc':1.15,'adapt-tstp-dec':2.0,'sub-iter-nums':30,'implicit-scheme-new?':True})
    m['campaign_qualified_step_s']=qualified;dump(c.MANIFEST,m)
    job['cases'][label].update(startup_manifest=str(root/'startup/run-manifest.json'),
                              run_manifest=str(c.MANIFEST),qualified_step_s=qualified)
    event(job,'SPEED_ARM_PREPARED',active_case=label,qualified_step_s=qualified)
    return s,m,qualified
