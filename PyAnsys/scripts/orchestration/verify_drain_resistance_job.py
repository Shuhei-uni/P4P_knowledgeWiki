"""Verify bounded run execution and expose evidence for scientific review."""
from pathlib import Path
import argparse,json,subprocess,sys,yaml
p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--iterations',type=int,required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[3]
# Existing verifier reduces the same report schema and verifies fields and sections.
subprocess.run([sys.executable,str(root/'PyAnsys/scripts/orchestration/verify_phase09_job.py'),'--receipt',str(args.receipt),'--start',str(args.start),'--iterations',str(args.iterations)],check=True)
rp=Path(json.loads(args.receipt.read_text())['run_manifest']);r=json.loads(rp.read_text());state=root/'Project/experiments/full-geometry-drain-resistance/phase-state.yaml';s=yaml.safe_load(state.read_text())
runs=[json.loads(p.read_text()) for p in (root/'PyAnsys/output/full-geometry-drain-resistance').glob('**/run.json')]
s.update(status='BLOCK_COMPLETE_REVIEW_REQUIRED',solver_iterating=False,completed_iterations=sum(x.get('completed_iterations',x.get('issued_iterations',0)) for x in runs),solver_wall_seconds=sum(x.get('elapsed_s',0) for x in runs),current_action='N1000 evidence ready; scientific review required before any continuation',live_run_manifest=str(rp),qualified=False)
state.write_text(yaml.safe_dump(s,sort_keys=False))
print('Drain-resistance block verified; no automatic continuation authorized by this verifier.')
