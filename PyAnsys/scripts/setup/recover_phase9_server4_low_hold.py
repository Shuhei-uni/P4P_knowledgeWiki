"""Verify the completed Server 4 low-feed hold after a laptop RPC loss.
No solve, initialization, feed change, process exit, or restart is submitted.
"""
from pathlib import Path,PureWindowsPath
import sys,json,time,math,re,fcntl,copy
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
from run_phase72a_adaptive_film import FILM
out=run.OUT;tag=str(time.time_ns());evidence=out/('low-hold-recovery-'+tag);evidence.mkdir()
lock=(out/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
paths=json.loads((out/'server4-paths.json').read_text())
for key,name in [('work','WORK'),('shared','SHARED'),('parent','PARENT'),('mesh_folder','MESH_FOLDER'),('host_python','HOST_PYTHON')]:setattr(run,name,PureWindowsPath(paths[key]))
m=json.loads((out/'2_6M-run.json').read_text());campaign=json.loads((out/'campaign-manifest.json').read_text());pair=campaign['failure_pair']
run.dump(evidence/'original-run.json',m);run.dump(evidence/'original-campaign.json',campaign)
s=run.attach();run.require_idle(s)
coordinate=run.native_iteration(s)
run.dump(evidence/'live-coordinate.json',{'native_iteration':coordinate,'iterate_active':s.settings.solution.run_calculation.iterate.is_active(),'film':run.film(s)})
print('IDLE_COORDINATE',coordinate,flush=True)
assert coordinate==m['active_target']==pair['native_iteration']==3580
assert m['verified_native_end']==1600 and m['active_stage']=='low-feed-hold'
run.assert_bulk_active(s);run.require_bulk_audit(s);run.read_feed(s,.25)
text=run.read_text(s,m['active_transcript']);(evidence/'native-low-hold.trn').write_text(text)
rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
steps=1980;dt=1e-7;before_time=m['blocks'][-1]['film_end_s'];accepted=before_time+steps*dt
assert len(rows)==steps, f'Incomplete native film rows: {len(rows)}'
assert re.search(r'^\s*3580\s+',text,re.M), 'Native terminal print absent'
assert not re.search(r'floating point exception|fatal error|Divergence detected',text,re.I)
assert all(all(math.isfinite(x) for x in row) and 0<=row[2]<=1 for row in rows)
assert all(math.isclose(row[0],before_time+(i+1)*dt,abs_tol=1e-10,rel_tol=1e-6) and math.isclose(row[1],dt,rel_tol=1e-7) for i,row in enumerate(rows))
assert math.isclose(rows[-1][0],accepted,abs_tol=1e-12)
print('NATIVE_LOW_HOLD_ROWS_VERIFIED',len(rows),accepted,flush=True)
h=run.histories(s,m['report_paths'],list(m['report_paths']));ids=set(range(1581,3581))
assert len(h)==34 and all(ids.issubset(v) and all(math.isfinite(v[i]) for i in ids) for v in h.values())
run.dump(evidence/'report-coverage.json',{'status':'PASS','report_count':34,'window':[1581,3580],'all_finite':True})
print('ALL_34_HISTORIES_VERIFIED',flush=True)
for key in ['case','data']:
 assert run.remote_file_exists(s,pair[key])
 digest=run.remote_file_sha256(s,pair[key],str(run.WORK/'scratch'/(f'recovery-{key}-{tag}.sha256')))
 assert digest==pair[key+'_sha256'], 'Preserved endpoint hash changed'
before=run.base.state(s);template=json.loads(run.prepared_receipt('2_6M').read_text())['state']
assert all(math.isfinite(v[0]) for v in before['readback']['fields'].values())
for key in ['hooks','lower_film_wall','entry_faces','dpm','film_parameters','controls']:assert before['readback'][key]==template['readback'][key], 'Scientific invariant changed: '+key
assert before['methods']==template['methods']
proof={'status':'REOPEN_PENDING','pair':pair,'before':before,'film_rows':len(rows),'film_end_s':accepted}
run.dump(evidence/'checkpoint-proof.json',proof)
run.load(s,pair);after=run.base.state(s);run.require_bulk_audit(s);run.assert_bulk_active(s)
run.require_match(after['readback'],before['readback']);setup_check=run.require_setup_same(after['setup'],before['setup']);assert after['methods']==before['methods']
assert math.isclose(run.film(s)['film_elapsed_time'],accepted,abs_tol=1e-12)
proof.update(status='REOPEN_VERIFIED',after=after,setup_check=setup_check,film=run.film(s));run.dump(evidence/'checkpoint-proof.json',proof)
block={'stage':'low-feed-hold','start':1600,'end':3580,'film_start_s':before_time,'film_end_s':accepted,'step_s':dt,'peak_film_courant':max(row[2] for row in rows),'transcript':m['active_transcript'],'pair':pair,'fields':after['readback']['fields'],'checkpoint_proof':str(evidence/'checkpoint-proof.json'),'recovered_after':'laptop RPC keepalive watchdog timeout; native solve completed'}
m['blocks'].append(block);m.update(status='CHECKPOINT_VERIFIED',verified_native_end=3580,active_target=None,latest_pair=pair,recovery_evidence=str(evidence))
run.dump(out/'2_6M-run.json',m)
run.dump(evidence/'recovery-terminal.json',{'status':'N3580_RECOVERED_REOPEN_VERIFIED','native_iteration':3580,'film_end_s':accepted,'report_count':34,'no_solve_submitted':True})
print('N3580_RECOVERED_REOPEN_VERIFIED',str(evidence),flush=True)
