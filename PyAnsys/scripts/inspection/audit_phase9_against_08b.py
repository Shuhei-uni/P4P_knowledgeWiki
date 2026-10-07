"""Extract native settings for the human-requested pre-run 08b comparison.

Server 3 only. No iterations, no reinitialization, no reference-file writes.
Restore the preserved Phase 9 child after reference extraction.
"""
from pathlib import Path
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts/setup'),str(ROOT/'src')]
import run_phase9_mesh_startup as run
from pyansys_fluent.stage4_native import remote_file_sha256

REFERENCE=run.SHARED/'P4P-Fluent-Artifacts/08b/TwoPhaseInletV2(Purnanto).cas.h5'


def capture(s):
    result={'version':str(s.get_fluent_version()),'setup':s.settings.setup.get_state(),
            'solution':s.settings.solution.get_state()}
    parameters=s.rp_vars()
    selected={}
    pattern=re.compile(r'multiphase|mixture|vof|surface.tension|sigma|phase.interaction|slip|drag|lift|virtual.mass|operating|gravity|pressure|pseudo|wall.film|turb|rng|k.epsilon|discret|residual|relax|body.force',re.I)
    for key,value in parameters.items():
        if pattern.search(key):selected[key]=value
    result['native_parameters']=selected
    model=s.settings.setup.models.multiphase
    result['multiphase_children']={name:{'active':getattr(model,name).is_active()} for name in model.child_names}
    return result


def main():
    s=run.previous.attach()
    if not s.settings.solution.run_calculation.iterate.is_active():raise RuntimeError('Server 3 must be idle')
    child=json.loads((run.OUT/'342k-prepared.json').read_text())
    if run.native_iteration(s)!=1580:raise RuntimeError('Unpreserved iteration before audit')
    raw=run.OUT/'raw/08b-settings-audit';raw.mkdir(parents=True,exist_ok=True)
    phase9=raw/'phase9-before.json'
    if not phase9.exists():run.dump(phase9,capture(s));print('PHASE9_SETTINGS_CAPTURED',flush=True)
    reference=raw/'08b-native.json'
    if not reference.exists():
        digest=remote_file_sha256(s,str(REFERENCE),str(run.WORK/'scratch/08b-reference.sha256.txt'))
        run.dump(raw/'reference-identity.json',{'case':str(REFERENCE),'case_sha256':digest,'data_loaded':False,'purpose':'Setup comparison only'})
        print('LOADING_08B_REFERENCE',flush=True)
        s.settings.file.read_case(file_name=str(REFERENCE))
        run.dump(reference,capture(s));print('08B_SETTINGS_CAPTURED',flush=True)
    run.load(s,child['pair'])
    run.require_match(run.base.state(s)['readback'],child['state']['readback'])
    run.dump(run.OUT/'08b-audit-extraction.json',{'status':'REFERENCE_CAPTURED_PHASE9_RESTORED','reference':str(reference),'phase9':str(phase9),'restore_pair':child['pair'],'solve_calls':0})
    print('PHASE9_RESTORED_NO_SOLVES',flush=True)


if __name__=='__main__':main()
