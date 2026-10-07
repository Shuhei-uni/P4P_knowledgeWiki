"""Human-selected feedback-OFF child; reuse selected Stage 4 runner."""
from pathlib import Path,PureWindowsPath
import sys,json,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase72a_stage4_realism as run
from pyansys_fluent.stage4_native import ensure_remote_directory
from pyansys_fluent.remote_text import read_text
OLD=run.OUT
run.OUT=OLD/'feedback-off';run.MANIFEST=run.OUT/'run-manifest.json'
run.WORK=PureWindowsPath(r'C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\realism-20261007\feedback-off')
run.FLOW_MOMENTUM_COUPLING=False

def prepare():
 if run.MANIFEST.exists():raise RuntimeError('Existing retry must be reconciled; use --resume')
 run.OUT.mkdir(exist_ok=False)
 s=run.parent.attach();assert s.settings.solution.run_calculation.iterate.is_active()
 old=json.loads((OLD/'run-manifest.json').read_text())
 for p in [run.WORK,run.WORK/'scratch',run.WORK/'monitors']:ensure_remote_directory(s,str(p))
 n=run.parent.native_iteration(s)
 previous=run.save(s,f'preserved-feedback-on-N{n}')
 s.tui.file.stop_transcript()
 source=old['prepared_pair']
 s.settings.file.read_case(file_name=source['case']);s.settings.file.read_data(file_name=source['data'])
 assert run.parent.native_iteration(s)==29815
 before=run.state(s);clock=run.film(s)
 run.dump(run.OUT/'loaded-parent.json',{'state':before,'film':clock,'pair':source})
 s.settings.setup.boundary_conditions.wall['wall'].phase['mixture'].wall_film.enable_flow_momentum_coupling=False
 expected=json.loads(json.dumps(before['setup']));expected['boundary_conditions']['wall']['wall']['phase']['mixture']['wall_film']['enable_flow_momentum_coupling']=False
 after=run.state(s);assert after['setup']==expected and after['methods']==before['methods']
 run.require_match({'fields':after['readback']['fields']},{'fields':before['readback']['fields']})
 assert run.film(s)['film_elapsed_time']==clock['film_elapsed_time'];run.audit(s)
 paths={}
 for name in s.settings.solution.monitor.report_files.get_object_names():
  obj=s.settings.solution.monitor.report_files[name];key=obj.report_defs()[0];path=str(run.WORK/'monitors'/(key+'.out'));obj.file_name=path;paths[key]=path
 s.settings.file.auto_save.data_frequency=0
 pair=run.save(s,'feedback-off-prepared-N29815');audit=run.reopen(s,pair)
 run.dump(run.OUT/'prepared-reopen.json',{'state':run.state(s),'film':run.film(s),'audit':audit})
 run.dump(run.OUT/'report-definitions.json',s.settings.solution.report_definitions.get_state())
 m={'status':'PREPARED_VERIFIED','authority':'human_20261007_flow_momentum_coupling_OFF_retry','server_id':'1',
 'parent_pair':source,'parent_native_iteration':29815,'bulk_target_iteration':31815,'bulk_step_s':1e-6,
 'film_only_added_target_s':.05,'film_target_step_s':15e-6,'work_root':str(run.WORK),'output_root':str(run.OUT),
 'blocks':[],'original_equations':audit['equations'],'prepared_pair':pair,'latest_pair':pair,
 'prepared_reopen':audit,'verified_native_end':29815,'parent_film_time_s':clock['film_elapsed_time'],
 'preserved_feedback_on_endpoint':previous,'controlled_delta':'wall Flow Momentum Coupling OFF','report_paths':paths,'initialization':'FORBIDDEN'}
 assert all(m['original_equations'].values());run.dump(run.MANIFEST,m)
 print('FEEDBACK_OFF_PREPARED_VERIFIED',flush=True)
 # Reuse the generic sequence under the new manifest and audit expectation.
 sys.argv=[sys.argv[0],'--resume']
 run.main()

if __name__=='__main__':
 try:
  if '--resume' in sys.argv:run.main()
  else:prepare()
 except Exception:
  if run.MANIFEST.exists():
   m=json.loads(run.MANIFEST.read_text());m.update(status='UNREALISTIC' if m.get('run_classification')=='UNREALISTIC' else 'RECOVERY_REQUIRED',error=traceback.format_exc());run.dump(run.MANIFEST,m)
  raise
