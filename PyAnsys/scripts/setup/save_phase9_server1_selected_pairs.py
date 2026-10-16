"""Preserve exact freeze-onset and 195ms pairs; restore the live 200ms state.

Attach only. Never iterate, initialise, interrupt, or exit Fluent. The 0.9ms
freeze-onset pair is explicitly reconstructed by changing only equation flags
on the original N10580 pair. The original 195ms pair is copied byte for byte.
"""
import argparse,hashlib,json,math,shutil,time,traceback
from pathlib import Path,PureWindowsPath
from phase9_server1_680k_common import run,attach,OUT
from pyansys_fluent.stage4_native import exclusive_writer_lock

def digest(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def verify_pair(pair):
 for key in ('case','data'):
  if digest(pair[key])!=pair[key+'_sha256']:raise RuntimeError('Source pair hash differs: '+key)

def check_coordinate(s,native,clock,bulk_active):
 run.require_idle(s)
 if run.native_iteration(s)!=native or not math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12):raise RuntimeError('Native/film coordinate differs')
 equations=s.settings.solution.controls.equations.get_state()
 if not equations or any(bool(v)!=bulk_active for v in equations.values()):raise RuntimeError('Bulk equation state differs')

def copy_pair(pair,folder,stem):
 verify_pair(pair);folder=Path(str(folder));folder.mkdir(parents=True,exist_ok=True)
 result={'native_iteration':pair['native_iteration']}
 for key,suffix in (('case','.cas.h5'),('data','.dat.h5')):
  target=folder/(stem+suffix)
  with Path(pair[key]).open('rb') as source,target.open('xb') as dest:shutil.copyfileobj(source,dest)
  actual=digest(target)
  if actual!=pair[key+'_sha256']:raise RuntimeError('Selected copy hash differs')
  result[key]=str(target);result[key+'_sha256']=actual
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args()
 receipt=OUT/('selected-checkpoints-'+args.tag+'.json')
 state={'status':'STARTING','tag':args.tag,'server_id':'1','cells':679970,'new_iterations':0,'fluent_exited':False}
 def save():run.dump(receipt,state)
 if receipt.exists():raise RuntimeError('Existing export receipt; no replay')
 save()
 with exclusive_writer_lock(OUT/'controller.lock'):
  m=json.loads((OUT/'run-manifest.json').read_text())
  if m['status']!='COMPLETE_VERIFIED' or m['server_id']!='1' or m['cells']!=679970:raise RuntimeError('Wrong completed lane')
  onset=next(b for b in m['blocks'] if b['stage']=='bulk-adjustment')
  frozen=next(b for b in m['blocks'] if math.isclose(b['film_end_s'],.195,abs_tol=1e-12))
  if onset['pair']['native_iteration']!=10580 or not math.isclose(onset['film_end_s'],.0009,abs_tol=1e-12) or frozen['bulk_active']:raise RuntimeError('Selected boundary identity differs')
  for pair in (onset['pair'],frozen['pair'],m['latest_pair']):verify_pair(pair)
  shared=PureWindowsPath(m['selected_shared_pair']['case']).parent
  s=attach();check_coordinate(s,104080,.2,True);before=run.base.state(s)
  folder=run.WORK/'680k/ewf-200ms'/('selected-checkpoints-'+args.tag)
  restore_pair=run.save(s,folder,'pre-export-200ms-state')
  state.update(status='LIVE_ENDPOINT_PRESERVED',restore_pair=restore_pair,shared_folder=str(shared));save()
  try:
   run.load(s,onset['pair']);check_coordinate(s,10580,.0009,True)
   original=run.base.state(s)
   equations=s.settings.solution.controls.equations.get_state()
   s.settings.solution.controls.equations.set_state({key:False for key in equations})
   check_coordinate(s,10580,.0009,False);off=run.base.state(s)
   run.require_match({'fields':off['readback']['fields']},{'fields':original['readback']['fields']})
   if off['methods']!=original['methods'] or off['film_model']!=original['film_model']:raise RuntimeError('Freeze changed methods or film controls')
   pair=run.save(s,folder,'bulk-freeze-0p9ms-N10580')
   run.load(s,pair);check_coordinate(s,10580,.0009,False)
   run.require_match(run.base.state(s)['readback'],off['readback'])
   shared_onset=copy_pair(pair,shared,'bulk-freeze-0p9ms-N10580-'+args.tag)
   state['freeze_onset']={'film_age_s':.0009,'native_iteration':10580,'bulk_active':False,'origin':'reconstructed from exact N10580 /0.9ms pair; only bulk equation flags switched off; no iterations','parent_pair':onset['pair'],'local_pair':pair,'shared_pair':shared_onset,'field_reports_unchanged':True,'reopen_verified':True};state['status']='FREEZE_ONSET_SAVED_VERIFIED';save()
   run.load(s,frozen['pair']);check_coordinate(s,103080,.195,False)
   shared_frozen=copy_pair(frozen['pair'],shared,'frozen-195ms-N103080-'+args.tag)
   state['frozen_195ms']={'film_age_s':.195,'native_iteration':103080,'bulk_active':False,'origin':'original frozen endpoint before bulk reactivation; byte-identical selected copy','local_pair':frozen['pair'],'shared_pair':shared_frozen,'reopen_verified':True};state['status']='BOTH_PAIRS_SAVED_VERIFIED';save()
  except BaseException:
   state.update(status='EXPORT_ERROR',error=traceback.format_exc());save();raise
  finally:
   try:
    run.load(s,restore_pair);check_coordinate(s,104080,.2,True)
    after=run.base.state(s);run.require_match(after['readback'],before['readback']);run.require_setup_same(after['setup'],before['setup'])
    if after['methods']!=before['methods'] or after['film_model']!=before['film_model']:raise RuntimeError('Restored controls differ')
    state.update(live_200ms_restored=True,restored_native=104080,restored_film_age_s=run.film(s)['film_elapsed_time']);save()
   except BaseException:
    state.update(status='RESTORE_ERROR',restore_error=traceback.format_exc());save();raise
  state.update(status='COMPLETE_VERIFIED',cloud_upload_independently_verified=False);save()
  index=Path(str(shared))/('selected-checkpoints-'+args.tag+'.json')
  with index.open('x') as f:json.dump(state,f,indent=2);f.write('\n')
  print('SELECTED_CHECKPOINTS_COMPLETE_VERIFIED',str(receipt),flush=True)

if __name__=='__main__':main()
