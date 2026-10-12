"""Server 6 only: Plan v1 on the selected 154063-cell N5080 parent."""
from pathlib import Path,PureWindowsPath
import argparse,json,math,os,re,time,traceback
from phase9_server6_slit_common import run,attach,OUT
from pyansys_fluent import ewf_local_drain as drain
from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.ewf_staged import refresh_plan,FILM,INNER,history
from pyansys_fluent.stage4_native import exclusive_writer_lock
from pyansys_fluent.execution_contract import verify_drain_probe
from run_phase72a_stage4_ewf_drain import define_reports,compute

STAGES=[('bulk-adjustment',1500,1e-7,True),('frozen-transition',1000,1e-7,False),
 ('step-2p5us',1000,2.5e-6,False),('step-5us',1000,5e-6,False),
 ('growth-5000',5000,5e-6,False),('growth-10000-a',10000,5e-6,False),
 ('growth-10000-b',10000,5e-6,False),('growth-10000-c',10000,5e-6,False),
 ('growth-to-195ms',1750,5e-6,False),('bulk-reactivation-to-200ms',1000,5e-6,True)]

def lane_read_text(s,path):
 # Detached Server6 controller runs beside these files; avoid large Scheme RPCs.
 local=Path(path)
 if os.name=='nt' and local.is_file() and local.resolve().is_relative_to(Path(str(run.WORK)).resolve()):
  return local.read_text(encoding='utf-8',errors='replace')
 return run.read_text(s,path)

def lane_file_sha256(s,path,scratch):
 """Server6-local PowerShell hash with durable output; no solve/settings calls."""
 if not run.remote_file_exists(s,path):raise FileNotFoundError(path)
 if run.remote_file_exists(s,scratch):raise FileExistsError(scratch)
 quote=lambda value:"'"+str(value).replace("'","''")+"'"
 code=("$ErrorActionPreference='Stop'; $h=(Get-FileHash -LiteralPath "+quote(path)+
       " -Algorithm SHA256).Hash.ToLowerInvariant(); if ($h -notmatch '^[0-9a-f]{64}$') {throw 'Invalid SHA256'}; [IO.File]::WriteAllText("+
       quote(scratch)+",$h,[Text.Encoding]::ASCII)")
 result=run.base.powershell(s,code)
 if result not in (0,None):raise RuntimeError('Server6 file hash command failed')
 for attempt in range(15):
  text=lane_read_text(s,scratch).strip()
  if re.fullmatch(r'[0-9a-f]{64}',text):return text
  time.sleep(1)
 raise RuntimeError('Server6 hash output unconfirmed; preserve files, no solve replay')

def lane_save(s,folder,label):
 run.require_idle(s);run.ensure_remote_directory(s,str(folder/'scratch'))
 case=str(folder/(label+'.cas.h5'));data=str(folder/(label+'.dat.h5'))
 if run.remote_file_exists(s,case) or run.remote_file_exists(s,data):raise FileExistsError(label)
 s.settings.file.write_case(file_name=case);s.settings.file.write_data(file_name=data)
 pair={'case':case,'data':data,'native_iteration':run.native_iteration(s)}
 for key in ['case','data']:
  pair[key+'_sha256']=lane_file_sha256(s,pair[key],str(folder/'scratch'/(label+'-'+key+'.ps-sha256.txt')))
 return pair

def current_report_paths(s,names):
 """Fluent changes report filenames on data reload; use live active definitions."""
 paths={}
 for obj in s.settings.solution.monitor.report_files.get_state().values():
  defs=obj['report_defs']
  if len(defs)!=1 or defs[0] not in names:continue
  if not obj['active'] or obj['frequency_of']!='iteration' or obj['frequency']!=1:
   raise RuntimeError('Required native history is inactive or not per iteration')
  name=defs[0]
  if name in paths:raise RuntimeError('Ambiguous native report source')
  path=PureWindowsPath(obj['file_name'])
  paths[name]=str(path if path.is_absolute() else run.WORK/path)
 if set(paths)!=set(names):raise RuntimeError('Missing native report definitions')
 return paths

def render_journal(folder,label,count):
 path=lambda n:str(folder/n).replace('\\','/')
 return '\n'.join(['/file/start-transcript "'+path(label+'.trn')+'"',
 '/solve/iterate '+str(count),'/file/write-case-data "'+path(label+'.cas.h5')+'"',
 '/file/stop-transcript',''])

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');args=parser.parse_args()
 with exclusive_writer_lock(OUT/'controller.lock'):
  manifest=OUT/'run-manifest.json'
  if args.resume:
   m=json.loads(manifest.read_text())
   recovery=json.loads((OUT/m.get('resume_plan_file','lower-step-recovery-plan.json')).read_text())
   if m['status']!='RECOVERY_READY' or recovery['status']!='RECONCILED_AND_REOPENED':raise RuntimeError('Resume not reconciled')
   if m['latest_pair']!=recovery['parent_pair'] or m['schedule']!=recovery['schedule']:raise RuntimeError('Recovery identity differs')
   s=attach();run.require_idle(s)
   if s.settings.solution.run_calculation.iterating():raise RuntimeError('Resume session busy')
   if run.native_iteration(s)!=m['verified_native_end']:raise RuntimeError('Resume native differs')
   if not math.isclose(run.film(s)['film_elapsed_time'],m['accepted_film_s'],abs_tol=1e-12):raise RuntimeError('Resume clock differs')
   run.require_bulk_audit(s);run.read_feed(s,1.0);drain.audit(s,True)
   if any(s.settings.solution.controls.equations.get_state().values()):raise RuntimeError('Recovery bulk must be frozen')
   names=define_reports(s);paths=m['report_paths']
   stamp=str(time.time_ns());folder=run.WORK/'slit154k'/'ewf-200ms'
   m.update(status='RUNNING',error=None);run.dump(manifest,m)
  else:
   if manifest.exists():raise RuntimeError('Reconcile previous Server 6 run before launch')
   prepared=json.loads((OUT/'slit154k-ewf-settings-current.json').read_text())
   if prepared['status']!='SETTINGS_APPLIED_REOPEN_VERIFIED':raise RuntimeError('Unverified child')
   functional=json.loads((OUT/'matched-drain-probe.json').read_text())
   if functional['status']!='PASS' or functional['production_restored_iteration']!=5080:raise RuntimeError('Functional drain proof not restored')
   s=attach();run.require_idle(s)
   if run.native_iteration(s)!=5080:raise RuntimeError('Wrong native origin')
   run.assert_bulk_active(s);run.require_bulk_audit(s);run.read_feed(s,1.0);drain.audit(s,True)
   before=run.base.state(s);run.require_match(before['readback'],prepared['after']['readback'])
   run.require_setup_same(before['setup'],prepared['after']['setup'])
   if before['methods']!=prepared['after']['methods']:raise RuntimeError('Bulk methods changed')
   clock=run.film(s)['film_elapsed_time']
   if not math.isclose(clock,.0035,abs_tol=1e-12):raise RuntimeError('Wrong inherited film age')
   stamp=str(time.time_ns());folder=run.WORK/'slit154k'/'ewf-200ms'
   run.ensure_remote_directory(s,str(folder/'scratch'))
   names=define_reports(s)
   paths=run.base.instrument(s,folder/'monitors')
   autosave=s.settings.file.auto_save
   autosave.case_frequency='each-time';autosave.root_name=str(folder/'auto-%i')
   autosave.retain_most_recent_files=False;autosave.data_frequency=1000
   m={'status':'RUNNING','server_id':'6','cells':154063,'active_mesh':'slit154k',
    'authority':'human_server6_full_authority_slit154k_only_20261010','start_pair':prepared['pair'],
    'start_film_s':clock,'verified_native_end':5080,'latest_pair':prepared['pair'],
    'report_paths':paths,'schedule':STAGES,'blocks':[],'target_film_s':.2,
    'native_target_final':47330,'execution_host':'SERVER6_WINDOWS','laptop_required':False,
    'never_exit_fluent':True,'drain_proof_limit_percent':1.0,'functional_drain_proof':functional,
    'review':'Exclusive host lock; exact reopened parent/readback; native fixed journal commands; local paired autosave; transcript clocks and finite fields; frozen drainage proof before faster steps; final save/reopen.'}
   run.dump(manifest,m)
  try:
   for stage,count,dt,bulk_active in m['schedule']:
    if stage in {block['stage'] for block in m['blocks']}:continue
    run.require_idle(s);start=run.native_iteration(s)
    if start!=m['verified_native_end']:raise RuntimeError('Live coordinate changed')
    clock=m.get('accepted_film_s',m['start_film_s'])
    equations=s.settings.solution.controls.equations.get_state()
    # Separate the equation switch from the timestep switch, with readback.
    s.settings.solution.controls.equations.set_state({key:bulk_active for key in equations})
    if any(bool(v)!=bulk_active for v in s.settings.solution.controls.equations.get_state().values()):raise RuntimeError('Equation readback differs')
    params=dict(s.rp_vars('wall-film/model-parameters'));delta=refresh_plan(dt)
    s.rp_vars('wall-film/model-parameters',[(key,delta.get(key,value)) for key,value in params.items()])
    if not all(dict(s.rp_vars('wall-film/model-parameters'))[k]==v for k,v in delta.items()):raise RuntimeError('Step/cadence readback differs')
    expected_params=dict(s.rp_vars('wall-film/model-parameters'))
    s.tui.define.models.eulerian_wallfilm.solution_options()
    if dict(s.rp_vars('wall-film/model-parameters'))!=expected_params:raise RuntimeError('Native EWF control callback changed parameters')
    s.settings.setup.named_expressions['P72dRefreshSpan'].definition=f'{dt:.17g}[s]'
    activation=lane_save(s,folder,f'activated-{stage}-{stamp}')
    run.load(s,activation)
    if run.native_iteration(s)!=start or not math.isclose(run.film(s)['film_elapsed_time'],clock,abs_tol=1e-12):raise RuntimeError('Control activation changed coordinates')
    if any(bool(v)!=bulk_active for v in s.settings.solution.controls.equations.get_state().values()):raise RuntimeError('Activated equations differ')
    if not all(dict(s.rp_vars('wall-film/model-parameters'))[k]==v for k,v in delta.items()):raise RuntimeError('Activated film controls differ')
    drain.audit(s,True)
    paths=current_report_paths(s,names);m['report_paths']=paths
    initial=compute(s,names);bulk_before=run.base.state(s)['readback']['fields']
    label=f'{stage}-N{start+count}-{stamp}';remote=str(folder/(label+'.jou'))
    journal=render_journal(folder,label,count);(OUT/(label+'.jou')).write_text(journal)
    run.write_ascii_text_new(s,remote,journal)
    m.update(active_stage=stage,active_target=start+count,active_step_s=dt,bulk_active=bulk_active,active_journal=remote,active_transcript=str(folder/(label+'.trn')))
    run.dump(manifest,m);print('BATCH slit154k',stage,start,start+count,flush=True)
    s.scheme.eval('(ti-menu-load-string "'+quote_scheme_string('/file/read-journal "'+remote.replace('\\','/')+'"')+'")')
    end=run.native_iteration(s)
    transcript=lane_read_text(s,str(folder/(label+'.trn')));(OUT/(label+'.trn')).write_text(transcript)
    rows=[tuple(map(float,x.groups())) for x in FILM.finditer(transcript)]
    if end!=start+count:raise RuntimeError('Native solve ended early; do not replay')
    if len(rows)!=count or any(not all(math.isfinite(v) for v in row) for row in rows):raise RuntimeError('Missing/nonfinite film clocks')
    if any(not math.isclose(row[0],clock+(i+1)*dt,abs_tol=1e-10,rel_tol=1e-6) or not math.isclose(row[1],dt,rel_tol=1e-7) for i,row in enumerate(rows)):raise RuntimeError('Film clock differs from schedule')
    if re.search(r'floating point exception|fatal error|received signal|Divergence detected',transcript,re.I):raise RuntimeError('Native failure requires recovery')
    film_end=rows[-1][0]
    pair={'case':str(folder/(label+'.cas.h5')),'data':str(folder/(label+'.dat.h5')),'native_iteration':end}
    for key in ['case','data']:pair[key+'_sha256']=lane_file_sha256(s,pair[key],str(folder/'scratch'/f'{stage}-{key}-{stamp}.sha256.txt'))
    after=compute(s,names)
    if any(not math.isfinite(v[0]) for v in after.values()):raise RuntimeError('Nonfinite endpoint reports')
    block={'stage':stage,'count':count,'step_s':dt,'bulk_active':bulk_active,'film_start_s':clock,'film_end_s':film_end,'pair':pair,'initial':initial,'after':after,'peak_courant':max(row[2] for row in rows),'courant_ceiling':m.get('courant_ceiling',.1)}
    achieved=[];left=0
    for accepted in FILM.finditer(transcript):
     inner=list(INNER.finditer(transcript[left:accepted.start()]))
     if inner:achieved.append([float(inner[-1][k].strip()) for k in [2,3,4]])
     left=accepted.end()
    block['inner_steps_observed']=len(achieved)
    block['numerical_acceptance_policy']=m.get('numerical_acceptance_policy','courant_only')
    block['courant_exceeded_diagnostic']=block['peak_courant']>m.get('courant_ceiling',.8)
    block['inner_convergence_status']='DIAGNOSTIC_ONLY'
    block['inner_steps_passed']=sum(all(math.isfinite(x) and 0<=x<=1e-5 for x in row) for row in achieved)
    m['blocks'].append(block);m.update(verified_native_end=end,latest_pair=pair,accepted_film_s=film_end,active_target=None);run.dump(manifest,m)
    if not bulk_active:
     bulk_after=run.base.state(s)['readback']['fields']
     unchanged={k:math.isclose(v[0],bulk_after[k][0],rel_tol=1e-10,abs_tol=1e-12) for k,v in bulk_before.items() if not k.startswith('p72a-e2.7-ewf-')}
     if not all(unchanged.values()):raise RuntimeError('Frozen bulk report fields changed')
     paths=current_report_paths(s,names);m['report_paths']=paths;block['report_paths']=paths
     hs={name:history(lane_read_text(s,paths[name])) for name in names}
     ids=range(start+1,end+1)
     if any(not all(i in h and math.isfinite(h[i]) for i in ids) for h in hs.values()):raise RuntimeError('Missing frozen histories')
     removal=sum(hs['p72d-drain-rate'][i]*dt for i in ids)
     supply=sum((hs['p72d-total-secondary'][i]+hs['p72d-total-dpm'][i])*dt for i in ids)
     departure=sum(after[n][0]-initial[n][0] for n in ['p72d-total-mass','p72d-total-outflow','p72d-total-stripped'])
     # v252 film-phase2-mass is net of separated mass. Preserve gross alternative.
     gap=departure+removal-supply
     proof={'setup_identity':'server6-slit154k-plan-v1','frozen_bulk':True,'bulk_fields_unchanged':all(unchanged.values()),'accepted_film_time_s':count*dt,'film_start_s':clock,'film_end_s':film_end,'drained_mass_kg':removal,'direct_film_drain':True,'native_evidence_verified':True,'evidence_paths':[str(folder/(label+'.trn')),paths['p72d-drain-rate']],'bulk_equations':s.settings.solution.controls.equations.get_state(),'integrated_direct_removal_kg':removal,'ledger_error_percent':100*abs(gap)/max(abs(supply),1e-12),'ledger_limit_percent':1.0,'ledger_residual_kg':gap,'gross_ledger_residual_kg':gap+after['p72d-total-separated'][0]-initial['p72d-total-separated'][0],'ledger_basis':'v252-net-secondary-consistency','native_transcript':str(folder/(label+'.trn'))}
     proof['verification']=verify_drain_probe(proof,setup_identity='server6-slit154k-plan-v1',frozen_bulk=True)
     block['drain_proof']=proof;run.dump(OUT/(stage+'-drain-proof.json'),proof);run.dump(manifest,m)
     if proof['verification']['status']!='PASS':
      proof['production_ledger_status']='UNRESOLVED_DIAGNOSTIC'
      proof['functional_drain_verified_separately']=True
      run.dump(OUT/(stage+'-drain-proof.json'),proof);run.dump(manifest,m)
    # Human: keep running to100ms; Courant/residual/ledger excursions are diagnostics.
   if not math.isclose(m['accepted_film_s'],m['target_film_s'],abs_tol=1e-10):raise RuntimeError('Final film target differs')
   before=run.base.state(s);run.load(s,m['latest_pair']);after=run.base.state(s)
   run.require_match(after['readback'],before['readback']);run.require_setup_same(after['setup'],before['setup'])
   run.assert_bulk_active(s);run.require_bulk_audit(s);run.read_feed(s,1.0);drain.audit(s,True)
   if run.native_iteration(s)!=m['native_target_final'] or not math.isclose(run.film(s)['film_elapsed_time'],m['target_film_s'],abs_tol=1e-12):raise RuntimeError('Final reopen coordinate differs')
   run.dump(OUT/'final-reopen.json',{'pair':m['latest_pair'],'before':before,'after':after,'film':run.film(s)})
   shared=run.SHARED/'P4P-Fluent-Artifacts/Phase9/Server6/slit154k'/(f"ewf-{m['target_film_s']*1000:g}ms-N{m['native_target_final']}-"+stamp)
   run.ensure_remote_directory(s,str(shared))
   shared_pair={}
   for key in ['case','data']:
    target=str(shared/Path(m['latest_pair'][key].replace('\\','/')).name)
    code="$ErrorActionPreference='Stop'; Copy-Item -LiteralPath '"+m['latest_pair'][key]+"' -Destination '"+target+"'"
    if run.base.powershell(s,code) not in (0,None):raise RuntimeError('Selected final shared copy failed')
    digest=lane_file_sha256(s,target,str(folder/'scratch'/('shared-'+key+'-'+stamp+'.sha256.txt')))
    if digest!=m['latest_pair'][key+'_sha256']:raise RuntimeError('Selected final shared hash mismatch')
    shared_pair[key]=target;shared_pair[key+'_sha256']=digest
   m.update(status='COMPLETE_VERIFIED',active_stage=None,active_target=None,selected_shared_pair=shared_pair,cloud_upload_independently_verified=False);run.dump(manifest,m)
  except BaseException:
   m.update(status='RECOVERY_REQUIRED',error=traceback.format_exc());run.dump(manifest,m)
   try:
    if s.settings.file.stop_transcript.is_active():s.settings.file.stop_transcript()
   except Exception:pass
   raise

if __name__=='__main__':main()
