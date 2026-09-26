"""Repair E4's local completion-path audit without dispatching any Fluent call."""
import json
import sys
import hashlib
from datetime import datetime,timezone
from pathlib import Path

BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'src'))
from pyansys_fluent.run_handoff import load_spec,verify_required_files,_run_verifier


def main():
    directory=BASE/'output/phase07b-convergence-investigation/e4'
    spec=load_spec(directory/'job.yaml',repo_root=BASE.parent)
    old=json.loads(spec.manifest_path.read_text())
    assert old['status'] in ['COMPLETE','BLOCKED'], 'Existing worker has not terminated; do not interfere'
    assert old['runner']['return_code']==0, 'Runner failed; reconcile actual scientific disposition separately'
    checks=verify_required_files(spec.required_files)
    verifier=_run_verifier(spec)
    assert all(x['passed'] for x in checks), 'Required scientific artifacts are missing'
    assert verifier and verifier['passed'], 'Local terminal proof failed'
    receipt={'status':'COMPLETE_LOCAL_COMPLETION_PATHS_RECONCILED','utc':datetime.now(timezone.utc).isoformat(),
             'job_id':spec.job_id,'original_worker_manifest':str(spec.manifest_path),
             'original_worker_manifest_sha256':hashlib.sha256(spec.manifest_path.read_bytes()).hexdigest(),
             'original_status':old['status'],'required_files':checks,'verifier':verifier,
             'fluent_calls':0,'iterations_issued':0,'controller_launches':0,
             'scientific_status':'Terminal runner evidence verified; full G4 interpretation/native QA is separate.'}
    target=directory/'completion-reconciliation.json'
    assert not target.exists(), 'Preserve existing reconciliation evidence'
    target.write_text(json.dumps(receipt,indent=2)+'\n')
    print(target)


if __name__=='__main__':main()
