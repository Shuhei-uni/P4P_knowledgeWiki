"""Build the six levels around the verified anchor, one Fluent operation at a time."""
import json,subprocess,sys
from pathlib import Path
from build_single_inlet_family import OUT

levels=[('curvature-trial',1.23**4),('curvature-middle',1.5),('curvature-anchor',1),
        ('selected-fine-1',.8),('selected-fine-2',.65),('selected-fine-3',.53),('selected-fine-4',.45)]
if __name__=='__main__':
    running=[]
    for path in OUT.glob('*-status.json'):
        record=json.loads(path.read_text())
        if record.get('status')=='RUNNING':running.append(record['id'])
    if running:raise RuntimeError('Another build is still running: '+str(running))
    anchor=json.loads((OUT/'anchor-verified-status.json').read_text())
    if anchor['status']!='COMPLETE':raise RuntimeError('Anchor is not verified')
    for rid,scale in levels:
        print('BUILD',rid,scale,flush=True)
        with (OUT/(rid+'-run.txt')).open('a') as log:
            result=subprocess.run([sys.executable,str(Path(__file__).with_name('build_single_inlet_family.py')),
                '--scale',str(scale),'--id',rid],stdout=log,stderr=subprocess.STDOUT)
        status=json.loads((OUT/(rid+'-status.json')).read_text())
        print(json.dumps(status),flush=True)
        if result.returncode:raise RuntimeError('Level failed: '+rid)
