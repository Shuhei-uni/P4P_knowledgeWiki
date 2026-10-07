"""Verify completed delayed-absorber trial, including activation and schedule."""
from pathlib import Path
import json,hashlib,math
out=Path(__file__).resolve().parents[2]/'output/phase8-stage2/20261007/slow-enable3000'
m=json.loads((out/'run-manifest.json').read_text());r=json.loads((out/'final-reopen.json').read_text());b=json.loads((out/'build.json').read_text())
assert m['status']=='COMPLETE_VERIFIED_ANALYSIS_REQUIRED' and m['server_id']=='2'
assert m['verified_native_iteration']==r['native_iteration']==3000
assert len(m['segments'])==12
start=b.get('pre_run_verification_updates',0)
assert start in [0,10]
if start:
 assert b['iteration_proof']['executed_stage_iterations']==10
 assert len(b['iteration_proof']['native_transcript_iterations'])==10
for seg,(count,fraction) in zip(m['segments'],b['schedule']):
 assert seg['start']==start and seg['end']==start+count
 assert math.isclose(seg['feed']['multiplier'],fraction)
 assert seg['absorber_enabled']==(start>=1000) and not seg['solver_failure_markers']
 start+=count
assert m['activation']['native_iteration']==1000
assert m['activation']['before_pair']['native_iteration']==m['activation']['after_pair']['native_iteration']==1000
assert r['audit']['fixed_settings']=='PASS' and r['audit']['absorber_enabled']
assert len(r['report_coverage'])==18 and all(not x['missing'] for x in r['report_coverage'].values())
for kind in ['case','data']:
 h=hashlib.sha256()
 with Path(m['final_pair'][kind]).open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 assert h.hexdigest()==m['final_pair'][kind+'_sha256']
print('PASS: exactly3000 updates, low OFF/startup, activationN1000, ramp, final full feed, reopen/hash/18histories')
