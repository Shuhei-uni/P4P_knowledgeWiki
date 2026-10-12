"""Server 3-only transport and isolated paths; never connect to another server."""
from pathlib import Path,PureWindowsPath
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_mesh_startup as run
from pyansys_fluent.connection import connect
OUT=ROOT/'output/phase9-ewf-server3-997k/20261010';OUT.mkdir(parents=True,exist_ok=True)
STATIC=ROOT/'output/phase9-mesh-convergence/20261007'
contract=OUT/'08b-approved-bulk-contract.json'
if not contract.exists():contract.write_bytes((STATIC/contract.name).read_bytes())
run.OUT=OUT

def attach(profile=None):
 # This endpoint was independently verified as Fluent 2025 R2 before launch.
 # Use the repository's proven v252 attach route; avoid unbounded reflection.
 import functools
 import ansys.fluent.core._grpc_services as low
 import ansys.fluent.core.services as high
 from ansys.fluent.core.utils.fluent_version import FluentVersion
 from ansys.fluent.core import config
 low._server_supports_v1=lambda channel:False
 high.create_service_factory=functools.partial(high.create_service_factory,product_version=FluentVersion.v252)
 config.check_health=False
 s=connect('3',start_transcript=False,tcp_timeout_seconds=5)
 if profile is None:profile=s.scheme.eval('(getenv "USERPROFILE")')
 if not isinstance(profile,str) or not profile:raise RuntimeError('Cannot resolve Server 3 user profile')
 run.WORK=PureWindowsPath(profile)/'Documents/FluentRuns/Phase9-Server3-997k/20261010'
 run.SHARED=PureWindowsPath(profile)/'OneDrive - The University of Auckland'
 return s
