"""Reframe unrun freshN0 preparation to10000 native iterations/1000 autosaves."""
from pathlib import Path
import sys,json,copy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_phase8_08b_new997k_fresh_tui2000 as initial
r=initial.r;old=initial.old
SOURCE_OUT=initial.OUT
OUT=old.PARENT_OUT/'fresh-tui10000-off';WORK=old.PARENT_WORK/'fresh-tui10000-off'
r.OUT=OUT;r.WORK=WORK;old.OUT=OUT;old.WORK=WORK;old.transfer.OUT=OUT;old.transfer.WORK=WORK
from pyansys_fluent.remote_text import write_ascii_text_new
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture

def main():
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'raw').mkdir(exist_ok=True);assert not (OUT/'build.json').exists()
 parent=json.loads((SOURCE_OUT/'build.json').read_text());s=r.attach();old.audit(s,parent['reference']);assert old.native(s)==0
 for folder in ['scratch','monitors','autosaves','raw']:r.ensure_remote_directory(s,str(WORK/folder))
 for kind in ['case','data']:assert r.hash_remote(s,parent['prepared_pair'][kind],'fresh-source-'+kind)==parent['prepared_pair'][kind+'_sha256']
 with SessionTranscriptCapture(s,stream_path=OUT/'raw/preparation-native.txt',echo=False):
  r.remote_chdir(s,str(WORK));s.settings.mesh.size_info()
  paths={name:str(WORK/'monitors'/(name+'.out')).replace('\\','/') for name in parent['report_paths']}
  for name,path in paths.items():assert not r.remote_file_exists(s,path);s.settings.solution.monitor.report_files[name+'-rfile'].file_name=path
  s.settings.file.auto_save.set_state({'case_frequency':'each-time','data_frequency':1000,'root_name':str(WORK/'autosaves/checkpoint').replace('\\','/'),'retain_most_recent_files':False,'append_file_name_with':{'file_suffix_type':'time-step','file_decimal_digit':6}})
  # Retain the already verified fresh initialization; no extra Hybrid or flow solves.
  reference=old.snapshot(s);assert reference==parent['reference']
  pair=old.transfer.save(s,'prepared-fresh-N0-off');pair['native_iteration']=0
  s.settings.file.read_case(file_name=pair['case']);s.settings.file.read_data(file_name=pair['data'])
  b=copy.deepcopy(parent);b.update(status='PREPARED_REOPEN_VERIFIED',target_iteration=10000,requested_iterations=10000,prepared_pair=pair,report_paths=paths,journal=str(WORK/'run10000-off.jou'),journal_endpoint_case=str(WORK/'journal-endpoint.cas.h5'),journal_endpoint_data=str(WORK/'journal-endpoint.dat.h5'),native_transcript=str(WORK/'raw/native-run.trn'),execution='One native /solve/iterate10000; paired autosaves every1000; final journal endpoint verified by hostdriver',autosave=s.settings.file.auto_save.get_state(),superseded_unrun_preparation_pair=parent['prepared_pair'],new_verification_solve_iterations=0)
  old.paths(s,b);assert old.native(s)==0;b['audit']=old.audit(s,reference);b['reopened_fields']=old.fields(s);b['autosave']=s.settings.file.auto_save.get_state()
  assert s.settings.file.auto_save.data_frequency()==1000 and s.settings.file.auto_save.case_frequency()=='each-time'
  r.dump(OUT/'build.json',b);write_ascii_text_new(s,str(WORK/'build-host.json'),json.dumps(b,indent=2)+'\n')
  journal='\n'.join(['/file/start-transcript "'+str(WORK/'raw/native-run.trn').replace('\\','/')+'"','/solve/iterate 10000','/file/write-case-data "'+str(WORK/'journal-endpoint.cas.h5').replace('\\','/')+'"','/file/stop-transcript',''])
  (OUT/'run10000-off.jou').write_text(journal);write_ascii_text_new(s,str(WORK/'run10000-off.jou'),journal)
  r.dump(SOURCE_OUT/'superseded-before-solving.json',{'status':'SUPERSEDED_BEFORE_SOLVING','replacement':'fresh-tui10000-off','reason':'Userchanged requested horizon to10000 and checkpointcadence1000','carrier_solve_updates':0})
 print('PREPARED_FRESH_NEW997K_08B_SETTINGS_OFF_10000_TUI_1000_AUTOSAVE',flush=True)
if __name__=='__main__':main()
