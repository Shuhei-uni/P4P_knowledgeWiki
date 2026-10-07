"""Set the human's 0.3 m limit on verified Server 1 N40483; no solver updates."""
from pathlib import Path, PureWindowsPath
import functools
import json
import math
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts/setup'),str(ROOT/'src')]
import run_phase72a_stage4_setting_sensitivity as q
from pyansys_fluent.film_thickness_guard import assess_thickness
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256

OUT=ROOT/'output/phase72a-stage4-film-limit/20261007'
WORK=PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\film-limit-20261007')
MANIFEST=OUT/'run-manifest.json'


def live(s):
    return {'native_iteration':q.r.parent.native_iteration(s),'film':q.r.film(s),
            'audit':q.r.audit(s),'state':q.r.state(s),'fields':q.r.fields(s)}


def unchanged(before,after,*,changed_limit=False):
    assert after['native_iteration']==before['native_iteration']==40483
    assert after['film']==before['film'], 'Native film clock or solution state changed'
    assert after['state']['setup']==before['state']['setup']
    assert after['state']['methods']==before['state']['methods']
    expected=json.loads(json.dumps(before['state']['readback']))
    if changed_limit:expected['film_parameters']['thickness-limit']=.3
    q.r.require_match(after['state']['readback'],expected)
    # The instantaneous secondary-phase source is cleared on reload; it is not a persisted stock.
    stable=lambda x:{k:v for k,v in x['fields'].items() if k!=q.r.ACC}
    q.r.require_match({'fields':stable(after)},{'fields':stable(before)})


def main():
    reconcile='--reconcile' in sys.argv
    if MANIFEST.exists() and not reconcile:
        raise RuntimeError('Existing configuration receipt: reconcile without repeating the mutation')
    q.use_branch('stripping-on')
    parent=json.loads(q.r.MANIFEST.read_text())['final_pair']
    known=json.loads((q.BASE/'final-live-readback.json').read_text())
    s=q.r.parent.attach()
    print('CONNECTED_SERVER1',flush=True)
    s.rp_vars.allowed_values=functools.lru_cache(maxsize=1)(s.rp_vars.allowed_values)
    assert s.settings.solution.run_calculation.iterate.is_active(), 'Server 1 is busy'
    current=live(s)
    print('LIVE_STATE_READ',current['native_iteration'],flush=True)
    before=json.loads((OUT/'before.json').read_text()) if reconcile else current
    unchanged(known,before)
    assert before['audit']==known['audit']
    if reconcile:
        unchanged(before,current,changed_limit=True)
        expected=dict(before['audit']['film_parameters']);expected['thickness-limit']=.3
        assert current['audit']['film_parameters']==expected
    assert not any(before['audit']['equations'].values())
    assert before['audit']['film_parameters']['thickness-limit']==1.0
    assert before['audit']['film_parameters']['timestep-max']==15e-6
    assert math.isclose(before['film']['film_elapsed_time'],.3731843386354754,rel_tol=0,abs_tol=1e-12)
    for folder in [WORK,WORK/'scratch']:
        ensure_remote_directory(s,str(folder))
    for kind in ['case','data']:
        assert remote_file_sha256(s,parent[kind],str(WORK/'scratch'/f'parent-{kind}-{time.time_ns()}.sha256'))==parent[kind+'_sha256']
    print('PARENT_HASHES_VERIFIED',flush=True)
    if not reconcile:
        OUT.mkdir(parents=True,exist_ok=False)
        q.r.dump(OUT/'before.json',before)
    m=json.loads(MANIFEST.read_text()) if reconcile else {'status':'PARENT_VERIFIED','authority':'human_20261007_film_limit_0_3_unrealistic_if_reached',
       'server_id':'1','fluent_version':str(s.get_fluent_version()),'parent_pair':parent,
       'parent_native_iteration':40483,'parent_film_time_s':before['film']['film_elapsed_time'],
       'numerical_delta':{'thickness-limit':{'before_m':1.0,'after_m':.3}},
       'work_root':str(WORK),'output_root':str(OUT),'initialization':'FORBIDDEN',
       'new_solver_updates':0,'unrealistic_film_thickness_limit_m':.3,
       'classification_rule':'Any recorded native maximum film thickness >= 0.3 m makes the run UNREALISTIC; a later decrease does not clear it.',
       'guard_review':'Every sample in each large batch, before submitting a further batch',
       'guard_implementation':'PyAnsys/scripts/setup/run_phase72a_stage4_realism.py',
       'physical_validation':False,'blocks':[]}
    if reconcile:
        assert m['status']=='CONFIGURATION_RECOVERY_REQUIRED'
        m.setdefault('configuration_recovery_events',[]).append({'error':m.pop('error'),
            'resolution':'Readback comparison now permits the one declared thickness-limit change; no solve and no repeated mutation.'})
    q.r.dump(MANIFEST,m)
    q.r.WORK=WORK
    if not reconcile:q.r.setparams(s,{'thickness-limit':.3})
    changed=live(s)
    unchanged(before,changed,changed_limit=True)
    expected=dict(before['audit']['film_parameters']);expected['thickness-limit']=.3
    assert changed['audit']['film_parameters']==expected
    pair=q.r.save(s,'limit03-N40483')
    print('NEW_LOCAL_PAIR_SAVED',flush=True)
    m['latest_pair']=pair;q.r.dump(MANIFEST,m)
    q.r.reopen(s,pair)
    reopened=live(s)
    unchanged(before,reopened,changed_limit=True)
    assert reopened['audit']['film_parameters']==expected
    assert not any(reopened['audit']['equations'].values())
    thickness=assess_thickness({40483:reopened['fields']['p72a-e2.7-ewf-thickness-max'][0]},.3)
    q.r.dump(OUT/'reopened.json',reopened)
    m.update(status='CONFIGURED_REOPEN_VERIFIED',latest_pair=pair,final_pair=pair,
             verified_native_end=40483,verified_film_time_s=reopened['film']['film_elapsed_time'],
             ready_step_s=15e-6,bulk_equations_frozen=True,flow_momentum_coupling=False,
             film_mass_kg=reopened['fields'][q.r.MASS][0],thickness_assessment=thickness,
             frozen_fields=reopened['state']['readback']['fields'],
             report_paths=json.loads((q.BASE/'stripping-on/run-manifest.json').read_text())['report_paths'],
             paired_reopen='PASS',only_declared_parameter_changed=True,solver_left_open=True)
    q.r.dump(MANIFEST,m)
    print(json.dumps({k:m[k] for k in ['status','latest_pair','verified_native_end','verified_film_time_s',
                                      'new_solver_updates','ready_step_s','film_mass_kg','thickness_assessment']},indent=2),flush=True)


if __name__=='__main__':
    try:
        main()
    except Exception:
        if MANIFEST.exists():
            m=json.loads(MANIFEST.read_text());m.update(status='CONFIGURATION_RECOVERY_REQUIRED',error=traceback.format_exc())
            q.r.dump(MANIFEST,m)
        raise
