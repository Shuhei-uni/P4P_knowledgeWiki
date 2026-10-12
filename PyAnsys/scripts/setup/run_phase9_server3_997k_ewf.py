"""Run the agreed 997k settings/count schedule on Server 3 only."""
import argparse,fcntl,json,math,re,time,traceback
from pathlib import Path,PureWindowsPath
from phase9_server3_997k_common import run,attach,OUT
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.ewf_staged import refresh_plan
from pyansys_fluent.common import quote_scheme_string

COURANT_LIMIT=0.8

STAGES=[('bulk-adjustment',1500,1e-7,True),('frozen-transition',1000,1e-7,False),
 ('step-2p5us',1000,2.5e-6,False),('step-5us',1000,5e-6,False),
 ('growth-5000',5000,5e-6,False),('growth-10000-a',10000,5e-6,False),
 ('growth-10000-b',10000,5e-6,False),('growth-10000-c',10000,5e-6,False),
 ('growth-to-195ms',2320,5e-6,False),('bulk-reactivation-to-200ms',1000,5e-6,True)]

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
 expected=dict(s.rp_vars('wall-film/model-parameters'))
 s.tui.define.models.eulerian_wallfilm.solution_options()
 if dict(s.rp_vars('wall-film/model-parameters'))!=expected:raise RuntimeError('Native EWF callback changed parameters')
 pair=run.save(s,folder,label)
 run.load(s,pair)
 after=run.base.state(s)
 persistent={k:v for k,v in before['readback']['fields'].items() if 'secondary-phase-mass' not in k}
 run.require_match({'fields':{k:after['readback']['fields'][k] for k in persistent}},{'fields':persistent})
 if after['methods']!=before['methods']:raise RuntimeError('Activation changed bulk methods')
 if not math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12):raise RuntimeError('Activation changed film clock')
 if not all(dict(s.rp_vars('wall-film/model-parameters'))[k]==v for k,v in delta.items()):raise RuntimeError('Activated controls differ')
 return pair

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');args=parser.parse_args()
 lock=(OUT/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 manifest=OUT/'run-manifest.json'
 if manifest.exists() and not args.resume:raise RuntimeError('Existing run requires reconciliation')
 prepared=json.loads((OUT/'997k-ewf-settings-current.json').read_text())
 # Verified saved Server 3 path avoids a blocking getenv while native solve is active.
 profile=str(PureWindowsPath(*PureWindowsPath(prepared['pair']['case']).parts[:3]))
 s=attach(profile=profile);stamp=str(time.time_ns());folder=run.WORK/'997k';live=OUT/('live-'+stamp+'.txt')
 observing_handover=args.resume and json.loads(manifest.read_text()).get('status')=='NATIVE_COMMAND_HANDED_OVER_CLIENT_STOPPED'
 if observing_handover:
  # Capture before inspecting busy state, so completion cannot fall into a stream gap.
  s.transcript.start(file_name=str(live),write_to_stdout=False)
  rp=OUT/'desktop-controller.json';receipt=json.loads(rp.read_text());receipt.update(live_transcript=str(live),status='OBSERVING_ACCEPTED_NATIVE_COMMAND');run.dump(rp,receipt)
  if not s.settings.solution.run_calculation.iterate.is_active():
   print('WAITING_FOR_ACCEPTED_NATIVE_JOURNAL_NO_SOLVE_SUBMITTED',flush=True)
   while True:
    handed=json.loads(manifest.read_text())
    expected_base=PureWindowsPath(handed['active_journal']).stem
    finished=False
    for evidence in [live,OUT/'passive-supervision.txt']:
     if not evidence.exists():continue
     with evidence.open('rb') as stream:
      stream.seek(max(0,evidence.stat().st_size-131072));text=stream.read().decode(errors='replace')
     # A second transcript subscriber can replace the SDK stream. Use the
     # independent watcher output, matching this exact native journal identity.
     if expected_base+'.cas.h5' in text and '/file/stop-transcript' in text and 'Transcript closed.' in text:
      finished=True;break
    if finished:break
    time.sleep(15)
 run.require_idle(s)
 if args.resume:
  m=json.loads(manifest.read_text())
  if m['status']=='NATIVE_COMMAND_HANDED_OVER_CLIENT_STOPPED':
   run.dump(OUT/('original-laptop-handover-'+stamp+'.json'),m)
   start=m['verified_native_end'];target=m['active_target'];stage=m['active_stage'];dt=m['active_step_s']
   if run.native_iteration(s)!=target:raise RuntimeError('Handed-over horizon not reached; inspect without duplicating solve')
   film_end=run.film(s)['film_elapsed_time'];clock=m['accepted_film_s'];count=target-start
   if not math.isclose(film_end-clock,count*dt,abs_tol=1e-10):raise RuntimeError('Handed-over film clock differs')
   base=m['active_journal'][:-4];pair={'case':base+'.cas.h5','data':base+'.dat.h5','native_iteration':target}
   for key in ['case','data']:pair[key+'_sha256']=run.remote_file_sha256(s,pair[key],str(folder/'scratch'/f'handover-{key}-{stamp}.sha256.txt'))
   text=run.read_text(s,base+'.trn');(OUT/('completed-handover-'+stamp+'.trn')).write_text(text)
   rows=re.findall(r'Film time = ([\d.eE+-]+) with timestep = ([\d.eE+-]+), \(max_cfl: ([\d.eE+-]+)\)',text)
   if len(rows)!=count or any(not math.isclose(float(row[1]),dt,abs_tol=1e-12) for row in rows):raise RuntimeError('Handed-over accepted-step evidence incomplete')
   if re.search(r'floating point exception|fatal error|Divergence detected',text,re.I):raise RuntimeError('Native handover failure requires recovery')
   peak_courant=max(float(row[2]) for row in rows)
   run.dump(OUT/('handover-courant-'+stamp+'.json'),{'peak_courant':peak_courant,'limit':COURANT_LIMIT,'pair':pair})
   if not all(math.isfinite(float(x)) for row in rows for x in row) or peak_courant>COURANT_LIMIT:raise RuntimeError('Film Courant exceeds 0.8 operating limit; preserve endpoint and review lower-step recovery before continuation')
   before=run.base.state(s);run.load(s,pair);after=run.base.state(s)
   persistent={k:v for k,v in before['readback']['fields'].items() if 'secondary-phase-mass' not in k}
   run.require_match({**after['readback'],'fields':{k:after['readback']['fields'][k] for k in persistent}},{**before['readback'],'fields':persistent});run.require_setup_same(after['setup'],before['setup'])
   if after['methods']!=before['methods'] or not math.isclose(run.film(s)['film_elapsed_time'],film_end,abs_tol=1e-12):raise RuntimeError('Handed-over saved state differs')
   drain.audit(s,True);run.read_feed(s,1.0)
   m['blocks'].append({'peak_courant':peak_courant,'courant_limit':COURANT_LIMIT,'stage':stage,'count':count,'step_s':dt,'bulk_active':m['bulk_active'],'film_start_s':clock,'film_end_s':film_end,'pair':pair,'completed_while_mac_disconnected':True})
   m.update(verified_native_end=target,latest_pair=pair,accepted_film_s=film_end,active_target=None,status='LAPTOP_HANDOVER_RECONCILED')
   run.dump(manifest,m);run.dump(OUT/'laptop-resume-verification.json',{'status':'PASS','native_iteration':target,'film_s':film_end,'pair':pair,'accepted_updates':count,'saved_reopen_fields_setup_methods_preserved':True})
   stages=STAGES[len(m['blocks']):]
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
   stages=STAGES[len(m['blocks']):]
   m.setdefault('recoveries',[]).append({'reason':'RP numerical controls were not activated; require save/reopen at changes','failed_endpoint':failed,'restored_native':m['verified_native_end']})
   m.pop('error',None)
   print('ROLLBACK_VERIFIED',m['verified_native_end'],m['accepted_film_s'],flush=True)
 else:
  if run.native_iteration(s)!=8080:raise RuntimeError('Start native differs')
  run.assert_bulk_active(s);run.require_bulk_audit(s);run.read_feed(s,1.0);drain.audit(s,True)
  before=run.base.state(s);run.require_match(before['readback'],prepared['after']['readback']);run.require_setup_same(before['setup'],prepared['after']['setup'])
  m={'server_id':'3','cells':997604,'active_mesh':'997k','authority':'human_transfer_to_server3_997k_restart_settings_authorized_20261010','start_pair':prepared['pair'],
     'start_film_s':run.film(s)['film_elapsed_time'],'verified_native_end':8080,'latest_pair':prepared['pair'],'schedule':STAGES,
     'blocks':[],'target_film_s':.2,'native_target_final':50900,'never_exit_fluent':True,'requires_desktop_running':True}
  stages=STAGES
 monitor_folder=folder/'monitors'/stamp
 run.base.powershell(s,"New-Item -ItemType Directory -Force -Path '"+str(monitor_folder)+"' | Out-Null")
 paths=run.base.instrument(s,monitor_folder)
 m['inherited_direct_drain_proof']={'source':'Server6 same997k mesh/setup matched OFF/ON probe','ledger_error_percent':0.03916295923863323,'scope':'Applied direct lower-wall removal only; no production mass closure claim'}
 s.settings.file.auto_save.root_name=str(folder/('autosave-'+stamp));s.settings.file.auto_save.data_frequency=1000
 if not observing_handover:s.transcript.start(file_name=str(live),write_to_stdout=False)
 m.update(status='RUNNING',live_transcript=str(live),report_paths=paths,active_target=None)
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
   changed=bulk_changed or any(params[k]!=v for k,v in delta.items())
   s.settings.setup.named_expressions['P72dRefreshSpan'].definition=f'{dt:.17g}[s]'
   if changed:
    print('ACTIVATE_CONTROLS_SAVE_REOPEN',stage,dt,flush=True)
    activation=activate_controls(s,delta,folder,f'activate-{stage}-{stamp}')
    m['last_activation_pair']=activation;run.dump(manifest,m)
   drain.audit(s,True)
   label=f'{stage}-N{start+count}-{stamp}';remote=str(folder/(label+'.jou'))
   journal=render_journal(folder,label,count);(OUT/(label+'.jou')).write_text(journal);run.write_ascii_text_new(s,remote,journal)
   m.update(active_stage=stage,active_target=start+count,active_step_s=dt,bulk_active=bulk_active,active_journal=remote)
   run.dump(manifest,m);print('BATCH 997k',stage,start,start+count,flush=True)
   cmd='/file/read-journal "'+remote.replace('\\','/')+'"'
   s.scheme.eval('(ti-menu-load-string "'+quote_scheme_string(cmd)+'")')
   end=run.native_iteration(s);film_end=run.film(s)['film_elapsed_time']
   if end!=start+count:raise RuntimeError('Native command ended early; do not replay automatically')
   if not math.isclose(film_end-clock,count*dt,abs_tol=1e-10):raise RuntimeError('Accepted film clock does not match native schedule')
   pair={'case':str(folder/(label+'.cas.h5')),'data':str(folder/(label+'.dat.h5')),'native_iteration':end}
   for key in ['case','data']:
    pair[key+'_sha256']=run.remote_file_sha256(s,pair[key],str(folder/'scratch'/f'{stage}-{key}-{stamp}.sha256.txt'))
   transcript=run.read_text(s,str(folder/(label+'.trn')));(OUT/(label+'.trn')).write_text(transcript)
   rows=re.findall(r'Film time = ([\d.eE+-]+) with timestep = ([\d.eE+-]+), \(max_cfl: ([\d.eE+-]+)\)',transcript)
   if len(rows)!=count or any(not all(math.isfinite(float(x)) for x in row) or not math.isclose(float(row[1]),dt,rel_tol=1e-7) for row in rows):raise RuntimeError('Native accepted-step evidence differs')
   if re.search(r'floating point exception|fatal error|Divergence detected',transcript,re.I):raise RuntimeError('Native failure text requires recovery')
   peak_courant=max(float(row[2]) for row in rows)
   run.dump(OUT/(label+'-courant.json'),{'peak_courant':peak_courant,'limit':COURANT_LIMIT,'pair':pair})
   if peak_courant>COURANT_LIMIT:raise RuntimeError('Film Courant exceeds 0.8 operating limit; preserve endpoint and review lower-step recovery before continuation')
   m['blocks'].append({'peak_courant':peak_courant,'courant_limit':COURANT_LIMIT,'stage':stage,'count':count,'step_s':dt,'bulk_active':bulk_active,'film_start_s':clock,'film_end_s':film_end,'pair':pair})
   m.update(verified_native_end=end,latest_pair=pair,accepted_film_s=film_end,active_target=None);run.dump(manifest,m)
  if not math.isclose(m['accepted_film_s'],.2,abs_tol=1e-10):raise RuntimeError('Final film age differs from 200 ms')
  run.assert_bulk_active(s);run.read_feed(s,1.0)
  m.update(status='COMPLETE_NATIVE_SCHEDULE_FINAL_VERIFICATION_PENDING',active_stage=None,active_target=None);run.dump(manifest,m)
 except BaseException:
  m.update(status='RECOVERY_REQUIRED',error=traceback.format_exc());run.dump(manifest,m);raise
 finally:
  receipt=json.loads(rp.read_text());receipt['status']=m['status'];run.dump(rp,receipt)

if __name__=='__main__':main()
