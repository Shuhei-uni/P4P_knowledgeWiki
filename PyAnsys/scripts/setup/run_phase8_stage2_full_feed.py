"""Fresh full-feed F2 SIMPLE trial; 3000 total updates; Server 2 only."""
from pathlib import Path
import json,sys,time,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase8_stage2_f2_simple as base
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
BASE_OUT=base.OUT;BASE_WORK=base.WORK
OUT=BASE_OUT/'full-feed3000';WORK=BASE_WORK/'full-feed3000'
base.OUT=OUT;base.WORK=WORK

def prepare(s):
 assert not (OUT/'build.json').exists()
 old=json.loads(base.read_text(s,str(BASE_WORK/'controller-repo/PyAnsys/output/phase8-stage2/20261007/job-retry01-manifest.json')))
 assert old['status']=='BLOCKED'
 base.ensure_remote_directory(s,str(WORK/'scratch'))
 parent=json.loads((BASE_OUT/'failure-inspection.json').read_text())['checkpoint']
 for kind in ['case','data']:assert base.hash_remote(s,parent[kind],'full-feed-parent-'+kind)==parent[kind+'_sha256']
 base.ensure_remote_directory(s,str(WORK/'scratch'));base.ensure_remote_directory(s,str(WORK/'monitors'));base.remote_chdir(s,str(WORK))
 # Settings and mesh only: a new full-feed Hybrid field replaces all old data.
 s.settings.file.read_case(file_name=parent['case']);start=base.feed(s,1.0)
 old_build=json.loads((BASE_OUT/'build.json').read_text());definitions=old_build['report_definitions'];paths={}
 for name in definitions:
  path=str(WORK/'monitors'/(name+'.out')).replace('\\','/');assert not base.remote_file_exists(s,path)
  s.settings.solution.monitor.report_files[name+'-rfile'].file_name=path;paths[name]=path
 base.configure_residual_history(s,4000)
 assert not any(x['check_convergence'] for x in s.settings.solution.monitor.residual.equations.get_state().values())
 s.settings.solution.initialization.hybrid_initialize();base.ensure_iteration_expression(s)
 before=base.parity_audit(s,exact_flows=True);pair=base.save(s,'prepared-full-feed-N0');base.load(s,pair)
 assert base.native(s)==0;pair['native_iteration']=0
 after=base.parity_audit(s,exact_flows=True);assert before==after
 base.check_stage2_reports(s,definitions,paths)
 build={'status':'PREPARED_REOPEN_VERIFIED','server_id':'2','target_iteration':3000,'initialization':'Fresh Hybrid at full feed; no inherited parent data','parent_settings_pair':parent,'prepared_pair':pair,'start_feed':start,'report_definitions':definitions,'report_paths':paths,'parity_audit':after,'settings':base.setup(s),'mesh_cells':997604,'schedule':[[1000,1.0]]*3,'previous_ramp_attempt_iterations':1422,'new_trial_budget':3000}
 base.dump(OUT/'build.json',build);print('PREPARED_FULL_FEED_REOPEN_N0',flush=True)

def finalize(s):
 assert not (OUT/'build.json').exists()
 assert base.native(s)==0
 parent=json.loads((BASE_OUT/'failure-inspection.json').read_text())['checkpoint']
 pair={'case':str(WORK/'prepared-full-feed-N0.cas.h5'),'data':str(WORK/'prepared-full-feed-N0.dat.h5'),'native_iteration':0}
 for kind in ['case','data']:pair[kind+'_sha256']=base.hash_remote(s,pair[kind],'finalize-full-feed-'+kind)
 base.load(s,pair);assert base.native(s)==0
 old_build=json.loads((BASE_OUT/'build.json').read_text());definitions=old_build['report_definitions'];paths={name:str(WORK/'monitors'/(name+'.out')).replace('\\','/') for name in definitions}
 base.check_stage2_reports(s,definitions,paths);audit=base.parity_audit(s,exact_flows=True)
 build={'status':'PREPARED_REOPEN_VERIFIED','server_id':'2','target_iteration':3000,'initialization':'Fresh Hybrid at full feed; no inherited parent data','parent_settings_pair':parent,'prepared_pair':pair,'start_feed':{'multiplier':1.,'liquid_kg_s':base.TARGET_LIQUID,'vapor_kg_s':base.TARGET_VAPOR},'report_definitions':definitions,'report_paths':paths,'parity_audit':audit,'settings':base.setup(s),'mesh_cells':997604,'schedule':[[1000,1.0]]*3,'previous_ramp_attempt_iterations':1422,'new_trial_budget':3000}
 base.dump(OUT/'build.json',build);print('PREPARED_FULL_FEED_REOPEN_N0',flush=True)

def run(s):
 assert not (OUT/'run-manifest.json').exists()
 b=json.loads((OUT/'build.json').read_text());base.load(s,b['prepared_pair']);assert base.native(s)==0
 m={'status':'RUNNING','server_id':'2','started_utc':base.now(),'requested_total_iterations':3000,'verified_native_iteration':0,'initialization':b['initialization'],'segments':[],'checkpoints':[],'report_paths':b['report_paths'],'transcript_files':[str(OUT/'raw/native-transcript.txt')]};base.dump(OUT/'run-manifest.json',m)
 try:
  with SessionTranscriptCapture(s,stream_path=OUT/'raw/native-transcript.txt',echo=False) as capture:
   for target in [1000,2000,3000]:
    begin=base.native(s);flows=base.feed(s,1.0);marker=capture.mark();t=time.monotonic()
    m.update(active_segment={'start':begin,'target':target,'feed':flows},updated_utc=base.now());base.dump(OUT/'run-manifest.json',m);print('SOLVE',begin,'to',target,'FULL_FEED',flush=True)
    s.tui.solve.iterate(target-begin);capture.wait_until_quiet(quiet_seconds=.25,timeout_seconds=5)
    end=base.native(s);failed=bool(base.FAILURE_MARKER.search(capture.text_since(marker)))
    m['segments'].append({'start':begin,'end':end,'feed':flows,'wall_seconds':time.monotonic()-t,'solver_failure_markers':failed});m['observed_native_iteration']=end
    if failed or end!=target:raise RuntimeError(f'Solver stopped at N{end}; expected N{target}; failure_marker={failed}')
    pair=base.save(s,f'checkpoint-N{target}');m['checkpoints'].append(pair);m.update(verified_native_iteration=end,updated_utc=base.now());base.dump(OUT/'run-manifest.json',m)
   final=m['checkpoints'][-1];base.load(s,final);assert base.native(s)==3000
   audit=base.parity_audit(s,exact_flows=True);base.check_stage2_reports(s,b['report_definitions'],b['report_paths'])
   histories={name:base.read_text(s,path) for name,path in b['report_paths'].items()};base.dump(OUT/'report-histories.json',histories);coverage={}
   for name,text in histories.items():
    ids={int(line.split()[0]) for line in text.splitlines() if line.strip() and line.split()[0].isdigit()};missing=sorted(set(range(10,3001,10))-ids);coverage[name]={'samples':len(ids),'missing':missing};assert not missing,(name,missing)
   base.dump(OUT/'final-reopen.json',{'native_iteration':3000,'pair':final,'parity_audit':audit,'report_coverage':coverage})
   m.update(status='COMPLETE_VERIFIED_ANALYSIS_REQUIRED',completed_utc=base.now(),final_pair=final);base.dump(OUT/'run-manifest.json',m);print('COMPLETE_VERIFIED_N3000',flush=True)
 except Exception:
  m.update(status='EXECUTION_STOPPED_DIAGNOSIS_REQUIRED',error=traceback.format_exc(),stopped_utc=base.now())
  try:
   m['observed_native_iteration']=base.native(s)
   m['failed_pair_diagnostic_only']=base.save(s,f'failed-state-N{base.native(s)}-diagnostic-only')
   b=json.loads((OUT/'build.json').read_text());base.dump(OUT/'report-histories.json',{name:base.read_text(s,path) for name,path in b['report_paths'].items()})
  except Exception:m['preservation_error']=traceback.format_exc()
  base.dump(OUT/'run-manifest.json',m);raise

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);s=base.attach()
 {'prepare':prepare,'finalize':finalize,'run':run}[sys.argv[1]](s)
