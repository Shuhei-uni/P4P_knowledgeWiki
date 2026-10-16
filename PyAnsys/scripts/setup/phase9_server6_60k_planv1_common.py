"""Server6-only Phase9 60k Planv1 lane."""
from pathlib import Path,PureWindowsPath
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from phase9_server6_slit_common import attach as original_attach,run
OUT=ROOT/'output/phase9-server6-60k-planv1/20261014';OUT.mkdir(parents=True,exist_ok=True)
def attach():
 s=original_attach();profile=PureWindowsPath(s.scheme.eval('(getenv "USERPROFILE")'))
 run.WORK=profile/'Documents/FluentRuns/Phase9-Server6-60k-planv1/20261014'
 run.SHARED=profile/'OneDrive - The University of Auckland';run.OUT=OUT
 return s
