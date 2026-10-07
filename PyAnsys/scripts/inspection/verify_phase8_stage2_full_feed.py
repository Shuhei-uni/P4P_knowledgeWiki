"""Verify full-feed N3000 completion on the execution host."""
from pathlib import Path
import json,hashlib
out=Path(__file__).resolve().parents[2]/'output/phase8-stage2/20261007/full-feed3000'
m=json.loads((out/'run-manifest.json').read_text());r=json.loads((out/'final-reopen.json').read_text())
assert m['status']=='COMPLETE_VERIFIED_ANALYSIS_REQUIRED' and m['server_id']=='2'
assert m['requested_total_iterations']==3000 and m['verified_native_iteration']==r['native_iteration']==3000
assert [(x['start'],x['end']) for x in m['segments']]==[(0,1000),(1000,2000),(2000,3000)]
assert all(x['feed']['multiplier']==1 and not x['solver_failure_markers'] for x in m['segments'])
assert [x['native_iteration'] for x in m['checkpoints']]==[1000,2000,3000]
for kind in ['case','data']:
 h=hashlib.sha256()
 with Path(m['final_pair'][kind]).open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 assert h.hexdigest()==m['final_pair'][kind+'_sha256']
assert len(r['report_coverage'])==17 and all(not x['missing'] for x in r['report_coverage'].values())
print('PASS: fresh full feed, exactly 3000 updates, checkpoints, final hashes/reopen, all 17 reports')
