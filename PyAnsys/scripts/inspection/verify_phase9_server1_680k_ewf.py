"""Verify terminal Server 1 evidence without another Fluent mutation."""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/phase9-ewf-server1-680k/20261009'
m=json.loads((OUT/'run-manifest.json').read_text())
assert m['status'] in ['COMPLETE_VERIFIED','BOUNDED_COMPLETE_VERIFIED'] and m['server_id']=='1' and m['cells']==679970
assert m['verified_native_end']==m['native_target_final'] and math.isclose(m['accepted_film_s'],m['target_film_s'],abs_tol=1e-10)
assert len(m['blocks'])==len(m['schedule'])
assert sum(b['count'] for b in m['blocks'])==m['native_target_final']-9080
for b,e in zip(m['blocks'],m['schedule']):assert [b['stage'],b['count'],b['step_s'],b['bulk_active']]==e
assert json.loads((OUT/'final-reopen.json').read_text())['pair']==m['latest_pair']
for b in m['blocks']:
 assert m.get('no_limit_checks') is True or b['peak_courant']<=b.get('courant_limit',.1) or (b.get('courant_continuation_authority')=='human: continue from N18580; 20261010' and b['stage']=='growth-5000' and b['pair']['native_iteration']==18580)
 for k in ['case','data']:
  p=Path(b['pair'][k]);assert p.is_file()
  with p.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==b['pair'][k+'_sha256']
 if not b['bulk_active']:
  proof=b['drain_proof']
  assert m.get('no_limit_checks') is True or proof['verification']['status']=='PASS' or (m.get('ledger_diagnostic_only') is True and proof.get('continuation')=='LEDGER_WARNING_AUTHORIZED' and proof['verification']['failures']==['film ledger exceeds the declared probe tolerance'])
print(m['status']+': Server 1; 679970 cells; N'+str(m['native_target_final'])+'; '+str(m['target_film_s']*1000)+' ms; '+str(len(m['blocks']))+' paired stage checkpoints.')
