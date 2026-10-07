"""Server-local driver: one native journal; verify end without laptop dependency."""
from pathlib import Path,PureWindowsPath
import sys,json,math,traceback
# Existing verified host controller libraries, passed explicitly by deployer.
sys.path.insert(0,sys.argv[1])
import run_phase8_08b_native997k_off2000 as old
r=old.r
OUT=Path(sys.argv[2]);WORK=PureWindowsPath(str(OUT))
r.OUT=OUT;r.WORK=WORK;old.OUT=OUT;old.WORK=WORK;old.transfer.OUT=OUT;old.transfer.WORK=WORK
b=json.loads((OUT/'build-host.json').read_text());TARGET=b['target_iteration']

def main():
 assert not (OUT/'run-manifest.json').exists();s=r.attach();old.paths(s,b);old.audit(s,b['reference']);assert old.native(s)==0
 m={'status':'RUNNING','server_id':'2','cells':997604,'start_iteration':0,'target_iteration':TARGET,'absorber_enabled':False,'journal':b['journal'],'tui_command':'/solve/iterate '+str(TARGET),'execution_host':'SERVER2_WINDOWS','laptop_required':False,'started_utc':r.now()};r.dump(OUT/'run-manifest.json',m)
 try:
  # Fluent executes the full journal natively, including solve, autosave and final write.
  s.tui.file.read_journal(b['journal'])
  n=old.native(s);m['observed_native_iteration']=n
  native_log=Path(b['native_transcript']).read_text(errors='replace');failed=bool(r.FAILURE_MARKER.search(native_log))
  m['native_failure_marker']=failed
  pair={'case':b['journal_endpoint_case'],'data':b['journal_endpoint_data'],'native_iteration':n}
  for kind in ['case','data']:assert Path(pair[kind]).is_file();pair[kind+'_sha256']=r.hash_remote(s,pair[kind],'endpoint-'+kind)
  m['journal_endpoint_pair']=pair
  assert n==TARGET and not failed,('Native journal stopped early or failed',n,failed)
  before=old.fields(s);s.settings.file.read_case(file_name=pair['case']);s.settings.file.read_data(file_name=pair['data']);old.paths(s,b);a=old.audit(s,b['reference']);after=old.fields(s);assert old.native(s)==TARGET
  def flat(values):return {k:v[0] for row in values for k,v in row.items()}
  for name,value in flat(before).items():assert math.isclose(value,flat(after)[name],rel_tol=1e-9,abs_tol=1e-10),(name,value,flat(after)[name])
  histories={name:Path(path).read_text() for name,path in b['report_paths'].items()};coverage={}
  for name,value in histories.items():
   ids={int(line.split()[0]) for line in value.splitlines() if line.split() and line.split()[0].isdigit()};missing=sorted(set(range(10,TARGET+1,10))-ids);coverage[name]={'samples':len(ids),'missing':missing};assert not missing,(name,missing)
  r.dump(OUT/'report-histories.json',histories);r.dump(OUT/'final-reopen.json',{'native_iteration':TARGET,'pair':pair,'audit':a,'before':before,'after':after,'report_coverage':coverage})
  m.update(status='COMPLETE_VERIFIED_ANALYSIS_REQUIRED',final_pair=pair,completed_utc=r.now());r.dump(OUT/'run-manifest.json',m);print('COMPLETE_NATIVE_TUI',TARGET,'OFF_SAVE_REOPEN_VERIFIED',flush=True)
 except Exception:
  m.update(status='EXECUTION_STOPPED_DIAGNOSIS_REQUIRED',error=traceback.format_exc(),stopped_utc=r.now())
  try:m['observed_native_iteration']=old.native(s)
  except Exception:m['native_coordinate_readback']='Unavailable after solver/session failure; use transcript'
  m['autosave_files']=[{'name':p.name,'bytes':p.stat().st_size} for p in (OUT/'autosaves').glob('*') if p.is_file()]
  r.dump(OUT/'run-manifest.json',m);raise
if __name__=='__main__':main()
