from pathlib import Path
import sys,json,functools
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from pyansys_fluent.connection import connect
import ansys.fluent.core._grpc_services as low
import ansys.fluent.core.services as high
from ansys.fluent.core.utils.fluent_version import FluentVersion
from ansys.fluent.core import config
from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import SchemeInterpreterService
from ansys.api.fluent.v0 import scheme_eval_pb2
low._server_supports_v1=lambda channel:False
high.create_service_factory=functools.partial(high.create_service_factory,product_version=FluentVersion.v252)
config.check_health=False
original=SchemeInterpreterService.string_eval
def bounded(self,expression):
    return self._stub.StringEval(scheme_eval_pb2.StringEvalRequest(input=expression),metadata=self._metadata,timeout=5).output
SchemeInterpreterService.string_eval=bounded
s=connect('4',start_transcript=False,tcp_timeout_seconds=5)
print('ATTACHED_SERVER4',flush=True)
version=str(s.get_fluent_version())
has_mesh=s.settings.setup.cell_zone_conditions.is_active()
idle=not has_mesh or s.settings.solution.run_calculation.iterate.is_active()
r={'server_id':'4','version':version,'has_mesh':has_mesh,'idle':idle}
if idle:
    r['userprofile']=s.scheme.eval('(getenv "USERPROFILE")')
    r['onedrive']=s.scheme.eval('(getenv "OneDriveCommercial")')
    if has_mesh:
        from run_phase72a_e27_server1_continuation import native_iteration
        r['native_iteration']=native_iteration(s)
        r['cell_zones']=s.settings.setup.cell_zone_conditions.get_state()
        try:r['film']=dict(s.rp_vars('wall-film/solution-state'))
        except Exception as exc:r['film_error_type']=type(exc).__name__
path=ROOT/'output/phase9-mesh-convergence-server4/20261007/initial-live-state.json'
path.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2),flush=True)
