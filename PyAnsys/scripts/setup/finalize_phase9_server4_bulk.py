"""Preserve the user-selected Server 4 initial-bulk endpoint; never solve."""
from pathlib import Path, PureWindowsPath
import sys, json, time, math, re, fcntl
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
from run_phase72a_adaptive_film import FILM
from pyansys_fluent.common import quote_scheme_string

out = run.OUT
tag = str(time.time_ns())
evidence = out/('final-initial-bulk-'+tag)
evidence.mkdir()
lock = (out/'controller.lock').open('a+')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
paths = json.loads((out/'server4-paths.json').read_text())
for key, name in [('work','WORK'),('shared','SHARED'),('parent','PARENT'),('mesh_folder','MESH_FOLDER'),('host_python','HOST_PYTHON')]:
    setattr(run, name, PureWindowsPath(paths[key]))
m = json.loads((out/'2_6M-run.json').read_text())
run.dump(evidence/'original-run.json', m)
s = run.attach()
run.require_idle(s)
end = run.native_iteration(s)
assert end == m['active_target'] == 8580
run.assert_bulk_active(s)
run.require_bulk_audit(s)
feed = run.read_feed(s, 1.0)
print('IDLE_FULL_FEED_ENDPOINT', end, flush=True)
# Close the inherited known batch transcript once, after native idle proof.
s.settings.file.stop_transcript()
text = run.read_text(s, m['active_transcript'])
(evidence/'native-final-batch.trn').write_text(text)
rows = [tuple(map(float, x.groups())) for x in FILM.finditer(text)]
start = m['verified_native_end']
before_time = m['blocks'][-1]['film_end_s']
dt = 1e-7
accepted = before_time+(end-start)*dt
assert len(rows) == end-start == 1000
assert re.search(r'^\s*'+str(end)+r'\s+', text, re.M)
assert not re.search(r'floating point exception|fatal error|Divergence detected', text, re.I)
assert all(all(math.isfinite(x) for x in row) and 0 <= row[2] <= 1 for row in rows)
assert all(math.isclose(row[0], before_time+(i+1)*dt, abs_tol=1e-10, rel_tol=1e-6)
           and math.isclose(row[1], dt, rel_tol=1e-7) for i,row in enumerate(rows))
h = run.histories(s, m['report_paths'], list(m['report_paths']))
ids = set(range(1581,end+1))
assert len(h) == 34 and all(ids.issubset(v) and all(math.isfinite(v[i]) for i in ids) for v in h.values())
run.dump(evidence/'report-coverage.json', {'status':'PASS','report_count':34,'window':[1581,end],'all_finite':True})
before = run.base.state(s)
assert all(math.isfinite(v[0]) for v in before['readback']['fields'].values())
pair = run.save(s, run.WORK/'2_6M', f'final-initial-bulk-N{end}-{tag}')
proof = {'status':'SAVED_REOPEN_PENDING','pair':pair,'before':before,'film_end_s':accepted}
run.dump(evidence/'checkpoint-proof.json', proof)
print('LOCAL_PAIR_SAVED_HASHED', end, flush=True)
run.load(s, pair)
after = run.base.state(s)
run.require_match(after['readback'], before['readback'])
proof['setup_check'] = run.require_setup_same(after['setup'], before['setup'])
assert after['methods'] == before['methods']
run.assert_bulk_active(s)
run.require_bulk_audit(s)
assert math.isclose(run.film(s)['film_elapsed_time'], accepted, abs_tol=1e-12)
proof.update(status='REOPEN_VERIFIED', after=after, film=run.film(s))
run.dump(evidence/'checkpoint-proof.json', proof)
print('LOCAL_PAIR_REOPEN_VERIFIED', flush=True)
destination = run.SHARED/'P4P-Fluent-Artifacts'/'Phase9'/'Server4'/'2_6M'/f'final-initial-bulk-N{end}-{tag}'
copy_script = run.WORK/'scratch'/f'copy-final-{tag}.py'
copy_receipt = run.WORK/'scratch'/f'copy-final-{tag}.json'
script = '\n'.join([
    'import pathlib,json,shutil,hashlib',
    'p='+repr(pair), 'dest=pathlib.Path('+repr(str(destination))+')',
    'dest.mkdir(parents=True,exist_ok=False)',
    'def digest(f):',
    ' h=hashlib.sha256()',
    ' with open(f,"rb") as stream:',
    '  for block in iter(lambda:stream.read(8*1024*1024),b""):h.update(block)',
    ' return h.hexdigest()',
    'r={"status":"COPY_HASH_VERIFIED","files":{}}',
    'for key in ["case","data"]:',
    ' src=pathlib.Path(p[key]); target=dest/src.name',
    ' shutil.copy2(src,target)',
    ' actual=digest(target)',
    ' assert actual==p[key+"_sha256"]',
    ' r["files"][key]={"path":str(target),"sha256":actual,"bytes":target.stat().st_size}',
    'pathlib.Path('+repr(str(copy_receipt))+').write_text(json.dumps(r,indent=2))',
    '(dest/"pair-copy-receipt.json").write_text(json.dumps(r,indent=2))',
])+'\n'
run.write_ascii_text_new(s,str(copy_script),script)
command = f'cmd /c ""{run.HOST_PYTHON}" "{copy_script}""'
result = s.scheme.eval(f'(system "{quote_scheme_string(command)}")')
assert result in (0,None), result
copied = json.loads(run.read_text(s,str(copy_receipt)))
assert copied['status'] == 'COPY_HASH_VERIFIED'
block = {'stage':'full-feed-hold','start':start,'end':end,'film_start_s':before_time,
         'film_end_s':accepted,'step_s':dt,'peak_film_courant':max(r[2] for r in rows),
         'transcript':m['active_transcript'],'pair':pair,'fields':after['readback']['fields'],
         'checkpoint_proof':str(evidence/'checkpoint-proof.json')}
m['blocks'].append(block)
m.update(status='FINAL_INITIAL_BULK_DEVELOPMENT',verified_native_end=end,active_target=None,latest_pair=pair)
screen = run.hold_screen(s,m)
m.setdefault('hold_screens',[]).append(screen)
run.refresh_hold_screens(m)
receipt = {'status':'FINAL_INITIAL_BULK_DEVELOPMENT','server_id':'4','mesh':'2_6M','cells':2596657,
           'native_iteration':end,'full_feed_iterations':end-m['full_hold_start'],
           'film_end_s':accepted,'film_step_s':dt,'peak_final_batch_courant':max(r[2] for r in rows),
           'feed':feed,'local_pair':pair,'onedrive':copied,'onedrive_directory':str(destination),
           'checkpoint_proof':str(evidence/'checkpoint-proof.json'),'last_window':screen,
           'all_bulk_equations_active':True,'ewf_settings_final':False,'no_solve_submitted':True,
           'authority':'User selects current endpoint as final initial bulk development despite unsteady state',
           'claim_limit':'Not steady state, final mesh convergence, mass closure or physical validation. Original 4000-update minimum not reached.',
           'cloud_sync':'Files and hashes verified in Server 4 OneDrive folder; remote cloud upload not independently verified.'}
run.dump(evidence/'final-receipt.json',receipt)
run.dump(out/'final-initial-bulk.json',receipt)
m.update(final_evidence=str(evidence),onedrive_final_pair=copied['files'])
run.dump(out/'2_6M-run.json',m)
run.write_ascii_text_new(s,str(destination/'final-initial-bulk.json'),json.dumps(receipt,indent=2)+'\n')
print('FINAL_PAIR_ONEDRIVE_HASH_VERIFIED',str(destination),flush=True)
