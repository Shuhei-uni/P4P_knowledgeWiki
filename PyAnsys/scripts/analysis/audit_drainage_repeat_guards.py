from pathlib import Path
import json,numpy as np
p=Path(__file__).resolve().parents[2]/'output/drainage-benchmark-repeat1';c=json.loads((p/'campaign.json').read_text());audit=[]
for r in c['cases']:
 rows=[json.loads(x) for x in (p/r['tag']/'guard-history.jsonl').read_text().splitlines()];indices=[int(x['biter']) for x in rows];wanted=set(range(r['start_iteration']+1,r['start_iteration']+r['iterations']+1));seen=set(indices)
 a={'case':r['tag'],'covered_iterations':len(wanted & seen),'missing':sorted(wanted-seen),'finite':all(np.isfinite(list(x.values())).all() for x in rows),'maximum_speed':max(x['bmax'] for x in rows),'stop_reason':r.get('stop_reason'),'capture_error':r.get('capture_error')};a['passed']=r['status']=='COMPLETE' and not a['missing'] and a['finite'] and a['maximum_speed']<=20 and not a['stop_reason'] and not a['capture_error'];audit.append(a)
a={'cases':audit,'interrupt_proof_passed':c['cases'][0].get('interrupt_proof_passed',False),'completed_iterations':c['completed_iterations'],'passed':len(audit)==4 and all(x['passed'] for x in audit) and c['cases'][0].get('interrupt_proof_passed',False)};(p/'guard-audit.json').write_text(json.dumps(a,indent=2));print(json.dumps(a,indent=2))
