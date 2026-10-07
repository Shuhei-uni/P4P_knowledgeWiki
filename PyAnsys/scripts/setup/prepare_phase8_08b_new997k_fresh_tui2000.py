"""Fresh Hybrid on08b-settings/new997k,OFF; prepare native server-local journal."""
from pathlib import Path
import sys,json,uuid
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase8_08b_native997k_off2000 as old
r=old.r
PARENT_OUT=old.OUT;OUT=old.PARENT_OUT/'fresh-tui2000-off';WORK=old.PARENT_WORK/'fresh-tui2000-off'
old.transfer.OUT=OUT;old.transfer.WORK=WORK;r.OUT=OUT;r.WORK=WORK
from pyansys_fluent.remote_text import write_ascii_text_new
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture

def main(resume_initialized=False):
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'raw').mkdir(exist_ok=True);assert not (OUT/'build.json').exists()
 s=r.attach();parent=json.loads((PARENT_OUT/'build.json').read_text())
 if not resume_initialized:old.audit(s,parent['reference']);assert old.native(s)==10000
 for folder in ['scratch','monitors','autosaves','raw']:r.ensure_remote_directory(s,str(WORK/folder))
 for kind in ['case','data']:assert r.hash_remote(s,parent['prepared_pair'][kind],'parent-'+kind)==parent['prepared_pair'][kind+'_sha256']
 raw=OUT/'raw/preparation-native.txt'
 if raw.exists():raw=OUT/'raw'/('preparation-'+uuid.uuid4().hex+'.txt')
 with SessionTranscriptCapture(s,stream_path=raw,echo=False):
  r.remote_chdir(s,str(WORK));s.settings.mesh.size_info()
  paths={name:str(WORK/'monitors'/(name+'.out')).replace('\\','/') for name in parent['report_paths']}
  for name,path in paths.items():
   if not resume_initialized:assert not r.remote_file_exists(s,path)
   s.settings.solution.monitor.report_files[name+'-rfile'].file_name=path
  s.settings.file.auto_save.set_state({'case_frequency':'each-time','data_frequency':100,'root_name':str(WORK/'autosaves/checkpoint').replace('\\','/'),'retain_most_recent_files':False,'append_file_name_with':{'file_suffix_type':'time-step','file_decimal_digit':6}})
  # Use native TUI initialization; no carrier verification iterations.
  if not resume_initialized:s.tui.solve.initialize.hyb_initialization()
  expr_before_save=old.native(s)
  option=s.settings.setup.models.discrete_phase.numerics.high_res_tracking.quad_face_centroid_enabled
  expected=parent['reference']['settings']['setup']['models']['discrete_phase']['numerics']['high_res_tracking']['quad_face_centroid_enabled']
  if option.get_state()!=expected:
   r.dump(OUT/'hybrid-tracking-option-restored.json',{'option':'quad_face_centroid_enabled','automatically_enabled_by_hybrid':option.get_state(),'original08b':expected})
   option.set_state(expected)
  reference=old.snapshot(s);assert reference==parent['reference'],'Original08b settings or report definitions changed during initialization'
  fresh_fields=old.fields(s)
  pair=old.transfer.save(s,'prepared-fresh-N0-off');pair['native_iteration']=0
  s.settings.file.read_case(file_name=pair['case']);s.settings.file.read_data(file_name=pair['data'])
  build={'status':'PREPARED_REOPEN_VERIFIED','server_id':'2','cells':997604,'start_iteration':0,'target_iteration':2000,'requested_iterations':2000,'parent_settings_pair':parent['prepared_pair'],'prepared_pair':pair,'reference':reference,'report_paths':paths,'report_definitions':parent['report_definitions'],'initialization':'Native TUI /solve/initialize/hyb-initialization','initial_fields':fresh_fields,'pre_save_iteration_expression':expr_before_save,'absorber_enabled':False,'journal':str(WORK/'run2000-off.jou'),'journal_endpoint_case':str(WORK/'journal-endpoint.cas.h5'),'journal_endpoint_data':str(WORK/'journal-endpoint.dat.h5'),'native_transcript':str(WORK/'raw/native-run.trn'),'execution':'One native /solve/iterate2000; paired autosaves every100; final journal endpoint verified by hostdriver','autosave':s.settings.file.auto_save.get_state(),'residual':s.settings.solution.monitor.residual.get_state(),'new_verification_solve_iterations':0}
  old.WORK=WORK;old.OUT=OUT;old.paths(s,build);build['audit']=old.audit(s,reference);assert old.native(s)==0
  build['reopened_fields']=old.fields(s)
  r.dump(OUT/'build.json',build);write_ascii_text_new(s,str(WORK/'build-host.json'),json.dumps(build,indent=2)+'\n')
  # Generic endpoint name avoids labelling an early stopped solve as N2000.
  journal='\n'.join(['/file/start-transcript "'+str(WORK/'raw/native-run.trn').replace('\\','/')+'"','/solve/iterate 2000','/file/write-case-data "'+str(WORK/'journal-endpoint.cas.h5').replace('\\','/')+'"','/file/stop-transcript',''])
  (OUT/'run2000-off.jou').write_text(journal);write_ascii_text_new(s,str(WORK/'run2000-off.jou'),journal)
 print('PREPARED_NEW997K_08B_SETTINGS_FRESH_N0_ABSORBER_OFF',flush=True)
if __name__=='__main__':main(resume_initialized='resume-initialized' in sys.argv)
