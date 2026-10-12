"""Replace only the selected 997k OneDrive pair; preserve the live Fluent case."""
from pathlib import Path, PureWindowsPath
import copy
import hashlib
import json
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts/setup')]
import run_phase9_mesh_startup as run
from pyansys_fluent.common import quote_scheme_string, remote_file_exists
from pyansys_fluent.remote_text import write_ascii_text_new, read_text


def deadline(_signum, _frame):
    raise TimeoutError('Selection operation timed out; reconcile receipt before retry')


def main():
    tag = str(time.time_ns())
    out = ROOT / 'output/phase9-997k-final-selection/20261009' / tag
    out.mkdir(parents=True, exist_ok=False)
    selected_path = run.OUT / 'initial-bulk-final-selection.json'
    old = json.loads(selected_path.read_text())
    assert old['pairs']['997k']['native_iteration'] == 9103
    source = json.loads((run.OUT / '997k-run.json').read_text())
    pair = source['final_pair']
    assert pair['native_iteration'] == 8080
    proof_path = Path(next(b['checkpoint_proof'] for b in source['blocks'] if b['end'] == 8080))
    proof = json.loads(proof_path.read_text())
    assert proof['status'] == 'REOPEN_VERIFIED'
    assert proof['pair']['case_sha256'] == pair['case_sha256']
    assert proof['pair']['data_sha256'] == pair['data_sha256']
    (out / 'previous-selection.json').write_text(json.dumps(old, indent=2) + '\n')
    destination = PureWindowsPath(old['destination'])
    shared = {kind: str(destination / '997k' / f'997k-initial-bulk-N8080.{ext}.h5')
              for kind, ext in [('case', 'cas'), ('data', 'dat')]}
    new = copy.deepcopy(old)
    new.update(authority='human_select_997k_N8080_final_20261009', selection_iteration=8080,
               **{'997k_pair': pair}, film=source['final_film'], steady_claim=False,
               selected_997k_previous_endpoint=9103, selection_receipt=str(out / 'receipt.json'))
    new['pairs']['997k'] = {'native_iteration': 8080, 'source': pair, 'shared_pair': shared,
                           'hashes': {kind: pair[kind + '_sha256'] for kind in ['case', 'data']}}
    new.pop('live_native_after', None)
    new['shared_997k_reopen'] = {'status': 'SOURCE_REOPEN_VERIFIED_COPY_HASH_MATCH',
                                'native_iteration': 8080, 'source_checkpoint_proof': str(proof_path),
                                'shared_pair_loaded_in_this_operation': False}
    payload = {'old': old, 'new': new, 'tag': tag}
    remote_script = str(run.WORK / '997k' / f'select-final-N8080-{tag}.py')
    remote_receipt = str(run.WORK / '997k' / f'select-final-N8080-{tag}.json')
    host = '''import pathlib,json,hashlib,shutil,os
payload=json.loads(PAYLOAD)
old,new=payload['old'],payload['new']
dest=pathlib.Path(new['destination'])
source=new['pairs']['997k']['source']
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as stream:
  for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
for kind in ['case','data']:
 assert digest(source[kind])==source[kind+'_sha256'],'Source hash mismatch'
archive=dest/'archive'/('superseded-997k-N9103-'+payload['tag'])
archive.mkdir(parents=True,exist_ok=False)
for name in ['selection-manifest.json','all-five-selected-endpoints.json','README.txt','ALL-FIVE-ENDPOINTS.txt']:
 p=dest/name
 if p.exists():shutil.copy2(p,archive/name)
for kind in ['case','data']:
 prior=pathlib.Path(old['pairs']['997k']['shared_pair'][kind])
 assert digest(prior)==old['pairs']['997k']['hashes'][kind],'Previous export hash mismatch'
 target=pathlib.Path(new['pairs']['997k']['shared_pair'][kind])
 assert not target.exists(),'Reconcile existing new destination first'
 temp=target.with_name(target.name+'.pending-'+payload['tag'])
 shutil.copy2(source[kind],temp)
 assert digest(temp)==source[kind+'_sha256'],'Copied hash mismatch'
 os.replace(temp,target)
for kind in ['case','data']:
 prior=pathlib.Path(old['pairs']['997k']['shared_pair'][kind])
 shutil.move(str(prior),str(archive/prior.name))
new['superseded_997k_archive']=str(archive)
for name in ['selection-manifest.json','all-five-selected-endpoints.json']:
 target=dest/name;temp=dest/(name+'.pending-'+payload['tag'])
 temp.write_text(json.dumps(new,indent=2)+'\\n',encoding='utf-8');os.replace(temp,target)
text='Selected final initial bulk-development states. No steady-state or mesh-convergence claim.\\n\\n60k N8080, 342k N8580, 680k N9080, 997k N8080: subfolders here.\\n2.6M N8580: ../../Server4/2_6M/final-initial-bulk-N8580-1791516489726781000\\n\\n997k N8080 selected by the human on 9 October 2026. Case/data hashes match the reopened source checkpoint.\\nSuperseded 997k N9103 and previous manifests preserved under archive/.\\n'
for name in ['README.txt','ALL-FIVE-ENDPOINTS.txt']:(dest/name).write_text(text,encoding='utf-8')
receipt={'status':'SELECTED_N8080_COPY_HASH_VERIFIED','selection':new,'archive':str(archive),'files':{kind:{'path':new['pairs']['997k']['shared_pair'][kind],'sha256':digest(new['pairs']['997k']['shared_pair'][kind])} for kind in ['case','data']},'cloud_upload_independently_verified':False}
pathlib.Path(RECEIPT).write_text(json.dumps(receipt,indent=2)+'\\n',encoding='utf-8')
'''.replace('PAYLOAD', repr(json.dumps(payload))).replace('RECEIPT', repr(remote_receipt))
    (out / 'host-copy.py').write_text(host)
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(30)
    s = run.attach()
    before = {'native_iteration': run.native_iteration(s), 'iterating': s.settings.solution.run_calculation.iterating()}
    assert remote_file_exists(s, str(run.HOST_PYTHON))
    write_ascii_text_new(s, remote_script, host)
    signal.alarm(180)
    command = f'cmd /c ""{run.HOST_PYTHON}" "{remote_script}""'
    result = s.scheme.eval('(system "' + quote_scheme_string(command) + '")')
    assert result in [0, None], result
    receipt = json.loads(read_text(s, remote_receipt))
    signal.alarm(30)
    after = {'native_iteration': run.native_iteration(s), 'iterating': s.settings.solution.run_calculation.iterating()}
    signal.alarm(0)
    assert receipt['status'] == 'SELECTED_N8080_COPY_HASH_VERIFIED'
    for kind in ['case', 'data']:
        assert receipt['files'][kind]['sha256'] == pair[kind + '_sha256']
    receipt.update(live_before=before, live_after=after, case_loads=0, solves=0,
                   script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   review='Hash source and old export; stage and hash new pair; archive old pair; promote manifests; no Fluent case/settings changes')
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    selected_path.write_text(json.dumps(receipt['selection'], indent=2) + '\n')
    (run.OUT / '997k-final-selection-N8080.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('SELECTED_N8080_COPY_HASH_VERIFIED', str(out / 'receipt.json'), flush=True)


if __name__ == '__main__':
    main()
