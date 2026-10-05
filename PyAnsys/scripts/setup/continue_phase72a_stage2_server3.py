"""Verified N45606 transfer and bounded aggressive EWF continuation on Server 3.

Attach only. Preserve Stage 3, never initialize, use local paired checkpoints.
Operations are separate so the first 100 updates can be judged before compute.
"""
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import argparse
import json
import math
import re
import sys
import subprocess
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
from continue_phase72a_stage3_adaptive import attach, clocks_and_residuals
from run_phase72a_stage3_server3 import state, instrument, iterate, powershell
from run_phase72a_local_film_replay import require_match
from run_phase72a_e27_server1_continuation import native_iteration, pair_save, dump
from run_phase72a_adaptive_film import history, FILM, ROW
from pyansys_fluent.common import remote_chdir
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256, configure_autosave

OUT = ROOT / 'output/phase72a-stage2-server3/20261005'
WORK = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\ContactAbsorber\server3-aggressive-20261005')
PARENT = ROOT / 'output/phase72a-adaptive-server1/20261005/recovered-N45606'
DELTA = {'ewf-adaptive?': True, 'courant-number': .15, 'adapt-tstp-inc': 1.3,
         'adapt-tstp-dec': 2.0, 'adapt-init-dt': 2e-6}
SUB = re.compile(r'sub-iteration:\s*(\d+) residual - h:\s*([^;]+); u:\s*([^;]+); v:\s*(\S+)')
MANIFEST = OUT / 'run-manifest.json'
VARIANT = 'aggressive'


def film(s):
    return dict(s.rp_vars('wall-film/solution-state'))


def save(s, label):
    return pair_save(s, WORK / f'{label}.cas.h5', WORK / 'scratch', scratch_tag=label)


def analyse():
    subprocess.run([sys.executable, str(ROOT / 'scripts/analysis/analyze_phase72a_stage2_server3.py'), '--variant', VARIANT], check=True)


def share_final(s, m):
    """Share only the selected final pair and library, with destination hashes."""
    durable = PureWindowsPath(r'C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\ContactAbsorber\server3-aggressive-20261005') / f"N{m['verified_native_end']}"
    if VARIANT=='moderate':
        durable=durable.parent/'moderate-restart'/durable.name
    ensure_remote_directory(s, str(durable))
    receipt = {}
    for kind in ['case', 'data']:
        source=m['latest_pair'][kind]
        dest=durable / PureWindowsPath(source).name
        assert powershell(s, f"$ErrorActionPreference='Stop'; if(Test-Path -LiteralPath '{dest}'){{throw 'Exists'}}; Copy-Item -LiteralPath '{source}' -Destination '{dest}'") == 0
        observed=remote_file_sha256(s,str(dest),str(WORK/'scratch'/f"shared-N{m['verified_native_end']}-{kind}.sha"))
        assert observed == m['latest_pair'][kind+'_sha256']
        receipt[kind]=str(dest)
        receipt[kind+'_sha256']=observed
    receipt['status']='SERVER3_DESTINATION_HASH_VERIFIED_CLOUD_SYNC_UNVERIFIED'
    receipt['library_archive']=r'C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\ContactAbsorber\local20000\20261004T081120Z\contact-libraries.zip'
    m['shared_final_pair']=receipt
    dump(MANIFEST,m)


def invariant(actual, original):
    for group in ['hooks', 'lower_film_wall', 'entry_faces', 'dpm', 'controls']:
        if actual['readback'][group] != original['readback'][group]:
            raise RuntimeError(f'Scientific invariant changed: {group}')
    assert actual['methods'] == original['methods']
    assert actual['setup'] == original['setup'], 'Mesh/model/feed/setup invariant changed'
    for k, v in original['film_model'].items():
        assert actual['film_model'][k] == DELTA.get(k, v), k


def prepare(s):
    if MANIFEST.exists():
        raise RuntimeError('Existing run must be reconciled before preparation')
    OUT.mkdir(parents=True, exist_ok=True)
    assert s.settings.solution.run_calculation.iterate.is_active()
    if VARIANT=='aggressive':
        assert native_iteration(s)==8000
    else:
        previous_out=ROOT/'output/phase72a-stage2-server3/20261005'
        previous=json.loads((previous_out/'run-manifest.json').read_text())
        assert previous['status']=='SMOKE_COMPLETE'
        assert native_iteration(s)==previous['verified_native_end']
    for folder in [WORK, WORK / 'scratch', WORK / 'monitors', WORK / 'autosave']:
        ensure_remote_directory(s, str(folder))
    m = {'status': 'PRESERVING_STAGE3', 'server_id': '3',
         'authority': 'human_2026_10_05_full_server3_continue_N45606_aggressive_ewf',
         'host': s.scheme.eval('(getenv "COMPUTERNAME")'), 'version': str(s.get_fluent_version()),
         'parent_native_iteration': 45606, 'controlled_delta': DELTA,
         'adaptive_ceiling': 'NOT_VERIFIED; timestep-max unchanged and not treated as ceiling',
         'work_root': str(WORK), 'blocks': [], 'solver_left_open': True,
         'lineage': 'N45606 from independent local four-rank N33586, not separate Server1 N23586 branch',
         'film_horizon_corrected_restart_s': .2, 'max_additional_updates': 80000 if VARIANT=='moderate' else 40000,
         'variant':VARIANT}
    dump(MANIFEST, m)
    prior = state(s)
    if VARIANT=='aggressive':
        ref3 = json.loads((ROOT / 'output/phase72a-stage3-server3/20261005/adaptive-aggressive-N6000-N8000/endpoint-N8000.json').read_text())
        require_match(prior['readback'], ref3['state']['readback'])
        preserved=save(s,'preserved-stage3-N8000')
        m['preserved_stage3_pair']=preserved
    else:
        ref=json.loads((previous_out/f"endpoint-N{previous['verified_native_end']}.json").read_text())
        require_match(prior['readback'],ref['state']['readback'])
        preserved=save(s,f"preserved-aggressive-probe-N{previous['verified_native_end']}")
        m['preserved_probe_pair']=preserved
        m['preserved_stage3_pair']=previous['preserved_stage3_pair']
        m['excluded_probe_manifest']=str(previous_out/'run-manifest.json')
        m['excluded_probe_reason']='6.416 and 3.208 microsecond probes did not provide sustained inner-film convergence; restart exact original fields'
    s.settings.file.read_case(file_name=preserved['case'])
    s.settings.file.read_data(file_name=preserved['data'])
    require_match(state(s)['readback'], prior['readback'])
    m['stage3_preservation_reopen'] = 'PASS'
    dump(MANIFEST, m)
    source = json.loads((PARENT / 'shared-endpoint.json').read_text())['pair']
    for kind in ['case', 'data']:
        assert remote_file_sha256(s, source[kind], str(WORK / 'scratch' / f'source-{kind}.sha')) == source[kind + '_sha256']
        dest = WORK / PureWindowsPath(source[kind]).name
        assert powershell(s, f"$ErrorActionPreference='Stop'; if(Test-Path -LiteralPath '{dest}'){{throw 'Exists'}}; Copy-Item -LiteralPath '{source[kind]}' -Destination '{dest}'") == 0
        assert remote_file_sha256(s, str(dest), str(WORK / 'scratch' / f'copied-{kind}.sha')) == source[kind + '_sha256']
        m.setdefault('parent_pair', {})[kind] = str(dest)
        m['parent_pair'][kind + '_sha256'] = source[kind + '_sha256']
    # Library archive was verified and unpacked for Stage 3 on this same host.
    archive = PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage3\20261005\contact-libraries.zip')
    assert remote_file_sha256(s, str(archive), str(WORK / 'scratch/library.sha')) == '446428fb0d41e98efb55454f30dff656c935d044cfb6229669c9dab05507be3e'
    assert powershell(s, f"$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath '{archive}' -DestinationPath '{WORK}'") == 0
    remote_chdir(s, str(WORK))
    s.transcript.start(file_name=str(OUT / 'parent-load.txt'), write_to_stdout=False)
    s.settings.file.read_case(file_name=m['parent_pair']['case'])
    s.settings.setup.user_defined.load(udf_library_name='libcontactv2')
    s.settings.file.read_data(file_name=m['parent_pair']['data'])
    s.transcript.stop()
    assert native_iteration(s) == 45606
    original = state(s)
    expected = json.loads((PARENT / 'endpoint.json').read_text())['readback']
    cached = {'v2-flux-phase2-liquidinlet', 'v2-flux-phase2-liquidinlet(User Mass Source)',
              'v2-flux-phase2-steamoutlet', 'v2-flux-phase2-steamoutlet(User Mass Source)', 'v2-applied-absorber'}
    cleaned = lambda v: {**v, 'fields': {k: x for k, x in v['fields'].items() if k not in cached}}
    require_match(cleaned(original['readback']), cleaned(expected))
    if not math.isclose(-original['readback']['fields']['v2-applied-absorber'][0], original['readback']['fields']['p72-contact-removal'][0], rel_tol=1e-9):
        raise RuntimeError('Loaded contact source differs from independent depletion expression')
    clock = film(s)
    expected_clock = dict(json.loads((PARENT / 'native-film-solution-state.json').read_text()))
    assert clock == expected_clock
    dump(OUT / 'loaded-parent.json', {'state': original, 'film': clock})
    m['parent_film_clock_s'] = clock['film_elapsed_time']
    m['corrected_restart_film_clock_s'] = .08
    params = s.rp_vars('wall-film/model-parameters')
    s.rp_vars('wall-film/model-parameters', [(k, DELTA.get(k, v)) for k, v in params])
    m['report_paths'] = instrument(s, WORK / 'monitors')
    configure_autosave(s, str(WORK / 'autosave'), data_frequency=1000)
    s.settings.file.auto_save.retain_most_recent_files = False
    prepared = state(s)
    invariant(prepared, original)
    require_match({'fields': prepared['readback']['fields']}, {'fields': original['readback']['fields']})
    m['prepared_pair'] = save(s, 'prepared-N45606')
    s.settings.file.read_case(file_name=m['prepared_pair']['case'])
    s.settings.file.read_data(file_name=m['prepared_pair']['data'])
    require_match(state(s)['readback'], prepared['readback'])
    assert film(s) == clock
    dump(OUT / 'prepared-reopen.json', {'state': state(s), 'film': film(s), 'checks': 'PASS'})
    m.update(status='PREPARED_VERIFIED', verified_native_end=45606, parent_verification='HASH_SETTINGS_INVENTORIES_BOUNDARY_FLUXES_FILM_CLOCK_AND_SOURCE', prepared_reopen='PASS')
    dump(MANIFEST, m)
    print('PREPARED_VERIFIED_N45606', flush=True)


def collect(s, m, start, end, initial, final, before_fields, path):
    histories = {}
    for name, remote in m['report_paths'].items():
        raw = read_text(s, remote)
        (OUT / f'{name}.out').write_text(raw)
        h = history(raw)
        assert set(range(45607, end + 1)).issubset(h), name
        assert all(math.isfinite(v) for v in h.values()), name
        histories[name] = h
    dump(OUT / 'report-histories.json', {k: {'iterations': sorted(h), 'values': [h[i] for i in sorted(h)], 'file': m['report_paths'][k]} for k, h in histories.items()})
    text = path.read_text()
    clocks, residuals, terminal = clocks_and_residuals(text, start, end, final['film_elapsed_time'])
    ewf, pending, lastfilm = {}, [], None
    for line in text.splitlines():
        match = SUB.search(line)
        if match:
            pending.append([int(match[1]), *map(float, match.groups()[1:])])
        if FILM.search(line):
            lastfilm = pending
            pending = []
        row = ROW.match(line)
        if row and start < int(row[1]) <= end and lastfilm:
            ewf[int(row[1])] = lastfilm
            lastfilm = None
    if lastfilm and end not in ewf:
        ewf[end] = lastfilm
    assert set(ewf) == set(range(start + 1, end + 1)), 'Film inner residual coverage incomplete'
    dump(OUT / f'clocks-N{start}-N{end}.json', clocks)
    dump(OUT / f'carrier-residuals-N{start}-N{end}.json', residuals)
    dump(OUT / f'film-residuals-N{start}-N{end}.json', ewf)
    assert final['max_timestep_count'] - initial['max_timestep_count'] == end - start
    mass = histories['p72a-e2.7-ewf-film-mass-total']
    drain = histories['p72a-e2.7-ewf-outflow-mass-total']
    acc = histories['p72a-e2.7-ewf-secondary-phase-mass-total']
    t0 = initial['film_elapsed_time']
    integral, exact_dt = 0., {}
    for n in range(start + 1, end + 1):
        dt = clocks[n][0] - t0
        assert dt > 0
        exact_dt[n] = dt
        integral += dt * acc[n]
        t0 = clocks[n][0]
    elapsed = final['film_elapsed_time'] - initial['film_elapsed_time']
    gain = mass[end] - before_fields['p72a-e2.7-ewf-film-mass-total'][0]
    drained = drain[end] - before_fields['p72a-e2.7-ewf-outflow-mass-total'][0]
    bad = [n for n, rows in ewf.items() if max(rows[-1][1:]) > 1]
    met = {'native_start': start, 'native_end': end, 'updates': end-start, 'added_film_time_s': elapsed,
           'native_film_clock_s': final['film_elapsed_time'], 'corrected_restart_added_time_s': final['film_elapsed_time']-.08,
           'actual_final_step_s': final['film_timestep'], 'peak_film_cfl': max(v[2] for v in clocks.values()),
           'film_inventory_kg': mass[end], 'inventory_gain_kg': gain, 'storage_kg_s': gain/elapsed,
           'accretion_kg_s': integral/elapsed, 'drainage_kg_s': drained/elapsed,
           'drainage_deficit_percent': 100*(integral-drained)/integral,
           'film_ledger_error_percent': 100*abs(gain+drained-integral)/abs(integral),
           'maximum_thickness_m': max(histories['p72a-e2.7-ewf-thickness-max'][n] for n in range(start+1,end+1)),
           'film_residual_updates': len(ewf), 'film_final_residual_above_1_updates': len(bad),
           'film_final_residual_above_1_percent': 100*len(bad)/(end-start),
           'film_final_residual_max': [max(rows[-1][k] for rows in ewf.values()) for k in [1,2,3]],
           'film_all_final_residuals_below_1e5_minus_percent': 100*sum(max(r[-1][1:]) <= 1e-5 for r in ewf.values())/len(ewf),
           'terminal_mapping': terminal, 'time_basis': 'Native endpoint clock and per-update printed clocks; rounded intermediate times',
           'claim_limit': 'Film-side ledger only; no whole-separator or timestep-independent qualification'}
    return met


def block(s, m, steps):
    start = native_iteration(s)
    assert start == m['verified_native_end']
    end = start + steps
    original = json.loads((OUT / 'loaded-parent.json').read_text())['state']
    before = state(s)
    invariant(before, original)
    initial = film(s)
    path = OUT / f'batch-N{start}-N{end}.txt'
    assert not path.exists()
    s.transcript.start(file_name=str(path), write_to_stdout=False)
    # Native server transcript survives a client stream failure.
    remote_log = str(WORK / f'native-N{start}-N{end}.trn').replace('\\', '/')
    s.scheme.eval(f'(ti-menu-load-string "/file/start-transcript \\\"{remote_log}\\\"")')
    m.update(status='RUNNING', active_native_window=[start,end], command=f'/solve/iterate {steps}', started_utc=datetime.now(timezone.utc).isoformat())
    dump(MANIFEST, m)
    print('SUBMIT', start, end, flush=True)
    begun = time.monotonic()
    iterate(s, steps)
    current = state(s)
    invariant(current, original)
    pair = save(s, f'checkpoint-N{end}')
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(state(s)['readback'], current['readback'])
    final = film(s)
    s.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
    time.sleep(.5)
    s.transcript.stop()
    native_text = read_text(s, str(WORK / f'native-N{start}-N{end}.trn'))
    native_path = OUT / f'native-N{start}-N{end}.trn'
    native_path.write_text(native_text)
    met = collect(s, m, start, end, initial, final, before['readback']['fields'], native_path)
    met['wall_seconds'] = time.monotonic()-begun
    dump(OUT / f'endpoint-N{end}.json', {'pair': pair, 'state': state(s), 'film': final, 'metrics': met, 'reopen': 'PASS'})
    m['blocks'].append(met)
    m.update(status='BLOCK_COMPLETE', verified_native_end=end, latest_pair=pair, final_reopen='PASS', latest_metrics=met)
    dump(MANIFEST, m)
    print('BLOCK_COMPLETE', json.dumps(met), flush=True)
    analyse()
    if met['peak_film_cfl'] > 1 or met['maximum_thickness_m'] > .003 or met['film_inventory_kg'] > 12.3 or met['film_ledger_error_percent'] > 1:
        raise RuntimeError('Declared numerical recovery bound exceeded; endpoint preserved')
    return met


def run(s, operation):
    m = json.loads(MANIFEST.read_text())
    DELTA.update(m['controlled_delta'])
    if m['status'] not in ['PREPARED_VERIFIED', 'SMOKE_COMPLETE', 'BLOCK_COMPLETE']:
        raise RuntimeError('Reconcile previous run before solve')
    if operation in ['smoke', 'probe']:
        if operation == 'smoke':
            assert native_iteration(s) == 45606
        block(s, m, 100)
        m['status'] = 'SMOKE_COMPLETE'
        dump(MANIFEST,m)
        analyse()
        return
    while m['verified_native_end']-45606 < m['max_additional_updates']:
        met = block(s,m,1000)
        # Preserve the aggressive contrast, then require numerical repair for
        # sustained severe inner-film failure before committing a longer run.
        if met['film_final_residual_above_1_percent'] > 20:
            m['status']='INNER_FILM_RECOVERY_REQUIRED'
            dump(MANIFEST,m)
            analyse()
            return 2
        tail = m['blocks'][-3:]
        stationary = len(tail)==3 and all(x['updates']==1000 and abs(x['drainage_deficit_percent'])<1 and x['film_ledger_error_percent']<.1 and x['film_final_residual_above_1_updates']==0 and x['film_all_final_residuals_below_1e5_minus_percent']>=99 for x in tail)
        if stationary or met['corrected_restart_added_time_s'] >= m['film_horizon_corrected_restart_s']:
            m.update(status='BOUNDED_HORIZON_COMPLETE', film_stationarity_screen=bool(stationary), idle=s.settings.solution.run_calculation.iterate.is_active(), completed_utc=datetime.now(timezone.utc).isoformat())
            dump(MANIFEST,m)
            share_final(s,m)
            analyse()
            return 0
    m['status']='UPDATE_BUDGET_COMPLETE_HORIZON_NOT_REACHED'
    dump(MANIFEST,m)
    return 2


def repair(s, operation):
    """Preserve an assessed probe and verify one numerical repair without solve."""
    m=json.loads(MANIFEST.read_text())
    assert m['status'] in ['SMOKE_COMPLETE', 'BLOCK_COMPLETE', 'INNER_FILM_RECOVERY_REQUIRED']
    assert native_iteration(s)==m['verified_native_end']
    before=state(s)
    clock=film(s)
    delta={'sub-iter-nums':30} if operation=='repair-inner' else {'courant-number':.08}
    if operation=='repair-inner':
        assert before['film_model']['sub-iter-nums']==10
    elif operation=='repair-step':
        assert before['film_model']['courant-number']==.15
    params=s.rp_vars('wall-film/model-parameters')
    s.rp_vars('wall-film/model-parameters',[(k,delta.get(k,v)) for k,v in params])
    DELTA.update(m['controlled_delta'])
    DELTA.update(delta)
    after=state(s)
    invariant(after,json.loads((OUT/'loaded-parent.json').read_text())['state'])
    require_match({'fields':after['readback']['fields']},{'fields':before['readback']['fields']})
    pair=save(s,f"{operation}-prepared-N{m['verified_native_end']}")
    s.settings.file.read_case(file_name=pair['case'])
    s.settings.file.read_data(file_name=pair['data'])
    require_match(state(s)['readback'],after['readback'])
    assert film(s)==clock
    m['controlled_delta']=dict(DELTA)
    if operation=='repair-step':
        m['max_additional_updates']=60000
    m.setdefault('numerical_repairs',[]).append({'native_iteration':m['verified_native_end'],'delta':delta,'pair':pair,'reopen':'PASS','reason':'Severe final inner-film residuals in aggressive probe'})
    m.update(status='PREPARED_VERIFIED',latest_pair=pair)
    dump(MANIFEST,m)
    print('NUMERICAL_REPAIR_VERIFIED',json.dumps(delta),flush=True)


def main():
    global OUT,WORK,MANIFEST,VARIANT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['prepare','smoke','probe','repair-inner','repair-step','run'])
    parser.add_argument('--variant',choices=['aggressive','moderate'],default='aggressive')
    args=parser.parse_args()
    VARIANT=args.variant
    if VARIANT=='moderate':
        OUT=OUT/'moderate-restart'
        WORK=WORK/'moderate-restart'
        MANIFEST=OUT/'run-manifest.json'
        DELTA.update({'courant-number':.06,'sub-iter-nums':30})
    s=attach()
    try:
        if args.operation=='prepare':
            return prepare(s)
        if args.operation in ['repair-inner','repair-step']:
            return repair(s,args.operation)
        return run(s,args.operation)
    except Exception:
        if MANIFEST.exists():
            m=json.loads(MANIFEST.read_text())
            m.update(status='RECOVERY_REQUIRED', error=traceback.format_exc())
            dump(MANIFEST,m)
        raise


if __name__=='__main__':
    raise SystemExit(main())
