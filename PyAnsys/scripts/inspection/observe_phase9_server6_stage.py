"""Finite read-only stage observer: native stage file avoids historical stream replay."""
import sys,json,grpc,time,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'scripts/setup'),str(ROOT/'src')]
from phase9_server6_997k_common import run,OUT
from pyansys_fluent.connection import resolve_connection_kwargs
from ansys.api.fluent.v0 import scheme_eval_pb2 as pb,scheme_eval_pb2_grpc as rpc
from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import Symbol as S,_convert_py_value_to_scheme_pointer as put,_convert_scheme_pointer_to_py_value as get
from pyansys_fluent.ewf_staged import FILM

def main():
 kw=resolve_connection_kwargs('6',start_transcript=False);launch=json.loads((OUT/'host-launch.json').read_text())
 with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
  stub=rpc.SchemeEvalStub(channel)
  class Reader:
   def __init__(self):self.scheme=self
   def eval(self,expr):
    req=pb.SchemeEvalRequest();put((S('eval'),(S('with-input-from-string'),expr,S('read')),S('user-initial-environment')),req.input)
    return get(stub.SchemeEval(req,timeout=5,metadata=(('password',kw['password']),)).output)
  reader=Reader();deadline=time.monotonic()+180
  while time.monotonic()<deadline:
   try:
    m=json.loads(run.read_text(reader,launch['run_manifest']));run.dump(OUT/'host-run-manifest.json',m)
    if m['status']=='RECOVERY_REQUIRED':print('CONTROLLER_REQUIRES_RECOVERY',m.get('error'),flush=True);return
    if m.get('active_target') and m.get('active_stage')=='step-2p5us':
     text=run.read_text(reader,m['active_transcript']);rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
     if rows:
      print('NATIVE_STAGE_ROWS',len(rows),'FIRST',rows[0],'LAST',rows[-1],flush=True)
      valid=all(all(math.isfinite(v) for v in row) and math.isclose(row[1],2.5e-6,rel_tol=1e-7) and row[0]>.0009 for row in rows)
      result={'status':'FROZEN_2P5US_ADVANCEMENT_OBSERVED' if valid else 'NATIVE_STAGE_STEP_OR_CLOCK_DIFFERS','server_id':'6','film_time_s':rows[-1][0],'film_step_s':rows[-1][1],'observed_peak_courant':max(x[2] for x in rows),'source':m['active_transcript'],'verified_origin':10580,'active_native_target':11580,'observed_updates':len(rows),'observer_mutations':0,'final_endpoint_complete':False}
      run.dump(OUT/'resume-native-observation.json',result);print(json.dumps(result,indent=2),flush=True);return
   except grpc.RpcError as exc:print('BOUNDED_READ_UNCONFIRMED',exc.code().name,flush=True)
   time.sleep(10)
  print('NO_CURRENT_STAGE_FILM_ROW_WITHIN_WINDOW',flush=True)
if __name__=='__main__':main()
