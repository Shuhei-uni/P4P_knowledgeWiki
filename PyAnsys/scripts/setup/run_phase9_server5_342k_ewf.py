"""Run the agreed 342k settings/count schedule on Server 5 only."""
import argparse,fcntl,json,math,re,time,traceback
from pathlib import Path
from phase9_server5_common import run,attach,OUT
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.ewf_staged import refresh_plan
from pyansys_fluent.common import quote_scheme_string
from phase9_server5_live_stream import start_live_stream

STAGES=[('bulk-adjustment',1500,1e-7,True),('frozen-transition',1000,1e-7,False),
 ('step-2p5us',1000,2.5e-6,False),('step-5us',1000,5e-6,False),
 ('growth-5000',5000,5e-6,False),('growth-10000-a',10000,5e-6,False),
 ('growth-10000-b',10000,5e-6,False),('growth-10000-c',10000,5e-6,False),
 ('growth-to-195ms',2310,5e-6,False),('bulk-reactivation-to-200ms',1000,5e-6,True)]

FILM_COURANT_LIMIT=0.8

def verify_film_updates(text,count,dt):
 rows=re.findall(r'Film time = ([\d.eE+-]+) with timestep = ([\d.eE+-]+), \(max_cfl: ([\d.eE+-]+)\)',text)
 if len(rows)!=count or any(not math.isclose(float(row[1]),dt,abs_tol=1e-12) for row in rows):
  raise RuntimeError('Accepted film-step evidence incomplete')
 maximum=max(float(row[2]) for row in rows)
 if any(not math.isfinite(float(row[2])) for row in rows) or maximum>FILM_COURANT_LIMIT:
  raise RuntimeError(f'Film Courant limit exceeded: {maximum} > {FILM_COURANT_LIMIT}; preserve attempt and reconcile lower-step recovery')
 return maximum

def recovery_stages(clock,dt):
 # First prove 1,000 updates at the lower level, then use long fixed-input blocks.
 remaining=round((.195-clock)/dt)
 if remaining<=0 or not math.isclose(clock+remaining*dt,.195,abs_tol=1e-10):
  raise RuntimeError('Recovery clock does not align with frozen endpoint')
 stages=[];index=0
 while remaining:
  count=min(1000 if index==0 else 10000,remaining)
  stages.append((f'courant-recovery-frozen-{index+1}',count,dt,False))
  remaining-=count;index+=1
 stages.append(('bulk-reactivation-to-200ms',round(.005/dt),dt,True))
 return stages

def render_journal(folder,label,count):
 path=lambda n:str(folder/n).replace('\\','/')
 return '\n'.join(['/file/start-transcript "'+path(label+'.trn')+'"',
                   '/solve/iterate '+str(count),
                   '/file/write-case-data "'+path(label+'.cas.h5')+'"',
                   '/file/stop-transcript',''])

def activate_controls(s,delta,folder,label):
 before=run.base.state(s);clock=run.film(s)['film_elapsed_time']
 params=dict(s.rp_vars('wall-film/model-parameters'))
 s.rp_vars('wall-film/model-parameters',[(k,delta.get(k,v)) for k,v in params.items()])
 pair=run.save(s,folder,label)
 run.load(s,pair)
 after=run.base.state(s)
 run.require_match({'fields':after['readback']['fields']},{'fields':before['readback']['fields']})
 if after['methods']!=before['methods']:raise RuntimeError('Activation changed bulk methods')
 if not math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12):raise RuntimeError('Activation changed film clock')
 if not all(dict(s.rp_vars('wall-film/model-parameters'))[k]==v for k,v in delta.items()):raise RuntimeError('Activated controls differ')
 return pair

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');parser.add_argument('--recover-courant',action='store_true');args=parser.parse_args()
 if args.recover_courant and not args.resume:raise RuntimeError('Courant recovery requires explicit resume mode')
 lock=(OUT/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 manifest=OUT/'run-manifest.json'
 if manifest.exists() and not args.resume:raise RuntimeError('Existing run requires reconciliation')
 prepared=json.loads((OUT/'342k-ewf-settings-current.json').read_text())
 s=attach();stamp=str(time.time_ns());folder=run.WORK/'342k';live=OUT/('live-'+stamp+'.txt')
 observing_handover=args.resume and not args.recover_courant and json.loads(manifest.read_text()).get('status')=='NATIVE_COMMAND_HANDED_OVER_CLIENT_STOPPED'
 if observing_handover:
  # Capture before inspecting busy state, so completion cannot fall into a stream gap.
  start_live_stream(live)
  rp=OUT/'desktop-controller.json';receipt=json.loads(rp.read_text());receipt.update(live_transcript=str(live),status='OBSERVING_ACCEPTED_NATIVE_COMMAND');run.dump(rp,receipt)
  if not s.settings.solution.run_calculation.iterate.is_active():
   print('WAITING_FOR_ACCEPTED_NATIVE_JOURNAL_NO_SOLVE_SUBMITTED',flush=True)
   while True:
    text=live.read_text()[-131072:] if live.exists() else ''
    if '/file/stop-transcript' in text and 'Transcript closed.' in text:break
    time.sleep(15)
 run.require_idle(s)
 if args.resume:
  m=json.loads(manifest.read_text())
  if args.recover_courant:
   if m['status'] not in {'NATIVE_COMMAND_HANDED_OVER_CLIENT_STOPPED','RECOVERY_REQUIRED'}:raise RuntimeError('Unexpected Courant recovery starting state')
   run.dump(OUT/('original-courant-attempt-'+stamp+'.json'),m)
   request=json.loads((OUT/'courant-recovery-request.json').read_text())
   healthy=request['healthy_pair'];clock=request['healthy_film_s'];dt=request['lower_step_s']
   if request['film_courant_operating_limit']!=FILM_COURANT_LIMIT:raise RuntimeError('Recovery limit differs')
   failed=run.save(s,folder,'preserved-courant-attempt-'+stamp)
   failed_clock=run.film(s)
   original=m['active_journal'][:-4]+'.trn'
   failed_text=run.read_text(s,original);(OUT/('preserved-courant-attempt-'+stamp+'.trn')).write_text(failed_text)
   # An interrupted native journal can skip its final stop-transcript command.
   # Preserve its contents first, then close it before any replacement journal.
   if s.settings.file.stop_transcript.is_active():s.settings.file.stop_transcript()
   if not s.settings.file.start_transcript.is_active():raise RuntimeError('Native transcript is not ready for a replacement journal')
   for key in ['case','data']:
    digest=run.remote_file_sha256(s,healthy[key],str(folder/'scratch'/f'healthy-{key}-{stamp}.sha256.txt'))
    if digest!=healthy[key+'_sha256']:raise RuntimeError('Healthy checkpoint hash differs')
   run.load(s,healthy)
   if run.native_iteration(s)!=healthy['native_iteration'] or not math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12):raise RuntimeError('Healthy checkpoint coordinate differs')
   run.require_bulk_audit(s);run.read_feed(s,1.0);drain.audit(s,True)
   if any(s.settings.solution.controls.equations.get_state().values()):raise RuntimeError('Recovery requires frozen parent')
   retained=m['blocks'][:request['retain_blocks']]
   if not retained or retained[-1]['pair']!=healthy:raise RuntimeError('Healthy block identity differs')
   stages=recovery_stages(clock,dt)
   m.setdefault('recoveries',[]).append({'reason':'Film Courant exceeded human 0.8 limit','failed_pair':failed,'failed_clock':failed_clock,'excluded_blocks':m['blocks'][request['retain_blocks']:],'restored_pair':healthy,'lower_step_s':dt})
   m.update(blocks=retained,verified_native_end=healthy['native_iteration'],latest_pair=healthy,accepted_film_s=clock,schedule=[(b['stage'],b['count'],b['step_s'],b['bulk_active']) for b in retained]+stages,native_target_final=healthy['native_iteration']+sum(x[1] for x in stages),status='COURANT_RECOVERY_RESTORED')
   m.pop('error',None);run.dump(manifest,m)
   run.dump(OUT/'courant-recovery-verification.json',{'status':'PARENT_RESTORED','failed_pair':failed,'failed_clock':failed_clock,'healthy_pair':healthy,'healthy_film_s':clock,'remaining_stages':stages,'film_courant_operating_limit':FILM_COURANT_LIMIT})
   print('COURANT_RECOVERY_PARENT_VERIFIED',healthy['native_iteration'],clock,dt,flush=True)
  elif m['status']=='CONTROL_REPAIR_READY_TO_CONTINUE':
   proof=json.loads((OUT/'transcript-control-repair.json').read_text())
   if proof['status']!='PASS' or proof['native_iteration']!=m['verified_native_end']:raise RuntimeError('Control repair proof differs')
   if run.native_iteration(s)!=m['verified_native_end'] or not math.isclose(run.film(s)['film_elapsed_time'],m['accepted_film_s'],abs_tol=1e-12):raise RuntimeError('Unadvanced control repair coordinate differs')
   run.require_bulk_audit(s);run.read_feed(s,1.0);drain.audit(s,True)
   stages=m['schedule'][len(m['blocks']):]
   # Reopen numerical controls even if RP setters already contain the values.
   m['force_first_activation_after_control_repair']=True
   print('CONTROL_REPAIR_COORDINATE_VERIFIED',m['verified_native_end'],m['accepted_film_s'],flush=True)
  elif m['status']=='NATIVE_COMMAND_HANDED_OVER_CLIENT_STOPPED':
   run.dump(OUT/('original-laptop-handover-'+stamp+'.json'),m)
   start=m['verified_native_end'];target=m['active_target'];stage=m['active_stage'];dt=m['active_step_s']
   if run.native_iteration(s)!=target:raise RuntimeError('Handed-over horizon not reached; inspect without duplicating solve')
   film_end=run.film(s)['film_elapsed_time'];clock=m['accepted_film_s'];count=target-start
   if not math.isclose(film_end-clock,count*dt,abs_tol=1e-10):raise RuntimeError('Handed-over film clock differs')
   base=m['active_journal'][:-4];pair={'case':base+'.cas.h5','data':base+'.dat.h5','native_iteration':target}
   for key in ['case','data']:pair[key+'_sha256']=run.remote_file_sha256(s,pair[key],str(folder/'scratch'/f'handover-{key}-{stamp}.sha256.txt'))
   text=run.read_text(s,base+'.trn');(OUT/('completed-handover-'+stamp+'.trn')).write_text(text)
   maximum_cfl=verify_film_updates(text,count,dt)
   if re.search(r'floating point exception|fatal error|Divergence detected',text,re.I):raise RuntimeError('Native handover failure requires recovery')
   before=run.base.state(s);run.load(s,pair);after=run.base.state(s)
   run.require_match(after['readback'],before['readback']);run.require_setup_same(after['setup'],before['setup'])
   if after['methods']!=before['methods'] or not math.isclose(run.film(s)['film_elapsed_time'],film_end,abs_tol=1e-12):raise RuntimeError('Handed-over saved state differs')
   drain.audit(s,True);run.read_feed(s,1.0)
   m['blocks'].append({'stage':stage,'count':count,'step_s':dt,'bulk_active':m['bulk_active'],'film_start_s':clock,'film_end_s':film_end,'pair':pair,'completed_while_mac_disconnected':True,'maximum_reported_film_courant':maximum_cfl})
   m.update(verified_native_end=target,latest_pair=pair,accepted_film_s=film_end,active_target=None,status='LAPTOP_HANDOVER_RECONCILED')
   run.dump(manifest,m);run.dump(OUT/'laptop-resume-verification.json',{'status':'PASS','native_iteration':target,'film_s':film_end,'pair':pair,'accepted_updates':count,'saved_reopen_fields_setup_methods_preserved':True})
   stages=m.get('schedule',STAGES)[len(m['blocks']):]
   print('HANDOVER_COMPLETION_VERIFIED',target,film_end,flush=True)
  else:
   m=json.loads(manifest.read_text())
   if m['status']!='RECOVERY_REQUIRED':raise RuntimeError('Resume requires recorded recovery state')
   run.dump(OUT/('original-run-before-recovery-'+stamp+'.json'),m)
   # Preserve the actual command endpoint before rolling back the wrong-step branch.
   native=run.native_iteration(s);base=m['active_journal'][:-4]
   failed=({'native_iteration':native,'film':run.film(s),'case':base+'.cas.h5','data':base+'.dat.h5'} if native!=m['verified_native_end'] else json.loads((OUT/'clock-activation-recovery.json').read_text())['failed_endpoint'])
   for key in ['case','data']:failed[key+'_sha256']=run.remote_file_sha256(s,failed[key],str(folder/'scratch'/f'failed-{key}-{stamp}.sha256.txt'))
   transcript=run.read_text(s,base+'.trn');(OUT/('failed-wrong-step-'+stamp+'.trn')).write_text(transcript)
   run.dump(OUT/'clock-activation-recovery.json',{'status':'ROLLBACK_IN_PROGRESS','failed_endpoint':failed,'resume_pair':m['latest_pair'],'original_error':m['error']})
   for key in ['case','data']:
    digest=run.remote_file_sha256(s,m['latest_pair'][key],str(folder/'scratch'/f'resume-{key}-{stamp}.sha256.txt'))
    if digest!=m['latest_pair'][key+'_sha256']:raise RuntimeError('Resume pair hash differs')
   run.load(s,m['latest_pair'])
   if not math.isclose(run.film(s)['film_elapsed_time'],m['accepted_film_s'],abs_tol=1e-12):raise RuntimeError('Restored film clock differs')
   if run.native_iteration(s)!=m['verified_native_end']:raise RuntimeError('Restored iteration differs')
   stages=m.get('schedule',STAGES)[len(m['blocks']):]
   m.setdefault('recoveries',[]).append({'reason':'RP numerical controls were not activated; require save/reopen at changes','failed_endpoint':failed,'restored_native':m['verified_native_end']})
   m.pop('error',None)
   print('ROLLBACK_VERIFIED',m['verified_native_end'],m['accepted_film_s'],flush=True)
 else:
  if run.native_iteration(s)!=8580:raise RuntimeError('Start native differs')
  run.assert_bulk_active(s);run.require_bulk_audit(s);run.read_feed(s,1.0);drain.audit(s,True)
  before=run.base.state(s);run.require_match(before['readback'],prepared['after']['readback']);run.require_setup_same(before['setup'],prepared['after']['setup'])
  m={'server_id':'5','active_mesh':'342k','authority':'human_server5_full_authority_apply_then_run','start_pair':prepared['pair'],
     'start_film_s':run.film(s)['film_elapsed_time'],'verified_native_end':8580,'latest_pair':prepared['pair'],'schedule':STAGES,
     'blocks':[],'target_film_s':.2,'native_target_final':51390,'never_exit_fluent':True,'requires_desktop_running':True}
  stages=STAGES
 monitor_folder=folder/'monitors'/stamp
 run.base.powershell(s,"New-Item -ItemType Directory -Force -Path '"+str(monitor_folder)+"' | Out-Null")
 paths=run.base.instrument(s,monitor_folder)
 s.settings.file.auto_save.root_name=str(folder/('autosave-'+stamp));s.settings.file.auto_save.data_frequency=1000
 if not observing_handover:start_live_stream(live)
 m.update(status='RUNNING',live_transcript=str(live),report_paths=paths,active_target=None,film_courant_operating_limit=FILM_COURANT_LIMIT)
 run.dump(manifest,m)
 rp=OUT/'desktop-controller.json';receipt=json.loads(rp.read_text());receipt['live_transcript']=str(live);run.dump(rp,receipt)
 try:
  for stage,count,dt,bulk_active in stages:
   run.require_idle(s);start=run.native_iteration(s);clock=run.film(s)['film_elapsed_time']
   equations=s.settings.solution.controls.equations.get_state()
   bulk_changed=any(bool(v)!=bulk_active for v in equations.values())
   if bulk_changed:
    s.settings.solution.controls.equations.set_state({key:bulk_active for key in equations})
    if any(bool(v)!=bulk_active for v in s.settings.solution.controls.equations.get_state().values()):raise RuntimeError('Equation setter readback differs')
   params=dict(s.rp_vars('wall-film/model-parameters'));delta=refresh_plan(dt)
   changed=bulk_changed or any(params[k]!=v for k,v in delta.items()) or m.pop('force_first_activation_after_control_repair',False)
   s.settings.setup.named_expressions['P72dRefreshSpan'].definition=f'{dt:.17g}[s]'
   if changed:
    print('ACTIVATE_CONTROLS_SAVE_REOPEN',stage,dt,flush=True)
    activation=activate_controls(s,delta,folder,f'activate-{stage}-{stamp}')
    m['last_activation_pair']=activation;run.dump(manifest,m)
   drain.audit(s,True)
   if not s.settings.file.start_transcript.is_active():raise RuntimeError('Existing native transcript must be reconciled before journal submission')
   label=f'{stage}-N{start+count}-{stamp}';remote=str(folder/(label+'.jou'))
   journal=render_journal(folder,label,count);(OUT/(label+'.jou')).write_text(journal);run.write_ascii_text_new(s,remote,journal)
   m.update(active_stage=stage,active_target=start+count,active_step_s=dt,bulk_active=bulk_active,active_journal=remote)
   run.dump(manifest,m);print('BATCH 342k',stage,start,start+count,flush=True)
   cmd='/file/read-journal "'+remote.replace('\\','/')+'"'
   s.scheme.eval('(ti-menu-load-string "'+quote_scheme_string(cmd)+'")')
   end=run.native_iteration(s);film_end=run.film(s)['film_elapsed_time']
   if end!=start+count:raise RuntimeError('Native command ended early; do not replay automatically')
   if not math.isclose(film_end-clock,count*dt,abs_tol=1e-10):raise RuntimeError('Accepted film clock does not match native schedule')
   pair={'case':str(folder/(label+'.cas.h5')),'data':str(folder/(label+'.dat.h5')),'native_iteration':end}
   for key in ['case','data']:
    pair[key+'_sha256']=run.remote_file_sha256(s,pair[key],str(folder/'scratch'/f'{stage}-{key}-{stamp}.sha256.txt'))
   transcript=run.read_text(s,str(folder/(label+'.trn')));(OUT/(label+'.trn')).write_text(transcript)
   if re.search(r'floating point exception|fatal error|Divergence detected',transcript,re.I):raise RuntimeError('Native failure text requires recovery')
   maximum_cfl=verify_film_updates(transcript,count,dt)
   m['blocks'].append({'stage':stage,'count':count,'step_s':dt,'bulk_active':bulk_active,'film_start_s':clock,'film_end_s':film_end,'pair':pair,'maximum_reported_film_courant':maximum_cfl})
   m.update(verified_native_end=end,latest_pair=pair,accepted_film_s=film_end,active_target=None);run.dump(manifest,m)
  if not math.isclose(m['accepted_film_s'],.2,abs_tol=1e-10):raise RuntimeError('Final film age differs from 200 ms')
  run.assert_bulk_active(s);run.read_feed(s,1.0)
  m.update(status='COMPLETE_NATIVE_SCHEDULE_FINAL_VERIFICATION_PENDING',active_stage=None,active_target=None);run.dump(manifest,m)
 except BaseException:
  m.update(status='RECOVERY_REQUIRED',error=traceback.format_exc());run.dump(manifest,m);raise
 finally:
  receipt=json.loads(rp.read_text());receipt['status']=m['status'];run.dump(rp,receipt)

if __name__=='__main__':main()
