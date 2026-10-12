"""Bounded Server 1 Scheme transport for host file operations only.

This creates no Fluent solver session and exposes no solve/settings commands.
Use only proven file expressions and external host process operations.
"""
from types import SimpleNamespace
from pathlib import PureWindowsPath
import grpc
from phase9_server1_680k_common import run
from pyansys_fluent.connection import resolve_connection_kwargs
from ansys.api.fluent.v0 import scheme_eval_pb2,scheme_eval_pb2_grpc
from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import Symbol as S,_convert_py_value_to_scheme_pointer,_convert_scheme_pointer_to_py_value


def attach_files(host_repo):
 details=resolve_connection_kwargs('1',start_transcript=False)
 channel=grpc.insecure_channel(str(details['ip'])+':'+str(details['port']));stub=scheme_eval_pb2_grpc.SchemeEvalStub(channel)
 class Scheme:
  def eval(self,expression):
   request=scheme_eval_pb2.SchemeEvalRequest()
   _convert_py_value_to_scheme_pointer((S('eval'),(S('with-input-from-string'),expression,S('read')),S('user-initial-environment')),request.input)
   reply=stub.SchemeEval(request,metadata=[('password',details['password'])],timeout=20)
   return _convert_scheme_pointer_to_py_value(reply.output)
 run.WORK=PureWindowsPath(host_repo).parent
 return SimpleNamespace(scheme=Scheme(),file_transport_channel=channel)
