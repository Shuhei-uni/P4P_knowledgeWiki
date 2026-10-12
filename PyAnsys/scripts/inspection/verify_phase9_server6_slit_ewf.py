"""Verify terminal Server 6 evidence without another Fluent mutation."""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/phase9-server6-slit154k/20261010'
m=json.loads((OUT/'run-manifest.json').read_text())
assert m['status']=='COMPLETE_VERIFIED' and m['server_id']=='6' and m['cells']==154063
assert m['verified_native_end']==m['native_target_final'] and math.isclose(m['accepted_film_s'],m['target_film_s'],abs_tol=1e-10)
assert len(m['blocks'])==len(m['schedule'])
assert m['verified_native_end']==m['start_pair']['native_iteration']+sum(b['count'] for b in m['blocks'])
assert math.isclose(m['start_film_s']+sum(b['count']*b['step_s'] for b in m['blocks']),m['target_film_s'],abs_tol=1e-10)
final_bulk=[]
for b in reversed(m['blocks']):
 if not b['bulk_active']:break
 final_bulk.insert(0,b)
assert final_bulk and math.isclose(final_bulk[0]['film_start_s'],m['target_film_s']-.005,abs_tol=1e-10)
assert math.isclose(sum(b['count']*b['step_s'] for b in final_bulk),.005,abs_tol=1e-10)
assert json.loads((OUT/'final-reopen.json').read_text())['pair']==m['latest_pair']
for b in m['blocks']:
 for k in ['case','data']:
  p=Path(b['pair'][k]);assert p.is_file()
  digest=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(8*1024*1024),b''):digest.update(chunk)
  assert digest.hexdigest()==b['pair'][k+'_sha256']
print(f"COMPLETE_VERIFIED: Server 6; 154063 cells; N{m['verified_native_end']}; {m['target_film_s']*1000:g} ms; {len(m['blocks'])} paired stage checkpoints.")
