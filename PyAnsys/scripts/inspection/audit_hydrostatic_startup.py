from pathlib import Path
import sys,json,signal,fcntl,os
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'PyAnsys/scripts/setup'))
from build_steady_vof_hydrostatic import connect,assert_contract,remote_file_exists,snapshot
from ansys.fluent.core.field_data_interfaces import SurfaceFieldDataRequest,ScalarFieldDataRequest,SurfaceDataType
import numpy as np
out=root/'PyAnsys/output/hydrostatic-startup-audit';out.mkdir(exist_ok=True)
lock=(root/'PyAnsys/output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('Bounded audit')));signal.alarm(180)
from datetime import datetime,timezone
try:
 s=connect(1,start_transcript=False,tcp_timeout_seconds=5)
except Exception as e:
 (out/'connectivity.json').write_text(json.dumps({'checked_at_utc':datetime.now(timezone.utc).isoformat(),'server':1,'reachable':False,'error_type':type(e).__name__,'solves_issued':0},indent=2));raise
(out/'connectivity.json').write_text(json.dumps({'checked_at_utc':datetime.now(timezone.utc).isoformat(),'server':1,'reachable':True,'solves_issued':0},indent=2))
assert not s.settings.solution.run_calculation.iterating();assert_contract(s)
rp=Path(json.loads((root/'PyAnsys/output/steady-vof-hydrostatic/n500-receipt.json').read_text())['run_manifest']);r=json.loads(rp.read_text());assert s.settings.setup.named_expressions['P9Iteration'].get_value()==1
assert all(remote_file_exists(s,r['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
a={'native_iteration':1,'iterating':False,'preserved_pair':r['case'],'settings':snapshot(s),'patch_arguments':s.settings.solution.initialization.patch.calculate_patch.argument_names,'patch_state':s.settings.solution.initialization.patch.get_state(),'initialization_children':s.settings.solution.initialization.child_names}
(out/'live-audit.json').write_text(json.dumps(a,indent=2,default=str));print({k:v for k,v in a.items() if k!='settings'})
names=['brine-outlet','steam-outlet','liquid-inlet','steam-inlet'];data=s.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=names,data_types=[SurfaceDataType.FacesCentroid]))
np.savez_compressed(out/'boundary-centroids.npz',**{n:np.asarray(data[n].face_centroids) for n in names})

for boundary_value in [False,True]:
 try:
  pressure=s.fields.field_data.get_field_data(ScalarFieldDataRequest(field_name='pressure',surfaces=names,node_value=False,boundary_value=boundary_value))
  np.savez_compressed(out/('boundary-pressure-'+str(boundary_value)+'.npz'),**{n:np.asarray(pressure[n]) for n in names})
 except Exception as e:
  (out/('boundary-pressure-'+str(boundary_value)+'-error.json')).write_text(json.dumps({'error':repr(e)}))
print('Live audit captured; no solver iterations or field mutations issued.')
