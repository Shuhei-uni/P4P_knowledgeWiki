"""Server 5-only transport and isolated paths; never connect to another server."""
from pathlib import Path,PureWindowsPath
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_mesh_startup as run
from pyansys_fluent.connection import connect
OUT=ROOT/'output/phase9-ewf-server5/20261009';OUT.mkdir(parents=True,exist_ok=True)
STATIC=ROOT/'output/phase9-mesh-convergence/20261007'
contract=OUT/'08b-approved-bulk-contract.json'
if not contract.exists():contract.write_bytes((STATIC/contract.name).read_bytes())
run.OUT=OUT

def attach():
 from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import SchemeInterpreterService
 from ansys.api.fluent.v0 import scheme_eval_pb2
 original=SchemeInterpreterService.string_eval
 def bounded(self,expression):
  if expression=='(cx-version)':return self._stub.StringEval(scheme_eval_pb2.StringEvalRequest(input=expression),metadata=self._metadata,timeout=5).output
  return original(self,expression)
 SchemeInterpreterService.string_eval=bounded
 try:s=connect('5',start_transcript=False,tcp_timeout_seconds=5)
 finally:SchemeInterpreterService.string_eval=original
 profile=s.scheme.eval('(getenv "USERPROFILE")')
 if not isinstance(profile,str) or not profile:raise RuntimeError('Cannot resolve Server 5 user profile')
 run.WORK=PureWindowsPath(profile)/'Documents/FluentRuns/Phase9-Server5/20261009'
 run.SHARED=PureWindowsPath(profile)/'OneDrive - The University of Auckland'
 return s
