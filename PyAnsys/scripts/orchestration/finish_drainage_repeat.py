"""Wait for exact existing repeat controller, audit it and restore owned separator; no solves."""
from pathlib import Path
import sys,json,time,os,subprocess,fcntl
from datetime import datetime,timezone,timedelta
import yaml
BASE=Path(__file__).resolve().parents[2];ROOT=BASE.parent;out=BASE/'output/drainage-benchmark-repeat1';p=out/'campaign.json';r=json.loads(p.read_text());pid=r['controller_pid'];deadline=datetime.fromisoformat(yaml.safe_load((ROOT/'Project/experiments/drainage-boundary-verification/phase-state.yaml').read_text())['execution_deadline_utc'])
while True:
 r=json.loads(p.read_text())
 try:os.kill(pid,0);alive=True
 except ProcessLookupError:alive=False
 if not alive:break
 if datetime.now(timezone.utc)>deadline+timedelta(minutes=10):raise RuntimeError('Controller did not terminate after deadline; reconcile owned session')
 time.sleep(10)
assert r['status'] in ['COMPLETE','RECONCILE_REQUIRED'],r['status']
result={'controller_pid':pid,'controller_exited':True,'campaign_status':r['status'],'analysis_passed':False,'guard_passed':False,'restored':False}
if r['status']=='COMPLETE':
 subprocess.run([sys.executable,str(BASE/'scripts/analysis/analyze_drainage_benchmark.py'),str(out)],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(BASE/'scripts/analysis/audit_drainage_repeat_guards.py')],cwd=ROOT,check=True)
 result['analysis_passed']=json.loads((out/'analysis.json').read_text())['all_passed'];result['guard_passed']=json.loads((out/'guard-audit.json').read_text())['passed']
else:
 last=r['cases'][-1];assert last.get('pair_exists') or last.get('interrupted_pair_exists'),'Failed endpoint preservation unverified'
sys.path.insert(0,str(BASE/'scripts/setup'))
from build_phase09_pool import connect,assert_contract,remote_file_exists
lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating()
parent=json.loads((BASE/'output/drainage-benchmark/restore-parent.json').read_text());assert all(remote_file_exists(s,parent['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
s.settings.file.read_case_data(file_name=parent['case']);assert_contract(s);assert s.settings.setup.named_expressions['P9Iteration'].get_value()==2000;assert not s.settings.solution.run_calculation.iterating()
result.update(restored=True,restored_case=parent['case'],native_iteration=2000,checked_at_utc=datetime.now(timezone.utc).isoformat());(out/'completion-verification.json').write_text(json.dumps(result,indent=2))
pstate=ROOT/'Project/experiments/drainage-boundary-verification/phase-state.yaml';st=yaml.safe_load(pstate.read_text());st.update(status='CORRECTED_REPEAT_VERIFIED' if result['analysis_passed'] and result['guard_passed'] else 'CORRECTED_REPEAT_REVIEW_REQUIRED',repeat_completed_iterations=r['completed_iterations'],completed_iterations=2000+r['completed_iterations'],solver_iterating=False,restored_separator_native_iteration=2000,current_action='Repeat terminal evidence and restoration available; scientific review required before any separator run',repeat_verification='../../../PyAnsys/output/drainage-benchmark-repeat1/completion-verification.json');pstate.write_text(yaml.safe_dump(st,sort_keys=False))
print(json.dumps(result,indent=2));assert result['analysis_passed'] and result['guard_passed']
