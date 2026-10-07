"""Verify revised startup and exactly 2200 iterations on Server 2."""
from pathlib import Path
import json,hashlib,math
out=Path(__file__).resolve().parents[2]/'output/phase8-stage2/20261007/step-enable2200'
m=json.loads((out/'run-manifest.json').read_text());r=json.loads((out/'final-reopen.json').read_text());b=json.loads((out/'build.json').read_text())
assert m['status']=='COMPLETE_VERIFIED_ANALYSIS_REQUIRED' and m['server_id']=='2'
assert m['requested_total_iterations']==m['verified_native_iteration']==r['native_iteration']==2200
assert b['schedule']==[[200,.25],[500,.25],[250,.5],[250,.75],[1000,1.]]
assert len(m['segments'])==5
start=0
for seg,(count,fraction) in zip(m['segments'],b['schedule']):
 assert seg['start']==start and seg['end']==start+count
 assert math.isclose(seg['feed']['multiplier'],fraction)
 assert seg['absorber_enabled']==(start>=200) and not seg['solver_failure_markers']
 start+=count
assert m['activation']['native_iteration']==200
assert m['activation']['before_pair']['native_iteration']==m['activation']['after_pair']['native_iteration']==200
assert [x['native_iteration'] for x in m['checkpoints']]==[200,700,950,1200,2200]
assert r['audit']['fixed_settings']=='PASS' and r['audit']['absorber_enabled']
assert len(r['report_coverage'])==18 and all(not x['missing'] for x in r['report_coverage'].values())
for kind in ['case','data']:
 h=hashlib.sha256()
 with Path(m['final_pair'][kind]).open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 assert h.hexdigest()==m['final_pair'][kind+'_sha256']
print('PASS: N2200, 200 OFF +500 low ON +2x250 steps +1000 full; activation, checkpoints, finalreopen/hashes, reports')
