from pathlib import Path,PureWindowsPath
import sys,json,time
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
import run_phase9_server4_2_6M as run
s=run.attach();run.require_idle(s)
profile=s.scheme.eval('(getenv "USERPROFILE")');folder=PureWindowsPath(profile)/'Documents/FluentRuns/Phase9-Server4/20261007/scratch'
path=folder/('host-tools-'+str(time.time_ns())+'.json')
deps=folder.parent/'audit-deps'
code="$ErrorActionPreference='Continue'; $p=(Get-Command python.exe).Source; $r=(& $p -m pip install --disable-pip-version-check --no-deps --target '"+str(deps)+"' 'h5py==3.11.0' 2>&1 | Out-String); [IO.File]::WriteAllText('"+str(path)+"',$r,[Text.Encoding]::ASCII)"
run.base.powershell(s,code)
r=run.read_text(s,str(path));(run.OUT/'host-h5py-install.txt').write_text(r);print(r)
