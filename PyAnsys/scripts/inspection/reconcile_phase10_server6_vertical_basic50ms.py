from pathlib import Path
import sys,json,hashlib,math
from datetime import datetime,timezone
root=Path.cwd();sys.path.insert(0,str(root/'PyAnsys/scripts/setup'))
import run_phase10_server6_vertical_basic50ms as a
out=a.OUT
m=json.loads((out/'host-run-manifest.json').read_text());j=json.loads((out/'host-job-manifest.json').read_text())
assert m['status']=='COMPLETE_50MS_REOPEN_VERIFIED' and j['status']=='COMPLETE','Host controller must finish before native query'
s,_=a.connect();a.idle(s)
assert a.run.native_iteration(s)==34661
film=a.run.film(s);assert math.isclose(film['film_elapsed_time'],.05,abs_tol=1e-10)
parameters=dict(s.rp_vars('wall-film/model-parameters'));expected=dict(m['parameters']);expected['timestep-max']=m['schedule'][-1][2];assert parameters==expected
walls=a.wall_audit(s);assert s.settings.solution.controls.equations.get_state()==m['bulk_equations']
shared=m['shared_pair'];files={}
base=Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland')
for key in ['case','data']:
 rel=shared[key].split('OneDrive - The University of Auckland\\',1)[1];p=base/Path(rel.replace('\\','/'));assert p.exists(),p
 digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==shared[key+'_sha256']
 files[key]={'path':str(p),'bytes':p.stat().st_size,'sha256':digest}
r={'status':'COMPLETE_50MS_REOPEN_AND_ONEDRIVE_HASH_VERIFIED','server_id':'6','native_iteration':34661,'film_s':film['film_elapsed_time'],'final_film_state':film,'updates':sum(x['updates'] for x in m['blocks']),'blocks':[{k:x[k] for k in ['label','updates','step_s','film_end_s','film_rows_observed','peak_courant_diagnostic']} for x in m['blocks']],'wall_checks':walls,'parameters_match_angled_basic_ewf_except_endpoint_step':True,'bulk_equations_frozen':True,'files':files,'host_job_status':j['status'],'fluent_left_open':True,'solver_mutations_in_reconciliation':0,'solve_replayed_after_timeout':False,'observed_utc':datetime.now(timezone.utc).isoformat()}
(out/'completion-reconciliation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','native_iteration','film_s','updates','host_job_status']},indent=2))
