"""Run the predeclared 50-step smoke then 950-step recovery screen, without a CLI wakeup."""
from pathlib import Path
import json,subprocess,sys,argparse
BASE=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--build',type=Path);p.add_argument('--receipt-dir',type=Path,default=BASE/'output/phase09-preflight/recovery-screen');args=p.parse_args()
receipt_dir=args.receipt_dir
receipt_dir.mkdir(exist_ok=True)
build=args.build or Path(json.loads((BASE/'output/phase09-preflight/small-step-build-receipt.json').read_text())['manifest'])
parent=None
for start,count,label in [(0,50,'smoke'),(50,950,'continuation')]:
 receipt=receipt_dir/(label+'-receipt.json')
 command=[sys.executable,str(BASE/'scripts/setup/run_phase09_pool.py'),'--build',str(build),'--mode','flow','--iterations',str(count),'--expected-start',str(start),'--receipt',str(receipt)]
 if parent:command+=['--parent-run',str(parent)]
 subprocess.run(command,check=True)
 subprocess.run([sys.executable,str(BASE/'scripts/orchestration/verify_phase09_job.py'),'--receipt',str(receipt),'--start',str(start),'--iterations',str(count)],check=True)
 parent=Path(json.loads(receipt.read_text())['run_manifest'])
 # Verification requires a complete bounded block, no safety/capture stop,
 # paired endpoint, native histories, all fields and section exports.
 print('VERIFIED_STAGE',label,parent,flush=True)
print('RECOVERY_SCREEN_COMPLETE; scientific assessment remains required',flush=True)
