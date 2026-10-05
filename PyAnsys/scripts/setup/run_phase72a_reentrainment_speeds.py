"""Three bounded local EWF speed contrasts in a caller-owned Fluent session.

No launch, attach, exit or remote-server access. Startup retains historical A
fields. Film-only development is explicitly distinguished from full-model time.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import time
import traceback

import numpy as np
from run_phase72a_r3_ewf_absorber_direct import save_pair, validate_roughness
from run_phase72a_e27_server1_continuation import native_iteration
from run_phase72a_adaptive_film import FILM, history
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(r'C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse\Stage3-Reentrainment-20261006')
OUT = ROOT / 'output/phase72a-reentrainment-speeds/20261006'
TARGET = .250
SPEEDS = (26.81, 20.11, 32.14)
FEATURES = {'dpm-collection?': True, 'dpm-splashing?': True,
            'film-stripping?': True, 'film-separation?': True}
# Verified on v252 from native numerical prompts and incremental readback.
MODEL_ARGS = ['yes','yes','yes','yes','no','no','no','no','yes','yes','yes',
              0,20.00000859436694,0,'no','yes',100,.14,.5,.3,'no']
MASS = 'p72a-e2.7-ewf-film-mass-total'
ACC = 'p72a-e2.7-ewf-secondary-phase-mass-total'
DRAIN = 'p72a-e2.7-ewf-outflow-mass-total'
DPM = 'p72-re-dpm-source'
STRIP = 'p72-re-stripped-mass'
SEP = 'p72-re-separated-mass'
SUB = re.compile(r'sub-iteration:\s*(\d+) residual - h:\s*([^;]+); u:\s*([^;]+); v:\s*(\S+)')
FATAL = re.compile(r'floating point exception|received signal|Divergence detected in AMG solver|fatal error', re.I)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, default=str, allow_nan=False)+'\n', encoding='utf-8')
    temp.replace(path)


def clock(s):
    return dict(s.rp_vars('wall-film/solution-state'))


def parameters(s):
    return dict(s.rp_vars('wall-film/model-parameters'))


def controls(s, changes):
    current = parameters(s)
    if not set(changes).issubset(current):
        raise RuntimeError('Unavailable film control')
    old_time = clock(s)['film_elapsed_time']
    s.rp_vars('wall-film/model-parameters', [(k, changes.get(k,v)) for k,v in current.items()])
    # Fluent keeps a separate active film solver configuration. As in the
    # reference runner, paired save/reopen activates native numerical changes.
    n = native_iteration(s)
    pair = save_pair(s,WORK/f'numerical-controls-N{n}-{time.time_ns()}.cas.h5',n)
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    actual = parameters(s)
    if any(actual[k] != v for k,v in changes.items()):
        raise RuntimeError('Film control readback differs')
    if clock(s)['film_elapsed_time'] != old_time:
        raise RuntimeError('Film control write reset clock')


def feed(s, speed, fraction):
    bc = s.settings.setup.boundary_conditions.mass_flow_inlet
    result = {}
    for zone, phase, nominal in [('liquidinlet','phase-2',116.92),('steaminlet','phase-1',80.69)]:
        value = nominal * speed / 26.81 * fraction
        obj = bc[zone].phase[phase].momentum.mass_flow_rate
        obj.value = value
        actual = obj.get_state()['value']
        if not math.isclose(actual,value,rel_tol=1e-12):
            raise RuntimeError('Feed readback differs')
        result[zone] = actual
    return result


def audit(s):
    return {'film_parameters': parameters(s), 'film_clock': clock(s),
            'wall': s.settings.setup.boundary_conditions.wall['wall'].get_state(),
            'collector': s.settings.setup.cell_zone_conditions.fluid['p71a-v2-virtual-outlet'].get_state(),
            'inlets': s.settings.setup.boundary_conditions.mass_flow_inlet.get_state(),
            'methods': s.settings.solution.methods.get_state(),
            'controls': s.settings.solution.controls.get_state(),
            'dpm': s.settings.setup.models.discrete_phase.get_state()}


def assert_features(s):
    p = parameters(s)
    if any(p.get(k) != v for k,v in FEATURES.items()):
        raise RuntimeError('Re-entrainment option mismatch')
    for key in ['aux-src-smoothing?','mom-pressure?','mom-spreading?','surface-tension?',
                'solve-energy?','solve-scalar?','random-edge-separation?']:
        if p[key]:
            raise RuntimeError('Unexpected film physics: '+key)
    w = s.settings.setup.boundary_conditions.wall['wall'].phase['mixture'].wall_film.get_state()
    if not w['enable_dpm_wall_splash'] or not w['allow_film_boundary_separation']:
        raise RuntimeError('Wall-level re-entrainment disabled')
    if w['enable_flow_momentum_coupling']:
        raise RuntimeError('Unexpected film feedback')
    validate_roughness(s)


def reports(s, work):
    surfaces = s.settings.solution.report_definitions.surface
    files = s.settings.solution.monitor.report_files
    for name, field in [(DPM,'film-dpm-mass-src'),(STRIP,'film-stripped-mass'),(SEP,'film-separated-mass')]:
        if name not in surfaces.get_object_names():
            surfaces.create(name=name)
        surfaces[name].set_state({'report_type':'surface-sum','field':field,'surface_names':['wall']})
        if name not in files.get_object_names():
            files.create(name=name)
        files[name].report_defs = [name]
    folder = work/'monitors'
    folder.mkdir(parents=True, exist_ok=False)
    paths = {}
    for name in files.get_object_names():
        obj = files[name]
        defs = obj.report_defs()
        if len(defs) != 1 or defs[0] in paths:
            raise RuntimeError('Ambiguous native report history')
        path = folder/(defs[0]+'.out')
        obj.set_state({'file_name':str(path),'frequency_of':'iteration','frequency':1,'active':True})
        paths[defs[0]] = str(path)
    return paths


def values(s, names):
    result = {}
    for group in s.settings.solution.report_definitions.compute(report_defs=names):
        result.update({k:float(v[0]) for k,v in group.items()})
    return result


def facets(s, path):
    from ansys.fluent.core.fields.field_data_interfaces import ScalarFieldDataRequest, SurfaceFieldDataRequest, SurfaceDataType
    result = {}
    for name in ['film-mass','film-thickness','film-x-velocity','film-y-velocity','film-z-velocity']:
        payload = s.fields.field_data.get_field_data(ScalarFieldDataRequest(surfaces=['wall'],field_name=name,node_value=False,boundary_value=True))
        result[name] = np.asarray(payload['wall'],dtype=float).reshape(-1)
    geom = s.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=['wall'],data_types=[SurfaceDataType.FacesCentroid]))
    result['centroids'] = np.asarray(geom['wall'].face_centroids,dtype=float).reshape(-1,3)
    if not all(np.isfinite(v).all() for v in result.values()) or np.min(result['film-thickness']) < 0:
        raise RuntimeError('Nonfinite/negative film facets')
    np.savez_compressed(path, **result)
    return result


def reopen(s, pair):
    before = audit(s)
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    after = audit(s)
    if before != after:
        dump(Path(pair['case']).with_suffix('.reopen-diff.json'),{'before':before,'after':after})
        raise RuntimeError('Paired save/reopen audit differs')
    assert_features(s)
    return after


def batch(s, m, work, out, count, label, paths, dt, frozen=False, selected=True):
    n = native_iteration(s)
    initial = clock(s)
    names = [MASS,ACC,DRAIN,DPM,STRIP,SEP,'p72a-e2.7-ewf-thickness-max']
    before = values(s,names)
    transcript = work/(f'{label}-N{n}-{n+count}.txt')
    s.transcript.stop()
    s.transcript.start(file_name=str(transcript),write_to_stdout=False)
    capture = SessionTranscriptCapture(s,stream_path=out/(transcript.stem+'-client.txt'),echo=False).start()
    marker = capture.mark()
    m.update(status='RUNNING',active_stage=label,active_native_start=n,active_target=n+count,
             active_tui_command=f'/solve/iterate {count}')
    dump(out/'run-manifest.json',m)
    start = time.monotonic()
    s.tui.solve.iterate(count)
    capture.wait_until_quiet(timeout_seconds=10,quiet_seconds=.2)
    text = capture.text_since(marker)
    capture.close()
    s.transcript.stop()
    # Persisted paired files form a solver-command barrier. Read native state
    # after it; the TUI return can precede the final film-state update.
    pair = save_pair(s,work/f'{label}-N{n+count}.cas.h5',n+count)
    final = clock(s)
    end = native_iteration(s)
    if end != n+count:
        raise RuntimeError('Native update horizon differs; endpoint preserved')
    histories = {name:history(Path(path).read_text(errors='replace')) for name,path in paths.items()}
    required = set(range(n+1,end+1))
    if any(not required.issubset(h) for h in histories.values()):
        raise RuntimeError('Native report coverage incomplete; endpoint preserved')
    printed = [tuple(map(float,x.groups())) for x in FILM.finditer(text)]
    if len(printed) != count:
        # Native transcript is independent of the client-stream drain.
        text = transcript.read_text(errors='replace')
        printed = [tuple(map(float,x.groups())) for x in FILM.finditer(text)]
    if len(printed) != count:
        raise RuntimeError('Native film-clock coverage incomplete')
    actual_elapsed = final['film_elapsed_time']-initial['film_elapsed_time']
    if not math.isclose(actual_elapsed,count*dt,abs_tol=1e-10,rel_tol=1e-9):
        raise RuntimeError('Actual fixed film step differs')
    ids = list(range(n+1,end+1))
    acc = sum(histories[ACC][i]*dt for i in ids)
    dpm = sum(histories[DPM][i]*dt for i in ids)
    changes = {k:histories[k][end]-before[k] for k in [MASS,DRAIN,STRIP,SEP]}
    residual = sum(changes.values())-acc-dpm
    ledger = 100*abs(residual)/max(abs(acc)+abs(dpm),1e-30)
    fields_path = out/f'{label}-N{end}-facets.npz'
    arrays = facets(s,fields_path)
    record = {'label':label,'native_start':n,'native_end':end,'updates':count,
              'film_start_s':initial['film_elapsed_time'],'film_end_s':final['film_elapsed_time'],
              'fixed_step_s':dt,'frozen_bulk':frozen,'selected':selected,'wall_seconds':time.monotonic()-start,
              'peak_courant':max(x[2] for x in printed),'film_ledger_error_percent':ledger,
              'film_ledger_residual_kg':residual,'integrated_accretion_kg':acc,'integrated_dpm_kg':dpm,
              'ledger_status':'DIAGNOSTIC_SOURCE_TIMING_GAP' if ledger>1 else 'SMALL_SAMPLED_LEDGER_GAP',
              'mass_changes_kg':changes,'final_film_mass_kg':histories[MASS][end],
              'max_thickness_m':float(np.max(arrays['film-thickness'])),
              'facet_file':str(fields_path),'transcript':str(transcript),'pair':pair,'report_paths':paths,
              'inner_residual_rows':len(SUB.findall(text)),
              'inner_residual_limit':'Unavailable under alternative implicit scheme' if parameters(s)['implicit-scheme-new?'] else 'See native transcript'}
    dump(out/(transcript.stem+'-metrics.json'),record)
    m.setdefault('blocks',[]).append(record)
    m['latest_pair'] = pair
    m['verified_native_end'] = end
    m['verified_film_time_s'] = final['film_elapsed_time']
    dump(out/'run-manifest.json',m)
    print('VERIFIED_BATCH',m['speed_m_s'],label,end,round(final['film_elapsed_time']*1000,6),
          'ms',round(histories[MASS][end],6),'kg','ledger',round(ledger,6),flush=True)
    if FATAL.search(text) or not all(math.isfinite(v) for h in histories.values() for v in h.values()):
        raise RuntimeError('Fatal/nonfinite endpoint preserved')
    if record['peak_courant'] > 1 or record['max_thickness_m'] >= parameters(s)['thickness-limit']:
        raise RuntimeError('Film numerical recovery boundary exceeded; endpoint preserved')
    return record, arrays


def compare_fields(a,b):
    if not np.allclose(a['centroids'],b['centroids'],rtol=0,atol=1e-12):
        raise RuntimeError('Facet correspondence differs')
    mass = a['film-mass']
    av = np.stack([a[f'film-{axis}-velocity'] for axis in 'xyz'],axis=1)
    bv = np.stack([b[f'film-{axis}-velocity'] for axis in 'xyz'],axis=1)
    return {'mass_L1_percent':float(100*np.sum(abs(b['film-mass']-mass))/max(np.sum(mass),1e-30)),
            'velocity_difference_percent':float(100*np.sum(mass*np.linalg.norm(bv-av,axis=1))/max(np.sum(mass*np.linalg.norm(av,axis=1)),1e-30)),
            'max_thickness_difference_percent':float(100*abs(np.max(b['film-thickness'])-np.max(a['film-thickness']))/max(np.max(a['film-thickness']),1e-30))}


def qualify(s,m,work,out,paths,reference_dt=.5e-6):
    screen_n = native_iteration(s)
    screen_id = f'{screen_n}-{time.time_ns()}'
    source = save_pair(s,work/f'screen-parent-N{screen_id}.cas.h5',screen_n)
    duration = .0005
    controls(s,{'ewf-adaptive?':False,'timestep-max':reference_dt,'sub-iter-nums':30})
    reference_paths = reports(s,work/f'screen-{screen_id}-reference')
    reference, a = batch(s,m,work,out,round(duration/reference_dt),f'screen-reference-{screen_id}',reference_paths,reference_dt,True,False)
    for dt in [20e-6,10e-6,5e-6,2.5e-6]:
        s.settings.file.read_case(file_name=source['case'])
        s.settings.file.read_data(file_name=source['data'])
        controls(s,{'ewf-adaptive?':False,'timestep-max':dt,'sub-iter-nums':30})
        label = 'screen-'+screen_id+'-'+str(dt*1e6).replace('.','p')+'us'
        # Each sibling gets distinct native report files; selected history is
        # assembled from the recorded per-block sources, never appended joins.
        trial_paths = reports(s,work/f'screen-{screen_id}'/label)
        try:
            trial, b = batch(s,m,work,out,round(duration/dt),label,trial_paths,dt,True,False)
        except RuntimeError as error:
            m.setdefault('screens',[]).append({'passed':False,'step_s':dt,'error':str(error),'parent':source})
            dump(out/'run-manifest.json',m)
            continue
        comparison = compare_fields(a,b)
        passed = comparison['mass_L1_percent'] <= 1 and comparison['velocity_difference_percent'] <= 2 and comparison['max_thickness_difference_percent'] <= 2
        m.setdefault('screens',[]).append({'comparison':comparison,'passed':passed,'reference':reference,'candidate':trial})
        dump(out/'run-manifest.json',m)
        if passed:
            trial['selected'] = True
            dump(out/'run-manifest.json',m)
            dump(out/'selected-screen.json',m['screens'][-1])
            return dt, trial_paths
    s.settings.file.read_case(file_name=reference['pair']['case'])
    s.settings.file.read_data(file_name=reference['pair']['data'])
    reference['selected'] = True
    m['latest_pair'] = reference['pair']
    m['verified_native_end'] = reference['native_end']
    m['verified_film_time_s'] = reference['film_end_s']
    m.setdefault('step_limits',[]).append('Acceleration screen failed; use the conservative reference step')
    dump(out/'run-manifest.json',m)
    return reference_dt, reference_paths


def run_case(s,speed):
    label = str(speed).replace('.','p')
    attempt = 0
    base_label = label
    while (WORK/label).exists() or (OUT/label).exists():
        attempt += 1
        label = base_label + f'-retry{attempt}'
    work = WORK/label
    out = OUT/label
    work.mkdir(exist_ok=False)
    out.mkdir(parents=True,exist_ok=False)
    m = {'status':'PREPARING','speed_m_s':speed,'target_film_time_s':TARGET,
         'work':str(work),'output':str(out),'execution':'direct-fluent-use','blocks':[],
         'parent_case':str(WORK/'inputs/prepared-A-N1580.cas.h5'),
         'parent_data':str(WORK/'inputs/prepared-A-N1580.dat.h5')}
    dump(out/'run-manifest.json',m)
    try:
        s.settings.file.read_case(file_name=m['parent_case'])
        s.settings.file.read_data(file_name=m['parent_data'])
        parent_params = parameters(s)
        s.settings.file.auto_save.data_frequency = 0
        s.tui.define.models.eulerian_wallfilm.model_options(*MODEL_ARGS)
        # Filled from the verified boundary TUI recipe before execution.
        apply_wall_tui(s)
        actual = parameters(s)
        if {k:v for k,v in actual.items() if parent_params.get(k)!=v} != FEATURES:
            raise RuntimeError('Unexpected physical option delta')
        assert_features(s)
        m['feed_quarter'] = feed(s,speed,.25)
        paths = reports(s,work)
        m['report_paths'] = paths
        prepared = save_pair(s,work/'prepared-A-N1580.cas.h5',1580)
        m['prepared_reopen'] = reopen(s,prepared)
        m['prepared_pair'] = prepared
        if native_iteration(s)!=1580 or clock(s)['film_elapsed_time']!=0:
            raise RuntimeError('Parent coordinate or dry clock differs')
        dump(out/'run-manifest.json',m)
        return continue_case(s,m,work,out,paths)
    except Exception:
        m.update(status='RECOVERY_REQUIRED',error=traceback.format_exc())
        dump(out/'run-manifest.json',m)
        raise


def continue_case(s,m,work,out,paths):
    speed = m['speed_m_s']
    if clock(s)['film_elapsed_time'] > .0035+1e-12:
        return develop_case(s,m,work,out,paths)
    if native_iteration(s) < 2080:
        batch(s,m,work,out,min(20,2080-native_iteration(s)),'low-smoke',paths,1e-6)
    if native_iteration(s) < 2080:
        batch(s,m,work,out,2080-native_iteration(s),'low-hold',paths,1e-6)
    # Exact original ramp writes retained; ten-update blocks are deliberate.
    ramp_start = max(0,native_iteration(s)-2080)
    s.transcript.start(file_name=str(work/f'ramp-native-from-{ramp_start}.txt'),write_to_stdout=False)
    for r in range(ramp_start,2000,10):
        written = feed(s,speed,.25+.75*r/2000)
        m.update(status='RUNNING',active_stage='ramp',active_target=2080+r+10)
        m.setdefault('ramp_commands',[]).append({'r':r,'feed':written})
        s.tui.solve.iterate(10)
        if (r+10)%500==0:
            n = native_iteration(s)
            stem = work/f'ramp-N{n}.cas.h5'
            if stem.exists():
                stem = work/f'ramp-N{n}-recovery-{time.time_ns()}.cas.h5'
            pair = save_pair(s,stem,n)
            m.update(latest_pair=pair,verified_native_end=n,verified_film_time_s=clock(s)['film_elapsed_time'])
            dump(out/'run-manifest.json',m)
            print('RAMP_CHECKPOINT',speed,n,flush=True)
    s.transcript.stop()
    feed(s,speed,1.)
    if native_iteration(s) < 5080:
        batch(s,m,work,out,5080-native_iteration(s),'full-feed-hold',paths,1e-6)
    m['startup_pair'] = m['latest_pair']
    m['startup_film_time_s'] = clock(s)['film_elapsed_time']
    if not math.isclose(m['startup_film_time_s'],.0035,abs_tol=1e-12):
        raise RuntimeError('Startup film horizon differs')
    if 'full_bulk_equations' not in m:
        m['full_bulk_equations'] = s.settings.solution.controls.equations.get_state()
    for name in m['full_bulk_equations']:
        s.settings.solution.controls.equations[name]=False
    # The Student TUI hides this beta menu. The reference run uses the same
    # native numerical parameter; apply and verify it without changing physics.
    controls(s,{'implicit-scheme-new?':True})
    m['bulk_development_policy'] = 'FROZEN_AFTER_SPEED_SPECIFIC_STARTUP'
    return develop_case(s,m,work,out,paths)


def develop_case(s,m,work,out,paths):
    speed = m['speed_m_s']
    dt, paths = qualify(s,m,work,out,paths)
    next_review = .05 * (math.floor(clock(s)['film_elapsed_time']/.05)+1)
    while clock(s)['film_elapsed_time'] < TARGET-1e-10:
        remaining = TARGET-clock(s)['film_elapsed_time']
        count = min(1000,max(1,int(math.floor((remaining+1e-12)/dt))))
        if remaining < dt:
            dt = remaining
            controls(s,{'timestep-max':dt})
        batch(s,m,work,out,count,f'develop-{len(m["blocks"]):03d}',paths,dt,True)
        if clock(s)['film_elapsed_time'] >= next_review and clock(s)['film_elapsed_time'] < TARGET-.001:
            # Requalify on developed fields. Every stage preserves its
            # selected path; added film time belongs to the chosen arm only.
            dt, paths = qualify(s,m,work,out,paths,2.5e-6)
            next_review += .05
    m['final_pair'] = m['latest_pair']
    m['final_reopen'] = reopen(s,m['final_pair'])
    m.update(status='COMPLETE',actual_film_time_s=clock(s)['film_elapsed_time'],
             native_end=native_iteration(s),solver_left_open=True)
    dump(out/'run-manifest.json',m)
    print('CASE_COMPLETE',speed,m['actual_film_time_s'],flush=True)
    return m

def apply_wall_tui(s):
    s.scheme.eval('(ti-menu-load-string "/define/boundary-conditions/set/wall wall () mixture film-splash-wall? yes film-boundary-separation? yes quit")')


def run_all(s):
    manifest = {'status':'RUNNING','speeds_m_s':list(SPEEDS),'target_film_time_s':TARGET,'cases':[]}
    dump(OUT/'campaign-manifest.json',manifest)
    try:
        for speed in SPEEDS:
            result=run_case(s,speed)
            manifest['cases'].append({'speed_m_s':speed,'manifest':str(Path(result['output'])/'run-manifest.json'),'final_pair':result['final_pair']})
            dump(OUT/'campaign-manifest.json',manifest)
        manifest['status']='COMPLETE_ANALYSIS_REQUIRED'
        dump(OUT/'campaign-manifest.json',manifest)
    except Exception:
        manifest.update(status='RECOVERY_REQUIRED',error=traceback.format_exc())
        dump(OUT/'campaign-manifest.json',manifest)
        raise


def complete_campaign(s, active_manifest, middle_result=None):
    """Finish an already-started middle case and both independent speed cases."""
    manifest = {'status':'RUNNING','speeds_m_s':list(SPEEDS),
                'target_film_time_s':TARGET,'cases':[]}
    dump(OUT/'campaign-manifest.json',manifest)
    try:
        if middle_result is None or middle_result.get('status') != 'COMPLETE':
            work = Path(active_manifest['work'])
            out = Path(active_manifest['output'])
            # The active local endpoint is preserved. The next stage uses the
            # native coordinate, not a requested or cached iteration count.
            active_manifest.pop('error',None)
            safe = [b for b in active_manifest['blocks'] if b['selected'] and b['peak_courant']<=1
                    and b['film_ledger_error_percent']<=1]
            if safe:
                prior = safe[-1]
                s.settings.file.read_case(file_name=prior['pair']['case'])
                s.settings.file.read_data(file_name=prior['pair']['data'])
                paths = prior['report_paths']
            else:
                paths = active_manifest['report_paths']
            middle_result = continue_case(s,active_manifest,work,out,paths)
        for speed in SPEEDS:
            result = middle_result if speed == 26.81 else run_case(s,speed)
            manifest['cases'].append({'speed_m_s':speed,'manifest':str(Path(result['output'])/'run-manifest.json'),
                                      'final_pair':result['final_pair']})
            dump(OUT/'campaign-manifest.json',manifest)
        analyse_campaign(manifest)
        manifest['status']='COMPLETE'
        dump(OUT/'campaign-manifest.json',manifest)
        print('THREE_SPEED_CAMPAIGN_COMPLETE',flush=True)
    except Exception:
        manifest.update(status='RECOVERY_REQUIRED',error=traceback.format_exc())
        dump(OUT/'campaign-manifest.json',manifest)
        raise


def analyse_campaign(manifest):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data = []
    summary = []
    for item in sorted(manifest['cases'],key=lambda x:x['speed_m_s']):
        m = json.loads(Path(item['manifest']).read_text())
        if m['status'] != 'COMPLETE' or abs(m['actual_film_time_s']-TARGET)>1e-9:
            raise RuntimeError('Analysis requires three verified endpoints')
        names = [MASS,ACC,DRAIN,DPM,STRIP,SEP]
        points = {}
        startup = {name:history(Path(m['report_paths'][name]).read_text()) for name in names}
        for n in range(1581,5081):
            points[(n-1580)*1e-6] = [startup[name][n] for name in names]
        for block in m['blocks']:
            if not block['selected'] or not block['frozen_bulk']:
                continue
            h = {name:history(Path(block['report_paths'][name]).read_text()) for name in names}
            for n in range(block['native_start']+1,block['native_end']+1):
                t = block['film_start_s']+(n-block['native_start'])*block['fixed_step_s']
                points[t] = [h[name][n] for name in names]
        times = np.array(sorted(points))
        rows = np.array([points[t] for t in times])
        fields = np.load(m['blocks'][-1]['facet_file'])
        selected = [b for b in m['blocks'] if b['selected']]
        summary.append({'speed_m_s':m['speed_m_s'],'film_time_ms':m['actual_film_time_s']*1000,
                        'film_mass_kg':float(rows[-1,0]),'stripped_mass_kg':float(rows[-1,4]),
                        'separated_mass_kg':float(rows[-1,5]),'max_thickness_mm':float(np.max(fields['film-thickness'])*1000),
                        'peak_selected_courant':max(b['peak_courant'] for b in selected),
                        'max_selected_ledger_error_percent':max(b['film_ledger_error_percent'] for b in selected),
                        'manifest':item['manifest'],'final_pair':m['final_pair']})
        data.append((m,times,rows,fields))
    dump(OUT/'comparison.json',summary)
    fig, axes = plt.subplots(2,1,figsize=(8,6),sharex=True)
    for m,t,rows,_ in data:
        label=f"{m['speed_m_s']:.2f} m/s"
        axes[0].plot(t*1000,rows[:,0],label=label)
        axes[1].plot(t*1000,rows[:,4]+rows[:,5],label=label)
    axes[0].set_ylabel('Film inventory (kg)')
    axes[1].set_ylabel('Stripped + separated mass (kg)')
    axes[1].set_xlabel('Native EWF elapsed time (ms)')
    for ax in axes:
        ax.axvline(3.5,color='gray',linestyle=':',linewidth=1)
        ax.grid(alpha=.25)
    axes[0].legend()
    fig.suptitle('Re-entrainment speed sensitivity; bulk frozen after 3.5 ms')
    fig.tight_layout()
    fig.savefig(OUT/'film-and-reentrainment.png',dpi=160)
    plt.close(fig)
    vmax=max(np.max(f['film-thickness'])*1000 for _,_,_,f in data)
    fig, axes=plt.subplots(1,3,figsize=(12,5),subplot_kw={'projection':'3d'})
    for ax,(m,_,_,fields) in zip(axes,data):
        c=fields['centroids']
        artist=ax.scatter(c[:,0],c[:,1],c[:,2],c=fields['film-thickness']*1000,s=3,vmin=0,vmax=vmax,cmap='viridis')
        ax.set_title(f"{m['speed_m_s']:.2f} m/s; 250 ms")
        ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)'); ax.set_zlabel('z (m)')
        ax.set_box_aspect(np.ptp(c,axis=0))
    fig.colorbar(artist,ax=axes,shrink=.65,label='Film thickness (mm)',pad=.08)
    fig.savefig(OUT/'endpoint-film-thickness.png',dpi=160,bbox_inches='tight')
    plt.close(fig)
    project = ROOT.parent/'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/reentrainment-speed-sensitivity'
    relative = '../../../../../../PyAnsys/output/phase72a-reentrainment-speeds/20261006/'
    lines=['# Local re-entrainment speed sensitivity — results','',
           '| Speed (m/s) | Film time (ms) | Film mass (kg) | Stripped (kg) | Separated (kg) | Maximum thickness (mm) |',
           '| ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in summary:
        lines.append(f"| {r['speed_m_s']:.2f} | {r['film_time_ms']:.6f} | {r['film_mass_kg']:.6f} | {r['stripped_mass_kg']:.6g} | {r['separated_mass_kg']:.6g} | {r['max_thickness_mm']:.6f} |")
    lines += ['',f'![Film inventory and re-entrainment]({relative}film-and-reentrainment.png)','',
              f'![Endpoint native wall-film thickness]({relative}endpoint-film-thickness.png)','',
              '| Evidence / limit | Meaning |','| --- | --- |',
              '| Three paired endpoints | Native clock reached 250 ms; saved cases were reopened and checked |',
              '| Fixed carrier fields after 3.5 ms | Finite-time film response to each speed-specific startup field |',
              '| Stripping and separation | Internal liquid transfer; not external separator removal |',
              f"| Sampled film ledger | Largest selected-block gap: {max(r['max_selected_ledger_error_percent'] for r in summary):.4f}%; DPM source timing is not fully reconciled; no exact conservation claim |",
              '| Alternative implicit EWF | Inner residual evidence is limited; matched-time timestep screens are local checks |',
              '| Stationarity and validation | This endpoint does not establish steady film, mesh convergence or physical validation |','',
              f'[Machine comparison and endpoint hashes]({relative}comparison.json)','']
    (project/'results.md').write_text('\n'.join(lines),encoding='utf-8')
    state_path = ROOT.parent/'Project/experiments/phase-07-2a-wall-liquid-routing/phase-state.yaml'
    state_text = state_path.read_text(encoding='utf-8')
    match = re.search(r'(?m)^local_reentrainment_speed_sensitivity:\n(?:[ \t].*\n)*',state_text)
    if match:
        block = re.sub(r'(?m)^  status: .*$', '  status: COMPLETE_THREE_250MS_ENDPOINTS',match.group())
        block += '  results: Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/reentrainment-speed-sensitivity/results.md\n'
        block += '  completed_speeds_m_s: [20.11, 26.81, 32.14]\n'
        state_path.write_text(state_text[:match.start()]+block+state_text[match.end():],encoding='utf-8')
