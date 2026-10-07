"""Read-only final proof of the original08b native997k transfer; no solves."""
from pathlib import Path
import sys,json,math,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/setup'))
import transfer_phase8_08b_native997k as t
from pyansys_fluent.remote_text import write_ascii_text_new
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
s=t.r.attach();out=t.OUT;receipt=json.loads((out/'transfer-receipt.json').read_text())
with SessionTranscriptCapture(s,stream_path=out/'raw'/('final-verification-'+uuid.uuid4().hex+'.txt'),echo=False):
 source=json.loads((out/'source-live.json').read_text());audit=t.compare(s,source);fields=t.field_metrics(s)
 t.r.dump(out/'ready-fields.json',fields)
 def parse(x):
  # Native report compute returns one value/unit dictionary per definition.
  if isinstance(x,list):return {k:v for row in x for k,v in row.items()}
  return x
 mapped=parse(receipt['fields_mapped']);reopened=parse(receipt['fields_reopened']);ready=parse(fields)
 print('FIELD_VALUES',json.dumps({'mapped':mapped,'reopened':reopened,'ready':ready}),flush=True)
 for name,val in mapped.items():
  a=val[0] if isinstance(val,list) else val
  for state in [reopened,ready]:
   b=state[name][0] if isinstance(state[name],list) else state[name]
   assert math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-10),(name,a,b)
 script=t.WORK/'inspect-native-ready-mesh.py'
 if not t.r.remote_file_exists(s,str(script)):write_ascii_text_new(s,str(script),(t.r.ROOT/'scripts/inspection/inspect_phase9_mesh_inputs.py').read_text())
 result=t.WORK/'ready-topology.json';log=t.WORK/'ready-topology.log'
 python=t.BASE_WORK/'controller-venv/Scripts/python.exe'
 command="$p8MeshLog=(& "+t.r.q(python)+' '+t.r.q(script)+' --single-mesh '+t.r.q(receipt['ready_pair']['case'])+' --output '+t.r.q(result)+" 2>&1 | Out-String); [IO.File]::WriteAllText("+t.r.q(log)+",$p8MeshLog,[Text.Encoding]::ASCII)"
 t.r.powershell(s,command)
 if not t.r.remote_file_exists(s,str(result)):raise RuntimeError(t.r.read_text(s,str(log)))
 topo=json.loads(t.r.read_text(s,str(result)));assert topo['cells']==997604
 assert len(topo['cell_zones'])==1 and topo['cell_zones'][0]['name']=='fluid'
 assert {z['name']:z['zoneType'] for z in topo['face_zones']}=={'wall':3,'bottom':3,'steamoutlet':5,'liquidinlet':20,'steaminlet':20,'interior-fluid':2}
 for kind in ['case','data']:assert t.r.hash_remote(s,receipt['ready_pair'][kind],'ready-verify-'+kind)==receipt['ready_pair'][kind+'_sha256']
 t.r.dump(out/'ready-topology.json',topo)
 t.r.dump(out/'final-verification.json',{'status':'PASS','server_id':'2','settings_audit':audit,'fields_reproduced_on_reopen':True,'fields':fields,'cells':topo['cells'],'pair_hashes_verified':True,'new_solve_iterations':0})
 print('FINAL_VERIFICATION_PASS',flush=True)
