"""Verify Stage 2 completion from native saved evidence on the execution host."""
from pathlib import Path
import json,hashlib,math
root=Path(__file__).resolve().parents[2]
out=root/'output/phase8-stage2/20261007'
m=json.loads((out/'run-manifest.json').read_text());r=json.loads((out/'final-reopen.json').read_text())
assert m['status']=='COMPLETE_VERIFIED_ANALYSIS_REQUIRED' and m['server_id']=='2'
assert m['verified_native_iteration']==5000 and r['native_iteration']==5000
assert m['pre_run_verification_updates']==10
segments=m['segments'];assert sum(x['end']-x['start'] for x in segments)==4990
previous=10
for x in segments:
 assert x['start']==previous and not x['solver_failure_markers'];previous=x['end']
 if x['end']<=1000:assert x['feed']['multiplier']==.25
 if x['start']>=2000:assert x['feed']['multiplier']==1
assert [x['native_iteration'] for x in m['checkpoints']]==[1000,2000,3000,4000,5000]
for kind in ['case','data']:
 path=Path(m['final_pair'][kind]);assert path.is_file()
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 assert h.hexdigest()==m['final_pair'][kind+'_sha256']
assert len(r['report_coverage'])==17 and all(not v['missing'] for v in r['report_coverage'].values())
print('PASS: N5000; total budget; schedule; local final pair hashes; reopened native counter; all 17 histories')
