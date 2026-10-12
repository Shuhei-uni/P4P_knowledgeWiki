import sys,json,time
from pathlib import Path,PureWindowsPath
sys.path.insert(0,str(Path('PyAnsys/scripts/setup').absolute()))
import run_phase9_mesh_startup as r
from pyansys_fluent.common import quote_scheme_string
stamp=str(time.time_ns());s=r.attach();r.require_idle(s)
observed=json.loads((r.OUT/'human-selected-initial-bulk-live.json').read_text());n=r.native_iteration(s)
if n!=observed['native_iteration']:raise RuntimeError('Native iteration changed since idle inspection')
r.assert_bulk_active(s);r.read_feed(s,1.0)
pair=r.save(s,r.WORK/'997k',f'human-final-initial-bulk-N{n}-{stamp}')
record={'status':'LOCAL_SELECTED_PAIR_SAVED','authority':'human_select_manual_stop_initial_bulk_not_steady','selection_iteration':n,'997k_pair':pair,'film':r.film(s),'bulk_equations':r.assert_bulk_active(s),'steady_claim':False,'destination':str(r.SHARED/'P4P-Fluent-Artifacts'/'Phase9'/'initial-bulk-development-final'/('selected-'+stamp)),'pairs':{}}
receipt=r.OUT/f'initial-bulk-final-share-{stamp}.json';r.dump(receipt,record);print('LOCAL_SELECTED_PAIR_SAVED',n,flush=True)
for mesh in ['60k','342k','680k','997k']:
 source=pair if mesh=='997k' else json.loads((r.OUT/(mesh+'-run.json')).read_text())['final_pair']
 dest=PureWindowsPath(record['destination'])/mesh
 names={k:str(dest/f'{mesh}-initial-bulk-N{source["native_iteration"]}.{ext}.h5') for k,ext in [('case','cas'),('data','dat')]}
 def psquote(t):return "'"+t.replace("'","''")+"'"
 script="$ErrorActionPreference = 'Stop'\nNew-Item -ItemType Directory -Force -Path "+psquote(str(dest))+" | Out-Null\n"
 for k in ['case','data']:
  script+='Copy-Item -LiteralPath '+psquote(source[k])+' -Destination '+psquote(names[k])+' -ErrorAction Stop\n'
 ps=str(r.WORK/'997k'/f'share-{mesh}-{stamp}.ps1');r.write_ascii_text_new(s,ps,script)
 command='cmd /c powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+ps+'"'
 result=s.scheme.eval('(system "'+quote_scheme_string(command)+'")')
 if result not in [0,None]:raise RuntimeError(f'Copy failed for {mesh}: {result}')
 entry={'native_iteration':source['native_iteration'],'source':source,'shared_pair':names,'hashes':{}}
 for k in ['case','data']:
  digest=r.remote_file_sha256(s,names[k],str(r.WORK/'997k'/'scratch'/f'share-{mesh}-{k}-{stamp}.sha256.txt'))
  if digest!=source[k+'_sha256']:raise RuntimeError('Shared hash differs')
  entry['hashes'][k]=digest
 record['pairs'][mesh]=entry;r.dump(receipt,record);print('SHARED_PAIR_HASH_VERIFIED',mesh,source['native_iteration'],flush=True)
record.update(status='SERVER3_FOUR_SELECTED_PAIRS_SHARED_VERIFIED',server4='SEPARATE_OWNER_NO_SELECTED_FINAL_IN_RECORDS',live_native_after=r.native_iteration(s));r.dump(receipt,record);r.dump(r.OUT/'initial-bulk-final-selection.json',record)
print('SHARED_FINAL_FOLDER',record['destination'],flush=True)
