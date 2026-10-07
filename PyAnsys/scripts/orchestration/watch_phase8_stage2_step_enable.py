"""Passive transcript monitoring; query Cortex files only after terminal hint."""
from pathlib import Path
import sys,json,time,re,traceback,grpc
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase8_stage2_step_enable as t
from pyansys_fluent.connection import resolve_connection_kwargs
from ansys.api.fluent.v0 import transcript_pb2,transcript_pb2_grpc
HOST=t.BASE_WORK/'controller-repo-step-enable2200/PyAnsys/output/phase8-stage2/20261007/step-enable2200'
ROW=re.compile(r'^\s*(\d+)\s+[-+\d.eE]+\s+[-+\d.eE]+\s+[-+\d.eE]+',re.M)
FAIL=re.compile(r'floating.point|fatal signal|bad termination|eof inside list|Error encountered in critical',re.I)

def fetch_terminal():
 s=t.base.attach();r=t.base
 if not r.remote_file_exists(s,str(HOST/'job-manifest.json')):return None
 job=json.loads(r.read_text(s,str(HOST/'job-manifest.json')))
 r.dump(t.OUT/'host-job-snapshot.json',job)
 if job['status'] not in ['COMPLETE','BLOCKED']:return None
 for name in ['run-manifest.json','report-histories.json','final-reopen.json','run-error.json','runner.log','verifier.log','raw/native-transcript.txt']:
  if r.remote_file_exists(s,str(HOST/name)):
   v=r.read_text(s,str(HOST/name));dest=t.OUT/('raw/host-native-transcript.txt' if name.startswith('raw/') else 'host-'+name)
   if dest.exists():assert dest.read_text()==v,dest
   else:dest.write_text(v)
 return 0 if job['status']=='COMPLETE' else 1

def main():
 deadline=time.monotonic()+30*3600;started=False;hint=False;tail='';last=0
 while time.monotonic()<deadline:
  if hint:
   try:
    status=fetch_terminal()
    if status is not None:return status
   except Exception as e:print('Terminal evidence not yet readable:',type(e).__name__,flush=True)
   time.sleep(60);continue
  k=resolve_connection_kwargs('2',start_transcript=False)
  channel=grpc.insecure_channel(str(k['ip'])+':'+str(k['port']))
  stream=transcript_pb2_grpc.TranscriptStub(channel).BeginStreaming(transcript_pb2.TranscriptRequest(),metadata=[('password',k['password'])],timeout=55)
  try:
   for response in stream:
    with (t.OUT/'raw/passive-native-transcript.txt').open('a') as evidence:
     evidence.write(response.transcript)
    tail=(tail+response.transcript)[-12000:]
    ids=[int(x) for x in ROW.findall(tail)]
    if any(1<=x<=200 for x in ids):started=True
    if started:
     last=max([last]+[x for x in ids if x<=2200])
     if last>=2200 or FAIL.search(tail):hint=True;stream.cancel();break
  except grpc.RpcError as e:
   if started and e.code() in [grpc.StatusCode.UNAVAILABLE,grpc.StatusCode.INTERNAL,grpc.StatusCode.UNKNOWN]:hint=True
   if e.code()!=grpc.StatusCode.DEADLINE_EXCEEDED:print('Transcript transport:',e.code().name,flush=True)
  finally:channel.close()
  print('Passive native progress:',last,'terminal_hint:',hint,flush=True)
  if hint:time.sleep(30)
  else:time.sleep(5)
 raise RuntimeError('30-hour monitor horizon reached; host state requires inspection')
if __name__=='__main__':
 try:sys.exit(main())
 except Exception:traceback.print_exc();sys.exit(1)
