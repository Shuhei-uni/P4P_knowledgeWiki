"""Bounded read-only transcript prefix for the single Server6 150ms continuation."""
from pathlib import Path
import sys,json,grpc,math
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'PyAnsys/src'))
from pyansys_fluent.connection import resolve_connection_kwargs
from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.ewf_staged import FILM
from ansys.api.fluent.v0 import scheme_eval_pb2 as pb,scheme_eval_pb2_grpc as rpc
from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import Symbol as S,_convert_py_value_to_scheme_pointer as put,_convert_scheme_pointer_to_py_value as get
OUT=ROOT/'PyAnsys/output/phase10-proposed-design/20261013/vertical-basic-ewf-to150ms'
def main():
    m=json.loads((OUT/'host-run-manifest.json').read_text())
    assert m['status']=='RUNNING' and m.get('active_stage')=='ten-us-to150ms' and m.get('active_target')==44661
    kw=resolve_connection_kwargs('6',start_transcript=False,tcp_timeout_seconds=3)
    path=quote_scheme_string(m['active_transcript'].replace('\\','/'))
    expr='(let ((p (open-input-file "'+path+'"))) (let loop ((chars \'()) (n 0)) (let ((c (read-char p))) (if (or (eof-object? c) (>= n 100000)) (begin (close-input-port p) (list->string (reverse chars))) (loop (cons c chars) (+ n 1))))))'
    req=pb.SchemeEvalRequest();put((S('eval'),(S('with-input-from-string'),expr,S('read')),S('user-initial-environment')),req.input)
    with grpc.insecure_channel(f"{kw['ip']}:{kw['port']}") as ch:
        text=get(rpc.SchemeEvalStub(ch).SchemeEval(req,timeout=5,metadata=(('password',kw['password']),)).output)
    assert isinstance(text,str)
    (OUT/'native-startup-prefix.trn').write_text(text)
    rows=[list(map(float,x.groups())) for x in FILM.finditer(text)]
    assert rows and all(math.isclose(row[1],1e-5,abs_tol=1e-12) for row in rows)
    assert rows[0][0]>.05 and rows[-1][0]<=.150000001
    r={'status':'NATIVE_FIXED_10US_STARTUP_VERIFIED','server_id':'6','scope':'bounded_transcript_prefix_not_latest_clock_or_final_endpoint','film_rows_observed':len(rows),'first_film_row':rows[0],'last_prefix_film_row':rows[-1],'all_observed_steps_s':1e-5,'target_native_iteration':44661,'target_film_s':.15,'source_native_iteration':34661,'source_film_s':.05,'solver_mutations':0,'solve_replayed_after_timeout':False,'observed_utc':datetime.now(timezone.utc).isoformat()}
    (OUT/'native-startup.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
