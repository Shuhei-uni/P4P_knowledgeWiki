"""Reconcile server-owned batch, then add the human-requested 2000 bulk updates."""
import sys,json,traceback
from pathlib import PureWindowsPath
import retry_phase72a_stage4_feedback_off as retry
run=retry.run

def main():
 m=json.loads(run.MANIFEST.read_text())
 authority=json.loads((run.OUT/'bulk-extension-authority.json').read_text())
 run.WORK=PureWindowsPath(m['work_root'])
 s=run.parent.attach()
 actual=run.parent.native_iteration(s);run.audit(s)
 if m.get('active_target') is not None:
  assert actual==m['active_target']==31815,(actual,m.get('active_target'))
  run.batch(s,m,actual-m['verified_native_end'],'bulk-film',m['active_step_s'],False,completed=True)
 assert m['verified_native_end']==31815 and actual==31815
 m['bulk_target_iteration']=authority['new_bulk_target']
 m['bulk_extension_authority']=authority
 m['status']='CHECKPOINT_VERIFIED';run.dump(run.MANIFEST,m)
 print('BULK_EXTENSION_VERIFIED',actual,'target',m['bulk_target_iteration'],flush=True)
 sys.argv=[sys.argv[0],'--resume'];run.main()

if __name__=='__main__':
 try:main()
 except Exception:
  m=json.loads(run.MANIFEST.read_text());m.update(status='RECOVERY_REQUIRED',error=traceback.format_exc());run.dump(run.MANIFEST,m)
  raise
