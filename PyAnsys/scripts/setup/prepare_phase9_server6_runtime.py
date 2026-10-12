"""Prepare the isolated Server 6 controller runtime; no solve or Fluent exit."""
import sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts/setup'),str(ROOT/'src')]
from phase9_server6_997k_common import attach,run,OUT
s=attach();run.require_idle(s)
tag=str(time.time_ns());venv=run.WORK/'controller-venv';rpath=run.WORK/'997k'/'scratch'/('runtime-install-'+tag+'.json')
q=lambda v:"'"+str(v).replace("'","''")+"'"
base=json.loads((OUT/'ansys-python-preflight.json').read_text());assert base['return_code']==0
code="$ErrorActionPreference='Continue'; $python="+q(base['executable'])+"; $log=(& $python -E -m venv "+q(venv)+" 2>&1 | Out-String); $create=$LASTEXITCODE; if ($create -eq 0) {$log+=(& "+q(venv/'Scripts/python.exe')+" -E -m pip install --disable-pip-version-check 'ansys-fluent-core==0.42.0' 'numpy==2.2.6' 'python-dotenv==1.2.2' 'PyYAML==6.0.3' 'pandas==2.3.3' 'matplotlib==3.10.9' 2>&1 | Out-String); $install=$LASTEXITCODE} else {$install=-1}; [IO.File]::WriteAllText("+q(rpath)+",(@{venv="+q(venv)+";create_code=$create;install_code=$install;output=$log}|ConvertTo-Json -Depth 5),[Text.Encoding]::ASCII)"
print('HOST_RUNTIME_INSTALL_BEGIN',flush=True)
run.base.powershell(s,code);r=json.loads(run.read_text(s,str(rpath)));run.dump(OUT/'host-runtime-install.json',r)
print(json.dumps({k:r[k] for k in ['venv','create_code','install_code']},indent=2));print(r['output'][-3000:])
assert r['create_code']==r['install_code']==0
