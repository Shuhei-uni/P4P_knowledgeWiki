"""Read-only Server 1 stream, independent of a busy Fluent attach handshake."""
import argparse,json,re,sys,time
from pathlib import Path
import grpc
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src')]
from pyansys_fluent.connection import resolve_connection_kwargs
from ansys.api.fluent.v0 import transcript_pb2,transcript_pb2_grpc
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();p=args.output;p.parent.mkdir(parents=True,exist_ok=True)
if p.exists():raise FileExistsError('Use a fresh stream path to preserve evidence')
statepath=p.with_suffix('.state.json')
r=resolve_connection_kwargs('1',start_transcript=False)
if 'server_info_file_name' in r:raise RuntimeError('Explicit Server 1 endpoint required')
channel=grpc.insecure_channel(str(r['ip'])+':'+str(r['port']))
metadata=[('password',r['password'])]
stub=transcript_pb2_grpc.TranscriptStub(channel)
film=re.compile(r'Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)')
state={'status':'SUBSCRIBING','server_id':'1','mode':'read_only_raw_transcript','stream':str(p),'film_time_s':None,'film_step_s':None,'last_output_unix_s':None,'reconnects':0}
def save():
 temp=statepath.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(statepath)
save();print('SERVER1_RAW_TRANSCRIPT_SUBSCRIBER_READY',flush=True)
stream=None;buffer='';last_save=0
try:
 with p.open('x',buffering=1) as f:
  while True:
   try:
    stream=stub.BeginStreaming(transcript_pb2.TranscriptRequest(),metadata=metadata,timeout=3600)
    for response in stream:
     f.write(response.transcript);f.flush();buffer=(buffer+response.transcript)[-16000:]
     rows=list(film.finditer(buffer))
     if rows:
      latest=rows[-1];state.update(film_time_s=float(latest[1]),film_step_s=float(latest[2]),film_courant=float(latest[3]))
     now=time.time();state.update(status='STREAMING',last_output_unix_s=now)
     if now-last_save>=5:save();last_save=now
    state.update(status='STREAM_ENDED')
   except grpc.RpcError as e:state.update(status='RECONNECTING',last_rpc_status=e.code().name)
   state['reconnects']+=1;save();time.sleep(2)
finally:
 if stream is not None:stream.cancel()
 channel.close();state['status']='LAPTOP_OBSERVER_STOPPED';save()
