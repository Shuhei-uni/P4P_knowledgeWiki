"""Passive transcript during carrier solves; reconcile terminal host evidence."""
from pathlib import Path
import sys,json,time,re,grpc,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase8_08b_native997k_off2000 as t
from pyansys_fluent.connection import resolve_connection_kwargs
from ansys.api.fluent.v0 import transcript_pb2,transcript_pb2_grpc
HOST=t.transfer.BASE_WORK/'controller-repo-08b-off2000/PyAnsys/output/phase8-stage2/20261007/08b-native997k/run2000-off'
ROW=re.compile(r'^\s*(\d+)\s+[-+\d.eE]+\s+[-+\d.eE]+\s+[-+\d.eE]+',re.M)
FAIL=re.compile(r'floating.point|fatal signal|bad termination|eof inside list|Error encountered in critical',re.I)

def fetch():
 s=t.r.attach();r=t.r
 if not r.remote_file_exists(s,str(HOST/'job-manifest.json')):return None
 job=json.loads(r.read_text(s,str(HOST/'job-manifest.json')));r.dump(t.OUT/'host-job-snapshot.json',job)
 if job['status'] not in ['COMPLETE','BLOCKED']:return None
 for name in ['run-manifest.json','report-histories.json','final-reopen.json','runner.log','verifier.log','raw/native-transcript.txt']:
  if r.remote_file_exists(s,str(HOST/name)):
   value=r.read_text(s,str(HOST/name));dest=t.OUT/('raw/host-native-transcript.txt' if name.startswith('raw/') else 'host-'+name)
   if dest.exists():assert dest.read_text()==value,dest
   else:dest.write_text(value)
 return 0 if job['status']=='COMPLETE' else 1

def main():
 deadline=time.monotonic()+36*3600;last=10000;tail='';hint=False;hint_at=None
 while time.monotonic()<deadline:
  if hint:
   try:
    result=fetch()
    if result is not None:return result
   except Exception as e:print('Terminal evidence not yet readable:',type(e).__name__,flush=True)
   if time.monotonic()-hint_at>300:
    t.r.dump(t.OUT/'monitor-terminal-recovery-required.json',{'status':'TERMINAL_HINT_HOST_EVIDENCE_UNAVAILABLE','last_printed_iteration':last,'native_tail':tail[-3000:],'action':'Recoverhostjob/checkpoints; no restart or new solve'})
    return 1
   time.sleep(20);continue
  k=resolve_connection_kwargs('2',start_transcript=False);channel=grpc.insecure_channel(str(k['ip'])+':'+str(k['port']))
  stream=transcript_pb2_grpc.TranscriptStub(channel).BeginStreaming(transcript_pb2.TranscriptRequest(),metadata=[('password',k['password'])],timeout=55)
  try:
   for response in stream:
    with (t.OUT/'raw/passive-native-transcript.txt').open('a') as handle:handle.write(response.transcript)
    tail=(tail+response.transcript)[-16000:];ids=[int(x) for x in ROW.findall(tail)];last=max([last]+[x for x in ids if 10000<=x<=12000])
    if last>=12000 or FAIL.search(tail):hint=True;hint_at=time.monotonic();stream.cancel();break
  except grpc.RpcError as e:
   if e.code() in [grpc.StatusCode.UNAVAILABLE,grpc.StatusCode.INTERNAL,grpc.StatusCode.UNKNOWN]:hint=True;hint_at=time.monotonic()
   if e.code()!=grpc.StatusCode.DEADLINE_EXCEEDED:print('Transcript transport:',e.code().name,flush=True)
  finally:channel.close()
  t.r.dump(t.OUT/'passive-progress.json',{'last_printed_iteration':last,'additional_printed_updates':last-10000,'terminal_hint':hint,'sampled_utc':t.r.now()})
  print('Passive native progress:',last,'terminal_hint:',hint,flush=True);time.sleep(5)
 raise RuntimeError('36-hour monitor horizon reached; inspecthoststate')
if __name__=='__main__':
 try:sys.exit(main())
 except Exception:traceback.print_exc();sys.exit(1)
