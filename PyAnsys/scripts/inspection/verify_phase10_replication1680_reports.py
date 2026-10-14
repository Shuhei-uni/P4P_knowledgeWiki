"""Audit the original1680 report stop without a repeated solve or DPM update.

Requires byte-identical retrieval and independent controller absence. Preserve
the original error and compare post-reopen reports with the DPM transcript.
"""
from pathlib import Path
import json,sys,hashlib,re
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'PyAnsys/scripts'/d) for d in ['setup','inspection','analysis']]+[str(ROOT/'PyAnsys/src'),str(ROOT/'PyAnsys/src/pyansys_fluent')]
from extract_phase10_predivergence_fields import attach
from deploy_phase10_bf01 import Bridge
from pyansys_fluent.remote_text import write_ascii_text_new_labeled,read_text_bounded
from analyze_phase10_replication1600_dpm import audit_report,TERMINAL
import run_phase10_mesh_family as core
out=ROOT/'PyAnsys/output/phase10-single-inlet-mesh-convergence';dest=out/'replication-enthalpy-M04';folder=dest/'H1680';m=json.loads((folder/'raw/manifest.json').read_text());proof=json.loads((dest/'collection-recovery.json').read_text());assert proof['controller_absent_verified'] and proof['byte_identical'];assert m['solved_updates']==m['completed_iteration']==1500 and m['DPM_update_dispatches']==m['DPM_completed_updates']==1
aggregate=audit_report((folder/'raw/DPM-aggregate.txt').read_text(),109)
results={n:audit_report((folder/'raw'/('DPM-'+n+'.txt')).read_text(),v['initial_values']['mass_flow_rate']['total_flow_rate']) for n,v in m['settings_expected']['models']['discrete_phase']['injections'].items()}
tol=aggregate['printed_roundoff_bound_kg_s']+sum(v['printed_roundoff_bound_kg_s'] for v in results.values())
for fate in TERMINAL:assert abs(sum(v['final_mass_kg_s'][fate] for v in results.values())-aggregate['final_mass_kg_s'][fate])<=tol
assert sum(v['tracked_count'] for v in results.values())==aggregate['tracked_count'] and aggregate['terminal_counts']['aborted']==0
trn=(folder/'raw/DPM-tracking.trn').read_text();counts=re.findall(r'number tracked\s*=\s*(\d+)',trn);assert counts and int(counts[0])==aggregate['tracked_count']
s=attach(json.loads((out/'run-config.json').read_text()))
try:
 s.events.stop();assert not s.settings.solution.run_calculation.iterating() and core.iteration(s)==1500
 core.require_state_same(core.state(s),m['settings_expected']);before=core.compute(s,m['report_names'])
 for a,b in zip(before,m['checkpoints'][-1]['reports']):
  name=next(iter(a))
  if name!='p10-vorticity-mean':core.require_state_same(a,b)
 live_vort=next(v['p10-vorticity-mean'][0] for v in before if 'p10-vorticity-mean' in v)
 block=trn.split('p10-vorticity-mean',1)[1];printed=float(re.search(r'fluid\s+([0-9.]+)',block)[1]);assert abs(live_vort-printed)<=0.0000051
 core.reopen(s,m['tracked_pair']);assert core.iteration(s)==1500
 core.require_state_same(core.state(s),m['settings_expected']);core.require_state_same(core.compute(s,m['report_names']),before)
 assert s.fields.solution_variable_info.get_zones_info()['fluid'].count==946967
 state=core.state(s)
finally:s._fluent_connection._channel.close()
v=dict(m);v.update(original_status=m['status'],original_error=m['error'],status='COMPLETE_EVIDENCE_VERIFIED_UNQUALIFIED',aggregate=aggregate,injection_results=results,efficiency_percent=100*(1-aggregate['final_mass_kg_s']['escaped']/109),final_pair=m['tracked_pair'],strict_reopen_verified=True,controller_absent_verified=True,carrier_reports_unchanged=True,settings_readback=state,transcript_closed=True,DPM_transcript=m['tracked_pair']['case'].replace('\\','/').rsplit('/',1)[0]+'/DPM-tracking.trn',DPM_transcript_sha256=hashlib.sha256((folder/'raw/DPM-tracking.trn').read_bytes()).hexdigest(),report_sha256={n:hashlib.sha256((folder/'raw'/('DPM-'+n+'.txt')).read_bytes()).hexdigest() for n in m['report_files']},recovery={'format':'Single-fate reports omit Net; count/fate, feed-mass closure and aggregate reconciliation retained','additional_carrier_updates':0,'additional_DPM_updates':0,'original_error_manifest_sha256':hashlib.sha256((folder/'raw/manifest.json').read_bytes()).hexdigest(),'source_collection':str(dest/'collection-recovery.json'),'checkpoint_pre_reopen_vorticity_s_1':next(v['p10-vorticity-mean'][0] for v in m['checkpoints'][-1]['reports'] if 'p10-vorticity-mean' in v),'DPM_transcript_vorticity_s_1':printed,'current_post_reopen_vorticity_s_1':live_vort,'other_15_checkpoint_reports_exactly_unchanged':True})
cfg=json.loads((out/'run-config.json').read_text());b=Bridge(cfg)
try:
 path=m['tracked_pair']['case'].replace('\\','/').rsplit('/',1)[0]+'/verification-repaired.json'
 write_ascii_text_new_labeled(b,path,json.dumps(v,indent=2)+'\n');assert json.loads(read_text_bounded(b,path))==v
 v['native_verification']=path
finally:b.channel.close()
(folder/'verified-manifest.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps({'status':v['status'],'efficiency_percent':v['efficiency_percent'],'paired_reopen':True,'additional_carrier_updates':0,'additional_DPM_updates':0}))
