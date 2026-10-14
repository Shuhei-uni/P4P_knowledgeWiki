"""One-time byte-identical recovery collector for the original three-case stop.

Only run after an independent live idle check. Refuse any running or remainder
launch; the original native error and every raw artifact remain immutable.
"""
import base64,json,hashlib,os,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'PyAnsys/scripts/setup'),str(ROOT/'PyAnsys/src')]
import probe_phase10_native_receipts as p
from pyansys_fluent.remote_text import ascii_write_expression
from deploy_phase10_bf01 import psquote
from pyansys_fluent.common import quote_scheme_string
out=p.OUT;dest=out/'replication-enthalpy-M04';cfg=json.loads((out/'run-config.json').read_text());launch=json.loads((out/'current-launch.json').read_text())
assert launch['experiment']=='REPLICATION_ENTHALPY_SWEEP' and launch['selected_queue']==[1440,1520,1680,1760]
assert launch['status']=='STOPPED_PRESERVE_ENDPOINT', 'Original batch must be terminal'
endpoint,md=p.connection(cfg,os.environ)
def ev(expr,timeout=15):
 ch=p.grpc.insecure_channel(endpoint);stub=p.scheme_eval_pb2_grpc.SchemeEvalStub(ch)
 try:
  q=p.proto.SchemeEvalRequest();p._convert_py_value_to_scheme_pointer((p.Symbol('eval'),(p.Symbol('with-input-from-string'),expr,p.Symbol('read')),p.Symbol('user-initial-environment')),q.input,'25.2.0');r=stub.SchemeEval(q,metadata=md,timeout=timeout);return p._convert_scheme_pointer_to_py_value(r.output,'25.2.0')
 finally:ch.close()
def rd(path,limit):
 path=quote_scheme_string(path.replace('\\','/'));return ev('(let ((p (open-input-file "'+path+'"))) (let loop ((chars (quote ())) (left '+str(limit)+')) (let ((c (read-char p))) (cond ((eof-object? c) (close-input-port p) (list->string (reverse chars))) ((= left 0) (close-input-port p) (error "bound")) (else (loop (cons c chars) (- left 1)))))))')
tag=uuid.uuid4().hex[:8];ps=launch['work']+'/collect-recovery-'+tag+'.ps1';bundle=ps+'.json';paths={};pairs=[]
for h in [1440,1520,1680]:
 m=json.loads((dest/'passive-read'/('H'+str(h)+'-manifest.json')).read_text());work=launch['work']+'/H'+str(h)
 paths['H'+str(h)+'/manifest.json']=work+'/manifest.json';paths['H'+str(h)+'/preparation.trn']=work+'/preparation.trn';paths['H'+str(h)+'/DPM-tracking.trn']=work+'/DPM-tracking.trn'
 for point in m['checkpoints']:
  pairs.append(point['pair'])
  if 'transcript' in point:paths['H'+str(h)+'/'+Path(point['transcript'].replace('\\','/')).name]=point['transcript']
 pairs.append(m.get('final_pair',m['tracked_pair']))
 paths.update({'H'+str(h)+'/'+Path(v.replace('\\','/')).name:v for v in m['report_files'].values()})
 paths.update({'H'+str(h)+'/monitors/'+n+'.out':v['file'] for n,v in m['report_paths'].items()})
code="$ErrorActionPreference='Stop'\ntry {\n$workers=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -match 'run_phase10|resume_phase10|phase10_core'})\nif($workers.Count -gt 0){throw 'Phase10 controller still present'}\n$proof=@()\n"
for pair in pairs:
 for k in ['case','data']:
  code+='$h=(Get-FileHash -LiteralPath '+psquote(pair[k])+' -Algorithm SHA256).Hash.ToLower()\nif($h -ne '+psquote(pair[k+'_sha256'])+'){throw "Pair hash changed"}\n$proof+=@{path='+psquote(pair[k])+';sha256=$h}\n'
code+='$rows=@()\n'
for name,path in paths.items():
 code+='$bytes=[IO.File]::ReadAllBytes('+psquote(path)+')\nif($bytes.Length -gt 1048576){throw "File exceeds bound"}\n$rows+=@{name='+psquote(name)+';path='+psquote(path)+';sha256=(Get-FileHash -LiteralPath '+psquote(path)+' -Algorithm SHA256).Hash.ToLower();base64=[Convert]::ToBase64String($bytes);bytes=$bytes.Length}\n'
code+='$payload=@{status="PASS";workers=@();pairs=$proof;files=$rows} | ConvertTo-Json -Depth 6\nif($payload.Length -gt 4000000){throw "Bundle exceeds bound"}\n$payload | Set-Content -LiteralPath '+psquote(bundle)+' -Encoding Ascii\n} catch { @{status="FAIL";error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath '+psquote(bundle)+' -Encoding Ascii }\n'
intent={'script':ps,'bundle':bundle,'source_sha256':hashlib.sha256(code.encode('ascii')).hexdigest(),'state':'BEFORE_UPLOAD'};(dest/'collection-recovery-intent.json').write_text(json.dumps(intent,indent=2)+'\n')
# String acknowledgements and exclusive unique path; no unlabelled Boolean/void replies.
expr='(if (file-exists? "'+quote_scheme_string(ps)+'") (error "Existing recovery artifact") (begin '+ascii_write_expression(ps,code)+' "SAVED"))'
assert ev(expr,30)=='SAVED';assert rd(ps,131072).replace('\r\n','\n')==code
intent['state']='UPLOADED_VERIFIED_BEFORE_OS';(dest/'collection-recovery-intent.json').write_text(json.dumps(intent,indent=2)+'\n')
cmd='powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+ps+'"'
ev('(begin (system "'+quote_scheme_string(cmd)+'") "EXECUTED")',60)
result=json.loads(rd(bundle,4000000));assert result['status']=='PASS',result
for row in result['files']:
 data=base64.b64decode(row['base64']);assert hashlib.sha256(data).hexdigest()==row['sha256'];h,name=row['name'].split('/',1);target=dest/h/'raw'/name;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==data,'Immutable raw changed'
 else:target.write_bytes(data)
records=[{k:v for k,v in r.items() if k!='base64'} for r in result['files']]
receipt={'status':'PASS','controller_absent_verified':True,'native_pairs_rehashed':result['pairs'],'files':records,'source_bundle':bundle,'byte_identical':True};(dest/'collection-recovery.json').write_text(json.dumps(receipt,indent=2)+'\n')
for h in [1440,1520,1680]:
 (dest/('H'+str(h))/'retrieval.json').write_text(json.dumps({'status':'BYTE_IDENTICAL_RETRIEVAL_VERIFIED','controller_absent_verified':True,'files':[r for r in records if r['name'].startswith('H'+str(h)+'/')]},indent=2)+'\n')
launch.update(status='STOPPED_PRESERVE_ENDPOINT',controller_exited_verified=True,solved_updates=4500,native_pair_hashes_verified=True,evidence_retrieved=True);(dest/'sweep-launch.json').write_text(json.dumps(launch,indent=2)+'\n');(out/'current-launch.json').write_text(json.dumps(launch,indent=2)+'\n')
print(json.dumps({'status':'PASS','files':len(records),'pairs_rehashed':len(result['pairs']),'controller_absent':True}))
