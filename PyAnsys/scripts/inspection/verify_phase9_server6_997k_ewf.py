"""Verify terminal Server 6 evidence without another Fluent mutation."""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/phase9-ewf-server6-997k/20261009'
m=json.loads((OUT/'run-manifest.json').read_text())
assert m['status']=='COMPLETE_VERIFIED' and m['server_id']=='6' and m['cells']==997604
assert m['verified_native_end']==50900 and math.isclose(m['accepted_film_s'],.2,abs_tol=1e-10)
assert len(m['blocks'])==10 and sum(b['count'] for b in m['blocks'])==42820
assert json.loads((OUT/'final-reopen.json').read_text())['pair']==m['latest_pair']
for b in m['blocks']:
 for k in ['case','data']:
  p=Path(b['pair'][k]);assert p.is_file()
  digest=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(8*1024*1024),b''):digest.update(chunk)
  assert digest.hexdigest()==b['pair'][k+'_sha256']
 if not b['bulk_active']:assert b['drain_proof']['verification']['status']=='PASS'
print('COMPLETE_VERIFIED: Server 6; 997604 cells; N50900; 200 ms; ten paired stage checkpoints.')
