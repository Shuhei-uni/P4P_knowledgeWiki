"""Offline terminal proof:08b settings/new997k, 2000 extra updates, OFF."""
from pathlib import Path
import json,hashlib
out=Path(__file__).resolve().parents[2]/'output/phase8-stage2/20261007/08b-native997k/run2000-off'
m=json.loads((out/'run-manifest.json').read_text());b=json.loads((out/'build.json').read_text());f=json.loads((out/'final-reopen.json').read_text())
assert m['status']=='COMPLETE_VERIFIED_ANALYSIS_REQUIRED'
assert m['server_id']=='2' and b['cells']==997604
assert m['start_iteration']==10000 and m['target_iteration']==m['verified_native_iteration']==f['native_iteration']==12000
assert m['additional_iterations']==2000 and not m['absorber_enabled'] and not f['audit']['absorber_enabled']
assert [(x['start'],x['end']) for x in m['segments']]==[(10000,11000),(11000,12000)]
assert all(not x['failure_marker'] and not x['absorber_enabled'] for x in m['segments'])
assert [x['native_iteration'] for x in m['checkpoints']]==[11000,12000]
assert len(f['report_coverage'])==17 and all(not x['missing'] for x in f['report_coverage'].values())
for kind in ['case','data']:
 h=hashlib.sha256()
 with Path(m['final_pair'][kind]).open('rb') as stream:
  for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
 assert h.hexdigest()==m['final_pair'][kind+'_sha256']
print('PASS: new997k,08b settings,2000 additional carrier updates,N12000,OFF,paired reopen/hashes,17 histories')
