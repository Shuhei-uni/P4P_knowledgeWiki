"""Initialize, save/reload and run three source-free iterations on clean Phase7b.

Do not load any historical case or compile/load a UDF. Diagnostic only.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,ntpath,signal,sys,traceback,re
BASE=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(BASE/'src'))
from dotenv import load_dotenv
load_dotenv(BASE/'.env')
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.remote_text import read_text
ZONE='simple-spiral-separator--brine-outlet-'
ROOT='C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal'

def counts(s):
 exprs=s.settings.setup.named_expressions
 if 'P7bGlobalIteration' not in exprs.get_object_names():
  exprs.create(name='P7bGlobalIteration')
  exprs['P7bGlobalIteration'].definition='Iteration'
 return {'sol_iterations_rpvar':s.rp_vars('sol/iterations'),
         'global_iteration':exprs['P7bGlobalIteration'].get_value()}
def source_flags(s):
 return {ph:s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources.enable() for ph in ['mixture','phase-1','phase-2']}
def main():
 p=BASE/'output/phase07b_preparation'; stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 r={'stamp':stamp,'status':'CONNECTING','scientific_screen':False,'requested_iterations':3,'transcript':ROOT+'/logs/p7b-clean-smoke-'+stamp+'.trn','initial_case':ROOT+'/case-data/p7b-clean-initial-'+stamp+'.cas.h5','final_case':ROOT+'/case-data/p7b-clean-smoke-'+stamp+'.cas.h5','report':ROOT+'/reports/p7b-clean-smoke-'+stamp+'.out'}
 out=p/'clean-reference-smoke.json'
 def persist(): out.write_text(json.dumps(r,indent=2,default=str)+'\n')
 def stage(x): r['status']=x; persist(); print(x,flush=True)
 signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('diagnostic deadline')))
 signal.alarm(30); s=connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5); signal.alarm(0)
 assert s.settings.setup.models.multiphase.model()=='mixture'
 assert s.settings.setup.general.solver.time()=='steady'
 assert s.settings.setup.user_defined.auto_compile_compiled_functions() is False
 assert not any(source_flags(s).values())
 r['residual_settings']=s.settings.solution.monitor.residual.get_state()
 r['profile_update_interval']=s.settings.solution.run_calculation.profile_update_interval()
 assert r['profile_update_interval']==1
 r['domains']=s.scheme.eval("(cx-send '(rpgetvar 'domains))")
 s.settings.file.start_transcript(file_name=r['transcript'])
 try:
  stage('HYBRID_INITIALIZATION'); signal.alarm(120)
  s.settings.solution.initialization.hybrid_initialize(); signal.alarm(0)
  r['initial_counts']=counts(s)
  # Calibrate actual numbering against the file-backed report below. Fluent's
  # Iteration expression evaluates to 1 immediately after Hybrid Initialization.
  exprs=s.settings.setup.named_expressions
  exprs.create(name='P7bCleanWaterVolume')
  exprs['P7bCleanWaterVolume'].definition=f'VolumeInt(Volumefraction(phase="phase-2"),["{ZONE}"])'
  r['initial_water_volume']=exprs['P7bCleanWaterVolume'].get_value()
  v=s.settings.solution.report_definitions.volume; v.create(name='p7b-clean-native-water')
  v['p7b-clean-native-water'].report_type='volume-integral'
  v['p7b-clean-native-water'].field='phase-2-vof'
  v['p7b-clean-native-water'].cell_zones=[ZONE]
  e=s.settings.solution.report_definitions.single_valued_expression; e.create(name='p7b-clean-expression-water')
  e['p7b-clean-expression-water'].definition='P7bCleanWaterVolume'
  files=s.settings.solution.monitor.report_files; files.create(name='p7b-clean-water-history')
  rf=files['p7b-clean-water-history']; rf.file_name=r['report']; rf.report_defs=['p7b-clean-native-water','p7b-clean-expression-water']; rf.frequency=1; rf.active=True
  assert ntpath.normcase(ntpath.normpath(rf.file_name()))==ntpath.normcase(ntpath.normpath(r['report']))
  r['report_readback']=rf.get_state(); r['initial_source_flags']=source_flags(s)
  stage('SAVING_INITIAL_PAIR'); s.settings.file.write_case_data(file_name=r['initial_case'])
  r['initial_data']=r['initial_case'].replace('.cas.h5','.dat.h5')
  assert all(remote_file_exists(s,r[k]) for k in ['initial_case','initial_data'])
  stage('REOPENING_INITIAL_PAIR'); signal.alarm(120)
  s.settings.file.read_case_data(file_name=r['initial_case']); signal.alarm(0)
  r['reopened_counts']=counts(s); r['reopened_water_volume']=s.settings.setup.named_expressions['P7bCleanWaterVolume'].get_value()
  # Fresh initialized data reloads at global iteration 0 even though the
  # expression evaluated to 1 immediately after Hybrid Initialization.
  assert r['reopened_counts']['global_iteration']==0
  assert not any(source_flags(s).values())
  s.settings.file.stop_transcript()
  before=read_text(s,r['transcript']); (p/'clean-reference-smoke-setup.trn').write_text(before)
  assert 'SEGMENTATION VIOLATION' not in before
  r['solve_transcript']=ROOT+'/logs/p7b-clean-smoke-solve-'+stamp+'.trn'
  s.settings.file.start_transcript(file_name=r['solve_transcript'])
  stage('RUNNING_THREE_SOURCE_FREE_ITERATIONS'); signal.alarm(120)
  s.settings.solution.run_calculation.iterate(iter_count=3); signal.alarm(0)
  r['after_counts']=counts(s); r['final_source_flags']=source_flags(s)
  s.settings.file.stop_transcript()
  txt=read_text(s,r['solve_transcript']); (p/'clean-reference-smoke-solve.trn').write_text(txt)
  rpt=read_text(s,r['report']); (p/'clean-reference-smoke.out').write_text(rpt)
  r['cortex_fault_count']=txt.count('SEGMENTATION VIOLATION')
  rows=[[float(v) for v in l.split()] for l in rpt.splitlines() if re.match(r'^\d+\s',l)]
  r['report_rows']=rows; r['residual_iterations']=[int(x) for x in re.findall(r'^\s*(\d+)\s+\d\.\d+e',txt,re.M)]
  persist()
  assert r['cortex_fault_count']==0
  assert not any(r['final_source_flags'].values())
  assert [int(x[0]) for x in rows]==[1,2,3]
  assert r['residual_iterations']==[1,2,3]
  assert r['after_counts']['global_iteration']==3
  assert all(abs(x[1]-x[2])<1e-12 for x in rows)
  stage('SAVING_DIAGNOSTIC_FINAL_PAIR'); s.settings.file.write_case_data(file_name=r['final_case'])
  r['final_data']=r['final_case'].replace('.cas.h5','.dat.h5')
  assert all(remote_file_exists(s,r[k]) for k in ['final_case','final_data'])
  stage('CLEAN_THREE_ITERATION_SMOKE_PASS')
 except Exception as exc:
  signal.alarm(0); r['error']=str(exc); (p/'clean-reference-smoke-error.txt').write_text(traceback.format_exc()); stage('BLOCKED')
  try: s.settings.file.stop_transcript()
  except Exception: pass
  raise
 print(json.dumps({k:v for k,v in r.items() if k not in ['domains','residual_settings']},indent=2),flush=True)
if __name__=='__main__': main()
