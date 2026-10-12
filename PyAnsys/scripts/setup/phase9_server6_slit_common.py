"""Isolated Server 6 / 154k slit transport; shared mechanics, no other attach."""
from pathlib import Path, PureWindowsPath
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_mesh_startup as run
from pyansys_fluent.connection import connect
OUT=ROOT/'output/phase9-server6-slit154k/20261010'
OUT.mkdir(parents=True,exist_ok=True)
contract=OUT/'08b-approved-bulk-contract.json'
if not contract.exists():
    contract.write_bytes((ROOT/'output/phase9-mesh-convergence/20261007'/contract.name).read_bytes())
def attach():
    import functools
    import ansys.fluent.core._grpc_services as low
    import ansys.fluent.core.services as high
    from ansys.fluent.core.utils.fluent_version import FluentVersion
    from ansys.fluent.core import config
    low._server_supports_v1=lambda channel:False
    high.create_service_factory=functools.partial(high.create_service_factory,product_version=FluentVersion.v252)
    config.check_health=False
    from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import SchemeInterpreterService
    from ansys.api.fluent.v0 import scheme_eval_pb2
    original=SchemeInterpreterService.string_eval
    def bounded_version(self,input):
        if input=='(cx-version)':
            return self._stub.StringEval(scheme_eval_pb2.StringEvalRequest(input=input),metadata=self._metadata,timeout=5).output
        return original(self,input)
    SchemeInterpreterService.string_eval=bounded_version
    try:s=connect('6',start_transcript=False,tcp_timeout_seconds=5)
    finally:SchemeInterpreterService.string_eval=original
    value=s.scheme.eval('(getenv "USERPROFILE")')
    if not isinstance(value,str) or not value:raise RuntimeError('Server 6 profile unavailable')
    profile=PureWindowsPath(value)
    run.WORK=profile/'Documents/FluentRuns/Phase9-Server6-slit154k/20261010'
    run.SHARED=profile/'OneDrive - The University of Auckland'
    run.OUT=OUT
    return s
