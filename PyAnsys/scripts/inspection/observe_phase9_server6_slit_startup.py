"""Bounded read-only native transcript prefix; no attach reflection or solve."""
from pathlib import Path
import json,sys,grpc,math
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.ewf_staged import FILM,residuals
from ansys.api.fluent.v0 import scheme_eval_pb2 as pb,scheme_eval_pb2_grpc as rpc
from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import Symbol as S,_convert_py_value_to_scheme_pointer as put,_convert_scheme_pointer_to_py_value as get
OUT=ROOT/'output/phase9-server6-slit154k/20261010'

def main():
 m=json.loads((OUT/'host-run-manifest.json').read_text())
 if not m.get('active_transcript'):print('NATIVE_COMMAND_NOT_YET_RECORDED');return
 kw=resolve_connection_kwargs('6',start_transcript=False,tcp_timeout_seconds=3)
 path=quote_scheme_string(m['active_transcript'].replace('\\','/'))
 expression='(let ((p (open-input-file "'+path+'"))) (let loop ((chars \'()) (n 0)) (let ((c (read-char p))) (if (or (eof-object? c) (>= n 131072)) (begin (close-input-port p) (list->string (reverse chars))) (loop (cons c chars) (+ n 1))))))'
 with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as channel:
  req=pb.SchemeEvalRequest();put((S('eval'),(S('with-input-from-string'),expression,S('read')),S('user-initial-environment')),req.input)
  try:text=get(rpc.SchemeEvalStub(channel).SchemeEval(req,timeout=5,metadata=(('password',kw['password']),)).output)
  except grpc.RpcError as e:print('BOUNDED_PREFIX_READ_UNCONFIRMED',e.code().name);return
 rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
 native=residuals(text)
 result={'status':'NATIVE_FILM_ADVANCEMENT_OBSERVED' if rows else 'NO_NATIVE_FILM_ROW_IN_PREFIX','server_id':'6','cells':154063,
         'active_stage':m['active_stage'],'active_target':m['active_target'],'source':m['active_transcript'],
         'observed_rows_in_prefix':len(rows),'first_film_row':rows[0] if rows else None,'last_prefix_film_row':rows[-1] if rows else None,
         'observed_native_in_prefix':max(native) if native else None,'read_limit_chars':131072,'solver_mutations':0,
         'scope':'Prefix establishes startup only; does not establish latest live or completed endpoint.'}
 if rows:
  assert all(all(math.isfinite(v) for v in row) and math.isclose(row[1],m['active_step_s'],rel_tol=1e-7) for row in rows)
  assert rows[-1][0]>m['start_film_s']
 (OUT/'native-startup-observation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
