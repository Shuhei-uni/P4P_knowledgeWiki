"""Read-only terminal monitor for the Server 2 host controller."""
from pathlib import Path
import json,sys,time,traceback,subprocess
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from run_phase8_stage2_f2_simple import attach,OUT,WORK
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.common import remote_file_exists
SLOW_ENABLE='--slow-enable3000' in sys.argv
ABSORBER='--absorber3000' in sys.argv
FULL_FEED='--full-feed3000' in sys.argv or ABSORBER or SLOW_ENABLE
if SLOW_ENABLE:
 from run_phase8_stage2_slow_enable import OUT,BASE_WORK
 host=BASE_WORK/'controller-repo-slow-enable3000-retry01/PyAnsys/output/phase8-stage2/20261007/slow-enable3000'
elif ABSORBER:
 from run_phase8_stage2_absorber import OUT
 from run_phase8_stage2_full_feed import BASE_WORK
 host=BASE_WORK/'controller-repo-absorber3000-retry02/PyAnsys/output/phase8-stage2/20261007/absorber3000'
elif FULL_FEED:
 from run_phase8_stage2_full_feed import OUT,BASE_WORK
 host=BASE_WORK/'controller-repo-full-feed3000/PyAnsys/output/phase8-stage2/20261007/full-feed3000'
else:host=WORK/'controller-repo/PyAnsys/output/phase8-stage2/20261007'
JOB_NAME='job-manifest.json' if FULL_FEED else 'job-retry02-manifest.json'
LOG_NAMES=['runner.log','verifier.log'] if FULL_FEED else ['runner-retry02.log','verifier-retry02.log']
def probe():
 s=attach()
 if not remote_file_exists(s,str(host/JOB_NAME)):return 2
 job=json.loads(read_text(s,str(host/JOB_NAME)))
 (OUT/'host-job-snapshot.json').write_text(json.dumps(job,indent=2)+'\n')
 if job['status'] not in ['COMPLETE','BLOCKED']:return 2
 for name in ['run-manifest.json','report-histories.json','final-reopen.json','run-error.json','raw/native-transcript.txt']+LOG_NAMES:
  if remote_file_exists(s,str(host/name)):
   text=read_text(s,str(host/name));dest=OUT/(('raw/host-native-transcript-retry02.txt' if ABSORBER else 'raw/host-native-transcript-retry01.txt' if SLOW_ENABLE else 'raw/host-native-transcript.txt') if name.startswith('raw/') else ('host-retry02-' if ABSORBER else 'host-retry01-' if SLOW_ENABLE else 'host-')+name)
   if dest.exists():assert dest.read_text()==text,dest
   else:dest.write_text(text)
 print('HOST_TERMINAL',job['status'],flush=True)
 return 0 if job['status']=='COMPLETE' else 1

def main():
 if '--probe' in sys.argv:return probe()
 deadline=time.monotonic()+30*3600
 while time.monotonic()<deadline:
  try:
   result=subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),'--probe']+(['--slow-enable3000'] if SLOW_ENABLE else ['--absorber3000'] if ABSORBER else ['--full-feed3000'] if FULL_FEED else []),timeout=300,capture_output=True,text=True)
   print(result.stdout+result.stderr,flush=True)
   if result.returncode in [0,1]:return result.returncode
  except subprocess.TimeoutExpired:print('Read-only connection probe timed out; host run state remains unknown',flush=True)
  time.sleep(60)
 raise RuntimeError('Host monitor reached 30-hour external-connection deadline; inspect preserved host job')
if __name__=='__main__':
 try:sys.exit(main())
 except Exception:
  traceback.print_exc();sys.exit(3 if '--probe' in sys.argv else 1)
